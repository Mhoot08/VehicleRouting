# config.py
import tkinter as tk
from tkinter import ttk

TIMEWINDOW = False
RECUIT = True
TABOU = False
DESCENTE = False

RECUIT_ALPHA = 0.95
RECUIT_TEMPERATURE_INITIALE = 3
RECUIT_N2 = 50000

TABOU_TAILLE_LISTE_TABOU = 10
TABOU_NOMBRE_ITERATIONS = 100

DESCENTE_NOMBRE_ITERATIONS = 100

NOMBRE_CAMIONS = 10

NOMBRE_LANCERS = 10
NOMBRE_CLIENTS = 30

OPERATEURS = ["relocate_intra", "exchange_intra", "exchange_extra", "relocate_extra", "cross_exchange", "rotate_camion"]


