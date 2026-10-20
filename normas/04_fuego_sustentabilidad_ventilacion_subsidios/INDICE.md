# 04 · Fuego, sustentabilidad, ventilación, eficiencia energética y subsidios

Proyecto: vivienda rural en Puringue Pobre, comuna de Mariquina, provincia de Valdivia, Región de Los Ríos. **Zona térmica G** (confirmado en `../01_permisos_urbanismo_estructura/2024_MINVU_Tabla-Zonas-Termicas-por-Comuna.pdf`). Dos pisos, unos 130 m², estructura de madera o mixta, familia de 4 personas con mascotas. Bomba de calor, piso radiante, FV on-grid y ventilación mecánica.

Revisión al 19-oct-2026. Valor UF de referencia: unos $40.600 (MINVU/24horas indican que 50 UF ≈ $2.031.000 en mayo de 2026).

> Algunos documentos de reglamentación térmica ya están en la carpeta 01 (son idénticos, verificado con md5) y no se duplicaron aquí:
> `2025_MINVU-DITEC_Actualizacion-Reglamentacion-Termica.pdf`, `2025_MINVU_Comunicado-Actualizacion-Normativa-Termica.pdf`, `2026_MINVU-DITEC_Art-4110-Exigencias-Residencial-Edu-Salud.pdf`, `2025_MINVU_Res-Ex-1802_Condiciones-calculo-condensacion.pdf`.
> La franquicia solar térmica (Ley 20.365) está en `../03_agua_alcantarillado_gas_calefaccion/2009_Ley20365-Franquicia-Sistemas-Solares-Termicos.pdf`.

---

## 1. Tabla de documentos descargados

| Archivo | Documento | Versión / fecha | Fuente |
|---|---|---|---|
| `2025_MINVU_Listado-Oficial-Comportamiento-Fuego-ED17.pdf` | Listado Oficial de Comportamiento al Fuego de Elementos y Componentes de la Construcción | ED17, enero 2025 (la última que se encontró) | [MINVU – Listado Oficial Comportamiento al Fuego ED17-2025](https://www.minvu.gob.cl/wp-content/uploads/2025/02/00_Listado-Oficial-de-Comportamiento-al-Fuego-de-Elementos-y-Componentes-de-la-Construccion_-ED17-2025-NVO.pdf) |
| *(texto extraído, no guardado: es .docx y pertenece a la carpeta 01)* | OGUC, Título 4 Cap. 3 (seguridad contra incendio), art. 4.1.10 (térmica/ventilación) y art. 4.2.7 (barandas) | Actualizada por D.S. N°68, D.O. 02-10-2026 | [MINVU – OGUC D.S. 47 actualizada (docx)](https://www.minvu.gob.cl/wp-content/uploads/2019/05/OGUC-Mayo-2026-D.S.-N68-D.O.-02-10-2026_rev-JCB_RLP-16-10-26.docx) |
| `2025_DiarioOficial_Ley-21744-SERNAFOR-modifica-LGUC.pdf` | Ley 21.744: crea el Servicio Nacional Forestal y modifica la LGUC (zonas de riesgo y de interfaz) | D.O. 23-05-2025 | [Diario Oficial – Ley 21.744](https://www.diariooficial.interior.gob.cl/publicaciones/2025/05/23/44155/01/2650043.pdf) |
| `2022_CONAF_Metodologia-Comunidades-Preparadas.pdf` | Metodología Comunidades Preparadas frente a Incendios Forestales | 2022 (actualizado mar-2024) | [CONAF – Metodología Comunidades Preparadas 2022](https://www.conaf.cl/centro-documental/metodologia-comunidades-preparadas-2022/) |
| `2022_CONAF_Manual-Comunitario-Comunidades-Preparadas.pdf` | Manual Comunitario de prevención de incendios forestales (53 MB) | 2022 | [CONAF – Manual Comunitario 2022](https://www.conaf.cl/centro-documental/manual-comunitario-2022/) |
| `2024_MINVU_Diptico-Chile-se-Prepara-Hogar-Incendios.pdf` | Díptico "Chile se prepara – Hogar" (basado en CONAF) | dic-2024 | [MINVU – Díptico Chile se prepara Hogar](https://www.minvu.gob.cl/wp-content/uploads/2024/12/DIPTICO-chile-se-prepara-HOGAR.pdf) |
| `2024_MINVU_Diptico-Chile-se-Prepara-Barrios-Incendios.pdf` | Díptico "Chile se prepara – Barrios" | dic-2024 | [MINVU – Díptico Chile se prepara Barrios](https://www.minvu.gob.cl/wp-content/uploads/2024/12/DIPTICO-chile-se-prepara-BARRIOS.pdf) |
| `2020_UChile-RederCastillo_Prescripciones-tecnicas-viviendas-interfaz.pdf` | Prescripciones técnicas para viviendas en interfaz urbano-forestal (Castillo Soto, U. de Chile, FONDEF). Es académico, no oficial | 2020 | [Revista REDER – Prescripciones técnicas interfaz](https://www.revistareder.com/ojs/index.php/reder/article/download/51/54) |
| `2019_ONEMI-MINVU_Plan-Familia-Preparada.pdf` | Plan Familia Preparada (emergencias en el hogar) | 2019 | [MINVU/ONEMI – Plan Familia Preparada](https://csustentable.minvu.gob.cl/wp-content/uploads/2019/01/Plan-Familia-Preparada.pdf) |
| `2026_MINVU-MMA_Manuales-tecnicos-ventilacion-PPDA.pdf` | Res. Ex. 26/2026 SEREMI Valparaíso: manual "Sistema de ventilación continua tipo mixta" y planilla de caudales según NCh 3309 (DITEC) | 16-01-2026 | [MMA/PPDA – Manuales técnicos MINVU](https://ppda.mma.gob.cl/wp-content/uploads/2026/01/Manuales-tecnicos-MINVU.pdf) |
| `2014_CITEC-UBB-DECON-UC_Manual-Hermeticidad-al-aire-edificaciones.pdf` | Manual de hermeticidad al aire de edificaciones (58 MB) | 2014 | [DECON UC – Manual de hermeticidad](https://construccionsustentable.uc.cl/images/Documentos/Manual_de_hermeticidad_al_aire_de_edificaciones.pdf) |
| `2018_MINVU_ECSV-Resumen-Ejecutivo.pdf` | Estándares de Construcción Sustentable para Viviendas (ECSV): resumen ejecutivo | 2018 | [MINVU – ECSV Resumen Ejecutivo](https://csustentable.minvu.gob.cl/wp-content/uploads/2019/01/RRESUMEN-EJECUTIVO-ESTANDARES-DE-CONSTRUCCION-SUSTENTABLE-PARA-VIVIENDAS-DE-CHILE.pdf) |
| `2018_MINVU_ECSV-Tomo-I-Salud-Bienestar-2ed.pdf` | ECSV Tomo I: Salud y Bienestar | 2ª ed. 2018 | [MINVU – ECSV Tomo I](https://csustentable.minvu.gob.cl/wp-content/uploads/2018/03/EST%C3%81NDARES-DE-CONSTRUCCI%C3%93N-SUSTENTABLE-PARA-VIVIENDAS-DE-CHILE-TOMO-I-SALUD-Y-BIENESTAR.pdf) |
| `2018_MINVU_ECSV-Tomo-II-Energia.pdf` | ECSV Tomo II: Energía | 2ª ed. 2018 | [MINVU – ECSV Tomo II](https://csustentable.minvu.gob.cl/wp-content/uploads/2018/09/ESTANDARES-DE-CONSTRUCCION-SUSTENTABLE-PARA-VIVIENDAS-DE-CHILE-TOMO-II-ENERGIA.pdf) |
| `2018_MINVU_ECSV-Tomo-III-Agua-2ed.pdf` | ECSV Tomo III: Agua | 2ª ed. 2018 | [MINVU – ECSV Tomo III](https://csustentable.minvu.gob.cl/wp-content/uploads/2018/09/ESTANDARES-DE-CONSTRUCCION-SUSTENTABLE-PARA-VIVIENDAS-DE-CHILE-TOMO-III-AGUA.pdf) |
| `2016_MINVU_ECSV-Tomo-IV-Materiales-Residuos.pdf` | ECSV Tomo IV: Materiales y Residuos | 1ª ed. nov-2016 (no tiene 2ª edición) | [MINVU – ECSV Tomo IV](https://csustentable.minvu.gob.cl/wp-content/uploads/2016/11/ECSV_4.pdf) |
| `2018_MINVU_ECSV-Tomo-V-Impacto-Ambiental-2ed.pdf` | ECSV Tomo V: Impacto Ambiental | 2ª ed. 2018 | [MINVU – ECSV Tomo V](https://csustentable.minvu.gob.cl/wp-content/uploads/2018/03/EST%C3%81NDARES-DE-CONSTRUCCI%C3%93N-SUSTENTABLE-PARA-VIVIENDAS-DE-CHILE-TOMO-V-IMPACTO-AMBIENTAL.pdf) |
| `2018_MINVU_ECSV-Tomo-VI-Entorno-Inmediato-2ed.pdf` | ECSV Tomo VI: Entorno Inmediato | 2ª ed. 2018 | [MINVU – ECSV Tomo VI](https://csustentable.minvu.gob.cl/wp-content/uploads/2018/03/EST%C3%81NDARES-DE-CONSTRUCCI%C3%93N-SUSTENTABLE-PARA-VIVIENDAS-DE-CHILE-TOMO-VI-ENTORNO-INMEDIATO.pdf) |
| `2025_MINVU_Manual-Certificacion-Vivienda-Sustentable.pdf` | Manual de aplicación de la Certificación de Vivienda Sustentable (CVS), Res. Ex. 1827/2025 | 2025 | [MINVU – Manual CVS 2025](https://www.minvu.gob.cl/wp-content/uploads/2025/12/Manual-de-Certificacion-de-Vivienda-Sustentable-2025.pdf) |
| `2025_MINVU_Manual-Tecnico-Calificacion-Energetica-Viviendas-CEV.pdf` | Manual Técnico para la Calificación Energética de Viviendas en Chile (Res. Ex. 1.339/2025) | 18-08-2025 | [Sistema CEV – Manual CEV 2025](https://www.calificacionenergetica.cl/media/2025.08.18-Manual-CEV.pdf) |
| `2026_MINVU_DS1-Construccion-Vivienda-Ficha-Mayo2026.pdf` | Ficha MINVU DS1: construcción de vivienda (tramos, aportes, ahorro) | mayo 2026 | [MINVU – DS1 Construcción ficha](https://www.minvu.gob.cl/wp-content/uploads/2019/05/DS1_CONSTRUCCION_.pdf) |
| `2026_ChileAtiende_DS1-Tramo3-Construir-hasta-2200UF.pdf` | ChileAtiende: "DS1 Tramo 3: subsidio para construir una vivienda de hasta 2.200 UF" | act. 14-10-2026 | [ChileAtiende – DS1 Tramo 3 construir](https://www.chileatiende.gob.cl/fichas/83931) |
| `2017_MINVU_DS10-2015-Habitabilidad-Rural-texto-actualizado.pdf` | DS 10 (V. y U.) 2015, Programa de Habitabilidad Rural, texto actualizado | actualizado al 22-06-2017 | [MINVU – DS 10 texto actualizado](https://www.minvu.gob.cl/wp-content/uploads/2019/05/DS_10_2015_ACT_22_06_2017_Programa-de-Habitabilidad-Rural.pdf) |
| `2025_ChileAtiende_DS10-Habitabilidad-Rural-Ficha.pdf` | ChileAtiende: Programa de Habitabilidad Rural (ahorro por tramo RSH, complementarios FV, solar y térmico) | act. 06-10-2025 | [ChileAtiende – Habitabilidad Rural](https://www.chileatiende.gob.cl/fichas/111032) |
| `2018_MINVU_Guia-Soluciones-Accesibles-Viviendas.pdf` | Guía de soluciones accesibles para espacios públicos y viviendas | 2018 | [MINVU – Guía de Accesibilidad](https://csustentable.minvu.gob.cl/wp-content/uploads/2018/08/GUIA-ACCESIBILIDAD.pdf) |
| `2021_MINVU_Soluciones-Tecnicas-Accesibilidad-Universal.pdf` | Soluciones técnicas de accesibilidad universal | 2021 | [MINVU – Soluciones Técnicas AU](https://csustentable.minvu.gob.cl/wp-content/uploads/2021/06/AU_3062021.pdf) |

---

## 2. Qué dice cada documento para esta casa

### Fuego

**Listado Oficial de Comportamiento al Fuego ED17-2025**
- Con él se acredita la resistencia F de cada solución. Si un elemento no aparece en el listado, se necesita un ensayo o la asimilación por un especialista (OGUC 4.3.2). Secciones útiles para una casa de madera: A.2.3.15/30/60 (paneles verticales F-15, F-30 y F-60), F.2.1.15/30 (complejo cielo-techumbre), F.2.2 (cielo falso) y G.2.1.15/30/60 (entrepisos de madera protegidos).
- Ejemplo concreto: A.2.3.15.112 es un muro MGP10 de 35×70 a 0,40 m, con yeso-cartón ST de 10 mm al interior, LP SmartPanel de 11,1 mm al exterior y celulosa de 40 mm. Da **F-15** (IDIEM 2015). Para llegar a F-30/F-60 se usa doble placa o placa RF de 12,5–15 mm (ver A.2.3.30 y A.2.3.60).
- Cada inscripción tiene vigencia de **5 años**. Antes de especificar, revisa que el código siga vigente y pide al proveedor el informe de ensayo.

**OGUC Título 4, Capítulo 3 (texto vigente al D.S. 68 de 2026)**
- **Art. 4.3.5 n°14 (el más importante): una vivienda aislada de hasta 2 pisos y ≤ 140 m² solo exige F-15 en todos sus elementos soportantes.** Con 130 m² esta casa cumple la condición. Si las etapas futuras pasan de 140 m², la casa queda como **tipo "d"** (Tabla 1 del art. 4.3.4, habitacional de 1–2 pisos). Según el n°15, solo la superficie que exceda debe cumplir el tipo nuevo.
- Exigencias del tipo "d" (art. 4.3.3), por si se supera ese umbral: soportantes verticales **F-30**, soportantes horizontales (entrepiso) **F-30**, techumbre con cielo falso **F-15**, muros divisorios entre unidades **F-60** y muro cortafuego **F-120** (estos dos no aplican a una casa aislada). Escaleras y tabiques: sin exigencia.
- La escalera interior que une 2 pisos de la misma unidad está exenta (n°13). El cielo falso no cuenta como protección del entrepiso salvo que figure en el Listado (n°6). Un elemento inclinado 20° o más se trata como horizontal (n°12).
- Estufa a leña o chimenea (si la hay): el ducto debe salir vertical y sobrepasar la cubierta (art. 4.3.15, en vivienda unifamiliar puede ser menos de 1,5 m). Si el piso tiene una resistencia menor a F-60, delante del hogar va un revestimiento **F-60 de 0,50 m de ancho que sobresalga 0,30 m por lado** (art. 4.3.17). No se permite madera a menos de **0,60 m** de un hogar de chimenea (art. 4.3.15).

**Ley 21.744 (SERNAFOR, D.O. 23-05-2025)**
- Define la **"zona de amortiguación"** (franja que separa el bosque de lo edificado, sin continuidad de vegetación arbórea o arbustiva) y las **"zonas de interfaz urbano-rural"**, que fijan los planes reguladores.
- Modifica la LGUC (art. 33): los planes reguladores y seccionales deberán incorporar zonas de **riesgo y restricción**. Hoy no impone una distancia concreta a una vivienda rural individual. Sí conviene revisar el PRI o PRC de Mariquina y la cartografía de riesgo de CONAF/SENAPRED.

**CONAF – Metodología y Manual Comunidades Preparadas 2022**
- Zonas alrededor de la casa, medidas desde el borde exterior del alero: **Zona 1, de 0 a 2 m**, limpieza intensiva sin nada combustible. **Zona 2, de 2 a 10 m**, protección de la casa: eliminar el "combustible escalera" entre suelo y copa. **Zona 3, de 10 a 30 m**, espacio defendible: discontinuidad y espaciamiento de la vegetación. **Zona 4, de 30 a 60 m**, interfaz: bajar la intensidad para que trabajen los brigadistas.
- Según el manual, las casas con **al menos 10 m de autoprotección y techo no combustible** sobrevivieron a los incendios. Recomienda techo de material no combustible (zinc, acero o teja), **aleros cerrados**, ductos de ventilación con malla y sin aberturas grandes, canaletas limpias, terrazas sin nada combustible debajo y **nada inflamable en 3 m** alrededor de la casa (leñera fuera de esa franja).
- Díptico MINVU "Hogar": residuos y pasto retirados al menos **2 m** de la casa, y **2 a 5 m** libres entre las ramas bajas y el suelo. También pide un extintor ABC y un kit de emergencia.
- Castillo Soto (U. de Chile, FONDEF): con pastizal denso bastan **9–10 m** despejados para retrasar la ignición más de 5 min. Con arbustos o árboles se necesitan **20 m**, y con matorral alto **24–25 m**. Para pequeños propietarios recomienda podar hasta **3 m** de altura y, frente a plantaciones, **una franja de 10 m de cortafuego más 15 m de corta-combustible (25 m)**.

**Plan Familia Preparada (ONEMI/MINVU 2019)**
- Plan familiar de evacuación, punto de encuentro y mochila de emergencia. Considera a niños pequeños (pañales, fórmula), a las mascotas (transportadoras y correas) y la ruta de salida si el camino rural queda cortado.

### Ventilación, hermeticidad y calidad del aire

**OGUC art. 4.1.10 (DS 15/2024, vigente desde el 28-11-2025)**
- **Infiltración máxima de la envolvente: 5,0 ach a 50 Pa (provincia de Valdivia, Tabla 7)**, medida con NCh 3295 (blower door) y con los dispositivos de ventilación sellados. Hay una alternativa para lotes de 10 viviendas o menos mientras no haya profesionales inscritos en la región: especificar sellos en las EETT para marcos, uniones, perforaciones, soleras, ductos, etc.
- **Ventanas y puertas exteriores: clase 3 de permeabilidad al aire** (zona G, Tabla 9, NCh 3296/3297), o una solución inscrita en el Listado Oficial de Soluciones Constructivas.
- **Ventilación obligatoria**: la tasa debe ser al menos la de NCh 3308/3309 y se acredita con un "Informe de acreditación de cumplimiento de la tasa de ventilación".
- Valores máximos de U en zona G: techumbre **0,28 W/m²K** (Rt 3,57), muros **0,40** (Rt 2,50), piso ventilado **0,39**, puertas opacas **1,70**. El sobrecimiento lleva aislación por el exterior con **R100 ≥ 91**. El entretecho necesita ventilación cruzada (rejilla o celosía). Hay que verificar el riesgo de condensación según NCh 1973 y la Res. Ex. 1802.

**Manual MINVU "Sistema de ventilación continua tipo mixta" y planilla NCh 3309 (Res. Ex. 26/2026)**
- Por recinto: dormitorio principal **7 L/s** (abertura de admisión de 28 cm²), cada dormitorio simple **3,5 L/s** (14 cm²), baño **36 m³/h (10 L/s)** continuo con extractor higrorregulable a 60% HR, y cocina **Q = A × h × 5 (m³/h)**, o sea 5 renovaciones por hora.
- Cada recinto seco lleva un dispositivo de admisión, las puertas interiores llevan celosía o rebaje, y los ductos de extracción no se comparten. Planilla Excel: [MINVU – Planilla ventilación NCh 3309 v3.1](https://csustentable.minvu.gob.cl/wp-content/uploads/2021/05/VENTILACION-NCH-3309-V3.1-2018.xlsx).

**ECSV Tomo I (Salud y Bienestar), que cita NCh 3309:2014**
- **Tasa mínima para toda la vivienda (Tabla 1.2 / NCh 3309 Tabla 1B): de 93 a 139 m² con 3 dormitorios son 35 L/s ≈ 126 m³/h; con 4 dormitorios, 38 L/s ≈ 137 m³/h.** Ese es el caudal de diseño del equipo de ventilación mecánica (VMC) para esta casa.
- Extracción: cocina 50 L/s intermitente o 5 ach continuo; baño 25 L/s intermitente o 10 L/s continuo. Las tomas y descargas de aire deben quedar a **≥ 10 m** entre sí y a **≥ 20 m** de fuentes de contaminación como caminos o estufas vecinas.
- Desde Los Lagos al sur, el ECSV exige **recuperador de calor** en ventilación mecánica. Mariquina queda justo al norte de ese límite, pero en zona G se recomienda igual. HR interior óptima entre 30 y 70%. La **zona G es de alto riesgo de humedad**, por lo que conviene prever deshumidificación o VMC con control de humedad. Usar filtros MERV ≥ 6 si hay MP2,5 alto (humo de leña en invierno).

**Manual de hermeticidad al aire (CITEC UBB / DECON UC, 2014)**
- Explica cómo diseñar la barrera de aire continua en entramado de madera, sus detalles (encuentros solera-losa, ventanas, pasadas de instalaciones) y el ensayo blower door. Sirve como base para bajar de 5 ach50 a 1–3 ach50 si se busca un estándar tipo passivhaus.

### Eficiencia energética y sustentabilidad

**Manual Técnico CEV 2025 (Ley 21.305, DS 05/2024)**
- **La CEV es obligatoria desde el 5-oct-2025** para obtener la recepción definitiva, pero solo cuando construye una empresa constructora o inmobiliaria o el SERVIU. **En autoconstrucción por el propietario no es obligatoria**, aunque puede hacerse de forma voluntaria como "vivienda existente". Si la casa se hace con DS1 y un contratista, conviene incluirla.
- Escala de A+ a G, según el % de ahorro frente a la vivienda de referencia (OGUC 2007). Etapas: precalificación provisoria (sin permiso), precalificación (con permiso) y calificación (obra terminada, con visita del evaluador). La calificación vale **10 años**.
- El Informe de Precalificación Energética también sirve para acreditar el art. 4.1.10 (alternativa para viviendas).

**ECSV Tomos I a VI + Resumen Ejecutivo (MINVU 2018)**
- Tomo I: confort higrotérmico, calidad del aire, iluminación natural y solución de secado de ropa (clave en zona G para no secar ropa adentro).
- Tomo II: demanda energética por zona, envolvente, asoleamiento y equipos (bomba de calor y FV suman al % de ahorro). Tomo III: eficiencia hídrica y aguas lluvia. Tomo IV: materiales y residuos (madera certificada, Declaraciones Ambientales de Producto). Tomo V: emisiones e impacto ambiental. Tomo VI: entorno inmediato (vegetación, sombras y riesgos).

**Manual CVS 2025 (Certificación de Vivienda Sustentable)**
- Sistema voluntario que puntúa los requisitos ECSV. Sirve como checklist de diseño. No es exigencia para obtener el permiso.

### Accesibilidad, seguridad infantil y personas de baja estatura

**OGUC art. 4.2.7 (barandas)**
- **No es obligatorio en vivienda unifamiliar** (art. 4.2.1), pero se recomienda como buena práctica con niños. Baranda de **≥ 0,95 m** donde la caída supere 1 m, **0,85 m** en el tramo inclinado de la escalera, y elementos que **no dejen pasar una esfera de 12,5 cm**. En el triángulo peldaño-baranda se admite hasta 18,5 cm. Ventanas de segundo piso: abertura limitada a ≤ 0,12 m o antepecho de 0,60 m o más.
- Peldaños de vía de evacuación (referencia): huella ≥ 0,28 m y contrahuella entre 0,13 y 0,18 m. Para una estatura promedio de 1,64 m, una contrahuella de unos 0,17 m es más cómoda.

**Guía de Soluciones Accesibles (MINVU 2018) y Soluciones Técnicas AU (2021)**
- Mecanismos de apertura de ventanas entre **0,90 y 1,20 m**, lavamanos a **0,80 m**, barras en la ducha a 0,75 m (horizontal) y entre 0,80 y 1,40 m (vertical), y un círculo de giro de 1,50 m en el baño. Estas alturas son más bajas que las habituales del mercado y sirven para personas de baja estatura y para niños.
- Ducha sin escalón (desnivel ≤ 0,5 cm hacia el desagüe): útil con niños pequeños y para la vejez.

---

## 3. Subsidios recomendados para esta familia

**Supuestos:** hogar sin vivienda propia, con terreno rural propio. El tramo RSH y el tope de ingreso dependen de cada hogar: verificarlos en [Registro Social de Hogares – Mi ChileAtiende](https://www.chileatiende.gob.cl/fichas/4466-registro-social-de-hogares).

| Programa | ¿Aplica? | Por qué / montos |
|---|---|---|
| **DS1 Tramo 3 – Construcción en sitio propio** | **SÍ, es la opción principal** | Pide RSH (si supera el 90%, un tope de ingreso fijado en cada llamado; en un llamado anterior era unos **$3,43 MM para hogares de 4** en la zona centro-sur, por confirmar para 2026). **Ahorro mínimo 50 UF** (≈ $2,03 MM). **Aporte del Estado de unos 400 UF** (ficha MINVU de mayo 2026; la prensa habla de 250 a 400 UF según el precio). **Precio máximo de la vivienda 2.200 UF** y **hasta 140 m²**, con al menos baño, estar-comedor-cocina y 1 dormitorio. Cuenta de ahorro para la vivienda con **≥ 12 meses de antigüedad**. Se puede complementar con crédito hipotecario. Fuentes: [ChileAtiende – DS1 Tramo 3 construir](https://www.chileatiende.gob.cl/fichas/83931) y [MINVU – DS1 Construcción ficha](https://www.minvu.gob.cl/wp-content/uploads/2019/05/DS1_CONSTRUCCION_.pdf). |
| DS1 Tramo 2 | Solo si el RSH es ≤ 80% | Ahorro 30 UF, aporte 600 UF, vivienda ≤ 1.600 UF. Ese tope es bajo para 130 m² con bomba de calor. |
| DS10 Habitabilidad Rural (sitio del residente) | **Poco probable** | Una postulación individual exige déficit habitacional **alto** (cualquier RSH; si supera el 90%, al menos 2 indicadores), **medio** (RSH ≤ 60%) o **bajo** (RSH ≤ 40%). Una familia que arrienda en condiciones normales tiene déficit bajo. Subsidio base según RSH: 500 UF (≤ 40%), 450 (41–60%), **300 (61–80%)** y **150 (> 80%)**. Ahorro 10/30/**50 UF**. Complementos de hasta **100 UF** en soluciones sanitarias o de energía (200 si son más de una especialidad), que pueden incluir **FV, colector solar y acondicionamiento térmico**. Vivienda ≤ 1.400 UF y obligatoriamente a través de una **Entidad de Gestión Rural (EGR)**. Los llamados de 2026 para Los Ríos (resoluciones de jul/sep/oct-2026) son **colectivos (Ecobarrios)**, no individuales. Fuentes: [MINVU – DS 10 texto actualizado](https://www.minvu.gob.cl/wp-content/uploads/2019/05/DS_10_2015_ACT_22_06_2017_Programa-de-Habitabilidad-Rural.pdf) y [ChileAtiende – Habitabilidad Rural](https://www.chileatiende.gob.cl/fichas/111032). |
| DS49 FSEV – Sitio propio / autoconstrucción asistida 2026 | No | Postulación individual solo hasta el **50% del RSH** (densificación hasta 40%). Ahorro de 10–15 UF. [MINVU – Llamado DS49 sitio propio y autoconstrucción asistida 2026](https://www.minvu.gob.cl/postulacion/llamado-en-condiciones-especiales-del-ds49-para-construccion-en-sitio-propio-densificacion-predial-y-pequeno-condominio-incluyendo-el-procedimiento-de-autoconstruccion-asistida-2026/) |
| DS27 Mejoramiento (térmico, solar térmico, FV) | No | Exige una vivienda ya construida con recepción final, avalúo de hasta 1.375 UF, una **localidad urbana de más de 5.000 habitantes** y RSH ≤ 60%. El llamado 2026 se abrió el 24-08-2026: [MINVU – Programa de Mejoramiento de Viviendas y Barrios 2026](https://www.minvu.gob.cl/noticia/minvu-anuncia-puesta-en-marcha-de-programa-de-mejoramiento-de-viviendas-y-barrios-que-proyecta-la-creacion-de-casi-20-mil-empleos/) |
| Franquicia SST, Ley 20.365 | No en autoconstrucción | El crédito tributario lo usa la **empresa constructora** (contra sus PPM), con un contrato de mantención de 5 años. Solo sirve si contratan a una constructora y la vigencia en 2026 está por confirmar. |
| Casa Solar (Ministerio de Energía) | Por confirmar | Fue una compra agregada de FV con cofinanciamiento para casas con avalúo de hasta 3.000 UF (ediciones 2020–2021). No se encontró un llamado 2026: [Ministerio de Energía – Casa Solar](https://energia.gob.cl/node/22148). |

**Pasos concretos (DS1 Tramo 3):**
1. **Ahora (octubre 2026):** abrir una **cuenta de ahorro para la vivienda** (BancoEstado u otro banco) si no tienen una. Exige 12 meses de antigüedad: con la apertura en oct-2026 llegan a los llamados de la 2ª mitad de 2027. Si alguno ya tiene una cuenta abierta antes de mayo-2026, podría alcanzar el 1er llamado de 2027.
2. Revisar el **tramo RSH** en Mi ChileAtiende y actualizar el registro si cambió el hogar (cambios en la composición del hogar).
3. Depositar **≥ 50 UF** (≈ $2,1 MM) y mantenerlos hasta la fecha de corte del llamado (en 2026 fue el 29-may). No usar ese ahorro en la obra antes de postular.
4. Ordenar el terreno: inscripción de dominio a nombre del postulante o su cónyuge, **art. 55 LGUC** (IFC del SAG e informe favorable de la SEREMI MINVU; ver la carpeta 01), y certificados de informaciones previas y de factibilidad de servicios (agua de APR o pozo, electricidad), emitidos dentro de la ventana que exige el llamado.
5. Proyecto de arquitectura con permiso de edificación para una **primera etapa de ≤ 2.200 UF** que sea una vivienda completa y habitable (unos 60–80 m² con baño, cocina-estar y dormitorios), pensada para ampliarse después hasta 140 m² sin cambiar el régimen F-15.
6. Postular en el **llamado DS1** (en 2026 fue del 16 al 30 de junio en minvu.cl; la prensa menciona un 2º llamado en noviembre, por confirmar). Si salen seleccionados, contratar al constructor. Si construye una empresa, la **CEV es obligatoria** para la recepción.
7. Financiar la diferencia con ahorro, crédito hipotecario para construcción y las etapas posteriores con recursos propios. El dividendo no debería superar ~25 % del ingreso del hogar; simular el crédito con el banco.

---

## 4. Normas pagadas / no descargadas

| Norma | Tema | Por qué no está |
|---|---|---|
| [INN – NCh 3308 Ventilación – Calidad aceptable de aire interior – Requisitos](https://ecommerce.inn.cl/) | Tasas de ventilación (exigidas por OGUC 4.1.10) | Pagada (INN) |
| [INN – NCh 3309:2014 Ventilación – Calidad aceptable de aire interior en edificios residenciales de baja altura](https://ecommerce.inn.cl/) | Tablas 1B, 3 y 4 de caudales (resumidas en ECSV Tomo I) | Pagada |
| [INN – NCh 3295 Hermeticidad – Método de presurización](https://ecommerce.inn.cl/) | Ensayo blower door | Pagada |
| [INN – NCh 3296 / NCh 3297 Permeabilidad al aire de ventanas](https://ecommerce.inn.cl/) | Clase 3 en zona G | Pagada |
| [INN – NCh 935/1 Resistencia al fuego – Elementos de construcción](https://ecommerce.inn.cl/) | Ensayo de las clases F | Pagada |
| [INN – NCh 1973 Condensación](https://ecommerce.inn.cl/) y [INN – NCh 853 Transmitancia](https://ecommerce.inn.cl/) | Cálculo térmico | Pagada |
| [MINVU – OGUC D.S. 47 actualizada (docx)](https://www.minvu.gob.cl/wp-content/uploads/2019/05/OGUC-Mayo-2026-D.S.-N68-D.O.-02-10-2026_rev-JCB_RLP-16-10-26.docx) | Texto completo OGUC | Es .docx (no PDF) y corresponde a la carpeta 01. Se usó solo para extraer datos |
| [Cámara – Boletín 16335-14 Prevención de incendios forestales y rurales](https://www.camara.cl/legislacion/ProyectosDeLey/tramitacion.aspx?prmBOLETIN=16335-14) | Ley de incendios (zonas ZIURF y ZAF, cortafuegos obligatorios) | **No es ley**: en sep-2026 estaba trabado en Comisión Mixta ([El Desconcierto – doble empate Comisión Mixta ley incendios](https://eldesconcierto.cl/actualidad/gobernador-mundaca-emplaza-al-senado-doble-empate-que-mantiene-trabada-la-ley-incendios-n5462275)). El PDF espejo devolvió HTML |
| [Cámara – Boletín 16919-14 Detectores de humo en viviendas](https://www.camara.cl/legislacion/ProyectosDeLey/tramitacion.aspx?prmBOLETIN=16919-14) | Detectores de humo y CO obligatorios en viviendas nuevas | Proyecto aprobado por la Cámara, pendiente en el Senado ([Cámara – A Sala obligación detectores de humo](https://www.camara.cl/cms/2025/04/21/a-sala-obligacion-para-viviendas-de-contar-con-detectores-de-humo-para-prevenir-incendios/)). Hay otro proyecto de jun-2026. Hoy **no es obligatorio**. El PDF espejo devolvió HTML |

---

## 5. Por confirmar

- **Tope de ingreso del DS1 Tramo 3 para RSH > 90%** en el próximo llamado. La cifra de unos $3,43 MM para 4 personas viene de un llamado anterior (prensa). Compararla con el ingreso del hogar.
- **Monto exacto del aporte DS1 Tramo 3 en sitio propio**: MINVU indica 400 UF y la prensa entre 250 y 400 UF según el precio. Revisar la resolución del llamado 2027.
- **Fecha del 2º llamado DS1 de 2026 o del 1º de 2027** (minvu.gob.cl y ChileAtiende).
- **Montos DS10 actualizados**: la Res. Ex. 395/2025 y la Circular PHR 20/2025 actualizan los valores y la Res. Ex. 3130/2016 fija los multiplicadores por comuna (Mariquina). El texto descargado es de 2017. Además, el tipo de déficit habitacional de la familia lo determina el RSH.
- **Vigencia de la franquicia Ley 20.365** en 2026 y la existencia de un llamado **Casa Solar 2026**.
- **Mapas de riesgo de interfaz de CONAF/SENAPRED** para Puringue Pobre, y si el PRI o PRC de Mariquina define zonas de restricción tras la Ley 21.744.
- **Estado final del Boletín 16335-14** (ley de incendios), que podría imponer fajas obligatorias a los propietarios en zonas ZIURF o ZAF.
- **Guía de seguridad infantil en el hogar de MINSAL/Chile Crece Más** ("Elimine los riesgos de su casa"): no se encontró un PDF oficial descargable.
- **Guía oficial de Bomberos o SEC sobre detectores de humo y CO**: no se encontró un PDF. Recomendación técnica (no obligatoria): un detector de humo fotoeléctrico en cada dormitorio, pasillo y escalera, interconectados. Detector de CO solo si hay combustión (estufa a leña o gas). La bomba de calor no produce CO.
- **Edición del Listado de Fuego posterior a ED17** (no se encontró una ED18-2026). Revisar que las soluciones elegidas sigan vigentes, porque la inscripción dura 5 años.
- Si se elige VMC con recuperador, verificar que el **Informe de acreditación de la tasa de ventilación** (OGUC 4.1.10) lo pueda firmar el arquitecto o un profesional competente ante la DOM de Mariquina.
