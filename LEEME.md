# Casa 2 pisos — planos en FreeCAD

## Qué hay aquí
| Archivo | Qué es |
|---|---|
| `Casa.FCStd` | Modelo FreeCAD: muros 3D, losas, escalera, ventanas + capas eléctricas y de gasfitería |
| `laminas/PLANOS_COMPLETOS.pdf` | Las 11 láminas en un solo PDF |
| `laminas/01_arquitectura.pdf` | Plantas con cotas, superficies y vista 3D |
| `laminas/02_electrico.pdf` | Luces, enchufes, detectores, 15 circuitos (RIC SEC), cargador EV, cuadro de cargas |
| `laminas/03_gasfiteria.pdf` | Agua fría/caliente (bomba de calor, sin gas), alcantarillado 3 %, fosa séptica |
| `laminas/04_emplazamiento.pdf` | Orientación solar, carta solar, rosa de vientos, terreno, clima |
| `laminas/05_techumbre_fv_lluvias.pdf` | Techo 35°, paneles FV, canaletas, cosecha de lluvia |
| `laminas/06_ventilacion_calefaccion.pdf` | Piso radiante, ventilación con recuperador (VMC), balance térmico |
| `laminas/07_elevaciones_corte.pdf` | Elevaciones N y S, corte, envolvente térmica zona G |
| `CUMPLIMIENTO_NORMATIVO.md` | **Verificación norma por norma** (generada por `calculo/verificar_normas.py`) |
| `MANUAL_CONSTRUCCION.md` | **Manual por etapas: qué hacer primero, costos, financiamiento, decisiones de diseño** |
| `normas/` | Biblioteca normativa 2026 (152 PDF oficiales), con `README.md` e `INDICE.md` por tema |
| `laminas/08_estructura.pdf` | Muros de corte, entrepiso, cerchas y **cargas a fundación** (fundaciones por terceros) |
| `laminas/09_topografia.pdf` | Curvas de nivel (DEM), contexto, perfiles y movimiento de tierra |
| `laminas/10_interiorismo.pdf` | Plantas amobladas japandi: muebles a medida, qué esconde cada uno, materialidad |
| `laminas/11_iluminacion_domotica.pdf` | Luz indirecta, sensores y actuadores, escenas de Home Assistant, equipos por etapa |
| `INTERIORISMO.md` | **Diseño interior: concepto, materiales, recinto por recinto, domótica, cambios a coordinar y presupuesto** |
| `interiorismo_datos.py` | **Muebles, materiales, luces y domótica** (editar aquí) |
| `calculo/MEMORIAS.pdf` | Memorias: estructural, condensación (Glaser), FV + batería, topografía |
| `calculo/FEM_Viga.FCStd` | Análisis por elementos finitos (CalculiX) de la viga sobre la terraza |
| `calculo/*.py` | Cálculos reproducibles: `estructura.py`, `condensacion.py`, `fv_bateria.py`, `generar_memorias.py` |
| `sitio/topografia.py` | Topografía aproximada desde DEM (AWS Terrain Tiles / SRTM) |
| `sitio/INFORME_SITIO.md` | **Clima, sol, entorno y normativa del terreno (insumo permanente)** |
| `sitio/clima_sitio.json` | Datos procesados que leen los planos |
| `casa_datos.py` | **Medidas de la casa** (muros, puertas, ventanas, recintos) |
| `instalaciones_datos.py` | **Posición** de luces, enchufes, cañerías, artefactos |
| `especialidades_datos.py` | Techo, paneles, aguas lluvias, ventilación, emplazamiento, envolvente |

## Uso básico de FreeCAD
- Abrir: doble clic en `Casa.FCStd`.
- Orbitar: botón central del mouse y arrastrar (o trackpad: dos dedos).
- Vistas rápidas: tecla `0` isométrica, `2` superior, `1` frontal; `V` y luego `F` = ajustar a pantalla.
- Panel izquierdo (árbol "Modelo"): seleccionas un elemento y con la **barra espaciadora** lo ocultas o lo muestras.
  - `Piso2` → ocúltalo para ver el primer piso desde arriba.
  - `Electrico_P1`, `Gasfiteria_P1`, etc. → capas de instalaciones.
  - `Interior_P1`, `Interior_P2` → muebles (ocúltalos para ver sólo la obra).

## Cambiar medidas
1. Edita los números en `casa_datos.py` / `instalaciones_datos.py` (en metros).
2. Regenera los PDF:  `python3 generar_laminas.py`
   Si cambias estructura, paneles o consumo: `python3 -I calculo/estructura.py`, `python3 -I calculo/fv_bateria.py`,
   `python3 -I calculo/condensacion.py` y luego `python3 -I calculo/generar_memorias.py`.
   Siempre al final: `python3 -I calculo/verificar_normas.py` (actualiza CUMPLIMIENTO_NORMATIVO.md).
3. Regenera el modelo: en FreeCAD, menú Macro → Consola Python, y pega:
   ```python
   exec(open("/Users/jai/personal/casa_freecad/construir_instalaciones.py").read())
   ```
   (o simplemente pídeselo a Claude).

## Para aprender FreeCAD con este proyecto
- **Part**: muros, losas y techo son sólidos `Part::Feature` (cajas + cortes booleanos). Mira `construir_3d.py`.
- **Draft**: las instalaciones son capas Draft (líneas, círculos, textos). Mira `construir_instalaciones.py`.
- **Mesh**: el terreno `Terreno_DEM` es una malla triangular generada desde la topografía.
- **FEM**: abre `calculo/FEM_Viga.FCStd`, cambia al banco de trabajo *FEM*, doble clic en `CCX_Results` para ver tensiones.

## Importante
- Las medidas son **aproximadas** (1er piso 12 × 6 m, 2do piso 10 × 6 m). Verifica en terreno.
- Instalaciones = anteproyecto. Para construir se requiere proyecto firmado por instalador
  eléctrico SEC (TE1, TE4 solar, TE6 cargador EV) y proyecto sanitario aprobado por la SEREMI de Salud.
  Casa sin gas. Fundaciones fuera de alcance (las proyecta un tercero con las cargas de la lámina 08).
