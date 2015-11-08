__author__ = 'frodriguez'

from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota.settings import STUN_DISTANCE, ENEMY_TEAMS, FIREBALL_RADIUS, FIREBALL_DISTANCE, HERO_ATTACK_DISTANCE
from tota.things import Ancient, Hero, Tower, Creep

AUTHOR = 'francusa'


def create():
    def pulenta_hero_logic(self, things, t):
        # some useful data about the enemies I can see in the map
        enemy_team = ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]

        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        # now lets decide what to do
        if self.can('heal', t) and self.life < self.max_life:
            # if I'm hurt and can heal, heal
            return 'heal', self.position
        else:
            # else, try to attack
            if closest_enemy:
                if closest_enemy_distance <= STUN_DISTANCE and self.can('stun', t):
                    # try to stun him
                    return 'stun', closest_enemy.position
                elif FIREBALL_RADIUS < closest_enemy_distance <= FIREBALL_DISTANCE \
                        and self.can('fireball', t):
                    # else try to fireball him, but only if I'm not in range
                    return 'fireball', closest_enemy.position
                elif closest_enemy_distance <= HERO_ATTACK_DISTANCE:
                    # else try to attack him
                    return 'attack', closest_enemy.position
                # elif closest_enemy_distance < settings.STUN_DISTANCE and self.can('stun', t):
                #     # try to stun him
                #     return 'stun', closest_enemy.position
                # else:
                    # of finally just move to him
                else:
                    their_base = [thing for thing in things.values()
                                  if thing.team == enemy_team and isinstance(thing, Ancient)][0]
                    my_tower = [thing for thing in things.values()
                                if thing.team == self.team and isinstance(thing, Tower)]
                    my_team = [thing for thing in things.values()
                               if thing.team == self.team and isinstance(thing, Creep)]
                    closest_to_base = closest(their_base, my_team)
                    my_team_wo_closest = [thing for thing in things.values()
                                          if thing.team == self.team and isinstance(thing, Creep)
                                          and thing != closest_to_base]
                    snd_closest_to_base = closest(their_base, my_team_wo_closest)
                    enemies_close = [thing for thing in things.values()
                                     if thing.team == enemy_team
                                     and (isinstance(thing, Creep) or isinstance(thing, Hero))
                                     and distance(thing, their_base) < distance(self, their_base)]
                    #my_team_pos = map(lambda x: x.position, my_team)
                    team_reference = snd_closest_to_base if snd_closest_to_base is not None \
                        else closest_to_base

                    if self.max_life < 300:
                        if my_tower:
                            my_tower = my_tower[0]
                            element = my_tower
                        else:
                            element = team_reference
                    # elif len(enemies_close) > 2:
                    #     element = snd_closest_to_base
                    elif distance(their_base, team_reference) > distance(their_base, self):
                        if len(enemies_close) > 2:
                            element = team_reference
                        elif len(enemies_close) > 1:
                            return None
                        else:
                            element = their_base
                    else:
                        element = their_base
                    # else:
                    #     element = [thing for thing in things.values()
                    #                if thing.team == enemy_team and isinstance(thing, Ancient)][0]

                    moves = sort_by_distance(element,
                                             possible_moves(self, things))
                    if moves:
                        return 'move', moves[0]
                return None

    return pulenta_hero_logic
