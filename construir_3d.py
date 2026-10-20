# Construye el modelo 3D de la casa en FreeCAD a partir de casa_datos.py
import sys, importlib, math
import FreeCAD as App
import Part

CARPETA = "/Users/jai/personal/casa_freecad"
if CARPETA not in sys.path:
    sys.path.insert(0, CARPETA)
import casa_datos as D
importlib.reload(D)

M = 1000.0  # metros -> mm
V = App.Vector

NOMBRE = "Casa"
if NOMBRE in App.listDocuments():
    App.closeDocument(NOMBRE)
doc = App.newDocument(NOMBRE)


def caja(x0, y0, z0, x1, y1, z1):
    return Part.makeBox((x1 - x0) * M, (y1 - y0) * M, (z1 - z0) * M, V(x0 * M, y0 * M, z0 * M))


def muro(x1, y1, x2, y2, t, z0, h):
    e = t / 2
    if y1 == y2:  # horizontal
        return caja(min(x1, x2) - e, y1 - e, z0, max(x1, x2) + e, y1 + e, z0 + h)
    return caja(x1 - e, min(y1, y2) - e, z0, x1 + e, max(y1, y2) + e, z0 + h)


def vano(x, y, w, o, z0, h):
    p = 0.30  # profundidad del corte, mayor que cualquier muro
    if o == 'h':
        return caja(x - w / 2, y - p / 2, z0, x + w / 2, y + p / 2, z0 + h)
    return caja(x - p / 2, y - w / 2, z0, x + p / 2, y + w / 2, z0 + h)


def agregar(nombre, forma, color, grupo, transp=0):
    o = doc.addObject("Part::Feature", nombre)
    o.Shape = forma
    if App.GuiUp:
        o.ViewObject.ShapeColor = color
        o.ViewObject.Transparency = transp
    grupo.addObject(o)
    return o


def piso(n, muros, puertas, ventanas, z0, h):
    g = doc.addObject("App::DocumentObjectGroup", f"Piso{n}")
    solido = muro(*muros[0], z0, h)
    for m in muros[1:]:
        solido = solido.fuse(muro(*m, z0, h))
    cortes = [vano(x, y, w, o, z0 - 0.01, 2.05) for x, y, w, o, *_ in puertas]
    cortes += [vano(x, y, w, o, z0 + s, hv) for x, y, w, o, s, hv in ventanas]
    for c in cortes:
        solido = solido.cut(c)
    solido = solido.removeSplitter()
    agregar(f"Muros_P{n}", solido, (0.93, 0.92, 0.88), g)
    vidrios = [vano(x, y, w, o, z0 + s, hv) for x, y, w, o, s, hv in ventanas]
    for i, (x, y, w, o, s, hv) in enumerate(ventanas):
        t = 0.02
        b = caja(x - w / 2, y - t, z0 + s, x + w / 2, y + t, z0 + s + hv) if o == 'h' else \
            caja(x - t, y - w / 2, z0 + s, x + t, y + w / 2, z0 + s + hv)
        agregar(f"Vidrio_P{n}_{i+1}", b, (0.55, 0.78, 0.95), g, 60)
    return g


# --- Piso 1 ---
g1 = piso(1, D.MUROS_1, D.PUERTAS_1, D.VENTANAS_1, 0, D.H1)
losa1 = caja(*D.LOSA_1[0][:2], -0.10, *D.LOSA_1[0][2:], 0)
for r in D.LOSA_1[1:]:
    losa1 = losa1.fuse(caja(r[0], r[1], -0.10, r[2], r[3], 0))
agregar("Radier_P1", losa1.removeSplitter(), (0.75, 0.72, 0.68), g1)
for i, r in enumerate(D.TERRAZAS):
    agregar(f"Terraza_{i+1}", caja(r[0], r[1], -0.12, r[2], r[3], -0.02), (0.60, 0.45, 0.20), g1)

# Escalera en U (geometría en casa_datos.ESCALONES)
g_esc = doc.addObject("App::DocumentObjectGroup", "Escalera")
pasos = None
for x0, y0, x1, y1, z in D.ESCALONES:
    s = caja(x0, y0, 0, x1, y1, z)
    pasos = s if pasos is None else pasos.fuse(s)
agregar("Escalera_U", pasos.removeSplitter(), (0.55, 0.40, 0.28), g_esc)

# --- Piso 2 ---
g2 = piso(2, D.MUROS_2, D.PUERTAS_2, D.VENTANAS_2, D.Z2, D.H2)
x0, y0, x1, y1 = D.LOSA_2
losa2 = caja(x0, y0, D.H1, x1, y1, D.Z2).cut(caja(*D.HUECO_ESCALERA[:2], D.H1 - 0.1, *D.HUECO_ESCALERA[2:], D.Z2 + 0.1))
agregar("Losa_P2", losa2, (0.75, 0.72, 0.68), g2)
agregar("Techo_Living", caja(*D.TECHO_1[:2], D.H1, *D.TECHO_1[2:], D.Z2), (0.75, 0.72, 0.68), g1)

# --- Techumbre, paneles FV y elementos exteriores (especialidades_datos.py) ---
import especialidades_datos as E
importlib.reload(E)


def prisma(pts, eje, desde, hasta):
    """Extruye un polígono definido en el plano perpendicular a 'eje' ('x' o 'y')."""
    if eje == "x":
        vs = [V(desde * M, a * M, b * M) for a, b in pts]
        d = V((hasta - desde) * M, 0, 0)
    else:
        vs = [V(a * M, desde * M, b * M) for a, b in pts]
        d = V(0, (hasta - desde) * M, 0)
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(d)


g_t = doc.addObject("App::DocumentObjectGroup", "Techumbre")
e_t = 0.22
zb, zc, yc = E.Z_BORDE_ALERO, E.Z_CUMBRERA, E.CUMBRERA_Y
ty0, ty1 = E.TECHO_Y
tx0, tx1 = E.TECHO_X
for nombre, ya in (("Faldon_Sur", ty0), ("Faldon_Norte", ty1)):
    f = prisma([(ya, zb), (yc, zc), (yc, zc + e_t), (ya, zb + e_t)], "x", tx0, tx1)
    agregar(nombre, f, (0.62, 0.60, 0.57), g_t)
z_muro = D.Z2 + D.H2
for xf in (2, 12):
    fr = prisma([(0, z_muro), (6, z_muro), (yc, z_muro + yc * E.TAN)], "x", xf - D.EXT / 2, xf + D.EXT / 2)
    agregar(f"Fronton_x{xf}", fr, (0.93, 0.92, 0.88), g_t)
tb = E.TECHO_BAJO
agregar("Techo_Bajo", prisma([(tb["x"][0], tb["z_bajo"]), (tb["x"][1], tb["z_alto"]), (tb["x"][1], tb["z_alto"] + 0.18),
                              (tb["x"][0], tb["z_bajo"] + 0.18)], "y", tb["y"][0], tb["y"][1]), (0.62, 0.60, 0.57), g_t)

g_fv = doc.addObject("App::DocumentObjectGroup", "Paneles_FV")
sn, cs = math.sin(math.radians(E.PENDIENTE)), math.cos(math.radians(E.PENDIENTE))
for i, (x0, x1, s0, s1, etapa) in enumerate(E.PANELES):
    z_off = zc + e_t + 0.08
    pts = [(yc + s0 * cs, z_off - s0 * sn), (yc + s1 * cs, z_off - s1 * sn),
           (yc + s1 * cs, z_off - s1 * sn + 0.04), (yc + s0 * cs, z_off - s0 * sn + 0.04)]
    agregar(f"Panel_E{etapa}_{i + 1:02d}", prisma(pts, "x", x0, x1),
            (0.10, 0.20, 0.45) if etapa == 1 else (0.55, 0.65, 0.85), g_fv, 0 if etapa == 1 else 50)

g_ext = doc.addObject("App::DocumentObjectGroup", "Exteriores")
for i, (cx, cy, tc) in enumerate(D.COLUMNAS_1):
    agregar(f"Pilar_{i + 1}", caja(cx - tc / 2, cy - tc / 2, 0, cx + tc / 2, cy + tc / 2, D.H1), (0.7, 0.7, 0.7), g_ext)
agregar("Bomba_Calor", caja(6.45, -0.75, 0.15, 7.45, -0.35, 0.95), (0.56, 0.27, 0.68), g_ext)  # unidad exterior, muro sur
agregar("Acumulador_ACS_300L", Part.makeCylinder(0.30 * M, 1.75 * M, V(7.45 * M, 0.40 * M, 0)), (0.85, 0.40, 0.40), g_ext)
cx0, cy0, cx1, cy1 = E.CASETA_AGUA
agregar("Caseta_Presurizacion", caja(cx0, cy0, -0.3, cx1, cy1, 2.0), (0.75, 0.82, 0.92), g_ext)
agregar("Cargador_EV", caja(E.WALLBOX[0] - 0.12, E.WALLBOX[1] - 0.12, -0.3, E.WALLBOX[0] + 0.12, E.WALLBOX[1] + 0.12, 1.3),
        (0.0, 0.33, 0.67), g_ext)
est = Part.makeCylinder(1.1 * M, 1.8 * M, V(E.ESTANQUE["x"] * M, E.ESTANQUE["y"] * M, -0.3 * M))
agregar("Estanque_Lluvias", est, (0.30, 0.55, 0.75), g_ext)

agregar("Inversor_Hibrido", caja(E.INVERSOR[0] - 0.25, 0.10, 0.9, E.INVERSOR[0] + 0.25, 0.30, 1.5), (0.85, 0.88, 0.95), g_ext)
agregar("Bateria_11kWh", caja(E.BATERIA["x"] - 0.30, 0.10, 0.0, E.BATERIA["x"] + 0.30, 0.35, 1.0), (0.12, 0.30, 0.61), g_ext)

# --- Terreno (DEM aproximado, sitio/topografia.json) con plataforma nivelada a -0,30 ---
import Mesh
g_topo = doc.addObject("App::DocumentObjectGroup", "Terreno")
T = E.TOPO["lote"]
px0, py0, px1, py1 = (-1.5, -1.5, 13.5, 7.5)
z_plat = E.TOPO["cota_plataforma"] - E.NPT_MSNM


def zt(i, j):
    x, y = T["x"][0] + j * T["paso"], T["y"][0] + i * T["paso"]
    if px0 <= x <= px1 and py0 <= y <= py1:
        return z_plat
    return T["z"][i][j] - E.NPT_MSNM


tris = []
for i in range(len(T["z"]) - 1):
    for j in range(len(T["z"][0]) - 1):
        p = [V((T["x"][0] + (j + dj) * T["paso"]) * M, (T["y"][0] + (i + di) * T["paso"]) * M, zt(i + di, j + dj) * M)
             for di, dj in ((0, 0), (0, 1), (1, 1), (1, 0))]
        tris += [p[0], p[1], p[2], p[0], p[2], p[3]]
terreno = doc.addObject("Mesh::Feature", "Terreno_DEM")
terreno.Mesh = Mesh.Mesh(tris)
g_topo.addObject(terreno)
if App.GuiUp:
    terreno.ViewObject.ShapeColor = (0.55, 0.62, 0.40)
    terreno.ViewObject.Transparency = 20
# el radier queda 0,30 m sobre la plataforma (NPT = plataforma + 0,30)

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
doc.saveAs(CARPETA + "/Casa.FCStd")
print("OK", len(doc.Objects), "objetos")
