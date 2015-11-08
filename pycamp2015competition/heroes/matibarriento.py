from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota import settings
from tota.things import Ancient, Tower, Creep

AUTHOR = 'MatiBarriento'


def create():
    def logic(self, things, t):
        #For fun

        #self.xp = 1000000

        #Enemies
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]

        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        enemy_ancient = [thing for thing in enemies
                         if isinstance(thing, Ancient)][0]
        try:
            enemy_tower = [thing for thing in enemies
                       if isinstance(thing, Tower)][0]
        except:
            pass

        closest_enemy_distance = distance(self, closest_enemy)

        #Friends
        friends = [thing for thing in things.values()
                   if thing.team == self.team]
        friendly_creeps = [friend for friend in friends
                           if isinstance(friend, Creep)]
        closest_friend_creep = closest(self, friendly_creeps)

        friendly_ancient = [thing for thing in friends
                            if isinstance(thing, Ancient)][0]

        #Utils

        #Act

        life_factor = (self.level + 1)
        life_comparer = self.max_life - (self.max_life * (life_factor / 100))
        life_comparer = life_comparer if life_comparer >= 0 else self.max_life

        if self.life < life_comparer or self.life < self.max_life * 0.30:
            if self.can('heal', t):
                return 'heal', self.position
            else:
                target_to_go = closest_friend_creep if closest_friend_creep else friendly_ancient
                moves = sort_by_distance(target_to_go,
                                         possible_moves(self, things))
                for move in moves:
                    return 'move', move
        elif closest_enemy:
            if closest_enemy_distance <= settings.STUN_DISTANCE and self.can('stun', t):
                return 'stun', closest_enemy.position
            elif closest_enemy_distance <= settings.FIREBALL_DISTANCE and self.can('fireball', t) and closest_enemy_distance > settings.FIREBALL_RADIUS:
                return 'fireball', closest_enemy.position
            elif closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
                return 'attack', closest_enemy.position
            else:
                moves = sort_by_distance(closest_enemy,
                                         possible_moves(self, things))
                if moves:
                    return 'move', moves[0]
        else:
            moves = sort_by_distance(friendly_creeps[-1],
                                     possible_moves(self, things))
            for move in moves:
                return 'move', move

    return logic


# if self.level < 50:
#             # if (friendly_creeps is None
#             #         or (
#             #             distance(self, enemy_ancient) <
#             #             distance(closest_friend_creep, enemy_ancient),
#             #         )):
#             #     moves = sort_by_distance(closest_friend_creep,
#             #                              possible_moves(self, things))
#             #     for move in moves:
#             #         return 'move', move
#             # else:
#             if not self.life < self.max_life:
#                 if (closest_enemy_distance <= settings.STUN_DISTANCE
#                         and self.can('stun', t)):
#                     return 'stun', closest_enemy.position
#                 # elif (closest_enemy_distance <= settings.FIREBALL_DISTANCE
#                 #       and self.can('fireball', t)
#                 #       and closest_enemy_distance > settings.FIREBALL_RADIUS):
#                 #     return 'fireball', closest_enemy.position
#                 elif closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
#                     return 'attack', closest_enemy.position

#                 else:
#                     moves = sort_by_distance(friendly_creeps[-1],
#                                              possible_moves(self, things))
#                     for move in moves:
#                         return 'move', move
#         # else:
#         #     if (closest_enemy_distance <= settings.STUN_DISTANCE
#         #        and self.can('stun', t)):
#         #         return 'stun', closest_enemy.position
#         #     elif (closest_enemy_distance <= settings.FIREBALL_DISTANCE
#         #           and self.can('fireball', t)
#         #           and closest_enemy_distance > settings.FIREBALL_RADIUS):
#         #         return 'fireball', closest_enemy.position
#         #     elif closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
#         #         return 'attack', closest_enemy.position
