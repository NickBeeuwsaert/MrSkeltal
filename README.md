# MrSkeltal
This is a proof-of-concept/weekend project to learn vertex skinning.

## Running
The code is meant to be run on Python 3.6. However, it should run on Python3.4+
if you switch to the `python3.4` branch

In addition to the master branch using pygame, there is also an experimental SDL2 binding in the `sdl2` branch.

if you want to run on python3.4+ and use SDL2, merge the `python3.4` branch and `sdl2` branch in a new branch

### Method 1
Install into a virtual environment as an application

    $ python3 -m venv venv
    $ venv/bin/pip install -e.
    $ venv/bin/mr_skeltal --show-skeleton models/cube_test.ms3d

### Method 2
Run as a package in a virtual environment

    $ python3 -m venv
    $ venv/bin/pip install -r requirements.txt
    $ venv/bin/python -m mr_skeltal --show-skeleton models/cube_test.ms3d
