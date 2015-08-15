from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota import settings

from random import choice

def predict_move(item, things):
    if i.name in ('tree', 'tower', 'ancient'):
        # These not move
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
                                 if isinstance(thing, Ancient)][0]
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

def predict(things):
    # Returns a new version of things mapping positions to list of pairs (p, object)
    # Where p is a probability.
    result = {}
    for pos, item in things.items():
        moves = predict_move(item, things)
        prob = 1.0 / len(moves)
        for m in moves:
            l = result.setdefault(m, [])
            l.append(m, (prob, item))
    return result

def create():
    def simple_hero_logic(self, things, t):
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
        if closest_enemy and closest_enemy_distance <= settings.STUN_DISTANCE and self.can('stun', t):
            # try to stun him
            return 'stun', closest_enemy.position
        elif closest_enemy and closest_enemy_distance <= settings.FIREBALL_DISTANCE and self.can('fireball', t) and closest_enemy_distance > settings.FIREBALL_RADIUS:
            # else try to fireball him, but only if I'm not in range
            return 'fireball', closest_enemy.position
        elif closest_enemy and closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
            # else try to attack him
            return 'attack', closest_enemy.position
        elif self.life < self.max_life:
            if self.can('heal', t):
                # if I'm hurt and can heal, heal
                return 'heal', self.position
            else:
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

    return simple_hero_logic
