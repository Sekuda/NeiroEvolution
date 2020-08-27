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
RADAR_COUNT = 10


def turn_car(event):
    global ANGLE, image_tk
    ANGLE -= 10
    ANGLE %= 360

    image_tmp = def_image.rotate(-ANGLE)
    image_tk = ImageTk.PhotoImage(image_tmp)
    # w.create_image(250, 250, image=image_tk)
    w.itemconfig(img, image=image_tk)
    compute_collision_points()
    compute_radar()


def turn_car_left(event):
    global ANGLE, image_tk, img
    ANGLE += 10
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
    return rotate_point(x, y, center_x, center_y, angle)


def rotate_point(x, y, centerx, centery, degrees):
    newx = (x - centerx) * math.cos(degrees * math.pi / 180) - (y - centery) * math.sin(degrees * math.pi / 180) + centerx;
    newy = (x - centerx) * math.sin(degrees * math.pi / 180) + (y - centery) * math.cos(degrees * math.pi / 180) + centery;
    return [newx, newy]


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
        point_position = turn_point_by_angle(ANGLE, centerx, centery, x, y)
        collision_points.append(draw_point(*point_position))



def compute_radar():
    w.delete(*radars)
    w.delete(*radars_line)

    radars.clear()
    coord = w.coords(img)
    #
    step = 180/(RADAR_COUNT-1)
    x = coord[0]
    y = coord[1] - car_width
    for i in range(RADAR_COUNT):
        angle_ = ANGLE + step*(i)
        radar_position = rotate_point(x, y, coord[0], coord[1], angle_)

        radar = draw_point(*radar_position, fill_="yellow")
        radars.append(radar)

        line = w.create_line(*coord, *radar_position)
        radars_line.append(line)



if __name__ == "__main__":

    compute_radar()
    compute_collision_points()

    mainloop()
