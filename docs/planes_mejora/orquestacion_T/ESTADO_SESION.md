# Estado de la cadena T — punto de reanudación (se reescribe en cada guardado)

**Prompt de continuación al día: `PROMPT_REANUDAR.md` (misma carpeta).** Para reanudar en una sesión NUEVA: abrir `Proyecto_alcantarillas` (escritura), `Normas` (lectura) y `Cotas-esviaje-alcantarillas`
(lectura; el INFORME está en su rama `claude/serene-mayer-88a2o0`). Leer, en la rama `tesis/orquestacion-estado`, carpeta
`docs/planes_mejora/orquestacion_T/`: este archivo, `ORQUESTACION.md` (convenciones que recibe cada agente; sus rutas de
scratchpad son de la sesión vieja: usar las de la nueva), `NOTAS_ORQUESTADOR.md`, `AUDITORIAS_PENDIENTES.md` y los dos dictámenes.
Entorno: `pip install -r requirements.txt -r requirements-dev.txt openpyxl`; `export NORMAS_DIR=<clon de Normas>`; no hay tkinter
(apt 503): configuración «PyMuPDF sí · Tk no». Suite ~4.5 min.

## Entregado en `origin/main`
- **T-0: `87d1ce7`**. Par con NORMAS_DIR: 4219 passed / 16 skipped / 4235. Diámetros movidos: ninguno.
- **T-2: `ad5cb97`** (hidráulica). Par con NORMAS_DIR: 4390 passed / 16 skipped / 4406 (sin NORMAS_DIR 4383/23). Diámetros movidos: ninguno.
- **T-4: `7fb7926`** (materiales/durabilidad). Par con NORMAS_DIR: 4521 passed / 16 skipped / 4537 (sin NORMAS_DIR 4509/28). Diámetros movidos: ninguno.
- **T-1: `5bca7c6`** (hidrología). Par con NORMAS_DIR: 4712 passed / 16 skipped / 4728 (sin NORMAS_DIR 4694/34). Diámetros movidos: ninguno.
- **T-6: `7e74065`** (geometría; LOTE 1 COMPLETO). Par con NORMAS_DIR: 4850 passed / 16 skipped / 4866 (sin NORMAS_DIR 4832/34). Diámetros movidos: ninguno; L por extremo (+0.9 a +2 %).
- **T-8: `df1b23c`** (protección de entrada y salida; hecho y auditado con Opus; FALTA la auditoría con Fable). Par con NORMAS_DIR: 4960 passed / 16 skipped / 4976 (sin NORMAS_DIR 4942/34). Diámetros y números de Laushey sin mover. Pendiente del dueño: `regla_espesor_longitud_proteccion_salida` (`manual` hoy / `envolvente_hec14`).

- **T-5: `1522635`** (estructural del conducto, Fase 8 real; FASE A con Opus, DOS auditorías adversariales —Opus y Fable—, correcciones e integración con Fable). Par con NORMAS_DIR: **5161 passed / 16 skipped / 5177** (sin NORMAS_DIR 5143/34). 109 criterios, 34 sin valor. Diámetros y materiales movidos: ninguno; `F8.CLASE` nueva en A-01/A-02 (37.42 / 37.04 frente a 50.0 N/m/mm); relleno máximo 2.851 m (1.691 con Tipo 4). El caso G2 de T-4 (TMC Ø 1.95) deja de dimensionar con remachada simple (APROBADO). Informe: `INFORME_T-5_final.md`.

- **T-8 correcciones: `e78a4e7`** (segunda auditoría + seis decisiones del dueño; FASE A Fable, integración Opus). Par con NORMAS_DIR (según CLAUDE.md de main): **5230 passed / 16 skipped / 5246** (sin NORMAS_DIR 5212/34). 109 criterios, 34 sin valor. Movido (APROBADO): espesor 0.592/0.479 → 0.770 m y longitud 5.00 → 5.40 m en A-01/A-02; d50 y diámetros sin mover.

- **T-3: `6c25f1d`** (Familia C: el marco se dimensiona; FASE A Opus, auditoría Fable —AJUSTADO, 12 hallazgos, todos cerrados—, correcciones e integración Opus). Par con NORMAS_DIR: **5336 passed / 16 skipped / 5352** (sin NORMAS_DIR 5318/34). +106 tests. Diámetros/secciones/materiales movidos: ninguno; corrida 6 nueva (C-01 marco 1.20 × 0.90, HW 0.623 m); `n_manning_cajon` = fila `concrete_boxes` de HDS-5 (0.012, 0.015); G1 del marco avisa. INF-0.4 e INF-3.2.1 cerrados; INF-0.5 en parte. Informe: `INFORME_T-3_final.md`. Pendiente del dueño (no bloquea): pesar el marco en V7 (ficha T3-08).

- **T-9: `c654a16`** (espaciamiento de alivios, Fase 10; FASE A Opus, auditoría Opus —AJUSTADO, 11 hallazgos, todos cerrados—, correcciones e integración Opus). Par con NORMAS_DIR: **5529 passed / 19 skipped / 5548** (sin NORMAS_DIR 5511/37). +196 tests. Diámetros/secciones/materiales movidos: ninguno; ÚNICO veredicto que cambia: VB1 de B-01 pasa de «no se evaluó» a NO CUMPLE (530 m desde A-02 > 200 m; decisión C del dueño, criterio `obras_familia_a_extremo_de_cuneta` conmutable); VB2 nueva (aporte ≤ capacidad). INF-5.1.12 e INF-3.3.8 cerrados; INF-5.1.8 en parte. Informe: `INFORME_T-9_final.md`.

- **T-7a: `250c972`** (cabezal: geometría por punto y aleros; FASE A Opus, auditoría Opus —AJUSTADO, 10 hallazgos, todos cerrados—, correcciones e integración Opus). Par con NORMAS_DIR (remedido por el orquestador sobre `250c972`): **5690 passed / 19 skipped / 5709** (sin NORMAS_DIR 5672/37). +161 tests. 119 criterios, 25 sin valor. Diámetros/secciones/materiales/HW movidos: ninguno. INF-5.1.15, INF-3.4.1, INF-3.4.2 cerrados; INF-4.2, INF-4.3, INF-4.1 en parte (los cierra T-7b). Informe: `INFORME_T-7a_final.md`. **LOTE 2 COMPLETO (T-3, T-5, T-7a, T-8, T-9 en main).**

- **T-7b: `451a10a`** (cabezal: ensamble de estabilidad en dos marcos; V5 y V8 con método declarable; FASE A y auditoría con Fable —AJUSTADO, 10 hallazgos, todos cerrados—, correcciones e integración con Opus sobre especificación del orquestador y la cuña de referencia del auditor). Par con NORMAS_DIR: **5979 passed / 23 skipped / 6002** (sin NORMAS_DIR 5961/41). +293 tests. Diámetros/secciones/materiales/HW movidos: ninguno. INF-4.4, INF-4.5, INF-5.1.5, INF-4.1 cerrados; INF-4.2 cerrado con salvedad; INF-4.3 en parte (T7A-03); EXT-7-02, EXT-7-04. Informe: `INFORME_T-7b_final.md`. Con datos de prueba el cabezal de la regla NO pasa E3 estático ni E1 sísmico (sensible a la fila de φ y a los factores de inclinación; iteración de zapata diferida por decisión del dueño).

- **T-7c: `2b13dc1`** (cabezal: armado con AASHTO LRFD Sección 5, E.060 de contraste, alternativa ciclópea; FASE A y auditoría con Fable —AJUSTADO, 12 hallazgos—, correcciones e integración con Opus). Par con NORMAS_DIR: **6253 passed / 23 skipped / 6276** (sin NORMAS_DIR 6235/41). +274 tests. Diámetros/secciones/materiales/HW movidos: ninguno. INF-4.6, INF-3.4.5, EXT-7-01 cerrados. Informe: `INFORME_T-7c_final.md`. NO aplicado (fichas): η en el cabezal (T7C-11), 14.3.1 a [N→] (T7C-10). Criterio nuevo sin valor: `clase_exposicion_fisuracion_cabezal`. **Cabezal completo (T-7a, T-7b, T-7c) en main.**

- **T-7 verificación: `2265d90`** (verificador Fable sobre las correcciones de fórmula de los cierres de T-7b y T-7c: 6 conformes, 3 defectos; corregidos e integrados por Fable). Par con NORMAS_DIR: **6287 passed / 23 skipped / 6310** (sin NORMAS_DIR 6269/41). +34 tests. V8 a presión compite con el perfil y nunca da menos que la carga de diseño; η_I del cruce en el cabezal (η_D, η_R [A] nuevos); piso de la zapata armada 0.37 → 0.404 m (A8 cumple por construcción). Diámetros/secciones/materiales/HW movidos: ninguno. Informe: `INFORME_T-7_verificacion.md`. Hallazgo sin corregir: escalón de 11 mm de E-A en HW/D = 1.2 (ficha T7V-01).

- **T-10: `14f6138`** (memoria M11 completa; FASE A, auditoría corta y cierre con Opus —AJUSTADO, ningún cálculo cambió, 7 hallazgos cerrados—). Par con NORMAS_DIR: **6337 passed / 23 skipped / 6360** (sin NORMAS_DIR 6319/41). +50 tests. INF-3.4.7 e INF-4.7 cerrados; nota en INF-5.1.10. Movidos: ninguno. Tamaño: 107.04 KB y 31.0 páginas por punto. Informe: `INFORME_T-10_final.md`. El mismo commit está en `tesis/T-10-final`.

## CUARTA SESIÓN (abierta 2026-11-13 03:56 UTC; el orquestador corre en Fable porque así quedó el selector — el dueño fue avisado; regla del dueño: «Fable sólo cuando sea necesario»)
- Entorno: `/home/user/andy-rba30/normas` (NORMAS_DIR) y `/home/user/andy-rba30/cotas-esviaje-alcantarillas` (rama del INFORME) clonados; worktrees `/home/user/wt/{main,estado,T-3,T-9,T-7a}`; scratchpad nuevo (ver ENMIENDA DE LA CUARTA SESIÓN en `ORQUESTACION.md`).
- 04:05 UTC — lanzadas en paralelo las tres auditorías adversariales de FASE A (sólo lectura): **T-3 con Fable** → `SP/AUDITORIA_T-3.md`; **T-9 con Opus** (`ENCARGO_AUDITORIA_T-9_fable.md` + añadidos A–D sobre las decisiones del dueño) → `SP/AUDITORIA_T-9.md`; **T-7a con Opus** → `SP/AUDITORIA_T-7a.md`. Los informes se copian a esta carpeta al llegar.
- 05:20 UTC — T-3 EN MAIN (`6c25f1d`). T-9: correcciones hechas (`9880688` en `tesis/T-9`) e INTEGRANDO sobre `6c25f1d` (Opus; `ENCARGO_T-9_cierre.md`). T-7a: correcciones hechas en `tesis/T-7a` (`d90cf1a`, 5113 / 16 / 5129 en la rama; `INFORME_T-7a_correcciones.md` en SP), espera «integra» tras T-9 (`ENCARGO_T-7a_cierre.md`). T-7b: precisiones listas (`PRECISIONES_T-7b.md`, punto 0 = V5 declarable + puerta de `ancho_derecho_via_m`, decisión del dueño del 13-nov).
- 05:58 UTC — T-9 EN MAIN (`c654a16`). T-7a INTEGRANDO sobre `c654a16` (Opus, agente reanudado; si se corta: retomar desde `origin/tesis/T-7a` con `ENCARGO_T-7a_cierre.md`, PARTE 2). Decisión del dueño (05:35): cabezal normal al eje por defecto.
- 06:23 UTC — T-7a EN MAIN (`250c972`). **T-7b FASE A lanzada con FABLE** (worktree `/home/user/wt/T-7b`, rama `tesis/T-7b` desde `250c972`; `ENCARGO_T-7b.md` + `PRECISIONES_T-7b.md`; si se corta: retomar desde `origin/tesis/T-7b` con el mismo encargo). Después: auditoría Fable de T-7b → correcciones → integración (Opus) → T-7c (Fable) → T-10 (Opus) → T-11 → T-12 (Opus).
- 08:56 UTC — **T-7b FASE A TERMINADA con Fable** (`fc792d9` en `tesis/T-7b`; 5910 / 21 / 5931 en la rama; +222 tests; diámetros/HW movidos: ninguno; `INFORME_T-7b_faseA.md`). **Auditoría adversarial con Fable lanzada a las 09:00** → `SP/AUDITORIA_T-7b.md`. Preguntas al dueño RESUELTAS el 13-nov 09:45 («sigue con tus recomendaciones»; ver DECISIONES_DUENO): antes eran `drenaje_trasdos` de archivo = `drenado` (hoy `sin_drenaje`: nada se evalúa); el cabezal de la regla de T-7a NO pasa estabilidad con datos de prueba → iterar el ancho de zapata B con paso y techo [A]; k_h sin reducir deja la sísmica «no evaluable» → declarar la reducción por desplazamiento (decisión del Propietario). Se mantienen sin preguntar: terreno delante horizontal, fila de φ de zapatas (0.45/0.80), V8 «sin desborde».
- 10:40 UTC — T-7b EN MAIN (`451a10a`). **T-7c FASE A lanzada con FABLE** (worktree `/home/user/wt/T-7c`, rama `tesis/T-7c`; `ENCARGO_T-7c.md` + `PRECISIONES_T-7c.md`; si se corta: retomar desde `origin/tesis/T-7c`). Después: auditoría Fable de T-7c (incluye revisar la cuña de T-7b) → correcciones/integración (Opus) → T-10 → T-11 → T-12 (Opus).
- 12:33 UTC — **T-7c FASE A TERMINADA con Fable** (`f50edbe` en `tesis/T-7c`; 6200 / 23 / 6223 en la rama; +221 tests; diámetros/HW movidos: ninguno; `INFORME_T-7c_faseA.md`). **Auditoría adversarial con Fable lanzada a las 12:35** (incluye la cuña de T-7b) → `SP/AUDITORIA_T-7c.md` (si el auditor no puede escribir archivos, se extrae de su transcript como las de T-3 y T-7b). Después: correcciones + integración con Opus (`ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md`; redactar `ENCARGO_T-7c_cierre.md` con las resoluciones), y T-10 → T-11 → T-12 con Opus.
- 12:58 UTC — auditoría Fable de T-7c LLEGADA (AJUSTADO: 2 ALTA, 5 MEDIA, 5 BAJA; la cuña de T-7b APROBADA; `AUDITORIA_T-7c.md`). **Cierre de T-7c (correcciones + integración) lanzado con OPUS** (`ENCARGO_T-7c_cierre.md`; si se corta: retomar desde `origin/tesis/T-7c`). T-10 preparado: `ENCARGO_T-10.md` + `PRECISIONES_T-10.md` (lanzar con Opus cuando `tesis(T-7c)` esté en main: worktree `/home/user/wt/T-10` desde `origin/main`; FASE A → auditoría corta con Opus → correcciones e integración).
- 14:55 UTC — T-7c EN MAIN (`2b13dc1`). Lanzados EN PARALELO: **verificador Fable** (sólo lectura) sobre las correcciones de fórmula de los cierres de T-7b y T-7c → `SP/VERIFICACION_T-7_fable.md` (decisión del dueño de las 13:10; si halla defectos los corrige Fable con commit propio en main), y **T-10 FASE A con Opus** (worktree `/home/user/wt/T-10`, rama `tesis/T-10` desde `2b13dc1`; `ENCARGO_T-10.md`). Después de T-10: auditoría corta con Opus → correcciones e integración → T-11 → T-12 (Opus).
- 15:15 UTC — verificación Fable LLEGADA (`VERIFICACION_T-7_fable.md`: 6 conformes; 3 defectos: V8 a presión puede dar menos carga que la lámina libre —MEDIA—; η = 1.00 implícito en el cabezal frente a 1.05 del conducto —MEDIA—; el piso de la zapata armada no puede cumplir E.060 15.7 —BAJA—). **Corrección lanzada con FABLE** (worktree `/home/user/wt/T-7v`, rama `tesis/T-7-verificacion`; `ENCARGO_T-7_verificacion_correcciones.md`; integra él mismo en main con commit `tesis(T-7): verificacion…`; si se corta: retomar desde `origin/tesis/T-7-verificacion`). T-10 FASE A (Opus) sigue en paralelo y rebasará sobre ese commit.
- T-7 verificación EN MAIN (`2265d90`). T-10 FASE A (Opus) sigue; se le avisó de rebasar sobre `2265d90`. Después: auditoría corta de T-10 con Opus → correcciones e integración → T-11 → T-12 (Opus). Ya no queda trabajo planificado para agentes Fable.
- 16:22 UTC — T-10: FASE A (`3f1ee53` en `tesis/T-10`, 6326 / 23 / 6349) y auditoría corta con Opus (`AUDITORIA_T-10.md`: AJUSTADO, ningún cálculo cambió, 2 MEDIA + 5 BAJA) HECHAS. **Correcciones + integración de T-10 en curso con Opus** (agente reanudado; si se corta: retomar desde `origin/tesis/T-10`, aplicar `AUDITORIA_T-10.md` y la PARTE 2 de `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md`; el árbol se APLASTA sobre `origin/main`). **Siguiente: T-11** (`ENCARGO_T-11.md` + `PRECISIONES_T-11.md`: implementa OPUS; audita FABLE; lo que toque fórmulas lo corrige Fable) y T-12 (Opus; dos vistas de la memoria: replantear al dueño).
- 16:50 UTC — T-10 EN MAIN (`14f6138`). **T-11 FASE A lanzada con OPUS** (worktree `/home/user/wt/T-11`, rama `tesis/T-11`; `ENCARGO_T-11.md` + `PRECISIONES_T-11.md`; si se corta: retomar desde `origin/tesis/T-11`). Después: auditoría adversarial de T-11 con FABLE → correcciones (fórmulas/citas: Fable; resto Opus) e integración → T-12 (Opus; `PRECISIONES_T-12.md` en borrador: faltan del dueño la LICENCIA, el nombre del autor y confirmar las dos vistas de la memoria).
- 17:05 UTC — corte de la cuarta sesión con T-11 FASE A a medias: `bc3531b` en `tesis/T-11` (punto 1 hecho: juego DATOS DE PRUEBA, `docs/validacion_integral.md` generado, un xfail de diagnóstico; FALTAN contrato 3.4, punto 3 sensibilidad, punto 2 HDS-5/HY-8, alcance declarado, corrida de referencia con hidrología, fichas, suite, línea base).

## QUINTA SESIÓN (abierta 2026-11-13 17:16 UTC; orquestador en Opus 5.5)
- Entorno: Normas y Cotas clonados en `/home/user/andy-rba30/`; worktrees `/home/user/wt/{main,T-11}` y `/home/user/orq` (= `/home/user/wt/estado`); SP nuevo (ENMIENDA DE LA QUINTA SESIÓN en `ORQUESTACION.md`). Límites a las 17:16: «Semanal · todos» 59 % (reinicia HOY 19:00 UTC según el evento); el dueño avisa que Fable se restablece a las 14:00 de Perú (19:00 UTC): la auditoría Fable de T-11 se lanza al restablecerse.
- 17:25 UTC — suite de `14f6138` en marcha para confirmar el par; **continuación de T-11 FASE A lanzada con OPUS** (worktree `/home/user/wt/T-11`; `ENCARGO_T-11.md` + `PRECISIONES_T-11.md` + «continúa desde `bc3531b`»; si se corta: retomar desde `origin/tesis/T-11`).
- 17:22 UTC — comprobación previa para T-12: los 18 PDF de `normas/` de la app están IGUALES (sha1) en el repositorio Normas: se pueden retirar sin que el dueño suba nada. Encargo de la auditoría Fable de T-11 listo (`ENCARGO_AUDITORIA_T-11_fable.md`); recordatorio programado a las 19:03 UTC.
- 17:33 UTC — par de `14f6138` CONFIRMADO por el orquestador con `NORMAS_DIR`: 6337 passed / 23 skipped (collected 6360), 7 min 10 s.
- (histórico) auditoría de T-7b → correcciones (ALTA de fórmula/cita: Fable; resto Opus) → integración (Opus) → T-7c (Fable) (Opus; Fable sólo para correcciones ALTA de fórmulas/citas), después T-7b → T-7c (Fable), T-10 → T-11 → T-12.

## Estado de las ramas al cerrar la tercera sesión (tercera sesión, reanudada 2026-11-12 15:35 UTC) — ramas en el remoto; NADA de esto en main todavía
| Prompt | Rama | Estado |
|---|---|---|
| T-8 correcciones | `tesis/T-8-correcciones` (`52f5747`, desde `df1b23c`) | **FASE B (integración) EN CURSO con OPUS desde las 17:45 UTC** (`ENCARGO_T-8_correcciones_faseB.md`; si se corta: retomar desde `origin/tesis/T-8-correcciones`, rebasar sobre `origin/main` y seguir ese encargo). FASE A CERRADA con Fable (17:25 UTC): 5029 / 16 / 5045 con `NORMAS_DIR` (5011 / 34 sin él); +69 tests; mutación de M6 531–536 / 574. Auditoría corregida entera (H12 refutado en parte) y las seis decisiones del dueño aplicadas. Números movidos (APROBADOS): A-01 espesor 0.592 → 0.770 m y longitud 5.00 → 5.40 m; A-02 espesor 0.479 → 0.770 m y longitud 5.00 → 5.40 m; d50 sin mover (rige Laushey); `manual` reproduce lo anterior; diámetros movidos: ninguno. **FALTA LA FASE B (integración), con OPUS**, cuando T-5 esté en main: la lista exacta está en §9–§10 de `INFORME_T-8_correcciones.md` (riesgos de rebase: `ProteccionSalida.d50` es ahora «el que rige»; campos renombrados de la hoya; el párrafo de T-8 de `CLAUDE.md` contradice esta pasada y hay que reescribirlo). Preguntas al dueño: digitalizar Figs. 3.3–3.4; `max(V_c, V_erosion)` en M4; fuera de la Tabla 10.1; techo de 360 min (no sale de HEC-14: declarado); conseguir AASHTO M 288 |
| T-3 Familia C | `tesis/T-3` (`255c97a`, desde `df1b23c`) | **FASE A TERMINADA** (Opus): 4999 / 16 / 5015 en su rama; diámetros movidos: ninguno (C-01 pasa de bloqueado a marco 1.20 × 0.90 en la corrida por defecto: movimiento declarado); informe `INFORME_T-3_faseA.md`. FALTA: auditoría adversarial con Fable (aplazada por dosificación), correcciones y FASE B. PARADA (c) abierta: la progresión de secciones que pide la cadena (1.00–4.00 × 1.00–3.00) NO contiene 1.20 × 0.90 y deja a C-01 sin dimensionar; en el archivo quedó [A] provisional ((1.20, 0.90), (1.50, 1.20), (2.00, 1.50)). Otras preguntas: embocadura del cajón (aletas 30–75° hoy; la decide T-7a), VC2 aviso o bloqueo |
| T-7a cabezal geometría | `tesis/T-7a` (`1b83d39`; código en `64f7d02`; desde `df1b23c`) | **FASE A TERMINADA** (Opus): 5034 / 16 / 5050 en su rama; diámetros movidos: ninguno; informe `INFORME_T-7a_faseA.md`. FALTA: auditoría adversarial con Fable (aplazada por dosificación), correcciones y FASE B (después de T-3: la embocadura/ke del cajón deben ser de la banda 30–75°, que es lo que T-3 dejó y el dueño confirmó). Hallazgo T7A-01: la Fase 9 por punto NO se alcanza a expediente porque V5 se detiene siempre en `ancho_derecho_via_m`, que no tiene puerta de entrada (hay que abrirla: dato externo; candidato a T-7b o a la integración). Lecturas a confirmar: cos α en la longitud de aleros (no sen α), pie del cabezal de salida en la más baja entre solera y fondo del receptor (A-01: −0.69 m), zapata como «footing» de AASHTO 12.6.5; sin los 60° de la caja receptora (Lámina 02-A sin aleros). Pies de commit con otra atribución: se aplastan al integrar |
| T-9 espaciamiento | `tesis/T-9` (`304cea6`, desde `df1b23c`) | **FASE A TERMINADA** (Opus): 5059 / 19 / 5078 en su rama; diámetros movidos: ninguno; informe `INFORME_T-9_faseA.md`. FALTA: auditoría adversarial con Fable (`ENCARGO_AUDITORIA_T-9_fable.md`; se lanzó y se PARÓ a los 2 min por dosificación: relanzar cuando T-5 y T-8 estén en main), correcciones y FASE B. Preguntas al dueño: valor de `seccion_cuneta` (propone 0.40 × 1.20 m, mínimo de la Tabla 34 «muy lluviosa»), borde libre de la cuneta (v8 sin cifra), TR 35 años, si las obras A cuentan como extremo de tramo |

**2026-11-12 ~16:00 UTC — el dueño restablece Fable («úsalo de manera normal, no te limites a Opus 5.5»)**: auditorías adversariales
con Fable lanzadas para T-8 (`ENCARGO_AUDITORIA_T-8_fable.md` → `AUDITORIA_T-8_fable.md`; correcciones en una pasada sobre main) y
para T-5 (`ENCARGO_AUDITORIA_T-5_fable.md`, en paralelo con la de Opus). Desde ahora: auditorías, T-7b, T-7c y T-11 con Fable; lo
ya lanzado con Opus sigue con Opus.

**DOSIFICACIÓN REFORZADA (dueño, 2026-11-12 ~17:20 UTC, con Fable en 75 %): «dosifica más Fable, para lo más crítico y donde se
necesite».** Fable SÓLO para: implementación y auditoría de T-7b y T-7c; auditoría de T-3; correcciones de severidad ALTA que
toquen fórmulas o citas. OPUS para: todas las integraciones (FASE B), auditorías de T-9 y T-7a (con pasada corta de Fable sólo
sobre lo que Opus marque dudoso), correcciones MEDIA/BAJA, T-10, T-12; T-11 según cuota. El orquestador corre en Fable: mínimas rondas.

**REPARTO ANTERIOR (dueño, 2026-11-12 ~16:10 UTC; sustituye al de «Decisiones del dueño» de abajo): «usa Fable en lo importante,
Opus puede usarse para lo sencillo».** Fable: auditorías adversariales, correcciones de auditoría, integraciones (FASE B) de los
prompts de cálculo, implementación de T-7b, T-7c, T-11 y de cualquier prompt de cálculo que se lance de aquí en adelante.
Opus 5.5: lo sencillo (T-12, regeneración de documentos, tareas mecánicas, T-10 si resulta mecánico). Las FASE A de T-3, T-7a y
T-9 ya lanzadas con Opus NO se interrumpen (su trabajo está guardado en sus ramas); las audita y las corrige/integra Fable.

Los agentes empujan WIP a su rama tras cada commit: si hay corte, se retoma desde `origin/tesis/T-n` con el mismo encargo
(«continúa: mira `git log`/`git status` y completa lo que falte»).

Orden de integración (serie; cada uno: rebase sobre origin/main aplastado en UN commit `tesis(T-n): …`, censos, generados, línea
base, tracker, decisiones_diferidas, tabla de CLAUDE.md, suite verde con NORMAS_DIR, `git push origin HEAD:main`):
~~T-5~~ (hecho, `1522635`) → **T-8 (correcciones; integrando) → T-3 → T-9 → T-7a** (T-3 antes que T-7a por `embocadura_cajon`; T-5 antes que T-3 por M8/marco). Después T-7b → T-7c (Fable),
T-10 (Opus) → T-11 (Fable) → T-12 (Opus). Auditorías con Fable pendientes: **T-8** (ya en main: pasada de correcciones), T-5, T-3,
T-9, T-7a. Ningún diámetro del fixture puede moverse (A-01 y A-02 Ø 0.90).

## PUNTO DE REANUDACIÓN (guardado 2026-11-12 17:47 UTC — marca del 96–97 % de Fable)
«Semanal · Fable» 94 % a las 17:43 (subía ≈ 0.8 puntos/min con dos agentes Fable); «Semanal · todos» 78 %. Reinicio que da el
evento: mié 18-nov 19:00 UTC. **Una sesión nueva debe abrirse con el modelo OPUS 5.5** (el orquestador en Fable gasta Fable en cada
ronda) y seguir en este orden:
1. Comprobar si la integración de las correcciones de T-8 entró (`git log origin/main`: commit `tesis(T-8): correcciones de la
   segunda auditoria …` sobre `1522635`). Si no, terminarla con Opus (`ENCARGO_T-8_correcciones_faseB.md`).
2. T-3 (`tesis/T-3`, `255c97a`), T-9 (`tesis/T-9`, `304cea6`) y T-7a (`tesis/T-7a`, `1b83d39`) tienen la FASE A hecha y SIN
   auditar. Reparto (dosificación reforzada): auditoría de T-3 con FABLE (cuando haya cuota); auditorías de T-9
   (`ENCARGO_AUDITORIA_T-9_fable.md` sirve tal cual para Opus) y de T-7a con OPUS, con pasada corta de Fable sólo sobre lo dudoso;
   correcciones ALTA de fórmulas/citas con Fable, el resto con Opus; integraciones con Opus, en serie T-3 → T-9 → T-7a, aplicando
   `DECISIONES_DUENO_2026-11-12.md` (T-3: progresión del marco y embocadura; T-9: cuneta, borde libre, obras A; T-7a: cos α, pie
   del cabezal, caja sin aleros, puerta de `ancho_derecho_via_m`).
3. T-7b → T-7c con Fable (dictamen del marco del cabezal en esta carpeta). T-10 (Opus) → T-11 (según cuota) → T-12 (Opus).
4. Preguntas abiertas al dueño (recomendación del orquestador dada, SIN respuesta todavía): de T-8 — digitalizar Figs. 3.3–3.4 de
   HEC-14 en prompt aparte (recomendado sí), `max(V_c, V_erosion)` en la banda de régimen de M4 (sí), fuera de la Tabla 10.1 dejar
   cotas inferiores + aviso (como está), 360 min (sí); de T-5 — confirmar tres cosas hechas sin decisión expresa: `DatoFaltanteError`
   cuando a un punto sólo le falta un dato de la Fase 8, pandeo del HDPE con el MAYOR entre la letra y la suma por duración, y la
   tubería empernada de EG-2013 507.02 a) que hoy detiene (alternativa: diferirla a perfil con aviso); T-9 — TR de 35 años, pendiente
   de que el auditor verifique la fila en el PDF.
5. Documentos que debe conseguir el dueño: AASHTO M 170M o ASTM C76M legible (Clases I, III, IV, V), AASHTO M 288, tabla de
   equivalencia Proctor para la instalación Tipo 3, perfil del fabricante del HDPE.
6. Pendiente fuera de la cadena (decisión del dueño): armado del marco de la Familia C (ver NOTAS_ORQUESTADOR.md).

## Aviso de cuota (histórico, 2026-11-12 04:30 UTC; el dato vigente está en USO.md)
Semanal de Fable al 97 % (marca del dueño alcanzada: guardado y prompt entregados); semanal de todos los modelos al 80 %; ambos
reinician el sábado 14 a las 05:00 UTC. El orquestador de la sesión original corre en Fable: una sesión NUEVA debe orquestar con
Opus 5.5 y reservar Fable (desde el sábado) para las auditorías adversariales pendientes (T-8, T-5 y los que se hagan con Opus) y
para T-7b, T-7c y T-11.

## Decisiones del dueño (vigentes)
- T-4 punto 3: OPCIÓN A (`v_max_tmc` [A], 4.572 m/s, ventana 3.048–4.572; dictamen). T-7b punto 1: OPCIÓN (b) LRFD rige + ASD E.050 en paralelo (dictamen).
- Familia B: aceptación «V1+V2+V4+V5+espaciamiento Fase 10» → cablear en T-9. INF-5.1.8 → T-9. Severidades INF- aceptadas como propuestas.
- FEN: se RESTAURA «adoptar el más conservador»; `serie_sin_fen` sólo como contraste (NO_CUMPLE si da menos que la completa).
- `borde_libre_bajo_tw_ahogante` = `no_cumple` (opción a).
- Umbrales electroquímicos de AASHTO LRFD sobre TMC: por analogía, `aviso` por defecto y `excluye` barrible.
- FEN: `serie_sin_fen` con menos lluvia que la completa BLOQUEA el cálculo hidrológico del punto (el Q por columna sólo avisa).
- Pendiente: M7 adopta mínima/máxima sólo sobre la pendiente del cauce y lo dice; V10 juzga las declaradas (decisión del orquestador, comunicada).
- Todo verificado contra el PDF y coherente ingenierilmente (tesis); auditor adversarial antes de cada cierre de prompt de cálculo
  (puede aligerarse en T-10 y T-12 si el dueño lo pide; aún no lo ha pedido).
- Guardar progreso en el remoto con frecuencia.
- **Reparto de modelos (2026-11-12, límite «Semanal · Fable» casi agotado; reinicia sáb 14 05:00 UTC):** lo que no requiere Fable va
  con Opus 5.5 en esfuerzo extra (agentes con `model: opus`, `effort: xhigh`): implementación de T-8, T-5, T-9, T-3, T-7a,
  integraciones, T-10, T-12. Se reserva a Fable: auditorías adversariales de los prompts de cálculo, T-7b, T-7c y T-11.
  Los prompts de cálculo hechos con Opus pasan una auditoría adversarial con Opus antes de integrarse y una segunda con Fable
  cuando haya cuota (pasada de correcciones). Vigilancia: a 96–97 % de Fable guardar y dejar prompt; a 99 % revisar avance.

## Después del lote 1
Lote 2 en paralelo: T-3 (T-2, T-4 y T-6 ya en main: LISTO PARA LANZAR), T-5 (tras T-4), T-7a (T-2 y T-6 ya en main: LISTO PARA LANZAR; longitud entre cabezales, ficha T6-01; socavación de T-8 para el desplante), T-8 (tras T-2; HEC-14: socavación = cap. 5),
T-9 (T-1 ya está en main: LISTO PARA LANZAR con Opus; + Familia B + INF-5.1.8; duración mínima de lluvia y C de pavimento ya resueltos por T-1). Luego T-7b → T-7c, y T-10 → T-11 → T-12.
Resumen al dueño tras cada prompt: IDs (entero / en parte / no), tests nuevos, números movidos y por qué, diferidos, SHA.
