# Encargo: AUDITORÍA ADVERSARIAL con el modelo de reserva — T-8 (protección de entrada y salida, Fase 6), YA integrado en main

Eres el auditor adversarial. SOLO LECTURA: no edites ni hagas commits. T-8 se implementó y auditó con otro modelo y se integró en
`origin/main` (`df1b23c`); el dueño exige una SEGUNDA auditoría independiente; lo que encuentres se corregirá en una pasada posterior.
Es para una tesis de ingeniería: todo verificado contra el PDF y coherente ingenierilmente.

- Árbol a auditar: `/home/user/wt/main` (checkout de `df1b23c`, sólo lectura). Diff: `git diff 7e74065 df1b23c` (un commit).
  Módulo principal: `src/modulos/M6_proteccion.py`; tests: `tests/test_t8_proteccion.py`; fichas T8-01..06 (Parte XLV de
  `docs/decisiones_diferidas.md`); el párrafo «T-8 de la cadena T» de `CLAUDE.md` resume lo hecho y las diez correcciones de la
  primera auditoría (no las des por buenas: compruébalas).
- Lee primero `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (convenciones, reglas no negociables, lecciones) y `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ENCARGO_T-8.md` (lo pedido).
- PDF: `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`); `hec14.pdf` es la fuente principal.
  Página escaneada/figura → renderízala a PNG en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-8-aud/` y léela con Read. Temporales sólo ahí. Mutantes: `tests/apoyo/mutacion.py`
  o una copia del árbol en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-8-aud/`; nunca edites `/home/user/wt/main`. No corras la suite entera más de una vez (CPU compartida).

## Qué comprobar (como mínimo)
1. **Cada fórmula, coeficiente, tabla y rango de validez contra HEC-14** (numeral, página impresa y PDF, texto literal, unidades SI
   vs. inglesas y sufijo `_SI`): Cap. 10 (Ec. 10.4 y 10.5, límites de TW 0.4D–1.0D, Tabla 10.1 de clases, largo y ancho del apron
   3D + (2/3)L, espesor ≥ 2·D50 —o lo que de verdad diga—, filtro 10.2), Cap. 5 (Ec. 5.1 a 5.4, Tablas 5.1 a 5.4, duración de 30 min
   y qué dice la fuente por debajo, corrección por caída/pendiente, límites de IP y de la resistencia al corte, α y unidades de
   `HEC14_TAU_C_ALFA_U_SI`), Cap. 3 (tirante de borde 3.1.3, Froude con `ye = (A/2)^0.5`), nota 8 de la Tabla 1.1 (límite 1.50 m:
   ¿la fuente lo dice así y para ese método?). Manual MTC 4.1.1.3.7 c) ec. (49) Laushey, Tabla Nº 11 (valor a valor) y Láminas 04–05
   (por imagen); EG-2013 511.08 y Tabla 511-06 con sus notas; HDS-5 5.3.2. Transcripciones de tabla: todas las celdas.
2. **Dorados**: rehaz A MANO los ejemplos resueltos de HEC-14 que los tests usan (págs. 10-18/10-19 y el de socavación; el «CU escalado
   a λ = 0.9» — ¿es legítimo escalar un ejemplo empírico por Froude para caber en un límite?, ¿el test prueba la fórmula o se prueba a sí mismo?).
3. **Coherencia ingenieril**: dirección del conservadurismo de cada elección [A]/[C] (`regla_espesor_longitud_proteccion_salida`
   = `manual` por defecto frente a `envolvente_hec14`: en A-01 0.592 m frente a 0.770 m; `duracion_caudal_pico_socavacion_min`;
   `lectura_coeficientes_socavacion_hec14`; `referencia_profundidad_socavacion`; `tipo_proteccion_entrada`); «protección
   requerida» según la Tabla Nº 11 con régimen; una sola regla de régimen; que un método fuera de rango sea aviso/no evaluable según
   lo que la fuente PROHÍBE o sólo describe; que la profundidad de socavación para el desplante (la consumirá T-7a) no quede del lado inseguro.
4. **Nada inventado ni relleno silencioso**; fuente / interpretación / lo-que-el-proyecto-hace separados; verbos de obligación con
   cita de ese carácter; los seis datos externos con forma y dominio validados (prueba NaN, negativos, cero, cadenas, booleanos).
5. **Robustez**: entradas límite (S = 0, TW = 0, TW ≫ D, Q minúsculo, marco, N celdas > 1, d50 del lecho 0) → sólo `ErrorProyecto`
   capturado o aviso; nunca `ZeroDivisionError`/`KeyError`/`TypeError`. Avisos en `InformePunto.avisos()`, CLI, JSON y memoria.
6. **Lo que NO debía moverse**: d50 de Laushey 0.338 / 0.274 m, espesor 0.592 / 0.479 m, longitud 5.00 m y los diámetros de la línea
   base frente a `7e74065` (mídelo con el comparador de E-B sobre una copia del árbol base).
7. **Tests y mutación**: tests vacuos; los 42 mutantes vivos de la ficha T8-06 ¿están bien clasificados o esconden un hueco real?
8. Lo que veas: docstrings falsos, citas con el capítulo equivocado (la cadena decía cap. 3 para socavación; es el 5), erratas.

## Entrega
Informe en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/AUDITORIA_T-8_fable.md`: veredicto (APROBADO / AJUSTADO / RECHAZADO) y hallazgos numerados H1… con severidad
(BLOQUEANTE / ALTA / MEDIA / BAJA), evidencia reproducible (comando y salida, o página y texto literal) y corrección concreta anclada
por símbolo; separa «refutado con evidencia» de «sospecha»; lista aparte las decisiones del dueño. Devuélveme un resumen de menos de
300 palabras: veredicto, hallazgos por severidad, los tres más graves, si algún número de la línea base está mal, decisiones del dueño.
