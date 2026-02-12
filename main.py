from __future__ import annotations
import argparse
import sys
import neat
import pygame

from core import(W, H, TRACK_W, PANEL_W, FPS_NORMAL, FPS_FAST, MAX_TICKS, STALL_TICKS,
                 C_GRASS, C_WHITE, CRED, write_neat_config, ParticleSystem, Car,)
from tracks import Track, build_tracks, draw_minimap
from visuals import draw_speedometer, draw_nn, Dashboard
#get all the car stuff from core later



class Simulation:
    def __init__(self, pop_size: int = 120):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H)) #get width and height later too
        pygame.display.set_caption(
            "Self-Driving Car NN"
        )
        self.clock = pygame.time.Clock()
        self.track_surf = pygame.Surface((TRACK_W, H)) #also will get from core
        self.pop_size = pop_size #amnt of cars per generation
        self.cfg_path = write_neat_config(pop_size)
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.cfg_path,)
        self.tracks = build_tracks() #Ill add this method later, and make like 7 differnet tracks or something
        self.ti = 0
        self.track: Track = self.tracks[0]

        self.particles = ParticleSystem()
        self.dash = Dashboard()
        self.dash.track_name = self.track.name

        self.font_l = pygame.font.SysFont("Arial", 22, bold= True) #large meduim and small fonts
        self.font_m = pygame.font.SysFont("Arial", 15)
        self.font_s = pygame.font.SysFont("Arial", 11)

        self.running = True
        self.paused = False
        self.fast = False
        self.gen = 0

        self.cam_x, self.cam_y = 0.0,0.0
        self.cam_tx, self.cam_ty = 0.0,0.0 #make cameras follow cars

        self.cars: list[Car] = []
        self.nets: list = []
        self.genomes: list[tuple] = []
        self.best_genome = None
        self.best_genome_fit = 0.0



    def run(self):
        pop = neat.Population(self.config)
        pop.add_reporter(neat.StdOutReporter(True))
        pop.add_reporter(neat.StatisticsReporter())
        try:
            pop.run(self._eval, 9999)
        except SystemExit:
            pass
        finally:
            pygame.quit

    def _eval(self, genomes, config):
        #just scores ai and gives it reward based on progress
        self.gen += 1
        self.cars.clear()
        self.nets.clear()
        self.genomes.clear()

        sx, sy, sa = self.track.start[0], self.track.start[1], self.track.start_a

        for gid, genome in genomes:
            genome.fitness = 0.0
            self.nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
            self.cars.append(Car(sx,sy,sa))
            self.genomes.append((gid, genome))

        self.dash.total = len(self.cars)
        self.dash.track_name = self.track.name

        tick = 0
        stall = [0] * len(self.cars)
        prev_cp = [0] * len(self.cars)

        while tick < MAX_TICKS and self.running:
            tick += 1
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self. running = False; pygame.quit(); sys.exit()

            if self.paused:
                self._render()