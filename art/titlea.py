# Title screen picture (option A): the POCKET PANFISH logo, and a big pumpkinseed leaping out of the water on a line,
# with a splash. The words BEST / PLAY / SOUND are added by the game, bottom left. Drawn at 8x and reduced.
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont
K = 8
def red(im, t=0.5): return np.asarray(im.resize((im.width // K, im.height // K), Image.BOX), np.float32) / 255 > t
def edge(m):
    p = np.pad(m, 1); H, W = m.shape; o = m.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): o |= p[dy:dy + H, dx:dx + W]
    return o
def fish(angle):                                   # a big pumpkinseed, facing right, rotated to leap
    S = 48 * K; body = Image.new('L', (S, S), 0); ink = Image.new('L', (S, S), 0); b = ImageDraw.Draw(body); k = ImageDraw.Draw(ink)
    def P(*pts): return [(x * K, y * K) for x, y in pts]
    def E(cx, cy, rx, ry): return [(cx - rx) * K, (cy - ry) * K, (cx + rx) * K, (cy + ry) * K]
    b.ellipse(E(26, 24, 13, 9), 255)                                        # an oval body, plain white
    b.polygon(P((16, 21), (12, 22.5), (4, 15), (7.5, 24), (4, 33), (12, 25.5), (16, 27)), 255)   # a narrow tail stalk and a forked tail
    b.polygon(P((17, 18), (18, 11), (21, 13), (23, 9), (26, 12), (28, 10), (31, 13), (33, 16)), 255)   # the back fin: spiny points, standing up
    b.polygon(P((19, 31), (22, 38), (26, 32)), 255)                          # belly fin, pointing back
    k.line(P((31, 18.5), (35, 22.5)), 255, width=K + 3); k.line(P((31, 22.5), (35, 18.5)), 255, width=K + 3)   # X for an eye
    k.line(P((39, 25), (36, 26)), 255, width=K + 1)                          # mouth
    k.arc(E(20, 24, 4, 8), 300, 60, 255, width=K + 2)                       # the gill line
    body = body.rotate(angle, Image.BICUBIC, center=(24 * K, 24 * K)); ink = ink.rotate(angle, Image.BICUBIC, center=(24 * K, 24 * K))
    return red(body, 0.45), red(ink, 0.35)
scr = np.zeros((64, 128), bool)
def put(w, m, x, y):
    h, ww = w.shape; ys, xs = slice(y, y + h), slice(x, x + ww)
    scr[ys, xs] = (scr[ys, xs] & ~m) | w
# water, splash rings and drops
im = Image.new('L', (128 * K, 64 * K), 0); d = ImageDraw.Draw(im)
WY = 50
for x in range(66, 128): d.rectangle([x * K, (WY + [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0][x & 15]) * K, x * K + K - 1, (WY + 1 + [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0][x & 15]) * K - 1], 255)
for x, h in ((86, 3), (89, 5), (92, 6), (98, 6), (101, 5), (104, 3)): d.line([(x * K, WY * K), ((x + (x - 95) * 0.3) * K, (WY - h) * K)], 255, width=K)   # a crown of splash
for x, y in ((80, 44), (85, 39), (108, 41), (113, 46), (76, 49), (117, 50), (90, 46)): d.ellipse([(x - 0.8) * K, (y - 1.2) * K, (x + 0.8) * K, (y + 1.2) * K], 255)
scr |= red(im)
fw, fi = fish(40)
put(fw & ~fi, edge(fw), 74, 2)
# the line, from a rod up off the screen to its mouth (the mouth is at (38, 24) on the unrotated fish)
a = math.radians(40); mx = 24 + (38 - 24) * math.cos(a) + (24 - 24) * math.sin(a); my = 24 - (38 - 24) * math.sin(a) + (24 - 24) * math.cos(a)
ln = Image.new('L', (128 * K, 64 * K), 0); ImageDraw.Draw(ln).line([(124 * K, 0), ((74 + mx) * K, (2 + my) * K)], 255, width=K)
scr |= red(ln) & ~edge(fw | np.zeros_like(fw)) if False else red(ln)
# the logo, top left, with a dotted drop shadow
def text_mask(txt, size, font='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'):
    f = ImageFont.truetype(font, size * K); box = f.getbbox(txt); tw, th = box[2] - box[0], box[3] - box[1]
    t = Image.new('L', (tw + 2 * K, th + 2 * K), 0); ImageDraw.Draw(t).text((K - box[0], K - box[1]), txt, 255, font=f, stroke_width=K // 4, stroke_fill=255)
    return red(t)
for txt, size, x, y in (('POCKET', 10, 3, 1), ('PANFISH', 15, 1, 11)):
    m = text_mask(txt, size); h, w = m.shape
    sh = np.zeros_like(scr); sh[y + 2:y + 2 + h, x + 2:x + 2 + w] = m
    mm = np.zeros_like(scr); mm[y:y + h, x:x + w] = m
    yy, xx = np.mgrid[0:64, 0:128]
    scr &= ~edge(mm); scr |= (sh & ((xx + yy) % 2 == 0) & ~edge(mm)) | mm
np.save('titlea.npy', scr)
Image.fromarray(scr.astype(np.uint8) * 255).resize((512, 256), Image.NEAREST).save('/tmp/titlea.png'); print('ok')
