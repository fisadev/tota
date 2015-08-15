import json
from os import path

from tota.game import Drawer


class JsonReplayDrawer(Drawer):
    def __init__(self, replay_dir):
        self.replay_dir = replay_dir

    def draw(self, game):
        """Draw the world with 'ascii'-art ."""
        things_data = []
        tick_data = {
            't': game.world.t,
            'things': things_data,
            'effects': game.world.effects,
        }

        for thing in game.world.things.values():
            thing_data = {
                'id': id(thing),
                'type': thing.__class__.__name__,
                'position': thing.position,
            }
            if thing_data['type'] != 'Tree':
                thing_data.update({
                    'life': thing.life,
                    'name': thing.name,
                    'team': thing.team,
                    'level': getattr(thing, 'level', None),
                    'xp': getattr(thing, 'xp', None),
                    'action': thing.last_action,
                    'target': thing.last_target,
                })

            things_data.append(thing_data)

        tick_path = path.join(self.replay_dir, '%08d.json' % game.world.t)
        with open(tick_path, 'w') as tick_file:
            json.dump(tick_data,
                      tick_file,
                      indent=2 if game.debug else None)
