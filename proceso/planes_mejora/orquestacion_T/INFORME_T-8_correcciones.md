# INFORME — T-8, pasada de correcciones de la segunda auditoría adversarial (FASE A)

- Rama `tesis/T-8-correcciones` (worktree `/home/user/wt/T-8c`), desde `df1b23c`. Empujada a `origin`.
- **No está en `main`**: al cerrar la FASE A, `origin/main` seguía en `df1b23c` (sin el commit `tesis(T-5)`), y el encargo
  manda no integrar en ese caso. FASE B pendiente de que el orquestador reanude.
- Las seis **decisiones del dueño** (2026-11-12) llegaron a media pasada **por el orquestador**
  (`orq/DECISIONES_DUENO_2026-11-12.md`); no las recibí del dueño directamente. Las apliqué como valor de archivo y
  sustituyen a las resoluciones provisionales a–h donde discrepan.

## 1. Hallazgo → corregido / refutado, con la evidencia

| ID | Sev. | Estado | Qué se hizo y dónde (símbolo) | Evidencia |
|---|---|---|---|---|
| H1 | ALTA | **Corregido** y superado por la decisión D1 | `M6._regla_de_la_proteccion`: `envolvente_hec14` es el valor de archivo y alcanza a la **piedra** (`d50 = max(Laushey, Ec. 10.4)`), al espesor y a la longitud; los avisos del contraste salen bajo las dos reglas; si HEC-14 no es evaluable rige Laushey con aviso; fuera de la Tabla 10.1, cotas inferiores (2.0·d50 y 8D, lectura declarada) y «pide un disipador». `cli._volcar` separa el numeral del d50 de lo que sale de HEC-14; `ADVERTENCIA_ALCANCE_ENVOLVENTE` | Caso del auditor rehecho a mano en el test (Ø 0.90, Q 1.15: Laushey 0.10756 m, Ec. 10.4 0.16809 m → rige 0.168 m, e 0.60 m). 8 tests `test_h1_*` |
| H2 | ALTA | **Corregido** (lo de ahora); lo de fondo, diferido | `velocidad_admisible_del_cauce(cota_inferior=…)`, `VelocidadAdmisible.concluyente`, `_aviso_el_contraste_no_concluye`: con la velocidad al tirante crítico el contraste **no concluye** (`requerida` None, veredicto INDICADOR, llega a `avisos()`, CLI, JSON y memoria). `_aviso_tirante_de_borde` da la magnitud. La hoya cohesiva (V^0.36) lo avisa también | Figura 3.4 de HEC-14 (PDF 37) releída por imagen: yo/D = 0.323 / 0.467 / 0.572 en descarga libre contra yc/D = 0.420 / 0.604 / 0.743 → V_borde/V_c = 1.43 / 1.38 / 1.35 (el auditor dio 1.37: confirmado). Ejemplo impreso pág. 3-4: +8 % a +13 %. Caso A-02 con S = 0 por el pipeline |
| H3 | MEDIA | **Corregido** | `fundamentos.FROUDE_SALIDA` reescrito (parámetro de HEC-14; no clasifica el régimen; cita `HEC14.1#T1_1_APRON`). Revisados los diez `F6.*`: reescritos también `F6.V_ADMISIBLE`, `F6.APRON`, `F6.APRON_GEOMETRIA`, `F6.GEOMETRIA_ADOPTADA` | Tabla 1.1 (PDF 15): fila «Riprap apron», Froude «na». Apéndice D (PDF 280-281): «Six are summarized and compared» |
| H4 | MEDIA (sospecha) | **Confirmado con la fuente y corregido** (D4) | `requisito_de_filtro`: la nota (5) b sólo en la columna «>50»; `citas.INTERPRETACION_NOTA_5_T511_06`; cita nueva `EG2013.511.05#T511_02_NOTA_5`; aviso en «<15» con la otra lectura | **La Tabla 511-02 de la misma Sección** (pág. impresa 1011, PDF 1019) numera las dos notas por separado: rótulo «(3) (4)» y sólo la celda «0,22 (5)» lleva la de suelos cohesivos. Leído por texto e imagen; test `pdf` propio |
| H5 | MEDIA | **Corregido** (D5) | `HEC14_APRON_ALTURA_MAX_M = 1.524` (60 in), con las dos cifras en el comentario y en la nota de la cita | Nota 8 (PDF 15) y Sec. 10.2 (PDF 217): «1500 mm (60 in)»; ejemplo CU (PDF 220): D = 5.0 ft. Dorado a escala real: 0.43188 ft a mano; el escalado λ = 0.9 se conserva como prueba de fórmula |
| H6 | MEDIA | **Corregido** | Tres `Interpretacion` colgadas de `HEC14.10.2#TW`, `MC_HHD.4.1.1.3.7c#PROTECCION`, `EG2013.511.08#T511_06`; los pasos las imprimen en `nota_del_proyecto` leídas del registro (`M6._lectura`); textos en nombre del proyecto en M6, v8 y `contrato_entradas.md` | 7 tests `test_h6_*` |
| H7 | BAJA | **Corregido** | `M6._exigir_texto_de` (tipo antes que pertenencia) en terreno, régimen, `donde`, embocadura y regla | listas, dicts, enteros y `None` → `DatoInvalidoError` |
| H8 | BAJA | **Corregido** | «manda» → «recomienda» en avisos, `origen_duracion` y docstrings | la cita `HEC14.5.1.2#T30` es RECOMENDACION |
| H9 | BAJA | **Corregido** | Cita nueva `HEC14.10.1#HS` («The riprap floor is constructed at the approximate depth of scour, hs…», pág. 10-1, PDF 202) en el paso 6.14 y en la ficha del criterio | Figura 10.1 vista por imagen: hs acotado desde la prolongación de la solera |
| H10 a-e | BAJA | **Corregido** | (a) el mensaje dice D′; (b) el `LimiteNumericoError` de la hoya nombra D84/D16 o V/Sv/IP; (c) `servicio._UNIDAD_DE_CLAVE`: «minutos»; (d) y (e) comentarios de `constantes_normativas` y `modelos.ProteccionSalida.V` | tests `test_h10*` |
| H11 | BAJA | **Resuelto por D6**, sin columna nueva | «Sin enrocado» ya no existe: las tres celdas del CSV llevan siempre número cuando la Fase 6 corrió | `test_h11_*`; `COLUMNAS_RESUMEN_CSV` no cambia |
| H12 | BAJA | **Refutado en parte, con ficha (T8-11)** | No se ponen techos físicos: ninguna fuente de `normas/` los da y el proyecto los prohíbe (`CLAUDE.md`; comentario de `servicio._DOMINIO_DE_CLAVE`). La cadena `"1.0"` la admite `_numero_externo` para todas las claves desde EXT-1 | HEC-14 págs. 5-1 a 5-7 releídas: no limita Sv, t ni el tamaño del lecho |
| H13 | BAJA | **Corregido** | Tests de las 26 celdas de la Tabla N° 11, las 32 de las Tablas 5.2/5.3 y las 28 de las 5.1/5.4 | releídas del PDF (80, 55, 56, 60) |
| H14 | obs. (M4) | **Avisado en M6; M4 sin tocar; pregunta** | `M6._aviso_banda_de_regimen`. Ficha T8-09 | Medido: S = 0.0058 → 3.160 m/s, d50 0.329 m; S = 0.0056 → 2.412 m/s, 0.191 m (V_erosion 3.114 → 0.319 m) |
| H15 | BAJA | **Corregido** | `ApronHEC14.regimen_determinado` con aviso; un resultado sin TW o sin y_c pierde el apron y conserva el d50 | `test_h15_*` |
| obs. | — | **No refutable sin fuente; declarado** | Comentario en `TERRENOS_COHESIVOS_T11`, ficha T8-10 y `contrato_entradas.md` §6 | la tabla cita el manual de California, que no está en `normas/` |
| bordes | — | **Fijados** | Seis tests `test_borde_*` (IP 5 y 16, Hd 4, TW = D y 0.4D, 2.0·d50, clase «≥», V = V_adm) | verdes antes y después (guardias) |

## 2. Decisiones del dueño aplicadas (relayadas por el orquestador)

1. **D1** — regla = `envolvente_hec14`, con la piedra. Aplicada.
2. **D2** — no concluir con cota inferior; Figs. 3.3–3.4 diferidas (ficha T8-08). Aplicada.
3. **D3** — duración por criterio = 360 min, [C] → [A], ventana 30–360, cita literal `HEC14.5.1.2#DOS_TERCIOS`. Aplicada.
   **Una premisa no la sostiene el literal y lo digo**: «la ventana 30–360 que la fuente sostiene». La fuente sostiene el piso
   (30 min) y la razón para no quedarse en él («2/3 to 3/4 of the maximum scour depth»); **el techo de 360 no sale de HEC-14**,
   que no da duración máxima: es adopción del proyecto, y la ficha del criterio lo declara.
4. **D4** — la lectura que no relaja, como `Interpretacion`. Aplicada, y además sostenida con la Tabla 511-02.
5. **D5** — 1.524 m. Aplicada.
6. **D6** — «sin enrocado» nunca. Aplicada: `d50` lleva siempre número; `requerida` informa. **Contradice a la cadena T**
   (T-8 punto 1: «cálculo del d50 solo entonces»): declarado en la ficha T8-02.

## 3. Números movidos

**Diámetros y materiales movidos: ninguno** (bloque `diseno` idéntico en los tres JSON, medido con `cli.py --comparar` contra
`df1b23c`; A-01 y A-02 siguen en Ø 0.90 m de concreto).

Movidos, aprobados por el dueño, por la regla `envolvente_hec14` (corrida ancha de perfil):

| Punto | d50 que rige | espesor | longitud |
|---|---|---|---|
| A-01 | 0.338 m (**no se mueve**; rige Laushey, la Ec. 10.4 pide 0.252) | 0.592 → **0.770 m** (clase 4: 2.2·0.35) | 5.00 → **5.40 m** (6·0.90) |
| A-02 | 0.274 m (**no se mueve**; la Ec. 10.4 pide 0.104) | 0.479 → **0.770 m** | 5.00 → **5.40 m** |

`manual` reproduce exactamente los números anteriores (`test_manual_sigue_dando_exactamente_los_numeros_de_antes`).
La hoya de socavación no está en la línea base (el fixture no declara lecho); con un lecho declarado, 30 → 360 min: arena,
A-01 1.196 → 1.389 m y A-02 0.846 → 0.982 m (×1.161); cohesivo IP 12 / 24 kPa, 2.087 → 2.676 m y 2.009 → 2.576 m (×1.282).
Línea base regenerada con su README: 15 diferencias y 0 no comparables en `informe_perfil_ancho.json`; en los otros dos JSON,
sólo `criterios_sha1`.

## 4. Tests y pares medidos

- Nuevos: **69** — `tests/test_t8_correcciones.py` (63) y 6 anclajes de `test_decisiones_diferidas` (fichas T8-07 a T8-12).
  `tests/test_t8_proteccion.py` sigue en 96, con una veintena reescritos a la verdad nueva (declarado en su cabecera).
- **Rojo**: escrito primero con `xfail(strict=True)` para H1–H15; las decisiones del dueño obligaron a reescribir H1, H2, H11
  y D3 con el código en marcha. Rojo **medido** con el archivo final sobre un árbol exportado de `df1b23c`: **43 rojos, 20
  verdes** (los verdes son guardias).
- Suite entera sobre `52f5747`, «PyMuPDF sí · Tk no», con `NORMAS_DIR`: **5029 passed / 16 skipped / 5045 collected** (§7).
- Mutación de M6 (arnés de EXT-11, contra los dos archivos): 574 mutantes, 531 muertos (92.5 %) en la medida entera; tras
  cuatro aserciones, remedidas sólo las tres funciones tocadas, **536/574 (93.4 %)** — una medida entera más una parcial.

## 5. Diferido, con símbolo

- T8-08 `M6._aviso_tirante_de_borde`: digitalizar las Figuras 3.3 y 3.4 de HEC-14.
- T8-09 `M6._aviso_banda_de_regimen`: la velocidad de salida de M4 en la banda de régimen.
- T8-10 `citas.INTERPRETACION_NOTA_5_T511_06`: AASHTO M 288 y el manual de California.
- T8-11 `servicio._DOMINIO_DE_CLAVE`: techos de transcripción para los datos de la Fase 6.
- T8-07 `M6._regla_de_la_proteccion`: fuera de la Tabla 10.1 el programa da cotas inferiores, no un disipador.

## 6. Preguntas para el dueño, con su antes / después

1. **Tirante de borde (T8-08).** Hoy, con control de salida y TW < y_c, el d50 de Laushey se calcula con la velocidad crítica
   y se avisa que es cota inferior. Digitalizar las Figs. 3.3–3.4 lo corregiría. Antes/después estimado del caso del auditor
   (A-02 con S = 0): V 1.739 → ≈ 2.13 m/s, d50 de Laushey 0.100 → ≈ 0.149 m; en descarga libre, d50 × 1.8–2.0. ¿Se abre el
   prompt?
2. **Banda de régimen en M4 (T8-09).** ¿La velocidad de salida debe ser `max(V_crítica, V_erosion)` cuando n mínimo daría
   flujo supercrítico? Antes/después medido (A-01 con S = 0.0056): 2.412 → 3.114 m/s, d50 0.191 → 0.319 m. No mueve la línea
   base (A-01 y A-02 van por control de entrada).
3. **Fuera de la Tabla 10.1 (T8-07).** Con la envolvente, cuando la piedra que rige supera 0.55 m imprimo cotas inferiores
   (2.0·d50; 8D) con aviso de disipador. Alternativa: no dar espesor ni longitud y dejar sólo el aviso. ¿Cuál?
4. **Techo de 360 min (D3).** Es adopción del proyecto, no de la fuente. ¿Se mantiene 360 o se fija otro techo con otra
   justificación (p. ej. la duración del hidrograma de diseño de T-1 cuando exista)?
5. **AASHTO M 288 y el manual de California** (T8-10): conseguirlos cierra dos lecturas.

## 7. Par de la suite, y sobre qué commit

Medido sobre **`52f5747`** (cabeza de `tesis/T-8-correcciones`, árbol limpio), configuración «PyMuPDF sí · ventana Tk no»:

| | passed | skipped | collected |
|---|---|---|---|
| con `NORMAS_DIR` | **5029** | **16** | **5045** |
| sin `NORMAS_DIR` | **5011** | **34** | **5045** |

Base `df1b23c`: 4960 / 16 / 4976. La diferencia, +69, son los 63 de `tests/test_t8_correcciones.py` y los 6 anclajes de
`test_decisiones_diferidas`; ninguno pasa a `skipped` con `NORMAS_DIR` (el único marcado `pdf` abre EG-2013, que está en
`normas/` de la app). Las otras tres configuraciones no se midieron (no hay tkinter).

## 8. Lo que NO hice

- **FASE B entera**: no rebasé sobre `main`, no toqué el tracker `.xlsx`, ni la tabla ni el párrafo «T-8» de `CLAUDE.md`
  (que hoy dice cosas que esta pasada cambia: «Laushey sigue rigiendo», «102 / 35», los números 0.592 / 0.479 / 5.00), ni
  `verificar_sesion.py`, ni `LO_QUE_ESCRIBIO_CADA_PROMPT`. Los generados llevan sello provisional de la rama.
- No digitalicé las Figuras 3.3–3.4 ni toqué M4.
- No reforcé las tres aserciones débiles que el auditor señaló en tests anteriores (`> 0`, `p.apron is None or …`).
- No medí las otras tres configuraciones de entorno (no hay tkinter).

## 9. Filas del tracker para la FASE B

| ID | Estado | Nota |
|---|---|---|
| INF-3.3.7 | Cerrado (sin cambio) | Nota: segunda auditoría de T-8 y decisiones del dueño del 2026-11-12 — rige la envolvente Laushey / HEC-14 (piedra, espesor, longitud); «sin enrocado» no es conclusión; contraste con Tabla 11 no concluye con velocidad al crítico; nota (5) b sólo «>50»; límite del apron 60 in; duración 360 min [A]. Commit de correcciones |
| INF-5.1.13 | Cerrado (sin cambio) | Nota: guardias de tipo en `proteccion_entrada`; la lectura «alta = mayor que la Tabla 11» es `Interpretacion`. Commit de correcciones |
| MAT-X6 | (como esté) | Nota: la divergencia Manual / HEC-14 se resuelve por la envolvente (decisión del dueño); `manual` barrible. En A-01, 0.592 → 0.770 m. Commit de correcciones |

## 10. Lista EXACTA de lo que queda para la integración (FASE B, la hace otro agente)

Punto de partida: rama `tesis/T-8-correcciones` en `52f5747` (tres commits `wip`, base `df1b23c`). Se integra detrás de
`tesis(T-5)`, como UN commit `tesis(T-8): correcciones de la segunda auditoria — … — INF-3.3.7, INF-5.1.13 (nota); MAT-X6 (nota)`.

1. **Rebase aplastado** sobre el `origin/main` que tenga T-5. Conflictos probables, todos de texto:
   - `src/criterios_adoptados.py`: T-5 añade criterios; los míos son ediciones EN SITIO de cinco fichas de T-8
     (`espesor_proteccion_salida`, `longitud_proteccion_salida`, `duracion_caudal_pico_socavacion_min`,
     `regla_espesor_longitud_proteccion_salida`, `referencia_profundidad_socavacion`). No añado ni quito claves.
   - `src/normativa/citas.py` (añado al final 3 citas y, al principio del bloque T-8, 3 `Interpretacion`),
     `fundamentos.py` (sólo los `F6.*`), `constantes_normativas.py` (bloque T-8), `modelos.py` (dataclasses de T-8),
     `servicio.py` (`_UNIDAD_DE_CLAVE`, junto a `_numero_externo`), `cli.py`, `M11_reporte.py`.
   - `docs/decisiones_diferidas.md`: mis fichas T8-07…T8-12 van al final de la Parte XLV (antes del `---` de la siguiente
     Parte, si T-5 añadió una); `docs/hoja_de_ruta_alcantarillas_v8.md` (bloque T-8 de la Fase 6);
     `docs/contrato_entradas.md` (filas de T-8 y la tabla nueva «Documentos que el repositorio de normas no tiene», al final
     del §6: si T-5 añadió ahí su lista de AASHTO M 170M, se juntan).
   - `tests/test_guardias_de_la_suite.py`: una entrada en `TEXTUAL_CON_RAZON`.
2. **Censos a recalcular sobre el árbol fusionado** (no los toqué porque no cambian en mi rama): criterios 102 y sin valor 35
   (no añado ninguno; `duracion_caudal_pico_socavacion_min` pasa de etiqueta [C] a [A]: revisar cualquier recuento por
   etiqueta que T-5 haya escrito); `CLAVES_EXTERNAS` 18 (sin cambio); marcas `literal-ok` (sin cambio);
   **citas: 306 → 309** y fichas de `decisiones_diferidas`: +6.
3. **Generados** (regenerar los cuatro con el par FINAL medido sobre el árbol fusionado):
   `python3 -m src.normativa.manifiesto --escribir --suite "<N> passed, <M> skipped (PyMuPDF sí · ventana Tk no · repositorio de normas enlazado)"`
   y `python3 -m src.indice_formulas --escribir --suite "…"`. En mi rama llevan el sello provisional «5029 passed, 16 skipped».
4. **Línea base**: `sh tests/linea_base_familia_c/regenerar.sh` sobre el árbol fusionado y comparar con la de T-5. Lo que
   esta pasada mueve respecto de la de T-5 debe ser SÓLO lo de mi sección del README («Regenerada en la pasada de
   correcciones de T-8»): espesor (0.592/0.479 → 0.770 m) y longitud (5.00 → 5.40 m) de A-01 y A-02, la línea `Fase 6`, la
   tercera advertencia, los avisos, las claves `d50_laushey_m` / `rige_la_envolvente`, las dos huellas. Ningún diámetro.
   Ajustar en esa sección del README el commit de referencia («contra `df1b23c`» → el de T-5) si la regeneración se mide
   contra él.
5. **Tracker** `docs/auditorias/matriz_cruzada_auditorias.xlsx`, hoja `Hallazgos` (openpyxl), Responsable «Claude Code
   (cadena T, T-8)», Commit = el de correcciones; las filas y sus notas están en el §9 de este informe (INF-3.3.7,
   INF-5.1.13, MAT-X6: ninguna cambia de estado, las tres ganan nota). Y `tests/test_t0_gobernanza.py::
   LO_QUE_ESCRIBIO_CADA_PROMPT` si esa tabla fija las notas por prompt.
6. **`CLAUDE.md`**: (a) tabla de entornos: sumar **69** a las cuatro filas (ninguno de los 69 depende de Tk; uno es `pdf`,
   de modo que las dos filas «PyMuPDF = no» suman 68 `passed` y 1 `skipped`), medir «sí · no» sobre `origin/main` y decir las
   otras tres como derivadas; `collected` 4976 + (lo de T-5) + 69; la cuenta de marcados `pdf` sube en 1 y la lista
   «…T-6: 4866; T-8: 4976» gana su entrada. (b) Un párrafo «correcciones de T-8» delante del de T-8, y **corregir en el
   párrafo de T-8 lo que ya no es cierto**: «Laushey … sigue rigiendo y no se movió» (rige la envolvente; se mueven espesor
   y longitud), «`manual` por defecto y `envolvente_hec14` barrible» (es al revés), «`duracion_caudal_pico_socavacion_min`
   [C] (30 min…)» (es [A], 360), «velocidad máxima admisible … dice si la protección es requerida» (informa; la protección
   se mantiene siempre), «un conducto de más de 1.50 m» (60 in = 1.524 m), «notas (5)a y (5)b … por fila» (la (5) b sólo en
   «>50»), y la frase de la línea base «espesor 0.592 y 0.479 m, longitud 5.00 m». En la sección «Excepciones»,
   `MetodoNoEvaluableError`: «un conducto de más de 1.50 m de alto» → 1.524 m (60 in).
7. **Fichas**: ya escritas (T8-07 a T8-12, y enmiendas al pie de T8-01, T8-02, T8-04, T8-05). Sólo renumerar la Parte si
   T-5 ocupó la XLV, y, si se quiere, anotar en T8-12 el par final.
8. **Cierre**: suite entera verde con y sin `NORMAS_DIR` sobre el árbol fusionado, `git push origin HEAD:main`, confirmar
   `origin/main == HEAD`, remedir el par, dejar `tesis/T-8-correcciones` en ese commit.

**Riesgo a vigilar en el rebase**: si T-5 (u otro prompt) lee `ProteccionSalida.d50` creyendo que es Laushey, ahora es «el que
rige» (el de Laushey está en `d50_laushey`); y `HoyaDeSocavacion.profundidad_al_techo_de_la_ventana` / `duracion_techo_min`
se llaman ahora `profundidad_alternativa` / `duracion_alternativa_min` (clave JSON `profundidad_alternativa_m`). T-7a, que
consumirá `socavacion_salida`, recibe la hoya de 360 min cuando no hay hidrograma.
