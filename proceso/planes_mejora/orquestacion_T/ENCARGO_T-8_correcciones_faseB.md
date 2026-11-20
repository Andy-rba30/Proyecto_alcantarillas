# Encargo: INTEGRAR en main (FASE B) la pasada de correcciones de T-8 — trabajo de integración, sin cálculo nuevo

Worktree `/home/user/wt/T-8c`, rama `tesis/T-8-correcciones`, HEAD `52f5747` (árbol limpio; base `df1b23c`). Otro agente cerró ahí
la FASE A: correcciones de la segunda auditoría adversarial de T-8 (protección de salida, M6) y seis decisiones del dueño, con la
suite verde en la rama (5029 / 16 / 5045 con `NORMAS_DIR`). **`origin/main` ya es `1522635` (T-5 integrado: 5161 / 16 / 5177).**
Tu trabajo es SÓLO la integración: no cambies fórmulas, valores de archivo ni decisiones; si algo de cálculo no cuadra tras el
rebase, PARA y repórtalo en vez de «arreglarlo».

## Lee primero
1. `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (convenciones; la ENMIENDA final describe la FASE B de esta sesión: rebase aplastado, ritual,
   `git push origin HEAD:main`, pie de commit, informe).
2. **`/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-8_correcciones.md`, entero: sus §9–§10 son tu lista de trabajo** (pasos de la integración, filas y notas del
   tracker, riesgos de rebase: `ProteccionSalida.d50` es ahora «el que rige», campos renombrados de la hoya de socavación, el
   párrafo «T-8 de la cadena T» de `CLAUDE.md` contradice esta pasada y hay que reescribirlo).
3. `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/DECISIONES_DUENO_2026-11-12.md` (sección T-8: lo que el dueño aprobó, incluido que se muevan espesor y longitud de la
   protección de la línea base) y `CLAUDE.md` de `origin/main` (el párrafo de T-5 recién escrito es el modelo de estilo y trae
   los conteos vigentes: 109 criterios, 34 sin valor, collected 5177).

## Pasos
1. `git fetch origin main`; rebase de la rama sobre `origin/main` aplastada en UN commit
   `tesis(T-8): correcciones de la segunda auditoria — <resumen> — INF-3.3.7, INF-5.1.13 (correcciones)`. Conflictos esperables
   con T-5 en `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py`, `M11_reporte.py`,
   `normativa/*`, `decisiones_diferidas.md`, v8, `CLAUDE.md`, generados y línea base: se resuelven conservando LAS DOS cosas
   (nunca descartes lo de T-5). Commits `wip` y `git push --force-with-lease origin tesis/T-8-correcciones` tras cada bloque verde.
2. Censos sobre el árbol fusionado (conteo de criterios y de «sin valor», `test_ext5_forma_gui`, `test_criterios_adoptados`,
   `test_cierre_perfil`, `test_nivel_medido`, `test_memoria_sustentada`, `test_sin_literales`, techos de `test_ext8` REMEDIDOS,
   `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`); fichas T8-07… en la Parte de T-8 de `docs/decisiones_diferidas.md`
   sin chocar con la Parte que T-5 añadió.
3. Línea base de la Familia C regenerada sobre el árbol final y medida con el comparador de E-B contra `1522635`: sólo puede
   moverse lo que la pasada declara (A-01: espesor 0.592 → 0.770 m y longitud 5.00 → 5.40 m; A-02: espesor 0.479 → 0.770 m y
   longitud 5.00 → 5.40 m; textos, avisos, criterios usados, huellas, recuentos). d50 0.338 / 0.274 m sin mover. **Diámetros y
   materiales: ninguno** (A-01 y A-02 concreto Ø 0.90; `F8.CLASE` 37.42 / 37.04 igual). Si algo más se mueve, NO empujes a main.
   README de la línea base con cada diferencia clasificada.
4. Tracker `.xlsx` (openpyxl, sobre el de `origin/main`): notas en INF-3.3.7, INF-5.1.13 y MAT-X6 con el commit; responsable
   «Claude Code (cadena T, T-8)». Los cuatro documentos generados con su sello. `CLAUDE.md`: párrafo de T-8 REESCRITO donde esta
   pasada lo contradice (envolvente por defecto con la piedra, 1.524 m, 360 min como elección declarada, «sin enrocado» nunca como
   conclusión, números nuevos de la línea base), suma de tests, tabla de pares («sí · no» MEDIDO con `NORMAS_DIR`; las otras tres
   DERIVADAS, dicho así), invariante `collected` y cadena de totales.
5. Suite ENTERA verde con `NORMAS_DIR=/home/user/andy-rba30/normas` y medida también sin él; `git push origin HEAD:main`;
   `git fetch origin main`; confirma `origin/main == HEAD`; deja la rama empujada en ese commit.

## Entrega
Informe en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-8_correcciones_faseB.md` y, como respuesta, MENOS DE 250 PALABRAS: SHA en `origin/main`, par medido
(con y sin `NORMAS_DIR`), conflictos resueltos, lo que se movió en la línea base frente a `1522635` («diámetros movidos: ninguno» o
la lista), y cualquier cosa que no cuadró. No ejecutes ningún otro prompt.
