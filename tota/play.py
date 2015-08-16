#!/usr/bin/env python
"""Tota game runner.

Usage:
    ./play.py --help
    ./play.py RADIANT_HEROES DIRE_HEROES [-m MAP] [-s SIZE] [-d] [-b] [-f MAX_FRAMES] [-c] [-r REPLAY_DIR] [-q]

    DIRE_HEROES and RADIANT_HEROES must be comma separated lists

Options:
    -h --help            Show this help.
    -m MAP               The path to the map file to use (there is a default
                         map)
    -s SIZE              The size of the world. Format: COLUMNSxROWS
    -d                   Debug mode (lots of extra info, and step by
                         step game play)
    -f MAX_FRAMES        Maximum frames per second [default: 2].
    -b                   Use basic icons if you have trouble with the
                         normal icons.
    -c                   Use a compressed view if the default one is too wide
                         for your terminal.
    -r REPLAY_DIR        Save a json replay, which consists in *lots* of files
                         (1 per tick) inside the specified dir.
    -q                   Don't draw the map in the terminal.
"""
import os
from docopt import docopt

from tota.game import Game
from tota.drawers.terminal import TerminalDrawer
from tota.drawers.json_replay import JsonReplayDrawer

DEFAULT_MAP_SIZE = (87, 33)
DEFAULT_MAP_PATH = './map.txt'


def play():
    """Initiate a game, using the command line arguments as configuration."""
    arguments = docopt(__doc__)

    # start a game
    # parse arguments
    debug = arguments['-d']
    use_basic_icons = arguments['-b']
    use_compressed_view = arguments['-c']
    max_frames = int(arguments['-f'])

    radiant_heroes = arguments['RADIANT_HEROES'].split(',')
    dire_heroes = arguments['DIRE_HEROES'].split(',')

    drawers = []
    if not arguments['-q']:
        drawers.append(TerminalDrawer(use_basic_icons=use_basic_icons,
                                      use_compressed_view=use_compressed_view))

    if arguments['-r']:
        replay_dir = arguments['-r']
        drawers.append(JsonReplayDrawer(replay_dir=replay_dir))

    size = arguments['-s']
    if size:
        size = tuple(map(int, size.split('x')))
    else:
        size = DEFAULT_MAP_SIZE

    map_path = arguments['-m'] or DEFAULT_MAP_PATH

    # create and start game
    g = Game(radiant_heroes=radiant_heroes,
             dire_heroes=dire_heroes,
             map_file_path=map_path,
             world_size=size,
             debug=debug,
             drawers=drawers)
    os.system('clear')
    g.play(max_frames)


if __name__ == '__main__':
    play()
