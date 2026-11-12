# Encargo: AUDITORÍA ADVERSARIAL de T-9 (espaciamiento de alivios con L hidráulico calculado, Fase 10) — FASE A, antes de integrar

Eres el auditor adversarial. SOLO LECTURA: no edites ni hagas commits. Intenta REFUTAR el trabajo de otro agente (otro modelo) antes
de que entre en `main`. Es para una tesis de ingeniería: todo verificado contra el PDF de la norma y coherente ingenierilmente.

- Worktree a auditar: `/home/user/wt/T-9` (rama `tesis/T-9`, HEAD `304cea6`). Diff: `git diff df1b23c 304cea6`. Base = `origin/main`.
- Lee primero: `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (convenciones, reglas no negociables, lecciones; con su ENMIENDA final),
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/PRECISIONES_T-9.md` (lo que se le pidió además del bloque T-9 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`) y
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-9_faseA.md` (lo que el implementador dice que hizo: NO lo des por bueno). De `CLAUDE.md`: «Fuente de verdad»,
  «Taxonomía», «Arquitectura» (en especial la regla de T-1: `MH_hidrologia` sólo lo importa `servicio.py`; puerta FEN), «Nivel de
  entrega», «Excepciones».
- PDF: `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`). Página escaneada o tabla como
  figura → renderízala a PNG en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-9-aud/` y léela con Read. Temporales sólo ahí. Mutantes: `tests/apoyo/mutacion.py` o una copia
  del árbol; para medir contra la base, `git worktree add --detach /tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-9-aud/base df1b23c` (quítalo al terminar). No corras la
  suite entera más de una vez (4 CPU compartidas con otros agentes).

## Qué comprobar (como mínimo)
1. **Cada cita y cada número contra el PDF del manual MTC** (numeral, título, página impresa y PDF, texto literal y su CARÁCTER:
   ¿exige, recomienda o describe?): núm. 4.1.2.1 de cunetas; longitud máxima de tramo (250 m / 200 m: ¿para qué condición cada
   una?); las Tablas que el implementador llama 32, 33 y 34 (TODAS las celdas: coeficientes de Manning de cunetas, velocidades
   límite por revestimiento, dimensiones mínimas por región); la «ec. 117» de Manning; la fila de periodo de retorno / riesgo que
   da «35 años» (¿la fila es la de cunetas?, ¿el manual da TR o riesgo y vida útil?, ¿quién lo calcula?); DG-2018 si se cita.
2. **Coherencia ingenieril, con un caso A MANO** (aritmética escrita, independiente del código): capacidad de una cuneta triangular
   por Manning con las unidades correctas; caudal por metro «q·b/10⁶» (¿qué es q, en qué unidades, de dónde sale el 10⁶?); L
   hidráulico = capacidad / caudal por metro: ¿es dimensionalmente correcto y del lado seguro (tc de la cuneta sin iterar, ficha
   T9-02: ¿sub o sobreestima la longitud?)?; el criterio por velocidad límite: ¿una cuneta que supera la velocidad admisible acorta
   el tramo o exige otro revestimiento? ¿se usa la velocidad MÍNIMA (sedimentación) en algún sitio?; «lectura_velocidad_limite_cuneta
   = extremo inferior»: ¿es el lado seguro?
3. **INF-5.1.8 — `area_ha` con «consumidor real»**: el implementador hace q = Q / `area_ha` cuando el Q es declarado. ¿Eso es un
   consumidor legítimo (la escorrentía específica de la cuenca del alivio aplicada a la franja de la cuneta) o un uso forzado para
   no quitar la columna? ¿Las unidades cierran? ¿Qué pasa si `area_ha` es la cuenca natural y no la plataforma?
4. **Aceptación de la Familia B** = («V1», «V2», «V4», «V5», «VB1»): dice que «sigue sin filtrar nada» y que un test por AST fija
   que ningún módulo lee el campo. ¿Entonces el cableado es real o decorativo? ¿Qué pidió el dueño (v8 §2.3, ficha T0-03)? Mide
   B-01 en todas las corridas de la línea base y de `docs/guia_perfil.md` frente a `df1b23c`: «diámetros movidos: ninguno» o la lista.
5. **VB1 puede fallar de verdad** y no falla en falso: tramo de 250 m, obra B única sin extremo («no se evaluó»: ¿aviso o bloqueo?,
   ¿cuenta en `cerrado`?), dos obras B en orden inverso de progresiva, progresivas iguales, `inicio_tramo_cuneta_km` posterior a
   la obra, valores negativos/NaN/cadena en los tres datos externos nuevos, `S_cuneta` = 0 o negativa, `seccion_cuneta` sin valor
   (¿`CriterioPendienteError` como bloqueo del punto, dentro de `_etapa`?). Sólo `ErrorProyecto`; nunca corrida caída.
6. **Nada inventado ni relleno silencioso**: cada criterio nuevo (`seccion_cuneta` sin valor con ventana, `revestimiento_cuneta` =
   concreto, `lectura_velocidad_limite_cuneta`, el campo de borde libre 0–0.10 m): ¿la ventana y la justificación son de la fuente
   o del implementador? ¿`revestimiento_cuneta = concreto` por defecto es una elección no conservadora que debería quedar sin valor?
   ¿El pre-vuelo (`anticipo.datos_faltantes_por_punto`) sigue diciendo la verdad? ¿El «nivel» de los criterios nuevos lo mide una corrida?
7. **Arquitectura**: M10 no importa MH (AST); ninguna lluvia de diseño sin pasar por la puerta FEN; M11 sin aritmética; avisos por
   `InformePunto.avisos()` (CLI, JSON, memoria); fuente / interpretación / lo-que-el-proyecto-hace separados.
8. **Tests y mutación**: dorados a mano o copia de la fórmula; tests vacuos; corre el arnés de mutación sobre las funciones nuevas
   de M10 (el implementador NO lo hizo) acotado a ~20 min y lista los mutantes vivos que importan.
9. Las cuatro «preguntas para el dueño» del informe: da tu recomendación fundada en la fuente para cada una.

## Entrega
Informe en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/AUDITORIA_T-9_fable.md`: veredicto (APROBADO / AJUSTADO / RECHAZADO), hallazgos numerados H1… con severidad
(BLOQUEANTE / ALTA / MEDIA / BAJA), evidencia reproducible (comando y salida, o página y texto literal) y la corrección concreta
anclada por símbolo; separa «refutado con evidencia» de «sospecha»; lista aparte las decisiones del dueño con tu recomendación.
Devuélveme un resumen de menos de 300 palabras: veredicto, hallazgos por severidad, los tres más graves, «diámetros movidos»,
decisiones para el dueño.
