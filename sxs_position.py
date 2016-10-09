DISPLAY_DIM = (1920, 1080)
SOURCE_DIM = (384, 224)
SCALE = 1.

stretch = min(*(float(disp) / src for disp, src in zip(DISPLAY_DIM, SOURCE_DIM)))

xstretch = SCALE * .5 * stretch
ystretch = SCALE * stretch
# sep unit is pixels *before* xstretch is applied
# this formula makes both sides perfectly overlap. it is possible one might want to
# slightly modify the separation to make it feel more natural. increasing moves the
# scene 'into' the screen. the math is beyond me, though.
sep = DISPLAY_DIM[0] / stretch + ((1. - SCALE) / SCALE - 1) * SOURCE_DIM[0]

print 'x stretch', xstretch
print 'y stretch', ystretch
print 'separation', sep
