# The title screen (Nov 2026): underwater. POCKET PANFISH in its own rounded "bubble" lettering, centred; lake weed
# swaying up both sides, sand along the bottom, a hook dangling on its line beside the words, and the PRESS sign.
# The game adds the lake's fish swimming by behind the words.
# Writes titlebg.npy (8 frames of the water, weed and sand), titlelogo.npy (the words: white, mask) and titlehook.npy.
import numpy as np, math
from PIL import Image, ImageDraw
from scipy import ndimage as nd
K = 8
# ---- the lettering: a rounded monoline font, drawn from skeletons with thick round strokes (only the letters needed)
def arc(cx, cy, rx, ry, a0, a1, n=14): return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
GLY = {
 'P': (6, [[(0, 10), (0, 0), (3.5, 0)] + arc(3.5, 2.5, 2.5, 2.5, -90, 90) + [(0, 5)]]),
 'A': (6, [[(0, 10), (0, 3)] + arc(3, 3, 3, 3, 180, 360) + [(6, 10)], [(0, 6.5), (6, 6.5)]]),
 'N': (6, [[(0, 10), (0, 0), (6, 10), (6, 0)]]),
 'F': (5, [[(5, 0), (0, 0), (0, 10)], [(0, 5), (4, 5)]]),
 'I': (0, [[(0, 0), (0, 10)]]),
 'S': (6, [arc(3, 2.5, 3, 2.5, -35, -180, 10) + arc(3, 7.5, 3, 2.5, -90, 145, 16)]),
 'H': (6, [[(0, 0), (0, 10)], [(6, 0), (6, 10)], [(0, 5), (6, 5)]]),
 'O': (6, [arc(3, 5, 3, 5, 0, 360, 28)]),
 'C': (6, [arc(3, 5, 3, 5, -40, -320, 22)]),
 'K': (6, [[(0, 0), (0, 10)], [(5.5, 0), (0, 6)], [(2.2, 3.6), (6, 10)]]),
 'E': (5, [[(5, 0), (0, 0), (0, 10), (5, 10)], [(0, 5), (4, 5)]]),
 'T': (6, [[(0, 0), (6, 0)], [(3, 0), (3, 10)]]),
 'U': (6, [[(0, 0), (0, 7)] + arc(3, 7, 3, 3, 180, 0) + [(6, 0)]]),
 'D': (6, [[(0, 0), (0, 10), (2.5, 10)] + arc(2.5, 5, 3.5, 5, 90, -90) + [(0, 0)]]),
}
def glyph(c, cap, stroke):
    w, paths = GLY[c]; s = (cap - stroke) / 10.0; pad = stroke / 2 + 1
    W = int((w * s + 2 * pad) * K) + 1; H = int((cap + 2) * K)
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im); r = stroke / 2 * K
    for p in paths:
        pts = [((pad + x * s) * K, (pad + y * s) * K) for x, y in p]
        d.line(pts, 255, width=int(stroke * K), joint='curve')
        for x, y in pts: d.ellipse([x - r, y - r, x + r, y + r], 255)
    a = np.asarray(im.resize((W // K, H // K), Image.BOX), np.float32) / 255 > 0.5
    ys, xs = np.where(a); return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
def word(t, cap, stroke, gap):
    gs = [glyph(c, cap, stroke) for c in t]; H = max(g.shape[0] for g in gs); W = sum(g.shape[1] for g in gs) + gap * (len(gs) - 1)
    out = np.zeros((H, W), bool); x = 0
    for g in gs: out[:g.shape[0], x:x + g.shape[1]] = g; x += g.shape[1] + gap
    return out
# the logo: POCKET over PANFISH, centred on each other, with a black edge so nothing behind runs into the letters
pk = word('POCKET', 9, 2, 2); pf = word('PANFISH', 19, 4, 1)
W = pf.shape[1] + 4; H = 14 + pf.shape[0] + 4
logo = np.zeros((H, W), bool)
logo[1:1 + pk.shape[0], (W - pk.shape[1]) // 2:(W - pk.shape[1]) // 2 + pk.shape[1]] |= pk
logo[14:14 + pf.shape[0], 2:2 + pf.shape[1]] |= pf   # (a clear gap under POCKET)
mask = nd.binary_dilation(logo, np.ones((3, 3)))
np.save('titlelogo.npy', np.stack([logo, mask]))
# ---- the hook: eye, shank, bend, point and barb (the game draws its line)
im = Image.new('L', (9 * K, 15 * K), 0); d = ImageDraw.Draw(im)
def P(*p): return [(a * K, b * K) for a, b in p]
x, yl = 6.5, 13.6
d.ellipse(P((x - 1.6, 0.4), (x + 1.6, 3.4)), outline=255, width=K)
d.line(P((x, 3.4), (x, yl - 3)), 255, width=int(K * 1.3))
d.arc(P((x - 6, yl - 7), (x + 0.6, yl + 0.6)), 0, 180, 255, width=int(K * 1.3))
d.line(P((x - 5.7, yl - 3.4), (x - 5.7, yl - 7)), 255, width=int(K * 1.3))
d.line(P((x - 5.7, yl - 7), (x - 3.8, yl - 5)), 255, width=int(K * 1.1))
hook = np.asarray(im.resize((9, 15), Image.BOX), np.float32) / 255 > 0.4
np.save('titlehook.npy', np.stack([hook, nd.binary_dilation(hook)]))
# ---- the water: rippling surface, swaying lake weed (filled ribbons), sand with pebbles; 8 frames of the sway
BLADES = [(5, 44, 0.15, 4.5), (12, 30, -0.2, 4), (0, 24, 0.1, 3.5), (123, 38, -0.15, 4.5), (116, 22, 0.2, 4)]
def frame(f):
    ph = f / 8 * 2 * math.pi; s = np.zeros((64, 128), bool)
    im = Image.new('L', (128 * K, 64 * K), 0); d = ImageDraw.Draw(im)
    for i, (bx, h, lean, w) in enumerate(BLADES):
        left = []; right = []
        for k in range(25):
            t = k / 24; y = 63 - t * h
            x = bx + lean * t * h * 0.15 + math.sin(t * h / 6.0 + ph + i * 1.7) * (1.0 + 2.6 * t)
            ww = w * 0.5 * (1 - t * 0.55) if t < 0.9 else w * 0.5 * 0.45 * (1 - (t - 0.9) / 0.1) + 0.2
            left.append(((x - ww) * K, y * K)); right.append(((x + ww) * K, y * K))
        d.polygon(left + right[::-1], 255)
    s |= np.asarray(im.resize((128, 64), Image.BOX), np.float32) / 255 > 0.45
    for x in range(128):
        y = 61 + int(round(math.sin(x / 9) * 1.0)); s[y:64, x] = False; s[y, x] = True
    for x, y in ((10, 63), (22, 62), (37, 63), (55, 62), (70, 63), (88, 62), (101, 63), (117, 62)): s[y, x] = True
    return s
# the PRESS sign, part of the picture: a white frame, PRESS in the game's font, and a round button that is pushed in
# on frames 3 and 7 (the game shows a frame every 8 ticks)
import re
FONT = [int(v) for v in re.search(r'\{([^}]*)\}', open('font.h').read()).group(1).split(',')]
def text5(s, txt, x, y):
    for c in txt:
        for i in range(5):
            col = FONT[(ord(c) - 32) * 5 + i]
            for j in range(8):
                if col >> j & 1: s[y + j, x + i] = True
        x += 6
def sign(s, pushed):
    x0, y0, w, h = 40, 42, 49, 14
    im = Image.new('L', (128, 64), 0); d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0, y0, x0 + w - 1, y0 + h - 1], radius=3, fill=0, outline=255)
    a = np.asarray(im) > 127; reg = np.zeros_like(a); reg[y0:y0 + h, x0:x0 + w] = True
    inside = nd.binary_fill_holes(a) & reg
    s[inside] = False; s |= a
    text5(s, 'PRESS', 44, 46)
    cx, cy = 81, 49
    yy, xx = np.mgrid[0:64, 0:128]; dd = np.hypot(xx - cx, yy - cy)
    s |= (dd > 3.5) & (dd < 4.5)                                   # the ring
    c = cy if pushed else cy - 1
    cap = np.hypot(xx - cx, yy - c) < 2.4; s |= cap
HK = None
def framed(f):
    s = frame(f); sign(s, f in (3, 7))
    hy = 15 + ((f >> 2) & 1)                                       # the hook bobs gently on its line
    s[2:hy, 117] = True; hm = nd.binary_dilation(hook); r = s[hy:hy + 15, 111:120]; r[hm] = hook[hm]
    return s
B = [["....." , ".....", "..X..", ".....", "....."], [".....", "..X..", ".X.X.", "..X..", "....."], [".XXX.", "X...X", "X.X.X", "X...X", ".XXX."]]
bw = np.array([[[c == 'X' for c in r] for r in f] for f in B]); np.save('titlebub.npy', bw)   # three bubble sizes
np.save('titlebg.npy', np.stack([framed(f) for f in range(8)]))
prev = framed(0).copy(); lx = (128 - W) // 2
m = mask; prev[3:3 + H, lx:lx + W][m] = logo[m]
Image.fromarray((prev * 255).astype(np.uint8)).resize((512, 256), Image.NEAREST).save('title2_preview.png')
print('logo', logo.shape)

# ---- the sound screen, 2 frames (ON, OFF): the same water and weed, SOUND in the lettering; the chosen word is solid,
# the other just an outline
def sound(on):
    s = frame(0)
    words = [('ON', 29), ('OFF', 45)]
    sd = word('SOUND', 15, 3, 1); ys = 6; xs = (128 - sd.shape[1]) // 2
    m = nd.binary_dilation(sd, np.ones((3, 3))); r = s[ys:ys + sd.shape[0], xs:xs + sd.shape[1]]; r[m] = sd[m]
    for k, (t, y) in enumerate(words):
        w = word(t, 11, 3, 2); x = (128 - w.shape[1]) // 2
        g = w if (k == 0) == on else (w & ~nd.binary_erosion(w))
        m = nd.binary_dilation(w, np.ones((3, 3))); r = s[y:y + w.shape[0], x:x + w.shape[1]]; r[m] = g[m]
    return s
snd = np.stack([sound(True), sound(False)]); np.save('soundscr.npy', snd)
Image.fromarray((np.hstack([snd[0], np.zeros((64, 4), bool), snd[1]]) * 255).astype(np.uint8)).resize((1040, 256), Image.NEAREST).save('sound_preview.png')
