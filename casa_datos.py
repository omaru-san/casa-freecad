# Datos geométricos de la casa (metros, a eje de muro). Editar aquí para ajustar medidas.
# Origen (0,0) = esquina inferior-izquierda de la terraza. X hacia la derecha, Y hacia arriba (norte del dibujo).
# Primer piso 12 x 6 m (incluye terrazas). Segundo piso 10 x 6 m.

import math as _m

EXT = 0.20   # espesor muro exterior
INT = 0.10   # espesor tabique interior

# Entrepiso de madera ACÚSTICO (el 2° piso no lleva piso radiante): piso flotante sobre lámina antiimpacto
# + cielo desacoplado con canal resiliente. Meta: ruido de pasos L'nT,w ≤ 55 dB (un entrepiso de madera
# simple da ~75 dB). De arriba hacia abajo: (capa, espesor m, peso kN/m²)
ENTREPISO = [
    ("Porcelanato símil madera 20×120 + adhesivo flexible C2S1", 0.012, 0.25),
    ("Piso flotante: 2 placas de yeso-fibra 12,5 mm encoladas", 0.025, 0.30),
    ("Lámina antiimpacto 10 mm (ΔLw ≥ 20 dB) + banda perimetral", 0.010, 0.02),
    ("OSB 18 mm machihembrado (diafragma estructural)", 0.018, 0.11),
    ("Vigas 2×10 @ 40 + lana mineral 100 mm en la cavidad", 0.235, 0.16),
    ("Canal resiliente 13 mm (el cielo no toca las vigas)", 0.013, 0.02),
    ("2 × yeso-cartón 12,5 mm (la primera RF)", 0.025, 0.20),
]
LOSA = round(sum(c[1] for c in ENTREPISO), 2)   # espesor total del entrepiso (0,34 m)
Z2 = 2.70                                       # nivel piso 2: 15 contrahuellas de 18 cm
H1 = round(Z2 - LOSA, 2)                        # altura libre piso 1 (2,36 m ≥ 2,30, OGUC 4.1.1)
H2 = 2.50

# ---------- PISO 1 ----------
# muros: (x1, y1, x2, y2, espesor)
MUROS_1 = [
    (0, 2, 0, 6, EXT),
    (0, 6, 12, 6, EXT),
    (12, 6, 12, 2, EXT),
    (12, 2, 10.5, 2, EXT),
    (10.5, 2, 10.5, 0, EXT),
    (10.5, 0, 2, 0, EXT),
    (2, 0, 2, 2, EXT),
    (2, 2, 0, 2, EXT),
    (2, 2, 10.5, 2, INT),    # living/pasillo | franja de servicios
    (4.4, 0, 4.4, 2, INT),   # oficina 1 | baño
    (6.2, 0, 6.2, 2, INT),   # baño | lavandería
    (7.8, 0, 7.8, 2, INT),   # lavandería | sala técnica
    (8.6, 0, 8.6, 2, INT),   # sala técnica | escalera
    (8, 3, 8, 6, INT),       # cocina | despensa
    (8, 3, 12, 3, INT),      # despensa/oficina 2 | pasillo
    (9.5, 3, 9.5, 6, INT),   # despensa | oficina 2
]
# puertas: (x, y centro sobre el muro, ancho, orientación 'h'/'v', apertura +1/-1 hacia +y/+x o -y/-x, 0 = vano)
PUERTAS_1 = [
    (11.25, 2, 0.90, 'h', 1),  # acceso principal desde terraza entrada
    (1.00, 2, 1.40, 'h', 1),   # living -> terraza (doble)
    (3.20, 2, 0.80, 'h', -1),  # oficina 1
    (4.85, 2, 0.70, 'h', -1),  # baño
    (7.00, 2, 0.70, 'h', -1),  # lavandería
    (7.8, 1.65, 0.60, 'v', 1), # sala técnica desde la lavandería (gatera con microchip en la hoja)
    (10.00, 2, 0.90, 'h', 0),  # escalera (vano)
    (8.75, 3, 0.70, 'h', 1),   # despensa
    (10.30, 3, 0.80, 'h', 1),  # oficina 2
]
# ventanas: (x, y, ancho, orient, alto antepecho, alto ventana)
VENTANAS_1 = [
    (2.00, 6, 2.00, 'h', 0.90, 1.30),
    (5.00, 6, 2.00, 'h', 0.90, 1.30),
    (7.00, 6, 1.20, 'h', 1.10, 1.00),   # cocina (sobre lavaplatos)
    (10.75, 6, 1.20, 'h', 0.90, 1.30),  # oficina 2
    (0, 4.00, 1.50, 'v', 0.90, 1.30),
    (12, 4.50, 1.20, 'v', 0.90, 1.30),
    (3.20, 0, 1.20, 'h', 0.90, 1.30),   # oficina 1
    (5.30, 0, 0.60, 'h', 1.60, 0.50),   # baño
    (7.00, 0, 0.80, 'h', 1.30, 0.80),   # lavandería
]
RECINTOS_1 = [  # (nombre, x0, y0, x1, y1)
    ("LIVING / COCINA", 0, 2, 8, 6), ("TERRAZA", 0, 0, 2, 2), ("OFICINA 1", 2, 0, 4.4, 2),
    ("BAÑO", 4.4, 0, 6.2, 2), ("LAVANDERÍA", 6.2, 0, 7.8, 2), ("SALA TÉCNICA", 7.8, 0, 8.6, 2),
    ("ESCALERA", 8.6, 0, 10.5, 2), ("TERRAZA ENTRADA", 10.5, 0, 12, 2), ("DESPENSA", 8, 3, 9.5, 6),
    ("OFICINA 2", 9.5, 3, 12, 6), ("PASILLO", 8, 2, 12, 3),
]
ETIQUETA_LIVING = (3.2, 3.0)  # posición de la etiqueta del living (lejos de las luminarias)

# ---------- PISO 2 ----------
MUROS_2 = [
    (2, 0, 12, 0, EXT),
    (12, 0, 12, 6, EXT),
    (12, 6, 2, 6, EXT),
    (2, 6, 2, 0, EXT),
    (2, 3, 12, 3, INT),        # dormitorios | pasillo/closet
    (5.5, 3, 5.5, 6, INT),     # dorm 1 | dorm 2
    (8.75, 3, 8.75, 6, INT),   # dorm 2 | dorm 3
    (4.4, 0, 4.4, 3, INT),     # closet | baño/pasillo
    (4.4, 2, 10.5, 2, INT),    # pasillo | baño/escalera
    (7.8, 0, 7.8, 2, INT),     # baño | ropería
    (8.6, 0, 8.6, 2, INT),     # ropería | escalera
    (10.5, 0, 10.5, 2, INT),   # escalera | hall
]
PUERTAS_2 = [
    (3.20, 3, 0.80, 'h', -1),   # dorm principal -> walk-in closet
    (5.00, 3, 0.80, 'h', 1),    # dorm principal
    (8.25, 3, 0.80, 'h', 1),    # dorm 2
    (11.40, 3, 0.80, 'h', 1),   # dorm 3
    (5.60, 2, 0.70, 'h', -1),   # baño desde pasillo
    (8.20, 2, 0.60, 'h', -1),   # ropería desde pasillo
    (4.4, 1.50, 0.70, 'v', 1),  # baño desde closet
    (10.5, 0.55, 0.85, 'v', 0), # llegada escalera
]
# Piso 2: antepecho 1,00 m (≥ 0,95 m del art. 4.2.7 OGUC, aplicado por seguridad de la bebé y los gatos)
# + limitador de apertura 10 cm en hojas practicables. Dormitorios con ≥ 1,5 m libres frente a la ventana (OGUC 4.1.2).
VENTANAS_2 = [
    (3.75, 6, 1.50, 'h', 1.00, 1.30),
    (7.10, 6, 1.50, 'h', 1.00, 1.30),
    (10.40, 6, 1.50, 'h', 1.00, 1.30),
    (2, 4.50, 1.20, 'v', 1.00, 1.30),
    (12, 4.50, 1.20, 'v', 1.00, 1.30),
    (2, 1.50, 0.80, 'v', 1.30, 0.80),     # closet
    (6.00, 0, 0.60, 'h', 1.60, 0.50),     # baño
    (11.25, 0, 1.00, 'h', 1.00, 1.30),    # hall
]
RECINTOS_2 = [
    ("DORMITORIO PRINCIPAL", 2, 3, 5.5, 6), ("DORMITORIO 2", 5.5, 3, 8.75, 6),
    ("DORMITORIO 3", 8.75, 3, 12, 6), ("WALK-IN CLOSET", 2, 0, 4.4, 3),
    ("BAÑO", 4.4, 0, 7.8, 2), ("ROPERÍA", 7.8, 0, 8.6, 2), ("ESCALERA", 8.6, 0, 10.5, 2),
    ("PASILLO", 4.4, 2, 12, 3),
    ("", 10.5, 0, 12, 2),  # hall de llegada (sin etiqueta)
]
EXTERIORES = ("TERRAZA", "TERRAZA ENTRADA")

# Losas (rectángulos x0, y0, x1, y1)
LOSA_1 = [(0, 2, 12, 6), (2, 0, 10.5, 2)]
TERRAZAS = [(0, 0, 2, 2), (10.5, 0, 12, 2)]
LOSA_2 = (2, 0, 12, 6)
TECHO_1 = (0, 2, 2, 6)  # parte del living sin segundo piso encima
HUECO_ESCALERA = (8.65, 0.05, 10.45, 1.95)   # cuadrado que circunscribe la helicoidal
COLUMNAS_1 = [(12, 0, 0.20)]  # pilar H.A. bajo la esquina del piso 2 que vuela sobre la terraza de entrada

# ---------- ESCALERA HELICOIDAL Ø 1,80 m (15 contrahuellas de 18 cm; ver lámina ESC-01) ----------
# Se entra desde el pasillo del P1 por el vano norte y el primer peldaño queda de frente (la primera arista,
# a 0°, corre E–O). Sube en sentido horario, pasa bajo los peldaños altos (altura libre ≥ 2,10 m) y llega al
# P2 a 24°: un descanso de losa (de 24° a −48°) lleva al hall por el mismo vano este. Libera la franja
# x 7,80–8,60, que pasa a ser sala técnica (P1) y ropería (P2).
CONTRAHUELLA = Z2 / 15
ESC_CENTRO = (9.55, 1.00)
ESC_R, ESC_NUCLEO = 0.90, 0.08          # radio exterior del peldaño y del pilar central de acero
ESC_PASO = 24.0                         # grados por peldaño (14 peldaños = 336°)
ESC_LINEA = 0.60                        # línea de huella (2/3 del radio)
HUELLA = round(ESC_LINEA * _m.radians(ESC_PASO), 3)


def _pt(ang, r):
    return (ESC_CENTRO[0] + r * _m.cos(_m.radians(ang)), ESC_CENTRO[1] + r * _m.sin(_m.radians(ang)))


def _sector(a0, a1, n=6):
    """Peldaño entre los ángulos a0 y a1 (grados), del pilar al borde exterior."""
    arco = [_pt(a0 + (a1 - a0) * k / n, ESC_R) for k in range(n + 1)]
    return [_pt(a0, ESC_NUCLEO)] + arco + [_pt(a1, ESC_NUCLEO)]


def sector_peldanos(k0, k1):
    """Planta del espacio bajo los peldaños k0..k1 (guardado oculto bajo la helicoidal)."""
    return _sector(-(k0 - 1) * ESC_PASO, -k1 * ESC_PASO, n=4 * (k1 - k0 + 1))


ESCALONES = [(_sector(-(k - 1) * ESC_PASO, -k * ESC_PASO), k * CONTRAHUELLA) for k in range(1, 15)]  # (polígono, z_sup)
_FIN = 360 - 14 * ESC_PASO              # ángulo de llegada al P2 (24°)
# descanso del P2 (losa a +Z2): de la llegada hasta el borde de los peldaños 1–2, que tienen altura libre ≥ 2,0 m
_A_DESC = -2 * ESC_PASO
DESCANSO_P2 = [_pt(_FIN, ESC_NUCLEO), (10.45, ESC_CENTRO[1] + (10.45 - ESC_CENTRO[0]) * _m.tan(_m.radians(_FIN))),
               (10.45, 0.05), (ESC_CENTRO[0] + (ESC_CENTRO[1] - 0.05) / _m.tan(_m.radians(-_A_DESC)), 0.05),
               _pt(_A_DESC, ESC_NUCLEO)]
FLECHA_ESCALERA = [(10.05, 1.85), _pt(0, ESC_LINEA)] + [_pt(-a, ESC_LINEA) for a in range(10, 341, 10)]
ALTURA_LIBRE = round(min(H1 - 2 * CONTRAHUELLA,                     # bajo el descanso del P2
                         12 * CONTRAHUELLA - 0.06), 2)               # al entrar, bajo los peldaños 12–14

# ---------- COTAS: (valores, coordenada fija, eje 'x'|'y', desplazamiento mm) ----------
COTAS_1 = [
    ([0, 8, 9.5, 12], 6, "x", 7), ([0, 12], 6, "x", 13),
    ([0, 2, 4.4, 6.2, 7.8, 8.6, 10.5, 12], 0, "x", -7),
    ([0, 2, 3, 6], 12, "y", 7), ([2, 6], 0, "y", -7), ([0, 6], 0, "y", -13),
]
COTAS_2 = [
    ([2, 5.5, 8.75, 12], 6, "x", 7), ([2, 12], 6, "x", 13),
    ([2, 4.4, 7.8, 8.6, 10.5, 12], 0, "x", -7),
    ([0, 2, 3, 6], 12, "y", 7), ([0, 6], 2, "y", -7),
]
