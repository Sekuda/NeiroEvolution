import math
from tkinter import *
from PIL import ImageTk, Image

ANGLE = 0

window = Tk()
window.geometry('500x500-0-0')
w = Canvas(window, width=500, height=500)
w.focus_set()
w.pack()

def_image = Image.open("Taxi.png")
def_image = def_image.resize((200, 200), Image.ANTIALIAS)
image = def_image.rotate(ANGLE, expand=True)
image_tk = ImageTk.PhotoImage(image)
img = w.create_image(250, 250, image=image_tk)
collision_points = []
radars = []
radars_line = []
car_height = 80
car_width = 180
RADAR_COUNT = 11


def turn_car(event):
    global ANGLE, image_tk
    ANGLE -= 5
    ANGLE %= 360

    image_tmp = def_image.rotate(-ANGLE)
    image_tk = ImageTk.PhotoImage(image_tmp)
    # w.create_image(250, 250, image=image_tk)
    w.itemconfig(img, image=image_tk)
    compute_collision_points()
    compute_radar()


def turn_car_left(event):
    global ANGLE, image_tk, img
    ANGLE += 5
    ANGLE %= 360

    image_tmp = def_image.rotate(-ANGLE)
    image_tk = ImageTk.PhotoImage(image_tmp)
    # w.create_image(250, 250, image=image_tk)
    w.itemconfig(img, image=image_tk)
    compute_collision_points()
    compute_radar()


w.bind('<Button-1>', turn_car)
w.bind('<Button-3>', turn_car_left)


def draw_point(x, y, fill_="green"):
    radius = 5
    point = w.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill_)
    return point

def turn_rectangle_by_angle(angle, center: (), width: int, height: int):
    '''
    Поворачивает прямоугольник на "angle" относительно заданного центра
    функция рассчитывает новое положение точки относительно центра и угла поворота
    :param angle: угол поворота
    :param center: центр поворота
    :param width: ширина прямоугольника
    :param height: высота прямоугольника
    :return: новые координаты вершин
    :param center_x: центр по Х
    :param center_y: центр по У
    :param x: текущая х
    :param y: текущая у
    :return:
    '''
    new_points_coord = []
    for i in ((center[0] - height / 2, center[1] - width / 2),
              (center[0] + height / 2, center[1] - width / 2),
              (center[0] + height / 2, center[1] + width / 2),
              (center[0] - height / 2, center[1] + width / 2)):

        centerx, centery = center[0], center[1]
        x, y = i[0], i[1]
        new_points_coord.append(rotate_point(x, y, centerx, centery, angle))

    return new_points_coord


def rotate_point(x, y, centerx, centery, degrees):
    # newx = (x - centerx) * math.cos(degrees * math.pi / 180) - (y - centery) * math.sin(degrees * math.pi / 180) + centerx;
    # newy = (x - centerx) * math.sin(degrees * math.pi / 180) + (y - centery) * math.cos(degrees * math.pi / 180) + centery;
    newx = (x - centerx) * math.cos(math.radians(degrees)) - (y - centery) * math.sin(math.radians(degrees)) + centerx
    newy = (x - centerx) * math.sin(math.radians(degrees)) + (y - centery) * math.cos(math.radians(degrees)) + centery

    return [newx, newy]


def offset_point(centerX, centerY, offset, angle):
    # x = centerX + cos(radians(360 - (angle + degree))) * length
    # y = centerY + sin(radians(360 - (angle + degree))) * length
    #
    # offsetX = deltaX * cos(90 - Angle) - deltaY * sin(90 - Angle)
    # offsetY = deltaX * sin(90 - Angle) + deltaY * cos(90 - Angle)
    #
    # newX = (X2 - X) * cos(90 - Angle) - (Y2 - Y) * sin(90 - Angle) + X;
    # newY = (X2 - X) * sin(90 - Angle) + (Y2 - Y) * cos(90 - Angle) + Y;
    # moveX = X3 - newX;
    # moveY = Y3 - newY;

    x = centerX + math.cos(math.radians(180 + angle)) * offset
    y = centerY + math.sin(math.radians(180 + angle)) * offset
    return [x, y]


def compute_collision_points():
    w.delete(*collision_points)
    coord = w.coords(img)

    for i in ((coord[0] - car_width / 2, coord[1] - car_height / 2),
              (coord[0] + car_width / 2, coord[1] - car_height / 2),
              (coord[0] + car_width / 2, coord[1] + car_height / 2),
              (coord[0] - car_width / 2, coord[1] + car_height / 2)):
        centerx = coord[0]
        centery = coord[1]
        x = i[0]
        y = i[1]
        point_position = rotate_point(x, y, centerx, centery, ANGLE)
        collision_points.append(draw_point(*point_position))


# def compile_radar_lenn():
#     length = 0
#     x = int(self.center[0] + math.cos(math.radians(360 - (ANGLE + degree))) * length)
#     y = int(self.center[1] + math.sin(math.radians(360 - (ANGLE + degree))) * length)


def compute_radar():
    w.delete(*radars)
    w.delete(*radars_line)

    radars.clear()
    coord = w.coords(img)
    #
    step = 270 / (RADAR_COUNT - 1)
    x = coord[0]
    y = coord[1] - car_width
    for i in range(RADAR_COUNT):
        angle_ = ANGLE + step * i + 45
        # radar_position = rotate_point(x, y, coord[0], coord[1], angle_)
        for i in range(600):
            radar_position = offset_point(coord[0], coord[1], i, angle_)
            if (radar_position[0] >= 500 or radar_position[1] >= 500
                    or radar_position[0] <= 0 or radar_position[1] <= 0):
                break

        radar = draw_point(*radar_position, fill_="yellow")
        radars.append(radar)

        line = w.create_line(*coord, *radar_position)
        radars_line.append(line)


if __name__ == "__main__":
    compute_radar()
    compute_collision_points()

    mainloop()
