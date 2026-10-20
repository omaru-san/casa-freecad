#!/usr/bin/env python3
"""Cálculo estructural simplificado (anteproyecto académico) — vivienda 2 pisos en tabiquería de madera.

Normas de referencia: NCh433 Of.96 Mod.2009 + DS 61 (sismo), NCh1537 (sobrecargas), NCh432 (viento),
NCh1198 (madera, tensiones admisibles), NCh1990 / pino radiata grado estructural.
Salida: calculo/estructura.json.  Uso: python3 -I estructura.py   (desde la carpeta del proyecto)

ADVERTENCIA: ejercicio de aprendizaje. Tipo de suelo, capacidad de soporte y propiedades de la madera
son SUPUESTOS; un proyecto real requiere mecánica de suelos y un calculista.
"""
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
import casa_datos as D  # noqa: E402
import especialidades_datos as E  # noqa: E402

G = 9.81

# ---------------- materiales (pino radiata grado estructural, valores admisibles referenciales) ----------------
MADERA = {"nombre": "Pino radiata estructural C24 / MSR (NCh1198, valores admisibles)",
          "Ff": 9.3, "Fcz": 2.5, "Fv": 1.1, "E": 9000.0, "densidad_kN_m3": 5.0}
OSB = {"nombre": "OSB 11,1 mm estructural, clavo 2½\" (8d) @ 10 cm bordes / 20 cm interior",
       "v_adm_kN_m": 5.5}   # corte admisible del muro (equiv. SDPWS ASD 380 plf)
SUELO = {"tipo": "D (supuesto: suelo fluvial/volcánico medianamente denso)", "S": 1.20, "T0": 0.75, "Tp": 0.85,
         "n": 1.80, "sigma_adm_kPa": 100.0}
SISMO = {"zona": 3, "A0_g": 0.40, "I": 1.0, "categoria": "II (vivienda)", "R": 5.5, "R0": 7.0,
         "sistema": "Muros y diafragmas de madera (NCh433 Tabla 5.1)"}

# ---------------- cargas (kN/m²) ----------------
CARGAS = {
    "cubierta_inclinada": 0.05 + 0.07 + 0.03,       # zinc 0,4 + OSB 11 + fieltro (por m² inclinado)
    "estructura_techo": 0.15,                       # cerchas W @ 60 + costaneras (por m² inclinado)
    "paneles_fv": 0.15,                             # 625 Wp ≈ 34 kg/2,7 m² + rieles (sobre su área)
    "cielo_p2": 0.10 + 0.04 + 0.06,                 # yeso 12,5 + lana 200 mm + cadenetas 2×4
    "entrepiso": 0.10 + 0.11 + 0.13 + 0.10 + 0.03,  # piso + OSB 18 + vigas 2×10 @ 40 + cielo yeso + aislac.
    "muro_ext": 0.45, "muro_int": 0.35,            # por m² de muro
    "tabiques_movibles": 0.50,                      # NCh1537, equivalente repartido sobre entrepiso
    "SC_vivienda": 2.0, "SC_techo": 0.30, "nieve": 0.0,  # NCh1537; nieve 0 (31 años sin nieve en el sitio)
}

H1, H2 = D.H1 + D.LOSA, D.H2       # alturas de entrepiso para el sismo
Z1, Z2 = H1, H1 + H2


def largo_muros(muros, tipo=None):
    return sum(math.hypot(x2 - x1, y2 - y1) for x1, y1, x2, y2, t in muros if tipo is None or t == tipo)


# ---------------- pesos sísmicos ----------------
inc = 1 / math.cos(math.radians(E.PENDIENTE))
area_techo_h = (E.TECHO_X[1] - E.TECHO_X[0]) * (E.TECHO_Y[1] - E.TECHO_Y[0])
area_fv = len(E.PANELES) * E.PANEL["largo"] * E.PANEL["ancho"]
techo_D = area_techo_h * (CARGAS["cubierta_inclinada"] + CARGAS["estructura_techo"]) * inc + area_fv * CARGAS["paneles_fv"]
cielo_D = 60.0 * CARGAS["cielo_p2"]
area_tb = (E.TECHO_BAJO["x"][1] - E.TECHO_BAJO["x"][0]) * (E.TECHO_BAJO["y"][1] - E.TECHO_BAJO["y"][0])
techo_bajo_D = area_tb * (CARGAS["cubierta_inclinada"] + CARGAS["estructura_techo"] + CARGAS["cielo_p2"])
area_p2 = 60.0 - (D.HUECO_ESCALERA[2] - D.HUECO_ESCALERA[0]) * (D.HUECO_ESCALERA[3] - D.HUECO_ESCALERA[1])
entrepiso_D = area_p2 * (CARGAS["entrepiso"] + CARGAS["tabiques_movibles"])
mu2 = largo_muros(D.MUROS_2, D.EXT) * H2 * CARGAS["muro_ext"] + largo_muros(D.MUROS_2, D.INT) * H2 * CARGAS["muro_int"]
mu1 = largo_muros(D.MUROS_1, D.EXT) * D.H1 * CARGAS["muro_ext"] + largo_muros(D.MUROS_1, D.INT) * D.H1 * CARGAS["muro_int"]
frontones = 2 * 0.5 * 6 * (E.Z_CUMBRERA - D.Z2 - D.H2) * CARGAS["muro_ext"]

P2 = techo_D + cielo_D + frontones + mu2 / 2 + 0.25 * CARGAS["SC_techo"] * area_techo_h * 0  # SC techo no participa
P1 = entrepiso_D + 0.25 * CARGAS["SC_vivienda"] * area_p2 + mu2 / 2 + mu1 / 2 + techo_bajo_D
P = P1 + P2

# ---------------- coeficiente sísmico (método estático NCh433 6.2) ----------------
T_est = 0.05 * (Z2 ** 0.75)            # período estimado de muros de madera livianos
C_formula = 2.75 * SUELO["S"] * SISMO["A0_g"] / SISMO["R"] * (SUELO["Tp"] / T_est) ** SUELO["n"]
C_max = 0.40 * SUELO["S"] * SISMO["A0_g"]   # R = 5,5 -> Cmax = 0,40 S A0/g (Tabla 6.4)
C_min = SUELO["S"] * SISMO["A0_g"] / 6
C = max(C_min, min(C_formula, C_max))
Q0 = C * SISMO["I"] * P


def Ak(zk_1, zk, H):
    return math.sqrt(1 - zk_1 / H) - math.sqrt(1 - zk / H)


A1, A2 = Ak(0, Z1, Z2), Ak(Z1, Z2, Z2)
F2 = A2 * P2 / (A1 * P1 + A2 * P2) * Q0
F1 = A1 * P1 / (A1 * P1 + A2 * P2) * Q0
TORSION = 1.15  # amplificación por torsión accidental (±0,10 b) y excentricidad de rigidez

# ---------------- viento (NCh432, simplificado) ----------------
V = 35.0                                   # m/s, racha máx. del sitio 124 km/h ≈ 34,4 m/s
q_b = 0.613 * V ** 2 / 1000                # kPa
Kz, G_raf, Cp_tot = 0.85, 0.85, 1.30       # exposición C rural, h ≈ 7 m; barlovento + sotavento
q_z = Kz * q_b
area_x = 12 * H1 + 10 * H2 + 10.8 * (E.Z_CUMBRERA - D.Z2 - D.H2) * 0.5   # fachada N/S (viento ⟂ eje largo)
area_y = 6 * (H1 + H2) + 6 * (E.Z_CUMBRERA - D.Z2 - D.H2) * 0.5           # frontón E/O
W_ns = q_z * G_raf * Cp_tot * area_x       # empuja en dirección Y (N-S)
W_eo = q_z * G_raf * Cp_tot * area_y       # empuja en dirección X (E-O)
succion_techo = q_z * G_raf * 0.9          # kPa, faldón sotavento + interior
anclaje_par = (succion_techo - 0.6 * (CARGAS["cubierta_inclinada"] + CARGAS["estructura_techo"])) * 0.6 * 3.6  # por cercha


# ---------------- muros de corte ----------------
def segmentos(muros, puertas, ventanas, h):
    """Paños llenos de muro (sin vanos) por dirección. Devuelve {'x': [(largo, ...)], 'y': [...]}."""
    res = {"x": [], "y": []}
    for x1, y1, x2, y2, t in muros:
        horiz = y1 == y2
        lo, hi = (min(x1, x2), max(x1, x2)) if horiz else (min(y1, y2), max(y1, y2))
        fijo = y1 if horiz else x1
        cortes = []
        for ab in list(puertas) + list(ventanas):
            x, y, w, o = ab[:4]
            if (o == 'h') == horiz and abs((y if horiz else x) - fijo) < 1e-6:
                c = x if horiz else y
                if lo <= c <= hi:
                    cortes.append((c - w / 2, c + w / 2))
        cortes.sort()
        cur = lo
        for a, b in cortes + [(hi, hi)]:
            if a - cur > 0.05:
                res["x" if horiz else "y"].append(round(a - cur, 2))
            cur = max(cur, b)
    return res


def capacidad(segs, h):
    """Suma de capacidades: paños con h/b > 3,5 no cuentan; si h/b > 2 se reduce por 2b/h (SDPWS)."""
    tot, util = 0.0, 0.0
    for b in segs:
        if h / b > 3.5:
            continue
        f = 1.0 if h / b <= 2 else 2 * b / h
        tot += OSB["v_adm_kN_m"] * b * f
        util += b
    return tot, util


s1 = segmentos(D.MUROS_1, D.PUERTAS_1, D.VENTANAS_1, D.H1)
s2 = segmentos(D.MUROS_2, D.PUERTAS_2, D.VENTANAS_2, D.H2)
muros_corte = {}
for piso, segs, V_sis, h in ((1, s1, (F1 + F2) * TORSION, D.H1), (2, s2, F2 * TORSION, D.H2)):
    for dirc, W_v in (("x", W_eo if piso == 2 else W_eo), ("y", W_ns)):
        cap, util = capacidad(segs[dirc], h)
        W_piso = W_v * (0.5 if piso == 2 else 1.0)
        dem = max(V_sis, W_piso)
        muros_corte[f"P{piso}_{dirc}"] = {
            "largo_util_m": round(util, 1), "capacidad_kN": round(cap, 1), "demanda_sismo_kN": round(V_sis, 1),
            "demanda_viento_kN": round(W_piso, 1), "FU": round(dem / cap, 2),
            "v_kN_m": round(dem / util, 2) if util else None}

# anclaje (hold-down) típico: paño de 1,2 m en P1 dirección más cargada
peor = max(muros_corte.values(), key=lambda m: m["FU"])
v_peor = peor["v_kN_m"]
T_holddown = v_peor * D.H1 - 0.6 * (CARGAS["muro_ext"] * D.H1 + 3.0) * 1.2 / 2  # kN (vuelco - 0,6 peso)

# ---------------- elementos de madera ----------------
def viga(nombre, b, h, L, q, apoyo="simple", limite=300):
    """q en kN/m, L en m, b/h en mm. Retorna tensiones y deflexión."""
    W = b * h ** 2 / 6
    I = b * h ** 3 / 12
    M = q * L ** 2 / (8 if apoyo == "simple" else 12)
    Vc = q * L / 2
    f_b = M * 1e6 / W
    f_v = 1.5 * Vc * 1e3 / (b * h)
    k = 5 / 384 if apoyo == "simple" else 1 / 384
    d = k * q * (L * 1000) ** 4 / (MADERA["E"] * I)
    return {"elemento": nombre, "seccion_mm": f"{b}×{h}", "L_m": L, "q_kN_m": round(q, 2), "M_kNm": round(M, 2),
            "fb_MPa": round(f_b, 2), "Ff_adm": MADERA["Ff"], "fv_MPa": round(f_v, 2), "Fv_adm": MADERA["Fv"],
            "flecha_mm": round(d, 1), "flecha_adm_mm": round(L * 1000 / limite, 1),
            "FU": round(max(f_b / MADERA["Ff"], f_v / MADERA["Fv"], d / (L * 1000 / limite)), 2)}


s_vig = 0.40
q_ent = (CARGAS["entrepiso"] + CARGAS["tabiques_movibles"] + CARGAS["SC_vivienda"]) * s_vig
s_par = 0.60
q_par = ((CARGAS["cubierta_inclinada"] + CARGAS["estructura_techo"]) * inc + CARGAS["paneles_fv"] + CARGAS["SC_techo"]) * s_par
# Cerchas tipo W @ 60 cm apoyadas sólo en muros y=0 e y=6: cada muro recibe la mitad del ancho de techo
trib_techo = (E.TECHO_Y[1] - E.TECHO_Y[0]) / 2
L_NUDO_SUP = (E.CUMBRERA_Y - 0) / 2 / math.cos(math.radians(E.PENDIENTE))   # tramo de cuerda superior entre nudos
L_NUDO_INF = 6.0 / 3                                                     # cuerda inferior W: 3 tramos
q_viga_terraza = ((CARGAS["cubierta_inclinada"] + CARGAS["estructura_techo"]) * inc + CARGAS["cielo_p2"] + CARGAS["SC_techo"]) * trib_techo \
    + CARGAS["muro_ext"] * D.H2 + (CARGAS["entrepiso"] + CARGAS["SC_vivienda"]) * 1.0
elementos = [
    viga("Viga entrepiso (living, luz mayor)", 45, 240, 4.0, q_ent),
    viga("Viga entrepiso (franja servicios)", 45, 240, 2.0, q_ent),
    viga("Cercha W: cuerda superior (tramo entre nudos)", 45, 140, round(L_NUDO_SUP, 2), q_par),
    viga("Cercha W: cuerda inferior + cielo (tramo)", 45, 90, L_NUDO_INF, (CARGAS["cielo_p2"] + 0.5) * 0.6),
    viga("Viga sobre terraza entrada (y=0, x 10,5→12)", 2 * 45, 240, 1.5, q_viga_terraza),
    viga("Viga sobre terraza entrada (x=12, y 0→2)", 2 * 45, 240, 2.0, q_viga_terraza),
]
# pilar esquina terraza
N_pilar = q_viga_terraza * (1.5 + 2.0) / 2
lado = 140
A_p = lado * lado
lam = 2600 / (lado / math.sqrt(12))
pilar = {"elemento": "Pilar esquina terraza (madera laminada)", "seccion_mm": f"{lado}×{lado}", "N_kN": round(N_pilar, 1),
         "fc_MPa": round(N_pilar * 1e3 / A_p, 2), "esbeltez": round(lam, 0),
         "Fc_adm_pandeo_MPa": round(7.5 * min(1, 2800 / lam ** 2 * 1.3), 2)}

# ---------------- cargas sobre la fundación (insumo: las fundaciones las diseña un tercero) ----------------
def linea_fund(nombre, techo_trib, ent_trib, muros_kN_m):
    """Carga lineal de servicio en la base del muro (sobre sobrecimiento), sin peso propio de la fundación."""
    techo_d = ((CARGAS["cubierta_inclinada"] + CARGAS["estructura_techo"]) * inc + CARGAS["paneles_fv"] + CARGAS["cielo_p2"]) * techo_trib
    techo_l = CARGAS["SC_techo"] * techo_trib
    ent_d = (CARGAS["entrepiso"] + CARGAS["tabiques_movibles"]) * ent_trib
    ent_l = CARGAS["SC_vivienda"] * ent_trib
    d, l_ = techo_d + ent_d + muros_kN_m, techo_l + ent_l
    return {"eje": nombre, "D_kN_m": round(d, 1), "L_kN_m": round(l_, 1), "q_kN_m": round(d + l_, 1)}


muro2 = CARGAS["muro_ext"] * D.H2
muro1 = CARGAS["muro_ext"] * D.H1
fund = [
    linea_fund("Eje y=0 (fachada sur)", trib_techo, 1.0, muro2 + muro1),
    linea_fund("Eje y=6 (fachada norte, con FV)", trib_techo, 2.0, muro2 + muro1),
    linea_fund("Eje y=2 (interior, bajo entrepiso)", 0.0, 3.0, CARGAS["muro_int"] * D.H1 + CARGAS["muro_int"] * D.H2 * 0.5),
]

res = {
    "advertencia": "Ejercicio académico de anteproyecto. Suelo y maderas supuestos; requiere mecánica de suelos y calculista.",
    "sistema": "Tabiquería de madera (plataforma) con muros de corte OSB; entrepiso de vigas 2×10 @ 40; techumbre de cerchas "
               "tipo W @ 60 cm (luz 6 m muro a muro, sin apoyo intermedio). Fundaciones: proyecto aparte (fuera de alcance).",
    "materiales": {"madera": MADERA, "osb": OSB, "hormigon": "Fundaciones y sobrecimiento: proyecto por terceros"},
    "suelo": SUELO, "sismo": SISMO, "cargas_kN_m2": CARGAS,
    "pesos_kN": {"techo": round(techo_D, 1), "cielo_p2": round(cielo_D, 1), "frontones": round(frontones, 1),
                 "muros_p2": round(mu2, 1), "muros_p1": round(mu1, 1), "entrepiso": round(entrepiso_D, 1),
                 "techo_bajo": round(techo_bajo_D, 1), "P1_nivel1": round(P1, 1), "P2_nivel2": round(P2, 1), "P_total": round(P, 1),
                 "peso_por_m2_kPa": round(P / 125, 2)},
    "coef_sismico": {"T_estimado_s": round(T_est, 3), "C_formula": round(C_formula, 3), "C_max": round(C_max, 3),
                     "C_min": round(C_min, 3), "C": round(C, 3), "Q0_kN": round(Q0, 1),
                     "F1_kN": round(F1, 1), "F2_kN": round(F2, 1), "Ak": [round(A1, 3), round(A2, 3)], "torsion": TORSION},
    "viento": {"V_m_s": V, "q_basica_kPa": round(q_b, 3), "q_z_kPa": round(q_z, 3), "W_NS_kN": round(W_ns, 1),
               "W_EO_kN": round(W_eo, 1), "succion_techo_kPa": round(succion_techo, 2),
               "anclaje_par_kN": round(anclaje_par, 2)},
    "muros_corte": muros_corte,
    "segmentos_m": {"P1": s1, "P2": s2},
    "holddown_tipico_kN": round(T_holddown, 1),
    "elementos": elementos, "pilar": pilar, "cargas_a_fundacion": fund,
    "reacciones_puntuales_kN": {"pilar_esquina_terraza": round(N_pilar, 1), "holddown_traccion": round(T_holddown, 1),
                                "corte_basal_Q0": round(Q0, 1)},
    "fem_verificacion": {
        "modelo": "calculo/FEM_Viga.FCStd — viga 90×240 mm, L = 2,0 m, empotrada en extremos, q = 6,71 kN/m (presión 74,6 kPa)",
        "malla": "Gmsh tetraédrica, 3.799 nodos", "solver": "CalculiX (FreeCAD 1.1 FEM)",
        "von_mises_max_MPa": 2.39, "desplazamiento_max_mm": 0.34,
        "teoria_empotrada": {"sigma_MPa": 2.59, "flecha_mm": 0.30},
        "conclusion": "Coincide con la teoría de vigas (<15 %, el FEM incluye deformación por corte). "
                      "Con apoyo simple (caso de diseño) la tensión es 3,9 MPa < 9,3 MPa admisible.",
    },
}
with open(os.path.join(AQUI, "estructura.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
for k in ("pesos_kN", "coef_sismico", "viento", "muros_corte"):
    print(k, json.dumps(res[k], ensure_ascii=False))
print("holddown", res["holddown_tipico_kN"])
for e_ in elementos:
    print(e_)
print(pilar)
for f_ in fund:
    print(f_)
