# Encargo: T-7b (cabezal: estabilidad; V5 y V8) — correcciones de la auditoría adversarial + integración en main

Sigue `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (léelo primero, entero; donde dice base `df1b23c`, la de T-7b es `250c972`).
Worktree `/home/user/wt/T-7b`, rama `tesis/T-7b`, HEAD `fc792d9`; `origin/main` = `250c972` (nadie más empuja a main). Lee además
`ORQ/ENCARGO_T-7b.md`, `ORQ/PRECISIONES_T-7b.md`, `ORQ/INFORME_T-7b_faseA.md` y **`ORQ/AUDITORIA_T-7b.md`** (AJUSTADO: 3 ALTA,
4 MEDIA, 3 BAJA; la aritmética del ensamble coincide con AASHTO; «diámetros movidos: ninguno»). Te tocan TODOS sus hallazgos.
Los scripts con que el auditor midió cada cosa están en `ORQ/aud_T-7b_scripts/` (`cuna.py`, `nf.py`, `v5.py`/`v8.py` si están,
`sens1.py`, `a01.py`): son REFERENCIA validada, léelos; no los copies al repo tal cual.

## Resoluciones del orquestador (vinculantes; si el PDF contradice una premisa, gana la fuente y lo reportas)
- **H1 (ALTA, fórmula) — datum del nivel freático.** `NF_profundidad_m` se mide desde `punto.cota_terreno`, como en M8, el censo
  y el contrato de entradas. Pasa al `EntornoDelCabezal` la COTA del agua (`cota_terreno − NF`) y deriva de ella `h_w_natural` y
  `D_w` en `M9.cargas_del_cabezal` y `M9._empotramiento_delante`. Corrige el docstring, reescribe DECLARÁNDOLO el test que
  congelaba el defecto y añade un dorado a mano con pie ≠ terreno (salida de A-01: agua a 40.70 msnm, 0.20 m sobre la base).
- **H2 (ALTA, fórmula) — V5.** `embalse_a_nivel` mide HW/S_cauce hasta el FONDO: incluye el tramo natural del cauce y falla en
  falso (con los anchos de la Tabla 304.09 no puede cumplir). Lo que la fuente sostiene (HDS-5 núm. 2.2.5, págs. impresas 2.9–2.10 /
  PDF 71–72: verifícalo) es un criterio de COTA. Haz las dos cosas:
  (a) añade a la categoría de `remanso_derecho_via` el método **`cota_de_afectacion`**: cota del embalse (cota de fondo de entrada
      + HW de M4) ≤ cota de afectación aguas arriba, DATO EXTERNO por punto (`cota_afectacion_aguas_arriba_msnm`; opcional, sin
      valor por defecto; forma y dominio; `CLAVES_EXTERNAS`, pre-vuelo, `familias_que_usan` A y B; quién lo debe, a
      `docs/contrato_entradas.md`: es la cota del terreno o del bien a proteger en el límite del derecho de vía, de la topografía),
      con su cita de HDS-5 2.2.5 y su carácter; sin el dato → `DatoFaltanteError`; puede fallar de verdad;
  (b) conserva `embalse_a_nivel`, pero el paso, el criterio y la ficha T7B-01 dicen sin rodeos que d incluye el tramo natural
      del cauce (cota SUPERIOR de la extensión del embalse atribuible a la obra), que con los anchos normativos sólo cumple en
      cauces de pendiente fuerte, y que restar el tirante natural exige la sección del cauce, que no es dato de entrada (diferido).
  El criterio sigue SIN valor de archivo (sin declararlo todo queda como hoy). El test de punta a punta pasa a usar
  `cota_de_afectacion` con una cota de prueba rotulada (no un derecho de vía de 400 m).
- **H3 (ALTA) — V8.** (1) `EventoExtremoDelPunto.resolver` deja de devolver «no evaluable» cuando el caudal extremo no cabe en
  lámina libre: calcula el HW con el barril trabajando a presión con lo que M4 YA tiene (control de entrada sumergido y control
  de salida a barril lleno; no escribas ecuaciones nuevas: reutiliza las de M4 y di cuál gobierna); si de verdad queda fuera del
  dominio de las cartas, `MetodoNoEvaluableError` con el rótulo de HDS-5. (2) V8 se evalúa sólo sobre el candidato que ya cumple
  todo lo anterior (no enmascara un V1 o V5 incumplido) y el mensaje no llama «adoptada» a una sección candidata. (3) Barrido del
  auditor (Q_ext ×1.11 … ×1.97 en A-01) como test: di en cuáles cumple, en cuáles no y por qué. Ningún resultado del fixture sin
  declarar puede cambiar.
- **H4 + pregunta 3 (fórmula) — cuña de tanteo.** Implementa en `M9.cargas_del_cabezal` el empuje por **cuña de tanteo de
  Coulomb/Culmann sobre el plano del talón con la superficie REAL del relleno** (talud que sube y se quiebra en la plataforma),
  estática y sísmica (pseudoestática con k_h, k_v), como opción de `regla_pendiente_relleno_trasdos` y como **valor de archivo**:
  es lo que la fuente pide para geometrías que se apartan de Coulomb (AASHTO 3.11.5.3 «…Culmann method», 3.11.5.8.1 «Coulomb
  trial wedge», C11.6.5.3 para el sismo: verifica los tres literales y cítalos con su carácter). La «pendiente equivalente 2H»
  queda como alternativa barrible con su sesgo dicho (subestima 7–11 % en A-01). Referencia validada: `ORQ/aud_T-7b_scripts/cuna.py`
  (coincide con Coulomb en talud infinito y con Mononobe-Okabe en relleno horizontal a 1e-8). Oráculos del auditor para A-01 con
  los datos de prueba: estático 16.95 kN/m (entrada) y 28.61 (salida); sísmico k_h 0.25: 30.58 y 50.85; **k_h 0.50: 59.7 y 98.2
  kN/m (cifra finita: la sísmica deja de ser «no evaluable» con el k_h de archivo)**. Tus dorados: esos dos límites analíticos
  (Coulomb, M-O) más un caso de superficie quebrada resuelto a mano con dos o tres cuñas escritas. Punto de aplicación y
  descomposición: como hoy, dicho en el paso. Mononobe-Okabe cerrado queda como contraste impreso donde sea evaluable. Guardias
  MAT-D13 (cuña sin máximo, superficie degenerada → `LimiteNumericoError`/`MetodoNoEvaluableError`, nunca una cifra).
  **`factor_muro_eleccion` NO cambia de valor de archivo** (la reducción de k_h por desplazamiento sigue siendo una declaración
  del Propietario, 11.6.5.2.2).
- **H5 + pregunta 5 — fila de φ y el incumplimiento del cabezal de la regla.** Se mantiene de archivo `zapatas_seccion_10`
  (0.45 / 0.80), justificada como LA MÁS EXIGENTE y la que el Manual de Puentes peruano transcribe —no como «la tabla 11.5.7-1
  remite a la Sección 10», que es inexacto: la letra de AASHTO 11.5.7 («shall be used for wall design») da 0.55 / 1.0 para muros
  de gravedad y semigravedad; dilo así en el criterio y en la ficha—. Cuando el veredicto de una fila cambia entre opciones de la
  ventana (fila de φ; factores de inclinación), AVISO por `avisos()` que lo diga con las dos cifras. La ficha T7B-09 y la memoria
  presentan el «cabezal de la regla no pasa» como sensible a esas dos elecciones [A] y a datos de prueba. **NO iteres el ancho de
  la zapata** (pregunta 2: diferido con ficha; el proyectista cierra con `cabezal_declarado`); recalcula y reporta cómo quedan las
  doce filas de A-01 con el modelo corregido (H1, H4, H6).
- **H6 + pregunta 1 — agua.** `drenaje_trasdos` se queda en **`sin_drenaje`** de archivo (AASHTO 11.6.6: «shall be drained or, if
  drainage cannot be provided… full hydrostatic pressure»; `drenado` es una declaración que compromete los planos: dilo así y di
  cómo se declara). Corrige el tope del agua con `sin_drenaje` (hasta el relleno retenido / la coronación, nunca por encima del
  muro) y unifica la redacción con `HIPOTESIS_EMPUJE_BAJO_NF`. Con `drenado`: aviso y ficha de que el modelo toma sólo el freático
  natural y NO el desembalse rápido tras la avenida (relleno mojado hasta HW con el cauce vacío; C11.6.6: los lloraderos no
  aseguran el drenaje), con el orden de magnitud del auditor.
- **H7 — muro no cedente.** Régimen del cabezal como criterio [A] categórico (`cedente` / `no_cedente`; valor de archivo
  `cedente` para la estabilidad EXTERNA, que es lo que el ensamble calcula, declarado como hipótesis de modelación con las citas
  de 11.6.5.4 y su comentario), y `M9.solicitaciones_por_elemento` MARCA para T-7c con qué coeficiente salen los empujes (K_A hoy)
  y que con muro no cedente el diseño de resistencia iría con K0 (+52 % en A-01): campo explícito en la interfaz y ficha.
- **H8, H9, H10 (BAJA)**: aplícalos (textos que contradicen al código; aviso de aleros desproporcionados cuando α + θ se acerca a
  90° —umbral como [A] con ventana o comparación con una magnitud ya existente, sin número suelto—; la aserción tautológica del
  contraste con VARIOS).
- **Preguntas 4 y 6**: `terreno_delante_del_cabezal = horizontal` y V8 «sin desborde de la plataforma» se mantienen.
- **Tracker**: `INF-4.4`, `INF-4.5`, `INF-5.1.5` cerrados; `INF-4.2` cerrado CON LA SALVEDAD escrita (la ruta real a la Fase 9
  exige declarar el método de V5 y sus datos, TR y Q del evento extremo y el EMS: entradas del proyecto); `INF-4.3` en parte
  (T7A-03); `INF-4.1` cerrado si los datos por punto entran como dice el informe (decídelo con la evidencia y dilo); `EXT-7-02`,
  `EXT-7-04` cerrados; notas en `INF-0.5`, `EXT-N-04`, `SIS-F-15`, `T1-03`. La v8: corrige el rótulo E.050 [N] de §0.1 y §9.3
  (ficha T7A-08) y lo que la §9 diga del método de V5.

## Integración — lo específico de T-7b
Censos esperables tras tus correcciones: criterios 128 + los que añadas; `CLAVES_EXTERNAS` 24 + 1. Línea base contra `250c972`:
sólo textos, huellas, recuentos y lo que el informe §4 declara (bloqueo «K_AE (9.2)» del proyecto que desaparece; pre-vuelo de
expediente con `NF_profundidad_m` de «espera» a «DETIENE»). **Diámetros, secciones, materiales y HW: ninguno.**
Commit: `tesis(T-7b): cabezal — ensamble de estabilidad en dos marcos … — INF-4.4, INF-4.5, INF-5.1.5, INF-4.2 (cerrados); INF-4.3 (en parte); EXT-7-02, EXT-7-04`.
Deja dicho en tu informe, para T-7c: la interfaz `solicitaciones_por_elemento` (campos, unidades, combinaciones, régimen).

Entrega: `SP/INFORME_T-7b_final.md` + resumen < 350 palabras (SHA en `origin/main`, par con y sin `NORMAS_DIR`, IDs, tests
nuevos, cómo quedan las doce filas LRFD de A-01, movidos, diferidos, preguntas para el dueño).
