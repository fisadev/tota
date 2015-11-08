from tota.utils import closest, distance, sort_by_distance, possible_moves
from tota.things import Tower, Ancient, Creep, Hero
from tota import settings

AUTHOR = "matuu"


def media_position(something, default):
    if len(something) > 0:
        x = 0
        y = 0
        for val in something:
            x += val.position[0]
            y += val.position[1]
        return (x//len(something), y//len(something))
    else:
        return default


def in_radius(position, things, radius):
    list_thing = list()
    for thing in things:
        if distance(position, thing) <= radius:
            list_thing.append(thing)
    return list_thing


def is_older(thing, firsts, seconds, radius):
    return len(in_radius(thing, firsts, radius)) > len(in_radius(thing, seconds, radius))


def create():
    ENEMY_HERO_XP = 0

    def matuuuuu_logic(self, things, t):
        nonlocal ENEMY_HERO_XP
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [ene for ene in things.values() if ene.team == enemy_team]

        friends = [thing for thing in things.values() if thing.team == self.team]

        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        closest_enemy_hero = closest(self, [x for x in enemies if isinstance(x, Hero)])
        if closest_enemy_hero:
            closest_enemy_hero_distance = distance(self, closest_enemy_hero)

        enemy_ancient = [thing for thing in enemies if isinstance(thing, Ancient)]
        if enemy_ancient:
            enemy_ancient = enemy_ancient[0]
        my_ancient = [thing for thing in friends if isinstance(thing, Ancient)]
        if my_ancient:
            my_ancient = my_ancient[0]
        my_tower = [thing for thing in friends if isinstance(thing, Tower)]
        if my_tower:
            my_tower = my_tower[0]
        enemy_tower = [thing for thing in enemies if isinstance(thing, Tower)]
        if enemy_tower:
            enemy_tower = enemy_tower[0]

        friends_creep = [thing for thing in friends if isinstance(thing, Creep)]

        if self.can('heal', t):
            if (self.life < self.max_life and is_older(self.position, friends, enemies, settings.HEAL_RADIUS)) \
                    or self.life < (self.max_life * 0.75):
                return 'heal', self.position
        if closest_enemy or closest_enemy_hero:
            if closest_enemy_hero:
                if closest_enemy_hero_distance <= settings.STUN_DISTANCE and self.can('stun', t):
                    return 'stun', closest_enemy_hero.position
            if (self.can('fireball', t)):
                def throw_fireball(me, ce):
                    if distance(me, ce) <= settings.FIREBALL_DISTANCE and distance(me, ce) > settings.FIREBALL_RADIUS and \
                            is_older(ce, enemies, friends, settings.FIREBALL_RADIUS):
                        return 'fireball', ce.position
                temp_enemies = enemies
                for i in range(3):
                    temp_enemy = closest(self, temp_enemies)
                    if temp_enemy:
                        throw_fireball(self, temp_enemy)
                        temp_enemies = [ene for ene in temp_enemies if ene != temp_enemy]
                    else:
                        break
            if closest_enemy_distance <= settings.HERO_ATTACK_DISTANCE:
                return 'attack', closest_enemy.position
            else:
                moves = None
                if self.xp > 4 and ENEMY_HERO_XP > 2 and self.xp//2 >= ENEMY_HERO_XP:
                    if closest_enemy_hero:
                        ENEMY_HERO_XP = closest_enemy_hero.xp
                        moves = sort_by_distance(closest_enemy_hero, possible_moves(self, things))
                    elif enemy_tower:
                        moves = sort_by_distance(enemy_tower, possible_moves(self, things))
                    else:
                        moves = sort_by_distance(enemy_ancient, possible_moves(self, things))
                else:
                    if closest_enemy_hero:
                        ENEMY_HERO_XP = closest_enemy_hero.xp
                        if distance(self, my_ancient) > distance(closest_enemy_hero, my_ancient):
                            moves = sort_by_distance(my_ancient, possible_moves(self, things))
                        elif my_tower and distance(self, my_tower) > distance(closest_enemy_hero, my_tower):
                            moves = sort_by_distance(my_tower, possible_moves(self, things))

                    if not moves:
                        if my_tower:
                            friends_creep.append(my_tower)
                            moves = sort_by_distance(media_position(friends_creep, my_tower.position), possible_moves(self, things))
                        else:
                            moves = sort_by_distance(media_position(friends_creep, my_ancient.position), possible_moves(self, things))
                if moves:
                    return 'move', moves[0]
        else:
            if enemy_tower:
                moves = sort_by_distance(enemy_tower, possible_moves(self, things))
            else:
                moves = sort_by_distance(enemy_ancient, possible_moves(self, things))
            if moves:
                return 'move', moves[0]
            elif self.life < self.max_life and self.can('heal', t):
                return 'heal', self.position
        return None
    return matuuuuu_logic
