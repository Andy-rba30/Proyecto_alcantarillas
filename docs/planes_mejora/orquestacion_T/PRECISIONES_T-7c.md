# Precisiones del orquestador para T-7c (cabezal: armado o concreto ciclópeo) — cuarta sesión

Base: `origin/main` con T-7b integrado (el orquestador te da el SHA). Lee `ORQ/ORQUESTACION.md` (con su ENMIENDA DE LA CUARTA
SESIÓN), `ORQ/INFORME_T-7b_final.md` ENTERO (trae la interfaz `M9.solicitaciones_por_elemento`: campos, unidades, combinaciones,
régimen del muro), `ORQ/AUDITORIA_T-7b.md` (H7), `ORQ/AUDITORIA_T-7a.md` (H7, dudoso 4), `ORQ/DICTAMEN_marco_cabezal.md` y la
sección «Cuarta sesión» de `ORQ/DECISIONES_DUENO_2026-11-12.md`.

- **IDs canónicos**: `INF-4.6`; la ficha `EXT-7-01` de `docs/decisiones_diferidas.md` (ec. (11-32) de E.060 y las cuantías; el
  cierre de C07 dejó tres criterios de cortante alto vacíos); el `NotImplementedError` de `M9.diseno_flexion_corte`; y la pregunta
  que T-7a dejó para ti: el rótulo por ÁMBITO de E.060 22.7.4 (y de todo artículo de E.060 que uses).
- **Qué norma arma (resolución del orquestador, coherente con la decisión del dueño sobre el marco de T-7b: rige LRFD de
  AASHTO)**: las solicitaciones que recibes son las FACTORADAS de AASHTO (Resistencia I y Evento Extremo I) → la resistencia se
  verifica con **AASHTO LRFD Sección 5** (5.6 flexión; 5.7 cortante, método simplificado β = 2, θ = 45° donde el 5.7.3.4.1 lo
  permite: verifica sus condiciones en el PDF; φ de 5.5.4.2). Nunca combines cargas factoradas de AASHTO con φ de E.060 ni al
  revés (misma regla de no cruce que T-7b). **E.060 se calcula e imprime EN PARALELO como contraste [N→]** (su ámbito son las
  edificaciones del RNE; para un cabezal vial es por analogía, como E.050): cuantías mínimas de muros (cap. 14), cortante en
  muros (11.10, con la ec. 11-32 y sus topes: los tres criterios vacíos reciben su valor del numeral, verificado), recubrimiento
  (7.7.1), mínimos de zapata (15.7), concreto simple (cap. 22). En los MÍNIMOS constructivos (cuantía mínima, espaciamiento
  máximo, recubrimiento, espesores) rige el más exigente de los dos, declarado como [A] con su justificación; en resistencia rige
  AASHTO. Si al leer las dos fuentes ves que esta resolución no se sostiene, NO la fuerces: implementa lo que la fuente sostiene y
  devuelve la pregunta con las opciones.
- **Régimen del muro (H7 de la auditoría de T-7b)**: el ensamble de estabilidad externa va con K_A (muro cedente, hipótesis
  declarada). Para el DISEÑO DE RESISTENCIA de la pantalla, AASHTO 11.6.5.4 y su comentario dicen que un muro que no puede ceder
  (el cabezal monolítico con barril y aleros se le parece) se diseña con K0 y con la resultante más alta. Lee el criterio de
  régimen que T-7b dejó y la marca de la interfaz: arma con el régimen declarado y **imprime al lado la solicitación con K0**
  (contraste; +52 % en A-01 según el auditor) con aviso por `avisos()` cuando cambie el armado. No elijas tú el régimen de archivo.
- **Elementos**: pantalla y zapata (punta y talón) como vigas de 1 m. Los ALEROS: di qué hace el programa con ellos (muro en
  voladizo de altura variable: sección crítica en el arranque) o difiérelos con ficha y símbolo; no los dejes en silencio.
- **Ciclópeo**: con D ≥ 0.90 m todo cabezal de la obra sale voladizo armado (la rama de gravedad sólo se alcanza declarando
  `altura_max_gravedad_m` o el tipo en `cabezal_declarado`): implementa la alternativa igualmente, probada por esa puerta, y dilo.
- **El cabezal de la regla de T-7a puede NO pasar estabilidad** (ficha T7B-09; la iteración del ancho de zapata está diferida): tú
  armas la geometría que recibes, pase o no, y lo dices; no iteres dimensiones.
- **Barras y espaciamientos «propuestos»**: catálogo [A] con ventana (diámetros comerciales); el programa propone, no impone.
  `categoria_refuerzo_aashto` y `exposicion_quimica_ems` son entradas [S] SIN valor por defecto silencioso: lee cómo están hoy y
  qué dice el prompt («valor por defecto NO»): si eso equivale a rellenar un dato de sitio, déjalo como dato que falta con el
  recubrimiento más exigente aplicable como cota conservadora declarada, y repórtalo.
- **Unidades**: todo en SI. Las ecuaciones de AASHTO en ksi-pulgadas se convierten en la constante (sufijo `_SI`, con el valor
  imperial en el comentario), nunca en la llamada. El procedimiento MCFT transcrito en ksi-pulgadas: se retira o queda como
  referencia NO ejecutable con nota, como dice el prompt.
- **Añadido para tu auditor** (no para ti): revisará también la cuña de tanteo que las correcciones de T-7b dejaron en
  `M9.cargas_del_cabezal`.

Reglas de siempre: PARADA (c) (ningún diámetro, sección, material ni HW del fixture se mueve); excepciones dentro de
`ErrorProyecto` y como `Bloqueo` del punto; nivel EXPEDIENTE; avisos por `InformePunto.avisos()`; M11 sin aritmética; dorados a
mano; tests primero en rojo o rojo medido y declarado; mutación con el arnés sobre lo nuevo; ruta real de expediente con los
datos de prueba rotulados de T-7b.

## Añadido al lanzar (2026-11-13): base y régimen
- **Base**: `origin/main` = `451a10a` (T-7b integrado; par con `NORMAS_DIR` 5979 passed / 23 skipped / 6002 collected; sin él
  5961 / 41). Worktree `/home/user/wt/T-7c`, rama `tesis/T-7c`.
- **Régimen para el DISEÑO DE RESISTENCIA de los elementos (decisión delegada por el dueño: «sigue con tus recomendaciones»)**:
  se ARMA con **K0** (muro que no puede ceder: el cabezal es monolítico con el barril y con los aleros; AASHTO 11.6.5.4 y su
  comentario: verifica el literal y su carácter) como valor de archivo de un criterio [A] PROPIO de la resistencia de los
  elementos, con `cedente` (K_A / K_AE, lo que entrega hoy la interfaz) como alternativa barrible e IMPRESA al lado como
  contraste. La estabilidad externa de T-7b NO cambia (sigue con K_A, hipótesis declarada en su criterio). La interfaz
  `solicitaciones` ya trae `K0` y `K0_sobre_K_A` por sección: di exactamente cómo escalas (qué parte de V_u y M_u es empuje de
  tierra y cuál no: el peso, la sobrecarga viva y el agua no se multiplican por el cociente a ciegas) y fíjalo con un dorado a
  mano. En sismo no inventes un K0 sísmico: di qué sostiene la fuente y, si no da método, arma el Evento Extremo con lo que la
  interfaz entrega y avísalo.
- El dueño confirmó además: NO se itera el ancho de la zapata (se espera al EMS real); el cabezal de la regla puede no pasar
  estabilidad y se arma igual, diciéndolo.
