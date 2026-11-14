# Cadena de prompts UI — llevar a la ventana lo que la cadena T dejó sólo en la línea de comandos

**Para:** una sesión orquestadora de Claude Code que ejecute los prompts, en paralelo donde el grafo lo permita y en secuencia donde no.
**Fecha:** 14 de noviembre de 2026.
**Punto de partida:** `origin/main` en `07ef296` (cierre de T-12).
**Serie de commits:** `interfaz(UI-n): <resumen> — <fichas cerradas>`.

---

## 0. Qué entra y qué no (el filtro: «¿el proyectista lo NECESITA ver o tocar en la ventana?»)

La cadena T añadió mucho cálculo, y casi todo **ya se ve en la ventana sin tocarla**: el
detalle de la pestaña 3 pinta `cli._lineas_punto`, que incluye el caudal de cada punto, la
Fase 6 (protección y socavación), la Fase 8 (estructural), la durabilidad y el cabezal del
punto (`_lineas_cabezal_del_punto`); la tabla de verificaciones lista VB1, VB2, CB, A, C…
porque lee `informe_punto.verificaciones()`; y los datos nuevos por punto
(`cabezal_declarado`, `material_lecho_salida`, `ancho_derecho_via_m`,
`Q_evento_extremo_m3s`…) entran por el campo «JSON de datos externos» que ya existe. Eso
**no se toca**.

Lo que sí falta, medido sobre `gui/app.py` en `07ef296`:

| # | Hueco | Por qué es NECESARIO en la ventana | Ficha que lo difirió |
|---|---|---|---|
| 1 | No hay campos para `--cuencas` y `--estacion` | Sin ellos la ventana **no puede calcular el caudal** (la función principal de T-1); y peor: la sesión no los guarda, de modo que el PDF que la ventana escribe en un proceso hijo (`gui/exportacion_pdf.py`, `cli.py --sesion`) recalcularía **sin** la hidrología que la ventana usó | T1-04 |
| 2 | No hay botón para la memoria **resumida** | Es la vista para imprimir del entregable (T-12); hoy sólo sale por `cli.py --sesion … --html-resumida` | T12-04 |
| 3 | El bloque **del cabezal del proyecto** (`cli._lineas_cabezal(informe.cabezal)`: suma de los cabezales, cadena sísmica, K_AE/K_A, recubrimientos, cuantías) no se pinta en ninguna pestaña | Es un resultado de T-7 que el proyectista no puede ver en la ventana salvo exportando | — (no tenía ficha) |
| 4 | No hay botón «Barrido…» | Es la única forma de defender un [A] con su sensibilidad sin salir a la CLI | PF-3-01 |

**Lo que NO entra, a propósito** (corre por detrás o ya tiene su vía en la ventana):

- El estimador del pre-vuelo para la Fase 1-bis (la otra mitad de T1-04): es una
  estimación que no gobierna ningún botón; el anticipo ya dice «depende de la hidrología».
  Sigue diferido en T1-04.
- EXT-3-03 (método no evaluable en el tablero de criterios): el bloqueo ya se ve en la
  tabla «Bloqueos» de la pestaña 3 y en los recuentos.
- EXT-10-01 (declarar [S] en la ventana): lo prohíbe la regla R4; la puerta es el campo
  «JSON de datos de sitio», que ya existe.
- `--progreso`, `--criterios`, `--csv-resumen`, `--comparar`, `--declarar`, `--json`,
  `--datos-sitio`, `--proyecto`, `--alcance`: ya tienen su equivalente en la ventana.
- Ningún cálculo, criterio, constante ni texto de memoria cambia. Si un prompt descubre que
  lo necesita, se detiene y lo difiere con ficha.

---

## 1. Reglas comunes (incluidas por referencia en todos los prompts)

1. **Lee `CLAUDE.md` entero antes de tocar nada**, en especial «GUI», «Arquitectura»
   (EXT-4: el estado viaja en `Informe.contexto`; EXT-8: el PDF en proceso hijo; EXT-9: un
   solo estilo de import, `cli.py` adaptador) y «Tests». Lee también
   `proceso/reglas_de_correccion_de_auditorias.md` y la ficha de
   `docs/decisiones_diferidas.md` que tu prompt cierra.
2. **La ventana sólo pinta.** Ninguna regla de negocio nueva en `gui/`: lo que la ventana
   muestra sale de `src/` o de `cli.py` (el MISMO texto que la CLI, pintado con
   `comp.escribir_lineas_de_cli`). Componentes de `gui/componentes.py` (`CampoValidable`,
   `BotonAccion`, `Panel`, `Tooltip`, `MarcoScroll`); no se reinventan.
3. **No se rompe nada.** Los cuatro exportadores, «Guardar/Cargar sesión», «Importar
   decisiones», «Nuevo proyecto», la invalidación del informe en los gestos que cambian el
   estado (EXT-4) y el proceso hijo del PDF (EXT-8) siguen funcionando igual. Una sesión
   guardada antes de esta cadena (formato 3) **se sigue abriendo** sin perder nada. La línea
   base (`docs/linea_base.md`, `tests/linea_base_familia_c/`) no se mueve; si un número se
   mueve, es un defecto.
4. **Tests primero, en rojo**: `pytest.mark.xfail(strict=True)` con la expectativa, nunca
   con la salida actual como oráculo; al implementar, quitar el `xfail`. Dos capas, como la
   suite ya hace: lógica pura con el doble de tkinter (`tests/apoyo/doble_tkinter`,
   `tests/test_gui_contrato.py`) **y** ventana real.
5. **Entorno con Tk de verdad.** El contenedor por defecto no trae `tkinter`, y sin él los
   tests de ventana real se SALTAN. Antes de la suite:
   `apt-get install -y python3-tk xvfb` (o el equivalente) y `pip install ttkbootstrap`, y
   correr con `xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header`. Enlaza
   también `NORMAS_DIR` (CLAUDE.md, «Dónde están los PDF de normas»). **Una sesión de esta
   cadena no cierra con los tests de ventana saltados**: si no consigue Tk, lo dice en su
   informe como «no verificado» y no lo cuenta como verde.
6. **Documentos generados.** Si un test de sincronía falla porque cambió el JSON o la
   memoria de una corrida de referencia (p. ej. la corrida `caudal_calculado` de T-11),
   regenera con el comando que CLAUDE.md da para ese documento y declara la causa.
7. **Ritual de cierre** (`proceso/bitacora_conteos_y_entorno.md`): suite del entregable y
   de proceso verdes con `passed + skipped = collected` y los saltos explicados; ficha de
   `docs/decisiones_diferidas.md` marcada «Cerrado (UI-n)» o con lo que quede abierto;
   fila del par de la suite en la bitácora; un commit por prompt; integrar y empujar
   (§3). Devolver: fichas cerradas (entera / en parte / no), tests nuevos, archivos
   tocados, lo diferido. **Detenerse ahí; no ejecutar el prompt siguiente.**

---

## 2. Grafo de ejecución

```
UI-1 hidrología en la ventana + sesión formato 4      (primero, secuencial)
 ├── UI-2 pestaña 4: memoria resumida + cabezal del proyecto  ─┐ paralelo
 └── UI-3 pestaña 2: botón «Barrido…»                         ─┘ (worktrees)
UI-4 integración y verificación de la ventana         (último, secuencial)
```

**Por qué UI-1 va primero:** cambia el formato de la sesión y lo que viaja al proceso hijo;
UI-2 (el PDF resumido también sale por el hijo) y UI-3 (el barrido tiene que correr con la
misma hidrología que la ventana) se apoyan en eso.

**Puntos calientes** si UI-2 y UI-3 corren en paralelo: `gui/app.py` (UI-2 toca sólo la
pestaña 4 y sus botones; UI-3 sólo la pestaña 2), `gui/exportacion_pdf.py` (sólo UI-2),
`tests/test_gui_contrato.py` (cada uno añade al FINAL), `docs/decisiones_diferidas.md`
(cada uno su ficha). Orden de integración: UI-2 y después UI-3, con la suite verde en el
destino tras cada una.

---

## 3. Dónde se entrega

La entrega del proyecto es `origin/main` (bitácora, «Cierre de tarea»): cada prompt trabaja
en su rama, la integra en `main`, empuja y mide el par de la suite sobre `origin/main`. Si
la sesión sólo tiene permiso para empujar a una rama designada, integra allí, lo dice en su
informe y deja la fusión a `main` al dueño.

---

## 4. Los prompts

### UI-1 · Hidrología en la pestaña 1 y en la sesión (secuencial, primero)

```text
Ejecuta únicamente UI-1 de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md y aplica sus reglas comunes (§1). Cierra la parte de interfaz de la ficha T1-04 de docs/decisiones_diferidas.md (NO el estimador del pre-vuelo, que sigue diferido). Lee antes: CLAUDE.md, la ficha T1-04, src/servicio.py::cargar_hidrologia y ::correr, src/sesion.py, gui/exportacion_pdf.py, el bloque de la pestaña 1 de gui/app.py y docs/contrato_entradas.md §2-bis.

1. Pestaña 1, panel «Proyecto y CSV»: dos campos de archivo nuevos, «CSV de cuencas (opcional)» y «CSV de la estación (opcional)», con «Examinar…» y botón «i» de ayuda como los de datos externos (la ayuda sale de src/, no se escribe en gui/). Van JUNTOS: si sólo hay uno, la ventana lo dice al validar (el mensaje es el de cargar_hidrologia, no uno nuevo).
2. Al ejecutar, la ventana carga las dos entradas con servicio.cargar_hidrologia y pasa hidrologia= a servicio.correr. Un error de carga se muestra como hoy se muestra uno del JSON de datos externos (ErrorProyecto → aviso del expediente; FileNotFoundError → aviso de archivo), sin tumbar la ventana. Cambiar cualquiera de los dos campos invalida el informe vigente (mismo gesto que cambiar el CSV, EXT-4). «Nuevo proyecto» los vacía.
3. El anticipo de la pestaña 1 recibe ids_con_caudal_calculable desde la hidrología cargada (el mismo conjunto que usa la CLI en _prevuelo) para que un Q_m3s vacío que la corrida va a calcular no se pinte como «DETIENE», y se refresca al cambiar los campos.
4. Sesión formato 4 (src/sesion.py, FORMATO_SESION = 4): dos claves nuevas con las rutas de cuencas y estación, guardadas y resueltas con la MISMA convención de rutas que el CSV. Una sesión de formato 3 se abre igual que hoy (sin hidrología) y se reescribe en 4 al guardar; test de migración con una sesión v3 real: hoy no hay ninguna en tests/fixtures, así que ANTES de cambiar el formato guarda una con el código de partida (con declaraciones, datos de sitio y una corrida embebida) como fixture rotulado. restaurar_sesion repone los dos campos.
5. Proceso hijo del PDF y CLI: sesion_de_la_corrida (gui/exportacion_pdf.py) lleva las dos rutas CON QUE CORRIÓ el informe, y cli.py --sesion las usa cuando la línea de comandos no trae --cuencas/--estacion (las banderas explícitas ganan, como con las demás). Test de equivalencia por las dos puertas: el JSON del hijo con hidrología es el mismo que el de la ventana (patrón de EXT-8/EXT-9).
6. Huellas: ContextoCorrida gana cuencas_sha1 y estacion_sha1, de los MISMOS bytes que se leyeron (como csv_sha1), None sin hidrología. Se imprimen en el encabezado de trazabilidad de la memoria y en el JSON sólo cuando hay hidrología, de modo que la línea base no cambia.
7. Tests: contrato con el doble de tkinter (campos, invalidación, sesión), ventana real bajo xvfb con tests/fixtures/hidrologia/ (el caudal del punto sale «calculado» en el detalle de la pestaña 3), migración v3→v4, equivalencia del hijo, huellas.

No cambies ningún cálculo. Ritual de cierre. Commit: interfaz(UI-1): ... — T1-04 (en parte: interfaz y sesión).
```

### UI-2 · Pestaña 4: memoria resumida y cabezal del proyecto (después de UI-1; paralelo con UI-3)

```text
Ejecuta únicamente UI-2 de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md y aplica sus reglas comunes (§1). Cierra la ficha T12-04 de docs/decisiones_diferidas.md y el hueco 3 del §0 (cabezal del proyecto no visible). Lee antes: CLAUDE.md, la ficha T12-04, M11_reporte.py::memoria_resumida_html / exportar_html_resumida / exportar_pdf_resumida, gui/exportacion_pdf.py, cli.py::_lineas_cabezal y el bloque de la pestaña 4 de gui/app.py (btn_json, btn_html, btn_pdf, btn_csv, btn_comparar, btn_cancelar_pdf).

1. Botones «Memoria resumida (HTML)» y «Memoria resumida (PDF)» en la fila de exportación de la pestaña 4, con el MISMO contrato que los cuatro existentes: motivo compartido sin corrida (MOTIVO_SIN_CORRIDA), apagados al invalidar el informe y en los mismos gestos, leen de Informe.contexto (EXT-4) y nunca del estado vivo. Antes de añadir, enumera por grep todos los sitios que tratan a los botones de exportación como grupo (tuplas de botones, invalidación, habilitación tras correr) y añade los nuevos en TODOS.
2. El HTML resumido se escribe en proceso con M11.exportar_html_resumida. El PDF resumido sale por el proceso hijo de EXT-8, igual que el completo: cli.py --sesion <sesion> --pdf-resumida <destino>, con el botón de cancelar, el aviso de progreso y el manejo de errores del PDF completo; añade a gui/exportacion_pdf.py la variante del comando sin duplicar la lógica. La sesión que viaja al hijo es la de UI-1 (con hidrología si la corrida la tuvo).
3. Panel «Cabezal del proyecto» en la pestaña 4: pinta cli._lineas_cabezal(self.informe.cabezal) con comp.escribir_lineas_de_cli —ni una palabra distinta de la CLI—, vacío con su motivo cuando no hay corrida, y con el texto que la CLI imprima cuando el alcance es perfil o la Fase 9 no corrió. Se refresca y se vacía con el resto de la pestaña.
4. Tests: contrato (grupo de botones, invalidación, motivo), ventana real bajo xvfb (HTML resumido escrito y con el mismo encabezado de trazabilidad que el completo; PDF resumido por el hijo, saltado sólo si falta weasyprint y diciéndolo), panel del cabezal igual al texto de la CLI sobre la corrida de referencia de expediente con cabezal (src/indice_formulas.CORRIDAS_DE_REFERENCIA).

No cambies ningún cálculo ni la plantilla de la memoria. Ritual de cierre. Commit: interfaz(UI-2): ... — T12-04.
```

### UI-3 · Pestaña 2: botón «Barrido…» (después de UI-1; paralelo con UI-2)

```text
Ejecuta únicamente UI-3 de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md y aplica sus reglas comunes (§1). Cierra la ficha PF-3-01 de docs/decisiones_diferidas.md. Lee antes: CLAUDE.md (sección GUI, párrafo de PF-3), la ficha PF-3-01, src/barrido.py entero (barrer, verificar_valores, ResultadoDeBarrido, lineas_de_la_tabla, volcado_del_barrido), src/editores.py (esquema_de, editores tipados de E-B), gui/editores.py, cli.py::_barrer_desde_cli y el bloque de la pestaña 2 de gui/app.py.

1. Botón «Barrido…» en la pestaña 2, activo sólo con un criterio seleccionado que tenga ventana (sensibilidad) y apagado con su motivo en los demás. Abre un Toplevel que pide la lista de valores con el editor tipado de E-B del criterio (un valor por fila, añadir/quitar), más fila y nota cuando el criterio las exige (las mismas reglas que «Aplicar»). Los valores pasan por barrido.verificar_valores ANTES de correr nada; un valor fuera de la ventana se rechaza en el Toplevel y no corre ninguna corrida.
2. Dónde corre: el barrido corre el pipeline una vez por valor y repone el estado con restaurar_sesion(sustituir=True). NO puede tocar el informe de la pestaña 3 ni el estado de la pestaña 2 mientras corre, ni congelar la ventana. Preferencia: proceso hijo con el patrón de EXT-8 (la sesión de la ventana, con la hidrología de UI-1, y el barrido por la CLI con --json a un temporal que la ventana lee). Si eliges otra vía (hilo), demuestra con test que el estado de la ventana al terminar es idéntico al de antes (estado_de_sesion) y que el informe vigente no cambió. Deja la decisión en una ficha nueva UI3-01.
3. El Toplevel pinta la tabla del barrido con las MISMAS líneas que la CLI (lineas_de_la_tabla o el volcado JSON equivalente), incluida la columna de verificaciones incumplidas en la progresión y el «no comparable», con botón «Guardar JSON del barrido». Cancelable. Al cerrar, la pestaña 2 se refresca. El barrido NO arma memoria ni toca los exportadores (es anexo de la tesis).
4. Tests: contrato (habilitación por criterio, rechazo fuera de ventana sin correr, fila/nota exigidas), ventana real bajo xvfb con un barrido de dos valores sobre un [A] de perfil de la guía (docs/guia_perfil.md) cuyas líneas coinciden con las de la CLI para la misma sesión, y estado de la ventana idéntico antes y después.

No cambies src/barrido.py salvo lo imprescindible para llamarlo desde la ventana (y si lo cambias, la CLI sigue imprimiendo lo mismo). Ritual de cierre. Commit: interfaz(UI-3): ... — PF-3-01.
```

### UI-4 · Integración y verificación de la ventana (último)

```text
Ejecuta únicamente UI-4 de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md y aplica sus reglas comunes (§1). Parte de main con UI-1, UI-2 y UI-3 integrados. No añadas funciones.

1. Recorrido de extremo a extremo bajo xvfb, con ventana real, sobre las tres corridas de referencia (src/indice_formulas.CORRIDAS_DE_REFERENCIA) y el ejemplo tests/ejemplo_puntos.csv: cargar CSV, datos externos, cuencas y estación; ejecutar a perfil y a expediente; pestaña 3 (detalle con caudal calculado, protección, Fase 8 y cabezal del punto); pestaña 4 (cabezal del proyecto); los seis exportadores; guardar sesión, «Nuevo proyecto», cargar sesión y volver a ejecutar (mismo JSON); abrir una sesión v3 antigua; un barrido. Déjalo como test (o script en tests/apoyo/ que un test llama) para que no dependa de esta sesión.
2. Capturas PNG de las cuatro pestañas y de la ventana del barrido en docs/capturas_interfaz/ (con xvfb y ImageMagick `import -window root` o equivalente), referenciadas desde el README.
3. README de usuario: la sección de la ventana dice dónde están ahora la hidrología, la memoria resumida, el cabezal del proyecto y el barrido; quita las frases que mandan a la CLI para lo que ya hace la ventana (p. ej. «la resumida sale de la sesión guardada con python cli.py --sesion…»). docs/guia_perfil.md sólo si alguna instrucción dejó de ser cierta.
4. Revisa que las fichas T1-04 (en parte), T12-04, PF-3-01 y UI3-01 dicen lo que quedó, y que ninguna otra ficha de docs/decisiones_diferidas.md sigue afirmando que algo «no está en la ventana» cuando ya lo está.
5. Suite del entregable (también sobre git archive HEAD) y de proceso, con Tk; par en la bitácora.

Ritual de cierre. Commit: interfaz(UI-4): ventana verificada de extremo a extremo — cierre de la cadena UI.
```

---

## 5. Prompt para la sesión orquestadora

```text
Eres la sesión ORQUESTADORA de la cadena UI del repositorio Andy-rba30/Proyecto_alcantarillas. No implementas tú: lanzas una sesión (o subagente en worktree) por prompt, revisas lo que devuelve y decides si avanzar.

0. Prepara: clona el repo; trae la rama donde vive la cadena y llévala a main si aún no está:
   git fetch origin claude/friendly-thompson-ph73b7 main
   git checkout main && git checkout origin/claude/friendly-thompson-ph73b7 -- proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md
   (commit «proceso: cadena de prompts UI» si el archivo no estaba en main). Lee enteros CLAUDE.md y ese archivo. Instala Tk y xvfb (§1 regla 5), enlaza NORMAS_DIR (clon de Andy-rba30/Normas) y mide el par de la suite de partida con xvfb-run; anótalo.

1. Ejecuta el grafo del §2:
   - UI-1 sola. Espera su informe.
   - Si UI-1 cerró con la suite verde y en main: lanza UI-2 y UI-3 EN PARALELO, cada una en su worktree/rama desde el main con UI-1. Integra UI-2 primero y luego UI-3 (rebase de UI-3 sobre main con UI-2; suite verde en el destino tras cada integración).
   - UI-4 al final, sola.
   A cada sesión pásale literalmente el bloque ```text``` de su prompt y nada más.

2. Puerta entre etapas (no avances si falla alguna): suite verde con passed + skipped = collected; los tests de ventana real CORRIERON (no saltados por falta de Tk); la línea base no se movió; ningún archivo de src/modulos/, criterios_adoptados.py, constantes_normativas.py ni datos_sitio.py tocado salvo lo que el prompt permite; ficha de decisiones_diferidas actualizada; un commit con la serie interfaz(UI-n). Si falla, devuelve el trabajo a esa sesión con el defecto concreto; dos intentos fallidos → detente y repórtame.

3. Antes de integrar cada etapa, lanza un revisor independiente (subagente sin el contexto del implementador) con el diff y el prompt, que busque: un exportador o gesto de invalidación que quedó fuera del grupo, una sesión v3 que ya no abre, el hijo del PDF recalculando sin hidrología, texto de la ventana distinto del de la CLI, estado de la ventana cambiado tras un barrido. Lo confirmado se corrige antes de integrar.

4. Entrega en origin/main (§3). Si sólo puedes empujar a una rama designada, integra allí y dímelo.

5. Informe final, en español y breve: qué quedó en la ventana (con las capturas de UI-4), fichas cerradas, lo diferido, el par de la suite de partida y de llegada, y cualquier decisión que necesite del dueño.
```
