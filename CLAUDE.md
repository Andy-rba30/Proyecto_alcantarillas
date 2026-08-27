# Reglas del proyecto

## Fuente de verdad
- Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v8.md (o la version
  vigente que exista en docs/: M11 la localiza con el patron
  `hoja_de_ruta_alcantarillas_v*.md` y exige que haya exactamente una). Toda cita de
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
  índices, y constantes matemáticas puras (pi). Tres archivos más quedan
  exentos por no contener valores de proyecto: tolerancias.py (precisión
  numérica: cambiarla no mueve ninguna magnitud física), dominios.py (rango
  físico posible de un dato de entrada: no entra en ninguna fórmula) y
  constantes_fisicas.py (constantes físicas universales -- hoy cinco nombres:
  G = 9.81 m/s², RHO_AGUA, N_POR_KN, GAMMA_AGUA y GAMMA_AGUA_KN_M3 (esta
  última derivada de las tres anteriores, no un literal independiente) --
  el mismo valor en cualquier obra del planeta; no responde a "qué exige la
  norma peruana" y por eso no es [N]). Regla
  para saber si un número va en uno de esos tres: si cambiarlo puede alterar un
  resultado del cálculo, no va ahí. datos_sitio.py está exento por la razón
  CONTRARIA: sus números sí son valores de proyecto, y de los más pesados —
  está aparte porque no son constantes universales, no porque no importen.
  G_LAUSHEY = 9.8 SÍ vive en constantes_normativas.py, a pesar de ser
  numéricamente el mismo concepto físico: es el valor que la Sec. 4.1.1.3.7 c)
  de la hoja de ruta escribe explícitamente para su fórmula de d50, y separarlo
  de la gravedad genérica evita que una obra tenga dos valores distintos de "g"
  (9.8 en Laushey, 9.81 en todo lo demás) conviviendo sin que nadie lo declare.
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
- Python 3.11+. Dependencias: numpy, scipy (brentq), pytest, ttkbootstrap,
  weasyprint. Cualquier dependencia adicional se consulta antes.
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

## Cierre de tarea: la entrega es `origin/main`

**Una tarea no está terminada hasta que su trabajo está en `origin/main`.**
El último paso de cualquier tarea, siempre, son estos dos:

1. **Fusionar a `main` y empujar.** Una rama de trabajo empujada al remoto no
   es una entrega: es un borrador que nadie lee. Un commit que no está en
   `main` no cuenta como entregado.
2. **Confirmar el conteo de tests leyéndolo de `origin/main`**, no del clon
   local ni de la rama de trabajo. Traer el remoto primero (`git fetch origin
   main`) y correr la suite sobre ese árbol. El número que se reporta es ese.

Por qué está escrito aquí: esto falló dos veces. La primera se arregló a mano
en el "PASO 0" y no se dejó regla, así que volvió a pasar — siete commits y 36
tests quedaron en una rama sin fusionar mientras se reportaba `main` como si
los tuviera, y una auditoría posterior los dio por perdidos.

Al reportar el conteo, distinguir **`passed` de `collected`**: hoy hay un test
`skipped` permanente, de modo que `collected = passed + 1`. Decir cuál de los
dos se está citando; la mayor parte de la confusión histórica de números sale
de mezclarlos.

Si la fusión no se puede hacer (permisos, política de egress, conflicto), eso
**no** convierte la tarea en terminada: se reporta explícitamente qué quedó sin
fusionar, en qué rama y con qué SHA, para que nadie lo lea como entregado.

## Reglas de corrección de hallazgos de auditoría

Este repositorio tiene 234 hallazgos de tres auditorías externas
(`docs/auditorias/auditoria_matematica.md`, `auditoria_sistema.md`,
`auditoria_normativa.md`), ya cruzados en
`docs/auditorias/matriz_cruzada_auditorias.xlsx` (14 clusters por causa raíz, 8
conflictos resueltos). Ese archivo es el TRACKER: el estado de cada hallazgo se
marca ahí, en las columnas Estado / Responsable / Commit. El PLAN es
`docs/hoja_de_ruta_correcciones_v12.md`.

1. Antes de tocar un archivo, busca su cluster en la hoja `Clusters` y abre la
   ficha de cada ID citado (MAT-, SIS-, NOR-) para leer su evidencia completa.
   Un cluster se corrige entero, en un solo cambio de diseño y un solo commit.
   Nunca hallazgo por hallazgo. Solo 224 de los 234 caen en alguno de los 14
   clusters: los otros 10 llevan `—` en la columna Cluster (los nueve
   `NOR-OK-*` y `NOR-AAS-07`, retirado) porque la auditoría los revisó y los
   cerró como correctos, sin corrección que hacer. No son trabajo pendiente.
2. Antes de aplicar cualquier corrección, consulta la hoja `Conflictos` (o la §6
   del plan). Ocho objetos del repositorio tienen una corrección "obvia" que es
   la EQUIVOCADA porque otra auditoría descubrió por qué. Si el objeto que vas a
   tocar está ahí, la resolución de esa fila es vinculante y sustituye a tu
   criterio.
3. Después de implementar, contrasta tu solución contra la evidencia de cada
   ficha y decime explícitamente si la cierra, la cierra en parte, o no la
   cierra. Si tu solución contradice lo que dice la ficha, parate y explicá por
   qué antes de seguir.
4. Ancla todo por NOMBRE DE SÍMBOLO (función, constante, clave de criterio),
   nunca por número de línea. Al menos 66 de 296 referencias archivo:línea del
   manifiesto no llevan a lo que dicen llevar, y las auditorías corren sobre dos
   commits distintos (71b134fb y 2e1708ab).
5. Cita los IDs siempre con prefijo MAT- / SIS- / NOR-. `F-01` y `F-02`
   significan hallazgos DISTINTOS en la auditoría Normativa y en la de Sistema.
6. No escribas tests contra el comportamiento actual antes de cerrar las fases
   de corrección: congelarías los defectos. Los tests van en su fase, después.
7. Cuando el código y la hoja de ruta discrepan, el defecto se reporta contra la
   hoja de ruta primero y la fuente primaria (el PDF en normas/) decide.
8. No inventes valores normativos ni citas: numeral, artículo y página salen del
   PDF, no de memoria. Si un dato lo tiene que decidir el proyectista, no lo
   elijas vos: dejalo como vacío declarado, por la vía que el proyecto ya usa
   para V5 y V8.
9. Actualiza la columna Estado/Responsable/Commit de la hoja `Hallazgos` del
   `.xlsx` para cada ID que cierres en la sesión. `openpyxl` está PREAUTORIZADO
   para esto (`pip install openpyxl --break-system-packages`): es herramienta de
   mantenimiento del tracker, no dependencia del software calculado — no va en
   requirements.txt ni necesita consulta previa.

### Git (fase de corrección)
- El trabajo puede pasar por ramas auxiliares, pero ninguna queda abierta: al
  cerrar cada sesión, todo tiene que estar fusionado en `main`.
- Un commit por sesión (ver `docs/hoja_de_ruta_correcciones_v12.md`), con
  mensaje `fase1(Sn): resumen — IDs cerrados`, donde `Sn` es el número de
  sesión (S1, S2...).
- No hagas commit si la suite no está en verde.
