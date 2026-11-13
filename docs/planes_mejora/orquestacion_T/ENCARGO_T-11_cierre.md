# Encargo: T-11 — correcciones [RESTO] de la auditoría + INTEGRACIÓN EN MAIN (cierre) — sexta sesión

Eres el agente que CIERRA T-11. Worktree `/home/user/wt/T-11`, rama `tesis/T-11` (el orquestador te da el HEAD: FASE A de T-11 +
la corrección de T11-03 que hizo otro agente). Base de integración: `origin/main` = `14f6138`. Sigue
`ORQ/ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (PARTE 1 y PARTE 2) con la ENMIENDA DE LA SEXTA SESIÓN de
`ORQ/ORQUESTACION.md` (rutas, pie de commit, base). Lee además: `ORQ/PRECISIONES_T-11.md`, `ORQ/INFORME_T-11_faseA.md`,
**`ORQ/AUDITORIA_T-11.md` (tu lista de correcciones)**, `SP/INFORME_T-11_T11-03.md` (lo que hizo el agente de T11-03 y lo que te
deja dicho) y el final de `ORQ/DECISIONES_DUENO_2026-11-12.md` («Decisiones del dueño sobre las dos preguntas abiertas de T-11»).
T-11 VALIDA: ningún cálculo cambia. PARADA (c) vigente: ningún diámetro, sección, material ni HW del fixture o de la línea base
se mueve.

## PARTE 1 — hallazgos que te tocan (H4 ya está hecho: NO lo rehagas; sólo comprueba que sigue verde tras tus cambios)

Resoluciones del orquestador (se aplican; si la evidencia las contradice, deja lo que la evidencia sostiene y repórtalo):

- **H1 (ALTA)** — tal como lo propone el auditor: `lista_exacta` / `quitar_una` medidas sobre DOS bases (el juego, y el juego sin
  las declaraciones que pisan un valor de archivo) y unidas; `peso_especifico_saturado_relleno_kn_m3` entra a la §7 del contrato;
  las condicionales que detienen y no se miden (`h_eq_banda_intermedia_borde`, `h_eq_bajo_altura_tabulada`,
  `N_cq_N_gammaq_meyerhof`, `q_n_kpa` en roca) nombradas como «condicionales no medidas»; la frase «lo que no está aquí no detiene
  nada» sustituida por lo que la medida sostiene («además de las columnas obligatorias de la §1»); la §7 no puede contradecir a
  la §3.3; el test fija el mínimo nuevo.
- **H2 (MEDIA) — RESOLUCIÓN: el resultado TITULAR del §2 de `docs/validacion_integral.md` es el de los VALORES DE ARCHIVO**
  (`drenaje_trasdos` = `sin_drenaje`, `factor_muro_eleccion` = `sin_reduccion`: decisiones confirmadas por el dueño), impreso
  PRIMERO: qué pasa con ellos (filas estáticas LRFD, sísmica «método no evaluable» —ficha T7B-05—, y el γ saturado del relleno como
  ensayo del EMS que hace falta). DESPUÉS, como «variante que ejercita la cadena sísmica y el caso drenado», el resultado del
  juego tal como está (drenado + reducción por desplazamiento). Línea generada con las claves de `J.DECLARACIONES` cuyo criterio
  TIENE valor de archivo (clave, valor de archivo, valor del juego, por qué el juego lo cambia). Variante nueva en `J.VARIANTES`
  (`decisiones_de_archivo`, con el γ saturado de prueba declarado por la puerta de ensayo y su línea de plausibilidad). Los
  BARRIDOS de sensibilidad siguen midiéndose sobre el juego (hace falta una base donde el método sea evaluable), y el anexo lo
  dice en su §1 con esas palabras. El juego (`J.DECLARACIONES`) NO se cambia: cambia qué se presenta como titular.
- **H3 (MEDIA)** — sumar a `sensibilidad.BARRIDOS` los criterios que el auditor midió (`espesor_pared_cajon`,
  `pendiente_minima_conducto`, `remanso_derecho_via`, `umbral_no_colapso_evento_extremo`, `peso_especifico_relleno_kn_m3`,
  `margen_zapata_bajo_socavacion_m`, `referencia_profundidad_socavacion`, `lectura_coeficientes_socavacion_hec14`,
  `punto_aplicacion_incremento_sismico`, `terreno_delante_del_cabezal`, `F_pga_lectura_columna_extrema`, `talud_terraplen`,
  `metodo_longitud_conducto`, `revestimiento_cuneta`, `origen_cota_fondo_entrada`) y, mejor, DERIVAR la lista del censo (todo
  criterio con valor efectivo y ventana legible por máquina) con la lista NOMINAL de los no barribles y su razón. `n_manning_cajon`:
  decir que el lado alto de la ventana (HDS-5 B.3, 0.012–0.022) no se midió y por qué (la puerta no admite el par). «LEÍDO, SIN
  EFECTO MEDIBLE» se redefine en §1 (qué magnitudes compara y cuáles no) y el HW se compara con tolerancia nombrada, no con `!=`.
  `predimensionamiento_cabezal`: decir que `fraccion_ancho_zapata` = 0.7 ya es el techo de su ventana. Los recuentos («N mueven el
  diseño») se rehacen con la medida, en el anexo, la ficha T11-05 y los tests.
- **H5 (MEDIA)** — `docs/validacion_hy8.md` y `TOLERANCIA_HY8_*` dicen EXACTAMENTE la decisión del dueño (13-nov 18:25): criterio
  del proyecto, NO normativo, coherente con el 3 % de lectura de la validación HDS-5; aplicada a HW y a HW/D (columna HW/D en la
  tabla; D del tubo o altura de la celda); control distinto → «explicar» sea cual sea el porcentaje; velocidad de salida SIN
  veredicto cuando el programa no la saca de un perfil (columna «cómo sale / lleva veredicto»); versión y fecha de HY-8 como campo
  obligatorio del encabezado de cada tabla. Ejecutable: «Roadway Data» (cota de rasante de cada punto; sin desborde), el n del
  tirante normal, y el porcentaje de longitud corregido. El test deja de ser tautológico: fija las cinco reglas.
- **H6 (MEDIA)** — el anexo dice de `v_max_concreto_eleccion` la decisión del dueño (se queda SIN valor; rige 6.0 m/s de la Tabla
  Nº 10; el paso a TMC Ø 1.20 con 3.0 m/s es resultado de la tesis que no cambia el fixture) y que ese resultado depende de
  `suelo_agresivo_lrfd_sobre_tmc` (con `excluye`, A-01 se detiene en `perfil_hdpe_fabricante`: medirlo como barrido combinado
  declarado o como variante). El dato `sulfatos_suelo_ppm: 500` NO se cambia: se corrige su línea de plausibilidad (no agresivo
  para el concreto por la Tabla 4.4 de E.060 —verifícalo contra el PDF—; agresivo para el acero galvanizado por el umbral de
  AASHTO que aplica `suelo_agresivo_acero_lrfd`).
- **H7 (MEDIA)** — variante `C01_fondo_en_el_canal` en `J.VARIANTES` y la frase del §2 sobre VC2 y el remanso de C-01; TW de C-01
  coherente con el tirante normal del canal que el propio juego declara (0.41 m por punto, con su línea), si no mueve la sección
  ni el HW publicado más allá de lo que el auditor midió (dilo); si regenerar la tercera corrida del índice por ese cambio te
  complica, deja el TW global y di la incoherencia y su efecto medido en una línea.
- **H8 (BAJA)** — `tipo_cabezal` del cuadro resumen de la Fase 11 leído DEL PUNTO (`informe.cabezal.embocadura` / el tipo del
  cabezal del punto), no de la decisión única de la hoja de ruta. Es reporte (M11), sin aritmética. Mueve por TEXTO los CSV de
  resumen de la línea base: decláralo. Si resulta más que plomería de reporte, NO lo fuerces: ficha con símbolo y a T-12.
- **H9 (BAJA) — SE APLICA AHORA (decisión del dueño, 2026-11-13 ~20:05 UTC)**: en `cli.informe_json`, `HW_salida_m: null`
  cuando `perfil_sustituye_aproximacion` y `perfil_HW_remanso_m is None` (la aproximación descartada sigue publicada en
  `perfil_HW_aproximado_m`), y «salida: no se forma» (o la redacción que el código ya use en la línea «Perfil») en la línea
  «Control» del texto de la CLI. Es FORMATO, no cálculo: revisa TODOS los lectores de esa clave (comparador de E-B, barrido de
  PF-3, CSV de resumen, GUI, `tests/apoyo/*`, la validación de HY-8 de T-11, tests) para que un `null` no los rompa ni se lea
  como «cambio de HW». Mueve la línea base sólo en esa clave (A-02 y B-01 donde aplique) y en esa línea de texto: decláralo.
  **Condición**: el HW que gobierna, `HW_entrada_m`, diámetros, secciones y materiales no cambian; si el cambio mueve algo más
  que esa clave y esa línea, NO lo apliques, deja ficha con símbolo y repórtalo.
- **H10 (BAJA)** — fila A7 con `EstadoDeVerificacion.NO_APLICA` y su razón cuando E.060 no fija f'c mínimo. Es transparencia, no
  cálculo: ningún veredicto ni número cambia. Si rompe dorados de T-7c más allá de contar una fila, ficha y repórtalo.
- **H11, H12, H13, H14 (BAJA)** — como los propone el auditor (columna «consumidor» en el censo del §6; `TW_receptor` descrito como
  `servicio._resolver_tw` lo hace; `SIN_CONSUMIDOR_Y_SIN_MEDIDA` medido y nombrado, y el «ocho» de `CLAUDE.md` corregido al número
  real; `LEEME` rotulado en `tests/fixtures/corridas_de_referencia/hidrologia_calculada/`; textos falsos corregidos; porcentajes
  con dos decimales y tolerancia nombrada; fichas T11-03/04/05 al día; aserciones de los tests que digan lo que su nombre dice;
  marca `lento` sólo donde lo sea; la línea de plausibilidad de `Q_evento_extremo_m3s` y la frase de que con 2.0× A-01 pasa a
  Ø 1.05 m por V8; la cadena «caudal calculado → diseño» dicha como NO validada, con la propuesta de un juego de cuencas coherente
  para el lote posterior).

Para cada hallazgo: test que lo fija (rojo medido contra el árbol previo), corrección, y una línea «cerrado / en parte / refutado».

## PARTE 2 — integración
La de `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md`, sobre `origin/main` = `14f6138`, UN commit `tesis(T-11): …`. Además:
- **Tracker** (IDs canónicos; responsable «Claude Code (cadena T, T-11)»): `INF-0.5` → **Cerrado CON SALVEDAD escrita en la fila**
  (precedente `INF-4.2`): a perfil el fixture dimensiona sin declarar nada; a expediente, con todos los datos puestos, siguen
  deteniendo por DECISIÓN del dueño `remanso_derecho_via`, `TR_evento_extremo`, `umbral_no_colapso_evento_extremo` y
  `categoria_refuerzo_aashto` (si el tracker no admite la salvedad en «Cerrado», «Cerrado parcial»). `INF-3.4.3` → Cerrado (T-7b;
  verificado por T-11). `INF-3.4.4` → **Cerrado parcial** (residual: E4/E5 sin evaluar —T7B-07—, Meyerhof en talud vacío, zapata
  sin iterar —T7B-09—). `INF-3.4.6` → Cerrado con NOTA (con el `drenaje_trasdos` de archivo la sísmica no es evaluable, T7B-05).
  NOTAS en `INF-3.2.2` (validación HDS-5/HEC-14 generada; procedimiento HY-8 con la tolerancia aceptada por el dueño) e
  `INF-5.1.8` (estado real). Fila de T-11 en `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`.
- `docs/linea_base.md` y `CLAUDE.md` (punto 5 de T-11): párrafo de T-11 en el estilo de los existentes, tabla de pares («sí · no»
  MEDIDO con `NORMAS_DIR`; las otras tres derivadas), `collected`, cadena de totales, `-m pdf`, saltos sin `NORMAS_DIR`, «tres
  corridas de referencia», y lo que la corrección de T11-03 deja falso (p. ej. lo que dice de B-01).
- Línea base regenerada sobre el árbol final y medida contra `14f6138` con el comparador de E-B: cada diferencia clasificada en su
  README (T11-03: textos «no factible» y, si aplica, `delta_rasante_m`; H8: `tipo_cabezal`; alcance declarado). **«Diámetros /
  secciones / materiales / HW movidos: ninguno» o NO empujas a main.**
- Fichas de T-11 renumeradas a la Parte siguiente libre de `docs/decisiones_diferidas.md`; `docs/contrato_entradas.md` al día.
- Suite ENTERA verde con `NORMAS_DIR` y medida sin él; `git push origin HEAD:main` (fast-forward, nunca `--force`); confirma
  `origin/main == HEAD`; deja `tesis/T-11` en ese commit.

## Entrega
`SP/INFORME_T-11_final.md` (hallazgo por hallazgo; IDs; tests y pares; movidos con su causa; diferidos con símbolo; preguntas para
el dueño con recomendación; lo que NO hiciste; y una sección **«Lo que T-12 debe saber»**) y, como respuesta, MENOS DE 350
PALABRAS con el SHA en `origin/main`, el par, IDs, tests nuevos, movidos, diferidos y preguntas. No ejecutes T-12.
