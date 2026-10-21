"""Láminas 10 (plantas amobladas + materialidad) y 11 (iluminación y domótica). Leen interiorismo_datos.py."""
import math

import casa_datos as D
import instalaciones_datos as I
import interiorismo_datos as N
from generar_laminas import (OX1, OX2, S, Lamina, Planta, dibujar_arquitectura, dibujar_artefacto,
                             leyenda, marco, notas, tabla, titulos_plantas)

C_LED = "#e0a100"
C_SEG = "#c0392b"
C_DOMO = {"hub": "#222", "sensor": "#1f6fd1", "seguridad": C_SEG, "actuador": "#2e8b57"}


def plantas_base(L):
    titulos_plantas(L)
    pls = []
    for piso, ox in ((1, OX1), (2, OX2)):
        pl = Planta(L, ox)
        dibujar_arquitectura(pl, piso)
        pls.append(pl)
    return pls


def aclarar(hexa, k):
    """Mezcla un color con blanco (k = 0 sin cambio, 1 = blanco)."""
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(c + (255 - c) * k):02x}" for c in (r, g, b))


def rotulos(pl, piso):
    for p, texto, x, y in N.ETIQUETAS:
        if p == piso:
            pl.L.txt(*pl.P(x, y), texto, fs=1.7, peso="bold", color="#333")


def dibujar_muebles(pl, piso, rotular=True, tenue=False):
    L = pl.L
    for cod, x, y, w, h in I.ARTEFACTOS_1 if piso == 1 else I.ARTEFACTOS_2:
        if cod not in ("DU", "LP", "IND"):  # ducha, lavaplatos e inducción quedan dentro de B2, B4 y K1
            dibujar_artefacto(pl, cod, x, y, w, h)
    for cod, p, (x0, y0, x1, y1), (z0, z1), mat, nombre, _ in N.MUEBLES:
        if p != piso:
            continue
        color = aclarar(N.MATERIALES[mat][2], 0.6 if tenue else 0)
        piso_zona = z1 <= 0.05
        if piso_zona:
            a, b = pl.P(x0, y1)
            L.add(f'<rect x="{a:.2f}" y="{b:.2f}" width="{(x1 - x0) * S:.2f}" height="{(y1 - y0) * S:.2f}" '
                  f'fill="{color}" stroke="#555" stroke-width="0.15" stroke-dasharray="0.8 0.5"/>')
        else:
            pl.caja(x0, y0, x1, y1, relleno=color, borde="#555", ancho=0.18)
        if z1 >= 2.0:  # guardado de piso a cielo: aspa
            pl.poly([(x0, y0), (x1, y1)], color="#777", ancho=0.1)
            pl.poly([(x0, y1), (x1, y0)], color="#777", ancho=0.1)
        if rotular and cod:
            cx, cy = pl.P((x0 + x1) / 2, (y0 + y1) / 2)
            fs = min(1.5, 0.75 * min(x1 - x0, y1 - y0) * S + 0.6)
            L.rect(cx - 2.1, cy - 1.2, 4.2, 2.1, relleno="#fff", borde="#333", ancho=0.12)
            L.txt(cx, cy + 0.45, cod, fs=max(fs, 1.25), peso="bold")
    if piso == 1:   # guardado oculto bajo la helicoidal (tambor de listones)
        for cod, (k0, k1), *_ in N.GUARDADO_ESCALERA:
            pl.poly(D.sector_peldanos(k0, k1), cerrar=True, color="#555", ancho=0.15,
                    relleno=aclarar(N.MATERIALES["LEN"][2], 0.6 if tenue else 0.35))
        for pts, _ in D.ESCALONES:   # los peldaños se siguen viendo encima del tambor
            pl.poly(pts, color="#666", ancho=0.12, cerrar=True)
        for cod, (k0, k1), *_ in N.GUARDADO_ESCALERA if rotular else ():
            am = math.radians(-((k0 + k1) / 2 - 0.5) * D.ESC_PASO)
            cx, cy = pl.P(D.ESC_CENTRO[0] + 0.55 * math.cos(am), D.ESC_CENTRO[1] + 0.55 * math.sin(am))
            L.rect(cx - 2.1, cy - 1.2, 4.2, 2.1, relleno="#fff", borde="#333", ancho=0.12)
            L.txt(cx, cy + 0.45, cod, fs=1.25, peso="bold")
    for p, x0, y0, x1, y1 in N.PUERTAS_SEGURIDAD:
        if p == piso:
            pl.poly([(x0, y0), (x1, y1)], color=C_SEG, ancho=0.6)


def tabla_muebles(L, x, y, piso, titulo, fs=1.4, alto=3.75):
    L.txt(x, y - 2, titulo, fs=2.2, anchor="start", peso="bold")
    filas = [m for m in N.MUEBLES if m[1] == piso and m[0]]
    if piso == 1:
        filas += [(c, 1, None, None, "LEN", f"{nombre} (oculto)", f"{guarda}. {acceso}.")
                  for c, _, acceso, nombre, guarda in N.GUARDADO_ESCALERA]
    anchos = (8, 50, 80)
    L.rect(x, y, sum(anchos), alto, relleno="#eee")
    for i, (c, t) in enumerate(zip(anchos, ("Cód.", "Mueble", "Qué esconde / resuelve"))):
        L.txt(x + sum(anchos[:i]) + 1.2, y + alto * 0.72, t, fs=fs, anchor="start", peso="bold")
    for k, (cod, _, _, _, mat, nombre, esconde) in enumerate(filas, start=1):
        yy = y + k * alto
        L.rect(x + 0.6, yy + 0.7, 2.2, alto - 1.4, relleno=N.MATERIALES[mat][2], borde="#555", ancho=0.1)
        L.txt(x + 3.4, yy + alto * 0.72, cod, fs=fs, anchor="start", peso="bold")
        L.txt(x + anchos[0] + 1.2, yy + alto * 0.72, nombre, fs=fs, anchor="start")
        L.txt(x + anchos[0] + anchos[1] + 1.2, yy + alto * 0.72, esconde or "—", fs=fs, anchor="start", color="#444")
        L.linea([(x, yy), (x + sum(anchos), yy)], color="#bbb", ancho=0.1)
    L.rect(x, y, sum(anchos), alto * (len(filas) + 1), borde="#000", ancho=0.3)


def lamina_interiorismo():
    L = Lamina()
    p1, p2 = plantas_base(L)
    for pl, piso in ((p1, 1), (p2, 2)):
        dibujar_muebles(pl, piso)
        rotulos(pl, piso)
    marco(L, "INT-01", "INTERIORISMO JAPANDI — PLANTAS AMOBLADAS", 10, escala="1:100 (imprimir en A3)")
    tabla_muebles(L, 12, 136, 1, "PRIMER PISO — MUEBLES A MEDIDA")
    tabla_muebles(L, 152, 136, 2, "SEGUNDO PISO — MUEBLES A MEDIDA")
    L.txt(345, 34, "MATERIALIDAD", fs=2.8, anchor="start", peso="bold")
    for i, (cod, (nombre, uso, color)) in enumerate(N.MATERIALES.items()):
        yy = 40 + i * 8.6
        L.rect(345, yy - 2.5, 7, 6, relleno=color, borde="#555", ancho=0.15)
        L.txt(353.5, yy - 0.2, f"{cod} · {nombre}", fs=1.45, anchor="start", peso="bold")
        L.txt(353.5, yy + 2.4, uso, fs=1.3, anchor="start", color="#555")
    leyenda(L, 345, 150, [
        (lambda L, x, y: (L.rect(x - 3.5, y - 1.5, 7, 3, relleno="#e4ded3", borde="#555", ancho=0.18),
                          L.linea([(x - 3.5, y - 1.5), (x + 3.5, y + 1.5)], color="#777", ancho=0.1),
                          L.linea([(x - 3.5, y + 1.5), (x + 3.5, y - 1.5)], color="#777", ancho=0.1)),
         "Guardado de piso a cielo"),
        (lambda L, x, y: L.rect(x - 3.5, y - 1.5, 7, 3, relleno="#c49a6c", borde="#555", ancho=0.18), "Mueble bajo / cama"),
        (lambda L, x, y: L.add(f'<rect x="{x-3.5}" y="{y-1.5}" width="7" height="3" fill="#cfc7ba" stroke="#555" '
                               f'stroke-width="0.15" stroke-dasharray="0.8 0.5"/>'), "Zona de piso (genkan, ducha)"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_SEG, ancho=0.6), "Puerta de seguridad escalera"),
    ], titulo="SIMBOLOGÍA")
    notas(L, 345, 184, "CRITERIOS", [
        "1. Japandi: madera clara, blanco cálido,",
        "   negro carbón; pocos objetos a la vista.",
        "2. Sin tiradores: apertura push o uñero.",
        "   Push con traba de niños bajo 1,20 m.",
        "3. Pasos libres ≥ 0,90 m (cocina ≥ 0,95).",
        "4. Telas lavables y porcelanato: 3 gatos",
        "   y 1 perro. Nada colgante al alcance.",
        "5. Muebles fijados al muro (sismo/niños).",
        "6. Detalle en INTERIORISMO.md",
    ], fs=1.5)
    return L


def sim_domo(L, x, y, cod):
    desc, cat = N.DOMOTICA_TIPOS[cod]
    c = C_DOMO[cat]
    L.circ(x, y, 1.45, relleno="#fff" if cat != "hub" else c, borde=c, ancho=0.3)
    L.txt(x, y + 0.5, cod, fs=1.25, peso="bold", color=c if cat != "hub" else "#fff")


def lamina_domotica():
    L = Lamina()
    p1, p2 = plantas_base(L)
    for pl, piso in ((p1, 1), (p2, 2)):
        dibujar_muebles(pl, piso, rotular=False, tenue=True)
        rotulos(pl, piso)
        for p, pts, _ in N.ILUMINACION:
            if p == piso:
                pl.poly(pts, color=C_LED, ancho=0.7)
        for p, x, y, cod in N.DOMOTICA:
            if p == piso:
                sim_domo(L, *pl.P(x, y), cod)
    # cortinas motorizadas en todas las ventanas (rollers blackout en dormitorios, screen en el resto)
    from casa_datos import VENTANAS_1, VENTANAS_2
    for pl, vents in ((p1, VENTANAS_1), (p2, VENTANAS_2)):
        for x, y, w, o, *_ in vents:
            # la línea va 22 cm hacia el interior de la casa (centro aprox. x = 7, y = 3)
            if o == "h":
                ux, uy, dx, dy = 1, 0, 0, 0.22 if y < 3 else -0.22
            else:
                ux, uy, dx, dy = 0, 1, 0.22 if x < 7 else -0.22, 0
            pl.poly([(x - ux * w / 2 + dx, y - uy * w / 2 + dy), (x + ux * w / 2 + dx, y + uy * w / 2 + dy)],
                    color="#2e8b57", ancho=0.35, dash="0.6 0.4")
    marco(L, "INT-02", "ILUMINACIÓN Y DOMÓTICA", 11)
    L.txt(12, 132, "ESCENAS (Home Assistant, funcionan sin internet)", fs=2.4, anchor="start", peso="bold")
    anchos = (24, 46, 104)
    y0, alto = 135, 4.6
    L.rect(12, y0, sum(anchos), alto, relleno="#eee")
    for i, t in enumerate(("Escena", "Se activa con", "Qué hace")):
        L.txt(12 + sum(anchos[:i]) + 1.2, y0 + alto * 0.7, t, fs=1.6, anchor="start", peso="bold")
    for k, fila in enumerate(N.ESCENAS, start=1):
        yy = y0 + k * alto
        for i, t in enumerate(fila):
            L.txt(12 + sum(anchos[:i]) + 1.2, yy + alto * 0.7, t, fs=1.6, anchor="start", peso="bold" if i == 0 else "normal")
        L.linea([(12, yy), (12 + sum(anchos), yy)], color="#bbb", ancho=0.1)
    L.rect(12, y0, sum(anchos), alto * (len(N.ESCENAS) + 1), borde="#000", ancho=0.3)
    notas(L, 12, 182, "ARQUITECTURA DE LA DOMÓTICA", [
        "1. Controlador Home Assistant local en el armario técnico G2 (junto al TDA), con UPS. Sin nube obligatoria.",
        "2. Protocolos abiertos: Zigbee 3.0 / Thread-Matter para sensores; Wi-Fi sólo para equipos grandes.",
        "3. Se conservan los interruptores físicos: micromódulos Zigbee detrás (RIC 10, un efecto por luminaria).",
        "4. Cat6 a cada recinto + PoE para cámaras y videoportero. Ducto vacío de reserva al entretecho.",
        "5. Piso radiante: una zona por recinto, termostato = sensor AM; la bomba de calor recibe SG-Ready.",
        "6. VMC sube automáticamente con CO₂ > 900 ppm o HR > 65 % (baños, cocina, lavandería).",
        "7. Cortinas motorizadas a batería recargable (sin cordones: seguridad bebé y gatos).",
        "8. Ver INTERIORISMO.md para equipos sugeridos, etapas y presupuesto.",
    ], fs=1.6)
    L.txt(152, 182, "EQUIPOS POR ETAPA (referencial 2026, cotizar)", fs=2.4, anchor="start", peso="bold")
    tabla(L, 152, 185, [26, 92, 18], [("Etapa", "Equipos", "CLP")] + N.EQUIPOS, fs=1.45, alto=4.6)
    items = [(lambda L, x, y, c=c: sim_domo(L, x, y, c), d) for c, (d, _) in N.DOMOTICA_TIPOS.items()]
    items += [
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_LED, ancho=0.7), "LED indirecto regulable"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color="#2e8b57", ancho=0.35, dash="0.6 0.4"),
         "Cortina motorizada"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_SEG, ancho=0.6), "Puerta de seguridad"),
    ]
    leyenda(L, 345, 34, items, titulo="SIMBOLOGÍA")
    return L
