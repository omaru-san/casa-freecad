#!/usr/bin/env python3
"""Genera calculo/MEMORIAS.html y MEMORIAS.pdf (Chrome headless) a partir de los JSON de cálculo.
Uso: python3 -I generar_memorias.py   (correr antes estructura.py, condensacion.py, fv_bateria.py y sitio/topografia.py)
"""
import json
import os
import subprocess
import sys
from html import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
import casa_datos as D  # noqa: E402
import especialidades_datos as E  # noqa: E402
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def cargar(*p):
    with open(os.path.join(RAIZ, *p), encoding="utf-8") as f:
        return json.load(f)


EST = cargar("calculo", "estructura.json")
CON = cargar("calculo", "condensacion.json")
FV = cargar("calculo", "fv_bateria.json")
TOPO = cargar("sitio", "topografia.json")
CLIMA = cargar("sitio", "clima_sitio.json")
MESES = [m["mes"] for m in CLIMA["mensual"]]


def n(v, d=1):
    if isinstance(v, (int, float)):
        s = f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return s
    return escape(str(v))


def tabla(enc, filas, clase=""):
    h = "".join(f"<th>{escape(e)}</th>" for e in enc)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f'<table class="{clase}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def ok(fu):
    return f'<span class="{"ok" if fu <= 1 else "mal"}">{n(fu, 2)} {"✔" if fu <= 1 else "✘"}</span>'


def grafico_glaser(caso):
    """Presión de vapor real vs saturación a lo largo del espesor equivalente de difusión (Sd)."""
    W, H, m = 300, 150, 34
    pts = caso["perfil"]
    sd = [0.0] + [p.get("Sd_acum_m", 0.0) for p in pts[1:]]
    xs = sorted(set(sd))
    xmax = max(sd) or 1
    pmax = 2500
    X = lambda s: m + (W - m - 8) * (s / xmax) ** 0.5   # raíz: separa capas delgadas de la barrera
    Y = lambda p: H - 22 - (H - 34) * p / pmax
    grid = "".join(f'<line x1="{m}" x2="{W-8}" y1="{Y(p):.1f}" y2="{Y(p):.1f}" stroke="#e5e5e5"/>'
                   f'<text x="{m-4}" y="{Y(p)+3:.1f}" text-anchor="end" font-size="8" fill="#666">{p}</text>' for p in range(0, 2501, 500))
    sat = " ".join(f"{X(s):.1f},{Y(p['psat']):.1f}" for s, p in zip(sd, pts))
    pv = " ".join(f"{X(s):.1f},{Y(p['pv']):.1f}" for s, p in zip(sd, pts))
    capas = "".join(f'<line x1="{X(s):.1f}" x2="{X(s):.1f}" y1="12" y2="{H-22}" stroke="#ccc" stroke-dasharray="2 2"/>' for s in xs)
    malo = caso["condensacion_intersticial"]
    return f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Diagrama de Glaser {escape(caso["nombre"])}">
      {grid}{capas}
      <polyline points="{sat}" fill="none" stroke="#888" stroke-width="2" stroke-dasharray="5 3"/>
      <polyline points="{pv}" fill="none" stroke="{"#c0392b" if malo else "#1f4e9c"}" stroke-width="2"/>
      <text x="{W-10}" y="{Y(pts[-2]['psat'])-5:.1f}" text-anchor="end" font-size="8" fill="#555">p. saturación</text>
      <text x="{m+4}" y="{Y(pts[0]['pv'])-5:.1f}" font-size="8" fill="#222">p. vapor real</text>
      <text x="{m}" y="{H-8}" font-size="8" fill="#666">interior</text>
      <text x="{W-8}" y="{H-8}" text-anchor="end" font-size="8" fill="#666">exterior → (Sd acumulado, escala √)</text>
      <text x="4" y="10" font-size="8" fill="#666">Pa</text></svg>'''


def cap_estructura():
    pk, cs, vi, s = EST["pesos_kN"], EST["coef_sismico"], EST["viento"], EST["suelo"]
    filas_c = [[escape(k.replace("_", " ")), n(v, 2)] for k, v in EST["cargas_kN_m2"].items()]
    filas_p = [[escape(k.replace("_", " ")), n(v)] for k, v in pk.items()]
    mc = [[escape(k.replace("_", " ")), n(m["largo_util_m"]), n(m["capacidad_kN"]), n(m["demanda_sismo_kN"]),
           n(m["demanda_viento_kN"]), ok(m["FU"])] for k, m in EST["muros_corte"].items()]
    el = [[escape(e["elemento"]), e["seccion_mm"], n(e["L_m"], 2), n(e["q_kN_m"], 2), n(e["M_kNm"], 2),
           f'{n(e["fb_MPa"], 2)} / {n(e["Ff_adm"])}', f'{n(e["fv_MPa"], 2)} / {n(e["Fv_adm"])}',
           f'{n(e["flecha_mm"])} / {n(e["flecha_adm_mm"])}', ok(e["FU"])] for e in EST["elementos"]]
    fu = [[escape(f["eje"]), n(f["D_kN_m"]), n(f["L_kN_m"]), n(f["q_kN_m"])] for f in EST["cargas_a_fundacion"]]
    rp = EST["reacciones_puntuales_kN"]
    p, fem = EST["pilar"], EST["fem_verificacion"]
    return f"""
<h1 id="est">1. Memoria de cálculo estructural</h1>
<p class="aviso">{escape(EST["advertencia"])}</p>
<h2>1.1 Descripción del sistema</h2><p>{escape(EST["sistema"])}</p>
<p><b>Materiales:</b> {escape(EST["materiales"]["madera"]["nombre"])} (Ff = {n(EST["materiales"]["madera"]["Ff"])} MPa,
Fv = {n(EST["materiales"]["madera"]["Fv"])} MPa, E = {n(EST["materiales"]["madera"]["E"], 0)} MPa) ·
{escape(EST["materiales"]["osb"]["nombre"])} · {escape(EST["materiales"]["hormigon"])}.</p>
<p><b>Entrepiso acústico</b> ({n(D.LOSA * 100, 0)} cm; el 2° piso no lleva piso radiante ni mortero):</p>
{tabla(["Capa (de arriba hacia abajo)", "Espesor mm", "Peso kN/m²"], [[escape(c), n(e * 1000, 0), n(w, 2)] for c, e, w in D.ENTREPISO])}
<h2>1.2 Bases de cálculo</h2>
<ul><li><b>Sismo:</b> NCh433 Of.96 Mod.2009 + DS 61, zona {EST["sismo"]["zona"]} (A0 = {EST["sismo"]["A0_g"]} g),
categoría {escape(EST["sismo"]["categoria"])}, I = {EST["sismo"]["I"]}, {escape(EST["sismo"]["sistema"])}: R = {EST["sismo"]["R"]}, R0 = {EST["sismo"]["R0"]}.</li>
<li><b>Suelo:</b> tipo {escape(s["tipo"])}: S = {s["S"]}, T0 = {s["T0"]} s, T' = {s["Tp"]} s, n = {s["n"]}; σadm = {n(s["sigma_adm_kPa"], 0)} kPa (supuesto — requiere mecánica de suelos).</li>
<li><b>Sobrecargas:</b> NCh1537 — vivienda 2,0 kPa, techo 0,3 kPa; nieve 0 (sin nieve en 31 años de registro del sitio).</li>
<li><b>Viento:</b> NCh432 simplificado, V = {n(vi["V_m_s"], 0)} m/s (racha máxima ERA5 del sitio 124 km/h), exposición C.</li></ul>
<div class="cols"><div><h3>Cargas unitarias (kN/m²)</h3>{tabla(["Carga", "Valor"], filas_c)}</div>
<div><h3>Pesos sísmicos (kN)</h3>{tabla(["Ítem", "Valor"], filas_p)}</div></div>
<h2>1.3 Análisis sísmico — método estático (NCh433 6.2)</h2>
<p>Período estimado T* = 0,05·H<sup>0,75</sup> = {n(cs["T_estimado_s"], 3)} s. C = 2,75·S·A0/(g·R)·(T'/T*)<sup>n</sup> = {n(cs["C_formula"], 2)}
&gt; Cmáx = 0,40·S·A0/g = {n(cs["C_max"], 3)} ⇒ <b>C = {n(cs["C"], 3)}</b> (Cmín = {n(cs["C_min"], 3)}).</p>
<p>Corte basal <b>Q0 = C·I·P = {n(cs["Q0_kN"])} kN</b>. Distribución en altura por A<sub>k</sub> (NCh433 6.2.5):
A1 = {n(cs["Ak"][0], 3)}, A2 = {n(cs["Ak"][1], 3)} ⇒ F1 = {n(cs["F1_kN"])} kN, F2 = {n(cs["F2_kN"])} kN.
Se amplifica ×{n(cs["torsion"], 2)} por torsión accidental.</p>
<h2>1.4 Viento</h2><p>q = 0,613·V² = {n(vi["q_basica_kPa"], 3)} kPa; q<sub>z</sub> = {n(vi["q_z_kPa"], 3)} kPa.
Fuerza total N–S {n(vi["W_NS_kN"])} kN, E–O {n(vi["W_EO_kN"])} kN. Succión en techo {n(vi["succion_techo_kPa"], 2)} kPa ⇒
amarra anti-levantamiento {n(vi["anclaje_par_kN"], 2)} kN por cercha (conector metálico tipo H2.5, cap. ≥ 2 kN).</p>
<h2>1.5 Muros de corte (OSB 11,1 mm, v<sub>adm</sub> = {n(EST["materiales"]["osb"]["v_adm_kN_m"])} kN/m)</h2>
<p>Sólo paños llenos con h/b ≤ 3,5; si h/b &gt; 2 la capacidad se reduce por 2b/h. Demanda = máx(sismo con torsión, viento).</p>
{tabla(["Piso/dirección", "Largo útil (m)", "Capacidad (kN)", "Sismo (kN)", "Viento (kN)", "FU"], mc)}
<p>Anclaje hold-down típico en extremos de paños del piso 1: <b>{n(EST["holddown_tipico_kN"])} kN</b> (perno Ø12 + conector a sobrecimiento).</p>
<h2>1.6 Elementos de madera (tensiones admisibles NCh1198)</h2>
{tabla(["Elemento", "Sección mm", "L m", "q kN/m", "M kNm", "fb/Ff MPa", "fv/Fv MPa", "Flecha/adm mm", "FU"], el, "chica")}
<p><b>Iteración de diseño:</b> en una primera versión la techumbre usaba pares con viga cumbrera apoyada sobre el muro y = 3 del piso 2,
lo que descargaba en mitad de las vigas del living (sin muro bajo él) y la cadeneta de cielo 2×4 a 3 m no cumplía flecha (FU 1,8).
Se reemplazó por <b>cerchas tipo W @ 60 cm</b> que salvan los 6 m muro a muro.</p>
<p><b>Pilar esquina terraza:</b> {escape(p["seccion_mm"])} mm, N = {n(p["N_kN"])} kN, fc = {n(p["fc_MPa"], 2)} MPa,
λ = {n(p["esbeltez"], 0)}, Fc,adm con pandeo ≈ {n(p["Fc_adm_pandeo_MPa"], 1)} MPa ⇒ cumple holgado.</p>
<h2>1.7 Verificación por elementos finitos (FreeCAD + CalculiX)</h2>
<p>{escape(fem["modelo"])}. {escape(fem["malla"])}, solver {escape(fem["solver"])}.</p>
{tabla(["Resultado", "FEM", "Teoría (empotrada)"], [["Tensión máx. (MPa)", n(fem["von_mises_max_MPa"], 2), n(fem["teoria_empotrada"]["sigma_MPa"], 2)],
                                                     ["Desplazamiento máx. (mm)", n(fem["desplazamiento_max_mm"], 2), n(fem["teoria_empotrada"]["flecha_mm"], 2)]])}
<p>{escape(fem["conclusion"])}</p>
<h2>1.8 Cargas a fundación (las fundaciones se proyectan aparte)</h2>
<p>Por decisión del mandante, <b>las fundaciones quedan fuera de este anteproyecto</b> y las diseña un tercero con su mecánica de suelos.
Se entregan las cargas de servicio en la base de los muros (sin peso propio de fundación ni sobrecimiento). El sobrecimiento debe
quedar ≥ 20 cm sobre el terreno, con aislación de borde R100 ≥ 91 (DS 15, zona G) y pernos para los hold-down.</p>
{tabla(["Eje", "D (kN/m)", "L (kN/m)", "D + L (kN/m)"], fu)}
<p>Cargas puntuales: pilar esquina terraza N = {n(rp["pilar_esquina_terraza"])} kN · tracción hold-down {n(rp["holddown_traccion"])} kN ·
corte basal total Q0 = {n(rp["corte_basal_Q0"])} kN (a transmitir por los anclajes de solera Ø12 @ ≤ 0,50 m).</p>
"""


def cap_condensacion():
    c = CON["condiciones"]
    casos = ""
    for k in CON["casos"]:
        filas = [[escape(p["capa"]), n(p["T"], 2), n(p["psat"], 0), n(p["pv"], 0),
                  '<span class="mal">condensa</span>' if (p["pv"] > p["psat"] and p["capa"] != "interior") else "—"] for p in k["perfil"]]
        estado = ('<span class="mal">✘ condensación intersticial en: ' + escape(", ".join(k["interfaces_con_condensacion"])) + "</span>"
                  if k["condensacion_intersticial"] else '<span class="ok">✔ sin condensación intersticial</span>')
        casos += f"""<div class="caso"><h3>{escape(k["nombre"])}</h3>
<p>U = {n(k["U"], 3)} W/m²K · Rt = {n(k["Rt"], 2)} m²K/W · Sd total = {n(k["Sd_total_m"])} m · T<sub>si</sub> = {n(k["Tsi"], 2)} °C · {estado}</p>
<div class="cols"><div>{tabla(["Capa (hacia afuera)", "T °C", "psat Pa", "pv Pa", ""], filas, "chica")}</div><div>{grafico_glaser(k)}</div></div></div>"""
    pt, ve, hr = CON["puente_termico_pie_derecho"], CON["ventana"], CON["hr_interior_max_pct"]
    return f"""
<h1 id="con">2. Memoria de condensación (NCh1973 — método de Glaser)</h1>
<p><b>Condiciones de cálculo:</b> interior {n(c["Ti"])} °C y {int(c["HRi"] * 100)} % HR (p<sub>v</sub> = {n(c["pv_interior_Pa"], 0)} Pa,
punto de rocío {n(c["T_rocio_interior"])} °C); exterior {n(c["Te"])} °C y {int(c["HRe"] * 100)} % HR — {escape(c["origen_exterior"])}.
Criterio de moho: superficie interior ≥ {n(c["T_superficial_min_moho"])} °C (80 % HR superficial).</p>
{casos}
<h2>2.1 Condensación superficial y puentes térmicos</h2>
<ul><li>Muro con pies derechos (15 %): U ponderado = {n(pt["U_muro_ponderado"], 3)} W/m²K (≤ 0,40 zona G ✔); T<sub>si</sub> sobre el pie derecho = {n(pt["Tsi_sobre_pie_derecho"])} °C:
{"sin" if pt["ok_condensacion"] else "CON"} condensación; {"✔ sin" if pt["ok_moho"] else "✘ riesgo de"} moho a 75 % HR interior.</li>
<li>Ventana DVH U = {n(ve["U"])}: vidrio a {n(ve["Tsi_vidrio"])} °C: {"sin" if ve["ok_condensacion"] else "CON"} condensación;
{"✔ sin" if ve["ok_moho"] else "✘ riesgo de"} moho a 75 % HR. {escape(ve["nota"])}</li></ul>
<h2>2.2 Conclusiones</h2>
<ol><li><b>La barrera de vapor es obligatoria</b> en muros y cielo: sin ella el vapor condensa en la cara fría de la lana mineral, contra el OSB.</li>
<li>Con barrera, ninguna interfaz condensa en julio.</li>
<li>La superficie más fría es el {escape(hr["superficie_critica"])}: para evitar moho la <b>humedad interior debe mantenerse ≤ {hr["sin_moho"]} %</b>
(condensación visible sobre {hr["sin_condensacion"]} %). Se logra con la ventilación de la lámina VEN-01 (VMC con recuperador de calor 35 L/s,
extracción continua en baños, cocina y lavandería, no secar ropa adentro) y es el principal riesgo de una casa hermética en este clima.</li>
<li>Alternativa para eliminar el puente térmico de los pies derechos: 30–40 mm de aislación continua por el exterior del OSB.</li></ol>
"""


def cap_fv():
    s, an, ae, rc = FV["sistema"], FV["anual"], FV["escenario_ev"]["anual"], FV["respaldo_corte"]
    filas = [[MESES[i], n(m["pv"], 0), n(m["carga"], 0), n(m["directo"], 0), n(m["bateria"], 0), n(m["importa"], 0),
              n(m["exporta"], 0), f'{int(m["autosuficiencia_pct"])} %', n(m["dias_sin_red"], 1)] for i, m in enumerate(FV["mensual"])]
    filas.append(["<b>Año</b>", f"<b>{n(an['pv'], 0)}</b>", f"<b>{n(an['carga'], 0)}</b>", n(an["directo"], 0), n(an["bateria"], 0),
                  n(an["importa"], 0), n(an["exporta"], 0), f'<b>{int(an["autosuficiencia_pct"])} %</b>', n(an["dias_sin_red"], 0)])
    filas_e = [[MESES[i], n(m["carga"], 0), n(m["importa"], 0), f'{int(m["autosuficiencia_pct"])} %'] for i, m in enumerate(FV["escenario_ev"]["mensual"])]
    return f"""
<h1 id="fv">3. Memoria fotovoltaica con batería</h1>
<p><b>Sistema:</b> {s["paneles"]} paneles × {s["wp"]} Wp = <b>{n(s["kwp"])} kWp</b>, inclinación {s["inclinacion"]}° azimut {s["azimut"]}
(3 filas × 4 apaisados en el faldón norte); inversor híbrido {n(s["inversor_kw"], 0)} kW; batería LiFePO4 {n(s["bateria_kwh"], 0)} kWh
({n(s["bateria_util_kwh"])} kWh útiles, {s["reserva_respaldo_pct"]} % reservado para cortes).</p>
<p><b>Método:</b> balance hora a hora durante {len(s["anios_simulados"])} años ({s["anios_simulados"][0]}–{s["anios_simulados"][-1]})
con la producción horaria de PVGIS 5.2 para el sitio (incluye sombras del horizonte), eficiencia de batería 92 % ida y vuelta,
potencia máx. 5 kW, prioridad: consumo → batería → red. La bomba del pozo funciona de 8 a 12 h para aprovechar el sol.</p>
<p><b>Consumo supuesto:</b> {n(FV["supuestos_consumo"]["anual_kwh"], 0)} kWh/año — {escape(FV["supuestos_consumo"]["descripcion"])},
más bomba de pozo 0,75 kW. <i>Ajustar con boletas reales.</i></p>
{tabla(["Mes", "FV kWh", "Consumo", "Directo", "Desde batería", "Compra red", "Inyecta", "Autosuf.", "Días sin red"], filas, "chica")}
<h2>3.1 Resultados</h2>
<ul><li>Autosuficiencia anual <b>{int(an["autosuficiencia_pct"])} %</b>: la red sólo aporta {n(an["importa"], 0)} kWh/año, concentrados en junio–julio.</li>
<li><b>{int(an["dias_sin_red"])} días al año</b> sin comprar energía. La batería hace ~{int(an["ciclos"])} ciclos/año (vida útil LiFePO4 &gt; 6.000 ciclos).</li>
<li>Excedente inyectado {n(an["exporta"], 0)} kWh/año (net billing, Ley 21.118): descuenta cargos de la boleta.</li>
<li><b>Respaldo ante cortes</b> (frecuentes en temporales del N–NO): {n(rc["horas_bateria_llena"])} h con batería llena y carga crítica
de {n(rc["carga_critica_kw"], 2)} kW (refrigerador, luces LED, router, bomba). Con sol, el sistema se recarga durante el corte (inversor híbrido con modo isla).</li></ul>
<h2>3.2 Escenario con auto eléctrico</h2>
<p>{escape(FV["escenario_ev"]["descripcion"])}. Consumo {n(ae["carga"], 0)} kWh/año ⇒ autosuficiencia {int(ae["autosuficiencia_pct"])} %,
compra {n(ae["importa"], 0)} kWh e inyecta {n(ae["exporta"], 0)} kWh: <b>el balance anual sigue siendo positivo</b>: el cargador
de 11 kW (RIC 15) programado de 10 a 16 h aprovecha los excedentes de verano.</p>
{tabla(["Mes", "Consumo", "Compra red", "Autosuf."], filas_e, "chica")}
"""


def cap_topo():
    t, mt = TOPO, TOPO["movimiento_tierra_m3"]
    esq = [[escape(k), n(v, 2), n(v - t["NPT"], 2)] for k, v in t["cotas_esquinas_casa"].items()]
    return f"""
<h1 id="top">4. Topografía aproximada</h1>
<p class="aviso">{escape(t["fuente"])}</p>
<p>Cota del sitio {n(t["cota_sitio"], 2)} m s.n.m.; pendiente media {n(t["pendiente_media_pct"])} % con bajada hacia {t["rumbo_bajada_deg"]}° (ONO, hacia el estero).
Desnivel natural bajo la casa: {n(t["desnivel_bajo_casa"], 2)} m.</p>
<p><b>Plataforma:</b> la casa se emplaza en un <b>sector plano</b> del terreno (decisión del 20-10-2026); el DEM de 30 m no lo
distingue y marca un desnivel de {n(t["desnivel_bajo_casa"], 2)} m que la topografía real debe descartar. NPT ±0,00 ≈ <b>{n(t["NPT"], 2)} m s.n.m.</b>
(referencial). Movimiento de tierra: escarpe de capa vegetal {n(E.ESCARPE, 2)} m ({n(mt["area_m2"] * E.ESCARPE)} m³) y base granular
compactada {n(E.BASE_GRANULAR, 2)} m ({n(mt["area_m2"] * E.BASE_GRANULAR)} m³) sobre {int(mt["area_m2"])} m²; sin corte ni relleno compensado.</p>
{tabla(["Esquina (x, y)", "Cota natural", "Respecto a NPT"], esq)}
"""


css = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #222; line-height: 1.4; background: #fff; }
h1 { font-size: 16pt; border-bottom: 2px solid #222; padding-bottom: 4px; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 12pt; margin-top: 16px; } h3 { font-size: 10.5pt; margin: 8px 0 4px; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 8.8pt; }
th, td { border: 1px solid #bbb; padding: 3px 5px; text-align: left; } th { background: #eee; }
table.chica { font-size: 7.8pt; }
.ok { color: #1e7b34; font-weight: bold; } .mal { color: #b03a2e; font-weight: bold; }
.aviso { background: #fff4e5; border-left: 4px solid #e08a00; padding: 6px 10px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }
.caso { page-break-inside: avoid; border-top: 1px solid #ddd; margin-top: 8px; }
.portada { text-align: center; margin-top: 60mm; } .portada h1 { border: none; font-size: 24pt; }
"""
html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Memorias de cálculo</title><style>{css}</style></head><body>
<div class="portada"><h1 style="page-break-before:avoid">Vivienda 2 pisos — Puringue Pobre, Mariquina</h1>
<p style="font-size:13pt">Memorias de cálculo de anteproyecto</p>
<p>1. Estructural · 2. Condensación · 3. Fotovoltaica con batería · 4. Topografía</p>
<p>20-10-2026 · Ejercicio académico (proyecto de aprendizaje FreeCAD). Sin firmas profesionales.</p></div>
{cap_estructura()}{cap_condensacion()}{cap_fv()}{cap_topo()}
</body></html>"""
ruta_html = os.path.join(AQUI, "MEMORIAS.html")
with open(ruta_html, "w", encoding="utf-8") as f:
    f.write(html)
ruta_pdf = os.path.join(AQUI, "MEMORIAS.pdf")
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={ruta_pdf}",
                f"file://{ruta_html}"], check=True, capture_output=True)
print("OK", ruta_pdf)
