# Bitácora Auditable de Cierre (`Proyecto_alcantarillas` + `Normas`, 2026-11-24)

Bitácora operativa de cierre para auditoría posterior. Registra cronológicamente qué se ejecuta, por qué se ejecuta y cómo queda el estado verificado en cada paso.

## Entorno de ejecución (Windows)

- **Fecha de inicio:** `2026-11-24T10:03:47-05:00`
- **Sistema operativo:** `Microsoft Windows 11 Home Single Language` (`Version: 10.0.26300`, `BuildNumber: 26300`)
- **CPU:** `16` núcleos lógicos (`NUMBER_OF_PROCESSORS = 16`)
- **Pantalla / DPI:** `AppliedDPI = 120` (escala 125 %, `1920x1080`)
- **Intérprete fijo (`$PY`):** `C:\Users\Andy Bayona Antón\AppData\Local\Programs\Python\Python313\python.exe` (`Python 3.13.2`)
- **Librerías clave:** `Tk 8.6`, `PyMuPDF 1.28.2`, `WeasyPrint 69.0`, `pytest 9.1.1`, `pytest-xdist 3.8.0`, `PyInstaller 6.19.0`
- **Variables de entorno:** `NORMAS_DIR = D:\Normas_repo`, `PYTHONIOENCODING = utf-8`
- **Rutas de repositorios:**
  - Repo principal: `D:\Proyecto_alcantarillas` (se preservan los 5 archivos locales no rastreados del usuario sin ejecutar `git clean`)
  - Worktree limpio de medición y sellado: `D:\alc_limpio`
  - Repo de normas: `D:\Normas_repo`

---

## Paso 1. Inicializar la bitácora auditable externa (`D:\bitacora_cierre_2026-11-24.md`)

- **Hora ISO:** `2026-11-24T10:03:47-05:00`
- **Qué se hace:** Se crea el archivo vivo `D:\bitacora_cierre_2026-11-24.md` fuera del árbol de trabajo `D:\alc_limpio`.
- **Por qué se hace:** Mantener `D:\alc_limpio` con `git status --short` completamente limpio durante la ejecución de `pytest` y durante el sellado (`_commit_de_origen()` añadiría `+cambios-sin-commit` si existieran archivos modificados o sin seguimiento en el worktree), garantizando trazabilidad completa para auditoría posterior.
- **Cómo queda:** Archivo creado en `D:\bitacora_cierre_2026-11-24.md` con la ficha de entorno verificada.

---

## Paso 2. Actualizar `D:\Normas_repo` a `claude/normas2-integracion` (`1991bef`)

- **Hora ISO:** `2026-11-24T10:04:35-05:00`
- **Qué se hace:**
  ```powershell
  git -C D:\Normas_repo fetch origin --prune
  git -C D:\Normas_repo checkout -B claude/normas2-integracion origin/claude/normas2-integracion
  ```
- **Por qué se hace:** Los cambios de N1 (`MP2018`), N2 (`LEY_29338`, `REGLAMENTO_LEY_29338`, `RNGIV`) y N3 (`HEC11`) en `07a784e` requieren que los 5 PDFs movidos desde `normas_2/` a `normas/` estén presentes en `NORMAS_DIR` para `pytest -m pdf` y `test_ext6_registro_normativo.py`.
- **Cómo queda:**
  - Rama: `claude/normas2-integracion` (tracking `origin/claude/normas2-integracion`), `HEAD = 1991bef`, `git status --short` vacío.
  - Conteo en `D:\Normas_repo\normas\`: **27 PDFs reales** (tamaño mínimo verificado `238,233` bytes; cero punteros Git LFS en `normas/`).

---

## Paso 3. Preparar el worktree limpio `D:\alc_limpio` en `claude/confident-cannon-0vgath` (`07a784e`)

- **Hora ISO:** `2026-11-24T10:04:53-05:00`
- **Qué se hace:**
  ```powershell
  git -C D:\Proyecto_alcantarillas fetch origin --prune --tags
  git -C D:\Proyecto_alcantarillas worktree remove --force D:\alc_limpio
  git -C D:\Proyecto_alcantarillas worktree prune
  git -C D:\Proyecto_alcantarillas worktree add -B claude/confident-cannon-0vgath D:\alc_limpio origin/claude/confident-cannon-0vgath
  ```
- **Por qué se hace:** Sustituir el worktree previo (que había quedado en `wip/windows-parches-ronda1` `404d06c`) por una copia completamente limpia de la rama activa más avanzada (`origin/claude/confident-cannon-0vgath`), sin afectar el checkout `D:\Proyecto_alcantarillas` ni sus 5 archivos locales no rastreados.
- **Cómo queda:**
  - `D:\alc_limpio`: rama `claude/confident-cannon-0vgath`, `HEAD = 07a784e`, `git status --short` vacío.
  - `D:\Proyecto_alcantarillas`: conserva intactos los 5 archivos locales no rastreados (`abrir_app.vbs`, `abrir_app_debug.bat`, `docs/CADENA_PROMPTS_tesis_app_alcantarillas.md`, `docs/INFORME_evaluacion_app_alcantarillas_vs_PDF.md`, `prueba.html`).

---

## Paso 4. Pre-verificación rápida en Windows sobre `07a784e`

- **Hora ISO:** `2026-11-24T10:05:07-05:00` → `2026-11-24T10:09:35-05:00`
- **Qué se hace:** Se ejecutan en Windows sobre `D:\alc_limpio` (`07a784e`, `NORMAS_DIR=D:\Normas_repo` en `1991bef`) los módulos que habían presentado fallos previos de Windows, las pruebas reales de ventana Tk, los tests del registro normativo y la suite de `proceso/tests` (registro completo en `D:\preverif_07a784e.txt`).
- **Por qué se hace:** Confirmar antes de invertir ~2 horas en la corrida completa que las rondas 1–3 de compatibilidad Windows, los cambios N1–N3 con el clon actualizado de normas y las guardias de `proceso/` pasan en esta máquina Windows.
- **Cómo queda:**
  - **4A** (`test_ve5_gui.py`, `test_ui5_decisiones.py`, `test_ui1_hidrologia_ventana.py`, `test_cierre_varios.py`, `test_ext6_registro_normativo.py`, `test_manifiesto_citas.py`, `test_gui_contrato.py`): **`327 passed, 9 skipped in 237.82s (0:03:57)`** (`rc = 0`).
  - **4B** (`test_ui3_barrido_ventana.py -k "test_e_la_ventana_real"`): **`1 passed, 46 deselected in 21.88s`** (`rc = 0`).
  - **4C** (`proceso/tests`): **`145 passed in 0.80s`** (`rc = 0`).
  - `git -C D:\alc_limpio status --short`: vacío.

---

## Paso 5. Corrida completa definitiva sobre `07a784e` en Windows (`NORMAS_DIR` = `1991bef`)

- **Hora ISO:** `2026-11-24T10:09:56-05:00` → `2026-11-24T12:22:37-05:00`
- **Qué se hace:**
  - **5a:** `pytest -n auto --dist loadfile -q -p no:cacheprovider --no-header -rfE` → `D:\suite_completa_07a784e.txt`
  - **5b:** `pytest -m aislado -q -p no:cacheprovider --no-header -rfE` → `D:\suite_aislado_07a784e.txt`
- **Por qué se hace:** Medir el par completo oficial (`passed`, `skipped`) sobre `07a784e` con `NORMAS_DIR`, PyMuPDF y Tk activos antes del sellado y del fast-forward a `main`.
- **Cómo queda (hallazgos detectados — se detiene el sellado y se replanifica):**
  - **5a (`D:\suite_completa_07a784e.txt`):** **`7 failed, 9266 passed, 29 skipped, 3 errors in 7918.44s (2:11:58)`**
    - 2 fallos esperados por sello provisional (`PROVISIONAL: suite por medir`):
      - `tests/test_trazabilidad_csv.py::test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes`
      - `tests/test_indice_formulas.py::test_el_sello_lleva_fecha_commit_y_par_de_la_suite`
    - 5 fallos no esperados:
      1. `tests/test_normativa_pdf.py::test_T0_el_sha1_de_cada_fuente_coincide_con_el_PDF` — `LEY_29338`: declarado `ac47b59be519288b6aaa3d0eb32bc2b96dd80416`, real `38d7a8ff88332cc682e676215a49425d213d86ae` («caducan 4 citas»).
      2. `tests/test_ui4_recorrido_ventana.py::test_c0_las_filas_de_exportacion_caben_en_la_geometria_por_defecto` — `assert '1376x973' == '1100x800'` (escalado DPI 125 % en Windows).
      3. `tests/test_ve5_gui_ventana.py::test_38_la_ventana_se_mide_en_su_geometria_minima` — `assert [1126, 776] == [900, 620]` (escalado DPI 125 % en Windows).
      4. `tests/test_ui4_recorrido_ventana.py::test_c5_los_dos_pdf_salen_por_el_hijo_con_la_hidrologia[pdf---pdf]` — `sesion["cuencas"]` salió con `\` (`tests\fixtures\...`) frente a `/` (`recorrido.relativa`).
      5. `tests/test_ui4_recorrido_ventana.py::test_c5_los_dos_pdf_salen_por_el_hijo_con_la_hidrologia[pdf_resumida---pdf-resumida]` — misma diferencia `\` vs `/`.
    - 3 errores (timeout de fixture):
      - `tests/test_ext5_forma_gui.py::test_b_c01_no_se_bloquea_en_n_celdas_y_su_bloqueo_real_es_S_cauce`
      - `tests/test_ext5_forma_gui.py::test_la_pestana_2_pone_cara_de_solo_lectura_a_un_derivado`
      - `tests/test_ext5_forma_gui.py::test_d_nan_recibe_el_mismo_veredicto_en_la_ventana_real`
      - Causa: `subprocess.TimeoutExpired` en `tests/test_ext5_forma_gui.py:550` (`gui_ext5_real`, `timeout=600`).
  - **5b (`D:\suite_aislado_07a784e.txt`):** **`1 failed, 9305 deselected in 13.61s`**
    - `tests/test_ext8_rendimiento_gui.py::test_pc10_import_cli_cabe_en_el_presupuesto_sin_weasyprint` — `import cli cuesta 0.328 s de CPU (minimo de 7); el presupuesto es 0.3 s` (`0.328125 < 0.3`).

---

## Paso 5c. Aislamiento de `tests/test_ext5_forma_gui.py` (verificación de los 3 timeouts)

- **Hora ISO:** `2026-11-24T12:25:50-05:00`
- **Qué se hace:** Se ejecuta `tests/test_ext5_forma_gui.py` en solitario sin `-n auto` (`& $PY -m pytest -q -p no:cacheprovider --no-header -rfE tests/test_ext5_forma_gui.py`).
- **Por qué se hace:** Determinar si los 3 errores (`subprocess.TimeoutExpired`, `timeout=600` sobre `gui_ext5_real`) observados en la corrida paralela (`-n 16`) correspondían a un bug real de la aplicación o únicamente a contención de CPU/Tk al correr 16 workers simultáneos.
- **Cómo queda:** **`303 passed in 13.63s`** (`rc = 0`, 0 fallos, 0 errores). Se confirma que los 3 errores de la corrida paralela fueron exclusivamente contención bajo `-n 16`.

---

## Paso 6 (Revisión A). Restaurar binario `LEY_29338` en `D:\Normas_repo` y verificar `tests/test_normativa_pdf.py`

- **Hora ISO:** `2026-11-24T12:28:29-05:00`
- **Qué se hace:**
  ```powershell
  git -C D:\Normas_repo config core.autocrlf false
  git -C D:\Normas_repo rm --cached -r .
  git -C D:\Normas_repo reset --hard 1991bef
  & $PY -m pytest -q -p no:cacheprovider --no-header -rfE tests/test_normativa_pdf.py
  ```
- **Por qué se hace:** En Windows, `D:\Normas_repo` tenía `core.autocrlf = true` y el repositorio de normas carece de `.gitattributes` con `*.pdf binary`. Al hacer checkout de `1991bef`, Git alteró bytes `\n` → `\r\n` en `normas/Ley 29338 Ley de Recursos Hidricos (SPIJ).pdf` (`11,007,041` bytes / SHA-1 `ac47b59be519288b6aaa3d0eb32bc2b96dd80416` → `11,733,086` bytes / SHA-1 `38d7a8ff88332cc682e676215a49425d213d86ae`), haciendo fallar `test_T0_el_sha1_de_cada_fuente_coincide_con_el_PDF`.
- **Cómo queda:**
  - `Ley 29338 Ley de Recursos Hidricos (SPIJ).pdf` restaurado al blob exacto (`11,007,041` bytes, SHA-1 `ac47b59be519288b6aaa3d0eb32bc2b96dd80416`).
  - `tests/test_normativa_pdf.py`: **`35 passed in 88.47s (0:01:28)`** (`rc = 0`).

---

## Paso 7 (Revisión B). Compilación y prueba del empaquetado PyInstaller C3 en Windows

- **Hora ISO:** `2026-11-24T12:30:43-05:00`
- **Qué se hace:** Se compila `empaquetado/proyecto_alcantarillas.spec` en directorio temporal (`$env:TEMP\pyi_build` y `$env:TEMP\pyi_dist`) y se prueba `alcantarillas_cli.exe --help` y `alcantarillas_cli.exe --prevuelo tests/fixtures/corridas_de_referencia/perfil_guia/puntos.csv`; luego se eliminan las carpetas temporales.
- **Por qué se hace:** Verificar en Windows la receta C3 de `11_PLAN_MANTENIBILIDAD_Y_USO.md` y hallazgo N2 de `AUDITORIA_MAIN_2026-11-24.md` (que nunca habían sido compilados ni ejecutados) sin dejar residuos dentro de `D:\alc_limpio`.
- **Cómo queda:**
  - Compilación PyInstaller (`6.19.0`, Python `3.13.2`, Windows 11 Build `26300`): **`BUILD_RC = 0`**.
  - Ejecutables generados: `alcantarillas_cli.exe` (`17,473,499` bytes) y `alcantarillas_gui.exe` (`17,476,667` bytes).
  - `alcantarillas_cli.exe --help`: **`HELP_RC = 0`** (muestra ayuda completa).
  - `alcantarillas_cli.exe --prevuelo tests/fixtures/corridas_de_referencia/perfil_guia/puntos.csv`: ejecutó el análisis completo de pre-vuelo con `src/` empaquetado (AST y docs sin errores de rutas congeladas) y devolvió **`PREVUELO_RC = 1`** al reportar entradas `DETIENE` faltantes en ese CSV sin `--datos-externos`. *(Nota: queda por probar interactivamente `alcantarillas_gui.exe` con exportación PDF real congelada en pantalla.)*
  - Directorios temporales eliminados y `git -C D:\alc_limpio status --short` vacío.

---

## Paso 8 (Revisión C). Sincronización con remoto (`7252e82`) y motivo de detención antes del sellado / fast-forward

- **Hora ISO:** `2026-11-24T12:31:00-05:00`
- **Qué se hace:**
  ```powershell
  git -C D:\alc_limpio merge --ff-only origin/claude/confident-cannon-0vgath
  ```
- **Por qué se hace y por qué NO se selló ni se hizo fast-forward a `main`:**
  1. Mientras se ejecutaba la corrida en Windows, la sesión remota de Claude subió el commit **`7252e82`** a `origin/claude/confident-cannon-0vgath` (`proceso: bitacora de la suite medida de N1-N3 (07a784e), cierre sin sellar`). En él queda registrado que incluso en Linux en reposo el paso `-m aislado` (`test_pc10_import_cli_cabe_en_el_presupuesto_sin_weasyprint`) falló dos veces (`0.313 s` vs `0.30 s`) y que el dictamen de Fable impide sellar o fusionar a `main` hasta que se decida cómo tratar el presupuesto/coste de `import cli`.
  2. En Windows también fallaron:
     - `test_pc10_import_cli_cabe_en_el_presupuesto_sin_weasyprint` (`0.328125 s` vs `0.3 s`).
     - `test_ui4_recorrido_ventana.py::test_c0` (`'1376x973' == '1100x800'`) y `test_ve5_gui_ventana.py::test_38` (`[1126, 776] == [900, 620]`) debido al escalado DPI 125 % en Windows (`3d8a8ea`/`5248a36` escalan la ventana por DPI pero esos dos tests comparan dimensiones literales sin escalar).
     - `test_ui4_recorrido_ventana.py::test_c5` (`pdf` y `pdf_resumida`: `sesion["cuencas"]` lleva `\` de Windows frente a `recorrido.relativa` con `/`, consecuencia del rollback parcial `cd45995`).
  3. Respetando la regla operativa de no modificar código ni tomar decisiones técnicas/Git por cuenta propia, se detiene aquí el sellado y el fast-forward, dejando ambos repositorios listos y documentados para que Claude/Fable y el dueño decidan:
     - `D:\Proyecto_alcantarillas`: intacto con sus 5 archivos locales no rastreados.
     - `D:\alc_limpio`: limpio en `claude/confident-cannon-0vgath` (`7252e82`), `git status --short` vacío.
     - `D:\Normas_repo`: limpio en `claude/normas2-integracion` (`1991bef`, `core.autocrlf = false`), `git status --short` vacío.
     - `origin/main` de `Proyecto_alcantarillas`: sin cambios en `1f56d99`.
     - `origin/main` de `Normas`: sin cambios en `ce4c90e`.

---

## Paso 9 (Cierre — Paso 1). Fijar `*.pdf binary` en `D:\Normas_repo\.gitattributes` (`4dea7ed`)

- **Hora ISO:** `2026-11-24T15:13:47-05:00`
- **Qué se hace:** Se añaden las reglas `*.pdf binary` y `*.PDF binary` al inicio de `D:\Normas_repo\.gitattributes` (saltos LF), preservando al final la regla específica de Git LFS para `normas_2/HDMcombined 882025.pdf`.
- **Por qué se hace:** Evitar que futuros clones o checkouts en Windows con `core.autocrlf = true` alteren bytes `\n` → `\r\n` dentro de PDFs como ocurrió con `Ley 29338 Ley de Recursos Hidricos (SPIJ).pdf`. Colocar las reglas genéricas antes que la regla LFS garantiza que la regla LFS siga teniendo precedencia sobre `HDMcombined 882025.pdf`.
- **Cómo queda:** Commit **`4dea7ed`** en `claude/normas2-integracion` (`1 file changed, 2 insertions(+)`), `git -C D:\Normas_repo status --short` vacío.

---

## Paso 10 (Cierre — Paso 2 / Commit A). Carga diferida de `M11_reporte`, `M12_metrados` y `MH_hidrologia` en `import cli` (`7707bed`)

- **Hora ISO:** `2026-11-24T15:21:15-05:00`
- **Qué se hace:**
  - En `cli.py`: se sustituye la importación ansiosa de 16 símbolos de `src.modulos.M11_reporte` por `__getattr__(nombre)` bajo demanda y accesos vía `sys.modules[__name__].<nombre>` dentro de las funciones de salida/plantilla (preservando `monkeypatch.setattr(cli, ...)` y reexportación idéntica).
  - En `src/servicio.py`: se sustituyen las importaciones ansiosas de `MH_hidrologia` y `M12_metrados` por `_ModuloPerezoso` (conservando `from src.modulos import MH_hidrologia` dentro de `_cargar_mh` para la guardia AST de `test_t1_hidrologia.py`) y se mueve `from src.modulos.M11_reporte import sha1_de_bytes` dentro de `cargar_hidrologia` y `correr`.
  - En `tests/test_ext8_rendimiento_gui.py`: se añade `test_pc10_import_cli_difiere_reporte_metrados_e_hidrologia` para vigilar que ninguno de los 3 módulos cargue en `import cli` y que la identidad de objeto se conserve.
- **Por qué se hace:** El presupuesto `PRESUPUESTO_IMPORT_CLI_S = 0.3` fallaba tanto en Linux en reposo (`0.313 s` en `7252e82`) como en Windows (`0.328 s` en `07a784e`) porque `import cli` arrastraba ansiosamente los 19 submódulos de `M11_reporte`, `M12_metrados` y `MH_hidrologia` (~100 ms entre los tres) sin usarlos al arrancar. Diferirlos resuelve la causa raíz sin relajar el presupuesto de `0.30 s` ni tocar el cálculo.
- **Cómo queda:**
  - `_cpu_de_import_cli()` medido en Windows: **`0.2656 s`** (bajo el límite de `0.30 s`, desde `0.3281 s`).
  - `pytest -m aislado tests/test_ext8_rendimiento_gui.py`: **`1 passed, 35 deselected in 2.87s`**.
  - Guardias (`test_ext8_rendimiento_gui.py`, `test_ext9_paquete_servicio.py`, `test_guardias_de_la_suite.py`, `test_sin_literales.py`, `test_t1_hidrologia.py`, `test_cli.py`, `test_ve5_gui.py`): **`469 passed, 4 skipped in 340.08s (0:05:40)`** (`0 failed`).
  - Commit en `claude/confident-cannon-0vgath`: **`7707bed`** (`3 files changed, 129 insertions(+), 49 deletions(-)`).

---

## Paso 11 (Cierre — Paso 3 / Commit B). Ajustes de compatibilidad Windows en UI-4, VE-5 y tope paralelo de `ext5` (`940333a`)

- **Hora ISO:** `2026-11-24T15:30:19-05:00`
- **Qué se hace:**
  - `tests/apoyo/gui_ui4_recorrido_real.py` + `tests/test_ui4_recorrido_ventana.py`: `test_c0` calcula y compara en `win32` la geometría escalada por `comp.factor_de_escala` y recortada al área de trabajo (`±2` px de redondeo DWM; en Linux conserva exactamente `"1100x800"`); `test_c5` compara `sesion["cuencas"]` y `sesion["estacion"]` contra `str(Path(recorrido.relativa(...)))` respetando el separador nativo de la ronda 2 (`cd45995`).
  - `tests/apoyo/gui_ve5_real.py` + `tests/test_ve5_gui_ventana.py`: `test_38_la_ventana_se_mide_en_su_geometria_minima` valida en `win32` contra `r["minsize"]` escalado (`≥ 900×620`, `±2` px); en Linux conserva exactamente `[900, 620]`.
  - `tests/test_ext5_forma_gui.py`: se aumenta `timeout` del fixture `resumen_real` de `600` a `1500` s (igual que `test_ui1` y `test_ui3`) para evitar cortes bajo carga paralela (`-n 16`).
- **Por qué se hace:** Cerrar los 4 fallos reales de Windows (`c0`, `test_38`, `c5` ×2) y los 3 errores por timeout paralelo de `test_ext5_forma_gui.py` medidos sobre `07a784e`, manteniendo intacto el comportamiento en Linux/CI y la regla de rutas nativas de `WIN-01`.
- **Cómo queda:**
  - `pytest tests/test_ve5_gui_ventana.py tests/test_ui4_recorrido_ventana.py tests/test_ext5_forma_gui.py`: **`363 passed, 1 skipped in 463.63s (0:07:43)`** (`rc = 0`).
  - Commit en `claude/confident-cannon-0vgath`: **`940333a`** (`5 files changed, 29 insertions(+), 5 deletions(-)`).

---

## Paso 12 (Cierre — Paso 4 / Commit C). Fichas `EXT-8-07` y `WIN-04` en `docs/decisiones_diferidas.md` (`4bf340f`)

- **Hora ISO:** `2026-11-24T15:33:15-05:00`
- **Qué se hace:** Se añaden las fichas `EXT-8-07` (anclada en `cli.py::__getattr__`) y `WIN-04` (anclada en `tests/test_ui4_recorrido_ventana.py::test_c0_las_filas_de_exportacion_caben_en_la_geometria_por_defecto`) a `docs/decisiones_diferidas.md`, se regenera su `# Índice de fichas` con `tests.test_decisiones_diferidas --escribir` (saltos LF) y se comprueba sincronía con `src.normativa.manifiesto` y `src.indice_formulas`.
- **Por qué se hace:** Mantener trazabilidad auditable y anclada por símbolo de las decisiones técnicas cerradas en los Commits A y B y en `D:\Normas_repo`.
- **Cómo queda:**
  - `src.normativa.manifiesto` (`rc=0`) y `src.indice_formulas` (`rc=0`): ambos **sincronizados** (cuerpo idéntico, 0 referencias resincronizadas).
  - `pytest tests/test_decisiones_diferidas.py proceso/tests`: **`566 passed in 16.49s`** (`0 failed`).
  - Commit en `claude/confident-cannon-0vgath`: **`4bf340f`** (`1 file changed, 45 insertions(+), 1 deletion(-)`).
  - `git -C D:\alc_limpio status --short`: vacío.


---

## Paso 13. Programación de hibernación automática a las 17:30:00

- **Hora ISO:** `2026-11-24T16:58:33-05:00`
- **Qué se hace:** Se registra en el Programador de Tareas de Windows la tarea única `Hibernar_1730_20261124` (`Register-ScheduledTask`) ejecutando `shutdown.exe /h` para `2026-11-24T17:30:00-05:00`, con `DisallowStartIfOnBatteries = False`, `StopIfGoingOnBatteries = False`, `StartWhenAvailable = False`, `EndBoundary = 2026-11-24T17:32:00-05:00` y `DeleteExpiredTaskAfter = PT5M`.
- **Por qué se hace:** Solicitud expresa del usuario al salir a las `17:30` para hibernar el equipo preservando en memoria la corrida paralela `task-484` sobre `4bf340f` sin abortarla ni volver a disparar la hibernación al encender el equipo después.
- **Cómo queda:**
  - Tarea `Hibernar_1730_20261124`: `State = Ready`, `NextRunTime = 24/11/2026 17:30:00`, `StartBoundary = 2026-11-24T17:30:00-05:00`, `EndBoundary = 2026-11-24T17:32:00-05:00`, `Enabled = True`.
  - Trabajo en curso sin interrupción: `task-484` sigue corriendo hacia `D:\suite_definitiva_paralelo.txt` y `D:\alc_limpio` permanece limpio.


---

## Paso 14. Fin de la corrida paralela definitiva (`task-484`) y paso `-m aislado` sobre `4bf340f`

- **Hora ISO:** `2026-11-25T09:20:49-05:00`
- **Qué se hace:**
  - Concluye la corrida paralela `task-484` iniciada el `2026-11-24T15:33:25-05:00` (`pytest -n auto --dist loadfile -q -p no:cacheprovider --no-header -rfE` → `D:\suite_definitiva_paralelo.txt`), que incluyó el periodo de hibernación nocturna del equipo entre las `2026-11-24T17:30:00-05:00` y las `2026-11-25T09:10:30-05:00` (~15 h 40 min en hibernación; tiempo activo real aproximado de ~2 h 00 min).
  - Se verifica la recolección total en `D:\alc_limpio`: `9309` tests recolectados.
  - Se ejecuta el paso `-m aislado` sin `-n` (`D:\suite_definitiva_aislado.txt`) con `NORMAS_DIR = D:\Normas_repo` (`4dea7ed`).
- **Por qué se hace:** Medir el par definitivo completo (`passed`, `skipped`) sobre el árbol `4bf340f` tras integrar `7707bed` (`EXT-8-07`), `940333a` (`WIN-04`), `4bf340f` y `4dea7ed` antes de sellar los documentos generados.
- **Cómo queda:**
  - `D:\suite_definitiva_paralelo.txt`: **`2 failed, 9277 passed, 29 skipped in 63617.67s (17:40:17)`** (`0 errors`, `1` test `aislado` deseleccionado).
    - Los 2 únicos fallos son exactamente los esperados por el sello `PROVISIONAL` anterior:
      - `tests/test_trazabilidad_csv.py::test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes`
      - `tests/test_indice_formulas.py::test_el_sello_lleva_fecha_commit_y_par_de_la_suite`
  - `D:\suite_definitiva_aislado.txt`: **`1 passed, 9308 deselected in 19.31s`** (`exit code = 0`).
  - **Par definitivo MEDIDO sobre `4bf340f`:** **`9280 passed, 29 skipped`** (`9277 + 2 de sello + 1 aislado = 9280`; `9280 + 29 = 9309` recolectados).
  - La tarea `Hibernar_1730_20261124` se ejecutó según lo previsto a las `17:30` y se autoeliminó al expirar (`Get-ScheduledTask` vacío).


---

## Paso 15. Sellado de documentos generados y verificación de sincronía (`e2b5d07`)

- **Hora ISO:** `2026-11-25T09:28:09-05:00`
- **Qué se hace:**
  - Con `D:\alc_limpio` limpio en `4bf340f` (`git status --short` vacío), se ejecutan:
    - `$PY -m src.normativa.manifiesto --escribir --suite "9280 passed, 29 skipped (Windows 11 · Python 3.13.2 · PyMuPDF sí · ventana Tk sí · repositorio de normas enlazado · paralelo -n 16 más el paso aislado)"`
    - `$PY -m src.indice_formulas --escribir --suite "9280 passed, 29 skipped (Windows 11 · Python 3.13.2 · PyMuPDF sí · ventana Tk sí · repositorio de normas enlazado · paralelo -n 16 más el paso aislado)"`
  - Se comprueban finales de línea LF (`crlf=0` en los cuatro archivos) y `git diff` mostrando únicamente las dos líneas de sello (`2026-11-25 · 4bf340f`, sin `+cambios-sin-commit`).
  - Se ejecutan los tests de sello y sincronía (`tests/test_trazabilidad_csv.py`, `tests/test_indice_formulas.py`, `tests/test_ext9_paquete_servicio.py`, `tests/test_manifiesto_citas.py`).
  - Se crea el commit atómico de sellado (`docs: sella indice_formulas.md y trazabilidad.csv con el par MEDIDO (4bf340f; 9280 passed, 29 skipped)`).
- **Por qué se hace:** Fijar en `docs/indice_formulas.md` y `docs/trazabilidad.csv` el sello definitivo del par medido sobre el árbol limpio `4bf340f` y validar que todos los tests de sello y sincronía pasen antes del commit de proceso.
- **Cómo queda:**
  - `docs/manifiesto_citas.md`: `0` referencias resincronizadas (`crlf = 0`, `906` líneas).
  - `docs/manifiesto_registro_normativo.md`: `3977` líneas (`crlf = 0`, sin cambios).
  - `docs/trazabilidad.csv`: `690` líneas (`crlf = 0`), sello `2026-11-25 · 4bf340f · ... 9280 passed, 29 skipped ...`.
  - `docs/indice_formulas.md`: `1775` líneas (`crlf = 0`), sello `2026-11-25 · 4bf340f · 9280 passed, 29 skipped ...`.
  - Pruebas de sello y sincronía: **`73 passed in 298.78s (0:04:58)`** (`rc = 0`).
  - Commit en `claude/confident-cannon-0vgath`: **`e2b5d07`** (`e2b5d07374380a9c641d15f81d852e575977cd8a`, `2 files changed, 2 insertions(+), 2 deletions(-)`).

---

## Paso 16. Actualización de `proceso/`, copia de la bitácora auditable y guardias de proceso

- **Hora ISO:** `2026-11-25T09:30:00-05:00`
- **Qué se hace:**
  - Se añade al final de `proceso/bitacora_conteos_y_entorno.md` (sin alterar ninguna palabra histórica anterior) la sección del cierre en Windows sobre `4bf340f` / sello `e2b5d07` (`9280 passed, 29 skipped`, C3 PyInstaller y `4dea7ed`).
  - Se actualiza `proceso/planes_mejora/ve3_estado/LEEME.md` con el bloque de estado `2026-11-25` encima del bloque anterior.
  - Se actualiza la fila `C3 receta PyInstaller` en `proceso/planes_mejora/11_PLAN_MANTENIBILIDAD_Y_USO.md` (§8).
  - Se copia esta bitácora externa normalizada a LF en `proceso/planes_mejora/ve3_estado/BITACORA_CIERRE_N1_N3_WINDOWS_2026-11-24.md` (verificando cero CRLF y cero direcciones de correo electrónico en los archivos de `proceso/`).
  - Se ejecutan `proceso/tests` y las guardias de entregable (`tests/test_t12_entregable.py`, `tests/test_sin_literales.py`, `tests/test_decisiones_diferidas.py`) antes de registrar el commit de proceso y proceder al fast-forward de `main` (cuya verificación remota queda registrada externamente en el Paso 17 de `D:\bitacora_cierre_2026-11-24.md`).
- **Por qué se hace:** Dejar al día la bitácora oficial de proceso (`bitacora_conteos_y_entorno.md`), la guía de estado (`LEEME.md`), la tabla C3 (§8 de `11_PLAN_MANTENIBILIDAD_Y_USO.md`) y una bitácora cronológica completa auditable dentro del repositorio sin romper ninguna invariante histórica ni introducir CRLF.
- **Cómo queda:**
  - `proceso/tests` (guardias de gobernanza T-0/T-12, `test_la_bitacora_conserva_su_texto_historico_y_admite_actualizarse`, cruce de temarios y auditoría): **`145 passed in 0.91s`** (`0 failed`).
  - `proceso/tests` + `tests/test_t12_entregable.py` + `tests/test_sin_literales.py` + `tests/test_decisiones_diferidas.py`: **`742 passed in 315.35s (0:05:15)`** (`0 failed`).
  - Los cuatro archivos de `proceso/` quedan normalizados con finales LF (`crlf = 0`) y sin direcciones de correo electrónico (única coincidencia `@` histórica previa en `bitacora_conteos_y_entorno.md`: la etiqueta de sensibilidad `F4.PERFIL@4.3c`), verificados con `proceso/tests` antes de crear el commit de cierre en `claude/confident-cannon-0vgath` (`Commit E`, cuya integración a `main` y hashes remotos finales se anotan en el Paso 17 de `D:\bitacora_cierre_2026-11-24.md`).
