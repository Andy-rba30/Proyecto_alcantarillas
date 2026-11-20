# INFORME T-10 · FASE A — memoria M11 completa

- Worktree `/home/user/wt/T-10`, rama `tesis/T-10`. Base original `2b13dc1`; **rebasada sobre `origin/main` = `2265d90`** (verificación de T-7) por aviso del orquestador: sin conflictos de código (citas, fichas y README: las dos partes; generados y línea base regenerados).
- Rama tras el rebase: `ab36ef3` (FASE A aplastada), `86c6240` (rebase, generados), `4fb74e9` (sellos con el par medido) y `3f1ee53` (unión `-s ours` con la historia anterior de `origin/tesis/T-10`: el push forzado tras el rebase NO estaba permitido; el árbol de `3f1ee53` es idéntico al de `4fb74e9`). **HEAD = `origin/tesis/T-10` = `3f1ee53a1cea6c0add414f2f0e29bec32ce27c22`. No fusionado ni empujado a `main`.** Al integrar: aplastar sobre `origin/main`.
- Sin cambios de cálculo: ningún número de ningún resultado se mueve (ver §5).

## 1. IDs (canónicos del INFORME)

| ID | Estado | Por qué |
|---|---|---|
| `INF-3.4.7` («La Fase 9 no aparece en la memoria HTML; solo en CLI/JSON») | **entero** | La Fase 9 del punto ya existía desde T-7a/7b (geometría, cargas con brazos y momentos, combinaciones, pasos E y A); T-10 añade lo que faltaba frente al JSON/CLI: tabla de solicitaciones por elemento, excentricidad de cada combinación, **tabla de armado** (secciones críticas: M_u que rige y cedente/reposo, A_s resistencia/mínimos/adoptado, barra, M_r/V_r, fisuración 5.6.7, contraste E.060; y tabla por elemento y posición), los avisos del cabezal (40 de 47 en A-01 faltaban), y la **Fase 9 del PROYECTO** (cadena sísmica eslabón por eslabón con etiqueta/origen/criterio/condición, K_AE, recubrimientos con su paso, cuantías, notas, bloqueos), que solo estaba en CLI/JSON. |
| `INF-4.7` («sección Fase 9 por punto con tabla estática/sísmica, fórmulas sustituidas, FS vs admisibles, geometría») | **entero, con una salvedad** | Todo lo anterior + pasos E-ASD/E-LRFD con φR vs ΣγQ y FS ya emitidos. «Referencia al plano»: el programa no produce planos; no hay a qué remitir. |
| `INF-5.1.10` (el prompt lo llama `INF-5.1.9`) | **entero** | T-0 corrigió la cita; el índice regenerado con una corrida que DIMENSIONA muestra la fila `4.4` («cuál control gobierna») con «num. 3.3.5 … pág. impresa 3.25» y `4.2.1` con su cita. `INF-5.1.9` canónico (`sucs_fundacion`) no se tocó. |

## 2. Tests y par medido

- Archivo nuevo `tests/test_t10_memoria.py`: **33** tests (censo numérico y de textos por clave sobre las dos corridas, avisos en las tres vistas, rótulos de bloqueo, cadena sísmica, armado en tabla, traza de Fase 9 sin repetir, V4b/V6/V9/7.B.3b con la sustitución rehecha a mano, ninguna remisión rota y ningún paso entero dos veces, alcance declarado en tres vistas con su ficha, anexo de sensibilidad, índice y datos de las corridas iguales a los de la guía y a los de T-7c leídos por AST).
- `test_decisiones_diferidas` +7 (fichas T10-01..07); `test_guardias_de_la_suite` −1 (sale del censo `PUBLICAS_SIN_REFERENCIA_EN_TESTS` `M11_reporte.verificaciones_publicadas`, que un test ya nombra). **Neto +39.**
- Reescritos DECLARÁNDOLO (sin sumar ni restar): `test_M5_verificaciones` (V4b tiene paso y la nota de §15.6.3 en la Familia C —el test decía «el día que V4b tenga fundamento, este test cae»—), `test_memoria_sustentada` (censo `SIN_FUNDAMENTO` vacío; la máquina del hueco se prueba con una entrada de prueba), `test_traza_punto` (ningún hueco emitido; V4b llega como paso), `test_indice_formulas` (dos corridas; el chequeo de valores solo sobre magnitudes con unidad, con la razón), `test_t6_geometria` (7.B.3b entre 7.B.3 y 7.B.4; selección por código), `test_dimensional_piloto` (conserva SU corrida, la antigua del índice; relación de V4b), `test_ext8_rendimiento_gui` (techos remedidos, §4).
- **Par MEDIDO «PyMuPDF sí · Tk no», con `NORMAS_DIR`, sobre la rama rebasada (árbol `86c6240`, el de `4fb74e9`/`3f1ee53` salvo los sellos): 6326 passed / 23 skipped / 6349 collected** (+39 netos sobre `2265d90`: 6287/23/6310; antes del rebase, 6292/23/6315 sobre `2b13dc1`). Sin `NORMAS_DIR`: no medido en esta FASE A (derivado: 18 menos y 18 más saltos, como en la base). Otras configuraciones: no medidas (sin tkinter).
- **Rojo**: no escrito en rojo con `xfail` (el censo tenía que medirse antes de saber qué fijar). Medido con el archivo final contra un árbol de `2265d90` (y antes contra `2b13dc1`, igual): la colección falla (no existe `modelos.ALCANCE_DECLARADO`); con ese import tolerado, **31 de 33 rojos** (6 failed, 25 errors) y 2 verdes que valen antes y después (`test_todo_A_con_valor_tiene_ventana`, autocomprobación del censo de textos).

## 3. El CENSO de lo que faltaba en la memoria, y cómo quedó

Método: las dos corridas de referencia nuevas (abajo); para cada punto dimensionado, toda hoja numérica del JSON buscada en su bloque HTML (formatos 2/3/4 decimales y enteros) y toda hoja de texto; avisos por punto en las tres vistas. Antes de T-10:

| Fase / bloque | Faltaba en el HTML (base) | Cómo quedó |
|---|---|---|
| Fase 9 del punto — armado | `secciones[]` A_s resistencia/mínimos/adoptado, recubrimiento, f_ss, contraste E.060, M_u reposo; `tabla[]` A_s y Ø de barra | tablas `_bloque_armado` (M11) con los números de `ArmadoDelCabezal` |
| Fase 9 del punto — estabilidad | `solicitaciones[]` V_u y M_u (39-42 de 48), `combinaciones[].excentricidad` | tabla `_tabla_solicitaciones`; columna `e` (propiedad de `CombinacionDeEstabilidad`, no aritmética de M11) |
| Fase 9 del proyecto | toda: cadena sísmica, K_AE/K_A, recubrimientos, cuantías, notas | `bloque_cabezal_proyecto`, detrás de los puntos |
| Avisos del punto | 40/47 en A-01 (expediente), 2/34 en perfil (embocadura de B-01) | `_avisos_que_faltan`: los de `InformePunto.avisos()` que la fase no imprimió, una vez |
| Fase 7 | `proyeccion_taludes`, `altura_terraplen_salida`, semilongitudes | paso **7.B.3b** emitido por M7 (`LongitudConducto.paso_reparto`), solo en la geometría del punto que llega a 7.B |
| Fase 7 | `cota_entrada_origen.nota` (texto del adaptador) | `CotaDeEntrada.nota` (modelos): una fuente, JSON y memoria |
| Fase 5 | V4b, V6, V9 como hueco censado («frase suelta») | pasos con fórmula sustituida (§6) |
| Datos | `cota_fondo_entrada`, `cota_coronacion_canal` (pendientes del JSON sin fila) | dos filas en `CAMPOS_CSV` |
| Fases 3-5 | `alcance_norma_producto`, `tipo` del material | fila y código en la tabla del diseño |
| Fase 2 | `TR_numeral` cuando el TR no procede (C-01) | se imprime al lado |
| Fase 6 | `filtro.citas` | citas del filtro con su numeral y enlace al anexo |
| Fase 10 | `aporte_alivio.origen_aporte` | en el párrafo de la Fase 10 |
| Embocadura (perfil) | regla, criterios, coherencia del marco | línea «Embocadura del punto» del punto dimensionado sin cabezal |
| Anexo | 17 anclas rotas (pasos de Fase 8 y 10 que el anexo no escribía; T-5/T-9) | `pasos_impresos` los incluye |

Queda censado con razón (`TEXTOS_CON_OTRA_VISTA`, 3 claves): `bloqueos[].mensaje` (se imprimen sus partes), `verificaciones[].fase` (rótulo de agrupación), `filtro.citas[]` (se imprime el numeral; el test lo comprueba). **Números: ninguno pendiente.**

Además: **alcance declarado** del dueño (`modelos.ALCANCE_DECLARADO`: armado de la sección del marco T5-07, cabezal paralelo T7A-03, iteración del ancho de zapata T7B-09, V7 del marco sin DC T3-08, Figuras 3.3-3.4 de HEC-14 T8-08) en CLI, JSON (`alcance.declarado`) y memoria; **rótulo legible por tipo de bloqueo** («espera un dato», «método no evaluable»…; `ROTULO_TIPO_DE_BLOQUEO`); **anexo A.4** de criterios [A] usados con valor efectivo, ventana, modo de resolución y puntos que lo nombran (`anexo_sensibilidad`, `criterios_A_por_punto`; no recalcula; todo [A] con valor ya tenía ventana).

## 4. Tamaño (método de `test_ext8`: marginal 4 vs 1 punto, expediente, entradas ampliadas, declaraciones de la suite)

| | KB/punto | páginas/punto | 1 punto | 4 puntos |
|---|---|---|---|---|
| base `2265d90` (= `2b13dc1`) | 113.99 | 32.33 | 104 pág | 201 pág |
| T-10 | **107.04** | **31.00** | 118 pág | 211 pág |
| perfil (sin techo) | 149.96 → 141.04 | — | | |

Techos remedidos y pegados: `KB_POR_PUNTO_MAX` 114.5 → 107.5; `PAGINAS_POR_PUNTO_MAX` 33 → 31.5. Por fase (A-01 a expediente con Fase 9 entera): bloque del punto 721 → 612 KB (desarrollo de verificaciones ~340 KB, traza Fase 9 257 → 96 KB). Deduplicación: (1) pasos del armado impresos dos veces (161 KB en A-01) → la traza remite; (2) primera aparición en el documento (`M11._YaImpreso`): paso, elección o nota idénticos salen una vez con ancla y luego como línea + enlace (fuera del documento, enteros). El objetivo de EXT-8 (< 15 KB / 10 pág) **no es alcanzable sin perder sustento**: ficha T10-01.

## 5. Movidos

**Diámetros, secciones, materiales y HW movidos: ninguno.** Línea base regenerada sobre el árbol rebasado; comparador de E-B contra `2265d90`: `informe_expediente` e `informe_rama_error` IGUALES; `informe_familia_c` 8 y `informe_perfil_ancho` 6 diferencias, todas `V4b/V6/V9.veredicto` `None → 'cumple'` (FORMATO: el `cumple` ya era `true`; el veredicto viene ahora del paso); 0 no comparables. `memoria_punto_cajon.html` y los dos CSV de resumen idénticos byte a byte; `cli_*.txt` +6 líneas (alcance declarado); memorias: formato. Las corridas del censo contra `2265d90`: mismas diferencias de veredicto, mismos materiales, secciones y HW (A-01/A-02/B-01 Ø 0.90 concreto; C-01 marco 1.20 × 0.90; HW idénticos).

## 6. Otros cambios con su razón

- **V4b, V6, V9 ganan paso** (ficha T10-03): `F5.V4b` DEFINE con cita NUEVA `HDS5_3ED.2.2.5d#AGENCIAS` (verificada en el PDF: pág. impresa 2.10, PDF 72, item d. «Agency Constraints», «The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5.», carácter DEFINICIÓN); umbral [A] `HW_D_max`; nota de §15.6.3 en la Familia C. `F5.V6` RECOMIENDA (`MC_HHD.4.1.1.3.4a#MULTIPLES`). `F5.V9` DEFINE; juzga contra M 170M 7.2.1 / M 36 Table 6 / M 294 trad. 7.2.1 cuando el tope sale de la norma; con `D_max_catalogo` [A] o el marco, **sustituye y no juzga** (sin umbral ni veredicto, NOR-PRO-01/02). `SIN_FUNDAMENTO` queda vacío. Entradas V4b/V6/V9 en `UMBRALES_DE_VERIFICACION` (como V10).
- **Índice de fórmulas** (ficha T10-02): dos corridas de PRUEBA ya existentes, copiadas a `tests/fixtures/corridas_de_referencia/` y comprobadas iguales a la guía y al AST de `test_t7c` — `perfil_guia` (4 dimensionados, B-01 con TW 0.30) y `expediente_cabezal` (A-01 con Fase 9 y armado). 159 → 476 pasos, 28 → 197 fórmulas, 19 → 79 de 122 fundamentos. El índice enmascara los valores que un módulo escribe dentro de una procedencia («= número», número con unidad).
- Ficha EXT-9-03: su ancla `corrida_de_referencia` pasa a `correr_referencia`.

## 7. Diferidos (símbolo)

T10-01 `M11_reporte._YaImpreso` (objetivo de tamaño) · T10-02 `indice_formulas.CORRIDAS_DE_REFERENCIA` (hidrología calculada fuera del índice) · T10-03 `fundamentos.SIN_FUNDAMENTO` (V9 sin juicio con tope de catálogo/marco) · T10-04 `M11_reporte.bloque_cabezal_proyecto` (tres textos con otra vista) · T10-05 `modelos.ALCANCE_DECLARADO` · T10-06 `M11_reporte.anexo_sensibilidad` (el barrido sigue siendo PF-3) · T10-07 (rojo medido). Parte «LII (provisional)» de `docs/decisiones_diferidas.md`: renumerar al integrar.

## 8. Filas del tracker (para la integración)

| ID | Estado | Responsable | Nota |
|---|---|---|---|
| `INF-3.4.7` | Cerrado | Claude Code (cadena T, T-10) | Fase 9 del punto y del proyecto en la memoria HTML con tablas y pasos; censo JSON↔HTML por clave (`tests/test_t10_memoria.py`) |
| `INF-4.7` | Cerrado | Claude Code (cadena T, T-10) | Tabla estática/sísmica, solicitaciones, armado en tabla, FS/φR vs ΣγQ por paso; sin «referencia al plano»: el programa no produce planos |
| `INF-5.1.10` | Cerrado | Claude Code (cadena T, T-10) | Índice regenerado con corridas que dimensionan: la fila 4.4 cita HDS-5 3.3.5 |

## 9. Preguntas para el dueño

1. **Tamaño**: ¿se aceptan los techos remedidos (107 KB y 31 pág por punto en la corrida de la línea base; un punto con Fase 9 armada pesa ~610 KB) o se quiere una memoria impresa resumida (tablas por punto) con el desarrollo completo como anexo digital? Recomiendo **aceptar ahora** y decidir el formato impreso en T-12.
2. **V9 sin juicio** cuando el tope es de catálogo [A] o la progresión del marco: ¿conforme? Recomiendo **sí** (no hay numeral que citar).
3. ¿Una tercera corrida de referencia con la hidrología de prueba para que la Fase 1-bis calculada aparezca en el índice? Recomiendo hacerlo en **T-11**.

## 10. Lo que NO hice

- No pude empujar con `--force-with-lease` tras el rebase (lo denegó el permiso de la sesión): uní la historia anterior con `merge -s ours` para que el push fuera de avance rápido; el árbol no cambia.
- `Verificacion.avisos` (nuevo en `2265d90`): no hizo falta tocar nada; llega por `InformePunto.avisos()` y `_avisos_que_faltan` lo imprime si su fase no lo hizo (el test de avisos en tres vistas lo cubre).

- No escribí la aceptación en rojo antes del código (rojo medido contra la base: 31/33).
- No toqué la GUI. No medí sin `NORMAS_DIR` ni las configuraciones con Tk o sin PyMuPDF.
- No escribí el tracker, la tabla de CLAUDE.md, `verificar_sesion.py` ni `LO_QUE_ESCRIBIO_CADA_PROMPT` (integración).
- No toqué fórmulas de M9. M5 y M7 solo EMITEN pasos de lo que ya calculaban (V4b/V6/V9, 7.B.3b); `v4b_relacion_hw_d` recibe `punto` opcional para la nota de §15.6.3.
- La cadena sísmica se imprime como tabla de eslabones (`PasoSismico`), no como `PasoDeMemoria`.
- No corrí mutación.
