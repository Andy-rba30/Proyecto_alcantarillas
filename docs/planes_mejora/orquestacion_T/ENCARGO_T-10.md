# Encargo: T-10 (memoria M11 completa) — FASE A, cuarta sesión

Eres el agente ejecutor del prompt T-10 de la cadena T. Worktree `/home/user/wt/T-10`, rama `tesis/T-10`, creada desde
`origin/main` (el SHA y el par de referencia te los da el orquestador en el mensaje). No toques `/home/user/Proyecto_alcantarillas`,
`/home/user/wt/main` (consulta) ni `/home/user/wt/estado` (sólo lectura). `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/`;
`SP` = `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/` (temporales en `SP/T-10/`).

1. Lee PRIMERO, enteros: `ORQ/ORQUESTACION.md` (convenciones, reglas no negociables, PARADAS, lecciones; la ENMIENDA DE LA CUARTA
   SESIÓN del final gana —salvo la base—), `CLAUDE.md` de tu worktree (constitución; en especial «La memoria la EMITE el cálculo;
   M11 la formatea», «Ningún texto literal se transcribe dos veces», «Tres cosas se imprimen separadas», EXT-4 y EXT-8), la NOTA
   DEL ORQUESTADOR y la §2 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`, **tu bloque «T-10» de ese archivo (tu prompt)**,
   y **`ORQ/PRECISIONES_T-10.md`** (corrige y acota el prompt; donde discrepe, gana).
2. FASE A del MODO PARALELO de ORQUESTACION.md: implementación entera con sus tests (primero en rojo con `xfail(strict=True)`;
   si no, rojo medido contra la base y declarado), suite ENTERA verde en tu rama con `NORMAS_DIR=/home/user/andy-rba30/normas`,
   commits `wip(T-10)` con `git push origin tesis/T-10` tras cada bloque (puede haber cortes: di qué falta). SIN tocar el `.xlsx`,
   la tabla de conteos de `CLAUDE.md` ni `verificar_sesion.py`; SIN fusionar ni empujar a `main`.
3. Antes de terminar: comparador de E-B y `diff` sobre la línea base contra la base: «diámetros/secciones/materiales/HW
   movidos: ninguno», y cada diferencia clasificada como FORMATO.
4. Pie de los commits: el de tu aviso de atribución de sesión; si no tienes, `Co-Authored-By: Claude Opus 5.5
   <noreply@anthropic.com>` y `Claude-Session: https://claude.ai/code/session_01Jteyqg5CzW7hzPFvqiat9M`. Ningún identificador de
   modelo en otro sitio. Nunca `/dev/null` como destino de `cli.py --json`.
5. Entrega: `SP/INFORME_T-10_faseA.md` (IDs entero / en parte / no; tests y par; el CENSO de lo que faltaba y cómo quedó; medida
   de tamaño por fase antes/después; movidos; diferidos con símbolo; filas del tracker; preguntas; lo que NO hiciste) y, como
   respuesta, MENOS DE 350 PALABRAS con lo esencial y el SHA de la rama. Un auditor revisará tu diff. No ejecutes otro prompt.
