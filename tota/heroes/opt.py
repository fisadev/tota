from tota.utils import closest, distance, sort_by_distance, possible_moves, circle_positions
from tota import settings

from random import choice

AUTHOR = 'Darni'

def predict_move(item, things, t):
    if item.name in ('tree', 'tower', 'ancient'):
        # These not move
        return [item.position]
    elif item.disabled_until > t:
        # Disabled does not move
        return [item.position]
    else:
        # CREEPS
        # heros are assumed to be creep-like
        
        # Copy and paste from things.py
        enemy_team = settings.ENEMY_TEAMS[item.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        closest_enemy = closest(item, enemies)
        closest_enemy_distance = distance(item, closest_enemy)

        if closest_enemy_distance <= settings.CREEP_ATTACK_DISTANCE:
            return [item.position]
        else:
            if closest_enemy_distance > settings.CREEP_AGGRO_DISTANCE:
                # enemy too far away, go to the ancient
                enemy_ancient = [thing for thing in enemies
                                 if thing.name=='ancient'][0]
                move_target = enemy_ancient
            else:
                # enemy in aggro distance, go to it!
                move_target = closest_enemy

            moves = sort_by_distance(move_target,
                                     possible_moves(item, things))
            if not moves:
                return [item.position]
            elif len(moves) == 1:
               return [moves[0]]
            else:
                if distance(moves[0], move_target) == distance(moves[1], move_target):
                    return moves[:2]
                else:
                    return moves[:1]
        return [item.position]

def predict(things, t):
    # Returns a new version of things mapping positions to list of pairs (p, object)
    # Where p is a probability.
    result = {}
    for pos, item in things.items():
        moves = predict_move(item, things, t)
        prob = 1.0 / len(moves)
        for m in moves:
            l = result.setdefault(m, [])
            l.append((prob, item))
    return result

# Action effects:
# (ancient-kills, tower-kills, hero-kills, creep-kills, damage)
def mkaction(action, position, ancient_kills=0, tower_kills=0, hero_kills=0, creep_kills=0, damage=0):
    return {
        'action': action,
        'position': position,
        'ancient_kills': ancient_kills,
        'tower_kills': tower_kills,
        'hero_kills': hero_kills,
        'creep_kills': creep_kills,
        'damage': damage,
    }

def value(action):
    return (action['ancient_kills'],
            action['tower_kills'],
            action['hero_kills'],
            action['creep_kills'],
            action['damage'])

def multiplier(my_team, other_team):
    if other_team == my_team:
        return -1
    elif other_team == settings.ENEMY_TEAMS[my_team]:
        return +1
    else:
        return 0

def still_damage(self, things, t, defaultpos=None):
    # Estimate damage that I will get by standing still
    enemy_team = settings.ENEMY_TEAMS[self.team]
    enemies = [thing for thing in things.values()
               if thing.team == enemy_team]
    friends = [thing for thing in things.values()
               if thing.team == self.team]
    position = defaultpos or self.position
    result = 0
    for e in enemies:
        if e.disabled_until > t or not e.alive:
            # filter stunned stuff
            pass
        elif e.name == 'ancient':
            pass
        elif e.name == 'tower':
            if distance(position, e.position) <= settings.TOWER_ATTACK_DISTANCE and closest(e, friends) == self:
                result += sum(settings.TOWER_ATTACK_BASE_DAMAGE) / 2
        elif e.name == 'creep':
            if distance(position, e.position) <= settings.CREEP_ATTACK_DISTANCE and closest(e, friends) == self:
                result += sum(settings.CREEP_ATTACK_BASE_DAMAGE) / 2
        else:
            # assume hero
            multiplier = (1 + settings.HERO_ATTACK_LEVEL_MULTIPLIER * e.level)
            if e.can('fireball', t) and distance(position, e.position) <= settings.FIREBALL_RADIUS+1:
                result += sum(settings.FIREBALL_BASE_DAMAGE) / 2 * multiplier
            elif e.can('stun', t) and distance(position, e.position) <= settings.STUN_DISTANCE:
                result += settings.STUN_DURATION*sum(settings.HERO_ATTACK_BASE_DAMAGE) / 2 * multiplier
            elif distance(e.position, position) <= settings.HERO_ATTACK_DISTANCE:
                result += sum(settings.HERO_ATTACK_BASE_DAMAGE) / 2 * multiplier
    return result

def predict_attacks(self, things, t, act_name, maxrange, radius, base_damage, current):
    attackable_positions = circle_positions(self.position, maxrange)
    result = []
    DAMAGE = base_damage * (1 + settings.HERO_ATTACK_LEVEL_MULTIPLIER * self.level)
    received = still_damage(self, current, t)
    will_die = 0
    if received >= self.life:
        received = self.life
        will_die = 1
    for center in attackable_positions:
        action = mkaction(act_name, center, hero_kills=-will_die, damage=-received)
        for p in circle_positions(center, radius):
            for prob, item in things.get(p, ()):
                m = prob * multiplier(self.team, item.team)
                damage = m * max(min(DAMAGE, item.life), item.life-item.max_life) # Clip for damage and heal effects
                action['damage'] += damage
                if damage >= item.life: # scored a kill!
                    if item.name == 'ancient':
                        action['ancient_kills'] += m
                    if item.name == 'tower':
                        action['tower_kills'] += m
                    if item.name == 'creep':
                        action['creep_kills'] += m
                    if item.team != settings.TEAM_NEUTRAL:
                        # Must be a hero
                        action['hero_kills'] += m
        result.append(action)
    return result

def predict_moves(self, things, t):
    result = []
    for p in possible_moves(self, things)+[self.position]:
        received = still_damage(self, things, t, self.position)/2 + still_damage(self, things, t, p)/2
        will_die = 0
        if received >= self.life:
            received = self.life
            will_die = 1
        result.append(mkaction('move', p, hero_kills=-will_die, damage=-received))
    return result

def create():
    def option_logic(self, things, t):
        prediction = predict(things, t)
        actions = []
        actions.extend(predict_moves(self, things, t))
        actions.extend(predict_attacks(self, prediction, t, 'attack', settings.HERO_ATTACK_DISTANCE, 0, sum(settings.HERO_ATTACK_BASE_DAMAGE)/2, things))
        if self.can("fireball", t):
            actions.extend(predict_attacks(self, prediction, t, 'fireball', settings.FIREBALL_DISTANCE, settings.FIREBALL_RADIUS, sum(settings.FIREBALL_BASE_DAMAGE)/2, things))
        if self.can("stun", t):
            actions.extend(predict_attacks(self, prediction, t, 'stun', settings.STUN_DISTANCE, 0, settings.STUN_DURATION*sum(settings.HERO_ATTACK_BASE_DAMAGE)/2, things))
        if self.can("heal", t):
            # FIXME: heal should count prevented kills
            actions.extend(predict_attacks(self, prediction, t, 'heal', settings.HEAL_DISTANCE, settings.HEAL_RADIUS, -sum(settings.HEAL_BASE_HEALING)/2, things))
        actions.sort(key=value,reverse=True)
        best = actions[0]
        if value(best) == (0, 0, 0, 0, 0):
            return bored_tactics(self, things, t)
        return best['action'], best['position']

    def bored_tactics(self, things, t):
        # some useful data about the enemies I can see in the map
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        friends = [thing for thing in things.values()
                   if thing.team == self.team and thing != self]
        closest_friend = closest(self, friends)

        # now lets decide what to do
        if self.life < self.max_life:
            # go to friends
            moves = sort_by_distance(closest_friend,
                                     possible_moves(self, things))
            if moves:
                return 'move', moves[0]
        elif closest_enemy:
            # of finally just move to him
            moves = sort_by_distance(closest_enemy,
                                     possible_moves(self, things))
            for move in moves:
                return 'move', move
        else:
            # no enemies, do nothing
            return None

    #return simple_hero_logic
    return option_logic
