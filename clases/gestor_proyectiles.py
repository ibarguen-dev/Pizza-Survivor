from clases.config import ANCHO_PANTALLA, ALTO_PANTALLA


class GestorProyectiles:
    def __init__(self, clase_proyectil):
        self.proyectiles = []
        self.clase_proyectil = clase_proyectil

    def lanzar(self, x, y, objetivo_x, objetivo_y):
        proyectil = self.clase_proyectil(x, y, objetivo_x, objetivo_y)
        self.proyectiles.append(proyectil)

    def actualizar(self):
        for p in self.proyectiles:
            p.mover()
        # Eliminar los que salieron de pantalla
        self.proyectiles = [
            p for p in self.proyectiles
            if not p.esta_fuera_de_pantalla(ANCHO_PANTALLA, ALTO_PANTALLA)
        ]

    def detectar_colisiones_enemigos(self, gestor_enemigos):
        eliminados = []
        for i, proyectil in enumerate(self.proyectiles):
            if gestor_enemigos.detectar_colision_proyectil(proyectil):
                eliminados.append(i)
        for i in reversed(eliminados):
            self.proyectiles.pop(i)
        return len(eliminados)

    def dibujar(self, pantalla):
        for p in self.proyectiles:
            p.dibujar(pantalla)
