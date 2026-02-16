from __future__ import annotations
import math
import neat
import pygame

from core import(
    W, H, PANEL_W, TRACK_W, MAX_SPD, NUM_RAYS,
    C_PANEL_BG, C_ACCENT, C_ACCENT2, C_ACCENT3, C_RED, C_WHITE, C_DIM,
    C_GRAPH_BG, C_GRID,
)

def draw_speedometer(surf, speed, font):
    center_x = 110
    center_y = H-170
    radius = 55

    bg = pygame.Surface((130, 130), pygame.SRCALPHA)
    pygame.draw.circle(bg, (15, 15, 25, 200), (65, 65), 65)
    surf.blit(bg, (center_x-65, center_y-65))

    fraction = abs(speed)/MAX_SPD
    if fraction > 1.0:
        fraction = 1.0
    start = 135
    sweep = 270