"""Interfaz del juego: menú principal, instrucciones y pantalla de fin.

La interfaz es independiente del resto de la lógica: recibe eventos de pygame
y devuelve una acción ("jugar", "instrucciones", "reiniciar", "salir", None)
que el bucle principal de `main.py` interpreta.
"""
import pygame

from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA,
    COLOR_ACENTO, COLOR_FONDO_MENU, COLOR_PANEL, COLOR_PANEL_BORDE,
    COLOR_PELIGRO, COLOR_SOMBRA, COLOR_TEXTO, COLOR_TEXTO_SECUNDARIO,
)
from clases.rutas import resolver

# Acciones que puede devolver la interfaz
ACCION_NINGUNA = None
ACCION_JUGAR = "jugar"
ACCION_INSTRUCCIONES = "instrucciones"
ACCION_REINICIAR = "reiniciar"
ACCION_SALIR = "salir"

# Secciones de las instrucciones: (título, icono o None, lista de líneas)
SECCIONES_INSTRUCCIONES = [
    (
        "CONTROLES",
        None,
        [
            "Flechas  ->  Mover al repartidor",
            "ESPACIO  ->  Usar el super poder que toque en la cola",
            "E  ->  Lanzar una pizza manual al jefe mas cercano",
            "ESC  ->  Volver al menu principal",
        ],
    ),
    (
        "ATAQUE AUTOMATICO",
        None,
        [
            "El repartidor lanza pizzas solo al enemigo mas cercano.",
            "Cada perro o gato muere de un solo impacto.",
            "Los jefes son distintos: necesitan 3 impactos por vida.",
            "Cada enemigo destruido suma puntos.",
        ],
    ),
    (
        "SUPER PODER 1 - ONDA PERFORANTE",
        "assets/imagenes/super_poder_1.png",
        [
            "Onda que atraviesa a todos los enemigos de su recorrido.",
            "Si toca a un jefe le quita una vida entera y se consume.",
            "Dispara hacia el enemigo mas cercano.",
        ],
    ),
    (
        "SUPER PODER 2 - ORBITA PROTECTORA",
        "assets/imagenes/super_poder_2.png",
        [
            "Un satelite orbita al repartidor y absorbe 3 golpes.",
            "Cada enemigo que te alcanza es consumido por el satelite.",
            "La orbita dura 15 segundos y luego desaparece.",
        ],
    ),
    (
        "CARGAS Y RECOLECTABLES",
        None,
        [
            "Cada super poder tiene 3 cargas: se gasta el que cogiste antes.",
            "Tocar un poder que ya tienes recarga sus cargas.",
            "Si el poder ya estaba lleno, ganas una vida extra.",
            "Los itens aparecen cada 12-20 s y hay que tocarlos.",
            "Los corazones dan una vida extra (maximo 5) durante los 2 primeros",
            "minutos de la partida.",
        ],
    ),
    (
        "ENEMIGOS COMUNES",
        None,
        [
            "PERRO  -  Te persigue despacio desde los bordes de la pantalla.",
            "GATO  -  Te persigue igual, pero es mas rapido que el perro.",
            "JAURIA  -  Perros invocados por un jefe: avanzan en linea recta",
            "y no corrigen su direccion, asi que se pueden esquivar.",
        ],
    ),
    (
        "JEFES",
        None,
        [
            "Aparece un jefe cada 3 minutos y medio, al azar.",
            "PERRO ZOMBI  -  Persigue e invoca jaurias de perros.",
            "ZOMBIE  -  Alterna persecucion y descanso: aprovecha el descanso.",
            "Tienen 5 vidas y una barra de vida en pantalla.",
            "Disparan proyectiles: no te quedes quieto.",
            "Las pizzas manuales (tecla E) son la mejor forma de herirlos.",
        ],
    ),
    (
        "OBJETIVO",
        None,
        [
            "Sobrevive todo el tiempo que puedas y suma puntos.",
            "Tienes 3 vidas y un segundo de invulnerabilidad tras cada golpe.",
            "El mejor puntaje de la sesion se guarda en pantalla.",
        ],
    ),
]

# Alturas de cada tipo de linea en el panel de instrucciones
ALTO_LINEA_TITULO = 34
ALTO_LINEA_TEXTO = 22
ALTO_LINEA_SEPARACION = 12


def _sombra(texto, pantalla, posicion, color_sombra=COLOR_SOMBRA, offset=(2, 2)):
    """Dibuja una sombra bajo el texto para que resalte sobre el fondo."""
    sombra = texto.copy()
    sombra.set_alpha(160)
    pantalla.blit(sombra, (posicion[0] + offset[0], posicion[1] + offset[1]))


def _panel(pantalla, rect, color=COLOR_PANEL, borde=COLOR_PANEL_BORDE, alpha=235):
    """Dibuja un panel rectangular con borde."""
    superficie = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(superficie, color, superficie.get_rect(), border_radius=12)
    superficie.set_alpha(alpha)
    pantalla.blit(superficie, rect.topleft)
    if borde is not None:
        pygame.draw.rect(pantalla, borde, rect, 2, border_radius=12)


class Menu:
    """Menu principal con las opciones de jugar, instrucciones y salir.

    Incluye una segunda pantalla con las instrucciones del juego, que se puede
    desplazar con la rueda del raton o con las flechas.
    """

    ANCHO_PANEL_INSTRUCCIONES = 700
    ALTO_PANEL_INSTRUCCIONES = 470

    def __init__(self, fondo=None):
        self.fondo = fondo
        self.opciones = ["Iniciar partida", "Instrucciones", "Salir del juego"]
        self.opcion_seleccionada = 0
        self.mostrando_instrucciones = False
        self.desplazamiento = 0

        self.fuente_titulo = pygame.font.Font(None, 92)
        self.fuente_subtitulo = pygame.font.Font(None, 32)
        self.fuente_opcion = pygame.font.Font(None, 42)
        self.fuente_pie = pygame.font.Font(None, 26)
        self.fuente_seccion = pygame.font.Font(None, 28)
        self.fuente_texto = pygame.font.Font(None, 24)

        # Iconos decorativos e iconos de las secciones de instrucciones.
        self.icono_pizza = self._cargar_icono("assets/imagenes/pizza.png", 72, 72)
        self.iconos_seccion = {}
        for _, ruta, _ in SECCIONES_INSTRUCCIONES:
            if ruta and ruta not in self.iconos_seccion:
                self.iconos_seccion[ruta] = self._cargar_icono(ruta, 28, 28)

        # Alturas calculadas una vez para poder limitar el desplazamiento.
        self._lineas = self._construir_lineas()
        self._alto_total = self._calcular_alto_total()

    @staticmethod
    def _cargar_icono(ruta, ancho, alto):
        try:
            imagen = pygame.image.load(resolver(ruta))
        except pygame.error:
            return None
        return pygame.transform.scale(imagen, (ancho, alto))

    # ------------------------------------------------------------------ #
    # Entrada
    # ------------------------------------------------------------------ #
    def manejar_evento(self, evento):
        """Procesa un evento. Devuelve la acción a ejecutar."""
        if evento.type == pygame.QUIT:
            return ACCION_SALIR

        if evento.type == pygame.KEYDOWN:
            if self.mostrando_instrucciones:
                return self._evento_instrucciones(evento)
            return self._evento_menu(evento)

        if evento.type == pygame.MOUSEBUTTONDOWN:
            # La rueda del raton desplaza las instrucciones.
            if evento.button == 4:
                self.desplazamiento = max(0, self.desplazamiento - 40)
                return ACCION_NINGUNA
            if evento.button == 5:
                self.desplazamiento = min(
                    self.desplazamiento_maximo(), self.desplazamiento + 40
                )
                return ACCION_NINGUNA
            if self.mostrando_instrucciones:
                return ACCION_NINGUNA
            if evento.button == 1:
                indice = self._opcion_bajo_cursor(evento.pos)
                if indice is not None:
                    self.opcion_seleccionada = indice
                    return self._accion_opcion(indice)

        if evento.type == pygame.MOUSEMOTION and not self.mostrando_instrucciones:
            indice = self._opcion_bajo_cursor(evento.pos)
            if indice is not None:
                self.opcion_seleccionada = indice

        return ACCION_NINGUNA

    def _evento_menu(self, evento):
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return self._accion_opcion(self.opcion_seleccionada)
        elif evento.key == pygame.K_ESCAPE:
            return ACCION_SALIR
        return ACCION_NINGUNA

    def _accion_opcion(self, indice):
        if indice == 0:
            return ACCION_JUGAR
        if indice == 1:
            self.mostrando_instrucciones = True
            self.desplazamiento = 0
            return ACCION_INSTRUCCIONES
        return ACCION_SALIR

    def _evento_instrucciones(self, evento):
        if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.mostrando_instrucciones = False
        elif evento.key in (pygame.K_UP, pygame.K_w):
            self.desplazamiento = max(0, self.desplazamiento - 30)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.desplazamiento = min(self.desplazamiento_maximo(), self.desplazamiento + 30)
        elif evento.key == pygame.K_PAGEUP:
            self.desplazamiento = max(0, self.desplazamiento - 200)
        elif evento.key == pygame.K_PAGEDOWN:
            self.desplazamiento = min(self.desplazamiento_maximo(), self.desplazamiento + 200)
        elif evento.key == pygame.K_HOME:
            self.desplazamiento = 0
        elif evento.key == pygame.K_END:
            self.desplazamiento = self.desplazamiento_maximo()
        return ACCION_NINGUNA

    def _opcion_bajo_cursor(self, posicion):
        """Índice de la opción sobre la que está el ratón (o None)."""
        for i, rect in enumerate(self._rects_opciones()):
            if rect.collidepoint(posicion):
                return i
        return None

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def dibujar(self, pantalla):
        if self.mostrando_instrucciones:
            self._dibujar_instrucciones(pantalla)
        else:
            self._dibujar_menu(pantalla)

    def _fondo_oscurecido(self, pantalla):
        """Dibuja el fondo del juego con un velo oscuro encima."""
        if self.fondo is not None:
            pantalla.blit(self.fondo, (0, 0))
            velo = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
            velo.fill((8, 6, 14, 200))
            pantalla.blit(velo, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO_MENU)

    def _dibujar_menu(self, pantalla):
        self._fondo_oscurecido(pantalla)

        # Icono de pizza sobre el titulo.
        if self.icono_pizza is not None:
            pantalla.blit(
                self.icono_pizza,
                self.icono_pizza.get_rect(center=(ANCHO_PANTALLA // 2, 92)),
            )

        titulo = self.fuente_titulo.render("PIZZA SURVIVOR", True, COLOR_TEXTO)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 158))
        _sombra(titulo, pantalla, rect_titulo.topleft)
        pantalla.blit(titulo, rect_titulo)

        subtitulo = self.fuente_subtitulo.render(
            "Reparte pizza. Sobrevive a los perros y a sus jefes.",
            True, COLOR_TEXTO_SECUNDARIO,
        )
        pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO_PANTALLA // 2, 198)))

        # Opciones del menu.
        rects = self._rects_opciones()
        for i, opcion in enumerate(self.opciones):
            seleccionada = i == self.opcion_seleccionada
            color = COLOR_ACENTO if seleccionada else COLOR_TEXTO_SECUNDARIO
            texto = self.fuente_opcion.render(opcion, True, color)
            rect = rects[i]
            if seleccionada:
                # Marca y fondo destacado para la opción seleccionada.
                fondo = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    fondo, (*COLOR_ACENTO, 40), fondo.get_rect(), border_radius=10
                )
                pantalla.blit(fondo, rect.topleft)
                pygame.draw.rect(pantalla, COLOR_ACENTO, rect, 1, border_radius=10)
            pantalla.blit(texto, texto.get_rect(center=rect.center))

        # Pie de pagina con los controles.
        pie = self.fuente_pie.render(
            "↑ ↓ para moverte   ·   ENTER para confirmar", True, COLOR_TEXTO_SECUNDARIO
        )
        pantalla.blit(pie, pie.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 40)))

    def _rects_opciones(self):
        """Rectángulos de las opciones, en el orden en que se dibujan."""
        rects = []
        ancho = 360
        alto = 46
        x = (ANCHO_PANTALLA - ancho) // 2
        y = 262
        for _ in self.opciones:
            rects.append(pygame.Rect(x, y, ancho, alto))
            y += alto + 12
        return rects

    # ------------------------------------------------------------------ #
    # Instrucciones
    # ------------------------------------------------------------------ #
    def _construir_lineas(self):
        """Lista de lineas del panel: (tipo, texto, icono)."""
        lineas = []
        for titulo, icono, items in SECCIONES_INSTRUCCIONES:
            lineas.append(("titulo", titulo, icono))
            for item in items:
                lineas.append(("texto", item, None))
            lineas.append(("separacion", "", None))
        return lineas

    def _calcular_alto_total(self):
        alto = 0
        for tipo, _, _ in self._lineas:
            if tipo == "titulo":
                alto += ALTO_LINEA_TITULO
            elif tipo == "texto":
                alto += ALTO_LINEA_TEXTO
            else:
                alto += ALTO_LINEA_SEPARACION
        return alto

    def desplazamiento_maximo(self):
        visible = self.ALTO_PANEL_INSTRUCCIONES - 2 * self._margen_panel()
        return max(0, self._alto_total - visible)

    @staticmethod
    def _margen_panel():
        return 22

    def _dibujar_instrucciones(self, pantalla):
        self._fondo_oscurecido(pantalla)

        rect_panel = pygame.Rect(
            (ANCHO_PANTALLA - self.ANCHO_PANEL_INSTRUCCIONES) // 2,
            (ALTO_PANTALLA - self.ALTO_PANEL_INSTRUCCIONES) // 2,
            self.ANCHO_PANEL_INSTRUCCIONES,
            self.ALTO_PANEL_INSTRUCCIONES,
        )
        _panel(pantalla, rect_panel)

        # Titulo del panel.
        titulo = self.fuente_subtitulo.render("COMO SE JUEGA", True, COLOR_ACENTO)
        pantalla.blit(titulo, (rect_panel.x + 26, rect_panel.y - 30))

        # Contenido con desplazamiento.
        margen = self._margen_panel()
        x = rect_panel.x + margen
        y = rect_panel.y + margen - self.desplazamiento
        limite_inferior = rect_panel.bottom - margen

        for tipo, texto, icono in self._lineas:
            if tipo == "titulo":
                alto = ALTO_LINEA_TITULO
            elif tipo == "texto":
                alto = ALTO_LINEA_TEXTO
            else:
                alto = ALTO_LINEA_SEPARACION

            if y + alto >= rect_panel.y + margen and y <= limite_inferior:
                if tipo == "titulo":
                    color = COLOR_ACENTO
                    fuente = self.fuente_seccion
                else:
                    color = COLOR_TEXTO
                    fuente = self.fuente_texto
                if texto:
                    dibujado = fuente.render(texto, True, color)
                    pantalla.blit(dibujado, (x, y))
                    # El icono de la sección va justo detras de su titulo.
                    if icono and icono in self.iconos_seccion:
                        pantalla.blit(
                            self.iconos_seccion[icono],
                            (x + dibujado.get_width() + 10, y + 2),
                        )
            y += alto

        # Barra de desplazamiento.
        self._dibujar_barra_desplazamiento(pantalla, rect_panel)

        # Pie: como salir de las instrucciones.
        pie = self.fuente_pie.render(
            "ESC para volver   ·   ↑ ↓ o rueda del raton para desplazar",
            True, COLOR_TEXTO_SECUNDARIO,
        )
        pantalla.blit(pie, pie.get_rect(center=(ANCHO_PANTALLA // 2, rect_panel.bottom + 26)))

    def _dibujar_barra_desplazamiento(self, pantalla, rect_panel):
        maximo = self.desplazamiento_maximo()
        if maximo <= 0:
            return
        alto_total = rect_panel.height - 2 * self._margen_panel()
        proporcion = self.desplazamiento / maximo
        alto_barra = max(30, int(alto_total * (alto_total / self._alto_total)))
        y = rect_panel.y + self._margen_panel() + int((alto_total - alto_barra) * proporcion)
        x = rect_panel.right - 10
        pygame.draw.rect(
            pantalla,
            (70, 62, 92),
            pygame.Rect(x - 4, rect_panel.y + self._margen_panel(), 6, alto_total),
            border_radius=3,
        )
        pygame.draw.rect(
            pantalla,
            COLOR_ACENTO,
            pygame.Rect(x - 4, y, 6, alto_barra),
            border_radius=3,
        )


class PantallaFin:
    """Pantalla de game over.

    Muestra el resultado de la partida y se queda esperando a que el jugador
    decida: "S" vuelve a jugar y "N" cierra el juego.
    """

    def __init__(self, puntaje, tiempo_ms, mejor_puntaje=0):
        self.puntaje = puntaje
        self.tiempo_ms = tiempo_ms
        self.mejor_puntaje = mejor_puntaje

        self.fuente_titulo = pygame.font.Font(None, 92)
        self.fuente_dato = pygame.font.Font(None, 40)
        self.fuente_opcion = pygame.font.Font(None, 44)
        self.fuente_pie = pygame.font.Font(None, 26)

    # ------------------------------------------------------------------ #
    # Entrada
    # ------------------------------------------------------------------ #
    def manejar_evento(self, evento):
        """Procesa un evento. Devuelve "reiniciar", "salir" o None."""
        if evento.type == pygame.QUIT:
            return ACCION_SALIR
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_s:
                return ACCION_REINICIAR
            if evento.key == pygame.K_n:
                return ACCION_SALIR
        return ACCION_NINGUNA

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def dibujar(self, pantalla):
        """Se dibuja encima de la última escena de la partida."""
        velo = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
        velo.fill((10, 4, 8, 190))
        pantalla.blit(velo, (0, 0))

        titulo = self.fuente_titulo.render("GAME OVER", True, COLOR_PELIGRO)
        rect_titulo = titulo.get_rect(center=(ANCHO_PANTALLA // 2, 130))
        _sombra(titulo, pantalla, rect_titulo.topleft)
        pantalla.blit(titulo, rect_titulo)

        minutos = self.tiempo_ms // 60000
        segundos = (self.tiempo_ms % 60000) // 1000
        datos = [
            ("Puntaje", str(self.puntaje)),
            ("Tiempo sobrevivido", f"{minutos}:{segundos:02d}"),
            ("Mejor puntaje de la sesion", str(max(self.mejor_puntaje, self.puntaje))),
        ]
        y = 210
        for etiqueta, valor in datos:
            texto_etiqueta = self.fuente_pie.render(etiqueta, True, COLOR_TEXTO_SECUNDARIO)
            pantalla.blit(texto_etiqueta, texto_etiqueta.get_rect(midright=(390, y)))
            texto_valor = self.fuente_dato.render(valor, True, COLOR_TEXTO)
            pantalla.blit(texto_valor, texto_valor.get_rect(midleft=(410, y - 8)))
            y += 46

        # Aviso principal: se queda en pantalla hasta que el jugador decida.
        aviso = self.fuente_opcion.render("¿Que quieres hacer?", True, COLOR_ACENTO)
        pantalla.blit(aviso, aviso.get_rect(center=(ANCHO_PANTALLA // 2, 380)))

        opciones = [
            ("S", "Jugar de nuevo"),
            ("N", "Cerrar el juego"),
        ]
        x = 190
        for i, (tecla, accion) in enumerate(opciones):
            rect = pygame.Rect(x, 420, 190, 70)
            color_borde = COLOR_ACENTO if self._pulsando(i) else COLOR_PANEL_BORDE
            _panel(pantalla, rect, color=COLOR_PANEL, borde=color_borde, alpha=245)
            texto_tecla = self.fuente_opcion.render(tecla, True, COLOR_ACENTO)
            pantalla.blit(texto_tecla, texto_tecla.get_rect(center=(rect.x + 40, rect.centery)))
            texto_accion = self.fuente_pie.render(accion, True, COLOR_TEXTO)
            pantalla.blit(texto_accion, texto_accion.get_rect(center=(rect.x + 118, rect.centery)))
            x += 230

        pie = self.fuente_pie.render(
            "Pulsa S para volver a jugar   ·   Pulsa N para cerrar el juego",
            True, COLOR_TEXTO_SECUNDARIO,
        )
        pantalla.blit(pie, pie.get_rect(center=(ANCHO_PANTALLA // 2, 530)))

    def _pulsando(self, indice):
        """Alterna el resaltado entre las dos opciones para llamar la atencion."""
        return (pygame.time.get_ticks() // 400) % 2 == indice
