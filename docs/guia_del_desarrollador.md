# Guía del desarrollador — `Proyecto_alcantarillas`

> Documento técnico de incorporación rápida. Complementa la constitución en
> [`CLAUDE.md`](../CLAUDE.md) y el contrato de entradas en
> [`docs/contrato_entradas.md`](contrato_entradas.md).

---

## 1. Arquitectura y flujo de datos

El paquete principal vive en [`src/`](../src/__init__.py) con un único estilo de importación (`from src... import ...`). Las interfaces (`cli.py` y `gui/`) actúan como adaptadores sin lógica de cálculo.

```text
CSV puntos (M0) + --datos-externos + --datos-sitio + [--cuencas / --estacion]
   │
   ▼
src/servicio.py::correr(...)
   ├─► Fase 0-bis  ML_licuefaccion       (evaluación de licuefacción)
   ├─► Fase 1-bis  MH_hidrologia         (caudal por cuenca si Q_m3s viene vacío)
   ├─► Fase 2      M1_clasificacion      (familia A/B/C y período de retorno TR)
   ├─► Fases 3–5   MD + M2..M5           (iteración material/sección, Manning, HDS-5, V1–V10/VC)
   ├─► Fase 6      M6_proteccion         (socavación y enrocado HEC-14 / Laushey)
   ├─► Fase 7      M7_geometria          (rasante, recubrimiento y longitud del conducto)
   ├─► Fase 8      M8_estructural        (cargas vivas/muertas, M170M, A796, M294, pórtico)
   ├─► Fase 9      M9_cabezal            (geometría por punto, estabilidad, armado, aleros)
   ├─► Fase 10     M10_espaciamiento     (alivios de cuneta VB1/VB2)
   └─► Fase 11     M12_metrados          (compatibilidad rasante y metrados EG-2013)
   │
   ▼
Informe + ContextoCorrida (foto inmutable de usos, efectivos y huellas SHA-1)
   │
   ▼
src/modulos/M11_reporte/ (solo formatea: JSON, HTML completa/resumida, PDF, CSV resumen)
```

### Reglas clave del flujo
- **Estado inmutable de corrida:** `servicio.correr` limpia registros al inicio (`reiniciar_usos()`) y captura `ContextoCorrida` al terminar. Los exportadores (`cli.informe_json`, `M11_reporte`) leen exclusivamente desde `Informe.contexto`.
- **La memoria la emite el cálculo:** cada función matemática devuelve su resultado y sus objetos `PasoDeMemoria` (construidos con `modelos.paso(fundamento_id, ...)`). `M11_reporte` no ejecuta aritmética sobre magnitudes ni duplica textos normativos.
- **Taxonomía de errores:** toda falla de datos o dominio hereda de `modelos.ErrorProyecto` (`DatoFaltanteError`, `DatoInvalidoError`, `CriterioPendienteError`, `DisenoNoFactibleError`, `LimiteNumericoError`, `MetodoNoEvaluableError`).

---

## 2. Las tres casas de valores y las cinco etiquetas

Ningún literal numérico de proyecto puede vivir suelto en los módulos de cálculo (`tests/test_sin_literales.py`). Toda magnitud pertenece a una de estas tres casas:

| Casa | Archivo | Qué contiene | Etiqueta(s) |
|---|---|---|---|
| **Norma peruana fija** | `src/constantes_normativas.py` | Exigencias con numeral verificado, idénticas en todo el país | `[N]` |
| **Criterios del proyecto** | `src/criterios/*.py` (fichas por dominio) y `src/criterios_adoptados.py` (mecanismo) | Analogías, fuentes extranjeras, adopciones y vacíos declarables | `[N→]`, `[C]`, `[A]`, `[S]` pendientes |
| **Datos de sitio del corredor** | `src/datos_sitio.py` | Hechos geográficos/sísmicos leídos sobre este corredor (sobreescribibles por `--datos-sitio`) | `[S]` |

*(Las tolerancias numéricas en `src/tolerancias.py`, límites físicos de lectura en `src/dominios.py` y constantes físicas universales en `src/constantes_fisicas.py` quedan exentos por no ser parámetros de diseño.)*

### Ejemplos reales de cada etiqueta

1. **`[N]`** — `Y_SOBRE_D_MAX = 0.75` en `src/constantes_normativas.py` (Manual MTC Sec. 4.1.1.3.7 b).
2. **`[N→]`** — `"resguardo_HW_subrasante"` (`valor="segun_CBR"`) en `src/criterios/hidraulica.py` (aplicado por analogía del Manual de Suelos y Pavimentos).
3. **`[S]`** — `"PGA_roca_B"` en `src/datos_sitio.py` (lectura del mapa sísmico E.030 para el corredor; requiere `trazabilidad`, sin `sensibilidad`).
4. **`[C]`** — `"hds5_embocadura_hdpe"` en `src/criterios/hidraulica.py` (coeficientes tomados de FHWA HDS-5).
5. **`[A]`** — `"gamma_EQ"` (`valor=0.5`, `sensibilidad=(0.0, 1.0)`) en `src/criterios/sismo.py` (adopción del proyectista con rango de barrido obligatorio).

---

## 3. Recetas paso a paso

### 3.1 Cómo añadir un criterio `[A]`
1. **Registra la ficha** en el archivo de su dominio en `src/criterios/` (`hidraulica.py`, `cabezal_calculo.py`, …), dentro de su `CRITERIOS` (indentación de 4 espacios para la clave); el catálogo `criterios_adoptados.CRITERIOS` la toma de ahí. Un archivo de fichas nuevo se registra en `MODULOS_DE_FICHAS` (`src/criterios/__init__.py`), o la guardia `tests/test_d2_catalogo_de_fichas.py` lo rechaza. Especifica:
   - `valor` (o `None` si queda pendiente de declarar),
   - `nivel` (`NIVEL_PERFIL` o `NIVEL_EXPEDIENTE`),
   - `etiqueta="A"`,
   - `forma` (de `criterios_adoptados.FORMAS`, p. ej. `FORMA_FLOAT`, `FORMA_CATEGORIA`, `FORMA_DICT_CON_CAMPOS`),
   - `concepto` y `justificacion` en estilo impersonal y unidades SI (cumpliendo las reglas E1–E7 de `tests/test_estilo_criterios.py`),
   - `fuente`, `sensibilidad` (obligatoria en todo `[A]` de perfil) y `resolucion` (`EnRango`, `DeTabla`, `Libre`, etc.).
2. **Conéctalo en el módulo consumidor** mediante `ca.valor("mi_clave")` (o `ca.valor_si_declarado(...)` si es `opcional=True`) y declara la constante de clave `CRITERIO_...` en dicho módulo.
3. **Actualiza las guardias y tests:**
   - Verifica `tests/test_nivel_medido.py` (comprueba `nivel` en las dos direcciones).
   - Verifica `tests/test_estilo_criterios.py` (linter E1–E7).
   - Añade tests unitarios y de sensibilidad en el módulo correspondiente y regenera documentos si corresponde.

### 3.2 Cómo añadir una verificación con `PasoDeMemoria`
1. **Asegura el `Fundamento`** en `src/normativa/fundamentos.py` (p. ej. `"F5.V1"`): define `id`, `fase`, `titulo`, `verbo` compatible con el `caracter` de su `cita_id`, y `que_pasa_si_no_se_hace`.
2. **Construye el paso y la verificación** dentro de la función de cálculo (ver ejemplo en `src/modulos/M5_verificaciones.py::v1_borde_libre`):
   - Emite el paso llamando a `modelos.paso("F5.V...", codigo=..., que=..., formula=..., sustitucion=..., resultado=..., unidad=..., umbral=..., cumple=...)`.
   - Devuelve `Verificacion(cumple=..., numeral=..., valor=..., criterio_aplicado=..., pasos=(p,))` (nunca un `bool` desnudo).
3. **Verifica las guardias:**
   - Contrasta el módulo contra `tests/fixtures/casos_patron.py` (`tests/test_guardias_de_la_suite.py`).
   - Comprueba `tests/test_indice_formulas.py` (el argumento de `paso(...)` debe ser un literal `str`).

### 3.3 Cómo añadir una cita al registro normativo y regenerar manifiestos
1. **Verifica la fuente en `NORMAS_DIR`** usando PyMuPDF:
   ```powershell
   $env:NORMAS_DIR="D:\Normas_repo"
   py -3.13 -m src.normativa.extraccion texto hds5 20
   ```
2. **Registra la fuente/cita/tabla** en `src/normativa/fuentes.py`, `src/normativa/citas.py` o `src/normativa/tablas.py` conservando tildes y texto literal exacto de la página verificada (`Verbatim`, `Verificado`).
3. **Verifica contra el PDF** corriendo:
   ```powershell
   $env:NORMAS_DIR="D:\Normas_repo"
   py -3.13 -m pytest tests/test_normativa.py tests/test_normativa_pdf.py -q -p no:cacheprovider
   ```
4. **Regenera los documentos generados** (nunca editarlos a mano):
   ```powershell
   py -3.13 -m src.normativa.manifiesto --escribir --suite "<N passed, M skipped (entorno)>"
   py -3.13 -m src.indice_formulas --escribir --suite "<N passed, M skipped (entorno)>"
   ```

---

## 4. Ejecución de pruebas y mantenimiento

Todas las pruebas se ejecutan desde la raíz del repositorio (`D:\Proyecto_alcantarillas`).

| Qué quieres correr | Comando (PowerShell) | Cuándo usarlo |
|---|---|---|
| **Suite rápida** (sin `lento`) | `py -3.13 -m pytest -m "not lento" -n 4 -q -p no:cacheprovider --no-header` | Iteración diaria (~13 min) |
| **Solo tests de PDF** | `$env:NORMAS_DIR="D:\Normas_repo"; py -3.13 -m pytest -m pdf -n 4 -q -p no:cacheprovider` | Al tocar citas, fuentes o tablas |
| **Suite completa** (cierre) | `$env:NORMAS_DIR="D:\Normas_repo"; py -3.13 -m pytest -n 4 --dist loadfile -q -p no:cacheprovider --no-header` | Cierre de bloque / release (`--dist loadfile` evita repetir fixtures `scope="module"`) |
| **Tests aislados** (miden tiempo) | `py -3.13 -m pytest -m aislado -q -p no:cacheprovider --no-header` (sin `-n`) | Siempre después de una corrida con `-n`: xdist los deselecciona. El par del sello suma las dos invocaciones |
| **Suite de proceso** | `py -3.13 -m pytest proceso/tests -q -p no:cacheprovider` | Al tocar `proceso/` o el tracker |
| **Regenerar validaciones** | `py -3.13 -m tests.apoyo.validacion_integral --escribir` (y análogos `validacion_externa`, `sensibilidad`, `validacion_cabezal`, `validacion_conducto`, `validacion_hidrologica`) | Si cambia el cuerpo de los anexos |

---

## 5. Empaquetado para Windows sin Python (C3)

La receta [`empaquetado/proyecto_alcantarillas.spec`](../empaquetado/proyecto_alcantarillas.spec) empaqueta el software en una carpeta distribuible `--onedir` (`dist/proyecto_alcantarillas/`) usando `contents_directory="."` para conservar la jerarquía en disco que leen en tiempo de ejecución `M11_reporte` (`src/plantillas/*.html`, `docs/`), el catálogo de criterios (anclas en `docs/` y SHA-1 de `criterios_adoptados.py` y `src/criterios/`) y `variables_entrada.py` (AST de `src/modulos/`).

### Requisitos y compilación
1. Instalar dependencias de ejecución, GUI/PDF y empaquetado (`pyinstaller>=6.0` declarado en [`requirements-dev.txt`](../requirements-dev.txt) y en el extra `empaquetado` de [`pyproject.toml`](../pyproject.toml)):
   ```powershell
   py -3.13 -m pip install -r requirements.txt -r requirements-dev.txt ttkbootstrap==2.2.1 weasyprint==69.0
   ```
2. Compilar desde la raíz del repositorio:
   ```powershell
   py -3.13 -m PyInstaller --clean --noconfirm empaquetado/proyecto_alcantarillas.spec
   ```
   Se generan dos ejecutables compartiendo la misma carpeta `dist/proyecto_alcantarillas/`:
   - `alcantarillas_cli.exe` (línea de comandos: `--prevuelo`, corrida completa, `--json`, `--html`, `--pdf`)
   - `alcantarillas_gui.exe` (interfaz gráfica Tkinter / `ttkbootstrap`)

### Exportación a PDF y fallback a HTML
- Si en la máquina donde se compila está instalado GTK3/Pango (`C:\Program Files\GTK3-Runtime Win64\bin` o MSYS2), PyInstaller recoge las DLL nativas de WeasyPrint dentro del paquete y `alcantarillas_cli.exe --pdf` genera PDF `%PDF-1.7` sin depender del `PATH` del equipo destino.
- Si se compila o ejecuta sin las librerías nativas de WeasyPrint operativas, `M11_reporte.exportar_pdf` recurre automáticamente a la vía HTML (`--html` / exportación desde navegador con `Ctrl+P → Guardar como PDF`), sin bloquear el cálculo.
- Dentro de la GUI, los dos procesos hijo --- la exportación a PDF (`gui/exportacion_pdf.py`) y «Barrido…» (`gui/proceso_barrido.py`) --- eligen el programa con `exportacion_pdf.lanzador_de_la_cli`: desde el clon, el intérprete y `cli.py`; congelada (`sys.frozen`), `alcantarillas_cli.exe` de la misma carpeta (auditoría del 2026-11-24, hallazgo N2; antes lanzaban `alcantarillas_gui.exe` como si fuera el intérprete).

> **Receta sin verificar.** El paquete no se ha construido ni probado todavía en Windows. Hasta hacerlo (abrir la ventana, correr una plantilla de `plantillas/`, exportar el PDF y lanzar un barrido desde `alcantarillas_gui.exe`), el entregable se usa desde el clon con Python, como dice el `README.md`, y el ejecutable no se ofrece al usuario.
