from io import BytesIO
import shutil
import math
import os
import requests
import pygame
from PIL import Image, UnidentifiedImageError

SIZE = (512, 256)
FPS = 60
BLACK = (0, 0, 0)
APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def find_full_address_by_name(name):
    try:
        params = {
            "geocode": "+".join(name.split(" ")),
            "apikey": APIKEY,
            "results": "1",
            "format": "json",
        }
        response = requests.get(
            "http://geocode-maps.yandex.ru/1.x/", params=params)
        s = (response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                            ["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"])
        try:
            postal_code = (response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                           ["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"])
        except Exception:
            postal_code = 'нет'
        return s, 'Почтовый индекс: ' + postal_code
    except Exception:
        return "Упс, что-то пошло не так"


def check_org_coords(coords):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        search_params = {
            "apikey": api_key,
            'lang': 'ru_RU',
            "text": find_full_address_by_coords(coords)[0],
            "type": "biz"
        }
        response = requests.get(search_api_server, params=search_params)
        json_response = response.json()
        point = json_response["features"][0]["geometry"]["coordinates"]
        name = json_response["features"][0]["properties"]["CompanyMetaData"]["name"]
        address = json_response["features"][0]["properties"]["CompanyMetaData"]["address"]
        if lonlat_distance(coords, point) <= 50:
            return address + ' ' + name
    except Exception:
        return False
    return False


def find_full_address_by_coords(coordinates):
    try:
        params = {
            "geocode": ','.join([str(i) for i in coordinates]),
            "apikey": APIKEY,
            "results": "1",
            "format": "json",
        }
        response = requests.get("http://geocode-maps.yandex.ru/1.x/",
                                params=params)
        s = (response.json()["response"]["GeoObjectCollection"]["featureMember"][0]
             ["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"])
        try:
            postal_code = (response.json()["response"]["GeoObjectCollection"]["featureMember"][0]
                           ["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"])
        except Exception:
            postal_code = 'нет'
        return s, 'Почтовый индекс: ' + postal_code
    except Exception:
        return "Упс, что-то пошло не так"


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def find_coordinates_by_name(name):
    try:
        params = {
            "apikey": APIKEY,
            "geocode": "+".join(name.split(" ")),
            "results": "1",
            "format": "json",
        }
        response = requests.get(
            "http://geocode-maps.yandex.ru/1.x/", params=params)
        s = ",".join((response.json()["response"]["GeoObjectCollection"]
                                     ["featureMember"][0]["GeoObject"]["Point"]["pos"]).split())
        return s, 1
    except IndexError:
        return "71.430411,51.128207", 0


class Map:

    def __init__(self, coordinates, zoom):
        self.coordinates = coordinates
        self.map_type = "map"
        self.zoom = zoom
        self.text = ""
        self.metka = ""
        self.full_address = ""
        self.postal_code = ""
        self.postal_code_view = True
        self.image = self.get_map(firstly=True)
        self.zoom_borders = (0, 17)
        self.longitude_borders = (-180, 180)
        self.latitude_borders = (-90, 90)

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

    def show(self, surf, color):
        surf.blit(self.image, (0, 0))

        font = pygame.font.Font(None, 24)

        txt_surface = font.render("Сброс метки", True, pygame.Color("black"))
        reset_box.w = txt_surface.get_width() + 10
        pygame.draw.rect(surf, (200, 200, 200), reset_box)
        surf.blit(txt_surface, (reset_box.x + 5, reset_box.y + 6))

        color_address = "white" if self.full_address == "" else "black"
        txt_surface = font.render(
            self.full_address, True, pygame.Color("black"))
        output_box.w = max(200, txt_surface.get_width() + 10)
        pygame.draw.rect(surf, color_address, output_box, 3)
        surf.blit(txt_surface, (output_box.x + 5, output_box.y + 6))

        text = self.postal_code if self.postal_code_view else ""
        txt_surface = font.render(text, True, pygame.Color("black"))
        postal_code_box.w = max(200, txt_surface.get_width() + 10)
        pygame.draw.rect(surf, (200, 200, 200), postal_code_box, 3)
        surf.blit(txt_surface, (postal_code_box.x + 5, postal_code_box.y + 6))

        txt_surface = font.render(self.text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        surf.blit(txt_surface, (input_box.x + 5, input_box.y + 7))
        pygame.draw.rect(surf, color, input_box, 2)

    def find_by_coordinates(self, mouse_pos):
        if 0 <= mouse_pos[0] <= SIZE[0]:
            if 0 <= mouse_pos[1] <= SIZE[1]:
                shift = (mouse_pos[0] - SIZE[0] // 2,
                         SIZE[1] // 2 - mouse_pos[1])
                step = [(360 / (2 ** self.zoom)) / 256 * shift[0],
                        (180 / (2 ** self.zoom)) / 256 * shift[1]]
                coordinates = self.coordinates[:]
                coordinates[0] += step[0]
                coordinates[1] += step[1]
                self.to_adres_by_coords(coordinates)

    def find_org(self, mouse_pos):
        if 0 <= mouse_pos[0] <= SIZE[0]:
            if 0 <= mouse_pos[1] <= SIZE[1]:
                shift = (mouse_pos[0] - SIZE[0] // 2,
                         SIZE[1] // 2 - mouse_pos[1])
                step = [(360 / (2 ** self.zoom)) / 256 * shift[0],
                        (180 / (2 ** self.zoom)) / 256 * shift[1]]
                coordinates = self.coordinates[:]
                coordinates[0] += step[0]
                coordinates[1] += step[1]
                self.to_adres_org_by_coords(coordinates)

    def change_zoom(self, step):
        if self.zoom_borders[0] <= self.zoom + step <= self.zoom_borders[1]:
            self.zoom += step
            self.image = self.get_map()

    def reset(self):
        self.text = ""
        self.metka = ""
        self.full_address = ""
        self.postal_code = ""
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

    def change_postal_code_view(self):
        self.postal_code_view = not self.postal_code_view

    def to_adres(self):
        coordinates = find_coordinates_by_name(self.text)
        self.full_address, self.postal_code = (
            "Упс! Что-то пошло не так", "") if not coordinates[1] else find_full_address_by_name(self.text)
        self.metka = coordinates[0] + ",pm2rdl"
        self.coordinates = [float(coord)
                            for coord in coordinates[0].split(",")]
        self.image = self.get_map()

    def to_adres_by_coords(self, coords):
        self.text = ''
        self.full_address, self.postal_code = find_full_address_by_coords(
            coords)
        self.metka = ','.join([str(i) for i in coords]) + ",pm2rdl"
        self.image = self.get_map()

    def to_adres_org_by_coords(self, coords):
        self.text = ''
        t = check_org_coords(coords)
        if t:
            self.full_address, self.postal_code = find_full_address_by_coords(
                coords)
            self.full_address = t
            self.metka = ','.join([str(i) for i in coords]) + ",pm2rdl"
            self.image = self.get_map()
        else:
            self.reset()


if __name__ == '__main__':
    try:
        os.mkdir('temp/')
    except:
        pass
    print('Переключение слоёв карты осуществляется цифрами')
    print('Чтобы перейти по адресу, нажмите Enter')
    print('Отображение/скрытие почтового индекса - i')
    pygame.init()
    screen = pygame.display.set_mode([SIZE[0], SIZE[1] + 105])
    pygame.display.set_caption('Map')
    clock = pygame.time.Clock()
    active = False
    running = True
    color_inactive = pygame.Color((90, 90, 90))
    color_active = pygame.Color("black")
    input_color = color_inactive
    input_box = pygame.Rect(25, 265, 140, 26)
    reset_box = pygame.Rect(25, 300, 70, 26)
    output_box = pygame.Rect(25, 335, 140, 23)
    postal_code_box = pygame.Rect(150, 300, 200, 23)
    operator = Map([34.11, 66.56], 5)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_BACKSPACE:
                        operator.text = operator.text[:-1]
                    elif event.key == pygame.K_RETURN:
                        operator.to_adres()
                        operator.text = ''
                    else:
                        operator.text += event.unicode
                else:
                    if event.key == pygame.K_i:
                        operator.change_postal_code_view()
                    else:
                        operator.key_down(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    operator.find_by_coordinates(event.pos)
                elif event.button == pygame.BUTTON_RIGHT:
                    operator.find_org(event.pos)
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
