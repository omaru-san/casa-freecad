"""Láminas 12 (tablero eléctrico: unilineal, frente de tableros y cuadro de cargas) y 13 (obras exteriores).
Usan los helpers de generar_laminas.py / generar_especialidades.py y los datos de instalaciones_datos.py y
especialidades_datos.py."""
import math

import especialidades_datos as E
import instalaciones_datos as I
from generar_especialidades import C_LLUVIA, TINTA2, Vista, contorno_p1, miles, norte, rotulo
from generar_laminas import C_AF, C_ALC, C_CIRC, Lamina, leyenda, marco, notas, num, tabla

C_TAB = "#1f4e9c"
C_CERCO = "#3e6e30"
C_SENDERO = "#e4d9c3"


def circuito(cod):
    return next(c for c in I.CIRCUITOS if c[0] == cod)


def grupos(tablero_r):
    """{diferencial: [circuitos]} en orden de I.CIRCUITOS, para el TDA (False) o el TDA-R (True)."""
    g = {}
    for c in I.CIRCUITOS:
        if c[0] in ("EV", "FV") or (c[0] in I.RESPALDO) != tablero_r:
            continue
        g.setdefault(c[4].split("· ")[1], []).append(c[0])
    return g


# =====================================================================
#  12 TABLERO ELÉCTRICO
# =====================================================================

def sim_automatico(L, x, y, h=5):
    """Interruptor automático (contacto inclinado + cruz) entre y e y+h."""
    L.linea([(x, y), (x, y + h * 0.3)], ancho=0.3)
    L.linea([(x, y + h * 0.3), (x + h * 0.32, y + h * 0.75)], ancho=0.3)
    L.linea([(x, y + h * 0.75), (x, y + h)], ancho=0.3)
    k = h * 0.1
    L.linea([(x - k, y + h * 0.3 - k), (x + k, y + h * 0.3 + k)], ancho=0.25)
    L.linea([(x - k, y + h * 0.3 + k), (x + k, y + h * 0.3 - k)], ancho=0.25)


def sim_diferencial(L, x, y, txt):
    L.rect(x - 4, y, 8, 5.5, relleno="#fff", borde="#000", ancho=0.3)
    L.txt(x, y + 2.4, "ID", fs=1.5, peso="bold")
    L.txt(x, y + 4.6, txt, fs=1.1, color=TINTA2)


def caja(L, x0, y0, x1, y1, t1, t2="", relleno="#fff", borde="#000"):
    L.rect(x0, y0, x1 - x0, y1 - y0, relleno=relleno, borde=borde, ancho=0.35)
    oscuro = relleno == borde
    L.txt((x0 + x1) / 2, (y0 + y1) / 2 - (0.6 if t2 else -0.6), t1, fs=1.8, peso="bold", color="#fff" if oscuro else borde)
    if t2:
        L.txt((x0 + x1) / 2, (y0 + y1) / 2 + 2.6, t2, fs=1.3, color="#fff" if oscuro else TINTA2)


def tierra(L, x, y):
    L.linea([(x, y), (x, y + 3)], ancho=0.3)
    for k, w in enumerate((3, 2, 1)):
        L.linea([(x - w, y + 3 + k), (x + w, y + 3 + k)], ancho=0.3)


def ramas(L, x0, y_bus, tablero_r, paso=11.5, gap=5):
    """Dibuja diferenciales + automáticos + rótulos bajo una barra. Devuelve la x final."""
    x = x0
    for dif, cods in grupos(tablero_r).items():
        xs = [x + i * paso for i in range(len(cods))]
        xm = (xs[0] + xs[-1]) / 2
        L.linea([(xm, y_bus), (xm, y_bus + 3)], ancho=0.3)
        sim_diferencial(L, xm, y_bus + 3, "30 mA" + (" A" if "tipo A" in dif or dif.startswith("IDR") else ""))
        L.txt(xm + 4.6, y_bus + 4.6, dif.replace(" tipo A", ""), fs=1.3, anchor="start", peso="bold", color=C_TAB)
        yb = y_bus + 12
        L.linea([(xm, y_bus + 8.5), (xm, yb)], ancho=0.3)
        L.linea([(xs[0], yb), (xs[-1], yb)], ancho=0.45)
        for xc, cod in zip(xs, cods):
            c = circuito(cod)
            sim_automatico(L, xc, yb, 6)
            L.linea([(xc, yb + 6), (xc, yb + 9)], ancho=0.3)
            L.txt(xc, yb + 11.5, cod, fs=1.8, peso="bold", color=C_CIRC.get(cod, "#000"))
            L.txt(xc - 0.4, yb + 13.5, c[1], fs=1.35, anchor="start", rot=90)
            L.txt(xc + 1.6, yb + 13.5, f"{c[2]} · {c[3]} · fase {c[4][0]}", fs=1.2, anchor="start", rot=90, color=TINTA2)
        x = xs[-1] + paso + gap
    return x


def unilineal(L):
    L.txt(15, 24, "DIAGRAMA UNILINEAL — TDA (general) y TDA-R (respaldo con batería)", fs=3.0, anchor="start", peso="bold")
    xa = 24
    caja(L, xa - 9, 29, xa + 9, 37, "RED SAESA", "BT 380/220 V aérea")
    L.linea([(xa, 37), (xa, 41)], ancho=0.4)
    caja(L, xa - 9, 41, xa + 9, 49, "kWh ↔", "medidor bidireccional")
    L.linea([(xa, 49), (xa, 52)], ancho=0.4)
    sim_automatico(L, xa, 52, 7)
    L.txt(xa + 3, 56, "General 4P 25 A", fs=1.4, anchor="start", peso="bold")
    L.linea([(xa, 59), (xa, 70)], ancho=0.4)
    # DPS tipo 1+2 a tierra
    L.linea([(xa, 63), (xa - 6, 63), (xa - 6, 65)], ancho=0.3)
    L.rect(xa - 8, 65, 4, 4, relleno="#fde2d2", borde="#c0392b", ancho=0.3)
    L.txt(xa - 6, 61.8, "DPS T1+2", fs=1.2, color="#c0392b", peso="bold")
    tierra(L, xa - 6, 69)
    L.txt(xa - 6, 77.8, "≤ 20 Ω", fs=1.2, color=TINTA2)
    # barra TDA
    y_bus = 70
    L.linea([(xa, y_bus), (238, y_bus)], ancho=0.9)
    L.txt(xa + 2, y_bus - 1.5, "BARRA TDA", fs=1.5, anchor="start", peso="bold")
    x_fin = ramas(L, 42, y_bus, False)
    # EV
    ev = circuito("EV")
    L.linea([(x_fin, y_bus), (x_fin, y_bus + 3)], ancho=0.3)
    sim_diferencial(L, x_fin, y_bus + 3, "tipo B")
    L.linea([(x_fin, y_bus + 8.5), (x_fin, y_bus + 12)], ancho=0.3)
    sim_automatico(L, x_fin, y_bus + 12, 6)
    L.txt(x_fin, y_bus + 23.5, "EV", fs=1.8, peso="bold", color="#05a")
    L.txt(x_fin - 0.4, y_bus + 25.5, ev[1], fs=1.35, anchor="start", rot=90)
    L.txt(x_fin + 1.6, y_bus + 25.5, f"{ev[2]} · {ev[3]} · gestión dinámica", fs=1.2, anchor="start", rot=90, color=TINTA2)
    # FV: inversor híbrido, paneles, batería
    xf = x_fin + 22
    L.linea([(xf, y_bus), (xf, y_bus + 3)], ancho=0.3)
    sim_diferencial(L, xf, y_bus + 3, "100 mA")
    L.linea([(xf, y_bus + 8.5), (xf, y_bus + 12)], ancho=0.3)
    sim_automatico(L, xf, y_bus + 12, 6)
    L.txt(xf + 2.5, y_bus + 15, "FV 3×16 A", fs=1.3, anchor="start", peso="bold")
    L.linea([(xf, y_bus + 18), (xf, 96)], ancho=0.3)
    caja(L, xf - 14, 96, xf + 16, 110, "INVERSOR HÍBRIDO", "6 kW trifásico · AFCI", relleno="#eef3fb", borde=C_TAB)
    caja(L, xf - 14, 124, xf + 6, 136, "PANELES", "12 × 625 Wp", relleno="#eef3fb", borde=C_TAB)
    L.linea([(xf - 4, 110), (xf - 4, 124)], color=C_TAB, ancho=0.4, dash="1.2 0.6")
    L.rect(xf - 6, 114.5, 4, 4, relleno="#fde2d2", borde="#c0392b", ancho=0.3)
    L.txt(xf - 14, 140, "Caja DC (■): fusibles · DPS DC · seccionador", fs=1.2, anchor="start", color="#c0392b")
    caja(L, xf + 10, 124, xf + 32, 136, "BATERÍA", "LiFePO4 11 kWh", relleno=C_TAB, borde=C_TAB)
    L.linea([(xf + 12, 110), (xf + 12, 124)], color=C_TAB, ancho=0.4, dash="1.2 0.6")
    # salida de respaldo → TDA-R
    xr0 = xf + 40
    L.linea([(xf + 16, 103), (xr0 - 4, 103), (xr0 - 4, 80)], color=C_TAB, ancho=0.6)
    L.txt(xf + 17, 101.6, "salida backup", fs=1.3, anchor="start", color=C_TAB, peso="bold")
    L.linea([(xr0 - 4, 80), (405, 80)], ancho=0.9)
    L.txt(xr0 - 2, 78.5, "BARRA TDA-R (respaldo)", fs=1.5, anchor="start", peso="bold", color=C_TAB)
    ramas(L, xr0 + 8, 80, True)
    L.txt(xr0 - 2, 147, "Con corte de red el inversor pasa a modo isla (< 20 ms) y el TDA-R sigue con batería y sol.",
          fs=1.4, anchor="start", color=C_TAB)


def frente_tablero(L, x0, y0, titulo, filas, mod=2.6, alto=10):
    """Vista frontal esquemática: filas DIN de 18 módulos. filas = [[(texto, módulos, color)], ...]"""
    ancho = 18 * mod
    L.txt(x0, y0 - 2, titulo, fs=1.8, anchor="start", peso="bold")
    L.rect(x0 - 2, y0, ancho + 4, len(filas) * (alto + 2) + 2, relleno="#f4f4f2", borde="#000", ancho=0.4)
    for i, fila in enumerate(filas):
        y = y0 + 2 + i * (alto + 2)
        L.linea([(x0, y + alto / 2), (x0 + ancho, y + alto / 2)], color="#bbb", ancho=0.8)
        x = x0
        for txt, m, col in fila:
            L.rect(x, y, m * mod, alto, relleno=col, borde="#555", ancho=0.2)
            L.txt(x + m * mod / 2, y + alto / 2 + 0.5, txt, fs=1.15 if m > 1 else 0.95, peso="bold",
                  color="#fff" if col in (C_TAB, "#c0392b", "#05a") else "#222", rot=0 if m > 1 else -90)
            x += m * mod
        if x < x0 + ancho:
            L.rect(x, y, x0 + ancho - x, alto, relleno="none", borde="#bbb", ancho=0.15)
            L.txt((x + x0 + ancho) / 2, y + alto / 2 + 0.5, "reserva", fs=1.0, color="#999")


def frentes(L, x0, y0):
    L.txt(x0, y0 - 7, "FRENTE DE LOS TABLEROS (esquemático, 18 módulos por fila)", fs=2.2, anchor="start", peso="bold")
    gr, ID_C, MCB_C = grupos(False), "#dfe8f5", "#fff"
    fila_ids = []
    for dif, cods in gr.items():
        fila_ids.append([(dif.split()[0], 4, ID_C)] + [(c, 1, MCB_C) for c in cods])
    tda = [[("GENERAL 4P 25A", 4, "#c0392b"), ("DPS T1+2", 4, "#fde2d2"), ("ID FV 100mA", 4, ID_C), ("FV 3×16", 4, MCB_C)],
           [("ID EV tipo B", 4, ID_C), ("EV 3×16", 4, MCB_C)] + fila_ids[0],
           fila_ids[1] + fila_ids[2],
           fila_ids[3] + [("CT", 2, "#eee")]]
    frente_tablero(L, x0, y0, "TDA — pasillo de acceso, eje 1,50 m", tda)
    filas_r = [[(dif, 4, ID_C)] + [(c, 1, MCB_C) for c in cods] for dif, cods in grupos(True).items()]
    tdar = [[("GENERAL 4P 20A", 4, C_TAB)] + filas_r[0]] + filas_r[1:]
    frente_tablero(L, x0 + 54, y0, "TDA-R — junto al TDA", tdar)


def cuadro_cargas(L, x0, y0):
    filas = [("Circ.", "Tablero", "Fase", "P inst. W", "FD", "P dem. W")]
    fases = {"R": 0.0, "S": 0.0, "T": 0.0}
    for c in I.CIRCUITOS:
        if c[0] not in I.POTENCIA:
            continue
        w, fd = I.POTENCIA[c[0]]
        fase = c[4].split(" ·")[0]
        tab = "TDA-R" if c[0] in I.RESPALDO else "TDA"
        filas.append((c[0], tab, fase, miles(w), num(fd)[:-1] if fd < 1 else "1", miles(w * fd)))
        if c[0] != "EV":
            fases[fase] += w * fd
    L.txt(x0, y0 - 3, "CUADRO DE CARGAS (potencia instalada × factor de demanda)", fs=2.2, anchor="start", peso="bold")
    tabla(L, x0, y0, [12, 16, 11, 20, 10, 20], filas, fs=1.5, alto=3.9)
    y = y0 + 3.9 * len(filas) + 4
    tot = sum(fases.values())
    v = 230
    for k, (f, w) in enumerate(fases.items()):
        L.txt(x0, y + k * 3.3, f"Fase {f}: {miles(w)} W = {num(w / v)[:-1]} A  (empalme {I.EMPALME_A} A ✓)", fs=1.5,
              anchor="start", peso="bold")
    y += 3 * 3.3 + 1.5
    for k, t in enumerate([
        f"Demanda simultánea sin EV: {miles(tot)} W. Contratado 3×{I.CONTRATADO_A} A = {miles(3 * I.CONTRATADO_A * v)} W:",
        f"en punta el inversor aporta hasta 6 kW (batería/sol) → red ≈ {miles(max(0, tot - 6000))} W ✓.",
        "El cargador EV usa sólo el remanente (gestión dinámica); el apoyo ACS (C12) no",
        "se enciende junto con la inducción (Home Assistant).",
    ]):
        L.txt(x0, y + k * 3.1, t, fs=1.45, anchor="start", color=TINTA2)


def lamina_tablero():
    L = Lamina()
    marco(L, "TAB-01", "TABLERO ELÉCTRICO — UNILINEAL Y CUADRO DE CARGAS", 12, escala="sin escala")
    unilineal(L)
    cuadro_cargas(L, 15, 166)
    frentes(L, 132, 168)
    notas(L, 292, 158, "NOTAS (DS 8/2019 · RIC SEC)", [
        "1. Anteproyecto: lo calcula, ejecuta y declara (TE1) un",
        "   instalador SEC; FV con TE4 y cargador EV con TE6.",
        "2. Tierra TN-S: electrodo de fundación (Cu desnudo 35 mm²",
        "   en la fundación, Etapa 3) + barra copperweld. ≤ 20 Ω.",
        "3. Equipotencial: cañerías metálicas, estructura de",
        "   paneles, cubierta, estanques y bomba del pozo.",
        "4. DPS tipo 1+2 en el TDA (línea aérea rural, rayos) y",
        "   DPS DC en la caja de los paneles.",
        "5. Alumbrado curva B, fuerza curva C. Diferencial 30 mA",
        "   (≤ 3 circuitos c/u); tipo A en electrónica, B en EV.",
        "6. Conductores libres de halógenos; caída de tensión",
        "   ≤ 3 % (C15 exterior en 4 mm²).",
        "7. Gabinete IP40, eje 1,50 m, rotulado y 25 % reserva.",
        "8. C8 alimenta el tablero de la caseta: guardamotor de",
        "   la bomba sumergible + presurizadora VSD.",
        "9. Inducción configurada a 4,6 kW; medidor por fase (CT)",
        "   en el TDA para Home Assistant.",
        "10. Ubicación en planta: ELE-01. Ductos exteriores: EXT-01.",
    ], fs=1.55)
    return L


# =====================================================================
#  13 OBRAS EXTERIORES
# =====================================================================

def largo(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def sim_luz_ext(L, x, y, tipo):
    if tipo == "baliza":
        L.circ(x, y, 1.1, relleno="#fff", borde="#c77d00", ancho=0.35)
        L.circ(x, y, 0.45, relleno="#c77d00", borde="none")
    elif tipo == "foco":
        L.add(f'<polygon points="{x},{y - 1.5} {x + 1.4},{y + 1} {x - 1.4},{y + 1}" fill="#f5c542" stroke="#c77d00" stroke-width="0.3"/>')
    else:
        L.circ(x, y, 1.2, relleno="#fff", borde="#c77d00", ancho=0.35)
        L.add(f'<path d="M{x - 1.2:.2f},{y:.2f} A1.2,1.2 0 0 0 {x + 1.2:.2f},{y:.2f} Z" fill="#c77d00"/>')


def lamina_exteriores():
    L = Lamina()
    marco(L, "EXT-01", "OBRAS EXTERIORES: CERCO, ACCESOS, LUCES Y DUCTOS", 13, escala="1:200")
    L.txt(130, 22, "PLANTA DE OBRAS EXTERIORES", fs=4, peso="bold")
    k = 5
    v = Vista(L, 15 + 21.5 * k, 30 + 21.5 * k, k)
    dx0, dy0, dx1, dy1 = E.DESLINDE
    # cerco del deslinde con portón de acceso
    px, py, an = E.PORTON["x"], E.PORTON["y"], E.PORTON["ancho"]
    pe = E.PORTON["peatonal"]
    v.poly([(px, py - an / 2), (px, dy0), (dx0, dy0), (dx0, dy1), (dx1, dy1), (px, py + an / 2 + pe)],
           color="#777", ancho=0.35, dash="3 1 0.6 1")
    v.txt(dx0 + 0.5, dy0 + 0.6, "Cerco del deslinde: 4 hebras + malla de campo (deslinde referencial)", fs=1.5, anchor="start",
          color=TINTA2)
    # camino y estacionamiento
    v.poly(E.ACCESO, color="#d8d3c8", ancho=3.0 * k)
    v.caja(*E.ESTACIONAMIENTO, relleno="#eeeae0", borde="#999", ancho=0.2)
    ex0, ey0, ex1, ey1 = E.ESTACIONAMIENTO
    v.txt((ex0 + ex1) / 2, ey0 + 1.4, "Estacionamiento 2 autos", fs=1.6, color=TINTA2)
    v.txt(23, -4.2, "Camino de ripio", fs=1.5, color=TINTA2)
    # portón vehicular + peatonal (hojas batientes)
    for (y_a, w_) in ((py - an / 2, an / 2), (py + an / 2, -an / 2)):
        v.poly([(px, y_a), (px - abs(w_) * 0.7, y_a + w_ * 0.7)], color="#000", ancho=0.4)
    v.poly([(px, py + an / 2), (px - pe * 0.7, py + an / 2 + pe * 0.7)], color="#000", ancho=0.4)
    rotulo(L, *v.P(px, py), *v.P(px + 1, py - 4.5), "Portón 4,0 m + peatonal 1,0 m", fs=1.4)
    rotulo(L, *v.P(*E.PILAR_ACCESO[:2]), *v.P(px + 1, 1.5), "Pilar: número, buzón, citófono", fs=1.4)
    # senderos
    for pts, ancho, nombre in E.SENDEROS:
        v.poly(pts, color="#b8a888", ancho=ancho * k + 0.5)
        v.poly(pts, color=C_SENDERO, ancho=ancho * k)
    # instalaciones de referencia (tenue)
    v.caja(E.FOSA["x"][0], E.FOSA["y"][0], E.FOSA["x"][1], E.FOSA["y"][1], relleno="#efe2d4", borde=C_ALC, ancho=0.3)
    v.txt(sum(E.FOSA["x"]) / 2, -2.0, "fosa", fs=1.3, color=C_ALC)
    for dr in E.DRENES:
        v.poly(dr, color=C_ALC, ancho=0.25, dash="2 0.8")
    v.txt(-15, 1.3, "drenes", fs=1.3, color=C_ALC)
    cx0, cy0, cx1, cy1 = E.CASETA_AGUA
    v.caja(cx0, cy0, cx1, cy1, relleno="#e3efff", borde=C_AF, ancho=0.35)
    v.txt((cx0 + cx1) / 2, cy0 + 1.2, "CASETA", fs=1.3, peso="bold", color=C_AF)
    pzx, pzy = v.P(*E.POZO)
    L.circ(pzx, pzy, 3.5, relleno="#e3efff", borde=C_AF, ancho=0.35)
    v.txt(E.POZO[0], E.POZO[1] - 1.6, "pozo", fs=1.3, color=C_AF)
    ex, ey = v.P(E.ESTANQUE["x"], E.ESTANQUE["y"])
    L.circ(ex, ey, 1.1 * k, relleno="#d6ecf7", borde=C_LLUVIA, ancho=0.35)
    v.txt(E.ESTANQUE["x"], E.ESTANQUE["y"] - 0.3, "EAL", fs=1.4, peso="bold", color=C_LLUVIA)
    # casa
    contorno_p1(v)
    v.txt(6.2, 2.4, "VIVIENDA", fs=2.6, peso="bold")
    # bodega
    bx0, by0, bx1, by1 = E.BODEGA["rect"]
    v.caja(bx0, by0, bx1, by1, relleno="#d5d8dc", borde="#333", ancho=0.4)
    v.txt((bx0 + bx1) / 2, (by0 + by1) / 2 - 0.3, "BODEGA", fs=1.6, peso="bold")
    rotulo(L, *v.P((bx0 + bx1) / 2, by1), *v.P(21.0, 6.5), "Bodega metálica (≥ 10 m de la casa)", fs=1.35)
    # cerco del patio (perro) y sus puertas
    v.poly(E.CERCO_PATIO, color=C_CERCO, ancho=0.6, dash="2.2 0.7")
    for (x, y), o, w, _ in E.PUERTAS_CERCO:
        a, b = ((x, y - w / 2), (x, y + w / 2)) if o == "v" else ((x - w / 2, y), (x + w / 2, y))
        v.poly([a, b], color="#fff", ancho=1.2)
        v.poly([a, (a[0] + w * 0.7, a[1] + w * 0.3) if o == "v" else (a[0] + w * 0.3, a[1] + w * 0.7)],
               color=C_CERCO, ancho=0.4)
    v.txt(1.0, 14.8, "PATIO CERCADO (perro)", fs=2.2, peso="bold", color=C_CERCO, anchor="start")
    v.txt(1.0, 13.7, "malla galvanizada 1,5 m enterrada 0,30 m · postes impregnados c/ 2,5 m", fs=1.4, color=C_CERCO,
          anchor="start")
    # ductos enterrados
    col = {"C8": C_CIRC["C8"], "Pozo": C_AF, "EV": "#05a", "C15": C_CIRC["C15"]}
    for nombre, pts, _ in E.DUCTOS_EXT:
        v.poly(pts, color=col[nombre], ancho=0.45, dash="1.6 0.6")
        for p in pts[1:-1]:
            X, Y = v.P(*p)
            L.rect(X - 0.8, Y - 0.8, 1.6, 1.6, relleno="#fff", borde=col[nombre], ancho=0.3)
    # luces, residuos y antena
    for x, y, tipo, _ in E.LUCES_EXT:
        sim_luz_ext(L, *v.P(x, y), tipo)
    for (x, y), t in E.RESIDUOS:
        X, Y = v.P(x, y)
        L.rect(X - 1.6, Y - 1.2, 3.2, 2.4, relleno="#8d6e4a", borde="#000", ancho=0.2)
    rotulo(L, *v.P(*E.RESIDUOS[1][0]), *v.P(17.5, 18.5), "Compostera cerrada", fs=1.35)
    rotulo(L, *v.P(*E.RESIDUOS[0][0]), *v.P(26.0, 6.0), "Basura", fs=1.35)
    X, Y = v.P(*E.ANTENA[:2])
    L.add(f'<polygon points="{X},{Y - 2} {X + 1.6},{Y + 1.2} {X - 1.6},{Y + 1.2}" fill="none" stroke="#05a" stroke-width="0.4"/>')
    rotulo(L, X, Y, *v.P(11.0, 9.5), "Antena internet (frontón E)", fs=1.35, anchor="end")
    # empalme aéreo
    v.poly([(28.5, 3.4), (I.MEDIDOR_ELEC[0], I.MEDIDOR_ELEC[1])], color="#000", ancho=0.3, dash="3 1")
    v.txt(26.5, 4.4, "Empalme aéreo", fs=1.4)
    norte(L, 30, 48)
    for i in range(5):
        L.rect(24 + i * 10, 200, 10, 1.2, relleno="#000" if i % 2 == 0 else "#fff", borde="#000", ancho=0.2)
    L.txt(24, 204, "0", fs=1.5)
    L.txt(74, 204, "10 m", fs=1.5)

    # cuadro de cantidades
    cerco_patio = largo(E.CERCO_PATIO)
    deslinde = 2 * ((dx1 - dx0) + (dy1 - dy0)) - an - pe
    m2_send = sum(largo(p) * a for p, a, _ in E.SENDEROS)
    n_luz = {t: sum(1 for *_, tp, _d in E.LUCES_EXT if tp == t) for t in ("baliza", "foco", "aplique")}
    filas = [("Ítem", "Especificación", "Cantidad"),
             ("Patio cercado (perro)", "Malla galv. 1,5 m enterrada 0,30 m, postes 3×3\" impregnados c/ 2,5 m", f"{num(cerco_patio)} m"),
             ("Puertas del patio", "Peatonal 1,0 m con cierre automático + portón 3,0 m de jardín", "2 u"),
             ("Cerco del deslinde", "4 hebras + malla de campo (largo referencial: definir con la escritura)", f"{miles(deslinde)} m"),
             ("Portón de acceso", "Vehicular 4,0 m batiente con motor 24 V y batería + peatonal 1,0 m", "1 + 1 u"),
             ("Pilar de acceso", "Número iluminado, buzón, citófono IP, caseta de basura cerrada", "1 u"),
             ("Senderos", "Adoquín o baldosa sobre base compactada 15 cm, drenante", f"{num(m2_send)} m²"),
             ("Bodega exterior", "Metálica 3,0 × 2,6 m sobre radier, luz y enchufe (C15)", f"{num((bx1 - bx0) * (by1 - by0))} m²"),
             ("Luminarias exteriores", "LED 2700 K apantalladas, sensor + crepuscular (C15)",
              f"{n_luz['baliza']} bal. · {n_luz['foco']} foco · {n_luz['aplique']} apl."),
             ("Ductos enterrados", "Zanja 0,60 m, energía y datos separados, cinta, cámaras 40×40",
              f"{miles(sum(largo(p) for _, p, _ in E.DUCTOS_EXT))} m"),
             ("Residuos", "Caseta de basura junto al camino + compostera de 2 cámaras", "2 u"),
             ("Internet rural", "Antena 4G/5G o satelital en frontón E + ducto al rack", "1 u")]
    tabla(L, 15, 212, [34, 108, 26], filas, fs=1.45, alto=4.4)
    L.txt(15, 209, "CUADRO DE OBRAS EXTERIORES (cantidades del dibujo; cotizar con el deslinde real)", fs=2.2,
          anchor="start", peso="bold")

    leyenda(L, 300, 30, [
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_CERCO, ancho=0.6, dash="2.2 0.7"), "Cerco patio (perro)"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color="#777", ancho=0.35, dash="3 1 0.6 1"), "Cerco del deslinde"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_SENDERO, ancho=3), "Sendero pavimentado"),
        (lambda L, x, y: sim_luz_ext(L, x, y, "baliza"), "Baliza de sendero"),
        (lambda L, x, y: sim_luz_ext(L, x, y, "foco"), "Foco con sensor"),
        (lambda L, x, y: sim_luz_ext(L, x, y, "aplique"), "Aplique exterior"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_CIRC["C15"], ancho=0.45, dash="1.6 0.6"), "Ducto C15 + datos"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color="#05a", ancho=0.45, dash="1.6 0.6"), "Ducto cargador EV"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_CIRC["C8"], ancho=0.45, dash="1.6 0.6"), "Ducto C8 caseta"),
        (lambda L, x, y: L.linea([(x - 3.5, y), (x + 3.5, y)], color=C_AF, ancho=0.45, dash="1.6 0.6"), "Cable bomba del pozo"),
        (lambda L, x, y: L.rect(x - 0.8, y - 0.8, 1.6, 1.6, relleno="#fff", borde="#555", ancho=0.3), "Cámara de paso 40×40"),
        (lambda L, x, y: L.rect(x - 1.6, y - 1.2, 3.2, 2.4, relleno="#8d6e4a"), "Residuos"),
    ])
    notas(L, 300, 118, "CRITERIOS", [
        "1. El patio usa la casa como parte del cierre: la",
        "   entrada, la caseta, la fosa y el estacionamiento",
        "   quedan fuera (camión limpiafosas sin abrir el patio).",
        "2. La malla enterrada evita que el perro excave. Los",
        "   gatos no se contienen con cerco.",
        "3. Bodega metálica a ≥ 10 m de la casa (CONAF): no",
        "   hay leña ni combustibles junto a los muros.",
        "4. Luz cálida 2700 K hacia abajo (fauna, cielo",
        "   oscuro); se enciende con sensor y escena HA.",
        "5. Zanja común a 0,60 m: energía y datos en ductos",
        "   separados ≥ 0,20 m, cinta de advertencia encima.",
        "6. Senderos drenantes: el barro de Los Ríos queda",
        "   fuera del genkan.",
        "7. Basura cerrada junto al camino (recolección rural),",
        "   compost dentro del patio en compostera cerrada.",
        "8. Fajas CONAF, fosa, drenes y aguas lluvias: EMP-01.",
    ], fs=1.55)
    return L
