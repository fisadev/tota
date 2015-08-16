import time

from tota.world import World
from tota.things import Ancient, Hero, Creep, Tower, Tree
from tota.utils import closes_empty_position, distance
from tota import settings


def get_hero_function(name):
    """Get the function that has the logic for a specific hero."""
    module = __import__('tota.heroes.' + name, fromlist=['create', ])
    create_function = getattr(module, 'create')

    return create_function()


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
                 debug=False, drawers=None):
        self.radiant_heroes = radiant_heroes
        self.dire_heroes = dire_heroes
        self.map_file_path = map_file_path
        self.debug = debug
        self.drawers = drawers or []

        self.heroes = []
        self.ancients = {}

        self.world = World(world_size, debug=debug)

        self.initialize_world_map()
        self.cache_ancients()
        self.initialize_heroes()

    def initialize_world_map(self):
        """Read map and initialize it."""
        with open(self.map_file_path, encoding='utf-8') as map_file:
            map_text = map_file.read()
            self.world.import_map(map_text)

    def import_map(self, map_text):
        """Import data from a map text."""
        # for each char, create the corresponding object
        for row_index, line in enumerate(map_text.split('\n')):
            for col_index, char in enumerate(line):
                position = (col_index, row_index)

                if char == 'T':
                    self.world.spawn(Tree(), position)
                elif char == 'r':
                    self.world.spawn(Tower(settings.TEAM_RADIANT), position)
                elif char == 'd':
                    self.world.spawn(Tower(settings.TEAM_DIRE), position)
                elif char == 'R':
                    self.world.spawn(Ancient(settings.TEAM_RADIANT), position)
                elif char == 'D':
                    self.world.spawn(Ancient(settings.TEAM_DIRE), position)

    def cache_ancients(self):
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

        for team in (settings.TEAM_DIRE, settings.TEAM_RADIANT):
            self.ancients[team] = get_ancient(team)

    def initialize_heroes(self):
        teams = {
            settings.TEAM_DIRE: self.dire_heroes,
            settings.TEAM_RADIANT: self.radiant_heroes,
        }
        for team, heroes in teams.items():
            for hero_name in heroes:
                hero = Hero(name=hero_name,
                            team=team,
                            act_function=get_hero_function(hero_name))
                self.heroes.append(hero)

    def spawn_near_ancient(self, thing):
        """Spawn players or creeps near their ancient."""
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
                for team in (settings.TEAM_RADIANT, settings.TEAM_DIRE):
                    for i in range(settings.CREEP_WAVE_SIZE):
                        creep = Creep(team)
                        self.spawn_near_ancient(creep)

            self.spawn_heroes()
            self.world.step()
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

    def spawn_heroes(self):
        for hero in self.heroes:
            if hero.respawn_at == self.world.t:
                hero.life = hero.max_life
                self.spawn_near_ancient(hero)

    def update_experience(self):
        for thing in list(self.world.things.values()):
            if not thing.alive:
                for hero in self.heroes:
                    if hero.alive and hero.team != thing.team and distance(hero, thing) < settings.XP_DISTANCE:
                        if isinstance(thing, Creep):
                            hero.xp += settings.XP_CREEP_DEAD
                        elif isinstance(thing, Hero):
                            hero.xp += settings.XP_HERO_DEAD
                        elif isinstance(thing, Tower):
                            hero.xp += settings.XP_TOWER_DEAD

    def clean_deads(self):
        """Remove dead things from the world."""
        for thing in list(self.world.things.values()):
            if not thing.alive:
                self.world.destroy(thing)
                if isinstance(thing, Hero):
                    thing.respawn_at = self.world.t + settings.HERO_RESPAWN_COOLDOWN

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
