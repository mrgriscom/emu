#!/usr/bin/python

import sys
import os.path
import subprocess
import random
from datetime import datetime

RANDOM_LOG = '/tmp/emu_rand.log'

launch_script = os.path.join(os.path.dirname(sys.argv[0]), 'launch.py')
launcher = sys.argv[1]

if os.path.split(launcher)[1].startswith('_random'):
    dir = os.path.dirname(launcher)
    games = [k for k in os.listdir(dir) if not k.startswith('_random')]
    game = random.choice(games)
    launcher = os.path.join(dir, game)

    with open(RANDOM_LOG, 'a') as f:
        f.write('%s %s\n' % (datetime.now(), launcher))

with open(launcher) as f:
    arg = f.read().strip()

subprocess.call([launch_script, arg])
