#!/usr/bin/env python3
"""Verificación de riesgo de condensación superficial e intersticial (método de Glaser, NCh1973 / ISO 13788).
Condiciones exteriores de diseño desde sitio/clima_sitio.json (julio, mes más frío).
Salida: calculo/condensacion.json.  Uso: python3 -I condensacion.py
"""
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
with open(os.path.join(RAIZ, "sitio", "clima_sitio.json"), encoding="utf-8") as f:
    CLIMA = json.load(f)
jul = CLIMA["mensual"][6]
TI, HRI = 20.0, 0.75                          # interior (vivienda en clima húmedo, criterio conservador)
TE, HRE = jul["t_min"], jul["humedad_rel"] / 100 + 0.02   # media de mínimas de julio y HR de julio (+2 %)


def psat(t):
    if t >= 0:
        return 610.5 * math.exp(17.269 * t / (237.3 + t))
    return 610.5 * math.exp(21.875 * t / (265.5 + t))


def rocio(pv):
    a = math.log(pv / 610.5)
    return 237.3 * a / (17.269 - a)


# capa: (nombre, espesor m, lambda W/mK, mu)  — Sd = mu * e ;  "R" fija para superficies
MURO = [("Rsi", None, 0.13, None), ("Yeso-cartón RH 12,5", 0.0125, 0.25, 8), ("Barrera de vapor PE 0,2 mm", 0.0002, None, 100000),
        ("Lana mineral 140", 0.140, 0.040, 1.2), ("OSB 11,1", 0.0111, 0.13, 150), ("Membrana hidrófuga respirable", 0.0005, None, 100),
        ("Rse (cámara ventilada)", None, 0.13, None)]
MURO_SIN_BARRERA = [c for c in MURO if not c[0].startswith("Barrera")]
CIELO = [("Rsi (flujo ascendente)", None, 0.10, None), ("Yeso-cartón 12,5", 0.0125, 0.25, 8),
         ("Barrera de vapor PE 0,2 mm", 0.0002, None, 100000), ("Lana mineral 2×100", 0.200, 0.040, 1.2),
         ("Rse (entretecho ventilado)", None, 0.10, None)]
FRACCION_PIE_DERECHO = 0.15


def R_capa(c):
    nombre, e, lam, mu = c
    if e is None:
        return lam
    return 0.0 if lam is None else e / lam


def glaser(capas, nombre):
    Rs = [R_capa(c) for c in capas]
    Sds = [0.0 if c[1] is None else c[1] * c[3] for c in capas]
    Rt, Sdt = sum(Rs), sum(Sds)
    pvi, pve = HRI * psat(TI), HRE * psat(TE)
    pos, R_acum, Sd_acum = [], 0.0, 0.0
    perfil = [{"capa": "interior", "T": TI, "psat": round(psat(TI)), "pv": round(pvi)}]
    condensa = []
    for c, R, Sd in zip(capas, Rs, Sds):
        R_acum += R
        Sd_acum += Sd
        T = TI - (TI - TE) * R_acum / Rt
        pv = pvi - (pvi - pve) * Sd_acum / Sdt
        ps = psat(T)
        perfil.append({"capa": c[0], "T": round(T, 2), "psat": round(ps), "pv": round(pv), "Sd_acum_m": round(Sd_acum, 2),
                       "R_acum": round(R_acum, 3)})
        if pv > ps * 1.0001 and c[1] is not None:
            condensa.append(c[0])
    tsi = TI - (TI - TE) * Rs[0] / Rt
    return {"nombre": nombre, "U": round(1 / Rt, 3), "Rt": round(Rt, 2), "Sd_total_m": round(Sdt, 1),
            "Tsi": round(tsi, 2), "fRsi": round((tsi - TE) / (TI - TE), 3), "perfil": perfil,
            "condensacion_intersticial": bool(condensa), "interfaces_con_condensacion": condensa}


def u_paralelo(capas, frac):
    """U con pies derechos (camino de madera λ 0,13 en la capa aislante)."""
    R_a = sum(R_capa(c) for c in capas)
    capas_b = [(n, e, 0.13 if n.startswith("Lana") else lam, mu) for n, e, lam, mu in capas]
    R_b = sum(R_capa(c) for c in capas_b)
    return (1 - frac) / R_a + frac / R_b, R_b


pvi = HRI * psat(TI)
T_rocio = rocio(pvi)
T_moho = rocio(pvi / 0.80)  # superficie al 80 % HR (criterio de moho)
casos = [glaser(MURO, "Muro perimetral (con barrera de vapor)"), glaser(MURO_SIN_BARRERA, "Muro SIN barrera de vapor (contraejemplo)"),
         glaser(CIELO, "Cielo bajo entretecho ventilado")]
U_muro, R_pd = u_paralelo(MURO, FRACCION_PIE_DERECHO)
tsi_pd = TI - (TI - TE) * 0.13 / R_pd
ventana_U = 1.6
tsi_ventana = TI - (TI - TE) * 0.13 * ventana_U

res = {
    "metodo": "Glaser (NCh1973 / ISO 13788), régimen estacionario",
    "condiciones": {"Ti": TI, "HRi": HRI, "Te": TE, "HRe": round(HRE, 2),
                    "origen_exterior": "Julio: media de mínimas y HR media (sitio/clima_sitio.json, ERA5 1995–2025)",
                    "pv_interior_Pa": round(pvi), "T_rocio_interior": round(T_rocio, 1), "T_superficial_min_moho": round(T_moho, 1)},
    "casos": casos,
    "puente_termico_pie_derecho": {"U_muro_ponderado": round(U_muro, 3), "Tsi_sobre_pie_derecho": round(tsi_pd, 1),
                                   "ok_condensacion": tsi_pd > T_rocio, "ok_moho": tsi_pd > T_moho},
    "ventana": {"U": ventana_U, "Tsi_vidrio": round(tsi_ventana, 1), "ok_condensacion": tsi_ventana > T_rocio,
                "ok_moho": tsi_ventana > T_moho,
                "nota": "Borde de marco y espaciador: usar espaciador 'warm edge' y ventilación permanente."},
}
for c in casos:
    c["ok_superficial"] = c["Tsi"] > T_moho
# humedad interior máxima para que la superficie más fría (vidrio) no supere 80 % HR (moho) ni 100 % (condensación)
t_fria = min(tsi_ventana, tsi_pd)
res["hr_interior_max_pct"] = {"sin_moho": round(100 * 0.80 * psat(t_fria) / psat(TI)),
                              "sin_condensacion": round(100 * psat(t_fria) / psat(TI)),
                              "superficie_critica": "vidrio DVH" if tsi_ventana < tsi_pd else "pie derecho"}
with open(os.path.join(AQUI, "condensacion.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res["condiciones"], ensure_ascii=False))
for c in casos:
    print(c["nombre"], "U", c["U"], "Tsi", c["Tsi"], "intersticial:", c["condensacion_intersticial"], c["interfaces_con_condensacion"])
    for p in c["perfil"]:
        print("   ", p)
print(res["puente_termico_pie_derecho"], res["ventana"], res["hr_interior_max_pct"])
