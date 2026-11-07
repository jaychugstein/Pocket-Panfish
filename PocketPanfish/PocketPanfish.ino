// POCKET PANFISH - a freshwater fishing game for Arduboy FX / FX-C, set on Lake Huron at night.
// Loony Larry fishes a lake four screens wide, setting off from a dock at the far left. Left/Right moves him. Hold A or B (they
// do the same thing) to let the line down; let go to reel in, press again to bob it. A fish bites only if the lure touches its
// head. The derby: land one of each of the 7 kinds (the top corner shows the ones still needed). A kind you already have costs
// you a line. Snags and snapping turtles cut your line, gar, pike and bass steal your catch; lose all your line and it's over.
// Old boots cost points; spools of line give one back.
// The pictures and the font live on the FX flash chip; the best score is saved there too.
#include <Arduboy2.h>
#include <ArduboyTones.h>
#include "fxdata.h"
Arduboy2Base ab;
ARDUBOY_NO_USB                             // saves ~3 KB, like most cart games (press reset to upload something else)
ArduboyTones snd(ab.audio.enabled);
#define AB_JUST (ab.justPressed(A_BUTTON) || ab.justPressed(B_BUTTON))   // A and B do exactly the same thing
#define AB_HELD (ab.pressed(A_BUTTON) || ab.pressed(B_BUTTON))

// ---------------------------------------------------------------- text (5x7 font from the FX chip)
int16_t tx_, ty_; uint8_t tc_ = WHITE;
void at(int16_t x, int16_t y) { tx_ = x; ty_ = y; }
void pc(char c) {
  if (c == '[' || c == ']') {                                  // a d-pad key with an arrow
    uint8_t k = tc_, bg = tc_ == WHITE ? BLACK : WHITE; ab.fillRect(tx_, ty_, 7, 7, k); ab.drawPixel(tx_, ty_, bg); ab.drawPixel(tx_ + 6, ty_, bg); ab.drawPixel(tx_, ty_ + 6, bg); ab.drawPixel(tx_ + 6, ty_ + 6, bg);
    for (uint8_t i = 0; i < 3; i++) ab.drawFastVLine(c == '[' ? tx_ + 2 + i : tx_ + 4 - i, ty_ + 3 - i, 1 + 2 * i, bg);
    tx_ += 8; return;
  }
  uint8_t g = (c >= 32 && c <= 90) ? c - 32 : 0, gl[5]; FX::readDataBytes(FX_FONT + g * 5, gl, 5);
  for (uint8_t i = 0; i < 6; i++, tx_++) { uint8_t b = i < 5 ? gl[i] : 0; for (uint8_t j = 0; j < 7; j++) if (b >> j & 1) ab.drawPixel(tx_, ty_ + j, tc_); }
}
uint8_t nlen(uint32_t v) { uint8_t n = 1; while (v >= 10) { v /= 10; n++; } return n; }
void pn(uint32_t v) { char b[10]; uint8_t n = 0; do { b[n++] = '0' + v % 10; v /= 10; } while (v); while (n) pc(b[--n]); }
uint8_t pt(uint8_t id, bool draw = true) {                    // print one of the game's words from the FX chip (or just measure it); returns its length
  char b[TEXT_SLOT]; FX::readDataBytes(FX_TEXT + id * TEXT_SLOT, (uint8_t*)b, TEXT_SLOT);
  uint8_t n = 0; while (n < TEXT_SLOT && b[n]) { if (draw) pc(b[n]); n++; } return n;
}
void bigNum(int16_t cx, int16_t y, uint32_t v, uint8_t k) {   // a big centred number
  char b[10]; uint8_t n = 0; do { b[n++] = '0' + v % 10; v /= 10; } while (v);
  int16_t x = cx - (n * 6 * k - k) / 2;
  while (n) { uint8_t g = b[--n] - 32, gl[5]; FX::readDataBytes(FX_FONT + g * 5, gl, 5);
    for (uint8_t i = 0; i < 5; i++) for (uint8_t j = 0; j < 7; j++) if (gl[i] >> j & 1) ab.fillRect(x + i * k, y + j * k, k, k, WHITE);
    x += 6 * k; }
}
uint16_t msgLb;                                                // the weight of the fish you just landed, tenths of a pound
void pw(uint16_t lb) { pn(lb / 10); pc('.'); pc('0' + lb % 10); pt(T_LB); }   // a weight: 2.4LB
void boxText(int16_t cx, int16_t y, uint8_t s) {               // centred words in a black box with a white frame; T_LB: the weight
  int16_t w = (s == T_LB ? nlen(msgLb / 10) + 4 : pt(s, false)) * 6 - 1; ab.fillRect(cx - w / 2 - 3, y - 3, w + 6, 13, BLACK); ab.drawRect(cx - w / 2 - 3, y - 3, w + 6, 13, WHITE);
  at(cx - w / 2, y); if (s == T_LB) pw(msgLb); else pt(s);
}

// ---------------------------------------------------------------- the lake (Lake Huron at night)
const int16_t WORLD = 512, SURF = 13, BED = 61, DOCK_END = 28;   // four screens wide; the water line; the lake bottom; the dock's end
const int16_t WRECK_X = 236, WRECK_Y = BED - WRECK_H + 4;     // a sunken boat lies near the middle
const int16_t ROOF_Y = WRECK_Y + 8, ROOF_X0 = WRECK_X + 3, ROOF_X1 = WRECK_X + 49;   // its deck: the hook stops there
enum { K_BOAT, K_SUN, K_PERCH, K_BASS, K_WALL, K_TROUT, K_CAT, K_PIKE, K_GAR, K_CRAW, K_BOOT, K_CHEST, K_TURTLE, K_SPOOL, NKIND = K_TURTLE };   // K_BOAT is Larry
//                                 sun perch bass walleye trout cat pike gar craw boot chest
const uint16_t POINTS[] PROGMEM = { 0, 100, 150, 250, 400, 600, 300, 500, 350, 50, 0, 2000 };
const uint8_t WEIGHT[] PROGMEM = { 0, 1, 1, 2, 3, 3, 3, 3, 4, 1, 1, 5 };       // heavier catches reel in slower
const uint8_t SWIM[] PROGMEM = { 0, 12, 9, 8, 5, 14, 4, 7, 11, 3, 0, 0 };     // swimming speed, 32nds of a pixel a frame
const uint8_t BAND[][2] PROGMEM = { { 0, 0 }, { 18, 30 }, { 22, 36 }, { 28, 42 }, { 36, 48 }, { 46, 55 }, { 55, 57 }, { 30, 46 }, { 17, 26 }, { BED - 3, BED - 3 }, { BED - 4, BED - 4 }, { BED - 4, BED - 4 } };   // how deep each kind swims

void spr(int16_t x, int16_t y, uint8_t k, uint8_t f) { FX::drawBitmap(x, y, FX_SPR + pgm_read_word(SPROFS + k), f, dbmMasked); }
uint8_t sw(uint8_t k) { return pgm_read_byte(SPRW + k); }
uint8_t sh(uint8_t k) { return pgm_read_byte(SPRH + k); }

enum { F_GONE, F_SWIM, F_FLEE, F_HOOK, F_FREE, F_CHASE, F_STEAL };
struct Fish { float x, y, tx, ty; uint8_t k, st, left, t, lead, sz; };   // sz: how big this one is (6 is average; 10 and up is a lunker)   // lead: the perch it follows in a school (255 = none)
#define NF 14
Fish fish[NF];
struct Turtle { float x; bool on, left; uint8_t t; } turtle[1];   // a snapping turtle
struct Spool { float x, y; uint16_t t; bool on; } spool;
int16_t spX; uint8_t spT;                                      // a splash at the surface

enum { S_TITLE, S_SOUND, S_TALK, S_PLAY, S_OVER, S_DONE };
uint16_t derbyT;                                               // how long this derby has taken (frames)
uint8_t page;                                                  // which of Larry's pages (0, 1 before the derby; 2 won; 3 lost)
const uint8_t DERBY = 7;                                       // the derby: land one of each of the 7 kinds of fish
uint8_t got;                                                   // which kinds you've landed so far (a bit for each)
uint8_t st = S_TITLE; uint16_t tick, stT;
float bx = 64, bvx, camx; bool bleft;                          // the boat
enum { L_IDLE, L_DOWN, L_UP };
uint8_t lineSt, snapT; float lineLen; int8_t hooked = -1;      // lineLen: how much line is out
float hx, hy, hvx, hvy;                                             // where the hook is (it trails behind when you row) and how fast it's moving
uint8_t lines, combo, level, shakeT, popT, msgT, newBest, casts;
uint8_t want, wantRun;                                         // the fish wanted next (shown in the corner) and how many in a row you've landed
uint16_t caught, spoolT, spawnT, chestT;
struct Save { uint32_t best; uint8_t rec[NKIND]; } sv;            // saved on the FX chip: the best score, and the biggest of each kind you've ever landed
#define best sv.best
uint16_t newRec;                                               // the kinds you set a new record for this derby (a bit each)
uint32_t score; int32_t popV; int16_t popX, popY; uint8_t msg;
uint8_t tally[NKIND];                                             // how big the biggest one of each kind you landed was (0 = none)
const uint8_t LBS[] PROGMEM = { 0, 4, 5, 22, 28, 60, 45, 70, 35, 2, 15, 250 };   // a typical weight for each kind, in tenths of a pound (an average-sized one)
void resetLine();
float sgx, sgy;                                                // where the line got caught on a snag
bool onFloor;                                                  // the lure is resting on the bottom
uint8_t msg2;                                                  // a second line under it (NEW FISH!, LUNKER!, ALREADY GOT!...)
void say(uint8_t s) { msg = s; msgT = 80; msg2 = 0; }
int16_t SX(float x) { return (int16_t)x - (int16_t)camx; }
int16_t lineX() { return (int16_t)bx + (bleft ? -16 : 16); }   // where the rod tip is
bool lineWet() { return lineSt != L_IDLE || lineLen > 0; }
bool lureMoving() { return lineWet() && (fabs(hvx) > 0.12f || fabs(hvy) > 0.3f || (lineSt == L_DOWN && lineLen < 40 && (tick & 1))); }   // a lure being dragged, bobbed or dropping
void pop(int32_t v) { popV = v; popT = 45; popX = lineX(); popY = SURF - 10; }
void addScore(int32_t v) { if (v < 0 && (uint32_t)(-v) > score) score = 0; else score += v; }

void splash(int16_t x) { spX = x; spT = 16; }
bool touching(Fish& f) {                                       // is the hook on this one? only the head counts (its mouth end)
  uint8_t w = sw(f.k), h = sh(f.k);
  if (f.k >= K_BOOT || f.k == K_CRAW) return fabs(f.x - hx) <= w / 2 && fabs(hy - f.y) <= h / 2;   // boots, chests and crawfish: anywhere
  float hw = w * 0.3f + 2;                                      // the front third or so, where the mouth is
  float front = f.left ? f.x - w / 2 : f.x + w / 2, rel = f.left ? hx - front : front - hx;   // how far behind its nose the hook is
  return rel >= -1 && rel <= hw && fabs(hy - f.y) <= h / 2;
}

// ---------------------------------------------------------------- who lives in the lake, each kind in its own way
//  pumpkinseed: shallow, darts about, hits a lure sinking or rising slowly, spooks if it's dragged sideways
//  perch:       little schools behind a leader; like the pumpkinseed
//  bass:        mid water; charges a hook that's being dragged
//  walleye:     deep; eases over to a lure going slowly up or down
//  lake trout:  near the bottom, fast and skittish: any moving hook sends them off
//  catfish:     crawl the bottom; smell out a hook resting on the bottom
//  pike:        lurk among the weeds, then lunge at a dragged hook from a long way off
//  gar:         cruise just under the surface; they steal whatever you're reeling in
//  crawfish:    scuttle along the bottom; bass and catfish hunt them
//  boots and the treasure chest just sit on the bottom
bool crowded(Fish& me, float x, float y) {                     // would another fish be right there? (its own school doesn't count)
  for (auto& o : fish) if (&o != &me && o.st != F_GONE && o.st != F_HOOK && fabs(o.x - x) < 22 && fabs(o.y - y) < 9
      && !(me.lead != 255 && &o == &fish[me.lead]) && !(o.lead != 255 && &fish[o.lead] == &me)) return true;
  return false;
}
void pickTarget(Fish& f) {
  for (uint8_t tries = 0; tries < 4; tries++) {                // somewhere to go that isn't already taken, so they spread out
    int16_t d = f.k == K_GAR ? random(120, 260) : f.k == K_SUN ? random(10, 40) : f.k == K_CRAW ? random(6, 30) : random(20, 110);
    f.tx = f.x + (random(2) ? d : -d);
    if (f.tx < 8) f.tx = 8 + random(40); if (f.tx > WORLD - 8) f.tx = WORLD - 8 - random(40);
    if (f.k == K_CRAW && f.tx > ROOF_X0 - 8 && f.tx < ROOF_X1 + 8) f.tx = f.x;
    f.ty = random(pgm_read_byte(&BAND[f.k][0]), pgm_read_byte(&BAND[f.k][1]) + 1);
    if (!crowded(f, f.tx, f.ty)) break;
  }
  f.t = f.k == K_CAT ? random(60, 200) : f.k == K_PIKE ? random(150, 320) : f.k == K_SUN ? random(10, 40)
      : f.k == K_GAR ? random(5, 30) : f.k == K_CRAW ? random(30, 150) : random(30, 110);   // a pause before it sets off
}
uint8_t countK(uint8_t k) { uint8_t n = 0; for (auto& f : fish) if (f.st != F_GONE && f.k == k) n++; return n; }
uint8_t countAll() { uint8_t n = 0; for (auto& f : fish) if (f.st != F_GONE && f.k <= K_PIKE) n++; return n; }
int8_t freeSlot() { for (uint8_t i = 0; i < NF; i++) if (fish[i].st == F_GONE) return i; return -1; }
int8_t addFish(uint8_t k, int8_t lead) {
  int8_t i = freeSlot(); if (i < 0) return -1; Fish& f = fish[i];
  f.k = k; f.st = F_SWIM; f.left = random(2); f.lead = 255;
  f.sz = 4 + random(5) + (random(6) ? 0 : random(3, 7));      // mostly ordinary, now and then a real lunker
  f.y = random(pgm_read_byte(&BAND[k][0]), pgm_read_byte(&BAND[k][1]) + 1);
  if (lead >= 0) { f.lead = lead; f.x = fish[lead].x + random(-12, 13); f.y = fish[lead].y + random(-5, 6); f.tx = f.x; f.ty = f.y; f.t = 0; return i; }
  for (uint8_t tries = 0; tries < 12; tries++) {               // somewhere you can't see (never on screen at the start), away from other fish
    f.x = random(10, WORLD - 10);
    if (f.x > camx - 16 && f.x < camx + 144 && (st != S_PLAY || stT < 5 || random(4))) continue;
    if (!crowded(f, f.x, f.y)) break;
  }
  if (f.y > BED - 8 && f.x > ROOF_X0 - 8 && f.x < ROOF_X1 + 8) f.x = ROOF_X1 + 20 + random(60);   // (things on the bottom stay out of the wreck)
  pickTarget(f); return i;
}
void spawnFish() {
  uint8_t r = random(100), k;
  if (r < 6 && countK(K_BOOT) < 2) k = K_BOOT;
  else {                                                       // the bigger, deeper kinds show up more as you go
    static const uint8_t W0[7] PROGMEM = { 30, 25, 20, 10, 5, 10, 6 }, W4[7] PROGMEM = { 15, 17, 17, 15, 13, 12, 11 };
    uint8_t lv = level, w[7]; uint8_t tot = 0;
    for (uint8_t i = 0; i < 7; i++) { uint8_t a = pgm_read_byte(W0 + i), b = pgm_read_byte(W4 + i); w[i] = a + ((int8_t)(b - a)) * lv / 4; tot += w[i]; }
    uint8_t q = random(tot); k = K_PIKE;
    for (uint8_t i = 0; i < 7; i++) { if (q < w[i]) { k = K_SUN + i; break; } q -= w[i]; }
  }
  int8_t i = addFish(k, -1);
  if (k == K_PERCH && i >= 0) { uint8_t n = random(1, 3); while (n--) addFish(K_PERCH, i); }   // perch come in schools
}
void newGame() {
  for (auto& f : fish) f.st = F_GONE;
  for (auto& t : turtle) t.on = false; spool.on = false;
  spT = 0;
  score = 0; caught = 0; level = 0; combo = 0; lines = 3; lineSt = L_IDLE; lineLen = 0; hooked = -1; snapT = 0; casts = 0;
  bx = DOCK_END + 18; bvx = 0; camx = 0; bleft = false;   // you set off from the dock
  popT = 0; msgT = 0; shakeT = 0; newBest = 0; spoolT = 1500; spawnT = 0; chestT = 900;
  resetLine();
  for (auto& t : tally) t = 0;
  for (uint8_t n = 0; n < 4; n++) spawnFish();
  for (uint8_t n = 0; n < 3; n++) addFish(K_CRAW, -1);
  turtle[0] = { 400, true, true, 0 };
  want = K_SUN; wantRun = 0; derbyT = 0; got = 0;
}
void snap(uint8_t why) {                                         // the line breaks: whatever was on it gets away
  if (hooked >= 0) { fish[hooked].st = F_FREE; fish[hooked].t = 40; hooked = -1; }
  sgx = hx; sgy = hy;                                          // where it caught: the line stays stuck there, pulling the rod right over, then breaks
  lineSt = L_IDLE; lineLen = 0; snapT = 80; combo = 0; wantRun = 0;
  if (lines) lines--;
  say(lines ? why : T_OUT); msgT = 0; snd.tone(400, 40, 300, 40, 400, 40);   // (the words show when it breaks)
}
void land() {                                                  // the catch comes up into the boat
  Fish& f = fish[hooked]; uint8_t k = f.k, z = f.sz; f.st = F_GONE; if (z > tally[k]) tally[k] = z; splash(lineX());
  for (auto& o : fish) if (o.lead == hooked) o.lead = 255;    // its school scatters
  hooked = -1;
  if (k == K_BOOT) { combo = 0; addScore(-100); pop(-100); say(T_BOOT); snd.tone(330, 100, 247, 200); }
  else if (k == K_CHEST) { addScore(2000); pop(2000); say(k); snd.tone(1047, 70, 1319, 70, 1568, 160); }
  else if (k > K_PIKE) { addScore(50); pop(50); say(k); }   // a crawfish: a few points, but it's not a derby fish
  else if (!(got >> k & 1)) {                  // a kind you didn't have yet: its points (times your combo) plus a bonus that grows each time in a row
    got |= 1 << k;
    combo = combo < 5 ? combo + 1 : 5; caught++; level = caught / 4;
    wantRun++; int32_t v = (int32_t)pgm_read_word(POINTS + k) * z / 6 * combo + 300L * wantRun;   // bigger fish are worth more
    say(k); msg2 = T_LB; msgLb = pgm_read_byte(LBS + k) * z / 6;   // and under it, what it weighed
    snd.tone(784, 60, 1047, 60, 1568, 160); addScore(v); pop(v);
  } else {                                                     // one you've already got: it costs you, and your streak
    combo = 0; wantRun = 0; addScore(-100); pop(-100);
    if (lines) lines--;                                        // and a line
    say(k); msg2 = T_ALREADY; snd.tone(330, 90, 220, 160);
  }
  shakeT = pgm_read_byte(WEIGHT + k) * 3;
}

void chase(Fish& f, uint8_t t) { f.st = F_CHASE; f.t = t; f.lead = 255; }
void updateFish() {
  float spm = 1.0f + level * 0.06f; bool wet = lineWet() && hooked < 0 && !snapT, moving = lureMoving();
  bool still = wet && !moving, onBottom = wet && hy >= BED - 6, gentle = wet && fabs(hvx) < 0.2f;   // gentle: going straight down or up, not dragged sideways
  for (uint8_t i = 0; i < NF; i++) {
    Fish& f = fish[i]; if (f.st == F_GONE) continue;
    if ((f.k == K_BOOT || f.k == K_CHEST) && f.st != F_HOOK) { if (f.y < BED - 4) f.y += 0.6f; else f.st = F_SWIM; continue; }   // they just sink back down
    float sp = pgm_read_byte(SWIM + f.k) / 32.0f * spm;
    float dx = f.x - hx, dy = f.y - hy, ax = fabs(dx), ay = fabs(dy);
    if (f.st == F_SWIM && wet && lineSt == L_DOWN && f.k != K_CRAW && ax < 10 && dy > 0 && dy < 14 && random(25) == 0) {   // a hook dropping on its head can startle it
      f.st = F_FLEE; f.t = 35; f.tx = f.x + (dx > 0 ? 50 : -50); f.lead = 255; }
    if (f.st == F_SWIM && wet) {                               // how each kind reacts to your hook
      switch (f.k) {
        case K_SUN: case K_PERCH:                              // like real panfish: they hit a lure sinking or rising slowly, but one dragged sideways spooks them
          if (!gentle && ax < 18 && ay < 12 && random(3) == 0) { f.st = F_FLEE; f.t = 50; f.tx = f.x + (dx > 0 ? 70 : -70); f.lead = 255; }
          else if (gentle && ax < 22 && ay < 12 && random(60) == 0) chase(f, 60); break;
        case K_TROUT:                                          // wary: a hook dragged or bobbed close by, or the boat rowing hard over them, sends them off;
          if ((fabs(hvx) > 0.25f || fabs(bvx) > 0.7f) && ax < 22 && ay < 14 && random(6) == 0) { f.st = F_FLEE; f.t = 60; f.tx = f.x + (dx > 0 ? 90 : -90); }
          else if (still && ax < 30 && ay < 16 && random(70) == 0) chase(f, 90); break;   // ...but they'll come to a hook left still near them
        case K_BASS: if (moving && ax < 30 && ay < 12 && random(12) == 0) chase(f, 70); break;
        case K_PIKE: if (moving && ax < 40 && ay < 14 && random(10) == 0) chase(f, 50); break;   // a lunge from its hiding spot
        case K_WALL: if (ax < 22 && ay < 10 && random(gentle ? 90 : 300) == 0) chase(f, 60); break;   // eases over to a slow lure
        case K_CAT: if (onBottom && still && ax < 40 && random(80) == 0) chase(f, 120); break;   // smells it out
      }
    }
    if (f.st == F_SWIM && hooked >= 0 && f.k == K_GAR && fish[hooked].k != K_GAR) {   // a gar goes after the fish on your line
      Fish& h = fish[hooked]; if (fabs(f.x - h.x) < 70 && fabs(f.y - h.y) < 30) { f.st = F_CHASE; f.t = 200; }
    }
    if (f.st == F_SWIM && hooked >= 0 && (f.k == K_PIKE || f.k == K_BASS) && fish[hooked].k <= K_PERCH) {   // a pike or bass may go for a little fish on your line
      Fish& h = fish[hooked]; if (fabs(f.x - h.x) < 45 && fabs(f.y - h.y) < 25 && random(150) == 0) { f.st = F_STEAL; f.t = 150; f.lead = 255; }
    }
    if (f.st == F_SWIM && (f.k == K_BASS || f.k == K_CAT) && (tick & 15) == (i & 15))   // bass and catfish hunt crawfish
      for (auto& c : fish) if (c.st == F_SWIM && c.k == K_CRAW && fabs(c.x - f.x) < 40 && fabs(c.y - f.y) < 20) { f.tx = c.x; f.ty = c.y; f.t = 0; break; }
    if (f.k == K_BASS || f.k == K_CAT) for (auto& c : fish) if (c.st == F_SWIM && c.k == K_CRAW && fabs(c.x - f.x) < 5 && fabs(c.y - f.y) < 4) { c.st = F_GONE; break; }   // gulp
    switch (f.st) {
      case F_STEAL: {                                          // chasing the little fish you're reeling in
        if (hooked < 0 || fish[hooked].k > K_PERCH || !--f.t) { f.st = F_SWIM; pickTarget(f); break; }
        Fish& h = fish[hooked];
        if (fabs(f.x - h.x) < 6 && fabs(f.y - h.y) < 5) {       // got it
          h.st = F_GONE; hooked = -1; combo = 0; wantRun = 0; addScore(-100); pop(-100);
          say(f.k == K_PIKE ? T_PIKEGOT : T_BASSGOT); snd.tone(300, 60, 200, 120);
          f.st = F_FLEE; f.t = 60; f.tx = f.x + (f.left ? -80 : 80); break;
        }
        float c = f.k == K_PIKE ? 2.2f : 1.8f;
        f.left = h.x < f.x; if (fabs(h.x - f.x) > sp * c) f.x += f.left ? -sp * c : sp * c;
        f.y += h.y > f.y ? 0.45f : -0.45f; if (f.y < 16) f.y = 16;
      } break;
      case F_CHASE: {
        float gx = hx, gy = hy;
        if (f.k == K_GAR) {
          if (hooked < 0) { f.st = F_SWIM; pickTarget(f); break; }
          Fish& h = fish[hooked]; gx = h.x; gy = h.y;
          if (fabs(f.x - gx) < 6 && fabs(f.y - gy) < 5) {     // it steals your fish
            h.st = F_GONE; hooked = -1; combo = 0; wantRun = 0; addScore(-100); pop(-100);
            say(T_GARGOT); snd.tone(300, 60, 200, 120); f.st = F_FLEE; f.t = 60; f.tx = f.x + (f.left ? -80 : 80); break;
          }
        } else if (!wet || !--f.t) { f.st = F_SWIM; pickTarget(f); break; }
        else if (fabs(f.x - gx) < 12 && fabs(f.y - gy) < 8 && random(30) == 0) {   // sometimes it gets wary at the last moment and turns away
          f.st = F_FLEE; f.t = 40; f.tx = f.x + (f.x > gx ? 50 : -50); break; }
        float c = f.k == K_PIKE ? 4.0f : f.k == K_BASS ? 2.5f : f.k == K_GAR ? 1.6f : f.k == K_CAT ? 1.5f : 1.0f;
        f.left = gx < f.x; if (fabs(gx - f.x) > sp * c) f.x += f.left ? -sp * c : sp * c;
        f.y += gy > f.y ? 0.35f : -0.35f;
        float lo = (f.k == K_CAT ? 48 : 16), hi = BED - 3; if (f.y < lo) f.y = lo; if (f.y > hi) f.y = hi;
      } break;
      case F_SWIM: case F_FLEE: case F_FREE: {
        if (f.st == F_FREE) { sp *= 2.2f; f.tx = f.x + (f.left ? -20 : 20); if (!--f.t) { f.st = F_SWIM; pickTarget(f); } }
        else if (f.st == F_FLEE) { sp *= 2.4f; if (!--f.t) { f.st = F_SWIM; pickTarget(f); } }
        else if (f.lead != 255) {                              // in a school: keep close behind the leader
          Fish& L = fish[f.lead];
          if (L.st != F_SWIM && L.st != F_FLEE) { f.lead = 255; pickTarget(f); break; }
          f.tx = L.x + (L.left ? 7 : -7) * (1 + (i & 1)); f.ty = L.y + ((i & 2) ? 4 : -4);
          if (fabs(f.tx - f.x) < 2) { f.left = L.left; if (fabs(f.ty - f.y) > 0.3f) f.y += f.ty > f.y ? 0.25f : -0.25f; break; }
          sp *= 1.3f;
        }
        else if (f.t) { f.t--; if ((tick & 31) == (i & 31) && f.k != K_CRAW) f.y += random(-1, 2) * 0.5f; break; }   // idling, drifting a little
        if (f.k == K_SUN && f.st == F_SWIM) sp *= (tick >> 2) & 3 ? 0.4f : 2.5f;       // quick little darts
        if (f.k == K_CRAW) sp *= (tick >> 3) & 1;                                       // scuttle, stop, scuttle
        f.left = f.tx < f.x;
        if (fabs(f.tx - f.x) <= sp) { f.x = f.tx; if (f.st == F_SWIM && f.lead == 255) pickTarget(f); } else f.x += f.left ? -sp : sp;
        if (f.x < 6) { f.x = 6; f.tx = 40; } if (f.x > WORLD - 6) { f.x = WORLD - 6; f.tx = WORLD - 40; }
        if (fabs(f.ty - f.y) > 0.3f) f.y += f.ty > f.y ? 0.25f : -0.25f;
        float lo = pgm_read_byte(&BAND[f.k][0]) - 4, hi = pgm_read_byte(&BAND[f.k][1]) + 2; if (hi > BED - 3) hi = BED - 3; if (f.y < lo) f.y = lo; if (f.y > hi) f.y = hi;
      } break;
      case F_HOOK: {                                           // hooked by the mouth: its nose stays on the hook and it thrashes, swinging its tail side to side
        if ((tick & 15) == 0) f.left = !f.left;
        int8_t w2 = sw(f.k) / 2; f.x = hx + (f.left ? w2 : -w2); f.y = hy;
      } break;
    }
  }
  if (spawnT) spawnT--;
  else {
    spawnT = 90;
    if (countAll() < 5) spawnFish();
    if (countK(K_CRAW) < 3) addFish(K_CRAW, -1);
    if (countK(K_GAR) < (caught >= 3)) addFish(K_GAR, -1);   // a gar turns up once you've landed 3 of the 7
    if (got != 0xFE) { do want = want % K_PIKE + 1; while (got >> want & 1); }   // the corner shows each kind you still need, in turn
    if (!countK(want)) addFish(want, -1);                    // (and makes sure there's one out there)
  }
  if (chestT) chestT--;                                        // now and then a treasure chest lies on the bottom
  else { chestT = random(1800, 3000); if (!countK(K_CHEST)) addFish(K_CHEST, -1); }
}
// Snags: sunken logs lying at an angle on the bottom. Get the hook caught on one and
// the line's gone, like a real snag.
const int16_t LOGS[3][4] = { { 112, BED, 146, BED - 13 }, { 338, BED, 306, BED - 11 }, { 452, BED, 478, BED - 9 } };
void updateSnags() {
  if (!lineWet() || snapT) return;
  int16_t px = hx, py = hy;
  for (auto& L : LOGS) {                                       // the hook touching a log
    int16_t lo = min(L[0], L[2]), hi = max(L[0], L[2]);
    if (px >= lo && px <= hi) { int16_t ly = L[1] + (int32_t)(px - L[0]) * (L[3] - L[1]) / (L[2] - L[0]); if (abs(py - ly) < 3) { snap(T_SNAG); return; } }
  }
}
void drawSnags(int16_t sy) {
  for (auto& L : LOGS) {
    int16_t x0 = SX(L[0]), y0 = L[1] + sy, x1 = SX(L[2]), y1 = L[3] + sy;
    if (x0 < -40 || x0 > 168) continue;
    ab.drawLine(x0, y0 - 1, x1, y1, WHITE); ab.drawLine(x0, y0 - 2, x1, y1 - 1, WHITE);   // a fat old log
    int16_t mx = (x0 + x1) / 2; ab.drawLine(mx, (y0 + y1) / 2 - 2, mx + (x1 > x0 ? -3 : 3), (y0 + y1) / 2 - 7, WHITE);   // a broken-off branch sticking up
  }
}
void updateHazards() {
  updateSnags();
  do { Turtle& t = turtle[0];                                      // the snapping turtle plods along the bottom
    if (!t.on) { if ((tick & 511) == 300) { t.on = true; t.left = random(2); t.x = t.left ? WORLD + 12 : -12; t.t = 0; } continue; }
    if (lineWet() && onFloor && fabs(hx - t.x) < 50) { t.t = 0; t.left = hx < t.x; }   // a lure sitting on the bottom draws it over
    if (t.t) t.t--; else { t.x += t.left ? -0.15f : 0.15f; if (random(400) == 0) t.t = random(60, 200); }
    if (t.x < -20 || t.x > WORLD + 20) { t.on = false; continue; }
    if (lineWet() && !snapT && fabs(hx - t.x) < 11 && hy > BED - 12) { snap(T_TURTLE); snd.tone(120, 80, 90, 160); }
  } while (0);
  if (spoolT) spoolT--;                                        // a spool of line sinks down now and then
  else if (!spool.on) { spool = { camx + random(20, 108), (float)SURF + 2, 0, true }; if (spool.x > ROOF_X0 - 6 && spool.x < ROOF_X1 + 6) spool.x = ROOF_X1 + 12; spoolT = random(2400, 3600); }
  if (spool.on) { spool.y += 0.18f; if (spool.y > BED - 4) spool.on = false; }   // it sinks, and once it's on the bottom it's gone
}
float depthAt(float x) { return (x > ROOF_X0 && x < ROOF_X1) ? ROOF_Y : BED - 1; }
// The line is a little chain of points, like a real line in water: the top is tied to where the line enters the water under
// the rod tip, gravity sinks it (the hook most), the water slows every point down, and the line can't stretch. So when you
// row, the line bends back into a curve and the hook trails behind, riding a bit higher the faster you go, but never out of the water.
#define NODES 9
float nx[NODES], ny[NODES], ox_[NODES], oy_[NODES];
void resetLine() { float rx = lineX(); for (uint8_t i = 0; i < NODES; i++) { nx[i] = ox_[i] = rx; ny[i] = oy_[i] = SURF + 1; } hx = rx; hy = SURF + 1; hvx = 0; }
void moveHook() {
  float rx = lineX();
  if (!lineWet()) { resetLine(); return; }
  float seg = lineLen / (NODES - 1);
  nx[0] = ox_[0] = rx; ny[0] = oy_[0] = SURF + 1;              // where the line goes into the water
  float px = nx[NODES - 1];
  for (uint8_t i = 1; i < NODES; i++) {                         // drift, slowed by the water, and sink
    float vx = (nx[i] - ox_[i]) * 0.9f, vy = (ny[i] - oy_[i]) * 0.9f;
    ox_[i] = nx[i]; oy_[i] = ny[i];
    nx[i] += vx; ny[i] += vy + (i == NODES - 1 ? 0.3f : 0.04f);   // (a heavier hook: it answers the button quickly)
  }
  for (uint8_t it = 0; it < 5; it++) {                          // the line can't stretch
    for (uint8_t i = 1; i < NODES; i++) {
      float dx = nx[i] - nx[i - 1], dy = ny[i] - ny[i - 1], d = sqrt(dx * dx + dy * dy);
      if (d > seg && d > 0.001f) { float k = (d - seg) / d; if (i == 1) { nx[i] -= dx * k; ny[i] -= dy * k; } else { nx[i] -= dx * k * 0.5f; ny[i] -= dy * k * 0.5f; nx[i - 1] += dx * k * 0.5f; ny[i - 1] += dy * k * 0.5f; } }
    }
    for (uint8_t i = 1; i < NODES; i++) {                       // never out of the water, never through the bottom (or the wreck's deck)
      if (!(nx[i] > -999 && nx[i] < 9999 && ny[i] > -99 && ny[i] < 999)) { nx[i] = rx; ny[i] = SURF + 1; }   // (safety)
      if (ny[i] < SURF + 2) ny[i] = SURF + 2;
      float fl = depthAt(nx[i]); if (ny[i] > fl) ny[i] = fl;
    }
  }
  hvy = ny[NODES - 1] - hy; hx = nx[NODES - 1]; hy = ny[NODES - 1]; hvx = hx - px;
  onFloor = hy >= depthAt(hx) - 0.5f;
}
void hookCheck() {                                             // the hook grabs the first thing it touches
  for (uint8_t i = 0; i < NF && hooked < 0; i++) {
    Fish& f = fish[i]; if (f.st == F_GONE || f.st == F_HOOK) continue;
    if (touching(f)) { if (f.k == K_GAR) { snap(T_GARCUT); return; }   // a gar's teeth go right through your line
      hooked = i; f.st = F_HOOK; lineSt = L_UP; snd.tone(1500, 30, 2000, 50); }
  }
}
void updateLine() {
  if (snapT) { snapT--; bvx *= 0.8f; if (snapT == 50) { shakeT = 12; msgT = 80; snd.tone(1400, 30, 300, 60, 150, 120); } moveHook(); return; }   // held fast... then SNAP
  if (!lines) return;
  if (AB_JUST && lineSt == L_IDLE) { lineSt = L_DOWN; if (casts < 255) casts++; snd.tone(900, 20, 700, 20); splash(lineX()); }
  else if (AB_JUST && lineSt == L_UP && hooked < 0) lineSt = L_DOWN;   // press again while reeling in: it drops back down (so you can bob the line)
  if (lineSt == L_DOWN && !AB_HELD) lineSt = L_UP;            // let go: you reel the line back in
  if (lineSt == L_DOWN) {
    if (!onFloor && lineLen < depthAt(lineX()) - SURF + 4) { lineLen += 0.4f; if ((tick & 3) == 0) snd.tone(1100 - (int16_t)lineLen * 12, 8); }   // lets out line until the hook hits bottom
    { static bool was; if (onFloor && !was) snd.tone(140, 40); was = onFloor; }                         // thunk: it rests there until you let go
    moveHook(); hookCheck();
    if (lineSt == L_DOWN && spool.on && fabs(spool.x - hx) < 5 && hy >= spool.y - 3 && hy <= spool.y + 4) {
      spool.on = false; lineSt = L_UP; if (lines < 5) lines++; say(T_LINE); snd.tone(1047, 40, 1568, 80);
    }
  } else if (lineSt == L_UP) {
    float spd = 0.77f;
    if (hooked >= 0) {
      uint8_t w = pgm_read_byte(WEIGHT + fish[hooked].k); spd = w == 1 ? 0.45f : w == 2 ? 0.32f : w == 3 ? 0.21f : w == 4 ? 0.16f : 0.11f;
      if ((tick & 7) == 0) snd.tone(250 + (int16_t)lineLen * 8, 25);
      if (w >= 3) bvx += fish[hooked].left ? -0.03f : 0.03f;    // a big one tugs the boat about
    } else if ((tick & 7) == 0) snd.tone(1800, 4);             // an empty reel just clicks
    lineLen -= spd; if (lineLen < 0) lineLen = 0;
    moveHook();
    if (hooked < 0) hookCheck();                               // like real fishing, a fish can take the hook as you reel in
    if (lineLen <= 0) { lineSt = L_IDLE; if (hooked >= 0) land(); }
  } else moveHook();
}
void updateBoat() {
  bool L = ab.pressed(LEFT_BUTTON), R = ab.pressed(RIGHT_BUTTON);
  float acc = lineSt == L_IDLE ? 0.08f : 0.04f, top = lineSt == L_IDLE ? 1.5f : 1.0f;
  if (L) bvx -= acc; if (R) bvx += acc; if (!L && !R) bvx *= 0.93f;
  if (bvx > top) bvx = top; if (bvx < -top) bvx = -top;
  if (!lineWet()) { if (L && !R) bleft = true; if (R && !L) bleft = false; }   // the rod swaps sides only when the line is in
  bx += bvx; if (bx < DOCK_END + 16) { bx = DOCK_END + 16; bvx = 0; }   // (bumps up against the dock)
  if (bx > WORLD - 18) { bx = WORLD - 18; bvx = 0; }
  float w = bx - 64; if (w < 0) w = 0; if (w > WORLD - 128) w = WORLD - 128;
  camx += (w - camx) * 0.15f;
}

// ---------------------------------------------------------------- drawing
const uint8_t WAVE[16] PROGMEM = { 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0 };
void drawLake(int16_t sy) {
  for (uint8_t i = 0; i < 34; i++) {                         // stars, drifting slowly as you row, each twinkling in its own time
    uint8_t h = i * 97 + 31, y = (uint8_t)(i * 7 + (h >> 4)) % 11;
    int16_t x = (int16_t)(i * 61 + h) % 192 - (int16_t)(camx / 4); x = ((x % 192) + 192) % 192;
    if (x > 127 || (x < 56 && y < 8)) continue;               // (not behind the score)
    uint8_t ph = (uint8_t)(tick + h * 3) & 127;
    if (ph < 6 && (i & 3)) continue;                          // a quick blink off
    if (i % 5 == 0 && ph > 112) {                             // the bright ones flare into a little sparkle
      uint8_t r = ph > 120 ? 2 : 1;
      ab.drawFastHLine(x - r, y + sy, 2 * r + 1, WHITE); ab.drawFastVLine(x, y - r + sy, 2 * r + 1, WHITE);
    } else ab.drawPixel(x, y + sy, WHITE);
  }
  for (int16_t x = 0; x < 128; x++) {                         // the water line, rolling
    uint8_t w = pgm_read_byte(WAVE + ((x + (int16_t)camx + (tick >> 3)) & 15));
    ab.drawPixel(x, SURF + w + sy, WHITE); if ((x & 3) == 0 && w == 0) ab.drawPixel(x, SURF + 2 + sy, WHITE);
  }
  for (int16_t x = -((int16_t)camx & 63); x < 128; x += 64) FX::drawBitmap(x, BED - 4 + sy, FX_BED, 0, dbmMasked);   // the lake bottom: sand, grains and pebbles
  if (camx < DOCK_END + 4) {                                   // the dock, at the far left
    int16_t d0 = SX(0), d1 = SX(DOCK_END);
    ab.fillRect(d0, SURF - 3 + sy, d1 - d0 + 1, 3, BLACK);     // (hides the waves under it)
    ab.drawFastHLine(d0, SURF - 3 + sy, d1 - d0 + 1, WHITE); ab.drawFastHLine(d0, SURF - 1 + sy, d1 - d0 + 1, WHITE);   // the deck
    for (int16_t x = 3; x <= DOCK_END; x += 4) ab.drawPixel(SX(x), SURF - 2 + sy, WHITE);   // plank ends
    for (int16_t x = 2; x <= DOCK_END; x += 14) {               // posts, down to the bottom (dotted under the water)
      ab.drawFastVLine(SX(x), SURF + sy, 2, WHITE); for (int16_t y = SURF + 3; y < BED; y += 2) ab.drawPixel(SX(x), y + sy, WHITE); }
  }
  for (int16_t w = 12; w < WORLD; w += 37) {                  // weeds swaying
    int16_t x = SX(w); if (x < -4 || x > 131 || (w > ROOF_X0 - 8 && w < ROOF_X1 + 8)) continue;
    uint8_t h = 6 + (w * 7) % 13;
    for (uint8_t y = 0; y < h; y++) ab.drawPixel(x + ((((y + (tick >> 4) + w) >> 2) & 1) ? 1 : 0), BED - 1 - y + sy, WHITE);
  }
}
void drawFish(Fish& f, int16_t sy) {
  int16_t x = SX(f.x) - sw(f.k) / 2, y = (int16_t)f.y - sh(f.k) / 2 + sy; if (x > 130 || x + sw(f.k) < -2) return;
  bool moving = f.st != F_SWIM || !f.t;
  spr(x, y, f.k, (f.left ? 2 : 0) + (moving ? (tick >> (f.st == F_SWIM ? 3 : 2)) & 1 : 0));
}
// The rod, drawn from his hands to the tip, so it can bend: a fish on the line bends it (the heavier, the more, and it
// jerks as the fish fights), dragging the line bends it a little, and a press of the button gives it a twitch.
float rodBend;
int16_t rodTX, rodTY;                                          // where the tip ended up (the line hangs from there)
void drawRod(int16_t bsx, int16_t boy, bool left, float bend) {
  int8_t s = left ? -1 : 1;
  int16_t bx0 = bsx + s * 9, by0 = boy + 6;                     // the butt, held in Larry's beak
  int16_t tx = bsx + s * 16, ty = boy;                          // the tip when the rod is straight
  tx -= (int16_t)(s * bend * 4); ty += (int16_t)(bend * 7);     // bent: the tip pulls down and in
  int16_t mx = (bx0 + bsx + s * 16) / 2 + (int16_t)(s * bend * 1.5f), my = (by0 + boy) / 2 - (int16_t)(bend * 1.5f);   // the middle bows up
  ab.drawLine(bx0, by0, mx, my, WHITE); ab.drawLine(mx, my, tx, ty, WHITE);
  rodTX = tx; rodTY = ty;
}
void drawPlay() {
  int16_t sy = shakeT ? (int8_t)((tick & 2) ? 1 : -1) : 0;
  drawLake(sy);
  for (auto& f : fish) if (f.st != F_GONE && f.st != F_HOOK) drawFish(f, sy);
  for (auto& t : turtle) if (t.on) { int16_t x = SX(t.x) - 11; if (x > -24 && x < 130) spr(x, BED - 8 + sy, K_TURTLE, (t.left ? 2 : 0) + (t.t ? 0 : (tick >> 4) & 1)); }   // the snapping turtle (it walks behind the wreck)
  FX::drawBitmap(SX(WRECK_X), WRECK_Y + sy, FX_WRECK, 0, dbmMasked);   // fish can hide behind and under the wreck
  drawSnags(sy);
  if (spool.on) spr(SX(spool.x) - 4, (int16_t)spool.y - 4 + sy, K_SPOOL, 0);
  // the boat and the line
  int16_t bsx = SX(bx), boy = 1 + ((tick >> 5) & 1) + sy; uint8_t bf = hooked >= 0 ? 1 : 0;
  int16_t lx = SX(lineX());
  { float tgt = 0;                                              // how much the rod bends right now
    if (hooked >= 0) tgt = 0.25f + 0.13f * pgm_read_byte(WEIGHT + fish[hooked].k) + (((tick >> 2) + (tick >> 4)) & 1 ? 0.12f : 0);
    else if (lineWet()) { tgt = fabs(hvx) * 0.8f + (onFloor ? 0 : 0.06f); if (tgt > 0.5f) tgt = 0.5f; }
    if (snapT > 50) tgt = 1.1f + (tick & 2 ? 0.15f : 0);         // snagged: bent right over, straining
    rodBend += (tgt - rodBend) * 0.2f; if (AB_JUST && lineWet()) rodBend += 0.25f; }
  drawRod(bsx, boy, bleft, rodBend);                         // (worked out before the line, which hangs from its tip)
  if (snapT > 50) ab.drawLine(rodTX, rodTY, SX(sgx), (int16_t)sgy + sy, WHITE);   // snagged: the line pulled tight to where it's caught
  else if (snapT) ab.drawLine(rodTX, rodTY, rodTX - (bleft ? -2 : 2), rodTY + 6 + ((tick >> 2) & 1), WHITE);   // snapped: a loose end flapping from the rod
  int16_t jx = SX(hx), jy = (int16_t)hy + sy; bool jig = hooked < 0, drag = fabs(hvx) > 0.2f, flip = hvx < 0, mov = lureMoving();
  if (lineWet()) {
    ab.drawLine(rodTX, rodTY, lx, SURF + sy, WHITE);            // from the rod tip into the water, then along its curve to the hook
    for (uint8_t i = 1; i < NODES; i++) ab.drawLine(SX(nx[i - 1]), (int16_t)ny[i - 1] + sy, SX(nx[i]), (int16_t)ny[i] + sy, WHITE);
  } else if (!snapT) {                                         // line in: the jig dangles from the rod tip, swaying, and swings back when you row
    uint8_t w = (tick >> 3) & 7; jx = rodTX - (int16_t)(bvx * 3) + (w < 4 ? w : 7 - w) - 1; jy = rodTY + 5;
    ab.drawLine(rodTX, rodTY, jx, jy - 1, WHITE); drag = fabs(bvx) > 0.5f; flip = bvx < 0; mov = drag;
  } else jig = false;
  if (jig) {                                                   // the lure: a small jig. It hangs with its skirt down when still, and when you drag it
    static const uint8_t JIG[4][6] PROGMEM = { { 4,14,14,10,21,10 }, { 4,14,14,14,10,10 }, { 8,29,30,5,0,0 }, { 8,30,29,2,0,0 } };   // the skirt streams out behind it
    uint8_t fr = (drag ? 2 : 0) + ((tick >> (mov ? 2 : 4)) & 1); flip &= drag;   // (dragged left: mirror it so the head leads)
    int16_t x0 = jx - 2, y0 = jy - 1;
    for (uint8_t r = 0; r < 6; r++) { uint8_t b = pgm_read_byte(&JIG[fr][r]);
      for (uint8_t c = 0; c < 5; c++) if (b >> c & 1) { int16_t px = flip ? x0 + 4 - c : x0 + c; ab.drawPixel(px, y0 + r, WHITE); } }
  }
  if (hooked >= 0) drawFish(fish[hooked], sy);
  spr(bsx - 15, boy, K_BOAT, (bleft ? 2 : 0) + bf);
  if (spT) { spT--; int8_t r = (16 - spT) / 3; int16_t x = SX(spX), y = SURF - 1 - (spT > 8) + sy; ab.drawPixel(x - r - 1, y, WHITE); ab.drawPixel(x + r + 1, y, WHITE); ab.drawPixel(x - r, y - 1, WHITE); ab.drawPixel(x + r, y - 1, WHITE); }   // splash
  // score, line left, combo, and the fish wanted next
  at(0, 0); pn(score);
  { int16_t hx0 = nlen(score) * 6 + 2;                         // line left (little hooks) and your streak, along the top after the score
    for (uint8_t i = 0; i < lines; i++) { int16_t x = hx0 + i * 5; ab.drawRect(x + 1, 0, 3, 3, WHITE); ab.drawFastVLine(x + 2, 3, 4, WHITE); ab.drawPixel(x + 1, 7, WHITE); ab.drawFastVLine(x, 5, 2, WHITE); }   // each hook: eyelet, shank, bend and point
    if (combo > 1) { at(hx0 + lines * 5 + 2, 0); pc('X'); pn(combo); } }
  at(128 - (nlen(caught) + 3) * 6, 15); pn(caught); pc('/'); pn(DERBY);   // the derby: how many of Larry's fish so far (under the card)
  spr(126 - sw(want), 1, want, 2 + ((tick >> 4) & 1));        // a fish you still need, top right, drawn straight over the sky
  if (popT) { popT--; int16_t y = popY - (45 - popT) / 4; int16_t w = (nlen(popV < 0 ? -popV : popV) + 1) * 6; int16_t x = SX(popX) - w / 2; if (x < 0) x = 0; if (x + w > 127) x = 127 - w;
    ab.fillRect(x - 1, y - 1, w + 1, 9, BLACK); at(x, y); pc(popV < 0 ? '-' : '+'); pn(popV < 0 ? -popV : popV); }
  if (msgT) { msgT--; if (msgT > 10 || (msgT & 2)) { boxText(64, 30, msg); if (msg2) boxText(64, 45, msg2); } }
  if (st == S_PLAY && !casts && stT < 128 && (stT & 32)) boxText(64, 30, T_HOLD);   // first time: how to play (two blinks, then gone)
}

// ---------------------------------------------------------------- screens
const uint16_t WINSONG[] PROGMEM = { 523, 110, 659, 110, 784, 110, 1047, 220, 0, 60, 784, 110, 1047, 450, TONES_END };
const uint16_t LOSESONG[] PROGMEM = { 392, 260, 370, 260, 349, 260, 330, 600, TONES_END };
void titleScreen() {                                           // the logo and a frying pan flipping a pumpkinseed; PRESS A blinks
  FX::drawBitmap(0, 0, FX_LOGO, (tick >> 3) & 7, dbmNormal);
  if (stT == 20) snd.tones(WINSONG);                          // a fanfare to start (the same one as winning the derby)   // 8 frames of the flip
  if (AB_JUST) { randomSeed(micros()); st = S_SOUND; stT = 0; }
}
void soundScreen() {                                           // up / down turns the sound on or off; A or B goes on
  FX::drawBitmap(0, 0, FX_SOUND, !ab.audio.enabled(), dbmNormal);
  if (ab.justPressed(UP_BUTTON) || ab.justPressed(DOWN_BUTTON)) { ab.audio.toggle(); ab.audio.saveOnOff(); snd.tone(880, 40); }
  if (AB_JUST && stT > 5) { st = S_TALK; page = 0; stT = 0; }
}
void talkScreen() {                                            // Loony Larry talks: his words type out into the bubble, a page at a time
  uint8_t shown = stT < 600 ? stT / 3 : 200, n = 0; char ln[12], cur = ' ';   // a letter every 3 frames
  FX::drawBitmap(0, 0, FX_LARRY, shown < 60 ? pgm_read_byte(PSTR("\1\2\1\0") + ((stT >> 2) & 3)) : 3, dbmNormal);   // beak flapping as he talks, then a grin
  for (uint8_t l = 0; l < 5; l++) {
    FX::readDataBytes(FX_TALK + (page * 5 + l) * 12, (uint8_t*)ln, 12); at(51, 5 + l * 11);
    for (uint8_t k = 0; k < 12; k++) { char c = ln[k]; if (n == shown - 1) cur = c; if (n++ < shown) {
      pc(c); } }
  }
  if (shown < 60 && stT % 3 == 0 && cur != ' ') snd.tone(180 + (cur & 7) * 25, 18);   // mumbling: a sound for each letter, a gap between words
  if (AB_JUST) {
    if (shown < 60) stT = 200;                                 // finish the page
    else if (++page == 2) { newGame(); st = S_PLAY; stT = 0; snd.tone(523, 60, 784, 90); }
    else if (page > 2) { st = S_DONE; stT = 0; }
    else stT = 0;
  }
}
void playScreen() {
  updateBoat(); updateLine(); updateFish(); updateHazards(); if (derbyT < 65000) derbyT++;
  if (shakeT) shakeT--;
  drawPlay();
  if ((!lines || caught >= DERBY) && !snapT && hooked < 0) { st = S_OVER; stT = 0; }   // out of line, or the derby's won
}
void overScreen() {                                            // derby won or out of line: a moment to see it, then Larry has his say
  updateBoat(); updateFish(); updateHazards(); if (shakeT) shakeT--;
  bool won = caught >= DERBY; msgT = 0; popT = 0; drawPlay(); boxText(64, 30, won ? T_WON : T_OUT);
  if (stT > 120) {
    if (won) { addScore(500L * lines); if (derbyT < 18000) addScore((18000 - derbyT) / 3); }   // a bonus for every line left, and for finishing quickly (under 5 minutes)
    st = S_TALK; page = won ? 2 : 3; stT = 0; newBest = score > best; if (newBest) best = score;
    newRec = 0; for (uint8_t k = 0; k < NKIND; k++) if (tally[k] > sv.rec[k]) { sv.rec[k] = tally[k]; newRec |= 1 << k; }   // new records: the heaviest of each kind
    if (newBest || newRec) FX::saveGameState(sv);
    snd.tones(won ? WINSONG : LOSESONG);                       // a fanfare, or a sad trombone
  }
}
void doneScreen() {
  at(49, 0); pt(T_SCORE); bigNum(64, 9, score, 2);
  if (caught >= DERBY) { uint16_t t = derbyT / 60; at(98, 0); pn(t / 60); pc(':'); pc('0' + t % 60 / 10); pc('0' + t % 10); }   // how long the derby took, top right
  if (newBest) { if (stT & 16) { at(37, 25); pt(T_NEWBEST); } } else { int16_t w = (5 + nlen(best)) * 6; at(64 - w / 2, 25); pt(T_BEST); pn(best); }
  static uint8_t k;                                            // what you caught, one kind at a time
  if (stT % 90 == 1) for (uint8_t i = 0; i < NKIND; i++) { if (++k > K_CHEST) k = K_SUN; if (tally[k]) break; }
  if (tally[k]) { spr(64 - sw(k) / 2, 33, k, (stT >> 3) & 1);
    uint16_t lb = pgm_read_byte(LBS + k) * tally[k] / 6;   // its weight, from how big it was: e.g. LARGEMOUTH BASS 2.4LB
    if ((newRec >> k & 1) && (stT & 16)) { at(66 + sw(k) / 2, 37); pt(T_RECORD); }   // the heaviest you've ever landed
    int16_t w = (pt(k, false) + 5 + nlen(lb / 10)) * 6; at(64 - w / 2, 47); pt(k); pc(' '); pw(lb); }
  ab.drawFastHLine(0, 55, 128, WHITE);
  at(4, 57); pc('['); pt(T_TITLE); at(74, 57); pt(T_AGAIN); pc(']');
  if (stT > 30) {
    if (AB_JUST || ab.justPressed(RIGHT_BUTTON)) { newGame(); st = S_PLAY; stT = 0; }
    if (ab.justPressed(LEFT_BUTTON)) { st = S_TITLE; stT = 0; }
  }
}

void setup() {
  ab.boot(); ab.display(); FX::begin(FX_DATA_PAGE, FX_SAVE_PAGE); ab.flashlight(); ab.systemButtons(); ab.audio.begin(); ab.setFrameRate(60); ab.waitNoButtons();
  if (!FX::loadGameState(sv)) memset(&sv, 0, sizeof sv);
}
void loop() {
  if (!ab.nextFrame()) return;
  ab.pollButtons(); ab.clear(); tick++; stT++;
  switch (st) {
    case S_TITLE: titleScreen(); break;
    case S_PLAY: playScreen(); break;
    case S_OVER: overScreen(); break;
    case S_DONE: doneScreen(); break;
    case S_TALK: talkScreen(); break;
    case S_SOUND: soundScreen(); break;
  }
  FX::display();
}
