# Instalaciones eléctricas y de gasfitería (metros, mismo sistema de coordenadas que casa_datos.py).
# PROPUESTA PRELIMINAR: debe ser revisada y firmada por un instalador eléctrico SEC y un gasfiter autorizado.

# ================= ELÉCTRICO =================
CIRCUITOS = [  # (código, descripción, protección, conductor)
    ("C1", "Alumbrado piso 1 y exteriores", "10 A curva C", "1,5 mm² NYA/THHN"),
    ("C2", "Alumbrado piso 2", "10 A curva C", "1,5 mm² NYA/THHN"),
    ("C3", "Enchufes living, pasillo, exteriores", "16 A + dif. 30 mA", "2,5 mm²"),
    ("C4", "Enchufes cocina y despensa", "16 A + dif. 30 mA", "2,5 mm²"),
    ("C5", "Enchufes baños y lavandería (IP44)", "16 A + dif. 30 mA", "2,5 mm²"),
    ("C6", "Enchufes piso 2", "16 A + dif. 30 mA", "2,5 mm²"),
    ("C7", "Enchufes oficinas 1 y 2", "16 A + dif. 30 mA", "2,5 mm²"),
    ("C8", "Bomba pozo 0,75 kW + hidropack (respaldo)", "16 A curva D + dif.", "2,5 mm² + tierra"),
    ("FV", "Inversor híbrido 6 kW ↔ batería 11 kWh", "2×32 A + DPS AC/DC", "6 mm² AC · 6 mm² DC solar"),
]
GENERAL = "Automático general 2x32 A · Puesta a tierra ≤ 20 Ω · Subtablero de respaldo (C1, C2, C4, C8) alimentado por el inversor híbrido"

# luces: (x, y, circuito, tipo 'cielo' | 'muro')
LUCES_1 = [
    (2.00, 4.20, "C1", "cielo"),   # 0 living
    (4.50, 4.20, "C1", "cielo"),   # 1 comedor
    (6.80, 4.60, "C1", "cielo"),   # 2 cocina
    (3.20, 1.00, "C1", "cielo"),   # 3 oficina 1
    (5.30, 1.00, "C1", "cielo"),   # 4 baño
    (7.00, 1.00, "C1", "cielo"),   # 5 lavandería
    (9.15, 1.00, "C1", "cielo"),   # 6 escalera
    (8.75, 4.50, "C1", "cielo"),   # 7 despensa
    (10.75, 4.50, "C1", "cielo"),  # 8 oficina 2
    (9.00, 2.50, "C1", "cielo"),   # 9 pasillo
    (11.25, 2.50, "C1", "cielo"),  # 10 acceso
    (11.25, 1.00, "C1", "cielo"),  # 11 terraza entrada (bajo losa piso 2)
    (1.88, 1.00, "C1", "muro"),    # 12 aplique terraza
]
# interruptores: (x, y, tipo 'simple' | 'doble' | 'conmutador', [índices de luces que controla])
INTERRUPTORES_1 = [
    (11.85, 2.17, "doble", [9, 10, 11]),
    (1.90, 2.17, "doble", [0, 1, 12]),
    (7.87, 5.00, "simple", [2]),
    (2.60, 1.83, "simple", [3]),
    (4.30, 2.17, "simple", [4]),
    (6.45, 1.83, "simple", [5]),
    (9.40, 2.17, "conmutador", [6]),
    (9.30, 3.15, "simple", [7]),
    (10.90, 3.15, "simple", [8]),
]
# enchufes: (x, y, circuito, 'IP' si es impermeable)
ENCHUFES_1 = [
    (0.12, 3.00, "C3", ""), (0.12, 5.20, "C3", ""), (3.50, 5.88, "C3", ""), (4.00, 2.12, "C3", ""),
    (1.88, 0.40, "C3", "IP"), (8.30, 2.12, "C3", ""), (11.95, 1.88, "C3", "IP"),
    (5.80, 5.88, "C4", ""), (7.75, 5.88, "C4", ""), (7.88, 4.00, "C4", ""), (8.75, 5.88, "C4", ""),
    (6.08, 0.60, "C5", "IP"), (6.60, 0.12, "C5", "IP"), (7.68, 1.50, "C5", "IP"),
    (2.12, 1.00, "C7", ""), (4.28, 1.00, "C7", ""),
    (11.88, 3.40, "C7", ""), (11.88, 5.60, "C7", ""), (9.62, 4.50, "C7", ""),
]
TABLERO = (11.60, 2.88, "TDA")       # tablero de distribución (interior, junto al acceso)
MEDIDOR_ELEC = (10.62, 1.60, "MED")  # medidor/empalme en terraza de entrada
ACOMETIDA = [(10.62, 1.60), (10.62, 2.45), (11.60, 2.45), (11.60, 2.88)]

LUCES_2 = [
    (3.75, 4.50, "C2", "cielo"),   # 0 dormitorio principal
    (7.10, 4.50, "C2", "cielo"),   # 1 dormitorio 2
    (10.40, 4.50, "C2", "cielo"),  # 2 dormitorio 3
    (3.20, 1.50, "C2", "cielo"),   # 3 walk-in closet
    (6.10, 1.00, "C2", "cielo"),   # 4 baño
    (9.15, 1.00, "C2", "cielo"),   # 5 escalera (conmutada con piso 1)
    (6.80, 2.50, "C2", "cielo"),   # 6 pasillo
    (11.25, 1.50, "C2", "cielo"),  # 7 hall
]
INTERRUPTORES_2 = [
    (4.40, 3.17, "simple", [0]),
    (2.60, 2.83, "simple", [3]),
    (7.65, 3.17, "simple", [1]),
    (10.80, 3.17, "simple", [2]),
    (5.05, 2.17, "simple", [4]),
    (10.62, 1.20, "conmutador", [5, 6, 7]),
]
ENCHUFES_2 = [
    (2.12, 3.60, "C6", ""), (2.12, 5.50, "C6", ""), (5.38, 4.50, "C6", ""),
    (5.62, 5.50, "C6", ""), (8.63, 4.00, "C6", ""), (8.63, 5.50, "C6", ""),
    (8.87, 4.50, "C6", ""), (11.88, 3.60, "C6", ""), (11.88, 5.50, "C6", ""),
    (4.28, 2.50, "C6", ""), (9.50, 2.88, "C6", ""), (7.68, 1.00, "C5", "IP"),
]

# ================= GASFITERÍA =================
# artefactos: (código, x, y, ancho, alto)  WC, LV lavamanos, DU ducha, LP lavaplatos,
# LD lavadero, LAV lavadora, CAL calefont, COC cocina a gas
ARTEFACTOS_1 = [
    ("WC", 4.85, 0.40, 0.40, 0.65), ("LV", 5.75, 0.30, 0.50, 0.40), ("DU", 5.75, 1.50, 0.80, 0.80),
    ("LAV", 6.60, 0.40, 0.60, 0.60), ("LD", 7.50, 1.00, 0.55, 0.60), ("CAL", 7.50, 0.30, 0.38, 0.30),
    ("LP", 7.00, 5.75, 0.80, 0.50), ("COC", 5.80, 5.70, 0.60, 0.60),
]
ARTEFACTOS_2 = [
    ("WC", 4.85, 0.40, 0.40, 0.65), ("LV", 5.90, 0.30, 1.00, 0.45), ("DU", 7.30, 0.70, 0.90, 1.20),
]
# cañerías: listas de polilíneas [(x, y), ...]
AF_1 = [  # agua fría
    [(11.00, -0.60), (7.65, -0.60), (7.65, 0.15), (4.55, 0.15)],    # matriz desde medidor
    [(7.50, 0.15), (7.50, 0.30)],                                    # alimentación calefont
    [(6.10, 0.15), (6.10, 1.50), (5.80, 1.50)],                      # ducha
    [(7.70, 0.15), (7.70, 2.30), (7.88, 2.30), (7.88, 5.60), (7.30, 5.60)],  # lavadero + cocina
]
AC_1 = [  # agua caliente desde calefont
    [(7.40, 0.30), (7.40, 0.25), (4.65, 0.25)],
    [(6.00, 0.25), (6.00, 1.40), (5.80, 1.40)],
    [(7.60, 0.30), (7.60, 2.40), (7.78, 2.40), (7.78, 5.50), (7.30, 5.50)],
]
AF_2 = [[(4.55, 0.15), (7.70, 0.15), (7.70, 0.70)]]
AC_2 = [[(4.65, 0.25), (7.60, 0.25), (7.60, 0.60)]]
SUBIDAS = [(4.55, 0.15, "AF"), (4.65, 0.25, "AC")]  # montantes a piso 2

ALC_1 = [  # alcantarillado (PVC sanitario)
    [(4.85, 0.40), (4.85, -1.30)],                                      # WC  Ø110
    [(5.75, 1.50), (5.20, 1.50), (5.20, 0.75), (4.85, 0.75)],           # ducha Ø50
    [(5.75, 0.30), (5.75, 0.75), (5.20, 0.75)],                         # lavamanos Ø40
    [(4.55, 0.50), (4.55, -1.10), (4.85, -1.30)],                       # bajada piso 2 Ø110
    [(7.50, 1.00), (7.00, 1.00), (7.00, 0.75), (6.60, 0.75), (6.60, -1.30)],  # lavadero + lavadora Ø50
    [(7.00, 5.75), (7.00, 7.20), (-1.20, 7.20), (-1.20, -1.30)],         # cocina Ø50 -> Ø110 ext. (rodea por el norte)
    [(6.60, -1.30), (-1.20, -1.30), (-1.20, -2.60)],                     # colector exterior Ø110 hacia el oeste
]
# Sector rural sin colector: el terreno baja hacia el O-NO, la fosa séptica va aguas abajo (ver EMP-01)
CAMARAS = [(4.85, -1.30, "C.I.1"), (7.00, 7.20, "C.I.2"), (-1.20, 7.20, "C.I.3"), (-1.20, -1.30, "C.I.4")]
UNION_DOMICILIARIA = (-1.20, -2.60)
SALIDA_TEXTO = "→ Fosa séptica + drenes (ver EMP-01)"
ALC_2 = [
    [(4.85, 0.40), (4.55, 0.50)],
    [(7.30, 0.70), (6.60, 0.70), (6.60, 0.85), (4.55, 0.85), (4.55, 0.50)],
    [(5.90, 0.30), (5.90, 0.85)],
]
BAJADA = (4.55, 0.50, "B.A.S. Ø110 + VENT. Ø75 a techo")

GAS_1 = [
    [(12.30, -0.35), (7.50, -0.35), (7.50, 0.30)],                       # a calefont
    [(12.30, -0.35), (12.30, 6.60), (5.80, 6.60), (5.80, 5.70)],         # a cocina
]
MEDIDOR_AGUA = (11.00, -0.60)  # llegada desde el pozo: hidropack + filtro + UV
TEXTO_AGUA = "Desde pozo: hidropack 100 L + filtro + UV"
SIGLA_AGUA = "HP"
MEDIDOR_GAS = (12.30, -0.35)
# posiciones de rótulos de cañerías (x, y)
ROTULO_COLECTOR = (-1.20, 2.50)
ROTULO_COCINA = (3.00, 7.20)
ROTULO_GAS = (9.00, 6.60)
