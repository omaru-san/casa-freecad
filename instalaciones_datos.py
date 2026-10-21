# Instalaciones eléctricas y sanitarias (metros, mismo sistema de coordenadas que casa_datos.py).
# PROPUESTA PRELIMINAR: debe ser revisada y firmada por un instalador eléctrico SEC y un proyectista sanitario.
# Casa TODO ELÉCTRICA: sin gas ni combustión (bomba de calor aire-agua + inducción). Cumplimiento: CUMPLIMIENTO_NORMATIVO.md

# ================= ELÉCTRICO (DS 8/2019 + pliegos RIC SEC) =================
# Diferenciales ≤ 30 mA en todo circuito de alumbrado y enchufes (RIC 10 5.1.3.5), máx. 3 circuitos por diferencial (5.1.3.7)
CIRCUITOS = [  # (código, destino, protección, conductor, fase · diferencial)
    # --- TDA-R: subtablero de RESPALDO, alimentado por la salida "backup" del inversor híbrido (sigue con corte de luz) ---
    ("C1", "Alumbrado P1 y terrazas (IP54)", "10 A curva B", "1,5 mm²", "R · IDR1"),
    ("C2", "Alumbrado P2 + detectores de humo", "10 A curva B", "1,5 mm²", "S · IDR1"),
    ("C13", "Ventilación VMC + rack red/domótica", "10 A curva C", "1,5 mm²", "R · IDR1"),
    ("C4", "Enchufes cocina (exclusivo, refrigerador)", "16 A curva C", "2,5 mm²", "R · IDR2"),
    ("C8", "Tablero caseta: presurizadora + bomba pozo", "16 A curva C", "2,5 mm²", "T · IDR2"),
    # --- TDA: tablero general (sólo con red o con sol) ---
    ("C3", "Enchufes living-comedor y exterior", "16 A curva C", "2,5 mm²", "S · ID1"),
    ("C6", "Enchufes dormitorios P2", "16 A curva C", "2,5 mm²", "T · ID1"),
    ("C7", "Enchufes oficinas 1 y 2", "16 A curva C", "2,5 mm²", "T · ID1"),
    ("C5", "Enchufes lavandería y baños", "16 A curva C", "2,5 mm²", "T · ID2"),
    ("C14", "Ventiloconvectores P2 + toallero baño P2", "10 A curva C", "1,5 mm²", "S · ID2"),
    ("C15", "Exterior: alumbrado, bodega y portón", "16 A curva C", "4 mm² (caída de tensión)", "T · ID2"),
    ("C9", "Encimera inducción (limitada a 4,6 kW)", "25 A curva C", "4 mm²", "R · ID3"),
    ("C10", "Horno eléctrico (exclusivo)", "16 A curva C", "2,5 mm²", "S · ID3"),
    ("C11", "Bomba de calor aire-agua (exterior)", "20 A curva C", "4 mm²", "S · ID4 tipo A"),
    ("C12", "Apoyo ACS + circuladores calefacción", "16 A curva C", "2,5 mm²", "T · ID4 tipo A"),
    ("EV", "Cargador auto 11 kW (RIC 15, TE6)", "3×16 A curva C", "5×4 mm²", "RST · tipo B"),
    ("FV", "Inversor híbrido 6 kW + batería (AFCI)", "3×16 A + DPS", "5×4 mm²", "RST · 100 mA"),
]
RESPALDO = ("C1", "C2", "C13", "C4", "C8")   # circuitos del TDA-R (respaldo con batería)
# Potencia instalada (W) y factor de demanda, para el cuadro de cargas del tablero (TAB-01).
POTENCIA = {
    "C1": (400, 1.0), "C2": (300, 1.0), "C13": (300, 1.0), "C4": (3000, 0.4), "C8": (1500, 0.7),
    "C3": (1500, 0.3), "C6": (1500, 0.3), "C7": (1500, 0.4), "C5": (2200, 0.5), "C14": (500, 1.0),
    "C15": (1000, 0.5), "C9": (4600, 0.7), "C10": (3000, 0.5), "C11": (2500, 1.0), "C12": (3000, 0.5),
    "EV": (11000, 1.0),
}
def demanda_fases():
    """Demanda por fase (W) sin el EV, para el cuadro de cargas (TAB-01) y la verificación normativa."""
    f = {"R": 0.0, "S": 0.0, "T": 0.0}
    for c in CIRCUITOS:
        if c[0] in POTENCIA and c[0] != "EV":
            w, fd = POTENCIA[c[0]]
            f[c[4].split(" ·")[0]] += w * fd
    return f


EMPALME_A = 25          # A por fase (empalme 3×25 A; se contrata 3×16 A)
CONTRATADO_A = 16
GENERAL = ("Empalme trifásico 3×25 A (contratar 3×16 A para mantener BT1 ≤ 10 kW) · general 4P 25 A · alimentador ≥ 6 mm² "
           "(apto 3×32 A) · TN-S, tierra ≤ 20 Ω · DPS tipo 1+2 (zona rural, línea aérea) · respaldo desde inversor híbrido: "
           "TDA-R con C1, C2, C4, C8, C13")

# luces: (x, y, circuito, tipo 'cielo' | 'muro')
LUCES_1 = [
    (2.00, 4.20, "C1", "cielo"),   # 0 living
    (4.50, 4.20, "C1", "cielo"),   # 1 comedor
    (6.80, 4.60, "C1", "cielo"),   # 2 cocina
    (3.20, 1.00, "C1", "cielo"),   # 3 oficina 1
    (5.30, 1.00, "C1", "cielo"),   # 4 baño
    (7.00, 1.00, "C1", "cielo"),   # 5 lavandería
    (10.05, 1.55, "C1", "cielo"),  # 6 escalera
    (8.75, 4.50, "C1", "cielo"),   # 7 despensa
    (10.75, 4.50, "C1", "cielo"),  # 8 oficina 2
    (9.00, 2.50, "C1", "cielo"),   # 9 pasillo
    (11.25, 2.50, "C1", "cielo"),  # 10 acceso
    (11.25, 1.00, "C1", "cielo"),  # 11 terraza entrada (bajo losa piso 2)
    (1.88, 1.00, "C1", "muro"),    # 12 aplique terraza
    (8.20, 1.00, "C1", "cielo"),   # 13 sala técnica
]
# interruptores: (x, y, tipo 'simple' | 'doble' | 'conmutador', [índices de luces que controla])
# RIC 10 5.2: cada centro con interruptor independiente (un efecto por luminaria). Altura 1,05 m (estatura 1,64 m).
INTERRUPTORES_1 = [
    (11.85, 2.17, "doble", [10, 11]),
    (11.85, 2.80, "simple", [9]),
    (1.90, 2.17, "doble", [0, 12]),
    (2.35, 2.17, "simple", [1]),
    (7.87, 5.00, "simple", [2]),
    (2.60, 1.83, "simple", [3]),
    (4.30, 2.17, "simple", [4]),
    (6.45, 1.83, "simple", [5]),
    (9.40, 2.17, "conmutador", [6]),
    (9.30, 3.15, "simple", [7]),
    (10.90, 3.15, "simple", [8]),
    (7.73, 1.20, "simple", [13]),
]
# enchufes: (x, y, circuito, 'IP' si es impermeable). Todos de alvéolos protegidos (RIC 10 5.1.2.8).
# Living/dormitorios: ≥ 1 doble por cada 8 m de perímetro; cocina ≥ 3; lavadero ≥ 1 (RIC 10 5.2).
# Baños: ningún enchufe en volúmenes 0, 1 y 2 (≥ 0,60 m del borde de la ducha; RIC 11 sección 6).
ENCHUFES_1 = [
    (0.12, 3.00, "C3", ""), (0.12, 5.20, "C3", ""), (3.50, 5.88, "C3", ""), (4.00, 2.12, "C3", ""),
    (1.88, 0.40, "C3", "IP"), (8.30, 2.12, "C3", ""), (11.95, 1.88, "C3", "IP"),
    (5.00, 5.88, "C4", ""), (7.75, 5.88, "C4", ""), (7.88, 4.00, "C4", ""), (8.75, 5.88, "C4", ""),
    (6.25, 5.88, "C10", ""),
    (6.08, 0.25, "C5", "IP"), (6.60, 0.12, "C5", "IP"), (7.68, 1.50, "C5", "IP"),
    (2.12, 1.00, "C7", ""), (4.28, 1.00, "C7", ""),
    (11.88, 3.40, "C7", ""), (11.88, 5.60, "C7", ""), (9.62, 4.50, "C7", ""),
]
TABLERO = (11.60, 2.88, "TDA")       # pasillo de acceso: no en dormitorio, baño, lavadero ni closet (RIC 10 5.1.3.2)
TABLERO_R = (10.95, 2.88, "TDA-R")   # subtablero de respaldo, junto al TDA (lo alimenta la salida backup del inversor)
MEDIDOR_ELEC = (10.62, 1.60, "MED")  # medidor bidireccional/empalme en terraza de entrada
ACOMETIDA = [(10.62, 1.60), (10.62, 2.45), (11.60, 2.45), (11.60, 2.88)]

LUCES_2 = [
    (2.90, 4.50, "C2", "cielo"),   # 0 dormitorio principal (A)
    (7.10, 4.50, "C2", "cielo"),   # 1 dormitorio 2
    (10.40, 4.50, "C2", "cielo"),  # 2 dormitorio 3
    (3.20, 1.50, "C2", "cielo"),   # 3 walk-in closet
    (6.10, 1.00, "C2", "cielo"),   # 4 baño
    (10.05, 1.55, "C2", "cielo"),  # 5 escalera (conmutada con piso 1)
    (6.80, 2.50, "C2", "cielo"),   # 6 pasillo
    (11.25, 1.50, "C2", "cielo"),  # 7 hall
    (4.60, 4.50, "C2", "cielo"),   # 8 dormitorio principal (B): recinto > 10 m² exige 2 centros
    (8.20, 1.00, "C2", "cielo"),   # 9 ropería
]
INTERRUPTORES_2 = [
    (4.40, 3.17, "doble", [0, 8]),
    (2.60, 2.83, "simple", [3]),
    (7.65, 3.17, "simple", [1]),
    (10.80, 3.17, "simple", [2]),
    (5.05, 2.17, "simple", [4]),
    (10.62, 1.20, "conmutador", [5]),
    (10.62, 1.65, "doble", [6, 7]),
    (8.62, 2.17, "simple", [9]),
]
ENCHUFES_2 = [
    (2.12, 3.60, "C6", ""), (2.12, 5.50, "C6", ""), (5.38, 4.50, "C6", ""),
    (5.62, 5.50, "C6", ""), (8.63, 4.00, "C6", ""), (8.63, 5.50, "C6", ""),
    (8.87, 4.50, "C6", ""), (11.88, 3.60, "C6", ""), (11.88, 5.50, "C6", ""),
    (4.28, 2.50, "C6", ""), (9.50, 2.88, "C6", ""), (5.30, 0.12, "C5", "IP"),
]
# conexiones fijas de equipos: (piso, x, y, circuito, sigla)
CONEXIONES_FIJAS = [
    (1, 5.80, 5.88, "C9", "IND"),    # encimera de inducción
    (1, 7.75, 0.70, "C12", "ACS"),   # resistencia de apoyo del acumulador ACS
    (1, 6.95, -0.15, "C11", "BC"),   # unidad exterior bomba de calor (muro sur, bajo alero)
    (1, 8.45, 2.12, "C12", "COL"),   # colector piso radiante P1 + circulador (el 2° piso no tiene piso radiante)
    (1, 11.88, 2.60, "C13", "RACK"), # rack red/domótica (Home Assistant) junto al tablero
    (2, 2.70, 0.45, "C13", "VMC"),   # recuperador de calor en walk-in closet
    (2, 2.30, 4.50, "C14", "FC"),    # ventiloconvector dorm. principal (ver especialidades_datos.FANCOILS)
    (2, 7.00, 3.25, "C14", "FC"),    # ventiloconvector dormitorio 2
    (2, 10.40, 5.75, "C14", "FC"),   # ventiloconvector dormitorio 3
    (2, 4.85, 1.80, "C14", "TOA"),   # toallero eléctrico baño P2
]
# Las canalizaciones del 2° piso suben desde el TDA por un ducto en el tabique del pasillo (mismo x, y)
MONTANTE_ELEC = (11.60, 2.88)
# detectores (piso, x, y, tipo): humo fotoeléctrico interconectado; térmico en cocina (evita falsas alarmas)
DETECTORES = [
    (1, 2.60, 3.40, "humo"), (1, 6.80, 3.60, "temp"), (1, 9.80, 2.50, "humo"),
    (2, 3.75, 5.10, "humo"), (2, 7.10, 5.10, "humo"), (2, 10.40, 5.10, "humo"),
    (2, 6.00, 2.50, "humo"), (2, 11.25, 0.90, "humo"),
]
# cargador de auto eléctrico en el estacionamiento (ver especialidades_datos.WALLBOX): sale del TDA por ducto enterrado
SALIDA_EV = (11.95, 2.30)

# ================= SANITARIO (RIDAA DS 50/2002 · DS 236) =================
# artefactos: (código, x, y, ancho, alto)  WC, LV lavamanos, DU ducha, LP lavaplatos, LD lavadero, LAV lavadora,
# ACS acumulador bomba de calor 300 L (Ø 0,60), IND encimera de inducción (sin gas)
ARTEFACTOS_1 = [
    ("WC", 4.85, 0.40, 0.40, 0.65), ("LV", 5.75, 0.30, 0.50, 0.40), ("DU", 5.75, 1.50, 0.80, 0.80),
    ("LAV", 6.60, 0.40, 0.60, 0.60), ("LD", 7.50, 1.05, 0.55, 0.60), ("ACS", 7.45, 0.40, 0.60, 0.60),
    ("LP", 7.00, 5.75, 0.80, 0.50), ("IND", 5.80, 5.70, 0.60, 0.52),
]
ARTEFACTOS_2 = [
    ("WC", 4.85, 0.40, 0.40, 0.65), ("LV", 5.90, 0.30, 1.00, 0.45), ("DU", 7.30, 0.70, 0.90, 1.20),
]
# cañerías: listas de polilíneas [(x, y), ...]
AF_1 = [  # agua fría (PPR/PEX), presión ≥ 14 m.c.a. en el artefacto más desfavorable
    [(11.00, -0.60), (7.65, -0.60), (7.65, 0.15), (4.55, 0.15)],    # matriz desde caseta de presurización
    [(7.20, 0.15), (7.20, 0.30)],                                    # alimentación acumulador ACS
    [(6.10, 0.15), (6.10, 1.50), (5.80, 1.50)],                      # ducha
    [(7.70, 0.15), (7.70, 1.90)],                                    # sube por el tabique lavandería|escalera
    [(7.88, 3.10), (7.88, 5.60), (7.30, 5.60)],                      # baja por el tabique cocina|despensa → lavaplatos
]
AC_1 = [  # agua caliente desde acumulador (con válvula mezcladora termostática a 45-48 °C)
    [(7.40, 0.30), (7.40, 0.25), (4.65, 0.25)],
    [(6.00, 0.25), (6.00, 1.40), (5.80, 1.40)],
    [(7.60, 0.30), (7.60, 1.90)],
    [(7.78, 3.10), (7.78, 5.50), (7.30, 5.50)],
]
# El agua fría y caliente NO va embutida en el radier (ahí está el piso radiante: una fuga obligaría a romperlo).
# Corre por la cámara técnica de los muros y cruza el pasillo por el ENTREPISO (sobre el cielo del P1), en PEX sin
# uniones dentro del entrepiso, con abrazaderas con goma (no transmite ruido) y registro en el cielo.
AF_1_ENTREPISO = [[(7.70, 1.90), (7.70, 2.30), (7.88, 2.30), (7.88, 3.10)]]
AC_1_ENTREPISO = [[(7.60, 1.90), (7.60, 2.40), (7.78, 2.40), (7.78, 3.10)]]
# Pasadas por el sobrecimiento: camisa de PVC un diámetro mayor, dejada antes de hormigonar (no se pica después).
PASADAS = [(7.65, 0.0, "Ø50"), (4.85, 0.0, "Ø160"), (4.55, 0.0, "Ø160"), (6.60, 0.0, "Ø75"), (7.00, 6.0, "Ø75"),
           (6.95, 0.0, "Ø40")]
AF_2 = [[(4.55, 0.15), (7.70, 0.15), (7.70, 0.70)]]
AC_2 = [[(4.65, 0.25), (7.60, 0.25), (7.60, 0.60)]]
SUBIDAS = [(4.55, 0.15, "AF"), (4.65, 0.25, "AC")]  # montantes a piso 2
# Circuito hidráulico de la bomba de calor (ida/retorno PE-RT Ø25 aislado): BC → acumulador/buffer → colectores P1 y P2
HIDRAULICO_1 = [
    [(6.95, -0.35), (6.95, 0.05), (7.15, 0.05), (7.15, 0.12)],       # BC exterior → acumulador ACS / válvula 3 vías
    [(7.15, 0.70), (7.15, 2.12), (8.45, 2.12)],                      # → colector P1 (y montante a colector P2)
]
VALVULA_TERMOSTATICA = (7.45, 0.85)   # mezcladora termostática a la salida del acumulador

ALC_1 = [  # alcantarillado (PVC sanitario), pendiente 3 % (RIDAA art. 88)
    [(4.85, 0.40), (4.85, -1.30)],                                      # WC  Ø110
    [(5.75, 1.50), (5.20, 1.50), (5.20, 0.75), (4.85, 0.75)],           # ducha Ø50
    [(5.75, 0.30), (5.75, 0.75), (5.20, 0.75)],                         # lavamanos Ø40
    [(4.55, 0.50), (4.55, -1.10), (4.85, -1.30)],                       # bajada piso 2 Ø110
    [(7.50, 1.05), (7.00, 1.05), (7.00, 0.75), (6.60, 0.75), (6.60, -1.30)],  # lavadero + lavadora Ø50
    [(7.00, 5.75), (7.00, 7.20), (-1.20, 7.20), (-1.20, -1.30)],         # cocina Ø50 -> Ø110 ext. (rodea por el norte)
    [(6.60, -1.30), (-1.20, -1.30), (-1.20, -2.60)],                     # colector exterior Ø110 hacia el oeste
]
# Sector rural sin colector: el terreno baja hacia el O-NO, la fosa séptica va aguas abajo (ver EMP-01)
CAMARAS = [(4.85, -1.30, "C.I.1"), (7.00, 7.20, "C.D."), (-1.20, 7.20, "C.I.3"), (-1.20, -1.30, "C.I.4")]
# C.D. = cámara desgrasadora (sólo recibe la cocina): retiene la grasa antes de la fosa; se limpia cada 2–3 meses.
UNION_DOMICILIARIA = (-1.20, -2.60)
SALIDA_TEXTO = "→ Fosa séptica + drenes (ver EMP-01)"
ALC_2 = [
    [(4.85, 0.40), (4.55, 0.50)],
    [(7.30, 0.70), (6.60, 0.70), (6.60, 0.85), (4.55, 0.85), (4.55, 0.50)],
    [(5.90, 0.30), (5.90, 0.85)],
]
BAJADA = (4.55, 0.50, "B.A.S. Ø110 + VENT. Ø75 a techo")

MEDIDOR_AGUA = (11.00, -0.60)  # llave de paso general + filtro; viene de la caseta de presurización (EMP-01)
TEXTO_AGUA = "Desde caseta: estanque 3.000 L + presurizadora"
SIGLA_AGUA = "LLP"
# posiciones de rótulos de cañerías (x, y)
ROTULO_COLECTOR = (-1.20, 2.50)
ROTULO_COCINA = (3.00, 7.20)
ROTULO_HIDRAULICO = (9.30, 1.75)
