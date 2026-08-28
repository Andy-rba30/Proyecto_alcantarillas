# Manifiesto del registro normativo

> **Este documento se GENERA.** No se edita a mano: lo produce
> `src/normativa/manifiesto.py` desde los objetos de `src/normativa/`,
> y el test `test_el_indice_del_registro_esta_sincronizado` lo
> regenera y compara. Si difieren, lo que hay que corregir es el
> registro, no este archivo.
>
> **Por qué existe, y en qué se diferencia de `manifiesto_citas.md`.**
> Aquél es un volcado de lo que el código afirma, anclado por
> `archivo:línea` — un ancla que se rompe con cualquier inserción, que
> es de lo que salió `NOR-MAN-04`. Éste se ancla por **id de objeto**,
> y por eso no puede desincronizarse en silencio: o lo regenera el
> generador, o el test falla.

## 1. Fuentes

Las que están en `normas/`, con el SHA-1 exacto contra el que se
verificó cada cita y la regla de paginación MEDIDA, no supuesta.

| id | Documento | Edición | Paginación (pdf ← impresa) | Páginas | SHA-1 | Texto extraíble |
|---|---|---|---|---|---|---|
| `AASHTO_LRFD_9` | AASHTO LRFD Bridge Design Specifications | Ninth Edition, 2020 | por capítulo: 1=15, 10=1289, 11=1469, 12=1638, 13=1750, 14=1782, 15=1872, 2=24, 3=54, 4=251, 5=359, 6=706, 7=1134, 8=1197, 9=1239 | 1905 | `71f4ced4c80f58db75a0bcdf4ac6b5d86dc0f858` | sí |
| `AASHTO_M170M` | AASHTO M 170M-04 «Standard Specification for Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe [Metric]» | M 170M-04 | por capítulo: M 170M=0 | 23 | `dcc40c0e5e9c99ad9f18490fa8c5b2d9394faa51` | **no** |
| `AASHTO_M36` | AASHTO M 36 «Corrugated Steel Pipe, Metallic-Coated, for Sewers and Drains» | M 36 | corrida, +1 | 24 | `f85b5658385ae6779dde4e5fd340ac3122b62636` | **no** |
| `ASTM_A760` | ASTM A760/A760M-10 «Especificacion Estandar para Tuberia de Acero Corrugado, con Recubrimiento Metalico, para Alcantarillas y Drenajes» | A760/A760M-10 | corrida, +0 | 15 | `47d0d447143ca158615dff7dec79f2f7a8975732` | **no** |
| `E030` | Norma Tecnica E.030 «Diseño Sismorresistente» | Edicion 2026, publicada en el diario oficial El Peruano | corrida, +0 | 68 | `fe0a58e4be4b8709324e65ed6ad0c25b8e0b6899` | sí |
| `E050` | Norma Tecnica E.050 «Suelos y Cimentaciones» | Edicion 2018 | corrida, +0 | 82 | `5fac1ecd997a6d6e80bcbf0967f89f9ddcc8106c` | sí |
| `E060` | Norma Tecnica E.060 «Concreto Armado» | Edicion 2009 | corrida, +0 | 205 | `cffe0efffc767f5d06a33e1f4eed3a16a01bdd81` | sí |
| `EG2013` | Manual de Carreteras "Especificaciones Tecnicas Generales para Construccion" (EG-2013) | Version revisada y corregida a junio 2013 | corrida, +8 | 1282 | `e35681d06b13226744324bc6b242b608ca9fa3ba` | sí |
| `HDS5_3ED` | HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-HIF-12-026) | Third Edition, April 2012 | por capítulo: 1=38, 2=62, 3=82, 4=126, 5=136, 6=162, 7=181, A=189, B=202, C=210, DG1=271, DG2=285, DG3=293, DG4=312 | 323 | `7b985e047c615b765e7c41b6ff12df0505c02ce4` | sí |
| `HDS5_SI_1985` | HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-IP-85-15), copia rotulada «SI» por sus cartas metricas | September 1985 | **sin determinar** | 410 | `59c6623c78793f7f947b7095027096b86f88ddf0` | sí |
| `MC_HHD` | Manual de Hidrologia, Hidraulica y Drenaje | Version Libro | corrida, +3 | 225 | `a31e853b8171b931863d7afa4379bbbc57cacb0d` | sí |
| `MP` | Manual de Puentes | Version Libro | corrida, +1 | 673 | `67a7a9f1c61cad8f9ca179cd4ca777f96b49dc44` | sí |
| `MS` | Manual de Carreteras: Suelos, Geologia, Geotecnia y Pavimentos — Seccion Suelos y Pavimentos | Version abril 2014 | corrida, +1 | 281 | `21d19a71090c1e586cd31596db8a4d007dc7b96f` | sí |

## 2. Fuentes que se citan y NO están en `normas/`

Ordenadas por lo que cuesta traerlas, para que la deuda se vea sin
leer la §15 del plan. **Ninguna puede sostener un `[N]`**: la etiqueta
exige numeral verificado, y aquí no hay contra qué verificar.

| id | Documento | Esfuerzo | Qué desbloquearía | Sustituto vigente |
|---|---|---|---|---|
| `DG2018` | Manual de Carreteras: Diseño Geometrico DG-2018 | facil, es descarga publica | 'clase_de_via' y con ella 'carriles_por_sentido': hoy el Cuadro 4.1 no se puede aplicar sin declararlos | datos de sitio declarados por el proyectista |
| `HEC14` | HEC-14 «Hydraulic Design of Energy Dissipators for Culverts and Channels» | facil, es descarga publica | el dimensionamiento de disipadores, fuera de alcance hoy | Laushey (num. 4.1.1.3.7 c) del Manual) para d50 |
| `LEY_29338` | Ley 29338, Ley de Recursos Hidricos, y su reglamento | facil, es descarga publica | el tramite, no el calculo | — |
| `WSDOT_HM` | WSDOT Hydraulics Manual | facil, es descarga publica | 'v_max_tmc' y 'v_max_hdpe', hoy [C] sin PDF | los dos criterios siguen [C] y la ventana los rotula «fuente no disponible en el expediente» |
| `AASHTO_M294` | AASHTO M 294 «Corrugated Polyethylene Pipe, 300- to 1500-mm Diameter» | compra o suscripcion | D_max['hdpe']: hoy es tope de CATALOGO ([A], criterio 'D_max_catalogo') porque la norma que lo sostendria no esta. La otra ausencia barata | Catalogo CAT_TUBERIA_LOCAL, rotulado como tal |
| `ASTM_A796` | ASTM A796/A796M «Structural Design of Corrugated Steel Pipe...» | compra o suscripcion | la mitad TMC de 'clases_producto_por_relleno'. Es una de las DOS ausencias baratas del plan | el criterio queda [A] y declara el vacio |
| `ASTM_A798` | ASTM A798/A798M «Installing Factory-Made Corrugated Steel Pipe for Sewers and Other Applications» | compra o suscripcion | nada que el EG-2013 no cubra ya para obra vial peruana | EG-2013 Seccion 507 |
| `ASTM_A807` | ASTM A-807 (la designacion que la hoja de ruta atribuye al calibre de TMC por altura de relleno) | compra o suscripcion | nada: la remision es FALSA. El calibre por altura de cobertura es de ASTM A796/A796M. Queda declarada como discrepancia abierta contra la hoja de ruta | ninguno; la remision se retira, no se sustituye |
| `ASTM_C76` | ASTM C76 «Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe» | compra o suscripcion | nada nuevo: AASHTO M 170M-04, que SI esta, tabula de 300 a 3600 mm y ya desmiente el tope | AASHTO M 170M-04, presente en normas/ |
| `APENDICE_A3_MP` | Manual de Puentes, Apendice A3: mapas de isoaceleracion | gabinete | nada por la via de conseguirlo: el apendice SI esta en el PDF. Lo que no se puede es leer la isolinea por texto | datos_sitio['PGA_roca_B'], [S] con la lectura del mapa declarada y verificable por imagen |
| `MEYERHOF_1957` | Meyerhof, G. G. (1957), abacos de N_cq y N_gamma_q | gabinete | nada nuevo: los abacos SI estan, reproducidos en el Manual de Puentes. Lo que no se puede es leerlos por texto — son raster | Manual de Puentes num. 2.8.1.3.1.2c. NO es un caso de fuente ausente sino de fuente presente ilegible por texto: la lectura del abaco se declara [S] y se verifica por imagen |
| `SERIES_SENAMHI_ANA` | Series hidrometeorologicas SENAMHI / ANA para la cuenca del corredor | gabinete | el Q de la Familia A, hoy bloqueado. Es la ausencia mas cara del expediente | ninguno: el calculo se detiene, y debe |
| `ESTUDIO_GEOTECNICO` | Estudio de Mecanica de Suelos (EMS) del expediente | de campo | toda la durabilidad del concreto (y con ella el recubrimiento), la clase de sitio sismica y el resguardo de la napa | ninguno: los criterios valen None y bloquean |

## 3. Catálogos, que NO son fuentes

Un tope de catálogo no tiene numeral, y el registro no le deja fingir
que lo tiene: un `Catalogo` no puede ser el `fuente_id` de una cita.

- **`CAT_TUBERIA_LOCAL` — Catalogo de conductos disponibles para el corredor** (oferta comercial y capacidad de transporte a la obra (La Union, Piura)).
  Qué norma NO lo sostiene: NINGUNA. Los topes 2.70 / 2.10 / 1.50 m se atribuian a «ASTM C76 / AASHTO M170», «AASHTO M36 / ASTM A760» y «AASHTO M294», y las dos primeras atribuciones estan verificadas EN CONTRA sobre los PDF de normas/: ASTM A760/A760M-10 tabula de 100 a 3600 mm y AASHTO M 170M-04 de 300 a 3600 mm con diseños especiales por encima. La tercera no se pudo contrastar porque M294 no esta. Un tope de catalogo no tiene numeral, y descartaba material en silencio con una cita que ninguna norma sostiene (NOR-PRO-01, NOR-PRO-02, MAT-O8)

## 4. Citas

Una fila por objeto `Cita`. El `id` es el ancla: no hay número de
línea que se pueda romper.

### AASHTO LRFD Bridge Design Specifications  (`AASHTO_LRFD_9`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `AASHTO_LRFD_9.3.11.6.4` | 3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.3.11.6.4#ALTURA` | 3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.3.11.6.4#APLICA` | 3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.C3.11.6.4` | C3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | definicion | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.T3.11.6.4-1` | Table 3.11.6.4-1 | «Equivalent Height of Soil for Vehicular Loading on Abutments Perpendicular to Traffic» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.T3.11.6.4-2` | Table 3.11.6.4-2 | «Equivalent Height of Soil for Vehicular Loading on Retaining Walls Parallel to Traffic» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |

> **`AASHTO_LRFD_9.3.11.6.4`** — El articulo entero, sus dos tablas y su comentario C3.11.6.4 caben en la pag. impresa 3-151; no continua en la 3-152, donde empieza el 3.11.6.5. La frase de la interpolacion es EXIGENCIA («shall»); la de tomar valores de las tablas es PERMISO («may be taken»).

> **`AASHTO_LRFD_9.3.11.6.4#ALTURA`** — La altura que entra en las tablas NO es la altura visible del muro: incluye la zapata. Con `GeometriaCabezal` eso es H + espesor_zapata. Medirla sin la zapata SUBESTIMA la altura y, como h_eq decrece con ella, SOBRESTIMA h_eq -- conservador, pero es la lectura equivocada de la tabla.

> **`AASHTO_LRFD_9.C3.11.6.4`** — HALLAZGO DE S12, y es el que obliga a matizar el conflicto #4: NO EXISTE en el articulado ninguna frase que reparta las dos tablas. El cuerpo normativo las cita JUNTAS Y SIN CONDICIONANTE («may be taken from Tables 3.11.6.4-1 and 3.11.6.4-2»). Lo que las reparte son (a) los TITULOS de las tablas y (b) este comentario, que no es articulado. Y no ofrecen un eje libre «orientacion»: ofrecen dos BINOMIOS ACOPLADOS -- estribo+perpendicular y muro de contencion+paralelo --. No hay tabla para «muro perpendicular» ni para «estribo paralelo».

> **`AASHTO_LRFD_9.T3.11.6.4-1`** — Su variable de entrada se llama literalmente «Abutment Height (ft)»: es una tabla de ESTRIBOS. Aplicarla a un cabezal de alcantarilla es analogia declarada, no lectura directa.

> **`AASHTO_LRFD_9.T3.11.6.4-2`** — Encabezado de DOS niveles: sobre las columnas 2 y 3 va «heq (ft) Distance from wall backface to edge of traffic», y bajo el «0.0 ft» y «1.0 ft or Further». El umbral es UNA PULGADA-PIE EXACTA: 1.0 ft = 0.3048 m, no 0.30 m. Redondearlo a 0.30 relaja el criterio y va del lado inseguro.

### Manual de Hidrologia, Hidraulica y Drenaje  (`MC_HHD`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `MC_HHD.3.12.5#G` | 3.12.5 | «Otras Metodologías» | pág. impresa **63** · PDF 66 | definicion | 2026-08-28 · ambos |
| `MC_HHD.3.6` | 3.6 | «Selección del Período de Retorno» | pág. impresa **25** · PDF 28 | recomendacion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.1` | 4.1.1.3.1 | «Aspectos generales» | pág. impresa **70** · PDF 73 | definicion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.4a` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **72** · PDF 75 | exigencia | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.5` | 4.1.1.3.5 | «Recomendaciones y factores a tomar en cuenta para el diseño de una alcantarilla» | pág. impresa **73** · PDF 76 | recomendacion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.6` | 4.1.1.3.6 | «Diseño hidráulico» | pág. impresa **74** · PDF 77 | definicion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.6#T09` | 4.1.1.3.6, Tabla Nº 09 | «Diseño hidráulico» | pág. impresa **75** · PDF 78 | definicion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.6#T10` | 4.1.1.3.6, Tabla Nº 10 | «Diseño hidráulico» | pág. impresa **76** · PDF 79 | exigencia | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.6#VMIN` | 4.1.1.3.6, párrafo posterior a la Tabla Nº 10 | «Diseño hidráulico» | pág. impresa **77** · PDF 80 | recomendacion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.7a` | 4.1.1.3.7 a) | 4.1.1.3.7  Consideraciones para el diseño › «a)   Material sólido de arrastre» | pág. impresa **79** · PDF 82 | recomendacion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.7b` | 4.1.1.3.7 b) | 4.1.1.3.7  Consideraciones para el diseño › «b)  Borde libre» | pág. impresa **79** · PDF 82 | recomendacion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.7c` | 4.1.1.3.7 c), ec. (49) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **80** · PDF 83 | aproximacion | 2026-08-28 · imagen renderizada |
| `MC_HHD.4.1.1.3.7c#G` | 4.1.1.3.7 c), lista de variables de la ec. (49) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **80** · PDF 83 | definicion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.5.1` | 4.1.1.5.1 | 4.1.1.5  PUENTES › «Aspectos generales» | pág. impresa **87** · PDF 90 | definicion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.5.4b24#G` | 4.1.1.5.4 b.2.4), ec. (63) | b.2.) Socavación General › «Método de Laursen» | pág. impresa **111** · PDF 114 | definicion | 2026-08-28 · ambos |
| `MC_HHD.4.1.2.1d` | 4.1.2.1 d) | 4.1.2.1 Cunetas › «d) Desagüe de las cunetas» | pág. impresa **179** · PDF 182 | exigencia | 2026-08-28 · ambos |

> **`MC_HHD.3.12.5#G`** — Primera de las DOS paginas del Manual donde 9.8 figura como gravedad.

> **`MC_HHD.3.6`** — El numeral abre en la pag. impresa 23 (PDF 26); la Tabla Nº 02 y este parrafo estan en la 25 (PDF 28).

> **`MC_HHD.4.1.1.3.5`** — Se declara aunque el proyecto no tome ningun valor de el: es el numeral con el que se confundio la Tabla Nº 09 antes de S5, y tenerlo escrito con su titulo es lo que impide repetir la confusion. NO contiene ninguna tabla de rugosidad.

> **`MC_HHD.4.1.1.3.6#T09`** — La tabla ocupa dos paginas impresas: los grupos A, B y C en la 75 (PDF 78) y el grupo D con la linea de Fuente en la 76 (PDF 79).

> **`MC_HHD.4.1.1.3.6#T10`** — El titulo se imprime en DOS renglones y el segundo dice solo «revestidos»; el `texto_literal` es el primero, que es el que se puede buscar de corrido. El titulo completo esta en `TablaNormativa.titulo_literal`.

> **`MC_HHD.4.1.1.3.6#VMIN`** — El parrafo cruza el salto de pagina: arranca en la impresa 76 («Se deberá verificar que la velocidad mínima del flujo dentro del conducto no produzca sedimentación que pueda incidir en una») y el numero se imprime en la 77. El `texto_literal` es la mitad que contiene el valor, porque es la que T5 tiene que poder encontrar en la pagina que la cita declara.

> **`MC_HHD.4.1.1.3.7a`** — Las CUATRO caracteristicas a las que «el párrafo anterior» remite estan en la pag. impresa 78 (PDF 81), no en la 79: la cita del repositorio decia solo «pag. 79» y con eso el condicionante quedaba fuera del rango citado. El rango correcto es 78-79. El valor 1.22 m NO esta en la fuente: el Manual escribe «Ф 48”» y la conversion (48 in = 1.2192 m) es del proyecto.

> **`MC_HHD.4.1.1.3.7b`** — El 0.75 que el codigo usa es la DERIVACION aritmetica de este 25 % (1 - 0.25), no una cifra impresa; y la fuente no escribe «y/D» sino «la altura, diámetro o flecha de la estructura». La frase inmediatamente anterior SI es prohibitiva («las alcantarillas no deben ser diseñadas para trabajar a sección llena») pero prohibe la seccion llena, no fija el 25 %.

> **`MC_HHD.4.1.1.3.7c`** — La ec. (49) es d50 = V² / (3.1 g). La extraccion de texto la devuelve desordenada («) 1.3 ( 2 50 g V d =») por el orden de trazado, de modo que la lectura fiable es la de la pagina renderizada: el metodo de esta cita es IMAGEN y decirlo es parte de la verificacion.

> **`MC_HHD.4.1.1.3.7c#G`** — NOR-HID-01 / MAT-O7. ESTE NUMERAL NO ESCRIBE NINGUN VALOR DE g: define el simbolo y su unidad. El 9.8 que el proyecto usa SI esta en el Manual, en otros dos numerales (ver MC_HHD.3.12.5 y MC_HHD.4.1.1.5.4b24), y el 9.81 no aparece ni una vez en las 225 paginas. Se corrige la ATRIBUCION, no el numero.

> **`MC_HHD.4.1.1.5.1`** — NOR-HID-05, cerrado: el numeral ARRANCA en la pag. impresa 86 (PDF 89) y la frase que sostiene el valor esta en la 87 (PDF 90). La cita anterior decia «pag. 88», donde el Manual imprime «a.1) Topografía – Batimetría del cauce y zonas adyacentes», del num. 4.1.1.5.2.

> **`MC_HHD.4.1.1.5.4b24#G`** — Segunda y ultima pagina del Manual donde 9.8 figura como gravedad. Es socavacion general por contraccion en PUENTES, no la de salida de alcantarilla: sostiene el NUMERO, no el numeral de Laushey.

> **`MC_HHD.4.1.2.1d`** — NOR-HID-02, cerrado en sus DOS extremos. (1) LA PAGINA: el repositorio citaba la impresa 178, que trae la TABLA Nº 34 de dimensiones minimas del apartado c); el apartado d) esta en la 179. (2) EL CARACTER: las dos cifras NO tienen la misma fuerza. El 250 es «será ... como máximo», exigencia con valvula de escape expresa («deberán justificarse técnicamente»); el 200 es «se recomienda reducir», recomendacion pura. Tratarlas como un dict de topes duros equivalentes borra la diferencia. Ademas la fuente nombra solo DOS regimenes en este apartado y deja sin longitud el regimen «lluvioso» intermedio de su propia Tabla Nº 34.

### Manual de Puentes  (`MP`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `MP.2.1.4.3.9` | 2.1.4.3.9 | «Aparatos de Apoyo» | pág. impresa **91** · PDF 92 | exigencia | 2026-08-28 · ambos |
| `MP.2.4.2.2#SOBRECARGA` | 2.4.2.2 | «Cargas de Suelo: EH, ES, y DD» | pág. impresa **102** · PDF 103 | exigencia | 2026-08-28 · ambos |

> **`MP.2.1.4.3.9`** — NOR-PUE-01 / MAT-D5. ESTE NUMERAL NO SOSTIENE LA SOBRECARGA DE TRASDOS y esta aqui para que se vea que no la sostiene. No contiene la palabra «sobrecarga», ni «trasdós», ni «relleno equivalente», ni el valor 0.60: va de aparatos de apoyo (bearings), y su contexto lo confirma (2.1.4.3.7 Drenaje, 2.1.4.3.8 Pavimentación, 2.1.4.3.9 Aparatos de Apoyo, 2.1.5 Señalización). El texto que si sostiene la sobrecarga esta en el num. 2.4.2.2 — ver MP.2.4.2.2#SOBRECARGA. El numeral falso estaba propagado a seis puntos del repositorio.

> **`MP.2.4.2.2#SOBRECARGA`** — EL 0.60 ES UN PISO, NO UN VALOR DE DISEÑO: la fuente dice «no menor que». Y esta expresado como ALTURA DE RELLENO EQUIVALENTE, no como presion: el paso a p = γ·0.60·Ka es derivacion del proyectista, correcta pero no escrita en este numeral. El titulo del numeral nombra EH, ES y DD y NO incluye LS.

### Manual de Carreteras: Suelos, Geologia, Geotecnia y Pavimentos — Seccion Suelos y Pavimentos  (`MS`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `MS.3.2.1` | 3.2.1 | «Terraplén» | pág. impresa **24** · PDF 25 | exigencia | 2026-08-28 · texto |
| `MS.3.2.2` | 3.2.2 | «Corte» | pág. impresa **24** · PDF 25 | exigencia | 2026-08-28 · texto |
| `MS.3.3` | 3.3 | «Sub rasante del camino» | pág. impresa **24** · PDF 25 | exigencia | 2026-08-28 · texto |
| `MS.4.2` | 4.2 | «Caracterización de la sub rasante» | pág. impresa **28** · PDF 29 | exigencia | 2026-08-28 · ambos |
| `MS.4.2#C41` | 4.2, Cuadro 4.1 | «Caracterización de la sub rasante» | pág. impresa **28** · PDF 29 | exigencia | 2026-08-28 · ambos |
| `MS.4.2#PERFIL` | 4.2, párrafo posterior al Cuadro 4.1 | «Caracterización de la sub rasante» | pág. impresa **29** · PDF 30 | exigencia | 2026-08-28 · texto |
| `MS.4.4#C411` | Cuadro 4.11 | «Cuadro 4.11 Categorías de Sub rasante» | pág. impresa **37** · PDF 38 | definicion | 2026-08-28 · texto |
| `MS.4.5.4` | 4.5.4 | «Sub rasante» | pág. impresa **42** · PDF 43 | exigencia | 2026-08-28 · texto |
| `MS.9.1.1` | 9.1, apartado 1) | «Criterios geotécnicos para establecer la estabilización de suelos» | pág. impresa **89** · PDF 90 | exigencia | 2026-08-28 · texto |
| `MS.9.1.3` | 9.1, apartado 3) | «Criterios geotécnicos para establecer la estabilización de suelos» | pág. impresa **89** · PDF 90 | exigencia | 2026-08-28 · texto |

> **`MS.3.2.1`** — NOR-SUE-03: ES EL UNICO DE LOS CUATRO NUMERALES QUE EL REPOSITORIO CITABA QUE SOSTIENE LOS DOS VALORES. El 3.2.2 «Corte» y el 3.3 «Sub rasante del camino» traen un 95 % de OTRO elemento (fondo de excavacion escarificado, y ultimos 0.30 m bajo la subrasante) y ningun 90 %; el 9.1(1) no contiene ningun porcentaje de compactacion.

> **`MS.3.2.2`** — Su 95 % es el del FONDO DE EXCAVACION EN CORTE, escarificado 0.15 m: no es el de la corona del terraplen. No contiene el 90 %.

> **`MS.3.3`** — Sostiene CBR_MIN_SUBRASANTE = 6.0 %, no la compactacion del cuerpo. Y el 6 % TAMPOCO es umbral binario: el mismo numeral da salida por estabilizacion, reemplazo, elevacion de rasante o cambio de trazo.

> **`MS.4.2#C41`** — El Cuadro entero cabe en una sola pagina impresa; no se parte. NOR-SUE-01: SI condiciona el numero por CARRILES POR SENTIDO, y la cadena «4 (o 6)» que el repositorio le atribuia no existe en ninguna celda.

> **`MS.4.2#PERFIL`** — NOR-SUE-02, cerrado en sus dos extremos. (1) NO ESTA EN EL CUADRO 4.1: el Cuadro no contiene ninguna celda con 4.0 km ni con 2.0 km, solo «x km». El 4.0 vive en este parrafo de la pag. impresa 29. (2) ES CONDICIONAL DOS VECES: solo para estudios a nivel de perfil, y solo «de no existir información secundaria» -- el orden de prelacion impreso es usar primero la informacion secundaria. El mismo parrafo fija ademas 2.0 km para factibilidad y prefactibilidad, que el repositorio no recoge.

> **`MS.4.4#C411`** — LA PAGINA LA CORRIGIO LA GUARDIA, no el verificador: el informe de verificacion daba la impresa 38 (PDF 39) y el test T2 la rechazo porque el texto no estaba ahi. El Cuadro 4.11 se imprime en la pag. impresa 37 (PDF 38); la 38 trae la Figura 4.1 de correlaciones. Es exactamente para lo que existe T2. ERRATA DE LA PROPIA FUENTE, hallada al verificar: el num. 4.5.4 remite «al cuadro 4.10» para la categoria de sub rasante, pero el Cuadro 4.10 (pag. impresa 36) es «Clasificación de los suelos basada en AASHTO M 145 y/o ASTM D 3282». La tabla de categorias es esta, el Cuadro 4.11. Sin efecto sobre los cuatro escalones del resguardo, que el propio 4.5.4 enuncia con sus intervalos.

> **`MS.4.5.4`** — NOR-SUE-05, cerrado en sus dos extremos. (1) NO ES UNA TABLA: es PROSA CORRIDA, y el numeral arranca en la pag. impresa 41 mientras este parrafo esta en la 42. (2) «RESGUARDO» NO ES PALABRA DEL MANUAL: aparece UNA sola vez en las 281 paginas, en la impresa 56, y en el sentido de «al resguardo de la luz» para conservar muestras. El Manual lo llama «quedar encima del nivel de la napa freática como mínimo a X m». (3) LA FUENTE OFRECE REMEDIO: la ultima oracion del mismo parrafo autoriza subdrenes, capas anticontaminantes o drenantes, o elevar la rasante. Tratarlo como umbral duro de rechazo endurece a la fuente.

> **`MS.9.1.1`** — NOR-SUE-03: ES EL NUMERAL QUE NO CONTIENE NINGUNO DE LOS DOS VALORES DE COMPACTACION. No imprime ni 0.95 ni 0.90 ni ningun porcentaje: va de CBR ≥ 6 % y de alternativas de estabilizacion. Sostiene CBR_MIN_SUBRASANTE, no COMPACTACION_*.

> **`MS.9.1.3`** — El apartado 3) CRUZA EL SALTO DE PAGINA: arranca en la impresa 89 (PDF 90) y termina en la 90 (PDF 91), donde se imprimen el 1.00 m, el 1.20 m y la frase de los remedios («En caso necesario, se colocarán subdrenes o capas anticontaminantes y/o drenantes o se elevará la rasante hasta el nivel necesario»). El `texto_literal` es la mitad que cabe en la pagina que la cita declara, porque es la que T2 tiene que poder encontrar ahi. Segunda ocurrencia de la MISMA regla, con las mismas cuatro cifras, y con tres diferencias literales: dice «La superficie» donde el 4.5.4 dice «El nivel superior», dice «extraordinaria y muy buena» donde aquel dice «excelente - muy buena», y NO enuncia los intervalos numericos de CBR. Los intervalos solo estan en el 4.5.4, y por eso la cita del proyecto al 4.5.4 es la correcta.

## 5. Tablas normativas

El rótulo de completitud **no lo escribe nadie**: lo deriva la tabla de
sus campos `alcance` y `uso`, de modo que no puede contradecirlos.

### `AASHTO_LRFD_9.T3.11.6.4-1` — Table 3.11.6.4-1—Equivalent Height of Soil for Vehicular Loading on Abutments Perpendicular to Traffic

- Cita: `AASHTO_LRFD_9.T3.11.6.4-1`
- Tabla completa · el calculo usa 2 de 2 columnas y 3 de 3 filas
- **Laguna de la fuente**: los muros de MENOS de 5.0 ft (1.524 m): la tabla arranca en 5.0 y la interpolacion que la fuente exige es «for intermediate wall heights», o sea ENTRE filas. Por debajo de 5.0 no hay fila con que interpolar y extrapolar no lo autoriza nadie. Se cierra con: el proyecto adopta el h_eq de la primera fila (4.0 ft) para toda altura menor, que es el lado conservador porque h_eq DECRECE con la altura (`criterios_adoptados['h_eq_bajo_altura_tabulada']`)
- Vistas de cálculo derivadas: `H_EQ_ESTRIBO_PERPENDICULAR_FT`

| Fila | Abutment Height (ft) | heq (ft) | Uso |
|---|---|---|---|
| 5.0 | 5.0 | 4.0 | usada |
| 10.0 | 10.0 | 3.0 | usada |
| ≥20.0 | 20.0 | 2.0 | usada |

### `AASHTO_LRFD_9.T3.11.6.4-2` — Table 3.11.6.4-2—Equivalent Height of Soil for Vehicular Loading on Retaining Walls Parallel to Traffic

- Cita: `AASHTO_LRFD_9.T3.11.6.4-2`
- Tabla completa · el calculo usa 3 de 3 columnas y 3 de 3 filas
- **Laguna de la fuente**: la banda 0.0 ft < distancia < 1.0 ft. La fuente manda interpolar «for intermediate wall HEIGHTS» -- entre filas -- y NO autoriza interpolar entre estas dos columnas. Se cierra con: el proyecto lee la columna «0.0 ft», que es el lado conservador, para toda distancia menor de 1.0 ft (`criterios_adoptados['h_eq_banda_intermedia_borde']`)
- **Laguna de la fuente**: los muros de menos de 5.0 ft (1.524 m). Se cierra con: el h_eq de la primera fila para toda altura menor: h_eq decrece con la altura y por debajo de 5.0 ft no hay fila con que interpolar (`criterios_adoptados['h_eq_bajo_altura_tabulada']`)
- Vistas de cálculo derivadas: `H_EQ_MURO_PARALELO_FT`

| Fila | Retaining Wall Height (ft) | 0.0 ft | 1.0 ft or Further | Uso |
|---|---|---|---|---|
| 5.0 | 5.0 | 5.0 | 2.0 | usada |
| 10.0 | 10.0 | 3.5 | 2.0 | usada |
| ≥20.0 | 20.0 | 2.0 | 2.0 | usada |

### `MC_HHD.T02` — TABLA Nº 02: VALORES  MAXIMOS RECOMENDADOS DE RIESGO ADMISIBLE DE OBRAS DE DRENAJE

- Cita: `MC_HHD.3.6`
- Tabla completa · el calculo usa 3 de 3 columnas y 2 de 6 filas
- Vistas de cálculo derivadas: `TABLA_02_FILAS`, `RIESGO_ADMISIBLE`

| Fila | TIPO DE OBRA | RIESGO ADMISIBLE (**) ( %) | (**) Vida Útil considerado (n) | Uso |
|---|---|---|---|---|
| Puentes (*) | Puentes (*) | 25 | 40 | no usada |
| Alcantarillas de paso de quebradas importantes y badenes | Alcantarillas de paso de quebradas importantes y badenes | 30 | 25 | usada |
| Alcantarillas de paso quebradas menores y descarga de agua de cunetas | Alcantarillas de paso quebradas menores y descarga de agua de cunetas | 35 | 15 | usada |
| Drenaje de la plataforma (a nivel longitudinal) | Drenaje de la plataforma (a nivel longitudinal) | 40 | 15 | no usada |
| Subdrenes | Subdrenes | 40 | 15 | no usada |
| Defensas Ribereñas | Defensas Ribereñas | 25 | 40 | no usada |

> (*) (*)   - Para obtención de la luz y nivel de aguas máximas extraordinarias. - Se recomienda un período de retorno T de 500 años para el cálculo de socavación.

> (**) (**) - Vida Útil considerado (n) • Puentes y Defensas Ribereñas n= 40 años. •  Alcantarillas de quebradas importantes n= 25 años. •  Alcantarillas de quebradas menores n= 15 años. • Drenaje de plataforma y Sub-drenes n= 15 años.

>  Se tendrá en cuenta,  la importancia y la vida útil de la obra a diseñarse.

>  El Propietario de una Obra es el que define el riesgo admisible de falla y la vida útil de las obras.

### `MC_HHD.T09` — TABLA  Nº  09:  Valores del Coeficiente de Rugosidad de Manning (n)

- Cita: `MC_HHD.4.1.1.3.6#T09`
- Transcripcion acotada · el calculo usa 3 de 4 columnas y 2 de 4 filas
- Fuente que la tabla se atribuye: *Hidráulica de Canales Abiertos, Ven Te Chow, 1983.*
- **Transcripción acotada.** Razón: el grupo A es el unico de la tabla que describe una alcantarilla; los grupos B (canales revestidos o desarmables), C (excavado o dragado) y D (corrientes naturales) describen el CAUCE, no el conducto, y ningun modulo dimensiona un cauce. Dentro del grupo A se transcriben las cuatro subfilas que el catalogo de la Sec. 3.2 puede alcanzar
  - Qué queda fuera: del grupo A: «a. Bronce Polido», «b. Acero» (soldado, con remaches) y las seis subfilas restantes de «a. Concreto» y «b. Madera», mas «c. Albañilería de piedra.». Fuera del grupo A: «B.CANALES REVESTIDOS», «C. EXCAVADO» y «D. CORRIENTES NATURALES»
  - Dónde leerlo: MC_HHD, num. 4.1.1.3.6, Tabla Nº 09: los grupos A, B y C en la pag. impresa 75 (PDF 78) y el grupo D con la linea de Fuente en la 76 (PDF 79)
- Columna «NORMAL» transcrita y **no usada**: la regla de doble n (Sec. 4.1 de la hoja de ruta) no pide el valor corriente sino los dos EXTREMOS -- n maximo para capacidad y tirante, n minimo para velocidad maxima y socavacion --, de modo que cada verificacion se resuelve con el extremo que la deja del lado seguro. El valor NORMAL entraria en un calculo de un solo n, que es justo lo que la regla prohibe
- **Afirmación negativa**: la Tabla Nº 09 no lista HDPE. Ámbito barrido: las 225 paginas del PDF: «HDPE» aparece 0 veces y «polietileno» solo en la pag. impresa 71 (listado de tipos de alcantarilla) y en la de subdrenes. Ninguna fila de la Tabla Nº 09 lo nombra
- **Errata declarada**: `DIS-MCHHD-T09-A2-DESPLAZADA`
- Vistas de cálculo derivadas: `TABLA_09_FILAS`, `MANNING`

| Fila | TIPO DE CANAL | MÍNIMO | NORMAL | MÁXIMO | Uso |
|---|---|---|---|---|---|
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.1. METÁLICOS -- c. Metal corrugado -- sub - dren |  | 0.017 | 0.019 | 0.021 | no usada |
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.1. METÁLICOS -- c. Metal corrugado -- dren para aguas lluvias |  | 0.021 | 0.024 | 0.03 | usada |
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.2 NO METÁLICOS -- a. Concreto -- tubo recto y libre de basuras |  | 0.01 | 0.011 | 0.013 | usada |
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.2 NO METÁLICOS -- b. Madera -- duelas |  | 0.01 | 0.012 | 0.014 | no usada |

### `MC_HHD.T10` — TABLA  Nº  10:    Velocidades máximas  admisibles (m/s)  en conductos revestidos

- Cita: `MC_HHD.4.1.1.3.6#T10`
- Tabla completa · el calculo usa 2 de 2 columnas y 1 de 3 filas
- Fuente que la tabla se atribuye: *HCANALES, Máximo Villon B.*
- **Afirmación negativa**: la Tabla Nº 10 no lista TMC ni HDPE. Ámbito barrido: las TRES filas de la tabla, leidas integras en la pag. impresa 76 sobre la pagina renderizada. «TMC» aparece en otras paginas del Manual (impresas 73 y 79 y en las laminas), nunca en esta tabla; HDPE no aparece en el Manual
- **Interpretación del proyectista, no de la fuente**: Que los dos números de una fila recorran la calidad del revestimiento — el superior para el acabado de mejor calidad y el inferior para el más pobre — es una lectura que este proyecto adopta para poder elegir un techo más conservador dentro de la fila ('v_max_concreto_eleccion'). El Manual NO la escribe.
  - En contra: la frase que introduce la tabla habla de «un rango, cuyos límites se describen a continuación»
  - En contra: la fila de mampostería trae un solo valor, que no encaja con una lectura de acabados
  - A favor: el título dice «Velocidades máximas admisibles (m/s)», que es lo único que decide que ninguno de los dos números sea un piso
  - A favor: el rótulo de su única columna de valores es «VELOCIDAD (M/S)»
- Vistas de cálculo derivadas: `TABLA_10_FILAS`, `V_MAX`

| Fila | TIPO DE REVESTIMIENTO | VELOCIDAD (M/S) | Uso |
|---|---|---|---|
| Concreto |  | 3.0 – 6.0 | usada |
| Ladrillo con concreto |  | 2.5 – 3.5 | no usada |
| Mampostería de piedra y concreto |  | 2.0 | no usada |

### `MS.C41` — Cuadro 4.1 Número de Calicatas para Exploración de Suelos

- Cita: `MS.4.2#C41`
- Tabla completa · el calculo usa 2 de 8 columnas y 4 de 6 filas
- Columna «Tipo de Carretera»: **elección pendiente** (`COND-CLASE-DE-VIA`) — el cálculo se detiene
- Columna «Profundidad (m)» transcrita y **no usada**: gobierna la campaña de campo, no el dimensionamiento de la alcantarilla. Se transcribe porque NOR-SUE-04 la reclamaba: el Cuadro SI fija la profundidad, en columna propia, y el repositorio no la recogia
- Columna «Calzada 2 carriles por sentido»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`) — el cálculo se detiene
- Columna «Calzada 3 carriles por sentido»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`) — el cálculo se detiene
- Columna «Calzada 4 carriles por sentido»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`) — el cálculo se detiene
- Columna «Observación» transcrita y **no usada**: es la regla de UBICACION de las calicatas, no de densidad; ninguna fase la evalua
- Fila «Autopistas: carreteras de IMDA mayor de 6000 veh/día, de calzadas separadas, cada una con dos o más carriles»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`)
- Fila «Carreteras Duales o Multicarril: carreteras de IMDA entre 6000 y 4001  veh/dia, de calzadas separadas, cada una con dos o más carriles»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`)
- **Laguna de la fuente**: las calzadas de MAS de 4 carriles por sentido: el Cuadro tabula 2, 3 y 4 y no dice que hacer con 5 o mas. Se cierra con: ninguna. La fuente no extrapola ni dice que la ultima fila se prolongue
- Vistas de cálculo derivadas: `CALICATAS_POR_KM`, `CALICATAS_POR_SENTIDO`, `CALICATAS_PROFUNDIDAD_M`

| Fila | Tipo de Carretera | Profundidad (m) | Calzada 2 carriles por sentido | Calzada 3 carriles por sentido | Calzada 4 carriles por sentido | Número mínimo de Calicatas | x sentido | Observación | Uso |
|---|---|---|---|---|---|---|---|---|---|
| Autopistas: carreteras de IMDA mayor de 6000 veh/día, de calzadas separadas, cada una con dos o más carriles |  | 1.5 | 4 | 4 | 6 | -> | True | Las calicatas se  ubicarán longitudinalmente y en forma alternada | pendiente |
| Carreteras Duales o Multicarril: carreteras de IMDA entre 6000 y 4001  veh/dia, de calzadas separadas, cada una con dos o más carriles |  | 1.5 | 4 | 4 | 6 | -> | True | Las calicatas se  ubicarán longitudinalmente y en forma alternada | pendiente |
| Carreteras de Primera Clase: carreteras con un IMDA entre 4000-2001 veh/día, de una calzada de dos carriles. |  | 1.5 |  |  |  | 4 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | usada |
| Carreteras de Segunda Clase: carreteras con un IMDA entre 2000-401 veh/día, de una calzada de dos carriles. |  | 1.5 |  |  |  | 3 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | usada |
| Carreteras de Tercera Clase: carreteras con un IMDA entre 400-201 veh/día, de una calzada de dos carriles. |  | 1.5 |  |  |  | 2 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | usada |
| Carreteras de Bajo Volumen de Tránsito: carreteras con un IMDA ≤ 200 veh/día, de una calzada. |  | 1.5 |  |  |  | 1 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | usada |

> Fuente Fuente:  Elaboración Propia, teniendo en cuenta el Tipo de Carretera establecido en la RD 037-2008-MTC/14 y el Manual de Ensayo de Materiales del MTC

## 6. Condiciones que detienen el cálculo

Lo indeterminado bloquea; lo que no bloquea lleva su justificación
escrita, y el test la exige.

| id | Dónde | Resuelve | Efecto |
|---|---|---|---|
| `COND-CARRILES-POR-SENTIDO` | tabla:MS.C41#MS.C41#autopista | `carriles_por_sentido` | bloquea |
| `COND-CARRILES-POR-SENTIDO` | tabla:MS.C41#MS.C41#dual | `carriles_por_sentido` | bloquea |
| `COND-CLASE-DE-VIA` | tabla:MS.C41#MS.C41#autopista | `clase_de_via` | bloquea |
| `COND-CLASE-DE-VIA` | tabla:MS.C41#MS.C41#dual | `clase_de_via` | bloquea |
| `COND-DMIN-ALTO-VOLUMEN` | cita:MC_HHD.4.1.1.3.4a | `clase_de_via` | advierte |
| `COND-DMIN-CANAL-RIEGO` | cita:MC_HHD.4.1.1.3.4a | `familia == 'C'` | excluye |
| `COND-LS-DISTANCIA-H-MEDIO` | cita:MP.2.4.2.2#SOBRECARGA | `distancia_trafico <= H / 2` | advierte |
| `COND-LS-LOSA-APROXIMACION` | cita:MP.2.4.2.2#SOBRECARGA | `losa_de_aproximacion` | excluye |
| `COND-PERFIL-SIN-INFO-SECUNDARIA` | cita:MS.4.2#PERFIL | `existe_informacion_secundaria_tramo` | bloquea |
| `COND-SELVA-ALTA` | cita:MC_HHD.4.1.1.3.7a | `region == 'selva_alta'` | excluye |

## 7. Discrepancias declaradas

`CLAUDE.md` obliga, cuando la fuente primaria gana a la hoja de ruta, a
declararlo en el punto de uso, a reportar el defecto contra la hoja de
ruta **y a dejar dicho que la hoja de ruta sigue mal mientras no se
corrija**. La tercera obligación vive aquí.

### abierta_contra_hoja_de_ruta

- **`DIS-HR-A807` — la norma que fija el calibre de la plancha de TMC por altura de relleno.** Gana **ASTM_A796**: la remision de la hoja de ruta es falsa. A-807 no es la norma que se le atribuye
  - Si se sigue la otra: se busca el calibre en un documento que no lo tiene, y la busqueda termina en un vacio aparente que no es tal
  - *hoja_de_ruta*: lo remite a «ASTM A-807» en su Sec. 7.A, en su Fase 8 y en su Anexo B
  - *ASTM_A796*: el calibre por altura de cobertura es de ASTM A796/A796M, no de A-807
- **`DIS-HR-CICLOPEO` — el f'c minimo de la matriz del concreto ciclopeo.** Gana **EG2013**: sobre el MISMO material rigen las dos normas y por la regla del mayor de Sec. 0.2 gobierna la mayor. La hoja de ruta mira solo a E.060 y no ve que sobre el mismo material rige tambien la norma vial del MTC
  - Si se sigue la otra: quien lea la hoja de ruta sin leer el codigo dimensionara un cabezal de ciclopeo con una matriz de 10 MPa que este calculo va a rechazar
  - *hoja_de_ruta*: su Sec. 9.4 pide f'c de matriz >= 10 MPa citando solo el Art. 22.10 de E.060
  - *EG2013*: la Clase G de la Tabla 503-07 -- concreto ciclopeo -- pide 14 MPa, y la Seccion 503 es la que este proyecto cita para los cabezales
- **`DIS-HR-D-MAX` — los topes de diametro por material (2.70 / 2.10 / 1.50 m).** Gana **ASTM_A760**: la fuente primaria, leida de los PDF de normas/, desmiente las dos atribuciones contrastables. No son topes normativos: son topes de CATALOGO, y como tales descartaban material en silencio con una cita que ninguna norma sostiene. AASHTO M294 no esta en normas/ y el tope del HDPE no se pudo contrastar
  - Si se sigue la otra: un punto que necesite mas de 2.10 m de TMC se declara no factible por una razon que la norma citada no sostiene
  - *hoja_de_ruta*: su Anexo B los declara bajo el rotulo «topes por norma de producto - VERIFICAR», atribuidos a ASTM C76 / AASHTO M170, AASHTO M36 / ASTM A760 y AASHTO M294
  - *ASTM_A760*: su Tabla 1 tabula diametros nominales de 100 mm (4 in) a 3600 mm (144 in): los 2100 mm son una fila mas de la serie, no un maximo
  - *AASHTO_M170M*: el conjunto de sus Tablas 1 a 5 cubre de 300 mm (Tablas 2 a 5) a 3600 mm (Tablas 3 y 5), y la Sec. 7.2 «Modified and Special Designs» preve ademas diseños por encima de lo tabulado con permiso del propietario. LEIDO TABLA POR TABLA la envolvente no es uniforme -- la Tabla 1, Clase I, va de 1500 a 3450 mm --, y la redaccion anterior de esta cita, «Tablas 1 a 5: de 300 a 3600 mm», era falsa leida distributivamente
- **`DIS-HR-G-LAUSHEY` — la atribucion del valor g = 9.8 m/s2 al num. 4.1.1.3.7 c).** Gana **MC_HHD**: verificado contra el PDF barriendo las 225 paginas: «9.8» como valor de la gravedad aparece en dos paginas, ninguna de ellas la 80. EL NUMERO ES DEFENDIBLE Y LA CITA NO LO ERA: es el mismo genero de defecto que el proyecto purgo con el «19.62 = 2g». Se corrige la atribucion, no el numero
  - Si se sigue la otra: un revisor que abra la pag. 80 buscando el 9.8 no lo encuentra, y una cita que no se puede comprobar es indistinguible de una inventada
  - *hoja_de_ruta*: escribe «d50 en m, V en m/s, g = 9.8 m/s2» bajo el encabezado «Laushey — num. 4.1.1.3.7 c), pag. 80», presentando el 9.8 como si el numeral lo imprimiera
  - *MC_HHD*: el num. 4.1.1.3.7 c), pag. impresa 80, define g SIN numero: «g : Aceleracion de la gravedad (m/s2)». El 9.8 SI esta en el Manual, pero en otros dos numerales -- el 3.12.5 (pag. impresa 63) y el 4.1.1.5.4 b.2.4) (pag. impresa 111) --, y el 9.81 no aparece ni una vez
- **`DIS-HR-H-EQ` — la altura de suelo equivalente de la sobrecarga de trafico (h_eq).** Gana **AASHTO_LRFD_9**: por la Via 1 de Sec. 0.2 (AASHTO LRFD de extremo a extremo) y por la regla del mayor: el Manual fija un PISO («no menor que la equivalente a 0.60 m») y AASHTO tabula el valor. Los dos rigen, y h_eq es el mayor de los dos. El 0.60 plano no es defendible para un cabezal de 2 m con trafico perpendicular
  - Si se sigue la otra: con h_eq = 0.60 m fijo, un cabezal de 2.0 m con trafico perpendicular subestima la sobrecarga viva en un factor 1.87, y con gamma_LS = 1.75 eso llega al empuje de diseño
  - *hoja_de_ruta*: «Sobrecarga en el trasdos (num. 2.1.4.3.9, pag. 91): ... se añade sobrecarga vertical >= 0.60 m de relleno equivalente ... En un cabezal bajo terraplen vial SIEMPRE APLICA». Dos defectos en una frase: el numeral es «Aparatos de Apoyo» y el «siempre aplica» borra la condicion de distancia que la fuente pone
  - *MP*: el num. 2.1.4.3.9 se titula «Aparatos de Apoyo» y no contiene ni la palabra sobrecarga ni el 0.60. El texto real esta en el num. 2.4.2.2 «Cargas de Suelo: EH, ES, y DD», pag. impresa 102, y es CONDICIONAL: «Cuando se prevea trafico a una distancia horizontal, medida desde la parte superior de la estructura, menor o igual a la mitad de su altura...», con exencion expresa si hay losa de aproximacion
  - *AASHTO_LRFD_9*: el Art. 3.11.6.4 tabula h_eq por altura del muro, y para 2.0 m con trafico perpendicular da 1.12 m por interpolacion obligatoria. El Manual de Puentes NO transcribe esas tablas: su traduccion de la Sec. 3.11 se corta en el empuje pasivo k_p
- **`DIS-HR-H-RELLENO-MIN` — la altura minima de relleno sobre la clave para concreto y TMC.** Gana **AASHTO_LRFD_9**: «no fijado» ya no es cierto: lo fija AASHTO LRFD, que el propio Sec. 0.2 adopta de extremo a extremo, y las dos remisiones de la hoja son falsas (M 170M no da alturas de relleno y A-807 no es la norma que se le atribuye). Declarar un vacio sobre la fuente que SI trae el dato es el defecto que Sec. 0.5 llama el mas grave
  - Si se sigue la otra: se declara vacio lo que la norma adoptada tabula, y la cobertura minima queda sin piso
  - *hoja_de_ruta*: su Sec. 7.A dice «No fijado. Remite al Proyecto, AASHTO M-170M (clases I-V) o ASTM A-807»
  - *AASHTO_LRFD_9*: el Art. 12.6.6.3 y la Tabla 12.6.6.3-1 tabulan la cobertura minima para los tres tipos de conducto del catalogo

### resuelta

- **`DIS-CN-CALICATAS` — si el Cuadro 4.1 dice cuando son 4 calicatas y cuando 6.** Gana **MS**: verificado contra el PDF. Afirmar que la fuente calla donde habla es la forma inversa del mismo defecto que persigue este cluster: en vez de citar lo que no dice, se niega lo que si dice, y el resultado es igual de invisible -- un vacio inventado que convierte en [A] lo que es [N]
  - Si se sigue la otra: la densidad de la campaña geotecnica se elegiria como criterio [A] cuando la norma la determina, y una autopista de 4 carriles por sentido saldria con la mitad de las calicatas que el Cuadro exige
  - *codigo*: el comentario de CALICATAS_POR_SENTIDO afirmaba: «El Cuadro admite ademas 6 en vez de 4 para autopistas con 4 carriles por sentido, y «4 (o 6)» para duales. Ese 6 NO se transcribe aqui: el Cuadro lo da como alternativa SIN DECIR CUANDO APLICA CADA UNA, de modo que la eleccion entre 4 y 6 no es [N]»
  - *MS*: el Cuadro 4.1 SI lo condiciona, y por carriles por sentido
- **`DIS-CN-EG-508-07` — la pagina impresa del relleno minimo de 0,30 m del HDPE.** Gana **EG2013**: el desfase de este documento es +8 y es el mas grande del corpus: confundir pagina impresa con pagina PDF produce exactamente un error de 8, que es la distancia entre las dos cifras que el repositorio manejaba
  - Si se sigue la otra: la cita mas load-bearing del proyecto -- la que llega impresa a la memoria -- manda al revisor a una pagina que no dice lo que la cita afirma
  - *codigo*: el repositorio cito esa frase primero en la pag. impresa 982 y despues en la 984, y las dos citas conviven en el expediente
  - *EG2013*: la pagina impresa que la imprime, verificada
- **`DIS-HDS5-EDICIONES` — la constante K del termino de friccion del control de salida.** Gana **HDS5_3ED**: es la unica de las dos que publica la conversion SI. La copia de 1985 opera en unidades inglesas con rotulos duales, y el «si» de su nombre de archivo se refiere a sus cartas metricas, no al cuerpo del documento
  - Si se sigue la otra: aplicar 29 en metrico sobrestima el termino de friccion un +9.6 %, y no falla ruidosamente: devuelve numeros plausibles y equivocados
  - *HDS5_3ED*: «KU = 29 in English Units (19.63 in SI)»
  - *HDS5_SI_1985*: imprime 29 en sus ecs. (4b) y (5) con rotulos duales «ft (m)» y NO imprime 19.63, pese al «si» del nombre del archivo

### errata_de_imprenta

- **`DIS-MCHHD-T09-A2-DESPLAZADA` — la alineacion de la columna de valores con sus rotulos en el bloque A.2 NO METALICOS de la Tabla Nº 09.** Gana **Ven Te Chow 1983**: es un descuido de composicion del bloque A.2 -- el A.1 de la MISMA tabla no lo tiene --, y la lectura corrida es la unica que deja a cada hoja con su valor y coincide fila por fila con la fuente que la tabla se atribuye. HALLAZGO DE S12: el repositorio ya transcribia la lectura corregida y NO lo declaraba, de modo que su valor de Manning mas usado -- MANNING['concreto_tubo_recto'] -- se apoyaba en una lectura corregida que ningun revisor podia reproducir abriendo la pagina
  - Si se sigue la otra: MANNING['concreto_tubo_recto'] pasaria de (0.010, 0.013) a (0.011, 0.014): +10 % en el n minimo, que es el que gobierna V3 y la socavacion, y +7.7 % en el maximo, que gobierna capacidad y tirante
  - *MC_HHD*: en la pag. impresa 75 los valores del bloque A.2 se imprimen UN RENGLON MAS ARRIBA que sus rotulos: «0.010 0.011 0.013» queda a la altura de «a. Concreto» y «0.010 0.012 0.014» a la de «b. Madera», que son rotulos de categoria sin valores propios -- como «b. Acero» y «c. Metal corrugado» del bloque A.1, que SI quedan en blanco. Leida al pie de la letra, la pagina deja sin valor a «Tubo con moldaje madera en bruto» y a «c. Albañilería de piedra.», que son hojas de la jerarquia
  - *Ven Te Chow 1983*: la fuente que la propia Tabla Nº 09 declara asigna 0.010/0.011/0.013 a «culvert, straight and free of debris» y 0.010/0.012/0.014 a «wood stave», que son «tubo recto y libre de basuras» y «duelas». Corriendo un renglon, las diez ternas del bloque encajan una a una con las diez hojas, sin sobrar ni faltar
- **`DIS-MP-EXCENTRICIDAD` — el limite de excentricidad sismica para gamma_EQ = 0.0.** Gana **AASHTO_LRFD_9**: es descuido de traduccion y no decision del MTC, y lo prueba el propio Manual: tres paginas antes traduce el MISMO giro correctamente en su numeral ESTATICO, y en el mismo parrafo sismico traduce bien «eight-tenths». Solo degrada «two-thirds», y solo ahi. Ademas la lectura literal es normativamente imposible: dejaria el limite bajo SISMO al doble de estricto que bajo carga estatica permanente, invirtiendo la filosofia de estados limite
  - Si se sigue la otra: e <= B/6 en vez de B/3: rechazaria diseños que la norma acepta. Es conservador, y por eso no cambia ningun resultado ya emitido, pero deja la cita sin sostener
  - *MP*: traduce el «middle two-thirds» de AASHTO como «tercio central», que no es lo mismo: dos tercios centrales es e <= B/3 y el tercio central es e <= B/6
  - *AASHTO_LRFD_9*: «within the middle two-thirds of the base for gamma_EQ = 0.0»
- **`DIS-MP-KAE-SIGNO` — el signo del denominador de K_AE (Mononobe-Okabe).** Gana **AASHTO_LRFD_9**: no por preferencia de fuente: con el signo menos K_AE DIVERGE cuando el radicando tiende a 1, y el caso limite k_h = k_v = 0 deja de devolver el Ka de Coulomb. La formula se rompe donde el propio Manual la manda coincidir, y el Manual declara transcribirla de AASHTO
  - Si se sigue la otra: K_AE diverge; quien «corrija» M9 contra la letra impresa del Manual rompe la formula
  - *MP*: imprime «[1 - raiz(...)]», signo MENOS, verificado renderizando la pag. impresa 586 a 6x: el trazo es horizontal unico, sin trazo vertical
  - *AASHTO_LRFD_9*: imprime «[1 + raiz(...)]»
- **`DIS-MP-KH0-ROCA` — el lado del 1.2 en la clausula de roca de k_h0.** Gana **AASHTO_LRFD_9**: gana la PROSA del Manual, que coincide con AASHTO; el parentesis esta mal compuesto
  - Si se sigue la otra: una REDUCCION del 17 % de k_h0, justo lo contrario de lo que la prosa de la misma frase acaba de decir
  - *MP*: el parentesis imprime «1.2 kh0=FpgaPGA», con el 1.2 del lado izquierdo; leido al pie de la letra daria k_h0 = F_pga*PGA/1.2. La PROSA de la misma frase dice lo contrario
  - *AASHTO_LRFD_9*: «k_h0 shall be based on 1.2 times the site-adjusted peak ground acceleration coefficient (i.e., k_h0 = 1.2 F_pga PGA)»
- **`DIS-MP-NUMERAL-2.3.1.1.12.3` — el numeral impreso de «Limites de Excentricidad».** Gana **MP**: se cita COMO LO IMPRIME, con la advertencia, para que quien lo busque lo encuentre. Corregir el numeral en la cita mandaria al revisor a un renglon que el documento no tiene
  - Si se sigue la otra: citar «2.8.1.1.12.3» manda a un numeral que el Manual no imprime
  - *MP*: lo imprime «2.3.1.1.12.3», con un 3 donde toca un 8, rompiendo la serie 2.8.1.1.12.2 -> 2.8.1.1.12.5; el indice repite la errata
  - *AASHTO_LRFD_9*: la remision cruzada del propio Manual (11.6.3.3) si es correcta

## 8. Lo que falta por transcribir

Campos `POR_TRANSCRIBIR` en el registro: **0**, en 0 citas.
Este número es un **trinquete**: sólo puede decrecer, y un test lo
vigila. Una cita con cualquier campo pendiente NO puede llevar firma de
verificación.


Citas sin firma de verificación: **0** de 34.

