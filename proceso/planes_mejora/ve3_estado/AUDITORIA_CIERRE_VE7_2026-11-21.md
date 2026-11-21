# Auditoría independiente del cierre de VE-7 en `main` (2026-11-21)

Material de proceso (`proceso/`), no del entregable. Auditoría adversarial e
independiente del cierre final hecho en `main` de
`Andy-rba30/Proyecto_alcantarillas`: commits `5eccfe2` y `362beb4`, etiqueta
`respaldo-2026-11-20` y limpieza de ramas a etiquetas `respaldo/*`. No se
modificó ningún archivo del entregable. El plan de mejoras que salió de esta
auditoría está aparte, en `proceso/planes_mejora/11_PLAN_MANTENIBILIDAD_Y_USO.md`.

## Dictamen

**APROBADO CON CAMBIOS.** Las cuatro correcciones de `5eccfe2` son correctas,
están verificadas contra el código y no encubren ninguna regresión; `src/` no
tiene deuda introducida por el cierre. Hay que corregir dos cosas antes de
dar el cierre por terminado: **el sello del par de la suite no corresponde a
una corrida medida** (y no se reproduce), y **un test de rendimiento es
intermitente** en una máquina en reposo.

## 1. Entorno de la verificación

- Contenedor Linux (Ubuntu 24.04), 4 núcleos, 15 GB.
- `/usr/bin/python3.12` (3.12.3) con `requirements.txt` + `requirements-dev.txt`
  + `pytest-xdist`; Tk 8.6 (`python3-tk`); `xvfb-run -a`.
- `NORMAS_DIR=/home/user/andy-rba30/normas`: clon de `Andy-rba30/Normas`
  (22 PDF en `normas/`).
- Worktree limpio fuera del repositorio, desacoplado (`git worktree add --detach
  <scratchpad>/limpio2 362beb4`, `git status` vacío).

## 2. Revisión de commits y declaración

### a) `C-01` `E3-LRFD.est.e` — CORRECTO, medido

Se midió la causa variando **sólo** `espesor_pared_cajon` sobre la base
`juego_cabezal_de_la_regla` (la misma de §3.1 del anexo):

| `espesor_pared_cajon` | `fila_phi_estabilidad_cabezal` (muros → zapatas) | `factores_inclinacion_carga_portante` (aplicar → omitir) |
|---|---|---|
| 0.30 m (juego, VE7B-11) | `cumple` → `no cumple` | `cumple` → `cumple` |
| 0.25 m | `no cumple` → `no cumple` | `no cumple` → `no cumple` |
| 0.20 m (archivo) | `no cumple` → `no cumple` | `no cumple` → `no cumple` |

Cifras leídas del `informe_json` de C-01 con 0.30 m: `valor_obtenido` =
40.9399 kN/m, `valor_admisible` = 41.4585 kN/m (muros) y 33.1668 kN/m
(zapatas; razón 0.800, la de φ_τ 0.8 frente a 1.0), ancho de zapata 1.715 m,
`H_c` = 2.45 m. Coinciden al decimal con la prosa de §3.1, con el test y con
el informe de cierre. **El paso a `cumple` se debe a la pared de 0.30 m de
VE7B-11 y a nada más.** Los tres tubos circulares siguen en `no cumple` con
los dos [A].

### b) `test_los_juicios_del_anexo` — CORRECTO

Contadas las claves distintas por efecto en `docs/validacion_sensibilidad.md`:
MUEVE EL DISEÑO 11 barridos (10 claves; `v_max_concreto_eleccion` sobre dos
bases), MUEVE VEREDICTOS 27, MUEVE EL HW 2, LEÍDO SIN EFECTO MEDIBLE 38, NO
LO LEE LA CORRIDA 19: **11/27/2/38/19**, 97 barridos, como dice el test.

### c) `NO_LEIDO_PORQUE` — CORRECTO

- `demanda_sismica_licuefaccion` está en LEÍDO (el juego declara
  `licuefaccion_ems` desde `5f9a662`): su retirada es correcta.
- Ninguna fila dice «SIN RAZÓN ESCRITA».
- Las tres razones nuevas, contra el código:
  - `intervalos_de_clase_chi_cuadrado`: sólo lo lee `MH_hidrologia.py:1352`,
    dentro de la prueba chi-cuadrado del caudal calculado. ✔
  - `carga_viva_tubo_concreto_somero`: sólo lo lee
    `M8_estructural.lectura_del_tubo_de_concreto_somero` (`:1386`), llamada
    desde `_carga_viva_en_la_franja` (`:1434`) para el tubo de concreto con
    relleno menor de 2.0 ft. ✔
  - `empuje_sismico_muro_que_no_cede`: sus dos lecturas
    (`M9_cabezal.py:7362` y `:8525`) exigen `regimen == REGIMEN_NO_CEDENTE`
    (`reposo_rige` en `:8173` también lo exige). ✔

### d) `FH.RM_*` y `FH.C_SUBAREAS` — CORRECTO

`FH.RM_INTENSIDAD`, `FH.RM_C` y `FH.RM_CAUDAL` están en §2 de
`docs/indice_formulas.md` (líneas 183-185, corrida `materiales_y_ramas`); en
§4 sólo quedan `FH.C_SUBAREAS` y `FH.FACTOR_P24`, como exige el test.

## 3. Verificación real

| Comprobación | Resultado |
|---|---|
| GitHub Actions `44859160957` sobre `main` (`362beb4`), sin `NORMAS_DIR` | **success**, `9007 passed, 174 skipped` en 2 h 27 min |
| Suite completa, worktree limpio `362beb4`, `NORMAS_DIR` + Tk + xvfb, `-n 3`, una sola corrida | **`1 failed, 9167 passed, 13 skipped`** en 2 h 31 min 57 s |
| El test fallido, repetido solo con la máquina en reposo | 2 de 3 pasan (ver hallazgo H2) |
| Exportación (`git archive 362beb4`, sin `.git` ni `proceso/`): `test_indice_formulas`, `test_trazabilidad_csv`, `test_manifiesto_citas`, `test_ext9_paquete_servicio`, `test_t12_entregable` | `186 passed, 2 skipped` (los 2 de `test_t12_entregable` que exigen `git`, saltados diciéndolo) |
| `proceso/tests` | `145 passed` |
| `python3 -m proceso.verificar_sesion` | **No corrido aquí.** Lanza la suite completa dos veces en serie; queda a cargo del dueño en local, después de las correcciones |

Una primera corrida completa (`-n 4`) quedó en 8970 de 9181 tests sin ningún
fallo, pero la cortó el tope de 2 h de las tareas de segundo plano del entorno
y **no se usa** para el par.

Los 13 saltos son todos de `tests/test_familias_del_csv.py:174` (las
columnas que cada familia SÍ usa) y no dependen del entorno.

## 4. Ramas y etiquetas

- `origin` tiene una sola rama, `main`, en `362beb4` (la rama de esta
  auditoría, `claude/youthful-babbage-9njfr2`, se creó después y sólo lleva
  material de `proceso/`).
- `respaldo-2026-11-20` es una etiqueta anotada que apunta a `362beb4`.
- Las 51 etiquetas `respaldo/*` existen en el remoto. Con la historia
  completa (sin clon superficial): 28 están contenidas en `main` y 23
  conservan commits propios, entre 1 y 78 (respaldos WIP de agentes,
  `keen-cray-rhxzmg` con su fusión rota rehecha, y
  `tesis/orquestacion-estado`, archivada en `proceso/`). **Ninguna rama
  borrada perdió commits**: lo que no está en `main` está bajo su etiqueta.
- Las cabezas de los 46 PR fusionados (`#1` a `#46`) son alcanzables desde
  `main` y las etiquetas.

## 5. Hallazgos

| Id | Severidad | Hallazgo | Archivo y línea | Acción sugerida |
|---|---|---|---|---|
| H1 | **MEDIA** | El par del sello `9167 passed, 14 skipped` **no salió de una corrida completa**: se dedujo sumando a los 9007 del CI los 158 tests `-m pdf` y los 2 de `test_ext6`. Además **no se reproduce**: la corrida completa con `NORMAS_DIR` dio 9168 tests no saltados (9167 passed + 1 intermitente) y **13** saltos. Sin `NORMAS_DIR`, fuera de la marca `pdf` sólo saltan 2 tests (`test_ext6_registro_normativo.py:223` y `:250`): 13 + 158 + 2 = 173, no 174. El salto restante del CI es propio de su entorno y no de los PDF. Contradice la regla de `CLAUDE.md` de que el sello lo pone quien regenera con el par medido | `docs/indice_formulas.md:10`; `docs/trazabilidad.csv:1`; `proceso/bitacora_conteos_y_entorno.md` (fila «entregable, `5eccfe2`, con `NORMAS_DIR`») | Tras corregir H2, una sola corrida completa con `NORMAS_DIR` en árbol limpio y sellar con `python -m src.indice_formulas --escribir --suite "<par medido>"` y `python -m src.normativa.manifiesto --escribir --suite "<par medido>"`. Corregir la fila de la bitácora rotulándola como deducida. Par esperado en Linux con historia completa: **9168 passed, 13 skipped** |
| H2 | **MEDIA** | `test_pc10_import_cli_cabe_en_el_presupuesto_sin_weasyprint` es **intermitente**. Diez muestras de `import cli` con la máquina en reposo dieron 0.216 a 0.263 s frente a un presupuesto de 0.30 s (margen ~15 %). Falló en la corrida completa (0.390 s) y 1 de 3 veces en solitario. Puede volver rojo el CI o una demostración sin que nada haya cambiado | `tests/test_ext8_rendimiento_gui.py:82` (`PRESUPUESTO_IMPORT_CLI_S = 0.3`) y `:315-321` | Medir en el CI y en la máquina del dueño y fijar el presupuesto «con holgura sobre la medida», como ya dice la ficha EXT-8-01. Alternativas: más corridas para el mínimo o un presupuesto relativo. Declararlo en la ficha. No se toca sin confirmación del dueño |
| H3 | BAJA | La prosa de §3.1 lleva **cifras escritas a mano dentro del generador** (40.94, 41.46, 33.17, 1.715). Hoy son exactas, pero `test_el_anexo_de_sensibilidad_esta_sincronizado` regenera desde el mismo literal y no detectaría que el cálculo cambió | `tests/apoyo/sensibilidad.py:856-864`; `tests/test_t11_sensibilidad.py:338-340` (docstring) | Derivar las cifras de la medida (`estados_del_cabezal` y el `informe_json`) o añadir un `assert` sobre `valor_obtenido` / `valor_admisible` de C-01 con su tolerancia |
| H4 | BAJA | El bloque de estado del LEEME quedó **desactualizado**: dice que falta esperar el CI y luego el fast-forward, la etiqueta y la limpieza, todo ya hecho, y manda a «retomar desde `claude/optimistic-carson-ag7mwp`», rama ya borrada. `PROMPT_RETOMAR.md` también nombra ramas borradas | `proceso/planes_mejora/ve3_estado/LEEME.md:6-35`; `proceso/planes_mejora/ve3_estado/PROMPT_RETOMAR.md` | Cerrar el bloque: CI `44859160957` verde, `main` en `362beb4`, `respaldo-2026-11-20`, ramas en `respaldo/*`; retomar desde `main` |
| H5 | INFORMATIVA | Los sellos de `362beb4` se cambiaron editando la línea del sello, no regenerando con los comandos. Es aceptable porque los tests de sello leen el sello y comparan el cuerpo, y el cuerpo de `5bafd44` sincroniza en Linux, también en la exportación. Queda resuelto con la acción de H1 | `docs/indice_formulas.md:10`; `docs/trazabilidad.csv:1` | Ninguna aparte de H1 |

## 6. ¿Listo para entrega y sustentación?

- **Código de cálculo (`src/`)**: sin deuda introducida por el cierre. Las
  correcciones de `5eccfe2` sólo tocaron `tests/`, `docs/` y `proceso/`, y son
  correctas.
- **Entregable**: queda listo **después de H1 y H2**, que son una corrección
  de un test de la suite y un resellado, sin cambios en `src/`. H3 y H4 son
  mejoras de proceso y no bloquean.
- Pendiente del dueño: correr `python3 -m proceso.verificar_sesion` en local
  con `NORMAS_DIR` después de las correcciones (prompt en la conversación de
  esta auditoría) y contrastar su par con el sello.
