# Encargo: T-7a (cabezal: geometría por punto y aleros) — correcciones de la auditoría adversarial; la integración va DESPUÉS de T-3 y T-9

Sigue `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (léelo primero, entero). Worktree `/home/user/wt/T-7a`, rama `tesis/T-7a`,
HEAD `1b83d39`, base `df1b23c`. Auditoría: `ORQ/AUDITORIA_T-7a.md` (AJUSTADO: 2 ALTA, 6 MEDIA, 2 BAJA; «diámetros movidos:
ninguno»; trae el veredicto sobre las cuatro decisiones del dueño y los riesgos de integración). Te tocan TODOS sus hallazgos.

**AHORA haz sólo la PARTE 1 (correcciones en tu rama, tests afectados y UNA suite entera verde al final, push a
`origin tesis/T-7a`) y PÁRATE con un informe corto.** El orquestador te escribirá «integra» cuando `origin/main` tenga los
commits `tesis(T-3)` y `tesis(T-9)`; entonces haces la PARTE 2.

## Resoluciones del orquestador (vinculantes; si el PDF contradice una premisa, gana la fuente y lo reportas)
- **H1 (ALTA, fórmula) — los aleros con esviaje.** La convención se confirma: α se mide con la prolongación de la pared del
  barril (HDS-5 3.ª ed., List of Symbols, pág. impresa xix / PDF 23: «ΘW Flare angle of wingwalls with respect to extension of
  culvert side wall»: transcríbela al registro y cítala; por eso es cos y no sen). Pero el talud baja PERPENDICULAR A LA VÍA (así
  lo modela `M7.longitud_conducto`), y el eje forma θ (esviaje) con esa dirección: un alero forma α − θ con la bajada del talud y
  el otro α + θ. Por tanto, con el cabezal normal al eje:
  `L_corto = (h0 − H_f)·talud / cos(α − θ)` y `L_largo = (h0 − H_f)·talud / cos(α + θ)` (θ en valor absoluto; con θ = 0 las dos
  dan la de hoy). `M9.predimensionar_aleros` recibe el esviaje y `Aleros` lleva las DOS longitudes; si el CSV no trae el sentido
  de giro del esviaje (sólo magnitud), se llaman «corto» y «largo» y el paso dice que el lado lo fija la planta. Guardia MAT-D13:
  `not (cos(α + θ) > TOL)` → `LimiteNumericoError` con el par culpable (α, θ) y lo que lo resuelve (declarar los aleros por
  `cabezal_declarado` o un α menor dentro de la ventana): el alero de ese lado no alcanza nunca la altura final. Dorado a mano
  (A-01: θ 15°, α 45°, talud 2.0, h0 − H_f = 1.05 m → 2.1/cos 30° = 2.425 m y 2.1/cos 60° = 4.200 m; C-01: θ 30°). Paso 9.0.3 con
  θ en la sustitución; `F9.ALEROS` sin «avanza en la dirección del eje»; quita «los aleros absorben el giro» del docstring y di
  lo que SÍ ocurre: un cabezal normal al eje queda con el talud a cotas distintas en sus dos extremos, Δz = L_c·sen θ/talud
  (imprímelo como aviso cuando θ ≠ 0). El cabezal paralelo a la vía (esviado; Carta 11) queda como alternativa diferida en la
  ficha T7A-03, que además avisa a T-7b del acoplamiento con `orientacion_muro_respecto_al_trafico`.
- **H2 (ALTA) — la decisión 4 del dueño NO se aplica: su premisa quedó refutada.** NO abras la puerta de `ancho_derecho_via_m`
  (un dato sin lector no se abre). Reescribe la ficha T7A-01 con las tres capas que el auditor midió (criterio vacío
  `remanso_derecho_via`; `M5.v5_remanso` que no lee el dato porque no hay método; V8 con `TR_evento_extremo` y el caudal del
  evento extremo), di que hoy ningún test recorre la Fase 9 por la ruta real de expediente, y deja escrito lo que la cerraría
  (método de V5 + dato + TR y Q de V8). En tus filas del tracker **`INF-4.2` e `INF-4.3` quedan «en parte»** (función, memoria y
  tests sobre `servicio._fase_9`; residual: alcanzable a expediente, ficha T7A-01); `INF-5.1.15`, `INF-3.4.1` e `INF-3.4.2` como
  los propuso la FASE A si H1 queda cerrado. El orquestador llevará el método de V5 a un prompt posterior.
- **H3 — dentellón de la Lámina Nº 04** (confirmado por el orquestador sobre el recorte a 300 dpi): el «0.80 min.» se mide desde
  el TERRENO al borde de la losa (cara inferior del paquete losa + granular) hasta la base del dentellón, no desde la cara
  superior de la losa. Usa UNA referencia de terreno por extremo —la misma de `ExtremoDelConducto.cota_pie`— para desplante,
  losa y dentellón (en la salida de A-01 hoy la base del dentellón queda sólo 0.11 m bajo el lecho receptor). Corrige la `nota`
  de `MC_HHD.LAMINA_04#DENTELLON` y `LosaDeEntrega.profundidad_dentellon`.
- **H4**: CB6 (zapata de gravedad declarada ≥ mínimo de E.060 22.7.4) y CB7 (dentellón ≥ mínimo del criterio y base por DEBAJO
  del fondo de la hoya cuando la hay: AASHTO 12.6.5 dice «extending below»), con `_verificacion_cb`; pueden fallar de verdad.
- **H5**: los tests que el auditor pide (hoya real de `M6.socavacion_salida` por la ruta de `servicio._fase_9` con D_f, CB5 y
  dentellón a mano; CB5 fallando; `altura_total_m` declarada; marco de dos celdas; frontera de CB2; rama «método distinto de por
  extremo»). Mata los mutantes vivos que importan.
- **H6 — longitud entre cabezales**: el talud muere en el RELLENO retenido (coronación − bordillo), no en la corona del bordillo:
  A-01 → 13.486 m (y no 12.865). Declara la cara de medida y da aparte la de metrado (suma el espesor de los dos muros sobre el
  eje). Corrige «milímetros» (son centímetros). Revisa con el mismo criterio el h0 de `predimensionar_aleros` y di qué nivel usa
  y por qué (si queda el mayor, dilo como lado de más longitud, no como geometría exacta).
- **H7**: di en la ficha T7A-04 y en un aviso que el umbral «gravedad hasta 2.0 m» se mide sobre la altura TOTAL (con desplante)
  y que con D ≥ 0.90 m no se alcanza (todo cabezal de la obra sale voladizo armado); nombra E.060 22.10.2.1–22.10.2.2 (verifica
  pág. 195) como límite del ciclópeo. No cambies el umbral ni su referencia: queda como alternativa en la ventana.
- **H8 (dudoso 1) — E.050 26.2 es [N→], no [N]**, coherente con `ORQ/DICTAMEN_marco_cabezal.md` (el ámbito de la E.050 son las
  edificaciones del RNE; para un cabezal vial se aplica POR ANALOGÍA; 39.13.7 → Cap. IV es lo que hace cercana la analogía):
  `PROFUNDIDAD_CIMENTACION_MIN_M` sale de `constantes_normativas.py` y pasa a criterio [N→] con la analogía declarada; CB4 dice
  «por analogía», no «EXIGENCIA de E.050» a secas. Reporta el rótulo [N] de la tabla §0.1 de la v8 como defecto de la hoja.
- **Dudoso 3 — AASHTO 12.6.5 «footings of structures»**: `margen_zapata_bajo_socavacion_m` sigue [C], con una `Interpretacion`
  explícita: la fuente habla de las zapatas de la estructura enterrada; el proyecto LEE incluida la zapata del cabezal (lado seguro).
- **Dudoso 4 — piso de la zapata ARMADA**: verifica el literal de E.060 15.7 (pág. 138: altura de la zapata sobre el refuerzo
  inferior ≥ 300 mm) y, si lo dice, la regla pasa a `e_z = max(H/divisor, piso)` con el piso [N→] (300 mm sobre el refuerzo más el
  recubrimiento contra el suelo de E.060 7.7.1, verificado), declarado como mínimo por analogía; si el literal no lo sostiene,
  déjalo como está y repórtalo. (En la entrada de A-01 hoy sale 0.225 m.)
- **Dudoso 5**: «H/8–H/6» sigue [A]; la ficha dice que su origen (VARIOS p. 42) no se pudo verificar en esta sesión.
- **H9 (todos sus ítems) y H10**: aplícalos. En H10: ninguna frase puede decir o sugerir que «más material» es el lado seguro
  (con kh = 0.50 y μ < kh más masa empeora el deslizamiento sísmico): dilo así en la ficha T7A-04; lo evalúa T-7b.
- **Decisiones del dueño**: 1 (cos α) confirmada y completada con H1; 2 (pie de salida en la más baja) se mantiene con la
  referencia única de H3; 3 (caja receptora sin aleros, Lámina 02-A) se mantiene, y el residual se AVISA: la entrada de un alivio
  de cuneta (Familia B) suele ser caja receptora, que el programa no modela (hoy recibe cabezal con aleros): aviso en los puntos
  B y ficha; 4 NO se aplica (H2).
- La embocadura del marco es la de aletas 30–75° que T-3 deja con valor de archivo (se integra antes): tu coherencia
  embocadura ↔ ke ↔ carta debe darla por buena con α entre 30° y 60° y decirlo sin ruido (la nota de coherencia no debe salir como
  aviso permanente si no hay incoherencia).

## Para la PARTE 2 (cuando se te diga «integra»)
Riesgos: los de la sección «Riesgos de integración» de la auditoría (`servicio.correr_punto`: `_fase_9` detrás de
`_fase_6_socavacion` y de la Fase 8; `M6.proteccion_entrada` y `tests/test_t8_proteccion.py` reescritos en main por las
correcciones de T-8; techos de `test_ext8` REMEDIDOS; censos; tu Parte de `decisiones_diferidas.md` renumerada). Commit:
`tesis(T-7a): cabezal — geometria por punto y aleros … — INF-5.1.15, INF-3.4.1, INF-3.4.2 (cerrados); INF-4.2, INF-4.3, INF-4.1 (en parte)`.

Entrega de la PARTE 1: `SP/INFORME_T-7a_correcciones.md` + resumen < 300 palabras (hallazgo por hallazgo, tests nuevos y par de
la rama, «diámetros movidos: ninguno» o la lista, SHA de la rama, preguntas para el dueño).
