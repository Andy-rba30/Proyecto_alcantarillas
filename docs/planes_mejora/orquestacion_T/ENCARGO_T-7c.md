# Encargo: T-7c (cabezal: armado o concreto ciclópeo) — FASE A, cuarta sesión

Eres el agente ejecutor del prompt T-7c de la cadena T. Worktree `/home/user/wt/T-7c`, rama `tesis/T-7c`, creada desde
`origin/main` = `451a10a` (T-0 a T-9, con T-7a y T-7b, integrados; par de referencia
con `NORMAS_DIR`: 5979 passed / 23 skipped / 6002 collected; sin él 5961 / 41). No toques `/home/user/Proyecto_alcantarillas`,
`/home/user/wt/main` (consulta) ni `/home/user/wt/estado` (sólo lectura). `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/`;
`SP` = `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/` (temporales en `SP/T-7c/`).

1. Lee PRIMERO, enteros: `ORQ/ORQUESTACION.md` (convenciones, reglas no negociables, PARADAS, lecciones de las auditorías; la
   ENMIENDA DE LA CUARTA SESIÓN del final gana —salvo la base, que es la de arriba—), `CLAUDE.md` de tu worktree (constitución),
   la NOTA DEL ORQUESTADOR y la §2 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`, **tu bloque «T-7c» de ese archivo (es tu
   prompt, tal cual)**, `docs/contrato_entradas.md`, la sección §4 del INFORME
   (`/home/user/andy-rba30/cotas-esviaje-alcantarillas/INFORME_evaluacion_app_alcantarillas_vs_PDF.md`), y
   **`ORQ/PRECISIONES_T-7c.md`** (corrige y acota el prompt; donde discrepe, gana; trae qué norma arma, el régimen K0 para la
   resistencia y las decisiones del dueño), junto con `ORQ/INFORME_T-7b_final.md` (la interfaz
   `solicitaciones` que consumes). Antes de tocar un objeto: hoja `Conflictos` del tracker
   (`tests/apoyo/tracker.py`, sólo lectura) y `docs/decisiones_diferidas.md` (fichas EXT-7-01, T7A-04, T7A-08, T7B-08, T7B-09, T7B-14).
2. Ejecuta la FASE A del MODO PARALELO de ORQUESTACION.md: implementación entera con sus tests (primero en rojo con
   `xfail(strict=True)`; si no, mide el rojo contra `451a10a` y decláralo), dorados a mano con la aritmética escrita, toda cita
   verificada por ti contra el PDF (numeral, título, página impresa y PDF, texto literal, carácter), suite ENTERA verde en tu rama
   con `NORMAS_DIR=/home/user/andy-rba30/normas`, commits intermedios `wip(T-7c)` con `git push origin tesis/T-7c` tras cada
   bloque coherente (puede haber cortes: deja en el mensaje qué falta). SIN tocar el `.xlsx` del tracker, la tabla de conteos de
   `CLAUDE.md` ni `verificar_sesion.py`; SIN fusionar ni empujar a `main`. Criterios nuevos al FINAL de su sección y constantes en
   bloque `# --- T-7c ---`. Mutación con el arnés de EXT-11 (`tests/apoyo/mutacion.py`, sobre una copia en `SP/T-7c/`) sobre lo
   nuevo de M9, con los vivos clasificados.
3. Antes de terminar: mide con el comparador de E-B la línea base (`tests/linea_base_familia_c/`, y `tests/ejemplo_puntos.csv` a
   perfil y a expediente) contra `451a10a` y di «diámetros/secciones/materiales/HW movidos: ninguno» o la lista (PARADA (c)).
4. Pie de TODOS los commits:

   Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>
   Claude-Session: https://claude.ai/code/session_01Jteyqg5CzW7hzPFvqiat9M

   Ningún identificador de modelo en ningún otro sitio del repo. Nunca `/dev/null` como destino de `cli.py --json`.
5. Entrega: informe completo en `SP/INFORME_T-7c_faseA.md` (formato de ORQUESTACION.md: IDs entero / en parte / no; tests y par
   medido; movidos; diferidos con símbolo; filas del tracker a escribir; preguntas para el dueño con opciones y tu recomendación;
   lo que NO hiciste; y una sección «lo que el auditor debería mirar primero» con las lecturas de la fuente en que más dudas) y,
   como respuesta, MENOS DE 400 PALABRAS con lo esencial y el SHA de la rama. El orquestador pasará un auditor adversarial sobre
   tu diff: déjalo auditable. No ejecutes ningún otro prompt (T-10, la memoria, viene después
   y es de otro agente: deja la tabla de armado por elemento emitida como `PasoDeMemoria`/datos, sin maquetarla de más).
