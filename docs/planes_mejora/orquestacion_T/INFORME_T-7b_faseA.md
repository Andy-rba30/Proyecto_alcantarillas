# Informe de T-7b (cabezal: ensamble de estabilidad en dos marcos; V5 y V8 con método declarable) — FASE A

Rama `tesis/T-7b`, desde `origin/main` = `250c972`. **No fusionada ni empujada a `main`.** SHA de la rama: `fc792d9`.
No toqué el `.xlsx` del tracker, la tabla de conteos de `CLAUDE.md` ni `verificar_sesion.py`.

## 1. IDs

| ID | Estado que propongo | Por qué |
|---|---|---|
| `INF-4.4` (cargas del cabezal) | **Cerrado**, con un residual declarado | `M9.cargas_del_cabezal`: DC, EV, EH de Coulomb **descompuesto** sobre el plano vertical del talón, LS por h_eq (con su empuje y su peso), WA (hidrostática y subpresión, sin doble cuenta: suelo sumergido + agua aparte), EQ (incremento de Mononobe-Okabe e inercia del muro y del relleno). Cada carga sin factorar, con su brazo y el elemento al que llega. Residual: **el empuje del agua del cauce sobre la cara frontal no se cuenta** (estabiliza; condición crítica = cauce vacío; ficha T7B-03). |
| `INF-4.5` (estabilidad ensamblada) | **Cerrado**, con residuales declarados | `M9.ensamble_estabilidad`: E1 a E3 por cabezal (entrada y salida) y por condición (estática y sísmica), en dos marcos, seis filas cada vez, con su paso de memoria. E4 y E5 impresas como diferidas al expediente con el EMS (T7B-07). Residuales: capacidad portante de terreno horizontal, sin las tablas de talud de AASHTO 10.6.3.1.2c (T7B-04). |
| `INF-5.1.5` (mezcla de marcos) | **Cerrado** | Rige el LRFD de AASHTO 11.6; el ASD de E.050 se calcula en paralelo sobre cargas de servicio y sale al lado; `marco_estabilidad_cabezal` [A] decide cuál rige. Un test recorre las combinaciones y las filas y fija que no se cruzan (ningún factor ≠ 1 en una permanente del marco ASD; ningún φ en una fila ASD; ningún FS en una LRFD). La hoja de ruta lo dice (§Fase 9 y §9.3) y E.050 pasa a [N→]. |
| `INF-4.2` (geometría del cabezal) | **Cerrado** (era «en parte» por la ficha T7A-01) | A-01 llega a la Fase 9 **por `servicio.correr` a `--alcance expediente`** con V5 y V8 declarados, y sus dos cabezales salen con E1 a E3 evaluadas. |
| `INF-4.3` (aleros) | **En parte** (sin cambio de fondo) | El residual de T7A-01 queda cerrado; sigue el del cabezal paralelo a la vía para el marco (ficha T7A-03, diferida a después de T-7c). Verifiqué HDS-5 núm. 5.4.2 contra el PDF y lo escribí en esa ficha. |
| `INF-4.1` (datos por punto) | **Cerrable** — lo decide el orquestador | Los geotécnicos entran por punto (`NF_profundidad_m`, `suelo_fundacion`); los sísmicos son de corredor por diseño. |
| `EXT-7-02` (E6 fuera de las exigidas) | **Cerrado** | La excentricidad sísmica es la fila E2 del marco LRFD sísmico; `gamma_EQ` vale 0.5 [A]. |
| `EXT-7-04` (resultante entera como horizontal) | **Cerrado** | El ensamble la descompone. |
| `EXT-7-03` (Ka de Coulomb entero) | Sin cambio | No tenía nada que cerrar. |
| `EXT-7-01` (ec. 11-32 de E.060) | **NO** | Es del armado (T-7c). El encargo decía «EXT-7-01..04»; el título real de la 01 es de cuantías. |
| «Doble cuenta del agua» | **Cerrado** | No era una ficha EXT-7: era la desviación declarada en `constantes_normativas.HIPOTESIS_EMPUJE_BAJO_NF`. Reescrita. |
| `INF-0.5` (criterios vacíos) | Nota | `remanso_derecho_via` y `TR_evento_extremo` siguen vacíos **a propósito** (decisión del dueño) y ahora tienen método detrás. |
| `T1-03` | En parte | V8 lee `Q_evento_extremo_m3s`; el enlace con la Fase 1-bis sigue diferido. |

## 2. Qué hace (símbolos)

**PUNTO 0.** `M5.v5_remanso(punto, resultado, derecho_de_via=)`: criterio sin valor → `CriterioPendienteError` (como antes); método inválido → `DatoInvalidoError`; sin `ancho_derecho_via_m` → `DatoFaltanteError`; método `perfil_de_remanso_paso_a_paso` → `MetodoNoEvaluableError`; `embalse_a_nivel`: x = HW / S_cauce, **d = (L_boca + x)·cos(esviaje) ≤ ancho / 2**; S_cauce no positiva → `MetodoNoEvaluableError`. `M5.v8_evento_extremo(..., evento=)`: TR → dato Q → dato TW → umbral → cota de entrada + HW(Q_ext) ≤ cota del borde de la plataforma. `servicio._datos_de_expediente` arma los dos; `servicio.CLAVES_DE_V5_Y_V8` (tres claves externas nuevas; `CLAVES_EXTERNAS` = 24) y `suelo_fundacion` en `CLAVES_DE_CABEZAL`; pre-vuelo en `anticipo.datos_faltantes_por_punto`.

**Ensamble (bloque `# --- T-7b ---` de `M9_cabezal.py`).** `datos_del_cabezal_del_punto` → `EntornoDelCabezal`; `geometria_del_relleno`, `angulos_del_empuje`, `cargas_del_cabezal`, `combinaciones_de_estabilidad`, `factores_de_resistencia`, `resistencia_portante_nominal`, `ensamble_estabilidad` → `EstabilidadDelCabezal`; `solicitaciones_por_elemento` (interfaz de T-7c); `integrar_estabilidad`. `servicio._fase_9` corre una etapa por cabezal y condición: lo que no se puede evaluar queda como `Bloqueo` del punto. Salida en CLI (`cli._lineas_cabezal_del_punto`), JSON (`"estabilidad"`) y memoria (`M11._bloque_cabezal`).

**Criterios** (128; 22 sin valor; 6 opcionales). Nueve nuevos al final de su sección: `umbral_no_colapso_evento_extremo` (sin valor), `marco_estabilidad_cabezal`, `fila_phi_estabilidad_cabezal`, `drenaje_trasdos`, `peso_especifico_saturado_relleno_kn_m3` (sin valor, de ensayo), `fraccion_delta_sobre_phi_trasdos` [C], `regla_pendiente_relleno_trasdos`, `factores_inclinacion_carga_portante`, `terreno_delante_del_cabezal`. Reescritos: `remanso_derecho_via` (categoría, sin valor), `gamma_EQ` (0.5), `inclinacion_muro_beta` (0), `punto_aplicacion_incremento_sismico` (0.6 [C]), `pendiente_relleno_trasdos_i` y `friccion_muro_suelo_delta` (opcionales), `c_phi_fundacion` (campos nuevos, sin valor).

**Registro.** 34 citas nuevas (412 → 446), todas verificadas por mí contra el PDF (numeral, título, página impresa y PDF, literal, carácter): AASHTO 11.6.3.2/.3/.5/.6/.7, 10.6.3.4, 10.5.5.2.2, 11.5.7, 11.5.8, C11.5.6, 11.6.5.2.2/.3/.4, 11.6.6, C3.11.5.3, C3.11.5.8.1, 10.6.3.1.1/.2a/.2c; E.050 17.1 y 39.13.8; HDS-5 2.2.5 y 5.4.2. Dos `Interpretacion` nuevas (drenaje; faja simétrica). Doce fundamentos (`F5.V5`, `F5.V8`, diez `F9.*`).

## 3. Tests y par medido

**Par medido de la rama** (PyMuPDF sí · Tk no), suite entera sobre `fc792d9`:

- con `NORMAS_DIR`: **5910 passed / 21 skipped / 5931 collected**, 0 fallos;
- sin `NORMAS_DIR`: **5892 passed / 39 skipped** (los mismos dieciocho saltos más que en la base).

Base `250c972`: 5690 / 19 / 5709. **+222 tests netos.** `skipped` 19 → 21 por diseño (ver §4.4). Las otras tres configuraciones no las medí.

| Archivo | Antes → después | Qué |
|---|---|---|
| `tests/test_t7b_cabezal_estabilidad.py` | 0 → **207** | la aceptación (abajo) |
| `tests/test_decisiones_diferidas.py` | 232 → 244 | los 12 anclajes de T7B-01..12 |
| `tests/test_ext5_forma_gui.py` | 253 → 262 | crece solo con los 9 criterios nuevos |
| `tests/test_familias_del_csv.py` | 20 → 23 | `ancho_derecho_via_m` × 3 familias (2 saltan por diseño) |
| `tests/test_nivel_medido.py` | 10 → 11 | el criterio de la verificación diferida sólo lo lee V8 (por AST) |
| `tests/test_M9_cabezal.py` | 219 → 212 | cuatro vacíos de la Fase 9 dejaron de serlo |
| `tests/test_criterios_adoptados.py` | 161 → 158 | tres criterios menos entre los vacíos |

**La aceptación (207)**: tablas de AASHTO contra su página (4, `pdf`); fichas de los criterios; V5 (dorado a mano, faja estrecha que **no cumple**, umbral inclusivo, cada parada con su excepción, la `Interpretacion` de la faja simétrica); V8; puertas de datos y pre-vuelo; **el ensamble contra dos muros de tanteo calculados a mano** (`CP_T7B_ESTABILIDAD`: cargas, brazos, combinaciones, seis filas estáticas y la condición sísmica; `CP_T7B_MURO_2`: pantalla trapecial, cuña, pendiente y agua parcial), suelo cohesivo, roca, resultante fuera de la zapata, zapata en talud, márgenes, solicitaciones, la peor combinación bajo sismo; **la regla de no cruce**; qué marco decide; el agua una sola vez; lo que detiene y con qué excepción; E4 y E5; el contraste con las cifras del encargo (rotulado); y **trece de punta a punta por `servicio.correr`** (A-01 llega a la Fase 9 con E1 a E3 evaluadas; V5 que falla; sin freático; sísmica no evaluable; CLI, JSON y memoria; perfil; «sin declarar nada, el fixture se detiene donde se detenía»).

**Reescritos declarándolo en el propio test** (sin sumar ni restar salvo lo de la tabla): `test_M9_cabezal` (cuatro ángulos y el brazo sísmico), `test_ext7_cabezal` (la resultante ya se descompone; el censo de funciones sin llamador), `test_t7a_correcciones` (los tres H2: la puerta de `ancho_derecho_via_m` se abrió), `test_M5_verificaciones`, `test_ext6_registro_normativo` (F5.V5 es fundamento, no hueco), `test_memoria_sustentada` (doce fundamentos que la corrida por defecto no alcanza; V5 y V8 salen de `SIN_FUNDAMENTO`), `test_nivel_medido` (`c_phi_fundacion` sale de `SIN_CONSUMIDOR_Y_SIN_MEDIDA`), `test_pf2_prevuelo`, `test_guardias_de_la_suite` (los dos `.md` de fixtures; `gamma_eq` tiene consumidor), `test_sin_literales` (censo de marcas), `test_estilo_criterios` (no: corregí las fichas), `test_criterios_adoptados`, `test_ext5_forma_gui`, `test_ayuda_entrada`, `test_familias_del_csv`, y el generador `tests/apoyo/guia_perfil.py` (una regla para las tres claves nuevas).

**Rojo: no se escribió primero; se midió.** Copiando el archivo y el fixture a un árbol exportado de `250c972` (con un calce para que los tipos que allí no existen queden en `None` y cada test falle por separado): de los 202 tests de ese momento, **186 rojos (112 F + 74 E) y 16 verdes** — 4 literales del PDF, 4 guardias «sin valor de archivo», la guardia «sin declarar nada» y **7 rechazos de dato que allí pasan por la razón equivocada** (la clave no existía y se rechazaba por desconocida). Los 5 tests añadidos después no se remidieron.

## 4. Movido

**Diámetros, secciones, materiales y HW movidos: ninguno.** Línea base regenerada y medida contra `250c972` con `diff` y con el comparador de E-B en los cuatro JSON (27 / 31 / 27 / 3 diferencias, 0 no comparables): los bloques `diseno`, `verificaciones`, `hidraulica`, `geometria`, `estructural`, `proteccion_*`, `socavacion`, `durabilidad` y `caudal` de cada punto son idénticos. `cli_rama_error.txt`, los dos CSV de resumen y `memoria_punto_cajon.html` no cambian un byte.

Lo que **sí** cambia sin declarar nada, y conviene que el auditor lo vea:

1. El **texto** de la ficha de `remanso_derecho_via` donde viaja (ya es el método de V5), las dos huellas y los recuentos (119/25 → 128/22; sin consumidor 8 → 7).
2. **A expediente desaparece un bloqueo del proyecto**: la etapa «K_AE de Mononobe-Okabe (9.2)» de `servicio.correr_cabezal`, que se detenía en `phi_relleno_trasdos`. El K_AE ya no es del proyecto (depende de la pendiente del relleno de cada cabezal). «Etapas bloqueadas» 10 → 9, y `phi_relleno_trasdos` deja de figurar entre los criterios que bloquearon esa corrida (sigue sin valor y bloquea la estabilidad del punto que se dimensione).
3. **El pre-vuelo de expediente anuncia `NF_profundidad_m`** como falta que detiene en los puntos que la traen vacía (el ensamble la lee): `--prevuelo` a expediente sale con 1 donde salía con 0 (ficha T7B-12; un test de `test_pf2_prevuelo` reescrito declarándolo).
4. `skipped` sube de 19 a 21 **por diseño**: `test_familias_del_csv` parametriza (dato × familia) y salta las familias que sí usan el dato; `ancho_derecho_via_m` lo usan A y B.

## 5. Hallazgos que devuelvo (no los tapé)

1. **Con la regla de predimensionamiento de T-7a el cabezal de A-01 no pasa el marco que rige** (datos de prueba: φ relleno 34°, φ_f 32°, γ 18, NF 1.40 m, drenado, k_h 0.25). E3-LRFD estático: 33.95 > 28.86 kN/m (entrada) y 54.07 > 48.57 (salida). E1-LRFD sísmico: 79.3 > 56.1 kPa y 100.2 > 57.9. Igual en A-02 y C-01. Con zapata declarada de 3.00 m las doce filas LRFD cumplen; con 2.40 m el de salida no. No toqué la regla (ficha T7B-09; dos tests lo fijan).
2. **Con el k_h de archivo (0.50, sin reducción) la sísmica no es evaluable**: Mononobe-Okabe exige φ ≥ i + 26.6°, y el relleno sube detrás del cabezal (i ≈ 9–11°). Sale `MetodoNoEvaluableError`, no una cifra (T7B-06).
3. **Con `drenaje_trasdos` de archivo (`sin_drenaje`) ningún cabezal se evalúa** sin dos declaraciones más (peso saturado; y la sísmica queda fuera de dominio).
4. **AASHTO 9.ª ed. 10.6.3.1.2c no trae N_cq / N_γq**: trae tablas de coeficientes de reducción. Las figuras de Meyerhof son las del Manual de Puentes 2016. No transcribí las tablas (T7B-04).
5. **La hoja de ruta §9.3 decía que el cabezal «se apoya en el borde del terraplén»**: con la geometría de T-7a la zapata queda bajo el cauce y el talud sube detrás. Discrepancia declarada en la hoja y en el punto de uso.
6. **A V8 le faltaba más que entradas**: método y umbral. Implementé el mínimo declarable (sin valor de archivo).
7. Un candidato que no conduce el caudal extremo en lámina libre deja el punto en «método no evaluable» aunque otro anterior haya incumplido V5 (regla T4-10): con una faja de 300 m, A-01 termina bloqueado por V8 y el V5 incumplido se lee en la traza (T7B-02).

## 6. Diferidos (símbolo)

T7B-01 `M5.v5_remanso` (perfil de remanso) · T7B-02 `M5.v8_evento_extremo` (desborde admitido, flujo a presión) · T7B-03 `M9.ensamble_estabilidad` (modelo de muro por metro; vano; agua del cauce) · T7B-04 `M9.resistencia_portante_nominal` (talud, forma, profundidad) · T7B-05 `criterios_adoptados::drenaje_trasdos` · T7B-06 `M9.cargas_del_cabezal` (GLE) · T7B-07 `M9.PENDIENTES_E4_E5` · T7B-08 `M9.solicitaciones_por_elemento` · T7B-09 `M9.predimensionar_cabezal` · T7B-10 (aceptación tras el código) · T7B-11 `M9.h_eq_sobrecarga_trasdos` (orientación por punto) · T7B-12 `servicio._verificador_perfil`. Parte L de `docs/decisiones_diferidas.md`; notas de cierre en T7A-01, T7A-03, EXT-7-02, EXT-7-04 y T1-03.

## 7. Filas del tracker a escribir (no las escribí)

`INF-4.4`, `INF-4.5`, `INF-5.1.5`, `INF-4.2` → Cerrado · `INF-4.3` → Cerrado parcial (queda T7A-03) · `INF-4.1` → a decidir · `INF-0.5` → NOTA · filas que nombran V5: `EXT-N-04` → NOTA (el método existe y es declarable; el ancho tiene puerta), `SIS-F-15` → NOTA (los dos `.md` de fixtures actualizados: tres sitios de `AssertionError` menos). Responsable «Claude Code (cadena T, T-7b)». Y la fila de T-7b en `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`, que no añadí porque depende de lo que el tracker escriba.

Censos que cambian y que `CLAUDE.md` nombra (no lo edité): criterios 119 → 128; sin valor 25 → 22; opcionales 4 → 6; sin consumidor 9 → 8 en `SIN_CONSUMIDOR_Y_SIN_MEDIDA`; `CLAVES_EXTERNAS` 21 → 24; citas 412 → 446; marcas `literal-ok` de `dominios.py` 12 → 13 y de `M9_cabezal.py` 6 → 13.

## 8. Preguntas para el dueño

1. **Valor de archivo de `drenaje_trasdos`.** (a) `sin_drenaje` —lo que el encargo dice: la presión sólo se reduce si el drenaje se declara—; (b) `drenado`. *Recomiendo (b)*: AASHTO 11.6.6 y E.050 39.13.8 piden el drenaje, y con (a) ningún cabezal se evalúa sin declarar además el peso saturado, y la sísmica nunca.
2. **El cabezal de la regla de T-7a no pasa.** (a) dejarlo como incumplimiento que el proyectista cierra con `cabezal_declarado` (hoy); (b) subir `fraccion_ancho_zapata` de la regla; (c) iterar B hasta cumplir; (d) dentellón de corte contando el pasivo. *Recomiendo (c)* con paso y techo declarados, después de tener el EMS real: los números de hoy son de prueba.
3. **k_h sin reducción deja la sísmica sin evaluar.** (a) declarar `factor_muro_eleccion` = reducción por desplazamiento (decisión del Propietario); (b) implementar GLE. *Recomiendo (a)* y dejar (b) diferido.
4. **`terreno_delante_del_cabezal` = `horizontal`**, contra el texto de la §9.3. *Recomiendo mantenerlo*: es lo que la geometría de T-7a da.
5. **Fila de φ**: `zapatas_seccion_10` (0.45 / 0.80, de archivo) o `muros_tabla_11_5_7` (0.55 / 1.0). *Recomiendo la de archivo*: la Tabla 11.5.7-1 remite a la Sección 10 para la cimentación del muro y es la menos favorable.
6. **V8**: ¿vale «sin desborde de la plataforma» como única lectura implementada? *Recomiendo sí por ahora*: es la más exigente y no inventa nada.

## 9. Lo que NO hice

- No implementé la progresión de dimensiones del cabezal, el perfil de remanso, el desborde admitido de V8, el flujo a presión con el caudal extremo, GLE, las tablas de talud de 10.6.3.1.2c, la orientación del muro por punto ni el agua del cauce contra la cara frontal.
- No reproduje DC = 7.47 t ni EV = 3.07 t del ejemplo de VARIOS (dependen de una geometría que el encargo no da). Sí Ka, Kp, K_AE (0.4965 contra 0.498), P_A, ΔP_AE, el momento sísmico y EQ, con φ = 26.17° reconstruido de Kp: es un **contraste rotulado**, no un dorado.
- No escribí los tests en rojo primero: el rojo está medido contra `250c972` (abajo).
- No medí las configuraciones con Tk ni sin PyMuPDF.
- No añadí la fila de T-7b en `LO_QUE_ESCRIBIO_CADA_PROMPT` ni toqué el tracker.
- El botón o la pestaña de la GUI para los tres datos nuevos: no; entran por `--datos-externos`.

## 10. Lo que el auditor debería mirar primero

1. **El plano de empuje y EV / EH.** Tomo el plano vertical del extremo del talón (C3.11.5.3) con δ = 0.67·φ sobre ese plano suelo–suelo y Coulomb con la pendiente equivalente del talud quebrado (C3.11.5.8.1, por analogía, regla 2H). Las Figuras C11.5.6-1/-2 rotulan el suelo sobre el talón «1.35 EH» / «1.00 EH» en un caso y «1.00 EV» en la -4: lo leí como EV. Es la lectura en que más dudo.
2. **Los factores mínimos**: 0.90 DC, **1.00 EV** (conflicto #2 de la hoja `Conflictos`: el del muro, no el 0.90 del conducto), 1.50 EH en las **dos** componentes, LS 1.75 sólo como empuje en excentricidad y deslizamiento.
3. **El marco ASD bajo sismo** lleva la sobrecarga viva **entera** (factor 1) y los dos casos del 11.6.5.1; E.050 no dice qué acompaña al sismo. Informa, no decide.
4. **Capacidad portante**: factores de inclinación con cargas **sin factorar**, exponente n = 2 (carga normal al largo), zapata corrida, d_q = 1, interpolación lineal de las tablas; en sismo, las cargas de servicio del mismo caso.
5. **φ de evento extremo**: 0.8 portante / 1.0 deslizamiento (11.5.8); el límite de excentricidad sísmico interpola con γ_EQ.
6. **V5**: qué distancia contra qué ancho (mitad de la faja, `Interpretacion` en `DG2018.304.07.02`), y que el plano horizontal no es la curva de remanso.
7. **El piso del segundo caso sísmico**: «50 % P_AE, no menor que el empuje estático» lo implemento como EH entero e incremento 0.
8. **`combinaciones_de_estabilidad` aplica WA con 1.00** en los dos marcos y `_combinar` cuenta la subpresión como momento volcante.
9. Lo retirado de `servicio.correr_cabezal` (punto 2 de §4).

## 11. Mutación (arnés de EXT-11, `tests/apoyo/mutacion.py`, copias en `SP/T-7b/mut`)

Objetivo: `tests/test_t7b_cabezal_estabilidad.py`. Lo nuevo de M9 (26 funciones, 833 mutantes) y `v5_remanso` / `v8_evento_extremo` (82).

| Medida | M9 | M5 |
|---|---|---|
| **Primera corrida — INVÁLIDA, la descarté** | 100 % | — |
| Primera válida | 525 / 833 (63.0 %) | 64 / 82 (78.0 %) |
| Tras la primera tanda contra los vivos | 687 / 833 (82.5 %) | 78 / 82 (95.1 %) |
| **Final** | **715 / 833 (85.8 %)** | **78 / 82 (95.1 %)** |

La corrida inválida: un test localizaba el bloque de T-7b de M9 por su comentario de cabecera, y el arnés reescribe el módulo con `ast.unparse` (sin comentarios): todo mutante «moría» por eso. Lo anclé por símbolo y comprobé que la aceptación pasa sobre los dos módulos reescritos **sin mutar** antes de volver a medir. La medida final es anterior a los dos últimos tests (cuña saturada; avisos sin repetir).

**Los 118 vivos de M9, clasificados:**
- **29 fronteras a tolerancia** (`<=` por `<`, o el signo de `TOL_UMBRAL_NORMATIVO`) en los umbrales de las seis filas y en las guardias de talón y agua: sólo se distinguen con un muro que caiga exactamente en el umbral. V5 y V8 sí tienen su caso de frontera.
- **32 comparaciones estrictas / no estrictas** sobre magnitudes que sólo valen cero con geometría degenerada (`W_pant > 0`, `B_ef > 0`, `c.N > 0`, `q_R > 0`), el `<` del piso del segundo caso sísmico (iguales sólo en la igualdad exacta), y **cuatro que son huecos reales**: las ramas `fs is None` del marco ASD (momento volcante o empuje nulos: FS infinito, no lo recorre ningún test), y la elección `uso > peor` cuando dos combinaciones empatan.
- **57 de otro tipo**: constantes de guardia `0 → 1` (umbrales de positividad con valores siempre mayores que 1 en los tests), textos de mensaje, la selección de la peor combinación ASD cuando gana la misma por las dos vías, y **6 del factor i_c con φ > 0**, inalcanzables: E.050 Art. 20 pone c = 0 en friccionantes y el término de cohesión se anula.

**Los 4 vivos de M5**: tres `<=` por `<` con tolerancia (equivalentes fuera de la igualdad exacta) y `Q_ext > 0` por `>= 0`, tapado por la guardia siguiente (Q_ext ≥ Q de diseño).
