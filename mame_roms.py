import os
import os.path
import collections
from lxml import etree
import tempfile
import shutil

MAME_VERSION = '0.177'
MAME_PATH = '/home/drew/mame177' #'/mnt/ext/roms/mame/'
MAME_EXT = '.7z'

# Downloaded from http://www.progettoemma.net/public/cat/cat32en.zip
CATLIST_PATH = os.path.join(os.path.dirname(__file__), 'cat32en')

# Delete these roms from the library
REMOVE_CATS = [
    'Casino',
    'Electromechanical',
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

# TODO load all info upfront
# name
# file
# romdeps
# chd
# device deps
# genre

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

# Parse the mame full xml dump
def load_mame_xml():
    return etree.parse(os.popen('mame -listxml')).getroot()

# Return mame full rom xml indexed by rom name
def mame_roms_xml():
    return dict((e.attrib['name'], e) for e in load_mame_xml())

# Return a map of rom => roms that rom depends on. If filelist passed, dependencies
# are trimmed to those that exist on disk.
def rom_dependencies(xml_index, filelist=None):
    rom_deps = {}
    for name, e in xml_index.iteritems():
        deps = set()
        rom_deps[name] = deps
        for attr in ('romof', 'cloneof'):
            if attr in e.attrib:
                deps.add(e.attrib[attr])
        deps.update(dev.attrib['name'] for dev in e.findall('device_ref'))
        assert all(dep != name for dep in deps)
        assert all(dep in xml_index for dep in deps)

    # TODO need to worry about transitive dependencies?

    if filelist:
        for name in rom_deps.keys():
            rom_deps[name] = filter(lambda dep: dep in filelist, rom_deps[name])

    return dict((k, v) for k, v in rom_deps.iteritems() if v)

def verify_roms():
    output = os.popen('mame -verifyroms -rp "%s"' % MAME_PATH).readlines()
    return set(ln.split()[1] for ln in output if ln.strip().endswith('is bad'))
    
# Remove roms that are in undesired categories and not depended on by any other rom
def cull_roms(xml_index=None, filelist=None, dry_run=False):
    if not xml_index:
        xml_index = mame_roms_xml()
    if not filelist:
        filelist = mame_rom_archives()

    rom_deps = rom_dependencies(xml_index, filelist)
    depended_on = collections.defaultdict(set)
    for rom, deps in rom_deps.iteritems():
        for dep in deps:
            depended_on[dep].add(rom)
            
    genres = rom_genres()
    to_remove = set(rom for rom in xml_index.keys() if genres[rom] in REMOVE_CATS)
    depended_on_by_keepers = set(rom for rom in to_remove if rom in depended_on and any(d not in to_remove for d in depended_on[rom]))
    to_remove -= depended_on_by_keepers
    to_remove_disk = [rom for rom in filelist if rom in to_remove]

    if dry_run:
        return

    before_bad = verify_roms()

    discard_dir = tempfile.mkdtemp()
    for rom in sorted(to_remove_disk):
        print 'discarding', rom
        shutil.move(os.path.join(MAME_PATH, rom + MAME_EXT), discard_dir)
    print 'discards in', discard_dir
        
    after_bad = verify_roms()
    new_bad = after_bad - before_bad
    if new_bad:
        print '!! newly failing roms', new_bad

    with open(os.path.join(MAME_PATH, 'VERSION'), 'w') as f:
        f.write('%s\n' % MAME_VERSION)

def advanced_verify():
    roms = all_mame_roms()
    genres = rom_genres()
    playable_roms = set(r for r in roms if genres[r] not in (REMOVE_CATS + HIDE_CATS))

    for rom in sorted(playable_roms):
        output = os.popen('mame -verifyroms -rp %s %s 2>&1' % (MAME_PATH, rom)).readlines()
        status_ln = [ln for ln in output if ln.startswith('romset ')][0]
        if not any(status_ln.strip().endswith(k) for k in ('is good', 'is best available')):
            print output
        
        
    print len(playable_roms)
    from pprint import pprint
    pprint(sorted(playable_roms))
    
    
if __name__ == "__main__":

    pass
            
#hide non-playable (bad emul); driver status: preliminary?
#hide num players: 0
#isbios/isdevice/ismechanical
