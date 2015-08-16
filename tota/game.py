from collections import defaultdict
import random
import time

from tota.world import World
from tota.things import Ancient, Hero, Creep, Tower, Tree
from tota.utils import closes_empty_position, distance
from tota import settings


def get_hero_implementation(name):
    """Get the function that has the logic for a specific hero."""
    module = __import__('tota.heroes.' + name, fromlist=['create', 'AUTHOR'])
    create_function = getattr(module, 'create')
    author = getattr(module, 'AUTHOR')

    return create_function(), author


class Drawer:
    """Something that has the ability to 'draw' the game in some format."""
    def draw(self, game):
        """Draw a tick of the game."""
        pass


class Game:
    """An instance of game controls the flow of the game.

       This includes player and creeps spawning, game main loop, deciding when
       to stop, importing map data, drawing each update, etc.
    """
    def __init__(self, radiant_heroes, dire_heroes, map_file_path, world_size,
                 debug=False, protected=False, drawers=None):
        self.radiant_heroes = radiant_heroes
        self.dire_heroes = dire_heroes
        self.map_file_path = map_file_path
        self.debug = debug
        self.protected = protected
        self.drawers = drawers or []

        self.heroes = []
        self.ancients = {}
        self.towers = {}
        self.events = []
        self.scores = defaultdict(lambda: 0)

        self.world = World(world_size)

        self.initialize_world_map()
        self.cache_structures()
        self.initialize_heroes()

    def initialize_world_map(self):
        """Read map and initialize it."""
        with open(self.map_file_path, encoding='utf-8') as map_file:
            map_text = map_file.read()
            self.world.import_map(map_text)

    def cache_structures(self):
        """
        Find each team's structures, and store it dicts for faster access.
        """
        def get_ancient(team):
            ancients = [thing for thing in self.world.things.values()
                        if isinstance(thing, Ancient) and thing.team == team]
            if not ancients:
                message = "Can't find the ancient for the {} team".format(team)
                raise Exception(message)
            elif len(ancients) > 1:
                message = "Team {} has 2 ancients".format(team)
                raise Exception(message)
            else:
                return ancients[0]

        def get_towers(team):
            return [thing for thing in self.world.things.values()
                    if isinstance(thing, Tower) and thing.team == team]

        for team in (settings.TEAM_DIRE, settings.TEAM_RADIANT):
            self.ancients[team] = get_ancient(team)
            self.towers[team] = get_towers(team)

    def initialize_heroes(self):
        """
        Instantiate each hero and add it to the list.
        """
        teams = {
            settings.TEAM_DIRE: self.dire_heroes,
            settings.TEAM_RADIANT: self.radiant_heroes,
        }
        for team, heroes in teams.items():
            for hero_name in heroes:
                hero_function, author = get_hero_implementation(hero_name)
                hero = Hero(name=hero_name,
                            team=team,
                            act_function=hero_function,
                            author=author)
                self.heroes.append(hero)

    def spawn_near_ancient(self, thing):
        """Spawn something near its ancient."""
        # start searching from the ancient position, outwards, until an empty
        # space is found, using breadth first graph search
        ancient = self.ancients[thing.team]
        spawn_at = closes_empty_position(ancient, self.world)
        if spawn_at:
            self.world.spawn(thing, spawn_at)
        else:
            message = "Can't spawn {} near its ancient".format(thing.name)
            raise Exception(message)

    def play(self, frames_per_second=2.0):
        """Game main loop, ending in a game result with description."""
        while True:
            # spawn creep wave
            if self.world.t % settings.CREEP_WAVE_COOLDOWN == 0:
                self.event(self, 'Spawn creep waves')
                for team in (settings.TEAM_RADIANT, settings.TEAM_DIRE):
                    for i in range(settings.CREEP_WAVE_SIZE):
                        creep = Creep(team)
                        self.spawn_near_ancient(creep)

            self.spawn_heroes()
            self.step()
            self.update_experience()
            self.clean_deads()

            self.draw()

            self.world.effects = {}

            if self.debug:
                input()
            else:
                time.sleep(1.0 / frames_per_second)

            if self.game_ended():
                description = self.game_result()
                print('')
                print(description)

                return description

    def step(self):
        """Forward one instant of time."""
        self.world.t += 1
        actions = self.get_actions()
        random.shuffle(actions)
        self.perform_actions(actions)

    def get_actions(self):
        """For each thing, call its act method to get its desired action."""
        actions = []
        actors = [thing for thing in self.world.things.values()
                  if thing.acts]
        for thing in actors:
            if thing.disabled_until > self.world.t:
                message = 'disabled until {}'.format(thing.disabled_until)
                self.event(thing, message)
            else:
                try:
                    act_result = thing.get_action(self.world.things,
                                                  self.world.t)
                    if act_result is None:
                        message = 'is idle'
                    else:
                        action, target_position = act_result
                        if action not in thing.possible_actions:
                            message = 'returned unknown action {}'.format(action)
                        else:
                            actions.append((thing, action, target_position))
                            message = 'wants to {} into {}'.format(action,
                                                                   target_position)
                        self.event(thing, message)
                except Exception as err:
                    message = 'error with act from {}: {}'.format(thing.name,
                                                                  str(err))
                    self.event(thing, message)
                    if not self.protected:
                        raise

        return actions

    def perform_actions(self, actions):
        """Execute actions, and add their results as events."""
        for thing, action, target_position in actions:
            try:
                action_function = thing.possible_actions[action]
                done, event = action_function(thing, self.world, target_position)
                if done:
                    thing.last_uses[action] = self.world.t
                thing.last_action_done = done
                self.event(thing, event)
            except Exception as err:
                message = 'error executing {} action: {}'
                self.event(thing, message.format(action, str(err)))
                if not self.protected:
                    raise

    def event(self, thing, message):
        """Log an event."""
        self.events.append((self.world.t, thing, message))

    def spawn_heroes(self):
        """Spawn heros that need to spawn (dead or start of the game)."""
        for hero in self.heroes:
            if hero.respawn_at == self.world.t:
                hero.life = hero.max_life
                self.event(hero, 'spawned')
                self.spawn_near_ancient(hero)

    def update_experience(self):
        """Add the experience gained for being close to enemy deads."""
        for thing in list(self.world.things.values()):
            if not thing.alive:
                for hero in self.heroes:
                    if hero.alive and hero.team != thing.team and distance(hero, thing) < settings.XP_DISTANCE:
                        xp_gain = 0
                        if isinstance(thing, Creep):
                            xp_gain = settings.XP_CREEP_DEAD
                        elif isinstance(thing, Hero):
                            xp_gain = settings.XP_HERO_DEAD
                        elif isinstance(thing, Tower):
                            xp_gain = settings.XP_TOWER_DEAD
                        hero.xp += xp_gain

                        self.event(hero, 'gained {} xp'.format(xp_gain))

    def clean_deads(self):
        """Remove dead things from the world."""
        for thing in list(self.world.things.values()):
            if not thing.alive:
                self.world.destroy(thing)
                self.event(thing, 'died')
                if isinstance(thing, Hero):
                    thing.respawn_at = self.world.t + settings.HERO_RESPAWN_COOLDOWN
                if isinstance(thing, (Hero, Tower)):
                    enemy_team = settings.ENEMY_TEAMS[thing.team]
                    self.scores[enemy_team] += 1

    def draw(self):
        """Call each drawer instance."""
        for drawer in self.drawers:
            drawer.draw(self)

    def destroyed_ancients(self):
        """Which ancients have been destroyed?"""
        return [ancient for ancient in self.ancients.values()
                if not ancient.alive]

    def game_ended(self):
        """Has the game ended?"""
        return len(self.destroyed_ancients()) > 0

    def game_result(self):
        """Was the game won?"""
        return '\n'.join('Team {} lost!'.format(ancient.team)
                         for ancient in self.destroyed_ancients())
