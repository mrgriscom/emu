#!/usr/bin/python

import sys
import os
import collections
from zipfile import ZipFile
import subprocess
import itertools
import tempfile

ROM_ROOT = '/home/drew/roms'

SYSTEMS = {
    '32x': {
        'emulator': 'retroarch-pico',
        'extensions': ['32x'],
    },
    'fds': {
        'emulator': 'retroarch-nestopia',
        'extensions': ['fds'],
        'bios': 'required', # disksys.rom
    },
    'gameboy': {
        'emulator': 'retroarch-gambatte',
        'extensions': ['gb'],
    },
    'gamegear': {
        'emulator': 'retroarch-genesisplusgx',
        'extensions': ['gg'],
    },
    'gba': {
        'emulator': 'retroarch-mgba',
        'extensions': ['gba'],
    },
    'gbc': {
        'emulator': 'retroarch-gambatte',
        'extensions': ['gbc'],
    },
    'genesis': {
        'emulator': 'retroarch-genesisplusgx',
        'extensions': ['md'],
    },
    'mame': {
        'emulator': 'mame',
        'extensions': [],
    },
    'n64': {
        'emulator': 'retroarch-mupen64',
        'extensions': ['n64'],
    },
    'nes': {
        'emulator': 'retroarch-nestopia',
        'extensions': ['nes'],
    },
    'psx': {
        'emulator': 'retroarch-beetle-psx',
        'extensions': ['cue', 'iso'],
        'bios': 'required', # scph*.bin
    },
    'segacd': {
        'emulator': 'retroarch-genesisplusgx',
        'extensions': ['cue', 'iso'],
        'bios': 'required', # bios_CD_U.bin
    },
    'snes': {
        'emulator': 'retroarch-bsnes',
        'extensions': ['sfc'],
        'bios': 'certain_games', # *.rom
        # http://emulation.gametechwiki.com/index.php/Emulator_Files#Super_Famicom_.28SNES.29
        # "SNES Coprocessor ROMs for bsnes"

    },
    'turbografx': {
        'emulator': 'retroarch-beetle-pce',
        'extensions': ['pce'],
    },
    'virtualboy': {
        'emulator': 'retroarch-beetle-vb', # sbs rendering handled via custom shader
        'extensions': ['vb'],
    },
    'wii': {
        'emulator': 'dolphin',
        'extensions': ['wad'],
    },
}

EMULATORS = {
    'mame': {},
    'retroarch-bsnes': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/bsnes_mercury_balanced_libretro.so'],
    },
    'retroarch-gambatte': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/gambatte_libretro.so'],
    },
    'retroarch-genesisplusgx': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/genesis_plus_gx_libretro.so'],
    },
    'retroarch-beetle-pce': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/mednafen_pce_fast_libretro.so'],
    },
    'retroarch-beetle-psx': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/mednafen_psx_libretro.so'],
    },
    'retroarch-beetle-vb': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/mednafen_vb_libretro.so'],
    },
    'retroarch-mgba': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/mgba_libretro.so'],
    },
    'retroarch-mupen64': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/mupen64plus_libretro.so'],
    },
    'retroarch-nestopia': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/nestopia_libretro.so'],
    },
    'retroarch-pico': {
        'exe': 'retroarch',
        'params': ['-L', '/usr/lib/libretro/picodrive_libretro.so'],
    },
    'dolphin': {
        'exe': 'dolphin-emu',
        'params': ['-e'],
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
