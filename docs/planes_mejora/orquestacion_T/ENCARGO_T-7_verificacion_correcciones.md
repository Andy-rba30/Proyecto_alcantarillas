# Encargo: correcciones de la VERIFICACIÓN Fable de los cierres de T-7b y T-7c — implementación e integración en main (Fable)

Worktree `/home/user/wt/T-7v`, rama `tesis/T-7-verificacion`, desde `origin/main` = `2b13dc1` (par con `NORMAS_DIR` 6253 passed /
23 skipped / 6276 collected; sin él 6235 / 41). En paralelo otro agente hace T-10 (memoria, M11) en `/home/user/wt/T-10`: NO lo
toques; él rebasará sobre tu commit. `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/` (sólo lectura);
`SP` = `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/` (temporales en `SP/T-7v/`).

SÉ ECONÓMICO: lee sólo `ORQ/VERIFICACION_T-7_fable.md` ENTERO (tu lista de trabajo: trae la corrección por símbolo y los valores
de control), de `CLAUDE.md` las secciones «Fuente de verdad», «Taxonomía de etiquetas», «Arquitectura», «Excepciones»,
«Cierre de tarea» y el párrafo más reciente de la cadena T (modelo de estilo y censos vigentes), y de `ORQ/ORQUESTACION.md` las
«Reglas no negociables», «Git» y la ENMIENDA DE LA CUARTA SESIÓN. Lo demás, por símbolo y bajo demanda.

## Qué corregir (tres defectos; los seis puntos CONFORMES no se tocan)
1. **Punto 3 — V8 con el barril a presión (MEDIA, lado inseguro).** En `M4.hidraulica_a_presion`, cuando gobierne la salida:
   con `salida.HW_sobre_D` < 1.2 (la banda de cautela de E-A) no se entrega menos carga que la de lámina libre del mismo punto, y
   se AVISA; por debajo de `H_O_HW_SOBRE_D_MIN` (0.75) la aproximación no vale: `MetodoNoEvaluableError` con el rótulo de HDS-5
   (o aviso expreso si la fuente lo permite: decide con la pág. 3.24 de HDS-5 y dilo). En `M5.v8_evento_extremo`: guardia
   `HW_ext ≥ resultado.HW − tolerancia` (un caudal mayor no puede dar menos carga), con aviso por `avisos()` si se acota.
   Control (tubo de A-01, S 0.003, L 60 m, TW 0): HW_ext(Q = 1.0213) ≥ 0.9654 m. A-01 del fixture no cambia (1.588 m; 43.69 msnm).
2. **Punto 9 — η de AASHTO 1.3.2.1 en el cabezal (MEDIA).** El conducto del mismo cruce lleva η_I = 1.05 ([A] del Propietario,
   `eta_importancia_operativa_conducto`, T-5) y el cabezal usa 1.00 implícito. Aplícalo: la clasificación de importancia es del
   CRUCE, así que el cabezal lee el MISMO criterio (una decisión, un valor: no dupliques el número; si el nombre del criterio
   dice «conducto», ajusta concepto/justificación para que diga que rige el cruce, o añade un criterio propio del cabezal sólo
   si la fuente obliga a separarlos, y dilo); η_D y η_R del cabezal como elección declarada (1.00 convencional por 1.3.3 y 1.3.4:
   verifica los literales en el PDF, págs. PDF 18, 21, 22, y cítalos). En `M9.combinaciones_de_estabilidad` y
   `M9._combinaciones_en_reposo`: η en γ máximo, 1/η en γ mínimo, 1.00 en Evento Extremo I y en Servicio (ec. 1.3.2.1-2 y -3).
   Rige en los DOS usos (estabilidad LRFD y armado); el marco ASD de E.050 no lleva η. Paso de memoria que lo diga con su cita.
   Control: talón de salida de A-01 (datos de prueba) M_u 71.72 → 75.31 kN·m/m → Ø 1/2" @ 0.15. Rehaz A MANO los dorados que
   cambian (22 según la ficha T7C-11) DECLARÁNDOLO en cada test, y di cómo quedan las doce filas E1–E3 de A-01 y su armado.
   La ficha T7C-11 pasa a cerrada.
3. **Punto 7 — piso del espesor de la zapata armada (BAJA en severidad, pero la regla no puede cumplir nunca la norma que cita).**
   E.060 15.7 (pág. 138) pide ≥ 300 mm SOBRE el refuerzo inferior. `M9.peralte_minimo_zapata` (T-7a) da 0.30 + 0.070 = 0.37 m, y
   la fila A8 del armado mide 0.272 m con el recubrimiento de cota y 0.2937 m aun con categorías B/C: A8 no cumple en ningún
   cabezal de regla. Corrige la REGLA: espesor ≥ 0.30 + recubrimiento con que se arma (el de `recubrimiento_para_armar`: la cota
   de 91.44 mm mientras falte el dato) + medio diámetro de barra (lado seguro: la mayor barra del catálogo de propuesta, o lo que
   sea coherente con cómo A8 mide; dilo), [N→] por analogía como ya está rotulado, sin redondeos no declarados. Con eso A8 CUMPLE
   por construcción en un cabezal de regla y sigue pudiendo FALLAR con una zapata declarada más delgada. Corrige la nota de A8 y
   el texto falso («con 50.8 mm cumpliría»), imprime la lectura que la fila usa (cara / eje de la barra) y decláralo. Esto MUEVE
   la geometría del cabezal (zapata de A-01: 0.37 → ≈ 0.40 m) y con ella los números de estabilidad y de armado de los datos de
   prueba: rehaz a mano los dorados afectados (los mismos que toca η: una sola pasada), DECLARÁNDOLO. No mueve ningún diámetro,
   sección, material ni HW del conducto.
- Además: matiz de texto del punto 2 (la nota de V5 «el nivel más alto del embalse (en la boca)» vale sólo para el embalse a nivel).

## Reglas
Toda cita o número nuevo verificado contra el PDF; dorados a mano con la aritmética escrita; tests primero en rojo
(`xfail(strict=True)`) o rojo medido contra `2b13dc1` y declarado; ningún diámetro, sección, material ni HW del fixture se mueve
(compruébalo con el comparador de E-B sobre `tests/linea_base_familia_c/`: sólo huellas, recuentos y notas); excepciones dentro
de `ErrorProyecto`; avisos por `InformePunto.avisos()`; todo en SI; nunca `/dev/null` como destino de `cli.py --json`.
Commits `wip` con `git push origin tesis/T-7-verificacion` tras cada bloque (puede haber cortes: di qué falta).

## Integración (tú mismo, al terminar)
UN commit sobre `origin/main`: `tesis(T-7): verificacion de formulas de los cierres de T-7b y T-7c — V8 a presion no entrega
menos carga que la lamina libre; eta del cruce en el cabezal (AASHTO 1.3.2.1); piso de la zapata armada por E.060 15.7 — …`.
Ritual acotado: censos que cambien (criterios, literales, fundamentos), fichas (`docs/decisiones_diferidas.md`: T7C-11 cerrada;
T7B-02 y la de A8 al día; Parte nueva si hace falta), tracker `.xlsx` (notas en `INF-4.5`, `INF-4.6`, `INF-4.2`; responsable
«Claude Code (cadena T, T-7)»), fila en `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT` si el test la exige, línea base
regenerada y clasificada en su README, los generados resellados (`python3 -m src.normativa.manifiesto --escribir --suite "<par>"`,
`python3 -m src.indice_formulas …`), `CLAUDE.md` (párrafo corto de esta pasada, suma de tests, tabla de pares —«sí · no» MEDIDO con
`NORMAS_DIR`, las otras tres DERIVADAS—, `collected`, cadena de totales). Suite ENTERA verde con
`NORMAS_DIR=/home/user/andy-rba30/normas` y medida también sin él; `git push origin HEAD:main` (fast-forward; nunca `--force`);
confirma `origin/main == HEAD`; deja la rama empujada ahí. Pie de los commits:

    Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01Jteyqg5CzW7hzPFvqiat9M

Ningún identificador de modelo en otro sitio del repo.

## Entrega
`SP/INFORME_T-7_verificacion.md` y, como respuesta, MENOS DE 300 PALABRAS: SHA en `origin/main`, par con y sin `NORMAS_DIR`,
qué quedó de cada uno de los tres puntos, las doce filas E1–E3 y el armado de A-01 con los datos de prueba (antes → después),
«diámetros/secciones/materiales/HW movidos: ninguno», lo que NO hiciste.
