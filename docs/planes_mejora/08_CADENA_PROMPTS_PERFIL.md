# Cadena de prompts PF — cierre del diseño a nivel de perfil para las tres familias

**Origen:** la revisión de cierre de E-B (2026-09-21). Con la cadena EXT y la
evolución E-A/E-B en `origin/main` (`533e8b2`), la app dimensiona a `--alcance
perfil` las tres familias del §2.3 de la v8, y se comprobó con una corrida real
sobre `tests/ejemplo_puntos.csv`: A-01 y A-02 (paso), B-01 (alivio, con TW no
ahogante) y C-01 (cruce de canal, marco 1.00 × 1.00 m con los siete criterios del
cajón declarados por `--declarar`). Lo que esta cadena cierra es lo que esa
corrida dejó a la vista: un hallazgo abierto que sí toca el perfil (PC-03), los
bloqueos que salen «en cebolla» (una capa por corrida), la sensibilidad de los
[A] que un jurado va a pedir, un umbral que la fuente nombra como indicador, y
una guía de uso que hoy no existe.

**Cómo ejecutar la cadena.** Un prompt por sesión, en el orden dado. Cada sesión
termina con el ritual de cierre de `07_CADENA_PROMPTS_EXT.md` («Reglas comunes»,
incluidas aquí por referencia y NO repetidas). No se avanza al siguiente si la
suite no está en verde y el trabajo no está en `origin/main`. PF-1 y PF-6 tocan
hallazgos del tracker; el resto es evolución y no cierra IDs.

**Serie de commits:** `ext(PF-n): <resumen> — <IDs cerrados o «sin IDs»>`.

**Lo que NINGÚN prompt de esta cadena hace**, para que nadie lo lea como
pendiente: hidrología (el caudal entra por el CSV), nivel de expediente (Fases
8 y 9, V5, V8), fuentes que no están en `normas/`, y una vista nueva de la GUI
que no sea derivada de un objeto que ya existe.

---

## Estado de partida medido (2026-09-21, `533e8b2`)

| Qué | Medida |
|---|---|
| Suite («sí · sí») | 3891 passed, 3 skipped, collected 3894 |
| Criterios | 74; 35 sin valor; 9 de perfil sin valor (7 del cajón + `TW_receptor` + `homogeneidad_serie_fen`) |
| Tracker | 303 filas; abiertos PC-03, PC-31, R48-001, R48-007; C5-02 marcado «Reabierto → EXT-6» con EXT-6 ya corrido |
| Corrida de perfil | 4 de 4 puntos dimensionados con luz, TW, `S_conducto ≥ S_cauce`, cota de coronación del canal y los siete del cajón |

Las capas de bloqueo que costaron una corrida cada una, en el orden en que
aparecieron: `luz_m` (JSON) → los siete criterios del cajón → `cota_coronacion_canal`
(CSV, sólo Familia C) → V2b por `S_conducto < S_cauce`. Es la evidencia de PF-2.

---

## PF-1 · PC-03: el descarte por HWi/D ≤ 0 deja de ser definitivo

> **Corregido al ejecutarlo (PF-1, 2026-09-21).** El punto (1) del prompt
> —«si D_i no tiene dominio, prueba el siguiente antes de descartar»— estaba
> al revés: HWi/D DECRECE con D, de modo que si la carta se cae en el D
> mínimo ninguno mayor la levanta, y el descarte del material entero era
> correcto. Lo que PF-1 cerró es la clase (vacío declarable
> `hw_entrada_fuera_de_rango`, ficha PF-1-01) y la visibilidad del bloqueo;
> la monotonía quedó fijada como propiedad P9. El texto del prompt se
> conserva tal como se ejecutó.

```text
Ejecuta únicamente PF-1 de docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md y aplica las reglas comunes de 07_CADENA_PROMPTS_EXT.md. Sesión con plan mode. Lee antes la ficha PC-03 de la hoja Hallazgos del tracker (abierta) y la refutación que la acota: el umbral analítico S* = 2·(H_c/D + K·q*^M) y la monotonía en D ya están escritos en v8 §4.2 y en los docstrings de M4_control; en el corredor del repositorio (S_cauce 0.006–0.008) nunca se dispara, y en una vía de evitamiento con alivios pequeños en tramos empinados sí. Hoy `M4.control_entrada` (MAT-D10) lanza DisenoNoFactibleError cuando HWi/D ≤ 0 y `MD.disenar_punto` descarta el material ENTERO; el Bloqueo viaja con `criterio=None`, por lo que `M11.criterios_bloqueantes` lo salta y ni la pestaña 4 ni el bloque «criterios pendientes» de la CLI lo muestran. Decide y escribe primero, en docs/decisiones_diferidas.md, QUÉ clase de excepción corresponde según la taxonomía de CLAUDE.md, en el orden en que se pregunta: no falta dato (no es Faltante), el dato es válido (no es Invalido), la aritmética cabe (no es LimiteNumerico); lo que ocurre es que la ecuación de control de entrada no tiene dominio para ese par (Q, S) y HDS-5 no da otro método en esa rama: argumenta si es MetodoNoEvaluableError (diferible a perfil, no a expediente, como los dos casos vivos de EXT-3) o un vacío declarable [A] con CriterioPendienteError; la ficha PC-03 pide la segunda y la refutación acota la primera, y tú tienes que elegir con el argumento escrito y contrastarlo contra las dos. Sea cual sea la clase: (1) el descarte no puede ser del material entero cuando OTRO diámetro de la serie sí tiene dominio (usa la monotonía en D que M4 ya documenta: si D_i no tiene dominio, prueba el siguiente antes de descartar; deja escrito por qué la monotonía lo permite, con la cita); (2) el Bloqueo lleva `criterio` o `tipo` de modo que M11.criterios_bloqueantes y la pestaña 4 lo pinten con etapa, punto y motivo; (3) el motivo nombra el par (Q, S) culpable y el S* analítico, con la forma MAT-D13. Tests primero en rojo con xfail(strict=True): el caso de la ficha (D = 0.90, Q = 0.05, S = 0.40 y Q = 0.10, S = 0.55) medido por `cli.correr` sobre un CSV de un punto; el caso que SÍ tiene dominio en un D mayor y hoy sale no factible; el Bloqueo visible en `M11.criterios_bloqueantes` y en el JSON `criterios.bloquearon`; y una propiedad por malla en tests/test_ext11_propiedades.py: para todo (Q, S) con S < S*(D) el control de entrada devuelve HWi/D > 0. Regenera la línea base de la Familia C sólo si algún número o rótulo cambia y declara en su README qué y por qué. Cierra PC-03 en el tracker con el SHA. Ritual de cierre. Devuelve: clase elegida y por qué, qué IDs cerraste, tests nuevos, números movidos, diferidos. Detente ahí.
```

## PF-2 · Pre-vuelo de datos por familia: todas las capas de la cebolla en una sola lectura

```text
Ejecuta únicamente PF-2 de docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md y aplica las reglas comunes de 07_CADENA_PROMPTS_EXT.md. Sesión con plan mode. Evidencia: la corrida de perfil de la revisión de E-B necesitó cuatro corridas para llegar a dimensionar C-01, porque cada bloqueo apareció después del anterior: `luz_m` (JSON de --datos-externos), los siete criterios del cajón, `cota_coronacion_canal` (columna del CSV que sólo la Familia C exige) y `S_conducto` (JSON). El anticipo de la pestaña 1 (`src/anticipo.py`: `criterios_vacios_alcanzables`, `contraste_de_cabecera`, `diferimientos_del_alcance`) ya estima criterios vacíos por alcance y celdas vacías por columna leyendo `M0_carga.COLUMNAS`, `M0_carga.VACIOS_ADMITIDOS` y `M0_carga.leer_cabecera`, pero NO mira el JSON de datos externos (`servicio.CLAVES_EXTERNAS`, `servicio.cargar_datos_externos`, `servicio._resolver_tw` y los demás resolvedores) ni dice qué columnas exige CADA familia de las filas presentes. Añade a `src/anticipo.py` un cuarto bloque, `datos_faltantes_por_punto(csv, externos, alcance)`, DERIVADO y nunca escrito a mano: para cada fila del CSV, por su familia, qué columnas obligatorias vienen vacías (de `VACIOS_ADMITIDOS.familias`), qué claves externas de `CLAVES_EXTERNAS` faltan para ese punto (globales o por punto) y de dónde tendría que venir cada una (el `concepto` de `variables_entrada` y el texto que `DatoFaltanteError` ya lleva para esa clave, leído del código y no transcrito). Sigue siendo ESTIMACIÓN (`AVISO_DEL_ANTICIPO`): no gobierna ningún filtro ni el botón de ejecutar. Expónlo en dos sitios: la CLI con `--prevuelo` (imprime el anticipo entero y termina con 0 si no estima faltas y 1 si estima alguna; NO corre el pipeline, guardia por AST como la de `--comparar`) y el panel de la pestaña 1 (una tabla más en el mismo MarcoScroll; `gui/app.py` sólo pinta). Tests primero en rojo con xfail(strict=True): sobre `tests/ejemplo_puntos.csv` SIN JSON el pre-vuelo nombra `luz_m` en los cuatro puntos, `cota_coronacion_canal` sólo en C-01 y `L_hidraulico_m` sólo en B-01; con `tests/linea_base_familia_c/entradas_ampliadas.json` deja de nombrar `S_conducto` para C-01; la unión de lo que el pre-vuelo estima para cada punto contiene todo `DatoFaltanteError` que la corrida real de perfil produce (un test que corre el pipeline y contrasta, en la dirección «nada real escapa a la estimación», y que documenta los falsos positivos si los hay); la guardia por AST de que `datos_faltantes_por_punto` no ejecuta `servicio.correr`; y el parametrizado de `test_gui_contrato` sobre `ARBOLES_DE_LA_GUI` si tocas un árbol nuevo. No cierra IDs. Ritual de cierre. Detente ahí.
```

## PF-3 · Barrido de sensibilidad de los [A] de perfil con el comparador

```text
Ejecuta únicamente PF-3 de docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md y aplica las reglas comunes de 07_CADENA_PROMPTS_EXT.md. Sesión con plan mode. La constitución obliga a que todo [A] de perfil lleve `sensibilidad`, y una tesis tiene que mostrar qué pasa con el diámetro, el HW y las verificaciones cuando el [A] recorre su ventana. El comparador de E-B (`src/comparador.py::comparar`, `TOL_COMPARADOR_ABS/REL`) ya sabe decir en qué difieren dos volcados por identidad de punto. Añade `src/barrido.py` con `barrer(csv, externos, alcance, clave, valores, declaraciones_base)` que: (1) valida CADA valor por la MISMA puerta que una declaración (`src.editores.verificar` o `declaracion.declarar_valor`/`declarar_en_rango`/`declarar_desde_tabla` según el modo, con `ValueError` si cae fuera de la ventana: un barrido fuera de la ventana no es sensibilidad, es otra adopción); (2) corre `servicio.correr` una vez por valor, con `declaracion.limpiar()` y `ca.quitar_valor_dinamico` entre corridas para que ninguna herede el estado de la anterior (EXT-4: cada `Informe.contexto` es de su corrida); (3) compara cada volcado contra el del primer valor con `comparador.comparar` y arma una tabla por punto: valor del [A], material, D o B×H, HW, control gobernante, verificaciones que cambian de veredicto, y «no comparable» cuando cambia el método (`CAMPOS_DE_METODO`); (4) devuelve un objeto de `modelos.py` (`ResultadoDeBarrido`, con los volcados enteros dentro) y NO recalcula nada por su cuenta: la aritmética es la del pipeline y la comparación la del comparador (guardia por AST: `src/barrido.py` no importa `src.modulos`). CLI: `--barrido CLAVE=v1,v2,v3` (ast.literal_eval por valor, como `--declarar`; repetible para varias claves, una a la vez, nunca producto cartesiano), salida de texto con la tabla y `--json` con el `ResultadoDeBarrido`; la memoria HTML NO cambia (el barrido no es parte del expediente, es un anexo de la tesis). GUI: un botón «Barrido…» en la pestaña 2 sobre el criterio seleccionado que pide los valores por el parser único (`interpretar_texto_declarado`) y pinta la tabla en un Toplevel; opcional si no cabe en la sesión, y si lo difieres dilo en decisiones_diferidas.md con símbolo. Tests primero en rojo con xfail(strict=True): el barrido de `ke_entrada` en tres valores de su ventana sobre A-01 produce tres corridas con `criterios_sha1` idéntico y `csv_sha1` idéntico, y HW monótono no decreciente con ke; un valor fuera de la ventana no corre nada (ValueError antes de la primera corrida); el estado del proceso queda limpio al terminar (`ca.valores_dinamicos()` y `declaracion.procedencias()` iguales a los de entrada); el barrido de un criterio de tabla exige fila o nota por la misma puerta que la pestaña 2; y la guardia por AST. No cierra IDs. Ritual de cierre. Detente ahí.
```

> **Ejecutado (PF-3, 2026-09-21).** Entró `src/barrido.py::barrer` con la CLI
> (`--barrido`, `--barrido-nota`, `--barrido-fila`) y los tres tipos en
> `modelos.py`. Dos desvíos del texto del prompt, declarados: el aislamiento
> entre corridas no se hizo con `declaracion.limpiar()` y
> `ca.quitar_valor_dinamico` sino con la fotografía de `estado_de_sesion` y
> `restaurar_sesion(sustituir=True)`, que repone también la procedencia de lo
> que el proceso tenía al entrar; y el botón «Barrido…» de la pestaña 2 se
> difirió con símbolo (ficha PF-3-01). `barrer` recibe el volcador
> (`volcar=cli.informe_json`) porque `src/` no importa `cli` (EXT-9).

## PF-4 · V2b: umbral duro o indicador con aviso, declarado y no cableado

```text
Ejecuta únicamente PF-4 de docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md y aplica las reglas comunes de 07_CADENA_PROMPTS_EXT.md. Sesión con plan mode. Usa el verificador-normativo antes de tocar nada: HDS-5 3.ª ed., num. 5.3.3 «Sedimentation», pág. impresa 5.11 —la cita ya está en el registro; lee su `texto_literal` y su `caracter`—. La fuente nombra DOS «key indicators of potential problems» (pendiente del barril menor que la del cauce; rugosidad mayor que la del cauce) y no fija umbral. `M5_verificaciones.v2b_sedimentacion` (V2b, implementada en S20) convierte el primero en umbral duro «por decisión conservadora del proyecto», y en la corrida de perfil de la revisión de E-B eso descartó los siete marcos de la serie de C-01 con el dato de sonda (0.004 frente a 0.006) — en un cruce de canal real la pendiente del conducto suele venir fijada por el canal. Esa «decisión conservadora» es un [A] que vive cableado y sin ficha, que es lo que la constitución prohíbe. Crea en criterios_adoptados.py el criterio `regimen_v2b` con forma `categoria`, dos opciones cerradas en `sensibilidad` («umbral_duro»: la conducta actual, V2b incumplida detiene el punto; «indicador_con_aviso»: V2b se evalúa igual, se imprime en la memoria con el texto literal de la fuente y el veredicto INDICADOR, y NO descarta el diámetro), nivel PERFIL, etiqueta [A] con `Fundamento` cuyo verbo esté sostenido por el `caracter` de la cita (NOR-MEM-01: no escribas «la norma exige» sobre «key indicators»), y VALOR «umbral_duro» —no vacío: dejarlo vacío detendría los cuatro puntos de toda corrida de perfil, y esta sesión no cambia ningún número de la línea base—. La segunda mitad del indicador (n de Manning del cauce natural) sigue pendiente como hoy; no la inventes. El veredicto INDICADOR tiene que ser un `TipoDeVeredicto` que ya exista o uno nuevo argumentado en modelos.py (revisa PC-27, «Cerrado parcial», antes: el estado de verificación ya tiene tres capas y no puede ganar una cuarta sin cerrar aquélla); `Verificacion.cumple` sigue siendo bool y la memoria lo pinta como aviso, no como incumplimiento ni como diferido. Tests primero en rojo con xfail(strict=True): con el valor del archivo la línea base de la Familia C no cambia un byte (diff vacío); declarando «indicador_con_aviso» por `--declarar`, C-01 con `S_conducto = 0.004` dimensiona y su memoria imprime el texto literal de 5.3.3 desde `Registro.textos_literales()` y el veredicto de aviso; la guardia de forma rechaza «aviso» y «1»; el criterio aparece en la pestaña 2 con editor de categoría; y `tests/test_cierre_perfil.py` sigue midiendo que el criterio es de perfil porque la corrida lo invoca. Reporta contra la v8 (fila V2b de la tabla de Fase 5) si su redacción dice «umbral» donde la fuente dice «indicator», con la cita. No cierra IDs del tracker; enlaza PC-27 si lo tocas. Ritual de cierre. Detente ahí.
```

## PF-5 · Guía de corrida de perfil que la suite ejecuta

```text
Ejecuta únicamente PF-5 de docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md y aplica las reglas comunes de 07_CADENA_PROMPTS_EXT.md. Sin plan mode. El README describe requisitos, exportación y multi-obra; no dice cómo se lleva un CSV de una vía nueva hasta un perfil con las tres familias dimensionadas. Escribe docs/guia_perfil.md para un tesista que no ha leído el código, con esta secuencia y NADA que no exista como objeto: (1) qué columnas del CSV exige cada familia, derivado de `M0_carga.COLUMNAS` y `VACIOS_ADMITIDOS` (si PF-2 ya entró, el texto remite al `--prevuelo`); (2) el JSON de `--datos-externos` con las seis claves de `servicio.CLAVES_EXTERNAS`, globales y por punto, y cuál gana; (3) el `sitio.json` de `--datos-sitio` para una obra que no es La Unión, con trazabilidad y fecha, y la advertencia de corredor que sale si no se declara; (4) los nueve [A] de perfil sin valor (`ca.criterios_de_perfil_sin_valor()`), con la FORMA de cada uno (`Criterio.forma`), su ventana y un ejemplo de `--declarar` sintácticamente válido por forma —serie de pares, texto de fila, entero, real—, sin recomendar ningún valor: la guía dice cómo se declara, no qué; (5) la lectura del RESUMEN: qué significa «Puntos dimensionados», «Etapas bloqueadas», «Diferidas por alcance» y por qué «Expediente cerrado: no» es lo esperado a perfil; (6) las salidas: JSON, HTML, PDF, CSV resumen, sesión, y `--comparar`/`--barrido` si PF-3 ya entró. La guía NO se escribe a mano dos veces: cada bloque de comandos de la guía lo ejecuta `tests/test_guia_perfil.py` en subproceso sobre `tests/ejemplo_puntos.csv`, un fixture JSON y un sitio.json de prueba, y afirma el número de puntos dimensionados que la guía promete (los cuatro, con los siete del cajón declarados y `S_conducto ≥ S_cauce`); las listas de columnas, claves y criterios de la guía se comparan contra los símbolos de los que salen (test de sincronía, como los cuatro generados), de modo que si un criterio cambia de forma el test lo dice. Enlaza la guía desde README.md en una línea. No cierra IDs. Ritual de cierre. Detente ahí.
```

## PF-6 · Cabos: R48-007, la fila que el editor no suelta, lo que el comparador calla

```text
Ejecuta únicamente PF-6 de docs/planes_mejora/08_CADENA_PROMPTS_PERFIL.md y aplica las reglas comunes de 07_CADENA_PROMPTS_EXT.md. Sin plan mode. Tres cabos medidos, en un solo commit porque los tres son guardias pequeñas y ninguno mueve un número de cálculo. (a) R48-007, abierto: `dominios.CBR_MAX_FISICO = 100.0` es un techo que `M0_carga` aplica con DatoInvalidoError, y el Manual de Suelos tiene la categoría S5 abierta por arriba (cuadro de categorías de subrasante, pág. impresa 37) y base granular con CBR 100 % (pág. 129). ANTES de tocar dominios.py verifica las dos páginas contra el PDF con el verificador-normativo y cita numeral, página y texto literal; si la fuente sostiene que un CBR > 100 % es legítimo, dominios.py deja de topar en 100 (recuerda que dominios.py acota lo que un dato PUEDE SER, y que un techo que la fuente no fija es un valor de proyecto inventado); si no lo sostiene, di por qué y deja la fila como está. Cierra o argumenta R48-007 en el tracker con el SHA. (b) `gui/editores.py::EditorEscalar._al_fila_elegida` prellena la clave y deja el campo editable; si el proyectista reescribe el texto, `_fila_y_nota_del_editor` sigue devolviendo la fila vieja y la puerta (`declaracion.declarar_desde_tabla`, cierre de E-B parte 3) rechaza con «NOMBRA la fila…». Haz que el editor suelte la fila cuando el texto deja de ser la clave de la fila elegida, sin declarar nada por su cuenta (guardia por AST de EB-01 intacta); mídelo en `tests/apoyo/gui_eb_real.py` con el gesto real. (c) `src/comparador.py`: `lineas()` dice «salvo la marca de tiempo y las rutas de origen» y calla que ignora `expediente.csv`; `alcance.diferidos` se compara sólo por longitud (`diferidos[len]`); `True` y `1` salen IGUALES porque `_es_numero` excluye bool y `True == 1`. Compara `diferidos` por contenido, distingue bool de número, y que `lineas()` nombre exactamente lo que el comparador omite, leído de una tupla `CAMPOS_OMITIDOS` que el test contrasta contra el código. Tests primero en rojo con xfail(strict=True) para los tres. Ritual de cierre. Devuelve qué IDs cerraste (entero / en parte / no). Detente ahí.
```

---

## Después de PF-6

Quedan fuera de esta cadena, y no por olvido: PC-31 (sin daño medido), R48-001
(el umbral de 6.0 m de ancho de cauce, que es de clasificación y no de perfil),
la fila C5-02 del tracker (revisar si EXT-6 la cerró y actualizar el estado, sin
código), y todo lo de expediente. Si PF-1 elige `MetodoNoEvaluableError`, PC-27
(«Cerrado parcial») gana un tercer productor y conviene cerrarlo en la sesión
siguiente a PF-4, que es la otra que toca el estado de verificación.
