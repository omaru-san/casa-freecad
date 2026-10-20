"""Láminas 08 (estructura) y 09 (topografía). Leen calculo/estructura.json y sitio/topografia.json."""
import json
import math
import os

import casa_datos as D
import especialidades_datos as E
from generar_especialidades import TINTA2, Vista, contorno_p1, flecha, miles, norte
from generar_laminas import C_MURO, OX1, OX2, Lamina, Planta, leyenda, marco, notas, num, tabla

AQUI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AQUI, "calculo", "estructura.json"), encoding="utf-8") as _f:
    EST = json.load(_f)
C_CORTE = "#2e8b57"
C_FUND = "#cfcac0"
C_TOPO = "#b49a74"


def paños(muros, puertas, ventanas):
    """Paños llenos de muro: [(x0, y0, x1, y1, largo)] (mismo criterio que calculo/estructura.py)."""
    out = []
    for x1, y1, x2, y2, t in muros:
        horiz = y1 == y2
        lo, hi = (min(x1, x2), max(x1, x2)) if horiz else (min(y1, y2), max(y1, y2))
        fijo = y1 if horiz else x1
        cortes = sorted((c - w / 2, c + w / 2) for c, w in
                        (((x if horiz else y), w) for x, y, w, o, *_ in list(puertas) + list(ventanas)
                         if (o == 'h') == horiz and abs((y if horiz else x) - fijo) < 1e-6 and lo <= (x if horiz else y) <= hi))
        cur = lo
        for a, b in cortes + [(hi, hi)]:
            if a - cur > 0.05:
                out.append(((cur, fijo, a, fijo) if horiz else (fijo, cur, fijo, a)) + (a - cur, t))
            cur = max(cur, b)
    return out


def dibujar_muros_corte(pl, muros, puertas, ventanas, h):
    for x0, y0, x1, y1, b, t in paños(muros, puertas, ventanas):
        es_corte = h / b <= 3.5
        e = t / 2 + 0.05
        if x0 == x1:
            pl.caja(x0 - e, y0, x0 + e, y1, relleno=C_CORTE if es_corte else "#999")
        else:
            pl.caja(x0, y0 - e, x1, y0 + e, relleno=C_CORTE if es_corte else "#999")
        if es_corte:
            for px, py in ((x0, y0), (x1, y1)):
                X, Y = pl.P(px, py)
                pl.L.add(f'<polygon points="{X:.2f},{Y - 1.1:.2f} {X + 1.0:.2f},{Y + 0.7:.2f} {X - 1.0:.2f},{Y + 0.7:.2f}" fill="#000"/>')


def tabla_dicts(L, x, y, titulo, filas, anchos, fs=1.5):
    L.txt(x, y - 2.5, titulo, fs=2.1, anchor="start", peso="bold")
    tabla(L, x, y, anchos, filas, fs=fs, alto=4.3)


def lamina_estructura():
    L = Lamina()
    marco(L, "EST-01", "ESTRUCTURA — MUROS DE CORTE, ENTREPISO Y CARGAS A FUNDACIÓN", 8)
    L.txt(OX1 + 60, 22, "MUROS DE CORTE P1 (fundación por terceros)", fs=3.6, peso="bold")
    L.txt(OX2 + 70, 22, "ENTREPISO, CERCHAS Y MUROS DE CORTE P2", fs=3.6, peso="bold")
    p1 = Planta(L, OX1)
    p2 = Planta(L, OX2)
    # --- P1: fundaciones corridas ---
    for x1, y1, x2, y2, t in D.MUROS_1:
        b = 0.40 if t == D.EXT or (y1 == y2 == 2) else 0.30
        if y1 == y2:
            p1.caja(min(x1, x2) - b / 2, y1 - b / 2, max(x1, x2) + b / 2, y1 + b / 2, relleno="none", borde="#bbb", ancho=0.12)
        else:
            p1.caja(x1 - b / 2, min(y1, y2) - b / 2, x1 + b / 2, max(y1, y2) + b / 2, relleno="none", borde="#bbb", ancho=0.12)
    for cx, cy, t in D.COLUMNAS_1:
        p1.caja(cx - t / 2, cy - t / 2, cx + t / 2, cy + t / 2, relleno="#000")
        X, Y = p1.P(cx, cy)
        L.txt(X + 4, Y + 5, f"Pilar 14×14 lam. · N = {num(EST['pilar']['N_kN'])} kN a fundación", fs=1.3, anchor="start")
    dibujar_muros_corte(p1, D.MUROS_1, D.PUERTAS_1, D.VENTANAS_1, D.H1)
    for (x, y) in [(0, 2), (0, 6), (12, 6), (12, 2), (2, 0), (10.5, 0)]:
        X, Y = p1.P(x, y)
        dz = E.cota_terreno(x, y) - E.NPT_MSNM
        L.txt(X + (-1.5 if x < 6 else 1.5), Y + (-1.6 if y > 3 else 3.6), f"NTN {num(dz)}", fs=1.3,
              anchor="end" if x < 6 else "start", color="#7a6040")
    X, Y = p1.P(0.0, -0.9)
    L.txt(X, Y + 2, "Ejes de muro (gris): la fundación la proyecta un tercero con las cargas de la tabla", fs=1.3, anchor="start", color="#7a6040")
    # --- P2: entrepiso ---
    for n, x0, y0, x1, y1 in D.RECINTOS_2:
        p2.caja(x0, y0, x1, y1, relleno="#f7f5ef")
    for (xa, xb, ya, yb, et, lx, ly) in ((2.3, 7.9, 2.0, 6.0, "2×10 @ 40 (L = 4,0 m)", 3.75, 4.6),
                                         (2.3, 7.7, 0.0, 2.0, "2×10 @ 40 (L = 2,0 m)", 6.1, 1.0),
                                         (8.1, 11.9, 3.0, 6.0, "2×10 @ 40 (L = 3,0 m)", 10.4, 4.6), (10.6, 11.9, 0.0, 3.0, "", 0, 0)):
        for k in range(int((xb - xa) / 0.4) + 1):
            x = xa + k * 0.4
            p2.poly([(x, ya + 0.08), (x, yb - 0.08)], color="#c8b89a", ancho=0.15)
        if et:
            X, Y = p2.P(lx, ly)
            L.rect(X - 15, Y - 2.4, 30, 3.6, relleno="#fff", borde="none")
            L.txt(X, Y + 0.4, et, fs=1.5, peso="bold")
    hx0, hy0, hx1, hy1 = D.HUECO_ESCALERA
    p2.caja(hx0, hy0, hx1, hy1, relleno="#fff", borde="#000", ancho=0.4)
    p2.poly([(hx0, hy0), (hx1, hy1)], ancho=0.15)
    p2.poly([(hx0, hy1), (hx1, hy0)], ancho=0.15)
    X, Y = p2.P((hx0 + hx1) / 2, hy1 + 0.25)
    L.txt(X, Y, "Hueco escalera · brochales 2×(2×10)", fs=1.3)
    for pts in (((10.5, 0), (12, 0)), ((12, 0), (12, 2))):
        p2.poly(pts, color="#c0392b", ancho=1.4)
    X, Y = p2.P(12, 0)
    L.txt(X + 2, Y + 0.5, "Vigas 2×(45×240)\nsobre pilar", fs=1.3, anchor="start", color="#c0392b")
    dibujar_muros_corte(p2, D.MUROS_2, D.PUERTAS_2, D.VENTANAS_2, D.H2)
    # cercha W esquemática
    cx0, cy0, k = 200, 150, 9.0
    L.txt(cx0, cy0 - 26, "CERCHA TIPO W @ 60 cm (luz 6,0 m + aleros 0,6)", fs=2.0, anchor="start", peso="bold")
    ap = [(-0.6, -0.6 * E.TAN), (3.0, 3.0 * E.TAN), (6.6, -0.6 * E.TAN)]
    P = lambda u, v: (cx0 + (u + 0.6) * k, cy0 - v * k)
    L.linea([P(*ap[0]), P(*ap[1]), P(*ap[2])], ancho=0.6)
    L.linea([P(0, 0), P(6, 0)], ancho=0.6)
    for a_, b_ in (((0, 0), (1.5, 1.5 * E.TAN)), ((2, 0), (1.5, 1.5 * E.TAN)), ((2, 0), (3, 3 * E.TAN)),
                   ((4, 0), (3, 3 * E.TAN)), ((4, 0), (4.5, 1.5 * E.TAN)), ((6, 0), (4.5, 1.5 * E.TAN))):
        L.linea([P(*a_), P(*b_)], ancho=0.35)
    for u in (0, 6):
        X, Y = P(u, 0)
        L.add(f'<polygon points="{X},{Y} {X - 1.5},{Y + 2.4} {X + 1.5},{Y + 2.4}" fill="#000"/>')
    L.txt(P(3, 0)[0], cy0 + 5, "Cuerdas 2×6 (sup.) / 2×4 (inf.) · diagonales 2×4 · placas dentadas · amarra anti-succión por cercha",
          fs=1.35)
    # tablas
    pk, cs, vi = EST["pesos_kN"], EST["coef_sismico"], EST["viento"]
    tabla_dicts(L, 15, 182, "SISMO (NCh433, zona 3, suelo D supuesto) Y VIENTO", [
        ("Parámetro", "Valor"),
        ("Peso sísmico P (D + 25 % SC)", f"{num(pk['P_total'])} kN ({num(pk['peso_por_m2_kPa'])} kPa)"),
        ("R / I / S / A0", f"{EST['sismo']['R']} / {EST['sismo']['I']} / {EST['suelo']['S']} / {EST['sismo']['A0_g']} g"),
        ("C = Cmáx = 0,40·S·A0/g", f"{num(cs['C'])[:-1]}{num(cs['C'])[-1]}"),
        ("Q0 = C·I·P", f"{num(cs['Q0_kN'])} kN  (F1 {num(cs['F1_kN'])} · F2 {num(cs['F2_kN'])})"),
        ("Viento N–S / E–O (V = 35 m/s)", f"{num(vi['W_NS_kN'])} / {num(vi['W_EO_kN'])} kN"),
        ("Succión techo · amarra por cercha", f"{num(vi['succion_techo_kPa'])} kPa · {num(vi['anclaje_par_kN'])} kN"),
    ], [44, 46])
    mc = EST["muros_corte"]
    filas = [("Piso/dir.", "Largo útil", "Capac.", "Sismo", "Viento", "FU")]
    for k_, m in mc.items():
        filas.append((k_.replace("_", " "), f"{num(m['largo_util_m'])} m", f"{num(m['capacidad_kN'])}",
                      f"{num(m['demanda_sismo_kN'])}", f"{num(m['demanda_viento_kN'])}", num(m["FU"])))
    tabla_dicts(L, 110, 182, "MUROS DE CORTE OSB (kN, v adm 5,5 kN/m)", filas, [16, 16, 13, 13, 13, 10])
    filas = [("Elemento", "Sección", "L", "fb/Ff", "Flecha", "FU")]
    for el in EST["elementos"]:
        filas.append((el["elemento"][:42], el["seccion_mm"], num(el["L_m"]), f"{num(el['fb_MPa'])}/{num(el['Ff_adm'])[:-1]}",
                      f"{num(el['flecha_mm'])[:-1]}/{num(el['flecha_adm_mm'])[:-1]}", num(el["FU"])))
    tabla_dicts(L, 200, 182, "ELEMENTOS DE MADERA (MPa, mm)", filas, [57, 13, 8, 15, 12, 8])
    fu = EST["cargas_a_fundacion"]
    filas = [("Eje", "D kN/m", "L kN/m", "D+L")] + [(f["eje"][:34], num(f["D_kN_m"]), num(f["L_kN_m"]), num(f["q_kN_m"])) for f in fu]
    tabla_dicts(L, 15, 225, "CARGAS A FUNDACIÓN (servicio, insumo para terceros)", filas, [52, 12, 12, 12])
    fem = EST["fem_verificacion"]
    notas(L, 110, 225, "VERIFICACIÓN FEM EN FREECAD (CalculiX)", [
        "Viga 90×240 sobre terraza de entrada, L = 2,0 m, q = 6,71 kN/m:",
        f"FEM: von Mises {num(fem['von_mises_max_MPa'])} MPa · flecha {num(fem['desplazamiento_max_mm'])} mm",
        f"Teoría (empotrada): {num(fem['teoria_empotrada']['sigma_MPa'])} MPa · {num(fem['teoria_empotrada']['flecha_mm'])} mm",
        "Archivo: calculo/FEM_Viga.FCStd (abrir y ver resultados).",
        "Hold-down típico en extremos de paños P1: " + f"{num(EST['holddown_tipico_kN'])} kN.",
    ], fs=1.5)
    leyenda(L, 345, 40, [
        (lambda L, x, y: L.rect(x - 3.5, y - 1, 7, 2, relleno=C_CORTE), "Muro de corte OSB"),
        (lambda L, x, y: L.rect(x - 3.5, y - 1, 7, 2, relleno="#999"), "Paño angosto (no cuenta)"),
        (lambda L, x, y: L.add(f'<polygon points="{x},{y - 1.1} {x + 1},{y + 0.7} {x - 1},{y + 0.7}" fill="#000"/>'), "Anclaje hold-down"),
        (lambda L, x, y: L.rect(x - 3.5, y - 1.5, 7, 3, relleno="none", borde="#bbb", ancho=0.12), "Eje de muro (fund. terceros)"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color="#c0392b", ancho=1.4), "Viga 2×(45×240)"),
        (lambda L, x, y: L.linea([(x, y - 2), (x, y + 2)], color="#c8b89a", ancho=0.4), "Vigas entrepiso 2×10 @ 40"),
    ])
    L.txt(345, 88, EST["advertencia"][:44], fs=1.4, anchor="start", color="#a33")
    L.txt(345, 91.5, EST["advertencia"][44:92], fs=1.4, anchor="start", color="#a33")
    L.txt(345, 95, EST["advertencia"][92:], fs=1.4, anchor="start", color="#a33")
    return L


# =====================================================================
#  09 TOPOGRAFÍA
# =====================================================================

def perfil(L, x0, y0, w, h, datos, titulo, marca):
    """datos [[dist, z]] — escala vertical automática para que quepa el terreno y la casa (alto 7,3 m)."""
    kh = w / (datos[-1][0] - datos[0][0])
    zmin = math.floor(min(z for _, z in datos)) - 1
    zmax = max(max(z for _, z in datos), E.NPT_MSNM + E.Z_CUMBRERA) + 1
    kv = h / (zmax - zmin)
    L.txt(x0, y0 - 2.5, titulo, fs=1.9, anchor="start", peso="bold")
    for zz in range(int(zmin) + (int(zmin) % 2), int(zmax) + 1, 4):
        y = y0 + h - (zz - zmin) * kv
        L.linea([(x0, y), (x0 + w, y)], color="#eee", ancho=0.15)
        L.txt(x0 - 1, y + 0.5, str(zz), fs=1.2, anchor="end", color=TINTA2)
    pts = [(x0 + (d - datos[0][0]) * kh, y0 + h - (z - zmin) * kv) for d, z in datos]
    L.linea(pts + [(pts[-1][0], y0 + h), (pts[0][0], y0 + h)], color="#7a6040", ancho=0.4, cerrar=True, relleno="#eadfcd")
    a, b = marca
    xa, xb = x0 + (a - datos[0][0]) * kh, x0 + (b - datos[0][0]) * kh
    yN = y0 + h - (E.NPT_MSNM - zmin) * kv
    alto = E.Z_CUMBRERA * kv
    L.rect(xa - 0.4, yN - alto, xb - xa + 0.8, alto, relleno="#555")
    L.txt(xb + 1.5, yN - alto + 1.5, "casa", fs=1.4, peso="bold", anchor="start")
    L.txt(x0 + w, y0 + h + 3.2, f"H 1:{int(round(1000 / kh, -2))} · V ×{num(kv / kh)[:-3]}", fs=1.3, anchor="end", color=TINTA2)


def lamina_topografia():
    T = E.TOPO
    L = Lamina()
    marco(L, "TOP-01", "TOPOGRAFÍA APROXIMADA (DEM) Y MOVIMIENTO DE TIERRA", 9, escala="1:250 · contexto 1:5000")
    L.txt(122, 22, "PLANO TOPOGRÁFICO DEL LOTE (curvas c/ 0,5 m)", fs=3.6, peso="bold")
    v = Vista(L, 106, 120, 4)
    v.caja(-21.5, -11.5, 28.5, 21.5, borde="#999", ancho=0.3, dash="3 1 0.6 1")
    for (p, q, z) in T["lote"]["curvas_05m"]:
        if -21.5 <= p[0] <= 28.5 and -11.5 <= p[1] <= 21.5:
            mayor = abs(z - round(z)) < 1e-6
            v.poly([p, q], color="#8a6a40" if mayor else C_TOPO, ancho=0.4 if mayor else 0.15)
    # rótulos de curvas mayores (uno por nivel)
    vistos = set()
    for (p, q, z) in T["lote"]["curvas_05m"]:
        if abs(z - round(z)) < 1e-6 and z not in vistos and -18 < p[0] < 26 and 8 < p[1] < 19:
            vistos.add(z)
            X, Y = v.P(*p)
            L.rect(X - 2.2, Y - 1.7, 4.4, 2.4, relleno="#fff")
            L.txt(X, Y + 0.3, f"{int(round(z))}", fs=1.5, color="#8a6a40", peso="bold")
    px0, py0, px1, py1 = (-1.5, -1.5, 13.5, 7.5)
    v.caja(px0, py0, px1, py1, relleno="none", borde="#c0392b", ancho=0.35, dash="1.5 0.8")
    contorno_p1(v)
    v.txt(6, 3.0, f"NPT {num(T['NPT'])}", fs=2.0, peso="bold")
    v.txt(6, 1.8, "plataforma en sector plano" if E.PLATAFORMA_NIVELADA else f"plataforma {num(T['cota_plataforma'])}",
          fs=1.5, color="#c0392b")
    for k, z in T["cotas_esquinas_casa"].items():
        x, y = (float(c) for c in k.strip("()").split(","))  # claves "(x,y)" de topografia.py
        X, Y = v.P(x, y)
        L.circ(X, Y, 0.6, relleno="#7a6040", borde="none")
        L.txt(X + (1.2 if x > 6 else -1.2), Y + (-1.0 if y > 3 else 2.4), num(z), fs=1.3,
              anchor="start" if x > 6 else "end", color="#7a6040")
    for (x, y, et) in ((sum(E.FOSA["x"]) / 2, sum(E.FOSA["y"]) / 2, "fosa"), (E.POZO[0], E.POZO[1], "pozo"),
                       (E.ESTANQUE["x"], E.ESTANQUE["y"], "estanque")):
        X, Y = v.P(x, y)
        L.circ(X, Y, 1.0, relleno="#fff", borde="#333", ancho=0.3)
        L.txt(X, Y + 3.6, f"{et} {num(E.cota_terreno(x, y))}", fs=1.3)
    flecha(L, *v.P(18, 15), *v.P(18 + 8 * math.sin(math.radians(T["rumbo_bajada_deg"])),
                                 15 + 8 * math.cos(math.radians(T["rumbo_bajada_deg"]))), color="#7a6040", ancho=0.45)
    v.txt(19, 16.5, f"baja {num(T['pendiente_media_pct'])[:-1]} % hacia {T['rumbo_bajada_deg']}°", fs=1.5, color="#7a6040", anchor="start")
    norte(L, 32, 46)
    # contexto 1:5000 con curvas de 2 m
    x0, y0, w, h, k = 292, 30, 110, 112, 0.2
    cx, cy = x0 + w / 2, y0 + h / 2
    L.rect(x0, y0, w, h, relleno="#fafaf7", borde="#000", ancho=0.3)
    L.add(f'<clipPath id="ct"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#ct)">')
    for (p, q, z) in T["contexto"]["curvas_2m"]:
        mayor = abs(z / 10 - round(z / 10)) < 1e-6
        L.linea([(cx + (p[0] - 6) * k, cy - (p[1] - 3) * k), (cx + (q[0] - 6) * k, cy - (q[1] - 3) * k)],
                color="#8a6a40" if mayor else C_TOPO, ancho=0.35 if mayor else 0.12)
    with open(os.path.join(AQUI, "sitio", "raw", "osm.json"), encoding="utf-8") as f:
        osm = json.load(f)["elements"]
    for e_ in osm:
        t = e_.get("tags", {})
        if "geometry" in e_ and ("waterway" in t or "highway" in t):
            pts = [(cx + (g["lon"] - E.SITIO["lon"]) * 111320 * math.cos(math.radians(E.SITIO["lat"])) * k,
                    cy - (g["lat"] - E.SITIO["lat"]) * 111320 * k) for g in e_["geometry"]]
            L.linea(pts, color="#5aa0d8" if "waterway" in t else "#555", ancho=0.8 if "waterway" in t else 0.6)
    L.add("</g>")
    L.circ(cx, cy, 5, relleno="none", borde="#c0392b", ancho=0.4)
    L.txt(x0 + 2, y0 + 4, f"CONTEXTO 1:5000 · curvas c/ 2 m ({num(T['contexto']['z_min'])[:-1]}–{num(T['contexto']['z_max'])[:-1]} m)",
          fs=1.8, peso="bold", anchor="start")
    # perfiles
    perfil(L, 298, 152, 104, 30, T["perfil_oeste_este"], "PERFIL OESTE → ESTE (por el sitio, ±200 m)", (0, 12))
    perfil(L, 298, 197, 104, 30, T["perfil_sur_norte"], "PERFIL SUR → NORTE (±200 m)", (0, 6))
    mt = T["movimiento_tierra_m3"]
    if E.PLATAFORMA_NIVELADA:
        filas = [
            ("PLATAFORMA (sector plano del terreno)", "Valor"),
            ("NPT ±0,00 (referencial DEM)", f"{num(T['NPT'])} m s.n.m."),
            ("Área plataforma", f"{int(mt['area_m2'])} m²"),
            (f"Escarpe capa vegetal ({num(E.ESCARPE)} m)", f"{num(mt['area_m2'] * E.ESCARPE)} m³"),
            (f"Base granular compactada ({num(E.BASE_GRANULAR)} m)", f"{num(mt['area_m2'] * E.BASE_GRANULAR)} m³"),
            ("Corte / relleno compensado", "no se requiere"),
        ]
        nota3 = ["3. La casa va en un sector PLANO del terreno (decisión del 20-10-2026). El DEM de 30 m",
                 f"   no lo distingue (marca {num(T['desnivel_bajo_casa'])} m de desnivel): la topografía real lo confirmará.",
                 "   Sólo se retira la capa vegetal y se compacta una base granular al 95 % Proctor.",
                 "4. Aun en plano: plataforma 15 cm sobre el terreno vecino y drenaje perimetral."]
    else:
        filas = [
            ("MOVIMIENTO DE TIERRA (plataforma)", "Valor"),
            ("Cota plataforma / NPT", f"{num(T['cota_plataforma'])} / {num(T['NPT'])}"),
            ("Desnivel natural bajo la casa", f"{num(T['desnivel_bajo_casa'])} m"),
            ("Área plataforma", f"{int(mt['area_m2'])} m²"),
            ("Corte (lado este)", f"{num(mt['corte'])} m³"),
            ("Relleno compactado (lado oeste)", f"{num(mt['relleno'])} m³"),
            ("Balance", f"{num(mt['corte'] - mt['relleno'])} m³ (compensado)"),
        ]
        nota3 = ["3. Plataforma compensada: el corte del lado E rellena el lado O en capas de 20 cm",
                 "   compactadas al 95 % Proctor modificado. Fundaciones del lado O se profundizan",
                 "   hasta terreno natural (no apoyar sobre relleno).",
                 "4. Talud de corte/relleno 1:2 con drenaje al pie; aguas superficiales desviadas al ONO."]
    tabla(L, 15, 182, [52, 22], filas, fs=1.6, alto=4.6)
    notas(L, 105, 182, "NOTAS", [
        f"1. Fuente: {T['fuente']}",
        f"   Resolución {num(T['resolucion_px_m'])} m/px interpolada; precisión vertical ±2–5 m.",
        "2. NO reemplaza un levantamiento topográfico con estación total o GNSS-RTK,",
        "   exigido para el permiso (OGUC 5.1.6). Usar este plano sólo para anteproyecto.",
        *nota3,
        f"5. Pendiente general {num(T['pendiente_media_pct'])[:-1]} % hacia el estero: la fosa y drenes quedan aguas abajo",
        "   de la casa y del pozo (correcto para gravedad y protección del pozo).",
    ], fs=1.55)
    return L
