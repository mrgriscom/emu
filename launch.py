#!/usr/bin/python

import sys
import os
import collections
from zipfile import ZipFile
import subprocess
import itertools
import tempfile

ROM_ROOT = '/home/drew/roms'

def snes_launch(flags):
    core = 'bsnes_mercury_balanced'
    if 'high-accuracy' in flags:
        core = 'bsnes_mercury_accuracy'
    return retroarch_launch(core)

SYSTEMS = {
    '32x': {
        'launch': lambda _: retroarch_launch('picodrive'),
        'extensions': ['32x'],
        # core lacks multi-tap support
    },
    'fds': {
        'launch': lambda _: retroarch_launch('nestopia'),
        'extensions': ['fds'],
        # bios: disksys.rom
        # multitap: TODO
    },
    'gameboy': {
        'launch': lambda _: retroarch_launch('gambatte'),
        'extensions': ['gb'],
    },
    'gamegear': {
        'launch': lambda _: retroarch_launch('genesis_plus_gx'),
        'extensions': ['gg'],
    },
    'gba': {
        'launch': lambda _: retroarch_launch('mgba'),
        'extensions': ['gba'],
    },
    'gbc': {
        'launch': lambda _: retroarch_launch('gambatte'),
        'extensions': ['gbc'],
    },
    'genesis': {
        'launch': lambda _: retroarch_launch('genesis_plus_gx'),
        'extensions': ['md'],
        # multitap: TODO
    },
    'mame': {
        'launch': lambda _: ['mame'],
        'extensions': [],
    },
    'n64': {
        'launch': lambda _: retroarch_launch('mupen64plus'),
        'extensions': ['n64'],
    },
    'nes': {
        'launch': lambda _: retroarch_launch('nestopia'),
        'extensions': ['nes'],
        # multitap: built-in, handled by NstDatabase.xml (in bios dir)
    },
    'psx': {
        'launch': lambda _: retroarch_launch('mednafen_psx'),
        'extensions': ['cue', 'iso'],
        # bios: scph*.bin
        # multitap: TODO
    },
    'segacd': {
        'launch': lambda _: retroarch_launch('genesis_plus_gx'),
        'extensions': ['cue', 'iso'],
        # bios: bios_CD_U.bin
        # multitap: TODO handled as with geneis?
    },
    'snes': {
        'launch': snes_launch,
        'extensions': ['sfc'],
        # bios: specific games require co-processor ROMs
        #   http://emulation.gametechwiki.com/index.php/Emulator_Files#Super_Famicom_.28SNES.29
        #   "SNES Coprocessor ROMs for bsnes"
        # multitap: TODO
    },
    'turbografx': {
        'launch': lambda _: retroarch_launch('mednafen_pce_fast'),
        'extensions': ['pce'],
        # multitap: built-in
    },
    'virtualboy': {
        'launch': lambda _: retroarch_launch('mednafen_vb'),
        'extensions': ['vb'],
        # sbs rendering handled via custom default shader setting
    },
    'wii': {
        'launch': lambda _: ['dolphin', '-e'],
        'extensions': ['wad'],
        # experimental
    },
}

GAME_OVERRIDES = {
    'high-accuracy': [
        'snes/A.S.P. - Air Strike Patrol (USA)',
    ],
}

def retroarch_launch(core):
    return ['retroarch', '-L', '/usr/lib/x86_64-linux-gnu/libretro/%s_libretro.so' % core]

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
    # TODO could be multiple relevant extensions
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

def make_command(launch, rom):
    rom_id = os.path.splitext(os.path.relpath(os.path.abspath(rom), ROM_ROOT))[0]
    rom_flags = map_reduce(GAME_OVERRIDES.iteritems(), lambda (k, vs): [(v, k) for v in vs], set).get(rom_id, set())
    
    cmd = launch(rom_flags)
    if hasattr(cmd, '__call__'):
        return cmd(rom)
    else:
        return cmd + [rom]

def _log(msg):
    sys.stderr.write(msg + '\n')

if __name__ == "__main__":

    rom = sys.argv[1]

    system = match_system(rom)
    if not system:
        raise RuntimeError('could not determine system')

    cmd = make_command(SYSTEMS[system]['launch'], rom)

    _log('running: %s' % cmd)
    subprocess.call(cmd)
