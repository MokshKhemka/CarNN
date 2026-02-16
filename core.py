from __future__ import annotations

import math
import os
import random
import tempfile
import pygame


W, H = 1440, 860
PANEL_W = 350
TRACK_W = W - PANEL_W

FPS_NORMAL = 60
FPS_FAST = 0

MAX_TICKS = 1500
STALL_TICKS = 350

CAR_W, CAR_H = 18, 36
MAX_SPD = 8.5
MIX_SPD = -2
ACCEL = 0.32
BRAKE_F = 0.55
FRICTION = 0.05
TURN_SPD = 4.2
DRIFT_FACTOR = 0.92
NUM_RAYS = 10
RAY_LEN = 220
RAY_SPREAD = math.pi * 1.1 #around 200 degres

MAX_PARTICLES = 4000
TYRE_MARk_LIFE = 400
SPARK_LIFE = 18


C_ROAD = (90, 150, 90)
C_GRASS = (34, 52, 28)
C_CURB_R = (200, 60, 60)
C_CURB_W = (220, 220, 220)
C_LINE = (200, 200, 200)
C_PANEL_BG = (18, 18, 26)
C_ACCENT = (0, 220, 160)
C_ACCENT2 = (90, 140, 255)
C_ACCENT3 = (255, 180, 50)
C_RED = (255, 70, 70)
C_WHITE = (235, 235, 240)
C_DIM = (140, 140, 155)
C_GRAPH_BG = (28, 28, 42)
C_GRID = (44, 44, 60)

NEAT_CONFIG_STR =  """
[NEAT]
fitness_criterion     = max
fitness_threshold     = 999999999
pop_size              = {pop_size}
reset_on_extinction   = True

[DefaultGenome]
activation_default      = tanh
activation_mutate_rate  = 0.08
activation_options      = tanh sigmoid relu

aggregation_default     = sum
aggregation_mutate_rate = 0.05
aggregation_options     = sum

bias_init_mean          = 0.0
bias_init_stdev         = 1.0
bias_max_value          = 30.0
bias_min_value          = -30.0
bias_mutate_power       = 0.5
bias_mutate_rate        = 0.7
bias_replace_rate       = 0.1

compatibility_disjoint_coefficient = 1.0
compatibility_weight_coefficient   = 0.5

conn_add_prob           = 0.5
conn_delete_prob        = 0.5

enabled_default         = True
enabled_mutate_rate     = 0.01

feed_forward            = True
initial_connection      = full_direct

node_add_prob           = 0.3
node_delete_prob        = 0.3

num_hidden              = 0
num_inputs              = {num_inputs}
num_outputs             = 3

response_init_mean      = 1.0
response_init_stdev     = 0.0
response_max_value      = 30.0
response_min_value      = -30.0
response_mutate_power   = 0.0
response_mutate_rate    = 0.0
response_replace_rate   = 0.0

weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_max_value        = 30
weight_min_value        = -30
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.8
weight_replace_rate     = 0.1

[DefaultSpeciesSet]
compatibility_threshold = 3.0

[DefaultStagnation]
species_fitness_func = max
max_stagnation       = 20
species_elitism      = 2

[DefaultReproduction]
elitism            = 3
survival_threshold = 0.2
"""

def write_neat_config(pop_size= 35):
    txt = NEAT_CONFIG_STR.format(pop_size = pop_size , num_inputs = NUM_RAYS)
    path = os.path.join(tempfile.gettempdir(), "neat_cars_cfg.txt")
    with open(path, "w") as f:
        f.write(txt)
    return path
#to make it look cooler, creating a particle
class Particle:
    x: float
    y: float
    vx: float = 00.0
    vy: float = 0.0
    life: int = 60
    max_life: int = 60
    kind: str = "tyre"
    color: tuple = (80,80,80) #gray
    size: float = 2.0

class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit_tyre(self, x, y):
        if len(self.particles) < MAX_PARTICLES:
            self.particles.append([x, y, 0, 0, TYRE_MARk_LIFE, TYRE_MARk_LIFE])

    def emit_sparks(self, x, y, count = 4):
        for _ in range(count):
            a = random.unifrom(0, math.tau)
            spd = random.uniform(1, 3)
            if len(self.particles) < MAX_PARTICLES:
                self.particles.append([x, y, math.cos(a)*spd, math.sin(a)*spd, SPARK_LIFE, SPARK_LIFE])


