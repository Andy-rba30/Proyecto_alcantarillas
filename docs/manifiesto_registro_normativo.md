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

| id | Documento | Edición | Paginación (pdf ← impresa) | Páginas | SHA-1 | Texto extraíble | Vigencia (T1) |
|---|---|---|---|---|---|---|---|
| `AASHTO_LRFD_9` | AASHTO LRFD Bridge Design Specifications | Ninth Edition, 2020 | por capítulo: 1=15, 10=1289, 11=1469, 12=1638, 13=1750, 14=1782, 15=1872, 2=24, 3=54, 4=251, 5=359, 6=706, 7=1134, 8=1197, 9=1239 | 1905 | `71f4ced4c80f58db75a0bcdf4ac6b5d86dc0f858` | sí | **posterior detectada** 2026-09-14: AASHTO LRFD Bridge Design Specifications, 10th Edition (LRFDBDS-10, 2024) |
| `AASHTO_M170M` | AASHTO M 170M-04 «Standard Specification for Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe [Metric]» | M 170M-04 | por capítulo: M 170M=0 | 23 | `dcc40c0e5e9c99ad9f18490fa8c5b2d9394faa51` | **no** | **posterior detectada** 2026-09-14: AASHTO M 170M-23 (2023; equivalente ASTM C76M-22) |
| `AASHTO_M294_TRAD` | AASHTO M 294-11 «Tubería corrugada de polietileno, 300 a 1500 mm (12 a 60 in.) de diámetro» — TRADUCCION NO OFICIAL al español | M 294-11 (traduccion no oficial al español) | **sin determinar** | 17 | `7cecb19f73e4d101866832a3fc57db752fa53379` | sí | **posterior detectada** 2026-09-14: AASHTO M 294-25 (2025) |
| `AASHTO_M36` | AASHTO M 36 «Corrugated Steel Pipe, Metallic-Coated, for Sewers and Drains» | M 36-03 (2007) | por capítulo: M 36=1 | 24 | `f85b5658385ae6779dde4e5fd340ac3122b62636` | **no** | **posterior detectada** 2026-09-14: AASHTO M 36M/M 36-24 (2024) |
| `ASTM_A760` | ASTM A760/A760M-10 «Especificacion Estandar para Tuberia de Acero Corrugado, con Recubrimiento Metalico, para Alcantarillas y Drenajes» | A760/A760M-10 | corrida, +0 | 15 | `47d0d447143ca158615dff7dec79f2f7a8975732` | **no** | **posterior detectada** 2026-09-14: ASTM A760/A760M-25 |
| `ASTM_A796` | ASTM A796/A796M-13 «Structural Design of Corrugated Steel Pipe, Pipe-Arches, and Arches» (practica de diseño estructural de tuberia de acero corrugado, arcos-tubo y arcos) | A796/A796M-13 | corrida, +0 | 21 | `df7858f04caf61bc1c3a4ea3d664e38cacddee25` | **no** | **posterior detectada** 2026-09-14: ASTM A796/A796M-21 |
| `DG2018` | Manual de Carreteras: Diseño Geométrico DG-2018 (MTC, «Revisada y Corregida a Enero de 2018») | DG-2018 | corrida, +1 | 285 | `96ea04423a7e0e7fc44b5cd5d8824d6166a8e816` | sí | confirmada 2026-09-20; aprobada por RD 03-2018-MTC/14 |
| `E030` | Norma Tecnica E.030 «Diseño Sismorresistente» | Edicion 2026, publicada en el diario oficial El Peruano | corrida, +0 | 68 | `fe0a58e4be4b8709324e65ed6ad0c25b8e0b6899` | sí | confirmada 2026-09-14; aprobada por RM 183-2026-VIVIENDA |
| `E050` | Norma Tecnica E.050 «Suelos y Cimentaciones» | Edicion 2018 | corrida, +0 | 82 | `5fac1ecd997a6d6e80bcbf0967f89f9ddcc8106c` | sí | confirmada 2026-09-14; aprobada por RM 406-2018-VIVIENDA |
| `E060` | Norma Tecnica E.060 «Concreto Armado» | Edicion 2009 | corrida, +0 | 205 | `cffe0efffc767f5d06a33e1f4eed3a16a01bdd81` | sí | confirmada 2026-09-14; aprobada por DS 010-2009-VIVIENDA |
| `EG2013` | Manual de Carreteras "Especificaciones Tecnicas Generales para Construccion" (EG-2013) | Version revisada y corregida a junio 2013 | corrida, +8 | 1282 | `e35681d06b13226744324bc6b242b608ca9fa3ba` | sí | confirmada 2026-09-14; aprobada por RD 03-2013-MTC/14 |
| `HDS5_3ED` | HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-HIF-12-026) | Third Edition, April 2012 | por capítulo: 1=38, 2=62, 3=82, 4=126, 5=136, 6=162, 7=181, A=189, B=202, C=210, DG1=271, DG2=285, DG3=293, DG4=312; romanas: i=5 | 323 | `7b985e047c615b765e7c41b6ff12df0505c02ce4` | sí | confirmada 2026-09-14 |
| `HDS5_SI_1985` | HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-IP-85-15), copia rotulada «SI» por sus cartas metricas | September 1985 | **sin determinar** | 410 | `59c6623c78793f7f947b7095027096b86f88ddf0` | sí | **posterior detectada** 2026-09-14: HDS-5 Third Edition, FHWA-HIF-12-026 (2012), presente en normas/ como HDS5_3ED |
| `HEC14` | HEC-14 «Hydraulic Design of Energy Dissipators for Culverts and Channels» (Hydraulic Engineering Circular No. 14, FHWA-NHI-06-086) | Third Edition, July 2006 (con la fe de erratas del 1 de octubre de 2012 en la PDF 3) | por capítulo: 1=13, 10=201, 11=221, 12=245, 2=27, 3=31, 4=41, 5=53, 6=63, 7=77, 8=123, 9=157, A=249, B=259, C=277, D=279, R=283 | 287 | `1bffcbe220cd67e4c0de8b87b46d1ece64ce7217` | sí | confirmada 2026-11-11 |
| `MC_HHD` | Manual de Hidrologia, Hidraulica y Drenaje | Version Libro | corrida, +3 | 225 | `a31e853b8171b931863d7afa4379bbbc57cacb0d` | sí | confirmada 2026-09-14; aprobada por RD 20-2011-MTC/14 |
| `MP` | Manual de Puentes | Version Libro | corrida, +1 | 673 | `67a7a9f1c61cad8f9ca179cd4ca777f96b49dc44` | sí | **posterior detectada** 2026-09-14: Manual de Puentes actualizado 2018 (630 paginas); aprobada por RD 041-2016-MTC/14; **derogada por RD 19-2018-MTC/14** |
| `MS` | Manual de Carreteras: Suelos, Geologia, Geotecnia y Pavimentos — Seccion Suelos y Pavimentos | Version abril 2014 | corrida, +1 | 281 | `21d19a71090c1e586cd31596db8a4d007dc7b96f` | sí | confirmada 2026-09-14; aprobada por RD 10-2014-MTC/14 |
| `WSDOT_HM` | WSDOT Hydraulics Manual (M 23-03) | M 23-03.12, April 2026 | por capítulo: 1=14, 10=265, 10A=289, 2=36, 2A=63, 3=65, 4=86, 5=100, 6=120, 7=130, 7A=210, 7B=211, 8=215, 9=264, G=298 | 325 | `b34bb7bd448c249301e2a1a82234be70e8b6d916` | sí | confirmada 2026-11-11 |

## 2. Fuentes que se citan y NO están en `normas/`

Ordenadas por lo que cuesta traerlas, para que la deuda se vea sin
leer la §15 del plan. **Ninguna puede sostener un `[N]`**: la etiqueta
exige numeral verificado, y aquí no hay contra qué verificar.

| id | Documento | Esfuerzo | Qué desbloquearía | Sustituto vigente |
|---|---|---|---|---|
| `LEY_29338` | Ley 29338, Ley de Recursos Hidricos, y su reglamento | facil, es descarga publica | el tramite, no el calculo | — |
| `RNGIV` | Reglamento Nacional de Gestion de Infraestructura Vial, aprobado por DS 034-2008-MTC, y sus modificatorias | facil, es descarga publica | la cita textual de la definicion juridica del derecho de via y de quien lo aprueba, que hoy V5 solo tiene por remision del DG-2018; no mueve ningun numero: los anchos estan en la Tabla 304.09 del DG-2018, que si esta | la remision del DG-2018 §304.07.01 (cita DG2018.304.07.01) |
| `AASHTO_M259` | AASHTO M 259 «Precast Reinforced Concrete Box Sections for Culverts, Storm Drains, and Sewers» (ASTM C789) | compra o suscripcion | la alternativa PREFABRICADA al marco vaciado in situ de la Familia C: seria una decision nueva de alcance (ruta_familia_c §14.1), no un dato | marco vaciado in situ, diseñado por AASHTO LRFD Seccion 5 y Art. 12.11 y construido por EG-2013 503 y 504 |
| `AASHTO_M273` | AASHTO M 273 «Precast Reinforced Concrete Box Sections for Culverts, Storm Drains, and Sewers with Less Than 2 ft of Cover Subjected to Highway Loadings» (ASTM C850) | compra o suscripcion | lo mismo que M 259, para el caso de cobertura baja; ninguna de las dos mueve el diseño in situ | marco vaciado in situ, diseñado por AASHTO LRFD Seccion 5 y Art. 12.11 y construido por EG-2013 503 y 504 |
| `AASHTO_M294` | AASHTO M 294-11 «Corrugated Polyethylene Pipe, 300- to 1500-mm Diameter» -- el ORIGINAL EN INGLES, del que deriva la traduccion no oficial presente en normas/ | compra o suscripcion | citar a AASHTO y no a un traductor anonimo, no el tope: (1) reverificar contra el original lo que hoy sostiene la traduccion -- la serie de tamaños nominales 300-1500 mm (1.1.1, 7.2.1), la tabla de espesores minimos de pared (7.2.2) y la exclusion del diseño estructural (1.4) -- y, si el original imprime folio, firmar (`Verificado`) lo que hoy no puede firmarse por T6; (2) comprobar que el original no imprime nada que la traduccion omita o altere en esos numerales; (3) leer el diametro exterior o la altura de perfil si el original los fijara, que la traduccion no trae. NO desbloquearia un [N]: es norma de producto extranjera, y 'D_max_catalogo' seguiria [A] con el techo de la serie como extremo declarado | AASHTO_M294_TRAD, traduccion no oficial presente en normas/, rotulada como tal en cada cita |
| `ASTM_A798` | ASTM A798/A798M «Installing Factory-Made Corrugated Steel Pipe for Sewers and Other Applications» | compra o suscripcion | nada que el EG-2013 no cubra ya para obra vial peruana | EG-2013 Seccion 507 |
| `ASTM_A807` | ASTM A-807 (la designacion que la hoja de ruta atribuye al calibre de TMC por altura de relleno) | compra o suscripcion | nada: la remision es FALSA, y desde N1 esta VERIFICADA en positivo y no solo por ausencia: A796 num. 22.1 la cita como practica de INSTALACION («shall conform to Practice A798/A798M or A807/A807M»), que es exactamente para lo que EG-2013 507.05/.06/.08 la invocan. El calibre lo fija A796 por procedimiento (num. 7 a 10) -- no hay tabla en ninguna de las dos --. DIS-HR-A807 quedo RESUELTA en N1 al corregirse la fila de la v8 | ninguno; la remision se retira, no se sustituye |
| `ASTM_C76` | ASTM C76 «Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe» | compra o suscripcion | nada nuevo: AASHTO M 170M-04, que SI esta, tabula de 300 a 3600 mm y ya desmiente el tope | AASHTO M 170M-04, presente en normas/ |
| `APENDICE_A3_MP` | Manual de Puentes, Apendice A3: mapas de isoaceleracion | gabinete | nada por la via de conseguirlo: el apendice SI esta en el PDF. Lo que no se puede es leer la isolinea por texto | datos_sitio['PGA_roca_B'], [S] con la lectura del mapa declarada y verificable por imagen |
| `MEYERHOF_1957` | Meyerhof, G. G. (1957), abacos de N_cq y N_gamma_q | gabinete | nada nuevo: los abacos SI estan, reproducidos en el Manual de Puentes. Lo que no se puede es leerlos por texto — son raster | Manual de Puentes num. 2.8.1.3.1.2c. NO es un caso de fuente ausente sino de fuente presente ilegible por texto: la lectura del abaco se declara [S] y se verifica por imagen |
| `SERIES_SENAMHI_ANA` | Series hidrometeorologicas SENAMHI / ANA para la cuenca del corredor | gabinete | el SUSTENTO del Q de la Familia A, que hoy entra ya calculado por la columna `Q_m3s` sin que el programa pueda comprobar de que serie salio. Es la ausencia mas cara del expediente | ninguno. El programa NO se detiene por ella: un `Q_m3s` lleno se calcula y el criterio sale en el bloque de pendientes sin haber frenado nada; quien recibe el CSV exige aparte el estudio hidrologico que lo respalda |
| `ESTUDIO_GEOTECNICO` | Estudio de Mecanica de Suelos (EMS) del expediente | de campo | toda la durabilidad del concreto (y con ella el recubrimiento), la clase de sitio sismica y el resguardo de la napa | ninguno: los criterios valen None y bloquean |

## 3. Catálogos, que NO son fuentes

Un tope de catálogo no tiene numeral, y el registro no le deja fingir
que lo tiene: un `Catalogo` no puede ser el `fuente_id` de una cita.

- **`CAT_TUBERIA_LOCAL` — Catalogo de conductos disponibles para el corredor** (oferta comercial y capacidad de transporte a la obra (La Union, Piura)).
  Qué norma NO lo sostiene: NINGUNA de las dos contrastables sobre el original, y la tercera solo sobre una traduccion. Los topes 2.70 / 2.10 / 1.50 m se atribuian a «ASTM C76 / AASHTO M170», «AASHTO M36 / ASTM A760» y «AASHTO M294», y las dos primeras atribuciones estan verificadas EN CONTRA sobre los PDF de normas/: ASTM A760/A760M-10 tabula de 100 a 3600 mm y AASHTO M 170M-04 de 300 a 3600 mm con diseños especiales por encima. La tercera se contrasto en N2 sobre la TRADUCCION NO OFICIAL de AASHTO M 294-11 (`AASHTO_M294_TRAD`, citas 1.1.1 y 7.2.1): su ambito y su serie de tamaños nominales terminan en 1500 mm, de modo que el tope del HDPE es el unico que coincide con el techo de una norma de producto -- segun una traduccion sin firma; el original sigue ausente --. No cambia la clase del dato: el tope sigue siendo de catalogo para los tres materiales, porque la eleccion (que diametro admite el proyecto por disponibilidad) es la misma, y en HDPE ademas no hay serie por encima. Un tope de catalogo no tiene numeral, y descartaba material en silencio con una cita que ninguna norma sostiene (NOR-PRO-01, NOR-PRO-02, MAT-O8)

## 4. Citas

Una fila por objeto `Cita`. El `id` es el ancla: no hay número de
línea que se pueda romper.

### AASHTO LRFD Bridge Design Specifications  (`AASHTO_LRFD_9`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `AASHTO_LRFD_9.1.2#BRIDGE` | 1.2 | «DEFINITIONS» | pág. impresa **1-2** · PDF 17 | definicion | 2026-09-22 · ambos |
| `AASHTO_LRFD_9.1.3.5` | 1.3.5 | «1.3.5—Operational Importance» | pág. impresa **1-7** · PDF 22 | permiso | 2026-11-12 · texto |
| `AASHTO_LRFD_9.10.5.4.2` | 10.5.4.2 | «Liquefaction Design Requirements» | pág. impresa **10-34** · PDF 1323 | exigencia | 2026-08-29 · texto |
| `AASHTO_LRFD_9.10.5.4.2#ESPECTRO` | 10.5.4.2, configuracion licuada | «Liquefaction Design Requirements» | pág. impresa **10-34** · PDF 1323 | recomendacion | 2026-08-29 · texto |
| `AASHTO_LRFD_9.10.5.5.2.2#T1` | 10.5.5.2.2, Tabla 10.5.5.2.2-1 | «Spread Footings» | pág. impresa **10-42** · PDF 1331 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.10.6.1.2#DESPLANTE` | 10.6.1.2 | «Bearing Depth» | pág. impresa **10-52** · PDF 1341 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.10.6.3.1.1#NIVEL_FREATICO` | 10.6.3.1.1 | «General» | pág. impresa **10-69** · PDF 1358 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.10.6.3.1.2a#QN` | 10.6.3.1.2a | «Basic Formulation» | pág. impresa **10-70** · PDF 1359 | recomendacion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.10.6.3.1.2a#T1` | 10.6.3.1.2a, Tabla 10.6.3.1.2a-1 | «Basic Formulation» | pág. impresa **10-72** · PDF 1361 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.10.6.3.1.2c#TALUD` | 10.6.3.1.2c | «Considerations for Footings on Slopes» | pág. impresa **10-74** · PDF 1363 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.10.6.3.4#RESISTENCIA` | 10.6.3.4 | «Failure by Sliding» | pág. impresa **10-84** · PDF 1373 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.10.7.5#INDICATIVOS` | 10.7.5 | «Corrosion and Deterioration» | pág. impresa **10-125** · PDF 1414 | recomendacion | 2026-11-11 · texto |
| `AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO` | 11.10.6.4.2a | «Steel Reinforcements» | pág. impresa **11-89** · PDF 1558 | definicion | 2026-11-11 · texto |
| `AASHTO_LRFD_9.11.12.8#AGRESIVO` | 11.12.8 | «Corrosion Protection» | pág. impresa **11-134** · PDF 1603 | definicion | 2026-11-11 · texto |
| `AASHTO_LRFD_9.11.5.7#MUROS` | 11.5.7 | «Resistance Factors—Service and Strength» | pág. impresa **11-15** · PDF 1484 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.5.8#EXTREMO` | 11.5.8 | «Resistance Factors—Extreme Event Limit State» | pág. impresa **11-18** · PDF 1487 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.5.8#PORTANTE` | 11.5.8 | «Resistance Factors—Extreme Event Limit State» | pág. impresa **11-18** · PDF 1487 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.3.2#PORTANTE` | 11.6.3.2 | «Bearing Resistance» | pág. impresa **11-21** · PDF 1490 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.3.3#EXC` | 11.6.3.3 | «Eccentricity Limits» | pág. impresa **11-24** · PDF 1493 | exigencia | 2026-09-12 · texto |
| `AASHTO_LRFD_9.11.6.3.5#PASIVA` | 11.6.3.5 | «Passive Resistance» | pág. impresa **11-24** · PDF 1493 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.3.6#DESLIZAMIENTO` | 11.6.3.6 | «Sliding» | pág. impresa **11-24** · PDF 1493 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.3.7#GLOBAL` | 11.6.3.7 | «Overall Stability» | pág. impresa **11-24** · PDF 1493 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.5.1#EXC` | 11.6.5.1 | «General» | pág. impresa **11-25** · PDF 1494 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.11.6.5.2.1#ROCA` | 11.6.5.2.1 | «Characterization of Acceleration at Wall Base» | pág. impresa **11-27** · PDF 1496 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.11.6.5.2.2#ALTURA` | 11.6.5.2.2 | «Estimation of Acceleration Acting on Wall Mass» | pág. impresa **11-28** · PDF 1497 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.5.2.2#REDUCCION` | 11.6.5.2.2 | «Estimation of Acceleration Acting on Wall Mass» | pág. impresa **11-28** · PDF 1497 | permiso | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION` | 11.6.5.3 | «Calculation of Seismic Active Earth Pressures» | pág. impresa **11-30** · PDF 1499 | recomendacion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.5.3#VALIDEZ` | 11.6.5.3 | «Calculation of Seismic Active Earth Pressures» | pág. impresa **11-29** · PDF 1498 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE` | 11.6.5.4 | «Calculation of Seismic Earth Pressure for Nonyielding Abutments and Walls» | pág. impresa **11-32** · PDF 1501 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.11.6.6#DRENAJE` | 11.6.6 | «Drainage» | pág. impresa **11-35** · PDF 1504 | exigencia | 2026-11-13 · texto |
| `AASHTO_LRFD_9.12.10.2.1#PESO_MIN` | 12.10.2.1 | «12.10.2.1 Standard Installations» | pág. impresa **12-52** · PDF 1690 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.2.1#VAF` | 12.10.2.1 | «12.10.2.1 Standard Installations» | pág. impresa **12-52** · PDF 1690 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.2.2` | 12.10.2.2 | «12.10.2.2 Pipe Fluid Weight» | pág. impresa **12-54** · PDF 1692 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.2.3` | 12.10.2.3 | «12.10.2.3—Live Loads» | pág. impresa **12-54** · PDF 1692 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.4.3.1` | 12.10.4.3.1 | «12.10.4.3.1—Bearing Resistance» | pág. impresa **12-64** · PDF 1702 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.4.3.1#DLOAD` | 12.10.4.3.1 | «12.10.4.3.1—Bearing Resistance» | pág. impresa **12-64** · PDF 1702 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.4.3.1#TIPO1` | 12.10.4.3.1 | «12.10.4.3.1—Bearing Resistance» | pág. impresa **12-64** · PDF 1702 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.4.3.2a` | 12.10.4.3.2a | «12.10.4.3.2a—Earth Load Bedding Factor for Circular Pipe» | pág. impresa **12-65** · PDF 1703 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.10.4.3.2c` | 12.10.4.3.2c | «12.10.4.3.2c—Live Load Bedding Factors» | pág. impresa **12-66** · PDF 1704 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.11.1` | 12.11.1 | «General» | pág. impresa **12-68** · PDF 1706 | exigencia | 2026-09-20 · texto |
| `AASHTO_LRFD_9.12.11.2.1#LL` | 12.11.2.1 | «12.11.2.1—General» | pág. impresa **12-68** · PDF 1706 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.11.2.2.1` | 12.11.2.2.1 | «12.11.2.2.1—Embankment and Trench Conditions» | pág. impresa **12-69** · PDF 1707 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.2.2` | 12.12.2.2 | «12.12.2.2—Deflection Requirement» | pág. impresa **12-75** · PDF 1713 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.10.1b#STUB` | 12.12.3.10.1b | «12.12.3.10.1b—Local Buckling Effective Area» | pág. impresa **12-85** · PDF 1723 | permiso | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.10.1c#EP` | 12.12.3.10.1c | «12.12.3.10.1c—Compression Strain» | pág. impresa **12-86** · PDF 1724 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.10.1d` | 12.12.3.10.1d | «12.12.3.10.1d—Thrust Strain Limits» | pág. impresa **12-86** · PDF 1724 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.10.1e` | 12.12.3.10.1e | «12.12.3.10.1e—General Buckling Strain Limits» | pág. impresa **12-86** · PDF 1724 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.2` | 12.12.3.2 | «12.12.3.2—Section Properties» | pág. impresa **12-76** · PDF 1714 | recomendacion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.3#PANDEO` | 12.12.3.3 | «12.12.3.3—Chemical and Mechanical» | pág. impresa **12-76** · PDF 1714 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.5` | 12.12.3.5 | «12.12.3.5—Factored and Service Loads» | pág. impresa **12-78** · PDF 1716 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.12.3.6` | 12.12.3.6 | «12.12.3.6—Handling and Installation» | pág. impresa **12-82** · PDF 1720 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.4.2.4` | 12.4.2.4 | «Precast Concrete Structures» | pág. impresa **12-8** · PDF 1646 | exigencia | 2026-09-20 · texto |
| `AASHTO_LRFD_9.12.5.4` | 12.5.4 | «12.5.4—Load Modifiers and Load Factors» | pág. impresa **12-11** · PDF 1649 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.5.5` | 12.5.5 | «12.5.5—Resistance Factors» | pág. impresa **12-11** · PDF 1649 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.5.6.1#FF` | 12.5.6.1 | «12.5.6.1—Corrugated Metal Pipe and Structural Plate Structures» | pág. impresa **12-13** · PDF 1651 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.5.6.3` | 12.5.6.3 | «12.5.6.3—Thermoplastic and Fiberglass Pipe» | pág. impresa **12-14** · PDF 1652 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.6.1#FLOTACION` | 12.6.1 | «Loading» | pág. impresa **12-14** · PDF 1652 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX` | 12.6.1 | «Loading» | pág. impresa **12-14** · PDF 1652 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.12.6.2.3#UPLIFT` | 12.6.2.3 | «Uplift» | pág. impresa **12-19** · PDF 1657 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.12.6.5#ALEROS` | 12.6.5 | «Scour» | pág. impresa **12-20** · PDF 1658 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.6.5#DENTELLON` | 12.6.5 | «Scour» | pág. impresa **12-20** · PDF 1658 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.6.5#ZAPATAS` | 12.6.5 | «Scour» | pág. impresa **12-20** · PDF 1658 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.6.6.3#COBERTURA` | 12.6.6.3 | «Minimum Cover» | pág. impresa **12-21** · PDF 1659 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA` | 12.6.6.3 | «Minimum Cover» | pág. impresa **12-22** · PDF 1660 | exigencia | 2026-11-12 · ambos |
| `AASHTO_LRFD_9.12.7.2.2` | 12.7.2.2 | «12.7.2.2—Thrust» | pág. impresa **12-25** · PDF 1663 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.7.2.3` | 12.7.2.3 | «12.7.2.3—Wall Resistance» | pág. impresa **12-26** · PDF 1664 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.7.2.4` | 12.7.2.4 | «12.7.2.4—Resistance to Buckling» | pág. impresa **12-26** · PDF 1664 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.12.7.2.5` | 12.7.2.5 | «12.7.2.5—Seam Resistance» | pág. impresa **12-27** · PDF 1665 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.10.2#CLASE_F` | 3.10.2 | «Seismic Hazard» | pág. impresa **3-71** · PDF 125 | exigencia | 2026-08-29 · texto |
| `AASHTO_LRFD_9.3.10.2.2` | 3.10.2.2 | «Site-Specific Procedure» | pág. impresa **3-100** · PDF 154 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.3.10.3.1` | 3.10.3.1 | «Site Class Definitions» | pág. impresa **3-101** · PDF 155 | exigencia | 2026-08-29 · texto |
| `AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES` | 3.10.3.1, nota «Exceptions» al pie de la Tabla 3.10.3.1-1 | «Site Class Definitions» | pág. impresa **3-102** · PDF 156 | exigencia | 2026-08-29 · texto |
| `AASHTO_LRFD_9.3.10.3.1#INVESTIGACION` | 3.10.3.1, nota «Exceptions» al pie de la Tabla 3.10.3.1-1 | «Site Class Definitions» | pág. impresa **3-102** · PDF 156 | exigencia | 2026-08-29 · texto |
| `AASHTO_LRFD_9.3.11.3` | 3.11.3 | «Presence of Water» | pág. impresa **3-118** · PDF 172 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.3.11.5.2#K0` | 3.11.5.2 | «At-Rest Lateral Earth Pressure Coefficient, ko» | pág. impresa **3-120** · PDF 174 | permiso | 2026-11-13 · texto |
| `AASHTO_LRFD_9.3.11.5.3#CULMANN` | 3.11.5.3 | «Active Lateral Earth Pressure Coefficient, ka» | pág. impresa **3-121** · PDF 175 | permiso | 2026-11-13 · texto |
| `AASHTO_LRFD_9.3.11.5.8.1#CUNA` | 3.11.5.8.1 | Lateral Earth Pressures for Mechanically Stabilized Earth Walls › «General» | pág. impresa **3-137** · PDF 191 | recomendacion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.3.11.6.4` | 3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.3.11.6.4#ALTURA` | 3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.3.11.6.4#APLICA` | 3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO` | 3.6.1.2.6a | «3.6.1.2.6a—General» | pág. impresa **3-26** · PDF 80 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE` | 3.6.1.2.6a | «3.6.1.2.6a—General» | pág. impresa **3-26** · PDF 80 | permiso | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.6.1.2.6a#EJES` | 3.6.1.2.6a | «3.6.1.2.6a—General» | pág. impresa **3-26** · PDF 80 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.6.1.2.6a#RELLENO` | 3.6.1.2.6a | «3.6.1.2.6a—General» | pág. impresa **3-26** · PDF 80 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL` | 3.6.1.2.6a | «3.6.1.2.6a—General» | pág. impresa **3-26** · PDF 80 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS` | 3.6.1.2.6a | «3.6.1.2.6a—General» | pág. impresa **3-26** · PDF 80 | permiso | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.6.1.2.6b#PL` | 3.6.1.2.6b | «3.6.1.2.6b—Traffic Parallel to the Culvert Span» | pág. impresa **3-28** · PDF 82 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.3.7.2` | 3.7.2 | «Buoyancy» | pág. impresa **3-45** · PDF 99 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.5.10.1` | 5.10.1 | «Concrete Cover» | pág. impresa **5-167** · PDF 526 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.5.10.1#ESTRIBOS` | 5.10.1 | «Concrete Cover» | pág. impresa **5-168** · PDF 527 | permiso | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.5.10.1#PISO` | 5.10.1 | «Concrete Cover» | pág. impresa **5-168** · PDF 527 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.A11.3.1#KAE` | A11.3.1, ec. A11.3.1-1 | «Mononobe–Okabe Method» | pág. impresa **11-145** · PDF 1614 | aproximacion | 2026-08-28 · imagen renderizada |
| `AASHTO_LRFD_9.C10.5.5.2.2#ASD` | C10.5.5.2.2 | «Spread Footings» | pág. impresa **10-42** · PDF 1331 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C10.6.3.3#EQUIVALENCIA` | C10.6.3.3 | «Eccentric Load Limitations» | pág. impresa **10-84** · PDF 1373 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C11.5.6#FIGURAS` | C11.5.6, Figuras C11.5.6-1 y C11.5.6-2 | «Load Combinations and Load Factors» | pág. impresa **11-13** · PDF 1482 | definicion | 2026-11-13 · ambos |
| `AASHTO_LRFD_9.C11.5.6#SOBRECARGA` | C11.5.6 | «Load Combinations and Load Factors» | pág. impresa **11-12** · PDF 1481 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA` | C11.6.3.3 | «Eccentricity Limits» | pág. impresa **11-24** · PDF 1493 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C11.6.5.3#CUNA` | C11.6.5.3 | «Calculation of Seismic Active Earth Pressures» | pág. impresa **11-30** · PDF 1499 | permiso | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C11.6.5.3#RESULTANTE` | C11.6.5.3 | «Calculation of Seismic Active Earth Pressures» | pág. impresa **11-30** · PDF 1499 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C11.6.5.4#CEDENTE` | C11.6.5.4 | «Calculation of Seismic Earth Pressure for Nonyielding Abutments and Walls» | pág. impresa **11-32** · PDF 1501 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C11.6.5.4#K0` | C11.6.5.4 | «Calculation of Seismic Earth Pressure for Nonyielding Abutments and Walls» | pág. impresa **11-32** · PDF 1501 | recomendacion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C12.12.2.2` | C12.12.2.2 | «C12.12.2.2» | pág. impresa **12-74** · PDF 1712 | recomendacion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.C12.12.3.2` | C12.12.3.2 | «C12.12.3.2» | pág. impresa **12-76** · PDF 1714 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.C12.6.2.3` | C12.6.2.3 | «Uplift» | pág. impresa **12-19** · PDF 1657 | recomendacion | 2026-08-28 · texto |
| `AASHTO_LRFD_9.C12.6.9#NIVEL_4` | C12.6.9 | «Corrosive and Abrasive Conditions» | pág. impresa **12-24** · PDF 1662 | definicion | 2026-11-11 · texto |
| `AASHTO_LRFD_9.C12.7.2.2` | C12.7.2.2 | «C12.7.2.2» | pág. impresa **12-25** · PDF 1663 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.C3.10.3.1-1#PASO1` | Tabla C3.10.3.1-1, paso 1 | «Steps for Site Classification» | pág. impresa **3-103** · PDF 157 | recomendacion | 2026-08-29 · texto |
| `AASHTO_LRFD_9.C3.11.5.3#DELTA` | C3.11.5.3 | «Active Lateral Earth Pressure Coefficient, ka» | pág. impresa **3-121** · PDF 175 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON` | C3.11.5.3 | «Active Lateral Earth Pressure Coefficient, ka» | pág. impresa **3-122** · PDF 176 | definicion | 2026-11-13 · texto |
| `AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO` | C3.11.5.8.1 | «General» | pág. impresa **3-137** · PDF 191 | permiso | 2026-11-13 · ambos |
| `AASHTO_LRFD_9.C3.11.6.4` | C3.11.6.4 | «Live Load Surcharge (LS)» | pág. impresa **3-151** · PDF 205 | definicion | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.C3.4.1#GAMMA_EQ` | C3.4.1 | «3.4.1-Load Factors and Load Combinations» | pág. impresa **3-10** · PDF 64 | recomendacion | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.C3.6.1.2.6b` | C3.6.1.2.6b | «C3.6.1.2.6b» | pág. impresa **3-27** · PDF 81 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T12.10.2.1-1` | Table 12.10.2.1-1 | «Table 12.10.2.1-1—Standard Embankment Installation Soils and Minimum Compaction Requirements» | pág. impresa **12-50** · PDF 1688 | exigencia | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T12.10.2.1-1#PROCTOR` | Table 12.10.2.1-1 | «Table 12.10.2.1-1—Standard Embankment Installation Soils and Minimum Compaction Requirements» | pág. impresa **12-51** · PDF 1689 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T12.12.3.3-1` | Table 12.12.3.3-1 | «Table 12.12.3.3-1—Mechanical Properties of Thermoplastic Pipe» | pág. impresa **12-77** · PDF 1715 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T12.12.3.5-1` | Table 12.12.3.5-1 | «Table 12.12.3.5-1—Ms Based on Soil Type and Compaction Condition» | pág. impresa **12-81** · PDF 1719 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T12.12.3.5-2` | Table 12.12.3.5-2 | «Table 12.12.3.5-2—Equivalent ASTM and AASHTO Soil Classifications» | pág. impresa **12-82** · PDF 1720 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T12.6.6.3-1` | Table 12.6.6.3-1 | 12.6.6.3 › Minimum Cover › «Minimum Cover» | pág. impresa **12-22** · PDF 1660 | exigencia | 2026-08-28 · imagen renderizada |
| `AASHTO_LRFD_9.T3.10.3.1-1#F` | Tabla 3.10.3.1-1, fila F | «Site Class Definitions» | pág. impresa **3-102** · PDF 156 | definicion | 2026-08-29 · ambos |
| `AASHTO_LRFD_9.T3.11.6.4-1` | Table 3.11.6.4-1 | «Equivalent Height of Soil for Vehicular Loading on Abutments Perpendicular to Traffic» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.T3.11.6.4-2` | Table 3.11.6.4-2 | «Equivalent Height of Soil for Vehicular Loading on Retaining Walls Parallel to Traffic» | pág. impresa **3-151** · PDF 205 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.T3.4.1-1` | Table 3.4.1-1 | «Load Combinations and Load Factors» | pág. impresa **3-17** · PDF 71 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.T3.4.1-2` | Table 3.4.1-2 | «Load Factors for Permanent Loads» | pág. impresa **3-18** · PDF 72 | exigencia | 2026-08-28 · texto |
| `AASHTO_LRFD_9.T3.6.1.2.6a-1` | Table 3.6.1.2.6a-1 | «Table 3.6.1.2.6a-1—Live Load Distribution Factor (LLDF) for Buried Structures» | pág. impresa **3-27** · PDF 81 | definicion | 2026-11-12 · texto |
| `AASHTO_LRFD_9.T5.10.1-1` | Table 5.10.1-1 | «Minimum Cover for Main Reinforcing Steel (in.)» | pág. impresa **5-169** · PDF 528 | exigencia | 2026-08-28 · ambos |
| `AASHTO_LRFD_9.TA12-11` | Table A12-11 | «PE Corrugated Pipes (AASHTO M 294)» | pág. impresa **12-108** · PDF 1746 | definicion | 2026-11-11 · texto |
| `AASHTO_LRFD_9.TA12-9` | Table A12-9 | «Table A12-9—Mechanical Properties for Spiral Rib and Corrugated Metal Pipe and Pipe Arch» | pág. impresa **12-107** · PDF 1745 | definicion | 2026-11-12 · texto |

> **`AASHTO_LRFD_9.1.2#BRIDGE`** — Es la definicion a la que remite el num. 4.1.1.5.1 del Manual de Hidrologia («siguiendo lo establecido en las especificaciones AASHTO LRFD»). La magnitud es «an opening»: la ABERTURA de la estructura. 20.0 ft son 6.096 m y el Manual escribe 6.0 m sin decir como pasa de una cifra a la otra: la diferencia esta declarada en DIS-LUZ-DENOMINACION y el codigo compara los 6.0 m del Manual ([N], el mas exigente de los dos).

> **`AASHTO_LRFD_9.1.3.5`** — Es quien fija eta_I: el Propietario. La misma pagina gradua eta_I >= 1.05 (critical or essential), 1.00 (typical) y >= 0.95 (relatively less important), que es la graduacion que el Manual de Puentes 2.3.2.5 traduce. NINGUNA de las dos prescribe 1.05 para una estructura enterrada: 12.5.4 solo fija la redundancia.

> **`AASHTO_LRFD_9.10.5.4.2`** — POR DONDE ENTRA LA LICUEFACCION EN AASHTO, que no es por la clase de sitio: es la Seccion 10, Cimentaciones, bajo 10.5.4 «Extreme Events Limit States». Y el disparador lo dice todo -- zona sismica 3 o 4, MAS napa freatica en los 50 ft superiores, MAS caracteristicas de suelo por (N1)60, q_ciN, V_s1 o unidad geologica con antecedente de licuefaccion --: ninguna de las tres condiciones menciona la clase de sitio. «Site Class F» no aparece en NINGUNA pagina de la Seccion 10.

> **`AASHTO_LRFD_9.10.5.4.2#ESPECTRO`** — EL ARGUMENTO POSITIVO, y es el que convierte NOR-AAS-02 de argumento por silencio en argumento por coherencia interna de la fuente. Si un suelo licuable fuera Clase F por serlo, su fila no tendria factor -- son cinco asteriscos -- y no habria espectro «no licuado» con que empezar. AASHTO manda justo lo contrario: analizar primero SIN licuefaccion y despues CON ella, con el mismo espectro; y en la pag. impresa 10-35 acota el espectro especifico de sitio a no menos de dos tercios del que da el procedimiento general «modified by the site factors in Article 3.10.3.2». Es decir: AASHTO ESPERA que a un sitio licuable le aplique un factor de sitio TABULADO de 3.10.3.2. Eso es incompatible con que la licuefaccion lo hiciera Clase F por si sola.

> **`AASHTO_LRFD_9.10.5.5.2.2#T1`** — La tabla, «Resistance Factors for Geotechnical Resistance of Shallow Foundations at the Strength Limit State», esta transcrita entera en `constantes_normativas.PHI_ZAPATAS_T10_5_5_2_2_1`: portante 0.50 (teorico en arcilla), 0.50 (arena con CPT), 0.45 (arena con SPT), 0.45 (semiempirico), 0.45 (roca), 0.55 (ensayo de placa); deslizamiento 0.90 (prefabricado sobre arena), 0.80 (vaciado in situ sobre arena), 0.85 (concreto sobre arcilla), 0.90 (suelo sobre suelo); pasivo 0.50. Es la tabla que el Manual de Puentes transcribe (2.8.1.1.12.6).

> **`AASHTO_LRFD_9.10.6.1.2#DESPLANTE`** — La regla general de las zapatas superficiales de la Seccion 10: bajo la socavacion, sin margen. La de las estructuras enterradas (12.6.5) le añade 2.0 ft, y es la que el proyecto aplica al cabezal de salida.

> **`AASHTO_LRFD_9.10.6.3.1.1#NIVEL_FREATICO`** — La misma pagina fija q_R = phi_b·q_n (ec. 10.6.3.1.1-1) y manda usar las dimensiones EFECTIVAS de la zapata cuando la carga es excentrica («shall be used instead of the overall dimensions L and B in all equations, tables, and figures pertaining to bearing resistance»): el ensamble calcula q_n con B' = B - 2e de cada combinacion.

> **`AASHTO_LRFD_9.10.6.3.1.2a#QN`** — Ec. 10.6.3.1.2a-1: q_n = c·N_cm + gamma_q·D_f·N_qm·C_wq + 0.5·gamma_f·B·N_gamma_m·C_wgamma, con N_cm = N_c·s_c·i_c, N_qm = N_q·s_q·d_q·i_q y N_gamma_m = N_gamma·s_gamma·i_gamma (ecs. -2 a -4). N_c, N_q y N_gamma, de la Tabla 10.6.3.1.2a-1 (pag. impresa 10-72; `constantes_normativas.FACTORES_CAPACIDAD_CARGA_T10_6_3_1_2A_1`); C_wq y C_wgamma, de la Tabla -2. Los factores de inclinacion de la carga (ecs. -5 a -9, pag. impresa 10-71) usan cargas SIN FACTORAR («H = unfactored horizontal load», «V = unfactored vertical load»), y su comentario PERMITE omitirlos: «In practice, therefore, for footings with modest embedment, consideration may be given to omission of the load inclination factors» (criterio 'factores_inclinacion_carga_portante'). El factor de profundidad d_q «should be used only when the soils above the footing bearing elevation are as competent as the soils beneath the footing level; otherwise … 1.0», y su ecuacion esta verificada para D_f/B de 1 a 8: el ensamble toma d_q = 1.0.

> **`AASHTO_LRFD_9.10.6.3.1.2a#T1`** — 46 filas, phi_f de 0 a 45 grados enteros, transcritas celda a celda y contrastadas con la capa de texto de la pagina por un test. En la misma pagina, la Tabla 10.6.3.1.2a-2 de C_wq y C_wgamma por profundidad del nivel freatico (tres filas: D_w = 0.0, D_w = D_f, D_w > 1.5B + D_f) y la frase «Where the position of groundwater is at a depth less than 1.5 times the footing width below the footing base, the bearing resistance is affected». La tabla no dice que hacer entre filas: el ensamble interpola linealmente y lo declara.

> **`AASHTO_LRFD_9.10.6.3.1.2c#TALUD`** — LA 9.ª EDICION YA NO USA N_cq NI N_gamma_q. La zapata en talud o junto a el se resuelve con un coeficiente de reduccion RC_BC (Leshchinsky, 2015) aplicado a la resistencia de terreno horizontal, ec. 10.6.3.1.2c-1, tabulado en las Tablas 10.6.3.1.2c-1 y -2 (pags. impresas 10-76 y siguientes) por angulo del talud, phi, B/H, retiro b/B y numero de estabilidad N_s = gamma·H_s/c, donde H_s es «height of sloping ground surface below bottom of footing». Los abacos de N_cq y N_gamma_q (Meyerhof, 1957) son los del Manual de Puentes 2016 (Figuras 2.8.1.3.1.2c-1 y -2), que traduce la 7.ª edicion. Las dos tablas de RC_BC NO estan transcritas: con terreno que DESCIENDE delante de la zapata el programa pide los factores del Manual por el criterio 'N_cq_N_gammaq_meyerhof' (ficha T7B-04). El comentario advierte que los RC_BC valen para zapata SIN empotramiento.

> **`AASHTO_LRFD_9.10.6.3.4#RESISTENCIA`** — Ec. 10.6.3.4-1: R_R = phi_tau·R_tau + phi_ep·R_ep (resistencia factorada al deslizamiento; phi de la Tabla 10.5.5.2.2-1). Ec. 10.6.3.4-2: R_tau = C·V·tan(phi_f), con «C = 1.0 for concrete cast against soil» y 0.8 para la zapata prefabricada; V es la fuerza vertical total y phi_f el angulo de friccion interna del suelo drenado. Sobre arcilla (pag. impresa 10-85), con al menos 6.0 in de material granular compactado bajo la zapata, la menor de la cohesion y la mitad del esfuerzo normal: ese caso ESTA implementado (`M9._resistencia_al_deslizamiento`), con la condicion constructiva de las 6.0 in avisada; la nota de la FASE A decia lo contrario (correcciones de T-7b, H8).

> **`AASHTO_LRFD_9.10.7.5#INDICATIVOS`** — PILOTES. La lista de suelo: «resistivity less than 2,000 ohm-cm», «pH less than 5.5», «pH between 5.5 and 8.5 in soils with high organic content», «sulfate concentrations greater than 1,000 ppm», rellenos sanitarios y de escoria, drenaje minero o industrial. La de agua: «chloride content greater than 500 ppm». El comentario C10.7.5 dice que los valores se adaptaron de Fang (1991) y Tomlinson (1987). SON INDICATIVOS («should be considered as indicative») Y MENOS ESTRICTOS que los del 11.10.6.4.2a salvo en el pH: se citan como segunda fuente del mismo cuerpo; los numeros que la matriz compara son los del 11.10.6.4.2a.

> **`AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO`** — El numeral abre en la pag. impresa 11-88 (PDF 1557) y la lista esta en la 11-89: pH = 5 to 10; Resistivity >= 3000 ohm-cm; Chlorides <= 100 ppm; Sulfates <= 200 ppm; Organic Content <= 1 percent. ES UN CRITERIO PARA EL RELLENO DE MUROS DE SUELO REFORZADO CON ACERO GALVANIZADO, no para alcantarillas: define en que suelo valen las tasas de perdida de galvanizado y de acero del propio articulo. El proyecto lo aplica al tubo de acero corrugado galvanizado POR ANALOGIA --mismo metal, mismo recubrimiento, mismo medio--, y por eso el efecto por defecto es un aviso y no una exclusion (criterio 'suelo_agresivo_lrfd_sobre_tmc').

> **`AASHTO_LRFD_9.11.12.8#AGRESIVO`** — Muros de suelo claveteado (soil nail). Repite la lista del 11.10.6.4.2a con «Resistivity >= 3,000 ohm-cm» y «Organic Content <= 1 percent by weight», y añade las dos frases que aquel no trae: basta incumplir UNO de los criterios para que el suelo sea agresivo, y «If the resistivity is greater than or equal 5,000 ohm-cm, the chlorides and sulfates requirements may be waived». Esa dispensa es potestativa y la matriz NO la aplica: es el lado seguro.

> **`AASHTO_LRFD_9.11.5.7#MUROS`** — La oracion anterior manda usar la Tabla 11.5.7-1 «for wall design, unless region-specific values or substantial successful experience is available to justify higher values». La tabla (pag. impresa 11-17, PDF 1486), bloque «Mechanically Stabilized Earth Walls, Gravity Walls, and Semigravity Walls», SI identifica el portante de los muros de gravedad y semigravedad (0.55) y el deslizamiento (1.0): `constantes_normativas.PHI_MUROS_T11_5_7_1`. TENSION que el proyecto declara: el 11.6.3.6 remite el deslizamiento al 10.6.3.4, cuyas ecuaciones nombran los phi de la Tabla 10.5.5.2.2-1 (0.80 vaciado in situ sobre arena). Cual de las dos filas rige en el cabezal es el criterio [A] 'fila_phi_estabilidad_cabezal'; de archivo, la menor.

> **`AASHTO_LRFD_9.11.5.8#EXTREMO`** — NO ES «phi = 1.0» A SECAS: la misma pagina especifica las excepciones. «For overall stability of the retaining wall when earthquake loading is included, a resistance factor, phi, of 0.9 shall be used. For bearing resistance, a resistance factor of 0.8 shall be used for gravity and semigravity walls and 0.9 for MSE walls» (cita gemela #PORTANTE). El deslizamiento si va con 1.0.

> **`AASHTO_LRFD_9.11.5.8#PORTANTE`** — El comentario C11.5.8 da la razon: reducir la posibilidad de que la falla por capacidad portante ocurra antes de que el muro deslice. Vive en `constantes_normativas.PHI_EVENTO_EXTREMO_11_5_8`.

> **`AASHTO_LRFD_9.11.6.3.2#PORTANTE`** — Cargas Y resistencias factoradas. En suelo: «the vertical stress shall be calculated assuming a uniformly distributed pressure over an effective base area», ec. 11.6.3.2-1, sigma_v = ΣV / (B - 2e). En roca, lineal (ecs. -2 a -5, pag. impresa 11-22). El articulo esta escrito para «Abutments and retaining walls» (11.6.3.1): aplicarlo al cabezal es la hipotesis de modelacion del criterio 'marco_estabilidad_cabezal', no un mandato de la fuente.

> **`AASHTO_LRFD_9.11.6.3.3#EXC`** — Es el numeral al que la remision impresa del Manual -- «(11.6.3.3 AASHTO)», bajo su encabezado errado 2.3.1.1.12.3 -- llega: existe, se titula «Eccentricity Limits» y su cuerpo articulado (columna izquierda; el C11.6.3.3 va aparte) impone el mismo limite estatico. La remision es correcta aunque el numeral peruano este mal impreso, que es lo que DIS-MP-NUMERAL-2.3.1.1.12.3 declara. Para roca, la frase hermana dice «middle nine-tenths». En el flujo del PDF «two-thirds» va partido con guion a fin de renglon; la busqueda normalizada lo reconstruye.

> **`AASHTO_LRFD_9.11.6.3.5#PASIVA`** — La frase completa: «…below the depth of maximum scour, freeze-thaw, or other disturbances. In the latter case, only the embedment below the greater of these depths shall be considered effective». El ensamble NO cuenta empuje pasivo delante de la zapata en ningun caso: es el lado seguro, y delante del cabezal esta el cauce, que socava.

> **`AASHTO_LRFD_9.11.6.3.6#DESLIZAMIENTO`** — Remite el deslizamiento del muro al de las zapatas (10.6.3.4).

> **`AASHTO_LRFD_9.11.6.3.7#GLOBAL`** — Sigue en la pag. impresa 11-25: se investiga en Resistencia I con phi = 0.75 (parametros y estratigrafia bien definidos) o 0.65 (muy variables o con informacion limitada), y el comentario dice que equivalen a FS = 1.3 y 1.5. Es E4/E5: el programa NO lo evalua (hace falta un analisis de equilibrio limite con la estratigrafia del EMS) y lo imprime como diferido.

> **`AASHTO_LRFD_9.11.6.5.1#EXC`** — «middle two-thirds», no «tercio central»: es la parte de AASHTO que gana a la errata de traduccion del Manual. Y su comentario C11.6.5.1 ARRANCA en esta misma pagina (columna derecha), no en la 11-26; lo que si esta en la 11-26 es el texto que el repositorio le atribuye.

> **`AASHTO_LRFD_9.11.6.5.2.1#ROCA`** — El 1.2 esta literal, y del lado correcto de la igualdad: es lo que resuelve la errata de imprenta del Manual, cuyo parentesis lo pone a la izquierda.

> **`AASHTO_LRFD_9.11.6.5.2.2#ALTURA`** — La altura h del empuje: desde la base del talon hasta el terreno que queda directamente encima del talon. Con el relleno subiendo detras del muro, h es mayor que la altura del muro; el ensamble la mide asi en las dos condiciones.

> **`AASHTO_LRFD_9.11.6.5.2.2#REDUCCION`** — Es un PERMISO con dos condiciones, escritas en la oracion anterior: «If the wall is free to move laterally under the influence of seismic loading and if lateral wall movement during the design seismic event is acceptable to the Owner». La segunda no es tecnica: la decide el Propietario. Es la fuente del criterio 'factor_muro_eleccion' (de archivo, sin reduccion).

> **`AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION`** — El sujeto es la presion equivalente a la fuerza TOTAL estatica mas sismica, P_AE: su resultante no baja de H/3. Con relleno inclinado, «this force shall be distributed over the total height, h».

> **`AASHTO_LRFD_9.11.6.5.3#VALIDEZ`** — El sujeto es «The M-O Method». Tres condiciones: (1) el material detras del muro se aproxima a un suelo uniforme y sin cohesion en la cuña 3H:1V desde el talon; (2) «the backfill is not saturated and in a loose enough condition such that it can liquefy during shaking»; (3) «the combination of peak ground acceleration and backslope angle do not exceed the friction angle of the soil behind the wall», ec. 11.6.5.3-1: phi >= i + arctan[kh/(1 - kv)]. Fuera de ellas: «For wall geometry or site conditions for which the M-O Method is not suitable, the GLE Method should be used». El programa no implementa el metodo GLE: fuera del dominio se detiene con «metodo no evaluable», no fuerza la ecuacion (el comentario desaconseja poner el radicando en cero).

> **`AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE`** — El comentario da los ejemplos: «integral abutments, abutment walls with structural wing walls, tunnel portal walls, and tied back cylinder pile walls», y añade que para ellos una resultante en h/2 «may be warranted». Un cabezal monolitico con el barril y con aleros estructurales se parece a ese caso: es coherente con no reducir kh ('factor_muro_eleccion' = sin reduccion).

> **`AASHTO_LRFD_9.11.6.6#DRENAJE`** — La alternativa es de la fuente: o el relleno se drena, o el muro se diseña con la hidrostatica completa del agua del relleno. El comentario avisa que los lloraderos solos no bastan: «Weep holes or geocomposite panel drains at the wall face do not assure fully drained conditions. Drainage systems should be designed to completely drain the entire retained soil volume». La fuente no dice hasta que nivel sube el agua de un relleno sin drenar: el proyecto LEE hasta la superficie del relleno retenido (criterio 'drenaje_trasdos').

> **`AASHTO_LRFD_9.12.10.2.1#VAF`** — W_E = F_e w B_c H (Eq. 12.10.2.1-1). Tabla 12.10.2.1-3 (pag. 12-53): VAF 1.35 / 1.40 / 1.40 / 1.45 para los Tipos 1 a 4. Los requisitos de cada tipo, Tabla 12.10.2.1-1 (pag. 12-50).

> **`AASHTO_LRFD_9.12.10.2.2`** — 62.4 lb/ft3 = 9.80 kN/m3; el programa usa el peso especifico del agua de constantes_fisicas (9.81 kN/m3), la misma magnitud fisica: 0.1 % de diferencia, del lado mayor.

> **`AASHTO_LRFD_9.12.10.4.3.1`** — D = (12/S_i)((W_E + W_F)/B_FE + W_L/B_FLL) (Eq. 12.10.4.3.1-1, en kip/ft y pulgadas): en SI, D en N/m/mm con W en N/m y S_i en mm, sin factor de unidad. Es estado limite de SERVICIO: sin factores de carga ni de resistencia.

> **`AASHTO_LRFD_9.12.10.4.3.2a`** — Tabla 12.10.4.3.2a-1: B_FE por diametro (12, 24, 36, 72 y 144 in) y tipo de instalacion; «For pipe diameters other than those listed ... may be determined by interpolation».

> **`AASHTO_LRFD_9.12.11.1`** — El Art. 12.11 se titula «REINFORCED CONCRETE CAST-IN-PLACE AND PRECAST BOX CULVERTS AND REINFORCED CAST-IN-PLACE ARCHES» (partido en tres renglones en la misma pagina; por eso no va en `jerarquia_numeral`). Rige el diseño estructural del marco in situ Y del prefabricado; y su cuarto parrafo dice que las dimensiones ESTANDAR del prefabricado estan en «AASHTO M 259 (ASTM C789) and M 273 (ASTM C850)»: para el in situ no hay dimensiones estandar, se proyectan. Es la mitad de diseño del rotulo de M2: «diseño LRFD Sec. 5 y Art. 12.11».

> **`AASHTO_LRFD_9.12.11.2.2.1`** — W_E = F_e gamma_s B_c H con F_e = 1 + 0.20 H/B_c (Eqs. 12.11.2.2.1-1 y -2).

> **`AASHTO_LRFD_9.12.12.2.2`** — Eq. 12.12.2.2-2: Delta_t = K_B(D_L P_sp + C_L P_L) D_o / (1000(E_p I_p/R^3 + 0.061 M_s)) + eps_sc D; «D_L ... a value of 1.5 is typical» y «K_B ... a value of 0.10 is typical». El 1000 es el paso de ksi a psi: en SI desaparece.

> **`AASHTO_LRFD_9.12.12.3.10.1b#STUB`** — A_eff = P_st K_t / F_u <= A_g (Eq. 12.12.3.10.1b-5); K_t de la Tabla 12.12.3.10.1b-1 (PE: 0.9 inicial, 0.3 a 50 años, 0.25 a 75).

> **`AASHTO_LRFD_9.12.12.3.10.1c#EP`** — Es la definicion de E_p en las Eqs. 12.12.3.10.1c-1 y -2. De ella lee el proyecto que la deformacion se SUMA por duracion: la de las cargas permanentes con el modulo y el area efectiva de largo plazo y la de la carga viva con los iniciales (Interpretacion en el paso F8.EMPUJE).

> **`AASHTO_LRFD_9.12.12.3.10.1e`** — eps_bck = 1.2 C_n (E_p I_p)^(1/3) [phi_s M_s (1-2nu)/(1-nu)^2]^(2/3) R_h / (A_eff E_p), R_h = 11.4/(11 + D/(12H)), C_n = 0.55 (pag. 12-87). Adimensional en cualquier sistema coherente de unidades.

> **`AASHTO_LRFD_9.12.12.3.2`** — La frase empieza al pie de la pag. 12-75 (PDF 1713): «Section properties for thermoplastic pipe, including wall area, moment of inertia, and profile geometry should», y termina en la 12-76. El verbo es «should»: RECOMENDACION. El titulo del numeral esta en la PDF 1713.

> **`AASHTO_LRFD_9.12.12.3.3#PANDEO`** — La frase anterior deja al Ingeniero la eleccion entre propiedades iniciales y de largo plazo «Except for buckling». Es lo que manda el pandeo general del HDPE: TODO con el modulo de la vida de diseño (50 o 75 años), tambien la parte de la carga viva. La FASE A de T-5 sumaba el pandeo por duracion (la carga viva con el modulo inicial) y no citaba esta frase.

> **`AASHTO_LRFD_9.12.12.3.5`** — Eqs. 12.12.3.5-1 a -8, leidas renderizadas; K_gammaE «installation factor typically taken as 1.5 to provide traditional safety» (misma pagina); K_2 = 1.0 para el empuje en el arranque (pag. 12-79).

> **`AASHTO_LRFD_9.12.12.3.6`** — Eq. 12.12.3.6-1: FF = S^2/(E I), con I el momento de inercia (in4/in), E el modulo de elasticidad INICIAL (ksi) y S el «diameter of pipe» (in). La norma no dice que diametro: el proyecto toma el EXTERIOR, que da el FF mayor.

> **`AASHTO_LRFD_9.12.4.2.4`** — LA NORMA DE PRODUCTO DEL CAJON PREFABRICADO ES M 259 / M 273, y las dos estan AUSENTES de normas/ (`fuentes.AASHTO_M259`, `AASHTO_M273`). Es lo que sostiene la decision de docs/ruta_familia_c.md §14.1 --- marco VACIADO IN SITU --- y el rotulo «sin norma de producto» que M2 imprime para la seccion rectangular (EXT-N-03): un marco in situ no es un producto que se compra contra una especificacion, y rotularlo con la norma del tubo (M 170M) era una atribucion falsa.

> **`AASHTO_LRFD_9.12.5.4`** — Con eta_D = 1.00 (diseño convencional) y eta_R = 1.00 (redundante), el modificador de la carga es el de importancia operativa, que declara el propietario (MP.2.3.2.5).

> **`AASHTO_LRFD_9.12.5.5`** — Tabla 12.5.5-1 (pag. 12-12): tubo metalico helicoidal, area y pandeo 1.00; anular remachado o empernado, area y pandeo 1.00 y costura longitudinal 0.67; PE: empuje 1.00, rigidez del suelo 0.90, pandeo global 0.70, flexion 1.00.

> **`AASHTO_LRFD_9.12.5.6.1#FF`** — Tabla 12.5.6.1-1: acero, corrugacion de 0.25 y 0.5 in, 43 in/kip (= 0.2455 mm/N); 1.0 in, 33 in/kip. Coincide con ASTM A796 num. 10.3 para terraplen (0.245 mm/N con 13 mm): no hay discrepancia. C12.5.6.1: son exigencias CONSTRUCTIVAS, no un estado limite de servicio.

> **`AASHTO_LRFD_9.12.5.6.3`** — 95.0 in/kip = 0.5425 mm/N. Vista de calculo: FF_LIMITE_TERMOPLASTICO_MM_N.

> **`AASHTO_LRFD_9.12.6.1#FLOTACION`** — ES LA UNICA APARICION DE «flotation» EN LAS 1905 PAGINAS del PDF, medida. Y trae su propia CONDICION DE DISPARO -- «with inverts below the water table» --, que es la que hace de esta verificacion algo que no siempre aplica: sin freatico sobre el invert no hay nada que evaluar. NO SE LEE SOLA: dos frases mas abajo, EN EL MISMO PARRAFO de este mismo numeral, esta `AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX`, que manda aplicar el factor MAXIMO de EV -- lo contrario de lo que V7 hace --. C7 cito esta frase y elidio aquella, y lo encontro su auditoria adversarial: recortar un parrafo justo antes de la frase que discute tu propia lectura es la forma NOR-HID-01 aplicada a un recorte. La discusion esta registrada en DIS-AASHTO-GAMMA-EV-12.6.1.

> **`AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX`** — PARRAFO PROPIO dentro del num. 12.6.1, inmediatamente despues de la frase de flotacion y antes de la de reparto de carga de rueda. ES `lex specialis` PARA ESTRUCTURAS ENTERRADAS y dice MAXIMO, mientras el Art. 3.4.1 -- que el Manual de Puentes traduce en 2.4.5.3.1 -- manda investigar el MINIMO cuando la carga permanente aumenta la estabilidad. Los dos son `shall`. QUE NO SE DEDUZCA DE AQUI: que V7 este mal. Aplicar el maximo a EV en una verificacion de FLOTACION haria la comprobacion MAS FACIL, no mas exigente, porque ahi EV estabiliza -- medido sobre la corrida del entregable de C7: el lado estabilizante pasaria de 23.256 a 34.884 kN/m contra los mismos 20.405 de subpresion, y el margen se multiplicaria por cinco --. Esa es justamente la razon de que el proyecto lea esta frase como referida al diseno POR empuje de tierra y no al equilibrio de flotacion. Pero es una LECTURA: el texto no trae esa salvedad, y por eso vive en DIS-AASHTO-GAMMA-EV-12.6.1 y no en un comentario.

> **`AASHTO_LRFD_9.12.6.2.3#UPLIFT`** — SEGUNDA exigencia, acumulativa con la del 12.6.1 y no redundante: aquella manda EVALUAR la carga de flotacion y esta manda CONSIDERAR el levantamiento. Su condicion de disparo es el nivel freatico MAS ALTO previsto, que es la hipotesis que V7 adopta.

> **`AASHTO_LRFD_9.12.6.5#ALEROS`** — Pide alargar los aleros hasta proteger el relleno estructural que rodea al conducto, sin dar una longitud. La longitud de los aleros del programa sale de la geometria del talud (hasta que baja a la altura final declarada), que es una regla del proyecto [A] y no de esta frase.

> **`AASHTO_LRFD_9.12.6.5#DENTELLON`** — Es el dentellon (cut-off wall) del borde de la losa de entrega: bajo la socavacion maxima prevista. La misma frase admite la alternativa «or a paved invert»; el proyecto declara las dos cosas -- losa Y dentellon --, que es lo que dibujan las Laminas 02 y 02-A del Manual («LOSA INFERIOR» y «UÑA»).

> **`AASHTO_LRFD_9.12.6.5#ZAPATAS`** — Articulo de la Seccion 12 (estructuras enterradas: las alcantarillas). Abre con «Buried structures shall be designed so that no movement of any part of the structure will occur as a result of scour». El proyecto LEE que el cabezal de salida es parte de la estructura y que su zapata es una de esas «footings»: es una lectura, y por eso la regla es [C] y no [N] (la hoja de ruta pone la Seccion 12 de AASHTO como [C], tabla de la §0.1). 2.0 ft = 0.6096 m exactos (1 ft = 0.3048 m).

> **`AASHTO_LRFD_9.12.6.6.3#COBERTURA`** — El ARTICULO abre en la pag. impresa 12-21; solo la TABLA esta en la 12-22. Y una correccion contra la ficha de auditoria, no contra el repositorio: NOR-VAC-01 transcribe la fila de Reinforced Concrete Pipe como «raiz(Bc)/8» y el PDF imprime «B'c/8», con Bc' definido en 12-21 como «out-to-out vertical rise of pipe». Es una PRIMA, no un radical: artefacto de la linearizacion de la capa de texto. Corregir en la ficha antes de derivar cualquier numero.

> **`AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA`** — Es la UNICA regla de la Sec. 12 sobre la cobertura de un CAJON de concreto, y esta en el articulado 12.6.6.3, debajo de la Tabla 12.6.6.3-1 (que no tiene fila de cajon de concreto: `AfirmacionNegativa` SIN_CAJON_DE_CONCRETO_T12663). No fija una cobertura minima: ADMITE el cajon sin cobertura y a cambio exige diseñar la losa superior para la carga vehicular directa. Junto con el num. 4.1.1.3.4 a) del Manual (`MC_HHD.4.1.1.3.4a#NIVELES`: la rasante puede coincidir con la losa) y la Lamina N 03 (que dibuja el marco en cruce de canal sin relleno acotado), sostiene que el piso de 0.3048 m del criterio 'cobertura_minima_cajon' [A] es MAS RESTRICTIVO que la fuente: por eso G1 del marco AVISA y no bloquea cuando solo falta esa cobertura (auditoria de T-3, H5).

> **`AASHTO_LRFD_9.12.7.2.2`** — T_L = P_FD(S)/2 + P_FL(C_L)F_1/2; C_L = l_w <= S; F_1 = 0.75S/l_w >= F_min; F_min = 15/(12(S)) >= 1. P_FD «as specified in Article 12.12.3.4 with VAF taken as 1.0 and D_o taken as S»: la lectura del proyecto de esa remision esta en la Interpretacion del paso.

> **`AASHTO_LRFD_9.12.7.2.4`** — Ecs. 12.7.2.4-1 y -2 con k = «soil stiffness factor taken as 0.22» (misma pagina); C12.7.2.4 lo llama conservador.

> **`AASHTO_LRFD_9.12.7.2.5`** — Solo para costura LONGITUDINAL: la tuberia helicoidal con costura engargolada o soldada no la tiene (ASTM A796 num. 8.1.3.1). La resistencia nominal de la costura remachada de 68 x 13 mm esta en la Tabla 5 de A796 (tabla ASTM_A796.T5) y en la Tabla A12-7 de AASHTO; la EMPERNADA de esa corrugacion no esta en ninguna de las dos.

> **`AASHTO_LRFD_9.3.10.2#CLASE_F`** — AQUI ESTA EL `SHALL`, Y EL REPOSITORIO CITABA EL TEXTO MAS DEBIL DE LOS TRES. La segunda condicion de la lista es «The site is classified as Site Class F (Article 3.10.3.1),», y el verbo de la frase que la introduce es `shall`. La Nota 2 de las tablas de factores -- que es lo que Sec. 0.5 y el criterio venian citando -- dice `should`, y el Art. 3.10.2.2 (pag. impresa 3-100) repite el `shall`. La afirmacion del expediente («AASHTO exige de forma incondicional un estudio de respuesta de sitio para la Clase F») es CIERTA; lo que estaba mal era el anclaje, que se apoyaba en una recomendacion para sostener una exigencia. No es una discrepancia -- las fuentes no se contradicen --, es una cita corta.

> **`AASHTO_LRFD_9.3.10.2.2`** — «6 miles» esta literal; cualquier conversion a km (9.66) es del proyecto. Y `shall be CONSIDERED`: obliga a considerar el estudio, no a hacerlo. La remision al USGS Active Fault Map tambien es literal, y es el punto: ese mapa no cubre el Peru.

> **`AASHTO_LRFD_9.3.10.3.1`** — LA CLASE DE SITIO ES UNA MEDICION, y de ahi cuelga la etiqueta del criterio: se determina por la RIGIDEZ medida (v_s, N o s_u) sobre una profundidad fija, no por una eleccion del proyectista. PROFUNDIDAD: el articulado dice «the upper 100 ft» -- 30.48 m --, no «30 m»; ver DIS-HR-30M-VS-100FT. Y dos erratas de la fuente que se conservan en el verbatim de la primera oracion cuando se cite entera: «A though F» por «through», y la falta de punto tras «100 ft».

> **`AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES`** — LA CITA QUE CIERRA EL CONFLICTO #8, y estaba en el articulado sin que nadie la hubiera leido. El expediente no necesitaba una autorizacion para suponer la Clase F: tenia una PROHIBICION expresa de suponerla, con dos puertas de salida que no tiene abiertas -- determinacion de la autoridad competente, o dato geotecnico -- porque el SPT esta pendiente. Y la misma nota trae un DEBER POSITIVO que es la otra mitad: «Where the soil properties are not known in sufficient detail to determine the site class, a site investigation shall be undertaken sufficient to determine the site class». No dice «no supongas y sigue»: dice INVESTIGA. ES ARTICULADO, no comentario: va al pie de la Tabla 3.10.3.1-1, en la columna de especificacion. El `should not` de AASHTO lo endurece el Manual de Puentes a «no seran supuestas».

> **`AASHTO_LRFD_9.3.10.3.1#INVESTIGACION`** — Es la PRIMERA oracion del bloque «Exceptions» y precede a la prohibicion de suponer E o F: el orden de la fuente es investigar primero y no suponer despues. Se registra aparte porque es una exigencia distinta -- un deber de hacer, no una prohibicion -- y porque la memoria la cita por su cuenta al declarar que ensayo cierra el vacio.

> **`AASHTO_LRFD_9.3.11.5.2#K0`** — Ec. 3.11.5.2-1: k_o = 1 - sen(phi'_f). Vale para muro vertical y TERRENO HORIZONTAL: detras del cabezal el relleno sube, y el K0 que la interfaz de T-7c imprime es una referencia del orden de magnitud del empuje de un muro que no cede, no el coeficiente de ese relleno.

> **`AASHTO_LRFD_9.3.11.5.3#CULMANN`** — La Figura 3.11.5.3-1 es la del muro con un relleno de talud UNIFORME. El relleno detras del cabezal sube con el talud del terraplen y se quiebra en la plataforma: se aparta de la figura, y la fuente permite entonces la cuña de tanteo de Culmann. Es la regla de archivo de 'regla_pendiente_relleno_trasdos' («cuna_de_tanteo», `M9.cuna_de_tanteo`). La frase sigue: «(e.g., see Terzaghi et al., 1996)».

> **`AASHTO_LRFD_9.3.11.5.8.1#CUNA`** — ES DE LOS MUROS DE SUELO REFORZADO (3.11.5.8): para el relleno quebrado («broken back») la fuente recomienda la cuña de tanteo o el GLE, y su comentario permite la pendiente equivalente simplificada (cita AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO). Aplicada al cabezal por ANALOGIA: el criterio 'regla_pendiente_relleno_trasdos' lo declara.

> **`AASHTO_LRFD_9.3.11.6.4`** — El articulo entero, sus dos tablas y su comentario C3.11.6.4 caben en la pag. impresa 3-151; no continua en la 3-152, donde empieza el 3.11.6.5. La frase de la interpolacion es EXIGENCIA («shall»); la de tomar valores de las tablas es PERMISO («may be taken»).

> **`AASHTO_LRFD_9.3.11.6.4#ALTURA`** — La altura que entra en las tablas NO es la altura visible del muro: incluye la zapata. Con `GeometriaCabezal` eso es H + espesor_zapata. Medirla sin la zapata SUBESTIMA la altura y, como h_eq decrece con ella, SOBRESTIMA h_eq -- conservador, pero es la lectura equivocada de la tabla.

> **`AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO`** — Es el caso que este programa NO implementa: con menos de 2.0 ft (0.6096 m) de relleno sobre un tubo de concreto la Fase 8 se detiene con MetodoNoEvaluableError en vez de aplicar fuera de su dominio la distribucion de 3.6.1.2.6b.

> **`AASHTO_LRFD_9.3.6.1.2.6a#EJES`** — «respectively shall» SIN coma: asi lo entrega la capa de texto del ejemplar. Es lo que deja fuera la carga de carril del HL-93: en una alcantarilla solo cuentan los ejes del camion y del tandem.

> **`AASHTO_LRFD_9.3.6.1.2.6a#RELLENO`** — ES EL METODO DE LA CARGA VIVA SOBRE EL CONDUCTO, y tiene DOS dominios distintos: mas de 1.0 ft de relleno para la tuberia que no es de concreto y 2.0 ft o mas para el tubo de concreto. Por debajo el mismo numeral manda otra cosa (Eq. 4.6.2.10.2-1 para el tubo de concreto, «more comprehensive methods» con menos de 1.0 ft), que este programa no implementa: lo dice como metodo no evaluable. El Manual de Puentes no transcribe este numeral (su 2.4.3.2 trae el HL-93 y el 2.4.3.3.2 el IM de lo enterrado, no la distribucion a traves del relleno): por eso es [C].

> **`AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL`** — El trafico «paralelo al vano» es el de la inmensa mayoria de las alcantarillas viales (C3.6.1.2.6b, misma columna de la pag. 3-27): el vano de un tubo es su diametro, medido a lo largo de la via. La lectura de que las obras de este expediente caen ahi es del proyecto y la dice el paso de la carga viva.

> **`AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS`** — La segunda mitad del permiso de #DESPRECIABLE: en una alcantarilla de VARIOS vanos la condicion no es la luz de un vano sino la distancia entre las caras interiores de los muros extremos. El marco de varias celdas la usa (`M8.demanda_marco`); el permiso solo se toma si 'carga_viva_bajo_relleno_alto' lo declara.

> **`AASHTO_LRFD_9.3.6.1.2.6b#PL`** — Las ecuaciones 3.6.1.2.6b-1 a -7 (pags. 3-27 y 3-28) se leyeron renderizadas: H_int-t = (s_w - w_t/12 - 0.06 D_i/12)/LLDF; w_w = w_t/12 + LLDF(H) + 0.06 D_i/12 (mas s_w si H >= H_int-t); H_int-p = (s_a - l_t/12)/LLDF; l_w = l_t/12 + LLDF(H) (mas s_a si H >= H_int-p); P_L = P(1 + IM/100)(m)/A_LL. La ec. -1 escribe D_j y la lista de simbolos D_i: errata tipografica de la fuente, el simbolo es el mismo. Las cifras en pulgadas y pies se convierten a SI una sola vez (constantes_fisicas).

> **`AASHTO_LRFD_9.3.7.2`** — «all components below design water level»: el mismo ambito neutro que el numeral peruano. Es DEFINITORIA de la fuerza; quien pone la condicion de disparo para una estructura enterrada es el 12.6.1, que remite aqui expresamente.

> **`AASHTO_LRFD_9.5.10.1`** — El factor por relacion agua-cemento NO es opcional: la norma dice `shall`, y esta en el CUERPO ARTICULADO (columna izquierda), no en el comentario. Sostiene NOR-AAS-05.

> **`AASHTO_LRFD_9.5.10.1#ESTRIBOS`** — EL TERCER TEXTO QUE CONDICIONA LA TABLA 5.10.1-1, y el ultimo: la cadena «Table 5.10.1-1» aparece en TRES paginas de toda la especificacion -- 5-167, 5-168 y 5-169 -- y en ninguna mas, de modo que la lista de condicionantes esta cerrada, no muestreada. ESTE PROYECTO NO LO CONSUME: dimensiona barras PRINCIPALES, y la regla es de estribos y zunchos. Se registra porque «tabla transcrita completa» incluye lo que la condiciona, y porque su forma -- restar 0.5 in con piso de 1.0 in -- NO es un `Modificador` del registro, que es multiplicativo: meterla ahi seria una lectura falsa del tipo, que es justo lo que el esquema existe para impedir.

> **`AASHTO_LRFD_9.5.10.1#PISO`** — El piso absoluto sobre las barras principales, que es lo que impide que el factor de 0.8 del W/CM lleve el recubrimiento a cualquier cosa. El Manual de Puentes lo traduce como «1.0 in (25 mm)» y el proyecto aplica la PULGADA EXACTA (25.4 mm), que es la mayor de las dos cifras que la propia fuente peruana escribe.

> **`AASHTO_LRFD_9.A11.3.1#KAE`** — El ENCABEZADO del articulo se imprime en la pag. impresa 11-144 (PDF 1613) y la ECUACION en la 11-145 (PDF 1614). La forma exacta del corchete -- «[1 + raiz(...)]» -- NO ES VERIFICABLE por extraccion de texto: la capa devuelve la formula rota. Se decide sobre la imagen renderizada, y por eso el metodo es IMAGEN. Las unidades de la fuente son imperiales (kcf, ft).

> **`AASHTO_LRFD_9.C10.5.5.2.2#ASD`** — El comentario dice de donde salen los phi: de la calibracion contra los FS de tensiones admisibles. Los FS de E.050 (3,0 y 2,5 al portante; 1,5 al deslizamiento) son esos mismos, de modo que los dos marcos son dos escrituras de un nivel de seguridad parecido y por eso se pueden imprimir lado a lado SIN mezclar sus numeros.

> **`AASHTO_LRFD_9.C10.6.3.3#EQUIVALENCIA`** — El articulo (pag. impresa 10-83) fija el limite «evaluated based on factored loads»: un tercio de la dimension de la zapata en suelo, 0.45 en roca. Este comentario dice de donde sale: B/3 sobre cargas FACTORADAS equivale a B/6 sobre cargas de SERVICIO. Es la razon de la regla de no cruce: comparar e de servicio con B/3, o e factorada con B/6, mezcla los dos marcos.

> **`AASHTO_LRFD_9.C11.5.6#FIGURAS`** — SON DOS FIGURAS, leidas por imagen (los factores estan dibujados, no en la capa de texto). C11.5.6-1, «…for Bearing Resistance»: 1.25 DC en el muro, 1.35 sobre el relleno del talon, y el empuje EH inclinado delta sobre el plano vertical que sube del talon, con 1.50 EH cos(delta) horizontal y 1.50 EH sen(delta) vertical. C11.5.6-2, «…for Sliding and Eccentricity»: 0.90 DC, 1.00 sobre el relleno del talon y el mismo 1.50 en las dos componentes de EH. EL RELLENO DEL TALON VA ROTULADO «EH» EN LAS DOS FIGURAS DE ESTE EJEMPLAR («1.35 EH», «1.00 EH»): son los gamma_p maximo y minimo de EV para muros de la Tabla 3.4.1-2, y la Figura C11.5.6-4 de la pagina 11-15 rotula esa misma carga «1.00 EV». Se lee como EV: es un rotulo errado de la figura, no un factor distinto. La Figura C11.5.6-4 (Evento Extremo I, pag. impresa 11-15, PDF 1484): 1.00 DC, 1.00 EV, 1.00 P_AE cos(delta), 1.00 P_AE sen(delta) y 1.00 P_IR sobre el muro y sobre el relleno del talon.

> **`AASHTO_LRFD_9.C11.5.6#SOBRECARGA`** — La oracion arranca en la pag. impresa 11-11: «Where live load surcharge is applicable, the factored surcharge force is generally included over the backfill immediately above the wall only for evaluation of foundation bearing resistance and structure design, as shown in Figure C11.5.6-3. The live load surcharge is not included over the backfill for evaluation of eccentricity, sliding…». Es decir: el PESO de la sobrecarga viva sobre el talon entra solo en el portante; su EMPUJE entra siempre. Y: «The load factor for live load surcharge is the same for both vertical and horizontal load effects»; en Evento Extremo I ese factor es gamma_EQ. El mismo comentario fija que el factor de WA «is always 1.0».

> **`AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA`** — Es el comentario que dice por que el marco LRFD NO TIENE factor de seguridad al volteo: lo REEMPLAZAN el limite de excentricidad y la presion de contacto. Por eso la fila E2 del marco LRFD es la excentricidad (e <= B/3 en suelo, sobre cargas factoradas) y la del marco ASD el cociente de momentos de E.050 39.13.6: son dos verificaciones distintas con el mismo numero de fila, y no se cruzan.

> **`AASHTO_LRFD_9.C11.6.5.3#CUNA`** — Es lo que sostiene la cuña pseudoestatica bajo sismo (`M9.cuna_de_tanteo` con k_h y k_v): con el relleno que sube y se quiebra en la plataforma, Mononobe-Okabe con una pendiente equivalente queda fuera de su dominio con el k_h de archivo, y la cuña da cifra. La condicion de la frase -- suelo no estratificado detras del muro -- es la del relleno compactado del trasdos. El mismo comentario añade que estos metodos de equilibrio limite «may be overly conservative».

> **`AASHTO_LRFD_9.C11.6.5.3#RESULTANTE`** — DESCRIBE la practica anterior (Seed y Whitman, 1970), no la prescribe: «Past practice … has been to either assume a uniform distribution … or, if the static and seismic components of earth pressure are treated separately, using an inverted trapezoid for the seismic component, with the seismic force located at 0.6h». El mismo comentario añade que la investigacion mas reciente situa la resultante del empuje TOTAL en h/3, que como minimo no debe quedar por debajo de la estatica, y que «a slightly higher combined static/seismic resultant location (e.g., 0.4h to 0.5h) may be considered». La fraccion se aplica al INCREMENTO (P_AE - P_A), no al total: con 0.6h en el incremento y h/3 en el estatico, la resultante combinada cae entre 0.4h y 0.5h. Es la fuente del criterio [C] 'punto_aplicacion_incremento_sismico'.

> **`AASHTO_LRFD_9.C11.6.5.4#CEDENTE`** — Es la hipotesis del empuje activo y de Mononobe-Okabe: el muro CEDE. El criterio 'regimen_cabezal' la declara para la estabilidad externa del cabezal. Sigue: «Examples of walls that may be nonyielding are integral abutments, abutment walls with structural wing walls, tunnel portal walls, and tied back cylinder pile walls», y para los suelos granulares la resistencia se moviliza con un desplazamiento de la corona «about 0.5 percent of the abutment or wall height».

> **`AASHTO_LRFD_9.C11.6.5.4#K0`** — Liga el muro que no cede con el empuje en REPOSO (K0) en el estado limite de resistencia. Es lo que la interfaz de T-7c marca: las solicitaciones salen con el coeficiente del muro que cede y llevan al lado el K0 de 3.11.5.2 (cita AASHTO_LRFD_9.3.11.5.2#K0).

> **`AASHTO_LRFD_9.C12.12.3.2`** — Comentario. La frase empieza en la pag. 12-75: «Historically, AASHTO bridge specifications have contained minimum values for the moment of inertia and wall area of thermoplastic pipe; however, these values», y sigue en la 12-76: «... Thus, there is no way to provide meaningful generic information on section properties.» Son los minimos de la Tabla A12-11: con ellos el resultado es una COTA INFERIOR, no un veredicto sobre un producto (`M8.cota_inferior_hdpe`).

> **`AASHTO_LRFD_9.C12.6.2.3`** — DICE «the culvert», NO «pipe», y eso importa: es de las pocas frases de la Sec. 12 sobre flotacion que no se restringe a tuberia. Pero es comentario y dice `should`: sostiene la FORMA de la comparacion -- peso de la clave contra empuje -- y no el criterio de aceptacion. Un factor de seguridad numerico NO sale de aqui, y atribuirselo seria inventarle una exigencia.

> **`AASHTO_LRFD_9.C12.6.9#NIVEL_4`** — SEGUNDA FUENTE DEL CORTE DE 15 ft/s, y dice lo mismo que la primera: es un NIVEL de abrasion de la FHWA (carga de fondo pesada Y velocidad), no un techo de velocidad. Los otros tres niveles, en la misma columna: Level 1 sin carga de fondo y velocidades muy bajas; Level 2 «velocities of 5.0 ft/s or less»; Level 3 «between 5.0 ft/s and 15.0 ft/s». El corte inferior es 5.0 ft/s aqui y 6 ft/s en la Tabla 8-4 de WSDOT: las dos clasificaciones no coinciden por abajo y si por arriba. El articulado 12.6.9 (misma pagina) no fija ningun limite: pide que la vida util del material iguale o supere la de la alcantarilla y nombra los remedios usuales para el metal («increased gauge thickness», «protective linings»).

> **`AASHTO_LRFD_9.C3.10.3.1-1#PASO1`** — ES COMENTARIO Y POR ESO NO ESTRECHA EL ARTICULADO -- lleva prefijo `C` y cuelga del epigrafe C3.10.3.1 --, pero importa por algo que el debate «lista abierta o cerrada» estaba tapando: el paso 1 no es retorico, es un PROCEDIMIENTO. Manda comprobar esas categorias y, si el sitio no cae en ninguna, seguir al paso 2 (capa blanda -> Clase E) y al paso 3 (calcular v_s, N o s_u sobre los 100 ft superiores -> Clase A a E). En ninguno de los tres pasos hay una ruta que lleve de «suelo licuable» a la Clase F. Refuta por su cuenta la version fuerte de NOR-AAS-02 que la refutacion adversarial R95-073 ya habia tumbado: el «the three categories» existe, pero esta aqui, no en el articulado.

> **`AASHTO_LRFD_9.C3.11.5.3#DELTA`** — La oracion completa (la capa de texto pierde las letras griegas): «Alternatively, long-term practice has been to use delta = 0.67·phi_f at the interface between the back of the wall and the retained soil to calculate ka for soil against concrete as well as soil against soil». DESCRIBE una practica («long-term practice»), no fija el valor; antes ofrece la Tabla C3.11.5.3-1 (pag. impresa 3-124) de valores «presumptive». En la pagina siguiente: aun en los muros de semigravedad en voladizo, donde la superficie de friccion es suelo contra suelo, «the wall friction is usually limited to 0.67·phi_f». Es la fuente del criterio [C] 'fraccion_delta_sobre_phi_trasdos'.

> **`AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON`** — FIJA EL PLANO DE EMPUJE del muro en voladizo con talon: el vertical que sube desde el extremo del talon, con el suelo que queda entre ese plano y la pantalla contado como peso del muro (es la carga EV del ensamble). Sobre ese plano la friccion es suelo contra suelo, y la Figura C3.11.5.3-1b (leida por imagen, pag. impresa 3-123) acota el angulo del empuje entre phi/3 y 2·phi/3. Es lo que cierra la eleccion que `M9.empujes_trasdos` dejaba al llamador («el plano del trasdos o el del talon»).

> **`AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO`** — ES DE LOS MUROS DE SUELO REFORZADO (3.11.5.8, «Lateral Earth Pressures for Mechanically Stabilized Earth Walls»), y el articulo dice lo que la regla general pide: «For “broken back” soil surcharge conditions, a generalized limit equilibrium (GLE) analysis, as presented in Article A11.3.3, or a Coulomb trial wedge analysis should be used». El comentario PERMITE la alternativa simplificada de la Figura C3.11.5.8.1-1 (pag. impresa 3-138, PDF 192, leida por imagen): la pendiente equivalente del relleno es la de la recta que une la coronacion del muro con el terreno a una distancia horizontal 2H detras de el, y el empuje actua inclinado delta sobre la altura h del plano vertical trasero. Aplicarla al cabezal -- cuyo relleno sube con el talud del terraplen y se quiebra en el borde de la plataforma -- es una ANALOGIA, que el criterio 'regla_pendiente_relleno_trasdos' declara.

> **`AASHTO_LRFD_9.C3.11.6.4`** — HALLAZGO DE S12, y es el que obliga a matizar el conflicto #4: NO EXISTE en el articulado ninguna frase que reparta las dos tablas. El cuerpo normativo las cita JUNTAS Y SIN CONDICIONANTE («may be taken from Tables 3.11.6.4-1 and 3.11.6.4-2»). Lo que las reparte son (a) los TITULOS de las tablas y (b) este comentario, que no es articulado. Y no ofrecen un eje libre «orientacion»: ofrecen dos BINOMIOS ACOPLADOS -- estribo+perpendicular y muro de contencion+paralelo --. No hay tabla para «muro perpendicular» ni para «estribo paralelo».

> **`AASHTO_LRFD_9.C3.4.1#GAMMA_EQ`** — EL 0.50 ESTA LITERAL EN LA FUENTE, pero como COMENTARIO y con el calificador «is reasonable»: no es una exigencia ni una de dos opciones tabuladas. Y el 0.0 aparece solo como referencia a ediciones pasadas del Standard Specifications, seguido de «This issue is not resolved». Quien lo determina es el PROYECTO («project-specific basis», Art. 3.4.1, pag. impresa 3-19), no «el propietario».

> **`AASHTO_LRFD_9.T12.10.2.1-1`** — La fila del Tipo 4, riñones y costado inferior. Las otras tres (misma pagina): Tipo 1, riñones 95 % Categoria I, costado 90 % I, 95 % II o 100 % III; Tipo 2, riñones 90 % I o 95 % II, costado 85 % I, 90 % II o 95 % III; Tipo 3, riñones y costado 85 % I, 90 % II o 95 % III. Cama: D_o/24, no menos de 3.0 in, en los Tipos 1 a 3 sobre suelo; ninguna en el Tipo 4.

> **`AASHTO_LRFD_9.T12.10.2.1-1#PROCTOR`** — La primera de las interpretaciones que la norma pone al pie de la tabla. La Tabla 27.5.2.2-3 que nombra NO esta en normas/.

> **`AASHTO_LRFD_9.T12.12.3.3-1`** — Fila «Corrugated PE Pipe – AASHTO M 294» (leida renderizada): 5.0 % | 4.1 % | F_u 3.0 ksi, E 110.0 ksi (inicial) | 0.90, 22 (50 años) | 0.90, 21 (75 años).

> **`AASHTO_LRFD_9.T12.12.3.5-1`** — M_s en ksi por nivel de P_sp (1, 5, 10, 20, 40 y 60 psi) y por suelo y compactacion (Sn, Si, Cl; % del Proctor ESTANDAR, nota 2). Entre niveles se interpola (pag. 12-80).

> **`AASHTO_LRFD_9.T12.12.3.5-2`** — Sn (Gravelly sand, SW): SW, SP, GW, GP, arenas y gravas con 12 % de finos o menos; AASHTO M 145 A-1, A-3. Si (Sandy silt, ML): GM, SM, ML, y GC y SC con menos de 20 % que pasa el tamiz N.° 200; A-2-4, A-2-5, A-4. Cl (Silty clay, CL): CL, MH, GC, SC, y GC y SC con mas de 20 %; A-2-6, A-2-7, A-5, A-6. La nota 2 de la Tabla 12.12.3.5-1 (pag. 12-81): el sufijo es el % de la densidad maxima de AASHTO T 99 (Proctor Estandar).

> **`AASHTO_LRFD_9.T12.6.6.3-1`** — LA TABLA VIVE UNA PAGINA DESPUES QUE SU NUMERAL, y por eso lleva cita propia: el articulado 12.6.6.3 abre en la 12-21 (PDF 1659) y la tabla entera esta en la 12-22 (PDF 1660). Citarlas con la misma pagina manda al revisor a la pagina donde la tabla no esta. SUS COLUMNAS NO SON LAS QUE EL EXPEDIENTE SUPONIA: son «Type», «Condition» y «Minimum Cover*», TRES, y las condiciones de pavimento son VALORES de la segunda columna que solo aparecen en 2 de los 13 tipos. No es una matriz tipo x condicion de pavimento. El repositorio ya la leia asi -- repite la misma fila en las tres condiciones para el metal corrugado, en vez de inventarle dos que la tabla no trae --, y esta verificacion lo confirma.

> **`AASHTO_LRFD_9.T3.10.3.1-1#F`** — LAS TRES CATEGORIAS Y EL «SUCH AS». La celda enumera turbas o arcillas altamente organicas (H > 10.0 ft), arcillas de muy alta plasticidad (H > 25.0 ft con PI > 75) y estratos potentes de arcilla blanda o semirrigida (H > 120 ft). NINGUNA es licuefaccion: la busqueda de `liquef` sobre la pagina PDF 156 entera da cero, y en las 1905 paginas del documento los conjuntos {paginas con `liquef`} y {paginas con «Site Class F»} son disjuntos. PERO el encabezado es «such as», lista abierta, de modo que lo que se sostiene es la afirmacion NEGATIVA -- la norma no escribe el salto -- y no la contraria. La tension con el «the three categories» del comentario esta declarada en DIS-AASHTO-F-LISTA-ABIERTA, y la decision no depende de como se resuelva: por las dos lecturas el salto sigue sin estar escrito. Verificada tambien por imagen: los tres bullets son glifos Symbol.

> **`AASHTO_LRFD_9.T3.11.6.4-1`** — Su variable de entrada se llama literalmente «Abutment Height (ft)»: es una tabla de ESTRIBOS. Aplicarla a un cabezal de alcantarilla es analogia declarada, no lectura directa.

> **`AASHTO_LRFD_9.T3.11.6.4-2`** — Encabezado de DOS niveles: sobre las columnas 2 y 3 va «heq (ft) Distance from wall backface to edge of traffic», y bajo el «0.0 ft» y «1.0 ft or Further». El umbral es UNA PULGADA-PIE EXACTA: 1.0 ft = 0.3048 m, no 0.30 m. Redondearlo a 0.30 relaja el criterio y va del lado inseguro.

> **`AASHTO_LRFD_9.T3.4.1-1`** — NOR-AAS-03, resuelto a favor del codigo vigente: la ficha reprochaba «pag. 3-14» y el repositorio ya decia 3-17, que es lo correcto segun la fuente.

> **`AASHTO_LRFD_9.T3.4.1-2`** — Confirma dos hallazgos abiertos: EV «Retaining Walls and Abutments» = 1.35 / 1.00 (no 0.90; sostiene NOR-PUE-03) y EH At-Rest = 1.35 / 0.90, CON minimo declarado -- lo que refuta la afirmacion negativa de NOR-AAS-04, que sostenia que la fuente no declara minimo para EH en reposo. El N/A pertenece a la fila siguiente, «AEP for anchored walls».

> **`AASHTO_LRFD_9.T3.6.1.2.6a-1`** — Dos filas: «Concrete Pipe with fill depth 2.0 ft or greater» (1.15 para diametro de 2.0 ft o menos, 1.75 para 8.0 ft o mas, «Linearly interpolate for LLDF between these limits») y «All other culverts and buried structures» (1.15). El «diameter» se lee como el diametro INTERIOR del catalogo; vista de calculo en constantes_normativas (LLDF_*).

> **`AASHTO_LRFD_9.T5.10.1-1`** — TRES categorias de acero -- A, B y C --, bajo el encabezado de grupo «Reinforcing Material Category», y la tabla peruana tiene UNA sola columna porque cubre una sola categoria: la no protegida. Es la clave de NOR-AAS-01: los 3.0 in de «Coastal» son de la Categoria A, y con B o C la tabla baja a 2.0 in = 50.8 mm, con lo que la regla del mayor la pasaria a ganar E.060.

> **`AASHTO_LRFD_9.TA12-11`** — ES LA FUENTE DEL DIAMETRO EXTERIOR DEL HDPE, que su norma de producto no trae (afirmacion negativa SIN_DIAMETRO_EXTERIOR_M294_TRAD). Apendice A12 «PLATE, PIPE, AND PIPE ARCH PROPERTIES» de la Seccion 12: para cada tamaño nominal de tuberia corrugada de PE bajo M 294 tabula el diametro interior MINIMO, el diametro exterior MAXIMO y las propiedades minimas de la pared (A, c, I). OCHO filas, de 12 a 48 in: NO trae 54 ni 60 in, de modo que para 1350 y 1500 mm el diametro exterior sigue sin fuente y 'espesor_pared_conducto' no declara esas filas. Unidades inglesas; la conversion a metros (1 in = 0.0254 m exactos) es del proyecto. La nota al pie de la tabla avisa de que para 42 y 48 in el espesor de pared se diseñe con la resistencia a traccion de largo plazo (900 psi): es de la Fase 8, no del diametro exterior, y `M8.verificar_hdpe` la aplica en esas dos filas con las propiedades de largo plazo (T-5).

> **`AASHTO_LRFD_9.TA12-9`** — Fila «Steel(3)»: F_u 45.0 ksi, F_y 33.0 ksi, E_m 29,000 ksi; la nota (3) es el texto literal. Son las cifras de la comprobacion LRFD que rige. ASTM A796 num. 4 escribe 225 / 310 / 200 000 MPa (redondeo metrico de las mismas): se usan solo en el contraste ASD.

### AASHTO M 170M-04 «Standard Specification for Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe [Metric]»  (`AASHTO_M170M`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `AASHTO_M170M.1.1` | 1.1 | «SCOPE» | pág. impresa **M 170M-1** · PDF 1 | definicion | 2026-09-20 · imagen renderizada |
| `AASHTO_M170M.1.1#NOTA1` | 1.2, Note 1 | «SCOPE» | pág. impresa **M 170M-1** · PDF 1 | definicion | 2026-09-20 · imagen renderizada |
| `AASHTO_M170M.7.2.1` | 7.2.1 | «Modified and Special Designs» | pág. impresa **M 170M-13** · PDF 13 | definicion | 2026-11-11 · imagen renderizada |
| `AASHTO_M170M.7.2.2` | 7.2.2 | «Modified and Special Designs» | pág. impresa **M 170M-13** · PDF 13 | exigencia | 2026-11-11 · imagen renderizada |
| `AASHTO_M170M.T1#DIAMETROS` | Table 1 | «Design Requirements for Class I Reinforced Concrete Pipe» | pág. impresa **M 170M-3** · PDF 3 | definicion | 2026-11-12 · imagen renderizada |
| `AASHTO_M170M.T1_T5#DIAMETROS` | Tables 1 to 5 | «Table 1—Design Requirements for Class I Reinforced Concrete Pipe» | pág. impresa **M 170M-3** · PDF 3 | definicion | 2026-09-12 · imagen renderizada |
| `AASHTO_M170M.T2#DLOAD` | Table 2 | «Design Requirements for Class II Reinforced Concrete Pipe» | pág. impresa **M 170M-5** · PDF 5 | definicion | 2026-11-12 · imagen renderizada |
| `AASHTO_M170M.T5` | Table 5 | «Table 5—Design Requirements for Class V Reinforced Concrete Pipe» | pág. impresa **M 170M-10** · PDF 10 | definicion | 2026-09-22 · imagen renderizada |

> **`AASHTO_M170M.1.1`** — Leida sobre la PDF 1 renderizada a escala 3.0 (el OCR imprime «iniendcd io be used» y «culvens»). Cubre TUBERIA («pipe»); un marco rectangular vaciado in situ no es tuberia y esta norma no lo rige. La PDF 1 rotula ademas «AASHTO Designation: M 170M-04» y «ASTM Designation: C 76M-02», que es la doble designacion del rotulo que M2 imprime.

> **`AASHTO_M170M.1.1#NOTA1`** — LO QUE LA NORMA DICE QUE NO ES: ni cama, ni relleno, ni la relacion entre la carga de campo y la clase. La nota sigue: la experiencia muestra que el buen desempeño depende de elegir la clase, la cama y el relleno, y el propietario «is cautioned that he must correlate the field requirements with the class of pipe specified». Es la misma clausula que M 36 lleva en su 1.3 y A760 en su 1.4, y la razon de que 'clases_producto_por_relleno' sea un criterio del proyecto y no una lectura de la norma.

> **`AASHTO_M170M.7.2.1`** — Leida sobre la PDF 13 renderizada; la capa visible del ejemplar es un OCR defectuoso («pemiitted», «mquest», «reinfomenicnt») y la transcripcion corrige esas letras. LO QUE SOSTIENE: los tamaños que las Tablas 1 a 5 listan SIN area de acero no tienen diseño estandar; son diseños especiales que el fabricante propone y el propietario aprueba. LEIDO TABLA A TABLA SOBRE LAS PAGINAS RENDERIZADAS (T-4, 2026-11-11): Tabla 1 (Clase I, PDF 3), filas de 1500 a 2700 mm con pared y acero --la de 2700: pared A 225 mm, pared B 250 mm-- y filas de 2850, 3000, 3150, 3300 y 3450 mm con llamada a nota y rayas; Tabla 3 (Clase III, PDF 6-7), la ultima fila con acero es la de 2700 mm y las de 3000, 3150 y 3600 llevan llamada y rayas (las de 2850, 3300 y 3450 no se leen en el ejemplar); Tabla 5 (Clase V, PDF 10), pared tabulada hasta 1800 mm (AASHTO_M170M.T5). La nota al pie de las tablas, leida en la PDF 3 y en la PDF 5: «For modified or special designs, see Section 7.2 ...» y «Pipe over 2400 mm in diameter shall have two circular cages or an inner circular cage plus one elliptical cage». NO LEIDO: el cuerpo de la Tabla 2 (PDF 4) y el maximo de la Tabla 4, cuya mitad baja no esta en el escaneo. Con lo leido, el mayor diametro con diseño estandar es 2700 mm en las dos clases que se pudieron leer hasta el final.

> **`AASHTO_M170M.7.2.2`** — Leida sobre la PDF 13 renderizada, con el mismo OCR defectuoso («conwetc strength», «rind st ngth»). EL ESPESOR DE PARED DE UN DISEÑO ESPECIAL LO DA EL FABRICANTE en su descripcion: la norma no lo tabula. Es la segunda frase del 7.2.2; la primera exige que el diseño se base en evaluaciones racionales o empiricas de la resistencia ultima y del agrietamiento. El 7.2.3 pide al fabricante la prueba de adecuacion (ensayos de tres aristas).

> **`AASHTO_M170M.T1#DIAMETROS`** — LEIDO POR IMAGEN. La primera fila de la Tabla 1 (Clase I) es la de 1500 mm: la norma no tabula la Clase I por debajo. Las Tablas 2 a 5 (Clases II a V; PDF 4, 6, 8 y 10) empiezan en 300 mm. Vista de calculo: DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM. El ultimo diametro con diseño estandar de cada clase NO se transcribe: solo se lee con seguridad en las Clases I y II (2700 mm) y V (1800 mm, pared C); por encima la norma remite al diseño especial de su num. 7.2, y el tope de 2700 mm del catalogo de concreto lo fija DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM.

> **`AASHTO_M170M.T1_T5#DIAMETROS`** — ES EL ANCLA DE DIS-HR-D-MAX: la envolvente de diametros de las cinco tablas, leida TABLA POR TABLA sobre las paginas renderizadas (escaneo con OCR inutilizable; ver la Fuente). Columna «Internal Designated Diameter, mm»: Tabla 1 (Clase I, PDF 3): 1500 a 3450; Tabla 2 (Clase II, PDF 4-5): 300 a 3450; Tabla 3 (Clase III, PDF 6-7): 300 a 3600; Tabla 4 (Clase IV, PDF 8-9): arranca en 300 y SU MAXIMO NO ES VERIFICABLE en este ejemplar -- la tinta de la mitad baja de la PDF 8 no esta en el escaneo --; Tabla 5 (Clase V, PDF 10-11): 300 a 3600. La envolvente NO es uniforme y por eso «Tablas 1 a 5: de 300 a 3600» solo es cierta leida como CONJUNTO. Encima de lo tabulado, el num. 7.2 «Modified and Special Designs» (PDF 13) preve, con permiso del propietario, «special designs for sizes and loads beyond those shown in Tables 1 to 5» (7.2.1); y el num. 4.1 «CLASSIFICATION» (PDF 2) remite: «The corresponding strength requirements are prescribed in Tables 1 to 5.» DOS RESERVAS DE LEGIBILIDAD, ninguna contraria: el rotulo al pie de la PDF 3 esta degradado (la correspondencia «M 170M-3» la fijan los rotulos legibles de las paginas vecinas M 170M-2 y M 170M-4 y la regla de paginacion), y los digitos del numero de tabla en las paginas de continuacion (PDF 7 y 9) no se leen: la asignacion de cada continuacion a su tabla es por secuencia de rotulos y coherencia de filas.

> **`AASHTO_M170M.T2#DLOAD`** — LEIDO POR IMAGEN, y es LA UNICA D-load de 0.3 mm LEGIBLE en el ejemplar. La pag. PDF 5 («Table 2—Continued») imprime al pie «D-load to produce a 0.3-mm crack 50.0» y «D-load to produce the ultimate load ?S.0» (el primer digito, ilegible). Las Tablas 1, 3, 4 y 5 son recomposiciones OCR con digitos equivocados (nota de la Fuente): la de la Clase V imprime «\ 40.0», la de la Clase III solo la ultima, «100.0», y la Clase I e IV no se leen. NO SE COMPLETAN DE MEMORIA: las Clases I, III, IV y V quedan sin D-load en 'clases_producto_por_relleno' y el paso lo dice. Y la Tabla 2 (PDF 4) tiene filas con pared B y acero de 300 a 2700 mm: la Clase II existe en todo el catalogo de concreto.

> **`AASHTO_M170M.T5`** — La pagina PDF 10 es un escaneo real, legible, impreso girado 90 grados (el rotulo de pie «M 170M-10» y «TS-4a» van verticales). La columna «Internal Designed Diameter, mm» --asi la imprime, con «Designed» y no «Designated»-- tiene 27 filas de 300 a 3600 mm, y es la serie que CP11 usa como dorado del concreto. Las columnas de espesor de pared B (300 a 1200 mm) y C (300 a 1800 mm) son legibles y se transcriben; las de refuerzo no, porque ningun modulo las consume (M8 no dimensiona el tubo de concreto).

### AASHTO M 294-11 «Tubería corrugada de polietileno, 300 a 1500 mm (12 a 60 in.) de diámetro» — TRADUCCION NO OFICIAL al español  (`AASHTO_M294_TRAD`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `AASHTO_M294_TRAD.1.1.1` | 1.1.1 | 1.1. › «Ámbito» | pág. impresa **s/n** · PDF 1 | definicion | **NO verificada** |
| `AASHTO_M294_TRAD.1.4` | 1.4 | «Ámbito» | pág. impresa **s/n** · PDF 1 | definicion | **NO verificada** |
| `AASHTO_M294_TRAD.7.2.1` | 7.2.1 | REQUERIMIENTOS › Dimensiones de la tubería: › «Tamaño nominal» | pág. impresa **s/n** · PDF 5 | exigencia | **NO verificada** |
| `AASHTO_M294_TRAD.7.2.2` | 7.2.2 | REQUERIMIENTOS › Dimensiones de la tubería: › «Espesor de pared» | pág. impresa **s/n** · PDF 5 | exigencia | **NO verificada** |
| `AASHTO_M294_TRAD.7.7` | 7.7 | «Ensayo de compresión» | pág. impresa **s/n** · PDF 8 | exigencia | **NO verificada** |

> **`AASHTO_M294_TRAD.1.1.1`** — SIN FIRMA A PROPOSITO, no sin verificar: la fuente es una TRADUCCIÓN NO OFICIAL al español de AASHTO M 294-11 y no imprime folio (`pagina_impresa` dice «s/n» por eso), y el invariante T6 impide firmar una pagina PDF de una fuente sin paginacion medida -- ver la cabecera del bloque --. Contenido comprobado en N2 (verificador-normativo, 2026-09-14, por texto y por imagen de la hoja 1): la frase esta integra en la PDF 1 bajo «1. Ámbito», inciso 1.1.1. Es la frase que fija el TECHO DE LA SERIE del HDPE en 1500 mm, y el ancla de DIS-HR-D-MAX para el HDPE; el num. 7.2.1 la desarrolla diametro a diametro. Lo que acredita es lo que la traduccion dice; el original en ingles sigue ausente (`AASHTO_M294`).

> **`AASHTO_M294_TRAD.1.4`** — SIN FIRMA A PROPOSITO, no sin verificar: TRADUCCIÓN NO OFICIAL sin folio, invariante T6 (ver la cabecera del bloque). Contenido comprobado en N2 (verificador-normativo, 2026-09-14, por texto y por imagen de la hoja 1): el Verbatim son las TRES PRIMERAS ORACIONES de un parrafo de cuatro, integras en la PDF 1; la cuarta -- la que remite al fabricante «el detalle de la seción del perfil de la pared» -- queda fuera del Verbatim a proposito y la usa la afirmacion negativa SIN_DIAMETRO_EXTERIOR_M294_TRAD. «instalaión» y «LFRD» son erratas de la traduccion y se transcriben como se imprimen (T21). Es el ancla de la afirmacion negativa SIN_CLASE_POR_ALTURA_M294_TRAD: la norma de producto del HDPE excluye camas, relleno y carga de cubierta, y remite el diseño estructural a AASHTO LRFD Seccion 12 -- que es lo que 'clases_producto_por_relleno' venia afirmando del HDPE sin poder contrastarlo --.

> **`AASHTO_M294_TRAD.7.2.1`** — SIN FIRMA A PROPOSITO, no sin verificar: TRADUCCIÓN NO OFICIAL sin folio, invariante T6 (ver la cabecera del bloque). Contenido comprobado en N2 (verificador-normativo, 2026-09-14, por texto y por imagen de la hoja 5): la frase esta integra en la PDF 5 bajo «7. REQUERIMIENTOS» > «7.2. Dimensiones de la tubería:». La primera oracion del numeral, que el Verbatim no incluye, define el tamaño nominal como el diametro nominal INTERIOR. El num. 1.3 (PDF 1) declara los valores SI como los estandar y las pulgadas entre parentesis como no necesariamente equivalencias exactas, de modo que 1500 mm es el valor y 60 in. la aproximacion. Lo que acredita es lo que la traduccion dice; para el HDPE la serie TERMINA donde el proyecto topa (1.50 m), a diferencia de A760 y M 170M, que tabulan hasta 3600 mm.

> **`AASHTO_M294_TRAD.7.2.2`** — SIN FIRMA A PROPOSITO, no sin verificar: TRADUCCIÓN NO OFICIAL sin folio, invariante T6 (ver la cabecera del bloque). Contenido comprobado en N2 (verificador-normativo, 2026-09-14, por texto y por imagen de la hoja 5). «lo siguientes» es errata de la traduccion, transcrita como se imprime (T21). Sostiene la tabla AASHTO_M294_TRAD.T7.2.2. LO QUE ESTE ESPESOR ES Y NO ES, porque el nombre invita al error: es el minimo de la pared interior lisa (Tipo S) o de las dos paredes (Tipo D), medido segun 9.6.4; NO es la altura del perfil corrugado y NO fija el diametro exterior, que la traduccion no trae en ninguna hoja (SIN_DIAMETRO_EXTERIOR_M294_TRAD). Por eso esta tabla NO cierra 'espesor_pared_conducto' para el HDPE.

> **`AASHTO_M294_TRAD.7.7`** — SIN FIRMA A PROPOSITO, no sin verificar: traduccion no oficial de AASHTO M 294-11. Lo que acredita es lo que la traduccion imprime, y sin folio no se firma (mismo regimen que las otras cuatro citas de esta fuente; leida en texto e imagen por T-5). Es el MINIMO de producto con que el programa obtiene el area efectiva del perfil sin conocer su geometria: P_st >= 0.5 A_g F_y, y por 12.12.3.10.1b-5, A_eff = P_st K_t / F_u.

### AASHTO M 36 «Corrugated Steel Pipe, Metallic-Coated, for Sewers and Drains»  (`AASHTO_M36`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `AASHTO_M36.1.1` | 1.1 | «SCOPE» | pág. impresa **M 36-1** · PDF 2 | definicion | 2026-09-20 · imagen renderizada |
| `AASHTO_M36.1.2` | 1.2 | «SCOPE» | pág. impresa **M 36-1** · PDF 2 | definicion | 2026-11-11 · imagen renderizada |
| `AASHTO_M36.8.1.1` | 8.1.1 | «Pipe Dimensions» | pág. impresa **M 36-10** · PDF 11 | exigencia | 2026-11-11 · imagen renderizada |
| `AASHTO_M36.T1` | Table 1 | «Corrugation Requirements for Type I, IA, II, IIA, and III Pipe» | pág. impresa **M 36-6** · PDF 7 | definicion | 2026-11-11 · imagen renderizada |
| `AASHTO_M36.T6` | Table 6 | «Table 6—Pipe Sizes» | pág. impresa **M 36-11** · PDF 12 | definicion | 2026-09-12 · imagen renderizada |
| `AASHTO_M36.T7` | Table 7 | «Thicknesses of Metallic-Coated Steel Sheet» | pág. impresa **M 36-12** · PDF 13 | definicion | 2026-11-11 · imagen renderizada |

> **`AASHTO_M36.1.1`** — RASTER PURO: leida sobre la PDF 2 renderizada a escala 3.0. La portada rotula «AASHTO Designation: M 36-03 (2007)» y «ASTM Designation: A 760/A 760M-01a». Cubre tuberia de acero corrugado para drenaje pluvial, subdrenes y alcantarillas; el resto del numeral 1.1 enumera los recubrimientos metalicos (zinc, aluminio tipo 2, aleacion 55 % Al-Zn, Zn-5 % Al-mischmetal, aluminio tipo 1) y no se transcribe. La MISMA clausula, en español, es el 1.1 de A760 (`corresponde_en`).

> **`AASHTO_M36.1.2`** — RASTER PURO: leida sobre la PDF 2 renderizada a 130 dpi. LA NORMA DE PRODUCTO DEL TMC NO FIJA NINGUN UMBRAL de pH, resistividad, salinidad ni velocidad: reconoce que hay ambientes en que ningun recubrimiento metalico basta y remite la proteccion adicional a M 190 (recubrimiento bituminoso) y M 245 (precubierto de polimero), que no estan en normas/. Su 1.3 excluye ademas cama, relleno y la relacion entre carga de tierra y espesor de plancha.

> **`AASHTO_M36.8.1.1`** — RASTER PURO: leida sobre la mitad inferior de la PDF 11 renderizada a 170 dpi. EL DIAMETRO NOMINAL DEL TMC ES EL INTERIOR, MEDIDO EN LA CRESTA INTERIOR de las corrugaciones. Es lo que permite escribir D_ext = D + 2 x (profundidad de corrugacion + espesor de plancha). La primera frase del numeral manda elegir el diametro nominal de la Tabla 6 (AASHTO_M36.T6), que marca ademas las corrugaciones estandar de cada diametro; y el 8.1.2, misma pagina, que el espesor de plancha lo especifique el comprador de entre los de la Tabla 7.

> **`AASHTO_M36.T1`** — RASTER PURO: leida sobre la PDF 7 renderizada a 100 dpi entera y el recorte de las Tablas 1 y 2 a 220 dpi. El `texto_literal` es la nota b de la tabla, y es la que hace falta: la PROFUNDIDAD de la corrugacion se mide de cresta a valle sobre la MISMA cara de la plancha, de modo que la altura total del perfil --lo que separa el diametro interior del exterior-- es profundidad MAS espesor de plancha. La nota sigue con el procedimiento de arbitraje de la Tabla 2 cuando una corrugacion mide menos que el minimo.

> **`AASHTO_M36.T6`** — RASTER PURO: leida entera sobre la pagina PDF 12 renderizada (escalas 4.0 y 8.0; las filas 2550-3600 exigieron la segunda para separar las columnas de costilla). La pagina impresa lleva el rotulo «M 36-11» al pie, que confirma el desfase +1 de la Fuente.

> **`AASHTO_M36.T7`** — RASTER PURO: leida sobre la PDF 13 renderizada a 100 dpi entera y el recorte de la tabla a 220 dpi. SIETE ESPESORES ESPECIFICADOS DE PLANCHA: 1.02, 1.32, 1.63, 2.01, 2.77, 3.51 y 4.27 mm; la columna del galvanizado (M 218, «Zinc Coated») los marca los siete. Son los mismos siete de las Tablas 3 a 9 de ASTM A796, que es donde estan sus propiedades seccionales (A, I, r). La Nota 9, debajo de la tabla, dice que el espesor requerido lo determina el comprador con los criterios de diseño de AASHTO («Standard Specifications for Highway Bridges, Division I, Section 12, or other appropriate guidelines»): la norma de producto LISTA los espesores y no elige ninguno.

### ASTM A760/A760M-10 «Especificacion Estandar para Tuberia de Acero Corrugado, con Recubrimiento Metalico, para Alcantarillas y Drenajes»  (`ASTM_A760`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `ASTM_A760.1.1` | 1.1 | «Alcance» | pág. impresa **1** · PDF 1 | definicion | 2026-09-20 · imagen renderizada |
| `ASTM_A760.T1` | Tabla 1 | «TABLA 1 Tamaños de tubería» | pág. impresa **3** · PDF 3 | definicion | 2026-09-12 · imagen renderizada |

> **`ASTM_A760.1.1`** — ToUnicode roto: leida sobre la PDF 1 renderizada a escala 3.0. El ejemplar es la TRADUCCION AL ESPAÑOL (propiedad declarada en la Fuente): el encabezado imprime «1 Alcance» y, arriba a la derecha, «AASHTO No. M 36 / M 36M», la doble designacion. Su 1.4 repite la clausula de M 170M Note 1 y M 36 1.3: la norma no incluye cama, relleno ni la relacion carga-espesor, y remite la instalacion a la Practica A798/A798M (ausente, DIS-HR-A807).

> **`ASTM_A760.T1`** — Leida sobre la pagina PDF 3 renderizada (S14 dejo comprobado que es legible a escala 2.0; esta transcripcion se hizo a 4.0). El PDF es la TRADUCCION AL ESPAÑOL de la norma (propiedad declarada en la Fuente): el titulo impreso es «TABLA 1 Tamaños de tubería» y los encabezados mezclan «en.» (in.) con «pulg.». La MISMA tabla existe como Table 6 de AASHTO M 36 (doble designacion, ediciones distintas): las diferencias medidas entre las dos estan declaradas en la correspondencia CORR-TAMANOS-TMC.

### ASTM A796/A796M-13 «Structural Design of Corrugated Steel Pipe, Pipe-Arches, and Arches» (practica de diseño estructural de tuberia de acero corrugado, arcos-tubo y arcos)  (`ASTM_A796`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `ASTM_A796.10.2` | 10.2 | 10. › «Handling and Installation» | pág. impresa **4** · PDF 4 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.10.3` | 10.3 | 10. › «Handling and Installation» | pág. impresa **4** · PDF 4 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.10.4` | 10.4 | 10. › «Handling and Installation» | pág. impresa **4** · PDF 4 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.10.5` | 10.5 | 10. › «Handling and Installation» | pág. impresa **4** · PDF 4 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.10.6` | 10.6 | 10. › «Handling and Installation» | pág. impresa **4** · PDF 4 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.11.1#DEF` | 11.1 | 11. › Minimum Cover Requirements › «Minimum Cover Design» | pág. impresa **5** · PDF 5 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.11.1#PISOS` | 11.1 | 11. › Minimum Cover Requirements › «Minimum Cover Design» | pág. impresa **5** · PDF 5 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.17.1` | 17.1 | 17. › «Materials» | pág. impresa **5** · PDF 5 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.22.1` | 22.1 | 22. › «Construction and Installation» | pág. impresa **6** · PDF 6 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.5.1` | 5.1 | «Basis of Design» | pág. impresa **2** · PDF 2 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.6.2.2.1` | 6.2.2.1 | 6. › Loads › 6.2.2 › Live Loads › «Live Loads Under Highway» | pág. impresa **3** · PDF 3 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.7.1` | 7.1 | «Design Method» | pág. impresa **3** · PDF 3 | permiso | 2026-09-14 · imagen renderizada |
| `ASTM_A796.8.1.1.2#SELECCION` | 8.1.1.2 | 8. › 8.1.1 › Required Wall Area: › «Design by ASD Method» | pág. impresa **3** · PDF 3 | exigencia | 2026-09-14 · imagen renderizada |
| `ASTM_A796.8.1.3.1` | 8.1.3.1 | «Required Seam Strength» | pág. impresa **4** · PDF 4 | definicion | 2026-11-12 · imagen renderizada |
| `ASTM_A796.9.1` | 9.1 | 9. › Design by LRFD Method › «Factored Loads» | pág. impresa **4** · PDF 4 | exigencia | 2026-11-12 · imagen renderizada |
| `ASTM_A796.T11` | Table 11 | «TABLE 11 Sectional Properties of Spiral Rib Pipe for 19 mm Wide by 19 mm Deep Rib with a Spacing of 190 mm Center to Center (Helical) [SI Units]» | pág. impresa **11** · PDF 11 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.T15` | Table 15 | «TABLE 15 Sectional Properties of Spiral Rib Pipe for 19 mm Wide by 25 mm Deep Rib with a Spacing of 292 mm Center to Center (Helical) [SI Units]» | pág. impresa **12** · PDF 12 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.T17` | Table 17 | «TABLE 17 Sectional Properties of Spiral Rib Pipe for 19 mm Wide by 25 mm Deep Rib with a Spacing of 216 mm Center to Center (Helical) [SI Units]» | pág. impresa **13** · PDF 13 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.T3` | Table 3 | «TABLE 3 Sectional Properties of Corrugated Steel Sheets for Corrugation: 38 by 6.5 mm (Helical) [SI Units]» | pág. impresa **7** · PDF 7 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.T5` | Table 5 | «TABLE 5 Sectional Properties of Corrugated Steel Sheets for Corrugation: 68 by 13 mm (Annular or Helical) [SI Units]» | pág. impresa **8** · PDF 8 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.T7` | Table 7 | «TABLE 7 Sectional Properties of Corrugated Steel Sheets for Corrugation: 75 by 25 mm (Annular or Helical) [SI Units]» | pág. impresa **9** · PDF 9 | definicion | 2026-09-14 · imagen renderizada |
| `ASTM_A796.T9` | Table 9 | «TABLE 9 Sectional Properties of Corrugated Steel Sheets for Corrugation: 125 by 25 mm (Helical) [SI Units]» | pág. impresa **10** · PDF 10 | definicion | 2026-09-14 · imagen renderizada |

> **`ASTM_A796.10.2`** — El 10.2 no lleva titulo propio: cuelga de «10. Handling and Installation». FF = s²/EI es la ec. (12) del 10.1. Los limites de FF (10.2 a 10.8) son el sitio de la practica donde la RIGIDEZ MINIMA por perfil esta tabulada -- 10.2/10.3 para plancha corrugada, 10.4 a 10.6 para costilla espiral (con o sin insertos), 10.7 compuesta, 10.8 costilla cerrada --: es lo que, en la practica norteamericana, gobierna el calibre minimo por diametro en coberturas bajas.

> **`ASTM_A796.10.3`** — Sin titulo propio: cuelga de «10. Handling and Installation».

> **`ASTM_A796.10.4`** — Sin titulo propio: cuelga de «10. Handling and Installation». Aplica a los TRES perfiles de costilla espiral de ASTM_A760.T1 (Tablas 11, 15 y 17): lo señalo la auditoria adversarial de N1, que refuto la primera version de este bloque, donde 10.4 a 10.6 se habian dejado fuera como si fueran de otro producto.

> **`ASTM_A796.10.5`** — Sin titulo propio: cuelga de «10. Handling and Installation».

> **`ASTM_A796.10.6`** — Sin titulo propio: cuelga de «10. Handling and Installation». El 10.7 (misma pagina) añade que para tuberia COMPUESTA de costilla los limites de 10.4 a 10.6 «shall be multiplied by 1.05», y el 10.8 tabula la costilla cerrada; ninguno de los dos productos esta en ASTM_A760.T1 y no se transcriben.

> **`ASTM_A796.11.1#DEF`** — «require-ments» lleva el guion de fin de renglon como lo imprime la columna, con el mismo criterio que «recom-mendations» en la cita 5.1. «Hmin» se imprime con el «min» en subindice; se transcribe en linea. La MISMA definicion (a la subrasante en pavimento flexible, a la cara superior del pavimento rigido) es la de la variable h del num. 4.1. Sigue la tabulacion de cargas por eje (ASTM_A796.11.1 en tablas.py) y las ecs. (13) a (16), que dan Hmin en funcion de raiz((AL)d/EI) y del diametro S: 0.55·S·raiz(…) entre 0.23 y 0.45, S/8 por debajo de 0.23 y S/4 por encima de 0.45. Las ecuaciones no se transcriben como Verbatim porque son formulas compuestas; quien las implemente las lee de la pagina.

> **`ASTM_A796.11.1#PISOS`** — «Hmin» con el «min» en subindice, transcrito en linea. Los 300 mm coinciden con los 12 in de la Tabla 12.6.6.3-1 de AASHTO LRFD para el metal corrugado (AASHTO_LRFD_9.T12.6.6.3-1), y la ec. (15) (Hmin = S/8 para tuberia rigida) coincide con el S/8 de esa misma fila: las dos fuentes son consistentes y NO se abre discrepancia. El escalon de 600 mm para espesor < 1.32 mm NO esta en AASHTO. El num. 11.4 «Construction Loads» (misma pagina) añade una cobertura minima DE OBRA, bajo equipo pesado: «The minimum cover shall be 4 ft [1.2 m] unless field conditions and experience justify modification.»; es exigencia de construccion, no de servicio, y no lleva cita propia porque ningun objeto del registro la consumiria hoy (T4).

> **`ASTM_A796.22.1`** — El guion de «pipe-arches» partido a fin de renglon («pipe- / arches») es el propio guion de la palabra, no uno de corte, y se transcribe como «pipe-arches».

> **`ASTM_A796.5.1`** — Los dos guiones de fin de renglon («recom-mendations», «prac-tice») se transcriben como los imprime la columna. El encabezado «5. Basis of Design» esta al pie de la columna derecha de la PDF 2 y el numeral 5.2 sigue en la PDF 3.

> **`ASTM_A796.6.2.2.1`** — Es una tabulacion SIN TITULO ni numero de tabla, impresa en el cuerpo del numeral: la TablaNormativa toma como titulo literal el encabezado del numeral, con el precedente de E060.7.7.1. El num. 6.2.2.3 (misma pagina, sin titulo propio) añade «Values for intermediate covers shall be interpolated.»: es el renglon que hace de la tabulacion una BANDA y no escalones, y la Interpretacion de la tabla lo recoge. No lleva cita propia porque ningun objeto del registro la consumiria hoy (T4).

> **`ASTM_A796.8.1.1.2#SELECCION`** — El 8.1.1.2 no lleva titulo propio: cuelga de «8.1.1 Required Wall Area:» bajo «8. Design by ASD Method», y abre con «Determine the required wall cross-sectional area. The safety factor (SF) on wall area is 2.» y la ec. (4), A = T(SF)/f_y -- el SF = 2 no lleva cita propia porque ningun objeto del registro lo consumiria hoy (T4); lo consumira la sesion que implemente el procedimiento --. La lista entre corchetes es la de las tablas en unidades SI, que son las que este registro transcribe para las siete corrugaciones de ASTM_A760.T1 (Tablas 3, 5, 7, 9, 11, 15 y 17). Los dos ultimos renglones de la frase se imprimen SOLAPADOS en el render («15, Table 17, ... Table 27,» sobre «Table 29, Table 31, Table 33, or Table 35]»): es la capa de texto duplicada del ejemplar, y se leyo a escala 5.0.

> **`ASTM_A796.9.1`** — Sigue la ec. (8), P_f = 1.95 EL + 1.75 (LL + IL), con EL = Hw (ec. 1, la columna de suelo SOBRE el tubo). Es la lectura que la practica especifica del acero corrugado hace de la presion de clave: sin factor de instalacion ni nivel de arranque, y coincide con C12.7.2.2 de AASHTO. Leida por imagen (PDF 4).

> **`ASTM_A796.T11`** — Gemela SI de la Table 10 (3/4 by 3/4 by 7 1/2 in.), que esta al pie de la PDF 10 y cuya nota A se imprime al ABRIR la PDF 11. La Table 12/13 que sigue («Ribbed Pipe with Inserts») es otro producto y no se transcribe.

> **`ASTM_A796.T15`** — Gemela SI de la Table 14 (3/4 by 1 by 11 1/2 in.). SU NOTA A NO ESTA EN SU PAGINA: la PDF 12 termina en la ultima fila (2.77) y el renglon «A Net effective properties at full yield stress.» se imprime al ABRIR la PDF 13, antes de la Table 16. La TablaNormativa lo transcribe con pagina_pdf=13 por esa razon.

> **`ASTM_A796.T17`** — Gemela SI de la Table 16 (3/4 by 1 by 8 1/2 in.).

> **`ASTM_A796.T3`** — Gemela SI de la Table 2 (1 1/2 by 1/4 in.), impresa debajo de ella en la misma pagina. La figura acotada (Pitch = 38.1 mm, Depth = 6.35 mm, radio 7.14 mm) no se transcribe: es dibujo.

> **`ASTM_A796.T5`** — Gemela SI de la Table 4 (2 2/3 by 1/2 in.). Es la corrugacion estandar de la mayor parte de los diametros de ASTM_A760.T1. Los subencabezados de remaches («8-mm Rivets», «10-mm Rivets») se imprimen SOLAPADOS con «Single/Double» en el render por la capa duplicada del ejemplar; se leyeron a escala 8.0.

> **`ASTM_A796.T7`** — Gemela SI de la Table 6 (3 by 1 in.). ERRATA DE LA FUENTE, transcrita tal cual: el encabezado del momento de inercia imprime «I, mm4/m» donde las otras seis tablas imprimen «mm4/mm»; los valores (112.94 a 411.04) son del orden de mm4/mm, como en la Table 9 de la corrugacion vecina.

> **`ASTM_A796.T9`** — Gemela SI de la Table 8 (5 by 1 in.), que esta al pie de la PDF 9; la Table 9 abre la PDF 10 con su propia «NOTE 1».

### Manual de Carreteras: Diseño Geométrico DG-2018 (MTC, «Revisada y Corregida a Enero de 2018»)  (`DG2018`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `DG2018.304.05#BOMBEO` | 304.05 | «Bombeo» | pág. impresa **195** · PDF 196 | exigencia | 2026-11-11 · texto |
| `DG2018.304.06#PERALTE` | 304.06 | «Peralte» | pág. impresa **196** · PDF 197 | definicion | 2026-11-11 · texto |
| `DG2018.304.07.01` | 304.07.01 | 304.07 Derecho de Vía o faja de dominio › «Generalidades» | pág. impresa **198** · PDF 199 | definicion | 2026-09-20 · ambos |
| `DG2018.304.07.02` | 304.07.02 | 304.07 Derecho de Vía o faja de dominio › «Ancho y aprobación del Derecho de Vía» | pág. impresa **198** · PDF 199 | exigencia | 2026-09-20 · ambos |
| `DG2018.304.07.02#INCREMENTO` | 304.07.02 | 304.07 Derecho de Vía o faja de dominio › «Ancho y aprobación del Derecho de Vía» | pág. impresa **199** · PDF 200 | exigencia | 2026-09-20 · ambos |
| `DG2018.304.07.02#INCREMENTO_DRENAJE` | 304.07.02 | 304.07 Derecho de Vía o faja de dominio › «Ancho y aprobación del Derecho de Vía» | pág. impresa **199** · PDF 200 | exigencia | 2026-09-20 · ambos |
| `DG2018.304.07.02#T304.09` | Tabla 304.09 | 304.07 Derecho de Vía o faja de dominio › «Anchos mínimos de Derecho de Vía» | pág. impresa **199** · PDF 200 | definicion | 2026-09-20 · ambos |
| `DG2018.304.10#T304.11` | 304.10, Tabla 304.11 | «Taludes» | pág. impresa **208** · PDF 209 | definicion | 2026-09-20 · ambos |
| `DG2018.304.11` | 304.11 | «304.11 Cunetas» | pág. impresa **208** · PDF 209 | definicion | 2026-11-12 · texto |
| `DG2018.304.11#DESAGUE` | 304.11 | «304.11 Cunetas» | pág. impresa **208** · PDF 209 | exigencia | 2026-11-13 · texto |

> **`DG2018.304.05#BOMBEO`** — La Tabla 304.03 «Valores del bombeo de la calzada» (misma pagina) da 2.0 % y 2.5 % para pavimento asfaltico o de concreto Portland segun la precipitacion sea menor o mayor de 500 mm/año, 2.5 % y 2.5-3.0 % para tratamiento superficial y 3.0-3.5 % y 3.0-4.0 % para afirmado. NO SE TRANSCRIBE como tabla ni se adopta un valor: el bombeo de la seccion tipica es un dato del trazo (dato externo 'bombeo'), y sin el la plataforma se toma horizontal a la cota de rasante. La berma lleva su propia inclinacion (num. 304.04.02, Figura 304.03), de modo que el dato que entra es la pendiente transversal MEDIA de la semiplataforma.

> **`DG2018.304.06#PERALTE`** — Los maximos de la Tabla 304.05 (misma pagina: 4.0 a 12.0 % segun la zona) no se usan aqui. El peralte del cruce es un dato del trazo (dato externo 'peralte'): sube un borde de la plataforma y baja el otro.

> **`DG2018.304.07.01`** — LA REMISION AL RNGIV (DS 034-2008-MTC) ES LO QUE ESTA CITA ACREDITA, y el Reglamento NO esta en normas/: el archivo que hubo hasta 5196dd2 era la publicacion de El Peruano de 2006, no el decreto de 2008 (ver `fuentes.RNGIV`). La pagina imprime a continuacion seis conceptos (ancho y aprobacion, libre disponibilidad, registro, propiedad, propiedad restringida, condiciones de uso) que remiten al Reglamento y no se transcriben: ninguno trae numero.

> **`DG2018.304.07.02`** — EXIGENCIA SOBRE EL ANCHO, no sobre el agua: «anchos mínimos que debe tener». El mismo numeral dice antes que cada autoridad competente del articulo 4 del RNGIV «establece y aprueba mediante resolución del titular» el derecho de via de sus carreteras, y que para determinarlo «deberá tenerse en consideración la instalación de los dispositivos auxiliares y obras básicas requeridas para el funcionamiento de la vía». Es el requisito juridico [N] de V5 (v8 fila V5, enmendada en EXT-0); la condicion hidraulica no esta aqui ni en ninguna otra parte del 304.07.

> **`DG2018.304.07.02#INCREMENTO`** — EL TERCERO DE LOS CUATRO CASOS ES EL DEL PROYECTO: la pagina imprime, con viñeta, «Del borde más alejado de las obras de drenaje» (los otros tres: el borde superior de los taludes de corte mas alejados, el pie de los terraplenes mas altos y el borde exterior de los caminos de servicio). Lo que la frase ESCRIBE es que el ancho fijado «se incrementará en 5.00 m» en ese caso; COMO se compone ese incremento con el ancho de la Tabla 304.09 --- si el limite de la faja queda a 5.00 m del borde de la obra de drenaje, o si se suman 5.00 m al ancho de la fila --- no lo escribe, y es la lectura registrada en `interpretacion` (auditoria adversarial de EXT-6). El mismo numeral admite anchos menores en zonas urbanas «excepcionalmente», por saneamiento fisico legal: es una excepcion de la autoridad, no del proyectista. Vive en `constantes_normativas.INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M`. La viñeta del drenaje es su propia cita (#INCREMENTO_DRENAJE): la pagina separa los cuatro casos con un glifo de viñeta que la capa de texto conserva, y una sola cadena no los une.

> **`DG2018.304.07.02#INCREMENTO_DRENAJE`** — El tercero de los cuatro casos en que el ancho «se incrementará en 5.00 m» (cita gemela #INCREMENTO). Es el que aplica a una alcantarilla: el borde es el del cabezal o el ala mas alejada del eje. Como se compone el incremento con el ancho de la Tabla 304.09 es la interpretacion registrada en la cita gemela.

> **`DG2018.304.07.02#T304.09`** — CINCO FILAS Y DOS COLUMNAS, transcritas enteras en `tablas.DG2018_T304_09`: Autopistas Primera Clase 40, Autopistas Segunda Clase 30, Carretera Primera Clase 25, Carretera Segunda Clase 20, Carretera Tercera Clase 16 (m). La clase de la via de ESTE corredor es el dato de sitio 'clase_de_via', vacio hasta que el estudio de demanda cierre el IMDA; sin el, ninguna fila se elige y el piso no se aplica.

> **`DG2018.304.10#T304.11`** — El numeral 304.10 abre en la impresa 202 (PDF 203) y la Tabla 304.11 esta en la 208 (PDF 209). Transcrita entera en `tablas.DG2018_T304_11`: tres materiales por tres alturas, en V:H. La fila «Gravas, limo arenoso y arcilla» da 1:1.5, 1:1.75 y 1:2 para menos de 5 m, 5 a 10 m y mas de 10 m, que es exactamente la ventana (1.5, 2.0) H:V que 'talud_terraplen' declaraba como «practica corriente» sin poder citarla. Sigue siendo [A]: la tabla es referencial y la seccion tipica del expediente es la que cierra el valor.

> **`DG2018.304.11`** — La misma pagina: «Las dimensiones de las cunetas se deducen a partir de cálculos hidráulicos, teniendo en cuenta su pendiente longitudinal, intensidad de precipitaciones pluviales, área de drenaje y naturaleza del terreno, entre otros», «Las pendientes longitudinales mínimas absolutas serán 0.2%, para cunetas revestidas y 0.5% para cunetas sin revestir» y «Se limitará la longitud de las cunetas, conduciéndolas hacia los cauces naturales del terreno, obras de drenaje transversal o proyectando desagües dónde no existan». El talud de corte de referencia es la Tabla 304.10 (pag. impresa 204, PDF 205): de 1:10 (H:V, roca fija) a 2:1 (arenas) para cortes menores de 5 m; es la ventana del talud exterior en 'seccion_cuneta'.

### Norma Tecnica E.030 «Diseño Sismorresistente»  (`E030`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `E030.T2#S5` | Art. 14.6, Tabla Nº 2, fila S5 | «Tipos de perfiles de suelo» | pág. impresa **11** · PDF 11 | exigencia | 2026-08-29 · texto |
| `E030.T4` | Art. 17, Tabla Nº 4 | «Factor de suelo» | pág. impresa **13** · PDF 13 | exigencia | 2026-08-29 · texto |

> **`E030.T2#S5`** — LA PRIMERA CITA DE E.030 DEL REGISTRO, y llego tarde por un artefacto: el PDF emite la ligadura U+FB01 seguida de un espacio -- «clasiﬁ cación», «perﬁ les», «especíﬁ co» --, de modo que ninguna frase entera de esta norma se encontraba en su propia pagina hasta que `extraccion.pdf` aprendio a deshacerlo. EL ESTATUTO DE S5, con precision: es fila de la Tabla Nº 2 -- sexta y ultima, «Suelos excepcionales», con diez viñetas de las que la PRIMERA es «Suelos potencialmente licuables» y esta es la decima --, y a la vez NO tiene fila en la Tabla Nº 3 del num. 14.7 ni columna en las Tablas Nº 4 y Nº 5. Es decir: nominal en la tabla que la define, laguna en las tres que dan numeros. La prohibicion es CONDICIONADA: la misma oracion la levanta con estudio especifico y mejoramiento del estrato. La hoja de ruta la citaba mal por tres sitios -- corregidos en I2; ver DIS-HR-CLASE-DE-SITIO-F, resuelta --, y su pasaje de Fase 0-bis quedo literal con la elision marcada, como constantes_normativas.E030_S5_TEXTO, que siempre la transcribio exacta.

> **`E030.T4`** — DONDE LOS DOS ESQUEMAS CONVERGEN, que es lo que faltaba mirar. E.030 no tiene F_pga, Fa ni Fv: su aparato es S, T_P y T_L. Y su Tabla Nº 4 «Factor de suelo S» tiene columnas S0, S1, S2, S3 y S4 -- NO tiene columna S5 --, de modo que a su categoria excepcional no le asigna factor, igual que AASHTO y el Manual no se lo asignan a la Clase F. El verbatim es la celda de la fila Z4, columna S4: en la zona sismica de esta obra, E.030 ya exige analisis de respuesta de sitio un escalon ANTES de la categoria excepcional. Con S5 no hay siquiera celda que leer. Los dos esquemas discrepan en el CRITERIO -- E.030 nombra los suelos licuables, AASHTO no -- y coinciden en la CONSECUENCIA: ninguno tabula un factor para su categoria excepcional.

### Norma Tecnica E.050 «Suelos y Cimentaciones»  (`E050`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `E050.17.1#SERVICIO` | Art. 17.1 | «Cargas a utilizar» | pág. impresa **32** · PDF 32 | exigencia | 2026-11-13 · texto |
| `E050.20` | Art. 20.2 y 20.3 | «Capacidad de carga» | pág. impresa **33** · PDF 33 | exigencia | 2026-08-28 · texto |
| `E050.21` | Art. 21.1 y 21.2 | «Factor de seguridad frente a una falla por corte» | pág. impresa **34** · PDF 34 | exigencia | 2026-08-28 · texto |
| `E050.24` | Art. 24 | «Suelos no permitidos para apoyar las cimentaciones» | pág. impresa **37** · PDF 37 | exigencia | 2026-11-11 · texto |
| `E050.24#REMOVER` | Art. 24 | «Suelos no permitidos para apoyar las cimentaciones» | pág. impresa **37** · PDF 37 | exigencia | 2026-11-11 · texto |
| `E050.26.2#PROFUNDIDAD` | Art. 26.2 | «Profundidad de cimentación» | pág. impresa **38** · PDF 38 | exigencia | 2026-11-12 · texto |
| `E050.30.3` | Art. 30.3 | «Cimentaciones superficiales en taludes o en su cercanía» | pág. impresa **39** · PDF 39 | exigencia | 2026-08-28 · texto |
| `E050.38.1` | Art. 38, 38.1 | «Licuación de suelos» | pág. impresa **51** · PDF 51 | definicion | 2026-11-11 · texto |
| `E050.38.4.3` | 38.4.3 | Licuación de suelos › «Exploración de campo» | pág. impresa **51** · PDF 51 | exigencia | 2026-08-28 · texto |
| `E050.39.13.6` | 39.13.6 a) y b) | Sostenimiento de excavaciones › «Muros de contención» | pág. impresa **72** · PDF 72 | exigencia | 2026-08-28 · ambos |
| `E050.39.13.8#DRENAJE` | 39.13.8 | Sostenimiento de excavaciones › «Muros de contención» | pág. impresa **73** · PDF 73 | exigencia | 2026-11-13 · texto |
| `E050.FIG3` | Figura 3 | «Simbología de Suelos (Referencial)» | pág. impresa **31** · PDF 31 | definicion | 2026-11-11 · texto |

> **`E050.17.1#SERVICIO`** — Es lo que fija CON QUE CARGAS se comparan los factores de seguridad de E.050: cargas de SERVICIO, sin factorar. La oracion sigue «…que se utilizan para el diseño estructural de las columnas del nivel más bajo de la edificación»: la norma es de edificaciones, y su aplicacion al cabezal es por analogia [N→].

> **`E050.20`** — El repositorio citaba «Art. 20» a secas; los numerales exactos son 20.2 (cohesivos, phi = 0) y 20.3 (friccionantes, c = 0). El simbolo phi no sobrevive a la extraccion de texto -- la norma lo compone con fuente simbolica --, y por eso el `texto_literal` es el inciso que si se puede buscar.

> **`E050.21`** — LA SEGUNDA CONDICION NO ES «SISMICA» A SECAS: es «solicitacion maxima de sismo O VIENTO (la que sea mas desfavorable)». El viento esta dentro de la misma casilla, y la clave «sismico» del repositorio lo excluia (NOR-E050-01).

> **`E050.24`** — ES LA FUENTE PERUANA MAS CERCANA A «suelos de fundación de mala calidad», que el num. 4.1.1.3.4 a) del Manual de Hidrologia nombra y no define (COND-MARCO-SUELO-MALA-CALIDAD). La E.050 es de EDIFICACIONES y no de obras viales: por eso el conjunto 'sucs_fundacion_deficiente' es [A] --una adopcion apoyada en esta lista-- y no [N]. De los materiales que el articulo enumera, solo dos tienen simbolo SUCS (Figura 3 de la misma norma): la turba (Pt) y el suelo organico (OL, OH); la tierra vegetal y los rellenos no se clasifican por SUCS.

> **`E050.24#REMOVER`** — La segunda frase del articulo, que la cita E050.24 no traia: la norma no se limita a prohibir cimentar sobre turba y suelo organico, MANDA REMOVERLOS Y REEMPLAZARLOS por relleno controlado. El aviso de suelo de fundacion deficiente lo dice con estas palabras (H9 de la auditoria de T-4).

> **`E050.26.2#PROFUNDIDAD`** — La oracion completa: «La profundidad de cimentación es definida por el PR y está condicionada por la estratigrafía del suelo, a cambios de volumen por humedecimiento-secado, hielo-deshielo o condiciones particulares de uso de la estructura, no siendo menor de 0,80 metros…». Y sigue: «En el caso de cimentación sobre roca, el PR define la profundidad de cimentación, pudiendo en este caso ser menor a 0,80 metros». El 26.1, en la misma pagina, la MIDE «desde el nivel de la superficie del terreno a la base de la cimentación». Es el minimo de E.050, la norma con que la Sec. 9.3 de la hoja de ruta verifica la estabilidad del cabezal; no es un valor de proyecto. --- Correcciones de T-7a (H8) --- Para un CABEZAL VIAL se aplica POR ANALOGIA ([N→], criterio 'profundidad_cimentacion_min_cabezal_m'), no como [N]: ver la `Interpretacion`.

> **`E050.30.3`** — AQUI la norma SI dice «condiciones sismicas». Es el unico de los tres numerales de FS que usa esa palabra.

> **`E050.38.1`** — El 38.1 lo dice de los suelos granulares y de algunos suelos granulares con finos cohesivos ubicados bajo la napa freatica; el 38.2, en la misma pagina, lista las caracteristicas que el suelo tiene que presentar a la vez para ser susceptible, y el 38.5 (pag. 52) manda el analisis del potencial de licuacion por Seed e Idriss. ESTE PROGRAMA NO EVALUA LA LICUACION: la cita existe para que la linea «no esta entre los grupos declarados deficientes» de un suelo SM, SP o ML no se lea como «apto» (H9).

> **`E050.38.4.3`** — NOR-E050-02, cerrado, y con un hallazgo de mas. (1) EL ESPACIAMIENTO SI TIENE NUMERAL: es este, y el repositorio lo declaraba «sin numeral». Ademas va reforzado con «obligatoriamente». (2) LO GRAVE, que el repositorio omitia: los dos valores viven bajo «Articulo 38.- Licuacion de suelos», y el 38.4.1 los dispara SOLO «Cuando la historia sismica del lugar haga sospechar la posibilidad de ocurrencia de Licuacion». NO son el programa de SPT general de E.050 -- ese esta en el 14.2.3 y la Tabla 3, pags. 18-19 --: son el programa de exploracion PARA ANALISIS DE LICUEFACCION. Citarlos como minimos universales del SPT extiende la norma mas alla de lo que dice.

> **`E050.39.13.6`** — NOR-E050-01, cerrado. La palabra «sismico» NO APARECE en este numeral: la segunda condicion se llama «Condición Pseudo - dinámico» en a-2 y «condición pseudo-dinámica» en b). No es un sinonimo decorativo -- designa el METODO de analisis, coeficiente sismico horizontal aplicado como fuerza estatica equivalente --, y E.050 usa CUATRO vocabularios distintos para esa casilla segun el numeral: «sismo o viento» (Art. 21.2), «condiciones sismicas» (Art. 30.3), «pseudo-dinamico» (39.13.6) y «dinamico» a secas (Anexo I, pag. impresa 74). Y una coletilla que el repositorio no recogia cierra el numeral y condiciona a) y b) por igual: «En todos los casos respecto al estado límite del suelo».

> **`E050.39.13.8#DRENAJE`** — LA REMISION ESTA ERRADA EN EL EJEMPLAR: no existe un numeral 39.14.6; los factores de seguridad del muro de contencion estan en el 39.13.6, una pagina antes. Se lee 39.13.6. Sigue: «El sistema de drenaje estará formado por un filtro graduado de material granular sin finos o por un geotextil o geodren», y la Figura 23 lo dibuja. Aplicado al cabezal por analogia [N→].

> **`E050.FIG3`** — Los quince simbolos SUCS con su descripcion: GW, GP, GM, GC, SW, SP, SM, SC, ML, CL, OL, MH, CH, OH y Pt. La figura se rotula «(Referencial)». Es el conjunto cerrado del que 'sucs_fundacion_deficiente' elige, transcrito en la tabla E050.FIG3. Los simbolos DOBLES de un suelo de frontera («SP-SM» en el CSV de ejemplo) no estan en la figura: se componen de dos de estos.

### Norma Tecnica E.060 «Concreto Armado»  (`E060`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `E060.11.10.1` | 11.10.1 | «DISPOSICIONES ESPECIALES PARA MUROS» | pág. impresa **103** · PDF 103 | exigencia | 2026-09-20 · texto |
| `E060.11.10.10.2` | 11.10.10.2 | 11.10 DISPOSICIONES ESPECIALES PARA MUROS › «Diseño del refuerzo para cortante en muros» | pág. impresa **104** · PDF 104 | exigencia | 2026-09-20 · texto |
| `E060.11.10.10.3` | 11.10.10.3 | 11.10 DISPOSICIONES ESPECIALES PARA MUROS › «Diseño del refuerzo para cortante en muros» | pág. impresa **104** · PDF 104 | exigencia | 2026-09-20 · ambos |
| `E060.11.10.2` | 11.10.2 | «DISPOSICIONES ESPECIALES PARA MUROS» | pág. impresa **103** · PDF 103 | exigencia | 2026-09-20 · texto |
| `E060.14.3.1` | 14.3.1 | «REFUERZO MÍNIMO» | pág. impresa **133** · PDF 133 | exigencia | 2026-08-28 · texto |
| `E060.14.3.2` | 14.3.2 | «REFUERZO MÍNIMO» | pág. impresa **133** · PDF 133 | exigencia | 2026-08-28 · texto |
| `E060.14.3.3` | 14.3.3 | «REFUERZO MÍNIMO» | pág. impresa **133** · PDF 133 | exigencia | 2026-08-28 · texto |
| `E060.14.5.3.2` | 14.5.3.2 | 14.5 › MÉTODO EMPÍRICO DE DISEÑO PARA MUROS DE CARGA › «Espesor mínimo de muros diseñados por el método empírico de diseño» | pág. impresa **134** · PDF 134 | exigencia | 2026-11-12 · texto |
| `E060.14.8.4` | 14.8.4 | «Muros de contención» | pág. impresa **134** · PDF 134 | exigencia | 2026-08-28 · texto |
| `E060.15.7#PERALTE` | 15.7 | «PERALTE MÍNIMO DE LAS ZAPATAS» | pág. impresa **138** · PDF 138 | exigencia | 2026-11-13 · texto |
| `E060.22.10.2#CICLOPEO` | 22.10.2.1 | 22.10 CONCRETO CICLOPEO › «Limitaciones» | pág. impresa **195** · PDF 195 | exigencia | 2026-11-13 · texto |
| `E060.22.7.4#ZAPATA` | 22.7.4 | «ZAPATAS» | pág. impresa **193** · PDF 193 | exigencia | 2026-11-12 · texto |
| `E060.4.4.2` | 4.4.2 | «PROTECCIÓN DEL REFUERZO CONTRA LA CORROSIÓN» | pág. impresa **39** · PDF 39 | exigencia | 2026-08-28 · texto |
| `E060.7.7.1` | 7.7.1 | 7.7 RECUBRIMIENTO DE CONCRETO PARA EL REFUERZO › «Concreto construido en sitio (no preesforzado)» | pág. impresa **54** · PDF 54 | exigencia | 2026-08-28 · texto |
| `E060.7.7.5.1` | 7.7.5.1 | «Ambientes corrosivos» | pág. impresa **55** · PDF 55 | exigencia | 2026-08-28 · texto |
| `E060.T4.2` | Tabla 4.2 | «REQUISITOS PARA CONDICIONES ESPECIALES DE EXPOSICIÓN» | pág. impresa **37** · PDF 37 | exigencia | 2026-08-28 · ambos |
| `E060.T4.4` | Tabla 4.4 | «REQUISITOS PARA CONCRETO EXPUESTO A SOLUCIONES DE SULFATOS» | pág. impresa **38** · PDF 38 | exigencia | 2026-08-28 · ambos |

> **`E060.11.10.1`** — LA PREGUNTA DE APLICABILIDAD, dicha por la norma: el cortante PERPENDICULAR al plano --- que es el que el empuje de tierras produce en la pantalla de un cabezal --- se diseña por 11.12 (losas), no por 11.10. Antes de aplicar el 0.0025 de 11.10.10.2 hay que decir en que plano actua el cortante que lo dispara.

> **`E060.11.10.10.2`** — El titulo de la jerarquia esta en la PDF 103 y el del 11.10.10 en la 104. El 0,0025 rige BAJO 11.10.10, que 11.10.7 y 11.10.8 disparan por Vu contra 0,085·raiz(f'c)·Acw; fuera de ese regimen el piso es el 0,002 del 14.3.1 (cita E060.14.3.1, cuya primera oracion remite aqui). El valor NO se transcribe como constante [N] en esta sesion: lo cablea EXT-7 con su caso patron.

> **`E060.11.10.10.3`** — EL VERBATIM SE CORTA DONDE EMPIEZA EL SIMBOLO: la capa de texto imprime «ρv» como glifos sueltos y la ecuacion como imagen, de modo que la oracion entera no se encuentra por texto. Leida sobre la pagina renderizada (EXT-6), la ec. (11-32) es ρv = 0,0025 + 0,5·(2,5 − hm/ℓm)·(ρh − 0,0025) ≥ 0,0025, «pero no necesita ser mayor que el valor de ρh requerido por 11.10.10.1», con hm la altura total del muro y ℓm su longitud total. Es lo que R95-031 (H-13) señalo: bajo el regimen de 11.10.10 la cuantia VERTICAL tambien tiene piso 0,0025, y `M9.cuantia_de_diseno` devolvia 0,0015 en vertical con cortante alto. Se corrige en EXT-7 (EXT-M-05); aqui queda la cita que le faltaba.

> **`E060.11.10.2`** — La segunda oracion del numeral --- «Para muros estructurales que resistan cargas en su plano originadas por la acción de los sismos, se aplicará adicionalmente lo dispuesto en 21.9» --- no se transcribe: el cabezal no es muro estructural de un edificio.

> **`E060.14.3.1`** — EL ESCALONAMIENTO 0,002 -> 0,0025 LO ANUNCIA ESTE MISMO NUMERAL, no solo el 11.10.10.2: su primera oracion remite a 11.10 «a menos que se requiera una cantidad mayor por cortante». La norma imprime «0,002» y «0,0015».

> **`E060.14.3.3`** — El repositorio no le asignaba pagina; es la impresa 133. Y hay un SEGUNDO numeral con el mismo contenido y otras palabras: el 14.8.4 (pag. impresa 134), que es el que rige DIRECTAMENTE un muro de contencion como el cabezal.

> **`E060.14.5.3.2`** — EXIGENCIA DENTRO DE SU AMBITO, que no es el del marco: el 14.5.3 fija el espesor minimo de los muros diseñados por el METODO EMPIRICO de 14.5, y la pared de un marco enterrado se diseña por flexion y carga axial (14.8.1 remite al Capitulo 10). Lo que la hace la fuente mas cercana para el espesor de un marco a nivel de perfil es su OBJETO: un muro exterior ENTERRADO, con suelo contra una cara, que es lo que es la pared del cajon. El proyecto la aplica POR ANALOGIA como piso del criterio [A] 'espesor_pared_cajon'; no es [N] para el marco. Leida en la capa de texto de la pagina 134 (que imprime «los  muros  exteriores» con doble espacio).

> **`E060.14.8.4`** — Hallado al verificar: es el gemelo del 14.3.3 para muros de contencion, y por tanto el aplicable directo a un cabezal. El expediente citaba solo el 14.3.3.

> **`E060.15.7#PERALTE`** — La frase sigue: «ni menor de 400 mm en el caso de zapatas apoyadas sobre pilotes». Es del Capitulo 15 (zapatas de concreto ARMADO), que la Via 1 de la §0.2 de la hoja de ruta saca del diseño estructural (rige AASHTO LRFD Seccion 5), y E.060 es una norma de edificaciones: aplicada a la zapata del cabezal de voladizo armado es una ANALOGIA, y el criterio que la usa es [N→] ('peralte_min_zapata_armada_m'). El espesor total suma ademas el recubrimiento del refuerzo inferior contra el suelo (E.060 7.7.1 a), 70 mm, que si rige por la excepcion de durabilidad de la §0.2).

> **`E060.22.10.2#CICLOPEO`** — El 22.10.2.2, en la misma pagina, sigue: «En elementos en voladizo con una longitud mayor a la mitad de su peralte, será necesario verificar las resistencias en flexión y corte», y el 22.10.2.3 fija φ = 0,5 y f'c de diseño no mayor de 10 MPa. Es el limite del cabezal de GRAVEDAD en ciclopeo: un muro de gravedad, no un voladizo de concreto simple. La regla del tipo por altura de 'predimensionamiento_cabezal' no lo juzga (es geometria); lo juzga T-7c, y la memoria lo avisa cuando el tipo sale de gravedad.

> **`E060.22.7.4#ZAPATA`** — Capitulo 22, «Concreto estructural simple», que es el que la hoja de ruta §9.4 y M9.verificar_ciclopeo aplican al cabezal de gravedad en concreto ciclopeo (Art. 22.10). La Via 1 de la §0.2 saca a E.060 del diseño estructural ARMADO; el ciclopeo no tiene otra norma en normas/, y por eso este minimo se aplica al cabezal de gravedad y no al de voladizo armado.

> **`E060.4.4.2`** — ES EL ESLABON QUE ATA EL CLUSTER DE DURABILIDAD DE PUNTA A PUNTA: manda aplicar la Tabla 4.2 a los cloruros externos Y remite al recubrimiento del 7.7. Sin el, la cadena a/c -> recubrimiento queda sin numeral que la sostenga. El disparador es acotado -- cloruros «de quimicos descongelantes, sal, agua salobre, agua de mar o salpicaduras» --, no cloruros en el suelo en general.

> **`E060.7.7.1`** — EL PROPIO ENCABEZADO REMITE AL 7.7.5.1: el aumento por ambiente corrosivo no es una nota externa que alguien decidio traer, es la excepcion que el articulo de los 70/50/40 mm declara.

> **`E060.7.7.5.1`** — EXIGENCIA DE RESULTADO SIN CUANTIFICAR: manda aumentar y no dice cuanto. El cuanto es [A] del proyectista, y la ALTERNATIVA del final -- «o debe disponerse de otro tipo de proteccion» -- es un camino de cumplimiento distinto que este expediente no contempla y que hay que dejar visible.

> **`E060.T4.2`** — La invocan DOS numerales por vias distintas, y los dos hacen falta: el 4.2.2 (pag. impresa 37) por condiciones especiales de exposicion en general, y el 4.4.2 (pag. impresa 39) especificamente para los cloruros, que es el disparador de este expediente.

> **`E060.T4.4`** — La invoca el num. 4.3.1, bajo «4.3 EXPOSICION A SULFATOS». El `texto_literal` es la NOTA COMUN a las dos tablas, y esta a proposito: es la regla que decide que se especifica cuando el sitio tiene sulfatos Y cloruros a la vez -- el caso de un corredor costero con freatico somero --, y esta impresa al pie de LAS DOS (pags. 37 y 38), colgando en cada una de las columnas de a/c y de f'c. Transcribir una tabla sin la otra deja el requisito a medias.

### Manual de Carreteras "Especificaciones Tecnicas Generales para Construccion" (EG-2013)  (`EG2013`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `EG2013.205.12#COMPACTACION` | 205.12 c) 1 | «Compactación» | pág. impresa **193** · PDF 201 | exigencia | 2026-11-12 · texto |
| `EG2013.205.12c1` | 205.12 c) 1. | «205.12 Criterio» | pág. impresa **193** · PDF 201 | exigencia | 2026-08-28 · texto |
| `EG2013.501.07` | 501.07 | «Tolerancias» | pág. impresa **889** · PDF 897 | exigencia | 2026-11-12 · texto |
| `EG2013.503.01#ALCANCE` | 503.01 | «Descripción» | pág. impresa **905** · PDF 913 | definicion | 2026-08-28 · texto |
| `EG2013.503.04#T503_07` | 503.04, Tabla 503-07 | «Clases de concreto» | pág. impresa **912** · PDF 920 | exigencia | 2026-08-28 · ambos |
| `EG2013.503.10h#CAJON` | 503.10 h) | «Operaciones para el vaciado de la mezcla» | pág. impresa **926** · PDF 934 | recomendacion | 2026-08-28 · texto |
| `EG2013.503.11g#COTAS` | 503.11 g) 2. | 503.11 Criterios › «Calidad del trabajo terminado» | pág. impresa **934** · PDF 942 | exigencia | 2026-11-12 · texto |
| `EG2013.506.01#ALCANCE` | 506.01 | «Descripción» | pág. impresa **959** · PDF 967 | definicion | 2026-08-28 · texto |
| `EG2013.506.02#CLASE` | 506.02 | «Tubería» | pág. impresa **959** · PDF 967 | exigencia | 2026-11-12 · texto |
| `EG2013.506.07` | 506.07 | «Solado» | pág. impresa **960** · PDF 968 | exigencia | 2026-11-12 · texto |
| `EG2013.506.10` | 506.10 | «Sujeción» | pág. impresa **961** · PDF 969 | exigencia | 2026-11-12 · texto |
| `EG2013.507.02#EMPERNADA` | 507.02 a) | «Tubos conformados estructuralmente de planchas o láminas corrugadas de acero galvanizado en caliente» | pág. impresa **969** · PDF 977 | exigencia | 2026-11-12 · texto |
| `EG2013.507.10` | 507.10 | «Aguas y Suelos agresivos» | pág. impresa **974** · PDF 982 | exigencia | 2026-11-11 · texto |
| `EG2013.508.02#GRANULAR` | 508.02 d) | «Material para cama de asiento» | pág. impresa **982** · PDF 990 | exigencia | 2026-11-12 · texto |
| `EG2013.508.02a` | 508.02 a | «Tubos de polietileno de alta densidad (PAD o HDPE)» | pág. impresa **981** · PDF 989 | definicion | 2026-11-11 · texto |
| `EG2013.508.07#COMPACTACION` | 508.07 | «Colocación del relleno alrededor de la estructura» | pág. impresa **984** · PDF 992 | exigencia | 2026-11-12 · texto |
| `EG2013.508.07#RELLENO_MIN` | 508.07 | «Colocación del relleno alrededor de la estructura» | pág. impresa **984** · PDF 992 | exigencia | 2026-08-28 · texto |
| `EG2013.511.05#T511_02_NOTA_5` | 511.05, Tabla 511-02, nota (5) | «511.05 Geotextiles usados en subdrenaje» | pág. impresa **1011** · PDF 1019 | definicion | 2026-11-12 · ambos |
| `EG2013.511.08#EROSION` | 511.08 | «511.08 Geotextiles usados en control permanente de erosión» | pág. impresa **1014** · PDF 1022 | definicion | 2026-11-12 · texto |
| `EG2013.511.08#NOTA_5A` | 511.08, Tabla 511-06, nota (5) a | «511.08 Geotextiles usados en control permanente de erosión» | pág. impresa **1015** · PDF 1023 | recomendacion | 2026-11-12 · texto |
| `EG2013.511.08#T511_06` | 511.08, Tabla 511-06 | «511.08 Geotextiles usados en control permanente de erosión» | pág. impresa **1015** · PDF 1023 | exigencia | 2026-11-12 · texto |
| `EG2013.T205-01` | 205.02, Tabla 205-01 | «Requisitos de los materiales» | pág. impresa **186** · PDF 194 | exigencia | 2026-11-12 · texto |
| `EG2013.T301-01` | 301.02, Tabla 301-01 | «Tabla 301-01» | pág. impresa **238** · PDF 246 | exigencia | 2026-11-12 · texto |
| `EG2013.T507-01` | 507.02 a), Tabla 507-01 | «Espesores Mínimos de Alcantarillas Circulares y Abovedadas» | pág. impresa **970** · PDF 978 | exigencia | 2026-11-12 · texto |

> **`EG2013.205.12#COMPACTACION`** — Y «el 95% ... cuando se verifique la compactación de la corona del terraplén». La Seccion 502 (rellenos para estructuras) remite a estos mismos niveles (502.09(c)(1)).

> **`EG2013.205.12c1`** — ES LA REMISION DE SEGUNDO NIVEL de tres de las cuatro fichas de cama y relleno: el «95 % MDS» que el expediente les atribuia no es literal de las Secciones 505, 506 ni 507 -- llega desde aqui, por remision. El valor es correcto; lo que faltaba era decir por que via llega, que es la diferencia entre una cita y una deduccion.

> **`EG2013.501.07`** — Seccion 501, excavacion para estructuras. Es el extremo ALTO de la ventana del criterio [A] 'desajuste_empalme_canal_m': la cota de la excavacion que recibe la losa de fondo admite 2 cm. Tampoco habla de empalmes: es analogia declarada.

> **`EG2013.503.01#ALCANCE`** — «ESTRUCTURAS DE DRENAJE» ES EL TERMINO DE ENCABEZAMIENTO y la lista que sigue es ENUNCIATIVA, no cerrada: un marco de concreto vaciado in situ es una estructura de drenaje y no esta nombrado ahi. Que si lo esta bajo esta Seccion lo prueba el 503.10 h), que le fija plazo de desencofrado a la «placa superior en alcantarillas de cajon». Por si sola esta cita NO dice que el marco se pague aqui: eso es ensamblaje del proyecto sobre las tres citas mas la ausencia de partida propia.

> **`EG2013.503.04#T503_07`** — La tabla tiene DOS columnas, no tres: «Clase» y «Resistencia minima a la compresion a 28 dias». El uso no es columna, es encabezado de grupo dentro de la primera. Y no lleva ninguna nota al pie.

> **`EG2013.503.10h#CAJON`** — ES LA UNICA MENCION DEL CAJON DE CONCRETO EN TODO EL EG-2013 -- barrido de las 1282 paginas, ver SIN_PARTIDA_DE_CAJON_EG2013 -- y hay que leerla por lo que prueba y no por lo que dice. LO QUE PRUEBA: que el EG-2013 CONTEMPLA la alcantarilla de cajon de concreto y la regula bajo la Seccion 503, «Concreto estructural». Una norma que fija plazo de desencofrado de la placa superior de un cajon esta regulando su vaciado in situ. LO QUE NO DICE: nada sobre pago, ni sobre cobertura, ni sobre dimensiones. Y su CARACTER no es exigencia: el parrafo que la introduce dice «Excepcionalmente si las operaciones de campo no estan controladas por pruebas de laboratorio la siguiente lista PUEDE ser empleada como GUIA para el tiempo minimo requerido antes de la remocion de encofrados y soportes». O sea que el plazo es guia condicionada; lo que NO es condicionado es la existencia de la fila, que es lo unico que este proyecto le pide.

> **`EG2013.503.11g#COTAS`** — Es una tolerancia de ACEPTACION de la obra terminada (503.11, «Aceptación de los trabajos»), bajo el rotulo «2. Otras tolerancias» de g. «Calidad del trabajo terminado», junto a «Espesores de placas: -10 mm a +20 mm». La cota superior de la placa de FONDO de un marco es su invert: el proyecto la toma POR ANALOGIA como el desajuste que admite el empalme de la salida con el fondo del canal (VC2, criterio [A] 'desajuste_empalme_canal_m'). La fuente no habla de empalmes ni de canales.

> **`EG2013.506.01#ALCANCE`** — LO QUE ESTA CITA HACE ES DELIMITAR, y por eso es DEFINICION y no EXIGENCIA: no prohibe nada, dice de que trata la Seccion. Su objeto es «la instalacion de TUBOS», y las otras tres piezas de la misma Seccion lo confirman -- 506.02 remite a AASHTO M-170M y pide el «diametro interno», y la partida 506.A del Anexo 2 se mide en METRO LINEAL --. Un marco vaciado in situ no tiene diametro interior ni se mide por metro lineal de tubo suministrado: la 506 no lo alcanza. Los cuatro titulos de las Secciones 505 a 508 empiezan por «Tuberia».

> **`EG2013.506.02#CLASE`** — La norma peruana manda que el PROYECTO indique la clase: es la salida de la Fase 8 para el tubo de concreto, no una entrada.

> **`EG2013.506.07`** — El solado: «una capa o solado de material granular, que cumplan con las características de material para subbase, de por lo menos 15 cm de espesor compactado», compactado como la corona del terraplen (205.12(c)(1): 95 % del Proctor Modificado). La sujecion (506.10) sube con el mismo material y la misma densidad hasta un sexto del diametro exterior; el relleno (506.11) es el de la Seccion 502.

> **`EG2013.506.10`** — Por encima de 1/6 del diametro exterior el relleno es el de la Seccion 502 (506.11), que remite a la densidad de 205.12(c)(1): 90 % del Proctor Modificado en base y cuerpo. Con esas dos exigencias el EG-2013 no garantiza el 95 % de Categoria I en toda la zona de riñones que pide el Tipo 1 de AASHTO, y si excluye el Tipo 4, que no exige compactacion: es la lectura con que 'instalacion_estandar_concreto' fija su ventana.

> **`EG2013.507.02#EMPERNADA`** — El mismo inciso fija las normas de los pernos (ASTM A-449 / F568 y A 307 Grado A) y de las tuercas (A-563 Grado C), y habla del «corrugado, perforado y formación de las planchas».

> **`EG2013.507.10`** — ES EL UNICO UMBRAL NUMERICO DE DURABILIDAD DE LA TUBERIA QUE LA NORMA PERUANA ESCRIBE, y esta en la Seccion 507 «Tubería metálica corrugada»: pH < 5.8 del AGUA QUE CONDUCE el tubo. EXIGE PROTEGER, no prohibe el material, y no dice con que («acorde al Proyecto»). «Sustancias agresivas» del suelo no se cuantifica. Las Secciones 505, 506 y 508 (concreto simple, concreto reforzado y polietileno) no traen clausula equivalente: buscadas por «agresiv», «corrosi», «salin», «pH» y «resistividad» en las pags. PDF 940 a 1000.

> **`EG2013.508.02#GRANULAR`** — La Seccion 301 es la de los afirmados: franjas granulometricas con 5 a 25 % de finos e indice de plasticidad de 4 a 9 (cita EG2013.T301-01). La misma letra dice que la cama «estará constituida por arena gruesa».

> **`EG2013.508.02a`** — La norma peruana de construccion DEFINE el producto: interior liso y pared exterior corrugada; sigue «Debe cumplir con la guía AASHTO, clasificación tipo “S”» y remite a AASHTO M294. Respalda DOS cosas de T-4: que la fila de n que corresponde al HDPE en la Table B.1 de HDS-5 es la de interior liso («Smooth») y no la corrugada, y que el diametro exterior del tubo no es el interior mas una pared delgada sino mas la altura de un perfil corrugado.

> **`EG2013.508.07#COMPACTACION`** — El material del relleno es el de la Seccion 502 (mismo numeral), y el de la cama y la SUJECION LATERAL lo fija el 508.02 d): granular (cita EG2013.508.02#GRANULAR). Con 95 % del Proctor MODIFICADO la compactacion es al menos la de las columnas «-95» de la Tabla 12.12.3.5-1 de AASHTO (Proctor ESTANDAR, T 99), porque la densidad maxima del ensayo modificado no es menor que la del estandar. La version anterior de esta nota decia que el tipo de suelo no lo fija la norma y que por eso se tomaba «el mas desfavorable» (Cl-95): omitia el 508.02 d) (auditoria de T-5).

> **`EG2013.508.07#RELLENO_MIN`** — NOR-EG-01 / NOR-EG-02. La pagina impresa es la 984 (PDF 992). La 982 (PDF 990) trae 508.02 b), c) y d) -- calidad del tubo, muestreo y material para cama de asiento --, nada de altura de relleno. El desfase de este documento es +8, el mayor del corpus, y confundir impresa con PDF produce exactamente ese error. NO CONFUNDIR CON SU VECINA: el 508.08 (pag. impresa 985) tambien dice 0,30 m, pero es la exigencia de EJECUCION -- que el equipo pesado no circule antes de alcanzarla --, no la altura minima de diseño. Dos frases con el mismo numero en paginas contiguas.

> **`EG2013.511.05#T511_02_NOTA_5`** — LA TABLA HERMANA de la 511-06, en la misma Seccion 511: misma fila «Tamaño de Abertura Aparente», mismas tres columnas por el pasante del tamiz N.º 200 y las mismas celdas 0,43 / 0,25 / 0,22. Aqui las dos notas llevan numeros DISTINTOS: el rotulo de la fila dice «Tamaño de Abertura Aparente (3) (4)», y la (4) es el diseño para un sitio especifico en suelos problematicos; la nota de los suelos cohesivos es la (5), que termina «es de 0.30 mm», y la lleva SOLO la celda «0,22 (5)» de la columna «>50». Leida por texto y por imagen. No se aplica al enrocado --es la tabla de subdrenaje--: se cita como el hecho de la propia fuente que sostiene la lectura de la nota (5) de la Tabla 511-06 (`Interpretacion` de EG2013.511.08#T511_06).

> **`EG2013.511.08#EROSION`** — Define el AMBITO: el geotextil que va entre un enrocado y el suelo. El parrafo siguiente dice «La función principal del geotextil es la filtración». EL NUMERAL NO OBLIGA A PONER FILTRO: especifica el geotextil cuando el proyecto lo pone. EG-2013 no trae la palabra «emboquillado» en ninguna de sus 1282 paginas (barrido por texto en T-8), y su Seccion 603 «Defensas ribereñas» trata el enrocado de ribera, no el de salida de alcantarilla.

> **`EG2013.511.08#NOTA_5A`** — Frase completa: «Debería efectuarse un diseño del geotextil para un sitio específico especialmente si uno o más de los siguientes suelos problemáticos son encontrados: suelos inestables o altamente erosionables tales como los limos no cohesivos; suelos de gradación abierta; suelos laminados alternando arenas y limos; arcillas dispersivas y/o polvo de roca.» La llamada (5) la llevan el rotulo de la FILA «Tamaño de Abertura Aparente (3) (4) (5)» y la celda «0,22(5)». El proyecto lee que el rotulo llama a ESTA nota, que vale para la fila entera, y la celda a la (5) b (`Interpretacion` de la cita EG2013.511.08#T511_06).

> **`EG2013.511.08#T511_06`** — La Tabla 511-06 «Geotextiles para control permanente de erosión-requerimientos» entra por el «Porcentaje de Suelo in Situ que pasa Tamiz N.º 200 (0,075 mm)» en tres columnas (< 15, 15-50, > 50) y fija la permitividad minima (0,7 / 0,2 / 0,1 s-1) y el tamaño de abertura aparente maximo (0,43 / 0,25 / 0,22 mm); la clase es la 1 de la Tabla 511-01 (la 2 para los tejidos de monofilamento) y la estabilidad ultravioleta, 50 % tras 500 horas. Su nota (5) a pide un diseño especifico en suelos problematicos y su nota (5) b da 0,30 mm para cohesivos con indice de plasticidad mayor de 7. LA LLAMADA (5) APARECE DOS VECES, en el rotulo de la fila «Tamaño de Abertura Aparente (3) (4) (5)» y en la celda «0,22(5)» de la columna «>50», y la tabla no dice que nota llama cada una: la lectura del proyecto va en `interpretacion`. El dato que la tabla pide --el pasante del tamiz N.º 200-- es del EMS.

> **`EG2013.T205-01`** — Los materiales de terraplen, que la Seccion 502 (502.02, pag. impresa 895) manda usar en los rellenos para estructuras: «Tipo de Material: A-1-a, A-1-b, A-2-4, A-2-6 y A-3», con indice de plasticidad menor de 11 en base y cuerpo y menor de 10 en la corona. El A-2-6 es el mas plastico de los cinco, y la Tabla 12.12.3.5-2 de AASHTO LRFD lo agrupa con las arcillas (Cl).

> **`EG2013.T301-01`** — Requisitos del afirmado, al pie de la Tabla 301-01 (franjas A-1, A-2, C, D, E y F, con 5-20, 5-20, 5-15, 5-20, 6-20 y 8-25 % que pasa el tamiz N.° 200): limite liquido 35 % max., indice de plasticidad 4-9 %, CBR 40 % min.

> **`EG2013.T507-01`** — Circular: 0.60 m -> 1.80 mm; 0.90 -> 2.00; 1.20 -> 2.50; 1.50 -> 3.00; 1.80 -> 3.30 (al pie: «ASTM–A–760, TABLA 1 – ASTM–A-929 – TABLA 4»). ES LA UNICA CIFRA PERUANA SOBRE EL CALIBRE DEL TMC y hasta T-5 ningun modulo la leia: la plancha adoptada de 2.01 mm queda por debajo del minimo desde 1.20 m de diametro. Vista de calculo: ESPESOR_MIN_TMC_EG2013_MM.

### HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-HIF-12-026)  (`HDS5_3ED`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `HDS5_3ED.1.2#MODELO` | 1.2 | «COMPARISONS BETWEEN CULVERTS, BRIDGES, AND STORM DRAINS» | pág. impresa **1.4** · PDF 42 | recomendacion | 2026-09-22 · ambos |
| `HDS5_3ED.1.2#NBIS` | 1.2 | «COMPARISONS BETWEEN CULVERTS, BRIDGES, AND STORM DRAINS» | pág. impresa **1.3** · PDF 41 | definicion | 2026-09-22 · ambos |
| `HDS5_3ED.2.2.4#LONGITUD` | 2.2.4 b. | «Roadway Data» | pág. impresa **2.8** · PDF 70 | aproximacion | 2026-11-11 · ambos |
| `HDS5_3ED.2.2.5#EMBALSE` | 2.2.5 | «Allowable Headwater» | pág. impresa **2.9** · PDF 71 | definicion | 2026-11-13 · texto |
| `HDS5_3ED.2.2.5#NO_EXCEDER` | 2.2.5 | «Allowable Headwater» | pág. impresa **2.9** · PDF 71 | recomendacion | 2026-11-13 · texto |
| `HDS5_3ED.2.2.5a#COTA_CRITICA` | 2.2.5 a. | «Allowable Headwater» | pág. impresa **2.10** · PDF 72 | permiso | 2026-11-13 · texto |
| `HDS5_3ED.2.2.5a#COTA_DE_DANO` | 2.2.5 a. | «Allowable Headwater» | pág. impresa **2.10** · PDF 72 | permiso | 2026-11-13 · texto |
| `HDS5_3ED.3.1.3#CRITICO_EN_LA_ENTRADA` | 3.1.3 | «3.1.3  Inlet Control» | pág. impresa **3.2** · PDF 84 | definicion | 2026-11-12 · texto |
| `HDS5_3ED.3.1.3#SUMERGENCIA` | 3.1.3 | «Inlet Control» | pág. impresa **3.2** · PDF 84 | definicion | 2026-09-20 · texto |
| `HDS5_3ED.3.1.3#TRANSICION` | 3.1.3 | «Inlet Control» | pág. impresa **3.4** · PDF 86 | aproximacion | 2026-08-28 · texto |
| `HDS5_3ED.3.1.4#0_75D` | 3.1.4 | «Outlet Control» | pág. impresa **3.12** · PDF 94 | exigencia | 2026-09-21 · texto |
| `HDS5_3ED.3.1.4#EMPALME` | 3.1.4, ec. (3.7) | «Outlet Control» | pág. impresa **3.12** · PDF 94 | definicion | 2026-09-21 · texto |
| `HDS5_3ED.3.1.4#HW_REMANSO` | 3.1.4 | «Outlet Control» | pág. impresa **3.12** · PDF 94 | definicion | 2026-09-21 · texto |
| `HDS5_3ED.3.1.4#K` | 3.1.4, ec. (3.4b) | «Outlet Control» | pág. impresa **3.10** · PDF 92 | definicion | 2026-08-28 · texto |
| `HDS5_3ED.3.1.4#LONGITUD` | 3.1.4 | «Outlet Control» | pág. impresa **3.9** · PDF 91 | aproximacion | 2026-11-11 · texto |
| `HDS5_3ED.3.1.4#REMANSO` | 3.1.4 | «Outlet Control» | pág. impresa **3.12** · PDF 94 | definicion | 2026-09-21 · texto |
| `HDS5_3ED.3.1.6#V_SALIDA` | 3.1.6 | «Outlet Velocity» | pág. impresa **3.18** · PDF 100 | definicion | 2026-09-20 · texto |
| `HDS5_3ED.3.1.6#V_SALIDA_TW` | 3.1.6 | «Outlet Velocity» | pág. impresa **3.18** · PDF 100 | definicion | 2026-09-20 · texto |
| `HDS5_3ED.3.3.2#V_SALIDA_ENTRADA` | 3.3.2 | «Inlet Control» | pág. impresa **3.24** · PDF 106 | aproximacion | 2026-09-20 · texto |
| `HDS5_3ED.3.3.3#HO` | 3.3.3 | «Outlet Control» | pág. impresa **3.24** · PDF 106 | aproximacion | 2026-08-28 · texto |
| `HDS5_3ED.3.3.3#HO_1_2D` | 3.3.3 | «Outlet Control» | pág. impresa **3.24** · PDF 106 | exigencia | 2026-08-28 · texto |
| `HDS5_3ED.3.3.3#HO_SUMERGIDA` | 3.3.3 | «Outlet Control» | pág. impresa **3.24** · PDF 106 | exigencia | 2026-08-28 · texto |
| `HDS5_3ED.3.3.4#HORIZONTAL` | 3.3.4 | «Culverts with Horizontal or Adverse Slopes» | pág. impresa **3.25** · PDF 107 | permiso | 2026-11-11 · texto |
| `HDS5_3ED.3.3.4#H_SIN_AJUSTE` | 3.3.4 | «Culverts with Horizontal or Adverse Slopes» | pág. impresa **3.25** · PDF 107 | permiso | 2026-11-11 · texto |
| `HDS5_3ED.3.3.4#KS` | 3.3.4 | «Culverts with Horizontal or Adverse Slopes» | pág. impresa **3.25** · PDF 107 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.3.3.5#ENCAJE` | 3.3.5 | «Evaluation of Results» | pág. impresa **3.25** · PDF 107 | exigencia | 2026-11-11 · texto |
| `HDS5_3ED.3.3.5#GOBIERNA` | 3.3.5 | «Evaluation of Results» | pág. impresa **3.25** · PDF 107 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.3.5#PERFIL` | 3.5 | «CULVERT DESIGN USING SOFTWARE (WATER SURFACE PROFILES)» | pág. impresa **3.36** · PDF 118 | definicion | 2026-09-21 · texto |
| `HDS5_3ED.3.5.1#H2` | 3.5.1 | «USGS Flow Types and Water Surface Profiles» | pág. impresa **3.37** · PDF 119 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.3.5.1#S1` | 3.5.1 | «USGS Flow Types and Water Surface Profiles» | pág. impresa **3.37** · PDF 119 | definicion | 2026-09-21 · texto |
| `HDS5_3ED.3.5.1#TIPO7` | 3.5.1 | «USGS Flow Types and Water Surface Profiles» | pág. impresa **3.38** · PDF 120 | definicion | 2026-09-21 · texto |
| `HDS5_3ED.5.3.1#ENTRADA` | 5.3.1 | «5.3.1  Scour at Inlets» | pág. impresa **5.9** · PDF 145 | definicion | 2026-11-12 · texto |
| `HDS5_3ED.5.3.2#APRON` | 5.3.2 | «5.3.2  Scour at Outlets» | pág. impresa **5.11** · PDF 147 | definicion | 2026-11-12 · texto |
| `HDS5_3ED.5.3.2#PRACTICA` | 5.3.2 | «5.3.2  Scour at Outlets» | pág. impresa **5.11** · PDF 147 | definicion | 2026-11-12 · texto |
| `HDS5_3ED.5.3.3#ALINEADO` | 5.3.3 | «Sedimentation» | pág. impresa **5.11** · PDF 147 | definicion | 2026-08-30 · texto |
| `HDS5_3ED.5.3.3#DEPRESION` | 5.3.3 | «Sedimentation» | pág. impresa **5.12** · PDF 148 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.5.3.3#INDICADORES` | 5.3.3 | «Sedimentation» | pág. impresa **5.11** · PDF 147 | definicion | 2026-08-30 · texto |
| `HDS5_3ED.5.4.1#ESVIAJE` | 5.4.1 | «Skewed Barrels» | pág. impresa **5.12** · PDF 148 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.5.4.2#EVITAR` | 5.4.2 | «Skewed Inlets» | pág. impresa **5.14** · PDF 150 | recomendacion | 2026-11-13 · texto |
| `HDS5_3ED.5.4.2#MAXIMO_PRACTICO` | 5.4.2 | «Skewed Inlets» | pág. impresa **5.13** · PDF 149 | recomendacion | 2026-11-11 · texto |
| `HDS5_3ED.5.4.2#PARALELO` | 5.4.2 | «Skewed Inlets» | pág. impresa **5.13** · PDF 149 | definicion | 2026-11-13 · texto |
| `HDS5_3ED.5.4.3#REPARTO` | 5.4.3 | «Multiple Barrels» | pág. impresa **5.15** · PDF 151 | aproximacion | 2026-09-20 · texto |
| `HDS5_3ED.5.4.4#PENDIENTE_10` | 5.4.4 | «Barrels on Steep Slopes» | pág. impresa **5.16** · PDF 152 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.5.4.4#PENDIENTE_20` | 5.4.4 | «Barrels on Steep Slopes» | pág. impresa **5.16** · PDF 152 | recomendacion | 2026-11-11 · texto |
| `HDS5_3ED.A.2` | A.2, A.2.1 | «INLET CONTROL EQUATIONS» | pág. impresa **A.2** · PDF 191 | definicion | 2026-08-28 · texto |
| `HDS5_3ED.A.2.1#FORMA_1` | A.2.1 | «Unsubmerged Inlet Control Equations» | pág. impresa **A.1** · PDF 190 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.A.2.1#KS` | A.2.1 | «Unsubmerged Inlet Control Equations» | pág. impresa **A.2** · PDF 191 | definicion | 2026-08-28 · texto |
| `HDS5_3ED.A.2.1#QLIM` | A.2.1 | «Unsubmerged Inlet Control Equations» | pág. impresa **A.1** · PDF 190 | aproximacion | 2026-08-28 · texto |
| `HDS5_3ED.A.2.2#QLIM` | A.2.2 | «Submerged Inlet Control Equations» | pág. impresa **A.2** · PDF 191 | aproximacion | 2026-08-28 · texto |
| `HDS5_3ED.A.3#FORMAS` | A.3 | «A.3  INLET CONTROL DIMENSIONLESS DESIGN CURVES» | pág. impresa **A.2** · PDF 191 | exigencia | 2026-09-07 · texto |
| `HDS5_3ED.A.3#PENDIENTE_2` | A.3 | «A.3  INLET CONTROL DIMENSIONLESS DESIGN CURVES» | pág. impresa **A.2** · PDF 191 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.A.3.1#CRITICO` | A.3.1 | «Elliptical Structural Plate Example» | pág. impresa **A.3** · PDF 192 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.B.3#CAJON_IN_SITU` | B.3 | «CONCRETE BOX CULVERT» | pág. impresa **B.2** · PDF 204 | definicion | 2026-11-12 · ambos |
| `HDS5_3ED.SIMBOLOS#THETA_W` | List of Symbols, ΘW | «LIST OF SYMBOLS (Cont.)» | pág. impresa **xix** · PDF 23 | definicion | 2026-11-13 · texto |
| `HDS5_3ED.TA.1` | Table A.1 | «Constants for Inlet Control Equations for Charts in Appendix G.» | pág. impresa **A.8** · PDF 197 | definicion | 2026-08-28 · ambos |
| `HDS5_3ED.TB.1` | Table B.1 | «Manning's n Values for Culverts.» | pág. impresa **B.6** · PDF 208 | definicion | 2026-11-11 · texto |
| `HDS5_3ED.TC.2` | Table C.2 | «Entrance Loss Coefficients.» | pág. impresa **C.6** · PDF 216 | definicion | 2026-08-28 · ambos |

> **`HDS5_3ED.1.2#MODELO`** — «A reasonable guideline»: RECOMENDACION, no definicion. Distingue dos cosas que DIS-LUZ-DENOMINACION separa: la clasificacion administrativa del cruce (ancho total, NBIS, pag. 1.3) y el metodo hidraulico (luz de UN barril). Este proyecto aplica el umbral de 6.0 m del Manual de Hidrologia a la denominacion --alcantarilla o puente-- y por eso lee el ancho total.

> **`HDS5_3ED.1.2#NBIS`** — La unica fuente de normas/ que dice que ancho cuenta en un cruce de VARIOS barriles: el TOTAL («the total width of a multiple barrel crossing»), para la clasificacion como puente (NBIS). Es la parte que sostiene la lectura de `luz_m` como abertura total del cruce (DIS-LUZ-DENOMINACION). El parrafo siguiente, en la pag. 1.4, matiza que para el METODO HIDRAULICO la guia razonable es modelar como puente «a single culvert with a span of 20 ft (6.1 m) or more» (HDS5_3ED.1.2#MODELO).

> **`HDS5_3ED.2.2.4#LONGITUD`** — Inciso «b. Culvert Length» del num. 2.2.4, que abre en la pag. impresa 2.7 (PDF 69). Las dos oraciones anteriores dicen COMO se obtiene: «The dimensions are obtained by superimposing the estimated culvert barrel on the roadway cross section and the streambed profile (Figure 2.4). This superposition establishes the inlet and outlet invert elevations». La Figura 2.4 (misma pagina, leida por imagen) dibuja la seccion A-A SOBRE EL EJE ESVIADO del conducto, con tres cotas rotuladas en la corona -- «Pavement Elevation» en el borde izquierdo, «Centerline Elevation» en el eje y «Shoulder Elevation» en el borde derecho --, el talud «Se : 1» y un «Upstream Invert» mas alto que el «Downstream Invert»: un talud a cada lado y dos fondos a cotas distintas, no dos taludes iguales medidos en el eje. LOS TALUDES DE LA FIGURA MUEREN EN LA CARA SUPERIOR DEL BARRIL, no en su fondo. La cita sostiene la superposicion APROXIMADA del barril estimado y nada mas: que el proyecto baje cada talud hasta el fondo -- un barril de altura cero, porque la seccion no se conoce todavia -- es eleccion suya, declarada en el criterio 'metodo_longitud_conducto', y da la cota superior de la longitud. El inciso «a. Cross Section» de la misma pagina añade que la seccion que el proyectista necesita es la del cruce, «skewed with reference to the roadway centerline».

> **`HDS5_3ED.2.2.5#EMBALSE`** — La fuente identifica la carga a la entrada con la PROFUNDIDAD DEL EMBALSE aguas arriba («headwater, or ponding depth»). Es lo unico que esta cita sostiene: que el HW de M4 es el nivel del embalse en la boca. NO da un metodo para la extension del embalse aguas arriba ni nombra el derecho de via: el plano horizontal a la cota del HW cortando el fondo del cauce es el metodo [A] del proyecto ('remanso_derecho_via' = «embalse_a_nivel»), y el paso de V5 lo dice con sus supuestos.

> **`HDS5_3ED.2.2.5#NO_EXCEDER`** — La comparacion que la fuente plantea es de NIVELES: la carga de diseño contra la admisible. Es la forma del metodo «cota_de_afectacion» de V5 (correcciones de T-7b, H2): la cota del embalse de diseño contra una cota admisible aguas arriba, sin ninguna longitud.

> **`HDS5_3ED.2.2.5a#COTA_CRITICA`** — Del inciso a. «Economic Considerations»: las restricciones del sitio suelen fijar «some designated elevation that is not to be exceeded within a specified return period», y esta frase dice a que puede corresponder: el hombro de la plataforma o la cota de desborde de la via. La oracion siguiente da la otra: «Another criteria might be the flood damage elevation of an upstream building or another upstream road crossing». Es lo que sostiene que V8 compare el nivel del evento extremo con el borde de la plataforma; no fija el periodo de retorno ni dice que desbordar sea colapsar.

> **`HDS5_3ED.2.2.5a#COTA_DE_DANO`** — Del inciso a. «Economic Considerations»: la cota admisible puede ser la de daño de una edificacion o de otro cruce aguas arriba. Es lo que sostiene el metodo «cota_de_afectacion» de V5: la cota del embalse de diseño (solera de entrada + HW de M4) contra la cota del terreno o del bien a proteger en el limite del derecho de via aguas arriba, dato externo por punto (`cota_afectacion_aguas_arriba_msnm`, de la topografia). La fuente no fija el periodo de retorno ni nombra el derecho de via: la eleccion de ESA cota como la admisible es del proyecto ('remanso_derecho_via' [A]). El inciso b. trae otro criterio de nivel, el AUMENTO admisible de la superficie del agua (de 0 a 1 ft en la llanura de inundacion de la FEMA), que exige el perfil del cauce sin la obra y no esta implementado.

> **`HDS5_3ED.3.1.3#CRITICO_EN_LA_ENTRADA`** — Lo dice de las Figuras 3.1A y 3.1C, el Tipo 1 del USGS, con la entrada NO sumergida. Sostiene la velocidad que el proyecto lee en la boca cuando gobierna el control de entrada: la critica. Con la entrada sumergida (Figuras 3.1B y 3.1D) la boca trabaja como orificio y la fuente no da la velocidad en ella.

> **`HDS5_3ED.3.1.3#SUMERGENCIA`** — El parrafo sigue con la Fig. 3.1D: «submergence of both the inlet and the outlet ends of the culvert does not assure full flow». Sostiene que LLENO, en `modelos.RegimenBarril`, describe la salida y el tramo aguas abajo del resalto, no la longitud entera.

> **`HDS5_3ED.3.1.3#TRANSICION`** — NOR-HDS-06, cerrado: ESTE es el numeral de la zona de transicion, no el «Cap. IV» que el criterio citaba. El Capitulo 4 de la 3a ed. se titula «CULVERT DESIGN FOR AQUATIC ORGANISM PASSAGE (AOP)» -- paso de fauna acuatica -- y tampoco se salva leyendolo como la edicion de 1985, cuyo Capitulo 4 es «Tapered Inlets». Es el mismo patron que NOR-PUE-01: el numeral existe y su titulo no corresponde. La otra mitad de la cita vieja, «y Apendice A», SI era correcta: la misma regla esta en el num. A.2.

> **`HDS5_3ED.3.1.4#0_75D`** — Las dos frases anteriores de la misma pagina dicen cuando el metodo aproximado «works best» (barril lleno al menos en parte) y que «becomes increasingly inaccurate as the headwater falls further below the top of the barrel». Esta es la que CUANTIFICA: hasta 0.75D los resultados son adecuados aun con el barril parcialmente lleno en toda su longitud, y por debajo el remanso es obligatorio («are required»). Es lo que sostiene que bajo HW/D < 0.75 `ResultadoHidraulico.HW_salida` sea el HW del remanso y no el de la aproximacion, y que por encima la aproximacion siga gobernando con el remanso impreso como comprobacion (v8 §4.3). Conviene leerla junto a la pag. 3.24: alli la vineta dice «can only be used if the barrel flows full for most of its length», una condicion MAS estricta que esta; el proyecto mide aquella (paso 4.3c) y aplica esta, y lo declara como discrepancia interna de la fuente en `constantes_normativas.H_O_CONDICION_APLICACION`.

> **`HDS5_3ED.3.1.4#EMPALME`** — La Ec. 3.7 sigue a esta frase: Sf = Hf/L = Ku·n²·V²/(R^1.33·2g), con Ku = 29 (19.63 en SI, la misma `K_FRICCION_SI` de la Sec. 4.3). El proyecto la escribe con R^(4/3), como `perdida_carga`, y la usa en los dos sentidos: la linea llena que arranca en un TW sobre la clave y BAJA de ella aguas arriba cuando Sf < S (el caso del corredor de referencia, B-01 ampliada), y la que arranca donde la M2 corta la clave (Fig. 3.7B).

> **`HDS5_3ED.3.1.4#HW_REMANSO`** — Es la forma del HW por remanso: HW = y_entrada + (1 + ke)·V_entrada²/2g, con las velocidades de aproximacion y de salida nulas (num. 3.3.3, «assumed to be zero for the manual method»). Con la linea llena de punta a punta reproduce exactamente HW = H + h_o - S·L de `control_salida` con h_o = TW.

> **`HDS5_3ED.3.1.4#K`** — El 19.63 ESTA en la fuente, no es derivacion. El numeral abre en la pag. impresa 3.5 y la ecuacion esta en la 3.10.

> **`HDS5_3ED.3.1.4#LONGITUD`** — Lista «Factors Influencing Outlet Control», que empieza en la pag. impresa 3.8 (PDF 90); el numeral abre en la 3.5 (PDF 87). La oracion anterior define la magnitud: «Barrel length is the total culvert length from the entrance to the exit of the culvert». Es la razon, escrita por la fuente, de que la longitud del diseño hidraulico se calcule ANTES de conocer la seccion y por eso sin su altura: la altura del barril y la pendiente mueven la longitud real, y el diseño arranca con una aproximacion.

> **`HDS5_3ED.3.1.4#REMANSO`** — Es el procedimiento en prosa (pieza 1 del paquete I1): la frontera aguas abajo max(y_c, TW) y la marcha hacia la entrada. La frase anterior dice para que casos: «Backwater calculations may be required for the partly full flow conditions shown in Figures 3.7A and C».

> **`HDS5_3ED.3.1.6#V_SALIDA`** — La oracion sigue con «(Figure 3.14).» y la lista de tres vinetas que reparte los casos por el TW: tirante critico si TW < y_c, TW si y_c < TW < D, seccion entera si TW > D. `M4.velocidad_de_salida` lo escribe como el area al tirante min(D, max(TW, y_c)).

> **`HDS5_3ED.3.1.6#V_SALIDA_TW`** — Tercera vineta de la lista. Es la que sostiene el regimen LLENO de `modelos.RegimenBarril`: con TW sobre la clave la seccion efectiva es la entera, y V2 compara Q/A_llena.

> **`HDS5_3ED.3.3.2#V_SALIDA_ENTRADA`** — Es el ultimo parrafo del num. 3.3.2, en la misma pagina en que arranca el 3.3.3. El 3.1.6 dice lo mismo con mas matiz en la pag. 3.18 («the velocity calculated in this manner may be slightly higher than the actual velocity at the outlet»): por eso el caracter es APROXIMACION. De las dos ramas de n el proyecto toma la de n_min, el techo, para el d50 de la Fase 6.

> **`HDS5_3ED.3.3.3#HO`** — Las TRES condiciones estan en esta pagina, y la primera tiene una SEGUNDA MITAD que el expediente no recogia: «It should not be used if the inlet is not submerged». Son dos condiciones, no una. Ademas la fuente no escribe la razon HW/D: escribe «the headwater depth (referenced to the inlet invert) is less than 1.2D», y la referencia al invert de entrada es parte de la definicion. Las tres son `should` / `can only`, no `shall`. C4: EL VERBATIM ESTABA TRUNCADO EN «flows full for», que es donde el PDF parte la linea, y la truncadura se llevaba «most of its length» -- o sea LA CONDICION MISMA --. Leido asi, el rotulo «texto literal» publicaba un requisito MAS LAXO que el de la fuente: «que el barril fluya lleno» en vez de «que fluya lleno en la mayor parte de su longitud». Es la elision sin marcar que CLAUDE.md persigue, y `test_normativa_pdf` no la veia porque verifica por subcadena y una truncadura siempre lo es. Verificado contra la PDF 106: la oracion termina en «most of its length.»

> **`HDS5_3ED.3.3.3#HO_1_2D`** — De aqui salen los DOS limites que `M4` evalua punto por punto: 1.2D (cautela) y 0.75D (no usar). La transcripcion anterior del expediente se saltaba, sin marcarlo, la oracion sobre las backwater calculations -- que es justamente la que dice QUE HACER cuando el punto cae en la banda de cautela. Una elision no marcada dentro de algo rotulado «texto literal» es la misma clase de defecto que NOR-HID-06.

> **`HDS5_3ED.3.3.3#HO_SUMERGIDA`** — Segunda mitad de la vineta de h_o, y es una condicion DISTINTA de la primera: aquella acota por llenado del barril, esta por sumergencia de la entrada. El expediente las leia como una sola.

> **`HDS5_3ED.3.3.4#HORIZONTAL`** — Es la frase que admite S = 0 (INF-5.1.6). La leyo T-0 y la dejo sin cita; la transcribe T-2. El parrafo sigue con el caso en que se usa («A horizontal slope is used when flow may occur in either direction») y con una regla practica para la pendiente ADVERSA, que este proyecto NO admite: S < 0 sigue siendo dato invalido.

> **`HDS5_3ED.3.3.4#H_SIN_AJUSTE`** — El control de salida no cambia con S = 0: H es la misma y la caida S·L vale cero, de modo que HW = H + h_o.

> **`HDS5_3ED.3.3.4#KS`** — Dice QUE ES el termino Ks·S: la seccion de control queda dentro del barril, algo mas baja que el fondo de la entrada. De ahi que con S = 0 el termino valga cero, que es lo que la ecuacion (A.1) da sola: la vineta que sigue manda SUMAR 0.01 al HW/D del nomograma en un barril horizontal, y ese 0.01 es 0.5 x 0.02, la correccion que el nomograma lleva restada por haberse trazado al 2 % (`HDS5_3ED.A.3#PENDIENTE_2`). El codigo resuelve la ecuacion, no lee el nomograma, y por eso no suma nada: evalua Ks·S con la S real.

> **`HDS5_3ED.3.3.5#ENCAJE`** — La oracion que sigue dice que se comprueba al encajar: «The culvert barrel must have adequate cover, the length should be close to the approximate length, and the headwalls and wingwalls must be dimensioned». La cobertura es G1 (7.A); la longitud «close to the approximate length» es el paso 7.B.5 de este proyecto, que la fuente escribe con «should» y SIN TOLERANCIA: no hay cifra de cuanto es «close», y el proyecto no la inventa -- imprime las dos longitudes y su diferencia.

> **`HDS5_3ED.3.3.5#GOBIERNA`** — Es el paso del PROCEDIMIENTO DE DISEÑO del Capitulo 3 («Culvert Hydraulic Design», num. 3.3 «Culvert Design Using Nomographs») que dice cual control gobierna. La oracion anterior fija el sujeto: «For the first alternative selected, compare the headwater elevations calculated for inlet and outlet control». Dos cosas que la frase dice y que el paso que la cita respeta: compara COTAS de carga (headwater elevations), que con los dos controles referidos al mismo fondo de entrada es comparar los dos HW; y «is designated» es una definicion del metodo, no una exigencia sobre el diseño. La oracion siguiente da la razon fisica: «The culvert can be expected to operate with that higher headwater for at least part of the time». Lo que el paso 4.4 hace ADEMAS --tomar como HW de salida el del remanso cuando la aproximacion de h_o esta fuera de rango-- no sale de aqui sino de la pag. 3.12 (`HDS5_3ED.3.1.4#0_75D`), que el paso cita aparte. Hasta T-0 el paso citaba `HDS5_3ED.A.2`, las ecuaciones de control de entrada (INF-5.1.10).

> **`HDS5_3ED.3.5#PERFIL`** — La frase esta en el parrafo introductorio de la Seccion 3.5 que abre la pag. 3.36, justo ANTES del encabezado 3.5.1 (el encabezado 3.5 esta en la pag. 3.34, PDF 116), y es la que nombra las TRES salidas del perfil que E-A implementa: el tirante (V1), la velocidad (V2) y la longitud de barril lleno (la primera condicion de h_o). El parrafo sigue: «The profile is determined by first establishing if the culvert slope is supercritical (inlet control) or subcritical (outlet control). Next, the tailwater is used to establish which profile to assume and at what depth to start the profile».

> **`HDS5_3ED.3.5.1#H2`** — La fuente NOMBRA los perfiles de pendiente horizontal (H2 y H3) como parte de los que HY-8 calcula desde la version 7.3, y no los desarrolla. El rotulo `TipoDePerfil.H2` es de aqui; el procedimiento con que el proyecto lo integra es el mismo paso directo de la pag. 3.12, con S = 0.

> **`HDS5_3ED.3.5.1#S1`** — Parrafo «USGS Flow Type 1 (Inlet Control)». Es lo que sostiene `PerfilLamina.alcanza_entrada`: en pendiente pronunciada la S1 que arranca en el TW (o en y_c, con longitud cero) solo gobierna el HW si llega a la cara de entrada; si corta y_c antes, el control es de entrada y aguas arriba del resalto el flujo es supercritico. La fuente sigue con la localizacion del resalto por la profundidad secuente (JFt, JFf) y, en HY-8 7.3, por momentum: el proyecto NO situa el resalto --le basta saber que la S1 no llega-- y lo deja escrito en decisiones_diferidas.md.

> **`HDS5_3ED.3.5.1#TIPO7`** — Parrafo «USGS Flow Type 7 (Outlet Control)»; el de los tipos 4 y 6, en la misma pagina, dice lo mismo para el barril lleno «for most of its length» (FFt/FFc) y que con «tailwater … higher than the culvert crown at the exit … the barrel flows full (FFf)». Es la fuente de que la fraccion llena sea un RESULTADO del perfil y no una lectura, y de los rotulos M1/M2 de `modelos.TipoDePerfil`.

> **`HDS5_3ED.5.3.1#ENTRADA`** — El parrafo anterior describe el mecanismo: al contraerse el flujo hacia el barril, vortices y zonas de alta velocidad atacan los taludes del terraplen junto a la boca, y a menudo se forma una hoya aguas arriba del piso del conducto. La fuente ENUMERA las medidas y no las dimensiona ni dice cual corresponde a que embocadura: la asignacion por tipo de embocadura es lectura del proyecto.

> **`HDS5_3ED.5.3.2#APRON`** — Describe una practica y remite a HEC-14 Sec. 10.2. El parrafo termina: «Providing scour protection for large floods or when more serious erosion problems exist requires protection measures designed based on HEC-14». En la pag. impresa 5.9 el mismo numeral dice que los metodos para estimar la hoya de socavacion local estan en HEC-14.

> **`HDS5_3ED.5.3.2#PRACTICA`** — La frase que sigue a la de HDS5_3ED.5.3.2#APRON. Describe una practica: el apron se pone salvo que el campo diga que no hace falta. Es lo que sostiene que el programa no concluya «sin enrocado» cuando la velocidad no supera la Tabla Nº 11: la proteccion se mantiene y el aviso cita esta frase.

> **`HDS5_3ED.5.3.3#ALINEADO`** — Es la contracara del indicador y la que explica por que la verificacion pasa en la inmensa mayoria de los puntos de este corredor: Sec. 7.B fija que la alcantarilla sigue la pendiente del cauce, de modo que S_conducto = S_cauce salvo que el punto declare `S_conducto` aparte. El «generally» es de la fuente y se conserva: no dice «nunca».

> **`HDS5_3ED.5.3.3#DEPRESION`** — Es el final del num. 5.3.3, ya en la pag. impresa 5.12, y lo que la fuente dice del caso que el primer indicador describe: el conducto mas plano que su cauce sedimenta SOBRE TODO con caudales bajos y SUELE limpiarse solo con los altos. La oracion siguiente pide abordar ese diseño con cautela y con mas investigacion de campo; no lo prohibe. Sostiene que el indicador se aplique como aviso (`regimen_v2b`). EL NUMERAL ENTERO, leido en T-2 (INF-3.2.9): ademas de los dos indicadores --pendiente y rugosidad-- nombra como factores la magnitud del caudal y el material del cauce, los cauces en agradacion, los cambios de pendiente a la entrada, las instalaciones multibarril y las entradas deprimidas. Ninguno lleva cifra.

> **`HDS5_3ED.5.3.3#INDICADORES`** — LOS DOS INDICADORES SON COMPARACIONES, NO UMBRALES. La fuente no escribe ninguna cifra: nombra dos desigualdades entre el conducto y el cauce natural. La primera -- S_conducto < S_cauce -- este software la puede evaluar con dos columnas que ya tiene. La segunda -- n_conducto > n_cauce -- necesita el n del CAUCE NATURAL, que no es columna de Sec. 1.2 y por eso queda declarada, no adivinada.

> **`HDS5_3ED.5.4.1#ESVIAJE`** — Es la convencion de `esviaje_grados`: 0 = perpendicular («A culvert aligned normal to the roadway centerline has a zero barrel skew angle», oracion anterior). El mismo numeral nombra la consecuencia geometrica que 1/cos(esviaje) cuantifica: tender el barril sobre el cauce tiene la desventaja de que «the inlet may be skewed with respect to the culvert barrel and the culvert will be longer».

> **`HDS5_3ED.5.4.2#EVITAR`** — Sigue: «Both tapered inlets and multiple barrel culverts perform better with the inlet face oriented normal to the barrel», y cierra con lo que el cabezal normal al eje exige del terraplen: «The embankment fill should be warped to fit the culvert when avoiding inlet skew (Figure 5.16)». Es la consecuencia constructiva de la orientacion adoptada: con esviaje, el talud se alabea para encontrar un muro normal al barril (el aviso de Δz de `M9.cabezal_del_punto` es su medida).

> **`HDS5_3ED.5.4.2#MAXIMO_PRACTICO`** — HABLA DEL ESVIAJE DE LA EMBOCADURA («inlet skew angle», el angulo de la cara del conducto con la normal al barril), NO del esviaje del barril. La oracion siguiente da la razon -- «The upper limit is dictated by the difficulty in transitioning the flow from the stream into the culvert» -- y el parrafo siguiente el puente entre los dos angulos: «Culverts which have a barrel skew angle often have an inlet skew angle as well. This is because headwalls are generally constructed parallel to a roadway centerline to avoid warping of the embankment fill». Con el cabezal PARALELO a la via, que es la disposicion que este proyecto supone (terraplen sin alabear), el esviaje de la embocadura es igual al del barril y el maximo practico de 45 grados le alcanza; con el terraplen alabeado para dejar la embocadura normal al barril (Figura 5.16) no le alcanza. Por eso 'esviaje_max_grados' es [A] y no [C]: la analogia depende de una disposicion constructiva que el expediente decide.

> **`HDS5_3ED.5.4.2#PARALELO`** — DESCRIBE la practica («generally»): con el barril esviado, el cabezal se suele construir PARALELO al eje de la via para no alabear el terraplen, y entonces la embocadura queda esviada respecto del barril. El parrafo siguiente mide el efecto: «Skewed inlets slightly reduce the hydraulic performance of the culvert under inlet control conditions. The differences are minor and are incorporated into the inlet control nomographs for box culverts (Charts 11 and 12)». El proyecto adopta lo CONTRARIO por decision del dueño (2026-11-13): cabezal NORMAL al eje del conducto en las tres familias, que es lo que suponen el ke y las cartas con que se dimensiona; el paralelo a la via queda diferido solo para el marco (ficha T7A-03).

> **`HDS5_3ED.5.4.3#REPARTO`** — Es el sosten de la regla vinculante #3 (Q/N por barril) que hasta EXT-2 no estaba en el registro. La fuente lo escribe como un SUPUESTO («is assumed») condicionado a barriles hidraulicamente identicos -- misma seccion, misma cota de fondo, misma embocadura --, que es exactamente lo que `SeccionRectangular` modela: UNA celda repetida N veces. Para barriles distintos o con cotas distintas la misma pagina remite a un procedimiento iterativo o a una curva de funcionamiento combinada (Section 3.5), que el proyecto NO implementa: el criterio 'n_celdas_cajon' declara N celdas iguales y nada mas.

> **`HDS5_3ED.5.4.4#PENDIENTE_10`** — DESCRIBE una practica, no fija un limite: bajo el 10 % no hacen falta medidas estructurales especiales. Es el unico numero sobre pendiente maxima que trae una fuente de `normas/`, y por eso es el valor que `pendiente_maxima_conducto` adopta como [A]. Entre 10 % y 20 % la misma pagina pide atar las ultimas secciones del tubo; por encima del 20 %, `HDS5_3ED.5.4.4#PENDIENTE_20`.

> **`HDS5_3ED.5.4.4#PENDIENTE_20`** — La cautela hidraulica del USBR que nombra esta en la misma pagina: no dejar que el barril fluya lleno en caidas grandes. Este programa no dimensiona anclajes ni ataduras de tubo: por eso la ventana de `pendiente_maxima_conducto` termina en 0.10.

> **`HDS5_3ED.A.2`** — NOR-HDS-03, confirmado: `Ku` y `Ks` estan en la LISTA DE VARIABLES de las ecuaciones del num. A.2.1, pag. impresa A.2, y NO en la Tabla A.1. La Tabla A.1 tiene nueve columnas y de constantes de la ecuacion solo cuatro -- K, M, c e Y --: no hay columna K_u ni columna K_s.

> **`HDS5_3ED.A.2.1#FORMA_1`** — LA BASE DE LA FORMA 1 ES H_c, y los demas terminos --K(q*)^M y Ks·S-- son «correction factors». Es lo que sostiene el piso «energia_critica» de `hw_entrada_fuera_de_rango`: cuando la correccion por pendiente, extrapolada, anula la carga, el proyecto se queda con la base de la que la ecuacion parte. LA FUENTE NO PRESCRIBE ESE PISO --no dice que hacer cuando HWi/D sale nulo o negativo--: por eso el criterio sigue siendo [A], con «descartar» como alternativa, y no [C].

> **`HDS5_3ED.A.2.1#QLIM`** — «apply up to ABOUT»: la fuente NO fija un umbral duro. Y los 3.5 son del sistema INGLES; su equivalente SI, entre parentesis, es 1.93. Como `caudal_adimensional` multiplica por KU_SI = 1.811, el q* que M4 compara ya esta en la escala inglesa y le corresponden 3.5 y 4.0: cambiarlos por los del parentesis seria aplicar dos veces la conversion.

> **`HDS5_3ED.A.3#PENDIENTE_2`** — Dos cosas en una frase: que la correccion por pendiente es CHICA («the slope effect is small»), y que fijarla en el 2 % deja la carga del lado conservador en pendientes mayores. Es el extremo inferior de la ventana de `pendiente_maxima_conducto` (0.02: la pendiente con que la fuente traza sus curvas) y el argumento con que el proyecto lee el termino Ks·S como una correccion menor que no puede anular la carga.

> **`HDS5_3ED.A.3.1#CRITICO`** — ES LA CONDICION DE FLUJO CRITICO ESCRITA POR LA FUENTE, y no con los simbolos del paso que la cita. La pagina la escribe como V_c^2/(2g) = y_h/2 con y_h = A_p/T_p el tirante hidraulico, y dos renglones despues como numero de Froude: «Since the Froude number equals 1.0 at critical depth, Vc can be determined from the Froude number equation», con Qc = Ap (g yh)^0.5. Sustituyendo V = Q/A y y_h = A/T, las dos son Q^2/g = A^3/T, que es la forma en que `M4._residuo_critico` la resuelve: la igualdad es algebra de una linea y la hace el proyecto, no la fuente. Esta en un EJEMPLO del Apendice A (el desarrollo de la curva adimensional de una seccion eliptica), no en un numeral de definiciones: el HDS-5 no dedica ningun apartado a definir el tirante critico --lo lee de las cartas del Apendice C (num. 3.3.3)--, y esta es la unica pagina del ejemplar que escribe la condicion con la que se calcula. La misma pagina define H_c/D = d_c/D + y_h/(2D), ec. (A.4), que es el H_c de la Forma 1.

> **`HDS5_3ED.B.3#CAJON_IN_SITU`** — La pagina imprime «0.022  see concrete lined open channels  from» con DOS espacios a cada lado y sin parentesis (comprobado renderizada); el texto va como la capa de texto lo entrega, con los espacios normalizados. DESCRIBE el rango del cajon VACIADO IN SITU y lo liga a la calidad del ENCOFRADO, no a un acabado: es la ventana HACIA ARRIBA del n de capacidad del criterio 'n_manning_cajon' [C], cuyo valor de archivo es la fila «Concrete Boxes / Smooth» de la Tabla B.1 (0.012-0.015, pag. impresa B.6). Remite a la Tabla 1 del HDS 3 (FHWA 1961), que no esta en normas/.

> **`HDS5_3ED.SIMBOLOS#THETA_W`** — La definicion completa es «ΘW Flare angle of wingwalls with respect to extension of culvert side wall, degrees». Fija la CONVENCION del angulo de los aleros: se mide con la PROLONGACION DE LA PARED DEL BARRIL, de modo que 0 grados son aleros paralelos al barril y 90 grados aleros en el plano del muro. Es la misma que imprimen los rotulos de la Tabla C.2 («to barrel») y la que hace que la longitud de un alero lleve el COSENO del angulo que forma con la bajada del talud, no el seno. La geometria de la longitud es del proyecto: esta cita solo fija desde donde se mide el angulo.

> **`HDS5_3ED.TA.1`** — ERRATA DE LA PROPIA FUENTE, hallada al verificar: el titulo dice «for Charts in Appendix G» y en esta 3a edicion NO EXISTE un Apendice G -- las cartas estan en el Apendice C. Se transcribe como lo imprime, con la advertencia, para que quien lo busque lo encuentre. SEGUNDA REMISION RANCIA DE LA MISMA FUENTE, hallada en C2 y sin ID propio todavia: el num. A.3.1 (pag. impresa A.2, PDF 191) dice «From Table A.1, Chart 34, Scale 3», y la carta 34 -- Pipe Arch CM -- esta en la Tabla A.2 de esta edicion, no en la A.1. Explica por que el repositorio llego a afirmar que la Tabla A.1 trae pipe-arch, que no lo trae. Y LA PAGINA IMPRESA «A.8» ES INFERIDA, NO LEIDA: PDF 197 no lleva folio. La inferencia por secuencia es correcta (PDF 196 lleva A.7) y la regla de paginacion la predice; queda dicho aqui porque «pagina impresa» nombra algo que en esta pagina no esta impreso. VERIFICADO EN I3 (verificador-normativo, metodo texto extraido con coordenadas + render de la pagina entera, los cuatro bordes): PDF 197 no imprime folio en ningun borde -- la pagina esta almacenada apaisada de forma nativa (792x612, rotation=0), asi que el barrido de texto no pierde nada --; los folios vecinos leidos son A.5@194, A.6@195, A.7@196 y B.1@203; entre A.7 y B.1 van SEIS paginas sin folio y no «cuatro apaisadas», como decia esta nota hasta I3: las cinco del Apendice A -- tres apaisadas de tablas (197-199), la VERTICAL de las Tablas A.4-A.6 (200) y la en blanco (201) -- mas la portadilla del Apendice B (202), que por regla del documento nunca folia. La cadena «A.8» no aparece en ninguna pagina del PDF, y ningun esquema consistente con los folios impresos puede asignar a PDF 197 otro numero: la unica lectura alternativa no es otro folio, es «sin folio». Veredicto: CORRECTO-INFERIDO; `pagina_impresa` se queda en «A.8» -- es el valor que la regla de paginacion de T6 predice -- y esta nota es la que dice que no es una lectura.

> **`HDS5_3ED.TB.1`** — LA PAGINA ROTULA «B.1.  Manning's n Values for Culverts.» SIN LA PALABRA «Table»; el numeral «Table B.1» es como el propio HDS-5 la llama en el cuerpo. El `texto_literal` es su nota al pie 1, y va a proposito: los n son de LABORATORIO y la fuente advierte que los de campo pueden variar por abrasion, corrosion, deflexion y juntas. La fila «Corrugated Polyethylene / Smooth», 0.009-0.015 (Barfuss & Tullis 1988; Tullis et al. 1990), es la que cierra 'n_manning_hdpe' como [C]: hasta T-4 era la fila del concreto de la Tabla N 09 aplicada por analogia. Y desde la auditoria de T-3 (H1), la fila «Concrete Boxes / Smooth», 0.012-0.015 (FHWA 1961), cierra 'n_manning_cajon' como [C] por la misma razon: la Tabla N 09 no tiene fila de seccion rectangular.

> **`HDS5_3ED.TC.2`** — NOR-HDS-01, confirmado contra el PDF. La cita original decia «pagina C.2», que es EL NUMERO DE LA TABLA LEIDO COMO PAGINA: la pag. impresa C.2 (PDF 212) es la continuacion del indice de cartas del apendice. La tabla esta en la C.6 (PDF 216).

### HDS-5 «Hydraulic Design of Highway Culverts» (FHWA-IP-85-15), copia rotulada «SI» por sus cartas metricas  (`HDS5_SI_1985`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `HDS5_SI_1985.EC4B#K` | ecs. (4b) y (5) | «Hydraulics of Outlet Control» | pág. impresa **s/n** · PDF 54 | definicion | **NO verificada** |

> **`HDS5_SI_1985.EC4B#K`** — SIN FIRMA A PROPOSITO, no sin verificar: la paginacion de la fuente es `SinDeterminar` (la copia no imprime folios; `pagina_impresa` dice «s/n» por eso) y el invariante T6 impide firmar una pagina PDF de una fuente sin paginacion medida. El contenido esta verificado de hecho (trazabilidad/T2 · verificador-normativo, 2026-09-12, metodo AMBOS): POR IMAGEN, la ec. rotulada (4b) imprime Hf = [29 n² L / R^1.33]·V²/2g y la (5) H = [1 + ke + 29 n² L / R^1.33]·V²/2g -- constante 29, no 19.63; las ecuaciones son imagenes incrustadas y no salen en la capa de texto --. POR TEXTO, las definiciones llevan rotulo dual «ft (m)» (el Verbatim es una de ellas) y «19.63» da cero paginas en las 410 del documento. Es el ancla de DIS-HDS5-EDICIONES: leer el 29 «en SI» multiplica el termino de friccion por 29/19.63 = 1.477 (+47.7 % sobre el TERMINO), que en CP-8 sube H de 0.4977 a 0.5455 m (+9.6 % sobre H); es lo que K_FRICCION_SI existe para atrapar. Las dos bases se dicen juntas porque el repositorio las mezclo (EXT-G-03).

### HEC-14 «Hydraulic Design of Energy Dissipators for Culverts and Channels» (Hydraulic Engineering Circular No. 14, FHWA-NHI-06-086)  (`HEC14`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `HEC14.1#T1_1_APRON` | 1, Table 1.1, nota 8 | «CHAPTER 1: ENERGY DISSIPATOR DESIGN» | pág. impresa **1-2** · PDF 15 | aproximacion | 2026-11-12 · texto |
| `HEC14.10.1#DOS_D50` | 10.1 | «10.1 RIPRAP BASIN» | pág. impresa **10-1** · PDF 202 | recomendacion | 2026-11-12 · texto |
| `HEC14.10.1#HS` | 10.1 | «10.1 RIPRAP BASIN» | pág. impresa **10-1** · PDF 202 | definicion | 2026-11-12 · ambos |
| `HEC14.10.1.1#YE` | 10.1.1 | «10.1.1 Design Development» | pág. impresa **10-2** · PDF 203 | definicion | 2026-11-12 · texto |
| `HEC14.10.2#ANCHO` | 10.2 | «10.2 RIPRAP APRON» | pág. impresa **10-18** · PDF 219 | permiso | 2026-11-12 · texto |
| `HEC14.10.2#EC_10_4` | 10.2, Ec. (10.4) | «10.2 RIPRAP APRON» | pág. impresa **10-17** · PDF 218 | recomendacion | 2026-11-12 · ambos |
| `HEC14.10.2#EC_10_5` | 10.2, Ec. (10.5) | «10.2 RIPRAP APRON» | pág. impresa **10-17** · PDF 218 | definicion | 2026-11-12 · ambos |
| `HEC14.10.2#FILTRO` | 10.2 | «10.2 RIPRAP APRON» | pág. impresa **10-18** · PDF 219 | recomendacion | 2026-11-12 · texto |
| `HEC14.10.2#PROFUNDIDAD` | 10.2 | «10.2 RIPRAP APRON» | pág. impresa **10-18** · PDF 219 | recomendacion | 2026-11-12 · texto |
| `HEC14.10.2#T10_1` | 10.2, Table 10.1 | «10.2 RIPRAP APRON» | pág. impresa **10-18** · PDF 219 | recomendacion | 2026-11-12 · ambos |
| `HEC14.10.2#TW` | 10.2 | «10.2 RIPRAP APRON» | pág. impresa **10-17** · PDF 218 | aproximacion | 2026-11-12 · texto |
| `HEC14.10.2#TW_ALTO` | 10.2 | «10.2 RIPRAP APRON» | pág. impresa **10-18** · PDF 219 | aproximacion | 2026-11-12 · texto |
| `HEC14.3#CONTINUIDAD` | 3 | «CHAPTER 3: CULVERT OUTLET VELOCITY AND VELOCITY MODIFICATION» | pág. impresa **3-1** · PDF 32 | definicion | 2026-11-12 · texto |
| `HEC14.3.1.3#BORDE` | 3.1.3 | «3.1.3 Unsubmerged Outlets (Brink Depth)» | pág. impresa **3-3** · PDF 34 | definicion | 2026-11-12 · texto |
| `HEC14.5#PEOR_CASO` | 5 | «CHAPTER 5: ESTIMATING SCOUR AT CULVERT OUTLETS» | pág. impresa **5-1** · PDF 54 | definicion | 2026-11-12 · texto |
| `HEC14.5.1#EC_5_1` | 5.1, Ec. (5.1) | «COHESIONLESS SOILS» | pág. impresa **5-1** · PDF 54 | aproximacion | 2026-11-12 · ambos |
| `HEC14.5.1.1#T5_1` | 5.1.1, Table 5.1 | «5.1.1 Scour Hole Geometry» | pág. impresa **5-2** · PDF 55 | definicion | 2026-11-12 · texto |
| `HEC14.5.1.2#DOS_TERCIOS` | 5.1.2 | «5.1.2 Time of Scour» | pág. impresa **5-2** · PDF 55 | definicion | 2026-11-12 · texto |
| `HEC14.5.1.2#NO_BAJO_30` | 5.1.2 | «5.1.2 Time of Scour» | pág. impresa **5-2** · PDF 55 | aproximacion | 2026-11-12 · texto |
| `HEC14.5.1.2#T30` | 5.1.2 | «5.1.2 Time of Scour» | pág. impresa **5-2** · PDF 55 | recomendacion | 2026-11-12 · texto |
| `HEC14.5.1.3#CABEZAL` | 5.1.3 | «5.1.3 Headwalls» | pág. impresa **5-2** · PDF 55 | recomendacion | 2026-11-12 · texto |
| `HEC14.5.1.4#T5_2` | 5.1.4, Table 5.2 | «5.1.4 Drop Height» | pág. impresa **5-3** · PDF 56 | definicion | 2026-11-12 · texto |
| `HEC14.5.1.5#T5_3` | 5.1.5, Table 5.3 | «5.1.5 Slope» | pág. impresa **5-3** · PDF 56 | definicion | 2026-11-12 · texto |
| `HEC14.5.2#EC_5_2` | 5.2, Ec. (5.2) y (5.3) | «COHESIVE SOILS» | pág. impresa **5-6** · PDF 59 | aproximacion | 2026-11-12 · ambos |
| `HEC14.5.2#EC_5_4` | 5.2, Ec. (5.4) | «COHESIVE SOILS» | pág. impresa **5-7** · PDF 60 | definicion | 2026-11-12 · ambos |
| `HEC14.5.2#RANGO_IP` | 5.2 | «COHESIVE SOILS» | pág. impresa **5-7** · PDF 60 | aproximacion | 2026-11-12 · texto |
| `HEC14.D#SOLO_VELOCIDAD` | D | «APPENDIX D: RIPRAP APRON SIZING EQUATIONS» | pág. impresa **D-2** · PDF 281 | recomendacion | 2026-11-12 · texto |

> **`HEC14.1#T1_1_APRON`** — Es la nota 8 de la Table 1.1 «Energy Dissipators and Limitations», y cuelga de la fila «Riprap apron» (Chapter 10), cuya columna de Froude dice «na». La Sec. 10.2 lo dice como poblacion y no como prohibicion: «The most commonly used device for outlet protection, primarily for culverts 1500 mm (60 in) or smaller, is a riprap apron» (pag. impresa 10-16). La tabla se titula «Limitations» y la nota es una de ellas: un conducto mas alto sale como metodo no evaluable. LA FUENTE DA DOS CIFRAS QUE NO COINCIDEN: 60 in son 1.524 m, no 1.500. Rige 1.524 m (`constantes_normativas.HEC14_APRON_ALTURA_MAX_M`), lectura declarada: es la que deja evaluar el ejemplo resuelto de la propia fuente, que usa D = 5.0 ft = 60 in (pag. impresa 10-19). La misma tabla limita la POZA de enrocado (riprap basin) a Fr < 3.

> **`HEC14.10.1#DOS_D50`** — Es de la POZA de enrocado, no del apron; se cita porque fija el mismo piso que la Tabla 10.1 alcanza para las piedras grandes (cita HEC14.10.2#PROFUNDIDAD). La Figura 10.1 de la misma pagina, leida por imagen, mide hs DESDE la solera de salida del conducto hasta el fondo de la poza.

> **`HEC14.10.1#HS`** — Es de la POZA de enrocado (Sec. 10.1), otro metodo que la hoya del Cap. 5. Se cita por lo unico que sostiene: en la poza, hs es la profundidad del piso de enrocado, y la Figura 10.1 de la misma pagina, leida por imagen, la acota DESDE la prolongacion de la solera de salida del conducto hasta ese piso. Es la lectura «solera_de_salida» del criterio 'referencia_profundidad_socavacion'. Hasta la segunda auditoria de T-8 (H9) eso se apoyaba en HEC14.10.1#DOS_D50, cuyo literal habla del espesor del revestimiento y no de la referencia de hs.

> **`HEC14.10.1.1#YE`** — Sigue: «For rectangular culverts, ye = yo (culvert brink depth). For circular culverts, ye = (A/2)^1/2, where A is the brink area». El paso 1 del procedimiento (num. 10.1.5, pag. impresa 10-5) forma con el el numero de Froude de la salida, Fr = Vo / (g·ye)^1/2. Es el Froude que HEC-14 usa para sus disipadores; el apron de la Ec. (10.4) no lo lleva.

> **`HEC14.10.2#ANCHO`** — El ejemplo resuelto de la pag. impresa 10-19 (PDF 220) lo escribe: «Width (at apron end) = 3D + (2/3)L». El 3D es el ancho del apron en la boca de la Figura 10.4 y el (2/3)L el abocinado de 1:3 por cada lado.

> **`HEC14.10.2#EC_10_4`** — La Ec. (10.4), leida de la pagina renderizada: D50 = 0.2·D·[Q / (g^0.5·D^2.5)]^(4/3)·(D / TW), con D50, D y TW en m (ft), Q en m3/s (ft3/s) y g = 9.81 m/s2 (32.2 ft/s2). ES ADIMENSIONAL --el grupo Q/(g^0.5·D^2.5) no tiene unidades--, de modo que el 0.2 vale igual en SI y en unidades inglesas y no hay coeficiente que convertir. El Apendice D (Ec. D.5, pag. impresa D-2) da la misma relacion SIN la gravedad, D50 = 0.020·D·[Q/(α·D^2.5)]^(4/3)·(D/TW) con α = 0.55 (SI) y 1.0 (CU): esa forma SI depende de unidades y no es la que se usa. «RECOMMENDED FOR CIRCULAR CULVERTS»: no cubre el marco. La ecuacion supone una piedra de gravedad especifica 2.65.

> **`HEC14.10.2#EC_10_5`** — La Ec. (10.5), leida de la pagina renderizada: D' = (D + yn)/2, con D' «adjusted culvert rise» e yn «normal (supercritical) depth in the culvert». D' entra en la Ec. (10.4) en lugar de D.

> **`HEC14.10.2#FILTRO`** — HEC 11 no esta en el repositorio de normas: el diseño del filtro no se transcribe. Lo que se cita es que el apron LLEVA filtro.

> **`HEC14.10.2#PROFUNDIDAD`** — El piso del espesor del apron: 2.0·D50. El criterio 'espesor_proteccion_salida' adopta 1.75·d50 (ventana 1.5-2.0) y queda siempre bajo ese piso salvo en el techo de su ventana, que lo iguala: la Fase 6 lo avisa en todo punto que dimensiona.

> **`HEC14.10.2#T10_1`** — ES UN EJEMPLO, y la fuente lo dice dos veces: en el titulo («Example») y en la pag. 10-17 («A project or design standard can be developed such as the example from the Federal Highway Administration Federal Lands Highway Division»). Seis clases: D50 de 125, 150, 250, 350, 500 y 550 mm; longitud del apron 4D, 4D, 5D, 6D, 7D y 8D, con la nota «D is the culvert rise»; profundidad 3.5, 3.3, 2.4, 2.2, 2.0 y 2.0 veces D50. Debajo: «Table 10.1 provides guidance on the apron length and depth». La clase es la de D50 mayor o igual que el requerido (pag. 10-17).

> **`HEC14.10.2#TW`** — EL LIMITE DE VALIDEZ DE LA Ec. (10.4), con sus dos lados. Por abajo, el ejemplo resuelto de la pag. impresa 10-18 enseña que hacer: con TW/D = 0.33 «This is less than 0.4D, therefore, use TW = 0.4D». Por arriba, la pag. 10-18 remite a OTRO procedimiento (cita HEC14.10.2#TW_ALTO).

> **`HEC14.10.2#TW_ALTO`** — Con el TW sobre la clave la Ec. (10.4) queda FUERA de su rango aceptable y la fuente manda a la Figura 10.3 (atenuacion de la velocidad aguas abajo) y a la Sec. 10.3 para dimensionar la piedra. La Figura 10.3 es una familia de curvas que este programa no tiene digitalizada: ese caso sale como metodo no evaluable, no con la ecuacion extrapolada.

> **`HEC14.3#CONTINUIDAD`** — Sigue: «The flow area, A, for determining outlet velocity is calculated using the culvert outlet depth that is consistent with the culvert flow type», y el num. 3.1.2 (pag. impresa 3-2, PDF 33) da la regla de HDS-5 que M4 aplica: «the higher of the tailwater or critical depth», o la seccion llena con la salida sumergida (3.1.1). Es la relacion con que M6 asigna a la velocidad de salida su area, A = Q/V, para el tirante equivalente del Froude; los procedimientos de HEC-14 hacen lo mismo («A = Q/Vo», pag. impresa 9-40, PDF 197).

> **`HEC14.3.1.3#BORDE`** — Con el TW bajo el tirante critico, el tirante en el borde de la salida (brink depth) es MENOR que el critico: la velocidad real a la salida es MAYOR que Q/A(yc), que es la que M4 toma por HDS-5 3.1.6. El mismo numeral lo dice al aproximar el borde con las curvas criticas: «Since critical depth is larger than brink depth, determining brink depth in this manner is not conservative, but is acceptable». Las Figuras 3.3 y 3.4 dan el borde y no estan digitalizadas.

> **`HEC14.5#PEOR_CASO`** — Dos limites en el mismo parrafo: las ecuaciones dan la hoya MAXIMA de los ensayos («worst-case») y «do not include long-term channel degradation of the downstream channel». El capitulo abre diciendo de que depende el metodo: caudal, forma del conducto, tipo de suelo, duracion del flujo, pendiente, altura del conducto sobre el lecho y tirante de aguas abajo; el tirante de aguas abajo NO entra en la Ec. (5.1).

> **`HEC14.5.1#EC_5_1`** — La Ec. (5.1), leida de la pagina renderizada: [hs/Rc, Ws/Rc, Ls/Rc, Vs/Rc^3] = Cs·Ch·(α / σ^(1/3))·[Q / (g^0.5·Rc^2.5)]^β·(t/316)^θ, con Rc «hydraulic radius at the end of the culvert (assuming full flow)», t «time in minutes» y σ = (D84/D16)^0.5. ES ADIMENSIONAL salvo por el tiempo: el 316 esta en minutos y vale igual en SI y en unidades inglesas. ERRATA DE LA FUENTE: la lista de variables de esta pagina remite «Cs … see Table 5.2» y «Ch … see Table 5.3», y las tablas estan al reves --la 5.2 es de Ch (altura sobre el lecho) y la 5.3 de Cs (pendiente)--, como dicen sus titulos y el texto de los num. 5.1.4 y 5.1.5.

> **`HEC14.5.1.1#T5_1`** — α, β, θ: profundidad 2.27, 0.39, 0.06; ancho 6.94, 0.53, 0.08; longitud 17.10, 0.47, 0.10; volumen 127.08, 1.24, 0.18. El numeral dice ademas que la profundidad maxima se da a unos 0.4·Ls aguas abajo de la salida (Fletcher y Grace, 1972) y que la hoya maxima ocurre con tirantes de aguas abajo menores que la mitad de la altura del conducto (Bohan, 1970).

> **`HEC14.5.1.2#DOS_TERCIOS`** — La frase que sigue a la recomendacion de los 30 minutos. Es lo que dice cuanto de la hoya MAXIMA cubre esa duracion: entre dos tercios y tres cuartos. Sostiene que el criterio 'duracion_caudal_pico_socavacion_min' no adopte los 30 minutos para el desplante del cabezal cuando no hay hidrograma (decision del dueño del 2026-11-12).

> **`HEC14.5.1.2#NO_BAJO_30`** — LIMITE DE VALIDEZ: con t < 30 min los exponentes no aplican. El mismo numeral dice que entre 2/3 y 3/4 de la profundidad maxima se alcanza en los primeros 30 minutos.

> **`HEC14.5.1.2#T30`** — «This knowledge» es la duracion del caudal pico. Para suelos cohesivos la pag. impresa 5-7 repite la regla: «Use 30 minutes for t in Equation 5.2 and Equation 5.3 if it is not known».

> **`HEC14.5.1.3#CABEZAL`** — Es la frase que liga la hoya de socavacion con el DESPLANTE del cabezal de salida. Antes dice que el cabezal perpendicular desplaza la hoya aguas abajo sin cambiar esencialmente su magnitud (Ruff et al., 1982).

> **`HEC14.5.1.4#T5_2`** — Hd = altura del fondo de la salida sobre el lecho, en DIAMETROS («Hd is the height above bed in pipe diameters»): filas 0, 1, 2 y 4. Ch de profundidad 1.00, 1.22, 1.26, 1.34; de ancho 1.00, 1.51, 1.54, 1.66; de longitud 1.00, 0.73, 0.73, 0.73; de volumen 1.00, 1.28, 1.47, 1.55. La tabla no dice como leer entre filas ni mas alla de Hd = 4.

> **`HEC14.5.1.5#T5_3`** — Pendiente en %: filas 0, 2, 5 y «>7». Cs de profundidad 1.00, 1.03, 1.08, 1.12; de ancho 1.00, 1.28, 1.28, 1.28; de longitud 1.00, 1.17, 1.17, 1.17; de volumen 1.00, 1.30, 1.30, 1.30. La tabla no dice como leer entre filas, ni entre el 5 % y el 7 %.

> **`HEC14.5.2#EC_5_2`** — Ec. (5.2), conducto circular: [hs/D, Ws/D, Ls/D, Vs/D^3] = Cs·Ch·α·(ρV²/τc)^β·(t/316)^θ. Ec. (5.3), otras formas: lo mismo con ye = (A/2)^1/2 en lugar de D y αe en lugar de α. V es la velocidad media de salida, ρ = 1000 kg/m3 (1.94 slugs/ft3) y τc la tension tractiva critica de la Ec. (5.4). El numero ρV²/τc es adimensional; lo que depende de unidades es αu de la Ec. (5.4).

> **`HEC14.5.2#EC_5_4`** — Ec. (5.4): τc = 0.001·(Sv + αu)·tan(30 + 1.73·PI), con el argumento de la tangente en GRADOS (el ejemplo resuelve tan (50.76) con PI = 12), Sv la resistencia al corte saturada y αu «unit conversion constant, 8630 N/m2 (SI), 180 lb/ft2 (CU)». τc sale en N/m2. La Tabla 5.4 (misma pagina) da α, β, θ y αe: profundidad 0.86, 0.18, 0.10, 1.37; ancho 3.55, 0.17, 0.07, 5.63; longitud 2.82, 0.33, 0.09, 4.48; volumen 0.62, 0.93, 0.23, 2.48.

> **`HEC14.5.2#RANGO_IP`** — LIMITE DE VALIDEZ. El suelo ensayado fue UNA arcilla arenosa (58 % arena, 27 % arcilla, 15 % limo, indice de plasticidad 15; pag. impresa 5-6).

> **`HEC14.D#SOLO_VELOCIDAD`** — Las dos ecuaciones que HEC-14 descarta son las que dimensionan la piedra SOLO con la velocidad de salida: D.2 (Berry, 1948; Peterka, 1978), D50 = α·V² con α = 0.0413 en SI, y D.3 (Searcy, 1967; la de la edicion anterior de HEC-14 y de HEC 11), D50 = 0.692/(S − 1)·V²/(2g). Ninguna de las dos es la de Laushey, que HEC-14 no nombra. El apendice compara seis relaciones sobre diez casos de HY8 y retiene la de Fletcher y Grace (Ec. D.5), que es la Ec. (10.4) del Capitulo 10 escrita sin la gravedad. La lectura de que la ec. (49) del Manual pertenece a la misma familia que D.2 y D.3 es del proyecto y va en `M6_proteccion`, no aqui.

### Manual de Hidrologia, Hidraulica y Drenaje  (`MC_HHD`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `MC_HHD.3.12.2` | 3.12.2 | ESTIMACIÓN DE CAUDALES › «Método Racional» | pág. impresa **49** · PDF 52 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.12.2#AREA` | 3.12.2 | ESTIMACIÓN DE CAUDALES › «Método Racional» | pág. impresa **49** · PDF 52 | aproximacion | 2026-11-11 · texto |
| `MC_HHD.3.12.2#T08` | 3.12.2 | ESTIMACIÓN DE CAUDALES › «Método Racional» | pág. impresa **50** · PDF 53 | exigencia | 2026-11-11 · ambos |
| `MC_HHD.3.12.2.1#K` | 3.12.2.1 | «Método Racional Modificado» | pág. impresa **51** · PDF 54 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.12.2.1#TC` | 3.12.2.1 | «Método Racional Modificado» | pág. impresa **51** · PDF 54 | aproximacion | 2026-11-11 · ambos |
| `MC_HHD.3.12.5#G` | 3.12.5 | «Otras Metodologías» | pág. impresa **63** · PDF 66 | definicion | 2026-08-28 · ambos |
| `MC_HHD.3.12.5#PIURA` | 3.12.5 | «Otras Metodologías» | pág. impresa **64** · PDF 67 | exigencia | 2026-11-11 · texto |
| `MC_HHD.3.13` | 3.13 | «Avenida de Diseño» | pág. impresa **65** · PDF 68 | definicion | 2026-11-11 · texto |
| `MC_HHD.3.4#FEN` | 3.4 | «Evaluación de la Información Hidrológica» | pág. impresa **22** · PDF 25 | exigencia | 2026-11-11 · texto |
| `MC_HHD.3.4#REGISTRO` | 3.4 | «Evaluación de la Información Hidrológica» | pág. impresa **22** · PDF 25 | recomendacion | 2026-11-11 · texto |
| `MC_HHD.3.6` | 3.6 | «Selección del Período de Retorno» | pág. impresa **25** · PDF 28 | recomendacion | 2026-08-28 · ambos |
| `MC_HHD.3.7.1` | 3.7.1 | ANALISIS ESTADISTICO DE DATOS HIDROLOGICOS › «Modelos de distribución» | pág. impresa **25** · PDF 28 | recomendacion | 2026-11-11 · texto |
| `MC_HHD.3.7.1.1` | 3.7.1.1 | «Distribución Normal» | pág. impresa **26** · PDF 29 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.7.1.2` | 3.7.1.2 | «Distribución  Log  Normal  2  Parámetros» | pág. impresa **27** · PDF 30 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.7.1.7` | 3.7.1.7 | «Distribución Gumbel» | pág. impresa **29** · PDF 32 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.7.2b` | 3.7.2 b) | 3.7.2 Pruebas de bondad de ajuste › «b) Prueba Kolmogorov – Smirnov» | pág. impresa **32** · PDF 35 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.7.2b#ELIGE` | 3.7.2 b) | 3.7.2 Pruebas de bondad de ajuste › «b) Prueba Kolmogorov – Smirnov» | pág. impresa **32** · PDF 35 | permiso | 2026-11-11 · texto |
| `MC_HHD.3.7.2b#T03` | 3.7.2 b) | 3.7.2 Pruebas de bondad de ajuste › «b) Prueba Kolmogorov – Smirnov» | pág. impresa **32** · PDF 35 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.8.1#DICK_PESCHKE` | 3.8.1 | «Curvas Intensidad – Duración – Frecuencia» | pág. impresa **37** · PDF 40 | permiso | 2026-11-11 · ambos |
| `MC_HHD.3.8.1#DURACION` | 3.8.1 | «Curvas Intensidad – Duración – Frecuencia» | pág. impresa **36** · PDF 39 | definicion | 2026-11-11 · texto |
| `MC_HHD.3.8.1#T04` | 3.8.1 | «Curvas Intensidad – Duración – Frecuencia» | pág. impresa **36** · PDF 39 | permiso | 2026-11-11 · ambos |
| `MC_HHD.3.9#T05` | 3.9 | «Tiempo de Concentración» | pág. impresa **39** · PDF 42 | definicion | 2026-11-11 · ambos |
| `MC_HHD.3.9#T05_CALIFORNIA` | 3.9 | «Tiempo de Concentración» | pág. impresa **39** · PDF 42 | aproximacion | 2026-11-11 · ambos |
| `MC_HHD.3.9#T05_FAA` | 3.9 | «Tiempo de Concentración» | pág. impresa **39** · PDF 42 | aproximacion | 2026-11-11 · ambos |
| `MC_HHD.3.9#T05_KIRPICH` | 3.9 | «Tiempo de Concentración» | pág. impresa **39** · PDF 42 | aproximacion | 2026-11-11 · ambos |
| `MC_HHD.3.9#T05_SCS` | 3.9 | «Tiempo de Concentración» | pág. impresa **40** · PDF 43 | aproximacion | 2026-11-11 · ambos |
| `MC_HHD.4.1.1.3.1` | 4.1.1.3.1 | «Aspectos generales» | pág. impresa **70** · PDF 73 | definicion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.2` | 4.1.1.3.2 | «Ubicación en planta» | pág. impresa **71** · PDF 74 | definicion | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.3` | 4.1.1.3.3 | «Pendiente longitudinal» | pág. impresa **71** · PDF 74 | exigencia | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.4a` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **72** · PDF 75 | exigencia | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.4a#MARCO` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **72** · PDF 75 | recomendacion | 2026-09-07 · texto |
| `MC_HHD.4.1.1.3.4a#MULTIPLES` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **72** · PDF 75 | recomendacion | 2026-09-07 · texto |
| `MC_HHD.4.1.1.3.4a#NIVELES` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **72** · PDF 75 | permiso | 2026-09-07 · texto |
| `MC_HHD.4.1.1.3.4a#SEPARACION` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **72** · PDF 75 | recomendacion | 2026-11-12 · texto |
| `MC_HHD.4.1.1.3.4a#TIPOS` | 4.1.1.3.4 a) | 4.1.1.3.4  Elección del tipo de alcantarilla › «a)  Tipo y sección» | pág. impresa **71** · PDF 74 | definicion | 2026-09-07 · texto |
| `MC_HHD.4.1.1.3.4b` | 4.1.1.3.4 b) | 4.1.1.3.4  Elección del tipo de alcantarilla › «b)  Materiales» | pág. impresa **73** · PDF 76 | definicion | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.5` | 4.1.1.3.5 | «Recomendaciones y factores a tomar en cuenta para el diseño de una alcantarilla» | pág. impresa **73** · PDF 76 | recomendacion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.6` | 4.1.1.3.6 | «Diseño hidráulico» | pág. impresa **74** · PDF 77 | definicion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.6#T09` | 4.1.1.3.6, Tabla Nº 09 | «Diseño hidráulico» | pág. impresa **75** · PDF 78 | definicion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.6#T10` | 4.1.1.3.6, Tabla Nº 10 | «Diseño hidráulico» | pág. impresa **76** · PDF 79 | exigencia | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.6#T11` | 4.1.1.3.6, Tabla Nº 11 | «Diseño hidráulico» | pág. impresa **77** · PDF 80 | exigencia | 2026-11-12 · ambos |
| `MC_HHD.4.1.1.3.6#VMIN` | 4.1.1.3.6, párrafo posterior a la Tabla Nº 10 | «Diseño hidráulico» | pág. impresa **77** · PDF 80 | recomendacion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.6#VMIN_INICIO` | 4.1.1.3.6, párrafo posterior a la Tabla Nº 10 (primera mitad) | «Diseño hidráulico» | pág. impresa **76** · PDF 79 | exigencia | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.6#V_SALIDA` | 4.1.1.3.6, párrafo anterior a la Tabla Nº 11 | «Diseño hidráulico» | pág. impresa **77** · PDF 80 | exigencia | 2026-11-12 · texto |
| `MC_HHD.4.1.1.3.7a` | 4.1.1.3.7 a) | 4.1.1.3.7  Consideraciones para el diseño › «a)   Material sólido de arrastre» | pág. impresa **79** · PDF 82 | recomendacion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.7b` | 4.1.1.3.7 b) | 4.1.1.3.7  Consideraciones para el diseño › «b)  Borde libre» | pág. impresa **79** · PDF 82 | recomendacion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.3.7b#LLENA` | 4.1.1.3.7 b) | 4.1.1.3.7  Consideraciones para el diseño › «b)  Borde libre» | pág. impresa **79** · PDF 82 | exigencia | 2026-09-20 · texto |
| `MC_HHD.4.1.1.3.7c` | 4.1.1.3.7 c), ec. (49) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **80** · PDF 83 | aproximacion | 2026-08-28 · imagen renderizada |
| `MC_HHD.4.1.1.3.7c#ALIVIADERO` | 4.1.1.3.7 c) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **80** · PDF 83 | permiso | 2026-11-12 · texto |
| `MC_HHD.4.1.1.3.7c#G` | 4.1.1.3.7 c), lista de variables de la ec. (49) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **80** · PDF 83 | definicion | 2026-08-28 · ambos |
| `MC_HHD.4.1.1.3.7c#PROTECCION` | 4.1.1.3.7 c) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **79** · PDF 82 | recomendacion | 2026-11-12 · texto |
| `MC_HHD.4.1.1.3.7c#REVESTIMIENTOS` | 4.1.1.3.7 c) | 4.1.1.3.7  Consideraciones para el diseño › «c)  Socavación local a la salida de la alcantarilla» | pág. impresa **80** · PDF 83 | recomendacion | 2026-11-12 · texto |
| `MC_HHD.4.1.1.3.7d` | 4.1.1.3.7 d) | 4.1.1.3.7  Consideraciones para el diseño › «d)  Mantenimiento y limpieza» | pág. impresa **80** · PDF 83 | exigencia | 2026-09-07 · texto |
| `MC_HHD.4.1.1.3.7e` | 4.1.1.3.7 e) | 4.1.1.3.7  Consideraciones para el diseño › «e)  Abrasión» | pág. impresa **81** · PDF 84 | recomendacion | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.7f#COSTA` | 4.1.1.3.7 f) | 4.1.1.3.7  Consideraciones para el diseño › «f)  Corrosión» | pág. impresa **81** · PDF 84 | exigencia | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.7f#SALINIDAD` | 4.1.1.3.7 f) | 4.1.1.3.7  Consideraciones para el diseño › «f)  Corrosión» | pág. impresa **81** · PDF 84 | definicion | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.7f#TMC` | 4.1.1.3.7 f) | 4.1.1.3.7  Consideraciones para el diseño › «f)  Corrosión» | pág. impresa **82** · PDF 85 | recomendacion | 2026-11-11 · texto |
| `MC_HHD.4.1.1.3.7g#AGRESIVAS` | 4.1.1.3.7 g) | 4.1.1.3.7  Consideraciones para el diseño › «g)  Seguridad y vida útil» | pág. impresa **82** · PDF 85 | recomendacion | 2026-11-11 · texto |
| `MC_HHD.4.1.1.4.1e` | 4.1.1.4.1 e) | 4.1.1.4   BADENES › 4.1.1.4.1  Consideraciones para el diseño › «e)   Borde libre» | pág. impresa **85** · PDF 88 | exigencia | 2026-09-08 · texto |
| `MC_HHD.4.1.1.4.1e#RANGO` | 4.1.1.4.1 e), segunda oracion | 4.1.1.4   BADENES › 4.1.1.4.1  Consideraciones para el diseño › «e)   Borde libre» | pág. impresa **85** · PDF 88 | recomendacion | 2026-09-08 · texto |
| `MC_HHD.4.1.1.5.1` | 4.1.1.5.1 | 4.1.1.5  PUENTES › «Aspectos generales» | pág. impresa **87** · PDF 90 | definicion | 2026-08-28 · texto |
| `MC_HHD.4.1.1.5.4b24#G` | 4.1.1.5.4 b.2.4), ec. (63) | b.2.) Socavación General › «Método de Laursen» | pág. impresa **111** · PDF 114 | definicion | 2026-08-28 · ambos |
| `MC_HHD.4.1.2.1#SECCION` | 4.1.2.1 | «4.1.2.1 Cunetas» | pág. impresa **173** · PDF 176 | definicion | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1#T09` | 4.1.2.1 a) | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **175** · PDF 178 | definicion | 2026-11-13 · ambos |
| `MC_HHD.4.1.2.1#T304_12` | 4.1.2.1, Tabla 304.12 (del DG-2001) | «4.1.2.1 Cunetas» | pág. impresa **173** · PDF 176 | exigencia | 2026-11-13 · ambos |
| `MC_HHD.4.1.2.1#T32` | 4.1.2.1 a), Tabla Nº 32 | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **175** · PDF 178 | definicion | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1#T33` | 4.1.2.1 a), Tabla Nº 33 | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **175** · PDF 178 | exigencia | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1#UBICACION` | 4.1.2.1 | «4.1.2.1 Cunetas» | pág. impresa **173** · PDF 176 | definicion | 2026-11-13 · ambos |
| `MC_HHD.4.1.2.1a` | 4.1.2.1 a) | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **174** · PDF 177 | definicion | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1a#CONDICION` | 4.1.2.1 a), procedimiento de calculo | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **177** · PDF 180 | exigencia | 2026-11-13 · ambos |
| `MC_HHD.4.1.2.1a#MANNING` | 4.1.2.1 a), ecuación (117) | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **174** · PDF 177 | definicion | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1a#VELOCIDAD` | 4.1.2.1 a), ecuaciones (4.2) y (4.5) | 4.1.2.1 Cunetas › «a) Capacidad de las cunetas» | pág. impresa **176** · PDF 179 | definicion | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1b` | 4.1.2.1 b) | 4.1.2.1 Cunetas › «b) Caudal Q de aporte» | pág. impresa **177** · PDF 180 | definicion | 2026-11-11 · ambos |
| `MC_HHD.4.1.2.1c#T34` | 4.1.2.1 c), Tabla Nº 34 | 4.1.2.1 Cunetas › «c) Dimensiones mínimas» | pág. impresa **178** · PDF 181 | exigencia | 2026-11-12 · ambos |
| `MC_HHD.4.1.2.1d` | 4.1.2.1 d) | 4.1.2.1 Cunetas › «d) Desagüe de las cunetas» | pág. impresa **179** · PDF 182 | exigencia | 2026-08-28 · ambos |
| `MC_HHD.4.1.2.1d#ALIVIO` | 4.1.2.1 d) | 4.1.2.1 Cunetas › «d) Desagüe de las cunetas» | pág. impresa **179** · PDF 182 | exigencia | 2026-11-13 · ambos |
| `MC_HHD.4.1.2.1e` | 4.1.2.1 e) | 4.1.2.1 Cunetas › «e) Revestimiento de las cunetas» | pág. impresa **180** · PDF 183 | exigencia | 2026-11-12 · ambos |
| `MC_HHD.4.1.2a` | 4.1.2 a) | 4.1.2 DRENAJE LONGITUDINAL DE LA CARRETERA › «a) Período de retorno» | pág. impresa **171** · PDF 174 | definicion | 2026-11-12 · ambos |
| `MC_HHD.4.1.2c` | 4.1.2 c) | 4.1.2 DRENAJE LONGITUDINAL DE LA CARRETERA › «c) Velocidad máxima del agua» | pág. impresa **172** · PDF 175 | exigencia | 2026-11-12 · ambos |
| `MC_HHD.LAMINA_01` | Lámina Nº 01 | «UBICACIÓN TÍPICA DE ALCANTARILLAS» | pág. impresa **206** · PDF 209 | definicion | 2026-11-11 · imagen renderizada |
| `MC_HHD.LAMINA_02` | Anexos, Lámina Nº 02 | «TIPO  TMC CON PROTECCIÓN DE» | pág. impresa **207** · PDF 210 | definicion | 2026-11-12 · ambos |
| `MC_HHD.LAMINA_02A` | Anexos, Lámina Nº 02-A | «TIPO  TMC CON PROTECCIÓN DE» | pág. impresa **208** · PDF 211 | definicion | 2026-11-12 · ambos |
| `MC_HHD.LAMINA_03` | Lámina Nº 03 | «SECCIONES TÍPICAS DE ALCANTARILLAS» | pág. impresa **209** · PDF 212 | definicion | 2026-09-07 · imagen renderizada |
| `MC_HHD.LAMINA_04` | Anexos, Lámina Nº 04 | «PERFIL LONGITUDINAL Y SECCIÓN TÍPICAS» | pág. impresa **210** · PDF 213 | definicion | 2026-11-12 · ambos |
| `MC_HHD.LAMINA_04#DENTELLON` | Anexos, Lámina Nº 04 | «DE ALIVIADERO CON DISIPADOR DE ENERGÍA» | pág. impresa **210** · PDF 213 | definicion | 2026-11-12 · ambos |
| `MC_HHD.LAMINA_05` | Anexos, Lámina Nº 05 | «ALCANTARILLA  CON  ENROCADO» | pág. impresa **211** · PDF 214 | definicion | 2026-11-12 · ambos |

> **`MC_HHD.3.12.2`** — Ecuacion (28). Las unidades estan en la pag. impresa 50 (PDF 53): Q «Descarga máxima de diseño (m3/s)», C «Coeficiente de escorrentía (Ver Tabla Nº 08)», I «Intensidad de precipitación máxima horaria (mm/h)», A «Área de la cuenca (Km2).» El 0,278 es 1/3.6, la conversion de mm/h·km² a m³/s: es el mismo cociente que el num. 4.1.2.1 b) escribe como C·I·A/3.6. El numeral NO trae ejemplo numerico.

> **`MC_HHD.3.12.2#AREA`** — La desigualdad es ESTRICTA: 10 km² exactos quedan fuera. Y el verbo es descriptivo («Muy usado para»): la fuente no prohibe el metodo por encima, dice donde se usa. El proyecto lo aplica como limite de validez y por encima no evalua, remitiendo al hidrograma unitario del num. 3.12.3.

> **`MC_HHD.3.12.2#T08`** — Es la oracion que sigue a la Tabla Nº 08. La tabla da el NUMERO; que fila describe a la cuenca lo establece el estudio, con sus caracteristicas: por eso cobertura y suelo son columnas del CSV de cuencas y no una eleccion del programa.

> **`MC_HHD.3.12.2.1#K`** — Ecuacion (29), con «K : Coeficiente de Uniformidad». Su apartado «B) Coeficiente de Uniformidad» da la ecuacion (31), vista en imagen: K = 1 + Tc^1.25 / (Tc^1.25 + 14), con «Tc= Tiempo de concentración (horas)». K es siempre mayor que 1 y crece con Tc (1.01 a 0.25 h, 1.07 a 1 h, 1.79 a 24 h). El metodo trae ademas su propia intensidad (ec. 34), su factor reductor por area (ec. 32) y su coeficiente C por numero de curva (ec. 35), que el proyecto NO usa: toma la formula del tiempo de concentracion (ec. 30) y, con ella, este coeficiente.

> **`MC_HHD.3.12.2.1#TC`** — Ecuacion (30), apartado «A) Tiempo de Concentración (Tc)», vista en imagen: Tc = 0.3 · (L / S^0.25)^0.76, con «L= Longitud del cauce mayor (km)» y «S= Pendiente promedio del cauce mayor (m/m)»; Tc sale en HORAS (lo dicen el rango de arriba y el apartado B). Es la formula de Temez, y vive AQUI y no en la Tabla Nº 05. El rango de area y de Tc es el del metodo racional modificado entero, del que esta formula es una pieza: el proyecto toma SOLO la formula del tiempo de concentracion y le aplica ese rango como validez; no usa el resto del metodo (coeficiente de uniformidad, factor reductor, numero de curva).

> **`MC_HHD.3.12.5#G`** — Primera de las DOS paginas del Manual donde 9.8 figura como gravedad.

> **`MC_HHD.3.12.5#PIURA`** — La oracion entera: «Otra metodología es la que resalte la influencia de El Fenómeno “El Niño”, en especial en la Vertiente del Pacífico del Perú, departamentos de Piura y Tumbes, donde es necesario un tratamiento especial del análisis para determinar el caudal de diseño.» El Manual lo dice de los caudales y no da el tratamiento; el proyecto lo imprime en la memoria hidrologica porque el ajuste de una sola distribucion a una serie con años de El Niño puede dejar la lluvia de diseño por debajo de lo ya observado, y eso se avisa en el paso del ajuste.

> **`MC_HHD.3.13`** — El numeral no da formula ni umbral: remite al estudio hidrologico («Estimación de Caudales») y a «la experiencia y el buen tino del ingeniero proyectista». Por eso el caudal especifico Q/A se imprime como contraste y no se juzga contra nada.

> **`MC_HHD.3.4#FEN`** — El numeral abre en la pag. impresa 21 (PDF 24) y esta oracion esta en la 22 (PDF 25). Son DOS mandatos en una oracion y tiran en sentidos opuestos: la serie «deberá incluir» los años del Niño, y esos años deben «ser evaluados» para no sobredimensionar. La fuente no dice COMO evaluarlos: de ahi el criterio 'homogeneidad_serie_fen'.

> **`MC_HHD.3.4#REGISTRO`** — Misma oracion que MC_HHD.3.4#FEN, otra clausula. Es «se recomienda»: una serie mas corta no queda prohibida, y por eso el paso de la serie lo imprime como INDICADOR y no detiene.

> **`MC_HHD.3.6`** — El numeral abre en la pag. impresa 23 (PDF 26); la Tabla Nº 02 y este parrafo estan en la 25 (PDF 28).

> **`MC_HHD.3.7.1`** — La lista de ocho (i a viii) se imprime en la pag. impresa 26 (PDF 29): Normal, Log Normal 2 parámetros, Log Normal 3 parámetros, Gamma 2 parámetros, Gamma 3 parámetros, Log Pearson tipo III, Gumbel y Log Gumbel. El Manual imprime la funcion de cada una y SOLO de tres dice como se estiman sus parametros: la Normal (media y desviacion estandar, 3.7.1.1), la Log Normal de 2 parametros (media y desviacion de los logaritmos, 3.7.1.2) y Gumbel (metodo de momentos, 3.7.1.7).

> **`MC_HHD.3.7.1.1`** — Ecuacion (2), la densidad normal. El renglon siguiente dice lo mismo del otro parametro: «S = parámetro de escala, igual a la desviación estándar de x.»

> **`MC_HHD.3.7.1.2`** — La pagina imprime, vistas en imagen, Y = Σ log xi / n y Sy = raiz( Σ (yi − Y)² / (n − 1) ): la desviacion es la MUESTRAL, con n − 1. El numeral escribe «y=log(x)» sin decir la base; el cuantil no depende de ella mientras se use la misma para ajustar y para invertir, y el proyecto usa el logaritmo natural.

> **`MC_HHD.3.7.1.7`** — Ecuacion (9): F(x) = exp(−exp(−α(x − β))). Las dos relaciones, vistas en imagen: α = 1.2825 / σ y β = µ − 0.45 σ. Los dos numeros son los que la pagina imprime (los exactos son π/√6 = 1.28255 y 0.5772·√6/π = 0.45005). La pagina NO dice para que tamaño de muestra valen ni menciona correccion alguna por n.

> **`MC_HHD.3.7.2b`** — D = máx |Fo(xm) − F(xm)| y, ecuacion (13), Fo(xm) = 1 − m/(n+1), con m el numero de orden del dato en una lista de MAYOR a menor. El valor critico d sale de la Tabla Nº 03 de la misma pagina. La desigualdad es estricta: D = d no acepta.

> **`MC_HHD.3.7.2b#ELIGE`** — Es lo que sostiene el valor de archivo del criterio 'distribucion_precipitacion_maxima' (la de menor D): la fuente PERMITE elegir asi, no lo manda.

> **`MC_HHD.3.7.2b#T03`** — La tabla empieza en la pag. impresa 32 (PDF 35: n = 5 a 25) y termina en la 33 (PDF 36: n = 30, 35 y 40, y «Fuente: Aparicio, 1999.»).

> **`MC_HHD.3.8.1#DICK_PESCHKE`** — Ecuacion (16), vista en imagen: Pd = P24h · (d / 1440)^0.25, con d en MINUTOS y las dos precipitaciones en mm. Y a renglon seguido: «La intensidad se halla dividiendo la precipitación Pd entre la duración.» Las dos condiciones van unidas por «o»: basta con no tener registros pluviograficos, que es el caso de una serie de maximas en 24 horas.

> **`MC_HHD.3.8.1#T04`** — La Tabla Nº 04 empieza en la pag. impresa 36 (PDF 39: 1 a 8 horas) y termina en la 37 (PDF 40: 10 a 48 horas). El coeficiente multiplica a la precipitacion maxima en 24 horas y da la PRECIPITACION de esa duracion; la intensidad es ese producto entre la duracion.

> **`MC_HHD.3.9#T05`** — La Tabla Nº 05 ocupa las pags. impresas 39 (PDF 42: Kirpich, California Culverts Practice, Izzard y Federal Aviation Administration) y 40 (PDF 43: ecuaciones de onda cinematica y ecuacion de retardo SCS). Su encabezado dice «FÓRMULA PARA tc (minutos)». NO lista a Temez.

> **`MC_HHD.3.9#T05_CALIFORNIA`** — Fila «California Culverts Practice (1942)». La formula, vista en imagen: tc = 0.0195 · (L³ / H)^0.385, con «L = longitud del curso de agua más largo, m.» y «H = diferencia de nivel entre la divisoria de aguas y la salida, m.» La observacion NO escribe un rango numerico propio.

> **`MC_HHD.3.9#T05_FAA`** — Fila «Federal Aviation Administration (1970)». La formula, vista en imagen: tc = 0.7035 · (1.1 − C) · L^0.50 / S^0.333, con «C = coeficiente de escorrentía del método racional», «L = longitud del flujo superficial, m.» y «S = pendiente de la superficie, m/m». Es una formula de FLUJO SUPERFICIAL (sobre una superficie, no por un cauce) y la observacion no le escribe rango numerico: es la que el proyecto ofrece para una plataforma, un talud o una cuenca plana sin cauce definido.

> **`MC_HHD.3.9#T05_KIRPICH`** — Fila «Kirpich (1940)». La formula, vista en imagen: tc = 0.01947 · L^0.77 · S^−0.385, con «L = longitud del canal desde aguas arriba hasta la salida, m.» y «S = pendiente promedio de la cuenca, m/m». La observacion sigue: para flujo superficial en superficies de concreto o asfalto se debe multiplicar tc por 0.4; para canales de concreto, por 0.2; ningun ajuste para flujo superficial en suelo descubierto o para flujo en cunetas. El «(3 a 10%)» es la poblacion de la que salio la formula.

> **`MC_HHD.3.9#T05_SCS`** — Fila «Ecuación de retardo SCS (1973)». La formula, vista en imagen: tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 / S^0.5, con «L = longitud hidráulica de la cuenca (mayor trayectoria de flujo), m.», «CN = Número de curva SCS» y «S = pendiente promedio de la cuenca, m/m». La observacion sigue: buena cuando el area esta completamente pavimentada, tiende a sobreestimar en areas mixtas, y «la ecuación supone que tc = 1.67 x retardo de la cuenca». Las «800 Ha» son la poblacion a la que se adapto; el proyecto las trata como a los «3 a 10%» de Kirpich.

> **`MC_HHD.4.1.1.3.2`** — El numeral NO da un esviaje maximo ni una longitud: dice que lo ideal es seguir la corriente y que desplazar la ubicacion natural obliga a acondicionar el cauce a la entrada y a la salida con obras de encauzamiento. Es el fundamento de que el conducto se tienda esviado (factor 1/cos) en vez de rectificar el cruce.

> **`MC_HHD.4.1.1.3.3`** — EXIGENCIA SIN NUMERO. El numeral entero son dos parrafos: este y la remision a la Lamina Nº 01 («ubicación típica de alcantarillas respecto a la pendiente del cauce»). No fija pendiente minima ni maxima, ni en porcentaje ni por material: obliga a ESTUDIAR el cambio de pendiente. Las cifras «2 % en TMC, 1 % en marco» que circulan en expedientes no salen de aqui.

> **`MC_HHD.4.1.1.3.4a#SEPARACION`** — LA REGLA ES DE TUBERIAS y su razon es la COMPACTACION DEL RELLENO entre tubos: «medida entre las superficies externas», «que facilite la compactación del material de relleno». Un marco multicelda VACIADO IN SITU (§14.1 de docs/ruta_familia_c.md) es monolitico: sus celdas comparten tabique y entre ellas no hay relleno que compactar, de modo que la separacion entre celdas es el espesor del tabique y esta regla no la fija. Se cita en V6 (T-3) como la regla que aplicaria si las celdas fueran barriles independientes con relleno entre ellos: D/2, con 0.40 m <= s <= 1.00 m.

> **`MC_HHD.4.1.1.3.4b`** — EL MANUAL NO DA REGLA DE ELECCION DE MATERIAL, y lo dice con esas palabras. La frase anterior enumera de que depende: «tiempo de vida útil, costo, resistencia, rugosidad, condiciones del terreno, resistencia a la corrosión, abrasión, fuego e impermeabilidad». Es lo que hace de la matriz de durabilidad un FILTRO con fuentes tecnicas y no una eleccion normativa: el Manual nombra los factores (suelo, agua) y no pone umbrales.

> **`MC_HHD.4.1.1.3.5`** — Se declara aunque el proyecto no tome ningun valor de el: es el numeral con el que se confundio la Tabla Nº 09 antes de S5, y tenerlo escrito con su titulo es lo que impide repetir la confusion. NO contiene ninguna tabla de rugosidad.

> **`MC_HHD.4.1.1.3.6#T09`** — La tabla ocupa dos paginas impresas: los grupos A, B y C en la 75 (PDF 78) y el grupo D con la linea de Fuente en la 76 (PDF 79).

> **`MC_HHD.4.1.1.3.6#T10`** — El titulo se imprime en DOS renglones y el segundo dice solo «revestidos»; el `texto_literal` es el primero, que es el que se puede buscar de corrido. El titulo completo esta en `TablaNormativa.titulo_literal`.

> **`MC_HHD.4.1.1.3.6#T11`** — El titulo se imprime en DOS renglones y el segundo dice solo «revestidos»: mismo caso que la Tabla Nº 10. Trece filas de terreno y DOS columnas de valores, «FLUJO INTERMITENTE (M/S)» y «FLUJO PERMANENTE (M/S)»; seis de las filas cuelgan del encabezado «Material graduado (no coloidal)», que no lleva valores. Al pie: «Fuente: Manual de Carreteras de California». Leida por texto y por imagen; la transcripcion entera es `TablaNormativa` MC_HHD.T11.

> **`MC_HHD.4.1.1.3.6#VMIN`** — El parrafo cruza el salto de pagina: arranca en la impresa 76 («Se deberá verificar que la velocidad mínima del flujo dentro del conducto no produzca sedimentación que pueda incidir en una») y el numero se imprime en la 77. El `texto_literal` es la mitad que contiene el valor, porque es la que T5 tiene que poder encontrar en la pagina que la cita declara.

> **`MC_HHD.4.1.1.3.6#VMIN_INICIO`** — La frase se corta donde la corta la PAGINA, no donde conviene: «...incidir en una» es literalmente el ultimo renglon de la pag. impresa 76, y completarla aqui con «reducción de su capacidad hidráulica» produciria un texto que no esta en esta pagina y que el buscador de un lector no encuentra. La continuacion es `MC_HHD.4.1.1.3.6#VMIN`, y las dos juntas son la oracion entera.

> **`MC_HHD.4.1.1.3.6#V_SALIDA`** — Es la frase que convierte la Tabla Nº 11 en un limite de la velocidad de SALIDA: «debe limitarse». El parrafo siguiente presenta la tabla «con valores máximos admisibles de velocidades de flujo según el tipo de material donde se desplaza». El Manual no dice que hacer cuando la velocidad los supera; lo dice el num. 4.1.1.3.7 c): proteger el cauce.

> **`MC_HHD.4.1.1.3.7a`** — Las CUATRO caracteristicas a las que «el párrafo anterior» remite estan en la pag. impresa 78 (PDF 81), no en la 79: la cita del repositorio decia solo «pag. 79» y con eso el condicionante quedaba fuera del rango citado. El rango correcto es 78-79. El valor 1.22 m NO esta en la fuente: el Manual escribe «Ф 48”» y la conversion (48 in = 1.2192 m) es del proyecto.

> **`MC_HHD.4.1.1.3.7b`** — El 0.75 que el codigo usa es la DERIVACION aritmetica de este 25 % (1 - 0.25), no una cifra impresa; y la fuente no escribe «y/D» sino «la altura, diámetro o flecha de la estructura». La frase inmediatamente anterior SI es prohibitiva («las alcantarillas no deben ser diseñadas para trabajar a sección llena») pero prohibe la seccion llena, no fija el 25 %.

> **`MC_HHD.4.1.1.3.7b#LLENA`** — Es la oracion inmediatamente ANTERIOR a la del 25 %, en el mismo parrafo. Prohibe la seccion llena y no fija cuanto borde libre hace falta: por eso sostiene el «no cumple» de V1 a barril LLENO (y/D = 1) y no el umbral 0.75, que sigue siendo la recomendacion endurecida por el proyecto.

> **`MC_HHD.4.1.1.3.7c`** — La ec. (49) es d50 = V² / (3.1 g). La extraccion de texto la devuelve desordenada («) 1.3 ( 2 50 g V d =») por el orden de trazado, de modo que la lectura fiable es la de la pagina renderizada: el metodo de esta cita es IMAGEN y decirlo es parte de la verificacion.

> **`MC_HHD.4.1.1.3.7c#ALIVIADERO`** — La frase siguiente remite a la Lámina Nº 04 (cita MC_HHD.LAMINA_04). Es la alternativa que el Manual da cuando la velocidad es alta: no reviste el cauce, reduce la velocidad. El programa no la dimensiona.

> **`MC_HHD.4.1.1.3.7c#G`** — NOR-HID-01 / MAT-O7. ESTE NUMERAL NO ESCRIBE NINGUN VALOR DE g: define el simbolo y su unidad. El 9.8 que el proyecto usa SI esta en el Manual, en otros dos numerales (ver MC_HHD.3.12.5 y MC_HHD.4.1.1.5.4b24), y el 9.81 no aparece ni una vez en las 225 paginas. Se corrige la ATRIBUCION, no el numero.

> **`MC_HHD.4.1.1.3.7c#PROTECCION`** — LA ORACION CRUZA DE PAGINA: sigue en la impresa 80 (PDF 83) con «natural mediante la construcción de emboquillados de piedra…» (cita MC_HHD.4.1.1.3.7c#REVESTIMIENTOS). Nombra la ENTRADA junto a la salida: es el unico texto del Manual que sostiene una proteccion de entrada, y la sostiene como RECOMENDACION, sin formula ni dimension.

> **`MC_HHD.4.1.1.3.7c#REVESTIMIENTOS`** — Segunda mitad de la oracion. Enumera TRES clases de revestimiento --emboquillados de piedra, enchapado de rocas acomodadas, «otros tipos»-- sin preferir ninguna ni dar dimensiones: de ahi el conjunto cerrado del criterio 'tipo_proteccion_entrada'. Y fija el alcance en planta por un criterio fisico, no por una longitud: hasta donde la socavacion local no incida.

> **`MC_HHD.4.1.1.3.7e`** — CUALITATIVO, SIN NINGUN VALOR: el inciso define la abrasion «la erosión del material de la alcantarilla por la acción de sólidos flotantes transportados por el cauce natural» y dice de que depende («carácter y cantidad de material de arrastre, duración, frecuencia y velocidad del flujo»), pero no escribe ninguna velocidad maxima para el metal ni para el plastico. La Tabla N 10 (num. 4.1.1.3.6) tampoco los lista. Es la razon de que 'v_max_tmc' sea [A]: la norma peruana manda considerar la abrasion y no da el numero.

> **`MC_HHD.4.1.1.3.7f#COSTA`** — LA FRASE SE CORTA DONDE LA CORTA LA PAGINA: «...requieren» es el ultimo renglon de la pag. impresa 81, y sigue en la 82 (PDF 85) con «algún tipo de protección para asegurar su vida útil». Dice CUALQUIER material, no solo el metal, y no cuantifica «cercanas al mar»: el corredor del repositorio (La Union, Bajo Piura) esta en la costa, y si la frase le alcanza lo decide el proyectista con el EMS, no este registro.

> **`MC_HHD.4.1.1.3.7f#SALINIDAD`** — El parrafo anterior nombra las tres condiciones que la matriz de durabilidad recibe como ensayo: «condiciones alcalinas y ácidas presentes en el suelo y en el agua, y la conductividad eléctrica del suelo» --o sea pH y resistividad--. NO DA UMBRAL de salinidad ni de cloruros: por eso 'cloruros_ppm' produce un AVISO y no un descarte.

> **`MC_HHD.4.1.1.3.7f#TMC`** — El inciso abre en la pag. impresa 81 (PDF 84) y este parrafo esta en la 82. La frase anterior, misma pagina: «los suelos con alto contenido de materia orgánica son nocivos para los metales ya que se corroen».

> **`MC_HHD.4.1.1.3.7g#AGRESIVAS`** — LA ORACION SIGUE, y se corta aqui a proposito antes del salto de pagina: «..., por ello, se recomienda el uso de otros materiales para la construcción de» (fin de la impresa 82) «alcantarillas, como concreto de alta resistencia o tubos de alta densidad» (impresa 83, PDF 86). ES RECOMENDACION («no es recomendable»), no prohibicion, y NO CUANTIFICA ninguna de las condiciones: no dice que velocidad es excesiva ni que salinidad es agresiva. La matriz de durabilidad la imprime como AVISO cuando un ensayo declarado cae en una de esas condiciones; el descarte del TMC por pH o por resistividad sale de los umbrales de WSDOT §8-5 [C].

> **`MC_HHD.4.1.1.4.1e`** — «debe contemplar mantener» es EXIGENCIA, y lo que exige es que HAYA borde libre: no fija cuanto. El cuanto esta en la oracion siguiente y es RECOMENDACION --- por eso son dos citas y no una, igual que el par VMIN_INICIO / VMIN de V2 ---. Fundir las dos en un solo objeto haria pasar por exigido el 0.30-0.50, que la fuente solo recomienda.

> **`MC_HHD.4.1.1.4.1e#RANGO`** — LA ORACION LLEVA DOS COSAS Y SOLO UNA ES EL RANGO. La primera mitad DESCRIBE una practica --- que el borde libre se asuma igual a la altura de velocidad --- y el «sin embargo» la desplaza en favor del par de valores. El rango va en TEXTO CORRIDO, sin tabla, y no es funcion de ninguna variable: ni del caudal, ni de la luz, ni de la velocidad. El Manual tampoco da regla para elegir dentro de el, y por eso la eleccion es del proyectista y no de la fuente. «0.50m» va sin espacio entre numero y unidad, tal como imprime.

> **`MC_HHD.4.1.1.5.1`** — NOR-HID-05, cerrado: el numeral ARRANCA en la pag. impresa 86 (PDF 89) y la frase que sostiene el valor esta en la 87 (PDF 90). La cita anterior decia «pag. 88», donde el Manual imprime «a.1) Topografía – Batimetría del cauce y zonas adyacentes», del num. 4.1.1.5.2.

> **`MC_HHD.4.1.1.5.4b24#G`** — Segunda y ultima pagina del Manual donde 9.8 figura como gravedad. Es socavacion general por contraccion en PUENTES, no la de salida de alcantarilla: sostiene el NUMERO, no el numeral de Laushey.

> **`MC_HHD.4.1.2.1#SECCION`** — La misma pagina, dos renglones antes: las cunetas «serán de concreto vaciadas en el sitio, prefabricados o de otro material resistente a la erosión». Y despues: la inclinacion del talud interior (1:Z1) se rige por la Tabla 304.12 del DG-2001 (1:2 a 1:4 segun velocidad de diseño e IMDA) y la del exterior (1:Z2) «será de acuerdo al tipo de inclinación considerada en el talud de corte». La Figura Nº 27 (pag. impresa 174) dibuja el ancho «a» y la profundidad «d» de la seccion triangular: a = Z1·d.

> **`MC_HHD.4.1.2.1#T09`** — La viñeta anterior a la del coeficiente de Strickler (MC_HHD.4.1.2.1#T32): el apartado ofrece las DOS tablas y no dice cual rige. El programa usa la Tabla Nº 32, que es la que el num. 4.1.2.1 escribe para cunetas, y lo declara en el paso de la capacidad con la Tabla Nº 09 como alternativa.

> **`MC_HHD.4.1.2.1#T304_12`** — La tabla, leida en imagen: «Tabla 304.12 INCLINACIONES MÁXIMAS DEL TALUD (V:H) INTERIOR DE LA CUNETA», filas por V.D. (km/h) y columnas por I.M.D.A. (veh./dia): con V.D. < 70 e IMDA < 750, 1:2 —con la llamada «(*) Sólo en casos muy especiales»— o 1:3; con V.D. < 70 e IMDA > 750, 1:3; con V.D. > 70 e IMDA < 750, 1:3; con V.D. > 70 e IMDA > 750, 1:4. Son inclinaciones MAXIMAS: un talud mas tendido siempre cumple. Ni la velocidad de diseño ni el IMDA son datos del programa: la Fase 10 rechaza un talud mas empinado que 1:2, que ninguna fila admite, y avisa de la fila que el talud adoptado deja fuera. Vistas de calculo: `constantes_normativas.CUNETA_Z1_MIN_T304_12`.

> **`MC_HHD.4.1.2.1#T32`** — TABLA Nº 32 «Valores de K más usados»: «Cunetas excavadas en el terreno K = 33», «Cunetas en roca K = 25», «Cunetas de concreto K = 67». Al pie: «Fuente: Ingeniería Vial I de Hugo Morales Sosa». Transcripcion entera: `TablaNormativa` MC_HHD.T32.

> **`MC_HHD.4.1.2.1#T33`** — Ocho filas de superficie y UNA columna, «VELOCIDAD LÍMITE ADMISIBLE (M/S)», con un intervalo por fila (0.20 – 0.60 ... 4.50 – 6.00). Las dos ultimas llevan «*», cuya nota dice «Para flujos de muy corta duración». Al pie: «Fuente: Manual de Diseño de Carreteras Pavimentadas de Bajo Volumen de Tránsito-MTC». El num. 4.1.2 c), pag. impresa 172, repite los mismos valores como Tabla Nº 31. EL CARACTER es el del apartado e) (pag. impresa 180): las cunetas «deben ser revestidas» cuando la velocidad media supera estos limites. Cual de los dos extremos de la fila rige NO lo dice la fuente: es el criterio 'lectura_velocidad_limite_cuneta'.

> **`MC_HHD.4.1.2.1a`** — Lo que la fuente llama capacidad son DOS caudales y rige el menor. No escribe borde libre: la primera es la cuneta LLENA. La hoja de ruta (Fase 10, punto 2) dice «capacidad admisible con borde libre» sin dar el borde libre; ver el campo `borde_libre_m` del criterio 'seccion_cuneta'.

> **`MC_HHD.4.1.2.1a#CONDICION`** — Es el cierre del SEGUNDO procedimiento de la pagina (el de las ecuaciones (4.2) o (4.5)); el primero, en la impresa 176-177 (PDF 179-180), cierra con la misma condicion y «volver al paso 1». La condicion compara la CAPACIDAD de la cuneta con el caudal de APORTE del apartado b) —«el caudal calculado en el área de aporte correspondiente a la longitud de cuneta»—: es la verificacion VB2 de la Fase 10. La desigualdad es estricta; el programa la evalua con la tolerancia numerica del proyecto.

> **`MC_HHD.4.1.2.1a#MANNING`** — La ecuacion, vista en imagen: «Q = A x V = (A x Rh^2/3 x S^1/2) / n   (117)», con Rh = A/P «(área de la sección entre el perímetro mojado)» y S la «Pendiente del fondo (m/m)».

> **`MC_HHD.4.1.2.1a#VELOCIDAD`** — Vistas en imagen (PDF 178-179): (4.2) y (4.5) «Rh = (nv / √S)^3/2», el radio hidraulico con el que la velocidad de Manning es la admisible; es Manning despejado y vale para cualquier seccion. LAS OTRAS CUATRO NO SE USAN, y es deliberado: (4.1) «Rh = 5x√H / 6», (4.3) «A = 5H²/4», (4.4) «Rh = Hx√13 / 10» y (4.6) «A = 13H²/12», escritas para taludes «1:2 y 1:2» y «1:1.5 y 1:1.5», no reproducen la geometria que nombran: con los dos taludes 1:2 (V:H) el area de la seccion triangular de profundidad H es 2·H² y su radio hidraulico H/√5, y (4.1) no es siquiera dimensionalmente un radio. El programa calcula A, P y Rh de la geometria declarada. El procedimiento de la pagina --«Elijo una altura H, que sea menor a 0.60m»-- acota la profundidad de la ventana de 'seccion_cuneta'.

> **`MC_HHD.4.1.2.1b`** — La expresion, vista en imagen: Q = C·I·A / 3.6, con Q en m3/s, «C : Coeficiente de escurrimiento de la cuenca», «A : Área aportante en Km2» e «I : Intensidad de la lluvia de diseño en mm/h». Es la ecuacion (28) del num. 3.12.2 con el 0,278 escrito como 1/3.6. La pagina le imprime DOS numeros de ecuacion, (118) y (147): no se cita por numero.

> **`MC_HHD.4.1.2.1c#T34`** — El apartado c), en la pagina anterior: «Las dimensiones serán fijadas de acuerdo a las condiciones pluviales. De elegir la sección triangular, las dimensiones mínimas serán las indicadas en la Tabla Nº 34.» Cuatro regiones por precipitacion anual: seca (<400 mm/año) 0.20 x 0.50 m; lluviosa (400 a <1600) 0.30 x 0.75; muy lluviosa (1600 a <3000) 0.40 x 1.20; muy lluviosa (>3000) 0.30* x 1.20, «* Sección Trapezoidal con un ancho mínimo de fondo de 0.30». Son MINIMOS: la tabla no fija la seccion, fija su piso. La Figura Nº 28 (pag. impresa 179) repite la tabla. Transcripcion entera: `TablaNormativa` MC_HHD.T34.

> **`MC_HHD.4.1.2.1d`** — NOR-HID-02, cerrado en sus DOS extremos. (1) LA PAGINA: el repositorio citaba la impresa 178, que trae la TABLA Nº 34 de dimensiones minimas del apartado c); el apartado d) esta en la 179. (2) EL CARACTER: las dos cifras NO tienen la misma fuerza. El 250 es «será ... como máximo», exigencia con valvula de escape expresa («deberán justificarse técnicamente»); el 200 es «se recomienda reducir», recomendacion pura. Tratarlas como un dict de topes duros equivalentes borra la diferencia. Ademas la fuente nombra solo DOS regimenes en este apartado y deja sin longitud el regimen «lluvioso» intermedio de su propia Tabla Nº 34.

> **`MC_HHD.4.1.2.1d#ALIVIO`** — La primera frase del apartado d), antes de las dos longitudes maximas (MC_HHD.4.1.2.1d). El Manual nombra SOLO las alcantarillas de alivio como desagüe de la cuneta: que una obra de Familia A cierre el tramo lo sostiene el DG-2018 (DG2018.304.11#DESAGUE), no esta frase.

> **`MC_HHD.4.1.2.1e`** — Sigue: «o cuando el terreno es muy permeable que permite la filtración hacia el pavimento ... Se recomienda un revestimiento de concreto f´c = 175 kg/cm2 y espesor de 0.075m.» Es lo que sostiene el valor «concreto» del criterio 'revestimiento_cuneta', junto al primer parrafo del num. 4.1.2.1 (las cunetas «serán de concreto vaciadas en el sitio, prefabricados o de otro material resistente a la erosión»).

> **`MC_HHD.4.1.2a`** — Remite a la Tabla Nº 02 (num. 3.6, pag. impresa 25, PDF 28: «VALORES MAXIMOS RECOMENDADOS DE RIESGO ADMISIBLE DE OBRAS DE DRENAJE»), que da RIESGO admisible en %, no periodo de retorno, y deja la vida util en su nota (**). Dos de sus filas tocan el agua de la cuneta: «Alcantarillas de paso quebradas menores y descarga de agua de cunetas», R 35 % con n = 15 años (T = 35.32 años por la ecuacion R = 1 − (1 − 1/T)^n), y «Drenaje de la plataforma (a nivel longitudinal)», R 40 % con n = 15 años (T = 29.87 años). La nota de la tabla: «El Propietario de una Obra es el que define el riesgo admisible de falla y la vida útil de las obras». Cual se usa para la cuneta es la `interpretacion` de esta cita.

> **`MC_HHD.4.1.2c`** — Desigualdades ESTRICTAS. Es del drenaje longitudinal entero, no solo de la cuneta. EL DG-2018 DICE OTRA COSA DEL MINIMO: num. 304.11 (pag. impresa 208, PDF 209), «Las pendientes longitudinales mínimas absolutas serán 0.2%, para cunetas revestidas y 0.5% para cunetas sin revestir». El programa no elige entre las dos: la pendiente de la cuneta es un dato del trazo y la Fase 10 AVISA cuando cae fuera de la banda del Manual, nombrando la del DG-2018.

> **`MC_HHD.LAMINA_01`** — Es un plano, leido sobre la pagina renderizada. Cinco esquemas: a) siguiendo la pendiente natural del cauce; b) entrada bajo la pendiente natural; c) salida sobre la pendiente natural; d) entrada bajo y salida sobre la pendiente natural; e) pendientes pronunciadas (con muro y anclaje). En a) el conducto va de cabezal a cabezal sobre el fondo del cauce y los taludes del terraplen mueren en la coronacion de los cabezales. En c) y d) la salida queda POR ENCIMA del cauce, con dos notas del propio plano: «la posibilidad de dejar el tubo en voladizo debe ser analizada estructuralmente. El terreno a la salida debe ser roca u otro material resistente a la erosión» y «alcantarillas pequeñas pueden descargar con seguridad sobre un talud de enrocado». NO ACOTA NINGUNA DIMENSION: ni el desnivel de la salida ni la longitud. Sostiene que una salida elevada sobre el fondo del receptor exige proteccion, y por eso el desnivel de entrega no es conservador en un solo sentido.

> **`MC_HHD.LAMINA_02`** — ES UNA FIGURA, leida por imagen: «SECCIÓN TÍPICA DE ALCANTARILLA TIPO TMC CON PROTECCIÓN DE ENTRADA Y SALIDA». Rotula el «REVESTIMIENTO DE PIEDRA EMBOQUILLADA» del cauce, la «UÑA» al pie y la «PROTECCION DE DESCARGA» sobre «AFIRMADO COMPACTADO». Las dimensiones van como LETRAS (g, i, j, m, n, p, q) y la lamina no trae la tabla que les de valor: no fija ninguna medida. La Lámina 02-A (pag. impresa 208, PDF 211) añade la «ENTRADA TIPO CAJA RECEPTORA» y las salidas con y sin aleros, tambien con letras; la Lámina 03 (pag. impresa 209, PDF 212) rotula «CON PROTECCIÓN A LA ENTRADA Y SALIDA», con todas las cotas «VARIABLE».

> **`MC_HHD.LAMINA_02A`** — ES UNA FIGURA, leida por imagen: «SECCION TÍPICA DE ALCANTARILLA TIPO TMC CON PROTECCIÓN DE ENTRADA Y SALIDA», Lamina 02-A. Dibuja TRES remates: «ENTRADA TIPO CAJA RECEPTORA» (planta), «SALIDA TIPO CABEZAL CON ALEROS - PLANTA» -- el angulo de los aleros va acotado como «VARIABLE» -- y «SALIDA TIPO CABEZAL SIN ALEROS». Delante del cabezal, «LOSA INFERIOR» y, al borde de la proteccion, «UÑA». Todas las dimensiones son LETRAS (a, b, c, d, e, f, g, h, i, j, k, m, n, q, w) sin tabla de valores: la lamina respalda los TIPOS de remate, no sus medidas ni el angulo.

> **`MC_HHD.LAMINA_04`** — ES UNA FIGURA, leida por imagen: «PERFIL LONGITUDINAL Y SECCIÓN TÍPICAS DE ALIVIADERO CON DISIPADOR DE ENERGÍA HIDRÁULICA, A LA SALIDA DE ALCANTARILLAS». A diferencia de las Láminas 02, 03 y 05, ESTA SI LLEVA COTAS: escalones de concreto ciclopeo de 1.00 m de alto, losa de 0.15 m sobre 0.20 m de relleno granular, muros de 0.20 m en la corona y 0.30 m en la base (Sección B-B), tubos de drenaje perforados Ø4", y un dentellon final de «0.80 min.» de profundidad y 0.40 m de ancho. Las longitudes de los tramos van como «VARIABLE». Es el detalle tipico de una medida que el programa no dimensiona.

> **`MC_HHD.LAMINA_04#DENTELLON`** — ES UNA FIGURA, leida por imagen: «PERFIL LONGITUDINAL Y SECCIÓN TÍPICAS DE ALIVIADERO CON DISIPADOR DE ENERGÍA HIDRÁULICA, A LA SALIDA DE ALCANTARILLAS». Al pie del ultimo escalon dibuja un dentellon de concreto ciclopeo acotado «0.80 min.» de profundidad y «0.40m» de ancho; las losas, «0.15m» de concreto sobre «0.20m» de relleno granular. DESDE DONDE SE MIDE (correcciones de T-7a, H3; releida a 250 y 400 ppp): la linea de cota superior del «0.80 min.» arranca en la superficie del TERRENO NATURAL junto al borde del dentellon, que alli coincide con la cara inferior del paquete losa + relleno granular; la inferior, en la base del dentellon. No se mide desde la cara superior de la losa: desde ella la profundidad dibujada es del orden de 1.15 m (0.80 + 0.15 + 0.20). Es la UNICA lamina del Manual que acota un dentellon (la 03 no acota nada: `SIN_COTAS_LAMINA_03`; la 02 y la 02-A, con letras). Es de un ALIVIADERO, no de una losa de entrega: usarla para el dentellon del cabezal es una analogia, y el criterio que la aplica es [N→] y lo declara.

> **`MC_HHD.LAMINA_05`** — ES UNA FIGURA, leida por imagen: «SECCIÓN TÍPICA DE CRUCE DE ALCANTARILLA CON ENROCADO DE PROTECCION A LA SALIDA». Dibuja el enrocado sobre el talud de salida hasta el fondo del cauce, y bajo el dos capas ROTULADAS: «FILTRO» y «CAMA DE APOYO». NO TRAE NINGUNA DIMENSION: los taludes van como «H:V» y las dos cotas del pie como «VARIABLE». El num. 4.1.1.3.7 c) la presenta con «En los Anexos: Lámina Nº 05, se aprecia una sección típica de alcantarilla con enrocado de protección a la salida» (pag. impresa 80). Lo unico que se le puede atribuir es que el enrocado tipico del Manual LLEVA filtro y cama de apoyo.

### Manual de Puentes  (`MP`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `MP.1.10#FIG_1_10A_LUZ_LIBRE` | Figura 1.10-a | «Figura 1.10-a Puentes Tipo Viga» | pág. impresa **73** · PDF 74 | definicion | 2026-09-22 · imagen renderizada |
| `MP.2.1.4.3.9` | 2.1.4.3.9 | «Aparatos de Apoyo» | pág. impresa **91** · PDF 92 | exigencia | 2026-08-28 · ambos |
| `MP.2.3.1.1.12.3#EXC_ESTATICA` | 2.3.1.1.12.3 | «Límites de Excentricidad» | pág. impresa **250** · PDF 251 | exigencia | 2026-09-12 · texto |
| `MP.2.3.2.5` | 2.3.2.5 | «Importancia Operativa» | pág. impresa **99** · PDF 100 | permiso | 2026-11-12 · texto |
| `MP.2.4.2.1#PESOS` | 2.4.2.1, Tabla 2.4.2.1-1 | «Cargas Muertas: DC, DW, y EV» | pág. impresa **102** · PDF 103 | permiso | 2026-11-12 · texto |
| `MP.2.4.2.2#SOBRECARGA` | 2.4.2.2 | «Cargas de Suelo: EH, ES, y DD» | pág. impresa **102** · PDF 103 | exigencia | 2026-08-28 · ambos |
| `MP.2.4.3.11.2#CLASE_F` | 2.4.3.11.2 | «Peligro Sísmico» | pág. impresa **121** · PDF 122 | exigencia | 2026-08-29 · texto |
| `MP.2.4.3.11.2.1.1` | 2.4.3.11.2.1.1, Tabla 2.4.3.11.2.1.1-1, fila F | «Definiciones de Clases de Sitio» | pág. impresa **122** · PDF 123 | definicion | 2026-08-29 · ambos |
| `MP.2.4.3.11.2.1.1#EXCEPCIONES` | 2.4.3.11.2.1.1, bloque «Excepciones» | «Definiciones de Clases de Sitio» | pág. impresa **122** · PDF 123 | exigencia | 2026-08-29 · texto |
| `MP.2.4.3.2.2.2` | 2.4.3.2.2.2 | «Camión de Diseño» | pág. impresa **104** · PDF 105 | definicion | 2026-11-12 · texto |
| `MP.2.4.3.2.2.3` | 2.4.3.2.2.3 | «Tándem de Diseño» | pág. impresa **104** · PDF 105 | definicion | 2026-11-12 · texto |
| `MP.2.4.3.2.2.5` | 2.4.3.2.2.5 | «Área de Contacto de los Neumáticos» | pág. impresa **104** · PDF 105 | definicion | 2026-11-12 · texto |
| `MP.2.4.3.2.2.6` | 2.4.3.2.2.6 | «Presencia Múltiple de Sobrecargas» | pág. impresa **105** · PDF 106 | exigencia | 2026-11-12 · texto |
| `MP.2.4.3.3.2` | 2.4.3.3.2 | «Componentes Enterrados» | pág. impresa **109** · PDF 110 | exigencia | 2026-11-12 · texto |
| `MP.2.4.3.8.2` | 2.4.3.8.2 | «Subpresiones» | pág. impresa **113** · PDF 114 | exigencia | 2026-08-28 · texto |
| `MP.2.4.4.1.5.3` | 2.4.4.1.5.3 | «Coeficiente de Empuje Lateral Activo, ka» | pág. impresa **135** · PDF 136 | permiso | 2026-09-20 · texto |
| `MP.2.4.5.2#EV` | 2.4.5.2 | «Cargas y Denominación de las Cargas» | pág. impresa **140** · PDF 141 | definicion | 2026-08-28 · texto |
| `MP.2.4.5.3.1#MINIMO` | 2.4.5.3.1 | «Factores de Carga y Combinaciones de Carga» | pág. impresa **142** · PDF 143 | exigencia | 2026-08-28 · texto |
| `MP.2.8.1.1.14.1#EXC` | 2.8.1.1.14.1 | «Generalidades» | pág. impresa **253** · PDF 254 | exigencia | 2026-09-12 · texto |
| `MP.2.8.1.1.14.2.1#ROCA` | 2.8.1.1.14.2.1 | «Caracterización de la Aceleración en la Base del Muro de Contención» | pág. impresa **254** · PDF 255 | exigencia | 2026-09-12 · ambos |
| `MP.A.11.3.1#KAE` | A.11.3.1, ec. A.11.3.1-2 | «Método de Mononobe -Okabe» | pág. impresa **586** · PDF 587 | aproximacion | 2026-09-12 · ambos |
| `MP.GLOSARIO#OBRAS_DE_ARTE_MENORES` | Glosario | «GLOSARIO DE TERMINOS» | pág. impresa **45** · PDF 46 | definicion | 2026-09-22 · ambos |
| `MP.INTRODUCCION#LRFD_2014` | Introducción al Manual de Puentes | «INTRODUCCIÓN AL MANUAL DE PUENTES» | pág. impresa **43** · PDF 44 | permiso | 2026-09-20 · ambos |
| `MP.T2.4.3.11.2.1.2-1` | Tabla 2.4.3.11.2.1.2-1 | «Efectos de Sitio» | pág. impresa **123** · PDF 124 | exigencia | 2026-08-28 · imagen renderizada |
| `MP.T2.4.5.3.1-1` | 2.4.5.3.1, Tabla 2.4.5.3.1-1 | «Factores de Carga y Combinaciones» | pág. impresa **143** · PDF 144 | exigencia | 2026-08-28 · texto |
| `MP.T2.4.5.3.1-2` | 2.4.5.3.1, Tabla 2.4.5.3.1-2 | «Factores de Carga y Combinaciones» | pág. impresa **143** · PDF 144 | exigencia | 2026-08-28 · texto |
| `MP.T2.9.1.5.5.3-1` | 2.9.1.5.5.3, Tabla 2.9.1.5.5.3-1 | «Recubrimiento de Concreto» | pág. impresa **377** · PDF 378 | exigencia | 2026-08-28 · texto |

> **`MP.1.10#FIG_1_10A_LUZ_LIBRE`** — Rotulo de la figura, leido sobre la pagina renderizada: la cota «C = LUZ LIBRE» va entre el PILAR N° 1 y el PILAR N° 2 --un solo vano--, mientras «L = LONGITUD» cubre todo entre estribos y «L1, L2 = LUZ DE TRAMO» van entre ejes de apoyo. Es la unica definicion de luz libre del Manual de Puentes, y es POR VANO: bajo esta lectura un marco de tres celdas de 2.5 m tiene luz libre 2.5 m. La parte EN CONTRA de DIS-LUZ-DENOMINACION.

> **`MP.2.1.4.3.9`** — NOR-PUE-01 / MAT-D5. ESTE NUMERAL NO SOSTIENE LA SOBRECARGA DE TRASDOS y esta aqui para que se vea que no la sostiene. No contiene la palabra «sobrecarga», ni «trasdós», ni «relleno equivalente», ni el valor 0.60: va de aparatos de apoyo (bearings), y su contexto lo confirma (2.1.4.3.7 Drenaje, 2.1.4.3.8 Pavimentación, 2.1.4.3.9 Aparatos de Apoyo, 2.1.5 Señalización). El texto que si sostiene la sobrecarga esta en el num. 2.4.2.2 — ver MP.2.4.2.2#SOBRECARGA. El numeral falso estaba propagado a seis puntos del repositorio.

> **`MP.2.3.1.1.12.3#EXC_ESTATICA`** — EL NUMERAL SE CITA COMO LO IMPRIME, CON SU ERRATA: un 3 donde la serie pide un 8. En la misma pagina impresa 250 conviven «2.3.1.1.12.3 Límites de Excentricidad» y «2.3.1.1.12.4 Erosión Subsuperficial» (la errata alcanza a los dos sufijos) con «2.8.1.1.12.5 Resistencia Pasiva» y «2.8.1.1.12.6 Deslizamiento», ya en la serie correcta; el indice (PDF 21) repite las dos erratas. Ver DIS-MP-NUMERAL-2.3.1.1.12.3. La frase transcrita es ademas la traduccion CORRECTA de «middle two-thirds» en el numeral ESTATICO -- el hecho que sostiene el por_que de DIS-MP-EXCENTRICIDAD: el Manual sabe traducir el giro y solo lo degrada en el numeral sismico --. El «dentro los» sin «de» es de la fuente. Dos parrafos mas abajo la misma pagina dice «dentro del medio central del ancho de la base» para el mismo caso de suelo: tension interna de la fuente, que se deja anotada y no se resuelve aqui.

> **`MP.2.3.2.5`** — Para resistencia: eta_I >= 1.05 criticos o esenciales, = 1.00 tipicos, >= 0.95 de relativa menor importancia (misma pagina). AASHTO 12.5.4 lo aplica a las estructuras enterradas.

> **`MP.2.4.2.1#PESOS`** — Tabla 2.4.2.1-1 «Pesos específicos» (3.5.1-1 AASHTO), en kcf: «Arena, limo o arcilla compactado 0.120» y «Superficies de desgaste bituminosos 0.140» (igual que «Laminados grava, macadam, o de lastre»). PERMISO, no exigencia: rige a falta de informacion precisa, y el relleno de este proyecto no la tiene.

> **`MP.2.4.2.2#SOBRECARGA`** — EL 0.60 ES UN PISO, NO UN VALOR DE DISEÑO: la fuente dice «no menor que». Y esta expresado como ALTURA DE RELLENO EQUIVALENTE, no como presion: el paso a p = γ·0.60·Ka es derivacion del proyectista, correcta pero no escrita en este numeral. El titulo del numeral nombra EH, ES y DD y NO incluye LS.

> **`MP.2.4.3.11.2#CLASE_F`** — LA SEGUNDA VIA, INDEPENDIENTE DE LA NOTA 2 DE LA TABLA. La segunda condicion de la lista es «Si el sitio está clasificado como sitio clase F (Articulo. 2.4.3.11.2.1.1) (3.10.3.1 AASHTO).», y el verbo es «sera usado», imperativo. De modo que la exigencia de estudio para la Clase F esta DOS veces en el Manual -- aqui en el articulado y en la Nota 2 de las tres tablas de factores -- y ninguna de las dos admite dispensa. Barrido completo: «sitio clase F» aparece 4 veces en las 673 paginas (esta y las tres Notas 2); no hay ninguna salvedad por periodo fundamental corto. La quinta aparicion de «clase F» en el Manual es ACERO ASTM A668 Clase F (pag. impresa 289) y no guarda relacion: es la tercera homonimia de «Clase F» del corpus, junto al concreto Clase F de EG-2013 (NOR-VOC-04).

> **`MP.2.4.3.11.2.1.1`** — LA TRADUCCION ES FIEL: las tres categorias son las mismas de AASHTO -- turbas o arcillas altamente organicas (H > 10 ft), arcillas de alta plasticidad (H > 25 ft con PI > 75), estratos de arcillas de buen espesor blandas o semirrigidas (H > 120 ft) -- y el «tales como» traduce el «such as», de modo que la lista queda abierta tambien aqui. TAMPOCO nombra la licuefaccion. El Manual la trata en otros sitios -- num. 2.4.3.11.1, 2.8.0.3, 2.8.2.1.1.1, 2.8.2.1.1.3, 2.8.2.1.1.6.2 y Apendice A11 --, once apariciones en ocho paginas, y NINGUNA en este numeral ni en su tabla. No existe en el Manual un solo numeral titulado «Licuefaccion».

> **`MP.2.4.3.11.2.1.1#EXCEPCIONES`** — LA MISMA PROHIBICION QUE AASHTO, Y MAS DURA: donde AASHTO dice «should not be assumed», el Manual escribe «NO SERAN SUPUESTAS». La norma nacional endurece la traduccion, de modo que por la Via 1 (AASHTO) o por la Via 2 (Manual) el resultado es el mismo y el expediente no puede elegir la version blanda. «Entidaddetermine», sin espacio, es errata del impreso y se transcribe tal cual (T21). DOS PUERTAS Y UN DEBER: la prohibicion cede si la Entidad determina la clase -- via autonoma, sin dato geotecnico -- o si la establecen datos geotecnicos; y la oracion anterior manda «se emprenderá una investigación de sitio suficiente para definir su clase». Este expediente no tiene ninguna de las dos puertas abiertas y si tiene el deber pendiente.

> **`MP.2.4.3.2.2.2`** — El eje del camion HL-93 en la unidad primaria del Manual, 32.0 kip; el «(14.55 t.)» es una equivalencia redondeada. Para la carga sobre una alcantarilla la separacion que gobierna es la MINIMA, 14.0 ft, que es la que acerca los ejes.

> **`MP.2.4.3.2.2.6`** — La frase introduce el uso obligatorio de la Tabla 2.4.3.2.2.6-1 con UN carril cargado: «1 | 1.20» (misma pagina).

> **`MP.2.4.3.3.2`** — Sigue la ec. 2.4.3.3.2-1 (3.6.2.2-1 AASHTO): IM = 33(1.0 - 0.125 D_E) >= 0 %, con «D_E = profundidad mínima de la cubierta de tierra sobre la estructura (ft)». El Manual conserva los PIES: la pendiente en SI es 0.125/0.3048 por metro (IM_ENTERRADO_PENDIENTE_SI).

> **`MP.2.4.3.8.2`** — SU AMBITO ES NEUTRO RESPECTO DE LA FORMA y por eso el marco entra DIRECTO, sin analogia que declarar: dice «todos los componentes de la estructura», no «la tuberia». DEFINE LA FUERZA U y nada mas: no fija estado limite, ni combinacion, ni criterio de aceptacion. La desigualdad que V7 evalua NO sale de aqui -- ver el `por_que` de F5.V7 --. El «2.4.3.8.1» al que remite es el empuje hidrostatico general, del que esta es la componente vertical.

> **`MP.2.4.4.1.5.3`** — ES COULOMB (3.11.5.3 AASHTO): ka = sen²(θ + φ'f) / [r·sen²θ·sen(θ − δ)], con r = [1 + √(sen(φ'f + δ)·sen(φ'f − β) / (sen(θ − δ)·sen(θ + β)))]², ecs. 2.4.4.1.5.3-1 y -2 (PDF 136); la simbologia (Figura 2.4.4.1.5.3-1, «empuje activo de Coulomb») y la Tabla 2.4.4.1.5.3-1 de δ estan en la PDF 137 (pag. impresa 136). θ es el angulo de la cara posterior del muro con la HORIZONTAL y β el del relleno con la horizontal: en la formulacion de M9 (Mononobe-Okabe con k_h = k_v = 0) el trasdos se mide desde la VERTICAL (β_M9 = 90° − θ) y el talud del relleno es i (= β del Manual); la identidad entre las dos escrituras es exacta y la recalcula el bloque __main__ de tests/fixtures/casos_patron.py (CP-9, bloque C). Con θ = 90°, δ = 0 y β = 0 se reduce a tan²(45 − φ/2), la forma que la v8 §9.2 escribia (DIS-HR-KA-COULOMB, resuelta en EXT-0). El «se puede tomar» es PERMISO: la fuente ofrece la expresion, no la impone; el proyecto la adopta como coeficiente estatico por homogeneidad con el sismico (EXT-M-06).

> **`MP.2.4.5.2#EV`** — LO QUE LA DEFINICION NO DICE, y hay que decirlo porque el proyecto lo da por supuesto: no aparecen las palabras «sobre», «encima» ni «cobertura». Que EV sea el relleno que descansa SOBRE la estructura es una lectura -- razonable y estandar, y sostenida por la fila «enterrada» que se elige, no por esta frase --. Se transcribe el predicado y no la linea entera («EV = presion...») porque la tabla de simbolos separa el simbolo del texto y el volcado los reordena.

> **`MP.2.4.5.3.1#MINIMO`** — ES EL ESLABON QUE FALTABA, y faltaba entero: es lo que AUTORIZA a V7 a minorar EV y DC. Sin esta frase, tomar el extremo minimo de la fila de gamma_p seria una eleccion del proyectista sin respaldo; con ella es lo que la fuente manda hacer cuando la carga permanente ESTABILIZA, que es exactamente el caso de la flotacion. El titulo del numeral se imprime en la pag. impresa 140 (PDF 141) y el texto en la 142 (PDF 143): por eso `pagina_pdf_titulo`.

> **`MP.2.8.1.1.14.1#EXC`** — «tercio central» donde AASHTO 11.6.5.1 escribe «middle two-thirds»: es la frase que DIS-MP-EXCENTRICIDAD declara errata de traduccion -- el mismo parrafo traduce bien «ocho décimas» (eight-tenths), y el numeral estatico de tres paginas antes traduce bien los dos tercios --. El encabezado «2.8.1.1.14.1  Generalidades (11.6.5.1 AASHTO)» se imprime al pie de la pag. impresa 252 (PDF 253) y la frase esta en la 253 (PDF 254).

> **`MP.2.8.1.1.14.2.1#ROCA`** — LA FRASE CONTIENE LAS DOS MITADES DE DIS-MP-KH0-ROCA: la prosa correcta («estará basado en 1.2 veces el coeficiente...») y el parentesis mal compuesto, con el 1.2 del lado IZQUIERDO de la igualdad -- confirmado sobre la imagen renderizada, por eso el metodo es AMBOS; en el impreso el «=» va compuesto a nivel de subindice y hay salto de linea entre «1.2» y «kh0»; la transcripcion lineal es fiel --. El rotulo de remision debajo del titulo imprime «(11.6.5.2.1AASHTO)» sin espacio. Que el lado correcto sea k_h0 = 1.2·F_pga·PGA lo dice AASHTO 11.6.5.2.1, no este parentesis: por eso gana la prosa (ver la discrepancia).

> **`MP.A.11.3.1#KAE`** — EL CORCHETE DEL DENOMINADOR IMPRIME «[1 −√ ...]^-2», SIGNO MENOS: trazo horizontal unico, sin trazo vertical, decidido sobre la imagen renderizada a 6x -- es la errata de imprenta que DIS-MP-KAE-SIGNO declara; AASHTO imprime «[1 + raiz(...)]» y gana --. La etiqueta impresa de la ecuacion es «Donde (A.11.3.1-2. AASHTO)», con punto tras el 2. El espaciado del titulo, «Mononobe -Okabe» (espacio antes del guion, ninguno despues), es de la fuente y se conserva. Unidades imperiales (kcf, ft), como en el apendice AASHTO del que se transcribe.

> **`MP.GLOSARIO#OBRAS_DE_ARTE_MENORES`** — La magnitud que el glosario compara con los 6.00 m es la LUZ LIBRE de la obra, no el ancho del cauce que la obra salva. El glosario empieza en la pag. impresa 44 (PDF 45), donde imprime su titulo «GLOSARIO DE TERMINOS»; esta entrada esta en la 45 (PDF 46). Que es «luz libre» NO lo dice esta entrada: lo dibuja la Fig. 1.10-a (MP.1.10#FIG_1_10A_LUZ_LIBRE), por VANO.

> **`MP.INTRODUCCION#LRFD_2014`** — «AASTHO» y «Septima» sin tilde son de la fuente (sic). La Presentacion (PDF 42, impresa 41) lo repite: la actualizacion «se elaboró incorporando en gran parte las Especificaciones Técnicas de las Normas Americanas AASHTO LRFD, Septima Edición del año 2014». El registro cita la 9a ed. (2020) y la 10a (2024) esta publicada: el MP ancla la 7a y PERMITE las posteriores a «la entidad y/o propietario» --- no al proyectista, que propone ---, de modo que la eleccion entre 9a y 10a es tecnica (DIS-MP-LRFD-EDICION dice por que la 9a es admisible; cual rige es de 'edicion_que_rige_el_expediente').

> **`MP.T2.4.3.11.2.1.2-1`** — TRES DE SUS RASGOS SOLO SE VEN RENDERIZANDO, y los tres deciden una lectura: el signo `>` de la ultima columna, el asterisco de la fila F y el «1» del encabezado superior, que es la llamada a la Nota 1 y no un exponente.

> **`MP.T2.4.5.3.1-1`** — EL PROPIO MANUAL LA NOMBRA DE DOS FORMAS INCOMPATIBLES: el rotulo impreso sobre la tabla dice «Tabla 2.4.5.3.1-1» y el cuerpo del texto, en la pag. impresa 142, la llama «Tabla 2.4.5.3-1», sin el «.1». Se cita la forma del ROTULO, que es la que un revisor lee sobre la tabla que tiene delante.

> **`MP.T2.4.5.3.1-2`** — NOR-PUE-04: el repositorio afirmaba que el Manual «no transcribe la Tabla 3.4.1-1» y que los gamma eran un vacio declarado. Las dos afirmaciones eran falsas -- el Manual transcribe LAS DOS tablas, completas y con sus valores, dentro del rango de paginas que el propio archivo citaba --, y declarar un vacio sobre la pagina que trae la tabla es el defecto que Sec. 0.5 llama el mas grave.

> **`MP.T2.9.1.5.5.3-1`** — LO QUE EL TITULO DE LA TABLA DICE Y NADIE HABIA LEIDO -- y es la clave del cluster C07 --: «Recubrimiento para las armaduras principales de aceros NO PROTEGIDAS». La tabla peruana tiene UNA columna porque cubre UNA categoria de acero: la no protegida, que AASHTO llama Categoria A. El acero epoxico o galvanizado el Manual lo trata en un numeral aparte, el 2.9.1.5.5.4.

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

### WSDOT Hydraulics Manual (M 23-03)  (`WSDOT_HM`)

| id de la cita | Numeral | Título literal del numeral | Página | Carácter | Verificada |
|---|---|---|---|---|---|
| `WSDOT_HM.2-6.2#FRECUENCIA` | 2-6.2 | «Runoff Coefficients» | pág. impresa **2-8** · PDF 44 | exigencia | 2026-11-11 · texto |
| `WSDOT_HM.2-6.2#T2-2` | 2-6.2 | «Runoff Coefficients» | pág. impresa **2-9** · PDF 45 | definicion | 2026-11-11 · texto |
| `WSDOT_HM.2-6.3#TC_MINIMO` | 2-6.3 | «Time of Concentration» | pág. impresa **2-10** · PDF 46 | exigencia | 2026-11-11 · texto |
| `WSDOT_HM.3-3.5#10FTS` | 3-3.5 | «Velocities in Culverts: General» | pág. impresa **3-11** · PDF 76 | recomendacion | 2026-11-11 · texto |
| `WSDOT_HM.8-3.1#CONCRETO` | 8-3.1 | «Concrete Pipe» | pág. impresa **8-10** · PDF 225 | permiso | 2026-11-11 · texto |
| `WSDOT_HM.8-3.3#SEVERA` | 8-3.3 | «Thermoplastic Pipe: General» | pág. impresa **8-13** · PDF 228 | exigencia | 2026-11-11 · texto |
| `WSDOT_HM.8-4.3#ZONA_III` | 8-4.3 | «Corrosion Zone III» | pág. impresa **8-17** · PDF 232 | permiso | 2026-11-11 · texto |
| `WSDOT_HM.8-5.1#PH` | 8-5.1 | «pH» | pág. impresa **8-25** · PDF 240 | exigencia | 2026-11-11 · texto |
| `WSDOT_HM.8-5.2#RESISTIVIDAD` | 8-5.2 | «Resistivity» | pág. impresa **8-26** · PDF 241 | exigencia | 2026-11-11 · texto |
| `WSDOT_HM.T8-4` | Table 8-4 | «Pipe Abrasion Levels» | pág. impresa **8-27** · PDF 242 | definicion | 2026-11-11 · texto |

> **`WSDOT_HM.2-6.2#FRECUENCIA`** — La oracion anterior fija la base: «The coefficients in Table 2-2 are applicable for peak storms of 10-year frequency.» Y la siguiente el tope: «The runoff coefficient shall not be increased above 0.95, unless approved by the RHE.» La fuente nombra tres frecuencias (25, 50 y 100 años) y no dice que hacer entre ellas ni por encima de 100.

> **`WSDOT_HM.2-6.2#T2-2`** — Table 2-2: veintiseis coberturas por tres columnas de pendiente (Flat, Rolling 2%–10%, Hilly Over 10%). «Pavement and roofs» vale 0.90 en las tres; «Side slopes, earth» 0.60; «Side slopes, turf» 0.30; «Earth shoulders» 0.50. Son coeficientes para una tormenta de 10 años de periodo de retorno: ver WSDOT_HM.2-6.2#FRECUENCIA.

> **`WSDOT_HM.2-6.3#TC_MINIMO`** — El num. 2-6.4 «Rainfall Intensity» (pag. impresa 2-11, PDF 47) lo repite --«PEOs shall never use a time of concentration that is less than 5 minutes for intensity calculations»-- y da las dos razones: las curvas intensidad-duracion por debajo de ese tiempo son extrapolacion, y la lluvia tarda en generar escorrentia. Es una exigencia de WSDOT para SUS curvas; aqui cubre un vacio del Manual peruano (que no fija duracion minima, barrido entero) y entra como [C], no como norma.

> **`WSDOT_HM.3-3.5#10FTS`** — 10 ft/s = 3.048 m/s ES UMBRAL DE CONSULTA, NO PROHIBICION. El mismo numeral dice antes que las alcantarillas con velocidades «in the range of 3 to 10 feet per second (ft/s) tend to have fewer operational problems» y que fuera de ese rango hay que tratarlo con el ingeniero regional; y despues, que «Corrugated metal culverts may be designed with extra thickness to account for possible abrasion». Es el PISO de la ventana de 'v_max_tmc' [A]: por debajo de el la propia fuente no ve problema de abrasion que justifique un techo mas bajo.

> **`WSDOT_HM.8-3.1#CONCRETO`** — El numeral abre en la 8-9 (PDF 224) y la frase esta en la 8-10. Es lo que sostiene que la matriz de durabilidad NO excluya al concreto por pH ni por resistividad; lo que el concreto si recibe son REQUISITOS de mezcla y recubrimiento, y esos salen de la norma peruana (E.060 Tablas 4.2 y 4.4, Art. 4.4.2).

> **`WSDOT_HM.8-3.3#SEVERA`** — ES LA UNICA FRASE DEL MANUAL QUE PROHIBE UN MATERIAL POR ABRASION, y la prohibicion cuelga del NIVEL («severely abrasive conditions as described in Table 8-4»), no de una velocidad. La frase anterior del mismo parrafo dice lo contrario de lo que se esperaria de un material prohibido: «Laboratory testing indicates that the resistance of thermoplastic pipe to abrasive bed loads is equal to or greater than that of other types of pipe material»; la razon de la prohibicion es que no se puede REFORZAR. El mismo parrafo declara al termoplastico resistente a pH y resistividad y aceptable en las tres zonas de corrosion sin tratamiento. Sostiene 'v_max_hdpe' [C] y la regla de abrasion de la matriz de durabilidad (`M2.matriz_durabilidad`).

> **`WSDOT_HM.8-4.3#ZONA_III`** — LA ZONA III ES LA DE CORROSION SEVERA, y la misma pagina la describe con palabras que valen para un corredor costero de riego: «Low-lying roadways ... and coastal areas subjected to the influence of saltwater bays, marshes, and tide flats». La frase sigue en la 8-18: el aluminio se admite con las condiciones del §8-3. La Tabla 8-3 (pag. 8-25, PDF 240) lista las alternativas aceptables y no trae ningun tubo de acero.

> **`WSDOT_HM.8-5.1#PH`** — EL pH ES «soil or water pH» (primer parrafo del §8-5, misma pagina). Fuera de 5.0-8.5 solo valen los tubos de la Zona de Corrosion III, que el §8-4.3 y la Tabla 8-3 (misma pagina) limitan a concreto, termoplastico y aluminio: NINGUN tubo de acero. La pagina siguiente (8-26) repite el intervalo: «the acceptable range of 5.0 to 8.5». Es criterio de una agencia vial de EE. UU. --fuente tecnica reconocida, [C]--, no norma peruana: el umbral peruano es el de EG-2013 507.10 (pH < 5.8 exige proteger la tuberia), que no prohibe el material.

> **`WSDOT_HM.8-5.2#RESISTIVIDAD`** — La resistividad es «the measure of the ability of soil or water to pass electric current» (misma pagina): el dato puede ser del suelo o del agua, y rige el menor. Por debajo de 1 000 ohm-cm solo valen los materiales de la Zona III (concreto, termoplastico y aluminio): el acero corrugado queda fuera.

> **`WSDOT_HM.T8-4`** — LA TABLA OCUPA DOS PAGINAS: las tres primeras filas en la 8-27 (PDF 242) y la cuarta, «Severely abrasive», en la 8-28 (PDF 243). ES UNA TABLA DE NIVELES DE ABRASION, NO DE VELOCIDADES MAXIMAS: cada nivel se describe por tres caracteristicas del sitio (carga de fondo, pendiente y velocidad) y el `texto_literal` --el segundo parrafo del §8-6 «Abrasion», que la introduce-- dice que no hace falta que concurran las tres. Por eso tomar la velocidad sola como criterio suficiente de «severamente abrasivo» es una lectura que la fuente PERMITE y no impone (`Interpretacion` de la tabla). DEFINICION y no EXIGENCIA para la cita: los «shall» estan en las celdas de «Recommended Invert Protection» (mas calibre para el metal desde el nivel moderado), no en la clasificacion.

## 5. Tablas normativas

El rótulo de completitud **no lo escribe nadie**: lo deriva la tabla de
sus campos `alcance` y `uso`, de modo que no puede contradecirlos.

### `AASHTO_LRFD_9.T12.6.6.3-1` — Table 12.6.6.3-1—Minimum Cover

- Cita: `AASHTO_LRFD_9.T12.6.6.3-1`
- Tabla completa · el calculo usa 3 de 3 columnas y 5 de 14 filas
- **Afirmación negativa**: la Tabla 12.6.6.3-1 no tiene fila de alcantarilla CAJON DE CONCRETO -- ni vaciada in situ ni prefabricada --, y el Art. 12.11, que es el de los cajones de concreto, no fija altura minima de cobertura de suelo ni se remite al Art. 12.6.6.3. Ámbito barrido: las CATORCE filas de la tabla, leidas sobre la pagina RENDERIZADA (impresa 12-22, PDF 1660): sus dos filas de concreto dicen «Reinforced Concrete PIPE» y la unica que trae la palabra «box» es «Structural Plate Box Structures», que es METALICA y cuya celda de cobertura dice «1.4 ft. as specified in Article 12.9.1»: SI da cobertura, y ademas remite. ESTA FRASE DECIA «ni siquiera da cobertura» Y ERA FALSA SOBRE LA PROPIA PAGINA que este objeto existe para acreditar; lo encontro la auditoria adversarial de C7. El hecho negativo no cambia -- esa fila es metalica y no cubre a un marco de concreto --; lo que cambia es que se sostiene por lo que la fila ES y no por un vacio que no tiene. Mas el Art. 12.11 completo, «REINFORCED CONCRETE CAST-IN-PLACE AND PRECAST BOX CULVERTS AND REINFORCED CAST-IN-PLACE ARCHES», SIETE paginas impresas de la 12-68 a la 12-74, delimitadas por encabezado impreso (12.10.5 cierra antes; 12.12 «THERMOPLASTIC PIPES» abre en la 12-74) y leidas las siete renderizadas ademas del volcado. Censo dentro de ese ambito, insensible a mayusculas: «12.6.6» 0 veces, «12.6.6.3» 0, «table 12.6.6.3-1» 0, «fill height» 0, «depth of fill» 0, «soil cover» 0, «earth cover» 0; «minimum cover» 1, y es el titulo del falso amigo 12.11.5.4. «cover» 3: ese titulo mas DOS de los cuatro umbrales de metodo de «2.0 ft». «fill» 7: los otros DOS de esos umbrales, TRES «backfill» del num. 12.11.2.2.1 --donde H es «depth of backfill», la VARIABLE de la carga de tierra, sin cota inferior-- y el «compacted fill» / «uncompacted fill» del C12.11.2.2.1. EL REPARTO ANTERIOR DECIA «los cuatro umbrales y cinco backfill», que suma NUEVE y no los SIETE que el propio censo declara: lo encontro la auditoria adversarial de C7 remidiendo, y es el defecto propio de este objeto -- un barrido cuyo desglose no cuadra no acredita el hecho negativo, aunque los totales sean correctos, que lo eran --. Lo unico que remite hacia fuera es el paraguas generico del 12.11.1 -- «Designs shall conform to applicable Articles of these Specifications, except as provided otherwise herein» --, que no es la remision especifica a 12.6.6.3. Paginacion medida sobre encabezados impresos: pagina PDF 1-based = folio + 1638 (en indice 0-based, + 1637); comprobada en los folios 12-67, 12-68, 12-69 y 12-74
- Vistas de cálculo derivadas: `cobertura_minima_aashto`

| Fila | Type | Condition | Minimum Cover* | Uso |
|---|---|---|---|---|
| Corrugated Metal Pipe |  | — | S/8 ≥ 12.0 in. | usada |
| Spiral Rib Metal Pipe -- Steel Conduit |  | Steel Conduit | S/4 ≥ 12.0 in. | no usada |
| Spiral Rib Metal Pipe -- Aluminum Conduit where S ≤ 48.0 in. |  | Aluminum Conduit where S ≤ 48.0 in. | S/2 ≥ 12.0 in. | no usada |
| Spiral Rib Metal Pipe -- Aluminum Conduit where S > 48.0 in. |  | Aluminum Conduit where S > 48.0 in. | S/2.75 ≥ 24.0 in. | no usada |
| Structural Plate Pipe Structures |  | — | S/8 ≥ 12.0 in. | no usada |
| Long-Span Structural Plate Pipe Structures |  | — | -> | no usada |
| Structural Plate Box Structures |  | — | -> | no usada |
| Deep Corrugated Structural Plate Structures |  | — | -> | no usada |
| Fiberglass Pipe |  | — | 12.0 in. | no usada |
| Thermoplastic Pipe -- Under unpaved areas |  | Under unpaved areas | ID/8 ≥ 12.0 in. | usada |
| Thermoplastic Pipe -- Under paved roads |  | Under paved roads | ID/2 ≥ 24.0 in. | usada |
| Steel-Reinforced Thermoplastic Culverts |  | — | S/5 ≥ 12.0 in. | no usada |
| Reinforced Concrete Pipe -- Under unpaved areas or top of flexible pavement |  | Under unpaved areas or top of flexible pavement | Bc/8 or B'c/8, whichever is greater, ≥ 12.0 in. | usada |
| Reinforced Concrete Pipe -- Under bottom of rigid pavement |  | Under bottom of rigid pavement | 9.0 in. | usada |

> * Minimum cover taken from top of rigid pavement or bottom of flexible pavement

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

### `AASHTO_LRFD_9.T5.10.1-1` — Table 5.10.1-1—Minimum Cover for Main Reinforcing Steel (in.)

- Cita: `AASHTO_LRFD_9.T5.10.1-1`
- Tabla completa · el calculo usa 1 de 7 columnas y 2 de 21 filas
- Columna «A» transcrita y **no usada**: el calculo opera en SI y consume la columna en mm; la pulgada es la unidad IMPRESA y sin ella la conversion no se puede comprobar
- Columna «B» transcrita y **no usada**: idem cat_a_in
- Columna «C» transcrita y **no usada**: idem cat_a_in
- Columna «A (conversion del proyecto)»: **elección pendiente** (`COND-CATEGORIA-REFUERZO`) — el cálculo se detiene
- Columna «B (conversion del proyecto)»: **elección pendiente** (`COND-CATEGORIA-REFUERZO`) — el cálculo se detiene
- Columna «C (conversion del proyecto)»: **elección pendiente** (`COND-CATEGORIA-REFUERZO`) — el cálculo se detiene
- Vistas de cálculo derivadas: `tabla_recubrimiento_aashto_mm`

| Fila | Situation | A | B | C | A (conversion del proyecto) | B (conversion del proyecto) | C (conversion del proyecto) | Uso |
|---|---|---|---|---|---|---|---|---|
| Severe to Moderate Exposure -- Direct exposure to salt water |  | 4.0 | 2.5 | 2.5 | 101.6 | 63.5 | 63.5 | no usada |
| Severe to Moderate Exposure -- Cast against earth |  | 3.0 | 2.0 | 2.0 | 76.2 | 50.8 | 50.8 | usada |
| Severe to Moderate Exposure -- Coastal |  | 3.0 | 2.0 | 2.0 | 76.2 | 50.8 | 50.8 | usada |
| Severe to Moderate Exposure -- Exposure to deicing salts |  | 2.5 | 2.0 | 1.5 | 63.5 | 50.8 | 38.1 | no usada |
| Severe to Moderate Exposure -- Deck surfaces subject to tire stud or chain wear |  | 2.5 | 2.5 | 2.0 | 63.5 | 63.5 | 50.8 | no usada |
| Severe to Moderate Exposure -- Other than noted above |  | 2.0 | 2.0 | 1.5 | 50.8 | 50.8 | 38.1 | no usada |
| Limited Exposure -- Other than noted below -- Up to No. 11 bar |  | 1.5 | 1.0 | 1.0 | 38.1 | 25.4 | 25.4 | no usada |
| Limited Exposure -- Other than noted below -- No. 14 and No. 18 bars |  | 2.0 | 2.0 | 2.0 | 50.8 | 50.8 | 50.8 | no usada |
| Limited Exposure -- Bottom of cast-in-place slabs -- Up to No. 11 bar |  | 1.0 | 1.0 | 1.0 | 25.4 | 25.4 | 25.4 | no usada |
| Limited Exposure -- Bottom of cast-in-place slabs -- No. 14 and No. 18 bars |  | 2.0 | 2.0 | 2.0 | 50.8 | 50.8 | 50.8 | no usada |
| Limited Exposure -- Precast soffit form panels |  | 0.8 | 0.8 | 0.8 | 20.32 | 20.32 | 20.32 | no usada |
| Piling -- Precast reinforced piles -- Noncorrosive environments |  | 2.0 | 1.5 | 1.0 | 50.8 | 38.1 | 25.4 | no usada |
| Piling -- Precast reinforced piles -- Corrosive environments |  | 3.0 | 2.5 | 2.0 | 76.2 | 63.5 | 50.8 | no usada |
| Piling -- Precast prestressed piles |  | 2.0 | 1.0 | 1.0 | 50.8 | 25.4 | 25.4 | no usada |
| Piling -- Cast-in-place piles -- Noncorrosive environments |  | 2.0 | 1.5 | 1.5 | 50.8 | 38.1 | 38.1 | no usada |
| Piling -- Cast-in-place piles -- Corrosive environments |  | 3.0 | 2.5 | 2.0 | 76.2 | 63.5 | 50.8 | no usada |
| Piling -- Cast-in-place piles -- Shells |  | 2.0 | 1.5 | 1.0 | 50.8 | 38.1 | 25.4 | no usada |
| Piling -- Cast-in-place piles -- Auger-cast, tremie concrete, or slurry construction |  | 3.0 | 2.5 | 2.0 | 76.2 | 63.5 | 50.8 | no usada |
| Precast Culverts -- Top slabs used as a driving surface |  | 2.5 | 2.0 | 1.5 | 63.5 | 50.8 | 38.1 | no usada |
| Precast Culverts -- Top slabs with less than 2.0 ft of fill |  | 2.0 | 1.5 | 1.0 | 50.8 | 38.1 | 25.4 | no usada |
| Precast Culverts -- All other members |  | 1.0 | 1.0 | 1.0 | 25.4 | 25.4 | 25.4 | no usada |

>  Category A—Uncoated reinforcing steel meeting AASHTO M 31M/M 31

>  Category B—Epoxy coated or galvanized meeting ASTM A775/A775M

>  Category C—Materials meeting AASHTO M 334M/M 334

### `AASHTO_LRFD_9.TA12-11` — Table A12-11—PE Corrugated Pipes (AASHTO M 294)

- Cita: `AASHTO_LRFD_9.TA12-11`
- Tabla completa · el calculo usa 4 de 6 columnas y 3 de 8 filas
- Columna «Min. ID (in.)» transcrita y **no usada**: el diametro interior minimo es una tolerancia de producto que el catalogo no verifica
- Columna «Min. c (in.)» transcrita y **no usada**: la distancia a la fibra extrema solo entra en la deformacion combinada de flexion y empuje (AASHTO LRFD 12.12.3.10.2), que la Fase 8 difiere al expediente: el minimo de la tabla no describe la geometria del perfil que esa comprobacion necesita
- **Laguna de la fuente**: los tamaños nominales de 54 y 60 in (1350 y 1500 mm), que la serie de AASHTO M 294-11 SI incluye (num. 7.2.1, traduccion no oficial): la tabla termina en 48 in. Se cierra con: ninguna: no se extrapola el diametro exterior. 'espesor_pared_conducto' no declara esas dos filas para el HDPE y `M2.espesor_pared` detiene el material en ese escalon con DatoFaltanteError, nombrando la fila que falta (`criterios_adoptados['espesor_pared_conducto']`)
- **Interpretación del proyectista, no de la fuente**: «Max. OD» se lee como el techo del diametro exterior del producto: el t que 'espesor_pared_conducto' declara para el HDPE es el que hace D + 2t = Max. OD sobre el diametro DESIGNADO del catalogo (0.90, 1.05 y 1.20 m), no sobre el «Min. ID» de la fila
  - En contra: Es una tabla de PROPIEDADES para el diseño estructural (Apendice A12), no una especificacion de producto: el diametro exterior real lo fija el fabricante del perfil y puede ser menor.
  - En contra: El catalogo designa 900, 1050 y 1200 mm donde la fila dice 36, 42 y 48 in (914.4, 1066.8 y 1219.2 mm): el t declarado se mide desde el designado, de modo que es entre 7 y 10 mm mayor que (Max. OD - nominal)/2. Va del lado conservador en 7.A y en V7.
  - En contra: La cobertura minima de la Tabla 12.6.6.3-1 para termoplastico se entra con el diametro INTERIOR, de modo que este t no la mueve.
- Vistas de cálculo derivadas: `PE_M294_PERFIL_MINIMO`

| Fila | Nominal Size (in.) | Min. ID (in.) | Max. OD (in.) | Min. A (in.2/ft) | Min. c (in.) | Min. I (in.4/in.) | Uso |
|---|---|---|---|---|---|---|---|
| 12 | 12 | 11.8 | 14.7 | 1.5 | 0.35 | 0.024 | no usada |
| 15 | 15 | 14.8 | 18.0 | 1.9 | 0.45 | 0.053 | no usada |
| 18 | 18 | 17.7 | 21.5 | 2.3 | 0.5 | 0.062 | no usada |
| 24 | 24 | 23.6 | 28.7 | 3.1 | 0.65 | 0.116 | no usada |
| 30 | 30 | 29.5 | 36.4 | 3.9 | 0.75 | 0.163 | no usada |
| 36 | 36 | 35.5 | 42.5 | 4.5 | 0.9 | 0.222 | usada |
| 42* | 42 | 41.5 | 48.0 | 4.69 | 1.11 | 0.543 | usada |
| 48* | 48 | 47.5 | 55.0 | 5.15 | 1.15 | 0.543 | usada |

> * For the 42.0-in. and 48.0-in. pipe, the wall thickness should be designed using the long-term tensile strength provision, i.e., 900 psi, until new design criteria are established in the AASHTO bridge and structures specifications.

### `AASHTO_M170M.T5` — Table 5—Design Requirements for Class V Reinforced Concrete Pipe

- Cita: `AASHTO_M170M.T5`
- Tabla completa · el calculo usa 0 de 3 columnas y 0 de 27 filas
- Columna «Internal Designed Diameter, mm» transcrita y **no usada**: ningun modulo dimensiona hoy el tubo de concreto por clase D-load: la columna de diametros es el dorado de CP11 para `M2.siguiente_diametro` (contraste de la progresion contra la serie de la norma de producto, conflicto #7) y los espesores son el insumo de la verificacion pendiente de 'espesor_pared_conducto', que los leyo por imagen
- Columna «Wall Thickness, mm» transcrita y **no usada**: ningun modulo dimensiona hoy el tubo de concreto por clase D-load: la columna de diametros es el dorado de CP11 para `M2.siguiente_diametro` (contraste de la progresion contra la serie de la norma de producto, conflicto #7) y los espesores son el insumo de la verificacion pendiente de 'espesor_pared_conducto', que los leyo por imagen
- Columna «Wall Thickness, mm» transcrita y **no usada**: ningun modulo dimensiona hoy el tubo de concreto por clase D-load: la columna de diametros es el dorado de CP11 para `M2.siguiente_diametro` (contraste de la progresion contra la serie de la norma de producto, conflicto #7) y los espesores son el insumo de la verificacion pendiente de 'espesor_pared_conducto', que los leyo por imagen
- **Interpretación del proyectista, no de la fuente**: El ejemplar de normas/ conserva esta tabla como ESCANEO REAL (PDF 10, girado 90 grados) y las Tablas 1 a 4 como recomposiciones OCR cuya imagen trae digitos equivocados (371 por 375, 1390 por 1350, «3tS0», «6tXI») y filas superpuestas. Por eso la serie de diametros del concreto se toma de la Clase V: la serie designada es la misma en las cinco clases --la norma tabula por diametro y clase--, y es lo unico que el registro afirma de esta transcripcion.
  - En contra: las Tablas 1 a 4 (Clases I a IV) NO estan transcritas y no se puede comprobar contra ESTE ejemplar que sus filas de diametro coincidan con las de la Tabla 5; la coincidencia se apoya en que la norma tabula la misma serie designada por clase
  - En contra: la pagina PDF 11 (continuacion de la Tabla 5, rotada 180 grados) vuelve a ser OCR y no se transcribe
  - A favor: la Tabla 1 (Clase I, PDF 3), aun recompuesta, empieza en 1500 y termina en 3450/3600 con el mismo paso de 150 mm; la Tabla 3 (Clase III, PDF 6) empieza en 300 con el mismo paso de 75 mm
  - A favor: las trece celdas de pared B que 'espesor_pared_conducto' leyo por imagen de las Tablas 2 y 3 coinciden, de 900 a 1200 mm, con la columna B de esta tabla (100, 113, 125)

| Fila | Internal Designed Diameter, mm | Wall Thickness, mm | Wall Thickness, mm | Uso |
|---|---|---|---|---|
| 300 | 300 | 50 | 69 | no usada |
| 375 | 375 | 57 | 75 | no usada |
| 450 | 450 | 63 | 82 | no usada |
| 525 | 525 | 69 | 88 | no usada |
| 600 | 600 | 75 | 94 | no usada |
| 675 | 675 | 82 | 100 | no usada |
| 750 | 750 | 88 | 107 | no usada |
| 825 | 825 | 94 | 113 | no usada |
| 900 | 900 | 100 | 119 | no usada |
| 1050 | 1050 | 113 | 132 | no usada |
| 1200 | 1200 | 125 | 144 | no usada |
| 1350 | 1350 |  | 157 | no usada |
| 1500 | 1500 |  | 169 | no usada |
| 1650 | 1650 |  | 182 | no usada |
| 1800 | 1800 |  | 194 | no usada |
| 1950 | 1950 |  |  | no usada |
| 2100 | 2100 |  |  | no usada |
| 2250 | 2250 |  |  | no usada |
| 2400 | 2400 |  |  | no usada |
| 2550 | 2550 |  |  | no usada |
| 2700 | 2700 |  |  | no usada |
| 2850 | 2850 |  |  | no usada |
| 3000 | 3000 |  |  | no usada |
| 3150 | 3150 |  |  | no usada |
| 3300 | 3300 |  |  | no usada |
| 3450 | 3450 |  |  | no usada |
| 3600 | 3600 |  |  | no usada |

### `AASHTO_M294_TRAD.T7.2.2` — Espesor de pared

- Cita: `AASHTO_M294_TRAD.7.2.2`
- Tabla completa · el calculo usa 2 de 4 columnas y 0 de 12 filas
- Columna «Espesor de pared, mm (in.)» transcrita y **no usada**: ningun modulo consume el espesor minimo de la pared interior del HDPE: no es el t que separa D interior de D exterior que 'espesor_pared_conducto' necesita (la altura del perfil corrugado no esta en la fuente) y el proyecto no verifica hoy el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- Columna «Espesor de pared, mm (in.)» transcrita y **no usada**: ningun modulo consume el espesor minimo de la pared interior del HDPE: no es el t que separa D interior de D exterior que 'espesor_pared_conducto' necesita (la altura del perfil corrugado no esta en la fuente) y el proyecto no verifica hoy el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- **Afirmación negativa**: AASHTO M 294-11 (traducción no oficial) no contiene ninguna tabla de clase, calibre ni rigidez por altura de relleno o de cobertura: el num. 1.4 excluye expresamente camas, relleno y carga de cubierta de tierra y remite el diseño estructural a AASHTO LRFD Seccion 12. Lo unico que tabula por diametro es la rigidez MINIMA de tuberia al 5 % de deflexion (7.4), que es un requisito de producto, no una seleccion por altura. Ámbito barrido: las 17 hojas del ejemplar, leidas ENTERAS por texto (extraible y limpio) y las hojas 1, 5 y 8 tambien renderizadas: doce numerales de nivel 1 (Ámbito, Documentos mencionados, Terminología, Clasificación, Información para órdenes de compra, Materiales, Requerimientos, Acondicionamiento, Método de ensayo, Inspección y re-ensayo, Marcado, Aseguramiento de calidad), la Tabla 1 (perforaciones Clase 1), las tabulaciones de 7.2.2 (espesor de pared) y 7.4 (rigidez), el Anexo A1 y el Apéndice X1. Barrido por palabra: «cobertura» 0 apariciones; «relleno» 5, todas en 1.4 (la exclusion) o en 7.9.1 y 7.9.2 (el material de relleno frente a las uniones, no una altura); «cubierta» 2 (1.4 y «la tubería ... cubierta en esta especificación», 4.1); «altura» 3 (la H de las perforaciones en la Tabla 1 y 7.3.1, y la altura de caida del martillo en 9.3); «clase» solo para perforaciones y para la clasificacion de celda de la resina
- **Afirmación negativa**: AASHTO M 294-11 (traducción no oficial) no fija el diametro exterior ni la altura del perfil corrugado de ningun tamaño nominal: el tamaño nominal es el diametro INTERIOR (7.2.1), la tolerancia es del diametro interior (7.2.3), y el 7.2.2 tabula el espesor minimo de la pared interior lisa (Tipo S) o de las dos paredes (Tipo D), no la altura del perfil. El t que separa D interior de D exterior no sale de esta fuente. Ámbito barrido: las 17 hojas del ejemplar, por texto: «diámetro exterior» y «diámetro externo» dan cero apariciones; «exterior» aparece 7 veces (3.9 dos veces, 4.1.1, 4.1.3, 7.2.2, 9.4.2 y 9.7) y «externa/externo» 10, nombrando una pared, un valle, una carga, una grieta (3.8), unas fuerzas (9.6.3) o un laboratorio (A1.1), nunca una dimension; «espesor» aparece 5 veces (6 con «espesores»), en 7.2.2, en la Nota 4 de 9.4 (espesor de la probeta) y en 9.6.4; «perfil» 7 (1.4, el titulo de T 341 en 2.1, 6.1.1, dos en 7.7 y dos en 9.4.2), ninguna con una altura -- el 1.4 remite al fabricante «el detalle de la seción del perfil de la pared», que es exactamente el dato que la norma no fija --. Recuentos del verificador-normativo de N2 por palabra entera, sin distinguir mayusculas
- **Interpretación del proyectista, no de la fuente**: La columna de diametros es la serie cerrada de tamaños nominales de la norma de producto del HDPE, y su ultima fila (1500 mm) es el techo del ambito: por encima no hay producto M 294. Coincide con el tope de catalogo del HDPE (1.50 m) y con la progresion 0.90 + 0.15 m del proyecto de 900 a 1500
  - En contra: Es una TRADUCCION NO OFICIAL: acredita lo que la traduccion imprime, y el original en ingles no se ha leido. Sin firma posible (sin folio, T6).
  - En contra: Que la serie termine en 1500 mm dice que M 294-11 no cubre tamaños mayores, no que no existan tuberias de PE mayores bajo otra especificacion: el tope sigue siendo de catalogo.
  - En contra: Por debajo de 900 mm la serie tiene cinco tamaños (300 a 750) que el proyecto no recorre por el piso peruano del num. 4.1.1.3.4 a) del Manual, no por esta tabla.

| Fila | Diámetro, mm (in.) | Diámetro, mm (in.) | Espesor de pared, mm (in.) | Espesor de pared, mm (in.) | Uso |
|---|---|---|---|---|---|
| 300 (12) | 300 | 12 | 0.9 | 0.035 | no usada |
| 375 (15) | 375 | 15 | 1.0 | 0.04 | no usada |
| 450 (18) | 450 | 18 | 1.3 | 0.05 | no usada |
| 525 (21) | 525 | 21 | 1.5 | 0.06 | no usada |
| 600 (24) | 600 | 24 | 1.5 | 0.06 | no usada |
| 675 (27) | 675 | 27 | 1.5 | 0.06 | no usada |
| 750 (30) | 750 | 30 | 1.5 | 0.06 | no usada |
| 900 (36) | 900 | 36 | 1.7 | 0.07 | no usada |
| 1050 (42) | 1050 | 42 | 1.8 | 0.07 | no usada |
| 1200 (48) | 1200 | 48 | 1.8 | 0.07 | no usada |
| 1350 (54) | 1350 | 54 | 2.0 | 0.08 | no usada |
| 1500 (60) | 1500 | 60 | 2.0 | 0.08 | no usada |

### `AASHTO_M36.T1` — Table 1—Corrugation Requirements for Type I, IA, II, IIA, and III Pipe

- Cita: `AASHTO_M36.T1`
- Tabla completa · el calculo usa 1 de 6 columnas y 3 de 4 filas
- Columna «Nominal Size, mm» transcrita y **no usada**: tolerancia de FABRICACION de la corrugacion (paso maximo, profundidad minima, radio interior): el calculo no verifica el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- Columna «Maximum Pitch, mm» transcrita y **no usada**: tolerancia de FABRICACION de la corrugacion (paso maximo, profundidad minima, radio interior): el calculo no verifica el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- Columna «Minimum Depth, mm» transcrita y **no usada**: tolerancia de FABRICACION de la corrugacion (paso maximo, profundidad minima, radio interior): el calculo no verifica el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- Columna «Nominal, mm» transcrita y **no usada**: tolerancia de FABRICACION de la corrugacion (paso maximo, profundidad minima, radio interior): el calculo no verifica el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- Columna «Minimum, mm» transcrita y **no usada**: tolerancia de FABRICACION de la corrugacion (paso maximo, profundidad minima, radio interior): el calculo no verifica el producto contra su norma de fabricacion. Se transcribe integra porque una tabla podada no deja ver que se eligio una columna
- **Interpretación del proyectista, no de la fuente**: La altura total del perfil corrugado --lo que separa el diametro interior del exterior en cada lado-- es la profundidad NOMINAL de la corrugacion mas el espesor de la plancha: D_ext = D + 2 x (profundidad + espesor)
  - En contra: La norma no escribe esa suma: es geometria del proyecto sobre dos definiciones suyas (la profundidad de cresta a valle sobre una misma cara, nota b; el diametro nominal medido en la cresta interior, num. 8.1.1).
  - En contra: La profundidad real puede ser menor que la nominal: la tabla admite 12 mm de minimo donde el rotulo dice 13. Tomar la nominal da un diametro exterior mayor, que es el lado conservador en 7.A (clave mas alta) y en V7 (mas volumen desplazado).
  - En contra: En tuberia de corrugacion HELICOIDAL la circunferencia exterior depende del angulo de la helice (Nota 7 del num. 8.1.1); el diametro exterior en un corte perpendicular al eje sigue siendo el de esta suma.
  - A favor: ASTM A796 Table 5 se titula «... for Corrugation: 68 by 13 mm» y da r = 4.37 mm para 2.01 mm de espesor: un radio de giro de un tercio de la profundidad, que es lo que corresponde a un perfil de 13 mm de altura de onda.
- Vistas de cálculo derivadas: `TMC_PLANCHA_CORRUGADA`

| Fila | Nominal Size, mm | Nominal Size, mm | Maximum Pitch, mm | Minimum Depth, mm | Nominal, mm | Minimum, mm | Uso |
|---|---|---|---|---|---|---|---|
| 38 by 6.5 | 38 | 6.5 | 48 | 6.0 | 7 | 6.5 | no usada |
| 68 by 13 | 68 | 13 | 73 | 12 | 17 | 12 | usada |
| 75 by 25 | 75 | 25 | 83 | 24 | 14 | 12 | usada |
| 125 by 25 | 125 | 25 | 135 | 24 | 40 | 36 | usada |

> a Pitch is measured from crest to crest of corrugation, at 90 degrees to the direction of corrugation.

> b Depth is measured as the vertical distance from a straightedge resting on the corrugation crests parallel to the axis of the pipe to the bottom of the intervening valley. If the depth measurement of one or more corrugations is less than the value indicated herein, the depth of all corrugations between seams shall be measured, and the requirements of Table 2 shall be applied. (See Section 7.2.1.)

> c Minimum inside radius requirement does not apply to a corrugation containing a helical lock seam.

> d The corrugation size of 38 by 6.5 mm is available only in helically corrugated pipe.

### `AASHTO_M36.T6` — Table 6—Pipe Sizes

- Cita: `AASHTO_M36.T6`
- Tabla completa · el calculo usa 4 de 9 columnas y 0 de 31 filas
- Columna «38 by 6.5 mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «19 by 19 by 190 mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «19 by 25 by 292 mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «19 by 25 by 216 mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «Minimum Outside Circumference, mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Vistas de cálculo derivadas: `DIAMETROS_ESTANDAR_TMC`

| Fila | Nominal Inside Diameter, mm | 38 by 6.5 mm | 68 by 13 mm | 75 by 25 mm | 125 by 25 mm | 19 by 19 by 190 mm | 19 by 25 by 292 mm | 19 by 25 by 216 mm | Minimum Outside Circumference, mm | Uso |
|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 100 | X |  |  |  |  |  |  | 264 | no usada |
| 150 | 150 | X |  |  |  |  |  |  | 441 | no usada |
| 200 | 200 | X |  |  |  |  |  |  | 598 | no usada |
| 250 | 250 | X |  |  |  |  |  |  | 755 | no usada |
| 300 | 300 | X | X |  |  |  |  |  | 912 | no usada |
| 375 | 375 | X | X |  |  |  |  |  | 1148 | no usada |
| 450 | 450 | X | X |  |  | X | X | X | 1383 | no usada |
| 500 | 500 |  | X |  |  | X | X | X | 1620 | no usada |
| 600 | 600 |  | X |  |  | X | X | X | 1854 | no usada |
| 675 | 675 |  | X |  |  | X | X | X | 2091 | no usada |
| 750 | 750 |  | X |  |  | X | X | X | 2483 | no usada |
| 825 | 825 |  | X |  | X | X | X | X | 2561 | no usada |
| 900 | 900 |  | X | X | X | X | X | X | 2797 | no usada |
| 1050 | 1050 |  | X | X | X | X | X | X | 3269 | no usada |
| 1200 | 1200 |  | X | X | X | X | X | X | 3739 | no usada |
| 1350 | 1350 |  | X | X | X | X | X | X | 4209 | no usada |
| 1500 | 1500 |  | X | X | X | X | X | X | 4675 | no usada |
| 1650 | 1650 |  | X | X | X | X | X | X | 5142 | no usada |
| 1800 | 1800 |  | X | X | X | X | X | X | 5609 | no usada |
| 1950 | 1950 |  | X | X | X | X | X | X | 6075 | no usada |
| 2100 | 2100 |  | X | X | X | X | X | X | 6542 | no usada |
| 2250 | 2250 |  |  | X | X | X | X | X | 7008 | no usada |
| 2400 | 2400 |  |  | X | X | X | X | X | 7475 | no usada |
| 2550 | 2550 |  |  | X | X | X | X | X | 7941 | no usada |
| 2700 | 2700 |  |  | X | X | X | X | X | 8408 | no usada |
| 2850 | 2850 |  |  | X | X | X |  | X | 8874 | no usada |
| 3000 | 3000 |  |  | X | X | X |  | X | 9341 | no usada |
| 3150 | 3150 |  |  | X | X |  |  | X | 9807 | no usada |
| 3300 | 3300 |  |  | X | X |  |  | X | 10274 | no usada |
| 3450 | 3450 |  |  | X | X |  |  | X | 10740 | no usada |
| 3600 | 3600 |  |  | X | X |  |  | X | 11207 | no usada |

> a An “X” indicates standard corrugation sizes for each nominal diameter of pipe.

> b Rib sizes 19 by 19 by 190 mm and 19 by 25 by 292 mm.

> c Measured in valley of annular corrugations. Not applicable to helically corrugated pipe.

### `AASHTO_M36.T7` — Table 7—Thicknesses of Metallic-Coated Steel Sheet

- Cita: `AASHTO_M36.T7`
- Tabla completa · el calculo usa 2 de 7 columnas y 7 de 7 filas
- Columna «M 274 AlT2, Aluminum Coated» transcrita y **no usada**: el catalogo no distingue el tipo de recubrimiento metalico de la plancha: el material del proyecto es TMC GALVANIZADA (M 218, la primera columna) y elegir otro recubrimiento es una decision de durabilidad que la matriz de la Sec. 3.3 deja al proyectista
- Columna «M 289, 55 Percent Aluminum-Zinc Alloy Coated» transcrita y **no usada**: el catalogo no distingue el tipo de recubrimiento metalico de la plancha: el material del proyecto es TMC GALVANIZADA (M 218, la primera columna) y elegir otro recubrimiento es una decision de durabilidad que la matriz de la Sec. 3.3 deja al proyectista
- Columna «A 885, Zinc and Aramid Fiber Coated» transcrita y **no usada**: el catalogo no distingue el tipo de recubrimiento metalico de la plancha: el material del proyecto es TMC GALVANIZADA (M 218, la primera columna) y elegir otro recubrimiento es una decision de durabilidad que la matriz de la Sec. 3.3 deja al proyectista
- Columna «A 929M Zn-5 Al-MM, Alloy Coated» transcrita y **no usada**: el catalogo no distingue el tipo de recubrimiento metalico de la plancha: el material del proyecto es TMC GALVANIZADA (M 218, la primera columna) y elegir otro recubrimiento es una decision de durabilidad que la matriz de la Sec. 3.3 deja al proyectista
- Columna «A 929M AlT1, Aluminum Coated» transcrita y **no usada**: el catalogo no distingue el tipo de recubrimiento metalico de la plancha: el material del proyecto es TMC GALVANIZADA (M 218, la primera columna) y elegir otro recubrimiento es una decision de durabilidad que la matriz de la Sec. 3.3 deja al proyectista

| Fila | Specified Thickness, mm | M 218, Zinc Coated | M 274 AlT2, Aluminum Coated | M 289, 55 Percent Aluminum-Zinc Alloy Coated | A 885, Zinc and Aramid Fiber Coated | A 929M Zn-5 Al-MM, Alloy Coated | A 929M AlT1, Aluminum Coated | Uso |
|---|---|---|---|---|---|---|---|---|
| 1.02 | 1.02 | X |  | X |  | X |  | usada |
| 1.32 | 1.32 | X | X | X |  | X | X | usada |
| 1.63 | 1.63 | X | X | X | X | X | X | usada |
| 2.01 | 2.01 | X | X | X | X | X | X | usada |
| 2.77 | 2.77 | X | X | X | X | X | X | usada |
| 3.51 | 3.51 | X | X | X | X | X | X | usada |
| 4.27 | 4.27 | X |  |  | X | X |  | usada |

> a An “X” indicates sheet thickness included in the applicable specification for coating types listed.

### `ASTM_A760.T1` — TABLA 1 Tamaños de tubería

- Cita: `ASTM_A760.T1`
- Tabla completa · el calculo usa 0 de 11 columnas y 0 de 31 filas
- Columna «en.» transcrita y **no usada**: el calculo opera en SI; la pulgada es la unidad IMPRESA y sin ella la conversion no se puede comprobar
- Columna «mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «1 1/2 por 1/4 en. [38 por 6,5 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «2 2/3 por 1/2 en. [68 por 13 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «3 por 1 pulg. [75 por 25 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «5 por 1 pulg. [125 por 25 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «3/4 por 3/4 por 7 1/2 en. [19 por 19 por 190 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «3/4 por 1 por 11 1/2 en. [19 por 25 por 292 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «3/4 por 1 por 8 1/2 en. [19 por 25 por 216 mm]» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- Columna «en.» transcrita y **no usada**: el calculo opera en SI; la pulgada es la unidad IMPRESA y sin ella la conversion no se puede comprobar
- Columna «mm» transcrita y **no usada**: ningun modulo de calculo consume hoy la relacion diametro/corrugacion: es el insumo de la mitad TRANSCRIBIBLE de la verificacion pendiente del TMC declarada en 'clases_producto_por_relleno' (NOR-PRO-04), y la consulta el proyectista al especificar el producto. La otra mitad -- el calibre por altura de cobertura -- dejo de estar bloqueada por una fuente ausente en N1 (ASTM A796/A796M-13 esta en normas/) y resulto no ser una tabla: A796 fija el calibre por PROCEDIMIENTO (num. 7 a 11), con sus Tablas 3 a 17 -- transcritas aqui, una por corrugacion -- como insumo. Se cierra implementando ese procedimiento, no transcribiendo
- **Interpretación del proyectista, no de la fuente**: Este PDF es la TRADUCCION AL ESPAÑOL de A760/A760M-10 (la Fuente lo declara). La traduccion degrada rotulos, no valores: «en.» es in., los marcadores de nota A y B llegan como «UNA» y «segundo», y dos circunferencias en pulgadas (187.0 y 243.0) se imprimen con punto decimal donde el resto usa coma. Los numeros se leyeron uno a uno sobre la imagen y coinciden celda a celda, en mm, con la Table 6 de AASHTO M 36, que es la misma norma en edicion anterior.
  - En contra: el original en ingles de A760/A760M-10 no esta en normas/, de modo que el cotejo contra el ingles solo pudo hacerse via AASHTO M 36, que es otra EDICION: las dos celdas en que difieren (375 y 825) no se pueden atribuir con certeza a la edicion o a la traduccion
  - En contra: TRES CELDAS SON ARITMETICAMENTE ANOMALAS DENTRO DE LA PROPIA TABLA, Y LA ANOMALIA ESTA IMPRESA EN LAS DOS EDICIONES (hallada por auditoria aritmetica en I1b y desempatada releyendo los digitos a 26-60x en ambos PDF): la circunferencia 264 de la fila 100 da 23.16 mm por pulgada donde las demas filas dan 24.9-25.0 (la razon interna pediria 284); el diametro 500 de la fila de 21 in rompe el paso de 75 mm de la serie 450-600 (el paso pediria 525, fila que NO existe en ninguno de los dos ejemplares); y la circunferencia 2483 de la fila 750 da 26.67 mm por pulgada y rompe la progresion +237/+392/+78 donde la regular es ~236 (pediria 2326). NO SE CORRIGEN: los tres valores estan impresos identicos en las dos ediciones y reescribirlos seria inventar un valor normativo contra la fuente primaria. Si son erratas de imprenta arrastradas o la serie real, no es decidible con lo adjunto: exige el original ingles de A760/A760M-10 u otro ejemplar independiente, que no estan en normas/
  - A favor: los 31 diametros y las 31 circunferencias en mm coinciden celda a celda entre las dos ediciones, que es la comprobacion cruzada mas fuerte disponible sin el original -- y en I1b las seis celdas en disputa se releyeron digito a digito, con controles de forma sobre glifos vecinos, en los dos PDF

| Fila | en. | mm | 1 1/2 por 1/4 en. [38 por 6,5 mm] | 2 2/3 por 1/2 en. [68 por 13 mm] | 3 por 1 pulg. [75 por 25 mm] | 5 por 1 pulg. [125 por 25 mm] | 3/4 por 3/4 por 7 1/2 en. [19 por 19 por 190 mm] | 3/4 por 1 por 11 1/2 en. [19 por 25 por 292 mm] | 3/4 por 1 por 8 1/2 en. [19 por 25 por 216 mm] | en. | mm | Uso |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 4 | 100 | X |  |  |  |  |  |  | 11.4 | 264 | no usada |
| 150 | 6 | 150 | X |  |  |  |  |  |  | 17.7 | 441 | no usada |
| 200 | 8 | 200 | X |  |  |  |  |  |  | 24.0 | 598 | no usada |
| 250 | 10 | 250 | X |  |  |  |  |  |  | 30.2 | 755 | no usada |
| 300 | 12 | 300 | X | X |  |  |  |  |  | 36.5 | 912 | no usada |
| 375 | 15 | 375 | X | X |  |  | X |  |  | 46.0 | 1148 | no usada |
| 450 | 18 | 450 | X | X |  |  | X | X | X | 55.4 | 1383 | no usada |
| 500 | 21 | 500 |  | X |  |  | X | X | X | 64.8 | 1620 | no usada |
| 600 | 24 | 600 |  | X |  |  | X | X | X | 74.2 | 1854 | no usada |
| 675 | 27 | 675 |  | X |  |  | X | X | X | 83.6 | 2091 | no usada |
| 750 | 30 | 750 |  | X |  |  | X | X | X | 93.1 | 2483 | no usada |
| 825 | 33 | 825 |  | X |  |  | X | X | X | 102.5 | 2561 | no usada |
| 900 | 36 | 900 |  | X | X | X | X | X | X | 111.9 | 2797 | no usada |
| 1050 | 42 | 1050 |  | X | X | X | X | X | X | 130.8 | 3269 | no usada |
| 1200 | 48 | 1200 |  | X | X | X | X | X | X | 149.6 | 3739 | no usada |
| 1350 | 54 | 1350 |  | X | X | X | X | X | X | 168.4 | 4209 | no usada |
| 1500 | 60 | 1500 |  | X | X | X | X | X | X | 187.0 | 4675 | no usada |
| 1650 | 66 | 1650 |  | X | X | X | X | X | X | 205.7 | 5142 | no usada |
| 1800 | 72 | 1800 |  | X | X | X | X | X | X | 224.3 | 5609 | no usada |
| 1950 | 78 | 1950 |  | X | X | X | X | X | X | 243.0 | 6075 | no usada |
| 2100 | 84 | 2100 |  | X | X | X | X | X | X | 261.7 | 6542 | no usada |
| 2250 | 90 | 2250 |  |  | X | X | X | X | X | 280.3 | 7008 | no usada |
| 2400 | 96 | 2400 |  |  | X | X | X | X | X | 299.0 | 7475 | no usada |
| 2550 | 102 | 2550 |  |  | X | X | X | X | X | 317.6 | 7941 | no usada |
| 2700 | 108 | 2700 |  |  | X | X | X | X | X | 336.3 | 8408 | no usada |
| 2850 | 114 | 2850 |  |  | X | X | X |  | X | 355.0 | 8874 | no usada |
| 3000 | 120 | 3000 |  |  | X | X | X |  | X | 373.6 | 9341 | no usada |
| 3150 | 126 | 3150 |  |  | X | X |  |  | X | 392.3 | 9807 | no usada |
| 3300 | 132 | 3300 |  |  | X | X |  |  | X | 410.9 | 10274 | no usada |
| 3450 | 138 | 3450 |  |  | X | X |  |  | X | 429.6 | 10740 | no usada |
| 3600 | 144 | 3600 |  |  | X | X |  |  | X | 448.3 | 11207 | no usada |

> UNA Una “X” indica tamaños de corrugación estándar para cada diámetro nominal de tubería.

> segundo Medido en valle de corrugaciones anulares. No aplicable a tubería ondulada helicoidalmente.

> c Tamaño adicional para tubería Tipo IS.

### `ASTM_A796.10.2` — 10.2

- Cita: `ASTM_A796.10.2`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 6 filas
- Columna «Depth of Corrugation, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Depth of Corrugation, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Depth of Corrugation, in. [mm] | Depth of Corrugation, in. [mm] | FF, in./lbf [mm/N] | FF, in./lbf [mm/N] | Uso |
|---|---|---|---|---|---|
| ¼ [6.5] | ¼ | 6.5 | 0.06 | 0.342 | no usada |
| ⅜ [10] | ⅜ | 10 | 0.06 | 0.342 | no usada |
| ½ [13] | ½ | 13 | 0.06 | 0.342 | no usada |
| 1 [25] | 1 | 25 | 0.06 | 0.342 | no usada |
| 2 [51] | 2 | 51 | 0.02 | 0.114 | no usada |
| 5½ [140] | 5½ | 140 | 0.02 | 0.114 | no usada |

### `ASTM_A796.10.3` — 10.3

- Cita: `ASTM_A796.10.3`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 8 filas
- Columna «Depth of Corrugation, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Depth of Corrugation, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Depth of Corrugation, in. [mm] | Depth of Corrugation, in. [mm] | FF, in./lbf [mm/N] | FF, in./lbf [mm/N] | Uso |
|---|---|---|---|---|---|
| ¼ [6.5] | ¼ | 6.5 | 0.043 | 0.245 | no usada |
| ⅜ [10] | ⅜ | 10 | 0.043 | 0.245 | no usada |
| ½ [13] | ½ | 13 | 0.043 | 0.245 | no usada |
| 1 [25] | 1 | 25 | 0.033 | 0.188 | no usada |
| 2 (round pipe) [51] | 2 (round pipe) | 51 | 0.02 | 0.114 | no usada |
| 2 (pipe-arch, arch, underpass) [51] | 2 (pipe-arch, arch, underpass) | 51 | 0.03 | 0.171 | no usada |
| 5½ (round pipe) [140] | 5½ (round pipe) | 140 | 0.02 | 0.114 | no usada |
| 5½ (pipe-arch, arch, underpass) [140] | 5½ (pipe-arch, arch, underpass) | 140 | 0.03 | 0.171 | no usada |

### `ASTM_A796.10.4` — 10.4

- Cita: `ASTM_A796.10.4`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 3 filas
- Columna «Profile, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Profile, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Profile, in. [mm] | Profile, in. [mm] | FF, in./lbf [mm/N] | FF, in./lbf [mm/N] | Uso |
|---|---|---|---|---|---|
| ¾ by ¾ by 7½ [19 by 19 by 190] | ¾ by ¾ by 7½ | 19 by 19 by 190 | 0.367 I¹ᐟ³ | 0.0825 | no usada |
| ¾ by 1 by 8½ [19 by 25 by 216] | ¾ by 1 by 8½ | 19 by 25 by 216 | 0.262 I¹ᐟ³ | 0.0589 | no usada |
| ¾ by 1 by 11½ [19 by 25 by 292] | ¾ by 1 by 11½ | 19 by 25 by 292 | 0.220 I¹ᐟ³ | 0.0495 | no usada |

### `ASTM_A796.10.5` — 10.5

- Cita: `ASTM_A796.10.5`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 3 filas
- Columna «Profile, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Profile, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Profile, in. [mm] | Profile, in. [mm] | FF, in./lbf [mm/N] | FF, in./lbf [mm/N] | Uso |
|---|---|---|---|---|---|
| ¾ by ¾ by 7½ [19 by 19 by 190] | ¾ by ¾ by 7½ | 19 by 19 by 190 | 0.263 I¹ᐟ³ | 0.0591 | no usada |
| ¾ by 1 by 8½ [19 by 25 by 216] | ¾ by 1 by 8½ | 19 by 25 by 216 | 0.163 I¹ᐟ³ | 0.0366 | no usada |
| ¾ by 1 by 11½ [19 by 25 by 292] | ¾ by 1 by 11½ | 19 by 25 by 292 | 0.163 I¹ᐟ³ | 0.0366 | no usada |

### `ASTM_A796.10.6` — 10.6

- Cita: `ASTM_A796.10.6`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 3 filas
- Columna «Profile, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Profile, in. [mm]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «FF, in./lbf [mm/N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Profile, in. [mm] | Profile, in. [mm] | FF, in./lbf [mm/N] | FF, in./lbf [mm/N] | Uso |
|---|---|---|---|---|---|
| ¾ by ¾ by 7½ [19 by 19 by 190] | ¾ by ¾ by 7½ | 19 by 19 by 190 | 0.217 I¹ᐟ³ | 0.0488 | no usada |
| ¾ by 1 by 8½ [19 by 25 by 216] | ¾ by 1 by 8½ | 19 by 25 by 216 | 0.140 I¹ᐟ³ | 0.0315 | no usada |
| ¾ by 1 by 11½ [19 by 25 by 292] | ¾ by 1 by 11½ | 19 by 25 by 292 | 0.140 I¹ᐟ³ | 0.0315 | no usada |

### `ASTM_A796.11.1` — 11.1 Minimum Cover Design

- Cita: `ASTM_A796.11.1#DEF`
- Tabla completa · el calculo usa 0 de 3 columnas y 0 de 4 filas
- Columna «Class of Loading» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Maximum Axle Load, lbf [N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Maximum Axle Load, lbf [N]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- **Afirmación negativa**: ASTM A796/A796M-13 no contiene ninguna tabla de calibre (espesor) de TMC por altura de cobertura, ni de altura maxima de relleno por calibre: el espesor es la SALIDA del procedimiento de los num. 7 a 10 (area de pared requerida con SF = 2, pandeo, costura, factor de flexibilidad) elegida de las Tablas 2 a 35, y la cobertura minima sale de las ecs. (13) a (16) del num. 11.1 mas dos pisos absolutos. Ámbito barrido: las 21 paginas PDF del ejemplar (la impresa 1 falta: es la PDF 1 en blanco), leidas RENDERIZADAS de la 2 a la 7 -- todo el articulado, num. 2.1 a 24.1 -- y de la 7 a la 21 por los titulos de las 35 tablas: la TABLE 1 «Resistance Factors for LRFD Design» (PDF 3, factores phi) y las 34 restantes, TABLE 2 a TABLE 35, que son todas «Sectional Properties of ...» (planchas corrugadas, costilla espiral, costilla con insertos, compuestas, costilla cerrada y planchas estructurales); ninguna cruza espesor con altura de cobertura -- la PDF 15, girada, con las Tablas 20 y 21, se leyo entera por imagen porque su capa de texto no devuelve los titulos --. Censo por texto sobre la capa duplicada, que localiza palabras sueltas pero NO todas sus apariciones (la copia partida a mitad de palabra las esconde), contrastado por imagen: «height of cover» 1 pagina por texto (la PDF 6, num. 18.2.4) y TRES por imagen (PDF 2, la variable h del 4.1; PDF 3, las cabeceras de las tabulaciones del 6.2.2; PDF 6, num. 18.2.4 y 18.3); «minimum cover» 3 paginas por texto y por imagen (PDF 5, num. 11; PDF 6, num. 18.3; PDF 7, keywords); «maximum cover» 0, «gage» 0, «gauge» 0, «A807» 1 (la PDF 6, num. 22.1). El num. 18.3 dice que la altura maxima de cobertura de un ARCO-TUBO la fija a menudo la capacidad portante del suelo en la esquina, no una tabla. El unico cruce espesor/cobertura es el escalon del 11.1: espesor < 1.32 mm => Hmin >= 600 mm
- **Interpretación del proyectista, no de la fuente**: Cuatro clases de carga en cuatro filas: H20 y HS 20 con 32 000 lbf [142 300 N], H15 y HS 15 con 24 000 lbf [106 700 N]. Es el (AL) de las ecs. (13) a (16)
  - En contra: Los renglones H20 y HS 20 se imprimen SOLAPADOS en el ejemplar, y no por la capa de texto duplicada: es un defecto de composicion de la propia pagina -- la fila HS 20 esta compuesta 5.8 pt por debajo de H20 cuando el paso entre las demas filas es de 11 pt (medido sobre las lineas base de los spans en N1) --, de modo que a simple vista parecen una fila repetida. Que son dos filas distintas con el mismo valor se apoya en las cuatro lineas base distintas de la capa de texto, que lista las cuatro etiquetas en orden (H20, HS 20, H15, HS 15) cada una con su carga, y en el patron de H15 / HS 15, que si se imprimen separados.
  - En contra: La clase de carga que rige en la obra no la elige esta tabla: AASHTO LRFD (que Sec. 0.2 adopta) usa HL-93 y no H20/HS 20; cual fila aplica seria un [A] el dia que se implemente el num. 11.1.

| Fila | Class of Loading | Maximum Axle Load, lbf [N] | Maximum Axle Load, lbf [N] | Uso |
|---|---|---|---|---|
| H20 | H20 | 32000 | 142300 | no usada |
| HS 20 | HS 20 | 32000 | 142300 | no usada |
| H15 | H15 | 24000 | 106700 | no usada |
| HS 15 | HS 15 | 24000 | 106700 | no usada |

### `ASTM_A796.6.2.2.1` — 6.2.2.1 Live Loads Under Highway

- Cita: `ASTM_A796.6.2.2.1`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 9 filas
- Columna «Height of Cover, ft [m]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Height of Cover, ft [m]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Live Load, lbf/ft² [kPa]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Live Load, lbf/ft² [kPa]» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- **Interpretación del proyectista, no de la fuente**: Los escalones no son tramos: el num. 6.2.2.3 manda interpolar entre coberturas intermedias, de modo que la tabla se lee como una banda de interpolacion de 0.30 a 2.44 m y como cero por encima
  - En contra: La instruccion de interpolar esta en OTRO numeral (6.2.2.3) y no en la tabulacion: quien lea solo la tabla ve escalones.
  - En contra: Por debajo de 0.30 m la tabla no dice nada, y ese caso lo cubre el piso del num. 11.1 (Hmin nunca menor de 300 mm), no una fila.

| Fila | Height of Cover, ft [m] | Height of Cover, ft [m] | Live Load, lbf/ft² [kPa] | Live Load, lbf/ft² [kPa] | Uso |
|---|---|---|---|---|---|
| 1 [0.30] | 1 | 0.3 | 1800 | 86.2 | no usada |
| 2 [0.61] | 2 | 0.61 | 800 | 38.3 | no usada |
| 3 [0.91] | 3 | 0.91 | 600 | 28.7 | no usada |
| 4 [1.22] | 4 | 1.22 | 400 | 19.2 | no usada |
| 5 [1.52] | 5 | 1.52 | 250 | 12.0 | no usada |
| 6 [1.83] | 6 | 1.83 | 200 | 9.6 | no usada |
| 7 [2.13] | 7 | 2.13 | 175 | 8.4 | no usada |
| 8 [2.44] | 8 | 2.44 | 100 | 4.8 | no usada |
| over 8 [over 2.44] | over 8 | over 2.44 | neglect | -- | no usada |

### `ASTM_A796.T11` — TABLE 11 Sectional Properties of Spiral Rib Pipe for 19 mm Wide by 19 mm Deep Rib with a Spacing of 190 mm Center to Center (Helical) [SI Units]

- Cita: `ASTM_A796.T11`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 4 filas
- Columna «Specified Thickness, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Area of Section, A, mm²/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Moment of Inertia, I, mm⁴/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Radius of Gyration, r, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Moment of Inertia, I, mm⁴/mm | Radius of Gyration, r, mm | Uso |
|---|---|---|---|---|---|
| 1.63 | 1.63 | 1.077 | 46.23 | 6.55 | no usada |
| 2.01 | 2.01 | 1.507 | 60.65 | 6.34 | no usada |
| 2.77 | 2.77 | 2.506 | 90.74 | 6.02 | no usada |
| 3.51 | 3.51 | 3.634 | 121.81 | 5.79 | no usada |

> A Net effective properties at full yield stress.

### `ASTM_A796.T15` — TABLE 15 Sectional Properties of Spiral Rib Pipe for 19 mm Wide by 25 mm Deep Rib with a Spacing of 292 mm Center to Center (Helical) [SI Units]

- Cita: `ASTM_A796.T15`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 3 filas
- Columna «Specified Thickness, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Area of Section, A, mm²/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Moment of Inertia, I, mm⁴/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Radius of Gyration, r, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Moment of Inertia, I, mm⁴/mm | Radius of Gyration, r, mm | Uso |
|---|---|---|---|---|---|
| 1.63 | 1.63 | 0.792 | 75.05 | 9.73 | no usada |
| 2.01 | 2.01 | 1.109 | 99.63 | 9.47 | no usada |
| 2.77 | 2.77 | 1.869 | 151.74 | 9.02 | no usada |

> A Net effective properties at full yield stress.

### `ASTM_A796.T17` — TABLE 17 Sectional Properties of Spiral Rib Pipe for 19 mm Wide by 25 mm Deep Rib with a Spacing of 216 mm Center to Center (Helical) [SI Units]

- Cita: `ASTM_A796.T17`
- Tabla completa · el calculo usa 0 de 4 columnas y 0 de 3 filas
- Columna «Specified Thickness, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Area of Section, A, mm²/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Moment of Inertia, I, mm⁴/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Radius of Gyration, r, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Moment of Inertia, I, mm⁴/mm | Radius of Gyration, r, mm | Uso |
|---|---|---|---|---|---|
| 1.63 | 1.63 | 1.057 | 97.98 | 9.63 | no usada |
| 2.01 | 2.01 | 1.469 | 129.67 | 9.4 | no usada |
| 2.77 | 2.77 | 2.433 | 196.37 | 8.99 | no usada |

> A Net effective properties at full yield stress.

### `ASTM_A796.T3` — TABLE 3 Sectional Properties of Corrugated Steel Sheets for Corrugation: 38 by 6.5 mm (Helical) [SI Units]

- Cita: `ASTM_A796.T3`
- Tabla completa · el calculo usa 0 de 6 columnas y 0 de 4 filas
- Columna «Specified Thickness, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Area of Section, A, mm²/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Tangent Length, TL, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Tangent Angle, Δ,°» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Moment of Inertia, I, mm⁴/mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Radius of Gyration, r, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Tangent Length, TL, mm | Tangent Angle, Δ,° | Moment of Inertia, I, mm⁴/mm | Radius of Gyration, r, mm | Uso |
|---|---|---|---|---|---|---|---|
| 1.02 | 1.02 | 0.965 | 14.5 | 21.44 | 4.15 | 2.07 | no usada |
| 1.32 | 1.32 | 1.287 | 14.4 | 21.52 | 5.62 | 2.08 | no usada |
| 1.63 | 1.63 | 1.611 | 14.2 | 21.61 | 7.19 | 2.11 | no usada |
| 2.01 | 2.01 | 2.011 | 14.1 | 21.71 | 9.28 | 2.15 | no usada |

> A This thickness should only be used for the inner liner of double-wall type IA pipe, or for temporary pipe. When used for other than temporary pipe, it should be polymer coated.

### `ASTM_A796.T5` — TABLE 5 Sectional Properties of Corrugated Steel Sheets for Corrugation: 68 by 13 mm (Annular or Helical) [SI Units]

- Cita: `ASTM_A796.T5`
- Tabla completa · el calculo usa 8 de 10 columnas y 6 de 7 filas
- Columna «Tangent Length, TL, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Tangent Angle, Δ, °» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Vistas de cálculo derivadas: `TMC_PLANCHA_CORRUGADA`, `COSTURA_REMACHADA_TMC_KN_M`

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Tangent Length, TL, mm | Tangent Angle, Δ, ° | Moment of Inertia, I, mm⁴/mm | Radius of Gyration, r, mm | Single | Double | Single | Double | Uso |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.02 | 1.02 | 0.984 | 19.9 | 26.56 | 18.39 | 4.232 | N/A | N/A | N/A | N/A | no usada |
| 1.32 | 1.32 | 1.31 | 19.8 | 26.65 | 24.58 | 4.336 | N/A | N/A | N/A | N/A | usada |
| 1.63 | 1.63 | 1.64 | 19.6 | 26.74 | 31.0 | 4.348 | 244 | 315 | N/A | N/A | usada |
| 2.01 | 2.01 | 2.049 | 19.3 | 26.86 | 39.2 | 4.371 | 266 | 435 | N/A | N/A | usada |
| 2.77 | 2.77 | 2.87 | 18.8 | 27.11 | 56.13 | 4.422 | N/A | N/A | 341 | 683 | usada |
| 3.51 | 3.51 | 3.691 | 18.3 | 27.37 | 74.28 | 4.486 | N/A | N/A | 357 | 715 | usada |
| 4.27 | 4.27 | 4.515 | 17.8 | 27.65 | 93.82 | 4.559 | N/A | N/A | 374 | 748 | usada |

> A This thickness should only be used for the inner liner of double-wall type IA pipe, or for temporary pipe. When used for other than temporary pipe, it should be polymer coated.

### `ASTM_A796.T7` — TABLE 7 Sectional Properties of Corrugated Steel Sheets for Corrugation: 75 by 25 mm (Annular or Helical) [SI Units]

- Cita: `ASTM_A796.T7`
- Tabla completa · el calculo usa 6 de 8 columnas y 6 de 6 filas
- Columna «Tangent Length, TL, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Tangent Angle, Δ, °» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- **Interpretación del proyectista, no de la fuente**: El momento de inercia de esta tabla se lee en mm⁴/mm, como en las otras seis, aunque el encabezado imprima «mm⁴/m»
  - En contra: La pagina imprime «I, mm⁴/m», y esta transcripcion respeta el rotulo en la etiqueta de la columna: la lectura en mm⁴/mm es del proyecto, apoyada en que los valores (112.94 a 411.04) son del mismo orden que los de la Table 9 (145.03 a 411.18), de profundidad de corrugacion vecina y rotulada «mm⁴/mm».
- Vistas de cálculo derivadas: `TMC_PLANCHA_CORRUGADA`, `COSTURA_REMACHADA_TMC_KN_M`

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Tangent Length, TL, mm | Tangent Angle, Δ, ° | Moment of Inertia, I, mm⁴/m | Radius of Gyration, r, mm | Double | Double | Uso |
|---|---|---|---|---|---|---|---|---|---|
| 1.32 | 1.32 | 1.505 | 24.2 | 44.39 | 112.94 | 8.661 | N/A | N/A | usada |
| 1.63 | 1.63 | 1.884 | 23.8 | 44.6 | 141.88 | 8.679 | 419 | N/A | usada |
| 2.01 | 2.01 | 2.356 | 23.4 | 44.87 | 178.34 | 8.705 | 521 | N/A | usada |
| 2.77 | 2.77 | 3.302 | 22.6 | 45.42 | 253.31 | 8.758 | N/A | 773 | usada |
| 3.51 | 3.51 | 4.25 | 21.7 | 46.02 | 330.61 | 8.819 | N/A | 929 | usada |
| 4.27 | 4.27 | 5.203 | 20.8 | 46.65 | 411.04 | 8.887 | N/A | 1032 | usada |

### `ASTM_A796.T9` — TABLE 9 Sectional Properties of Corrugated Steel Sheets for Corrugation: 125 by 25 mm (Helical) [SI Units]

- Cita: `ASTM_A796.T9`
- Tabla completa · el calculo usa 4 de 6 columnas y 5 de 5 filas
- Columna «Tangent Length, TL, mm» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Columna «Tangent Angle, Δ,°» transcrita y **no usada**: ningun modulo de calculo consume esta tabla o columna. Desde T-5 la Fase 8 verifica el TMC por AASHTO LRFD 12.7.2 (LRFD), con la carga viva HL-93 del Manual de Puentes y no la H20, con los limites de flexibilidad de la Tabla 12.5.6.1-1 y con las propiedades seccionales y la costura de las Tablas 5, 7 y 9 de esta norma, que son las de las corrugaciones del catalogo; el procedimiento por tensiones admisibles de ASTM A796 (num. 6 a 11) se imprime solo como CONTRASTE, con sus propios parametros del num. 4. Lo demas documenta que espesores existen para cada corrugacion y con que rigidez, para quien especifique el producto
- Vistas de cálculo derivadas: `TMC_PLANCHA_CORRUGADA`

| Fila | Specified Thickness, mm | Area of Section, A, mm²/mm | Tangent Length, TL, mm | Tangent Angle, Δ,° | Moment of Inertia, I, mm⁴/mm | Radius of Gyration, r, mm | Uso |
|---|---|---|---|---|---|---|---|
| 1.63 | 1.63 | 1.681 | 18.5 | 35.58 | 145.03 | 9.289 | usada |
| 2.01 | 2.01 | 2.1 | 18.0 | 35.8 | 181.77 | 9.304 | usada |
| 2.77 | 2.77 | 2.942 | 16.9 | 36.3 | 256.46 | 9.34 | usada |
| 3.51 | 3.51 | 3.785 | 15.6 | 36.81 | 332.94 | 9.38 | usada |
| 4.27 | 4.27 | 4.627 | 14.3 | 37.39 | 411.18 | 9.426 | usada |

### `DG2018.T304.09` — Anchos mínimos de Derecho de Vía

- Cita: `DG2018.304.07.02#T304.09`
- Tabla completa · el calculo usa 0 de 2 columnas y 0 de 5 filas
- Columna «Clasificación» transcrita y **no usada**: la clase de via del corredor es el dato de sitio 'clase_de_via', vacio hasta que el estudio de demanda cierre el IMDA; sin el no se elige fila
- Columna «Anchos mínimos (m)» transcrita y **no usada**: V5 se detiene en el dato de sitio 'ancho_derecho_via_m', que hoy no llega por ninguna via; cuando llegue, este piso --- con el incremento del 304.07.02 compuesto como diga su interpretacion --- es contra lo que se comprueba
- Vistas de cálculo derivadas: `ANCHO_MIN_DERECHO_VIA_M`

| Fila | Clasificación | Anchos mínimos (m) | Uso |
|---|---|---|---|
| Autopistas Primera Clase |  | PisoUnico(minimo=40.0, unidad='m', cita_id='DG2018.304.07.02', que_pasa_fuera=<QuePasaFuera.INCUMPLE_LA_NORMA: 'incumple'>, rotulo_obligatorio='La fuente escribe un MINIMO exigible.') | no usada |
| Autopistas Segunda Clase |  | PisoUnico(minimo=30.0, unidad='m', cita_id='DG2018.304.07.02', que_pasa_fuera=<QuePasaFuera.INCUMPLE_LA_NORMA: 'incumple'>, rotulo_obligatorio='La fuente escribe un MINIMO exigible.') | no usada |
| Carretera Primera Clase |  | PisoUnico(minimo=25.0, unidad='m', cita_id='DG2018.304.07.02', que_pasa_fuera=<QuePasaFuera.INCUMPLE_LA_NORMA: 'incumple'>, rotulo_obligatorio='La fuente escribe un MINIMO exigible.') | no usada |
| Carretera Segunda Clase |  | PisoUnico(minimo=20.0, unidad='m', cita_id='DG2018.304.07.02', que_pasa_fuera=<QuePasaFuera.INCUMPLE_LA_NORMA: 'incumple'>, rotulo_obligatorio='La fuente escribe un MINIMO exigible.') | no usada |
| Carretera Tercera Clase |  | PisoUnico(minimo=16.0, unidad='m', cita_id='DG2018.304.07.02', que_pasa_fuera=<QuePasaFuera.INCUMPLE_LA_NORMA: 'incumple'>, rotulo_obligatorio='La fuente escribe un MINIMO exigible.') | no usada |

### `DG2018.T304.11` — Taludes referenciales en zonas de relleno (terraplenes)

- Cita: `DG2018.304.10#T304.11`
- Tabla completa · el calculo usa 0 de 3 columnas y 0 de 3 filas
- Columna «<5» transcrita y **no usada**: la altura de terraplen por punto se conoce, pero el material del cuerpo del terraplen no es dato del expediente y la tabla es referencial: acota la ventana de 'talud_terraplen', no lo fija
- Columna «5-10» transcrita y **no usada**: la altura de terraplen por punto se conoce, pero el material del cuerpo del terraplen no es dato del expediente y la tabla es referencial: acota la ventana de 'talud_terraplen', no lo fija
- Columna «>10» transcrita y **no usada**: la altura de terraplen por punto se conoce, pero el material del cuerpo del terraplen no es dato del expediente y la tabla es referencial: acota la ventana de 'talud_terraplen', no lo fija

| Fila | <5 | 5-10 | >10 | Uso |
|---|---|---|---|---|
| Gravas, limo arenoso y arcilla | 1.5 | 1.75 | 2.0 | no usada |
| Arena | 2.0 | 2.25 | 2.5 | no usada |
| Enrocado | 1.0 | 1.25 | 1.5 | no usada |

### `E050.FIG3` — Simbología de Suelos (Referencial)

- Cita: `E050.FIG3`
- Tabla completa · el calculo usa 2 de 3 columnas y 15 de 15 filas
- Columna «DIVISIONES MAYORES» transcrita y **no usada**: agrupa los simbolos; el criterio elige por simbolo, no por division
- Vistas de cálculo derivadas: `SIMBOLOS_SUCS`

| Fila | DIVISIONES MAYORES | SUCS | DESCRIPCIÓN | Uso |
|---|---|---|---|---|
| GW | SUELOS GRANULARES / GRAVA Y SUELOS GRAVOSOS | GW | GRAVA BIEN GRADUADA | usada |
| GP | SUELOS GRANULARES / GRAVA Y SUELOS GRAVOSOS | GP | GRAVA MAL GRADUADA | usada |
| GM | SUELOS GRANULARES / GRAVA Y SUELOS GRAVOSOS | GM | GRAVA LIMOSA | usada |
| GC | SUELOS GRANULARES / GRAVA Y SUELOS GRAVOSOS | GC | GRAVA ARCILLOSA | usada |
| SW | SUELOS GRANULARES / ARENA Y SUELOS ARENOSOS | SW | ARENA BIEN GRADUADA | usada |
| SP | SUELOS GRANULARES / ARENA Y SUELOS ARENOSOS | SP | ARENA MAL GRADUADA | usada |
| SM | SUELOS GRANULARES / ARENA Y SUELOS ARENOSOS | SM | ARENA LIMOSA | usada |
| SC | SUELOS GRANULARES / ARENA Y SUELOS ARENOSOS | SC | ARENA ARCILLOSA | usada |
| ML | SUELOS FINOS / LIMOS Y ARCILLAS (LL < 50) | ML | LIMO INORGÁNICO DE BAJA PLASTICIDAD | usada |
| CL | SUELOS FINOS / LIMOS Y ARCILLAS (LL < 50) | CL | ARCILLA INORGÁNICA DE BAJA PLASTICIDAD | usada |
| OL | SUELOS FINOS / LIMOS Y ARCILLAS (LL < 50) | OL | LIMO ORGÁNICO O ARCILLA ORGÁNICA DE BAJA PLASTICIDAD | usada |
| MH | SUELOS FINOS / LIMOS Y ARCILLAS (LL > 50) | MH | LIMO INORGÁNICO DE ALTA PLASTICIDAD | usada |
| CH | SUELOS FINOS / LIMOS Y ARCILLAS (LL > 50) | CH | ARCILLA INORGÁNICA DE ALTA PLASTICIDAD | usada |
| OH | SUELOS FINOS / LIMOS Y ARCILLAS (LL > 50) | OH | LIMO ORGÁNICO O ARCILLA ORGÁNICA DE ALTA PLASTICIDAD | usada |
| Pt | SUELOS ALTAMENTE ORGÁNICOS | Pt | TURBA Y OTROS SUELOS ALTAMENTE ORGÁNICOS. | usada |

### `E060.T4.2` — TABLA 4.2 REQUISITOS PARA CONDICIONES ESPECIALES DE EXPOSICIÓN

- Cita: `E060.T4.2`
- Tabla completa · el calculo usa 2 de 3 columnas y 2 de 3 filas
- Columna «Condición de la exposición»: **elección pendiente** (`COND-EXPOSICION-QUIMICA-EMS`) — el cálculo se detiene
- Vistas de cálculo derivadas: `EXPOSICION_ESPECIAL`

| Fila | Condición de la exposición | Relación máxima agua - material cementante (en peso) para concretos de peso normal * | f’c mínimo (MPa) para concretos de peso normal o con agregados ligeros* | Uso |
|---|---|---|---|---|
| Concreto que se pretende tenga baja permeabilidad en exposición al agua. |  | 0.5 | 28 | usada |
| Concreto expuesto a ciclos de congelamiento y deshielo en condición húmeda o a productos químicos descongelantes. |  | 0.45 | 31 | no usada |
| Para proteger de la corrosión el refuerzo de acero cuando el concreto está expuesto a cloruros provenientes de productos descongelantes, sal, agua salobre, agua de mar o a salpicaduras del mismo origen. |  | 0.4 | 35 | usada |

> * Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se debe utilizar la menor relación máxima agua-material cementante aplicable y el mayor f’c mínimo.

### `E060.T4.4` — TABLA 4.4 REQUISITOS PARA CONCRETO EXPUESTO A SOLUCIONES DE SULFATOS

- Cita: `E060.T4.4`
- Tabla completa · el calculo usa 5 de 6 columnas y 4 de 4 filas
- Columna «Exposición a sulfatos»: **elección pendiente** (`COND-EXPOSICION-QUIMICA-EMS`) — el cálculo se detiene
- **Laguna de la fuente**: el punto SO4 = 2,0 % exacto en la escala del suelo -- y 10 000 ppm exacto en la del agua --. VERIFICADO SOBRE LA IMAGEN RENDERIZADA: la fila severa se imprime «0,2 ≤ SO4 < 2,0», con cota superior ESTRICTA, y la muy severa «2,0 < SO4», con cota inferior ESTRICTA y sin «≤». El valor exacto no cae en ninguna de las dos. Se cierra con: la hoja de ruta lo cierra: su Sec. 3.3 escribe la fila severa como «0.20 - 2.00» y la muy severa como «> 2.00», de modo que el punto exacto queda en SEVERA. Se sigue esa lectura y no la mas exigente porque la fuente primaria no la contradice: calla. Y la unica diferencia practica entre las dos filas es el cemento (V frente a V mas puzolana): la a/c y el f'c son los mismos, de modo que el recubrimiento no cambia por este borde (`hoja_de_ruta §3.3`)
- **Errata declarada**: `DIS-E060-BORDE-2-0`
- Vistas de cálculo derivadas: `SULFATOS`

| Fila | Exposición a sulfatos | Sulfato soluble en agua (SO4) presente en el suelo, porcentaje en peso | Sulfato (SO4) en el agua, ppm | Tipo de Cemento | Relación máxima agua - material cementante (en peso) para concretos de peso normal* | f’c mínimo (MPa) para concretos de peso normal y ligero* | Uso |
|---|---|---|---|---|---|---|---|
| Insignificante |  | 0,0 ≤ SO4 < 0,1 | 0 ≤ SO4< 150 |  |  |  | usada |
| Moderada** |  | 0,1 ≤ SO4 < 0,2 | 150 ≤ SO4 < 1500 | II, IP(MS), IS(MS), P(MS), I(PM)(MS), I(SM)(MS) | 0.5 | 28 | usada |
| Severa |  | 0,2 ≤ SO4 < 2,0 | 1500 ≤ SO4 < 10000 | V | 0.45 | 31 | usada |
| Muy severa |  | 2,0 < SO4 | 10000 < SO4 | Tipo V más puzolana*** | 0.45 | 31 | usada |

> * Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se debe utilizar la menor relación máxima agua-material cementante aplicable y el mayor f’c mínimo.

> ** Se considera el caso del agua de mar como exposición moderada.

> *** Puzolana que se ha comprobado por medio de ensayos, o por experiencia, que mejora la resistencia a sulfatos cuando se usa en concretos que contienen cemento tipo V.

### `E060.T7.7.1` — 7.7.1 Concreto construido en sitio (no preesforzado)

- Cita: `E060.7.7.1`
- Transcripcion acotada · el calculo usa 2 de 2 columnas y 3 de 3 filas
- **Transcripción acotada.** Razón: el inciso (c) del articulo -- «Concreto no expuesto a la intemperie ni en contacto con el suelo» -- describe elementos interiores de edificacion (losas, muros, viguetas, vigas y columnas, cascaras y losas plegadas). Un cabezal de alcantarilla esta, por definicion, contra el suelo o a la intemperie: ninguna de sus siete filas puede aplicarle
  - Qué queda fuera: (c) Concreto no expuesto a la intemperie ni en contacto con el suelo: losas, muros y viguetas (40 y 20 mm), vigas y columnas (40 mm), y cascaras y losas plegadas (20, 15 y 15 mm)
  - Dónde leerlo: E.060, Art. 7.7.1 (c), pag. impresa 54
- Vistas de cálculo derivadas: `RECUBRIMIENTO`

| Fila | Situación | Recubrimiento mínimo | Uso |
|---|---|---|---|
| (a) -- Concreto colocado contra el suelo y expuesto permanentemente a él |  | 70 | usada |
| (b) -- Concreto en contacto permanente con el suelo o la intemperie -- Barras de 3/4” y mayores |  | 50 | usada |
| (b) -- Concreto en contacto permanente con el suelo o la intemperie -- Barras de 5/8” y menores, mallas electrosoldadas |  | 40 | usada |

### `EG2013.T503-07` — Tabla 503-07 Clases de concreto estructural

- Cita: `EG2013.503.04#T503_07`
- Tabla completa · el calculo usa 2 de 2 columnas y 2 de 7 filas
- **Errata declarada**: `DIS-HR-CICLOPEO`
- Vistas de cálculo derivadas: `CLASES_CONCRETO_EG2013_MPA`

| Fila | Clase | Resistencia mínima a la compresión a 28 días | Uso |
|---|---|---|---|
| Concreto pre y post tensado -- A |  | 35.0 | no usada |
| Concreto pre y post tensado -- B |  | 32.0 | no usada |
| Concreto reforzado -- C |  | 28.0 | no usada |
| Concreto reforzado -- D |  | 21.0 | no usada |
| Concreto reforzado -- E |  | 17.5 | no usada |
| Concreto simple -- F |  | 14.0 | usada |
| Concreto ciclópeo -- G |  | 14.0 | usada |

### `HDS5_3ED.TA1` — Table A.1.  Constants for Inlet Control Equations for Charts in Appendix G.

- Cita: `HDS5_3ED.TA.1`
- Transcripcion acotada · el calculo usa 8 de 10 columnas y 2 de 26 filas
- **Transcripción acotada.** Razón: de las 36 filas de la tabla, este proyecto transcribe las 26 que describen una EMBOCADURA DE BARRIL: las ocho circulares de las Cartas 1, 2 y 3 -- de las que el catalogo USA tres: concreto a escuadra a ras del muro y las dos de metal corrugado, cabezal e inglete --, y las dieciocho del cajon rectangular de concreto de las Cartas 8 a 13. Las cinco circulares y las tres de la Carta 13 que anadio T-2 no cambian ningun calculo: quedan disponibles para que la embocadura del cabezal nombre su fila
  - Qué queda fuera: las diez filas de TAPERED INLET, que son caras y gargantas de una entrada abocinada y no embocaduras de barril: las dos de «Circular» de la Carta 55 (garganta lisa y rugosa), las tres de «Ellipital Face» de la Carta 56 y las cinco de «Rectangular Concrete» de las Cartas 57, 58 y 59
  - Dónde leerlo: HDS-5 3a ed., Tabla A.1, PDF 197. La pagina NO LLEVA FOLIO IMPRESO, de modo que la «pag. impresa A.8» que el repositorio declara es una INFERENCIA por secuencia (PDF 196 lleva A.7) y no una lectura. En I3 el verificador-normativo la confirmo CORRECTO-INFERIDO por texto con coordenadas Y por render de la pagina entera, los cuatro bordes: ningun folio en 197; vecinos leidos A.5@194 a A.7@196 y B.1@203; entre A.7 y B.1 van seis paginas sin folio (las tres apaisadas de tablas 197-199, la vertical de las Tablas A.4-A.6 en 200, la en blanco 201 y la portadilla del Apendice B en 202 -- esta frase decia «cuatro apaisadas» hasta I3), y ninguna asignacion alternativa de folios es consistente con los impresos. `pagina_impresa` se queda en «A.8»: es el valor que la regla de paginacion de T6 predice, y la nota de `HDS5_3ED.TA.1` es la que declara que no es una lectura
- Columna «Nomograph Scale» transcrita y **no usada**: identifica la escala del nomograma impreso; este programa resuelve las ecuaciones y no lee nomogramas
- Columna «References» transcrita y **no usada**: son las referencias bibliograficas de cada carta (Bossy 1963, FHWA 1974, NBS 5th, HEC 13); no entran en ninguna formula
- Fila «8 -- Rect. Box Concrete -- 30° to 75° wingwall flares»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «8 -- Rect. Box Concrete -- 90° and 15° wingwall flares»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «8 -- Rect. Box Concrete -- 0° wingwall flares»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «9 -- Rect. Box Concrete -- 45° wingwall flare d = .043D»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «9 -- Rect. Box Concrete -- 18° to 33.7° wingwall flare d = .083D»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «10 -- Rect. Box Concrete -- 90° headwall w/3/4" chamfers»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «10 -- Rect. Box Concrete -- 90° headwall w/45° bevels»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «10 -- Rect. Box Concrete -- 90° headwall w/33.7° bevels»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «11 -- Rect. Box Concrete -- 3/4" chamfers; 45° skewed headwall»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «11 -- Rect. Box Concrete -- 3/4" chamfers; 30° skewed headwall»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «11 -- Rect. Box Concrete -- 3/4" chamfers; 15° skewed headwall»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «11 -- Rect. Box Concrete -- 45° bevels; 10°-45° skewed headw.»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «12 -- Rect. Box 3/4" chamf. Conc. -- 45° non-offset wingwall flares»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «12 -- Rect. Box 3/4" chamf. Conc. -- 18.4° non-offset wingwall flares»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «12 -- Rect. Box 3/4" chamf. Conc. -- 18.4° non-offset wingwall flares 30° skewed barrel»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «13 -- Rect. Box Top Bev. Conc. -- 45° wingwall flares - offset»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «13 -- Rect. Box Top Bev. Conc. -- 33.7° wingwall flares - offset»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- Fila «13 -- Rect. Box Top Bev. Conc. -- 18.4° wingwall flares - offset»: **elección pendiente** (`COND-EMBOCADURA-CAJON`)
- **Errata declarada**: `DIS-HDS5-APENDICE-G`
- Vistas de cálculo derivadas: `HDS5_INLET`

| Fila | Chart No | Shape and Material | Nomograph Scale | Inlet Configuration | Equation Form | Unsubmerged K | Unsubmerged M | Submerged c | Submerged Y | References | Uso |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 -- Circular Concrete -- Square edge w/headwall | 1 | Circular Concrete | 1 | Square edge w/headwall | 1 | 0.0098 | 2.0 | 0.0398 | 0.67 | 1, 2 | usada |
| 2 -- Circular CM -- Headwall | 2 | Circular CM | 1 | Headwall | 1 | 0.0078 | 2.0 | 0.0379 | 0.69 | 1, 2 | usada |
| 2 -- Circular CM -- Mitered to slope | 2 | Circular CM | 2 | Mitered to slope | 1 | 0.021 | 1.33 | 0.0463 | 0.75 | 1, 2 | no usada |
| 1 -- Circular Concrete -- Groove end w/headwall | 1 | Circular Concrete | 2 | Groove end w/headwall | 1 | 0.0018 | 2.0 | 0.0292 | 0.74 | 1, 2 | no usada |
| 1 -- Circular Concrete -- Groove end projecting | 1 | Circular Concrete | 3 | Groove end projecting | 1 | 0.0045 | 2.0 | 0.0317 | 0.69 | 1, 2 | no usada |
| 2 -- Circular CM -- Projecting | 2 | Circular CM | 3 | Projecting | 1 | 0.034 | 1.5 | 0.0553 | 0.54 | 1, 2 | no usada |
| 3 -- Circular -- Beveled ring, 45° bevels | 3 | Circular | A | Beveled ring, 45° bevels | 1 | 0.0018 | 2.5 | 0.03 | 0.74 | 2 | no usada |
| 3 -- Circular -- Beveled ring, 33.7° bevels* | 3 | Circular | B | Beveled ring, 33.7° bevels* | 1 | 0.0018 | 2.5 | 0.0243 | 0.83 | 2 | no usada |
| 8 -- Rect. Box Concrete -- 30° to 75° wingwall flares | 8 | Rect. Box Concrete | 1 | 30° to 75° wingwall flares | 1 | 0.026 | 1.0 | 0.0347 | 0.81 | 1, 3 | pendiente |
| 8 -- Rect. Box Concrete -- 90° and 15° wingwall flares | 8 | Rect. Box Concrete | 2 | 90° and 15° wingwall flares | 1 | 0.061 | 0.75 | 0.04 | 0.8 | 1, 3 | pendiente |
| 8 -- Rect. Box Concrete -- 0° wingwall flares | 8 | Rect. Box Concrete | 3 | 0° wingwall flares | 1 | 0.061 | 0.75 | 0.0423 | 0.82 | 1, 3 | pendiente |
| 9 -- Rect. Box Concrete -- 45° wingwall flare d = .043D | 9 | Rect. Box Concrete | 1 | 45° wingwall flare d = .043D | 2 | 0.51 | 0.667 | 0.0309 | 0.8 | 3 | pendiente |
| 9 -- Rect. Box Concrete -- 18° to 33.7° wingwall flare d = .083D | 9 | Rect. Box Concrete | 2 | 18° to 33.7° wingwall flare d = .083D | 2 | 0.486 | 0.667 | 0.0249 | 0.83 | 3 | pendiente |
| 10 -- Rect. Box Concrete -- 90° headwall w/3/4" chamfers | 10 | Rect. Box Concrete | 1 | 90° headwall w/3/4" chamfers | 2 | 0.515 | 0.667 | 0.0375 | 0.79 | 3 | pendiente |
| 10 -- Rect. Box Concrete -- 90° headwall w/45° bevels | 10 | Rect. Box Concrete | 2 | 90° headwall w/45° bevels | 2 | 0.495 | 0.667 | 0.0314 | 0.82 | 3 | pendiente |
| 10 -- Rect. Box Concrete -- 90° headwall w/33.7° bevels | 10 | Rect. Box Concrete | 3 | 90° headwall w/33.7° bevels | 2 | 0.486 | 0.667 | 0.0252 | 0.865 | 3 | pendiente |
| 11 -- Rect. Box Concrete -- 3/4" chamfers; 45° skewed headwall | 11 | Rect. Box Concrete | 1 | 3/4" chamfers; 45° skewed headwall | 2 | 0.545 | 0.667 | 0.04505 | 0.73 | 3 | pendiente |
| 11 -- Rect. Box Concrete -- 3/4" chamfers; 30° skewed headwall | 11 | Rect. Box Concrete | 2 | 3/4" chamfers; 30° skewed headwall | 2 | 0.533 | 0.667 | 0.0425 | 0.705 | 3 | pendiente |
| 11 -- Rect. Box Concrete -- 3/4" chamfers; 15° skewed headwall | 11 | Rect. Box Concrete | 3 | 3/4" chamfers; 15° skewed headwall | 2 | 0.522 | 0.667 | 0.0402 | 0.68 | 3 | pendiente |
| 11 -- Rect. Box Concrete -- 45° bevels; 10°-45° skewed headw. | 11 | Rect. Box Concrete | 4 | 45° bevels; 10°-45° skewed headw. | 2 | 0.498 | 0.667 | 0.0327 | 0.75 | 3 | pendiente |
| 12 -- Rect. Box 3/4" chamf. Conc. -- 45° non-offset wingwall flares | 12 | Rect. Box 3/4" chamf. Conc. | 1 | 45° non-offset wingwall flares | 2 | 0.497 | 0.667 | 0.0339 | 0.803 | 3 | pendiente |
| 12 -- Rect. Box 3/4" chamf. Conc. -- 18.4° non-offset wingwall flares | 12 | Rect. Box 3/4" chamf. Conc. | 2 | 18.4° non-offset wingwall flares | 2 | 0.493 | 0.667 | 0.0361 | 0.806 | 3 | pendiente |
| 12 -- Rect. Box 3/4" chamf. Conc. -- 18.4° non-offset wingwall flares 30° skewed barrel | 12 | Rect. Box 3/4" chamf. Conc. | 3 | 18.4° non-offset wingwall flares 30° skewed barrel | 2 | 0.495 | 0.667 | 0.0386 | 0.71 | 3 | pendiente |
| 13 -- Rect. Box Top Bev. Conc. -- 45° wingwall flares - offset | 13 | Rect. Box Top Bev. Conc. | 1 | 45° wingwall flares - offset | 2 | 0.497 | 0.667 | 0.0302 | 0.835 | 3 | pendiente |
| 13 -- Rect. Box Top Bev. Conc. -- 33.7° wingwall flares - offset | 13 | Rect. Box Top Bev. Conc. | 2 | 33.7° wingwall flares - offset | 2 | 0.495 | 0.667 | 0.0252 | 0.881 | 3 | pendiente |
| 13 -- Rect. Box Top Bev. Conc. -- 18.4° wingwall flares - offset | 13 | Rect. Box Top Bev. Conc. | 3 | 18.4° wingwall flares - offset | 2 | 0.493 | 0.667 | 0.0227 | 0.887 | 3 | pendiente |

> ¹²³⁴ Bossy 1963

### `HDS5_3ED.TB.1` — B.1.  Manning's n Values for Culverts.

- Cita: `HDS5_3ED.TB.1`
- Tabla completa · el calculo usa 4 de 5 columnas y 2 de 13 filas
- Columna «Reference» transcrita y **no usada**: bibliografia de la fuente: documenta de que ensayo sale cada rango, no entra en el calculo
- **Interpretación del proyectista, no de la fuente**: El par (minimo, maximo) de la fila «Corrugated Polyethylene / Smooth» se toma entero como la doble n del HDPE de interior liso: 0.015 para capacidad y tirante, 0.009 para velocidad maxima y socavacion
  - En contra: Son valores de LABORATORIO (nota 1): la fuente advierte que los de campo pueden variar por abrasion, corrosion, deflexion y juntas, y no dice hacia donde.
  - En contra: La fila vale para el interior LISO (tuberia Tipo S o D de M 294). Con interior corrugado (Tipo C) rige la fila siguiente, 0.018-0.025, y usar esta seria gruesamente inseguro en capacidad.
  - En contra: El rango es mas ancho que el del concreto de la Tabla N 09 peruana (0.010-0.013), que es el que el proyecto aplicaba por analogia: baja el n minimo y sube el maximo.

| Fila | Type of Culvert | Roughness or Corrugation | Manning's n | Manning's n | Reference | Uso |
|---|---|---|---|---|---|---|
| Concrete Pipe | Concrete Pipe | Smooth | 0.01 | 0.011 | Straub et al. 1960; May et al. 1986; Tullis 1986 & 1991a | no usada |
| Concrete Boxes | Concrete Boxes | Smooth | 0.012 | 0.015 | FHWA 1961 | usada |
| Spiral Rib Metal Pipe | Spiral Rib Metal Pipe | Smooth | 0.012 | 0.013 | Tullis 1983 & 1991b | no usada |
| Corrugated Metal Pipe (Helical Corrugations) | Corrugated Metal Pipe (Helical Corrugations) | 2-2/3 by 1/2 in 68 by 13 mm | 0.011 | 0.023 | FHWA 1980; Tullis 1991c | no usada |
| Corrugated Metal Pipe (Helical Corrugations) | Corrugated Metal Pipe (Helical Corrugations) | 6 by 1 in 150 by 25 mm | 0.022 | 0.025 | FHWA 1980 | no usada |
| Corrugated Metal Pipe, Pipe-Arch and Box (Annular Corrugations) | Corrugated Metal Pipe, Pipe-Arch and Box (Annular Corrugations) | 2-2/3 by 1/2 in 68 by 13 mm | 0.022 | 0.027 | FHWA 1980 | no usada |
| Corrugated Metal Pipe, Pipe-Arch and Box (Annular Corrugations) | Corrugated Metal Pipe, Pipe-Arch and Box (Annular Corrugations) | 5 by 1 in 125 by 25 mm | 0.025 | 0.026 | FHWA 1980 | no usada |
| Corrugated Metal Pipe, Pipe-Arch and Box (Annular Corrugations) | Corrugated Metal Pipe, Pipe-Arch and Box (Annular Corrugations) | 3 by 1 in 75 by 25 mm | 0.027 | 0.028 | FHWA 1980 | no usada |
| Corrugated Metal Structural Plate (Annular Corrugations) | Corrugated Metal Structural Plate (Annular Corrugations) | 6 by 2 in 150 by 50 mm | 0.033 | 0.035 | FHWA 1980 | no usada |
| Corrugated Metal Structural Plate (Annular Corrugations) | Corrugated Metal Structural Plate (Annular Corrugations) | 9 by 2-1/2 in 230 by 64 mm | 0.033 | 0.037 | FHWA 1980 | no usada |
| Corrugated Polyethylene | Corrugated Polyethylene | Smooth | 0.009 | 0.015 | Barfuss & Tullis 1988; Tullis et al. 1990 | usada |
| Corrugated Polyethylene | Corrugated Polyethylene | Corrugated | 0.018 | 0.025 | Clyde 1980; USBR 1985 | no usada |
| Polyvinyl chloride (PVC) | Polyvinyl chloride (PVC) | Smooth | 0.009 | 0.011 | Neale and Price 1964; Bishop and Jeppson 1975 | no usada |

> 1 The Manning's n values indicated in this table were obtained in the laboratory and are supported by the provided reference. Actual field values for culverts may vary depending on the effect of abrasion, corrosion, deflection, and joint conditions.

> 2 See Figure B.3, Manning's n varies with barrel size.

### `HDS5_3ED.TC2` — Table C.2.  Entrance Loss Coefficients.

- Cita: `HDS5_3ED.TC.2`
- Transcripcion acotada · el calculo usa 2 de 2 columnas y 2 de 22 filas
- **Transcripción acotada.** Razón: desde C2 la transcripcion cubre las tres familias que la tabla imprime: «Pipe, Concrete», «Pipe. or Pipe-Arch. Corrugated Metal» y «Box, Reinforced Concrete». Lo que queda fuera ya no es una familia entera sino la eleccion de borde dentro de cada una, y eso no lo decide el alcance de la transcripcion sino el criterio que elige la embocadura
  - Qué queda fuera: nada del cuerpo de la tabla: las tres familias estan transcritas enteras -- nueve filas de tubo de concreto, seis de metal corrugado y siete de cajon de concreto bajo sus cuatro rotulos de agrupacion, 22 filas con coeficiente en total --. Fuera queda la formula H_e = Ke(V^2/2g) del encabezado, que la pagina imprime como imagen y que M4 implementa en `perdida_carga`
  - Dónde leerlo: HDS-5 3a ed., Tabla C.2, pag. impresa C.6 (PDF 216)
- Fila «Box, Reinforced Concrete -- Headwall parallel to embankment (no wingwalls) -- Square-edged on 3 edges»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Fila «Box, Reinforced Concrete -- Headwall parallel to embankment (no wingwalls) -- Rounded on 3 edges to radius of D/12 or B/12 or beveled edges on 3 sides»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Fila «Box, Reinforced Concrete -- Wingwalls at 30⁰ to 75⁰ to barrel -- Square-edged at crown»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Fila «Box, Reinforced Concrete -- Wingwalls at 30⁰ to 75⁰ to barrel -- Crown edge rounded to radius of D/12 or beveled top edge»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Fila «Box, Reinforced Concrete -- Wingwall at 10⁰ to 25⁰ to barrel -- Square-edged at crown»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Fila «Box, Reinforced Concrete -- Wingwalls parallel (extension of sides) -- Square-edged at crown»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Fila «Box, Reinforced Concrete -- Wingwalls parallel (extension of sides) -- Side- or slope-tapered inlet»: **elección pendiente** (`COND-EMBOCADURA-CAJON-KE`)
- Vistas de cálculo derivadas: `KE_HDS5_C2`

| Fila | Type of Structure and Design of Entrance | Coefficient Ke | Uso |
|---|---|---|---|
| Pipe, Concrete -- Projecting from fill, socket end (groove-end) |  | 0.2 | no usada |
| Pipe, Concrete -- Projecting from fill, sq. cut end |  | 0.5 | no usada |
| Pipe, Concrete -- Headwall or headwall and wingwalls -- Socket end of pipe (groove-end |  | 0.2 | no usada |
| Pipe, Concrete -- Headwall or headwall and wingwalls -- Square-edge |  | 0.5 | usada |
| Pipe, Concrete -- Rounded (radius = D/12 |  | 0.2 | no usada |
| Pipe, Concrete -- Mitered to conform to fill slope |  | 0.7 | no usada |
| Pipe, Concrete -- *End-Section conforming to fill slope |  | 0.5 | no usada |
| Pipe, Concrete -- Beveled edges, 33.7⁰ or 45⁰ bevels |  | 0.2 | no usada |
| Pipe, Concrete -- Side- or slope-tapered inlet |  | 0.2 | no usada |
| Pipe. or Pipe-Arch. Corrugated Metal -- Projecting from fill (no headwall) |  | 0.9 | no usada |
| Pipe. or Pipe-Arch. Corrugated Metal -- Headwall or headwall and wingwalls square-edge |  | 0.5 | usada |
| Pipe. or Pipe-Arch. Corrugated Metal -- Mitered to conform to fill slope, paved or unpaved slope |  | 0.7 | no usada |
| Pipe. or Pipe-Arch. Corrugated Metal -- *End-Section conforming to fill slope |  | 0.5 | no usada |
| Pipe. or Pipe-Arch. Corrugated Metal -- Beveled edges, 33.7⁰ or 45⁰ bevels |  | 0.2 | no usada |
| Pipe. or Pipe-Arch. Corrugated Metal -- Side- or slope-tapered inlet |  | 0.2 | no usada |
| Box, Reinforced Concrete -- Headwall parallel to embankment (no wingwalls) -- Square-edged on 3 edges |  | 0.5 | pendiente |
| Box, Reinforced Concrete -- Headwall parallel to embankment (no wingwalls) -- Rounded on 3 edges to radius of D/12 or B/12 or beveled edges on 3 sides |  | 0.2 | pendiente |
| Box, Reinforced Concrete -- Wingwalls at 30⁰ to 75⁰ to barrel -- Square-edged at crown |  | 0.4 | pendiente |
| Box, Reinforced Concrete -- Wingwalls at 30⁰ to 75⁰ to barrel -- Crown edge rounded to radius of D/12 or beveled top edge |  | 0.2 | pendiente |
| Box, Reinforced Concrete -- Wingwall at 10⁰ to 25⁰ to barrel -- Square-edged at crown |  | 0.5 | pendiente |
| Box, Reinforced Concrete -- Wingwalls parallel (extension of sides) -- Square-edged at crown |  | 0.7 | pendiente |
| Box, Reinforced Concrete -- Wingwalls parallel (extension of sides) -- Side- or slope-tapered inlet |  | 0.2 | pendiente |

> * Note: "End Sections conforming to fill slope," made of either metal or concrete, are the sections commonly available from manufacturers.  From limited hydraulic tests they are equivalent in operation to a headwall in both inlet and outlet control.

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

### `MC_HHD.T03` — TABLA Nº 03: Valores críticos d para la prueba Kolmogorov – Smirnov

- Cita: `MC_HHD.3.7.2b#T03`
- Tabla completa · el calculo usa 4 de 4 columnas y 8 de 8 filas
- Fuente que la tabla se atribuye: *Aparicio, 1999.*
- **Laguna de la fuente**: un tamaño de muestra que no sea uno de los ocho tabulados (5, 10, ..., 40), y todo n mayor de 40. La pagina no manda interpolar ni da la expresion para muestras grandes, y una serie de maximas anuales casi nunca tiene un n multiplo de cinco. Se cierra con: el proyecto NO interpola ni extrapola la tabla: calcula el valor critico EXACTO del mismo estadistico para el n de la serie (el cuantil 1 − α de la distribucion bilateral de Kolmogorov-Smirnov para muestra finita, `scipy.stats.kstwo`), que es una identidad matematica y no un valor adoptado. Lo que lo autoriza es que ese calculo REPRODUCE las veinticuatro celdas impresas a sus dos decimales, comprobado celda a celda en tests/test_t1_hidrologia.py: la tabla es ese cuantil redondeado. En un n tabulado se usa la celda impresa (`MH_hidrologia.valor_critico_ks`)
- Vistas de cálculo derivadas: `TABLA_03_KS`

| Fila | TAMAÑO DE LA MUESTRA | α = 0.10 | α = 0.05 | α = 0.01 | Uso |
|---|---|---|---|---|---|
| 5 | 5 | 0.51 | 0.56 | 0.67 | usada |
| 10 | 10 | 0.37 | 0.41 | 0.49 | usada |
| 15 | 15 | 0.3 | 0.34 | 0.4 | usada |
| 20 | 20 | 0.26 | 0.29 | 0.35 | usada |
| 25 | 25 | 0.24 | 0.26 | 0.32 | usada |
| 30 | 30 | 0.22 | 0.24 | 0.29 | usada |
| 35 | 35 | 0.2 | 0.22 | 0.27 | usada |
| 40 | 40 | 0.19 | 0.21 | 0.25 | usada |

### `MC_HHD.T04` — TABLA Nº 04: Coeficientes de duración lluvias entre 48 horas y una hora

- Cita: `MC_HHD.3.8.1#T04`
- Tabla completa · el calculo usa 2 de 2 columnas y 16 de 16 filas
- Fuente que la tabla se atribuye: *Manual para el Diseño de Carreteras Pavimentadas de Bajo Volumen de Tránsito*
- **Laguna de la fuente**: las duraciones que no son una de las dieciseis tabuladas: la pagina no dice que se interpole entre filas. Se cierra con: interpolacion LINEAL entre las dos filas vecinas, que es lectura del proyecto y se imprime como tal en el paso. Solo se alcanza si el criterio 'relacion_intensidad_duracion' elige esta tabla; el valor de archivo es la relacion de Dick y Peschke, que no necesita interpolar (`criterios_adoptados['relacion_intensidad_duracion']`)
- **Laguna de la fuente**: las duraciones MENORES de una hora, que son las de casi toda cuenca pequeña y de toda cuneta: la tabla empieza en 1 hora y su titulo lo dice. Se cierra con: ninguna: por debajo de una hora la tabla no se extrapola y el calculo se detiene remitiendo a la relacion de Dick y Peschke, que es la que el mismo numeral nombra para ese caso (`criterios_adoptados['relacion_intensidad_duracion']`)
- Vistas de cálculo derivadas: `TABLA_04_COEFICIENTES_DE_DURACION`

| Fila | DURACIÓN DE LA PRECIPITACIÓN EN HORAS | COEFICIENTE | Uso |
|---|---|---|---|
| 1 | 1 | 0.25 | usada |
| 2 | 2 | 0.31 | usada |
| 3 | 3 | 0.38 | usada |
| 4 | 4 | 0.44 | usada |
| 5 | 5 | 0.5 | usada |
| 6 | 6 | 0.56 | usada |
| 8 | 8 | 0.64 | usada |
| 10 | 10 | 0.73 | usada |
| 12 | 12 | 0.79 | usada |
| 14 | 14 | 0.83 | usada |
| 16 | 16 | 0.87 | usada |
| 18 | 18 | 0.9 | usada |
| 20 | 20 | 0.93 | usada |
| 22 | 22 | 0.97 | usada |
| 24 | 24 | 1.0 | usada |
| 48 | 48 | 1.32 | usada |

### `MC_HHD.T05` — TABLA Nº 05: Fórmulas para el cálculo del tiempo de concentración

- Cita: `MC_HHD.3.9#T05`
- Tabla completa · el calculo usa 3 de 3 columnas y 4 de 6 filas
- Fuente que la tabla se atribuye: ** SCS   Soil Conservation Service*
- **Afirmación negativa**: la Tabla Nº 05 no lista la formula de Temez. Sus seis filas son Kirpich, California Culverts Practice, Izzard, Federal Aviation Administration, onda cinematica y retardo SCS. Ámbito barrido: la tabla entera, pags. impresas 39 y 40 (PDF 42 y 43), en texto y en imagen; y el Manual entero por la cadena «mez»: Temez solo aparece en el num. 3.12.2.1, pag. impresa 50 (PDF 53)
- **Afirmación negativa**: ni la Tabla Nº 05 ni el resto del Manual fijan una duracion minima de la lluvia de diseño ni un tiempo de concentracion minimo. Ámbito barrido: el Manual entero, 225 paginas, por las cadenas «mínim» y «minut» junto a «concentración» y «duración»
- Vistas de cálculo derivadas: `TC_KIRPICH_SI`, `TC_CALIFORNIA_SI`, `TC_FAA_SI`, `TC_RETARDO_SCS_SI`

| Fila | MÉTODO Y FECHA | FÓRMULA PARA tc (minutos) | OBSERVACIONES | Uso |
|---|---|---|---|---|
| Kirpich (1940) | Kirpich (1940) | tc = 0.01947 · L^0.77 · S^-0.385 ; L = longitud del canal desde aguas arriba hasta la salida, m ; S = pendiente promedio de la cuenca, m/m | Desarrollada a partir de información del SCS en siete cuencas rurales de Tennessee con canales bien definidos y pendientes empinadas (3 a 10%); para flujo superficial en superficies de concreto o asfalto se debe multiplicar tc por 0.4; para canales de concreto se debe multiplicar por 0.2; no se debe hacer ningún ajuste para flujo superficial en suelo descubierto o para flujo en cunetas. | usada |
| California Culverts Practice (1942) | California Culverts Practice (1942) | tc = 0.0195 · (L^3 / H)^0.385 ; L = longitud del curso de agua más largo, m ; H = diferencia de nivel entre la divisoria de aguas y la salida, m | Esencialmente es la ecuación de Kirpich; desarrollada para pequeñas cuencas montañosas en California. | usada |
| Izzard (1946) | Izzard (1946) | tc = 525 · (0.0000276·i + c) · L^0.33 / (S^0.333 · i^0.667) ; i = intensidad de lluvia, mm/h ; c = coeficiente de retardo ; L = longitud de la trayectoria de flujo, m ; S = pendiente de la trayectoria de flujo, m/m | Desarrollada experimentalmente en laboratorio por el Bureau of Public Roads para flujo superficial en caminos y Áreas de céspedes; los valores del coeficiente de retardo varían desde 0.0070 para pavimentos muy lisos hasta 0.012 para pavimentos de concreto y 0.06 para superficies densamente cubiertas de pasto; la solución requiere de procesos iterativos; el producto de i por L debe ser ≤ 3800. | no usada |
| Federal Aviation Administration (1970) | Federal Aviation Administration (1970) | tc = 0.7035 · (1.1 − C) · L^0.50 / S^0.333 ; C = coeficiente de escorrentía del método racional ; L = longitud del flujo superficial, m ; S = pendiente de la superficie, m/m | Desarrollada de información sobre el drenaje de aeropuertos recopilada por el Corps of Engineers: el método tiene como finalidad el ser usado en problemas de drenaje de aeropuertos pero ha sido frecuentemente usado para flujo superficial en cuencas urbanas. | usada |
| Ecuaciones de onda cinemática Morgali y Linsley (1965) Aron y Erborge (1973) | Ecuaciones de onda cinemática | tc = 7 · L^0.6 · n^0.6 / (I^0.4 · S^0.3) ; L = longitud del flujo superficial, m ; n = coeficiente de rugosidad de Manning ; I = intensidad de lluvia, mm/h ; S = pendiente promedio del terreno, m/m | Ecuación para flujo superficial desarrollada a partir de análisis de onda cinemática de la escorrentía superficial desde superficies desarrolladas; el método requiere iteraciones debido a que tanto I (Intensidad de lluvia) como tc son desconocidos, la superposición de una curva de intensidad – duración – frecuencia da una solución gráfica directa para tc. | no usada |
| Ecuación de retardo SCS (1973) | Ecuación de retardo SCS (1973) | tc = 0.0136 · L^0.8 · (1000/CN − 9)^0.7 / S^0.5 ; L = longitud hidráulica de la cuenca (mayor trayectoria de flujo), m ; CN = Número de curva SCS ; S = pendiente promedio de la cuenca, m/m | Ecuación desarrollada por el SCS a partir de información de cuencas de uso agrícola; ha sido adaptada a pequeñas cuencas urbanas con áreas inferiores a 800 Ha; se ha encontrado que generalmente es buena cuando el área se encuentra completamente pavimentada; para áreas mixtas tiene tendencia a la sobreestimación; se aplican factores de ajuste para corregir efectos de mejoras en canales e impermeabilización de superficies; la ecuación supone que tc = 1.67 x retardo de la cuenca. | usada |

### `MC_HHD.T08` — TABLA Nº 08:   Coeficientes de escorrentía método racional

- Cita: `MC_HHD.3.12.2#T08`
- Tabla completa · el calculo usa 5 de 5 columnas y 15 de 15 filas
- **Laguna de la fuente**: una pendiente del terreno de EXACTAMENTE 1 %: la columna «SUAVE» se rotula «> 1%» y la «DESPRECIABLE» «< 1%», las dos con desigualdad estricta. Las otras tres fronteras (5, 20 y 50 %) si quedan cubiertas: «> 5%» deja el 5 % exacto en la columna anterior. Se cierra con: el proyecto lee la columna «SUAVE», que es la de mayor coeficiente y por tanto el lado conservador (mas caudal), y el paso lo imprime (`MH_hidrologia.clase_de_pendiente`)
- **Afirmación negativa**: la Tabla Nº 08 no tiene fila de pavimento, de plataforma ni de talud de terraplen: sus cinco coberturas son Sin vegetación, Cultivos, Pastos y vegetación ligera, Hierba y grama, y Bosques y densa vegetación. Ámbito barrido: la tabla entera, pag. impresa 50 (PDF 53), en texto y en imagen; y el num. 4.1.2.1 b) «Caudal Q de aporte» (pag. impresa 177), que pide el «Coeficiente de escurrimiento de la cuenca» sin dar tabla propia para la plataforma
- **Interpretación del proyectista, no de la fuente**: La columna se elige con la pendiente del TERRENO de la cuenca, que el CSV de cuencas trae en la columna obligatoria `S_terreno`. El programa NO entra a la tabla con la pendiente del cauce (`S_cauce_cuenca`): son dos magnitudes y la una no rellena a la otra.
  - En contra: pide al estudio hidrologico un dato mas por cuenca: una cuenca sin pendiente media del terreno medida no se calcula, aunque su cauce si tenga pendiente
  - A favor: la tabla dice «PENDIENTE DEL TERRENO» y no «del cauce»
  - A favor: la pendiente del cauce principal es, en general, MENOR que la pendiente media del terreno de su cuenca: leer la tabla con ella puede caer una columna a la derecha y dar un coeficiente menor, que es el lado NO conservador. Hasta la auditoria de T-1 el programa hacia eso cuando la celda iba vacia
- Vistas de cálculo derivadas: `TABLA_08_COEFICIENTE_DE_ESCORRENTIA`, `TABLA_08_PENDIENTES`

| Fila | PRONUNCIADA > 50% | ALTA > 20% | MEDIA > 5% | SUAVE > 1% | DESPRECIABLE < 1% | Uso |
|---|---|---|---|---|---|---|
| Sin vegetación -- Impermeable | 0.8 | 0.75 | 0.7 | 0.65 | 0.6 | usada |
| Sin vegetación -- Semipermeable | 0.7 | 0.65 | 0.6 | 0.55 | 0.5 | usada |
| Sin vegetación -- Permeable | 0.5 | 0.45 | 0.4 | 0.35 | 0.3 | usada |
| Cultivos -- Impermeable | 0.7 | 0.65 | 0.6 | 0.55 | 0.5 | usada |
| Cultivos -- Semipermeable | 0.6 | 0.55 | 0.5 | 0.45 | 0.4 | usada |
| Cultivos -- Permeable | 0.4 | 0.35 | 0.3 | 0.25 | 0.2 | usada |
| Pastos, vegetación ligera -- Impermeable | 0.65 | 0.6 | 0.55 | 0.5 | 0.45 | usada |
| Pastos, vegetación ligera -- Semipermeable | 0.55 | 0.5 | 0.45 | 0.4 | 0.35 | usada |
| Pastos, vegetación ligera -- Permeable | 0.35 | 0.3 | 0.25 | 0.2 | 0.15 | usada |
| Hierba, grama -- Impermeable | 0.6 | 0.55 | 0.5 | 0.45 | 0.4 | usada |
| Hierba, grama -- Semipermeable | 0.5 | 0.45 | 0.4 | 0.35 | 0.3 | usada |
| Hierba, grama -- Permeable | 0.3 | 0.25 | 0.2 | 0.15 | 0.1 | usada |
| Bosques, densa vegetación -- Impermeable | 0.55 | 0.5 | 0.45 | 0.4 | 0.35 | usada |
| Bosques, densa vegetación -- Semipermeable | 0.45 | 0.4 | 0.35 | 0.3 | 0.25 | usada |
| Bosques, densa vegetación -- Permeable | 0.25 | 0.2 | 0.15 | 0.1 | 0.05 | usada |

### `MC_HHD.T09` — TABLA  Nº  09:  Valores del Coeficiente de Rugosidad de Manning (n)

- Cita: `MC_HHD.4.1.1.3.6#T09`
- Transcripcion acotada · el calculo usa 3 de 4 columnas y 2 de 5 filas
- Fuente que la tabla se atribuye: *Hidráulica de Canales Abiertos, Ven Te Chow, 1983.*
- **Transcripción acotada.** Razón: el grupo A es el unico de la tabla que describe una alcantarilla; los grupos B (canales revestidos o desarmables), C (excavado o dragado) y D (corrientes naturales) describen el CAUCE, no el conducto, y ningun modulo dimensiona un cauce. Dentro del grupo A se transcriben las cuatro subfilas que el catalogo de la Sec. 3.2 puede alcanzar
  - Qué queda fuera: del grupo A: «a. Bronce Polido», «b. Acero» (soldado, con remaches), las CINCO subfilas restantes de «a. Concreto» -- «tubo con curvas, conexiones», «tubo de alcantarillado con cámaras, entradas.», «Tubo con moldaje de acero.», «Tubo de moldaje madera cepillada» y «Tubo con moldaje madera en bruto» --, la «laminada y tratada» de «b. Madera» y «c. Albañilería de piedra.». Fuera del grupo A: «B.CANALES REVESTIDOS», «C. EXCAVADO» y «D. CORRIENTES NATURALES». (Eran seis subfilas de «a. Concreto» hasta C2, que transcribio «afinado».)
  - Dónde leerlo: MC_HHD, num. 4.1.1.3.6, Tabla Nº 09: los grupos A, B y C en la pag. impresa 75 (PDF 78) y el grupo D con la linea de Fuente en la 76 (PDF 79)
- Columna «NORMAL» transcrita y **no usada**: la regla de doble n (Sec. 4.1 de la hoja de ruta) no pide el valor corriente sino los dos EXTREMOS -- n maximo para capacidad y tirante, n minimo para velocidad maxima y socavacion --, de modo que cada verificacion se resuelve con el extremo que la deja del lado seguro. El valor NORMAL entraria en un calculo de un solo n, que es justo lo que la regla prohibe
- Fila «A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.2 NO METÁLICOS -- a. Concreto -- afinado»: **elección pendiente** (`COND-N-MANNING-CAJON`)
- **Afirmación negativa**: la Tabla Nº 09 no lista HDPE. Ámbito barrido: las 225 paginas del PDF: «HDPE» aparece 0 veces y «polietileno» solo en la pag. impresa 71 (listado de tipos de alcantarilla) y en la de subdrenes. Ninguna fila de la Tabla Nº 09 lo nombra
- **Errata declarada**: `DIS-MCHHD-T09-A2-DESPLAZADA`
- Vistas de cálculo derivadas: `TABLA_09_FILAS`, `MANNING`

| Fila | TIPO DE CANAL | MÍNIMO | NORMAL | MÁXIMO | Uso |
|---|---|---|---|---|---|
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.1. METÁLICOS -- c. Metal corrugado -- sub - dren |  | 0.017 | 0.019 | 0.021 | no usada |
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.1. METÁLICOS -- c. Metal corrugado -- dren para aguas lluvias |  | 0.021 | 0.024 | 0.03 | usada |
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.2 NO METÁLICOS -- a. Concreto -- tubo recto y libre de basuras |  | 0.01 | 0.011 | 0.013 | usada |
| A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO -- A.2 NO METÁLICOS -- a. Concreto -- afinado |  | 0.011 | 0.012 | 0.014 | pendiente |
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

### `MC_HHD.T11` — TABLA  Nº  11:   Velocidades  máximas  admisibles (m/s) en canales no revestidos

- Cita: `MC_HHD.4.1.1.3.6#T11`
- Tabla completa · el calculo usa 3 de 3 columnas y 13 de 13 filas
- Fuente que la tabla se atribuye: *Manual de Carreteras de California*
- Vistas de cálculo derivadas: `V_MAX_NO_REVESTIDOS`

| Fila | TIPO DE TERRENO | FLUJO  INTERMITENTE (M/S) | FLUJO  PERMANENTE (M/S) | Uso |
|---|---|---|---|---|
| Arena fina (no coloidal) |  | 0.75 | 0.75 | usada |
| Arcilla arenosa (no coloidal) |  | 0.75 | 0.75 | usada |
| Arcilla limosa (no coloidal) |  | 0.9 | 0.9 | usada |
| Arcilla fina |  | 1.0 | 1.0 | usada |
| Ceniza volcánica |  | 1.2 | 1.0 | usada |
| Grava fina |  | 1.5 | 1.2 | usada |
| Arcilla dura (coloidal) |  | 1.8 | 1.4 | usada |
| Material graduado (no coloidal) -- Desde arcilla a grava |  | 2.0 | 1.5 | usada |
| Material graduado (no coloidal) -- Desde limo a grava |  | 2.1 | 1.7 | usada |
| Material graduado (no coloidal) -- Grava |  | 2.3 | 1.8 | usada |
| Material graduado (no coloidal) -- Grava gruesa |  | 2.4 | 2.0 | usada |
| Material graduado (no coloidal) -- Desde grava a piedras (< 15 cm) |  | 2.7 | 2.1 | usada |
| Material graduado (no coloidal) -- Desde grava a piedras (> 20 cm) |  | 3.0 | 2.4 | usada |

### `MC_HHD.T32` — TABLA  Nº  32:  Valores de K más usados

- Cita: `MC_HHD.4.1.2.1#T32`
- Tabla completa · el calculo usa 2 de 2 columnas y 3 de 3 filas
- Fuente que la tabla se atribuye: *Ingeniería Vial I de Hugo Morales Sosa*
- Vistas de cálculo derivadas: `CUNETA_STRICKLER_T32`

| Fila | Cunetas | K | Uso |
|---|---|---|---|
| Cunetas excavadas en el terreno |  | 33 | usada |
| Cunetas en roca |  | 25 | usada |
| Cunetas de concreto |  | 67 | usada |

### `MC_HHD.T33` — TABLA Nº  33: Velocidades límites admisibles

- Cita: `MC_HHD.4.1.2.1#T33`
- Tabla completa · el calculo usa 2 de 2 columnas y 8 de 8 filas
- Fuente que la tabla se atribuye: *Manual de Diseño de Carreteras Pavimentadas de Bajo Volumen de Tránsito-MTC*
- Vistas de cálculo derivadas: `CUNETA_VELOCIDAD_LIMITE_T33`

| Fila | TIPO DE SUPERFICIE | VELOCIDAD LÍMITE ADMISIBLE (M/S) | Uso |
|---|---|---|---|
| Arena fina o limo (poca o ninguna arcilla) |  | 0.2 – 0.6 | usada |
| Arena arcillosa dura, margas duras |  | 0.6 – 0.9 | usada |
| Terreno parcialmente cubierto de vegetación |  | 0.6 – 1.2 | usada |
| Arcilla grava, pizarras blandas con cubierta vegetal |  | 1.2 – 1.5 | usada |
| Hierba |  | 1.2 – 1.8 | usada |
| Conglomerado, pizarras duras, rocas blandas |  | 1.4 – 2.4 | usada |
| Mampostería, rocas duras |  | 3.0 – 4.5 | usada |
| Concreto |  | 4.5 – 6.0 | usada |

> * * Para flujos de muy corta duración

### `MC_HHD.T34` — TABLA  Nº  34:  Dimensiones  mínimas

- Cita: `MC_HHD.4.1.2.1c#T34`
- Tabla completa · el calculo usa 3 de 3 columnas y 3 de 4 filas
- Fuente que la tabla se atribuye: *Manual de Diseño de Carreteras Pavimentadas de Bajo Volumen de Tránsito-MTC*
- Vistas de cálculo derivadas: `CUNETA_DIMENSIONES_MINIMAS_T34`

| Fila | REGIÓN | PROFUNDIDAD (D) (M) | ANCHO (A) (M) | Uso |
|---|---|---|---|---|
| Seca (<400 mm/año) |  | 0.2 | 0.5 | usada |
| Lluviosa (De 400 a <1600 mm/año) |  | 0.3 | 0.75 | usada |
| Muy lluviosa (De 1600 a <3000 mm/año) |  | 0.4 | 1.2 | usada |
| Muy lluviosa (>3000 mm/año) |  | 0.3 | 1.2 | no usada |

> * * Sección Trapezoidal con un ancho mínimo de fondo de 0.30

### `MP.TCOMB` — Tabla 2.4.5.3.1-1 Combinaciones de Carga y Factores de Carga

- Cita: `MP.T2.4.5.3.1-1`
- Transcripcion acotada · el calculo usa 4 de 14 columnas y 3 de 3 filas
- **Transcripción acotada.** Razón: la Sec. 9.2 de la hoja de ruta nombra TRES combinaciones -- Resistencia I, Servicio I y Evento Extremo I -- y ninguna fase del proyecto evalua las otras diez
  - Qué queda fuera: Resistencia II, III, IV y V; Evento Extremo II; Servicio II, III y IV; Fatiga I y Fatiga II
  - Dónde leerlo: Manual de Puentes, num. 2.4.5.3.1, Tabla 2.4.5.3.1-1, pag. impresa 143 (PDF 144)
- Columna «WS» transcrita y **no usada**: ninguna fase evalua viento sobre la estructura
- Columna «WL» transcrita y **no usada**: ninguna fase evalua viento sobre la carga viva
- Columna «FR» transcrita y **no usada**: ninguna fase evalua friccion
- Columna «TU» transcrita y **no usada**: ninguna fase evalua temperatura uniforme
- Columna «TG» transcrita y **no usada**: ninguna fase evalua gradiente termico
- Columna «SE» transcrita y **no usada**: ninguna fase evalua asentamiento diferencial
- Columna «BL» transcrita y **no usada**: ninguna fase evalua explosion
- Columna «IC» transcrita y **no usada**: ninguna fase evalua carga de hielo
- Columna «CT» transcrita y **no usada**: ninguna fase evalua colision de vehiculo
- Columna «CV» transcrita y **no usada**: ninguna fase evalua colision de embarcacion
- Vistas de cálculo derivadas: `TABLA_COMBINACIONES_FILAS`

| Fila | DC DD DW EH EV ES EL PS CR SH | LL IM CE BR PL LS | WA | WS | WL | FR | TU | TG | SE | EQ | BL | IC | CT | CV | Uso |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Resistencia I | -> | 1.75 | 1.0 / 1.0 | -- | -- | 1.0 | 0.5 / 1.2 | gamma_TG | gamma_SE | -- | -- | -- | -- | -- | usada |
| Servicio I | 1.0 / 1.0 | 1.0 | 1.0 / 1.0 | 0.3 | 1.0 | 1.0 | 1.0 / 1.2 | gamma_TG | gamma_SE | -- | -- | -- | -- | -- | usada |
| Evento Extremo I | 1.0 / 1.0 | gamma_EQ | 1.0 / 1.0 | -- | -- | 1.0 | -- | -- | -- | 1.0 / 1.0 | -- | -- | -- | -- | usada |

>  Usar solamente uno de los indicados en estas columnas en cada combinación

### `MP.TFPGA` — Tabla 2.4.3.11.2.1.2-1 Valores de Factor de Sitio, F_pga En Periodo-Cero en el Espectro de Aceleracion

- Cita: `MP.T2.4.3.11.2.1.2-1`
- Tabla completa · el calculo usa 5 de 6 columnas y 4 de 6 filas
- Columna «Clase de Sitio»: **elección pendiente** (`COND-CLASE-DE-SITIO`) — el cálculo se detiene
- Fila «E»: **elección pendiente** (`COND-CLASE-DE-SITIO`)
- Fila «F»: **elección pendiente** (`COND-CLASE-DE-SITIO`)
- **Laguna de la fuente**: un PGA de EXACTAMENTE 0.50. La ultima columna se rotula «PGA > 0.50», desigualdad estricta, y la anterior es «PGA = 0.40»: la tabla no dice si el borde se lee en la ultima columna o se interpola contra la anterior. EL PGA DE ESTE PROYECTO CAE JUSTO AHI, de modo que no es un caso teorico. Se cierra con: un criterio [A] declarado, no un `>=` del codigo: la decision es del proyectista porque la fuente no la toma (`criterios_adoptados['F_pga_lectura_columna_extrema']`)
- **Afirmación negativa**: el Manual no dice como se lee un PGA exactamente igual a un rotulo extremo de la Tabla 2.4.3.11.2.1.2-1 (0.10 o 0.50 exactos): su Nota 1 manda interpolar en linea recta para valores intermedios de PGA sin nombrar los puntos entre los que se interpola, sus dos rotulos extremos son desigualdades estrictas que no cubren su propio limite, y el articulado del num. 2.4.3.11.2.1.2 presenta las tablas sin regla de lectura de bordes. Tratar los cinco numeros de los rotulos como nodos de la interpolacion -- y en particular suponer que la columna extrema aplica en su propio limite -- es inferencia del lector, no texto de la fuente. Ámbito barrido: las paginas PDF 121 a 126 (impresas 120 a 125), las seis sobre pagina renderizada y la de la tabla ademas en recorte ampliado y en texto plano: numerales 2.4.3.10.3 a 2.4.3.11.5 completos, incluido el 2.4.3.11.2.1.2 «Factores de Sitio» con sus dos parrafos y sus tres tablas con sus notas. Nada en ese ambito trae regla de borde. El contraste que muestra que la desigualdad estricta es deliberada y no tipografia: la Tabla 2.4.3.11.5-1 (impresa 125, PDF 126) si imprime el signo de menor o igual cuando quiere decirlo. Fuera de esas paginas no se barrio
- Vistas de cálculo derivadas: `F_PGA_TABLA`

| Fila | Clase de Sitio | PGA < 0.10 | PGA = 0.20 | PGA = 0.30 | PGA = 0.40 | PGA > 0.50 | Uso |
|---|---|---|---|---|---|---|---|
| A |  | 0.8 | 0.8 | 0.8 | 0.8 | 0.8 | usada |
| B |  | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | usada |
| C |  | 1.2 | 1.2 | 1.1 | 1.0 | 1.0 | usada |
| D |  | 1.6 | 1.4 | 1.2 | 1.1 | 1.0 | usada |
| E |  | 2.5 | 1.7 | 1.2 | 0.9 | 0.9 | pendiente |
| F |  | * | * | * | * | * | pendiente |

> 1 Usar línea recta de interpolación para valores intermedios de PGA.

> 2 Llevar a cabo investigaciones geotecnicas especificas del sitio y análisis de respuesta dinámica de sitio, para todos los sitios en sitio clase F

### `MP.TGAMMA_P` — Tabla 2.4.5.3.1-2 Factores de carga para cargas permanentes, γp

- Cita: `MP.T2.4.5.3.1-2`
- Tabla completa · el calculo usa 3 de 3 columnas y 6 de 18 filas
- **Errata declarada**: `DIS-MP-ERRATAS-GAMMA-P`
- Vistas de cálculo derivadas: `TABLA_GAMMA_P_FILAS`

| Fila | Tipo de Carga, Tipo de Fundaciones, y Métodos Usados para Fuerza de Arrastre Hacia Abajo (Downdrag) | Maximo | Mínimo | Uso |
|---|---|---|---|---|
| DC: Componentes y Auxiliares. |  | 1.25 | 0.9 | no usada |
| DC: Resistencia IV Solamente. |  | 1.5 | 0.9 | no usada |
| DD: Downdrag -- Pilotes, α Método de Tomlinson. |  | 1.4 | 0.25 | no usada |
| DD: Downdrag -- Pilotes, λ Método. |  | 1.05 | 0.3 | no usada |
| DD: Downdrag -- Pilotes Perforados, (Drilled Shaft) Método de O’Neill and Reese (1999). |  | 1.25 | 0.35 | no usada |
| DW: Superficie de rodadura y accesorios. |  | 1.5 | 0.65 | no usada |
| EH: Presión Horizontal de la tierra. -- Activa. |  | 1.5 | 0.9 | usada |
| EH: Presión Horizontal de la tierra. -- En reposo. |  | 1.35 | 0.9 | no usada |
| EH: Presión Horizontal de la tierra. -- AEP Para paredes ancladas. |  | 1.35 | N/A | no usada |
| EL: Esfuerzos residuales acumulados resultantes del proceso constructivo, (Locked-in construction Stresses.) |  | 1.0 | 1.0 | no usada |
| EV: Presion vertical de la tierra -- Estabilidad global. |  | 1.0 | N/A | no usada |
| EV: Presion vertical de la tierra -- Muros y estribos de retención. |  | 1.35 | 1.0 | usada |
| EV: Presion vertical de la tierra -- Estructura rígida enterrada. |  | 1.3 | 0.9 | usada |
| EV: Presion vertical de la tierra -- Pórticos rígidos. |  | 1.35 | 0.9 | no usada |
| EV: Presion vertical de la tierra -- Estructuras flexible enterradas -- o Alcantarillas cajón metálicas, plancas estructurales con corrugaciones y alcantarillas de fibra de vidrio. |  | 1.5 | 0.9 | usada |
| EV: Presion vertical de la tierra -- Estructuras flexible enterradas -- o Alcantarillas termoplásticas. |  | 1.3 | 0.9 | usada |
| EV: Presion vertical de la tierra -- Estructuras flexible enterradas -- o Entre otros. |  | 1.95 | 0.9 | no usada |
| ES: Carga superficial(Sobrecarga) en el terreno |  | 1.5 | 0.75 | usada |

### `MP.TRECUB` — Tabla 2.9.1.5.5.3-1 Recubrimiento para las armaduras principales de aceros no protegidas

- Cita: `MP.T2.9.1.5.5.3-1`
- Tabla completa · el calculo usa 2 de 3 columnas y 3 de 22 filas
- Columna «Recubrimiento (in.)» transcrita y **no usada**: el calculo opera en SI y consume la columna en mm; la pulgada se transcribe porque es la unidad en que la fuente lo imprime y sin ella no se puede comprobar la conversion
- Vistas de cálculo derivadas: `RECUBRIMIENTO_MP_MM`

| Fila | Situación | Recubrimiento (in.) | Recubrimiento (mm) | Uso |
|---|---|---|---|---|
| Exposición directa al agua salada |  | 4.0 | 101.6 | no usada |
| Vaciado del concreto contra el suelo |  | 3.0 | 76.2 | usada |
| Ubicaciones costeras |  | 3.0 | 76.2 | usada |
| sales_anticongelantes |  | 2.5 | 63.5 | no usada |
| tableros_neumaticos_clavos |  | 2.5 | 63.5 | no usada |
| exterior_no_superior |  | 2.0 | 50.8 | usada |
| interior_hasta_n11 |  | 1.5 | 38.1 | no usada |
| interior_n14_n18 |  | 2.0 | 50.8 | no usada |
| losa_in_situ_inferior_hasta_n11 |  | 1.0 | 25.4 | no usada |
| losa_in_situ_inferior_n14_n18 |  | 2.0 | 50.8 | no usada |
| paneles_prefabricados_encofrados |  | 0.8 | 20.32 | no usada |
| pilar_prefabricado_no_corrosivo |  | 2.0 | 50.8 | no usada |
| pilar_prefabricado_corrosivo |  | 3.0 | 76.2 | no usada |
| pilote_prefabricado_pretensado |  | 2.0 | 50.8 | no usada |
| pilar_in_situ_no_corrosivo |  | 2.0 | 50.8 | no usada |
| pilar_in_situ_corrosivo_general |  | 3.0 | 76.2 | no usada |
| pilar_in_situ_corrosivo_protegida |  | 3.0 | 76.2 | no usada |
| pilar_in_situ_cascaras |  | 2.0 | 50.8 | no usada |
| pilar_in_situ_tremie_o_lechada |  | 3.0 | 76.2 | no usada |
| alcantarilla_cajon_prefab_losa_de_rodadura |  | 2.5 | 63.5 | no usada |
| Alcantarillas de cajón de concreto prefabricados: forjados con inferior a 2 pies de relleno que no se utilicen como una superficie de conducción |  | 2.0 | 50.8 | no usada |
| alcantarilla_cajon_prefab_otros_miembros |  | 1.0 | 25.4 | no usada |

### `MS.C41` — Cuadro 4.1 Número de Calicatas para Exploración de Suelos

- Cita: `MS.4.2#C41`
- Tabla completa · el calculo usa 0 de 8 columnas y 0 de 6 filas
- Columna «Tipo de Carretera»: **elección pendiente** (`COND-CLASE-DE-VIA`) — el cálculo se detiene
- Columna «Profundidad (m)» transcrita y **no usada**: gobierna la campaña de campo, no el dimensionamiento de la alcantarilla. Se transcribe porque NOR-SUE-04 la reclamaba: el Cuadro SI fija la profundidad, en columna propia, y el repositorio no la recogia
- Columna «Calzada 2 carriles por sentido»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`) — el cálculo se detiene
- Columna «Calzada 3 carriles por sentido»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`) — el cálculo se detiene
- Columna «Calzada 4 carriles por sentido»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`) — el cálculo se detiene
- Columna «Número mínimo de Calicatas» transcrita y **no usada**: gobierna la CAMPAÑA DE CAMPO -- cuantas calicatas hay que abrir --, no el dimensionamiento de la alcantarilla. Llega al expediente como `CALICATAS_POR_KM` y `CALICATAS_POR_SENTIDO`, las dos declaradas en `constantes_normativas.CONSTANTES_DE_REFERENCIA`: se transcriben para que la memoria pueda imprimirlas y para que la cita sea verificable, no porque entren en formula
- Columna «x sentido» transcrita y **no usada**: gobierna la CAMPAÑA DE CAMPO -- cuantas calicatas hay que abrir --, no el dimensionamiento de la alcantarilla. Llega al expediente como `CALICATAS_POR_KM` y `CALICATAS_POR_SENTIDO`, las dos declaradas en `constantes_normativas.CONSTANTES_DE_REFERENCIA`: se transcriben para que la memoria pueda imprimirlas y para que la cita sea verificable, no porque entren en formula
- Columna «Observación» transcrita y **no usada**: es la regla de UBICACION de las calicatas, no de densidad; ninguna fase la evalua
- Fila «Autopistas: carreteras de IMDA mayor de 6000 veh/día, de calzadas separadas, cada una con dos o más carriles»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`)
- Fila «Carreteras Duales o Multicarril: carreteras de IMDA entre 6000 y 4001  veh/dia, de calzadas separadas, cada una con dos o más carriles»: **elección pendiente** (`COND-CARRILES-POR-SENTIDO`)
- **Laguna de la fuente**: las calzadas de MAS de 4 carriles por sentido: el Cuadro tabula 2, 3 y 4 y no dice que hacer con 5 o mas. Se cierra con: ninguna. La fuente no extrapola ni dice que la ultima fila se prolongue (`datos_sitio['carriles_por_sentido']`)
- Vistas de cálculo derivadas: `CALICATAS_POR_KM`, `CALICATAS_POR_SENTIDO`, `CALICATAS_PROFUNDIDAD_M`

| Fila | Tipo de Carretera | Profundidad (m) | Calzada 2 carriles por sentido | Calzada 3 carriles por sentido | Calzada 4 carriles por sentido | Número mínimo de Calicatas | x sentido | Observación | Uso |
|---|---|---|---|---|---|---|---|---|---|
| Autopistas: carreteras de IMDA mayor de 6000 veh/día, de calzadas separadas, cada una con dos o más carriles |  | 1.5 | 4 | 4 | 6 | -> | True | Las calicatas se  ubicarán longitudinalmente y en forma alternada | pendiente |
| Carreteras Duales o Multicarril: carreteras de IMDA entre 6000 y 4001  veh/dia, de calzadas separadas, cada una con dos o más carriles |  | 1.5 | 4 | 4 | 6 | -> | True | Las calicatas se  ubicarán longitudinalmente y en forma alternada | pendiente |
| Carreteras de Primera Clase: carreteras con un IMDA entre 4000-2001 veh/día, de una calzada de dos carriles. |  | 1.5 |  |  |  | 4 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | no usada |
| Carreteras de Segunda Clase: carreteras con un IMDA entre 2000-401 veh/día, de una calzada de dos carriles. |  | 1.5 |  |  |  | 3 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | no usada |
| Carreteras de Tercera Clase: carreteras con un IMDA entre 400-201 veh/día, de una calzada de dos carriles. |  | 1.5 |  |  |  | 2 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | no usada |
| Carreteras de Bajo Volumen de Tránsito: carreteras con un IMDA ≤ 200 veh/día, de una calzada. |  | 1.5 |  |  |  | 1 | False | Las calicatas se  ubicarán longitudinalmente y en forma alternada | no usada |

> Fuente Fuente:  Elaboración Propia, teniendo en cuenta el Tipo de Carretera establecido en la RD 037-2008-MTC/14 y el Manual de Ensayo de Materiales del MTC

### `WSDOT_HM.T2-2` — Runoff Coefficients for the Rational Method: 10-Year Return Frequency

- Cita: `WSDOT_HM.2-6.2#T2-2`
- Tabla completa · el calculo usa 3 de 3 columnas y 4 de 26 filas
- **Laguna de la fuente**: un periodo de retorno que no sea 10, 25, 50 o 100 años: la fuente da el incremento del coeficiente para esos tres (10, 20 y 25 %) y no dice que hacer entre ellos ni por encima de 100. Se cierra con: el proyecto toma el incremento de la frecuencia tabulada inmediatamente MAYOR o igual, que es el lado conservador porque el incremento crece con el periodo de retorno, y el paso lo imprime; por encima de 100 años no hay frecuencia mayor que tomar y el calculo se detiene como metodo no evaluable (`criterios_adoptados['coeficiente_escorrentia_superficie_vial']`)
- Vistas de cálculo derivadas: `coeficiente_escorrentia_superficie_vial`

| Fila | Flat | Rolling (2%–10%) | Hilly (Over 10%) | Uso |
|---|---|---|---|---|
| Pavement and roofs | 0.9 | 0.9 | 0.9 | usada |
| Earth shoulders | 0.5 | 0.5 | 0.5 | usada |
| Drives and walks | 0.75 | 0.8 | 0.85 | no usada |
| Gravel pavement | 0.5 | 0.55 | 0.6 | no usada |
| City business areas | 0.8 | 0.85 | 0.85 | no usada |
| Suburban residential | 0.25 | 0.35 | 0.4 | no usada |
| Single-family residential | 0.3 | 0.4 | 0.5 | no usada |
| Multi units, detached | 0.4 | 0.5 | 0.6 | no usada |
| Multi units, attached | 0.6 | 0.65 | 0.7 | no usada |
| Lawns, very sandy soil | 0.05 | 0.07 | 0.1 | no usada |
| Lawns, sandy soil | 0.1 | 0.15 | 0.2 | no usada |
| Lawns, heavy soil | 0.17 | 0.22 | 0.35 | no usada |
| Grass shoulders | 0.25 | 0.25 | 0.25 | no usada |
| Side slopes, earth | 0.6 | 0.6 | 0.6 | usada |
| Side slopes, turf | 0.3 | 0.3 | 0.3 | usada |
| Median areas, turf | 0.25 | 0.3 | 0.3 | no usada |
| Cultivated land, clay, and loam | 0.5 | 0.55 | 0.6 | no usada |
| Cultivated land, sand, and gravel | 0.25 | 0.3 | 0.35 | no usada |
| Industrial areas, light | 0.5 | 0.7 | 0.8 | no usada |
| Industrial areas, heavy | 0.6 | 0.8 | 0.9 | no usada |
| Parks and cemeteries | 0.1 | 0.15 | 0.25 | no usada |
| Playgrounds | 0.2 | 0.25 | 0.3 | no usada |
| Woodland and forests | 0.1 | 0.15 | 0.2 | no usada |
| Meadows and pasture land | 0.25 | 0.3 | 0.35 | no usada |
| Pasture with frozen ground | 0.4 | 0.45 | 0.5 | no usada |
| Unimproved areas | 0.1 | 0.2 | 0.3 | no usada |

### `WSDOT_HM.T8-4` — Table 8-4 Pipe Abrasion Levels

- Cita: `WSDOT_HM.T8-4`
- Tabla completa · el calculo usa 5 de 5 columnas y 4 de 4 filas
- **Interpretación del proyectista, no de la fuente**: El proyecto toma el corte de 15 ft/s (4.572 m/s) entre los niveles «moderately» y «severely abrasive» como techo de velocidad de V3 para TMC y HDPE, es decir: toma la velocidad POR SI SOLA como criterio suficiente para clasificar el sitio como severamente abrasivo
  - En contra: La tabla clasifica el SITIO por tres caracteristicas (carga de fondo, pendiente y velocidad), no fija una velocidad maxima para ningun material.
  - En contra: Para el METAL la tabla no prohibe nada en ningun nivel: prescribe remedio (mas calibre o solera de concreto), y el «shall» de aumentar uno o dos calibres ya rige desde 6 ft/s en el nivel moderado. V3 no sustituye esa proteccion.
  - En contra: La prohibicion del termoplastico en el nivel severo NO esta en esta tabla sino en el §8-3.3 (WSDOT_HM.8-3.3#SEVERA). La fila severa de esta edicion no nombra al termoplastico: su ultima frase habla de «Sacrificial metal pipe», y por su redaccion («exhibits better abrasion characteristics than metal or concrete», la misma que el §3-3.5 aplica al termoplastico) parece una errata del ejemplar. Es inferencia, no texto: se transcribe como se imprime.
  - En contra: Los cortes inferiores (3 y 6 ft/s) no entran en ninguna verificacion del proyecto; el de 6 ft/s (1.829 m/s) es desde donde la fuente pide mas calibre para el metal.
  - A favor: La nota que introduce la tabla (WSDOT_HM.T8-4) dice que no hace falta que concurran todos los criterios de un nivel para asignarlo: clasificar por la velocidad sola es una lectura conservadora que la fuente admite.
  - A favor: AASHTO LRFD C12.6.9 (AASHTO_LRFD_9.C12.6.9#NIVEL_4) pone el mismo corte de 15.0 ft/s para el nivel 4 de abrasion de la FHWA.
- Vistas de cálculo derivadas: `NIVELES_DE_ABRASION`

| Fila | Abrasion Level | General Site Characteristics | General Site Characteristics | General Site Characteristics | Recommended Invert Protection | Uso |
|---|---|---|---|---|---|---|
| Non-abrasive | Non-abrasive | Little or no bed load | Slope less than 1% | Velocities less than 3 ft/s | Generally, most pipes may be used under these circumstances, if a protective treatment is deemed necessary for metal pipes, any of the protective treatments specified in Section 8-5.3.1 would be adequate. | usada |
| Low abrasive | Low abrasive | Minor bed loads of sands, silts, and clays | Slopes 1%–2% | Velocities less than 6 ft/s | For metal pipes, an additional gage thickness may be specified if existing pipes in the vicinity show susceptibility to abrasion, or any of the protective treatments specified in Section 8-5.3.1 would be adequate. | usada |
| Moderately abrasive | Moderately abrasive | Moderate bed loads of sands and gravels, with stone sizes up to about 3 inches | Slopes 2%–4% | Velocities from 6 to 15 ft/s | Metal pipe thickness shall be increased one or two standard gages. The PEO may want to consider a concrete-lined alternative. Concrete pipe and box culverts shall be specified with an increased wall thickness or an increased concrete compressive strength. Thermoplastic pipe may be used without additional treatments. | usada |
| Severely abrasive | Severely abrasive | Heavy bed loads of sands, gravel, and rocks, with stone sizes up to 12 inches or larger | Slopes steeper than 4% | Velocities greater than 15 ft/s | Metal pipe thickness shall be increased at least two standard gages, or the pipe invert shall be lined with concrete. Box culverts shall be specified with an increased wall thickness or an increased concrete compressive strength. Sacrificial metal pipe exhibits better abrasion characteristics than metal or concrete. However, it generally cannot be reinforced to provide additional invert protection and shall not be used in this condition. | usada |

## 6. Condiciones que detienen el cálculo

Lo indeterminado bloquea; lo que no bloquea lleva su justificación
escrita, y el test la exige.

| id | Dónde | Resuelve | Efecto |
|---|---|---|---|
| `COND-AC-ALTA` | modificador:MOD-RECUB-AC | `exposicion_quimica_ems` | bloquea |
| `COND-AC-BAJA` | modificador:MOD-RECUB-AC | `exposicion_quimica_ems` | bloquea |
| `COND-CARRILES-POR-SENTIDO` | tabla:MS.C41#MS.C41#autopista | `carriles_por_sentido` | bloquea |
| `COND-CARRILES-POR-SENTIDO` | tabla:MS.C41#MS.C41#dual | `carriles_por_sentido` | bloquea |
| `COND-CATEGORIA-REFUERZO` | tabla:AASHTO_LRFD_9.T5.10.1-1#AASHTO_LRFD_9.T5.10.1-1#vaciado_contra_suelo | `categoria_refuerzo_aashto` | bloquea |
| `COND-CATEGORIA-REFUERZO` | tabla:AASHTO_LRFD_9.T5.10.1-1#AASHTO_LRFD_9.T5.10.1-1#costera | `categoria_refuerzo_aashto` | bloquea |
| `COND-CLASE-DE-SITIO` | cita:MP.T2.4.3.11.2.1.2-1 | `clase_sitio` | bloquea |
| `COND-CLASE-DE-VIA` | tabla:MS.C41#MS.C41#autopista | `clase_de_via` | bloquea |
| `COND-CLASE-DE-VIA` | tabla:MS.C41#MS.C41#dual | `clase_de_via` | bloquea |
| `COND-DMIN-ALTO-VOLUMEN` | cita:MC_HHD.4.1.1.3.4a | `clase_de_via` | advierte |
| `COND-DMIN-CANAL-RIEGO` | cita:MC_HHD.4.1.1.3.4a | `familia == 'C'` | excluye |
| `COND-EMBOCADURA-CAJON` | cita:HDS5_3ED.TA.1 | `embocadura_cajon` | bloquea |
| `COND-EMBOCADURA-CAJON-KE` | cita:HDS5_3ED.TC.2 | `embocadura_cajon` | bloquea |
| `COND-EXPOSICION-QUIMICA-EMS` | cita:E060.T4.4 | `exposicion_quimica_ems` | bloquea |
| `COND-LS-DISTANCIA-H-MEDIO` | cita:MP.2.4.2.2#SOBRECARGA | `distancia_trafico <= H / 2` | advierte |
| `COND-LS-LOSA-APROXIMACION` | cita:MP.2.4.2.2#SOBRECARGA | `losa_de_aproximacion` | excluye |
| `COND-MARCO-SUELO-MALA-CALIDAD` | cita:MC_HHD.4.1.1.3.4a#MARCO | `el Manual recomienda el marco «cuando se tiene la presencia de suelos de fundacion de mala calidad» y NO define «mala calidad»: no da umbral, ni clasificacion, ni remision a otra norma. La columna `sucs_fundacion` del CSV trae el grupo SUCS del punto, y traducirlo a «mala calidad» seria inventar el mapeo que la fuente calla` | advierte |
| `COND-MULTICELDA-ARRASTRE` | cita:MC_HHD.4.1.1.3.4a#MULTIPLES | `la capacidad de arrastre del curso -- palizada, troncos, material de cauce -- no es una magnitud que este programa calcule ni una columna del CSV: se establece con inspeccion del cauce` | advierte |
| `COND-N-MANNING-CAJON` | cita:MC_HHD.4.1.1.3.6#T09 | `n_manning_cajon` | bloquea |
| `COND-PERFIL-SIN-INFO-SECUNDARIA` | cita:MS.4.2#PERFIL | `existe_informacion_secundaria_tramo` | bloquea |
| `COND-SELVA-ALTA` | cita:MC_HHD.4.1.1.3.7a | `region == 'selva_alta'` | excluye |

## 6-bis. Fundamentos: por qué se hace cada paso

El campo `por_que` de `PasoDeMemoria` (§4.4 del plan v12) sale de aquí,
no del docstring del módulo que calcula. El `verbo` está sostenido por
el `caracter` de al menos una de sus citas — invariante T11 —, que es
lo que impide escribir «la norma obliga» sobre un párrafo que
recomienda.

| id | Fase | Paso | Verbo | Citas |
|---|---|---|---|---|
| `F1.TW` | Fase 1 - Datos de entrada | TW en el cuerpo receptor: nivel de agua durante la avenida, por Manning en la seccion del receptor (Sec. 1.3) | **define** | `MC_HHD.4.1.1.3.6` |
| `F10.APORTE` | Fase 10 - Alcantarillas de alivio: espaciamiento | Caudal aportante por metro de cuneta: escorrentia especifica del area tributaria por su ancho | **define** | `MC_HHD.4.1.2.1b`, `MC_HHD.4.1.2a` |
| `F10.APORTE_CAPACIDAD` | Fase 10 - Alcantarillas de alivio: espaciamiento | Verificacion VB2: el caudal de aporte del alivio contra la capacidad admisible de la cuneta | **obliga** | `MC_HHD.4.1.2.1a#CONDICION`, `MC_HHD.4.1.2.1a`, `MC_HHD.4.1.2.1b` |
| `F10.CAPACIDAD` | Fase 10 - Alcantarillas de alivio: espaciamiento | Capacidad admisible de la cuneta: el menor del caudal con la cuneta llena y del que produce la velocidad limite admisible | **define** | `MC_HHD.4.1.2.1a`, `MC_HHD.4.1.2.1a#MANNING`, `MC_HHD.4.1.2.1a#VELOCIDAD`, `MC_HHD.4.1.2.1#T32`, `MC_HHD.4.1.2.1#T09`, `MC_HHD.4.1.2.1#T304_12`, `MC_HHD.4.1.2.1e` |
| `F10.CUNETA` | Fase 10 - Alcantarillas de alivio: espaciamiento | Longitud maxima de recorrido de la cuneta, que fija el espaciamiento de las alcantarillas de alivio | **obliga** | `MC_HHD.4.1.2.1d` |
| `F10.L_HIDRAULICO` | Fase 10 - Alcantarillas de alivio: espaciamiento | Longitud por capacidad de la cuneta: a partir de ella el caudal aportante supera la capacidad admisible | **define** | `MC_HHD.4.1.2.1a`, `MC_HHD.4.1.2.1b`, `DG2018.304.11` |
| `F10.TRAMO` | Fase 10 - Alcantarillas de alivio: espaciamiento | Verificacion VB1: espaciamiento adoptado entre alcantarillas de alivio contra el espaciamiento maximo | **obliga** | `MC_HHD.4.1.2.1d`, `DG2018.304.11#DESAGUE`, `MC_HHD.4.1.2.1d#ALIVIO` |
| `F2.LUZ` | Fase 2 - Clasificacion y periodo de retorno | Denominacion de la obra por su luz: alcantarilla o puente | **define** | `MC_HHD.4.1.1.3.1`, `MC_HHD.4.1.1.5.1`, `MP.GLOSARIO#OBRAS_DE_ARTE_MENORES`, `AASHTO_LRFD_9.1.2#BRIDGE`, `HDS5_3ED.1.2#NBIS` |
| `F2.TR` | Fase 2 - Clasificacion y periodo de retorno | Periodo de retorno del caudal de diseno, obtenido del riesgo admisible y la vida util de la Tabla N 02 | **recomienda** | `MC_HHD.3.6` |
| `F3.CELDAS` | Fase 3 - Tipo, material y durabilidad | Numero de celdas del cajon: una sola, o multicelda | **recomienda** | `MC_HHD.4.1.1.3.4a#MULTIPLES`, `HDS5_3ED.5.4.3#REPARTO` |
| `F3.DUR.ABRASION` | Fase 3 - Tipo, material y durabilidad | Matriz de durabilidad: nivel de abrasion del sitio frente a lo que cada material admite | **obliga** | `WSDOT_HM.8-3.3#SEVERA`, `WSDOT_HM.T8-4`, `WSDOT_HM.3-3.5#10FTS`, `AASHTO_LRFD_9.C12.6.9#NIVEL_4`, `MC_HHD.4.1.1.3.7e`, `MC_HHD.4.1.1.3.7g#AGRESIVAS` |
| `F3.DUR.CLORUROS` | Fase 3 - Tipo, material y durabilidad | Matriz de durabilidad: cloruros del suelo o del agua y proteccion del refuerzo y del acero | **obliga** | `E060.4.4.2`, `E060.T4.2`, `MC_HHD.4.1.1.3.7f#SALINIDAD`, `MC_HHD.4.1.1.3.7f#COSTA` |
| `F3.DUR.PH` | Fase 3 - Tipo, material y durabilidad | Matriz de durabilidad: pH del suelo o del agua frente a los umbrales de la tuberia de acero corrugado | **obliga** | `EG2013.507.10`, `WSDOT_HM.8-5.1#PH`, `WSDOT_HM.8-4.3#ZONA_III`, `WSDOT_HM.8-3.1#CONCRETO`, `MC_HHD.4.1.1.3.7f#TMC`, `AASHTO_M36.1.2`, `MC_HHD.4.1.1.3.4b` |
| `F3.DUR.RESISTIVIDAD` | Fase 3 - Tipo, material y durabilidad | Matriz de durabilidad: resistividad del suelo o del agua frente al umbral de la tuberia de acero corrugado | **obliga** | `WSDOT_HM.8-5.2#RESISTIVIDAD`, `WSDOT_HM.8-4.3#ZONA_III`, `MC_HHD.4.1.1.3.7f#SALINIDAD` |
| `F3.DUR.SUELO_AGRESIVO` | Fase 3 - Tipo, material y durabilidad | Matriz de durabilidad: agresividad del suelo para la tuberia de acero corrugado galvanizado | **recomienda** | `AASHTO_LRFD_9.10.7.5#INDICATIVOS`, `AASHTO_LRFD_9.11.10.6.4.2a#NO_AGRESIVO`, `AASHTO_LRFD_9.11.12.8#AGRESIVO`, `EG2013.507.10`, `MC_HHD.4.1.1.3.7f#COSTA`, `MC_HHD.4.1.1.3.7g#AGRESIVAS` |
| `F3.DUR.SUELO_FUNDACION` | Fase 3 - Tipo, material y durabilidad | Suelo de fundacion deficiente: aviso de que el Manual recomienda el marco de concreto | **recomienda** | `MC_HHD.4.1.1.3.4a#MARCO`, `E050.24`, `E050.24#REMOVER`, `E050.38.1`, `E050.FIG3` |
| `F3.DUR.SULFATOS` | Fase 3 - Tipo, material y durabilidad | Matriz de durabilidad: sulfatos del suelo o del agua y requisitos del concreto | **obliga** | `E060.T4.4` |
| `F3.D_EXTERIOR` | Fase 3 - Tipo, material y durabilidad | Espesor de pared del conducto: lo que separa el diametro hidraulico D del diametro exterior D_ext = D + 2t | **define** | `AASHTO_M36.T1`, `AASHTO_M36.8.1.1`, `AASHTO_LRFD_9.TA12-11`, `EG2013.508.02a` |
| `F3.D_MIN` | Fase 3 - Tipo, material y durabilidad | Seccion minima circular de 0.90 m (36") | **obliga** | `MC_HHD.4.1.1.3.4a` |
| `F3.MANTENIMIENTO` | Fase 3 - Tipo, material y durabilidad | Cota inferior de la progresion de secciones: dimension interior que permite mantener y limpiar el conducto | **obliga** | `MC_HHD.4.1.1.3.7d` |
| `F3.SECCION_CANAL` | Fase 3 - Tipo, material y durabilidad | Adopcion de la seccion del cajon en un cruce de canal de riego, fuera del piso de 0.90 m | **obliga** | `MC_HHD.4.1.1.3.4a` |
| `F3.TIPO_MARCO` | Fase 3 - Tipo, material y durabilidad | Tipo de estructura del cruce: alcantarilla tipo marco de concreto de seccion rectangular | **recomienda** | `MC_HHD.4.1.1.3.4a#TIPOS`, `MC_HHD.4.1.1.3.4a#NIVELES`, `MC_HHD.4.1.1.3.4a#MARCO`, `MC_HHD.LAMINA_03` |
| `F4.CONTROL` | Fase 4 - Dimensionamiento hidraulico | Carga a la entrada HW por los dos controles del HDS-5, entrada y salida, y adopcion del mayor | **define** | `HDS5_3ED.A.2`, `HDS5_3ED.3.1.4#K`, `HDS5_3ED.3.3.5#GOBIERNA` |
| `F4.FORMA_HDS5` | Fase 4 - Dimensionamiento hidraulico | Forma de la ecuacion de control de entrada del HDS-5 que aplica a esta seccion, y por que | **define** | `HDS5_3ED.A.2`, `HDS5_3ED.TA.1`, `HDS5_3ED.A.3#FORMAS` |
| `F4.HO` | Fase 4 - Dimensionamiento hidraulico | Altura de la linea de energia a la salida, h_o = max(TW, (d_c + D)/2) | **define** | `HDS5_3ED.3.3.3#HO`, `HDS5_3ED.3.3.3#HO_SUMERGIDA`, `HDS5_3ED.3.3.3#HO_1_2D`, `HDS5_3ED.3.1.4#0_75D` |
| `F4.HORIZONTAL` | Fase 4 - Dimensionamiento hidraulico | Barril horizontal (S = 0): no hay tirante normal, y el regimen del conducto lo fija el extremo de aguas abajo | **permite** | `HDS5_3ED.3.3.4#HORIZONTAL`, `HDS5_3ED.3.3.4#KS`, `HDS5_3ED.3.3.4#H_SIN_AJUSTE`, `HDS5_3ED.3.5.1#H2` |
| `F4.MANNING` | Fase 4 - Dimensionamiento hidraulico | Tirante normal y velocidad en el conducto, por Manning: UNA geometria (el tirante, con n_max) y DOS velocidades, una por cada extremo del rango de la Tabla N 09 | **define** | `MC_HHD.4.1.1.3.6`, `MC_HHD.4.1.1.3.6#T09` |
| `F4.N_CAJON` | Fase 4 - Dimensionamiento hidraulico | Coeficiente de rugosidad de Manning del cajon de concreto, por analogia declarada dentro del grupo A de la Tabla N 09 | **define** | `MC_HHD.4.1.1.3.6`, `MC_HHD.4.1.1.3.6#T09` |
| `F4.N_CAJON_TB1` | Fase 4 - Dimensionamiento hidraulico | Coeficiente de rugosidad de Manning del cajon de concreto, por la fila del cajon de la Tabla B.1 del HDS-5 | **define** | `HDS5_3ED.TB.1`, `HDS5_3ED.B.3#CAJON_IN_SITU` |
| `F4.PERFIL` | Fase 4 - Dimensionamiento hidraulico | Perfil de la lamina de agua por paso directo desde la salida hacia la entrada: longitud a seccion llena y carga a la entrada por remanso (HDS-5 pag. 3.12 y Section 3.5) | **define** | `HDS5_3ED.3.1.4#REMANSO`, `HDS5_3ED.3.1.4#EMPALME`, `HDS5_3ED.3.1.4#HW_REMANSO`, `HDS5_3ED.3.1.4#0_75D`, `HDS5_3ED.3.5#PERFIL`, `HDS5_3ED.3.5.1#S1`, `HDS5_3ED.3.5.1#TIPO7`, `HDS5_3ED.3.3.3#HO` |
| `F4.PISO_HW` | Fase 4 - Dimensionamiento hidraulico | Carga de control de entrada cuando la correccion por pendiente Ks·S la deja nula o negativa: el piso adoptado (`hw_entrada_fuera_de_rango`) | **define** | `HDS5_3ED.A.2.1#FORMA_1`, `HDS5_3ED.A.2.1#KS`, `HDS5_3ED.A.3#PENDIENTE_2` |
| `F4.REGIMEN` | Fase 4 - Dimensionamiento hidraulico | Regimen del barril y velocidad a la salida, con el area que HDS-5 3.1.6 asigna a cada caso | **define** | `HDS5_3ED.3.1.6#V_SALIDA`, `HDS5_3ED.3.1.6#V_SALIDA_TW`, `HDS5_3ED.3.3.2#V_SALIDA_ENTRADA`, `HDS5_3ED.3.1.3#SUMERGENCIA` |
| `F4.SECCION` | Fase 4 - Dimensionamiento hidraulico | Area, perimetro mojado y radio hidraulico de la seccion, para el tirante de trabajo | **define** | `MC_HHD.4.1.1.3.6` |
| `F4.YC` | Fase 4 - Dimensionamiento hidraulico | Tirante critico de la seccion, y la energia critica H_c | **define** | `HDS5_3ED.3.3.3#HO`, `HDS5_3ED.A.2`, `HDS5_3ED.A.3.1#CRITICO` |
| `F5.V1` | Fase 5 - Verificaciones | V1 - Borde libre: y no mayor que la relacion de llenado adoptada (por defecto 0.75 de la altura, diametro o flecha de la estructura, el complemento del 25 % recomendado) | **recomienda** | `MC_HHD.4.1.1.3.7b`, `MC_HHD.4.1.1.3.7b#LLENA` |
| `F5.V10` | Fase 5 - Verificaciones | V10 - Pendiente del conducto dentro de la banda adoptada: no menor que la minima ni mayor que la maxima | **define** | `MC_HHD.4.1.1.3.3`, `HDS5_3ED.3.3.4#HORIZONTAL`, `HDS5_3ED.5.4.4#PENDIENTE_10`, `HDS5_3ED.5.4.4#PENDIENTE_20`, `HDS5_3ED.A.3#PENDIENTE_2` |
| `F5.V2` | Fase 5 - Verificaciones | V2 - Velocidad minima de autolimpieza: V no menor que el piso adoptado (por defecto los 0.25 m/s recomendados) | **recomienda** | `MC_HHD.4.1.1.3.6#VMIN_INICIO`, `MC_HHD.4.1.1.3.6#VMIN` |
| `F5.V2b` | Fase 5 - Verificaciones | V2b - Sedimentacion / colmatacion: el indicador de pendiente del HDS-5 mas el acceso de mantenimiento declarado | **define** | `HDS5_3ED.5.3.3#INDICADORES`, `HDS5_3ED.5.3.3#ALINEADO` |
| `F5.V2b.REGIMEN` | Fase 5 - Verificaciones | V2b - El regimen con que se aplica el indicador de pendiente: umbral duro o indicador con aviso (`regimen_v2b`) | **define** | `HDS5_3ED.5.3.3#INDICADORES`, `HDS5_3ED.5.3.3#ALINEADO`, `HDS5_3ED.5.3.3#DEPRESION` |
| `F5.V3` | Fase 5 - Verificaciones | V3 - Velocidad maxima admisible del revestimiento (Tabla N 10) | **obliga** | `MC_HHD.4.1.1.3.6#T10` |
| `F5.V4` | Fase 5 - Verificaciones | V4 - Carga a la entrada bajo la subrasante, con el resguardo que fija el CBR | **obliga** | `MS.4.5.4`, `MS.9.1.3` |
| `F5.V5` | Fase 5 - Verificaciones | V5: el embalse aguas arriba frente al derecho de via, por el metodo declarado (cota de afectacion o embalse a nivel) | **define** | `HDS5_3ED.2.2.5#EMBALSE`, `HDS5_3ED.2.2.5#NO_EXCEDER`, `HDS5_3ED.2.2.5a#COTA_DE_DANO`, `DG2018.304.07.01`, `DG2018.304.07.02`, `DG2018.304.07.02#INCREMENTO` |
| `F5.V7` | Fase 5 - Verificaciones | V7 - Flotacion del conducto vacio bajo el nivel freatico | **obliga** | `MP.2.4.3.8.2`, `AASHTO_LRFD_9.12.6.1#FLOTACION`, `AASHTO_LRFD_9.12.6.2.3#UPLIFT`, `AASHTO_LRFD_9.3.7.2`, `MP.2.4.5.3.1#MINIMO`, `AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX`, `MP.2.4.5.2#EV`, `AASHTO_LRFD_9.C12.6.2.3`, `MP.T2.4.5.3.1-1`, `MP.T2.4.5.3.1-2` |
| `F5.V7_FILA` | Fase 5 - Verificaciones | Fila de gamma_p de la Tabla 2.4.5.3.1-2 que describe a esta estructura | **define** | `MP.2.4.5.2#EV`, `MP.T2.4.5.3.1-2` |
| `F5.V8` | Fase 5 - Verificaciones | V8: nivel del embalse con el caudal del evento extremo frente a la cota de desborde de la plataforma | **permite** | `HDS5_3ED.2.2.5a#COTA_CRITICA` |
| `F5.VC1` | Fase 5 - Verificaciones | VC1 - Cruce de canal: el agua embalsada a la entrada no llega a la coronacion del canal, con su borde libre | **recomienda** | `MC_HHD.4.1.1.4.1e`, `MC_HHD.4.1.1.4.1e#RANGO` |
| `F6.APRON` | Fase 6 - Proteccion de entrada y salida | Tamaño de piedra del apron de enrocado por HEC-14, Ec. (10.4): D50 en funcion de Q, D y TW | **recomienda** | `HEC14.10.2#EC_10_4`, `HEC14.10.2#TW`, `HEC14.10.2#TW_ALTO`, `HEC14.10.2#EC_10_5`, `HEC14.1#T1_1_APRON`, `HDS5_3ED.5.3.2#APRON`, `HEC14.D#SOLO_VELOCIDAD` |
| `F6.APRON_GEOMETRIA` | Fase 6 - Proteccion de entrada y salida | Clase de enrocado, longitud, profundidad y ancho del apron por la Tabla 10.1 de HEC-14 | **recomienda** | `HEC14.10.2#T10_1`, `HEC14.10.2#ANCHO`, `MC_HHD.LAMINA_05`, `MC_HHD.4.1.1.3.7c#ALIVIADERO`, `MC_HHD.LAMINA_04`, `HDS5_3ED.5.3.2#APRON` |
| `F6.ENTRADA` | Fase 6 - Proteccion de entrada y salida | Proteccion de la entrada: velocidad en la boca y revestimiento del cauce y del talud | **recomienda** | `MC_HHD.4.1.1.3.7c#PROTECCION`, `MC_HHD.4.1.1.3.7c#REVESTIMIENTOS`, `HDS5_3ED.5.3.1#ENTRADA`, `HDS5_3ED.3.1.3#CRITICO_EN_LA_ENTRADA`, `MC_HHD.LAMINA_02` |
| `F6.FILTRO` | Fase 6 - Proteccion de entrada y salida | Filtro entre el enrocado y el suelo: requisitos del geotextil de control permanente de erosion | **recomienda** | `MC_HHD.LAMINA_05`, `HEC14.10.2#FILTRO`, `EG2013.511.08#EROSION`, `EG2013.511.08#T511_06`, `EG2013.511.08#NOTA_5A`, `EG2013.511.05#T511_02_NOTA_5` |
| `F6.FROUDE` | Fase 6 - Proteccion de entrada y salida | Numero de Froude de HEC-14 a la salida del conducto, Fr_e = V / (g·ye)^0.5, con el tirante equivalente | **define** | `HEC14.10.1.1#YE`, `HDS5_3ED.3.1.6#V_SALIDA`, `HEC14.3#CONTINUIDAD`, `HEC14.1#T1_1_APRON` |
| `F6.GEOMETRIA_ADOPTADA` | Fase 6 - Proteccion de entrada y salida | Espesor y longitud de la proteccion de salida que el proyecto adopta | **recomienda** | `MC_HHD.4.1.1.3.7c#REVESTIMIENTOS`, `MC_HHD.4.1.1.3.7c`, `HEC14.10.2#T10_1`, `HEC14.10.2#PROFUNDIDAD`, `HEC14.10.2#EC_10_4` |
| `F6.LAUSHEY` | Fase 6 - Proteccion de entrada y salida | Diametro medio del enrocado de proteccion a la salida, d50 = V^2 / (3.1 g) | **define** | `MC_HHD.4.1.1.3.7c` |
| `F6.SOCAVACION` | Fase 6 - Proteccion de entrada y salida | Hoya de socavacion local a la salida por HEC-14, Cap. 5: profundidad, ancho y longitud | **recomienda** | `HEC14.5.1#EC_5_1`, `HEC14.5#PEOR_CASO`, `HEC14.5.1.1#T5_1`, `HEC14.5.1.4#T5_2`, `HEC14.5.1.5#T5_3`, `HEC14.5.1.2#T30`, `HEC14.5.1.2#NO_BAJO_30`, `HEC14.5.1.2#DOS_TERCIOS`, `HEC14.5.2#EC_5_2`, `HEC14.5.2#RANGO_IP`, `HEC14.5.2#EC_5_4` |
| `F6.SOCAVACION_DESPLANTE` | Fase 6 - Proteccion de entrada y salida | Profundidad de socavacion que se entrega al desplante del cabezal de salida | **recomienda** | `HEC14.5.1.3#CABEZAL`, `HDS5_3ED.5.3.2#APRON`, `HEC14.10.1#HS` |
| `F6.V_ADMISIBLE` | Fase 6 - Proteccion de entrada y salida | Velocidad del flujo contra la maxima admisible del terreno del cauce (Tabla Nº 11) | **recomienda** | `MC_HHD.4.1.1.3.6#V_SALIDA`, `MC_HHD.4.1.1.3.6#T11`, `MC_HHD.4.1.1.3.7c#PROTECCION`, `HDS5_3ED.5.3.2#PRACTICA` |
| `F7.COTA_SALIDA` | Fase 7 - Compatibilidad geometrica | Caida del conducto y cota de fondo de la salida | **define** | `MC_HHD.LAMINA_01`, `HDS5_3ED.2.2.4#LONGITUD` |
| `F7.EMPALME_CANAL` | Fase 7 - Compatibilidad geometrica | Empalme de la salida de un paso de canal con el fondo del canal aguas abajo (VC2, aviso) | **define** | `MC_HHD.LAMINA_03`, `EG2013.503.11g#COTAS`, `EG2013.501.07` |
| `F7.ENCAJE` | Fase 7 - Compatibilidad geometrica | Encaje de la seccion adoptada en la seccion transversal: longitud entre cabezales a la clave | **obliga** | `HDS5_3ED.3.3.5#ENCAJE`, `HDS5_3ED.3.1.4#LONGITUD` |
| `F7.ENTREGA` | Fase 7 - Compatibilidad geometrica | Entrega al cuerpo receptor: cota de salida frente a su fondo | **define** | `MC_HHD.LAMINA_01`, `MC_HHD.4.1.1.3.3` |
| `F7.ESVIAJE` | Fase 7 - Compatibilidad geometrica | Factor de esviaje, 1 / cos(esviaje) | **define** | `HDS5_3ED.5.4.1#ESVIAJE`, `MC_HHD.4.1.1.3.2` |
| `F7.ESVIAJE_MAX` | Fase 7 - Compatibilidad geometrica | Esviaje del cruce frente al maximo que el proyecto adopta | **recomienda** | `HDS5_3ED.5.4.2#MAXIMO_PRACTICO`, `MC_HHD.4.1.1.3.2` |
| `F7.LONGITUD` | Fase 7 - Compatibilidad geometrica | Longitud del conducto sobre la seccion transversal del cruce | **define** | `HDS5_3ED.2.2.4#LONGITUD`, `HDS5_3ED.3.1.4#LONGITUD`, `DG2018.304.10#T304.11`, `DG2018.304.05#BOMBEO`, `DG2018.304.06#PERALTE` |
| `F7.MARCO` | Fase 7 - Compatibilidad geometrica | Geometria del marco adoptado: dimensiones exteriores, cotas de fondo y de clave, relleno sobre la losa | **define** | `MC_HHD.LAMINA_03`, `MC_HHD.4.1.1.3.4a#NIVELES`, `E060.14.5.3.2` |
| `F7.PENDIENTE` | Fase 7 - Compatibilidad geometrica | Pendiente adoptada del conducto, con su origen | **obliga** | `MC_HHD.4.1.1.3.3`, `HDS5_3ED.5.3.3#ALINEADO` |
| `F7.RELLENO` | Fase 7 - Compatibilidad geometrica | Altura minima de relleno sobre la clave del conducto | **obliga** | `AASHTO_LRFD_9.12.6.6.3#COBERTURA`, `EG2013.508.07#RELLENO_MIN` |
| `F7.REMANSO_CANAL` | Fase 7 - Compatibilidad geometrica | Sobreelevacion de la lamina del canal en el cruce y longitud minima del remanso aguas arriba (aviso) | **define** | `MC_HHD.4.1.1.3.6` |
| `F8.CARGA_TIERRA` | Fase 8 - Verificacion estructural del conducto | Carga de tierra sobre el conducto: prisma de relleno y paquete estructural, con la interaccion suelo-estructura de su tipo | **obliga** | `AASHTO_LRFD_9.12.10.2.1#VAF`, `AASHTO_LRFD_9.12.10.2.1#PESO_MIN`, `AASHTO_LRFD_9.12.10.2.2`, `AASHTO_LRFD_9.C12.7.2.2`, `AASHTO_LRFD_9.12.11.2.2.1`, `MP.2.4.2.1#PESOS` |
| `F8.CARGA_VIVA` | Fase 8 - Verificacion estructural del conducto | Carga viva HL-93 a la profundidad de la clave: presion vertical por la rueda distribuida a traves del relleno | **obliga** | `AASHTO_LRFD_9.3.6.1.2.6a#RELLENO`, `AASHTO_LRFD_9.3.6.1.2.6a#EJES`, `AASHTO_LRFD_9.3.6.1.2.6a#UN_CARRIL`, `AASHTO_LRFD_9.3.6.1.2.6a#DESPRECIABLE`, `AASHTO_LRFD_9.3.6.1.2.6a#VARIOS_VANOS`, `AASHTO_LRFD_9.3.6.1.2.6a#CONCRETO_SOMERO`, `AASHTO_LRFD_9.T3.6.1.2.6a-1`, `AASHTO_LRFD_9.3.6.1.2.6b#PL`, `AASHTO_LRFD_9.C3.6.1.2.6b`, `MP.2.4.3.2.2.2`, `MP.2.4.3.2.2.3`, `MP.2.4.3.2.2.5`, `MP.2.4.3.2.2.6`, `MP.2.4.3.3.2`, `AASHTO_LRFD_9.12.11.2.1#LL` |
| `F8.CLASE_CONCRETO` | Fase 8 - Verificacion estructural del conducto | Clase del tubo de concreto reforzado por el metodo indirecto: D-load requerida frente a la D-load de la clase | **obliga** | `AASHTO_LRFD_9.12.10.4.3.1`, `AASHTO_LRFD_9.12.10.4.3.1#TIPO1`, `AASHTO_LRFD_9.12.10.4.3.1#DLOAD`, `AASHTO_LRFD_9.12.10.4.3.2a`, `AASHTO_LRFD_9.12.10.4.3.2c`, `AASHTO_LRFD_9.12.10.2.3`, `AASHTO_M170M.T2#DLOAD`, `AASHTO_M170M.T1#DIAMETROS`, `AASHTO_LRFD_9.T12.10.2.1-1`, `AASHTO_LRFD_9.T12.10.2.1-1#PROCTOR`, `EG2013.506.02#CLASE`, `EG2013.506.07`, `EG2013.506.10`, `EG2013.T205-01`, `EG2013.205.12#COMPACTACION` |
| `F8.HDPE_DEFLEXION` | Fase 8 - Verificacion estructural del conducto | Tuberia de polietileno corrugado: deflexion vertical de servicio | **obliga** | `AASHTO_LRFD_9.12.12.2.2`, `AASHTO_LRFD_9.C12.12.2.2` |
| `F8.HDPE_EMPUJE` | Fase 8 - Verificacion estructural del conducto | Tuberia de polietileno corrugado: deformacion de compresion por el empuje frente a su limite | **obliga** | `AASHTO_LRFD_9.12.12.3.10.1d`, `AASHTO_LRFD_9.12.12.3.10.1c#EP`, `AASHTO_LRFD_9.12.12.3.5`, `AASHTO_LRFD_9.T12.12.3.3-1`, `AASHTO_LRFD_9.T12.12.3.5-1`, `AASHTO_LRFD_9.12.12.3.10.1b#STUB`, `AASHTO_M294_TRAD.7.7`, `AASHTO_LRFD_9.TA12-11`, `AASHTO_LRFD_9.12.12.3.2`, `AASHTO_LRFD_9.C12.12.3.2`, `AASHTO_LRFD_9.T12.12.3.5-2`, `AASHTO_LRFD_9.12.5.4`, `AASHTO_LRFD_9.1.3.5`, `MP.2.3.2.5`, `EG2013.508.02#GRANULAR`, `EG2013.T301-01`, `EG2013.508.07#COMPACTACION` |
| `F8.HDPE_FF` | Fase 8 - Verificacion estructural del conducto | Tuberia de polietileno corrugado: factor de flexibilidad para el manejo y la instalacion | **obliga** | `AASHTO_LRFD_9.12.5.6.3`, `AASHTO_LRFD_9.12.12.3.6`, `AASHTO_LRFD_9.TA12-11` |
| `F8.HDPE_PANDEO` | Fase 8 - Verificacion estructural del conducto | Tuberia de polietileno corrugado: pandeo general del anillo | **obliga** | `AASHTO_LRFD_9.12.12.3.10.1e`, `AASHTO_LRFD_9.12.12.3.3#PANDEO`, `AASHTO_LRFD_9.12.12.3.10.1c#EP`, `AASHTO_LRFD_9.T12.12.3.5-1`, `AASHTO_LRFD_9.12.5.5` |
| `F8.MARCO_DEMANDA` | Fase 8 - Verificacion estructural del conducto | Marco de concreto: cargas sobre la losa superior y momento de referencia; el diseño de la seccion se difiere | **obliga** | `AASHTO_LRFD_9.12.11.2.2.1`, `AASHTO_LRFD_9.12.11.2.1#LL` |
| `F8.RECUBRIMIENTO` | Fase 8 - Verificacion estructural del conducto | Recubrimiento del refuerzo, por la regla del mayor entre E.060 y AASHTO | **obliga** | `E060.7.7.1`, `AASHTO_LRFD_9.T5.10.1-1` |
| `F8.TMC_AREA` | Fase 8 - Verificacion estructural del conducto | Tuberia metalica corrugada: empuje de anillo mayorado frente a la resistencia de la pared, con el pandeo | **obliga** | `AASHTO_LRFD_9.12.7.2.2`, `AASHTO_LRFD_9.C12.7.2.2`, `AASHTO_LRFD_9.12.7.2.3`, `AASHTO_LRFD_9.12.7.2.4`, `AASHTO_LRFD_9.12.5.4`, `AASHTO_LRFD_9.1.3.5`, `AASHTO_LRFD_9.12.5.5`, `AASHTO_LRFD_9.TA12-9`, `MP.2.3.2.5`, `ASTM_A796.9.1`, `ASTM_A796.T5`, `EG2013.T507-01` |
| `F8.TMC_ASD` | Fase 8 - Verificacion estructural del conducto | Tuberia metalica corrugada: contraste por tensiones admisibles (ASTM A796, num. 8), que no rige | **permite** | `ASTM_A796.7.1`, `ASTM_A796.8.1.1.2#SELECCION`, `ASTM_A796.6.2.2.1` |
| `F8.TMC_COSTURA` | Fase 8 - Verificacion estructural del conducto | Tuberia metalica corrugada: resistencia de la costura longitudinal | **obliga** | `AASHTO_LRFD_9.12.7.2.5`, `ASTM_A796.8.1.3.1`, `ASTM_A796.T5`, `AASHTO_LRFD_9.12.5.5`, `EG2013.507.02#EMPERNADA` |
| `F8.TMC_FF` | Fase 8 - Verificacion estructural del conducto | Tuberia metalica corrugada: factor de flexibilidad de manejo e instalacion | **obliga** | `AASHTO_LRFD_9.12.5.6.1#FF`, `ASTM_A796.10.3` |
| `F9.AGUA` | Fase 9 - Cabezal y aletas | Agua en el trasdos: nivel, empuje hidrostatico, suelo sumergido y subpresion | **obliga** | `AASHTO_LRFD_9.3.11.3`, `AASHTO_LRFD_9.11.6.6#DRENAJE`, `E050.39.13.8#DRENAJE`, `MP.2.4.3.8.2` |
| `F9.ALEROS` | Fase 9 - Cabezal y aletas | Aleros: angulo, longitud, alturas inicial y final, espesor | **obliga** | `AASHTO_LRFD_9.12.6.5#ALEROS`, `MC_HHD.LAMINA_02A`, `HDS5_3ED.SIMBOLOS#THETA_W` |
| `F9.COMBINACIONES` | Fase 9 - Cabezal y aletas | Cargas del cabezal con sus brazos y combinaciones de cada marco: factoradas (LRFD) y de servicio (ASD) | **obliga** | `AASHTO_LRFD_9.11.6.3.2#PORTANTE`, `AASHTO_LRFD_9.C11.5.6#FIGURAS`, `AASHTO_LRFD_9.C11.5.6#SOBRECARGA`, `MP.T2.4.5.3.1-2`, `E050.17.1#SERVICIO` |
| `F9.CORONACION` | Fase 9 - Cabezal y aletas | Coronacion y altura del cabezal: sobre la clave exterior y sobre el nivel de agua del extremo | **obliga** | `HDS5_3ED.3.3.5#ENCAJE` |
| `F9.DESPLANTE` | Fase 9 - Cabezal y aletas | Profundidad de desplante del cabezal: minimo de E.050 y, a la salida, bajo la socavacion | **obliga** | `E050.26.2#PROFUNDIDAD`, `AASHTO_LRFD_9.12.6.5#ZAPATAS`, `AASHTO_LRFD_9.10.6.1.2#DESPLANTE`, `HEC14.5.1.3#CABEZAL` |
| `F9.DIMENSIONES` | Fase 9 - Cabezal y aletas | Predimensionamiento del cabezal: tipo, espesores, zapata y longitud del muro | **define** | `MC_HHD.LAMINA_02A`, `E060.22.7.4#ZAPATA`, `E060.15.7#PERALTE`, `E060.22.10.2#CICLOPEO` |
| `F9.E1_LRFD` | Fase 9 - Cabezal y aletas | E1 (LRFD): presion factorada sobre el ancho efectivo frente a la resistencia portante factorada | **obliga** | `AASHTO_LRFD_9.11.6.3.2#PORTANTE`, `AASHTO_LRFD_9.10.6.3.1.1#NIVEL_FREATICO`, `AASHTO_LRFD_9.10.6.3.1.2a#QN`, `AASHTO_LRFD_9.10.6.3.1.2a#T1`, `AASHTO_LRFD_9.10.6.3.1.2c#TALUD`, `AASHTO_LRFD_9.10.5.5.2.2#T1`, `AASHTO_LRFD_9.11.5.7#MUROS`, `AASHTO_LRFD_9.11.5.8#PORTANTE` |
| `F9.E2_LRFD` | Fase 9 - Cabezal y aletas | E2 (LRFD): excentricidad de la resultante factorada frente al limite de la base | **obliga** | `AASHTO_LRFD_9.11.6.3.3#EXC`, `AASHTO_LRFD_9.C11.6.3.3#REEMPLAZA`, `AASHTO_LRFD_9.C10.6.3.3#EQUIVALENCIA`, `AASHTO_LRFD_9.11.6.5.1#EXC` |
| `F9.E3_LRFD` | Fase 9 - Cabezal y aletas | E3 (LRFD): fuerza horizontal factorada frente a la resistencia factorada al deslizamiento | **obliga** | `AASHTO_LRFD_9.11.6.3.6#DESLIZAMIENTO`, `AASHTO_LRFD_9.10.6.3.4#RESISTENCIA`, `AASHTO_LRFD_9.11.6.3.5#PASIVA`, `AASHTO_LRFD_9.10.5.5.2.2#T1`, `AASHTO_LRFD_9.11.5.7#MUROS`, `AASHTO_LRFD_9.11.5.8#EXTREMO` |
| `F9.EMBOCADURA` | Fase 9 - Cabezal y aletas | Embocadura del punto: cabezal con aleros o recto, angulo de los aleros y lo que la Tabla C.2 del HDS-5 hace con ellos | **define** | `HDS5_3ED.TC.2`, `MC_HHD.LAMINA_02A`, `HDS5_3ED.5.4.2#PARALELO`, `HDS5_3ED.5.4.2#EVITAR` |
| `F9.EMPUJES` | Fase 9 - Cabezal y aletas | Empuje activo del relleno sobre el plano vertical del talon: coeficiente de la cuña de tanteo con la superficie real (o de Coulomb con una pendiente equivalente), altura y componentes horizontal y vertical | **define** | `MP.2.4.4.1.5.3`, `AASHTO_LRFD_9.C3.11.5.3#PLANO_DEL_TALON`, `AASHTO_LRFD_9.C3.11.5.3#DELTA`, `AASHTO_LRFD_9.3.11.5.3#CULMANN`, `AASHTO_LRFD_9.3.11.5.8.1#CUNA`, `AASHTO_LRFD_9.C3.11.5.8.1#TALUD_QUEBRADO`, `AASHTO_LRFD_9.11.6.5.2.2#ALTURA` |
| `F9.E_ASD` | Fase 9 - Cabezal y aletas | E1 a E3 (ASD): factores de seguridad al portante, al volteo y al deslizamiento con cargas de servicio | **obliga** | `E050.21`, `E050.39.13.6`, `E050.20`, `E050.17.1#SERVICIO`, `AASHTO_LRFD_9.C10.5.5.2.2#ASD` |
| `F9.GLOBAL` | Fase 9 - Cabezal y aletas | E4 y E5: estabilidad global del muro y del talud, diferidas al expediente | **obliga** | `AASHTO_LRFD_9.11.6.3.7#GLOBAL`, `E050.39.13.6`, `E050.30.3` |
| `F9.LONGITUD` | Fase 9 - Cabezal y aletas | Longitud entre cabezales con el talud muriendo en el relleno que retienen, y longitud de metrado del barril | **obliga** | `HDS5_3ED.3.3.5#ENCAJE`, `HDS5_3ED.3.1.4#LONGITUD` |
| `F9.LOSA` | Fase 9 - Cabezal y aletas | Losa de entrega y dentellon delante del cabezal | **obliga** | `AASHTO_LRFD_9.12.6.5#DENTELLON`, `MC_HHD.LAMINA_04#DENTELLON`, `MC_HHD.LAMINA_02` |
| `F9.SISMO` | Fase 9 - Cabezal y aletas | Demanda sismica del cabezal: empuje sismico (cuña de tanteo pseudoestatica, o Mononobe-Okabe), su punto de aplicacion, la inercia del muro y los dos casos de combinacion | **obliga** | `AASHTO_LRFD_9.11.6.5.3#VALIDEZ`, `AASHTO_LRFD_9.C11.6.5.3#CUNA`, `AASHTO_LRFD_9.C11.6.5.4#CEDENTE`, `AASHTO_LRFD_9.C11.6.5.4#K0`, `AASHTO_LRFD_9.3.11.5.2#K0`, `AASHTO_LRFD_9.11.6.5.3#DISTRIBUCION`, `AASHTO_LRFD_9.C11.6.5.3#RESULTANTE`, `AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE`, `AASHTO_LRFD_9.11.6.5.2.2#REDUCCION`, `AASHTO_LRFD_9.A11.3.1#KAE`, `MP.2.8.1.1.14.1#EXC` |
| `F9.SOBRECARGA` | Fase 9 - Cabezal y aletas | Sobrecarga viva de trafico sobre el relleno: altura equivalente, empuje y peso sobre el talon | **obliga** | `MP.2.4.2.2#SOBRECARGA`, `AASHTO_LRFD_9.3.11.6.4`, `AASHTO_LRFD_9.3.11.6.4#ALTURA`, `AASHTO_LRFD_9.C11.5.6#SOBRECARGA` |
| `FH.AJUSTE` | Fase 1-bis - Hidrologia: caudal de diseño | Precipitacion maxima en 24 horas para el periodo de retorno, por ajuste de una distribucion de probabilidad a la serie | **recomienda** | `MC_HHD.3.7.1`, `MC_HHD.3.7.1.1`, `MC_HHD.3.7.1.2`, `MC_HHD.3.7.1.7`, `MC_HHD.3.7.2b` |
| `FH.C` | Fase 1-bis - Hidrologia: caudal de diseño | Coeficiente de escorrentia C de la Tabla Nº 08, por cobertura vegetal, tipo de suelo y pendiente del terreno | **obliga** | `MC_HHD.3.12.2#T08`, `WSDOT_HM.2-6.2#T2-2`, `WSDOT_HM.2-6.2#FRECUENCIA` |
| `FH.FEN` | Fase 1-bis - Hidrologia: caudal de diseño | Contraste del tratamiento de los años FEN: la lluvia de diseño adoptada frente a la de la serie completa y la de la serie sin los años FEN | **obliga** | `MC_HHD.3.4#FEN`, `MC_HHD.3.12.5#PIURA` |
| `FH.INTENSIDAD` | Fase 1-bis - Hidrologia: caudal de diseño | Intensidad de la lluvia de diseño para una duracion igual al tiempo de concentracion, desde la precipitacion maxima en 24 horas | **permite** | `MC_HHD.3.8.1#DICK_PESCHKE`, `MC_HHD.3.8.1#T04`, `MC_HHD.3.8.1#DURACION`, `WSDOT_HM.2-6.3#TC_MINIMO` |
| `FH.KS` | Fase 1-bis - Hidrologia: caudal de diseño | Prueba de bondad de ajuste de Kolmogorov-Smirnov: D = max |Fo(xm) − F(xm)| contra el valor critico d de la Tabla Nº 03 | **define** | `MC_HHD.3.7.2b`, `MC_HHD.3.7.2b#T03`, `MC_HHD.3.7.2b#ELIGE` |
| `FH.Q_ESPECIFICO` | Fase 1-bis - Hidrologia: caudal de diseño | Caudal especifico Q/A del caudal de diseño, como contraste de plausibilidad | **define** | `MC_HHD.3.13`, `MC_HHD.3.12.2` |
| `FH.RACIONAL` | Fase 1-bis - Hidrologia: caudal de diseño | Caudal de diseño por el metodo racional, Q = 0.278 · C · I · A | **define** | `MC_HHD.3.12.2`, `MC_HHD.3.12.2#AREA`, `MC_HHD.4.1.2.1b`, `MC_HHD.3.12.2.1#K` |
| `FH.SERIE` | Fase 1-bis - Hidrologia: caudal de diseño | Serie de precipitacion maxima en 24 horas de la estacion: longitud de registro, años FEN que contiene y como se tratan | **obliga** | `MC_HHD.3.4#FEN`, `MC_HHD.3.4#REGISTRO`, `MC_HHD.3.12.5#PIURA` |
| `FH.TC` | Fase 1-bis - Hidrologia: caudal de diseño | Tiempo de concentracion de la cuenca, por el metodo declarado en el CSV de cuencas | **define** | `MC_HHD.3.9#T05`, `MC_HHD.3.9#T05_KIRPICH`, `MC_HHD.3.9#T05_CALIFORNIA`, `MC_HHD.3.9#T05_FAA`, `MC_HHD.3.9#T05_SCS`, `MC_HHD.3.12.2.1#TC` |

## 7. Discrepancias declaradas

`CLAUDE.md` obliga, cuando la fuente primaria gana a la hoja de ruta, a
declararlo en el punto de uso, a reportar el defecto contra la hoja de
ruta **y a dejar dicho que la hoja de ruta sigue mal mientras no se
corrija**. La tercera obligación vive aquí.

### abierta

- **`DIS-AASHTO-GAMMA-EV-12.6.1` — que extremo del factor de carga de EV -- empuje vertical de tierra -- aplica a una ESTRUCTURA ENTERRADA.** Gana **AASHTO_LRFD_9 (Art. 3.4.1, = Manual de Puentes 2.4.5.3.1)**: PARA LA VERIFICACION DE FLOTACION, y solo para ella. El argumento no es de jerarquia -- las dos son `shall` y la 12.6.1 es ademas la especial para estructuras enterradas -- sino de QUE MAGNITUD SE ESTA VERIFICANDO. La 12.6.1 fija el extremo con que se diseña la estructura POR el empuje de tierra, donde EV es la SOLICITACION y el maximo es el extremo desfavorable. En V7, EV es lo que SUJETA al conducto contra la subpresion: es resistencia, no solicitacion, y ahi el extremo desfavorable es el minimo. Aplicar el maximo haria la comprobacion MAS FACIL, que es la direccion insegura, y por eso leerla literalmente aqui contradice el proposito del propio Art. 3.4.1. Y ES UNA LECTURA, no una cita: el texto de 12.6.1 NO trae esa salvedad. Se declara asi, en vez de resolverse en silencio, porque el proyecto no tiene numeral que la sostenga.
  - Si se sigue la otra: V7 pasaria a mayorar el lado estabilizante. Medido sobre la corrida del entregable de C7 -- C-01, marco 1.20 x 0.90 --: el estabilizante pasaria de 23.256 a 34.884 kN/m contra los mismos 20.405 kN/m de subpresion, y el margen se multiplicaria por cinco. O sea que seguir la otra parte NO endurece la verificacion: la ablanda, y un conducto que hoy no pasa pasaria. Es la direccion insegura, y es la razon de que esta discrepancia importe aunque su efecto hoy sea que ningun punto cambie de veredicto.
  - *AASHTO_LRFD_9 (Art. 3.4.1, = Manual de Puentes 2.4.5.3.1)*: manda investigar el MINIMO cuando la carga permanente aumenta la estabilidad: «Si la carga permanente aumenta la estabilidad ... tambien se debera investigar el valor minimo del factor de carga para dicha carga permanente»
  - *AASHTO_LRFD_9 (Art. 12.6.1, estructuras enterradas)*: manda aplicar el MAXIMO, sin salvedad: «For vertical earth pressure, the maximum load factor from Table 3.4.1-2 shall apply»
- **`DIS-LUZ-DENOMINACION` — la MAGNITUD que el umbral de denominacion alcantarilla/puente compara (que «luz» es, y en un cruce multicelda cual) y su CIFRA (6.0 m frente a 20.0 ft = 6.096 m).** Gana **HDS5_3ED**: en la MAGNITUD: es la unica de las cuatro que dice que ancho cuenta en un cruce de varias celdas --el total del cruce, para la clasificacion como puente--, y las otras tres coinciden en lo que descarta el hallazgo R48-001: la luz es una propiedad de la ESTRUCTURA (su abertura o luz libre), no el ancho del cauce natural. Por eso `luz_m` es la abertura libre que el cruce exige de la estructura, leida de la topografia, y M1 la compara entera; es ademas la lectura conservadora, porque manda al Manual de Puentes el cruce que lo exige. En la CIFRA gana el Manual de Hidrologia: el codigo compara 6.0 m ([N], LUZ_MAX_ALCANTARILLA), mas exigente que los 6.096 m de AASHTO y de HDS-5; una luz de 6.05 m es puente aqui y no alli
  - Si se sigue la otra: con la luz libre POR VANO de la Fig. 1.10-a un cruce de 8 m salvado con tres celdas de 2.5 m seria obra de arte menor y se disenaria con el Manual de Hidrologia, mientras el NBIS lo cuenta como puente; y con los 6.096 m de AASHTO una luz entre 6.0 y 6.096 m dejaria de ser puente. Lo que el hallazgo leyo en el codigo --comparar el ANCHO DEL CAUCE-- confundiria el dato hidraulico con el estructural
  - *MC_HHD*: «la estructura cuya luz sea menor a 6.0 m» y «cuya luz sea mayor o igual a 6.0 m, siguiendo lo establecido en las especificaciones AASHTO LRFD»: escribe «luz» sin definirla y la cifra 6.0 m
  - *MP*: obras de arte menores son las de «luz libre menor que 6.00 m (20 ft)», y su Fig. 1.10-a dibuja la luz libre POR VANO, entre pilares: bajo esta lectura un marco de tres celdas de 2.5 m tiene luz libre 2.5 m y es obra de arte menor
  - *AASHTO_LRFD_9*: «Any structure having an opening not less than 20.0 ft»: la ABERTURA de la estructura, y 20.0 ft son 6.096 m, no 6.0
  - *HDS5_3ED*: los cruces que superan 20 ft (6.1 m) de luz «either as a single barrel or the total width of a multiple barrel crossing» son puentes para el NBIS; y para el metodo hidraulico la guia razonable es modelar como puente «a single culvert with a span of 20 ft (6.1 m) or more»

### resuelta

- **`DIS-AASHTO-F-LISTA-ABIERTA` — si la enumeracion de la Clase de Sitio F es abierta o cerrada.** Gana **AASHTO_LRFD_9 · articulado**: por jerarquia: el comentario explica el articulado y no puede estrecharlo. Se declara, y no se archiva, porque un revisor puede apoyarse en el comentario y hay que poder responderle. LO QUE IMPORTA ES QUE LA DECISION NO DEPENDE DE ESTO: si la lista es cerrada, un suelo licuable NO es Clase F y la premisa es falsa; si es abierta, la norma calla y la premisa es no sostenida. Por las dos lecturas el salto sigue sin estar escrito, y por las dos rige la prohibicion de suponer la clase sin dato geotecnico. La resolucion se apoya en esa prohibicion -- que es articulado y no admite lectura doble -- y no en el recuento de categorias
  - Si se sigue la otra: citar el «the three categories» como si fuera articulado da un argumento mas fuerte del que la fuente permite, y es refutable en el acto: fue exactamente lo que la refutacion adversarial R95-073 hizo con la primera version de NOR-AAS-02
  - *AASHTO_LRFD_9 · articulado*: la fila F de la Tabla 3.10.3.1-1 abre con «Soils requiring site-specific evaluations, SUCH AS:», que es lista ejemplificativa: no dice «the following» ni «limited to» ni cuenta las categorias
  - *AASHTO_LRFD_9 · comentario*: la Tabla C3.10.3.1-1, paso 1, la llama «THE THREE CATEGORIES of Site Class F», que la lee como cerrada
- **`DIS-CN-CALICATAS` — si el Cuadro 4.1 dice cuando son 4 calicatas y cuando 6.** Gana **MS**: verificado contra el PDF. Afirmar que la fuente calla donde habla es la forma inversa del mismo defecto que persigue este cluster: en vez de citar lo que no dice, se niega lo que si dice, y el resultado es igual de invisible -- un vacio inventado que convierte en [A] lo que es [N]
  - Si se sigue la otra: la densidad de la campaña geotecnica se elegiria como criterio [A] cuando la norma la determina, y una autopista de 4 carriles por sentido saldria con la mitad de las calicatas que el Cuadro exige
  - *codigo*: el comentario de CALICATAS_POR_SENTIDO afirmaba: «El Cuadro admite ademas 6 en vez de 4 para autopistas con 4 carriles por sentido, y «4 (o 6)» para duales. Ese 6 NO se transcribe aqui: el Cuadro lo da como alternativa SIN DECIR CUANDO APLICA CADA UNA, de modo que la eleccion entre 4 y 6 no es [N]»
  - *MS*: el Cuadro 4.1 SI lo condiciona, y por carriles por sentido
- **`DIS-CN-EG-508-07` — la pagina impresa del relleno minimo de 0,30 m del HDPE.** Gana **EG2013**: el desfase de este documento es +8 y es el mas grande del corpus: confundir pagina impresa con pagina PDF produce exactamente un error de 8, que es la distancia entre las dos cifras que el repositorio manejaba
  - Si se sigue la otra: la cita mas load-bearing del proyecto -- la que llega impresa a la memoria -- manda al revisor a una pagina que no dice lo que la cita afirma
  - *codigo*: el repositorio cito esa frase primero en la pag. impresa 982 y despues en la 984, y las dos citas conviven en el expediente
  - *EG2013*: la pagina impresa que la imprime, verificada
- **`DIS-E060-BORDE-2-0` — en que fila de la Tabla 4.4 cae un SO4 de 2,0 % exacto en el suelo (o de 10 000 ppm exacto en el agua).** Gana **hoja_de_ruta**: no es que la hoja de ruta contradiga a la fuente primaria: es que la fuente CALLA, y la hoja de ruta es la fuente de verdad del proyecto mientras el documento normativo no la contradiga. Se declara porque es una LECTURA y no un dato -- la tabla impresa no la escribe --, y por eso cada fila del registro dice si su limite inferior es estricto en vez de esconder la respuesta en un `>=` del codigo
  - Si se sigue la otra: la unica diferencia practica entre las dos filas es el CEMENTO -- V frente a V mas puzolana --: la relacion a/c y el f'c minimo son los mismos, de modo que el recubrimiento del refuerzo no cambia por este borde
  - *E060*: no lo dice. Verificado sobre la imagen renderizada de la pag. impresa 38: la fila severa se imprime «0,2 ≤ SO4 < 2,0», con cota superior ESTRICTA, y la muy severa «2,0 < SO4», con cota inferior ESTRICTA y sin «≤». El valor exacto no cae en ninguna de las dos: es un hueco del texto impreso
  - *hoja_de_ruta*: su Sec. 3.3 escribe la fila severa como «0.20 - 2.00» y la muy severa como «> 2.00», de modo que el punto exacto queda en SEVERA
- **`DIS-HDS5-EDICIONES` — la constante K del termino de friccion del control de salida.** Gana **HDS5_3ED**: es la unica de las dos que publica la conversion SI. La copia de 1985 opera en unidades inglesas con rotulos duales, y el «si» de su nombre de archivo se refiere a sus cartas metricas, no al cuerpo del documento
  - Si se sigue la otra: aplicar 29 en metrico multiplica el termino de friccion por 29/19.63 = 1.477 (+47.7 % sobre el termino), que en CP-8 sube H de 0.4977 a 0.5455 m (+9.6 % sobre H), y no falla ruidosamente: devuelve numeros plausibles y equivocados
  - *HDS5_3ED*: «KU = 29 in English Units (19.63 in SI)»
  - *HDS5_SI_1985*: imprime 29 en sus ecs. (4b) y (5) con rotulos duales «ft (m)» y NO imprime 19.63, pese al «si» del nombre del archivo
- **`DIS-HR-30M-VS-100FT` — la profundidad sobre la que se define la clase de sitio.** Gana **AASHTO_LRFD_9**: 100 ft son 30.48 m: la profundidad de campaña que hay que pedir es la misma y el numero es defendible, de modo que esto NO es una contradiccion de fondo sino una atribucion -- el mismo genero que DIS-HR-G-LAUSHEY, donde el 9.8 era correcto y la pagina no lo imprimia. Trabajar en SI es la regla del proyecto y es legitimo; atribuirle a AASHTO un texto que no imprime, no. Y la correccion no debilita nada: el argumento de que el SPT de 15 m de E.050 Art. 38 no cierra este criterio se sostiene con MAS margen sobre 30.48 m que sobre 30
  - Si se sigue la otra: un revisor que abra el Art. 3.10.3.1 buscando los «30 m» no los encuentra, y una cita que no se puede comprobar es indistinguible de una inventada -- en el campo que precisamente define que ensayo hay que contratar
  - *hoja_de_ruta*: Sec. 0.5 pedia «la caracterizacion de los 30 m superiores (Vs30 o N) que define la clase», y el criterio 'clase_sitio' se lo atribuia al articulado: «Los 30 m son parte de la DEFINICION de la clase (AASHTO LRFD Art. 3.10.3.1)». EL CRITERIO SE CORRIGIO EN S14 (pide «100 ft (30.48 m)» y declara esta discrepancia); LA HOJA, EN I2 (Sec. 0.5 y Tablero 3.6 escriben la profundidad que el articulado imprime)
  - *AASHTO_LRFD_9*: el Art. 3.10.3.1 dice «the upper 100 ft», y la Tabla 3.10.3.1-1 define v_s, N y s_u «for the upper 100 ft of the soil profile». La cifra «30 m» no esta impresa en el numeral
- **`DIS-HR-A807` — la norma que fija el calibre de la plancha de TMC por altura de relleno.** Gana **ASTM_A796**: la remision de la hoja de ruta era falsa, y desde N1 lo es por VERIFICACION y no por ausencia: A807 es practica de instalacion (22.1) y el calibre lo determina A796 por procedimiento. El «gana» que esta discrepancia traia anotado desde I2 era provisional y la fuente lo confirma CON UN MATIZ que el anticipo no tenia: A796 tampoco trae «tabla de calibre por altura»; lo que trae es el procedimiento que las tablas de fabricante derivan
  - Si se sigue la otra: se busca el calibre en un documento que no lo tiene (A807), y despues se busca una TABLA en el que si lo determina (A796), que tampoco la tiene: la busqueda termina dos veces en un vacio aparente que no es tal
  - *hoja_de_ruta*: lo remitia a «ASTM A-807 / AASHTO M36 -- calibre según altura» en la tabla de su Fase 8, y con la disputa anotada al pie desde I2. CORREGIDA EN N1, con la fuente en la mano: la fila remite a ASTM A796/A796M como PRACTICA DE DISEÑO (el espesor sale del procedimiento de sus num. 7 a 10 y se elige de las Tablas 2 a 35; la cobertura minima, del num. 11) y a A760/A760M = M 36 como norma de producto. Las remisiones que ademas traian su Sec. 7.A y su Anexo B -- sobre la ALTURA minima de relleno, no el calibre -- se retiraron en I2 con DIS-HR-H-RELLENO-MIN
  - *ASTM_A796*: A807/A807M es una practica de INSTALACION, no la norma del calibre: su num. 22.1 manda que la construccion e instalacion «shall conform to Practice A798/A798M or A807/A807M», y es la unica mencion de A807 en las 20 paginas con contenido del ejemplar (la impresa 1, la lista de normas referenciadas del num. 2.1, falta)
  - *ASTM_A796*: el calibre no se LEE de una tabla por altura de cobertura -- no la hay: afirmacion negativa SIN_TABLA_CALIBRE_POR_COBERTURA_A796, con las 21 paginas y los 35 titulos de tabla como ambito --: el espesor se SELECCIONA de las tablas de propiedades seccionales por el area de pared requerida que sale del calculo (num. 8.1.1.2, SF = 2)
  - *ASTM_A796*: el unico cruce entre espesor y cobertura de la norma va al reves de lo que la hoja suponia: no «calibre por cobertura» sino «cobertura por calibre», y solo en un escalon (Hmin >= 600 mm si el espesor es menor de 1.32 mm; 300 mm en todo caso)
  - *ASTM_A796*: la norma de PRODUCTO a la que remite es A760/A760M (num. 17.1), que es la misma de doble designacion que AASHTO M 36: la mitad «AASHTO M36» de la fila era correcta como norma de producto y falsa como fuente del calibre
- **`DIS-HR-CICLOPEO` — el f'c minimo de la matriz del concreto ciclopeo.** Gana **EG2013**: sobre el MISMO material rigen las dos normas y por la regla del mayor de Sec. 0.2 gobierna la mayor. La hoja de ruta mira solo a E.060 y no ve que sobre el mismo material rige tambien la norma vial del MTC
  - Si se sigue la otra: quien lea la hoja de ruta sin leer el codigo dimensionara un cabezal de ciclopeo con una matriz de 10 MPa que este calculo va a rechazar
  - *hoja_de_ruta*: su Sec. 9.4 pedia f'c de matriz >= 10 MPa citando solo el Art. 22.10 de E.060. CORREGIDA EN I2: la linea escribe los dos minimos y el mayor (14 MPa, Clase G de la Tabla 503-07), con su nota
  - *EG2013*: la Clase G de la Tabla 503-07 -- concreto ciclopeo -- pide 14 MPa, y la Seccion 503 es la que este proyecto cita para los cabezales
- **`DIS-HR-CLASE-DE-SITIO-F` — la premisa de Sec. 0.5: «el sitio clasifica como Clase de Sitio F por susceptibilidad a licuefaccion».** Gana **AASHTO_LRFD_9**: porque la hoja de ruta no tiene con que sostener el salto y las fuentes tienen con que vedarlo, y son dos cosas distintas: (1) NINGUNO de los dos documentos que el criterio invoca escribe «suelo licuable -> Clase F»; en las 1905 paginas de AASHTO los conjuntos de paginas con `liquef` y con «Site Class F» son DISJUNTOS, y en las 673 del Manual la licuefaccion vive en once pasajes de cimentaciones y del Apendice A11, ninguno en el numeral de clases de sitio. (2) Pero el «such as» deja la lista abierta, de modo que el silencio solo daria una premisa NO SOSTENIDA, no una premisa falsa -- y esa es la parte del hallazgo que la refutacion adversarial R95-073 habia acotado con razon. (3) Lo que cierra la cuestion es que las dos fuentes PROHIBEN suponer la clase E o F sin determinacion de la autoridad o dato geotecnico. El expediente no tiene ninguna de las dos: el SPT esta pendiente. Suponerla no es una adopcion declarable del proyectista, es lo que la norma veda. El Manual y E.030 concurren, cada uno por su via, y por eso el resultado no depende de que Via de Sec. 0.2 se elija
  - Si se sigue la otra: la memoria declara formalmente una clase de sitio que ninguna fuente sostiene y que las dos prohiben suponer, y la declara ademas para nada: la fila F no tiene factor -- son cinco asteriscos en las cinco columnas --, de modo que la premisa no aporta un numero al calculo y si aporta al expediente una afirmacion refutable de un vistazo. Es la forma exacta del defecto que la propia Sec. 0.5 llama el mas grave que ha tenido este expediente
  - *hoja_de_ruta*: Sec. 0.5 decia: «El sitio clasifica como Clase de Sitio F por susceptibilidad a licuefaccion: arenas saturadas con NF a 1.4 m en la llanura del Bajo Piura. Clasificarlo como D o E mientras la Fase 0-bis advierte riesgo de licuefaccion seria una contradiccion interna del expediente. Eso no ha cambiado.» Y en Fase 0-bis, punto 2, escribia «la condicion S5 / Clase F», con una barra que asimila las dos taxonomias. CORREGIDA EN I2: la Sec. 0.5 declara la clase INDETERMINADA con la prohibicion de suponerla E o F, separa las dos taxonomias, y el pasaje entrecomillado de la Fase 0-bis quedo literal con su elision marcada (los cuatro defectos de §3 de docs/resolucion_clase_sitio.md)
  - *AASHTO_LRFD_9*: PROHIBE SUPONERLA: «Site classes E or F should not be assumed unless the authority having jurisdiction determines that... or... are established by geotechnical data», en el articulado, al pie de la Tabla 3.10.3.1-1. Y manda investigar: «a site investigation shall be undertaken sufficient to determine the site class»
  - *MP*: lo mismo y mas duro: «Las clases de Sitio E o F NO SERAN SUPUESTAS a no ser que la Entidad determine la clase de sitio E o F o estas sean establecidas por datos geotecnicos»
  - *E030*: es la fuente de la letra, y su letra es OTRA: los suelos potencialmente licuables son la primera viñeta del perfil S5 «Suelos excepcionales» de su Tabla Nº 2, que es un esquema distinto (S0-S5, por descripcion) del de AASHTO (A-F, por rigidez medida sobre los 100 ft superiores)
  - *E030 · Tabla Nº 4*: y tampoco da factor a su categoria excepcional: la Tabla Nº 4 «Factor de suelo S» tiene columnas S0 a S4 y ninguna S5. En la zona 4, ya la columna S4 dice «Requiere un analisis de respuesta de sitio»
- **`DIS-HR-D-MAX` — los topes de diametro por material (2.70 / 2.10 / 1.50 m).** Gana **ASTM_A760**: la fuente primaria, leida de los PDF de normas/, desmiente las dos atribuciones contrastables sobre el original. No son topes normativos: son topes de CATALOGO, y como tales descartaban material en silencio con una cita que ninguna norma sostiene. La tercera, la del HDPE, se contrasto en N2 sobre la traduccion no oficial de AASHTO M 294-11 y resulto CIERTA (la serie termina en 1500 mm), pero no devuelve el tope a la norma: la clase del dato la fija la eleccion, que es de catalogo para los tres, y una traduccion sin firma no sostiene un rotulo «por norma de producto»
  - Si se sigue la otra: un punto que necesite mas de 2.10 m de TMC se declara no factible por una razon que la norma citada no sostiene
  - *hoja_de_ruta*: su Anexo B los declaraba bajo el rotulo «topes por norma de producto - VERIFICAR», atribuidos a ASTM C76 / AASHTO M170, AASHTO M36 / ASTM A760 y AASHTO M294. CORREGIDA EN I2: §3.2, §3.4, Tablero 1.2, Anexo A, Anexo B y Anexo C reescritos con la verdad verificada -- topes de CATALOGO [A], 'D_max_catalogo' --; el del HDPE quedo declarado como no contrastado (M294 ausente) hasta N2, que lo contrasto sobre la TRADUCCION NO OFICIAL de M 294-11 y actualizo la fila
  - *ASTM_A760*: su Tabla 1 tabula diametros nominales de 100 mm (4 in) a 3600 mm (144 in): los 2100 mm son una fila mas de la serie, no un maximo
  - *AASHTO_M170M*: el conjunto de sus Tablas 1 a 5 cubre de 300 mm (Tablas 2 a 5) a 3600 mm (Tablas 3 y 5), y la Sec. 7.2 «Modified and Special Designs» preve ademas diseños por encima de lo tabulado con permiso del propietario. LEIDO TABLA POR TABLA la envolvente no es uniforme -- la Tabla 1, Clase I, va de 1500 a 3450 mm --, y la redaccion anterior de esta cita, «Tablas 1 a 5: de 300 a 3600 mm», era falsa leida distributivamente
  - *AASHTO_M294_TRAD*: su num. 1.1.1 (traducción no oficial) fija el ambito en los tamaños nominales «de 300 a 1500 mm», y su num. 7.2.1 desarrolla la serie cerrada de doce diametros, de 300 a 1500 mm: el 1500 es la ultima fila y no hay «y superiores». El tope de 1.50 m del HDPE coincide con el techo de la norma de producto -- segun la traduccion, sin firma --
- **`DIS-HR-FORMAS-HDS5` — las DOS formas de la ecuacion de control de entrada no sumergido del HDS-5 (columna «Equation Form» de la Tabla A.1).** Gana **HDS5_3ED**: la fuente primaria esta transcrita y verificada: las 18 filas de `T_HDS5_A1` llevan su `equation_form` leido de la columna de la tabla (metodo AMBOS; releidas en D9 fila por fila, 18 de 18), y las ecs. (A.1)/(A.2) del num. A.2.1 estan citadas y verificadas (HDS5_3ED.A.2; el parrafo que las rotula «Form (1)» y «Form (2)» esta en la pag. impresa A.1 / PDF 190, y la (A.2) abre la A.2 / PDF 191). El codigo ya bifurcaba por forma (`modelos.ConstantesHDS5.forma`, `M4._hw_sobre_D_no_sumergido`, C3) y la memoria imprime que forma uso y por que (`F4.FORMA_HDS5`); la que habia que corregir era la v8, y D9 la corrigio
  - Si se sigue la otra: quien implemente el cajon desde la v8 tal como estuvo hasta D9 -- sin la Forma 2 -- copiara la ec. (A.1) y le cambiara las constantes, y el resultado es un HW MAYOR que el real: el H_c/D espurio domina por dos ordenes al Ks*S que resta. Medido en la auditoria de I3 sobre el marco de la linea base (2.00 x 1.50 m, Q = 6 m3/s, S = 0.004, Carta 10 escala 1): 3.047 m frente a los 1.592 m reales, +91 % -- sobrediseño y falsos no-factibles, con sus deltas de rasante inventados. Para que la direccion se invirtiera haria falta S > 2*H_c/D, fuera incluso de dominios.S_CAUCE_MAX. ESTA FICHA DECIA LO CONTRARIO hasta esa auditoria -- «el HW sale MENOR que el real», heredado de la fila D-9 de C2/C3, que miraba el termino Ks*S sin mirar el H_c/D que la copia arrastra --: un efecto con la direccion equivocada hace elegir mal que defecto corregir primero, y por eso se corrige aqui y no en una nota
  - *hoja_de_ruta*: su Fase 4, §4.2, escribia UNA ecuacion de control de entrada no sumergido -- la que lleva el termino Ks*S --, la rotulaba «Forma 1» y jamas decia que existiera otra: medido sobre el documento entero (remedido en I3), «Forma» aparecia TRES veces y las tres eran «Forma 1»; «Forma 2» no aparecia nunca. Presentaba ademas las constantes K, M, c, Y de la Tabla A.1 como si una sola ecuacion las consumiera, y usaba «las dos formas» (dos veces, en la nota de la transicion y en la de MAT-D10) para nombrar las dos RAMAS -- no sumergida y sumergida --, que colisiona con el termino «Equation Form» del propio HDS-5. CORREGIDA EN D9 (commit «cierre(D9)»), con los cinco puntos del paquete de §16.19 de docs/ruta_familia_c.md y nota «Corregido (DIS-HR-FORMAS-HDS5, D9)» en cada uno: la §4.2 escribe ahora la Forma 2, ec. (A.2), tras la (A.1), con la regla de seleccion por la columna «Equation Form» de la Tabla A.1 (las tres circulares que tabula son Forma 1; del cajon solo la Carta 8 lo es); las notas de la transicion y de MAT-D10 dicen «ramas» y condicionan el umbral del signo a la Forma 1; el requisito de programacion de §4.2.1 dice que la Forma 2 no usa H_c en control de entrada; y la tabla de constantes dice que K y M estan ajustadas cada una a su forma, con la direccion del error corregida: el HW sale MAYOR. Fuera del paquete y sin corregir, declarado: el bloque de codigo de su §12 transcribe un HDS5_INLET sin la clave `forma`, que el codigo lleva desde C2; es una copia envejecida de codigo, no una afirmacion sobre el HDS-5
  - *HDS5_3ED*: su Tabla A.1 tiene una columna «Equation Form» con valores 1 y 2, fila por fila: la Forma 1 es la ec. (A.1), HW_i/D = H_c/D + K*(q*)^M + Ks*S, y la Forma 2 es la ec. (A.2), HW_i/D = K*(q*)^M, SIN el termino Ks*S. De las cartas de cajon transcritas, solo la Carta 8 es Forma 1; las Cartas 9 a 12 son Forma 2. Las tres configuraciones circulares que la §4.2 tabula (filas de las Cartas 1 y 2) son todas Forma 1, que es por lo que la omision no se nota en las Familias A y B
- **`DIS-HR-G-LAUSHEY` — la atribucion del valor g = 9.8 m/s2 al num. 4.1.1.3.7 c).** Gana **MC_HHD**: verificado contra el PDF barriendo las 225 paginas: «9.8» como valor de la gravedad aparece en dos paginas, ninguna de ellas la 80. EL NUMERO ES DEFENDIBLE Y LA CITA NO LO ERA: es el mismo genero de defecto que el proyecto purgo con el «19.62 = 2g». Se corrige la atribucion, no el numero
  - Si se sigue la otra: un revisor que abra la pag. 80 buscando el 9.8 no lo encuentra, y una cita que no se puede comprobar es indistinguible de una inventada
  - *hoja_de_ruta*: escribia «d50 en m, V en m/s, g = 9.8 m/s2» bajo el encabezado «Laushey — num. 4.1.1.3.7 c), pag. 80», presentando el 9.8 como si el numeral lo imprimiera. CORREGIDA ANTES DE I2 (su Fase 6 lleva la nota «Corregido (NOR-HID-01, MAT-O7)» con la atribucion buena) y este registro quedo atras: el estado se pone al dia en I2
  - *MC_HHD*: el num. 4.1.1.3.7 c), pag. impresa 80, define g SIN numero: «g : Aceleracion de la gravedad (m/s2)». El 9.8 SI esta en el Manual, pero en otros dos numerales -- el 3.12.5 (pag. impresa 63) y el 4.1.1.5.4 b.2.4) (pag. impresa 111) --, y el 9.81 no aparece ni una vez
- **`DIS-HR-H-EQ` — la altura de suelo equivalente de la sobrecarga de trafico (h_eq).** Gana **AASHTO_LRFD_9**: por la Via 1 de Sec. 0.2 (AASHTO LRFD de extremo a extremo) y por la regla del mayor: el Manual fija un PISO («no menor que la equivalente a 0.60 m») y AASHTO tabula el valor. Los dos rigen, y h_eq es el mayor de los dos. El 0.60 plano no es defendible para un cabezal de 2 m con trafico perpendicular
  - Si se sigue la otra: con h_eq = 0.60 m fijo, un cabezal de 2.0 m con trafico perpendicular subestima la sobrecarga viva en un factor 1.87, y con gamma_LS = 1.75 eso llega al empuje de diseño
  - *hoja_de_ruta*: escribia «Sobrecarga en el trasdos (num. 2.1.4.3.9, pag. 91): ... se añade sobrecarga vertical >= 0.60 m de relleno equivalente ... En un cabezal bajo terraplen vial SIEMPRE APLICA». Dos defectos en una frase: el numeral es «Aparatos de Apoyo» y el «siempre aplica» borra la condicion de distancia que la fuente pone. LA FRASE PRINCIPAL SE CORRIGIO ANTES DE I2 (num. 9.2 de la v8, con su nota del conflicto #4: piso condicional + tabla de AASHTO por altura y orientacion); EL RESIDUO -- el numeral falso en el comentario `SOBRECARGA_TRASDOS_H_EQ` del Anexo B -- se corrigio en I2
  - *MP*: el num. 2.1.4.3.9 se titula «Aparatos de Apoyo» y no contiene ni la palabra sobrecarga ni el 0.60. El texto real esta en el num. 2.4.2.2 «Cargas de Suelo: EH, ES, y DD», pag. impresa 102, y es CONDICIONAL: «Cuando se prevea trafico a una distancia horizontal, medida desde la parte superior de la estructura, menor o igual a la mitad de su altura...», con exencion expresa si hay losa de aproximacion
  - *AASHTO_LRFD_9*: el Art. 3.11.6.4 tabula h_eq por altura del muro, y para 2.0 m con trafico perpendicular da 1.12 m por interpolacion obligatoria. El Manual de Puentes NO transcribe esas tablas: su traduccion de la Sec. 3.11 se corta en el empuje pasivo k_p
- **`DIS-HR-H-RELLENO-MIN` — la altura minima de relleno sobre la clave para concreto y TMC.** Gana **AASHTO_LRFD_9**: «no fijado» ya no es cierto: lo fija AASHTO LRFD, que el propio Sec. 0.2 adopta de extremo a extremo, y las dos remisiones de la hoja son falsas (M 170M no da alturas de relleno y A-807 no es la norma que se le atribuye). Declarar un vacio sobre la fuente que SI trae el dato es el defecto que Sec. 0.5 llama el mas grave
  - Si se sigue la otra: se declara vacio lo que la norma adoptada tabula, y la cobertura minima queda sin piso
  - *hoja_de_ruta*: su Sec. 7.A decia «No fijado. Remite al Proyecto, AASHTO M-170M (clases I-V) o ASTM A-807». CORREGIDA EN I2: la fila remite a AASHTO LRFD 12.6.6.3 / Tabla 12.6.6.3-1, y el comentario del Anexo B tambien
  - *AASHTO_LRFD_9*: el Art. 12.6.6.3 y la Tabla 12.6.6.3-1 tabulan la cobertura minima para los tres tipos de conducto del catalogo
- **`DIS-HR-KA-COULOMB` — el coeficiente de empuje activo ESTATICO del trasdos del cabezal.** Gana **MP**: es la fuente primaria del marco elegido en §9.1 y la unica formulacion homogenea con el incremento sismico: restar un K_AE de Mononobe-Okabe (con i, β y δ) a un Ka de Rankine (que ignora los tres) mezcla dos modelos sobre el mismo muro. La hoja de ruta transcribia el caso particular sin nombrarlo
  - Si se sigue la otra: con i = β = δ = 0 ningun numero se mueve; en cuanto alguno deja de ser cero el coeficiente cambia (en el bloque C de CP-9, +9.7 % con i = 5°, β = 5° y δ = 17°; barriendo las cuatro ventanas declaradas, de −11.1 % a +44.4 %, y NO el «−6.25 % a +7.23 %» que la enmienda de EXT-0 escribio en la v8 y que EXT-7 corrigio), y quien lea la hoja sin leer el codigo dimensionara con el coeficiente equivocado
  - *hoja_de_ruta*: su §9.2 escribia «Ka = tan²(45 − φ/2)» sin decir de donde salia, y el codigo la seguia: empuje estatico y sobrecarga con Rankine (`ka_rankine`) mientras el incremento sismico iba con Mononobe-Okabe, que es Coulomb con aceleracion. CORREGIDA EN EXT-0: la linea nombra el Ka de Coulomb del Manual y dice que con β = δ = 0 y trasdos vertical se reduce a la forma que escribia
  - *MP*: el coeficiente de empuje lateral activo «se puede tomar como» la expresion de Coulomb, ecs. 2.4.4.1.5.3-1 y -2, con θ, δ y β; con angulos nulos coincide con tan²(45 − φ/2) (diferencia medida −5.6e-17)
- **`DIS-HR-M294-PASO` — donde empieza el paso de 150 mm en la serie de diametros nominales del HDPE (AASHTO M 294).** Gana **AASHTO_M294_TRAD**: la fuente imprime la serie diametro a diametro y la hoja de ruta la resumia de memoria. Es una traduccion no oficial, sin firma, y es lo unico que hay en normas/; el original en ingles (ausente) tendria que confirmarlo. No cambia ningun valor del proyecto: la progresion arranca en 0.90 m y desde ahi la serie SI es de 150 mm, que es lo que 'diametros_normalizados' afirma y CP11 comprueba; lo que estaba mal era la frase que lo justificaba
  - Si se sigue la otra: quien leyera la v8 creeria que M 294 no tabula el 675 mm; para el calculo es inocuo, porque ningun tamaño bajo 0.90 m se recorre, y por eso se corrige la frase y no el criterio
  - *hoja_de_ruta*: su §3.2, «Por qué funciona», escribia que «AASHTO M294 lo hace en pasos de 150 mm por encima de 600 mm», con lo que tras el 600 vendria el 750 y no existirian ni el 675 ni el paso de 75 mm. CORREGIDA EN N2 con la nota «Corregido (DIS-HR-M294-PASO, N2)»: el paso de 150 mm empieza en 750 mm
  - *AASHTO_M294_TRAD*: su num. 7.2.1 (traducción no oficial) lista 300, 375, 450, 525, 600, 675, 750, 900, 1050, 1200, 1350 y 1500 mm: de 300 a 750 el paso es de 75 mm y el de 150 mm va de 750 a 900 y de ahi hasta 1500
- **`DIS-HR-VIA-DE-LA-LICUEFACCION` — por que via entra la licuefaccion en el diseño sismico.** Gana **AASHTO_LRFD_9**: es el argumento POSITIVO, y por eso vale mas que el silencio: si la licuefaccion hiciera Clase F por si sola, la fila del sitio no tendria factor -- cinco asteriscos -- y el procedimiento del num. 10.5.4.2 no podria arrancar, porque empieza por un espectro «no licuado» que exige un factor de sitio de 3.10.3.2 aplicable. Las dos reglas solo son coherentes si un suelo licuable puede clasificar A-E y evaluarse aparte, que es exactamente el reparto que el expediente ya hace con su SPT de 15 m
  - Si se sigue la otra: el riesgo de licuefaccion se contabiliza dos veces o ninguna: entra por el factor de sitio -- donde no hay numero que leer -- y deja sin disparar la evaluacion del num. 10.5.4.2, que es la que produce las verificaciones que este sitio necesita (perdida de resistencia, asentamiento, desplazamiento lateral)
  - *hoja_de_ruta*: Sec. 0.5 hacia de la licuefaccion la CAUSA de la clase de sitio -- «Clase de Sitio F POR susceptibilidad a licuefaccion» --, de modo que el riesgo geotecnico entraba al calculo por el factor de sitio. CORREGIDA EN I2: la Sec. 0.5 lleva el reparto de la fuente -- la clase por rigidez medida (pendiente), la licuefaccion por el num. 10.5.4.2 y el SPT de la Fase 0-bis --
  - *AASHTO_LRFD_9*: la evalua en la Seccion 10, Cimentaciones, num. 10.5.4.2 «Liquefaction Design Requirements», y la dispara por zona sismica 3 o 4 MAS napa freatica en los 50 ft superiores MAS caracteristicas de suelo. Ninguna de las tres condiciones es la clase de sitio, y «Site Class F» no aparece en ninguna pagina de la Seccion 10
  - *AASHTO_LRFD_9 · 10.5.4.2 in fine*: y ademas ESPERA que a un sitio licuable le aplique un factor de sitio tabulado: manda analizar en configuracion no licuada y licuada con el mismo espectro, y acota el espectro especifico a no menos de dos tercios del general «modified by the site factors in Article 3.10.3.2»
- **`DIS-MP-LRFD-EDICION` — la edicion de AASHTO LRFD que rige el diseño del cabezal (Sec. 9.4).** Gana **AASHTO_LRFD_9**: el MP no exige la 7a: la adapta y PERMITE considerar las actualizaciones, de modo que citar la 9a esta dentro de lo que la fuente legal autoriza. Lo que queda abierto es si rige la 9a o la 10a (2024), que es una eleccion tecnica de la entidad y/o propietario a propuesta del proyectista --- la fuente permite a aquellos, no a este --- y no una discrepancia entre fuentes
  - Si se sigue la otra: citar articulos de una 7a ed. que no esta en normas/ y contra la que ninguna cita esta verificada; la memoria imprimiria numerales que nadie abrio
  - *MP*: adapta «AASHTO en su versión LRFD BRIDGE DESIGN SPECIFICATIONS del año 2014, Septima Edición» y añade que la entidad «podrá considerar las actualizaciones»
  - *AASHTO_LRFD_9*: es la 9a ed. (2020), la que esta en normas/ y contra la que estan verificadas las citas de las Secciones 3, 5, 10, 11 y 12; la 7a de 2014 no esta

### errata_de_imprenta

- **`DIS-HDS5-APENDICE-G` — el apendice al que remite el titulo de la Tabla A.1 de HDS-5.** Gana **HDS5_3ED**: el titulo se transcribe COMO LO IMPRIME, con la advertencia: corregirlo en la cita mandaria al revisor a buscar un titulo que el documento no tiene. Es errata de la fuente, y probablemente arrastre de una edicion anterior
  - Si se sigue la otra: quien busque el «Apendice G» no lo encuentra y puede concluir que la tabla no esta
  - *HDS5_3ED*: su Tabla A.1 se titula «Constants for Inlet Control Equations for Charts in Appendix G» y en esta 3a edicion NO EXISTE un Apendice G
  - *codigo*: las cartas estan en el Apendice C, «DESIGN CHARTS, TABLES, AND FORMS», que abre en la pag. impresa C.1 (PDF 211)
- **`DIS-MCHHD-LAMINA-03-TMC` — que dibuja la Lamina Nº 03 del Manual, segun el cuerpo del propio Manual y segun la lamina.** Gana **MC_HHD (Lamina Nº 03)**: es la pagina que contiene el dibujo. El cuerpo la ANUNCIA y la lamina la CONTIENE: ante una discrepancia entre el anuncio y la cosa anunciada, gana la cosa. Ademas la contradiccion es verificable en un sentido y no en el otro -- se puede contar las figuras de la lamina; no se puede deducir su contenido del anuncio --. Se registra porque un revisor que lea el cuerpo, vaya a la lamina y encuentre una TMC en la primera figura pensara que la cita del proyecto esta mal puesta, y no lo esta: lo que esta mal es el anuncio del propio Manual
  - Si se sigue la otra: ninguno sobre ningun numero: la lamina no acota nada (ver la afirmacion negativa `SIN_COTAS_LAMINA_03`). El efecto es sobre la CREDIBILIDAD de la cita -- el revisor cuenta tres figuras donde el Manual anuncia una clase --, y por eso se declara en vez de corregirse en silencio
  - *MC_HHD (cuerpo del num. 4.1.1.3.4 a))*: el cuerpo del num. 4.1.1.3.4 a), pag. impresa 73 (PDF 76), anuncia la lamina asi: «En la Lámina Nº 03, se aprecia secciones típicas de alcantarillas tipo marco de concreto con protecciones de entrada y salida.» -- solo marco de concreto
  - *MC_HHD (Lamina Nº 03)*: la lamina misma, pag. impresa 209 (PDF 212), trae TRES figuras y la PRIMERA no es de marco: se titula «ALCANTARILLA TIPO TUBERÍA METÁLICA CORRUGADA». Las otras dos si lo son -- «ALCANTARILLA TIPO MARCO DE CONCRETO» y «ALCANTARILLA TIPO MARCO DE CONCRETO EN CRUCE DE CANAL DE RIEGO» --. El cajetin las cubre a las tres con un titulo que no menciona material: «SECCIONES TÍPICAS DE ALCANTARILLAS»
- **`DIS-MCHHD-T09-A2-DESPLAZADA` — la alineacion de la columna de valores con sus rotulos en el bloque A.2 NO METALICOS de la Tabla Nº 09 (y, con el mismo corrimiento, en los bloques B.1, B.2 y C de la misma pagina).** Gana **MC_HHD (evidencia interna de la pagina)**: es un descuido de composicion: el bloque A.1 de la MISMA tabla no lo tiene, y la lectura corrida es la unica que deja a cada hoja con su valor y a cada rotulo de categoria sin el, como en el A.1. Se sostiene en la pagina y no en otra fuente: la tabla se atribuye a Ven Te Chow (1983), y esa correspondencia -- que la redaccion de S12 invocaba como parte ganadora -- NO es verificable con normas/, donde Chow no esta (auditoria de T-3, H10). HALLAZGO DE S12: el repositorio ya transcribia la lectura corregida y NO lo declaraba, de modo que su valor de Manning mas usado -- MANNING['concreto_tubo_recto'] -- se apoyaba en una lectura corregida que ningun revisor podia reproducir abriendo la pagina
  - Si se sigue la otra: MANNING['concreto_tubo_recto'] pasaria de (0.010, 0.013) a (0.011, 0.014): +10 % en el n minimo, que es el que gobierna V3 y la socavacion, y +7.7 % en el maximo, que gobierna capacidad y tirante; y la fila «afinado» -- la alternativa barrible de 'n_manning_cajon' -- de (0.011, 0.014) a (0.013, 0.017). La lectura literal es MAS conservadora para capacidad (n_max mayor) y menos para V3 y el d50 (n_min mayor): la correccion no es la opcion del lado seguro en las dos ramas, es la lectura que la pagina sostiene
  - *MC_HHD (lectura literal)*: en la pag. impresa 75 los valores del bloque A.2 se imprimen UN RENGLON MAS ARRIBA que sus rotulos: «0.010 0.011 0.013» queda a la altura de «a. Concreto» y «0.010 0.012 0.014» a la de «b. Madera», que son rotulos de categoria sin valores propios -- como «b. Acero» y «c. Metal corrugado» del bloque A.1, que SI quedan en blanco. Leida al pie de la letra, la pagina deja sin valor a «Tubo con moldaje madera en bruto» y a «c. Albañilería de piedra.», que son hojas de la jerarquia
  - *MC_HHD (evidencia interna de la pagina)*: la MISMA pagina, renderizada (impresa 75, PDF 78), trae el bloque A.1 ALINEADO: sus rotulos de categoria «b. Acero» y «c. Metal corrugado» quedan en blanco y cada hoja lleva su terna. En el A.2 es al reves: los rotulos de categoria «a. Concreto» y «b. Madera» llevan terna y la ULTIMA hoja de cada categoria queda en blanco. Corriendo un renglon hacia abajo, las diez ternas del bloque encajan una a una con las diez hojas, sin sobrar ni faltar, y la composicion queda igual que la del A.1. El MISMO corrimiento se repite en los bloques B.1 («a. Acero liso» con terna y «b. Corrugado» en blanco), B.2 («a. Madera», «b. Concreto» y «c. Albañilería» con terna; «Planchas», «excavado en roca descompuesta» y «piedra sola» en blanco) y C. («a. Tierra, recto y uniforme», «b. Tierra, sinuoso», «c. Roca» y «d. Canales sin mantención» con terna; «con algo de vegetación», «fondo pedregoso - malezas.», «irregular» y «Fondo limpio, bordes con vegetación» en blanco). El repositorio no transcribe ni usa ninguna fila de B ni de C (TABLA_09_GRUPO)
- **`DIS-MP-ERRATAS-GAMMA-P` — las erratas de imprenta de la Tabla 2.4.5.3.1-2 del Manual, que la transcripcion conserva tal cual.** Gana **MP**: es la norma peruana vigente y en las filas que este proyecto usa las dos fuentes coinciden digito a digito. Las erratas se COPIAN TAL CUAL, no se arreglan: la fila que la memoria imprime tiene que poder buscarse en el PDF, y si aqui se «corrigieran» las tildes, la nota de erratas estaria atribuyendo al Manual una falta que seria del codigo
  - Si se sigue la otra: ninguno numerico en lo que se usa; la omision de «profundas» SI importa al elegir la fila del TMC, y por eso viaja al criterio 'factores_carga_aashto' y no a esta nota
  - *MP*: «Maximo» SIN tilde en el encabezado de columna, mientras «Mínimo» a su lado la lleva; «EV: Presion vertical de la tierra» sin tilde en «Presion», mientras la fila hermana «EH: Presión Horizontal de la tierra» si la lleva; «Estructuras flexible enterradas», sin la «s» de flexibles; «plancas» por «planchas»
  - *AASHTO_LRFD_9*: su Table 3.4.1-2 escribe «All others» donde el Manual traduce «Entre otros», y «Structural Plate Culverts with DEEP Corrugations» donde el Manual omite «profundas» -- omision SUSTANTIVA, no de imprenta, porque cambia que fila describe a un TMC
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


Citas sin firma de verificación: **6** de 454.
- `AASHTO_M294_TRAD.1.1.1`
- `AASHTO_M294_TRAD.1.4`
- `AASHTO_M294_TRAD.7.2.1`
- `AASHTO_M294_TRAD.7.2.2`
- `AASHTO_M294_TRAD.7.7`
- `HDS5_SI_1985.EC4B#K`

