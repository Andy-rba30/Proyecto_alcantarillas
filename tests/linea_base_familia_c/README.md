# Línea base de la Familia C — sesión C0

**Para qué existe.** Es el **único criterio de salida duro de C1**: el refactor de sección
no puede mover ningún número, y esto es contra qué se comprueba. No es documentación: es un
artefacto de diff.

## Cómo se usa

```sh
sh tests/linea_base_familia_c/regenerar.sh
git diff --stat tests/linea_base_familia_c/
```

**El diff tiene que salir VACÍO.** Si sale algo, o el refactor movió un valor, o movió un
rótulo de la memoria. Las dos cosas son hallazgos de C1, no ruido.

## Con qué se midió

| | |
|---|---|
| `origin/main` | **`4f6cf69`** |
| Entorno | **PyMuPDF sí / ventana Tk no** — la configuración de referencia del plan |
| Suite | **1536 passed, 2 skipped** (collected 1538) |
| Corrida | `python3 cli.py tests/ejemplo_puntos.csv --luz 2.75 --alcance perfil` |

## Por qué está normalizada

Corrida cruda, la salida **no es reproducible**: generada dos veces seguidas, difiere.
`regenerar.sh` retira tres campos volátiles, y el tercero es el que de verdad importa:

1. `generado (UTC): <iso>` en la salida de la CLI.
2. `corrida UTC: <iso>` y la misma fecha en formato local, en el HTML.
3. **`Fecha de criterios_adoptados.py`**, que `M11_reporte` saca de `ruta.stat().st_mtime`.
   **Cambia por CLON, no por corrida**: en un checkout nuevo es la hora del clon. Sin
   retirarlo, este diff daría rojo en otra máquina con el código idéntico.

Los patrones son específicos a propósito: un barrido de fechas genérico pisaría texto
normativo. Medido en C0: en el HTML hay **tres** fechas y las tres son volátiles.

## Dónde se detiene C-01 hoy, y con qué

Reproducible con el fixture del repositorio. Los datos declarados por
`--datos-externos` son **valores de sonda**, no datos de proyecto: sirven para llegar al
bloqueo, y ninguno se escribe en el CSV.

**RE-MEDIDA EN C6, y la última fila había caducado dos veces.** Decía «los **tres** datos
declarados» cuando el fixture trae cuatro desde C6, y su fila final seguía prometiendo un
`DisenoNoFactibleError` con «M2 no ofrece material candidato para la Familia C», que **C5
retiró** al abrirle catálogo al marco. Una tabla de «dónde para hoy» que describe dónde
paraba hace dos sesiones es peor que no tenerla: se lee como medición.

La columna «dónde para» nombra el **bloqueo sustantivo**. En las siete filas lo precede
el mismo `DiferidoPorAlcance` que C5 emite para todo punto de Familia C —la declaración de
sustitución del criterio de dimensionamiento—, que no es un bloqueo del expediente y no
distingue una fila de otra.

| Declarado para C-01 | Dónde para | Símbolo |
|---|---|---|
| *(nada)* | `DatoFaltanteError` · «Falta el dato `S_cauce`» en la etapa *tirante en el receptor (TW, Sec. 1.3)* | `cli._resolver_tw` → `PuntoCritico.exigir` |
| `Q_m3s` | igual que arriba | igual |
| `S_conducto` | `DatoFaltanteError` · «Falta el dato `Q_m3s`» en *material y diámetro (bucle de MD)* | `MD.disenar_punto` → `PuntoCritico.exigir` |
| `TW_m` | igual que la anterior | igual |
| `TW_m` + `Q_m3s` | `DatoFaltanteError` · «Falta el dato `S_cauce`» en *material y diámetro* | `MD.disenar_punto` → `PuntoCritico.exigir` |
| **`Q_m3s` + `S_conducto`** | **`CriterioPendienteError`** · «falta declarar: `embocadura_cajon`», con concepto, fuente, qué lo resuelve y los puntos | **`M2.catalogo`** → `criterios_adoptados.valor` |
| `Q_m3s` + `S_conducto` + `S_cauce` | igual que la anterior | igual |

**El par mínimo que llega al bloqueo real sigue siendo `Q_m3s` + `S_conducto`**, y `TW_m`
sigue siendo redundante: declarar la pendiente del conducto cubre a la vez la vía de
Sec. 1.3 y la que MD necesita.

**Y `S_cauce` no cambia dónde para C-01 hoy, a propósito.** El punto se detiene ANTES, en
el catálogo del marco, porque sus cinco criterios están sin declarar. La clave hace falta
para el escalón siguiente —con los criterios declarados, V2b se detenía sin ella— y por eso
el fixture la trae: para que el día que se declaren, el artefacto no vuelva a moverse por un
dato de entrada. El detalle está en §16.1-bis, §1.1 y §16.11 de `docs/ruta_familia_c.md`.

## Regeneraciones posteriores

- **C2** (`familiaC(C2)`): la memoria HTML cambia en **dos líneas, y ninguna es un
  número de cálculo**. (1) el SHA-1 de `criterios_adoptados.py`, porque ese archivo
  cambió; (2) el criterio `hds5_embocadura_hdpe`, que pasa a imprimir `forma = 1` junto
  a sus K, M, c, Y y Ks. Lo segundo es el efecto buscado: `ConstantesHDS5` gana el campo
  `forma` —la columna «Equation Form» de la Tabla A.1, que hasta C2 no se transcribía— y
  el contrato de memoria (§4.5) exige que nada de lo que se añade quede invisible en el
  reporte. El HW, los tirantes y las velocidades no se mueven: `git diff` sobre esta
  línea base da exactamente esas dos líneas.
- **EXT-1** (`ext(EXT-1)`, 2026-09-20): cambian **tres archivos**
  (`memoria_expediente.html`, `memoria_perfil.html`, `memoria_perfil_ancha.html`) y
  **ninguna línea es un número de cálculo**: (1) el SHA-1 de `criterios_adoptados.py`,
  porque ese archivo cambió; (2) la fila «Sensibilidad declarada» que aparece en tres
  fichas de criterio que antes no la tenían —`ke_entrada` (0.2, 0.9: el recorrido de la
  Tabla C.2 derivado de `KE_HDS5_C2`), `v_max_tmc` y `v_max_hdpe` (0.25, 4.572: el piso
  [N] de V2 y el techo de la Tabla 8-4)—, efecto buscado de PC-02; (3) **sólo en
  `memoria_perfil.html`**, la ficha de `seccion_receptor` (EXT-V-05): su sensibilidad
  pasa de cinco frases en prosa a un dict `{campo: (min, max)}` que la guardia evalúa, y
  su justificación recupera la procedencia de cada banda (dren colector del Bajo Piura,
  llanura de riego, canal en tierra con vegetación estacional) que la prosa llevaba y el
  dict solo no lleva —lo señaló el auditor adversarial: la memoria no puede perder de
  dónde sale un rango—. Los 10 archivos restantes —JSON, CSV, volcados de la CLI y el
  punto de cajón— son idénticos byte a byte: ningún HW, tirante ni velocidad se mueve,
  que era la condición de la sesión.

- **EXT-2** (`ext(EXT-2)`, 2026-09-20): cambian **diez archivos**, y por primera vez
  desde C3 **se mueven números de cálculo**, todos declarados y todos esperados:
  1. **`informe_perfil_ancho.json`, `memoria_perfil.html`, `memoria_expediente.html`,
     `memoria_perfil_ancha.html` — A-01, la transición (`EXT-M-04`)**: el escalón
     Ø 0.90 m de A-01 cae en la transición del control de entrada (q\* = 3.5018) y su
     extremo inferior pasa a evaluarse con `H_c(Q_lo)`: `HW_entrada` **1.0423077 →
     1.0420015 m (−0.306 mm)**, y con él la cota mínima de rasante por resguardo
     (44.0923 → 44.0920 msnm), el V4 obtenido y el V4b. En las tres memorias el paso
     F4.CONTROL de A-01 sustituye además `Q_lo`, `H_c_lo`, `HW_lo` y `HW_hi`; en la
     estrecha y en la de expediente A-01 sigue sin dimensionar y el número se mueve en
     su traza. A-02 y C-01 no se mueven en ningún archivo.
  2. **Las tres memorias HTML** llevan además (a) el SHA-1 de `criterios_adoptados.py`
     —cambió la justificación de `metodo_transicion_hds5`, que ahora dice con qué H_c
     se evalúa el extremo— y (b) la ficha de ese criterio con la frase nueva.
  3. **`memoria_punto_cajon.html` (`EXT-M-03`, ensanche N = 3)**: `punto_cajon.py`
     declara `n_celdas_cajon = 3` y pasa por el reparto de M4. Cada barril recibe
     Q/N = 2.000 m³/s: y_n 1.040 → 0.472 m, q\* 2.957 → 0.986 (sigue no sumergido,
     Forma 2 pura), HW entrada 1.577 → 0.758 m, HW salida → 0.941 m, gobierna la
     salida y `h_o` cae fuera de rango; la traza gana el paso **«Caudal que entra a
     cada celda»** (F3.CELDAS, cita `HDS5_3ED.5.4.3#REPARTO`) y el `<pre>` imprime N y
     Q_celda. Con N = 1 esta línea base era ciega al reparto: repartir o no repartir
     daba el mismo número.
  4. **`cli_perfil_ancho.txt`, `informe_perfil_ancho.json`, `resumen_perfil_ancho.csv`,
     `memoria_perfil_ancha.html`, `informe_expediente.json`, `memoria_expediente.html`
     — B-01, la fila con TW > D (`PC-18`)**: `entradas_ampliadas.json` declara
     `TW_m = 1.00 m` para B-01 (D = 0.90 m), por encima del 0.30 global. Es la
     **salida ahogada**: `h_o = TW`, `HW_salida` **0.356 → 0.818 m** (control de
     salida), la cota mínima de 7.A pasa a gobernarla el resguardo (39.855 → 40.168
     msnm, `resguardo_HW_subrasante` en vez de `cobertura_minima_aashto`), V4 obtenido
     38.756 → 39.218, V4b 0.395 → 0.909. **Y V1 y V2 siguen [OK] sobre el tirante
     normal y la velocidad uniforme** con el barril ahogado: es exactamente la
     condición de `EXT-M-01` (régimen del barril), que EXT-3 corrige, y desde aquí la
     línea base la tiene congelada y visible. TW = 1.00 m es un valor de sonda, como
     el 0.30: no es una medición.
  Los tres archivos restantes —`cli_perfil.txt`, `cli_rama_error.txt`,
  `informe_rama_error.json`— son idénticos byte a byte: la corrida estrecha imprime
  HW con dos decimales y −0.306 mm no los mueve, y la rama de error no llega a M4.

  **Mutaciones que esta línea base ve desde EXT-2, medidas:**
  - «pasar el Q total a M4» (`Q_celda = Q` en `M4.resolver_control`) → mueve
    `memoria_punto_cajon.html` (y_n, HW, q\*, el paso del reparto). Antes no movía
    nada: ninguna sección rectangular llegaba a `resolver_control` con N > 1.
  - «extremo móvil» (`H_c_lo = critico.H_c`) → mueve los cuatro archivos de A-01.

  **Mutaciones que esta línea base NO ve, y hay que saberlo:**
  - **El techo `Q_lleno` de `tirante_normal` (`PC-06`)**: ningún punto del fixture cae en
    la banda (Q_lleno, Q_manning(H)) del marco —C-01 se detiene antes, en
    `embocadura_cajon`, y el punto de cajón corre con Q/N = 2.0 m³/s, lejos de 7.70—.
    Quitar la guardia no mueve un byte. Lo cubren `test_ext2_multicelda_transicion`
    y `test_seccion_rectangular`.
  - **El reparto en el camino `normal=None` de `resolver_control`**: `punto_cajon.py`
    inyecta el tirante normal (resuelto para Q/N con el mismo `caudal_por_celda`), de
    modo que un reparto que sólo faltara en el camino sin tirante inyectado no se ve
    aquí. Lo cubre `test_el_camino_sin_tirante_inyectado_tambien_reparte`.
  - **Un marco de N celdas que pase por MD y la Fase 5**: C-01 sigue sin dimensionar
    (cinco criterios del cajón sin declarar), y V6 rechaza N > 1. El multicelda de
    punta a punta vive en el test de aceptación (`_disenar_marco_n3`, con verificador
    inyectado), no en el corredor.
  - **La rama V6 con N > 1** (sigue siendo `celdas == 1`; ficha EXT-2-01 de
    `docs/decisiones_diferidas.md`).
  - **`H_c_lo` bajo Forma 2**: el punto de cajón usa una carta de Forma 2 y no cae en
    la transición; que `H_c_lo` sea `None` allí lo fija
    `test_bajo_forma_2_no_hay_H_c_del_extremo_y_la_recta_no_se_mueve`.

- **EXT-3** (`ext(EXT-3)`, 2026-09-20): cambian **nueve archivos**, los nueve por el
  régimen del barril, el dominio del método h_o y el bloque h_o del JSON (`EXT-M-01`,
  `EXT-M-02`, `PC-04`, `SIS-B-18`, `EXT-2-02`). Idénticos byte a byte: `cli_expediente.txt`,
  `cli_rama_error.txt`, `informe_rama_error.json` y `resumen_expediente.csv` (la rama de
  error no llega a M4; la corrida de expediente sigue sin dimensionar ningún punto y su
  volcado de texto no imprime la traza de escalones).
  1. **`cli_perfil.txt`, `memoria_perfil.html` — la corrida ESTRECHA de C0, sin TW
     declarado**: el TW sale por la vía 4 de Sec. 1.3 (receptor a sección llena) y para
     **A-02 vale 1.196 m sobre D = 0.90 m**: el barril va **LLENO**, V1 (y/D = 1) y V2
     (Q/A_llena) NO cumplen en Ø 0.90 y Ø 1.05, el primer D > TW (Ø 1.20) va
     parcialmente lleno bajo control de salida —V1/V2 diferidas— y ahí el concreto
     se cae por relleno negativo sobre la clave (`cota_subrasante`) y TMC/HDPE por el
     espesor de pared sin declarar: **A-02 pasa de dimensionado (Ø 0.90, control de
     salida) a «sin dimensionar» con `DisenoNoFactibleError`**. No es daño colateral:
     hasta EXT-3 esa misma corrida imprimía «manda TW: la salida está ahogada» junto a
     V1 [OK] con y/D = 0.373 sobre un barril que iba lleno (exactamente `EXT-M-01`), y el
     TW de 1.196 m es el escenario acotado de la vía 4, no una medición. A-01 (TW < D,
     control de salida) **sigue sin dimensionar, como antes** —`DisenoNoFactibleError`
     por relleno negativo sobre la clave (`cota_subrasante`)—, y lo que gana son **dos
     bloqueos diferidos** `MetodoNoEvaluableError` (V1 y V2) en su traza. Puntos
     dimensionados 1 → 0 (el que cae es A-02); etapas bloqueadas 13 → 19; diferidas
     9 → 14.
  2. **`cli_perfil_ancho.txt`, `informe_perfil_ancho.json`, `resumen_perfil_ancho.csv`,
     `memoria_perfil_ancha.html` — la corrida ANCHA, con TW declarado**: A-01 y A-02
     (control de entrada, TW = 0.30) no mueven ningún número y ganan las dos líneas
     nuevas del volcado («Regimen» y «h_o») y las **trece claves nuevas del JSON**
     (`Q_celda_m3s`, `numero_celdas`, `regimen_barril`, `V_llena_m_s`, `V_salida_m_s`,
     `V_salida_procedencia`, `y_salida_m`, `h_o_m`, `TW_m`, `ahogado_por_TW`,
     `HW_sobre_D_salida`, `h_o_fuera_de_rango`, `h_o_requiere_cautela`). **B-01, la fila
     con TW = 1.00 m > D = 0.90 m (`PC-18`)**, que EXT-2 dejó congelada con V1/V2 [OK]
     sobre el barril ahogado: Ø 0.90 va LLENO y **V1 (y/D = 1.0) y V2 (Q/A_llena =
     0.149 m/s) NO cumplen**; el punto cierra en **Ø 1.05** (TW < D, parcialmente lleno
     bajo control de salida) con **V1 y V2 diferidas** por método no evaluable,
     HW/D_salida = 0.778 (cautela, no fuera de rango), y la Fase 6 recibe la velocidad de
     SALIDA de HDS-5 3.1.6 —Q entre el área al TW, **0.112 m/s** en vez de la uniforme
     1.956— de modo que **d50 pasa de 0.126 a 0.0004 m** (el CSV lo imprime 0.000): con la
     salida ahogada por el receptor el chorro no existe, que es lo que la fuente mide.
     La clave del JSON de la Fase 6 pasa de `V_erosion_m_s` a `V_salida_m_s`.
  3. **`informe_expediente.json`, `memoria_expediente.html` — la corrida de
     EXPEDIENTE**: ningún punto dimensiona (igual que antes) pero A-01 (Ø 1.20) y A-02
     (Ø 0.90) se detienen ahora en **V1 con `MetodoNoEvaluableError`** (control de
     salida, barril parcialmente lleno) en vez de en el criterio pendiente de V5; los
     escalones Ø 0.90 de B-01 con TW = 1.00 llevan `incumplidas: [V1, V2]`.
  4. **Las cuatro memorias HTML** llevan además el SHA-1 de `criterios_adoptados.py` (no
     cambió ningún valor: cambió el archivo) y el bloque de umbrales con la
     `H_O_CONDICION_APLICACION` reescrita («no es un aviso: bloqueo método no
     evaluable»). **`memoria_punto_cajon.html`** gana el paso **F4.REGIMEN** («Regimen del
     barril y velocidad a la salida») en su traza; ningún número del cajón se mueve.

  **Mutaciones que esta línea base ve desde EXT-3:** volver V2 a `V_sedimentacion` bajo
  LLENO (B-01 vuelve a Ø 0.90 en la ancha; A-02 vuelve a dimensionar en la estrecha);
  `regimen_del_barril` devolviendo siempre PARCIALMENTE_LLENO (mismo efecto); pasar
  `V_erosion` a M6 (d50 de B-01 vuelve a 0.126). **Lo que NO ve:** el bloqueo «método no
  evaluable» de la carga HW —ningún punto de las cuatro corridas queda bajo control de
  salida con HW/D < 0.75 tras EXT-3 (B-01 sube a Ø 1.05 y pasa a 0.778)—; lo cubren
  `tests/test_ext3_regimen_barril.py` y `tests/test_cierre_perfil.py` (B-01 del corredor
  de perfil, HW/D = 0.395).
- **EXT-4** (`ext(EXT-4)`, 2026-09-20): cambian **ocho archivos** y **ningún número de
  cálculo se mueve**: es el contexto de corrida (`EXT-A-01`, `PC-07`, `PC-09`) y la cuenta
  única de etapas bloqueadas (`EXT-G-02`). Idénticos byte a byte: `cli_expediente.txt`,
  `cli_rama_error.txt`, `resumen_expediente.csv`, `resumen_perfil_ancho.csv` y
  `memoria_punto_cajon.html`.
  1. **Los tres JSON** (`informe_expediente.json`, `informe_perfil_ancho.json`,
     `informe_rama_error.json`) ganan en `expediente` las dos huellas de la corrida
     (`csv_sha1`, de los bytes que M0 leyó, y `criterios_sha1`), y cada fila de
     `criterios.bloquearon` la clave `diferido`. En los dos primeros, la clave
     `cota_entrada_origen` de la geometría deja de ser el dict que la duplicación del
     literal publicaba (`adoptada: True, regla` leída del registro global AL EXPORTAR) y
     pasa a `{rotulo, adoptada, criterio, regla, procedencia, nota}` leído entero de
     `CotaDeEntrada` —`regla` viaja con la cota desde M5—. Los tres puntos con geometría
     siguen diciendo `ADOPTADA` / `cota_terreno`: el valor no cambió, cambió de dónde sale.
  2. **`cli_perfil.txt`, `cli_perfil_ancho.txt`**: el bloque «CRITERIOS PENDIENTES QUE
     BLOQUEARON UNA ETAPA» imprime la línea «Diferido : por alcance; no cuenta para el
     cierre» en los criterios cuyo bloqueo estaba entero diferido (`remanso_derecho_via`,
     `TR_evento_extremo`). «Etapas bloqueadas» del RESUMEN no cambia de número: la CLI ya
     restaba lo diferido; lo que EXT-4 hace es que la GUI y la memoria lean la MISMA
     cuenta (`Informe.resumen`).
  3. **Las tres memorias HTML de la CLI** ganan la fila «Diferidas por alcance (no cuentan
     para el cierre)» en la tabla del encabezado y la línea «Diferido por alcance» en las
     fichas de criterios bloqueantes diferidas; llevan además el SHA-1 nuevo de
     `criterios_adoptados.py` (cambió el archivo —`reiniciar_usos`,
     `verificar_declaracion`, el docstring de `limpiar_valores_dinamicos`—, no ningún
     valor).

  **Mutaciones que esta línea base ve desde EXT-4:** dejar de vaciar el registro de usos
  al entrar en `cli.correr` NO la mueve —cada comando es un proceso nuevo— y por eso el
  caso (a) de `tests/test_ext4_contexto_corrida.py` corre dos veces en el mismo proceso;
  publicar `cota_entrada_origen` leyendo el registro la mueve sólo si algo se declara
  entre correr y exportar, que la CLI no hace: lo cubre el caso (b). Lo que sí ve: perder
  la clave `diferido`, las huellas del `expediente` o la fila de diferidas del encabezado.

## C3 ensanchó la ventana, y son diez archivos

La ventana de C0 miraba **una** corrida: perfil, sin TW, tirando el JSON, sin CSV de
resumen, y con **1 de los 4 puntos** llegando a dimensionarse. Costó dos veces: C1 metió una
regresión de salida impresa que esta línea base **no vio** (la rama de error necesita un
`--declarar` para alcanzarse), y en C2 el defecto de la Forma 2 lo encontró un auditor
leyendo el código, no el diff.

C3 la ensancha en cuatro ejes:

| | Antes | Ahora |
|---|---|---|
| Salidas capturadas | CLI + HTML | CLI + HTML + **JSON** + **CSV de resumen** |
| Alcances | perfil | perfil **y expediente** (plantillas distintas, Fases 8 y 9 ejecutadas) |
| Puntos dimensionados | **1** de 4 | **3** de 4 |
| C-01 (Familia C) | se detenía por falta de TW | llega a su **bloqueo real**: «el catálogo de Sec. 3.2 no ofrece marco» — justo lo que C4 y C5 cambian |

**La corrida estrecha de C0 se conserva intacta**, con la misma línea de comando y los
mismos dos archivos, para que el diff histórico siga siendo comparable.

**`entradas_ampliadas.json` es un FIXTURE, no datos de proyecto.** El TW y el caudal de
C-01 están ahí para **ejercitar caminos de código**; no son una medición de campo ni
pretenden serlo, y ninguna constante `[N]` puede apoyarse en ellos.

Los diez archivos se comprobaron **deterministas**: dos corridas consecutivas del script
producen bytes idénticos.

### La auditoría de C3 encontró que faltaba el eje que motivaba todo

El README y el commit de C3a invocan como motivo del ensanche que *«la rama de error
necesita un `--declarar` para alcanzarse»* —la regresión de C1—, y las tres corridas nuevas
usaban `--datos-externos` y **ninguna usaba `--declarar`**. El único eje que justificaba el
ensanche era el único que no se ensanchó.

Corregido: una **cuarta corrida** fuerza un diámetro de arranque negativo con el comando
exacto con que se reprodujo aquella regresión, y captura `cli_rama_error.txt` e
`informe_rama_error.json`. Medido: la cadena `Dato invalido en 'D': el diametro debe ser
positivo` aparece **3 veces en el CLI y 12 en el JSON**. Un renombre del `campo` o del
`motivo` —que es exactamente lo que C1 hizo sin verlo— ahora mueve el diff.

**Son 12 archivos**, los 12 deterministas.

## Lo que ensanchó C4: la quinta corrida, que no es la CLI

`punto_cajon.py` resuelve **una sección rectangular con una carta de cajón de la Tabla A.1
— Forma 2 —** y publica `memoria_punto_cajon.html`: un `<pre>` con los números que la
memoria no imprime (los dos HW, el que gobierna, las dos velocidades, q\*, h_o) más los
**siete pasos de memoria** pintados por el mismo `M11.bloque_pasos` de producción.

**Por qué no pasa por la CLI, que habría sido lo natural.** Porque la CLI todavía no puede
producir un cajón: `MD.disenar_material` construye `SeccionCircular(D)` sobre la progresión
de diámetros de M2, y abrir ese catálogo al marco es **C5**. El límite de alcance de C4 lo
dice con todas las letras. La alternativa era dejar la ceguera abierta una sesión más.

**Qué cierra, medido.** Hasta C3.5 la mutación «cablear `forma = 1`» no movía un byte,
porque las tres cartas circulares del catálogo son Forma 1. Vuelto a medir con esta corrida:

| Mutación | Antes | Ahora |
|---|---|---|
| `forma = FORMA_1` en `_pasos_hidraulicos` (la **etiqueta**) | no movía nada | **mueve `memoria_punto_cajon.html`** |
| la Forma 2 deja de bifurcar en el **cálculo** (se aplica la ec. A.1) | no movía nada | **HW de entrada 1.576717 m → 3.031241 m** |

**NO ES UN DISEÑO, y el driver lo lleva escrito.** Es un fixture, igual que
`entradas_ampliadas.json`. Toma prestadas tres decisiones que son de C5 sólo para poder
correr —la fila de la Tabla Nº 09 (`concreto_afinado`), la carta de HDS-5 y el `ke_entrada`
del bloque de tubo (regla vinculante #11)— y no pasa por la Fase 5: no hay verificaciones,
ni elección de material, ni iteración de catálogo.

**Son 13 archivos**, los 13 deterministas.

### Lo que la ventana sigue sin mirar, y queda dicho

- **El código de salida**: los cuatro comandos llevan `|| true`. Una regresión de exit code
  es invisible.
- **`--pdf` y `--criterios`**: sin cobertura.
- ~~**Ningún test consume esta línea base.**~~ **CERRADO**: `tests/test_linea_base.py` corre
  el script contra un destino temporal y compara. Es la razón de que `regenerar.sh` admita
  un argumento de destino — sin él, el test tendría que repetir los cuatro comandos y
  habría **dos** definiciones de la línea base que podrían divergir.

  **Lo que el test sí ve y lo que no, medido con tres mutaciones:** ve invertir la etiqueta
  de ecuación (la que dejaba la suite verde) y ve renombrar el `motivo` de un
  `DatoInvalidoError` (la regresión de C1). ~~**No** ve cablear `forma = 1`.~~ **CERRADO en
  C4** con la quinta corrida: ver el bloque de arriba, con las dos mutaciones vueltas a
  medir. Las dos capas siguen siendo complementarias — los tests unitarios cubren caminos
  que el corredor no recorre —.
- **La memoria generada no lleva la advertencia de fixture.** Quien abra
  `memoria_perfil_ancha.html` suelto ve una memoria completa con TW = 0.300 m y nada que
  diga que es una sonda; la advertencia vive en este README y en el script.

## Lo que movió E-A (2026-09-21), y por qué no es una regresión

E-A trajo el **perfil de la lámina de agua por paso directo** (`M4.perfil_lamina`,
pasos 4.3c y 4.3d) y cerró NOR-HDS-05. Diez de los 13 archivos se regeneraron, y el
diff se lee entero así:

- **Ningún número de cálculo se movió en los puntos que siguen dimensionando.** A-01 y
  A-02 (ancha) son barriles supercríticos con TW < y_c: la S1 desde y_c tiene longitud
  cero, el remanso no alcanza la entrada y la entrada gobernaba y sigue gobernando.
  Cambia lo que se IMPRIME: la línea `Perfil` de `cli_perfil_ancho.txt`, las diez claves
  `perfil_*` del bloque `diseno` del JSON y los dos pasos nuevos en las memorias.
- **B-01 (ancha) deja de dimensionarse**, y es un resultado, no una pérdida: su TW de
  1.00 m (fixture) ahoga un barril de 0.90 m —a D = 0.90 va LLENO y V1 no cumple— y en
  todo D mayor la S1 arranca en el TW, llega a la entrada y deja `V_min = Q/A(TW)` entre
  0.06 y 0.11 m/s < 0.25: V2 no cumple en ningún escalón y el punto termina en
  `DisenoNoFactibleError` (motivo V2 en la traza). Hasta E-A salía «dimensionado» a
  1.05 m con V1/V2 DIFERIDAS por «método no evaluable», que era lo que EXT-3 declaró
  provisional. `resumen_perfil_ancho.csv` lo refleja (fila B-01 vacía) y el resumen pasa
  de 3 a 2 dimensionados.
- **Desaparecen todos los bloqueos `MetodoNoEvaluableError`** (V1, V2 y «carga HW») de
  las cuatro corridas de la CLI: en la estrecha los tres circulares llegan otra vez a V5
  y se detienen ahí (los `motivo` de la traza en `informe_expediente.json` pasan de
  «método no evaluable» a `CriterioPendienteError('remanso_derecho_via')`); «Diferidas
  por alcance» baja de 14 a 8 (estrecha) y de 13 a 10 (ancha).
- `criterios_sha1` cambia porque `criterios_adoptados.py` reescribió los textos de
  `geometria_control_salida` (la premisa ahora se mide); `hoja_ruta_sha1` por la
  enmienda de la v8 §4.1/§4.3.
- **Ningún número de calculo se movió en `memoria_punto_cajon.html`**: el marco gana los
  dos pasos del perfil (M2 desde y_c que llega a la entrada) y el HW efectivo del
  control de salida es el del remanso, porque su aproximación queda bajo 0.75·H; la
  aproximación misma (1.045982117 m, el dorado de EXT-2) sigue impresa en el paso 4.3 y
  viaja en `perfil_HW_aproximado_m`.

## Lo que movió E-B (2026-09-21), y por qué no es una regresión

E-B no tocó ningún módulo de cálculo: trajo los editores tipados de la pestaña 2, el
comparador de dos `informe_json`, la pareja responsable/evidencia y el índice de la
memoria. Se regeneró por dos cambios de FORMATO, medidos con `diff`:

- **`informe_perfil_ancho.json` e `informe_expediente.json`**: cada fila de
  `criterios.bloquearon` lleva dos claves nuevas, `responsable` y `evidencia`,
  derivadas de la ficha por `src/responsable.py` (E13 reducido). Ningún otro byte del
  JSON se movió; `informe_rama_error.json` no cambia porque esa corrida no tiene
  bloqueantes por criterio.
- **Las tres memorias de la CLI** (`memoria_perfil.html`, `memoria_perfil_ancha.html`,
  `memoria_expediente.html`): el marcador `%%indice` (el `<nav class="indice">` con una
  entrada por `<h2 id>` de la plantilla y una por punto), las tres reglas de estilo del
  índice y el `id="punto-<id>"` de cada bloque de punto. `memoria_punto_cajon.html` no
  cambia: el driver imprime pasos por `M11.bloque_pasos`, no la plantilla entera.
- Los cuatro `cli_*.txt`, los dos `resumen_*.csv` y `informe_rama_error.json`: idénticos.

El comparador de E14 es desde esta sesión el segundo consumidor de esta línea base:
`tests/test_linea_base.py` compara los dos JSON comprometidos con los recién generados
por `comparador.comparar` además de byte a byte, y tiene que decir IGUALES.

## Regenerada en PF-1 (2026-09-21): el recuento de criterios, nada más

PF-1 abrió el criterio [A] de perfil `hw_entrada_fuera_de_rango` (PC-03) y el
corredor del repositorio no lo invoca —su S* ronda 0.38 m/m y las pendientes
del corredor son 0.006–0.008—, de modo que **ningún número de cálculo se
movió**. Lo que cambia, medido con `git diff`: la huella `criterios_sha1` de
los tres JSON, la lista de criterios sin valor que los JSON y las memorias
imprimen (entra la clave nueva) y el recuento «74 criterios declarados, 35
todavía sin valor» → «75 / 36» en las tres memorias. Es el mismo movimiento de
FORMATO que EXT-7 declaró al abrir los dos criterios del cabezal.

La parte 2 de PF-1 (los ajustes del auditor adversarial) la movió otra vez y
sólo en formato: `hoja_ruta_sha1` (la nota «Corregido (PF-1)» de la v8 §4.2),
`criterios_sha1` (la `justificacion` del criterio nuevo) y tres claves nuevas
en el bloque `diseno` del JSON —`hw_entrada_piso`,
`hw_entrada_HW_sobre_D_formula`, `hw_entrada_S_limite_m_m`—, las tres en
`null` porque ningún punto del corredor adopta el piso.

## Regenerada en PF-4 (2026-09-21): formato alrededor de V2b, ningún número

PF-4 sacó a `criterios_adoptados.py` el régimen con que V2b aplica el indicador
de HDS-5 §5.3.3 (`regimen_v2b`, valor de archivo `umbral_duro`: la conducta
de S20), de modo que **ningún número de cálculo se movió**: los dos puntos que
llegan a V2b (A-01 y A-02) tienen `S_conducto = S_cauce` y C-01 se detiene
antes, en los siete del cajón. Se midió con el comparador de E-B
(`src.comparador.comparar`) sobre los tres JSON de `a96bbec` frente a los
regenerados, y cada diferencia es de una de estas clases:

- `criterios_sha1` (el criterio nuevo), en los tres JSON; la huella de la
  hoja de ruta cambia también, por la nota «Corregido (PF-4)» de la v8 §5.2,
  pero sólo aparece en las tres memorias: el JSON no la lleva;
- la clave nueva `veredicto` de cada verificación (`cli._verificacion_json`:
  `cumple` dice si el punto se detiene y `veredicto` qué juzgó la memoria;
  bajo `indicador_con_aviso` difieren a propósito), 26 en el JSON ancho y 4
  en los otros dos;
- el texto de `NUMERAL_V2B` en las dos filas V2b (ya no dice «por decisión
  conservadora del proyecto» sino que nombra el criterio), también en
  `cli_perfil_ancho.txt`;
- `regimen_v2b` entre los criterios usados y en la lista
  `verificacion_pendiente` (21 → 22), en el JSON ancho y el de expediente;
- en las tres memorias: el CSS `.indicador` / `tr.fila-indicador`, el
  recuento «75 criterios declarados» → «76», la huella, el bloque de umbrales
  (la «aplicación» de V2b nombra el criterio), la elección del régimen en el
  paso F5.V2b de A-01 y A-02, la ficha de `regimen_v2b` en el bloque de
  criterios y el fundamento `F5.V2b.REGIMEN` en el anexo.

Lo que la ventana NO ve, y queda dicho: el régimen `indicador_con_aviso`,
que ningún punto de la línea base declara. Lo mide
`tests/test_pf4_regimen_v2b.py` con C-01 y la pendiente de sonda (0.004
frente a 0.006) por la CLI real, en las dos direcciones: bajo el valor del
archivo los tres marcos se descartan por V2b; bajo aviso C-01 dimensiona con
el marco 1.20 × 0.90 m, V2b sale `cumple=True` con veredicto `indicador`, y
la memoria imprime el literal del 5.3.3 desde el registro con la marca de
aviso.


## Regenerada en T-0 (2026-11-11): formato, y ningún número

T-0 de la cadena T (`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`) no toca
fórmulas ni umbrales: corrige textos, renombra un código de paso con alias,
cambia dos citas de fórmula y enmienda la hoja de ruta. La línea base se
regeneró y se comparó archivo por archivo contra la de `c2262a2`, troceando
cada HTML por etiquetas. **Seis de los trece archivos no cambian un byte**:
los cuatro `cli_*.txt`, los dos CSV de resumen —que son donde viven el
diámetro, las velocidades, el HW y el control de cada punto— y
`entradas_ampliadas.json` aparte. Lo que cambia, entero:

- **Los tres JSON: una sola línea cada uno**, la huella `criterios_sha1`
  (`criterios_adoptados.py` cambió comentarios y los textos `fuente` de dos
  fichas). Ningún otro campo: los diámetros, tirantes, velocidades y cargas
  son los mismos números, dígito a dígito.
- **Las tres memorias de la CLI, 29 cambios cada una en 17 clases**:
  - «(v7)» → «(v8)» en el pie y en la tabla de trazabilidad: M11 lee la
    versión del encabezado de la hoja de ruta, que T-0 corrigió;
  - las dos huellas, `hoja_ruta_sha1` (la v8 enmendada) y `criterios_sha1`;
  - el código de paso `F4.YC_RECT` → `F4.YC`, en el rótulo del paso, en su
    remisión y en el ancla de su ficha del anexo (4 + 3 + 1);
  - la procedencia de la fórmula del tirante crítico, que no existía, en
    cada paso 4.2.1 (3): «num. A.3.1 · … · pág. impresa A.3 · PDF 192»;
  - la procedencia de la fórmula del paso 4.4, de «num. A.2, A.2.1 · INLET
    CONTROL EQUATIONS» a «num. 3.3.5 · Evaluation of Results · pág. impresa
    3.25 · PDF 107» (3), y esa cita entre las del paso (3) y las del
    fundamento `F4.CONTROL` (1);
  - las dos citas nuevas en el anexo de citas, con su frase literal (2), y
    la de la A.3.1 entre las del fundamento `F4.YC` (1);
  - los textos de `v_max_tmc` y `v_max_hdpe` en el bloque de criterios: el
    campo `fuente` de cada uno (1 + 1) y su `tabla_pendiente` (2), que dejan
    de decir que WSDOT es una fuente ausente.
- **`memoria_punto_cajon.html`, 5 cambios**: el código de paso y su remisión,
  y las dos procedencias de fórmula.

**Diámetros movidos: ninguno.** A-01 y A-02 siguen en Ø 0.90 m de concreto
reforzado en la corrida ancha de perfil, y los otros puntos se detienen
donde se detenían.

## Regenerada en T-2 (2026-11-11): una verificación nueva, avisos y textos; ningún número

T-2 de la cadena T (hidráulica: pendiente del barril, borde libre bajo TW,
tailwater, cartas de HDS-5, criterios con respaldo). Se comparó con el
comparador de E-B (`comparador.comparar`) cada JSON contra el de `87d1ce7`, y
los dos CSV de resumen byte a byte. Lo que cambia, entero:

- **Los dos CSV de resumen: nada.** Ni un byte.
- **Los tres JSON:**
  - `criterios_sha1` (tres criterios nuevos, dos con valor de archivo nuevo);
  - por punto, las claves nuevas `datos_declarados.acceso_mantenimiento_previsto`
    (`null`: nadie lo declara), `tw_seccion_receptor` y `avisos`;
  - la verificación **V10** (pendiente del conducto) en los dos puntos que
    llegan a la Fase 5 en la corrida ancha de perfil, A-01 y A-02: cumple en
    los dos (0.006 y 0.008 contra 0.10), y va detrás de V4b;
  - en el bloque de criterios: `pendiente_minima_conducto`,
    `pendiente_maxima_conducto` y `borde_libre_bajo_tw_ahogante` entre los
    usados —los dos de pendiente también en la corrida de expediente, donde
    V10 se evalúa antes de que V5 se detenga—; `regimen_v2b.valor` de
    `umbral_duro` a `indicador_con_aviso`; `hw_entrada_fuera_de_rango` deja
    la lista de los sin valor (36 → 35) y `verificacion_pendiente` pasa de 22
    a 23;
  - los textos `fuente` y `mensaje` del bloqueo de `embocadura_cajon` (la
    ficha dice ahora dieciocho filas de cajón, con la Carta 13).
- **Los cuatro `cli_*.txt`:** la línea nueva del RESUMEN, «Verificaciones con
  aviso: 0», en los cuatro; la fila `[OK] V10` de A-01 y A-02 (corrida
  ancha); la línea `aviso: TW del receptor: seccion adoptada [A] por falta de
  levantamiento…` en los tres puntos cuyo TW sale de la vía 4 (corrida
  estrecha y rama de error); y el texto `fuente` de `embocadura_cajon`.
- **Las tres memorias de la CLI:** las dos huellas (`hoja_ruta_sha1`,
  `criterios_sha1`), el recuento «79 criterios declarados, 36 todavia sin
  valor» → «82 … 35», la fila «Verificaciones con aviso» del resumen, la fila
  V10 del bloque de umbrales y de la tabla de cada punto que llega a la
  Fase 5, el aviso de la sección adoptada en el paso 1.3, las fichas de los
  criterios usados y las citas nuevas del anexo.
- **`memoria_punto_cajon.html`, una línea:** la traza del punto, por el texto
  de la ficha de `embocadura_cajon` y la cita del num. 4.1.1.3.7 d) en el
  paso de V2b.

**Diámetros movidos: ninguno, y los mismos puntos dimensionan.** A-01 y A-02
siguen en Ø 0.90 m de concreto reforzado en la corrida ancha de perfil (HW
1.0420 y 0.5720 m, los mismos dígitos); B-01 sigue sin cerrar por V1/V2 con
el TW declarado de 1.00 m, y C-01 se detiene donde se detenía, en
`embocadura_cajon`. El cambio de `regimen_v2b` no alcanza a ningún punto de
estas corridas: el único con `S_conducto < S_cauce` es C-01, que no llega a
la Fase 5 sin los criterios del cajón. Y `borde_libre_bajo_tw_ahogante`
queda en `no_cumple` por decisión del dueño del proyecto, que es la conducta
anterior: con `aviso`, A-02 pasaría a dimensionarse en la corrida estrecha
(ficha `T2-02` de `docs/decisiones_diferidas.md`).

## Regenerada en T-4 (2026-11-11): más materiales evaluados, ningún diámetro ni veredicto

T-4 de la cadena T cambia de dónde salen el espesor de pared, el tope de
diámetro, el n del HDPE y la etiqueta de `v_max_tmc`, y añade la matriz de
durabilidad. **Antes y después se midieron las cuatro corridas**, comparando
JSON ruta a ruta —en la rama contra `87d1ce7` y, al integrar detrás de T-2,
otra vez contra `ad5cb97`, con los valores de archivo de T-2 ya presentes—:
por punto, el material y la sección
adoptados, el código, el estado, el veredicto, el valor obtenido y el
admisible de cada verificación, y el tipo de cada bloqueo. **Son idénticos en los doce pares punto × corrida.**
Tres de los trece archivos no cambian un byte: los dos CSV de resumen —donde
viven el diámetro, las velocidades, el HW y el control— y
`memoria_punto_cajon.html`.

**Material y diámetro adoptados, antes → después:**

| Corrida | A-01 | A-02 | B-01 | C-01 |
|---|---|---|---|---|
| perfil ancha | concreto Ø 0.90 → **igual** | concreto Ø 0.90 → **igual** | sin dimensionar → igual | sin dimensionar → igual |
| perfil estrecha | sin dimensionar → igual | sin dimensionar → igual | sin dimensionar → igual | sin dimensionar → igual |
| expediente | sin dimensionar → igual | sin dimensionar → igual | sin dimensionar → igual | sin dimensionar → igual |
| rama de error | sin dimensionar → igual | sin dimensionar → igual | sin dimensionar → igual | sin dimensionar → igual |

**Diámetros movidos: ninguno. Veredictos movidos: ninguno. Valores admisibles
movidos: ninguno** —el de V9 sigue en 2.700 m: una primera versión de T-4 lo
llevó a 3.600 m y la auditoría adversarial lo refutó contra la fuente (por
encima de 2700 mm AASHTO M 170M no tabula diseño estándar)—.

Lo que cambia, clasificado:

- **La lista de materiales EVALUADOS (movimiento declarado, `INF-5.1.17`).**
  En la corrida ancha, B-01 pasa de 10 a 21 escalones: el concreto recorre
  los mismos 8; el TMC va ahora de 0.90 a 2.10 m (antes se detenía en 0.90 m
  por `DatoFaltanteError` de `espesor_pared_conducto[tmc]`) y el HDPE de
  0.90 a 1.35 m (antes, igual en 0.90 m). El punto sigue «no factible», con
  el mismo tipo de bloqueo, y su motivo cambia de texto: el TMC termina como
  el concreto, en la clave que alcanza la subrasante; y el del HDPE dice
  ahora cuántos escalones se evaluaron y desde cuál no («NO SE EVALUO desde
  Ø 1.35 m hasta el tope…» por la fila que la Table A12-11 de AASHTO LRFD no
  trae). En las otras tres corridas el motivo de los puntos de tubo cambia
  de texto por la misma razón, y el HDPE de 0.90 m de A-01 en la de
  expediente se evalúa e incumple V1 con su n máximo de 0.015 (`INF-3.2.1`).
- **V9 de A-01 y A-02 (corrida ancha): mismo admisible, otro criterio.**
  `D_max_catalogo` [A] → `D_max_norma_producto` [C] (`INF-3.3.1`), con la
  clave nueva `diseno.dimension_max_criterio` en el JSON.
- **Formato — durabilidad.** Cada punto que pasa la Fase 2 gana en el
  volcado la línea «Sec. 3.3 durabilidad: sin ensayos, matriz no aplicada» y
  la del suelo de fundación, el bloque «Durabilidad de los materiales
  (Sec. 3.3)» en la memoria y la clave `durabilidad` en el JSON. La línea
  del suelo dice que SM, SP-SM y ML no están en el conjunto declarado
  deficiente, que eso no los califica como aptos y remite al Art. 38 de la
  E.050 (`INF-5.1.9`). **Los tres puntos con TMC candidata (A-01, A-02,
  B-01) ganan además el aviso fijo del Manual de Hidrología** —núm.
  4.1.1.3.7 f) y g): el Manual no recomienda alcantarillas metálicas en
  condiciones muy agresivas—, que no depende de ningún ensayo; C-01, donde
  la TMC no es candidata, no lo lleva.
- **Criterios usados.** Sale `D_max_catalogo` (opcional y sin valor: nadie
  lo declara) y entran `D_max_norma_producto`, `corrugacion_y_espesor_tmc` y
  `sucs_fundacion_deficiente`; cambian el valor y la etiqueta de
  `n_manning_hdpe` ([N→] (0.010, 0.013) → [C] (0.009, 0.015)), la etiqueta
  de `v_max_tmc` ([C] → [A]) y los textos de `v_max_hdpe`,
  `espesor_pared_conducto` (gana la entrada del HDPE) y `D_max_catalogo`.
  En `verificacion_pendiente` sale `D_max_catalogo` y entran los dos
  primeros.
- **Huellas y recuento.** `criterios_sha1`, `hoja_ruta_sha1` (la v8
  enmendada) y el recuento de criterios declarados en las memorias, 82 → 88 sobre el
  árbol de T-2 (seis de T-4; los dos
  últimos, de la auditoría: `suelo_agresivo_acero_lrfd` y
  `suelo_agresivo_lrfd_sobre_tmc`, que sin ensayos nadie invoca); los
  criterios sin valor siguen siendo los que eran (35).
- **V7 (corrida ancha).** El paso de flotación gana la elección
  `F3.D_EXTERIOR`, que dice de dónde salió el espesor; el número no cambia.

## Regenerada en T-1 (2026-11-12, integrado detrás de T-2 y T-4): el origen del caudal y un aviso; ningún número

T-1 de la cadena T crea la Fase 1-bis (`src/modulos/MH_hidrologia.py`): el caudal de
las Familias A y B se puede **calcular** dentro del programa con `--cuencas` y
`--estacion`. Las corridas de esta línea base **no traen** esas dos entradas y sus
puntos de Familia A y B llevan `Q_m3s` lleno: el caudal sigue entrando declarado y
ningún cálculo cambia. La línea base se regeneró sobre el árbol fusionado y se midió
contra `7fb7926` (T-0 + T-2 + T-4) en los **doce pares punto × corrida** de los tres
JSON: `dimensionado`, material, tipo, sección, norma de producto, caudal, pendiente,
carga y control gobernante del diseño; código, estado, veredicto, valor obtenido y
admisible de cada verificación; fase, etapa, tipo, criterio y campo de cada bloqueo;
las iteraciones enteras, el periodo de retorno, la protección de salida, la geometría,
el bloque estructural, la durabilidad, la sección del receptor y los datos declarados
son **idénticos**. Diez de los 13 archivos cambian; los dos CSV de resumen y
`memoria_punto_cajon.html` no cambian un byte. Lo que cambia, entero:

- **Los cuatro `cli_*.txt`, seis líneas nuevas cada uno**, dos por cada punto de
  Familia A y B: «Fase 1b Q declarado por el estudio hidrológico: Q = … | Q/A = …
  (C*I = …)», y la línea `aviso:` permanente del caudal declarado —el criterio
  `homogeneidad_serie_fen` rige sólo el caudal que el programa calcula, y al declarado
  no se le atribuye ningún tratamiento—, que sale con los demás avisos del punto
  (`InformePunto.avisos()`, de T-2). La línea «Verificaciones con aviso» del RESUMEN
  no cambia: un caudal declarado no dispara ningún indicador de la hidrología.
- **Los tres JSON, en cinco clases** (medido ruta a ruta):
  - la clave nueva `caudal` de cada punto: `origen` «declarado», la leyenda, el caudal
    específico Q/A, la lámina equivalente, `tratamiento_fen` en `null`, el aviso y el
    paso `1b.8`; `null` en C-01, que es Familia C;
  - `avisos` de A-01, A-02 y B-01: una entrada más, la primera, con ese aviso;
  - `clasificacion.origen_del_caudal` de los tres (deja de nombrar a `Tc.py` y nombra
    la columna `Q_m3s` y a `MH_hidrologia`) y `clasificacion.TR_fundamento` de B-01,
    que cita ese mismo texto;
  - `criterios.verificacion_pendiente`: tres entradas más
    (`distribucion_precipitacion_maxima`, `relacion_intensidad_duracion`,
    `coeficiente_uniformidad_temez`). Las listas de criterios **usados** y **sin
    valor** no cambian: ninguna corrida invoca la hidrología;
  - la huella `criterios_sha1`.
- **Las tres memorias de la CLI:** las dos huellas (`criterios_sha1`; `hoja_ruta_sha1`
  por las notas de T-1 en la v8) y el recuento de criterios, de 88 a **95** (los siete
  de T-1, todos con valor de archivo: «35 todavía sin valor» no cambia); la fila
  «Familia» de la clasificación de A-01, A-02 y B-01, con el origen del caudal nuevo;
  el bloque nuevo «Caudal de diseño y su origen (Fase 1-bis)» de esos tres puntos —la
  leyenda, el aviso y el paso `1b.8` del caudal específico, que **no juzga** (sin
  umbral)—; la ficha de `umbral_area_quebrada_importante_ha`, cuya `justificacion` ya
  no se apoya en los puntos del fixture (`INF-5.1.3`; el valor y la ventana son los
  mismos); la ficha de `homogeneidad_serie_fen` entre los criterios sin valor
  (concepto, fuente y ventana nuevos); y el fundamento `FH.Q_ESPECIFICO` con sus dos
  citas (`MC_HHD.3.12.2`, `MC_HHD.3.13`) en el anexo.

**Diámetros movidos: ninguno.** A-01 y A-02 siguen en Ø 0.90 m de concreto reforzado
en la corrida ancha de perfil, B-01 y C-01 se detienen donde se detenían, y el periodo
de retorno de los tres puntos es el mismo (71, 71 y 35 años).

## Lo que movió T-6 (2026-11-12, integrado detrás de T-2, T-4 y T-1): la longitud del conducto, y con ella la caída, la cota de salida y el HW de salida

T-6 de la cadena T (geometría) **sí mueve números**, y cada uno tiene su
causa. La columna «antes» es la línea base de `5bca7c6` (T-0 + T-2 + T-4 +
T-1), contra la que se midió el árbol fusionado con el comparador de E-B
(`cli.py --comparar`) en los tres JSON y en los doce pares punto × corrida. Son los que dependen de la longitud del conducto, que pasa de
calcularse con la altura del eje para los dos taludes a calcularse **por
extremo** (criterio `[A]` `metodo_longitud_conducto` = `por_extremo`; HDS-5
núm. 2.2.4 b. y Figura 2.4, pág. impresa 2.8): el talud de la salida baja
`S·L` más que el de la entrada, y `L = [ancho + talud·(H_e + H_s0)] /
[cos(esviaje) − talud·S]` en vez de `(ancho + 2·talud·H_eje) / cos(esviaje)`.
Con el fondo de entrada igual al terreno —los cuatro puntos del fixture— las
dos fórmulas difieren sólo en el factor `cos / (cos − talud·S)`.

| Punto | L antes (m) | L ahora (m) | factor | Causa |
|---|---|---|---|---|
| A-01 | 18.6350 | 18.8694 | 1.0126 | talud 2.0 × S 0.006, esviaje 15° |
| A-02 | 18.2695 | 18.5677 | 1.0163 | talud 2.0 × S 0.008, esviaje 5° |
| B-01 | 18.4000 | 18.7755 | 1.0204 | talud 2.0 × S 0.010, esviaje 0° |
| C-01 | 21.2465 | 21.4446 | 1.0093 | talud 2.0 × S 0.004 (`S_conducto`), esviaje 30° |

De la longitud cuelgan, en la corrida ancha de perfil (`--datos-externos`), los
únicos dos puntos que dimensionan:

| Punto | Magnitud | Antes | Ahora | Causa |
|---|---|---|---|---|
| A-01 | caída `S·L` (m) | 0.1118 | 0.1132 | `0.006 × L` |
| A-01 | cota de salida (msnm) | 41.9882 | 41.9868 | `42.10 − caída` |
| A-01 | HW de salida (m) | 0.9929 | 0.9925 | +0.0010 de fricción, −0.0014 de caída |
| A-01 | HW gobernante (m) | 1.0420 | 1.0420 | **no cambia**: gobierna la entrada |
| A-02 | caída `S·L` (m) | 0.1462 | 0.1485 | `0.008 × L` |
| A-02 | cota de salida (msnm) | 39.7038 | 39.7015 | `39.85 − caída` |
| A-02 | HW de salida (m) | 0.5618 | 0.5596 | fricción y caída, como en A-01 |
| A-02 | HW gobernante (m) | 0.5720 | 0.5720 | **no cambia**: gobierna la entrada |

Con el HW de salida se mueven, en el bloque `diseno` del JSON, las dos claves
que son el mismo número dicho de otra manera: `perfil_HW_aproximado_m` (igual
al HW de salida) y `HW_sobre_D_salida` (A-01 1.1032 → 1.1028; A-02 0.6242 →
0.6218).

Y en la corrida estrecha (sin TW declarado, `informe_rama_error.json`), el TW
de la vía 4 de la Sec. 1.3, que se mide sobre el fondo de la **salida** y por
eso sube lo que la salida baja: A-01 1.1118 → 1.1132 m, A-02 1.1962 → 1.1985 m,
B-01 1.4840 → 1.4878 m. Ningún punto dimensionaba en esa corrida ni dimensiona
ahora; la progresión de secciones probadas y el motivo de cada descarte son los
mismos.

**Diámetros movidos: ninguno.** A-01 y A-02 siguen en Ø 0.90 m de concreto
reforzado, control de entrada, con las mismas verificaciones de `5bca7c6`
en «cumple», más G3; B-01 y C-01 siguen sin dimensionar por lo mismo que
antes, con las mismas iteraciones y el mismo tipo en cada bloqueo. Y la
banda de pendiente de T-2 (0.0 a 0.10), que M7 aplica desde T-6 a la
pendiente del cauce, **no mueve ninguna**: las del fixture van de 0.006 a
0.010 y los cuatro puntos conservan su origen (cauce, o declarada en C-01). Medido
además con el método anterior declarado (`--declarar
metodo_longitud_conducto=terraplen_simetrico`): reproduce las longitudes de la
columna «antes» dígito a dígito.

**Un bloqueo cambia de etapa, no de causa.** C-01 en las dos corridas
estrechas no trae pendiente (ni `S_cauce` ni `S_conducto`). Antes se detenía
en «tirante en el receptor (TW, Sec. 1.3)», que era la primera etapa en
pedirla; ahora se detiene una etapa antes, en «longitud del conducto (7.B)»,
porque la longitud por extremo necesita la pendiente. El dato que falta es el
mismo (`DatoFaltanteError` sobre `S_cauce`), y su `longitud_m` pasa de 21.2465
a `null`.

Lo demás es **formato**, y entra por los cinco puntos del prompt:

- **Verificaciones.** G2 lleva criterio (`desnivel_minimo_entrega_m`, 0.0 m:
  el admisible sigue siendo el fondo del receptor), numeral nuevo y paso de
  memoria; aparece **G3**, el aviso de esviaje (`esviaje_max_grados` = 45°),
  en «cumple» para 15° y 5°.
- **JSON, bloque `geometria`.** Claves nuevas: `longitud_calculo` (método,
  bordes de plataforma, altura de terraplén y proyección de talud por
  extremo, semilongitudes), `S_conducto_origen`, `longitud_a_la_clave_m`
  (14.676 m en A-01, 14.487 m en A-02), `desnivel_entrega_m`, `avisos` y
  `tamizado.provisional`. El `origen` de `longitud_m` nombra el método.
- **Aviso de fondo adoptado.** Los cuatro puntos adoptan el fondo de entrada
  igual al terreno: el mensaje de 7.A termina en «PROVISIONAL: fondo de
  entrada adoptado igual al terreno de plataforma: medir en el cauce» y el
  aviso sale con los demás del punto. Las cotas de rasante mínima **no
  cambian** (44.092 y 41.372 msnm).
- **Los avisos salen por `InformePunto.avisos()`, una vez.** En los cuatro
  `cli_*.txt` cada punto con longitud calculada gana dos líneas `aviso:`
  —el fondo adoptado y la plataforma horizontal—, también B-01 y C-01, que
  no dimensionan: su longitud ya entró al diseño de cada escalón. Las mismas
  dos entran en la lista `avisos` del punto en el JSON. G3 no se disparó en
  ningún punto (15°, 5°, 0° y 30° contra 45°) y por eso «Verificaciones con
  aviso» no cambia.
- **V10.** La procedencia de `S_conducto` en su paso y su nota dicen ahora el
  reparto con M7 (la pendiente del cauce fuera de la banda la sustituye el
  extremo; V10 sólo la incumple una declarada), y lo mismo el texto de
  `UMBRALES_DE_VERIFICACION`. Ningún valor de V10 cambia.
- **Criterios usados.** Entran `metodo_longitud_conducto`,
  `desnivel_minimo_entrega_m` y `esviaje_max_grados`; y en
  `informe_rama_error.json` también `pendiente_minima_conducto` y
  `pendiente_maxima_conducto`, que M7 lee antes de la Fase 4 aunque el punto
  no llegue a V10.
- **Memorias.** Los pasos 7.B.1 a 7.B.5 de los puntos que dimensionan y los
  7.B.2 y 7.B.3 de los que no; los de G2 y G3 en el desarrollo de
  verificaciones; los fundamentos y las citas de esos pasos en el anexo; tres
  criterios más entre los usados; y las dos huellas (`criterios_sha1`,
  `hoja_ruta_sha1`: la v8 lleva la nota «Corregido (T-6)» en §7.B).
- **Sin cambio de un byte:** los dos CSV de resumen,
  `memoria_punto_cajon.html` y `entradas_ampliadas.json`.

**Lo que la columna «L ahora» NO es, dicho junto al aviso «medir en el
cauce».** Los cuatro puntos adoptan el fondo de entrada igual a
`cota_terreno`, que es el terreno **en el eje** de la vía
(`docs/contrato_entradas.md`). El método por extremo ancla esa cota en la
**entrada** del conducto y carga toda la caída aguas abajo. Para un lecho de
pendiente `S` que pasara por esa cota en el eje —la entrada algo más alta, la
salida algo más baja— la longitud de A-01 sería **18.638 m**: la fórmula
anterior daba 18.635 y la nueva 18.869 (+0.232 m). El cálculo no se cambia
—el perfil adoptado ya tenía ese sesgo en la cota de salida, y con
`cota_fondo_entrada` medida es exacto—, pero el paso 7.B.3 lo escribe con su
número en cada punto de fondo adoptado. Y medir **al fondo** es elección del
proyecto, no de la fuente: es la cota superior de la longitud, y no el lado
seguro por construcción (en A-01 el HW de salida es 0.9925 m con la longitud
al fondo y 1.0002 m con la longitud a la clave; gobierna la entrada, 1.042 m).

**Y dos avisos más por punto**, que dejó el auditor adversarial de T-6 y que
son formato: «plataforma tomada horizontal: no se declaró `bombeo` ni
`peralte`…» con lo que cada 1 % de bombeo acortaría la longitud (20.1 cm en
A-01), entre los avisos del punto, en `geometria.avisos` del JSON y en la nota
del paso 7.B.3; y el umbral de G2 cita la Lámina Nº 01 (carácter DEFINICIÓN)
en vez del numeral de la pendiente.

**Lo que movió el cierre de la integración (2026-11-12), que es formato.** Al
terminar la integración se regeneró otra vez sobre el árbol final, y contra la
generación anterior de la misma rama sólo cambian dos cosas: la huella
`criterios_sha1`, y el `concepto` de `pendiente_minima_conducto` y
`pendiente_maxima_conducto` en la lista de criterios usados de los tres JSON,
que deja de decir «la aplica V10» y dice el reparto con M7 («M7 eleva a ella /
limita a ella la del cauce y V10 juzga con ella la declarada»). Las otras dos
correcciones del cierre no tocan la línea base: el aviso de fondo adoptado de
un punto que no dimensiona sale ahora de la cota de entrada y no de la
longitud —en el fixture todos los puntos usan el método por extremo, cuya
longitud ya lo llevaba, y los cuatro `cli_*.txt` no cambian un byte—, y la
banda vacía, que sólo se alcanza burlando la puerta de los dos criterios, se
detiene como bloqueo del punto en la etapa «pendiente adoptada del conducto
(7.B.1)» en vez de tumbar la corrida.

## Regenerada en T-8 (2026-11-12): la Fase 6 de entrada y salida; ningún número de cálculo

T-8 de la cadena T (protección de entrada y salida, `INF-3.3.7`, `INF-5.1.13`). Se regeneró
sobre el árbol ya fusionado con T-6 y se midió contra la línea base de `7e74065`
(`tesis(T-6)`), diferencia a diferencia con el comparador de E-B y con `diff`:

- **Los tres JSON:** `criterios_sha1` (cinco criterios nuevos —`tipo_proteccion_entrada`,
  `duracion_caudal_pico_socavacion_min`, `lectura_coeficientes_socavacion_hec14`,
  `regla_espesor_longitud_proteccion_salida` y `referencia_profundidad_socavacion`— y los
  textos de `espesor_proteccion_salida` y `longitud_proteccion_salida`, que dicen desde T-8
  contra qué se contrastan, sin cambiar su valor). En `informe_perfil_ancho.json`, además,
  por cada punto que llega a la Fase 6 (A-01 y A-02): las claves nuevas de
  `proteccion_salida` (`requerida`, que va en `null` porque nadie declara el terreno;
  `froude_salida`; `velocidad_admisible`, `null`; `apron_hec14`; `filtro`;
  `clase_hec14_de_la_piedra`, clase 4 en los dos; `regla_espesor_longitud`, `manual`;
  `espesor_adoptado_m` y `longitud_adoptada_m`), los bloques nuevos `proteccion_entrada` y
  `socavacion_salida` (sin lecho declarado: «sin dato», con `referencia` y las dos cotas en
  `null`), los textos de dos de las tres advertencias de siempre (`ADVERTENCIA_FALTA_FILTRO`
  y `ADVERTENCIA_ALCANCE_HDS5`, que dejan de decir que HEC-14 no está) y los avisos nuevos
  de la Fase 6 en `avisos` (seis en A-01, cinco en A-02); y `tipo_proteccion_entrada` y
  `regla_espesor_longitud_proteccion_salida` entre los criterios usados.
- **`cli_perfil_ancho.txt`:** en A-01 y A-02, las dos advertencias con su texto nuevo, cuatro
  líneas de detalle de la Fase 6 (Froude «Fr_e … régimen por el tirante contra el crítico»,
  apron de HEC-14 como contraste, entrada, socavación para el desplante) y los avisos de la
  fase: tres por punto por falta de datos del sitio (terreno del receptor, terreno de la
  entrada, lecho); el del espesor bajo el piso de 2.0·D₅₀ de HEC-14 en los dos; en A-01 los
  dos del contraste con el apron —la longitud adoptada (5.00 m) es menor que la del apron de
  clase 4 (6·0.90 = 5.40 m) y el espesor adoptado (1.75·d₅₀ = 0.592 m) menor que su
  profundidad (2.2·0.35 = 0.770 m)—, y en A-02 el de la clase de la piedra adoptada (la Ec.
  10.4 pide la clase 1; la piedra de 0.274 m es de la clase 4, y con ella lo adoptado queda
  corto en longitud y espesor).
- **Las tres memorias de la CLI:** las dos huellas —`criterios_sha1` y `hoja_ruta_sha1`,
  esta por la nota «Ampliado (T-8)» de la Fase 6 de la v8— y el recuento «97 criterios
  declarados, 35 todavia sin valor» → «102 … 35»; en la ancha, el título «Fase 6 —
  Proteccion de entrada y salida», el filtro como requisito, la entrada, la socavación, los
  avisos de la fase y el desarrollo de los pasos que el fixture alcanza (6.1, 6.2, 6.3,
  6.5, 6.6, 6.6b y 6.9; los demás piden datos del sitio que no trae), las fichas de los criterios
  usados y las citas nuevas del anexo.
- **Sin cambio de un byte:** `cli_perfil.txt`, `cli_expediente.txt`, `cli_rama_error.txt`,
  los dos CSV de resumen, `memoria_punto_cajon.html` y `entradas_ampliadas.json`.

**Diámetros movidos: ninguno, y los mismos puntos dimensionan.** El bloque `diseno` de los
cuatro puntos es idéntico al de `7e74065` en los tres JSON: A-01 y A-02 siguen en
Ø 0.90 m de concreto reforzado en la corrida ancha de perfil; B-01 y C-01 se detienen donde
se detenían, con los mismos bloqueos. **Los números de Laushey no se movieron**: d₅₀ = 0.338
y 0.274 m, espesor 0.592 y 0.479 m, longitud 5.000 m. La Fase 6 corre después del
dimensionado y no lo realimenta; «Verificaciones con aviso» del RESUMEN no cambia, porque
ningún paso de la Fase 6 de este fixture tiene veredicto INDICADOR.
