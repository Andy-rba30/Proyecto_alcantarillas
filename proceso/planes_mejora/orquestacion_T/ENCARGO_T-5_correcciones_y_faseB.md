# Encargo: T-5 (estructural del conducto, Fase 8 real) — CORRECCIONES DE AUDITORÍA + FASE B (integrar en main)

Worktree `/home/user/wt/T-5`, rama `tesis/T-5`, HEAD `ab7fc3a` (FASE A de otro agente; base `7fb7926`). Respaldo: `origin/tesis/T-5-faseA`
(= `ab7fc3a`, no lo toques). `origin/main` = `df1b23c` (T-1, T-6 y T-8 entraron después de tu base). Otros agentes trabajan en
`/home/user/wt/T-3`, `T-7a`, `T-9` (FASE A, no integran hasta que tú termines) y un auditor lee `/home/user/wt/main`: no los toques.

## Lee primero (entero)
1. `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (convenciones + ENMIENDA del final: base, rutas, guardado con push, FASE B con `git push origin HEAD:main`, informe).
2. `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ENCARGO_T-5.md` (lo que se pidió en FASE A, con las precisiones) y el bloque T-5 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`.
3. LAS DOS AUDITORÍAS ADVERSARIALES, completas: `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/AUDITORIA_T-5_fable.md` y `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/AUDITORIA_T-5_opus.md` (scripts y salidas de los
   auditores en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud-fable/` y `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud/`).
4. `CLAUDE.md` ENTERO del worktree (y, tras el rebase, los párrafos de T-1, T-6 y T-8, que traen lecciones de integración).

## Parte 1 — Correcciones
Cada hallazgo de las dos auditorías (todas las severidades): lo CORRIGES, o lo REFUTAS con evidencia escrita (página y texto literal,
o comando y salida). Ninguno se queda sin respuesta. Sugerencia de orden: rebasa primero sobre `origin/main` (resolviendo conflictos
y censos) y corrige sobre el árbol fusionado, con commits `wip(T-5)` y `git push --force-with-lease origin tesis/T-5` tras cada bloque
verde (puede haber cortes por límite de uso: el mensaje del commit dice qué falta). Tests de cada corrección PRIMERO en rojo.

Resoluciones del orquestador sobre los puntos que los auditores dejan «para el dueño» (aplícalas; son provisionales y se le
presentan al dueño en tu informe con el antes/después, así que mide cada alternativa):

a. **Camión vs tándem (Fable H1)**: se elige por EFECTO (la carga lineal / D-load / empuje que gobierna), no por presión. Dorado a
   mano independiente del código (el test actual copia la regla del código: reescríbelo). Declara lo que se mueve (`F8.CLASE` de
   A-01 y A-02 y lo que cuelgue). Si con la corrección el concreto Ø 0.90 Clase II dejara de cumplir en A-01/A-02 → PARADA (c).
b. **Carga viva sobre 8 ft (Fable H2)**: la fuente PERMITE despreciarla («may be neglected», verifica numeral y condición completa:
   también «exceeds the span»). Un permiso no se usa en silencio: criterio [A] categórico de dos valores, valor de archivo
   **conservarla** (lado seguro), «despreciar según la fuente» como alternativa barrible con su cita; el paso dice cuál aplicó.
   El relleno máximo cambia (≈3.18 → ≈2.85 m): decláralo.
c. **Tipo de instalación del concreto (Opus H2)**: la ventana admite `tipo_4` (diseñar como Tipo 4 es siempre válido y más
   desfavorable). El valor de archivo sale de la regla de la cadena —«el más desfavorable que EG-2013 admita»— leída contra el
   texto LITERAL de EG-2013 505–508 (compactación y cama exigidas): si lo que EG-2013 EXIGE corresponde a un Tipo 3 o mejor de la
   Tabla 12.10.2.1-1, queda Tipo 3 con la justificación CORRECTA (no «el más desfavorable» a secas: «la instalación que EG-2013
   exige, leída como Tipo 3; el Tipo 4 es la cota conservadora, barrible»), y la `Interpretacion` impresa; si EG-2013 no lo
   sostiene, Tipo 4. Informa relleno máximo y clase con ambos.
d. **HDPE (Opus H1, Fable H3)**: la fuente dice que los mínimos de la Tabla A12-11 no son para diseño (verifica C12.12.3.2 literal).
   Las propiedades de sección del perfil son DATO DEL FABRICANTE: entrada opcional sin valor por defecto. Sin ellas, la verificación
   corre con el mínimo de la tabla como COTA INFERIOR declarada y lo dice en el paso, en los avisos del punto y en la ficha del
   criterio (que hoy sólo lo dice de A-01): «con el perfil mínimo no cumple; no es un veredicto sobre un producto real». Relleno
   por defecto del HDPE: lo que EG-2013 508.02 (literal, con su carácter) exija para la zona de la tubería; si exige material
   granular, el valor de archivo para el HDPE debe ser coherente con esa exigencia y citarla (no `Cl-95` por inercia). Pandeo con
   el módulo que 12.12.3.3 manda para cada carga; añade el factor de flexibilidad del termoplástico (verifica numeral y límite).
   RESTRICCIÓN: si con esto el HDPE pasa a cumplir y DESPLAZA a un material adoptado en la línea base o en un test que fija
   material/diámetro → PARADA (c): deja por defecto lo que no mueve nada y devuelve la pregunta.
e. **`fabricacion_tmc` y el caso G2 de T-4 (Opus H3, Fable media)**: RESTAURA el test de T-4 tal como está en `origin/main` (no se
   edita un test que fija un dimensionado para que pase). Elige el valor de archivo con la fuente (EG-2013 507.02 literal: qué
   fabricación describe; tablas de costura de A796 / M 36, que el auditor Fable NO releyó: reléelas tú valor a valor). Si el
   valor que la fuente sostiene (o el más desfavorable admisible) hace que ese TMC Ø 1.95 deje de dimensionar → PARADA (c): valor
   de archivo = el que NO lo mueve, el otro como alternativa barrible, y la pregunta al dueño con el antes/después. Costura
   empernada sin tabla → vacío declarado con lo que lo destraba.
f. **η = 1.05**: verifica 12.5.4 y 1.3.x literales; si la fuente lo PRESCRIBE para el relleno sobre estructuras enterradas no es
   una elección [A]: etiqueta y cita lo que corresponda.
g. **Clases de M 170M ilegibles**: los dos auditores confirman que sólo la Clase II se puede leer. Sigue siendo un vacío declarado
   (lo destraba un ejemplar legible de M 170M / ASTM C76: va a la lista del dueño), pero (i) la tabla de clases debe saber en qué
   DIÁMETROS tabula la norma cada clase, para que completarla no elija una clase que no existe para ese diámetro (Opus: Ø 0.90
   «Clase I»); (ii) el mensaje del bloqueo cuando se pide más que la Clase II dice exactamente qué falta; (iii) corrige el
   docstring «subir de diámetro no lo resuelve».
h. Todos los MEDIA y BAJA restantes, y tests para los mutantes vivos que importan (relleno máximo de TMC y HDPE, rama del nivel
   freático, deflexión admisible, muestreo del «primer cruce»).

## Parte 2 — FASE B (integrar en main), con el ritual entero de ORQUESTACION.md y de CLAUDE.md
- Rebase aplastado en UN commit `tesis(T-5): <resumen> — <IDs canónicos>` sobre `origin/main` (ID canónico: `INF-3.3.5`, más las
  filas `INF-3.3.k` que T-0 te asigna; NO `INF-5.1.5`, que es de T-7b). Pie del commit: el de ORQUESTACION.md.
- Censos sobre el árbol fusionado (criterios: 102 en main + los tuyos; `CLAVES_EXTERNAS`; `dominios.py` y demás marcas de
  `test_sin_literales`; `test_ext5_forma_gui`, `test_criterios_adoptados`, `test_cierre_perfil`, `test_nivel_medido`,
  `test_memoria_sustentada`, techos de `test_ext8` REMEDIDOS, `LO_QUE_ESCRIBIO_CADA_PROMPT` con tu fila); Parte nueva de
  `docs/decisiones_diferidas.md` (la XLV es de T-8: la tuya es la XLVI) con sus anclajes; v8 enmendada donde discrepe.
- Tracker `.xlsx` (openpyxl, sobre el de `origin/main`): estado, «Claude Code (cadena T, T-5)», commit. Los cuatro documentos
  generados y la línea base de la Familia C regenerados sobre el árbol final; README de la línea base con cada diferencia clasificada.
- **PARADA (c)**: mide con el comparador de E-B contra `df1b23c` los doce pares punto × corrida: material, sección, veredictos,
  admisibles y tipo de bloqueo idénticos salvo lo que T-5 declara (verificaciones `F8.*` nuevas, avisos, criterios usados,
  huellas, recuentos). A-01 y A-02 siguen en concreto Ø 0.90. Si algo más se mueve, NO empujes a main: guarda en tu rama y repórtalo.
- `CLAUDE.md`: párrafo «T-5 de la cadena T» al estilo de los de T-8/T-6, la tabla de pares («sí · no» MEDIDO con `NORMAS_DIR`;
  las otras tres DERIVADAS, dicho así), el invariante `collected`, la cadena de totales y el conteo de criterios en todos los
  sitios donde aparece.
- Suite ENTERA verde con `NORMAS_DIR=/home/user/andy-rba30/normas` (mídela también sin él); `git push origin HEAD:main`;
  `git fetch origin main`; confirma `origin/main == HEAD`; deja `tesis/T-5` empujada en ese commit.

## Entrega
Informe completo en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/INFORME_T-5_final.md` (formato de ORQUESTACION.md + tabla «hallazgo → corregido / refutado, con evidencia» +
las preguntas para el dueño con antes/después: instalación, HDPE, `fabricacion_tmc`/G2, carga viva sobre 8 ft, η, ejemplar legible de
M 170M). Como respuesta, un resumen de MENOS DE 400 PALABRAS: IDs (entero / en parte / no), tests nuevos y par medido, números movidos
y por qué, «diámetros movidos: ninguno» o la lista, diferidos, SHA en `origin/main`, preguntas para el dueño. No ejecutes ningún
otro prompt. No reportes como hecho lo que no verificaste.
