# Backlog ejecutable — orden, dependencias, modelo y esfuerzo

**Sustituye a:** `05_BACKLOG_EJECUTABLE.md`.
Los prompts completos viven en los planes G/R/I/T; aquí está el orden, qué
depende de qué, y con qué modelo y esfuerzo abrir cada sesión (misma
convención que la tabla §10 de `docs/hoja_de_ruta_correcciones_v12.md`).
Desaparecieron las fases F0–F6 del backlog original: su Fase 0 (inventario)
ya existe como código ejecutable, su Fase 1 (esquema de ficha) se descartó
con razones en `00_LEEME_DICTAMEN.md` §3, y sus ~38 sesiones quedan en
**12 (9 núcleo + 3 opcionales)**.

## Orden recomendado

| # | Sesión | Plan | Depende de | Modelo | Esfuerzo | Plan mode | Por qué este orden |
|---|---|---|---|---|---|---|---|
| 1 | **G4** · Traza «¿de dónde sale este número?» | G | — | Opus 5 | high | sí | La mejora de mayor valor; el dato ya existe; no toca cálculo |
| 2 | **R1** · Linter de estilo con trinquete | R | — | Sonnet 5 | high | no | Mecánico de amplitud; produce el censo que prioriza R2 |
| 3 | **G1** · Pestaña 1 agrupada + lenguaje | G | — | Opus 5 | high | sí | Lo que más confunde a terceros hoy |
| 4 | **I1** · Los 6 «Cerrado parcial» | I | — | Opus 5 | high | sí | Toca tracker y conflictos; cuanto antes, menos deriva |
| 5 | **R2a/R2b** · Reescritura por lotes (2 sesiones) | R | R1 | Opus 5 | high | no | Juicio de redacción sobre 69 textos; valor congelado |
| 6 | **T2** · Trinquetes del registro | T | — | Opus 5 | high | no | Baja deuda medible; alimenta a I2 (citas de partes) |
| 7 | **I2** · Discrepancias vivas | I | mejor tras T2 | **Fable 5** | high | sí | Toca la v8 y la jerarquía de fuentes: la sesión más delicada |
| 8 | **G3** · Anticipo pre-corrida | G | mejor tras G1 | Opus 5 | high | sí | Reusa la maquinaria de familias de G1 |
| 9 | **I3** · Residuos Familia C | I | I2 (protocolo v8) | Opus 5 | high | sí | Cierra la bitácora de la ruta C |
| 10 | **R3** · Nota 1 de F_pga | R | R1 | Fable 5 | high | sí | Posible reetiquetado: juicio normativo fino |
| 11 | **G2** · Filtro por fase | G | — | Sonnet 5 | medium | no | Pequeña y autocontenida |
| 12 | **G5** · Ayuda de conceptos | G | G1–G4 | Sonnet 5 | high | no | Cierra la cara de usuario; incluye el guion de prueba humana |
| op | **T1** · Vigencia de ediciones | T | — | Sonnet 5 | medium | no | Necesita red; independiente de todo |
| op | **I4** · Índice de fórmulas + dimensional piloto | I | — | Opus 5 | high | no | Guardias nuevas; solo si el núcleo está cerrado |
| op | **T3** · Export CSV del registro | T | — | Sonnet 5 | medium | no | Comodidad para revisor externo |

Reglas de la tabla, heredadas de la casa:

- **Una sesión = un prompt.** Mezclar dos en el mismo hilo genera cambios sin
  declarar — tu regla original, y es correcta.
- **No cambies el esfuerzo a mitad de sesión** (rompe la caché del contexto).
- **Plan mode «sí»** marca las sesiones que rozan conflictos vinculantes, la
  hoja de ruta v8 o el motor validado: ahí el plan es donde se detecta la
  corrección ingenua antes de escribirla.
- Ninguna sesión abre dependencias nuevas sin consultar; `openpyxl` está
  preautorizado solo para el tracker.

## Ritual de cierre (ya embebido en cada prompt; aquí como recordatorio)

1. Suite completa en verde ANTES de commit (regla dura: no hay commit en rojo).
2. Commit con el prefijo de la serie y el id (`GUI(G1): …`, `criterios(R2a): …`,
   `cierre(I1): …`, `trazabilidad(T2): …`).
3. Entrega en `origin/main` — una rama empujada no es una entrega.
4. Conteo reportado como **par** `passed + skipped = collected`, leído desde
   `origin/main`, diciendo el entorno (PyMuPDF sí/no, Tk sí/no). Última
   referencia documentada: 1800 recolectados (tabla de 4 configuraciones en
   `CLAUDE.md`); si tu sesión añade tests, la tabla de `CLAUDE.md` se
   actualiza en el mismo commit.
5. Si algo quedó sin fusionar (permiso, conflicto), se reporta rama + SHA
   explícitamente: no se da por entregado.

## Qué pasó con los tickets de tu backlog original

| Tuyo | Destino |
|---|---|
| F0-01..F0-05 (inventario, fichas de familia, vigencia) | F0-04 sobrevive como **T1**; el resto ya existe como código ejecutable (censo, ayuda derivada, manifiesto generado) |
| F1-01..F1-06 (esquema de ficha y migración) | **Descartado** — dictamen §3: el esquema real ya cubre; el problema era de redacción → R1/R2 |
| F2-01..F2-10 (GUI) | F2-02/07 → **G1** · F2-05 → **G2** (recortado: familia diferida con razón) · F2-06 → **G3** (corregido: informativo) · F2-09 → **G4** · F2-08 → **G5** · F2-01/03/04 ya existen (S21/S22) · F2-10 (prueba humana) → dentro de **G5** |
| F3-01..F3-12 (auditoría ingenieril) | F3-02/03 (V4b) **descartado** — resuelto en S14 por el conflicto #1 · F3-06 (`LimiteVelocidad`) **descartado** — símbolo retirado con guardia · F3-04/07 → **I4** en versión generada/piloto · F3-12 → **I1** con el pendiente real (6 parciales, no 48+8) · el grafo de dependencias queda como está (`_consumo_por_modulo` es estimación declarada y no debe gobernar nada) |
| F4-01..F4-07 (criterios) | F4-02 → **R1** · F4-03/04/05 → **R2a/R2b** (por nivel, no por fase) · F4-06 (ADRs) **descartado** → `decisiones_diferidas.md` · F4-01 lo produce el propio censo de R1 |
| F5-01..F5-06 (trazabilidad) | F5-01/02 ya existen (tablas completas + `PendienteDeCondicion`) · F5-03/06 → **T3** · F5-04 ya existe (63 tests del registro) · F5-05 → nota en §abajo |
| F6-01..F6-03 (cierre) | Sin campos viejos que retirar (no hubo migración); la corrida por familia extremo a extremo ya la fija `tests/test_linea_base.py` + `test_cierre_perfil.py` |

## Una nota sobre «mapa para revisores» (tu F5-05)

Tu idea de una sección de entrada para revisores externos es buena y barata,
pero su lugar no es `CLAUDE.md` (que ya es larga y es la constitución para
agentes, no para revisores). Si la quieres, pídela como micro-sesión: un
`docs/para_revisores.md` de una página que solo enlace — taxonomía (en
`CLAUDE.md`), manifiesto generado, decisiones diferidas, tracker — sin
duplicar una línea de contenido, con un test de que los enlaces apuntan a
archivos existentes. Cualquier cosa más grande duplicaría y divergiría.

## Añadido en la sesión de orden previa a N1 (pre-N1): las dos sesiones de norma y el orden de lo que queda

Cuando se escribió este backlog las dos fuentes ausentes más valiosas seguían
ausentes. El dueño consiguió las dos, y sus prompts viven junto a estos planes:
`prompt_N1_A796.md` (ASTM A796/A796M-13) y `prompt_N2_M294.md` (AASHTO M 294-11,
traducción no oficial). Los dos PDF están ya en `normas/` con el nombre exacto
que cada prompt cita, **sin registrar todavía**: registrarlos ES la tarea de N1
y de N2. Mientras tanto `FUENTES_AUSENTES` los sigue censando como ausentes,
con una `paginacion=SinDeterminar` cuya razón («la fuente no está en normas/»)
ya no es literal. Ningún test enumera el directorio, así que la suite no lo
nota; N1 y N2 lo vuelven a dejar cierto. Es el estado transitorio que los dos
prompts dan por prerrequisito.

Las doce sesiones del núcleo (1 a 12) están entregadas en `origin/main`, más
un R3b que R3 dejó como cola. El orden de lo que queda, decidido en pre-N1:

| # | Sesión | Depende de | Modelo | Esfuerzo | Plan mode | Por qué este orden |
|---|---|---|---|---|---|---|
| 13 | **N1** · ASTM A796/A796M-13 al registro | PDF en `normas/` (hecho en pre-N1) | Fable 5 | high | sí | Cierra trabajo real del tracker: la mitad (2) de NOR-PRO-04, `DIS-HR-A807` (abierta contra la v8) y la mitad TMC de `clases_producto_por_relleno`. Los tres opcionales no cierran nada del tracker |
| 14 | **N2** · AASHTO M 294-11 (traducción no oficial) | N1, en sesión aparte | Fable 5 | high | sí | Respalda `D_max_catalogo['hdpe']` y mueve SIS-F-13; su propio prompt exige correr después de N1 |
| 15 | **T1** · Vigencia de ediciones | N1 y N2 | Sonnet 5 | medium | no | Verifica vigencia por fuente PRESENTE: tras N1 y N2 son 15 y no 13, y las dos nuevas son ediciones superadas (2013 y 2011), exactamente el caso que T1 modela. Correrla antes dejaría fuera las dos fuentes más delicadas |
| 16 | **I4** · Índice de fórmulas + dimensional piloto | núcleo cerrado | Opus 5 | high | no | Independiente de las fuentes; el plan lo condiciona a que el núcleo esté cerrado, y el núcleo incluye los dos parciales que N1 y N2 mueven |
| 17 | **T3** · Export CSV del registro | todo lo anterior | Sonnet 5 | medium | no | Se genera del registro: va al final para que salga completo y no haya que regenerarlo dos veces |

Dos avisos para las sesiones N, medidos en pre-N1:

- El censo de ausentes registra `ASTM_A796` con año 2019 y el ejemplar es la
  edición 2013; el prompt ya manda registrar la que ES. Las cifras del ejemplar
  que el prompt da (21 páginas, primera en blanco, SHA-1, capa de texto
  duplicada) se comprobaron sobre el archivo que quedó en `normas/`. Las de
  M 294 (17 páginas, texto extraíble, SHA-1) también.
- El caso patrón de M2 que N2 evalúa necesita además las Tablas 1 a 5 de
  M 170M, que según la ficha de SIS-F-13 en el tracker siguen sin transcribir.
  Lo probable es que M2 quede censado con esa razón y no ya con la ausencia de
  M 294; el prompt dice «evalúa», y eso es lo que hay que evaluar.

La regla no cambia: una sesión = un prompt, y la tabla de entornos de
`CLAUDE.md` se vuelve a medir en las cuatro configuraciones cada vez que el
conteo se mueve. Pre-N1 la encontró seis sesiones atrasada y la re-midió.
