# INFORME — T-11, corrección del defecto de diagnóstico T11-03 (hallazgo H4 de la auditoría)

Rama `tesis/T-11`, de `c774035` a **`10fb84b`** (tres commits `wip(T-11): T11-03 …`, empujados a
`origin/tesis/T-11`; nada fusionado ni empujado a `main`). Base de consulta: `14f6138`.

## 1. Qué decidí en B (el delta de rasante) y por qué

**Lo doy, pero sólo cuando es geometría pura, y rotulado.** No rehago el acoplamiento.

Los dos textos que se contradecían:

- CLAUDE.md, «Excepciones»: `DisenoNoFactibleError` «Debe llevar el motivo y, si aplica, el delta de
  rasante requerido».
- Docstring de `MD`: «No calcula el delta de rasante. `DisenoNoFactibleError.delta_rasante_m` sale
  vacío a propósito… es el tamizado de 7.A, que fija la rasante ANTES del bucle y no desde dentro».

La fuente (v8), literal:

- §7.A: «cota rasante ≥ max{ cota clave + h_rec + e_paq ; cota entrada + HW + resguardo(CBR) + e_paq }»,
  y su nota `MAT-O6`: la segunda condición es V4 escrita al revés («… = `cota de subrasante −
  resguardo`, que es V4») y «La **primera** condición no necesitaba corrección: `cota clave`, `h_rec` y
  `e_paq` son una cota y dos espesores».
- §7.B: «El chequeo devuelve *"no factible → subir rasante X cm"*, nunca un resultado silencioso».
- «**Acoplamiento circular declarado:** rasante → paquete estructural → subrasante → CBR → resguardo →
  V4 → rasante. Se corta fijando la rasante en 7.A y congelándola.»

Lectura: las dos cosas valen a la vez. La v8 prohíbe **mover o iterar** la rasante desde el bucle (eso
no se hace), y pide que un «no factible» lleve X. X es la fórmula de 7.A para una sección nombrada; lo
que la ata al acoplamiento es el HW (segunda condición). Por eso:

- MD le pide a `M7.tamizado_rasante` el delta **del escalón que no cabe** (rasante, paquete y CBR del
  CSV congelados; MD no tiene fórmula propia) y lo informa **sólo si** (a) ese escalón cumple todo lo
  que la Fase 5 le evaluó —V4 incluida, luego el resguardo ya está satisfecho— y (b) el tamizado dice
  que gobierna el **recubrimiento**: `clave + h_rec + e_paq − rasante`, que no lleva el HW.
- El del punto es el menor entre materiales, y se rotula: **cota inferior para ese escalón, no el
  remedio verificado del punto** (a ese escalón le faltan V7, V8, V9 y la Fase 8; la longitud y el HW
  cambian; los escalones menores se reevalúan con más relleno), y **provisional** si el fondo de
  entrada es el terreno adoptado (regla de T-6).
- Si el escalón que no cabe además incumple algo, **no hay delta** y el motivo dice por qué. Es el caso
  que me hizo no darlo siempre: en B-01 (TW = 1.00 m) el escalón que no cabe incumple V2, que empeora al
  crecer el tubo; un «subir la rasante 0.39 m» mandaría al revisor a una obra que no resuelve el punto.

Lo que **no** afirmo, y conviene que el dueño lo sepa: el delta no es ni el mínimo ni el suficiente
para el punto. En A-01 sin TW (0.320 m) los escalones anteriores incumplen V7 por mucho (concreto
Ø 1.65 m: 4.1 frente a 30.1):
con 0.32 m más de rasante lo esperable es que V7 siga sin cerrar. El rótulo lo dice; quitarlo sería
inventar un remedio.

Corregidos: el docstring de cabecera de `MD` («Lo que MD NO hace» y «Excepciones»), el de
`disenar_punto` y el de `_motivo_escalon_fallido`; nota «Corregido (`T11-03`…)» en la v8 §7.B.

## 2. A, B, C

- **A — CERRADO.** `MD.disenar_material` reconoce por geometría (`_escalon_sin_cabida`: excepción
  `DatoInvalidoError` sobre `cota_subrasante` **y** `M5.cota_clave` sin relleno bajo la subrasante,
  umbral `TOL_UMBRAL_NORMATIVO`, forma MAT-D13) el escalón que no cabe; lo anota con sus dos cotas
  (`PasoDiseno.sin_cabida`, `modelos.EscalonSinCabida`) y devuelve el material como «descartado por
  rasante», con el motivo del escalón anterior. El punto sale «NO FACTIBLE POR RASANTE», al principio
  del mensaje. `M5.altura_relleno_sobre_clave` no cambia.
- **B — CERRADO EN PARTE** (por decisión, §1): hay delta sólo cuando es geometría pura; en los demás
  casos sigue `null`, con la razón escrita.
- **C — CERRADO EN PARTE.** `MD._exigir_datos_validos`: el `DatoInvalidoError` de un dato del punto que
  levanta la **Fase 5** sale con su `campo` (bloqueo `DATO_INVALIDO`) cuando detuvo un escalón que
  cumplía lo demás o a todos los candidatos (patrón PC-28 + T-5). El caso del auditor
  (`Q_evento_extremo_m3s` = 0.5 en A-01) queda así. **Fuera, a propósito:** (i) cuando un candidato
  posterior cierra, el resultado aceptado no se toca (lo prohibía el encargo); (ii) el
  `DatoInvalidoError` que M3/M4 levantan **antes** de la Fase 5 sigue saliendo «no factible».

## 3. Tests nuevos y par medido

- `tests/test_t11_no_factible_por_rasante.py`: **29 tests**. Contra `c774035`: **23 rojos y 6 verdes**,
  que son las guardias de «lo que no cambia» (M5 conserva su excepción; el material que cierra no
  cambia porque otro no quepa ni porque otro tenga un dato inválido; las iteraciones de A-01 son las de
  siempre; el dato inválido sobre un escalón que ya incumple y el de antes de la Fase 5 siguen igual).
  Dorados a mano en el docstring (clave 44.075 msnm, delta 0.3298 m del concreto Ø 1.80 m; 0.31981 m
  del TMC Ø 1.95 m; A-02 0.4428 m).
- `tests/test_t11_validacion_integral.py`: el `xfail(strict=True)` liberado y endurecido (dos dorados).
- `tests/test_MD.py`: sólo docstrings (el doble `_RevientaMaterial` ya no «reproduce V7»; el test de
  los tres materiales que revientan sigue valiendo y dice por qué).
- **Suite entera, con `NORMAS_DIR`, sobre `10fb84b`: 6417 passed / 23 skipped / 0 xfailed (collected 6440), 391.8 s; salida en `SP/T-11/suite.txt`.** Referencia antes del cambio: 6387
  passed / 23 skipped / 1 xfailed (6411). La primera corrida entera dio 2 rojos en
  `test_manifiesto_citas` (una referencia `MD:178` desplazada por mis líneas): resincronizada con
  `manifiesto.resincronizar` y vuelta a correr entera.

## 4. Lo que cambió en la línea base (lista exacta, frente a `c774035`)

Regenerada con `regenerar.sh`. Ocho archivos; en cada uno esto y nada más:

| Archivo | Qué | Antes → después |
|---|---|---|
| `cli_perfil.txt` | mensaje `[DisenoNoFactibleError]` de A-01, A-02, B-01 (3 líneas) | «…Concreto reforzado: material no evaluable: DatoInvalidoError: Dato invalido en 'cota_subrasante'… (-0.025 m de relleno)…» → «…NO FACTIBLE POR RASANTE: en 2 de 3 candidatos… Concreto reforzado: material descartado por rasante: Ø 1.80 m no cabe bajo la subrasante (clave a 44.075 msnm, subrasante a 44.050 msnm: +0.025 m)… Escalon anterior: Ø 1.65 m: incumple V7…». A-01 termina en «Subir la rasante 0.32 m»; A-02 y B-01, «No se da delta de rasante» |
| `cli_perfil_ancho.txt`, `cli_familia_c.txt` | mensaje de B-01 (1 línea cada uno) | ídem; sin delta; nombra V2 (Ø 1.80 m anterior y Ø 1.95 m que no cabe, clave 40.538 sobre 40.450) |
| `informe_perfil_ancho.json`, `informe_familia_c.json` | B-01: `mensaje` del bloqueo; `motivo` de `iteraciones[7]` y `[16]` | «Ø 1.95 m: el escalon no se pudo evaluar -- DatoInvalidoError…» → «Ø 1.95 m no cabe bajo la subrasante (clave a 40.538 msnm, subrasante a 40.450 msnm: +0.088 m): …; de lo que se le evaluo antes incumple V2». `delta_rasante_m` sigue `null` |
| `memoria_perfil.html` | los 3 mensajes y 6 motivos de escalón; **2 criterios usados más** (`cobertura_minima_aashto` [C], `condicion_pavimento` [A]) en el anexo y en A.4; huella de la v8 | el tamizado de A-01 los invoca; huella `4555b94e…` → `fc97629b…` |
| `memoria_perfil_ancha.html` | mensaje y 2 motivos de B-01; huella de la v8 | ídem |
| `memoria_expediente.html` | sólo la huella de la v8 | ídem |

Sin cambio (`cmp`): `cli_expediente.txt`, `cli_rama_error.txt`, `informe_expediente.json`,
`informe_rama_error.json`, `memoria_punto_cajon.html`, los dos CSV de resumen.

**Comparador de E-B contra `14f6138`:** `informe_expediente.json` e `informe_rama_error.json` IGUALES;
`informe_perfil_ancho.json` e `informe_familia_c.json`, 3 diferencias cada uno (las de la tabla),
**0 no comparables**. Corrida estrecha (sin JSON en la carpeta), medida aparte: 12 diferencias, 0 no
comparables — 3 mensajes, 6 motivos de escalón, `delta_rasante_m` de A-01 `None` → 0.31981, y los dos
criterios que pasan a «usados». Y, fuera de la línea base, las **78 corridas del juego de T-11**
(completo, sin TW, variantes y «quitar una») volcadas antes y después: 74 IGUALES y 4 que difieren sólo
en `mensaje`, `motivo`, `delta_rasante_m` y esos dos criterios.

**Diámetros, secciones, materiales y HW movidos: ninguno.** Las `iteraciones` (escalones y lo que cada
uno incumple), idénticas.

Los documentos generados de T-11 (`validacion_integral.md`, `validacion_sensibilidad.md`,
`validacion_hds5.md`, `validacion_hy8.md`, `guia_perfil.md`, `indice_formulas.md`) **no cambian de
texto**: sus tests de sincronía pasan sin regenerar.

## 5. Mutación

`tests/apoyo/mutacion.py` sobre las doce funciones de MD tocadas, contra el archivo nuevo,
`test_MD`, `test_ext1_entradas` y `test_cierre_c05`: primera pasada 86/97; tras los tests que pidió,
**92 de 96 muertos (95.8 %)**. Los 4 vivos: la frontera `> TOL` → `>= TOL` de `_escalon_sin_cabida`
(inalcanzable: exige `subrasante − clave == TOL` exacto en coma flotante) y tres en líneas de T-5 que no
toqué (`ultimo_por_fase_8` ×2 y `decisivos[0]` de los faltantes). No toqué ninguna comparación del censo
de `test_ext11_mutacion`.

## 6. Lo que NO hice

- No toqué el `.xlsx`, la tabla de conteos de CLAUDE.md, `verificar_sesion.py` ni H1–H3 / H5–H14.
- No resellé `trazabilidad.csv` ni `indice_formulas.md` (llevan el par anterior).
- No extendí C al dato inválido de antes de la Fase 5: lo probé y **cambiaba el tipo de bloqueo de la
  rama de error de la línea base** (`DisenoNoFactibleError` → `DatoInvalidoError`, campo `'D'`). Lo
  retiré; queda en la ficha (abierto 4) como decisión del dueño.
- No di delta cuando el escalón que no cabe incumple sólo V4 (saldría por resguardo, con el HW).
- No añadí `sin_cabida` al JSON de `iteraciones[]` (viaja en el motivo y en `delta_rasante_m`).

## 7. Para el agente de integración

- **Conteo:** +29 tests y el xfail liberado → medido 6417 / 23 / 0 xfailed, collected 6440 (sólo esa
  configuración: PyMuPDF sí, Tk no, normas enlazadas; sin `NORMAS_DIR` no lo medí).
- **Textos de CLAUDE.md:** «B-01 … `DisenoNoFactibleError` con motivo V2» (párrafo de E-A) **vuelve a
  ser cierto** (el mensaje nombraba un dato inválido); la frase de `DisenoNoFactibleError` («si aplica,
  el delta») ya no contradice a MD. **Faltan** en CLAUDE.md: la regla nueva de `DatoInvalidoError` en
  MD (`_exigir_datos_validos`) y el párrafo de conteos de esta corrección. La ficha T11-03 está
  **cerrada en parte**; el rótulo «Parte LIV (provisional)» sigue sin renumerar.
- **Riesgos:** (1) cualquier edición posterior de la v8 mueve la huella de las tres memorias de la
  línea base; (2) cualquier línea añadida a `MD.py` antes de `NUMERAL_BUCLE` desincroniza
  `manifiesto_citas.md` (se arregla con `manifiesto.resincronizar`); (3) el mensaje «no factible» es
  ahora más largo (3.5 kB en A-01 y 4.6 kB en B-01 de la corrida estrecha, frente a 1.5 kB): lleva el
  diagnóstico delante por eso; (4) `PasoDiseno` gana un
  campo opcional (`sin_cabida`), con valor por defecto.
- **Preguntas para el dueño** (ficha T11-03, abiertos 3 y 4): ¿bloquear también cuando un candidato
  cierra y uno anterior tenía un dato inválido (como T4-10 hace con el dato que falta)?; ¿sacar como
  dato inválido el diámetro de arranque negativo de la rama de error?
