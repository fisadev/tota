from os import system

from tota.game import Drawer
from tota import settings

from termcolor import colored


def make_bar(length, life, max_life):
    """Create a small unicode bar."""
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
            towers = game.towers[team]
            heroes = [hero for hero in game.heroes
                           if hero.team == team]

            ancient_template = '{icon} {bar}({life}/{max_life}) Ancient                              '
            ancient_stats = ancient_template.format(
                icon=ancient.ICON_BASIC if self.use_basic_icons else ancient.ICON,
                bar=make_bar(20, ancient.life, ancient.max_life),
                life=int(ancient.life) if ancient.alive else 'destroyed!',
                max_life=int(ancient.max_life),
            )

            screen += '\n' + colored(ancient_stats, settings.TEAM_COLORS[team])

            for tower in sorted(towers, key=lambda x: x.position):
                tower_template = '{icon} {bar}({life}/{max_life}) Tower                               '
                tower_stats = tower_template.format(
                    icon=tower.ICON_BASIC if self.use_basic_icons else tower.ICON,
                    bar=make_bar(20, tower.life, tower.max_life),
                    life=int(tower.life) if tower.alive else 'destroyed!',
                    max_life=int(tower.max_life),
                )

                screen += '\n' + colored(tower_stats, settings.TEAM_COLORS[team])

            for hero in sorted(heroes, key=lambda x: x.name):
                hero_template = '{icon} {bar}({life}/{max_life}) Hero: {name}. Lvl {level} {level_bar}'
                hero_stats = hero_template.format(
                    icon=hero.ICON_BASIC if self.use_basic_icons else hero.ICON,
                    bar=make_bar(20, hero.life, hero.max_life),
                    name=hero.name,
                    life=int(hero.life) if hero.alive else 'dead',
                    max_life=int(hero.max_life),
                    level=hero.level,
                    level_bar=make_bar(10, hero.xp % settings.XP_TO_LEVEL,
                                       settings.XP_TO_LEVEL),
                )

                screen += '\n' + colored(hero_stats, settings.TEAM_COLORS[team])

        # print events (of last step) for debugging
        if game.debug:
            screen += u'\n'
            screen += u'\n'.join([colored('{}: {}'.format(thing, event),
                                          settings.TEAM_COLORS[thing.team])
                                  for t, thing, event in game.events
                                  if t == game.world.t])

        if game.debug:
            system('clear')

        GO_TO_TOP = '\033[0;0H'
        print(GO_TO_TOP + screen)

