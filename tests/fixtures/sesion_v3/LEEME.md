# DATOS DE PRUEBA, NO DEL PROYECTO

`sesion_v3_partida.json` es una sesión de **formato 3** escrita por «Guardar sesion» de la
ventana DE VERDAD con el código de partida de UI-1 (`bcd2d1a`, antes de que
`src/sesion.py` pasara al formato 4): el CSV de ejemplo, el JSON de datos externos de la
línea base, el `sitio.json` de la corrida de referencia `expediente_cabezal` en el campo de
la pestaña 1, un criterio declarado con su procedencia (`phi_relleno_trasdos`) y la corrida
embebida con su `informe_json`. **Ningún valor es del proyecto**: son las entradas de
prueba de `tests/`, y el nombre del proyecto lo dice.

Sirve para una sola cosa: comprobar que una sesión guardada antes de UI-1 se sigue
abriendo igual —por la ventana y por `cli.py --sesion`— y que al guardarla se reescribe en
el formato actual (`tests/test_ui1_hidrologia_ventana.py`). **No se regenera**: es un
archivo de la versión anterior del programa, y regenerarlo con el código nuevo lo
convertiría en una sesión de formato 4 que ya no prueba nada. Las rutas son relativas a la
raíz del repositorio, como las teclearía quien trabaja desde ella.
