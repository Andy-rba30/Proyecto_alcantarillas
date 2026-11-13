# Encargo: T-9 (espaciamiento de alivios, Fase 10) — correcciones de la auditoría adversarial; la integración va DESPUÉS de T-3

Sigue `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (léelo primero, entero). Worktree `/home/user/wt/T-9`, rama `tesis/T-9`,
HEAD `304cea6`, base `df1b23c`. Auditoría: `ORQ/AUDITORIA_T-9.md` (AJUSTADO: 1 ALTA, 4 MEDIA, 6 BAJA; «diámetros movidos:
ninguno»; trae las respuestas A–D sobre las decisiones del dueño y los riesgos de rebase). Te tocan TODOS sus hallazgos.

**AHORA haz sólo la PARTE 1 (correcciones en tu rama, suite afectada verde, push a `origin tesis/T-9`) y PÁRATE con un informe
corto.** T-3 se está integrando en `main` en este momento y T-9 va detrás: el orquestador te escribirá «integra» cuando
`origin/main` tenga el commit `tesis(T-3)`; entonces haces la PARTE 2 (rebase sobre ese `origin/main`, ritual entero, push).

## Resoluciones del orquestador (vinculantes; si el PDF contradice una premisa, gana la fuente y lo reportas)
- **H1 (ALTA, fórmula) — la condición literal del Manual manda.** El Manual (núm. 4.1.2.1 a), págs. impresas 176–177 / PDF
  179–180: «si Q manning > Q de aporte … el diseño está terminado») compara la CAPACIDAD de la cuneta con el caudal de APORTE.
  Por contrato, en la Familia B `Q_m3s` es el caudal de la cuneta que descarga en el alivio. Entonces:
  1. Siempre que existan el caudal del punto (declarado o calculado) y la capacidad (`CapacidadCuneta.Q_admisible_m3s`), la
     Fase 10 VERIFICA `Q_aporte ≤ Q_adm`, y puede FALLAR (NO_CUMPLE que llega a `incumplidas()`, RESUMEN, CLI, JSON y memoria):
     como condición dentro de VB1 o como verificación propia de la Fase 10 (VB2) que entra a la aceptación de la Familia B junto
     a VB1 —elige la forma más limpia y dila—. El caso del auditor (0.20 × 0.50, Z2 0.5, concreto, S 0.005, b 12, Q 0.095 →
     Q_adm 0.0522 m³/s) debe dar NO CUMPLE: es tu test en rojo, con su aritmética a mano.
  2. Aporte por metro q' para la longitud hidráulica: con el TRAMO conocido (longitud s entre extremos), q' = Q/s (aporte
     uniforme a lo largo del tramo real) y L_h = Q_adm·s/Q —equivalente exacto de la condición literal—, sin mezclar `area_ha`
     con `ancho_tributario_m`. Con el tramo NO conocido, se conserva q' = (Q/`area_ha`)·b, pero el paso imprime la longitud que
     ese par implica, s_impl = `area_ha`·10⁴/b, y AVISA (por `avisos()`) cuando s_impl supera la longitud máxima normativa del
     tramo: el área declarada no es la faja b × tramo y la L calculada no es fiable (en B-01: 18 ha / 12 m = 15 000 m). Sin
     tolerancia inventada: la comparación es contra `long_max_cuneta`. Con el caudal CALCULADO por la Fase 1-bis
     (`caudal_de_aporte_cuneta`) sigue el camino de hoy (q del racional por b).
  3. `L_hidraulico_m` declarado sigue ganando para la longitud; la condición 1 se evalúa igual si hay con qué, y si no hay
     (falta `seccion_cuneta`/`S_cuneta`) se dice «no se evaluó» por `avisos()`, sin exigir datos nuevos a quien declaró L.
  4. Reescribe DECLARÁNDOLO el test «duplicar `area_ha` duplica L» (qué fijaba, por qué era el síntoma, qué fija ahora).
     `INF-5.1.8`: di con honestidad si queda cerrado o en parte (consumidores reales de `area_ha`: el contraste Q/A de T-1 y la
     coherencia s_impl).
- **H2**: un `TramoDeAlivio` cuya verificación NO se evaluó no puede dejar «Expediente cerrado: sí» ni «con aviso: 0»: cuenta
  (como `Bloqueo` que espera el dato que lo destraba o en `con_aviso`: la vía que ya exista para «espera a un tablero»; dilo) y
  la guía lo dice.
- **H3**: avisa de cada hueco que VB1 no mira (entre la obra anterior y un `inicio_tramo_cuneta_km` declarado; tras el último
  alivio); un inicio POSTERIOR a la obra no se acepta en silencio (`DatoInvalidoError` que nombre el par); no presupongas el
  sentido del flujo en los textos.
- **H4 + D (TR)**: quita el «TR = 35 años» cableado en textos de M10: se imprime el TR del PUNTO (el que M1 calculó, con R del
  Propietario si lo declaró). La Tabla Nº 02 da RIESGO (35 % «descarga de agua de cunetas», 40 % «drenaje de la plataforma»,
  n = 15 años; lo fija el Propietario): la fila del alivio (T ≈ 35.3 años) se usa como ENVOLVENTE conservadora de la de la cuneta
  (T ≈ 29.9), declarado así —`Interpretacion`, no «la fila de la cuneta»—. Verifica la tabla en el PDF (pág. impresa 25 / PDF 28).
- **H5 + A (`seccion_cuneta` con valor de archivo; decisión del dueño)**: valor = mínimo de la Tabla Nº 34 «muy lluviosa (1600 a
  <3000 mm/año)»: profundidad 0.40 m, ancho 1.20 m (⇒ Z1 = 3, que es lo que la tabla fija), **Z2 (talud exterior) = 1.0 como
  elección [A] declarada** —la fuente NO lo fija: «de acuerdo al talud de corte» (Manual pág. 173; DG-2018 304.11 y Tabla 304.10);
  1.0 es el más empinado de las filas de suelo fino/arenoso y el lado seguro para la capacidad—, borde libre 0. Ventana que la
  fuente sostiene (corrige la atribución errónea a la Tabla 304.12 que el auditor señala): d y a ≥ el mínimo de la fila de la
  región adoptada; Z2 en el rango de la Tabla 304.10; bl 0–0.10 m. La ficha declara: (i) que la REGIÓN pluvial es elección ligada
  a un dato de sitio sin trazabilidad en el repositorio (año FEN; coherente con los 200 m), y que por encima de 3000 mm/año el
  mínimo es TRAPEZOIDAL, no implementado (aviso/ficha); (ii) el aviso de la Tabla 304.12 (1:4 si V.D. > 70 km/h con IMDA > 750).
  B-01 no puede cambiar (el auditor lo midió). El ejemplo `--declarar seccion_cuneta` de la guía desaparece: regenera.
- **B (borde libre)**: retira de la v8 la frase «con borde libre» sin cifra, con nota de corrección (el Manual calcula a cuneta
  llena: cita literal pág. 174); campo [A] 0–0.10 m con valor 0 y el 0.10 declarado como adopción.
- **C (obras de Familia A como extremo de tramo; decisión del dueño: SÍ por defecto)**: implementa como criterio [A] categórico
  con valor de archivo «sí» y «no» barrible; fuente: DG-2018 304.11 («…obras de drenaje transversal…», pág. 208 / PDF 209), como
  `Interpretacion` (el Manual 4.1.2.1 d) sólo nombra alcantarillas de alivio; el perfil decide si la cuneta llega a esa obra);
  `inicio_tramo_cuneta_km` declarado gana. **Consecuencia que el auditor midió y que se DECLARA, no se esconde**: B-01 queda a
  530 m de A-02 → VB1 NO CUMPLE en el fixture (línea base y guía). No mueve ningún diámetro. La guía dice la verdad: muestra el
  NO CUMPLE y cómo se resuelve (alivio intermedio o `inicio_tramo_cuneta_km` declarado con su procedencia); README de la línea
  base con el antes/después.
- **Dudosos del auditor, resueltos por el orquestador**: (1) B-01 en terraplén: el modelo de cuneta triangular describe la cuneta
  en corte AGUAS ARRIBA del alivio, no la sección del cruce: dilo en el paso/ficha (sin cambio de cálculo). (2) n de la cuneta: se
  usa la Tabla Nº 32 (Strickler), que es la específica del núm. 4.1.2.1; decláralo en el paso y nombra la Tabla Nº 09 como
  alternativa que el propio Manual cita. (3) «* Para flujos de muy corta duración» (Tabla Nº 33): transcribe la nota al registro y
  que el paso la imprima cuando el revestimiento sea concreto o mampostería (el extremo inferior es la lectura conservadora;
  la fuente no da otro valor para flujo prolongado). (4) región > 3000 mm/año: ver A (i).
- **H6–H11 (BAJA)**: aplícalos todos (incluido el mutante vivo de Z2 en `caudal_a_velocidad`: test con Z2 ≠ 1 y dorado a mano).

## Para la PARTE 2 (cuando se te diga «integra»)
IDs canónicos: `INF-5.1.12` (cerrado), `INF-3.3.8` (cerrado), `INF-5.1.8` (según H1), aceptación de la Familia B (ficha T0-03).
Riesgos de rebase: los de la sección final de la auditoría (31 archivos; línea base se REGENERA; `CLAVES_EXTERNAS` 18 → 21; tu
Parte de `decisiones_diferidas.md` se renumera a la siguiente libre). Commit:
`tesis(T-9): espaciamiento de alivios — … — INF-5.1.12, INF-3.3.8 (cerrados); INF-5.1.8 (…)`.

Entrega de la PARTE 1: `SP/INFORME_T-9_correcciones.md` + resumen < 300 palabras (hallazgo por hallazgo, tests nuevos, lo que se
mueve en el fixture con su causa, «diámetros movidos: ninguno» o la lista, SHA de la rama).
