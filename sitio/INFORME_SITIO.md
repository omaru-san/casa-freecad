# Informe del sitio — Puringue Pobre, Mariquina (Los Ríos)

> **Insumo permanente del proyecto.** Los planos leen `clima_sitio.json`. Para actualizar:
> volver a descargar `raw/` y correr `python3 -I analizar_sitio.py`, luego `python3 ../generar_laminas.py`.

- **Coordenadas:** −39,470913, −73,001954 ([ver en Google Maps](https://www.google.com/maps?q=-39.470913,-73.001954))
- **Elevación:** ~18 m s.n.m.
- **Terreno:** baja hacia el NO, de 22 m al S a 13 m al O en unos 100 m.
- **Fecha del análisis:** 19-10-2026.

## 1. Clima (1995–2025, 31 años · reanálisis ERA5 vía Open-Meteo)

| | Valor |
|---|---|
| Lluvia anual media | **1.713 mm** (rango 1.064–2.426) |
| Días con lluvia ≥ 1 mm | 136 / año |
| Lluvia en junio (mes más lluvioso) | 324 mm, con 18 días de lluvia |
| Lluvia en enero–febrero (verano seco) | ~40 mm/mes |
| Máx. diaria registrada / T10 / T25 | 136 / 94 / 107 mm |
| T media anual | 12,0 °C |
| T media julio / enero | 7,5 °C / 17,0 °C |
| T mínima absoluta / máxima absoluta | −4,5 °C / 37,0 °C |
| Heladas | ~8 días/año (may–sep) |
| Nieve | ninguna en 31 años |
| Humedad relativa invierno | 86–89 % |
| Grados-día calefacción (base 15 °C) | 1.292 |
| Racha máxima | 124 km/h, siempre del N–NO |
| Radiación horizontal | 1.598 kWh/m²·año (jun 1,4 / dic 7,6 kWh/m²·día) |

**Viento (2010–2025):**
- En el total de horas domina el S, con 27 %: es la brisa de buen tiempo del verano.
- Con lluvia, el viento viene del **N (40 %) y del NO (33 %)**.
- Con viento de 30 km/h o más, viene del **N (41 %) y del NO (36 %)**, y nunca del S ni del E.
- **Conclusión:** la fachada norte recibe a la vez el sol y los temporales.

**Tendencia y proyección:**
- La lluvia baja unos **−129 mm por década**. La extrapolación lineal da ~1.200 mm/año hacia 2050.
- La temperatura no muestra una tendencia clara en esta serie (−0,15 °C por década).
- Los escenarios CMIP6 para el sur de Chile indican menos lluvia y más calor.
- **Implicancias:** guardar agua lluvia para el verano, pero dimensionar canaletas con los extremos y no con los promedios.

## 2. Sol y fotovoltaico (PVGIS 5.2, JRC — ERA5 2005–2020, pérdidas 14 %)

| Fecha | Altura del sol al mediodía | Salida → puesta (azimut) | Horas de sol |
|---|---|---|---|
| 21 dic | 74,0° | 120° (ESE) → 240° (OSO) | 14,5 h |
| 21 mar / sep | 50,9° | 90° → 270° | 12,0 h |
| 21 jun | **27,1°** | 58° (NE) → 302° (NO) | **9,0 h** |

| Inclinación (azimut N) | kWh/kWp·año | Junio | May–Ago |
|---|---|---|---|
| 20° | 1.469 | 53 | 266 |
| 30° | 1.498 | 61 | 297 |
| **35° (elegida)** | **1.500** | 64 | 309 |
| 45° | 1.475 | 68 | 327 |

**Decisión de orientación:**
- La casa va con el eje largo E–O, y la fachada larga y el faldón de 35° **hacia el norte geográfico**.
- El norte magnético está ~7° al E del geográfico: verificar en terreno.
- **Producción esperada:**
  - Etapa 1: 8 paneles de 450 W = 3,6 kWp, unos **5.400 kWh/año**.
  - Etapa 2: 16 paneles = 7,2 kWp, unos 10.800 kWh/año.

## 3. Entorno (OpenStreetMap)

- **Camino vecinal:** a 99 m al E. Por ahí entran el acceso, el agua (APR) y la electricidad.
- **Ruta T-240:** a 267 m al E.
- **Cauce/estero:** a 159 m al NO, con el terreno 4–5 m más bajo. Riesgo de inundación bajo, pero hay napa alta posible: hacer un **test de percolación** antes de definir los drenes.

## 3b. Topografía aproximada (actualizado 20-10-2026, `topografia.json`)

- **Fuente:** DEM (AWS Terrain Tiles, base SRTM de ~30 m).
- **Cota del sitio:** 25,7 m s.n.m. Open-Meteo daba 18 m porque usa un DEM de 90 m.
- **Pendiente:** 12,5 % hacia el ONO (296°). El estudio anterior estimaba ~5 %.
- **Bajo la casa:** desnivel natural de 1,9 m. La plataforma se nivela a 25,75 y el NPT queda en 26,05; corte de 39 m³ y relleno de 42 m³, compensados.
- **Advertencia:** precisión vertical ±2–5 m. Hace falta un levantamiento real para el permiso.

## 3c. Decisiones del usuario (20-10-2026)

- **Agua:** no hay APR → **pozo propio** con bomba sumergible, hidropack, filtro y UV. El pozo va aguas arriba (SE), a más de 30 m de los drenes.
- **Paneles:** 12 × 625 Wp = 7,5 kWp, apaisados en 3 filas × 4. Inversor híbrido de 6 kW y **batería de 11 kWh**.
- **Simulación horaria (con 3.831 kWh/año de consumo supuesto):** 95 % de autosuficiencia y 312 días/año sin usar la red.

## 4. Normativa aplicable (verificada al 19-10-2026)

| Tema | Exigencia | Fuente |
|---|---|---|
| Zona térmica | **Zona G**, toda la comuna | [Tabla ZT por comunas](https://www.calificacionenergetica.cl/media/TABLA-ZT_REGIONES_PROVINCIAS-Y-COMUNAS.pdf) |
| U máx. (W/m²K) | Techumbre 0,28 · muros 0,40 · piso ventilado 0,39 · puertas 1,70 · sobrecimiento R100 ≥ 91 | [DS 15 MINVU (mod. OGUC 4.1.10)](https://www.minvu.gob.cl/wp-content/uploads/2024/10/Modificacion-art-4110-OGUC_Reglamentacion-Termica.pdf), vigente desde el 28-11-2025 |
| Ventanas (U ≤ 1,6) | Máximo N 76 % · O-E 40 % · S 26 % del muro; permeabilidad clase 3 | ídem, Tabla 3 |
| Hermeticidad | ≤ 5,0 ren/h a 50 Pa (provincia de Valdivia) | [Actualización RT – DITEC MINVU](https://www.minvu.gob.cl/wp-content/uploads/2025/11/Actualizacion-RT_DITEC.pdf) |
| Condensación y ventilación | Memoria de condensación (NCh 1973 / NCh 853) y sistema de ventilación (NCh 3308/3309) | [Nueva Reglamentación Térmica](https://www.minvu.gob.cl/nueva-reglamentacion-termica/) |
| Sismo | **Zona 3** (A0 = 0,40 g). Cálculo estructural obligatorio sobre 100 m² | [prNCh433 Tabla 1](https://sochige.cl/wp-content/uploads/2023/03/NCh00433-2022-043.pdf) |
| Alcantarillado rural | DS 236/1926: fosa con 24 h de retención + lodos 2 años; drenes de 5–25 m de tubo por persona; ≥ 20 m de pozos de agua | [DS 236 – LeyChile](https://www.bcn.cl/leychile/navegar?idNorma=171085), [Manual SUBDERE](https://www.subdere.gov.cl/sites/default/files/documentos/manual.pdf) |
| Autorización sanitaria | Proyecto aprobado por la SEREMI de Salud + autorización de funcionamiento | [ChileAtiende – aprobación](https://www.chileatiende.gob.cl/fichas/16614-aprobacion-de-proyectos-de-agua-potable-o-aguas-servidas-domesticas-particular) |
| Agua potable | APR/SSR (Ley 20.998) con certificado de factibilidad, o pozo propio (art. 56 del Código de Aguas) | [Ley 20.998 – DOH](https://doh.mop.gob.cl/APR/Materiales/Triptico%20Ley%2020998%20min%20act.pdf) |
| Leña / pellet | Mariquina **no** tiene plan de descontaminación (solo Valdivia comuna) | [PPDA – MMA](https://ppda.mma.gob.cl/) |
| Gas | DS 66 SEC: calefont tipo A/B prohibido en baño y dormitorio. Recomendado tipo C (estanco) | [DS 66 – SEC](https://www.sec.cl/sitioweb/transparencia_activa/julio2010/Decreto_66.pdf) |
| Fotovoltaico | Net billing hasta 300 kW. Trámite: solicitud a la distribuidora (probablemente SAESA) + TE4 SEC | [ChileAtiende – TE4](https://www.chileatiende.gob.cl/fichas/48597-declaracion-de-puesta-en-servicio-de-generadoras-residenciales-te4) |
| Intensidad de lluvia | Pichoy T10: 5 min ≈ 66 mm/h, 10 min ≈ 50 mm/h (derivada, no es IDF oficial) | [Tesis UACh 2008](http://cybertesis.uach.cl/tesis/uach/2008/bmfcif363e/doc/bmfcif363e.pdf) |
| Permiso DOM | Formulario FUN, Certificado de Informaciones Previas (CIP), plantas, cortes, elevaciones, emplazamiento, EETT con anexo térmico, cálculo estructural, topografía | [OGUC – LeyChile](https://www.bcn.cl/leychile/navegar?idNorma=8201), [DOM en Línea](https://domenlinea.minvu.cl) |

**No confirmado (preguntar):**
- Distancia mínima de la fosa a los deslindes (SEREMI de Salud).
- Cifras en cm² de las rejillas del DS 66 (las calcula el instalador SEC).
- Polígono de concesión eléctrica del predio.
- Tabla final de la NCh433:2026, que entra en vigencia ~feb-2027.
