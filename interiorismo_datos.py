# Interiorismo japandi: muebles, materialidad, iluminación y domótica (metros, mismo sistema que casa_datos.py).
# Criterios: madera clara + blanco cálido + negro carbón; nada a la vista que pueda ir guardado ("esconder");
# guardado de piso a cielo sin tiradores (push / uñero); domótica local con Home Assistant (Zigbee / Matter).
# Ergonomía 1,64 m: mesón 0,85 m, barras de clóset 1,00 / 1,65 m, muebles altos de cocina desde 1,40 m.
# Interiores a cara de muro: muro exterior 0,10 m y tabique 0,05 m desde el eje.

# ---------- MATERIALIDAD: código -> (nombre, uso, color de muestra) ----------
MATERIALES = {
    "LEN": ("Lenga aceitada (madera nativa certificada)", "Mesa, bancos, camas, vanitorios, peldaños", "#c49a6c"),
    "FRE": ("Frentes HPL mate 'lino blanco' antihuella", "Cocina, columnas, clósets y cama abatible, sin tiradores", "#e4ded3"),
    "LIN": ("Lino lavado / tela performance antimanchas", "Sofá con funda lavable, cortinas, cojines", "#d9d0c1"),
    "PIE": ("Porcelanato símil caliza mate 60×120 R10", "Piso P1 y baños; ideal para piso radiante y uñas", "#cfc7ba"),
    "PIO": ("Porcelanato piedra oscura texturada", "Genkan (entrada) y terrazas", "#77716a"),
    "MAD": ("Porcelanato símil roble claro 20×120", "Piso P2: dormitorios y pasillo", "#c8b497"),
    "MUR": ("Pintura mineral 'blanco arroz' antihongos", "Muros y cielos (clima húmedo de Los Ríos)", "#eee9e0"),
    "NEG": ("Negro carbón mate", "Grifería, rieles, manillas, telón, perfiles", "#33312e"),
    "SAL": ("Verde salvia (acento)", "Azulejo vertical en duchas, textiles, clóset dorm. 2", "#8e9b86"),
    "TER": ("Pino termotratado", "Ofuro, listones de cielo del baño, banco de ducha", "#9c7a57"),
    "SHO": ("Panel efecto washi (policarbonato, a prueba de gatos)", "Puertas correderas del walk-in y la despensa", "#f3efe6"),
    "FIE": ("Fieltro PET reciclado antracita", "Fondo acústico tras listones de lenga", "#4a4845"),
}

# ---------- MUEBLES: (código, piso, (x0, y0, x1, y1), (z0, z1), material, nombre, qué esconde) ----------
# Nombre "" = otra pieza del mueble anterior (no se rotula ni va a la tabla).
# z1 ≥ 2,0 se dibuja con aspa (guardado de piso a cielo); z1 ≤ 0,05 es una zona de piso (borde punteado).
MUEBLES = [
    # --- living / comedor / cocina (32 m²) ---
    ("L1", 1, (0.10, 2.90, 0.55, 5.60), (0, 0.45), "LEN", "Banco bajo ventana oeste con cajones",
     "Proyector láser de tiro ultracorto que sube con la escena Cine, juguetes y nicho-cama del perro"),
    ("L2", 1, (0.12, 3.10, 0.28, 5.40), (2.16, 2.36), "NEG", "Telón motorizado 100\" en cajón de cielo",
     "Reemplaza el televisor: baja frente a la ventana sólo cuando se usa"),
    ("L3", 1, (1.95, 3.00, 2.85, 5.20), (0, 0.70), "LIN", "Sofá bajo 3 cuerpos, funda lavable",
     "Cajón inferior para mantas; tela antiarañazos (gatos)"),
    ("L4", 1, (0.95, 3.60, 1.55, 4.60), (0, 0.38), "LEN", "Mesa de centro con cubierta elevable",
     "Sube a altura de trabajo; guarda controles, cargadores y libros"),
    ("C1", 1, (3.35, 3.45, 4.75, 4.35), (0, 0.75), "LEN", "Mesa comedor maciza 140×90 adosada a la isla",
     "Alas extensibles bajo la cubierta: 6 → 8 personas"),
    ("C2", 1, (3.40, 2.95, 4.70, 3.30), (0, 0.45), "LEN", "Banco-baúl del comedor (3 puestos)",
     "Individuales, servilletas y juegos de mesa"),
    ("C3", 1, (3.50, 4.45, 4.60, 4.90), (0, 0.80), "LEN", "Dos sillas de lenga con asiento de cuerda", ""),
    ("K1", 1, (4.60, 5.30, 7.95, 5.90), (0, 0.85), "FRE", "Cocina lineal norte con uñero (sin tiradores)",
     "Inducción con extractor integrado (sin campana), lavavajillas panelado, reciclaje en 4 fracciones"),
    ("K2", 1, (7.35, 3.05, 7.95, 5.30), (0, 2.36), "FRE", "Muro de columnas de piso a cielo",
     "Refrigerador panelado, horno + microondas, despensero extraíble y 'garaje' de electrodomésticos"),
    ("K3", 1, (4.75, 3.45, 6.35, 4.35), (0, 0.85), "LEN", "Isla 160×90",
     "Comedero del perro en cajón del zócalo, enchufe escamoteable, ollas en cajones"),
    # --- oficinas ---
    ("O1", 1, (2.15, 0.10, 4.00, 0.70), (0.70, 0.75), "LEN", "Escritorio flotante bajo la ventana (oficina 1)",
     "Bandeja pasacables y regleta bajo la cubierta: cero cables a la vista"),
    ("O2", 1, (4.00, 0.75, 4.35, 1.90), (0, 2.36), "FRE", "Guardado de piso a cielo (oficina 1)",
     "Impresora en bandeja extraíble y archivo"),
    ("O3", 1, (2.10, 0.75, 2.16, 1.90), (0.10, 2.26), "LEN", "Panel acústico de listones sobre fieltro",
     "Quita el eco en videollamadas y tapa las canalizaciones"),
    ("O4", 1, (9.55, 3.95, 10.00, 5.85), (0, 2.10), "FRE", "Cama abatible horizontal 140 + escritorio (oficina 2)",
     "Pieza de invitados que desaparece; el escritorio queda horizontal al bajar la cama"),
    ("G2", 1, (11.30, 3.05, 11.90, 3.35), (0, 2.20), "FRE", "Armario técnico embutido (se abre desde el pasillo)",
     "Tablero TDA, rack de red, Home Assistant, ONT y switch PoE tras puerta enrasada con rejilla"),
    # --- despensa ---
    ("D1", 1, (8.05, 3.80, 8.45, 5.95), (0, 2.30), "LEN", "Despensa en U con repisas regulables",
     "Freezer vertical bajo, alimento de mascotas en bidones herméticos, compras al por mayor"),
    ("", 1, (9.05, 3.80, 9.45, 5.95), (0, 2.30), "LEN", "", ""),
    ("", 1, (8.45, 5.55, 9.05, 5.95), (0, 2.30), "LEN", "", ""),
    # --- entrada (genkan) y escalera ---
    ("G1", 1, (10.55, 2.05, 11.95, 2.95), (0, 0.01), "PIO", "Genkan: piedra oscura + felpudo embutido",
     "Marca dónde quedan los zapatos; sin desnivel para el coche de la bebé"),
    ("G3", 1, (8.10, 2.05, 9.50, 2.25), (0.15, 1.05), "FRE", "Zapatero basculante flotante de 20 cm",
     "12–15 pares; luz LED bajo el mueble con la escena Llegada"),
    ("G4", 1, (11.88, 2.10, 11.95, 2.60), (1.40, 1.70), "LEN", "Listón con ganchos abatibles",
     "Ganchos que se pliegan al ras: abrigos, correa del perro, llaves"),
    ("E1", 1, (8.70, 1.00, 10.45, 1.95), (0, 1.26), "LEN", "Cajones kaidan-dansu en las contrahuellas",
     "7 cajones bajo los peldaños del tramo 1, con traba de niños: herramientas, pilas, linternas"),
    ("E2", 1, (7.85, 0.10, 10.45, 0.95), (0, 1.26), "FRE", "Bodega bajo la escalera (acceso desde la lavandería)",
     "Arenero de gatos con extracción VMC, base de la aspiradora robot, carro largo con maletas y cuna de viaje"),
    ("", 1, (7.85, 0.95, 8.70, 1.95), (0, 1.26), "FRE", "", ""),
    # --- lavandería y baño P1 ---
    ("V1", 1, (6.25, 0.10, 6.95, 0.75), (0, 2.36), "FRE", "Columna lavadora + secadora bomba de calor",
     "Apiladas tras puertas; libera el mesón para doblar ropa"),
    ("V2", 1, (7.20, 0.75, 7.75, 1.35), (0, 0.85), "FRE", "Lavadero bajo tapa + tendedero de techo con poleas",
     "Tapa abatible convierte el lavadero en mesón; tendedero sube al cielo"),
    ("V3", 1, (7.72, 1.40, 7.88, 1.90), (0, 0.90), "NEG", "Escotilla 50×90 con gatera microchip",
     "Acceso a la bodega E2: sólo los gatos entran al arenero"),
    ("V4", 1, (6.25, 1.50, 6.60, 1.95), (0, 0.60), "FRE", "Canasto bajo el ducto de ropa sucia", ""),
    ("B1", 1, (5.35, 0.10, 6.15, 0.55), (0.45, 0.85), "LEN", "Vanitorio flotante con cajones",
     "Espejo-botiquín embutido en el tabique; estanque del WC dentro del tabique técnico"),
    ("B2", 1, (5.35, 1.10, 6.15, 1.95), (0, 0.02), "PIE", "Ducha a ras de piso con desagüe lineal",
     "Nicho embutido; teléfono a 0,50 m para bañar al perro"),
    # --- dormitorio principal y walk-in ---
    ("P1", 2, (3.00, 3.80, 4.50, 5.70), (0, 0.35), "LEN", "Cama plataforma 150×190 baja",
     "4 cajones de 1 m bajo la plataforma (ropa de cama de temporada)"),
    ("P2", 2, (2.75, 5.70, 4.75, 5.90), (0, 0.90), "LEN", "Cabecero-repisa bajo la ventana norte",
     "LED indirecto, veladores flotantes, enchufes y cargadores inalámbricos ocultos"),
    ("P3", 2, (4.55, 4.60, 5.05, 5.50), (0, 0.80), "LEN", "Cuna colecho (primer año)",
     "Temporal: después pasa al dormitorio 3"),
    ("W1", 2, (2.10, 0.10, 2.75, 0.75), (0, 2.50), "FRE", "Mueble técnico del recuperador VMC",
     "Recuperador tras puertas con rejilla; filtros se cambian sin herramientas"),
    ("W2", 2, (2.10, 0.80, 2.70, 2.95), (0, 2.50), "LEN", "Clóset abierto doble barra (1,00 / 1,65 m)",
     "Cajonera bajo la ventana; zapatos en zócalo extraíble"),
    ("W3", 2, (2.75, 0.10, 4.35, 0.70), (0, 2.50), "LEN", "Clóset sur: cajones + barra + altillo",
     "Caja fuerte en el cajón inferior; maletas en el altillo"),
    ("W4", 2, (3.85, 1.95, 4.35, 2.95), (0, 2.50), "FRE", "Ropa blanca de la casa",
     "Sábanas y toallas de toda la familia en un solo lugar"),
    # --- dormitorio 2 (hija de 12 años) ---
    ("A1", 2, (5.55, 3.05, 6.15, 5.90), (0, 2.50), "SAL", "Clóset de muro completo, puertas push",
     "Barras a 1,40 y 1,65 m (crece con ella); hace de colchón acústico con el dormitorio principal"),
    ("A2", 2, (7.80, 3.95, 8.70, 5.85), (0, 0.45), "LEN", "Cama nido 90×190",
     "Segunda cama extraíble para pijamadas + 2 cajones"),
    ("A3", 2, (6.20, 5.30, 7.75, 5.90), (0.70, 0.75), "LEN", "Escritorio bajo la ventana + tablero de clavijas",
     "Cajonera con ruedas que se guarda bajo la cubierta"),
    # --- dormitorio 3 (bebé) ---
    ("N1", 2, (8.80, 3.05, 10.90, 3.65), (0, 2.50), "FRE", "Clóset sur con repisas regulables",
     "Hoy pañales y ropa de bebé; mañana barra y cajones"),
    ("N2", 2, (11.40, 3.95, 11.90, 4.85), (0, 0.90), "LEN", "Cómoda-mudador",
     "La bandeja mudador se retira y queda una cómoda"),
    ("N3", 2, (8.85, 4.10, 9.60, 5.50), (0, 0.90), "LEN", "Cuna convertible 70×140 → cama junior",
     "Lejos de la ventana; cajón inferior"),
    ("N4", 2, (11.10, 5.05, 11.85, 5.80), (0, 0.90), "LIN", "Sillón de lactancia + pouf", ""),
    ("N5", 2, (9.90, 4.00, 11.00, 5.00), (0, 0.03), "LIN", "Tatami de juego (EVA + yute)", ""),
    # --- baño P2 y hall ---
    ("B3", 2, (5.40, 0.10, 6.40, 0.55), (0.45, 0.85), "LEN", "Vanitorio doble flotante",
     "Espejos-botiquín embutidos con luz; estanque del WC en tabique técnico"),
    ("B4", 2, (6.65, 0.10, 7.75, 1.95), (0, 0.02), "PIE", "Zona húmeda japonesa: ducha + ofuro",
     "Ofuro 110×70×60 para bañar a los niños; piso continuo y mampara fija"),
    ("", 2, (6.65, 1.25, 7.75, 1.95), (0, 0.60), "TER", "", ""),
    ("B6", 2, (6.25, 1.50, 6.60, 1.95), (0, 0.90), "FRE", "Ducto de ropa sucia a la lavandería",
     "Tapa con traba; cae al canasto V4 bajo el mesón de la lavandería"),
    ("H1", 2, (11.45, 0.10, 11.90, 1.60), (0, 0.45), "LEN", "Banco-biblioteca del hall (rincón de lectura)",
     "Cajones con libros infantiles y mantas; repisas sobre el banco"),
]

# Puertas de seguridad de la escalera (bebé, gatos): (piso, x0, y0, x1, y1) con sensor de contacto
PUERTAS_SEGURIDAD = [(1, 9.55, 2.00, 10.45, 2.00), (2, 10.50, 0.125, 10.50, 0.975)]

# ---------- ILUMINACIÓN: (piso, [(x, y), ...], descripción) — LED regulable, blanco 2700–4000 K según la hora ----------
ILUMINACION = [
    (1, [(0.25, 2.30), (0.25, 5.75), (4.50, 5.75)], "LED indirecto en fosa de cielo del living"),
    (1, [(4.75, 3.45), (6.35, 3.45)], "Zócalo de la isla (luz de noche 5 %)"),
    (1, [(8.10, 2.25), (9.50, 2.25)], "Bajo el zapatero (escena Llegada)"),
    (1, [(10.45, 1.00), (8.70, 1.00)], "Luz en peldaños, tramo 1"),
    (1, [(8.70, 0.95), (10.45, 0.95)], "Luz en peldaños, tramo 2"),
    (2, [(2.75, 5.70), (4.75, 5.70)], "Cabecero (lectura y despertar gradual)"),
    (2, [(4.50, 2.90), (11.80, 2.90)], "Guía nocturna ámbar en zócalo del pasillo"),
    (2, [(6.70, 0.15), (7.70, 0.15)], "Nicho de la ducha"),
]

# ---------- DOMÓTICA: (piso, x, y, código) — controlador Home Assistant local en G2 ----------
DOMOTICA_TIPOS = {  # código -> (descripción, categoría)
    "HA": ("Home Assistant + rack (en G2)", "hub"),
    "PR": ("Sensor de presencia mmWave", "sensor"),
    "AM": ("Sensor ambiente T° / HR / CO₂ (zona piso radiante)", "sensor"),
    "FU": ("Sensor de fuga de agua", "seguridad"),
    "VA": ("Válvula motorizada de corte de agua", "seguridad"),
    "CE": ("Cerradura digital + videoportero", "seguridad"),
    "PS": ("Contacto en puerta de seguridad", "seguridad"),
    "MB": ("Monitor de bebé local (sin nube)", "seguridad"),
    "TE": ("Motor del telón + proyector", "actuador"),
    "GA": ("Gatera con lector de microchip", "actuador"),
    "RO": ("Base de aspiradora robot", "actuador"),
    "BO": ("Botonera de escenas (reemplaza interruptor)", "actuador"),
}
DOMOTICA = [
    (1, 11.60, 3.20, "HA"), (1, 11.25, 1.80, "CE"), (1, 11.55, 2.30, "BO"), (1, 2.35, 2.30, "BO"),
    (1, 1.50, 5.30, "PR"), (1, 6.00, 4.80, "PR"), (1, 9.00, 2.60, "PR"), (1, 5.00, 1.30, "PR"),
    (1, 6.95, 1.50, "PR"), (1, 3.40, 1.30, "PR"),
    (1, 2.60, 5.50, "AM"), (1, 3.00, 1.65, "AM"), (1, 11.00, 4.00, "AM"),
    (1, 7.40, 5.10, "FU"), (1, 6.60, 0.90, "FU"), (1, 7.45, 0.90, "FU"), (1, 5.60, 0.80, "FU"),
    (1, 11.00, -0.60, "VA"), (1, 10.00, 1.75, "PS"), (1, 0.40, 4.25, "TE"), (1, 7.55, 1.65, "GA"),
    (1, 8.20, 0.45, "RO"),
    (2, 6.50, 2.50, "PR"), (2, 11.10, 1.20, "PR"), (2, 5.20, 1.20, "PR"), (2, 3.20, 1.60, "PR"),
    (2, 2.50, 3.45, "AM"), (2, 6.60, 3.45, "AM"), (2, 9.40, 3.95, "AM"),
    (2, 7.20, 0.50, "FU"), (2, 10.75, 0.55, "PS"), (2, 9.70, 5.75, "MB"), (2, 5.20, 3.30, "BO"),
]

# ---------- ESCENAS (Home Assistant): (nombre, disparador, qué hace) ----------
ESCENAS = [
    ("Buenos días", "Alarma del celular, lun-vie", "Cortinas suben, cabecero 30 % → 100 % en 15 min, ACS ok"),
    ("Cine", "Botonera living", "Baja el telón, sube el proyector, cortinas cerradas, fosa LED 10 %"),
    ("Siesta bebé", "Botón en dorm. 3", "Timbre en silencio, pasillo P2 ámbar 5 %, VMC en modo bajo"),
    ("Llegada", "Cerradura abre con huella", "Genkan + zapatero, clima a confort, aviso si puerta seguridad abierta"),
    ("Salir", "Botonera entrada", "Apaga todo, baja temperatura 2 °C, cámaras y sensores de fuga en guardia"),
    ("Noche", "23:00 o botón cabecero", "Guía nocturna ámbar por presencia, puertas de seguridad vigiladas"),
    ("Sol a favor", "Excedente FV > 2 kW", "Secadora, lavavajillas, ACS a 60 °C y carga del auto"),
    ("Fuga", "Cualquier sensor FU", "Cierra la válvula general y avisa al celular"),
]

# ---------- RÓTULOS de recintos en las plantas amobladas (piso, texto, x, y): en zonas libres de muebles ----------
ETIQUETAS = [
    (1, "LIVING", 1.25, 5.15), (1, "COMEDOR", 4.05, 5.05), (1, "COCINA", 6.85, 4.85), (1, "OFICINA 1", 3.35, 0.95),
    (1, "BAÑO", 4.95, 1.40), (1, "LAV.", 6.70, 1.10), (1, "DESP.", 8.75, 4.70), (1, "OFICINA 2", 10.95, 4.95),
    (1, "PASILLO", 9.95, 2.62), (1, "TERRAZA", 1.00, 1.00), (1, "TERRAZA\nENTRADA", 11.25, 1.00),
    (2, "DORM. PRINCIPAL", 3.55, 3.40), (2, "DORM. 2", 6.95, 4.40), (2, "DORM. 3", 10.45, 5.45),
    (2, "WALK-IN", 3.25, 1.45), (2, "BAÑO", 5.90, 0.90), (2, "PASILLO", 6.30, 2.50), (2, "HALL", 10.95, 1.75),
]

# ---------- EQUIPOS DE DOMÓTICA por etapa: (etapa, equipos, costo referencial CLP 2026 — cotizar) ----------
EQUIPOS = [
    ("1 · Obra gruesa", "Cat6 a cada recinto, ducto de reserva, cajas profundas tras interruptores, enchufe en G2", "0,3–0,5 MM"),
    ("2 · Mudanza", "Home Assistant (mini PC) + coordinador Zigbee/Thread, cerradura digital, 6 sensores de fuga + válvula", "0,6–0,9 MM"),
    ("3 · Confort", "Sensores AM por zona, presencia mmWave, micromódulos en interruptores, contactos puertas seg.", "0,6–1,0 MM"),
    ("4 · Cuando haya capital", "Cortinas motorizadas (17 ventanas), telón + proyector UST, LED indirecto, videoportero PoE", "2,5–4,5 MM"),
]
