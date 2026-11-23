# Estado de VE-3 (para retomar si la sesión se corta)

Material de proceso, no del entregable. Lo mantiene la sesión orquestadora y se actualiza
cada vez que se integra algo. Fecha de esta versión: 2026-11-23.

> **ESTADO (2026-11-23, tarde, sesión `claude/nifty-brahmagupta-rfj9o6`, PR #47): integración
> del plan de mantenibilidad.** Contiene a `claude/serene-keller-2p7pcs` y a sus ramas de agentes
> (`-d2` fusionada en `d027a7e`; `-d3-m11` y `-d3-modelos` ya lo estaban); `-d3-constantes` nunca
> se subió y la ficha D3-03 la difiere (dictamen Fable). Pasos 1 a 5 de la sección 8 del plan:
> hechos. Paso 6 (cierra H1): suite completa en esta nube con `NORMAS_DIR`, Tk (`xvfb-run`) y
> Python 3.12, en worktree limpio; sello con el par medido y una segunda corrida que lo confirma.
> Paso 7: fast-forward de `main`, sólo con la autorización del dueño. **Si la sesión se corta:**
> retomar desde `claude/nifty-brahmagupta-rfj9o6`.

> **ESTADO ANTERIOR (2026-11-23, sesión `claude/serene-keller-2p7pcs`): plan de mantenibilidad y uso.**
> El cierre de VE-7 de abajo está TERMINADO (lo confirma la auditoría
> `AUDITORIA_CIERRE_VE7_2026-11-21.md`): CI `44859160957` verde, `main` en `362beb4`, etiqueta
> `respaldo-2026-11-20` y las ramas superadas bajo `respaldo/*`. Lo que sigue al cierre es el
> plan `proceso/planes_mejora/11_PLAN_MANTENIBILIDAD_Y_USO.md`, que una sesión desde la máquina
> del dueño llevó en `v2/mantenibilidad-y-uso` hasta D2 a medias (`0b8c4a7`, WIP) y expiró.
> Esta sesión retoma desde esa punta en `claude/serene-keller-2p7pcs` (contiene a `v2` y a
> `main`). La tabla «8. Estado» del plan dice qué está hecho, con su commit; los hallazgos H1–H5
> de la auditoría se cierran aquí (H2 por decisión del dueño: mínimo de siete corridas, mismo
> límite). **Si la sesión se corta:** retomar desde `claude/serene-keller-2p7pcs` y las ramas
> `claude/serene-keller-2p7pcs-*` de los agentes que no estén fusionadas en ella.
> **Avance y lo que falta, paso a paso:** sección «8. Estado» del plan (se actualiza en cada
> hito). La suite completa la corre el dueño en su máquina en el paso 6, sobre el commit final.

> **CIERRE DE VE-7 — TERMINADO (ver el bloque de arriba); lo que sigue es su registro (2026-11-20, ~20:00 UTC, sesión `claude/optimistic-carson-ag7mwp`, rama ya borrada y conservada en `respaldo/claude/optimistic-carson-ag7mwp`).**
> Rama de trabajo: `claude/optimistic-carson-ag7mwp` = `claude/ve7-fix-suite` (todo VE-7: alero,
> lotes A/B/C, peralte y arreglos de suite; 80 commits sobre `claude/laughing-euler-ybme10`, 0
> por detrás) + A11. Revisadas todas las ramas: lo no contenido está declarado superado.
> - **Hecho:** A11 — `NORMAS_DIR` enlazado (clon de `Andy-rba30/Normas` en
>   `/home/user/andy-rba30/normas`), `E060.22.10.2.2#VOLADIZO` firmada contra la pág. 195 y cita
>   principal de C7; dictamen Fable APROBADO CON CAMBIOS, aplicados. Los 158 tests `-m pdf`
>   pasan con el PDF. Línea base, validación hidrológica/externa/conducto/cabezal y bloques de
>   la guía regenerados: sin cambios.
> - **Avance (~22:30 UTC → 2026-11-21 ~02:50 UTC):** `validacion_integral` y
>   `validacion_sensibilidad` regeneradas y subidas. El run de GitHub Actions `44824122722`
>   (sobre `e65b1c8`, idéntico en código/docs/tests a `8472063`, `ubuntu-24.04`, Python 3.12 +
>   Tk + WeasyPrint, sin `NORMAS_DIR`) cerró en `2 h 28 min 12 s` con **`6 failed, 9001 passed,
>   174 skipped`** (9 181 recolectados): los 4 desajustes reales de T-11 (`test_t11_sensibilidad`
>   x3 + `test_t11_validacion_integral` x1) más los 2 sellos `PROVISIONAL`. Se diagnosticaron,
>   corrigieron y declararon en
>   `proceso/planes_mejora/ve3_estado/INFORME_CIERRE_FALLOS_SUITE_2026-11-20.md` (dictamen
>   adversarial `auditor-argon`: **APROBADO**). Verificados en verde:
>   `test_t11_sensibilidad.py` (**9 passed**), `test_t11_validacion_integral.py` (**31 passed**),
>   `-m pdf` con `NORMAS_DIR` (**158 passed**), guardias/decisiones/literales/VE-2
>   (**561 passed**) y `proceso/tests` (**145 passed**).
> - **En curso / Falta:** sellos definitivos de `docs/indice_formulas.md` y
>   `docs/trazabilidad.csv` (`5eccfe2 · 9167 passed, 14 skipped (PyMuPDF sí · ventana Tk sí ·
>   repositorio de normas enlazado)`) y fila final en `proceso/bitacora_conteos_y_entorno.md`
>   **aplicados**. Queda únicamente esperar confirmación en verde del run de GitHub Actions
>   (`Pruebas`) sobre este commit sellado y, tras su confirmación, hacer fast-forward de
>   `claude/laughing-euler-ybme10` y `main`, crear la etiqueta `respaldo-2026-11-20` y limpiar
>   ramas superadas.
> - **Si la sesión se corta:** retomar desde `claude/optimistic-carson-ag7mwp`.

> **VE-7 EN CURSO (2026-11-20, noche).** Decisión del dueño: cerrar TODO lo de código, con las
> decisiones a cargo de Fable. Triaje de Fable de todo lo abierto (censo + «Abierto» de las fichas
> VE4–VE6 + sus recomendaciones): 25 ítems a implementar en tres lotes y el resto cerrado como
> bloqueo declarado o «no procede» con cita. Ramas, desde `cb15e32`, cada una con push de respaldo
> cada ~20 min: `claude/ve7-alero-estabilidad` (T7C-04), `claude/ve7-lote-a` (cabezal y embocadura,
> A1–A10), `claude/ve7-lote-b` (conducto, pórtico, metrados, hidrología, B1–B13),
> `claude/ve7-lote-c` (registro, memoria, CLI, C1–C6). Después: A11 (cita de C7 a
> `E060.22.10.2.2#VOLADIZO`), integración en esta rama, revisión Fable de las decisiones nuevas,
> regeneración de documentos, suite en worktree limpio, sello y fast-forward de `main`.
> **Si la sesión se corta:** retomar desde esas ramas (su último commit) e integrarlas en este orden:
> alero → A → B → C → A11.
> **Avance (2026-11-20, noche):** las cuatro ramas recibieron revisión de Fable; alero y lote A tienen
> el dictamen aplicado y están integrados en `claude/ve7-integracion` (desde `b6be2af`, 1566 tests de
> sus áreas en verde). Lote B (dictamen en curso: B10 C por tabla, envolvente seco/sumergido, ▲ NF
> estacional, ▲ ancho de 5.10.6, ▲ metrado del acero, ▲ cuneta 0.30) y lote C (dictamen en curso:
> comparador cerrado, línea CLI de 0-bis, 4.1 del índice, quinta corrida, test_c7, caducidad de la
> cita sin firma) faltan por terminar e integrar. Pendiente en esta rama: 11 fallos de
> `test_t11_validacion_integral`/`test_t11_sensibilidad` por diagnosticar antes de sellar `main`.
> **Diagnóstico (7 de validación integral):** no son de cálculo; el juego completo de
> `tests/apoyo/validacion_integral.py` es anterior a VE-5 y no declara lo nuevo. Corregir declarando
> en el JUEGO (datos de prueba rotulados): `licuefaccion_ems` (global, `no_licua` con Mw/Tr ≥ los
> adoptados, documento/fecha/metodo), `incremento_acero_por_despiece` y `clase_concreto_losa_entrega`
> (sin valor de archivo por dictamen Fable: el juego los declara); y actualizar los censos del test:
> fichas de método {VC1-01, VE5-MET-01}, §7 del contrato (+`arrastre_de_solidos`, que el juego ya
> lee), sin consumidor = 2 (ediciones), perfil sin valor (+`carga_viva_tubo_concreto_somero`,
> `factores_idf_regional`), y el escalón «no cabe» que ahora trae además el bloqueo de Fase 0-bis
> (VE6-02: va al lado de las demás faltas; el test debe buscar el bloqueo de diseño, no el primero).
> Luego regenerar `docs/validacion_integral.md` y repasar los 4 de `test_t11_sensibilidad`.

> **ESTADO (2026-11-20, tarde, sesión `claude/laughing-euler-ybme10`): VE-5 y VE-6 integrados.**
> `main` había sido vaciado (commit `03ab811`, «Repositorio vaciado a pedido del propietario»)
> y `claude/keen-cray-rhxzmg` traía la fusión de los lotes de VE-5 con marcadores de conflicto
> y ~300 líneas perdidas (servicio, M6, tolerancias). Esta sesión:
>
> - **Rehízo la integración de VE-5** desde `6fd1c54` (m8, m9, mh, catlic, gui, fixve4, uno a
>   uno) y la enlazó con `03ab811` por una fusión `-s ours`, para que `main` avance por
>   fast-forward sin reescribir historia. Revisó las 36 ramas: todo commit con nombre está en
>   la integración; los respaldos WIP están superados; `tesis/orquestacion-estado` quedó
>   archivada en `proceso/planes_mejora/orquestacion_T/` (scripts como `.py.txt`).
> - **VE-6** (agentes en paralelo, cada uno en su rama, con respaldo continuo):
>   `claude/ve6-m9-cabezal` (+`-2`): ítems 9 (alero por secciones), 10 (ciclópeo C7/C8), 28
>   (orientación y distancia al borde por punto) y 29 (cuantía [N→]); `claude/ve6-integrador`:
>   ítems 22 (refinamiento con la longitud entre cabezales), 34 (G1 en el bucle, V10, delta con
>   V4) y T7A-03 (cabezal paralelo, Carta 11); `claude/ve6-prevuelo` (+`-2`): NF de M12 a
>   expediente detrás de M9 y la Fase 0-bis al margen del dimensionado. **Todas las decisiones
>   las revisó Fable** (dictamen del consultor por delegación del dueño): aprobadas con
>   cambios, y los cambios están aplicados (fichas VE6-*, VE6M9-*, Partes LXII y LXIII).
>   Fable también decidió que `incremento_acero_por_despiece` y `clase_concreto_losa_entrega`
>   quedan [A] sin valor (VE5-MET-01).
> - **Hoja de ruta:** se añadió el «Addendum VE-6» a la nota T11-03 de §7.B (decisión del
>   consultor por delegación del dueño); el texto anterior no se tocó.
> - **Entorno:** el «Default» no deja PyPI: se usa el entorno personal `proyecto_alcantarillas`;
>   Tk para Python 3.12 por apt (`python3-tk`, `python3-pil.imagetk`) y la suite con
>   `xvfb-run -a /usr/bin/python3.12 -m pytest -n 4`. Los worktrees de agentes viven en
>   `.claude/worktrees/` (excluidos en `.git/info/exclude`) y ensucian dos guardias que barren el
>   árbol: medir la suite en un clon o worktree limpio.
> - **Queda:** sellar índice y manifiesto con el par de la suite, fila en la bitácora y
>   fast-forward de `main` (el dueño confirmó que el código final va en `main`).
> - **Abierto, no se cierra con código:** el EMS, el estudio hidrológico, la topografía, el
>   fabricante y los documentos de normas que lista el censo (§9); la zapata y la estabilidad
>   del alero (T7C-04); la cita propia de E.060 22.10.2.2 (falta el PDF: `NORMAS_DIR`).

> **ESTADO (2026-11-20, ~08:30 UTC, sesión `claude/keen-cray-rhxzmg`).** La sesión
> `claude/cool-euler-tpoj7o` se cortó (~06:36 UTC; las sesiones hijas de VE-5 no dejaron ramas
> salvo `claude/ve5-gui`). Esta sesión retoma en `claude/keen-cray-rhxzmg`:
>
> - **Integrado aquí:** `cool-euler` entero; VE-4a, VE-4b, VE-4c, VE-4d y VE-4e (merges con los
>   censos reconciliados en `70226de`: criterios 158, `CLAVES_EXTERNAS` 28, el mapa de métodos de
>   V5/V8 en tuplas); VE5-GUI `67a58c0` (ítems 37 y 42). 643 tests de las áreas tocadas en verde.
> - **En curso (worktrees en `/home/user/wt/<lote>`, ramas locales `claude/ve5-<lote>`; si la
>   sesión se corta, esos commits se pierden con el contenedor — retomar desde el censo):**
>   m8 (VE-4f desde `3f1433e` → ítem 1 pórtico → 23 → 26), m6 (VE-4g desde `d6849e9` → ítem 2 y
>   caída del Cap. 11), m9 (muro que no cede → 4 → 3 → 9 → 10 → 28 → 29 → 34 → T7A-03), mh (12, 14,
>   13, 11), m45 (17, 18, 19, 24), catlic (20, 21, 6, clase de sitio), gui (38, 40, 39, 46, 43, 44,
>   49, 45, 47, 48), met (8). Revisión Fable independiente de VE-4a…e en curso.
> - **Después:** integrar los lotes, regenerar documentos y línea base, suite completa en clon
>   limpio y exportación, sellos, bitácora y `main` (autorizado por el dueño cuando la suite pase).
> - Entorno: el «Default» no deja PyPI; se creó el entorno personal «Proyecto_alcantarillas» con
>   registros de paquetes.

> **ESTADO (2026-11-20, sesión `claude/jolly-clarke-qojnbj` trabajando sobre la rama
> `claude/cool-euler-tpoj7o`).** Retoma desde `ba63b8a` (VE-3.15 y VE-3.16 hechos, sellos
> PROVISIONAL). Decisiones del dueño en el chat de esta sesión (2026-11-20): **seguir las
> recomendaciones** sobre las decisiones abiertas y «terminar todo».
>
> - **Hecho:** la hoja de ruta corregida por el dueño (`24e7c0b`): la §9.2 (ficha VE3-20,
>   «No se asume de archivo: se declara por obra») y la Fase 9 «El agua una sola vez»
>   (ficha VE3-21, `drenado` de archivo), cada una con su nota «Corregido» verificada contra
>   AASHTO LRFD 9.ª; revisión independiente con Fable (`verificaciones_del_dueno/
>   revision_fable_hoja_de_ruta_ve3_20_21.md`, «integrar con correcciones», H1 a H5
>   aplicadas). Los valores de archivo NO cambian. Línea base regenerada (sólo huellas y el
>   texto de la ficha de `factor_muro_eleccion`); manifiesto, trazabilidad e índice
>   regenerados con sello PROVISIONAL (`5d8ed52`).
> - **En curso:** la suite completa sobre `5d8ed52` en clon limpio y en exportación
>   (`git archive HEAD`), con Python 3.12 + Tk, xvfb y `NORMAS_DIR` enlazado. La medición
>   previa sobre `ba63b8a` llegó al 55 % sin un fallo antes de detenerla.
> - **Falta:** sellar con el par medido, fila en la bitácora, y la **autorización expresa del
>   dueño para integrar en `main`** (la rama va 42 commits por delante y 0 por detrás).
> - **Autorizado por el dueño (2026-11-20, chat):** integrar en `main` cuando la suite pase.
> - **VE-4 lanzado (2026-11-20, decisión del dueño: hacer las cinco mejoras diferidas, en
>   paralelo, con Fable para revisar).** Un agente por mejora, cada uno en su worktree y su
>   rama, con respaldo cada 20-30 min; base `ec0306a`. Sin regenerar documentos (lo hace el
>   integrador) y sin editar la hoja de ruta (proponen el texto):
>   `claude/ve4a-e4e5-declarado` (E4/E5 del cabezal como resultado declarado del EMS, T7B-07),
>   `claude/ve4b-prevuelo-hidrologia` (estimador del pre-vuelo de la Fase 1-bis, T1-04),
>   `claude/ve4c-v5-remanso` (V5 `perfil_de_remanso_paso_a_paso`, T7B-01),
>   `claude/ve4d-v8-desborde` (V8 `desborde_admitido_con_terraplen_protegido`, T7B-02),
>   `claude/ve4e-agua-por-condicion` (WA estática y sísmica con `sin_drenaje`, VE3-21).
>   Y (dueño, 2026-11-20) `claude/ve4f-relleno-bajo`: la carga viva con relleno bajo, fuera del
>   dominio de AASHTO 3.6.1.2.6a (límite 3 de «Apuntado para después de VE-4»); se integra
>   después de VE-4a a VE-4e. VE-4a terminado (`cf302c0`), en revisión Fable. Decisión del
>   dueño pendiente de VE4A-01, con la recomendación: `fila_phi_estabilidad_global` vacía hasta
>   el EMS; con el EMS, 0.65 (FS ≥ 1.54, coherente con el 1.50 de E.050) salvo sondeos en cada
>   cabezal.
>   Después: revisión independiente con Fable de cada una, integración en una rama, suite,
>   sellos y `main`. Si la sesión se corta: cada rama tiene su avance; retomar desde ellas.
> - **Sigue abierto, para cada obra (no es del programa):** con los valores de archivo el
>   sismo del cabezal no cierra; se cierra declarando por obra `reduccion_por_desplazamiento`
>   + `cedente`, con el detalle de juntas, la aceptación escrita del Propietario y el EMS real
>   (φ de fundación, clase de sitio, licuefacción; la Zona 4 de AASHTO es una estimación).

> **ESTADO (2026-11-18, ~12:30 UTC, sesión `claude/cool-euler-tpoj7o`).** La sesión del dueño
> en `claude/festive-bell-wrmps1` **se cortó** después de `b3a8831` (04:49 UTC; el último
> respaldo de sus agentes es de las 04:54 y no trae nada que no esté en la rama). Esta sesión
> retoma desde ese commit en `claude/cool-euler-tpoj7o`. Lo que la sesión cortada dejó hecho y
> sin cerrar:
>
> - Hecho: VE-3.15 (decisiones 9 a 14) con las correcciones H1 a H8 de su revisión Fable;
>   T11-10, T11-03 (abiertos 3 y 4), T8-08 y T8-09; los textos de la hoja de ruta que el dueño
>   corrigió (VE1-01 D3, VE2-01, VE3-18); la validación hidrológica con seis casos reales
>   (`docs/validacion_hidrologica.md`, VE3-19); los informes Fable del dentellón y del sismo.
> - Sin cerrar: los documentos generados (sólo se regeneraron `validacion_integral.md`,
>   `validacion_hidrologica.md` y la línea base), la suite en clon limpio y exportación, los
>   sellos, la bitácora y este LEEME.
>
> **El análisis de por qué el cabezal no cierra el sismo TERMINÓ**
> (`verificaciones_del_dueno/sismo_cabezal_que_se_pasa.md`): no hay error aritmético; lo que
> lo hace fallar es el relleno lleno de agua bajo sismo (`drenaje_trasdos` = `sin_drenaje`,
> contra el nivel medio de C11.6.5.3) sobre k_h = k_h0 completo. Medido por esta sesión con
> la app: con los valores de archivo los cuatro puntos del juego fallan E1 y E3 sísmicos en
> sus dos cabezales; con `drenado`, `reduccion_por_desplazamiento` y `cedente` (lo que el
> juego declara) los cuatro cumplen.
>
> **Decisión del dueño (2026-11-18, en el chat de esta sesión): seguir las recomendaciones.**
> Orden de trabajo de esta sesión:
> 1. Cerrar VE-3.15 tal como está: regenerar los documentos, suite en clon limpio y en
>    exportación, sellos, bitácora.
> 2. VE-3.16: `drenaje_trasdos` = `drenado` como valor de archivo (11.6.6: «shall be
>    drained»), con el juego de validación, el contrato de entradas y la línea base
>    reajustados (borrador del cambio del criterio en el stash de la sesión; se rehace si se
>    pierde). Con el relleno drenado, el agua del sismo es la del freático del punto, que es
>    lo que pide C11.6.5.3: la corrección del nivel medio queda cubierta para el valor de
>    archivo; con `sin_drenaje` declarado el sismo sigue con el relleno lleno (es lo que se
>    declara) y se ficha.
> 3. La reducción de k_h (0.5·k_h0, muro que cede) NO pasa a valor de archivo: aceptar el
>    desplazamiento es del Propietario y la §9.2 de la hoja de ruta lo desaconseja para el
>    cabezal empotrado. Se declara por obra, como ya hace el juego. El defecto de la §9.2
>    («sin reducción» presentado como el lado seguro sin decir que es desplazamiento nulo y
>    que con PGA 0.50 g no cierra) se REPORTA en una ficha; la hoja de ruta no se edita.
> 4. Integrar en `main` sólo con autorización expresa del dueño.
>
> **Avance de esta sesión (2026-11-18, ~14:30 UTC).** Suite del estado que dejó la sesión
> cortada (`b3a8831`, clon limpio, `-n 4`): **33 fallos de 8198**. Resueltos en esta rama:
> línea base y documentos de validación regenerados; guardias de estilo (floats con `==`,
> tolerancias sin nombre, `sys.path` de la evidencia hidrológica congelada) sin subir cupos;
> `test_t7_verificacion` fuera del cambio de VE-3.15 (valores previos y muro que cede
> declarado; ningún dorado cambia); expectativas movidas por la decisión 9 (zapata de 3 m),
> T11-10 (sesión v3) y VE-3.15 (diez barridos de sensibilidad sin efecto, cabezal de la
> regla); techo de memoria por punto 109.6 KB. Ficha VE3-20 escrita. Pendiente: anexo de
> sensibilidad regenerándose, medir `import cli` con la máquina libre, regenerar
> manifiesto/trazabilidad/índice con el par, suite completa en clon limpio y exportación,
> sellos, bitácora; VE-3.16 (drenado) en preparación en paralelo.

> **CAMBIO DE SESIÓN (2026-11-18, decisión del dueño).** VE-3 hasta VE-3.14 está en `main`
> (`5e0fa00`, fast-forward de 81 commits, empujado por la sesión del dueño). **La sesión
> orquestadora de `claude/youthful-shannon-rjzmuc` NO empuja más** ni a esa rama ni a `main`.
> Desde aquí sigue la sesión del dueño en `claude/festive-bell-wrmps1`: VE-3.15 (decisiones
> 9 a 14 del cabezal, aceptadas como abajo) y su paso a `main`.
>
> **Decisiones 9 a 14, respuesta del dueño (2026-11-18): se aceptan los dictámenes de
> `verificaciones_del_dueno/cabezal_decisiones_9_14.md`.** 9 método exacto del talón con la
> envolvente (Resistencia I con γ máx. y mín., Evento Extremo I; presión lineal de 10.6.5 con
> despegue). 10 cuña sobre la cara de la pantalla hasta la superficie real, con la inercia de
> la pantalla en sismo. 11 `muros_tabla_11_5_7` por AASHTO 11.5.7, sin la cita del Manual de
> Puentes 2.11.8.5 y declarando la tensión con su 2.8.1.1.12.6. 12 un solo régimen, «no cede»
> en el archivo; «cede» sólo declarado con justificación, con guardia. 13 el mayor entre el
> centroide estático y H/3 sólo con el muro que cede; h/2 con el que no cede. 14 margen 0
> bajo la hoya sin proteger; no la «hoya protegida».

> **MENSAJE DEL DUEÑO A LA SESIÓN ORQUESTADORA DE VE-3 (2026-11-17, 20:30 UTC), dejado
> desde otra sesión porque el dueño ya NO tiene acceso a esta.** Nadie va a leer el chat de
> esta sesión ni a responder preguntas en él: todo lo que importe tiene que quedar en el
> repositorio.
>
> 1. **Copia ya al repo lo que tengas fuera de él**, empezando por
>    `/home/user/verificacion_fable/ENSAYOS_DISENO_CONDUCTO.md` (aunque esté a medias,
>    rotulado BORRADOR) a `proceso/planes_mejora/ve3_estado/`, con commit y push a esta
>    rama. Desde ahora, todo informe en curso se copia y empuja con los respaldos de cada
>    15 minutos, igual que el código.
> 2. **Las preguntas al dueño no se hacen en el chat**: escríbelas en este LEEME
>    («Decisiones pendientes del dueño»), con tu recomendación, y sigue con lo que no
>    dependa de ellas.
> 3. **Deja un `PROMPT_CONTINUAR.md` en esta carpeta, y mantenlo al día**, para que otra
>    sesión retome VE-3 desde las ramas si esta se corta (como se hizo con VE-2).
> 4. No integres en `main`: eso sigue esperando la autorización del dueño.

## Decisiones pendientes del dueño (con la recomendación de la sesión)

La sesión sigue con lo que no depende de ellas. Responder aquí (o en el chat) basta.

> **RESPUESTA DEL DUEÑO (2026-11-17, ~20:45 UTC), escrita desde otra sesión: se ACEPTAN las
> cinco recomendaciones tal como están abajo.**
>
> 1. Clases III a V: **sí**, transcribirlas como [C] desde la tabla de ASTM C76 del USACE EM
>    1110-2-2902, con su cita verificada (numeral, página impresa, texto literal). Hazlo ya.
> 2. `borde_libre_bajo_tw_ahogante`: **se mantiene `no_cumple`**.
> 3. O-2 del cabezal: **se deja el ancho real** del acero de temperatura y se cierra O-2.
> 4. Carga viva de M8 con poco relleno: **revisión de ingeniero antes de la sustentación**;
>    ningún cambio de código.
> 5. Integrar en `main` cuando la suite esté verde y los ensayos del cabezal estén hechos;
>    **antes de integrar, avísalo en este LEEME** (el dueño autoriza el paso a `main` aquí).
>
> **Verificaciones independientes en curso desde la otra sesión (modelo Fable)** sobre lo de
> mayor importancia: (a) los valores D0.01 de las Clases I a V contra el PDF del USACE y, si
> se puede leer, contra AASHTO M 170M / ASTM C76 —la decisión 1 depende de ellos—, y (b) la
> lectura de la carga viva de M8 con poco relleno contra AASHTO LRFD 9.ª 3.6.1.2.6 —es la
> revisión de la decisión 4, como primer filtro antes del ingeniero—. Sus informes llegarán
> como archivos nuevos en `proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/`. No
> esperes por ellos: si (a) encuentra una discrepancia en una cifra que ya transcribiste,
> corrígela con su cita; si (b) encuentra un defecto real, trátalo como hallazgo de VE-3.
> Revisa esa carpeta cada vez que actualices este LEEME.
>
> **SEGUNDA RESPUESTA DEL DUEÑO (2026-11-17, ~20:55 UTC), tras las dos verificaciones Fable
> (ya en `verificaciones_del_dueno/`):**
>
> 6. **Carga viva de M8 con poco relleno: se MANTIENE la lectura literal de AASHTO LRFD 9.ª
>    (sin L_e).** No se adopta el L_e de ACPA como criterio. Se añade SÓLO un aviso en el
>    paso F8.CLASE (tubos de concreto con relleno < 1.0 m) con el contraste de la práctica
>    ACPA (la clase que saldría con L_e), rotulado como contraste que NO gobierna. Corrige
>    además la redacción de la ficha VE3-04 y de `docs/validacion_conducto.md` (≈ línea 83):
>    la causa dominante del +65 % es que la 9.ª ed. no escribe L_e (×1.51), no el cambio de
>    edición. El hueco de 1.0 ≤ H < 2.0 ft en concreto (hallazgo 3 de ese informe) es
>    hallazgo de VE-3: trátalo o fíchalo.
> 7. **Clases III a V: transcribir CON el tope de diámetro por clase** de M 170M (H1 alto del
>    informe `clases_iii_v_astm_c76.md`): Clase V sólo hasta 1200 mm con pared B; el tope
>    de la Clase IV, ilegible en el ejemplar, queda BLOQUEADO (no se inventa). Cita al USACE
>    como fuente secundaria y di qué corrobora M 170M y qué no (H2, H3).

1. **Clases III a V del tubo de concreto (ensayos del conducto, H1, alta).** Sólo la Clase II
   de M 170M está transcrita, y con más de ≈ 2.4 m de tierra sobre la clave ningún tubo de
   concreto cierra (13 de 57 corridas sin diseño; en 11 la app ya tenía un TMC que cumple).
   El PDF de AASHTO M 170M del repositorio no deja leer esas filas, pero el USACE EM
   1110-2-2902 (en `Normas/ejemplos_resueltos/conducto/`, pág. PDF 71) imprime la tabla de
   ASTM C76: Clase I 40, II 50, III 65, IV 100, V 140 N/m/mm (D0.01). **Recomendación:
   transcribir III a V como [C] desde el USACE, con su cita verificada**; con ellas, 16 de 17
   corridas coinciden con el diseño a mano.
2. **`borde_libre_bajo_tw_ahogante` = `no_cumple` (H5, criterio [A]).** Sobredimensiona hasta
   cuatro escalones cuando el TW ahoga la salida (E07 1.35 → 0.90 con `aviso`). **Recomendación:
   mantener `no_cumple`** (es el lado seguro y fue una decisión anterior del dueño), salvo
   que el dueño prefiera la lectura `aviso`; la sensibilidad ya lo muestra.
3. **O-2 del cabezal (VE3-03):** ancho del acero de temperatura de M9 (el real) frente a la
   franja de 12 in de CDOT; en los casos de CDOT manda el piso. **Recomendación: dejar el
   ancho real** (es el de la ec. 5.10.6-1 aplicada a la sección) y cerrar O-2.
4. **Carga viva de M8 con poco relleno (VE3-04):** lectura literal de la 9.ª ed., del lado
   seguro (+65 % frente a ACPA 2009). **Recomendación: que la revise un ingeniero** antes de
   la sustentación; no hay cambio de código pendiente.
5. **Integrar en `main`** cuando la suite esté verde y los ensayos del cabezal hechos.

Lo que la sesión corrige SIN esperar decisión (defectos frente a la hoja de ruta): H2 (V1 con
control de entrada y TW entre 0.75 D y D usa el tirante normal, contra la nota T-2 de la hoja
de ruta), H4 (V7 omite el peso propio del tubo, contra la fórmula 0.90·(DC + EV) ≥ U, y el
proyecto ya declara el peso del concreto), H3 (el delta de rasante que falta o que ignora V7)
y los titulares engañosos de los «no factible».

## Decisiones pendientes del dueño — ENSAYOS DEL CABEZAL (2026-11-17, ~22:00 UTC)

Informe: `ENSAYOS_DISENO_CABEZAL.md` (Opus, esfuerzo máximo, 10 escenarios, 20 cabezales).
**Veredicto: hoy la app NO entrega buenos diseños de cabezal.** El motor de estabilidad está
bien (111 filas E1–E3 coinciden con un motor independiente); el diseño queda incompleto
(pantalla y alero sin dimensionar) y sobredimensionado (peralte de zapata hasta 4.3 veces).
La sesión corrige YA los DEFECTOS (VE-3.14, abajo). Estas son ELECCIONES de criterio, con la
recomendación de la sesión; la sesión deja cada una implementada como opción del criterio
para que la decisión sea sólo cambiar el valor de archivo:

En curso: **VE-3.14** corrige los DEFECTOS (cortante general 5.7.3.4.2, parada en el tope y
punta que crece, pantalla y alero dimensionados, sismo con agua por C11.6.5.3, textos y
JSON) y deja las elecciones 9–14 como opciones con su efecto medido; respaldo
`claude/youthful-shannon-rjzmuc-respaldo-cabezal-defectos`.

**Corrección de la sesión tras la verificación del dueño (`verificaciones_del_dueno/cabezal_decisiones_9_14.md`):** la cita del Manual de Puentes 2.11.8.5 en la 11 estaba mal leída (es de barreras de sonido): la 11 se sostiene sólo con AASHTO 11.5.7 / Tabla 11.5.7-1. La recomendación 12 se RETIRA (C11.6.5.4 y la hoja de ruta §9.2: un cabezal con aleros puede no ceder; el valor de archivo ya es «sin reducción»). La 14 queda en sólo bajar el margen (HEC-14 5.1.3); la «hoya protegida» se retira por no tener fuente. 9, 10 y 13, con las condiciones de esa verificación. VE-3.14 implementa las opciones con esas condiciones, sin cambiar valores de archivo.

9. **Talón de la zapata (H-2, parte C):** hoy rige el «peso entero» de 11.6.1.2 (2.4 a 13
   veces el momento del método exacto con los talones largos que genera el bucle).
   **Recomendación: método exacto (con la reacción del terreno), como Caltrans BDP 11.2**;
   AASHTO lo permite («unless a more exact method is used», pág. 11-20).
10. **Carga de la pantalla (H-4):** hoy el diagrama del plano virtual del talón (1.5 a 4 veces
    la cuña sobre la propia cara de la pantalla). **Recomendación: cuña de tanteo sobre la
    cara de la pantalla** (Caltrans BDP 11.2, pág. 11.2-27/28).
11. **Factores φ de estabilidad (H-7):** hoy los de zapatas (Tabla 10.5.5.2.2-1: 0.45/0.80).
    **Recomendación: los de muros, Tabla 11.5.7-1 (0.55/1.0)**: 11.5.7 dice «shall be used
    for wall design» y el Manual de Puentes 2.11.8.5 remite a ella.
12. **Régimen estabilidad / armado (H-8):** hoy la estabilidad con muro que cede (k_h =
    0.5·k_h0) y el armado con muro que no cede (K0, k_h0). **Recomendación: el mismo régimen
    para los dos; muro que cede** salvo que el Propietario declare aleros estructurales que
    impidan el giro (C11.6.5.4).
13. **Punto de aplicación del incremento sísmico (H-9):** hoy 0.6·h. **Recomendación: la
    especificación de la 9.ª ed., 11.6.5.3: distribución como la estática y no menos de H/3**
    (el comentario admite 0.4–0.5 h para el total).
14. **Desplante de la salida bajo la hoya de socavación SIN proteger + 0.61 m, además del
    enrocado (H-14):** doble protección. **Recomendación: con el delantal de enrocado
    diseñado, desplantar bajo la hoya protegida** (o bajar el margen); a decidir.

## AVISO DE INTEGRACIÓN EN `main` (2026-11-18, sesión orquestadora, modelo Haiku 5.5)

**Estado al integrar (2026-11-18):** suite verde en clon limpio (7767 / 11 / 7778, bitácora) y en
exportación (7763 / 15 / 7778). Se integra en `main` la rama completa (VE-2 y VE-3, con VE-3.14); las
decisiones 9–14 siguen pendientes del dueño y no cambian ningún valor de archivo.

Cumplidas las dos condiciones de la respuesta del dueño (punto 5):
- **Ensayos del cabezal hechos:** `ENSAYOS_DISENO_CABEZAL.md` (Opus, esfuerzo máximo) y su
  corrección en VE-3.14 (bloques 1–5 y las opciones 9, 10, 11, 13 y 14; la 12 no se propone).
  Las fichas VE3-12 a VE3-17 los recogen.
- **Suite verde:** se mide sobre el conjunto integrado (VE-3.1 a VE-3.14) en clon limpio y en
  exportación; el par medido se anota en la bitácora antes de subir a `main`.

Lo que entra en `main`: VE-3 completo (VE-3.1 a VE-3.14, con las verificaciones y las
correcciones de los ensayos). Las **decisiones 9 a 14 siguen pendientes** y NO cambian ningún
valor de archivo: las opciones están implementadas y medidas (tabla en
`ENSAYOS_DISENO_CABEZAL.md`), y el dueño elige cuál activar cambiando el valor. Si el dueño
prefiere no entrar en `main` hasta decidirlas, avisar aquí antes del push.

## Dónde está cada cosa


- `main` = `3a65e30`: VE-2 integrado con sus correcciones y dos verificaciones Fable.
- `claude/youthful-shannon-rjzmuc` (rama de trabajo de la sesión): VE-3 integrado hasta
  `61a4dcc` y empujado:
  - VE-3.1: bajo control de salida V3 juzga la mayor de `V_erosion` y `V_salida` (ficha VE3-01).
  - VE-3.2: `c_phi_fundacion` y `capacidad_portante_adm` son [S]; `Mw_licuefaccion` sigue [A] (VE3-02).
  - VE-3.3: M9 contra Caltrans BDP 11.2.2 y CDOT Ex. 11/8 (`docs/validacion_cabezal.md`, VE3-03).
  - VE-3.4: M8 contra ACPA, USACE y PPI (`docs/validacion_conducto.md`, VE3-04).
- Repositorio de normas (`Andy-rba30/Normas`, `main` `b845d8b`): `ejemplos_resueltos/` con los
  PDF y hojas de los ejemplos (cajón, cabezal y muros, conducto) y su catálogo.

## En curso (agentes en paralelo) — actualizado tras integrar VE-3.5 a VE-3.8 (`6a87006`); línea base y documentos generados del conjunto en `1fdffd7` (sellos PROVISIONAL)

Integrado en la rama además de lo de arriba: VE-3.5 (la zapata del cabezal se dimensiona por
estabilidad), VE-3.6/3.7 (Familia C: VC3 contra el desnivel F del canal, fuente USBR; remanso
por paso directo), VE-3.8 (correcciones de la revisión Fable a la validación estructural).
148 criterios. El PDF del USBR está en el repositorio de normas (`normas/`).

| Trabajo | Respaldo del trabajo en curso (cada 15 min) |
|---|---|
| **Retomado** (el primer agente se detuvo a las 19:49 UTC; uno nuevo parte de su respaldo `3c15302` y respalda en `claude/youthful-shannon-rjzmuc-respaldo-cabezal-espesor-2`) — VE-3.9: paso 0.10 m y tope 1.5·H como valor de archivo de `dimensionamiento_zapata_cabezal`, y el ESPESOR de la zapata también se dimensiona (armado del talón A1/A2) | `claude/youthful-shannon-rjzmuc-respaldo-cabezal-espesor` |

VE-3.10 (VC3 sin F bloquea) ya está integrado (`8ca5fc9`, ficha VE3-06 en `eb97467`).
VE-3.9 quedó a medias: su último respaldo es `3c15302` en la rama de respaldo de la tabla
(sobre `6a87006`, con un commit «wip VE-3.9» y 21 archivos sin commitear: código, tests,
generados y la §23 de la línea base empezada). Para retomarlo: partir de esa rama, revisar
contra el encargo de VE-3.9 como BORRADOR, terminar, y rebasar sobre la rama de trabajo.

Además en curso: **VE-3.11**, las correcciones de los ensayos del conducto que no esperan
decisión (H2, H3, H4 y titulares), respaldo en
`claude/youthful-shannon-rjzmuc-respaldo-ensayos-h2-h4`. Los informes en curso de
`/home/user/verificacion_fable/` se copian a `informes_en_curso/` con cada respaldo.

**Acuse de la sesión orquestadora (2026-11-17, ~21:05 UTC):** leídas las dos respuestas del
dueño y las dos verificaciones. VE-3.9 integrado (`347d8e2`, `6c54867`, ficha VE3-05 en
`a82b99d`). En curso: VE-3.11 (H2, H3, H4 y titulares; respaldo `…-respaldo-ensayos-h2-h4`),
VE-3.12 (decisiones 1, 3, 6 y 7: clases III–V [C] del USACE con tope por clase, Clase IV
bloqueada donde no se lee; O-2 cerrado; aviso ACPA en F8.CLASE sin gobernar y la redacción del
+65 %; el hueco 1.0–2.0 ft; respaldo `…-respaldo-clases-y-aviso-acpa`) y los ensayos de
diseño del CABEZAL (Opus, esfuerzo máximo; informe en `informes_en_curso/`). La decisión 2
(`no_cumple`) no requiere cambio. Antes de integrar en `main` se avisará aquí.

> **TERCERA RESPUESTA DEL DUEÑO (2026-11-17, ~21:10 UTC) — decisión 8: el borde libre bajo
> el nivel del receptor.** `borde_libre_bajo_tw_ahogante` SIGUE en `no_cumple` (la decisión 2
> no cambia y ningún diámetro adoptado cambia). Lo que cambia es la PRESENTACIÓN: hoy, cuando
> el TW del receptor deja al barril sin borde libre, la progresión sube el diámetro hasta
> D > TW/0.75 (hasta cuatro escalones, E07 0.90 → 1.35 m de los ensayos del conducto) y la
> memoria sólo dice el diámetro adoptado. La justificación del propio criterio dice que la
> causa es el nivel del receptor y que lo que lo resuelve suele ser la cota de la salida o la
> rasante. Pedido:
>
> - En todo punto donde V1 descartó escalones SÓLO por el TW del receptor (el escalón cumplía
>   V1 con su tirante propio y todo lo demás de la Fase 5), la memoria (completa y resumida),
>   el JSON y la pestaña 3 dicen: (a) que el diámetro lo gobernó el nivel del receptor, no el
>   caudal; (b) el diámetro que bastaría por la hidráulica sola (el que `aviso` adoptaría);
>   (c) la cota de salida —o el descenso del TW— con la que ese diámetro cumpliría V1
>   (TW ≤ 0.75·D sobre la solera de salida), rotulada como alternativa que el proyectista
>   evalúa, no como remedio verificado (no se re-corren las demás fases con esa cota).
> - Es presentación emitida por el cálculo (`PasoDeMemoria`, regla «la memoria la emite el
>   cálculo»), no aritmética en M11. Test en rojo primero; caso de los ensayos (E07) y la
>   línea base. Ficha nueva en `docs/decisiones_diferidas.md` si algo queda fuera.
> - Prioridad: después de VE-3.11 y VE-3.12; antes de integrar en `main`.

> **CUARTA INSTRUCCIÓN DEL DUEÑO (2026-11-17, ~21:15 UTC) — la cuota y el PASE.** Vigila tu
> cuota semanal de tokens (el aviso de uso de la sesión, `/usage` o los avisos de límite que
> recibas; si no puedes leerla, tómala como 97 % al primer aviso de límite). **Al llegar al
> 97 %, o antes si ves que se agota, PASA el trabajo a la otra sesión del dueño**, que
> vigila esta rama cada 5 minutos:
>
> 1. Detén los agentes en curso en un punto limpio; respalda en sus ramas `…-respaldo-*`
>    TODO lo que tengan (código, tests, generados e informes de `informes_en_curso/`).
> 2. Pon al día este LEEME (qué está integrado, qué está a medias y en qué rama de respaldo,
>    qué falta, decisiones del dueño pendientes de aplicar) y `PROMPT_CONTINUAR.md`, de modo
>    que una sesión nueva pueda retomar sin leer el chat.
> 3. Escribe `proceso/planes_mejora/ve3_estado/PASE.md` con: hora UTC, % de cuota, el
>    último commit integrado, la lista de ramas de respaldo con su estado (terminado / a
>    medias / sin empezar) y lo PRIMERO que tiene que hacer quien retome.
> 4. Commit con mensaje que empiece por **«PASE:»** y push a esta rama. Desde ese momento
>    no empujes nada más a `claude/youthful-shannon-rjzmuc` ni a sus respaldos: la otra
>    sesión toma la rama.

**Acuse de la sesión orquestadora (2026-11-17, ~21:25 UTC):** leídas la TERCERA respuesta
(decisión 8: presentación del diámetro gobernado por el nivel del receptor, sin cambiar
diámetros) y la CUARTA instrucción (cuota y PASE). La decisión 8 entra en cola detrás de
VE-3.11 y VE-3.12 y antes de `main`. Sobre la cuota: esta sesión no tiene acceso a una
lectura de la cuota semanal y hasta ahora no ha recibido ningún aviso de límite; al PRIMER
aviso de límite se toma como 97 % y se hace el PASE (detener agentes en punto limpio,
respaldar, LEEME y PROMPT_CONTINUAR al día, `PASE.md`, commit «PASE:» y no empujar más).

**Estado (2026-11-17, ~21:45 UTC):** VE-3.11 integrado (`7221fe0`, ficha VE3-08: V7 con el
peso propio del concreto, V1 con el resalto dentro del barril, titulares por V2/V2b/V10, delta
de 7.A rotulado con V7; ningún diámetro de la línea base cambia). En curso: VE-3.12 (decisiones
1, 3, 6, 7; respaldo `…-respaldo-clases-y-aviso-acpa`), la DECISIÓN 8 (VE-3.13; respaldo
`…-respaldo-decision-8`) y los ensayos de diseño del cabezal (informe en `informes_en_curso/`).

**Punto de control (2026-11-17, ~23:00 UTC):** integrados VE-3.12 (clases III–V con tope,
contraste ACPA, O-2) y VE-3.13 (decisión 8); suite del entregable en clon limpio **7732 / 11 /
7743, verde** (`725948e`, bitácora). Falta sólo VE-3.14 (defectos del cabezal; bloques 1 y 2
hechos, 3 a 5 y las opciones en curso; respaldo `…-respaldo-cabezal-defectos`). Las
decisiones 9–14 siguen pendientes del dueño (con la recomendación corregida arriba).

## Decisiones del dueño (2026-11-17)

- VE2-04: sí, V3 con la mayor velocidad bajo control de salida (hecho, VE-3.1).
- VE2-05: c_phi y capacidad portante a [S], Mw sigue [A] (hecho, VE-3.2).
- Validar M8 y M9 con ejemplos americanos; los peruanos no hacen falta para lo estructural.
- El programa DIMENSIONA el cabezal (VE-3.5, en curso).
- Completar la Familia C (VE-3.6/3.7, en curso).
- Que Fable revise al final la validación con ejemplos, contando con que los ejemplos pueden
  estar mal (en curso).
- Después: ensayos de diseño simulados (la app diseña; Fable diseña a mano sin ver la app; se
  compara que cumpla, que no esté sobredimensionado y que sea monótono).
- Guardar el progreso periódicamente (este archivo y las ramas de respaldo).
- Paso 0.10 m y tope 1.5·H de la zapata como valor de archivo; que crezca también el espesor;
  VC3 sin F bloquea el punto (2026-11-17, tarde).
- Sin cuota de Fable: las revisiones independientes y los ensayos de diseño se hacen con Opus a
  esfuerzo máximo. Ensayos del conducto en curso (informe en
  /home/user/verificacion_fable/ENSAYOS_DISENO_CONDUCTO.md, se copia aquí al terminar); los del
  cabezal, después de VE-3.9.

## Pendiente después de lo que está en curso

1. Integrar VE-3.5 y VE-3.6/3.7, regenerar, suite (clon limpio y exportación), sellos, bitácora.
2. Ensayos de diseño simulados con Fable (conducto y cabezal).
3. Validación hidrológica con casos reales calificados (los PDF en el repositorio de normas,
   `ejemplos_resueltos/casos_reales/`, con su informe de calificación): INDECI Piura
   (Miraflores 1971-2008, con y sin FEN), UPeU Colpahuayco–Langui (Témez), UNTumbes TU-107
   (caso adversarial: años duplicados) y ESPOL Intervalles (cajón con HY-8).
4. Abierto para el dueño: VE3-03 O-1/O-2 (Ec y ancho del acero de temperatura de M9) y VE3-04
   (la carga viva de M8 con poco relleno sobre tubos pequeños: del lado seguro, sin ejemplo con
   la edición 2013 o posterior).
5. Integrar en `main` con autorización del dueño.

## Objetivo del dueño (2026-11-20): que no quede NADA implementable pendiente

«La idea es terminar todo; si surge algo nuevo, terminarlo también.» Plan en curso:
- VE-4a a VE-4f en curso (arriba) y **VE-4g** (`claude/ve4g-hec14-limites`): HEC-14 con varios
  barriles y conductos de más de 1.524 m, y el resto de los límites de M6.
- Después de integrar VE-4a y VE-4e (tocan M9): el **muro que no cede** (11.6.5.4) y el
  **cabezal paralelo a la vía en un marco** (T7A-03).
- **Censo completo de pendientes** por un consultor Fable (sólo lectura): fichas abiertas,
  «no evaluable» del código, criterios sin valor, fuentes ausentes, hoja de ruta. Clasifica
  en (A) implementable ya, (B) necesita decisión del dueño, (C) necesita datos externos,
  (D) fuera de alcance; con norma verificada y lotes paralelos. Su informe se copia aquí
  al llegar y se lanzan los (A)/(B).
- Lo que no se puede cerrar con código (EMS, datos reales, revisión de experto, ejemplares de
  norma) queda listado, con la app lista para recibirlo.

## VE-5: lotes del censo (`CENSO_PENDIENTES_FABLE_2026-11-20.md`), lanzados 2026-11-20 ~06:25 UTC

**Decisiones adoptadas por la sesión con la autorización del dueño** («si surgen cosas nuevas,
igual cerrar todo»; «seguir las recomendaciones»): licuefacción como resultado declarado del
EMS con bloqueo de expediente; distribuciones sólo con estimadores que una fuente de Normas
imprima; caída de HEC-14 Cap. 11 dentro del alcance; caja receptora espera HEC-22 (C);
longitud entre cabezales con pasada de refinamiento y aviso; V9 por el diámetro designado; V7
del marco con su DC y γ mínimo; pórtico del marco con empuje en reposo, reducción del 50 % de
3.11.7 sólo en el momento positivo de la losa superior y cantos separados; NO se hace el editor
de [S] en la ventana (R4); el hijo del PDF lee la corrida embebida. Fila de φ de E4/E5 vacía
hasta el EMS. Fuera (D): ítems 15, 16, 25, 27, 32, 33, 35 (cuneta en terraplén), 41.

**Sesiones hijas** (contenedores propios, base `claude/ve4b-prevuelo-hidrologia`; cada una deja
su informe en `informes_ve5/<lote>.md` de su rama):
- VE5-MH `claude/ve5-mh-hidrologia` (ítems 12, 14, 13) — `session_01GF7Ze2ngaZH7BhoD4xRPH3`
- VE5-CAT `claude/ve5-catalogo-cuneta` (20, 21) — `session_01GF7Ze28wiXaC7oeemHKMz1`
- VE5-MET `claude/ve5-metrados` (8) — `session_01GF7Ze22xYu1ZkzUgJXt7tN`
- VE5-GUI `claude/ve5-gui` (37, 38, 40, 42) — `session_01GF7Ze2Yq9kRgSMchXKRNFh`
- VE5-LIC `claude/ve5-licuefaccion` (6) — `session_01GF7ZdzpkYmr6rDW9FAswPa`

**En cola** (cuando se integre lo que toca el mismo archivo): M8 (1 pórtico → 23 → 26) tras
VE-4f; M9 (muro que no cede → 4 → 3 → 9 → 10 → 28 → 29 → cabezal paralelo T7A-03) tras VE-4a y
VE-4e; M6 (2 con Cap. 11; 30, 31 si llegan documentos) tras VE-4g; M4/M5 (17 → 18 → 19 → 24) y
11 tras VE-4c y VE-4d; GUI/M11 2.º lote (39, 43, 44, 45, 46, 47, 48, 49) tras VE5-GUI y VE5-MET;
integrador final: 22, 34, documentos, línea base, conteos. VE-4b terminado (`950f5e4`), en
revisión Fable.

## Apuntado para después de VE-4 (dueño, 2026-11-20): límites de cobertura de la app

Lo que la app hoy no evalúa y se detiene diciéndolo (sin inventar un número). Prioridad según
si las obras reales caen en esos casos:

1. **Cabezal de muro que no cede** (`regimen_cabezal` = `no_cedente`): las presiones de muro
   rígido de AASHTO 11.6.5.4 no están implementadas (MetodoNoEvaluable del cabezal).
2. **Cabezal paralelo a la vía en un marco** (Carta 11 del HDS-5, ficha T7A-03, INF-4.3):
   fuera del alcance declarado.
3. **Carga viva con relleno < 2.0 ft** sobre tubo de concreto o marco (≤ 1.0 ft en flexibles):
   fuera del dominio de AASHTO LRFD 3.6.1.2.6a (MetodoNoEvaluable estructural, M8).
4. **Socavación con HEC-14** en varios barriles o en conductos de más de 1.524 m de alto
   (nota 8 de la Tabla 1.1): MetodoNoEvaluable de HEC-14 (M6; rige el d50 de Laushey).
5. **Datos de producto del fabricante**: perfil del HDPE (`perfil_hdpe_fabricante`), costura
   empernada del TMC y la Clase IV de concreto por encima de 300 mm (ilegible en el ejemplar
   de AASHTO M 170M): DatoFaltante que detiene el escalón.

**HY-8:** el dueño recuerda haber comparado la app con HY-8, pero el repositorio no guarda
esos resultados: `docs/validacion_hy8.md` (generado, último cambio en VE-3.10) sólo trae el
procedimiento, las entradas y las salidas del programa, y la fila INF-3.2.2 del tracker
sigue «Cerrado parcial». Para cerrarla: copiar al repo la tabla HY-8 contra la app (HW de
entrada y de salida, control, velocidad de salida, por punto) con la versión de la app con
que se corrió; si fue antes de VE-3.15, revisar C-01, cuyos números movieron T8-08 y T8-09.

## Entorno

Entorno de nube «Proyecto_alcantarillas» (personal, red abierta). Python 3.12 de `uv` con Tk
en `/home/user/venv312` (`requirements.txt`, PyMuPDF, `pillow<13`; openpyxl sólo para leer las
hojas de CDOT). `NORMAS_DIR=/home/user/Normas`. Suite: `xvfb-run -a python -m pytest -q -p
no:cacheprovider --no-header` en un clon limpio fuera del repositorio.
