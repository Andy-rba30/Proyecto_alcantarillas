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
