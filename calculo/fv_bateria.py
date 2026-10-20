#!/usr/bin/env python3
"""Simulación horaria FV + batería (5 años, PVGIS 2016–2020) para 12 × 625 Wp a 35° norte.
Salida: calculo/fv_bateria.json.  Uso: python3 -I fv_bateria.py
"""
import json
import os
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

PANELES, WP = 12, 625
KWP = PANELES * WP / 1000                        # 7,5 kWp
INVERSOR_KW = 6.0                                # híbrido monofásico (relación DC/AC 1,25)
BAT_NOMINAL = 11.0                               # kWh
BAT_UTIL = BAT_NOMINAL * 0.90                    # DoD 90 %
BAT_P_MAX = 5.0                                  # kW carga/descarga
EF_CARGA = EF_DESCARGA = 0.96                    # ida y vuelta ≈ 92 %
SOC_RESERVA = 0.20                               # 20 % reservado para cortes de luz (respaldo)

# Consumo base (supuesto, kWh/día): familia de 4 (bebé y niña), casa TODO ELÉCTRICA sin gas:
# artefactos + iluminación LED + inducción y horno (~1,0) + VMC con recuperador (~0,6),
# + bomba del pozo/presurizadora: ~0,8 kWh/día invierno, ~1,6 kWh/día verano por riego.
CONSUMO_DIA = [10.4, 10.4, 10.5, 10.9, 11.4, 11.9, 11.9, 11.5, 11.0, 10.7, 10.5, 10.4]
BOMBA_DIA = [1.6, 1.6, 1.2, 0.9, 0.8, 0.8, 0.8, 0.8, 0.9, 1.1, 1.4, 1.6]
# forma horaria del consumo de la casa (pesos, hora local 0–23)
FORMA = [0.55, 0.45, 0.42, 0.40, 0.40, 0.45, 0.80, 1.25, 1.20, 0.90, 0.80, 0.85,
         1.00, 0.95, 0.80, 0.75, 0.85, 1.10, 1.45, 1.70, 1.75, 1.55, 1.15, 0.80]
_SF = sum(FORMA)
CARGA_CRITICA_KW = 0.35   # refrigerador + luces LED + router + bomba (promedio) en corte de luz


def hora_local(t):
    """'20160101:0010' UTC -> (año, mes, día, hora local). Chile continental: UTC-3 sep–abr, UTC-4 abr–sep."""
    a, m, d, h = int(t[:4]), int(t[4:6]), int(t[6:8]), int(t[9:11])
    off = 4 if 4 <= m <= 8 else 3
    h -= off
    if h < 0:
        h += 24
        d -= 1  # el día exacto no afecta los promedios mensuales
    return a, m, max(d, 1), h


with open(os.path.join(RAIZ, "sitio", "raw", "pvgis_horario_7p5kwp.json"), encoding="utf-8") as f:
    horas = json.load(f)["outputs"]["hourly"]

def simular(extras=()):
    """extras: [(kWh/día adicionales por mes, pesos horarios de esa carga), ...]."""
    soc = BAT_UTIL * 0.5
    mes = defaultdict(lambda: defaultdict(float))
    dias = defaultdict(lambda: {"import": 0.0})
    anios = set()
    mes = defaultdict(lambda: defaultdict(float))
    dias = defaultdict(lambda: {"import": 0.0})
    anios = set()
    for reg in horas:
        a, m, d, h = hora_local(reg["time"])
        anios.add(a)
        pv = min(reg["P"] / 1000.0, INVERSOR_KW)          # kWh en la hora (AC, recortado por inversor)
        carga = CONSUMO_DIA[m - 1] * FORMA[h] / _SF
        if 8 <= h <= 11:                                    # bomba del pozo de día (aprovecha el sol)
            carga += BOMBA_DIA[m - 1] / 4
        for extra_dia, extra_forma in extras:
            carga += extra_dia[m - 1] * extra_forma[h] / sum(extra_forma)
        directo = min(pv, carga)
        excedente, deficit = pv - directo, carga - directo
        carga_bat = min(excedente, BAT_P_MAX, (BAT_UTIL - soc) / EF_CARGA)
        soc += carga_bat * EF_CARGA
        exporta = excedente - carga_bat
        disponible = max(0.0, soc - SOC_RESERVA * BAT_UTIL)
        desc = min(deficit, BAT_P_MAX, disponible * EF_DESCARGA)
        soc -= desc / EF_DESCARGA
        importa = deficit - desc
        k = (a, m)
        for nombre, v in (("pv", pv), ("carga", carga), ("directo", directo), ("bateria", desc),
                          ("importa", importa), ("exporta", exporta), ("ciclos", carga_bat * EF_CARGA / BAT_UTIL)):
            mes[k][nombre] += v
        dias[(a, m, d)]["import"] += importa

    n_anios = len(anios)
    mensual = []
    for m in range(1, 13):
        acum = defaultdict(float)
        for a in anios:
            for kk, v in mes[(a, m)].items():
                acum[kk] += v / n_anios
        dias_mes = [v for (a, mm, d), v in dias.items() if mm == m]
        autonomos = sum(1 for v in dias_mes if v["import"] < 0.05) / n_anios
        mensual.append({k: round(v, 1) for k, v in acum.items()} | {
            "autosuficiencia_pct": round(100 * (1 - acum["importa"] / acum["carga"]), 0),
            "dias_sin_red": round(autonomos, 1)})

    tot = {k: round(sum(m_[k] for m_ in mensual), 0) for k in ("pv", "carga", "directo", "bateria", "importa", "exporta", "ciclos")}
    tot["autosuficiencia_pct"] = round(100 * (1 - tot["importa"] / tot["carga"]), 0)
    tot["autoconsumo_pct"] = round(100 * (tot["directo"] + tot["bateria"]) / tot["pv"], 0)
    tot["dias_sin_red"] = round(sum(m_["dias_sin_red"] for m_ in mensual), 0)

    return mensual, tot, anios


# Calefacción por piso radiante con bomba de calor aire-agua (SCOP 3,5) + ACS con la misma bomba de calor.
# Demanda de calefacción anual de la lámina VEN-01 (~4.800 kWh térmicos, con VMC) repartida por grados-día mensuales.
with open(os.path.join(RAIZ, "sitio", "clima_sitio.json"), encoding="utf-8") as f:
    _CLIMA = json.load(f)
_DIAS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_GD = [max(0.0, 15 - m["t_media"]) * d for m, d in zip(_CLIMA["mensual"], _DIAS)]
DEMANDA_CALEF_KWH = 4800
COP_CALEF, ACS_KWH_DIA_ELEC = 3.5, 1.3
CALEF_DIA = [DEMANDA_CALEF_KWH * g / sum(_GD) / d / COP_CALEF for g, d in zip(_GD, _DIAS)]
EXTRA_DIA = [c + ACS_KWH_DIA_ELEC for c in CALEF_DIA]
FORMA_CALEF = [0.6, 0.5, 0.5, 0.5, 0.5, 0.7, 1.2, 1.4, 1.2, 1.0, 1.0, 1.1,
               1.3, 1.3, 1.2, 1.1, 1.1, 1.3, 1.5, 1.5, 1.4, 1.2, 1.0, 0.8]

# Auto eléctrico: 12.000 km/año × 0,17 kWh/km ≈ 2.000 kWh/año, cargado de 10 a 16 h (excedente solar)
EV_DIA = 5.6
FORMA_EV = [0] * 10 + [1] * 6 + [0] * 8
CALEF = (EXTRA_DIA, FORMA_CALEF)
mensual, tot, anios = simular([CALEF])
mensual_e, tot_e, _ = simular([CALEF, ([EV_DIA] * 12, FORMA_EV)])
n_anios = len(anios)
res = {
    "sistema": {"paneles": PANELES, "wp": WP, "kwp": KWP, "inversor_kw": INVERSOR_KW, "bateria_kwh": BAT_NOMINAL,
                "bateria_util_kwh": round(BAT_UTIL, 1), "reserva_respaldo_pct": int(SOC_RESERVA * 100),
                "inclinacion": 35, "azimut": "norte", "anios_simulados": sorted(anios)},
    "supuestos_consumo": {"kwh_dia_casa": CONSUMO_DIA, "kwh_dia_bomba_pozo": BOMBA_DIA,
                          "kwh_dia_bomba_calor_y_acs": [round(v, 1) for v in EXTRA_DIA],
                          "anual_kwh": round(sum((c + b + e) * 30.4 for c, b, e in zip(CONSUMO_DIA, BOMBA_DIA, EXTRA_DIA)), 0),
                          "descripcion": "Casa todo eléctrica: piso radiante con bomba de calor SCOP 3,5 + ACS con bomba de calor, "
                                         "inducción, VMC; sin gas ni pellet"},
    "mensual": mensual, "anual": tot,
    "escenario_ev": {"descripcion": "Igual + auto eléctrico 12.000 km/año (≈ 2.000 kWh) cargado de 10 a 16 h",
                     "ev_kwh_dia": EV_DIA, "mensual": mensual_e, "anual": tot_e},
    "respaldo_corte": {"carga_critica_kw": CARGA_CRITICA_KW,
                       "horas_con_reserva_20pct": round(SOC_RESERVA * BAT_UTIL / CARGA_CRITICA_KW, 1),
                       "horas_bateria_llena": round(BAT_UTIL / CARGA_CRITICA_KW, 1)},
}
with open(os.path.join(AQUI, "fv_bateria.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res["anual"], ensure_ascii=False))
print("CON EV", json.dumps(res["escenario_ev"]["anual"], ensure_ascii=False))
print(json.dumps(res["respaldo_corte"]))
for i, m in enumerate(mensual):
    print(i + 1, m)
