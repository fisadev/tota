import random

from tota.things import Tree, Tower, Ancient
from tota.utils import inside_map
from tota import settings


class World:
    """World where to play the game."""
    def __init__(self, size, debug=False):
        self.size = size
        self.debug = debug
        self.things = {}
        self.t = -1
        self.events = []

    def spawn(self, thing, position):
        """Add a thing to the world."""
        if not inside_map(position):
            message = "Can't spawn things outside the map {}".format(position)
            raise Exception(message)

        other = self.things.get(position)
        if other is None:
            self.things[position] = thing
            thing.position = position
        else:
            message = "Can't place {} in a position occupied by {}."
            raise Exception(message.format(thing, other))

    def event(self, thing, message):
        """Log an event."""
        self.events.append((self.t, thing, message))

    def step(self):
        """Forward one instant of time."""
        self.t += 1
        actions = self.get_actions()
        random.shuffle(actions)
        self.perform_actions(actions)

    def get_actions(self):
        """For each thing, call its act method to get its desired action."""
        actions = []
        actors = [thing for thing in self.things.values()
                  if thing.acts]
        for thing in actors:
            if thing.disabled_until > self.t:
                message = 'disabled until {}'.format(thing.disabled_until)
                self.event(thing, message)
            else:
                try:
                    act_result = thing.act(self.things, self.t)
                    if act_result is None:
                        message = 'is idle'
                    else:
                        action, target_position = act_result
                        if action not in self.possible_actions:
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
                    if self.debug:
                        raise

        return actions

    def perform_actions(self, actions):
        """Execute actions, and add their results as events."""
        for thing, action, target_position in actions:
            try:
                action_function = thing.possible_actions[action]
                event = action_function(thing, self, target_position)
                self.event(thing, event)
            except Exception as err:
                message = 'error executing {} action: {}'
                self.event(thing, message.format(action, str(err)))
                if self.debug:
                    raise

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

