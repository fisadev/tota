from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota import settings


def create():
    def simple_hero_logic(self, things, t):
        # some useful data about the enemies I can see in the map
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        if self.life < self.max_life and self.can('heal', t):
            # if I'm hurt and can heal, heal
            return 'heal', self.position
        else:
            # else, try to attack
            if closest_enemy:
                # there is an enemy
                if closest_enemy_distance < settings.STUN_DISTANCE and self.can('stun', t):
                    # try to stun him
                    return 'stun', closest_enemy.position
                elif closest_enemy_distance < settings.FIREBALL_DISTANCE and self.can('fireball', t) and closest_enemy_distance > settings.FIREBALL_RADIUS:
                    # else try to fireball him, but only if I'm not in range
                    return 'firebal', closest_enemy.position
                elif closest_enemy_distance < settings.HERO_ATTACK_DISTANCE:
                    # else try to attack him
                    return 'attack', closest_enemy.position
                else:
                    # of finally just move to him
                    moves = sort_by_distance(closest_enemy,
                                             possible_moves(self, things))
                    for move in moves:
                        return 'move', move
            else:
                # no enemies, do nothing
                return None

    return simple_hero_logic
