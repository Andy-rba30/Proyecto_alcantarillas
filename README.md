# Expediente de alcantarillas — M0 a M11

Calculador de alcantarillas de cruce para carretera, con memoria de cálculo
auditable. La fuente normativa única es `docs/hoja_de_ruta_alcantarillas_v8.md`
y las reglas del proyecto están en `CLAUDE.md`, que es su constitución: si algo
de este archivo y algo de aquél discrepan, gana `CLAUDE.md`.

Este README cubre **cómo instalarlo y ponerlo a correr**. No documenta el
cálculo: eso lo hace la memoria que el propio programa emite.

## Requisitos

Python **3.11 o superior**.

```
pip install -r requirements.txt
```

Eso es todo lo que hace falta para **calcular** una alcantarilla y emitir la
memoria en HTML. `requirements-dev.txt` es aparte y solo hace falta para
**comprobar** que lo calculado se apoya en lo que las normas dicen (lee su
encabezado: explica por qué están separados).

## Cómo se corre

```
python cli.py <csv de puntos> --alcance perfil|expediente [--html salida.html] [--pdf salida.pdf]
python -m gui.app          # la ventana
```

De un CSV nuevo a las tres familias dimensionadas a nivel de perfil, paso a
paso y con comandos que la suite ejecuta: `docs/guia_perfil.md`.

## Exportar a PDF desde la ventana: en un proceso aparte

Desde EXT-8 el botón «Exportar memoria (PDF)» no escribe el PDF en el hilo de la
ventana: lanza `python cli.py --sesion <sesión> --pdf <destino> --progreso` en un
subproceso con la sesión serializada de la ventana (proyecto, CSV, datos externos,
alcance y criterios declarados con su procedencia). La ventana sigue viva, el
progreso se lee de las líneas `progreso: hecho/total etapa` que la CLI imprime, y
«Cancelar PDF» termina el proceso sin dejar un archivo a medias. Medido antes de
EXT-8: 11 s y 287 MB para 4 puntos, 69 s y 1.3 GB para 40, 360 s y 5.7 GB para 200;
por encima de 40 puntos la ventana ofrece la vía del navegador (HTML + Ctrl+P). Las
dos banderas nuevas valen también a mano: `--sesion` repone una sesión guardada y
`--progreso` imprime el avance.

## Otra obra sobre el mismo despliegue: `--datos-sitio` y la sesión (formato 3)

Los datos de sitio **[S]** del corredor de la obra del repositorio (el PGA del
mapa, el corredor mismo) viven en `src/datos_sitio.py` con su trazabilidad, y
**no se editan** para calcular otra obra (EXT-10, EXT-V-01). Otra obra declara
los suyos **por sesión**, con trazabilidad y fecha, y por la misma guardia que
el archivo:

```
python cli.py <csv> --alcance expediente --datos-sitio sitio.json --proyecto "Obra B"
```

```json
{"PGA_roca_B": {"valor": 0.30, "trazabilidad": "lectura del mapa A3 sobre ...", "fecha": "2026-09-21"},
 "corredor_del_proyecto": {"valor": "Obra B, km 10-12", "trazabilidad": "...", "fecha": "2026-09-21"}}
```

En la ventana es el campo «JSON de datos de sitio» de la pestaña 1, y el botón
«Nuevo proyecto» abre una obra vacía (una sesión nueva, nunca un archivo
vaciado). La sesión guardada es desde EXT-10 el **formato 3**: `id`, la ruta del
`sitio.json`, el bloque `sitio` con los [S] declarados, `csv_sha1` y las
corridas con su `informe_json` embebido; una sesión v1 o v2 se migra al abrirla
y la ventana o la CLI dicen qué completaron. La memoria y el JSON imprimen **de
qué archivo salió cada [S]** («Origen») y advierten si el nombre del proyecto
no coincide con el corredor de los datos de sitio; con `--sesion`, la CLI dice
además si su corrida **reproduce** la guardada en la sesión o **difiere**.

## Exportar a PDF: WeasyPrint necesita librerías nativas

**En Linux y macOS normalmente no hay nada que hacer.** En **Windows sí**, y
conviene saber por qué antes de perder tiempo: `pip install weasyprint` instala
el paquete de Python y **no** instala las librerías nativas de las que depende
—las de GTK: GObject, Pango, Cairo, GDK-PixBuf—. Sin ellas el paquete está
instalado y no carga.

### Qué pasa si faltan

**La exportación no se pierde.** El programa escribe la memoria en HTML junto
al destino que elijas y la abre en el navegador para guardarla con
`Ctrl+P → Guardar como PDF`. La plantilla ya viene configurada en A4 y trae su
CSS de impresión, de modo que el PDF que sale por esa vía es equivalente. Es
una **vía alternativa, no un fallo**, y el mensaje que ves lo dice con esas
palabras.

### Cómo instalarlas

Aquí **no se transcribe una lista de DLLs**, y es deliberado: la lista cambia
con la versión de WeasyPrint y con la de GTK, y una lista copiada envejece sin
que nadie se entere —que es exactamente el defecto que este proyecto persigue—.
**El mensaje de error nombra la biblioteca concreta que falta en tu máquina**,
porque el programa guarda la excepción real del import en vez de tirarla. Ésa
es la fuente de verdad; empezá por leerla:

> `weasyprint SI esta instalado y no pudo cargarse: […] Lo que dijo el sistema
> al cargarlo: OSError: cannot load library 'gobject-2.0-0': …`

La vía que la propia documentación de WeasyPrint recomienda en Windows es
**MSYS2**:

1. Instalar MSYS2 desde <https://www.msys2.org/>.
2. En su terminal: `pacman -S mingw-w64-x86_64-pango`. Pango arrastra
   GObject, Cairo y GDK-PixBuf, que son las demás.
3. Añadir `C:\msys64\mingw64\bin` al `PATH` **del usuario**, y abrir una
   consola nueva (el `PATH` no se refresca en las ya abiertas).
4. Comprobar: `python -c "import weasyprint; print(weasyprint.__version__)"`.
   Si imprime la versión, el botón «Exportar memoria (PDF)» ya escribe el PDF
   directo.

Si el paso 4 sigue fallando, **volvé a leer el mensaje**: va a nombrar la
siguiente biblioteca que falte, y el paquete de `pacman` que la trae se busca
por ese nombre. La documentación al día está en
<https://doc.courtbouillon.org/weasyprint/stable/first_steps.html>.

### Por qué no se cambió de motor

Se midió, sobre una memoria real de 134 páginas y 26 tablas. `PyMuPDF.Story`
—que no necesita librerías nativas— rompe las tablas: 218 páginas y celdas
apiladas una palabra por línea. `xhtml2pdf` se acerca mucho en conteo de
páginas y texto, pero ignora `border-collapse`, `float`, `page-break-inside` y
el anidamiento, y con eso aplana en tarjetas del mismo peso visual lo que la
memoria imprime como bloques anidados. Ese anidamiento **no es estilo**: es
como se separan en pantalla lo que la fuente **dice**, lo que el proyecto
**lee** y lo que el proyecto **hace**, que `CLAUDE.md` exige mantener
separados. Cambiar de motor abarataría la instalación degradando el
entregable.

## Tests

```
pip install -r requirements-dev.txt
python -m pytest -q
```

El conteo es un **par**, no un número, y depende de tres ejes independientes:
si está PyMuPDF, si hay con qué levantar una ventana Tk, y si hay un intérprete
POSIX (`sh` o `bash`) en el `PATH`. Los pares medidos, con el árbol de cada
uno, están en `docs/ruta_familia_c.md`, §16.18. Lo que no depende del entorno
es la suma: si `passed + skipped` deja de dar `collected`, hay un fallo o un
error de recolección, no una dependencia ausente.
