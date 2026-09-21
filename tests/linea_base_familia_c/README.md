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
