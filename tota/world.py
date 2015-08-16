from tota.things import Tree, Tower, Ancient
from tota.utils import inside_map
from tota import settings


class World:
    """World where to play the game."""
    def __init__(self, size):
        self.size = size
        self.things = {}
        self.effects = {}
        self.t = 0

    def spawn(self, thing, position):
        """Add a thing to the world."""
        if not inside_map(position, self.size):
            message = "Can't spawn things outside the map {}".format(position)
            raise Exception(message)

        other = self.things.get(position)
        if other is None:
            self.things[position] = thing
            thing.position = position
        else:
            message = "Can't place {} in a position occupied by {}."
            raise Exception(message.format(thing, other))

    def destroy(self, thing):
        """Remove something from the world."""
        del self.things[thing.position]
        thing.position = None

    def import_map(self, map_text):
        """Import data from a map text."""
        # for each char, create the corresponding object
        for row_index, line in enumerate(map_text.split('\n')):
            for col_index, char in enumerate(line):
                position = (col_index, row_index)

                if char == 'T':
                    self.spawn(Tree(), position)
                elif char == 'r':
                    self.spawn(Tower(settings.TEAM_RADIANT), position)
                elif char == 'd':
                    self.spawn(Tower(settings.TEAM_DIRE), position)
                elif char == 'R':
                    self.spawn(Ancient(settings.TEAM_RADIANT), position)
                elif char == 'D':
                    self.spawn(Ancient(settings.TEAM_DIRE), position)
