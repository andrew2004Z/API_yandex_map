from io import BytesIO
from PIL import Image, UnidentifiedImageError
import requests
import pygame
import shutil
import os
SIZE = (512, 256)
FPS = 60
BLACK = (0, 0, 0)
APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"

def find_coordinates_by_name(name):
    try:
        params = {
            "geocode": "+".join(name.split(" ")),
            "apikey": APIKEY,
            "results": "1",
            "format": "json",
        }
        response = requests.get("http://geocode-maps.yandex.ru/1.x/", params=params)
        s = ",".join((response.json()["response"]["GeoObjectCollection"]
                                     ["featureMember"][0]["GeoObject"]["Point"]["pos"]).split())
        return s, 1
    except IndexError:
        return "71.430411,51.128207", 0  # оп, пасхалочка


def find_full_address_by_name(name):
    try:
        params = {
            "geocode": "+".join(name.split(" ")),
            "apikey": APIKEY,
            "results": "1",
            "format": "json",
        }
        response = requests.get("http://geocode-maps.yandex.ru/1.x/", params=params)
        s = (response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                            ["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"])
        return s
    except Exception:
        return "Упс, что-то пошло не так"


class Map:

    def __init__(self, coordinates, zoom):
        self.coordinates = coordinates
        self.map_type = "map"
        self.zoom = zoom

        self.text = ""
        self.metka = ""
        self.full_address = ""

        self.image = self.get_map(firstly=True)

        self.zoom_borders = (0, 17)
        self.longitude_borders = (-180, 180)
        self.latitude_borders = (-90, 90)

    def set_params(self, coordinates, zoom):
        self.coordinates = coordinates
        self.zoom = zoom

    def get_params(self):
        return self.coordinates, self.zoom

    def get_map(self, firstly=False):
        try:
            map_params = {
                "l": self.map_type,
                "size": ','.join([str(i) for i in SIZE]),
                "ll": ','.join([str(i) for i in self.coordinates]),
                "z": self.zoom,
                "pt": self.metka
            }
            response = requests.get("http://static-maps.yandex.ru/1.x/",
                                    params=map_params)
            Image.open(BytesIO(response.content)).save('temp/' + 'temp.png')
            return pygame.image.load('temp/' + 'temp.png')
        except UnidentifiedImageError:
            return self.image if not firstly else None

    def show(self, surf, color):
        surf.blit(self.image, (0, 0))

        font = pygame.font.Font(None, 24)

        txt_surface = font.render("Сброс метки", True, pygame.Color("black"))
        reset_box.w = txt_surface.get_width() + 10
        pygame.draw.rect(surf, (200, 200, 200), reset_box)
        surf.blit(txt_surface, (reset_box.x + 5, reset_box.y + 6))

        color_address = "white" if self.full_address == "" else "black"
        txt_surface = font.render(self.full_address, True, pygame.Color("black"))
        output_box.w = max(200, txt_surface.get_width() + 10)
        pygame.draw.rect(surf, color_address, output_box, 3)
        surf.blit(txt_surface, (output_box.x + 5, output_box.y + 6))

        txt_surface = font.render(self.text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        surf.blit(txt_surface, (input_box.x + 5, input_box.y + 7))
        pygame.draw.rect(surf, color, input_box, 2)

    def key_down(self, key):
        functions = {
            self.change_zoom: {
                pygame.K_PAGEUP: 1,
                pygame.K_PAGEDOWN: -1,
            },
            self.change_coordinates: {
                pygame.K_UP: (0, 1),
                pygame.K_DOWN: (0, -1),
                pygame.K_LEFT: (-1, 0),
                pygame.K_RIGHT: (1, 0),
            },
            self.change_type: {
                pygame.K_1: 'map',
                pygame.K_2: 'sat',
                pygame.K_3: 'skl',
                pygame.K_4: 'sat,skl',
            },
        }
        for function in list(functions.keys()):
            if key in list(functions[function].keys()):
                function(functions[function][key])
                return

    def change_zoom(self, step):
        if self.zoom_borders[0] <= self.zoom + step <= self.zoom_borders[1]:
            self.zoom += step
            self.image = self.get_map()

    def change_coordinates(self, step):
        step = [step[0] * (360 / (2 ** self.zoom)) * SIZE[0] / 256,
                step[1] * (180 / (2 ** self.zoom)) * SIZE[1] / 256]
        if step[0]:
            if self.longitude_borders[0] <= self.coordinates[0] + step[0]:
                if self.coordinates[0] + step[0] <= self.longitude_borders[1]:
                    self.coordinates[0] += step[0]
                    self.image = self.get_map()
        elif step[1]:
            if self.latitude_borders[0] <= self.coordinates[1] + step[1]:
                if self.coordinates[1] + step[1] <= self.latitude_borders[1]:
                    self.coordinates[1] += step[1]
                    self.image = self.get_map()

    def change_type(self, new_type):
        if new_type != self.map_type:
            self.map_type = new_type
            self.image = self.get_map()

    def to_adres(self):
        coordinates = find_coordinates_by_name(self.text)
        self.full_address = "Упс! Что-то пошло не так" if not coordinates[1] else find_full_address_by_name(self.text)
        self.metka = coordinates[0] + ",pm2rdl"
        self.set_params([float(coor) for coor in coordinates[0].split(",")], 5)
        self.image = self.get_map()

    def reset(self):
        self.text = ""
        self.metka = ""
        self.full_address = ""
        self.image = self.get_map()


if __name__ == '__main__':
    try:
        os.mkdir('temp/')
    except FileExistsError:
        pass

    print('Переключение слоёв карты осуществляется цифрами')
    print('Чтобы перейти по адрессу, нажмите Enter')

    pygame.init()
    screen = pygame.display.set_mode([SIZE[0], SIZE[1] + 105])
    pygame.display.set_caption('Map')
    clock = pygame.time.Clock()
    running = True
    active = False
    color_inactive = pygame.Color((90, 90, 90))
    color_active = pygame.Color("black")
    input_color = color_inactive

    input_box = pygame.Rect(25, 265, 140, 26)
    reset_box = pygame.Rect(25, 300, 70, 26)
    output_box = pygame.Rect(25, 335, 140, 23)

    operator = Map([34.11, 66.56], 5)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        operator.to_adres()
                        operator.text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        operator.text = operator.text[:-1]
                    else:
                        operator.text += event.unicode
                else:
                    operator.key_down(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                if reset_box.collidepoint(event.pos):
                    operator.reset()
                input_color = color_active if active else color_inactive

        screen.fill("white")
        operator.show(screen, input_color)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    shutil.rmtree('temp/', ignore_errors=True)
