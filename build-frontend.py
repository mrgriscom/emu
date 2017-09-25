import os.path
from lxml import etree
import shutil
import re
import mame_roms

ROMS_PATH = '/home/drew/roms'
FRONTEND_CONFIG_ROOT = '/home/drew/dev/emu/configs/emulationstation'

SYSTEMS = [
    {
        'system': 'mame',
        'fullname': 'Arcade',
    },
    {
        'system': 'nes',
        'fullname': 'Nintendo Entertainment System',
    },
    {
        'system': 'fds',
        'fullname': 'Famicom Disk System',
        'theme': 'famicom',
    },
    {
        'system': 'genesis',
        'fullname': 'Sega Genesis / Mega Drive',
        'platform': 'genesis,megadrive',
    },
    {
        'system': 'snes',
        'fullname': 'Super Nintendo',
    },
    {
        'system': 'turbografx',
        'fullname': 'TurboGrafx-16 / PC Engine',
        'theme': 'pcengine',
    },
    {
        'system': '32x',
        'fullname': 'Sega 32X',
        'theme': 'sega32x',
    },
    {
        'system': 'segacd',
        'fullname': 'Sega CD',
        'disc': True,
    },
    {
        'system': 'n64',
        'fullname': 'Nintendo 64',
    },
    {
        'system': 'psx',
        'fullname': 'Sony PlayStation',
        'disc': True,
    },
    {
        'system': 'virtualboy',
        'fullname': 'Virtual Boy',
    },
    {
        'system': 'wii',
        'fullname': 'Wii',
        'ext': ['.wad'],
    },
    {
        'system': 'gameboy',
        'fullname': 'Game Boy',
        'theme': 'gb',
    },
    {
        'system': 'gamegear',
        'fullname': 'Game Gear',
    },
    {
        'system': 'gbc',
        'fullname': 'Game Boy Color',
    },
    {
        'system': 'gba',
        'fullname': 'Game Boy Advance',
    },
]

def get_games(system):
    name = system['system']
    rom_path = os.path.join(ROMS_PATH, name)
    
    if name == 'mame':
        mame_info = mame_roms.load_mame_metadata()
        for rom in mame_roms.playable_roms(mame_info):
            yield {
                'dir': rom_path,
                'file': rom['rom'],
                'name': rom['name'],
            }
    else:
        extensions = ['.cue'] if system.get('disc') else system.get('ext', ['.7z', '.zip'])
        for k in os.listdir(rom_path):
            if not any(k.endswith(ext) for ext in extensions):
                continue
            if k.startswith('[BIOS]'):
                continue
            yield {
                'dir': rom_path,
                'file': k,
                'name': os.path.splitext(k)[0],
            }
    
GAMELIST_DIR = os.path.join(FRONTEND_CONFIG_ROOT, 'gamelists')
LAUNCH_LINKS_DIR = os.path.join(FRONTEND_CONFIG_ROOT, 'launchlinks')
ROULETTE = '_random.game'

for dir in (GAMELIST_DIR, LAUNCH_LINKS_DIR):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)

with open('favorites') as f:
    favorites = filter(None, (ln.strip() for ln in f.readlines() if not ln.startswith('#')))
    
root = etree.Element('systemList')
for system in SYSTEMS:
    name = system['system']

    system_launch_links_dir = os.path.join(LAUNCH_LINKS_DIR, name)
    os.mkdir(system_launch_links_dir)
    # space in subdir is necessary to place before other games (emulationstation groups folder
    # contents in menu and uses path name as sort key)
    system_fav_launch_links_dir = os.path.join(system_launch_links_dir, ' favorites')
    os.mkdir(system_fav_launch_links_dir)

    theme = system.get('theme', name)
    e = etree.SubElement(root, 'system')
    etree.SubElement(e, 'name').text = name
    etree.SubElement(e, 'fullname').text = system['fullname']
    etree.SubElement(e, 'path').text = system_launch_links_dir
    etree.SubElement(e, 'extension').text = '.game'
    etree.SubElement(e, 'command').text = '~/dev/emu/fe-launch.py %ROM%'
    etree.SubElement(e, 'theme').text = theme
    etree.SubElement(e, 'platform').text = system.get('platform', theme)

    gamelist = etree.Element('gameList')
    
    for game in get_games(system):
        is_favorite = any(os.path.join(os.path.split(game['dir'])[1], game['file']) == fav for fav in favorites)

        launch_path = os.path.join(system_launch_links_dir, '%s.game' % os.path.splitext(game['file'])[0])
        with open(launch_path, 'w') as f:
            f.write('%s\n' % os.path.join(game['dir'], game['file']))

        e = etree.SubElement(gamelist, 'game')
        etree.SubElement(e, 'path').text = os.path.join('.', launch_path)
        etree.SubElement(e, 'name').text = game['name']

        if is_favorite:
            fav_launch_path = os.path.join(system_fav_launch_links_dir, '%s.game' % os.path.splitext(game['file'])[0])
            with open(fav_launch_path, 'w') as f:
                f.write('%s\n' % os.path.join(game['dir'], game['file']))

            e = etree.SubElement(gamelist, 'game')
            etree.SubElement(e, 'path').text = os.path.join('.', fav_launch_path)
            etree.SubElement(e, 'name').text = game['name']

    with open(os.path.join(system_launch_links_dir, ROULETTE), 'w'):
        pass
        
    e = etree.SubElement(gamelist, 'game')
    etree.SubElement(e, 'path').text = os.path.join('.', os.path.join(system_launch_links_dir, ROULETTE))
    etree.SubElement(e, 'name').text = ' Surprise Me!'
    #etree.SubElement(e, 'image').text = 'x.jpg'
    
    gamelist_dir = os.path.join(FRONTEND_CONFIG_ROOT, 'gamelists', name)
    os.mkdir(gamelist_dir)
    with open(os.path.join(gamelist_dir, 'gamelist.xml'), 'w') as f:
        f.write(etree.tostring(gamelist, pretty_print=True))

with open(os.path.join(FRONTEND_CONFIG_ROOT, 'es_systems.cfg'), 'w') as f:
    f.write(etree.tostring(root, pretty_print=True))

"""
<gameList>
	<game id="1455" source="theGamesDB.net">
		<desc></desc>
		<image>./downloaded_images/2010 - Street Fighter (Japan)-image.jpg</image>
		<rating>0.7</rating>
		<releasedate>19900808T000000</releasedate>
		<developer>Capcom</developer>
		<publisher>Capcom</publisher>
		<genre>Fighting</genre>
		<region>Japan</region>
		<romtype>Original</romtype>
	</game>
"""
