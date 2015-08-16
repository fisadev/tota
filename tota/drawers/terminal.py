from tota.game import Drawer
from tota import settings

from termcolor import colored


class TerminalDrawer(Drawer):
    def __init__(self, use_basic_icons=False, use_compressed_view=False):
        self.use_basic_icons = use_basic_icons
        self.use_compressed_view = use_compressed_view

    def position_draw(self, game, position):
        """Get the string to draw for a given position of the world."""
        # decorations first, then things over them
        thing = game.world.things.get(position)
        effect = game.world.effects.get(position)
        effect_color = settings.EFFECT_COLORS.get(effect)

        if thing is not None:
            if self.use_basic_icons:
                icon = thing.ICON_BASIC
            else:
                icon = thing.ICON

            color = settings.TEAM_COLORS[thing.team]
        else:
            icon = ' '
            color = None

        if effect_color is not None:
            on_color = 'on_' + effect_color
        else:
            on_color = None

        if self.use_compressed_view:
            widener = ''
        else:
            widener = ' '

        return colored(icon + widener, color, on_color)

    def draw(self, game):
        """Draw the world with 'ascii'-art ."""
        screen = ''

        # print the world
        screen += '\n'.join(u''.join(self.position_draw(game, (x, y))
                                     for x in range(game.world.size[0]))
                            for y in range(game.world.size[1]))

        # game stats
        screen += '\nticks:{}'.format(game.world.t)

        # print hero stats
        for hero in sorted(game.heroes, key=lambda x: x.name):
            if hero.alive:
                # a small "health bar" with unicode chars, from 0 to 10 chars
                life_chars_count = int((10.0 / hero.max_life) * hero.life)
                life_chars = life_chars_count * '\u2588'
                no_life_chars = (10 - life_chars_count) * '\u2591'
                if self.use_basic_icons:
                    heart = ''
                else:
                    heart = '\u2665 '
                life_bar = heart + '{}{}'.format(life_chars, no_life_chars)
            else:
                if self.use_basic_icons:
                    skull = ''
                else:
                    skull = '\u2620 '
                life_bar = skull + '[dead]'

            hero_template = '{bar}({life}) {name} ({level})                     '
            hero_stats = hero_template.format(bar=life_bar,
                                              name=hero.name,
                                              life=int(hero.life),
                                              level=hero.level)

            screen += '\n' + colored(hero_stats,
                                     settings.TEAM_COLORS[hero.team])

        # print events (of last step) for debugging
        if game.debug:
            screen += u'\n'
            screen += u'\n'.join([colored('{}: {}'.format(thing.name, event),
                                          settings.TEAM_COLORS[thing.team])
                                  for t, thing, event in game.events
                                  if t == game.world.t])
        GO_TO_TOP = '\033[0;0H'
        print(GO_TO_TOP + screen)

