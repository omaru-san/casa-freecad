# Manual de construcción por etapas — Casa Puringue Pobre (Mariquina, Los Ríos)

> **Para quién:** familia de 4 personas (estatura promedio 1,64 m), con:
> - niños pequeños;
> - mascotas (gatos y perro);
> - 2 autos;
> - una bomba de calor.
>
> *Versión pública: se omitieron datos personales y financieros del hogar.*
>
> **Objetivo:** una casa de calidad y duradera, con:
> - seguridad contra incendio;
> - eficiencia energética (bomba de calor, piso radiante, termoaislación zona G y paneles solares);
> - ventilación sana, domótica y buena presión de agua.
>
> **Supuestos (corregir si no calzan):**
> - el terreno es propio, en Puringue Pobre (ver [sitio/INFORME_SITIO.md](sitio/INFORME_SITIO.md));
> - hay un **presupuesto inicial acotado** y se irá sumando capital por etapas.
>
> **Normativa:** está toda descargada en [normas/](normas/README.md) (vigente a oct-2026).
> Los artículos que se citan acá están en esos PDF.
>
> **Costos:** son **estimaciones de orden de magnitud** (UF ≈ $40.000). Hay que cotizarlos siempre.

---

## 0. Lo más importante en una página

1. **Con un presupuesto inicial acotado no se construye la casa, pero sí se hace lo más valioso:**
   - el proyecto completo aprobado;
   - los estudios de suelo;
   - el permiso;
   - abrir el camino a subsidio y crédito.

   Una casa de ~130 m² con este estándar cuesta del orden de **$130–200 MM**, o sea **25–38 UF/m²**.
   Gastar el presupuesto inicial en obra sin tener financiada la obra gruesa es el error más caro posible:
   - la madera y el hormigón a medio hacer se deterioran con 1.700 mm de lluvia al año;
   - los proyectos improvisados después cuestan el doble.
2. **Financiamiento realista:**
   - **Subsidio DS1 Tramo 3, construcción en sitio propio:** ~400 UF (≈ $16 MM). Exige ahorro de 50 UF en una cuenta de ahorro para la vivienda con **12 meses de antigüedad**, así que hay que **abrirla esta semana**.
   - **Crédito hipotecario para construcción en sitio propio.** BancoEstado y otros bancos lo dan contra el terreno y el proyecto aprobado. El dividendo no debería superar ~25 % del ingreso del hogar.
   - **Ahorro propio por etapas.**
   - **Ojo con el DS1:** el Tramo 3 tiene un tope de ingreso (en un llamado anterior, ~$3,43 MM para hogares de 4). Hay que compararlo con el ingreso del hogar y confirmarlo en el próximo llamado (ver [normas/04/INDICE](normas/04_fuego_sustentabilidad_ventilacion_subsidios/INDICE.md)).
   - El DS1 exige vivienda de **≤ 2.200 UF y ≤ 140 m²**.
3. **Mantener la casa en ≤ 140 m²:**
   - calza con el DS1;
   - la OGUC exige solo **F-15** en la estructura (sobre 140 m² sube a F-30);
   - baja el costo.
4. **Primero la envolvente, después las terminaciones.** El orden que nunca se altera:
   - fundaciones (las proyecta y ejecuta un tercero, ver Etapa 3);
   - estructura;
   - techo;
   - barreras;
   - ventanas;
   - instalaciones;
   - aislación;
   - prueba de hermeticidad;
   - revestimientos.

   **Construir de octubre a abril** y cerrar el techo antes de mayo.
5. **Diseño ya ajustado a la norma (20-10-2026).** Los planos de `laminas/` quedaron como **casa todo eléctrica**:
   - bomba de calor aire-agua para el piso radiante y el agua caliente;
   - cocina de inducción y ventilación mecánica con recuperador de calor;
   - **sin gas**, y por lo tanto sin riesgo de monóxido de carbono ni trámite TC6.

   El detalle norma por norma está en [CUMPLIMIENTO_NORMATIVO.md](CUMPLIMIENTO_NORMATIVO.md) (55 verificaciones automáticas).
   **Las fundaciones quedan fuera de este proyecto:** la lámina 08 entrega las cargas para quien las diseñe.

---

## 1. Lo que dice el lugar (y por qué importa)

| Dato del sitio | Consecuencia de diseño |
|---|---|
| Zona térmica **G** | Transmitancia U máxima (W/m²K): techo **0,28**, muros **0,40**, piso ventilado **0,39**; sobrecimiento con R100 ≥ 91. Ventanas termopanel clase 3. Infiltraciones ≤ **5 renovaciones/h a 50 Pa** (DS 15, OGUC 4.1.10). |
| Lluvia de 1.713 mm/año y temporales del N–NO | Aleros ≥ 60 cm, **fachada ventilada**, barrera hídrica, canaletas dimensionadas para 66 mm/h, sobrecimiento ≥ 20 cm sobre el terreno y drenaje perimetral. |
| Humedad de 86–89 % en invierno | Riesgo de **condensación y hongos**: memoria de condensación (exterior 3,5 °C / 98 % HR, Res. Ex. 1802), barrera de vapor en la cara caliente y **ventilación mecánica**. |
| Zona sísmica 3 | Estructura calculada. Madera preservada según NCh 819 y anclajes (OGUC 5.6). **NCh433:2026 rige desde ~feb-2027**: ingresar el permiso antes, o diseñar ya con la nueva norma. |
| Napa posiblemente alta y estero a 159 m | **Calicata y test de percolación en invierno** antes de diseñar la fosa y las fundaciones. Revisar si hay suelo orgánico (ver el manual de suelos orgánicos del sur). |
| Rural, sin alcantarillado | Fosa séptica y drenes (DS 236), con proyecto aprobado por la **SEREMI de Salud**. Agua de APR o pozo. |
| Entorno rural con praderas y plantaciones | **Interfaz urbano-forestal:** techo no combustible, aleros cerrados y faja libre de combustible de 30 m (CONAF). |
| 1.500 kWh/kWp·año (FV a 35° hacia el norte) | La FV rinde bien en verano y poco en junio. Con net billing, el verano "paga" parte del invierno. |

---

## 2. Decisiones de diseño para esta familia

### 2.1 Tamaño y forma
- **Tamaño:**
  - Mantener **≤ 140 m²** (hoy son ~132 m²).
  - Sobre 100 m² se exige cálculo estructural, salvo madera ejecutada según OGUC Título 5 Cap. 6. Igual se recomienda calcular por la zona sísmica 3.
- **Forma:**
  - Compacta (rectángulo), con el eje largo E–O y la fachada larga hacia el norte (como el anteproyecto).
  - Cada quiebre o esquina agrega costo, puentes térmicos y filtraciones.
- **Niños pequeños y escalera:**
  - Puertas de seguridad arriba y abajo.
  - Pasamanos continuo y baranda de ≥ 0,95 m con barrotes separados < 10 cm.
  - Dejar un dormitorio en el 1er piso convertible es buena idea a largo plazo.

### 2.2 Ergonomía para estatura de 1,64 m
Son alturas recomendadas, no obligatorias. **Altura de piso a cielo ≥ 2,30 m** (OGUC 4.1.1); 2,40 m es suficiente y ahorra calefacción.

| Elemento | Estándar habitual | Recomendado para ustedes |
|---|---|---|
| Mesón de cocina | 90 cm | **85–86 cm** |
| Base de los muebles altos de cocina | 150 cm | **138–142 cm** (última repisa ≤ 180 cm) |
| Interruptores | 110–120 cm | **100–105 cm** (los niños también llegan) |
| Ducha (salida de agua) | 210 cm | **195–200 cm**, con barra deslizable |
| Barra del clóset | 180 cm | **160–165 cm** (doble barra en los infantiles) |
| Antepecho de ventanas | 90 cm | 90 cm, con **limitador de apertura** en el 2° piso por niños y mascotas |

### 2.3 Mascotas (gatos y perro)
- **Pisos:**
  - **Porcelanato o cerámica** en las zonas comunes: es el mejor piso para piso radiante, resiste uñas y se limpia bien.
  - Evitar alfombra y piso flotante laminado delgado.
- **Barro e higiene:**
  - **"Mudroom"** o lavadero junto al acceso, con ducha baja para el perro: con el barro de Los Ríos se agradece todos los días.
  - Espacio de arenero ventilado, con extracción en lavadero o baño.
- **Puerta gatera:** usar un modelo **hermético** (con burlete) o no ponerla, porque rompe la hermeticidad.
- **Cables:** nada de cables expuestos (ver 2.6). Los gatos y perros los muerden.
- **Mallas:** mallas mosquiteras o de protección en las ventanas que se abren.

### 2.4 Seguridad contra incendio
| Medida | Por qué y cómo | Obligatorio |
|---|---|---|
| Resistencia **F-15** en elementos soportantes (≤ 140 m²) | Planchas de yeso-cartón RF de 12,5–15 mm por el interior en muros y cielos. Soluciones del [Listado Oficial de Comportamiento al Fuego ED17](normas/04_fuego_sustentabilidad_ventilacion_subsidios/2025_MINVU_Listado-Oficial-Comportamiento-Fuego-ED17.pdf). | Sí (OGUC 4.3) |
| **Cubierta metálica** (zinc-alum o acero prepintado), aleros cerrados por debajo con fibrocemento y rejillas de ventilación con malla metálica fina | Las pavesas de incendios forestales entran por los aleros abiertos. | Recomendado (CONAF) |
| **Faja de defensa** alrededor de la casa: 0–2 m sin vegetación (ripio), 2–10 m con pasto corto y sin leña, y 10–30 m con árboles raleados y podados en altura | Es la medida más eficaz contra un incendio forestal. | Recomendado (CONAF) |
| **Detectores de humo interconectados** en pasillos y dormitorios | Inalámbricos de 10 años o integrados a la domótica. | No (proyecto de ley), pero imprescindible |
| **Sin combustión dentro de la casa** (bomba de calor e inducción) | Elimina el monóxido de carbono y el fuego abierto. Si algún día ponen una estufa, agregar detector de CO. | — |
| Extintor PQS de 6 kg en la cocina y el 2° piso, y manta ignífuga en la cocina | Bajo costo y alto impacto. | Recomendado |
| Paneles solares: inversor con **AFCI** y cable de corriente continua en tubo metálico | Obligatorio desde el 01-01-2026 (SEC Res. 33.038). | Sí |
| **Reserva de agua contra incendio**: el estanque de agua lluvia, con salida de 1½" y manguera | Sirve contra un incendio forestal y para riego. | Recomendado |
| Plan de evacuación familiar | Todos lo conocen y cada niño pequeño tiene un adulto asignado ([Plan Familia Preparada](normas/04_fuego_sustentabilidad_ventilacion_subsidios/2019_ONEMI-MINVU_Plan-Familia-Preparada.pdf)). | — |

### 2.5 Envolvente: termoaislación, hermeticidad y durabilidad
Solución sugerida para **muro de entramado de madera**, de adentro hacia afuera:
1. Yeso-cartón RF de 15 mm.
2. **Cámara técnica para instalaciones** de 40 mm (pino de 2×2"), para que los enchufes no perforen la barrera de vapor. Es el detalle que más ayuda a la hermeticidad.
3. **Barrera de vapor** (polietileno de 0,2 mm o membrana "inteligente"), con traslapes sellados con cinta.
4. Entramado de 2×6" (138 mm) relleno con **lana mineral**, que además ayuda al fuego.
5. OSB estructural de 11,1 mm.
6. **Barrera hídrica permeable al vapor** (tipo Tyvek).
7. **Listón separador de 20–25 mm**, que forma la cámara ventilada, con malla anti-roedores abajo.
8. **Revestimiento** de fibrocemento o madera.

**Qué cumple cada capa:**
- Las capas 4 y 5 forman la estructura y cumplen U ≤ 0,40 con holgura.
- Las capas 6 y 7 forman la **fachada ventilada**, clave en Los Ríos.

**Resto de la envolvente:**
- **Techo:** ≥ 200 mm de lana mineral o de vidrio (apunta a U ≈ 0,20, mejor que el 0,28 exigido).
- **Ventanas:** PVC con termopanel bajo emisivo, U ≤ 1,6 y **clase 3** de permeabilidad. Instaladas con cinta de sellado y sin espuma sola.
- **Piso:** radier sobre **EPS de alta densidad ≥ 80–100 mm**, más polietileno bajo el radier contra la humedad del suelo. Aislante en el borde del sobrecimiento (R100 ≥ 91).
- **Madera:** preservada (CCA o MCA según NCh 819) en todo lo que toque hormigón o esté en el exterior.
- **Prueba de hermeticidad (blower door)** antes de cerrar los tabiques. Meta: **≤ 3 renovaciones/h a 50 Pa**; la norma exige ≤ 5.

### 2.6 Electricidad, paneles solares, auto eléctrico y domótica
Detalle en [normas/02/INDICE](normas/02_electrico_solar_domotica/INDICE.md).

**Empalme:**
- Pedir **factibilidad a SAESA** (el formulario está descargado).
- Ideal: **trifásico** contratado a 3×16 A (se mantiene la tarifa BT1), con el alimentador y el tablero dimensionados para 3×32 A.
- El monofásico (máximo 40 A) se queda corto para bomba de calor, inducción y auto al mismo tiempo.

**Protecciones (obligatorias):**
- **Diferencial de 30 mA** en todos los circuitos, con máximo 3 circuitos por diferencial.
- **Enchufes con alvéolos protegidos.**
- Protector de sobretensión tipo 2.
- Tierra ≤ 20 Ω.

**Cargador de auto (RIC 15):**
- Circuito exclusivo y diferencial tipo B.
- Se declara con **TE6**.
- Dejar el **ducto y el cable ya instalados** al estacionamiento aunque el cargador se compre después.

**Paneles solares:**
- Etapa 1: 3,6 kWp. Etapa 2: 7,2 kWp.
- Net billing con SAESA. El TE4 lo declara un instalador SEC clase A o B.
- Dejar la estructura de techo calculada para el peso de los 16 paneles desde el principio.

**Domótica** (económica y sin depender de una marca):
- Cable **Cat6 a cada recinto** más un **ducto vacío de reserva** desde el rack hasta el entretecho y el exterior.
- Controlador **Home Assistant** con dispositivos **Zigbee o Matter**.
- Automatizaciones útiles:
  - termostatos por zona del piso radiante;
  - la ventilación sube según la humedad y el CO₂;
  - el auto carga cuando hay sol;
  - corte de agua con sensor de fuga;
  - alarma de humo al celular.
- Rack de red en la **sala técnica con llave**, junto al tablero, el inversor y el acumulador de agua caliente.

### 2.7 Agua, presión, agua caliente y alcantarillado
Detalle en [normas/03/INDICE](normas/03_agua_alcantarillado_gas_calefaccion/INDICE.md).

**Fuente de agua:**
- Pedir **factibilidad al APR o SSR**.
- Si no hay cupo, pozo propio: el art. 56 permite ≤ 0,5 L/s y 20 m³/mes sin derecho de aguas, con análisis de calidad.

**Buena presión:**
- Estanque de **2.000–3.000 L**.
- **Bomba presurizadora de velocidad variable** ajustada a ~30–35 m.c.a., más hidroneumático de 20–24 L.
- Matriz de 25–32 mm en PPR o PEX.
- El RIDAA exige ≥ 14 m.c.a. tras el medidor y una velocidad ≤ 2 m/s.

**Agua caliente con bomba de calor:**
- Acumulador de **250–300 L** a 55–60 °C.
- **Ciclo antilegionella semanal a ≥ 60 °C.**
- **Válvula mezcladora termostática a 45–48 °C** a la salida: obligatoria en la práctica con niños.
- Griferías termostáticas en la ducha y la tina.

**Fosa séptica:**
- Prefabricada certificada de ~2.000–2.400 L, más drenes según el test de percolación.
- **≥ 20 m del pozo** (mejor 30 m), aguas abajo y con acceso para el camión limpiafosas.
- Si la napa está alta: biofiltro o planta domiciliaria aprobada por la SEREMI.

**Agua lluvia:**
- Un techo de ~150 m² capta ~215 m³/año.
- Estanques de **10–20 m³** con desviador de primeras aguas, para riego e inodoros en verano.
- **Red separada y morada, sin conexión con el agua potable.**

**Alcantarillado:**
- Tubo de 100 mm, pendiente de 3 % (mínimo legal; la pendiente fija el proyectista).
- Cámaras de inspección a ≤ 30 m y en cada cambio de dirección.

### 2.8 Calefacción y ventilación
**Piso radiante con la bomba de calor:**
- Impulsión a **30–40 °C**, que es donde la bomba de calor es más eficiente.
- Tubo PEX-a o PE-RT de 16 mm **con barrera antioxígeno**, a 10–20 cm entre tubos.
- Circuitos ≤ 100–120 m, colector con caudalímetros y **termostato por zona**.
- Prueba de presión antes del mortero.
- **Poner piso radiante en ambos pisos.** En el 2° piso va sobre la losa o placa con aislante acústico, o con radiadores de baja temperatura si sale caro.

**Bomba de calor:**
- Potencia del orden de **6–8 kW térmicos** (la calcula el proyectista según la pérdida de calor).
- Unidad exterior en la fachada **oriente u poniente**, protegida de los temporales del N–NO y lejos de los dormitorios por el ruido.
- Entrada **SG-Ready** para la domótica y los paneles solares.

**Ventilación** (exigida por la nueva reglamentación térmica):
- Caudal ~**35 L/s (126 m³/h)** para la casa (NCh 3309 vía ECSV).
- **Opción recomendada:** ventilación mecánica **de doble flujo con recuperador de calor (HRV)**. Recupera ~80 % del calor y saca la humedad. Instalada cuesta ~$2,5–4,5 MM.
- **Opción por etapas:** dejar los **ductos instalados** en la obra gruesa y partir con extractores higrorregulables continuos en baños y cocina, más celosías de admisión en los dormitorios. El HRV se agrega después.
- **Campana de cocina con salida al exterior** y extractor del baño a ≥ 10 L/s.

---

## 3. Pasos de construcción: qué hacer primero y qué después

Cada etapa trae sus entregables, quién la hace y el costo estimado. **Regla:** no partir una etapa sin tener financiada la siguiente cuando una deja algo expuesto a la lluvia (ver las etapas 3 y 4).

### Etapa 0 — Decisiones y ahorro (mes 0, esta semana) · ≈ $0–2 MM
- [ ] Abrir la **cuenta de ahorro para la vivienda** (BancoEstado u otro) y depositar mensualmente hasta 50 UF. Los 12 meses de antigüedad son requisito del DS1.
- [ ] Verificar el **RSH** (Registro Social de Hogares) del hogar en ChileAtiende.
- [ ] Tener a mano los **títulos del terreno**: inscripción en el Conservador de Bienes Raíces de Valdivia (Mariquina), rol SII y deslindes.
- [ ] Pedir el **Certificado de Informaciones Previas (CIP)** a la DOM de Mariquina. Es barato y dice qué se puede construir.
- [ ] Pedir la **factibilidad de agua** al APR o SSR del sector y la **factibilidad eléctrica a SAESA**, preguntando por la red trifásica.
- [ ] Ir a 2–3 bancos con el CIP y preguntar por un **crédito hipotecario para construcción en sitio propio**: monto, pie y cómo se entregan los fondos (por avance de obra).

### Etapa 1 — Estudios del terreno (mes 1–3, idealmente en invierno) · ≈ $1–2 MM
- [ ] **Topografía** con curvas de nivel y deslindes (~$0,4–0,8 MM).
- [ ] **Mecánica de suelos** básica: calicata de 1,5–2 m y **test de percolación con la napa alta**, en junio–agosto (~$0,6–1,2 MM). Define el sistema de fosa y drenes; entregarla también a quien proyecte las fundaciones.

### Etapa 2 — Proyecto completo y permisos (mes 2–6) · ≈ $4–7 MM
- [ ] **Arquitecto** que:
  - ajuste el anteproyecto (las láminas actuales sirven de base);
  - firme y tramite el permiso en la **DOM en Línea**.

  Al tratarse de la vivienda del propietario en zona rural, basta el permiso de la DOM, sin informe del SAG ni de la SEREMI MINVU ([DDU 455](normas/01_permisos_urbanismo_estructura/2021_MINVU_DDU-455_Recapitulativa-art55-LGUC-area-rural.pdf)).
- [ ] **Cálculo estructural** (ingeniero civil): estructura de madera para la zona sísmica 3 y carga de los paneles solares en el techo. Las fundaciones van aparte, con las cargas de la lámina 08.
- [ ] **Especificaciones técnicas con anexo térmico:** cumplimiento del DS 15, memoria de condensación y partida de hermeticidad y ventilación.
- [ ] **Proyecto eléctrico** (instalador SEC) con la sección de paneles solares, el cargador y la domótica.
- [ ] **Proyecto sanitario** (agua potable y fosa) para la **SEREMI de Salud Los Ríos** (SEREMI en Línea).
- [ ] **Proyecto de calefacción** (piso radiante y bomba de calor) y **de ventilación**: generalmente lo entrega gratis el proveedor serio de los equipos; exigir el cálculo de la pérdida de calor.
- [ ] **Ingresar el permiso** antes de ~feb-2027 si se diseña con la NCh433 actual.
- [ ] Pagar los derechos municipales (~1,5 % del presupuesto oficial). La DOM tiene 25 días hábiles para resolver.
- [ ] **Postular al DS1** cuando haya llamado, con el permiso en mano y el ahorro listo.

> **Lo que deja el presupuesto inicial:** al terminar la etapa 2 está prácticamente usado, y bien usado. Ya tienen:
> - un proyecto aprobado que permite pedir crédito;
> - el subsidio;
> - cotizar llave en mano o por partidas;
> - evitar errores irreparables.

### Etapa 3 — Faena e interfaz con las fundaciones (temporada seca, oct–dic) · ≈ $3–6 MM sin fundaciones
- [ ] **Instalación de faena:**
  - cierre perimetral;
  - bodega con llave;
  - baño químico;
  - **empalme eléctrico provisorio** (o definitivo de inmediato si SAESA lo permite);
  - agua de obra.
- [ ] **Camino de acceso de ripio** y **zona de estacionamiento para 2 autos** (≥ 5,5 × 5,5 m), con ducto del cargador ya enterrado.
- [ ] Despeje, trazado (con el norte geográfico verificado), excavación y **drenaje perimetral** con geotextil y grava.
- [ ] **Instalaciones bajo el radier:**
  - alcantarillado con pendiente;
  - ducto del empalme;
  - ductos de agua;
  - **tubo de puesta a tierra en las fundaciones** (electrodo de fundación).
- [ ] **Fundaciones y sobrecimiento: las proyecta y ejecuta un tercero.** Entregarle por escrito:
  - las cargas de la lámina 08 y de las [memorias](calculo/MEMORIAS.pdf), cap. 1.8;
  - los ejes de muros;
  - los pernos de solera Ø12 @ ≤ 0,50 m y los hold-down;
  - las pasadas de alcantarillado y los ductos;
  - el sobrecimiento ≥ 20 cm sobre el terreno, con **aislante de borde R100 ≥ 91** (DS 15);
  - el radier **sobre EPS ≥ 80 mm y polietileno**, que es la base del piso radiante.
- [ ] Recibir el sobrecimiento **a nivel y escuadra** antes de partir la estructura de madera (tolerancia ±5 mm).

### Etapa 4 — Obra gruesa y casa cerrada al agua (ene–abr) · ≈ $45–65 MM
- [ ] Entramados de muros (madera preservada), anclajes, entrepiso y escalera estructural.
- [ ] **Techumbre completa:**
  - estructura calculada para los paneles solares;
  - **cubierta metálica**;
  - canaletas y bajadas.

  **Hito: techo cerrado antes de mayo.**
- [ ] OSB, **barrera hídrica** y **ventanas** con sellos. La casa queda "cerrada al agua".
- [ ] Aleros cerrados con rejilla y malla metálica.

### Etapa 5 — Instalaciones embutidas (may–jul, se trabaja adentro con la casa ya cerrada) · ≈ $15–25 MM
- [ ] **Eléctrica:**
  - canalizaciones;
  - cajas;
  - Cat6;
  - ducto a los paneles solares;
  - **tablero con 25 % de reserva**.
- [ ] **Agua fría y caliente** (PEX o PPR), con **prueba de presión** antes de cerrar.
- [ ] **Ductos de ventilación** (aunque el HRV se compre después).
- [ ] **Fosa séptica, drenes y estanques**, con inspección de la SEREMI de Salud.

### Etapa 6 — Aislación y hermeticidad · ≈ $8–12 MM
- [ ] Lana mineral en muros y techo.
- [ ] **Barrera de vapor** sellada con cinta.
- [ ] Cámara técnica.
- [ ] **Prueba blower door.** Si no da ≤ 5 ren/h (meta 3), sellar y repetir **antes** de forrar.

### Etapa 7 — Piso radiante y bomba de calor · ≈ $8–14 MM
- [ ] Banda perimetral, tubos PEX y colectores, **prueba de presión a 6 bar por 24 h**.
- [ ] Mortero de 5 cm.
- [ ] Instalación de la bomba de calor y el acumulador de agua caliente, con la válvula mezcladora termostática.
- [ ] **Primer encendido gradual** para secar el mortero: subir 1–2 °C por día, nunca de golpe.

### Etapa 8 — Terminaciones (por prioridad, mientras ya viven ahí) · ≈ $25–45 MM
- [ ] Revestimientos interiores: yeso-cartón RF, pintura lavable antihongos y porcelanato.
- [ ] Revestimiento exterior con fachada ventilada.
- [ ] **Núcleo habitable primero:**
  - 1 baño;
  - cocina;
  - dormitorio principal;
  - un dormitorio infantil.
- [ ] Puertas, muebles y artefactos. Mesones a 85 cm.

### Etapa 9 — Paneles solares, domótica y ventilación con recuperador (cuando haya capital) · ≈ $6–12 MM
- [ ] **Paneles solares 3,6 kWp:**
  - TE4 y net billing con SAESA;
  - inversor con AFCI;
  - diferencial de 30 mA en el inversor.
- [ ] Ventilación HRV. Domótica con Home Assistant.
- [ ] Cargador del auto con TE6.
- [ ] Más adelante, la **etapa 2 de paneles** (7,2 kWp) o una batería.

### Etapa 10 — Recepciones y regularización
- [ ] **TE1** (electricidad, SEC) → medidor definitivo.
- [ ] **Autorización de funcionamiento** de agua y alcantarillado (SEREMI de Salud).
- [ ] **Recepción final de la DOM.** Permite el avalúo fiscal y el uso legal, y la exigen los bancos y el subsidio.
- [ ] Guardar la carpeta de la obra: planos "as built", fotos de las instalaciones antes de cerrar, garantías y certificados.

**Total orientativo:** ~$130–200 MM, según la superficie final, las terminaciones y cuánto se autogestiona. Un presupuesto real sale de cotizar con el proyecto de la etapa 2.

---

## 4. Eficiencia y eficacia: reglas prácticas

1. **Comprar el proyecto antes que materiales.** Cada $1 en diseño ahorra ~$10 en obra.
2. **Cotizar 3 contratistas por partida** con las especificaciones técnicas en la mano. Contrato escrito con estados de pago por avance verificado, nunca por adelantado, y retención del 5–10 % hasta la recepción.
3. **Inspección técnica (ITO)** independiente en los hitos críticos:
   - enfierradura;
   - anclajes;
   - barrera de vapor;
   - prueba de presión;
   - blower door.

   Cuesta poco comparado con un error oculto.
4. **Fotografiar todo antes de cerrar.** Es el mapa de las instalaciones para siempre.
5. **Calendario de lluvias:** trabajos exteriores de oct a abr; interiores de may a sep.
6. **No ahorrar en lo que no se puede cambiar después:**
   - fundaciones (las proyecta y ejecuta un tercero, ver Etapa 3);
   - estructura;
   - aislación;
   - ventanas;
   - barreras;
   - ductos.

   **Sí se puede postergar:**
   - terminaciones;
   - muebles;
   - paneles solares;
   - recuperador de calor;
   - domótica.
7. **Comprar materiales por partida completa** y guardarlos protegidos de la lluvia.
8. **Mantención anual** (durabilidad):
   - limpiar canaletas en otoño;
   - revisar los sellos de las ventanas;
   - limpiar los filtros del HRV cada 3–6 meses;
   - limpiar la fosa cada 2 años;
   - limpiar los paneles solares en primavera;
   - mantener la faja de defensa contra incendio antes del verano.

---

## 5. Por confirmar (preguntas abiertas)
- El tope de ingreso del DS1 Tramo 3 para el próximo llamado (2026–2027) y las fechas de postulación.
- Si SAESA es la distribuidora del predio y si hay red trifásica cerca.
- El cupo del APR de Puringue Pobre.
- La napa y la percolación (invierno). Si es alta, se pasa a biofiltro o planta domiciliaria.
- Las exigencias específicas del Plan Regulador o de la DOM de Mariquina (las dice el CIP).
- Si se mantiene el diseño de 2 pisos (más económico por m²) o se pasa a 1 piso (más cómodo con niños pequeños y mascotas, pero más techo y fundación).

## 6. Glosario rápido
| Sigla | Qué es |
|---|---|
| OGUC / LGUC | Ordenanza y Ley General de Urbanismo y Construcciones: las reglas de toda construcción |
| DOM | Dirección de Obras Municipales: da el permiso y la recepción |
| CIP | Certificado de Informaciones Previas: lo que se puede construir en el terreno |
| SEC / TE1 / TE4 / TE6 | Superintendencia de Electricidad / declaración de la instalación eléctrica / de los paneles solares / del cargador del auto |
| RIC | Pliegos técnicos de la SEC para instalaciones eléctricas de consumo |
| RIDAA | Reglamento de instalaciones domiciliarias de agua potable y alcantarillado |
| DS 236 | Reglamento de fosas sépticas y alcantarillados particulares |
| U (W/m²K) | Transmitancia térmica: cuánto calor se escapa; mientras menor, mejor |
| m.c.a. | Metros de columna de agua: unidad de presión (10 m.c.a. ≈ 1 bar) |
| HRV | Ventilación mecánica con recuperación de calor |
| Net billing | Inyectar a la red el excedente solar y descontarlo de la cuenta |
| F-15 / F-30 | Minutos que un elemento resiste el fuego |
| APR / SSR | Agua potable rural / Servicio Sanitario Rural |
