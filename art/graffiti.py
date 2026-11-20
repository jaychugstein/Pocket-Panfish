# Fat graffiti-style bubble letters for the title (Nov 20 2026), drawn by hand: solid, puffy, round letters that squish
# into each other, each one sitting on top of the one before with a black keyline between them, and the whole word
# wrapped in a white outline like a sticker. The i in PANFISH is a lowercase one with a fat dot, for fun.
import numpy as np
from scipy import ndimage as nd
BIG = {   # PANFISH: 17 tall
'P': """
.XXXXXXXX...
XXXXXXXXXXX.
XXXXXXXXXXXX
XXXX...XXXXX
XXXX...XXXXX
XXXX...XXXXX
XXXXXXXXXXXX
XXXXXXXXXXXX
XXXXXXXXXXX.
XXXXXXXXX...
XXXXX.......
XXXXX.......
XXXXX.......
XXXXX.......
XXXXX.......
XXXXX.......
.XXX........""",
'A': """
....XXXXX....
..XXXXXXXXX..
.XXXXXXXXXXX.
XXXXXX.XXXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
.XXX.....XXX.""",
'N': """
.XXX.....XXX.
XXXXX...XXXXX
XXXXXX..XXXXX
XXXXXXX.XXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXX.XXXXXXX
XXXXX..XXXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
.XXX.....XXX.""",
'F': """
.XXXXXXXXX.
XXXXXXXXXXX
XXXXXXXXXXX
XXXXXXXXXX.
XXXXX......
XXXXX......
XXXXXXXXX..
XXXXXXXXXX.
XXXXXXXXX..
XXXXX......
XXXXX......
XXXXX......
XXXXX......
XXXXX......
XXXXX......
XXXXX......
.XXX.......""",
'I': """
.XXX.
XXXXX
XXXXX
.XXX.
.....
.XXX.
XXXXX
XXXXX
XXXXX
XXXXX
XXXXX
XXXXX
XXXXX
XXXXX
XXXXX
XXXXX
.XXX.""",
'S': """
..XXXXXXXX..
.XXXXXXXXXXX
XXXXXXXXXXXX
XXXXX...XXX.
XXXXX.......
XXXXXX......
.XXXXXXXXX..
..XXXXXXXXX.
....XXXXXXXX
.......XXXXX
.......XXXXX
.XXX...XXXXX
XXXXX.XXXXXX
XXXXXXXXXXXX
XXXXXXXXXXXX
.XXXXXXXXXX.
..XXXXXXXX..""",
'H': """
.XXX.....XXX.
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXXXXXXXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
XXXXX...XXXXX
.XXX.....XXX.""",
}
SMALL = {   # POCKET: 12 tall
'P': """
.XXXXXX..
XXXXXXXX.
XXXXXXXXX
XXXX..XXX
XXXX..XXX
XXXXXXXXX
XXXXXXXX.
XXXXXXX..
XXXX.....
XXXX.....
XXXX.....
.XX......""",
'O': """
..XXXXXX..
.XXXXXXXX.
XXXXXXXXXX
XXXX..XXXX
XXXX..XXXX
XXXX..XXXX
XXXX..XXXX
XXXX..XXXX
XXXXXXXXXX
XXXXXXXXXX
.XXXXXXXX.
..XXXXXX..""",
'C': """
..XXXXXX.
.XXXXXXXX
XXXXXXXXX
XXXX..XX.
XXXX.....
XXXX.....
XXXX.....
XXXX.....
XXXX..XX.
XXXXXXXXX
.XXXXXXXX
..XXXXXX.""",
'K': """
.XX....XX.
XXXX..XXXX
XXXX.XXXXX
XXXXXXXXX.
XXXXXXXX..
XXXXXXX...
XXXXXXX...
XXXXXXXX..
XXXXXXXXX.
XXXX.XXXXX
XXXX..XXXX
.XX....XX.""",
'E': """
.XXXXXXX
XXXXXXXX
XXXXXXXX
XXXX....
XXXXXXX.
XXXXXXX.
XXXXXXX.
XXXX....
XXXX....
XXXXXXXX
XXXXXXXX
.XXXXXXX""",
'T': """
.XXXXXXXX.
XXXXXXXXXX
XXXXXXXXXX
.XXXXXXXX.
...XXXX...
...XXXX...
...XXXX...
...XXXX...
...XXXX...
...XXXX...
...XXXX...
....XX....""",
}
def letter(c, big):
    rows = (BIG if big else SMALL)[c].strip('\n').split('\n'); w = max(map(len, rows))
    return np.array([[ch == 'X' for ch in r.ljust(w, '.')] for r in rows])
def word(t, big, step, bounce):
    # returns (white pixels, everything the word covers): letters overlap by -step, later ones on top with a black keyline
    gs = [letter(c, big) for c in t]; b0 = max(abs(b) for b in bounce)
    H = max(g.shape[0] for g in gs) + 2 * b0 + 2; steps = step if isinstance(step, list) else [step] * (len(gs) - 1)
    W = sum(g.shape[1] for g in gs) + sum(steps) + 2
    img = np.zeros((H, W), bool); cover = np.zeros((H, W), bool); x = 1
    for i, g in enumerate(gs):
        y = 1 + b0 + bounce[i % len(bounce)]; f = np.zeros_like(img); f[y:y + g.shape[0], x:x + g.shape[1]] = g
        img &= ~nd.binary_dilation(f, np.ones((3, 3)))   # (the black keyline round this letter, over the ones before)
        img |= f; cover |= f; x += g.shape[1] + (steps[i] if i < len(steps) else 0)
    return img, cover
def sticker(img, cover, shadow=True):
    # wrap the word: a black gap, then a white outline all round, thicker at the bottom right like a drop shadow
    H, W = img.shape; P = 4; I = np.pad(img, P); C = np.pad(cover, P)
    gap = nd.binary_dilation(C, np.ones((3, 3)))
    ring = nd.binary_dilation(gap, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    if shadow: ring |= np.roll(np.roll(ring, 1, 0), 1, 1)
    out = (ring & ~gap) | I; mask = ring | gap
    ys, xs = np.where(mask); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return out[y0:y1, x0:x1], mask[y0:y1, x0:x1]
