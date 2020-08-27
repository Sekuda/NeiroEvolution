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


def turn_car(event):
    global ANGLE, image_tk
    ANGLE += 10
    ANGLE %= 360

    image_tmp = def_image.rotate(ANGLE, expand=True)
    image_tk = ImageTk.PhotoImage(image_tmp)
    # w.create_image(250, 250, image=image_tk)
    w.itemconfig(img, image=image_tk)
    compute_collision_points()


def turn_car_left(event):
    global ANGLE, image_tk, img
    ANGLE -= 10
    ANGLE %= 360

    image_tmp = def_image.rotate(ANGLE, expand=True)
    image_tk = ImageTk.PhotoImage(image_tmp)
    # w.create_image(250, 250, image=image_tk)
    w.itemconfig(img, image=image_tk)
    compute_collision_points()


w.bind('<Button-1>', turn_car)
w.bind('<Button-3>', turn_car_left)


def draw_point(x, y):
    radius = 5
    point = w.create_oval(x - radius, y - radius, x + radius, y + radius, fill="green")
    return point


def turn_point_by_angle(angle, center_x, center_y, x, y):
    '''
    функция рассчитывает новое положение точки относительно центра и угла поворота
    :param angle: угол поворота
    :param center_x: центр по Х
    :param center_y: центр по У
    :param x: текущая х
    :param y: текущая у
    :return:
    '''
    new_x = (x - center_x) * math.sin(angle * math.pi / 180) - (
            (y - center_y) * math.cos(angle * math.pi / 180)) + center_x

    new_y = (x - center_x) * math.cos(angle * math.pi / 180) + (
            (y - center_y) * math.sin(angle * math.pi / 180)) + center_y

    return new_x, new_y


def turn_rectangle_by_angle(angle, center: (), width: int, height: int):
    '''
    Поворачивает прямоугольник на "angle" относительно заданного центра
    :param angle: угол поворота
    :param center: центр поворота
    :param width: ширина прямоугольника
    :param height: высота прямоугольника
    :return: новые координаты вершин
    '''
    new_points_coord = []
    for i in ((center[0] - height / 2, center[1] - width / 2),
              (center[0] + height / 2, center[1] - width / 2),
              (center[0] + height / 2, center[1] + width / 2),
              (center[0] - height / 2, center[1] + width / 2)):

        centerx, centery = center[0], center[1]
        x, y = i[0], i[1]
        new_points_coord.append(turn_point_by_angle(angle, centerx, centery, x, y))

    return new_points_coord


def compute_collision_points():
    w.delete(*collision_points)
    coord = w.coords(img)
    car_height = 80
    car_width = 180

    for i in ((coord[0] - car_height / 2, coord[1] - car_width / 2),
              (coord[0] + car_height / 2, coord[1] - car_width / 2),
              (coord[0] + car_height / 2, coord[1] + car_width / 2),
              (coord[0] - car_height / 2, coord[1] + car_width / 2)):

        centerx = coord[0]
        centery = coord[1]
        x = i[0]
        y = i[1]

        collision_points.append(draw_point(*turn_point_by_angle(ANGLE, centerx, centery, x, y)))

if __name__ == "__main__":

    compute_collision_points()

    mainloop()
