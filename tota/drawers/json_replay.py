import json
from os import path

from tota.game import Drawer


class JsonReplayDrawer(Drawer):
    def __init__(self, replay_dir):
        self.replay_dir = replay_dir
        self.heroes_data_saved = False

    def save_heroes(self, game):
        """Save a json with the detail of the heroes."""
        self.heroes_data_saved = True

        heroes_data = {}
        for hero in game.heroes:
            heroes_data[hero.name] = hero.author

        heroes_path = path.join(self.replay_dir, 'heroes.json')
        with open(heroes_path, 'w') as heroes_file:
            json.dump(heroes_data,
                      heroes_file,
                      indent=2 if game.debug else None)

    def draw(self, game):
        """Draw the world with 'ascii'-art ."""
        if not self.heroes_data_saved:
            self.save_heroes(game)

        things_data = []
        tick_data = {
            't': game.world.t,
            'things': things_data,
            'effects': [{
                            'position': position,
                            'effect': effect,
                        }
                        for position, effect in game.world.effects.items()]
        }

        for thing in game.world.things.values():
            thing_data = {
                'id': id(thing),
                'type': thing.__class__.__name__,
                'position': thing.position,
            }
            if thing_data['type'] != 'Tree':
                is_current_action = thing.last_action_t == game.world.t
                thing_data.update({
                    'life': thing.life,
                    'max_life': thing.max_life,
                    'name': thing.name,
                    'team': thing.team,
                    'level': getattr(thing, 'level', None),
                    'xp': getattr(thing, 'xp', None),
                    'action': thing.last_action if is_current_action else None,
                    'target': thing.last_target if is_current_action else None,
                    'action_done': (thing.last_action_done
                                    if is_current_action else None),
                })

            things_data.append(thing_data)

        tick_path = path.join(self.replay_dir, '%08d.json' % game.world.t)
        with open(tick_path, 'w') as tick_file:
            json.dump(tick_data,
                      tick_file,
                      indent=2 if game.debug else None)
