# Manifiesto: dato de proyecto disfrazado de constante `[N]` — **CERRADO**

Auditoría de clasificación sobre `src/constantes_normativas.py`,
`src/criterios_adoptados.py` y los docstrings de `src/modulos/*.py`, buscando
un defecto **distinto** al de `docs/manifiesto_citas.md`: no si el numeral
existe, sino si el valor que lo cita es una constante universal o un dato de
este expediente.

> **Estado: las cuatro filas del diagnóstico están corregidas en el código, y
> la duda de taxonomía que las bloqueaba se resolvió creando la quinta
> etiqueta `[S]`.** Este documento se conserva como el registro de qué se
> encontró, qué se decidió y por qué. Lo que era una tabla de hallazgos ahora
> es una tabla de resoluciones.

## El criterio de diagnóstico

> Para cada variable etiquetada `[N]`: si este software se usara para diseñar
> una alcantarilla en **otra vía, otra provincia, otro suelo**, ¿el valor
> seguiría siendo el mismo número?

Si la respuesta es **no** —porque el número depende de dónde está o qué
características tiene ESTE proyecto—, la variable está mal clasificada, aunque
el numeral que cita sea correcto y verificable. El caso que sirvió de patrón
(`ZONA_SISMICA_LA_UNION`, `Z_E030`): ambas citan E.030 correctamente, pero "La
Unión está en Zona 4" es un hecho de ubicación de este expediente, no una
constante universal.

---

## Lo que faltaba: la quinta etiqueta

El diagnóstico se detuvo en tres filas marcadas `DUDA`, y todas por la misma
razón: **el vocabulario de cuatro etiquetas no tenía casilla para un hecho de
sitio.** `N->` no aplicaba (no se presta una regla pensada para otra cosa),
`C` no aplicaba (la fuente ES peruana y ES la que rige), y `A` no aplicaba del
todo (nadie "adoptó" el nivel freático: se **midió**).

La decisión, que el diagnóstico dejó expresamente al equipo del proyecto, fue
**crear la quinta etiqueta** en vez de forzar los tres casos dentro de `[A]`:

    [S]  Dato de sitio. Obtenido mediante un procedimiento normativo real
         (mapa, ensayo, medicion de campo) aplicado a las coordenadas o
         condiciones de ESTE proyecto. No es eleccion del proyectista ni
         analogia: es un hecho determinado, no portable a otro proyecto. En
         vez de sensibilidad declara TRAZABILIDAD obligatoria: el
         procedimiento exacto, la fuente, y si el dato aplica a todo el
         corredor o varia punto a punto.

**Por qué no se forzaron dentro de `[A]`.** `[A]` significa "adopción
declarada, con análisis de sensibilidad obligatorio". Un rango de sensibilidad
responde a "¿y si se hubiera elegido el otro extremo?", y esa pregunta no
tiene sentido sobre un hecho: el nivel freático no está a 1.4 m *por
decisión*, y ofrecer un rango alternativo insinuaría que sí. Al revés, la
pregunta que un revisor sí necesita hacerle a un `[S]` —"¿dónde exactamente se
leyó esto?"— no tenía campo donde vivir. La quinta etiqueta cambia
`sensibilidad` por `trazabilidad` justamente ahí.

**Dónde vive cada `[S]`.** La etiqueta obliga a declarar el ámbito, y el
ámbito decide el archivo:

| Ámbito del dato | Dónde vive | Ejemplos |
|---|---|---|
| Único para todo el corredor (~5 km) | `src/datos_sitio.py` | `PGA_roca_B`, `ZONA_SISMICA_LA_UNION`, `Z_E030` |
| Varía punto a punto | Columna del CSV | `NF_profundidad_m`, `cbr_subrasante`, `sucs_fundacion` |
| De corredor, pero pendiente de un ensayo que lo cierre | `criterios_adoptados.py` con campo `trazabilidad` | `PERFIL_SUELO_PRESUNTO` |

`src/datos_sitio.py` es paralelo a `tolerancias.py` y `dominios.py` en su
forma —un archivo exento del barrido de literales— y **lo contrario en su
naturaleza**: aquellos están exentos porque sus números NO son valores de
proyecto; éste lo está porque los suyos sí lo son, y de los más pesados (el
PGA gobierna la cadena sísmica entera). Está aparte porque no son constantes
universales, no porque no importen. Su docstring lo dice como regla práctica:
*si el valor cambia al mover la obra de sitio pero NO al cambiar de
proyectista, es `[S]`*.

---

## Tabla de resoluciones

| # | Variable | Dónde estaba | Etiqueta que tenía | Dónde está ahora | Etiqueta | Qué cambió de verdad |
|---|---|---|---|---|---|---|
| 1 | `PERFIL_SUELO_PRESUNTO = "S5"` | `constantes_normativas.py`, bloque "§10 E.030 — solo referencia" | `[N]` (implícita: el archivo solo admite `[N]`) | [`criterios_adoptados.py`](../src/criterios_adoptados.py), junto a `clase_sitio`, con `reemplazado_por = "Ensayo SPT"` | `[S]` | El Art. 14.6 define el **esquema** S0–S5; qué letra le toca a este sitio es aplicarlo a la llanura del Bajo Piura. **Verificado que hoy es referencia muerta**: ningún módulo de `src/modulos/` lo invoca, y un test lo vigila para que no deje de serlo en silencio. Se conserva declarado porque es la presunción geotécnica sobre la que se apoyan `clase_sitio` y la hipótesis de licuefacción de Sec. 0.5 |
| 2 | `PGA_roca_B = 0.50` g | `criterios_adoptados.py` | `[N]` | [`datos_sitio.py`](../src/datos_sitio.py) | `[S]` | Dato de todo el corredor, con `trazabilidad` y `ambito` declarados. **La trazabilidad que la etiqueta exige no está completa y el archivo lo dice con todas las letras**: ver la nota de abajo |
| 3 | `factor_muro = 1.0` | `criterios_adoptados.py` | `[N]` | Partido en dos: `FACTOR_MURO_TABLA = {rigido: 1.0, desplazable: 0.5}` en [`constantes_normativas.py`](../src/constantes_normativas.py) y `factor_muro_eleccion` en [`criterios_adoptados.py`](../src/criterios_adoptados.py) | `[N]` la tabla, `[A]` la elección | Es el reparto que el proyecto ya aplicaba a `F_pga` y a `v_max_concreto_eleccion`, y que esta variable rompía. La justificación es la ya escrita ("cabezal empotrado, sin desplazamiento admisible garantizado"), con sensibilidad `(0.5, 1.0)`. `M9.factor_muro()` ahora **rechaza** con `DatoInvalidoError` una elección que no sea una fila de la tabla: la elección es libre entre dos valores, no entre todos |
| 4 | `NF_profundidad_m = 1.4` m | `criterios_adoptados.py` | `[N]` | Columna del CSV: [`modelos.PuntoCritico`](../src/modelos.py), [`M0_carga.COLUMNAS`](../src/modulos/M0_carga.py) | `[S]` por punto | Ver la nota de abajo sobre por qué la columna va **vacía** y no con cuatro `1.4` |
| — | `ZONA_SISMICA_LA_UNION = 4`, `Z_E030 = 0.45` | `constantes_normativas.py` | `[N]` | [`datos_sitio.py`](../src/datos_sitio.py) | `[S]` | El caso que sirvió de patrón, cerrado con el mismo tratamiento. **Cambio de clasificación, no de uso**: Sec. 0.4 ya había decidido que no gobiernan el cabezal (se descarta el sismo de 475 años de E.030 frente al PGA de Tr = 1000 años), no los invocaba ningún módulo antes y no los invoca ninguno ahora |

---

## Las dos decisiones que no se pudieron cerrar contra evidencia

Las correcciones anteriores son mecánicas: mover una declaración de archivo no
requiere información nueva. Estas dos sí la requerían, y la información no
está en el expediente. Se resolvieron **sin inventarla**, y quedan aquí a la
vista.

### `PGA_roca_B`: la lectura del mapa no se pudo comprobar

La instrucción era condicional: comprobar en el mapa del Apéndice A3 si la
curva de isoaceleración cambia dentro de los ~5 km del corredor; si no cambia,
`datos_sitio.py` con las coordenadas exactas de lectura como trazabilidad; si
cambia, columna del CSV.

**La comprobación no se pudo hacer, y no por descuido:**

1. El mapa del Apéndice A3 es una figura del PDF del Manual de Puentes, que no
   está en el repositorio.
2. El expediente **no registra sobre qué punto se hizo la lectura**. La hoja de
   ruta declara el resultado ("Lectura para La Unión (Piura): PGA = 0.50 g",
   num. 83) y anota la coordenada como pendiente abierto —item 1.4 del tablero,
   *"registrar las coordenadas o la curva de isoaceleración sobre la que se
   hizo la lectura"*—, advirtiendo además que **las curvas varían dentro de un
   mismo departamento**.

Sin el mapa y sin el punto de lectura, la condición no se puede evaluar: la
única forma de "cerrarla" habría sido inventar unas coordenadas, que es
exactamente lo que la etiqueta `[S]` existe para impedir.

**Qué se hizo entonces.** Se aplicó la rama de `datos_sitio.py`, porque es la
única que no exige inventar nada: la otra rama (columna del CSV) obligaría a
escribir cuatro valores de PGA por punto que nadie ha leído. La clasificación
—`[S]`, dato de sitio— es correcta en ambas ramas; lo que la comprobación
decidía era sólo el **ámbito**. Y ese ámbito queda declarado como lo que es:

- `trazabilidad` dice, en el propio archivo, que **la coordenada exacta y la
  curva NO están registradas** y que la reproducibilidad llega hasta el nombre
  del distrito.
- `verificacion_pendiente` conserva el pendiente 1.4 y le añade la
  comprobación que quedó sin hacer: *al registrar las coordenadas, comprobar
  sobre el mapa si la curva cambia dentro de los ~5 km; si cambiara, este dato
  deja de ser único para el tramo y pasa a ser columna del CSV*.
- M11 imprime el dato con una **advertencia de trazabilidad incompleta**, de
  modo que la memoria no puede presentarlo como cerrado.

El valor `0.50 g` no cambió y no está en discusión: lo declara la hoja de ruta
(num. 83 y num. 590). Lo que está abierto es dónde se leyó.

### `NF_profundidad_m`: la columna va vacía, no con cuatro `1.4`

La elección era repetir `1.4` en las cuatro filas del CSV o declarar que
varía. **Se declaró que varía**, y la columna se carga vacía en los cuatro
puntos.

El 1.4 m nunca fue una medición en un cruce: es la caracterización de la
llanura del Bajo Piura, una descripción de zona. Copiarla a cuatro filas
produciría cuatro mediciones donde hubo una descripción, y el propio criterio
—en su `verificacion_pendiente`— ya pedía *confirmar si el NF es único para
todo el tramo o varía punto a punto*. No hay en el expediente ninguna
evidencia de uniformidad.

Consecuencias, todas visibles y ninguna silenciosa:

- La columna admite vacío por el **estudio geotécnico**, que es un tablero
  distinto del 3.1 (ANA/Junta). La fila se carga marcada y quien se detiene es
  la verificación que necesite el dato, no la carga del CSV.
- `punto.exigir("NF_profundidad_m")` lanza `DatoFaltanteError` en vez de
  asumir un valor.
- **V7 (flotación) sigue siendo calculable** sin el NF de cada punto: su
  hipótesis es sumersión completa del conducto ("tubería vacía, NF en su cota
  más alta"), y sumergido del todo el conducto desplaza su volumen entero esté
  el freático a 1.4 m o a 0.8 m. `M8.empuje_flotacion_kn_m()` ya no invocaba el
  valor para calcular, sólo para registrar el uso.
- Lo que sí necesita el número es la **subpresión del cabezal** en M9:
  `altura_agua_sobre_base(D_f, NF_profundidad_m)` y `empujes_trasdos(...)`
  reciben el NF por argumento, del punto. Dos cabezales del mismo tramo con el
  freático a distinta profundidad se calculan con el suyo, que es justo lo que
  un criterio único de tramo no podía expresar.

---

## Lo que este cambio NO hace

- No mueve ningún valor: los números son los mismos, en otro archivo y con
  otra etiqueta.
- No verifica ninguna cita normativa. Eso es
  [`manifiesto_citas.md`](manifiesto_citas.md), regenerado en paralelo.
- No cierra el pendiente 1.4 de la hoja de ruta (coordenadas de lectura del
  PGA), ni el estudio geotécnico del que salen los NF por punto. Los deja
  declarados donde un revisor los ve.
- No resuelve si las otras filas `⚠ sin numeral` de `constantes_normativas.py`
  están bien clasificadas. Con cinco etiquetas en la mano, varias merecen una
  segunda mirada; ninguna se tocó aquí.

## Guardias automáticas que dejan este estado

Este documento describe una decisión; los tests la sostienen. Si alguien
deshace cualquiera de las cuatro correcciones, falla la suite y no la lectura
de un manifiesto:

| Guardia | Qué impide |
|---|---|
| `tests/test_sin_literales.py::test_los_datos_de_sitio_salieron_de_constantes_y_criterios` | Que un `[S]` vuelva a declararse en `constantes_normativas.py`, o quede declarado en dos archivos |
| `tests/test_sin_literales.py::test_la_tabla_del_factor_de_muro_es_normativa_y_la_eleccion_no` | Que tabla y elección vuelvan a mezclarse en un solo valor |
| `tests/test_criterios_adoptados.py::test_ningun_criterio_adoptado_lleva_ya_la_etiqueta_N` | Que una constante universal vuelva al archivo de lo no normativo |
| `tests/test_criterios_adoptados.py::test_un_criterio_S_declara_trazabilidad_y_no_sensibilidad` | Un `[S]` sin trazabilidad, o con el rango de sensibilidad de un `[A]` |
| `criterios_adoptados._coherencia_de_etiquetas()` (al importar) | Lo mismo, pero antes de que empiece cualquier corrida |
| `tests/test_criterios_adoptados.py::test_el_perfil_de_suelo_es_referencia_declarada_y_no_calculo` | Que `PERFIL_SUELO_PRESUNTO` deje de ser referencia muerta sin que nadie decida si basta una presunción de tramo |
| `tests/test_datos_sitio.py::test_lo_que_vive_aqui_es_de_corredor_y_no_de_punto` | Que un dato que varía punto a punto se quede en `datos_sitio.py` en vez de mudarse al CSV |
| `tests/test_M0_carga.py::test_el_NF_esta_pendiente_en_todas_las_familias` | Que el 1.4 m vuelva a las filas del CSV como si fueran cuatro mediciones |
| `tests/test_M11_reporte.py::TestEtiquetaDeSitio` | Que la `[S]` llegue a la memoria sin color propio, sin leyenda o sin bloque de declaración |
