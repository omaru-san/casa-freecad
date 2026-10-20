#!/usr/bin/env python3
"""Topografía aproximada del sitio a partir de teselas de elevación Terrarium (AWS Terrain Tiles,
fuente principal SRTM ~30 m en Chile). Genera sitio/topografia.json con grillas, curvas de nivel,
perfiles y movimiento de tierra.  Uso: python3 -I topografia.py

ADVERTENCIA: un DEM de 30 m NO reemplaza un levantamiento topográfico; sirve para anteproyecto.
"""
import json
import math
import os
import struct
import zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
DEM = os.path.join(AQUI, "raw", "dem")
LAT, LON = -39.470913, -73.001954
Z = 15
TX, TY = (9738, 9739, 9740), (20299, 20300, 20301)
CASA_CENTRO = (6.0, 3.0)   # el punto GPS se asume en el centro de la planta del piso 1
CASA = [(0, 2), (0, 6), (12, 6), (12, 2), (10.5, 2), (10.5, 0), (2, 0), (2, 2)]  # contorno P1 (incluye terrazas aparte)
PLATAFORMA = (-1.5, -1.5, 13.5, 7.5)  # área nivelada alrededor de la casa (x0, y0, x1, y1)


def leer_png(ruta):
    with open(ruta, "rb") as f:
        datos = f.read()
    assert datos[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, ancho, alto = 8, b"", 0, 0
    while pos < len(datos):
        n = struct.unpack(">I", datos[pos:pos + 4])[0]
        tipo = datos[pos + 4:pos + 8]
        cuerpo = datos[pos + 8:pos + 8 + n]
        if tipo == b"IHDR":
            ancho, alto, prof, color = struct.unpack(">IIBB", cuerpo[:10])
            assert prof == 8 and color == 2, "se espera RGB 8 bit"
        elif tipo == b"IDAT":
            idat += cuerpo
        pos += 12 + n
    crudo = zlib.decompress(idat)
    bpp, stride = 3, ancho * 3
    filas, prev, i = [], bytearray(stride), 0
    for _ in range(alto):
        filtro = crudo[i]
        linea = bytearray(crudo[i + 1:i + 1 + stride])
        i += 1 + stride
        for k in range(stride):
            a = linea[k - bpp] if k >= bpp else 0
            b = prev[k]
            c = prev[k - bpp] if k >= bpp else 0
            if filtro == 1:
                linea[k] = (linea[k] + a) & 255
            elif filtro == 2:
                linea[k] = (linea[k] + b) & 255
            elif filtro == 3:
                linea[k] = (linea[k] + (a + b) // 2) & 255
            elif filtro == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                linea[k] = (linea[k] + pr) & 255
        filas.append([linea[3 * j] * 256 + linea[3 * j + 1] + linea[3 * j + 2] / 256 - 32768 for j in range(ancho)])
        prev = linea
    return filas


# mosaico 768 x 768
mosaico = [[0.0] * 768 for _ in range(768)]
for ix, tx in enumerate(TX):
    for iy, ty in enumerate(TY):
        t = leer_png(os.path.join(DEM, f"t_{Z}_{tx}_{ty}.png"))
        for r in range(256):
            mosaico[iy * 256 + r][ix * 256:(ix + 1) * 256] = t[r]

n = 2 ** Z
px_sitio = ((LON + 180) / 360 * n - TX[0]) * 256
py_sitio = ((1 - math.asinh(math.tan(math.radians(LAT))) / math.pi) / 2 * n - TY[0]) * 256
RES = 156543.03392 * math.cos(math.radians(LAT)) / n  # m por pixel


def cota(x, y):
    """Elevación (m s.n.m.) en coordenadas de la casa (m, +Y norte), interpolación bilineal."""
    px = px_sitio + (x - CASA_CENTRO[0]) / RES
    py = py_sitio - (y - CASA_CENTRO[1]) / RES
    i, j = int(math.floor(py)), int(math.floor(px))
    fy, fx = py - i, px - j
    z00, z01 = mosaico[i][j], mosaico[i][j + 1]
    z10, z11 = mosaico[i + 1][j], mosaico[i + 1][j + 1]
    return (z00 * (1 - fx) * (1 - fy) + z01 * fx * (1 - fy) + z10 * (1 - fx) * fy + z11 * fx * fy)


def grilla(x0, x1, y0, y1, paso):
    xs = [x0 + k * paso for k in range(int(round((x1 - x0) / paso)) + 1)]
    ys = [y0 + k * paso for k in range(int(round((y1 - y0) / paso)) + 1)]
    return xs, ys, [[cota(x, y) for x in xs] for y in ys]


def curvas(xs, ys, zz, equidistancia):
    """Marching squares: segmentos [((x,y),(x,y), z)]."""
    zmin = min(min(f) for f in zz)
    zmax = max(max(f) for f in zz)
    niveles = [math.ceil(zmin / equidistancia) * equidistancia + k * equidistancia
               for k in range(int((zmax - zmin) / equidistancia) + 2)]
    segs = []
    for nv in niveles:
        for i in range(len(ys) - 1):
            for j in range(len(xs) - 1):
                esq = [(xs[j], ys[i], zz[i][j]), (xs[j + 1], ys[i], zz[i][j + 1]),
                       (xs[j + 1], ys[i + 1], zz[i + 1][j + 1]), (xs[j], ys[i + 1], zz[i + 1][j])]
                pts = []
                for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
                    za, zb = esq[a][2], esq[b][2]
                    if (za - nv) * (zb - nv) < 0:
                        t = (nv - za) / (zb - za)
                        pts.append((round(esq[a][0] + t * (esq[b][0] - esq[a][0]), 2),
                                    round(esq[a][1] + t * (esq[b][1] - esq[a][1]), 2)))
                if len(pts) == 2:
                    segs.append([pts[0], pts[1], round(nv, 2)])
                elif len(pts) == 4:
                    segs.append([pts[0], pts[1], round(nv, 2)])
                    segs.append([pts[2], pts[3], round(nv, 2)])
    return segs


# lote 1 m (curvas 0,5 m) y contexto 8 m (curvas 2 m)
lx, ly, lz = grilla(-25, 32, -15, 25, 1.0)
cx, cy, cz = grilla(-400, 400, -400, 400, 8.0)

# terreno bajo la casa y plataforma
esquinas = {f"({x},{y})": round(cota(x, y), 2) for x, y in CASA}
z_casa = [cota(x + 0.5, y + 0.5) for x in range(0, 12) for y in range(0, 6)]
z_med = sum(z_casa) / len(z_casa)
z_plataforma = round(z_med * 20) / 20  # redondeo a 5 cm
NPT = round(z_plataforma + 0.30, 2)
corte = relleno = 0.0
x0, y0, x1, y1 = PLATAFORMA
paso = 0.5
for i in range(int((x1 - x0) / paso)):
    for j in range(int((y1 - y0) / paso)):
        d = cota(x0 + (i + 0.5) * paso, y0 + (j + 0.5) * paso) - z_plataforma
        if d > 0:
            corte += d * paso * paso
        else:
            relleno += -d * paso * paso

# pendiente media y dirección (plano ajustado sobre ±30 m)
sxx = sxy = syy = sxz = syz = sz = n_p = 0
for x in range(-24, 37, 3):
    for y in range(-27, 34, 3):
        z = cota(x, y)
        dx, dy = x - 6, y - 3
        sxx += dx * dx; syy += dy * dy; sxy += dx * dy; sxz += dx * z; syz += dy * z
det = sxx * syy - sxy * sxy
gx = (sxz * syy - syz * sxy) / det
gy = (syz * sxx - sxz * sxy) / det
pend = 100 * math.hypot(gx, gy)
rumbo_bajada = (math.degrees(math.atan2(-gx, -gy)) + 360) % 360

perfil_oe = [[x, round(cota(x, 3), 2)] for x in range(-200, 201, 4)]
perfil_sn = [[y, round(cota(6, y), 2)] for y in range(-200, 201, 4)]

res = {
    "fuente": "AWS Terrain Tiles (Terrarium, z15, ~3,7 m/px; dato base SRTM ~30 m). Anteproyecto, no reemplaza topografía.",
    "resolucion_px_m": round(RES, 2),
    "cota_sitio": round(cota(*CASA_CENTRO), 2),
    "cotas_esquinas_casa": esquinas,
    "terreno_medio_bajo_casa": round(z_med, 2),
    "desnivel_bajo_casa": round(max(z_casa) - min(z_casa), 2),
    "cota_plataforma": z_plataforma,
    "NPT": NPT,
    "movimiento_tierra_m3": {"corte": round(corte, 1), "relleno": round(relleno, 1), "area_m2": (x1 - x0) * (y1 - y0)},
    "pendiente_media_pct": round(pend, 1),
    "rumbo_bajada_deg": round(rumbo_bajada),
    "lote": {"x": [lx[0], lx[-1]], "y": [ly[0], ly[-1]], "paso": 1.0, "z": [[round(v, 2) for v in f] for f in lz],
             "curvas_05m": curvas(lx, ly, lz, 0.5)},
    "contexto": {"x": [cx[0], cx[-1]], "y": [cy[0], cy[-1]], "paso": 8.0, "curvas_2m": curvas(cx, cy, cz, 2.0),
                 "z_min": round(min(min(f) for f in cz), 1), "z_max": round(max(max(f) for f in cz), 1)},
    "perfil_oeste_este": perfil_oe, "perfil_sur_norte": perfil_sn,
}
with open(os.path.join(AQUI, "topografia.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False)
for k in ("resolucion_px_m", "cota_sitio", "cotas_esquinas_casa", "terreno_medio_bajo_casa", "desnivel_bajo_casa",
          "cota_plataforma", "NPT", "movimiento_tierra_m3", "pendiente_media_pct", "rumbo_bajada_deg"):
    print(k, res[k])
print("contexto z", res["contexto"]["z_min"], res["contexto"]["z_max"], "curvas lote", len(res["lote"]["curvas_05m"]))
