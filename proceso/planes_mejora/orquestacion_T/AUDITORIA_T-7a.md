# AUDITORÍA ADVERSARIAL — T-7a (cabezal por punto y aleros), FASE A

Árbol auditado: `/home/user/wt/T-7a`, rama `tesis/T-7a`, HEAD `1b83d39` (código `64f7d02`), base `df1b23c`.
Solo lectura. Base de comparación: worktree desechable de `df1b23c` en SP (retirado al terminar).
Mutación: copia del árbol en `SP/T-7a-aud/copia`, arnés de EXT-11 y TMPDIR en SP.

## Veredicto: **AJUSTADO**

Es AJUSTADO y no RECHAZADO por tres razones: no se mueve ningún diámetro, sección ni HW del fixture (lo medí bit a bit); las ocho citas nuevas están bien transcritas contra su PDF; y la arquitectura cumple: M11 no hace aritmética, los avisos salen por `InformePunto.avisos()`, las guardias tienen la forma MAT-D13 y los criterios de perfil se miden por corrida. Para cerrar `INF-4.3` hay que corregir antes **H1**, que es la fórmula de los aleros. **H2** obliga a reescribir el plan de integración de la decisión 4 del dueño.

---

## Hallazgos — REFUTADOS CON EVIDENCIA

### H1 · ALTA · toca FÓRMULA: sí — los aleros ignoran el esviaje: con θ ≠ 0 los dos aleros de un mismo cabezal NO son iguales, y el docstring afirma lo contrario
- **Convención.** Está bien y la fuente la sostiene. HDS-5 3.ª ed., List of Symbols, pág. impresa **xix** (PDF 23): «ΘW Flare angle of wingwalls **with respect to extension of culvert side wall**, degrees». El ángulo se mide con el eje, y por eso es **cos α** y no sen α (con sen α, un alero paralelo, α → 0, daría L → ∞). Esta cita es más directa que el rótulo de la Tabla C.2 que usa el código: conviene citarla.
- **Lo que falla.** El talud del terraplén baja **perpendicular a la vía**, no a lo largo del eje del conducto. El propio M7 lo modela así: `M7.longitud_conducto` proyecta `talud·H/cos θ` sobre el eje. Un alero a +α del eje forma |α − θ| con la dirección de bajada del talud, y el otro forma α + θ:
  `L₁ = (h0 − H_f)·talud / cos(α − θ)` y `L₂ = (h0 − H_f)·talud / cos(α + θ)`.
  `M9.predimensionar_aleros` no recibe el esviaje y da la misma `L = (h0 − H_f)·talud/cos α` a los dos lados. El docstring de `Aleros` dice «simétricos».
- **Caso numérico. A-01**: θ = 15°, α = 45°, talud 2.0; en la entrada h0 = 1.45 y H_f = 0.40.
  - El código da 2.970 m a cada lado.
  - La geometría pide **2.425 m y 4.200 m**: el alero largo queda 29 % corto.
  - En la salida (h0 = 2.137) el código da 4.912 m y la geometría pide **4.011 y 6.947 m**.
- **C-01**: θ = 30°, α = 45°, porque 30 no supera el umbral. El alero largo necesita `cos 75°` en el divisor, es decir **2.73 veces** lo que imprime el código. Medido con `SP/T-7a-aud/scripts/demo.py`, caso 3: código 2.970 m, geometría **2.174 m y 8.114 m**.
- **Caso límite sin guardia.** Con α + θ ≥ 90° el alero no alcanza nunca la altura final. Por ejemplo θ = 60° con α = 30°: M0 lo admite, porque el esviaje máximo de 45° solo genera un aviso G3. El código devuelve una longitud finita y no avisa.
- **Afirmación falsa en el código.** El docstring de `predimensionar_cabezal` dice «con esviaje, los aleros absorben el giro respecto del talud». No lo hacen. Además, un cabezal NORMAL al eje queda con el talud a cotas distintas en sus dos extremos, Δz = L_c·sen θ/talud:
  - C-01: 2.20·0.5/2 = **0.55 m**;
  - A-01: 1.70·0.259/2 = 0.22 m.
  
  Con un cabezal así, la corona horizontal no puede coincidir con el talud en toda su longitud.
- **Corrección, anclada por símbolo.**
  - `M9.predimensionar_aleros(…, esviaje_grados)` debe devolver dos longitudes. `Aleros` gana `longitud_aguas_arriba` y `longitud_aguas_abajo`; si se prefiere un solo campo, que sea el mayor de los dos y que se avise.
  - Con `not (cos(α+θ) > TOL)`, levantar `DatoInvalidoError` o `LimiteNumericoError` con el par culpable (α, θ).
  - En la memoria: paso 9.0.3 con θ en la sustitución, y `F9.ALEROS` sin la frase «avanza en la dirección del eje».
  - Alternativa: adoptar un cabezal paralelo a la vía (esviado) como [A]. Eso toca las filas de la Carta 11, que hoy se excluyen precisamente por la elección «normal al eje».
  - La ficha T7A-03 tiene que decirlo.
  - El conflicto #4 y el [S] `orientacion_muro_respecto_al_trafico` quedan acoplados a esta elección: es un riesgo para T-7b.

### H2 · ALTA · toca FÓRMULA o CITA: no — T7A-01 está mal diagnosticado, y la decisión 4 del dueño parte de una premisa falsa
- La ficha T7A-01 dice que «V5 se detiene siempre en `ancho_derecho_via_m`, que no tiene puerta». Lo medido es otra cosa, en tres capas.
  - **Primera capa.** A expediente, A-01, A-02 y B-01 se detienen antes, en el **criterio** `remanso_derecho_via`: [A] sin valor, `CriterioPendienteError` en el bucle de MD. Lo medí con `SP/T-7a-aud/scripts/exp.py` sobre T-7a, con TW 0.3.
  - **Segunda capa.** Con `remanso_derecho_via` declarado (`exp2.py`), `M5.v5_remanso` levanta `DatoFaltanteError('ancho_derecho_via_m')` **sin condición**. El dato no se lee en ningún sitio, porque no hay método de remanso con el que compararlo: la función termina siempre en ese `raise`. Abrir la puerta del dato no cambia nada.
  - **Tercera capa.** Aunque V5 cumpliera (lo simulé en `exp4.py`), A-01 y A-02 se detienen en **V8**: `TR_evento_extremo` está vacío, y después falta el caudal del evento extremo, ficha T1-03.
  - C-01 a expediente se detiene también en V8: `exp3.py`, con los siete criterios del cajón declarados.
- **Consecuencia.** La decisión 4 («abrir la puerta de `ancho_derecho_via_m` … para que la Fase 9 por punto se alcance de punta a punta») **no consigue su objetivo**. Hoy **ningún test** corre la Fase 9 por la ruta real. Todos llaman a `servicio._fase_9` a mano sobre un informe de perfil: los fixtures `a01_con_cabezal` y `test_la_fase_9_del_marco_c01`, y `test_una_dimension_declarada_por_punto_llega_a_la_memoria`.
- **Corrección.**
  - Reescribir T7A-01 con las tres capas.
  - Devolver la pregunta al dueño con estas opciones:
    - (a) método de remanso + valor de `remanso_derecho_via` + el dato + el TR y el Q de V8;
    - (b) correr la Fase 9 como anticipo no bloqueante a perfil, que es la pregunta 2 del informe de FASE A;
    - (c) dejar `INF-4.2` e `INF-4.3` como **«en parte»** mientras no haya una corrida que los alcance.
  - Abrir solo la puerta del dato no sirve.

### H3 · MEDIA · toca CITA: sí — el «0.80 min.» de la Lámina Nº 04 no se mide desde la cara superior de la losa
- **Lectura de la lámina.** Lámina Nº 04, pág. impresa 210, PDF 213. La rendericé a 300 dpi (`SP/T-7a-aud/img/mc_213_dent.png`).
  - La línea superior de la cota «0.80 min.» arranca en la superficie del **terreno natural**, junto al dentellón, que coincide con la cara inferior del relleno granular. Ese paquete es de 0.15 m de concreto sobre 0.20 m de granular.
  - Medido a escala con la cota de «1.00m» de la misma figura (208 px = 1.00 m), la profundidad desde la cara superior de la losa es ≈ 1.15 m.
- **Lo que hace el código.** `LosaDeEntrega.profundidad_dentellon` (docstring) y `dentellon_losa_entrega` aplican 0.80 m «desde la cara superior de la losa». Con la losa de 0.30 m del propio código, el dentellón penetra **0.50 m** bajo la losa, no 0.80 m bajo el terreno.
- **Agravante en A-01 (salida).** El pie se toma en el receptor (41.30), pero la losa y el dentellón se refieren a la solera (41.987). La base del dentellón queda en 41.187: **0.11 m** bajo el lecho receptor, frente a 0.80 m en la lámina análoga. Son dos referencias de terreno distintas para el mismo extremo.
- **Corrección.** Medir el dentellón desde el terreno al borde de la losa, o desde la cara inferior de la losa más su base granular. Usar la misma referencia que `ExtremoDelConducto.cota_pie`. Corregir la `nota` de la cita `MC_HHD.LAMINA_04#DENTELLON`.

### H4 · MEDIA · toca FÓRMULA o CITA: no — una dimensión DECLARADA puede violar un mínimo con número y ninguna CB lo dice
Medido con `demo.py`:
- **Caso 1.** `tipo: gravedad_ciclopeo` con `espesor_zapata_m: 0.20` pasa CB1 a CB4 en verde, sin aviso. Viola E.060 22.7.4, pág. 193: «no debe ser menor que 300 mm», [N].
- **Caso 2.** `profundidad_dentellon_m: 0.10` con la hoya 2.0 m por debajo pasa CB1 a CB5 en verde. Viola AASHTO 12.6.5, pág. 12-20 / PDF 1658: «a cut-off wall … extending below the maximum anticipated depth of scour … shall be used», y la cota de 0.80 m de la Lámina Nº 04 ([N→]).
- **Corrección.** Añadir a `M9.verificar_compatibilidad_cabezal`, con el mismo `_verificacion_cb`:
  - CB6: `e_z ≥ ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M` cuando el tipo es gravedad;
  - CB7: profundidad del dentellón ≥ el mínimo del criterio y base ≤ fondo de la hoya, cuando la hay.

### H5 · MEDIA · toca FÓRMULA o CITA: no — mutación: 185 de 226 muertos (81.9 %); sobreviven mutantes que importan
- **Cómo lo medí.** Arnés de EXT-11 sobre las funciones nuevas de M9, con objetivos `test_t7a_cabezal_geometria` y `test_M9_cabezal`. Detalle en `SP/T-7a-aud/mut.json`. Los vivos que importan:
  - `verificar_compatibilidad_cabezal`: `cota_fondo_hoya - margen → + margen` **vive**. CB5 nunca se prueba fallando: el margen de 2.0 ft no lo defiende ningún test.
  - `verificar_compatibilidad_cabezal`: `clave_exterior + recubrimiento → −` **vive**. CB2 no se prueba en su frontera.
  - `predimensionar_cabezal`: `desplante + H_c → desplante − H_c` **vive**. La coronación que sale de una `altura_total_m` declarada no la comprueba ningún test.
  - `extremos_del_conducto`: `socavacion is None → is not None`, dos casos, **viven**. **Ningún test pasa una `SocavacionSalida` con hoya real por la ruta de la etapa**: el enlace T-8 → T-7a (la hoya baja el desplante) solo se prueba con un `ExtremoDelConducto` armado a mano.
  - `extremos_del_conducto`: el ancho de N celdas (`- (n-1)*t` → `+` o `/`) vive, porque N > 1 nunca se prueba. También viven la guardia de TW e `y_salida_m` nulos y las guardias de α de `predimensionar_aleros`.
  - `longitud_entre_cabezales`: la rama «método distinto de por extremo» (`return None`) vive.
  - Los demás son de frontera o de texto, y probablemente equivalentes.
- **Corrección.**
  - Una prueba con `material_lecho_salida` (o `profundidad_socavacion_estimada_m`) que llegue a `servicio._fase_9` y fije D_f, CB5 y el dentellón con aritmética escrita.
  - Una CB5 que falle con un D_f declarado entre `hoya − margen` y `hoya`.
  - Una `altura_total_m` declarada con su coronación escrita a mano.
  - Un marco de dos celdas.

### H6 · MEDIA · toca FÓRMULA: sí — la longitud entre cabezales lleva el talud a la corona del bordillo, no al relleno
- **La incoherencia.** La regla define la coronación como clave + **relleno retenido (0.30)** + **bordillo (0.15)**; el bordillo, por definición, sobresale del relleno. Pero `M9.longitud_entre_cabezales` hace morir el talud en la coronación, y `predimensionar_aleros` toma h0 = coronación − pie. Así el talud monta sobre el bordillo, cuando CB2 verifica la coronación contra clave + recubrimiento y no contra la cota del bordillo.
- **A mano, A-01.** Comprobé el número del código:
  `L_cab = [9.60 + 2.0·((44.20 − 43.55) + (44.20 − 43.4368))]·(1/cos 15°) = (9.60 + 2.8264)·1.035276 = 12.865 m`
  Con el talud muriendo en el relleno (corona − 0.15):
  `(9.60 + 2·(0.80 + 0.9132))·1.035276 = 13.486 m` (+0.62 m)
- **Además.** La fórmula no dice si mide a la cara interior (trasdós) o a la exterior. El barril atraviesa el muro, que suma 2·0.30·1.035 = 0.62 m más para el metrado.
- **Cifra mal dicha.** El docstring y la ficha T7A-06 dicen que la cota de salida sube «milímetros». Cada extremo se mueve unos 3.0 m: 0.006·3.0 = **1.8 cm**.
- **Corrección.** Declarar el nivel (relleno, no bordillo) y la cara de medida; para el metrado, sumar el espesor del muro; corregir «milímetros». A la clave da 14.676 m, comprobado a mano; al fondo, 18.869 m.

### H7 · MEDIA · toca FÓRMULA o CITA: no — la rama «gravedad ciclópeo hasta 2.0 m» es inalcanzable con el catálogo, y cuando se alcanza no da un muro de gravedad
- **Inalcanzable.** H_c incluye D_f. Con `DIAMETRO_MIN = 0.90` (4.1.1.3.4 a, [N]), la mínima H_c es:
  - TMC: 0.90 + 0.015 + 0.30 + 0.15 + 0.80 = **2.165 m**;
  - concreto: **2.25 m**.
  
  Las dos superan 2.0 m: todo cabezal de la obra sale **voladizo armado**. El mínimo de E.060 22.7.4 y la regla H/6 nunca actúan en producción. Solo se alcanzan moviendo `altura_max_gravedad_m` dentro de su ventana, hasta 2.5.
- **Cuando se alcanza.** La pantalla de H/6 es más delgada que la del voladizo armado (0.30 m) para H_c < 1.8 m. La sección resultante (pantalla H/6, zapata de 0.7·H, talón de 0.3·H) es un voladizo de concreto simple. E.060 22.10.2.1 y 22.10.2.2 (pág. 195) limitan el ciclópeo a «muros de contención de gravedad» y obligan a verificar flexión y corte en voladizos de longitud mayor que medio peralte.
- **Corrección.** Declarar en la ficha T7A-04 que la regla mide la altura total y que es inalcanzable con D ≥ 0.90 m. O medir el umbral sobre la altura visible (coronación − pie). En cualquier caso, avisarlo.

### H8 · MEDIA · toca CITA: sí — E.050 26.2 rotulado [N] contra el dictamen del verificador ([N→] para un cabezal vial), sin declarar la discrepancia
- **Las dos lecturas del PDF.**
  - E.050, Art. 1 y Art. 3 (pág. 7): su objeto es la «cimentación de edificaciones y otras obras indicadas en esta Norma», y su ámbito, «en concordancia con … G.010 … RNE».
  - E.050, 39.13.7 (pág. 73): «El muro de contención debe cumplir con todo lo especificado en el Capítulo IV», y el Art. 26 está en el Cap. IV (págs. 35–40). Esto hace defendible el [N] para un muro de contención.
- **El conflicto.** El dictamen `ORQ/DICTAMEN_marco_cabezal.md` califica E.050 de **[N→]** para un cabezal vial. La tabla §0.1 de la v8 dice [N]. T-7a escribe `PROFUNDIDAD_CIMENTACION_MIN_M` en `constantes_normativas` (que es solo para [N]), y en CB4 pone «EXIGENCIA de E.050», sin decir nada de la discrepancia.
- **Corrección.** O se mueve a un criterio [N→] (como `dentellon_losa_entrega`), o se declara en la nota de la cita y de la constante por qué se lee [N] (la vía de 39.13.7). La regla de CLAUDE.md obliga a declararlo en el punto de uso. Va también a DUDOSO.

### H9 · BAJA · toca FÓRMULA o CITA: no — detalles
- **Dimensiones rotuladas como regla aunque salgan de valores declarados.** El talón se imprime «propuesta por regla» aunque B, la punta y la pantalla se hayan declarado. También `L_a` y h0 cuando se declara `altura_total_m`.
- **JSON.** `"criterios": ["embocadura_cabezal", ""]` cuando el cabezal es recto.
- **Docstring desactualizado.** `servicio.correr_cabezal` dice todavía «la geometria declarada».
- **Aviso con la causa equivocada.** El aviso de desplante sin socavación culpa a «falta `material_lecho_salida`» también cuando el lecho se declaró y `socavacion_salida` se bloqueó por método no evaluable o por dato inválido.
- **Dentellón al ras de la hoya.** A la salida, el dentellón llega **hasta** el fondo de la hoya, con margen 0, cuando AASHTO dice «extending **below**».
- **Cita de la fórmula.** `formula_cita_id` de `F9.ALEROS`, `F9.LOSA` y `F9.LONGITUD` apunta a fuentes que no contienen la fórmula. Es la misma práctica que M7, con nota.
- **Carta 12.** `BANDAS_ALETAS_CAJON_A1` admite la escala 3 de la Carta 12 («30° skewed barrel») aunque excluye la Carta 11 por la misma razón (cabezal normal al barril). Queda fuera de la ventana de 30° a 60°.
- **Recubrimiento sobre la clave.** `recubrimiento_clave_m` = 0.30 se justifica como «del orden de los 12 in» de la Tabla 12.6.6.3-1 de AASHTO, que son 0.3048 m. Es la lógica del conflicto #5 y de MAT-D16: un mínimo redondeado hacia abajo. O se quita la referencia o se usa 0.3048.
- **`variables_entrada`.** Atribuye `angulo_aletas` a la «Fase 9» (M9), aunque es de perfil y corre antes de la Fase 4.
- **Coherencia por familia.** La coherencia del marco se decide por la familia (C) y no por la forma de la sección. Hoy es equivalente, porque M2 solo da el marco a la Familia C.

### H10 · BAJA · toca FÓRMULA o CITA: no — «extremo de más material» no es el lado seguro con kh = 0.50
- La ficha no lo afirma («holgado no esconde falla»), pero la pregunta del encargo pedía comprobarlo.
- En el caso sísmico, cada kN de muro añade kh·ΔW = 0.5·ΔW a la fuerza que desliza y μ·ΔW a la que resiste.
- Con δ_base = 2/3·30°, μ = 0.364 < 0.5: más masa **empeora** el deslizamiento sísmico.
- Ejemplo: engrosar la pantalla de A-01 de 0.20 a 0.30 m añade ΔW = 4.86 kN/m y deja un neto de −0.66 kN/m.
- Que «más material» favorezca la estabilidad depende de φ, que el EMS todavía no ha dado.

## Sospechas (no refutadas)
- La zapata del voladizo armado con H/10 da 0.225 m en la entrada de A-01. E.060 15.7 (pág. 138) exige ≥ 300 mm **sobre el refuerzo inferior**. Si la Vía 1 (§0.2) deja fuera ese artículo, ¿qué mínimo de AASHTO Sec. 5 rige? Lo va a encontrar T-7c.
- «H/8–H/6» para la pantalla de un muro de gravedad: en el predimensionamiento clásico H/8–H/6 es el espesor de la zapata del muro de gravedad, no de la pantalla. El PDF de VARIOS (p. 42) no está en la sesión.

## Verificaciones que CONFIRMAN lo que dice el implementador
- **Citas**, comprobadas en el PDF (texto literal, número, página impresa y del PDF):
  - `E050.26.2#PROFUNDIDAD`: pág. 38 / PDF 38. Literal exacto; la excepción de roca está en la misma oración y la nota lo dice.
  - `AASHTO_LRFD_9.12.6.5#ZAPATAS`, `#DENTELLON` y `#ALEROS`: 12-20 / PDF 1658, «Scour». Literales exactos; los 2.0 ft están en el texto.
  - `AASHTO_LRFD_9.10.6.1.2#DESPLANTE`: 10-52 / PDF 1341. Exacto.
  - `E060.22.7.4#ZAPATA`: 193 / PDF 193, «300 mm». Exacto; el Cap. 22 alcanza al ciclópeo (22.10.1: «concreto simple … con piedra desplazadora»).
  - `MC_HHD.LAMINA_02A`: 208 / PDF 211, leída por imagen. Se ven la caja receptora sin aleros y la salida con aleros acotada «VARIABLE».
  - `MC_HHD.LAMINA_04#DENTELLON`: 210 / PDF 213. El texto «0.80 min.» y «0.40m» es correcto; la referencia de la cota, no (H3).
  - HDS-5 Tabla C.2, C.6 / PDF 216: tubo de concreto y de metal corrugado bajo «Headwall or headwall and wingwalls», 0.5. Cajón: 30–75° → 0.4; 10–25° → 0.5; paralelos → 0.7; sin aleros → 0.5.
- **Etiquetas.**
  - `angulo_aletas` 45/30: [A] con ventana por campo.
  - `predimensionamiento_cabezal`: [A]; ninguna regla se atribuye con página a VARIOS.
  - `embocadura_cabezal`: [A] de perfil.
  - `margen_zapata_bajo_socavacion_m` 0.6096: [C], ventana 0–0.6096, valor en el extremo conservador.
  - `dentellon_losa_entrega`: [N→] con la analogía declarada.
- **Geometría de A-01 a mano. Coinciden todos los valores con el código.**
  - Entrada:
    - coronación: max(42.10 + 1.00 + 0.45, 42.10 + 1.042) = 43.55;
    - desplante: 41.30 → H_c = 2.25 m, voladizo;
    - zapata: B = 1.575, e_z = 0.225, punta 0.520, talón 0.755;
    - muro y aleros: L_c = 1.70, L_a = 2.970.
  - Salida:
    - solera 41.987; pie = min(41.987, 41.30) = 41.30, **−0.687 m**;
    - coronación: max(42.987 + 0.45, 41.987 + 0.627) = 43.437;
    - desplante 40.50 → H_c = 2.937 m;
    - zapata: B = 2.056; aleros h0 = 2.137 → L_a = 4.912.
- **PARADA (c).** HW de A-01, A-02 y B-01 (corrida de perfil con TW 0.3) y de C-01 con los siete criterios del cajón: **iguales en `repr`** entre `df1b23c` y T-7a (C-01 = 0.623401190456344). Comparador de E-B sobre los tres JSON de `tests/linea_base_familia_c/`: ninguna diferencia en `diseno`, ninguna «no comparable». La protección de entrada de A-01 y A-02 cambia solo `tipo_embocadura` y el texto de `elementos`; V_entrada no cambia, ni ningún número de la Fase 6. `test_guia_perfil`, `test_linea_base`, `test_t7a`, `test_M9` y `test_nivel_medido`: **332 passed**. **Diámetros movidos: ninguno.**
- **Nivel.** La corrida de perfil usa `embocadura_cabezal` y `angulo_aletas` (de perfil) y no usa ninguno de los tres criterios de expediente nuevos.
- **Arquitectura.** M11 solo formatea. No encontré ninguna ruta nueva que salga fuera de `ErrorProyecto`, salvo el `ValueError` declarado de `extremos_del_conducto` (TW e `y_salida_m` nulos, que no ocurre con M4).

## Las cuatro decisiones del dueño
1. **cos α** — **CONFIRMADA en la convención, REFUTADA como fórmula completa.** La fuente es HDS-5 pág. xix (ΘW con la prolongación de la pared del barril). Con esviaje la longitud es /cos(α ∓ θ) y los dos aleros difieren (H1).
2. **Pie de salida en la más baja** — **SE SOSTIENE con AJUSTE.** Va del lado seguro para D_f y para los aleros. Pero la losa y el dentellón siguen referidos a la solera: son dos «terrenos» en el mismo extremo (H3).
3. **Caja receptora sin aleros** — **SE SOSTIENE.** La Lámina 02-A (PDF 211) dibuja la caja receptora sin aleros. Residual: el código no modela la caja receptora, y la entrada de B-01 (Familia B, alimentada por la cuneta) recibe un cabezal con aleros a 45°.
4. **Abrir la puerta de `ancho_derecho_via_m`** — **PREMISA REFUTADA** (H2). V5 no lee ese dato, porque falta el método. Antes la detiene el criterio vacío `remanso_derecho_via`, y después la detiene V8. La puerta sola no hace alcanzable la Fase 9.

## Riesgos de integración
- **`servicio.correr_punto`.** main insertó `_fase_8_conducto` y T-9 toca `_fase_10`. `_fase_9` tiene que quedar detrás de `_fase_6_socavacion` y de la Fase 8. Además, el import de `EMBOCADURA_CABEZAL_RECTO` en `servicio`.
- **`M6.proteccion_entrada`.** main pasó a `_exigir_texto_de`. Hay conflicto de texto en el docstring y en `Magnitud`; ningún conflicto de números.
- **`tests/test_t8_proteccion.py`.** main lo reescribió (312 líneas) y T-7a edita la aserción de la embocadura.
- **`tests/test_ext8`.** T-7a sube el techo a 22 páginas medidas sobre `df1b23c` (20.7); main midió 20.3. Hay que **remedirlo** sobre el árbol fusionado, no arrastrar el 22.
- **T-3.** Con su valor de archivo (`cajon_concreto_aletas_30_75` / `cajon_aletas_30_75_escuadra`), C-01 es coherente para α entre 30 y 60. A cambio, la nota de coherencia aparece siempre en C-01 (línea base). Su archivo nuevo `informe_familia_c.json` gana la clave `cabezal`. Un barrido de `embocadura_cabezal=cabezal_recto` bloquea C-01, y es lo esperado.
- **Censos.** Criterios: 109 + T-3 + T-9 + 3. `dominios` 12. `LO_QUE_ESCRIBIO_CADA_PROMPT`. Parte de `decisiones_diferidas`: la XLVI es de T-5 y hay que renumerar.
- **Tracker.** `INF-4.2` e `INF-4.3` no deberían marcarse «Cerrado» sin H1 y H2. Con H1 abierto, `INF-4.3` queda en parte.

## DUDOSO — para segunda opinión (máx. 5)
1. **E.050 26.2: ¿[N] o [N→] para un cabezal vial?** Art. 1/3 (pág. 7) frente a 39.13.7 → Cap. IV (pág. 73). Afecta a `PROFUNDIDAD_CIMENTACION_MIN_M` y a CB4.
2. **Lámina Nº 04: ¿desde qué plano se mide «0.80 min.»?** PDF 213, pág. impresa 210; recorte en `SP/T-7a-aud/img/mc_213_dent.png`. Leo terreno natural / cara inferior del granular. Afecta a `dentellon_losa_entrega` y `LosaDeEntrega.profundidad_dentellon`.
3. **AASHTO 12.6.5: ¿«the footings of structures» incluye la zapata de un cabezal?** 12-20 / PDF 1658. Lectura [C] en `margen_zapata_bajo_socavacion_m`.
4. **E.060 15.7 (pág. 138): ≥ 300 mm sobre el refuerzo inferior, frente a la zapata armada de H/10 = 0.225 m.** ¿Rige pese a la Vía 1 (§0.2 de la v8)? Afecta a `predimensionamiento_cabezal.divisor_peralte_zapata`.
5. **«H/8–H/6» como espesor de la pantalla de gravedad (INFORME §4.2, VARIOS p. 42 no disponible).** ¿Es el espesor de la zapata en la fuente original? Afecta a `predimensionamiento_cabezal.divisor_espesor_gravedad`.
