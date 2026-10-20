#!/usr/bin/env python3
"""Procesa los datos descargados del sitio (raw/) y genera:
  - clima_sitio.json : resumen climático, solar y de entorno (insumo para los planos)
Uso: python3 -I analizar_sitio.py
Fuentes: Open-Meteo Historical (ERA5), PVGIS 5.2 (JRC), OpenStreetMap (Overpass/Nominatim).
"""
import json
import math
import os
import statistics as st
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(AQUI, "raw")
LAT, LON = -39.470913, -73.001954
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
SECTORES = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]


def cargar(n):
    with open(os.path.join(RAW, n), encoding="utf-8") as f:
        return json.load(f)


def r(v, n=1):
    return None if v is None else round(v, n)


def tendencia(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return b, my - b * mx


def gumbel(maximos, T):
    m, s = st.mean(maximos), st.stdev(maximos)
    alfa = math.sqrt(6) * s / math.pi
    u = m - 0.5772 * alfa
    return u - alfa * math.log(-math.log(1 - 1 / T))


def sector(grados):
    return SECTORES[int(((grados % 360) + 22.5) // 45) % 8]


# ---------------- clima diario ----------------
d = cargar("om_daily.json")["daily"]
fechas = d["time"]
por_mes = defaultdict(lambda: defaultdict(list))
por_anio = defaultdict(lambda: defaultdict(list))
for i, f in enumerate(fechas):
    a, m = int(f[:4]), int(f[5:7])
    for k in d:
        if k != "time" and d[k][i] is not None:
            por_mes[m][k].append(d[k][i])
            por_anio[a][k].append(d[k][i])
    por_mes[m]["_anio_mes"].append((a, m))

anios = sorted(a for a in por_anio if len(por_anio[a]["precipitation_sum"]) >= 360)
n_anios = len(anios)

mensual = []
for m in range(1, 13):
    pm = por_mes[m]
    lluvia_mes = defaultdict(float)
    dias_lluvia = defaultdict(int)
    for (a, _), p in zip(pm["_anio_mes"], pm["precipitation_sum"]):
        lluvia_mes[a] += p
        dias_lluvia[a] += p >= 1.0
    mensual.append({
        "mes": MESES[m - 1],
        "t_max": r(st.mean(pm["temperature_2m_max"])),
        "t_min": r(st.mean(pm["temperature_2m_min"])),
        "t_media": r(st.mean(pm["temperature_2m_mean"])),
        "t_min_abs": r(min(pm["temperature_2m_min"])),
        "t_max_abs": r(max(pm["temperature_2m_max"])),
        "lluvia_mm": r(st.mean(lluvia_mes.values()), 0),
        "dias_lluvia": r(st.mean(dias_lluvia.values()), 0),
        "humedad_rel": r(st.mean(pm["relative_humidity_2m_mean"]), 0),
        "radiacion_kwh_m2_dia": r(st.mean(pm["shortwave_radiation_sum"]) / 3.6, 2),
        "sol_horas_dia": r(st.mean(pm["sunshine_duration"]) / 3600, 1),
        "heladas_dias": r(sum(t < 0 for t in pm["temperature_2m_min"]) / n_anios, 1),
        "racha_max_kmh": r(max(pm["wind_gusts_10m_max"]), 0),
    })

anual_lluvia = {a: sum(por_anio[a]["precipitation_sum"]) for a in anios}
anual_t = {a: st.mean(por_anio[a]["temperature_2m_mean"]) for a in anios}
max_diaria = {a: max(por_anio[a]["precipitation_sum"]) for a in anios}
# grados-día de calefacción base 15 °C (criterio usado en la reglamentación térmica chilena)
gd15 = {a: sum(max(0.0, 15 - t) for t in por_anio[a]["temperature_2m_mean"]) for a in anios}
b_ll, a_ll = tendencia(anios, [anual_lluvia[a] for a in anios])
b_t, a_t = tendencia(anios, [anual_t[a] for a in anios])

dir_dom = defaultdict(int)
for v in d["wind_direction_10m_dominant"]:
    if v is not None:
        dir_dom[sector(v)] += 1

# ---------------- horario: intensidad de lluvia y viento ----------------
h = cargar("om_hourly.json")["hourly"]
max_hora = defaultdict(float)
rosa_total, rosa_invierno, rosa_fuerte, rosa_lluvia = (defaultdict(int) for _ in range(4))
for t, p, ws, wd in zip(h["time"], h["precipitation"], h["wind_speed_10m"], h["wind_direction_10m"]):
    a, m = int(t[:4]), int(t[5:7])
    if p is not None:
        max_hora[a] = max(max_hora[a], p)
    if wd is None or ws is None:
        continue
    s = sector(wd)
    rosa_total[s] += 1
    if m in (5, 6, 7, 8):
        rosa_invierno[s] += 1
    if ws >= 30:
        rosa_fuerte[s] += 1
    if p and p >= 1:
        rosa_lluvia[s] += 1


def pct(rosa):
    tot = sum(rosa.values()) or 1
    return {s: r(100 * rosa[s] / tot) for s in SECTORES}


anios_h = sorted(max_hora)
i_10 = gumbel([max_hora[a] for a in anios_h], 10)

# ---------------- geometría solar ----------------
def sol_pos(dia_juliano, hora_solar):
    dec = math.radians(23.44) * math.sin(2 * math.pi * (284 + dia_juliano) / 365)
    lat = math.radians(LAT)
    w = math.radians(15 * (hora_solar - 12))
    alt = math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(w))
    az = math.atan2(-math.sin(w) * math.cos(dec),
                    math.cos(lat) * math.sin(dec) - math.sin(lat) * math.cos(dec) * math.cos(w))
    return math.degrees(alt), (math.degrees(az) + 360) % 360  # azimut desde el norte, sentido horario


trayectorias = {}
for nombre, dj in (("solsticio_verano_21dic", 355), ("equinoccio_21mar", 80), ("solsticio_invierno_21jun", 172)):
    pts = []
    for k in range(0, 24 * 4 + 1):
        hs = k / 4
        alt, az = sol_pos(dj, hs)
        if alt > 0:
            pts.append([r(hs, 2), r(alt), r(az)])
    trayectorias[nombre] = {"puntos_hora_alt_az": pts,
                            "altura_mediodia": r(max(p[1] for p in pts)),
                            "azimut_salida": pts[0][2], "azimut_puesta": pts[-1][2],
                            "horas_sol_astronomico": r(pts[-1][0] - pts[0][0], 1)}

# ---------------- PVGIS ----------------
def pv(nombre):
    j = cargar(nombre)
    mt = j["inputs"]["mounting_system"]["fixed"]
    return {"inclinacion": mt["slope"]["value"], "azimut_pvgis": mt["azimuth"]["value"],
            "kwh_anual_por_kwp": r(j["outputs"]["totals"]["fixed"]["E_y"], 0),
            "kwh_mensual_por_kwp": [r(x["E_m"], 0) for x in j["outputs"]["monthly"]["fixed"]],
            "irradiacion_plano_kwh_m2_anual": r(j["outputs"]["totals"]["fixed"]["H(i)_y"], 0)}


# PVGIS "optimalangles" devolvió 0° (no confiable): se hace un barrido manual de inclinaciones
pv_incl = {a: pv(f"pvgis_{a}.json") for a in (15, 20, 25, 30, 35, 40, 45, 50)}
INCLINACION_ELEGIDA = 35

# ---------------- entorno OSM ----------------
osm = cargar("osm.json")["elements"]


def dist_m(lat, lon):
    dy = (lat - LAT) * 111_320
    dx = (lon - LON) * 111_320 * math.cos(math.radians(LAT))
    return math.hypot(dx, dy), (math.degrees(math.atan2(dx, dy)) + 360) % 360


caminos, aguas = [], []
for e in osm:
    if "geometry" not in e:
        continue
    best = min((dist_m(g["lat"], g["lon"]) for g in e["geometry"]), key=lambda x: x[0])
    tags = e.get("tags", {})
    item = {"tipo": tags.get("highway") or tags.get("waterway"), "nombre": tags.get("name", ""),
            "dist_m": r(best[0], 0), "rumbo_desde_sitio": r(best[1], 0), "sector": sector(best[1])}
    if "highway" in tags:
        caminos.append(item)
    elif "waterway" in tags:
        aguas.append(item)
caminos.sort(key=lambda x: x["dist_m"])
aguas.sort(key=lambda x: x["dist_m"])
elev = cargar("elev.json")["elevation"]

res = {
    "sitio": {"lat": LAT, "lon": LON, "comuna": "Mariquina", "sector": "Puringue Pobre",
              "region": "Los Ríos", "elevacion_m": elev[0],
              "elevaciones_100m_N_S_E_O": {"N": elev[1], "S": elev[2], "E": elev[3], "O": elev[4]},
              "declinacion_magnetica_aprox": "≈ +7° E (2026; verificar con NOAA)",
              "caminos_cercanos": caminos[:5], "cursos_agua_cercanos": aguas[:5]},
    "periodo": f"{anios[0]}–{anios[-1]} ({n_anios} años)",
    "fuente_clima": "Open-Meteo Historical Weather API (reanálisis ERA5/ERA5-Land, ~10 km)",
    "mensual": mensual,
    "anual": {
        "lluvia_media_mm": r(st.mean(anual_lluvia.values()), 0),
        "lluvia_min_mm": r(min(anual_lluvia.values()), 0), "anio_mas_seco": min(anual_lluvia, key=anual_lluvia.get),
        "lluvia_max_mm": r(max(anual_lluvia.values()), 0), "anio_mas_lluvioso": max(anual_lluvia, key=anual_lluvia.get),
        "t_media": r(st.mean(anual_t.values())),
        "t_min_absoluta": r(min(min(por_anio[a]["temperature_2m_min"]) for a in anios)),
        "t_max_absoluta": r(max(max(por_anio[a]["temperature_2m_max"]) for a in anios)),
        "grados_dia_calefaccion_base15": r(st.mean(gd15.values()), 0),
        "dias_lluvia": r(sum(m["dias_lluvia"] for m in mensual), 0),
        "heladas_dias": r(sum(m["heladas_dias"] for m in mensual), 0),
        "nieve_cm_total_periodo": r(sum(x for x in d["snowfall_sum"] if x), 1),
        "racha_max_kmh": r(max(max(por_anio[a]["wind_gusts_10m_max"]) for a in anios), 0),
        "radiacion_horizontal_kwh_m2": r(sum(m["radiacion_kwh_m2_dia"] * 30.4 for m in mensual), 0),
        "serie_lluvia_mm": {a: r(v, 0) for a, v in anual_lluvia.items()},
        "serie_t_media": {a: r(v, 2) for a, v in anual_t.items()},
    },
    "tendencias_y_proyeccion": {
        "lluvia_mm_por_decada": r(b_ll * 10, 0),
        "temperatura_c_por_decada": r(b_t * 10, 2),
        "proyeccion_lineal_2035": {"lluvia_mm": r(a_ll + b_ll * 2035, 0), "t_media": r(a_t + b_t * 2035, 1)},
        "proyeccion_lineal_2050": {"lluvia_mm": r(a_ll + b_ll * 2050, 0), "t_media": r(a_t + b_t * 2050, 1)},
        "nota": "Extrapolación lineal de la serie 1995–2025; referencial. Los escenarios CMIP6 para el sur de "
                "Chile indican en general menos lluvia y más temperatura a 2050. Diseñar canaletas con extremos, "
                "no con promedios.",
    },
    "extremos_lluvia": {
        "max_diaria_mm_registrada": r(max(max_diaria.values()), 0),
        "max_diaria_T10_mm": r(gumbel(list(max_diaria.values()), 10), 0),
        "max_diaria_T25_mm": r(gumbel(list(max_diaria.values()), 25), 0),
        "max_horaria_mm_registrada": r(max(max_hora.values()), 1),
        "max_horaria_T10_mm_h": r(i_10, 1),
        "intensidad_diseno_canaletas_mm_h": 60,
        "nota_diseno": "El reanálisis suaviza los chubascos cortos. Para canaletas se adopta 60 mm/h "
                       "(≈ 2–3× la intensidad horaria T10 del reanálisis), valor conservador para 5–10 min.",
    },
    "viento": {
        "rosa_total_pct": pct(rosa_total), "rosa_invierno_pct": pct(rosa_invierno),
        "rosa_vientos_fuertes_30kmh_pct": pct(rosa_fuerte), "rosa_con_lluvia_pct": pct(rosa_lluvia),
        "direccion_dominante_diaria_pct": pct(dir_dom), "periodo_horario": f"{anios_h[0]}–{anios_h[-1]}",
    },
    "sol": {"trayectorias": trayectorias, "orientacion_recomendada": "Fachada larga y faldón FV hacia el NORTE geográfico"},
    "fotovoltaico_pvgis": {"por_inclinacion": {a: {k: v[k] for k in ("kwh_anual_por_kwp", "kwh_mensual_por_kwp")}
                                               for a, v in pv_incl.items()},
                           "inclinacion_elegida": INCLINACION_ELEGIDA,
                           "nota": "Óptimo anual 33–35°; 35° da el mismo total anual y +4 % en invierno vs 30°.",
                           "fuente": "PVGIS 5.2 (JRC), PVGIS-ERA5 2005–2020, pérdidas 14 %, con horizonte, azimut norte"},
}
with open(os.path.join(AQUI, "clima_sitio.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("anual", "tendencias_y_proyeccion", "extremos_lluvia")}, ensure_ascii=False, indent=1)[:3000])
print(json.dumps(res["viento"], ensure_ascii=False))
print(json.dumps(res["fotovoltaico_pvgis"], ensure_ascii=False))
print(json.dumps(res["sitio"], ensure_ascii=False))
for m in mensual:
    print(m)
for k, v in trayectorias.items():
    print(k, v["altura_mediodia"], v["azimut_salida"], v["azimut_puesta"], v["horas_sol_astronomico"])
