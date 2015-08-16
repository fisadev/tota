from tota.game import Drawer
from tota import settings

from termcolor import colored


def health_bar(length, life, max_life):
    """Create a small unicode health bar."""
    life = max(life, 0)
    life_chars_count = int(life / (max_life / length))
    life_chars = life_chars_count * '\u2588'
    no_life_chars = (length - life_chars_count) * '\u2591'

    return life_chars + no_life_chars


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

        # print teams stats
        for team in (settings.TEAM_RADIANT, settings.TEAM_DIRE):
            screen += '\n' + colored(team.upper(), settings.TEAM_COLORS[team])

            ancient = game.ancients[team]
            team_heroes = [hero for hero in game.heroes
                           if hero.team == team]

            ancient_template = '{icon} {bar}({life}) Ancient                              '
            ancient_stats = ancient_template.format(
                icon=ancient.ICON_BASIC if self.use_basic_icons else ancient.ICON,
                bar=health_bar(20, ancient.life, ancient.max_life),
                life=int(ancient.life) if ancient.alive else 'destroyed!',
            )

            screen += '\n' + colored(ancient_stats, settings.TEAM_COLORS[team])

            for hero in sorted(team_heroes, key=lambda x: x.name):
                hero_template = '{icon} {bar}({life}) Hero: {name} ({level})              '
                hero_stats = hero_template.format(
                    icon=hero.ICON_BASIC if self.use_basic_icons else hero.ICON,
                    bar=health_bar(20, hero.life, hero.max_life),
                    name=hero.name,
                    life=int(hero.life) if hero.alive else 'dead',
                    level=hero.level,
                )

                screen += '\n' + colored(hero_stats, settings.TEAM_COLORS[team])

        # print events (of last step) for debugging
        if game.debug:
            screen += u'\n'
            screen += u'\n'.join([colored('{}: {}'.format(thing, event),
                                          settings.TEAM_COLORS[thing.team])
                                  for t, thing, event in game.events
                                  if t == game.world.t])
        GO_TO_TOP = '\033[0;0H'
        print(GO_TO_TOP + screen)

