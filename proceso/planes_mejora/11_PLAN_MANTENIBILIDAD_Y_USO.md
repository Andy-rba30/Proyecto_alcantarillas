# Plan de mantenibilidad y uso (propuesto 2026-11-21)

Material de proceso (`proceso/`), no del entregable. Nace de la auditoría
independiente del cierre de VE-7 (`main` en `362beb4`), que calificó la
aplicación con **8.5/10** y dejó el eje «mantenibilidad y uso» en **6.5/10**.
Este plan dice cómo subir ese eje **sin cambiar ninguna fórmula ni ningún
resultado**. Nada de lo que sigue está implementado: es el orden de trabajo
para una sesión posterior.

## 0. Principios que no se negocian

1. **Ninguna tarea de este plan cambia un número calculado.** El par
   `passed`/`skipped` de la suite completa con `NORMAS_DIR` y el contenido de
   los documentos generados (`docs/indice_formulas.md`, `docs/trazabilidad.csv`,
   `docs/validacion_*.md`) tienen que salir idénticos antes y después, salvo
   lo que la tarea declare (por ejemplo, el nombre del módulo emisor en el
   índice si se parte M9).
2. **Un commit por tarea**, con la suite de las áreas tocadas en verde, y una
   corrida completa en worktree limpio al cerrar cada bloque.
3. **Se respeta `CLAUDE.md`**: cualquier dependencia nueva se consulta antes
   (regla «Estilo»); un documento generado no se edita a mano; el sello lleva
   el par **medido en una sola corrida completa**, no deducido.
4. **Prioridad para la sustentación:** bloques A, B y C. El D (partir
   archivos grandes) va después, porque es el más grande y no cambia
   resultados.

## 1. Diagnóstico medido (2026-11-21, sobre `362beb4`)

| Hecho | Medida |
|---|---|
| `src/modulos/M9_cabezal.py` | 16 793 líneas, 314 funciones |
| `src/criterios_adoptados.py` | 14 732 líneas |
| `src/modelos.py` | 8 714 líneas |
| `src/constantes_normativas.py` | 6 678 líneas |
| `src/modulos/M11_reporte.py` | 5 992 líneas |
| `src/servicio.py` | 5 501 líneas |
| `src/modulos/M5_verificaciones.py` | 5 056 líneas |
| `CLAUDE.md` | 965 líneas, con historiales del tipo «169 desde VE-6-m9, 168 desde VE-5-gui…» mezclados con las reglas |
| `docs/decisiones_diferidas.md` | 9 757 líneas |
| Suite del entregable en CI (serie, sin `NORMAS_DIR`) | 9 181 tests, 2 h 27 min (run `44859160957`) |
| Archivos más lentos | `tests/test_t11_sensibilidad.py` (1 h 48 min en serie) y `tests/test_t11_validacion_integral.py` (1 h 07 min) |
| Archivos que nombran `M9_cabezal` | 81 entre `src/`, `tests/`, `gui/` y `cli.py` |

## 2. Bloque A — Suite en dos velocidades (esfuerzo BAJO, efecto ALTO)

**Objetivo:** que el día a día corra en ~10 min y la suite completa quede para
el cierre y el CI.

- **A1. Marcador `lento`.** Declararlo en `pyproject.toml`
  (`markers = ["lento: corridas pesadas; se excluyen con -m 'not lento'", ...]`)
  junto al `pdf` existente, y marcar a nivel de módulo
  (`pytestmark = pytest.mark.lento`) los archivos que se llevan la mayor parte
  del tiempo. Para elegirlos se **mide** primero con
  `pytest --durations=60 -p no:cacheprovider` sobre la suite completa; no se
  eligen a ojo. Candidatos conocidos: `test_t11_sensibilidad.py`,
  `test_t11_validacion_integral.py`, los de sincronía de
  `test_indice_formulas.py` y los `tests/apoyo/gui_*_real.py`.
- **A2. Guardia del marcador.** Un test en `tests/test_guardias_de_la_suite.py`
  que falle si un archivo de la lista medida en A1 no lleva la marca, o si
  la marca aparece en un archivo fuera de esa lista. El umbral de duración es
  de la suite, no un valor de proyecto: vive en el propio test, no en
  `src/tolerancias.py`. Sin la guardia, la lista
  se desincroniza como cualquier lista escrita a mano.
- **A3. `pytest-xdist` en `requirements-dev.txt`** (dependencia NUEVA:
  **consultar al dueño antes**, regla «Estilo»). Medido en esta auditoría:
  con `-n 4` la suite completa con `NORMAS_DIR` pasa de ~2.5 h a menos de 1 h
  en una máquina de 4 núcleos.
- **A4. CI en dos trabajos.** `.github/workflows/pruebas.yml`: un trabajo
  rápido en cada push (`-m "not lento" -n auto`) y el completo
  (`-n auto`, sin filtro) en `main`, en etiquetas `respaldo-*` y por
  `workflow_dispatch`.
- **A5. Corridas pesadas una vez por proceso.** Revisar los fixtures de
  `test_t11_sensibilidad.py` y `test_t11_validacion_integral.py`: con xdist,
  un fixture `scope="module"` se recalcula en cada worker que recibe un test
  del módulo. Opciones, en este orden: agrupar los tests del módulo en un
  mismo worker (`--dist loadfile` en el CI completo) o cachear la medida en
  disco por huella (`criterios_sha1` + `csv_sha1`, que `ContextoCorrida` ya
  calcula).

**Criterio de aceptación:** el par `passed`/`skipped` de la suite completa no
cambia; `-m "not lento"` corre en menos de 15 min con `-n 4`; el CI rápido
queda por debajo de 20 min.

## 3. Bloque B — Documentación para quien llega (esfuerzo BAJO, efecto ALTO)

- **B1. `CLAUDE.md` corto (~150–200 líneas), sólo reglas vigentes.** Cada
  regla en presente y sin su historia. Los historiales («desde T-x…», los
  conteos acumulados de criterios, los precedentes S16/S19/S21) se mueven
  enteros, con `git mv` o copia literal, a
  `proceso/historia_de_las_reglas.md`, con un enlace por regla. **Cuidado:**
  hay tests y guardias que leen `CLAUDE.md` (buscarlos con
  `grep -rn "CLAUDE.md" tests src proceso/tests`); cada uno se adapta
  declarándolo, no se borra.
- **B2. `docs/guia_del_desarrollador.md` (2–3 páginas).** Contenido mínimo:
  1. El flujo de datos: CSV y JSON → `servicio.correr` → fases M0…M12 →
     `Informe` con `ContextoCorrida` → M11 (HTML/PDF/JSON).
  2. Las tres casas de los valores (`constantes_normativas.py`,
     `criterios_adoptados.py`, `datos_sitio.py`) y las cinco etiquetas, con
     un ejemplo de cada una.
  3. Recetas: cómo se añade un criterio [A] (ficha, `forma`, `nivel`,
     `sensibilidad`, `resolucion`, consumidor, test de nivel medido); cómo se
     añade una verificación (`Verificacion`, `PasoDeMemoria`, `Fundamento`,
     `cita_id`); cómo se añade una cita al registro y se regeneran los
     manifiestos.
  4. Cómo se corre: suite rápida, suite completa con `NORMAS_DIR`, tests
     `-m pdf`, regeneración de los documentos generados y sellado.
- **B3. `docs/manual_usuario.md`, orientado al ingeniero que diseña.** Un
  ejemplo completo de principio a fin: preparar el CSV (columnas mínimas por
  familia), `sitio.json`, `--datos-externos`; correr perfil y expediente;
  leer el pre-vuelo; declarar los pendientes; exportar la memoria. Puede
  apoyarse en `docs/guia_perfil.md`, pero no la sustituye.
- **B4. Índice de `docs/decisiones_diferidas.md`.** Una tabla al inicio con
  ficha, tema y estado (abierta, cerrada, bloqueo declarado), generada si es
  posible, para no recorrer 9 757 líneas.

**Criterio de aceptación:** una persona que no participó en el proyecto puede,
sólo con B2, añadir un criterio [A] de prueba con su test y verlo en la
memoria; y, sólo con B3, correr una obra de ejemplo y obtener su memoria.

## 4. Bloque C — Uso real (esfuerzo MEDIO, efecto ALTO en la sustentación)

- **C1. Proyecto piloto real.** Una obra ya diseñada y construida (expediente
  aprobado), corrida con la app; comparar diámetros, cotas, cabezal y
  metrados con lo que se construyó y documentar cada diferencia con su causa
  (criterio distinto, dato de sitio, error del expediente original o de la
  app). Sus datos van rotulados en `tests/fixtures/` sólo si el dueño
  autoriza publicarlos; si no, el informe va a `proceso/` sin los datos.
- **C2. Plantillas comentadas.** `plantillas/` con un CSV mínimo por familia
  (A, B, C), un `sitio.json` y un `datos_externos.json` con cada clave
  explicada, y una sesión vacía de la GUI («proyecto nuevo»). Que un test las
  corra con `--prevuelo` para que no envejezcan.
- **C3. Distribución sin Python.** Un ejecutable con PyInstaller (o un
  paquete con intérprete embebido) para Windows, con su receta en
  `docs/guia_del_desarrollador.md`. **Dependencia nueva: consultar antes.**
  Verificar que WeasyPrint (PDF) funcione empaquetado; si no, exportar HTML
  y dejar el PDF al navegador.
- **C4. Mensajes de la GUI ante los bloqueos más frecuentes.** Con el piloto,
  anotar qué bloqueos ve primero un usuario nuevo y revisar que el tablero
  de la pestaña 4 diga **qué dato falta y dónde se declara** sin leer
  `CLAUDE.md`.

## 5. Bloque D — Partir los archivos grandes (esfuerzo MEDIO-ALTO, después de la sustentación)

### D0. Prerrequisito obligatorio: que el AST vea subpaquetes

Hoy dos herramientas enumeran los módulos de cálculo **sin recursión**:

- `src/indice_formulas.py:438` — `for ruta in sorted(MODULOS.glob("*.py"))`
  (atribuye cada `fundamento_id` a su módulo emisor).
- `src/variables_entrada.py:276` — `sorted(_MODULOS.glob("M*.py"))` (estima
  qué fase consume cada variable).

Si `M9_cabezal.py` pasara a ser `M9_cabezal/` con varios archivos, las dos
**dejarían de ver a M9 sin fallar**: el índice perdería la atribución de sus
fundamentos y el censo de consumo daría falsos negativos. Antes de partir
nada:

1. Cambiar ambas a `rglob` (o a recorrer el paquete) con el nombre del
   módulo emisor = el del subpaquete de primer nivel (`M9_cabezal`), para
   que el índice no cambie.
2. Un test que construya un subpaquete de prueba en `tmp_path` y compruebe
   que las dos lo ven.
3. Buscar otras enumeraciones del mismo tipo
   (`grep -rn "glob(\|iterdir(" src tests`) y decidir cada una.

### D1. `src/modulos/M9_cabezal.py` → subpaquete `src/modulos/M9_cabezal/`

Partición propuesta (a confirmar leyendo el archivo; los nombres siguen las
secciones que ya tiene):

| Archivo | Contenido |
|---|---|
| `__init__.py` | reexporta **los mismos nombres públicos** que hoy (`from .estabilidad import estabilidad_del_alero`, …), para que los 81 archivos que importan `M9_cabezal` no cambien |
| `geometria.py` | regla de T-7a, embocadura, cabezal del punto, aleros con esviaje |
| `empujes.py` | activo, reposo, Mononobe-Okabe, incremento sísmico, empuje declarado |
| `estabilidad.py` | E1 a E3 (ASD y LRFD), dimensionamiento de la zapata por estabilidad |
| `armado.py` | A1 a A8, peralte por armado, cortante general de 5.7.3.4.2 |
| `ciclopeo.py` | C1 a C8 |
| `alero.py` | franjas del alero, su zapata y su armado (VE-6, VE-7) |

Reglas: mover sin reescribir; las constantes `CRITERIO_*` quedan en un solo
sitio (`_criterios.py` del subpaquete) y se reexportan; la guardia de
literales (`tests/test_sin_literales.py`) y las de importación
(`tests/test_ext9_paquete_servicio.py`) siguen en verde sin excepciones
nuevas; los documentos generados se regeneran y su diferencia tiene que ser
**nula** (o sólo rutas de archivo, declarado).

### D2. `src/criterios_adoptados.py` → mecanismo + fichas por fase

El mecanismo (`Criterio`, `valor`, `_verificar_*`, registro de usos,
declaración en caliente) se queda en `criterios_adoptados.py`; las fichas
pasan a `src/criterios/{hidrologia,hidraulica,conducto,cabezal,proteccion,metrados,...}.py`
y se registran en el mismo diccionario. Precaución: `criterios_sha1` (la
huella del `ContextoCorrida`) hoy se calcula sobre ese archivo; hay que
decidir si pasa a ser la huella del conjunto de archivos de fichas, y
declararlo, porque cambiará el valor de la huella aunque no cambie ningún
criterio.

### D3. Opcionales

`modelos.py` (por familia de tipos), `M11_reporte.py` (plantilla, secciones,
exportadores) y `constantes_normativas.py` (por norma), con las mismas
reglas que D1.

**Criterio de aceptación del bloque D:** mismo par `passed`/`skipped`, los
documentos generados idénticos (salvo rutas declaradas), ningún archivo de
`src/` por encima de ~3 000 líneas y ninguna importación de fuera del
subpaquete cambiada.

## 6. Orden sugerido y efecto esperado

| Orden | Tarea | Esfuerzo | Efecto en «mantenibilidad y uso» |
|---|---|---|---|
| 1 | A1–A5 (suite en dos velocidades) | 1 sesión | +0.5 |
| 2 | B1–B2 (`CLAUDE.md` corto y guía del desarrollador) | 1 sesión | +0.5 |
| 3 | C1 (piloto real) y C2 (plantillas) | 1–2 sesiones más el tiempo del dato real | +0.5 |
| 4 | B3–B4 (manual de usuario, índice de fichas) | 1 sesión | +0.2 |
| 5 | C3–C4 (ejecutable, mensajes de la GUI) | 1 sesión | +0.2 |
| 6 | D0 → D1 → D2 (partir archivos) | 2–3 sesiones | +0.3 |

Con 1 a 3 el eje pasa de ~6.5 a ~8 y la nota global a ~9.

## 7. Cómo retomar este plan

Pegar en una sesión nueva sobre `Andy-rba30/Proyecto_alcantarillas`:

```text
Implementa el bloque <A|B|C|D> de proceso/planes_mejora/11_PLAN_MANTENIBILIDAD_Y_USO.md.
Respeta sus principios (sección 0): ninguna fórmula ni resultado cambia; un commit por
tarea; suite completa con NORMAS_DIR en worktree limpio al cerrar el bloque, con el par
medido en UNA corrida completa; dependencias nuevas consultadas antes. Para el bloque D,
empieza obligatoriamente por D0. Al terminar, marca en este archivo qué tareas quedaron
hechas, con su commit.
```

## 8. Estado

Actualizado el 2026-11-23 por la sesión `claude/nifty-brahmagupta-rfj9o6`
(PR #47), que integra la de `claude/serene-keller-2p7pcs` y sus ramas de
agentes; ésta retomaba la de `v2/mantenibilidad-y-uso` (expiró con D2 a medias). Se va
actualizando en cada hito; si la sesión se corta, esta tabla y el bloque de
estado de `ve3_estado/LEEME.md` dicen desde dónde seguir.

| Tarea | Estado | Commit |
|---|---|---|
| A1 marcador `lento` | hecho | `138adde` |
| A2 guardia del marcador | hecho | `b4bd418` |
| A3 `pytest-xdist` | hecho | `74f7b94` |
| A4 CI en dos trabajos | hecho | `ab0d9ff` |
| A5 corridas pesadas por proceso | hecho | `2da284d` |
| B1 `CLAUDE.md` corto | hecho; D2/D3 reflejados | `6aa1cec`, `c74e9a8` |
| B2 guía del desarrollador | hecho; D2/D3 reflejados | `78df332`, `c74e9a8` |
| B3 manual de usuario | hecho | `eb0a721` |
| B4 índice de fichas | hecho | `89e82e4` |
| C1 piloto real | **bloqueado: falta el expediente real del dueño** | — |
| C2 plantillas | hecho | `91d561c` |
| C3 receta PyInstaller | hecho; sin verificar el ejecutable en Windows ni WeasyPrint empaquetado | `acb961d` |
| C4 mensajes de la pestaña 4 | hecho; corregido el import de `MH_hidrologia` que rompía la regla de T-1 | `c93e7bd`, `fe60c5c` |
| D0 AST de subpaquetes | hecho; corregido `base / "__init__.py"`, que la guardia de aritmética del índice (test `lento`) rechazaba | `030d208`, `571accc` |
| D1 `M9_cabezal/` | hecho; corregidas tres guardias que seguían leyendo `M9_cabezal.py` | `ab63aba`, `198aa65` |
| D2 `src/criterios/` | hecho: mecanismo en `criterios_adoptados.py` y fichas por dominio; `criterios_sha1` cubre el catálogo (ficha D2-01: cambia el valor de la huella sin cambiar criterio); línea base con sólo esa diferencia | `0b8c4a7`, `bf99cda`…`6d402c6` (fusión `d027a7e`), `07b3b98` |
| D3 `modelos.py` | hecho: 13 submódulos (máx. 1 617 líneas), AST de los 299 nodos idéntico, `__module__` normalizado a `src.modelos` (el JSON de sesión escribe `__module__:__qualname__`), DAG sin ciclos; CLI y JSON idénticos byte a byte; `import src.modelos` +5 ms | `80462f7` (fusión con conflicto resuelto en `test_t8_correcciones`) |
| D3 `M11_reporte.py` | hecho: 18 archivos más `__init__.py` (19 `.py`), todos de < 700 líneas, memoria HTML/CSV/JSON idéntica byte a byte (salvo fecha) en las 5 corridas de la línea base; el ancla del manifiesto que quedaba en `M11_reporte.py` pasa a `tablas_diseno.py`; guardias por AST sobre todo el subpaquete (`tests/apoyo/fuente_m11.py`) | `ac43c6e` (fusión `5b765f4`), `c9e1c04` |
| D3 `constantes_normativas.py` | diferida (ficha D3-03, dictamen Fable APROBADO CON CAMBIOS): la sesión que la empezó no dejó commit; partirla enmienda la regla de las tres casas sin cambiar ningún resultado | `0e4aa4d`, `5b6f310` |

**La CI rápida sobre la punta de `v2` (`0b8c4a7`, run `45196377613`)**: 59
failed, 8 659 passed, 173 skipped (sin los `lento` y sin `NORMAS_DIR`). 52
fallos son de D2 a medias; 6 de D1 y 1 de C4, ya corregidos en `198aa65` y
`fe60c5c`.

**Hallazgos de la auditoría del cierre de VE-7**
(`ve3_estado/AUDITORIA_CIERRE_VE7_2026-11-21.md`):

| Hallazgo | Estado | Commit |
|---|---|---|
| H1 sello deducido | hecho: suite completa MEDIDA en worktree limpio sobre `ca234cf` (`9213 passed, 13 skipped`, paralelo + aislado; sesión `claude/confident-cannon-0vgath`) y sello con ese par; fila en la bitácora | `90b8f74` |
| H2 test de `import cli` intermitente | hecho: mínimo de siete corridas, mismo límite de 0.30 s (decisión del dueño) | `728a791` |
| H3 cifras a mano en el anexo de sensibilidad | hecho: se leen de la corrida; medido, el anexo no cambia | `1961b4a` |
| H4 LEEME y `PROMPT_RETOMAR` desactualizados | hecho | `741043c` |
| H5 | informativo, sin acción aparte de H1 | — |

**Pasos 1 a 5: hechos en `claude/nifty-brahmagupta-rfj9o6`** (fusión de D2
`d027a7e`; LF `6a504c0`; fichas `0e4aa4d`, `5b6f310`; documentación `c74e9a8`;
manifiesto `c9e1c04`; línea base `07b3b98`; índice `f3ae153` con sello
PROVISIONAL). `-d3-constantes` nunca se subió: D3-03 la difiere. La suite
rápida sobre la integración dio 17 fallos, todos cerrados: 12 del manifiesto
(ancla de M11 y mudanzas de D2), 3 de la línea base (huella) y 1 de Tk
(entorno sin Tk). El paso 6 lo corre esta sesión en la nube (Linux, Python
3.12, Tk con `xvfb-run`, `NORMAS_DIR` = clon de `Andy-rba30/normas`): una
corrida completa mide el par, se sella con él y una segunda corrida completa
lo confirma.

**Paso 6 hecho (2026-11-24, sesión `claude/confident-cannon-0vgath`)**: sobre las rondas 1 y 2 de compatibilidad Windows (fichas WIN-01 a WIN-03), la suite completa se midió en la nube (Linux, `NORMAS_DIR`, Tk) y no en la máquina del dueño, que la había corrido en Windows sobre `7efb15d` (18 fallos: 2 de sello y 16 de plataforma, corregidos en las dos rondas). Sello `90b8f74`; el paso 7 (fast-forward de `main`) lo autorizó el dueño.

**El plan, en orden** (registro de lo que se pidió):

1. Integrar las ramas de los agentes (`claude/serene-keller-2p7pcs-d2`,
   `-d3-modelos`, `-d3-constantes`) en `claude/serene-keller-2p7pcs`
   (`-d3-m11` integrada en `5b765f4`; `-d3-modelos` integrada después). Al integrar D2, reaplicar la huella
   en `src/modulos/M11_reporte/_base.py` (`ARCHIVO_CRITERIOS`) y
   `trazabilidad.py` (`criterios_fecha`).
2. Normalizar los saltos de línea: 22 archivos de `v2` se subieron con CRLF
   desde Windows (`conftest.py`, `pyproject.toml`, `requirements-dev.txt`,
   `.gitignore`, `docs/decisiones_diferidas.md`, `src/responsable.py`,
   `src/modulos/M9_cabezal/*.py`, …). Pasan a LF y `.gitattributes` lo fija
   (`* text=auto eol=lf`), salvo los dos CSV de `tests/linea_base_familia_c/`
   que ya eran CRLF en `main` (los escribe el módulo `csv`).
3. Regenerar los documentos generados (`manifiesto_citas.md`,
   `manifiesto_registro_normativo.md`, `trazabilidad.csv`, `indice_formulas.md`)
   con sello PROVISIONAL y la línea base (`tests/linea_base_familia_c/regenerar.sh`):
   la única diferencia admitida es `criterios_sha1`, porque desde D2 la huella
   cubre el mecanismo y las fichas de `src/criterios/`.
4. Fichas en `docs/decisiones_diferidas.md`: D2 (con la declaración del
   cambio de la huella), D3 por archivo y EXT-8-06 (H2); regenerar su índice.
5. `CLAUDE.md` y `docs/guia_del_desarrollador.md` con la estructura nueva
   (`src/criterios/`, `src/modelos/`, `src/modulos/M11_reporte/`); esta tabla al día; push.
6. **El dueño**: suite completa con `NORMAS_DIR` en su máquina sobre el
   commit final, con el prompt que deja esta sesión; corregir lo que falle;
   sellar con el par MEDIDO (`python -m src.indice_formulas --escribir --suite
   "<par>"` y `python -m src.normativa.manifiesto --escribir --suite "<par>"`)
   y fila en `proceso/bitacora_conteos_y_entorno.md` (cierra H1).
7. Integración en `main` por fast-forward, sólo con la autorización del dueño.
