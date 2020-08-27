# https://neat-python.readthedocs.io/en/latest/
import random
import pygame
import math
import sys
import os
from NeiroEvolution.CompileCollision import turn_rectangle_by_angle

width = 650
height = 550


class Car:
    car_sprites = ("Audi", "Black_viper", "Orange", "Police", "Taxi")

    def __init__(self):
        self.random_sprite()

        self.angle = 120
        self.speed = 5

        self.radars = []
        self.collision_points = []

        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0
        self.center = []

    def random_sprite(self):
        self.car_sprite = pygame.image.load(random.choice(self.car_sprites) + '.png')
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
        # повернем картинку на нужный угол
        self.rotate_sprite()

        # Определим ей новую позицию в зависимости от угла и скорости
        self.set_new_position()

        # update distance & time spent
        self.distance += self.speed
        self.time_spent += 1  # aka turns

        self.compute_collision_points()
        # self.check_collision(road)

    def set_new_position(self):
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.compile_center()

    def rotate_sprite(self):
        self.car = pygame.transform.rotate(self.car_sprite, self.angle)

    def compute_collision_points(self):
        self.collision_points = turn_rectangle_by_angle(self.angle, self.center, 50, 20)

    def draw_collision_points(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.center[0]), int(self.center[1])), 5)
        for p in self.collision_points:
            # if (road.get_at((int(p[0]), int(p[1]))) == bg):
            pygame.draw.circle(screen, (255, 0, 0), (int(p[0]), int(p[1])), 5)

        # else:
        #     pygame.draw.circle(screen, (15, 192, 252), (int(p[0]), int(p[1])), 5)


def run_generation():
    car_cnt = 1
    cars = []

    for i in range(car_cnt):
        cars.append(Car())

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    road = pygame.image.load('road.png')
    road = pygame.transform.scale(road, (math.floor(road.get_size()[0] / 2),
                                         math.floor(road.get_size()[1] / 2)))

    # pygame.display.flip()
    while True:
        screen.blit(road, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True

        for car in cars:
            car.draw(screen)
            car.update(road)
            car.draw_collision_points(screen)

        pygame.display.flip()


if __name__ == "__main__":
    run_generation()
