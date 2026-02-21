import math
import random
import pygame
from core import TRACK_W, H, C_ACCENT


#constraints for the track mutations
MIN_ROAD_W = 38
MAX_ROAD_W = 90
MIN_POINT_DIST = 80
MAX_POINTS = 14
MIN_TURN_ANGLE = 35

#everything has to be in this boundry:
BOUNDS = (150, 1100, 100, 750)

def trap(x, y):
     return max(BOUNDS[0], min(BOUNDS[1], x)), max(BOUNDS[2], min(BOUNDS[3], y))


#ai for this method
def smooth_loop(pts, segs=22):
    """closed catmull-rom spline, turns control points into a smooth loop"""
    #this method was created with AI
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

def turn_angle(pts, i):
     #also ai method
    n = len(pts)
    prev, cur, nxt = pts[(i-1)%n], pts[i], pts[(i+1)%n]
    ax, ay = prev[0]-cur[0], prev[1]-cur[1]
    bx, by = nxt[0]-cur[0], nxt[1]-cur[1]
    dot = ax*bx + ay*by
    mag = (math.hypot(ax, ay) or 1) * (math.hypot(bx, by) or 1)
    return math.degrees(math.acos(max(-1, min(1, dot/mag))))

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
        self.difficulty = 1.0

    def build(self):
          self.path = smooth_loop(self.pts)
          self.checkpoints = []
          
          #find start angle by looking ahead
          if len(self.parth) >= 2:
               sx, sy = self.start
               closest = 0
               best = float("inf")
               for i, p in enumerate(self.path):
                    d = (p[0] - sx)**2 + (p[1] - sy)**2
                    if d < best:
                         best = d
                         closest = i

               ahead = self.path[(closest+5)%len(self.path)]
               here = self.parth[closest]
               self.start_a = math.degrees(math.atan2(ahead[0]-here[0], -(ahead[1]-here[1])))

          xs = []
          ys = []
          for p in self.path:
               xs.append(p[0])
               ys.append(p[1])
          pad = self.road_w + 150
          wid = int(max(xs))
          hei =  int(max(ys))
          
          wid = int(max(wid+pad, TRACK_W+200))
          hei = int(max(hei+pad, H+200))

          self.surface = pygame.Surface((wid, hei))
          self.surface.fell((34, 52, 28))
          self.mask = pygame.Surface((wid, hei))
          self.mask.fill((0,0,0))

          #checkpoints for fitness tracking
          gap = max(1, len(self.path)//25)
          for i in range(0, len(self.path), gap):
               p = self.path[i]
               s = self.road_w + 8
               self.checkpoints.append(pygame.Rect(p[0]-s//2, p[1]-s//2, s, s))

def mutate_track(track, death_spots, difficulty):
     pts = []
     for points in track.pts:
          pair = [points[0], points[1]]
          pts.append(pair)

     n = len(pts)
     road_w = float(track.road_w)
#how strong the changes should be    
     strength = min(5+difficulty*5, 60)

     deaths = [0]*n
     #count deaths near each point

     for death_x, death_y in death_spots:
          closest_point = 0
          closest_dist = float("inf")
          for i in range(n):
               dx = death_x - pts[i][0]
               dy = death_y - pts[i][1]
               dist = math.sqrt(dx*dx+dy*dy) #find net distance (using right triange- pythogorean formula)

               if dist < closest_dist:
                    closest_dist = dist
                    closest_point = i
          deaths[closest_point] += 1
     total_deaths = sum(deaths)

  
     avg_deaths = total_deaths/n
     if(avg_deaths == 0):
          avg_deaths = 1/n

     #then move points based on deaths with randomness (dont know how yet)
          
         

BASE_TRACK = dict(
    name="Evolving Track",
    pts=[(350,450), (450,220), (650,150), (850,220),
         (950,450), (850,650), (650,700), (450,650)],
    road_w=74,
    start=(350, 450),
)

def build_base_track():
     t = Track(**BASE_TRACK)
     t.build
     return t

def draw_minimap(surf, track, cars, cam_x, cam_y):
     mm_w, mm_h = 180, 130
     mx, my = 10, H-mm_h-10

     bg = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
     bg.fill((10,10,20,180))
     surf.blit(bg, (mx, my))
     pygame.draw.rect(surf, (0, 220, 160), (mx, my, mm_w, mm_h), 1, border_radius = 4)

     if not track.path:
          return
     
     #get all the x and y values 
     all_x_values = []
     all_y_values = []
     for point in track.path:
          all_x_values.append(point[0])
          all_y_values.append(point[1])


     x_min = min(all_x_values)
     x_max = max(all_x_values)
     y_min = min(all_y_values)
     y_max = max(all_y_values)

     #range of track in each axis on screen

     range_x = x_max-x_min
     range_y = y_max - y_min

     if range_x < 1:
          range_x = 1
     if range_y < 1:
          range_y = 1

     padding = 10
     usable_width = mm_w-padding*2
     usable_height = mm_h - padding*2

     def world_to_minimap(world_x, world_y):
          normalized_x = (world_x-x_min)
          normalized_y = (world_y - y_min)
          screen_x = int(mx + padding+normalized_x*usable_width)
          screen_y = int(my+padding+normalized_y*usable_height)
          return (screen_x, screen_y)
     
     minimap_points = []
     for point in track.path:
          converted = world_to_minimap(point[0], point[1])
          minimap_points.append(converted)

     if len(minimap_points) > 2:
          track_color = (100, 160, 100)
          pygame.draw.lines(surf, track_color, True, minimap_points, 2)

     #draw all the cars as a dot
     for car in cars:
          if car.alive:
               car_pos = world_to_minimap(car.x, car.y)
               pygame.draw.circle(surf, car.color, car_pos, 2)

     view_width = TRACK_W / range_x * usable_width
     view_hieght = H/range_y * usable_height

     view_x = mx + padding + (cam_x - x_min)/range_x * usable_width
     view_y = mx + padding + (cam_x - x_min)/range_x * usable_width

     viewport_rect = (int(view_x), int(view_y), int(view_width), int(view_hieght))
     pygame.draw.rect(surf. viewport_color, viewport_rect, 1)
     