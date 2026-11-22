# Reglas del proyecto

> Constitución técnica vigente (reglas en presente). El historial de precedentes,
> conteos acumulados y decisiones de cada sesión vive en
> [proceso/historia_de_las_reglas.md](proceso/historia_de_las_reglas.md).

## Fuente de verdad
- Fuente normativa única: `docs/hoja_de_ruta_alcantarillas_v*.md` (`v8`). Toda cita de numeral se verifica contra ella; nunca se inventa un numeral.
- **Única excepción: la fuente primaria** (el PDF en `NORMAS_DIR`, verificado con numeral, página impresa y texto literal). Si prevalece sobre la hoja de ruta: declarar la discrepancia en el punto de uso, reportar el defecto contra la hoja de ruta y advertir que la hoja de ruta sigue desactualizada.
- **Vacíos:** si la hoja de ruta no resuelve un parámetro requerido, no se inventa: se declara en `criterios_adoptados` (`valor=None`, etiqueta `[A]`, justificación y resolución) y se detiene el cálculo con `CriterioPendienteError`.
- Ver historia: [Fuente de verdad](proceso/historia_de_las_reglas.md#fuente-de-verdad).

## Taxonomía de etiquetas
Todo valor del proyecto lleva una de cinco etiquetas (en orden de determinación en M11):
- **`[N]`** Exigencia normativa peruana vigente con numeral verificado (`src/constantes_normativas.py`).
- **`[N→]`** Valor normativo aplicado por analogía con declaración expresa.
- **`[S]`** Dato de sitio obtenido mediante procedimiento normativo real sobre la obra; declara **trazabilidad** obligatoria y no tiene sensibilidad. De corredor vive en `src/datos_sitio.py` (sobrescribible por sesión vía `--datos-sitio` y `datos_sitio.establecer_dato_dinamico` con trazabilidad y fecha); punto a punto es columna del CSV.
- **`[C]`** Vacío normativo cubierto con fuente técnica reconocida (FHWA, AASHTO).
- **`[A]`** Adopción declarada del proyectista con rango o conjunto de **sensibilidad** obligatorio.
- Tablas normativas (`[N]`) y elección de fila (`[A]`) siempre se separan. Ver historia: [Taxonomía de etiquetas](proceso/historia_de_las_reglas.md#taxonomía-de-etiquetas-cinco-no-cuatro).

## Nivel de entrega: perfil o expediente
- Todo `Criterio` y `DatoSitio` declara `Criterio.nivel` (`NIVEL_PERFIL` o `NIVEL_EXPEDIENTE`), comprobado por ejecución en las dos direcciones (`tests/test_nivel_medido.py` y `tests/test_cierre_perfil.py`).
- Todo criterio sin valor declara `nivel`. Todo `[A]` de perfil declara `sensibilidad` y `resolucion`. Ver historia: [Nivel de entrega](proceso/historia_de_las_reglas.md#nivel-de-entrega-perfil-o-expediente).

## Arquitectura
- **Tres casas de valores:** `constantes_normativas.py` (`[N]`), `criterios_adoptados.py` (`[N→]`, `[C]`, `[A]` y `[S]` pendientes) y `datos_sitio.py` (`[S]` de corredor). Fuera de ellas (y de las exenciones `tolerancias.py`, `dominios.py`, `constantes_fisicas.py`) no hay literales numéricos de proyecto; excepciones matemáticas de fórmula llevan `# literal-ok: <razón>` (`tests/test_sin_literales.py`).
- **Paquete único `src/` y servicio:** todo import interno usa `from src... import ...`; prohibido manipular `sys.path` y prohibidos los imports relativos fuera de `src/normativa/` (`tests/test_ext9_paquete_servicio.py`). La orquestación vive en `src/servicio.py`; `cli.py` es adaptador y reexporta atributos esperados por `gui/` y tests.
- **Módulos y contratos:** los tipos que fluyen entre módulos viven en `src/modelos.py`. `MH_hidrologia.py` (Fase 1-bis) solo lo importa `servicio.py`; un `Q_m3s` lleno en CSV gana y no se recalcula. `M10_espaciamiento.py` (Fase 10) verifica `VB1` y `VB2`; `M9_cabezal` (Fase 9) diseña por punto estabilidad y armado (o verificación ciclópea); `M12_metrados.py` (Fase 11) mide sin desperdicio ni esponjamiento.
- **Puerta única de declaración:** `Criterio.forma` y `_verificar_criterio` validan archivo, declaración en caliente y escritura permanente. Ningún `valor=None` se sustituye por un default silencioso y cada lectura de criterio/`[S]` registra uso.
- **Estado inmutable y memoria emitida por cálculo:** `servicio.correr` limpia usos al entrar y congela `Informe.contexto` (`ContextoCorrida`) al salir; los exportadores solo leen del contexto. Cada función de cálculo emite `PasoDeMemoria` con `Fundamento` (`src/normativa/fundamentos.py`), textos literales desde `Registro.textos_literales()` y separación visual entre fuente (`class="fuente"`), interpretación (`class="interpretacion"`) y cálculo; `M11_reporte` solo formatea.
- Ver historia: [Arquitectura](proceso/historia_de_las_reglas.md#arquitectura).

## Unidades
- Todo el motor opera en **SI** (`m`, `m³/s`, `m/s`, `Pa`, `kN`). Ninguna función de cálculo acepta ni devuelve unidades imperiales o `kg/cm²`.
- Toda constante empírica dependiente de unidades lleva sufijo `_SI` y comentario con su equivalente imperial. La conversión de presentación ocurre únicamente en reporte. Ver historia: [Unidades](proceso/historia_de_las_reglas.md#unidades).

## Excepciones (taxonomía)
Toda excepción de dominio hereda de `modelos.ErrorProyecto` (prohibido usar `Exception` genérica en lógica de negocio; fallos de E/S salen como `FileNotFoundError`):
- `CriterioPendienteError`: criterio `[A]` o `[S]` sin valor; viaja como `Bloqueo` al tablero de resumen.
- `DisenoNoFactibleError`: ninguna combinación material/diámetro cumple; incluye motivo y, si aplica por geometría pura, `delta_rasante_m` como cota inferior.
- `DatoFaltanteError`: falta una columna del CSV, una celda obligatoria o un dato requerido que no es columna del CSV (como `--datos-externos` o un tablero externo).
- `DatoInvalidoError`: el dato existe pero incumple tipo, rango de `dominios.py` o consistencia de fila.
- `LimiteNumericoError`: entradas válidas cuya combinación desborda aritméticamente o anula un denominador; se valida a la salida sin inventar techos en `dominios.py` y con condición positiva negada (`not A > 0`, forma `MAT-D13`).
- `MetodoNoEvaluableError`: datos y criterios válidos pero fuera del dominio del método implementado; viaja como `Bloqueo` con `TipoDeBloqueo.METODO_NO_EVALUABLE` y rótulo propio por módulo.
- Ver historia: [Excepciones](proceso/historia_de_las_reglas.md#excepciones-taxonomía).

## Estilo
- Python 3.11+. Dependencias declaradas en `requirements.txt` y `requirements-dev.txt` (sincronizadas con `pyproject.toml`); cualquier dependencia nueva se consulta antes.
- Prohibido comparar flotantes con `==`; usar tolerancias explícitas y nombradas (`src/tolerancias.py`).
- Identificadores y docstrings en español; toda función de cálculo cita en su docstring el numeral que la sustenta. Ver historia: [Estilo](proceso/historia_de_las_reglas.md#estilo).

## GUI
- Tkinter + `ttkbootstrap`; componentes compartidos en `gui/componentes.py` (no reutilizar ni importar `legacy/Tc.py`, marcado `SUPERSEDED`).
- Navegación lateral (`NavegacionLateral`) montada sobre `ttk.Notebook` (`self.nb`), conservando `nb.select`/`nb.tabs`/`nb.index`/`nb.add` como única fuente del paso activo.
- Pestaña 2 declara por editores tipados (`gui/editores.py` y `src/editores.py`) sobre un único parser (`interpretar_texto_declarado`); la ayuda de entrada se deriva del censo (`gui/ayuda_entrada.py`); el anticipo de Pestaña 1 (`src/anticipo.py`) es informativo y nunca bloquea botones; el barrido (`src/barrido.py`) es transaccional y usa el comparador (`src/comparador.py`). Ver historia: [GUI](proceso/historia_de_las_reglas.md#gui).

## Tests
- Suite del entregable en `tests/` (`testpaths = ["tests"]`); mínimo un test por módulo y contraste con `tests/fixtures/casos_patron.py`.
- **Suite rápida de trabajo:** `pytest -m "not lento" -n auto`. **Suite completa:** `pytest -n auto --dist loadfile` con `NORMAS_DIR`.
- Documentos generados (no editar a mano; vigilados por tests de sincronía):
  - `docs/manifiesto_citas.md`, `docs/manifiesto_registro_normativo.md` y `docs/trazabilidad.csv`: `python -m src.normativa.manifiesto --escribir --suite "<N passed, M skipped (entorno)>"`.
  - `docs/indice_formulas.md`: `python -m src.indice_formulas --escribir --suite "<N passed, M skipped (entorno)>"`.
  - `docs/validacion_*.md`: `python -m tests.apoyo.<modulo> --escribir`.
- Ver historia: [Tests](proceso/historia_de_las_reglas.md#tests).

## Dónde están los PDF de normas
- La única vía para los PDF de normas es la variable de entorno **`NORMAS_DIR`** apuntando a un clon de `Andy-rba30/Normas` (este repositorio no versiona ningún PDF).
- Toda lectura pasa por `src/normativa/fuentes.py` (`directorios_de_normas()`, `ruta_pdf()`). Un `NORMAS_DIR` inexistente falla con `FileNotFoundError`; sin `NORMAS_DIR` definido, los tests `-m pdf` se saltan con motivo explícito (`conftest.py`). Ver historia: [PDF de normas](proceso/historia_de_las_reglas.md#dónde-están-los-pdf-de-normas-normas_dir-y-sólo-allí).

## Material de proceso
- Todo material de auditoría y proceso vive en `proceso/` (`export-ignore` en `.gitattributes`, fuera de `tests/`):
  - `proceso/bitacora_conteos_y_entorno.md`: ritual de cierre y tabla de conteos por entorno.
  - `proceso/reglas_de_correccion_de_auditorias.md`: protocolo de clusters, conflictos vinculantes y tracker.
  - `proceso/historia_de_las_reglas.md`: archivo histórico íntegro de `CLAUDE.md`.
  - `proceso/verificar_sesion.py` y `proceso/tests/`: verificación y guardias de proceso (`python -m pytest proceso/tests`). Ver historia: [Material de proceso](proceso/historia_de_las_reglas.md#material-de-proceso-proceso-desde-t-12).
