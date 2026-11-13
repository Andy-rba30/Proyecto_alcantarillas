# AUDITORÍA ADVERSARIAL de T-11 (validación integral de las tres familias) — FASE A

- Auditado: `/home/user/wt/T-11`, rama `tesis/T-11`, HEAD `c774035`; base `14f6138` (`/home/user/wt/main`).
- Sólo lectura sobre el repositorio. Temporales y scripts en `SP/T-11-aud/` (`SP` = `/tmp/claude-0/-home-user-Proyecto-alcantarillas/0d09ea9c-a87f-5311-8eec-38e45d8c2a3d/scratchpad/`). El worktree temporal de mutación se creó y se quitó (`git worktree list` queda como estaba).
- Entorno: `NORMAS_DIR=/home/user/andy-rba30/normas`, PyMuPDF sí, Tk no, python 3.13. No se corrió la suite entera.
- Orden de las reglas: `PY="NORMAS_DIR=/home/user/andy-rba30/normas PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/user/wt/T-11 python3"`, desde `/home/user/wt/T-11`. `var.py '<cambios>' [x]` corre el juego con los cambios de una variante (la forma de `J.VARIANTES`) e imprime diseño, bloqueos y, con `x`, las verificaciones que no cumplen.

## VEREDICTO: **AJUSTADO**

T-11 hace lo que dice en lo esencial: no cambia cálculo, el juego entra por las puertas, los cuatro documentos se generan con test de sincronía, las cifras de HDS-5 y HEC-14 están en su página y los barridos que publica se reproducen. **Diámetros / secciones / materiales / HW movidos: NINGUNO** (medido, §5 de abajo). Lo que hay que ajustar son JUICIOS: la «lista exacta» no es exacta con los valores de archivo, la corrida titular pisa dos decisiones que el dueño confirmó sin decirlo donde se lee el resultado, el anexo de sensibilidad deja fuera al menos cuatro [A] que mueven el diseño, y el defecto T11-03 es más ancho de lo descrito y su corrección SÍ toca texto de la línea base.

Hallazgos: **1 ALTA, 6 MEDIA, 7 BAJA. Todos [RESTO]; ninguno [FÓRMULA/CITA]** (lo verificado contra PDF está al final, en «Refutado con evidencia»).

---

## Hallazgos

### H1 · ALTA · [RESTO] — La «lista exacta» no es exacta: con los valores de ARCHIVO falta una entrada del EMS que detiene 24 etapas, y faltan condicionales que detienen

**Qué dice T-11.** `docs/contrato_entradas.md` §7: «exige que la tabla nombre **exactamente** las mismas entradas: ni una de más, ni una de menos. Lo que no está aquí no detiene nada si falta». `docs/validacion_integral.md` §4: `peso_especifico_saturado_relleno_kn_m3` → «SIN EFECTO MEDIBLE».

**Por qué es falso.** La lista se mide quitando una entrada a la vez de un juego que declara `drenaje_trasdos='drenado'` (el archivo dice `sin_drenaje`, confirmado por el dueño el 2026-11-13 09:45). Con el valor de archivo el relleno se calcula saturado y el γ saturado del relleno (ensayo del EMS, sin valor) detiene la estabilidad estática y sísmica y el armado de los dos cabezales de los cuatro puntos:

```
$PY SP/T-11-aud/var.py '(("declarar","drenaje_trasdos",None),("declarar","peso_especifico_saturado_relleno_kn_m3",None))'
A-01 dim Ø 0.90 m
   BLOQ CriterioPendienteError | estabilidad E1-E3 del cabezal de entrada, condicion estatico (T-7b) | peso_especifico_saturado_relleno_kn_m3
   BLOQ CriterioPendienteError | ... condicion sismico ... | BLOQ ... cabezal de salida (estatico, sismico) | BLOQ armado de entrada | BLOQ armado de salida
   (lo mismo en A-02, B-01 y C-01: 6 etapas por punto, 24 en total)
```

El propio contrato lo dice en su §3.3 («Sólo hace falta si hay agua en el relleno … o `drenaje_trasdos` = `sin_drenaje`, que es el valor de archivo: entonces, `CriterioPendienteError`»), de modo que la §7 contradice a la §3.3 por omisión.

**Otras condicionales que DETIENEN y la §7 no nombra** (su lista de «condicionales que el juego no dispara» se presenta como completa):
- `h_eq_banda_intermedia_borde` [A] sin valor — reproducido: `var.py '(("sitio","distancia_borde_calzada_al_trasdos_m",{"valor":0.1,"trazabilidad":"DATOS DE PRUEBA, NO DEL PROYECTO","fecha":"2026-11-13"}),)'` → `CriterioPendienteError` en los cuatro puntos (banda 0 < d < 1.0 ft de AASHTO 3.11.6.4; símbolo `M9.CRITERIO_H_EQ_BANDA_BORDE`).
- `h_eq_bajo_altura_tabulada` [A] sin valor — muro de menos de 5.0 ft = 1.524 m (`M9._interpolar_h_eq`).
- `N_cq_N_gammaq_meyerhof` [A] sin valor — con `terreno_delante_del_cabezal='talud_descendente'` (barrido: 24 veredictos por punto).
- `q_n_kpa` del EMS con fundación en roca (`M9`, rama `cimentacion_en_roca()` → «método no evaluable»).
- Las columnas obligatorias del CSV que el fixture ya trae (Q de A y B, cotas, CBR…): la carga se detiene sin ellas; la §7 no dice que su lista es «además de la §1».

**El test pasa con el defecto**: `test_la_lista_exacta_esta_nombrada_en_el_contrato_de_entradas` compara la §7 con la misma medida incompleta.

**Corrección (ancla por símbolo).**
1. `tests/apoyo/validacion_integral.py::lista_exacta` y `quitar_una`: medir sobre DOS bases y unir — el juego, y el juego sin las declaraciones que pisan un valor de archivo (`drenaje_trasdos`, `factor_muro_eleccion`). Con eso `peso_especifico_saturado_relleno_kn_m3` entra sola como «entrada del proyecto (ensayo, EMS)».
2. `docs/contrato_entradas.md` §7: fila nueva del γ saturado; en «Condicionales» sumar las cuatro de arriba; sustituir «Lo que no está aquí no detiene nada si falta» por una frase que diga que la lista es la del juego sobre las dos bases, además de las columnas obligatorias de la §1, y que las condicionales nombradas no se midieron.
3. `test_la_lista_exacta_…`: añadir al conjunto mínimo `peso_especifico_saturado_relleno_kn_m3`.

### H2 · MEDIA · [RESTO] — La corrida «completa» pisa dos decisiones que el dueño confirmó, hacia el lado favorable, y el §2 del documento no lo dice

`J.DECLARACIONES` declara `drenaje_trasdos='drenado'` y `factor_muro_eleccion='reduccion_por_desplazamiento'`; el archivo dice `sin_drenaje` y `sin_reduccion`, las dos confirmadas en `ORQ/DECISIONES_DUENO_2026-11-12.md` (13-nov 09:45). PRECISIONES_T-11 autoriza `--declarar` «para los CRITERIOS que el dueño dejó sin valor a propósito», no para pisar los que tienen valor. El archivo no se tocó (bien, y un test lo fija), pero el resultado que el documento presenta como titular («no pasan E3 estática ni E1 sísmica») es el de la versión favorable. Con las decisiones de archivo, medido:

```
$PY SP/T-11-aud/var.py '(("declarar","drenaje_trasdos",None),("declarar","factor_muro_eleccion",None))' x
  → en los 8 cabezales: E1-LRFD.est, E2-LRFD.est y E3-LRFD.est NO CUMPLEN (las tres filas estáticas del marco que rige)
    y la condición sísmica es «método no evaluable» (T7B-05).
$PY SP/T-11-aud/var.py '(("declarar","factor_muro_eleccion",None),)' x
  → con `sin_reduccion` y drenado: además E2-LRFD.sis y E3-LRFD.sis no cumplen en los 8 cabezales.
```

No está escondido (variante `drenaje_de_archivo`, anexo de sensibilidad), pero está en una celda de 6 000 caracteres y la «Lectura de ingeniería» del §2 no lo menciona.

**Corrección.** `validacion_integral.generar` §2: una línea generada con las claves de `J.DECLARACIONES` cuyo criterio TIENE valor de archivo (clave, valor de archivo, valor del juego) y el resultado de la variante con los dos valores de archivo (variante nueva en `J.VARIANTES`, p. ej. `decisiones_de_archivo`); la lectura del §2 debe decir las dos caras. Pregunta 1 al dueño: cuál de las dos es la titular.

### H3 · MEDIA · [RESTO] — El anexo de sensibilidad deja fuera [A] que MUEVEN EL DISEÑO dentro de su ventana; «5 mueven el diseño» está subcontado

Barrí con el mismo `sensibilidad.medir` (la puerta de PF-3) los criterios con ventana legible por máquina que NO están en `BARRIDOS` (`SP/T-11-aud/sweep_all.py`, salida en `sweep_all.out`). Resultado sobre el juego:

| Criterio (no está en el anexo) | Valores | Efecto medido |
|---|---|---|
| `espesor_pared_cajon` [A] perfil (0.20–0.30) | 0.20, 0.25, 0.30 | **MUEVE EL DISEÑO**: con 0.30, C-01 no dimensiona (V7) — ya lo decía la ficha T3-08 |
| `pendiente_minima_conducto` [A] perfil (0.0–0.005) | 0.0, 0.005 | **MUEVE EL DISEÑO**: con 0.005, C-01 no dimensiona (V10, V7) |
| `remanso_derecho_via` [A] (el juego lo declara) | cota_de_afectacion, embalse_a_nivel, perfil… | **MUEVE EL DISEÑO**: con `embalse_a_nivel` (y los 20 m de derecho de vía del propio juego) A-01, A-02 y B-01 no dimensionan. El juego dice que pone `ancho_derecho_via_m` «para que la ventana se pueda barrer», y no la barre |
| `umbral_no_colapso_evento_extremo` [A] | …, desborde_admitido… | los cuatro puntos: «método no evaluable» (V8) |
| `origen_cota_fondo_entrada` [A] perfil | cota_terreno, cota_fondo_entrada | los cuatro dejan de dimensionar (falta la celda) |
| `peso_especifico_relleno_kn_m3` [A] perfil (17–20) | 17, 20 | veredictos: 11 en A-01, 4 en A-02, 6 en B-01, 2 en C-01 |
| `margen_zapata_bajo_socavacion_m` [C], `referencia_profundidad_socavacion` [A], `lectura_coeficientes_socavacion_hec14` [A], `punto_aplicacion_incremento_sismico` [C], `terreno_delante_del_cabezal` [A], `F_pga_lectura_columna_extrema` [A], `talud_terraplen` [A], `metodo_longitud_conducto` [A], `revestimiento_cuneta` [A] | extremos | **MUEVEN VEREDICTOS** del cabezal o de la Fase 10 |

Además:
- **`n_manning_cajon`**: el anexo concluye «sólo el HW (0.6230 → 0.6234 m)» barriendo la alternativa de n MENOR. La parte alta de la ventana que la propia ficha cita (HDS-5 B.3: 0.012–0.022 en cajón VACIADO IN SITU, que es lo que el cuadro resumen dice de C-01) no se puede declarar: `sensibilidad.medir(Barrido("n_manning_cajon", …, valores=("concrete_boxes",(0.012,0.022))))` → `ValueError … forma str`. El anexo debe decir que ese lado no se midió y por qué; C-01 está gobernado por la salida, que es donde n pesa.
- **«LEÍDO, SIN EFECTO MEDIBLE»** sólo mira material/sección, veredictos y HW (y el HW con `!=` exacto: `metodo_longitud_conducto` lo «movía» en 3·10⁻⁶ m). `duracion_caudal_pico_socavacion_min`, `instalacion_estandar_concreto` etc. cambian magnitudes (hoya, márgenes) que el anexo no compara: hay que decirlo en §1, porque «sin efecto» se lee como «da igual».
- El [A] que produce la geometría juzgada en §3.1, `predimensionamiento_cabezal`, no se barre. Dato útil que falta: `fraccion_ancho_zapata` = 0.7 YA es el techo de su ventana (0.4–0.7): dentro de la ventana la zapata sólo puede achicarse.

**Corrección.** `sensibilidad.BARRIDOS`: sumar al menos `espesor_pared_cajon` (0.20, 0.25, 0.30), `pendiente_minima_conducto`, `remanso_derecho_via`, `umbral_no_colapso_evento_extremo`, `peso_especifico_relleno_kn_m3`, `margen_zapata_bajo_socavacion_m`, `referencia_profundidad_socavacion`, `punto_aplicacion_incremento_sismico`, `terreno_delante_del_cabezal`, `metodo_longitud_conducto`; mejor: derivar la lista del censo (todo criterio con valor efectivo y ventana numérica de dos extremos o `categoria`) y listar por nombre los NO barribles (ventana en prosa, dict, series) en vez de «lo que no está no se midió». `test_los_juicios_del_anexo`, la ficha T11-05 y el informe («5 mueven el diseño») se rehacen con la medida.

### H4 · MEDIA · [RESTO] — T11-03 es un defecto REAL, más ancho de lo descrito; su corrección toca TEXTO de la línea base; y tiene un hermano que T-11 no vio

**Es real.** `MD.disenar_material` sube de escalón hasta que la clave toca la subrasante; `M5.altura_relleno_sobre_clave` (llamada por `M5.v7_flotacion`) levanta `DatoInvalidoError('cota_subrasante')` sobre un dato que nadie tocó; `MD.disenar_punto` lo traga en su rama `except DatoInvalidoError` como «material no evaluable» y el `DisenoNoFactibleError` final sale sin `delta_rasante_m` y SIN el motivo verdadero. Reproducido: `SP/T-11-aud/sintw.py` (A-01: Ø 0.90–1.05 incumplen V1 y V4; 1.20–1.35 V1 y V7; 1.50–1.65 V7; en 1.80 todo lo evaluado cumple y V7 no se puede evaluar: −0.025 m).

**Es más ancho.** No es «el caso sin TW»: es la salida ESTÁNDAR de todo punto al que una verificación no le cierra en ningún diámetro. Medido: `remanso_derecho_via='embalse_a_nivel'` (V5), `cota_afectacion…=42.0` (V5), `Q_evento_extremo_m3s=6.0` (V8) y la variante `caudal_calculado` terminan todas en «Dato invalido en 'cota_subrasante'». Y **está en la línea base desde antes de T-11**: `grep -l "a nivel de la subrasante" tests/linea_base_familia_c/*` → `cli_perfil.txt` (A-01, A-02 y B-01), `cli_perfil_ancho.txt`, `cli_familia_c.txt`, dos JSON y dos memorias. CLAUDE.md dice de B-01 «`DisenoNoFactibleError` con motivo V2»; el mensaje que la línea base imprime nombra la subrasante. La ficha T11-03 y el informe dicen «no mueve ningún número del fixture»: cierto para diámetros, pero **la corrección cambia texto en siete archivos de la línea base y `delta_rasante_m` de `null` a un número en sus JSON**; hay que regenerarla declarándolo.

**El hermano que T-11 no vio.** Un `DatoInvalidoError` de un DATO DEL PUNTO levantado dentro de la Fase 5 sale igual como «no factible» con `campo: None`:
```
$PY SP/T-11-aud/var.py '(("externo","A-01","Q_evento_extremo_m3s",0.5),)'
A-01 NO-dim  BLOQ DisenoNoFactibleError | material y diametro (bucle de MD) | None None |
  … Concreto reforzado: material no evaluable: DatoInvalidoError: Dato invalido en 'Q_evento_extremo_m3s' … es menor que el de diseño …
```
El revisor tiene que CORREGIR un dato y el informe le dice que no existe diseño. Es el mismo hueco que PC-28 cerró para `DatoFaltanteError` y C05 para el criterio inválido.

**Corrección propuesta (para el agente que la haga).**
1. **Dónde:** en `MD.disenar_material`, dentro del `except ErrorProyecto` del escalón, una rama anterior para `DatoInvalidoError` que se reconoce por GEOMETRÍA y no por el texto: `M5.cota_clave(punto, material, seccion) >= punto.cota_subrasante - TOL_UMBRAL_NORMATIVO` (a esa altura `cota_clave` ya no puede fallar). No se hace pre-chequeo antes de `verificar`: movería de sitio el `DatoFaltanteError` de la pared del HDPE de 1.35 m y cambiaría las `iteraciones` de la línea base.
2. **Qué pasa con el escalón:** se registra como hoy (con sus `verificaciones_completadas`) con motivo «Ø 1.80 m: no cabe bajo la subrasante: clave a 44.075 msnm, subrasante a 44.050 (faltan 0.025 m sólo para enrasar)», y la progresión del material TERMINA (la clave sólo sube con la sección). El material se descarta con el motivo de sus escalones evaluados (`_motivo_descarte`), no con «material no evaluable».
3. **Qué excepción y con qué delta:** el punto sigue saliendo por `DisenoNoFactibleError` desde `MD.disenar_punto`, ahora con `delta_rasante_m` = el menor, entre los materiales, de `M7.tamizado_rasante(punto=…, material=…, seccion=<primer escalón que no cabe>, HW=resultado.HW).delta_rasante_m` (M7 no importa MD: se puede importar en el punto de uso; `resultado` existe porque `resolver_control` corrió antes de `verificar`). Es el número de la Sec. 7.A/7.B («no factible → subir rasante X cm») y debe rotularse COTA INFERIOR: con esa rasante el escalón entra a V7 y a la Fase 8, que no se evaluaron, y la longitud cambia. Para llevarlo sin romper el contrato `(None, motivo)` de `disenar_material` (lo usan tests): excepción `DisenoNoFactibleError` del material capturada en `disenar_punto` en una rama propia ANTES de `except ErrorProyecto`, o un campo opcional en `PasoDiseno`. `M5.altura_relleno_sobre_clave` NO cambia (su `DatoInvalidoError` directo lo fija `test_M5_verificaciones` C09/SIS-F-10 y lo usa la Fase 8 sobre la sección adoptada).
4. **El hermano:** en `MD.disenar_punto`, acumular los `DatoInvalidoError` cuyo `campo` no es un criterio ni la señal geométrica; si TODOS los candidatos se detuvieron en el mismo campo, relanzar el primero (bloqueo `DATO_INVALIDO` con su `campo`), como `_exigir_datos_presentes`.
5. **Lo que NO debe cambiar:** el resultado aceptado cuando algún material cierra (el que no cabe se descarta y el bucle sigue, como hoy); ningún diámetro, sección, material ni HW del fixture ni de la línea base; las `iteraciones` (mismos escalones, mismas verificaciones); `test_t3_correcciones_auditoria::test_h5_…` (`"subrasante" in motivos[1]` sigue valiendo). SÍ cambian, y se declaran: los mensajes «no factible» de la línea base (7 archivos), `delta_rasante_m` en sus JSON, el docstring de MD («No calcula el delta de rasante… sale vacío a propósito») y la clave del censo de mutantes de `test_ext11_mutacion` si se toca la comparación.
6. El `xfail` se libera; añadir el test del hermano (Q extremo < Q de diseño → `DATO_INVALIDO`, campo `Q_evento_extremo_m3s`).

### H5 · MEDIA · [RESTO] — `docs/validacion_hy8.md` no dice todavía lo que el dueño decidió (añadido A.1), y le faltan dos cosas para ser ejecutable

El procedimiento NO afirma resultados de HY-8 (verificado) y sus entradas salen de la corrida. Le falta, para decir exactamente la decisión del 13-nov 18:25:
1. §5 y `TOLERANCIA_HY8_*`: «propuesta de T-11, no normativa» → **«criterio del proyecto (aceptado por el dueño el 2026-11-13), NO normativo»**; lo mismo en la ficha T11-04.
2. La tolerancia se aplica a **HW y a HW/D**: hoy sólo «en HW», y la tabla del §4 no trae HW/D (D del tubo; altura de la celda en el marco).
3. **Tipo de control distinto → «explicar» sea cual sea el porcentaje**: hoy dice «tiene que ser el mismo; si no lo es, se reporta con las dos cargas».
4. **Velocidad de salida SIN veredicto** cuando el programa no la saca de un perfil: hoy §2 y §4 la presentan como magnitud a comparar. En A-01, A-02 y B-01 (control de entrada) el programa da la de flujo uniforme con n mínimo; HY-8 la da del perfil S2 sobre 18 m de barril: no son la misma magnitud. Columna nueva «cómo sale la velocidad / lleva veredicto: sí-no».
5. **Versión de HY-8**: el §6 la pide de pasada; debe ser campo obligatorio del encabezado de cada tabla (versión y fecha).
Para ser ejecutable además: (a) HY-8 exige «Roadway Data» (cota de coronación, longitud y ancho): hay que dar `cota_rasante` de cada punto y decir que no debe haber desborde; (b) decir con qué n se calculó el «Tirante normal» de la tabla. Menor: «≤ 0.002 %» de diferencia de longitud vale para S = 0.006; con el 0.010 de B-01 es 0.005 %.
`test_el_procedimiento_de_hy8_no_afirma_resultados` es tautológico (busca la frase «NO afirma ningún resultado»): que fije las cinco reglas.

### H6 · MEDIA · [RESTO] — El anexo no dice de `v_max_concreto_eleccion` lo que el dueño decidió (añadido A.2); y el TMC al que A-01 «pasa» está en un suelo que la misma corrida califica de agresivo para el TMC

Reproducido: `v_max_concreto_eleccion=3.0` → A-01 TMC Ø 1.20 m (V3 de A-01 = 3.206 m/s frente a 3.0: 7 % por encima). Falta en `docs/validacion_sensibilidad.md`:
1. Que el criterio **se queda SIN valor por decisión del dueño (2026-11-13)**, que rige el máximo de 6.0 m/s de la Tabla Nº 10, y que el resultado con 3.0 es **resultado de la tesis que no cambia el fixture**. Hoy sólo dice «el juego no lo declara: rige la regla de su ficha».
2. Que ese resultado depende de OTRO [A] y de un dato del juego: la matriz de durabilidad de la misma corrida dice «suelo agresivo según AASHTO LRFD 11.10.6.4.2a…: sulfatos en el suelo = 500 ppm mayor de 200 ppm. La TMC sigue candidata: la analogía avisa y no excluye (`suelo_agresivo_lrfd_sobre_tmc` = 'aviso')». Con `excluye` (dentro de su ventana), medido:
```
$PY SP/T-11-aud/var.py '(("declarar","v_max_concreto_eleccion",3.0),("declarar","suelo_agresivo_lrfd_sobre_tmc","excluye"))'
A-01 NO-dim  BLOQ DatoFaltanteError | … | perfil_hdpe_fabricante
```
3. **El comentario del juego es falso contra el propio programa**: `juego_validacion_integral.EXTERNOS` dice «Ensayos de durabilidad de un suelo NO agresivo» con `sulfatos_suelo_ppm: 500`; el criterio `suelo_agresivo_acero_lrfd` pone el máximo en 200 ppm. O se baja el dato de prueba a ≤ 200 ppm (y el `so4_suelo_pct` coherente), o se corrige la línea de plausibilidad («no agresivo para el concreto por la Tabla 4.4 de E.060; agresivo para el acero galvanizado por AASHTO»). Bajar el dato no mueve ningún diámetro (el concreto es el primer candidato), pero cambia avisos: decláralo.

### H7 · MEDIA · [RESTO] — Familia C: el caso titular dimensiona un marco que queda 0.616 m SOBRE el fondo del canal, y el documento no lo comenta

En la corrida completa C-01 «llega con diseño», pero con `VC2` INDICADOR («la salida queda 0.616 m SOBRE el fondo del canal aguas abajo: no empalma») y «Remanso aguas arriba del canal: no concluye» (salida de `cli.py`, bloque de C-01). La «Lectura de ingeniería» del §2 sólo habla del cabezal. El juego omite `cota_fondo_entrada` «porque es una medición que no inventa», pero inventa todas las demás; para un paso de canal es la que hace coherente el caso. Medido (`SP/T-11-aud/c01.py`): con `cota_fondo_entrada` de C-01 = 36.284 (fondo del canal + S·L) sigue dimensionando el marco 1.20 × 0.90 m (HW 0.623 m, salida), VC2 queda a −0.011 m y la longitud pasa de 21.0 a 23.9 m: la Familia C no depende de esa adopción, y eso es lo que la validación debería enseñar.
También: el TW de C-01 (0.30 m, global) es menor que el tirante normal del canal que el mismo juego declara en `seccion_receptor_medida` (b 1.0, z 1.5, S 0.006, n 0.025, Q 0.85 → 0.41 m). Medido con 0.41 m: HW 0.62307 m, sin cambio de sección. Es incoherencia del dato de prueba, sin efecto.

**Corrección.** Variante nueva `C01_fondo_en_el_canal` en `J.VARIANTES` (y TW de C-01 = 0.41 por punto, con su línea), y una frase en la lectura del §2 sobre VC2 y el remanso de C-01.

### H8 · BAJA · [RESTO] — El cuadro resumen de la Fase 11 imprime un `tipo_cabezal` único tomado de la hoja de ruta, también para el marco

`SP/T-11-aud/completa.csv`, columna `tipo_cabezal`: «Cerrada: tubo a ras del muro (square edge)» en los cuatro puntos, C-01 incluido (marco con aletas de 30° a 75°, Carta 8). Sale de `M11_reporte.decision_embocadura(tableros_pendientes(...))` (Tablero 2.3 de la hoja de ruta), no del punto: `informe.cabezal.embocadura` de cada punto dice `cabezal_con_aleros`, 45° (T-7a). La validación comprueba que el cuadro «lleva su fila», no lo que dice. Anterior a T-11 (T-7a). **Corrección:** `M11.fila_resumen` / `_fila_resumen_csv` leen la embocadura y el tipo del cabezal DEL PUNTO; mueve los dos CSV de resumen de la línea base (texto, ningún número). Puede ir a T-12 con ficha; hoy no está nombrado en ninguna parte.

### H9 · BAJA · [RESTO] — (añadido C) `diseno.HW_salida_m` del JSON tiene dos significados: **hueco de transparencia del contrato del JSON, no defecto de cálculo**

Evidencia (`SP/T-11-aud/completa.json`): C-01 → `HW_salida_m` 0.62299 = `perfil_HW_remanso_m` (≠ `perfil_HW_aproximado_m` 0.61371): la clave lleva el valor que SUSTITUYE. A-02 y B-01 → `HW_salida_m` = `perfil_HW_aproximado_m` (0.5625 y 0.3558) con `perfil_HW_remanso_m: null`: la clave lleva la aproximación DESCARTADA. En B-01, `HW_salida_m` 0.356 > `HW_entrada_m` 0.232 con `control_gobernante: entrada` y `HW_gobernante_m` 0.232: quien lea el JSON con la regla «gobierna la mayor» obtiene otra carga. El HW que gobierna es correcto (HDS-5 pág. impresa 3.24 / PDF 106: «If the headwater depth falls below 0.75D, the approximate method should not be used», y el S1 no alcanza la entrada); la CLI de texto lo explica en la línea «Perfil». **Corrección:** en `cli.informe_json`, `HW_salida_m: null` cuando `perfil_sustituye_aproximacion` y `perfil_HW_remanso_m is None` (la aproximación ya está en `perfil_HW_aproximado_m`), y «salida: no se forma» en la línea «Control» del texto. Mueve la línea base (A-02 del JSON ancho) por formato.

### H10 · BAJA · [RESTO] — (añadido C) La fila A7 que no aparece ni avisa: **hueco de transparencia, no defecto**

`M9.ensamblar_armado`, rama `if requisitos.fc_min_MPa is not None:`. Con exposición «insignificante» la Tabla 4.4 de E.060 no impone f'c mínimo: no hay nada que juzgar y no se rellena nada (correcto). Pero la tabla de A1 a A8 queda sin A7 y el lector no distingue «evaluada, sin mínimo aplicable» de «no evaluada». **Corrección:** emitir A7 con `EstadoDeVerificacion.NO_APLICA` (ya tiene productor real desde C10) y la razón («exposición a sulfatos insignificante y ninguna fila de la Tabla 4.2 aplicable: E.060 no fija f'c mínimo»). La variante `agua_con_cloruros` ya muestra el otro lado.

### H11 · BAJA · [RESTO] — El censo del §6 presenta como «lo destraba un ensayo» criterios que NO tienen consumidor; y `SIN_CONSUMIDOR_Y_SIN_MEDIDA` quedó sin evidencia de T-11

- `docs/validacion_integral.md` §6: `clase_sitio`, `capacidad_portante_adm`, `Mw_licuefaccion` salen como «ensayo» y las dos `edicion_*` como «decisión», con «lo que lo destraba». Ningún módulo los lee (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`); la presión admisible del EMS entra por `suelo_fundacion.q_adm_kpa`, no por `capacidad_portante_adm`. La tabla debe llevar la columna «consumidor: sí / no (censado)».
- `TW_receptor` sale como «decisión» (lo clasificaría «criterio que el proyectista declara») y su fuente es «PENDIENTE: ANA / Junta». Y el contrato §7 y el test dicen que «sólo se lee si el TW no llega por ninguna de las cuatro vías»; `servicio._resolver_tw` dice otra cosa: «SI 'TW_receptor' TIENE VALOR, MANDA SOBRE LAS VÍAS 3 Y 4».
- PRECISIONES 4 (iv) pedía `SIN_CONSUMIDOR_Y_SIN_MEDIDA` «al día»: T-11 no lo midió ni lo nombra. Lo conté: 7 entradas; CLAUDE.md sigue diciendo «ocho» (FASE B).
- `M9.FUNCIONES_SIN_CONSUMIDOR`: el test de T-11 es correcto (existen, sin llamador, el ensamble fuera del censo).
- `AssertionError`/`NotImplementedError`: ninguno en `src/modulos/` ni en `src/servicio.py` (los tres de `gui/editores.py` son métodos abstractos). Verificado con grep además del test.
- Tracker: 64 `INF-`; 22 no «Cerrado» = 19 + 3 «N/A (sin trabajo)»: la lista del informe §8 coincide con `tests/apoyo/tracker.py`. `INF-5.1.3`, `5.1.9`, `5.1.16` cerrados (T-1, T-4, T-4) e `INF-5.1.8` parcial (T-9): el informe dice la verdad.

### H12 · BAJA · [RESTO] — Textos que dicen lo contrario de lo que hay

1. `juego_validacion_integral.py` (docstring): «los archivos materializados … nunca se versionan». Falso desde `4f6cad6`: `tests/fixtures/corridas_de_referencia/hidrologia_calculada/` versiona los seis. Tres de ellos (`puntos.csv`, `externos.json`, `declaraciones.json`) no llevan la cabecera «DATOS DE PRUEBA» (el formato no la admite; igual que las dos carpetas de T-10): falta al menos un `LEEME` rotulado en la carpeta, o decirlo en la ficha T11-06.
2. `src/indice_formulas.py`: «Tres corridas con DATOS DE PRUEBA **que ya estaban en el repositorio**» y «ninguno es nuevo: `test_t10_memoria` comprueba que son los mismos que la guía y los de T-7b/T-7c». Para la tercera corrida no es cierto (freático 3.0 m, datos de A-02, B-01 y C-01, [S] de sitio: nuevos de T-11).
3. `docs/validacion_integral.md` §4: la leyenda define DETIENE como «aparece un bloqueo o el punto deja de dimensionar» y la tabla usa una clase que la leyenda no trae («NO FACTIBLE», fila de `TW_m`).
4. `docs/validacion_hds5.md`: fila `cmp_60_bisel_45 / HW_sobre_D` imprime «−3.0 %» con veredicto «fuera de la lectura (3 %)» y causa «−3.1 %»; `cajon_6x5 / H_ft` «−4.0 %» con causa «−3.9 %»; `EL_ho` «−5.7 %» con «−5.6 %». Y en HEC-14 «profundidad 3.3·D50: −1.0 % → > 1 %, censada»: 0.495/0.50 − 1 es −1 % exacto y cae fuera por 10⁻¹⁷ (comparación de floats sin tolerancia nombrada, contra «Estilo» de CLAUDE.md); el test «cada censada está de verdad fuera» pasa por ese ruido. Imprimir con dos decimales y comparar con tolerancia.
5. Fichas: T11-03 («no mueve ningún número del fixture»: ver H4), T11-04 («propuesta de T-11»: ver H5; y dice «17 cifras» de HEC-14 cuando el documento trae 19: 5 + 3 + 4 + 4 + 3), T11-05 («mueven el diseño: cinco»: ver H3).

### H13 · BAJA · [RESTO] — Tests que no fijan lo que su nombre dice

- `test_la_cli_real_dice_lo_mismo_que_el_servicio`: `assert f'id="punto-{id}"' in html or id_punto in html` — la segunda mitad es siempre cierta.
- `test_el_juego_solo_entra_por_las_puertas_de_la_cli`: «el CSV es una copia con las celdas del juego y nada más» sólo compara cabecera y número de líneas. Mutante medido (el materializado cambia además `sucs_fundacion` de B-01): este test queda verde; lo mata otro (`…es_el_juego_materializado`, byte a byte). Sin hueco real, pero la aserción no es la del docstring.
- `test_cada_barrido_recorre_la_ventana_de_su_criterio`: no comprueba que los valores estén DENTRO de la ventana (lo garantiza la puerta de `barrido.barrer` en ejecución: mi intento fuera de forma fue rechazado).
- Los de H1 y H5 (pasan con el defecto / tautológico).
Los 43 de los tres archivos corren en 39 s (42 passed, 1 xfailed): la marca `lento` de los barridos sobra.

### H14 · BAJA · [RESTO] — Dos líneas de plausibilidad que no sostienen su dato, y una cadena que la validación no recorre

- `Q_evento_extremo_m3s` = 1.11 × Q de diseño para un TR de 500 años (heredado de T-7b): la línea da la proporción, no por qué es plausible. Medido en A-01: con 1.29×, 1.50× y 1.71× sigue Ø 0.90 m; **con 2.0× pasa a Ø 1.05 m** (V8). El «llega con Ø 0.90» de la corrida completa depende de ese dato; dilo en la lectura del §2.
- La cadena «caudal CALCULADO → diseño» no se valida en ninguna corrida: en la única que calcula el caudal (variante `caudal_calculado`, tercera corrida del índice) A-01, A-02 y B-01 no dimensionan (25.8, 22.3 y 1.79 m³/s frente a 1.167, 0.480 y 0.095 declarados). La Fase 1-bis SÍ entra al índice (ocho `FH.*`, test). El documento atribuye la incoherencia a las cuencas sintéticas; no se sabe cuál de los dos juegos es el irreal (Pregunta 4).

---

## Lo que comprobé y se sostiene («refutado con evidencia» = intenté romperlo y no pude)

1. **No cambia cálculo.** `git diff 14f6138 HEAD -- src/`: sólo `modelos.ALCANCE_DECLARADO` (+2 entradas de texto) e `indice_formulas.py` (tercera corrida, `m2` en la máscara). `criterios_adoptados.py`, `datos_sitio.py`, `constantes_normativas.py`, `conftest.py`, `tests/ejemplo_puntos.csv`, `docs/linea_base.md`, `docs/guia_perfil.md`: sin diff. Corrí el juego completo por la CLI sobre la BASE (`/home/user/wt/main`) y sobre HEAD: `cli.py --comparar completa_base.json completa.json` → «IGUALES»; el texto difiere sólo en las dos líneas nuevas del alcance. Línea base: los cuatro JSON +12 líneas cada uno (las dos entradas de `alcance.declarado`), los cinco `cli_*.txt` +2 líneas, las tres memorias +1 142 caracteres (dos `<li>`). **Diámetros, secciones, materiales, HW: ninguno movido.**
2. **Corridas.** Completa por la CLI real: 4 de 4 dimensionan (A-01, A-02, B-01 concreto Ø 0.90; C-01 marco 1.20 × 0.90), `Traceback` ninguno, único bloqueo VC1-01. Por defecto: 9 etapas bloqueadas (luz ×4, `L_hidraulico_m`, `categoria_refuerzo_aashto` ×3, `exposicion_quimica_ems`) + VC1 diferido: coincide con el §3. 21 variantes adversariales mías (`SP/T-11-aud/probe.py`: NF 0 / 0.5 / 1.0, TW 0 / 0.9, luz 6.5, Q extremo menor y mayor, peralte y bombeo a la vez, fundación cohesiva, muro perpendicular, distancia de borde 0.1 m, etc.): **ninguna excepción fuera de `ErrorProyecto`**.
3. **Puerta de atrás.** No hay monkeypatch ni default: `V.correr` vacía y repone declaraciones y [S] de sesión; la CLI en subproceso da el mismo `diseno` y los mismos estados.
4. **HDS-5 contra el PDF** (`hif12026.pdf`, formularios renderizados a PNG: págs. impresas DG1.4 / PDF 275 y DG1.10 / PDF 281). Las siete filas coinciden cifra a cifra con el documento (p. ej. RCP 54 in: 1.77 / 7.97 / 4.1 / 4.3 / 4.7 / 107.0 / 15.3; cajón 6×5: 1.57 / 7.9 / 4.2 / 4.6 / 3.55 / 103.2 / 21.1; cajón 5×5 bisel: 1.71 / 8.55 / 4.8 / 4.9 / 5.0 / 104.9 / 20.8). Casillas «fuera» recalculadas a mano: cajón 6×5 `H` — fórmula (7) del pie con A 30 ft², R 30/22, n 0.012, L 250, ke 0.5 → 3.40 ft (impreso 3.55); cajón 5×5 bisel `H` — con ke 0.2 → 4.42 ft, con 0.5 → 5.09 ft (impreso 5.0): la inconsistencia es de la fuente, como dice el censo; CMP 60 `HW/D` — ec. sumergida con c 0.0300, Y 0.74, q* 4.555 → 1.3575 (impreso 1.40) y 7.10 ≠ 1.40 × 5.0. Tolerancia de la fuente: «accurate to within plus or minus ten percent, in terms of headwater elevation», pág. impresa 3.1 / PDF 83: literal.
5. **HEC-14 contra el PDF** (`hec14.pdf`): las 19 frases y los datos de entrada (Q 2.33, 85 ft³/s, 1.6 ft, 457, 0.764, 1.87, 23,970, 1.133, 3.88, 12.192, 8.5) están en PDF 219–220, 57–58, 61–62 y 197.
6. **Alcance declarado**: 7 entradas = las 5 de T-10 + `velocidad_salida_banda_de_regimen` (T8-09, símbolo `M6_proteccion._aviso_banda_de_regimen` existe) + `escalon_regla_salida_hw_1_2_d` (T7V-01; los 1.276 y 1.290 m³/s están en la ficha; la regla 0.75 D / 1.2 D es literal de HDS-5 pág. impresa 3.24 / PDF 106). Sin duplicados.
7. **Barridos reproducidos**: `v_max_concreto_eleccion` (mueve: A-01 → TMC Ø 1.20), `regimen_v2b` (mueve: C-01 no dimensiona con `umbral_duro`), `HW_D_max` (no mueve). Una clave a la vez por `barrido.barrer`; el primer valor es el efectivo.
8. **Tercera corrida del índice**: los seis archivos son la materialización del juego (test byte a byte); `FH.*` fuera del cuadro de no ejercitados; `test_indice_formulas`, `test_decisiones_diferidas`, `test_linea_base`, `test_t10_memoria`: verdes.
9. **Sospecha descartada**: que la zapata de la regla pudiera pasar dentro de la ventana de `predimensionamiento_cabezal`: no, `fraccion_ancho_zapata` ya está en su techo.

## Añadido D — cierre de filas del tracker

| ID | Veredicto | Evidencia y residual que debe quedar escrito en la fila |
|---|---|---|
| `INF-0.5` | **Cerrar con salvedad escrita** (precedente: `INF-4.2`), y sólo después de corregir H1 | A nivel de perfil el fixture dimensiona 4 de 4 sin declarar nada. A EXPEDIENTE, con todos los DATOS puestos, tres criterios que el dueño dejó vacíos a propósito (`remanso_derecho_via`, `TR_evento_extremo`, `umbral_no_colapso_evento_extremo`) siguen deteniendo el dimensionamiento de los cuatro puntos, y `categoria_refuerzo_aashto` la Fase 9 del proyecto: el hallazgo literal («criterios vacíos que detienen todo») persiste por decisión, y la fila tiene que decirlo. Si el tracker no admite salvedad: «Cerrado parcial» |
| `INF-3.4.3` | **Cerrar** (T-7b; verificado por T-11) | El ensamble consume las fórmulas; φ es entrada del EMS; δ [C], γ_EQ [A] y la regla de i con ventana y barridos. `inclinacion_muro_beta` sólo lo lee la vía de contraste (correcto con el plano vertical del talón) |
| `INF-3.4.4` | **Cerrar en parte** | Cerrado: ensamble, un marco que rige, capacidad portante, sin `AssertionError`. Residual: E4 y E5 (estabilidad global y del talud) NO se evalúan (ficha T7B-07; `metodo_estabilidad_global` vacío); Meyerhof en talud vacío; la geometría de regla no pasa y no se itera (T7B-09) |
| `INF-3.4.6` | **Cerrar** con NOTA | k_h y k_v justificados como criterios con fuente y ventana; el desplazamiento admisible es del Propietario. NOTA: con el `drenaje_trasdos` de archivo la sísmica no es evaluable (T7B-05) |

## Preguntas para el dueño (con recomendación)

1. **¿Cuál es la corrida titular de la validación?** Hoy corre con `drenado` y `reduccion_por_desplazamiento`, contra los dos valores de archivo que usted confirmó. *Recomendación:* titular con los valores de archivo (resultado: las tres filas estáticas LRFD no pasan y la sísmica no se evalúa) y la versión favorable como variante; las dos impresas en el §2.
2. **T11-03**: su corrección cambia el texto «no factible» en siete archivos de la línea base y pone un `delta_rasante_m` donde hoy hay `null`, sin mover ningún diámetro. *Recomendación:* aceptarlo, con el delta rotulado «cota inferior», e incluir el caso hermano (dato inválido del punto que hoy sale «no factible»).
3. **Cuadro resumen (`tipo_cabezal`) y `HW_salida_m` del JSON** (H8, H9): son de formato y mueven la línea base por texto. *Recomendación:* H9 ahora, con las correcciones de T-11; H8 en T-12 con ficha.
4. **Caudales del fixture frente a la hidrología calculada**: el programa calcula 15 a 22 veces el caudal declarado con la serie sintética. *Recomendación:* añadir (lote posterior) un juego sintético de cuencas coherente para que una corrida valide «caudal calculado → diseño»; y antes de usar el fixture como ejemplo de la tesis, contrastar sus Q con el estudio hidrológico real.
5. **`INF-0.5`**: ¿«Cerrado» con salvedad o «Cerrado parcial»? *Recomendación:* Cerrado con la salvedad escrita en la fila.
