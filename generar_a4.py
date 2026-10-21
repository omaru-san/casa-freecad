#!/usr/bin/env python3
"""Juego de planos para impresora casera A4: una vista por hoja, ampliada.

Toma las mismas láminas A3 (vectoriales) y recorta cada vista —planta, elevación,
tabla, simbología— en su propia hoja A4 apaisada, agrandada hasta llenar el papel.
Se llama desde generar_laminas.py. Las vistas a escala llevan escala gráfica, que
es la que vale para medir sobre el papel.

Salida: laminas/PLANOS_A4.pdf
"""
import os
import subprocess
from html import escape

AW, AH = 297, 210            # A4 apaisado
MX, TOP, BOT = 8, 18, 12     # márgenes, encabezado y pie (mm)
SEP = 6                      # separación entre recortes de una misma hoja
F_MAX = 2.0                  # no agrandar más que esto (tablas cortas)
FUENTE = "Helvetica, Arial, sans-serif"
FECHA = "20-10-2026"

# Simbologías (x0, y0, x1, y1 en mm de la lámina A3), que acompañan a cada planta
SIM_ARQ = (340, 32, 409, 80)
SIM_ELE = (340, 32, 409, 168)
SIM_SAN = (340, 32, 409, 150)
SIM_TEC = (340, 32, 409, 110)
SIM_VEN = (340, 32, 409, 120)
SIM_EST = (340, 32, 409, 100)
SIM_DOM = (340, 30, 409, 135)
# Plantas tipo: mismo tamaño de recorte en ambos pisos -> misma ampliación
P1 = (11, 15, 160, 129)
P2 = (176, 15, 325, 129)

# Por lámina: hojas (título, [recortes], escala de la lámina A3 o None si no aplica)
VISTAS = {
    "01_arquitectura": [
        ("Planta primer piso", [P1, SIM_ARQ], 100),
        ("Planta segundo piso", [P2, SIM_ARQ], 100),
        ("Cuadro de superficies, notas y vista 3D", [(11, 150, 288, 286)], None),
    ],
    "02_electrico": [
        ("Planta primer piso", [P1, SIM_ELE], 100),
        ("Planta segundo piso", [P2, SIM_ELE], 100),
        ("Cuadro de cargas y notas", [(11, 150, 290, 248)], None),
    ],
    "03_gasfiteria": [
        ("Planta primer piso", [(11, 15, 160, 150), SIM_SAN], 100),
        ("Planta segundo piso", [(176, 15, 325, 150), SIM_SAN], 100),
        ("Materiales y notas", [(11, 150, 290, 232)], None),
    ],
    "04_emplazamiento": [
        ("Emplazamiento en el terreno", [(11, 15, 235, 171)], 250),
        ("Carta solar y rosa de vientos", [(240, 25, 409, 115)], None),
        ("Contexto 1:5000 y decisiones de diseño", [(235, 120, 409, 243)], None),
        ("Clima del sitio", [(11, 172, 240, 255)], None),
    ],
    "05_techumbre_fv_lluvias": [
        ("Planta de techumbre", [(11, 15, 160, 130), SIM_TEC], 100),
        ("Diagrama unilineal FV y producción mensual", [(195, 30, 340, 160)], None),
        ("Aguas lluvias y simulación FV + batería", [(11, 170, 215, 230)], None),
    ],
    "06_ventilacion_calefaccion": [
        ("Planta primer piso", [P1, SIM_VEN], 100),
        ("Planta segundo piso", [P2, SIM_VEN], 100),
        ("Balance térmico y criterios", [(11, 170, 215, 240)], None),
    ],
    "07_elevaciones_corte": [
        ("Elevación norte", [(11, 15, 200, 135)], 100),
        ("Elevación sur", [(200, 15, 389, 135)], 100),
        ("Corte A-A", [(11, 145, 212, 255)], 100),
        ("Envolvente térmica zona G", [(215, 145, 409, 202)], None),
        ("Detalle del entrepiso acústico", [(215, 202, 409, 246)], None),
    ],
    "08_estructura": [
        ("Muros de corte primer piso", [(11, 15, 180, 135), SIM_EST], 100),
        ("Entrepiso, cerchas y muros de corte segundo piso", [(190, 15, 340, 121), SIM_EST], 100),
        ("Cercha tipo y elementos de madera", [(195, 120, 335, 215)], None),
        ("Sismo, muros de corte y cargas a fundación", [(11, 170, 195, 248)], None),
    ],
    "09_topografia": [
        ("Plano topográfico del lote", [(11, 15, 225, 175)], 250),
        ("Contexto 1:5000", [(290, 25, 409, 145)], None),
        ("Perfiles del terreno", [(290, 145, 409, 240)], None),
        ("Movimiento de tierra y notas", [(11, 175, 240, 230)], None),
    ],
    "10_interiorismo": [
        ("Planta amoblada primer piso", [P1], 100),
        ("Planta amoblada segundo piso", [P2], 100),
        ("Muebles a medida primer piso", [(11, 129, 151, 242)], None),
        ("Muebles a medida segundo piso", [(151, 129, 290, 232)], None),
        ("Materialidad, simbología y criterios", [(340, 30, 409, 143), (340, 143, 409, 215)], None),
    ],
    "11_iluminacion_domotica": [
        ("Planta primer piso", [P1, SIM_DOM], 100),
        ("Planta segundo piso", [P2, SIM_DOM], 100),
        ("Escenas de Home Assistant", [(11, 128, 190, 179)], None),
        ("Arquitectura de la domótica", [(11, 178, 150, 216)], None),
        ("Equipos por etapa", [(150, 178, 290, 216)], None),
    ],
    "12_tablero_electrico": [
        ("Diagrama unilineal TDA y TDA-R", [(11, 18, 409, 150)], None),
        ("Cuadro de cargas", [(11, 158, 125, 262)], None),
        ("Frente de los tableros y notas", [(126, 155, 290, 225), (288, 150, 409, 240)], None),
    ],
    "13_obras_exteriores": [
        ("Planta de obras exteriores", [(11, 15, 270, 207)], 200),
        ("Simbología y criterios", [(295, 25, 409, 160)], None),
        ("Cuadro de obras exteriores", [(11, 204, 190, 268)], None),
    ],
    "14_escaleras": [
        ("Alternativas A, B y C", [(11, 13, 251, 214)], None),
        ("Alternativas D y E (elegida)", [(250, 13, 409, 214)], None),
        ("Lo común y comparación", [(11, 214, 290, 286)], None),
    ],
}


def txt(x, y, s, fs, anchor="start", peso="normal", color="#222"):
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{fs}" text-anchor="{anchor}" font-weight="{peso}" '
            f'fill="{color}" font-family="{FUENTE}">{escape(s)}</text>')


def barra_escala(x1, y, mm_por_m):
    """Escala gráfica que termina en x1; elige un largo redondo de 30-80 mm."""
    metros = next(m for m in (1, 2, 5, 10, 20, 50, 100) if m * mm_por_m >= 30)
    largo, partes = metros * mm_por_m, 5 if metros in (5, 50) else 4
    x0 = x1 - largo
    s = [txt(x0 - 2, y + 2.6, "Escala gráfica", 2.2, anchor="end", color="#555")]
    for i in range(partes):
        relleno = "#222" if i % 2 == 0 else "#fff"
        s.append(f'<rect x="{x0 + i * largo / partes:.2f}" y="{y}" width="{largo / partes:.2f}" height="1.6" '
                 f'fill="{relleno}" stroke="#222" stroke-width="0.2"/>')
    s.append(txt(x0, y + 4.8, "0", 2, anchor="middle"))
    s.append(txt(x1, y + 4.8, f"{metros} m", 2, anchor="middle"))
    return "".join(s)


def hoja(contenido, codigo, titulo, vista, recortes, escala, n, total):
    """SVG de una hoja A4 con los recortes de la lámina lado a lado, a la mayor ampliación posible."""
    ancho = sum(x1 - x0 for x0, _, x1, _ in recortes) + SEP * (len(recortes) - 1)
    alto = max(y1 - y0 for _, y0, _, y1 in recortes)
    f = min((AW - 2 * MX) / ancho, (AH - TOP - BOT) / alto, F_MAX)
    x = MX + ((AW - 2 * MX) - ancho * f) / 2
    s = [f'<rect width="{AW}" height="{AH}" fill="#fff"/>']
    for x0, y0, x1, y1 in recortes:
        w, h = x1 - x0, y1 - y0
        s.append(f'<svg x="{x:.2f}" y="{TOP:.2f}" width="{w * f:.2f}" height="{h * f:.2f}" '
                 f'viewBox="{x0} {y0} {w} {h}" overflow="hidden">{contenido}</svg>')
        x += (w + SEP) * f
    s.append(f'<line x1="{MX}" y1="{TOP - 3}" x2="{AW - MX}" y2="{TOP - 3}" stroke="#222" stroke-width="0.3"/>')
    s.append(txt(MX, 9, f"{codigo} · {titulo}", 3.4, peso="bold"))
    s.append(txt(MX, 13.4, vista, 3.0, color="#444"))
    detalle = f"Escala ≈ 1:{round(escala / f / 5) * 5} — medir con la escala gráfica" if escala else "Sin escala"
    s.append(txt(AW - MX, 9, f"Hoja {n} de {total}", 3.0, anchor="end", peso="bold"))
    s.append(txt(AW - MX, 13.4, detalle, 2.4, anchor="end", color="#444"))
    s.append(f'<line x1="{MX}" y1="{AH - BOT + 3}" x2="{AW - MX}" y2="{AH - BOT + 3}" stroke="#999" stroke-width="0.2"/>')
    s.append(txt(MX, AH - 5, f"VIVIENDA 2 PISOS — ANTEPROYECTO · {FECHA} · Juego de planos A4, "
                 "una vista por hoja.", 2.2, color="#555"))
    s.append(txt(MX, AH - 2.2, "Medidas aproximadas — verificar en terreno. +Y = norte geográfico.", 2.2, color="#a33"))
    if escala:
        s.append(barra_escala(AW - MX, AH - 8, 1000 / escala * f))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{AW}mm" height="{AH}mm" viewBox="0 0 {AW} {AH}">' + "".join(s) + "</svg>")


def generar(laminas, salida):
    """laminas: lista de (nombre, Lamina). Escribe PLANOS_A4.pdf en la carpeta salida."""
    total = sum(len(VISTAS[nombre]) for nombre, _ in laminas)
    n = 0
    # Los SVG temporales van en la misma carpeta de salida: rsvg-convert sólo carga
    # imágenes (vista 3D) que estén junto al SVG o debajo de él.
    svgs = []
    try:
        for nombre, lam in laminas:
            contenido = "".join(lam.p)
            for vista, recortes, escala in VISTAS[nombre]:
                n += 1
                svg = os.path.join(salida, f".a4_{n:02d}.svg")
                with open(svg, "w", encoding="utf-8") as fh:
                    fh.write(hoja(contenido, lam.codigo, lam.titulo, vista, recortes, escala, n, total))
                svgs.append(svg)
        pdf = os.path.join(salida, "PLANOS_A4.pdf")
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, *svgs], check=True)
    finally:
        for svg in svgs:
            os.remove(svg)
    return pdf
