from io import BytesIO
from PIL import Image
import requests
import pygame
import shutil
import os
from config import *


class Map:

    def __init__(self, coordinates, zoom):
        self.coordinates = coordinates
        self.zoom = zoom
        self.image = self.get_map()
        self.borders = (0, 17)

    def set_params(self, coordinates, zoom):
        self.coordinates = coordinates
        self.zoom = zoom

    def get_params(self):
        return self.coordinates, self.zoom

    def get_map(self):
        map_params = {
            "l": "map",
            "ll": ','.join([str(i) for i in self.coordinates]),
            "z": self.zoom,
        }
        response = requests.get("http://static-maps.yandex.ru/1.x/",
                                params=map_params)
        Image.open(BytesIO(response.content)).save(PATH + 'temp.png')
        return pygame.image.load(PATH + 'temp.png')

    def show(self, surf):
        surf.blit(self.image, (0, 0))

    def key_down(self, key):
        if key not in [pygame.K_PAGEUP, pygame.K_PAGEDOWN]:
            return
        if key == pygame.K_PAGEUP:
            step = 1
        elif key == pygame.K_PAGEDOWN:
            step = -1
        if self.borders[0] <= self.zoom + step <= self.borders[1]:
            self.zoom += step
            self.image = self.get_map()


if __name__ == '__main__':
    try:
        os.mkdir(PATH)
    except FileExistsError:
        pass

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    running = True

    operator = Map((34.11, 66.56), 5)

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
    shutil.rmtree(PATH, ignore_errors=True)
