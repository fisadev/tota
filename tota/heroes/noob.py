from random import choice

from tota.utils import adjacent_positions

AUTHOR = 'fisa'


def create():

    def noob_hero_logic(self, things, t):
        actions = 'move', 'attack', 'fireball', 'heal', 'stun'
        positions = adjacent_positions(self.position)

        return 'stun', self.position
        return choice(actions), choice(positions)

    return noob_hero_logic
