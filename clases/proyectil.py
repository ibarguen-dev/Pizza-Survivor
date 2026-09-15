import pygame
import math


class Proyectil:
    ancho = 0
    alto = 0
    velocidad = 0
    imagen = None

    def __init__(self, x, y, objetivo_x, objetivo_y):
        self.x = x
        self.y = y
        self.calcular_direccion(objetivo_x, objetivo_y)

    def calcular_direccion(self, objetivo_x, objetivo_y):
        dx = objetivo_x - self.x
        dy = objetivo_y - self.y
        distancia = math.sqrt(dx ** 2 + dy ** 2)
        if distancia > 0:
            self.dx = (dx / distancia) * self.velocidad
            self.dy = (dy / distancia) * self.velocidad
        else:
            self.dx = 0
            self.dy = 0

    def mover(self):
        self.x += self.dx
        self.y += self.dy

    def obtener_posicion(self):
        return (self.x, self.y)

    def obtener_centro(self):
        return (self.x + self.ancho // 2, self.y + self.alto // 2)

    def esta_fuera_de_pantalla(self, ancho_pantalla, alto_pantalla):
        return (self.x < -self.ancho or self.x > ancho_pantalla or
                self.y < -self.alto or self.y > alto_pantalla)

    def colisiona_con(self, enemigo):
        cx, cy = self.obtener_centro()
        ex, ey = enemigo.obtener_centro()
        dx = cx - ex
        dy = cy - ey
        return math.sqrt(dx ** 2 + dy ** 2) < 30

    @classmethod
    def cargar_imagen(cls, ruta):
        cls.imagen = pygame.image.load(ruta)
        cls.imagen = pygame.transform.scale(cls.imagen, (cls.ancho, cls.alto))

    def dibujar(self, pantalla):
        if self.imagen:
            pantalla.blit(self.imagen, (self.x, self.y))
