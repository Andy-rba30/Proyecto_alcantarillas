# Planes de mejora — versión revisada contra el repositorio real

**Reemplaza a:** `PLANES MEJORA/00..05` (la versión que subiste).
**Fecha de revisión:** 2026-09-12, contra el árbol de `main` en el commit `21f831d`
(post-S23). Todo lo cuantitativo de estos planes se **midió ejecutando el código**,
no se copió de documentos.

---

## 1. El dictamen en tres frases

1. Tus planes están bien pensados como *dirección* — la ficha estructurada, la
   separación «lo que dice la fuente / lo que lee el proyectista», el pre-vuelo,
   la traza de cada número — pero se escribieron **sin leer el código** (lo
   declaran ellos mismos en la Fase 0) y contra una foto de hace muchas sesiones.
2. **Aproximadamente el 60 % de lo que proponen construir ya existe**, construido
   entre las sesiones S11 y S23 con más rigor del que los planes piden: el
   registro normativo completo, la transcripción íntegra de tablas, la memoria
   estructurada, el campo `nivel`, los filtros derivados de la GUI y la ayuda
   derivada del censo.
3. De lo restante, una parte **contradice reglas duras del proyecto** (dos
   propuestas son exactamente la «corrección ingenua» que la matriz de
   conflictos prohíbe) y otra parte sigue siendo **trabajo real y valioso** —
   esa parte es la que estos planes reescriben como prompts ejecutables.

---

## 2. Lo que tus planes proponían construir y YA EXISTE

Verificado símbolo por símbolo. No lo vuelvas a pedir en un prompt: una sesión
que lo reconstruya crearía un duplicado que divergiría del original.

| Propuesta del plan original | Lo que ya existe en el repo |
|---|---|
| «Ficha por objeto declarable, legible por máquina» (Plan 00 §2) | `Criterio` (17 campos, `src/criterios_adoptados.py`), `VariableDeEntrada` (censo de 95 variables en `src/variables_entrada.py`), `Cita`/`TablaNormativa`/`Fuente` (`src/normativa/esquema.py`). Son dataclasses congelados con invariantes en `__post_init__` — más estricto que el YAML propuesto |
| Esquema `Fuente` con edición, página impresa/PDF, carácter (Plan 04 §2) | `normativa.esquema.Fuente` y `Cita`: 13 fuentes presentes con SHA-1 medido y desfase de paginación medido, 13 ausentes declaradas con `Ausencia`, `Caracter` con **cinco** valores (exigencia/recomendación/permiso/definición/aproximación — más fino que los tres del plan) |
| «Registro central de normas» `registro.yaml` (Plan 04 §3) | `src/normativa/fuentes.py` + `Registro` (`registro.py`). Es código con tests, no YAML. **116 citas, 0 sin verificar, 0 por transcribir** |
| Separar «lo que dice la fuente» de «lo que interpreta el proyectista» (Plan 04 §1) | `Verbatim` vs `Interpretacion` (que exige ≥1 hecho `en_contra`), y la regla NOR-HID-04: tres clases CSS separadas en la memoria (`fuente` / `interpretacion` / lo que el proyecto hace) |
| Transcripción de tablas con celdas usadas / no resueltas / regla de lectura (Plan 04 §4) | `TablaNormativa`: 18 tablas transcritas **completas** con notas al pie, modificadores, `uso` por fila y columna, `CeldaSinValor`, lagunas, y `CorrespondenciaDeTablas.regla_al_cruzar`. `Registro.elecciones_pendientes()` devuelve hoy 37 celdas/filas bloqueadas por condición |
| Verificación de citas contra el PDF (Plan 04 §7) | `src/normativa/extraccion/` + `tests/test_normativa_pdf.py` (14 tests: SHA-1, texto literal en su página, título del numeral, regla de paginación) + `tests/test_normativa.py` (49 tests estructurales) |
| Linter normativo N1–N11 (Plan 04 §7) | Cubierto casi entero por los invariantes T1–T22 del esquema y esos 63 tests. Lo poco que falta está en el plan T de esta serie |
| Matriz de trazabilidad legible por máquina (Plan 04 §5) | `docs/manifiesto_registro_normativo.md` (157 KB, **generado** por `normativa.manifiesto.indice_del_registro`, anclado por id de objeto, con test de sincronía) |
| Campo `familias` y aviso «no aplica a esta corrida» (Plan 01 §3–4) | `cli.FAMILIAS_QUE_USAN` + `cli.familias_del_csv()` + `_pintar_no_aplica()` en la GUI (S21), defendido **por medida** en `tests/test_familias_del_csv.py` |
| Filtros y contadores en la pestaña de criterios (Plan 01 §4) | Tres filtros (estado, ámbito derivado del alcance, búsqueda) + recuento honesto «33 de 69 pendientes \| el filtro muestra N y esconde M». Falta fase y familia — ver plan G |
| Pestaña de ayuda generada, no escrita a mano (Plan 01 §4) | `gui/ayuda_entrada.py`: ventana con dos pestañas **derivadas** del censo (19 columnas CSV + 8 claves JSON), con test que añade una columna y comprueba que la ayuda la recoge sola |
| «La memoria la emite el cálculo» / traza de procedencia (Plan 01 §4, Plan 03 §C.3) | `PasoDeMemoria` (`src/modelos.py`): qué, por qué (`Fundamento` con verbo sostenido por el carácter de la cita), fórmula con cita, sustitución con procedencia, umbral con carácter, veredicto. M11 solo formatea (un test barre su AST). **Lo que falta es mostrarlo en la GUI** — plan G4 |
| Historia de decisiones fuera del texto (Plan 02 §5) | `docs/decisiones_diferidas.md` (archivo único, fichas por símbolo, guardia en `tests/test_decisiones_diferidas.py`) + el historial de git |
| Casos patrón fuente + borde + imposible (Plan 03 §B.3) | `tests/fixtures/casos_patron.py`: 27 símbolos CP en 10 familias, 4 autoverificados por recómputo independiente, guardia por AST de que todo módulo consume el suyo. Exentos declarados: M2, M8, M10 (falta fuente externa — conflicto #7 prohíbe inventar dorados) |
| Clasificación de variables por naturaleza/modo/forma/ámbito/estado (Plan 03 §C.1) | `Poblacion`, `Resolucion` (familia cerrada de 6 modos), etiqueta, `nivel`, y la **familia cerrada de rangos donde la semántica ES el tipo** (`IntervaloAdmisible`, `TechoUnico`, `ConjuntoDeMaximos` sin atributo `minimo`, …) — resuelve el «eje 4» del plan mejor que el campo `forma_del_valor` propuesto |

---

## 3. Lo que tus planes proponían y HAY QUE DESCARTAR (con la razón)

| Propuesta | Por qué se descarta |
|---|---|
| «Implementar o retirar V4b» (Plan 03 §A.3, ticket F3-03) | **Ya se resolvió, y de la única forma que el Conflicto #1 de la matriz permitía.** V4b existe (`M5_verificaciones.v4b_relacion_hw_d`, cableada en S14), su umbral es el criterio `[A]` `HW_D_max`, y `NUMERAL_V4B` declara expresamente que NO tiene numeral normativo (el 1.0–1.5 del HDS-5 es encuesta de práctica, NOR-HDS-02). Un prompt que pida «implementarla o retirarla» invita a deshacer una resolución vinculante |
| Refactor de `v_max_rango` a `LimiteVelocidad` (Plan 03 §C.1, ticket F3-06) | `v_max_rango` **fue retirado** al cerrar SIS-A-06 y hay una guardia (`tests/test_guardias_de_la_suite.py`) que **falla si el símbolo vuelve**. El modelo vigente es mejor que el propuesto: `Material.v_max_tabla10` (la fila de la Tabla N° 10 tal cual) + `v_max_adoptado` (techo escalar `[C]`), y en el registro el tipo `ConjuntoDeMaximos` — que no tiene `minimo` a propósito, porque los dos valores del concreto **son ambos máximos** (NOR-HID-04). El `LimiteVelocidad` propuesto, con `minimo`/`maximo`, reintroduciría exactamente esa confusión |
| `registro.yaml` paralelo al código (Plan 04 §3) | Duplicaría `src/normativa/fuentes.py`. Dos registros divergen; el proyecto ya pagó ese precio dos veces con textos duplicados |
| `docs/AUDITORIA/` + `inventario.json` + script de inventario (Plan 00 §6) | El inventario **ya es ejecutable**: `reporte_variables()`, `reporte_criterios()`, el manifiesto generado, la ayuda derivada. Un JSON volcado aparte se desactualiza el mismo día — que es la razón que el propio plan daba para no hacerlo a mano |
| `pendientes_criterios.md` (Plan 00 §9, Plan 02 §5) | Regla escrita del proyecto: «Nunca se abre un tercer documento para registrar avance». Los pendientes viven en el código (`criterios_sin_valor()`, hoy 33) y el estado de hallazgos en el `.xlsx` |
| `docs/decisiones/ADR-NNN-*.md` (Plan 02 §5) | El proyecto ya eligió el archivo único `decisiones_diferidas.md` **con guardia de símbolo vivo**; los ADR sueltos no la tendrían |
| Campo `texto_original` congelado en cada criterio (Plan 02 §2) | Git ya conserva cada versión del texto. Congelarlo en el archivo duplica ~69 párrafos que nadie leería y engorda un archivo que ya ronda las 6 400 líneas |
| Migrar los criterios a una ficha de 8 campos nuevos (Plan 02 §2) | La mitad de esos campos ya existe con otro nombre (`que_dice_la_fuente` → `Cita.texto_literal`; `interpretacion` → `Interpretacion` del registro; `sensibilidad` → campo real; `alcance_de_aplicacion` → `consumido_por` derivado). Migrar 69 criterios para ganar 2–3 campos es riesgo alto / retorno bajo. El problema real es de **redacción**, no de esquema — plan R |
| Re-auditar las «240 fórmulas» y cerrar «48 defectos + 8 patrones» (Plan 03, tickets F3-04..F3-12) | Números viejos. El tracker real (`matriz_cruzada_auditorias.xlsx`, hoja `Hallazgos`, 237 filas) dice: **220 Cerrado, 6 Cerrado parcial, 10 sin acción, 1 verificado**. Lo pendiente de verdad son esos 6 parciales + 10 discrepancias abiertas + la deuda declarada de §15 — plan I |
| Reutilizar componentes «de `legacy/Tc.py`» (Plan 01, prompt P-F2-02) | Corregido en la constitución desde S19 (SIS-B-10): los componentes vivos están en `gui/componentes.py` (`Tooltip`, `MarcoScroll`, `CampoValidable`, `BotonAccion`, `BotonAyuda`). `legacy/Tc.py` es antecedente, ni siquiera importable |
| Deshabilitar el botón de correr cuando el pre-vuelo detecte bloqueos (Plan 01 §5) | El anticipo pre-corrida solo puede ser una **estimación** (la invocación real depende de la ruta que tome cada punto), y la regla de la casa es que ninguna estimación gobierna un filtro — menos aún un botón. El pipeline ya degrada con elegancia: cada bloqueo se convierte en `Bloqueo` por etapa y por punto. El pre-vuelo se construye como panel informativo — plan G3 |

---

## 4. Lo que SÍ queda por hacer — los cuatro planes nuevos

| Plan | Archivo | Qué cubre | Sesiones |
|---|---|---|---|
| **G** — GUI | `01_PLAN_GUI.md` | Agrupar por familia la pestaña 1, limpiar el lenguaje, filtro por fase, **anticipo de bloqueos pre-corrida**, **traza «¿de dónde sale este número?»** desde `PasoDeMemoria`, ayuda de conceptos | G1–G5 |
| **R** — Redacción | `02_PLAN_REDACCION_CRITERIOS.md` | Linter de estilo sobre las justificaciones (sin migración de esquema), reescritura por lotes con valor congelado, verificación de la Nota 1 de F_pga | R1–R3 |
| **I** — Cierre ingenieril | `03_PLAN_CIERRE_INGENIERIL.md` | Los 6 «Cerrado parcial» reales, las 10 discrepancias vivas, los residuos de la Familia C, y dos guardias opcionales (índice de fórmulas generado, chequeo dimensional piloto) | I1–I4 |
| **T** — Trazabilidad | `04_PLAN_TRAZABILIDAD.md` | Vigencia de ediciones (lo único del Plan 4 original que faltaba), bajar los dos trinquetes (9 partes sin cita transcrita, 37 elecciones pendientes), export CSV opcional para revisor externo | T1–T3 |

`05_BACKLOG.md` los ordena, marca dependencias y dice qué modelo y esfuerzo
usar en cada sesión, siguiendo la convención de la casa (la tabla §10 de
`hoja_de_ruta_correcciones_v12.md`).

### Ideas tuyas que estos planes CONSERVAN

Para que se vea que la revisión no fue demolición: la separación por familia en
la pantalla de entrada (G1), el pre-vuelo (G3, corregido a informativo), la
traza por número (G4 — tu mejor idea, y la más barata porque el dato ya
existe), la prohibición de verbos de bitácora / primera persona / mayúsculas
enfáticas en los criterios (R1), la reescritura por lotes con `valor` congelado
y verificado (R2), la nota ingenieril sobre la Nota 1 de F_pga (R3 — y ahora es
barata de verificar porque la tabla `MP.TFPGA` ya está transcrita y verificada
contra el PDF), la prueba de usabilidad con una persona real (G1/G5), y el
sello fecha+commit+conteo en documentos generados (T3).

---

## 5. Cómo usar estos planes (léelo antes del primer prompt)

1. **Un prompt = una sesión de Claude Code.** No mezcles dos en el mismo hilo.
   Cada prompt es autocontenido: lleva contexto, reglas, tarea, aceptación y
   ritual de cierre.
2. **Los prompts ordenan MEDIR antes de tocar.** Todos los números de estos
   planes (69 criterios, 33 sin valor, 116 citas, 37 elecciones pendientes…)
   se midieron el 2026-09-12 sobre `21f831d`; si la sesión mide otra cosa,
   **gana el repo** y el prompt lo dice.
3. **Modelo y esfuerzo** vienen sugeridos por sesión en `05_BACKLOG.md`,
   siguiendo el criterio de la casa: Opus/high para juicio sobre código,
   Sonnet para trabajo mecánico de amplitud, plan mode donde hay conflictos
   vinculantes cerca. No cambies el esfuerzo a mitad de sesión.
4. **El ritual de cierre va dentro de cada prompt** y es el de `CLAUDE.md`:
   suite en verde antes de commit, entrega en `origin/main`, y el conteo
   reportado como **par** (`passed + skipped = collected`; última medida
   documentada: 1800 recolectados) leído desde `origin/main`, diciendo con qué
   entorno (PyMuPDF sí/no, Tk sí/no).
5. **Si quieres que las sesiones puedan leer estos planes**, cométalos a
   `docs/planes_mejora/` — son documentos de diseño, como la propia
   `hoja_de_ruta_correcciones_v12.md`, no un tercer registro de avance (el
   estado sigue viviendo en el código y en el `.xlsx`).

### Comandos de medición que los prompts reutilizan

```bash
PYTHONPATH=src python3 - <<'EOF'
import criterios_adoptados as ca, variables_entrada as ve
from normativa import registro
print("criterios:", len(ca.CRITERIOS), "| sin valor:", len([k for k,c in ca.CRITERIOS.items() if c.valor is None]))
print("perfil:", len(ca.criterios_del_alcance("perfil")))
r = registro.construir()
print("citas:", len(r.citas), "| por transcribir:", r.cuenta_por_transcribir())
print("elecciones pendientes:", len(r.elecciones_pendientes()))
print("partes sin cita transcrita:", len(r.partes_sin_cita_transcrita()))
print("discrepancias vivas:", len(r.discrepancias_abiertas()))
EOF
```

(Los nombres exactos de las vistas pueden variar una letra; el prompt de cada
sesión manda verificar con `dir(registro)` antes de asumir.)
