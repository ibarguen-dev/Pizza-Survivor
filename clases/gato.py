from .enemigo import Enemigo


class Gato(Enemigo):
    ancho = 54
    alto = 64
    velocidad = 0.7

    def __init__(self):
        super().__init__()
        self.cargar_imagen("assets/imagenes/gato.png")
