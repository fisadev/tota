from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota.things import Ancient, Tower, Creep, Tree, Hero
from tota import settings

AUTHOR = 'gbytz'

def create():
    ally_base = None
    ally_tower = None

    enemy_base = None
    enemy_tower = None
    enemy_hero = None


    def gbytz_hero_logic(self, things, t):
        nonlocal ally_base, ally_tower, enemy_base, enemy_tower, enemy_hero      
        if not (ally_base and ally_tower and enemy_base and enemy_tower):
            ally_base, ally_tower, enemy_base, enemy_tower = get_buildings(things, self.team)

        enemy_hero = get_enemy_hero(things, self.team)        
        ally_creeps, enemy_creeps = get_creeps(things, self.team)

        a_front, a_back, e_front, e_back = get_lines(self, ally_creeps, enemy_creeps)

        heal_power = calculate_power(self, settings.HEAL_BASE_HEALING, settings.HEAL_LEVEL_MULTIPLIER)
        fireball_power = calculate_power(self, settings.FIREBALL_BASE_DAMAGE, settings.FIREBALL_LEVEL_MULTIPLIER)

        enemies = sort_by_threat(get_enemies_at_distance(self, things, 7))
        if self.life <= self.max_life - heal_power and self.can('heal', t):
            delta = (0, 0)
            return 'heal', (self.position[0] + delta[0], self.position[1] + delta[1])            

        skirmish_points = eval_skirmish(self, ally_tower, ally_creeps, enemy_hero, enemy_tower, enemy_creeps) 
        if skirmish_points <= 0 :
            if ally_tower.life > 0 and len(a_back) > 0:
                if distance(self, ally_tower) < distance(self, closest(ally_base, a_back)):
                    target = ally_tower
                else:
                    target = closest(ally_base, a_back)
            elif ally_tower.life > 0:
                target = ally_tower
            elif len(a_back) > 0:
                target = closest(ally_base, a_back)
            else:
                target = ally_base
                
            action = move_to_target(self, target, things) 

        elif skirmish_points > 0:
            if len(enemies) > 0:
                action = attack_enemies(self, enemies, t, things)
            else:
                if len(e_front) > 0:
                    target = closest(ally_base, e_front)
                elif enemy_tower.life > 0:
                    target = enemy_tower
                else:
                    target = enemy_base

                action = move_to_target(self, target, things)

        return action

    return gbytz_hero_logic

def move_to_target(hero, target, things):
    moves = sort_by_distance(target, possible_moves(hero, things))
    action = None
    if len(moves) > 0:
        action = 'move', moves[0]
    return action

def attack_enemies(hero, enemies, t, things):
    can_fireball = hero.can('fireball', t)
    can_stun = hero.can('stun', t)

    main_threat = enemies[0]
    print(main_threat)
    dist_to_threat = distance(main_threat, hero)
  
    action_str = None
    target_position = main_threat.position
    if isinstance(main_threat, Tower):
        if dist_to_threat == 1:
            action_str = 'attack'
        elif dist_to_threat <= settings.STUN_DISTANCE:
            if can_stun:
                action_str = 'stun'
            else:
                return move_to_target(hero, main_threat, things)
        elif dist_to_threat <= settings.FIREBALL_DISTANCE and dist_to_threat > 2:
            if can_fireball:
                action_str = 'fireball'
            else: 
                return move_to_target(hero, main_threat, things)
        else:
            # Pensar como pegarle con el AOE
            pass
    elif isinstance(main_threat, Hero):
        if dist_to_threat == 1:
            if hero.life >= main_threat.life:
                action_str = 'attack'
            else:
                action_str = 'move'
                target_position = (hero.position[0] - 1, hero.position[1] - 1)
        elif dist_to_threat <= settings.STUN_DISTANCE:
            if can_stun:
                action_str = 'stun'
        elif dist_to_threat <= settings.FIREBALL_DISTANCE and dist_to_threat > 2:
            if can_fireball:
                action_str = 'fireball'
        else:
            # Pensar como pegarle con el AOE
            pass
    elif isinstance(main_threat, Creep):
        if dist_to_threat == 1:
            action_str = 'attack'
        elif can_fireball:
            if dist_to_threat <= settings.FIREBALL_DISTANCE and dist_to_threat > 2:
                action_str = 'fireball'
        else:
            return move_to_target(hero, main_threat, things)

    else:
        if dist_to_threat == 1:
            action_str = 'attack'
        elif can_fireball:
            if dist_to_threat <= settings.FIREBALL_DISTANCE and dist_to_threat > 2:
                action_str = 'fireball'
        else:
            return move_to_target(hero, main_threat, things)

    if action_str is None:
        action = None
    else:
        action = action_str, target_position

    return action

def get_enemies_at_distance(hero, things, dist):
    enemies = []
    for thing in things.values():
        if thing.team not in (hero.team, settings.TEAM_NEUTRAL) and distance(hero, thing) < dist and thing.life > 0: 
            enemies.append(thing)
    return enemies

def sort_by_threat(enemies):
    def by_threat(enemy):
        threat = 0
        if isinstance(enemy, Creep):
            threat = 1
        elif isinstance(enemy, Hero):
            threat = 2
        elif isinstance(enemy, Tower):
            threat = 3
        elif isinstance(enemy, Ancient):
            threat = 4
        return threat
    sorted_enemies = list(sorted(enemies, key=by_threat, reverse=True))
    return sorted_enemies

def get_lines(hero, ally_creeps, enemy_creeps):
    a_front = []
    a_back = []
    for ally in ally_creeps:
        if distance(ally, hero) > 5:
            a_back.append(ally)
        else:
            a_front.append(ally)
    
    e_front = []
    e_back = []
    for enemy in enemy_creeps:
        if distance(enemy, hero) > 8:
            e_back.append(enemy)
        else:
            e_front.append(enemy)

    return a_front, a_back, e_front, e_back

def get_enemy_hero(things, ally_team):
    for thing in things.values():
        if isinstance(thing, Hero) and thing.team != ally_team:
            return thing

def get_creeps(things, ally_team):
    ally_creeps = []
    enemy_creeps = []
    for thing in things.values():
        if isinstance(thing, Creep) and thing.life > 0:
            if thing.team == ally_team:
                ally_creeps.append(thing)
            else:
                enemy_creeps.append(thing)
    return ally_creeps, enemy_creeps

def get_buildings(things, ally_team):
    a_base = None
    a_tower = None
    e_base = None
    e_tower = None
    for thing in things.values():
        if isinstance(thing, Tower):
            if thing.team == ally_team:
                a_tower = thing
            else:
                e_tower = thing
        elif isinstance(thing, Ancient):
            if thing.team == ally_team:
                a_base = thing
            else:
                e_base = thing
    return a_base, a_tower, e_base, e_tower

def calculate_power(hero, base_power, power_level_multiplier):
    power = (base_power[1] - base_power[0]) / 2
    power_multiplier = 1 + (hero.level * power_level_multiplier)
    return power * power_multiplier

def eval_skirmish(hero, ally_tower, ally_creeps, enemy_hero, enemy_tower, enemy_creeps):
    a_front, a_back, e_front, e_back = get_lines(hero, ally_creeps, enemy_creeps)

    total_points = 0
    total_points += len(a_front)
    if enemy_hero is not None and distance(hero, enemy_hero) <= 7:
        total_points += hero.level - enemy_hero.level
        total_points -= len(e_front)

    if ally_tower is not None and ally_tower.life > 0 and distance(hero, ally_tower) <= 2:
        total_points += 5

    if enemy_tower is not None and enemy_tower.life > 0 and distance(hero, enemy_tower) <= 3:
        total_points -= 5

    return total_points


