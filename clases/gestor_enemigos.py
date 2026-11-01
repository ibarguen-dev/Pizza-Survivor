import pygame
from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA, INTERVALO_SPAWN_MINIMO_COMUN,
)
from clases.enemigo import Enemigo


class GestorEnemigos:
    def __init__(self):
        self.enemigos = []
        self._tipos = []  # (clase, intervalo_spawn, ultimo_spawn)
        self._multiplicador_dificultad = 1.0

    def agregar_tipo(self, clase_enemigo, intervalo_spawn, velocidad=None):
        """Registra un tipo de enemigo con su intervalo de spawn y velocidad.
        velocidad=None usa la velocidad definida en la clase del enemigo."""
        self._tipos.append({
            'clase': clase_enemigo,
            'intervalo': intervalo_spawn,
            'ultimo_spawn': pygame.time.get_ticks(),
            'intervalo_base': intervalo_spawn,
            'velocidad_base': velocidad if velocidad is not None else clase_enemigo.velocidad,
        })
        # Spawn inicial inmediato
        self.enemigos.append(clase_enemigo())

    def actualizar(self, tiempo_actual, objetivo_x, objetivo_y):
        # Mover todos los enemigos. Cada uno decide cómo se mueve:
        # los comunes persiguen, los jefes tienen su propio comportamiento
        # y la jauría avanza en línea recta.
        for enemigo in self.enemigos:
            enemigo.actualizar_movimiento(objetivo_x, objetivo_y)

        # Spawn por cada tipo registrado
        for tipo in self._tipos:
            intervalo_actual = tipo['intervalo'] * self._multiplicador_dificultad
            if tiempo_actual - tipo['ultimo_spawn'] >= intervalo_actual:
                enemigo = tipo['clase']()
                # Aplicar velocidad override si se definió
                if tipo['velocidad_base'] != tipo['clase'].velocidad:
                    enemigo.velocidad = tipo['velocidad_base']
                self.enemigos.append(enemigo)
                tipo['ultimo_spawn'] = tiempo_actual

    def aumentar_dificultad(self, tiempo_actual):
        """Aumenta dificultad cada 20s: reduce intervalos de spawn.

        Los enemigos comunes nunca bajan de INTERVALO_SPAWN_MINIMO_COMUN:
        siempre aparecen lento.
        """
        if not hasattr(self, '_ultimo_aumento'):
            self._ultimo_aumento = 0

        if tiempo_actual - self._ultimo_aumento >= 20000:
            self._ultimo_aumento = tiempo_actual
            # Reducir intervalos (hacerlos más frecuentes)
            for tipo in self._tipos:
                nuevo_intervalo = tipo['intervalo'] * 0.9
                if nuevo_intervalo >= INTERVALO_SPAWN_MINIMO_COMUN:
                    tipo['intervalo'] = nuevo_intervalo
            #print(f"[DIFICULTAD] Multiplicador: {self._multiplicador_dificultad:.2f}")
            return True
        return False

    def detectar_colision_repartidor(self, repartidor, radio_colision=55):
        """Elimina a los enemigos comunes que chocan con el repartidor.

        Los jefes no se eliminan al chocar: solo cuentan como un golpe.
        Devuelve el número de golpes (0 si ninguno).
        """
        centro_rx, centro_ry = repartidor.obtener_centro()
        eliminados = []
        golpes = 0
        for i, enemigo in enumerate(self.enemigos):
            cx, cy = enemigo.obtener_centro()
            dx = centro_rx - cx
            dy = centro_ry - cy
            dist = (dx**2 + dy**2)**0.5
            if dist < radio_colision:
                golpes += 1
                if not enemigo.es_jefe:
                    eliminados.append(i)
        for i in reversed(eliminados):
            self.enemigos.pop(i)
        return golpes

    def detectar_colision_proyectil(self, proyectil):
        """Aplica el daño del proyectil al enemigo que toca.

        Devuelve el enemigo golpeado (o None). Los enemigos comunes mueren
        al primer impacto; los jefes acumulan impactos.
        """
        for i, enemigo in enumerate(self.enemigos):
            if proyectil.colisiona_con(enemigo):
                if enemigo.recibir_dano(1) and not enemigo.es_jefe:
                    self.enemigos.pop(i)
                return enemigo
        return None

    def encontrar_mas_cercano(self, objetivo_x, objetivo_y):
        return Enemigo.encontrar_mas_cercano(objetivo_x, objetivo_y, self.enemigos)

    def dibujar(self, pantalla):
        for enemigo in self.enemigos:
            enemigo.dibujar(pantalla)

    def limpiar(self, margen=150):
        """Quita los enemigos que se han ido muy lejos de la pantalla.

        Los jefes nunca se limpian: pueden aparecer fuera de la pantalla y
        tardan un rato en entrar.
        """
        self.enemigos = [
            e for e in self.enemigos
            if e.es_jefe or not e.esta_fuera_de_pantalla(
                ANCHO_PANTALLA, ALTO_PANTALLA, margen
            )
        ]
