from io import BytesIO
from PIL import Image
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
        self.image = self.get_map()

    def set_params(self, coordinates, zoom):
        self.coordinates = coordinates
        self.zoom = zoom

    def get_params(self):
        return self.coordinates, self.zoom

    def get_map(self):
        map_params = {
            'l': 'map',
            'll': ','.join([str(i) for i in self.coordinates]),
            'z': self.zoom,
        }
        response = requests.get('http://static-maps.yandex.ru/1.x/', params=map_params)
        Image.open(BytesIO(response.content)).save('temp/' + 'temp.png')
        return pygame.image.load('temp/' + 'temp.png')

    def show(self, surf):
        surf.blit(self.image, (0, 0))


if __name__ == '__main__':
    try:
        os.mkdir(PATH)
    except FileExistsError:
        pass

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

    running = True

    operator = Map((50, 50), 5)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        operator.show(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    shutil.rmtree(PATH, ignore_errors=True)
