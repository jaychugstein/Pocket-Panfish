# Loony Lou, the common loon who runs the derby: black and white already, so he suits a 1-bit screen.
# lou(w, h, beak) draws him floating on the water, facing right, with his beak shut (0) or open (1, 2).
# Drawn as layers at 8x: white fills, the black head/neck/back, the white checks and necklace stripes, outlines.
import numpy as np
from PIL import Image, ImageDraw
K = 8
def lou(W, H, beak=0, s=1.0, ox=0, oy=0, hat=True):
    L = {n: Image.new('L', (W * K, H * K), 0) for n in ('white', 'black', 'check', 'stripe', 'top')}; D = {n: ImageDraw.Draw(L[n]) for n in L}
    def T(x, y): return ((ox + x * s) * K, (oy + y * s) * K)
    def P(*pts): return [T(x, y) for x, y in pts]
    def E(x0, y0, x1, y1): a, b = T(x0, y0), T(x1, y1); return [a[0], a[1], b[0], b[1]]
    w, b, c, st, tp = D['white'], D['black'], D['check'], D['stripe'], D['top']
    # body on the water: black back covered in white checks, a white breast at the front, sitting low in the water
    b.ellipse(E(2, 40, 52, 66), 255)
    c.chord(E(6, 42, 46, 62), 185, 330, 255)
    w.ellipse(E(34, 42, 52, 60), 255); b.chord(E(34, 42, 52, 60), 200, 320, 255)    # white breast
    b.polygon(P((0, 52), (10, 47), (7, 54)), 255)                               # tail tip
    # neck and head, black, with the white striped necklace
    b.polygon(P((30, 47), (32, 30), (42, 26), (46, 34), (45, 47)), 255)
    b.ellipse(E(29, 11, 51, 33), 255)                                          # head
    st.polygon(P((33, 36), (45, 34), (45, 38), (33, 40)), 255)                 # necklace band
    # the dagger beak
    if beak == 0: b.polygon(P((48, 20), (62, 25), (48, 26)), 255)
    else:
        o = 2 + beak * 1.5
        b.polygon(P((48, 19), (62, 22 - o / 2), (48, 23)), 255); b.polygon(P((48, 24), (61, 26 + o), (48, 27)), 255)
        w.polygon(P((48, 23), (61, 22.5 - o / 2 + 1.5), (61, 25 + o), (48, 24)), 0)
    # his eye: a ring with a dark middle
    tp.ellipse(E(41.5, 16.5, 46.5, 21.5), 255)
    # a little fishing hat, perched on top
    if hat:
        tp.polygon(P((29, 13), (51, 12), (49, 15), (31, 16)), 255)
        tp.polygon(P((33, 13), (35, 4), (45, 4), (47, 12)), 255)
    def g(n): return np.asarray(L[n].resize((W, H), Image.BOX), np.float32) / 255 > 0.5
    white, black, check, stripe, top = g('white'), g('black'), g('check'), g('stripe'), g('top')
    yy, xx = np.mgrid[0:H, 0:W]
    out = white & ~black                                        # white where there's white and no black over it
    out |= check & black & ((xx % 3 == 0) & (yy % 2 == 0))      # white checks on the black back
    out |= stripe & black & (xx % 2 == 0)                       # the striped necklace
    out |= top                                                  # eye ring and hat drawn on top
    sil = white | black | top                                   # a white outline all round him, so the black reads against the night
    p = np.pad(sil, 1); grow = sil.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): grow |= p[dy:dy + H, dx:dx + W]
    out |= grow & ~sil
    wl = int(T(0, 55)[1] / K)                                   # the waterline: he sits in the lake
    if 0 < wl < H:
        out[wl:] = False
        for x in range(W):
            if (x // 3) % 3 != 2: out[wl, x] = True
        for y in range(wl + 3, min(H, wl + 9), 3):
            for x in range(W):
                if sil[min(y, H - 1) - 2 * (y - wl) if 0 <= wl - (y - wl) < H else 0, x] and (x + y) % 4 == 0: out[y, x] = True   # a broken reflection
    # the eye's dark middle, and a band on the hat
    ex, ey = T(44, 19); ex, ey = int(ex / K), int(ey / K); out[ey - 1:ey + 1, ex - 1:ex + 1] = False
    if hat:
        hy = int(T(0, 11.5)[1] / K); hx0, hx1 = int(T(34, 0)[0] / K), int(T(46.5, 0)[0] / K); out[hy, hx0:hx1] = False
    return out
if __name__ == '__main__':
    a = lou(64, 64, 0, s=1.0, ox=0, oy=-2)
    Image.fromarray(a.astype(np.uint8) * 255).resize((512, 512), Image.NEAREST).save('/tmp/lou.png'); print('ok')
