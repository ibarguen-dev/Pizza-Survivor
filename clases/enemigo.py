import pygame
import random
import math


class Enemigo:
    ancho = 0
    alto = 0
    velocidad = 0
    imagen = None

    def __init__(self):
        self.x, self.y = self.obtener_posicion_inicial()

    @classmethod
    def obtener_posicion_inicial(cls):
        from clases.config import ANCHO_PANTALLA_SPAWN, ALTO_PANTALLA_SPAWN
        posiciones_por_borde = {
            "arriba": [random.randint(0, ANCHO_PANTALLA_SPAWN - cls.ancho), -cls.alto],
            "abajo": [random.randint(0, ANCHO_PANTALLA_SPAWN - cls.ancho), ALTO_PANTALLA_SPAWN],
            "izquierda": [-cls.ancho, random.randint(0, ALTO_PANTALLA_SPAWN - cls.alto)],
            "derecha": [ANCHO_PANTALLA_SPAWN, random.randint(0, ALTO_PANTALLA_SPAWN - cls.alto)],
        }
        borde = random.choice(list(posiciones_por_borde.keys()))
        return posiciones_por_borde[borde]

    def obtener_posicion(self):
        return (self.x, self.y)

    def mover_hacia(self, objetivo_x, objetivo_y):
        dx = objetivo_x - self.x
        dy = objetivo_y - self.y
        distancia = math.sqrt(dx ** 2 + dy ** 2)
        if distancia > 0:
            self.x += (dx / distancia) * self.velocidad
            self.y += (dy / distancia) * self.velocidad

    def obtener_centro(self):
        return (self.x + self.ancho // 2, self.y + self.alto // 2)

    def distancia_hacia(self, objetivo_x, objetivo_y):
        cx, cy = self.obtener_centro()
        dx = objetivo_x - cx
        dy = objetivo_y - cy
        return math.sqrt(dx ** 2 + dy ** 2)

    def colisiona_con(self, otro):
        cx1, cy1 = self.obtener_centro()
        cx2, cy2 = otro.obtener_centro()
        dx = cx1 - cx2
        dy = cy1 - cy2
        return math.sqrt(dx ** 2 + dy ** 2) < 30

    def esta_fuera_de_pantalla(self, ancho_pantalla, alto_pantalla, margen=50):
        return (self.x < -margen or self.x > ancho_pantalla + margen or
                self.y < -margen or self.y > alto_pantalla + margen)

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    @classmethod
    def cargar_imagen(cls, ruta):
        cls.imagen = pygame.image.load(ruta)
        cls.imagen = pygame.transform.scale(cls.imagen, (cls.ancho, cls.alto))

    def dibujar(self, pantalla):
        if self.imagen:
            pantalla.blit(self.imagen, (self.x, self.y))

    @classmethod
    def encontrar_mas_cercano(cls, objetivo_x, objetivo_y, lista_enemigos):
        if not lista_enemigos:
            return None
        mas_cercano = None
        menor_distancia = float('inf')
        for enemigo in lista_enemigos:
            dist = enemigo.distancia_hacia(objetivo_x, objetivo_y)
            if dist < menor_distancia:
                menor_distancia = dist
                mas_cercano = enemigo
        return mas_cercano
