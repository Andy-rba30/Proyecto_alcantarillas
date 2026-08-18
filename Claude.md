# Reglas del proyecto

## Fuente de verdad
- Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v7.md. Toda cita de
  numeral se verifica contra ese archivo. Nunca se inventa un numeral.
- Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta.
- **Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes.**
  Crea una entrada en criterios_adoptados.py con valor=None, etiqueta [A] y
  justificación de por qué hace falta, y detén el cálculo con excepción.
  Rellenar un vacío en silencio es el peor error posible en este proyecto.

## Taxonomía de etiquetas (cinco, no cuatro)
Todo valor de proyecto lleva una de estas cinco. Se leen de más determinado a
más elegido, y ese es el orden en que M11 las imprime:

- **[N]** Exigencia normativa peruana vigente, numeral verificado. El mismo
  número en cualquier obra del país. Vive en constantes_normativas.py.
- **[N→]** Valor normativo aplicado POR ANALOGÍA. Requiere declaración expresa.
- **[S]** **Dato de sitio.** Obtenido mediante un procedimiento normativo real
  (mapa, ensayo, medición de campo) aplicado a las coordenadas o condiciones de
  ESTE proyecto. No es elección del proyectista ni analogía: es un hecho
  determinado, no portable a otro proyecto. **En vez de sensibilidad declara
  trazabilidad obligatoria**: el procedimiento exacto, la fuente, y si el dato
  aplica a todo el corredor o varía punto a punto.
- **[C]** Vacío normativo cubierto con fuente técnica reconocida (FHWA, AASHTO).
- **[A]** Sin norma ni fuente única. Adopción declarada + sensibilidad.

Regla para separar [N] de [S]: si el valor cambia al mover la obra de sitio
pero NO al cambiar de proyectista, es [S]. "La Unión está en Zona 4" cita
E.030 correctamente y aun así no es [N]. Regla para separar [S] de [A]: un [A]
se defiende con un rango de sensibilidad porque hubo elección; un [S] no tiene
rango que elegir y se defiende con la trazabilidad de la lectura.

Dónde vive cada [S]: si vale para todo el corredor, en datos_sitio.py; si
varía punto a punto, es columna del CSV (NF_profundidad_m, cbr_subrasante). Un
[S] pendiente de ensayo que además comparte tablero con los criterios puede
quedar en criterios_adoptados.py con el campo `trazabilidad`.

Tabla y elección se separan siempre: los valores de una tabla normativa son
[N] y viven en constantes_normativas.py (F_PGA_TABLA, FACTOR_MURO_TABLA); cuál
fila aplica a esta obra es [A] y vive en criterios_adoptados.py ('F_pga',
'factor_muro_eleccion').

## Arquitectura
- Ningún módulo declara valores no normativos. Todo literal numérico fuera de
  constantes_normativas.py (solo [N]), criterios_adoptados.py ([N→],[C],[A] y
  los [S] pendientes de ensayo) o datos_sitio.py (solo [S] de corredor) es un
  defecto y se rechaza en revisión. Excepciones permitidas: 0, 1, 2,
  índices, y constantes matemáticas puras (pi). Dos archivos más quedan
  exentos por no contener valores de proyecto: tolerancias.py (precisión
  numérica: cambiarla no mueve ninguna magnitud física) y dominios.py (rango
  físico posible de un dato de entrada: no entra en ninguna fórmula). Regla
  para saber si un número va en uno de esos dos: si cambiarlo puede alterar un
  resultado del cálculo, no va ahí. datos_sitio.py está exento por la razón
  CONTRARIA: sus números sí son valores de proyecto, y de los más pesados —
  está aparte porque no son constantes universales, no porque no importen.
- Un literal que es parte de una fórmula transcrita de la hoja de ruta —el 8 de
  A = (D²/8)(θ − sen θ), el exponente 2/3 de Manning— se deja en el módulo
  marcado con `# literal-ok: <razón>`. La marca lo declara y lo hace visible en
  revisión; sin marca, tests/test_sin_literales.py lo rechaza.
- Los tipos que fluyen entre módulos están en modelos.py. Ningún módulo define
  sus propios dicts ad-hoc para lo que ya existe ahí.
- criterios_adoptados.valor(clave) y datos_sitio.valor(clave) con valor None
  lanzan CriterioPendienteError. Nunca se sustituye por un default silencioso.
- Cada invocación de un criterio o de un dato de sitio se registra, para que
  M11 imprima solo los usados.
- Cada verificación devuelve un objeto Verificacion(cumple, numeral, valor,
  criterio_aplicado), nunca un bool desnudo.

## Unidades
- **Todo el código opera en SI: metros, m³/s, m/s, Pa, kN.** Ninguna función
  acepta ni devuelve pulgadas, pies ni kg/cm².
- Las constantes empíricas dependientes de unidades llevan sufijo _SI en su
  nombre y un comentario con el valor imperial equivalente y por qué NO se usa.
- La conversión a unidades de presentación (pulgadas, kg/cm²) ocurre solo en
  la capa de reporte, nunca en el cálculo.

## Excepciones (taxonomía)
Todas descienden de ErrorProyecto, definidas en modelos.py, para que la GUI
distinga un problema del expediente de un fallo del programa con un solo except.
- CriterioPendienteError: criterio [A] sin valor. La GUI la muestra como
  "falta declarar: <clave>", no como error del programa.
- DisenoNoFactibleError: ninguna combinación material/diámetro cumple.
  Debe llevar el motivo y, si aplica, el delta de rasante requerido.
- DatoFaltanteError: falta un dato de entrada del CSV. Falta la **columna**
  entera, o la celda obligatoria viene vacía. Lleva el nombre de la columna.
- DatoInvalidoError: el dato **está** pero no puede ser: no es del tipo
  esperado, cae fuera del rango físico de dominios.py, o contradice a otro
  dato de su misma fila (§1.5). Hermana de DatoFaltanteError y no la misma:
  "falta la columna cbr_subrasante" y "el CBR dice 250 %" son dos problemas
  distintos del expediente y se corrigen de forma distinta. La regla para
  elegir: si el revisor tiene que **añadir** algo es Faltante, si tiene que
  **corregir** algo es Invalido.
No usar Exception genérica en lógica de negocio. Un fallo de E/S (archivo
inexistente) no es del expediente y sale como FileNotFoundError, fuera de
ErrorProyecto.

## Estilo
- Python 3.11+. Dependencias: numpy, scipy (brentq), pandas, pytest,
  ttkbootstrap, jinja2. Cualquier dependencia adicional se consulta antes.
- No comparar floats con ==. Tolerancias explícitas y nombradas.
- Identificadores en español (coherente con Tc.py), docstrings en español.
- Cada función de cálculo lleva en su docstring el numeral que la sustenta.

## GUI
- Reutilizar el patrón de legacy/Tc.py:
  Tkinter + ttkbootstrap, Notebook por pestañas, MarcoScroll, Tooltip, campo
  validable, plantilla con marcadores %%, sesión en JSON, export HTML/PDF/CSV.
  Leer esos archivos antes de escribir GUI. No reinventar los componentes.

## Tests
- pytest en tests/. Mínimo un test por módulo.
- Todo módulo de cálculo se contrasta contra tests/fixtures/casos_patron.py.
- Al cerrar cada módulo: commit con el nombre del módulo en el mensaje.