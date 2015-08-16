from tota import actions
from tota import settings
from tota.utils import distance, closest, sort_by_distance, possible_moves


class Thing:
    """Something in the world."""
    ICON = '?'
    ICON_BASIC = '?'

    def __init__(self, name, life, team, acts, position=None):
        if team not in (settings.TEAM_DIRE,
                        settings.TEAM_RADIANT,
                        settings.TEAM_NEUTRAL):
            raise Exception('Invalid team name: {}'.format(team))

        self.name = name
        self.life = life
        self._max_life = life
        self.team = team
        self.position = position
        self.acts = acts

        self.disabled_until = 0

        self.last_uses = {}
        self.possible_actions = {}
        self.possible_actions_cooldowns = {}

        self.last_action_t = None
        self.last_action = None
        self.last_target = None
        self.last_action_done = None

    @property
    def alive(self):
        return self.life > 0

    @property
    def max_life(self):
        return self._max_life

    @max_life.setter
    def max_life(self, value):
        self._max_life = value

    def get_action(self, things, t):
        """Call act to get the next action, and log the results."""
        result = self.act(things, t)
        self.last_action_t = t
        if result is None:
            self.last_action = None
            self.last_target = None
        else:
            action, target_position = result
            self.last_action = action
            self.last_target = target_position

        return result

    def act(self, things, t):
        """The acting logic itself."""
        return None

    def can(self, action, t):
        """Can do an action? (cooldown ready?)"""
        cooldown = self.possible_actions_cooldowns[action]
        last_use = self.last_uses.get(action, -100)
        return last_use + cooldown <= t

    def __str__(self):
        return self.name


class Tree(Thing):
    """The ones that don't move."""
    ICON = '\u03D4'
    ICON_BASIC = 'Y'

    def __init__(self, position=None):
        super().__init__(name='tree',
                         life=settings.TREE_LIFE,
                         team=settings.TEAM_NEUTRAL,
                         acts=False,
                         position=position)


class Creep(Thing):
    """The fodder."""
    ICON = '\u237E'
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
        self.possible_actions_cooldowns = {
            'attack': 0,
            'move': 0,
        }

    def act(self, things, t):
        enemy_team = settings.ENEMY_TEAMS[self.team]
        enemies = [thing for thing in things.values()
                   if thing.team == enemy_team]
        closest_enemy = closest(self, enemies)
        closest_enemy_distance = distance(self, closest_enemy)

        if closest_enemy_distance <= settings.CREEP_ATTACK_DISTANCE:
            # enemy in range, attack!
            return 'attack', closest_enemy.position
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
                                     possible_moves(self, things))
            for move in moves:
                return 'move', move

            return None


class Tower(Thing):
    """Defensive building, can attack enemies."""
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
        self.possible_actions_cooldowns = {
            'attack': 0,
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
    """A player in the game, a powerfull leveling hero with special skills."""
    ICON = '\u046A'
    ICON_BASIC = 'o'

    def __init__(self, name, team, act_function, author, position=None):
        super().__init__(name=name,
                         life=0,
                         team=team,
                         acts=True,
                         position=position)

        self.act_function = act_function
        self.xp = 0
        self.possible_actions = {
            'move': actions.move,
            'attack': actions.hero_attack,
            'heal': actions.heal,
            'fireball': actions.fireball,
            'stun': actions.stun,
        }
        self.possible_actions_cooldowns = {
            'attack': 0,
            'move': 0,
            'heal': settings.HEAL_COOLDOWN,
            'fireball': settings.FIREBALL_COOLDOWN,
            'stun': settings.STUN_COOLDOWN,
        }
        self.respawn_at = 0

        self.author = author

    @property
    def level(self):
        return int(self.xp / settings.XP_TO_LEVEL)

    @property
    def max_life(self):
        health = settings.HERO_LIFE
        health_multiplier = 1 + (self.level * settings.HERO_HEALTH_LEVEL_MULTIPLIER)

        return health * health_multiplier

    def act(self, things, t):
        """The hero act logic is defined in the hero function, call it."""
        return self.act_function(self, things, t)


class Ancient(Thing):
    """The team base, if it is destroyed, the team loses."""
    ICON = '\u265B'
    ICON_BASIC = '@'

    def __init__(self, team, position=None):
        super().__init__(name='ancient',
                         life=settings.ANCIENT_LIFE,
                         team=team,
                         acts=False,
                         position=position)
