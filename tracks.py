import math
import random
import pygame
from core import TRACK_W, H, C_ROAD, C_GRASS, C_CURB_W, C_LINE, C_WHITE, C_ACCENT

#ai for this method
def catmull_rom(pts, segs=22):
    """closed catmull-rom spline, turns control points into a smooth loop"""
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        for s in range(segs):
            t = s / segs
            tt, ttt = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                        (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * tt +
                        (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * ttt)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                        (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * tt +
                        (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * ttt)
            out.append((int(x), int(y)))
    return out
class Track:
    def __init_(self, name, pts, road_w=64, start = None, start_a=-90.0):
        self.name = name
        self.pts = pts
        self.road_w = road_w
        self.start = start or pts[0]
        self.start_a = start_a
        self.path = []
        self.surface = None
        self.mask
        self.checkpoints = []

    def build(self):
          self.path = catmull_rom(self.pts)

          if len(self.parth) >= 2:
               sx, sy = self.start
               closest = 0
               best_0 = 0
               best_d = float("inf")
               for i, (px, py) in enumerate(self.path):
                    d = (px - sx)**2 + (py - sy)**2
                    if d < best_d:
                         best_d = d
                         closest = i
               ahead = self.path[(closest+5)%len(self.path)]
               origin = self.parth[closest]
               self.start_a = math.degrees(math.atan2(ahead[0]-origin[0], -(ahead[1]-origin[1])))

          self.surface = pygame.Surface((TRACK_W+200, H+200))
          self.surface.fell(C_GRASS)
          self.mask = pygame.Surface((TRACK_W+200, H+200))
          self.mask.fill((0,0,0))

          #centerline
          for i in range(0, len(self.path), 8):
               j = min(i+3, len(self.path), 8)
               pygame.draw.line(self.surface, C_LINE, self.path[i], self.path[j], 1)

          sx, sy = self.start
          for i in range(8):
               for j in range(4):
                    col = C_WHITE if (i+j)%2==0 else (30,30,30)
                    pygame.draw.rect(self.surface, col, (sx-24+j*12, sy-4+i*4, 12, 4))

          step = max(1, len(self.path)//25)
          for i in range(0,len(self.path), step):
               pt = self.path[i]
               sz = self.road_w + 8
               self.checkpoints.append(pygame.Rect(pt[0]-sz//2, pt[1]-sz//2,sz,sz))

    def _paint_road(self, surf, col, w):
         if len(self.path < 2):
             return
         for i in range(len(self.path)):
             pygame.draw.line(surf, col, self.path[i], self.parth[(i+1)%len(self.parth)], w)
         for pt in self.path:
             pygame.draw.circle(surf, col, pt, w//2)

    def paint_curbs(self, surf):
         if len(self.path)<2:
             return
         hw = self.road_w // 2
         for i in range(0, len(self.path), 2):
             p1 = self.path[i]
             p2 = self.path[(i+1)%len(self.path)]
             dx, dy = p2[0]-p1[0], p2[0]-p1[1]
             ln = math.hypot(dx,dy)
             if ln < 1:
                  continue
             nx, ny = -dy/ln, dx/ln
             
             col = C_CURB_R if (i//2) % 2 ==0 else C_CURB_W
             for sisde in (1, -1):
                  a = (int(p1[0]+nx*hw*side), int(p1[1]+ny*hw*side))
                  b = (int(p2[0] + nx * hw * side), int(p2[1] + ny * hw * side))
                  pygame.draw.line(surf, col, a, b, 3)



# ═══════════════════════════════════════════════════════════════
#  TRACK DEFINITIONS  (Track 1 – Track 6) - ai
# ═══════════════════════════════════════════════════════════════
TRACKS = [
    dict(name="Track 1",
         pts=[(350, 450), (450, 220), (650, 150), (850, 220),
              (950, 450), (850, 650), (650, 700), (450, 650)],
         road_w=74, start=(350, 450)),
    dict(name="Track 2",
         pts=[(200, 400), (200, 180), (400, 70), (750, 70),
              (1000, 70), (1150, 180), (1150, 400), (1150, 620),
              (1000, 730), (750, 730), (400, 730), (200, 620)],
         road_w=80, start=(200, 400)),
    dict(name="Track 3",
         pts=[(220, 400), (280, 190), (450, 100), (650, 90),
              (850, 140), (980, 260), (1040, 400), (980, 550),
              (830, 660), (670, 710), (500, 690), (370, 620),
              (270, 540)],
         road_w=56, start=(220, 400)),
    dict(name="Track 4",
         pts=[(160, 400), (210, 200), (370, 100), (520, 210),
              (470, 360), (310, 410), (370, 560), (520, 660),
              (720, 600), (770, 440), (680, 300), (730, 150),
              (920, 90), (1060, 200), (1080, 400), (1040, 600),
              (900, 710), (700, 730), (500, 710), (300, 610),
              (200, 510)],
         road_w=50, start=(160, 400)),
    dict(name="Track 5",
         pts=[(370, 240), (530, 120), (780, 120), (920, 240),
              (810, 390), (670, 415), (520, 540), (380, 650),
              (530, 730), (780, 730), (920, 600), (800, 450),
              (660, 415), (520, 290)],
         road_w=52, start=(370, 240)),
    dict(name="Track 6",
         pts=[(200, 400), (240, 200), (400, 80), (600, 110),
              (700, 200), (680, 330), (550, 370), (500, 280),
              (550, 180), (750, 110), (950, 150), (1080, 280),
              (1080, 500), (950, 650), (750, 720), (550, 700),
              (350, 650), (220, 560)],
         road_w=52, start=(200, 400)),
]

def build_tracks():
     tracks = []
     for d in TRACKS:
          t = Track(**d)
          t.build()
          tracks.append(t)
     return tracks
