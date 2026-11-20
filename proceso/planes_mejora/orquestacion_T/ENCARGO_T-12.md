# Encargo: T-12 (repositorio listo para sustentación) — FASE A, quinta sesión

Eres el agente ejecutor del prompt T-12 de la cadena T, el ÚLTIMO. Worktree `/home/user/wt/T-12`, rama `tesis/T-12`, creada desde
`origin/main` con T-11 integrado (el SHA y el par de referencia te los da el orquestador en el mensaje). No toques
`/home/user/Proyecto_alcantarillas`, `/home/user/wt/main` (consulta) ni `/home/user/wt/estado` (sólo lectura).
`ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/`; `SP` =
`/tmp/claude-0/-home-user-Proyecto-alcantarillas/0d09ea9c-a87f-5311-8eec-38e45d8c2a3d/scratchpad/` (temporales en `SP/T-12/`).

1. Lee PRIMERO, enteros: `ORQ/ORQUESTACION.md` (la ENMIENDA DE LA QUINTA SESIÓN del final gana), `CLAUDE.md` de tu worktree, la
   NOTA DEL ORQUESTADOR y la §2 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`, **tu bloque «T-12» de ese archivo (tu prompt)**,
   **`ORQ/PRECISIONES_T-12.md`** (corrige y acota el prompt; donde discrepe, gana; las decisiones del dueño de LICENCIA y AUTOR ya
   están tomadas: no las vuelvas a preguntar), la sección «Cuarta sesión» de `ORQ/DECISIONES_DUENO_2026-11-12.md`,
   `ORQ/INFORME_T-10_final.md` y `ORQ/INFORME_T-11_final.md` («lo que T-12 debe saber»).
2. SIN CAMBIOS DE CÁLCULO: ningún archivo de `src/modulos/` cambia de comportamiento; la línea base de la Familia C sólo puede
   cambiar por la advertencia de fixture (punto 3), y el comparador de E-B lo demuestra. PARADA (c) vigente.
3. Comprobación previa ya hecha por el orquestador (17:22 UTC): los 18 PDF de `normas/` de la app son IGUALES (sha1) a los de
   `/home/user/andy-rba30/normas/normas/`. Repítela tú antes del `git rm` (si alguno difiere, NO lo retires y repórtalo).
4. Memoria en dos vistas (el punto CONDICIONAL de PRECISIONES): el orquestador te dice en el mensaje si ENTRA o se DIFIERE.
5. FASE A del MODO PARALELO: implementación entera con sus tests (rojo medido contra la base y declarado si no lo escribes
   primero), suite ENTERA verde en tu rama con `NORMAS_DIR=/home/user/andy-rba30/normas` y medida también SIN él (es el eje nuevo
   de la tabla de `CLAUDE.md`), commits `wip(T-12)` con `git push origin tesis/T-12` tras cada bloque (puede haber cortes: di qué
   falta). SIN tocar el `.xlsx` ni la tabla de conteos de `CLAUDE.md`; SIN fusionar ni empujar a `main`.
6. Pie de los commits: el de tu aviso de atribución; si no tienes, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` y
   `Claude-Session: https://claude.ai/code/session_01UcoTV8c2xW71eEw7p9oHgo`. Ningún identificador de modelo en otro sitio del
   repo. El correo del autor NO se escribe en ningún archivo. Nunca `/dev/null` como destino de `cli.py --json`.
7. Entrega: `SP/INFORME_T-12_faseA.md` (IDs entero / en parte / no; tests que salen de la suite del entregable y par nuevo, con y
   sin `NORMAS_DIR`; el CENSO de qué archivo de proceso lee cada test y lo que hiciste con él; qué se movió y adónde; movidos de la
   línea base; diferidos con símbolo; filas del tracker; preguntas; lo que NO hiciste) y, como respuesta, MENOS DE 350 PALABRAS
   con lo esencial y el SHA de la rama. Un auditor revisará tu diff. No ejecutes otro prompt.
