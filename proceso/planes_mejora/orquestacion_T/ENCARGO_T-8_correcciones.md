# Encargo: T-8 (protección de entrada y salida, Fase 6) — PASADA DE CORRECCIONES de la segunda auditoría adversarial

T-8 ya está en `origin/main` (`df1b23c`). Un auditor adversarial independiente lo auditó después: veredicto AJUSTADO, 0 BLOQUEANTE,
2 ALTA, 4 MEDIA, 8 BAJA y una observación fuera del diff (M4). Tu trabajo: aplicar TODAS sus correcciones (o refutarlas con
evidencia) en una pasada que entrará en main como UN commit `tesis(T-8): correcciones de la segunda auditoria — <resumen> — <IDs>`.

- Worktree `/home/user/wt/T-8c`, rama `tesis/T-8-correcciones` (desde `df1b23c`). MODO PARALELO: otro agente está integrando T-5
  en main AHORA (toca M8, criterios, CLAUDE.md, generados, línea base) y otros trabajan en `/home/user/wt/T-3`, `T-7a`, `T-9`.
  No toques sus worktrees. **FASE A (ahora)**: correcciones + tests en tu rama, suite verde, push a `origin tesis/T-8-correcciones`.
  **FASE B**: sólo cuando `git fetch origin main` muestre que `origin/main` ya contiene el commit `tesis(T-5)` — si al acabar la
  FASE A todavía no ha entrado, NO integres: termina y repórtalo, y el orquestador te reanuda—. Si ya entró: rebase aplastado sobre
  `origin/main`, ritual entero, `git push origin HEAD:main`.
- Lee primero, enteros: `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (con su ENMIENDA final), `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ENCARGO_T-8.md` (lo que se pidió),
  **`/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/AUDITORIA_T-8_fable.md`** (la auditoría: es tu lista de trabajo; sus scripts están en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-8-aud/`), `CLAUDE.md` ENTERO
  (el párrafo «T-8 de la cadena T» dice qué se hizo y qué se fijó), y las fichas T8-01..06 de `docs/decisiones_diferidas.md`.
- PDF: `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`); verifica TÚ cada cita que toques
  (HEC-14: página impresa y PDF, texto literal). Temporales sólo en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-8c/`.

## Resoluciones del orquestador sobre lo que el auditor deja «para el dueño» (provisionales: mide cada alternativa y repórtala)
a. **H1 — `envolvente_hec14` suprime los avisos de la piedra**: es un defecto, no una decisión. El contraste con HEC-14 (clase de la
   piedra adoptada frente a la Ec. 10.4, «pide un disipador», piso de 2·D50) se hace y se AVISA bajo las dos reglas. La regla
   `regla_espesor_longitud_proteccion_salida` gobierna espesor y longitud, que es lo que su nombre dice; si la envolvente debe
   alcanzar también al TAMAÑO de la piedra es pregunta para el dueño: deja dicho en la ficha qué cubre y qué no, y que la piedra
   la sigue fijando Laushey (el d50 de la línea base no se mueve) con el aviso cuando HEC-14 pide más.
b. **H2 — «sin enrocado» decidido con una velocidad que el propio programa avisa como subestimada** (control de salida con
   TW < y_c: el tirante real es el de borde, HEC-14 núm. 3.1.3, Figs. 3.3–3.4): con una velocidad que es COTA INFERIOR no se puede
   concluir «protección no requerida». En esa condición el contraste con la Tabla Nº 11 NO concluye «no requerida»: lo dice
   («no concluye: la velocidad de salida es cota inferior»), se mantiene la protección y el aviso llega a `avisos()`. Digitalizar
   las Figs. 3.3–3.4 es decisión del dueño (lectura de curvas): NO lo hagas ahora; deja la ficha diferida con lo que haría falta.
   Si el d50 de Laushey en esa condición también es cota inferior, AVÍSALO con la magnitud que el auditor midió, pero **no muevas
   el d50 de la línea base** (0.338 / 0.274 m): si la corrección correcta lo movería, impleméntala como alternativa NO activa por
   defecto y devuelve la pregunta con el antes/después.
c. **H3 — fundamento `F6.FROUDE`**: corrígelo para que diga lo que el paso 6.3 y la fuente dicen (Fr_e es parámetro de diseño; no
   clasifica el régimen; la Tabla 1.1 no lo usa para el apron). Revisa TODOS los fundamentos `F6.*` con el mismo ojo.
d. **Nota (5) b de la Tabla 511-06** (el auditor lo deja como SOSPECHA): relee la tabla y sus notas por imagen y por texto; corrige
   o refuta con el literal. Si la fuente es ambigua, la lectura es `Interpretacion` declarada, del lado seguro.
e. **1.500 vs 1.524 m (nota 8 de la Tabla 1.1)**: lee el literal (¿«5 ft»?, ¿«1.5 m»?, ¿ambos?). El límite se transcribe como la
   fuente lo escribe en SI; si la fuente da las dos cifras, se usa la que hace que su PROPIO ejemplo resuelto (60 in) sea evaluable
   y se declara; el dorado del ejemplo CU vuelve entonces a su escala real (conserva también el escalado como prueba de fórmula).
f. **Desplante a 30 o 360 min** y **«sin enrocado» sin inspección de campo**: preguntas para el dueño; deja la sensibilidad medida
   (profundidad de la hoya con 30 y con 360 min en los puntos del fixture) y el texto del aviso veraz; no cambies el valor de archivo.
g. Lecturas del proyecto impresas como fuente: sepáralas (`fuente` / `Interpretacion` / lo que el proyecto hace).
h. Todas las BAJA, los seis bordes inclusivos sin test, y la observación de M4 fuera del diff: si es un defecto de M4 verificable,
   corrígelo SÓLO si no mueve ningún número de la línea base ni ningún diámetro; si los movería, ficha y pregunta.

## Restricciones
- Tests de cada corrección PRIMERO en rojo (`xfail(strict=True)`), dorados a mano con la aritmética escrita.
- **Nada de la línea base se mueve salvo textos/avisos**: diámetros, materiales, d50 0.338/0.274 m, espesor 0.592/0.479 m, longitud
  5.00 m. Mídelo con el comparador de E-B contra `df1b23c` y dilo. Si un número de cálculo debe moverse para ser correcto: PARA,
  no lo actives por defecto y devuelve la pregunta.
- FASE B (cuando toque): censos sobre el árbol fusionado, generados, línea base regenerada con su README, tracker `.xlsx` (nota en
  INF-3.3.7 / INF-5.1.13 / MAT-X6 con el commit de correcciones), fichas nuevas en la Parte de T-8 de `decisiones_diferidas.md`
  (T8-07…), tabla y párrafo de `CLAUDE.md` (suma de tests, par «sí · no» medido), suite entera verde con y sin `NORMAS_DIR`.

## Entrega
Informe en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-8_correcciones.md` (tabla «hallazgo → corregido / refutado, con evidencia»; preguntas al dueño con su
antes/después) y, como respuesta, un resumen de MENOS DE 350 PALABRAS: qué se corrigió, tests nuevos y par medido (di sobre qué
árbol), números movidos («ninguno» o la lista), SHA y rama (y si entró en main), preguntas para el dueño. No ejecutes ningún otro prompt.
