# Configuración centralizada del juego
import pygame

# Pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
TITULO_VENTANA = "Pizza Survivor"
# Fotogramas por segundo. El valor alto mantiene el ritmo de juego con el que
# estan ajustadas las velocidades; bajarlo a 60 hace el juego mas lento.
FPS = 500

# Colores de la interfaz (menú, instrucciones y pantalla de fin)
COLOR_FONDO_MENU = (18, 14, 26)
COLOR_PANEL = (36, 29, 52)
COLOR_PANEL_BORDE = (104, 88, 140)
COLOR_TEXTO = (245, 240, 232)
COLOR_TEXTO_SECUNDARIO = (168, 158, 190)
COLOR_ACENTO = (255, 196, 64)
COLOR_PELIGRO = (226, 78, 78)
COLOR_SOMBRA = (0, 0, 0)

# Estados de la interfaz
ESTADO_MENU = "menu"
ESTADO_FIN = "fin"

# Límites del repartidor
LIMITE_REPARTIDOR_X = (0, 736)
LIMITE_REPARTIDOR_Y = (0, 500)

# Repartidor
VELOCIDAD_REPARTIDOR = 1
REPARTIDOR_ANCHO = 64
REPARTIDOR_ALTO = 100

# Enemigos
ANCHO_PANTALLA_SPAWN = 800
ALTO_PANTALLA_SPAWN = 600

# Los enemigos comunes aparecen más lento que antes
INTERVALO_SPAWN_PERRO = 4000
INTERVALO_SPAWN_GATO = 5000
# Piso del intervalo al subir la dificultad, para que sigan siendo lentos
INTERVALO_SPAWN_MINIMO_COMUN = 2500

# Proyectiles
RADIO_COLISION_PROYECTIL = 30

# Vidas de los enemigos comunes
VIDAS_ENEMIGO_COMUN = 1

# Jefes
VIDAS_JEFE = 5
# Modelo de daño de los jefes:
# - Cada proyectil (manual o automático) es un impacto.
# - Hacen falta IMPACTOS_POR_VIDA_JEFE impactos para quitar una vida
#   (3 proyectiles manuales = 1 vida).
# - El super poder 1 es la excepción: quita una vida de un solo golpe, pero
#   el poder desaparece al tocar al jefe.
IMPACTOS_POR_VIDA_JEFE = 3
ANCHO_JEFE = 110
ALTO_JEFE = 120
VELOCIDAD_JEFE = 0.5
# Un jefe aparece cada 3.5 minutos, elegido al azar
INTERVALO_APARICION_JEFE = 30000
PUNTOS_JEFE = 50
# Cuántos jefes pueden estar en pantalla a la vez
MAX_JEFES_SIMULTANEOS = 1
# Radio de colisión de los jefes (son mucho más grandes que los comunes)
RADIO_COLISION_JEFE = 55

# Ataque a distancia de los jefes
INTERVALO_ATAQUE_JEFE = 3000
VELOCIDAD_PROYECTIL_JEFE = 3.0
ANCHO_PROYECTIL_JEFE = 26
ALTO_PROYECTIL_JEFE = 27
RADIO_COLISION_PROYECTIL_JEFE = 26

# Jefe zombie humano: la ira (persecución) y el descanso
DURACION_IRA_ZOMBIE = 3000
DURACION_DESCANSO_ZOMBIE = 3000
VELOCIDAD_IRA_ZOMBIE = 0.7
VELOCIDAD_DESCANSO_ZOMBIE = 0.17

# Jefe perro zombi: la invocación de la jauría
INTERVALO_INVOCACION_JEFE = 6000
CANTIDAD_JAURIA = 6
VELOCIDAD_JAURIA = 1.3
ANCHO_JAURIA = 44
ALTO_JAURIA = 44
RADIO_COLISION_JAURIA = 26

# Pizzas manuales (tecla E)
PIZZAS_MANUALES_MAXIMAS = 5
INTERVALO_RECARGA_PIZZA = 3500
VELOCIDAD_PIZZA_MANUAL = 4.0
RADIO_COLISION_PIZZA_MANUAL = 26

# Vidas
VIDAS_INICIALES = 3
VIDAS_MAXIMAS = 5
DURACION_INVULNERABILIDAD = 1000

# Super poderes
TIPO_PERFORANTE = "perforante"
TIPO_ORBITA = "orbita"
TIPO_VIDA = "vida"
CARGAS_MAXIMAS_PODER = 3

# Intervalo de aparición de los recogibles (poderes y vidas)
INTERVALO_SPAWN_RECOGIBLE_MIN = 12000
INTERVALO_SPAWN_RECOGIBLE_MAX = 20000
# Durante los primeros 2 minutos también pueden aparecer vidas extra
VENTANA_VIDA_EXTRA = 120000
DURACION_RECOGIBLE = 12000
VELOCIDAD_RECOGIBLE = 0.25
RADIO_RECOGIBLE = 34

# Super poder 1: proyectil que atraviesa a varios enemigos
VELOCIDAD_PERFORANTE = 4.5
RADIO_PERFORANTE = 40

# Super poder 2: orbita protectora alrededor del repartidor
RADIO_ORBITA = 62
VELOCIDAD_ANGULAR_ORBITA = 0.06
ATAQUES_PROTEGIDOS = 3
DURACION_ORBITA = 15000

# Dificultad
INTERVALO_SPAWN_INICIAL = 2500
INTERVALO_SPAWN_MINIMO = 1000
DECREMENTO_SPAWN = 50

# Lanzamiento
INTERVALO_LANZAMIENTO = 1500

# Puntos
PUNTOS_POR_GOLPE = 1
PUNTOS_POR_GOLPE_JEFE = 2

# Sonidos
VOLUMEN_MUSICA = 0.3
VOLUMEN_SONIDOS = 0.7

# Estados del juego
ESTADO_JUGANDO = "jugando"
ESTADO_TERMINADO = "terminado"
