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
                self.clock.tick(30)
                tick -= 1
                continue

            alive = 0
            bf = 0.0
            for i, car in enumerate(self.cars): #add the points and give cars rewards for their progress 
                if not car.alive:
                    continue
                out = self.nets[i].activate(car.nn_inputs())
                steer = out[0]
                accel = (out[1]+1)/2
                brake = max(0, (out[2]+1)/2)
                car.update(steer, accel, brake, self.particles)
                car.cast_rays(self.track.mask)
                car.check_collision(self.track.mask, self.particles)
                car.check_checkpoints(self.track.checkpoints, tick)

                if car.cp_hit > prev_cp[i]:
                    stall[i] = tick
                    prev_cp[i] = car.cp_hit
                elif tick - stall[i] > STALL_TICKS:
                    car.alive = False

                f = car.fitness()
                self.genomes[i][1].fitness = f
                if car.alive:
                    alive += 1
                    bf = max(bf, f)

            self.particles.update()
            self.dash.live(alive, len(self.cars), bf)

            if alive ==0:
                break

            if not self.fast or tick %8 == 0:
                self._render()
                self.clock.tick(FPS_FAST if self.fast else FPS_NORMAL)

        #end of gen
        fits = [g.fitness for _, g in self.genomes]
        sp = self._species_count()
        self.dash.end_gen(self.gen, fits, sp)

        for gid, genome in self.genomes:
            if genome.fitness > self.best_genome_fit:
                self.best_genome_fit = genome.fitness
                self.best_genome = genome

        if not self.running:
            pygame.quit; sys.exit()

    def _species_count(self) -> int:
        try:
            ids = set()
            for _, g in self.genomes:
                sid = getattr(g, "species_id", None)
                if sid is not None:
                    ids.add(sid)
            return max(1, len(ids))
        except Exception:
            return 1
        
    def _update_camera(self):

        leader = self._leader()
        if leader:
            self.cam_tx = leader.x - TRACK_W/2
            self.cam_ty = leader.y - H/2
        else:
            self.cam_tx, self.cam_ty = 0, 0
        lerp = 0.08

        self.cam_x += (self.cam_tx - self.cam_x)*lerp
        self.cam_y += (self.cam_ty-self.cam_y)*lerp

    def _leader(self) -> Car|None:
        best, bf = None, -1.0
        for c in self.cars:
            if c.alive:
                f = c.fitness()
                if f>bf:
                    bf = f; best = c
        return best
    
    #do rendering and main later
                    
        
