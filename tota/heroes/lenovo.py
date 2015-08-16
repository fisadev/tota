from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota import settings

AUTHOR = 'angvp'


def create():

    def lenovo_hero_logic(self, things, t):
        # some useful data about the enemies I can see in the map
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        real_life = ((self.life / self.max_life) * 100)

        # now lets decide what to do
        if int(real_life) < 70 and self.can('heal', t):
            # if I'm hurt and can heal, heal
            if closest_enemy_distance <= settings.HEAL_DISTANCE and self.can('fireball', t):
                return 'fireball', closest_enemy.position
            elif closest_enemy_distance <= settings.HEAL_DISTANCE and self.can('stun', t):
                return 'stun', closest_enemy.position
            elif closest_enemy_distance <= settings.HEAL_DISTANCE and self.can('attack', t):
                return 'attack', closest_enemy.position
            else:
                return 'heal', self.position
        else:
            # else, try to attack
            if closest_enemy:
                # there is an enemy
                if closest_enemy_distance <= settings.STUN_DISTANCE and self.can('stun', t):
                    # try to stun him
                    return 'stun', closest_enemy.position
                if closest_enemy_distance <= settings.FIREBALL_DISTANCE and self.can('fireball', t) and closest_enemy_distance > settings.FIREBALL_RADIUS:
                    # else try to fireball him, but only if I'm not in range
                    return 'fireball', closest_enemy.position
                elif closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
                    # else try to attack him
                    return 'attack', closest_enemy.position
                else:
                    # of finally just move to him (if I have life > 50)
                    moves = sort_by_distance(closest_enemy,
                                             possible_moves(self, things))
                    if len(moves) > 0:
                        back_moves = moves[len(moves)-1]
                    else:
                        back_moves = self.position
                    if moves and int(real_life) > 50:
                        return 'move', moves[0]
                    else:
                        return 'move', back_moves


        # can't do the things I want. Do nothing.
        return None


    return lenovo_hero_logic
