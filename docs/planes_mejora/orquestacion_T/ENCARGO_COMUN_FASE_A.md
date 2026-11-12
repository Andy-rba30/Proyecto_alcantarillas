# Encargo común — prompt T-n de la cadena T, MODO PARALELO, FASE A (tercera sesión, 2026-11-12)

Eres el agente ejecutor de UN prompt de la cadena T (te digo cuál y tu worktree en el mensaje). Trabajas en tu worktree
`/home/user/wt/T-n`, rama `tesis/T-n`, creada desde `origin/main` = `df1b23c`. Otros agentes trabajan a la vez en otros worktrees
(`/home/user/wt/*`): no los toques (puedes LEERLOS si tu encargo lo dice), ni `/home/user/Proyecto_alcantarillas`.

1. PRIMERO lee entero `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (incluida la ENMIENDA del final, que gana donde discrepe: rutas, base, guardado
   de progreso con push a tu rama, lecciones, informe). Después, en tu worktree: `CLAUDE.md` ENTERO, la NOTA DEL ORQUESTADOR y la §2
   de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`, **tu bloque T-n de ese mismo archivo (es tu prompt, tal cual)**,
   `docs/contrato_entradas.md`, y las secciones del INFORME que tu prompt cita.
2. Lee tus precisiones: `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/PRECISIONES_T-n.md`. Corrigen o acotan el prompt; donde discrepen, ganan.
3. Ejecuta la FASE A de ORQUESTACION.md: implementación entera con sus tests (primero en rojo con `xfail(strict=True)`; si no,
   mide el rojo contra `df1b23c` y decláralo), suite ENTERA verde en tu rama con `NORMAS_DIR`, commits intermedios con push a
   `origin tesis/T-n` tras cada uno. SIN tocar el `.xlsx` del tracker, la tabla de conteos de `CLAUDE.md` ni `verificar_sesion.py`;
   SIN fusionar ni empujar a `main`. Verifica TÚ cada cita contra el PDF y cada fórmula con un caso a mano. El orquestador pasará
   un auditor adversarial sobre tu diff: déjalo auditable.
4. Antes de terminar: mide con el comparador de E-B la línea base (`tests/linea_base_familia_c/`, `tests/ejemplo_puntos.csv` a
   perfil y a expediente) contra `df1b23c` y di «diámetros movidos: ninguno» o la lista (PARADA (c)).
5. Entrega: informe completo en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-n_faseA.md` (formato de ORQUESTACION.md, con las filas del tracker que habrá que
   escribir y las preguntas para el dueño) y un resumen de menos de 400 palabras como respuesta. No ejecutes ningún otro prompt.
