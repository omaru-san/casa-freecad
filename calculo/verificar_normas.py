#!/usr/bin/env python3
"""Verifica automáticamente el anteproyecto contra la normativa chilena (OGUC, DS 15, RIC SEC, RIDAA, DS 236, CONAF).
Lee casa_datos.py, instalaciones_datos.py y especialidades_datos.py; escribe calculo/verificacion.json y
CUMPLIMIENTO_NORMATIVO.md.  Uso: python3 -I calculo/verificar_normas.py   (desde la carpeta del proyecto)
"""
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
import casa_datos as D  # noqa: E402
import especialidades_datos as E  # noqa: E402
import instalaciones_datos as I  # noqa: E402

FV = json.load(open(os.path.join(AQUI, "fv_bateria.json"), encoding="utf-8"))
RES = []


def check(tema, exigencia, valor, cumple, fuente, tipo="calculado"):
    RES.append({"tema": tema, "exigencia": exigencia, "valor": valor,
                "estado": "CUMPLE" if cumple is True else ("NO CUMPLE" if cumple is False else cumple),
                "fuente": fuente, "tipo": tipo})


def num(v, d=2):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dentro(x, y, r, tol=0.0):
    _, x0, y0, x1, y1 = r
    return x0 - tol <= x <= x1 + tol and y0 - tol <= y <= y1 + tol


def recintos(piso):
    return D.RECINTOS_1 if piso == 1 else D.RECINTOS_2


def area(r):
    return (r[3] - r[1]) * (r[4] - r[2])


def perimetro(r):
    return 2 * ((r[3] - r[1]) + (r[4] - r[2]))


HABITABLES = ("LIVING", "OFICINA", "DORMITORIO")

# ---------------- arquitectura (OGUC) ----------------
for piso, h in ((1, D.H1), (2, D.H2)):
    check("Arquitectura", f"Altura piso-cielo ≥ 2,30 m (piso {piso})", f"{num(h)} m", h >= 2.30, "OGUC 4.1.1")
sup = sum(area(r) for r in D.RECINTOS_1 if r[0] not in D.EXTERIORES) + sum(area(r) for r in D.RECINTOS_2)
check("Fuego / subsidio", "Superficie edificada ≤ 140 m² y ≤ 2 pisos → F-15 en soportantes; tope DS1",
      f"{num(sup, 1)} m²", sup <= 140, "OGUC 4.3.5 n°14 · DS1 MINVU")
for piso in (1, 2):
    vents = D.VENTANAS_1 if piso == 1 else D.VENTANAS_2
    for r in recintos(piso):
        if not r[0].startswith(HABITABLES):
            continue
        tiene = any(dentro(x, y, r, 0.15) for x, y, *_ in vents)
        check("Arquitectura", f"Ventana al exterior en local habitable: {r[0].title()}", "sí" if tiene else "no",
              tiene, "OGUC 4.1.2")
ante = min(s for x, y, w, o, s, h in D.VENTANAS_2 if h >= 1.0)
check("Seguridad niños", "Antepecho ventanas P2 ≥ 0,95 m (art. 4.2.7 no rige en vivienda unifamiliar; se aplica igual)",
      f"{num(ante)} m", ante >= 0.95, "OGUC 4.2.7 (recomendación)", "criterio")
regla = 2 * D.CONTRAHUELLA + D.HUELLA
check("Arquitectura", "Escalera cómoda: 0,60 ≤ 2·ch + h ≤ 0,65 m, ch ≤ 0,18 m", f"ch {num(D.CONTRAHUELLA, 3)} · 2ch+h {num(regla, 3)}",
      0.60 <= regla <= 0.65 and D.CONTRAHUELLA <= 0.18 + 1e-6, "Buena práctica (OGUC 4.2.11 sólo rige en evacuación)", "criterio")

# ---------------- envolvente (DS 15) ----------------
umax = {"Techumbre": 0.28, "Muros": 0.40, "Piso ventilado": 0.39, "Puerta acceso": 1.70}
for el, sol, u, _ in E.ENVOLVENTE["tabla"]:
    if el in umax:
        check("Térmica zona G", f"U {el.lower()} ≤ {num(umax[el])} W/m²K", f"{num(u)}", u <= umax[el] + 1e-9, "OGUC 4.1.10 (DS 15)")
lim = {"N": 76, "S": 26, "EO": 40}
for o, m in lim.items():
    pct = E._porcentaje_ventana(o)[0]
    check("Térmica zona G", f"Ventanas {o} ≤ {m} % del muro (U ventana ≤ 1,6)", f"{pct:.0f} %", pct <= m, "DS 15, Tabla 3")
check("Térmica zona G", "Hermeticidad ≤ 5,0 ren/h a 50 Pa (prov. Valdivia)", f"meta {num(E.N50_META, 1)} (blower door)",
      E.N50_META <= 5.0, "DS 15 · Actualización RT DITEC", "a verificar en obra")

# ---------------- ventilación ----------------
imp = sum(r[4] for r in E.REJILLAS if r[1] == "IM")
ext = sum(r[4] for r in E.REJILLAS if r[1] == "EX")
q_min = 0.15 * sup + 3.5 * (3 + 1)
check("Ventilación", f"Caudal NCh 3309 ≥ 0,15·A + 3,5·(dorm+1) = {num(q_min, 1)} L/s", f"impulsión {imp} / extracción {ext} L/s",
      imp >= q_min and abs(imp - ext) <= 2, "DS 15 → NCh 3309 (vía ECSV Tomo I)")
for nombre in ("Baño P1", "Baño P2", "Cocina"):
    q = sum(r[4] for r in E.REJILLAS if r[5] == nombre and r[1] == "EX")
    check("Ventilación", f"Extracción continua {nombre} ≥ 10 L/s", f"{q} L/s", q >= 10, "ECSV Tomo I / OGUC 4.1.3")

# ---------------- eléctrico (RIC SEC) ----------------
for piso in (1, 2):
    luces = I.LUCES_1 if piso == 1 else I.LUCES_2
    inter = I.INTERRUPTORES_1 if piso == 1 else I.INTERRUPTORES_2
    ench = I.ENCHUFES_1 if piso == 1 else I.ENCHUFES_2
    for r in recintos(piso):
        if not r[0] or r[0] in D.EXTERIORES or r[0] in ("ESCALERA", "PASILLO", "DESPENSA", "LAVANDERÍA", "WALK-IN CLOSET"):
            continue
        n_luz = sum(1 for x, y, *_ in luces if dentro(x, y, r))
        req = 2 if area(r) > 10 else 1
        check("Eléctrico", f"Centros de luz {r[0].title()} P{piso} ({num(area(r), 1)} m²) ≥ {req}", str(n_luz), n_luz >= req,
              "RIC 10 5.2 a)")
        if r[0].startswith(HABITABLES) or r[0].startswith("LIVING"):
            n_e = sum(1 for x, y, c, ip in ench if dentro(x, y, r, 0.15) and not ip and c not in ("C4", "C9", "C10"))
            req_e = math.ceil(perimetro(r) / 8)
            check("Eléctrico", f"Enchufes {r[0].title()} P{piso}: 1 por cada 8 m de perímetro → ≥ {req_e}", str(n_e), n_e >= req_e,
                  "RIC 10 5.2 b)")
    efectos = {"simple": 1, "conmutador": 1, "doble": 2}
    controladas = [i for _, _, t, idx in inter for i in idx]
    ok_ind = all(len(idx) <= efectos[t] for _, _, t, idx in inter) and len(set(controladas)) == len(luces)
    check("Eléctrico", f"Cada centro con interruptor independiente (P{piso})", f"{len(luces)} centros, {len(inter)} mandos", ok_ind,
          "RIC 10 5.2 a)")
n_coc = sum(1 for x, y, c, ip in I.ENCHUFES_1 if c == "C4" and 4.8 <= x <= 8.0 and y >= 3.5)
check("Eléctrico", "Cocina ≥ 3 enchufes dobles + circuito exclusivo 16 A + circuitos de inducción y horno",
      f"{n_coc} en C4 + C9 + C10", n_coc >= 3, "RIC 10 5.2 d), e)")
dif = {}
for c in I.CIRCUITOS:
    if "ID" in c[4]:
        k = c[4].split("ID")[1].split()[0]
        dif.setdefault(k, []).append(c[0])
peor = max(len(v) for v in dif.values())
check("Eléctrico", "Diferencial ≤ 30 mA en todo circuito de alumbrado/enchufes y ≤ 3 circuitos por diferencial",
      f"{len(dif)} diferenciales, máx. {peor} circuitos", peor <= 3, "RIC 10 5.1.3.5 y 5.1.3.7")
duchas = [(1, a) for a in I.ARTEFACTOS_1 if a[0] == "DU"] + [(2, a) for a in I.ARTEFACTOS_2 if a[0] == "DU"]
for piso, (_, cx, cy, w, h) in duchas:
    ench = I.ENCHUFES_1 if piso == 1 else I.ENCHUFES_2
    banos = [r for r in recintos(piso) if r[0] == "BAÑO"]
    dmin = 99
    for x, y, *_ in ench:
        if any(dentro(x, y, b, 0.15) for b in banos):
            dx = max(abs(x - cx) - w / 2, 0)
            dy = max(abs(y - cy) - h / 2, 0)
            dmin = min(dmin, math.hypot(dx, dy))
    check("Eléctrico", f"Enchufes del baño P{piso} fuera de volúmenes 0-1-2 (≥ 0,60 m de la ducha)", f"{num(dmin)} m",
          dmin >= 0.60, "RIC 11 sección 6")
tx, ty = I.TABLERO[:2]
en = [r[0] for r in D.RECINTOS_1 if dentro(tx, ty, r)]
check("Eléctrico", "Tablero fuera de dormitorios, baños, lavaderos y closets", en[0] if en else "—",
      not any(k in (en[0] if en else "") for k in ("DORM", "BAÑO", "LAVAND", "CLOSET")), "RIC 10 5.1.3.2")
check("Eléctrico", "Enchufes de alvéolos protegidos; cargador EV con circuito exclusivo y diferencial tipo B", "especificado",
      True, "RIC 10 5.1.2.8 · RIC 15", "especificado")
check("Solar", "Inversor con detección de arco (AFCI); diferencial 100 mA (5–10 kW)", f"inversor {num(FV['sistema']['inversor_kw'], 0)} kW",
      FV["sistema"]["inversor_kw"] <= 10, "Res. SEC 33.038 · RGR 02", "especificado")

potf = {"R": 0.0, "S": 0.0, "T": 0.0}
for c in I.CIRCUITOS:
    if c[0] in I.POTENCIA and c[0] != "EV":
        w, fd = I.POTENCIA[c[0]]
        potf[c[4][0]] += w * fd
desb = 100 * (max(potf.values()) - min(potf.values())) / (sum(potf.values()) / 3)
check("Eléctrico", "Fases equilibradas: desbalance de demanda ≤ 10 %", f"R {num(potf['R'], 0)} · S {num(potf['S'], 0)} · "
      f"T {num(potf['T'], 0)} W ({num(desb, 1)} %)", desb <= 10, "Buena práctica (RIC 10)", "criterio")
i_max = max(potf.values()) / 230
check("Eléctrico", f"Demanda por fase ≤ empalme {I.EMPALME_A} A (EV con gestión dinámica)", f"{num(i_max, 1)} A",
      i_max <= I.EMPALME_A, "RIC 10 / cuadro de cargas TAB-01")
check("Eléctrico", "Subtablero de respaldo (TDA-R) desde la salida backup del inversor; DPS tipo 1+2 por línea aérea rural",
      f"TDA-R: {', '.join(I.RESPALDO)}", True, "RIC 10 · RGR 02 · IEC 61643", "especificado")

# ---------------- estructura y acústica ----------------
EST = json.load(open(os.path.join(AQUI, "estructura.json"), encoding="utf-8"))
vg = next(e for e in EST["elementos"] if e["elemento"].startswith("Viga entrepiso (living"))
check("Estructura", "Flecha viga de entrepiso ≤ L/360 (piso de porcelanato sobre madera)",
      f"{num(vg['flecha_mm'], 1)} mm ≤ {num(vg['L_m'] * 1000 / 360, 1)} mm", vg["flecha_mm"] <= vg["L_m"] * 1000 / 360,
      "Fabricantes de adhesivos (ANSI A108 / TCNA)", "criterio")
capas = " ".join(c[0] for c in D.ENTREPISO).lower()
check("Acústica", "Entrepiso con piso flotante sobre lámina antiimpacto y cielo desacoplado (meta L'nT,w ≤ 55 dB)",
      f"{int(round(D.LOSA * 100))} cm · {num(sum(c[2] for c in D.ENTREPISO))} kN/m²",
      "a verificar en obra" if ("antiimpacto" in capas and "resiliente" in capas) else False,
      "Criterio (OGUC 4.1.6 rige sólo entre unidades distintas)", "criterio")

# ---------------- sanitario ----------------
check("Sanitario", "Pendiente de descargas 3 %–15 % (1 % sólo justificado)", "3 % (rótulo y notas)", True, "RIDAA art. 88", "especificado")
d_pozo = min(math.dist(E.POZO, p) for dr in E.DRENES for p in dr)
d_fosa = min(math.dist(E.POZO, (x, y)) for x in E.FOSA["x"] for y in E.FOSA["y"])
check("Sanitario", "Drenes y fosa a ≥ 20 m del pozo", f"drenes {num(d_pozo, 1)} m · fosa {num(d_fosa, 1)} m",
      min(d_pozo, d_fosa) >= 20, "DS 236")
vol = 5 * 150 * 1.0 + 5 * 40 * 2 * 1.0
check("Sanitario", f"Fosa ≥ 24 h de retención + lodos 2 años (5 pers. ≈ {num(vol / 1000, 1)} m³)", f"{num(E.FOSA['litros'] / 1000, 1)} m³",
      E.FOSA["litros"] >= vol, "DS 236")
check("Sanitario", "Presión ≥ 14 m.c.a. tras la llave de paso; bomba aspira de estanque; partida-detención ≤ 12 m.c.a.",
      "presurizadora VSD 30–42 m.c.a. desde estanque 3.000 L", True, "RIDAA art. 52 f) y bombeo k)", "especificado")
check("Sanitario", "Agua caliente sin gas: acumulación ≥ 60 °C semanal (Legionella) y salida ≤ 48 °C (niños)",
      "acumulador 300 L + VMT 45 °C", True, "Guías Legionella (Sanidad ES / Gob. Vasco)", "especificado")

def cerca_muro(x, y, tol=0.5):
    for x1, y1, x2, y2, _ in D.MUROS_1:
        dx, dy = x2 - x1, y2 - y1
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        if math.hypot(x - x1 - t * dx, y - y1 - t * dy) <= tol:
            return True
    return False


def en_planta(x, y):
    return any(r[1] < x < r[3] and r[2] < y < r[4] for r in D.RECINTOS_1 if r[0] not in D.EXTERIORES)


malos_af = 0
for pts in I.AF_1 + I.AC_1:
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n_ = max(1, int(math.dist((xa, ya), (xb, yb)) / 0.1))
        for k in range(n_ + 1):
            x, y = xa + (xb - xa) * k / n_, ya + (yb - ya) * k / n_
            if en_planta(x, y) and not cerca_muro(x, y):
                malos_af += 1
check("Sanitario", "Agua fría/caliente fuera del radier (piso radiante): por muros o entrepiso, nunca embutida en el piso",
      f"{len(I.AF_1_ENTREPISO + I.AC_1_ENTREPISO)} tramos por entrepiso · {malos_af} puntos fuera de muro",
      malos_af == 0, "Criterio de mantención (RIDAA art. 52: cañerías accesibles)", "criterio")
check("Sanitario", "Cámara desgrasadora en la descarga de la cocina, antes de la fosa", 
      "C.D." if any(n == "C.D." for *_, n in I.CAMARAS) else "no", any(n == "C.D." for *_, n in I.CAMARAS),
      "DS 236 · Manual SUBDERE (soluciones particulares)")

# ---------------- calefacción ----------------
import generar_especialidades as G  # noqa: E402
_, _, pot, demanda, area_rad = G.balance_termico()
p1, p2 = G.reparto_pisos(pot)
q_m2 = p1 * 1000 / area_rad
t_sup = 20 + (q_m2 / 8.92) ** (1 / 1.1)
check("Calefacción", "Temperatura superficial de piso radiante (P1) ≤ 29 °C en zonas de estar", f"{num(t_sup, 1)} °C ({num(q_m2, 0)} W/m²)",
      t_sup <= 29, "UNE-EN 1264 (referencia)")
fc = G.carga_fancoils(pot)
check("Calefacción", "P2 sin piso radiante: cada dormitorio con ventiloconvector ≥ su carga (equipo mín. 800 W a 35 °C)",
      " · ".join(f"{r} {num(w, 0)} W" for r, w in fc), all(w <= 800 for _, w in fc) and len(fc) == 3,
      "Balance térmico VEN-01", "calculado")
check("Calefacción", "Sin artefactos de combustión ni chimeneas (riesgo CO e incendio)", "bomba de calor + inducción", True,
      "Criterio de diseño (DS 66 no aplica: sin gas)", "especificado")

# ---------------- incendio forestal ----------------
check("Fuego", "Faja de defensa 0–2–10–30 m, techo metálico, aleros cerrados con malla", "dibujada en EMP-01", True,
      "CONAF Comunidades Preparadas · MINVU Chile se Prepara", "especificado")
check("Fuego", "Detectores de humo interconectados en dormitorios y circulaciones",
      f"{sum(1 for d in I.DETECTORES if d[3] == 'humo')} DH + {sum(1 for d in I.DETECTORES if d[3] == 'temp')} DT", True,
      "Buena práctica (proyecto de ley en trámite)", "especificado")

# ---------------- exterior ----------------
bx0, by0, bx1, by1 = E.BODEGA["rect"]
d_bod = math.hypot(max(0, bx0 - 12, 0 - bx1), max(0, by0 - 6, 0 - by1))   # rectángulo bodega ↔ planta 12 × 6 m
check("Fuego", "Bodega exterior no combustible a ≥ 10 m de la casa", f"{num(d_bod, 1)} m", d_bod >= 10,
      "CONAF Comunidades Preparadas", "calculado")


def dentro_poligono(x, y, pts):
    ins = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            ins = not ins
    return ins


patio = E.CERCO_PATIO + [(12.0, 0.0)]   # se cierra por la casa
fuera = {"fosa": (sum(E.FOSA["x"]) / 2, sum(E.FOSA["y"]) / 2),
         "estacionamiento": ((E.ESTACIONAMIENTO[0] + E.ESTACIONAMIENTO[2]) / 2, (E.ESTACIONAMIENTO[1] + E.ESTACIONAMIENTO[3]) / 2),
         "caseta": ((E.CASETA_AGUA[0] + E.CASETA_AGUA[2]) / 2, (E.CASETA_AGUA[1] + E.CASETA_AGUA[3]) / 2)}
dentro_ = [k for k, p in fuera.items() if dentro_poligono(*p, patio)]
check("Exterior", "Patio cercado del perro deja fuera fosa (camión), estacionamiento y caseta de agua",
      "ok" if not dentro_ else "dentro: " + ", ".join(dentro_), not dentro_, "Criterio de diseño (EXT-01)", "criterio")

with open(os.path.join(AQUI, "verificacion.json"), "w", encoding="utf-8") as f:
    json.dump(RES, f, ensure_ascii=False, indent=1)

malos = [r for r in RES if r["estado"] == "NO CUMPLE"]
md = ["# Cumplimiento normativo — anteproyecto Casa Puringue Pobre",
      "",
      "> Generado por `python3 -I calculo/verificar_normas.py` a partir de los archivos de datos. "
      "Se vuelve a generar después de cada cambio de diseño.",
      "> **Fundaciones fuera de alcance** (las proyecta un tercero; la lámina 08 entrega las cargas).",
      "",
      f"**Resultado:** {len(RES) - len(malos)} de {len(RES)} verificaciones cumplen"
      + (f"; **{len(malos)} no cumplen**." if malos else ".") ,
      "",
      "Estados:",
      "- **CUMPLE:** calculado por el script o especificado en los planos.",
      "- **a verificar en obra:** requiere una prueba física.",
      "- Tipo **criterio:** buena práctica más exigente que la norma.",
      "",
      "| Tema | Exigencia | Proyecto | Estado | Fuente |",
      "|---|---|---|---|---|"]
for r in RES:
    est = f"**{r['estado']}**" if r["estado"] != "CUMPLE" else "CUMPLE"
    md.append(f"| {r['tema']} | {r['exigencia']} | {r['valor']} | {est} | {r['fuente']} |")
md += ["",
       "## Cambios hechos al diseño para cumplir (20-10-2026)",
       "",
       "### Casa todo eléctrica",
       "- Se eliminaron el gas, el calefont y la estufa a pellet.",
       "- **Calefacción:** bomba de calor aire-agua (~6 kW): piso radiante en el 1er piso y ventiloconvectores",
       "  (fancoils) a la misma temperatura en los dormitorios del 2° piso; toallero eléctrico en el baño P2.",
       "- **Agua caliente:** acumulador de 300 L con válvula mezcladora termostática a 45 °C.",
       "- **Cocina:** encimera de inducción.",
       "- **Resultado:** sin CO ni chimeneas, sin trámite TC6.",
       "",
       "### Ventilación",
       "- VMC de doble flujo con recuperador de calor 80 %, 35 L/s (NCh 3309).",
       "- Reemplaza los extractores, las rejillas de gas y la microventilación.",
       "",
       "### Electricidad",
       "- **Circuitos:** de 9 a 17, con circuitos exclusivos para:",
       "  - cocina;",
       "  - inducción;",
       "  - horno;",
       "  - bomba de calor;",
       "  - apoyo de agua caliente y circuladores de calefacción;",
       "  - ventilación con domótica;",
       "  - cargador EV de 11 kW;",
       "  - ventiloconvectores del 2° piso (C14) y exterior: luces, bodega y portón (C15).",
       "- **Tableros:** TDA general + TDA-R de respaldo (salida backup del inversor: luces, refrigerador,",
       "  bombas de agua, VMC y red siguen con corte de luz). Unilineal y cuadro de cargas en TAB-01.",
       "- **Diferenciales:** 30 mA, con un máximo de 3 circuitos cada uno.",
       "- **Iluminación:**",
       "  - 2° centro de luz en el dormitorio principal (> 10 m²);",
       "  - un interruptor independiente por centro.",
       "- **Enchufes de baño fuera de la zona de ducha:**",
       "  - en el P2 estaba dentro de la ducha;",
       "  - en el P1 estaba a 0,5 m.",
       "- **Detectores:** de humo interconectados, y térmico en la cocina.",
       "- **Empalme:** trifásico, con DPS tipo 1+2 (línea aérea rural) y fases equilibradas.",
       "",
       "### Sanitario",
       "- **Pendiente de alcantarillado:** 3 % (antes 1 %).",
       "- **Agua del pozo:** pasa por un estanque de 3.000 L y una presurizadora de velocidad variable en una caseta (RIDAA: la bomba aspira de un estanque).",
       "- **Llaves de paso:** en cada recinto húmedo.",
       "- **Agua fría/caliente fuera del radier:** por la cámara técnica de los muros y el entrepiso.",
       "- **Cámara desgrasadora** en la salida de la cocina; tratamiento del pozo con filtro Fe/Mn si el análisis lo pide.",
       "",
       "### Seguridad",
       "- **Ventanas del P2:** antepecho de 1,00 m y limitador de apertura.",
       "- **Escalera:** baranda de 0,95 / 0,85 m y puertas de seguridad.",
       "- **Faja CONAF:** de 2/10/30 m alrededor de la casa.",
       "- **Cargador EV:** estacionamiento para 2 autos con el cargador.",
       "",
       "### Estructura",
       "- Se quitó el diseño de fundaciones.",
       "- Ahora se entregan las cargas a la fundación (D, L, pilar, hold-down y corte basal) para quien las proyecte.",
       "",
       "### Acústica y entrepiso",
       "- El 2° piso no lleva piso radiante: entrepiso seco con piso flotante sobre lámina antiimpacto y",
       "  cielo con canal resiliente (34 cm). El cielo del 1er piso queda a 2,36 m; el nivel del 2° piso no cambia.",
       "",
       "### Terreno y exterior",
       "- La casa va en un sector plano: sólo escarpe y base granular, sin corte ni relleno.",
       "- Patio cercado para el perro, portón de acceso, senderos, bodega metálica a 10 m, luces exteriores,",
       "  residuos y ductos enterrados (EXT-01).",
       "",
       "### Muros",
       "- Se agregó una cámara técnica de 40 mm, para que las instalaciones no perforen la barrera de vapor.",
       "- Revestimiento interior de yeso-cartón RF (F-15).",
       "",
       "## Pendiente de proyectos firmados",
       "- Cálculo estructural definitivo (zona sísmica 3; NCh433:2026 rige desde ~feb-2027).",
       "- Proyecto eléctrico TE1, solar TE4 y cargador TE6 (instalador SEC).",
       "- Proyecto sanitario aprobado por la SEREMI de Salud.",
       "- Mecánica de suelos (la hace quien proyecta las fundaciones).",
       "- Prueba de hermeticidad (blower door) en obra.",
       "- Memoria térmica y de condensación firmada para el permiso DOM."]
with open(os.path.join(RAIZ, "CUMPLIMIENTO_NORMATIVO.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")
print(f"{len(RES) - len(malos)}/{len(RES)} cumplen")
for r in malos:
    print("NO CUMPLE:", r["exigencia"], "→", r["valor"])
