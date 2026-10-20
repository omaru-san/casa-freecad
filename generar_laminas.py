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
C_AF, C_AC, C_ALC, C_GAS = "#1f6fd1", "#d62728", "#7b4b2a", "#e0a000"
C_CABLE = "#c0392b"
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
    col = "#666"
    for x0, y0, x1, y1, _ in D.ESCALONES:
        pl.caja(x0, y0, x1, y1, relleno="none", borde=col, ancho=0.15)
    pl.poly(D.FLECHA_ESCALERA, color=col, ancho=0.2)
    (xa, ya), (xb, yb) = D.FLECHA_ESCALERA[-2:]
    ax, ay = pl.P(xb, yb)
    d = 1 if xb > xa else -1
    pl.L.linea([(ax - d * 1.6, ay - 0.9), (ax, ay), (ax - d * 1.6, ay + 0.9)], color=col, ancho=0.2)
    tx, ty = pl.P(*D.FLECHA_ESCALERA[0])
    pl.L.txt(tx - 4, ty - 1, "SUBE" if piso == 1 else "BAJA", fs=1.5, color=col)


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

TOTAL_LAMINAS = 9


def marco(L, codigo, titulo, n, escala="1:100 (imprimir en A3)"):
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


def dibujar_electrico(pl, piso):
    L = pl.L
    luces = I.LUCES_1 if piso == 1 else I.LUCES_2
    inter = I.INTERRUPTORES_1 if piso == 1 else I.INTERRUPTORES_2
    ench = I.ENCHUFES_1 if piso == 1 else I.ENCHUFES_2
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
    if piso == 1:
        tx, ty = pl.P(*I.TABLERO[:2])
        mx, my = pl.P(*I.MEDIDOR_ELEC[:2])
        pl.poly(I.ACOMETIDA, color="#000", ancho=0.4)
        sim_tablero(L, tx, ty, I.TABLERO[2])
        sim_medidor(L, mx, my, "kWh")
        L.txt(mx + 2.8, my + 4.2, "EMPALME", fs=1.3, anchor="start")
        import especialidades_datos as E
        ix, iy = pl.P(*E.INVERSOR[:2])
        bx, by = pl.P(E.BATERIA["x"], E.BATERIA["y"])
        L.rect(ix - 2.6, iy - 1.6, 5.2, 3.2, relleno="#eef3fb", borde="#1f4e9c", ancho=0.35)
        L.txt(ix, iy + 0.6, "INV", fs=1.3, peso="bold", color="#1f4e9c")
        L.rect(bx - 2.6, by - 1.6, 5.2, 3.2, relleno="#1f4e9c", borde="#1f4e9c", ancho=0.35)
        L.txt(bx, by + 0.6, "BAT", fs=1.3, peso="bold", color="#fff")
        pl.poly([E.INVERSOR[:2], (10.25, 1.70), (11.60, 1.70), I.TABLERO[:2]], color="#1f4e9c", ancho=0.35, dash="1.5 0.6")
        L.txt(bx - 3.4, by + 4.3, "Sala técnica bajo escalera", fs=1.2, anchor="start", color="#1f4e9c")
        tx2, ty2 = pl.P(*I.TABLERO[:2])
        flecha_e = (tx2 + 2.5, ty2 - 3.5)
        L.txt(flecha_e[0] + 1, flecha_e[1], "C8 → bomba pozo", fs=1.3, anchor="start", color="#05a")


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
    elif cod == "CAL":
        L.rect(x0, y0, ww, hh, relleno="#ffe9b0", **k)
    elif cod == "COC":
        L.rect(x0, y0, ww, hh, relleno="#fff", **k)
        for dx in (-0.25, 0.25):
            for dy in (-0.25, 0.25):
                L.circ(cx + dx * ww, cy + dy * hh, ww * 0.15, ancho=0.2)
    L.txt(cx, y0 - 0.8 if cod in ("CAL",) else cy + 0.6, cod, fs=1.3, peso="bold", color="#333")


def dibujar_gasfiteria(pl, piso):
    L = pl.L
    if piso == 1:
        redes = [(I.ALC_1, C_ALC, 0.7, None), (I.GAS_1, C_GAS, 0.45, "3 1 0.6 1"),
                 (I.AF_1, C_AF, 0.45, None), (I.AC_1, C_AC, 0.45, "1.6 0.8")]
        arts = I.ARTEFACTOS_1
    else:
        redes = [(I.ALC_2, C_ALC, 0.7, None), (I.AF_2, C_AF, 0.45, None), (I.AC_2, C_AC, 0.45, "1.6 0.8")]
        arts = I.ARTEFACTOS_2
    for a in arts:
        dibujar_artefacto(pl, *a)
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
            L.txt(px, py + 4.2 if y < 0 else py - 2.4, n, fs=1.4, color=C_ALC, peso="bold")
        ux, uy = pl.P(*I.UNION_DOMICILIARIA)
        L.circ(ux, uy, 1.3, relleno=C_ALC, borde="#000", ancho=0.2)
        L.txt(ux + (-2.5 if ux > 100 else 2.5), uy + 0.6, I.SALIDA_TEXTO, fs=1.4, anchor="end" if ux > 100 else "start",
              color=C_ALC, peso="bold")
        mx, my = pl.P(*I.MEDIDOR_AGUA)
        sim_medidor(L, mx, my, I.SIGLA_AGUA)
        L.txt(mx, my + 4, I.TEXTO_AGUA, fs=1.2, color=C_AF)
        gx, gy = pl.P(*I.MEDIDOR_GAS)
        L.rect(gx - 2, gy - 2, 4, 4, relleno="#fff6d6", borde=C_GAS, ancho=0.4)
        L.txt(gx, gy + 0.6, "MG", fs=1.2, peso="bold")
        L.txt(gx + 2.6, gy + 4.5, "Medidor gas", fs=1.2, color="#8a6a00", anchor="start")
        lx, ly = pl.P(*I.ROTULO_COLECTOR)
        L.txt(lx + 2.2, ly, "PVC Ø110 · pend. ≥ 1%", fs=1.4, color=C_ALC, rot=-90)
        lx, ly = pl.P(*I.ROTULO_COCINA)
        L.txt(lx, ly - 1.2, "PVC Ø50 → Ø110", fs=1.4, color=C_ALC)
        lx, ly = pl.P(*I.ROTULO_GAS)
        L.txt(lx, ly - 1.0, "Gas: Cu tipo L Ø1/2\" (exterior)", fs=1.3, color="#8a6a00")


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
        "2. Muros exteriores 20 cm, tabiques 10 cm. Altura piso-cielo 2,50 m.",
        "3. Entrepiso: losa 20 cm. Nivel piso 2 = +2,70 m.",
        "4. Escalera en U: 15 contrahuellas de 18 cm, huellas 25 cm,",
        "   tramos de 0,90 m. Cabe justo en la franja de 2 m de fondo.",
        "   Llega al piso 2 por el hall sobre la terraza de entrada.",
        "5. Medidas inferidas del boceto: ajustar en casa_datos.py",
        "   y regenerar con  python3 generar_laminas.py",
    ])
    if img_iso and os.path.exists(img_iso):
        L.txt(200, 160, "VISTA 3D desde el NE (modelo FreeCAD)", fs=2.6, anchor="start", peso="bold")
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
    filas = [("Circ.", "Destino", "Protección", "Conductor")] + [tuple(c) for c in I.CIRCUITOS]
    tabla(L, 18, 160, [12, 62, 34, 30], filas, fs=1.9)
    L.txt(18, 157, "CUADRO DE CARGAS — TDA (Tablero de distribución)", fs=2.4, anchor="start", peso="bold")
    L.txt(18, 160 + 5.2 * len(filas) + 4.5, I.GENERAL, fs=1.9, anchor="start")
    notas(L, 165, 160, "NOTAS", [
        "1. Propuesta preliminar según criterios RIC (SEC Chile).",
        "   Debe ser calculada, ejecutada y declarada (TE1) por",
        "   un instalador eléctrico autorizado SEC.",
        "2. Todos los circuitos de enchufes con protección",
        "   diferencial 30 mA. Enchufes con tierra (3 polos).",
        "3. Zonas húmedas: enchufes IP44 fuera del volumen",
        "   de la ducha (≥ 0,60 m).",
        "4. Alturas: enchufes 0,30 m · cocina/lavandería 1,10 m",
        "   · interruptores 1,10 m.",
        "5. Canalización en PVC conduit Ø20 mm embutido.",
        "6. Luz de escalera conmutada entre piso 1 y piso 2.",
        "7. Inversor híbrido + batería 11 kWh: ante corte de red respalda",
        "   C1, C2, C4 (refrigerador) y C8 (bomba pozo) ~28 h a 0,35 kW.",
    ], fs=1.9)
    leyenda(L, 345, 40, [
        (lambda L, x, y: sim_luz(L, x, y, "cielo"), "Luminaria de cielo"),
        (lambda L, x, y: sim_luz(L, x, y, "muro"), "Aplique de muro"),
        (lambda L, x, y: sim_interruptor(L, x - 1, y + 1, "simple"), "Interruptor 9/12"),
        (lambda L, x, y: sim_interruptor(L, x - 1, y + 1, "doble"), "Interruptor doble 9/32"),
        (lambda L, x, y: sim_interruptor(L, x, y, "conmutador"), "Conmutador 9/24"),
        (lambda L, x, y: sim_enchufe(L, x, y, False), "Enchufe 10/16 A c/tierra"),
        (lambda L, x, y: sim_enchufe(L, x - 1, y, True), "Enchufe IP44 (húmedo)"),
        (lambda L, x, y: sim_tablero(L, x, y + 1, ""), "Tablero distribución TDA"),
        (lambda L, x, y: sim_medidor(L, x, y, "kWh"), "Medidor bidireccional"),
        (lambda L, x, y: (L.rect(x - 2.6, y - 1.6, 5.2, 3.2, relleno="#eef3fb", borde="#1f4e9c", ancho=0.35),
                          L.txt(x, y + 0.6, "INV", fs=1.3, peso="bold", color="#1f4e9c")), "Inversor híbrido 6 kW"),
        (lambda L, x, y: (L.rect(x - 2.6, y - 1.6, 5.2, 3.2, relleno="#1f4e9c", borde="#1f4e9c", ancho=0.35),
                          L.txt(x, y + 0.6, "BAT", fs=1.3, peso="bold", color="#fff")), "Batería LiFePO4 11 kWh"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_CABLE, ancho=0.2, dash="1 0.6"),
         "Retorno interruptor→luz"),
        (lambda L, x, y: L.txt(x, y + 0.6, "C3", fs=1.8, color="#05a"), "N° de circuito"),
    ])
    return L


def lamina_gasfiteria():
    L = Lamina()
    p1, p2 = base_plantas(L, tenue=True, areas=False)
    dibujar_gasfiteria(p1, 1)
    dibujar_gasfiteria(p2, 2)
    marco(L, "SAN-01", "AGUA POTABLE, ALCANTARILLADO Y GAS", 3)
    tabla(L, 18, 160, [34, 46, 40], [
        ("Red", "Material", "Diámetro"),
        ("Agua fría matriz", "PPR / Cu tipo L", "Ø25 mm (3/4\")"),
        ("Agua fría/caliente", "PPR / Cu tipo L", "Ø20 mm (1/2\")"),
        ("Descarga WC, B.A.S.", "PVC sanitario", "Ø110 mm"),
        ("Ducha, lavadero, lavaplatos", "PVC sanitario", "Ø50 mm"),
        ("Lavamanos", "PVC sanitario", "Ø40 mm"),
        ("Ventilación", "PVC sanitario", "Ø75 mm a techo"),
        ("Gas licuado/natural", "Cu tipo L", "Ø1/2\" – 3/4\""),
    ], fs=1.9)
    notas(L, 150, 160, "NOTAS", [
        "1. Propuesta preliminar. Proyecto sanitario debe ser firmado por",
        "   profesional y aprobado por la sanitaria (RIDAA). Gas: instalador",
        "   autorizado SEC (TC6).",
        "2. Calefont en lavandería: exige ventilación superior e inferior",
        "   y ducto de evacuación de gases al exterior. Alternativa:",
        "   termo eléctrico o calefont tiro forzado.",
        "3. Cámaras de inspección (C.I.) en cada cambio de dirección",
        "   y cada 30 m máx. Pendiente mínima 1% (Ø110) / 3% (Ø50).",
        "4. Montantes AF/AC y bajada B.A.S. alineados: baño P2 sobre baño P1.",
        "5. Sector rural sin alcantarillado: fosa séptica 2.400 L + drenes (DS 236),",
        "   aprobación SEREMI de Salud. Agua: pozo propio (art. 56 Código de Aguas)",
        "   + análisis físico-químico y bacteriológico; desinfección UV.",
        "6. Llaves de paso en cada recinto húmedo.",
    ], fs=1.9)
    leyenda(L, 345, 40, [
        (leyenda_linea(C_AF, 0.45), "Agua fría (AF)"),
        (leyenda_linea(C_AC, 0.45, "1.6 0.8"), "Agua caliente (AC)"),
        (leyenda_linea(C_ALC, 0.7), "Alcantarillado"),
        (leyenda_linea(C_GAS, 0.45, "3 1 0.6 1"), "Gas"),
        (lambda L, x, y: L.circ(x, y, 0.8, relleno=C_AF, borde="#000", ancho=0.15), "Montante AF"),
        (lambda L, x, y: L.circ(x, y, 0.8, relleno=C_AC, borde="#000", ancho=0.15), "Montante AC"),
        (lambda L, x, y: L.circ(x, y, 1.1, relleno=C_ALC, borde="#000", ancho=0.15), "Bajada aguas servidas"),
        (lambda L, x, y: L.rect(x - 1.6, y - 1.6, 3.2, 3.2, relleno="#fff", borde=C_ALC, ancho=0.4), "Cámara de inspección"),
        (lambda L, x, y: sim_medidor(L, x, y, "HP"), "Hidropack desde pozo"),
        (lambda L, x, y: (L.rect(x - 2, y - 2, 4, 4, relleno="#fff6d6", borde=C_GAS, ancho=0.4),
                          L.txt(x, y + 0.6, "MG", fs=1.2)), "Medidor de gas"),
        (lambda L, x, y: L.rect(x - 2, y - 1.5, 4, 3, relleno="#ffe9b0", borde="#333", ancho=0.25), "Calefont (CAL)"),
    ])
    L.txt(345, 120, "WC inodoro · LV lavamanos · DU ducha", fs=1.7, anchor="start", color="#444")
    L.txt(345, 124, "LP lavaplatos · LD lavadero · LAV lavadora", fs=1.7, anchor="start", color="#444")
    L.txt(345, 128, "COC cocina a gas · CAL calefont", fs=1.7, anchor="start", color="#444")
    return L


def main():
    os.makedirs(SALIDA, exist_ok=True)
    iso = os.path.join(AQUI, "laminas", "vista_3d.png")
    pdfs = []
    import generar_especialidades as GE
    import generar_estructura_topo as GT
    svgs = []
    for nombre, lam in (("01_arquitectura", lamina_arquitectura(iso)),
                        ("02_electrico", lamina_electrica()),
                        ("03_gasfiteria", lamina_gasfiteria()),
                        ("04_emplazamiento", GE.lamina_emplazamiento()),
                        ("05_techumbre_fv_lluvias", GE.lamina_techumbre()),
                        ("06_ventilacion_calefaccion", GE.lamina_ventilacion()),
                        ("07_elevaciones_corte", GE.lamina_elevaciones()),
                        ("08_estructura", GT.lamina_estructura()),
                        ("09_topografia", GT.lamina_topografia())):
        svg = os.path.join(SALIDA, nombre + ".svg")
        pdf = os.path.join(SALIDA, nombre + ".pdf")
        with open(svg, "w", encoding="utf-8") as f:
            f.write(lam.svg())
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, svg], check=True)
        subprocess.run(["rsvg-convert", "-w", "2400", "-o", os.path.join(SALIDA, nombre + ".png"), svg], check=True)
        pdfs.append(pdf)
        svgs.append(svg)
        print("OK", pdf)
    juego = os.path.join(SALIDA, "PLANOS_COMPLETOS.pdf")
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", juego, *svgs], check=True)
    print("OK", juego)


if __name__ == "__main__":
    main()
