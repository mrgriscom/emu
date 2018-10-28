import os
import os.path
import re

# run from config shaders/ dir

rootdir = 'shaders_glsl/'

def fix_path(preset, ln):
    if '//' in ln:
        ln = ln[:ln.find('//')]
        
    arg, val = ln.split('=')
    arg = arg.strip()
    val = val.strip()
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    fixed_path = os.path.normpath(os.path.join(os.path.split(preset)[0], val))
    return '%s = "%s"' % (arg, fixed_path)

for preset in sorted(os.popen("find %s -iname '*.glslp'" % rootdir).readlines()):
    preset = preset.strip()

    with open(preset) as f:
        data = f.readlines()

    out = []
    for ln in data:
        ln = ln.strip()
        if re.search(r'\.[a-zA-Z]{2}', ln) and '=' in ln:
            ln = fix_path(preset, ln)
        out.append(ln)

    assert preset.startswith(rootdir)
    preset = preset[len(rootdir):]
    outfile = preset.replace('/', '_')

    with open(outfile, 'w') as f:
        f.write('\n'.join(out))
    print outfile
    
