# Modelo de las alternativas de escalera (escaleras_datos.py) lado a lado, y una vista 3D de cada una
# para la lámina ESC-01 (laminas/escalera_A.png ...). Se ejecuta dentro de FreeCAD.
import sys, importlib
import FreeCAD as App
import Part

CARPETA = "/Users/jai/personal/casa_freecad"
if CARPETA not in sys.path:
    sys.path.insert(0, CARPETA)
import casa_datos as D
import escaleras_datos as X
importlib.reload(D)
importlib.reload(X)

M = 1000.0
V = App.Vector
SEP = 4.5                     # separación entre alternativas en el modelo (m, en x)
LENGA, FRENTE, BLANCO = (0.77, 0.60, 0.42), (0.89, 0.87, 0.83), (0.95, 0.94, 0.91)
HORMIGON, LOSA, NEGRO = (0.62, 0.62, 0.60), (0.80, 0.78, 0.74), (0.18, 0.18, 0.18)
Z2, CH, HU = D.Z2, X.CH, X.HU
BARANDA = 0.95

NOMBRE = "Escaleras"
if NOMBRE in App.listDocuments():
    App.closeDocument(NOMBRE)
doc = App.newDocument(NOMBRE)


def caja(x0, y0, z0, x1, y1, z1):
    return Part.makeBox((x1 - x0) * M, (y1 - y0) * M, (z1 - z0) * M, V(x0 * M, y0 * M, z0 * M))


def prisma(pts, z0, z1):
    """Polígono en planta extruido entre z0 y z1."""
    vs = [V(x * M, y * M, z0 * M) for x, y in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(V(0, 0, (z1 - z0) * M))


def perfil(pts_xz, y0, y1):
    """Polígono en el plano xz extruido entre y0 e y1."""
    vs = [V(x * M, y0 * M, z * M) for x, z in pts_xz]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(V(0, (y1 - y0) * M, 0))


def agregar(grupo, nombre, forma, color, dx, transp=0):
    forma = forma.copy()
    forma.translate(V(dx * M, 0, 0))
    o = doc.addObject("Part::Feature", f"{grupo.Name}_{nombre}")
    o.Shape = forma
    if App.GuiUp:
        o.ViewObject.ShapeColor = color
        o.ViewObject.Transparency = transp
    grupo.addObject(o)


def contexto(g, alt, dx):
    """Radier del P1, losa del P2 con el hueco y barandas en su borde."""
    hx0, hy0, hx1, hy1 = alt["hueco"]
    agregar(g, "Radier", caja(hx0 - 0.4, -0.3, -0.10, 11.4, 2.4, 0), LOSA, dx)
    losa = caja(hx0 - 0.4, -0.3, D.H1, 11.4, 2.4, Z2).cut(caja(hx0, hy0, D.H1 - 0.1, hx1, hy1, Z2 + 0.1))
    if alt["tipo"] == "helicoidal":
        losa = losa.fuse(prisma(D.DESCANSO_P2, D.H1, Z2))
    agregar(g, "Losa_P2", losa, LOSA, dx, 55)
    # baranda del P2 en los bordes norte y oeste del hueco (el este es la llegada al hall)
    tipo = alt["baranda"]
    for x0, y0, x1, y1 in ((hx0, hy1 - 0.05, hx1, hy1), (hx0, hy0, hx0 + 0.05, hy1)):
        if tipo == "celosia":
            listones(g, f"Celosia_P2_{x0:.2f}_{y0:.2f}", x0, y0, x1, y1, Z2, Z2 + BARANDA, dx)
        else:
            agregar(g, f"Baranda_P2_{x0:.2f}_{y0:.2f}", caja(x0, y0, Z2, x1, y1, Z2 + BARANDA), BLANCO, dx)


def listones(g, nombre, x0, y0, x1, y1, z0, z1, dx, lado=0.045, paso=0.095):
    """Celosía de listones verticales (hueco libre 5 cm: no pasa la cabeza de la bebé ni se escala)."""
    largo = max(x1 - x0, y1 - y0)
    forma = None
    for i in range(int(largo / paso) + 1):
        t = i * paso
        if x1 - x0 >= y1 - y0:
            s = caja(x0 + t, (y0 + y1 - lado) / 2, z0, x0 + t + lado, (y0 + y1 + lado) / 2, z1)
        else:
            s = caja((x0 + x1 - lado) / 2, y0 + t, z0, (x0 + x1 + lado) / 2, y0 + t + lado, z1)
        forma = s if forma is None else forma.fuse(s)
    agregar(g, nombre, forma, LENGA, dx)


def construir(cod, alt, dx):
    g = doc.addObject("App::DocumentObjectGroup", f"Escalera_{cod}")
    g.Label = f"{cod} · {alt['nombre']}"
    contexto(g, alt, dx)
    pel = alt["peldanos"]
    tipo = alt["tipo"]
    xd = X.XE - 7 * HU
    if tipo == "helicoidal":
        import math
        forma = None
        for pts, z in pel:
            s = prisma(pts, z - 0.05, z)
            forma = s if forma is None else forma.fuse(s)
        agregar(g, "Peldanos", forma, LENGA, dx)
        cx, cy = alt["centro"]
        agregar(g, "Pilar", Part.makeCylinder(D.ESC_NUCLEO * M, (Z2 + BARANDA) * M, V(cx * M, cy * M, 0)), NEGRO, dx)
        barrotes = None
        for k, (pts, z) in enumerate(pel):
            for f in (0.25, 0.75):
                a = math.radians(-(k + f) * D.ESC_PASO)
                b = Part.makeCylinder(0.008 * M, BARANDA * M, V((cx + (D.ESC_R - 0.03) * math.cos(a)) * M,
                                                                (cy + (D.ESC_R - 0.03) * math.sin(a)) * M, z * M))
                barrotes = b if barrotes is None else barrotes.fuse(b)
        agregar(g, "Barrotes", barrotes, NEGRO, dx)
        tambor = None
        for k0, k1 in alt.get("guardado", ()):
            for k in range(k0, k1 + 1):
                s = prisma(D.sector_peldanos(k, k), 0, k * CH - 0.05)
                tambor = s if tambor is None else tambor.fuse(s)
        if tambor:
            agregar(g, "Guardado_Oculto", tambor.removeSplitter(), (0.86, 0.72, 0.55), dx)
        return g
    if tipo == "macizo":
        forma = None
        for pts, z in pel:
            s = prisma(pts, 0, z)
            forma = s if forma is None else forma.fuse(s)
        agregar(g, "Peldanos", forma.removeSplitter(), LENGA, dx)
    elif tipo == "flotante":
        for i, (pts, z) in enumerate(pel):
            e = 0.15 if i == 7 else 0.06                       # el descanso es más grueso
            agregar(g, f"Peldano_{i + 1:02d}", prisma(pts, z - e, z), LENGA, dx)
        # bajo el tramo 2 y el descanso queda cerrado: bodega + sala técnica
        prof = [(X.XE, 0), (X.XE, Z2 - 0.06)]
        for i in range(6, -1, -1):
            prof += [(xd + i * HU, (9 + i) * CH - 0.06)] + ([(xd + i * HU, (8 + i) * CH - 0.06)] if i else [])
        prof += [(xd, 8 * CH - 0.15), (xd, 0)]
        agregar(g, "Bodega_Tramo2", perfil(prof, X.CS[0], X.CS[1]), FRENTE, dx)
        agregar(g, "Bodega_Descanso", caja(7.85, X.CS[0], 0, xd, X.CN[1], 8 * CH - 0.15), FRENTE, dx)
    else:  # hormigón: tramo 1 macizo, descanso y tramo 2 en losa quebrada, huellas de lenga encima
        tapa = 0.03
        cuerpo = None
        for pts, z in pel[:7]:
            s = prisma(pts, 0, z - tapa)
            cuerpo = s if cuerpo is None else cuerpo.fuse(s)
        cuerpo = cuerpo.fuse(prisma(pel[7][0], 8 * CH - 0.20, 8 * CH - tapa))
        zu = lambda x: 8 * CH + (x - xd) * CH / HU - 0.22
        prof = [(xd, zu(xd))]
        for i in range(7):
            prof += [(xd + i * HU, (9 + i) * CH - tapa), (xd + (i + 1) * HU, (9 + i) * CH - tapa)]
        prof += [(X.XE, zu(X.XE))]
        cuerpo = cuerpo.fuse(perfil(prof, X.CS[0], X.CS[1]))
        agregar(g, "Hormigon", cuerpo.removeSplitter(), HORMIGON, dx)
        for i, (pts, z) in enumerate(pel):
            agregar(g, f"Huella_{i + 1:02d}", prisma(pts, z - tapa, z), LENGA, dx)
    # guarda central entre los carriles (y 0,95–1,00), de piso hasta la baranda del P2
    x_ini = alt["pivote"][0] if alt["pivote"] else xd
    if alt["baranda"] == "celosia":
        listones(g, "Celosia_Central", x_ini, X.CS[1], X.XE, X.CN[0], 0, Z2 + BARANDA, dx)
    else:
        agregar(g, "Guarda_Central", caja(x_ini, X.CS[1], 0, X.XE, X.CN[0], Z2 + BARANDA),
                HORMIGON if tipo == "hormigon" else BLANCO, dx)
    if alt["pivote"]:
        px, py = alt["pivote"]
        agregar(g, "Poste_Nucleo", Part.makeCylinder(0.05 * M, (Z2 + BARANDA) * M, V(px * M, py * M, 0)), LENGA, dx)
    return g


grupos = {cod: construir(cod, alt, i * SEP) for i, (cod, alt) in enumerate(X.ALTERNATIVAS.items())}
doc.recompute()
doc.saveAs(CARPETA + "/Escaleras.FCStd")



def orientacion(azimut, elevacion):
    """Cámara mirando hacia el modelo desde el azimut dado (° desde +x, antihorario) y elevación (°), con Z arriba."""
    import math
    az, el = math.radians(azimut), math.radians(elevacion)
    atras = V(math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))
    derecha = V(0, 0, 1).cross(atras).normalize()
    arriba = atras.cross(derecha)
    m = App.Matrix(derecha.x, arriba.x, atras.x, 0, derecha.y, arriba.y, atras.y, 0, derecha.z, arriba.z, atras.z, 0)
    return App.Rotation(m)


if App.GuiUp:
    import FreeCADGui as Gui
    vista = Gui.ActiveDocument.ActiveView
    for cod, g in grupos.items():
        for otro in grupos.values():
            otro.Visibility = otro is g
            for o in otro.Group:
                o.Visibility = otro is g
        vista.setCameraType("Perspective")
        # directo en el nodo de cámara: setCameraOrientation anima y la captura saldría a medio giro
        vista.getCameraNode().orientation.setValue(*orientacion(55, 30).Q)
        vista.fitAll()
        vista.saveImage(f"{CARPETA}/laminas/escalera_{cod}.png", 1400, 1000, "White")
    for g in grupos.values():
        g.Visibility = True
        for o in g.Group:
            o.Visibility = True
    vista.setCameraType("Orthographic")
    vista.viewIsometric()
    vista.fitAll()
print("OK escaleras", {c: len(g.Group) for c, g in grupos.items()})
