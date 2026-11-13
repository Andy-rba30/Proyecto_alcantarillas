# Reglas de corrección de hallazgos de auditoría (material de proceso)

> **Qué es este archivo.** Las secciones «Reglas de corrección de hallazgos de
> auditoría» y «Git (fase de corrección)» de `CLAUDE.md`, MOVIDAS aquí ENTERAS
> por T-12 (2026-11-13, INF-5.2.2) sin reescribirlas: desde la línea siguiente
> a esta nota, el texto es el de `CLAUDE.md` en `f77c5d4`. Rigen el PROCESO de
> corrección de los hallazgos de las auditorías y del INFORME (el tracker, sus
> clusters y conflictos, el registro de decisiones diferidas), no el cálculo.
>
> **Las rutas que citan son las de antes de T-12.** El tracker
> `docs/auditorias/matriz_cruzada_auditorias.xlsx` es hoy
> `proceso/auditorias/matriz_cruzada_auditorias.xlsx`; los tres informes de
> auditoría y los temarios están en `proceso/auditorias/`; las cadenas de
> prompts, incluida la T, en `proceso/planes_mejora/`.
> `docs/decisiones_diferidas.md`, `docs/contrato_entradas.md` y
> `docs/hoja_de_ruta_correcciones_v12.md` siguen en `docs/`.

## Reglas de corrección de hallazgos de auditoría

Este repositorio tiene 234 hallazgos de tres auditorías externas
(`docs/auditorias/auditoria_matematica.md`, `auditoria_sistema.md`,
`auditoria_normativa.md`), ya cruzados en
`docs/auditorias/matriz_cruzada_auditorias.xlsx` (14 clusters por causa raíz, 8
conflictos resueltos; desde T-0, cinco clusters más, C15 a C19, para los
hallazgos `INF-`). Ese archivo es el TRACKER: el estado de cada hallazgo se
marca ahí, en las columnas Estado / Responsable / Commit. El PLAN es
`docs/hoja_de_ruta_correcciones_v12.md`. **Desde EXT-0 (2026-09-20) la hoja
`Hallazgos` tiene 303 filas, no 237**: entraron los 23 hallazgos de la
auditoría externa del 2026-09-19 con prefijo `EXT-` (nunca los prefijos
desnudos `A-`/`M-`/`V-`/`G-`, que colisionan con la de Sistema), los 35 puntos
ciegos `PC-` de su dictamen (`docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md`),
siete ítems `R95-`/`R48-` de los temarios de refutación que no tenían fila de
estado, y `C5-02`. Su plan es la cadena `docs/planes_mejora/07_CADENA_PROMPTS_EXT.md`
(serie de commits `ext(EXT-n)`), y un hallazgo puede volver de «Cerrado» a
«Reabierto (EXT-0)» cuando llega un argumento nuevo: le pasó a NOR-HDS-05,
NOR-HID-02 y SIS-B-22. **Y desde T-0 (2026-11-11) tiene 367 filas**: entraron
los 64 hallazgos del `INFORME_evaluacion_app_alcantarillas_vs_PDF.md`
(repositorio `Cotas-esviaje-alcantarillas`) con prefijo `INF-`, y cinco
clusters nuevos, C15 a C19, para las causas raíz que las tres auditorías no
tenían (hidrología, Fase 8, cabezal por punto, protección y espaciamiento,
criterios vacíos). Su plan es la cadena T,
`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md` (serie de commits
`tesis(T-n)`). **El ID de un `INF-` es el número del INFORME, no el que
escribe el prompt**: la cadena cita seis hallazgos del §5.1 con un número
que no es el de su ítem, y la tabla de equivalencias está al principio de
ese documento y en «Vínculos cruzados» de cada fila (ficha T0-04). Quien
cierre uno escribe el canónico. Las entradas de diseño que la cadena no
rellena —y quién debe cada una— están en `docs/contrato_entradas.md`.

**Dónde vive una decisión DIFERIDA**, que no es lo mismo que su estado:
`docs/decisiones_diferidas.md`. Un objeto que se conserva sin consumidor, un
barrido con un directorio exento, un procedimiento que no se implementa
todavía — cada uno con **qué se difirió, por qué, qué haría falta para
cerrarlo y dónde vive el símbolo**. El tracker dice en qué estado está un
hallazgo; ese registro dice qué se decidió y con qué argumento. No se
transcribe la razón: se cita el símbolo donde ya está escrita, y
`tests/test_decisiones_diferidas.py` comprueba que el símbolo siga existiendo.
Nació de los 22 hallazgos que la auditoría de sistema clasificó «deliberado
sin documentar», que eran decisiones correctas y mudas.

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
