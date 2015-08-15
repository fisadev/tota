Tota
====

Tota is a game in which you play **programming** simple bots, which will have  to
win a game *similar* to DotA.

Getting started
===============

The game isn't packaged for PyPI or anything, it's meant to be a playground, so just
clone the code, install its dependencies, and get inside the ``tota`` folder to
start messing around:


.. code-block:: bash

    git clone https://github.com/fisadev/tota.git
    cd tota
    sudo pip install -r requirements.txt

(If you know about virtualenv, use it!)


And now lets just run a simple demo game:


.. code-block:: bash

    PYTHONPATH=. python3 tota/play.py simple simple -f 10

(**Yes**, it needs **python3**)

The parameters of the ``play.py`` script are very easy to understand, just run 
it with ``--help`` (``simple`` is the name of a very simple hero already implemented
in the game).

The fun part: how to create your own heroes
===========================================

To create a hero you need to create a python module inside the ``heroes`` folder, 
with your hero name as module name. For example ``heroes/terminator.py``.

Inside your hero module, you have to define 2 things: a hero function and a ``create`` 
function.

Your hero function
------------------

It should be a simple function which receives 3 parameters:

* ``self``: your hero instance (created by the game)
* ``things``: a dictionary of all the things in the world, with the positions as keys.
* ``t``: the current time

This function will be called each game instant, so your hero can think and 
decide what to do next. 

The result of the function must be a tuple. This tuple has two parts:

* An action string: the name of the action you want to perform.
* A position tuple: the position to which you want to perform that action.

Example of a valid result: ``return "attack", (10, 2)``

This is an example of a very, very basic hero who only throws fireballs at 
himself:


.. code-block:: python

    # tota/heroes/fireballer.py
    def create():

        def fireballer_logic(self, things, t):
            return 'fireball', self.position

        return fireballer_logic


If your hero doesn't feel like doing anything useful, it could also return just 
None, and no action will be performed. He will just stand still, watching as 
his fellow creeps fight endless hordes of enemies without his help.

And also, there are other useful things for your hero:

* ``self.life``: amount of current life.
* ``self.position``: your current position on the map.
* ``self.can('some action', t)``: check if you can perform an action at the given time.
* ``self.last_uses``: a dictionary of the last time you used each skill with cooldown.
* and **more**! For a nice example, look at ``tota/heroes/simple.py``.


