# Encargo: AUDITORÍA ADVERSARIAL de T-11 (validación integral de las tres familias) — FASE A, antes de integrar (quinta sesión)

Eres el auditor adversarial. SOLO LECTURA: no edites archivos del repositorio ni hagas commits. Intenta REFUTAR el trabajo de otro
agente antes de que entre en `main`. Es para una tesis de ingeniería: todo verificado contra el PDF de la norma y coherente
ingenierilmente. T-11 VALIDA y NO cambia cálculo; tu foco son los **JUICIOS DE VALIDACIÓN**: qué se compara con qué, por qué un
punto llega o no llega a la Fase 11, si la lista de entradas y el censo dicen la verdad, si la sensibilidad mide lo que dice medir.

- Worktree a auditar: `/home/user/wt/T-11` (rama `tesis/T-11`, HEAD que te da el orquestador). Diff: `git diff 14f6138 HEAD`.
  Base = `origin/main` = `14f6138` (par con `NORMAS_DIR`: 6337 / 23 / 6360).
- `ORQ` = `/home/user/wt/estado/docs/planes_mejora/orquestacion_T/`; `SP` =
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/7cb96d40-c574-5ae4-841a-e8d6d2b9b04b/scratchpad/` (temporales sólo en
  `SP/T-11-aud/`; para medir contra la base: `git -C /home/user/wt/T-11 worktree add --detach SP/T-11-aud/base 14f6138`, y quítalo al
  terminar).
- Lee primero: `ORQ/ORQUESTACION.md` (con su ENMIENDA DE LA QUINTA SESIÓN), `ORQ/PRECISIONES_T-11.md` (lo que se pidió además del
  bloque T-11 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`), la sección «Cuarta sesión» de `ORQ/DECISIONES_DUENO_2026-11-12.md`
  (decisiones del dueño: no las reabras, pero sí di si el trabajo las respeta) y `SP/INFORME_T-11_faseA.md` (lo que el implementador
  dice que hizo: NO lo des por bueno). De `CLAUDE.md`: «Fuente de verdad», «Taxonomía», «Arquitectura», «Nivel de entrega»,
  «Excepciones».
- PDF: `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`). Página escaneada o tabla como
  figura → renderízala a PNG en `SP/T-11-aud/` y léela con Read. No corras la suite entera (el implementador la midió y la
  integración la remide): tests afectados y comandos puntuales.

## Qué comprobar (como mínimo)
1. **Punto 1 — corrida de punta a punta.** Reproduce la corrida completa y la corrida por defecto con las puertas de la CLI. ¿Las
   tres familias llegan a la Fase 11 con diseño, o el bloqueo que queda es una ENTRADA que el juego deja fuera A PROPÓSITO (y lo
   dice)? ¿Algún valor de prueba entró por la puerta de atrás (`criterios_adoptados.py`, `datos_sitio.py`,
   `constantes_normativas.py`, un monkeypatch, un default silencioso)? ¿Cada archivo del juego lleva la cabecera «DATOS DE PRUEBA, NO
   DEL PROYECTO» y cada valor nuevo una línea de plausibilidad (orden de magnitud) sin presentarse como dato del sitio? ¿Hay
   `NotImplementedError` / `AssertionError` / excepción fuera de `ErrorProyecto` en alguna de las dos corridas o en las variantes
   «una entrada quitada a la vez»? ¿La LISTA EXACTA de entradas del proyecto coincide, ítem por ítem, con `docs/contrato_entradas.md`
   y con lo que la corrida por defecto REALMENTE pide (bloqueos medidos), sin faltas ni sobras? ¿Los casos que el dueño dejó a
   propósito (B-01 con TW = 1.00 m no dimensiona por V2; VB1 de B-01 a 530 m; el cabezal de la regla que no pasa E3 estático ni E1
   sísmico) se presentan como RESULTADO honesto, con su sensibilidad, y no se esconden?
2. **Punto 2 — validación externa.** `docs/validacion_hds5.md`: ¿se GENERA desde los mismos casos de `CP_HDS5_DG1` con test de
   sincronía? ¿La tolerancia de lectura y las casillas fuera están censadas con su causa? Comprueba contra el PDF de HDS-5 (página
   impresa y PDF) al menos tres filas del ejemplo publicado y dos casillas «fuera». Si se añadieron ejemplos de HEC-14 (apron y
   socavación), verifica sus cifras contra su página. `docs/validacion_hy8.md`: ¿el procedimiento es ejecutable por el autor
   (entradas por punto, salida a comparar, tolerancia) y no afirma ningún resultado de HY-8?
3. **Punto 3 — sensibilidad.** ¿El anexo se genera con script y test de sincronía (o huella)? ¿Cada barrido declara UNA clave a la
   vez por la puerta de PF-3 (`barrido.verificar_valores`, la misma ventana)? ¿Los valores barridos están DENTRO de la ventana de
   cada [A]? ¿La conclusión «mueve / no mueve un diámetro o un veredicto» es la que la tabla del barrido sostiene? Reproduce dos
   barridos que el informe dice que SÍ mueven algo y uno que dice que NO. ¿Falta algún [A] que gobierne el diámetro o el cabezal
   (los que nombran el prompt y PRECISIONES, y los que tú midas: `regimen_v2b`, `hw_entrada_fuera_de_rango`, `n_manning_cajon`, η del
   cruce, `fila_phi_estabilidad_cabezal`, `factores_inclinacion_carga_portante`, `regla_pendiente_relleno_trasdos`,
   `regimen_resistencia_elementos_cabezal`, `gamma_EQ`, `fraccion_delta_sobre_phi_trasdos`, `factor_muro_eleccion`)?
4. **Punto 4 — censo final.** ¿Es verdad lo que dice de: criterios de perfil sin valor (y la entrada que destraba cada uno),
   `M9.FUNCIONES_SIN_CONSUMIDOR`, `SIN_CONSUMIDOR_Y_SIN_MEDIDA`, `AssertionError("inalcanzable")` en M8/M9, filas `INF-` no cerradas
   (incluidas INF-5.1.3, INF-5.1.8, INF-5.1.9, INF-5.1.16: compara con el tracker leído por `tests/apoyo/tracker.py`)? ¿El
   alcance declarado (armado del marco de la Familia C, cabezal paralelo a la vía, iteración de zapata, V7 del marco sin peso
   propio, Figuras 3.3–3.4 de HEC-14, `max(V_c, V_erosion)` en M4, escalón T7V-01) aparece en `docs/decisiones_diferidas.md` y en
   `modelos.ALCANCE_DECLARADO` sin duplicar lo que T-10 ya puso? ¿La tercera corrida de referencia (con hidrología de prueba) hace
   que la Fase 1-bis entre de verdad al índice de fórmulas?
5. **No cambia cálculo.** Compara la línea base (`tests/linea_base_familia_c/`) y la salida de `cli.py` sobre el fixture contra la
   base `14f6138` (comparador de E-B): «diámetros/secciones/materiales/HW movidos: ninguno», o la lista. Revisa el diff de `src/`:
   cada cambio ¿es plomería declarada con test, o es cálculo disfrazado?
6. **Defectos destapados.** Para cada `xfail(strict=True)` que el implementador dejó: ¿reproduce un defecto real, con evidencia, o
   es un falso positivo? ¿Hay defectos de cálculo, fórmula o cita que la validación destapa y el implementador NO vio? Para cada
   defecto de fórmula o cita, da la corrección concreta con la página y el texto literal (la corregirá un agente aparte).
7. **Tests**: dorados independientes del código, tests vacuos, tests que pasarían con el defecto. Mutación acotada (≤ 20 min,
   `tests/apoyo/mutacion.py`) sólo si hay lógica nueva en `src/` o en los juicios del apoyo.

## Entrega
Informe en `SP/AUDITORIA_T-11.md`: veredicto (APROBADO / AJUSTADO / RECHAZADO), hallazgos numerados H1… con severidad
(BLOQUEANTE / ALTA / MEDIA / BAJA), cada uno marcado como **[FÓRMULA/CITA]** (lo corrige Fable) o **[RESTO]** (lo corrige Opus),
evidencia reproducible (comando y salida, o página y texto literal) y la corrección concreta anclada por símbolo; separa «refutado con
evidencia» de «sospecha»; lista aparte las preguntas para el dueño con tu recomendación. Si no puedes escribir archivos, devuelve el
informe entero en tu respuesta. Respuesta: resumen de menos de 300 palabras con veredicto, hallazgos por severidad y por tipo, los
tres más graves, «diámetros movidos», preguntas para el dueño.
