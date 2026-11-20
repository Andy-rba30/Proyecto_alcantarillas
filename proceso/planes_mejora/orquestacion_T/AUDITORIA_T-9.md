# AUDITORÍA ADVERSARIAL de T-9 (Fase 10, espaciamiento de alivios) — FASE A

Rama `tesis/T-9`, HEAD `304cea6`, base `df1b23c`. Auditor de solo lectura. Experimentos sobre una
COPIA del árbol (`SP/T-9-aud/copia`, `git archive 304cea6`) y un worktree de la base (`SP/T-9-aud/base`,
retirado al terminar). PDF: `/home/user/andy-rba30/normas/normas/` (Manual de Hidrología: desfase +3;
DG-2018: +1). Scripts en `SP/T-9-aud/scripts/` (exp1…exp4, corridas.sh, mut.py).

## Veredicto: **AJUSTADO** (con un punto REFUTADO numéricamente: H1)

Las citas, páginas y tablas son correctas; la aritmética de M10 (Manning en el triángulo, q' = q·b/10⁶,
L = Q_adm/q') es dimensionalmente correcta y sus dorados están hechos a mano. VB1 falla de verdad, no cae
la corrida con datos malos y ningún diámetro se mueve. Pero la «escorrentía específica = Q/area_ha» combinada
con un `ancho_tributario_m` independiente da un **CUMPLE falso** reproducible (H1), y hay huecos de
cobertura de VB1 y textos que afirman lo que el código no garantiza.

Diámetros movidos: **ninguno** (medido: perfil, perfil ancho y expediente de la línea base, base vs T-9,
y la corrida final de la guía con los siete del cajón: A-01, A-02 y B-01 Ø 0.90 concreto en las dos ramas;
C-01 y B-01 se detienen en el mismo sitio. Con la decisión A declarada en caliente, tampoco).

Punto 1 del encargo (hoja `Conflictos` / §6): ninguno de los 8 objetos en disputa lo toca T-9. Punto 2
(consumidores): `DETALLE_FALTA_L_HIDRAULICO` pasó a plantilla con `{faltan}`; sus dos lectores
(`servicio`, `anticipo`) usan `detalle_falta_l_hidraulico()`; `gui/` no lo lee. Sin roturas. Punto 3
(literales): sólo `# literal-ok` en los exponentes de Manning; `METROS_POR_KM` entra en fórmula (precedente
de MH desde T-1; el docstring de `dominios.py` que dice «ninguna entra en fórmula» ya era falso).

---

## Hallazgos

### H1 — ALTA — REFUTADO con caso numérico — toca FÓRMULA: sí
**`servicio._escorrentia_del_punto` + `M10.longitud_hidraulica`: q = Q/`area_ha` con un `b` que no se
contrasta con el área da VB1 CUMPLE con un caudal de aporte mayor que la capacidad de la cuneta.**
Por contrato (`docs/contrato_entradas.md`, PERFILES[B].origen_del_caudal) en la Familia B `Q_m3s` es el
caudal de la cuneta y `area_ha` «el área tributaria de la cuneta que descarga en el alivio»;
`ancho_tributario_m` es «el ancho de la faja que drena a la cuneta por metro». Son dos descripciones de la
misma área y el código no comprueba que `area_ha·10⁴ ≈ b·s`. Cuando no coinciden, L sale multiplicado por
`area/(b·s)`. Caso (`scripts/exp1.py`): CSV del fixture + B-02 en 2+650; `seccion_cuneta` = 0.20 × 0.50 m,
Z2 = 0.5, bl = 0 (mínimo «seca»), concreto, `S_cuneta` = 0.005, b = 12 m.
A mano: Z1 = 2.5; A = 3.0·0.04/2 = 0.060 m²; P = 0.2·(√7.25 + √1.25) = 0.76212 m; Rh = 0.078727;
Rh^(2/3) = 0.18368; Q_adm = 67·0.060·0.18368·√0.005 = **0.0522 m³/s** (V = 0.87 m/s, gobierna llena).
q = 0.095/0.18 = 0.5278 m³/s/km²; q' = 0.5278·12/10⁶ = 6.33e-6; L = 8 244 m → máx = 200 m; tramo 200 m →
**VB1 CUMPLE**. Pero el aporte declarado del alivio (0.095 m³/s) supera la capacidad en **82 %**: la
condición literal del Manual («Q manning > Q de aporte», pág. impresa 176-177 / PDF 179-180) no se cumple.
Medido por el programa: `Q_adm 0.05221…  L_h 8244.47  max 200.0  tramo 200.0  VB1 True`.
El propio test `test_la_longitud_calculada_entra_al_espaciamiento_con_area_ha` congela el síntoma:
B-01 da L = 42 282 m (211 veces el normativo) porque 18 ha no es la faja de 12 m de un tramo de 200 m
(sería 0.24 ha); y «duplicar `area_ha` duplica L» es la incoherencia escrita como propiedad (con datos
coherentes, b = A/s, L = Q_adm·s/Q y no depende de A). La ficha T9-02 lo condiciona («siempre que el área
tributaria declarada sea la del tramo») pero nada lo verifica ni lo avisa.
**Corrección (anclada):** en `servicio._escorrentia_del_punto`/`M10.verificar_tramo`, comparar directamente
el caudal de aporte del alivio con `CapacidadCuneta.Q_admisible_m3s` (condición literal del Manual), y/o
exigir coherencia `|area_ha·10⁴ − b·s|/(b·s) ≤ tol` (DatoInvalidoError nombrando el par, forma MAT-D13) o
avisar; reescribir el test de «duplicar area_ha» declarándolo. INF-5.1.8 queda «en parte»: el consumidor
existe pero no es coherente sin ese control (T-1 ya le había dado consumidor: el contraste Q/A).

### H2 — MEDIA — refutado con medida — FÓRMULA: no
**VB1 sin evaluar no cuenta en ningún sitio del RESUMEN: «Expediente cerrado: si» y «con aviso: 0».**
`scripts/exp2.py` (A-01 + B-01, `L_hidraulico_m` 150, TW 0.3): `ResumenDeCorrida(puntos=2,
dimensionados=2, incumplidas=0, bloqueadas=0, diferidas=7, cerrado=True, con_aviso=0)`, con el aviso
«VB1 … NO SE EVALUO» sólo en el bloque del punto. Una verificación del conjunto de aceptación de la B que no
se evaluó no es un `Bloqueo` (ni «espera» ni diferida) ni un INDICADOR. Lo mismo en la guía (`resumen_perfil`
promete «Expediente cerrado: si» con B-01 sin VB1). Corrección: que `TramoDeAlivio` sin verificación cuente
(p. ej. `Bloqueo` de tipo espera/diferible con el dato que lo destraba, o en `con_aviso`), y decirlo en la guía.

### H3 — MEDIA — refutado con medida — FÓRMULA: no
**Tramos de cuneta que VB1 nunca mira, sin aviso** (`servicio._verificar_tramos_de_alivio`).
(a) Con `inicio_tramo_cuneta_km` declarado se ignora la obra B anterior: B-01 2+450, B-02 2+900 con inicio
2.80 → B-02 cumple con 100 m y los **350 m** 2+450→2+800 (que sólo pueden descargar en B-01) no se
evalúan; con inicio 3.00 (posterior a la obra: `abs()` lo acepta en silencio) quedan 450 m sin mirar
(`scripts/exp3.py`, casos «hueco» y «posterior»). (b) El tramo aguas abajo (progresivas crecientes) del
ÚLTIMO alivio no se evalúa nunca ni se avisa; el aviso del primero dice «aguas arriba», que presupone un
sentido de flujo que el propio docstring declara «no dato». Corrección: avisar de cada hueco (entre la obra
anterior y el inicio declarado, y tras el último alivio) o exigir el extremo en los dos sentidos.

### H4 — MEDIA — refutado con medida — toca CITA: sí
**«TR = 35 años» cableado en el texto de la memoria** (`M10.longitud_hidraulica`, nota del paso 10.3;
`espaciamiento_alivio`, procedencia y docstring). Con `riesgo_admisible_propietario =
{'quebrada_menor': {'R': 0.20, 'n': 15}}` el TR del punto pasa a **68 años** (67.72) y la nota sigue
diciendo «TR = 35 años: fila …» (`scripts/exp4.py`). Y con el caudal DECLARADO (el caso del fixture) el
programa no sabe con qué TR lo hizo el estudio, pero la nota afirma «con el periodo de retorno del punto de
Familia B en la Fase 2». Además la fila de la Tabla Nº 02 no da «TR = 35»: da R = 35 % (y n = 15 por la nota
(**)), de donde T = 35.3 años (ver D). Corrección: leer el TR de `informe.clasificacion` en el camino
calculado y decir «TR del estudio hidrológico, no conocido por el programa» en el declarado.

### H5 — MEDIA — toca CITA: sí
**La ventana de `seccion_cuneta` no es «la que las fuentes acotan»** (`criterios_adoptados.py::seccion_cuneta`).
(a) «ancho 2.40 = 4 × 0.60, el talud interior más tendido que la Tabla 304.12»: la tabla (Manual pág.
impresa 173 / PDF 176, reproducida del DG-2001) da «INCLINACIONES MÁXIMAS DEL TALUD (V:H) INTERIOR»: 1:2
(*sólo en casos muy especiales*) / 1:3 con V.D. < 70 km/h; 1:3 / 1:4 con > 70 km/h según IMDA < / > 750.
1:4 es la inclinación más EMPINADA admitida en la vía más exigente, no la más tendida. (b) Z1 = a/d no se
contrasta con esa tabla: la ventana acepta a = 0.50, d = 0.60 → Z1 = 0.83, prohibido para toda clase de vía.
(c) El piso de la ventana es el mínimo «seca» (0.20 × 0.50) mientras `long_max_cuneta` = 200 m adopta
«región muy lluviosa»: un barrido puede calcular con una sección por debajo de la EXIGENCIA de la Tabla Nº
34 («las dimensiones mínimas serán», pág. 177/PDF 180) para la región que el propio proyecto adoptó.

### H6 — BAJA — FÓRMULA: no
`revestimiento_cuneta` = «concreto» es el extremo MENOS conservador para la longitud (K = 67 frente a 33/25;
v_lim 4.50 frente a ≤ 3.00): la justificación no lo dice. La llamada «* Para flujos de muy corta duración»
de la fila Concreto (Tabla Nº 33) sólo va como nota del paso, y el evento de diseño es el FEN (lluvias
prolongadas). Hoy la velocidad no gobierna en concreto con S ≤ 2 % (V_llena 2.96 m/s con 0.40×1.20, S 2 %).

### H7 — BAJA — mutación — FÓRMULA: sí (uno)
Arnés de EXT-11 sobre 11 funciones de M10 y 3 de `servicio` (207 mutantes, objetivos
`test_t9_espaciamiento.py` + `test_M10_espaciamiento.py`): **175 muertos (84.5 %), 32 vivos**. Los que
importan: `caudal_a_velocidad` `Z2 ** 2 → Z2 ** 3` vive porque TODOS los tests usan Z2 = 1 (la rama de la
velocidad límite no tiene dorado con talud exterior ≠ 1); `_criterio_que_gobierna` → None (el
`criterio_aplicado` de VB1 con el límite hidráulico calculado no se comprueba); en `verificar_tramo`
`L_normativo + TOL → − TOL` (con un máximo desconocido y s = 200 m exactos el mutante da CUMPLE contra 200
sin conocer el hidráulico: falta la frontera); `valor >= 0 → > 0` (el 0+000 sólo se prueba en la carga);
`_escorrentia_del_punto` `and → or` en `caudal.origen == CALCULADO and cuenca is not None` (Q declarado con
cuenca presente: la regla «un Q_m3s lleno GANA y no se recalcula» no tiene test en la Fase 10). El resto son
textos (lado del aviso de pendiente, procedencia declarado/calculado, notas), guardias inalcanzables o
equivalentes. Detalle: `SP/T-9-aud/tmp/mut.json`.

### H8 — BAJA — FÓRMULA: no
`tests/test_guardias_de_la_suite.py::SIN_CASO_PATRON['M10_espaciamiento']` sigue diciendo «falta
`L_hidraulico`» y «su n de Manning»: T-9 los calcula (Tabla Nº 32) y su dorado vive en el test, no en
`tests/fixtures/casos_patron.py`. Es la «exención que sobrevive a su motivo» que esa guardia persigue.

### H9 — BAJA
`servicio.FAMILIAS_QUE_EXIGEN_COLUMNA['area_ha'] = (Familia.A,)` y su comentario («no la exige») quedan
desfasados: la Fase 10 la exige en B (rama `DatoFaltanteError('area_ha')` de `_escorrentia_del_punto`,
inalcanzable porque M0 ya la exige en B).

### H10 — BAJA — toca CITA: sí
Lecturas del proyecto escritas en notas y no como `Interpretacion` (CLAUDE.md: «fuente / lee / hace»): la
unión de filas Tabla 32–Tabla 33 (`nota_del_proyecto` de F10.CAPACIDAD), «es también el lado conservador»
en la nota de la CITA `MC_HHD.4.1.2a`, y el fundamento F10.TRAMO (verbo OBLIGA) cuyo `por_qué` dice «más de
lo que el Manual admite» con un umbral de 200 m que la fuente sólo RECOMIENDA («se recomienda reducir»).
T-9 no crea ninguna `Interpretacion`.

### H11 — BAJA
En el camino calculado, `MH.caudal_de_aporte_cuneta` corre sobre la MISMA cuenca y el MISMO TR que el caudal
del punto (el test lo afirma: `aporte.Q_m3s == b01.caudal.Q_m3s`): es el caudal del punto con otro rótulo y
la memoria repite los pasos de la Fase 1-bis.

## Sospechas no refutadas → ver «DUDOSO» al final.

---

## Respuestas A–D (premisas de las decisiones del dueño, contra el PDF)

**A. `seccion_cuneta` = mínimo «muy lluviosa».** Tabla Nº 34 «Dimensiones mínimas» (pág. impresa 178 /
PDF 181; repetida en la Figura Nº 28, pág. 179 / PDF 182), TODAS las celdas: Seca (<400 mm/año) D 0.20 /
A 0.50; Lluviosa (400 a <1600) 0.30 / 0.75; Muy lluviosa (1600 a <3000) **0.40 / 1.20**; Muy lluviosa
(>3000) 0.30* / 1.20, «* Sección Trapezoidal con un ancho mínimo de fondo de 0.30». Fuente declarada: Manual
de Carreteras de Bajo Volumen de Tránsito. Texto previo (pág. 177 / PDF 180): «De elegir la sección
triangular, las dimensiones mínimas serán las indicadas en la Tabla Nº 34» (EXIGENCIA de mínimos).
Qué son: «el ancho es medido desde el borde de la rasante hasta la vertical que pasa por el vértice inferior.
La profundidad es medida verticalmente desde el nivel del borde de la rasante al fondo» (pág. 173 / PDF 176;
Fig. 28 lo acota así) ⇒ a = Z1·d: 0.40 × 1.20 fija **Z1 = 3 (1:3)**, y NO el talud exterior. Taludes: interior
por la Tabla 304.12 (DG-2001 reproducida, pág. 173): 1:3 vale salvo V.D. > 70 km/h con IMDA > 750, que
exige 1:4 (a ≥ 1.60 m con d = 0.40); exterior «de acuerdo al tipo de inclinación considerada en el talud
de corte» (Manual pág. 173) y «por lo general coincide con el talud de corte» (DG-2018 304.11, pág. 208 /
PDF 209), con Tabla 304.10 (pág. 204 / PDF 205, cortes < 5 m, H:V): roca fija 1:10, roca suelta 1:6–1:4,
grava 1:1–1:3, limo arcilloso 1:1, arenas 2:1. **La fuente sostiene d = 0.40 y a = 1.20 como mínimo de esa
región; no sostiene ningún Z2**, que mueve Q_adm de 0.467 a 0.871 m³/s (Z2 0.1 → 2.0; S = 1 %, concreto;
con Z2 = 1: 0.670 m³/s, V 2.09 m/s). Recomendación: valor {0.40, 1.20, Z2 = 1.0, bl = 0} con Z2 declarado
como [A] (el talud más empinado de las filas de suelo del corredor, SM/SP-SM/ML → limo/arena, lado seguro
para la capacidad) hasta el EMS; ventana d ∈ [0.40, 0.60), a ∈ [1.20, 2.40] mientras rija «muy lluviosa»
(H5); avisar si la vía resulta > 70 km/h con IMDA > 750 (Z1 = 3 < 4); y declarar que la región en año FEN
está en 1600–<3000 mm/año (si pasa de 3000 el mínimo es trapezoidal, no implementado). **B-01 no cambia en
nada**: medido declarándola en caliente en las tres corridas de la línea base, sólo cambian las listas de
criterios (declarados / sin valor) del JSON — la Fase 10 de B-01 sigue detenida por falta de
`ancho_tributario_m` y `S_cuneta`, y en la guía gana `L_hidraulico_m` = 120.

**B. Borde libre.** Sostenido. Literal (4.1.2.1 a), pág. impresa 174 / PDF 177): «Se rige por dos límites: •
Caudal que transita con la cuneta llena • Caudal que produce la velocidad máxima admisible»; el procedimiento
(pág. 176-177): «Elijo una altura H, que sea menor a 0.60m … si Q manning > Q de aporte, Entonces el diseño
está terminado». En las 225 páginas «borde libre» sólo aparece para alcantarillas (4.1.1.3.7 b), 25 %) y
badenes (4.1.1.4.1 e), 0.30–0.50 m), nunca para cunetas. El 0.10 m del techo de la ventana es adopción.

**C. Obras A como extremo.** El Manual NO lo sostiene: 4.1.2.1 d) (pág. 179 / PDF 182) dice «La descarga
de agua de las cunetas se efectuará por medio de alcantarillas de alivio». Lo sostiene el **DG-2018 304.11**
(pág. 208 / PDF 209): «Se limitará la longitud de las cunetas, conduciéndolas hacia los cauces naturales del
terreno, obras de drenaje transversal o proyectando desagües dónde no existan». Aplicable como lectura
declarada (Interpretacion colgada de DG2018.304.11), con la salvedad de que el perfil (curvas verticales) decide
si la cuneta llega a esa obra. **Consecuencia medida** (simulada con `inicio_tramo_cuneta_km` = 1.92, la
progresiva de A-02): B-01 queda a 530 m de A-02 → **VB1 NO CUMPLE** (530 > 120 en la corrida final de la
guía; > 200 en la línea base, donde el máximo de B-01 no se conoce) → «Verificaciones incumplidas: 1» y
cambia el RESUMEN que la guía promete. No mueve diámetros, sí veredictos: el dueño debe saberlo antes.

**D. TR de 35 años.** La Tabla Nº 02 (núm. 3.6, pág. impresa 25 / PDF 28) se titula «VALORES MAXIMOS
RECOMENDADOS DE RIESGO ADMISIBLE DE OBRAS DE DRENAJE» y da **riesgo (%)**, no TR: «Alcantarillas de paso
quebradas menores y descarga de agua de cunetas 35»; «Drenaje de la plataforma (a nivel longitudinal) 40».
Nota (**): «Alcantarillas de quebradas menores n= 15 años. Drenaje de plataforma y Sub-drenes n= 15 años …
El Propietario de una Obra es el que define el riesgo admisible de falla y la vida útil de las obras». Con la
ec. (1) R = 1 − (1 − 1/T)^n: alivio (descarga de cunetas) T = **35.3 años**; cuneta (drenaje longitudinal,
al que remite 4.1.2 a), pág. 171: «según lo indicado en el ítem 3.6») T = **29.9 años**. Lo fija el
Propietario; la tabla da máximos recomendados (TR mínimos). El código hoy: M1 fija para la B la fila
«quebrada_menor» (R 0.35, n 15) → `exacto` 35.32, `anios` 35, endurecible con `riesgo_admisible_propietario`;
la Fase 10 no usa el TR en el camino declarado (usa Q/A del estudio) y en el calculado usa el del punto.
Recomendación: confirmar 35 como **envolvente conservadora** (la fila del alivio, más lluvia que la de la
cuneta), declarada así y no como «la fila de la cuneta», y corregir el texto cableado (H4).

## Preguntas del informe de FASE A (punto 9)
1. Sección: ver A (valor con Z2 declarado y ventana de la región adoptada). 2. Borde libre: retirar la
frase de la v8 (B). 3. TR: ver D. 4. Obras A: ver C, citando DG-2018 304.11, no el Manual. 5. Nivel de
perfil de la Fase 10: correcto (`long_max_cuneta` es de perfil y M10 no está diferido).

## Riesgos de rebase (no resueltos)
Archivos tocados a la vez por T-9 y por `origin/main` (`e78a4e7`): 31, entre ellos `servicio.py`
(`InformePunto` y `pasos_del_informe`/M11 con las piezas de T-5), `criterios_adoptados.py` (T-5 añadió 7;
T-3 añade `desajuste_empalme_canal_m`), `modelos.py`, `citas/tablas/fundamentos.py`, la línea base entera
(regenerar, no fusionar), `decisiones_diferidas.md` (la «Parte XLVI provisional» ya es de T-5),
`test_memoria_sustentada` (lista de fundamentos F8.* y F10.* no alcanzados), `test_t0_gobernanza`,
`guia_perfil.md` (tablas generadas: regenerar con `python -m tests.apoyo.guia_perfil`). Censos a recalcular:
criterios (109 + T-3 + 3), sin valor (+1, o 0 si se aplica A), `CLAVES_EXTERNAS` 18 → 21 (+1 de T-7a con
`ancho_derecho_via_m`), partición del pre-vuelo, marcas `literal-ok`. Si se aplica A, desaparece el ejemplo
`--declarar seccion_cuneta` de la guía; si se aplica C, cambian el RESUMEN de la guía y la línea base (H2/C).

## DUDOSO — para segunda opinión (máx. 5)
1. **B-01 está en terraplén de 2.2 m** (rasante 40.60, terreno 38.40) y el Manual dice que las cunetas «Se
   proyectarán para todos los tramos al pie de los taludes de corte» (pág. 173 / PDF 176); la v8 §2.3 pide
   para la B «>1.5 m con bordillo y bajantes». ¿Aplica el modelo de cuneta triangular de 4.1.2.1 al alivio
   del corredor? (`M10.capacidad_cuneta`, nota de `PERFILES[Familia.B]`).
2. **n de la cuneta: Tabla Nº 32 frente a Tabla Nº 09** — pág. 175 / PDF 178: «Los valores de Manning (n)
   más usados, se presentan en la Tabla Nº 09 … También se utiliza el Coeficiente de Strickler (K)». La
   elección no se declara y la regla de doble n (n mínimo para el límite de velocidad) no se aplica
   (`CUNETA_STRICKLER_T32`, `M10.caudal_a_velocidad`).
3. **«* Para flujos de muy corta duración»** en Concreto y Mampostería (Tabla Nº 33, pág. 175): ¿vale el
   extremo inferior 4.50 m/s para un evento FEN prolongado? (`lectura_velocidad_limite_cuneta`).
4. **Región pluvial del corredor en año FEN** (Tabla Nº 34, pág. 178): si supera 3000 mm/año el mínimo es la
   sección trapezoidal (no implementada; `MC_HHD.T34#muy_lluviosa_mas_de_3000`). Es un dato de sitio sin
   trazabilidad en el repositorio.
5. **F10.TRAMO con verbo OBLIGA y umbral DURO de 200 m** sobre un «se recomienda reducir» (pág. 179 /
   PDF 182): ¿basta la declaración en `Umbral.aplicacion` o el fundamento debe partir 250 (exige) / 200
   (adopción)? (`fundamentos.TRAMO_ALIVIO`).
