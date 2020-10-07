import tkinter as tk
import random

WIDTH = 300
HEIGHT = 300
INITIAL_SPEED = 0.5
MAX_INFECTED_AREA_RADIUS = 30
PERSON_CNT = 20
TEST_SECTOR = (50, 50, 180, 180)


class Person:
    def __init__(self, area, canvas, radius=3):
        self.x_speed = random.uniform(-0.5, 0.5)
        self.y_speed = random.uniform(-0.5, 0.5)
        self.radius = radius
        self.area = area
        self.oval_bounds = (0, 0, 0, 0)
        self.left, self.top, self.right, self.bot = (0, 0, 0, 0)
        self.person_oval = None
        self.radar_oval = None
        self.start_color = tuple((255, 0, 0))
        self.end_color = tuple((0, 0, 0))
        self.init_position()
        self.update_position(self.oval_bounds)
        self.infected = True#bool(random.randint(0, 1))
        self.chaotic_movement = False#bool(random.randint(0, 1))
        self.infected_area = self.radius
        self.draw(canvas)

    def init_position(self):
        """left - top - right - bot"""
        self.oval_bounds = (self.area[0] + (self.area[2] - self.area[0]) / 2 - self.radius,
                            self.area[1] + (self.area[3] - self.area[1]) / 2 - self.radius,
                            self.area[0] + (self.area[2] - self.area[0]) / 2 + self.radius,
                            self.area[1] + (self.area[3] - self.area[1]) / 2 + self.radius)

    def update_position(self, oval_bounds):
        self.oval_bounds = oval_bounds
        self.left = self.oval_bounds[0]
        self.top = self.oval_bounds[1]
        self.right = self.oval_bounds[2]
        self.bot = self.oval_bounds[3]

    def interpolate(self):
        # 'color_a' and 'color_b' are RGB tuples
        # 't' is a value between 0.0 and 1.0
        # this is a naive interpolation
        return tuple(int(a + (b - a) * (self.infected_area / MAX_INFECTED_AREA_RADIUS)) for a, b in zip(self.start_color, self.end_color))

    def draw_infected_area(self, canvas):
        if self.infected:
            new_color = self.interpolate()
            canvas.delete(self.radar_oval)

            self.radar_oval = canvas.create_oval(self.left-self.infected_area,
                                                    self.top-self.infected_area,
                                                    self.right+self.infected_area,
                                                    self.bot+self.infected_area,
                                                    fill="", outline='#%02x%02x%02x' % new_color, width=2)
            if self.infected_area < MAX_INFECTED_AREA_RADIUS:
                self.infected_area += 1
            else:
                self.infected_area = self.radius

    def draw(self, canvas):
        if self.infected:
            self.person_oval = canvas.create_oval(self.oval_bounds, fill="red")
        else:
            self.person_oval = canvas.create_oval(self.oval_bounds, fill="white")

    def bounce(self, action):
        # отскок с ускорением
        if self.chaotic_movement:
            rnd = random.uniform(-0.5, 0.5)
        else:
            rnd = random.random()-0.5
        if action == "bounce_x":
            self.y_speed = rnd if self.y_speed > 0 else - rnd
            # if abs(self.x_speed) < infected_MAX_SPEED:
            #     self.x_speed *= -infected_SPEED_UP
            # else:
            self.x_speed = -self.x_speed
        elif action == "bounce_y":
            self.x_speed = rnd if self.x_speed > 0 else - rnd
            self.y_speed = -self.y_speed
        elif action == "speed_up_y":
            if self.chaotic_movement:
                self.y_speed = rnd if self.y_speed > 0 else - rnd
            pass
        elif action == "speed_up_x":
            if self.chaotic_movement:
                self.x_speed = rnd if self.x_speed > 0 else - rnd
            pass

    def move(self, canvas, person_list):
        y_speed_tmp = self.y_speed if self.top != self.area[1] and self.bot != self.area[3] else 0
        # горизонтальный отскок
        # Если мы далеко от вертикальных линий
        if self.right + self.x_speed < self.area[2] and self.left + self.x_speed > self.area[0]:
            if check_horizontal_collisions(self, person_list):
                self.bounce("bounce_x")
            else:
                # просто двигаем Person
                canvas.move(self.person_oval, self.x_speed, y_speed_tmp)
                self.bounce("speed_up_x")
                self.update_position(c.coords(self.person_oval))

        # Если Person касается своей правой или левой стороной границы поля
        elif self.right == self.area[2] or self.left == self.area[0]:
            self.bounce("bounce_x")

        # Проверка ситуации, в которой Person может вылететь за границы сектора.
        # В таком случае просто двигаем его к границе поля.
        else:
            if self.right > self.area[0] + (self.area[2] - self.area[0]) / 2:
                canvas.move(self.person_oval, self.area[2] - self.right, y_speed_tmp)
            else:
                canvas.move(self.person_oval, -self.left + self.area[0], y_speed_tmp)
            self.update_position(c.coords(self.person_oval))

        x_speed_tmp = self.x_speed if self.left != self.area[0] and self.right != self.area[2] else 0
        # вертикальный отскок
        # Если мы далеко от вертикальных линий
        if self.top + self.y_speed > self.area[1] and self.bot + self.y_speed < self.area[3]:
            if check_vertical_collisions(self, person_list):
                self.bounce("bounce_y")
            else:
                # просто двигаем Person
                canvas.move(self.person_oval, x_speed_tmp, self.y_speed)
                self.bounce("speed_up_y")
                self.update_position(c.coords(self.person_oval))
        # Если Person касается своей верхней или нижней стороной границы поля
        elif self.top == self.area[1] or self.bot == self.area[3]:
            self.bounce("bounce_y")
        # Проверка ситуации, в которой Person может вылететь за границы сектора.
        # В таком случае просто двигаем его к границе поля.
        else:
            if self.top < self.area[1] + (self.area[3] - self.area[1]) / 2:
                canvas.move(self.person_oval, x_speed_tmp, self.area[1] - self.top)
            else:
                canvas.move(self.person_oval, x_speed_tmp, self.area[3] - self.bot)
            self.update_position(c.coords(self.person_oval))

        self.draw_infected_area(canvas)


def draw_sector(sector: ()):
    c.create_line(sector[0], sector[1], sector[2], sector[1], fill="white")
    c.create_line(sector[0], sector[3], sector[2], sector[3], fill="white")
    c.create_line(sector[0], sector[1], sector[0], sector[3], fill="white")
    c.create_line(sector[2], sector[1], sector[2], sector[3], fill="white")


def check_horizontal_collisions(person, _person_list):
    """
        1 проверка столкновения центра
        2 проверка попадания в область видимости (infected_area)
        3 Проверка попадания в область заражения (MAX_INFECTED_AREA_RADIUS)
    """

    if person.x_speed >= 0:
        next_position_x = person.right + person.x_speed

    else:
        next_position_x = person.left + person.x_speed
    next_position_y = person.top + person.radius

    for _p in _person_list:
        if person is _p:
            continue
        if _p.left < next_position_x < _p.right and _p.top < next_position_y < _p.bot:
            return True

    return False


def check_vertical_collisions(person, _person_list):
    """
        1 проверка столкновения центра
        2 проверка попадания в область видимости (infected_area)
        3 Проверка попадания в область заражения (MAX_INFECTED_AREA_RADIUS)
    """

    if person.y_speed >= 0:
        next_position_y = person.bot + person.y_speed
    else:
        next_position_y = person.top + person.y_speed
    next_position_x = person.left + person.radius

    for _p in _person_list:
        if person is _p:
            continue
        if _p.left < next_position_x < _p.right and _p.top < next_position_y < _p.bot:
            return True

    return False


def main():
    for i in person_list:
        i.move(c, person_list)
    # вызываем саму себя каждые 30 миллисекунд
    root.after(30, main)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Epidemic model simulation")

    c = tk.Canvas(root, width=WIDTH, height=HEIGHT, background="#000000")
    c.pack()

    sector = TEST_SECTOR
    draw_sector(sector)

    person_list = [Person(sector, c) for i in range(PERSON_CNT)]

    main()
    root.mainloop()



