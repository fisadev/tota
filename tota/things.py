from tota import actions
from tota import settings
from tota.utils import distance, closest


class Thing:
    ICON = '?'
    ICON_BASIC = '?'

    """Something in the world."""
    def __init__(self, name, life, team, acts, position=None):
        if team not in (settings.TEAM_DIRE,
                        settings.TEAM_RADIANT,
                        settings.TEAM_NEUTRAL):
            raise Exception('Invalid team name: {}'.format(team))

        self.name = name
        self.life = life
        self.max_life = life
        self.team = team
        self.position = position
        self.acts = acts
        self.disabled_until = 0

    def act(self, things, t):
        return None

    def __str__(self):
        return self.name


class Tree(Thing):
    ICON = '\u03D4'
    ICON_BASIC = 'Y'

    """The ones that don't move."""
    def __init__(self, position=None):
        super().__init__(name='tree',
                         life=settings.TREE_LIFE,
                         team=settings.TEAM_NEUTRAL,
                         acts=False,
                         position=position)


class Creep(Thing):
    ICON = '\u26AB'
    ICON_BASIC = '.'

    def __init__(self, team, position=None):
        super().__init__(name='creep',
                         life=settings.CREEP_LIFE,
                         team=team,
                         acts=True,
                         position=position)

        self.possible_actions = {
            'attack': actions.creep_attack,
            'move': actions.move,
        }

    def act(self, things, t):
        pass


class Tower(Thing):
    ICON = '\u265C'
    ICON_BASIC = 'I'

    def __init__(self, team, position=None):
        super().__init__(name='tower',
                         life=settings.TOWER_LIFE,
                         team=team,
                         acts=True,
                         position=position)

        self.possible_actions = {
            'attack': actions.tower_attack,
        }

    def act(self, things, t):
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        closest_enemy = closest(self, enemies)
        if distance(self, closest_enemy) <= settings.TOWER_ATTACK_DISTANCE:
            return 'attack', closest_enemy.position
        else:
            return None


class Hero(Thing):
    ICON = '\u2689'
    ICON_BASIC = 'o'

    def __init__(self, name, team, act_function, position=None):
        super().__init__(name=name,
                         life=settings.HERO_LIFE,
                         team=team,
                         acts=True,
                         position=position)

        self.act_function = act_function

        self.possible_actions = {
            'move': actions.move,
            'attack': actions.hero_attack,
            'heal': actions.heal,
            'fireball': actions.fireball,
            'stun': actions.stun,
        }

    def act(self, things, t):
        return self.act_function(things, t)


class Ancient(Thing):
    ICON = '\u265B'
    ICON_BASIC = '@'

    def __init__(self, team, position=None):
        super().__init__(name='tower',
                         life=settings.TOWER_LIFE,
                         team=team,
                         acts=False,
                         position=position)
