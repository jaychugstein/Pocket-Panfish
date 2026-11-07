# Pocket Panfish art: hand-drawn pixel sprites (facing right; the left-facing frames are mirrored here), the shipwreck and the
# logo. W = white, k = black inside the shape, . = see-through. Every sprite gets a 1px black edge in its mask so it reads
# over the fishing line. Writes art.pkl for fxpack.py and a preview to /tmp/pf_sheet.png.
import numpy as np, pickle
from PIL import Image, ImageDraw, ImageFont
def grid(rows):
    w = max(len(r) for r in rows); rows = [r.ljust(w, '.') for r in rows]
    white = np.array([[c == 'W' for c in r] for r in rows]); solid = np.array([[c in 'Wk' for c in r] for r in rows])
    return white, solid
def edge(m):
    p = np.pad(m, 1); H, W = m.shape; o = m.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): o |= p[dy:dy + H, dx:dx + W]
    return o
def pad1(white, solid):                       # one see-through pixel all round so the black edge fits
    return np.pad(white, 1), edge(np.pad(solid, 1))
def flip(f): return f[0][:, ::-1], f[1][:, ::-1]

S = {}
S['boat'] = [[   # Loony Larry himself, floating on the lake in his fishing hat, the rod in his beak (the game draws the rod);
"..............WWWW..........",   # frame 2: he leans back, reeling
"............WWWWWWWW........",
".............WkkkkW.........",
"............WkkkWkkW........",
"............WkkkkkkWWW......",
"............WkkkkkkkkkWW....",
"............WWkkkkkWWW......",
".............WkWkWkW........",
".....WWWWWWWWWkkkkkW........",
"...WWkkWkkWkkWkkkkkkW.......",
".WWkWkkkWkkkWkkkkkkkkW......",
"WkkkkkWkkkWkkkWkkkkkkW......",
".WWkkkkkkkkkkkkkkkkkW.......",
"...WWWWWWWWWWWWWWWWW........"],[
".............WWWW...........",
"...........WWWWWWWW.........",
"............WkkkkW..........",
"...........WkkkWkkW.........",
"...........WkkkkkkWWW.......",
"...........WkkkkkkkkkWW.....",
"...........WWkkkkkWWW.......",
"............WkWkWkW.........",
".....WWWWWWWWkkkkkkW........",
"...WWkkWkkWkkWkkkkkkW.......",
".WWkWkkkWkkkWkkkkkkkkW......",
"WkkkkkWkkkWkkkWkkkkkkW......",
".WWkkkkkkkkkkkkkkkkkW.......",
"...WWWWWWWWWWWWWWWWW........"]]
def wag(rows):                       # the second swim frame: the tail (first 3 columns) flicks down a pixel
    w = max(len(r) for r in rows); rows = [r.ljust(w, '.') for r in rows]
    tail = [r[:3] for r in rows]; tail = ['...'] + tail[:-1]
    return [t + r[3:] for t, r in zip(tail, rows)]
def fishy(rows): return [rows, wag(rows)]
S['sunfish'] = fishy([          # pumpkinseed: a deep round body, a spiny back fin, a gill line, a little eye and mouth
"......W.W.W...",
"....WWWWWWWW..",
"W..WWWWWWWWWW.",
"WW.WWWkWWWWkWW",
"WWWWWWkWWWWWWW",
"WWWWWWkWWWWWkk",
"WW.WWWkWWWWWW.",
"W..WWWWWWWWWW.",
"....WWWWWWWW..",
".....W...W...."])
S['perch'] = fishy([            # perch: a tall spiky front fin on its back, dark bars down its sides, forked tail
".........W.W.W....",
"......W..W.W.W....",
".....W.W.WWWWW....",
"W...WWWWWWWWWWWW..",
"WW.WkWWkWWkWWkWWW.",
".WWWkWWkWWkWWkWWkW",
".WWWkWWkWWkWWWWWWW",
"WW.WWWWWWWWWWWWWW.",
"W...WWWWWWWWWWW...",
"......W..W..W....."])
S['bass'] = fishy([             # largemouth bass: a dark stripe along its side, a big jaw reaching back past the eye
".......W.W.W.W.WW...",
"W....WWWWWWWWWWWWW..",
"WW..WWWWWWWWWWkWWWW.",
"WWWWWWWWWWWWWWkWWkWW",
".WWWkkkkkkkkkkkWWWWW",
"WWWWWWWWWWWWWWkWkkkk",
"WW..WWWWWWWWWWWWWWWW",
"W....WWWWWWWWWWWWW..",
"........W.....W....."])
S['walleye'] = fishy([          # walleye: long, a spiny front back fin and a soft rear one, a gill line, small eye, a big jaw
"......W.W.W...WWW....",
"W....WWWWWWWWWWWWWW..",
"WW..WWWWWWWWWWWkWWWW.",
".WWWWWWWWWWWWWWkWWkWW",
".WWWWWWWWWWWWWWkWWWkk",
"WW..WWWWWWWWWWWWWWWW.",
"W.....WWWWWWWWWWWW...",
"........W....W.W....."])
S['trout'] = fishy([            # lake trout: sleek, a deeply forked tail, a few pale-trout specks
"..........W..........",
"W.....WWWWWWWWWWW....",
"WW..WWWWWWkWWWWkWWW..",
".WWWWWkWWWWWWWWkWWkW.",
"..WWWWWWWWWWkWWkWWWWW",
".WWWWWWkWWWWWWWWWWkk.",
"WW..WWWWWWWWWWWWWWW..",
"W.....WWWWWWWWWWW....",
".......W.......W....."])
S['catfish'] = fishy([          # catfish: long and flat-headed, a little fin on its back, whiskers hanging from its chin
"........WW............",
"W.....WWWWWWWWW.......",
"WW..WWWWWWWWWWWWWWW...",
".WWWWWWWWWWWWWWkWWkWWW",
".WWWWWWWWWWWWWWkWWWWWW",
"WW..WWWWWWWWWWWWWWWWW.",
"W.....W.W.......W..W.W",
"................W..W.."])
S['pike'] = fishy([             # northern pike: long, a back fin set right by the tail, a long duck-bill snout
"....W.....................",
"W..WWWW.WWWWWWWWWWWW......",
"WWWWWWWWWWWWWWWWWkWWWW....",
"WWWWWWWWWWWWWWWWWkWWkWWWWW",
"WWWWWWWWWWWWWWWWWkWWWkkkkW",
"W..WWWW.WWWWWWWWWWWWW.....",
"....W......W.............."])
S['gar'] = fishy([              # longnose gar: long and thin, a long needle beak full of teeth
"...W..................W.......",
"W..WWWWWWWWWWWWWWWWWWWW.......",
"WWWWWWWWWWWWWWWWWWkWWkWWWWWWWW",
"W..WWWWWWWWWWWWWWWWWWWWkWkWkWk",
"...W...............W.........."])
S['craw'] = fishy([             # a crawfish: fan tail, segmented body, big claws out front
"..........WW",
"W.WWWWWWWW..",
"WWWkWkWWWWWW",
"W.WWWWWWWW..",
"..W.W.W..WW."])
S['boot'] = [[
".WWWWW..",
".WkkkW..",
".WWWWW..",
".WkWkW..",
".WWWWWW.",
".WWWWWWW",
"WWWWWWWW",
"WkkkkkkW"]] * 2
S['chest'] = [[    # a heavy old treasure chest
"..WWWWWWWWW..",
".WkkkkkkkkkW.",
"WWWWWWWWWWWWW",
"WkkkkkWkkkkkW",
"WkWkkWWWkkWkW",
"WkkkkkWkkkkkW",
"WkWkkkkkkkWkW",
"WWWWWWWWWWWWW"]] * 2
S['turtle'] = [[                # a snapping turtle: ridged shell, hooked beak, spiky tail
".....WWWWWWWW.......",
"...WWkWWkWWkWWW.....",
"..WWWWWWWWWWWWWW.WW.",
".WWkWWkWWkWWkWWWWWkW",
"WWWWWWWWWWWWWWWWWWWW",
"..WW.........WW...WW",
"..W...........W....."],[
".....WWWWWWWW.......",
"...WWkWWkWWkWWW.....",
"..WWWWWWWWWWWWWW.WW.",
".WWkWWkWWkWWkWWWWWkW",
"WWWWWWWWWWWWWWWWWWWW",
"...WW.......WW....WW",
"....W........W......"]]
S['spool'] = [[    # a spool of fishing line: catch it for one more line
"WWWWWWW",
".WkWkW.",
".WWWWW.",
".WkWkW.",
".WWWWW.",
"WWWWWWW"]] * 2
ORDER = ['boat', 'sunfish', 'perch', 'bass', 'walleye', 'trout', 'catfish', 'pike', 'gar', 'craw', 'boot', 'chest', 'turtle', 'spool']
SPR = {}
for k in ORDER:
    fr = [pad1(*grid(r)) for r in S[k]]
    H = max(f[0].shape[0] for f in fr); W = max(f[0].shape[1] for f in fr)
    fr = [(np.pad(a, ((0, H - a.shape[0]), (0, W - a.shape[1]))), np.pad(b, ((0, H - b.shape[0]), (0, W - b.shape[1])))) for a, b in fr]
    SPR[k] = fr + [flip(f) for f in fr]                   # frames: right 0, right 1, left 0, left 1

# the shipwreck: a sunken boat lying on the bottom, its deck is a roof the hook can't get through
def wreck():
    W, H = 52, 22
    def img(): im = Image.new('1', (W, H), 0); return im, ImageDraw.Draw(im)
    base, d = img(); inner, kd = img(); det, dd = img()
    d.polygon([(1, 9), (50, 6), (46, 21), (5, 21)], 1); kd.polygon([(4, 11), (47, 8), (44, 19), (7, 19)], 1)
    for x in range(10, 46, 7): dd.line([(x, 10), (x - 1, 19)], 1)                     # planks
    for x in (16, 30): dd.ellipse([x - 2, 12, x + 2, 16], 0, 1)                        # portholes
    dd.line([(22, 9), (18, 0)], 1); dd.line([(23, 9), (19, 0)], 1); dd.line([(15, 3), (24, 1)], 1)   # the broken mast
    dd.line([(37, 7), (41, 1)], 1)
    b, k, t = np.array(base), np.array(inner), np.array(det)
    return pad1((b & ~k) | t, b | t)
WRECK = wreck()

# the lake bottom: a 64-wide tile repeated along the lake. A sandy edge, a dithered bed under it, and scattered pebbles.
def bedtile():
    import random as R; R.seed(7)
    W, H = 64, 7; w = np.zeros((H, W), bool)                  # rows 0..6 are screen y 57..63 (the bottom line is row 4, y 61)
    for x in range(W):
        if R.random() < 0.85: w[4, x] = True                   # the edge of the bed, with a few gaps
        if (x + 1) % 2 == 0: w[5, x] = True                    # dithered sand underneath
        if x % 2 == 0 and R.random() < 0.7: w[6, x] = True
        if R.random() < 0.08: w[3, x] = True                   # grains sitting on top
    for x0 in (3, 14, 22, 37, 45, 56):                         # pebbles and stones of a few sizes
        r = R.choice([1, 1, 2, 3])
        for y in range(4 - r, 5):
            for x in range(x0 - r, x0 + r + 1):
                if 0 <= x < W and ((x - x0) ** 2) / (r + 0.5) ** 2 + ((y - 4) ** 2) / (r * 0.8 + 0.4) ** 2 <= 1: w[y, x] = True
        if r >= 2: w[4 - r + 1, x0 - 1] = False                # a little shading dot on the bigger ones
    return w, w.copy()
BED = bedtile()

def text_mask(txt, size, font='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc', K=8):
    f = ImageFont.truetype(font, size * K); box = f.getbbox(txt); tw, th = box[2] - box[0], box[3] - box[1]
    im = Image.new('L', (tw + 2 * K, th + 2 * K), 0); ImageDraw.Draw(im).text((K - box[0], K - box[1]), txt, 255, font=f, stroke_width=K // 4, stroke_fill=255)
    return np.asarray(im.resize((max(1, im.width // K), max(1, im.height // K)), Image.BOX), np.float32) / 255 > 0.5
def logo():                                              # POCKET / PANFISH with a dotted drop shadow, 128x34, see-through
    scr = np.zeros((34, 128), bool); sol = np.zeros((34, 128), bool)
    for a, y in ((text_mask('POCKET', 11), 0), (text_mask('PANFISH', 17), 10)):
        x = (128 - a.shape[1]) // 2; m = np.zeros((34, 128), bool); h = min(a.shape[0], 34 - y); m[y:y + h, x:x + a.shape[1]] = a[:h]
        sh = np.zeros_like(m); sh[2:, 2:] = m[:-2, :-2]; yy, xx = np.mgrid[0:34, 0:128]
        e = edge(m); scr &= ~e; sol |= e | sh
        scr |= (sh & ((xx + yy) % 2 == 0) & ~e) | m
    return scr, sol
LOGO = logo()

TITLE = np.load('titlea.npy')                                 # the title screen picture (titlea.py)
pickle.dump({'spr': SPR, 'order': ORDER, 'wreck': WRECK, 'logo': LOGO, 'bed': BED, 'title': TITLE}, open('art.pkl', 'wb'))
# preview
rows = [SPR[k] for k in ORDER] + [[WRECK], [LOGO]]
Wd = max(sum(f[0].shape[1] + 2 for f in r) for r in rows); Hd = sum(max(f[0].shape[0] for f in r) + 2 for r in rows)
sheet = np.full((Hd, Wd), 40, np.uint8); y = 0
for r in rows:
    x = 0
    for wh, m in r: sheet[y:y + wh.shape[0], x:x + wh.shape[1]] = np.where(wh, 255, np.where(m, 0, 90)); x += wh.shape[1] + 2
    y += max(f[0].shape[0] for f in r) + 2
Image.fromarray(sheet).resize((Wd * 4, Hd * 4), Image.NEAREST).save('/tmp/pf_sheet.png'); print('ok')
