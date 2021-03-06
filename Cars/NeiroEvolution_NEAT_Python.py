# https://neat-python.readthedocs.io/en/latest/
import random
import pygame
import math
import sys
import os
import neat
import pickle
import gzip

from NeiroEvolution.Cars.CompileCollision import turn_rectangle_by_angle, offset_point

width = 650
height = 550
bg = (213, 193, 154, 255)
generation = 0
SRC = 'src/'


class Car:
    car_sprites = ("Audi", "Black_viper", "Orange", "Police", "Taxi")

    def __init__(self):
        self.random_sprite()

        self.angle = 0
        self.speed = 3

        self.radars = []
        self.collision_points = []

        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0
        self.center = []
        self.kill_position = []

    def random_sprite(self):
        self.car_sprite = pygame.image.load(SRC + random.choice(self.car_sprites) + '.png')
        self.car_sprite = pygame.transform.scale(self.car_sprite,
                                                 (math.floor(self.car_sprite.get_size()[0] / 4),
                                                  math.floor(self.car_sprite.get_size()[1] / 4)))
        self.car = self.car_sprite

        self.pos = [256, 469]  # левый верхний угол картинки

        self.compile_center()

    def compile_center(self):
        self.center = (self.pos[0] + (self.car.get_size()[0] / 2), self.pos[1] + (self.car.get_size()[1] / 2))

    def draw(self, screen):
        pos = [int(self.pos[0]), int(self.pos[1])]
        screen.blit(self.car, pos)

    def update(self, road):
        self.speed = 1
        self.distance += self.speed
        # повернем картинку на нужный угол
        self.rotate_sprite()

        # Определим ей новую позицию в зависимости от угла и скорости
        self.set_new_position()

        # update distance & time spent
        self.distance += self.speed
        self.time_spent += 1  # aka turns

        self.compute_collision_points()
        self.check_collisions(road)

        self.compile_radars(road)

    def set_new_position(self):
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.compile_center()

    def rotate_sprite(self):
        self.car = pygame.transform.rotate(self.car_sprite, self.angle)

    def compute_collision_points(self):
        self.collision_points = turn_rectangle_by_angle(-self.angle, self.center, 35, 10)

    def draw_collision_points(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.center[0]), int(self.center[1])), 5)
        for p in self.collision_points:
            # if (road.get_at((int(p[0]), int(p[1]))) == bg):
            pygame.draw.circle(screen, (255, 0, 0), (int(p[0]), int(p[1])), 5)

        # else:
        #     pygame.draw.circle(screen, (15, 192, 252), (int(p[0]), int(p[1])), 5)

    def compile_radars(self, road):
        self.radars.clear()
        radar_cnt = 7
        max_radar_range = 200
        sector = 120
        step = sector / (radar_cnt - 1)
        for i in range(radar_cnt):
            # offset_angle = self.angle + step * i + 45
            offset_angle = self.angle + sector / 2 + (360 - step) * i
            for radar_range in range(max_radar_range):
                radar_position = offset_point(self.center[0], self.center[1], radar_range, -offset_angle)
                if radar_range + 1 == max_radar_range or road.get_at(
                        (int(radar_position[0]), int(radar_position[1]))) == bg:
                    distantion = int(math.sqrt(math.pow(int(radar_position[0]) - int(self.center[0]), 2) + math.pow(
                        int(radar_position[1]) - int(self.center[1]), 2)))
                    self.radars.append([radar_position, distantion])
                    break

    def draw_radars(self, screen):
        for r, distantion in self.radars:
            pygame.draw.line(screen, (255, 255, 40), self.center, r, 1)
            d = [int(r[0]), int(r[1])]
            pygame.draw.circle(screen, (255, 255, 10), d, 5)

    def draw_kill_place(self, screen):
        if not self.is_alive:
            d = [int(self.kill_position[0]), int(self.kill_position[1])]
            pygame.draw.circle(screen, (183, 35, 70), d, 5)

    def check_collisions(self, road):
        for collision in self.collision_points:
            if road.get_at((int(collision[0]), int(collision[1]))) == bg:
                self.is_alive = False
                self.kill_position = collision
                break

    def get_data(self):
        radars = self.radars
        data = [0] * 7

        for i, r in enumerate(radars):
            data[i] = int(r[1] / 30)

        return data

    def get_reward(self):
        return self.distance / 50.0


def run_generation(genomes, config):
    cars = []
    nets = []
    global generation
    generation += 1
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0  # every genome is not successful at the start
        cars.append(Car())

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    road = pygame.image.load(SRC + 'road.png')
    road = pygame.transform.scale(road, (math.floor(road.get_size()[0] / 2),
                                         math.floor(road.get_size()[1] / 2)))

    font = pygame.font.SysFont("Roboto", 30)
    heading_font = pygame.font.SysFont("Roboto", 40)

    # pygame.display.flip()
    while True:
        screen.blit(road, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True

        # input each car data
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            i = output.index(max(output))

            if i == 0:
                car.angle += 5
            elif i == 1:
                car.angle = car.angle
            elif i == 2:
                car.angle -= 5

        cars_left = 0
        max_distance = 0
        for i, car in enumerate(cars):
            if car.is_alive:
                genomes[i][1].fitness += car.get_reward()
                cars_left += 1
                car.update(road)
                max_distance = max(max_distance, car.distance)

            if car.is_alive:
                car.draw_radars(screen)
                car.draw(screen)
                # car.draw_collision_points(screen)

            car.draw_kill_place(screen)
        # if not cars_left:

        if cars_left < 10 or max_distance >= 3800:
            print(f"generation: [{generation}] - max distance: [{max_distance}] - cars left [{cars_left}]")
            save_checkpoint("best_gen_", config, population.population, population.species, population.generation)
            break

        label = heading_font.render("Поколение: " + str(generation), True, (73, 168, 70))
        label_rect = label.get_rect()
        label_rect.center = (width / 1.5, 300)
        screen.blit(label, label_rect)

        label = font.render("Машин осталось: " + str(cars_left), True, (51, 59, 70))
        label_rect = label.get_rect()
        label_rect.center = (width / 1.5, 375)
        screen.blit(label, label_rect)

        pygame.display.flip()

def run_generation_one_car(genomes, config):
    car = Car()
    nets = []
    global generation
    generation += 1
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0  # every genome is not successful at the start

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    road = pygame.image.load(SRC + 'road.png')
    road = pygame.transform.scale(road, (math.floor(road.get_size()[0] / 2),
                                         math.floor(road.get_size()[1] / 2)))

    font = pygame.font.SysFont("Roboto", 30)
    heading_font = pygame.font.SysFont("Roboto", 40)

    # pygame.display.flip()
    while True:
        screen.blit(road, (0, 0))

        output = nets[0].activate(car.get_data())
        i = output.index(max(output))

        if i == 0:
            car.angle += 5
        elif i == 1:
            car.angle = car.angle
        elif i == 2:
            car.angle -= 5

        if car.is_alive:
            # genomes[i][1].fitness += car.get_reward()
            car.update(road)
            # car.draw_radars(screen)
            car.draw(screen)

        pygame.display.flip()


def save_checkpoint(filename_prefix, config, population, species_set, generation):
    """ Save the current simulation state. """
    filename = '{0}{1}'.format(filename_prefix, generation)
    print("Saving checkpoint to {0}".format(filename))
    with gzip.open(filename, 'w', compresslevel=5) as f:
        data = (generation, config, population, species_set, random.getstate())
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def restore_checkpoint(filename):
    """Resumes the simulation from a previous saved point."""
    with gzip.open(filename) as f:
        generation, config, population, species_set, rndstate = pickle.load(f)
        random.setstate(rndstate)
        return neat.Population(config, (population, species_set, generation))


def main(checkpoint_path=""):
    global population
    config_path = "my_config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    if checkpoint_path == "":
        population = neat.Population(config)
    else:
        population = restore_checkpoint(checkpoint_path)

    population.run(run_generation, 30)
    save_checkpoint("best_gen_", config, population.population, population.species, population.generation)


if __name__ == "__main__":
    main("best_gen_8")
    # main()