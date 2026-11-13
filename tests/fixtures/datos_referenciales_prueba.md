> **FIXTURE DE PRUEBA, NO ES UN RESULTADO DEL PROYECTO.** Este archivo vive en
> `tests/fixtures/` y sus valores sirven para ejercitar caminos de codigo en las
> pruebas: ninguno es un dato, un criterio ni un resultado de la obra, y ninguno
> puede citarse en una memoria de calculo (T-12, INF-5.2.4). Los datos de diseño
> del proyecto y quien los aporta estan en `docs/contrato_entradas.md`.

# Datos Referenciales - Vía de Evitamiento La Unión, Bajo Piura
**SOLO PARA PRUEBA INTEGRAL. NINGUNO DE ESTOS VALORES ESTA APLICADO EN EL
CODIGO, y ninguno puede aplicarse a una memoria de calculo: no estan
verificados contra norma ni contra ensayo.**

Son valores de destrabe para una corrida exploratoria: se cargan en caliente
(`establecer_valor_dinamico`) o con `provisional=True`, se mira que puntos
completan diseno, y se revierten.

**REVISADO EN S16 (SIS-F-15).** La frase que ocupaba este lugar --- «los
criterios de `criterios_adoptados.py` siguen en `valor=None` a proposito» ---
era cierta cuando se escribio y hoy NO lo es para dos de las entradas de este
documento: `v_max_hdpe` y `v_max_tmc` ya NO estan vacios. Los cerro la fase de
correccion con una fuente citada (WSDOT Hydraulics Manual M 23-03.12, Cap. 8,
Tabla 8-4, pp. 8-27/8-28), etiqueta `[C]`, y con el valor en SI: **4.572 m/s**
--- los 15 ft/s de la tabla, convertidos, no los 6.0 y 4.5 que este documento
lista. Aplicar encima los numeros de aqui PISARIA un valor ya verificado con
cita, que es exactamente lo que la nota de la version corregida (abajo)
advierte para otras seis entradas.

**REVISADO OTRA VEZ EN S20 (cierre del nivel de PERFIL).** Cuatro entradas
mas dejaron de estar vacias, y esta vez no por una fase de correccion suelta
sino porque el nivel de perfil se cerro entero: `talud_terraplen` (2.0 H:V, no
el 1.5 de aqui: se adopto el extremo mas tendido de la banda, que es el
conservador para la longitud, la caida y G2), `longitud_proteccion_salida`
(5.0 m), `umbral_area_quebrada_importante_ha` (100.0 ha, que SI coincide con
el valor de aqui) y `peso_especifico_relleno_kn_m3` (17.0 kN/m3, no el 18.0
de aqui: se adopto el extremo INFERIOR del rango porque en V7 el relleno pesa
del lado estabilizante). Se les suman tres criterios que en S16 no existian y
hoy tambien estan cerrados: `condicion_pavimento`, `espesor_pared_conducto` y
`acceso_mantenimiento_v2b`. Aplicar encima los numeros de este documento
pisaria valores declarados con su ventana y su procedencia.

Del resto de la lista, lo que sigue vacio hoy: `v_max_concreto_eleccion`,
`pendiente_relleno_trasdos_i`,
`friccion_muro_suelo_delta`,
`metodo_estabilidad_global`,
`TR_evento_extremo`,
`c_phi_fundacion`, `capacidad_portante_adm`, `phi_relleno_trasdos`,
`TW_receptor` y `remanso_derecho_via`. Para
esos, la frase original sigue valiendo y los tests de invariante lo exigen.

(T-7b de la cadena T saco de esta lista dos, y cambio el caracter de otros
cuatro. `inclinacion_muro_beta` vale 0.0 --el trasdos vertical del
predimensionamiento de T-7a-- y `punto_aplicacion_incremento_sismico` vale
0.6 [C] con AASHTO C11.6.5.3: los dos coinciden con el numero de aqui.
`pendiente_relleno_trasdos_i` y `friccion_muro_suelo_delta` siguen sin valor
pero son OPCIONALES: sin declararlos, la pendiente sale de la geometria de
cada cabezal y delta de 0.67·phi; el `20.0` de aqui para delta coincide con
0.67·30. `remanso_derecho_via` ya no es un numero sino el METODO de V5, y
`c_phi_fundacion` pide ademas el peso especifico y si el suelo es cohesivo:
ninguno de los dos se puede aplicar con la forma que este documento trae.)
(T-7a de la cadena T saco de esta lista dos: el angulo de las aletas y el
predimensionamiento del cabezal, que dejaron de ser vacios y son REGLAS [A]
--45 grados, 30 si el esviaje supera 30; y las del predimensionamiento por
punto--, no la geometria unica que este documento traia.)
Y no es una lista arbitraria: **todos son de nivel EXPEDIENTE** salvo
`TW_receptor` y `v_max_concreto_eleccion` --- el primero porque la Sec. 1.3
lo dejo como ultima puerta y ninguna corrida normal lo invoca, el segundo
porque es `opcional=True` y sin declarar V3 aplica el techo normativo.

(La rama `prueba-integral` en que se hizo esta corrida fue renombrada a
`main`; el documento se conserva por sus hallazgos, no como receta a aplicar.)

Versión corregida: se retiraron 6 entradas que ya están cerradas o retiradas en el código real
(factores_carga_aashto, recubrimiento_aashto_mm, peso_especifico_concreto_kn_m3,
procedimiento_flexion_corte_aashto_sec5, FS_flotacion, N_cq_N_gammaq_meyerhof). Aplicar estos
valores encima pisaría trabajo ya verificado con cita.

## 1. Geometría y Geotecnia Básica
*   **v_max_concreto_eleccion**: `3.0` (m/s)
*   ~~**talud_terraplen**: `1.5` (H:V)~~ --- CERRADO en S20 con otro valor: `2.0` H:V, el extremo mas tendido de la ventana (1.5, 2.0), que es el conservador. No aplicar.
*   **pendiente_relleno_trasdos_i**: `0.0` (°)
*   ~~**inclinacion_muro_beta**: `0.0` (°)~~ --- CERRADO en T-7b con ESTE MISMO valor. Ya no hay nada que aplicar.
*   **friccion_muro_suelo_delta**: `20.0` (°)
*   ~~**punto_aplicacion_incremento_sismico**: `0.6` (H)~~ --- CERRADO en T-7b con ESTE MISMO valor, [C], ventana (0.333, 0.6). Ya no hay nada que aplicar.
*   **angulo_aletas**: `45.0` (°)
*   **predimensionamiento_cabezal**: `{'espesor_pantalla': 0.30, 'espesor_zapata': 0.40, 'talon': 0.50, 'puntera': 0.50}` (m)
*   **metodo_estabilidad_global**: `"Bishop_Simplificado"`

## 2. Hidrología e Hidráulica
*   ~~**longitud_proteccion_salida**: `3.0` (m)~~ --- CERRADO en S20: `5.0` m, ventana (3.0, 8.0). No aplicar.
*   **TR_evento_extremo**: `100` (años)
*   ~~**umbral_area_quebrada_importante_ha**: `100.0` (ha)~~ --- CERRADO en S20 con ESTE MISMO valor y ventana (50, 200) ha. Ya no hay nada que aplicar.
*   ~~**v_max_hdpe**: `6.0` (m/s)~~ --- CERRADO en el codigo con otro valor y
    otra fuente: `4.572` m/s [C], WSDOT Tabla 8-4. No aplicar.
*   ~~**v_max_tmc**: `4.5` (m/s)~~ --- idem: `4.572` m/s. Era [C] hasta T-4 y
    es [A] con ventana (3.048, 4.572) desde T-4: la fuente no fija ese valor
    como limite del metal (INF-3.2.4). No aplicar.

## 3. Normas de Producto
*   ~~**clases_producto_por_relleno**: `"Clase_III"`~~ --- CERRADO en T-5 con
    otra forma y otro valor: `{"concreto_reforzado": {"II": 50.0}}` [C], la
    D-load de 0.3 mm de la Clase II de AASHTO M 170M (la unica legible en el
    ejemplar), contra la que la Fase 8 ELIGE la clase por el metodo indirecto
    de AASHTO LRFD 12.10.4.3. Una clase no se declara: se calcula. No aplicar.

## 4. Datos externos (Tablero 3 — no cierran vía código, son de sitio)
*   **c_phi_fundacion**: `{'phi': 28.0, 'c': 0.0}` (SUCS SM)
*   **capacidad_portante_adm**: `80.0` (kPa)
*   **phi_relleno_trasdos**: `30.0` (°)
*   ~~**peso_especifico_relleno_kn_m3**: `18.0`~~ --- CERRADO en S20 con otro valor: `17.0` kN/m3, el extremo INFERIOR de la ventana (17.0, 20.0), que en V7 es el conservador. No aplicar.
*   **TW_receptor**: escenario "salida libre" — TW = cota_fondo_receptor del punto
*   **remanso_derecho_via**: asumir cumple (dentro de derecho de vía) para B-01
*   **Q_receptor / homogeneidad FEN**: no aplica a A-01/A-02/B-01; C-01 sigue bloqueada (correcto)
