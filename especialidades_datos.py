# Techumbre, fotovoltaico, aguas lluvias, ventilación/calefacción y emplazamiento.
# Coordenadas en metros, mismo sistema que casa_datos.py. +Y = NORTE GEOGRÁFICO.
# Los valores de diseño salen de sitio/clima_sitio.json (ver sitio/INFORME_SITIO.md).
import json
import math
import os

import casa_datos as D


def num_s(v):
    return f"{v:.1f}".replace(".", ",")


_AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_AQUI, "sitio", "clima_sitio.json"), encoding="utf-8") as _f:
    CLIMA = json.load(_f)

# ================= TECHUMBRE =================
PENDIENTE = 35.0                     # grados; óptimo FV del sitio (PVGIS) y buena evacuación de lluvia
TAN = math.tan(math.radians(PENDIENTE))
COS = math.cos(math.radians(PENDIENTE))
ALERO = 0.60                         # alero norte/sur (protege fachada norte de lluvia con viento N-NO)
ALERO_LAT = 0.40                     # alero en frontones este/oeste
Z_ALERO_MURO = D.Z2 + D.H2           # nivel de apoyo de la techumbre sobre muros del piso 2
CUMBRERA_Y = 3.0                     # cumbrera este-oeste, centrada
TECHO_X = (2 - ALERO_LAT, 12 + ALERO_LAT)
TECHO_Y = (0 - ALERO, 6 + ALERO)
Z_CUMBRERA = Z_ALERO_MURO + (CUMBRERA_Y - 0) * TAN
Z_BORDE_ALERO = Z_ALERO_MURO - ALERO * TAN

# Techo bajo sobre el sector del living sin segundo piso (a un agua, cae al oeste)
TECHO_BAJO = {"x": (-0.50, 2.0), "y": (1.60, 6.60), "z_alto": 3.30, "z_bajo": 2.85}  # ≈ 10° (mín. recomendable para zinc ondulado)
TECHO_BAJO["pendiente"] = math.degrees(math.atan((TECHO_BAJO["z_alto"] - TECHO_BAJO["z_bajo"]) / 2.5))

# Canaletas (y o x fijo) y bajadas de aguas lluvias
CANALETAS = [
    {"nombre": "Canaleta norte", "pts": [(TECHO_X[0], TECHO_Y[1]), (TECHO_X[1], TECHO_Y[1])],
     "area_m2": (TECHO_X[1] - TECHO_X[0]) * (TECHO_Y[1] - CUMBRERA_Y)},
    {"nombre": "Canaleta sur", "pts": [(TECHO_X[0], TECHO_Y[0]), (TECHO_X[1], TECHO_Y[0])],
     "area_m2": (TECHO_X[1] - TECHO_X[0]) * (CUMBRERA_Y - TECHO_Y[0])},
    {"nombre": "Canaleta techo bajo", "pts": [(TECHO_BAJO["x"][0], TECHO_BAJO["y"][0]), (TECHO_BAJO["x"][0], TECHO_BAJO["y"][1])],
     "area_m2": (TECHO_BAJO["x"][1] - TECHO_BAJO["x"][0]) * (TECHO_BAJO["y"][1] - TECHO_BAJO["y"][0])},
]
BAJADAS = [  # (x, y, destino)
    (1.75, 6.60, "estanque"), (12.25, 6.60, "estanque"),
    (1.75, -0.60, "infiltración"), (12.25, -0.60, "infiltración"),
    (-0.50, 6.45, "estanque"),
]
# Intensidad de diseño: IDF Valdivia-Pichoy (DGA, vía tesis UACh 2008), T = 10 años, duración 5 min
I_DISENO = 66  # mm/h


def caudal_ls(area_m2, i_mm_h=I_DISENO, c=0.95):
    return c * i_mm_h * area_m2 / 3600.0


# ================= FOTOVOLTAICO =================
PANEL = {"modelo": "Monocristalino bifacial 625 Wp (2,38 × 1,13 m)", "wp": 625, "largo": 2.382, "ancho": 1.134}
# 12 paneles en horizontal (apaisados): 3 filas × 4 sobre el faldón norte (4,39 m de largo inclinado)
PANELES_POR_FILA = 4
FILAS_S = [(0.30 + k * (PANEL["ancho"] + 0.03), 0.30 + k * (PANEL["ancho"] + 0.03) + PANEL["ancho"]) for k in range(3)]
_x0 = 7.0 - (PANELES_POR_FILA * PANEL["largo"] + (PANELES_POR_FILA - 1) * 0.02) / 2
PANELES = []  # (x0, x1, s0, s1, etapa)
for fila, (s0, s1) in enumerate(FILAS_S):
    for k in range(PANELES_POR_FILA):
        xa = _x0 + k * (PANEL["largo"] + 0.02)
        PANELES.append((xa, xa + PANEL["largo"], s0, s1, 1))
ETAPA1_KWP = sum(1 for p in PANELES if p[4] == 1) * PANEL["wp"] / 1000
TOTAL_KWP = len(PANELES) * PANEL["wp"] / 1000
_PV = CLIMA["fotovoltaico_pvgis"]["por_inclinacion"][str(int(PENDIENTE))]
PRODUCCION_KWH_KWP_MES = _PV["kwh_mensual_por_kwp"]
PRODUCCION_KWH_KWP_ANUAL = _PV["kwh_anual_por_kwp"]
# Sala técnica junto a la escalera, x 7,80–8,60 (interior, protegida de heladas: LiFePO4 no carga bajo 0 °C)
INVERSOR = (8.20, 1.80, "INV")   # inversor HÍBRIDO 6 kW, en el muro norte
BATERIA = {"kwh": 11.0, "x": 8.20, "y": 0.25, "tipo": "LiFePO4 11 kWh, 51,2 V"}
CONSUMO_ESTIMADO_KWH_MES = 640    # casa todo eléctrica + bomba de calor + pozo (ver calculo/fv_bateria.py)


def panel_a_planta(x0, x1, s0, s1):
    """Proyección en planta de un panel sobre el faldón norte."""
    return x0, CUMBRERA_Y + s0 * COS, x1, CUMBRERA_Y + s1 * COS


# ================= COSECHA DE AGUAS LLUVIAS =================
AREA_CAPTACION = CANALETAS[0]["area_m2"] + CANALETAS[2]["area_m2"]  # faldón norte + techo bajo -> estanque
ESTANQUE = {"x": 13.6, "y": 6.0, "litros": 5000}
COEF_ESCORRENTIA = 0.85

# ================= VENTILACIÓN / CALEFACCIÓN (casa todo eléctrica, sin combustión) =================
# flechas de ventilación cruzada natural para verano (piso, [(x,y),...])
VENT_CRUZADA = [
    (1, [(2.0, 5.7), (2.0, 4.0), (1.0, 2.6)]),       # living norte -> puerta terraza sur
    (1, [(5.0, 5.7), (5.0, 3.6), (8.9, 2.5), (11.25, 2.3)]),  # living norte -> acceso
    (1, [(10.75, 5.7), (11.6, 4.5)]),                # oficina 2 norte-este
    (2, [(3.75, 5.7), (3.75, 3.4), (2.6, 1.5)]),     # dorm principal -> closet
    (2, [(7.1, 5.7), (7.1, 3.6), (8.25, 3.1), (9.5, 2.5), (11.0, 2.5), (11.25, 0.4)]),  # dorm 2 -> hall sur
    (2, [(10.4, 5.7), (11.4, 3.3), (11.6, 2.5), (11.6, 0.4)]),   # dorm 3 -> hall sur
]
# Ventilación mecánica controlada de doble flujo con recuperador de calor (VMC). Caudal NCh 3309 (vía ECSV Tomo I):
# Q = 0,15 L/s·m² × 125 m² + 3,5 L/s × (3 dormitorios + 1) ≈ 33 L/s → diseño 35 L/s (126 m³/h), balanceado.
VMC = {"piso": 2, "x": 2.70, "y": 0.45, "w": 0.80, "h": 0.60, "caudal_ls": 35,
       "texto": "VMC doble flujo, recuperación ≥ 80 %, 150–200 m³/h, bypass de verano, filtros F7/M5",
       "toma": (2.0, 0.25), "expulsion": (2.0, 0.85)}   # por muro oeste del closet (separadas ≥ 0,6 m)
# rejillas: (piso, tipo 'IM' impulsión | 'EX' extracción, x, y, L/s, recinto)
REJILLAS = [
    (1, "IM", 2.00, 3.60, 10, "Living"), (1, "IM", 3.20, 1.40, 4, "Oficina 1"), (1, "IM", 10.75, 4.00, 4, "Oficina 2"),
    (2, "IM", 3.75, 5.10, 7, "Dorm. principal"), (2, "IM", 7.10, 5.10, 5, "Dormitorio 2"), (2, "IM", 10.40, 5.10, 5, "Dormitorio 3"),
    (1, "EX", 7.20, 4.20, 10, "Cocina"), (1, "EX", 5.00, 1.65, 10, "Baño P1"), (1, "EX", 6.55, 1.55, 3, "Lavandería"),
    (1, "EX", 8.20, 1.10, 2, "Sala técnica (arenero)"),
    (2, "EX", 6.60, 1.60, 10, "Baño P2"),
]
# elementos: (piso, código, x, y, texto)
ELEMENTOS_VENT = [
    (1, "CA", 5.80, 5.75, "Campana inducción, ducto Ø150 a muro norte con clapeta + aire de compensación"),
    (1, "BC", 6.95, -0.55, "Bomba de calor aire-agua monobloc ~6 kW (R290), muro sur bajo alero"),
    (1, "AC", 7.45, 0.40, "Acumulador ACS 300 L + válvula mezcladora termostática 45 °C"),
    (1, "CO", 8.45, 2.12, "Colector piso radiante P1 (caudalímetros + actuadores)"),
    (1, "DH", 7.50, 1.70, "Lavandería: secadora con bomba de calor (sin evacuación) o tendido con deshumidificador"),
    (2, "CF", 8.45, 2.12, "Distribuidor de los ventiloconvectores P2 (ida/retorno PE-RT Ø20 por el entrepiso)"),
    (2, "VT", 4.55, 0.50, "Ventilación B.A.S. Ø75 sobre cubierta"),
]
# Piso radiante SÓLO EN EL 1er PISO: zonas (piso, x0, y0, x1, y1, nombre) — PE-Xa/PE-RT 16 mm c/ barrera O₂, paso 15 cm
ZONAS_RADIANTE = [
    (1, 0.25, 2.25, 7.75, 5.75, "Living-cocina"), (1, 2.25, 0.25, 4.15, 1.75, "Oficina 1"),
    (1, 4.65, 0.25, 5.95, 1.75, "Baño"), (1, 9.75, 3.25, 11.75, 5.75, "Oficina 2"), (1, 8.25, 2.20, 11.75, 2.80, "Pasillo"),
]
# 2° piso SIN piso radiante (entrepiso seco y acústico, ver casa_datos.ENTREPISO): ventiloconvectores (fancoils) de
# consola baja conectados a la MISMA bomba de calor, a la misma temperatura de impulsión (35 °C) → no baja el SCOP.
# Silenciosos (≤ 25 dB(A) en velocidad mínima), termostato por dormitorio. En verano pueden refrescar (bandeja de condensado).
# (piso, x, y, orientación del muro 'h'|'v', recinto) — ubicados donde no chocan con los muebles de interiorismo_datos.py
FANCOILS = [
    (2, 2.15, 4.50, "v", "Dorm. principal"),   # bajo la ventana oeste (antepecho 1,00 m)
    (2, 7.00, 3.12, "h", "Dormitorio 2"),      # muro sur, entre el clóset y la puerta
    (2, 10.40, 5.88, "h", "Dormitorio 3"),     # bajo la ventana norte (la cuna queda lejos)
]
FANCOIL_TXT = "Ventiloconvector consola baja 0,8–1,2 kW a 35 °C, ≤ 25 dB(A), termostato por recinto"
TOALLERO_P2 = (2, 4.85, 1.90, "Toallero eléctrico 300 W con temporizador (baño P2)")
T_IMPULSION = 35   # °C en diseño (exterior −4,5 °C); curva climática 28–35 °C
PASO_TUBO = 0.15   # m
EFICIENCIA_VMC = 0.80
N50_META = 3.0     # ren/h a 50 Pa (exigido ≤ 5,0 en provincia de Valdivia)
SCOP_BC = 3.5

# ================= PLATAFORMA (decisión del usuario 20-10-2026) =================
# La casa se emplaza en un sector PLANO del terreno: no hay corte ni relleno compensado. El DEM de ~30 m
# (sitio/topografia.json) no tiene resolución para ver ese sector; la topografía real lo confirmará.
PLATAFORMA_NIVELADA = True
ESCARPE = 0.25          # m de capa vegetal que se retira bajo la plataforma (suelo orgánico)
BASE_GRANULAR = 0.15    # m de grava compactada bajo el radier (además de la grava de 10 cm del piso)

# ================= EMPLAZAMIENTO (m, mismo origen) =================
SITIO = CLIMA["sitio"]
NORTE_MAGNETICO_DEG = 7  # declinación aproximada (E); verificar en terreno
ACCESO = [(30.0, -3.5), (16.0, -3.5), (12.6, -1.0), (11.25, -0.2)]  # desde camino vecinal (este)
ESTACIONAMIENTO = (12.5, -10.5, 18.5, -5.0)   # 2 autos: 6,0 × 5,5 m, ripio compactado (permeable)
WALLBOX = (15.5, -5.2)                        # cargador 11 kW en poste, IP54 (RIC 15), cable recogido ≥ 10 cm del suelo
DUCTO_EV = [(12.0, 2.30), (12.6, 2.30), (12.6, -4.6), (15.5, -4.6), (15.5, -5.2)]  # ducto enterrado PVC Ø40
CASETA_AGUA = (13.2, 1.0, 15.4, 3.2)          # estanque AP 3.000 L + presurizadora VSD + filtros + UV (ver TRATAMIENTO_AGUA)
# Defensa contra incendio forestal (CONAF, Comunidades Preparadas): fajas medidas desde el muro
ZONAS_CONAF = [(2, "0–2 m: sin vegetación (ripio), sin leña ni combustibles"),
               (10, "2–10 m: pasto corto, plantas de bajo porte y riego"),
               (30, "10–30 m: árboles raleados y podados a 2 m (fuera del dibujo)")]
FOSA = {"x": (-7.0, -4.6), "y": (-2.4, -1.0), "litros": 2400}  # DS 236: 24 h retención + lodos 2 años, 5 personas
DRENES = [[(-9.0, -3.0 + k * 1.8), (-21.0, -3.0 + k * 1.8)] for k in range(3)]  # zanjas de infiltración
CAMARA_DISTRIBUCION = (-8.2, -1.2)
POZO = (21.0, -8.5)  # pozo profundo (no hay APR); aguas arriba de la fosa, > 20 m de drenes (DS 236)
DRENAJE_PERIMETRAL_OFFSET = 1.0
INFILTRACION_LLUVIAS = (-4.0, -7.5, -1.0, -5.5)  # pozo/zanja de infiltración de aguas lluvias (faldón sur)
CORTAVIENTO = [(-20.0, 4.0), (-17.0, 14.0), (-8.0, 21.0)]  # arco al NO/O, lejos del faldón FV

# Tratamiento del agua del pozo (en la caseta). En Los Ríos los pozos suelen traer hierro y manganeso:
# el análisis NCh 409 debe pedirlos explícitamente; el filtro catalítico sólo se instala si salen altos.
TRATAMIENTO_AGUA = ["Análisis NCh 409: coliformes, turbiedad, pH, Fe, Mn, As, nitratos",
                    "Filtro de sedimentos 20 µm + 5 µm (cartuchos)",
                    "Filtro catalítico Fe/Mn con retrolavado (si Fe > 0,3 o Mn > 0,1 mg/L)",
                    "Lámpara UV 12 GPM con alarma (desinfección, sin químicos)"]

# ================= OBRAS EXTERIORES (lámina EXT-01) =================
# Deslinde referencial (igual que EMP-01). Cerco del predio: 4 hebras + malla de campo; portón en el acceso.
DESLINDE = (-21.5, -11.5, 28.5, 21.5)
PORTON = {"x": 28.5, "y": -3.5, "ancho": 4.0, "peatonal": 1.0,
          "texto": "Portón vehicular 4,0 m (batiente, motor 24 V con batería) + puerta peatonal 1,0 m"}
PILAR_ACCESO = (28.5, -0.9, "Pilar de acceso: número del predio iluminado, buzón, citófono IP y caseta de basura cerrada")
# Patio cercado para el perro: malla de acero galvanizado 1,5 m, enterrada 0,30 m (anti-excavación), postes
# impregnados c/ 2,5 m. Usa la casa como parte del cierre; deja fuera el acceso, la caseta, la fosa y el estacionamiento
# (el camión limpiafosas entra sin abrir el patio).
CERCO_PATIO = [(9.0, 0.0), (9.0, -3.2), (-4.2, -3.2), (-4.2, 16.0), (19.5, 16.0), (19.5, 4.0), (12.0, 4.0)]
PUERTAS_CERCO = [((9.0, -1.6), "v", 1.0, "Puerta peatonal 1,0 m con cierre automático"),
                 ((19.5, 10.0), "v", 3.0, "Portón 3,0 m para maquinaria de jardín")]
# Senderos peatonales pavimentados (adoquín o baldosa sobre base compactada, drenante): (polilínea, ancho m, nombre)
SENDEROS = [
    ([(14.2, -5.0), (14.2, -2.4), (12.3, -0.8), (11.25, -0.3)], 1.2, "Estacionamiento → entrada"),
    ([(12.3, -0.8), (12.6, 0.4), (12.6, 2.1), (13.2, 2.1)], 1.0, "Entrada → caseta de agua"),
    ([(1.0, -0.1), (1.0, -1.6), (9.0, -1.6)], 1.0, "Terraza → puerta del patio"),
]
BODEGA = {"rect": (22.5, -1.6, 25.5, 1.0),
          "texto": "Bodega exterior 3,0 × 2,6 m metálica (no combustible), radier, luz y enchufe; ≥ 10 m de la casa (CONAF)"}
# Luminarias exteriores (circuito C15): LED 2700 K apantalladas hacia abajo (fauna y cielo oscuro), con sensor de
# movimiento + crepuscular, y escena en Home Assistant. (x, y, tipo 'baliza' | 'foco' | 'aplique', descripción)
LUCES_EXT = [
    (13.5, -4.0, "baliza", "Baliza 60 cm"), (13.5, -2.0, "baliza", "Baliza 60 cm"), (12.0, -0.4, "baliza", "Baliza 60 cm"),
    (15.5, -5.0, "foco", "Foco con sensor en el poste del cargador (estacionamiento)"),
    (15.4, 2.2, "aplique", "Aplique de la caseta"),
    (24.0, -1.6, "aplique", "Aplique con sensor de la bodega"),
    (28.5, -1.4, "aplique", "Número iluminado y luz del portón"),
    (19.3, 10.0, "aplique", "Aplique del portón de jardín"),
]
RESIDUOS = [((27.4, -0.9), "Caseta de basura cerrada junto al camino (perros y zorros)"),
            ((16.5, 14.5), "Compostera cerrada de 2 cámaras (restos de cocina y pasto)")]
# Antena de internet rural (4G/5G o satelital) en el frontón oriente: sin sombra sobre los paneles; ducto al rack.
ANTENA = (12.3, 3.0, "Antena 4G/5G o satelital en el frontón oriente + ducto Ø25 al rack (Cat6 + PoE)")
# Red exterior enterrada (energía y datos en ductos separados ≥ 0,20 m, zanja a 0,60 m, cinta de advertencia,
# cámara de paso 40×40 en cada cambio de dirección). (nombre, polilínea, contenido)
DUCTOS_EXT = [
    ("C8", [(12.0, 2.30), (12.6, 2.30), (13.2, 2.30)], "C8 TDA → tablero de la caseta (presurizadora)"),
    ("Pozo", [(15.4, 2.1), (21.0, 2.1), (21.0, -8.5)], "Caseta → bomba sumergible del pozo (cable plano 3×2,5)"),
    ("EV", [(12.0, 2.30), (12.6, 2.30), (12.6, -4.6), (15.5, -4.6), (15.5, -5.2)], "EV TDA → cargador 11 kW"),
    ("C15", [(12.0, 2.10), (13.0, 1.0), (13.0, -1.9), (26.5, -1.9), (28.5, -1.4)],
     "C15 alumbrado exterior, bodega y portón + ducto de datos (cámara y citófono)"),
]
# ================= ENVOLVENTE TÉRMICA (OGUC 4.1.10 mod. DS 15/2024 — Zona G, vigente 28-11-2025) =================
def _area_vanos(ventanas, puertas_vidriadas=()):
    return sum(w * h for _, _, w, _, _, h in ventanas) + sum(puertas_vidriadas)


def _porcentaje_ventana(orient):
    """% de ventana sobre muro por orientación (N, S, EO), a partir de los datos de la casa."""
    def lado(x, y, o):
        if o == 'h':
            return "N" if y >= 5.9 else "S"
        return "EO"
    muro = {"N": 12 * D.H1 + 10 * D.H2, "S": (8.5 + 2 + 1.5) * D.H1 + 10 * D.H2,
            "EO": (4 + 2 + 4 + 2) * D.H1 + 2 * 6 * D.H2}
    vent = {"N": 0.0, "S": 0.0, "EO": 0.0}
    for vs in (D.VENTANAS_1, D.VENTANAS_2):
        for x, y, w, o, s_, h in vs:
            vent[lado(x, y, o)] += w * h
    vent["S"] += 1.4 * 2.05  # puerta-ventana living -> terraza
    return 100 * vent[orient] / muro[orient], vent[orient], muro[orient]


U_VENTANA = 1.6  # PVC DVH 4/12/4 low-e argón (verificar ficha del fabricante)
_A_VENT = sum(_porcentaje_ventana(o)[1] for o in ("N", "S", "EO"))
_A_MURO = sum(_porcentaje_ventana(o)[2] for o in ("N", "S", "EO")) - _A_VENT - 0.9 * 2.05
ENVOLVENTE = {
    "zona": "ZONA TÉRMICA G (Mariquina) · OGUC 4.1.10 / DS 15 MINVU",
    # ren/h equivalentes: VMC 126 m³/h con recuperación 80 % + infiltración n50/20
    "renovaciones_h": round(126 * (1 - EFICIENCIA_VMC) / (125 * 2.5) + N50_META / 20, 2),
    "areas": [  # (elemento, área m², U W/m²K) para el balance
        ("Cielo P2 + techo bajo", 60 + 8, 0.19),
        ("Muros perimetrales (netos)", round(_A_MURO, 1), 0.32),
        ("Ventanas y puerta-ventana", round(_A_VENT, 1), U_VENTANA),
        ("Puerta de acceso", round(0.9 * 2.05, 1), 1.7),
        ("Piso P2 sobre terraza entrada", 3.0, 0.35),
        ("Radier (pérdida perimetral equiv.)", 65, 0.35),
    ],
    "tabla": [  # (elemento, solución, U propuesta, U máx. zona G)
        ("Techumbre", "Cielo: 2 capas lana mineral 100 mm cruzadas + barrera vapor", 0.19, "0,28"),
        ("Muros", "2×6 + lana min. 140 + OSB + barrera hum. + siding ventilado + cámara técnica + yeso RF (F-15)", 0.32, "0,40"),
        ("Piso ventilado", "Losa sobre terraza entrada + EPS 80 mm por cara inferior", 0.35, "0,39"),
        ("Sobrecimiento", "EPS 50 mm por exterior hasta 30 cm bajo terreno (R100 ≈ 130)", 0.0, "R100 ≥ 91"),
        ("Ventanas", f"PVC DVH low-e, clase 3 de permeabilidad (U {num_s(U_VENTANA)})", U_VENTANA, "según %"),
        ("Puerta acceso", "Puerta aislada con burletes", 1.7, "1,70"),
    ],
}
ENVOLVENTE["notas"] = [
    "Ventanas sobre muro: N {:.0f} % (máx. 76 %) · S {:.0f} % (máx. 26 %) · O-E {:.0f} % (máx. 40 %) con U 1,6.".format(
        _porcentaje_ventana("N")[0], _porcentaje_ventana("S")[0], _porcentaje_ventana("EO")[0]),
    "Hermeticidad: ≤ 5,0 ren/h a 50 Pa (prov. Valdivia). Partida de sellos en EETT.",
    "Memoria de condensación (Res. Ex. 1802: ext. 3,5 °C / 98 % HR) y ventilación NCh 3309: VMC 35 L/s con recuperador 80 %.",
    "Zona sísmica 3: cálculo estructural (> 100 m²). Fuego: F-15 en soportantes (OGUC 4.3.5 n°14, ≤ 140 m² y 2 pisos).",
]
ENVOLVENTE["capas"] = {
    "techumbre": "Zinc-alum 0,4 mm · fieltro · OSB 11 mm · cerchas · paneles FV a 35°",
    "cielo": "Lana mineral 2 × 100 mm · barrera de vapor · yeso-cartón 12,5 mm (U 0,19)",
    "muro": "Siding · cámara ventilada · barrera hum. · OSB · 2×6 + lana 140 · b. vapor · cámara técnica 40 · yeso RF 15 (U 0,32, F-15)",
    "entrepiso": f"Entrepiso acústico {int(round(D.LOSA * 100))} cm: porcelanato · piso flotante yeso-fibra · lámina antiimpacto · OSB 18 · "
                 "vigas 2×10 + lana 100 · canal resiliente · 2 yeso-cartón",
    "piso": "Radier 10 cm · polietileno 0,2 mm · grava 10 cm · EPS 50 mm en sobrecimiento",
}


# ================= TOPOGRAFÍA (sitio/topografia.json, DEM ~30 m) =================
with open(os.path.join(_AQUI, "sitio", "topografia.json"), encoding="utf-8") as _f:
    TOPO = json.load(_f)
NPT_MSNM = TOPO["NPT"]


def cota_terreno(x, y):
    """Cota natural (m s.n.m.) interpolada en la grilla del lote (1 m)."""
    g = TOPO["lote"]
    j = (x - g["x"][0]) / g["paso"]
    i = (y - g["y"][0]) / g["paso"]
    i0, j0 = max(0, min(int(i), len(g["z"]) - 2)), max(0, min(int(j), len(g["z"][0]) - 2))
    fi, fj = i - i0, j - j0
    z = g["z"]
    return (z[i0][j0] * (1 - fj) * (1 - fi) + z[i0][j0 + 1] * fj * (1 - fi)
            + z[i0 + 1][j0] * (1 - fj) * fi + z[i0 + 1][j0 + 1] * fj * fi)
