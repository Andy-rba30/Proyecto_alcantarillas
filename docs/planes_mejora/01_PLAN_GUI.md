# Plan G — GUI: familias visibles, anticipo de bloqueos y la traza de cada número

**Sustituye a:** `01_PLAN_UI_ENTRADAS.md`.
**Qué cambió en la revisión:** la GUI real ya tiene la anotación por familia
(S21), los filtros de estado y de alcance con recuento honesto, y la ayuda
derivada del censo (S22). Este plan se queda con lo que de verdad falta:
agrupar (no solo anotar), el filtro por fase, el anticipo pre-corrida
(informativo, nunca bloqueando el botón), la traza `PasoDeMemoria` en la
pestaña 3 — la mejora de mayor valor de toda la serie — y la ayuda de
conceptos. Todo lo que la GUI muestre se **deriva** del censo o del informe;
ninguna lista se escribe a mano (es el patrón que S21/S22 dejaron asentado y
testeado).

**Reglas que gobiernan las cinco sesiones:**

- Los componentes se leen de `gui/componentes.py` (`Tooltip`, `MarcoScroll`,
  `CampoValidable`, `BotonAccion` — que exige `motivo` cuando está apagado —,
  `BotonAyuda`). `legacy/Tc.py` es antecedente, no plantilla.
- La GUI no calcula ni decide: revela lo que el expediente declaró. Cualquier
  aritmética sobre magnitudes en `gui/` es defecto (misma regla que M11).
- Todo cambio de contrato se refleja en `tests/test_gui_contrato.py` (54 tests
  por AST, sin importar tkinter). Los tests de ventana real corren con
  `apt-get install -y python3-tk` + `xvfb-run` (documentado en `CLAUDE.md`).
- La suite mantiene el invariante `passed + skipped = collected`.

---

## G1 · Pestaña 1 agrupada por familia + limpieza de lenguaje

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. GUI Tkinter +
ttkbootstrap; los componentes vivos están en gui/componentes.py (NO en
legacy/Tc.py). La pestaña «1. Datos de entrada» (gui/app.py,
_construir_tab_datos) muestra hoy los cinco datos declarados de
cli.CAMPOS_EXTERNOS en una lista plana; desde S21 cada campo lleva una
anotación «no aplica: este CSV no trae puntos de Familia X»
(_pintar_no_aplica, alimentada por cli.familias_que_usan y
cli.familias_del_csv). Esa maquinaria derivada ya existe y se reutiliza; lo
que falta es que la pantalla la muestre AGRUPADA.

Tarea 1 — agrupar por familia, derivado:
- Reorganiza el bloque de datos declarados en secciones: «Comunes a todas las
  familias», y una sección por familia que tenga campos propios. La
  pertenencia se DERIVA de cli.FAMILIAS_QUE_USAN: un dato sin fila declarada
  lo usan las tres familias (esa semántica ya está fijada por
  tests/test_familias_del_csv.py) y va en «Comunes»; un dato con fila va en
  la sección de sus familias. Ninguna asignación campo→sección se escribe a
  mano en gui/.
- El encabezado de cada sección de familia muestra el conteo de puntos de esa
  familia en el CSV cargado (reutiliza _releer_familias / familias_del_csv).
  Sin CSV cargado, muestra «— puntos» y la sección queda visible.
- Conserva el comportamiento actual de ANOTAR sin deshabilitar (es decisión
  declarada en el docstring de _pintar_no_aplica; no la conviertas en
  deshabilitado). Una familia sin puntos en el CSV colapsa su sección o la
  atenúa, con el motivo visible — elige lo que menos código nuevo exija.

Tarea 2 — limpieza de lenguaje en la misma pestaña:
- Ninguna etiqueta visible contiene un nombre de bandera CLI (--luz, --tw,
  --alcance…) ni un código de módulo (M0, M11). Esa información no se
  pierde: pasa al texto del BotonAyuda/Tooltip del campo («equivale a la
  bandera --luz de la línea de comandos»).
- Revisa el título de la ventana y los rótulos de sección: si citan módulos
  internos («M0 a M10») o flags, reformúlalos en lenguaje de proyectista.
  Los códigos de módulo pueden ir a la barra de estado.
- Tildes correctas y unidad SI visible en cada campo numérico.

Tarea 3 — tests:
- Extiende tests/test_gui_contrato.py (patrón AST existente): (a) la
  asignación campo→sección se lee de cli.FAMILIAS_QUE_USAN y no de un dict
  local en gui/; (b) ninguna cadena visible de la pestaña 1 contiene un
  patrón de bandera CLI (regex sobre las cadenas del AST, con lista blanca
  para los textos de ayuda). Si algún test actual fija cadenas que cambiaste
  legítimamente, actualízalo diciendo en el commit por qué.
- Si el entorno lo permite (python3-tk + xvfb-run, ver CLAUDE.md sección de
  tests), añade o extiende un test de ventana real que construya la pestaña
  y verifique que las secciones existen. Si no se puede, dilo en el cierre.

Prohibido: tocar valores de cálculo, cli.py (salvo si necesitas EXPONER una
lista ya existente — no crear datos nuevos), criterios_adoptados.py.

Cierre (ritual de CLAUDE.md): suite completa en verde; commit
«GUI(G1): pestaña 1 agrupada por familia, derivada del censo, y limpieza de
lenguaje»; entrega en origin/main; reporta el conteo como PAR
passed+skipped=collected leído desde origin/main, diciendo con qué entorno
(PyMuPDF sí/no, Tk sí/no).
```

### Aceptación

- [ ] Las secciones se derivan de `cli.FAMILIAS_QUE_USAN` (mover una fila allí
      mueve el campo de sección, y un test lo comprueba).
- [ ] Conteo de puntos por familia en el encabezado de cada sección.
- [ ] Ninguna bandera CLI ni código de módulo en etiquetas visibles.
- [ ] Suite en verde con el par reportado desde `origin/main`.

---

## G2 · Filtro por fase en la pestaña 2 — y por qué NO por familia

La pestaña 2 ya tiene tres filtros (estado, ámbito derivado del alcance,
búsqueda) y el recuento honesto. Falta **fase**, que es el orden mental del
proyectista, y es derivable: `variables_entrada.variable(clave).fase` existe
para las 69 claves.

**Familia se difiere a propósito**, y conviene dejarlo escrito: no existe hoy
ninguna fuente derivable de «qué criterios aplica cada familia» (los criterios
no declaran familia; la única bifurcación por familia del pipeline es VC1/V5 y
la rama de sección rectangular). Una lista a mano criterio→familia sería
exactamente la clase de clasificación escrita que `Criterio.nivel` vino a
erradicar — si algún día se quiere, se hace como se hizo `nivel`: **midiendo
corridas por familia** (el molde es `tests/test_nivel_medido.py`).

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. La pestaña
«2. Criterios» de gui/app.py tiene tres filtros (FILTROS_DE_ESTADO,
FILTROS_DE_AMBITO derivado de ca.criterios_del_alcance y
M11.criterios_bloqueantes, y búsqueda) y el recuento honesto de
_pintar_recuento («33 de 69 pendientes | el filtro muestra N y esconde M»).
Antes de tocar nada, lee _refiltrar, _pasa_el_filtro y _pintar_recuento para
respetar su composición.

Tarea: añade un cuarto filtro «Fase», derivado — las opciones del combo se
construyen desde {variables_entrada.variable(clave).fase for clave in
ca.CRITERIOS}, nunca de una lista escrita en gui/. Se compone con los filtros
existentes (Y lógico), y el recuento sigue contando los pendientes sobre los
69 del archivo entero y diciendo cuántas filas esconde el filtro combinado.

NO añadas filtro por familia. Si te parece que falta, la razón de diferirlo
está en docs/planes_mejora/01_PLAN_GUI.md §G2 (si el archivo existe en el
repo) y se resume así: no hay fuente derivable criterio→familia y una lista a
mano está prohibida por el patrón del proyecto; el camino correcto sería
medirlo con corridas, como test_nivel_medido, y es otra sesión.

Tests: extiende tests/test_gui_contrato.py con el contrato del filtro nuevo
(las opciones salen de variables_entrada, el recuento no cambia de base).

Cierre: suite en verde; commit «GUI(G2): filtro por fase en la pestaña 2,
derivado del censo»; entrega en origin/main; conteo como par
passed+skipped=collected desde origin/main, con el entorno.
```

---

## G3 · Anticipo de bloqueos antes de correr (informativo)

**Corrección importante sobre tu plan:** el panel existe, pero **no deshabilita
el botón de correr**. El anticipo es una estimación (la invocación real de un
criterio depende de la ruta que tome cada punto), la regla de la casa es que
ninguna estimación gobierna un filtro, y el pipeline ya degrada bien: cada
falta se vuelve `Bloqueo` por etapa y por punto, y el tablero de la pestaña 4
(`criterios_bloqueantes`, seis columnas) es la verdad post-corrida. El
anticipo ahorra el ciclo «correr para descubrir», nada más.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. Hoy los bloqueos solo
se conocen DESPUÉS de ejecutar: M11_reporte.criterios_bloqueantes se puebla
post-corrida y alimenta _llenar_resumen (pestaña 4). El filtro
AMBITO_BLOQUEANTES de la pestaña 2 está deshabilitado hasta que haya corrida,
con MOTIVO_SIN_CORRIDA_FILTRO. Ese diseño se conserva: es la verdad medida.

Tarea: añade a la pestaña 1, junto al botón EJECUTAR, un panel «Anticipo
antes de correr» que se refresca al cargar CSV / cambiar alcance, con TRES
bloques, todos DERIVADOS:

1. Criterios vacíos alcanzables: intersección de
   ca.criterios_del_alcance(alcance) con los criterios sin valor no
   opcionales (ca.criterios_sin_valor() o equivalente — verifica el nombre
   real). Muestra clave y concepto; clic lleva a la fila en la pestaña 2
   (reutiliza la selección existente del árbol).
2. Columnas del CSV: contrasta la cabecera del CSV cargado contra
   M0_carga.COLUMNAS y M0_carga.VACIOS_ADMITIDOS (con sus familias) SIN
   ejecutar el pipeline — solo lectura de cabecera y conteo de celdas
   vacías por columna. Reutiliza lo que M0 ya exponga; si necesitas una
   función de solo-cabecera, va en src/ (por ejemplo en M0_carga), no en
   gui/, y con test propio.
3. Diferimientos del alcance: a --alcance perfil, la lista REAL de lo que se
   difiere (V5, V8, y los módulos de cli.MODULOS_DIFERIDOS_POR_ALCANCE),
   leída de cli, no escrita a mano.

Reglas duras:
- El panel se titula «Anticipo» y lleva una línea fija: «Estimación derivada
  del alcance; la lista definitiva la da la corrida (pestaña 4)». La palabra
  estimación no es opcional: el proyecto distingue estimaciones de medidas y
  esta es una estimación.
- El botón EJECUTAR nunca se deshabilita por el anticipo. Nada de «correr de
  todos modos»: correr siempre se puede; el pipeline convierte faltas en
  Bloqueos declarados.
- gui/ no parsea el CSV con lógica propia: toda lectura vive en src/ y la
  GUI la consume.

Tests: contrato AST (el panel existe, sus tres bloques leen de los símbolos
citados, el botón no depende del anticipo) + test unitario de la función de
anticipo en src/ (CSV de fixtures tests/ejemplo_puntos*.csv).

Cierre: suite en verde; commit «GUI(G3): anticipo de bloqueos pre-corrida,
derivado e informativo»; entrega en origin/main; conteo como par desde
origin/main, con el entorno.
```

### Aceptación

- [ ] Tres bloques derivados, cero listas a mano, rotulado como estimación.
- [ ] EJECUTAR siempre habilitado; el tablero post-corrida sigue siendo la verdad.
- [ ] La función de anticipo vive en `src/` con test propio.

---

## G4 · «¿De dónde sale este número?» — la traza en la pestaña 3

La mejora de mayor valor de la serie, y la más barata de lo que tu plan
suponía: **el dato ya existe**. Cada función de cálculo emite `PasoDeMemoria`
(qué, por qué con `Fundamento`, fórmula con `formula_cita_id`, sustitución con
procedencia de cada valor, umbral con carácter, veredicto) y M11 los recolecta
por corrida. Solo la memoria HTML/PDF los muestra; la pestaña 3 de la GUI
enseña verificaciones y bloqueos, pero no la cadena de procedencia.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. PasoDeMemoria está en
src/modelos.py; M11_reporte recolecta «todos los PasoDeMemoria que ESTA
corrida emitió» y declara HuecoDeVerificacion para las verificaciones que no
emiten paso (V4b, V5, V6, V8, V9 — censadas en normativa.fundamentos
SIN_FUNDAMENTO). La pestaña «3. Resultados por punto» (_construir_tab_puntos)
muestra verificaciones y bloqueos al seleccionar un punto. El patrón
arquitectónico a imitar es el de la ventana normativa: src/ produce el
contenido (src/ventana_normativa.py), gui/ solo pinta
(gui/ventana_normativa.py).

Tarea: al seleccionar un punto en la pestaña 3, ofrecer «¿De dónde sale este
número?»: un detalle (panel o Toplevel, elige lo más simple con
gui/componentes.py) que muestre los PasoDeMemoria de ese punto en el orden en
que M11 los imprime, con, por paso:
  - qué se calculó y POR QUÉ (el Fundamento con su verbo — obliga /
    recomienda / permite / define — tal como lo sostiene el carácter de su
    cita);
  - la fórmula con su cita (numeral + página);
  - la sustitución con la PROCEDENCIA de cada valor (etiqueta [N]/[A]/…,
    criterio o dato de sitio del que sale);
  - resultado, umbral con su carácter, y veredicto con margen;
  - las discrepancias que tocan sus citas, si las hay (la vista
    discrepancias_que_tocan del registro, que M11 ya consume).
Para las verificaciones sin paso, muestra el HuecoDeVerificacion declarado —
nunca una fila en blanco ni un texto inventado.

Reglas duras:
- La capa de contenido va en src/ (módulo nuevo pequeño o extensión donde
  corresponda), con el mismo contrato que M11: elige textos y orden, NO hace
  aritmética sobre magnitudes. gui/ pinta. Añade la guardia de AST para el
  módulo de contenido nuevo, calcada de la que ya barre M11.
- Se muestran los tres registros SEPARADOS donde aplique: lo que la fuente
  dice (cita), lo que el proyecto lee (interpretación) y lo que el proyecto
  hace. Pegarlos es NOR-HID-04; la memoria HTML ya los separa con clases
  CSS — respeta la misma división con estilos/encabezados de la GUI.
- Conversión a unidades de presentación: solo en esta capa de reporte, igual
  que en M11; el paso guarda SI.

Tests: unitarios de la capa de contenido en src/ (con una corrida sobre
tests/ejemplo_puntos.csv), guardia AST de no-aritmética, y contrato en
test_gui_contrato.py de que la pestaña 3 consume esa capa.

Cierre: suite en verde; commit «GUI(G4): traza de procedencia por punto desde
PasoDeMemoria»; entrega en origin/main; conteo como par desde origin/main,
con el entorno.
```

### Aceptación

- [ ] Cada número trazable hasta cita/criterio/dato de sitio sin abrir la memoria HTML.
- [ ] Cero aritmética en la capa nueva (guardia AST).
- [ ] Huecos declarados visibles como huecos.

---

## G5 · Ayuda de conceptos + prueba con una persona real

La ayuda de **entradas** ya existe y es derivada (dos pestañas: CSV y JSON).
Falta la de **conceptos**: qué es cada familia, qué significan las cinco
etiquetas, qué es bloqueante / opcional / vacío verificado / diferido, y el
glosario de símbolos y unidades. A diferencia de las listas, los párrafos
conceptuales son estables y pueden escribirse a mano; **las enumeraciones que
los acompañan se derivan** (familias de `modelos.Familia`, etiquetas y sus
archivos de residencia de la constitución, verificaciones de M5, unidades del
censo).

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md.
gui/ayuda_entrada.py::VentanaAyudaEntrada es una Toplevel con notebook de dos
pestañas (CSV / JSON), cuyo contenido produce src/ayuda_entrada.py derivándolo
del censo; tests/test_ayuda_entrada.py comprueba que una columna nueva aparece
sola. Sigue exactamente ese patrón.

Tarea: añade una tercera pestaña «Conceptos» a la ventana de ayuda:
1. Las tres familias: rótulo y descripción DERIVADOS de modelos.Familia y su
   documentación; de dónde sale el Q de cada una.
2. Las cinco etiquetas [N] [N→] [S] [C] [A] en lenguaje llano, cada una con
   el archivo donde vive esa clase de valor. Los párrafos explicativos son
   texto estable escrito a mano (declarado así en el docstring); la LISTA de
   etiquetas y archivos se deriva de donde el código ya la tenga — si no hay
   fuente única derivable, decláralo y deja la lista junto a una guardia que
   falle si aparece una etiqueta nueva sin fila de ayuda.
3. Estados de un criterio (pendiente / declarado en corrida / pisado /
   resuelto en archivo / vacío verificado / diferido): derivados de los
   estados reales de _estado_criterio y de los conceptos del pipeline, no
   inventados.
4. Glosario de símbolos y unidades: derivado del censo de variables_entrada
   (concepto + unidad).
La capa de contenido va en src/ayuda_entrada.py (o hermano), con tests del
mismo estilo que los existentes: añade un estado o una variable y la ayuda lo
recoge sin tocar gui/.

Tarea final — prueba de usabilidad real (manual, no automatizable): deja en
el resumen de cierre un guion de 5 pasos para que una persona que no conoce
el proyecto cargue tests/ejemplo_puntos.csv, lea el anticipo, corra a
--alcance perfil y encuentre de dónde sale un número. Esa prueba la ejecuta
el dueño del proyecto, no vos.

Cierre: suite en verde; commit «GUI(G5): pestaña de conceptos derivada en la
ayuda»; entrega en origin/main; conteo como par desde origin/main, con el
entorno.
```

---

## Fuera de alcance del plan G (igual que en tu plan, más dos)

- Cambiar el motor de GUI (sigue Tkinter + ttkbootstrap) y el formato del CSV.
- Modo web o multiusuario.
- Cualquier cambio en valores de cálculo.
- **Rehacer la ventana normativa** (`gui/ventana_normativa.py` + su capa de
  contenido): es el componente mejor resuelto de la GUI, con 47 tests.
- **Deshabilitar la corrida por estimaciones** — ver G3.
