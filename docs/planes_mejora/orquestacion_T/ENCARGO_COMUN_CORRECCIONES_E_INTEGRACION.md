# Encargo común — CORRECCIONES DE AUDITORÍA + INTEGRACIÓN EN MAIN de un prompt T-n (cuarta sesión, 2026-11-13)

Eres el agente que CIERRA un prompt de la cadena T cuya FASE A hizo otro agente. El orquestador te dice cuál (T-n), tu worktree
(`/home/user/wt/T-n`, rama `tesis/T-n`, base `df1b23c`) y qué hallazgos de la auditoría te tocan. Trabajas en español.
`ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/` (sólo lectura); `SP` =
`/tmp/claude-0/-home-user-Proyecto-alcantarillas/0d09ea9c-a87f-5311-8eec-38e45d8c2a3d/scratchpad/`.

## Lee primero (en este orden)
1. `ORQ/ORQUESTACION.md` ENTERO (convenciones, reglas no negociables, PARADAS, lecciones; la ENMIENDA DE LA CUARTA SESIÓN del
   final gana: base `e78a4e7`, rutas, pie de commit).
2. `CLAUDE.md` de `/home/user/wt/main` ENTERO (constitución; los párrafos de T-5 y de las correcciones de T-8 son el modelo de
   estilo del párrafo que escribirás y traen los censos vigentes: 109 criterios, 34 sin valor, collected 5246).
3. Tu bloque T-n de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md` (y su NOTA DEL ORQUESTADOR), `ORQ/PRECISIONES_T-n.md`,
   `ORQ/INFORME_T-n_faseA.md` (lo que se hizo; sus filas del tracker y sus riesgos), **`ORQ/AUDITORIA_T-n.md` (tu lista de
   correcciones)** y la sección T-n de `ORQ/DECISIONES_DUENO_2026-11-12.md` (decisiones del dueño: se aplican, salvo que el PDF
   contradiga su premisa, y entonces se deja lo que la fuente sostiene y se reporta).

## PARTE 1 — correcciones (en la rama, antes de rebasar o después, como te resulte más limpio)
- Aplica TODOS los hallazgos de la auditoría que el orquestador te asigne, anclando por símbolo. Para cada uno: test que lo fija
  (escrito en rojo primero o con el rojo medido contra el árbol previo), corrección, y una línea en tu informe: «cerrado / cerrado
  en parte / refutado (con la evidencia)». No des por bueno al auditor: si un hallazgo es falso, refútalo con la fuente.
- Toda cita y todo número nuevo o corregido lo verificas TÚ contra el PDF (numeral, título, página impresa y PDF, texto literal,
  carácter). Dorados a mano. Fuente / interpretación / lo-que-el-proyecto-hace, separados.
- Aplica las decisiones del dueño de tu sección.
- **PARADA (c)**: ningún diámetro, sección ni material adoptado del fixture se mueve (A-01 y A-02 concreto Ø 0.90; B-01; C-01
  marco 1.20 × 0.90 donde dimensiona). Si una corrección lo movería, NO la apliques por defecto: déjala como alternativa
  barrible y repórtalo.
- Commits `wip(T-n): …` con `git push --force-with-lease origin tesis/T-n` tras cada bloque (puede haber cortes).

## PARTE 2 — integración (FASE B)
1. `git fetch origin main`; rebase de la rama sobre `origin/main` aplastada en UN commit
   `tesis(T-n): <resumen> — <IDs canónicos del INFORME>`. Conflictos: se conservan LAS DOS cosas (nunca descartes lo que ya está
   en main). Zonas calientes: `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py`, `M11_reporte.py`,
   `normativa/*`, `decisiones_diferidas.md` (tu Parte se renumera a la siguiente libre), v8, `CLAUDE.md`, generados, línea base.
2. Censos recalculados sobre el árbol fusionado (criterios y «sin valor», `CLAVES_EXTERNAS`, marcas `literal-ok`,
   `test_ext5_forma_gui`, `test_criterios_adoptados`, `test_cierre_perfil`, `test_nivel_medido`, `test_memoria_sustentada`,
   `test_sin_literales`, techos de `test_ext8` REMEDIDOS, `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`).
3. Línea base de la Familia C regenerada sobre el árbol final y medida con el comparador de E-B contra `origin/main` previo:
   cada diferencia clasificada en su README; **«diámetros/secciones/materiales movidos: ninguno»** o NO empujas a main.
4. Tracker `.xlsx` (openpyxl, sobre el de `origin/main`; responsable «Claude Code (cadena T, T-n)»; IDs canónicos),
   `docs/decisiones_diferidas.md`, los cuatro documentos generados con su sello (`python3 -m src.normativa.manifiesto --escribir
   --suite "<par>"`, `python3 -m src.indice_formulas …`), `docs/contrato_entradas.md` y `docs/guia_perfil.md` si cambian de contrato.
5. `CLAUDE.md`: párrafo «T-n de la cadena T (fecha) sumó N tests…» en el estilo de los existentes, suma de tests, tabla de pares
   («sí · no» MEDIDO con `NORMAS_DIR`; las otras tres DERIVADAS, dicho así), invariante `collected`, cadena de totales, y las
   reglas de arquitectura que tu prompt añade donde correspondan. Corrige en su sitio lo que tu prompt deje falso.
6. Suite ENTERA verde con `NORMAS_DIR=/home/user/andy-rba30/normas` y medida también sin él. `git push origin HEAD:main`
   (fast-forward; si `main` avanzó: rebase, remide, reintenta; NUNCA `--force` sobre `main`). `git fetch origin main`, confirma
   `origin/main == HEAD`, y deja `tesis/T-n` empujada en ese commit.

## Entrega
Informe completo en `SP/INFORME_T-n_final.md` (hallazgo por hallazgo; IDs entero / en parte / no; tests nuevos y par medido con y
sin `NORMAS_DIR`; números movidos con su causa; diferidos con símbolo; preguntas para el dueño con tu recomendación; lo que NO
hiciste) y, como respuesta, MENOS DE 350 PALABRAS con: SHA en `origin/main`, par, IDs, tests nuevos, movidos («diámetros movidos:
ninguno» o la lista), diferidos, paradas/preguntas. No ejecutes ningún otro prompt. Si algo de cálculo no cuadra tras el rebase,
PARA y repórtalo en vez de forzarlo.
