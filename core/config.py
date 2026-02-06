import pygame

RES_LOGICA = (320, 180)
RES_FINESTRA = (1280, 720)
FPS = 60
FILE_MAPPA = "mappa_dungeon.json"

# UI Layout
SIDEBAR_WIDTH = 60
TOPBAR_HEIGHT = 25

TIPI_SUPERFICIE = {
    1: {"nome": "Erba", "colori": [(34, 100, 34), (45, 120, 45), (30, 80, 30)]},
    2: {"nome": "Sabbia", "colori": [(210, 180, 140), (194, 178, 128), (225, 198, 153)]},
    3: {"nome": "Roccia", "colori": [(80, 80, 80), (100, 100, 100), (60, 60, 60)]},
    4: {"nome": "Acqua", "colori": [(30, 60, 180), (40, 80, 200), (20, 50, 150)]}
}

# Aggiungi in config.py
MODES = ["ADD", "EDIT", "DELETE", "PAN", "FILL", "COLLISION"]

ZOOM_MIN = 0.5
ZOOM_MAX = 5.0