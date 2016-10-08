DISPLAY_DIM = (1920, 1080)
SOURCE_DIM = (384, 224)
SCALE = 1.

stretch = min(*(float(disp) / src for disp, src in zip(DISPLAY_DIM, SOURCE_DIM)))

xstretch = SCALE * .5 * stretch
ystretch = SCALE * stretch
# sep is pixels *before* xstretch is applied
sep = DISPLAY_DIM[0] / stretch + ((1. - SCALE) / SCALE - 1) * SOURCE_DIM[0]

print 'x stretch', xstretch
print 'y stretch', ystretch
print 'separation', sep
