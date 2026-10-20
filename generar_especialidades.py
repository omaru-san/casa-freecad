"""Láminas 04–07: emplazamiento y orientación, techumbre + aguas lluvias + FV,
ventilación y calefacción, elevaciones y corte. Usa los helpers de generar_laminas.py."""
import json
import math
import os

FV = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculo", "fv_bateria.json"), encoding="utf-8"))

import casa_datos as D
import especialidades_datos as E
import instalaciones_datos as I
from generar_laminas import (C_AF, C_ALC, C_GAS, C_MURO, C_TERRAZA, FUENTE, OX1, OX2, Lamina, Planta,
                             base_plantas, dibujar_arquitectura, leyenda, marco, notas, num, tabla)

AQUI = os.path.dirname(os.path.abspath(__file__))
C_LLUVIA = "#1f8fbf"
C_FV = "#1f4e9c"
C_VENT = "#0a8a7a"
C_TECHO = "#e8e2d6"
C_TIERRA = "#b49a74"
TINTA, TINTA2, GRILLA = "#222", "#666", "#ddd"


class Vista:
    """Transformación mundo (m) -> papel (mm) con escala propia. Si espejo, u crece hacia -x."""

    def __init__(self, L, ox, oy, k, espejo=False):
        self.L, self.ox, self.oy, self.k, self.espejo = L, ox, oy, k, espejo

    def P(self, u, v):
        return self.ox + (-u if self.espejo else u) * self.k, self.oy - v * self.k

    def poly(self, pts, **kw):
        self.L.linea([self.P(*p) for p in pts], **kw)

    def caja(self, u0, v0, u1, v1, relleno="none", borde="none", ancho=0.3, dash=None):
        pts = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        da = f' stroke-dasharray="{dash}"' if dash else ""
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in (self.P(*p) for p in pts))
        self.L.add(f'<polygon points="{d}" fill="{relleno}" stroke="{borde}" stroke-width="{ancho}"{da}/>')

    def txt(self, u, v, s, **kw):
        x, y = self.P(u, v)
        self.L.txt(x, y, s, **kw)


def miles(n):
    return f"{int(round(n)):,}".replace(",", ".")


def flecha(L, x0, y0, x1, y1, color=TINTA, ancho=0.35, cabeza=1.6, dash=None):
    L.linea([(x0, y0), (x1, y1)], color=color, ancho=ancho, dash=dash)
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (1, -1):
        L.linea([(x1, y1), (x1 - cabeza * math.cos(a + s * 0.4), y1 - cabeza * math.sin(a + s * 0.4))],
                color=color, ancho=ancho)


def rotulo(L, x, y, tx, ty, texto, fs=1.7, color=TINTA, anchor="start"):
    L.linea([(x, y), (tx, ty)], color="#888", ancho=0.15)
    L.circ(x, y, 0.4, relleno="#888", borde="none")
    L.txt(tx + (0.8 if anchor == "start" else -0.8), ty + 0.6, texto, fs=fs, anchor=anchor, color=color)


def norte(L, x, y, tam=9):
    L.add(f'<polygon points="{x},{y - tam} {x + tam*0.35},{y + tam*0.3} {x},{y + tam*0.1}" fill="#000"/>')
    L.add(f'<polygon points="{x},{y - tam} {x - tam*0.35},{y + tam*0.3} {x},{y + tam*0.1}" fill="#fff" stroke="#000" stroke-width="0.3"/>')
    L.txt(x, y - tam - 1.5, "N", fs=3.5, peso="bold")
    a = math.radians(E.NORTE_MAGNETICO_DEG)
    L.linea([(x, y), (x + tam * 1.1 * math.sin(a), y - tam * 1.1 * math.cos(a))], color="#a33", ancho=0.25, dash="1 0.6")
    L.txt(x + tam * 1.2 * math.sin(a) + 1, y - tam * 1.1, "NM", fs=1.6, color="#a33", anchor="start")


def contorno_p1(v, **kw):
    for n, x0, y0, x1, y1 in D.RECINTOS_1:
        v.caja(x0, y0, x1, y1, relleno=C_TERRAZA if n in D.EXTERIORES else "#e9e4d8")
    for x1, y1, x2, y2, t in D.MUROS_1:
        if t == D.EXT:
            v.poly([(x1, y1), (x2, y2)], color="#333", ancho=0.5)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# =====================================================================
#  04 EMPLAZAMIENTO Y ORIENTACIÓN
# =====================================================================

def carta_solar(L, cx, cy, R):
    L.txt(cx, cy - R - 8, "CARTA SOLAR (lat. 39,5° S)", fs=2.4, peso="bold")
    for alt in (0, 30, 60):
        L.circ(cx, cy, R * (90 - alt) / 90, relleno="#fff" if alt == 0 else "none", borde="#bbb", ancho=0.15 if alt else 0.3)
        if alt:
            L.txt(cx + 0.8, cy - R * (90 - alt) / 90 + 2.2, f"{alt}°", fs=1.3, color=TINTA2, anchor="start")
    for az, et in ((0, "N"), (90, "E"), (180, "S"), (270, "O")):
        a = math.radians(az)
        L.linea([(cx, cy), (cx + R * math.sin(a), cy - R * math.cos(a))], color=GRILLA, ancho=0.15)
        L.txt(cx + (R + 3) * math.sin(a), cy - (R + 3) * math.cos(a) + 1, et, fs=2.2, peso="bold")
    estilos = {"solsticio_verano_21dic": ("#c77d00", "21 dic"), "equinoccio_21mar": ("#777", "21 mar/sep"),
               "solsticio_invierno_21jun": ("#1f4e9c", "21 jun")}
    for clave, (col, et) in estilos.items():
        tr = E.CLIMA["sol"]["trayectorias"][clave]
        pts = [(cx + R * (90 - al) / 90 * math.sin(math.radians(az)), cy - R * (90 - al) / 90 * math.cos(math.radians(az)))
               for _, al, az in tr["puntos_hora_alt_az"]]
        L.linea(pts, color=col, ancho=0.5)
        for h, al, az in tr["puntos_hora_alt_az"]:
            if abs(h - round(h)) < 1e-6 and int(round(h)) % 2 == 0:
                x = cx + R * (90 - al) / 90 * math.sin(math.radians(az))
                y = cy - R * (90 - al) / 90 * math.cos(math.radians(az))
                L.circ(x, y, 0.5, relleno=col, borde="none")
                if clave == "solsticio_invierno_21jun":
                    L.txt(x, y + 2.6, f"{int(round(h))}h", fs=1.2, color=TINTA2)
        mx, my = pts[len(pts) // 2]
        L.txt(mx, my - 1.5, f"{et} · {tr['altura_mediodia']}°", fs=1.5, color=TINTA, peso="bold")
    L.txt(cx, cy + R + 6, "Sol del mediodía siempre al NORTE. Invierno: 27° de altura, 9 h de sol.", fs=1.5, color=TINTA2)


def rosa_vientos(L, cx, cy, R):
    L.txt(cx, cy - R - 8, "ROSA DE VIENTOS 2010–2025", fs=2.4, peso="bold")
    sect = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    vmax = 45.0
    for p in (15, 30, 45):
        L.circ(cx, cy, R * p / vmax, relleno="none", borde=GRILLA, ancho=0.15)
        L.txt(cx + 0.6, cy - R * p / vmax + 2, f"{p}%", fs=1.2, color=TINTA2, anchor="start")
    for i, s in enumerate(sect):
        a = math.radians(i * 45)
        L.txt(cx + (R + 3) * math.sin(a), cy - (R + 3) * math.cos(a) + 0.8, s, fs=2.0, peso="bold")

    def poligono(datos, relleno, borde, ancho, dash=None):
        pts = []
        for i, s in enumerate(sect):
            r = R * datos[s] / vmax
            a = math.radians(i * 45)
            pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
        L.linea(pts, color=borde, ancho=ancho, cerrar=True, relleno=relleno, dash=dash)

    v = E.CLIMA["viento"]
    poligono(v["rosa_total_pct"], "#d9d9d9", "#999", 0.3)
    poligono(v["rosa_con_lluvia_pct"], "none", C_LLUVIA, 0.6)
    poligono(v["rosa_vientos_fuertes_30kmh_pct"], "none", "#b03a2e", 0.6, "1.2 0.6")
    y = cy + R + 5
    for col, txt, dash in (("#999", "Todas las horas", None), (C_LLUVIA, "Horas con lluvia", None),
                           ("#b03a2e", "Viento ≥ 30 km/h", "1.2 0.6")):
        L.linea([(cx - 22, y), (cx - 16, y)], color=col, ancho=0.6, dash=dash)
        L.txt(cx - 15, y + 0.6, txt, fs=1.5, anchor="start")
        y += 3.6


def mapa_contexto(L, x0, y0, w, h):
    """Mapa real de OpenStreetMap alrededor del sitio (1:5000)."""
    k = 0.2  # mm por metro
    cx, cy = x0 + w / 2, y0 + h / 2
    L.rect(x0, y0, w, h, relleno="#fafaf7", borde="#000", ancho=0.3)
    L.add(f'<clipPath id="cm"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#cm)">')
    with open(os.path.join(AQUI, "sitio", "raw", "osm.json"), encoding="utf-8") as f:
        osm = json.load(f)["elements"]
    lat0, lon0 = E.SITIO["lat"], E.SITIO["lon"]
    for e in osm:
        if "geometry" not in e:
            continue
        t = e.get("tags", {})
        pts = [(cx + (g["lon"] - lon0) * 111320 * math.cos(math.radians(lat0)) * k,
                cy - (g["lat"] - lat0) * 111320 * k) for g in e["geometry"]]
        if "waterway" in t:
            L.linea(pts, color="#5aa0d8", ancho=0.8)
        elif "highway" in t:
            L.linea(pts, color="#999" if t["highway"] in ("track", "path") else "#555",
                    ancho=0.5 if t["highway"] in ("track", "path") else 1.0,
                    dash="1 0.6" if t["highway"] in ("track", "path") else None)
        elif "building" in t:
            L.linea(pts, color="#888", ancho=0.2, cerrar=True, relleno="#ccc")
    L.add("</g>")
    L.rect(cx - 12 * k / 2, cy - 6 * k / 2, 12 * k, 6 * k, relleno="#c0392b")
    L.circ(cx, cy, 6, relleno="none", borde="#c0392b", ancho=0.4)
    L.txt(cx + 7, cy - 4, "SITIO", fs=2, peso="bold", color="#c0392b", anchor="start")
    L.txt(x0 + 2, y0 + 4, "CONTEXTO 1:5000 (OpenStreetMap)", fs=2.0, peso="bold", anchor="start")
    for c in E.SITIO["caminos_cercanos"][:3]:
        if c["nombre"]:
            a = math.radians(c["rumbo_desde_sitio"])
            L.txt(cx + c["dist_m"] * k * math.sin(a) - 1, cy - c["dist_m"] * k * math.cos(a) - 8,
                  c["nombre"], fs=1.6, anchor="end", peso="bold")
    L.txt(x0 + 2, y0 + h - 6, "Camino vecinal a 99 m al E · Ruta T-240 a 267 m al E", fs=1.4, anchor="start")
    L.txt(x0 + 2, y0 + h - 3, "Estero/cauce a 159 m al NO (terreno 4–5 m más bajo)", fs=1.4, anchor="start", color="#2f6fa0")
    L.linea([(x0 + w - 24, y0 + h - 3), (x0 + w - 4, y0 + h - 3)], ancho=0.4)
    L.txt(x0 + w - 14, y0 + h - 4.2, "100 m", fs=1.4)


def lamina_emplazamiento():
    L = Lamina()
    marco(L, "EMP-01", "EMPLAZAMIENTO Y ORIENTACIÓN SOLAR", 4, escala="1:250 · contexto 1:5000")
    L.txt(122, 22, "EMPLAZAMIENTO EN EL TERRENO", fs=4, peso="bold")
    v = Vista(L, 106, 120, 4)
    # deslinde referencial
    v.caja(-21.5, -11.5, 28.5, 21.5, borde="#999", ancho=0.3, dash="3 1 0.6 1")
    v.txt(28, 20.4, "Deslinde referencial (definir con plano de loteo/escritura)", fs=1.6, anchor="end", color=TINTA2)
    # curvas de nivel (DEM, equidistancia 0,5 m)
    for (p, q, z) in E.TOPO["lote"]["curvas_05m"]:
        if -21.5 <= p[0] <= 28.5 and -11.5 <= p[1] <= 21.5:
            mayor = abs(z - round(z)) < 1e-6
            v.poly([p, q], color="#b49a74", ancho=0.3 if mayor else 0.12)
    for xs_, ys_ in ((-18, 12), (-8, -9), (24, 10), (25, -6), (6, 14)):
        v.txt(xs_, ys_, f"{E.cota_terreno(xs_, ys_):.0f}", fs=1.4, color="#8a6a40")
    # cortaviento
    for t in [i / 10 for i in range(11)]:
        (ax, ay), (bx, by), (cx_, cy_) = E.CORTAVIENTO
        x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * bx + t ** 2 * cx_
        y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * by + t ** 2 * cy_
        px, py = v.P(x, y)
        L.circ(px, py, 4.5, relleno="#cfe3c4", borde="#6a9a5a", ancho=0.3)
    v.txt(-5.5, 18.6, "Cortaviento de árboles nativos al NO / O", fs=1.8, peso="bold", color="#3e6e30", anchor="start")
    v.txt(-5.5, 17.5, "(frena viento con lluvia; lejos para no sombrear paneles)", fs=1.4, color="#3e6e30", anchor="start")
    # acceso y estacionamiento
    v.poly(E.ACCESO, color="#d8d3c8", ancho=2.5 * 4)
    v.poly(E.ACCESO, color="#aaa", ancho=0.2, dash="2 1")
    v.txt(23, -2.6, "ACCESO desde camino vecinal (E)", fs=1.8, peso="bold")
    v.caja(*E.ESTACIONAMIENTO, relleno="#eeeae0", borde="#999", ancho=0.2)
    v.txt((E.ESTACIONAMIENTO[0] + E.ESTACIONAMIENTO[2]) / 2, -6.5, "Estacionamiento", fs=1.6)
    # drenaje perimetral
    o = E.DRENAJE_PERIMETRAL_OFFSET
    v.poly([(-o, 2 - o), (-o, 6 + o), (12 + o, 6 + o), (12 + o, -o), (2 - o, -o), (2 - o, 2 - o), (-o, 2 - o)],
           color=C_LLUVIA, ancho=0.35, dash="1.5 0.8")
    v.poly([(-o, 6 + o), (-5.0, 9.5)], color=C_LLUVIA, ancho=0.35, dash="1.5 0.8")
    v.txt(-5.2, 10.3, "Descarga drenaje → NO", fs=1.4, color=C_LLUVIA)
    # casa
    contorno_p1(v)
    v.caja(*D.LOSA_2, borde="#333", ancho=0.3, dash="2 1")
    v.caja(E.TECHO_X[0], E.TECHO_Y[0], E.TECHO_X[1], E.TECHO_Y[1], borde="#777", ancho=0.2, dash="0.6 0.6")
    v.poly([(E.TECHO_X[0], E.CUMBRERA_Y), (E.TECHO_X[1], E.CUMBRERA_Y)], color="#777", ancho=0.2, dash="0.6 0.6")
    v.txt(6.2, 2.2, "VIVIENDA", fs=2.4, peso="bold")
    v.txt(6.2, 1.2, f"NPT ±0,00 = {num(E.NPT_MSNM)} m s.n.m.", fs=1.5)
    for x0, x1, s0, s1, et in E.PANELES:
        v.caja(*E.panel_a_planta(x0, x1, s0, s1), relleno=C_FV if et == 1 else "none", borde="#fff", ancho=0.2)
    # aguas lluvias
    ex, ey = E.ESTANQUE["x"], E.ESTANQUE["y"]
    v.poly([(1.75, 6.6), (1.75, 7.6), (ex, 7.6), (ex, ey)], color=C_LLUVIA, ancho=0.35)
    v.poly([(-0.5, 6.45), (-0.5, 7.6), (1.75, 7.6)], color=C_LLUVIA, ancho=0.35)
    v.poly([(12.25, 6.6), (12.25, 7.6)], color=C_LLUVIA, ancho=0.35)
    px, py = v.P(ex, ey)
    L.circ(px, py, 1.1 * 4, relleno="#d6ecf7", borde=C_LLUVIA, ancho=0.4)
    v.txt(ex, ey - 0.3, "EAL", fs=1.6, peso="bold", color=C_LLUVIA)
    v.txt(ex + 1.4, ey + 0.4, f"Estanque aguas lluvias {miles(E.ESTANQUE['litros'])} L", fs=1.5,
          anchor="start", color=C_LLUVIA)
    ix0, iy0, ix1, iy1 = E.INFILTRACION_LLUVIAS
    v.poly([(1.75, -0.6), (1.75, -4.8), (ix1 + 0.5, -4.8)], color=C_LLUVIA, ancho=0.35)
    v.poly([(12.25, -0.6), (12.25, -4.8), (1.75, -4.8)], color=C_LLUVIA, ancho=0.35)
    v.caja(ix0, iy0, ix1, iy1, relleno="#d6ecf7", borde=C_LLUVIA, ancho=0.3)
    v.txt((ix0 + ix1) / 2, iy0 - 1.0, "Infiltración aguas lluvias (faldón sur)", fs=1.4, color=C_LLUVIA)
    # alcantarillado -> fosa -> drenes
    v.poly([(-1.2, -1.3), (E.FOSA["x"][1], -1.7)], color=C_ALC, ancho=0.5)
    v.caja(E.FOSA["x"][0], E.FOSA["y"][0], E.FOSA["x"][1], E.FOSA["y"][1], relleno="#efe2d4", borde=C_ALC, ancho=0.4)
    v.txt(sum(E.FOSA["x"]) / 2, -1.9, "FOSA", fs=1.5, peso="bold", color=C_ALC)
    cdx, cdy = E.CAMARA_DISTRIBUCION
    v.poly([(E.FOSA["x"][0], -1.7), (cdx, cdy)], color=C_ALC, ancho=0.4)
    v.caja(cdx - 0.4, cdy - 0.4, cdx + 0.4, cdy + 0.4, relleno="#fff", borde=C_ALC, ancho=0.3)
    for dr in E.DRENES:
        v.poly([(cdx, cdy), dr[0]], color=C_ALC, ancho=0.2)
        v.poly(dr, color=C_ALC, ancho=0.35, dash="2 0.8")
    v.txt(-15, 1.6, "Drenes de infiltración (3 × 12 m)", fs=1.6, peso="bold", color=C_ALC)
    v.txt(-15, 0.7, "zanja 0,6 m, grava, tubo PVC Ø100 perforado", fs=1.3, color=C_ALC)
    # agua potable, gas, electricidad
    v.poly([E.POZO, (E.POZO[0], -2.2), (13.2, -2.2), (13.2, I.MEDIDOR_AGUA[1]), I.MEDIDOR_AGUA], color=C_AF, ancho=0.35)
    v.txt(17.5, -1.6, "Impulsión pozo → hidropack (PE Ø32)", fs=1.4, color=C_AF)
    px, py = v.P(*E.POZO)
    L.circ(px, py, 3, relleno="#e3efff", borde=C_AF, ancho=0.4)
    v.txt(E.POZO[0], E.POZO[1] - 1.8, "Pozo profundo + bomba sumergible", fs=1.4, color=C_AF)
    v.poly([(28.5, 3.4), (I.MEDIDOR_ELEC[0], I.MEDIDOR_ELEC[1])], color="#000", ancho=0.3, dash="3 1")
    v.txt(24, 4.0, "Empalme eléctrico aéreo (distribuidora)", fs=1.4)
    px, py = v.P(*I.MEDIDOR_GAS)
    L.rect(px - 1.5, py - 1.5, 3, 3, relleno="#fff6d6", borde=C_GAS, ancho=0.3)
    # distancias
    d_fosa = E.FOSA["x"][1] - 0.0
    d_dren = abs(E.DRENES[0][0][0])
    d_pozo = min(dist(E.POZO, p) for dr in E.DRENES for p in dr)
    y_c = -9.6
    v.poly([(E.FOSA["x"][1], y_c), (0, y_c)], color="#555", ancho=0.15)
    v.txt(E.FOSA["x"][1] / 2, y_c + 0.4, f"{num(abs(d_fosa))} m", fs=1.4)
    v.txt(-14, -9.0, f"Pozo ↔ drenes: {num(d_pozo)} m", fs=1.4, color=TINTA2)
    # pendiente
    flecha(L, *v.P(20, 15), *v.P(14, 19), color="#7a6040", ancho=0.4)
    v.txt(21, 14.6, f"Pendiente natural ≈ {num(E.TOPO['pendiente_media_pct'])[:-1]} % (DEM)", fs=1.5, color="#7a6040", anchor="start")
    v.txt(21, 13.6, "baja hacia el ONO (estero) · curvas c/0,5 m", fs=1.5, color="#7a6040", anchor="start")
    norte(L, 32, 46)
    # escala gráfica
    x0s, ys = 30, 162
    for i in range(5):
        L.rect(x0s + i * 8, ys, 8, 1.2, relleno="#000" if i % 2 == 0 else "#fff", borde="#000", ancho=0.2)
    L.txt(x0s, ys + 4, "0", fs=1.5)
    L.txt(x0s + 40, ys + 4, "10 m", fs=1.5)

    carta_solar(L, 272, 70, 30)
    rosa_vientos(L, 365, 70, 30)
    mapa_contexto(L, 300, 122, 110, 112)

    an = E.CLIMA["anual"]
    tr = E.CLIMA["tendencias_y_proyeccion"]
    notas(L, 236, 128, "DECISIONES DE DISEÑO", [
        "• Eje largo E–O; living, oficina 2",
        "  y dormitorios al NORTE.",
        "• Servicios (baños, lavandería,",
        "  escalera) al SUR: colchón térmico.",
        "• Faldón norte 35° = óptimo FV.",
        "• Lluvia y temporales vienen del N–NO:",
        "  aleros 60 cm, ventanas DVH con",
        "  burlete, sello de fachada norte.",
        "• Cortaviento al NO a ≥ 15 m.",
        "• Fosa y drenes aguas abajo (O–NO),",
        "  a > 20 m de pozos (DS 236).",
        "• Piso a +0,30 y drenaje perimetral",
        "  (humedad 88 % en invierno).",
    ], fs=1.6)
    filas = [["", *[m["mes"] for m in E.CLIMA["mensual"]]]]
    claves = [("T máx °C", "t_max"), ("T mín °C", "t_min"), ("Lluvia mm", "lluvia_mm"), ("Días lluvia", "dias_lluvia"),
              ("Humedad %", "humedad_rel"), ("Radiación kWh/m²d", "radiacion_kwh_m2_dia"), ("Sol h/día", "sol_horas_dia"),
              ("Heladas días", "heladas_dias")]
    for et, k in claves:
        dec = 1 if k in ("t_max", "t_min", "radiacion_kwh_m2_dia", "sol_horas_dia", "heladas_dias") else 0
        filas.append([et, *[f"{m[k]:.{dec}f}".replace(".", ",") for m in E.CLIMA["mensual"]]])
    tabla(L, 15, 178, [31] + [15.3] * 12, filas, fs=1.6, alto=4.6)
    L.txt(15, 176, f"CLIMA DEL SITIO {E.CLIMA['periodo']} — reanálisis ERA5 (Open-Meteo)", fs=2.2, anchor="start", peso="bold")
    resumen = [
        f"Lluvia anual {num(an['lluvia_media_mm'])[:-3]} mm (rango {int(an['lluvia_min_mm'])}–{int(an['lluvia_max_mm'])}) · "
        f"{int(an['dias_lluvia'])} días con lluvia · máx. diaria {int(E.CLIMA['extremos_lluvia']['max_diaria_mm_registrada'])} mm",
        f"T media {num(an['t_media'])} °C · mín. abs. {num(an['t_min_absoluta'])} °C · {int(an['heladas_dias'])} heladas/año · "
        f"sin nieve · grados-día calefacción (base 15) {int(an['grados_dia_calefaccion_base15'])}",
        f"Racha máx. {int(an['racha_max_kmh'])} km/h (del N–NO) · radiación horizontal {int(an['radiacion_horizontal_kwh_m2'])} kWh/m²·año",
        f"Tendencia 1995–2025: {int(tr['lluvia_mm_por_decada'])} mm/década de lluvia → proyección lineal 2050 ≈ "
        f"{int(tr['proyeccion_lineal_2050']['lluvia_mm'])} mm/año. Veranos más secos: guardar agua lluvia.",
    ]
    for i, t in enumerate(resumen):
        L.txt(15, 228 + i * 3.6, t, fs=1.65, anchor="start")
    L.txt(15, 245, "Fuentes: Open-Meteo Historical API (ERA5), PVGIS 5.2 (JRC), OpenStreetMap. Detalle en sitio/INFORME_SITIO.md",
          fs=1.4, anchor="start", color=TINTA2)
    return L


# =====================================================================
#  05 TECHUMBRE, AGUAS LLUVIAS Y FOTOVOLTAICO
# =====================================================================

def grafico_produccion(L, x0, y0, w, h):
    """Barras: producción FV mensual simulada; línea: consumo mensual (supuesto) — una sola escala."""
    pv = [m["pv"] for m in FV["mensual"]]
    carga = [m["carga"] for m in FV["mensual"]]
    meses = [m["mes"] for m in E.CLIMA["mensual"]]
    vmax = 1400
    s = FV["sistema"]
    L.txt(x0, y0 - 6, f"Producción vs consumo mensual — {s['paneles']} × {s['wp']} Wp ({num(s['kwp'])} kWp)",
          fs=2.2, anchor="start", peso="bold")
    L.txt(x0, y0 - 2.6, "kWh/mes · simulación horaria PVGIS 2016–2020 · barras = producción, línea = consumo supuesto",
          fs=1.5, anchor="start", color=TINTA2)
    for v_ in range(0, vmax + 1, 200):
        y = y0 + h - h * v_ / vmax
        L.linea([(x0 + 8, y), (x0 + w, y)], color=GRILLA if v_ else "#999", ancho=0.15)
        L.txt(x0 + 6.5, y + 0.6, str(v_), fs=1.3, anchor="end", color=TINTA2)
    paso = (w - 10) / 12
    pts = []
    for i, (m, d_) in enumerate(zip(meses, pv)):
        bx = x0 + 10 + i * paso
        bh = h * d_ / vmax
        L.add(f'<path d="M{bx + 0.5:.2f},{y0 + h:.2f} v{-bh + 1:.2f} q0,-1 1,-1 h{paso - 3:.2f} q1,0 1,1 v{bh - 1:.2f} Z" fill="{C_FV}"/>')
        L.txt(bx + paso / 2 - 0.5, y0 + h + 3, m, fs=1.3, color=TINTA2)
        if i in (0, 5):
            L.txt(bx + paso / 2 - 0.5, y0 + h - bh - 1.2, str(int(round(d_))), fs=1.4, color=TINTA)
        pts.append((bx + paso / 2 - 0.5, y0 + h - h * carga[i] / vmax))
    L.linea(pts, color="#333", ancho=0.5)
    for p in pts:
        L.circ(*p, 0.9, relleno="#333", borde="#fff", ancho=0.3)
    L.txt(pts[-1][0] + 2, pts[-1][1] + 0.6, "consumo", fs=1.4, anchor="start", color="#333")


def unilineal_fv(L, x0, y0):
    s = FV["sistema"]
    L.txt(x0, y0 - 4, "DIAGRAMA UNILINEAL FV HÍBRIDO (net billing + respaldo)", fs=2.4, anchor="start", peso="bold")
    cajas = [("Paneles", f"{s['paneles']} × {s['wp']} Wp", f"{num(s['kwp'])} kWp · 35° N"),
             ("Caja DC", "Fusibles + DPS", "Seccionador DC"),
             ("Inversor", f"Híbrido {num(s['inversor_kw'])[:-3]} kW", "monofásico"),
             ("TDA", "Autom. 2×32 A", "+ subtablero resp."),
             ("Medidor", "Bidireccional", "distribuidora"),
             ("Red", "Distribuidora", "BT 220 V")]
    w, h, gap = 18.5, 14, 4.8
    for i, (t, a, b) in enumerate(cajas):
        x = x0 + i * (w + gap)
        L.rect(x, y0, w, h, relleno="#eef3fb" if i in (0, 2) else "#fff", borde=C_FV if i in (0, 2) else "#000", ancho=0.35)
        L.txt(x + w / 2, y0 + 4.2, t, fs=2.0, peso="bold")
        L.txt(x + w / 2, y0 + 8.2, a, fs=1.4)
        L.txt(x + w / 2, y0 + 11.4, b, fs=1.4, color=TINTA2)
        if i:
            flecha(L, x - gap, y0 + h / 2, x - 0.6, y0 + h / 2, ancho=0.35, cabeza=1.2)
    xi = x0 + 2 * (w + gap)
    L.rect(xi, y0 + h + 8, w, 11, relleno=C_FV, borde=C_FV, ancho=0.35)
    L.txt(xi + w / 2, y0 + h + 12.6, "Batería", fs=2.0, peso="bold", color="#fff")
    L.txt(xi + w / 2, y0 + h + 16.6, f"LiFePO4 {num(s['bateria_kwh'])[:-3]} kWh", fs=1.4, color="#fff")
    flecha(L, xi + w / 2 - 2, y0 + h, xi + w / 2 - 2, y0 + h + 7.4, ancho=0.35, cabeza=1.2)
    flecha(L, xi + w / 2 + 2, y0 + h + 8, xi + w / 2 + 2, y0 + h + 0.6, ancho=0.35, cabeza=1.2)
    L.txt(x0, y0 + h + 26, "Respaldo ante cortes: C1, C2, C4 y C8 (bomba pozo). Puesta a tierra ≤ 20 Ω. Trámite: TE4 (SEC) + distribuidora.",
          fs=1.45, anchor="start", color=TINTA2)


def lamina_techumbre():
    L = Lamina()
    marco(L, "TEC-01", "TECHUMBRE, AGUAS LLUVIAS Y PANELES FV", 5)
    L.txt(OX1 + 60, 22, "PLANTA DE TECHUMBRE", fs=4, peso="bold")
    pl = Planta(L, OX1)
    # planta P1 de referencia muy tenue
    for n, x0, y0, x1, y1 in D.RECINTOS_1:
        pl.caja(x0, y0, x1, y1, relleno="none", borde="#ccc", ancho=0.12)
    # techo principal (dos aguas)
    tx0, tx1 = E.TECHO_X
    ty0, ty1 = E.TECHO_Y
    pl.caja(tx0, ty0, tx1, ty1, relleno=C_TECHO, borde="#000", ancho=0.4)
    pl.poly([(tx0, E.CUMBRERA_Y), (tx1, E.CUMBRERA_Y)], color="#000", ancho=0.5)
    for k in range(1, 22):
        x = tx0 + k * (tx1 - tx0) / 22
        pl.poly([(x, ty0), (x, ty1)], color="#d2c9b8", ancho=0.12)
    # techo bajo
    bx0, bx1 = E.TECHO_BAJO["x"]
    by0, by1 = E.TECHO_BAJO["y"]
    pl.caja(bx0, by0, bx1, by1, relleno=C_TECHO, borde="#000", ancho=0.4)
    # paneles
    for x0, x1, s0, s1, et in E.PANELES:
        pl.caja(*E.panel_a_planta(x0, x1, s0, s1), relleno=C_FV if et == 1 else "#fff", borde="#fff", ancho=0.4)
        if et == 2:
            a = E.panel_a_planta(x0, x1, s0, s1)
            pl.poly([(a[0], a[1]), (a[2], a[3])], color=C_FV, ancho=0.12)
    # pendientes
    for y_a, y_b, et in ((4.85, 6.35, "35° (70 %)"), (1.15, -0.25, "35° (70 %)")):
        x, ya = pl.P(1.95, y_a)
        _, yb = pl.P(1.95, y_b)
        flecha(L, x, ya, x, yb, ancho=0.35, cabeza=1.4)
        L.txt(x + 1.6, (ya + yb) / 2, et, fs=1.6, anchor="start", rot=-90)
    x, y = pl.P(1.7, 4.1)
    flecha(L, x, y, x - 18, y, ancho=0.3, cabeza=1.2)
    L.txt(x - 9, y - 1.2, f"{int(round(E.TECHO_BAJO['pendiente']))}°", fs=1.5)
    pl.L.txt(*pl.P(7.0, 3.25), "CUMBRERA  +" + num(E.Z_CUMBRERA), fs=1.6, peso="bold")
    # canaletas y bajadas
    for c in E.CANALETAS:
        pl.poly(c["pts"], color=C_LLUVIA, ancho=0.9)
    for x, y, dest in E.BAJADAS:
        px, py = pl.P(x, y)
        L.circ(px, py, 1.3, relleno="#fff", borde=C_LLUVIA, ancho=0.45)
        L.txt(px, py + (3.6 if y < 3 else -2.2), "BLL Ø90", fs=1.3, color=C_LLUVIA, peso="bold")
    # pasadas de cubierta
    for x, y, cod in ((1.0, 5.5, "Cañón estufa Ø125"), (7.5, 0.15, "Ducto calefont Ø100"), (4.55, 0.5, "Vent. B.A.S. Ø75"),
                      (6.1, 1.75, "Extractor baño P2")):
        px, py = pl.P(x, y)
        L.rect(px - 1, py - 1, 2, 2, relleno="#555", borde="none")
        L.txt(px + 1.8, py + 4.2 if y < 3 else py - 1.8, cod, fs=1.3, anchor="start", color=TINTA2)

    unilineal_fv(L, 200, 42)
    grafico_produccion(L, 200, 104, 135, 50)

    # cálculo aguas lluvias
    filas = [("Superficie", "Área m²", "Q (L/s)", "Canaleta", "Bajadas")]
    for c in E.CANALETAS:
        n_baj = sum(1 for b in E.BAJADAS if (c["nombre"] == "Canaleta norte" and b[1] > 6)
                    or (c["nombre"] == "Canaleta sur" and b[1] < 0) or (c["nombre"] == "Canaleta techo bajo" and b[0] < 0))
        filas.append((c["nombre"].replace("Canaleta ", "Faldón "), num(c["area_m2"]), num(E.caudal_ls(c["area_m2"])),
                      "Semicirc. 125 mm, pend. 0,5 %", f"{n_baj} × Ø90"))
    tabla(L, 15, 182, [30, 16, 16, 44, 18], filas, fs=1.6, alto=4.8)
    L.txt(15, 179, f"AGUAS LLUVIAS — intensidad de diseño {E.I_DISENO} mm/h (C = 0,95)", fs=2.2, anchor="start", peso="bold")
    cosecha = E.AREA_CAPTACION * E.CLIMA["anual"]["lluvia_media_mm"] * E.COEF_ESCORRENTIA / 1000
    cos_ene = E.AREA_CAPTACION * E.CLIMA["mensual"][0]["lluvia_mm"] * E.COEF_ESCORRENTIA
    notas(L, 15, 210, "COSECHA DE AGUAS LLUVIAS", [
        f"Faldón norte + techo bajo → estanque {miles(E.ESTANQUE['litros'])} L (riego, WC, lavado).",
        f"Captación anual ≈ {miles(cosecha)} m³; enero ≈ {miles(round(cos_ene, -2))} L → el estanque se llena en invierno",
        "y cubre parte del verano seco. Filtro de primeras aguas + rebalse a infiltración.",
        "Agua de techo con paneles es apta para riego/WC, NO para beber sin tratamiento.",
    ], fs=1.6)
    an, ae = FV["anual"], FV["escenario_electrico"]["anual"]
    rc = FV["respaldo_corte"]
    notas(L, 140, 182, "SIMULACIÓN HORARIA FV + BATERÍA (5 años)", [
        f"Producción {miles(an['pv'])} kWh/año · consumo supuesto {miles(an['carga'])} kWh/año (casa + bomba pozo).",
        f"Autosuficiencia {int(an['autosuficiencia_pct'])} % · {int(an['dias_sin_red'])} días/año sin comprar a la red.",
        f"Batería entrega {miles(an['bateria'])} kWh/año (~{int(an['ciclos'])} ciclos) · inyección a red {miles(an['exporta'])} kWh.",
        f"Junio–julio: autosuficiencia 83 %; la red cubre ~{int(FV['mensual'][5]['importa'])} kWh/mes.",
        f"Corte de luz: {num(rc['horas_bateria_llena'])[:-1]} h con batería llena a {num(rc['carga_critica_kw'])} kW (reserva 20 % siempre).",
        f"Escenario todo eléctrico (bomba de calor + termo BC, sin gas/pellet):",
        f"  consumo {miles(ae['carga'])} kWh · autosuficiencia {int(ae['autosuficiencia_pct'])} % · igual exporta "
        f"{miles(ae['exporta'])} > importa {miles(ae['importa'])}.",
        "Rieles de aluminio anclados a cerchas; paneles apaisados 3 × 4.",
    ], fs=1.55)
    leyenda(L, 345, 40, [
        (lambda L, x, y: L.rect(x - 3, y - 1.5, 6, 3, relleno=C_FV), "Panel FV 625 Wp"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_LLUVIA, ancho=0.9), "Canaleta"),
        (lambda L, x, y: L.circ(x, y, 1.3, relleno="#fff", borde=C_LLUVIA, ancho=0.45), "Bajada aguas lluvias"),
        (lambda L, x, y: L.rect(x - 1, y - 1, 2, 2, relleno="#555"), "Pasada de cubierta"),
        (lambda L, x, y: flecha(L, x - 3, y, x + 3, y, ancho=0.35, cabeza=1.2), "Sentido de caída"),
    ])
    L.txt(345, 92, "Cubierta: zinc-alum prepintado", fs=1.6, anchor="start")
    L.txt(345, 95.5, "0,4 mm sobre fieltro y OSB.", fs=1.6, anchor="start")
    L.txt(345, 99, "Fijación para rachas de 124 km/h.", fs=1.6, anchor="start")
    return L


# =====================================================================
#  06 VENTILACIÓN, CALEFACCIÓN Y HUMEDAD
# =====================================================================

def sim_vent(L, x, y, cod):
    L.circ(x, y, 2.0, relleno="#e6f4f1", borde=C_VENT, ancho=0.35)
    L.txt(x, y + 0.6, cod, fs=1.5, peso="bold", color=C_VENT)


def lamina_ventilacion():
    L = Lamina()
    p1, p2 = base_plantas(L, tenue=True, areas=False)
    marco(L, "VEN-01", "VENTILACIÓN, CALEFACCIÓN Y HUMEDAD", 6)
    for piso, pl in ((1, p1), (2, p2)):
        for pi, pts in E.VENT_CRUZADA:
            if pi != piso:
                continue
            P = [pl.P(*p) for p in pts]
            L.linea(P[:-1] + [P[-1]], color=C_VENT, ancho=0.45, dash="2 0.8")
            flecha(L, *P[-2], *P[-1], color=C_VENT, ancho=0.45, cabeza=1.6)
        ventanas = D.VENTANAS_1 if piso == 1 else D.VENTANAS_2
        for pi, idx in E.MICROVENT:
            if pi != piso:
                continue
            x, y, w, o = ventanas[idx][:4]
            px, py = pl.P(x, y)
            L.rect(px - 1.6, py - 1.6, 3.2, 3.2, relleno="#fff", borde=C_VENT, ancho=0.3)
            L.txt(px, py + 0.55, "MV", fs=1.1, peso="bold", color=C_VENT)
        for pi, cod, x, y, _ in E.ELEMENTOS_VENT:
            if pi == piso:
                sim_vent(L, *pl.P(x, y), cod)
    # cañón estufa y toma de aire
    leyenda(L, 345, 40, [
        (lambda L, x, y: flecha(L, x - 3.5, y, x + 3.5, y, color=C_VENT, ancho=0.45, cabeza=1.4), "Ventilación cruzada N→S"),
        (lambda L, x, y: (L.rect(x - 1.6, y - 1.6, 3.2, 3.2, relleno="#fff", borde=C_VENT, ancho=0.3),
                          L.txt(x, y + 0.55, "MV", fs=1.1, peso="bold", color=C_VENT)), "Microventilación en ventana"),
        (lambda L, x, y: sim_vent(L, x, y, "EX"), "Extractor 25 L/s c/ timer"),
        (lambda L, x, y: sim_vent(L, x, y, "CA"), "Campana cocina al exterior"),
        (lambda L, x, y: sim_vent(L, x, y, "DC"), "Ducto evacuación calefont"),
        (lambda L, x, y: sim_vent(L, x, y, "RS"), "Rejilla ventilación superior"),
        (lambda L, x, y: sim_vent(L, x, y, "RI"), "Rejilla ventilación inferior"),
        (lambda L, x, y: sim_vent(L, x, y, "ES"), "Estufa pellet certificada"),
        (lambda L, x, y: sim_vent(L, x, y, "TA"), "Toma aire exterior estufa"),
        (lambda L, x, y: sim_vent(L, x, y, "DH"), "Control humedad lavandería"),
        (lambda L, x, y: sim_vent(L, x, y, "VT"), "Ventilación alcantarillado"),
    ])
    # balance térmico simple
    env = E.ENVOLVENTE
    filas = [("Elemento", "Área m²", "U W/m²K", "U·A W/K")]
    tot = 0.0
    for nombre, area, u in env["areas"]:
        filas.append((nombre, num(area), num(u), num(area * u)))
        tot += area * u
    vol = 125 * 2.5
    hv = 0.34 * env["renovaciones_h"] * vol
    filas.append((f"Ventilación ({num(env['renovaciones_h'])} ren/h)", num(vol) + " m³", "—", num(hv)))
    tot += hv
    tabla(L, 15, 180, [52, 18, 18, 18], filas, fs=1.6, alto=4.6)
    gd = E.CLIMA["anual"]["grados_dia_calefaccion_base15"]
    demanda = tot * gd * 24 / 1000
    pot = tot * (20 - E.CLIMA["anual"]["t_min_absoluta"]) / 1000
    L.txt(15, 177, "BALANCE TÉRMICO ESTIMADO (envolvente propuesta)", fs=2.2, anchor="start", peso="bold")
    y_fin = 180 + 4.6 * len(filas) + 4
    L.txt(15, y_fin, f"Pérdida total ≈ {num(tot)} W/K → potencia de diseño ≈ {num(pot)} kW (20 °C int. / "
          f"{num(E.CLIMA['anual']['t_min_absoluta'])} °C ext.)", fs=1.7, anchor="start", peso="bold")
    L.txt(15, y_fin + 3.8, f"Demanda anual ≈ {miles(round(demanda, -2))} kWh ({int(gd)} grados-día base 15 °C) ≈ "
          f"{int(round(demanda / 125))} kWh/m²·año", fs=1.7, anchor="start")
    L.txt(15, y_fin + 7.6, f"≈ {int(round(demanda / 4800 * 1.15 * 1000 / 15, -1))} sacos de pellet de 15 kg/año "
          "(4,8 kWh/kg, rend. 87 %)", fs=1.7, anchor="start", color=TINTA2)
    notas(L, 140, 180, "CRITERIOS (humedad media invernal 88 %)", [
        "1. Ventilación cruzada norte-sur en todos los recintos habitables.",
        "2. Ventilación permanente con microventilación en marcos (MV)",
        "   + extracción mecánica en baños: evita condensación y hongos.",
        "3. Puertas interiores con 1 cm bajo la hoja (paso de aire).",
        "4. Calefont (DS 66 SEC): preferir tipo C estanco/tiro forzado;",
        "   rejillas y ducto según potencia, calculados por instalador SEC.",
        "5. Estufa a pellet certificada SEC, con toma de aire exterior;",
        "   cañón ≥ 0,6 m sobre la cumbrera dentro de 3 m (≈ +8,0 m).",
        "6. Barrera de vapor al lado cálido; barrera de humedad hidrófuga",
        "   respirable al exterior; sello de vanos con cinta.",
        "7. Alternativa superior: ventilación mecánica con recuperador",
        "   de calor (VMC) — recomendable con hermeticidad alta.",
        "8. No secar ropa al interior sin extracción/deshumidificador.",
    ], fs=1.55)
    return L


# =====================================================================
#  07 ELEVACIONES Y CORTE
# =====================================================================

def ventanas_fachada(v, ventanas, y_fachada, z0):
    for x, y, w, o, s, h in ventanas:
        if o == 'h' and abs(y - y_fachada) < 1e-6:
            v.caja(x - w / 2, z0 + s, x + w / 2, z0 + s + h, relleno="#d9ecf7", borde="#333", ancho=0.3)
            v.poly([(x, z0 + s), (x, z0 + s + h)], color="#333", ancho=0.15)


def puertas_fachada(v, puertas, y_fachada, exteriores):
    """Sólo puertas sobre muros exteriores: (x0, x1) de los tramos de fachada a esa coordenada y."""
    for x, y, w, o, *_ in puertas:
        if o == 'h' and abs(y - y_fachada) < 1e-6 and any(a <= x <= b for a, b in exteriores):
            v.caja(x - w / 2, 0, x + w / 2, 2.05, relleno="#c9b79c", borde="#333", ancho=0.3)


def chimenea(v):
    v.caja(0.88, E.TECHO_BAJO["z_alto"] - 0.2, 1.12, 8.0, relleno="#777", borde="#333", ancho=0.2)


def elevacion(L, ox, oy, lado):
    """lado 'norte' (mira al sur, este a la izquierda) o 'sur' (mira al norte)."""
    espejo = lado == "norte"
    v = Vista(L, ox, oy, 10, espejo=espejo)
    # en espejo P() usa -u: desplazar para que x=12,4 quede a la izquierda
    if espejo:
        v.ox = ox + 12.4 * 10
    else:
        v.ox = ox + 0.6 * 10
    yf = 6 if lado == "norte" else 0
    v.caja(-1.0, -0.6, 13.0, -0.3, relleno=C_TIERRA)
    v.poly([(-1.0, -0.3), (13.0, -0.3)], color="#000", ancho=0.4)
    y_t = 6.0 if lado == "norte" else 0.0
    nat = [(x / 2, E.cota_terreno(x / 2, y_t + (2 if lado == "norte" else -2)) - E.NPT_MSNM) for x in range(-6, 29)]
    v.poly(nat, color="#7a6040", ancho=0.35, dash="2 0.8")
    x_l, z_l = nat[-1] if not espejo else nat[0]
    v.txt(x_l, z_l + 0.25, "terreno natural", fs=1.3, color="#7a6040")
    # muros
    v.caja(0 if lado == "norte" else 2, -0.3, 12, D.H1 + D.LOSA, relleno="#f3f0ea", borde="#000", ancho=0.4)
    if lado == "sur":
        v.caja(0, -0.3, 2, D.H1 + D.LOSA, relleno="#ebe6dc", borde="#000", ancho=0.3)      # muro living tras terraza
        v.caja(10.5, -0.3, 12, D.H1, relleno="#ebe6dc", borde="#000", ancho=0.3)          # muro acceso retranqueado
        v.caja(11.9, -0.3, 12.1, D.H1, relleno="#555")                                   # pilar
    v.caja(2, D.Z2, 12, D.Z2 + D.H2, relleno="#f3f0ea", borde="#000", ancho=0.4)
    v.poly([(2 if lado == "sur" else 0, D.H1), (12, D.H1)], color="#999", ancho=0.2)
    # techo bajo (perfil)
    tb = E.TECHO_BAJO
    v.caja(tb["x"][0], tb["z_bajo"], tb["x"][1], tb["z_alto"] + 0.15, relleno="none", borde="none")
    v.poly([(tb["x"][0], tb["z_bajo"]), (tb["x"][1], tb["z_alto"]), (tb["x"][1], tb["z_alto"] + 0.18),
            (tb["x"][0], tb["z_bajo"] + 0.18), (tb["x"][0], tb["z_bajo"])], color="#000", ancho=0.3, cerrar=True, relleno="#bbb")
    # faldón visible
    v.caja(E.TECHO_X[0], E.Z_BORDE_ALERO, E.TECHO_X[1], E.Z_CUMBRERA, relleno=C_TECHO, borde="#000", ancho=0.4)
    for k in range(1, 28):
        x = E.TECHO_X[0] + k * (E.TECHO_X[1] - E.TECHO_X[0]) / 28
        v.poly([(x, E.Z_BORDE_ALERO), (x, E.Z_CUMBRERA)], color="#d2c9b8", ancho=0.12)
    v.poly([(E.TECHO_X[0], E.Z_BORDE_ALERO), (E.TECHO_X[1], E.Z_BORDE_ALERO)], color=C_LLUVIA, ancho=0.8)
    if lado == "norte":
        sn = math.sin(math.radians(E.PENDIENTE))
        for x0, x1, s0, s1, et in E.PANELES:
            v.caja(x0, E.Z_CUMBRERA - s1 * sn, x1, E.Z_CUMBRERA - s0 * sn,
                   relleno=C_FV if et == 1 else "#fff", borde="#fff", ancho=0.4)
    ventanas_fachada(v, D.VENTANAS_1, yf, 0)
    ventanas_fachada(v, D.VENTANAS_2, yf, D.Z2)
    if lado == "sur":
        puertas_fachada(v, D.PUERTAS_1, 2, [(0, 2), (10.5, 12)])
        for b in E.BAJADAS:
            if b[1] < 0:
                v.poly([(b[0], E.Z_BORDE_ALERO), (b[0], -0.3)], color=C_LLUVIA, ancho=0.6)
    else:
        for b in E.BAJADAS:
            if b[1] > 6:
                v.poly([(b[0], E.Z_BORDE_ALERO), (b[0], -0.3)], color=C_LLUVIA, ancho=0.6)
    chimenea(v)
    # niveles
    for z, et in ((0, f"NPT ±0,00 = {num(E.NPT_MSNM)} msnm"), (-0.3, "plataforma −0,30"), (D.Z2, f"NPT +{num(D.Z2)}"), (E.Z_CUMBRERA, f"+{num(E.Z_CUMBRERA)}"),
                  (8.0, "+8,00 cañón")):
        x, y = v.P(13.0 if not espejo else -1.0, z)
        L.linea([(x, y), (x + 4, y)], ancho=0.2)
        L.add(f'<polygon points="{x+4},{y} {x+5.2},{y-1.2} {x+2.8},{y-1.2}" fill="#000"/>')
        L.txt(x + 6, y + 0.6, et, fs=1.5, anchor="start")
    titulo = "ELEVACIÓN NORTE (paneles y vanos principales)" if lado == "norte" else "ELEVACIÓN SUR (acceso y servicios)"
    L.txt(ox + 70, oy - 82, titulo, fs=3.0, peso="bold")
    L.txt(ox + (6 if espejo else 128), oy + 9, "E" if espejo else "E", fs=2, peso="bold", color=TINTA2)
    L.txt(ox + (128 if espejo else 6), oy + 9, "O", fs=2, peso="bold", color=TINTA2)


def corte(L, ox, oy, x_corte=3.2):
    v = Vista(L, ox + 1.2 * 10, oy, 10)
    L.txt(ox + 55, oy - 82, f"CORTE A-A (x = {num(x_corte)} m, mirando al este)", fs=3.0, peso="bold")
    v.caja(-1.6, -1.0, 7.6, -0.3, relleno=C_TIERRA)
    v.poly([(-1.6, -0.3), (7.6, -0.3)], color="#000", ancho=0.4)
    # fundaciones y radier
    for y_m, t in ((0, D.EXT), (2, D.INT), (6, D.EXT)):
        v.caja(y_m - 0.2, -0.9, y_m + 0.2, -0.3, relleno="#9a9a9a", borde="#000", ancho=0.2)
        v.caja(y_m - t / 2, -0.3, y_m + t / 2, 0, relleno="#9a9a9a", borde="#000", ancho=0.2)
    v.caja(0.1, -0.15, 5.9, -0.1, relleno="#f2d24b", borde="none")   # aislación bajo radier
    v.caja(0.1, -0.1, 5.9, 0, relleno="#bdbdbd", borde="#000", ancho=0.2)
    # muros cortados P1 / P2
    for y_m, t, z0, h in ((0, D.EXT, 0, D.H1), (2, D.INT, 0, D.H1), (6, D.EXT, 0, D.H1),
                          (0, D.EXT, D.Z2, D.H2), (3, D.INT, D.Z2, D.H2), (6, D.EXT, D.Z2, D.H2)):
        v.caja(y_m - t / 2, z0, y_m + t / 2, z0 + h, relleno=C_MURO)
    # vanos cortados
    for (y_m, z0, s, h) in ((0, 0, 0.9, 1.3), (6, D.Z2, 0.9, 1.3)):
        v.caja(y_m - 0.1, z0 + s, y_m + 0.1, z0 + s + h, relleno="#fff", borde="#000", ancho=0.15)
        v.poly([(y_m, z0 + s), (y_m, z0 + s + h)], color=C_LLUVIA, ancho=0.2)
    # losa entrepiso y cielo con aislación
    v.caja(-0.1, D.H1, 6.1, D.Z2, relleno="#9a9a9a", borde="#000", ancho=0.2)
    v.caja(0.1, D.Z2 + D.H2, 5.9, D.Z2 + D.H2 + 0.2, relleno="#f2d24b", borde="#000", ancho=0.15)
    # cubierta
    sy0, sy1, zc = E.TECHO_Y[0], E.TECHO_Y[1], E.Z_CUMBRERA
    e = 0.22
    v.poly([(sy0, E.Z_BORDE_ALERO), (E.CUMBRERA_Y, zc), (sy1, E.Z_BORDE_ALERO), (sy1, E.Z_BORDE_ALERO + e),
            (E.CUMBRERA_Y, zc + e), (sy0, E.Z_BORDE_ALERO + e), (sy0, E.Z_BORDE_ALERO)],
           color="#000", ancho=0.3, cerrar=True, relleno="#c8b89a")
    sn, cs = math.sin(math.radians(E.PENDIENTE)), math.cos(math.radians(E.PENDIENTE))
    for _, _, s0, s1, et in E.PANELES[:: E.PANELES_POR_FILA]:
        a = (E.CUMBRERA_Y + s0 * cs, zc + e + 0.12 - s0 * sn)
        b = (E.CUMBRERA_Y + s1 * cs, zc + e + 0.12 - s1 * sn)
        v.poly([a, b], color=C_FV, ancho=1.0)
    for y_c in (sy0, sy1):
        px, py = v.P(y_c, E.Z_BORDE_ALERO + 0.05)
        L.circ(px, py, 1.0, relleno="#fff", borde=C_LLUVIA, ancho=0.4)
    # drenaje perimetral
    for y_d in (-0.75, 6.75):
        px, py = v.P(y_d, -0.85)
        L.rect(px - 2.5, py - 2.5, 5, 5, relleno="#d9d4c8", borde="#999", ancho=0.15)
        L.circ(px, py, 0.9, relleno="#fff", borde=C_LLUVIA, ancho=0.3)
    # recintos
    for y_t, z_t, t in ((1.0, 1.2, "OFICINA 1"), (4.0, 1.2, "LIVING"), (1.5, D.Z2 + 1.2, "CLOSET"),
                        (4.5, D.Z2 + 1.2, "DORMITORIO"), (3.0, D.Z2 + D.H2 + 0.8, "ENTRETECHO VENTILADO")):
        v.txt(y_t, z_t, t, fs=1.7, color=TINTA2)
    env = E.ENVOLVENTE["capas"]
    rot = [((3.0, zc + 0.1), (8.6, 8.4), env["techumbre"]),
           ((5.0, D.Z2 + D.H2 + 0.1), (8.6, 6.3), env["cielo"]),
           ((6.05, D.Z2 + 1.0), (8.6, 4.4), env["muro"]),
           ((5.0, D.H1 + 0.1), (8.6, 2.9), env["entrepiso"]),
           ((3.0, -0.12), (8.6, 0.9), env["piso"]),
           ((6.75, -0.85), (8.6, -0.6), "Drenaje perimetral Ø100 + grava + geotextil"),
           ((6.0, -0.6), (8.6, -1.3), "Fundación corrida H.A. + sobrecimiento +0,30")]
    for (ya, za), (yt, zt), t in rot:
        x, y = v.P(ya, za)
        tx, ty = v.P(yt, zt)
        rotulo(L, x, y, tx, ty, t, fs=1.45)
    # cota alero y altura
    for z, et in ((0, "±0,00"), (D.Z2, f"+{num(D.Z2)}"), (D.Z2 + D.H2, f"+{num(D.Z2 + D.H2)}"), (zc, f"+{num(zc)}")):
        x, y = v.P(-1.4, z)
        L.linea([(x, y), (x + 4, y)], ancho=0.2)
        L.txt(x - 0.5, y + 0.6, et, fs=1.4, anchor="end")
    x, y = v.P(sy0, E.Z_BORDE_ALERO - 0.4)
    L.txt(x, y + 2, "S", fs=2.2, peso="bold", color=TINTA2)
    x, y = v.P(sy1, E.Z_BORDE_ALERO - 0.4)
    L.txt(x, y + 2, "N", fs=2.2, peso="bold", color=TINTA2)


def lamina_elevaciones():
    L = Lamina()
    marco(L, "ELE-02", "ELEVACIONES Y CORTE — ENVOLVENTE TÉRMICA", 7)
    elevacion(L, 20, 108, "norte")
    elevacion(L, 205, 108, "sur")
    corte(L, 25, 232)
    zt = E.ENVOLVENTE
    filas = [("Elemento", "Solución propuesta", "U prop.", "U máx.")]
    for el, sol, u, umax in zt["tabla"]:
        filas.append((el, sol, num(u) if u else "—", umax))
    tabla(L, 218, 150, [22, 78, 13, 13], filas, fs=1.5, alto=4.6)
    L.txt(218, 147, f"ENVOLVENTE TÉRMICA — {zt['zona']}", fs=2.2, anchor="start", peso="bold")
    for i, t in enumerate(zt["notas"]):
        L.txt(218, 150 + 4.6 * len(filas) + 4 + i * 3.4, t, fs=1.5, anchor="start", color=TINTA2 if i else TINTA)
    return L
