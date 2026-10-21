#!/usr/bin/env python3
"""Genera las láminas A3 (SVG + PDF) de arquitectura, electricidad y gasfitería.

Uso:  python3 generar_laminas.py
Salida: carpeta laminas/
"""
import math
import os
import subprocess
from html import escape

import casa_datos as D
import instalaciones_datos as I

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "laminas")
S = 10.0  # 1:100 -> 1 m = 10 mm de papel
W, H = 420, 297  # A3 apaisado
FECHA = "20-10-2026"
OY = 118
OX1, OX2 = 26, 190

C_MURO = "#2b2b2b"
C_PISO = "#f7f5ef"
C_TERRAZA = "#d9bf8c"
C_AF, C_AC, C_ALC, C_HID = "#1f6fd1", "#d62728", "#7b4b2a", "#8e44ad"
C_CABLE = "#c0392b"
# un color por circuito para las canalizaciones (alimentación desde el tablero)
C_CIRC = {"C1": "#e6a100", "C2": "#b8860b", "C3": "#2e86c1", "C4": "#c0392b", "C5": "#17a589", "C6": "#7d3c98",
          "C7": "#1abc9c", "C8": "#5d6d7e", "C9": "#d35400", "C10": "#a04000", "C11": "#8e44ad", "C12": "#6c3483",
          "C13": "#2c3e50", "C14": "#ca6f1e", "C15": "#117a65"}
FUENTE = "Helvetica, Arial, sans-serif"


def num(v):
    return f"{v:.2f}".replace(".", ",")


class Lamina:
    def __init__(self):
        self.p = []

    def add(self, s):
        self.p.append(s)

    def txt(self, x, y, s, fs=2.5, anchor="middle", peso="normal", color="#222", rot=0):
        r = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ""
        lineas = str(s).split("\n")
        y0 = y - (len(lineas) - 1) * fs * 0.6
        for i, l in enumerate(lineas):
            self.add(f'<text x="{x:.2f}" y="{y0 + i * fs * 1.2:.2f}" font-size="{fs}" text-anchor="{anchor}" '
                     f'font-weight="{peso}" fill="{color}" font-family="{FUENTE}" xml:space="preserve"{r}>{escape(l)}</text>')

    def linea(self, pts, color="#000", ancho=0.3, dash=None, cerrar=False, relleno="none"):
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        tag = "polygon" if cerrar else "polyline"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<{tag} points="{d}" fill="{relleno}" stroke="{color}" stroke-width="{ancho}"{da} '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')

    def rect(self, x, y, w, h, relleno="none", borde="none", ancho=0.3):
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{relleno}" '
                 f'stroke="{borde}" stroke-width="{ancho}"/>')

    def circ(self, x, y, r, relleno="#fff", borde="#000", ancho=0.3):
        self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{relleno}" stroke="{borde}" stroke-width="{ancho}"/>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
                f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(self.p) + "</svg>")


class Planta:
    """Transforma coordenadas del mundo (m) a papel (mm) para una planta."""

    def __init__(self, lam, ox, oy=OY):
        self.L, self.ox, self.oy = lam, ox, oy

    def P(self, x, y):
        return self.ox + x * S, self.oy - y * S

    def poly(self, pts, **kw):
        self.L.linea([self.P(*p) for p in pts], **kw)

    def caja(self, x0, y0, x1, y1, **kw):
        a, b = self.P(min(x0, x1), max(y0, y1))
        self.L.rect(a, b, abs(x1 - x0) * S, abs(y1 - y0) * S, **kw)


# ---------------- dibujo de arquitectura base ----------------

def tramos_muro(m, aberturas):
    """Devuelve el muro como lista de rectángulos sólidos y los vanos que lo afectan."""
    x1, y1, x2, y2, t = m
    e = t / 2
    horiz = y1 == y2
    lo, hi = (min(x1, x2), max(x1, x2)) if horiz else (min(y1, y2), max(y1, y2))
    fijo = y1 if horiz else x1
    propios = []
    for ab in aberturas:
        x, y, w, o = ab[:4]
        if (o == 'h') == horiz and abs((y if horiz else x) - fijo) < 1e-6:
            c = x if horiz else y
            if lo - 1e-6 <= c <= hi + 1e-6:
                propios.append((c - w / 2, c + w / 2, ab))
    propios.sort()
    piezas, cur = [], lo - e
    for a, b, _ in propios:
        if a > cur:
            piezas.append((cur, a))
        cur = max(cur, b)
    if hi + e > cur:
        piezas.append((cur, hi + e))
    rects = []
    for a, b in piezas:
        rects.append((a, fijo - e, b, fijo + e) if horiz else (fijo - e, a, fijo + e, b))
    return rects, propios, horiz, fijo, e


def dibujar_arquitectura(pl, piso, tenue=False):
    muros = D.MUROS_1 if piso == 1 else D.MUROS_2
    puertas = D.PUERTAS_1 if piso == 1 else D.PUERTAS_2
    ventanas = D.VENTANAS_1 if piso == 1 else D.VENTANAS_2
    recintos = D.RECINTOS_1 if piso == 1 else D.RECINTOS_2
    c_muro = "#8a8a8a" if tenue else C_MURO
    for nombre, x0, y0, x1, y1 in recintos:
        pl.caja(x0, y0, x1, y1, relleno=C_TERRAZA if nombre in D.EXTERIORES else C_PISO)
    if piso == 1:
        for cx, cy, t in D.COLUMNAS_1:
            pl.caja(cx - t / 2, cy - t / 2, cx + t / 2, cy + t / 2, relleno=c_muro)
    if piso == 1:  # sombra del piso 2 sobre la terraza de entrada (alero)
        pl.caja(*D.TERRAZAS[-1], relleno="none", borde="#777", ancho=0.15)
    dibujar_escalera(pl, piso)
    for m in muros:
        rects, propios, horiz, fijo, e = tramos_muro(m, list(puertas) + list(ventanas))
        for r in rects:
            pl.caja(*r, relleno=c_muro)
        for a, b, ab in propios:
            if len(ab) == 6:  # ventana
                r = (a, fijo - e, b, fijo + e) if horiz else (fijo - e, a, fijo + e, b)
                pl.caja(*r, relleno="#fff", borde=c_muro, ancho=0.2)
                for k in (-0.25, 0.25):
                    if horiz:
                        pl.poly([(a, fijo + k * e), (b, fijo + k * e)], color=c_muro, ancho=0.12)
                    else:
                        pl.poly([(fijo + k * e, a), (fijo + k * e, b)], color=c_muro, ancho=0.12)
            else:
                dibujar_puerta(pl, a, b, ab, horiz, fijo, e, c_muro)


def dibujar_puerta(pl, a, b, ab, horiz, fijo, e, color):
    s = ab[4]
    if s == 0:
        return
    w = b - a
    hojas = [(a, 1, w / 2), (b, -1, w / 2)] if w >= 1.4 else [(a, 1, w)]
    for bis, dirr, r in hojas:
        base = fijo + s * e
        pts = []
        for i in range(17):
            ang = math.pi / 2 * i / 16
            u = bis + dirr * r * math.sin(ang)
            v = base + s * r * math.cos(ang)
            pts.append((u, v) if horiz else (v, u))
        pl.poly(pts, color=color, ancho=0.12, dash="0.8 0.5")
        hoja = [(bis, base), (bis, base + s * r)]
        pl.poly([(p if horiz else (p[1], p[0])) for p in hoja], color=color, ancho=0.35)


def dibujar_escalera(pl, piso):
    """Helicoidal: peldaños, pilar, línea de huella con flecha y, en el P2, el descanso de llegada."""
    col = "#666"
    for pts, _ in D.ESCALONES:
        pl.poly(pts, color=col, ancho=0.15, cerrar=True)
    if piso == 2:
        pl.poly(D.DESCANSO_P2, color=col, ancho=0.15, cerrar=True, relleno="#eee")
    cx, cy = pl.P(*D.ESC_CENTRO)
    pl.L.circ(cx, cy, D.ESC_NUCLEO * S, relleno="#444", borde="#444")
    pl.poly(D.FLECHA_ESCALERA, color=col, ancho=0.2)
    (xa, ya), (xb, yb) = (pl.P(*p) for p in D.FLECHA_ESCALERA[-2:])
    ang = math.atan2(yb - ya, xb - xa)
    ala = [(xb - 1.6 * math.cos(ang + s), yb - 1.6 * math.sin(ang + s)) for s in (0.5, -0.5)]
    pl.L.linea([ala[0], (xb, yb), ala[1]], color=col, ancho=0.2)
    tx, ty = pl.P(*D.FLECHA_ESCALERA[0])
    pl.L.txt(tx + 2.2, ty + 0.5, "SUBE" if piso == 1 else "BAJA", fs=1.5, color=col, anchor="start")


def etiquetas_recintos(pl, piso, con_area=True):
    """Sin área (láminas de instalaciones): etiqueta pequeña junto al borde superior del recinto."""
    recintos = D.RECINTOS_1 if piso == 1 else D.RECINTOS_2
    for nombre, x0, y0, x1, y1 in recintos:
        if nombre in ("ESCALERA", ""):
            continue
        cx, cy = pl.P((x0 + x1) / 2, (y0 + y1) / 2)
        if nombre == "LIVING / COCINA":
            cx, cy = pl.P(*D.ETIQUETA_LIVING)
        elif not con_area:
            cx, cy = pl.P((x0 + x1) / 2, y0 + 0.40 if nombre in D.EXTERIORES else y1 - 0.40)
        ancho = (x1 - x0) * S
        vertical = ancho < 15 and con_area
        disp = (y1 - y0) * S if vertical else ancho
        fs = min(2.4 if con_area else 1.7, 0.9 * disp / (0.62 * max(len(l) for l in nombre.split(" "))))
        nom = nombre.replace(" ", "\n") if (len(nombre) * fs * 0.62 > disp * 0.9) else nombre
        rot = -90 if vertical else 0
        pl.L.txt(cx, cy, nom, fs=fs, peso="bold", color="#333", rot=rot)
        if con_area:
            area = (x1 - x0) * (y1 - y0)
            dy = fs * (0.6 * nom.count("\n") + 1.6)
            if vertical:
                pl.L.txt(cx + dy, cy, f"{num(area)} m²", fs=1.7, color="#555", rot=rot)
            else:
                pl.L.txt(cx, cy + dy, f"{num(area)} m²", fs=1.7, color="#555")


def cota(pl, valores, fijo, eje, off):
    """Cadena de cotas. eje 'x': valores en x, a la altura y=fijo desplazada off mm (papel)."""
    L = pl.L
    for i, v in enumerate(valores):
        px, py = pl.P(v, fijo) if eje == "x" else pl.P(fijo, v)
        if eje == "x":
            L.linea([(px, py - off * 0.15), (px, py - off)], color="#555", ancho=0.1)
            L.linea([(px - 0.8, py - off + 0.8), (px + 0.8, py - off - 0.8)], color="#000", ancho=0.3)
        else:
            L.linea([(px + off * 0.15, py), (px + off, py)], color="#555", ancho=0.1)
            L.linea([(px + off - 0.8, py + 0.8), (px + off + 0.8, py - 0.8)], color="#000", ancho=0.3)
    a, b = valores[0], valores[-1]
    if eje == "x":
        p0, p1 = pl.P(a, fijo), pl.P(b, fijo)
        L.linea([(p0[0], p0[1] - off), (p1[0], p1[1] - off)], color="#000", ancho=0.15)
    else:
        p0, p1 = pl.P(fijo, a), pl.P(fijo, b)
        L.linea([(p0[0] + off, p0[1]), (p1[0] + off, p1[1])], color="#000", ancho=0.15)
    for v0, v1 in zip(valores, valores[1:]):
        m = (v0 + v1) / 2
        if eje == "x":
            px, py = pl.P(m, fijo)
            L.txt(px, py - off - (0.7 if off > 0 else -2.4), num(v1 - v0), fs=1.8)
        else:
            px, py = pl.P(fijo, m)
            L.txt(px + off - (0.7 if off > 0 else -2.4), py, num(v1 - v0), fs=1.8, rot=-90)


# ---------------- marco, rótulo y tablas ----------------

TOTAL_LAMINAS = 14


def marco(L, codigo, titulo, n, escala="1:100 (imprimir en A3)"):
    L.codigo, L.titulo = codigo, titulo
    L.rect(10, 10, W - 20, H - 20, borde="#000", ancho=0.5)
    x0, y0 = 290, 245
    L.rect(x0, y0, W - 10 - x0, H - 10 - y0, relleno="#fff", borde="#000", ancho=0.4)
    filas = [("PROYECTO", "VIVIENDA 2 PISOS — ANTEPROYECTO"), ("LÁMINA", titulo),
             ("ESCALA", escala), ("FECHA", FECHA), ("CÓDIGO", f"{codigo}   ·   {n} de {TOTAL_LAMINAS}")]
    for i, (k, v) in enumerate(filas):
        y = y0 + 7 + i * 8.2
        L.txt(x0 + 3, y, k, fs=1.8, anchor="start", color="#666")
        L.txt(x0 + 24, y, v, fs=2.6 if i == 1 else 2.2, anchor="start", peso="bold" if i == 1 else "normal")
        if i:
            L.linea([(x0, y - 4.6), (W - 10, y - 4.6)], color="#999", ancho=0.15)
    L.txt(355, 240, "Medidas aproximadas — verificar en terreno. +Y = norte geográfico.", fs=1.8, color="#a33")


def titulos_plantas(L):
    for ox, recs, t in ((OX1, D.RECINTOS_1, "PLANTA PRIMER PISO"), (OX2, D.RECINTOS_2, "PLANTA SEGUNDO PISO")):
        cx = ox + S * (min(r[1] for r in recs) + max(r[3] for r in recs)) / 2
        L.txt(cx, 22, t, fs=4, peso="bold")
        L.linea([(cx - 32, 23.5), (cx + 32, 23.5)], ancho=0.3)


def tabla(L, x, y, anchos, filas, fs=2.0, alto=5.2):
    tot = sum(anchos)
    for i, fila in enumerate(filas):
        yy = y + i * alto
        if i == 0:
            L.rect(x, yy, tot, alto, relleno="#eee")
        cx = x
        for w, c in zip(anchos, fila):
            L.txt(cx + 1.5, yy + alto * 0.7, c, fs=fs, anchor="start", peso="bold" if i == 0 else "normal")
            cx += w
        L.linea([(x, yy + alto), (x + tot, yy + alto)], color="#999", ancho=0.15)
    L.rect(x, y, tot, alto * len(filas), borde="#000", ancho=0.3)


def notas(L, x, y, titulo, lineas, fs=2.0, ancho_max=None):
    L.txt(x, y, titulo, fs=2.6, anchor="start", peso="bold")
    for i, l in enumerate(lineas):
        L.txt(x, y + 5 + i * fs * 1.55, l, fs=fs, anchor="start")


# ---------------- símbolos eléctricos ----------------

def sim_luz(L, x, y, tipo):
    if tipo == "muro":
        L.circ(x, y, 1.6)
        L.add(f'<path d="M{x-1.6:.2f},{y:.2f} A1.6,1.6 0 0 0 {x+1.6:.2f},{y:.2f} Z" fill="#000"/>')
    else:
        L.circ(x, y, 1.8)
        k = 1.27
        L.linea([(x - k, y - k), (x + k, y + k)], ancho=0.3)
        L.linea([(x - k, y + k), (x + k, y - k)], ancho=0.3)


def sim_enchufe(L, x, y, ip):
    L.circ(x, y, 1.3, relleno="#fff", ancho=0.25)
    for dx in (-0.45, 0.45):
        L.linea([(x + dx, y - 0.7), (x + dx, y + 0.7)], ancho=0.3)
    if ip:
        L.txt(x + 2.6, y - 1.0, "IP", fs=1.3, color="#05a")


def sim_interruptor(L, x, y, tipo):
    L.circ(x, y, 0.7, relleno="#000", ancho=0.1)
    angs = {"simple": [45], "doble": [35, 65], "conmutador": [45, 225]}[tipo]
    for a in angs:
        r = math.radians(a)
        ex, ey = x + 3 * math.cos(r), y - 3 * math.sin(r)
        L.linea([(x, y), (ex, ey)], ancho=0.3)
        px, py = -math.sin(r) * 0.8, -math.cos(r) * 0.8
        L.linea([(ex, ey), (ex + px, ey + py)], ancho=0.3)


def sim_tablero(L, x, y, txt):
    L.rect(x - 3, y - 1.2, 6, 2.4, relleno="#fff", borde="#000", ancho=0.3)
    L.add(f'<polygon points="{x-3:.2f},{y+1.2:.2f} {x+3:.2f},{y-1.2:.2f} {x+3:.2f},{y+1.2:.2f}" fill="#000"/>')
    L.txt(x, y - 2.2, txt, fs=1.6, peso="bold")


def sim_medidor(L, x, y, txt):
    L.rect(x - 2, y - 2, 4, 4, relleno="#fff", borde="#000", ancho=0.3)
    L.txt(x, y + 0.6, txt, fs=1.2, peso="bold")


def sim_detector(L, x, y, tipo):
    L.circ(x, y, 1.5, relleno="#fff" if tipo == "humo" else "#fde2d2", borde="#c0392b", ancho=0.3)
    L.txt(x, y + 0.55, "DH" if tipo == "humo" else "DT", fs=1.1, peso="bold", color="#c0392b")


def sim_conexion(L, x, y, sigla):
    L.rect(x - 1.5, y - 1.5, 3, 3, relleno="#fff", borde="#05a", ancho=0.3)
    L.linea([(x - 1.5, y - 1.5), (x + 1.5, y + 1.5)], color="#05a", ancho=0.2)
    L.txt(x + 2, y - 1.8, sigla, fs=1.2, anchor="start", color="#05a", peso="bold")


def puntos_circuito(piso):
    """{circuito: [(x, y), ...]} de todo lo que alimenta cada circuito en un piso."""
    luces = I.LUCES_1 if piso == 1 else I.LUCES_2
    ench = I.ENCHUFES_1 if piso == 1 else I.ENCHUFES_2
    pts = {}
    for x, y, c, _ in luces:
        pts.setdefault(c, []).append((x, y))
    for x, y, c, _ in ench:
        pts.setdefault(c, []).append((x, y))
    for p_, x, y, c, _ in I.CONEXIONES_FIJAS:
        if p_ == piso:
            pts.setdefault(c, []).append((x, y))
    for p_, x, y, _ in I.DETECTORES:
        if p_ == piso:
            pts.setdefault("C2", []).append((x, y))
    return pts


def origen_circuito(c, piso):
    if piso == 2:
        return I.MONTANTE_ELEC
    return (I.TABLERO_R if c in I.RESPALDO else I.TABLERO)[:2]


def canalizaciones(piso):
    """Árbol de canalización por circuito (Prim con distancia Manhattan) desde su tablero o la montante del P2.
    Devuelve [(circuito, [(x, y), (x, y), (x, y)])]: cada tramo es una L (primero horizontal, luego vertical)."""
    tramos = []
    for c, pts in puntos_circuito(piso).items():
        hechos = [origen_circuito(c, piso)]
        resto = list(dict.fromkeys(pts))
        while resto:
            a, b = min(((a, b) for a in hechos for b in resto),
                       key=lambda ab: abs(ab[0][0] - ab[1][0]) + abs(ab[0][1] - ab[1][1]))
            tramos.append((c, [a, (b[0], a[1]), b]))
            hechos.append(b)
            resto.remove(b)
    return tramos


def dibujar_electrico(pl, piso):
    L = pl.L
    luces = I.LUCES_1 if piso == 1 else I.LUCES_2
    inter = I.INTERRUPTORES_1 if piso == 1 else I.INTERRUPTORES_2
    ench = I.ENCHUFES_1 if piso == 1 else I.ENCHUFES_2
    for c, pts in canalizaciones(piso):  # alimentación desde el tablero (bajo los símbolos)
        pl.poly(pts, color=C_CIRC.get(c, "#555"), ancho=0.22)
    for x, y, tipo, idx in inter:  # cableado interruptor -> luminaria
        sx, sy = pl.P(x, y)
        for i in idx:
            lx, ly = pl.P(*luces[i][:2])
            mx, my = (sx + lx) / 2, (sy + ly) / 2
            dx, dy = lx - sx, ly - sy
            n = math.hypot(dx, dy) or 1
            cx, cy = mx - dy / n * n * 0.15, my + dx / n * n * 0.15
            L.add(f'<path d="M{sx:.2f},{sy:.2f} Q{cx:.2f},{cy:.2f} {lx:.2f},{ly:.2f}" fill="none" '
                  f'stroke="{C_CABLE}" stroke-width="0.2" stroke-dasharray="1 0.6"/>')
    for x, y, c, tipo in luces:
        px, py = pl.P(x, y)
        sim_luz(L, px, py, tipo)
        L.txt(px + 2.9, py - 1.8, c, fs=1.4, color="#05a", anchor="start")
    for x, y, tipo, _ in inter:
        sim_interruptor(L, *pl.P(x, y), tipo)
    for x, y, c, ip in ench:
        px, py = pl.P(x, y)
        sim_enchufe(L, px, py, ip)
        L.txt(px, py + 3.2, c, fs=1.2, color="#05a")
    for p_, x, y, c, sigla in I.CONEXIONES_FIJAS:
        if p_ == piso:
            sim_conexion(L, *pl.P(x, y), f"{sigla} {c}")
    for p_, x, y, tipo in I.DETECTORES:
        if p_ == piso:
            sim_detector(L, *pl.P(x, y), tipo)
    if piso == 1:
        tx, ty = pl.P(*I.TABLERO[:2])
        mx, my = pl.P(*I.MEDIDOR_ELEC[:2])
        pl.poly(I.ACOMETIDA, color="#000", ancho=0.4)
        sim_tablero(L, tx, ty, I.TABLERO[2])
        rx, ry = pl.P(*I.TABLERO_R[:2])
        sim_tablero(L, rx, ry, I.TABLERO_R[2])
        pl.poly([(8.40, 2.45), (I.TABLERO_R[0], 2.45), I.TABLERO_R[:2]], color="#1f4e9c", ancho=0.35, dash="1.5 0.6")
        sube = sorted({c for c in puntos_circuito(2)}, key=lambda c: int(c[1:]))
        L.txt(tx - 1, ty + 5.2, "↑ P2: " + ", ".join(sube), fs=1.2, anchor="end", color="#05a")
        sim_medidor(L, mx, my, "kWh")
        L.txt(mx + 2.8, my + 4.2, "EMPALME", fs=1.3, anchor="start")
        import especialidades_datos as E
        ix, iy = pl.P(*E.INVERSOR[:2])
        bx, by = pl.P(E.BATERIA["x"], E.BATERIA["y"])
        L.rect(ix - 2.6, iy - 1.6, 5.2, 3.2, relleno="#eef3fb", borde="#1f4e9c", ancho=0.35)
        L.txt(ix, iy + 0.6, "INV", fs=1.3, peso="bold", color="#1f4e9c")
        L.rect(bx - 2.6, by - 1.6, 5.2, 3.2, relleno="#1f4e9c", borde="#1f4e9c", ancho=0.35)
        L.txt(bx, by + 0.6, "BAT", fs=1.3, peso="bold", color="#fff")
        pl.poly([E.INVERSOR[:2], (8.40, 1.80), (8.40, 2.55), (I.TABLERO[0], 2.55), I.TABLERO[:2]], color="#1f4e9c",
                ancho=0.35, dash="1.5 0.6")
        tx2, ty2 = pl.P(*I.TABLERO[:2])
        flecha_e = (tx2 + 2.5, ty2 - 3.5)
        L.txt(flecha_e[0] + 1, flecha_e[1], "C8 → caseta presurizadora / pozo", fs=1.3, anchor="start", color="#05a")
        ex, ey = pl.P(*I.SALIDA_EV)
        L.linea([(ex, ey), (ex + 9, ey)], color="#05a", ancho=0.35, dash="1.5 0.6")
        L.txt(ex + 9.5, ey + 0.5, "EV → cargador 11 kW (estac.)", fs=1.2, anchor="start", color="#05a")
    else:
        mx, my = pl.P(*I.MONTANTE_ELEC)
        L.rect(mx - 1.2, my - 1.2, 2.4, 2.4, relleno="#05a", borde="#05a", ancho=0.2)
        L.txt(mx - 1.8, my + 4.2, "Montante desde TDA / TDA-R", fs=1.2, anchor="end", color="#05a")


# ---------------- símbolos de gasfitería ----------------

def dibujar_artefacto(pl, cod, x, y, w, h):
    L = pl.L
    x0, y0 = pl.P(x - w / 2, y + h / 2)
    ww, hh = w * S, h * S
    cx, cy = pl.P(x, y)
    k = dict(borde="#333", ancho=0.25)
    if cod == "WC":
        L.rect(x0, y0 + hh * 0.7, ww, hh * 0.3, relleno="#fff", **k)
        L.add(f'<ellipse cx="{cx:.2f}" cy="{y0 + hh*0.38:.2f}" rx="{ww*0.42:.2f}" ry="{hh*0.36:.2f}" fill="#fff" stroke="#333" stroke-width="0.25"/>')
    elif cod == "LV":
        L.rect(x0, y0, ww, hh, relleno="#fff", **k)
        L.add(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{ww*0.36:.2f}" ry="{hh*0.32:.2f}" fill="none" stroke="#333" stroke-width="0.2"/>')
    elif cod == "DU":
        L.rect(x0, y0, ww, hh, relleno="#fff", **k)
        L.linea([(x0, y0), (x0 + ww, y0 + hh)], color="#999", ancho=0.12)
        L.linea([(x0 + ww, y0), (x0, y0 + hh)], color="#999", ancho=0.12)
        L.circ(cx, cy, 0.6, ancho=0.2)
    elif cod in ("LP", "LD"):
        L.rect(x0, y0, ww, hh, relleno="#fff", **k)
        if cod == "LP":
            L.rect(x0 + 0.6, y0 + 0.6, ww / 2 - 0.9, hh - 1.2, **k)
            L.rect(x0 + ww / 2 + 0.3, y0 + 0.6, ww / 2 - 0.9, hh - 1.2, **k)
        else:
            L.rect(x0 + 0.7, y0 + 0.7, ww - 1.4, hh - 1.4, **k)
    elif cod == "LAV":
        L.rect(x0, y0, ww, hh, relleno="#fff", **k)
        L.circ(cx, cy, ww * 0.33, ancho=0.2)
    elif cod == "ACS":
        L.circ(cx, cy, ww / 2, relleno="#fde2e2", borde="#333", ancho=0.25)
    elif cod == "IND":
        L.rect(x0, y0, ww, hh, relleno="#2b2b2b", **k)
        for dx in (-0.25, 0.25):
            for dy in (-0.25, 0.25):
                L.circ(cx + dx * ww, cy + dy * hh, ww * 0.15, relleno="none", borde="#ddd", ancho=0.2)
    L.txt(cx, cy + 0.6, cod, fs=1.3, peso="bold", color="#fff" if cod == "IND" else "#333")


def dibujar_gasfiteria(pl, piso):
    L = pl.L
    if piso == 1:
        redes = [(I.ALC_1, C_ALC, 0.7, None), (I.HIDRAULICO_1, C_HID, 0.55, "3 1 0.6 1"),
                 (I.AF_1, C_AF, 0.45, None), (I.AC_1, C_AC, 0.45, "1.6 0.8")]
        arts = I.ARTEFACTOS_1
    else:
        redes = [(I.ALC_2, C_ALC, 0.7, None), (I.AF_2, C_AF, 0.45, None), (I.AC_2, C_AC, 0.45, "1.6 0.8")]
        arts = I.ARTEFACTOS_2
    for a in arts:
        dibujar_artefacto(pl, *a)
    if piso == 1:  # tramos de agua que cruzan por el entrepiso (banda gris debajo) — nunca por el radier
        for pts in I.AF_1_ENTREPISO + I.AC_1_ENTREPISO:
            pl.poly(pts, color="#d5d5d5", ancho=1.6)
        redes += [(I.AF_1_ENTREPISO, C_AF, 0.45, None), (I.AC_1_ENTREPISO, C_AC, 0.45, "1.6 0.8")]
    for lineas, color, ancho, dash in redes:
        for pts in lineas:
            pl.poly(pts, color=color, ancho=ancho, dash=dash)
    for x, y, t in I.SUBIDAS:
        px, py = pl.P(x, y)
        L.circ(px, py, 0.8, relleno=C_AF if t == "AF" else C_AC, borde="#000", ancho=0.15)
    px, py = pl.P(*I.BAJADA[:2])
    L.circ(px, py, 1.1, relleno=C_ALC, borde="#000", ancho=0.15)
    L.txt(px - 2, py + 5.5 if piso == 1 else py - 6, "B.A.S.", fs=1.4, color=C_ALC, anchor="end", peso="bold")
    sx, sy = pl.P(*I.SUBIDAS[-1][:2])
    L.txt(sx - 2, sy - 2.8 if piso == 1 else sy + 4.5, "AF/AC ↑ P2" if piso == 1 else "AF/AC desde P1",
          fs=1.3, anchor="end", color="#05a")
    if piso == 1:
        for x, y, n in I.CAMARAS:
            px, py = pl.P(x, y)
            L.rect(px - 1.6, py - 1.6, 3.2, 3.2, relleno="#fff", borde=C_ALC, ancho=0.4)
            if n == "C.D.":  # cámara desgrasadora: doble cuadro
                L.rect(px - 0.9, py - 0.9, 1.8, 1.8, relleno=C_ALC, borde="none")
            L.txt(px, py + 4.2 if y < 0 else py - 2.4, n, fs=1.4, color=C_ALC, peso="bold")
        ux, uy = pl.P(*I.UNION_DOMICILIARIA)
        L.circ(ux, uy, 1.3, relleno=C_ALC, borde="#000", ancho=0.2)
        L.txt(ux + (-2.5 if ux > 100 else 2.5), uy + 0.6, I.SALIDA_TEXTO, fs=1.4, anchor="end" if ux > 100 else "start",
              color=C_ALC, peso="bold")
        for x, y, d in I.PASADAS:
            px, py = pl.P(x, y)
            L.circ(px, py, 0.75, relleno="#fff", borde="#000", ancho=0.25)
            L.linea([(px - 0.75, py), (px + 0.75, py)], ancho=0.2)
        lx, ly = pl.P(7.95, 2.70)
        L.txt(lx + 1.2, ly + 0.5, "por entrepiso", fs=1.2, anchor="start", color="#777")
        mx, my = pl.P(*I.MEDIDOR_AGUA)
        sim_medidor(L, mx, my, I.SIGLA_AGUA)
        L.txt(mx, my + 4, I.TEXTO_AGUA, fs=1.2, color=C_AF)
        vx, vy = pl.P(*I.VALVULA_TERMOSTATICA)
        L.add(f'<polygon points="{vx-1.4},{vy-1} {vx+1.4},{vy+1} {vx+1.4},{vy-1} {vx-1.4},{vy+1}" fill="{C_AC}" stroke="#000" stroke-width="0.15"/>')
        L.txt(vx + 2, vy + 0.5, "VMT 45 °C", fs=1.2, anchor="start", color=C_AC, peso="bold")
        bx, by = pl.P(6.95, -0.55)
        L.rect(bx - 5, by - 2, 10, 4, relleno="#efe3f6", borde=C_HID, ancho=0.4)
        L.txt(bx, by + 0.6, "BC", fs=1.4, peso="bold", color=C_HID)
        for p_ in (1,):
            cx_, cy_ = pl.P(8.45, 2.12)
            L.rect(cx_ - 2, cy_ - 1, 4, 2, relleno="#efe3f6", borde=C_HID, ancho=0.35)
        lx, ly = pl.P(*I.ROTULO_HIDRAULICO)
        L.txt(lx, ly, "Calefacción PE-RT Ø25 → colector", fs=1.2, color=C_HID)
        lx, ly = pl.P(*I.ROTULO_COLECTOR)
        L.txt(lx + 2.2, ly, "PVC Ø110 · pend. ≥ 3 %", fs=1.4, color=C_ALC, rot=-90)
        lx, ly = pl.P(*I.ROTULO_COCINA)
        L.txt(lx, ly - 1.2, "PVC Ø50 → Ø110", fs=1.4, color=C_ALC)


def leyenda(L, x, y, items, titulo="SIMBOLOGÍA"):
    L.txt(x, y, titulo, fs=2.8, anchor="start", peso="bold")
    for i, (dib, texto) in enumerate(items):
        yy = y + 7 + i * 6.2
        dib(L, x + 4, yy)
        L.txt(x + 10, yy + 0.8, texto, fs=1.9, anchor="start")


def leyenda_linea(color, ancho, dash=None):
    return lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=color, ancho=ancho, dash=dash)


# ---------------- láminas ----------------

def base_plantas(L, cotas=False, tenue=False, areas=True):
    titulos_plantas(L)
    pls = []
    for piso, ox in ((1, OX1), (2, OX2)):
        pl = Planta(L, ox)
        dibujar_arquitectura(pl, piso, tenue=tenue)
        etiquetas_recintos(pl, piso, con_area=areas)
        pls.append(pl)
    return pls


def lamina_arquitectura(img_iso=None):
    L = Lamina()
    p1, p2 = base_plantas(L, cotas=True)
    for c in D.COTAS_1:
        cota(p1, *c)
    for c in D.COTAS_2:
        cota(p2, *c)
    marco(L, "ARQ-01", "PLANTAS DE ARQUITECTURA", 1)

    def sup(recs):
        return sum((x1 - x0) * (y1 - y0) for n, x0, y0, x1, y1 in recs if n not in D.EXTERIORES)
    s1, s2 = sup(D.RECINTOS_1), sup(D.RECINTOS_2)
    s_ter = sum((x1 - x0) * (y1 - y0) for n, x0, y0, x1, y1 in D.RECINTOS_1 if n in D.EXTERIORES)
    tabla(L, 18, 160, [52, 24], [
        ("CUADRO DE SUPERFICIES", "m²"),
        ("Primer piso", num(s1)), ("Segundo piso", num(s2)),
        ("Total edificado", num(s1 + s2)), ("Terrazas (no edificadas)", num(s_ter)),
        ("Superficies medidas a eje de muros", ""),
    ])
    notas(L, 18, 200, "NOTAS", [
        "1. Medidas en metros, a eje de muro. Escala 1:100 en A3.",
        f"2. Muros exteriores 20 cm, tabiques 10 cm. Piso-cielo P1 {num(D.H1)} m, P2 {num(D.H2)} m (≥ 2,30, OGUC 4.1.1).",
        f"3. Entrepiso acústico de madera {int(round(D.LOSA * 100))} cm (piso flotante + cielo desacoplado,",
        f"   detalle en ELE-02). Nivel piso 2 = +{num(D.Z2)} m. El P2 no lleva piso radiante.",
        "4. Escalera helicoidal Ø 1,80 m (ESC-01): 15 contrahuellas de",
        "   18 cm, huella 25 cm en la línea de huella. Se entra de frente",
        "   desde el pasillo; llega al hall del P2. Barrotes < 10 cm y puertas",
        "   de seguridad arriba y abajo (bebé, gatos). Libera la sala técnica.",
        "6. Ventanas P2 con antepecho 1,00 m y limitador de apertura 10 cm.",
        "7. Superficie ≤ 140 m² y 2 pisos → F-15 (OGUC 4.3.5 n°14), DS1 ok.",
        "8. Mesones 0,85 m y muebles altos a 1,40 m (estatura 1,64 m).",
        "9. Medidas en casa_datos.py; regenerar: python3 generar_laminas.py",
    ])
    if img_iso and os.path.exists(img_iso):
        L.txt(200, 160, "VISTA 3D (modelo FreeCAD)", fs=2.6, anchor="start", peso="bold")
        L.add(f'<image x="120" y="163" width="165" height="120" preserveAspectRatio="xMidYMid meet" '
              f'xlink:href="file://{img_iso}"/>')
    leyenda(L, 345, 40, [
        (lambda L, x, y: L.rect(x - 3.5, y - 1, 7, 2, relleno=C_MURO), "Muro / tabique"),
        (lambda L, x, y: (L.rect(x - 3.5, y - 1, 7, 2, relleno="#fff", borde=C_MURO, ancho=0.2),
                          L.linea([(x - 3.5, y), (x + 3.5, y)], ancho=0.12)), "Ventana"),
        (lambda L, x, y: (L.linea([(x - 3, y + 1.5), (x - 3, y - 2.5)], ancho=0.35),
                          L.add(f'<path d="M{x-3},{y-2.5} A4,4 0 0 1 {x+1},{y+1.5}" fill="none" stroke="#000" stroke-width="0.12" stroke-dasharray="0.8 0.5"/>')),
         "Puerta (abatimiento)"),
        (lambda L, x, y: L.rect(x - 3.5, y - 1.5, 7, 3, relleno=C_TERRAZA), "Terraza exterior"),
    ])
    return L


def lamina_electrica():
    L = Lamina()
    p1, p2 = base_plantas(L, tenue=True, areas=False)
    dibujar_electrico(p1, 1)
    dibujar_electrico(p2, 2)
    marco(L, "ELE-01", "INSTALACIÓN ELÉCTRICA", 2)
    filas = [("Circ.", "Destino", "Protección", "Conductor", "Fase · dif.")] + [tuple(c) for c in I.CIRCUITOS]
    tabla(L, 14, 160, [10, 56, 24, 17, 26], filas, fs=1.6, alto=4.3)
    L.txt(18, 157, "CUADRO DE CARGAS — TDA (Tablero de distribución)", fs=2.4, anchor="start", peso="bold")
    partes = I.GENERAL.split(" · ")
    for k_, linea in enumerate((" · ".join(partes[:3]), " · ".join(partes[3:]))):
        L.txt(14, 160 + 4.3 * len(filas) + 3.5 + 3 * k_, linea, fs=1.5, anchor="start")
    notas(L, 152, 160, "NOTAS (DS 8/2019 · pliegos RIC SEC)", [
        "1. Anteproyecto. Lo calcula, ejecuta y declara (TE1) un instalador",
        "   SEC; FV con TE4 (RGR 01/02) y cargador EV con TE6 (RIC 15).",
        "2. Diferencial ≤ 30 mA en todo circuito de alumbrado y enchufes, máx.",
        "   3 circuitos por diferencial (RIC 10 5.1.3.5 y 5.1.3.7). Tipo A en",
        "   cargas electrónicas; tipo B en el EV.",
        "3. Enchufes de alvéolos protegidos (RIC 10 5.1.2.8), con tierra.",
        "4. Baños: sin enchufes en volúmenes 0-1-2 (≥ 0,60 m de la ducha).",
        "   Exterior IP44 bajo alero / IP54 a la intemperie (RIC 10 5.2).",
        "5. Recintos > 10 m²: 2 centros, cada uno con su interruptor.",
        "6. Alturas (estatura 1,64 m): interruptores 1,05 m · enchufes 0,30 m",
        "   · cocina y lavandería 1,05 m (mesón 0,85 m) · TDA eje 1,50 m.",
        "7. Canalización PVC conduit Ø20 embutida en cámara técnica (no",
        "   perfora la barrera de vapor). Nada a la vista (mascotas).",
        "8. Detectores de humo interconectados 220 V + batería (DH) y",
        "   térmico en cocina (DT). Sin gas: no se requiere detector de CO.",
        "9. Inversor híbrido con AFCI (Res. SEC 33.038, desde 01-01-2026);",
        "   su salida de respaldo alimenta el TDA-R (C1, C2, C4, C8, C13).",
        "10. Canalización dibujada como árbol por circuito (color) desde su",
        "   tablero; al P2 sube por una montante en el tabique del pasillo.",
        "   Diagrama unilineal, cuadro de cargas y frente del tablero: TAB-01.",
        "11. Exterior (C15, EV, C8 caseta, pozo): ductos enterrados en EXT-01.",
    ], fs=1.6)
    leyenda(L, 345, 40, [
        (lambda L, x, y: sim_luz(L, x, y, "cielo"), "Luminaria de cielo"),
        (lambda L, x, y: sim_luz(L, x, y, "muro"), "Aplique de muro"),
        (lambda L, x, y: sim_interruptor(L, x - 1, y + 1, "simple"), "Interruptor 9/12"),
        (lambda L, x, y: sim_interruptor(L, x - 1, y + 1, "doble"), "Interruptor doble 9/32"),
        (lambda L, x, y: sim_interruptor(L, x, y, "conmutador"), "Conmutador 9/24"),
        (lambda L, x, y: sim_enchufe(L, x, y, False), "Enchufe 10/16 A alvéolos prot."),
        (lambda L, x, y: sim_enchufe(L, x - 1, y, True), "Enchufe IP44 (húmedo)"),
        (lambda L, x, y: sim_tablero(L, x, y + 1, ""), "Tablero distribución TDA"),
        (lambda L, x, y: sim_conexion(L, x, y, ""), "Conexión fija de equipo"),
        (lambda L, x, y: sim_detector(L, x, y, "humo"), "Detector humo / térmico"),
        (lambda L, x, y: sim_medidor(L, x, y, "kWh"), "Medidor bidireccional"),
        (lambda L, x, y: (L.rect(x - 2.6, y - 1.6, 5.2, 3.2, relleno="#eef3fb", borde="#1f4e9c", ancho=0.35),
                          L.txt(x, y + 0.6, "INV", fs=1.3, peso="bold", color="#1f4e9c")), "Inversor híbrido 6 kW"),
        (lambda L, x, y: (L.rect(x - 2.6, y - 1.6, 5.2, 3.2, relleno="#1f4e9c", borde="#1f4e9c", ancho=0.35),
                          L.txt(x, y + 0.6, "BAT", fs=1.3, peso="bold", color="#fff")), "Batería LiFePO4 11 kWh"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_CABLE, ancho=0.2, dash="1 0.6"),
         "Retorno interruptor→luz"),
        (lambda L, x, y: L.txt(x, y + 0.6, "C3", fs=1.8, color="#05a"), "N° de circuito"),
        (lambda L, x, y: L.rect(x - 1.2, y - 1.2, 2.4, 2.4, relleno="#05a", borde="#05a", ancho=0.2), "Montante a P2"),
    ])
    L.txt(345, 146, "CANALIZACIÓN POR CIRCUITO", fs=2.2, anchor="start", peso="bold")
    for k, c in enumerate(C_CIRC):
        x, y = 345 + (k % 4) * 16, 151 + (k // 4) * 4.4
        L.linea([(x, y), (x + 6, y)], color=C_CIRC[c], ancho=0.6)
        L.txt(x + 7, y + 0.6, c, fs=1.6, anchor="start")
    return L


def lamina_gasfiteria():
    L = Lamina()
    p1, p2 = base_plantas(L, tenue=True, areas=False)
    dibujar_gasfiteria(p1, 1)
    dibujar_gasfiteria(p2, 2)
    marco(L, "SAN-01", "AGUA POTABLE, AGUA CALIENTE Y ALCANTARILLADO", 3)
    tabla(L, 18, 160, [34, 46, 40], [
        ("Red", "Material", "Diámetro"),
        ("Agua fría matriz", "PPR PN20 / PEX", "Ø32 mm (1\")"),
        ("Agua fría/caliente", "PPR PN20 / PEX", "Ø20–25 mm"),
        ("Descarga WC, B.A.S.", "PVC sanitario", "Ø110 mm"),
        ("Ducha, lavadero, lavaplatos", "PVC sanitario", "Ø50 mm"),
        ("Lavamanos", "PVC sanitario", "Ø40 mm"),
        ("Ventilación", "PVC sanitario", "Ø75 mm a techo"),
        ("Calefacción (BC ↔ colectores)", "PE-RT/PEX aislado", "Ø25 mm"),
        ("Piso radiante (sólo P1)", "PE-Xa c/ barrera O₂", "Ø16 mm, paso 15 cm"),
        ("Ventiloconvectores P2", "PE-RT aislado", "Ø20 mm por entrepiso"),
    ], fs=1.9)
    notas(L, 150, 160, "NOTAS (RIDAA DS 50/2002 · DS 236/1926 · DS 735)", [
        "1. Anteproyecto. Proyecto sanitario firmado por profesional y aprobado",
        "   por la SEREMI de Salud Los Ríos (agua y alcantarillado particular).",
        "2. CASA SIN GAS: agua caliente con bomba de calor (BC) + acumulador",
        "   300 L a 55-60 °C, ciclo antilegionella semanal ≥ 60 °C y válvula",
        "   mezcladora termostática (VMT) a 45 °C por seguridad de los niños.",
        "3. Presión: ≥ 14 m.c.a. en el artefacto más desfavorable. Presurizadora",
        "   de velocidad variable, partida 30 / detención ≤ 42 m.c.a. (dif. ≤ 12).",
        "4. Pendiente de descargas 3 % (art. 88; 1 % sólo justificado). C.I. en",
        "   cada cambio de dirección y cada 30 m máx. Sifón con sello ≥ 50 mm.",
        "5. Llave de paso AF y AC en cada baño, cocina y lavandería (art. 52 e).",
        "6. Montantes AF/AC y bajada B.A.S. alineados: baño P2 sobre baño P1.",
        "7. Fosa séptica 2.400 L + drenes (DS 236), a ≥ 20 m del pozo. Cocina pasa",
        "   antes por cámara desgrasadora (C.D.), que se limpia cada 2–3 meses.",
        "8. Pozo: análisis NCh 409 con Fe, Mn y As; filtros 20/5 µm, catalítico",
        "   Fe/Mn si sale alto, y UV (caseta, ver EMP-01 / EXT-01).",
        "9. AF/AC NO van embutidas en el radier (piso radiante): suben por la",
        "   cámara técnica de los muros y cruzan por el ENTREPISO (banda gris),",
        "   en PEX sin uniones ocultas y con registro en el cielo.",
        "10. Descargas bajo el radier sólo en tramos cortos hasta la cámara",
        "   exterior. Pasadas del sobrecimiento con camisa dejada al hormigonar.",
        "11. Baños: membrana impermeable bajo la cerámica (15 cm en muros, 2 m",
        "   en ducha). Baño P2 sobre madera: placa cementicia + membrana +",
        "   desagüe lineal; B.A.S. insonorizada con abrazaderas con goma.",
    ], fs=1.6)
    leyenda(L, 345, 40, [
        (leyenda_linea(C_AF, 0.45), "Agua fría (AF)"),
        (leyenda_linea(C_AC, 0.45, "1.6 0.8"), "Agua caliente (AC)"),
        (leyenda_linea(C_ALC, 0.7), "Alcantarillado"),
        (leyenda_linea(C_HID, 0.55, "3 1 0.6 1"), "Calefacción (BC)"),
        (lambda L, x, y: L.circ(x, y, 0.8, relleno=C_AF, borde="#000", ancho=0.15), "Montante AF"),
        (lambda L, x, y: L.circ(x, y, 0.8, relleno=C_AC, borde="#000", ancho=0.15), "Montante AC"),
        (lambda L, x, y: L.circ(x, y, 1.1, relleno=C_ALC, borde="#000", ancho=0.15), "Bajada aguas servidas"),
        (lambda L, x, y: L.rect(x - 1.6, y - 1.6, 3.2, 3.2, relleno="#fff", borde=C_ALC, ancho=0.4), "Cámara de inspección"),
        (lambda L, x, y: (L.rect(x - 1.6, y - 1.6, 3.2, 3.2, relleno="#fff", borde=C_ALC, ancho=0.4),
                          L.rect(x - 0.9, y - 0.9, 1.8, 1.8, relleno=C_ALC)), "Cámara desgrasadora"),
        (lambda L, x, y: (L.linea([(x - 3.5, y), (x + 3.5, y)], color="#d5d5d5", ancho=1.6),
                          L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_AF, ancho=0.45)), "Tramo por entrepiso"),
        (lambda L, x, y: (L.circ(x, y, 0.75, relleno="#fff", borde="#000", ancho=0.25),
                          L.linea([(x - 0.75, y), (x + 0.75, y)], ancho=0.2)), "Pasada con camisa"),
        (lambda L, x, y: sim_medidor(L, x, y, "LLP"), "Llave de paso general"),
        (lambda L, x, y: L.circ(x, y, 2, relleno="#fde2e2", borde="#333", ancho=0.25), "Acumulador ACS 300 L"),
        (lambda L, x, y: L.rect(x - 3, y - 1.5, 6, 3, relleno="#efe3f6", borde=C_HID, ancho=0.4), "Bomba de calor / colector"),
    ])
    L.txt(345, 139, "WC inodoro · LV lavamanos · DU ducha", fs=1.7, anchor="start", color="#444")
    L.txt(345, 143, "LP lavaplatos · LD lavadero · LAV lavadora", fs=1.7, anchor="start", color="#444")
    L.txt(345, 147, "IND inducción · ACS acumulador", fs=1.7, anchor="start", color="#444")
    return L


def main():
    os.makedirs(SALIDA, exist_ok=True)
    iso = os.path.join(AQUI, "laminas", "vista_3d.png")
    pdfs = []
    import generar_especialidades as GE
    import generar_estructura_topo as GT
    import generar_interiorismo as GI
    import generar_a4
    import generar_tablero_exterior as GX
    import generar_escaleras as GS
    svgs, laminas = [], []
    for nombre, lam in (("01_arquitectura", lamina_arquitectura(iso)),
                        ("02_electrico", lamina_electrica()),
                        ("03_gasfiteria", lamina_gasfiteria()),
                        ("04_emplazamiento", GE.lamina_emplazamiento()),
                        ("05_techumbre_fv_lluvias", GE.lamina_techumbre()),
                        ("06_ventilacion_calefaccion", GE.lamina_ventilacion()),
                        ("07_elevaciones_corte", GE.lamina_elevaciones()),
                        ("08_estructura", GT.lamina_estructura()),
                        ("09_topografia", GT.lamina_topografia()),
                        ("10_interiorismo", GI.lamina_interiorismo()),
                        ("11_iluminacion_domotica", GI.lamina_domotica()),
                        ("12_tablero_electrico", GX.lamina_tablero()),
                        ("13_obras_exteriores", GX.lamina_exteriores()),
                        ("14_escaleras", GS.lamina_escaleras())):
        svg = os.path.join(SALIDA, nombre + ".svg")
        pdf = os.path.join(SALIDA, nombre + ".pdf")
        with open(svg, "w", encoding="utf-8") as f:
            f.write(lam.svg())
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, svg], check=True)
        subprocess.run(["rsvg-convert", "-w", "2400", "-o", os.path.join(SALIDA, nombre + ".png"), svg], check=True)
        pdfs.append(pdf)
        svgs.append(svg)
        laminas.append((nombre, lam))
        print("OK", pdf)
    juego = os.path.join(SALIDA, "PLANOS_COMPLETOS.pdf")
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", juego, *svgs], check=True)
    print("OK", juego)
    print("OK", generar_a4.generar(laminas, SALIDA))


if __name__ == "__main__":
    main()
