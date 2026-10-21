# Alternativas de escalera para el mismo hueco (lámina ESC-01, modelo Escaleras.FCStd).
# Todas respetan lo que no se mueve: llegada desde el pasillo del P1 por el vano norte (x 9,55–10,45),
# salida al hall del P2 por el vano este (y 0,13–0,98), 15 contrahuellas de Z2/15 = 18 cm, huella 25 cm
# y la sala técnica (inversor + batería) bajo el tramo alto. Cambia la forma, la estructura y lo que
# queda bajo los peldaños. Coordenadas en m, a eje de muro, como casa_datos.py.
import math

import casa_datos as D

CH, HU = D.CONTRAHUELLA, D.HUELLA
XE = 10.45                              # cara interior del muro este (arranque del tramo 1)
CN, CS = (1.00, 1.95), (0.10, 0.95)     # carriles norte (tramo 1) y sur (tramo 2)
LINEA_HUELLA = 0.48                     # línea de huella: al centro del carril, medida desde el eje central
HUECO_U = (7.85, 0.05, 10.45, 1.95)     # hueco de las escaleras en U (A, B, D)
ELEGIDA = "E"                           # la que está dibujada en el resto de las láminas (casa_datos.py)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def escalera_u():
    """U con descanso (la actual): 7 peldaños + descanso + 7 peldaños, el último a nivel del P2."""
    xd = XE - 7 * HU
    p = [(rect(XE - (i + 1) * HU, CN[0], XE - i * HU, CN[1]), (i + 1) * CH) for i in range(7)]
    p.append((rect(7.85, CS[0], xd, CN[1]), 8 * CH))
    p += [(rect(xd + i * HU, CS[0], xd + (i + 1) * HU, CS[1]), (9 + i) * CH) for i in range(7)]
    return p


def _borde_rayo(px, py, ang, caja):
    """Punto donde el rayo desde el pivote sale del rectángulo caja (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = caja
    dx, dy = math.cos(ang), math.sin(ang)
    ts = [t for t in ((x0 - px) / dx if dx < -1e-9 else None, (x1 - px) / dx if dx > 1e-9 else None,
                      (y0 - py) / dy if dy < -1e-9 else None, (y1 - py) / dy if dy > 1e-9 else None) if t]
    t = min(ts)
    return px + t * dx, py + t * dy


def escalera_compensada(n_recto=4, n_giro=6, ancho_giro=0.90):
    """U sin descanso: el giro de 180° se resuelve con peldaños compensados (abanico) desde un pivote."""
    xp = XE - n_recto * HU                 # pivote: fin de los tramos rectos, sobre el eje central
    yp = (CN[0] + CS[1]) / 2
    caja = (xp - ancho_giro, CS[0], xp, CN[1])
    esquinas = [(caja[0], caja[3]), (caja[0], caja[1])]   # NO y SO, por donde pasa el abanico
    p = [(rect(XE - (i + 1) * HU, CN[0], XE - i * HU, CN[1]), (i + 1) * CH) for i in range(n_recto)]
    paso = math.pi / n_giro
    for k in range(n_giro):
        a0, a1 = math.pi / 2 + k * paso, math.pi / 2 + (k + 1) * paso
        q0, q1 = _borde_rayo(xp, yp, a0, caja), _borde_rayo(xp, yp, a1, caja)
        medio = [c for c in esquinas if a0 < math.atan2(c[1] - yp, c[0] - xp) % (2 * math.pi) < a1]
        p.append(([(xp, yp), q0, *medio, q1], (n_recto + k + 1) * CH))
    base = n_recto + n_giro
    p += [(rect(xp + i * HU, CS[0], xp + (i + 1) * HU, CS[1]), (base + i + 1) * CH) for i in range(n_recto)]
    return p, (xp, yp), caja


_COMP, PIVOTE, CAJA_GIRO = escalera_compensada()
HUECO_COMPENSADA = (CAJA_GIRO[0], 0.05, XE, 1.95)


def huella_helicoidal():
    """(huella en la línea de huella, huella a 0,15 m del pilar) de la helicoidal de casa_datos."""
    a = math.radians(D.ESC_PASO)
    return D.ESC_LINEA * a, (D.ESC_NUCLEO + 0.15) * a


def huella_en_linea(peldanos, pivote=None, r=LINEA_HUELLA):
    """(mínima huella en la línea de huella, mínima en el borde interior a 0,15 m) de los peldaños compensados."""
    if pivote is None:
        return HU, HU
    giro = [pts for pts, _ in peldanos if pts[0] == pivote]
    if not giro:
        return HU, HU
    ang = math.pi / len(giro)
    return r * ang, 0.15 * ang


# Cada alternativa: geometría + cómo se construye + qué queda abajo + baranda + evaluación (1–3 puntos).
ALTERNATIVAS = {
    "A": {
        "nombre": "Kaidan-dansu (anterior)",
        "idea": "Escalera-mueble japonesa: peldaños macizos con cajones",
        "peldanos": escalera_u(), "hueco": HUECO_U, "pivote": None,
        "tipo": "macizo",          # cómo se modela: macizo | flotante | hormigon
        "estructura": [
            "Cajones-peldaño de lenga sobre zócalo, tramo 2",
            "en zanca de madera apoyada en bandas elastoméricas.",
            "Contrahuella cerrada; tabique guarda central.",
        ],
        "abajo": [((8.70, 1.00, 10.45, 1.95), "7 cajones (E1)"), ((7.85, 0.10, 10.45, 0.95), "Bodega + sala técnica")],
        "baranda": "muro",
        "pro": ["Máximo guardado (cajones + bodega)", "Sin huecos: segura para bebé y gatos", "Peldaños anchos: se sube con la bebé en brazos"],
        "contra": ["Caja cerrada: no pasa luz", "Madera hueca: algo de eco en los pasos"],
        "eval": {"guardado": 3, "luz": 1, "ruido": 2, "seguridad": 3, "espacio": 1},
        "costo": "base", "etapa": "Terminaciones (Etapa 6)", "planta": "No", "franja": None,
    },
    "B": {
        "nombre": "Celosía flotante (tategoshi)",
        "idea": "Peldaños en voladizo y celosía de listones hasta la baranda del P2",
        "peldanos": escalera_u(), "hueco": HUECO_U, "pivote": None,
        "tipo": "flotante",
        "estructura": [
            "Peldaños de lenga 60 mm empotrados con pletinas de",
            "acero 8 mm al muro norte reforzado (pies derechos",
            "dobles). Contrahuella abierta con hueco ≤ 10 cm.",
        ],
        "abajo": [((7.85, 0.10, 10.45, 0.95), "Bodega + sala técnica (cerrada)")],
        "baranda": "celosia",
        "pro": ["Luz del hall P2 baja al pasillo P1", "La más liviana a la vista: japandi puro",
                "La celosía no se escala (listones verticales)"],
        "contra": ["Se pierden los 7 cajones", "Peldaño volado: más resonante",
                   "Pletinas y muro reforzado en obra gruesa"],
        "eval": {"guardado": 2, "luz": 3, "ruido": 1, "seguridad": 2, "espacio": 1},
        "costo": "+20–30 %", "etapa": "Pletinas en Etapa 4, peldaños en Etapa 6", "planta": "No", "franja": None,
    },
    "C": {
        "nombre": "Compacta compensada",
        "idea": "Giro en abanico sin descanso: hueco 0,70 m más corto",
        "peldanos": _COMP, "hueco": HUECO_COMPENSADA, "pivote": PIVOTE,
        "tipo": "macizo",
        "estructura": [
            "4 peldaños + 6 compensados + 4 peldaños, macizos",
            "de lenga; poste-núcleo en el pivote y pasamanos",
            "continuo por el lado exterior (línea de huella).",
        ],
        "abajo": [((XE - 4 * HU, 1.00, XE, 1.95), "4 cajones"), ((CAJA_GIRO[0], 0.10, XE, 0.95), "Sala técnica")],
        "baranda": "muro",
        "pro": ["Lavandería P1 y baño P2 crecen 0,70 m", "Menos hueco en el entrepiso: más barata",
                "Sigue cerrada abajo"],
        "contra": ["Borde interior del abanico angosto", "Mover el tabique x 7,80 en ambos pisos",
                   "Bodega bajo la escalera se reduce"],
        "eval": {"guardado": 2, "luz": 1, "ruido": 2, "seguridad": 1, "espacio": 3},
        "costo": "−10–15 %", "etapa": "Terminaciones (Etapa 6)", "planta": "Sí: tabique 7,80 → 8,50",
        "franja": "lavand.",
    },
    "D": {
        "nombre": "Maciza acústica",
        "idea": "Hormigón revestido en lenga, desolidarizada de la casa",
        "peldanos": escalera_u(), "hueco": HUECO_U, "pivote": None,
        "tipo": "hormigon",
        "estructura": [
            "Tramo 1 macizo sobre radier engrosado; descanso y",
            "tramo 2 en losa quebrada 15 cm sobre apoyos de",
            "neopreno. Huella de lenga 30 mm sobre antiimpacto.",
        ],
        "abajo": [((7.85, 0.10, 10.45, 0.95), "Bodega + sala técnica")],
        "baranda": "muro",
        "pro": ["Casi no suena: la masa corta los golpes", "Masa térmica junto al piso radiante",
                "Dura toda la vida sin crujir"],
        "contra": ["~5 t: radier engrosado bajo el tramo 1", "Se hace en obra gruesa (moldaje)",
                   "Sin cajones bajo el tramo 1"],
        "eval": {"guardado": 2, "luz": 1, "ruido": 3, "seguridad": 3, "espacio": 1},
        "costo": "+40–60 %", "etapa": "Obra gruesa (Etapa 3–4)", "planta": "No", "franja": None,
    },
    "E": {
        "nombre": "Helicoidal Ø 1,80 (elegida)",
        "idea": "De frente desde el pasillo; guardado oculto bajo los peldaños",
        "guardado": [(3, 6), (7, 9), (10, 11)],
        "peldanos": D.ESCALONES, "hueco": D.HUECO_ESCALERA, "pivote": None, "centro": D.ESC_CENTRO,
        "tipo": "helicoidal",
        "estructura": [
            "Pilar de acero Ø 160 anclado al radier; peldaños",
            "de lenga 50 mm en ménsula. Bajo los peldaños 3–11,",
            "tambor de listones con puertas push invisibles.",
        ],
        "abajo": [((7.85, 0.05, 8.55, 1.95), "Sala técnica")],
        "baranda": "muro",
        "pro": ["Libera 0,80 m: sala técnica y ropería", "~1,8 m³ de guardado que no se ve",
                "Primer peldaño de frente al entrar"],
        "contra": ["Muebles grandes no suben: por ventana", "Peldaño angosto junto al pilar",
                   "Tambor curvo: carpintería a medida"],
        "eval": {"guardado": 3, "luz": 1, "ruido": 2, "seguridad": 2, "espacio": 3},
        "costo": "+10 a +25 %", "etapa": "Terminaciones (Etapa 6)", "planta": "Sí: tabique nuevo x 8,60",
        "franja": "sala\ntécnica",
    },
}
CRITERIOS = [("guardado", "Guardado bajo la escalera"), ("luz", "Luz natural al 1er piso"),
             ("ruido", "Silencio al subir y bajar"), ("seguridad", "Seguridad bebé y gatos"),
             ("espacio", "Espacio que libera")]

# Ancho que gana la lavandería con la compensada (el tabique sigue al nuevo borde del hueco)
GANANCIA_C = round(HUECO_COMPENSADA[0] - D.HUECO_ESCALERA[0], 2)


def peso_hormigon():
    """Peso aproximado (kN) de la alternativa D: tramo 1 macizo + descanso 20 cm + tramo 2 en losa quebrada."""
    ancho1, ancho2 = CN[1] - CN[0], CS[1] - CS[0]
    tramo1 = HU * CH * sum(range(1, 8)) * ancho1                            # perfil escalonado lleno
    descanso = (XE - 7 * HU - 7.85) * (CN[1] - CS[0]) * 0.20
    largo = math.hypot(7 * HU, 7 * CH)
    tramo2 = (largo * 0.15 + 7 * HU * CH / 2) * ancho2                       # losa + triángulos de peldaño
    return round((tramo1 + descanso + tramo2) * 24, 1)
