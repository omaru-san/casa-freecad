"""Lámina ESC-01: alternativas de escalera entre el pasillo del P1 y el hall del P2 (datos en escaleras_datos.py).

Cada columna: vista 3D del modelo Escaleras.FCStd (construir_escaleras.py), planta 1:50, estructura,
ventajas y cuidados. Abajo, lo común a todas y la matriz de comparación.
"""
import math
import os

import casa_datos as D
import escaleras_datos as X
from generar_laminas import AQUI, C_MURO, Lamina, marco, notas, num

K = 20.0                       # 1:50 -> 1 m = 20 mm
VX0, VY1 = 7.55, 2.30          # esquina superior izquierda de la ventana de planta (m)
COL, PASO = 14, 79.6           # x de la primera columna y separación entre columnas (mm)
C_LENGA, C_GUARDA, C_PRO, C_CONTRA = "#a8743f", "#555", "#2e7d32", "#b23a3a"


class Plano:
    def __init__(self, L, x0, y0):
        self.L, self.x0, self.y0 = L, x0, y0

    def P(self, x, y):
        return self.x0 + (x - VX0) * K, self.y0 + (VY1 - y) * K

    def poly(self, pts, **kw):
        self.L.linea([self.P(*p) for p in pts], **kw)

    def muro(self, a, b, e, vanos=()):
        """Muro a-b de espesor e, con vanos (desde, hasta) medidos sobre su eje."""
        (x1, y1), (x2, y2) = a, b
        horiz = y1 == y2
        u0, u1 = (x1, x2) if horiz else (y1, y2)
        cortes = [u0] + [v for vano in sorted(vanos) for v in vano] + [u1]
        for s0, s1 in zip(cortes[::2], cortes[1::2]):
            pts = [(s0, y1 - e / 2), (s1, y1 - e / 2), (s1, y1 + e / 2), (s0, y1 + e / 2)] if horiz else \
                [(x1 - e / 2, s0), (x1 + e / 2, s0), (x1 + e / 2, s1), (x1 - e / 2, s1)]
            self.poly(pts, cerrar=True, relleno=C_MURO, color=C_MURO, ancho=0.1)


def recorrido(alt):
    """Línea de huella (subida) por el centro de los carriles."""
    if alt["tipo"] == "helicoidal":
        return D.FLECHA_ESCALERA
    yn, ys = sum(X.CN) / 2, sum(X.CS) / 2
    if alt["pivote"]:
        px, py = alt["pivote"]
        r = (yn - ys) / 2
        arco = [(px - r * math.sin(math.pi * k / 12), py + r * math.cos(math.pi * k / 12)) for k in range(13)]
        return [(10.30, yn)] + arco + [(10.30, ys)]
    xm = (7.85 + X.XE - 7 * X.HU) / 2
    return [(10.30, yn), (xm, yn), (xm, ys), (10.30, ys)]


def planta(L, alt, x0, y0):
    pl = Plano(L, x0, y0)
    hx0 = alt["hueco"][0]
    xo = round(hx0 - 0.05, 2)                       # eje del tabique oeste de la escalera
    vano = next(p for p in D.PUERTAS_1 if p[4] == 0 and p[1] == 2)
    pl.muro((7.8, 0), (10.5, 0), D.EXT)
    pl.muro((7.8, 2), (10.5, 2), D.INT, [(vano[0] - vano[2] / 2, vano[0] + vano[2] / 2)])
    pl.muro((xo, 0), (xo, 2), D.INT)
    pl.muro((10.5, 0), (10.5, 2), D.INT, [(0.125, 0.975)])
    if alt["franja"]:   # franja que libera la escalera: se suma a la lavandería (tabique movido) o es un recinto
        if alt["tipo"] == "helicoidal":
            pl.muro((7.8, 0), (7.8, 2), D.INT)
        else:
            pl.poly([(7.8, -0.1), (7.8, 2.1)], color="#999", ancho=0.25, dash="1 0.8")
        L.txt(*pl.P((7.8 + xo) / 2, 1.0), f"+{num(xo - 7.8)}\n{alt['franja']}", fs=1.3, color="#666")
    for (r0, s0, r1, s1), texto in alt["abajo"]:
        pl.poly([(r0, s0), (r1, s0), (r1, s1), (r0, s1)], cerrar=True, relleno="#f3ece2", color="none")
    for i, (pts, z) in enumerate(alt["peldanos"]):
        pl.poly(pts, cerrar=True, color=C_LENGA, ancho=0.18, relleno="#fbf6ef" if i % 2 else "#f6ecdf")
    for (r0, s0, r1, s1), texto in alt["abajo"]:
        pl.poly([(r0, s0), (r1, s0), (r1, s1), (r0, s1)], cerrar=True, color="#b08a5a", ancho=0.15, dash="0.8 0.6")
    if alt["tipo"] == "helicoidal":
        for k0, k1 in alt.get("guardado", ()):
            pl.poly(D.sector_peldanos(k0, k1), cerrar=True, relleno="#ead9c2", color="#b08a5a", ancho=0.2,
                    dash="0.8 0.6")
        for pts, _ in alt["peldanos"]:
            pl.poly(pts, cerrar=True, color=C_LENGA, ancho=0.18)
        L.circ(*pl.P(*alt["centro"]), D.ESC_NUCLEO * K, relleno="#333", borde="#333")
    xg = alt["pivote"][0] if alt["pivote"] else X.XE - 7 * X.HU
    if alt["tipo"] == "helicoidal":
        pass                                            # sin guarda central: barrotes en el borde de cada peldaño
    elif alt["baranda"] == "celosia":
        n = int((X.XE - xg) / 0.095)
        for k in range(n + 1):
            cx, cy = pl.P(xg + k * 0.095, 0.975)
            L.rect(cx - 0.45, cy - 0.45, 0.9, 0.9, relleno=C_LENGA)
    else:
        pl.poly([(xg, 0.975), (X.XE, 0.975)], color=C_GUARDA, ancho=1.0)
    if alt["pivote"]:
        L.circ(*pl.P(*alt["pivote"]), 1.0, relleno=C_LENGA, borde=C_LENGA)
    camino = recorrido(alt)
    pl.poly(camino, color="#333", ancho=0.25)
    (xa, ya), (xb, yb) = (pl.P(*p) for p in camino[-2:])
    ang = math.atan2(yb - ya, xb - xa)
    L.linea([(xb - 1.8 * math.cos(ang + 0.5), yb - 1.8 * math.sin(ang + 0.5)), (xb, yb),
             (xb - 1.8 * math.cos(ang - 0.5), yb - 1.8 * math.sin(ang - 0.5))], color="#333", ancho=0.25)
    L.circ(*pl.P(*camino[0]), 0.6, relleno="#333", borde="#333")
    tx, ty = pl.P(10.3, 2.0)
    L.txt(tx, ty - 1.6, "pasillo P1 · SUBE", fs=1.4, color="#444")
    tx, ty = pl.P(10.62, 0.55)
    L.txt(tx + 1.2, ty, "hall P2", fs=1.4, color="#444", rot=-90)
    for (r0, s0, r1, s1), texto in alt["abajo"]:
        if alt["tipo"] != "helicoidal":
            L.txt(*pl.P((r0 + r1) / 2, s0 + 0.12), texto, fs=1.25, color="#7a5a32")


def columna(L, i, cod, alt):
    x0 = COL + i * PASO
    cx = x0 + 38
    L.txt(x0, 19, f"{cod} · {alt['nombre'].upper()}", fs=2.6, anchor="start", peso="bold")
    L.txt(x0, 23.5, alt["idea"], fs=1.7, anchor="start", color="#444")
    img = os.path.join(AQUI, "laminas", f"escalera_{cod}.png")
    if os.path.exists(img):
        L.add(f'<image x="{x0}" y="26" width="76" height="64" preserveAspectRatio="xMidYMid meet" '
              f'xlink:href="file://{img}"/>')
    L.txt(cx, 93, "Vista 3D (muros perimetrales ocultos)", fs=1.4, color="#777")
    if cod == X.ELEGIDA:
        L.rect(x0 + 52, 26, 24, 4.6, relleno="#2b2b2b")
        L.txt(x0 + 64, 29.3, "EN LOS PLANOS", fs=1.8, peso="bold", color="#fff")
    L.txt(x0, 99, "PLANTA P1 1:50", fs=1.7, anchor="start", peso="bold")
    planta(L, alt, x0 + 5, 101)
    y = 160
    L.txt(x0, y, "ESTRUCTURA", fs=1.9, anchor="start", peso="bold")
    for k, l in enumerate(alt["estructura"]):
        L.txt(x0, y + 3.6 + k * 2.9, l, fs=1.7, anchor="start")
    y = 175
    for titulo, items, color in (("A FAVOR", alt["pro"], C_PRO), ("CUIDADOS", alt["contra"], C_CONTRA)):
        L.txt(x0, y, titulo, fs=1.9, anchor="start", peso="bold", color=color)
        for k, l in enumerate(items):
            L.txt(x0, y + 3.6 + k * 2.9, f"• {l}", fs=1.7, anchor="start")
        y += 4.6 + len(items) * 2.9
    for k, (r, v) in enumerate((("Costo referencial", alt["costo"] if alt["costo"] != "base" else "base (100 %)"),
                                ("Se construye en", alt["etapa"]), ("¿Cambia la planta?", alt["planta"]))):
        L.txt(x0, 204 + k * 3.0, f"{r}:", fs=1.7, anchor="start", color="#666")
        L.txt(x0 + 23, 204 + k * 3.0, v, fs=1.6, anchor="start")


def matriz(L, x0, y0):
    anchos = [62] + [41.8] * len(X.ALTERNATIVAS)
    alto = 4.4
    filas = [("Criterio", *[f"{c} · {a['nombre'].split(' (')[0]}" for c, a in X.ALTERNATIVAS.items()])]
    filas += [(t, *[a["eval"][k] for a in X.ALTERNATIVAS.values()]) for k, t in X.CRITERIOS]
    filas.append(("Total", *[sum(a["eval"].values()) for a in X.ALTERNATIVAS.values()]))
    L.txt(x0, y0 - 2, "COMPARACIÓN (●●● mejor · ●○○ peor)", fs=2.4, anchor="start", peso="bold")
    for i, fila in enumerate(filas):
        yy = y0 + i * alto
        if i == 0:
            L.rect(x0, yy, sum(anchos), alto, relleno="#eee")
        cx = x0
        for j, (w, c) in enumerate(zip(anchos, fila)):
            if i and j and i < len(filas) - 1:
                for d in range(3):
                    L.circ(cx + w / 2 - 4 + d * 4, yy + alto / 2, 1.1, relleno="#333" if d < c else "#fff", borde="#333",
                           ancho=0.2)
            else:
                L.txt(cx + (1.5 if j == 0 else w / 2), yy + alto * 0.7, str(c), fs=1.8,
                      anchor="start" if j == 0 else "middle", peso="bold" if i in (0, len(filas) - 1) else "normal")
            cx += w
        L.linea([(x0, yy + alto), (x0 + sum(anchos), yy + alto)], color="#999", ancho=0.15)
    L.rect(x0, y0, sum(anchos), alto * len(filas), borde="#000", ancho=0.3)


def lamina_escaleras():
    L = Lamina()
    marco(L, "ESC-01", "ALTERNATIVAS DE ESCALERA", 14, escala="1:50 (plantas) · 3D sin escala")
    for i, (cod, alt) in enumerate(X.ALTERNATIVAS.items()):
        columna(L, i, cod, alt)
        if i:
            L.linea([(COL + i * PASO - 3, 15), (COL + i * PASO - 3, 212)], color="#ccc", ancho=0.2)
    regla = 2 * X.CH + X.HU
    h_linea, h_borde = X.huella_en_linea(X.ALTERNATIVAS["C"]["peldanos"], X.PIVOTE)
    he_linea, he_borde = X.huella_helicoidal()
    notas(L, 14, 220, "COMÚN A TODAS", [
        f"1. Entrada por el mismo vano del pasillo P1 y llegada al hall del P2: 15 contrahuellas de {X.CH * 100:.0f} cm,",
        f"   huella {X.HU * 100:.0f} cm en la línea de huella (2ch + h = {num(regla)} m).",
        "2. Baranda 0,95 m en el P2 y pasamanos continuo a 0,90 m; ningún hueco > 10 cm (bebé y gatos).",
        "3. Puertas de seguridad arriba y abajo con sensor; nariz antideslizante y luz LED en peldaños.",
        "4. Apoyos en bandas elastoméricas, sin contacto rígido con los muros de los dormitorios.",
    ], fs=1.7)
    notas(L, 150, 220, "LECTURA", [
        f"5. A–D ocupan 2,60 × 1,90 m; E sólo 1,80 × 1,90 y deja {num(D.HUECO_ESCALERA[0] - 7.85)} m para sala técnica (P1) y ropería (P2).",
        f"6. Huella a 15 cm del borde interior: C {num(h_borde)} m, E {num(he_borde)} m (en la línea de huella: {num(h_linea)} / {num(he_linea)}).",
        f"7. E: altura libre mínima {num(D.ALTURA_LIBRE)} m; camas y clósets al P2 desarmables o por ventana.",
        f"8. D pesa ≈ {num(X.peso_hormigon() / 10)[:-1]} t. Costos relativos a la A (lenga + carpintería); cotizar.",
    ], fs=1.7)
    matriz(L, 14, 252)
    return L
