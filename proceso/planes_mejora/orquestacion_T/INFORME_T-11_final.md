# INFORME FINAL · T-11 (validación integral de las tres familias) — correcciones de la auditoría e integración en `main`

- **Commit en `origin/main`: `f77c5d4` (`f77c5d47c635e70eb1883204175615fa8aad2dfd`** (fast-forward desde `14f6138`; `origin/main == HEAD` confirmado tras `git fetch`;
  `tesis/T-11` empujada en el mismo commit). Un solo commit `tesis(T-11): …` que aplasta la FASE A (`c774035`), la corrección
  de T11-03 (`10fb84b`) y estas correcciones.
- **T-11 VALIDA y no cambia cálculo.** **Diámetros / secciones / materiales / HW que gobierna movidos: ninguno** (medido clave a
  clave y con el comparador de E-B contra `14f6138`; §5). Lo único aprobado que toca un HW publicado es H9: la clave
  `HW_salida_m` de A-02 pasa a `null` donde el perfil descartó la aproximación (decisión del dueño, condición cumplida: el HW
  que gobierna, `HW_entrada_m`, diámetros, secciones y materiales no cambian).

## 1. Hallazgos de la auditoría, uno por uno

| H | Sev. | Resultado | Qué se hizo (ancla) |
|---|---|---|---|
| H1 | ALTA | **cerrado** | `validacion_integral.quitar_una_en_la_titular` + `lista_exacta(…, una_titular)`: la lista se mide sobre DOS bases (el juego y el juego con las decisiones de archivo) y se une. `peso_especifico_saturado_relleno_kn_m3` entra a la §7 del contrato (detiene 24 etapas con `sin_drenaje`); `CONDICIONALES_NO_MEDIDAS` (11, incl. `h_eq_banda_intermedia_borde`, `h_eq_bajo_altura_tabulada`, `N_cq_N_gammaq_meyerhof`, `q_n_kpa` en roca) nombradas en la §7; «lo que no está aquí no detiene nada» sustituido por «además de las columnas obligatorias… salvo las condicionales no medidas»; la §7 ya no contradice a la §3.3. El test fija el mínimo nuevo y que el γ saturado sólo sale de la segunda base. |
| H2 | MEDIA | **cerrado** | §2 de `docs/validacion_integral.md` = corrida TITULAR (variante nueva `decisiones_de_archivo`, con el γ saturado de prueba 20 kN/m³ declarado por `--declarar` y su línea de plausibilidad): las tres filas estáticas LRFD no pasan en 8/8 cabezales y la sísmica es «método no evaluable» (8 bloqueos T7B-05). Tabla generada con las claves de `J.DECLARACIONES` que pisan archivo (`J.PISA_EL_ARCHIVO_PORQUE`, con un test que exige igualdad). El juego queda como §2.1 «variante que ejercita la cadena sísmica y el caso drenado». El anexo §1 dice que los barridos son sobre el juego y por qué. `J.DECLARACIONES` no se tocó. |
| H3 | MEDIA | **cerrado** | `sensibilidad.BARRIDOS` = `BARRIDOS_A_MANO` + `barribles_del_censo()` (todo criterio con valor efectivo y ventana legible por máquina): 82 barridos sobre 80 criterios; los 61 restantes en `NO_BARRIBLES` POR NOMBRE con su razón; test de partición exacta. Incluidos los quince del auditor (y `espesor_pared_cajon` a mano, 0.20/0.25/0.30). `n_manning_cajon`: dicho que el lado alto (HDS-5 B.3) no se midió porque la puerta rechaza el par (forma `str`; verificado: `ValueError`) → ficha T11-10. «LEÍDO, SIN EFECTO MEDIBLE» redefinido en §1; HW con `TOL_HW_SENSIBILIDAD_M` (5e-5 m), no `!=`. `predimensionamiento_cabezal`: dicho que `fraccion_ancho_zapata` = 0.7 ya es el techo. Recuentos rehechos: **mueven el diseño 10 criterios (11 barridos)**, 25 veredictos, 2 sólo HW, 28 leídos sin efecto, 16 no leídos (anexo, ficha T11-05, test). |
| H4 | MEDIA | (hecho por T11-03) | Sigue verde (29 tests de `test_t11_no_factible_por_rasante.py`). |
| H5 | MEDIA | **cerrado** | `docs/validacion_hy8.md` y `TOLERANCIA_HY8_*`: «criterio del proyecto (aceptado por el dueño el 2026-11-13), NO normativo», coherente con el 3 % de lectura; HW y HW/D (columna nueva; D = altura interior: tubo o celda); control distinto → «explicar» (`juicio_hy8`); velocidad con columna «cómo sale / ¿lleva veredicto?» (no en A-01, A-02, B-01 —V_erosión de doble n, V·A ≠ Q por diseño—; sí en C-01, Q/A(y_c)); versión y fecha de HY-8 obligatorias en el encabezado de cada tabla de §6. Ejecutable: Roadway Data (cota de cresta = `cota_rasante`, ancho = plataforma, sin desborde), el n del tirante normal (n máx.), y la diferencia de longitud por punto (B-01: 0.0050 %). El test deja de ser tautológico: seis tests fijan las cinco reglas y la ejecutabilidad. |
| H6 | MEDIA | **cerrado** | Anexo §3.2: el criterio se queda SIN valor (decisión del dueño), rige 6.0 m/s; con 3.0 m/s A-01 → TMC Ø 1.20 (resultado de la tesis que no cambia el fixture), y medido como barrido combinado (base `juego_tmc_excluida`) y como variante (`v_max_concreto_3_con_tmc_excluida`): con `excluye`, A-01 se detiene en `perfil_hdpe_fabricante`. `sulfatos_suelo_ppm: 500` NO cambiado; su línea corregida: insignificante para el concreto (**E.060 Tabla 4.4, pág. impresa 38 / PDF 38: «Insignificante 0,0 ≤ SO4 < 0,1 · 0 ≤ SO4 < 150 · — — —»**, verificado), agresivo para el acero galvanizado (**AASHTO LRFD 9.ª, 11.10.6.4.2a, pág. impresa 11-89 / PDF 1558: «Sulfates ≤ 200 ppm»**, verificado). |
| H7 | MEDIA | **cerrado** | TW de C-01 = 0.41 m por punto (tirante normal del canal del juego, dorado a mano en la línea y en un test). Medido: sección igual, HW 0.62307 m (antes 0.62299: cuarta cifra). Variante `C01_fondo_en_el_canal` con **36.30 msnm** (no 36.284 del auditor: con ésa la salida quedaba 11 mm BAJO el canal y VC2 seguía avisando): VC2 y G2 cumplen, el remanso concluye, marco y HW iguales; la longitud 21.00 → 23.79 m y el cabezal, más alto, cambia veredictos de estabilidad (se dice). Frase del §2.1 generada con lo medido. La tercera corrida del índice se regeneró con el TW nuevo. |
| H8 | BAJA | **cerrado** | `M11.tipo_cabezal_del_punto` (embocadura del punto y tipo de sus cabezales); `fila_resumen(informe)` y `_fila_resumen_csv(informe)` sin el parámetro; `exportar_csv` sin `ruta_hoja`. Plomería de reporte, sin aritmética. Mueve por texto los dos CSV de resumen y la celda en las tres memorias (declarado en el README). |
| H9 | BAJA | **cerrado** (decisión del dueño) | `cli.salida_no_se_forma`; `HW_salida_m: null` en la condición exacta; línea «Control» con «salida no se forma: el perfil no alcanza la entrada». Lectores revisados: comparador (lo lee como diferencia, no «no comparable»; test), barrido PF-3 (lee `HW_gobernante_m`), CSV de resumen (no lo lee), GUI (no lo lee), `tests/apoyo/validacion_externa` (actualizado), tests. Línea base: sólo esa clave (A-02, dos JSON) y esa línea (dos `cli_*.txt`). |
| H10 | BAJA | **cerrado** | `M9._fila_de_durabilidad_no_aplica`: A7 con `NO_APLICA` y razón; ningún veredicto ni número cambia; dorados de T-7c intactos (586 tests de cabezal verdes sin tocarlos). |
| H11 | BAJA | **cerrado** | Columna «Consumidor» en el §6 (derivada de `variables_entrada`); `TW_receptor` como «dato del receptor (ANA / Junta)» y descrito como el código lo hace (se corrigió el docstring FALSO de `servicio._resolver_tw`, que decía que mandaba sobre las vías 3 y 4); `SIN_CONSUMIDOR_Y_SIN_MEDIDA` medido = 7 (test) y el «ocho» de `CLAUDE.md` y el «nueve» de `test_nivel_medido` corregidos. |
| H12 | BAJA | **cerrado** | Docstring del juego (sí se versionan los de la tercera corrida) + `LEEME.md` rotulado en `hidrologia_calculada/`; docstring de `src/indice_formulas.py` (la tercera corrida trae datos nuevos); leyenda del §4 con NO FACTIBLE; porcentajes con dos decimales y causas de `CP_HDS5_DG1` a dos decimales (test que exige que coincidan); `TOL_FRONTERA_DE_BANDA` (el −1 % del apron caía fuera por 1e-17: `CENSO_HEC14` queda vacío y la explicación pasa a la nota del ejemplo); fichas T11-03/04/05 al día (19 cifras de HEC-14, no 17). |
| H13 | BAJA | **cerrado** | La CLI real comprueba el ancla de cada punto; el CSV copia se compara celda a celda; la ventana de cada barrido se comprueba; `lento` sólo en el test que lanza un subproceso (convención del `conftest`). |
| H14 | BAJA | **cerrado** | Línea del Q extremo y frase medida en el §2.1 (`sensibilidad_q_extremo_A01`: con 1.5 y 1.71 veces sigue Ø 0.90; con 1.8 y 2.0 pasa a Ø 1.05 por V8); la cadena «caudal calculado → diseño» dicha como NO validada (cocientes medidos: 19 a 47 veces), con la propuesta del juego coherente para el lote posterior. |

## 2. IDs canónicos del tracker (responsable «Claude Code (cadena T, T-11)»)

- `INF-0.5` → **Cerrado CON SALVEDAD** escrita en la fila (a expediente siguen deteniendo, por decisión del dueño,
  `remanso_derecho_via`, `TR_evento_extremo`, `umbral_no_colapso_evento_extremo` y `categoria_refuerzo_aashto`).
- `INF-3.4.3` → **Cerrado** (T-7b; verificado por T-11). `INF-3.4.6` → **Cerrado** con NOTA (T7B-05).
- `INF-3.4.4` → **Cerrado parcial** (residual: E4/E5 sin evaluar —T7B-07—, Meyerhof en talud vacío, zapata sin iterar —T7B-09—).
- NOTAS (sin cambio de estado): `INF-3.2.2` (validación generada; HY-8 con la tolerancia aceptada) e `INF-5.1.8` (estado real).
- Fila de T-11 en `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`.

## 3. Tests y pares

| Archivo | Tests | Origen |
|---|---|---|
| `tests/test_t11_validacion_integral.py` | 31 | FASE A 25 (el xfail liberado por T11-03) + 6 de las correcciones |
| `tests/test_t11_validacion_externa.py` | 20 (5 `pdf`) | FASE A 12 + 8 de las correcciones |
| `tests/test_t11_sensibilidad.py` | 9 | FASE A 6 + 3 |
| `tests/test_t11_no_factible_por_rasante.py` | 29 | T11-03 |
| `tests/test_t11_correcciones.py` | 10 | correcciones (H8, H9, H10) |
| `tests/test_decisiones_diferidas.py` | +10 anclajes | T11-01..10 |

**+109 netos: collected 6360 → 6469.** `-m pdf`: 145 → **150**. Rojo de las correcciones medido con los cuatro archivos finales
contra `10fb84b`: **28 fallos y 4 errores de 70** (los 38 verdes son guardias y comportamiento previo).

**Par MEDIDO sobre el commit integrado** («PyMuPDF sí · Tk no»): con `NORMAS_DIR` **6446 passed, 23 skipped → collected 6469**; sin `NORMAS_DIR` **6423 passed, 46 skipped → collected 6469**. El par se midió sobre `64e9f28` (el árbol aplastado antes de escribir los dos sellos con ese par); `f77c5d4` sólo difiere en las líneas de sello de `docs/trazabilidad.csv` y `docs/indice_formulas.md`, y se remidió entero con `NORMAS_DIR` sobre `origin/main` (resultado al pie, §10).
Las otras tres configuraciones, DERIVADAS (no medidas; el contenedor no tiene tkinter): sí·sí 6459/10, no·sí 6310/159,
no·no 6297/172. Techos de `test_ext8` remedidos: 107.05 KB y 30.3 páginas por punto (techos 107.5 y 31.5: no se mueven).
Censos sin mover: 141 criterios, 20 sin valor, 507 citas, ningún fundamento ni marca `literal-ok` nueva.

## 4. Lo que cambió en el programa (todo de diagnóstico, formato o transparencia)

`src/modulos/MD.py` (T11-03), `src/modulos/M5_verificaciones.py` (docstring, T11-03), `src/modelos.py` (alcance declarado +2,
`EscalonSinCabida`), `cli.py` (H9), `src/modulos/M9_cabezal.py` (H10), `src/modulos/M11_reporte.py` (H8), `src/servicio.py`
(docstring de `_resolver_tw`), `src/indice_formulas.py` (tercera corrida, docstring). La v8 lleva la nota «Corregido (T11-03)».

## 5. Línea base (medida contra `14f6138`, README de la carpeta)

Comparador de E-B: `informe_expediente.json` e `informe_rama_error.json` IGUALES; `informe_perfil_ancho.json` e
`informe_familia_c.json` 4 diferencias / 0 no comparables (`[A-02] HW_salida_m` → null por H9; mensaje y dos motivos de B-01 por
T11-03). Texto: alcance declarado (+2 líneas) en los cinco `cli_*.txt` y las tres memorias (FASE A); mensajes «no factible por
rasante» (T11-03); línea «Control» de A-02 (H9); tipo de cabezal del cuadro resumen en los dos CSV y las tres memorias (H8);
huella de la v8 en las memorias (T11-03). Clave a clave en los cuatro JSON: material, sección, `HW_gobernante_m`,
`HW_entrada_m`, control, Q, V_erosión e y_normal idénticos. **Diámetros, secciones, materiales y HW que gobierna movidos: ninguno.**

## 6. Diferidos con símbolo (Parte LIV de `docs/decisiones_diferidas.md`, la siguiente libre)

T11-01 `juego_validacion_integral.py::OMITIDAS_A_PROPOSITO` · T11-02 `validacion_integral.py::lista_exacta` · T11-03
`MD.py::_resumen_por_rasante` (cerrada en parte; abiertos 3 y 4 son decisión del dueño) · T11-04 `validacion_externa.py::juicio_hy8`
· T11-05 `sensibilidad.py::BARRIDOS` · T11-06 `indice_formulas.py::CORRIDAS_DE_REFERENCIA` · T11-07 `modelos.py::ALCANCE_DECLARADO`
· T11-08 (rojo no primero) · **T11-09** `cli.py::salida_no_se_forma` (la fila «Control gobernante» de la MEMORIA sigue imprimiendo
la aproximación descartada: el dueño limitó H9 al JSON y la CLI) · **T11-10** `criterios_adoptados.py::n_manning_cajon` (el lado
alto de la ventana no se puede declarar: la ficha promete el par y la forma es `str`).

## 7. Preguntas para el dueño (con recomendación)

1. **T11-09**: ¿llevar «salida no se forma» también a la fila «Control gobernante» de la memoria? Mueve texto de las memorias de
   la línea base. *Recomendación:* sí, en T-12 o en el lote posterior, con la misma condición de `cli.salida_no_se_forma`.
2. **T11-10** (`n_manning_cajon`): ¿abrir la forma a la unión fila / par (con la guardia de la Tabla B.1 en
   `M2._fila_manning_de_cajon`) o corregir la ficha para que no prometa el par? *Recomendación:* abrir la forma (B.3 es el lado
   seguro del HW para un cajón vaciado in situ), en el lote posterior; es cambio de criterio, no de T-11.
3. **T11-03, abiertos 3 y 4** (del agente de T11-03, no aplicados): bloquear también cuando un candidato cierra y uno anterior
   tenía un dato inválido; sacar como dato inválido el diámetro de arranque negativo de la rama de error. *Recomendación:* el 3
   sí (mismo criterio que T4-10 para el dato que falta); el 4 sí, aceptando que cambia el tipo de bloqueo de la rama de error.
4. **HY-8, velocidad con veredicto** (C-01, control de salida, Q/A(y_c)): T-11 la juzga con las mismas bandas que HW (lectura
   de T-11; la decisión nombra HW y HW/D). *Recomendación:* confirmarlo.
5. Los datos de prueba del evento extremo (1.11 × Q de diseño) no se sostienen como cociente típico y gobiernan la llegada de
   A-01 (desde 1.8 × pasa a Ø 1.05 por V8): para la tesis, usar el estudio hidrológico real.

## 8. Lo que NO hice

- No corrí HY-8 ni afirmo resultados suyos. No medí las configuraciones con Tk ni sin PyMuPDF (derivadas).
- No apliqué los abiertos 3 y 4 de T11-03 ni llevé H9 a la memoria (fuera de la decisión del dueño).
- No cambié la forma de `n_manning_cajon` (sería cambio de criterio): ficha T11-10.
- No toqué `verificar_sesion.py`.

## 9. Lo que T-12 debe saber

- **Cuatro documentos generados nuevos** (`docs/validacion_integral.md`, `validacion_hds5.md`, `validacion_hy8.md`,
  `validacion_sensibilidad.md`), sin sello y con test de sincronía; se regeneran con `python -m tests.apoyo.validacion_integral
  --escribir` (escribe también la tercera corrida del índice y su `LEEME.md`), `python -m tests.apoyo.validacion_externa
  --escribir` y `python -m tests.apoyo.sensibilidad --escribir`. Son del ENTREGABLE (PRECISIONES_T-12: no se mueven). Cualquier
  cambio del juego, de un criterio o de la memoria los desincroniza: regenerar y mirar el diff.
- **`tests/test_t11_sensibilidad.py` parte el censo de criterios**: un criterio NUEVO tiene que ser barrible (y entonces cambia
  el anexo y `test_los_juicios_del_anexo`) o figurar en `sensibilidad.NO_BARRIBLES` con su razón. La fixture `medidas` corre
  ~200 corridas en proceso (~60 s); no lleva `lento` (la convención lo reserva a subprocesos).
- **`tests/test_t11_validacion_integral.py`**: `J.PISA_EL_ARCHIVO_PORQUE` tiene que nombrar EXACTAMENTE las claves de
  `J.DECLARACIONES` cuyo criterio tiene valor de archivo; la §7 del contrato tiene que nombrar la lista medida Y las
  `CONDICIONALES_NO_MEDIDAS`; `SIN_CONSUMIDOR_Y_SIN_MEDIDA` = 7.
- **HEC-14 vive sólo en el repositorio de normas**: los cinco `pdf` de `test_t11_validacion_externa.py` saltan sin `NORMAS_DIR`
  (por eso son 23 y no 18 los saltos sin él). Si T-12 retira `normas/` de la app, recontar.
- **Firmas cambiadas**: `M11.fila_resumen(informe)`, `M11._fila_resumen_csv(informe)`, `M11.exportar_csv(informe, destino)`
  (sin `ruta_hoja`); nuevas `M11.tipo_cabezal_del_punto`, `cli.salida_no_se_forma`, `M9._fila_de_durabilidad_no_aplica`.
- **La memoria «resumida» (si entra en T-12)**: la columna «Tipo de cabezal» ya es del punto; `HW_salida_m` puede ser `null`
  en el JSON; la fila «Control gobernante» de la memoria todavía imprime la aproximación descartada (T11-09).
- **Riesgos de integración heredados de T11-03**: cualquier edición de la v8 mueve la huella de las memorias de la línea base;
  cualquier línea añadida antes de un símbolo citado desincroniza `manifiesto_citas.md` (`python3 -m src.normativa.manifiesto
  --escribir --suite "…"` lo resincroniza).
- **Mover material de proceso**: `tests/test_t11_*.py` leen `docs/contrato_entradas.md`, `docs/decisiones_diferidas.md` y los
  cuatro documentos de validación; `test_t11_validacion_integral.py` importa `tests/test_nivel_medido.py`
  (`SIN_CONSUMIDOR_Y_SIN_MEDIDA`); `test_t0_gobernanza` y `tests/apoyo/tracker.py` leen el `.xlsx`.
- La tolerancia de HY-8 es criterio del proyecto (no `[N]`): vive en `tests/apoyo/validacion_externa.py`, no en
  `constantes_normativas.py`, a propósito.

## 10. Remedición sobre `origin/main`

`git fetch origin main` → `origin/main` = `f77c5d47c635e70eb1883204175615fa8aad2dfd` = HEAD del worktree; `tesis/T-11` empujada
en el mismo commit. Suite entera sobre ese árbol, con `NORMAS_DIR`, «PyMuPDF sí · Tk no»: **6446 passed, 23 skipped (438.6 s)
→ collected 6469**. Salidas: `SP/T-11/suite_final_con.txt`, `SP/T-11/suite_final_sin.txt`, `SP/T-11/suite_origin_main.txt`;
rojo de las correcciones: `SP/T-11/rojo_correcciones.txt`.
