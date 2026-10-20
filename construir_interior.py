# Agrega los muebles de interiorismo_datos.py al documento "Casa" (grupos Interior_P1 / Interior_P2).
# Lo ejecuta construir_instalaciones.py al final; también se puede correr solo sobre un Casa.FCStd abierto.
import sys, importlib
import FreeCAD as App
import Part

CARPETA = "/Users/jai/personal/casa_freecad"
if CARPETA not in sys.path:
    sys.path.insert(0, CARPETA)
import casa_datos as D
import interiorismo_datos as N
importlib.reload(N)

M = 1000.0
doc = App.getDocument("Casa")
for nombre in ("Interior_P1", "Interior_P2"):
    if doc.getObject(nombre):
        doc.getObject(nombre).removeObjectsFromDocument()
        doc.removeObject(nombre)
grupos = {p: doc.addObject("App::DocumentObjectGroup", f"Interior_P{p}") for p in (1, 2)}
BAJO_ESCALERA = ("E1", "E2")  # quedan dentro del sólido de la escalera: sólo se dibujan en planta

cod_actual, n = "", {}
for cod, piso, (x0, y0, x1, y1), (z0, z1), mat, nombre, _ in N.MUEBLES:
    cod_actual = cod or cod_actual
    if cod_actual in BAJO_ESCALERA:
        continue
    zb = 0 if piso == 1 else D.Z2
    alto = max(z1 - z0, 0.01)
    forma = Part.makeBox((x1 - x0) * M, (y1 - y0) * M, alto * M, App.Vector(x0 * M, y0 * M, (zb + z0) * M))
    n[cod_actual] = n.get(cod_actual, 0) + 1
    o = doc.addObject("Part::Feature", f"{cod_actual}_{n[cod_actual]}")
    o.Label = f"{cod_actual} {nombre}" if nombre else f"{cod_actual} (pieza {n[cod_actual]})"
    o.Shape = forma
    if App.GuiUp:
        h = N.MATERIALES[mat][2]
        o.ViewObject.ShapeColor = tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    grupos[piso].addObject(o)
doc.recompute()
print("OK interior", sum(n.values()), "piezas")
