# Construye el modelo completo: casa 3D (construir_3d.py) + instalaciones como capas Draft
import sys, importlib
import FreeCAD as App
import Draft

CARPETA = "/Users/jai/personal/casa_freecad"
if CARPETA not in sys.path:
    sys.path.insert(0, CARPETA)
import casa_datos as D
import instalaciones_datos as I
importlib.reload(D)
importlib.reload(I)

M = 1000.0
V = App.Vector
# Siempre parte de un modelo limpio: reconstruye el 3D (que recrea el documento) y luego agrega las capas
exec(open(CARPETA + "/construir_3d.py").read())
doc = App.getDocument("Casa")
App.setActiveDocument("Casa")
CAPAS = {}


def capa(nombre, color):
    c = Draft.make_layer(nombre, line_color=color, draw_style="Solid", line_width=3)
    c.Label = nombre
    CAPAS[nombre] = c
    return c


def pt(x, y, z):
    return V(x * M, y * M, z * M)


def wire(pts, z, cap, nombre):
    w = Draft.make_wire([pt(x, y, z) for x, y in pts], closed=False, face=False)
    w.Label = nombre
    cap.Proxy.addObject(cap, w)
    return w


def circulo(x, y, z, r, cap, nombre):
    c = Draft.make_circle(r * M, placement=App.Placement(pt(x, y, z), App.Rotation()), face=False)
    c.Label = nombre
    cap.Proxy.addObject(cap, c)
    return c


def texto(x, y, z, s, cap, alto=0.12):
    t = Draft.make_text([s], placement=App.Placement(pt(x, y, z), App.Rotation()))
    if App.GuiUp:
        t.ViewObject.FontSize = alto * M
    cap.Proxy.addObject(cap, t)
    return t


for piso, z in ((1, 0.03), (2, D.Z2 + 0.03)):
    ce = capa(f"Electrico_P{piso}", (0.85, 0.55, 0.0))
    cp = capa(f"Gasfiteria_P{piso}", (0.12, 0.43, 0.82))
    luces = I.LUCES_1 if piso == 1 else I.LUCES_2
    for i, (x, y, c, tipo) in enumerate(luces):
        circulo(x, y, z, 0.18, ce, f"Luz_{c}_{i}")
        texto(x + 0.22, y + 0.15, z, c, ce)
    for i, (x, y, tipo, idx) in enumerate(I.INTERRUPTORES_1 if piso == 1 else I.INTERRUPTORES_2):
        circulo(x, y, z, 0.07, ce, f"Interruptor_{tipo}_{i}")
        for j in idx:
            wire([(x, y), luces[j][:2]], z, ce, f"Retorno_{i}_{j}")
    for i, (x, y, c, ip) in enumerate(I.ENCHUFES_1 if piso == 1 else I.ENCHUFES_2):
        circulo(x, y, z, 0.12, ce, f"Enchufe_{c}{'_IP' if ip else ''}_{i}")
    if piso == 1:
        texto(*I.TABLERO[:2], z, "TDA", ce, 0.18)
        texto(*I.MEDIDOR_ELEC[:2], z, "MED", ce, 0.18)

    redes = [("AF", I.AF_1 if piso == 1 else I.AF_2), ("AC", I.AC_1 if piso == 1 else I.AC_2),
             ("ALC", I.ALC_1 if piso == 1 else I.ALC_2)] + ([("GAS", I.GAS_1)] if piso == 1 else [])
    colores = {"AF": (0.12, 0.43, 0.82), "AC": (0.84, 0.15, 0.16), "ALC": (0.48, 0.29, 0.16), "GAS": (0.88, 0.63, 0.0)}
    for red, lineas in redes:
        for k, pts in enumerate(lineas):
            w = wire(pts, z, cp, f"{red}_{k}")
            if App.GuiUp:
                w.ViewObject.LineColor = colores[red]
                w.ViewObject.LineWidth = 4 if red == "ALC" else 3
    for cod, x, y, w_, h_ in (I.ARTEFACTOS_1 if piso == 1 else I.ARTEFACTOS_2):
        r = Draft.make_rectangle(w_ * M, h_ * M, placement=App.Placement(pt(x - w_ / 2, y - h_ / 2, z), App.Rotation()), face=False)
        r.Label = f"Artefacto_{cod}"
        cp.Proxy.addObject(cp, r)
        texto(x - 0.1, y, z, cod, cp, 0.10)

# Montantes verticales de agua y bajada de alcantarillado entre pisos
cp1 = CAPAS["Gasfiteria_P1"]
for x, y, t in I.SUBIDAS:
    w = wire([(x, y), (x, y)], 0.03, cp1, f"Montante_{t}")
    w.Points = [pt(x, y, 0.03), pt(x, y, D.Z2 + 0.03)]
xb, yb, _ = I.BAJADA
w = wire([(xb, yb), (xb, yb)], 0.03, cp1, "Bajada_BAS")
w.Points = [pt(xb, yb, -0.4), pt(xb, yb, D.Z2 + D.H2 + 0.5)]

# Las capas Draft sobrescriben color de línea; dejar colores por objeto
for o in doc.Objects:
    if App.GuiUp and o.TypeId == "App::FeaturePython" and hasattr(o, "Group") and o.Label.startswith(("Electrico", "Gasfiteria")):
        o.ViewObject.OverrideLineColorChildren = False

doc.recompute()
doc.save()
print("OK instalaciones", len(doc.Objects), "objetos")
