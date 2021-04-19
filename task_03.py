from io import BytesIO
from PIL import Image, UnidentifiedImageError
import requests
import pygame
import shutil
import os

SIZE = (600, 450)
FPS = 60


class Map:

    def __init__(self, coordinates, zoom):
        self.coordinates = coordinates
        self.zoom = zoom
        self.image = self.get_map(firstly=True)
        self.zoom_borders = (0, 15)
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
                "l": "map",
                "size": ','.join([str(i) for i in SIZE]),
                "ll": ','.join([str(i) for i in self.coordinates]),
                "z": self.zoom,
            }
            response = requests.get("http://static-maps.yandex.ru/1.x/",
                                    params=map_params)
            Image.open(BytesIO(response.content)).save('temp/' + 'temp.png')
            return pygame.image.load('temp/' + 'temp.png')
        except UnidentifiedImageError:
            return self.image if not firstly else None

    def show(self, surf):
        surf.blit(self.image, (0, 0))

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
        step = [step[0] * (512 / (2 ** self.zoom)) * SIZE[0] / 1024,
                step[1] * (512 / (2 ** self.zoom)) * SIZE[1] / 1024]
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


if __name__ == '__main__':
    try:
        os.mkdir('temp/')
    except FileExistsError:
        pass

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    running = True

    operator = Map([50, 50], 5)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                operator.key_down(event.key)
        operator.show(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    shutil.rmtree('temp/', ignore_errors=True)
