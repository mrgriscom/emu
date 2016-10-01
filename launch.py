#!/usr/bin/python

import sys
import os
import collections
from zipfile import ZipFile
import subprocess
import itertools
import tempfile

ROM_ROOT = '/mnt/ext/roms'

SYSTEMS = {
    '32x': {
        'emulator': 'kega_fusion',
        'extensions': ['32x'],
    },
    'fds': {
        'emulator': 'mednafen',
        'extensions': ['fds'],
    },
    'gameboy': {
        'emulator': 'mednafen',
        'extensions': ['gb'],
    },
    'gamegear': {
        'emulator': 'mednafen',
        'extensions': ['gg'],
    },
    'gba': {
        'emulator': 'mednafen',
        'extensions': ['gba'],
    },
    'gbc': {
        'emulator': 'mednafen',
        'extensions': ['gbc'],
    },
    'genesis': {
        'emulator': 'mednafen',
        'extensions': ['md'],
    },
    'mame': {
        'emulator': 'mame',
        'extensions': [],
    },
    'n64': {
        'emulator': 'mupen64',
        'extensions': ['n64'],
    },
    'nes': {
        'emulator': 'mednafen',
        'extensions': ['nes'],
    },
    'psx': {
        'emulator': 'mednafen',
        'extensions': ['cue', 'iso'],
    },
    'segacd': {
        'emulator': 'kega_fusion',
        'extensions': ['iso', 'bin'],
    },
    'snes': {
        'emulator': 'mednafen',
        'extensions': ['sfc'],
    },
    'turbografx': {
        'emulator': 'mednafen',
        'extensions': ['pce'],
    },
    'virtualboy': {
        'emulator': 'mednafen',
        'extensions': ['vb'],
    },
}

EMULATORS = {
    'mame': {
        'params': ['-video', 'opengl', '-nofilter', '-rp', '%(romdir)s'],
    },
    'mednafen': {
        # too many params; just use .mednafen/mednafen-09x.cfg
        'audio_lock': True,
    },
    'kega_fusion': {
        'exe': 'kega-fusion',
        'params': ['-fullscreen'],
        # audio lock broken
    },
    'mupen64': {
        'exe': 'mupen64plus',
        # fullscreen broken
        #'params': ['--resolution', '1440x1080'],
        'compression_retarded': True,
    },
}

def extensions():
    return map_reduce(SYSTEMS.iteritems(), lambda (name, meta): [(ext, name) for ext in meta['extensions']])
        
def no_ext():
    return [sys for sys, meta in SYSTEMS.iteritems() if not meta['extensions']]

def get_ext(path):
    return os.path.splitext(path)[1][1:]

def map_reduce(data, emitfunc=lambda rec: [(rec,)], reducefunc=lambda v: v):
    """perform a "map-reduce" on the data

    emitfunc(datum): return an iterable of key-value pairings as (key, value). alternatively, may
        simply emit (key,) (useful for reducefunc=len)
    reducefunc(values): applied to each list of values with the same key; defaults to just
        returning the list
    data: iterable of data to operate on
    """
    mapped = collections.defaultdict(list)
    for rec in data:
        for emission in emitfunc(rec):
            try:
                k, v = emission
            except ValueError:
                k, v = emission[0], None
            mapped[k].append(v)
    return dict((k, reducefunc(v)) for k, v in mapped.iteritems())


def romdir(sys):
    return os.path.join(ROM_ROOT, sys)

def in_romdir(sys, rom):
    parent = os.path.join(romdir(sys), '')
    child = os.path.abspath(rom)
    return child.startswith(parent)

def inspect_zip(rom):
    archive = ZipFile(rom)
    return get_ext(archive.namelist()[0])

def match_system(rom):
    COMPRESSED_FORMATS = {
        'zip': inspect_zip,
    }

    for sys in no_ext():
        if in_romdir(sys, rom):
            return sys

    ext = get_ext(rom)
    if ext in COMPRESSED_FORMATS:
        ext = COMPRESSED_FORMATS[ext](rom)

    matches = extensions()[ext]
    if len(matches) == 1:
        return matches[0]
    else:
        for sys in matches:
            if in_romdir(sys, rom):
                return sys

def make_command(system, emu, meta, rom):
    exe = meta.get('exe', emu)
    params = meta.get('params', [])
    params = map(lambda p: p % {'romdir': romdir(system)}, params)

    if meta.get('compression_retarded'):
        tmp = tempfile.mkdtemp()
        subprocess.call(['unzip', rom, '-d', tmp])
        rom = os.path.join(tmp, os.listdir(tmp)[0])

    cmd = []
    if meta.get('audio_lock'):
        cmd.extend(['pasuspender', '--'])
    cmd.extend(itertools.chain([exe], params, [rom]))
    return cmd


def _log(msg):
    sys.stderr.write(msg + '\n')

if __name__ == "__main__":

    rom = sys.argv[1]

    system = match_system(rom)
    if not system:
        raise RuntimeError('could not determine system')

    emulator = SYSTEMS[system]['emulator']
    cmd = make_command(system, emulator, EMULATORS[emulator], rom)

    _log('running: %s' % cmd)
    subprocess.call(cmd)
