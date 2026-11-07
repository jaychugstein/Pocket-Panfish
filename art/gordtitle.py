# The title screen: a frying pan flipping a big pumpkinseed beside the POCKET PANFISH logo, 8 frames, with
# "PRESS A" on the first four so the game can blink it. Also the sound screen, 2 frames (ON / OFF).
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K = 4
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32
def dither(g):                                   # g: 0..1 greys -> 1-bit
    H, W = g.shape; t = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    return g > t
def gord(W=60, H=64):
    # three layers at 4x: white fills, half-tone (checker) areas, and black ink lines on top
    L = {n: Image.new('L', (W * K, H * K), 0) for n in ('fill', 'half', 'ink', 'top', 'ink2')}; D = {n: ImageDraw.Draw(L[n]) for n in L}
    f, h, k, t, k2 = D['fill'], D['half'], D['ink'], D['top'], D['ink2']
    def P(*pts): return [(x * K, y * K) for x, y in pts]
    def E(x0, y0, x1, y1): return [x0 * K, y0 * K, x1 * K, y1 * K]
    LW = K + 1
    # shirt: flannel (half-tone checks), suspenders, a button each
    f.polygon(P((0, 64), (1, 53), (11, 48), (41, 48), (51, 53), (52, 64)), 255)
    for x in range(0, 52, 8):
        for y in range(50, 64, 8): h.rectangle(E(x, y, x + 4, y + 4), 255)
    k.line(P((1, 53), (11, 48), (41, 48), (51, 53)), 255, width=LW)
    for x0 in (13, 34):
        h.rectangle(E(x0, 48, x0 + 5, 64), 0); k.rectangle(E(x0, 48, x0 + 5, 64), outline=255, width=K)
        k.ellipse(E(x0 + 1.5, 55, x0 + 3.5, 57), 255)
    f.polygon(P((20, 48), (26, 54), (32, 48)), 255); k.line(P((20, 48), (26, 54), (32, 48)), 255, width=K)
    # the head and ears
    f.ellipse(E(4, 25, 14, 37), 255); f.ellipse(E(38, 25, 48, 37), 255)
    k.ellipse(E(4, 25, 14, 37), outline=255, width=LW); k.ellipse(E(38, 25, 48, 37), outline=255, width=LW)
    k.arc(E(7, 28, 12, 34), 100, 260, 255, width=K); k.arc(E(40, 28, 45, 34), 280, 80, 255, width=K)
    f.ellipse(E(9, 12, 43, 50), 255); k.ellipse(E(9, 12, 43, 50), outline=255, width=LW)
    # stubbly chin (half-tone), cheeks shaded at the sides
    h.chord(E(10, 30, 42, 50), 30, 150, 255); k.ellipse(E(15, 34, 37, 47), 255)   # stubble on the chin
    # the hat: floppy bucket hat, half-tone crown, a lure hooked in the band
    f.polygon(P((0, 19), (52, 19), (47, 24), (5, 24)), 255); k.polygon(P((0, 19), (52, 19), (47, 24), (5, 24)), outline=255, width=LW)
    f.polygon(P((11, 19), (14, 2), (38, 2), (41, 19)), 255); h.polygon(P((13, 13), (15, 3), (37, 3), (39, 13)), 255)
    k.line(P((11, 19), (14, 2), (38, 2), (41, 19)), 255, width=LW)
    k.rectangle(E(11, 13, 41, 17), 255)                                         # dark band
    # eyebrows, crinkly happy eyes with a glint
    k.line(P((15, 26.5), (19, 25), (23, 26)), 255, width=K + 2); k.line(P((29, 26), (33, 25), (37, 26.5)), 255, width=K + 2)
    k.ellipse(E(17, 28, 21.5, 31.5), 255); k.ellipse(E(30.5, 28, 35, 31.5), 255)
    t.rectangle(E(18, 28.6, 19.2, 29.8), 255); t.rectangle(E(31.5, 28.6, 32.7, 29.8), 255)
    k.line(P((13, 29), (15, 30)), 255, width=K); k.line(P((13, 32), (15, 31)), 255, width=K)   # crow's feet
    k.line(P((39, 29), (37, 30)), 255, width=K); k.line(P((39, 32), (37, 31)), 255, width=K)
    # a big round nose
    t.ellipse(E(21, 27, 31, 36), 255)                            # a big round nose, drawn over everything
    k2.arc(E(21, 27, 31, 36), 345, 195, 255, width=K)
    k2.rectangle(E(23, 32.6, 24.6, 34), 255); k2.rectangle(E(27.4, 32.6, 29, 34), 255)   # nostrils
    # the big gummy grin, not a tooth in his head: black mouth, gums along the top, tongue at the bottom
    k.ellipse(E(15, 34, 37, 47), 255)                            # a wide-open grin...
    t.chord(E(13, 29.5, 39, 40.5), 0, 180, 255)                   # ...its top lip curving up into a smile
    k.arc(E(13, 29.5, 39, 40.5), 20, 160, 255, width=K)
    t.ellipse(E(22, 42.5, 30, 46.5), 255)                        # tongue (not a tooth in his head)
    # a fishing rod over his shoulder
    f.line(P((48, 64), (59, 31)), 255, width=K); k.line(P((47, 64), (58, 31)), 0, width=0)
    def g(n): return np.asarray(L[n].resize((W, H), Image.BOX), np.float32) / 255 > 0.5
    fill, half, ink, top, ink2 = g('fill'), g('half'), g('ink'), g('top'), g('ink2')
    yy, xx = np.mgrid[0:H, 0:W]; chk = (xx + yy) % 2 == 0
    out = fill.copy(); out[half & fill] = chk[half & fill]; out[ink] = False; out |= top; out[ink2] = False
    return out
def text(txt, size, font):
    f = ImageFont.truetype(font, size * 8); box = f.getbbox(txt); tw, th = box[2] - box[0], box[3] - box[1]
    t = Image.new('L', (tw + 16, th + 16), 0); ImageDraw.Draw(t).text((8 - box[0], 8 - box[1]), txt, 255, font=f)
    return np.asarray(t.resize((t.width // 8, t.height // 8), Image.BOX), np.float32) / 255 > 0.5
def edge(m):
    p = np.pad(m, 1); H, W = m.shape; o = m.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): o |= p[dy:dy + H, dx:dx + W]
    return o
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf'
def stamp(scr, m, x, y, shadow=True):                    # a word with a dotted drop shadow
    H, W = m.shape; mm = np.zeros_like(scr); mm[y:y + H, x:x + W] = m
    if shadow:
        sh = np.zeros_like(scr); sh[y + 2:y + 2 + H, x + 1:x + 1 + W] = m; yy, xx = np.mgrid[0:64, 0:128]
        scr &= ~edge(mm); scr |= sh & ((xx + yy) % 2 == 0) & ~edge(mm)
    scr |= mm
def centred(scr, m, cx, y, shadow=True): stamp(scr, m, cx - m.shape[1] // 2, y, shadow)
from loon import lou
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
RX = 95                                                   # the middle of the right-hand side
logo = np.zeros((64, 128), bool)
centred(logo, text('POCKET', 9, SERIF), RX, 9)
centred(logo, text('PANFISH', 13, SERIF), RX, 21)
import re, os
FONT = [int(v) for v in re.search(r'\{([^}]*)\}', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font.h')).read()).group(1).split(',')]
def px5(txt):                                             # the game's own crisp 5x7 letters
    m = np.zeros((7, len(txt) * 6 - 1), bool)
    for i, ch in enumerate(txt):
        g = ord(ch) - 32
        for c in range(5):
            for r in range(7): m[r, i * 6 + c] = FONT[g * 5 + c] >> r & 1
    return m
press = np.zeros((64, 128), bool); centred(press, px5('PRESS A'), RX, 47, False)
import importlib.util, math
spec = importlib.util.spec_from_file_location('titlea', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'titlea.py'))
def big_fish(angle):                                      # the big pumpkinseed from titlea.py, turned to any angle
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'titlea.py')).read().split('scr = np.zeros((64, 128), bool)')[0]
    ns = {}; exec(src, ns); return ns['fish'](angle)
def pan(tilt):                                            # a cast-iron frying pan seen from the side, long handle off to the left
    im = Image.new('L', (128 * 8, 64 * 8), 0); d = ImageDraw.Draw(im)
    def R(x, y):                                          # tilt (degrees) lifts the front, pivoting at the handle end
        a = math.radians(-tilt); cx, cy = 2, 53
        return ((cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a)) * 8, (cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)) * 8)
    d.polygon([R(1, 51), R(17, 52), R(17, 55), R(1, 55)], 255)              # the handle
    d.ellipse([R(3, 52)[0], R(3, 52)[1], R(6, 54)[0], R(6, 54)[1]], 0)       # its hanging hole
    d.polygon([R(15, 48), R(61, 48), R(56, 60), R(20, 60)], 255)             # the pan's side
    d.polygon([R(17, 49.5), R(59, 49.5), R(58, 51.5), R(18, 51.5)], 0)       # looking in over the rim
    d.line([R(22, 57), R(54, 57)], 0, width=6)                               # a highlight line on the iron
    return np.asarray(im.resize((128, 64), Image.BOX), np.float32) / 255 > 0.5
def below_rim(tilt):                                      # everything inside / under the pan, below its rim: hidden by the pan
    im = Image.new('L', (128 * 8, 64 * 8), 0); d = ImageDraw.Draw(im); a = math.radians(-tilt); cx, cy = 2, 53
    def R(x, y): return ((cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a)) * 8, (cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)) * 8)
    d.polygon([R(15, 49), R(61, 49), R(64, 72), R(13, 72)], 255)
    return np.asarray(im.resize((128, 64), Image.BOX), np.float32) / 255 > 0.5
def place(f, ang, cx, cy):                                # the big fish centred at (cx, cy)
    fw, fi = big_fish(ang); m = np.pad(fw, 1); e = fw.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): e |= m[dy:dy + 48, dx:dx + 48]
    x0, y0 = cx - 26, cy - 24
    for yy in range(48):
        for xx in range(48):
            Y, X = y0 + yy, x0 + xx
            if 0 <= Y < 64 and 0 <= X < 62 and e[yy, xx]: f[Y, X] = fw[yy, xx] and not fi[yy, xx]
frames = []
# the fish flips up out of the pan and back in: (pan tilt, fish angle, fish centre x, y, fish in front of the pan?, PRESS A shown)
FLIP = ((0, 0, 37, 46, False, 1), (9, 25, 37, 36, True, 1), (10, 70, 36, 25, True, 1), (7, 120, 34, 18, True, 1),
        (4, 175, 33, 16, True, 0), (2, 230, 33, 19, True, 0), (0, 285, 35, 27, True, 0), (0, 335, 37, 37, True, 0))   # 8 frames: a smooth flip
for tilt, ang, fx, fy, front, p in FLIP:
    f = np.zeros((64, 128), bool)
    if front: place(f, ang, fx, fy); f &= ~below_rim(tilt); f |= pan(tilt)   # the fish rising out: the part still in the pan is hidden
    else:
        place(f, ang, fx, fy); pm = pan(tilt); f[pm] = True
        f[49:52, 18:59] &= False                                  # (the pan's inside hides the fish's belly)
        f |= pan(tilt)
        for sx in (24, 36, 48):                                   # sizzle
            for k in range(4): f[37 - k * 2 - (k % 2), sx + (k % 2)] = True
    pb = pan(tilt); f[56:, :62] &= pb[56:, :62]                   # nothing pokes out under the pan
    f[:, 62:] = False; f |= logo
    if p: f |= press
    frames.append(f)
title1 = frames[1]
# the sound screen: a big SOUND, ON or OFF between two arrows, and a little speaker
def sound(on):                                            # the sound screen: a framed panel on a dotted texture, a big speaker, ON / OFF between up and down arrows
    yy, xx = np.mgrid[0:64, 0:128]
    s = ((xx % 4 == 0) & (yy % 4 == 0)) | ((xx % 4 == 2) & (yy % 4 == 2))   # the texture: an even scatter of dots
    im = Image.new('1', (128, 64), 0); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 2, 117, 61], 6, fill=0, outline=1); d.rounded_rectangle([12, 4, 115, 59], 5, fill=0, outline=1)   # the panel, a double frame
    panel = np.zeros((64, 128), bool); pm = Image.new('1', (128, 64), 0); ImageDraw.Draw(pm).rounded_rectangle([10, 2, 117, 61], 6, fill=1)
    s &= ~np.array(pm)
    d.rectangle([25, 30, 30, 41], 1); d.polygon([(30, 30), (38, 23), (38, 48), (30, 41)], 1)   # a big speaker
    if on:
        for r in (5, 9, 13): d.arc([38 - r, 35.5 - r, 38 + r, 35.5 + r], 305, 55, 1, width=2 if r < 13 else 1)   # sound coming out
    else:
        d.line([(42, 30), (50, 41)], 1, width=2); d.line([(50, 30), (42, 41)], 1, width=2)
    cx = 84
    d.polygon([(cx - 7, 26), (cx + 7, 26), (cx, 19)], 1)       # up arrow
    d.polygon([(cx - 7, 48), (cx + 7, 48), (cx, 55)], 1)       # down arrow
    s |= np.array(im)
    centred(s, text('SOUND', 13, SERIF), 64, 5, False)
    w = text('ON' if on else 'OFF', 15, SERIF); centred(s, w, cx, 37 - w.shape[0] // 2, False)
    return s
np.save('titlescr.npy', np.stack(frames)); np.save('soundscr.npy', np.stack([sound(True), sound(False)]))
for n, a in (('title', title1), ('sound_on', sound(True)), ('sound_off', sound(False))):
    Image.fromarray(a.astype(np.uint8) * 255).resize((512, 256), Image.NEAREST).save('/tmp/%s.png' % n)
print('ok')
