import tkinter as tk
import random

WIDTH = 300
HEIGHT = 300
TEST_SECTOR = (0, 0, 150, 150)
INITIAL_SPEED = 0.5
MAX_INFECTED_AREA_RADIUS = 10
PERSON_RADIUS = 3

PERSON_CNT = 20
INFECTED_CNT = 4

ZERO_X_SPEED = 0
ZERO_Y_SPEED = 0
SPAWN_IN_CENTER = 0
REPRODUCTION = 1


class Person:
    def __init__(self, area, infected=False):
        self.x_speed = round(0 if ZERO_X_SPEED else random.uniform(-INITIAL_SPEED, INITIAL_SPEED), 2)
        self.y_speed = round(0 if ZERO_Y_SPEED else random.uniform(-INITIAL_SPEED, INITIAL_SPEED), 2)
        self.radius = PERSON_RADIUS
        self.current_infected_area = PERSON_RADIUS
        self.infected = infected  # bool(random.randint(0, 1))
        self.chaotic_movement = False  # bool(random.randint(0, 1))
        self.live_power = 150
        self.reproduction_power = random.randint(0, 100)

        self.area = area
        self.oval_bounds = [0, 0, 0, 0]
        self.spawn_in_center = SPAWN_IN_CENTER
        self.init_start_position()
        self.left = self.oval_bounds[0]
        self.top = self.oval_bounds[1]
        self.right = self.oval_bounds[2]
        self.bot = self.oval_bounds[3]

        self.start_color = tuple((255, 0, 0))
        self.end_color = tuple((0, 0, 0))
        self.oval_id = None
        self.radar_id = None

    def init_start_position(self):
        """left - top - right - bot"""
        if self.spawn_in_center:
            self.oval_bounds = [self.area[0] + (self.area[2] - self.area[0]) / 2 - self.radius,
                                self.area[1] + (self.area[3] - self.area[1]) / 2 - self.radius,
                                self.area[0] + (self.area[2] - self.area[0]) / 2 + self.radius,
                                self.area[1] + (self.area[3] - self.area[1]) / 2 + self.radius]
        else:
            x = random.randint(self.area[0], self.area[2])
            y = random.randint(self.area[1], self.area[3])
            self.oval_bounds = [x - self.radius,
                                y - self.radius,
                                x + self.radius,
                                y + self.radius]

    def calculate_new_position(self, x, y):
        z = [round(self.oval_bounds[0] + x, 2),
             round(self.oval_bounds[1] + y, 2),
             round(self.oval_bounds[2] + x, 2),
             round(self.oval_bounds[3] + y, 2)]
        self.update_border_points(z)

    def update_border_points(self, oval_bounds):
        self.oval_bounds = oval_bounds
        self.left = self.oval_bounds[0]
        self.top = self.oval_bounds[1]
        self.right = self.oval_bounds[2]
        self.bot = self.oval_bounds[3]

    def interpolate(self):
        # 'color_a' and 'color_b' are RGB tuples
        # 't' is a value between 0.0 and 1.0
        # this is a naive interpolation
        return tuple(int(a + (b - a) * (self.current_infected_area / MAX_INFECTED_AREA_RADIUS)) for a, b in
                     zip(self.start_color, self.end_color))

    def calculate_infected_area(self):
        if self.infected:
            if self.current_infected_area < MAX_INFECTED_AREA_RADIUS:
                self.current_infected_area += 1
            else:
                self.current_infected_area = self.radius

    def bounce(self, action):
        # отскок с ускорением
        if self.chaotic_movement:
            rnd = round(random.uniform(-INITIAL_SPEED, INITIAL_SPEED), 2)
        else:
            rnd = round(random.uniform(0, INITIAL_SPEED), 2)
        if action == "bounce_x":
            self.y_speed = 0 if ZERO_Y_SPEED else rnd if self.y_speed > 0 else - rnd
            # if abs(self.x_speed) < infected_MAX_SPEED:
            #     self.x_speed *= -infected_SPEED_UP
            # else:
            self.x_speed = 0 if ZERO_X_SPEED else -self.x_speed
        elif action == "bounce_y":
            self.x_speed = 0 if ZERO_X_SPEED else rnd if self.x_speed > 0 else - rnd
            self.y_speed = 0 if ZERO_Y_SPEED else -self.y_speed
        elif action == "speed_up_y":
            if self.chaotic_movement:
                self.y_speed = 0 if ZERO_Y_SPEED else rnd if self.y_speed > 0 else - rnd
        elif action == "speed_up_x":
            if self.chaotic_movement:
                self.x_speed = 0 if ZERO_X_SPEED else rnd if self.x_speed > 0 else - rnd

    def move(self, _person_list):
        if self.live_power > 0:
            # горизонтальный отскок
            self.horizontal_move(_person_list)
            # вертикальный отскок
            self.vertical_move(_person_list)
            self.calculate_infected_area()

    def vertical_move(self, _person_list):
        x_speed_tmp = 0  # self.x_speed if self.left != self.area[0] and self.right != self.area[2] else 0
        # Если мы далеко от вертикальных линий
        if self.top + self.y_speed > self.area[1] and self.bot + self.y_speed < self.area[3]:
            if self.check_vertical_collisions(_person_list):
                self.bounce("bounce_y")
            else:
                # просто двигаем Person
                self.calculate_new_position(x_speed_tmp, self.y_speed)
                self.bounce("speed_up_y")
        # Если Person касается своей верхней или нижней стороной границы поля
        elif self.top == self.area[1] or self.bot == self.area[3]:
            self.bounce("bounce_y")
        # Проверка ситуации, в которой Person может вылететь за границы сектора.
        # В таком случае просто двигаем его к границе поля.
        else:
            if self.top < self.area[1] + (self.area[3] - self.area[1]) / 2:
                self.y_speed = self.area[1] - self.top
            else:
                self.y_speed = self.area[3] - self.bot
            self.calculate_new_position(x_speed_tmp, self.y_speed)

    def horizontal_move(self, _person_list):
        y_speed_tmp = 0  # self.y_speed if self.top != self.area[1] and self.bot != self.area[3] else 0
        # Если мы далеко от вертикальных линий
        if self.left + self.x_speed > self.area[0] and self.right + self.x_speed < self.area[2]:
            if self.check_horizontal_collisions(_person_list):
                self.bounce("bounce_x")
            else:
                # просто двигаем Person
                self.calculate_new_position(self.x_speed, y_speed_tmp)
                self.bounce("speed_up_x")
        # Если Person касается своей правой или левой стороной границы поля
        elif self.right == self.area[2] or self.left == self.area[0]:
            self.bounce("bounce_x")
        # Проверка ситуации, в которой Person может вылететь за границы сектора.
        # В таком случае просто двигаем его к границе поля.
        else:
            if self.right > self.area[0] + (self.area[2] - self.area[0]) / 2:
                self.x_speed = self.area[2] - self.right
                # self.update_position([self.area[2]-self.radius*2, self.top, self.area[2], self.bot])
            else:
                self.x_speed = -self.left + self.area[0]
                # self.update_position([self.area[0], self.top, self.area[0]+self.radius*2, self.bot])
            self.calculate_new_position(self.x_speed, y_speed_tmp)

    def check_horizontal_collisions(self, _person_list):
        if self.x_speed >= 0:
            next_position_x = self.right + self.x_speed
        else:
            next_position_x = self.left + self.x_speed

        next_position_y = self.top + self.radius

        for _p in _person_list:
            if self is _p or _p.live_power == 0:
                continue
            if _p.left <= next_position_x <= _p.right and _p.top <= next_position_y <= _p.bot:
                contact_reaction(self, _p)
                return True

        return False

    def check_vertical_collisions(self, _person_list):
        if self.y_speed >= 0:
            next_position_y = self.bot + self.y_speed
        else:
            next_position_y = self.top + self.y_speed

        next_position_x = self.left + self.radius

        for _p in _person_list:
            if self is _p or _p.live_power == 0:
                continue
            if _p.left <= next_position_x <= _p.right and _p.top <= next_position_y <= _p.bot:
                contact_reaction(self, _p)
                return True

        return False


def contact_reaction(catcher, target):
    if target.infected:
        catcher.infected = True  # взаимное инфицирование
        target.live_power += catcher.reproduction_power
    if catcher.infected:
        target.infected = True  # взаимное инфицирование
        catcher.live_power += target.reproduction_power

    if REPRODUCTION and \
            not (target.infected and catcher.infected) \
            and target.reproduction_power == catcher.reproduction_power == 100:
        child = Person(TEST_SECTOR)
        child.update_border_points(catcher.oval_bounds)
        person_list.append(child)
        catcher.reproduction_power = target.reproduction_power = 0


def draw_sector(sector: ()):
    c.create_line(sector[0], sector[1], sector[2], sector[1], fill="white")
    c.create_line(sector[0], sector[3], sector[2], sector[3], fill="white")
    c.create_line(sector[0], sector[1], sector[0], sector[3], fill="white")
    c.create_line(sector[2], sector[1], sector[2], sector[3], fill="white")


def draw(person, canvas):
    # draw
    if person.oval_id is None:
        person.oval_id = canvas.create_oval(person.oval_bounds, fill="white")
    else:
        canvas.move(person.oval_id, person.x_speed, person.y_speed)
    # draw_infected_area
    if person.infected:
        new_radar_color = person.interpolate()
        canvas.delete(person.radar_id)
        person.radar_id = canvas.create_oval(person.left - person.current_infected_area,
                                             person.top - person.current_infected_area,
                                             person.right + person.current_infected_area,
                                             person.bot + person.current_infected_area,
                                             fill="", outline='#%02x%02x%02x' % new_radar_color, width=2)
        canvas.itemconfigure(person.oval_id, fill="red")

        # draw_non_active_point
        if person.live_power == 0:
            canvas.itemconfigure(person.oval_id, fill="gray")
            canvas.delete(person.radar_id)
    else:
        if person.reproduction_power == 100:
            canvas.itemconfigure(person.oval_id, fill="yellow")
        else:
            canvas.itemconfigure(person.oval_id, fill="white")

def tact_update(person):
    if person.infected and person.live_power > 0:
        person.live_power -= 1
    if not person.infected and person.reproduction_power < 100:
        person.reproduction_power += 1
    if person.live_power == 0:
        person.y_speed = person.x_speed = 0


def main():
    for i in person_list:
        draw(i, c)
        i.move(person_list)
        tact_update(i)
        # print(c.coords(i.oval_id))
        # print(i.oval_bounds)

    root.after(30, main)  # вызываем саму себя каждые 30 миллисекунд


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Epidemic model simulation")

    c = tk.Canvas(root, width=WIDTH, height=HEIGHT, background="#000000")
    c.pack()

    draw_sector(TEST_SECTOR)

    person_list = [Person(TEST_SECTOR) for i in range(PERSON_CNT)] + \
                  [Person(TEST_SECTOR, True) for i in range(INFECTED_CNT)]
    main()
    root.mainloop()
