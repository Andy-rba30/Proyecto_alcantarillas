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

Reproducible con el fixture del repositorio. Los tres datos declarados por
`--datos-externos` son **valores de sonda**, no datos de proyecto: sirven para llegar al
bloqueo, y ninguno se escribe en el CSV.

| Declarado para C-01 | Dónde para | Símbolo |
|---|---|---|
| *(nada)* | `DatoFaltanteError` · «Falta el dato `S_cauce`» en la etapa *tirante en el receptor (TW, Sec. 1.3)* | `cli._resolver_tw` → `PuntoCritico.exigir` |
| `Q_m3s` | igual que arriba | igual |
| `S_conducto` | `DatoFaltanteError` · «Falta el dato `Q_m3s`» en *material y diámetro (bucle de MD)* | `MD.disenar_punto` → `PuntoCritico.exigir` |
| `TW_m` | igual que la anterior | igual |
| `TW_m` + `Q_m3s` | `DatoFaltanteError` · «Falta el dato `S_cauce`» en *material y diámetro* | `MD.disenar_punto` → `PuntoCritico.exigir` |
| **`Q_m3s` + `S_conducto`** | **`DisenoNoFactibleError`** · «M2 (Sec. 3.4) no ofrece material candidato para la Familia C…» | **`MD._motivo_sin_candidatos`** |

**El par mínimo que llega al bloqueo real es `Q_m3s` + `S_conducto`.** `TW_m` es
redundante: declarar la pendiente cubre a la vez la vía de Sec. 1.3 y la que MD necesita.
El detalle está en §16.1-bis y §1.1 de `docs/ruta_familia_c.md`.

## Regeneraciones posteriores

- **C2** (`familiaC(C2)`): la memoria HTML cambia en **dos líneas, y ninguna es un
  número de cálculo**. (1) el SHA-1 de `criterios_adoptados.py`, porque ese archivo
  cambió; (2) el criterio `hds5_embocadura_hdpe`, que pasa a imprimir `forma = 1` junto
  a sus K, M, c, Y y Ks. Lo segundo es el efecto buscado: `ConstantesHDS5` gana el campo
  `forma` —la columna «Equation Form» de la Tabla A.1, que hasta C2 no se transcribía— y
  el contrato de memoria (§4.5) exige que nada de lo que se añade quede invisible en el
  reporte. El HW, los tirantes y las velocidades no se mueven: `git diff` sobre esta
  línea base da exactamente esas dos líneas.

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
