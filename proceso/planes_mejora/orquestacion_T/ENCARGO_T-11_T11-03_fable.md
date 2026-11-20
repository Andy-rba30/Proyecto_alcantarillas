# Encargo: T-11 — corrección del defecto de diagnóstico T11-03 (hallazgo H4 de la auditoría) — sexta sesión

Eres el agente que corrige UN defecto, el que la validación integral de T-11 destapó y la auditoría adversarial confirmó y
ensanchó (H4 de `ORQ/AUDITORIA_T-11.md`). Trabajas en español, en el worktree `/home/user/wt/T-11` (rama `tesis/T-11`, HEAD
`c774035`, base `14f6138`). No toques `/home/user/Proyecto_alcantarillas`, `/home/user/wt/main` (consulta, la base) ni
`/home/user/wt/estado` (sólo lectura). `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/`; `SP` =
`/tmp/claude-0/-home-user-Proyecto-alcantarillas/0d09ea9c-a87f-5311-8eec-38e45d8c2a3d/scratchpad/` (temporales en `SP/T-11/`;
los scripts del auditor están en `SP/T-11-aud/`: `var.py`, `sintw.py`…). `export NORMAS_DIR=/home/user/andy-rba30/normas`.

## Lee primero
1. `ORQ/ORQUESTACION.md` (la ENMIENDA DE LA SEXTA SESIÓN del final gana), y de `CLAUDE.md` de tu worktree: «Excepciones
   (taxonomía)» entera, «Arquitectura», «Reglas de corrección de hallazgos de auditoría» (regla 2: la hoja `Conflictos` del
   tracker —`tests/apoyo/tracker.py`— y `docs/decisiones_diferidas.md` se consultan ANTES de tocar el objeto).
2. `ORQ/AUDITORIA_T-11.md`, hallazgo **H4** entero (su propuesta de corrección por símbolo es una PROPUESTA: no la des por buena).
3. El docstring de cabecera de `src/modulos/MD.py` («Lo que MD NO hace»: **«No calcula el delta de rasante.
   `DisenoNoFactibleError.delta_rasante_m` sale vacío a propósito…»**, por el acoplamiento circular rasante → subrasante → CBR →
   resguardo → V4 que la Sec. 7.A corta) y el de `MD.disenar_punto` («BLOQUEADO y NO FACTIBLE»); la Sec. 7.A / 7.B de
   `docs/hoja_de_ruta_alcantarillas_v8.md`; `M7_geometria.tamizado_rasante` y `TamizadoRasante`; `M5.altura_relleno_sobre_clave`
   y sus tests (C09 / SIS-F-10 en `test_M5_verificaciones`); PC-28 y C05 en `MD` (los dos precedentes: `DatoFaltanteError` y
   criterio inválido relanzados en vez de tragados); la ficha T11-03 de `docs/decisiones_diferidas.md` y el test
   `tests/test_t11_validacion_integral.py::test_el_escalon_que_no_cabe_bajo_la_subrasante_es_no_factible_por_rasante`.

## Qué hay que cerrar
A. **El diagnóstico equivocado.** Un escalón cuya clave no cabe bajo la subrasante sale hoy como `DatoInvalidoError` sobre
   `cota_subrasante` (un dato que nadie tocó), el material como «no evaluable» y el punto como «no factible» SIN el motivo
   verdadero. Es la salida habitual de todo punto al que una verificación no le cierra en ningún diámetro (está en siete archivos
   de la línea base). Debe terminar como no factible POR RASANTE, con el motivo de los escalones evaluados y el del que no cabe.
B. **El delta de rasante.** CLAUDE.md pide que `DisenoNoFactibleError` lleve «si aplica, el delta de rasante requerido»; el
   docstring de MD dice que sale vacío A PROPÓSITO. Son dos textos del proyecto que hoy se contradicen para este caso: RESUÉLVELO
   con la fuente (v8 §7.A/7.B) y dilo. Si el delta se puede dar sin rehacer el acoplamiento circular (p. ej. el de
   `M7.tamizado_rasante` para el primer escalón que no cabe, rotulado COTA INFERIOR porque con esa rasante V7 y la Fase 8 de ese
   escalón no se han evaluado y la longitud cambia), dalo y corrige el docstring de MD; si no se puede dar honestamente, NO lo
   inventes: deja `delta_rasante_m` vacío, que el motivo diga por qué y qué escalón no cabe y por cuánto (ese número sí es
   geometría pura), y reescribe el test xfail y la ficha a esa verdad, declarándolo. Decide tú, con la evidencia escrita.
C. **El hermano que T-11 no vio.** Un `DatoInvalidoError` de un DATO DEL PUNTO levantado dentro de la Fase 5 (p. ej.
   `Q_evento_extremo_m3s` menor que el de diseño) sale como «no factible» con `campo: None`: el revisor tiene que CORREGIR un dato
   y el informe le dice que no existe diseño. Debe salir como bloqueo `DATO_INVALIDO` con su `campo` (mismo patrón que PC-28).

## Lo que NO puede cambiar (PARADA (c), no negociable)
- El resultado aceptado cuando algún material cierra; **ningún diámetro, sección, material ni HW** del fixture
  (`tests/ejemplo_puntos.csv`), de la línea base (`tests/linea_base_familia_c/`), de la guía (`docs/guia_perfil.md`) ni de las
  corridas de referencia; las `iteraciones` (mismos escalones, mismas verificaciones evaluadas); ninguna fórmula ni umbral.
  `M5.altura_relleno_sobre_clave` conserva su `DatoInvalidoError` directo (lo fijan tests y lo usa la Fase 8).
- SÍ pueden cambiar, DECLARÁNDOLO uno a uno: los mensajes «no factible» de la línea base y, si lo das, `delta_rasante_m` de
  `null` a un número en sus JSON; el docstring de MD; la clave del censo de `test_ext11_mutacion` si tocas una comparación censada.
- Si la corrección movería un diámetro o un HW: NO la apliques; déjala reproducida y repórtalo.

## Cómo
- Test primero en rojo: el `xfail(strict=True)` existente (reescrito si decides B por la vía «sin delta») y los nuevos (el
  hermano; el caso de la línea base B-01 con TW = 1.00 m, cuyo motivo debe nombrar V2 —lo que CLAUDE.md dice de él— y no un dato
  inválido; un punto donde un material cierra y otro no cabe: resultado idéntico al de hoy). Dorados a mano (la cota de clave y el
  déficit se calculan con la aritmética escrita). Libera el xfail al corregir. Guardias con la forma MAT-D13.
- Regenera la línea base de la Familia C por su script (mira `tests/linea_base_familia_c/README.md`) y mídela contra la base
  `14f6138` con el comparador de E-B (`cli.py --comparar`): cada diferencia clasificada; «diámetros/secciones/materiales/HW
  movidos: ninguno» o NO sigues. Añade al README de la línea base la sección de esta corrección. Regenera los documentos
  generados de T-11 que cambien de texto (`python3 -m tests.apoyo.validacion_integral …`, sensibilidad, guía: mira sus tests de
  sincronía) y actualiza la ficha T11-03 (cerrada / cerrada en parte, con lo que quede).
- Corre los tests afectados mientras iteras (`test_MD`, `test_M5_verificaciones`, `test_M7_geometria`, `test_linea_base`,
  `test_cierre_perfil`, `test_cli`, `test_guia_perfil`, `test_ext1_entradas`, `test_ext11_*`, `test_pf3_barrido`, los `test_t11_*`,
  `test_t3_correcciones_auditoria`, `test_decisiones_diferidas`) y **la suite ENTERA una vez al final**
  (`NORMAS_DIR=/home/user/andy-rba30/normas python3 -m pytest -q -p no:cacheprovider --no-header > SP/T-11/suite.txt 2>&1`,
  ~7 min; referencia de la rama: 6387 passed / 23 skipped / 1 xfailed, collected 6411). Mutación acotada (≤ 15 min,
  `tests/apoyo/mutacion.py`) sobre las funciones de MD que toques.
- NO toques: el `.xlsx`, la tabla de conteos de `CLAUDE.md`, `verificar_sesion.py`, ni los demás hallazgos de la auditoría (H1–H3,
  H5–H14 los corrige otro agente después de ti, en esta misma rama). No fusiones ni empujes a `main`.
- Commits `wip(T-11): T11-03 …` con `git push origin tesis/T-11` tras cada bloque (puede haber cortes: di qué falta). Pie: el de tu
  aviso de atribución; si no lo recibes, el de la ENMIENDA. Ningún identificador de modelo en otro sitio del repo.

## Entrega
`SP/INFORME_T-11_T11-03.md`: qué decidiste en B y por qué (con la cita de la v8); A, B, C cerrado / en parte / no; tests nuevos y
par medido; la lista EXACTA de lo que cambió en la línea base (archivo, qué texto o clave, antes → después) y «diámetros /
secciones / materiales / HW movidos: ninguno»; mutación; lo que NO hiciste; lo que el agente de integración debe saber (riesgos,
textos de `CLAUDE.md` que quedan falsos, p. ej. «B-01 … `DisenoNoFactibleError` con motivo V2»). Respuesta: MENOS DE 300
PALABRAS con lo esencial y el SHA de la rama.
