# The talk screen: Loony Larry (drawn in loon.py) on the left and his speech bubble on the right (the game types his words
# into it). 4 frames: beak shut, a little open, wide open, and a grin. Writes gord.npy (and /tmp/gord/*.png previews).
import numpy as np
from PIL import Image, ImageDraw
K = 4; W, H = 128, 64
def frame(mouth):
    im = Image.new('L', (W * K, H * K), 0); d = ImageDraw.Draw(im)
    def P(*pts): return [(x * K, y * K) for x, y in pts]
    def E(x0, y0, x1, y1): return [x0 * K, y0 * K, x1 * K, y1 * K]
    # shoulders in a plaid shirt and overall straps
    d.polygon(P((0, 64), (2, 52), (10, 47), (34, 47), (42, 52), (44, 64)), 255)
    for x in range(4, 42, 4): d.line(P((x, 49), (x, 64)), 0, width=K // 2)
    for y in range(52, 64, 4): d.line(P((2, y), (43, y)), 0, width=K // 2)
    d.rectangle(E(11, 47, 15, 64), 255); d.rectangle(E(29, 47, 33, 64), 255)          # suspenders
    d.rectangle(E(12, 47, 14, 64), 0); d.rectangle(E(30, 47, 32, 64), 0)
    d.ellipse(E(12, 56, 14, 58), 255); d.ellipse(E(30, 56, 32, 58), 255)              # buttons
    # the head, a bit long, ears sticking out
    d.ellipse(E(8, 13, 36, 47), 255)
    d.ellipse(E(5, 26, 11, 34), 255); d.ellipse(E(33, 26, 39, 34), 255)
    d.arc(E(6, 27, 10, 33), 90, 270, 0, width=K // 2); d.arc(E(34, 27, 38, 33), 270, 90, 0, width=K // 2)
    # stubble: a few dots round the jaw
    for (x, y) in ((13, 38), (16, 41), (19, 43), (25, 43), (28, 41), (31, 38), (14, 41), (30, 41), (22, 44)): d.rectangle(E(x, y, x + 0.9, y + 0.9), 0)
    # bushy eyebrows, beady eyes, a big round nose
    d.line(P((13, 21), (20, 20)), 0, width=K + 3); d.line(P((24, 20), (31, 21)), 0, width=K + 3)
    d.ellipse(E(14.5, 23, 18.5, 27), 0); d.ellipse(E(25.5, 23, 29.5, 27), 0)            # eyes
    d.rectangle(E(15.5, 23.8, 16.5, 24.8), 255); d.rectangle(E(26.5, 23.8, 27.5, 24.8), 255)   # a glint in each
    d.ellipse(E(18, 25, 26, 33), 255); d.arc(E(18, 25, 26, 33), 20, 160, 0, width=K)  # nose
    d.ellipse(E(19.5, 30.5, 21, 32), 0); d.ellipse(E(23, 30.5, 24.5, 32), 0)          # nostrils
    # the mouth: no teeth at all, just gums
    if mouth == 0: d.arc(E(14, 31, 30, 41), 20, 160, 0, width=K + 2)                    # a toothless smile, lips tucked in
    elif mouth == 1: d.ellipse(E(17, 35, 27, 41), 0)
    elif mouth == 2: d.ellipse(E(16, 34, 28, 45), 0); d.ellipse(E(19, 41, 25, 44), 255)   # wide open, tongue showing, not a tooth in sight
    else: d.chord(E(12, 30, 32, 44), 0, 180, 0); d.ellipse(E(19, 39.5, 25, 43), 255)   # the big gummy grin (just a tongue, no teeth)
    # a fishing hat with a wide floppy brim and a lure hooked in it
    d.polygon(P((3, 16), (41, 16), (37, 19), (7, 19)), 255)
    d.polygon(P((11, 16), (13, 4), (31, 4), (33, 16)), 255)
    d.line(P((11, 13), (33, 13)), 0, width=K)                                            # hat band
    d.line(P((27, 6), (29, 10)), 0, width=K // 2); d.ellipse(E(28, 9, 31, 12), 0)       # the lure
    d.line(P((3, 16), (41, 16)), 0, width=K // 2)
    # the speech bubble, its tail pointing at his mouth
    d.rounded_rectangle(E(46, 1, 127, 62), radius=5 * K, outline=255, width=K)
    d.polygon(P((46, 34), (40, 38), (46, 41)), 255); d.polygon(P((47, 35), (43, 38), (47, 40)), 0)
    return np.asarray(im.resize((W, H), Image.BOX), np.float32) / 255 > 0.5
from loon import lou
def lframe(beak):                                   # Loony Lou (left) and the speech bubble (right)
    scr = frame(0).copy(); scr[:, :45] = False
    scr[:, :45] = lou(45, 64, beak, s=0.82, ox=-8, oy=4)
    return scr
frames = np.stack([lframe(b) for b in (0, 1, 2, 0)])
np.save('gord.npy', frames)
import os; os.makedirs('/tmp/gord', exist_ok=True)
for i, f in enumerate(frames): Image.fromarray((f * 255).astype(np.uint8)).resize((512, 256), Image.NEAREST).save('/tmp/gord/%d.png' % i)
print('ok')
