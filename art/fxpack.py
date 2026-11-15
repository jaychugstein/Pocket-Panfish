# Packs Pocket Panfish's art and font for the FX flash chip (Arduboy FX / FX-C). Run art.py first.
# Writes ../PocketPanfish/fxdata.h and ../PocketPanfish/fxdata/: fxdata-data.bin (the data), fxdata-save.bin (the empty 4K save
# block) and fxdata.bin (both together, as they sit at the end of the FX chip during development / in the emulator).
import os, re, pickle, numpy as np
ART = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ART, '..', 'PocketPanfish')
def sprite(frames, masked=True):          # frames of (white[, solid]) -> FX bitmap (dbmMasked: image byte then mask byte)
    H, W = frames[0][0].shape; out = bytearray([W >> 8, W & 255, H >> 8, H & 255])
    for f in frames:
        white = f[0]; sol = f[1] if masked else None
        for p in range((H + 7) // 8):
            for x in range(W):
                rows = [p * 8 + k for k in range(8)]
                out.append(sum(int(r < H and white[r, x]) << k for k, r in enumerate(rows)))
                if masked: out.append(sum(int(r < H and (sol[r, x] or white[r, x])) << k for k, r in enumerate(rows)))
    return bytes(out)
a = pickle.load(open(os.path.join(ART, 'art.pkl'), 'rb'))
spr = bytearray(); offs = []; ws = []; hs = []
for k in a['order']:
    offs.append(len(spr)); f = a['spr'][k]; ws.append(f[0][0].shape[1]); hs.append(f[0][0].shape[0]); spr += sprite(f)
TALK = [["HOWDY! I'M", "LOONY LARRY.", "I LIFT", "LUNKERS FOR", "A LIVIN'!"],
        ["CATCH ONE OF", "EACH SPECIES", "TO WIN! THE", "CORNER SHOWS", "WHAT'S LEFT."],
        ["", "OOOO-WEE!", "WE WON THE", "DERBY!", ""],
        ["", "AW SHUCKS.", "ALL OUTTA", "LINE. TRY", "AGAIN!"]]
NAMES = ['', 'PUMPKINSEED', 'PERCH', 'LARGEMOUTH BASS', 'WALLEYE', 'LAKE TROUT', 'CATFISH', 'NORTHERN PIKE', 'LONGNOSE GAR', 'CRAWFISH', 'OLD BOOT', 'TREASURE CHEST']
MSGS = [('OUT', 'OUT OF LINE!'), ('BOOT', 'OLD BOOT!'), ('ALREADY', 'ALREADY GOT!'),
        ('PIKEGOT', 'PIKE GOT IT!'), ('BASSGOT', 'BASS GOT IT!'), ('GARGOT', 'GAR STOLE IT!'), ('SNAG', 'SNAGGED!'), ('GARCUT', 'GAR BIT THROUGH!'), ('TURTLE', 'SNAPPING TURTLE!'),
        ('LINE', '+1 LINE'), ('HOLD', 'HOLD B TO DROP LINE'), ('WON', 'DERBY WON!'), ('SCORE', 'SCORE'), ('NEWBEST', 'NEW BEST!'), ('BEST', 'BEST '),
        ('LB', 'LB'), ('TITLE', ' TITLE'), ('AGAIN', 'AGAIN '), ('RECORD', 'RECORD!')]
TS = 20
TG = {'0': ['XXX', 'X.X', 'X.X', 'X.X', 'XXX'], '1': ['.X.', 'XX.', '.X.', '.X.', 'XXX'], '2': ['XXX', '..X', 'XXX', 'X..', 'XXX'],
      '3': ['XXX', '..X', '.XX', '..X', 'XXX'], '4': ['X.X', 'X.X', 'XXX', '..X', '..X'], '5': ['XXX', 'X..', 'XXX', '..X', 'XXX'],
      '6': ['XXX', 'X..', 'XXX', 'X.X', 'XXX'], '7': ['XXX', '..X', '.X.', '.X.', '.X.'], '8': ['XXX', 'X.X', 'XXX', 'X.X', 'XXX'],
      '9': ['XXX', 'X.X', 'XXX', '..X', 'XXX'], 'X': ['...', 'X.X', '.X.', 'X.X', '...']}
def _bar():
    fnt = [int(v) for v in re.search(r'\{([^}]*)\}', open(os.path.join(ART, 'font.h')).read()).group(1).split(',')]
    b = np.zeros((8, 128), bool)
    def txt(s, x):
        for c in s:
            for i in range(5):
                col = fnt[(ord(c) - 32) * 5 + i]
                for j in range(7):
                    if col >> j & 1: b[1 + j, x + i] = True
            x += 6
        return x
    def key(x, left):                                       # a d-pad key with an arrow (white, rounded, arrow cut out)
        b[1:8, x:x + 7] = True; b[1, x] = b[1, x + 6] = b[7, x] = b[7, x + 6] = False
        for i in range(3):
            cx = x + 2 + i if left else x + 4 - i
            b[1 + 3 - i:1 + 3 - i + 1 + 2 * i, cx] = False
    key(4, True); txt(' TITLE', 12); x = txt('AGAIN ', 74); key(x, False)
    return b
BAR = _bar()
TINY = [sum(1 << r for r in range(5) if TG[c][r][i] == 'X') for c in '0123456789X' for i in range(3)]
def ttext():                                               # every bit of text the game shows, 20 bytes a slot: the fish names (by kind), then the messages
    out = bytearray()
    for t in NAMES + [m for _, m in MSGS]: assert len(t) < TS, t; out += t.encode().ljust(TS, b'\0')
    return bytes(out)
def gtext():
    out = bytearray()
    for page in TALK:
        for line in page: out += line.center(12).encode()
    return bytes(out)
parts = [('FX_SPR', bytes(spr), 'the sprites (boat = Larry): ' + ', '.join(a['order']) + ' (4 frames each: right, right, left, left)'),
         ('FX_WRECK', sprite([a['wreck']]), 'the shipwreck (its deck is a roof the hook cannot get through)'),
         ('FX_BED', sprite([a['bed']]), 'the lake bottom, a 64x7 tile'),
         ('FX_LARRY', sprite([(g,) for g in np.load(os.path.join(ART, 'gord.npy'))], False), 'Loony Larry and his speech bubble, 4 frames (beak shut, open, wide, grin)'),
         ('FX_TALK', gtext(), 'what Larry says: 4 pages of 5 lines, 12 letters each (intro x2, won, lost)'),
         ('FX_TBG', sprite([(t,) for t in np.load(os.path.join(ART, 'titlebg.npy'))], False), 'the title screen underwater: surface, swaying weed and sand, 8 frames'),
         ('FX_TLOGO', sprite([tuple(np.load(os.path.join(ART, 'titlelogo.npy')))]), 'the POCKET PANFISH lettering (masked)'),
         ('FX_TBUB', sprite([(b, np.zeros_like(b)) for b in np.load(os.path.join(ART, 'titlebub.npy'))]), 'a rising bubble, 3 sizes (masked: see-through around it)'),
         ('FX_THOOK', sprite([tuple(np.load(os.path.join(ART, 'titlehook.npy')))]), 'the hook dangling beside the words (masked)'),
         ('FX_SOUND', sprite([(t,) for t in np.load(os.path.join(ART, 'soundscr.npy'))], False), 'the sound screen, 2 frames: ON, OFF'),
         ('FX_TEXT', ttext(), 'the words: fish names by kind, then the messages (20 bytes each, see the T_ numbers)'),
         ('FX_BAR', sprite([(BAR,)], False), 'the score screen\'s bottom line: [< TITLE] and [AGAIN >] (rows 56-63)'),
         ('FX_TINY', bytes(TINY), 'small 3x5 digits 0-9 then X, 3 bytes each (columns, bit 0 at the top), for the score'),
         ('FX_FONT', bytes(int(v) for v in re.search(r'\{([^}]*)\}', open(os.path.join(ART, 'font.h')).read()).group(1).split(',')), 'the 5x7 font (5 bytes a letter, from space)')]
data = bytearray(); hdr = []
for name, blob, note in parts:
    hdr.append('constexpr uint24_t %-9s = 0x%06X;   // %s' % (name, len(data), note)); data += blob
while len(data) % 4096: data.append(0xFF)
dpage = 0x10000 - (len(data) + 4096) // 256; spage = 0x10000 - 16
os.makedirs(os.path.join(OUT, 'fxdata'), exist_ok=True)
open(os.path.join(OUT, 'fxdata', 'fxdata-data.bin'), 'wb').write(data)
open(os.path.join(OUT, 'fxdata', 'fxdata-save.bin'), 'wb').write(b'\xff' * 4096)
open(os.path.join(OUT, 'fxdata', 'fxdata.bin'), 'wb').write(data + b'\xff' * 4096)
h = '// generated by art/fxpack.py - do not edit\n#pragma once\n#include <ArduboyFX.h>\n'
h += 'constexpr uint16_t FX_DATA_PAGE = 0x%04X;   // %d bytes of FX data\nconstexpr uint16_t FX_SAVE_PAGE = 0x%04X;   // a 4K block for the best score, private to this game\n' % (dpage, len(data), spage) + '\n'.join(hdr) + '\n'
h += 'const uint16_t SPROFS[] PROGMEM = {%s};\nconst uint8_t SPRW[] PROGMEM = {%s};\nconst uint8_t SPRH[] PROGMEM = {%s};\nconstexpr uint8_t WRECK_W = %d, WRECK_H = %d;\n' % (','.join(map(str, offs)), ','.join(map(str, ws)), ','.join(map(str, hs)), a['wreck'][0].shape[1], a['wreck'][0].shape[0])
_lg = np.load(os.path.join(ART, 'titlelogo.npy'))
h += 'constexpr uint8_t TLOGO_W = %d, TLOGO_H = %d;\n' % (_lg.shape[2], _lg.shape[1])
h += 'enum { ' + ', '.join('T_%s = %d' % (n, len(NAMES) + i) for i, (n, _) in enumerate(MSGS)) + ' };   // the messages in FX_TEXT (a fish kind is its own name)\nconstexpr uint8_t TEXT_SLOT = %d;\n' % TS
open(os.path.join(OUT, 'fxdata.h'), 'w').write(h); print(h)
import math
v = [round(127 * math.sin(2 * math.pi * i / 256)) for i in range(256)]
open(os.path.join(OUT, 'sintab.h'), 'w').write('// generated by art/fxpack.py: sine, 256 steps a turn, -127..127\n#pragma once\nconst int8_t SIN8[256] PROGMEM = {' + ','.join(map(str, v)) + '};\n')
