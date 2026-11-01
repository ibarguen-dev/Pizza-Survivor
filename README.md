<h1 align="center">Pizza Survivor</h1>

<p align="center">
  <img src="https://img.shields.io/badge/STATUS-EN%20DESARROLLO-green">
  <img src="https://img.shields.io/badge/MIT%20License-FFFFFF">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=fff">
  <img src="https://img.shields.io/badge/pygame-2.6.1-FFD43B?logo=pygame&logoColor=fff">
</p>

<p align="center">
  Eres un repartidor de pizza. Reparte pizza, esquiva a los perros y a sus jefes
  y sobrevive todo el tiempo que puedas.
</p>

---

## 📖 Tabla de contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Controles](#-controles)
- [Instalación](#-instalación)
- [Ejecución](#-ejecución)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Mecánicas](#-mecánicas)
- [Configuración](#-configuración)
- [Pruebas](#-pruebas)
- [Compilar con PyInstaller](#-compilar-con-pyinstaller)
- [Roadmap](#-roadmap)
- [Licencia](#-licencia)

---

## 📖 Descripción

**Pizza Survivor** es un juego de supervivencia (*survivor*) en 2D hecho con
**Python** y **pygame**. Controlas a un repartidor de pizza que debe aguantar
el máximo tiempo posible mientras los perros (y sus jefes) lo persiguen. Las
pizzas se lanzan solas, así que tu trabajo es moverte, esquivar y gastar bien
los superpoderes que aparecen por el escenario.

El proyecto nació con fines **educativos**, como práctica de POO, máquina de
estados, colisiones y carga de recursos en pygame.

---

## ✨ Características

- **Menú principal** con opciones de *Iniciar partida*, *Instrucciones* y
  *Salir del juego*, navegable con teclado o ratón.
- **Panel de instrucciones** con scroll (rueda del ratón, `↑` `↓`, `AVP`/`REP`).
- **Ataque automático**: el repartidor lanza pizzas al enemigo más cercano
  cada 1,5 s.
- **Enemigos comunes** que entran desde los bordes de la pantalla:
  - 🐕 **Perro** — lento pero constante.
  - 🐈 **Gato** — más rápido que el perro.
- **Jefes** que aparecen cada ~3,5 minutos al azar, con barra de vida en
  pantalla, 5 vidas y proyectiles propios:
  - 🧟 **Perro zombi** — persigue e invoca jaurías de perros.
  - 🧟 **Zombie** — alterna persecución y descanso (aprovecha el descanso).
- **Jaurías** invocadas por el jefe perro zombi: avanzan en línea recta y no
  corrigen su dirección, así que se pueden esquivar.
- **Superpoderes** como recogibles que hay que tocar:
  - 🌊 **Onda perforante** — atraviesa a todos los enemigos de su recorrido y
    le quita una vida entera a los jefes.
  - 🛰️ **Órbita protectora** — un satélite orbita al repartidor y absorbe 3
    ataques.
  - ❤️ **Vida extra** — hasta un máximo de 5 vidas.
- **Cola de poderes** con 3 cargas por superpoder: se gasta primero el que
  recogiste antes; tocar uno que ya tienes recarga sus cargas.
- **Dificultad progresiva**: los enemigos aparecen más a menudo con el tiempo.
- **HUD** con vidas, puntaje, cronómetro, inventario de poderes y munición.
- **Game Over** con puntaje, tiempo sobrevivido y mejor puntaje de la sesión.
- **Música y efectos de sonido** (disparo, golpe, vida perdida).
- **Carga tolerante a fallos**: si falta una imagen, el juego avisa y dibuja un
  marcador de posición en lugar de romperse.

---

## 🎮 Controles

| Tecla | Acción |
|-------|--------|
| `↑` `↓` `←` `→` | Mover al repartidor |
| `ESPACIO` | Usar el superpoder que toque en la cola |
| `E` | Lanzar una pizza manual al jefe más cercano |
| `ESC` | Volver al menú principal (en partida) / salir (en menú) |
| `S` | Jugar de nuevo (pantalla de game over) |
| `N` | Cerrar el juego (pantalla de game over) |

En el menú: `↑` `↓` o `W` `S` para moverse, `ENTER` o `ESPACIO` para
confirmar, o clic con el ratón.

---

## 🛠️ Instalación

**Requisitos:** Python 3.10 o superior.

```bash
# 1. Clona el repositorio
git clone https://github.com/ibarguen-dev/Pizza-Survivor.git
cd Pizza-Survivor

# 2. Crea un entorno virtual (opcional pero recomendado)
python -m venv .venv

# Actívalo en Windows:
.venv\Scripts\activate
# Actívalo en macOS/Linux:
source .venv/bin/activate

# 3. Instala pygame
pip install pygame
```

---

## 🚀 Ejecución

```bash
python main.py
```

La partida empieza en el menú principal. El juego corre a **500 FPS**; si en
tu máquina va demasiado rápido, baja el valor de `FPS` en `clases/config.py`.

---

## 📁 Estructura del proyecto

```
Pizza-Survivor/
├── main.py                  # Punto de entrada: assets, música y máquina de estados
├── LICENSE
├── assets/
│   ├── imagenes/            # Sprites del juego
│   └── mp3/                 # Música y efectos de sonido
└── clases/
    ├── __init__.py
    ├── config.py            # Todas las constantes del juego
    ├── rutas.py             # Resolución de rutas (soporta PyInstaller)
    ├── recursos.py          # Carga de imágenes con reserva
    ├── juego.py             # Clase Juego: orquesta todos los sistemas
    ├── repartidor.py        # El jugador
    ├── enemigo.py           # Clase base de los enemigos
    ├── perro.py             # Enemigo Perro
    ├── gato.py              # Enemigo Gato
    ├── jauria.py            # Perros invocados (avanzan en línea recta)
    ├── jefe.py              # Clase base de los jefes
    ├── jefe_perro.py        # Jefe Perro zombi
    ├── jefe_zombie.py       # Jefe Zombie
    ├── pizza.py             # Proyectil automático
    ├── pizza_manual.py      # Proyectil manual (tecla E)
    ├── proyectil.py         # Clase base de proyectiles
    ├── proyectil_jefe.py    # Proyectil de los jefes
    ├── recogible.py         # Objeto que aparece y hay que tocar
    ├── onda_perforante.py   # Superpoder 1
    ├── orbita.py            # Superpoder 2
    ├── gestor_enemigos.py   # Spawn, movimiento y colisiones de enemigos
    ├── gestor_jefes.py      # Aparición y comportamiento de los jefes
    ├── gestor_pizzas.py     # Pizzas manuales
    ├── gestor_poderes.py    # Cola de poderes, recogida y activación
    ├── gestor_proyectiles.py# Proyectiles automáticos
    ├── gestor_estado.py     # Vidas, puntaje e invulnerabilidad
    └── ui.py                # Menú, instrucciones y pantalla de fin
```

### Arquitectura

Flujo de la aplicación (máquina de estados en `main.py`):

```
MENU  ──(ENTER / clic en "Iniciar partida")──▶  JUGANDO
  ▲                                                │
  │(ESC)                                   (se pierden todas las vidas)
  │                                                ▼
  └──────────────────────────────────────── FIN (game over)
                                   (S) ──▶ JUGANDO      (N) ──▶ salir
```

Cada partida es un objeto `Juego` independiente, así que reiniciar tras un
game over es simplemente crear otro: no queda residuo de enemigos, jefes,
poderes ni puntuación de la partida anterior.

---

## 🎮 Mecánicas

### Enemigos comunes

Los perros y los gatos aparecen desde un borde aleatorio de la pantalla y
persiguen al repartidor calculando la dirección con trigonometría. Cada
impacto de pizza los elimina de un solo golpe y suma **1 punto**.

### Jefes

Aparece **un jefe cada 3,5 minutos**, elegido al azar. Tiene 5 vidas y una
barra de vida en pantalla. Los jefes se mueven más lento que los enemigos
comunes, pero **disparan proyectiles** cada 3 s, así que quedarse quieto es
mortal.

El modelo de daño es peculiar: **cada proyectil es un impacto** y hacen falta
**3 impactos para quitar una vida** al jefe. La excepción es la onda perforante,
que le quita una vida entera de un golpe (pero se consume al tocarlo).

Las **pizzas manuales** (tecla `E`, con munición limitada) son la forma más
rápida de herir a los jefes.

### Superpoderes y recogibles

| Constante | Valor | Descripción |
|-----------|-------|-------------|
| `CARGAS_MAXIMAS_PODER` | 3 | Usos por superpoder |
| `VIDAS_MAXIMAS` | 5 | Tope de vidas |
| `VENTANA_VIDA_EXTRA` | 120000 ms | Durante los primeros 2 min también salen corazones |
| `RADIO_PERFORANTE` | 40 | Alcance de la onda |
| `RADIO_ORBITA` | 62 | Radio de la órbita |
| `ATAQUES_PROTEGIDOS` | 3 | Golpes que absorbe la órbita |
| `DURACION_ORBITA` | 15000 ms | Duración de la órbita |

Los recogibles aparecen cada 12–20 s (intervalo aleatorio) y hay que
tocarlos para recogerlos.

---

## ⚙️ Configuración

Todo el juego se ajusta desde **`clases/config.py`**. Algunos valores útiles:

```python
# Pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 500                 # Bájalo si el juego va demasiado rápido

# Repartidor
VELOCIDAD_REPARTIDOR = 1
VIDAS_INICIALES = 3

# Enemigos
INTERVALO_SPAWN_PERRO = 4000    # ms entre apariciones
INTERVALO_SPAWN_GATO = 5000

# Jefes
VIDAS_JEFE = 5
INTERVALO_APARICION_JEFE = 30000  # ms (3,5 min)
IMPACTOS_POR_VIDA_JEFE = 3

# Pizzas manuales
PIZZAS_MANUALES_MAXIMAS = 5
INTERVALO_RECARGA_PIZZA = 3500

# Audio
VOLUMEN_MUSICA = 0.3
VOLUMEN_SONIDOS = 0.7
```

### Añadir un enemigo nuevo

1. Crea `clases/mi_enemigo.py` heredando de `Enemigo`.
2. Impón `es_jefe = False` y define su comportamiento.
3. Añádelo en `Juego.__init__` con `gestor_enemigos.agregar_tipo(MiEnemigo, intervalo)`.
4. Pon su sprite en `assets/imagenes/`.

---

## ✅ Pruebas

Las pruebas son scripts independientes que se ejecutan con `python` y no
requieren pytest. Usan el driver de vídeo y audio *dummy*, así que pueden
correr en un entorno sin pantalla.

```bash
python prueba_interfaz.py     # Menú, instrucciones, scroll y teclas S/N del game over
python prueba_flujo.py        # Flujo completo: menú → partida → game over → S → N
python prueba_humo.py         # Bucle real de main.py con jefes, jauría y pizzas
python prueba_mecanicas.py    # Superpoderes, órbita y onda perforante
python prueba_jefes.py        # Jefes, jauría y pizzas manuales
```

---

## 📦 Compilar con PyInstaller

```bash
pip install pyinstaller
pyinstaller main.spec
```

El ejecutable queda en `dist/`. `clases/rutas.py` resuelve las rutas de los
recursos tanto en modo código fuente como en el ejecutable congelado
(`sys._MEIPASS`).

---

## 🗺️ Roadmap

- [x] Refactorización a POO con módulos por responsabilidad
- [x] Menú, instrucciones y pantalla de fin
- [x] Enemigos comunes, jefes y jaurías
- [x] Superpoderes, recogibles y vidas extra
- [x] Pizzas manuales y superpoder 1 (onda perforante)
- [ ] Menú para cambiar de repartidor
- [ ] Bonificaciones por tiempo jugado
- [ ] Ranking persistente de los mejores tiempos (high score en disco)
- [ ] Estado de pausa (`P`)
- [ ] Más tipos de enemigos y oleadas

---

## 📄 Licencia

Pizza Survivor © 2026 Juan Esteban Torres Ibarguen — [MIT License](LICENSE).
