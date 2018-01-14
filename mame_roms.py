import os
import os.path
import collections
from lxml import etree
import tempfile
import shutil
import itertools
import re

MAME_VERSION = '0.177'
MAME_PATH = '/home/drew/roms/mame/'
MAME_EXT = '.7z'

def check_versions():
    exe_version = re.search('0[.][0-9]+', os.popen('mame -h').readlines()[0]).group()
    with open(os.path.join(MAME_PATH, 'VERSION')) as f:
        roms_version = f.read().strip()
    versions = {'expected': MAME_VERSION, 'exe': exe_version, 'roms': roms_version}
    assert len(set(versions.values())) == 1, versions
check_versions()
    
# Downloaded from http://www.progettoemma.net/public/cat/cat32en.zip
CATLIST_PATH = os.path.join(os.path.dirname(__file__), 'cat32en')

# Delete these roms from the library
REMOVE_CATS = [
    'Casino',
    'Electromechanical', # includes physical pinball, slot machines
]

# Hide these from the list of playable roms
HIDE_CATS = [
    'Development Systems',
    'Home Systems',
    'Portable Systems',
    'Professional Systems',
    'Synth',
    'System',
    'Utilities',
]

# All other categories
WHITELIST_CATS = [
    'Ball & Paddle',
    'Climbing',
    'Driving',
    'Fighter',
    'Maze',
    'Misc.',
    'Multi-cart Board',
    'Multiplay',
    'Not Classified',
    'Pinball',
    'Platform',
    'Print Club',
    'Puzzle',
    'Quiz',
    'Rhythm',
    'Shooter',
    'Sports',
    'Tabletop',
]

MATURE_EXTRA = ['chiller']

# Consolidate (and sanity check) all mame rom metadata
def load_mame_metadata(xml_index=None):
    if xml_index is None:
        xml_index = mame_roms_xml()
    files = mame_rom_archives()
    categories = rom_genres()
    mature = mature_roms()
    
    all_info = {}
    for name, e in sorted(xml_index.iteritems()):
        info = {}
        all_info[name] = info
        info.update({
            'name': name,
            'title': e.find('description').text,
            'cat': categories[name],
            'device': (e.attrib.get('isdevice') == 'yes'),
            'bios': (e.attrib.get('isbios') == 'yes'),
            'em': (e.attrib.get('ismechanical') == 'yes'),
            'file': (name in files),
            'mature': (name in mature),
        })

        year = None
        e_year = e.find('year')
        if e_year is not None:
            year = e_year.text
            if all(c == '?' for c in year):
                year = None
        info['year'] = year

        info['playable'] = all(not info[k] for k in ('device', 'bios', 'em'))
        # Note: 'em' not entirely synonymous with Electromechanical category
        
        #info['functional'] = False
        # input.players = 0 seems to indicate rom not functional (in addition to non-game devices)
        # How else to detect non-working games?
        
        romof = e.attrib.get('romof')
        cloneof = e.attrib.get('cloneof')
        devices = [ch.attrib['name'] for ch in e.findall('device_ref')]
        info['chd'] = bool(e.findall('disk'))
        # TODO more CHD validation?

        info['romdeps'] = set(filter(None, [romof, cloneof]))
        assert len(info['romdeps']) <= 1
        info['devdeps'] = devices
        assert all(name not in info[k] for k in ('romdeps', 'devdeps'))
        if info['device']:
            assert all(not info[k] for k in ('romdeps', 'devdeps'))
        # Is valid that rom may have no files (either directly or through dependencies)
            
    for name, info in all_info.iteritems():
        for rd in info['romdeps']:
            dep = all_info[rd]
            assert not dep['device']
            # Chained deps are possible.
        for dd in info['devdeps']:
            assert all_info[dd]['device']

    assert all_mame_roms() == set(name for name, info in all_info.iteritems() if not info['device'])
    assert files == set(name for name, info in all_info.iteritems() if info['file'])
    
    return all_info
    
# Parse the mame full xml dump
def load_mame_xml():
    return etree.parse(os.popen('mame -listxml')).getroot()

# Return mame full rom xml indexed by rom name
def mame_roms_xml():
    return dict((e.attrib['name'], e) for e in load_mame_xml())

# List of mame roms that can be launched
def all_mame_roms():
    return set(ln.split()[0] for ln in os.popen('mame -listfull').readlines()[1:])

# List of mame rom archives present on disk
def mame_rom_archives():
    return set(name for name, ext in map(os.path.splitext, os.listdir(MAME_PATH)) if ext == MAME_EXT)

# Parse a category file and return a mapping: category => [roms]
def roms_categories(catfile):
    categories = collections.defaultdict(set)
    current_cat = None
    with open(os.path.join(CATLIST_PATH, catfile)) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            
            if ln.startswith('['):
                current_cat = ln[1:-1]
                if current_cat in ('FOLDER_SETTINGS',):
                    current_cat = None
            else:
                if current_cat:
                    categories[current_cat].add(ln)
    return categories

# Return a map of rom => genre
def rom_genres():
    expected_categories = WHITELIST_CATS + HIDE_CATS + REMOVE_CATS
    roms_by_genre = roms_categories('Genre.ini')
    genres = {}
    for genre, roms in roms_by_genre.iteritems():
        assert genre in expected_categories
        for rom in roms:
            assert rom not in genres
            genres[rom] = genre
    return genres

def mature_roms():
    roms = set(roms_categories('Mature.ini')['* Mature *'])
    return sorted(roms | set(MATURE_EXTRA))

# Return list and metadata of all "playable" roms (visible in front-end)
def playable_roms(all_info, include_hidden=False):
    CATS = WHITELIST_CATS + (HIDE_CATS if include_hidden else [])    
    def process(info):
        if not (info['playable'] and info['cat'] in CATS):
            return

        return {
            'rom': info['name'],
            'name': info['title'],
            'year': info['year'],
            'mature': info['mature'],
        }
    return sorted(filter(None, map(process, all_info.values())), key=lambda e: e['name'])
    
# Remove roms that are in undesired categories and not depended on by any other rom
def cull_roms(all_info, dry_run=False):
    filelist = mame_rom_archives()
    used = set()
    def mark_used(info):
        if info['file']:
            used.add(info['name'])
        for dep in itertools.chain(info['romdeps'], info['devdeps']):
            mark_used(all_info[dep])

    for rom in playable_roms(all_info, True):
        mark_used(all_info[rom['rom']])
    to_remove = sorted(filelist - used)

    if not dry_run:
        before_bad = verify_roms()
        print '%d bad roms to start' % len(before_bad)
        
    discard_dir = tempfile.mkdtemp()
    for f in to_remove:
        print 'discarding', f
        if not dry_run:
            shutil.move(os.path.join(MAME_PATH, f + MAME_EXT), discard_dir)
    print 'discarded %d into %s' % (len(to_remove), discard_dir)

    if not dry_run:
        after_bad = verify_roms() - set(to_remove)  # This verification pass appears to skip most removed roms
        new_bad = after_bad - before_bad
        if new_bad:
            print '!! newly failing roms', new_bad

        # Tag the archive with mame version
        with open(os.path.join(MAME_PATH, 'VERSION'), 'w') as f:
            f.write('%s\n' % MAME_VERSION)

def verify_roms():
    # TODO handle rompath + separate chd path -- currently set in mame config
    output = os.popen('mame -verifyroms').readlines()
    return set(ln.split()[1] for ln in output if ln.strip().endswith('is bad'))


if __name__ == "__main__":

    pass
            
