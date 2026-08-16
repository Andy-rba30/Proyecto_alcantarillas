# Reglas del proyecto

## Fuente de verdad
- Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v7.md. Toda cita de
  numeral se verifica contra ese archivo. Nunca se inventa un numeral.
- Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta.
- **Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes.**
  Crea una entrada en criterios_adoptados.py con valor=None, etiqueta [A] y
  justificación de por qué hace falta, y detén el cálculo con excepción.
  Rellenar un vacío en silencio es el peor error posible en este proyecto.

## Arquitectura
- Ningún módulo declara valores no normativos. Todo literal numérico fuera de
  constantes_normativas.py (solo [N]) o criterios_adoptados.py ([N→],[C],[A])
  es un defecto y se rechaza en revisión. Excepciones permitidas: 0, 1, 2,
  índices, y constantes matemáticas puras (pi).
- Los tipos que fluyen entre módulos están en modelos.py. Ningún módulo define
  sus propios dicts ad-hoc para lo que ya existe ahí.
- criterios_adoptados.valor(clave) con valor None lanza CriterioPendienteError.
  Nunca se sustituye por un default silencioso.
- Cada invocación de un criterio se registra, para que M11 imprima solo los usados.
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
- CriterioPendienteError: criterio [A] sin valor. La GUI la muestra como
  "falta declarar: <clave>", no como error del programa.
- DisenoNoFactibleError: ninguna combinación material/diámetro cumple.
  Debe llevar el motivo y, si aplica, el delta de rasante requerido.
- DatoFaltanteError: falta un dato de entrada del CSV.
No usar Exception genérica en lógica de negocio.

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