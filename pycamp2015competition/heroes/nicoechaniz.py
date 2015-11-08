from random import choice
import settings
from tota.utils import distance, adjacent_positions, closest, sort_by_distance, adjacent_positions, possible_moves
from random import choice
from tota.things import Hero

from syslog import syslog as log

AUTHOR = "nicoechaniz"

def valid_positions(me, things):
    return [position for position in adjacent_positions(me)
     if (hasattr(things.get(position), "name") and things.get(position).name not in ["tree", "tower"]) or things.get(position) == None]    

def close(something, others, pos):
    """Returns the closest other to something (things/positions)."""
    if others:
        return sort_by_distance(something, others)[pos]

def log(txt):
    pass

def create():

    def rush_hero_logic(self, things, t):
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        enemy_ancient = [e for e in enemies if e.name == 'ancient'][0]
        enemy_tower = [e for e in enemies if e.name == 'tower']
        if enemy_tower: enemy_tower = enemy_tower[0]
        enemy_hero = [e for e in enemies if e.__class__.__name__ == "Hero"]
        if enemy_hero: enemy_hero = enemy_hero[0]
        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        friends = [thing for thing in things.values()
                   if thing.team == self.team and thing != self]
        friendly_ancient = [e for e in friends if e.name == 'ancient'][0]
        back_friends = sort_by_distance(self, friends)[2:]
        closest_friend = closest(self, friends)
        closest_friend_distance = distance(self, closest_friend)
        
        # I'm offside if there are not at least 2 friendlies in front of me
        offside = closest(enemy_ancient, back_friends + [self]) == self 

        # There are enemy units behind me
        enemy_offside = closest(friendly_ancient, enemies + [self]) != self 
#        log("offside: "+ str(offside))
#        log("friend: %s, enemy: %s" % (str(closest_friend), str(closest_enemy)))

        # if I can stun the other hero, that's highest priority
        if closest_enemy and closest_enemy == enemy_hero\
           and closest_enemy_distance <= settings.STUN_DISTANCE and self.can('stun', t):
            # try to stun him
            log('stun !!!')
            return 'stun', closest_enemy.position

        # move to get conver if I'm low on energy or there's an enemy behind me
        if (offside and self.life < 200):# or enemy_offside:
            moves = sort_by_distance(friendly_ancient, valid_positions(self, things))
            return 'move', moves[0]

        if self.life < (self.max_life - settings.HEAL_BASE_HEALING[1]) and self.can('heal', t)\
           and (closest_friend and closest_friend_distance <= settings.HEAL_DISTANCE):
            log("heal")
            return 'heal', self.position

        else:
            if closest_enemy:
                # there is an enemy
#                if closest_enemy_distance <= settings.FIREBALL_DISTANCE and self.can('fireball', t) and closest_enemy_distance > settings.FIREBALL_RADIUS and closest_friend_distance > (settings.FIREBALL_DISTANCE + settings.FIREBALL_RADIUS):
                if self.can('fireball', t) and closest_enemy_distance < settings.FIREBALL_DISTANCE +settings.FIREBALL_RADIUS\
                   and closest_enemy_distance > settings.FIREBALL_RADIUS\
                   and distance(closest_friend, closest_enemy) > settings.FIREBALL_RADIUS:

                    # else try to fireball him, but only if I'm not in range
                    log("fireball !!!")
                    return 'fireball', closest_enemy.position
                elif closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
                    # else try to attack him
                    log("attack")
                    return 'attack', closest_enemy.position


                else:
                    if enemy_tower:
                        if distance(self,enemy_tower) < 5:
                            log("halt")
                            return
                    moves = sort_by_distance(enemy_ancient, valid_positions(self, things))
                    return 'move', moves[0]


    return rush_hero_logic
