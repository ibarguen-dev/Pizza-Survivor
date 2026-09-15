import pygame
from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA, TITULO_VENTANA,
    INTERVALO_LANZAMIENTO, VOLUMEN_MUSICA, VOLUMEN_SONIDOS,
    ESTADO_TERMINADO,
)
from clases.repartidor import Repartidor
from clases.perro import Perro
from clases.gato import Gato
from clases.pizza import Pizza
from clases.gestor_enemigos import GestorEnemigos
from clases.gestor_proyectiles import GestorProyectiles
from clases.gestor_estado import GestorEstado
from clases.config import INTERVALO_SPAWN_INICIAL

pygame.init()
pygame.mixer.init()

# Pantalla
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption(TITULO_VENTANA)
icono = pygame.image.load("assets/imagenes/pizza.png")
pygame.display.set_icon(icono)

# Fondo
fondo = pygame.image.load("assets/imagenes/fondo.png")
fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))

# Recursos del repartidor
corazon_img = pygame.image.load("assets/imagenes/corazon.png")
corazon_img = pygame.transform.scale(corazon_img, (32, 32))
fuente = pygame.font.Font(None, 36)
fuente_grande = pygame.font.Font(None, 72)
fuente_media = pygame.font.Font(None, 48)

# Gestores
repartidor = Repartidor(368, 440, "assets/imagenes/repartidor.png")
gestor_enemigos = GestorEnemigos()
gestor_enemigos.agregar_tipo(Perro, INTERVALO_SPAWN_INICIAL)
gestor_enemigos.agregar_tipo(Gato, intervalo_spawn=3000,velocidad=0.7)
gestor_proyectiles = GestorProyectiles(Pizza)
gestor_estado = GestorEstado()

# Sonidos
pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
sonido_disparo = pygame.mixer.Sound("assets/mp3/disparo.mp3")
sonido_golpe = pygame.mixer.Sound("assets/mp3/golpe.mp3")
sonido_vida_perdida = pygame.mixer.Sound("assets/mp3/vida_perdida.mp3")
sonido_disparo.set_volume(VOLUMEN_SONIDOS)
sonido_golpe.set_volume(VOLUMEN_SONIDOS)
sonido_vida_perdida.set_volume(VOLUMEN_SONIDOS)

pygame.mixer.music.load("assets/mp3/MusicaFondo.mp3")
pygame.mixer.music.play(-1)

reloj = pygame.time.Clock()
tiempo_ultimo_lanzamiento = pygame.time.get_ticks()
se_ejecuta = True


def dibujar_vidas():
    for i in range(gestor_estado.vidas):
        pantalla.blit(corazon_img, (10 + i * 36, 10))


def dibujar_puntaje():
    texto = fuente.render(f"puntaje: {gestor_estado.puntaje}", True, (255, 255, 255))
    pantalla.blit(texto, (650, 10))


def dibujar_cronometro(tiempo_actual):
    tt = gestor_estado.obtener_tiempo_transcurrido(tiempo_actual)
    minutos = tt // 60000
    segundos = (tt % 60000) // 1000
    texto = fuente.render(f"Tiempo: {minutos}:{segundos:02d}", True, (255, 255, 255))
    pantalla.blit(texto, (350, 10))


def dibujar_pantalla_fin():
    pantalla.fill((0, 0, 0))
    tt = gestor_estado.tiempo_fin
    minutos = tt // 60000
    segundos = (tt % 60000) // 1000
    texto_go = fuente_grande.render("Game Over", True, (255, 0, 0))
    pantalla.blit(texto_go, texto_go.get_rect(center=(400, 200)))
    texto_punt = fuente_media.render(f"Puntaje: {gestor_estado.puntaje}", True, (255, 255, 255))
    pantalla.blit(texto_punt, texto_punt.get_rect(center=(400, 300)))
    texto_tiempo = fuente_media.render(f"Tiempo: {minutos}:{segundos:02d}", True, (255, 255, 255))
    pantalla.blit(texto_tiempo, texto_tiempo.get_rect(center=(400, 380)))


 while se_ejecuta:
    tiempo_actual = pygame.time.get_ticks()
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            se_ejecuta = False

        if evento.type in (pygame.KEYDOWN, pygame.KEYUP):
            presionada = evento.type == pygame.KEYDOWN
            repartidor.recibir_evento_tecla(evento.key, presionada)

    if gestor_estado.juego_terminado():
        dibujar_pantalla_fin()
        pygame.display.update()
        reloj.tick(500)
        continue

    repartidor.mover()

    # Lógica de juego
    rx, ry = repartidor.obtener_posicion()
    gestor_enemigos.actualizar(tiempo_actual, rx + 32, ry + 50)
    gestor_enemigos.aumentar_dificultad(tiempo_actual)

    if tiempo_actual - tiempo_ultimo_lanzamiento >= INTERVALO_LANZAMIENTO:
        objetivo = gestor_enemigos.encontrar_mas_cercano(rx + 32, ry + 50)
        if objetivo:
            ox, oy = objetivo.obtener_centro()
            gestor_proyectiles.lanzar(rx + 32, ry + 50, ox, oy)
            sonido_disparo.play()
        tiempo_ultimo_lanzamiento = tiempo_actual

    gestor_proyectiles.actualizar()
    puntos = gestor_proyectiles.detectar_colisiones_enemigos(gestor_enemigos)
    if puntos > 0:
        gestor_estado.sumar_puntaje(puntos)
        sonido_golpe.play()

    if gestor_enemigos.detectar_colision_repartidor(repartidor):
        if gestor_estado.perder_vida():
            sonido_vida_perdida.play()
            if gestor_estado.juego_terminado():
                pygame.mixer.music.stop()

    gestor_estado.actualizar_invencibilidad(tiempo_actual)

    # Dibujar
    pantalla.blit(fondo, (0, 0))
    dibujar_vidas()
    dibujar_puntaje()
    dibujar_cronometro(tiempo_actual)

    if not gestor_estado.esta_invulnerable() or (tiempo_actual // 100) % 2 == 0:
        repartidor.dibujar(pantalla)

    gestor_enemigos.dibujar(pantalla)
    gestor_proyectiles.dibujar(pantalla)

    pygame.display.update()
    reloj.tick(500)

pygame.quit()
