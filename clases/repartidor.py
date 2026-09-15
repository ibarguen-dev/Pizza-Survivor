import pygame
from clases.config import (
    VELOCIDAD_REPARTIDOR, REPARTIDOR_ANCHO, REPARTIDOR_ALTO,
    LIMITE_REPARTIDOR_X, LIMITE_REPARTIDOR_Y,
)


class Repartidor:
    def __init__(self, x, y, imagen_path):
        self.x = x
        self.y = y
        self.imagen = pygame.image.load(imagen_path)
        self.imagen = pygame.transform.scale(self.imagen, (REPARTIDOR_ANCHO, REPARTIDOR_ALTO))
        self.cambio_x = 0
        self.cambio_y = 0
        self.velocidad = VELOCIDAD_REPARTIDOR
        self.ancho = REPARTIDOR_ANCHO
        self.alto = REPARTIDOR_ALTO

    def mover(self):
        self.x += self.cambio_x
        self.y += self.cambio_y
        self.x = max(LIMITE_REPARTIDOR_X[0], min(self.x, LIMITE_REPARTIDOR_X[1]))
        self.y = max(LIMITE_REPARTIDOR_Y[0], min(self.y, LIMITE_REPARTIDOR_Y[1]))

    def obtener_centro(self):
        return (self.x + self.ancho // 2, self.y + self.alto // 2)

    def obtener_posicion(self):
        return (self.x, self.y)

    def recibir_evento_tecla(self, tecla, presionada):
        if presionada:
            if tecla == pygame.K_LEFT:
                self.cambio_x -= self.velocidad
            elif tecla == pygame.K_RIGHT:
                self.cambio_x += self.velocidad
            elif tecla == pygame.K_UP:
                self.cambio_y -= self.velocidad
            elif tecla == pygame.K_DOWN:
                self.cambio_y += self.velocidad
        else:
            if tecla in (pygame.K_LEFT, pygame.K_RIGHT):
                self.cambio_x = 0
            elif tecla in (pygame.K_UP, pygame.K_DOWN):
                self.cambio_y = 0

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, (self.x, self.y))
