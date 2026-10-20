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
# Sala técnica bajo el tramo alto de la escalera (interior, protegida de heladas: LiFePO4 no carga bajo 0 °C)
INVERSOR = (10.25, 0.22, "INV")   # inversor HÍBRIDO 6 kW
BATERIA = {"kwh": 11.0, "x": 9.65, "y": 0.22, "tipo": "LiFePO4 11 kWh, 51,2 V"}
CONSUMO_ESTIMADO_KWH_MES = 320    # supuesto: familia 4-5 personas + bomba de pozo (ver calculo/fv_bateria.py)


def panel_a_planta(x0, x1, s0, s1):
    """Proyección en planta de un panel sobre el faldón norte."""
    return x0, CUMBRERA_Y + s0 * COS, x1, CUMBRERA_Y + s1 * COS


# ================= COSECHA DE AGUAS LLUVIAS =================
AREA_CAPTACION = CANALETAS[0]["area_m2"] + CANALETAS[2]["area_m2"]  # faldón norte + techo bajo -> estanque
ESTANQUE = {"x": 13.6, "y": 6.0, "litros": 5000}
COEF_ESCORRENTIA = 0.85

# ================= VENTILACIÓN / CALEFACCIÓN =================
# flechas de ventilación cruzada (piso, [(x,y),...])
VENT_CRUZADA = [
    (1, [(2.0, 5.7), (2.0, 4.0), (1.0, 2.6)]),       # living norte -> puerta terraza sur
    (1, [(5.0, 5.7), (5.0, 3.6), (8.9, 2.5), (11.25, 2.3)]),  # living norte -> acceso
    (1, [(10.75, 5.7), (11.6, 4.5)]),                # oficina 2 norte-este
    (2, [(3.75, 5.7), (3.75, 3.4), (2.6, 1.5)]),     # dorm principal -> closet
    (2, [(7.1, 5.7), (7.1, 3.6), (8.25, 3.1), (9.5, 2.5), (11.0, 2.5), (11.25, 0.4)]),  # dorm 2 -> hall sur
    (2, [(10.4, 5.7), (11.4, 3.3), (11.6, 2.5), (11.6, 0.4)]),   # dorm 3 -> hall sur
]
# elementos: (piso, código, x, y, texto)
ELEMENTOS_VENT = [
    (1, "EX", 5.30, 1.75, "Extractor baño 25 L/s, salida a muro sur"),
    (1, "CA", 5.80, 5.75, "Campana cocina, ducto Ø150 a muro norte"),
    (1, "DC", 7.55, 0.50, "Ducto calefont Ø100 a techo"),
    (1, "RS", 6.30, 1.85, "Rejilla superior (sección según DS 66 / potencia)"),
    (1, "RI", 6.95, 0.25, "Rejilla inferior (sección según DS 66 / potencia)"),
    (1, "ES", 1.00, 5.50, "Estufa pellet 8 kW, cañón Ø80/125 por techo bajo"),
    (1, "TA", 0.15, 5.50, "Toma aire exterior estufa Ø80"),
    (1, "DH", 7.40, 1.60, "Lavandería: tendido interior con deshumidificador o secadora con condensación"),
    (2, "EX", 6.10, 1.75, "Extractor baño 25 L/s, ducto a techo"),
    (2, "VT", 4.55, 0.50, "Ventilación B.A.S. Ø75 sobre cubierta"),
]
# microventilación permanente en marcos de ventanas de recintos secos (piso, índice ventana)
MICROVENT = [(1, 0), (1, 1), (1, 3), (1, 6), (2, 0), (2, 1), (2, 2), (2, 7)]

# ================= EMPLAZAMIENTO (m, mismo origen) =================
SITIO = CLIMA["sitio"]
NORTE_MAGNETICO_DEG = 7  # declinación aproximada (E); verificar en terreno
ACCESO = [(30.0, -3.5), (16.0, -3.5), (12.6, -1.0), (11.25, -0.2)]  # desde camino vecinal (este)
ESTACIONAMIENTO = (14.0, -8.0, 19.0, -4.5)
FOSA = {"x": (-7.0, -4.6), "y": (-2.4, -1.0), "litros": 2400}  # DS 236: 24 h retención + lodos 2 años, 5 personas
DRENES = [[(-9.0, -3.0 + k * 1.8), (-21.0, -3.0 + k * 1.8)] for k in range(3)]  # zanjas de infiltración
CAMARA_DISTRIBUCION = (-8.2, -1.2)
POZO = (21.0, -8.5)  # pozo profundo (no hay APR); aguas arriba de la fosa, > 20 m de drenes (DS 236)
DRENAJE_PERIMETRAL_OFFSET = 1.0
INFILTRACION_LLUVIAS = (-4.0, -7.5, -1.0, -5.5)  # pozo/zanja de infiltración de aguas lluvias (faldón sur)
CORTAVIENTO = [(-20.0, 4.0), (-17.0, 14.0), (-8.0, 21.0)]  # arco al NO/O, lejos del faldón FV

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
    "renovaciones_h": 0.6,
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
        ("Muros", "Tabique madera 2×6 + lana min. 140 mm + OSB + barrera hum. + siding ventilado", 0.32, "0,40"),
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
    "Exige memoria de condensación (NCh 1973 / NCh 853) y sistema de ventilación (NCh 3308/3309).",
    "Zona sísmica 3 (NCh433): cálculo estructural obligatorio (> 100 m²).",
]
ENVOLVENTE["capas"] = {
    "techumbre": "Zinc-alum 0,4 mm · fieltro · OSB 11 mm · cerchas · paneles FV a 35°",
    "cielo": "Lana mineral 2 × 100 mm · barrera de vapor · yeso-cartón 12,5 mm (U 0,19)",
    "muro": "Siding · cámara ventilada · barrera hum. · OSB · 2×6 + lana 140 mm · yeso RH (U 0,32)",
    "entrepiso": "Losa / envigado + aislación acústica 50 mm",
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
