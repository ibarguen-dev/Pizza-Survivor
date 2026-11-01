"""Pizza Survivor - punto de entrada.


Flujo de la aplicación:

    MENU  ->  JUGANDO  ->  FIN (game over)  ->  JUGANDO | MENU

En el menú se puede empezar una partida o leer las instrucciones. Al perder
todas las vidas aparece la pantalla de fin, que espera a que el jugador pulse
S (jugar de nuevo) o N (cerrar el juego).
"""
import pygame

from clases.config import (
    ALTO_PANTALLA, ANCHO_PANTALLA, FPS,
    ESTADO_FIN, ESTADO_JUGANDO, ESTADO_MENU, TITULO_VENTANA,
    VOLUMEN_MUSICA, VOLUMEN_SONIDOS,
)
from clases.juego import Juego
from clases.rutas import resolver
from clases.ui import (
    ACCION_JUGAR, ACCION_REINICIAR, ACCION_SALIR, Menu, PantallaFin,
)

# Partida en curso. La usan las pruebas automaticas para inspeccionar el
# juego sin tener que pasar por la interfaz.
PARTIDA = {"juego": None}


def main():
    pygame.init()
    pygame.mixer.init()

    # Pantalla
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption(TITULO_VENTANA)
    icono = pygame.image.load(resolver("assets/imagenes/pizza.png"))
    pygame.display.set_icon(icono)

    # Fondo
    fondo = pygame.image.load(resolver("assets/imagenes/fondo.png"))
    fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))

    # Recursos de la interfaz
    corazon_img = pygame.transform.scale(
        pygame.image.load(resolver("assets/imagenes/corazon.png")), (32, 32)
    )
    fuentes = {
        "normal": pygame.font.Font(None, 36),
        "grande": pygame.font.Font(None, 72),
        "media": pygame.font.Font(None, 48),
    }

    # Sonidos
    pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
    sonidos = {
        "disparo": pygame.mixer.Sound(resolver("assets/mp3/disparo.mp3")),
        "golpe": pygame.mixer.Sound(resolver("assets/mp3/golpe.mp3")),
        "vida_perdida": pygame.mixer.Sound(resolver("assets/mp3/vida_perdida.mp3")),
    }
    for sonido in sonidos.values():
        sonido.set_volume(VOLUMEN_SONIDOS)
    pygame.mixer.music.load(resolver("assets/mp3/MusicaFondo.mp3"))
    pygame.mixer.music.play(-1)
    musica_sonando = True

    reloj = pygame.time.Clock()

    menu = Menu(fondo)
    juego = None
    pantalla_fin = None
    mejor_puntaje = 0
    estado = ESTADO_MENU
    salir = False

    while not salir:
        tiempo_actual = pygame.time.get_ticks()

        # ---------------------------------------------------------------- #
        # Eventos
        # ---------------------------------------------------------------- #
        for evento in pygame.event.get():
            if estado == ESTADO_MENU:
                accion = menu.manejar_evento(evento)
                if accion == ACCION_JUGAR:
                    juego = Juego(sonidos)
                    PARTIDA["juego"] = juego
                    pantalla_fin = None
                    estado = ESTADO_JUGANDO
                elif accion == ACCION_SALIR:
                    salir = True

            elif estado == ESTADO_JUGANDO:
                accion = juego.manejar_evento(evento)
                if accion == ACCION_SALIR:
                    salir = True
                elif accion == "menu":
                    # ESC: se vuelve al menu principal.
                    juego = None
                    PARTIDA["juego"] = None
                    estado = ESTADO_MENU

            elif estado == ESTADO_FIN:
                accion = pantalla_fin.manejar_evento(evento)
                if accion == ACCION_REINICIAR:
                    mejor_puntaje = max(mejor_puntaje, juego.gestor_estado.puntaje)
                    juego = Juego(sonidos)
                    PARTIDA["juego"] = juego
                    pantalla_fin = None
                    if not musica_sonando:
                        pygame.mixer.music.play(-1)
                        musica_sonando = True
                    estado = ESTADO_JUGANDO
                elif accion == ACCION_SALIR:
                    salir = True

        # ---------------------------------------------------------------- #
        # Actualizacion y dibujo
        # ---------------------------------------------------------------- #
        if estado == ESTADO_MENU:
            if not musica_sonando:
                # La musica se detiene en el game over: se reanuda al volver
                # al menu.
                pygame.mixer.music.play(-1)
                musica_sonando = True
            menu.dibujar(pantalla)

        elif estado == ESTADO_JUGANDO:
            if juego.actualizar(tiempo_actual):
                # Se acabaron las vidas: la partida termina aqui.
                pygame.mixer.music.stop()
                musica_sonando = False
                mejor_puntaje = max(mejor_puntaje, juego.gestor_estado.puntaje)
                pantalla_fin = PantallaFin(
                    juego.gestor_estado.puntaje,
                    juego.gestor_estado.tiempo_fin - juego.gestor_estado.tiempo_inicio,
                    mejor_puntaje,
                )
                estado = ESTADO_FIN
            else:
                juego.dibujar(pantalla, fondo, fuentes, corazon_img)

        elif estado == ESTADO_FIN:
            # Se dibuja la escena congelada de la ultima partida y encima la
            # pantalla de fin, para que el jugador vea donde se quedo.
            juego.dibujar(pantalla, fondo, fuentes, corazon_img)
            pantalla_fin.dibujar(pantalla)

        pygame.display.update()
        reloj.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
