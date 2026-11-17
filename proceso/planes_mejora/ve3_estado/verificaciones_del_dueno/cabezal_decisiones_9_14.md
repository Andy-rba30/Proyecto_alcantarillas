> Verificación independiente (modelo Fable, desde la otra sesión del dueño) de las ELECCIONES 9 a 14 del cabezal, ANTES de que el dueño decida. La sesión que la envía comprobó por su cuenta: `factor_muro_eleccion` = `sin_reduccion` en el archivo, y el texto de AASHTO C11.6.5.4 (muros con «structural wing walls» como no cedentes; 1.0·k_h0 «where doubt exists»). **Las decisiones 9 a 14 siguen PENDIENTES del dueño**: no las apliques por este informe; la respuesta del dueño irá al LEEME.

# Verificación independiente de las decisiones 9 a 14 del cabezal (VE-3)

**Objeto:** las seis elecciones de criterio que `proceso/planes_mejora/ve3_estado/LEEME.md` (rama `origin/claude/youthful-shannon-rjzmuc`, commit `ce46fcf`) propone al dueño a partir de `ENSAYOS_DISENO_CABEZAL.md`.
**Método:** cada cita se releyó en la fuente primaria (PDF de `/home/user/Normas`), con numeral, página impresa y texto literal. No se recalcularon los ensayos: sus cifras se toman tal como el informe las mide y se dice cuándo eso limita el dictamen.
**Fuentes leídas:** AASHTO LRFD 9.ª ed. (2020); Manual de Puentes MTC (versión libro); Caltrans BDP 11.2 (octubre 2022); HEC-14 3.ª ed.; Manual de Hidrología, Hidráulica y Drenaje MTC; hoja de ruta v8, `src/criterios_adoptados.py` y `docs/decisiones_diferidas.md` de la rama.

---

## 1. Resumen

| N.º | Recomendación de la sesión | ¿Cita exacta? | ¿Lo fija la hoja de ruta o norma peruana? | Efecto medido (informe de ensayos) | Dictamen |
|---|---|---|---|---|---|
| 9 | Talón con el método exacto (reacción del terreno) | Sí (11.6.1.2, pág. 11-20) | No. La hoja de ruta §9.4 (5) describe «peso entero» como hecho del código; el Manual de Puentes no transcribe 11.6.1.2 | M del talón 2.3 a 4 veces menor en geometrías que cumplen (hasta 13 en las que ya fallan); peralte 0.40–0.50 m en vez de 0.85–1.65 m | **ACEPTAR CON CONDICIÓN**: envolvente de Resistencia I (γ máx. y mín.) y Evento Extremo I, con la presión lineal de 10.6.5 y despegue |
| 10 | Pantalla cargada con la cuña sobre su propia cara | Sí (Caltrans BDP 11.2, págs. 11.2-27/28) | No | 1.35 a 1.5 veces menos momento con zapata de 0.40 m (hasta 4 con las zapatas infladas de hoy) | **ACEPTAR CON CONDICIÓN**: la cuña llega a la superficie real (talud sobre la corona y sobrecarga) y el sismo suma la inercia de la pantalla |
| 11 | φ de la Tabla 11.5.7-1 (0.55 / 1.0) | AASHTO sí. **Manual de Puentes 2.11.8.5 mal leído** (es de barreras de sonido) | No: la hoja de ruta §9 deja las dos tablas en la ventana del [A] | −0.10 a −0.90 m de B (típico −0.30 m) | **ACEPTAR**, corrigiendo la justificación |
| 12 | Mismo régimen para estabilidad y armado: muro que cede | Citas exactas, pero **la premisa «hoy k_h = 0.5·k_h0» es falsa para el valor de archivo** | Sí en parte: hoja de ruta §9.2 («No asumirlo en un cabezal empotrado en terraplén») y decisión del dueño del 2026-11-13 (T7C-02) | Pantalla de 0.30 m pasa en E1, E9, E10 con `cedente` | **ACEPTAR el principio, RECHAZAR el valor por defecto**: un solo régimen, pero el de archivo sigue siendo «no cede» |
| 13 | Incremento sísmico: distribución estática, no menos de H/3 | Sí (11.6.5.3, pág. 11-30) | No lo fija; el Manual de Puentes peruano dice lo mismo y lo refuerza | −0.20 a −0.30 m de B donde gobierna el portante sísmico | **ACEPTAR CON CONDICIÓN**: solo con el muro que cede; con el que no cede sigue h/2 |
| 14 | Desplantar bajo la «hoya protegida» (o bajar el margen) | Sin cita para la «hoya protegida» | No. El Manual de Hidrología solo recomienda proteger el cauce | No medido directamente; por la Tabla M-a, 0.61 m menos de altura llevan E1-salida de B 3.08 / e_z 0.80 a ≈ 2.6 / 0.40 | **RECHAZAR la «hoya protegida»** (ninguna fuente da esa profundidad); **ACEPTAR «bajar el margen»** a 0 dentro de la ventana |

**Veredicto.** Las seis recomendaciones reducen el margen, y cuatro de ellas (9, 10, 11, 13) están sostenidas por la letra de AASHTO o por un ejemplo resuelto reconocido: se pueden aceptar con las condiciones de la tabla.
La 12 no se puede aceptar tal como está redactada: AASHTO pone el estribo con aleros estructurales entre los muros que pueden no ceder y recomienda k_h = 1.0·k_h0 en caso de duda, la hoja de ruta lo advierte expresamente y el valor de archivo ya es «sin reducción».
La 14 mezcla una opción sostenida (margen 0, HEC-14 5.1.3) con otra que obligaría a inventar una profundidad que ninguna fuente del repositorio de normas da.

---

## 2. Decisión 9 — Momento del talón de la zapata

**Texto de la fuente.** AASHTO LRFD 11.6.1.2 «Loading», pág. impresa 11-20 (PDF 1489):

> «Where spread footings are used, the rear projection shall be designed as a cantilever supported at the abutment stem and loaded with the full weight of the superimposed material, unless a more exact method is used.»

AASHTO LRFD 10.6.5 «Structural Design», pág. impresa 10-86 (PDF 1375):

> «For structural design of an eccentrically loaded foundation, a triangular or trapezoidal contact stress distribution based on factored loads shall be used for footings bearing on all soil and rock conditions.»

Caltrans BDP 11.2, §11.2.2.4.3 «Heel», pág. 11.2-47:

> «The pressure q5 and q6 applied to CD is the bearing stress at the bottom of the footing and is obtained in external stability analysis.»

**¿La cita de la sesión es exacta?** Sí, en numeral, página y texto. La regla por defecto es el peso entero («shall»), y la salvedad permite el método exacto. Caltrans lo aplica como dice el informe.

**¿Lo fija la hoja de ruta o una norma peruana?** No. La nota «Corregido (T-7c)» de §9.4, punto (5), dice «el talón con el peso entero de lo que tiene encima (11.6.1.2)»: describe lo que el código hace, no una exigencia. El Manual de Puentes no transcribe 11.6.1.2 (no hay coincidencia en el texto del PDF). Si se acepta el cambio, esa nota de la hoja de ruta hay que corregirla.

**Seguridad.** Es práctica reconocida, pero el ahorro depende de la combinación:

- En el ejemplo de Caltrans gobierna la combinación de factores **mínimos**: M_B = 125.9 kip·ft (Strength Ib, pág. 11.2-53) contra 121.4 (Strength Ia, pág. 11.2-50).
- En el Evento Extremo del mismo ejemplo la reacción bajo el talón solo cubre 2.674 ft de un talón de 11.125 ft (pág. 11.2-54). Con la resultante cerca del límite de excentricidad, el talón queda casi sin apoyo y el método exacto tiende al peso entero.
- El informe mide el momento como «máx. Res/EE» (Tabla 3.2), así que ya envuelve las combinaciones; pero lo hace con k_h reducido a 0.25 en nueve de los diez escenarios. Con k_h = k_h0 el ahorro será menor.

**Cuantificación del informe.** La Tabla Z da razones peso entero / exacto de 2.3 (E6-entrada, 154/66) a 13.1 (E5-salida, 1510/115). El LEEME dice «2.4 a 13»: el mínimo real es 2.3, y las razones de 8 a 13 salen de geometrías que están en el tope de 1.5·H_c y no cumplen la estabilidad (E5-salida, E7, E8). En las que cumplen, la razón es 2.3 a 4.3.

**Dictamen: ACEPTAR CON CONDICIÓN.** El método exacto rige solo si (a) se toma la envolvente de Resistencia I con γ máximos y con γ mínimos y de los dos casos del Evento Extremo I; (b) la reacción es la lineal de 10.6.5 con las cargas factoradas de **esa misma** combinación, sin tracción (despegue); (c) el peso entero se sigue imprimiendo como contraste. Razón: AASHTO lo permite literalmente y el ejemplo de Caltrans muestra que la combinación que gobierna no es la obvia.

---

## 3. Decisión 10 — Carga sobre la pantalla

**Texto de la fuente.** Caltrans BDP 11.2, §11.2.2.4.1 «Stem», pág. 11.2-27:

> «The lateral load on the stem results from the horizontal active earth pressure. Soil pressure is obtained by performing a trial wedge analysis along AB; see Figure 11.2.2-8.»

y pág. 11.2-28: «P_A is assumed to be applied at 1/3 AB from the bottom of the stem.» La Figura 11.2.2-8 (leída en imagen) muestra AB como el plano del trasdós de la pantalla, desde su corona hasta su arranque, con la cuña que sube por el relleno en talud hasta C.

En §11.2.2.4.3, pág. 11.2-47, el mismo documento separa los dos diagramas: «Earth pressure FEDD′E′ is what has been used in the external stability analysis. Earth pressure ABB′ is the earth pressure applied on the stem.»

Para el sismo, pág. 11.2-33: «The stem is subject to seismic soil load and stem inertial force. Note the inertial force of the soil over the heel is not included in the stem design.»

**¿La cita es exacta?** Sí. AASHTO no prescribe el plano de carga para el diseño estructural de la pantalla (no hay texto en 3.11.5 ni en 11.6 que lo fije), de modo que el respaldo es el ejemplo de Caltrans y la estática: el empuje del plano virtual por encima de la zapata se reparte entre la pantalla y el corte sobre la cara superior del talón.

**¿Lo fija la hoja de ruta o una norma peruana?** No. La ficha T7C-12 lo declara como cota superior.

**Seguridad.** Es la práctica estándar y es la carga que actúa sobre el concreto. Dos cautelas:

- La cuña debe llegar a la superficie **real**: el talud que sube detrás de la corona y la sobrecarga viva dentro de la cuña. Una cuña con relleno horizontal a la altura de la corona subestimaría.
- En el Evento Extremo la pantalla lleva además su propia inercia (k_h·W de la pantalla), como en Caltrans.

**Cuantificación del informe.** Tabla P: 1.5 a 4 veces. La razón de 4 (E2-entrada, 50.3 contra 12.5) es en parte un artefacto: el diagrama mide 2.62 m sobre una pantalla de 1.57 m porque la zapata salió de 1.00 m. Con zapata de 0.40 m la razón es 1.35 a 1.5 (E1-entrada 27.6/18.0; E9-salida 91.5/68.0). Ese es el efecto real una vez corregido el peralte.

**Dictamen: ACEPTAR CON CONDICIÓN.** Cuña de tanteo sobre el plano del trasdós de la pantalla, hasta la superficie real y con la sobrecarga; inercia de la pantalla en sismo; la regla actual impresa como contraste. Razón: práctica reconocida y físicamente correcta; la regla vigente carga la pantalla con presión que actúa por encima de su corona.

---

## 4. Decisión 11 — Factores φ de estabilidad

**Texto de la fuente.** AASHTO LRFD 11.5.7, pág. impresa 11-15 (PDF 1484):

> «For the strength limit state, the resistance factors provided in Table 11.5.7-1 shall be used for wall design, unless region-specific values or substantial successful experience is available to justify higher values. Resistance factors for geotechnical design of foundations that may be needed for wall support, unless specifically identified in Table 11.5.7-1, are as specified in Tables 10.5.5.2.2-1, 10.5.5.2.3-1, and 10.5.5.2.4-1.»

Tabla 11.5.7-1, pág. impresa 11-17 (PDF 1486), bloque «Mechanically Stabilized Earth Walls, Gravity Walls, and Semigravity Walls»: «Bearing resistance — Gravity and semigravity walls: 0.55»; «Sliding: 1.0».

Caltrans BDP 11.2 usa exactamente esas filas en su muro en voladizo: «φ = 0.55 for bearing resistance» (pág. 11.2-24) y «φτ = 1.0 for friction resistance» (pág. 11.2-26), de su «CA Table 11.5.7-1».

**¿La cita es exacta?** La de AASHTO, sí. La tabla identifica expresamente el portante y el deslizamiento del muro de semigravedad, de modo que la remisión a la Sección 10 no alcanza a esas dos filas.

**La del Manual de Puentes está mal leída.** El núm. 2.11.8.5, pág. impresa 510 (PDF 511), lleva la marca «(15.9.5 AASHTO)» y pertenece a 2.11.8 «Diseño de Fundación» de las **barreras de sonido**:

> «Los factores de resistencia para el diseño geotecnico de las fundaciones será como se especifica en la Tabla 2.8.1.1.12.6-1 (10.5.5.2.2-1 AASHTO) para fundaciones con zapatas extendidas, [...] y Tabla 11.5.7-1 para muros de contención permanentes.»

No es el artículo de muros. El artículo de muros del Manual, 2.8.1.1.12.6 «Deslizamiento (11.6.3.6 AASHTO)», págs. impresas 250–251 (PDF 251–252), dice lo contrario para el deslizamiento: define φτ como el «especificado en la tabla 2.8.1.1.12.6-1 (10.5.5.2.2-1 AASHTO)», la de zapatas (0.80 / 0.85). El Manual no transcribe la Tabla 11.5.7-1. La justificación actual del criterio (`fila_phi_estabilidad_cabezal`) describe bien esta tensión; el informe de ensayos, no.

**¿Lo fija la hoja de ruta o una norma peruana?** No. La hoja de ruta §9 (nota de T-7b, «Marco LRFD») deja las dos tablas en la ventana del [A], y §0.2 adopta «AASHTO LRFD de extremo a extremo». El Manual de Puentes respalda la fila de zapatas solo para el deslizamiento y por arrastre del texto de 10.6.3.4.

**Seguridad.** Con γ_EH = 1.50 y las cargas verticales a su factor mínimo, φτ = 1.0 equivale a un factor de seguridad al deslizamiento de 1.5, el mismo de E.050 39.13.6 a) que la hoja de ruta §9.3 imprime en paralelo. Con 0.80 equivale a ≈ 1.9. En el portante, 0.55 equivale a un FS del orden de 2.5, por debajo del 3.0 de E.050 (que informa y no rige); el marco ASD lo avisará. El comentario C11.5.7 (pág. 11-16) añade: «Smaller resistance factors should be used if site or material variability is anticipated to be unusually high». Mientras el suelo sea de prueba y no del EMS, esa salvedad aplica.

**Cuantificación del informe.** Tabla A, columnas 4 → 5: −0.10 a −0.90 m (E7-salida 5.18 → 4.28); E7-entrada pasa de no cumplir a cumplir.

**Dictamen: ACEPTAR.** El valor de archivo pasa a `muros_tabla_11_5_7`. Razón: es la letra de 11.5.7 para el muro de semigravedad y lo que hace el ejemplo de Caltrans. Hay que corregir la justificación: el Manual de Puentes no «remite a ella para muros»; su artículo de muros nombra la tabla de zapatas para el deslizamiento, y eso debe quedar declarado como la tensión que es.

---

## 5. Decisión 12 — Régimen de estabilidad y de armado

**Texto de la fuente.** AASHTO LRFD 11.6.5.4, pág. impresa 11-32 (PDF 1501):

> «For abutment walls and other walls that are considered nonyielding, the value of kh used to calculate seismic earth pressure shall be increased to 1.0kh0 [...]»

C11.6.5.4, misma página:

> «Examples of walls that may be nonyielding are integral abutments, abutment walls with structural wing walls, tunnel portal walls, and tied back cylinder pile walls.»
> «The use of a factor of 1.0 applied to kh0 is recommended for design where doubt exists that an abutment or wall can yield sufficiently to mobilize backfill soil strengths. In general, if the lack of ability of the wall to yield requires that the wall be designed for K0 conditions for the strength limit state, then a kh of 1.0kh0 should be used for seismic design.»

11.6.5.2.2, pág. impresa 11-28 (PDF 1497):

> «If the wall is free to move laterally under the influence of seismic loading and if lateral wall movement during the design seismic event is acceptable to the Owner, kh0 should be reduced [...] Where the wall is capable of displacements of 1.0 to 2.0 in. or more during the design seismic event, kh may be reduced to 0.5kh0 [...]»

C3.11.5.2, pág. impresa 3-120 (PDF 174), a favor de la recomendación:

> «For typical cantilevered walls over 5.0 ft high with structural grade backfill, calculations indicate that the horizontal movement of the top of the wall due to a combination of structural deformation of the stem and rotation of the foundation is sufficient to develop active conditions.»

**¿La sesión lee lo que dice?** Las citas son exactas, pero la conclusión invierte la carga de la prueba. El comentario pone el estribo con aleros estructurales como ejemplo de muro que puede no ceder y recomienda 1.0·k_h0 **cuando hay duda**. La recomendación propone lo contrario: ceder salvo que el Propietario declare los aleros.

**La premisa del LEEME es inexacta.** Dice «hoy la estabilidad con muro que cede (k_h = 0.5·k_h0)». El valor de archivo de `factor_muro_eleccion` es `sin_reduccion` (k_h = k_h0). La reducción la **declararon** los ensayos en nueve de los diez escenarios; solo E8 corre con el valor de archivo. Con los valores de archivo, estabilidad y armado ya usan el mismo k_h0. La incoherencia aparece cuando alguien declara la reducción y deja el armado en `no_cedente_k0`.

**¿Lo fija la hoja de ruta?** En parte, y en contra de la recomendación:

- Hoja de ruta §9.2: «Si el muro admitiera desplazamiento de 1.0 a 2.0 in o más [...], k_h = 0.5 · k_h0 = 0.25. **No asumirlo en un cabezal empotrado en terraplén.**»
- Hoja de ruta §9.4, punto (4): el armado con el empuje en reposo es «decisión del dueño del 2026-11-13» (ficha T7C-02), tomada porque el cabezal es monolítico con el barril y con los aleros.
- El Manual de Puentes 2.8.1.1.14.4, pág. impresa 256, traduce 11.6.5.4 con el mismo mandato.

**Seguridad.** El principio de un solo régimen es correcto: el mismo muro no puede ceder para la estabilidad y no ceder para el armado. Pero el régimen que hay que unificar depende del cabezal:

- En estática la diferencia es pequeña: la pantalla con K0 lleva 15 a 25 % más momento que con el activo (Tabla 3.2: 20.8 contra 18.1; 107.3 contra 85.9 kN·m/m).
- En sismo es grande y viene de k_h, no de K0: E1-salida, 232.1 kN·m/m con k_h0 contra 104.6 con k_h reducido.
- Aceptar 25 a 50 mm de desplazamiento en un cabezal unido a un tubo significa aceptar esa apertura en la junta tubo-cabezal. Esa aceptación es del Propietario (11.6.5.2.2) y no la puede dar un valor de archivo.

**Cuantificación del informe.** Con `cedente` la pantalla de 0.30 m pasa en E1, E9 y E10 (corridas `*_wi_cedente`). El informe no separa cuánto de eso es K0 → activo y cuánto es k_h0 → 0.5·k_h0.

**Dictamen: ACEPTAR CON CONDICIÓN (el principio sí, el valor por defecto no).**
- Un solo régimen, impuesto por una guardia: declarar la reducción de k_h con el armado en «no cede» es contradictorio y debe detenerse o avisarse.
- El valor de archivo sigue siendo el del muro que no cede (K0 y k_h0, sin reducción), porque el cabezal que la app propone lleva aleros monolíticos, que es el ejemplo literal de C11.6.5.4.
- «Cede» con k_h = 0.5·k_h0 es la alternativa declarada, y solo cuando concurren: aleros separados con junta y calculados como exentos (11.6.1.4, pág. 11-20), aceptación del desplazamiento por el Propietario, y altura de más de 5.0 ft (1.52 m).

Razón: la fuente recomienda 1.0·k_h0 en caso de duda y la hoja de ruta prohíbe asumir la reducción en este tipo de cabezal.

---

## 6. Decisión 13 — Punto de aplicación del incremento sísmico

**Texto de la fuente.** AASHTO LRFD 11.6.5.3, pág. impresa 11-30 (PDF 1499):

> «The equivalent pressure representing the total static and seismic active force (PAE) as calculated by either method should be distributed using the same distribution as the static earth pressure used to design the wall when used for external stability evaluations, as illustrated in Figure 11.6.5.1-1, but no less than H/3.»

C11.6.5.3, misma página:

> «Past practice [...] using an inverted trapezoid for the seismic component, with the seismic force located at 0.6h above the wall base [...] (Seed and Whitman, 1970). More recent research indicates the location of the resultant of the total earth pressure (static plus seismic) should be located at h/3 above the wall base [...] However, a slightly higher combined static/seismic resultant location (e.g., 0.4h to 0.5h) may be considered, since there is limited evidence the resultant could be higher, especially for walls in which the impact of failure is relatively high.»

Manual de Puentes 2.8.1.1.14.3, pág. impresa 256 (PDF 257), traduce el artículo: «será distribuido usando la misma distribución que la presión estática del terreno [...] pero no menor que H/3». Y su Apéndice A.11.3.1, págs. impresas 587–588 (PDF 588–589):

> «para diseño de muros de rutina, una ubicación de la resultante de la combinación estática/sísmica, es suficiente tomar la ubicación usada para diseño estático, h/3.»

Caltrans BDP 11.2, pág. 11.2-17: «PAE is assumed to act at 1/3 AB from the bottom of the footing.»

**¿La cita es exacta?** Sí, con dos matices que el LEEME aplana. El verbo es «should», no «shall». Y H/3 es un **piso**: la recomendación adopta el piso. El 0.6 actual sobre el incremento deja el total entre 0.4h y 0.5h, que es el rango que el comentario reserva a los muros de falla costosa.

**¿Lo fija la hoja de ruta o una norma peruana?** No lo fija: tanto 1/3 como 0.6 cumplen «no menor que H/3». Pero la norma peruana respalda la recomendación con más claridad que AASHTO, y el informe de ensayos no la cita.

**Seguridad.** Práctica reconocida para muros de rutina, que es lo que es un cabezal de alcantarilla. Dos cautelas:

- El artículo habla de la estabilidad externa de un muro que cede. Para el muro que no cede, C11.6.5.4 pide considerar la resultante a h/2; esa regla del armado no debe moverse con esta decisión.
- La implementación debe tomar el mayor entre el centroide del diagrama estático y h/3, no h/3 a secas: con talud y sobrecarga el centroide estático puede quedar por encima.

**Cuantificación del informe.** Tabla A, columna 6: −0.20 a −0.30 m de B en E1, E2, E3, E6 y E10 salida. Medido con k_h reducido.

**Dictamen: ACEPTAR CON CONDICIÓN.** Valor de archivo 1/3 para la estabilidad externa del muro que cede, tomando el mayor entre el centroide estático y h/3; h/2 se mantiene para el muro que no cede; la memoria imprime la sensibilidad a 0.4h–0.5h. Razón: es la letra de 11.6.5.3 y del Manual de Puentes para muros de rutina.

---

## 7. Decisión 14 — Desplante de la salida y socavación

**Texto de la fuente.** HEC-14 §5.1.3, pág. impresa 5-2:

> «If the culvert is installed with a headwall, the headwall should extend to a depth equal to the maximum depth of scour.»

HEC-14 §1.2, pág. impresa 1-2, pone la hoya aceptada y el disipador como **alternativas**:

> «Step 3. [...] If the size of the scour hole is acceptable, the designer should document the size of the expected scour hole for maintenance and note the monitoring requirements. If the size of the scour hole is excessive, the designer should evaluate energy dissipators (step 4).»

HEC-14 §10.2, págs. impresas 10-17 y 10-18, sobre el delantal de enrocado:

> «However, if they are too short, or otherwise ineffective, they simply move the location of potential erosion downstream.»
> «To ensure continued satisfactory operation, maintenance personnel should inspect them after major flood events. If repeated severe damage occurs, the location may be a candidate for extending the apron or another type of energy dissipator.»

AASHTO LRFD 12.6.5, pág. impresa 12-20 (PDF 1658):

> «For structures placed over erodible deposits, a cut-off wall or scour curtain, extending below the maximum anticipated depth of scour or a paved invert, shall be used. The footings of structures shall be placed not less than 2.0 ft below the maximum anticipated depth of scour.»

AASHTO LRFD 10.6.1.2, pág. impresa 10-52 (PDF 1341): «spread footings shall be located to bear below the maximum anticipated depth of scour».

Manual de Hidrología MTC, núm. 4.1.1.3.7 c), págs. impresas 79–80: recomienda «la protección del cauce natural mediante la construcción de emboquillados de piedra, enchapado de rocas acomodadas u otros tipos de revestimientos». No da profundidad de desplante para el cabezal.

**¿La sesión lee lo que dice?** El argumento de «doble protección» tiene base: en el procedimiento de HEC-14 la hoya del Capítulo 5 es la de la salida **sin** disipador, y 5.1.3 pertenece a esa rama. Pero la recomendación no trae cita para lo que propone a cambio. Ninguna fuente del repositorio de normas da la profundidad de una «hoya protegida»: HEC-14 no la cuantifica para el delantal de 10.2, y la poza de 10.1 (que sí tiene un h_s) está fuera del alcance (hoja de ruta, Fase 6). Adoptarla obligaría a inventar un valor, que es lo que CLAUDE.md prohíbe.

**¿Lo fija la hoja de ruta o una norma peruana?** No. El margen es [C] con ventana 0 a 0.6096 m (`margen_zapata_bajo_socavacion_m`), y que la zapata del cabezal sea una de las «footings of structures» de 12.6.5 es lectura declarada del proyecto.

**Seguridad.** Aquí la recomendación es la menos sostenida de las seis:

- El delantal depende del mantenimiento y HEC-14 admite que puede fallar o trasladar la erosión. El desplante profundo no depende de nada.
- La app no diseña el filtro (requisito declarado, no dimensionado) y `M6_proteccion.py` advierte que sin filtro el enrocado se socava.
- La hoya de HEC-14 no incluye la degradación general del cauce (Cap. 5, pág. 5-1).
- AASHTO 12.6.5 no da crédito al enrocado: exige la pantalla bajo la socavación **o** solera pavimentada, y además el margen de 2.0 ft.
- La consecuencia de errar es el descalce del cabezal de salida y la erosión del terraplén.

Lo que sí es sostenible es el otro extremo de la ventana ya declarada: margen 0, que es la lectura literal de HEC-14 5.1.3 y de AASHTO 10.6.1.2. La profundidad declarada por un estudio del cauce (`profundidad_socavacion_estimada_m`) ya existe y gana; esa es la vía para quien tenga un valor con protección.

**Cuantificación.** El informe no mide esta decisión. Por la Tabla M-a (barrido de socavación en E1), bajar 0.61 m la altura de la salida lleva H_c de 3.83 a ≈ 3.2 m, B de 3.08 a ≈ 2.6 m y e_z de 0.80 a 0.40 m. Es una interpolación mía sobre su tabla, no una corrida.

Conviene saber que el desplante ya acumula tres decisiones conservadoras antes del margen: duración de 360 min en vez de 30 (la hoya crece con t), profundidad medida desde el fondo del cauce receptor y no desde la solera, y la envolvente de coeficientes entre filas.

**Dictamen: ACEPTAR CON CONDICIÓN.** Se acepta bajar el margen (hasta 0, dentro de la ventana) como decisión del dueño; se rechaza la «hoya protegida» mientras no exista una profundidad con fuente o declarada por un estudio. Razón: HEC-14 5.1.3 sostiene el margen 0; nada sostiene una hoya reducida por el delantal.

---

## 8. Hallazgos adicionales

**Citas mal leídas o imprecisas**

1. **Manual de Puentes 2.11.8.5 (decisión 11).** Es el artículo de fundaciones de barreras de sonido (15.9.5 AASHTO), pág. 510. El artículo de muros, 2.8.1.1.12.6 (págs. 250–251), remite el φτ del deslizamiento a la tabla de zapatas. La frase «el Manual de Puentes 2.11.8.5 remite a ella» no debe entrar a la justificación del criterio.
2. **Premisa de la decisión 12.** «Hoy k_h = 0.5·k_h0» no es el valor de archivo (`sin_reduccion`). Es lo que los ensayos declararon.
3. **«C10.6.5» en §1.2 del informe.** El «shall» de la presión triangular o trapezoidal está en el artículo 10.6.5, no en su comentario. Página correcta (10-86).
4. **«2.4 a 13 veces» (decisión 9).** El mínimo de la Tabla Z es 2.3, y el extremo alto procede de geometrías que no cumplen la estabilidad.
5. **«1.5 a 4 veces» (decisión 10).** El extremo alto depende de las zapatas infladas que la propia corrección de los defectos elimina; el efecto estable es 1.35 a 1.5.
6. **H-9 del informe** presenta H/3 como «la especificación»: el artículo dice «should» y «no less than», es un piso recomendado.
7. **H-7 del informe** corta la cita de 11.5.7 antes de «unless region-specific values or substantial successful experience is available to justify higher values». No cambia el sentido.

**Defectos del informe de ensayos que afectan a las decisiones**

8. **Casi todo el efecto medido es con k_h reducido.** Nueve de diez escenarios declaran la reducción. Con el valor de archivo (E8, k_h = 0.50) el propio diseño a mano necesita B ≈ 1.8 a 2.0·H_c y la app no encuentra zapata dentro del tope. La decisión que más pesa en el cabezal a PGA 0.50 g es `factor_muro_eleccion`, y no está entre las seis.
9. **Caltrans reduce k_h con comprobación.** En su ejemplo k_h = 0.28 sale de k_h0 = 0.70 y se verifica el desplazamiento (5.4 in < 6 in admisibles, pág. 11.2-20). El ejemplo respalda un solo régimen para estabilidad y pantalla, pero con el desplazamiento calculado y aceptado, no supuesto.
10. **Efecto combinado no medido por separado en seguridad.** La Tabla A muestra que 11 y 13 más la punta libre llevan B de 2.08 a 1.55 m en E1-entrada (−25 %) y de 4.78 a 3.70 m en E4-salida (−23 %). Cada reducción tiene fuente, pero el informe no imprime el factor de seguridad equivalente del diseño resultante en el marco ASD de E.050; conviene pedirlo antes de cambiar los valores de archivo.
11. **La norma peruana no se usó donde ayudaba.** El Manual de Puentes 2.8.1.1.14.3 y A.11.3.1 respaldan la decisión 13 de forma directa y el informe solo cita AASHTO.

**Consecuencias documentales si el dueño acepta**

12. La hoja de ruta §9.4 (5) («el talón con el peso entero») y §9 («Marco LRFD», fila de φ) describen el estado actual y hay que corregirlas.
13. La ficha T7C-02 registra una decisión del dueño del 2026-11-13 que la decisión 12 revierte; si se acepta la alternativa «cede», debe quedar dicho que se revierte y por qué.

**Lo que no verifiqué**

- No recalculé ningún número de los ensayos ni corrí la app.
- La página impresa de C3.11.1 (3-117) la tomo del registro del repositorio; el texto sí lo leí en el volcado.
- Las ecuaciones y tablas de AASHTO citadas aquí son de texto; solo leí en imagen la pág. 11-26 de AASHTO y la Figura 11.2.2-8 de Caltrans.
