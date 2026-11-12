# Estado de la cadena T — punto de reanudación (se reescribe en cada guardado)

Para reanudar en una sesión NUEVA: abrir `Proyecto_alcantarillas` (escritura), `Normas` (lectura) y `Cotas-esviaje-alcantarillas`
(lectura; el INFORME está en su rama `claude/serene-mayer-88a2o0`). Leer, en la rama `tesis/orquestacion-estado`, carpeta
`docs/planes_mejora/orquestacion_T/`: este archivo, `ORQUESTACION.md` (convenciones que recibe cada agente; sus rutas de
scratchpad son de la sesión vieja: usar las de la nueva), `NOTAS_ORQUESTADOR.md`, `AUDITORIAS_PENDIENTES.md` y los dos dictámenes.
Entorno: `pip install -r requirements.txt -r requirements-dev.txt openpyxl`; `export NORMAS_DIR=<clon de Normas>`; no hay tkinter
(apt 503): configuración «PyMuPDF sí · Tk no». Suite ~4.5 min.

## Entregado en `origin/main`
- **T-0: `87d1ce7`**. Par con NORMAS_DIR: 4219 passed / 16 skipped / 4235. Diámetros movidos: ninguno.
- **T-2: `ad5cb97`** (hidráulica). Par con NORMAS_DIR: 4390 passed / 16 skipped / 4406 (sin NORMAS_DIR 4383/23). Diámetros movidos: ninguno.
- **T-4: `7fb7926`** (materiales/durabilidad). Par con NORMAS_DIR: 4521 passed / 16 skipped / 4537 (sin NORMAS_DIR 4509/28). Diámetros movidos: ninguno.
- **T-1: `5bca7c6`** (hidrología). Par con NORMAS_DIR: 4712 passed / 16 skipped / 4728 (sin NORMAS_DIR 4694/34). Diámetros movidos: ninguno.
- **T-6: `7e74065`** (geometría; LOTE 1 COMPLETO). Par con NORMAS_DIR: 4850 passed / 16 skipped / 4866 (sin NORMAS_DIR 4832/34). Diámetros movidos: ninguno; L por extremo (+0.9 a +2 %).
- **T-8: `df1b23c`** (protección de entrada y salida; hecho y auditado con Opus; FALTA la auditoría con Fable). Par con NORMAS_DIR: 4960 passed / 16 skipped / 4976 (sin NORMAS_DIR 4942/34). Diámetros y números de Laushey sin mover. Pendiente del dueño: `regla_espesor_longitud_proteccion_salida` (`manual` hoy / `envolvente_hec14`).

## En curso (tercera sesión, reanudada 2026-11-12 15:35 UTC) — ramas en el remoto; NADA de esto en main todavía
| Prompt | Rama | Estado |
|---|---|---|
| T-5 estructural | `tesis/T-5` (`ab7fc3a`, base `7fb7926`) | FASE A hecha con Opus (4632/16/4648 sobre su base). La auditoría Opus de la sesión anterior se PERDIÓ con el corte: relanzada (Opus, esfuerzo extra) → informe en `AUDITORIA_T-5_opus.md` de esta carpeta cuando llegue. Después: correcciones + FASE B sobre `origin/main`. Decisiones a confirmar por el dueño: `fabricacion_tmc` remachada simple; instalación Tipo 3, η 1.05, relleno Cl-95. Falta la auditoría con Fable |
| T-3 Familia C | `tesis/T-3` (desde `df1b23c`) | FASE A lanzada (Opus, esfuerzo extra); encargo: `ENCARGO_COMUN_FASE_A.md` + `PRECISIONES_T-3.md` |
| T-7a cabezal geometría | `tesis/T-7a` (desde `df1b23c`) | FASE A lanzada (Opus, esfuerzo extra); `PRECISIONES_T-7a.md` |
| T-9 espaciamiento | `tesis/T-9` (desde `df1b23c`) | FASE A lanzada (Opus, esfuerzo extra); `PRECISIONES_T-9.md` (+ INF-5.1.8 + aceptación de la Familia B) |

Los agentes empujan WIP a su rama tras cada commit: si hay corte, se retoma desde `origin/tesis/T-n` con el mismo encargo
(«continúa: mira `git log`/`git status` y completa lo que falte»).

Orden de integración (serie; cada uno: rebase sobre origin/main aplastado en UN commit `tesis(T-n): …`, censos, generados, línea
base, tracker, decisiones_diferidas, tabla de CLAUDE.md, suite verde con NORMAS_DIR, `git push origin HEAD:main`):
**T-5 → T-3 → T-9 → T-7a** (T-3 antes que T-7a por `embocadura_cajon`; T-5 antes que T-3 por M8/marco). Después T-7b → T-7c (Fable),
T-10 (Opus) → T-11 (Fable) → T-12 (Opus). Auditorías con Fable pendientes: **T-8** (ya en main: pasada de correcciones), T-5, T-3,
T-9, T-7a. Ningún diámetro del fixture puede moverse (A-01 y A-02 Ø 0.90).

## Aviso de cuota (histórico, 2026-11-12 04:30 UTC; el dato vigente está en USO.md)
Semanal de Fable al 97 % (marca del dueño alcanzada: guardado y prompt entregados); semanal de todos los modelos al 80 %; ambos
reinician el sábado 14 a las 05:00 UTC. El orquestador de la sesión original corre en Fable: una sesión NUEVA debe orquestar con
Opus 5.5 y reservar Fable (desde el sábado) para las auditorías adversariales pendientes (T-8, T-5 y los que se hagan con Opus) y
para T-7b, T-7c y T-11.

## Decisiones del dueño (vigentes)
- T-4 punto 3: OPCIÓN A (`v_max_tmc` [A], 4.572 m/s, ventana 3.048–4.572; dictamen). T-7b punto 1: OPCIÓN (b) LRFD rige + ASD E.050 en paralelo (dictamen).
- Familia B: aceptación «V1+V2+V4+V5+espaciamiento Fase 10» → cablear en T-9. INF-5.1.8 → T-9. Severidades INF- aceptadas como propuestas.
- FEN: se RESTAURA «adoptar el más conservador»; `serie_sin_fen` sólo como contraste (NO_CUMPLE si da menos que la completa).
- `borde_libre_bajo_tw_ahogante` = `no_cumple` (opción a).
- Umbrales electroquímicos de AASHTO LRFD sobre TMC: por analogía, `aviso` por defecto y `excluye` barrible.
- FEN: `serie_sin_fen` con menos lluvia que la completa BLOQUEA el cálculo hidrológico del punto (el Q por columna sólo avisa).
- Pendiente: M7 adopta mínima/máxima sólo sobre la pendiente del cauce y lo dice; V10 juzga las declaradas (decisión del orquestador, comunicada).
- Todo verificado contra el PDF y coherente ingenierilmente (tesis); auditor adversarial antes de cada cierre de prompt de cálculo
  (puede aligerarse en T-10 y T-12 si el dueño lo pide; aún no lo ha pedido).
- Guardar progreso en el remoto con frecuencia.
- **Reparto de modelos (2026-11-12, límite «Semanal · Fable» casi agotado; reinicia sáb 14 05:00 UTC):** lo que no requiere Fable va
  con Opus 5.5 en esfuerzo extra (agentes con `model: opus`, `effort: xhigh`): implementación de T-8, T-5, T-9, T-3, T-7a,
  integraciones, T-10, T-12. Se reserva a Fable: auditorías adversariales de los prompts de cálculo, T-7b, T-7c y T-11.
  Los prompts de cálculo hechos con Opus pasan una auditoría adversarial con Opus antes de integrarse y una segunda con Fable
  cuando haya cuota (pasada de correcciones). Vigilancia: a 96–97 % de Fable guardar y dejar prompt; a 99 % revisar avance.

## Después del lote 1
Lote 2 en paralelo: T-3 (T-2, T-4 y T-6 ya en main: LISTO PARA LANZAR), T-5 (tras T-4), T-7a (T-2 y T-6 ya en main: LISTO PARA LANZAR; longitud entre cabezales, ficha T6-01; socavación de T-8 para el desplante), T-8 (tras T-2; HEC-14: socavación = cap. 5),
T-9 (T-1 ya está en main: LISTO PARA LANZAR con Opus; + Familia B + INF-5.1.8; duración mínima de lluvia y C de pavimento ya resueltos por T-1). Luego T-7b → T-7c, y T-10 → T-11 → T-12.
Resumen al dueño tras cada prompt: IDs (entero / en parte / no), tests nuevos, números movidos y por qué, diferidos, SHA.
