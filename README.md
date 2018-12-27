# MrSkeltal
This is a proof-of-concept/weekend project to learn vertex skinning.

## Running
The application should run on Python3.4+. If you would like to try the experimental SDL2-ctypes binding, switch to the `sdl2` branch and continue from there.

### Method 1
Install into a virtual environment as an application

    $ python3 -m venv venv
    $ venv/bin/pip install -e.
    $ venv/bin/mr_skeltal --show-skeleton models/cube_test.ms3d

### Method 2
Run as a package in a virtual environment

    $ python3 -m venv venv
    $ venv/bin/pip install -r requirements.txt
    $ venv/bin/python -m mr_skeltal --show-skeleton models/cube_test.ms3d
