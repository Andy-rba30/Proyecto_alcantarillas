# Uso de la sesión orquestadora (modelo claude-fable-5-2) — libro de consumo

Fuente: `get_session` de la sesión (campo `usage` y `rate_limit_info`). El costo es el EQUIVALENTE a precio de API que reporta
la plataforma para toda la sesión (orquestador + subagentes); no es necesariamente lo que se descuenta de un plan.

| Momento (UTC) | Hito | cost_usd acumulado | output tokens | cache read | Límite |
|---|---|---|---|---|---|
| 2026-11-12 00:04 | T-0 y T-2 en main; T-1, T-4, T-6 auditados y corregidos; T-4 integrando; T-8 arrancando | 446.56 | 2.69 M | 822 M | `seven_day_overage_included`: **allowed_warning**; reinicio 2026-11-14 05:00 UTC |

Referencias para estimar: T-0 ≈ 0.74 M tokens de subagente; cada prompt de cálculo ≈ 0.5–0.9 M (implementación) + 0.3–0.4 M (auditoría)
+ 0.3–0.7 M (correcciones e integración). Avance al primer registro ≈ 35 % de la cadena.

## Utilización de los límites (evento `rate_limit_event` de la sesión; campo `unifiedWindows`)

Regla del dueño (2026-11-12): seguir igual (Fable en todo, auditoría en cada prompt de cálculo). Cuando el límite más alto llegue a
**96–97 %**: guardar todo y dejarle el prompt de reanudación. A **99 %**: revisar el avance desde ese guardado; si es significativo,
guardar y dejar el prompt otra vez; si no, se queda así. Se vigila el MAYOR de los tres porcentajes.

| Momento (UTC) | 5 horas | 7 días | 7 días (con excedente incluido) | cost_usd | Nota |
|---|---|---|---|---|---|
| 2026-11-12 00:07 | 57 % (reinicia 03:40 UTC) | 67 % | **83 %** (aviso desde 75 %; reinicia sáb 14 05:00 UTC) | 446.56 | T-4 integrando, T-8 en FASE A |
| 2026-11-12 00:17 | 62 % | 68 % | **85 %** | — | T-4 integrado (`7fb7926`); T-1 integrando; T-8 y T-5 en FASE A |
| 2026-11-12 00:22 | 68 % | 69 % | **88 %** | — | tres agentes: T-1 integrando, T-5 y T-8 en FASE A (≈ 0.6 puntos/min en la ventana mayor) |
| 2026-11-12 00:26 | 68 % | 70 % | **89 %** | — | El dueño confirma con captura: la ventana mayor es «Semanal · Fable»; las otras dos son «5 horas» y «Semanal · todos los modelos». Se pausan T-5 y T-8 (recién empezados) para que el Fable restante termine la integración de T-1 |

**Equivalencias (captura del dueño, plan Ultra):** `five_hour` = Límite de 5 horas; `seven_day` = Semanal · todos los modelos;
`seven_day_overage_included` = **Semanal · Fable**. Al agotarse Fable se puede seguir con Opus 5.5 mientras quede «todos los modelos».
| 2026-11-12 00:28 | 72 % | 70 % | **89 %** (Fable) | — | T-1 integrando con Fable; T-8 y T-5 con Opus 5.5 esfuerzo extra |
| 2026-11-12 00:35 | 75 % | 71 % | **90 %** (Fable) | — | Fable sube ≈ 1 punto cada 8 min con sólo T-1 y el orquestador |
| 2026-11-12 00:45 | **81 %** | 72 % | 90 % (Fable) | — | el de 5 horas sube ≈ 0.6 puntos/min con T-1 + dos agentes Opus: corte probable hacia 01:15 UTC; reinicia 03:40 UTC |
| 2026-11-12 00:54 | **89 %** | 74 % | 92 % (Fable) | — | T-1 integrado (`5bca7c6`). Se pausan T-5 y T-8 (Opus) para que lo que queda del límite de 5 horas termine la integración de T-6 |

**Capacidad restante estimada (00:54 UTC):** en esta ventana, 34 puntos del límite de 5 horas costaron 8 puntos del semanal de todos
los modelos (≈ 0.24 puntos semanales por punto de 5 horas). Quedan 26 puntos del semanal de todos los modelos ≈ lo que resta de esta
ventana + UNA ventana completa de 5 horas más, y 8 puntos del semanal de Fable. Después, corte hasta el sábado 14 a las 05:00 UTC.
| 2026-11-12 00:56 | **90 %** | 74 % | 93 % (Fable) | — | sólo T-6 integrando (Fable) |
| 2026-11-12 01:12 | **95 %** | 75 % | 94 % (Fable) | — | sólo T-6 integrando; guardado por corte inminente del de 5 horas |
| 2026-11-12 03:42 | 0 % (reinició; próximo reinicio 08:40 UTC) | 77 % | **95 %** (Fable) | — | el dueño pide continuar: T-6 (cierre, Opus), T-8 y T-5 (Opus) |
| 2026-11-12 04:04 | 10 % | 79 % | 95 % (Fable, último dato) | — | tres agentes Opus: T-6 cierre, T-8, T-5 (≈ 1 punto semanal cada 11 min) |
| 2026-11-12 04:26 | 14 % | 80 % | 95 % (Fable, último dato) | — | T-6 integrado (`7e74065`): LOTE 1 COMPLETO; T-8 corrigiendo e integrando, T-5 en FASE A (ambos Opus) |
| 2026-11-12 04:28 | 15 % | 80 % | **97 %** (Fable) | — | MARCA 96–97 % DE FABLE: guardado completo y prompt entregado al dueño. El orquestador deja de programar revisiones periódicas (cada una gasta Fable) |

## Tercera sesión (reanudada 2026-11-12 15:33 UTC; el orquestador vuelve a correr en Fable porque así se abrió la sesión)

Fuente: `list_events(kinds=["rate_limit_event"])` de la sesión nueva. El evento ya NO trae la ventana de 5 horas mientras no hay aviso.
OJO: `resetsAt` = 1795028400 = **mié 18-nov 19:00 UTC** para las dos ventanas semanales (la sesión anterior anotó «sáb 14 05:00 UTC»).

| Momento (UTC) | 5 horas | Semanal · todos | Semanal · Fable | Nota |
|---|---|---|---|---|
| 2026-11-12 15:33 | s/d (sin aviso) | 73 % | **95 %** | arranque: lectura del estado, suite de `df1b23c`, cuatro agentes Opus lanzados (auditoría T-5; FASE A de T-3, T-7a, T-9) |
| 2026-11-12 15:44 | s/d | **26 %** (bajó de 73 %) | 96 % (último dato del evento) | par de `df1b23c` confirmado: 4960 / 16 / 4976 |
| 2026-11-12 ~16:00 | s/d | 26 % | restablecido según el DUEÑO («ya puedes usar Fable de manera normal»); el evento aún no lo refleja | se lanzan con Fable las auditorías adversariales de T-8 (ya en main) y de T-5 (segunda pasada, en paralelo con la de Opus) |
| 2026-11-12 16:00 | s/d | **34–35 %** | **15 %** (restablecido, confirmado por el evento) | 4 agentes Opus (auditoría T-5; FASE A T-3, T-7a, T-9) + 2 auditores Fable (T-8, T-5). El de todos los modelos subió 8–9 puntos en 16 min: vigilar |

**Regla del dueño (2026-11-12 ~16:20 UTC): cuando «Semanal · Fable» llegue a 50 %, DOSIFICAR**: Fable sólo para lo importante
(auditorías adversariales y sus correcciones en prompts de cálculo, T-7b, T-7c, T-11); todo lo demás —integraciones mecánicas,
regeneración de documentos, T-10, T-12— con Opus. Siguen vigentes las marcas de 96–97 % (guardar + prompt) y 99 % (revisar avance).
| 2026-11-12 16:12 | s/d | **40 %** | s/d (15 % a las 16:00) | llegan las dos auditorías de T-5; se lanza con Fable el agente de correcciones + integración. Ritmo del semanal de todos los modelos: ≈ 0.5 puntos/min con 5–6 agentes (26 % → 40 % en 28 min) |
