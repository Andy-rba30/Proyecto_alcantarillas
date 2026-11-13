# `proceso/` — el material del proceso de desarrollo (no es parte del entregable)

El programa de esta tesis se desarrolló con asistencia de IA (Claude Code), en sesiones
gobernadas por reglas escritas, auditorías externas y cadenas de prompts. Ese material
documenta **cómo se hizo** y permite auditarlo, pero **no es el software ni su
documentación de uso**: por eso vive aquí, separado del entregable. T-12, el último prompt
de la cadena T (2026-11-13, INF-5.2.2), lo **movió** aquí con `git mv` —nada se borró del
historial—.

**Qué lo separa del entregable, en la práctica:**

- `git archive` lo excluye (`.gitattributes`: `proceso export-ignore`): una exportación
  del entregable no lo lleva.
- `python -m pytest` desde la raíz no lo recoge (`testpaths = ["tests"]` en
  `pyproject.toml`): el par de la suite del entregable no cuenta estos tests.
- El README de usuario es el de la raíz; éste es el README de proceso.

## Qué hay aquí

| Ruta | Qué es | Antes de T-12 |
|---|---|---|
| `bitacora_conteos_y_entorno.md` | El ritual de cierre de cada sesión, el par de la suite medido sesión a sesión, la tabla de las cuatro configuraciones de entorno (PyMuPDF × Tk, con el eje `NORMAS_DIR`) y los incidentes de entorno. **La tabla de conteos se actualiza aquí.** | sección «Cierre de tarea» de `CLAUDE.md` |
| `reglas_de_correccion_de_auditorias.md` | Cómo se corrigen los hallazgos de las auditorías y del INFORME: clusters, conflictos vinculantes, el tracker, las decisiones diferidas, git. | secciones «Reglas de corrección…» y «Git (fase de corrección)» de `CLAUDE.md` |
| `auditorias/` | Los tres informes de auditoría externa (matemática, sistema, normativa), los temarios de refutación y el **tracker** `matriz_cruzada_auditorias.xlsx` (hoja `Hallazgos`: estado, responsable y commit de cada hallazgo). | `docs/auditorias/` |
| `planes_mejora/` | Los planes y las cadenas de prompts: la de la auditoría externa (EXT), la de perfil (PF) y la **cadena T** (`09_CADENA_PROMPTS_TESIS.md`, copia fiel del original con la nota del orquestador), más los prompts sueltos. | `docs/planes_mejora/` |
| `.claude/agents/` | Los subagentes de las sesiones (explorador, verificador normativo, auditor adversarial). Aquí Claude Code ya no los registra: una sesión que los necesite (el lote posterior a la cadena, por ejemplo) los copia a `.claude/agents/` de su propio árbol de trabajo. | `.claude/agents/` |
| `hoja_de_ruta_correcciones_v12.md` | El plan de las sesiones S1 a S24 de corrección de las auditorías, con sus prompts literales y la asignación de modelos de IA. | `docs/` (hasta el cierre de T-12) |
| `auditoria_y_ruta_despliegue_v9.md` | Documento de trabajo: auditoría del estado y ruta de cierre para el despliegue, con prompts. | `docs/` (hasta el cierre de T-12) |
| `verificar_sesion.py` | La verificación independiente de cierre de sesión: suite, conteos citados en los documentos, ramas, tracker y PDF de normas. `python3 -m proceso.verificar_sesion` desde la raíz. | raíz |
| `apoyo/tracker.py` | Lector del tracker con la biblioteca estándar (sin `openpyxl`). | `tests/apoyo/tracker.py` |
| `tests/` | Los tests de PROCESO, con su propio `conftest.py`: la gobernanza de la cadena T sobre el tracker y la copia de la cadena (`test_t0_gobernanza_proceso.py`), el cruce de los temarios con el tracker (`test_ext11_cruce_temarios.py`) y la cobertura de la auditoría de sistema por `docs/decisiones_diferidas.md` (`test_decisiones_diferidas_auditoria.py`). `python -m pytest proceso/tests` desde la raíz. | `tests/` |

La carpeta de orquestación de la cadena T (encargos, precisiones, informes y auditorías de
cada prompt) no está en `main`: vive en la rama `tesis/orquestacion-estado`, en
`docs/planes_mejora/orquestacion_T/`.

## Lo que se quedó en el entregable a propósito

`CLAUDE.md` (las reglas técnicas del código: etiquetas, archivos de valores, arquitectura,
excepciones, unidades, GUI, tests, PDF de normas), `docs/decisiones_diferidas.md` (cada
decisión diferida con su símbolo), `docs/contrato_entradas.md`, la hoja de ruta v8, los
manifiestos y el índice generados, `docs/trazabilidad.csv`, la guía de perfil y los cuatro
documentos de validación de T-11 son documentación del programa y siguen en `docs/`.
También siguen allí cinco documentos técnicos que nacieron del proceso:
`docs/ruta_familia_c.md` —que el código EXIGE al importar: sus secciones validan los
criterios `vacio_verificado`—, `docs/diseno_registro_normativo.md`,
`docs/resolucion_clase_sitio.md`, `docs/manifiesto_datos_proyecto_vs_constantes.md` y
`docs/linea_base.md`. Conservan menciones al proceso (sesiones, y en `ruta_familia_c.md`
los modelos de IA que hicieron cada paso): es la salvedad con que se cierra `INF-5.2.2`.
`hoja_de_ruta_correcciones_v12.md` y `auditoria_y_ruta_despliegue_v9.md` se movieron aquí
en el cierre de T-12: llevan prompts literales y asignación de modelos, y ni el código ni
los tests los leen.

**Las rutas que los documentos y los comentarios escritos antes de T-12 citan**
(`docs/auditorias/…`, `docs/planes_mejora/…`, `docs/hoja_de_ruta_correcciones_v12.md`,
`docs/auditoria_y_ruta_despliegue_v9.md`, `verificar_sesion.py`) se leen con las de la
tabla de arriba; no se reescribieron para no tocar texto histórico (ni la hoja de ruta v8,
cuya huella imprime cada memoria).

## Cómo correr lo de aquí

```
python -m pytest proceso/tests                 # los tests de proceso
python3 -m proceso.verificar_sesion             # el cierre de una sesión (corre las dos suites)
```

`verificar_sesion` necesita `openpyxl` (`requirements-dev.txt`) para el paso del tracker.

## El README anterior

Hasta T-12 la raíz tenía un único README que mezclaba la instalación con notas de
desarrollo (por qué no se cambió de motor de PDF, la medición de EXT-8). Está en el
historial: `git show f77c5d4:README.md`.
