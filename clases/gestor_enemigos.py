import pygame
from clases.config import ANCHO_PANTALLA, ALTO_PANTALLA
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
        # Mover todos los enemigos hacia el objetivo
        for enemigo in self.enemigos:
            dx = objetivo_x - enemigo.x
            dy = objetivo_y - enemigo.y
            distancia = (dx**2 + dy**2)**0.5
            if distancia > 0:
                enemigo.x += (dx / distancia) * enemigo.velocidad
                enemigo.y += (dy / distancia) * enemigo.velocidad

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
        """Aumenta dificultad cada 10s: reduce intervalos de spawn."""
        if not hasattr(self, '_ultimo_aumento'):
            self._ultimo_aumento = 0

        if tiempo_actual - self._ultimo_aumento >= 20000:
            self._ultimo_aumento = tiempo_actual
            # Reducir intervalos (hacerlos más frecuentes)
            for tipo in self._tipos:
                nuevo_intervalo = tipo['intervalo'] * 0.9
                if nuevo_intervalo >= 500:  # piso mínimo de 500ms
                    tipo['intervalo'] = nuevo_intervalo
            #print(f"[DIFICULTAD] Multiplicador: {self._multiplicador_dificultad:.2f}")
            return True
        return False

    def detectar_colision_repartidor(self, repartidor, radio_colision=55):
        centro_rx, centro_ry = repartidor.obtener_centro()
        eliminados = []
        for i, enemigo in enumerate(self.enemigos):
            cx, cy = enemigo.obtener_centro()
            dx = centro_rx - cx
            dy = centro_ry - cy
            dist = (dx**2 + dy**2)**0.5
            #print(f"[DEBUG] Enemigo {i}: distancia={dist:.1f}, radio={radio_colision}")
            if dist < radio_colision:
                #print(f"[DEBUG] COLISION detectada con enemigo {i}")
                eliminados.append(i)
        for i in reversed(eliminados):
            self.enemigos.pop(i)
        return len(eliminados) > 0

    def detectar_colision_proyectil(self, proyectil):
        for i, enemigo in enumerate(self.enemigos):
            if proyectil.colisiona_con(enemigo):
                self.enemigos.pop(i)
                return True
        return False

    def encontrar_mas_cercano(self, objetivo_x, objetivo_y):
        return Enemigo.encontrar_mas_cercano(objetivo_x, objetivo_y, self.enemigos)

    def dibujar(self, pantalla):
        for enemigo in self.enemigos:
            enemigo.dibujar(pantalla)

    def limpiar(self):
        self.enemigos = [
            e for e in self.enemigos
            if not e.esta_fuera_de_pantalla(ANCHO_PANTALLA, ALTO_PANTALLA)
        ]
