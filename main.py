from __future__ import annotations
import argparse
import sys
import neat
import pygame

from core import (
    W, H, TRACK_W, PANEL_W, FPS_NORMAL, FPS_FAST, MAX_TICKS, STALL_TICKS,
    C_GRASS, C_WHITE, C_RED,
    write_neat_config, Car,
)

from tracks import Track, build_base_track, draw_minimap, mutate_track, BASE_TRACK
from visuals import draw_nn, Dashboard



class Simulation:
    def __init__(self, pop_size: int = 120):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H)) 
        pygame.display.set_caption(
            "Self-Driving Car NN"
        )
        self.clock = pygame.time.Clock()
        self.track_surf = pygame.Surface((TRACK_W, H))

        self.pop_size = pop_size #amnt of cars per generation
        self.cfg_path = write_neat_config(pop_size)
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.cfg_path,)
        self.tracks = build_base_track() #Ill add this method later, and make like 7 differnet tracks or something
        self.ti = 0

        self.dash = Dashboard()
        self.dash.track_name = self.track.name

        self.font_l = pygame.font.SysFont("Arial", 22, bold= True) #large meduim and small fonts
        self.font_m = pygame.font.SysFont("Arial", 15)
        self.font_s = pygame.font.SysFont("Arial", 11)

        self.running = True
        self.paused = False
        self.fast = False
        self.gen = 0
        self.difficulty = 1.0 #how hard track is 
        self.mutations = 0

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
            pygame.quit()


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
                    self.running = False; pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    self._key(ev.key)

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

                car.update(steer, accel, brake)
                car.cast_rays(self.track.mask)
                car.check_collision(self.track.mask)
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

        self._evolve_track()

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
    
    def _render(self):
        self._update_camera()
        camera_x = self.cam_x
        camera_y = self.cam_y

        self.track_surf.fill(C_GRASS)
        track_offset_x = -camera_x
        track_offset_y = -camera_y
        self.track_surf.blit(self.track.surface, (track_offset_x, track_offset_y))

        #draw all cars
        leader = self._leader()
        for car in self.cars:
            if not car.alive:
                continue
            if car is leader:
                continue
            car.draw(self.track_surf, camera_x, camera_y, rays=False)

        if leader is not None:
            leader.draw(self.track_surf, camera_x, camera_y, rays=True)

        self.screen.blit(self.track_surf, (0,0))

        #gen counter
        gen_label = self.font_l.render(f"Gen Number {self.gen}", True, C_WHITE)
        label_width = gen_label.get_width()+20
        label_height = gen_label.get_height()+10
        backdrop = pygame.Surface((label_width, label_height), pygame.SRCALPHA)
        backdrop.fill((0,0,0,160))
        self.screen.blit(backdrop, (8,8))
        self.screen.blit(gen_label, (18, 13))


        badge_y = 42

        if self.paused:
            paused_label = self.font_m.render("PAUSD", True, C_RED)
            self.screen.blit(paused_label, (18, badge_y))

        current_speed = 0.0
        if leader is not None:
            current_speed = leader.speed

        all_cars = list(self.cars)
        draw_minimap(self.screen, self.track, all_cars, camera_x, camera_y)

        #neural network image for the best alive car
        best_genome = self._best_alive_genome()

        best_inputs = None
        if leader is not None and leader.alive:
            best_inputs = leader.nn_inputs()

        nn_x = TRACK_W - 290
        nn_y = H-240
        nn_width = 280
        nn_height = 230
        draw_nn(self.screen, best_genome, self.config, nn_x, nn_y, nn_width, nn_height, self.font_s, best_inputs)
        
        #dashboard
        self.dash.draw(self.screen, self.font_l, self.font_m, self.font_s)
        pygame.display.flip()
    def _best_alive_genome(self):
        #find best current car
        best_fitness = -1.0
        best_genome = None

        for i, car in enumerate(self.cars):
            if not car.alive:
                continue

            fitness = car.fitness()
            if fitness > best_fitness:
                best_fitness = fitness
                best_genome = self.genomes[i][1]

        if best_genome is None:
            return self.best_genome
        return best_genome
    
    def _key(self, key):
        if key == pygame.K_SPACE:
            self.paused = not self.paused
            return
        elif key == pygame.K_f:
            self.fast = not self.fast

        elif key == pygame.K_r:
            self.restart()
            return
        
        #track switching
        track_keys = [pygame.K_1, pygame.K_2, pygame.K_3,
            pygame.K_4, pygame.K_5, pygame.K_6,]
        if key in track_keys:
            track_index = key - pygame.K_1
            if track_index < len(self.tracks):
                self.ti = track_index
                self.track = self.tracks[track_index]
                #kill the cars
                for car in self.cars:
                    car.alive = False


def _evolve_track(self):
    #find where all the cars died
    death_positions = []
    for car in self.cars:
        if not car.alive:
            death_positions.append((car.x, car.y))

    #make it a little harder
    self.difficulty += 0.05

    self.track = mutate_track(self.track, death_positions, self.difficulty) #add this function to track
    self.mutations += 1

    self.dash.difficulty = self.difficulty
    self.dash.track_name = self.track.name


def main():
    #main is ai assited
    # read command-line flags (--fast, --pop)
    parser = argparse.ArgumentParser(description="NEAT Self-Driving Car Evolution")
    parser.add_argument("--fast", action="store_true", help="Start in fast mode")
    parser.add_argument("--pop", type=int, default=120, help="Population size")
    args = parser.parse_args()

    # create the simulation
    sim = Simulation(pop_size=args.pop)

    # if the user passed --fast, enable fast mode right away
    if args.fast:
        sim.fast = True

    # welcome banner
    print()
    print("  NEAT Self-Driving Car Evolution Simulator")
    print("  -----------------------------------------")
    print("  The track evolves to fight the AI each generation.")
    print("  Easy sections get harder. Hard sections ease up.")
    print()
    print("  Controls:")
    print("    SPACE  — Pause / Resume")
    print("    F      — Toggle fast mode")
    print("    R      — Reset everything")
    print()

    # start the main loop
    sim.run()

if __name__ == "__main__":
    main()