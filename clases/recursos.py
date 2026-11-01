"""Carga de imágenes con reserva, para que el juego no se caiga si falta un archivo."""
import os

import pygame

from clases.rutas import resolver


def ruta_existe(ruta):
    return os.path.isfile(resolver(ruta))


def cargar_imagen(ruta, ancho=None, alto=None):
    """Carga una imagen y la escala. Si falta, devuelve un marcador de posición."""
    if ruta_existe(ruta):
        imagen = pygame.image.load(resolver(ruta))
    else:
        print(f"[AVISO] No se encontró {ruta}; se usa un marcador de posición.")
        imagen = pygame.Surface((64, 64))
        imagen.fill((120, 120, 140))
        pygame.draw.circle(imagen, (200, 60, 60), (32, 32), 28)
    if ancho and alto:
        imagen = pygame.transform.scale(imagen, (ancho, alto))
    return imagen


def cargar_imagen_jefe(ruta, ancho, alto, color=(96, 150, 84)):
    """Carga la imagen de un jefe.

    Si el archivo no existe (por ejemplo 'zombie.png', que todavía no has
    añadido) se dibuja un jefe de dibujo con esa tonalidad en lugar de un
    rectángulo gris, para que el juego no se vea roto.
    """
    if ruta_existe(ruta):
        return pygame.transform.scale(pygame.image.load(resolver(ruta)), (ancho, alto))

    print(f"[AVISO] No se encontró {ruta}; se dibuja un jefe provisional.")
    imagen = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    oscuro = tuple(max(0, c - 45) for c in color)
    # Cuerpo
    pygame.draw.ellipse(imagen, color, (ancho * 0.12, alto * 0.42, ancho * 0.76, alto * 0.56))
    # Brazos
    pygame.draw.ellipse(imagen, color, (ancho * 0.02, alto * 0.46, ancho * 0.24, alto * 0.40))
    pygame.draw.ellipse(imagen, color, (ancho * 0.74, alto * 0.46, ancho * 0.24, alto * 0.40))
    # Cabeza
    pygame.draw.ellipse(imagen, color, (ancho * 0.24, alto * 0.06, ancho * 0.52, alto * 0.42))
    # Ojos
    radio_ojo = max(2, ancho // 18)
    pygame.draw.circle(imagen, oscuro, (int(ancho * 0.37), int(alto * 0.24)), radio_ojo)
    pygame.draw.circle(imagen, oscuro, (int(ancho * 0.63), int(alto * 0.24)), radio_ojo)
    # Mandíbula
    pygame.draw.rect(
        imagen, oscuro,
        (int(ancho * 0.36), int(alto * 0.35), int(ancho * 0.28), max(2, alto // 24)),
    )
    return imagen


def imagen_cabeza_jefe(ancho=40, alto=40):
    """Imagen de la cabeza para las vidas de los jefes.

    Usa 'head.png' si está disponible. Si no, deriva la cabeza del repartidor.
    En los dos casos se refleja horizontalmente: la cabeza del jefe es
    similar a la del repartidor pero al lado contrario.
    """
    if ruta_existe("assets/imagenes/head.png"):
        imagen = pygame.image.load(resolver("assets/imagenes/head.png")).convert_alpha()
    else:
        repartidor = pygame.image.load(
            resolver("assets/imagenes/repartidor.png")
        ).convert_alpha()
        ancho_original, alto_original = repartidor.get_size()
        # La cabeza es la parte superior del sprite del repartidor: se recorta
        # un cuadrado para no deformarla al ajustarla al icono.
        alto_cabeza = int(alto_original * 0.16)
        ancho_cabeza = min(ancho_original, alto_cabeza)
        x = (ancho_original - ancho_cabeza) // 2
        imagen = repartidor.subsurface(
            pygame.Rect(x, 0, ancho_cabeza, alto_cabeza)
        )
    return pygame.transform.scale(pygame.transform.flip(imagen, True, False), (ancho, alto))
