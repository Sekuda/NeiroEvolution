# https://neat-python.readthedocs.io/en/latest/
import random
import pygame
import math
import sys


width = 650
height = 550


class Car:
    car_sprites = ("Audi", "Black_viper", "Orange", "Police", "Taxi")

    def __init__(self):
        self.random_sprite()

        self.angle = 0
        self.speed = 5

        self.radars = []
        self.collision_points = []

        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0

    def random_sprite(self):
        self.car_sprite = pygame.image.load('sprites/' + random.choice(self.car_sprites) + '.png')
        self.car_sprite = pygame.transform.scale(self.car_sprite,
                                                 (math.floor(self.car_sprite.get_size()[0] / 4),
                                                  math.floor(self.car_sprite.get_size()[1] / 4)))
        self.car = self.car_sprite

        self.pos = [256, 469]
        self.compile_center()

    def compile_center(self):
        self.center = (self.pos[0] + (self.car.get_size()[0] / 2), self.pos[1] + (self.car.get_size()[1] / 2))

    def draw(self, screen):
        screen.blit(self.car, self.pos)

    def update(self, road):
        self.speed = 5

        # self.rotate(self.angle)



def run_generation():
    car_cnt = 30
    cars = []

    for i in range(car_cnt):
        cars.append(Car())

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    road = pygame.image.load('sprites/road.png')
    road = pygame.transform.scale(road, (math.floor(road.get_size()[0]/2),
                                         math.floor(road.get_size()[1]/2)))

    pygame.display.flip()
    while True:
        screen.blit(road, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True

        screen.blit(road, (0, 0))

        for car in cars:
            car.draw(screen)
            car.update(road)

        pygame.display.flip()


if __name__ == "__main__":
    run_generation()

    # print(pygame.display.set_mode.__doc__)
