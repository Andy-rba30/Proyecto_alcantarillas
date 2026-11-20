# Encargo: CERRAR la integración de T-6 (geometría) — FASE B a medias

Worktree `/home/user/wt/T-6`, rama `tesis/T-6`. `origin/main` = `5bca7c6` (T-0 + T-2 + T-4 + T-1). El agente que integraba T-6 fue
cortado por el límite de uso cuando iba a «reescribir y ampliar los tests de la pendiente». La rama YA está rebasada sobre
`origin/main` y lleva commits `wip(T-6)` (árbol limpio): squash provisional de FASE A, «reparto con V10, avisos por
InformePunto.avisos()» y «docs, tracker, línea base, generados provisionales». Hay un respaldo del estado previo al rebase en la
rama `tesis/T-6-faseA` (`3462f8b`): sólo consulta, no lo toques.

PRIMERO lee entero `/tmp/claude-0/-home-user/8c9a9d01-15e4-5a10-91d4-d894b414664c/scratchpad/ORQUESTACION.md` (convenciones, FASE B,
commit con su pie, informe). Después `CLAUDE.md` (al menos «Fuente de verdad», «Arquitectura», «Excepciones», «Cierre de tarea»),
la sección T-6 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md` y la sección «T-6» de
`/tmp/claude-0/-home-user/8c9a9d01-15e4-5a10-91d4-d894b414664c/scratchpad/AUDITORIAS_PENDIENTES.md` (el ítem 2 del auditor).
Entiende lo ya hecho con `git log --stat origin/main..HEAD` y leyendo `M7.pendiente_adoptada`, `M5.v10_pendiente_conducto`,
`M5.limites_de_pendiente`, `servicio._S_del_diseno` y `tests/test_t6_geometria.py`.

## Lo que falta (comprueba cada punto contra el árbol; lo que ya esté hecho, verifícalo y no lo rehagas)

1. **Ítem 2 del auditor** (choque `M7.pendiente_adoptada` ↔ V10 de T-2). División decidida: M7 adopta el límite sólo sobre la
   pendiente del CAUCE y lo dice; V10 juzga la pendiente adoptada (sólo puede fallar con una DECLARADA).
   (i) docstring de `M5.v10_pendiente_conducto` y ficha de T-2 alineados con esa división; (ii) origen MAXIMA → paso + aviso:
   S_conducto < S_cauce exige una estructura de caída/disipación y V2b lo juzga según `regimen_v2b` (archivo: `indicador_con_aviso`);
   origen MINIMA → la salida queda más baja que el cauce y G2 lo juzga; los avisos salen por `InformePunto.avisos()`, una sola vez;
   (iii) **tests de punta a punta de los dos casos** (era lo que el agente iba a escribir) y liberar el test `skipif` que esperaba
   las claves `pendiente_minima_conducto` / `pendiente_maxima_conducto`; (iv) ficha T6-02 ampliada con este choque;
   (v) con los valores de archivo (0.0 / 0.10) nada del fixture se mueve: mídelo.
2. Línea base contra `5bca7c6`: material/diámetro/veredicto/admisible/tipo de bloqueo idénticos salvo lo que T-6 declara
   (L, caída, cota de salida, HW de salida, TW de la vía 4, etapa del bloqueo de C-01, avisos). Los adoptados son A-01 y A-02
   concreto Ø 0.90 m (HW gobernante 1.0420 y 0.5720 m). Si algo más se mueve, PARA y repórtalo. README de la línea base al día.
3. Censos sobre el árbol fusionado: criterios (95 en main + los de T-6), `dominios.py` en `test_sin_literales`,
   `test_ext5_forma_gui`, `test_criterios_adoptados`, `test_cierre_perfil`, `test_nivel_medido`, `sin_alcanzar` de
   `test_memoria_sustentada`, `KB_POR_PUNTO_MAX` (en main 70: mide y deja el que corresponda diciéndolo),
   `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT` (fila de T-6), Parte XLIV de `docs/decisiones_diferidas.md`.
4. Tracker `.xlsx` (sobre el de `origin/main`): INF-5.1.18 Cerrado, INF-3.3.3 Cerrado, INF-3.2.7 Cerrado si el ítem 2 queda hecho,
   nota en PC-32 / C10-03 (esviaje: 45°, aviso G3 en vez de `DatoInvalidoError`). Responsable «Claude Code (cadena T, T-6)».
5. `CLAUDE.md`: párrafo de T-6 en el estilo de los de T-1/T-4/T-2 y tabla de pares («sí · no» MEDIDO con `NORMAS_DIR`; las otras
   tres DERIVADAS, dicho así); conteo de criterios.
6. Regenera los cuatro documentos generados y la línea base sobre el árbol final; suite ENTERA verde con
   `NORMAS_DIR=/home/user/andy-rba30/normas` (y mídela también sin él).
7. Aplasta todo en UN commit `tesis(T-6): <resumen> — <IDs canónicos>` sobre `origin/main` (pie obligatorio de ORQUESTACION.md).
8. Entrega: `git -C /home/user/proyecto_alcantarillas merge --ff-only tesis/T-6` (checkout principal limpio en `main`) y
   `git -C /home/user/proyecto_alcantarillas push -u origin main` (reintentos por red 2/4/8/16 s; si devuelve 403 «GitHub
   authentication required», no insistas: repórtalo). Confirma `origin/main == HEAD` y remide el par sobre ese árbol.
   NUNCA `git stash`. Commits intermedios en cada verde (puede haber cortes por límite de uso).
9. Informe final con el formato de ORQUESTACION.md: IDs (entero / en parte / no), tests nuevos, par, números movidos y por qué,
   «diámetros movidos: ninguno», diferidos, SHA en `origin/main`. No ejecutes ningún otro prompt.
