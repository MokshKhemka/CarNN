from __future__ import annotations
import math
import neat
import pygame

from core import(
    W, H, PANEL_W, TRACK_W, MAX_SPD, NUM_RAYS,
    C_PANEL_BG, C_ACCENT, C_ACCENT2, C_ACCENT3, C_RED, C_WHITE, C_DIM,
    C_GRAPH_BG, C_GRID,
)

def draw_speedometer(surf: pygame.Surface, speed: float, font: pygame.font.Font):
    cx, cy = 110, H-170
    r_outer = 55
    bg = pygame.Surface((130,130), pygame.SRCALPHA)
    pygame.draw.circle(bg, (15, 15, 25, 200), (65, 65), 65)
    surf.blit(bg, (cx-65, cy-65))

    pct = min(1.0, abs(speed)/MAX_SPD)

    for a_deg in range(135, 406, 3):
        a = math.radians(a_deg)
        px = cx+math.cos(a)*(r_outer-2)
        py=cy+math.sin(a)

    fill_end = 135 + int(pct*270)
    for a_deg in range(135, fill_end, 2):
        a = math.radians(a_deg)