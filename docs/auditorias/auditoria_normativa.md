# Auditoría normativa externa — verificación cita por cita contra `normas/`

| | |
|---|---|
| **Commit auditado** | `71b134fb5d4aff4a1c53062ebea99d2674d6e596` |
| **Suite sobre ese árbol** | 725 `passed` + 1 `skipped` (726 `collected`) |
| **Fecha** | 2026-08-26 |
| **Alcance** | El manifiesto de citas fila por fila, las transcripciones `[N]`, las analogías `[N→]`, los vacíos verificados de §14, las trampas de vocabulario, el reparto dato-de-sitio / constante, y la memoria exportada — contra los **13 PDF** de `normas/`, tres de ellos subidos para esta auditoría |
| **Resultado** | **93 hallazgos** — 11 críticas · 37 altas · 32 medias · 4 bajas · 9 OK. Por veredicto: **75 CONTRADICE · 15 CONFIRMA · 3 NO VERIFICABLE** |
| **Regla de la auditoría** | Solo lectura. **No se corrigió nada.** El árbol de trabajo quedó sin modificar en el commit auditado |

## Recuento

| Severidad | | Veredicto | |
|---|---|---|---|
| CRÍTICA | 11 | CONTRADICE | 75 |
| ALTA | 37 | CONFIRMA | 15 |
| MEDIA | 32 | NO VERIFICABLE con lo adjunto | 3 |
| BAJA | 4 | | |
| OK | 9 | | |

Las **9 fichas `OK-nn`** no son defectos: son las verificaciones más consecuentes que
**confirmaron** contra la fuente y se dejan escritas porque un revisor necesita saber qué
se comprobó y salió bien, no solo qué falló. Los otros 6 veredictos `CONFIRMA` viven
dentro de fichas con severidad, donde una parte del bloque confirma y otra no.

**Convención de severidad** (la misma que `auditoria_matematica.md` y `auditoria_sistema.md`):

| | |
|---|---|
| **CRÍTICA** | Cita falsa o transcripción `[N]` errada que un revisor puede abrir en el PDF y rechazar en el acto, o que rompe el conservadurismo declarado en el flujo activo |
| **ALTA** | Cita o vacío que no resiste el contraste con la fuente, atribución de numeral equivocada, o divergencia entre lo que el repo afirma y lo que el documento dice, sin daño numérico demostrado hoy |
| **MEDIA** | Discrepancia documental, de alcance o de etiqueta: el número es defendible, la cita o la etiqueta no |
| **BAJA** | Referencia corrida, redondeo o matiz de redacción |
| **OK** | Verificado correcto contra la fuente |

## Método

Se extrajo el texto de los trece PDF de `normas/` —incluidos los tres subidos para esta
auditoría— y se abrió **cada numeral citado sobre su página impresa real**, aplicando el
desfase de cada documento. Las normas escaneadas sin capa de texto (AASHTO M 36) o con la
fuente cifrada (ASTM A760) se OCRearon a 300 dpi antes de leerlas.

| Documento | Estado | Desfase impresa↔PDF |
|---|---|---|
| Manual de Hidrología, Hidráulica y Drenaje (MTC) | texto nativo | impresa = pdf − 3 |
| Manual de Suelos, Geología, Geotecnia y Pavimentos (MTC) | texto nativo | impresa = pdf − 1 |
| Manual de Puentes (MTC) | texto nativo | impresa = pdf − 1 |
| EG-2013, Capítulo V | texto nativo | impresa = pdf − 8 |
| NTE E.050 · E.060 · E.030 | texto nativo | impresa = pdf |
| AASHTO LRFD 9.ª ed. (2020) | texto nativo | numeración por sección |
| HDS-5 2.ª ed. SI (1985) | texto nativo | numeración por capítulo |
| HDS-5 3.ª ed. (FHWA-HIF-12-026, abril 2012) | texto nativo | numeración por capítulo |
| **AASHTO M 170M-04** *(nuevo)* | OCR 300 dpi + lectura visual | — |
| **AASHTO M 36-03 (2007)** *(nuevo)* | OCR 300 dpi (sin capa de texto) | — |
| **ASTM A760/A760M-10** *(nuevo)* | OCR 300 dpi (fuente cifrada) | — |

- Ningún hallazgo se aceptó por la sola afirmación de un auditor: cada uno pasó por un
  **refutador adversarial** con instrucción de derribarlo volviendo al PDF y al código por
  su cuenta, y de refutar por defecto ante cualquier duda razonable. Dos hallazgos que yo
  mismo había redactado (`ESPESOR_TEMPERATURA_DOS_CARAS = 0.250` y el paso `D_PASO = 0.15`)
  se cayeron en esa contrastación: el repo tenía razón y las fichas se retiraron antes de
  publicarse.
- **La fase de refutación quedó incompleta.** De 95 refutadores lanzados sobre el primer
  lote y 48 sobre el segundo, se cerraron 19 y 20 respectivamente antes de que la sesión
  se cortara por límite de créditos. El temario íntegro, con el estado exacto de cada
  ítem, está volcado en `temario_refutar_95.json` y `temario_refutar_48.json` de esta
  misma carpeta. **Los 93 hallazgos de abajo son los que sobrevivieron a la verificación
  del auditor principal**, que releyó cada uno contra la página impresa; lo que falta es
  la segunda opinión adversarial sobre 104 de ellos.
- El mensaje pedía cuatro archivos de normativa y llegaron tres. Lo que falta es lo que
  aparece en la sección final de filas fuera de alcance.
- La suite del repositorio pasa en este SHA: **725 passed, 1 skipped**. Ninguno de los
  defectos de abajo lo detecta un test, y esa es parte del hallazgo.

---

## 1. Críticas

| ID | Sev | Veredicto | Documento | Afirmación del repo (archivo:línea) | Qué dice el PDF (documento, página) |
|---|---|---|---|---|---|
| `PUE-01` | CRÍTICA | CONTRADICE | Manual de Puentes | **El numeral que sostiene la sobrecarga de tráfico en el trasdós es «Aparatos de Apoyo»** — `SOBRECARGA_TRASDOS_H_EQ = 0.60` m de relleno equivalente, atribuido al **num. 2.1.4.3.9, pág. 91**. El mismo numeral viaja a la memoria dentro de `NUMERAL_SOBRECARGA_TRASDOS` y sostiene `presion_sobrecarga_trasdos()`: p = γ·0.60·k_a.<br>*src/constantes_normativas.py:235 · :261 · src/modulos/M9_cabezal.py:588 · manifiesto §3* | El num. 2.1.4.3.9 se titula **«Aparatos de Apoyo»** y trata de dispositivos de apoyo de la superestructura; remite a AASHTO Sección 14. No menciona relleno, trasdós ni sobrecarga. · El 0.60 m está en **num. 2.4.2.2 «Cargas de Suelo: EH, ES, y DD»**: «Cuando se prevea tráfico a una distancia horizontal, medida desde la parte superior de la estructura, menor o igual a la mitad de su altura, las presiones serán incrementadas añadiendo una sobrecarga vertical **no menor que** la equivalente a 0,60 m de altura de relleno.» La condición «tráfico a ≤ H/2» que el código sí declara es correcta. El «no menor que» (es un mínimo, no un valor) y la exención por losa de aproximación no se recogen.<br>*Manual de Puentes, num. 2.1.4.3.9 → pág. impresa 91-92 (PDF 92-93) · num. 2.4.2.2 → pág. impresa 102 (PDF 103)* |
| `PUE-02` | CRÍTICA | CONTRADICE | AASHTO LRFD | **Bajo la Vía 1 declarada, 0.60 m es la fila menos conservadora de la tabla y no aplica a ningún cabezal de este proyecto** — El proyecto declara en Sec. 0.2 la **Vía 1: AASHTO LRFD de extremo a extremo** para el diseño estructural, con E.060 solo para durabilidad y recubrimientos. Sobre esa base adopta h_eq = 0.60 m sin dependencia de la altura del muro.<br>*src/constantes_normativas.py:235 · src/modulos/M9_cabezal.py:588 · docs/hoja_de_ruta_alcantarillas_v8.md (Sec. 0.2)* | **Tabla 3.11.6.4-1 «Equivalent Height of Soil for Vehicular Loading»**: altura de estribo 5.0 ft → h_eq 4.0 ft; 10.0 ft → 3.0 ft; ≥ 20.0 ft → 2.0 ft. Los 0.60 m ≈ 2.0 ft son la fila de **muros de 20 ft (6.1 m) o más**. Un cabezal de 2–4 m exigiría 3.0–4.0 ft = 0.91–1.22 m, entre 1.5× y 2× lo adoptado. El comentario de AASHTO añade que los valores tabulados «are generally greater than the traditional 2.0 ft of earth load historically used». · Y el Manual de Puentes **no incorpora AASHTO 3.11.6**: su num. 2.4.4.1 «Empuje del Suelo» va de 2.4.4.1.1 a 2.4.4.1.5.4 y salta a 2.4.5. Por eso el 0.60 m plano del Manual y la tabla de AASHTO conviven sin que el repositorio declare cuál gobierna.<br>*AASHTO LRFD 9.ª ed., Tabla 3.11.6.4-1 y C3.11.6.4, Sección 3 · Manual de Puentes, índice de 2.4.4.1* |
| `PUE-03` | CRÍTICA | CONTRADICE | Manual de Puentes | **El factor mínimo de EV no corresponde a ninguna fila de la tabla, y el que aplica al cabezal es más exigente** — `factores_carga_aashto["Resistencia I"]["EV"] = {max: 1.35, min: 0.90}`, etiqueta `[C]`. Y no es un descuido de tecleo: la justificación del criterio **lo afirma expresamente** — «la tabla fuente da EV mínimo **0.90, no 1.00**».<br>*src/criterios_adoptados.py:1343 (valor) y :1379-1380 (la afirmación)* | En la **Tabla 2.4.5.3.1-2 (= 3.4.1-2 AASHTO)**, EV se desglosa por tipo de elemento y *ninguna fila* es (1.35, 0.90): · · Estabilidad global — 1.00 / N/A · · **Muros y estribos de retención — 1.35 / 1.00** · · Estructura rígida enterrada — 1.30 / 0.90 · · Pórticos rígidos — 1.35 / 0.90 · · Estructuras flexibles enterradas — 1.50 · 1.30 · 1.95 / 0.90 · El par transcrito toma el máximo de «muros y estribos de retención» y el mínimo de otra fila. Para un cabezal —que M9 modela como muro de contención— el mínimo es **1.00**. Usar 0.90 rebaja un 10 % el peso estabilizante de tierra en E2 (volteo), E3 (deslizamiento) y V7 (flotación), que es la dirección insegura.<br>*Manual de Puentes, Tabla 2.4.5.3.1-2, pág. impresa 143 (PDF 144) · AASHTO LRFD 9.ª ed., Tabla 3.4.1-2, pág. 3-18* |
| `PUE-04` | CRÍTICA | CONTRADICE | Manual de Puentes | **El vacío de factores de carga se declara sobre las páginas que contienen las tablas** — El manifiesto declara `factores_carga_aashto = None` — «vacío que bloquea toda combinación de carga» — con la razón de que «el Manual nombra las combinaciones y **no transcribe las Tablas 3.4.1-1/-2**», citando **num. 2.4.5.3, págs. 140-143**. `constantes_normativas.py:254-259` repite el argumento.<br>*docs/manifiesto_citas.md §3, §8 y §12 · src/constantes_normativas.py:254-259* | El Manual **sí las transcribe, completas y con sus valores**, dentro del rango de páginas que el propio repositorio cita: · · **Tabla 2.4.5.3.1-1 «Combinaciones de Carga y Factores de Carga» (3.4.1-1 AASHTO)** — pág. impresa 143 · · **Tabla 2.4.5.3.1-2 «Factores de carga para cargas permanentes, γp» (3.4.1-2 AASHTO)** — pág. impresa 143 · · **Tabla 2.4.5.3.1-3 (3.4.1-3 AASHTO)** — pág. impresa 144 · Además el **código ya no está vacío**: `factores_carga_aashto` tiene hoy valor y etiqueta `[C]`. El manifiesto describe un estado del repositorio que ya no existe.<br>*Manual de Puentes, num. 2.4.5.3 pág. impresa 140; Tablas en págs. impresas 143-144 (PDF 144-145)* |
| `PUE-05` | CRÍTICA | CONTRADICE | Manual de Puentes | **«Vacío absoluto sobre conductos enterrados» — el Manual los trata en al menos cinco lugares** — Afirmación negativa repetida en §3, §14.a y el código: el Manual de Puentes «nunca incorporó la Sección 12 de AASHTO LRFD» y por eso hay «**vacío absoluto sobre conductos enterrados**».<br>*src/criterios_adoptados.py:1068-1073 · src/modulos/M8_estructural.py:35-36, :199-200, :209-210 · manifiesto §3 y §14.a* | La conclusión estrecha —que no existe un capítulo equivalente a la Sección 12— es cierta. El «vacío absoluto» no lo es. El Manual fija, sobre alcantarillas y estructuras enterradas: · · **num. 2.4.3.3.2 «Componentes Enterrados» (3.6.2.2 AASHTO)**, pág. 109: IM = 33(1.0 − 0.125·DE) ≥ 0 %, con DE = profundidad mínima de cubierta de tierra. · · **Tabla 2.4.5.3.1-2**, pág. 143: filas propias de «Estructura rígida enterrada» y «Estructuras flexibles enterradas» (alcantarillas cajón metálicas, termoplásticas). · · **num. 2.8.1.3A.6.2**, pág. 280: cortante en losas de alcantarilla cajón con menos / más de 2.0 ft (600 mm) de relleno. · · **num. 2.9.1.4.6.4.6**, pág. 362: armadura de distribución según la altura de relleno sobre la losa. · · **Tabla 2.9.1.5.5.3-1**, pág. 378: recubrimiento para «Alcantarillas de cajón de concreto prefabricados». · · «Alcantarillas Rectangulares», pág. 106, y la exención sísmica de la pág. 121.<br>*Manual de Puentes, págs. impresas 106, 109, 121, 143, 280, 362, 378* |
| `PUE-06` | CRÍTICA | CONTRADICE | Manual de Puentes | **La «evidencia de índice» que sostiene el vacío es falsa: 2.11 no es «Muros de Contención y Estribos»** — «↻ **Afirmación negativa, ahora con la evidencia de índice**: su índice **salta de 2.11 (Muros de Contención y Estribos) a 2.12 (Disposiciones Constructivas)** — no existe el equivalente de la Sec. 12».<br>*src/criterios_adoptados.py:1068-1073 · docs/manifiesto_citas.md §3 y §14.a punto 2* | El índice real de la Parte 2 es: 2.8 **Cimentaciones** (10 AASHTO) · 2.9 Superestructuras · 2.10 Requisitos para Apoyos (14.6 AASHTO) · **2.11 «DISEÑO DE BARRERAS DE SONIDO» (15 AASHTO)**, pág. 505 · 2.12 «Disposiciones Constructivas», pág. 513. · 2.11 *no* es «Muros de Contención y Estribos»; los muros y estribos viven dentro de **2.8 Cimentaciones** — que es justamente de donde el propio repositorio saca 2.8.1.1.14.2 y 2.8.1.3.1.2c. Y la numeración del Manual no sigue la de AASHTO (2.8↔10, 2.10↔14.6, 2.11↔15), de modo que «entre 2.11 y 2.12 debería estar la Sec. 12» no se sostiene como inferencia.<br>*Manual de Puentes, índice de la Parte 2 y cuerpo en págs. impresas 505 y 513* |
| `HID-01` | CRÍTICA | CONTRADICE | Manual de Hidrología | **El 9.8 de Laushey no está en el numeral que lo respalda — y el Manual sí escribe 9.8 donde el código usa 9.81** — `G_LAUSHEY = 9.8` en el archivo que admite «solo constantes `[N]` con numeral verificado», con el comentario «**g tal como lo escribe la Sec. 4.1.1.3.7 c) junto a su fórmula de d50**». Toda la separación entre `G_LAUSHEY = 9.8` y `constantes_fisicas.G = 9.81` se justifica con esa frase.<br>*src/constantes_normativas.py:51-57 · src/constantes_fisicas.py:19-31 · manifiesto §1* | El num. 4.1.1.3.7 c) da la fórmula (49) d₅₀ = V²/(3.1 g) y define únicamente: «g : Aceleración de la gravedad (m/s²)» No escribe ningún decimal. El «9.8» lo escribe la *hoja de ruta* (línea 495), no el Manual. · El Manual sí escribe «g = 9.8 m/s²» en otros dos sitios: **num. 3.12.5** (pág. 63), para la velocidad crítica Vc = √(yc·g), y en la velocidad de corte de socavación (HEC-18). Es decir, escribe 9.8 exactamente para el tirante crítico, que es donde M4 usa 9.81.<br>*Manual de Hidrología, num. 4.1.1.3.7 c) pág. impresa 80 (PDF 83) · num. 3.12.5 pág. impresa 63 (PDF 66)* |
| `VAC-01` | CRÍTICA | CONTRADICE | AASHTO LRFD | **El vacío de altura mínima de relleno no está cerrado: AASHTO Sec. 12 la tabula, y 0.30 m queda por debajo** — §14.a declara **vacío verificado**: «se fue a buscar a todas las fuentes donde podía estar y **no está en ninguna**», tras agotar tres fuentes (normas de producto, Manual de Puentes, EG-2013). Sobre eso se adopta 0.30 m por analogía `[N→]` para concreto y TMC, y se anota que el típico de concreto «es 1.0 ft (~0.305 m)» y que la verificación «debería *confirmarla*, no corregirla».<br>*docs/manifiesto_citas.md §14.a · src/criterios_adoptados.py:1074-1108* | **Art. 12.6.6.3 «Minimum Cover», Tabla 12.6.6.3-1** tabula la cobertura mínima por tipo de conducto: · · **Reinforced Concrete Pipe**, bajo zona no pavimentada o pavimento flexible — Bc/8 (o √Bc/8, el mayor) ≥ **12.0 in**; bajo pavimento rígido — 9.0 in · · **Corrugated Metal Pipe** — S/8 ≥ **12.0 in** · · **Thermoplastic Pipe** — ID/8 ≥ 12.0 in sin pavimentar; **ID/2 ≥ 24.0 in bajo pavimento** · Consecuencias: (1) el vacío es del corpus *peruano*, no del cuerpo normativo que el proyecto declara como Vía 1, y el documento está en el propio repositorio; (2) 0.30 m queda **5 mm por debajo** del piso de 12 in; (3) el valor que gobierna no es el piso sino Bc/8, que para un tubo de concreto de 2.40 m (Bc ≈ 2.9 m) da ≈ 0.36 m, un 20 % más que lo adoptado.<br>*AASHTO LRFD 9.ª ed., Art. 12.6.6.3 y Tabla 12.6.6.3-1, pág. 12-22 (PDF 1660)* |
| `SUE-01` | CRÍTICA | CONTRADICE | Manual de Suelos | **El Cuadro 4.1 sí dice cuándo son 4 calicatas y cuándo 6 — y la cita «4 (o 6)» no existe** — «El Cuadro admite además 6 en vez de 4 para autopistas con 4 carriles por sentido, y **“4 (o 6)”** para duales. Ese 6 NO se transcribe aquí: el Cuadro **lo da como alternativa sin decir cuándo aplica cada una**, de modo que la elección entre 4 y 6 no es `[N]`.»<br>*src/constantes_normativas.py:165-172* | El Cuadro 4.1 fija la condición de forma explícita, con la misma redacción para autopistas y para duales/multicarril: «Calzada 2 carriles por sentido: 4 calicatas × km × sentido · Calzada 3 carriles por sentido: 4 calicatas × km × sentido · Calzada 4 carriles por sentido: 6 calicatas × km × sentido» No es una alternativa abierta: es función determinada del número de carriles por sentido, de modo que el 6 es `[N]` y omitirlo exige declarar que esta vía tiene ≤ 3 carriles por sentido — cosa que el propio comentario dice que no está cerrada. Además la cadena entrecomillada «`4 (o 6)`» no aparece en el Cuadro (0 coincidencias en el documento).<br>*Manual de Suelos, num. 4.2, Cuadro 4.1, pág. impresa 28 (PDF 29)* |
| `PRO-01` | CRÍTICA | CONTRADICE | ASTM A760 / AASHTO M36 | **El tope de 2.10 m para TMC no está en la norma que lo respalda: A760 tabula hasta 3600 mm** — `D_MAX["tmc"] = 2.10` m, atribuido a «AASHTO M36 / ASTM A760», bajo el rótulo «topes por norma de producto - **VERIFICAR**». Superado el tope, M2 devuelve «material descartado por diámetro requerido».<br>*src/constantes_normativas.py:132-136 · src/criterios_adoptados.py, `diametros_normalizados`* | La **Tabla 1 «Tamaños de tubería»** de A760/A760M-10 (la norma que se declara equivalente a AASHTO M 36/M 36M) tabula diámetros nominales de **150 mm hasta 3600 mm**: 150, 200, 250, 300, 375, 450, 525, 600, 675, 750, 825, 900, 1050, 1200, 1350, 1500, 1650, 1800, 1950, **2100**, 2250, 2400, 2550, 2700, 2850, 3000, 3150, 3300, 3450, 3600. Los 2100 mm son un tamaño más de la serie, no un máximo. La norma citada no sostiene el tope, y el tope descarta el TMC en todo diseño que pida más de 2.10 m.<br>*ASTM A760/A760M-10, Tabla 1, pág. 2 del PDF (OCR 300 dpi)* |
| `PRO-02` | CRÍTICA | CONTRADICE | AASHTO M 170M | **El tope de 2.70 m para concreto reforzado tampoco es el de M 170M** — `D_MAX["concreto_reforzado"] = 2.70` m, atribuido a «ASTM C76 / AASHTO M170».<br>*src/constantes_normativas.py:132-136* | Las Tablas 1 a 5 de M 170M-04 (Clases I a V) tabulan diámetros internos designados de **300 mm a 3600 mm**. La Tabla 1 (Clase I) llega a 3450 mm y las Tablas 3 y 4 listan filas hasta 3600 mm. Por encima de ~2700 mm varias clases traen guiones —diseño especial, §7.2— pero el diámetro sigue tabulado y la norma prevé expresamente «special designs for sizes and loads beyond those shown in Tables 1 to 5». 2.70 m puede defenderse como «el mayor con armadura tabulada en todas las clases», pero eso no es lo que el código dice, y el código lleva la marca `VERIFICAR` sin numeral.<br>*AASHTO M 170M-04, Tablas 1-5 (PDF págs. 3, 4, 6, 8, 10) y §7.2* |

## 2. Altas

| ID | Sev | Veredicto | Documento | Afirmación del repo (archivo:línea) | Qué dice el PDF (documento, página) |
|---|---|---|---|---|---|
| `PRO-03` | ALTA | CONTRADICE | M 170M · M 36 · A760 | **La exclusión de alturas de relleno no está en la «Nota 1» de las tres normas, y la fórmula citada es de una sola** — «AASHTO M 170M, M 36 y ASTM A760 no contienen alturas de relleno admisibles. Su **Nota 1** las excluye de forma expresa: son especificaciones de **fabricación y compra**...». Atribución declarada: «**Nota 1 de cada norma**».<br>*src/criterios_adoptados.py:1113-1121 · docs/manifiesto_citas.md §9 y §14.a punto 1* | El **fondo es correcto** para las tres: ninguna da alturas de relleno. La **atribución es falsa en dos de tres**. · · **M 170M** — sí es la Nota 1: «This specification is a *manufacturing and purchase specification only*, and does not include requirements for bedding, backfill, or the relationship between field load condition and the strength classification of pipe.» ✔ · · **M 36** — la exclusión está en **§1.3**: «This specification does not include requirements for bedding, backfill, or the relationship between earth cover load and sheet thickness of the pipe.» Su Nota 1 habla de láminas con fibra de aramida y post-recubrimiento asfáltico. No usa la fórmula «manufacturing and purchase specification only». · · **A760** — la exclusión está en **§1.4**, con el mismo texto. Su Nota 1 es también la de la fibra de aramida.<br>*M 170M-04 Nota 1 (PDF pág. 1) · M 36-03(2007) §1.3 (PDF pág. 2) · A760/A760M-10 §1.4 (PDF pág. 1)* |
| `AAS-01` | ALTA | CONTRADICE | AASHTO LRFD | **Los 75 mm de recubrimiento AASHTO dependen de una categoría de acero que no se declara** — `recubrimiento_aashto_mm = {contra_suelo: 75.0, suelo_intemperie_ge_3_4: 75.0, suelo_intemperie_le_5_8: 75.0}`, etiqueta `[C]`, con la conclusión de que «AASHTO gobierna en los tres casos por la regla del mayor» frente a los 70/50/40 mm de E.060. Justificación: la categoría «ambiente costero» = 75 mm, «**uniforme sin importar el diámetro de barra**».<br>*src/criterios_adoptados.py, criterio `recubrimiento_aashto_mm` · src/modulos/M9_cabezal.py:1170-1215* | La **Tabla 5.10.1-1 «Minimum Cover for Main Reinforcing Steel (in.)»** tiene tres columnas por **Reinforcing Material Category**, no una: · · Coastal — **A 3.0 in · B 2.0 in · C 2.0 in** · · Cast against earth — A 3.0 · B 2.0 · C 2.0 · · Direct exposure to salt water — A 4.0 · B 2.5 · C 2.5 · Al pie: «Category A — Uncoated reinforcing steel meeting AASHTO M 31M/M 31 · Category B — Epoxy coated or galvanized meeting ASTM A775/A775M · Category C — Materials meeting AASHTO M 334M/M 334». · Los 75 mm son la Categoría **A** (y 3.0 in son 76.2 mm, redondeados a la baja sin declararlo). Con acero galvanizado o epóxico —opción natural en un corredor salino con freático somero— AASHTO daría 2.0 in = 50.8 mm y la regla del mayor la ganaría **E.060**, invirtiendo la conclusión. La categoría no se declara en ninguna parte.<br>*AASHTO LRFD 9.ª ed., Tabla 5.10.1-1, pág. 5-169 (PDF 528). La página que cita el criterio es correcta.* |
| `PUE-07` | ALTA | CONTRADICE | Manual de Puentes | **«La tabla del factor de muro» no es una tabla: el numeral solo autoriza la reducción a 0.5** — `FACTOR_MURO_TABLA = {rigido: 1.0, desplazable: 0.5}` en `constantes_normativas.py`, con el argumento de que «**las DOS filas son [N]: el numeral las fija**» y que solo la elección entre ellas es `[A]`. Todo el reparto tabla/elección del manifiesto de datos-vs-constantes (fila 3) descansa en esa lectura.<br>*src/constantes_normativas.py:241-250 · docs/manifiesto_datos_proyecto_vs_constantes.md* | El num. 2.8.1.1.14.2.2 no presenta ninguna tabla. Dice: «Donde el muro es capaz de desplazamientos de 1.0 a 2.0 in o más durante el evento sísmico de diseño, kₕ puede ser reducido a 0.5 kₕ₀ sin llevar a cabo un análisis de la deformación mediante el método Newmark…» Hay **un solo valor normativo, 0.5**, condicionado a capacidad de desplazamiento. El 1.0 es la ausencia de reducción (kₕ = kₕ₀), no una fila tabulada. El rango del código, «muros que admiten 25-50 mm», es la conversión de 1.0-2.0 in hecha dentro del archivo de constantes, no una cifra del Manual.<br>*Manual de Puentes, num. 2.8.1.1.14.2.2, pág. impresa 255 (PDF 256)* |
| `PUE-08` | ALTA | CONTRADICE | Manual de Puentes | **k_v = 0.0 se declara adopción del proyectista, y el Manual lo fija en el numeral que el proyecto ya cita** — `k_v = 0.0`, etiqueta `[A]`, fuente «**Práctica corriente; no fijado por el Manual de Puentes**», con sensibilidad (0.0, 0.5).<br>*src/criterios_adoptados.py:489-495 · manifiesto §11.b y §12* | En el mismo numeral del que el proyecto toma kₕ₀ = Aₛ: «El coeficiente de aceleración sísmica vertical, kᵥ, **se asumirá cero** con el propósito de calcular las presiones laterales del terreno, a no ser que el muro esté significativamente afectado por efectos de alguna falla cercana, o si son relativamente altas las aceleraciones verticales que probablemente estén actuando simultáneamente con la aceleración horizontal.» La afirmación negativa es falsa. El error va del lado seguro —se declara como elección algo que la norma respalda— pero debilita la memoria: presenta como discrecional un valor defendible como `[N]`, y el rango de sensibilidad (0.0, 0.5) sugiere una libertad que el numeral acota.<br>*Manual de Puentes, num. 2.8.1.1.14.2.1, pág. impresa 254 (PDF 255)* |
| `PUE-09` | ALTA | CONTRADICE | Manual de Puentes | **La Tabla de factores de sitio sí tipifica la Clase F: le pone asterisco y exige estudio de respuesta dinámica** — «**Afirmación negativa**: el Manual de Puentes NO tipifica excepciones para Clase F en su Tabla 2.4.3.11.2.1.2-1», etiqueta `[C]` — vacío cubierto con fuente técnica.<br>*src/criterios_adoptados.py:400-403 · manifiesto §3* | La Tabla 2.4.3.11.2.1.2-1 tiene **fila F con asterisco en las cinco columnas de PGA** y una Nota 2 al pie: «Llevar a cabo investigaciones geotécnicas específicas del sitio y análisis de respuesta dinámica de sitio, para todos los sitios en sitio clase F» Eso *es* tipificar: la tabla se pronuncia sobre la Clase F y su pronunciamiento es «aquí no hay factor tabulado, hay que hacer el estudio». No es un vacío que una fuente técnica deba cubrir; es una exigencia expresa de la que el proyecto se aparta, y la etiqueta `[C]` lo presenta como lo contrario.<br>*Manual de Puentes, Tabla 2.4.3.11.2.1.2-1 y Nota 2, pág. impresa 123 (PDF 124)* |
| `AAS-02` | ALTA | CONTRADICE | AASHTO LRFD · Manual de Puentes | **La premisa de toda la Sec. 0.5 — «el sitio es Clase F por licuefacción» — no la sostiene ninguna de las dos tablas** — `clase_sitio = "F_con_factores_tabulados_por_adopcion"`: el sitio se clasifica Clase F por susceptibilidad a licuefacción, y de ahí que usar factores tabulados sea «adopción declarada del proyectista **sin respaldo normativo**», contra una exigencia incondicional de AASHTO.<br>*src/criterios_adoptados.py:386-435 · manifiesto §8 · memoria, Tablero 1 ítem 1.1* | Las tres categorías de Clase F son idénticas en los dos documentos y **ninguna es «suelos licuables»**: «Soils requiring site-specific evaluations, such as: Peats or highly organic clays (H > 10.0 ft) · Very high plasticity clays (H > 25.0 ft with PI > 75) · Very thick soft/medium stiff clays (H > 120 ft)» La 9.ª edición trata la licuefacción en el **Art. 10.5.4.2 «Liquefaction Design Requirements»** (Sección 10, Cimentaciones) — no por vía de la clase de sitio. Un depósito de arena saturada clasificaría por V̄ₛ/N̄/S̄ᵤ, probablemente D o E, y la licuefacción se evaluaría aparte: exactamente lo que el proyecto ya hace con su SPT de 15 m. · *Efecto de segundo orden*: si el sitio no es Clase F, la «adopción sin respaldo normativo» que la memoria confiesa puede no ser necesaria.<br>*AASHTO LRFD 9.ª ed., Tabla 3.10.3.1-1 pág. 3-102 y Art. 10.5.4.2 pág. 10-34 · Manual de Puentes, Tabla 2.4.3.11.2.1.1-1 pág. impresa 122* |
| `EG-01` | ALTA | CONTRADICE | EG-2013 | **La cita más load-bearing del proyecto está en la pág. 984, no en la 982 — y llega impresa a la memoria** — «Subsección **508.07, pág. 982**», repetido en al menos seis lugares: el comentario de `H_RELLENO_MIN["hdpe"]`, el criterio `h_relleno_min_concreto_tmc`, el numeral de `CAMA_RELLENO_LATERAL["hdpe"]` («508.05/.07, págs. 981-982»), §6 y §14.a del manifiesto, y el texto que M11 imprime.<br>*src/constantes_normativas.py:177 y :230 · src/criterios_adoptados.py:1081, :1138 · docs/manifiesto_citas.md:254 y §14.a* | La **Subsección 508.07 «Colocación del relleno alrededor de la estructura»** está en la **pág. impresa 984**. La pág. impresa 982 corresponde a 508.02 (calidad de los tubos, inspección, material para cama). 508.05 está en la 983 y 508.08 en la 985. · El texto sí coincide **palabra por palabra**: «La altura de relleno mínimo desde la clave de la tubería hasta el nivel de la subrasante será de 0,30 m.» Verificado en la memoria generada: la línea impresa dice «EG-2013 Subsección 508.07, pág. 982», con la página equivocada, en las dos plantillas.<br>*EG-2013 Capítulo V, 508.07 → pág. impresa 984 (PDF 992)* |
| `EG-02` | ALTA | CONTRADICE | EG-2013 | **La cita literal del 508.07 no vive donde el manifiesto dice que vive** — §6 y §14.a atribuyen la cita textual del 0,30 m y el `H_RELLENO_MIN["hdpe"]` «`[N]` puro» a **`src/constantes_normativas.py:160`**.<br>*docs/manifiesto_citas.md:254 y :614* | *Defecto interno de trazabilidad.* La línea 160 de `constantes_normativas.py` es «`# sobre cuantos sentidos se cuenta el kilometro.`», comentario final del bloque `CALICATAS_POR_SENTIDO` — Manual de Suelos, Cuadro 4.1. Otro documento, otro tema. · La cita textual está en `src/criterios_adoptados.py:1138-1140`; la constante, en `constantes_normativas.py:177`. Un revisor que siga el enlace del manifiesto aterriza en calicatas.<br>*—* |
| `EG-03` | ALTA | CONTRADICE | EG-2013 | **Las páginas de las cuatro fichas de cama y relleno lateral están corridas o son cortas** — `CAMA_RELLENO_LATERAL`: concreto simple «505.03/.07/.10/.11, **págs. 950-951**» · concreto reforzado «506.03/.07/.10/.11, **págs. 959-960**» · TMC «507.06/.07/.08, **pág. 970**» · HDPE «508.05/.07, **págs. 981-982**». Las mismas páginas viajan a la memoria y a los planos (Sec. 11, entregable 7).<br>*src/constantes_normativas.py:204-232* | Páginas impresas reales: **505**.03 → 950 · .07 → 951 · **.10 → 952 · .11 → 953** (el rango declarado deja fuera justo las dos subsecciones de sujeción y relleno) · **506**.03 → 959 · .07 → 960 · **.10 y .11 → 961** · **507**.06 → **973** · .07 → 973-974 · .08 → **974** (la pág. 970 declarada cae dentro de 507.02, Materiales) · **508**.05 → **983** · .07 → **984**. · El *contenido* de las cuatro fichas confirma: Clase F con f'c 14 MPa (Tabla 503-07, pág. 912), ≥ 15 cm, 1/4 y 1/6 del diámetro exterior, arena suelta de 12 mm, capas de 15-20 cm, capas alternadas y simétricas de 0,15 m, «los 0,30 m superiores… a una densidad mínima del 100 % de la M.D.S.» y «No será aceptable la compactación del relleno por medio de anegación».<br>*EG-2013 Capítulo V, Secciones 505 a 508, págs. impresas 949-985* |
| `HDS-01` | ALTA | CONTRADICE | HDS-5 | **La Tabla C.2 no está en la página C.2 — y la cita se declara «cerrada»** — `ke_entrada = 0.5` (square edge with headwall), fuente «HDS-5 3.ª ed., Apéndice C, **Tabla C.2, pág. C.2** … **CITA CERRADA por verificación externa contra el documento**».<br>*src/criterios_adoptados.py, criterio `ke_entrada` · manifiesto §7* | La **Tabla C.2 «Entrance Loss Coefficients»** está en la **pág. C.6**. La pág. C.2 es la continuación del índice de cartas («Chart / Concrete Box Culverts (Continued)»). · El **valor confirma**: «Pipe, Concrete — Headwall or headwall and wingwalls — Square-edge → 0.5». El error es de página y es del tipo que revela que la página no se abrió: se copió el número de la tabla como número de página.<br>*HDS-5 3.ª ed., Tabla C.2, pág. C.6 (PDF 216); pág. C.2 = PDF 212* |
| `HDS-02` | ALTA | CONTRADICE | HDS-5 | **HW/D 1.0–1.5 es una encuesta de práctica de agencias estadounidenses, no un criterio del HDS-5, y está en otra página** — `HW_D_max = 1.5`, etiqueta `[C]` («vacío normativo cubierto con fuente técnica reconocida»), fuente «HDS-5 3.ª ed., **Sec. 2.2.5, pág. 2.14** — rango de HW/D de 1.0 a 1.5 para el diseño corriente. **CITA CERRADA**». El manifiesto añade que la sensibilidad (1.2, 1.5) «es un subrango del 1.0-1.5 de la fuente».<br>*src/criterios_adoptados.py, criterio `HW_D_max` · manifiesto §7* | La Sec. 2.2.5 «Allowable Headwater» empieza en la **pág. 2.9**; la frase está en su apartado **d) «Agency Constraints», pág. 2.10**. La pág. 2.14 trata de espolones de escombros y seguridad vial. · Y el texto no prescribe: «Some state or local highway agencies place limits on the headwater… **The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5.**» Es una descripción de lo que *imponen las agencias estatales*, no un valor que el HDS-5 fije. En el Perú la agencia es el MTC, cuyo Manual no fija HW/D: lo que se hizo fue adoptar una banda de práctica ajena como si fuera recomendación de la fuente. Además 1.5 es el **extremo superior** —el menos restrictivo— y la «sensibilidad» (1.2, 1.5) es la mitad alta de la banda.<br>*HDS-5 3.ª ed., Sec. 2.2.5 d), pág. 2.10 (PDF 72)* |
| `HID-02` | ALTA | CONTRADICE | Manual de Hidrología | **La longitud máxima de cuneta está en la pág. 179, y las dos cifras no tienen la misma fuerza normativa** — `LONG_MAX_CUNETA = {seca: 250.0, muy_lluviosa: 200.0}` y `NUMERAL_FASE_10 = "Fase 10 (num. 4.1.2.1 d), pag. 178)"`, que es lo que M10 lleva a la memoria. El criterio `long_max_cuneta = 200.0` repite la página.<br>*src/constantes_normativas.py:91 · src/modulos/M10_espaciamiento.py:62 · src/criterios_adoptados.py:932* | El num. 4.1.2.1 d) «Desagüe de las cunetas» está en la **pág. impresa 179**. La 178 es la Tabla N° 34 de dimensiones mínimas de cuneta. · Los valores confirman, pero con **modalidad distinta**: «En región seca o poca lluviosa la longitud de las cunetas **será** de 250 m como máximo, las longitudes de recorridos mayores deberán justificarse técnicamente; en región muy lluviosa **se recomienda** reducir esta longitud máxima a 200 m.» 250 m es exigencia; 200 m es recomendación. El código los declara los dos `[N]` del mismo rango. El proyecto adopta el *recomendado* como límite duro —conservador, pero la asimetría no se declara, igual que ocurre entre V1 y V2.<br>*Manual de Hidrología, num. 4.1.2.1 d), pág. impresa 179 (PDF 182)* |
| `SUE-02` | ALTA | CONTRADICE | Manual de Suelos | **El espaciamiento de 4 km a nivel de perfil no está en el Cuadro 4.1 y es condicional** — `ESPACIAMIENTO_PERFIL_KM = 4.0` «nivel perfil (**num. 4.2, Cuadro 4.1**)», declarado como constante `[N]` sin condición.<br>*src/constantes_normativas.py:173* | El 4.0 km no está en el Cuadro 4.1 sino en el texto corrido del num. 4.2, y viene condicionado: «En caso de estudios a nivel de perfil **se utilizará información secundaria existente** en el tramo del proyecto; **de no existir información secundaria** se efectuará el número de calicatas del cuadro 4.1 espaciadas cada 4.0 km en vez de cada km.» La regla primaria a nivel de perfil es usar información secundaria; los 4 km son el caso subsidiario. El mismo párrafo fija 2.0 km para factibilidad y prefactibilidad, y reglas para tramos de 500-1000 m y < 500 m, que tampoco se recogen.<br>*Manual de Suelos, num. 4.2, pág. impresa 29 (PDF 30)* |
| `SUE-03` | ALTA | CONTRADICE | Manual de Suelos | **Uno de los cuatro numerales que respaldan la compactación no contiene ninguno de los dos valores** — `COMPACTACION_CORONA = 0.95` y `COMPACTACION_CUERPO = 0.90`, ambos citados a «num. **3.2.1, 3.2.2, 3.3 y 9.1(1)**». El manifiesto marca esos numerales como el cierre de una fila que antes estaba «⚠ sin numeral».<br>*src/constantes_normativas.py:147-150 · manifiesto §2 (marca ⟳)* | · **3.2.1 Terraplén** (pág. 24) sostiene los dos: «La base y cuerpo del terraplén… en capas de hasta 0.30 m y compactadas al **90 %**… La **corona**… espesor mínimo de 0.30 m… en capas de 0.15 m, compactadas al **95 %**.» ✔ · · **3.3** (pág. 24) apoya la corona: «los últimos 0.30 m… compactados al 95 %». ✔ · · **3.2.2 Corte** (pág. 24) da 95 % para el fondo de excavación y 0.15 m de escarificado — relacionado, no es corona ni cuerpo. · · **9.1(1)** (pág. 89) **no contiene ni 0.95 ni 0.90**: trata de CBR ≥ 6 % y alternativas de estabilización. Es el numeral que sostiene `CBR_MIN_SUBRASANTE`, no la compactación.<br>*Manual de Suelos, num. 3.2.1 / 3.2.2 / 3.3, pág. impresa 24 (PDF 25) · num. 9.1(1), pág. impresa 89 (PDF 90)* |
| `E060-01` | ALTA | CONTRADICE | E.060 | **E.060 permite exceptuar la cuantía mínima en muros de contención, y el código argumenta lo contrario** — `constantes_normativas.py:302-317` defiende en extenso que `CUANTIA_MIN_MURO` es un **piso obligatorio**: «el Art. 14.3.1 fija un PISO **por debajo del cual ningún muro se arma**, y un piso se aplica — ρ_diseño = max(ρ_calculado, ρ_mínimo)».<br>*src/constantes_normativas.py:302-317 · src/modulos/M9_cabezal.py:1281 · manifiesto §5* | Los **valores confirman**: Art. 14.3.1 (pág. 133) da horizontal 0,002 y vertical 0,0015, sin inversión. Pero el capítulo tiene un artículo específico para muros de contención, que es lo que el cabezal es: «**14.8.2** El refuerzo mínimo será el indicado en 14.3. **Este requisito podrá exceptuarse** cuando el Ingeniero Proyectista disponga juntas de contracción y señale procedimientos constructivos que controlen los efectos de contracción y temperatura.» «Por debajo del cual ningún muro se arma» no es lo que dice la norma para muros de contención. La excepción existe y el código la niega expresamente.<br>*E.060, Art. 14.3.1 pág. 133 · Art. 14.8.2 pág. 134* |
| `E060-02` | ALTA | CONTRADICE | E.060 | **El acero en dos caras se decide con el umbral de temperatura e ignora el umbral general de 200 mm** — `requiere_temperatura_dos_caras` devuelve `False` y la memoria imprime «Acero por temperatura en UNA cara» para todo espesor < 0.250 m, apoyándose en `ESPESOR_TEMPERATURA_DOS_CARAS = 0.250` (Art. 14.8.3).<br>*src/modulos/M9_cabezal.py:1353-1377 · src/constantes_normativas.py:319-320* | El Art. 14.8.3 **confirma exactamente**: «El acero por temperatura y contracción deberá colocarse en ambas caras para muros de espesor mayor o igual a **250 mm**» — y 14.8 es, en efecto, «Muros de Contención». La transcripción es impecable. · Pero no es el único umbral. El **Art. 14.3.2** exige: «Los muros con un espesor **mayor que 200 mm**, excepto los muros de sótanos, deben tener el refuerzo **en cada dirección colocado en dos capas**», y el 14.8.2 remite expresamente a 14.3. Entre 200 y 250 mm el muro lleva refuerzo en dos capas por 14.3.2 aunque el acero por temperatura no lo exija, y la memoria imprime lo contrario.<br>*E.060, Art. 14.8.3 pág. 134 · Art. 14.3.2 pág. 133 · Art. 14.8.2 pág. 134* |
| `E060-03` | ALTA | CONTRADICE | E.060 | **Al Art. 11.10.10.2 se le atribuye un umbral que no define** — El criterio dice que «el Art. 11.10.10.2 lo sube a 0.0025 cuando la demanda de cortante supera **el umbral que ese artículo define (del orden de Vu > 0.5·φ·Vc)**».<br>*src/criterios_adoptados.py, criterio `cortante_alto_muro_e060_art_11_10_10_2`* | El artículo entero es: «11.10.10.2 La cuantía de refuerzo horizontal para cortante no debe ser menor que 0,0025 y su espaciamiento no debe exceder tres veces el espesor del muro ni de 400 mm.» No define umbral alguno. La condición de entrada la fija el 11.10.10.1 («Donde Vᵤ exceda la resistencia al corte Vc…»), y el «0.5·φ·Vc» pertenece a otro artículo, sobre vigas. El **0,0025 y la condición cualitativa de cortante alto confirman**; el umbral concreto es una atribución inventada.<br>*E.060, Arts. 11.10.10.1 y 11.10.10.2, pág. 104* |
| `MAN-01` | ALTA | CONTRADICE | Manifiesto ↔ código | **Cuatro criterios que el manifiesto inventaría como vacíos tienen hoy valor** — §3, §8 y §12 declaran `factores_carga_aashto`, `recubrimiento_aashto_mm`, `peso_especifico_concreto_kn_m3` y `procedimiento_flexion_corte_aashto_sec5` como `None`, etiqueta `[A]`, «vacío que bloquea…». §12 los cuenta entre los 26 sin valor.<br>*docs/manifiesto_citas.md:179-180, 295, 298-300, 486-487, 491, 493* | *Defecto interno.* Los cuatro tienen valor y etiqueta `[C]` en este SHA: `factores_carga_aashto` = diccionario completo de γ por combinación · `recubrimiento_aashto_mm` = 75 mm en las tres condiciones · `peso_especifico_concreto_kn_m3` = 23.56 · `procedimiento_flexion_corte_aashto_sec5` = φ, modelo de corte y β-θ. · El manifiesto es el índice por el que un revisor entra a la auditoría; describir como bloqueado lo que ya calcula invierte el sentido de la revisión.<br>*—* |
| `MAN-02` | ALTA | CONTRADICE | Manifiesto ↔ código | **Los recuentos de §12 y §13 no son los que devuelve el archivo, y se contradicen entre sí** — §13: «46 criterios: 0 `[N]` · **1 [N→]** · 1 `[S]` · **14 [C]** · 30 `[A]`», con la nota «los números de arriba son ahora los que devuelve el propio archivo». §12: «**Los 33 criterios [A]**… de los 33, **26 están sin valor**… solo **7** tienen valor declarado».<br>*docs/manifiesto_citas.md:457, 495-498, 519-531* | *Defecto interno.* Contado sobre el módulo: **46 criterios · 0 [N] · 2 [N→] · 1 [S] · 13 [C] · 30 [A]**; **23 sin valor** en total y, entre los `[A]`, **22 sin valor y 8 con valor**. · Los dos `[N→]` son `resguardo_HW_subrasante` y `h_relleno_min_concreto_tmc` —§14.a del propio manifiesto declara el segundo—. El octavo `[A]` con valor es `clase_sitio`, que §8 del propio manifiesto reetiquetó. La tabla de §12 tiene 33 filas porque cuatro ya no son `[A]`.<br>*—* |
| `MAN-03` | ALTA | CONTRADICE | Manifiesto ↔ código | **Un criterio retirado y una advertencia inexistente siguen inventariados** — §8 inventaría «`FS_flotacion = None` — FS de V7, ΣW ≥ FS·U», y una «**Advertencia transversal: declarar la EDICIÓN de AASHTO LRFD**» atribuida a `[CA:992-995]`.<br>*docs/manifiesto_citas.md:296 y :302* | *Defecto interno.* `FS_flotacion` **ya no existe**: el código lo declara retirado. Y `criterios_adoptados.py:992-995` pertenece al criterio `TR_evento_extremo` (V8) y habla de otra cosa: el texto de la «advertencia transversal» no está en el archivo citado ni en ningún otro.<br>*—* |
| `MAN-04` | ALTA | CONTRADICE | Manifiesto ↔ código | **Al menos 66 de 296 referencias archivo:línea no llevan a lo que dicen llevar, y todas caen en el hueco del test** — `tests/test_manifiesto_citas.py` vigila las referencias del manifiesto y pasa en verde. Su excepción declarada: las «referencias de prosa» (filas sin identificador entre backticks) solo se comprueban contra «que la línea no esté vacía».<br>*docs/manifiesto_citas.md (296 referencias) · tests/test_manifiesto_citas.py:52-67* | *Defecto interno.* Las 213 referencias verificadas por símbolo caen todas dentro de su bloque. Las **83 de prosa concentran el 100 % de los defectos**: al menos 66 apuntan a otra cosa. Focos: · · §4 (E.050) tiene un **desplazamiento sistemático de una función**: cada fila E1…E5 cita la función anterior a la que nombra. · · `M9_cabezal.py` — 14 referencias rotas, dos aterrizando en líneas de `import`. · · `criterios_adoptados.py` — 15 referencias caen en un criterio distinto del que la fila afirma (el índice «2.11 → 2.12» del Manual de Puentes se atribuye a `diametros_normalizados`). · · `[CN:35]` para `GAMMA_AGUA_KN_M3` (símbolo que ya no vive ahí), `[CN:47]` y `[CN:55]` para las dos afirmaciones negativas de las Tablas 9 y 10 (reales en 74 y 88), `[CN:86]` para el `VERIFICAR` de `D_MAX` (real en 132), `[CN:74]` para el comentario de `Ks` (real en 107), `[CN:41]` para la fórmula de TR (real en 68), `[CN:110]` para `h_o` (real en 127).<br>*—* |
| `VOC-01` | ALTA | NO VERIFICABLE | Trampa de vocabulario | **cota_TW es una cota absoluta y TW es un tirante: dos magnitudes distintas con casi el mismo nombre** — El CSV trae la columna `cota_TW` («Cota de TW», msnm) y el pipeline maneja además `TW`, definido como el tirante en el receptor **sobre el fondo de la salida**, en m. La opción de línea de comandos es `--tw`.<br>*src/modelos.py (PuntoCritico) · cli.py · src/modulos/M4_control.py · M5_verificaciones.py* | *Ambigüedad de nomenclatura, no de norma.* Una cota en msnm y un tirante sobre el fondo se diferencian por la cota de fondo de la salida; confundirlas desplaza el control de salida en la magnitud entera de esa cota. El repositorio distingue bien los dos conceptos en las definiciones, pero los nombra casi igual y expone los dos a la vez al usuario. Como las celdas `cota_TW` vienen vacías en las cuatro filas del CSV (tablero ANA), la confusión no se puede ejercitar hoy y no se pudo comprobar sobre datos reales: queda como riesgo declarado, no como error demostrado.<br>*—* |
| `VOC-02` | ALTA | CONTRADICE | Trampa de vocabulario | **«Recubrimiento» tiene tres sentidos en este expediente, no dos, y el tercero está sin declarar** — §14.a documenta **una** trampa: «recubrimiento» = altura de relleno de tierra *vs* recubrimiento de concreto sobre el acero (Manual de Puentes, Tabla 2.9.1.5.5.3-1). Añade que «son dos conceptos que comparten palabra en español y **no tienen ninguna relación**».<br>*src/criterios_adoptados.py:1129-1136 · docs/manifiesto_citas.md §14.a* | La trampa documentada es **real y está bien anotada**: la Tabla 2.9.1.5.5.3-1 existe, está en la pág. 378 y su fila de alcantarillas da 2.0 in. Pero: · · Hay un **tercer sentido**: en el EG-2013 Sección 507 y en M 36 / A760, «recubrimiento» es el **revestimiento metálico o bituminoso de la plancha de acero** («recubrimiento en peso de zinc», «recubrimiento galvanizado», «metallic-coated»). Es el sentido que gobierna la protección del TMC en el ambiente agresivo de este proyecto (507.10), y no está declarado. · · La afirmación «no tienen ninguna relación» es imprecisa *en la propia tabla citada*: la fila de alcantarillas es «forjados con **inferior a 2 pies de relleno** que no se utilicen como superficie de conducción → 2.0 in». El recubrimiento de acero exigido depende ahí de la altura de relleno. Los dos sentidos están acoplados en el mismo renglón del que se advierte que no lo están.<br>*Manual de Puentes, Tabla 2.9.1.5.5.3-1, pág. impresa 378 · EG-2013 507.10 pág. 974 y págs. 969-976 · A760 §1.1* |
| `VOC-03` | ALTA | CONTRADICE | Trampa de vocabulario | **«Luz» separa alcantarilla de puente, y el catálogo trabaja con diámetros** — `LUZ_MAX_ALCANTARILLA = 6.0` se compara contra la luz declarada del cruce (`--luz`) para decidir alcantarilla o puente, mientras M2 dimensiona por **diámetro** y el catálogo arranca en 0.90 m.<br>*src/constantes_normativas.py:28 · src/modulos/M1_clasificacion.py:78 · cli.py `--luz`* | Los dos numerales son complementarios y el umbral está bien leído: «alcantarilla… cuya **luz sea menor a 6.0 m**» (4.1.1.3.1) y «puente… cuya **luz sea mayor o igual a 6.0 m**» (4.1.1.5.1). Lo que ninguno de los dos define es qué es la «luz» de un conducto circular. El Manual usa «luz» también para puentes (distancia entre apoyos) y, en 4.1.1.3.4 a), habla de «sección mínima circular de 0.90 m de diámetro **o su equivalente de otra sección**» — es decir, admite secciones no circulares donde luz y diámetro no coinciden. El repositorio compara una entrada llamada «luz» contra un catálogo de diámetros sin declarar la equivalencia.<br>*Manual de Hidrología, num. 4.1.1.3.1 pág. 70 · 4.1.1.5.1 pág. 87 · 4.1.1.3.4 a) pág. 72* |
| `HID-03` | ALTA | CONTRADICE | Manual de Hidrología | **El diámetro mínimo de 0.90 m es condicional, y su excepción cubre a la Familia C de este proyecto** — `DIAMETRO_MIN = 0.90` y `D_INICIO = 0.90` («mínimo normativo MTC»), aplicados como piso incondicional del catálogo para todos los puntos y todas las familias.<br>*src/constantes_normativas.py:29 y :131 · src/modulos/M2_material.py:58* | El numeral trae dos condicionantes que el código no recoge: «**En carreteras de alto volumen de tránsito** y por necesidad de limpieza y mantenimiento de las alcantarillas, se adoptará una sección mínima circular de 0.90 m (36") de diámetro o su equivalente de otra sección, **salvo en cruces de canales de riego donde se adoptarán secciones de acuerdo a cada diseño particular**.» · La clase de vía «ni siquiera está cerrada» según el propio repositorio (depende del IMDA del estudio de demanda), así que «alto volumen de tránsito» no está establecido. · · La **Familia C de este expediente son cruces de canal** —el CSV los carga sin Q, sin área y sin S porque «el caudal lo fija el canal (ANA / Junta de Usuarios del Bajo Piura)»—, exactamente el caso que el numeral exceptúa. El piso de 0.90 m se les aplica igual.<br>*Manual de Hidrología, num. 4.1.1.3.4 a), pág. impresa 72 (PDF 75)* |
| `HID-04` | ALTA | NO VERIFICABLE | Manual de Hidrología | **«El rango recorre la calidad del revestimiento» no está en el Manual, y se imprime junto a la cita** — La nota de §1 y el campo `fuente` de `v_max_concreto_eleccion` —que la memoria **sí imprime**— afirman: «los dos números de la fila del concreto, 3.0 y 6.0 m/s, son ambos MÁXIMOS — **el rango recorre la calidad del revestimiento**, no un piso y un techo. 6.0 m/s es el máximo del acabado de mejor calidad… 3.0 m/s es el máximo del acabado más pobre».<br>*src/criterios_adoptados.py, criterio `v_max_concreto_eleccion` · docs/manifiesto_citas.md §1* | La **lectura de fondo se sostiene**: el título es «Velocidades máximas admisibles (m/s) en conductos revestidos», la única columna se rotula «VELOCIDAD (M/S)», y el piso de autolimpieza está aparte, en el párrafo siguiente. La corrección de V3 es correcta. · Lo que **no aparece en ninguna parte del Manual** es la explicación de *por qué* hay dos números: nada dice que recorran la calidad del acabado. La fuente de la tabla es «HCANALES, Máximo Villón B.». Además, la frase que introduce la tabla apunta en dirección contraria: «se encuentre dentro de un **rango**, cuyos **límites** se describen a continuación», y la fila de mampostería trae un solo número (2.0), incompatible con un rango de acabados. · Es una interpretación del proyectista, razonable, pero se imprime en la memoria adosada a la cita y sin marcarse como interpretación.<br>*Manual de Hidrología, Tabla N° 10 y párrafo previo, pág. impresa 76 (PDF 79)* |
| `HID-05` | ALTA | CONTRADICE | Manual de Hidrología | **El numeral del puente está en la pág. 86-87, no en la 88** — `NUMERAL_LUZ = "4.1.1.3.1 / 4.1.1.5.1" # Manual MTC, págs. 70 y 88`, que es lo que M1 lleva a la memoria.<br>*src/modulos/M1_clasificacion.py:78* | 4.1.1.3.1 «Aspectos generales» empieza en la **pág. impresa 70** ✔. 4.1.1.5.1 «Aspectos generales» (puentes) empieza en la **pág. 86**, y la frase que define el umbral —«se definirá como puente a la estructura cuya luz sea mayor o igual a 6.0 m, siguiendo lo establecido en las especificaciones AASHTO LRFD»— está en la **pág. 87**. La pág. 88 no contiene ninguna de las dos.<br>*Manual de Hidrología, págs. impresas 70, 86 y 87 (PDF 73, 89 y 90)* |
| `PUE-10` | ALTA | CONTRADICE | Manual de Puentes | **El recubrimiento de AASHTO se declara vacío mientras el Manual que el proyecto ya cita lo da** — `recubrimiento_aashto_mm` figuró como vacío «que bloquea la regla del mayor (Sec. 0.2)» y hoy se cierra citando solo AASHTO. En ninguno de los dos estados se usa el Manual de Puentes.<br>*src/criterios_adoptados.py, criterio `recubrimiento_aashto_mm` · docs/manifiesto_citas.md §8 y §12* | El Manual de Puentes **transcribe la tabla** como Tabla 2.9.1.5.5.3-1 (= 5.12.3-1 AASHTO), pág. 378, con «Vaciado del concreto contra el suelo → 3.0 in», «Ubicaciones costeras → 3.0 in» y «Exposición directa al agua salada → 4.0 in», más los factores de modificación por relación W/C (0.8 para W/C ≤ 0.40; 1.2 para W/C ≥ 0.50) que el criterio no recoge y que, con la relación a/c de 0.40 que el propio proyecto adopta por cloruros, **reducirían** el recubrimiento exigido un 20 %. El proyecto cita esa tabla en otro sitio —para advertir de la trampa de vocabulario— pero no la usa donde hace falta.<br>*Manual de Puentes, num. 2.9.1.5.5.3 pág. 377 y Tabla 2.9.1.5.5.3-1 pág. 378* |
| `MEM-01` | ALTA | CONTRADICE | Memoria exportada | **El matiz «recomienda, no prohíbe» que el manifiesto declara como lo único que se imprime de V2, no se imprime** — «ese matiz **viaja hasta la memoria** dentro de `M5.NUMERAL_V2`» (`constantes_normativas.py:42-44`) y «Es **lo único que la memoria imprime de V2**» (manifiesto §1).<br>*src/constantes_normativas.py:42-44 · docs/manifiesto_citas.md §1* | *Verificado sobre la memoria generada* (`cli.py --html` sobre `tests/ejemplo_puntos.csv`, alcances expediente y perfil): «recomend» aparece **0 veces** y «sedimentación» **0 veces** en ambas. El pipeline se detiene antes de V2 porque `homogeneidad_serie_fen` bloquea el Q de toda la Familia A, así que el matiz nunca llega al revisor. La afirmación es cierta sobre el código y falsa sobre el producto: hoy la memoria no lleva ese matiz.<br>*—* |
| `COH-01` | ALTA | CONFIRMA | HDS-5 · hoja de ruta | **El 19.63 es correcto y la hoja de ruta está equivocada: la discrepancia declarada se resuelve a favor del código** — `K_FRICCION_SI = 19.63`, con la afirmación de que «es el valor que el propio HDS-5 escribe como conversión SI de su constante K = 29… es una cifra de la **FUENTE PRIMARIA, transcrita**», y una «DISCREPANCIA ABIERTA» declarada porque la hoja de ruta sigue diciendo 19.62.<br>*src/constantes_normativas.py:111-126 · src/modulos/M4_control.py* | HDS-5 3.ª ed., **Ecuación 3.4b**: Hf = KU(n²L/R¹.³³)(V²/2g), donde «KU = **29 in English Units (19.63 in SI)**» La afirmación del código es exacta. La hoja de ruta escribe 19.62 en las líneas **436, 440, 797 y 908** — el código las cita como «432, 436, 790 y 901», tres de cuatro corridas ~7 líneas. · *Nota para la sustentación*: la constante deja de estar «⚠ sin numeral». Su numeral es **Ec. 3.4b, Sec. 3.1, pág. 3.10**, y conviene escribirlo.<br>*HDS-5 3.ª ed., Ec. 3.4b, pág. 3.10 (PDF 92); repetida como DG 3.1 en pág. C-? (PDF 296)* |
| `E030-02` | ALTA | CONTRADICE | E.030 | **El perfil S5 se declara «referencia muerta» y trae una prohibición expresa de construir** — `PERFIL_SUELO_PRESUNTO = "S5"`, etiqueta `[S]`: «el Art. 14.6 define el **esquema** S0-S5 y sus umbrales; qué letra le toca a este sitio es el resultado de aplicar ese esquema». El manifiesto lo califica de «**referencia muerta**: no lo invoca ningún módulo», y un test vigila que siga siéndolo.<br>*src/criterios_adoptados.py:347-384 · docs/manifiesto_citas.md §10 · tests/test_criterios_adoptados.py* | El esquema y la letra **confirman**: S5 «Suelos excepcionales», primera viñeta «Suelos potencialmente licuables». Lo que el código no recoge es la última viñeta de esa misma celda: «Estos casos no están cubiertos en la clasificación establecida en la Tabla Nº 2 de la presente Norma Técnica. **Se prohíbe las construcciones apoyadas sobre estos perfiles, salvo que se efectúe un estudio específico para el sitio, en el cual se debe considerar los mejoramientos en el estrato del perfil.**» Una clasificación que prohíbe construir salvo estudio específico no es una referencia muerta: es la afirmación normativa más fuerte que el expediente hace sobre este sitio. La memoria imprime la letra sin la consecuencia. · *Y converge con AAS-02*: E.030 sí incluye los suelos licuables en su categoría excepcional; AASHTO y el Manual de Puentes no los incluyen en la Clase F. El proyecto traslada una clasificación a la otra sin declarar que los dos esquemas discrepan justamente en el rasgo que motiva la clasificación.<br>*E.030 (2026), Art. 14.6, Tabla Nº 2, fila S5, pág. impresa 11* |
| `HDS-05` | ALTA | CONTRADICE | HDS-5 | **h_o se aplica siempre, y HDS-5 acota expresamente cuándo puede usarse** — `h_o = max(TW, (y_c + D)/2)` se calcula de forma **incondicional** en `control_salida()`, sin comprobar ni declarar límite de validez. El manifiesto marca la fila «⚠ sin numeral».<br>*src/modulos/M4_control.py:493-494 · src/constantes_normativas.py:127 · docs/manifiesto_citas.md §7* | La fórmula **confirma**, y además tiene numeral: Sec. 3.3.3, pág. 3.24. Pero viene con una condición de uso que el repositorio no recoge: «Approximate hydraulic gradeline hₒ = (dc + D)/2 **can only be used if the barrel flows full for most of its length. It should not be used if the inlet is not submerged.**» El proyecto adopta además `geometria_control_salida = "seccion_llena"` como criterio `[C]`, que presupone lo mismo que aquí hay que verificar. Con un barril que no llena —el caso que el propio criterio contempla en su alternativa— la aproximación se aplica fuera de su rango declarado y nadie se entera.<br>*HDS-5 3.ª ed., Sec. 3.3.3, pág. impresa 3.24 (PDF 106)* |
| `AAS-04` | ALTA | CONTRADICE | AASHTO LRFD | **También se afirma que la fuente no declara mínimo para EH en reposo, y sí lo declara** — La justificación del criterio dice: «La Tabla 3.4.1-2 además distingue EH activo (1.50/0.90) de **EH en reposo (1.35, sin mínimo declarado por la fuente)**», y el valor codificado es `EH_en_reposo: {max: 1.35}`, sin mínimo.<br>*src/criterios_adoptados.py:1345 (valor) y :1380-1382 (la afirmación)* | El bloque EH de la Tabla 3.4.1-2 da los tres pares completos: «Active **1.50 / 0.90** · At-Rest **1.35 / 0.90** · AEP for anchored walls 1.35 / N/A» Idéntico en el Manual de Puentes: «Activa 1.50 / 0.90 · En reposo 1.35 / **0.90** · AEP para paredes ancladas 1.35 / N/A». El único que de verdad no tiene mínimo es el AEP, y es «N/A», no una omisión de la fuente. La afirmación negativa es falsa, y el mínimo que falta es el que se usa en la combinación desfavorable.<br>*AASHTO LRFD 9.ª ed., Tabla 3.4.1-2, pág. 3-18 · Manual de Puentes, Tabla 2.4.5.3.1-2, pág. impresa 143* |
| `AAS-05` | ALTA | CONTRADICE | AASHTO LRFD | **El factor de modificación por relación a/c invertiría la conclusión de la regla del mayor** — `recubrimiento_aashto_mm` fija 75 mm por condición, «CITA CERRADA por verificación externa», y concluye que AASHTO gobierna en las tres condiciones frente a los 70/50/40 mm de E.060.<br>*src/criterios_adoptados.py:1501-1526 · src/modulos/M9_cabezal.py:1187-1215* | El Art. 5.10.1 no deja la Tabla 5.10.1-1 en bruto: «Cover for prestressing and reinforcing steel shall not be less than that specified in Table 5.10.1-1 **and modified for W/CM ratio**… Modification factors for W/CM ratio shall be the following: • For W/CM ≤ 0.40 → **0.8** • For 0.40 < W/CM < 0.50 → 1.0 • For W/CM ≥ 0.50 → 1.2» Este proyecto adopta `CLORUROS_EXTERNOS = {a_c_max: 0.40}`. Con W/CM = 0.40 el factor es **0.8**: 3.0 in × 0.8 = 2.4 in = **61 mm**, por debajo de los 70 mm de E.060 para «contra suelo». La regla del mayor pasaría a ganarla E.060 y la conclusión del criterio se invierte. El Manual de Puentes trae los mismos factores en su num. 2.9.1.5.5.3.<br>*AASHTO LRFD 9.ª ed., Art. 5.10.1, pág. 5-167 (PDF 526) · Manual de Puentes, num. 2.9.1.5.5.3, pág. impresa 377* |
| `AAS-06` | ALTA | CONTRADICE | AASHTO LRFD | **La expresión de β se transcribe sin la condición que la habilita** — `procedimiento_flexion_corte_aashto_sec5` incluye `"beta": "4.8 / (1 + 750*epsilon_s)"` y `"modelo_corte": "MCFT_seccional_directo_no_iterativo"`, como si fuera la expresión única.<br>*src/criterios_adoptados.py:1586-1599* | El Art. 5.7.3.4.2 la condiciona: «**For sections containing at least the minimum amount of transverse reinforcement** specified in Article 5.7.2.5, the value of β may be determined by Eq. 5.7.3.4.2-1: β = 4.8 / (1 + 750 εₛ). **When sections do not contain at least the minimum amount** of transverse reinforcement…» …y da otra expresión, dependiente además del parámetro de espaciamiento de fisura sₓₑ. Un muro de cabezal delgado sin estribos cae normalmente en el segundo caso. Transcrita sin la condición, la fórmula se aplicaría donde no vale.<br>*AASHTO LRFD 9.ª ed., Art. 5.7.3.4.2 y Ec. 5.7.3.4.2-1, pág. 5-70 (PDF 429)* |
| `PRO-04` | ALTA | CONTRADICE | M 36 · A760 | **La norma a la que se difiere la verificación pendiente del TMC no aparece en ninguna de las dos** — La verificación pendiente para TMC —«calibre por altura de relleno» y «relación **luz / corrugación**»— se atribuye a **ASTM A-807**, tanto en `clases_producto_por_relleno` como en la tabla final de §14.a.<br>*src/criterios_adoptados.py:1156, :1191, :1207 · docs/manifiesto_citas.md §9 y §14.a* | Búsqueda exhaustiva sobre el texto completo de las tres normas de producto: **«A-807» / «A 807» / «A807» aparece cero veces** en M 170M, M 36 y A760. · Las dos normas de acero remiten, para lo que aquí hace falta, a otras dos: · · **ASTM A796/A796M** — «Práctica para el **diseño estructural** de tuberías de acero corrugado», citada siete veces en A760 y en la lista de normas de M 36. Es la que lleva el calibre por altura de cobertura. · · **ASTM A798/A798M** — el procedimiento de instalación, al que remite A760 §1.4. · La relación luz/corrugación, además, **ya está en los documentos adjuntos**: la Tabla 6 de M 36 y la Tabla 1 de A760 marcan con «X» qué tamaños de corrugación son estándar para cada diámetro nominal. Parte del pendiente se puede cerrar hoy; la otra parte está en A796, no en A-807.<br>*AASHTO M 36-03(2007) §2 y Tabla 6 · ASTM A760/A760M-10 §1.4, §1.5 y Tabla 1* |
| `MEM-03` | ALTA | CONTRADICE | Memoria exportada | **La memoria justifica F_pga con una convergencia de la que ha desaparecido la fila que importa** — La justificación de `F_pga = 1.0`, **impresa en la Sección 3.2 de la memoria**: «Sin SPT no hay clase de sitio definitiva. Para PGA ≥ 0.50 **los factores convergen: 1.0 para clases C y D, 0.9 para E**…».<br>*src/criterios_adoptados.py:460 · memoria generada, Sec. 3.2* | Los tres valores **confirman**. Lo que no aparece es la cuarta fila de la misma columna: la Tabla 2.4.3.11.2.1.2-1 trae «**F² * * * * ***» con la Nota 2 «Llevar a cabo investigaciones geotécnicas específicas del sitio y análisis de respuesta dinámica de sitio, para todos los sitios en sitio clase F». · El proyecto sostiene en otro lado que **este sitio es Clase F**. La memoria, entonces, justifica el valor adoptado con una convergencia entre C, D y E que no incluye la clase que el propio expediente se atribuye — y la fila que le correspondería no da factor, exige un estudio. Las dos afirmaciones conviven en la misma memoria sin cruzarse.<br>*Manual de Puentes, Tabla 2.4.3.11.2.1.2-1 y Nota 2, pág. impresa 123 (PDF 124)* |

## 3. Medias

| ID | Sev | Veredicto | Documento | Afirmación del repo (archivo:línea) | Qué dice el PDF (documento, página) |
|---|---|---|---|---|---|
| `HID-06` | MEDIA | CONTRADICE | Manual de Hidrología | **El título entrecomillado de la Tabla N° 10 omite «(m/s)»** — El título se transcribe entre comillas como «**Velocidades máximas admisibles en conductos revestidos**», en `constantes_normativas.py`, en `NUMERAL_V3` y en el criterio que la memoria imprime.<br>*src/constantes_normativas.py:78 · src/modulos/M5_verificaciones.py:131-134 · src/criterios_adoptados.py (`v_max_concreto_eleccion`)* | El título impreso es «TABLA N° 10: **Velocidades máximas admisibles (m/s) en conductos revestidos**». Falta «(m/s)» en las tres copias. En una cita entre comillas que la memoria reproduce, la unidad omitida es precisamente lo que un revisor comprobaría primero.<br>*Manual de Hidrología, Tabla N° 10, pág. impresa 76 (PDF 79)* |
| `HID-07` | MEDIA | CONTRADICE | Manual de Hidrología | **Los nombres de fila de las Tablas N° 02 y N° 10 están recortados** — Claves `quebrada_importante` / `quebrada_menor` en `RIESGO_ADMISIBLE`, y `mamposteria_piedra` en `V_MAX`.<br>*src/constantes_normativas.py:64-67 y :84-89* | Tabla N° 02: las filas son «Alcantarillas de paso de quebradas importantes **y badenes**» y «Alcantarillas de paso quebradas menores **y descarga de agua de cunetas**». Lo recortado importa: la segunda categoría cubre también la descarga de cunetas, que es justo lo que la Fase 10 dimensiona. · Tabla N° 10: la fila es «Mampostería de piedra **y concreto**», y trae un **solo valor (2.0)**, no un par; el código lo convierte en `(2.0, 2.0)`.<br>*Manual de Hidrología, Tabla N° 02 pág. 25 (PDF 28) · Tabla N° 10 pág. 76 (PDF 79)* |
| `HID-08` | MEDIA | CONTRADICE | Manual de Hidrología | **R y n de la Tabla N° 02 son máximos recomendados, y la norma asigna la decisión al propietario** — `RIESGO_ADMISIBLE` se declara `[N]` y sus valores entran directamente al cálculo de TR.<br>*src/constantes_normativas.py:64-67 · src/modulos/M1_clasificacion.py* | Los **números confirman** (R 0.30 / n 25 → TR 71; R 0.35 / n 15 → TR 35, ambos correctos con la fórmula (1) del num. 3.6). Pero el título de la tabla es «**VALORES MÁXIMOS RECOMENDADOS** de riesgo admisible», el texto que la introduce dice «se recomienda utilizar **como máximo**», y la nota al pie cierra: «El Propietario de una Obra es el que define el riesgo admisible de falla y la vida útil de las obras.» Techo recomendado más decisión del propietario se parece más a un `[A]` declarado que a una constante `[N]`.<br>*Manual de Hidrología, Tabla N° 02 y notas, pág. impresa 25 (PDF 28)* |
| `HID-09` | MEDIA | CONTRADICE | Manual de Hidrología | **El 0.25 m/s está en la pág. 77; la 76 es donde arranca el párrafo** — «num. 4.1.1.3.6, **pág. 76**, párrafo inmediatamente posterior a la Tabla N° 10».<br>*src/constantes_normativas.py:32-39 · src/modulos/M5_verificaciones.py:125-130* | El párrafo empieza en la pág. 76 y **termina en la 77**: «…que pueda incidir en una» / «reducción de su capacidad hidráulica, recomendándose que la velocidad mínima sea igual a **0.25 m/s**». Quien vaya a la pág. 76 a comprobar el número no lo encuentra ahí. «Párrafo inmediatamente posterior a la Tabla N° 10» ✔ y el numeral 4.1.1.3.6 ✔.<br>*Manual de Hidrología, págs. impresas 76-77 (PDF 79-80)* |
| `HID-10` | MEDIA | CONTRADICE | Manual de Hidrología | **V1 y V2 salen del mismo tipo de frase y solo una lleva el matiz de recomendación** — `NUMERAL_V2` lleva expresamente «el numeral **RECOMIENDA, no prohíbe**» y se aplica como umbral duro «por decisión conservadora del proyecto». `NUMERAL_V1 = "4.1.1.3.7 b)"` va pelado.<br>*src/modulos/M5_verificaciones.py:115 y :125-130* | El 4.1.1.3.7 b) «Borde libre» está redactado igual de blando: «**Se recomienda** que el diseño hidráulico considere como mínimo el 25 % de la altura, diámetro o flecha de la estructura.» El 25 % y la lectura y/D ≤ 0.75 **confirman**. Lo que no se sostiene es el trato asimétrico: dos «se recomienda» del mismo numeral, uno anotado como recomendación y el otro presentado como exigencia. Un revisor que vea el matiz en V2 preguntará por qué no está en V1.<br>*Manual de Hidrología, num. 4.1.1.3.7 b), pág. impresa 79 (PDF 82)* |
| `HID-11` | MEDIA | CONFIRMA | Manual de Hidrología | **La Tabla N° 09 tiene tres columnas y el código transcribe dos, eligiendo una subfila sin declararlo** — `MANNING = {metal_corrugado: (0.021, 0.030), concreto_recto: (0.010, 0.013), madera_duelas: (0.010, 0.014)}`, comentado como «(n_min, n_max)».<br>*src/constantes_normativas.py:70-76* | Los seis números **confirman dígito por dígito**. Dos matices: · · La tabla tiene **MÍNIMO / NORMAL / MÁXIMO**; el código descarta la columna NORMAL, que es la de uso corriente (0.024 para metal corrugado, 0.011 para concreto recto, 0.012 para madera). · · «Metal corrugado» tiene dos subfilas: *sub-dren* (0.017 / 0.019 / 0.021) y *dren para aguas lluvias* (0.021 / 0.024 / 0.030). El código toma la segunda —la correcta para una alcantarilla— pero no declara la elección, y el par (0.021, 0.030) coincide numéricamente con el máximo de la primera subfila. · La afirmación negativa «HDPE no está listado» **confirma**.<br>*Manual de Hidrología, Tabla N° 09, pág. impresa 75 (PDF 78)* |
| `SUE-04` | MEDIA | CONTRADICE | Manual de Suelos | **El Cuadro 4.1 también fija la profundidad de calicata, que no se recoge** — Del Cuadro 4.1 se transcriben `CALICATAS_POR_KM` y `CALICATAS_POR_SENTIDO`.<br>*src/constantes_normativas.py:152-172* | Los dos **confirman** (4/4/4/3/2/1, y «× km × sentido» solo para autopistas y duales). El Cuadro tiene además una columna «Profundidad (m)» con el mismo valor en todas las filas: «**1.50 m respecto al nivel de sub rasante del proyecto**», reforzado por el num. 4.2 («calicatas de 1.5 m de profundidad mínima»). Es un valor `[N]` del mismo cuadro que el proyecto no lleva.<br>*Manual de Suelos, num. 4.2 y Cuadro 4.1, pág. impresa 28 (PDF 29)* |
| `SUE-05` | MEDIA | CONTRADICE | Manual de Suelos | **«Resguardo» es palabra del proyecto, no del Manual, y el resguardo admite remedios alternativos** — `RESGUARDO_NAPA_SUBRASANTE`, `resguardo_por_cbr()`, `resguardo_HW_subrasante` y V4 tratan el valor como umbral duro.<br>*src/constantes_normativas.py:141-145 · src/modulos/M5_verificaciones.py:321-322 · M7_geometria.py:82* | Los **cuatro escalones y los cuatro intervalos de CBR confirman literalmente**: «El nivel superior de la sub rasante debe quedar encima del nivel de la napa freática como mínimo a 0.60 m… (CBR ≥ 20 %); a 0.80 m… (6 % ≤ CBR < 20 %); a 1.00 m… (3 % ≤ CBR < 6 %); y a 1.20 m… (CBR < 3 %)». Transcripción impecable. · Dos matices: el Manual **no usa la palabra «resguardo»** en este sentido (0 ocurrencias en el Manual de Hidrología y en E.050; la única en el Manual de Suelos es «al resguardo de la luz», sobre conservación de muestras), y la frase continúa: «En caso necesario, **se colocarán subdrenes o capas anticontaminantes y/o drenantes o se elevará la rasante** hasta el nivel necesario» — es decir, el incumplimiento admite remedio y no es un rechazo binario.<br>*Manual de Suelos, num. 4.5.4, págs. impresas 41-42 (PDF 42-43) · num. 9.1(3), págs. 89-90* |
| `ANA-01` | MEDIA | NO VERIFICABLE | Analogía [N→] | **El argumento de conservadurismo de la analogía descansa en una fuente que no está en el repositorio** — «La analogía es conservadora: **el HDPE es el material con MENOR tolerancia a cobertura reducida bajo carga viva**… exigir su recubrimiento al concreto y al TMC **no puede quedar del lado inseguro**». La memoria lo imprime, apoyado en «WSDOT M 23-03.12, Tabla 8-6» como referencia comparativa.<br>*src/criterios_adoptados.py:1074-1108 · memoria generada* | La **dirección** del argumento se sostiene contra AASHTO 12.6.6.3: el termoplástico bajo pavimento pide ID/2 ≥ 24 in mientras el concreto y el metal piden ≥ 12 in. Pero: · · La **magnitud** no: el valor adoptado, 0.30 m, queda por debajo del piso de 12 in de concreto y metal (0.305 m) y muy por debajo del Bc/8 que gobierna en diámetros grandes. La analogía es conservadora en el orden de los materiales y **no en el número**. · · **WSDOT no está en el repositorio**, de modo que la única cita que la memoria ofrece al revisor para sostener «el concreto tolera más» es incomprobable. · · La analogía **sí está declarada como analogía**, con etiqueta `[N→]` y con las palabras «ADOPCIÓN POR ANALOGÍA SOBRE UN VACÍO VERIFICADO», tanto en el criterio como en la memoria. ✔<br>*AASHTO LRFD 9.ª ed., Tabla 12.6.6.3-1, pág. 12-22 · WSDOT M 23-03.12: no disponible* |
| `ANA-02` | MEDIA | CONFIRMA | Analogía [N→] | **La analogía del resguardo está declarada y el numeral original dice lo que se le atribuye** — `resguardo_HW_subrasante = "segun_CBR"`, etiqueta `[N→]`: la tabla del num. 4.5.4 —que regula el nivel freático— aplicada al HW de avenida, «el numeral regula el nivel freático, no un nivel transitorio».<br>*src/criterios_adoptados.py:908-917 · src/modulos/M5_verificaciones.py:134* | El num. 4.5.4 **sí regula el nivel freático** y la tabla es la que el código transcribe; el 9.1(3) la repite en el capítulo de estabilización. La analogía está declarada como tal, la etiqueta `[N→]` es la correcta según la taxonomía del propio proyecto y la memoria la imprime como analogía. · *Lo que un revisor preguntará*: el resguardo del 4.5.4 protege la subrasante del **ascenso capilar continuo** de un freático permanente. Un HW de avenida moja el terreno durante horas, por un mecanismo distinto, y puede subir por encima del freático. Que la analogía quede del lado seguro no se deduce del numeral: es plausible, no demostrado, y el criterio lo presenta como establecido.<br>*Manual de Suelos, num. 4.5.4 págs. 41-42 y num. 9.1(3) págs. 89-90* |
| `ANA-03` | MEDIA | CONTRADICE | HDS-5 | **La analogía de embocadura del HDPE usa la fila que da menos carga que la del metal** — `hds5_embocadura_hdpe = {K: 0.0098, M: 2.00, c: 0.0398, Y: 0.67, Ks: -0.5}`, etiqueta `[C]`: la fila del concreto aplicada al HDPE de interior liso a ras del muro.<br>*src/criterios_adoptados.py, criterio `hds5_embocadura_hdpe`* | Los cinco valores **confirman** contra la Tabla A.1 (fila «Circular Concrete / Square edge w/headwall»), y la página citada, **A.8, es correcta**. · Pero la analogía no es conservadora: en la misma tabla, «Circular CM / Headwall» da K = 0.0078, c = 0.0379, Y = 0.69. Aplicando la rama sumergida HWᵢ/D = c·q*² + Y + KₛS, la fila del concreto da un HW **menor** que la del metal en el rango de q* de interés. Elegir el concreto para un material intermedio produce una carga a la entrada más baja, que es la dirección insegura para V1 y para el resguardo. El criterio no declara esa comparación.<br>*HDS-5 3.ª ed., Tabla A.1, pág. A.8 (PDF 197)* |
| `HDS-03` | MEDIA | CONTRADICE | HDS-5 | **Ku, los límites 3.5/4.0 y las ecuaciones no están en la Tabla A.1 sino en el texto que la precede** — `KU_METRICO = 1.811`, `Q_LIM_NO_SUMERGIDO = 3.5` y `Q_LIM_SUMERGIDO = 4.0` se atribuyen los tres a «**Apéndice A, Tabla A.1, pág. A.8**», y el docstring de M4 dice que «las dos ramas extremas sí son las ecuaciones literales de la Tabla A.1».<br>*src/constantes_normativas.py:93-97 · src/modulos/M4_control.py* | Los **tres valores confirman**, y su uso conjunto es correcto —el punto donde más proyectos se equivocan—: HDS-5 dice «applies up to about Q/AD⁰.5 = 3.5 (**1.93 SI**)» y «above about Q/AD⁰.5 = 4.0 (**2.21 SI**)», de modo que al multiplicar por Kᵤ = 1.811 los umbrales que corresponden son los ingleses, 3.5 y 4.0, que es lo que M4 hace. ✔ · Lo que no cuadra es la ubicación: la Tabla A.1 (pág. A.8) contiene *solo* las constantes K, M, c, Y por carta. Kᵤ, Kₛ, los límites y las ecuaciones (A.1)-(A.3) están en el texto de la **Sec. A.2, págs. A.1-A.2**. La constante `Ks`, que el manifiesto marca «⚠ el código declara que NO figura en la Tabla A.1: proviene de la formulación», tiene numeral y página: **Sec. A.2.1, pág. A.2**, «Kₛ Slope correction, −0.5 (mitered inlets +0.7)».<br>*HDS-5 3.ª ed., Secs. A.2.1 y A.2.2, págs. A.1-A.2 (PDF 190-191) · Tabla A.1, pág. A.8 (PDF 197)* |
| `E060-04` | MEDIA | CONTRADICE | E.060 | **«Aumentar adecuadamente» no es lo que dice el artículo** — El comentario y el manifiesto entrecomillan que «el artículo dice “**aumentar adecuadamente**” y no fija cuánto».<br>*src/constantes_normativas.py:297-300 · docs/manifiesto_citas.md §5* | El Art. 7.7.5.1 (pág. 55) dice: «En ambientes corrosivos u otras condiciones severas de exposición, **debe aumentarse adecuadamente** el espesor del recubrimiento de concreto y debe tomarse en consideración su densidad y porosidad o debe disponerse de otro tipo de protección.» El fondo —que no fija cuánto— **confirma**. La cita entrecomillada no coincide: cambia la forma verbal y omite la alternativa expresa («o debe disponerse de otro tipo de protección»), que es un camino de cumplimiento distinto del que el criterio contempla.<br>*E.060, Art. 7.7.5.1, pág. 55* |
| `E060-05` | MEDIA | CONTRADICE | E.060 | **La Tabla 4.4 tiene dos escalas y seis cementos; el código lleva una escala y tres** — `SULFATOS` transcribe «(SO4_min %, SO4_max %, cemento, a/c, f'c)» con el cemento moderado como «**II/IP(MS)/IS(MS)**».<br>*src/constantes_normativas.py:287-292* | Los **cuatro rangos, las tres relaciones a/c y los tres f'c confirman** exactamente (0,50 / 28; 0,45 / 31; 0,45 / 31). Dos omisiones: · · La tabla da la exposición por **dos vías paralelas**: «Sulfato soluble en agua (SO₄) presente en el **suelo**, porcentaje en peso» y «Sulfato (SO₄) en el **agua**, ppm» (150 / 1500 / 10000). El código solo lleva la del suelo; si el expediente trae un análisis de agua —lo esperable con ANA de por medio— la tabla no se puede aplicar. · · El cemento para exposición moderada son **seis** tipos: «II, IP(MS), IS(MS), **P(MS), I(PM)(MS), I(SM)(MS)**». Se transcriben tres.<br>*E.060, Tabla 4.4, pág. 38* |
| `E060-06` | MEDIA | CONTRADICE | E.060 | **Los cloruros salen de la Tabla 4.2, y la regla de combinación de las dos tablas no se recoge** — `CLORUROS_EXTERNOS = {a_c_max: 0.40, fc_min_MPa: 35} # Art. 4.2 / 4.4`.<br>*src/constantes_normativas.py:293* | Los dos **valores confirman**, y salen de la **Tabla 4.2 «Requisitos para condiciones especiales de exposición» (pág. 37)**, fila «Para proteger de la corrosión el refuerzo de acero cuando el concreto está expuesto a cloruros provenientes de productos descongelantes, sal, agua salobre, agua de mar o a salpicaduras». El 4.4 es «Protección del refuerzo contra la corrosión» y remite a la Tabla 4.5, sobre contenido de ion cloruro en el concreto endurecido: otra exigencia. · Falta además la nota al pie que gobierna este proyecto, donde sulfatos y cloruros coinciden: «Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se debe utilizar la **menor** relación máxima agua-material cementante aplicable y el **mayor** f'c mínimo.»<br>*E.060, Tabla 4.2 pág. 37 · Tabla 4.4 y su nota al pie, pág. 38* |
| `E060-07` | MEDIA | CONTRADICE | E.060 · EG-2013 | **Para el concreto ciclópeo se cita el mínimo menos exigente de los dos disponibles** — `CICLOPEO_FC_MATRIZ_MIN = 10.0` MPa y `CICLOPEO_FRACCION_PIEDRA_MAX = 0.30`, Art. 22.10 de E.060.<br>*src/constantes_normativas.py:326-328* | E.060 Art. 22.10 **confirma**: f'c de la matriz = 10 MPa y piedra desplazadora ≤ 30 % del volumen total, en las págs. 194-195. · Pero el EG-2013 —cuya Sección 503 es la que el proyecto cita para cabezales— fija en su **Tabla 503-07** el concreto ciclópeo **Clase G**: «Se compone de concreto simple Clase F y agregado ciclópeo, en proporción de 30 % del volumen total, como máximo — **14 MPa** (140 kg/cm²)». Para una obra vial del MTC, el mínimo aplicable es el mayor de los dos, y el proyecto declara el menor sin mencionar el otro.<br>*E.060 Art. 22.10, págs. 194-195 · EG-2013 Tabla 503-07, pág. impresa 912* |
| `E050-01` | MEDIA | CONTRADICE | E.050 | **«Sísmico» sustituye a dos condiciones distintas que la norma nombra de otra forma** — La clave de la segunda columna de `FS` es `"sismico"` en las cinco filas.<br>*src/constantes_normativas.py:266-272* | Los **diez números confirman** en las páginas declaradas (3,0/2,5 en Art. 21.1-21.2 pág. 34; 1,50/1,25 en 39.13.6 a) y b) pág. 72; 1,5/1,25 en Art. 30.3 pág. 39). Pero la norma nombra dos condiciones distintas: el Art. 21.2 dice «para solicitación máxima de **sismo o viento** (la que sea más desfavorable)» y el 39.13.6 dice «Condición **Pseudo-dinámico**». Colapsarlas en «sismico» pierde el viento del Art. 21.2 y renombra la condición del 39.13.6 sin declararlo.<br>*E.050, Art. 21 pág. 34 · num. 39.13.6 pág. 72 · Art. 30.3 pág. 39* |
| `E050-02` | MEDIA | CONFIRMA | E.050 | **El espaciamiento del SPT sí tiene numeral: la marca «⚠ sin numeral» se puede cerrar** — `SPT_ESPACIAMIENTO = 1.0` «m entre ensayos», que el manifiesto marca «**⚠ sin numeral propio** (hereda el Art. 38 de la línea anterior)» y lista entre los puntos que la verificación debería mirar primero.<br>*src/constantes_normativas.py:284 · docs/manifiesto_citas.md §4 y §13* | Los dos valores salen de una sola frase del **Art. 38.4.3**: «Las perforaciones deben tener una profundidad mínima de **15 m** y deben ser realizadas por las técnicas de lavado o rotativa. Dentro de las perforaciones se llevan a cabo Ensayos de Penetración Estándar SPT (NTP 339.133) **espaciados obligatoriamente cada 1 m**.» El numeral preciso es **38.4.3, pág. 51**, y el contexto es el programa de exploración para licuefacción, que es exactamente el uso que el proyecto le da. La marca se puede retirar.<br>*E.050, Art. 38.4.3, pág. 51* |
| `AAS-03` | MEDIA | CONTRADICE | AASHTO LRFD | **Tres páginas de AASHTO citadas en las fuentes de criterios están corridas** — `factores_carga_aashto` → «Tablas 3.4.1-1 (**pág. 3-14**) y 3.4.1-2 (pág. 3-18); transcritas también en Manual de Puentes MTC, **págs. 143 y 146**» · `procedimiento_flexion_corte_aashto_sec5` → «Arts. 5.5.4.2 (**pág. 5-32**) y 5.7.3.4.2 / 5.7.3.3 / 5.7.2.8 (**págs. 5-70 a 5-243**)».<br>*src/criterios_adoptados.py, criterios `factores_carga_aashto` y `procedimiento_flexion_corte_aashto_sec5`* | · Tabla 3.4.1-1 → pág. **3-17** (no 3-14). Tabla 3.4.1-2 → 3-18 ✔. · · En el Manual de Puentes ambas están en la **pág. 143**; la 146 no las contiene. · · Art. 5.5.4.2 «Resistance Factors» → pág. **5-29** (no 5-32; en la 5-32 empieza 5.5.4.3). · · 5.7.2.8 «Shear Stress on Concrete» → 5-64 y 5.7.3.3 «Nominal Shear Resistance» → 5-67, ambas **anteriores** al 5-70 con que arranca el rango declarado. · Los **artículos existen y están bien titulados**, y los φ = 0.90 de flexión y de corte confirman literalmente.<br>*AASHTO LRFD 9.ª ed., págs. 3-17, 3-18, 5-29, 5-64, 5-67, 5-70* |
| `PUE-11` | MEDIA | CONTRADICE | Manual de Puentes | **La columna de la tabla F_pga es «PGA > 0.50» y el PGA de este proyecto es exactamente 0.50** — `F_PGA_TABLA = {C: 1.0, D: 1.0, E: 0.9} # Tabla 2.4.3.11.2.1.2-1, PGA >= 0.50`.<br>*src/constantes_normativas.py:238-240* | Los **tres valores confirman**. La columna se rotula «**PGA > 0.50**», estrictamente mayor, y la Nota 1 manda «usar línea recta de interpolación para valores intermedios de PGA». Con `PGA_roca_B = 0.50` exactamente, el sitio cae en la frontera entre la columna «PGA = 0.40» y la «> 0.50»; para la Clase D eso es 1.1 frente a 1.0. · Se omiten además las filas **A (0.8)**, **B (1.0)** —justamente la clase sobre la que se lee el PGA— y **F (asterisco)**.<br>*Manual de Puentes, Tabla 2.4.3.11.2.1.2-1, pág. impresa 123 (PDF 124)* |
| `PUE-12` | MEDIA | CONTRADICE | Manual de Puentes | **Una regla del numeral de k_h0 para cimentaciones en roca no se implementa ni se descarta** — M9 calcula Aₛ = F_pga · PGA y kₕ₀ = Aₛ, leyendo `PGA_roca_B`.<br>*src/modulos/M9_cabezal.py:28 y :281 · src/datos_sitio.py:128* | La igualdad kₕ₀ = Fₚgₐ·PGA = Aₛ **confirma**. El mismo párrafo añade: «Para muros cimentados sobre Sitio con suelos **Clase A o B (roca dura o blanda)**, kₕ₀ estará basado en **1.2 veces** el coeficiente de aceleración pico del suelo.» Probablemente no aplique —la fundación es la llanura arenosa, no roca— pero el dato de sitio se llama `PGA_roca_B` y nada en el código dice por qué el 1.2 no entra. Es exactamente el tipo de regla que un revisor busca al ver «roca_B» en el nombre.<br>*Manual de Puentes, num. 2.8.1.1.14.2.1, pág. impresa 254 (PDF 255)* |
| `PUE-13` | MEDIA | CONTRADICE | Manual de Puentes | **La segunda figura de Meyerhof está fuera del rango de páginas citado** — «figuras 2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), **págs. 272-273**» y `NUMERAL_ZAPATA_EN_TALUD = "2.8.1.3.1.2c, pags. 272-273"`.<br>*src/constantes_normativas.py:262 · src/criterios_adoptados.py (`N_cq_N_gammaq_meyerhof`)* | **Confirma** el texto («Para zapatas apoyadas en taludes o cerca de ellos: Nq = 0.0» y «Nc y Nγ se reemplazarán con Ncq y Nγq»), la numeración de las dos figuras y su atribución a Meyerhof 1957. El texto está en la pág. 272 y la **Figura -1 en la 273**, pero la **Figura -2 está en la pág. 274**, fuera del rango declarado.<br>*Manual de Puentes, num. 2.8.1.3.1.2c págs. impresas 272-274 (PDF 273-275)* |
| `VOC-04` | MEDIA | CONTRADICE | Trampa de vocabulario | **«Clase F» significa dos cosas incompatibles dentro del mismo expediente** — `CAMA_RELLENO_LATERAL["concreto_simple"]` usa «Concreto **Clase F** (f'c = 14 MPa)» y el criterio `clase_sitio` usa «**Clase F**» de sitio sísmico. Ambos llegan a la memoria.<br>*src/constantes_normativas.py:206-207 · src/criterios_adoptados.py:386* | Son dos taxonomías sin relación: EG-2013 Tabla 503-07 clasifica el concreto en A-B (pre/postensado), C-D-E (reforzado), **F (simple, 14 MPa)** y G (ciclópeo); AASHTO y el Manual de Puentes clasifican el **sitio** en A-F, donde F son «suelos que requieren evaluaciones específicas de sitio». Ninguno de los dos usos se marca en la memoria, y el segundo es el eje de la Sec. 0.5.<br>*EG-2013 Tabla 503-07 pág. 912 · Manual de Puentes Tabla 2.4.3.11.2.1.1-1 pág. 122* |
| `E030-01` | MEDIA | CONTRADICE | E.030 | **El Tr = 475 años no lo escribe el artículo; es una derivación** — `Z_E030 = 0.45`, concepto: «Factor de zona Z de E.030 (aceleración máxima en suelo rígido **para Tr = 475 años**)», fuente «Art. 11.1».<br>*src/datos_sitio.py:194-215* | El Art. 11.1 **confirma Z = 0,45 para la Zona 4** (Tabla N° 1) y dice: «Este factor representa la aceleración máxima horizontal en suelo rígido con una probabilidad de **10 % de ser excedida en 50 años**». No escribe «475 años». La equivalencia es correcta y estándar, pero es una derivación del proyectista presentada como concepto de la norma.<br>*E.030 (2026), Art. 11.1 y Tabla N° 1, pág. PDF 9* |
| `E030-03` | MEDIA | CONTRADICE | E.030 | **El mejor argumento para descartar E.030 está en su Art. 4 y no se usa** — El descarte de E.030 se justifica **solo por periodo de retorno**: «Sec. 0.4 descarta el sismo de 475 años de E.030 en favor del PGA de Tr = 1000 años del Manual de Puentes».<br>*src/datos_sitio.py:158-165 y :204-213 · docs/manifiesto_citas.md §10* | El Art. 4 «Ámbito de aplicación» acota la norma antes de que el periodo de retorno entre en juego: «La presente Norma Técnica es de cumplimiento obligatorio a nivel nacional y se aplica a: a) El diseño de **edificaciones** nuevas. b) El reforzamiento de **edificaciones** existentes y la reparación de estructuras que resulten dañadas por la acción de los sismos.» Un cabezal de alcantarilla en una carretera no es una edificación. Ese es un argumento de ámbito, más limpio y más fuerte que el de periodo de retorno, y el expediente no lo invoca en ningún sitio. La consecuencia práctica es que la memoria defiende el descarte por la vía discutible (¿por qué no usar los dos?) en vez de por la vía cerrada.<br>*E.030 (2026), Art. 4, pág. impresa 7* |
| `COH-02` | MEDIA | CONTRADICE | Coherencia interna | **El código se aparta de su fuente de verdad declarada, con acierto, y sin autorización escrita** — `Claude.md`: «Fuente normativa única: `docs/hoja_de_ruta_alcantarillas_v8.md`… **Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta**». `constantes_normativas.py:124-126`: «Aquí **gana la fuente primaria HDS-5** por verificación externa; la hoja de ruta debe corregirse».<br>*Claude.md · src/constantes_normativas.py:124-126 · docs/hoja_de_ruta_alcantarillas_v8.md:436, 440, 797, 908* | La decisión es **correcta en el fondo** (ver COH-01) y está declarada, que es lo importante. Lo que falta es la regla: la excepción «una verificación externa contra la fuente primaria gana a la hoja de ruta» no está escrita en ningún sitio, de modo que el proyecto tiene hoy dos jerarquías incompatibles y un precedente sin norma. Y el número sigue mal en la fuente de verdad: quien la lea sin leer el código diseña con 19.62.<br>*—* |
| `F-01` | MEDIA | CONTRADICE | Datos vs constantes | **El corredor de ~5 km está endurecido en un archivo de código** — `AMBITO_CORREDOR = "todo el corredor (el terraplén de ~5 km de la Fase 0-bis de la hoja de ruta, num. 150)"`, valor por defecto del campo `ambito` de todo dato de sitio.<br>*src/datos_sitio.py:94* | *Clasificación.* Es un hecho de **este** expediente escrito como constante de módulo, y la memoria lo imprime en la declaración de datos de sitio. No mueve ningún número, pero es exactamente lo que la etiqueta `[S]` existe para evitar: aplicar la app a otra carretera y heredar en silencio «~5 km». El ámbito debería ser un dato del proyecto, no un literal del archivo que define la etiqueta.<br>*—* |
| `F-02` | MEDIA | CONTRADICE | Datos vs constantes | **El barrido de literales no recorre cli.py ni gui/app.py** — `tests/test_sin_literales.py` se presenta como la guardia de «todo literal numérico bajo `src/`», con seis archivos exentos.<br>*tests/test_sin_literales.py:1-60* | *Alcance.* `cli.py` (69 KB) y `gui/app.py` quedan fuera del recorrido, y son justamente donde se fijan defaults de línea de comandos y de formulario. La regla de arquitectura de `Claude.md` habla de «ningún módulo», no de «ningún módulo bajo src/». *Verificado*: las quince marcas `# literal-ok` del árbol son todas partes de fórmula transcrita (el 45 de Kₐ de Rankine, el 1/3 del centroide, los exponentes de Manning, π/4, D/4, 4/3) — ninguna es abusiva. El hueco es de cobertura, no de contenido.<br>*—* |
| `MEM-02` | MEDIA | CONFIRMA | Memoria exportada | **Lo que la memoria sí hace bien** — Se generaron las dos memorias (`--alcance expediente` y `--alcance perfil`) sobre `tests/ejemplo_puntos.csv` y se leyeron enteras, junto con las dos plantillas y M11.<br>*src/plantillas/memoria_alcantarillas.html · memoria_perfil.html · src/modulos/M11_reporte.py* | *Verificado sobre el HTML generado.* · · **Ninguna cita sale truncada**: no hay recorte por longitud en M11 ni en las plantillas. · · Las **plantillas no contienen ningún numeral ni número normativo escrito a mano**: todo lo normativo llega desde los modelos. · · La **analogía `[N→]` se declara como analogía**, con las palabras «ADOPCIÓN POR ANALOGÍA SOBRE UN VACÍO VERIFICADO, a nivel de PERFIL» y la distinción entre lo que destraba el perfil y lo que sigue pendiente de expediente. · · La **adopción sin respaldo normativo de la Clase F se imprime** con esas palabras, en el Tablero 1. · · La **advertencia de trazabilidad incompleta del PGA** aparece (9 menciones de «trazabilidad»). · · `--proyecto` no trae valor por defecto: sin declararlo, la memoria dice «(proyecto no declarado)». · Lo que la memoria arrastra son los **errores de página** de EG-01 y HID-02, no defectos de la capa de reporte.<br>*—* |
| `HDS-06` | MEDIA | CONTRADICE | HDS-5 | **El «Cap. IV» que se cita para la zona de transición es, en la 3.ª edición, el capítulo de paso de fauna acuática** — `metodo_transicion_hds5`, fuente: «HDS-5 3.ª ed., abril 2012, **Cap. IV** y Apéndice A (curva de transición tangente, sin ecuación publicada)».<br>*src/criterios_adoptados.py:719-722 · docs/manifiesto_citas.md §7* | En la 3.ª edición el índice dice «**CHAPTER 4 — CULVERT DESIGN FOR AQUATIC ORGANISM PASSAGE (AOP)**». Ese capítulo no menciona la zona de transición del control de entrada en ningún punto. La descripción de la curva tangente está en el **Apéndice A, Sec. A.1** (y el fenómeno se introduce en el Cap. 3). La mitad «Apéndice A» de la cita es correcta; la mitad «Cap. IV» apunta a un capítulo que en esta edición trata de otra cosa — es una referencia arrastrada de la 2.ª edición de 1985, cuya numeración de capítulos era distinta.<br>*HDS-5 3.ª ed., índice pág. xiii y encabezado del Cap. 4 (PDF 17 y 127) · Sec. A.1 pág. A.1 (PDF 190)* |
| `AAS-07` | MEDIA | CONTRADICE | AASHTO LRFD | **El punto de aplicación del incremento sísmico se declara sin norma, y AASHTO lo trata** — `punto_aplicacion_incremento_sismico = None`, etiqueta `[A]`: «la altura de aplicación es una **convención de la literatura** (Seed-Whitman la sitúa en ~0.6H)», con sensibilidad (0.333, 0.6)·H y sin numeral.<br>*src/criterios_adoptados.py:579-599 · docs/manifiesto_citas.md §8 y §11.b* | AASHTO sí se pronuncia, en el comentario del artículo de empuje sísmico: «C11.6.5.3: Past practice for locating the resultant of the static and seismic earth pressure for external wall stability has been to either **assume a uniform distribution** of lateral earth pressure for the combined static plus seismic stress or, if the static and seismic components of earth pressure are computed separately…» y el Apéndice A11.3.1 desarrolla el reparto. No fija un número único —el `[A]` es defendible—, pero la afirmación de que solo hay «convención de la literatura» pasa por alto que el cuerpo normativo que el proyecto adopta como Vía 1 describe el procedimiento y acota las alternativas.<br>*AASHTO LRFD 9.ª ed., C11.6.5.3 pág. 11-30 (PDF 1499) y Apéndice A11.3.1* |
| `PRO-05` | MEDIA | CONTRADICE | AASHTO M 170M | **La memoria imprime las designaciones imperiales de un proyecto que opera en SI** — `NORMA_PRODUCTO["concreto_reforzado"] = "ASTM C76 / AASHTO M170"`, que es la etiqueta que M11 imprime en la memoria. El mismo par aparece en `D_MAX` y en `diametros_normalizados`.<br>*src/modulos/M2_material.py:149 · src/constantes_normativas.py:133 · src/modulos/M11_reporte.py* | El documento que el proyecto tiene ahora en `normas/` se designa «**AASHTO Designation: M 170M-04 / ASTM Designation: C 76M-02**», titulado «Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe **[Metric]**», y su §1.2 dice: «This specification is the **metric counterpart of M 170**». · M 170 y C 76 son las versiones en pulgadas; M 170M y C 76M las métricas. `Claude.md` impone que «todo el código opera en SI» y que la conversión solo ocurre en la capa de reporte — y aquí es justo la capa de reporte la que nombra las imperiales. El repositorio alterna «AASHTO M170» y «AASHTO M-170M» según el archivo.<br>*AASHTO M 170M-04, encabezado de designación y §1.2 (PDF pág. 1)* |

## 4. Bajas

| ID | Sev | Veredicto | Documento | Afirmación del repo (archivo:línea) | Qué dice el PDF (documento, página) |
|---|---|---|---|---|---|
| `PUE-14` | BAJA | CONTRADICE | Manual de Puentes | **El recubrimiento de alcantarillas de 2.0 in lleva dos condiciones que no se recogen** — «el Manual sí usa la palabra “recubrimiento” para alcantarillas y da **2.0 in / 50 mm**».<br>*src/criterios_adoptados.py:1129-1136* | La fila existe y **confirma**, dentro de «Alcantarillas de cajón de concreto prefabricados»: «forjados para ser utilizados como superficie de conducción → 2.5 in · forjados con **inferior a 2 pies de relleno** que no se utilicen como una superficie de conducción → **2.0 in** · todos los demás miembros → 1.0 in». Los 2.0 in son de *alcantarillas cajón prefabricadas* con menos de 600 mm de relleno, no de alcantarillas en general. 2.0 in son 50.8 mm.<br>*Manual de Puentes, Tabla 2.9.1.5.5.3-1, pág. impresa 378 (PDF 379)* |
| `HID-12` | BAJA | CONTRADICE | Manual de Hidrología | **El diámetro mínimo de selva alta es específico de TMC y es una recomendación** — `DIAMETRO_MIN_SELVA_ALTA = 1.22 # m = 48"; NO aplica en costa (4.1.1.3.7 a)`, con nombre genérico.<br>*src/constantes_normativas.py:30* | **Confirma** numeral, página (79) y valor: «**Se recomienda** utilizar, en zonas de selva alta, con las características físicas y geomorfológicas indicadas en el párrafo anterior, como diámetro mínimo **alcantarillas TMC Ø 48"**». El Manual escribe 48" (1.2192 m, redondeado a 1.22 ✔), lo limita a **TMC** y lo condiciona a una lista de cuatro características geomorfológicas. El nombre de la constante no lleva ninguna de las tres restricciones. «No aplica en costa» ✔.<br>*Manual de Hidrología, num. 4.1.1.3.7 a), pág. impresa 79 (PDF 82)* |
| `COH-03` | BAJA | CONTRADICE | Coherencia interna | **Las líneas que el código cita de la hoja de ruta están corridas siete** — «docs/hoja_de_ruta_alcantarillas_v8.md (**líneas 432, 436, 790 y 901**) sigue escribiendo 19.62».<br>*src/constantes_normativas.py:124-126* | *Defecto interno.* El 19.62 está en las líneas **436, 440, 797 y 908**. La 432 es el encabezado «### 4.3 Control de salida [C]»; falta la 440, que es la «Nota de unidades» —la más explícita de las cuatro—. Mismo patrón de desfase que las referencias del manifiesto, esta vez dentro del código.<br>*—* |
| `HDS-04` | BAJA | CONFIRMA | HDS-5 | **El +0.7 de inglete y el ke de 0.7 de inglete son dos coeficientes distintos con el mismo número** — `Ks = +0.7` para embocadura ingleteada (corrección por pendiente) y, en la misma cadena de cálculo, `ke` como coeficiente de pérdida de entrada.<br>*src/constantes_normativas.py:104-107 · src/criterios_adoptados.py (`ke_entrada`)* | Los dos **confirman por separado**: Kₛ = +0.7 para «mitered inlets» en la Sec. A.2.1 (pág. A.2), y kₑ = 0.7 para «Mitered to conform to fill slope» en la Tabla C.2 (pág. C.6). Son magnitudes sin relación que coinciden en valor y en condición. Con inglete, el mismo 0.7 aparece dos veces por dos motivos distintos: vale la pena anotarlo antes de que alguien los cruce.<br>*HDS-5 3.ª ed., Sec. A.2.1 pág. A.2 · Tabla C.2 pág. C.6* |

## 5. Verificado correcto (OK)

| ID | Sev | Veredicto | Documento | Afirmación del repo (archivo:línea) | Qué dice el PDF (documento, página) |
|---|---|---|---|---|---|
| `OK-01` | OK | CONFIRMA | AASHTO LRFD | **La cita falsa que el proyecto retiró era efectivamente falsa** — §8 declara retirada la cita «`clase_sitio = "F_con_excepcion_periodo_corto"` — excepción para estructuras de periodo fundamental corto (≤ 0.5 s)», con la afirmación de que «la dispensa **no está** en el Art. 3.10.3.1, ni en C3.10.3.1, ni en tabla o nota alguna».<br>*src/criterios_adoptados.py:386-435 · docs/manifiesto_citas.md §8* | **Re-verificado de forma independiente contra la 9.ª edición**: el Art. 3.10.3.1, el comentario C3.10.3.1, la Tabla 3.10.3.1-1 y la Tabla C3.10.3.1-1 no contienen ninguna dispensa por periodo corto. Lo único rotulado «Exceptions» en la tabla trata de propiedades del suelo desconocidas. Y el Art. 3.10.2 exige el procedimiento específico de sitio de forma incondicional cuando «The site is classified as Site Class F». · La retirada es correcta y bien fundada. Es el trabajo de verificación mejor hecho del expediente.<br>*AASHTO LRFD 9.ª ed., Arts. 3.10.2 y 3.10.3.1, Tablas 3.10.3.1-1 y C3.10.3.1-1, págs. 3-101 a 3-103* |
| `OK-02` | OK | CONFIRMA | HDS-5 | **La curva de transición sin ecuación publicada existe y está descrita como el proyecto dice** — `metodo_transicion_hds5`: «HDS-5 no interpola: en la zona 3.5 < q* < 4.0 traza una **curva TANGENTE** a las dos ramas, un empalme empírico ajustado sobre sus datos de laboratorio **del que no publica ecuación cerrada**. Quien prescribe la recta es Sec. 4.2 de la hoja de ruta, no la fuente primaria.»<br>*src/criterios_adoptados.py (`metodo_transicion_hds5`) · src/modulos/M4_control.py:14-90* | Literal, en la Sec. A.1: «Between the unsubmerged and the submerged conditions, there is a transition zone for which the NBS research provided only limited information. The transition zone is defined empirically by **drawing a curve between and tangent to** the curves defined by the unsubmerged and submerged equations.» Confirma los tres extremos: es tangente, es empírica y no hay ecuación. La simplificación está declarada como `[C]`, se invoca solo cuando un punto cae de verdad en la transición, y M4 rechaza con `DatoInvalidoError` cualquier otro valor del criterio. Es el manejo de vacío mejor construido del repositorio.<br>*HDS-5 3.ª ed., Sec. A.1, pág. A.1 (PDF 190)* |
| `OK-03` | OK | CONFIRMA | HDS-5 | **Las tres filas de constantes de embocadura son exactas** — `HDS5_INLET`: concreto square edge w/headwall (0.0098, 2.00, 0.0398, 0.67) · CMP headwall (0.0078, 2.00, 0.0379, 0.69) · CMP mitered (0.0210, 1.33, 0.0463, 0.75).<br>*src/constantes_normativas.py:99-106* | Tabla A.1, pág. A.8, filas 1 y 2: · · Chart 1, Circular Concrete, Scale 1, Square edge w/headwall → K 0.0098 · M 2.0 · c 0.0398 · Y 0.67 ✔ · · Chart 2, Circular CM, Scale 1, Headwall → K 0.0078 · M 2.0 · c 0.0379 · Y 0.69 ✔ · · Chart 2, Circular CM, Scale 2, Mitered to slope → K 0.0210 · M 1.33 · c 0.0463 · Y 0.75 ✔ · Doce números, doce coincidencias. La página A.8 es correcta.<br>*HDS-5 3.ª ed., Tabla A.1, pág. A.8 (PDF 197)* |
| `OK-04` | OK | CONFIRMA | Manual de Hidrología | **La cita textual larga de V_MIN coincide tilde por tilde** — Transcripción entrecomillada de cuatro líneas en `constantes_normativas.py:36-39` y repetida en M5.<br>*src/constantes_normativas.py:36-39 · src/modulos/M5_verificaciones.py:186-189* | Comparación palabra por palabra contra el PDF: «Se deberá verificar que la velocidad mínima del flujo dentro del conducto no produzca sedimentación que pueda incidir en una reducción de su capacidad hidráulica, recomendándose que la velocidad mínima sea igual a 0.25 m/s.» Coincidencia literal, incluidas tildes y puntuación. Es la única cita textual larga del repositorio y está impecable. (La página, ver HID-09.)<br>*Manual de Hidrología, num. 4.1.1.3.6, págs. impresas 76-77* |
| `OK-05` | OK | CONFIRMA | EG-2013 | **El mapeo de secciones del EG-2013 y la corrección del nombre «SUBSECCION» son correctos** — `SECCION_EG2013 = {concreto_simple: "505", concreto_reforzado: "506", tmc: "507", hdpe: "508"}` y `SECCION_CABEZALES = "503"`, con la corrección declarada de que «son Secciones completas del Capítulo V, no subsecciones de ninguna “Sección 500”: esa denominación no existe».<br>*src/constantes_normativas.py:190-196 · src/modulos/M8_estructural.py:143 · M9_cabezal.py:179* | Títulos reales: **502** Rellenos para Estructuras (pág. 893) · **503** Concreto Estructural (903) · **504** Acero de Refuerzo (937) · **505** Tubería de Concreto Simple (947) · **506** Tubería de Concreto Reforzado (957) · **507** Tubería Metálica Corrugada (967) · **508** Tubería de Polietileno de Alta Densidad (979). No existe ninguna «Sección 500». `NUMERAL_9_1` confirma con su página: 503.01 está en la **pág. 905**. La remisión 506.02 → AASHTO M-170M está en la **pág. 959**, tal como se declara.<br>*EG-2013, Capítulo V, págs. impresas 893-987* |
| `OK-06` | OK | CONFIRMA | E.050 · E.030 · Manual de Puentes | **Los factores de seguridad, la zonificación y el perfil de suelo confirman sin excepción** — Los diez valores de `FS`, `ZONA_SISMICA_LA_UNION = 4`, `Z_E030 = 0.45`, `PERFIL_SUELO_PRESUNTO = "S5"`, `SPT_PROF_MIN = 15.0`, `NUMERAL_C_PHI`, `NUMERAL_ZAPATA_TALUD_E050`, `NQ_ZAPATA_EN_TALUD = 0.0`, `CARGA_VIVA = "HL-93"` y el Tr = 1000 años del PGA.<br>*src/constantes_normativas.py:266-284, :236-237 · src/datos_sitio.py* | · E.050 Art. 20 (pág. 33): φ = 0 en cohesivos, c = 0 en friccionantes ✔ · Art. 30.1-30.2: doble verificación exacta ✔ · Art. 38.4.3: 15 m ✔ · · E.030 Anexo II: **La Unión, provincia de Piura → Zona 4** ✔ (y existen otras «La Unión» en Zona 3: la insistencia del repositorio en nombrar distrito y provincia está justificada) · Art. 11.1, Tabla N° 1: Zona 4 → Z = 0,45 ✔ · Art. 14.6, Tabla N° 2: S5 «Suelos excepcionales», primera viñeta «Suelos potencialmente licuables» ✔ · · Manual de Puentes: num. 2.4.3.8.2 «Subpresiones» pág. 113 ✔ · num. 2.4.3.2.2.1 (HL-93) pág. 103 ✔ · num. 2.8.1.3.1.2c: Nq = 0.0 ✔ · «7 % de probabilidad de excedencia en 75 años (equivalente a un periodo de retorno de **1000 años**). Los mapas… se presentan en el **Apéndice A3**» ✔<br>*E.050 págs. 33, 39, 51, 72 · E.030 Anexo II y Arts. 11.1, 14.6 · Manual de Puentes págs. 103, 113, 122, 272* |
| `OK-07` | OK | CONFIRMA | EG-2013 · normas de producto | **El vacío de altura mínima sí es real en el corpus peruano, y el paso de 0.15 m sí reproduce la serie** — §14.a puntos 1 y 3, y `D_PASO = 0.15 # m; reproduce las series de 6" y 150 mm`.<br>*src/criterios_adoptados.py:1076-1121 · src/constantes_normativas.py:130* | · **EG-2013**: lectura íntegra de las Secciones 502, 505, 506 y 507 con búsqueda de «altura de relleno», «recubrimiento», «cobertura», «relleno mínimo», «sobre la clave», «0,30» y «0,60». La **única** cláusula de altura mínima sobre la clave en todo el Capítulo V es la de 508.07, para HDPE. El vacío para concreto y TMC **confirma**. La cláusula constructiva de 508.08 («el equipo y vehículos pesados no deberán circular sobre la estructura antes que la altura de relleno mínima sobre la misma sea de 0,30 m») también confirma, en la pág. 985. · · **Series de diámetros**: M 170M Tabla 3 da 300, 375, 450, 525, 600, 675, 750, 825, **900, 1050, 1200, 1350, 1500…** y A760 Tabla 1 da la misma progresión. De 900 mm en adelante el paso es exactamente **150 mm**. El arranque en 0.90 m y el paso de 0.15 m reproducen la serie real. ✔<br>*EG-2013 Secciones 502-508 · AASHTO M 170M-04 Tablas 1-5 · ASTM A760 Tabla 1* |
| `OK-08` | OK | CONFIRMA | AASHTO LRFD | **El peso específico del concreto y los factores de resistencia están bien derivados y bien atribuidos** — `peso_especifico_concreto_kn_m3 = 23.56`, fuente «Tabla 3.5.1-1 + Comentario C3.5.1, pág. 3-21 (0.150 kcf, concreto normal armado)» · `phi_flexion = 0.9`, `phi_corte = 0.9`.<br>*src/criterios_adoptados.py, criterios `peso_especifico_concreto_kn_m3` y `procedimiento_flexion_corte_aashto_sec5`* | Tabla 3.5.1-1 «Unit Weights», pág. **3-21** ✔: «Concrete — Normal Weight with f'c ≤ 5.0 ksi → **0.145 kcf**». C3.5.1: «the unit weight of reinforced concrete is generally taken as **0.005 kcf greater** than the unit weight of plain concrete». 0.145 + 0.005 = 0.150 kcf = 23.56 kN/m³. · La derivación es correcta y —esto es lo notable— **está atribuida a las dos piezas que la componen**, tabla y comentario, en vez de presentarse como un valor tabulado. Art. 5.5.4.2 confirma φ = 0.90 para secciones de concreto armado controladas por tracción y φ = 0.90 para corte y torsión en concreto de peso normal.<br>*AASHTO LRFD 9.ª ed., Tabla 3.5.1-1 y C3.5.1 pág. 3-21 · Art. 5.5.4.2 pág. 5-29* |
| `OK-09` | OK | CONFIRMA | AASHTO M 170M | **M 170M clasifica por D-load, no por altura: la afirmación negativa se sostiene** — «**M 170M clasifica por D-load (resistencia), no por altura** — no existe la tabla clase-a-altura que el criterio decía que iba a extraer de ella».<br>*src/criterios_adoptados.py:1063-1065* | Confirmado en la propia norma y, de rebote, en el EG-2013. Las Tablas 1 a 5 de M 170M son «Design Requirements for Class I…V Reinforced Concrete Pipe» y se organizan por diámetro interno, espesor de pared y área de armadura; la nota al pie define el criterio de aceptación como «D-load to produce a 0.3-mm crack» y «D-load to produce the ultimate load». No hay ninguna tabla de clase por altura de relleno. · El EG-2013 lo confirma desde fuera, en su num. 506.05 b): «la carga necesaria para producir una grieta de 0,3 mm o la carga última, no podrá ser inferior a la prescrita en la tabla que corresponda de la especificación AASHTO M-170M».<br>*AASHTO M 170M-04, Tablas 1-5 y notas · EG-2013 pág. impresa 962* |

---

## 6. Trampas de vocabulario

El brief pedía buscar, más allá de la de «recubrimiento» que el propio proyecto documenta,
otras palabras que signifiquen cosas distintas en el código y en la norma. Salieron cuatro,
todas con ficha propia: `VOC-01`, `VOC-02`, `VOC-03`, `VOC-04`.

| Palabra | Sentido en el repo | Sentido en la norma | Ficha |
|---|---|---|---|
| **recubrimiento** | (a) relleno sobre la clave, (b) recubrimiento del acero en el concreto | y además (c) el `Bc/8` de AASHTO Art. 12.6.6.3, que crece con el diámetro y no es un valor fijo | `VOC-02` |
| **luz** | ancho del cauce que exige el cruce | el Manual de Hidrología no la define; el Manual de Puentes le da dos sentidos incompatibles en la misma página del glosario; AASHTO la mide entre caras interiores | `VOC-03` |
| **cota** vs **tirante** | `cota_TW` (msnm) y `TW` (tirante, m) conviven con nombres casi iguales | el HDS-5 usa TW siempre como tirante aguas abajo, medido desde el invert de salida | `VOC-01` |
| **Clase F** | clase de sitio sísmica (E.030 / Manual de Puentes) | y a la vez la clase de resistencia del tubo de concreto en ASTM C76 / M 170M | `VOC-04` |

Las otras que el brief nombraba —**resguardo** / **borde libre**, **subrasante** / **rasante**,
**diámetro** frente a **luz**— se buscaron y **no** produjeron hallazgo: el repo las usa de
forma consistente con su fuente. El resguardo es siempre el del Manual de Suelos (napa a
subrasante) y el código nunca lo confunde con un borde libre hidráulico; la cadena
rasante = subrasante + `e_paq` está bien orientada en M7. Eso se registra como cobertura,
no como defecto.

## 7. El manifiesto contra el código

`MAN-01`, `MAN-02`, `MAN-03`, `MAN-04` y, en coherencia interna,
`COH-02`, `COH-03`.

El manifiesto es el índice por el que un revisor entra al expediente, y hoy **no describe
el árbol que acompaña**:

- Los recuentos de §12 («los 33 criterios `[A]`») y §13 («1 `[N→]` · 1 `[S]` · 14 `[C]` ·
  30 `[A]`») no son los que devuelve el archivo. Ejecutado sobre este SHA,
  `criterios_adoptados.py` da **46 criterios: 30 `[A]` · 13 `[C]` · 2 `[N→]` · 1 `[S]`**, con
  **23 sin valor**. §12 y §13 además se contradicen entre sí (`MAN-02`).
- Cuatro criterios que el manifiesto inventaría como vacíos **tienen hoy valor**
  (`MAN-01`), y un criterio retirado sigue listado (`MAN-03`).
- De 296 referencias `archivo:línea` del manifiesto, **al menos 66 no llevan a lo que dicen
  llevar** (`MAN-04`). El test `tests/test_manifiesto_citas.py` no las atrapa porque las
  filas sin identificador entre comillas invertidas están declaradas excepción
  («referencias de prosa», tope `MAX_REFERENCIAS_DE_PROSA = 90`) y solo se comprueba que la
  línea exista, no que diga algo.

## 8. Variables de proyecto endurecidas como constante

Bloque F del brief: todo lo que cambiaría al aplicar la app a **otra** carretera debe ser
variable. Fichas `F-01`, `F-02`, más lo que aparece
distribuido en otras fichas.

| Valor | Dónde vive hoy | Qué es en realidad | Ficha |
|---|---|---|---|
| El corredor de ~5 km (progresivas, cotas de referencia) | endurecido en un archivo de código | dato de sitio `[S]`, columna del CSV o cabecera del proyecto | `F-01` |
| `PGA_roca_B = 0.50 g` · zona sísmica 4 | constante del proyecto | lectura de mapa `[S]` para **esta** ubicación | `E030-01`…`E030-03` |
| `clase_sitio` | criterio `[A]` con valor | sale del estudio geotécnico del punto | `E050-01`, `VOC-04` |
| `CBR`, `NF_profundidad_m`, `sucs_fundacion` | corredor `[S]` sin valor | correcto como `[S]`, pero declarados a nivel corredor y no por punto | `SUE-04` |
| `D_MAX` por material (2.70 / 2.10 / 1.50) | `constantes_normativas.py` con marca `VERIFICAR` | tope de catálogo del proveedor, no constante normativa | `PRO-01`…`PRO-05` |
| `v_max_hdpe` = `v_max_tmc` = 4.6 m/s | criterio `[C]` cerrado | adopción sobre una fuente **ausente** del repositorio (WSDOT) | `ANA-01` |
| El barrido de literales | no recorre `cli.py` ni `gui/app.py` | la regla de arquitectura no cubre los dos archivos con más números sueltos | `F-02` |

## 9. La memoria exportada

`MEM-01`, `MEM-02`, `MEM-03`. Se generó la memoria en sus dos alcances
(expediente y perfil) y se comparó lo **impreso** contra lo verificado en los bloques
anteriores.

- `MEM-01` — el matiz «recomienda, no prohíbe» que el manifiesto declara como lo único que
  se imprime de V2 **no llega a la memoria**.
- `MEM-03` — la justificación de `F_pga` imprime una convergencia de la que ha desaparecido
  la fila que la sostenía.
- `MEM-02` — lo que la memoria **sí** hace bien, registrado como cobertura.

## 10. Fuera del alcance por falta de documento

Filas del manifiesto que **no se pudieron verificar** porque el documento no está en el
repositorio. No son hallazgos: son deuda de verificación conocida.

| Documento ausente | Filas que dependen de él |
|---|---|
| **WSDOT Hydraulics Manual M 23-03.12** | §10-bis entera: `v_max_hdpe = 4.6` y `v_max_tmc = 4.6` (Cap. 8, S8-6, Tabla 8-4, pp. 8-27/8-28) · la referencia comparativa de §14.a a la Tabla 8-6 (cobertura reducida a 0.5 ft en concreto Clase V), que es el único apoyo documental del argumento de conservadurismo que la memoria imprime |
| **AASHTO M294** | `D_MAX["hdpe"] = 1.50` · la afirmación negativa de que M294 no tiene tabla de clase por altura (`CA:829-832`) · la fila HDPE de `NORMA_PRODUCTO` y de `diametros_normalizados` |
| **ASTM A-807** | El contenido al que remiten 507.05/.06/.08 del EG-2013. **Ojo**: para lo demás que se le atribuye, A-807 parece ser el documento equivocado — ver `PRO-04`. La «relación luz/corrugación» ya está en la Tabla 6 de M 36 y la Tabla 1 de A760, ambas adjuntas |
| **ASTM A796/A796M** y **A798/A798M** *(no estaban en la lista del proyecto)* | Son las que M 36 y A760 citan de verdad para el **diseño estructural** (calibre por altura de cobertura) y para la **instalación** del acero corrugado. Es donde vive la mitad TMC de `clases_producto_por_relleno`, que hoy se difiere a A-807 |
| **ASTM C76** | El lado imperial de `D_MAX["concreto_reforzado"]` y de `NORMA_PRODUCTO`. **Sustituible en la práctica**: M 170M-04 se declara la contraparte métrica de M 170 y equivalente a C 76M-02 |
| **DG-2018 (Diseño Geométrico)** | `remanso_derecho_via` · `talud_terraplen` · `pendiente_relleno_trasdos_i` · la sección tipo del expediente |
| **HEC-14** | `longitud_proteccion_salida` |
| **Ley 29338 y su reglamento** | La faja marginal en `remanso_derecho_via` (V5) |
| **Series SENAMHI · datos ANA / Junta de Usuarios** | `homogeneidad_serie_fen` · `TW_receptor` · `Q_receptor_m3s` y `cota_TW` del CSV |
| **Meyerhof (1957) original** | Los valores de N_cq y N_γq. Las Figuras 2.8.1.3.1.2c-1 y -2 **sí** se verificaron como existentes y correctamente numeradas, pero son ábacos raster: los valores no son legibles por texto |
| **Apéndice A3 del Manual de Puentes (mapas)** | La **lectura** de `PGA_roca_B = 0.50 g` sobre La Unión. El mapa existe y su título y periodo de retorno confirman; la isolínea sobre Piura es una imagen y no se puede leer con la resolución disponible |
| **Estudio geotécnico del expediente** | `NF_profundidad_m`, `cbr_subrasante` y `sucs_fundacion` por punto · `clase_sitio` · `c_phi_fundacion` · `capacidad_portante_adm` |

Además queda fuera, por definición, el bloque §12 del manifiesto: los criterios `[A]` no
tienen numeral que confrontar. Lo que sí se verificó de ellos es la **tabla o el artículo
subyacente** cuando lo citan, y ahí es donde salieron varios de los hallazgos.

---

## 11. Fichas

Cada ficha lleva la afirmación del repo con su `archivo:línea`, lo que dice el documento
con su página impresa, y el veredicto.

### 11.1 Críticas

### `PUE-01` — El numeral que sostiene la sobrecarga de tráfico en el trasdós es «Aparatos de Apoyo»

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/constantes_normativas.py:235 · :261 · src/modulos/M9_cabezal.py:588 · manifiesto §3
**Ubicación PDF** Manual de Puentes, num. 2.1.4.3.9 → pág. impresa 91-92 (PDF 92-93) · num. 2.4.2.2 → pág. impresa 102 (PDF 103)

**Afirmación del repo.** `SOBRECARGA_TRASDOS_H_EQ = 0.60` m de relleno equivalente, atribuido al **num. 2.1.4.3.9, pág. 91**. El mismo numeral viaja a la memoria dentro de `NUMERAL_SOBRECARGA_TRASDOS` y sostiene `presion_sobrecarga_trasdos()`: p = γ·0.60·k_a.

**Qué dice el documento.** El num. 2.1.4.3.9 se titula **«Aparatos de Apoyo»** y trata de dispositivos de apoyo de la superestructura; remite a AASHTO Sección 14. No menciona relleno, trasdós ni sobrecarga.
El 0.60 m está en **num. 2.4.2.2 «Cargas de Suelo: EH, ES, y DD»**:

> Cuando se prevea tráfico a una distancia horizontal, medida desde la parte superior de la estructura, menor o igual a la mitad de su altura, las presiones serán incrementadas añadiendo una sobrecarga vertical **no menor que** la equivalente a 0,60 m de altura de relleno.

La condición «tráfico a ≤ H/2» que el código sí declara es correcta. El «no menor que» (es un mínimo, no un valor) y la exención por losa de aproximación no se recogen.

### `PUE-02` — Bajo la Vía 1 declarada, 0.60 m es la fila menos conservadora de la tabla y no aplica a ningún cabezal de este proyecto

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/constantes_normativas.py:235 · src/modulos/M9_cabezal.py:588 · docs/hoja_de_ruta_alcantarillas_v8.md (Sec. 0.2)
**Ubicación PDF** AASHTO LRFD 9.ª ed., Tabla 3.11.6.4-1 y C3.11.6.4, Sección 3 · Manual de Puentes, índice de 2.4.4.1

**Afirmación del repo.** El proyecto declara en Sec. 0.2 la **Vía 1: AASHTO LRFD de extremo a extremo** para el diseño estructural, con E.060 solo para durabilidad y recubrimientos. Sobre esa base adopta h_eq = 0.60 m sin dependencia de la altura del muro.

**Qué dice el documento.** **Tabla 3.11.6.4-1 «Equivalent Height of Soil for Vehicular Loading»**: altura de estribo 5.0 ft → h_eq 4.0 ft; 10.0 ft → 3.0 ft; ≥ 20.0 ft → 2.0 ft. Los 0.60 m ≈ 2.0 ft son la fila de **muros de 20 ft (6.1 m) o más**. Un cabezal de 2–4 m exigiría 3.0–4.0 ft = 0.91–1.22 m, entre 1.5× y 2× lo adoptado. El comentario de AASHTO añade que los valores tabulados «are generally greater than the traditional 2.0 ft of earth load historically used».
Y el Manual de Puentes **no incorpora AASHTO 3.11.6**: su num. 2.4.4.1 «Empuje del Suelo» va de 2.4.4.1.1 a 2.4.4.1.5.4 y salta a 2.4.5. Por eso el 0.60 m plano del Manual y la tabla de AASHTO conviven sin que el repositorio declare cuál gobierna.

### `PUE-03` — El factor mínimo de EV no corresponde a ninguna fila de la tabla, y el que aplica al cabezal es más exigente

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:1343 (valor) y :1379-1380 (la afirmación)
**Ubicación PDF** Manual de Puentes, Tabla 2.4.5.3.1-2, pág. impresa 143 (PDF 144) · AASHTO LRFD 9.ª ed., Tabla 3.4.1-2, pág. 3-18

**Afirmación del repo.** `factores_carga_aashto["Resistencia I"]["EV"] = {max: 1.35, min: 0.90}`, etiqueta `[C]`. Y no es un descuido de tecleo: la justificación del criterio **lo afirma expresamente** — «la tabla fuente da EV mínimo **0.90, no 1.00**».

**Qué dice el documento.** En la **Tabla 2.4.5.3.1-2 (= 3.4.1-2 AASHTO)**, EV se desglosa por tipo de elemento y *ninguna fila* es (1.35, 0.90):
· Estabilidad global — 1.00 / N/A
· **Muros y estribos de retención — 1.35 / 1.00**
· Estructura rígida enterrada — 1.30 / 0.90
· Pórticos rígidos — 1.35 / 0.90
· Estructuras flexibles enterradas — 1.50 · 1.30 · 1.95 / 0.90
El par transcrito toma el máximo de «muros y estribos de retención» y el mínimo de otra fila. Para un cabezal —que M9 modela como muro de contención— el mínimo es **1.00**. Usar 0.90 rebaja un 10 % el peso estabilizante de tierra en E2 (volteo), E3 (deslizamiento) y V7 (flotación), que es la dirección insegura.

### `PUE-04` — El vacío de factores de carga se declara sobre las páginas que contienen las tablas

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** docs/manifiesto_citas.md §3, §8 y §12 · src/constantes_normativas.py:254-259
**Ubicación PDF** Manual de Puentes, num. 2.4.5.3 pág. impresa 140; Tablas en págs. impresas 143-144 (PDF 144-145)

**Afirmación del repo.** El manifiesto declara `factores_carga_aashto = None` — «vacío que bloquea toda combinación de carga» — con la razón de que «el Manual nombra las combinaciones y **no transcribe las Tablas 3.4.1-1/-2**», citando **num. 2.4.5.3, págs. 140-143**. `constantes_normativas.py:254-259` repite el argumento.

**Qué dice el documento.** El Manual **sí las transcribe, completas y con sus valores**, dentro del rango de páginas que el propio repositorio cita:
· **Tabla 2.4.5.3.1-1 «Combinaciones de Carga y Factores de Carga» (3.4.1-1 AASHTO)** — pág. impresa 143
· **Tabla 2.4.5.3.1-2 «Factores de carga para cargas permanentes, γp» (3.4.1-2 AASHTO)** — pág. impresa 143
· **Tabla 2.4.5.3.1-3 (3.4.1-3 AASHTO)** — pág. impresa 144
Además el **código ya no está vacío**: `factores_carga_aashto` tiene hoy valor y etiqueta `[C]`. El manifiesto describe un estado del repositorio que ya no existe.

### `PUE-05` — «Vacío absoluto sobre conductos enterrados» — el Manual los trata en al menos cinco lugares

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:1068-1073 · src/modulos/M8_estructural.py:35-36, :199-200, :209-210 · manifiesto §3 y §14.a
**Ubicación PDF** Manual de Puentes, págs. impresas 106, 109, 121, 143, 280, 362, 378

**Afirmación del repo.** Afirmación negativa repetida en §3, §14.a y el código: el Manual de Puentes «nunca incorporó la Sección 12 de AASHTO LRFD» y por eso hay «**vacío absoluto sobre conductos enterrados**».

**Qué dice el documento.** La conclusión estrecha —que no existe un capítulo equivalente a la Sección 12— es cierta. El «vacío absoluto» no lo es. El Manual fija, sobre alcantarillas y estructuras enterradas:
· **num. 2.4.3.3.2 «Componentes Enterrados» (3.6.2.2 AASHTO)**, pág. 109: IM = 33(1.0 − 0.125·DE) ≥ 0 %, con DE = profundidad mínima de cubierta de tierra.
· **Tabla 2.4.5.3.1-2**, pág. 143: filas propias de «Estructura rígida enterrada» y «Estructuras flexibles enterradas» (alcantarillas cajón metálicas, termoplásticas).
· **num. 2.8.1.3A.6.2**, pág. 280: cortante en losas de alcantarilla cajón con menos / más de 2.0 ft (600 mm) de relleno.
· **num. 2.9.1.4.6.4.6**, pág. 362: armadura de distribución según la altura de relleno sobre la losa.
· **Tabla 2.9.1.5.5.3-1**, pág. 378: recubrimiento para «Alcantarillas de cajón de concreto prefabricados».
· «Alcantarillas Rectangulares», pág. 106, y la exención sísmica de la pág. 121.

### `PUE-06` — La «evidencia de índice» que sostiene el vacío es falsa: 2.11 no es «Muros de Contención y Estribos»

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:1068-1073 · docs/manifiesto_citas.md §3 y §14.a punto 2
**Ubicación PDF** Manual de Puentes, índice de la Parte 2 y cuerpo en págs. impresas 505 y 513

**Afirmación del repo.** «↻ **Afirmación negativa, ahora con la evidencia de índice**: su índice **salta de 2.11 (Muros de Contención y Estribos) a 2.12 (Disposiciones Constructivas)** — no existe el equivalente de la Sec. 12».

**Qué dice el documento.** El índice real de la Parte 2 es: 2.8 **Cimentaciones** (10 AASHTO) · 2.9 Superestructuras · 2.10 Requisitos para Apoyos (14.6 AASHTO) · **2.11 «DISEÑO DE BARRERAS DE SONIDO» (15 AASHTO)**, pág. 505 · 2.12 «Disposiciones Constructivas», pág. 513.
2.11 *no* es «Muros de Contención y Estribos»; los muros y estribos viven dentro de **2.8 Cimentaciones** — que es justamente de donde el propio repositorio saca 2.8.1.1.14.2 y 2.8.1.3.1.2c. Y la numeración del Manual no sigue la de AASHTO (2.8↔10, 2.10↔14.6, 2.11↔15), de modo que «entre 2.11 y 2.12 debería estar la Sec. 12» no se sostiene como inferencia.

### `HID-01` — El 9.8 de Laushey no está en el numeral que lo respalda — y el Manual sí escribe 9.8 donde el código usa 9.81

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:51-57 · src/constantes_fisicas.py:19-31 · manifiesto §1
**Ubicación PDF** Manual de Hidrología, num. 4.1.1.3.7 c) pág. impresa 80 (PDF 83) · num. 3.12.5 pág. impresa 63 (PDF 66)

**Afirmación del repo.** `G_LAUSHEY = 9.8` en el archivo que admite «solo constantes `[N]` con numeral verificado», con el comentario «**g tal como lo escribe la Sec. 4.1.1.3.7 c) junto a su fórmula de d50**». Toda la separación entre `G_LAUSHEY = 9.8` y `constantes_fisicas.G = 9.81` se justifica con esa frase.

**Qué dice el documento.** El num. 4.1.1.3.7 c) da la fórmula (49) d₅₀ = V²/(3.1 g) y define únicamente:

> g : Aceleración de la gravedad (m/s²)

No escribe ningún decimal. El «9.8» lo escribe la *hoja de ruta* (línea 495), no el Manual.
El Manual sí escribe «g = 9.8 m/s²» en otros dos sitios: **num. 3.12.5** (pág. 63), para la velocidad crítica Vc = √(yc·g), y en la velocidad de corte de socavación (HEC-18). Es decir, escribe 9.8 exactamente para el tirante crítico, que es donde M4 usa 9.81.

### `VAC-01` — El vacío de altura mínima de relleno no está cerrado: AASHTO Sec. 12 la tabula, y 0.30 m queda por debajo

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** docs/manifiesto_citas.md §14.a · src/criterios_adoptados.py:1074-1108
**Ubicación PDF** AASHTO LRFD 9.ª ed., Art. 12.6.6.3 y Tabla 12.6.6.3-1, pág. 12-22 (PDF 1660)

**Afirmación del repo.** §14.a declara **vacío verificado**: «se fue a buscar a todas las fuentes donde podía estar y **no está en ninguna**», tras agotar tres fuentes (normas de producto, Manual de Puentes, EG-2013). Sobre eso se adopta 0.30 m por analogía `[N→]` para concreto y TMC, y se anota que el típico de concreto «es 1.0 ft (~0.305 m)» y que la verificación «debería *confirmarla*, no corregirla».

**Qué dice el documento.** **Art. 12.6.6.3 «Minimum Cover», Tabla 12.6.6.3-1** tabula la cobertura mínima por tipo de conducto:
· **Reinforced Concrete Pipe**, bajo zona no pavimentada o pavimento flexible — Bc/8 (o √Bc/8, el mayor) ≥ **12.0 in**; bajo pavimento rígido — 9.0 in
· **Corrugated Metal Pipe** — S/8 ≥ **12.0 in**
· **Thermoplastic Pipe** — ID/8 ≥ 12.0 in sin pavimentar; **ID/2 ≥ 24.0 in bajo pavimento**
Consecuencias: (1) el vacío es del corpus *peruano*, no del cuerpo normativo que el proyecto declara como Vía 1, y el documento está en el propio repositorio; (2) 0.30 m queda **5 mm por debajo** del piso de 12 in; (3) el valor que gobierna no es el piso sino Bc/8, que para un tubo de concreto de 2.40 m (Bc ≈ 2.9 m) da ≈ 0.36 m, un 20 % más que lo adoptado.

### `SUE-01` — El Cuadro 4.1 sí dice cuándo son 4 calicatas y cuándo 6 — y la cita «4 (o 6)» no existe

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** Manual de Suelos
**Ubicación repo** src/constantes_normativas.py:165-172
**Ubicación PDF** Manual de Suelos, num. 4.2, Cuadro 4.1, pág. impresa 28 (PDF 29)

**Afirmación del repo.** «El Cuadro admite además 6 en vez de 4 para autopistas con 4 carriles por sentido, y **“4 (o 6)”** para duales. Ese 6 NO se transcribe aquí: el Cuadro **lo da como alternativa sin decir cuándo aplica cada una**, de modo que la elección entre 4 y 6 no es `[N]`.»

**Qué dice el documento.** El Cuadro 4.1 fija la condición de forma explícita, con la misma redacción para autopistas y para duales/multicarril:

> Calzada 2 carriles por sentido: 4 calicatas × km × sentido · Calzada 3 carriles por sentido: 4 calicatas × km × sentido · Calzada 4 carriles por sentido: 6 calicatas × km × sentido

No es una alternativa abierta: es función determinada del número de carriles por sentido, de modo que el 6 es `[N]` y omitirlo exige declarar que esta vía tiene ≤ 3 carriles por sentido — cosa que el propio comentario dice que no está cerrada. Además la cadena entrecomillada «`4 (o 6)`» no aparece en el Cuadro (0 coincidencias en el documento).

### `PRO-01` — El tope de 2.10 m para TMC no está en la norma que lo respalda: A760 tabula hasta 3600 mm

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** ASTM A760 / AASHTO M36
**Ubicación repo** src/constantes_normativas.py:132-136 · src/criterios_adoptados.py, `diametros_normalizados`
**Ubicación PDF** ASTM A760/A760M-10, Tabla 1, pág. 2 del PDF (OCR 300 dpi)

**Afirmación del repo.** `D_MAX["tmc"] = 2.10` m, atribuido a «AASHTO M36 / ASTM A760», bajo el rótulo «topes por norma de producto - **VERIFICAR**». Superado el tope, M2 devuelve «material descartado por diámetro requerido».

**Qué dice el documento.** La **Tabla 1 «Tamaños de tubería»** de A760/A760M-10 (la norma que se declara equivalente a AASHTO M 36/M 36M) tabula diámetros nominales de **150 mm hasta 3600 mm**: 150, 200, 250, 300, 375, 450, 525, 600, 675, 750, 825, 900, 1050, 1200, 1350, 1500, 1650, 1800, 1950, **2100**, 2250, 2400, 2550, 2700, 2850, 3000, 3150, 3300, 3450, 3600. Los 2100 mm son un tamaño más de la serie, no un máximo. La norma citada no sostiene el tope, y el tope descarta el TMC en todo diseño que pida más de 2.10 m.

### `PRO-02` — El tope de 2.70 m para concreto reforzado tampoco es el de M 170M

**Sev** CRÍTICA · **Veredicto** CONTRADICE · **Documento** AASHTO M 170M
**Ubicación repo** src/constantes_normativas.py:132-136
**Ubicación PDF** AASHTO M 170M-04, Tablas 1-5 (PDF págs. 3, 4, 6, 8, 10) y §7.2

**Afirmación del repo.** `D_MAX["concreto_reforzado"] = 2.70` m, atribuido a «ASTM C76 / AASHTO M170».

**Qué dice el documento.** Las Tablas 1 a 5 de M 170M-04 (Clases I a V) tabulan diámetros internos designados de **300 mm a 3600 mm**. La Tabla 1 (Clase I) llega a 3450 mm y las Tablas 3 y 4 listan filas hasta 3600 mm. Por encima de ~2700 mm varias clases traen guiones —diseño especial, §7.2— pero el diámetro sigue tabulado y la norma prevé expresamente «special designs for sizes and loads beyond those shown in Tables 1 to 5». 2.70 m puede defenderse como «el mayor con armadura tabulada en todas las clases», pero eso no es lo que el código dice, y el código lleva la marca `VERIFICAR` sin numeral.

### 11.2 Altas

### `PRO-03` — La exclusión de alturas de relleno no está en la «Nota 1» de las tres normas, y la fórmula citada es de una sola

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** M 170M · M 36 · A760
**Ubicación repo** src/criterios_adoptados.py:1113-1121 · docs/manifiesto_citas.md §9 y §14.a punto 1
**Ubicación PDF** M 170M-04 Nota 1 (PDF pág. 1) · M 36-03(2007) §1.3 (PDF pág. 2) · A760/A760M-10 §1.4 (PDF pág. 1)

**Afirmación del repo.** «AASHTO M 170M, M 36 y ASTM A760 no contienen alturas de relleno admisibles. Su **Nota 1** las excluye de forma expresa: son especificaciones de **fabricación y compra**...». Atribución declarada: «**Nota 1 de cada norma**».

**Qué dice el documento.** El **fondo es correcto** para las tres: ninguna da alturas de relleno. La **atribución es falsa en dos de tres**.
· **M 170M** — sí es la Nota 1: «This specification is a *manufacturing and purchase specification only*, and does not include requirements for bedding, backfill, or the relationship between field load condition and the strength classification of pipe.» ✔
· **M 36** — la exclusión está en **§1.3**: «This specification does not include requirements for bedding, backfill, or the relationship between earth cover load and sheet thickness of the pipe.» Su Nota 1 habla de láminas con fibra de aramida y post-recubrimiento asfáltico. No usa la fórmula «manufacturing and purchase specification only».
· **A760** — la exclusión está en **§1.4**, con el mismo texto. Su Nota 1 es también la de la fibra de aramida.

### `AAS-01` — Los 75 mm de recubrimiento AASHTO dependen de una categoría de acero que no se declara

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py, criterio `recubrimiento_aashto_mm` · src/modulos/M9_cabezal.py:1170-1215
**Ubicación PDF** AASHTO LRFD 9.ª ed., Tabla 5.10.1-1, pág. 5-169 (PDF 528). La página que cita el criterio es correcta.

**Afirmación del repo.** `recubrimiento_aashto_mm = {contra_suelo: 75.0, suelo_intemperie_ge_3_4: 75.0, suelo_intemperie_le_5_8: 75.0}`, etiqueta `[C]`, con la conclusión de que «AASHTO gobierna en los tres casos por la regla del mayor» frente a los 70/50/40 mm de E.060. Justificación: la categoría «ambiente costero» = 75 mm, «**uniforme sin importar el diámetro de barra**».

**Qué dice el documento.** La **Tabla 5.10.1-1 «Minimum Cover for Main Reinforcing Steel (in.)»** tiene tres columnas por **Reinforcing Material Category**, no una:
· Coastal — **A 3.0 in · B 2.0 in · C 2.0 in**
· Cast against earth — A 3.0 · B 2.0 · C 2.0
· Direct exposure to salt water — A 4.0 · B 2.5 · C 2.5
Al pie: «Category A — Uncoated reinforcing steel meeting AASHTO M 31M/M 31 · Category B — Epoxy coated or galvanized meeting ASTM A775/A775M · Category C — Materials meeting AASHTO M 334M/M 334».
Los 75 mm son la Categoría **A** (y 3.0 in son 76.2 mm, redondeados a la baja sin declararlo). Con acero galvanizado o epóxico —opción natural en un corredor salino con freático somero— AASHTO daría 2.0 in = 50.8 mm y la regla del mayor la ganaría **E.060**, invirtiendo la conclusión. La categoría no se declara en ninguna parte.

### `PUE-07` — «La tabla del factor de muro» no es una tabla: el numeral solo autoriza la reducción a 0.5

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/constantes_normativas.py:241-250 · docs/manifiesto_datos_proyecto_vs_constantes.md
**Ubicación PDF** Manual de Puentes, num. 2.8.1.1.14.2.2, pág. impresa 255 (PDF 256)

**Afirmación del repo.** `FACTOR_MURO_TABLA = {rigido: 1.0, desplazable: 0.5}` en `constantes_normativas.py`, con el argumento de que «**las DOS filas son [N]: el numeral las fija**» y que solo la elección entre ellas es `[A]`. Todo el reparto tabla/elección del manifiesto de datos-vs-constantes (fila 3) descansa en esa lectura.

**Qué dice el documento.** El num. 2.8.1.1.14.2.2 no presenta ninguna tabla. Dice:

> Donde el muro es capaz de desplazamientos de 1.0 a 2.0 in o más durante el evento sísmico de diseño, kₕ puede ser reducido a 0.5 kₕ₀ sin llevar a cabo un análisis de la deformación mediante el método Newmark…

Hay **un solo valor normativo, 0.5**, condicionado a capacidad de desplazamiento. El 1.0 es la ausencia de reducción (kₕ = kₕ₀), no una fila tabulada. El rango del código, «muros que admiten 25-50 mm», es la conversión de 1.0-2.0 in hecha dentro del archivo de constantes, no una cifra del Manual.

### `PUE-08` — k_v = 0.0 se declara adopción del proyectista, y el Manual lo fija en el numeral que el proyecto ya cita

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:489-495 · manifiesto §11.b y §12
**Ubicación PDF** Manual de Puentes, num. 2.8.1.1.14.2.1, pág. impresa 254 (PDF 255)

**Afirmación del repo.** `k_v = 0.0`, etiqueta `[A]`, fuente «**Práctica corriente; no fijado por el Manual de Puentes**», con sensibilidad (0.0, 0.5).

**Qué dice el documento.** En el mismo numeral del que el proyecto toma kₕ₀ = Aₛ:

> El coeficiente de aceleración sísmica vertical, kᵥ, **se asumirá cero** con el propósito de calcular las presiones laterales del terreno, a no ser que el muro esté significativamente afectado por efectos de alguna falla cercana, o si son relativamente altas las aceleraciones verticales que probablemente estén actuando simultáneamente con la aceleración horizontal.

La afirmación negativa es falsa. El error va del lado seguro —se declara como elección algo que la norma respalda— pero debilita la memoria: presenta como discrecional un valor defendible como `[N]`, y el rango de sensibilidad (0.0, 0.5) sugiere una libertad que el numeral acota.

### `PUE-09` — La Tabla de factores de sitio sí tipifica la Clase F: le pone asterisco y exige estudio de respuesta dinámica

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:400-403 · manifiesto §3
**Ubicación PDF** Manual de Puentes, Tabla 2.4.3.11.2.1.2-1 y Nota 2, pág. impresa 123 (PDF 124)

**Afirmación del repo.** «**Afirmación negativa**: el Manual de Puentes NO tipifica excepciones para Clase F en su Tabla 2.4.3.11.2.1.2-1», etiqueta `[C]` — vacío cubierto con fuente técnica.

**Qué dice el documento.** La Tabla 2.4.3.11.2.1.2-1 tiene **fila F con asterisco en las cinco columnas de PGA** y una Nota 2 al pie:

> Llevar a cabo investigaciones geotécnicas específicas del sitio y análisis de respuesta dinámica de sitio, para todos los sitios en sitio clase F

Eso *es* tipificar: la tabla se pronuncia sobre la Clase F y su pronunciamiento es «aquí no hay factor tabulado, hay que hacer el estudio». No es un vacío que una fuente técnica deba cubrir; es una exigencia expresa de la que el proyecto se aparta, y la etiqueta `[C]` lo presenta como lo contrario.

### `AAS-02` — La premisa de toda la Sec. 0.5 — «el sitio es Clase F por licuefacción» — no la sostiene ninguna de las dos tablas

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD · Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:386-435 · manifiesto §8 · memoria, Tablero 1 ítem 1.1
**Ubicación PDF** AASHTO LRFD 9.ª ed., Tabla 3.10.3.1-1 pág. 3-102 y Art. 10.5.4.2 pág. 10-34 · Manual de Puentes, Tabla 2.4.3.11.2.1.1-1 pág. impresa 122

**Afirmación del repo.** `clase_sitio = "F_con_factores_tabulados_por_adopcion"`: el sitio se clasifica Clase F por susceptibilidad a licuefacción, y de ahí que usar factores tabulados sea «adopción declarada del proyectista **sin respaldo normativo**», contra una exigencia incondicional de AASHTO.

**Qué dice el documento.** Las tres categorías de Clase F son idénticas en los dos documentos y **ninguna es «suelos licuables»**:

> Soils requiring site-specific evaluations, such as: Peats or highly organic clays (H > 10.0 ft) · Very high plasticity clays (H > 25.0 ft with PI > 75) · Very thick soft/medium stiff clays (H > 120 ft)

La 9.ª edición trata la licuefacción en el **Art. 10.5.4.2 «Liquefaction Design Requirements»** (Sección 10, Cimentaciones) — no por vía de la clase de sitio. Un depósito de arena saturada clasificaría por V̄ₛ/N̄/S̄ᵤ, probablemente D o E, y la licuefacción se evaluaría aparte: exactamente lo que el proyecto ya hace con su SPT de 15 m.
*Efecto de segundo orden*: si el sitio no es Clase F, la «adopción sin respaldo normativo» que la memoria confiesa puede no ser necesaria.

### `EG-01` — La cita más load-bearing del proyecto está en la pág. 984, no en la 982 — y llega impresa a la memoria

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** EG-2013
**Ubicación repo** src/constantes_normativas.py:177 y :230 · src/criterios_adoptados.py:1081, :1138 · docs/manifiesto_citas.md:254 y §14.a
**Ubicación PDF** EG-2013 Capítulo V, 508.07 → pág. impresa 984 (PDF 992)

**Afirmación del repo.** «Subsección **508.07, pág. 982**», repetido en al menos seis lugares: el comentario de `H_RELLENO_MIN["hdpe"]`, el criterio `h_relleno_min_concreto_tmc`, el numeral de `CAMA_RELLENO_LATERAL["hdpe"]` («508.05/.07, págs. 981-982»), §6 y §14.a del manifiesto, y el texto que M11 imprime.

**Qué dice el documento.** La **Subsección 508.07 «Colocación del relleno alrededor de la estructura»** está en la **pág. impresa 984**. La pág. impresa 982 corresponde a 508.02 (calidad de los tubos, inspección, material para cama). 508.05 está en la 983 y 508.08 en la 985.
El texto sí coincide **palabra por palabra**:

> La altura de relleno mínimo desde la clave de la tubería hasta el nivel de la subrasante será de 0,30 m.

Verificado en la memoria generada: la línea impresa dice «EG-2013 Subsección 508.07, pág. 982», con la página equivocada, en las dos plantillas.

### `EG-02` — La cita literal del 508.07 no vive donde el manifiesto dice que vive

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** EG-2013
**Ubicación repo** docs/manifiesto_citas.md:254 y :614
**Ubicación PDF** —

**Afirmación del repo.** §6 y §14.a atribuyen la cita textual del 0,30 m y el `H_RELLENO_MIN["hdpe"]` «`[N]` puro» a **`src/constantes_normativas.py:160`**.

**Qué dice el documento.** *Defecto interno de trazabilidad.* La línea 160 de `constantes_normativas.py` es «`# sobre cuantos sentidos se cuenta el kilometro.`», comentario final del bloque `CALICATAS_POR_SENTIDO` — Manual de Suelos, Cuadro 4.1. Otro documento, otro tema.
La cita textual está en `src/criterios_adoptados.py:1138-1140`; la constante, en `constantes_normativas.py:177`. Un revisor que siga el enlace del manifiesto aterriza en calicatas.

### `EG-03` — Las páginas de las cuatro fichas de cama y relleno lateral están corridas o son cortas

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** EG-2013
**Ubicación repo** src/constantes_normativas.py:204-232
**Ubicación PDF** EG-2013 Capítulo V, Secciones 505 a 508, págs. impresas 949-985

**Afirmación del repo.** `CAMA_RELLENO_LATERAL`: concreto simple «505.03/.07/.10/.11, **págs. 950-951**» · concreto reforzado «506.03/.07/.10/.11, **págs. 959-960**» · TMC «507.06/.07/.08, **pág. 970**» · HDPE «508.05/.07, **págs. 981-982**». Las mismas páginas viajan a la memoria y a los planos (Sec. 11, entregable 7).

**Qué dice el documento.** Páginas impresas reales: **505**.03 → 950 · .07 → 951 · **.10 → 952 · .11 → 953** (el rango declarado deja fuera justo las dos subsecciones de sujeción y relleno) · **506**.03 → 959 · .07 → 960 · **.10 y .11 → 961** · **507**.06 → **973** · .07 → 973-974 · .08 → **974** (la pág. 970 declarada cae dentro de 507.02, Materiales) · **508**.05 → **983** · .07 → **984**.
El *contenido* de las cuatro fichas confirma: Clase F con f'c 14 MPa (Tabla 503-07, pág. 912), ≥ 15 cm, 1/4 y 1/6 del diámetro exterior, arena suelta de 12 mm, capas de 15-20 cm, capas alternadas y simétricas de 0,15 m, «los 0,30 m superiores… a una densidad mínima del 100 % de la M.D.S.» y «No será aceptable la compactación del relleno por medio de anegación».

### `HDS-01` — La Tabla C.2 no está en la página C.2 — y la cita se declara «cerrada»

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** HDS-5
**Ubicación repo** src/criterios_adoptados.py, criterio `ke_entrada` · manifiesto §7
**Ubicación PDF** HDS-5 3.ª ed., Tabla C.2, pág. C.6 (PDF 216); pág. C.2 = PDF 212

**Afirmación del repo.** `ke_entrada = 0.5` (square edge with headwall), fuente «HDS-5 3.ª ed., Apéndice C, **Tabla C.2, pág. C.2** … **CITA CERRADA por verificación externa contra el documento**».

**Qué dice el documento.** La **Tabla C.2 «Entrance Loss Coefficients»** está en la **pág. C.6**. La pág. C.2 es la continuación del índice de cartas («Chart / Concrete Box Culverts (Continued)»).
El **valor confirma**: «Pipe, Concrete — Headwall or headwall and wingwalls — Square-edge → 0.5». El error es de página y es del tipo que revela que la página no se abrió: se copió el número de la tabla como número de página.

### `HDS-02` — HW/D 1.0–1.5 es una encuesta de práctica de agencias estadounidenses, no un criterio del HDS-5, y está en otra página

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** HDS-5
**Ubicación repo** src/criterios_adoptados.py, criterio `HW_D_max` · manifiesto §7
**Ubicación PDF** HDS-5 3.ª ed., Sec. 2.2.5 d), pág. 2.10 (PDF 72)

**Afirmación del repo.** `HW_D_max = 1.5`, etiqueta `[C]` («vacío normativo cubierto con fuente técnica reconocida»), fuente «HDS-5 3.ª ed., **Sec. 2.2.5, pág. 2.14** — rango de HW/D de 1.0 a 1.5 para el diseño corriente. **CITA CERRADA**». El manifiesto añade que la sensibilidad (1.2, 1.5) «es un subrango del 1.0-1.5 de la fuente».

**Qué dice el documento.** La Sec. 2.2.5 «Allowable Headwater» empieza en la **pág. 2.9**; la frase está en su apartado **d) «Agency Constraints», pág. 2.10**. La pág. 2.14 trata de espolones de escombros y seguridad vial.
Y el texto no prescribe:

> Some state or local highway agencies place limits on the headwater… **The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5.**

Es una descripción de lo que *imponen las agencias estatales*, no un valor que el HDS-5 fije. En el Perú la agencia es el MTC, cuyo Manual no fija HW/D: lo que se hizo fue adoptar una banda de práctica ajena como si fuera recomendación de la fuente. Además 1.5 es el **extremo superior** —el menos restrictivo— y la «sensibilidad» (1.2, 1.5) es la mitad alta de la banda.

### `HID-02` — La longitud máxima de cuneta está en la pág. 179, y las dos cifras no tienen la misma fuerza normativa

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:91 · src/modulos/M10_espaciamiento.py:62 · src/criterios_adoptados.py:932
**Ubicación PDF** Manual de Hidrología, num. 4.1.2.1 d), pág. impresa 179 (PDF 182)

**Afirmación del repo.** `LONG_MAX_CUNETA = {seca: 250.0, muy_lluviosa: 200.0}` y `NUMERAL_FASE_10 = "Fase 10 (num. 4.1.2.1 d), pag. 178)"`, que es lo que M10 lleva a la memoria. El criterio `long_max_cuneta = 200.0` repite la página.

**Qué dice el documento.** El num. 4.1.2.1 d) «Desagüe de las cunetas» está en la **pág. impresa 179**. La 178 es la Tabla N° 34 de dimensiones mínimas de cuneta.
Los valores confirman, pero con **modalidad distinta**:

> En región seca o poca lluviosa la longitud de las cunetas **será** de 250 m como máximo, las longitudes de recorridos mayores deberán justificarse técnicamente; en región muy lluviosa **se recomienda** reducir esta longitud máxima a 200 m.

250 m es exigencia; 200 m es recomendación. El código los declara los dos `[N]` del mismo rango. El proyecto adopta el *recomendado* como límite duro —conservador, pero la asimetría no se declara, igual que ocurre entre V1 y V2.

### `SUE-02` — El espaciamiento de 4 km a nivel de perfil no está en el Cuadro 4.1 y es condicional

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Suelos
**Ubicación repo** src/constantes_normativas.py:173
**Ubicación PDF** Manual de Suelos, num. 4.2, pág. impresa 29 (PDF 30)

**Afirmación del repo.** `ESPACIAMIENTO_PERFIL_KM = 4.0` «nivel perfil (**num. 4.2, Cuadro 4.1**)», declarado como constante `[N]` sin condición.

**Qué dice el documento.** El 4.0 km no está en el Cuadro 4.1 sino en el texto corrido del num. 4.2, y viene condicionado:

> En caso de estudios a nivel de perfil **se utilizará información secundaria existente** en el tramo del proyecto; **de no existir información secundaria** se efectuará el número de calicatas del cuadro 4.1 espaciadas cada 4.0 km en vez de cada km.

La regla primaria a nivel de perfil es usar información secundaria; los 4 km son el caso subsidiario. El mismo párrafo fija 2.0 km para factibilidad y prefactibilidad, y reglas para tramos de 500-1000 m y < 500 m, que tampoco se recogen.

### `SUE-03` — Uno de los cuatro numerales que respaldan la compactación no contiene ninguno de los dos valores

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Suelos
**Ubicación repo** src/constantes_normativas.py:147-150 · manifiesto §2 (marca ⟳)
**Ubicación PDF** Manual de Suelos, num. 3.2.1 / 3.2.2 / 3.3, pág. impresa 24 (PDF 25) · num. 9.1(1), pág. impresa 89 (PDF 90)

**Afirmación del repo.** `COMPACTACION_CORONA = 0.95` y `COMPACTACION_CUERPO = 0.90`, ambos citados a «num. **3.2.1, 3.2.2, 3.3 y 9.1(1)**». El manifiesto marca esos numerales como el cierre de una fila que antes estaba «⚠ sin numeral».

**Qué dice el documento.** · **3.2.1 Terraplén** (pág. 24) sostiene los dos: «La base y cuerpo del terraplén… en capas de hasta 0.30 m y compactadas al **90 %**… La **corona**… espesor mínimo de 0.30 m… en capas de 0.15 m, compactadas al **95 %**.» ✔
· **3.3** (pág. 24) apoya la corona: «los últimos 0.30 m… compactados al 95 %». ✔
· **3.2.2 Corte** (pág. 24) da 95 % para el fondo de excavación y 0.15 m de escarificado — relacionado, no es corona ni cuerpo.
· **9.1(1)** (pág. 89) **no contiene ni 0.95 ni 0.90**: trata de CBR ≥ 6 % y alternativas de estabilización. Es el numeral que sostiene `CBR_MIN_SUBRASANTE`, no la compactación.

### `E060-01` — E.060 permite exceptuar la cuantía mínima en muros de contención, y el código argumenta lo contrario

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** E.060
**Ubicación repo** src/constantes_normativas.py:302-317 · src/modulos/M9_cabezal.py:1281 · manifiesto §5
**Ubicación PDF** E.060, Art. 14.3.1 pág. 133 · Art. 14.8.2 pág. 134

**Afirmación del repo.** `constantes_normativas.py:302-317` defiende en extenso que `CUANTIA_MIN_MURO` es un **piso obligatorio**: «el Art. 14.3.1 fija un PISO **por debajo del cual ningún muro se arma**, y un piso se aplica — ρ_diseño = max(ρ_calculado, ρ_mínimo)».

**Qué dice el documento.** Los **valores confirman**: Art. 14.3.1 (pág. 133) da horizontal 0,002 y vertical 0,0015, sin inversión. Pero el capítulo tiene un artículo específico para muros de contención, que es lo que el cabezal es:

> **14.8.2** El refuerzo mínimo será el indicado en 14.3. **Este requisito podrá exceptuarse** cuando el Ingeniero Proyectista disponga juntas de contracción y señale procedimientos constructivos que controlen los efectos de contracción y temperatura.

«Por debajo del cual ningún muro se arma» no es lo que dice la norma para muros de contención. La excepción existe y el código la niega expresamente.

### `E060-02` — El acero en dos caras se decide con el umbral de temperatura e ignora el umbral general de 200 mm

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** E.060
**Ubicación repo** src/modulos/M9_cabezal.py:1353-1377 · src/constantes_normativas.py:319-320
**Ubicación PDF** E.060, Art. 14.8.3 pág. 134 · Art. 14.3.2 pág. 133 · Art. 14.8.2 pág. 134

**Afirmación del repo.** `requiere_temperatura_dos_caras` devuelve `False` y la memoria imprime «Acero por temperatura en UNA cara» para todo espesor < 0.250 m, apoyándose en `ESPESOR_TEMPERATURA_DOS_CARAS = 0.250` (Art. 14.8.3).

**Qué dice el documento.** El Art. 14.8.3 **confirma exactamente**: «El acero por temperatura y contracción deberá colocarse en ambas caras para muros de espesor mayor o igual a **250 mm**» — y 14.8 es, en efecto, «Muros de Contención». La transcripción es impecable.
Pero no es el único umbral. El **Art. 14.3.2** exige: «Los muros con un espesor **mayor que 200 mm**, excepto los muros de sótanos, deben tener el refuerzo **en cada dirección colocado en dos capas**», y el 14.8.2 remite expresamente a 14.3. Entre 200 y 250 mm el muro lleva refuerzo en dos capas por 14.3.2 aunque el acero por temperatura no lo exija, y la memoria imprime lo contrario.

### `E060-03` — Al Art. 11.10.10.2 se le atribuye un umbral que no define

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** E.060
**Ubicación repo** src/criterios_adoptados.py, criterio `cortante_alto_muro_e060_art_11_10_10_2`
**Ubicación PDF** E.060, Arts. 11.10.10.1 y 11.10.10.2, pág. 104

**Afirmación del repo.** El criterio dice que «el Art. 11.10.10.2 lo sube a 0.0025 cuando la demanda de cortante supera **el umbral que ese artículo define (del orden de Vu > 0.5·φ·Vc)**».

**Qué dice el documento.** El artículo entero es:

> 11.10.10.2 La cuantía de refuerzo horizontal para cortante no debe ser menor que 0,0025 y su espaciamiento no debe exceder tres veces el espesor del muro ni de 400 mm.

No define umbral alguno. La condición de entrada la fija el 11.10.10.1 («Donde Vᵤ exceda la resistencia al corte Vc…»), y el «0.5·φ·Vc» pertenece a otro artículo, sobre vigas. El **0,0025 y la condición cualitativa de cortante alto confirman**; el umbral concreto es una atribución inventada.

### `MAN-01` — Cuatro criterios que el manifiesto inventaría como vacíos tienen hoy valor

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manifiesto ↔ código
**Ubicación repo** docs/manifiesto_citas.md:179-180, 295, 298-300, 486-487, 491, 493
**Ubicación PDF** —

**Afirmación del repo.** §3, §8 y §12 declaran `factores_carga_aashto`, `recubrimiento_aashto_mm`, `peso_especifico_concreto_kn_m3` y `procedimiento_flexion_corte_aashto_sec5` como `None`, etiqueta `[A]`, «vacío que bloquea…». §12 los cuenta entre los 26 sin valor.

**Qué dice el documento.** *Defecto interno.* Los cuatro tienen valor y etiqueta `[C]` en este SHA: `factores_carga_aashto` = diccionario completo de γ por combinación · `recubrimiento_aashto_mm` = 75 mm en las tres condiciones · `peso_especifico_concreto_kn_m3` = 23.56 · `procedimiento_flexion_corte_aashto_sec5` = φ, modelo de corte y β-θ.
El manifiesto es el índice por el que un revisor entra a la auditoría; describir como bloqueado lo que ya calcula invierte el sentido de la revisión.

### `MAN-02` — Los recuentos de §12 y §13 no son los que devuelve el archivo, y se contradicen entre sí

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manifiesto ↔ código
**Ubicación repo** docs/manifiesto_citas.md:457, 495-498, 519-531
**Ubicación PDF** —

**Afirmación del repo.** §13: «46 criterios: 0 `[N]` · **1 [N→]** · 1 `[S]` · **14 [C]** · 30 `[A]`», con la nota «los números de arriba son ahora los que devuelve el propio archivo». §12: «**Los 33 criterios [A]**… de los 33, **26 están sin valor**… solo **7** tienen valor declarado».

**Qué dice el documento.** *Defecto interno.* Contado sobre el módulo: **46 criterios · 0 [N] · 2 [N→] · 1 [S] · 13 [C] · 30 [A]**; **23 sin valor** en total y, entre los `[A]`, **22 sin valor y 8 con valor**.
Los dos `[N→]` son `resguardo_HW_subrasante` y `h_relleno_min_concreto_tmc` —§14.a del propio manifiesto declara el segundo—. El octavo `[A]` con valor es `clase_sitio`, que §8 del propio manifiesto reetiquetó. La tabla de §12 tiene 33 filas porque cuatro ya no son `[A]`.

### `MAN-03` — Un criterio retirado y una advertencia inexistente siguen inventariados

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manifiesto ↔ código
**Ubicación repo** docs/manifiesto_citas.md:296 y :302
**Ubicación PDF** —

**Afirmación del repo.** §8 inventaría «`FS_flotacion = None` — FS de V7, ΣW ≥ FS·U», y una «**Advertencia transversal: declarar la EDICIÓN de AASHTO LRFD**» atribuida a `[CA:992-995]`.

**Qué dice el documento.** *Defecto interno.* `FS_flotacion` **ya no existe**: el código lo declara retirado. Y `criterios_adoptados.py:992-995` pertenece al criterio `TR_evento_extremo` (V8) y habla de otra cosa: el texto de la «advertencia transversal» no está en el archivo citado ni en ningún otro.

### `MAN-04` — Al menos 66 de 296 referencias archivo:línea no llevan a lo que dicen llevar, y todas caen en el hueco del test

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manifiesto ↔ código
**Ubicación repo** docs/manifiesto_citas.md (296 referencias) · tests/test_manifiesto_citas.py:52-67
**Ubicación PDF** —

**Afirmación del repo.** `tests/test_manifiesto_citas.py` vigila las referencias del manifiesto y pasa en verde. Su excepción declarada: las «referencias de prosa» (filas sin identificador entre backticks) solo se comprueban contra «que la línea no esté vacía».

**Qué dice el documento.** *Defecto interno.* Las 213 referencias verificadas por símbolo caen todas dentro de su bloque. Las **83 de prosa concentran el 100 % de los defectos**: al menos 66 apuntan a otra cosa. Focos:
· §4 (E.050) tiene un **desplazamiento sistemático de una función**: cada fila E1…E5 cita la función anterior a la que nombra.
· `M9_cabezal.py` — 14 referencias rotas, dos aterrizando en líneas de `import`.
· `criterios_adoptados.py` — 15 referencias caen en un criterio distinto del que la fila afirma (el índice «2.11 → 2.12» del Manual de Puentes se atribuye a `diametros_normalizados`).
· `[CN:35]` para `GAMMA_AGUA_KN_M3` (símbolo que ya no vive ahí), `[CN:47]` y `[CN:55]` para las dos afirmaciones negativas de las Tablas 9 y 10 (reales en 74 y 88), `[CN:86]` para el `VERIFICAR` de `D_MAX` (real en 132), `[CN:74]` para el comentario de `Ks` (real en 107), `[CN:41]` para la fórmula de TR (real en 68), `[CN:110]` para `h_o` (real en 127).

### `VOC-01` — cota_TW es una cota absoluta y TW es un tirante: dos magnitudes distintas con casi el mismo nombre

**Sev** ALTA · **Veredicto** NO VERIFICABLE · **Documento** Trampa de vocabulario
**Ubicación repo** src/modelos.py (PuntoCritico) · cli.py · src/modulos/M4_control.py · M5_verificaciones.py
**Ubicación PDF** —

**Afirmación del repo.** El CSV trae la columna `cota_TW` («Cota de TW», msnm) y el pipeline maneja además `TW`, definido como el tirante en el receptor **sobre el fondo de la salida**, en m. La opción de línea de comandos es `--tw`.

**Qué dice el documento.** *Ambigüedad de nomenclatura, no de norma.* Una cota en msnm y un tirante sobre el fondo se diferencian por la cota de fondo de la salida; confundirlas desplaza el control de salida en la magnitud entera de esa cota. El repositorio distingue bien los dos conceptos en las definiciones, pero los nombra casi igual y expone los dos a la vez al usuario. Como las celdas `cota_TW` vienen vacías en las cuatro filas del CSV (tablero ANA), la confusión no se puede ejercitar hoy y no se pudo comprobar sobre datos reales: queda como riesgo declarado, no como error demostrado.

### `VOC-02` — «Recubrimiento» tiene tres sentidos en este expediente, no dos, y el tercero está sin declarar

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Trampa de vocabulario
**Ubicación repo** src/criterios_adoptados.py:1129-1136 · docs/manifiesto_citas.md §14.a
**Ubicación PDF** Manual de Puentes, Tabla 2.9.1.5.5.3-1, pág. impresa 378 · EG-2013 507.10 pág. 974 y págs. 969-976 · A760 §1.1

**Afirmación del repo.** §14.a documenta **una** trampa: «recubrimiento» = altura de relleno de tierra *vs* recubrimiento de concreto sobre el acero (Manual de Puentes, Tabla 2.9.1.5.5.3-1). Añade que «son dos conceptos que comparten palabra en español y **no tienen ninguna relación**».

**Qué dice el documento.** La trampa documentada es **real y está bien anotada**: la Tabla 2.9.1.5.5.3-1 existe, está en la pág. 378 y su fila de alcantarillas da 2.0 in. Pero:
· Hay un **tercer sentido**: en el EG-2013 Sección 507 y en M 36 / A760, «recubrimiento» es el **revestimiento metálico o bituminoso de la plancha de acero** («recubrimiento en peso de zinc», «recubrimiento galvanizado», «metallic-coated»). Es el sentido que gobierna la protección del TMC en el ambiente agresivo de este proyecto (507.10), y no está declarado.
· La afirmación «no tienen ninguna relación» es imprecisa *en la propia tabla citada*: la fila de alcantarillas es «forjados con **inferior a 2 pies de relleno** que no se utilicen como superficie de conducción → 2.0 in». El recubrimiento de acero exigido depende ahí de la altura de relleno. Los dos sentidos están acoplados en el mismo renglón del que se advierte que no lo están.

### `VOC-03` — «Luz» separa alcantarilla de puente, y el catálogo trabaja con diámetros

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Trampa de vocabulario
**Ubicación repo** src/constantes_normativas.py:28 · src/modulos/M1_clasificacion.py:78 · cli.py `--luz`
**Ubicación PDF** Manual de Hidrología, num. 4.1.1.3.1 pág. 70 · 4.1.1.5.1 pág. 87 · 4.1.1.3.4 a) pág. 72

**Afirmación del repo.** `LUZ_MAX_ALCANTARILLA = 6.0` se compara contra la luz declarada del cruce (`--luz`) para decidir alcantarilla o puente, mientras M2 dimensiona por **diámetro** y el catálogo arranca en 0.90 m.

**Qué dice el documento.** Los dos numerales son complementarios y el umbral está bien leído: «alcantarilla… cuya **luz sea menor a 6.0 m**» (4.1.1.3.1) y «puente… cuya **luz sea mayor o igual a 6.0 m**» (4.1.1.5.1). Lo que ninguno de los dos define es qué es la «luz» de un conducto circular. El Manual usa «luz» también para puentes (distancia entre apoyos) y, en 4.1.1.3.4 a), habla de «sección mínima circular de 0.90 m de diámetro **o su equivalente de otra sección**» — es decir, admite secciones no circulares donde luz y diámetro no coinciden. El repositorio compara una entrada llamada «luz» contra un catálogo de diámetros sin declarar la equivalencia.

### `HID-03` — El diámetro mínimo de 0.90 m es condicional, y su excepción cubre a la Familia C de este proyecto

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:29 y :131 · src/modulos/M2_material.py:58
**Ubicación PDF** Manual de Hidrología, num. 4.1.1.3.4 a), pág. impresa 72 (PDF 75)

**Afirmación del repo.** `DIAMETRO_MIN = 0.90` y `D_INICIO = 0.90` («mínimo normativo MTC»), aplicados como piso incondicional del catálogo para todos los puntos y todas las familias.

**Qué dice el documento.** El numeral trae dos condicionantes que el código no recoge:

> **En carreteras de alto volumen de tránsito** y por necesidad de limpieza y mantenimiento de las alcantarillas, se adoptará una sección mínima circular de 0.90 m (36") de diámetro o su equivalente de otra sección, **salvo en cruces de canales de riego donde se adoptarán secciones de acuerdo a cada diseño particular**.

· La clase de vía «ni siquiera está cerrada» según el propio repositorio (depende del IMDA del estudio de demanda), así que «alto volumen de tránsito» no está establecido.
· La **Familia C de este expediente son cruces de canal** —el CSV los carga sin Q, sin área y sin S porque «el caudal lo fija el canal (ANA / Junta de Usuarios del Bajo Piura)»—, exactamente el caso que el numeral exceptúa. El piso de 0.90 m se les aplica igual.

### `HID-04` — «El rango recorre la calidad del revestimiento» no está en el Manual, y se imprime junto a la cita

**Sev** ALTA · **Veredicto** NO VERIFICABLE · **Documento** Manual de Hidrología
**Ubicación repo** src/criterios_adoptados.py, criterio `v_max_concreto_eleccion` · docs/manifiesto_citas.md §1
**Ubicación PDF** Manual de Hidrología, Tabla N° 10 y párrafo previo, pág. impresa 76 (PDF 79)

**Afirmación del repo.** La nota de §1 y el campo `fuente` de `v_max_concreto_eleccion` —que la memoria **sí imprime**— afirman: «los dos números de la fila del concreto, 3.0 y 6.0 m/s, son ambos MÁXIMOS — **el rango recorre la calidad del revestimiento**, no un piso y un techo. 6.0 m/s es el máximo del acabado de mejor calidad… 3.0 m/s es el máximo del acabado más pobre».

**Qué dice el documento.** La **lectura de fondo se sostiene**: el título es «Velocidades máximas admisibles (m/s) en conductos revestidos», la única columna se rotula «VELOCIDAD (M/S)», y el piso de autolimpieza está aparte, en el párrafo siguiente. La corrección de V3 es correcta.
Lo que **no aparece en ninguna parte del Manual** es la explicación de *por qué* hay dos números: nada dice que recorran la calidad del acabado. La fuente de la tabla es «HCANALES, Máximo Villón B.». Además, la frase que introduce la tabla apunta en dirección contraria: «se encuentre dentro de un **rango**, cuyos **límites** se describen a continuación», y la fila de mampostería trae un solo número (2.0), incompatible con un rango de acabados.
Es una interpretación del proyectista, razonable, pero se imprime en la memoria adosada a la cita y sin marcarse como interpretación.

### `HID-05` — El numeral del puente está en la pág. 86-87, no en la 88

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/modulos/M1_clasificacion.py:78
**Ubicación PDF** Manual de Hidrología, págs. impresas 70, 86 y 87 (PDF 73, 89 y 90)

**Afirmación del repo.** `NUMERAL_LUZ = "4.1.1.3.1 / 4.1.1.5.1" # Manual MTC, págs. 70 y 88`, que es lo que M1 lleva a la memoria.

**Qué dice el documento.** 4.1.1.3.1 «Aspectos generales» empieza en la **pág. impresa 70** ✔. 4.1.1.5.1 «Aspectos generales» (puentes) empieza en la **pág. 86**, y la frase que define el umbral —«se definirá como puente a la estructura cuya luz sea mayor o igual a 6.0 m, siguiendo lo establecido en las especificaciones AASHTO LRFD»— está en la **pág. 87**. La pág. 88 no contiene ninguna de las dos.

### `PUE-10` — El recubrimiento de AASHTO se declara vacío mientras el Manual que el proyecto ya cita lo da

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py, criterio `recubrimiento_aashto_mm` · docs/manifiesto_citas.md §8 y §12
**Ubicación PDF** Manual de Puentes, num. 2.9.1.5.5.3 pág. 377 y Tabla 2.9.1.5.5.3-1 pág. 378

**Afirmación del repo.** `recubrimiento_aashto_mm` figuró como vacío «que bloquea la regla del mayor (Sec. 0.2)» y hoy se cierra citando solo AASHTO. En ninguno de los dos estados se usa el Manual de Puentes.

**Qué dice el documento.** El Manual de Puentes **transcribe la tabla** como Tabla 2.9.1.5.5.3-1 (= 5.12.3-1 AASHTO), pág. 378, con «Vaciado del concreto contra el suelo → 3.0 in», «Ubicaciones costeras → 3.0 in» y «Exposición directa al agua salada → 4.0 in», más los factores de modificación por relación W/C (0.8 para W/C ≤ 0.40; 1.2 para W/C ≥ 0.50) que el criterio no recoge y que, con la relación a/c de 0.40 que el propio proyecto adopta por cloruros, **reducirían** el recubrimiento exigido un 20 %. El proyecto cita esa tabla en otro sitio —para advertir de la trampa de vocabulario— pero no la usa donde hace falta.

### `MEM-01` — El matiz «recomienda, no prohíbe» que el manifiesto declara como lo único que se imprime de V2, no se imprime

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Memoria exportada
**Ubicación repo** src/constantes_normativas.py:42-44 · docs/manifiesto_citas.md §1
**Ubicación PDF** —

**Afirmación del repo.** «ese matiz **viaja hasta la memoria** dentro de `M5.NUMERAL_V2`» (`constantes_normativas.py:42-44`) y «Es **lo único que la memoria imprime de V2**» (manifiesto §1).

**Qué dice el documento.** *Verificado sobre la memoria generada* (`cli.py --html` sobre `tests/ejemplo_puntos.csv`, alcances expediente y perfil): «recomend» aparece **0 veces** y «sedimentación» **0 veces** en ambas. El pipeline se detiene antes de V2 porque `homogeneidad_serie_fen` bloquea el Q de toda la Familia A, así que el matiz nunca llega al revisor. La afirmación es cierta sobre el código y falsa sobre el producto: hoy la memoria no lleva ese matiz.

### `COH-01` — El 19.63 es correcto y la hoja de ruta está equivocada: la discrepancia declarada se resuelve a favor del código

**Sev** ALTA · **Veredicto** CONFIRMA · **Documento** HDS-5 · hoja de ruta
**Ubicación repo** src/constantes_normativas.py:111-126 · src/modulos/M4_control.py
**Ubicación PDF** HDS-5 3.ª ed., Ec. 3.4b, pág. 3.10 (PDF 92); repetida como DG 3.1 en pág. C-? (PDF 296)

**Afirmación del repo.** `K_FRICCION_SI = 19.63`, con la afirmación de que «es el valor que el propio HDS-5 escribe como conversión SI de su constante K = 29… es una cifra de la **FUENTE PRIMARIA, transcrita**», y una «DISCREPANCIA ABIERTA» declarada porque la hoja de ruta sigue diciendo 19.62.

**Qué dice el documento.** HDS-5 3.ª ed., **Ecuación 3.4b**: Hf = KU(n²L/R¹.³³)(V²/2g), donde

> KU = **29 in English Units (19.63 in SI)**

La afirmación del código es exacta. La hoja de ruta escribe 19.62 en las líneas **436, 440, 797 y 908** — el código las cita como «432, 436, 790 y 901», tres de cuatro corridas ~7 líneas.
*Nota para la sustentación*: la constante deja de estar «⚠ sin numeral». Su numeral es **Ec. 3.4b, Sec. 3.1, pág. 3.10**, y conviene escribirlo.

### `E030-02` — El perfil S5 se declara «referencia muerta» y trae una prohibición expresa de construir

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** E.030
**Ubicación repo** src/criterios_adoptados.py:347-384 · docs/manifiesto_citas.md §10 · tests/test_criterios_adoptados.py
**Ubicación PDF** E.030 (2026), Art. 14.6, Tabla Nº 2, fila S5, pág. impresa 11

**Afirmación del repo.** `PERFIL_SUELO_PRESUNTO = "S5"`, etiqueta `[S]`: «el Art. 14.6 define el **esquema** S0-S5 y sus umbrales; qué letra le toca a este sitio es el resultado de aplicar ese esquema». El manifiesto lo califica de «**referencia muerta**: no lo invoca ningún módulo», y un test vigila que siga siéndolo.

**Qué dice el documento.** El esquema y la letra **confirman**: S5 «Suelos excepcionales», primera viñeta «Suelos potencialmente licuables». Lo que el código no recoge es la última viñeta de esa misma celda:

> Estos casos no están cubiertos en la clasificación establecida en la Tabla Nº 2 de la presente Norma Técnica. **Se prohíbe las construcciones apoyadas sobre estos perfiles, salvo que se efectúe un estudio específico para el sitio, en el cual se debe considerar los mejoramientos en el estrato del perfil.**

Una clasificación que prohíbe construir salvo estudio específico no es una referencia muerta: es la afirmación normativa más fuerte que el expediente hace sobre este sitio. La memoria imprime la letra sin la consecuencia.
*Y converge con AAS-02*: E.030 sí incluye los suelos licuables en su categoría excepcional; AASHTO y el Manual de Puentes no los incluyen en la Clase F. El proyecto traslada una clasificación a la otra sin declarar que los dos esquemas discrepan justamente en el rasgo que motiva la clasificación.

### `HDS-05` — h_o se aplica siempre, y HDS-5 acota expresamente cuándo puede usarse

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** HDS-5
**Ubicación repo** src/modulos/M4_control.py:493-494 · src/constantes_normativas.py:127 · docs/manifiesto_citas.md §7
**Ubicación PDF** HDS-5 3.ª ed., Sec. 3.3.3, pág. impresa 3.24 (PDF 106)

**Afirmación del repo.** `h_o = max(TW, (y_c + D)/2)` se calcula de forma **incondicional** en `control_salida()`, sin comprobar ni declarar límite de validez. El manifiesto marca la fila «⚠ sin numeral».

**Qué dice el documento.** La fórmula **confirma**, y además tiene numeral: Sec. 3.3.3, pág. 3.24. Pero viene con una condición de uso que el repositorio no recoge:

> Approximate hydraulic gradeline hₒ = (dc + D)/2 **can only be used if the barrel flows full for most of its length. It should not be used if the inlet is not submerged.**

El proyecto adopta además `geometria_control_salida = "seccion_llena"` como criterio `[C]`, que presupone lo mismo que aquí hay que verificar. Con un barril que no llena —el caso que el propio criterio contempla en su alternativa— la aproximación se aplica fuera de su rango declarado y nadie se entera.

### `AAS-04` — También se afirma que la fuente no declara mínimo para EH en reposo, y sí lo declara

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py:1345 (valor) y :1380-1382 (la afirmación)
**Ubicación PDF** AASHTO LRFD 9.ª ed., Tabla 3.4.1-2, pág. 3-18 · Manual de Puentes, Tabla 2.4.5.3.1-2, pág. impresa 143

**Afirmación del repo.** La justificación del criterio dice: «La Tabla 3.4.1-2 además distingue EH activo (1.50/0.90) de **EH en reposo (1.35, sin mínimo declarado por la fuente)**», y el valor codificado es `EH_en_reposo: {max: 1.35}`, sin mínimo.

**Qué dice el documento.** El bloque EH de la Tabla 3.4.1-2 da los tres pares completos:

> Active **1.50 / 0.90** · At-Rest **1.35 / 0.90** · AEP for anchored walls 1.35 / N/A

Idéntico en el Manual de Puentes: «Activa 1.50 / 0.90 · En reposo 1.35 / **0.90** · AEP para paredes ancladas 1.35 / N/A». El único que de verdad no tiene mínimo es el AEP, y es «N/A», no una omisión de la fuente. La afirmación negativa es falsa, y el mínimo que falta es el que se usa en la combinación desfavorable.

### `AAS-05` — El factor de modificación por relación a/c invertiría la conclusión de la regla del mayor

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py:1501-1526 · src/modulos/M9_cabezal.py:1187-1215
**Ubicación PDF** AASHTO LRFD 9.ª ed., Art. 5.10.1, pág. 5-167 (PDF 526) · Manual de Puentes, num. 2.9.1.5.5.3, pág. impresa 377

**Afirmación del repo.** `recubrimiento_aashto_mm` fija 75 mm por condición, «CITA CERRADA por verificación externa», y concluye que AASHTO gobierna en las tres condiciones frente a los 70/50/40 mm de E.060.

**Qué dice el documento.** El Art. 5.10.1 no deja la Tabla 5.10.1-1 en bruto:

> Cover for prestressing and reinforcing steel shall not be less than that specified in Table 5.10.1-1 **and modified for W/CM ratio**… Modification factors for W/CM ratio shall be the following: • For W/CM ≤ 0.40 → **0.8** • For 0.40 < W/CM < 0.50 → 1.0 • For W/CM ≥ 0.50 → 1.2

Este proyecto adopta `CLORUROS_EXTERNOS = {a_c_max: 0.40}`. Con W/CM = 0.40 el factor es **0.8**: 3.0 in × 0.8 = 2.4 in = **61 mm**, por debajo de los 70 mm de E.060 para «contra suelo». La regla del mayor pasaría a ganarla E.060 y la conclusión del criterio se invierte. El Manual de Puentes trae los mismos factores en su num. 2.9.1.5.5.3.

### `AAS-06` — La expresión de β se transcribe sin la condición que la habilita

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py:1586-1599
**Ubicación PDF** AASHTO LRFD 9.ª ed., Art. 5.7.3.4.2 y Ec. 5.7.3.4.2-1, pág. 5-70 (PDF 429)

**Afirmación del repo.** `procedimiento_flexion_corte_aashto_sec5` incluye `"beta": "4.8 / (1 + 750*epsilon_s)"` y `"modelo_corte": "MCFT_seccional_directo_no_iterativo"`, como si fuera la expresión única.

**Qué dice el documento.** El Art. 5.7.3.4.2 la condiciona:

> **For sections containing at least the minimum amount of transverse reinforcement** specified in Article 5.7.2.5, the value of β may be determined by Eq. 5.7.3.4.2-1: β = 4.8 / (1 + 750 εₛ). **When sections do not contain at least the minimum amount** of transverse reinforcement…

…y da otra expresión, dependiente además del parámetro de espaciamiento de fisura sₓₑ. Un muro de cabezal delgado sin estribos cae normalmente en el segundo caso. Transcrita sin la condición, la fórmula se aplicaría donde no vale.

### `PRO-04` — La norma a la que se difiere la verificación pendiente del TMC no aparece en ninguna de las dos

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** M 36 · A760
**Ubicación repo** src/criterios_adoptados.py:1156, :1191, :1207 · docs/manifiesto_citas.md §9 y §14.a
**Ubicación PDF** AASHTO M 36-03(2007) §2 y Tabla 6 · ASTM A760/A760M-10 §1.4, §1.5 y Tabla 1

**Afirmación del repo.** La verificación pendiente para TMC —«calibre por altura de relleno» y «relación **luz / corrugación**»— se atribuye a **ASTM A-807**, tanto en `clases_producto_por_relleno` como en la tabla final de §14.a.

**Qué dice el documento.** Búsqueda exhaustiva sobre el texto completo de las tres normas de producto: **«A-807» / «A 807» / «A807» aparece cero veces** en M 170M, M 36 y A760.
Las dos normas de acero remiten, para lo que aquí hace falta, a otras dos:
· **ASTM A796/A796M** — «Práctica para el **diseño estructural** de tuberías de acero corrugado», citada siete veces en A760 y en la lista de normas de M 36. Es la que lleva el calibre por altura de cobertura.
· **ASTM A798/A798M** — el procedimiento de instalación, al que remite A760 §1.4.
La relación luz/corrugación, además, **ya está en los documentos adjuntos**: la Tabla 6 de M 36 y la Tabla 1 de A760 marcan con «X» qué tamaños de corrugación son estándar para cada diámetro nominal. Parte del pendiente se puede cerrar hoy; la otra parte está en A796, no en A-807.

### `MEM-03` — La memoria justifica F_pga con una convergencia de la que ha desaparecido la fila que importa

**Sev** ALTA · **Veredicto** CONTRADICE · **Documento** Memoria exportada
**Ubicación repo** src/criterios_adoptados.py:460 · memoria generada, Sec. 3.2
**Ubicación PDF** Manual de Puentes, Tabla 2.4.3.11.2.1.2-1 y Nota 2, pág. impresa 123 (PDF 124)

**Afirmación del repo.** La justificación de `F_pga = 1.0`, **impresa en la Sección 3.2 de la memoria**: «Sin SPT no hay clase de sitio definitiva. Para PGA ≥ 0.50 **los factores convergen: 1.0 para clases C y D, 0.9 para E**…».

**Qué dice el documento.** Los tres valores **confirman**. Lo que no aparece es la cuarta fila de la misma columna: la Tabla 2.4.3.11.2.1.2-1 trae «**F² * * * * ***» con la Nota 2 «Llevar a cabo investigaciones geotécnicas específicas del sitio y análisis de respuesta dinámica de sitio, para todos los sitios en sitio clase F».
El proyecto sostiene en otro lado que **este sitio es Clase F**. La memoria, entonces, justifica el valor adoptado con una convergencia entre C, D y E que no incluye la clase que el propio expediente se atribuye — y la fila que le correspondería no da factor, exige un estudio. Las dos afirmaciones conviven en la misma memoria sin cruzarse.

### 11.3 Medias

### `HID-06` — El título entrecomillado de la Tabla N° 10 omite «(m/s)»

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:78 · src/modulos/M5_verificaciones.py:131-134 · src/criterios_adoptados.py (`v_max_concreto_eleccion`)
**Ubicación PDF** Manual de Hidrología, Tabla N° 10, pág. impresa 76 (PDF 79)

**Afirmación del repo.** El título se transcribe entre comillas como «**Velocidades máximas admisibles en conductos revestidos**», en `constantes_normativas.py`, en `NUMERAL_V3` y en el criterio que la memoria imprime.

**Qué dice el documento.** El título impreso es «TABLA N° 10: **Velocidades máximas admisibles (m/s) en conductos revestidos**». Falta «(m/s)» en las tres copias. En una cita entre comillas que la memoria reproduce, la unidad omitida es precisamente lo que un revisor comprobaría primero.

### `HID-07` — Los nombres de fila de las Tablas N° 02 y N° 10 están recortados

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:64-67 y :84-89
**Ubicación PDF** Manual de Hidrología, Tabla N° 02 pág. 25 (PDF 28) · Tabla N° 10 pág. 76 (PDF 79)

**Afirmación del repo.** Claves `quebrada_importante` / `quebrada_menor` en `RIESGO_ADMISIBLE`, y `mamposteria_piedra` en `V_MAX`.

**Qué dice el documento.** Tabla N° 02: las filas son «Alcantarillas de paso de quebradas importantes **y badenes**» y «Alcantarillas de paso quebradas menores **y descarga de agua de cunetas**». Lo recortado importa: la segunda categoría cubre también la descarga de cunetas, que es justo lo que la Fase 10 dimensiona.
Tabla N° 10: la fila es «Mampostería de piedra **y concreto**», y trae un **solo valor (2.0)**, no un par; el código lo convierte en `(2.0, 2.0)`.

### `HID-08` — R y n de la Tabla N° 02 son máximos recomendados, y la norma asigna la decisión al propietario

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:64-67 · src/modulos/M1_clasificacion.py
**Ubicación PDF** Manual de Hidrología, Tabla N° 02 y notas, pág. impresa 25 (PDF 28)

**Afirmación del repo.** `RIESGO_ADMISIBLE` se declara `[N]` y sus valores entran directamente al cálculo de TR.

**Qué dice el documento.** Los **números confirman** (R 0.30 / n 25 → TR 71; R 0.35 / n 15 → TR 35, ambos correctos con la fórmula (1) del num. 3.6). Pero el título de la tabla es «**VALORES MÁXIMOS RECOMENDADOS** de riesgo admisible», el texto que la introduce dice «se recomienda utilizar **como máximo**», y la nota al pie cierra:

> El Propietario de una Obra es el que define el riesgo admisible de falla y la vida útil de las obras.

Techo recomendado más decisión del propietario se parece más a un `[A]` declarado que a una constante `[N]`.

### `HID-09` — El 0.25 m/s está en la pág. 77; la 76 es donde arranca el párrafo

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:32-39 · src/modulos/M5_verificaciones.py:125-130
**Ubicación PDF** Manual de Hidrología, págs. impresas 76-77 (PDF 79-80)

**Afirmación del repo.** «num. 4.1.1.3.6, **pág. 76**, párrafo inmediatamente posterior a la Tabla N° 10».

**Qué dice el documento.** El párrafo empieza en la pág. 76 y **termina en la 77**: «…que pueda incidir en una» / «reducción de su capacidad hidráulica, recomendándose que la velocidad mínima sea igual a **0.25 m/s**». Quien vaya a la pág. 76 a comprobar el número no lo encuentra ahí. «Párrafo inmediatamente posterior a la Tabla N° 10» ✔ y el numeral 4.1.1.3.6 ✔.

### `HID-10` — V1 y V2 salen del mismo tipo de frase y solo una lleva el matiz de recomendación

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/modulos/M5_verificaciones.py:115 y :125-130
**Ubicación PDF** Manual de Hidrología, num. 4.1.1.3.7 b), pág. impresa 79 (PDF 82)

**Afirmación del repo.** `NUMERAL_V2` lleva expresamente «el numeral **RECOMIENDA, no prohíbe**» y se aplica como umbral duro «por decisión conservadora del proyecto». `NUMERAL_V1 = "4.1.1.3.7 b)"` va pelado.

**Qué dice el documento.** El 4.1.1.3.7 b) «Borde libre» está redactado igual de blando: «**Se recomienda** que el diseño hidráulico considere como mínimo el 25 % de la altura, diámetro o flecha de la estructura.» El 25 % y la lectura y/D ≤ 0.75 **confirman**. Lo que no se sostiene es el trato asimétrico: dos «se recomienda» del mismo numeral, uno anotado como recomendación y el otro presentado como exigencia. Un revisor que vea el matiz en V2 preguntará por qué no está en V1.

### `HID-11` — La Tabla N° 09 tiene tres columnas y el código transcribe dos, eligiendo una subfila sin declararlo

**Sev** MEDIA · **Veredicto** CONFIRMA · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:70-76
**Ubicación PDF** Manual de Hidrología, Tabla N° 09, pág. impresa 75 (PDF 78)

**Afirmación del repo.** `MANNING = {metal_corrugado: (0.021, 0.030), concreto_recto: (0.010, 0.013), madera_duelas: (0.010, 0.014)}`, comentado como «(n_min, n_max)».

**Qué dice el documento.** Los seis números **confirman dígito por dígito**. Dos matices:
· La tabla tiene **MÍNIMO / NORMAL / MÁXIMO**; el código descarta la columna NORMAL, que es la de uso corriente (0.024 para metal corrugado, 0.011 para concreto recto, 0.012 para madera).
· «Metal corrugado» tiene dos subfilas: *sub-dren* (0.017 / 0.019 / 0.021) y *dren para aguas lluvias* (0.021 / 0.024 / 0.030). El código toma la segunda —la correcta para una alcantarilla— pero no declara la elección, y el par (0.021, 0.030) coincide numéricamente con el máximo de la primera subfila.
La afirmación negativa «HDPE no está listado» **confirma**.

### `SUE-04` — El Cuadro 4.1 también fija la profundidad de calicata, que no se recoge

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Suelos
**Ubicación repo** src/constantes_normativas.py:152-172
**Ubicación PDF** Manual de Suelos, num. 4.2 y Cuadro 4.1, pág. impresa 28 (PDF 29)

**Afirmación del repo.** Del Cuadro 4.1 se transcriben `CALICATAS_POR_KM` y `CALICATAS_POR_SENTIDO`.

**Qué dice el documento.** Los dos **confirman** (4/4/4/3/2/1, y «× km × sentido» solo para autopistas y duales). El Cuadro tiene además una columna «Profundidad (m)» con el mismo valor en todas las filas: «**1.50 m respecto al nivel de sub rasante del proyecto**», reforzado por el num. 4.2 («calicatas de 1.5 m de profundidad mínima»). Es un valor `[N]` del mismo cuadro que el proyecto no lleva.

### `SUE-05` — «Resguardo» es palabra del proyecto, no del Manual, y el resguardo admite remedios alternativos

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Suelos
**Ubicación repo** src/constantes_normativas.py:141-145 · src/modulos/M5_verificaciones.py:321-322 · M7_geometria.py:82
**Ubicación PDF** Manual de Suelos, num. 4.5.4, págs. impresas 41-42 (PDF 42-43) · num. 9.1(3), págs. 89-90

**Afirmación del repo.** `RESGUARDO_NAPA_SUBRASANTE`, `resguardo_por_cbr()`, `resguardo_HW_subrasante` y V4 tratan el valor como umbral duro.

**Qué dice el documento.** Los **cuatro escalones y los cuatro intervalos de CBR confirman literalmente**: «El nivel superior de la sub rasante debe quedar encima del nivel de la napa freática como mínimo a 0.60 m… (CBR ≥ 20 %); a 0.80 m… (6 % ≤ CBR < 20 %); a 1.00 m… (3 % ≤ CBR < 6 %); y a 1.20 m… (CBR < 3 %)». Transcripción impecable.
Dos matices: el Manual **no usa la palabra «resguardo»** en este sentido (0 ocurrencias en el Manual de Hidrología y en E.050; la única en el Manual de Suelos es «al resguardo de la luz», sobre conservación de muestras), y la frase continúa: «En caso necesario, **se colocarán subdrenes o capas anticontaminantes y/o drenantes o se elevará la rasante** hasta el nivel necesario» — es decir, el incumplimiento admite remedio y no es un rechazo binario.

### `ANA-01` — El argumento de conservadurismo de la analogía descansa en una fuente que no está en el repositorio

**Sev** MEDIA · **Veredicto** NO VERIFICABLE · **Documento** Analogía [N→]
**Ubicación repo** src/criterios_adoptados.py:1074-1108 · memoria generada
**Ubicación PDF** AASHTO LRFD 9.ª ed., Tabla 12.6.6.3-1, pág. 12-22 · WSDOT M 23-03.12: no disponible

**Afirmación del repo.** «La analogía es conservadora: **el HDPE es el material con MENOR tolerancia a cobertura reducida bajo carga viva**… exigir su recubrimiento al concreto y al TMC **no puede quedar del lado inseguro**». La memoria lo imprime, apoyado en «WSDOT M 23-03.12, Tabla 8-6» como referencia comparativa.

**Qué dice el documento.** La **dirección** del argumento se sostiene contra AASHTO 12.6.6.3: el termoplástico bajo pavimento pide ID/2 ≥ 24 in mientras el concreto y el metal piden ≥ 12 in. Pero:
· La **magnitud** no: el valor adoptado, 0.30 m, queda por debajo del piso de 12 in de concreto y metal (0.305 m) y muy por debajo del Bc/8 que gobierna en diámetros grandes. La analogía es conservadora en el orden de los materiales y **no en el número**.
· **WSDOT no está en el repositorio**, de modo que la única cita que la memoria ofrece al revisor para sostener «el concreto tolera más» es incomprobable.
· La analogía **sí está declarada como analogía**, con etiqueta `[N→]` y con las palabras «ADOPCIÓN POR ANALOGÍA SOBRE UN VACÍO VERIFICADO», tanto en el criterio como en la memoria. ✔

### `ANA-02` — La analogía del resguardo está declarada y el numeral original dice lo que se le atribuye

**Sev** MEDIA · **Veredicto** CONFIRMA · **Documento** Analogía [N→]
**Ubicación repo** src/criterios_adoptados.py:908-917 · src/modulos/M5_verificaciones.py:134
**Ubicación PDF** Manual de Suelos, num. 4.5.4 págs. 41-42 y num. 9.1(3) págs. 89-90

**Afirmación del repo.** `resguardo_HW_subrasante = "segun_CBR"`, etiqueta `[N→]`: la tabla del num. 4.5.4 —que regula el nivel freático— aplicada al HW de avenida, «el numeral regula el nivel freático, no un nivel transitorio».

**Qué dice el documento.** El num. 4.5.4 **sí regula el nivel freático** y la tabla es la que el código transcribe; el 9.1(3) la repite en el capítulo de estabilización. La analogía está declarada como tal, la etiqueta `[N→]` es la correcta según la taxonomía del propio proyecto y la memoria la imprime como analogía.
*Lo que un revisor preguntará*: el resguardo del 4.5.4 protege la subrasante del **ascenso capilar continuo** de un freático permanente. Un HW de avenida moja el terreno durante horas, por un mecanismo distinto, y puede subir por encima del freático. Que la analogía quede del lado seguro no se deduce del numeral: es plausible, no demostrado, y el criterio lo presenta como establecido.

### `ANA-03` — La analogía de embocadura del HDPE usa la fila que da menos carga que la del metal

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** HDS-5
**Ubicación repo** src/criterios_adoptados.py, criterio `hds5_embocadura_hdpe`
**Ubicación PDF** HDS-5 3.ª ed., Tabla A.1, pág. A.8 (PDF 197)

**Afirmación del repo.** `hds5_embocadura_hdpe = {K: 0.0098, M: 2.00, c: 0.0398, Y: 0.67, Ks: -0.5}`, etiqueta `[C]`: la fila del concreto aplicada al HDPE de interior liso a ras del muro.

**Qué dice el documento.** Los cinco valores **confirman** contra la Tabla A.1 (fila «Circular Concrete / Square edge w/headwall»), y la página citada, **A.8, es correcta**.
Pero la analogía no es conservadora: en la misma tabla, «Circular CM / Headwall» da K = 0.0078, c = 0.0379, Y = 0.69. Aplicando la rama sumergida HWᵢ/D = c·q*² + Y + KₛS, la fila del concreto da un HW **menor** que la del metal en el rango de q* de interés. Elegir el concreto para un material intermedio produce una carga a la entrada más baja, que es la dirección insegura para V1 y para el resguardo. El criterio no declara esa comparación.

### `HDS-03` — Ku, los límites 3.5/4.0 y las ecuaciones no están en la Tabla A.1 sino en el texto que la precede

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** HDS-5
**Ubicación repo** src/constantes_normativas.py:93-97 · src/modulos/M4_control.py
**Ubicación PDF** HDS-5 3.ª ed., Secs. A.2.1 y A.2.2, págs. A.1-A.2 (PDF 190-191) · Tabla A.1, pág. A.8 (PDF 197)

**Afirmación del repo.** `KU_METRICO = 1.811`, `Q_LIM_NO_SUMERGIDO = 3.5` y `Q_LIM_SUMERGIDO = 4.0` se atribuyen los tres a «**Apéndice A, Tabla A.1, pág. A.8**», y el docstring de M4 dice que «las dos ramas extremas sí son las ecuaciones literales de la Tabla A.1».

**Qué dice el documento.** Los **tres valores confirman**, y su uso conjunto es correcto —el punto donde más proyectos se equivocan—: HDS-5 dice «applies up to about Q/AD⁰.5 = 3.5 (**1.93 SI**)» y «above about Q/AD⁰.5 = 4.0 (**2.21 SI**)», de modo que al multiplicar por Kᵤ = 1.811 los umbrales que corresponden son los ingleses, 3.5 y 4.0, que es lo que M4 hace. ✔
Lo que no cuadra es la ubicación: la Tabla A.1 (pág. A.8) contiene *solo* las constantes K, M, c, Y por carta. Kᵤ, Kₛ, los límites y las ecuaciones (A.1)-(A.3) están en el texto de la **Sec. A.2, págs. A.1-A.2**. La constante `Ks`, que el manifiesto marca «⚠ el código declara que NO figura en la Tabla A.1: proviene de la formulación», tiene numeral y página: **Sec. A.2.1, pág. A.2**, «Kₛ Slope correction, −0.5 (mitered inlets +0.7)».

### `E060-04` — «Aumentar adecuadamente» no es lo que dice el artículo

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.060
**Ubicación repo** src/constantes_normativas.py:297-300 · docs/manifiesto_citas.md §5
**Ubicación PDF** E.060, Art. 7.7.5.1, pág. 55

**Afirmación del repo.** El comentario y el manifiesto entrecomillan que «el artículo dice “**aumentar adecuadamente**” y no fija cuánto».

**Qué dice el documento.** El Art. 7.7.5.1 (pág. 55) dice:

> En ambientes corrosivos u otras condiciones severas de exposición, **debe aumentarse adecuadamente** el espesor del recubrimiento de concreto y debe tomarse en consideración su densidad y porosidad o debe disponerse de otro tipo de protección.

El fondo —que no fija cuánto— **confirma**. La cita entrecomillada no coincide: cambia la forma verbal y omite la alternativa expresa («o debe disponerse de otro tipo de protección»), que es un camino de cumplimiento distinto del que el criterio contempla.

### `E060-05` — La Tabla 4.4 tiene dos escalas y seis cementos; el código lleva una escala y tres

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.060
**Ubicación repo** src/constantes_normativas.py:287-292
**Ubicación PDF** E.060, Tabla 4.4, pág. 38

**Afirmación del repo.** `SULFATOS` transcribe «(SO4_min %, SO4_max %, cemento, a/c, f'c)» con el cemento moderado como «**II/IP(MS)/IS(MS)**».

**Qué dice el documento.** Los **cuatro rangos, las tres relaciones a/c y los tres f'c confirman** exactamente (0,50 / 28; 0,45 / 31; 0,45 / 31). Dos omisiones:
· La tabla da la exposición por **dos vías paralelas**: «Sulfato soluble en agua (SO₄) presente en el **suelo**, porcentaje en peso» y «Sulfato (SO₄) en el **agua**, ppm» (150 / 1500 / 10000). El código solo lleva la del suelo; si el expediente trae un análisis de agua —lo esperable con ANA de por medio— la tabla no se puede aplicar.
· El cemento para exposición moderada son **seis** tipos: «II, IP(MS), IS(MS), **P(MS), I(PM)(MS), I(SM)(MS)**». Se transcriben tres.

### `E060-06` — Los cloruros salen de la Tabla 4.2, y la regla de combinación de las dos tablas no se recoge

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.060
**Ubicación repo** src/constantes_normativas.py:293
**Ubicación PDF** E.060, Tabla 4.2 pág. 37 · Tabla 4.4 y su nota al pie, pág. 38

**Afirmación del repo.** `CLORUROS_EXTERNOS = {a_c_max: 0.40, fc_min_MPa: 35} # Art. 4.2 / 4.4`.

**Qué dice el documento.** Los dos **valores confirman**, y salen de la **Tabla 4.2 «Requisitos para condiciones especiales de exposición» (pág. 37)**, fila «Para proteger de la corrosión el refuerzo de acero cuando el concreto está expuesto a cloruros provenientes de productos descongelantes, sal, agua salobre, agua de mar o a salpicaduras». El 4.4 es «Protección del refuerzo contra la corrosión» y remite a la Tabla 4.5, sobre contenido de ion cloruro en el concreto endurecido: otra exigencia.
Falta además la nota al pie que gobierna este proyecto, donde sulfatos y cloruros coinciden:

> Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se debe utilizar la **menor** relación máxima agua-material cementante aplicable y el **mayor** f'c mínimo.

### `E060-07` — Para el concreto ciclópeo se cita el mínimo menos exigente de los dos disponibles

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.060 · EG-2013
**Ubicación repo** src/constantes_normativas.py:326-328
**Ubicación PDF** E.060 Art. 22.10, págs. 194-195 · EG-2013 Tabla 503-07, pág. impresa 912

**Afirmación del repo.** `CICLOPEO_FC_MATRIZ_MIN = 10.0` MPa y `CICLOPEO_FRACCION_PIEDRA_MAX = 0.30`, Art. 22.10 de E.060.

**Qué dice el documento.** E.060 Art. 22.10 **confirma**: f'c de la matriz = 10 MPa y piedra desplazadora ≤ 30 % del volumen total, en las págs. 194-195.
Pero el EG-2013 —cuya Sección 503 es la que el proyecto cita para cabezales— fija en su **Tabla 503-07** el concreto ciclópeo **Clase G**: «Se compone de concreto simple Clase F y agregado ciclópeo, en proporción de 30 % del volumen total, como máximo — **14 MPa** (140 kg/cm²)». Para una obra vial del MTC, el mínimo aplicable es el mayor de los dos, y el proyecto declara el menor sin mencionar el otro.

### `E050-01` — «Sísmico» sustituye a dos condiciones distintas que la norma nombra de otra forma

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.050
**Ubicación repo** src/constantes_normativas.py:266-272
**Ubicación PDF** E.050, Art. 21 pág. 34 · num. 39.13.6 pág. 72 · Art. 30.3 pág. 39

**Afirmación del repo.** La clave de la segunda columna de `FS` es `"sismico"` en las cinco filas.

**Qué dice el documento.** Los **diez números confirman** en las páginas declaradas (3,0/2,5 en Art. 21.1-21.2 pág. 34; 1,50/1,25 en 39.13.6 a) y b) pág. 72; 1,5/1,25 en Art. 30.3 pág. 39). Pero la norma nombra dos condiciones distintas: el Art. 21.2 dice «para solicitación máxima de **sismo o viento** (la que sea más desfavorable)» y el 39.13.6 dice «Condición **Pseudo-dinámico**». Colapsarlas en «sismico» pierde el viento del Art. 21.2 y renombra la condición del 39.13.6 sin declararlo.

### `E050-02` — El espaciamiento del SPT sí tiene numeral: la marca «⚠ sin numeral» se puede cerrar

**Sev** MEDIA · **Veredicto** CONFIRMA · **Documento** E.050
**Ubicación repo** src/constantes_normativas.py:284 · docs/manifiesto_citas.md §4 y §13
**Ubicación PDF** E.050, Art. 38.4.3, pág. 51

**Afirmación del repo.** `SPT_ESPACIAMIENTO = 1.0` «m entre ensayos», que el manifiesto marca «**⚠ sin numeral propio** (hereda el Art. 38 de la línea anterior)» y lista entre los puntos que la verificación debería mirar primero.

**Qué dice el documento.** Los dos valores salen de una sola frase del **Art. 38.4.3**:

> Las perforaciones deben tener una profundidad mínima de **15 m** y deben ser realizadas por las técnicas de lavado o rotativa. Dentro de las perforaciones se llevan a cabo Ensayos de Penetración Estándar SPT (NTP 339.133) **espaciados obligatoriamente cada 1 m**.

El numeral preciso es **38.4.3, pág. 51**, y el contexto es el programa de exploración para licuefacción, que es exactamente el uso que el proyecto le da. La marca se puede retirar.

### `AAS-03` — Tres páginas de AASHTO citadas en las fuentes de criterios están corridas

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py, criterios `factores_carga_aashto` y `procedimiento_flexion_corte_aashto_sec5`
**Ubicación PDF** AASHTO LRFD 9.ª ed., págs. 3-17, 3-18, 5-29, 5-64, 5-67, 5-70

**Afirmación del repo.** `factores_carga_aashto` → «Tablas 3.4.1-1 (**pág. 3-14**) y 3.4.1-2 (pág. 3-18); transcritas también en Manual de Puentes MTC, **págs. 143 y 146**» · `procedimiento_flexion_corte_aashto_sec5` → «Arts. 5.5.4.2 (**pág. 5-32**) y 5.7.3.4.2 / 5.7.3.3 / 5.7.2.8 (**págs. 5-70 a 5-243**)».

**Qué dice el documento.** · Tabla 3.4.1-1 → pág. **3-17** (no 3-14). Tabla 3.4.1-2 → 3-18 ✔.
· En el Manual de Puentes ambas están en la **pág. 143**; la 146 no las contiene.
· Art. 5.5.4.2 «Resistance Factors» → pág. **5-29** (no 5-32; en la 5-32 empieza 5.5.4.3).
· 5.7.2.8 «Shear Stress on Concrete» → 5-64 y 5.7.3.3 «Nominal Shear Resistance» → 5-67, ambas **anteriores** al 5-70 con que arranca el rango declarado.
Los **artículos existen y están bien titulados**, y los φ = 0.90 de flexión y de corte confirman literalmente.

### `PUE-11` — La columna de la tabla F_pga es «PGA > 0.50» y el PGA de este proyecto es exactamente 0.50

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/constantes_normativas.py:238-240
**Ubicación PDF** Manual de Puentes, Tabla 2.4.3.11.2.1.2-1, pág. impresa 123 (PDF 124)

**Afirmación del repo.** `F_PGA_TABLA = {C: 1.0, D: 1.0, E: 0.9} # Tabla 2.4.3.11.2.1.2-1, PGA >= 0.50`.

**Qué dice el documento.** Los **tres valores confirman**. La columna se rotula «**PGA > 0.50**», estrictamente mayor, y la Nota 1 manda «usar línea recta de interpolación para valores intermedios de PGA». Con `PGA_roca_B = 0.50` exactamente, el sitio cae en la frontera entre la columna «PGA = 0.40» y la «> 0.50»; para la Clase D eso es 1.1 frente a 1.0.
Se omiten además las filas **A (0.8)**, **B (1.0)** —justamente la clase sobre la que se lee el PGA— y **F (asterisco)**.

### `PUE-12` — Una regla del numeral de k_h0 para cimentaciones en roca no se implementa ni se descarta

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/modulos/M9_cabezal.py:28 y :281 · src/datos_sitio.py:128
**Ubicación PDF** Manual de Puentes, num. 2.8.1.1.14.2.1, pág. impresa 254 (PDF 255)

**Afirmación del repo.** M9 calcula Aₛ = F_pga · PGA y kₕ₀ = Aₛ, leyendo `PGA_roca_B`.

**Qué dice el documento.** La igualdad kₕ₀ = Fₚgₐ·PGA = Aₛ **confirma**. El mismo párrafo añade:

> Para muros cimentados sobre Sitio con suelos **Clase A o B (roca dura o blanda)**, kₕ₀ estará basado en **1.2 veces** el coeficiente de aceleración pico del suelo.

Probablemente no aplique —la fundación es la llanura arenosa, no roca— pero el dato de sitio se llama `PGA_roca_B` y nada en el código dice por qué el 1.2 no entra. Es exactamente el tipo de regla que un revisor busca al ver «roca_B» en el nombre.

### `PUE-13` — La segunda figura de Meyerhof está fuera del rango de páginas citado

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/constantes_normativas.py:262 · src/criterios_adoptados.py (`N_cq_N_gammaq_meyerhof`)
**Ubicación PDF** Manual de Puentes, num. 2.8.1.3.1.2c págs. impresas 272-274 (PDF 273-275)

**Afirmación del repo.** «figuras 2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), **págs. 272-273**» y `NUMERAL_ZAPATA_EN_TALUD = "2.8.1.3.1.2c, pags. 272-273"`.

**Qué dice el documento.** **Confirma** el texto («Para zapatas apoyadas en taludes o cerca de ellos: Nq = 0.0» y «Nc y Nγ se reemplazarán con Ncq y Nγq»), la numeración de las dos figuras y su atribución a Meyerhof 1957. El texto está en la pág. 272 y la **Figura -1 en la 273**, pero la **Figura -2 está en la pág. 274**, fuera del rango declarado.

### `VOC-04` — «Clase F» significa dos cosas incompatibles dentro del mismo expediente

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Trampa de vocabulario
**Ubicación repo** src/constantes_normativas.py:206-207 · src/criterios_adoptados.py:386
**Ubicación PDF** EG-2013 Tabla 503-07 pág. 912 · Manual de Puentes Tabla 2.4.3.11.2.1.1-1 pág. 122

**Afirmación del repo.** `CAMA_RELLENO_LATERAL["concreto_simple"]` usa «Concreto **Clase F** (f'c = 14 MPa)» y el criterio `clase_sitio` usa «**Clase F**» de sitio sísmico. Ambos llegan a la memoria.

**Qué dice el documento.** Son dos taxonomías sin relación: EG-2013 Tabla 503-07 clasifica el concreto en A-B (pre/postensado), C-D-E (reforzado), **F (simple, 14 MPa)** y G (ciclópeo); AASHTO y el Manual de Puentes clasifican el **sitio** en A-F, donde F son «suelos que requieren evaluaciones específicas de sitio». Ninguno de los dos usos se marca en la memoria, y el segundo es el eje de la Sec. 0.5.

### `E030-01` — El Tr = 475 años no lo escribe el artículo; es una derivación

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.030
**Ubicación repo** src/datos_sitio.py:194-215
**Ubicación PDF** E.030 (2026), Art. 11.1 y Tabla N° 1, pág. PDF 9

**Afirmación del repo.** `Z_E030 = 0.45`, concepto: «Factor de zona Z de E.030 (aceleración máxima en suelo rígido **para Tr = 475 años**)», fuente «Art. 11.1».

**Qué dice el documento.** El Art. 11.1 **confirma Z = 0,45 para la Zona 4** (Tabla N° 1) y dice: «Este factor representa la aceleración máxima horizontal en suelo rígido con una probabilidad de **10 % de ser excedida en 50 años**». No escribe «475 años». La equivalencia es correcta y estándar, pero es una derivación del proyectista presentada como concepto de la norma.

### `E030-03` — El mejor argumento para descartar E.030 está en su Art. 4 y no se usa

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** E.030
**Ubicación repo** src/datos_sitio.py:158-165 y :204-213 · docs/manifiesto_citas.md §10
**Ubicación PDF** E.030 (2026), Art. 4, pág. impresa 7

**Afirmación del repo.** El descarte de E.030 se justifica **solo por periodo de retorno**: «Sec. 0.4 descarta el sismo de 475 años de E.030 en favor del PGA de Tr = 1000 años del Manual de Puentes».

**Qué dice el documento.** El Art. 4 «Ámbito de aplicación» acota la norma antes de que el periodo de retorno entre en juego:

> La presente Norma Técnica es de cumplimiento obligatorio a nivel nacional y se aplica a: a) El diseño de **edificaciones** nuevas. b) El reforzamiento de **edificaciones** existentes y la reparación de estructuras que resulten dañadas por la acción de los sismos.

Un cabezal de alcantarilla en una carretera no es una edificación. Ese es un argumento de ámbito, más limpio y más fuerte que el de periodo de retorno, y el expediente no lo invoca en ningún sitio. La consecuencia práctica es que la memoria defiende el descarte por la vía discutible (¿por qué no usar los dos?) en vez de por la vía cerrada.

### `COH-02` — El código se aparta de su fuente de verdad declarada, con acierto, y sin autorización escrita

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Coherencia interna
**Ubicación repo** Claude.md · src/constantes_normativas.py:124-126 · docs/hoja_de_ruta_alcantarillas_v8.md:436, 440, 797, 908
**Ubicación PDF** —

**Afirmación del repo.** `Claude.md`: «Fuente normativa única: `docs/hoja_de_ruta_alcantarillas_v8.md`… **Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta**». `constantes_normativas.py:124-126`: «Aquí **gana la fuente primaria HDS-5** por verificación externa; la hoja de ruta debe corregirse».

**Qué dice el documento.** La decisión es **correcta en el fondo** (ver COH-01) y está declarada, que es lo importante. Lo que falta es la regla: la excepción «una verificación externa contra la fuente primaria gana a la hoja de ruta» no está escrita en ningún sitio, de modo que el proyecto tiene hoy dos jerarquías incompatibles y un precedente sin norma. Y el número sigue mal en la fuente de verdad: quien la lea sin leer el código diseña con 19.62.

### `F-01` — El corredor de ~5 km está endurecido en un archivo de código

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Datos vs constantes
**Ubicación repo** src/datos_sitio.py:94
**Ubicación PDF** —

**Afirmación del repo.** `AMBITO_CORREDOR = "todo el corredor (el terraplén de ~5 km de la Fase 0-bis de la hoja de ruta, num. 150)"`, valor por defecto del campo `ambito` de todo dato de sitio.

**Qué dice el documento.** *Clasificación.* Es un hecho de **este** expediente escrito como constante de módulo, y la memoria lo imprime en la declaración de datos de sitio. No mueve ningún número, pero es exactamente lo que la etiqueta `[S]` existe para evitar: aplicar la app a otra carretera y heredar en silencio «~5 km». El ámbito debería ser un dato del proyecto, no un literal del archivo que define la etiqueta.

### `F-02` — El barrido de literales no recorre cli.py ni gui/app.py

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** Datos vs constantes
**Ubicación repo** tests/test_sin_literales.py:1-60
**Ubicación PDF** —

**Afirmación del repo.** `tests/test_sin_literales.py` se presenta como la guardia de «todo literal numérico bajo `src/`», con seis archivos exentos.

**Qué dice el documento.** *Alcance.* `cli.py` (69 KB) y `gui/app.py` quedan fuera del recorrido, y son justamente donde se fijan defaults de línea de comandos y de formulario. La regla de arquitectura de `Claude.md` habla de «ningún módulo», no de «ningún módulo bajo src/». *Verificado*: las quince marcas `# literal-ok` del árbol son todas partes de fórmula transcrita (el 45 de Kₐ de Rankine, el 1/3 del centroide, los exponentes de Manning, π/4, D/4, 4/3) — ninguna es abusiva. El hueco es de cobertura, no de contenido.

### `MEM-02` — Lo que la memoria sí hace bien

**Sev** MEDIA · **Veredicto** CONFIRMA · **Documento** Memoria exportada
**Ubicación repo** src/plantillas/memoria_alcantarillas.html · memoria_perfil.html · src/modulos/M11_reporte.py
**Ubicación PDF** —

**Afirmación del repo.** Se generaron las dos memorias (`--alcance expediente` y `--alcance perfil`) sobre `tests/ejemplo_puntos.csv` y se leyeron enteras, junto con las dos plantillas y M11.

**Qué dice el documento.** *Verificado sobre el HTML generado.*
· **Ninguna cita sale truncada**: no hay recorte por longitud en M11 ni en las plantillas.
· Las **plantillas no contienen ningún numeral ni número normativo escrito a mano**: todo lo normativo llega desde los modelos.
· La **analogía `[N→]` se declara como analogía**, con las palabras «ADOPCIÓN POR ANALOGÍA SOBRE UN VACÍO VERIFICADO, a nivel de PERFIL» y la distinción entre lo que destraba el perfil y lo que sigue pendiente de expediente.
· La **adopción sin respaldo normativo de la Clase F se imprime** con esas palabras, en el Tablero 1.
· La **advertencia de trazabilidad incompleta del PGA** aparece (9 menciones de «trazabilidad»).
· `--proyecto` no trae valor por defecto: sin declararlo, la memoria dice «(proyecto no declarado)».
Lo que la memoria arrastra son los **errores de página** de EG-01 y HID-02, no defectos de la capa de reporte.

### `HDS-06` — El «Cap. IV» que se cita para la zona de transición es, en la 3.ª edición, el capítulo de paso de fauna acuática

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** HDS-5
**Ubicación repo** src/criterios_adoptados.py:719-722 · docs/manifiesto_citas.md §7
**Ubicación PDF** HDS-5 3.ª ed., índice pág. xiii y encabezado del Cap. 4 (PDF 17 y 127) · Sec. A.1 pág. A.1 (PDF 190)

**Afirmación del repo.** `metodo_transicion_hds5`, fuente: «HDS-5 3.ª ed., abril 2012, **Cap. IV** y Apéndice A (curva de transición tangente, sin ecuación publicada)».

**Qué dice el documento.** En la 3.ª edición el índice dice «**CHAPTER 4 — CULVERT DESIGN FOR AQUATIC ORGANISM PASSAGE (AOP)**». Ese capítulo no menciona la zona de transición del control de entrada en ningún punto. La descripción de la curva tangente está en el **Apéndice A, Sec. A.1** (y el fenómeno se introduce en el Cap. 3). La mitad «Apéndice A» de la cita es correcta; la mitad «Cap. IV» apunta a un capítulo que en esta edición trata de otra cosa — es una referencia arrastrada de la 2.ª edición de 1985, cuya numeración de capítulos era distinta.

### `AAS-07` — El punto de aplicación del incremento sísmico se declara sin norma, y AASHTO lo trata

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py:579-599 · docs/manifiesto_citas.md §8 y §11.b
**Ubicación PDF** AASHTO LRFD 9.ª ed., C11.6.5.3 pág. 11-30 (PDF 1499) y Apéndice A11.3.1

**Afirmación del repo.** `punto_aplicacion_incremento_sismico = None`, etiqueta `[A]`: «la altura de aplicación es una **convención de la literatura** (Seed-Whitman la sitúa en ~0.6H)», con sensibilidad (0.333, 0.6)·H y sin numeral.

**Qué dice el documento.** AASHTO sí se pronuncia, en el comentario del artículo de empuje sísmico:

> C11.6.5.3: Past practice for locating the resultant of the static and seismic earth pressure for external wall stability has been to either **assume a uniform distribution** of lateral earth pressure for the combined static plus seismic stress or, if the static and seismic components of earth pressure are computed separately…

y el Apéndice A11.3.1 desarrolla el reparto. No fija un número único —el `[A]` es defendible—, pero la afirmación de que solo hay «convención de la literatura» pasa por alto que el cuerpo normativo que el proyecto adopta como Vía 1 describe el procedimiento y acota las alternativas.

### `PRO-05` — La memoria imprime las designaciones imperiales de un proyecto que opera en SI

**Sev** MEDIA · **Veredicto** CONTRADICE · **Documento** AASHTO M 170M
**Ubicación repo** src/modulos/M2_material.py:149 · src/constantes_normativas.py:133 · src/modulos/M11_reporte.py
**Ubicación PDF** AASHTO M 170M-04, encabezado de designación y §1.2 (PDF pág. 1)

**Afirmación del repo.** `NORMA_PRODUCTO["concreto_reforzado"] = "ASTM C76 / AASHTO M170"`, que es la etiqueta que M11 imprime en la memoria. El mismo par aparece en `D_MAX` y en `diametros_normalizados`.

**Qué dice el documento.** El documento que el proyecto tiene ahora en `normas/` se designa «**AASHTO Designation: M 170M-04 / ASTM Designation: C 76M-02**», titulado «Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe **[Metric]**», y su §1.2 dice: «This specification is the **metric counterpart of M 170**».
M 170 y C 76 son las versiones en pulgadas; M 170M y C 76M las métricas. `Claude.md` impone que «todo el código opera en SI» y que la conversión solo ocurre en la capa de reporte — y aquí es justo la capa de reporte la que nombra las imperiales. El repositorio alterna «AASHTO M170» y «AASHTO M-170M» según el archivo.

### 11.4 Bajas

### `PUE-14` — El recubrimiento de alcantarillas de 2.0 in lleva dos condiciones que no se recogen

**Sev** BAJA · **Veredicto** CONTRADICE · **Documento** Manual de Puentes
**Ubicación repo** src/criterios_adoptados.py:1129-1136
**Ubicación PDF** Manual de Puentes, Tabla 2.9.1.5.5.3-1, pág. impresa 378 (PDF 379)

**Afirmación del repo.** «el Manual sí usa la palabra “recubrimiento” para alcantarillas y da **2.0 in / 50 mm**».

**Qué dice el documento.** La fila existe y **confirma**, dentro de «Alcantarillas de cajón de concreto prefabricados»: «forjados para ser utilizados como superficie de conducción → 2.5 in · forjados con **inferior a 2 pies de relleno** que no se utilicen como una superficie de conducción → **2.0 in** · todos los demás miembros → 1.0 in». Los 2.0 in son de *alcantarillas cajón prefabricadas* con menos de 600 mm de relleno, no de alcantarillas en general. 2.0 in son 50.8 mm.

### `HID-12` — El diámetro mínimo de selva alta es específico de TMC y es una recomendación

**Sev** BAJA · **Veredicto** CONTRADICE · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:30
**Ubicación PDF** Manual de Hidrología, num. 4.1.1.3.7 a), pág. impresa 79 (PDF 82)

**Afirmación del repo.** `DIAMETRO_MIN_SELVA_ALTA = 1.22 # m = 48"; NO aplica en costa (4.1.1.3.7 a)`, con nombre genérico.

**Qué dice el documento.** **Confirma** numeral, página (79) y valor: «**Se recomienda** utilizar, en zonas de selva alta, con las características físicas y geomorfológicas indicadas en el párrafo anterior, como diámetro mínimo **alcantarillas TMC Ø 48"**». El Manual escribe 48" (1.2192 m, redondeado a 1.22 ✔), lo limita a **TMC** y lo condiciona a una lista de cuatro características geomorfológicas. El nombre de la constante no lleva ninguna de las tres restricciones. «No aplica en costa» ✔.

### `COH-03` — Las líneas que el código cita de la hoja de ruta están corridas siete

**Sev** BAJA · **Veredicto** CONTRADICE · **Documento** Coherencia interna
**Ubicación repo** src/constantes_normativas.py:124-126
**Ubicación PDF** —

**Afirmación del repo.** «docs/hoja_de_ruta_alcantarillas_v8.md (**líneas 432, 436, 790 y 901**) sigue escribiendo 19.62».

**Qué dice el documento.** *Defecto interno.* El 19.62 está en las líneas **436, 440, 797 y 908**. La 432 es el encabezado «### 4.3 Control de salida [C]»; falta la 440, que es la «Nota de unidades» —la más explícita de las cuatro—. Mismo patrón de desfase que las referencias del manifiesto, esta vez dentro del código.

### `HDS-04` — El +0.7 de inglete y el ke de 0.7 de inglete son dos coeficientes distintos con el mismo número

**Sev** BAJA · **Veredicto** CONFIRMA · **Documento** HDS-5
**Ubicación repo** src/constantes_normativas.py:104-107 · src/criterios_adoptados.py (`ke_entrada`)
**Ubicación PDF** HDS-5 3.ª ed., Sec. A.2.1 pág. A.2 · Tabla C.2 pág. C.6

**Afirmación del repo.** `Ks = +0.7` para embocadura ingleteada (corrección por pendiente) y, en la misma cadena de cálculo, `ke` como coeficiente de pérdida de entrada.

**Qué dice el documento.** Los dos **confirman por separado**: Kₛ = +0.7 para «mitered inlets» en la Sec. A.2.1 (pág. A.2), y kₑ = 0.7 para «Mitered to conform to fill slope» en la Tabla C.2 (pág. C.6). Son magnitudes sin relación que coinciden en valor y en condición. Con inglete, el mismo 0.7 aparece dos veces por dos motivos distintos: vale la pena anotarlo antes de que alguien los cruce.

### 11.5 Verificado correcto

### `OK-01` — La cita falsa que el proyecto retiró era efectivamente falsa

**Sev** OK · **Veredicto** CONFIRMA · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py:386-435 · docs/manifiesto_citas.md §8
**Ubicación PDF** AASHTO LRFD 9.ª ed., Arts. 3.10.2 y 3.10.3.1, Tablas 3.10.3.1-1 y C3.10.3.1-1, págs. 3-101 a 3-103

**Afirmación del repo.** §8 declara retirada la cita «`clase_sitio = "F_con_excepcion_periodo_corto"` — excepción para estructuras de periodo fundamental corto (≤ 0.5 s)», con la afirmación de que «la dispensa **no está** en el Art. 3.10.3.1, ni en C3.10.3.1, ni en tabla o nota alguna».

**Qué dice el documento.** **Re-verificado de forma independiente contra la 9.ª edición**: el Art. 3.10.3.1, el comentario C3.10.3.1, la Tabla 3.10.3.1-1 y la Tabla C3.10.3.1-1 no contienen ninguna dispensa por periodo corto. Lo único rotulado «Exceptions» en la tabla trata de propiedades del suelo desconocidas. Y el Art. 3.10.2 exige el procedimiento específico de sitio de forma incondicional cuando «The site is classified as Site Class F».
La retirada es correcta y bien fundada. Es el trabajo de verificación mejor hecho del expediente.

### `OK-02` — La curva de transición sin ecuación publicada existe y está descrita como el proyecto dice

**Sev** OK · **Veredicto** CONFIRMA · **Documento** HDS-5
**Ubicación repo** src/criterios_adoptados.py (`metodo_transicion_hds5`) · src/modulos/M4_control.py:14-90
**Ubicación PDF** HDS-5 3.ª ed., Sec. A.1, pág. A.1 (PDF 190)

**Afirmación del repo.** `metodo_transicion_hds5`: «HDS-5 no interpola: en la zona 3.5 < q* < 4.0 traza una **curva TANGENTE** a las dos ramas, un empalme empírico ajustado sobre sus datos de laboratorio **del que no publica ecuación cerrada**. Quien prescribe la recta es Sec. 4.2 de la hoja de ruta, no la fuente primaria.»

**Qué dice el documento.** Literal, en la Sec. A.1:

> Between the unsubmerged and the submerged conditions, there is a transition zone for which the NBS research provided only limited information. The transition zone is defined empirically by **drawing a curve between and tangent to** the curves defined by the unsubmerged and submerged equations.

Confirma los tres extremos: es tangente, es empírica y no hay ecuación. La simplificación está declarada como `[C]`, se invoca solo cuando un punto cae de verdad en la transición, y M4 rechaza con `DatoInvalidoError` cualquier otro valor del criterio. Es el manejo de vacío mejor construido del repositorio.

### `OK-03` — Las tres filas de constantes de embocadura son exactas

**Sev** OK · **Veredicto** CONFIRMA · **Documento** HDS-5
**Ubicación repo** src/constantes_normativas.py:99-106
**Ubicación PDF** HDS-5 3.ª ed., Tabla A.1, pág. A.8 (PDF 197)

**Afirmación del repo.** `HDS5_INLET`: concreto square edge w/headwall (0.0098, 2.00, 0.0398, 0.67) · CMP headwall (0.0078, 2.00, 0.0379, 0.69) · CMP mitered (0.0210, 1.33, 0.0463, 0.75).

**Qué dice el documento.** Tabla A.1, pág. A.8, filas 1 y 2:
· Chart 1, Circular Concrete, Scale 1, Square edge w/headwall → K 0.0098 · M 2.0 · c 0.0398 · Y 0.67 ✔
· Chart 2, Circular CM, Scale 1, Headwall → K 0.0078 · M 2.0 · c 0.0379 · Y 0.69 ✔
· Chart 2, Circular CM, Scale 2, Mitered to slope → K 0.0210 · M 1.33 · c 0.0463 · Y 0.75 ✔
Doce números, doce coincidencias. La página A.8 es correcta.

### `OK-04` — La cita textual larga de V_MIN coincide tilde por tilde

**Sev** OK · **Veredicto** CONFIRMA · **Documento** Manual de Hidrología
**Ubicación repo** src/constantes_normativas.py:36-39 · src/modulos/M5_verificaciones.py:186-189
**Ubicación PDF** Manual de Hidrología, num. 4.1.1.3.6, págs. impresas 76-77

**Afirmación del repo.** Transcripción entrecomillada de cuatro líneas en `constantes_normativas.py:36-39` y repetida en M5.

**Qué dice el documento.** Comparación palabra por palabra contra el PDF:

> Se deberá verificar que la velocidad mínima del flujo dentro del conducto no produzca sedimentación que pueda incidir en una reducción de su capacidad hidráulica, recomendándose que la velocidad mínima sea igual a 0.25 m/s.

Coincidencia literal, incluidas tildes y puntuación. Es la única cita textual larga del repositorio y está impecable. (La página, ver HID-09.)

### `OK-05` — El mapeo de secciones del EG-2013 y la corrección del nombre «SUBSECCION» son correctos

**Sev** OK · **Veredicto** CONFIRMA · **Documento** EG-2013
**Ubicación repo** src/constantes_normativas.py:190-196 · src/modulos/M8_estructural.py:143 · M9_cabezal.py:179
**Ubicación PDF** EG-2013, Capítulo V, págs. impresas 893-987

**Afirmación del repo.** `SECCION_EG2013 = {concreto_simple: "505", concreto_reforzado: "506", tmc: "507", hdpe: "508"}` y `SECCION_CABEZALES = "503"`, con la corrección declarada de que «son Secciones completas del Capítulo V, no subsecciones de ninguna “Sección 500”: esa denominación no existe».

**Qué dice el documento.** Títulos reales: **502** Rellenos para Estructuras (pág. 893) · **503** Concreto Estructural (903) · **504** Acero de Refuerzo (937) · **505** Tubería de Concreto Simple (947) · **506** Tubería de Concreto Reforzado (957) · **507** Tubería Metálica Corrugada (967) · **508** Tubería de Polietileno de Alta Densidad (979). No existe ninguna «Sección 500». `NUMERAL_9_1` confirma con su página: 503.01 está en la **pág. 905**. La remisión 506.02 → AASHTO M-170M está en la **pág. 959**, tal como se declara.

### `OK-06` — Los factores de seguridad, la zonificación y el perfil de suelo confirman sin excepción

**Sev** OK · **Veredicto** CONFIRMA · **Documento** E.050 · E.030 · Manual de Puentes
**Ubicación repo** src/constantes_normativas.py:266-284, :236-237 · src/datos_sitio.py
**Ubicación PDF** E.050 págs. 33, 39, 51, 72 · E.030 Anexo II y Arts. 11.1, 14.6 · Manual de Puentes págs. 103, 113, 122, 272

**Afirmación del repo.** Los diez valores de `FS`, `ZONA_SISMICA_LA_UNION = 4`, `Z_E030 = 0.45`, `PERFIL_SUELO_PRESUNTO = "S5"`, `SPT_PROF_MIN = 15.0`, `NUMERAL_C_PHI`, `NUMERAL_ZAPATA_TALUD_E050`, `NQ_ZAPATA_EN_TALUD = 0.0`, `CARGA_VIVA = "HL-93"` y el Tr = 1000 años del PGA.

**Qué dice el documento.** · E.050 Art. 20 (pág. 33): φ = 0 en cohesivos, c = 0 en friccionantes ✔ · Art. 30.1-30.2: doble verificación exacta ✔ · Art. 38.4.3: 15 m ✔
· E.030 Anexo II: **La Unión, provincia de Piura → Zona 4** ✔ (y existen otras «La Unión» en Zona 3: la insistencia del repositorio en nombrar distrito y provincia está justificada) · Art. 11.1, Tabla N° 1: Zona 4 → Z = 0,45 ✔ · Art. 14.6, Tabla N° 2: S5 «Suelos excepcionales», primera viñeta «Suelos potencialmente licuables» ✔
· Manual de Puentes: num. 2.4.3.8.2 «Subpresiones» pág. 113 ✔ · num. 2.4.3.2.2.1 (HL-93) pág. 103 ✔ · num. 2.8.1.3.1.2c: Nq = 0.0 ✔ · «7 % de probabilidad de excedencia en 75 años (equivalente a un periodo de retorno de **1000 años**). Los mapas… se presentan en el **Apéndice A3**» ✔

### `OK-07` — El vacío de altura mínima sí es real en el corpus peruano, y el paso de 0.15 m sí reproduce la serie

**Sev** OK · **Veredicto** CONFIRMA · **Documento** EG-2013 · normas de producto
**Ubicación repo** src/criterios_adoptados.py:1076-1121 · src/constantes_normativas.py:130
**Ubicación PDF** EG-2013 Secciones 502-508 · AASHTO M 170M-04 Tablas 1-5 · ASTM A760 Tabla 1

**Afirmación del repo.** §14.a puntos 1 y 3, y `D_PASO = 0.15 # m; reproduce las series de 6" y 150 mm`.

**Qué dice el documento.** · **EG-2013**: lectura íntegra de las Secciones 502, 505, 506 y 507 con búsqueda de «altura de relleno», «recubrimiento», «cobertura», «relleno mínimo», «sobre la clave», «0,30» y «0,60». La **única** cláusula de altura mínima sobre la clave en todo el Capítulo V es la de 508.07, para HDPE. El vacío para concreto y TMC **confirma**. La cláusula constructiva de 508.08 («el equipo y vehículos pesados no deberán circular sobre la estructura antes que la altura de relleno mínima sobre la misma sea de 0,30 m») también confirma, en la pág. 985.
· **Series de diámetros**: M 170M Tabla 3 da 300, 375, 450, 525, 600, 675, 750, 825, **900, 1050, 1200, 1350, 1500…** y A760 Tabla 1 da la misma progresión. De 900 mm en adelante el paso es exactamente **150 mm**. El arranque en 0.90 m y el paso de 0.15 m reproducen la serie real. ✔

### `OK-08` — El peso específico del concreto y los factores de resistencia están bien derivados y bien atribuidos

**Sev** OK · **Veredicto** CONFIRMA · **Documento** AASHTO LRFD
**Ubicación repo** src/criterios_adoptados.py, criterios `peso_especifico_concreto_kn_m3` y `procedimiento_flexion_corte_aashto_sec5`
**Ubicación PDF** AASHTO LRFD 9.ª ed., Tabla 3.5.1-1 y C3.5.1 pág. 3-21 · Art. 5.5.4.2 pág. 5-29

**Afirmación del repo.** `peso_especifico_concreto_kn_m3 = 23.56`, fuente «Tabla 3.5.1-1 + Comentario C3.5.1, pág. 3-21 (0.150 kcf, concreto normal armado)» · `phi_flexion = 0.9`, `phi_corte = 0.9`.

**Qué dice el documento.** Tabla 3.5.1-1 «Unit Weights», pág. **3-21** ✔: «Concrete — Normal Weight with f'c ≤ 5.0 ksi → **0.145 kcf**». C3.5.1: «the unit weight of reinforced concrete is generally taken as **0.005 kcf greater** than the unit weight of plain concrete». 0.145 + 0.005 = 0.150 kcf = 23.56 kN/m³.
La derivación es correcta y —esto es lo notable— **está atribuida a las dos piezas que la componen**, tabla y comentario, en vez de presentarse como un valor tabulado. Art. 5.5.4.2 confirma φ = 0.90 para secciones de concreto armado controladas por tracción y φ = 0.90 para corte y torsión en concreto de peso normal.

### `OK-09` — M 170M clasifica por D-load, no por altura: la afirmación negativa se sostiene

**Sev** OK · **Veredicto** CONFIRMA · **Documento** AASHTO M 170M
**Ubicación repo** src/criterios_adoptados.py:1063-1065
**Ubicación PDF** AASHTO M 170M-04, Tablas 1-5 y notas · EG-2013 pág. impresa 962

**Afirmación del repo.** «**M 170M clasifica por D-load (resistencia), no por altura** — no existe la tabla clase-a-altura que el criterio decía que iba a extraer de ella».

**Qué dice el documento.** Confirmado en la propia norma y, de rebote, en el EG-2013. Las Tablas 1 a 5 de M 170M son «Design Requirements for Class I…V Reinforced Concrete Pipe» y se organizan por diámetro interno, espesor de pared y área de armadura; la nota al pie define el criterio de aceptación como «D-load to produce a 0.3-mm crack» y «D-load to produce the ultimate load». No hay ninguna tabla de clase por altura de relleno.
El EG-2013 lo confirma desde fuera, en su num. 506.05 b): «la carga necesaria para producir una grieta de 0,3 mm o la carga última, no podrá ser inferior a la prescrita en la tabla que corresponda de la especificación AASHTO M-170M».

---

## 12. Estado de la fase de refutación

| Temario | Ítems | Cerrados | Pendientes | Primer pendiente |
|---|---|---|---|---|
| `temario_refutar_95.json` | 95 | 19 (`R95-001`…`R95-019`) | 76 | `R95-020` |
| `temario_refutar_48.json` | 48 | 20 (`R48-001`…`R48-020`) | 28 | `R48-021` |

El estado de cada ítem no es una suposición: sale del `journal.jsonl` de cada corrida
(`type=result` → cerrado, `type=failed` por límite de sesión → pendiente). Los cerrados
forman un **bloque contiguo desde el 001** en orden de lanzamiento, que es exactamente la
firma de un corte por créditos y no de fallos dispersos.

**Sobre la numeración.** En la ejecución original **no existía** una numeración `R95-NNN` /
`R48-NNN`: los refutadores se identificaban por el ID del hallazgo que refutaban (`H-05`,
`G-09`, `E-03`…) y un mismo hallazgo pudo tener más de un refutador. La numeración de los
dos temarios se asigna por **orden de lanzamiento ascendente**, tomado del timestamp del
primer mensaje de cada transcripción de agente. Ese orden es exacto y reproducible —los 95
y los 48 tienen timestamps únicos, sin un solo empate— y cada ítem conserva su `agent_id` y
su `spawn_ts` para que el mapeo se pueda auditar contra las transcripciones. No se inventó
ningún tramo.
