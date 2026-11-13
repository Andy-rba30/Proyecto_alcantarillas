# Bitácora de conteos y de entorno (material de proceso)

> **Qué es este archivo.** La sección «Cierre de tarea: la entrega es
> `origin/main`» de `CLAUDE.md`, MOVIDA aquí ENTERA por T-12 (2026-11-13,
> INF-5.2.2) sin resumirla ni reescribirla: desde la línea siguiente a esta
> nota, el texto es el de `CLAUDE.md` en `f77c5d4`. Es la bitácora del
> PROCESO de desarrollo —el ritual de cierre de cada sesión, el par de la
> suite medido sesión a sesión, las cuatro configuraciones de entorno y los
> incidentes—, no una regla técnica del programa, y por eso salió de la
> constitución, que conserva sólo las reglas técnicas.
>
> **Las rutas que cita son las de antes de T-12.** `docs/auditorias/` es hoy
> `proceso/auditorias/`, `docs/planes_mejora/` es `proceso/planes_mejora/`,
> `verificar_sesion.py` es `proceso/verificar_sesion.py` (se lanza con
> `python3 -m proceso.verificar_sesion`), `tests/apoyo/tracker.py` es
> `proceso/apoyo/tracker.py`, y los tests de proceso viven en
> `proceso/tests/` (`python -m pytest proceso/tests`), fuera de la suite del
> entregable. La tabla de configuraciones de abajo la actualiza cada
> integración, aquí y no en `CLAUDE.md`.
>
> **Desde T-12 el cierre corre DOS suites**: la del entregable (`python -m
> pytest`, que recoge sólo `tests/`) y la de proceso (`python -m pytest
> proceso/tests`); `python3 -m proceso.verificar_sesion` corre las dos (paso 1
> y 1-bis). Y mide también la suite sobre una EXPORTACIÓN del entregable
> (`git archive HEAD`, sin `proceso/` ni `.git`), que es lo que recibe quien
> descarga el ZIP. La actualización de este archivo AÑADE texto y cambia
> cifras; no borra ni reescribe el texto histórico (lo comprueba
> `proceso/tests/test_t12_proceso.py`).

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

Al reportar el conteo, distinguir **`passed` de `collected`** y saber que **el
conteo es un PAR, no un número**. Es la misma lección que el paso 2 de
`verificar_sesion.py` dejó escrita en S12 para PyMuPDF, aplicada ahora a un
segundo eje. Lo invariante es `collected = passed + skipped`, hoy **6425** en
la suite del ENTREGABLE (desde T-12 hay dos suites: la de proceso, aparte,
recoge **145**, y su invariante es el mismo); lo
que se mueve es el reparto, y **ningún salto de los de abajo es una
regresión**. (Desde T-0 hay un TERCER eje, el repositorio de normas enlazado
o no por `NORMAS_DIR`: son dieciocho saltos más sin él (siete hasta T-2,
doce hasta T-4; desde T-12, que retiró los PDF de `normas/`, son TODOS los
que abren un PDF: 152 más sin él, medidos), descritos en «Dónde
están los PDF de normas».) Son de **dos** clases desde EXT-11, y hasta entonces eran tres
(la primera viñeta de abajo explica la que desapareció):

- `tests/test_MD.py` YA NO SALTA. Hasta EXT-11 tenía el `skipped`
  **permanente** por condición imposible —un `skipif` que guardaba que
  `M5_verificaciones` no existiera, y ya no podía darse—, que era un test que
  nunca corría (PC-22). EXT-11 lo sustituyó por la simulación de la ausencia
  REAL: un subproceso sobre una copia del árbol sin el archivo de M5, donde
  `import_module` falla de verdad. Por eso la columna «sí · sí» pasa de 4 a
  3 saltos.
- `tests/test_gui_contrato.py` y `tests/test_ext5_forma_gui.py` — los tests
  de **ventana real**, que hoy son **once** en `test_gui_contrato` y `test_ext5_forma_gui` (S20 abrió el
  primero, la corrida de perfil; S22 el de la ayuda de entrada; G1 el de la
  selección real de la pestaña 2, que sobrevive al filtro; I1 el smoke que
  construye la app con las cuatro pestañas pobladas y abre y cierra
  `gui/ventana_normativa.py`, que hasta entonces no se construía nunca bajo
  Tk; EXT-4 el del contexto de corrida, que lee el texto real de «Etapas
  bloqueadas» y el estado real de los exportadores tras declarar, quitar,
  cargar sesión y fallar; EXT-5 los tres de `tests/apoyo/gui_ext5_real.py`
  sobre UNA corrida —el bloqueo real de C-01 tras declarar los siete del
  cajón por el ratón, la cara de solo lectura del `Derivada` en la pestaña 2
  y el veredicto de 'nan' al escribir y al declarar—; EXT-8 el de
  `tests/apoyo/gui_ext8_real.py`, que mide el rótulo visible del motivo, la
  rueda de X11, Escape, Control-Return y la exportación del PDF —por el
  SUBPROCESO, con el botón apagado, el estado terminal y la cancelación,
  cuando el intérprete de la ventana tiene weasyprint; por el navegador
  cuando no—; EXT-10 el de las dos obras; el cierre de C09 el de las tres
  caras restantes de la ventana normativa, `tests/apoyo/gui_caras_normativa.py`,
  que declara por el camino del botón en RANGO, CATALOGO y CAMPO—). Se saltan
  cuando ningún intérprete disponible puede levantar un `Tk`: falta `tkinter`,
  falta `ttkbootstrap` o falta entorno gráfico.
- `tests/test_familias_del_csv.py` — **seis** saltos de DISEÑO (tres hasta
  T-9, que sumó las tres claves de la cuneta, de la Familia B), no de entorno,
  y por eso valen lo mismo en las cuatro configuraciones. El test está
  parametrizado por (dato declarado × familia) y mide sólo las familias que
  NO usan el dato; las seis combinaciones que sí lo usan se saltan diciéndolo.
  Es el primer salto del repositorio que no depende de qué haya instalado.
- Y aparte, en bloque, los **33** de `tests/test_normativa_pdf.py` (32 hasta
  T1, que sumó el de la resolución impresa del Manual de Puentes), que se
  saltan sin PyMuPDF —dependencia de TEST, no de producción—. Ése es el eje
  que S12 documentó. Con los marcados `pdf` de otros archivos eran 35 en
  total hasta T-0, **39** desde T-0, que sumó cuatro en
  `tests/test_t0_gobernanza.py` (la portada, las páginas y la paginación de
  HEC-14 y del WSDOT Hydraulics Manual), **40** desde T-2, que sumó
  el de las cifras del ejemplo publicado de HDS-5 contra su página
  (`tests/test_t2_hidraulica.py`), y son **55** desde T-4, que sumó los
  quince de `tests/test_t4_materiales_durabilidad.py` que fijan en su página
  los números que el cálculo toma de WSDOT, AASHTO LRFD, HDS-5, EG-2013,
  ASTM A796 y la E.050. T-1 sumó **veinte** en `tests/test_t1_hidrologia.py`
  (catorce hechos del capítulo III del Manual de Hidrología y seis del
  capítulo 2 de WSDOT). Contados con `--collect-only -m pdf` son **76**
  sobre el árbol de T-1 y eran 56 sobre `7fb7926`, uno más que el 55 de la
  frase anterior: la diferencia es de antes de T-1 y no se rastreó. T-5 sumó
  **veintiocho** (trece en `tests/test_t5_estructural_conducto.py` y quince
  en `tests/test_t5_correcciones_auditoria.py`, que fijan en su página los
  números y las frases de AASHTO LRFD, el Manual de Puentes y el EG-2013 en
  que se apoya la Fase 8): son **104** sobre el árbol de T-5. Ninguno abre
  HEC-14 ni WSDOT, de modo que el eje de `NORMAS_DIR` no se mueve. Las
  correcciones de T-8 sumaron **uno** en `tests/test_t8_correcciones.py` (las
  llamadas de las Tablas 511-02 y 511-06 del EG-2013, que está en `normas/`
  de la app): son **105**, contados con `--collect-only -m pdf` sobre su
  árbol. T-9 sumó **siete** (cinco en `tests/test_t9_espaciamiento.py` y dos
  en `tests/test_t9_correcciones.py`, que fijan en su página las citas y las
  Tablas Nº 02, 32, 33, 34 y 304.12 del Manual de Hidrología y el núm. 304.11
  del DG-2018, los dos en `normas/` de la app): son **112**. T-7b sumó
  **doce** en `tests/test_t7b_cabezal_estabilidad.py` (las tablas de AASHTO
  LRFD que el ensamble transcribe, contra su página, y los literales de las
  ocho citas de sus correcciones, todas en `normas/` de la app): son **124**.
  T-7c sumó **veintiuno** en `tests/test_t7c_cabezal_armado.py` (AASHTO LRFD
  y E.060, en `normas/` de la app): son **145** sobre el árbol de T-10, que
  no sumó ninguno, como la verificación de fórmulas de T-7. T-11 sumó
  **cinco** en `tests/test_t11_validacion_externa.py` (las cifras de los
  ejemplos resueltos de HEC-14 que T-8 usó como oráculo, buscadas en su
  página; HEC-14 vive SÓLO en el repositorio de normas, de modo que saltan
  también sin `NORMAS_DIR`): son **150**, contados con `--collect-only -m pdf`
  sobre el árbol de T-11.

**No basta con que el intérprete de la suite tenga tkinter**, y conviene
decirlo porque invita al error contrario: el test de ventana sondea primero
`sys.executable` y después los intérpretes del sistema, de modo que un
`1949 passed` **no** demuestra que la suite corra sobre un Python con tkinter
—solo que alguno lo tenía—. Es exactamente lo que pasa hoy en el contenedor de
desarrollo, donde el intérprete de la suite no tiene tkinter y el test corre
igual, en un subproceso, sobre `python3.12`.

Son **cuatro** configuraciones y no dos, porque PyMuPDF y tkinter son
independientes. **T-12 de la cadena T (2026-11-13, integrado detrás de T-11,
con las correcciones de su auditoría), el último prompt de la cadena, PARTIÓ
la suite en dos**: la del ENTREGABLE (`python -m pytest` desde la raíz, que
por `testpaths` recoge sólo `tests/`) pasa de 6469 a **6425** `collected`, y
la de PROCESO (`python -m pytest proceso/tests`, con su propio
`conftest.py`) nace con **145**. Salieron de la primera, sin reescribirse,
**138** tests que leen material de proceso: los 119 de
`test_ext11_cruce_temarios`, los 16 de los bloques 1 y 6 de
`test_t0_gobernanza` con su test de `verificar_sesion` (hoy
`proceso/tests/test_t0_gobernanza_proceso.py`), el de las veintidós fichas de
la auditoría de sistema y los dos anclajes (EXT-11-03, T0-04) cuyo símbolo se
fue con ellos. Entraron **94** en el entregable —los 88 de
`tests/test_t12_entregable.py` (61 de la FASE A y 27 de las correcciones) y
los seis anclajes de `test_decisiones_diferidas` para las fichas T12-01 y
T12-03 a T12-07 de la Parte LV— y **siete** en proceso —los seis de
`proceso/tests/test_t12_proceso.py` y el anclaje de T12-02—: 6469 − 138 + 94
= 6425, 138 + 7 = 145, y las dos suites suman 6570 = 6469 + 101. Ninguno de
los 101 lleva la marca `pdf` (siguen 150) ni depende de Tk. **T-12 no cambia
cálculo** (`src/modulos/` sólo cambia en la plomería de reporte de M11, sin
aritmética): retiró los dieciocho PDF de `normas/` después de comprobar su
sha1 contra el repositorio de normas, de modo que `NORMAS_DIR` es la única
vía y **sin él salta TODO test que abre un PDF** —152 más que con
él, donde hasta T-11 eran veintitrés: los 150 `pdf`, con un solo motivo
(`conftest.pytest_runtest_setup`), la mitad de PC-23 que mira el repositorio
enlazado y el sha1 de los dos PDF censados—; movió con `git mv` el material
de proceso a `proceso/` —esta bitácora, que hasta aquí era la sección
«Cierre de tarea» de `CLAUDE.md`, entre él—; rotuló los fixtures; puso
`LICENSE` (todos los derechos reservados), `pyproject.toml` y el README de
usuario; dejó el manifiesto del registro en su estado final; y, por decisión
del dueño, entrega la memoria en dos vistas de la misma corrida —la resumida
para imprimir (`--html-resumida`, `--pdf-resumida`) y la completa como
anexo— y lleva T11-09 a la fila «Control gobernante». **La auditoría
adversarial (AJUSTADO: 1 ALTA, 4 MEDIA, 3 BAJA) se aplicó entera**: (H1,
ALTA) la suite del entregable no pasaba sobre una EXPORTACIÓN —2 failed sobre
`git archive` del árbol de la FASE A—: la exención de `proceso` de
`test_sin_literales` no caduca donde la exportación no lo lleva
(`AUSENTES_EN_UNA_EXPORTACION`), el arnés de mutación se salta sin `.git`, y
lo fijan un censo de lo que invoca git y la corrida de esos tests sobre una
exportación emulada; (H2) la resumida marca en texto la adopción sobre vacío
verificado (`M11.MARCA_VACIO_VERIFICADO`); (H3) lleva el corredor, su
advertencia y los [S] con su origen (`M11.datos_sitio_resumidos`); (H4) esta
bitácora se puede actualizar sin perder texto histórico —el test exige sus
palabras en orden, con las cifras libres— y `proceso.verificar_sesion` corre
`proceso/tests`; (H5) `hoja_de_ruta_correcciones_v12.md` y
`auditoria_y_ruta_despliegue_v9.md`, con prompts literales y asignación de
modelos de IA, pasaron a `proceso/`; (H6) la fila «h_o fuera de rango» llega
a las dos vistas (`M11._filas_h_o`); (H7) identidad de filas entre las vistas
y un solo formateador del estado del expediente
(`M11.estado_del_expediente`); (H8) los textos que habían quedado falsos, y
la resumida nombra la completa que de verdad se escribió. **No se escribió
en rojo primero**: el de la FASE A se midió contra `f77c5d4` (26 failed y 32
errores), y el de las correcciones con los dos archivos finales
(`tests/test_t12_entregable.py` y `proceso/tests/test_t12_proceso.py`)
contra la FASE A, `78a7780`: 29 rojos y 65 verdes de sus 94 (los verdes son
los de la FASE A que no cambian y guardias). Se reescribieron, declarándolo,
`test_t0_gobernanza`, `test_ext6_registro_normativo` (PC-23: la app no
versiona ningún PDF), `test_sin_literales`, `test_decisiones_diferidas`,
`test_ext11_mutacion` y `test_normativa_pdf`. Censos sin mover: 141
criterios y 20 sin valor, 507 citas, 150 tests `pdf`, ninguna marca
`literal-ok` nueva en `src/` y los techos de `test_ext8` sin tocar. Cierra
`INF-5.2.2` e `INF-5.2.3` con salvedad, `INF-5.2.4` e `INF-5.2.7`,
`INF-5.2.6` en parte, y deja una NOTA en `INF-5.2.1`. **La línea base de la
Familia C se regeneró y se midió contra `f77c5d4` con el comparador de
E-B**: los cuatro JSON IGUALES, los dos CSV y cuatro de los cinco `cli_*.txt`
idénticos byte a byte; las cuatro memorias completas cambian sólo por el
rótulo de fixture que les pone el generador y, en
`memoria_perfil_ancha.html`, por la cadena de T11-09 de A-02;
`cli_expediente.txt` gana la línea de la memoria resumida, que es archivo
nuevo; **ningún diámetro, sección, material ni HW se movió**. De las
configuraciones se MIDIERON TRES, todas en «sí · no» y sobre el commit que
entró en `main`: el entregable con el repositorio de normas enlazado,
6402 passed, 23 skipped, collected 6425; sin `NORMAS_DIR`, sobre el
mismo árbol, 6250 passed, 175 skipped; y sobre una EXPORTACIÓN
(`git archive HEAD`, sin `proceso/` ni `.git`) con `NORMAS_DIR`, 6398
passed, 27 skipped, 0 failed —los cuatro saltos de más son los tests que
leen lo versionado o necesitan `.git`: el arnés de mutación de
`test_ext11_mutacion`, la mitad de PC-23 de `test_ext6_registro_normativo`
(`git ls-files`) y, en `test_t12_entregable`, el de `git check-attr` y el de
la exportación emulada, cada uno diciendo por qué—. La suite de proceso:
145 passed con `NORMAS_DIR` y 145 sin él. **Las otras tres
filas de la tabla se dicen como derivadas, no como medidas**: la derivación
resta 44 a las de T-11 y no pasa ninguno a `skipped`.
**T-11 de la cadena T (2026-11-13, integrado detrás de T-10,
con la corrección del defecto T11-03 y las de su auditoría) sumó CIENTO NUEVE
tests netos**, cinco con la marca `pdf` (abren HEC-14, que vive sólo en el
repositorio de normas) y ninguno dependiente de Tk. **T-11 VALIDA y no cambia
cálculo**: corre el fixture de punta a punta a `--alcance expediente` con un
juego de DATOS DE PRUEBA que entra SÓLO por las puertas de la CLI
(`tests/fixtures/juego_validacion_integral.py`; ningún valor de prueba en los
tres archivos de valores, y un test lo fija), y **genera cuatro documentos con
su test de sincronía**: `docs/validacion_integral.md` (la corrida TITULAR con
las decisiones de ARCHIVO —el juego pisa `drenaje_trasdos` y
`factor_muro_eleccion`, que el dueño confirmó, y eso se presenta como
variante—: los cuatro puntos llegan a la Fase 11 con diseño, A-01, A-02 y B-01
concreto Ø 0.90 y C-01 marco 1.20 × 0.90; el cabezal de la regla no pasa las
tres filas estáticas del marco LRFD en los ocho cabezales y la sísmica es
«método no evaluable», T7B-05; la corrida sin juego, cada bloqueo en una de
tres clases; quitar una entrada a la vez sobre DOS bases; trece variantes; y
la lista exacta de lo que sigue requiriendo entrada, que la §7 de
`docs/contrato_entradas.md` repite —veintiuna, ADEMÁS de las columnas
obligatorias, y las condicionales que ninguna base dispara, nombradas—),
`docs/validacion_hds5.md` (HDS-5 DG1 y cinco ejemplos de HEC-14 contra su
página), `docs/validacion_hy8.md` (el procedimiento para que el autor corra
HY-8, sin afirmar ningún resultado, con la tolerancia que el dueño ACEPTÓ el
2026-11-13 como criterio del proyecto NO normativo: ≤ 3 % coincide, 3–10 % se
explica, > 10 % discrepancia, sobre HW y HW/D, control distinto → explicar,
velocidad sin veredicto donde no sale del mismo modo, versión y fecha de HY-8
obligatorias) y `docs/validacion_sensibilidad.md` (82 barridos de PF-3 sobre
80 criterios, la lista DERIVADA del censo —todo criterio con valor efectivo y
ventana legible por máquina— y los otros 61 por nombre con su razón; diez
criterios mueven el diseño dentro de su ventana). La tercera corrida de
referencia del índice de fórmulas es la hidrología calculada (ficha T10-02).
**Lo que T-11 corrigió del programa, todo de diagnóstico o de formato**: (T11-03)
el escalón que no cabe bajo la subrasante es «no factible POR RASANTE» con el
delta de 7.A cuando es geometría pura, y el dato inválido del punto que levanta
la Fase 5 sale con su campo (las dos reglas, en «Excepciones»); (H9, decisión
del dueño) `diseno.HW_salida_m` del JSON es `null` donde el control de salida
no se forma y la línea «Control» de la CLI lo dice (`cli.salida_no_se_forma`);
(H10) la fila A7 del armado sale «no aplica» con su razón cuando E.060 no fija
f'c mínimo; (H8) la columna «Tipo de cabezal» del cuadro resumen sale del punto
(`M11.tipo_cabezal_del_punto`) y no de la decisión 2.3 de la hoja de ruta.
**La auditoría adversarial (AJUSTADO: 1 ALTA, 6 MEDIA, 7 BAJA, ninguna de
fórmula ni de cita) se aplicó entera**: (H1, ALTA) la lista exacta medida sólo
sobre el juego no veía el peso específico saturado del relleno, que con el
`drenaje_trasdos` de archivo detiene 24 etapas, y la §7 contradecía a la §3.3;
(H2) el titular es el de los valores de archivo; (H3) los barridos se derivan
del censo y «leído, sin efecto medible» compara material, sección, veredictos y
el HW con tolerancia nombrada, no las demás magnitudes; (H5) el procedimiento
de HY-8, ejecutable y con las cinco reglas fijadas por test; (H6) el criterio
`v_max_concreto_eleccion` se queda SIN valor por decisión del dueño y su
resultado (3.0 m/s: A-01 a TMC Ø 1.20) depende de `suelo_agresivo_lrfd_sobre_tmc`
—con 'excluye' A-01 se detiene en el dato del fabricante del HDPE—, y la línea
de los sulfatos dice que son insignificantes para el concreto (E.060 Tabla 4.4,
pág. impresa 38) y agresivos para el acero galvanizado (AASHTO LRFD
11.10.6.4.2a, pág. impresa 11-89); (H7) el TW de C-01 es el tirante normal del
canal del juego (0.41 m) y la variante con la entrada en el canal empalma sin
mover el marco; (H11 a H14) el censo del §6 con su consumidor, `TW_receptor`
descrito como el código lo hace (el docstring de `servicio._resolver_tw` decía
que mandaba sobre las vías 3 y 4), `SIN_CONSUMIDOR_Y_SIN_MEDIDA` con siete y no
ocho, textos falsos, porcentajes con dos decimales y tolerancia de frontera
nombrada (el censo de HEC-14 queda vacío: el −1 % del apron caía fuera por
1e-17), aserciones que dicen lo que su nombre dice, la marca `lento` sólo en el
test que lanza un subproceso, y la cadena «caudal calculado → diseño» dicha
como NO validada con datos coherentes (lote posterior). Los 109: 31 de
`tests/test_t11_validacion_integral.py`, 20 de
`tests/test_t11_validacion_externa.py` (cinco `pdf`), 9 de
`tests/test_t11_sensibilidad.py`, 29 de `tests/test_t11_no_factible_por_rasante.py`,
10 de `tests/test_t11_correcciones.py` y los diez anclajes de
`test_decisiones_diferidas` para las fichas de la Parte LIV (T11-01..10). **No
se escribieron en rojo primero**: el de la FASE A se midió contra `14f6138` (8
rojos), el de T11-03 contra `c774035` (23 rojos de 29) y el de las correcciones,
con los cuatro archivos finales, contra `10fb84b` (28 fallos y 4 errores de 70).
Se reescribieron, declarándolo, `test_t10_memoria` (el alcance declarado pasa de
cinco a siete entradas), `test_MD` (docstrings), `test_M11_reporte` (la columna
del cabezal), `test_t8_correcciones` y `test_t8_proteccion` (la firma de
`fila_resumen`), `test_nivel_medido` (el «nueve» de su docstring), las causas
de `CP_HDS5_DG1` (dos decimales) y `test_t0_gobernanza` (la fila de T-11).
Censos sin mover: 141 criterios y 20 sin valor, 507 citas, ningún fundamento
ni marca `literal-ok` nueva; los techos de `test_ext8` se remidieron y no se
mueven (107.05 KB y 30.3 páginas por punto). Cierra `INF-0.5` CON SALVEDAD
escrita en su fila (a expediente siguen deteniendo, por decisión del dueño,
`remanso_derecho_via`, `TR_evento_extremo`, `umbral_no_colapso_evento_extremo` y
`categoria_refuerzo_aashto`), `INF-3.4.3` e `INF-3.4.6` (que T-7b construyó y
T-11 verificó) e `INF-3.4.4` en parte (E4 y E5 sin evaluar, Meyerhof en talud
vacío, la zapata sin iterar), y deja una NOTA en `INF-3.2.2` (falta la corrida
de HY-8 del autor) y en `INF-5.1.8`. **La línea base de la Familia C se
regeneró y se midió contra `14f6138` con el comparador de E-B**:
`informe_expediente.json` e `informe_rama_error.json` IGUALES (el comparador no
mira `alcance.declarado`, que gana dos entradas); `informe_perfil_ancho.json` e
`informe_familia_c.json`, 4 diferencias y 0 no comparables —`HW_salida_m` de
A-02 a `null` (H9) y el mensaje y dos motivos de escalón de B-01 (T11-03)—; los
`cli_*.txt` con las dos líneas del alcance, los mensajes «no factible por
rasante» y la línea «Control» de A-02; los dos CSV de resumen y las tres
memorias con el tipo de cabezal del punto; **ningún diámetro, sección,
material ni HW que gobierna se movió**. De las cuatro configuraciones se MIDIÓ
UNA, «sí · no», con el repositorio de normas enlazado: 6446 passed, 23 skipped,
collected 6469 (y sin `NORMAS_DIR`, sobre el mismo árbol: 6423 passed, 46
skipped). **Las otras tres se dicen como derivadas, no como medidas**: la
derivación suma 109 a las de T-10 y pasa cinco a `skipped` en las dos columnas
sin PyMuPDF.
**T-10 de la cadena T (2026-11-13, integrado detrás de la
verificación de fórmulas de T-7, con las correcciones de su auditoría) sumó
CINCUENTA tests netos**, ninguno con la marca `pdf` ni dependiente de Tk ni del
repositorio de normas: los 43 de `tests/test_t10_memoria.py`, los ocho anclajes
de `test_decisiones_diferidas` para las fichas de la Parte LIII (T10-01..08), y
**menos uno** en `test_guardias_de_la_suite` (`M11_reporte.verificaciones_publicadas`
sale del censo `PUBLICAS_SIN_REFERENCIA_EN_TESTS`, porque un test ya la nombra).
**T-10 no calcula nada nuevo: la memoria imprime lo que la CLI y el JSON ya
publicaban**, medido con un CENSO de las dos corridas de referencia nuevas
—cada hoja numérica y de texto del JSON de cada punto dimensionado, buscada en
su bloque HTML— y fijado POR CLAVE. Lo que faltaba y entra: de la Fase 9 del
punto, la tabla de solicitaciones por elemento, la excentricidad de cada
combinación (`CombinacionDeEstabilidad.excentricidad_publicable`: la regla de
N > 0 vive en el dato, no en M11 ni en la CLI), el armado en tabla por sección
crítica y por elemento y posición, y los avisos del punto que su fase no
imprimía (`M11._avisos_que_faltan`, una vez: 40 de 47 en A-01 faltaban); la
Fase 9 del PROYECTO entera (`M11.bloque_cabezal_proyecto`: la cadena sísmica
eslabón por eslabón, K_AE y K_A, recubrimientos, cuantías, notas y bloqueos,
en tablas con la clave en la primera columna), que sólo estaba en la CLI y el
JSON; **V4b, V6 y V9 ganan `PasoDeMemoria`** con su fundamento (`F5.V4b` con
la cita nueva `HDS5_3ED.2.2.5d#AGENCIAS`, de carácter DEFINICIÓN —la banda
1.0–1.5 es práctica de agencias de EE. UU. y el tope sigue siendo el [A]
`HW_D_max`—, `F5.V6` y `F5.V9`; V9 no juzga cuando el tope es de catálogo o de
la progresión del marco) y `fundamentos.SIN_FUNDAMENTO` queda VACÍO; el paso
7.B.3b del reparto por extremo (`LongitudConducto.paso_reparto`, sin cita de
fórmula: HDS-5 2.2.4 b. es contexto y el álgebra es del proyecto,
`M7.NOTA_ALGEBRA_DE_LA_LONGITUD`); la nota del origen de la cota de entrada en
el dato (`CotaDeEntrada.nota`); **lo que el dueño decidió no hacer, como
ALCANCE en las tres vistas** (`modelos.ALCANCE_DECLARADO`: el armado del
marco, el cabezal paralelo, la zapata sin iterar, el DC del marco en V7 y las
Figuras 3.3 y 3.4 de HEC-14, cada una con su ficha y su símbolo); y el anexo
A.4 de sensibilidad, que imprime la ventana de cada [A] usado y NO recalcula
(el barrido sigue siendo PF-3). Lo repetido se quitó: un paso, una elección o
una nota IDÉNTICOS a uno ya impreso salen una vez y después como su línea y un
enlace (`M11._YaImpreso`), y los 50 pasos del armado que A-01 imprimía dos
veces salen una. **El índice de fórmulas se genera ahora con dos corridas que
SÍ dimensionan** (`indice_formulas.CORRIDAS_DE_REFERENCIA`, datos de PRUEBA en
`tests/fixtures/corridas_de_referencia/`): la fila 4.4 cita HDS-5 núm. 3.3.5 y
`test_dimensional_piloto` conserva su propia corrida, la antigua. **La
auditoría adversarial (AJUSTADO, 2 MEDIA y 5 BAJA) se aplicó entera**: (H1) el
censo buscaba cada número en todo el bloque del punto —«0.40» sale 99 veces en
A-01— y cuatro mutantes vivían: ahora cada entrada del armado, de sus
secciones, de las combinaciones y de las solicitaciones se compara con SU
fila; (H2) el 7.B.3b sin la cita de fórmula; (H3) los dos tests que el
`SIN_FUNDAMENTO` vacío dejó vacuos se ejercitan con una entrada de prueba;
(H4) los docstrings que seguían diciendo «V4b no emite paso»; (H5) V4b sin
«que es más exigente», el rótulo de la frase del anexo según el CARÁCTER de la
cita (`M11.ROTULO_DE_LA_FRASE_POR_CARACTER`: una DEFINICIÓN «describe») y la
elección de V4b impresa como ventana; (H6) la V8 acotada de
`test_t7_verificacion` con su aviso UNA vez en la memoria; (H7) el 0.8·f_r y
el piso de 25.4 mm leídos de sus constantes. Los cinco mutantes de la
auditoría mueren. **Tres decisiones del dueño (2026-11-13)**: los techos
remedidos de `test_ext8` se ACEPTAN —`KB_POR_PUNTO_MAX` 114.5 → **107.5** y
`PAGINAS_POR_PUNTO_MAX` 33 → **31.5**, pegados a 107.04 KB y 31.00 páginas por
punto: BAJAN aunque la memoria imprime más, porque se quitó lo repetido; el
objetivo de EXT-8 sigue sin alcanzarse (ficha T10-01)—; V9 sin veredicto con
tope de catálogo o de marco, ACEPTADO (T10-03); y la tercera corrida de
referencia, con la hidrología de prueba, la hace T-11 (T10-02). **No se
escribió en rojo primero**: el rojo se midió con el archivo de la FASE A
contra `2265d90` (31 de 33 rojos y 2 guardias), y los diez tests de las
correcciones se comprobaron matando los mutantes de la auditoría sobre una
copia del árbol (ficha T10-07). Se reescribieron, declarándolo,
`test_M5_verificaciones` (V4b tiene paso), `test_memoria_sustentada` (el
censo vacío), `test_traza_punto` y `test_indice_formulas` (el hueco por una
entrada de prueba), `test_t6_geometria` (el 7.B.3b), `test_dimensional_piloto`
(su corrida), `test_ext8_rendimiento_gui` (los techos) y `test_t0_gobernanza`
(la fila de T-10). Censos: 141 criterios y 20 sin valor sin mover, citas del
registro de 506 a **507**, tres fundamentos nuevos, ninguna marca
`literal-ok` nueva. Cierra `INF-3.4.7` e `INF-4.7` (éste con la salvedad de su
fila: el programa no produce planos a los que remitir), y deja una NOTA en
`INF-5.1.10`, que cerró T-0 y que el prompt llama «INF-5.1.9» (el canónico
`INF-5.1.9`, `sucs_fundacion`, no se tocó). **La línea base de la Familia C se
regeneró y se midió contra `2265d90` con el comparador de E-B**: los cuatro
JSON ganan `alcance.declarado`; `informe_expediente.json` e
`informe_rama_error.json` IGUALES; `informe_familia_c.json` 8 diferencias e
`informe_perfil_ancho.json` 6, todas el `veredicto` de V4b, V6 y V9 de `null`
a `'cumple'`; 0 no comparables; los cinco `cli_*.txt` ganan las cinco líneas
del alcance; las tres memorias cambian de formato; la memoria del cajón y los
dos CSV de resumen no cambian un byte; **ningún diámetro, sección, material ni
HW se movió**. De las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el
repositorio de normas enlazado: 6337 passed, 23 skipped, collected 6360 (y
sin `NORMAS_DIR`, sobre el mismo árbol: 6319 passed, 41 skipped). **Las otras
tres se dicen como derivadas, no como medidas**, por lo mismo que en T-0: la
derivación suma 50 a las de la verificación de fórmulas de T-7, y ninguno pasa
a `skipped`.
**La verificación de las fórmulas de los cierres de T-7b y
T-7c (2026-11-13, integrada detrás de T-7c) sumó TREINTA Y CUATRO tests**,
ninguno con la marca `pdf` ni dependiente de Tk ni del repositorio de normas:
los 28 de `tests/test_t7_verificacion.py`, los cuatro anclajes de
`test_decisiones_diferidas` para las fichas de la Parte LII (T7V-01..04) y los
dos que crecen solos en `test_ext5_forma_gui` con los dos criterios nuevos. Un
verificador recalculó a mano y contra el PDF las fórmulas del cabezal y de V5
y V8: **AJUSTADO**, seis puntos conformes —que no se tocaron— y tres con
defecto, que esta pasada corrige. **(Punto 3, MEDIA, lado inseguro) V8 con el
caudal que no cabe en flujo uniforme**: `M4.hidraulica_a_presion` comparaba la
aproximación de barril lleno **sin** las dos reglas del HDS-5 núm. 3.3.3 (pág.
impresa 3.24) que `resolver_control` aplica desde E-A, y un caudal mayor podía
dar menos carga que uno menor (tubo de A-01, S 0.003, L 60 m, TW 0: 0.957 m
con 1.021 m³/s frente a 0.965 m con 0.987 m³/s). Ahora compite con el perfil
de la lámina (`perfil_lamina` no necesita tirante normal): bajo 1.2 D la
mayor de la aproximación y del remanso, bajo 0.75 D el remanso —**aviso
expreso y no «método no evaluable»**: la fuente dice que la aproximación
«should not be used» y dice también qué hacer, el cálculo de remanso que M4
tiene—; el control da 0.989 m. Y `M5.v8_evento_extremo` lleva la guardia
HW_ext ≥ HW de diseño: si no se cumple, juzga con la de diseño y lo avisa por
`Verificacion.avisos`, campo nuevo que `InformePunto.avisos()` recoge. **Lo
que quedó medido y sin corregir**: la regla de E-A tiene un escalón propio
donde la aproximación cruza HW/D = 1.2 (11 mm entre dos caudales en lámina
libre); es de `resolver_control`, conforme en la verificación, y para V8 lo
cubre la guardia (ficha T7V-01). **(Punto 9, MEDIA) el η de AASHTO LRFD
1.3.2.1 entra en el cabezal**, que usaba 1.00 implícito junto a un conducto
con η_I = 1.05: `M9.modificador_de_carga` arma η = η_D·η_R·η_I y las
combinaciones de Resistencia I lo llevan dentro de cada factor —η_i ≥ 0.95 en
las cargas de γ máximo, 1/η ≤ 1.0 en las de γ mínimo (DC y EV de la
combinación de mínimos), 1.00 en el Evento Extremo I y en Servicio—, en la
estabilidad LRFD y en el armado; el marco ASD de E.050 y el contraste de E.060
no lo llevan. **η_I es uno, el del cruce**: la misma clave
`eta_importancia_operativa_conducto` [A] que lee la Fase 8 (su concepto dice
ahora que rige el cruce; el nombre se conserva); η_D y η_R son dos [A] nuevos
del cabezal (`eta_ductilidad_cabezal`, `eta_redundancia_cabezal`, 1.00
convencional por 1.3.3 y 1.3.4, ventana 0.95–1.05), porque el 1.00 del
conducto sale de 12.5.4 y no alcanza al cabezal. WA y LS, de factor único, se
leen como cargas de γ máximo en las dos combinaciones (`Interpretacion` de la
cita). En el muro de tanteo η **cambia el veredicto** del deslizamiento LRFD
(37.177 > 37.156 kN/m; con 1.00 cumplía). Cierra la ficha T7C-11. **(Punto 7,
BAJA) el piso de la zapata armada**: `M9.peralte_minimo_zapata` daba 0.30 +
0.070 = 0.37 m, con el que la fila A8 —al eje de la barra, con el
recubrimiento con que se arma— no podía cumplir E.060 15.7 en ningún cabezal
de regla; ahora es 300 mm + ese recubrimiento + medio diámetro de la mayor
barra del catálogo (**0.4041 m** con la cota de 91.44 mm, 0.3827 m con 70 mm),
A8 cumple por construcción y sigue pudiendo fallar con una zapata declarada.
Y el matiz del punto 2: la nota de V5 por cota ya no llama «el nivel más
alto» al de la boca. **Dos cosas que conviene leer antes de tocar esos
tests:** (a) los dorados del muro de tanteo de T-7b y T-7c **no se rehicieron
uno a uno**: se calcularon con los factores de la tabla, y el fixture
`tanteo` de los dos archivos declara ahora η_I = 1.00 para que sigan fijando
la aritmética del ensamble; lo que η hace con el 1.05 de archivo lo fija a
mano `CP_T7V_ETA` (ficha T7V-02); (b) A-01 con los datos DE PRUEBA sí cambia
y se reescribió declarándolo: la zapata 0.37 → 0.4041 m, las doce filas E1 a
E3 del marco LRFD sin ningún cambio de veredicto (E3 estática 38.05 > 29.39 →
39.95 > 28.70 kN/m a la entrada y 57.93 > 49.13 → 60.83 > 47.90 a la salida),
A8 0.2722 → 0.3064 m (cumple), el talón de salida 71.72 → 75.45 kN·m/m (Ø 1/2"
@ 0.175 → @ 0.15) y la punta de salida @ 0.15 → @ 0.175. **No se escribió en
rojo primero**: el rojo se midió con el archivo final contra `2b13dc1` (26
rojos y 2 guardias); no se corrió mutación (ficha T7V-04). Se reescribieron,
declarándolo, `test_t7a_cabezal_geometria` y `test_t7a_correcciones` (el
piso), `test_t7b_cabezal_estabilidad` (el fixture, el apoyo de V8 que ahora
trae la carga de diseño, y la zapata de 3.00 m, cuyas 24 filas cumplen) y
`test_t7c_cabezal_armado` (el fixture, A8 y el armado de A-01). Censos: **141
criterios, 20 sin valor**, citas del registro de 503 a **506** (AASHTO 1.3.2.1,
1.3.3 y 1.3.4, leídas en sus páginas); ninguna marca `literal-ok` nueva. El
tracker no cambia ningún estado: `INF-4.2`, `INF-4.5` e `INF-4.6` ganan una
NOTA. **La línea base de la Familia C se regeneró y se midió contra `2b13dc1`
con el comparador de E-B**: una diferencia en cada uno de los cuatro JSON (la
huella `criterios_sha1`), 0 no comparables, y en las tres memorias las dos
huellas y el recuento «139 … 20» → «141 … 20»; ninguna corrida de la línea
base alcanza V8 ni la Fase 9; **ningún diámetro, sección, material ni HW se
movió**. De las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el
repositorio de normas enlazado: 6287 passed, 23 skipped, collected 6310 (y
sin `NORMAS_DIR`, sobre el mismo árbol: 6269 passed, 41 skipped). **Las otras
tres se dicen como derivadas, no como medidas**, por lo mismo que en T-0: la
derivación suma 34 a las de T-7c, y ninguno pasa a `skipped`.
**T-7c de la cadena T (2026-11-13, integrado detrás de T-7b, con las
correcciones de su auditoría) sumó DOSCIENTOS SETENTA Y CUATRO tests netos**, veintiuno
con la marca `pdf` (los números y las frases de AASHTO LRFD y de E.060 que el
armado toma, contra su página; los dos PDF en `normas/` de la app) y ninguno
dependiente de Tk ni del repositorio de normas: los 253 de
`tests/test_t7c_cabezal_armado.py` —la FASE A: **cada cabezal de voladizo
armado se ARMA** (`INF-4.6`; `M9.armar_elemento`, `M9.ensamblar_armado`,
`servicio._fase_9_armado`, detrás de la estabilidad y con la misma geometría,
sin iterarla) con AASHTO LRFD Sección 5 sobre las solicitaciones factoradas
del ensamble —flexión de 5.6.3.2 con el bloque de 5.6.2.2, cortante
simplificado de 5.7.3.4.1 donde la fuente lo permite y «método no evaluable»
fuera de él, φ de 5.5.4.2 y 1.0 en el Evento Extremo—, E.060 en paralelo como
contraste [N→] sin cruzar marcos, el mínimo más exigente de los dos, el empuje
en reposo de archivo (`regimen_resistencia_elementos_cabezal` [A] =
`no_cedente_k0`, decisión del dueño; la estabilidad externa sigue con el muro
que cede), la zapata con presión de contacto lineal (10.6.5) y el talón con el
peso entero (11.6.1.2), la ec. (11-32) de E.060 evaluada (cierra la ficha
`EXT-7-01`; los tres criterios de cortante en el plano dejan de estar vacíos),
la tabla de armado con la barra propuesta de un catálogo [A], y el cabezal de
gravedad verificado como concreto ciclópeo (C1 a C6)—, más la aceptación de
las **correcciones de la auditoría adversarial** (AJUSTADO: 2 ALTA, 5 MEDIA, 5
BAJA; la cuña de tanteo de T-7b, APROBADA) y de las resoluciones del
orquestador: (H1) la pantalla y el alero integran **cada diagrama de empuje
por encima del arranque** (`M9.empujes_sobre_el_arranque`, código de T-7b): la
resultante entera con su brazo desde el arranque, que el docstring llamaba
«del lado seguro», no lo era para el momento (−8.5 % en el muro de tanteo);
la inercia es la de la pantalla sola y el incremento sísmico se reparte con
el único diagrama lineal que tiene su resultante a 0.6·h; (H2) con el muro que
no cede **el Evento Extremo I del armado va con k_h = 1.0·k_h0** (AASHTO
11.6.5.4, «shall be increased to 1.0kh0») por una puerta de `k_h` en
`M9.cargas_del_cabezal` que la estabilidad no usa —en A-01 con los datos de
prueba la pantalla de salida pasa de Ø 1/2" @ 0.10 a Ø 5/8" @ 0.10—; (H3) **la
fisuración de AASHTO 5.6.7** en Servicio I (fila A6, `M9.fisuracion_aashto`),
con la clase de exposición como [A] **sin valor** del Propietario
(`clase_exposicion_fisuracion_cabezal`): sin declararla, la barra propuesta
respeta la Clase 1 y A6 sale «no decidida» cuando no cumple la 2; (H4) la
altura de la zapata sobre su refuerzo inferior frente a los 300 mm de E.060
15.7 con el recubrimiento con que se arma (fila A8: la zapata de 0.37 m de la
regla de T-7a **no cumple** con la cota de 91.4 mm, y no se itera); (H5) el
arranque del cuerpo ciclópeo es una **junta de construcción** y E.060 22.4.7
prohíbe la tracción por ella: C2 decide siempre, con la mayor de la
excentricidad de servicio y la amplificada, salvo vaciado monolítico
declarado (`junta_arranque_cabezal_ciclopeo` [A]), y C6 aplica la
excentricidad mínima de 22.6.3; (H6) el vano, la losa de entrega y el
dentellón, nombrados en lo que el armado no cubre; (H7) la fila A7 del f'c por
durabilidad y los textos que nombraban A6, A5 y R4/R5; (H8) d_v acotado al
peralte efectivo (`Interpretacion` de 5.7.2.8) y A2 como INDICADOR cuando la
pantalla pasa de 0.5·φ·V_c; (H9–H12) el aviso del reposo de mínimos que
vuelca, el K0 con talud impreso sin adoptar, los dos mutantes vivos con test,
el sufijo `_SI` y `RECUBRIMIENTO_BARRA_GRUESA_DESDE` en
`constantes_normativas`; y la pregunta 1: el 0.30 m de E.060 22.7.4 pasa de
constante [N] al criterio [N→] `espesor_min_zapata_concreto_simple_m` (las
cuantías de 14.3.1 no se movieron: ficha T7C-10). **El modificador de carga η
de AASHTO 1.3.2.1 no se aplicó al cabezal**: la fuente lo sostiene, pero
reescribe más de veinte dorados de T-7b ya integrados (medido; ficha T7C-11).
Los otros: los trece anclajes de `test_decisiones_diferidas` para las fichas
de la Parte LI (T7C-01..13); diez que crecen solos en `test_ext5_forma_gui`
con los diez criterios nuevos; y **menos dos** en `test_criterios_adoptados`
(tres de cortante en el plano dejan el parametrizado de vacíos y entra la
clase de exposición). **No se escribieron en rojo primero**: el rojo de la
FASE A es de recolección contra `451a10a`, y el archivo final contra la FASE A
(`f50edbe`) da 60 rojos y 189 verdes; la mutación de la FASE A dejó 843 de
1007 muertos y la del cierre, sobre las 23 funciones que tocó, 810 de 1012
(80.0 %: 777 en la primera vuelta con los tests rápidos, 19 con los dos
archivos enteros y 14 en dos vueltas parciales con los cuatro tests de «lo
que la mutación del cierre enseñó»: la fila A6 por dentro, la inercia de la
pantalla con un brazo distinto de 1 m, el aviso del d_v acotado y los números
de A8 y del paso del régimen); de los 202 vivos, 61 son fronteras de un umbral
con tolerancia, 84 constantes de relleno o de presentación, 16 guardias y
empates, 5 textos y 36 ramas que ningún dato válido alcanza o huecos que la
FASE A ya había nombrado (ficha T7C-08). Los
dorados están a mano en `CP_T7C_ARMADO` (rehecho con H1 y H8: activo 26.491 /
21.466 y reposo 43.502 / 35.402 kN y kN·m por metro en el muro de tanteo),
`CP_T7C_CICLOPEO` y el de la fisuración (el control del auditor: 0.147 y 0.061
m). Censos: **139 criterios, 20 sin valor**, citas del registro de 454 a
**503**, `M9` con 16 marcas `literal-ok`. Se reescribieron, declarándolo,
`test_M9_cabezal`, `test_ext7_cabezal`, `test_t7b_cabezal_estabilidad` (la
solicitación de la pantalla, H1), `test_t7a_cabezal_geometria` (el 0.30 m),
`test_memoria_sustentada` (trece fundamentos `F9.ARM_*` y `F9.CICLOPEO` que la
corrida por defecto no alcanza), `test_sin_literales` y `test_t0_gobernanza`
(la fila de T-7c). Cierra `INF-4.6` e `INF-3.4.5` con residuales nombrados
(fichas T7C-03, -04, -06, -09 y -11), y escribe una NOTA en `INF-0.5`,
`EXT-M-05`, `R95-031` e `INF-4.3`. **La línea base de la Familia C se
regeneró y se midió contra `451a10a` con el comparador de E-B**: 4, 2, 2 y 2
diferencias en los cuatro JSON —huella, recuento de criterios sin valor y dos
notas del cabezal del proyecto—, 0 no comparables; ninguna corrida de la línea
base alcanza el armado; **ningún diámetro, sección, material ni HW se movió**,
y las filas E1 a E3 de A-01 con los datos de prueba son idénticas a las de la
FASE A. Los techos de `test_ext8` no se remidieron porque la memoria de
referencia no cambia de tamaño. De las cuatro configuraciones se MIDIÓ UNA,
«sí · no», con el repositorio de normas enlazado: 6253 passed, 23 skipped, collected
6276 (y sin `NORMAS_DIR`, sobre el mismo árbol: 6235 passed, 41 skipped). **Las otras tres se dicen como
derivadas, no como medidas**, por lo mismo que en T-0: la derivación suma 274
a las de T-7b y pasa veintiuno a `skipped` en las dos columnas sin PyMuPDF.
**T-7b de la cadena T (2026-11-13, integrado detrás de T-7a, con las
correcciones de su auditoría) sumó DOSCIENTOS NOVENTA Y TRES tests netos**, doce con
la marca `pdf` (las tablas y las citas de AASHTO LRFD, HDS-5 y E.050 que el
ensamble toma, contra su página; todas en `normas/` de la app) y ninguno
dependiente de Tk ni del repositorio de normas: los 272 de
`tests/test_t7b_cabezal_estabilidad.py` —la FASE A: **el cabezal de cada
extremo de cada punto dimensionado se verifica en DOS MARCOS que no se
cruzan** (`INF-4.4`, `INF-4.5`, `INF-5.1.5`; `M9.ensamble_estabilidad`, una
etapa por cabezal y condición en `servicio._fase_9`): rige el LRFD de AASHTO
11.6 —cargas factoradas contra resistencias minoradas, la excentricidad en
lugar del volteo, φ de la fila que declara `fila_phi_estabilidad_cabezal`
[A] y 0.8 / 1.0 del 11.5.8 bajo sismo— y el ASD de E.050 `[N→]` se calcula
en paralelo sobre cargas de servicio e INFORMA (`marco_estabilidad_cabezal`
[A] = `lrfd_rige_asd_informa`, decisión del dueño); las cargas sin factorar
con su brazo (`CargaDeCabezal`), el empuje DESCOMPUESTO sobre el plano
vertical del talón (cierra `EXT-7-04`), el agua una sola vez (suelo sumergido
más hidrostática), la sobrecarga por h_eq, la demanda sísmica en los dos
casos del 11.6.5.1 con la excentricidad sísmica como fila E2 (cierra
`EXT-7-02`, `gamma_EQ` [A] = 0.5), la capacidad portante de AASHTO
10.6.3.1.2a sobre B − 2e, E4 y E5 impresas como diferidas, y las
solicitaciones factoradas por elemento para T-7c; y el PUNTO 0 (decisión del
dueño): V5 y V8 con método **declarable sin valor de archivo** y sus datos por
punto como claves de `--datos-externos`—, más la aceptación de las
**correcciones de la auditoría adversarial** (AJUSTADO: 3 ALTA, 4 MEDIA, 3
BAJA; la aritmética del ensamble coincidía con AASHTO) y de las resoluciones
del orquestador: (H1) **el freático es una COTA** medida bajo el terreno del
CRUCE, como en M8 (`EntornoDelCabezal.cota_freatico` = `cota_terreno − NF`):
la FASE A lo medía bajo el pie de cada cabezal y dejaba la salida de A-01
seca con 0.20 m de agua sobre la base; (H2) **V5 por COTA**, el criterio que
el HDS-5 núm. 2.2.5 sí sostiene (`remanso_derecho_via` gana
`cota_de_afectacion`: cota de entrada + HW ≤ `cota_afectacion_aguas_arriba_msnm`,
dato externo nuevo, opcional, sin valor por defecto, que admite cero y signo),
y `embalse_a_nivel` conservado diciendo que mide hasta el fondo —incluye el
tramo natural del cauce y es una cota superior de lo que la obra añade—;
(H3) **V8 con el barril a presión** (`M4.hidraulica_a_presion`: las piezas de
M4 que no necesitan tirante normal, gobierna la mayor) y evaluada solo sobre
el candidato que ya cumple lo anterior; (H4) **la cuña de tanteo de
Culmann** con la superficie real del relleno, estática y pseudoestática, es
la regla de archivo de `regla_pendiente_relleno_trasdos` (AASHTO 3.11.5.3,
3.11.5.8.1 y C11.6.5.3; `M9.cuna_de_tanteo`), con Coulomb y Mononobe-Okabe
con la pendiente 2H de contraste y barribles —en A-01 la 2H subestima el
empuje estático del 7 al 11 %, y con el k_h de archivo la sísmica deja de
ser «no evaluable»—, dorados a mano en `CP_T7B_CUNA` (los dos límites
analíticos y cuatro cuñas escritas sobre una superficie quebrada); (H5) el
«cabezal de la regla no pasa» se presenta como sensible a la fila de φ y a
los factores de inclinación, y toda fila que cambia de veredicto dentro de
esas ventanas se avisa con las dos cifras (`M9._avisos_de_sensibilidad`); el
ancho de la zapata NO se itera (diferido); (H6) sin drenaje el agua llena el
relleno RETENIDO y nunca sube por encima del muro, y con drenaje se avisa el
desembalse rápido que el modelo no contempla; (H7) **`regimen_cabezal` [A] =
`cedente`** (la hipótesis de la estabilidad externa; `no_cedente` detiene con
«método no evaluable») y cada solicitación para T-7c lleva el coeficiente con
que salió y el K0 de referencia; (H8–H10) textos que decían lo contrario que
el código, `gamma_saturado_kn_m3` del suelo de fundación retirado, el aviso
del cabezal con una sola condición evaluada, el alero que supera la longitud
entre cabezales, y una aserción tautológica reescrita—; los catorce anclajes
de `test_decisiones_diferidas` para las fichas de la Parte L (T7B-01..14);
diez que crecen solos en `test_ext5_forma_gui` con los diez criterios nuevos; seis en `test_familias_del_csv` (las dos claves de V5 por familia: dos pasan y cuatro son saltos de DISEÑO, porque las Familias A y B usan las dos, y por eso esta columna salta ahora diez y no seis en las cuatro configuraciones); y uno en `test_nivel_medido` (el criterio de la verificación diferida que solo lee V8); **menos diez**: siete de `test_M9_cabezal` (cuatro vacíos de la Fase 9 dejaron de serlo) y tres de `test_criterios_adoptados` que salen del parametrizado de vacíos. **No se escribieron en rojo primero**: la FASE A midió 186 rojos y
16 verdes de sus 202 contra `250c972`, y los 61 tests de las correcciones
son rojos los 61 (51 F/E rápidos y 10 lentos) contra la FASE A (`fc792d9`); la
mutación de la FASE A con el arnés de EXT-11 dejó 715 de 833 en M9 y 78 de 82
en V5/V8 (ficha T7B-10), y el código del cierre no se mutó otra vez. Censos:
**129 criterios, 22 sin valor** (diez nuevos; `remanso_derecho_via`,
`TR_evento_extremo` y `umbral_no_colapso_evento_extremo` siguen vacíos a
propósito, con método detrás), `CLAVES_EXTERNAS` **veinticinco**, las citas
del registro pasan de 412 a **454**, `dominios.py` gana una marca
`literal-ok` (13). Se reescribieron, declarándolo, `test_M9_cabezal`,
`test_ext7_cabezal`, `test_t7a_correcciones`, `test_M5_verificaciones`,
`test_ext6_registro_normativo`, `test_memoria_sustentada`, `test_nivel_medido`,
`test_pf2_prevuelo` (el freático pasa de «espera» a «DETIENE» a expediente),
`test_guardias_de_la_suite`, `test_sin_literales`, `test_criterios_adoptados`,
`test_ext5_forma_gui`, `test_ayuda_entrada`, `test_familias_del_csv` y
`test_t0_gobernanza` (la fila de T-7b; las tres de T-7a que T-7b reescribe
salen de la suya). Cierra `INF-4.4`, `INF-4.5`, `INF-5.1.5`, `INF-4.1` e
`INF-4.2` —este con la salvedad escrita: la ruta real a la Fase 9 exige
declarar el método de V5 y su dato, el TR y el caudal del evento extremo y el
EMS, entradas del proyecto—, y `INF-4.3` **en parte** (el cabezal paralelo a
la vía para el marco, ficha T7A-03). **La línea base de la Familia C se
regeneró sobre el árbol fusionado y se midió contra `250c972` con el
comparador de E-B**: 27, 27, 31 y 3 diferencias en los cuatro JSON, todas de
texto, huella y recuento —la ficha de `remanso_derecho_via` es ahora el
método de V5, «119 criterios … 25 sin valor» → «129 … 22», la nota del empuje
bajo el freático, y a expediente la etapa «K_AE de Mononobe-Okabe (9.2)» del
proyecto desaparece (el K_AE es de cada cabezal): «Etapas bloqueadas» 10 →
9—; **ningún diámetro, sección, material ni HW se movió** (los bloques de
cálculo de cada punto son idénticos; los dos CSV de resumen,
`cli_rama_error.txt` y `memoria_punto_cajon.html`, byte a byte). Los techos de `test_ext8` no se remidieron porque la memoria de referencia no cambia de tamaño: sin declarar nada ninguna corrida alcanza la Fase 9 del punto, y el test pasa con los de T-7a. De
las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de
normas enlazado: 5979 passed, 23 skipped, collected 6002 (y sin `NORMAS_DIR`, sobre el mismo árbol:
5961 passed, 41 skipped). **Las otras tres se dicen como derivadas, no como medidas**, por
lo mismo que en T-0: la derivación suma 293 a las de T-7a, pasa cuatro
a `skipped` en las cuatro columnas (los de diseño de `test_familias_del_csv`)
y doce más en las dos sin PyMuPDF.
**T-7a de la cadena T (2026-11-13, integrado detrás de T-9,
con las correcciones de su auditoría) sumó CIENTO SESENTA Y UN tests netos**,
ninguno con la marca `pdf` ni dependiente de Tk ni del repositorio de normas:
los 67 de `tests/test_t7a_cabezal_geometria.py` —la FASE A: **la Fase 9 es POR
PUNTO** (`INF-5.1.15`): cada punto dimensionado tiene dos cabezales
(`InformePunto.cabezal`, `servicio._fase_9` detrás de la socavación de la Fase
6 y de la Fase 8, `M9.cabezal_del_punto`) con su sección, su HW, sus cotas de
7.B y su socavación (`ExtremoDelConducto`), y el proyecto conserva solo la suma
(`InformeCabezal.por_punto`; `geometria_adoptada` se retiró);
`predimensionamiento_cabezal` deja de ser un vacío y guarda trece reglas [A]
con ventana (`M9.predimensionar_cabezal`, cada dimensión con su origen:
«propuesta por regla», «declarada» por `cabezal_declarado` —dato externo
opcional fuera de `CLAVES_EXTERNAS`, en `servicio.CLAVES_DE_CABEZAL`, con forma
y dominio en `M9.validar_cabezal_declarado`— o «derivada de dimensiones
declaradas»); los aleros existen (`modelos.Aleros`,
`M9.predimensionar_aleros`); la embocadura es del punto y de perfil
(`embocadura_cabezal` y `angulo_aletas` [A], `M9.embocadura_del_punto`, antes
de la Fase 4) y en un marco la carta y el ke declarados tienen que ser de la
banda de ángulo del cabezal (`M9.verificar_coherencia_embocadura_cajon`; con
los de T-3 la coherencia se cumple para α de 30 a 60° y su nota es un dato,
no un aviso); y la compatibilidad con el conducto es una verificación—; los 84
de `tests/test_t7a_correcciones.py`, la aceptación de las **correcciones de la
auditoría adversarial** (AJUSTADO: 2 ALTA, 6 MEDIA, 2 BAJA) y de las
decisiones del dueño: (H1) **con esviaje los dos aleros miden distinto**, `L =
(h0 − H_f)·talud / cos(α ∓ θ)` —el talud baja perpendicular a la vía y α se
mide con la prolongación de la pared del barril, ΘW del HDS-5, List of
Symbols, pág. impresa xix (cita `HDS5_3ED.SIMBOLOS#THETA_W`; para que la regla
de paginación la prediga, `esquema.PorCapitulo` ganó `romanas`)—, con
`LimiteNumericoError` si α + θ ≥ 90° y un aviso del desnivel del talud a lo
largo del muro, Δz = L_c·sen θ/talud (en A-01, 2.425 y 4.200 m en la entrada
donde la FASE A daba 2.970 a los dos; el cabezal NORMAL AL EJE es el de
archivo en las tres familias por decisión del dueño, el paralelo a la vía
queda diferido solo para el marco, ficha T7A-03, y el alero largo se acorta
declarando `cabezal_declarado.angulo_alero_largo_grados`); (H2) **la decisión
4 del dueño no se aplicó**: abrir la puerta de `ancho_derecho_via_m` no hace
alcanzable la Fase 9 a expediente, porque V5 se detiene antes en
`remanso_derecho_via`, `M5.v5_remanso` no lee el dato y V8 se detiene en
`TR_evento_extremo` —medido; lo cierra T-7b, ficha T7A-01—; (H3) el dentellón
se mide desde el terreno del pie, la misma referencia del desplante, como la
cota «0.80 min.» de la Lámina Nº 04 releída por imagen (en la salida de A-01,
base a 40.50 y no a 41.187); (H4) CB6 (espesor de la zapata contra el mínimo
de su tipo) y CB7 (base del dentellón contra el terreno y la hoya); (H6) el
talud muere en el relleno retenido, coronación menos bordillo (13.486 m entre
cabezales en A-01, 14.086 m de metrado); (H7) el umbral del ciclópeo se mide
sobre la altura total y con D ≥ 0.90 m todo cabezal sale voladizo armado, y se
avisa; (H8) el 0.80 m de E.050 26.2 sale de `constantes_normativas` y es [N→]
(`profundidad_cimentacion_min_cabezal_m`: el ámbito de E.050 son las
edificaciones), con el rótulo [N] de la §0.1 de la v8 declarado como defecto
de la hoja; (dudoso 4) el piso de la zapata armada de E.060 15.7 (pág. 138),
[N→] (`peralte_min_zapata_armada_m`), más 70 mm de 7.7.1 (0.225 → 0.37 m en la
entrada de A-01); (H9, H10) el origen «derivada», los avisos con su causa, la
fórmula del proyecto sin una cita que no la contiene, la escala 3 de la Carta
12 sin banda, y ninguna frase que diga que «más material» es el lado seguro
(con kh = 0.50 empeora el deslizamiento sísmico); (decisión 3) cada punto de
la Familia B avisa que su entrada suele ser una caja receptora que el programa
no modela—; los ocho anclajes de `test_decisiones_diferidas` para las fichas
de la Parte XLIX (T7A-01..08) y cinco que crecen solos en
`test_ext5_forma_gui` con los cinco criterios nuevos; **menos tres**: uno de
`test_M9_cabezal` (la geometría única por criterio) y los dos de
`test_criterios_adoptados` que salen del parametrizado de vacíos
(`angulo_aletas` y `predimensionamiento_cabezal`). **No se escribieron en rojo
primero**: la FASE A midió 63 fallos y 3 errores de sus 66 contra `df1b23c`, y
la primera tanda de las correcciones, 47 rojos y 14 verdes —guardias— de 61
contra la FASE A (`1b83d39`); la mutación con el arnés de EXT-11 sobre las 17
funciones de la Fase 9 del punto pasó de 185/226 (FASE A) a 309/326 con la
segunda tanda, y uno más a mano (ficha T7A-07). Censos: **119 criterios, 25 sin
valor** (cinco nuevos, todos con valor; `angulo_aletas` y
`predimensionamiento_cabezal` dejan de estar vacíos), las citas del registro
pasan de 401 a **412**, `CLAVES_EXTERNAS` sigue en veintiuna, `dominios.py`
gana una marca `literal-ok` (`DIMENSION_CABEZAL_MAX_M`, 12), y `angulo_aletas`
sale de `SIN_CONSUMIDOR_Y_SIN_MEDIDA`. Se reescribieron, declarándolo,
`test_M9_cabezal`, `test_modelos` (talón sin declarar → `DatoFaltanteError`),
`test_cli`, `test_criterios_adoptados`, `test_ext5_forma_gui`,
`test_nivel_medido`, `test_variables_entrada`, `test_t8_proteccion` (la
embocadura de la entrada es la del punto), `test_memoria_sustentada` (siete
`F9.*` que la corrida por defecto no alcanza), `test_sin_literales`,
`test_normativa` (`E060.15.7#PERALTE` sin tildes en la fuente) y
`test_t0_gobernanza` (la fila de T-7a). Los techos de `test_ext8` se
remidieron sobre el árbol fusionado y no se mueven (113.96 KB y 32.3 páginas
por punto). Cierra `INF-5.1.15`, `INF-3.4.1` e `INF-3.4.2`, y **en parte**
`INF-4.2` e `INF-4.3` (ninguna corrida de expediente alcanza la Fase 9: T-7b)
e `INF-4.1` (los datos geotécnicos y sísmicos: T-7b). **La línea base de la
Familia C se regeneró sobre el árbol fusionado y se midió contra `c654a16` con
el comparador de E-B** en los cuatro JSON: huellas, recuentos de criterios, el
bloque `cabezal` del proyecto, la embocadura y la protección de entrada de los
puntos dimensionados (`cabezal_recto` → `cabezal_con_aleros`), el aviso de B-01
y «Etapas bloqueadas» 11 → 10; **ningún diámetro, sección, material ni HW se
movió** (el bloque `diseno` de cada punto es idéntico). De las cuatro
configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de normas
enlazado: 5690 passed, 19 skipped, collected 5709 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 5672 passed, 37 skipped). **Las otras tres se dicen como
derivadas, no como medidas**, por lo mismo que en T-0: la derivación suma 161
a las de T-9, y ninguno pasa a `skipped`.
**T-9 de la cadena T (2026-11-13, integrado detrás de T-3,
con las correcciones de su auditoría) sumó CIENTO NOVENTA Y SEIS tests**,
siete con la marca `pdf` (las citas y las Tablas Nº 02, 32, 33, 34 y 304.12
del Manual de Hidrología y el núm. 304.11 del DG-2018, los dos en `normas/` de
la app) y ninguno dependiente de Tk ni del repositorio de normas: los 82 de
`tests/test_t9_espaciamiento.py` —la FASE A: **la Fase 10 deja de cumplir por
construcción** (`INF-5.1.12`): el paso 10.1 es un límite sin veredicto, la
longitud por capacidad se CALCULA cuando no se declara (`INF-3.3.8`; la
declarada gana) con la capacidad de la cuneta triangular del Manual núm.
4.1.2.1 a) —Manning ec. (117), n = 1/K de la Tabla Nº 32, velocidad límite de
la Tabla Nº 33 por `revestimiento_cuneta` [A] = concreto y
`lectura_velocidad_limite_cuneta` [A] = extremo inferior—, y **VB1** juzga el
tramo de cuneta de cada alivio contra el espaciamiento máximo; tres datos
externos nuevos y opcionales de la Familia B (`ancho_tributario_m`,
`S_cuneta`, `inicio_tramo_cuneta_km`: `CLAVES_EXTERNAS` tiene veintiuna) y la
aceptación de la Familia B cableada (ficha T0-03)—; los 87 de
`tests/test_t9_correcciones.py`, la aceptación de las **correcciones de la
auditoría adversarial** (AJUSTADO, H1 a H11) y de las decisiones A a D del
dueño del 2026-11-12, más los 21 `test_mut_*` de la mutación de la
integración: (H1, ALTA) **VB2**, la condición literal del Manual («Q manning >
Q de aporte», pág. impresa 177, cita `MC_HHD.4.1.2.1a#CONDICION`), el caudal
del punto contra la capacidad de la cuneta, que puede fallar y entra a la
aceptación (V1 + V2 + V4 + V5 + VB1 + VB2); con el tramo conocido el aporte se
reparte como Q / s (L = Q_adm · s / Q, el equivalente exacto de la condición),
sin tramo se conserva q · b y se avisa la longitud que el área y el ancho
implican —el CUMPLE falso del auditor (Q_adm 0.052 m³/s contra 0.095 de
aporte, L = 8 244 m) da ahora VB2 y VB1 NO CUMPLE—; con `L_hidraulico_m`
declarado y sin `S_cuneta`, VB2 sólo avisa (decisión del dueño); (H2) un VB1
sin evaluar es un **bloqueo** del punto que espera el dato que lo destraba, y el
pre-vuelo lo estima; (H3) los huecos de cuneta que VB1 no mira se avisan, un
inicio de tramo posterior a la obra es `DatoInvalidoError` y ningún texto
supone el sentido del flujo; (H4 + D) se imprime el TR del PUNTO, y la fila del
alivio de la Tabla Nº 02 (R 35 %, n 15: T = 35.32 años) es una
**envolvente** de la del drenaje de la plataforma (T = 29.87) declarada como
`Interpretacion`; (H5 + A) `seccion_cuneta` tiene valor de archivo, el mínimo
de la Tabla Nº 34 para región muy lluviosa (0.40 × 1.20 m) con el talud
exterior 1:1 como elección [A] y borde libre 0, la ventana empieza ahí y el
talud interior se contrasta con la Tabla 304.12 (más empinado que 1:2 es
`DatoInvalidoError`; Z1 = 3 se avisa); (B) la v8 ya no pide «con borde libre»
sin cifra; (C) las obras de Familia A **cierran el tramo** por defecto
(`obras_familia_a_extremo_de_cuneta` [A] = `si`, `no` barrible; lectura del
DG-2018 núm. 304.11, cita `DG2018.304.11#DESAGUE` con su `Interpretacion`);
(H6 a H11) la ficha del revestimiento dice que el concreto es el extremo
menos conservador para la longitud, cinco mutantes vivos de la FASE A
muertos, M10 con su caso patrón (`CP_T9_CUNETA`, a mano; sale de
`SIN_CASO_PATRON`), `area_ha` exigida por A y B, las lecturas como
`Interpretacion` y el aporte calculado que la Fase 1-bis calcula UNA vez con
`MH.caudal_de_aporte_cuneta`—; tres en `test_M10_espaciamiento` (el caso
patrón); los once anclajes de `test_decisiones_diferidas` para las fichas de la
Parte XLVIII (T9-01..11); cuatro que crecen solos en `test_ext5_forma_gui` con
los cuatro criterios nuevos; y nueve en `test_familias_del_csv` (seis pasan y
tres son saltos de DISEÑO: la Familia B usa las tres claves nuevas, y por eso
esta columna salta ahora seis y no tres en las cuatro configuraciones). **No
se escribieron en rojo primero**: la FASE A midió 81 rojos y 1 verde de sus
82 contra `df1b23c`, y las correcciones, 62 rojos y 4 verdes de sus 66
primeros contra la FASE A (`304cea6`); los `test_mut_*` se midieron contra
sus mutantes. La mutación con el arnés de EXT-11 sobre una copia del árbol
fusionado: **262 de 288 en M10 (91.0 %) y 78 de 78** en las seis funciones de
la Fase 10 de `servicio`; los 26 vivos son banda de tolerancia, guardias
inalcanzables, presentación o equivalentes (ficha T9-11). Censos: **114
criterios** (cuatro nuevos, ninguno sin valor: siguen **27**), las citas del
registro pasan de 384 a **401** (once de la FASE A y seis de las
correcciones), `CLAVES_EXTERNAS` **veintiuna**, ninguna marca `literal-ok`
nueva fuera de M10 (dos, los exponentes de Manning). Se reescribieron,
declarándolo, `test_guia_perfil` (las dos corridas de la guía y la sesión
salen con 1: la VB1 de B-01 no cumple), `test_cli` (el cierre de perfil
declara el inicio del tramo de B-01), `test_t2_hidraulica` y
`test_t6_geometria` (la VB1 de B-01 no es suya), `test_pf2_prevuelo` (la
partición: `inicio_tramo_cuneta_km` tiene regla), `test_ext8` (techos
remedidos y pegados a la medida: 114.0 KB y 32.3 páginas por punto a
expediente, donde `6c25f1d` medía 109.7 y 31.7, por el bloque de B-01), `test_memoria_sustentada`, `test_M1_clasificacion`,
`test_t0_gobernanza` (la fila de T-9) y `test_guardias_de_la_suite`. La CLI,
sin etapas bloqueadas y con incumplidas, ya no dice «mientras un criterio
siga sin valor». Cierra `INF-5.1.12` e `INF-3.3.8`, y `INF-5.1.8` **en parte**
(`area_ha` en B tiene consumidores reales, pero nada comprueba que sea el área
del tramo). **La línea base de la Familia C se regeneró sobre el árbol
fusionado y se midió contra `6c25f1d` con el comparador de E-B**, en los cuatro
JSON y con las mismas ocho diferencias en los cuatro (B-01: tramo, aporte, VB1
evaluada y texto del bloqueo; dos criterios usados más; huellas):
**ningún diámetro, sección ni material se movió**, y el ÚNICO veredicto que
cambia es la **VB1 de B-01**, que no se evaluaba y ahora NO CUMPLE (A-02 cierra
su tramo, 530 m > 200 m; en la guía, contra los 120 m de `L_hidraulico_m`):
«Verificaciones incumplidas» pasa de 0 a 1 en las cinco corridas de la CLI y
en las dos de la guía, que ya no cierran y dicen cómo se resuelve (un alivio
intermedio o el inicio del tramo declarado con su procedencia). Las entradas
que esto deja al proyecto —la región pluvial en año FEN, la velocidad de
diseño y el IMDA de la vía, el talud de corte, el inicio de cada tramo— están
en `docs/contrato_entradas.md` con quién las debe. De las cuatro
configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de normas
enlazado: 5529 passed, 19 skipped, collected 5548 (y sin
`NORMAS_DIR`, sobre el mismo árbol: 5511 passed, 37 skipped). **Las otras
tres se dicen como derivadas, no como medidas**, por lo mismo que en T-0: la
derivación suma 196 a las de T-3, pasa tres a `skipped` en las cuatro
columnas (los de diseño) y siete más en las dos sin PyMuPDF.
**T-3 de la cadena T (2026-11-12, cerrado e integrado el
2026-11-13 detrás de las correcciones de T-8, con las de su auditoría) sumó
CIENTO SEIS tests netos**, ninguno con la marca `pdf` ni dependiente de Tk
ni del repositorio de normas: los 44 de `tests/test_t3_familia_c.py` —la
aceptación de la FASE A: **la Familia C se dimensiona sin declarar nada**
(`INF-0.4`). Los siete criterios del marco tienen valor de archivo con fila
nombrada, cita y ventana —`embocadura_cajon` Carta 8 escala 1 (aletas de 30°
a 75°, Forma 1) y su `ke_entrada_cajon` 0.4 de la Tabla C.2; `n_celdas_cajon`
1; `secciones_cajon_normalizadas` (1.20, 0.90), (1.50, 1.20), (2.00, 1.50),
la decisión del dueño del 2026-11-12 (la de la cadena T, anchos 1.00–4.00 ×
alturas 1.00–3.00, no contiene el 1.20 × 0.90 y deja a C-01 sin dimensionar;
queda barrible, ficha T3-01); `espesor_pared_cajon` 0.20 m [A], piso de la
E.060 14.5.3.2 por analogía; `cobertura_minima_cajon` 0.3048 m [A]; y
`n_manning_cajon`, ver abajo—; VC2 (`M7.vc2_empalme_canal`, el empalme de la
salida con el fondo del canal, AVISO con `desajuste_empalme_canal_m` [A] =
0.010 m por analogía con EG-2013 503.11 g)), el remanso aguas arriba del canal
(`M7.remanso_canal`, aviso, con `seccion_receptor_medida`; sin ella «no se
evaluó»), la geometría del marco (`modelos.GeometriaMarco`, paso 7.B.M, con
el ancho de N celdas en `SeccionRectangular.ancho_exterior_de_celdas`) y V6
con N > 1 publicando el reparto, el tabique y el ancho total sin aceptar la
multicelda—; los 63 de `tests/test_t3_correcciones_auditoria.py`, la
aceptación de las **correcciones de la auditoría adversarial** (AJUSTADO, H1 a
H12), con las resoluciones del orquestador: (H1) `n_manning_cajon` pasa a
**[C]** con la fila **propia** del cajón, HDS-5 Tabla B.1 «Concrete Boxes |
Smooth | 0.012–0.015» (pág. impresa B.6), la misma fuente de la carta y del
ke del marco, con el num. B.3 (0.012–0.022 en vaciado in situ, según el
encofrado) como ventana hacia arriba y la fila «afinado» de la Tabla N° 09
(0.011, 0.014) como alternativa barrible —con dos tablas, la resolución no
fija `fila_id`, y el valor es la clave de la fila (`M2._fila_manning_de_cajon`
la acota y `constantes_normativas.MANNING_CAJON_HDS5` lee el par del
registro)—; (H10) la errata `DIS-MCHHD-T09-A2-DESPLAZADA` se sostiene en la
evidencia **interna** de la página (Chow no está en `normas/`), alcanza también
a los bloques B.1, B.2 y C, y la lectura literal sería más conservadora para
capacidad: lo dicen la discrepancia, el criterio y una nota de la v8 bajo su
tabla de Manning; (H2, H3) el remanso calcula el tirante crítico del canal
(`M3.tirante_critico_trapecial`) y **no concluye**, sin cifra presentada como
cota, en un canal de pendiente fuerte (S1 que termina en resalto) o con VC2
fuera de tolerancia (HW de una descarga libre que el canal no tiene); (H4)
VC2 **gobierna el empalme**: en la Familia C G2 admite por debajo su
tolerancia y los dos veredictos no se contradicen —A y B no cambian—; (H5)
G1 del **marco avisa** (INDICADOR) cuando sólo falta la cobertura adoptada,
que es más restrictiva que la fuente (MTC 4.1.1.3.4 a), Lámina N° 03 y AASHTO
LRFD 12.6.6.3, cita nueva `AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA`):
`TamizadoRasante.cobertura_como_aviso`, el resguardo sigue bloqueando y G1 del
tubo no cambia; (H6) V7 **no se toca**, y las fichas dicen la causa real de que
la progresión de la cadena deje a C-01 sin dimensionar —`M5.v7_flotacion`
lleva DC = 0—, diferida al dueño en la ficha T3-08; (H7) los pasos 7.B.R,
7.B.M y VC2 dejan vacía la cita de la fórmula; (H8) el test vacuo de la
pendiente del canal mide su guardia y mueren los mutantes vivos de VC2, del
remanso, de G2 y de la geometría —el arnés de EXT-11 sobre las seis funciones
tocadas mataba 104 de 120 antes de los nueve tests que eso sumó y 113 de 120
(94.2 %) después; los siete vivos son equivalentes, censados en la ficha
T3-12—; (H9) el aviso de VC2 imprime la S que cerraría el
empalme; (H11, H12) la progresión es la decisión del dueño y el espesor queda
[A] con su razón—; los doce anclajes de `test_decisiones_diferidas` para las
fichas de la Parte XLVII (T3-01..12); y el que crece solo en
`test_ext5_forma_gui` con el criterio nuevo; **menos catorce**: los siete del
cajón que salen del parametrizado de vacíos de `test_criterios_adoptados` y
los siete ejemplos de `--declarar` de `test_guia_perfil` (la guía ya no los
declara). **No se escribieron en rojo primero con `xfail`**: la FASE A midió
38 rojos y 3 verdes de sus 41 primeros contra `df1b23c`, y las correcciones se
escribieron antes del código y se midieron contra la FASE A rebasada
(`c6712d4`): con el archivo final, 33 rojos y 30 verdes, que son guardias y
matadores de mutantes (ficha T3-12). Censos: **110 criterios, 27 sin valor** (34 − 7); las citas
del registro pasan de 378 a 384, cuatro de la FASE A y dos de las
correcciones (`HDS5_3ED.B.3#CAJON_IN_SITU` y
`AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA`); `CLAVES_EXTERNAS` sigue en
dieciocho; ninguna marca `literal-ok` nueva. Se reescribieron, declarándolo, `test_t3_familia_c` (la fila de Manning
sale del parametrizado de «lo que la guía declaraba», el remanso con la sonda
de la guía no concluye, el test vacuo mide su campo), `test_memoria_sustentada`
(`F4.N_CAJON_TB1` y los tres `F7.*` de T-3 entre los que la corrida por
defecto no alcanza), `test_ext8` (techos remedidos: 109.7 KB y 31.7 páginas
por punto donde `e78a4e7` medía 70.3 y 20.3: C-01 llega a VC1 en vez de
detenerse en el primer criterio del cajón) y `test_t0_gobernanza` (la fila de
T-3; `INF-3.2.1` pasa de «Cerrado parcial» de T-4 a «Cerrado» de T-3). Cierra
`INF-0.4` e `INF-3.2.1`, y deja una nota en `INF-0.5`. **La línea base de la
Familia C se regeneró sobre el árbol fusionado y se midió contra `e78a4e7` con
el comparador de E-B**, y **ningún diámetro, sección ni material se movió**:
el bloque `diseno` de A-01, A-02 y B-01 es idéntico; C-01 pasa de bloqueado
por `embocadura_cajon` a bloqueado por el dato `cota_coronacion_canal` en las
corridas ancha y de expediente, y una **corrida 6 nueva** (la coronación de la
guía en una copia del CSV) lo dimensiona como **marco 1.20 × 0.90 m**, control
de salida, HW = 0.623 m (con la fila de la Tabla B.1 el HW de salida baja 0.4
mm y el tirante normal sube de 0.404 a 0.425 m; la sección no se mueve), con
la Fase 6 bajo la envolvente de las correcciones de T-8 —para un marco HEC-14
no es evaluable y rige Laushey, con aviso—. De las cuatro configuraciones se
MIDIÓ UNA, «sí · no», con el repositorio de normas enlazado: 5336 passed, 16
skipped, collected 5352 (y sin `NORMAS_DIR`, sobre el mismo árbol: 5318
passed, 34 skipped). **Las otras tres se dicen como derivadas, no como
medidas**: la derivación suma 106 a las de las correcciones de T-8 en las
cuatro columnas. **Las correcciones de T-8 (2026-11-12, integradas detrás de
T-5) sumaron SESENTA Y NUEVE tests**, uno con la marca `pdf` (abre el EG-2013,
que está en `normas/` de la app) y ninguno dependiente de Tk ni del
repositorio de normas: los 63 de `tests/test_t8_correcciones.py` —la
aceptación de la SEGUNDA auditoría adversarial de T-8 (H1 a H15) y de las seis
decisiones que el dueño del proyecto tomó sobre ella el mismo día (D1 a D6)—
y los seis anclajes de `test_decisiones_diferidas` para las fichas T8-07 a
T8-12, que cierran la Parte XLV antes de la de T-5. **Seis cosas cambian, y
conviene leerlas porque el párrafo de T-8 de abajo decía otra cosa y se
corrigió en su sitio:** (1) `regla_espesor_longitud_proteccion_salida` vale
`envolvente_hec14` y la envolvente alcanza a la PIEDRA: el d50 que rige es el
mayor del de Laushey —que se sigue calculando e imprimiendo,
`ProteccionSalida.d50_laushey`; `ProteccionSalida.d50` es desde aquí «el que
rige»— y del D50 de la Ec. (10.4), y el espesor y la longitud los mayores de
lo adoptado y de los de la Tabla 10.1 para esa piedra; donde HEC-14 no es
evaluable rige Laushey con lo adoptado y se avisa, y fuera de la Tabla 10.1 se
imprimen cotas inferiores (2.0·d50 y 8D) con el aviso de que hace falta un
disipador (ficha T8-07); `manual` queda barrible y reproduce exactamente los
números anteriores; (2) «sin enrocado» nunca es conclusión: la protección se
calcula y se mantiene SIEMPRE, el contraste con la Tabla Nº 11 informa si el
terreno la resistiría y suprimirla queda sujeto a inspección de campo (HDS-5
núm. 5.3.2), y con la velocidad tomada al tirante crítico —cota inferior de la
de borde: las Figuras 3.3 y 3.4 de HEC-14 no están digitalizadas, ficha
T8-08— el contraste NO concluye (veredicto INDICADOR,
`VelocidadAdmisible.concluyente`, que llega a `InformePunto.avisos()`);
(3) `duracion_caudal_pico_socavacion_min` pasa de [C] 30 min a [A] 360 min,
ventana 30–360 con 30 barrible y la cita literal de HEC-14 («2/3 to 3/4 of
the maximum scour depth», `HEC14.5.1.2#DOS_TERCIOS`): la fuente sostiene el
piso y la razón para no quedarse en él, y **el techo de 360 min es elección
del proyecto, no de HEC-14**, que no da duración máxima (la hoya de
`HoyaDeSocavacion` llama ahora `profundidad_alternativa` a la de la otra
punta de la ventana); (4) la nota (5) b de la Tabla 511-06 del EG-2013 vale
sólo en la columna «>50»: es la lectura que no relaja, declarada como
`Interpretacion` (`citas.INTERPRETACION_NOTA_5_T511_06`) y sostenida por la
Tabla 511-02 de la misma Sección, que numera las dos notas por separado, hasta
conseguir AASHTO M 288 (ficha T8-10); (5) el límite del apron es 60 in =
1.524 m (`HEC14_APRON_ALTURA_MAX_M`), la lectura que deja evaluable el ejemplo
resuelto de la propia fuente, y el CU vuelve a su escala real; (6) lo demás de
la auditoría: el Froude de HEC-14 no clasifica el régimen
(`fundamentos.FROUDE_SALIDA` y otros cuatro `F6.*` reescritos), tres
`Interpretacion` nuevas colgadas de HEC-14 10.2, del núm. 4.1.1.3.7 c) y de la
Tabla 511-06 que los pasos leen del registro, guardias de tipo en las entradas
de texto de M6 (H7), «recomienda» donde decía «manda» (H8), la cita de hs de
HEC-14 10.1 (H9), los mensajes y comentarios que decían lo contrario que el
código (H10), las tablas transcritas fijadas celda a celda (H13) y la banda de
régimen de M4 avisada desde M6 sin tocar M4 (ficha T8-09). Lo que la auditoría
pidió y no se hizo —techos físicos para los datos de la Fase 6— está refutado
con su razón en la ficha T8-11. **El rojo se escribió primero** con
`xfail(strict=True)`, y porque las decisiones del dueño llegaron a media
pasada y reescribieron H1, H2, H11 y D3 se REMIDIÓ con el archivo final sobre
`df1b23c`: 43 rojos y 20 verdes, que son guardias (ficha T8-12); la mutación
de M6 con el arnés de EXT-11 mata 536 de 574 (93.4 %), sumando una medida
entera y una parcial. Ningún archivo restó tests: `test_t8_proteccion` se
reescribió a la verdad nueva y sigue en 96 (declarado en su cabecera), y
`test_guardias_de_la_suite` gana una entrada en `TEXTUAL_CON_RAZON`. Ningún
censo cambia: 109 criterios, 34 sin valor, `CLAVES_EXTERNAS` dieciocho,
ninguna marca `literal-ok` nueva; las citas del registro pasan de 375 a
378. El tracker no cambia ningún estado: INF-3.3.7, INF-5.1.13 y MAT-X6
ganan una NOTA. **La línea base de la Familia C se regeneró sobre el árbol
fusionado y se midió contra `1522635` con el comparador de E-B, y es la
primera regeneración de la cadena T que mueve un número de la Fase 6, con la
aprobación del dueño**: 15 diferencias en el JSON ancho y 0 no comparables —el
espesor de A-01 y A-02 pasa de 0.592 y 0.479 m a 0.770 m (clase 4 de la Tabla
10.1: 2.2·0.35) y la longitud de 5.00 a 5.40 m (6·0.90); el d50 que rige NO se
mueve (0.338 y 0.274 m: rige Laushey, porque la Ec. 10.4 pide 0.252 y
0.104 m); las claves nuevas `d50_laushey_m` y `rige_la_envolvente`, la regla,
la tercera advertencia, el criterio entre los usados y la huella—, y sólo la
huella en los otros dos; las dos celdas de espesor y longitud del CSV ancho;
`cli_perfil.txt`, `cli_expediente.txt`, `cli_rama_error.txt`, el CSV de
expediente y la memoria del cajón no cambian un byte. El delta es el MISMO que
la rama midió contra `df1b23c` (comparado `diff` contra `diff`), y **ningún
diámetro ni material se movió**: A-01 y A-02 siguen en concreto de 0.90 m, y
la fila `F8.CLASE` de T-5 sigue en 37.42 y 37.04 N/m/mm. Los techos de
`test_ext8` se remidieron y no se mueven (70.3 KB y 20.3 páginas por punto a
expediente, iguales sobre `1522635`); la memoria de perfil, sin techo, pasa
de 101.4 a 102.6 KB por punto (el párrafo de la envolvente, el paso 6.6c y los
avisos). De las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el
repositorio de normas enlazado: 5230 passed, 16 skipped, collected
5246 (y sin `NORMAS_DIR`, sobre el mismo árbol: 5212 passed, 34
skipped). **Las otras tres se dicen como derivadas, no como medidas**, por lo
mismo que en T-0: la derivación suma 69 a las de T-5 y pasa uno de ellos a
`skipped` en las dos columnas sin PyMuPDF.
**T-5 de la cadena T (2026-11-12, integrado detrás de T-8: el
primero del segundo lote) sumó DOSCIENTOS UN tests netos**, veintiocho con la
marca `pdf` y ninguno dependiente de Tk ni del repositorio de normas: los 105
de `tests/test_t5_estructural_conducto.py` y los 74 de
`tests/test_t5_correcciones_auditoria.py` —**la Fase 8 REAL del conducto**
(`src/modulos/M8_estructural.py`, INF-3.3.5): la carga de tierra sobre la
altura real de relleno más el paquete estructural y la carga viva HL-93 del
Manual de Puentes distribuida a través del relleno por AASHTO LRFD 3.6.1.2.6
[C], con el IM de componentes enterrados (`M8.carga_viva_enterrada`: GOBIERNA
EL VEHÍCULO DE MAYOR EFECTO sobre el conducto, que cada consumidor pasa en
`efecto=`, no el de mayor presión; fuera del dominio del método,
`MetodoNoEvaluableError` con `MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL`); el
tubo de concreto por el método indirecto de 12.10.4.3 contra la D-load de
0.3 mm de la clase de M 170M (`M8.verificar_concreto`); el TMC por 12.7.2
—empuje, área con pandeo, costura y factor de flexibilidad— con progresión
de plancha dentro de la corrugación adoptada y el mínimo de la Tabla 507-01
del EG-2013, y ASTM A796 solo como contraste por tensiones admisibles que no
rige (`M8.verificar_tmc`); el HDPE por 12.12 —empuje, pandeo general,
deflexión y factor de flexibilidad— (`M8.verificar_hdpe`); la demanda de la
losa superior del marco con el pórtico diferido (`M8.demanda_marco`); y el
relleno máximo de lo elegido, por el primer cruce del margen. **Lo que
decide si la combinación material / diámetro / plancha / clase EXISTE corre
también a nivel de perfil**, como filas `F8.*` de la tabla de la Fase 5
(`M5.fase_8_estructural`), detrás de V9 y solo si todo lo anterior cumple; a
perfil se difieren la cama de apoyo y la demanda del marco (ficha T5-01). La
mina `AssertionError` de `M8.seleccionar_clase_calibre` quedó retirada. **La
FASE A la auditaron dos auditores adversariales independientes (AJUSTADO los
dos) y el dueño del proyecto decidió el 2026-11-12 las siete preguntas que
dejaban abiertas; el cierre las aplicó, y conviene leerlas porque cuatro
contradicen lo que la FASE A había escrito:** (1) la instalación del tubo de
concreto es el Tipo 3 de archivo con `tipo_4` DENTRO de la ventana y el Tipo
4 impreso al lado como contraste (pasos `F8.TIPO4` y `F8.HMAX_TIPO4`); la
correspondencia del EG-2013 con el Tipo 3 es lectura del proyecto y tiene una
condición, dicha en la `Interpretacion` de la cita —los numerales del tubo de
concreto son 506.07, 506.10 y 506.11 → 502 → 205.12(c)(1), 95 % del Proctor
Modificado en el solado y la sujeción y 90 % en el relleno; el 508.07 que la
decisión citaba es del polietileno— (ficha T5-12); (2) las propiedades de
sección del HDPE son DATO DEL FABRICANTE (`perfil_hdpe_fabricante`, [A]
opcional sin valor por defecto): sin ellas el HDPE queda «no verificado con
un producto real» —`DatoFaltanteError` con la cota inferior del perfil mínimo
de la Tabla A12-11 en el mensaje, que AASHTO C12.12.3.2 declara «not
meaningful for design»— y NO se adopta; el relleno de archivo es `Si-95`, la
columna menos favorable de las que corresponden al material granular que el
EG-2013 508.02 d) exige, y no `Cl-95`, con el que el perfil mínimo no cumple
a ninguna altura (fichas T5-05 y T5-10); (3) `fabricacion_tmc` es la
remachada simple, la costura más débil TABULADA, y el resultado avisa siempre
que el EG-2013 507.02 a) describe tubería empernada; el caso G2 de la
auditoría de T-4 (TMC de 1.95 m con ~8.5 m de relleno) deja de dimensionarse
y su test se reescribió DECLARÁNDOLO, no en silencio como en la FASE A (ficha
T5-08); (4) la carga viva pasados 8.0 ft de relleno se CONSERVA: despreciarla
es el permiso de 3.6.1.2.6a y lo declara `carga_viva_bajo_relleno_alto` [A]
(ficha T5-11); (5) η_I = 1.05 no lo prescribe ninguna fuente para una
estructura enterrada: es la clasificación de importancia del Propietario, [A]
con la ventana del Manual de Puentes 2.3.2.5, y η_R = 1.00 por 12.5.4; (6) un
tubo de concreto que pide más que la Clase II —la única D-load legible del
ejemplar de M 170M— BLOQUEA el punto con el mensaje que nombra las clases que
faltan para ese diámetro, y el ejemplar legible va a la lista de entradas del
dueño (`docs/contrato_entradas.md`); la clase no se ofrece por debajo del
primer diámetro que la norma le tabula (ficha T5-02); (7) el pandeo general
del HDPE va con el módulo de la vida de diseño, como manda la letra de
12.12.3.3, con la suma por duración al lado y rigiendo la mayor (ficha
T5-13). **Y una regla de MD que sale de ahí:** un punto al que solo le falta
un dato no es «no factible» —cuando la Fase 8 detiene por dato faltante un
escalón que cumple toda la tabla, `MD.disenar_punto` relanza ese
`DatoFaltanteError`—; el HDPE es el último candidato de M2, de modo que su
dato no bloquea a ningún otro (regla T4-10). Los dorados
(`CP_FASE_8_ESTRUCTURAL` y `CP_FASE_8_CIERRE`) están calculados a mano en
unidades inglesas, con la aritmética escrita. **Ni los tests de la FASE A ni
los de las correcciones se escribieron en rojo primero**: los de las
correcciones se midieron contra la FASE A rebasada (`1768b45`) y 48 de 71
fallan allí —los 23 que valen antes y después son quince literales del PDF y
ocho guardias—; y veinticuatro mutantes dirigidos, los que las dos auditorías
habían dejado vivos, mueren todos (ficha T5-14). Los otros 22 netos: los
catorce anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XLVI (T5-01..14); los siete que crecen solos en `test_ext5_forma_gui` con los
siete criterios nuevos (109 donde T-8 dejó 102; los sin valor bajan de 35 a
34, porque `clases_producto_por_relleno` deja de estar vacío y
`perfil_hdpe_fabricante` es opcional y no cuenta: los opcionales vuelven a
ser cuatro); dos en `test_t4_materiales_durabilidad` (el caso G2, que pasa de
un test a tres); y uno MENOS en `test_criterios_adoptados` (el caso de
`clases_producto_por_relleno` en el parametrizado de vacíos). Se reescribieron
al contrato nuevo `test_M8_estructural`, `test_cli`, `test_cierre_perfil` (la
fila `F8.CLASE` detrás de V9), `test_memoria_sustentada` (doce fundamentos
`F8.*` que la corrida por defecto no alcanza), `test_sin_literales`
(`src/modulos/M8_estructural.py`: 29), `test_normativa`,
`test_guardias_de_la_suite` y `test_t0_gobernanza`, que ganó la fila de T-5.
Cierra INF-3.3.5, con residuales declarados que dependen de entradas (las
clases ilegibles de M 170M, el perfil del fabricante del HDPE, la costura
empernada del TMC y el pórtico del marco). **La línea base de la Familia C se
regeneró sobre el árbol fusionado y se midió contra `df1b23c` con el
comparador de E-B**: 18 diferencias en el JSON ancho, todas de T-5 —la fila
`F8.CLASE` de A-01 y A-02 (37.42 y 37.04 frente a 50.0 N/m/mm), su bloque
`estructural` (Clase II, relleno máximo 2.851 m; 1.691 m con el Tipo 4), el
texto del diferimiento de la Fase 8, tres criterios usados, las huellas y los
recuentos— y 3 de huella y recuento en los otros dos; los dos CSV de resumen,
tres de los cuatro `cli_*.txt` y la memoria del cajón no cambian un byte, y
**ningún diámetro ni material se movió** (A-01 y A-02 siguen en concreto de
0.90 m). Los techos de `test_ext8` se remidieron y no se mueven (70.3 KB y
20.3 páginas por punto a expediente). De las cuatro configuraciones se MIDIÓ
UNA, «sí · no», con el repositorio de normas enlazado: 5161 passed, 16
skipped, collected 5177 (y sin `NORMAS_DIR`, sobre el mismo árbol: 5143
passed, 34 skipped). **Las otras tres se dicen como derivadas, no como
medidas**, por lo mismo que en T-0: la derivación suma 201 a las de T-8 y
pasa 28 de ellos a `skipped` en las dos columnas sin PyMuPDF.
**T-8 de la cadena T (2026-11-12, integrado detrás de T-6)
sumó CIENTO DIEZ tests**, ninguno con la marca `pdf` ni dependiente de Tk ni
del repositorio de normas: los 96 de `tests/test_t8_proteccion.py` —la Fase 6
de entrada y salida, con el d50 de Laushey del Manual (núm. 4.1.1.3.7 c)),
que T-8 dejó rigiendo sin moverse y que **desde sus correcciones rige dentro
de la ENVOLVENTE con HEC-14** (párrafo de arriba; lo que este párrafo dice
de T-8 y las correcciones cambiaron va corregido en su sitio):
`M6.proteccion_salida` lo contrasta con la velocidad máxima admisible del
terreno (Tabla Nº 11 del Manual, por `tipo_terreno_receptor` y
`regimen_flujo_descarga`) y dice si el terreno la resistiría —en T-8, si la
protección era «requerida»; desde las correcciones el contraste INFORMA, la
protección se mantiene siempre y «sin enrocado» no es conclusión—, y calcula
AL LADO el apron de HEC-14 Cap. 10 (`M6.apron_hec14`: Ec.
10.4 con el D' de la Ec. 10.5 y el TW acotado a 0.4D–1.0D, clase de la Tabla
10.1, ancho 3D + (2/3)L) y la clase de la piedra adoptada (paso 6.6b), con
aviso cuando lo adoptado queda corto y SIEMPRE que el espesor 1.75·d50 quede
bajo el piso de 2.0·D50 de HEC-14 —la decisión quedó preparada en
`regla_espesor_longitud_proteccion_salida` [A]; T-8 la dejó en `manual` con
`envolvente_hec14` barrible, y desde las correcciones es AL REVÉS:
`envolvente_hec14` de archivo, alcanzando también a la piedra, y `manual`
barrible—; el Froude de HEC-14 (`Fr_e` con `ye =
(A/2)^0.5`) es un parámetro de diseño y no un indicador de régimen, que sale
del tirante contra el crítico por UNA regla (`M6.flujo_supercritico`); el
filtro es un requisito declarado (Lámina Nº 05, HEC-14 núm. 10.2, EG-2013
núm. 511.08 con la Tabla 511-06 leída por fila y su nota (5) a; la (5) b, que
T-8 aplicaba a la fila, vale desde las correcciones sólo en la columna «>50»,
declarada como `Interpretacion`), no un dimensionado; la entrada (`M6.proteccion_entrada`, INF-5.1.13) publica la
velocidad en la boca de lo que M4 ya resolvió, la contrasta con la Tabla Nº
11 si se declara `tipo_terreno_entrada` y declara el revestimiento de
`tipo_proteccion_entrada` [A] y lo que se protege según la embocadura, sin
dimensiones porque ninguna fuente de `normas/` se las da (ficha T8-03); y la
socavación a la salida para el desplante (`M6.socavacion_salida`) es HEC-14
**Cap. 5** —no el 3, errata de la cadena—, Ec. 5.1 en no cohesivos y 5.2 a
5.4 en cohesivos con sus Tablas 5.1 a 5.4, la duración del pico declarada o
`duracion_caudal_pico_socavacion_min` —[C] de 30 min en T-8, el valor que la
fuente recomienda cuando no se conoce; desde las correcciones, [A] de 360 min
con ventana 30–360 y 30 barrible: a 30 min sólo se alcanza de 2/3 a 3/4 de
la socavación máxima, y el techo de 360 es elección del proyecto, no de
HEC-14—; una duración menor de 30 min se acota a 30 como cota superior,
porque los exponentes no valen por debajo; la lectura entre filas por
`lectura_coeficientes_socavacion_hec14` [A], la referencia de la profundidad
por `referencia_profundidad_socavacion` [A] y la cota del fondo de la hoya;
seis datos externos nuevos y opcionales entran por `--datos-externos`
(`servicio.CLAVES_EXTERNAS` tiene dieciocho), y sin ellos la fase lo avisa.
Los oráculos son los ejemplos resueltos de HEC-14 (el de las págs. 10-18 y
10-19, y el CU, que T-8 escaló a λ = 0.9 para caber en un límite de 1.50 m y
que desde las correcciones corre a su escala real con el de 60 in = 1.524 m)
y la aritmética escrita—; los seis anclajes de `test_decisiones_diferidas` para
las fichas de la Parte XLV (T8-01..06); los cinco que crecen solos en
`test_ext5_forma_gui` con los cinco criterios nuevos (102 donde T-6 dejó 97;
los sin valor siguen siendo 35); y los tres de `test_dimensional_piloto` con
`HEC14_TAU_C_ALFA_U_SI` en su censo. **No se escribieron en rojo primero**:
el prompt se retomó a medias con el código escrito, y el rojo se midió contra
`ad5cb97` (ficha T8-06); la mutación de M6 con el arnés de EXT-11, sobre el
módulo final, mata 472 de 514 mutantes (91.8 %) y los 42 vivos están
clasificados en esa ficha. El auditor adversarial dejó diez correcciones, entre
ellas el aviso de la duración adoptada por criterio con su sensibilidad, una
sola regla de régimen, un IP fuera de 5–16 que avisa y no bloquea, la salida
sin enrocado avisada con el literal de HDS-5 núm. 5.3.2 («…is typically a
standard practice unless…») y
su `Interpretacion` en vez de un verbo de obligación (desde las correcciones
el mismo literal acompaña al aviso de que la protección se MANTIENE y
suprimirla queda sujeto a inspección de campo), el límite de la nota 8 de la
Tabla 1.1 (1.50 m en T-8; 1.524 m desde las correcciones), el tirante de borde (HEC-14 núm. 3.1.3), el terreno
declarado contra el lecho y el rótulo `MOTIVO_METODO_NO_EVALUABLE_HEC14`.
Ningún archivo restó tests; se reescribieron `test_t0_gobernanza` (HEC-14
pasa de «sin citas» a citada y firmada por T-8, y la fila de T-8 en
`LO_QUE_ESCRIBIO_CADA_PROMPT`), `test_t2_hidraulica` (los avisos sin los de
geometría ni los de la Fase 6), `test_ayuda_entrada` (catorce externos que no
son columna), `test_memoria_sustentada` (las tres piezas de la Fase 6 y nueve
fundamentos `F6.*` que la corrida por defecto no alcanza), `test_normativa`
(el prefijo `HEC`) y `test_sin_literales` (`src/dominios.py`: 11, por
`PORCENTAJE_POR_UNIDAD`). Cierra INF-3.3.7 e INF-5.1.13, y deja una nota en
MAT-X6: su premisa, «HEC-14 no está en normas/», ya no se sostiene, y con
HEC-14 la contradicción numérica sí se ve (en A-01, 0.592 m de espesor contra
0.770 m de profundidad del apron de clase 4; las correcciones la resuelven
por la envolvente). **La línea base de la Familia C
se regeneró por FORMATO** sobre el árbol fusionado y se midió contra
`7e74065` con el comparador de E-B: los bloques nuevos de la Fase 6, los
textos de dos advertencias, los avisos de la fase, los criterios usados, las
huellas y el recuento «97 / 35» → «102 / 35»; el bloque `diseno` de los
cuatro puntos es idéntico, los cuatro `cli_*.txt` salvo el ancho, los dos CSV
de resumen y la memoria del cajón no cambian un byte, **ningún diámetro se
movió** y en T-8 los números de Laushey tampoco (d50 0.338 y 0.274 m, espesor
0.592 y 0.479 m, longitud 5.00 m); las correcciones movieron el espesor a
0.770 m y la longitud a 5.40 m en los dos puntos, con el d50 sin mover. De las cuatro configuraciones se MIDIÓ UNA,
«sí · no», con el repositorio de normas enlazado: 4960 passed, 16 skipped,
collected 4976 (y sin `NORMAS_DIR`, sobre el mismo árbol: 4942 passed, 34 skipped). **Las
otras tres se dicen como derivadas, no como medidas**, por lo mismo que en
T-0: la derivación suma 110 a las de T-6, y ninguno pasa a `skipped`.
**T-6 de la cadena T (2026-11-11, integrado el 12 detrás de
T-2, T-4 y T-1: el último del primer lote) sumó CIENTO TREINTA Y OCHO
tests**, ninguno con la marca `pdf` ni dependiente de Tk: los 131 de
`tests/test_t6_geometria.py` —la geometría de la Sec. 7.B, por los cinco
puntos de su prompt: (1) `cota_fondo_entrada` medida gana, y cuando falta
la adopción deja de ser muda: `CotaDeEntrada.aviso` («fondo de entrada
adoptado igual al terreno de plataforma: medir en el cauce») y
`TamizadoRasante.provisional`, que marca el delta de rasante de 7.A; (2) la
longitud **por extremo** —criterio [A] `metodo_longitud_conducto`, con
`terraplen_simetrico`, la fórmula anterior, conservada como caso
particular—: `L = [ancho + talud·(H_e + H_s0)] / [cos θ − talud·S]`, con la
salida `S·L` más baja y `bombeo` o `peralte` como datos externos opcionales
y **excluyentes** (DG-2018 núm. 304.05 y 304.06), cuya ausencia se avisa con
su sensibilidad; el HDS-5 (núm. 2.2.4 b. y Figura 2.4, pág. impresa 2.8)
sostiene la superposición aproximada del barril, y medir al **fondo** es
elección del proyecto —cota superior de la longitud, no el lado seguro por
construcción—, de modo que la longitud entre cabezales a la clave se imprime
como encaje (núm. 3.3.5) sin sustituir a la del diseño; y 7.B deja de ser
una frase: pasos 7.B.1 a 7.B.5 con fórmula sustituida, más los de G2 y G3;
(3) G2 con `desnivel_minimo_entrega_m` [A] (0.0 m, ventana 0.0–0.30:
ninguna fuente da la cifra, y el umbral lo dice); (4) `esviaje_max_grados`
con valor (45°, ventana 45–60, por analogía con el esviaje de embocadura
del HDS-5 núm. 5.4.2) y como **aviso** —la verificación G3, con veredicto
INDICADOR— en vez del `DatoInvalidoError` del cierre de C10; (5)
`M7.pendiente_adoptada`, que resuelve la pendiente UNA vez antes de la Fase
4 y la deja con su origen (`OrigenPendiente`: cauce, declarada, mínima o
máxima). El dorado `CP_T6_LONGITUD_POR_EXTREMO` está calculado a mano—; los
cinco anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XLIV (T6-01..05); y los dos que crecen solos en `test_ext5_forma_gui` con
los dos criterios nuevos (97 donde T-1 dejó 95; los «todavía sin valor»
que la memoria cuenta siguen siendo 35, porque `esviaje_max_grados` era
opcional y no contaba entre ellos: recibe valor y los opcionales quedan en
tres). **La aceptación se midió
en rojo contra `87d1ce7`** antes de darla por tal (y los diez ítems del
cierre, contra los commits `wip(T-6)`), y el auditor adversarial
dejó nueve correcciones (bombeo y peralte excluyentes, la atribución a la
fuente de lo que es elección del proyecto, «cota superior» donde decía
inferior, el sesgo del eje con el fondo adoptado, la guardia del esviaje
negativo, el dorado a mano, el umbral de G2 citando la Lámina Nº 01). **Cuatro
cosas de la integración, que es donde T-6 toca a los otros tres:** (a) **el
reparto con V10** —`M7.pendiente_adoptada` lee la banda con la lectura
única de T-2, `M5.limites_de_pendiente()`, y acota sólo la pendiente del
**cauce**; V10 juzga la que quedó y sólo se incumple con una pendiente
**declarada**. Acotar no resuelve la obra y se avisa
(`M7.aviso_de_pendiente`): con la máxima, el desnivel `(S_cauce − S)·L`
pide una estructura de caída o de disipación que el programa no dimensiona
y V2b lo juzga según `regimen_v2b` (con `indicador_con_aviso` el punto
dimensiona con el indicador; con `umbral_duro` no dimensiona y el motivo
nombra V2b); con la mínima, la salida queda bajo el cauce natural y la
juzga G2. Una pendiente de cauce no finita o no positiva no se sustituye
por un extremo: es `DatoInvalidoError` (un NaN es falso frente a `>=` y
salía con origen «mínima»)—; (b) **los avisos de 7.B salen por
`InformePunto.avisos()`, una vez** (`avisos_de_geometria`: fondo adoptado,
pendiente en un extremo, plataforma horizontal, transversal descartada), y
los lleva también el punto que no dimensiona, porque su longitud ya entró
al diseño de cada escalón; G3 no va en esa lista: es un INDICADOR y sale
por `con_aviso` como V2b, de modo que cuenta en `ResumenDeCorrida.con_aviso`;
(c) `servicio.CLAVES_EXTERNAS` tiene doce claves, `CLAVES_QUE_ADMITEN_CERO`
suma `bombeo` y `peralte` y `CLAVES_CON_SIGNO` nombra la única con signo;
(d) lo que dejó el cierre de la integración: la banda vacía de
`M5.limites_de_pendiente`, que `M7.pendiente_adoptada` lee FUERA de
`_etapa`, salía de `correr_punto` y tumbaba la corrida —es un bloqueo del
punto en `servicio.ETAPA_PENDIENTE`, como cuando la levantaba V10 dentro
de MD—; el aviso de fondo adoptado del punto que no dimensiona sale de la
cota de entrada (`InformePunto.cota_entrada`) y no de la longitud, que con
el método simétrico o la longitud declarada no lo llevaba; G3 tiene segunda
línea sobre su máximo; y las fichas de `pendiente_minima_conducto` y
`pendiente_maxima_conducto` dicen el reparto con M7 (decían «la aplica
V10»).
Ningún archivo restó tests; se reescribieron `test_M7_geometria`,
`test_cierre_c10` (PC-32 pasa de bloqueo a aviso), `test_cierre_perfil`
(la longitud de A-01 a mano, 18.869 m; `G3` en la lista de códigos),
`test_criterios_adoptados`, `test_nivel_medido`, `test_ayuda_entrada`,
`test_memoria_sustentada` (siete fundamentos `F7.*`), `test_pf2_prevuelo`,
`test_t2_hidraulica` (los dos tests que fijaban la tupla entera de avisos
la fijan sin los de geometría), `test_pf1_hw_fuera_de_rango` (el caso patrón de
0.40 m/m declara su pendiente: la del cauce ya no llega al diseño fuera de
la banda), `test_ext8` (techos remedidos: 70.3 KB y 20.7 páginas por punto
donde `5bca7c6` medía 63.7 y 18.7; quedan pegados a la medida, 71 y 21, y
los reconcilia T-10) y `test_t0_gobernanza`, que ganó la fila de T-6 y le
pasó INF-3.2.7. Cierra INF-5.1.18, INF-3.3.3 e INF-3.2.7 (que T-2 había
dejado en parte), y enmienda PC-32 / C10-03. **La línea base de la Familia C
se regeneró y T-6 SÍ mueve números, todos declarados en su README**: la
longitud de los cuatro puntos (A-01 18.6350 → 18.8694 m; A-02 18.2695 →
18.5677; B-01 18.4000 → 18.7755; C-01 21.2465 → 21.4446) y lo que cuelga de
ella —caída, cota de salida y HW de **salida** de A-01 y A-02 (0.9929 →
0.9925 y 0.5618 → 0.5596 m; el HW que gobierna, de entrada, no cambia), y
el TW de la vía 4 en la corrida estrecha—; el bloqueo de C-01 en esa
corrida cambia de etapa («longitud del conducto (7.B)» en vez del TW) con
la misma causa. Medido contra `5bca7c6` con el comparador de E-B en los
tres JSON y en los doce pares punto × corrida: material, sección, control,
veredicto y admisible de cada verificación, iteraciones y tipo de cada
bloqueo son idénticos, y **ningún diámetro se movió** (A-01 y A-02 siguen
en Ø 0.90 m). De las cuatro configuraciones se MIDIÓ UNA, «sí · no», con el
repositorio de normas enlazado: 4850 passed, 16 skipped, collected 4866 (y
sin `NORMAS_DIR`, sobre el mismo árbol: 4832 passed, 34 skipped). **Las
otras tres se dicen como derivadas, no como medidas**, por lo mismo que en
T-0: la derivación suma 138 a las de T-1, y ninguno pasa a `skipped`.
**T-1 de la cadena T (2026-11-11, integrado el 12 detrás de T-2 y T-4) sumó
CIENTO NOVENTA Y UN tests**, veinte con la marca `pdf` y ninguno dependiente
de Tk: los 113 de `tests/test_t1_hidrologia.py` y los 59 de
`tests/test_MH_hidrologia.py` —la hidrología DENTRO del programa: el módulo
nuevo `src/modulos/MH_hidrologia.py` (Fase 1-bis, importado sólo por
`servicio.py`, con un test que lo fija por AST) calcula el caudal de un punto
de Familia A o B por el método racional (`Q = 0.278·C·I·A`, Manual de
Hidrología núm. 3.12.2, ec. 28, con «A<10 Km2» estricto) a partir de dos
entradas opcionales que van juntas, `--cuencas` y `--estacion`, y deja
**nueve pasos de memoria** con su cita (1b.1 a 1b.8 y 1b.3b); la precedencia
no cambia —`Q_m3s` en `--datos-externos`, la columna `Q_m3s` llena, y sólo
con la celda vacía el cálculo— y un caudal declarado se imprime como «Q
declarado por el estudio hidrológico» con su contraste Q/A (paso 1b.8, sin
umbral: el núm. 3.13 no pone uno); el tiempo de concentración lo declara cada
fila del CSV de cuencas entre CUATRO filas de la Tabla Nº 05 (Kirpich,
California, FAA y retardo SCS; la tabla está entera en el registro e Izzard
y onda cinemática quedan diferidas) y Témez, que **no es fila de esa tabla**
sino la ec. (30) del núm. 3.12.2.1; la lluvia de diseño sale del ajuste de la
serie P24 con las tres distribuciones de las que el Manual imprime el
estimador (Normal, Log Normal 2P, Gumbel) y Kolmogorov–Smirnov, y la
intensidad de Dick y Peschke o de la Tabla Nº 04;
`homogeneidad_serie_fen` tiene **consumidor real** y es una categoría de
tres tratamientos sin valor de archivo: sin declararlo el caudal calculado
se detiene, y un caudal declarado nunca recibe `tratamiento_fen`. La
auditoría adversarial dejó trece correcciones (H1 a H13), entre ellas: la
lluvia de diseño que queda por debajo de un año ya registrado se contrasta
con la probabilidad observada de la ec. (13) y se avisa (paso 1b.2; cita
`MC_HHD.3.12.5#PIURA`); una celda `fen` vacía no es un «no»; `S_terreno` es
columna obligatoria y la Tabla Nº 08 no se lee nunca con la pendiente del
cauce; la población de la que salió cada fórmula de tc es DESCRIPCIÓN de la
tabla y lo que se hace fuera lo decide `tc_fuera_de_la_poblacion_del_metodo`
[A], con el mismo trato para Kirpich y California; la duración de la lluvia
no baja de `duracion_minima_lluvia_min` [C] (5 min, WSDOT núm. 2-6.3); con
Témez el caudal lleva el coeficiente de uniformidad K por
`coeficiente_uniformidad_temez` [A] (uso híbrido declarado); una superficie
de la plataforma vial toma su C de `coeficiente_escorrentia_superficie_vial`
[C] (WSDOT Table 2-2), nunca de una fila de la Tabla Nº 08 puesta por
omisión; `area_ha` y `area_km2` de la misma cuenca tienen que decir lo
mismo; y **la regla de la hoja de ruta se restauró y es dura** —«reportar el
ajuste con y sin ellos, adoptar el más conservador»: `serie_sin_fen` con
menos lluvia que la serie completa DETIENE el cálculo hidrológico del punto,
por decisión del dueño (ficha T1-09)—. Los dorados (`CP13_HIDROLOGIA`) están
calculados a mano, porque el Manual no trae ejemplo numérico, y los datos de
`tests/fixtures/hidrologia/` son sintéticos y lo dicen en su primera línea—;
los nueve anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XLIII (T1-01..09); los siete que crecen solos en `test_ext5_forma_gui` con
los siete criterios nuevos (95 donde T-4 dejó 88, y los sin valor siguen
siendo 35); y los tres de `test_dimensional_piloto` con
`RACIONAL_COEFICIENTE_SI` en su censo. **No se escribieron en rojo
primero**: el archivo de aceptación lo dice y midió el rojo sobre `87d1ce7`
(105 xfailed y 14 XPASS de 119). Ningún archivo restó tests; se reescribieron
`test_t2_hidraulica` (dos tests que decían «sin avisos» dicen «sin más aviso
que el del caudal declarado»), `test_cierre_perfil`, `test_nivel_medido`
(`homogeneidad_serie_fen` sale de `SIN_CONSUMIDOR_Y_SIN_MEDIDA`),
`test_memoria_sustentada` (ocho fundamentos `FH.*` que sólo se emiten con el
caudal calculado), `test_sin_literales` (`src/dominios.py`: 10),
`test_normativa`, `test_traza_punto` y `test_t0_gobernanza`, que ganó la
fila de T-1 en `LO_QUE_ESCRIBIO_CADA_PROMPT`. Tres cosas de la integración
con T-2: los avisos de la Fase 1-bis salen por `InformePunto.avisos()` con
los demás del punto, una sola vez; todo punto de Familia A o B con el caudal
declarado lleva ahí un aviso PERMANENTE (el criterio FEN no lo alcanza); y un
paso de la Fase 1-bis con veredicto INDICADOR cuenta en
`ResumenDeCorrida.con_aviso` junto a las verificaciones
(`InformePunto.indicadores_de_hidrologia`). Cierra INF-3.1.2, INF-3.1.3,
INF-3.1.5, INF-3.1.6, INF-5.2.5 e INF-5.1.3, y en parte INF-3.1.1 (la
delimitación de la cuenca es una entrada) e INF-3.1.4 (quién fija R y n
sigue siendo del Propietario). La línea base de la Familia C se regeneró
sobre el árbol fusionado y se midió contra `7fb7926` en los doce pares punto
× corrida: material, sección, código, estado, veredicto, valor obtenido y
admisible de cada verificación, tipo de cada bloqueo, iteraciones,
durabilidad y periodo de retorno son idénticos; cambian la línea «Fase 1b Q
declarado…», el aviso permanente, la clave `caudal`, el origen del caudal en
la clasificación, tres entradas de `verificacion_pendiente`, las huellas y
el recuento de criterios; los dos CSV de resumen y la memoria del cajón no
cambian un byte, y **ningún diámetro se movió**. De las cuatro
configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de normas
enlazado: 4712 passed, 16 skipped, collected 4728 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 4694 passed, 34 skipped). **Las otras tres se dicen como
derivadas, no como medidas**, por lo mismo que en T-0: la derivación suma
191 a las de T-4 y pasa 20 de ellos a `skipped` en las dos columnas sin
PyMuPDF. **T-4 de la cadena T (2026-11-11, integrado el 12 detrás de
T-2) sumó CIENTO TREINTA Y UN tests netos**, quince con la marca `pdf` y
ninguno dependiente de Tk: los 115 de
`tests/test_t4_materiales_durabilidad.py` —la aceptación de material,
durabilidad y topes: el espesor de pared del TMC derivado de la corrugación
y la plancha adoptadas (`corrugacion_y_espesor_tmc` [A]: 13 + 2.01 mm, M 36
Table 1 y núm. 8.1.1) y el del HDPE del diámetro exterior máximo de AASHTO
LRFD Table A12-11, con 7.A y V7 recalculados a mano sobre A-01 y B-01; el
tope de diámetro por norma de producto (`D_max_norma_producto` [C]: 2.70 /
3.60 / 1.50 m, y en concreto el último DISEÑO ESTÁNDAR de M 170M, no la
última fila de su serie), la corrugación como tope del TMC y
`D_max_catalogo` [A] opcional que sólo baja; `v_max_tmc` [A] con ventana
(3.048, 4.572) y `v_max_hdpe` [C] citado del §8-3.3 de WSDOT; el n del HDPE
[C] de HDS-5 Table B.1; la matriz de durabilidad como filtro real de
`M2.materiales_candidatos` con seis ensayos opcionales que entran por
`--datos-externos` (`servicio.CLAVES_DE_DURABILIDAD`, fuera de
`CLAVES_EXTERNAS` para que el pre-vuelo no los anuncie como faltas) y que
sin ensayos imprime «durabilidad: sin ensayos, matriz no aplicada»; el aviso
de marco leído de `sucs_fundacion` contra `sucs_fundacion_deficiente` [A]; y
las correcciones del auditor adversarial (H1 a H11), entre ellas que
`MD.disenar_punto` no acepta un candidato si uno ANTERIOR quedó sin evaluar
por un dato que falta —lo que invierte el «caso mixto» que EXT-1 había
dejado sin cambio en PC-28, ficha T4-10—, los criterios electroquímicos de
AASHTO LRFD para acero galvanizado enterrado aplicados por analogía
(`suelo_agresivo_acero_lrfd` [C]) con efecto declarado
(`suelo_agresivo_lrfd_sobre_tmc` [A] = `aviso` | `excluye`), EG-2013 507.10
aplicada entera y el aviso fijo del Manual para la TMC candidata—; los diez
anclajes de `test_decisiones_diferidas` para las fichas de la Parte XLII
(T4-01..10); y los seis que crecen solos en `test_ext5_forma_gui` con los
seis criterios nuevos (88 donde T-2 dejó 82). No se
escribieron en rojo primero: el registro y las fichas fueron antes, y el
archivo lo dice. Ningún archivo restó tests; se reescribieron al contrato
nuevo `test_M2_material`, `test_M3_hidraulica`, `test_M5_verificaciones`,
`test_MD`, `test_criterios_adoptados`, `test_declaracion`,
`test_ext11_propiedades`, `test_pf3_barrido`, `test_cierre_c05`,
`test_guardias_de_la_suite`, `test_memoria_sustentada`, `test_sin_literales`
(`src/dominios.py`: 8), `test_normativa` y `test_ext1_entradas` (el caso
mixto de PC-28), y `test_t0_gobernanza` ganó la fila de T-4 en
`LO_QUE_ESCRIBIO_CADA_PROMPT`. Cierra INF-5.1.17, INF-3.3.4, INF-3.3.1,
INF-3.2.4, INF-5.1.9 e INF-5.1.16, y en parte INF-3.2.1 (sólo el HDPE). La
línea base de la Familia C se regeneró sobre el árbol fusionado y se midió
contra `ad5cb97` en los doce pares punto × corrida: material, sección,
código, estado, veredicto, valor obtenido y admisible de cada verificación y
tipo de cada bloqueo son idénticos; cambian la lista de materiales EVALUADOS
(B-01 de la corrida ancha pasa de 10 a 21 escalones), el texto de los
motivos, el criterio que V9 cita, las líneas y el bloque de durabilidad, los
criterios usados y las huellas; los dos CSV de resumen y la memoria del
cajón no cambian un byte, y **ningún diámetro se movió**. De las cuatro
configuraciones se MIDIÓ UNA, «sí · no», con el repositorio de normas
enlazado: 4521 passed, 16 skipped, collected 4537 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 4509 passed, 28 skipped). **Las otras tres se dicen como
derivadas, no como medidas**, por lo mismo que en T-0: el contenedor no
tiene `tkinter` y desinstalar PyMuPDF apagaría la verificación normativa de
la sesión; la derivación suma 131 a las de T-2 y pasa 15 de ellos a
`skipped` en las dos columnas sin PyMuPDF. **T-2 de la cadena T (2026-11-11) sumó CIENTO SETENTA Y UN
tests netos** (173 nuevos y dos casos parametrizados que desaparecen), y
uno solo lleva la marca `pdf`; ninguno depende de Tk: los 160 de
`tests/test_t2_hidraulica.py` —la aceptación de los cierres de método de la
hidráulica: el barril horizontal (`S = 0` en M3 y M4, HDS-5 num. 3.3.4;
`modelos.SinTiranteNormal`, perfil `H2`, V1/V2 sobre el perfil y V3/d50
sobre la velocidad de salida, también con el control de entrada
gobernando), la banda de pendiente y V10 (`M5.v10_pendiente_conducto`,
evaluada detrás de V4b para que V5 y V8 no la tapen en el alcance de
expediente), el borde libre cuando lo toma el nivel del receptor
(`borde_libre_bajo_tw_ahogante`, con la monotonía de la lectura «aviso» a
lo largo del TW medida con seis TW y dos diámetros), la sección medida del
receptor con su validación de forma y de dominio, las 26 filas de la Tabla
A.1 valor a valor, el ejemplo publicado de HDS-5 (`CP_HDS5_DG1`: tolerancia
de lectura del 3 %, cinco casillas fuera censadas con su causa, las dos
filas de metal corrugado por intervalo con el n acotado por la Tabla B.1, y
ninguna fila en la transición), los indicadores que suben a los avisos y al
RESUMEN, el receptor seco y los diámetros de la línea base leídos del
archivo comprometido—; los siete anclajes de `test_decisiones_diferidas`
para las fichas de la Parte XLI (T2-01..07); los tres que crecen solos en
`test_ext5_forma_gui` con los tres criterios nuevos (79 → 82); uno en
`test_M3_hidraulica` y uno en `test_M4_control` (la pendiente NaN junto a la
negativa); y uno en `test_pf4_regimen_v2b` (C-01 sin declarar el régimen).
Los dos que desaparecen: el caso de `hw_entrada_fuera_de_rango` en el
parametrizado de vacíos de `test_criterios_adoptados` y su ejemplo de
`--declarar` en `test_guia_perfil`, porque el criterio ya tiene valor de
archivo. **Estos tests no se escribieron en rojo antes del código**: se
midieron después contra un árbol exportado de `87d1ce7` —126 rojos y 34
verdes, que son guardias que valen antes y después— y la mutación de lo
tocado se midió con el arnés de EXT-11 (283 mutantes, 28 vivos, censados
uno a uno en `MUTANTES_VIVOS_DE_T2`; ficha T2-07). Se reescribieron al contrato nuevo, sin
sumar ni restar, `test_M5_verificaciones` (doce filas y doce funciones;
V10 entre V4b y el hueco de V5), `test_cierre_perfil`, `test_cli`,
`test_ayuda_entrada`, `test_ea_perfil_lamina` (el perfil `H2`),
`test_ext11_mutacion` (dos claves del censo cambian de texto),
`test_ext11_propiedades` (el receptor seco), `test_memoria_sustentada` (dos
fundamentos que la corrida por defecto no alcanza), `test_dimensional_piloto`
(la relación de V10, que la corrida de referencia ya alcanza), `test_ext8`
(el techo de tamaño por punto, remedido: 60.8 KB), `test_sin_literales` (la
marca nueva de `dominios.py`), `test_pf1_hw_fuera_de_
rango` y `test_pf4_regimen_v2b` (los dos criterios con valor de archivo; el
caso patrón de PF-1, con S = 0.40, abre el techo de V10 para seguir midiendo
el piso), `test_seccion_rectangular` (quince cartas de cajón de Forma 2,
con el mínimo y el máximo sin mover) y `test_t0_gobernanza`, cuya tabla de
lo que cada prompt escribe en el tracker deja de fijar «cerrados == los de
T-0» y crece con cada integración. Cierra INF-5.1.6 e INF-5.1.7; en parte
INF-3.2.2, INF-3.2.6, INF-3.2.7 e INF-3.2.8; INF-3.2.5 por verificación
contra el PDF, sin tocar V4; e INF-3.2.9 queda diferido con ficha. Dos
valores de archivo cambian —`regimen_v2b` a `indicador_con_aviso` y
`hw_entrada_fuera_de_rango` a `energia_critica`— y los dos siguen siendo
[A]; `borde_libre_bajo_tw_ahogante` queda en `no_cumple` por decisión del
dueño, con «aviso» como alternativa barrible. La línea base de la Familia C
se regeneró por FORMATO, clasificado diferencia a diferencia con el
comparador de E-B (README de la línea base): la fila V10, los avisos, la
línea «Verificaciones con aviso» del RESUMEN, las huellas y los recuentos;
los dos CSV de resumen no cambian un byte y **ningún diámetro se movió**
(diez corridas medidas antes y después). De las cuatro configuraciones se
MIDIÓ UNA, «sí · no», sobre `origin/main` en el commit `tesis(T-2)`, con el
repositorio de normas enlazado: 4390 passed, 16 skipped, collected 4406 (y
sin `NORMAS_DIR`, sobre el mismo árbol: 4383 passed, 23 skipped). Las otras
tres se dicen como **derivadas**, por la misma razón que en T-0 —el
contenedor no tiene `tkinter` y no se puede instalar—: de los 171, uno
lleva la marca `pdf` (40 saltos sin PyMuPDF donde eran 39) y ninguno
depende de Tk (siguen siendo 13).
**T-0 de la cadena T (2026-11-11) sumó CINCUENTA Y SIETE
tests netos** (58 nuevos y uno retirado de un censo), sobre un árbol que ya
llevaba TRES que esta tabla no contaba: el orquestador de la cadena midió
`c2262a2` en «sí · no» y dio 4162 passed, 16 skipped, collected **4178**,
contra los 4175 que aquí se leían. El clon tiene un solo commit y los tres
no se pueden atribuir por historial; `c2262a2` es el cuarto bloque del
rediseño visual de la GUI, que sumó al menos el anclaje de la ficha
REDISEÑO-3-01 en `test_decisiones_diferidas`, y ninguno de los tres depende
de PyMuPDF ni de Tk (los 16 saltos de «sí · no» son los mismos). Los 58 de
T-0: los 53 de `tests/test_t0_gobernanza.py` —la aceptación de la
gobernanza de la cadena T, escrita primero en rojo con `xfail(strict=True)`
de módulo (medidos 50 xfailed y 3 XPASS antes de tocar nada; los tres valen
antes y después) y liberada al corregir: las 64 filas `INF-` del tracker con
el número del INFORME como ID canónico y cada alias de la cadena llevando a
una sola fila; la hoja de ruta v8 titulada v8, con el encabezado del CSV de
`M0_carga.COLUMNAS` y las claves de Manning y las dos gravedades del Anexo B
comparadas por AST con el código; los docstrings de M1, M4, M5, MD y M11 que
dejaron de afirmar lo que el código no hace (`_lo_que_afirma` descuenta lo
que el docstring cita entre «»: la casa no borra la frase que corrige); el
código de paso `F4.YC` con `F4.YC_RECT` como alias y las dos citas nuevas de
HDS-5; el contrato de entradas, que nombra cada columna, cada dato externo y
cada [S]; `NORMAS_DIR` con su caída y su error; HEC-14 y WSDOT como fuente
presente con la paginación que predice sus páginas; y la huella de la copia
de la cadena—, el de `test_ext6_registro_normativo` que mira el repositorio
de normas enlazado (la mitad de PC-23 que T-0 abre) y los cuatro anclajes de
`test_decisiones_diferidas` para las fichas de la Parte XL (T0-01..04). El
retirado: `M11_reporte.bloque_umbrales` sale del censo
`PUBLICAS_SIN_REFERENCIA_EN_TESTS`, porque un test ya la nombra. Ningún
archivo más sumó ni restó: `test_seccion_rectangular`, `test_M4_control`,
`test_ext2`, `test_dimensional_piloto` y `test_indice_formulas` cambian el
literal `F4.YC_RECT` por `F4.YC`; `test_normativa_pdf` y `test_ext6` buscan
los PDF por `fuentes.ruta_pdf`; `test_vigencia_fuentes` y `test_ext6`
admiten la tercera fecha de verificación; `test_ext11_cruce_temarios` espera
367 filas. Cierra INF-5.1.1, INF-5.1.2, INF-5.1.4, INF-5.1.10, INF-5.1.11 e
INF-5.1.14. La línea base de la Familia C se regeneró por FORMATO,
clasificado diferencia a diferencia (README de la línea base): las dos
huellas, «(v7)» → «(v8)», el código de paso y su ancla, las dos
procedencias de fórmula, las dos citas nuevas en el anexo y los textos de
`v_max_tmc` / `v_max_hdpe`; los cuatro `cli_*.txt` y los dos CSV de resumen
no cambian un byte, los tres JSON sólo en `criterios_sha1`, y **ningún
diámetro se movió**. De las cuatro configuraciones se MIDIÓ UNA, «sí · no»,
sobre `origin/main` en el commit `tesis(T-0)`, con el repositorio de normas
enlazado: 4219 passed, 16 skipped, collected 4235 (y sin `NORMAS_DIR`, sobre
el mismo árbol: 4212 passed, 23 skipped). **Las otras tres NO se pudieron
medir en el contenedor de T-0 y se dicen como derivadas, no como medidas**:
no tiene `tkinter` en ninguno de sus cuatro intérpretes (medido:
`python3`, 3.11, 3.12 y 3.13 dan `ModuleNotFoundError`) y `apt-get install
python3-tk` devuelve 503 según lo midió la sesión orquestadora de la cadena
(el espejo de paquetes no responde desde esa red), de modo que las dos
columnas «Ventana Tk = sí» no se pueden levantar; y las dos
«PyMuPDF = no» exigen desinstalarlo, que en un contenedor que no puede
reinstalar con garantía es apagar la mitad de la verificación normativa de
la sesión. La derivación: de los 58, cuatro llevan la marca `pdf` (39 saltos
sin PyMuPDF donde eran 35) y ninguno depende de Tk (siguen siendo 13).
**El cierre de los hallazgos abiertos (2026-09-22: C10,
C05, C09, C11 y C14, cinco commits `cierre(...)` de `67d5810` a `19bcf5a`)
sumó SESENTA tests netos**, y sólo uno depende de Tk: los 16 de
`tests/test_cierre_c10.py` —C5-02 (la fila del ke recuperada por
`M4._fila_del_ke_numerico`, rótulos sólo si el número es la celda, una fila
«Box» rechazada para el tubo), PC-27 (`modelos.EstadoDeVerificacion` como
fuente única con `cumple` y el veredicto del paso como vistas comprobadas,
NO_APLICA con productor real en V5 de la Familia C, la marca en M11, la
traza y la CLI de texto) y PC-32 (`esviaje_max_grados`, [A] opcional de
perfil leído por `M7.factor_esviaje`), escritos en rojo con `xfail(strict=True)`
—12 xfailed, 2 XPASS invariantes— y liberados, más los que dejó el auditor
adversarial (el hueco censado impreso encima de la fila «no aplica», la CLI
que decía `[OK]`, el mutante de la frontera del esviaje)—; los 17 de
`tests/test_cierre_c05.py` —PC-24 (`borde_libre_y_sobre_d_max` y
`velocidad_minima_autolimpieza_m_s`, [A] de perfil con el valor recomendado
por defecto, sólo endurecibles: `_umbral_adoptado_v1/_v2`, V1 con ventana
numérica (0, 0.75), y `MD.disenar_punto` relanzando el `DatoInvalidoError`
de un criterio en vez de tragarlo como «material no evaluable») y R48-030
(la v8 nombra WSDOT M 23-03.12 Tabla 8-4 en los seis sitios que decían «por
extraer»), 14 en rojo y liberados, más los tres del auditor (la memoria bajo
endurecimiento, la puerta de V1, el bloqueo del criterio)—; los 12 de
`tests/test_cierre_varios.py` —R48-001 (cinco citas nuevas verificadas: el
glosario y la Fig. 1.10-a del Manual de Puentes, AASHTO 1.2, HDS-5 §1.2 en
sus dos páginas; `DIS-LUZ-DENOMINACION` con el desacuerdo real, por vano
contra ancho total y 6.0 contra 6.096 m; la vía 2 del canal con usuario otra
vez), PC-31 (`registro.construir` con `lru_cache`, una instancia) y SIS-F-13
(la Tabla 5 de M 170M, PDF 10, el único escaneo real del ejemplar, transcrita
por imagen en `AASHTO_M170M.T5`: CP11 con dorado para los tres materiales)—;
el DUODÉCIMO test de ventana real de `test_gui_contrato`
(`tests/apoyo/gui_caras_normativa.py`: RANGO, CATALOGO y CAMPO construidas y
declaradas por `boton.invoke()`, SIS-F-01); dos parametrizados más en
`test_M2_material` (el concreto en CP11); tres que crecen solos en
`test_ext5_forma_gui` (76 → 79 criterios); y los nueve anclajes de
`test_decisiones_diferidas` para las fichas de las Partes XXXVI a XXXVIII
(C10-01..03, C05-01..02, C11-01, C14-01, C09-01..02). Ningún archivo restó
tests: `test_M5`, `test_cli`, `test_canal_discrepancias` y
`test_ext11_mutacion` reescribieron aserciones al contrato nuevo (V5 como
fila «no aplica», `criterio_aplicado` en V1/V2, la discrepancia declarada
por el paso 2.1, los operandos nuevos del censo de mutantes). Dos auditores
adversariales por cluster; el segundo refutó dos cierres —«las tres fuentes
coinciden» y «la PDF 10 está en blanco»— y los dos se rehicieron con las
fuentes que faltaban (`19bcf5a`). La línea base de la Familia C se regeneró
por FORMATO en cada cluster (clave `estado` del JSON, textos del ke y de
V1/V2, criterios usados, citas del paso 2.1 y su discrepancia; ningún número
de cálculo se movió). Aviso de entorno: durante la sesión `/dev/null` del
contenedor quedó sustituido por un archivo regular (un `cli.py --json
/dev/null` del auditor: `exportar` reemplaza el destino de forma atómica) y
los tests del subproceso del PDF fallaron hasta restaurarlo con `mknod` en
otra ruta y `mv`. Las cuatro configuraciones se MIDIERON sobre un checkout
limpio (`git worktree`) de `origin/main` en `19bcf5a`, en serie y sin otra
suite en marcha: las dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla,
las dos sin PyMuPDF desinstalándolo y reinstalándolo; `collected = 4175` en
las cuatro. Se midieron ANTES de sellar los documentos generados —los 13
tests de sincronía de `manifiesto_citas`, `trazabilidad.csv`,
`indice_formulas` y la convención de `test_ext9` fallaban en las cuatro por
el mismo motivo, ninguno depende de PyMuPDF ni de Tk— y la tabla suma esos
13 a cada `passed`; «sí · sí» se remidió sobre el commit de cierre con los
sellos puestos, y es el par que llevan los sellos. **PF-6 (2026-09-21) sumó DIECISIETE tests netos** (18
nuevos y un caso parametrizado retirado), y uno depende de Tk: los 15 de `tests/test_pf6_cabos.py` —los tres cabos, escritos primero
en rojo con `xfail(strict=True)` por test (medidos 12 xfailed y 0 XPASS antes
de tocar código) y liberados al corregir: (a) R48-007, el techo
`CBR_MAX_FISICO = 100.0` retirado contra la fuente primaria (verificador
normativo sobre el Manual de Suelos: S5 «CBR ≥ 30%» abierta, Cuadro 4.11
pág. 37; «Mínimo 100%» de la base granular, Cuadro Nº 10.2 pág. 108; «Base
Granular CBR 100%», Cuadro 12.13 pág. 129; y ningún techo en 281 páginas) y
sustituido por `CBR_MIN_FISICO`, con un CBR de 250 % que se carga y el piso
que sigue; (b) el editor escalar que suelta la fila cuando el texto deja de
ser su clave, medido en la ventana de verdad (`tests/apoyo/gui_eb_real.py`,
bloque 3b: el único de los 15 que depende de Tk); (c) `CAMPOS_OMITIDOS`
contrastado ruta a ruta contra el comportamiento del comparador, los
diferidos por contenido y un bool que nunca es igual a un número— y los tres
anclajes de `test_decisiones_diferidas` para las fichas de la Parte XXXV
(PF-6-01..03). Ningún archivo restó tests: `test_M0_carga` retira el caso
«250» de su parametrizado (ya no es inválido), `test_M5_verificaciones`
barre desde el piso y por encima de la tabla en vez de hasta el techo, y
`test_sin_literales` baja el censo de marcas de `dominios.py` de 5 a 4 (el
`0.0` del piso es literal exento). Cierra R48-007 entero. La línea base no
se movió: ningún número de cálculo cambia. Las cuatro configuraciones:
«sí · sí» MEDIDA sobre el árbol de PF-6 con `python3-tk` para `python3.12`
y PyMuPDF: 4112 passed, 3 skipped, collected 4115; las otras tres se
derivan de las de PF-5 sumando 17 `passed` con Tk, y 16 `passed` y 1
`skipped` sin Tk. **PF-5 (2026-09-21) sumó TREINTA Y CUATRO tests**, y ninguno
depende de PyMuPDF ni de Tk: los 32 de `tests/test_guia_perfil.py`, la
guardia de `docs/guia_perfil.md` —la guía de corrida de perfil para un
tesista, que NO se escribe a mano dos veces—: los ocho bloques de comandos
de la guía se ejecutan en subproceso, en el orden en que la guía los
presenta, con los archivos que la guía muestra (las cercas `archivo=` se
escriben tal cual y el CSV de trabajo se deriva de `tests/ejemplo_puntos.csv`
rellenando la sola celda que la guía dice), y se afirma lo que la guía
promete: el código de salida de cada comando, las líneas del RESUMEN que la
guía imprime contra la salida real, los cuatro puntos dimensionados con los
siete del cajón declarados y `S_conducto ≥ S_cauce`, la advertencia de
corredor sin `--datos-sitio` y su ausencia con él, la sesión mínima válida
que `--sesion` reproduce, `--comparar` y `--barrido`; las siete tablas
generadas se comparan texto a texto con `tests/apoyo/guia_perfil.py`, que
las deriva de sus símbolos (`M0_carga.COLUMNAS`, `VACIOS_ADMITIDOS`,
`servicio.CLAVES_EXTERNAS` con la bandera leída del parser real,
`datos_sitio.DATOS_SITIO`, `ca.criterios_de_perfil_sin_valor()` con
`Criterio.forma` y su ventana, `M11.COLUMNAS_RESUMEN_CSV`,
`sesion.sesion_vacia`) y se regeneran con `python -m tests.apoyo.guia_perfil`;
los diez ejemplos de `--declarar` (uno por criterio de perfil sin valor, en su
orden, con todas las formas) pasan la puerta real, y el README enlaza la
guía. El único `lento` es el del PDF por la sesión, que acepta los dos
finales declarados de `--pdf`. Los otros dos son los anclajes parametrizados
de `test_decisiones_diferidas` para las dos fichas de la Parte XXXIV
(PF-5-01, PF-5-02). No cierra IDs; las dos fichas registran lo que el prompt suponía y el árbol no
sostiene: DIEZ [A] de perfil sin valor desde PF-1 y no nueve, el `si` de
«Expediente cerrado» a perfil cuando nada bloquea al alcance declarado, la
copia del CSV con la coronación de C-01, y la sesión que la CLI no escribe.
La línea base no se movió: PF-5 no toca `src/`. Las cuatro configuraciones:
«sí · sí» MEDIDA sobre el árbol de PF-5 con `python3-tk` instalado para
`python3.12` (el intérprete de la suite es 3.11 sin tkinter; la sonda lo
encuentra sola) y PyMuPDF presente: 4095 passed, 3 skipped, collected 4098;
las otras tres se derivan sumando 34 a las de PF-4, porque ninguno de los
34 depende de PyMuPDF ni de Tk. **PF-4 (2026-09-21) sumó TREINTA tests**, y ninguno depende
de PyMuPDF ni de Tk: los 27 de `tests/test_pf4_regimen_v2b.py` —la
aceptación de PF-4: el régimen con que V2b aplica el indicador de HDS-5
§5.3.3 deja de estar cableado como «decisión conservadora del proyecto» y
pasa al criterio [A] de perfil `regimen_v2b` (categoría, valor de archivo
`umbral_duro`, ventana `umbral_duro` / `indicador_con_aviso`); 19 escritos
primero en rojo con `xfail(strict=True)` por test (medidos 19 xfailed, 0
XPASS, 2 passed y un teardown que fallaba en el árbol viejo por no existir
la clave) y liberados al corregir: la ficha, la guardia de forma sobre seis
valores malos y los dos buenos, `TipoDeVeredicto.INDICADOR` y su exigencia
de umbral, M11 pintándolo como aviso, V2b bajo los dos regímenes con la
elección y su fundamento en el paso, el consumidor que rechaza un régimen
que burla la puerta, la línea base sin mover un número medida con el
comparador de E-B, C-01 por la CLI real en las dos direcciones, y el editor
de categoría de la pestaña 2; más los que dejó la auditoría adversarial que
la sesión ejecutó al caerse el subagente (el literal buscado DENTRO del
bloque de C-01 y la clase de la fila, porque el literal ya se imprimía en
A-01 y A-02 y un `in html` a secas pasaba vacuo; y el barrido de PF-3, que
leía el veredicto sólo de `.cumple` y se habría callado un CUMPLE →
INDICADOR)—, los dos anclajes de `test_decisiones_diferidas` para las fichas
de la Parte XXXIII (PF-4-01, PF-4-02) y el que crece solo en
`test_ext5_forma_gui` con el criterio nuevo (75 → 76 criterios). Ningún
archivo restó tests. Cinco mutantes medidos y los cinco muertos: `cumple or
aviso` → `cumple`, INDICADOR → CUMPLE, `not cumple` → `cumple`, el paso sin
la elección del régimen, y el `nivel` del criterio a expediente. La línea
base de la Familia C se regeneró por FORMATO, clasificado diferencia a
diferencia con el propio comparador contra `a96bbec`: la huella
`criterios_sha1`, la clave nueva `veredicto` de cada verificación (26 en el
JSON ancho, 4 en los otros dos), el texto de `NUMERAL_V2B`, el criterio
nuevo entre los usados, `verificacion_pendiente` 21 → 22, y en las memorias
el CSS del aviso, la huella de la hoja de ruta y el recuento «75 / 36» →
«76 / 36»; ningún número de cálculo se movió y el CSV resumen, los tres
`cli_*.txt` salvo el numeral y la memoria del cajón quedaron intactos. Las
cuatro configuraciones: «sí · sí» MEDIDA sobre un checkout limpio
(`git worktree`) del commit `ext(PF-4)`, sin otra suite en marcha: 4061 passed,
3 skipped, collected 4064; las otras tres se derivan sumando 30 a
las de PF-3, porque ninguno de los 30 depende de PyMuPDF ni de Tk.
independientes. **PF-3 (2026-09-21) sumó TRECE tests**, y ninguno depende de
PyMuPDF ni de Tk: los 12 de `tests/test_pf3_barrido.py` —la aceptación del
barrido de sensibilidad: los siete del prompt escritos primero en rojo con
`xfail(strict=True)` por test (medidos 7 xfailed y 0 XPASS antes de tocar
código) y liberados al corregir (tres corridas sobre el mismo árbol con
`criterios_sha1` y `csv_sha1` idénticos, cada una con SU valor declarado y
su procedencia; la tabla leída del volcado y la primera corrida IGUAL a sí
misma; el valor fuera de la ventana que no corre nada, medido con
`servicio.correr` interceptado; el criterio de tabla que exige fila o nota
por la misma puerta; el estado del proceso repuesto con la MISMA
procedencia; la guardia por AST; y la CLI con dos barridos, el JSON y la
memoria que no se escribe), más los cinco que dejó el auditor adversarial
en la parte 2 (la comparación con la PRIMERA corrida y el «no comparable»
cuando A-01 pasa de control de entrada a salida en ke = 0.9; `_filas_de`
sobre una comparación sintética; el punto que deja de dimensionar y dice
V3; la base aplicada en la puerta como en la pestaña 2; y la CLI que
cierra la puerta de todos los barridos antes de correr, avisa de las
banderas que no aplica y nombra la clave inexistente y el valor vacío)— y
el anclaje de la ficha PF-3-01 en `test_decisiones_diferidas`. Ningún
archivo restó tests ni se reescribió. La línea base no se movió: el
comparador cambió tres literales por constantes con el mismo texto. Las
cuatro configuraciones: «sí · sí» MEDIDA sobre un checkout limpio
(`git worktree`) de `d4a4488` (el segundo commit `ext(PF-3)`, con los
ajustes del auditor), sin otra suite en marcha: 4031 passed, 3 skipped,
collected 4034; las otras tres se derivan sumando 13 a las de PF-2, porque
ninguno de los 13 depende de PyMuPDF ni de Tk. **PF-2 (2026-09-21) sumó QUINCE tests**, y ninguno depende de
PyMuPDF ni de Tk: los 14 de `tests/test_pf2_prevuelo.py` —la aceptación
del cuarto bloque del anticipo, escrita primero en rojo con
`xfail(strict=True)` por test (medidos 10 xfailed y 0 XPASS antes de tocar
código) y liberada al corregir: la luz en los cuatro puntos y lo de cada
familia (la coronación sólo en C-01, la longitud hidráulica sólo en B-01,
el caudal y la pendiente del canal en C-01 con S_conducto nombrado en la
misma entrada); con el JSON ampliado y la luz sólo queda la coronación; lo
que espera a un tablero no se confunde con lo que detiene; el TW sin vía
cae en el criterio con el mismo predicado del resolvedor; la UNIÓN contra
tres corridas reales con lo de más censado y medido; la guardia por AST de
que ni el bloque ni `cli._prevuelo` corren el pipeline; la CLI que sale con
1 y con 0; y las líneas del bloque; más los cuatro que dejó el auditor
adversarial en la parte 2: la celda obligatoria vacía que el JSON no
sustituye, la celda no numérica y la familia ilegible como faltas de
carga, la partición exacta de las claves externas sin columna, y la CLI
que sale con 1 cuando la cabecera detiene la carga— y el anclaje de la
ficha PF-2-01 en `test_decisiones_diferidas`. Ningún archivo restó tests:
`test_gui_contrato` fija las dos llamadas nuevas del panel,
`test_sin_literales` censa las cinco marcas de columna de la tabla nueva
de `gui/app.py` (45 → 50) y `test_ext9` retira ahora la marca de tiempo
REAL del JSON (`expediente.generado_utc`; retiraba una clave inexistente y
sólo pasaba con las dos corridas en el mismo segundo, que el aislamiento
de PF-2 destapó). La línea base no se movió. Las cuatro configuraciones:
«sí · sí» MEDIDA sobre un checkout limpio (`git worktree`) de `654ca60` (el
segundo commit `ext(PF-2)`, con los ajustes del auditor), sin otra suite en
marcha: 4018 passed, 3 skipped, collected 4021; las otras tres se derivan
sumando 15 a las de PF-1, porque ninguno de los 15 depende de PyMuPDF ni
de Tk. **PF-1 (2026-09-21) sumó CIENTO DOCE tests**, y ninguno
depende de PyMuPDF ni de Tk: los 13 de
`tests/test_pf1_hw_fuera_de_rango.py` —la aceptación de PC-03, escrita
primero en rojo con `xfail(strict=True)` por test (medidos 17 xfailed y 0
XPASS antes de tocar código sobre `863aac8`: los 11 ítems más 6 teardowns
del fixture `_limpio`, que en el árbol viejo fallaban al no existir la
clave) y liberada al corregir: la
carta fuera de rango es un vacío declarable (`CriterioPendienteError` sobre
`hw_entrada_fuera_de_rango`) con el par (Q, S) y S* en el mensaje; el
límite de signo analítico que `M4.pendiente_limite_de_signo` publica;
«energia_critica» adopta H_c y lo publica en `ControlEntrada.piso`;
«descartar» es la conducta anterior; la ficha es de perfil, categórica y
con ventana; el bloqueo viaja con criterio y la pestaña 4 y el JSON lo
pintan; declarado en caliente el punto dimensiona y la memoria lo
declara; S* no crece con D bajo Forma 1; y los dos que dejó el auditor
adversarial: el piso acota el SIGNO y por debajo de S* manda la ecuación
aunque dé menos que H_c, y bajo Forma 2 S* no es monótono y no alcanza el
dominio del dato—, los 96 de la propiedad P9 en
`tests/test_ext11_propiedades.py` (bajo S* la carta entrega carga sobre la
malla Q × D × fracción, en las tres ramas; S* no crece con D), el anclaje
de la ficha PF-1-01
en `test_decisiones_diferidas` y los dos que crecen solos con el criterio
nuevo (`test_ext5_forma_gui`, `test_criterios_adoptados`). Ningún archivo
restó tests: el parametrizado de MAT-D10 de `test_M4_control` mide ahora
los dos caminos (sin declarar y «descartar») y `test_cierre_perfil` cuenta
DIEZ vacíos de perfil, tres no invocados por el corredor. La línea base de
la Familia C se regeneró por FORMATO, medido con `diff`: `criterios_sha1`,
`hoja_ruta_sha1` (la nota «Corregido (PF-1)» de la v8 §4.2), la clave
nueva en la lista de criterios sin valor, el recuento «74 / 35» → «75 /
36» y las tres claves `hw_entrada_*` del JSON en `null`; ningún número de
cálculo se movió (README de la línea base). El auditor adversarial dejó
además la enmienda de la v8 con su declaración en el punto de uso, la
`justificacion` que promete sólo lo que el código hace, la monotonía
acotada a la Forma 1 y el piso viajando en `ResultadoHidraulico` y en el
JSON por punto. Las cuatro configuraciones: «sí · sí» MEDIDA sobre un
checkout limpio (`git worktree`) de `3d478d3` (el tercer commit
`ext(PF-1)`, tras el auditor y las dos guardias de la suite), sin otra
suite en marcha: 4003 passed, 3 skipped, collected 4006; las otras tres se
derivan sumando 112 a las del cierre de E-B, porque ninguno de los 112
depende de PyMuPDF ni de Tk.
**El cierre de E-B (2026-09-21, tras la revisión) sumó UN
test**, sin dependencia de PyMuPDF ni de Tk: el de
`tests/test_eb_editores_comparador.py` que cierra el hueco del texto que
nombra otra fila (escrito en rojo con `xfail(strict=True)`, medido 1
xfailed y 0 XPASS, y comprobado rojo otra vez sin la guardia antes de
liberarlo). Con él el archivo tiene 63. Se midió «sí · sí» sobre un
checkout limpio de `fbc57e6` (3891/3, collected 3894) y las otras tres
se derivan sumando 1, como en EXT-1 y EXT-2, porque el test no depende
de PyMuPDF ni de Tk. **E-B (2026-09-21) sumó SESENTA Y
NUEVE tests netos**, y ninguno depende de PyMuPDF; uno depende de Tk: los
62 de `tests/test_eb_editores_comparador.py` —la aceptación de E10, E14,
E13 reducido y E21 acotado: 53 en la parte 1 (51 funciones más un
parametrizado de tres casos), escrita primero en rojo con
`xfail(strict=True)` por test (medidos 52 xfailed, 1 passed y 0 XPASS
antes de tocar código; 49 XPASS al escribirlo, y liberados), más los
NUEVE que dejó el auditor adversarial en la parte 2 —y no ocho, que es lo
que decía el mensaje de `5a35ed3` («61 (+8)») y lo que sumaba el desglose
anterior de este párrafo: se contaron por nombre de función en el diff—
(el `descomponer_valor` que recortaba un triple y declaraba el recorte en
verde; el `repr` que ponía comillas a un texto; la pestaña 2 que no
declara desde un editor que no refleja el literal; la fila no elegible
que entraba con nota por otra puerta; la serie de claves que declara desde
la tabla; el dato de ensayo que exige su trazabilidad; el dict de tabla
que nombraba una fila cuyas celdas no eran el valor; el comparador con
falsos IGUALES en bloqueos, iteraciones y listas de estado; el NaN y el
infinito que caían del lado de «igual». La fila que un número «adivinaba»
y la categoría de tabla que proponía una clave que la guardia rechazaba
fueron REESCRITURAS de tests existentes, no altas) y el UNDÉCIMO test de ventana
real (`tests/apoyo/gui_eb_real.py`: la serie de pares par a par, el dict
con un campo fuera de ventana que no declara nada, la fila de la Tabla C.2
que pone 0.5 y el 0.55 que exige nota, las dos columnas nuevas y la
comparación de la corrida con su propio volcado)—, el de `test_linea_base`
con el comparador como segundo consumidor de la línea base, los seis
anclajes de `test_decisiones_diferidas` para las fichas de la Parte XXIX
(EB-01..06) y el parametrizado de `test_gui_contrato` que crece con
`gui/editores.py` en `ARBOLES_DE_LA_GUI`; menos UNO: el censo
`PUBLICAS_SIN_REFERENCIA_EN_TESTS` retira `M11_reporte.ancla_de_criterio`,
que la suite ya nombra. Ningún archivo restó tests: `test_cierre_perfil`
corta la memoria por el ancla y no por el título (el índice lo repite como
enlace), `test_ext4` conoce el quinto botón de la pestaña 4,
`test_sin_literales` censa `gui/editores.py` y las dos marcas de columna de
`gui/app.py` (43 → 45). La línea base de la Familia C se regeneró por
FORMATO, medido con `diff`: las claves `responsable` y `evidencia` en
`criterios.bloquearon` de los dos JSON con bloqueantes, y el índice, sus
tres reglas de estilo y el `id` de cada bloque de punto en las tres
memorias de la CLI; ningún número de cálculo se movió (README de la línea
base). Las cuatro configuraciones se MIDIERON sobre `origin/main` en
`5a35ed3` (el segundo commit `ext(E-B)`, con las correcciones del auditor,
fusionado por fast-forward), en serie, sobre un checkout limpio
(`git worktree`) y sin otra suite en marcha: las dos sin Tk sin `DISPLAY` y
con un `xvfb-run` que falla, las dos sin PyMuPDF desinstalándolo y
reinstalándolo; `collected = 3893` en las cuatro. **E-A (2026-09-21) sumó CUARENTA Y CINCO tests**, y
ninguno depende de PyMuPDF ni de Tk: los 36 de
`tests/test_ea_perfil_lamina.py` —la aceptación de NOR-HDS-05 entera, el
perfil de la lámina de agua por paso directo (HDS-5 pág. 3.12 / PDF 94
con la Ec. 3.7; umbrales de la pág. 3.24; Section 3.5.1): los 26 primeros
escritos en rojo con `xfail(strict=True)` de módulo —medidos 26 xfailed y
0 XPASS antes de tocar código— y liberados al corregir (los tipos
`PerfilLamina`/`TipoDePerfil`, los DOS dorados de LÍMITE que el conflicto
#7 admite sin corrida externa —flujo lleno de punta a punta, que reproduce
la fórmula cerrada de `control_salida` a 1e-9, y flujo uniforme en su
propia asíntota—, el balance de energía por estación y la monotonía de
M1/M2/S1, la convergencia N frente a 2N, la fracción analítica de longitud
llena, el caso (b) del dictamen que pasa a ENTRADA porque la S1 no alcanza
la entrada, el caso (c) con HW por remanso, V1/V2 sobre el perfil, la
corrida sin bloqueos «no evaluables», la regla vinculante #12 por AST y
las siete citas verificadas); los diez restantes los dejaron el auditor
adversarial (la asíntota y_n' de la Ec. 3.7 frente al y_n de Manning, la
banda 0.75–1.2 donde manda la comprobación si pide más carga, el TW a
1e-9 de la clave, el punto fijo sobre la asíntota) y el arnés de mutación
(`V_entrada_m_s` del retorno UNIFORME, los escalones mínimos)—, el de
`test_cli` (B-01 ahogado no cierra por V2 en ningún D), los siete
anclajes parametrizados de `test_decisiones_diferidas` para las fichas de
la Parte XXVIII (EA-01..07) y el que crece solo en `test_ext5_forma_gui`
con el criterio nuevo `fraccion_llena_mayor_parte` (73 → 74 criterios).
Ningún archivo restó tests: el bloque (b) de `test_ext3_regimen_barril`
se reescribió a la verdad nueva con el mismo número, `test_cierre_perfil`
(B-01 con V1/V2 evaluadas), `test_dimensional_piloto` (F4.PERFIL@4.3c/4.3d;
`K_FRICCION_SI` ya la nombra el paso 4.3c), `test_ext2` (HW multicelda
contra `perfil.HW_aproximado_m`), `test_ext11_mutacion` (censo remedido:
62 supervivientes con razón, 20 nuevos del perfil, un hueco real cerrado),
`test_ext8` (techos remedidos: 51.4 KB y 16.0 páginas por punto),
`test_sin_literales` (ocho marcas en M4) y `test_MD` (el y/D del punto
CP-2 con TW = 0 es el máximo del perfil M2, 0.7484, y no el uniforme) se
reescribieron sin sumar ni restar. La línea base de la Familia C se
regeneró y lo que se mueve está declarado en su README y en el commit:
B-01 (TW = 1.00 m) YA NO SE DIMENSIONA —la S1 desde el TW deja V_min =
Q/A(TW) entre 0.06 y 0.11 m/s < 0.25 en todo D: `DisenoNoFactibleError`
con motivo V2 donde antes salía 1.05 m con V1/V2 diferidas—; A-01 y A-02
no cambian de diámetro; el bloqueo «método no evaluable» desaparece de la
corrida; entran las doce claves `perfil_*` del JSON y los pasos 4.3c/4.3d;
cambian `criterios_sha1` y `hoja_ruta_sha1`. La mutación se remidió con el
arnés sobre las once funciones tocadas (242 mutantes: 212 muertos en la
primera vuelta, 87.6 %, 5 más en la segunda, 25 vivos, uno cerrado con
una aserción y 24 censados, ficha EA-06). Las cuatro configuraciones se
MIDIERON sobre `origin/main` en `b7d8def` (el commit `ext(E-A)`, fusionado
por fast-forward), en serie, sobre un checkout limpio (`git worktree`) y
sin otra suite en marcha: las dos sin Tk sin `DISPLAY` y con un `xvfb-run`
que falla, las dos sin PyMuPDF desinstalándolo y reinstalándolo;
`collected = 3824` en las cuatro. **EXT-11 (2026-09-21) sumó MIL CIENTO SESENTA Y DOS tests**,
y ninguno depende de PyMuPDF ni de Tk: los 981 de
`tests/test_ext11_propiedades.py` —las siete propiedades del motor por
mallas (Q = V_sedimentación·A en circular y rectangular; Q_total = N·Q_celda
a través de MD→M4; V_erosion ≥ V_sedimentación; continuidad y linealidad de
la transición en las dos formas; monotonía de HW(Q) bajo Forma 1;
tirante_normal = None para Q ≥ Q_lleno; HW(N=3) ≠ HW(N=1) y HW(N, N·Q) =
HW(1, Q)) más las dos tandas de «lo que la mutación enseñó» (V3 juzga la
rama alta y su paso lo publica; los umbrales de M5 son inclusivos; las
guardias del receptor trapecial, el par de Manning, el ke, la progresión
que se repite, la cota del TW, el motivo de descarte del marco)—, los 119
de `tests/test_ext11_cruce_temarios.py` (PC-29: 71 ítems ALTA/CRÍTICA de
los temarios cruzados con la hoja `Hallazgos`, leída con
`tests/apoyo/tracker.py` sin openpyxl), los 9 de
`tests/test_ext11_mutacion.py` (el arnés `tests/apoyo/mutacion.py`
probándose a sí mismo y el censo de 43 supervivientes con razón), los 47
netos de `test_guardias_de_la_suite` (la guardia PC-21
`afirmaciones_textuales_sobre_codigo` con taint, sus 16 autopruebas y el
censo `TEXTUAL_CON_RAZON`; el censo `PUBLICAS_SIN_REFERENCIA_EN_TESTS` de 29
públicas por tokens NAME con su llamador comprobado por AST, parametrizado),
los 5 anclajes de `test_decisiones_diferidas` para las fichas de la Parte
XXVII (EXT-11-01..05) y el test nuevo de test_cli (la Fase 8 llamada sobre
el concreto real de perfil). Ningún archivo restó tests: el skip permanente
de `test_MD` pasó a ser un test que corre (la ausencia real de M5 en
subproceso), y por eso «sí · sí» salta 3 y no 4; test_anticipo,
test_gui_contrato, test_ext8, test_ext10, test_ayuda_entrada, test_M5,
test_dimensional_piloto se reescribieron al AST sin sumar ni restar. La
mutación medida con el arnés (679 mutantes sobre M3–M5/MD, `_par_de_manning`
y las tres propiedades del par de n): 568 muertos en la primera vuelta
(83.6 %) contra diez archivos objetivo, 65 de los 111 restantes en la
segunda (línea base, cierre de perfil, CLI), 46 vivos, 43 tras la segunda
tanda; sin `hypothesis` ni `mutmut` (consulta sin respuesta, ficha
EXT-11-01). Las cuatro configuraciones se MIDIERON sobre `origin/main` en
`e734c23` (el commit `ext(EXT-11)`, fusionado por fast-forward), en serie,
sobre un checkout limpio (`git worktree`) y sin otra suite en marcha: las
dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla, las dos sin PyMuPDF
desinstalándolo y reinstalándolo; `collected = 3779` en las cuatro, y los
cuatro pares suben 1163 `passed` y bajan 1 `skipped` respecto de EXT-10,
porque ninguno de los 1162 depende de PyMuPDF ni de Tk y el salto
permanente de `test_MD` desapareció. **EXT-10 (2026-09-21) sumó OCHENTA Y CINCO tests**: los 78
de `tests/test_ext10_multiobra.py` —la aceptación de EXT-V-01 y de la fase
E04: 63 escritos primero en rojo con `xfail(strict=True)` por test —medidos
63 xfailed y 0 XPASS antes de tocar código; dos guardias no lo llevaron
porque valen antes y después, y se midió con un XPASS— y liberados al
corregir; los quince restantes los dejó el auditor adversarial (la forma y
el signo de un [S] declarado por sesión: `"0.30"`, `True`, `-0.3`, `[0.3]`,
una orientación fuera de las dos tabuladas, `"dos"` carriles; el origen por
entrada; el volcado que lee «SIN LEER» de la foto; la advertencia por
origen; la precedencia ruta/bloque)—, el DÉCIMO test de ventana real de
`test_gui_contrato` (`tests/apoyo/gui_ext10_real.py`: dos obras por el campo
de la pestaña 1, «Guardar sesion» en formato 3, «Nuevo proyecto», abrir B
tras A, borrar el campo, y un sitio.json malo que no corre) y los seis
anclajes parametrizados de `test_decisiones_diferidas` para las fichas de
la Parte XXVI (EXT-10-01..06). Ningún archivo restó tests: `test_M11_reporte`
admite un [S] entre los bloqueantes, `test_datos_sitio` enumera los campos
nuevos, `test_M9_cabezal` fuerza el valor por `object.__setattr__` para
seguir probando la guardia del consumidor, `test_ext4` lista dos lecturas
estáticas más y `test_sin_literales` censa la marca de `FORMATO_SESION`.
La línea base de la Familia C se regeneró por cambios de FORMATO medidos
con `diff`: `hoja_ruta_sha1` (la v8 enmendada), `criterios_sha1` (los
imports de `NIVEL_*`), el bloque `corredor_del_proyecto` y los campos
`origen`/`fecha`/`declarado_en_caliente` del JSON, la línea «Corredor» y la
fila «Origen» del HTML, y la advertencia de corredor de la obra del
repositorio en las memorias y los volcados; ningún número de cálculo se
movió. Las cuatro configuraciones se MIDIERON sobre `eb926e6` (el segundo
commit `ext(EXT-10)`, con los ajustes del auditor), en serie, sobre un
checkout limpio (`git worktree`) y sin otra suite en marcha: las dos sin
Tk sin `DISPLAY` y con un `xvfb-run` que falla, las dos sin PyMuPDF
desinstalándolo y reinstalándolo. De los 85, ninguno depende de PyMuPDF y
sólo el de ventana real depende de Tk: la columna «Ventana Tk = no» salta
ahora 14 y no 13, y la «PyMuPDF = no» sigue saltando 35 más que la de al
lado. **EXT-9 (2026-09-21) sumó DIECISIETE tests**: los 14 de
`tests/test_ext9_paquete_servicio.py` —la aceptación de PC-08 y de las fases
E01, E02, E03, E03a, E03b y E03c del plan de evolución: diez escritos primero
en rojo con `xfail(strict=True)` —medidos 4 passed, 10 xfailed y 0 XPASS
antes de tocar código— y liberados al convertir `src/` en paquete y mover la
orquestación a `src/servicio.py`; los cuatro que valen antes y después son la
guardia de identidad en subproceso (ningún archivo de `src/` bajo dos claves
de `sys.modules`), el rechazo por AST de `import src.X`, los imports
relativos confinados a `src/normativa/` y el mutante del detector— y los
tres anclajes parametrizados de `test_decisiones_diferidas` para las fichas
de la Parte XXV (EXT-9-01..03). Ningún otro archivo sumó ni restó tests: los tres `monkeypatch` de `test_cli` sobre
lo que el servicio LLAMA pasaron a `servicio`, los barridos de consumidores
de `test_criterios_adoptados` y `test_ext7_cabezal` incluyen ahora
`src/servicio.py`, y las guardias por AST que comparaban la primera parte
del nombre del módulo (`test_ext4`, `test_gui_contrato`, `test_MD`) miran
todas las partes para no quedar vacuas con el prefijo del paquete. La línea
base de la Familia C se regeneró por UNA sola razón medida con `diff`: la
huella `criterios_sha1`, porque `criterios_adoptados.py` cambió sus líneas
de import; ningún número de cálculo ni ningún otro byte se movió. Ninguno de
los diecisiete depende de PyMuPDF ni de Tk, de modo que los cuatro pares
suben 17 exactos. Las cuatro configuraciones se MIDIERON sobre `origin/main`
en `dda328e` (el commit `ext(EXT-9)`, fusionado por fast-forward), en serie,
sobre un checkout limpio (`git worktree`) y sin otra suite en marcha: las
dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla, las dos sin PyMuPDF
desinstalándolo y reinstalándolo. El commit de cierre que sigue a `dda328e`
lleva los ajustes del auditor adversarial (la guardia del anticipo en
`test_gui_contrato`, que buscaba `cli.X` en el `unparse` y quedó verde
sobre el docstring cuando `anticipo.py` pasó a leer `servicio.X`; el censo
de `from cli import` y la segunda corrida con banderas y `--declarar` en
`test_ext9`) sin sumar ni restar tests, y «sí · sí» se remidió sobre él. **EXT-8 (2026-09-20) sumó CUARENTA tests**: los 33 de
`tests/test_ext8_rendimiento_gui.py` —la aceptación del cluster «rendimiento
y GUI no bloqueante» (PC-10, PC-11, PC-12, PC-17), escrita primero en rojo
con `xfail(strict=True)` de módulo —medidos 28 xfailed y 0 XPASS antes de
tocar código, con `src/sesion.py` y `gui/exportacion_pdf.py` todavía
inexistentes— y liberada al corregir: el presupuesto de `import cli` en
subproceso con `-X importtime`, los tres perezosos comprobados en un
proceso limpio, la sonda de weasyprint con sus dos diagnósticos, la sesión
serializada de la CLI con procedencias, el progreso por stdout, el
subproceso real (PDF, equivalencia del JSON, cancelación, fallo), el anexo
con anclas y el cruce `href`↔`id`, el streaming, los techos de tamaño
MEDIDOS (44.6 KB y 14.0 páginas por punto: el objetivo del dictamen no se
alcanzó, ficha EXT-8-01) y la accesibilidad; los cinco últimos los dejó el
auditor adversarial (la sesión del hijo desde la corrida y no desde los
campos vivos, el hijo que no arranca, la bandera escrita que gana, el HTML
no truncado y el enlace roto del anexo)—, el noveno test de ventana real
en `test_gui_contrato` (`tests/apoyo/gui_ext8_real.py`) más el
parametrizado que crece con `gui/exportacion_pdf.py` en `ARBOLES_DE_LA_GUI`,
y los cinco anclajes de `test_decisiones_diferidas` para las fichas de la
Parte XXIV (EXT-8-01..05). Ningún archivo restó tests: `test_seccion_
rectangular` intercepta ahora `scipy.optimize.brentq` (de donde M4 lo toma
en el punto de uso), los dos de `test_M11_reporte` sondean antes de parchear
`WeasyHTML`, y `test_gui_contrato` lee la sesión de `_datos_de_sesion` y la
versión de `src/sesion.py`. La línea base de la Familia C se regeneró
(cambia el formato de la memoria: enlaces, anexo, el paso 2.1 una sola vez;
ningún número de cálculo se mueve: JSON, CSV y volcados intactos). Las
cuatro configuraciones se MIDIERON sobre `origin/main` en `8c1ac25` (el
commit `ext(EXT-8)`, fusionado por fast-forward), en serie, sobre un
checkout limpio: las dos sin Tk sin `DISPLAY` y con un `xvfb-run` que
falla, las dos sin PyMuPDF desinstalándolo y reinstalándolo. De los 40,
uno depende de PyMuPDF (`test_pc12_las_paginas_por_punto_caben_en_el_
techo_medido`, marcado `pdf`) y uno de Tk (el de ventana real): la columna
«PyMuPDF = no» salta ahora 39 y la «Ventana Tk = no» 13. **EXT-7 (2026-09-20) sumó CINCUENTA Y OCHO tests**: los 50
de `tests/test_ext7_cabezal.py` —la aceptación del cluster «cabezal» C07
(EXT-M-05, EXT-M-06, EXT-M-07 y R95-031), escrita primero en rojo con un
`xfail(strict=True)` de módulo —medidos 44 xfailed y 6 XPASS antes de tocar
código: los cinco del caso límite de Rankine y la guardia de que nada se
cablea a la CLI ya se cumplían— y liberada al corregir: la rama vertical con
cortante alto que se detiene en el plano del cortante (11.10.2 / 11.10.1 →
11.12) y en el piso de la ec. (11-32), `verificar_cuantia` con el mismo
argumento, el docstring comprobado por AST, el Ka de Coulomb del Manual
(`MP.2.4.4.1.5.3`, `DIS-HR-KA-COULOMB`) en el estático y la sobrecarga con
el bloque C de CP-9 recomputado con la escritura del Manual, y
`EstabilidadCabezal` con `exigidas`, `pendientes` y un `estable` estricto;
más los tres ajustes que dejó el auditor adversarial (el [A] del régimen
atribuido en la rama perpendicular, la resultante inclinada δ + β tomada
entera como horizontal y declarada, y el rango «−6.25 % a +7.23 %» de la v8
que era falso: medido −11.1 % a +44.4 %)—, los cuatro anclajes
parametrizados de `test_decisiones_diferidas` para las fichas de la Parte
XXIII (EXT-7-01..04), y los cuatro que crecen solos con los dos criterios
nuevos (dos en `test_ext5_forma_gui`, dos en `test_criterios_adoptados`).
Ningún archivo restó tests: los dos de `test_M9_cabezal` que pineaban
`estable` con tres ítems se reescribieron y uno de `test_ext5_forma_gui`
declara además el plano del cortante. La línea base de la Familia C se
regeneró (cambian la declaración del Ka en la nota de la memoria, el
recuento 71 → 73 criterios / 33 → 35 sin valor y la huella de criterios;
ningún número de cálculo se mueve). Las cuatro configuraciones se MIDIERON
sobre `origin/main` en `42a1cb1` (el commit `ext(EXT-7)`, fusionado por
fast-forward), en serie y sin otra suite en marcha —una primera medición se
descartó porque dos instancias del mismo script se solaparon y una
desinstaló PyMuPDF a mitad de la otra—: las dos sin Tk sin `DISPLAY` y con
un `xvfb-run` que falla, las dos sin PyMuPDF desinstalándolo y
reinstalándolo. Los cuatro pares suben 58 exactos, porque ninguno de los 58
depende de PyMuPDF ni de Tk: la cita nueva entra en los barridos de
`test_normativa_pdf` sin sumar un test. **EXT-6 (2026-09-20) sumó CINCUENTA tests**: los 35
de `tests/test_ext6_registro_normativo.py` —la aceptación del cluster
«registro normativo» (EXT-N-01..04, PC-23, PC-26, PC-30, resto de
EXT-G-03), escritos primero en rojo con `xfail(strict=True)` y liberados
al corregir: DG-2018 presente y medida, la guardia «todo PDF de `normas/`
es Fuente presente o está censado», el RNGIV que no vuelve, las citas
nuevas verificadas contra sus páginas, `norma_producto` por (material,
forma), la elección de edición partida en legal y técnica con
`Fuente.vigencia`, los textos 179 / Manning / TR / fricción, y los dos que
dejó el auditor adversarial (la puerta del criterio legal, que con forma
`str` aceptaba la opción «citada» sin fecha ni acto, y el contrato del JSON
leído del AST en vez de un `AssertionError` en la ruta de exportación)—, los nueve
netos de `tests/test_vigencia_fuentes.py` reescrito para el campo y los
dos criterios (25 frente a 16), y los seis que crecen solos con el
criterio nuevo y las cuatro fichas de la Parte XXII (`test_ext5_forma_gui`,
`test_criterios_adoptados`, `test_decisiones_diferidas`). Las cuatro
configuraciones se MIDIERON sobre el árbol de EXT-6 antes del commit (las
dos sin Tk sin `DISPLAY` y con un `xvfb-run` que falla; las dos sin
PyMuPDF desinstalándolo y reinstalándolo): los dos pares con PyMuPDF suben
50 y los dos sin él suben 49 `passed` y 1 `skipped`, porque el T5 nuevo
—el «5.00 m» de `DG2018.304.07.02#INCREMENTO` en
`VALORES_QUE_LA_CITA_SOSTIENE`— abre el PDF y la columna «PyMuPDF = no»
salta ahora 38 y no 37; ninguno de los 50 depende de Tk, y `sha1_de` es
`hashlib`. `origin/main` quedó en `363091b` por fast-forward y «sí · sí» se
remidió sobre un checkout limpio de ese commit: 2413 passed, 4 skipped. **EXT-5 (2026-09-20) sumó DOSCIENTOS SIETE tests**: los 204
de `tests/test_ext5_forma_gui.py` —la aceptación del cluster GUI (EXT-G-01,
PC-13, PC-14, la mitad de FORMA de EXT-V-02/05/06, la de pestaña 2 de
EXT-V-04 y EXT-G-03): los cuatro casos del prompt escritos primero en rojo
con `xfail(strict=True)` —130 fallos y 31 errores medidos antes de tocar
código— y liberados al corregir; la guardia de forma en las 70 claves (70
parametrizados sobre 'cero', uno por clave); el parser único medido por
casos y por AST en las dos ventanas; `validar_contra_rango` en forma MAT-D13
por comportamiento sobre los cinco tipos de rango y por AST; el censo de las
seis externas; y los tres de ventana real sobre `tests/apoyo/gui_ext5_real.py`,
más los dos que dejó el auditor adversarial (la forma `float` de
`cortante_alto_muro_e060_art_11_10_10_2`, que M9 lee con `float()`, y el
parser sólo con cifras ASCII)— y los tres anclajes parametrizados de
`test_decisiones_diferidas` para las fichas de la Parte XXI (EXT-5-01,
EXT-5-02, EXT-5-03). Ningún archivo restó tests: el test de ventana real de
perfil de `test_gui_contrato` se reescribió (dejó de ser ciego a PC-13) y los
de guardias de consumidor pasaron a `con_valor`. Las cuatro configuraciones se
MIDIERON sobre el árbol de EXT-5 antes del commit (las dos sin Tk sin
`DISPLAY` y con un `xvfb-run` que falla; las dos sin PyMuPDF desinstalándolo
y reinstalándolo), y los cuatro pares coinciden con la derivación: ninguno
de los 207 depende de PyMuPDF, y sólo los tres de ventana real dependen de
Tk (la columna «Ventana Tk = no» salta ahora 12 y no 9). **EXT-4
(2026-09-20) sumó TREINTA Y TRES tests**: los
veintinueve de `tests/test_ext4_contexto_corrida.py` —la aceptación del
cluster «estado» (EXT-A-01, EXT-A-02, EXT-G-02, PC-07, PC-09, PC-15, PC-16,
SIS-B-22 y los 27 accesos a `_USADOS` de la suite): los seis casos del
prompt escritos primero en rojo con `xfail(strict=True)` y liberados al
corregir (dos corridas en el mismo proceso, declarar tras correr, el
`csv_sha1` de la corrida, la sesión B vacía, la GUI que invalida el informe,
«Etapas bloqueadas» como una sola cuenta), más las tres guardias que dejan
la corrección probada: el AST de M11 sin lecturas de estado, el barrido de
la suite sin privados y el contexto congelado—, el de ventana real de
`test_gui_contrato` (`tests/apoyo/gui_contexto_real.py`: el texto real de la
etiqueta y el estado real de los cuatro exportadores tras declarar, quitar,
cargar sesión y fallar; es el QUINTO test de ventana real, y por eso la
columna «Ventana Tk = no» salta ahora 9 y no 8) y los tres anclajes
parametrizados de `test_decisiones_diferidas` para las fichas de la Parte XX
(EXT-4-01, EXT-4-02, EXT-4-03). Ningún archivo restó tests: los nueve que
vaciaban `_USADOS` a mano pasaron a las funciones públicas
(`reiniciar_usos`) o al contexto del informe. Las cuatro configuraciones se
MIDIERON sobre el árbol de `main` en `ec55253` (el commit `ext(EXT-4)`,
fusionado por fast-forward): las dos sin Tk con el `xvfb-run` que falla y
sin `DISPLAY`, las dos sin PyMuPDF desinstalándolo y reinstalándolo; los
cuatro pares coinciden con la derivación (ninguno de los treinta y tres
depende de PyMuPDF, y sólo el de ventana real depende de Tk). El push se
rechazó con 403 durante casi toda la sesión —la app de Claude sin acceso de
escritura al repositorio, como en D9 y PD— y el commit de cierre `d7ffa7a`
lo dejó dicho con su SHA; el acceso se restauró en la misma sesión, `main`
entró por fast-forward y `origin/main` quedó en `d7ffa7a`, sobre el que se
remidió «sí · sí»: 2156 passed, 4 skipped.
**EXT-3 (2026-09-20) sumó TREINTA tests**: los veintiséis de
`tests/test_ext3_regimen_barril.py` —la aceptación del cluster C06 (EXT-M-01,
EXT-M-02, PC-04, PC-27 mitad compuerta, SIS-B-18 mitad JSON): los cuatro
casos del prompt escritos primero en rojo con `xfail(strict=True)` y
liberados al corregir, los tipos nuevos (`RegimenBarril`,
`MetodoNoEvaluableError`, `Bloqueo` en `modelos.py` con `TipoDeBloqueo`), el
dorado CP-12 del régimen lleno, y los tres que dejó el auditor adversarial
(la compuerta llamada en los dos alcances, que una mutación «siempre
diferida» sobrevivía a 277 tests; la celda y/D del resumen siguiendo al
régimen)—, el de B-01 «dimensionado con HW no evaluable/diferido» en
`test_cierre_perfil`, y los tres anclajes parametrizados de
`test_decisiones_diferidas` para las fichas de la Parte XIX (EXT-3-01,
EXT-3-02, EXT-3-03). Las cuatro configuraciones se MIDIERON sobre
`origin/main` en 43b2531 (el contenedor arrancó sin `python3-tk`, se
instaló como manda el bloque de abajo, y las cuatro se midieron: las dos
sin PyMuPDF desinstalándolo y reinstalándolo; las dos sin Tk con el
`xvfb-run` que falla y sin `DISPLAY`). Las cinco citas nuevas entran en los
barridos de `test_normativa_pdf` sin sumar un test, y por eso la columna
«PyMuPDF = no» sigue saltando 33. **EXT-2 (2026-09-20) sumó DIECINUEVE tests**: los diecisiete de
`tests/test_ext2_multicelda_transicion.py` —la aceptación del cluster
hidráulico A del dictamen (EXT-M-03, EXT-M-04, PC-06, PC-19), catorce escritos
primero en rojo con `xfail(strict=True)` y liberados al corregir, dos que
fijan lo que NO cambia (la continuidad en q\* = 3.5 y 4.0, y V6 con N > 1) y
el que dejó el auditor adversarial (la fila «Hidráulica» de la tabla de M11
dice N y Q_celda)— y
los dos anclajes parametrizados de `test_decisiones_diferidas` para las fichas
nuevas de la Parte XVIII (EXT-2-01, EXT-2-02); ningún otro archivo sumó ni
restó tests (el test de la recta de `test_M4_control` se reescribió, no se
duplicó). Se midió «sí · no» sobre el árbol final (2089/8); las otras tres se
derivan sumando 19, porque ninguno de los diecinueve depende de PyMuPDF ni de
Tk: la cita nueva `HDS5_3ED.5.4.3#REPARTO`
entra en los barridos de `test_normativa_pdf` sin sumar un test. **EXT-1
(2026-09-20) había sumado NOVENTA Y DOS tests**: los 89 de
`tests/test_ext1_entradas.py` —la aceptación del cluster «entradas» del
dictamen, escrita primero en rojo con `xfail(strict=True)` y liberada al
corregir, un bloque por ID (EXT-A-03, EXT-V-02..06, PC-01, PC-02, PC-05,
PC-28, PC-32..35), más los dos de regresión que dejó el auditor adversarial
(la clave de fila que no «difiere» de ninguna celda y el par de Manning sin
declarar)—, el del «mismo rasero» para los criterios `Derivada` en
`test_criterios_adoptados`, y los dos anclajes parametrizados de
`test_decisiones_diferidas` para las fichas nuevas de la Parte XVII (PC-32 y
EXT-V-02). Se midió «sí · no» sobre el árbol final (2070/8); «no · no» se
midió antes de los dos tests del auditor (2035/41) y se deriva sumando 2,
porque ninguno de los dos depende de PyMuPDF; las dos con Tk se derivan
sumando 4, como en EXT-0: el contenedor no tenía `python3-tk`. **EXT-0 (2026-09-20)
había sumado CUATRO tests sin tocar un test**:
son los anclajes parametrizados de
`test_decisiones_diferidas.py::test_el_simbolo_que_cada_ficha_ancla_sigue_existiendo`
para las cuatro fichas nuevas de `docs/decisiones_diferidas.md` (SIS-B-22,
NOR-HID-02, EXT-V-01, EXT-G-03), de modo que el parametrizado crece con el
registro. Se midieron las dos configuraciones sin Tk sobre el árbol de EXT-0
(sí · no: 1978/8; no · no: ver la tabla) y las dos con Tk se derivan sumando
4, porque ese test no depende ni de PyMuPDF ni de Tk: el contenedor de EXT-0
no tenía `python3-tk` y no se instaló. **Las cuatro medidas anteriores, sobre
el mismo árbol en PD**
(`aefbdcd`, la rama de trabajo; el push se rechazó con 403 —la app de
Claude volvió a no tener acceso de escritura al repositorio, como en D9— y
las cuatro se midieron sobre ese árbol; el acceso se restauró en la misma
sesión, la rama entró en `main` por fast-forward y `origin/main` quedó en
`0c71854`, que sólo añade los sellos y esta tabla; la configuración
«sí · sí» se remidió sobre él: 1978 passed, 4 skipped, y los sellos de
`indice_formulas.md` y `trazabilidad.csv` llevan ese SHA), que sumó SIETE
tests, todos en
`tests/test_dimensional_piloto.py`: `K_MANNING_SI` en los tres
parametrizados del censo de constantes `_SI`, la afirmación positiva de
Manning con `k_n`, los dos censos en cero, el umbral del paso 4.3 juzgado
sobre una magnitud de su sustitución (`UMBRAL_JUZGA`), y la guardia sobre
el AST de M3 que pidió el auditor adversarial (sin ella, revertir
`_caudal_manning` a `(1/n)` dejaba la suite verde). D9 las había medido
sobre el árbol anterior (`749311c`, el `main` fusionado por fast-forward;
el push se rechazó primero con 403 —la app de Claude no tenía acceso de escritura al
repositorio— y entró horas después, una vez restaurado el acceso, sin
cambios: `origin/main` quedó en `80f2bc9`, que sólo añade los sellos y esta
tabla, y la configuración «sí · sí» se remidió sobre él: 1971 passed, 4
skipped), que sumó UN test neto: la ficha D9-01
en el parametrizado de `test_decisiones_diferidas` (la vía 2 del canal
censada sin usuario al resolver `DIS-HR-FORMAS-HDS5`; el test de la vía 2
se reescribió uno por uno). T3 las había medido sobre el árbol anterior
(`1aed003`), que sumó veintiún tests,
todos en `tests/test_trazabilidad_csv.py`: la sincronía de
`docs/trazabilidad.csv` con el registro, su sello de cuatro partes, las
catorce columnas, el orden determinista y los dos índices inversos
derivados. El sello de `docs/trazabilidad.csv` lleva ese mismo par —firmado
en el commit de cierre, porque el par se mide sobre `origin/main` y no
puede conocerse antes de la fusión—, y `test_trazabilidad_csv` exige que
sea un par. I4 las había medido sobre el árbol anterior
(`c4aca04`), que sumó treinta y nueve
tests: los diecinueve de `tests/test_indice_formulas.py` (la sincronía del
índice de fórmulas generado, su sello y sus huecos), los diecinueve de
`tests/test_dimensional_piloto.py` (el chequeo dimensional de M3–M5 con su
censo de lo que no cierra, y las dos constantes `_SI`) y la ficha `I4-01`
parametrizada en `test_decisiones_diferidas`; el sello de
`docs/indice_formulas.md` sigue llevando el par de I4, que es el del árbol
sobre el que se generó. T1 las había medido sobre el árbol anterior
(`c09c459`), que sumó diecinueve tests:
los dieciséis de `tests/test_vigencia_fuentes.py`, el de la resolución
impresa del Manual de Puentes en `test_normativa_pdf` (por eso la columna
«PyMuPDF = no» salta ahora 33 y no 32), la ficha `T1-01` parametrizada en
`test_decisiones_diferidas` y el criterio nuevo en el parametrizado de
pendientes de `test_criterios_adoptados`. N2 las había medido sobre el árbol
anterior (`dbba580`), que sumó once tests: la
guardia de la traducción no oficial de M 294-11
(`test_toda_cita_de_la_traduccion_de_M294_lo_dice`), los ocho de `CP11` en
`test_M2_material`, el del motivo de descarte del HDPE en `test_MD` y la
ficha `N2-01` parametrizada en `test_decisiones_diferidas`. Post-N1 las
había medido sobre el árbol anterior (su +1 fue el censo de las citas sin
firma deliberada, `CITAS_SIN_FIRMA_A_PROPOSITO`), N1 sobre el previo (su
ficha `N1-01`) y pre-N1 sobre el anterior a ése. Conviene
decir cómo llegó la tabla hasta ahí,
porque es el defecto que este párrafo persigue: I1b la dejó en 1830 y después
**seis sesiones** (G3, I3, R3, R3b, G2, G5) sumaron 51 tests sin volver a
medirla; pre-N1 la encontró en 1881 y fusionó además la rama de S24, que
llevaba desde el 2026-09-09 sin entrar en `main` y cuya ficha `S24-01` trae su
propio caso parametrizado en `test_decisiones_diferidas`: 1882; N1: 1883;
post-N1: 1884; N2: 1895; T1: 1914; I4: 1953; T3: 1974; D9: 1975; PD: 1982;
EXT-0: 1986; EXT-1: 2078; EXT-2: 2097; EXT-3: 2127; EXT-4: 2160; EXT-5:
2367; EXT-6: 2417; EXT-7: 2475; EXT-8: 2515; EXT-9: 2532; EXT-10: 2617;
EXT-11: 3779; E-A: 3824; E-B: 3893; cierre de E-B: 3894; PF-1: 4006; PF-2: 4021;
PF-3: 4034; PF-4: 4064; PF-5: 4098; PF-6: 4115; cierre C10/C05/C09/C11/C14:
4175; rediseño visual de la GUI (cuatro bloques, sin fila en esta tabla):
4178; T-0 de la cadena T: 4235; T-2: 4406; T-4: 4537; T-1: 4728; T-6:
4866; T-8: 4976; T-5: 5177; correcciones de T-8: 5246; T-3: 5352; T-9: 5548;
T-7a: 5709; T-7b: 6002; T-7c: 6276; verificación de fórmulas de T-7: 6310;
T-10: 6360; T-11: 6469; T-12: 6425 en la suite del entregable, que entregó
138 a la de proceso (145). La
«Ventana Tk = no» de las medidas de pre-N1 se consiguió simulando la ausencia
de entorno gráfico (sin `DISPLAY` y con un `xvfb-run` que falla), que es una
de las tres condiciones legítimas del salto; en N1, corriendo la suite ANTES
de instalar `python3-tk` (el contenedor arranca sin él) y otra vez después;
post-N1, N2, T1, I4, T3, D9 y PD repitieron el procedimiento de pre-N1 (N2,
T1, I4, T3, D9 y PD instalaron antes `python3-tk` y las dependencias de
`python3.12`, como manda el bloque de abajo). La «PyMuPDF = no», en todas
esas sesiones, desinstalándolo para la medida y reinstalándolo después:

| PyMuPDF | Ventana Tk | `passed` | `skipped` |
|---|---|---|---|
| sí | sí | 6415 (**derivado** en T-12, no medido: el contenedor no tiene tkinter) | 10 |
| sí | no | 6402 (**MEDIDO** en T-12 sobre el árbol integrado, con `NORMAS_DIR`) | 23 |
| no | sí | 6266 (**derivado**, no medido) | 159 |
| no | no | 6253 (**derivado**, no medido) | 172 |

Las cuatro filas son **con el repositorio de normas enlazado**
(`NORMAS_DIR`). Sin él, hasta T-11 (desde T-12 son 152, en la tabla
que sigue a este párrafo), las dos con PyMuPDF pasan VEINTITRÉS menos y saltan
veintitrés más desde T-11 (dieciocho desde T-1 hasta T-10; medido en «sí · no»
sobre el árbol de T-11: 6423 y 46; sobre el de T-10: 6319 y 41;
sobre el de la verificación de fórmulas de T-7, 6269 y 41;
sobre el de T-7c, 6235 y 41;
sobre el de T-7b, 5961 y 41; sobre el de T-7a, 5672 y 37; sobre el de T-9, 5511 y 37; sobre el de T-3, 5318 y 34; sobre el de las correcciones de T-8, 5212 y 34; sobre el
de T-5, 5143 y 34; sobre el de T-8, 4942 y 34; ni T-6, ni T-8, ni T-5, ni las
correcciones de T-8, ni T-3, ni T-9, ni T-7a, ni T-7b, ni T-7c, ni la verificación de fórmulas de T-7, ni T-10 sumaron ninguno que abra el repositorio de
normas; eran
siete hasta T-2 y doce hasta T-4: T-4 sumó los cinco de
`tests/test_t4_materiales_durabilidad.py` que abren el WSDOT Hydraulics
Manual y T-1 los seis de `tests/test_t1_hidrologia.py` que abren su capítulo
2, y T-11 los cinco de `tests/test_t11_validacion_externa.py` que abren
HEC-14); las dos sin PyMuPDF, uno menos y uno más, porque los otros
veintidós ya iban saltados por la marca `pdf`. Tras T-11 la tabla decía 6459 /
6446 / 6310 / 6297, medida sólo la segunda. Tras T-10 la tabla decía 6350 /
6337 / 6206 / 6193, medida sólo la segunda. Tras la verificación de fórmulas de T-7 la
tabla decía 6300 / 6287 / 6156 / 6143, medida sólo la segunda. Tras T-7c la tabla decía 6266 / 6253 / 6122
/ 6109, medida sólo la segunda. Tras T-7b la tabla decía 5992 / 5979 / 5869
/ 5856, medida sólo la segunda. Tras T-7a la tabla decía 5703 / 5690 / 5592
/ 5579, medida sólo la segunda. Tras T-9 la tabla decía 5542 / 5529 / 5431
/ 5418, medida sólo la segunda. Tras T-3 la tabla decía 5349 / 5336 / 5245
/ 5232, medida sólo la segunda. Tras las correcciones de T-8 la tabla
decía 5243 / 5230 / 5139 / 5126, medida sólo la segunda. Tras T-5 la tabla
decía 5174 / 5161 / 5071 / 5058, medida sólo la segunda. Tras T-8 la tabla decía 4973 / 4960 / 4898
/ 4885, medida sólo la segunda. Tras T-6 la tabla decía 4863 / 4850 / 4788
/ 4775, medida sólo la segunda. Tras T-1 la tabla decía 4725 / 4712 / 4650
/ 4637, medida sólo la segunda. Tras T-4 la tabla decía 4534 / 4521 / 4479
/ 4466, medida sólo la segunda. Tras T-2 la
tabla decía 4403 / 4390 / 4363 / 4350, medida sólo la segunda. Hasta T-0 la tabla decía 4172 / 4159 / 4137 / 4124, medidos
los cuatro en el cierre del 2026-09-22 sobre `19bcf5a`; tras T-0, 4232 /
4219 / 4193 / 4180, medida sólo la segunda.

**Desde T-12 el eje `NORMAS_DIR` abarca todos los PDF, y hay un cuarto árbol
que medir: la EXPORTACIÓN.** Los dieciocho PDF ya no están en `normas/` de
este repositorio, de modo que sin la variable se salta todo lo que abre uno
(antes, sólo lo de HEC-14 y WSDOT); y la suite del entregable tiene que pasar
también sobre `git archive HEAD` —sin `proceso/` ni `.git`, que es lo que
recibe quien descarga el ZIP—, donde se saltan, diciéndolo, los tests que
leen lo versionado. Medido en «PyMuPDF sí · ventana Tk no» sobre el commit de
T-12 que entró en `main`:

| Suite y árbol | `NORMAS_DIR` | `passed` | `skipped` | `collected` |
|---|---|---|---|---|
| entregable, checkout de git | sí | 6402 | 23 | 6425 |
| entregable, checkout de git | no | 6250 | 175 | 6425 |
| entregable, exportación (`git archive HEAD`) | sí | 6398 | 27 | 6425 |
| proceso (`python -m pytest proceso/tests`), checkout | sí | 145 | 0 | 145 |
| proceso, checkout | no | 145 | 0 | 145 |

La exportación salta 4 más que el checkout con `NORMAS_DIR`: los tests que
leen lo versionado o necesitan `.git`: el arnés de mutación de
`test_ext11_mutacion`, la mitad de PC-23 de `test_ext6_registro_normativo`
(`git ls-files`) y, en `test_t12_entregable`, el de `git check-attr` y el de
la exportación emulada, cada uno diciendo por qué.
La suite de proceso no existe en una exportación (`.gitattributes`:
`proceso export-ignore`) y no se cuenta en el par del entregable.

**Cómo se consigue la columna «Ventana Tk = sí», que S21 dio por imposible.**
S21 escribió que el contenedor no tiene `tkinter` en ninguno de sus intérpretes
y dejó dos celdas vacías. Era cierto y no era el final: `apt-get install
python3-tk` se lo da a `python3.12`, y con `xvfb-run` —que ya estaba— los
cuatro tests de ventana corren. La sonda de `test_gui_contrato._interprete_con_ventana`
los encuentra sola, sin tocar nada. Queda escrito porque una celda vacía se lee
como «no se puede» cuando lo cierto era «no estaba instalado»:

    apt-get install -y python3-tk
    python3.12 -m pip install numpy scipy ttkbootstrap weasyprint --break-system-packages

`weasyprint` entró en esa línea en EXT-8: sin él, el noveno test de ventana
real pasa igual —mide la vía del navegador— pero NO ejercita el subproceso
del PDF, que es lo que EXT-8 cerró; con él, lo ejercita de punta a punta
(botón apagado con motivo, progreso, estado terminal, cancelación). Medido
en EXT-8 sobre este contenedor en las dos condiciones.

**Y el número saltó de 1538 a 1794 en dos sesiones, no en una.** La tabla se
quedó en el árbol de S20 mientras la suite crecía: al abrir S21 el conteo ya
era `1651 passed, 35 skipped` (1686). Conviene decirlo porque la deriva de esta
tabla es el defecto que la propia sección persigue.

Decir cuál de los dos números se está citando **y con qué entorno**; la mayor
parte de la confusión histórica de números sale de mezclarlos. La regla que no
depende del entorno es la suma: si `passed + skipped` deja de dar `collected`,
hay un fallo o un error de recolección —no una dependencia ausente—, y eso sí
es una regresión.

Si la fusión no se puede hacer (permisos, política de egress, conflicto), eso
**no** convierte la tarea en terminada: se reporta explícitamente qué quedó sin
fusionar, en qué rama y con qué SHA, para que nadie lo lea como entregado.
