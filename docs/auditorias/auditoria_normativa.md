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

> **Limitación de este bloque, descubierta en la refutación (`R48-041`).** La memoria que
> se leyó sale de una corrida sobre `tests/ejemplo_puntos.csv` que **se detiene en la Fase 2**
> porque falta el dato externo `luz_m`. En esa corrida V4 y 7.A nunca se ejecutan, de modo
> que un criterio que solo se invoca ahí —`resguardo_HW_subrasante`, por ejemplo— no aparece
> en el bloque de criterios adoptados, y **eso no es un defecto**: `reporte_criterios(solo_usados=True)`
> hace exactamente lo que su docstring promete. Un hallazgo que se apoyaba en esa ausencia
> se refutó por este motivo (§13). Lo que quedó verificado del bloque G es lo que la memoria
> imprime hasta la Fase 2 más lo que sale de un render forzado; **lo que solo se imprime en
> Fase 5 no está cubierto por esta auditoría**. Cerrar esa parte exige un CSV con `luz_m`.

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
| `temario_refutar_95.json` | 95 | 59 | 36 | `R95-060` |
| `temario_refutar_48.json` | 48 | 48 | 0 | — (completo) |

El estado de cada ítem no es una suposición: los cerrados en la corrida original salen
del `journal.jsonl` (`type=result` → cerrado, `type=failed` por límite de sesión →
pendiente), y forman un **bloque contiguo desde el 001** en orden de lanzamiento, que es
la firma de un corte por créditos y no de fallos dispersos. Los cerrados posteriores
llevan además su veredicto, su evidencia y su razonamiento dentro del propio JSON.

**Sobre la numeración.** En la ejecución original **no existía** una numeración `R95-NNN` /
`R48-NNN`: los refutadores se identificaban por el ID del hallazgo que refutaban (`H-05`,
`G-09`, `E-03`…) y un mismo hallazgo pudo tener más de un refutador. La numeración de los
dos temarios se asigna por **orden de lanzamiento ascendente**, tomado del timestamp del
primer mensaje de cada transcripción de agente. Ese orden es exacto y reproducible —los 95
y los 48 tienen timestamps únicos, sin un solo empate— y cada ítem conserva su `agent_id` y
su `spawn_ts` para que el mapeo se pueda auditar contra las transcripciones. No se inventó
ningún tramo.

---

## 13. Refutación adversarial — resultados

Ítems reabiertos y cerrados tras el corte de sesión: **68**. Se sostienen **32** · ajustados **34** · refutados **2** · fuera de alcance **0**.

Cada ítem se re-verificó con instrucción de **derribar** el hallazgo: volver al PDF y al
código por cuenta propia y refutar por defecto ante cualquier duda razonable. `AJUSTADO`
significa que parte del cargo se sostiene y parte se cae; la severidad se mueve en
consecuencia.

| Ítem | Hallazgo | Resultado | Sev. final | Veredicto | Documento verificado | Razonamiento |
|---|---|---|---|---|---|---|
| `R48-021` | `G-09` | **AJUSTADO** | ALTA | CONTRADICE | AASHTO LRFD Bridge Design Specifications, 9th ed. (2020), Art. 12.6.6.3 «Minimum Cover» (pág. impresa 12-21) y Tabla 12.6.6.3-1 (pág. impresa 12-22) | Se sostiene: 12.0 in es un piso de un «shall not be less than», no un «típico», y el valor gobernante es Bc/8 o B'c/8 — para el tope de catálogo del propio proyecto (D_MAX concreto = 2.70 m, Bc ≈ 10.5 ft) da ≈ 15.7 in ≈ 0.40 m, de modo que la verificación corregiría el 0.30 m en vez de confirmarlo. La salvedad «salvo diseño especial de armadura» NO existe: busqué «special design» en todo el PDF y los únicos aciertos están en 12.8/12.9 (planchas estructurales), nada en 12.6.6.3 ni en C12.6.6.3. Además AASHTO mide la cobertura «from bottom of flexible pavement» e «including a well-compacted granular subbase and base course», mientras EG-2013 508.07 mide hasta la SUBRASANTE: son magnitudes distintas comparadas como si fueran la misma. AJUSTES a lo que afirmaba el auditor: (1) la Tabla está en pág. impresa 12-22 / PDFPAGE 1660, no en 12-21/1659 (ahí está solo el articulado); (2) el texto NO está impreso en memoria.txt:144 — memoria.txt tiene 0 coincidencias de «h_relleno» y su línea 144 habla de PGA_roca_B; solo aparece en memoria_perfil.txt:142 y en un render forzado de expediente. La severidad ALTA («argumento de conservadurismo que no se sostiene») se mantiene. |
| `R48-022` | `G-10` | **AJUSTADO** | MEDIA | CONFIRMA | FHWA HDS-5 3ª ed., abril 2012 (FHWA-HIF-12-026), Ec. (3.4b), pág. impresa 3.10 (PDFPAGE 92) y Ec. (DG 3.1), pág. impresa DG3.3 (PDFPAGE 296) | El número es el de la fuente primaria: contra el PDF el código CONFIRMA. El defecto real es interno y documental, no normativo. AJUSTES respecto del auditor: (1) la discrepancia SÍ está declarada fuera del comentario de código — docs/manifiesto_citas.md:274 dice «⚠ La hoja de ruta sigue diciendo 19.62 y debe corregirse», dato que el auditor no menciona y que desarma el «llega sin declarar»; (2) el pie de la memoria de perfil está en src/plantillas/memoria_perfil.html:319-321, no en :189-192 (esas líneas son la fila «estado_expediente»), y la discrepancia está en :124-126, no :123-126; (3) confirmé que 19.63 no aparece en ninguna memoria entregada (memoria.txt, memoria_perfil.txt, out/*.txt = 0 coincidencias) y solo emerge en un render forzado a Fase 4. Lo que sí es un defecto verificado y más agudo que el silencio: :825 atribuye a la hoja de ruta una ecuación que la hoja de ruta no escribe. Eso es «cita incompleta / referencia desfasada» = MEDIA; ALTA está inflada porque no hay número ni numeral equivocado. |
| `R48-023` | `G-12` | **AJUSTADO** | MEDIA | CONFIRMA | MTC, Manual de Carreteras: Suelos, Geología, Geotecnia y Pavimentos (abril 2014), num. 4.5.4 «Sub rasante» (pág. impresa 42) y num. 9.1(3) (págs. impresas 89-90) | La asimetría existe y la comprobé: de los dos [N→] solo uno entra en el bloque 0-bis y solo uno lleva la remisión. Pero la premisa que sostenía la severidad ALTA es falsa: la memoria imprime su propia leyenda de etiquetas — «N→ valor normativo aplicado por analogia, declarada» — encabezando la Sec. 3, de modo que la insignia no es una marca muda y la palabra «analogía» no aparece «solo» en el campo Justificación. Además el bloque está construido por definición para vacíos verificados (imprime «Registro completo de esa busqueda: docs/<vacio_verificado>») y resguardo_HW_subrasante NO es un vacío: el numeral existe, se cita con exactitud y su Justificación dice literalmente que 4.5.4 «regula la separacion frente al NIVEL FREATICO, no frente a un nivel transitorio de avenida». El veredicto contra el documento es CONFIRMA; queda un defecto de presentación real (la remisión ausente en la fila que sostiene el número), que es MEDIA, no ALTA. |
| `R48-024` | `HR-02` | **AJUSTADO** | MEDIA | CONTRADICE | Defecto interno del repo: Claude.md (150 líneas) frente a docs/hoja_de_ruta_alcantarillas_v8.md (911 líneas) y docs/auditoria_y_ruta_despliegue_v9.md:409-416, :483-486, :525. El documento que el ítem declara como fuente (HDS-5 2ª ed. SI, 1985) no interviene. | El desvío respecto de la fuente única existe y el remedio anunciado está sin ejecutar — eso lo comprobé línea por línea. AJUSTES: (1) Claude.md tiene 150 líneas, no 139, y sí contiene «auditoría» una vez (línea 141, con tilde: el auditor grepeó sin tilde), aunque nunca nombra el v9; (2) la regla de conflicto de Claude.md:8 está acotada a «tu conocimiento previo», no a una verificación externa contra un PDF que el propio repo guarda en normas/, de modo que el caso cae en un HUECO de gobierno y no contra una prohibición expresa; (3) el desvío no es silencioso: está declarado en constantes_normativas.py:124-126, en M4_control.py:122-124 y en docs/manifiesto_citas.md:274; (4) el DOCUMENTO FUENTE del ítem está mal asignado: HDS-5 2ª ed. SI no contiene ni 19.62 ni 19.63 (0 coincidencias); la cifra es de la 3ª ed. Añado un defecto que el auditor no vio y que es exactamente MEDIA: el propio comentario :124-125 cita las líneas «432, 436, 790 y 901» de la hoja de ruta cuando las reales son 436, 440, 797 y 908. Con el desvío declarado en tres sitios y el riesgo residual concentrado en el Anexo B, ALTA está inflada: MEDIA. |
| `R48-025` | `HR-03` | **AJUSTADO** | ALTA | CONTRADICE | FHWA HDS-5 3ª ed., abril 2012 (FHWA-HIF-12-026), Apéndice B, pág. impresa B.1 (PDFPAGE 203), Ec. (B.3); Ec. (3.4b) en pág. impresa 3.10 (PDFPAGE 92) | Se sostiene: la fuente remite explícitamente a la reordenación de (B.3), y esa reordenación mete 2g dentro de KU; en SI, con Kn = 1, KU es 2g y g SÍ interviene sola, justo el caso que documenta K_FRICCION_SI. Llamar «coincidencia numérica sin respaldo en la fuente» a 19.62 = 2×9.81 es afirmar un vacío que la propia norma llena, y el proyecto lo fijó en un test que ahora protege el razonamiento equivocado. AJUSTES respecto del auditor: (1) HDS-5 publica la (B.3) SOLO en unidades inglesas (coeficiente 1.486); no publica una forma SI, así que decir «el HDS-5 SI publica la derivación» es impreciso — la derivación publicada es la inglesa, donde g va dividida por 1.486² y no interviene sola; (2) el «2 × 9.815» del auditor no está en el documento: HDS-5 escribe «g is the acceleration due to gravity, 32.2 ft/s2 (9.8 m/s2)» (PDFPAGE 203 y 91), de modo que 9.815 es una retrocuenta, no una cifra de la fuente. Severidad ALTA se mantiene (argumento técnico que no se sostiene, replicado en el manifiesto y blindado por un test); no sube a CRÍTICA porque ni el número ni ningún numeral están mal, y comprobé que el razonamiento erróneo no llega a ninguna memoria (0 coincidencias de «coincidencia numerica» en los cuatro renders). |
| `R48-026` | `HR-05` | **AJUSTADO** | MEDIA | CONTRADICE | docs/hoja_de_ruta_alcantarillas_v8.md, Anexo B - Constantes normativas para el script (bloque ```python, lineas 743-872). Verificacion interna del repo, sin PDF detras. | La afirmacion "copiado literalmente" es falsa como enunciado global y lo comprobe mecanicamente: hay 27 nombres de diferencia y un valor cambiado. Se sostiene el defecto, pero no en grado ALTA: no hay numero normativo mal transcrito, ni numeral inexistente, ni atribucion a documento equivocado -- ninguna cita a un PDF se ve afectada, y el unico valor divergente lleva marca explicita de discrepancia abierta doce lineas mas abajo. Lo que queda es una declaracion de fidelidad incompleta en la primera linea del archivo, que el propio archivo desmiente en tres sitios: encaja en MEDIA ("cita incompleta, ambiguedad no declarada"). Grep de "copiado literalmente" y "Anexo B" en manifiesto_citas.md, auditoria_y_ruta_despliegue_v9.md y Claude.md no devuelve nada: fuera del propio archivo la frase no esta matizada en ningun lado. |
| `R48-027` | `HR-06` | **AJUSTADO** | BAJA | CONTRADICE | docs/hoja_de_ruta_alcantarillas_v8.md:495 y :751 (Anexo B); contrastado con MTC Manual de Hidrologia, Hidraulica y Drenaje, num. 4.1.1.3.7 c), pag. impresa 80 (PDFPAGE 83) y pag. impresa 111 (PDFPAGE 114). | Los hechos que alega el auditor son ciertos: la hoja de ruta escribe 9.8 y nunca 9.81, y el desdoblamiento mueve resultados. Lo que se cae es que sea un cambio no declarado: lo prescribe literalmente docs/auditoria_y_ruta_despliegue_v9.md §2.3 ("Lo correcto es acotarlo: G_LAUSHEY = 9.8 con su numeral (4.1.1.3.7 c), usado solo en M6, y una constante fisica G = 9.81 para todo lo demas"), lo declara Claude.md:55-67 como regla de arquitectura del proyecto, lo explica el docstring entero de constantes_fisicas.py y lo registra manifiesto_citas.md:22-26 avisando que recalculo los CP-8. Son cuatro declaraciones, no un silencio. Ademas la premisa de que el Anexo B fija una gravedad general se debilita: ese G = 9.8 vive en el bloque "Manual de Hidrologia" pegado a LAUSHEY_K, y el Anexo B se declara "solo constantes [N] con numeral verificado", categoria que una gravedad universal no cumple. Cambia respecto del auditor: no es ALTA sino BAJA, y el residuo es unico -- que la hoja de ruta v8 no se actualizo y que constantes_normativas.py no le puso la misma marca "DISCREPANCIA ABIERTA" que al 19.63. |
| `R48-028` | `HR-07` | **AJUSTADO** | MEDIA | CONTRADICE | docs/hoja_de_ruta_alcantarillas_v8.md:83, :87, :150 y :154 (verificacion interna del repo; ningun PDF de por medio). | La colision de vocabulario es real y la comprobe yo mismo: "num. 83/87/150" son numeros de linea impresos con el mismo prefijo que los numerales normativos, sin que datos_sitio.py declare la convencion en ninguna parte de su docstring, y viajan a la memoria dentro del campo Trazabilidad. Pero la escala pone esto en MEDIA, no en ALTA: es exactamente "ambiguedad de vocabulario no declarada" mas una "referencia archivo:linea desfasada" (el num. 150 apunta cuatro lineas antes de la frase del terraplen que dice citar), no una atribucion a documento equivocado ni una cita normativa falsa -- el codigo dice "de la hoja de ruta" en las tres ocurrencias, de modo que el documento apuntado es el correcto. Se ajusta la severidad a MEDIA y se corrige la linea 152 -> 154. |
| `R48-029` | `HR-08` | **AJUSTADO** | MEDIA | CONTRADICE | docs/manifiesto_citas.md §11.a (lineas 370-383) y docs/auditoria_y_ruta_despliegue_v9.md, item (8) del prompt de cierre (lineas 509-518). Verificacion interna del repo. | El defecto existe, pero su alcance es mucho menor que "M11 no distingue los NUMERAL_*". El item (8) de v9 exigia separar CUATRO constantes nombradas -- NUMERAL_V4, NUMERAL_9_1, NUMERAL_8_1 y NUMERAL_FASE_10 -- y las cuatro estan hechas; las demas estan inventariadas una a una en manifiesto_citas.md §11.a bajo el rotulo "Varios NUMERAL_* de modulo parecen numerales normativos y son secciones de la hoja de ruta". De los cinco senalados, tres son codigo muerto y uno solo aparece en un mensaje de excepcion: el unico que puede llegar a la memoria es NUMERAL_V6 = "3.1", y hoy esta latente porque ningun punto alcanza la Fase 5. Queda un caso real -- un "3.1" impreso en la columna "Numeral" con la celda de umbral rotulada "[N] constante normativa" -- que es "ambiguedad de vocabulario no declarada" en el entregable: MEDIA, no ALTA. Cambia respecto del auditor: no es un patron sistemico pendiente sino un unico residuo latente sobre un trabajo que cumplio el alcance que se le pidio. |
| `R48-030` | `HR-10` | **SE SOSTIENE** | ALTA | CONTRADICE | docs/hoja_de_ruta_alcantarillas_v8.md, seis sitios: :60 (§0.1), :76 (§0.3), :351 (§3.4), :455 (Fase 5, V3), :679 (Tablero 1, fila 1.3) y :724 (Anexo A). El WSDOT Hydraulics Manual M 23-03.12 NO esta en normas/, asi que el valor 4.6 m/s en si queda NO VERIFICABLE. | Lo comprobe yo mismo y se sostiene entero: el codigo cierra el pendiente 1.3 con una fuente que la fuente de verdad no nombra en ninguno de sus seis pronunciamientos, y M11 vuelca esa misma fila abierta al entregable, de modo que una memoria completa afirmaria a la vez "valores por extraer (PPI/FHWA)" y "4.6 m/s (WSDOT)". A diferencia del caso de la gravedad, aqui no hay autorizacion: v9 no menciona el tema, y Claude.md:9-12 obliga a lo contrario ("Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes... valor=None, etiqueta [A] y ... deten el calculo"). La unica declaracion es manifiesto_citas.md §10-bis y :400-401 ("cita cerrada - WSDOT ... Antes: PPI/FHWA"), y el propio codigo (M5:121-124) reconoce que el manifiesto "no va al expediente". Correccion menor al auditor: sus cinco primeras lineas estan desfasadas -- son 60, 76, 351, 455 y 679, no 64, 74, 338, 448 y 690 (solo 724 coincide); el contenido citado es literal. Se mantiene ALTA: atribucion a un documento que la fuente de verdad no reconoce, con contradiccion estructural en el entregable, y con el valor mismo no verificable por ausencia del WSDOT en normas/. |
| `R48-031` | `C-01` | **AJUSTADO** | MEDIA | CONTRADICE | AASHTO LRFD Bridge Design Specifications, 9th ed. 2020, Tabla 3.4.1-2, pag. impresa 3-18 (pdfpage 72), leida en el PDF original con Read | Cae el nucleo del hallazgo: el auditor afirma que 'el par (1.35, 0.90) no corresponde a NINGUNA fila', pero la fila 'Rigid Frames' es exactamente 1.35/0.90 -- y el propio auditor la lista en su evidencia, contradiciendose. Un cajon de concreto vaciado in situ es precisamente un rigid frame, de modo que el par transcrito es una fila real de la tabla y no una mezcla: no hay numero mal transcrito, luego no es CRITICA. Sobrevive un defecto mas estrecho y verificado: el cabezal de M9 es un muro de contencion/estribo, cuya fila da minimo 1.00, y la frase de CA:1379-1380 ('EV minimo 0.90, no 1.00') es falsa justamente para esa fila, que es la unica del bloque EV con minimo 1.00. El efecto hoy es conservador (0.90 < 1.00 reduce el termino estabilizante en volteo y en V7), y el criterio no matiza en ninguna parte el EV por tipo de elemento, aunque si lo hace para EH activo vs. en reposo. |
| `R48-032` | `C-02` | **SE SOSTIENE** | ALTA | CONTRADICE | AASHTO LRFD 9th ed. 2020, Art. 12.6.6.3 y Tabla 12.6.6.3-1, pags. impresas 12-21/12-22 (pdfpage 1659-1660), leidas en el PDF original | Comprobado: la cobertura minima de AASHTO no es un escalar por material sino una formula dependiente del diametro, y para concreto reforzado Bc/8 supera las 12.0 in en cuanto Bc > 8 ft = 2.44 m. Con D interior 2.70 m el exterior pasa de 3.0 m, luego Bc/8 ~ 0.38-0.40 m > 0.30 m adoptado: la analogia SI puede quedar del lado inseguro, que es exactamente lo que la frase declara imposible. El punto (i) del auditor es mas debil de lo que suena -- el repo nunca atribuye el 0.30 m a AASHTO, lo toma de EG-2013 Subseccion 508.07 para HDPE -- pero refuerza la falta de monotonia, porque AASHTO pide al termoplastico ID/2 >= 24 in bajo via pavimentada. Para TMC el hallazgo casi no muerde: con el tope de catalogo 2.10 m, S/8 = 10.3 in queda bajo el piso de 12.0 in = 0.3048 m, apenas 5 mm sobre el adoptado. Encaja literalmente en la severidad ALTA ('argumento de conservadurismo que no se sostiene'), y no sube a CRITICA porque el propio criterio acota el alcance a perfil ('NO sustituye la verificacion estructural por material, que es de expediente y sigue pendiente'). |
| `R48-033` | `C-03` | **AJUSTADO** | ALTA | CONTRADICE | AASHTO LRFD 9th ed. 2020, Art. 12.6.6.3 y Tabla 12.6.6.3-1, pags. impresas 12-21/12-22 (pdfpage 1659-1660), leidas en el PDF original | Se sostiene lo esencial: busque en todo el Art. 12.6.6.3, en su comentario C12.6.6.3 y en el resto de la Seccion 12 (los unicos 'special design' de la seccion estan en 12.8, placas estructurales de gran luz), y no existe ninguna clausula 'salvo diseno especial de armadura' para la cobertura del concreto reforzado; la excepcion real de la norma es otra (sin cobertura de suelo, disenar el techo del cajon para carga vehicular directa). Se ajusta un extremo de la acusacion: el '1.0 ft (~0.305 m)' NO es inventado, es el piso literal '> 12.0 in.' de la fila de concreto bajo area no pavimentada o pavimento flexible, de modo que la paráfrasis solo es correcta mientras Bc <= 8 ft. Lo que falla es la excepcion inexistente, el borrado de la dependencia de Bc -- que es justamente lo que hace caer el argumento de C-02 -- y el prejuzgar el resultado ('la verificacion deberia confirmarla, no corregirla') sobre una verificacion diferida al expediente. Ademas la nota omite que bajo pavimento rigido AASHTO admite 9.0 in = 0.229 m. Se mantiene ALTA por atribuir a un articulo nominado una clausula que no contiene; no sube a CRITICA porque no va entrecomillada como cita literal y el numero citado si existe en la tabla. |
| `R48-034` | `C-04` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA HDS-5 3a ed. (FHWA-HIF-12-026, abril 2012), Sec. 2.2.5 'Allowable Headwater', apartado 'd. Agency Constraints', pag. impresa 2.10 (pdfpage 72), leida en el PDF original | La pagina esta equivocada y lo verifique en el PDF original, no solo en el texto extraido: el pasaje esta en 2.9-2.10 y 2.14 es seguridad vial. Descarte que fuera confusion de edicion: la frase 'commonly ranges from 1.0 to 1.5' no aparece en ninguna parte de la 2a ed. SI (HDS5_SI), asi que el numero de pagina no viene de otra edicion; tampoco es confusion impresa/PDF, porque 2.14 corresponde a pdfpage 76 y alli no hay nada del tema. Agrava que el campo se declare 'CITA CERRADA por verificacion externa contra el documento', que es precisamente lo que la pagina desmiente, y que el error este duplicado en el manifiesto. El segundo reproche del auditor (naturaleza de la fuente) es mas interpretativo y solo lo sostengo en parte: HDS-5 describe limites que imponen las agencias, no un rango de diseno propio, pero 'commonly ranges' admite una lectura laxa como 'diseno corriente'. Severidad ALTA por la regla explicita 'pagina equivocada'. |
| `R48-035` | `C-05` | **AJUSTADO** | MEDIA | CONTRADICE | Interno al repo: src/criterios_adoptados.py:886-907 (HW_D_max) y :957-980 (remanso_derecho_via); src/modulos/M5_verificaciones.py:377-417; scratchpad/informe.json y memoria.txt | Se sostiene el pilar principal y lo verifique linea por linea: se adopta el extremo menos restrictivo del rango apoyandose en una compensacion -- V5 -- que el propio archivo declara bloqueada para todo punto por un criterio en None, y la justificacion de HW_D_max no lo advierte. Cae el segundo pilar: el auditor no leyo las lineas 895-900 del mismo campo, donde el repo dice expresamente que (1.2, 1.5) es un subrango deliberado y advierte que no se confunda con HDS-5; la acusacion de que la frase del manifiesto es 'normativamente enganosa' no se sostiene contra una salvedad escrita en el propio criterio. Bajo de ALTA a MEDIA porque no se mueve ningun numero normativo, nada esta oculto (el None, su comentario 'bloquea V5 para todo punto', informe.json y la memoria lo publican) y el defecto es de redaccion/coherencia: invocar como vigente un control que el expediente ya declara detenido, en un expediente que declara globalmente que no cierra. |
| `R48-036` | `C-06` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA HDS-5 3a ed. (FHWA-HIF-12-026), Cap. III, pags. impresas 3.12 (pdfpage 94), 3.24 (pdfpage 106) y 3.43 (pdfpage 125); Tabla C.2, pag. C.6 (pdfpage 216) | Se sostiene: el repo dice lo que se le atribuye y HDS-5 publica un piso numerico de aplicabilidad que ni el criterio ni M4 recogen, de modo que control_salida() aplica la geometria llena sin condicion (y su propio docstring admite que HW puede salir negativo). La frase "el caso de control de salida por definicion" ademas contradice al documento: HDS-5 titula la Tabla C.2 "Outlet Control, Full or Partly Full Entrance Head Loss" (pag. C.6) y dice "Backwater calculations may be required for the partly full flow conditions" (pag. 3.12). Mantengo ALTA y no subo a CRITICA porque no hay numero [N] mal transcrito ni numeral inexistente, y el vacio que el repo declara es el de la hoja de ruta ("Sec. 4.3 escribe la ecuacion pero NO dice a que seccion pertenecen V y R"), que es cierto. Correccion al auditor: las dos frases que atribuye a la "pag. 3.13" estan en la pag. impresa 3.12 (pdfpage 94); su rango 3.12-3.13 las cubre. |
| `R48-037` | `C-07` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA HDS-5 3a ed. (FHWA-HIF-12-026), Apendice C: Tabla C.2 en pag. impresa C.6 (pdfpage 216); pag. C.1 (pdfpage 211) y pag. C.2 (pdfpage 212) | Se sostiene tal cual: el valor 0.5 y la fila son correctos, la pagina no. La pag. C.2 no contiene la Tabla C.2 sino indice de charts de box culvert; el "C.2" que aparece en la pag. C.1 es el NUMERO DE TABLA en la lista de tablas de referencia, que es el origen probable de la confusion. Agravante verificado: el propio campo declara la cita "CERRADA por verificacion externa contra el documento" diciendo que la pagina era justamente lo que faltaba. Anado un defecto que el auditor no marco: la fila entrecomillada 'square edge with headwall' no es literal de la Tabla C.2 (alli se lee "Headwall or headwall and wingwalls" + "Square-edge"). Severidad ALTA (pagina equivocada) confirmada. Correccion menor de ubicacion: el manifiesto lo repite en la linea 277, no en la 279. |
| `R48-038` | `C-08` | **SE SOSTIENE** | ALTA | CONTRADICE | MTC EG-2013 (Revisada y Corregida a Junio 2013), Subseccion 508.07, pag. impresa 984 (pdfpage 992); pag. impresa 982 = pdfpage 990 | Se sostiene: la transcripcion es literal palabra por palabra (incluida la coma decimal "0,30 m") pero la pagina esta desfasada dos unidades y se repite en cada sitio donde aparece la cita, incluido el numero [N] de constantes_normativas. No es diferencia de edicion: el propio expediente cita 506.02 en la pag. 959 y esa SI cuadra con este mismo PDF (pdfpage 967, encabezado 959), asi que la base de paginacion es la misma y el error es del repo. Severidad ALTA (pagina equivocada) sostenida; no sube a CRITICA porque el valor 0.30 m, el numeral 508.07 y la frase son exactos. Correcciones de ubicacion al auditor: la constante esta en constantes_normativas.py:177 (no 176) y el bloque del manifiesto en las lineas 254/607/609. |
| `R48-039` | `C-09` | **SE SOSTIENE** | ALTA | CONTRADICE | MTC EG-2013, Subsecciones 507.05 y 507.06 en pag. impresa 973 (pdfpage 981) y 507.08 en pag. impresa 974 (pdfpage 982); 506.02 en pag. impresa 959 (pdfpage 967) | Se sostiene: la sustancia de las tres remisiones a ASTM A-807 es correcta, pero las paginas estan 4-5 unidades atras, y lo que hay en las paginas citadas agrava el error, porque 969-970 remiten a OTRAS normas de producto (ASTM A-929, AASHTO M-36 / ASTM A-760): un revisor que abra la pagina citada encuentra un juego de normas distinto. Verifique tambien la otra mitad del mismo parrafo y CONFIRMA: 506.02 "Tuberia" esta en la pag. impresa 959 (pdfpage 967) y dice "...establecidos en la especificacion AASHTO M-170M". Severidad ALTA (pagina equivocada) sostenida, y es carga util porque la cita sostiene una afirmacion negativa (el vacio verificado para concreto y TMC). Correccion de ubicacion al auditor: NO esta "reproducido en scratchpad/memoria.txt:144" -- memoria.txt no contiene la cadena "969" en ninguna linea; solo memoria_perfil.txt:142 la reproduce. |
| `R48-040` | `C-10` | **AJUSTADO** | MEDIA | NO VERIFICABLE | MTC Manual de Suelos, Geologia, Geotecnia y Pavimentos (abril 2014), num. 4.5.4 "Sub rasante", pag. impresa 42 (pdfpage 43) y num. 9.1(3), pag. impresa 89 (pdfpage 90) | Se ajusta a la baja. La premisa documental del auditor es correcta y la verifique: el Manual regula napa freatica y no dice nada sobre niveles de avenida, de modo que la frase "la analogia es conservadora" no es comprobable contra el documento -- el Manual ni la respalda ni la desmiente. Pero tres cosas rebajan el hallazgo. (1) El repo NO presenta esto como cita directa: lo etiqueta [N->], nombra el fenomeno correcto ("regula la separacion frente al NIVEL FREATICO, no frente a un nivel transitorio de avenida"), exige declararlo en la memoria, y M7:25-26 lo repite ("aplicada al HW POR ANALOGIA"); el auditor no peso esa salvedad. (2) El propio auditor concede que en elevacion la extension exige mas. (3) Su tercer apoyo -- "el resguardo es HOY el UNICO control entre el HW y la rasante" -- lo desmiente el codigo: M5_verificaciones.py:46-50 dice que mientras 'remanso_derecho_via' y 'TR_evento_extremo' sigan vacios, verificar() y MD.disenar_punto/disenar_lote "se detiene con CriterioPendienteError para CUALQUIER punto", asi que no hay diseno entregable apoyado solo en el resguardo. Lo que queda es MEDIA, ambiguedad de vocabulario no declarada: "conservadora" se afirma sin decir en que sentido (mas elevacion exigida frente a lado seguro del modo de falla) y el criterio no registra que 0.60/0.80/1.00/1.20 m estan calibrados para ascenso capilar de un freatico permanente. Correccion de ubicacion: en M7 se aplica en las lineas 332-338, no en la 82, que es docstring. |
| `R48-041` | `C-11` | **REFUTADO** | OK | CONFIRMA | Interno al repo: src/criterios_adoptados.py:908-918, src/modulos/M5_verificaciones.py:359, src/modulos/M7_geometria.py:331; memorias generadas en scratchpad/ | El auditor midio la memoria de una corrida que se detiene en Fase 2 por un dato externo ausente (`luz_m`), no un defecto del codigo. En esa corrida V4 y 7.A nunca se ejecutan, el resguardo nunca se aplica a ningun numero, y `reporte_criterios(solo_usados=True)` — cuyo docstring declara "lista unicamente los criterios que el calculo invoco" — hace exactamente lo que promete al omitirlo. Declarar una analogia que no se aplico seria ruido, no transparencia. La prueba empirica esta en el propio scratchpad: mem_forzada_exp.txt, mem_forzada_perfil.txt y mem_forzada.html, generadas forzando el calculo mas alla de Fase 2, contienen el criterio con su etiqueta N→ y su justificacion completa. No hay analogia no declarada al revisor: hay una corrida incompleta que la memoria misma declara como bloqueo. |
| `R48-042` | `C-12` | **AJUSTADO** | MEDIA | CONTRADICE | Interno al repo (src/criterios_adoptados.py:386-472 y :1988) contrastado con MTC Manual de Puentes, Tablas 2.4.3.11.2.1.1-1 (pag. impresa 122 / PDFPAGE 123) y 2.4.3.11.2.1.2-1 (pag. impresa 123 / PDFPAGE 124) | AJUSTADO. Lo que verifique y se sostiene: el criterio `clase_sitio` esta desconectado del calculo — su unico llamador vive en el bloque de demostracion `__main__` — y por eso jamas aparece en el bloque DECLARACION DE CRITERIOS ADOPTADOS de ninguna memoria, ni siquiera forzada; el F_pga que se apoya en el sí aparece y su justificacion impresa (memoria.txt:167) enumera "1.0 para clases C y D, 0.9 para E" sin nombrar la F, que es la clase declarada y para la que la tabla da "*". Lo que cae: la afirmacion del auditor de que "la adopcion mas grave del expediente no aparece en la memoria" es materialmente falsa. El Tablero 1 item 1.1 de memoria.html declara al revisor, con esas palabras, que el sitio es Clase F, que AASHTO exige el estudio de respuesta de sitio de forma incondicional y que el uso de factores tabulados pasa a adopcion [A]. Queda un defecto de cableado y de presentacion (falta la ficha del criterio con su `reemplazado_por` de 30 m y su `verificacion_pendiente`, y la justificacion de F_pga omite la clase del proyecto), no una adopcion oculta: MEDIA, no ALTA. |
| `R48-043` | `C-13` | **AJUSTADO** | MEDIA | CONTRADICE | AASHTO LRFD 9a ed. 2020, Tabla 3.10.3.1-1 "Site Class Definitions", pag. impresa 3-102 (PDFPAGE 156) y Tabla C3.10.3.1-1 (3-103, PDFPAGE 157); MTC Manual de Puentes, Tabla 2.4.3.11.2.1.1-1, pag. impresa 122 (PDFPAGE 123) | AJUSTADO, y por la mitad. Se cae la parte (b): la afirmacion negativa del repo esta acotada a la DISPENSA POR PERIODO CORTO y es exacta — la busque yo mismo en 3.10.3.1, C3.10.3.1 y la tabla, y no existe; no registrar un hallazgo colateral no contradice lo que el repo dice. Se sostiene, rebajada, la parte (a): el salto "licuable → Clase F" no esta en ninguno de los dos documentos que el criterio invoca, y el comentario AASHTO habla de "the three categories", de modo que la lista no se lee tan abierta como el "such as" sugiere. Atenuantes que el auditor no leyo, en el mismo archivo: el repo NO atribuye esa clasificacion a AASHTO — la fuente dice "NINGUNA autoriza la adopcion" y la etiqueta es [A] —, y CA:347-385 (`PERFIL_SUELO_PRESUNTO`, [S], "suelos potencialmente licuables", E.030 Art. 14.6) declara expresamente que es "la presuncion geotecnica sobre la que se apoyan tanto 'clase_sitio' como la hipotesis de licuefaccion", con `reemplazado_por` = SPT pendiente. No es cita falsa ni autorizacion inventada: es un paso inferencial con la fuente sin nombrar, agravado por la nota Exceptions (sin dato geotecnico las clases E o F no se suponen). MEDIA, no ALTA. |
| `R48-044` | `C-14` | **SE SOSTIENE** | ALTA | CONTRADICE | AASHTO M 170M-04 / ASTM C 76M-02, Sec. 1 SCOPE, Note 1 (M170M_OCR PDFPAGE 1); AASHTO M 36, clausula 1.3 y Note 9 (M36 PDFPAGE 2 y tabla 7); ASTM A760/A760M-10, clausula 1.4 (A760_OCR PDFPAGE 1) | SE SOSTIENE en ALTA. Comprobe las tres exclusiones de alcance en los OCR propios y las erratas son tipograficas ("docs not", "ficld", "éarth", "13" por "1.3"), no cambian el sentido. La contradiccion interna es aun mas literal que lo alegado: en docs/manifiesto_citas.md la fila 322 declara `clases_producto_por_relleno` "tabla clase/calibre × diámetro × rango de altura de relleno, **sin extraer**" y la fila 324, dos lineas mas abajo en la MISMA tabla, declara `h_relleno_min_concreto_tmc` "**cita cerrada en negativo**... Ya no es 'falta extraer': no hay nada que extraer", sobre las mismas tres normas. Y el defecto llega al revisor: memoria.html imprime el criterio en la tabla de vacios sin valor con "Qué lo resuelve = Tabla de clase/calibre por altura de relleno de la norma de producto, extraida y transcrita con su numeral" — una tarea que las normas nombradas excluyen de su alcance. Es atribucion a documento equivocado y un vacio verificado convertido en pendiente ficticia: ALTA se mantiene (no llega a CRITICA porque el valor es None y no endurece ningun numero). |
| `R48-045` | `C-16` | **AJUSTADO** | BAJA | CONFIRMA | Interno al repo: src/criterios_adoptados.py:37-45 (definicion de etiquetas), :749-773 (v_max_hdpe / v_max_tmc); docs/manifiesto_citas.md §10-bis (lineas 347-361) y §12 (lineas 421-434) | AJUSTADO a BAJA. Cae la consecuencia (a) del auditor, que era el nervio de la severidad: al ir como [C], `v_max_tmc` NO escapa del chequeo de citas — es una fila con numeral y pagina en §10-bis, precisamente la revision de la que §12 excluye a los [A]; reetiquetarlo lo habria SACADO de ahi. Cae tambien (b) como consecuencia medible: ninguna guardia del archivo exige `sensibilidad` a un [A] (`_verificar_sensibilidad` solo valida el rango si existe) y 16 de los 30 [A] no la declaran, asi que el cambio de etiqueta no produciria ningun analisis nuevo. Y la analogia con `clase_sitio` no transfiere: alli el repo dijo "no hay fuente que cubra nada -- la que se citaba no dice lo que se le hacia decir" (fuente muda), mientras que aqui la fuente sí entrega el numero (15 ft/s = 4.6 m/s, misma tabla y misma pagina que el HDPE) y solo difiere en la consecuencia. Queda un residuo real y menor: un techo que el proyectista endurece respecto del disparador de la fuente, sin rango de sensibilidad declarado — pero ya confesado en la propia fuente y en §10-bis, sin numero mal transcrito y sin ocultamiento al revisor. Es taxonomico/redaccional: BAJA. |
| `R48-046` | `C-17` | **AJUSTADO** | ALTA | CONTRADICE | AASHTO LRFD Bridge Design Specifications, 9th ed. 2020, Art. 5.10.1 y Tabla 5.10.1-1, pag. impresa 5-169 (PDFPAGE 528); Art. 5.10.1 en pag. 5-167 (PDFPAGE 526) | El nucleo del hallazgo se sostiene: la pagina 5-169 es correcta pero el numero no esta ahi -- la fila Coastal da 3.0 in = 76.2 mm, no 75.0 mm, y la tabla tiene un segundo eje (Categoria A/B/C) que el criterio omite. AJUSTO dos cosas del auditor. (1) Su inversion hipotetica no es real: la eleccion de Categoria A si esta escrita en el repo, en docs/auditoria_y_ruta_despliegue_v9.md:618 ("75 mm contra el suelo (Cat. A)") y :691 ("Categoria A (acero convencional)"), asi que el defecto es de trazabilidad del campo `fuente`, no un riesgo de que gobierne E.060. (2) Anado dos defectos que el auditor no vio y que van en la misma direccion insegura: el Art. 5.10.1 obliga a modificar el valor de tabla por el factor W/CM (0.8/1.0/1.2) y el criterio no lo declara -- con W/CM >= 0.50 el requisito seria 3.6 in = 91.4 mm; y la afirmacion de la justificacion "AASHTO LRFD Tabla 5.10.1-1 no organiza el recubrimiento por diametro de barra" es falsa como enunciado general, porque el bloque "Limited Exposure" si se divide en "Up to No. 11 bar" / "No. 14 and No. 18 bars". Severidad ALTA (no CRITICA): la etiqueta es [C], no [N], y los 1.2 mm no invierten cual norma gobierna en los tres casos. |
| `R48-047` | `C-18` | **AJUSTADO** | ALTA | CONTRADICE | AASHTO LRFD 9th ed. 2020: C5.1 pag. 5-1 (PDFPAGE 360); Art. 5.5.4.2 pags. 5-29 a 5-32 (PDFPAGE 388-391); Eq. 5.7.3.3-3 pag. 5-67 (PDFPAGE 426); Eqs. 5.7.3.4.2-1/-2/-3 pag. 5-70 (PDFPAGE 429) | Los dos defectos de fondo se comprueban con el PDF en la mano y se sostienen: AASHTO da DOS expresiones de beta y el criterio transcribe solo la de secciones CON estribos minimos -- la rama que da mayor Vc -- sin declarar la condicion, y el coeficiente 0.0316 es el factor psi->ksi del propio AASHTO, guardado bajo la clave "Vc_kN" dentro de un modulo cuyo docstring declara "Unidades: SI". AJUSTO tres puntos. (1) Cae la queja de pagina sobre 5.5.4.2: el articulo se extiende de 5-29 a 5-32 y la PDFPAGE 391 (pag. 5-32) todavia lleva su ultimo parrafo antes de "5.5.4.3-Stability", asi que la cita es imprecisa, no equivocada. (2) Se confirma en cambio que "5-243" es pagina equivocada: la PDFPAGE 602 (pag. 5-243) trata de apoyos de lanzamiento del Art. 5.12.5, nada que ver con 5.7.2.8 (5-64), 5.7.3.3 (5-67) ni 5.7.3.4.2 (5-70). (3) Ambos defectos de fondo YA estan registrados dentro del propio repo, en docs/auditorias/auditoria_matematica.md:57 (O9, MEDIA: "trampa de unidades latente... Falta ademas la condicion de aplicabilidad de beta"), y `M9.diseno_flexion_corte` (M9_cabezal.py:1436-1464) lanza NotImplementedError, de modo que hoy no mueve ningun numero. Mantengo ALTA porque quedan una pagina equivocada en el campo `fuente` y la omision de la rama menos favorable de una ecuacion de resistencia, no por su efecto en la corrida actual. |
| `R48-048` | `C-19` | **SE SOSTIENE** | ALTA | CONTRADICE | Verificacion INTERNA del repo (no hay PDF): docs/manifiesto_citas.md seccion 8, linea 296, contra src/criterios_adoptados.py y tests/test_manifiesto_citas.py | Comprobe las cinco piezas yo mismo y todas dan la razon al auditor. El manifiesto sigue inventariando un criterio inexistente con un ancla que aterriza en el campo `fuente` de otro criterio (`ke_entrada`), y la seccion 8 demuestra tener convencion para retirar filas -- la de `clase_sitio` esta tachada con "CITA FALSA - RETIRADA" -- que aqui no se aplico: la fila esta viva. El agujero del test es estructural tal como se describe: sin simbolo, la referencia cae en `prosa` y solo se comprueba que exista el archivo, que la linea este dentro del rango y que no este vacia. Matizo sin bajar severidad que la excepcion de prosa no queda del todo sin vigilancia agregada (`test_las_referencias_de_prosa_no_crecen_sin_control`, cupo 90, y `test_la_cobertura_verificable_no_se_degrada`, piso 0.65), pero ninguno de los dos mira fila por fila y una sola referencia degradada pasa por debajo de ambos. Anado que el preambulo de la seccion 8 ("Ninguna cita a AASHTO LRFD lleva hoy un valor numerico transcrito: todas las tablas quedaron sin extraer") tambien es falso hoy, y que este mismo defecto ya figura sin corregir en el registro interno docs/auditorias/auditoria_normativa.md:117 (MAN-03, ALTA, CONTRADICE). ALTA se sostiene: no es una linea desfasada (MEDIA), es un item [C] anunciado al revisor que no existe. |
| `R95-020` | `H-05` | **SE SOSTIENE** | CRITICA | CONTRADICE | MTC Manual de Puentes (2018), num. 2.4.3.3.2 (pag. impresa 109), num. 2.4.3.11.1 (121), Tabla 2.4.5.3.1-2 (143), num. 2.8.1.3A.6.2 (280), num. 2.11 (505); indice general pags. 36-38 | Se sostiene y la severidad es la correcta: el repo afirma un vacio que la norma llena, que es justamente el supuesto CRITICO del briefing. El Manual regula conductos enterrados en numerales propios y varios de ellos dependen de la altura de relleno (IM en funcion de D_E; el corte de losas de alcantarilla cajon segun tenga mas o menos de 2.0 ft de relleno, pag. impresa 280). Encontre ademas un error que el auditor no vio y que agrava el hallazgo: la premisa del indice es doblemente falsa. Abri el PDF en la pagina 506 = impresa 505 y el num. 2.11 no es «Muros de Contencion y Estribos» sino «2.11 DISENO DE BARRERAS DE SONIDO (15 AASHTO)»; y la numeracion 2.x del Manual no sigue a la de AASHTO (2.8 Cimentaciones = AASHTO 10, 2.9 Superestructuras = AASHTO 5), de modo que «el indice salta de 2.11 a 2.12» no prueba nada sobre la Seccion 12. Atenuantes que no cambian el veredicto: el repo si matiza dos lineas mas abajo (CA:1129-1135) la Tabla 2.9.1.5.5.3-1 -- uno de los seis lugares que lista el auditor -- y la conclusion operativa (ningun valor de altura minima de relleno para concreto y TMC) sobrevive: ninguno de los seis numerales fija un recubrimiento minimo de tierra. Lo insostenible es la palabra «absoluto», no el vacio de la magnitud buscada. |
| `R95-021` | `H-07` | **SE SOSTIENE** | MEDIA | CONTRADICE | MTC Manual de Puentes (2018), num. 2.4.3.8.1 y 2.4.3.8.2, pagina impresa 113 | Comprobado punto por punto: el PDF respalda al codigo y desmiente a la fila del manifiesto. El numeral 2.4.3.8.2 fija el PROCEDIMIENTO de subpresion, no el peso especifico del agua, tal como razona el docstring de constantes_fisicas.py:35-41 («la cita era correcta en cuanto a DONDE se usa el valor... pero equivocada en cuanto a QUE es el valor»). La fila :161 arrastra tres desfases simultaneos: archivo:linea (CN:35 ya no es esa constante), etiqueta ([N] con numeral para lo que el propio repo reclasifico como constante fisica) y atribucion. Mantengo MEDIA y no subo: es un defecto de documentacion, el codigo ya lleva la correccion escrita y el numero 9.81 kN/m3 no cambia ni afecta ningun calculo. Encaja en el renglon MEDIA del briefing («referencia archivo:linea desfasada, cita incompleta»). |
| `R95-022` | `H-10` | **SE SOSTIENE** | MEDIA | CONTRADICE | MTC Manual de Puentes (2018), num. 2.8.1.3.1.2c y sus figuras -1 y -2, paginas impresas 272, 273 y 274 | Se sostiene solo por la pagina, y lo comprobe yo mismo: el rango real es 272-274 y la figura -2 (suelos no cohesivos, la aplicable a las arenas del Bajo Piura) queda fuera del rango citado. Todo lo demas CONFIRMA literalmente: numeracion de las dos figuras, atribucion a Meyerhof 1957, caracter de abaco y N_q = 0.0. Mantengo MEDIA y no subo a ALTA: no es una pagina ajena sino un rango incompleto en una unidad, dentro del numeral y del documento correctos, y el criterio esta declarado con valor None (no se calcula nada con el), de modo que el dano es que un revisor pierda una pagina. Nota menor: el auditor cita docs/manifiesto_citas.md:179, que es la fila de `factores_carga_aashto`; la fila de Meyerhof es la :178. El mismo rango 272-273 se repite en docs/hoja_de_ruta_alcantarillas_v8.md:622, que el auditor no menciona. |
| `R95-023` | `H-14` | **AJUSTADO** | MEDIA | CONTRADICE | MTC Manual de Puentes (2018), num. 2.8.1.1.14.2 completo: 2.8.1.1.14.2.1 (pag. impresa 254) y 2.8.1.1.14.2.2 (pag. impresa 255) | AJUSTADO: se sostiene la mitad del hallazgo y cae su cargo mas fuerte, por eso bajo de ALTA a MEDIA. Lo que se sostiene: el numeral es prosa, no una tabla, y llamarlo «Tabla ... del Manual de Puentes» con «dos filas» es una caracterizacion que el PDF no admite; ademas «25-50 mm» es una conversion redondeada de «1.0 a 2.0 in» que ademas suelta el «o mas», y el Manual dice «puede ser reducido» (permisivo). Lo que cae: el auditor afirma que «rigido = 1.0 NO esta escrito en el numeral: es la ausencia de reduccion, inferida». Es falso -- el mismo numeral que el repo cita, 2.8.1.1.14.2, define kh0 como el coeficiente «asumiendo que el desplazamiento del muro sea cero» en su subnumeral .2.1, de modo que el factor 1.0 para muro que no se desplaza esta escrito, no inferido; y el repo cita el numeral PADRE, que cubre .2.1 y .2.2, asi que la referencia numeral no es erronea. Queda un defecto de vocabulario y de cita incompleta (renglon MEDIA del briefing), agravado por nada mas: el proyecto adopta 1.0, el lado sin reduccion, y declara la eleccion como [A] con sensibilidad (0.5, 1.0). Nota menor: el auditor cita manifiesto_citas.md:171 y :172; la fila del factor de muro es la :170. |
| `R95-024` | `H-20` | **AJUSTADO** | MEDIA | CONTRADICE | MTC Manual de Puentes (2018), Seccion 2.9 SUPERESTRUCTURAS (pag. impresa 331), pag. impresa 337 (= num. 2.9.1.4.4.3) y num. 2.9.1.5.6.3.4.2 (pag. impresa 387) | AJUSTADO, y bajo de ALTA a MEDIA porque cae el cargo que el auditor llamo «mas de fondo». Lo que se sostiene y verifique: la pagina esta mal -- la Seccion 2.9 arranca en la impresa 331 y en la 337 no hay ninguna remision general a la Seccion 5. Lo que cae: la frase «Sec. 9.4 remite el diseno a AASHTO LRFD Seccion 5 y no transcribia nada de esa seccion» (criterios_adoptados.py:1603-1604) habla de la hoja de ruta del proyecto, no del Manual; el repo nunca afirmo que el Manual no transcriba, de modo que la Seccion 2.9 con su beta-theta no contradice nada. Tambien se desactiva la alarma de mezcla de ediciones: el repo declara su edicion expresamente («AASHTO LRFD 9a ed., 2020» en CA:1591 y CA:1630, con Arts. 5.5.4.2 y 5.7.3.4.2), manifiesto_citas.md:302 ya lleva la advertencia transversal de declarar la edicion, y las expresiones que el Manual transcribe bajo la numeracion antigua son numericamente identicas a las adoptadas -- verifique en PDFPAGE 388 = pag. impresa 387: «beta = 4.8/(1 + 750 eps_s)» y «theta = 29 + 3500 eps_s», y «Vc = 0.0316 beta raiz(fc') bv dv» en la 387-386. Queda un puntero de pagina equivocado dentro de la seccion y el documento correctos, de la misma clase que H-10, que gradue MEDIA por consistencia. |
| `R95-025` | `H-21` | **AJUSTADO** | MEDIA | CONTRADICE | Defecto interno del repo: docs/manifiesto_citas.md, bloque §3 (Manual de Puentes), filas 161, 168, 172, 173 y 181. No aplica PDF. | Los cinco defectos de coordenada son reales y los comprobé uno por uno; el manifiesto se declara en su línea 31 «un volcado literal de lo que el código YA afirma… y dónde está escrito en el repositorio», promesa que estas filas no cumplen. Ajusto dos cosas del auditor. Primera: sus propios números de fila del manifiesto están corridos en cuatro de los cinco casos (las filas reales son 161, 168, 172, 173 y 181, no 161/170/173/177/183); el archivo no cambió desde 71b134fb, solo se añadieron docs/auditorias/*. Segunda: la etiqueta [C] no es un simple choque con CA:388, porque el manifiesto usa [C] como convención propia para siete filas rotuladas «Afirmación negativa» (172, 181, 182, 255, 323, 325, 326); el choque es con su propia leyenda ([C] = «vacío cubierto con fuente técnica reconocida») y con CA:406-412, que dice expresamente «deja de ser [C] … Pasa a [A]». Añado que el defecto es más amplio de lo reportado: la fila 182 cita [CA:1068-1073], que son la fuente y la verificación pendiente del criterio 'diametros_normalizados', no la evidencia de índice 2.11→2.12. Severidad MEDIA («referencia archivo:línea desfasada» del briefing) confirmada. |
| `R95-026` | `H-22` | **SE SOSTIENE** | MEDIA | CONTRADICE | Manual de Puentes (MTC), num. 2.4.3.11.2.1.1, Tabla 2.4.3.11.2.1.1-1 y su bloque «Excepciones», página impresa 122 (PDFPAGE 123) | Las dos afirmaciones del auditor se comprueban y ninguna está matizada en el repo. Refuerzo su punto sobre la licuefacción: la Tabla 3.10.3.1-1 de AASHTO LRFD 9ª ed. (PDFPAGE 156, pág. 3-102), que es la fuente que el propio criterio dice haber verificado, tampoco lista suelos licuables, y su comentario C3.10.3.1-1 habla de «the three categories of Site Class F», es decir, la lista funciona como cerrada pese al «tales como». No subo a ALTA porque el criterio ya está etiquetado [A] con fuente «NINGUNA autoriza la adopcion», declara en CA:422-425 que la adopción «no es conservadora por construccion» y exige en CA:432-447 la caracterización sobre 30 m; además presumir F no baja ningún número hoy (para PGA ≥ 0.50 la Tabla 2.4.3.11.2.1.2-1 da C=1.0, D=1.0, E=0.9 y F=«*»). El defecto es de cita incompleta de la tabla que gobierna toda la cadena sísmica, no de número mal transcrito: MEDIA. |
| `R95-027` | `H-02` | **AJUSTADO** | MEDIA | CONTRADICE | NTE E.060 Concreto Armado, num. 4.3.1, Tabla 4.4 «Requisitos para concreto expuesto a soluciones de sulfatos», fila Moderada, página impresa 38 (PDFPAGE 38) | La truncación es real y la comprobé contra el texto de la tabla en su página impresa: se pierden P(MS), I(PM)(MS) e I(SM)(MS) al pasar de la hoja de ruta a constantes_normativas.py y de ahí al manifiesto, y la fila queda etiquetada [N] como si fuera transcripción íntegra. Ajusto dos puntos del auditor. Primero, la consecuencia que alega no ocurre: «SULFATOS» no tiene ningún consumidor en src/ — el grep devuelve únicamente su declaración en CN:287 —, de modo que hoy ningún módulo rechaza un cemento P(MS) ni imprime la lista recortada en la memoria; el daño es documental, no de cálculo. Segundo, la línea de la hoja de ruta es la 325, no la 326 (la 326 es la fila Severa). Severidad MEDIA («cita incompleta» del briefing) confirmada: sin consumidor no llega a ALTA, pero con etiqueta [N] y sin marcar el recorte tampoco es cosmética. |
| `R95-028` | `H-07` | **AJUSTADO** | BAJA | CONTRADICE | NTE E.060 Concreto Armado, Art. 7.7.5 «Ambientes corrosivos», Art. 7.7.5.1, página impresa 55 (PDFPAGE 55) | La divergencia literal existe y la comprobé sobre la imagen del PDF, no solo sobre el texto extraído, así que bajo la regla del briefing el veredicto es CONTRADICE. Pero bajo la severidad de MEDIA a BAJA: es una sola flexión verbal (infinitivo por reflexivo) dentro de una frase de dos palabras, el sentido es idéntico, no altera ningún número ni ningún deber — el contexto del repo restituye el carácter imperativo («hay que sumarle el aumento por ambiente corrosivo… directamente invocable») — y se arregla escribiendo «debe aumentarse». Eso es exactamente la casilla «cosmética / redaccional» del briefing. Confirmo además la observación de página del auditor: el Art. 7.7.5.1 está en la impresa 55 y el Art. 7.7.1 empieza en la 54, que es la que declara CN:296 para RECUBRIMIENTO; ni CN:297 ni la fila 227 del manifiesto declaran página, así que no hay error de página que reportar. |
| `R95-029` | `H-12` | **AJUSTADO** | MEDIA | CONTRADICE | NTE E.060 Concreto Armado, Arts. 11.10.10.1 y 11.10.10.2, página impresa 104 (PDFPAGE 104); Arts. 11.10.7-11.10.8, impresas 103-104; Art. 11.5.6.1, impresa 91 (PDFPAGE 91) | La misatribución es real: el artículo citado no define umbral alguno, y el que el repo invoca es de otro artículo y de otro tipo de elemento (elementos a flexión, no muros), con forma y magnitud distintas de 0,085√f'c·Acw. Bajo de ALTA a MEDIA por dos matices que el auditor no recogió y que sí leí en el propio archivo. Primero, el criterio se autodeclara sin verificar en el campo que la memoria imprime junto a la justificación: fuente = «PENDIENTE - E.060 Art. 11.10.10.2… Verificar numeral y pagina contra el texto de E.060 antes de darle valor» (CA:1572-1575), y M11_reporte.py:1047-1048 vuelca justificación y fuente en el mismo bloque. Segundo, M9_cabezal.py:192-196 dice expresamente «El Art. 11.10.10.2 NO esta en la hoja de ruta: se cita como pendiente de recoger en ella, no como numeral verificado», y la propia justificación hedgea con «del orden de». El numeral existe y el 0,0025 está bien atribuido; el criterio es VACÍO y detiene el cálculo. Queda como cita defectuosa declarada como pendiente, no como número normativo falsificado — pero el riesgo señalado por el auditor sigue en pie para cuando se cierre con un Vu real. |
| `R95-030` | `H-15` | **SE SOSTIENE** | ALTA | CONTRADICE | NTE E.060 Concreto Armado, Cap. 14 MUROS: Arts. 14.3.1 y 14.3.2 (pag. impresa 133 = PDFPAGE 133) y Arts. 14.8.2 / 14.8.3 (pag. impresa 134 = PDFPAGE 134); Art. 11.10.10.5 (pag. impresa 104 = PDFPAGE 104). Verificado sobre el PDF original con Read pages 133-134 y 104. | La contradiccion es real y la comprobe en el PDF original, no en el OCR. El 14.8.2 remite el refuerzo minimo del muro de contencion a todo 14.3, y el propio 14.3.1 dice que ese refuerzo minimo «debe cumplir con las disposiciones de 14.3», que incluyen el 14.3.2: entre 200 y 250 mm el refuerzo va en dos capas aunque el 14.8.3 aun no exija el acero de temperatura en ambas caras. La transcripcion del 14.8.3 es impecable, pero el repo la usa como umbral UNICO y la memoria imprime «en UNA cara» en un rango donde la norma ya exige dos capas, sin criterio ni vacio que lo declare, cuando el mismo repo si declaro el caso analogo de los dos minimos de cuantia (CN:302-316, criterio 'cortante_alto_muro_e060_art_11_10_10_2'). Refuerzo no citado por el auditor y que agrava el hallazgo: docs/manifiesto_citas.md:230 rotula la constante como «ESPESOR_TEMPERATURA_DOS_CARAS = 0.250 m (refuerzo en dos caras)», generalizando a TODO el refuerzo un umbral que el 14.8.3 solo fija para el acero por temperatura. Mantengo ALTA: el numeral citado es correcto y esta bien transcrito (no es CRITICA), pero la regla resultante produce un detalle no conforme en una banda de espesor realizable. |
| `R95-031` | `H-13` | **AJUSTADO** | ALTA | CONTRADICE | NTE E.060 Concreto Armado, Arts. 11.10.10.2 / 11.10.10.3 y ec. (11-32), pag. impresa 104 = PDFPAGE 104; Art. 14.2.4, pag. impresa 133. Verificado sobre el PDF original con Read page 104. | El hallazgo se sostiene: bajo el regimen de 11.10.10 -aplicable a muros por el 14.2.4- la cuantia VERTICAL tambien tiene piso 0,0025 por el 11.10.10.3, y el repo afirma expresamente lo contrario en un docstring y lo ejecuta en el codigo, devolviendo 0.0015 sin aviso ni excepcion. Lo unico que matiza el cuadro es que la frase es literalmente cierta del articulo que nombra (el 11.10.10.2 si es solo horizontal) y que el 11.10.10.3 lleva un tope («no necesita ser mayor que rho_h»), ademas de que hoy la funcion no la llama nadie del pipeline (cero referencias desde cli.py, gui/app.py y M11). AJUSTO la severidad de MEDIA a ALTA: no es una cita incompleta sino una afirmacion negativa falsa -el repo asegura que la norma no escalona el minimo vertical cuando si lo escalona- ejecutada como rama silenciosa que entrega 1,67 veces menos acero, justo el error que el archivo de criterios existe para impedir. No llego a CRITICA porque ningun numero esta mal transcrito y el 0.0015 del Art. 14.3.1 es correcto. |
| `R95-032` | `H-19` | **AJUSTADO** | MEDIA | CONTRADICE | Verificacion interna: docs/manifiesto_citas.md, bloque 5 (lineas 214-234) contra docs/hoja_de_ruta_alcantarillas_v8.md:56, :62-68 y :626-631; titulos de capitulo de NTE E.060 verificados en PDFPAGE 87, 133 y 190. | La inconsistencia de premisa existe y la comprobe: el encabezado dice «solo ... durabilidad y recubrimientos» y debajo hay seis filas [N] de los Caps. 14 y 22. AJUSTO en tres puntos del recuento del auditor. (1) Las filas de durabilidad que caben en «Cap. 4 y Art. 7.7» son SIETE (221-227), no ocho; el bloque tiene 14 filas, 13 con [N] y una con [A]. (2) La fila del escalon por cortante (linea 229, Art. 11.10.10.2) NO lleva [N] sino [A] como vacio declarado, asi que no forma parte de las seis filas [N] discrepantes: las seis son 14.3.1, 14.8.3, 14.3.3 x2 y 22.10 x2. (3) Los datos de apoyo del auditor sobre E.060 tienen errores: el Cap. 11 «CORTANTE Y TORSION» empieza en pag. impresa 87 (no 91) y el Cap. 22 se titula «CONCRETO ESTRUCTURAL SIMPLE» en pag. 190 (no «CONCRETO SIMPLE ESTRUCTURAL», pag. 189). Tambien cae el ultimatum: las seis filas SI pueden llevar [N], porque la hoja de ruta las respalda expresamente en Sec. 9.4 (:630-631); lo que esta desfasado es el encabezado del bloque 5 y el alcance escrito en :56 y :68. Por eso bajo de ALTA a MEDIA: ningun valor normativo esta mal citado ni mal transcrito, el defecto es de alcance declarado -un «solo» que la propia hoja de ruta desmiente cuatro secciones mas abajo-. |
| `R95-033` | `H-20` | **SE SOSTIENE** | MEDIA | CONTRADICE | Verificacion interna del repo: docs/manifiesto_citas.md:231 contra src/modulos/M9_cabezal.py (sin documento normativo externo). | Comprobado: el ancla del manifiesto apunta a dos lineas que tratan de cuantias y del codigo R1/R2, no del espaciamiento, y la constante no aparece en ellas ni en su funcion. El uso real esta 108 lineas mas abajo, en :1385. No hay comentario ni docstring en el manifiesto que matice el ancla, y verifique con `git diff 71b134f HEAD -- src/ docs/manifiesto_citas.md` que ni el codigo ni el manifiesto cambiaron desde el SHA auditado, de modo que no es un desfase introducido despues. Mantengo MEDIA, que es exactamente como el briefing tipifica una «referencia archivo:linea desfasada». |
| `R95-034` | `H-22` | **AJUSTADO** | MEDIA | CONTRADICE | Verificacion interna del repo: docs/manifiesto_citas.md:228 contra src/modulos/M9_cabezal.py (sin documento normativo externo). | El desfase existe: el ancla cae 7 lineas antes, en la funcion vecina, y no en la que la propia fila nombra. Corrijo dos detalles del auditor: el max() efectivo esta en 1337-1340, no en 1338-1341 (1341 esta en blanco), y el aterrizaje no es del todo ciego, porque `verificar_cuantia` si usa el mismo minimo (`minima = cuantia_minima(...)` en :1276, `valor_admisible=minima` en :1282). AJUSTO la severidad de BAJA a MEDIA: es la misma clase de defecto que el ancla de espaciamiento y el briefing tipifica «referencia archivo:linea desfasada» como MEDIA sin graduar por distancia; que las dos funciones sean contiguas y compartan el minimo no cambia que el enlace no lleva a `cuantia_de_diseno`, que es lo unico que la fila afirma. Doy por buena la comprobacion colateral del auditor sobre M9:1162, M9:1229 y M9:1358, que verifique tambien. |
| `R95-035` | `H-21` | **SE SOSTIENE** | MEDIA | CONTRADICE | Verificacion interna del repo: docs/manifiesto_citas.md:233 (bloque §5, E.060) contra src/modulos/M9_cabezal.py | La contradiccion es real y la comprobe yo mismo con grep sobre las tres rutas: la linea 1303 no tiene ninguna relacion con el ciclopeo, y el uso real esta 115 lineas mas abajo. No es errata ni matiz: el propio preambulo del manifiesto declara que cada fila dice «donde esta escrito en el repositorio», asi que el ancla es una promesa de trazabilidad incumplida. Verifique ademas que `git diff 71b134fb..HEAD -- src/ docs/manifiesto_citas.md` esta vacio, de modo que el desfase no lo introdujo un commit posterior al SHA auditado. Severidad MEDIA se mantiene: encaja exactamente en «referencia archivo:linea desfasada» de la escala del briefing; no toca ningun numero ni ninguna cita normativa (10.0 MPa y Art. 22.10 son correctos y estan bien anclados en [CN:326]). |
| `R95-036` | `H-02` | **SE SOSTIENE** | ALTA | CONTRADICE | MTC EG-2013, Capitulo V, Subseccion 508.07 «Colocacion del relleno alrededor de la estructura», pagina impresa 984 (PDF 992). Contraste con la pagina impresa 982 (PDF 990). | No hay confusion impresa/PDF por parte del auditor: el numero va en el PIE (lo vi en la imagen, en azul abajo a la derecha) y coincide con el offset del briefing (impresa = pdfpage − 8: 992 − 8 = 984). El texto citado si es literal palabra por palabra, coma decimal incluida («0,30 m»), de modo que lo unico que falla es la pagina, y falla en los seis sitios, incluida la cadena que M11 imprime en la memoria. Severidad ALTA se mantiene por la escala del briefing («pagina equivocada» = ALTA); no sube a CRITICA porque ni el numeral 508.07 ni el valor 0.30 m ni la cita textual estan mal transcritos. Correccion procedente: pag. impresa 984. |
| `R95-037` | `H-03` | **AJUSTADO** | MEDIA | CONTRADICE | Verificacion interna del repo: docs/manifiesto_citas.md:254 y :616 contra src/constantes_normativas.py:160 y :176-177 (la norma de fondo, EG-2013 508.07, pag. impresa 984, si existe y es literal) | El defecto es real y lo comprobe yo mismo: el ancla [CN:160] es falsa para la cita textual (que no vive en ese archivo) y esta 17 lineas desfasada para el valor (177, no 160). Ajusto DOS cosas respecto del auditor. (1) Severidad: baja de ALTA a MEDIA, porque encaja en «referencia archivo:linea desfasada» de la escala y no en ninguno de los supuestos ALTA — la atribucion normativa (EG-2013, 508.07, texto literal) es correcta, el codigo si tiene la cita en criterios_adoptados.py y la memoria la puede imprimir; lo unico roto es el puntero repo↔repo, exactamente el mismo defecto que H-21 (R95-035), tasado en MEDIA. (2) Localizacion del propio hallazgo: el ancla [CN:160] de §14.a esta en la linea 616 del manifiesto, no en la 614 que declara el auditor (la 614 abre el parrafo «Vale para HDPE, y su magnitud es exactamente la que calcula V7...»). |
| `R95-038` | `H-13` | **SE SOSTIENE** | MEDIA | CONTRADICE | MTC EG-2013, Capitulo V, Seccion 505: 505.03 (pag. impresa 950), 505.07 (951), 505.10 (952-953), 505.11 (953) | El rango declarado 950-951 es real y esta truncado: cubre 505.03 y 505.07 pero deja fuera 505.10 y 505.11, que son precisamente las que sostienen las dos afirmaciones operativas de la ficha (1/4 del diametro exterior y relleno por la Sec. 502). El CONTENIDO si confirma en las cuatro subsecciones, con las citas literales que alega el auditor («concreto simple, clase F, segun lo especificado en la Subseccion 503.04», «espesor no menor de 15 cm», el cuarto del diametro y el reenvio a la Seccion 502 — este ultimo con la errata de la propia norma, «conforme a lo senalado la Seccion 502», sin «en»). Mantengo MEDIA y no subo a ALTA: no es una pagina equivocada de raiz como H-02 o H-10 (donde ninguna de las paginas declaradas contiene lo citado), sino una cita incompleta, supuesto que la escala del briefing tasa en MEDIA. Correccion procedente: pags. 950-953. |
| `R95-039` | `H-10` | **SE SOSTIENE** | ALTA | CONTRADICE | MTC EG-2013, Capitulo V, Seccion 507: 507.05 y 507.06 en pag. impresa 973 (PDF 981); 507.08 en pag. impresa 974 (PDF 982). Contraste con las paginas impresas 969 (PDF 977) y 970 (PDF 978). | La remision a ASTM A-807 existe y es literal en las tres subsecciones, de modo que la sustancia del argumento del repo (el EG-2013 cierra el circuito hacia la norma de producto para TMC) se sostiene. Lo que cae es la paginacion: el error es de 3 a 4 paginas y las paginas declaradas contienen materia de otra naturaleza — el encabezado de la Seccion 507 y la tabla de espesores minimos/galvanizado —, asi que un revisor que abra la 969-970 no encuentra ninguna de las tres remisiones. Verificado por dos vias: pie impreso leido sobre la imagen del PDF y offset del briefing (981 − 8 = 973; 982 − 8 = 974). Severidad ALTA se mantiene («pagina equivocada»). Correccion procedente: 507.05/.06, pag. 973; 507.08, pag. 974. |
| `R95-040` | `H-14` | **SE SOSTIENE** | MEDIA | CONTRADICE | EG-2013, Seccion 505: num. 505.10 y 505.11 (pag. impresa 953, PDFPAGE 961) y 505.06 (pag. impresa 951, PDFPAGE 959); cadena de remision 502.09(c)(1) (pag. impresa 900, PDFPAGE 908) y 205.12(c)(1) (pag. impresa 193, PDFPAGE 201) | Comprobado punto por punto: la Seccion 502 no exige 95 % al relleno de zanja, exige 90 % en base y cuerpo y 95 % solo en corona, de modo que «Relleno Sec. 502 >= 95% MDS» enuncia un requisito que la norma no enuncia. No es errata de OCR ni diferencia de edicion: el texto es capa nativa y el pie impreso de cada pagina coincide con el offset. La fraccion 1/4 si CONFIRMA — 505.10: «hasta una altura no menor de un cuarto del diametro exterior del tubo». Refuerza el hallazgo la incoherencia interna del propio repo: para el TMC, misma cadena hacia 205.12(c)(1), la ficha si desglosa «>= 90% en base y cuerpo, >= 95% en corona» (linea 220-221). Mitigacion que el auditor no cito y que impide subir la severidad: el comentario de las lineas 197-203 declara que la ficha es «Solo texto (cama, sujecion, numeral): no es una verificacion con umbral», y el error va del lado conservador; pero la ficha esta destinada a memoria y planos y esta etiquetada [N] en el manifiesto, asi que MEDIA se sostiene. |
| `R95-041` | `H-15` | **SE SOSTIENE** | MEDIA | CONTRADICE | EG-2013, Seccion 506: 506.03 (pag. impresa 959, PDFPAGE 967), 506.07 (pag. impresa 960, PDFPAGE 968), 506.10 y 506.11 (pag. impresa 961, PDFPAGE 969) | El rango declarado 959-960 cubre solo dos de los cuatro numerales citados; 506.10 y 506.11 — justamente los que aportan el 1/6 del diametro y la remision de relleno a la Seccion 502 — caen en la 961. No es confusion impresa/PDF: cada bloque de pagina lleva su propio pie impreso y el offset (impresa = PDFPAGE - 8) se verifica en las tres paginas. Tampoco es diferencia de edicion: el mismo archivo situa 506.03 en 959 y 506.07 en 960 exactamente donde el repo dice, luego la baseline de paginacion es la correcta y el defecto es un rango una pagina corto. Los contenidos si CONFIRMAN (1/6, subbase Sec. 402, 15 cm y 95 % de corona), por lo que el defecto es de referencia incompleta y MEDIA es la severidad adecuada. |
| `R95-042` | `H-17` | **SE SOSTIENE** | MEDIA | CONTRADICE | EG-2013, Seccion 508: 508.01/508.02 a) (pag. impresa 981, PDFPAGE 989), 508.02 d) (pag. impresa 982, PDFPAGE 990), 508.05 (pag. impresa 983, PDFPAGE 991), 508.07 (pag. impresa 984, PDFPAGE 992) | Verificado: ninguno de los dos numerales citados (508.05, 508.07) cae dentro del rango declarado 981-982, y el numeral omite 508.02(d), unica fuente de la «arena gruesa». No hay defensa de edicion: el mismo archivo situa 505.03 en 950 y 506.03 en 959 tal como el repo cita, luego la paginacion base coincide y estos son deslices localizados de 1 a 2 paginas. Los VALORES si confirman (arena gruesa, capas de 0,15 m, espesor 0,15-0,30 m, 0,30 m en suelo de baja capacidad portante o rocoso) y «roca o suelo blando» es parafrasis de un campo descriptivo sin comillas, no divergencia de valor. Mantengo MEDIA y no subo a ALTA porque el rango 981-982 si abre la Seccion 508 y si contiene la frase de la arena gruesa que la ficha resume: el defecto es de cita incompleta y numeral omitido, no de pagina totalmente ajena. |
| `R95-043` | `H-16` | **SE SOSTIENE** | ALTA | CONTRADICE | EG-2013, Seccion 507: 507.06 y arranque de 507.07 (pag. impresa 973, PDFPAGE 981), 507.07 arena y 507.08 (pag. impresa 974, PDFPAGE 982); pagina impresa 970 = PDFPAGE 978 | Comprobado sobre la imagen del PDF original, no solo sobre el texto extraido: la pagina 970 no contiene ninguno de los tres numerales citados y el material real esta 3-4 paginas mas adelante, repartido en dos paginas donde el repo declara una sola. No es confusion impresa/PDF (el pie impreso 973 aparece en la propia imagen de PDFPAGE 981) ni diferencia de edicion (505.03 en 950 y 506.03 en 959 coinciden con el repo). Los contenidos CONFIRMAN integramente: subbase Sec. 402 via 506.07 (15 cm y 95 % de corona), arena suelta de 12 mm, capas de 15-20 cm y 90/95 % por 205.12(c)(1). Severidad ALTA confirmada por la escala («pagina equivocada»): quien vaya a la 970 no encuentra nada de lo citado, a diferencia de R95-041 y R95-042 donde el rango al menos roza el material. |
| `R95-044` | `H-21` | **SE SOSTIENE** | MEDIA | CONTRADICE | EG-2013 completo (busqueda exhaustiva de «recubrimiento», 38 ocurrencias); 508.07 pag. impresa 984 (PDFPAGE 992) y 508.08 pag. impresa 985 (PDFPAGE 993); recubrimiento de zinc pag. impresa 971 (PDFPAGE 979); recubrimiento bituminoso pag. impresa 976 (PDFPAGE 984) | La afirmacion negativa se sostiene porque la busque de verdad y en todo el documento, no solo en las Secciones 502-508: el EG-2013 no usa «recubrimiento» para el relleno de tierra sobre la clave en ninguna de sus 38 apariciones. Confirme tambien la homonimia interna: M7.altura_recubrimiento() devuelve metros de tierra (modelos.py:767 «h_recubrimiento: float # m - relleno minimo sobre la clave») mientras M9_cabezal.recubrimiento_de_diseno()/recubrimiento_aashto_mm()/recubrimiento_e060_mm() devuelven milimetros de concreto sobre el acero, y constantes_normativas.py:10 llega a declarar «mm en recubrimientos». La trampa esta anotada solo para el Manual de Puentes (manifiesto §3 linea 183 y §14.a linea 619; criterios_adoptados.py:1129-1135) y el propio §14.a la comete al escribir «exigir su recubrimiento al concreto y al TMC» (manifiesto linea 598). Matiz a favor del repo que el auditor no menciono y que impide subir de MEDIA: el docstring de M7 y el de altura_recubrimiento si definen h_rec con el lexico normativo («relleno minimo sobre la clave», «EG-2013 508.07/508.08»), de modo que el valor y su numeral estan bien citados y el defecto es de nomenclatura no declarada, que la escala situa exactamente en MEDIA. |
| `R95-045` | `H-22` | **SE SOSTIENE** | MEDIA | CONTRADICE | Verificacion interna repo-repo: docs/manifiesto_citas.md §6, filas 243-244, contra src/constantes_normativas.py:176-189 y §14.a del propio manifiesto. Contraste normativo de apoyo: AASHTO M 170M-04, Nota 1 y num. 4.1 (M170M_OCR, PDFPAGE 2). | Se sostiene: el manifiesto se declara «un volcado literal de lo que el codigo YA afirma» (linea 31) y sus filas 243-244 reproducen, etiquetadas [N]/[C], exactamente el texto que el codigo borro por apuntar a tablas inexistentes, en contradiccion con el §14.a del propio documento. Dos matices comprobados que impiden subir la severidad: las clases I a V SI existen en M 170M (num. 4.1, Tablas 1 a 5), solo que clasifican por D-load, de modo que no es un numeral inexistente sino un puntero inutil; y la remision EG-2013 506.02 -> M-170M / 507.05-.06-.08 -> ASTM A-807 es real (fila 256 del propio manifiesto), asi que la columna «Documento fuente» no miente. Ademas el enlace [CN:176] aterriza dos lineas por encima del comentario correctivo, con lo que un verificador que siga el puntero lee la correccion. Queda como defecto de sincronia documental con etiqueta [N] indebida: MEDIA, la severidad propuesta. |
| `R95-046` | `H-23` | **AJUSTADO** | MEDIA | CONTRADICE | Verificacion interna repo-repo: docs/manifiesto_citas.md §6, filas 245, 247-250 y 255-257, contra src/criterios_adoptados.py:1074-1170, src/constantes_normativas.py:204-232 y src/modulos/M11_reporte.py:694-703. Convencion declarada en tests/test_manifiesto_citas.py, docstring lineas 16-21 y 52-70. | Los ocho desajustes son reales y los verifique yo mismo, de modo que el hallazgo no se cae; lo que se ajusta es su alcance. El auditor habla de «desfase sistematico» y de «punteros que no aterrizan», y eso es falso para siete de los ocho: el ancla del enlace (src/criterios_adoptados.py:1076, :1082, :1103) cae dentro del bloque del criterio h_relleno_min_concreto_tmc (1074-1170) y [CN:204] es la linea de definicion exacta de CAMA_RELLENO_LATERAL, que es precisamente lo que el propio repo declara legitimo y verifica en tests/test_manifiesto_citas.py («Apuntar DENTRO del bloque es legitimo y frecuente... Solo cuenta como desfase salir del bloque»). Lo que si esta mal es el RANGO impreso en la etiqueta -- un lector que no clique va a 1076-1082 y encuentra otra cosa, 60 lineas antes -- y un unico puntero genuinamente extraviado, [M11:697]. Ese mismo test declara ademas que las referencias de prosa, como la fila de afirmacion negativa, no las cubre nadie: «una referencia de prosa puede quedar desfasada sin que nada avise». Severidad MEDIA por «referencia archivo:linea desfasada», sin subir ni bajar. |
| `R95-047` | `H-24` | **SE SOSTIENE** | MEDIA | CONTRADICE | EG-2013, indice del Capitulo V (DRENAJE), pagina impresa vii-viii, PDFPAGE 7 -- no la 6 que anota el auditor, que corresponde al indice de pavimentos (Secciones 415-440). Repo: docs/manifiesto_citas.md:251 contra docs/hoja_de_ruta_alcantarillas_v8.md:57, :557 y :827. | Se sostiene entero: comprobe la inexistencia de la Seccion 500 en el indice del propio EG-2013 y las tres ocurrencias supervivientes con su numero de linea. El agravante que el auditor no explicita es que Claude.md:4 fija esa hoja de ruta como «Fuente normativa unica» y Claude.md:8 ordena «Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta», y el manifiesto §11.a la llama «la fuente de verdad del proyecto»: la regla de precedencia reinstalaria el numeral falso. La unica correccion que introduzco es de localizacion: el indice del Capitulo V esta en PDFPAGE 7, no en la 6. Mantengo MEDIA y no subo a ALTA porque el error normativo de fondo (la Seccion 500 inexistente) ya quedo puntuado en H-05 y aqui el defecto residual es de sincronia documental: el software no emite la cita falsa. |
| `R95-048` | `H-02` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA-HIF-12-026 (HDS-5, 3a ed., abril 2012), Apendice A: num. A.2.1, pag. impresa A.1 (PDFPAGE 190); num. A.2.2, pag. impresa A.2 (PDFPAGE 191); Tabla A.1, pag. A.8 (PDFPAGE 197, renderizada). | Se sostiene: los dos valores son correctos pero la pagina y el numeral que los respaldan son los equivocados, que es exactamente el supuesto de severidad ALTA («pagina equivocada»). No es un descuido aislado del encabezado: M4_control.py:340-341 tambien llama «ecuaciones literales de la Tabla A.1» a las Ecs. (A.1)/(A.2)/(A.3), que viven en el num. A.2, de modo que la confusion Tabla A.1 / Sec. A.2 es sistematica en el modulo. Confirmo tambien la exculpacion del auditor sobre el factor: 1.811 x 1.93 = 3.4952 y 1.811 x 2.21 = 4.0023, asi que comparar q* = KU_METRICO*Q/(area_llena(D)*sqrt(D)) (M4_control.py:301) contra 3.5 y 4.0 (M4_control.py:318-321) equivale a la regla SI del HDS-5. Correccion exacta de la cita: Apendice A, num. A.2.1, pag. A.1 para el 3.5, y num. A.2.2, pag. A.2 para el 4.0. |
| `R95-049` | `H-01` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA-HIF-12-026 (HDS-5, 3a ed., abril 2012), Apendice A, num. A.2.1, lista «Where:» de la pag. impresa A.2 (PDFPAGE 191, renderizada) frente a la Tabla A.1, pag. A.8 (PDFPAGE 197, renderizada). | Se sostiene: el valor 1.811 es literal y correcto, pero la fuente citada no lo contiene, y «pagina equivocada» es ALTA en la escala. El agravante interno es que el repo YA sabe lo que hay en esa tabla: M4_control.py:84-85 dice «Las cinco constantes de la Tabla A.1 son K, M, c e Y... y cuatro no son cinco. K_s ... NO figura en esa tabla», y sin embargo el encabezado atribuye a la misma tabla el Ku que esta en el mismo renglon del PDF que el Ks excluido. Solo corrijo un detalle aritmetico del auditor: la Tabla A.1 tiene diez columnas, no nueve (el propio auditor enumera diez). La correccion de cita que propone es exacta: Apendice A, num. A.2.1, pag. impresa A.2, lista de definicion de variables de las Ecs. (A.1)/(A.2). |
| `R95-050` | `H-08` | **AJUSTADO** | MEDIA | CONTRADICE | FHWA-HIF-12-026 (HDS-5 3a ed., 2012): indice pag. impresa v-vi (PDFPAGE 9-10), encabezado de Cap. 4 pag. impresa 4.1 (PDFPAGE 127), pag. impresa 3.4 (PDFPAGE 86) y Apendice A, Sec. A.2, pag. impresa A.1 (PDFPAGE 190) | La contradiccion es real y la comprobe yo mismo: el Cap. 4 de la 3a ed. es AOP y no toca la transicion, y en la 2a ed. el Cap. 4 era Tapered Inlets, asi que la cita no cuadra con ninguna edicion. Ajusto de ALTA a MEDIA porque la MITAD correcta de la cita hace el trabajo: el "Apendice A" que el repo tambien invoca es exactamente donde la fuente sostiene, literal, lo que el repo afirma (curva tangente empirica, sin ecuacion publicada), de modo que el lector si llega a la evidencia. Ademas el criterio es [C], no [N]: no hay ningun numero normativo en juego, solo un puntero de capitulo erroneo, que es "cita incompleta / referencia desfasada". Correccion que corresponde: "Cap. 3 (Sec. 3.1.3, pag. 3.4; Sec. 3.2.1, pag. 3.20) y Apendice A, Sec. A.2, pag. A.1", y en arabigos, que es como numera la 3a ed. |
| `R95-051` | `H-11` | **SE SOSTIENE** | MEDIA | CONTRADICE | Verificacion interna del repo: src/constantes_normativas.py:124-126 contra docs/hoja_de_ruta_alcantarillas_v8.md (911 lineas). Contraste normativo del valor: FHWA-HIF-12-026 pag. impresa 3.10 (PDFPAGE 92) | Verifique las cuatro lineas una por una con awk sobre el archivo y el hallazgo se sostiene tal cual: tres de las cuatro referencias estan desfasadas (+4, +7 y +7 lineas) y una ocurrencia real queda sin citar. La discrepancia de fondo (la hoja de ruta sigue diciendo 19.62 frente al 19.63 de constantes) es cierta y esta bien planteada; lo defectuoso es solo el puntero. Matizo un punto de la nota del auditor: la consecuencia que anuncia ("concluira que la discrepancia ya se cerro") esta algo sobredimensionada, porque cada linea citada cae dentro del mismo bloque y a 4-7 lineas de la ocurrencia real, visible en la misma pantalla. Aun asi la severidad correcta es MEDIA, que es justo el casillero "referencia archivo:linea desfasada" de la escala. |
| `R95-052` | `H-13` | **AJUSTADO** | MEDIA | CONTRADICE | FHWA-HIF-12-026 (HDS-5 3a ed., 2012), Sec. 3.3.3, pag. impresa 3.24 (PDFPAGE 106) y Sec. 3.1.4, pag. impresa 3.12 (PDFPAGE 94) | Las tres citas del auditor son literales y estan en las paginas que dice, y la ausencia de guarda numerica es cierta: grep de 0.75/1.2D sobre src/ solo devuelve el y/D<=0.75 de V1, que es otra cosa. Pero AJUSTO porque la afirmacion nuclear del auditor -- "sin declarar ni verificar limite de validez alguno" y "ni advertencia en la memoria" -- es falsa en su mitad declarativa: el repo declara la salvedad del barril que no llena en el criterio contiguo del mismo archivo y M11 la imprime. Lo que realmente falta son los DOS UMBRALES NUMERICOS (piso HW >= 0.75D, zona de cautela HW < 1.2D) y cualquier comprobacion ejecutable. Bajo de ALTA a MEDIA tambien porque la exposicion es estrecha: h_o >= (y_c+D)/2 >= D/2, y en el regimen HW < 0.75D el control de entrada gobierna casi siempre en `hw_gobernante()`, de modo que el numero fuera de dominio rara vez llega a ser el HW reportado. Queda como cita incompleta: se transcribe la formula sin sus dos numeros de validez. |
| `R95-053` | `H-17` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA-HIF-12-026 (HDS-5 3a ed., 2012), Sec. 2.2.5.d "Agency Constraints", pag. impresa 2.10 (PDFPAGE 72); inicio de Sec. 2.2.5 en pag. impresa 2.9 (PDFPAGE 71); indice en pag. impresa v (PDFPAGE 9) | Renderice el mapa de folios y lei las tres paginas: la 2.14 no tiene nada de HW/D y el rango esta cuatro paginas antes, en la 2.10. El rango 1.0-1.5 si esta bien transcrito y la seccion 2.2.5 es la correcta, pero la PAGINA es falsa, y con el agravante de estar marcada "CITA CERRADA por verificacion externa contra el documento": se declaro verificado lo que no se verifico. Mantengo ALTA, que es el casillero de "pagina equivocada" en la escala. Sostengo tambien el matiz de fondo del auditor: HDS-5 no propone 1.0-1.5 como rango propio de diseno sino que DESCRIBE lo que suelen imponer las agencias ("varies throughout the country, but commonly ranges from..."), y el repo lo redacta como "el rango que HDS-5 da para el diseno corriente", convirtiendo una observacion descriptiva en recomendacion de la fuente. |
| `R95-054` | `H-15` | **SE SOSTIENE** | ALTA | CONTRADICE | FHWA-HIF-12-026 (HDS-5 3a ed., 2012), Apendice C: Tabla C.2 "Entrance Loss Coefficients", pag. impresa C.6 (PDFPAGE 216); pag. impresa C.2 (PDFPAGE 212); Tabla A.1, pag. impresa A.8 (PDFPAGE 197) | Comprobe folio por folio con el mapa de paginas y leyendo ambas paginas: la Tabla C.2 esta en la C.6, no en la C.2, que es el indice de cartas. El VALOR 0.5 y la TABLA invocada son correctos, y por eso no subo a CRITICA; lo erroneo es la pagina y el rotulo de fila entrecomillado, que en la Tabla C.2 se lee "Headwall or headwall and wingwalls / Square-edge" y no "square edge with headwall" -- ese rotulo es el de la Tabla A.1, trasplantado. Agravante identico al de la cita anterior: figura como "CITA CERRADA por verificacion externa contra el documento". Mantengo ALTA ("pagina equivocada"). Unica correccion menor a la nota del auditor: el folio impreso va en la CABECERA de la pagina, no al pie, detalle que no altera nada. |
| `R95-055` | `H-20` | **REFUTADO** | OK | CONFIRMA | FHWA-HIF-12-026 (HDS-5, 3a ed. 2012), pag. impresa 3.9 (PDFPAGE 91) tras la Ec. (3.3) y pag. impresa B.1 (PDFPAGE 203) tras la Ec. (B.1) | El auditor atribuye al repo una afirmacion que el repo no hace. En ninguna parte se presenta 9.81 como transcripcion de HDS-5: el manifiesto (lineas 22-27) declara que la coherencia buscada es con GAMMA_AGUA_KN_M3, un asunto interno, y la fila 81 marca G como constante fisica SIN numeral que citar. Ademas el propio repo ya hizo, y documento, exactamente el ejercicio que el auditor pide - separar el numero de la fuente - cuando corrigio K_FRICCION_SI de 19.62 a 19.63 y borro la derivacion '2*g' por falsa. La divergencia 9.8/9.81 no toca ninguna cita del proyecto y la declaracion que el hallazgo reclama ya esta escrita en constantes_fisicas.py y en M4_control.py. |
| `R95-056` | `H-21` | **AJUSTADO** | MEDIA | CONTRADICE | Verificacion interna del repositorio: docs/manifiesto_citas.md:268-270 y :275 contra src/constantes_normativas.py:99-127 (no hay PDF que consultar) | El hallazgo se sostiene en su sustancia: el rango 99-100 no cubre ninguna de las tres entradas por completo - ni siquiera la de concreto, cuya segunda linea lleva dos de los cuatro valores citados - y las de CM headwall y CM mitered quedan fuera por entero; y la fila de h_o apunta a un encabezado de seccion en vez de a su comentario. Dos ajustes: (a) la fila de h_o esta en docs/manifiesto_citas.md:275, no en :276 - la :276 es 'hds5_embocadura_hdpe', que cita [CA:677] y no [CN:110]; (b) subo la severidad de BAJA a MEDIA porque el briefing clasifica expresamente 'referencia archivo:linea desfasada' como MEDIA. Verificado ademas que estos archivos no cambiaron entre el SHA auditado 71b134fb y HEAD, de modo que el desfase no es un artefacto de version. |
| `R95-057` | `H-02` | **AJUSTADO** | CRITICA | CONTRADICE | AASHTO LRFD Bridge Design Specifications, 9th ed. 2020 - Art. 12.6.6.3 'Minimum Cover', pag. impresa 12-21 (PDFPAGE 1659) y Tabla 12.6.6.3-1, pag. impresa 12-22 (PDFPAGE 1660) | El vacio esta mal afirmado y lo verifique yo mismo: AASHTO LRFD Sec. 12 tabula la cobertura minima para tuberia de concreto reforzado Y para tuberia metalica corrugada, el PDF esta en normas/, y la propia hoja de ruta del proyecto (linea 53) lo declara 'norma matriz' justamente por su Seccion 12. Decir 'no esta en ninguna fuente' tras revisar tres que no la incluyen es un vacio afirmado que la norma si llena: CRITICA segun el briefing. Ajustes respecto del auditor: (1) el apoyo mas fuerte no es la Via 1 de Sec. 0.2 (que trata la relacion carga-resistencia) sino la fila 53 de la hoja de ruta, que nombra la Sec. 12 por su nombre; (2) su consecuencia (3) esta invertida - AASHTO mide desde el fondo del pavimento flexible e INCLUYE base y subbase, de modo que el tramo del proyecto (clave a subrasante) es un SUBtramo del de AASHTO y 0.30 m a subrasante mas base y subbase supera las 12 in; por eso las consecuencias (1) 0.30 < 0.3048 y (2) Bc/8 ~ 0.39 m no demuestran diseno inseguro mientras no se reconcilien los datums, cosa que el repo tampoco hace. Lo que se sostiene es el defecto documental, no una insuficiencia numerica probada. |
| `R95-058` | `H-03` | **SE SOSTIENE** | ALTA | CONTRADICE | AASHTO LRFD 9th ed. 2020 - Art. 12.6.6.3 y C12.6.6.3, pag. impresa 12-21 (PDFPAGE 1659); Tabla 12.6.6.3-1, pag. 12-22 (PDFPAGE 1660); Art. 12.8.3.1.1 y su comentario, pag. impresa 12-30 (PDFPAGE 1668) | Comprobado en la fuente: 1.0 ft no es 'el tipico' sino el piso de max(Bc/8, B'c/8), y la excepcion 'salvo diseno especial de armadura' no existe en el Art. 12.6.6.3 - es lenguaje importado del Art. 12.8, otro material y otro articulo. La atribucion de contenido a un numeral que dice otra cosa es ALTA y se confirma la severidad propuesta. Dos precisiones: la fila esta en manifiesto_citas.md:635, no :634 (la 634 es el separador de la tabla), y el defecto no vive solo en el manifiesto sino tambien en el codigo (criterios_adoptados.py:1147-1155), lo que lo agrava en alcance. Matizo solo el tercer punto del auditor: 'la verificacion deberia confirmarla, no corregirla' queda SIN respaldo en el articulo citado mas que demostradamente falsa, porque AASHTO mide la cobertura desde el fondo del pavimento incluyendo base y subbase y el repo nunca reconcilia ese datum con su subrasante. |
| `R95-059` | `H-04` | **AJUSTADO** | BAJA | CONTRADICE | AASHTO LRFD 9th ed. 2020 - Tabla 12.6.6.3-1 'Minimum Cover', pag. impresa 12-22 (PDFPAGE 1660) | El argumento de conservadurismo SI se sostiene en la condicion que le toca al proyecto: bajo carretera pavimentada AASHTO exige al termoplastico ID/2 >= 24.0 in (0.61 m) y al concreto reforzado Bc/8 >= 12.0 in (0.30 m) - el HDPE es, ahi, el mas exigente por un factor de dos, y el propio auditor lo admite entre parentesis. Su contraejemplo vive en la fila de 'unpaved areas', que no es la situacion de una alcantarilla bajo subrasante; ademas, en el catalogo del proyecto tanto ID/8 como Bc/8 caen bajo el piso de 12.0 in salvo para concreto con Bc > 96 in (D del orden de 2.44 m o mas), un extremo del catalogo. Lo unico que queda en pie es redaccional: la frase esta escrita como propiedad incondicional del material y deberia condicionarse a la situacion de pavimento. Bajo ALTA a BAJA: no es un argumento de conservadurismo que se caiga, es una generalizacion sin acotar. |

### 13.1 Evidencia por ítem

**`R48-021` — hallazgo `G-09` — AJUSTADO (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD Bridge Design Specifications, 9th ed. (2020), Art. 12.6.6.3 «Minimum Cover» (pág. impresa 12-21) y Tabla 12.6.6.3-1 (pág. impresa 12-22)

Leí src/criterios_adoptados.py:1149-1155 (campo `reemplazado_por` del criterio abierto en :1074): «Concreto reforzado: AASHTO LRFD Art. 12.6.6.3 -- cobertura minima tipica 1.0 ft (~0.305 m) salvo diseno especial de armadura, de modo que la adopcion coincide practicamente con el tipico de AASHTO y la verificacion deberia confirmarla, no corregirla», repetido en docs/manifiesto_citas.md:635. Abrí el PDF (pages 1659-1660). Art. 12.6.6.3, pág. 12-21 / PDFPAGE 1659: «The minimum cover, including a well-compacted granular subbase and base course, shall not be less than that specified in Table 12.6.6.3-1». Tabla 12.6.6.3-1, pág. 12-22 / PDFPAGE 1660: «Reinforced Concrete Pipe | Under unpaved areas or top of flexible pavement | Bc/8 or B'c/8, whichever is greater, ≥ 12.0 in.»; «Under bottom of rigid pavement | 9.0 in.»; «Corrugated Metal Pipe | — | S/8 ≥ 12.0 in.»; nota al pie «* Minimum cover taken from top of rigid pavement or bottom of flexible pavement». En el impreso lo confirmé como «≥», no como «>» del OCR.

**`R48-022` — hallazgo `G-10` — AJUSTADO (MEDIA, CONFIRMA)**

*Dónde se miró:* FHWA HDS-5 3ª ed., abril 2012 (FHWA-HIF-12-026), Ec. (3.4b), pág. impresa 3.10 (PDFPAGE 92) y Ec. (DG 3.1), pág. impresa DG3.3 (PDFPAGE 296)

El PDF escribe dos veces la cifra: «KU = 29 in English Units (19.63 in SI)» (HIF12026.txt línea 4767, PDFPAGE 92 = pág. impresa 3.10) y «KU is 29 (19.63 in SI Units)» (línea 13763, PDFPAGE 296 = pág. impresa DG3.3). En el repo leí src/constantes_normativas.py:111 «K_FRICCION_SI = 19.63» y :124-126 «DISCREPANCIA ABIERTA CON LA HOJA DE RUTA... Aqui gana la fuente primaria HDS-5 por verificacion externa; la hoja de ruta debe corregirse». docs/hoja_de_ruta_alcantarillas_v8.md escribe 19.62 en 436, 440, 797 y 908. src/criterios_adoptados.py:825 imprime «La ecuacion de control de salida de la hoja de ruta, H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g)», y el pie renderiza «hoja_de_ruta_alcantarillas_v8.md (v7), fuente normativa unica del proyecto».

**`R48-023` — hallazgo `G-12` — AJUSTADO (MEDIA, CONFIRMA)**

*Dónde se miró:* MTC, Manual de Carreteras: Suelos, Geología, Geotecnia y Pavimentos (abril 2014), num. 4.5.4 «Sub rasante» (pág. impresa 42) y num. 9.1(3) (págs. impresas 89-90)

El numeral dice exactamente lo que el criterio afirma. Num. 4.5.4, pág. impresa 42 / PDFPAGE 43: «El nivel superior de la sub rasante debe quedar encima del nivel de la napa freática como mínimo a 0.60 m cuando se trate de una sub rasante excelente - muy buena (CBR ≥ 20 %); a 0.80 m ...; a 1.00 m ...; y, a 1.20 m ...». Num. 9.1(3), PDFPAGE 90-91 (págs. impresas 89-90): «La superficie de la sub rasante debe quedar encima del nivel de la napa freática como mínimo a 0.60 m...». En el repo leí src/criterios_adoptados.py:908-918 (etiqueta «N->», sin campo `vacio_verificado`), M11_reporte.py:1189-1192 (`if c.vacio_verificado and c.valor is not None`) y :751-760 (la remisión «☛ acotacion» condicionada a `declarado.vacio_verificado`). En un render forzado a Fase 5 la fila V4 sale «... num. 4.5.4 y 9.1(3) [hoja de ruta: Sec. 5.1] ... N→ resguardo_HW_subrasante» sin «☛ acotacion», mientras h_relleno_min_concreto_tmc sí la lleva.

**`R48-024` — hallazgo `HR-02` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Defecto interno del repo: Claude.md (150 líneas) frente a docs/hoja_de_ruta_alcantarillas_v8.md (911 líneas) y docs/auditoria_y_ruta_despliegue_v9.md:409-416, :483-486, :525. El documento que el ítem declara como fuente (HDS-5 2ª ed. SI, 1985) no interviene.

Claude.md:4-7: «Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v8.md ... Toda cita de numeral se verifica contra ese archivo. Nunca se inventa un numeral»; :8: «Si la hoja de ruta y tu conocimiento previo discrepan, gana la hoja de ruta». src/constantes_normativas.py:125-126: «Aqui gana la fuente primaria HDS-5 por verificacion externa; la hoja de ruta debe corregirse». Grepeé la hoja de ruta entera: 0 coincidencias de «fuente primaria», «prevalec», «gana la», «discrepan» o «discrepancia». La autorización está solo en docs/auditoria_y_ruta_despliegue_v9.md:409-416 («Corrección a mí mismo: `K_FRICCION_SI` debería ser 19.63, no 19.62») y :483-486, y Claude.md nunca nombra ese archivo. El remedio no se ejecutó: el Anexo B de la hoja de ruta (línea 797, dentro del bloque que Claude.md declara origen de constantes_normativas.py) sigue diciendo «K_FRICCION_SI = 19.62».

**`R48-025` — hallazgo `HR-03` — AJUSTADO (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA HDS-5 3ª ed., abril 2012 (FHWA-HIF-12-026), Apéndice B, pág. impresa B.1 (PDFPAGE 203), Ec. (B.3); Ec. (3.4b) en pág. impresa 3.10 (PDFPAGE 92)

Apéndice B, pág. impresa B.1 / PDFPAGE 203: «The Manning equation, an empirical relationship, is commonly used to calculate the barrel friction losses in culvert design.  The usual form of the Manning equation is as follows:» seguido de la Ec. (B.3) V = (1.486/n)·R^(2/3)·S^(1/2), y literal: «Substituting Hf/L for S and rearranging Equation (B.3) results in Equation (3.4b).» La (3.4b) es Hf = KU·(n²L/R^1.33)·V²/(2g) (PDFPAGE 92). Reordenando: KU = 2g/Kn²; en inglés 2(32.2)/1.486² = 29.16, el 29 del propio HDS-5; en SI Kn = 1, luego KU = 2g = 19.62. En el repo leí src/constantes_normativas.py:117-123 («Es una coincidencia numerica... HDS-5 no deriva K de la gravedad: K absorbe la conversion de unidades del termino de friccion de Manning, donde g no interviene sola»), el mismo texto en src/modulos/M4_control.py:109-116, la afirmación repetida en docs/manifiesto_citas.md:274 («coincidencia numérica sin respaldo en la fuente») y endurecida en tests/test_constantes_normativas.py:289-296, cuyo assert es `CN.K_FRICCION_SI != pytest.approx(2 * G, abs=1e-9)`.

**`R48-026` — hallazgo `HR-05` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* docs/hoja_de_ruta_alcantarillas_v8.md, Anexo B - Constantes normativas para el script (bloque ```python, lineas 743-872). Verificacion interna del repo, sin PDF detras.

Lei la linea 4 de src/constantes_normativas.py: "Anexo B de docs/hoja_de_ruta_alcantarillas_v8.md, copiado literalmente." Extraje el bloque del Anexo B (lineas 744-871) y lo compare con ast.literal_eval contra el modulo: 41 nombres en el Anexo B, 62 en el codigo, 36 comunes, un solo valor divergente (K_FRICCION_SI = 19.62 en el Anexo B frente a 19.63 en el codigo), 5 nombres del Anexo B ausentes (G, SUBSECCION, ZONA_SISMICA_LA_UNION, Z_E030, PERFIL_SUELO_PRESUNTO) y 26 anadidos por el codigo, doce de ellos NUMERAL_*. Los conteos del auditor son exactos. Pero el mismo archivo declara en sitio dos de las tres divergencias: lineas 124-126, "DISCREPANCIA ABIERTA CON LA HOJA DE RUTA: docs/hoja_de_ruta_alcantarillas_v8.md (lineas 432, 436, 790 y 901) sigue escribiendo 19.62", y lineas 51-56, donde G_LAUSHEY explica el renombre y remite a constantes_fisicas.py; el propio docstring, lineas 12-24, abre una "ADVERTENCIA DE DOBLE DEFINICION" que ya admite apartarse del Anexo B.

**`R48-027` — hallazgo `HR-06` — AJUSTADO (BAJA, CONTRADICE)**

*Dónde se miró:* docs/hoja_de_ruta_alcantarillas_v8.md:495 y :751 (Anexo B); contrastado con MTC Manual de Hidrologia, Hidraulica y Drenaje, num. 4.1.1.3.7 c), pag. impresa 80 (PDFPAGE 83) y pag. impresa 111 (PDFPAGE 114).

Hoja de ruta linea 751: "G = 9.8                             # m/s2", dentro del bloque "# ===== Manual de Hidrologia (RD 20-2011-MTC/14) =====" e inmediatamente debajo de "LAUSHEY_K = 3.1 ... d50 = V^2/(3.1*g), metrico (4.1.1.3.7 c)"; linea 495: "d50 en m, V en m/s, g = 9.8 m/s2". grep de "9.81" sobre las 911 lineas del documento: cero coincidencias, tal como dice el auditor. Codigo: constantes_normativas.py:51-56 (G_LAUSHEY = 9.8, "Uso exclusivo de M6 (Laushey). La gravedad generica del resto del script (M4: tirante critico, control de salida) es constantes_fisicas.G = 9.81") y constantes_fisicas.py:52 ("G = 9.81   # m/s2; aceleracion estandar de la gravedad (CGPM, 1901)"). En el PDF del Manual, el numeral de Laushey (pag. impresa 80, PDFPAGE 83) define "g : Aceleracion de la gravedad (m/s2)" SIN fijarle valor; el unico g numerico del manual esta en otra formula, pag. impresa 111 (PDFPAGE 114): "g : Aceleracion de la gravedad (9.8 m/s2)".

**`R48-028` — hallazgo `HR-07` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* docs/hoja_de_ruta_alcantarillas_v8.md:83, :87, :150 y :154 (verificacion interna del repo; ningun PDF de por medio).

Lei las cuatro lineas citadas: datos_sitio.py:94 "todo el corredor (el terraplen de ~5 km de la Fase 0-bis de la hoja de ruta, num. 150)"; :141 "(Sec. 0.4 de la hoja de ruta, num. 83)"; :184 "solo cita el Z que de ella resulta (num. 87)"; :209 "la hoja de ruta lo nombra en num. 87 solo para decir que NO se usa". En la hoja de ruta esos numeros son lineas: 83 = "**Aceleracion en roca.** Mapa **\"Isoaceleraciones Espectrales Suelo Tipo B...\"**", 87 = "No se usa el Z = 0.45 de E.030 para las fuerzas sobre el muro...", 150 = "**Demanda sismica de evaluacion:** a_max de Tr = 1000 anios (§0.6), mas M_w por declarar". El mismo prefijo designa numerales reales en el resto del repo (constantes_normativas.py: "num. 4.5.4", "num. 3.3", "num. 4.2, Cuadro 4.1"). El string SI llega al entregable: M11_reporte.py:997 emite "<dt>Trazabilidad</dt><dd>{_esc(d.trazabilidad)}</dd>". CORRECCION al auditor: la frase del terraplen no esta en la linea 152 sino en la 154 ("1. **El elemento en riesgo no es el cabezal: es el terraplen de 5 km.**"); la 152 es el encabezado "### Lo que significa". Verifique con git diff que ni la hoja de ruta ni datos_sitio.py cambiaron desde el SHA auditado 71b134f.

**`R48-029` — hallazgo `HR-08` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* docs/manifiesto_citas.md §11.a (lineas 370-383) y docs/auditoria_y_ruta_despliegue_v9.md, item (8) del prompt de cierre (lineas 509-518). Verificacion interna del repo.

Comprobado en el codigo: M5_verificaciones.py:140 "NUMERAL_V6 = \"3.1\"" y :438-440 lo entrega crudo ("numeral=NUMERAL_V6", "criterio_aplicado=None"); M11_reporte.py:738 emite "<th>Numeral</th>", :764 "umbral = f\"{_etiqueta_html('N')} constante normativa\"" y :765 "_td(_esc(v.numeral))" -- en la misma tabla donde M5:115 pone "NUMERAL_V1 = \"4.1.1.3.7 b)\"", que si es numeral MTC. ReferenciaNormativa (modelos.py:158-205) existe y compone "{numeral_norma} [hoja de ruta: {seccion_hoja_ruta}]", y grep en todo src/ devuelve exactamente cuatro usos: M5:134, M8:143, M9:179, M10:62. Grep de NUMERAL_MANNING, NUMERAL_ENTRADA y NUMERAL_SALIDA sobre src/, tests/, cli.py y gui/: solo la definicion, ningun uso; NUMERAL_CRITICO solo en M4_control.py:274, dentro del texto de una excepcion. La colision que alega el auditor tambien es real: constantes_normativas.py:154 cita "# num. 4.2, Cuadro 4.1" del Manual de Suelos y M4_control.py:182 llama "4.2" a la Sec. 4.2 de la hoja de ruta.

**`R48-030` — hallazgo `HR-10` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* docs/hoja_de_ruta_alcantarillas_v8.md, seis sitios: :60 (§0.1), :76 (§0.3), :351 (§3.4), :455 (Fase 5, V3), :679 (Tablero 1, fila 1.3) y :724 (Anexo A). El WSDOT Hydraulics Manual M 23-03.12 NO esta en normas/, asi que el valor 4.6 m/s en si queda NO VERIFICABLE.

Codigo: criterios_adoptados.py:749-773, "v_max_hdpe" y "v_max_tmc" con valor=4.6 y fuente "WSDOT Hydraulics Manual M 23-03.12 (abril 2026), Cap. 8, S8-6, Tabla 8-4 'Pipe Abrasion Levels', pp. 8-27/8-28"; M5_verificaciones.py:259-262, "...con cita de WSDOT Hydraulics Manual M 23-03.12, Cap. 8, Tabla 8-4 (el vacio que la hoja de ruta declaraba quedo cerrado)". Hoja de ruta, las seis filas que lo contradicen, todas apuntando a PPI/FHWA: :60 "Velocidades maximas en materiales flexibles | **PPI / FHWA** | [C] - valores por extraer"; :76 "Tabla N 10 no los cubre. Fuentes identificadas (PPI, FHWA); **valores numericos aun por extraer**"; :351 "**Uno:** velocidad maxima (fuente PPI/FHWA, valor por extraer)"; :455 "**TMC y HDPE: PPI/FHWA, valor por extraer**"; :679 "| 1.3 | Velocidades maximas admisibles para TMC y HDPE - **valores numericos** | PPI / FHWA | V3 para materiales flexibles |"; :724 "**Sin valor.** Fuente identificada (PPI/FHWA), valores por extraer". M11_reporte.py:425-486 (tableros_pendientes) lee los Tableros LITERALES del archivo de la hoja de ruta, de modo que la fila 1.3 entra al expediente tal cual. ls normas/ confirma que el WSDOT no esta; grep "velocidad" y "WSDOT" en auditoria_y_ruta_despliegue_v9.md: cero coincidencias.

**`R48-031` — hallazgo `C-01` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD Bridge Design Specifications, 9th ed. 2020, Tabla 3.4.1-2, pag. impresa 3-18 (pdfpage 72), leida en el PDF original con Read

La Tabla 3.4.1-2 (PDF pag. 72, cabecera '3-18') da, fila por fila de EV: 'Overall and Compound Stability' 1.00/N/A; 'Retaining Walls and Abutments' 1.35/1.00; MSE 1.35, 1.20, 1.35 (todas N/A); 'Rigid Buried Structure' 1.30/0.90; 'Rigid Frames' 1.35/0.90; 'Flexible Buried Structures' 1.50/0.90, 'Thermoplastic Culverts' 1.30/0.90, 'All others' 1.95/0.90; 'Soil Nail Walls' 1.00/N/A. En el repo, criterios_adoptados.py:1343 dice literalmente '"EV": {"max": 1.35, "min": 0.90},' y las lineas 1379-1380 dicen 'la tabla fuente da EV minimo 0.90, no 1.00'. El comentario de coherencia esta en criterios_adoptados.py:1227 ('Que Fase 8 y Fase 9 lean la misma declaracion...'), y M9_cabezal.py:858 (no :805) lee el mismo criterio.

**`R48-032` — hallazgo `C-02` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD 9th ed. 2020, Art. 12.6.6.3 y Tabla 12.6.6.3-1, pags. impresas 12-21/12-22 (pdfpage 1659-1660), leidas en el PDF original

Tabla 12.6.6.3-1 (PDF pag. 1660): 'Corrugated Metal Pipe / — / S/8 > 12.0 in.'; 'Thermoplastic Pipe / Under unpaved areas / ID/8 > 12.0 in.' y 'Under paved roads / ID/2 > 24.0 in.'; 'Reinforced Concrete Pipe / Under unpaved areas or top of flexible pavement / Bc/8 or Bc'/8, whichever is greater, > 12.0 in.'; con Bc = 'outside diameter or width of the structure (ft)'. El repo dice en criterios_adoptados.py:1101-1103: 'Exigir a concreto y a TMC el recubrimiento del material MENOS tolerante no puede quedar del lado inseguro, que es la unica direccion en que una analogia entre materiales puede fallar.' El catalogo propio (criterios_adoptados.py:1059-1060) declara 'max': {'concreto_reforzado': 2.70, 'tmc': 2.10, 'hdpe': 1.50} en diametro INTERIOR.

**`R48-033` — hallazgo `C-03` — AJUSTADO (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD 9th ed. 2020, Art. 12.6.6.3 y Tabla 12.6.6.3-1, pags. impresas 12-21/12-22 (pdfpage 1659-1660), leidas en el PDF original

El Art. 12.6.6.3 completo (PDF pags. 1659-1660) dice: 'The minimum cover, including a well-compacted granular subbase and base course, shall not be less than that specified in Table 12.6.6.3-1', y despues de la tabla solo agrega 'If soil cover is not provided, the top of precast or cast-in-place reinforced concrete box structures shall be designed for direct application of vehicular loads' y 'Additional cover requirements during construction shall be taken as specified in Article 30.5.5 of the AASHTO LRFD Bridge Construction Specifications'. La tabla da para concreto 'Bc/8 or Bc'/8, whichever is greater, > 12.0 in.' y, 'Under bottom of rigid pavement', '9.0 in.'. El repo dice en criterios_adoptados.py:1149-1154: 'AASHTO LRFD Art. 12.6.6.3 -- cobertura minima tipica 1.0 ft (~0.305 m) salvo diseno especial de armadura, de modo que la adopcion coincide practicamente con el tipico de AASHTO y la verificacion deberia confirmarla, no corregirla.'

**`R48-034` — hallazgo `C-04` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA HDS-5 3a ed. (FHWA-HIF-12-026, abril 2012), Sec. 2.2.5 'Allowable Headwater', apartado 'd. Agency Constraints', pag. impresa 2.10 (pdfpage 72), leida en el PDF original

PDF pag. 72, pie de pagina '2.10': 'd. Agency Constraints. Some state or local highway agencies place limits on the headwater produced by a culvert. For example, the headwater depth may not be allowed to exceed the barrel height or some multiple of the barrel height, expressed as HW/D. The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5. Although very low HW/D constraints will severely limit the flexibility inherent in culvert design, they must be followed unless a design exemption is granted.' La Sec. 2.2.5 arranca en pdfpage 71 = pag. impresa 2.9 (el indice del propio documento la lista en '2.9'). La pag. impresa 2.14 es pdfpage 76 y contiene la 'Figure 2.8. Concrete debris fins...' y la 'Sec. 2.3.3 Safety Assessment', nada de HW/D. El repo dice en criterios_adoptados.py:901-904: 'HDS-5 (FHWA) 3a ed., abril 2012, Sec. 2.2.5, pag. 2.14 - rango de HW/D de 1.0 a 1.5 para el diseno corriente. CITA CERRADA por verificacion externa contra el documento', y lo repite en docs/manifiesto_citas.md:279 ('Sec. 2.2.5, pag. 2.14').

**`R48-035` — hallazgo `C-05` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Interno al repo: src/criterios_adoptados.py:886-907 (HW_D_max) y :957-980 (remanso_derecho_via); src/modulos/M5_verificaciones.py:377-417; scratchpad/informe.json y memoria.txt

criterios_adoptados.py:890-893 dice 'Se adopta el extremo superior del rango que HDS-5 da para el diseno corriente, 1.0-1.5. El control gobernante del embalse sigue siendo la verificacion V5 (remanso dentro del derecho de via).' Y en :957-958: '"remanso_derecho_via": Criterio(valor=None,  # VACIO: bloquea V5 para todo punto'. M5_verificaciones.py:417 lo confirma: 'y no el metodo: mientras no exista, V5 no se declara cumplida'. informe.json lista 'remanso_derecho_via' en criterios.sin_valor_declarados, y memoria.txt lo repite en la linea 250 (no la 199 que citaba el auditor). Pero el MISMO campo, en :895-900, ya declara: 'SOBRE LA SENSIBILIDAD: la banda declarada es (1.2, 1.5), no el rango completo (1.0, 1.5) de la fuente. Se conserva a proposito ... y se deja dicho que es un SUBRANGO, para que nadie la confunda con lo que dice HDS-5'.

**`R48-036` — hallazgo `C-06` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA HDS-5 3a ed. (FHWA-HIF-12-026), Cap. III, pags. impresas 3.12 (pdfpage 94), 3.24 (pdfpage 106) y 3.43 (pdfpage 125); Tabla C.2, pag. C.6 (pdfpage 216)

Lei CA:848-885: la justificacion dice literalmente "Se adopta la SECCION LLENA (A = pi*D^2/4, R = D/4, V = Q/A) porque es la seccion para la que HDS-5 deriva esa expresion... que es el caso de control de salida por definicion", y el verificacion_pendiente es solo cualitativo ("verificar que el punto donde el control de salida GOBIERNE sea uno donde la hipotesis de seccion llena tenga sentido fisico"). La eleccion de seccion SI la respalda el documento: "In Equation 3.5 the hydraulic radius and velocity are full flow values" (pag. impresa 3.43, pdfpage 125). Pero los dos numeros de validez estan alli, literales: "Adequate results are obtained down to a headwater of 0.75D.  For lower headwaters, backwater calculations are required" (pag. impresa 3.12, pdfpage 94) y "If outlet control governs and the headwater depth (referenced to the inlet invert) is less than 1.2D... If the headwater depth falls below 0.75D, the approximate method should not be used" (pag. impresa 3.24, pdfpage 106). En M4:436-450 la unica guardia es un DatoInvalidoError si el criterio deja de valer "seccion_llena"; grep de 0.75D/1.2D sobre src/ y docs/ no devuelve ninguna comprobacion.

**`R48-037` — hallazgo `C-07` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA HDS-5 3a ed. (FHWA-HIF-12-026), Apendice C: Tabla C.2 en pag. impresa C.6 (pdfpage 216); pag. C.1 (pdfpage 211) y pag. C.2 (pdfpage 212)

CA:836-841 dice literal: "HDS-5 (FHWA) 3a ed., abril 2012, Apendice C, Tabla C.2, pag. C.2 - coeficientes de perdida de entrada; fila 'square edge with headwall', ke = 0.5. CITA CERRADA por verificacion externa contra el documento"; se repite en docs/manifiesto_citas.md:277 ("Apendice C, **Tabla C.2, pag. C.2**"). En el PDF, la pag. C.6 (pdfpage 216) abre con "Table C.2.  Entrance Loss Coefficients." y en el bloque "Pipe, Concrete" trae "Headwall or headwall and wingwalls / Square-edge  0.5" (y "Headwall or headwall and wingwalls square-edge  0.5" en el bloque de metal corrugado). La pag. C.1 (pdfpage 211) es la lista "Reference Tables: C.1 Manning's n For Small Natural Stream Channels / C.2 Entrance Loss Coefficients", y la pag. C.2 (pdfpage 212) es la continuacion del indice de charts ("11A, 11B Headwater Depth for Inlet Control, Single Barrel Box Culverts...").

**`R48-038` — hallazgo `C-08` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* MTC EG-2013 (Revisada y Corregida a Junio 2013), Subseccion 508.07, pag. impresa 984 (pdfpage 992); pag. impresa 982 = pdfpage 990

Lei CA:1138 ("508.07, pag. 982, literal, 'La altura de relleno minimo desde la clave de la tuberia hasta el nivel de la subrasante sera de 0,30 m.'"), CA:1081, CN:177 ("# m, clave a subrasante (508.07, pag. 982)"), manifiesto 254, 607 y 609, y memoria_perfil.txt:142. En el PDF, la pdfpage 992 lleva encabezado "...984" y contiene "508.07 Colocacion del relleno alrededor de la estructura" y, al pie, "La altura de relleno minimo desde la clave de la tuberia hasta el nivel de la subrasante sera de 0,30 m." La pdfpage 990 lleva encabezado "...982" y contiene "Diametro 1200 mm debe ser 124 kPa (18 psi) / Diametro 1500 mm debe ser 97 kPa (14 psi)" y "b. Calidad de los tubos de polietileno de alta densidad (PAD o HDPE)".

**`R48-039` — hallazgo `C-09` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* MTC EG-2013, Subsecciones 507.05 y 507.06 en pag. impresa 973 (pdfpage 981) y 507.08 en pag. impresa 974 (pdfpage 982); 506.02 en pag. impresa 959 (pdfpage 967)

CA:1145 dice "las Subsecciones 507.05, 507.06 y 507.08 (pags. 969-970) remiten a ASTM A-807 para TMC", repetido en manifiesto 256 y 607 y en memoria_perfil.txt:142. En el PDF: pdfpage 981 contiene "507.05 Preparacion del terreno base / El terreno base se preparara de acuerdo con la norma ASTM A-807..." y "507.06 Solado / El solado se construira de acuerdo con la especificacion ASTM A-807..."; pdfpage 982 (encabezado "...974") contiene "507.08 Relleno / ...se ejecutara de acuerdo a la especificacion ASTM A-807...". Las pags. impresas 969-970 (pdfpage 977-978) son el arranque de la Seccion 507: "507.01 ... 507.02 Los materiales... se seguira la especificacion ASTM A-929 y AASHTO M-36 / ASTM A-760".

**`R48-040` — hallazgo `C-10` — AJUSTADO (MEDIA, NO VERIFICABLE)**

*Dónde se miró:* MTC Manual de Suelos, Geologia, Geotecnia y Pavimentos (abril 2014), num. 4.5.4 "Sub rasante", pag. impresa 42 (pdfpage 43) y num. 9.1(3), pag. impresa 89 (pdfpage 90)

CA:908-919 dice, literal: "El numeral 4.5.4 regula la separacion frente al NIVEL FREATICO, no frente a un nivel transitorio de avenida. Se aplica POR ANALOGIA por ser el unico parametro normativo nacional que protege la subrasante de la saturacion. La analogia es conservadora y debe declararse en la memoria", con etiqueta [N->]. El numeral, leido entero, solo dice: "El nivel superior de la sub rasante debe quedar encima del nivel de la napa freatica como minimo a 0.60 m... a 0.80 m... a 1.00 m... y, a 1.20 m... En caso necesario, se colocaran subdrenes o capas anticontaminantes y/o drenantes o se elevara la rasante hasta el nivel necesario" (pag. impresa 42); 9.1(3) repite lo mismo (pag. impresa 89). Nada sobre resguardo hidraulico ni sobre avenidas.

**`R48-041` — hallazgo `C-11` — REFUTADO (OK, CONFIRMA)**

*Dónde se miró:* Interno al repo: src/criterios_adoptados.py:908-918, src/modulos/M5_verificaciones.py:359, src/modulos/M7_geometria.py:331; memorias generadas en scratchpad/

CA:916 dice literalmente "analogia es conservadora y debe declararse en la memoria". El mecanismo que lo lleva alli NO es un accidente: M5_verificaciones.py:359 y M7_geometria.py:331 contienen ambos la linea `ca.valor(CRITERIO_RESGUARDO)      # registra el uso; "segun_CBR" no es numerico`, un llamado puesto EXPRESAMENTE para inscribirlo en _USADOS. Es cierto que `grep -c resguardo_HW` = 0 en memoria.txt, memoria_perfil.txt, memoria.html y memoria_perfil.html, pero informe.json muestra por que: los cuatro puntos traen `"bloqueos": [{"fase": "Fase 2 - Clasificacion y TR (M1)", ... "campo": "luz_m", "mensaje": "Falta el dato 'luz_m'..."}]`. En el render forzado del mismo repo el criterio SI sale: mem_forzada_exp.txt imprime "N→ resguardo_HW_subrasante  Concepto Resguardo entre nivel de agua a la entrada y subrasante  Valor segun_CBR  Justificacion El numeral 4.5.4 regula la separacion frente al NIVEL FREATICO...".

**`R48-042` — hallazgo `C-12` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Interno al repo (src/criterios_adoptados.py:386-472 y :1988) contrastado con MTC Manual de Puentes, Tablas 2.4.3.11.2.1.1-1 (pag. impresa 122 / PDFPAGE 123) y 2.4.3.11.2.1.2-1 (pag. impresa 123 / PDFPAGE 124)

`grep -rn clase_sitio src/` devuelve un solo llamado ejecutable: CA:1988 `valor("clase_sitio")`, y esta dentro de `if __name__ == "__main__":` (CA:1986). Ningun modulo de src/modulos/ lo invoca, de modo que nunca entra en _USADOS: `grep clase_sitio` = 0 en memoria.txt, memoria_perfil.txt, informe.json y TAMBIEN en mem_forzada_exp.txt (a diferencia de R48-041, ningun render lo rescata). El Manual de Puentes confirma la lectura de la tabla: fila "F2 * * * * *" y Nota 2 "Llevar a cabo investigaciones geotecnicas especificas del sitio y análisis de respuesta dinámica de sitio, para todos los sitios en sitio clase F" (impresa 123). PERO memoria.html sí trae el fondo del asunto en el Tablero 1, item 1.1: "VERIFICADO — la dispensa por periodo corto de la Clase F no existe... AASHTO exige estudio de respuesta de sitio específico para la Clase F, de forma incondicional. La cita se retira de la memoria y el uso de factores tabulados pasa a adopción [A] (§0.5)".

**`R48-043` — hallazgo `C-13` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD 9a ed. 2020, Tabla 3.10.3.1-1 "Site Class Definitions", pag. impresa 3-102 (PDFPAGE 156) y Tabla C3.10.3.1-1 (3-103, PDFPAGE 157); MTC Manual de Puentes, Tabla 2.4.3.11.2.1.1-1, pag. impresa 122 (PDFPAGE 123)

AASHTO, Tabla 3.10.3.1-1, fila F: "Soils requiring site-specific evaluations, such as: Peats or highly organic clays (H > 10.0 ft of peat or highly organic clay where H = thickness of soil); Very high plasticity clays (H > 25.0 ft with PI > 75); Very thick soft/medium stiff clays (H >120 ft)" — la licuefaccion no figura, y su comentario cierra la lista: Tabla C3.10.3.1-1, paso 1, "Check for the three categories of Site Class F in Table 3.10.3.1-1 requiring site-specific evaluation". La misma tabla lleva: "Exceptions: ... Site classes E or F should not be assumed unless the authority having jurisdiction determines that site classes E or F could be present at the site or in the event that site classes E or F are established by geotechnical data" (el Manual de Puentes lo traduce igual en su Tabla 2.4.3.11.2.1.1-1). En el repo lei CA:391-392 ("El sitio es Clase F por susceptibilidad a licuefaccion (arenas saturadas, NF a 1.4 m); esa parte no cambia") y CA:395-399 ("no esta en ninguna tabla ni nota de tabla de clases de sitio"). En AASHTO la licuefaccion se trata en C3.11.4 y en el Art. 10.5.4.2, no en 3.10.3.

**`R48-044` — hallazgo `C-14` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO M 170M-04 / ASTM C 76M-02, Sec. 1 SCOPE, Note 1 (M170M_OCR PDFPAGE 1); AASHTO M 36, clausula 1.3 y Note 9 (M36 PDFPAGE 2 y tabla 7); ASTM A760/A760M-10, clausula 1.4 (A760_OCR PDFPAGE 1)

M 170M Note 1: "This specification is a manufacturing and purchase specification only, and do[e]s not include requirements for bedding, backfill, or the relationship between fi[e]ld load condition and the strength classification of pipe". M 36, 1.3: "This specification does not include requirements for bedding, backfill, or the relationship between [e]arth cover load and sheet thickness of the pipe", y su Note 9 remite: "The purchaser should determine the required thickness... according to the design criteria in AASHTO's Standard Specifications for Highway Bridges, Division I, Section 12". A760 1.4: "Esta especificación no incluye requisitos para cama, relleno o la relación entre la carga de la cubierta de tierra y el espesor de la lámina de la tubería", y remite a "Práctica A798 / A798M". En el repo lei CA:1206-1209 ("PENDIENTE - AASHTO M-170M... Falta EXTRAER la tabla completa") y CA:1114-1123 ("M 170M clasifica por D-load (resistencia), NO por altura, de modo que no hay tabla clase-a-altura que extraer de ella. Este campo decia antes que el valor saldria de ahi; no sale").

**`R48-045` — hallazgo `C-16` — AJUSTADO (BAJA, CONFIRMA)**

*Dónde se miró:* Interno al repo: src/criterios_adoptados.py:37-45 (definicion de etiquetas), :749-773 (v_max_hdpe / v_max_tmc); docs/manifiesto_citas.md §10-bis (lineas 347-361) y §12 (lineas 421-434)

CA:44-45 define literalmente "C    Vacio normativo cubierto con fuente tecnica reconocida (FHWA, AASHTO)" y "A    Sin norma ni fuente unica. Adopcion declarada + sensibilidad obligatoria". CA:763 lleva `etiqueta="C",               # idem v_max_hdpe: Anexo A lo etiqueta [C]` y la fuente admite "La fuente NO fija techo absoluto para metal -- por encima de este valor exige mayor calibre o revestimiento, no prohibe el material. Se adopta 4.6 m/s como limite de diseno conservador". Manifiesto §10-bis: "Los dos valores salen de la **misma** tabla de la misma página... El 4.6 m/s del TMC es, por eso, adopción conservadora del proyecto y no un techo de la fuente" — y ESA seccion es una tabla del chequeo de citas, con `v_max_tmc` como fila propia (numeral "Cap. 8, S8-6, Tabla 8-4", pp. 8-27/8-28, [CA:762], etiqueta [C]).

**`R48-046` — hallazgo `C-17` — AJUSTADO (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD Bridge Design Specifications, 9th ed. 2020, Art. 5.10.1 y Tabla 5.10.1-1, pag. impresa 5-169 (PDFPAGE 528); Art. 5.10.1 en pag. 5-167 (PDFPAGE 526)

Lei la pagina 528 del PDF original con Read: "Table 5.10.1-1-Minimum Cover for Main Reinforcing Steel (in.)", eje de columnas "Reinforcing Material Category / A / B / C", fila "Coastal | 3.0 | 2.0 | 2.0", y al pie "Category A-Uncoated reinforcing steel meeting AASHTO M 31M/M 31; Category B-Epoxy coated or galvanized meeting ASTM A775/A775M; Category C-Materials meeting AASHTO M 334M/M 334". El encabezado del articulo (PDFPAGE 526, pag. 5-167) dice ademas: "Cover for prestressing and reinforcing steel shall not be less than that specified in Table 5.10.1-1 and modified for W/CM ratio", con factores "For W/CM <= 0.40 ... 0.8 / For 0.40 < W/CM < 0.50 ... 1.0 / For W/CM >= 0.50 ... 1.2". En el repo lei src/criterios_adoptados.py:1501-1532: valor {contra_suelo: 75.0, suelo_intemperie_ge_3_4: 75.0, suelo_intemperie_le_5_8: 75.0} y fuente "Tabla 5.10.1-1, pag. 5-169, categoria de exposicion 'ambiente costero'"; el criterio figura en scratchpad/informe.json bajo criterios.usados.

**`R48-047` — hallazgo `C-18` — AJUSTADO (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD 9th ed. 2020: C5.1 pag. 5-1 (PDFPAGE 360); Art. 5.5.4.2 pags. 5-29 a 5-32 (PDFPAGE 388-391); Eq. 5.7.3.3-3 pag. 5-67 (PDFPAGE 426); Eqs. 5.7.3.4.2-1/-2/-3 pag. 5-70 (PDFPAGE 429)

Lei la pagina 429 del PDF con Read: "For sections containing at least the minimum amount of transverse reinforcement specified in Article 5.7.2.5, the value of beta may be determined by Eq. 5.7.3.4.2-1" y, a continuacion, "When sections do not contain at least the minimum amount of shear reinforcement, the value of beta may be as specified in Eq. 5.7.3.4.2-2", con beta = [4.8/(1+750*eps_s)]*[51/(39+s_xe)]; theta = 29 + 3500*eps_s es unica. En C5.1 (PDFPAGE 360, pag. 5-1) el texto dice literalmente "These specifications use kips and ksi units" y da la tabla de conversion "N, psi -> N, ksi: 1 -> 0.0316"; en la pag. 5-68 bv y dv se definen "(in.)". Art. 5.5.4.2 da "normal weight concrete .... 0.90" para "tension-controlled reinforced concrete sections" (5-29) y para "For shear and torsion in reinforced concrete sections" (5-30). En el repo lei src/criterios_adoptados.py:1586-1633: "beta": "4.8 / (1 + 750*epsilon_s)" sin condicion de aplicabilidad, "Vc_kN": "0.0316*beta*lambda*raiz(f_c_prima)*bv*dv", y fuente "Arts. 5.5.4.2 (pag. 5-32) y 5.7.3.4.2 / 5.7.3.3 / 5.7.2.8 (pags. 5-70 a 5-243)".

**`R48-048` — hallazgo `C-19` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* Verificacion INTERNA del repo (no hay PDF): docs/manifiesto_citas.md seccion 8, linea 296, contra src/criterios_adoptados.py y tests/test_manifiesto_citas.py

docs/manifiesto_citas.md:296 dice literal: "| `FS_flotacion = None` - FS de V7, SigmaW >= FS*U | Sec. 12 (no incorporada por el Manual de Puentes) | AASHTO LRFD | [CA:842](src/criterios_adoptados.py:842) | [C] |". Lei src/criterios_adoptados.py:842 y es "exactamente eso",  -- la ultima linea del campo `fuente` del criterio `ke_entrada` (HDS-5 Tabla C.2). En :1215-1228 esta el bloque de comentario "# 'FS_flotacion' SE RETIRO. Declaraba el factor de seguridad global de SigmaW >= FS*U..."; importando el modulo, `'FS_flotacion' in ca.CRITERIOS` devuelve False, y M5_verificaciones.py:467 dice "El criterio 'FS_flotacion' que sostenia el umbral se retiro". En tests/test_manifiesto_citas.py:105-115, `_clasificadas()` hace `candidatos = [s for s in _simbolos_citados(fila) if s in bloques]` y manda a `prosa` toda fila sin simbolo vivo; sobre `prosa` solo corren las comprobaciones de archivo existente, rango y linea no vacia.

**`R95-020` — hallazgo `H-05` — SE SOSTIENE (CRITICA, CONTRADICE)**

*Dónde se miró:* MTC Manual de Puentes (2018), num. 2.4.3.3.2 (pag. impresa 109), num. 2.4.3.11.1 (121), Tabla 2.4.5.3.1-2 (143), num. 2.8.1.3A.6.2 (280), num. 2.11 (505); indice general pags. 36-38

Lei src/criterios_adoptados.py:1124-1128, campo `fuente` de 'h_relleno_min_concreto_tmc': «(2) MANUAL DE PUENTES (RD 041-2016-MTC/14) -- nunca incorporo la Seccion 12 de AASHTO LRFD ('Buried Structures and Tunnel Liners'): su indice salta de 2.11 (Muros de Contencion y Estribos) a 2.12 (Disposiciones Constructivas). Vacio absoluto sobre conductos enterrados.» (repetido en docs/manifiesto_citas.md:182 y :606; la linea :184 que cita el auditor esta en blanco). Abri el PDF original en la pagina PDF 110 = pag. impresa 109 y leo el num. 2.4.3.3.2 «Componentes Enterrados (3.6.2.2 AASHTO): El incremento por carga dinamica para alcantarillas y otras estructuras enterradas, en porcentaje, se debera tomar como: IM = 33(1.0 - 0.125D_E) >= 0%», con «D_E = profundidad minima de la cubierta de tierra sobre la estructura (ft)». Verifique ademas en MTC_PUENTES.txt (PDFPAGE 122 = impresa 121) «No se requerira considerar acciones de sismo sobre alcantarillas tipo cajon y otras estructuras totalmente enterradas», y en PDFPAGE 144 = impresa 143 las filas EV «Estructura rigida enterrada 1.30 / 0.90» y «Estructuras flexible enterradas ... 1.50 / 1.30 / 1.95».

**`R95-021` — hallazgo `H-07` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* MTC Manual de Puentes (2018), num. 2.4.3.8.1 y 2.4.3.8.2, pagina impresa 113

En MTC_PUENTES.txt, PDFPAGE 114 (cabecera «Pagina 113»): «2.4.3.8.2 Subpresiones (3.7.2 AASHTO). La subpresion (flotabilidad) se debera considerar como una fuerza de levantamiento, tomada como la sumatoria de las componentes verticales de las presiones hidrostaticas, segun lo especificado en el Articulo 2.4.3.8.1 (3.7.1 AASHTO)...», y en 2.4.3.8.1, misma pagina: «La presion se debera calcular como el producto entre la altura de la columna de agua sobre el punto considerado, y el peso especifico del agua.» Ninguno de los dos asigna valor a ese peso especifico. Lei docs/manifiesto_citas.md:161: «GAMMA_AGUA_KN_M3 = 9.81 kN/m3 (subpresion) | num. 2.4.3.8.2 | Manual de Puentes | [CN:35] | [N]»; src/constantes_normativas.py:35 es hoy la linea «#» vacia dentro de la cita literal de V_MIN, y CN:58-62 dice «GAMMA_AGUA_KN_M3 ya no vive aqui... El num. 2.4.3.8.2 del Manual de Puentes dice como se calcula la subpresion, no cuanto pesa el agua». El valor esta en src/constantes_fisicas.py:59, derivado: `GAMMA_AGUA_KN_M3 = GAMMA_AGUA / N_POR_KN`.

**`R95-022` — hallazgo `H-10` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* MTC Manual de Puentes (2018), num. 2.8.1.3.1.2c y sus figuras -1 y -2, paginas impresas 272, 273 y 274

En MTC_PUENTES.txt el encabezado «2.8.1.3.1.2c Consideraciones para Zapatas Apoyadas en Taludes. (10.6.3.1.2c AASHTO)» cae en PDFPAGE 273 = pag. impresa 272; «Figura 2.8.1.3.1.2c-1 Factores de capacidad de carga modificados para zapatas en suelos cohesivos y sobre o adyacentes a terreno inclinado (Meyerhof 1957). Figura (10.6.3.1.2c-1 AASHTO)» en PDFPAGE 274, cabecera «Pagina 273»; «Figura 2.8.1.3.1.2c-2 ... en suelos no cohesivos y sobre o adyacentes a terreno inclinado (Meyerhof 1957). (Figura 10.6.3.1.2c-2 AASHTO)» en PDFPAGE 275, cabecera «Pagina 274». Lei src/criterios_adoptados.py:1467-1468: fuente=«PENDIENTE - Manual de Puentes num. 2.8.1.3.1.2c, figuras 2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), pags. 272-273», y el mismo rango en M9_cabezal.py:1064-1066, constantes_normativas.py:262 y docs/manifiesto_citas.md:177 y :178.

**`R95-023` — hallazgo `H-14` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* MTC Manual de Puentes (2018), num. 2.8.1.1.14.2 completo: 2.8.1.1.14.2.1 (pag. impresa 254) y 2.8.1.1.14.2.2 (pag. impresa 255)

En 2.8.1.1.14.2.2, PDFPAGE 256 = pag. impresa 255: «Donde el muro es capaz de desplazamientos de 1.0 a 2.0 in o mas durante el evento sismico de diseno, kh puede ser reducido a 0.5kh0 sin llevar a cabo un analisis de la deformacion mediante el metodo Newmark o una version simplificada de el.» Barri con grep todo el numeral 2.8.1.1.14 (lineas 18069-18300 del .txt): cero apariciones de «Tabla», de «25 mm» y de «50 mm». PERO en 2.8.1.1.14.2.1, PDFPAGE 255 = pag. impresa 254: «kh0=FpgaPGA = As donde kh0 es el coeficiente de aceleracion sismico horizontal asumiendo que el desplazamiento del muro sea cero». Lei src/constantes_normativas.py:241-250 («Las DOS filas son [N]: el numeral las fija», NUMERAL_FACTOR_MURO = «2.8.1.1.14.2»), criterios_adoptados.py:481-483 y M9_cabezal.py:295-298.

**`R95-024` — hallazgo `H-20` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* MTC Manual de Puentes (2018), Seccion 2.9 SUPERESTRUCTURAS (pag. impresa 331), pag. impresa 337 (= num. 2.9.1.4.4.3) y num. 2.9.1.5.6.3.4.2 (pag. impresa 387)

En MTC_PUENTES.txt, PDFPAGE 332, cabecera «Pagina 331»: «2.9 SUPERESTRUCTURAS / 2.9.1 Superestructuras de Concreto / 2.9.1.1 Generalidades»; el indice lo confirma («2.9 SUPERESTRUCTURAS ... 331»). PDFPAGE 338 = pag. impresa 337 es control de fisuracion por distribucion de armadura, sin ninguna remision a la Seccion 5 de AASHTO. Lei src/modulos/M9_cabezal.py:1439-1440 («AASHTO LRFD Seccion 5 (Sec. 9.4, via Manual de Puentes Seccion 2.9, pag. 337)») y docs/manifiesto_citas.md:180 y :299, que repiten «pag. 337». Pero «Sec. 9.4» NO es del Manual: es la seccion de la hoja de ruta del propio proyecto, docs/hoja_de_ruta_alcantarillas_v8.md:626 «### 9.4 Refuerzo y durabilidad -- Flexion y corte por AASHTO LRFD Seccion 5», en la misma serie que NUMERAL_9_2 = «Sec. 9.2» y NUMERAL_9_3 = «Sec. 9.3 (E.050)» (M9_cabezal.py:184-190).

**`R95-025` — hallazgo `H-21` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Defecto interno del repo: docs/manifiesto_citas.md, bloque §3 (Manual de Puentes), filas 161, 168, 172, 173 y 181. No aplica PDF.

Abrí las cinco líneas citadas y ninguna contiene lo que la fila le atribuye. src/constantes_normativas.py:35 es «#», una línea de comentario vacía dentro de la cita literal de V_MIN, y las líneas 58-62 del mismo archivo dicen «GAMMA_AGUA_KN_M3 ya no vive aqui: es una constante FISICA»; el valor está en src/constantes_fisicas.py:59 («GAMMA_AGUA_KN_M3 = GAMMA_AGUA / N_POR_KN»). M8_estructural.py:138-139 y :148 son el comentario sobre las Secciones 505/506/507/508 del EG-2013 y el cierre de NUMERAL_8_1; empuje_flotacion_kn_m() está en M8:197-209. M8:35-36 hablan de CAMA_RELLENO_LATERAL y M8:199-200/:209-210 son el docstring y el return de la flotación; la Sec. 12 de AASHTO aparece en M8:41, :326 y :336. M9_cabezal.py:220 es «CRITERIO_GAMMA_CONCRETO = "peso_especifico_concreto_kn_m3"» (el PGA está en M9:206 y M9:187), y criterios_adoptados.py:400-403 hablan de la dispensa que se le atribuía a AASHTO, no del Manual — esa frase está en CA:429-430 — mientras que el criterio 'clase_sitio' lleva etiqueta="A" en CA:388.

**`R95-026` — hallazgo `H-22` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* Manual de Puentes (MTC), num. 2.4.3.11.2.1.1, Tabla 2.4.3.11.2.1.1-1 y su bloque «Excepciones», página impresa 122 (PDFPAGE 123)

Verifiqué la página sobre la imagen del PDF original (PDFPAGE 123, pie «Página 122»): la fila F dice «Suelos que requieren evaluaciones específicas de sitio, tales como:» seguida de exactamente tres viñetas — «Turbas o arcillas altamente orgánicas (H > 10 ft…)», «Arcillas de alta plasticidad (H> 25 ft con PI > 75)» y «Estratos de Arcillas de buen espesor, blandas o semirrígidas (H > 120 ft)» — ninguna sobre suelos licuables. Debajo, en letra pequeña: «Excepciones: … Las clases de Sitio E o F no serán supuestas a no ser que la Entidaddetermine la clase de sitio E o F o estas sean establecidas por datos geotécnicos» (el pegado «Entidaddetermine» está en el PDF, no es artefacto de extracción). El repo afirma en src/criterios_adoptados.py:391-392 «El sitio es Clase F por susceptibilidad a licuefaccion (arenas saturadas, NF a 1.4 m); esa parte no cambia», y en CA:359 llama a PERFIL_SUELO_PRESUNTO «una presuncion de expediente». Un grep de «Excepcion|no seran supuestas|Entidad determine» sobre src/ y docs/manifiesto_citas.md solo devuelve encabezados de docstring de módulo: el bloque no está recogido en ninguna parte.

**`R95-027` — hallazgo `H-02` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* NTE E.060 Concreto Armado, num. 4.3.1, Tabla 4.4 «Requisitos para concreto expuesto a soluciones de sulfatos», fila Moderada, página impresa 38 (PDFPAGE 38)

La columna «Tipo de Cemento» de la fila «Moderada**» (0,1 ≤ SO4 < 0,2; 150 ≤ SO4 < 1500) dice literalmente «II, IP(MS), IS(MS), P(MS), I(PM)(MS), I(SM)(MS)» — seis designaciones. src/constantes_normativas.py:289 escribe «(0.10, 0.20, "II/IP(MS)/IS(MS)", 0.50, 28),» — tres. docs/hoja_de_ruta_alcantarillas_v8.md:325 sí transcribe las seis, y docs/manifiesto_citas.md:222 arrastra la versión recortada etiquetada [N] contra «Tabla 4.4», sin marca de recorte. Un grep de «P(MS)|I(PM)|I(SM)» sobre todo el repo solo devuelve esas cuatro líneas.

**`R95-028` — hallazgo `H-07` — AJUSTADO (BAJA, CONTRADICE)**

*Dónde se miró:* NTE E.060 Concreto Armado, Art. 7.7.5 «Ambientes corrosivos», Art. 7.7.5.1, página impresa 55 (PDFPAGE 55)

Leí la imagen del PDF original: «7.7.5.1 En ambientes corrosivos u otras condiciones severas de exposición, debe aumentarse adecuadamente el espesor del recubrimiento de concreto y debe tomarse en consideración su densidad y porosidad o debe disponerse de otro tipo de protección.» La secuencia «aumentar adecuadamente» no aparece. El repo la entrecomilla en tres sitios: src/constantes_normativas.py:297 («# "aumentar adecuadamente"») y :298 («el articulo dice "aumentar adecuadamente" y no fija cuanto»); src/modulos/M9_cabezal.py:1224 y :1231, este último dentro del texto que va a la memoria («El articulo dice 'aumentar adecuadamente' y no fija cuanto»); y docs/manifiesto_citas.md:227. Hay un cuarto sitio que el auditor no listó: src/criterios_adoptados.py:1528-1529, en la verificación pendiente de 'recubrimiento_aashto_mm'.

**`R95-029` — hallazgo `H-12` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* NTE E.060 Concreto Armado, Arts. 11.10.10.1 y 11.10.10.2, página impresa 104 (PDFPAGE 104); Arts. 11.10.7-11.10.8, impresas 103-104; Art. 11.5.6.1, impresa 91 (PDFPAGE 91)

Sobre la imagen del PDF de la página 104: «11.10.10.2 La cuantía de refuerzo horizontal para cortante no debe ser menor que 0,0025 y su espaciamiento no debe exceder tres veces el espesor del muro ni de 400 mm.» — texto completo, sin umbral. Los disparadores de E.060 para muros están en otros artículos: «11.10.7 Donde Vu sea menor que 0,085√f'c·Acw…», «11.10.8 Donde Vu sea mayor que 0,085√f'c·Acw…» y «11.10.10.1 Donde Vu exceda la resistencia al corte φVc…». El 0,5 φVc pertenece a «11.5.6.1 Debe colocarse un área mínima de refuerzo para cortante, Av min, en todo elemento de concreto armado sometido a flexión… donde Vu exceda de 0,5 φVc, excepto en: (a) Losas y zapatas» (impresa 91); un grep de «0,5» cruzado con Vc/cortante en E060.txt solo da esa línea y la de 11.12. src/criterios_adoptados.py:1542-1544 dice «el Art. 11.10.10.2 lo sube a 0.0025 cuando la demanda de cortante supera el umbral que ese articulo define (del orden de Vu > 0.5*phi*Vc)».

**`R95-030` — hallazgo `H-15` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* NTE E.060 Concreto Armado, Cap. 14 MUROS: Arts. 14.3.1 y 14.3.2 (pag. impresa 133 = PDFPAGE 133) y Arts. 14.8.2 / 14.8.3 (pag. impresa 134 = PDFPAGE 134); Art. 11.10.10.5 (pag. impresa 104 = PDFPAGE 104). Verificado sobre el PDF original con Read pages 133-134 y 104.

PDF pag. 133: «14.3.1 El refuerzo minimo vertical y horizontal debe cumplir con las disposiciones de 14.3...» y «14.3.2 Los muros con un espesor mayor que 200 mm, excepto los muros de sotanos, deben tener el refuerzo en cada direccion colocado en dos capas paralelas a las caras del muro.» PDF pag. 134: «14.8.2 El refuerzo minimo sera el indicado en 14.3...» y «14.8.3 El acero por temperatura y contraccion debera colocarse en ambas caras para muros de espesor mayor o igual a 250 mm.» En el repo lei M9_cabezal.py:1353-1377: el unico umbral es `return espesor >= ESPESOR_TEMPERATURA_DOS_CARAS - TOL_UMBRAL_NORMATIVO` (0.250 m, CN:319) y la nota imprime «Acero por temperatura en UNA cara: espesor ... < 0.250 m (E.060 Art. 14.8.3)». `grep -rn '14\.3\.2|dos capas'` sobre src/ y docs/ (excluido docs/auditorias) no devuelve NINGUN hit: el Art. 14.3.2 no existe en el repo ni como constante, ni como criterio, ni como vacio declarado.

**`R95-031` — hallazgo `H-13` — AJUSTADO (ALTA, CONTRADICE)**

*Dónde se miró:* NTE E.060 Concreto Armado, Arts. 11.10.10.2 / 11.10.10.3 y ec. (11-32), pag. impresa 104 = PDFPAGE 104; Art. 14.2.4, pag. impresa 133. Verificado sobre el PDF original con Read page 104.

PDF pag. 104: «11.10.10.3 La cuantia de refuerzo vertical para cortante, rho_v, no debe ser menor que: rho_v = 0,0025 + 0,5 (2,5 - hm/lm) (rho_h - 0,0025) >= 0,0025 (11-32) ... pero no necesita ser mayor que el valor de rho_h requerido por 11.10.10.1.» Y pag. 133: «14.2.4 El diseno para cortante debe cumplir con lo estipulado en 11.10.» En el repo lei M9_cabezal.py:1322-1325: «El escalon del Art. 11.10.10.2 es de la cuantia HORIZONTAL; en vertical, `cortante_alto=True` no cambia el minimo del Art. 14.3.1», y el codigo lo implementa en :1330 con `if cortante_alto and direccion == "horizontal":`, de modo que la rama vertical devuelve 0.0015. El criterio vacio de src/criterios_adoptados.py:1534-1584 esta acotado por escrito a «la cuantia horizontal minima de 0.0020 a 0.0025» y no menciona el 11.10.10.3 en ningun punto.

**`R95-032` — hallazgo `H-19` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna: docs/manifiesto_citas.md, bloque 5 (lineas 214-234) contra docs/hoja_de_ruta_alcantarillas_v8.md:56, :62-68 y :626-631; titulos de capitulo de NTE E.060 verificados en PDFPAGE 87, 133 y 190.

manifiesto_citas.md:216-217: «Entra al proyecto solo por la excepcion declarada de durabilidad y recubrimientos (Via 1 de Sec. 0.2); el diseno estructural es de AASHTO.» Bajo ese encabezado, las filas 228, 230, 231, 232, 233 y 234 llevan [N] y citan Arts. 14.3.1, 14.8.3, 14.3.3 (dos filas) y 22.10 (dos filas) -Caps. 14 y 22, no Cap. 4 ni Art. 7.7-. hoja_de_ruta:56 acota «RNE E.060, Cap. 4 y Art. 7.7 | [N] por excepcion declarada (0.2)» y :68 «E.060 Cap. 4 y Art. 7.7 si aplican, por ser especificacion de materiales». Pero la MISMA hoja de ruta, en :630-631, si trae esos articulos al proyecto: «Referencia de cuantias minimas (E.060 Art. 14.3.1, pag. 133)... acero por temperatura en ambas caras si espesor >= 250 mm (Art. 14.8.3); espaciamiento <= 3h y <= 400 mm (Art. 14.3.3)» y «Alternativa en concreto ciclopeo (E.060 Art. 22.10, pags. 194-195)».

**`R95-033` — hallazgo `H-20` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna del repo: docs/manifiesto_citas.md:231 contra src/modulos/M9_cabezal.py (sin documento normativo externo).

manifiesto_citas.md:231 dice literalmente: «`ESPACIAMIENTO_MAX_VECES_ESPESOR = 3.0` (<= 3h) | Art. 14.3.3 | E.060 | [CN:321](src/constantes_normativas.py:321), [M9:1276-1277](src/modulos/M9_cabezal.py:1276) | [N]». Lei esas lineas: M9_cabezal.py:1276 es `minima = cuantia_minima(direccion=direccion)` y :1277 `codigo = "R1" if direccion == "horizontal" else "R2"`, dentro de `verificar_cuantia` (1265-1285). `grep -n ESPACIAMIENTO_MAX_VECES_ESPESOR src/modulos/M9_cabezal.py` devuelve solo dos lineas: 148 (import) y 1385 (`return min(ESPACIAMIENTO_MAX_VECES_ESPESOR * espesor, ESPACIAMIENTO_MAX_ABSOLUTO)`, dentro de `espaciamiento_maximo`).

**`R95-034` — hallazgo `H-22` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna del repo: docs/manifiesto_citas.md:228 contra src/modulos/M9_cabezal.py (sin documento normativo externo).

manifiesto_citas.md:228 remata la fila con «aplicado como rho_diseno = max(rho_calculado, rho_minimo) en `M9.cuantia_de_diseno`» y ancla en «[CN:317](src/constantes_normativas.py:317), [M9:1281](src/modulos/M9_cabezal.py:1281)». Lei la linea 1281: es `valor_obtenido=cuantia_provista,`, dentro de `verificar_cuantia` (1265-1285). `cuantia_de_diseno` empieza en :1288 y el max() efectivo es el bloque `if cuantia_calculada >= minima - TOL_UMBRAL_NORMATIVO: adoptada, gobierna = cuantia_calculada, "calculo" / else: adoptada, gobierna = minima, "minimo_normativo"`, lineas 1337-1340.

**`R95-035` — hallazgo `H-21` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna del repo: docs/manifiesto_citas.md:233 (bloque §5, E.060) contra src/modulos/M9_cabezal.py

Lei docs/manifiesto_citas.md:233: «| `CICLOPEO_FC_MATRIZ_MIN = 10.0` MPa | Art. 22.10, pags. 194-195 | E.060 | [CN:326](src/constantes_normativas.py:326), [M9:1303](src/modulos/M9_cabezal.py:1303) | [N] |». Lei src/modulos/M9_cabezal.py:1303, que dice literalmente «    dos minimos horizontales -- 0.0020 (Art. 14.3.1) y el escalon del», linea interior del docstring de `cuantia_de_diseno` (cuantia minima de muros, Art. 14.3.1 / 11.10.10.2). `CICLOPEO_FC_MATRIZ_MIN` solo aparece en M9_cabezal.py en las lineas 143 (import), 1418 y 1421, dentro de `verificar_ciclopeo` (def en la linea 1406, docstring «R4 / R5: alternativa en concreto ciclopeo, E.060 Art. 22.10 (pags. 194-195)»). El ancla [CN:326] si es correcta: constantes_normativas.py:326 = «CICLOPEO_FC_MATRIZ_MIN = 10.0               # MPa            Art. 22.10».

**`R95-036` — hallazgo `H-02` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* MTC EG-2013, Capitulo V, Subseccion 508.07 «Colocacion del relleno alrededor de la estructura», pagina impresa 984 (PDF 992). Contraste con la pagina impresa 982 (PDF 990).

Abri el PDF original con Read pages=990-992. La pag. PDF 992 lleva pie impreso «984» y contiene «508.07 Colocacion del relleno alrededor de la estructura» y, al final, «La altura de relleno minimo desde la clave de la tuberia hasta el nivel de la subrasante sera de 0,30 m.» La pag. PDF 990, pie impreso «982», contiene solo 508.02 «b. Calidad de los tubos de polietileno de alta densidad (PAD o HDPE)», «c. Inspeccion, muestreo y rechazo del material» y «d. Material para cama de asiento»; 508.05 esta en la 983. Lei las seis ubicaciones del repo y las seis dicen 982: constantes_normativas.py:177 «"hdpe":     0.30,               # m, clave a subrasante (508.07, pag. 982)»; criterios_adoptados.py:1081 «pag. 982, exige 0.30 m desde la clave hasta la» y :1138 «508.07, pag. 982, literal, ...»; manifiesto_citas.md:254, :607 y :609; hoja_de_ruta_alcantarillas_v8.md:522 «[N] 508.07/508.08, pag. 982».

**`R95-037` — hallazgo `H-03` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna del repo: docs/manifiesto_citas.md:254 y :616 contra src/constantes_normativas.py:160 y :176-177 (la norma de fondo, EG-2013 508.07, pag. impresa 984, si existe y es literal)

Lei src/constantes_normativas.py:160, que dice literalmente «# sobre cuantos sentidos se cuenta el kilometro.» — comentario de cierre del bloque `CALICATAS_POR_SENTIDO` (Manual de Suelos, num. 4.2, Cuadro 4.1), sin ninguna relacion con el EG-2013. El valor esta en la 177: «"hdpe":     0.30,               # m, clave a subrasante (508.07, pag. 982)», dentro de `H_RELLENO_MIN` que abre en la 176. Un `grep -rn "altura de relleno m"` sobre todo el repo devuelve la cita textual solo en src/criterios_adoptados.py:1138-1139 y en los .md; en constantes_normativas.py no aparece en ninguna linea. La fila §6 del manifiesto (linea 239) si ancla bien el mismo valor en [CN:176].

**`R95-038` — hallazgo `H-13` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* MTC EG-2013, Capitulo V, Seccion 505: 505.03 (pag. impresa 950), 505.07 (951), 505.10 (952-953), 505.11 (953)

En EG2013.txt, con los marcadores PDFPAGE: «505.03 Material para solado y sujecion» cae en PDF 958 (pie impreso 950); «505.07 Solado» en PDF 959 (pie 951); «505.10 Sujecion» arranca al final de PDF 960 (pie 952) y su frase operativa cierra ya en PDF 961 (pie 953): «utilizada en el solado, hasta una altura no menor de un cuarto del diametro exterior del tubo.»; «505.11 Relleno — Una vez que la sujecion haya curado suficientemente, se efectuara el relleno de la zanja conforme a lo senalado la Seccion 502.» esta integra en PDF 961 (pie 953). Las cuatro ubicaciones del repo dicen lo mismo y lo lei una a una: constantes_normativas.py:209 «"numeral": "505.03/.07/.10/.11, pags. 950-951"», M8_estructural.py:141, manifiesto_citas.md:247 y hoja_de_ruta_alcantarillas_v8.md:561.

**`R95-039` — hallazgo `H-10` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* MTC EG-2013, Capitulo V, Seccion 507: 507.05 y 507.06 en pag. impresa 973 (PDF 981); 507.08 en pag. impresa 974 (PDF 982). Contraste con las paginas impresas 969 (PDF 977) y 970 (PDF 978).

Abri el PDF original con Read pages=981: pie impreso «973», y en el se leen «507.05 Preparacion del terreno base — El terreno base se preparara de acuerdo con la norma ASTM A-807 y lo indicado en la Subseccion 505.06...» y «507.06 Solado — El solado se construira de acuerdo con la especificacion ASTM A-807, empleando material de subbase granular segun la Seccion 402...». En el .txt, PDF 982 (pie 974) trae «507.08 Relleno — La zona de terraplen adyacente al tubo, con las dimensiones indicadas en el Proyecto, se ejecutara de acuerdo a la especificacion ASTM A-807 y lo indicado en la Seccion 502.» En cambio PDF 977 (pie 969) contiene «SECCION 507 / Tuberia metalica corrugada», 507.01 y el arranque de 507.02 a), y PDF 978 (pie 970) la «Tabla 507-01 Espesores Minimos de Alcantarillas Circulares y Abovedadas». Repo leido: criterios_adoptados.py:1145-1146 «las Subsecciones 507.05, 507.06 y 507.08 (pags. 969-970) / remiten a ASTM A-807 para TMC», manifiesto_citas.md:256 y :607, ambas con «507.05/.06/.08, pags. 969-970».

**`R95-040` — hallazgo `H-14` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* EG-2013, Seccion 505: num. 505.10 y 505.11 (pag. impresa 953, PDFPAGE 961) y 505.06 (pag. impresa 951, PDFPAGE 959); cadena de remision 502.09(c)(1) (pag. impresa 900, PDFPAGE 908) y 205.12(c)(1) (pag. impresa 193, PDFPAGE 201)

Lei src/constantes_normativas.py:207-208, que dice literalmente: «"sujecion_relleno_lateral": "Clase F hasta >= 1/4 del diametro exterior. Relleno Sec. 502 >= 95% MDS"». En el PDF, 505.11 dice completo: «Una vez que la sujecion haya curado suficientemente, se efectuara el relleno de la zanja conforme a lo senalado la Seccion 502.» (impresa 953 / PDFPAGE 961) — sin porcentaje alguno. La cadena remite a 502.09(c)(1): «Los niveles de densidad por alcanzar en las diversas capas del relleno son los mismos que se indican en la Subseccion 205.12(c) (1).» (impresa 900 / PDFPAGE 908), y 205.12(c)(1) fija «Di > 0,90 De (base y cuerpo)» y «Di > 0,95 De (corona)» (impresa 193 / PDFPAGE 201). El unico 95 % de la Seccion 505 esta en 505.06, preparacion del TERRENO BASE: «El material utilizado en el relleno debera clasificar como corona segun la Tabla 205-01 y su compactacion debera ser, como minimo, el 95% de la maxima obtenida en el ensayo modificado de compactacion (norma de ensayo MTC E 115).» (impresa 951 / PDFPAGE 959).

**`R95-041` — hallazgo `H-15` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* EG-2013, Seccion 506: 506.03 (pag. impresa 959, PDFPAGE 967), 506.07 (pag. impresa 960, PDFPAGE 968), 506.10 y 506.11 (pag. impresa 961, PDFPAGE 969)

Lei src/constantes_normativas.py:215: «"numeral": "506.03/.07/.10/.11, pags. 959-960"», replicado en docs/manifiesto_citas.md:248 y docs/hoja_de_ruta_alcantarillas_v8.md:562. En el PDF, la pagina con pie impreso 961 (PDFPAGE 969) contiene 506.09, 506.10 «Sujecion» — «…al mismo nivel de densidad exigido para el solado, hasta una altura no menor a 1/6 del diametro exterior de ella.» — y 506.11 «Relleno» — «El relleno posterior a lo largo de la tuberia satisfactoriamente colocada, se hara de acuerdo con lo especificado en la Seccion 502.». En 959 esta 506.03 («El solado y la sujecion se construiran con material para sub-base granular, cuyas caracteristicas deberan satisfacer lo establecido en la Seccion 402.») y en 960 esta 506.07 («de por lo menos 15 cm de espesor compactado […] su compactacion minima sera la que se especifica para la corona en la Subseccion 205.12(c) (1).»).

**`R95-042` — hallazgo `H-17` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* EG-2013, Seccion 508: 508.01/508.02 a) (pag. impresa 981, PDFPAGE 989), 508.02 d) (pag. impresa 982, PDFPAGE 990), 508.05 (pag. impresa 983, PDFPAGE 991), 508.07 (pag. impresa 984, PDFPAGE 992)

Lei src/constantes_normativas.py:225-226 («"cama_apoyo": "Arena gruesa, capas de 15 cm, espesor 15-30 cm (30 cm en roca o suelo blando)"») y :230 («"numeral": "508.05/.07, pags. 981-982"»). En el PDF, la «arena gruesa» esta solo en 508.02 d) Material para cama de asiento, pie impreso 982: «La cama de asiento estara constituida por arena gruesa, la cual sera conformada en capas de no mas de 0,15 m de espesor, y a todo lo ancho de la excavacion.» 508.05 esta en la 983: «El espesor estara entre 0,15 m y 0,30 m, no se admitira espesores menores a 0,15 m. Esta capa de material granular sera colocada sobre cualquier tipo de suelo de fundacion, con excepcion de suelos de baja capacidad portante o rocosos, en cuyo caso el espesor sera de 0,30 m.» — nunca nombra el material. 508.07 esta en la 984 y la 981 solo trae 508.01 y 508.02 a).

**`R95-043` — hallazgo `H-16` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* EG-2013, Seccion 507: 507.06 y arranque de 507.07 (pag. impresa 973, PDFPAGE 981), 507.07 arena y 507.08 (pag. impresa 974, PDFPAGE 982); pagina impresa 970 = PDFPAGE 978

Lei src/constantes_normativas.py:222: «"numeral": "507.06/.07/.08, pag. 970"». Abri el PDF original (Read, pagina 981) y su pie impreso es 973: contiene 507.05, 507.06 «Solado» — «empleando material de subbase granular segun la Seccion 402, en el ancho indicado en la Seccion 506, y de acuerdo con el procedimiento descrito en la Subseccion 506.07» — y el arranque de 507.07. La 974 (PDFPAGE 982) trae «se debera extender una capa de arena suelta de 12 mm de espesor aproximadamente» y 507.08 completa: «capas horizontales de 15 cm a 20 cm de espesor compacto» y «La compactacion en las capas del relleno no sera inferior a las que se indican en la Subseccion 205.12(c) (1)». La pagina impresa 970 (PDFPAGE 978) contiene la Tabla 507-01 «Espesores Minimos de Alcantarillas Circulares y Abovedadas» y 507.02 b) y c) — ni cama ni relleno.

**`R95-044` — hallazgo `H-21` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* EG-2013 completo (busqueda exhaustiva de «recubrimiento», 38 ocurrencias); 508.07 pag. impresa 984 (PDFPAGE 992) y 508.08 pag. impresa 985 (PDFPAGE 993); recubrimiento de zinc pag. impresa 971 (PDFPAGE 979); recubrimiento bituminoso pag. impresa 976 (PDFPAGE 984)

Lei src/modulos/M7_geometria.py:208 — «NUMERAL_G1 = "Sec. 7.A (recubrimiento EG-2013 / resguardo Sec. 5.1)"» — y :255 «def altura_recubrimiento(material: Material) -> float», cuyo docstring dice «h_rec: relleno minimo sobre la clave hasta la subrasante, m»; NUMERAL_G1 se emite como campo `numeral` de la Verificacion G1 (M7:381), es decir va a la memoria. Grepe las 38 ocurrencias de «recubrimiento» en el EG-2013: ninguna designa la altura de tierra sobre la clave; son recubrimiento del refuerzo («Recubrimiento del refuerzo: ±10%», «se deberan obtener los recubrimientos minimos especificados en la ultima edicion del Codigo ACI-318»), de zinc («El peso del total de recubrimiento de zinc por ambas caras del…», impresa 971), bituminoso («Calidad del recubrimiento bituminoso», impresa 976), de taludes/riberas con suelo vegetal (Sec. 413) y de la mezcla asfaltica. Para la magnitud en cuestion el EG-2013 dice «La altura de relleno minimo desde la clave de la tuberia hasta el nivel de la subrasante sera de 0,30 m.» (508.07, impresa 984) y «la altura de relleno minima sobre la misma» (508.08, impresa 985).

**`R95-045` — hallazgo `H-22` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna repo-repo: docs/manifiesto_citas.md §6, filas 243-244, contra src/constantes_normativas.py:176-189 y §14.a del propio manifiesto. Contraste normativo de apoyo: AASHTO M 170M-04, Nota 1 y num. 4.1 (M170M_OCR, PDFPAGE 2).

Manifiesto:243 columna «Numeral citado» = «AASHTO M-170M (clases I a V)», etiqueta [N]/[C]; :244 = «ASTM A-807 / AASHTO M36», misma etiqueta. El codigo que esa fila enlaza dice, en constantes_normativas.py:186-188: «Estos comentarios decian antes "AASHTO M-170M (clases I a V)" y "ASTM A-807 / AASHTO M36", que apuntaban a tablas que no existen», y las lineas 178-179 solo conservan «"concreto": None, # VACIO VERIFICADO -- no es "falta extraer"» y «"tmc": None, # VACIO VERIFICADO -- idem». El §14.a del mismo manifiesto lo repite: «AASHTO M 170M, AASHTO M 36, ASTM A760 — No contienen alturas de relleno admisibles... M 170M clasifica por D-load (resistencia), no por altura». AASHTO M 170M-04, Nota 1: «This specification is a manufacturing and purchase specification only, and does not include requirements for bedding, backfill, or the relationship between field load condition and the strength classification of pipe». Las mismas dos cadenas sobreviven en docs/hoja_de_ruta_alcantarillas_v8.md:523 («No fijado. Remite al Proyecto, AASHTO M-170M (clases I–V) o ASTM A-807») y :830 («"concreto": None, # AASHTO M-170M (clases I a V)»).

**`R95-046` — hallazgo `H-23` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna repo-repo: docs/manifiesto_citas.md §6, filas 245, 247-250 y 255-257, contra src/criterios_adoptados.py:1074-1170, src/constantes_normativas.py:204-232 y src/modulos/M11_reporte.py:694-703. Convencion declarada en tests/test_manifiesto_citas.py, docstring lineas 16-21 y 52-70.

Comprobado uno a uno: la afirmacion negativa esta en criterios_adoptados.py:1140-1142 («Para concreto y TMC no: las Secciones 505, 506 y 507 solo regulan colocacion y compactacion y remiten a la Seccion 502, que tampoco fija altura minima de diseno»), no en 1076-1082, donde solo hay «etiqueta="N->"» y «...subrasante, y lo exige SOLO PARA HDPE»; las remisiones formales estan en 1142-1146, no en 1082-1088; la nota del equipo pesado esta en 1167-1169 (campo verificacion_pendiente), no en 1103-1105, donde empieza «ALCANCE -- POR QUE 'A NIVEL DE PERFIL'». Las cuatro fichas ocupan constantes_normativas.py 205-210 / 211-216 / 217-223 / 224-231, y ninguna coincide con los rangos declarados 204-209 / 204-209 / 204-210 / 204-211. SECCION_EG2013 no aparece en M11_reporte.py: la linea 697 es «resultado = informe.resultado» y lo que se imprime es «material.seccion_eg2013» en las lineas 702-703.

**`R95-047` — hallazgo `H-24` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* EG-2013, indice del Capitulo V (DRENAJE), pagina impresa vii-viii, PDFPAGE 7 -- no la 6 que anota el auditor, que corresponde al indice de pavimentos (Secciones 415-440). Repo: docs/manifiesto_citas.md:251 contra docs/hoja_de_ruta_alcantarillas_v8.md:57, :557 y :827.

EG-2013, PDFPAGE 7: «CAPITULO V ... 881 / DRENAJE ... 881 / Seccion 501 Excavacion para estructuras ... 885» y asi hasta «Seccion 514 Capa Filtrante ... 1039»: el capitulo empieza en la 501 y no existe ninguna «Seccion 500» (grep sobre EG2013.txt: cero coincidencias). El manifiesto:251 declara que NUMERAL_8_1 «Corrige una cita doblemente falsa: ni "Sec. 8.1" es del EG-2013, ni existe una "Seccion 500"», y el codigo lo aplica (M8_estructural.py:135-142, constantes_normativas.py:190-193, modelos.py:175). Pero la hoja de ruta v8 conserva las tres ocurrencias, literales: linea 57 «| Materiales, camas, rellenos, ejecucion, partidas | **EG-2013, Seccion 500** (RD 22-2013-MTC/14) | [N] |», linea 557 «### 8.1 Cama de apoyo y relleno lateral — EG-2013 Seccion 500» y linea 827 «# ================= EG-2013, Seccion 500 ====================================».

**`R95-048` — hallazgo `H-02` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5, 3a ed., abril 2012), Apendice A: num. A.2.1, pag. impresa A.1 (PDFPAGE 190); num. A.2.2, pag. impresa A.2 (PDFPAGE 191); Tabla A.1, pag. A.8 (PDFPAGE 197, renderizada).

Pag. impresa A.1 (PDFPAGE 190), num. A.2.1: «Equations (A.1) and (A.2) apply up to about Q/AD0.5 = 3.5 (1.93 SI).» Pag. impresa A.2 (PDFPAGE 191), num. A.2.2: «The submerged equation (A.3) applies above about Q/AD0.5 = 4.0 (2.21 SI).  The terms are defined in Sections A.2.1.» Rendericé la PDFPAGE 197: la Tabla A.1 («Constants for Inlet Control Equations for Charts in Appendix G») tiene columnas Chart No / Shape and Material / Nomograph Scale / Inlet Configuration / Equation Form / Unsubmerged K / Unsubmerged M / Submerged c / Submerged Y / References y una sola nota al pie, «1Bossy 1963, 2FHWA 1974, 3NBS 5th, 4HEC 13»: ni 3.5 ni 4.0 aparecen en ella. El repo cita esa tabla como fuente en constantes_normativas.py:94 («# Apendice A, Tabla A.1, pag. A.8») para las lineas 96-97 «Q_LIM_NO_SUMERGIDO = 3.5» y «Q_LIM_SUMERGIDO = 4.0», y lo repite en manifiesto_citas.md:266-267 con etiqueta [N].

**`R95-049` — hallazgo `H-01` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5, 3a ed., abril 2012), Apendice A, num. A.2.1, lista «Where:» de la pag. impresa A.2 (PDFPAGE 191, renderizada) frente a la Tabla A.1, pag. A.8 (PDFPAGE 197, renderizada).

Pag. impresa A.2 (PDFPAGE 191), cierre del num. A.2.1: «K, M, c, Y — Constants from Tables A.1, A.2, A.3 / Ku — Unit conversion 1.0 (1.811 SI) / Ks — Slope correction, -0.5 (mitered inlets +0.7)». El renderizado de la PDFPAGE 197 confirma que la Tabla A.1 solo trae Chart No, Shape and Material, Nomograph Scale, Inlet Configuration, Equation Form, Unsubmerged K, Unsubmerged M, Submerged c, Submerged Y y References, con la unica nota «1Bossy 1963, 2FHWA 1974, 3NBS 5th, 4HEC 13»: no hay Ku ni Ks. El repo escribe en constantes_normativas.py:94-95 «# Apendice A, Tabla A.1, pag. A.8» seguido de «KU_METRICO = 1.811», y manifiesto_citas.md:265 repite «Apendice A, Tabla A.1, pag. A.8» con etiqueta [N]; criterios_adoptados.py:688 arrastra la misma cadena.

**`R95-050` — hallazgo `H-08` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5 3a ed., 2012): indice pag. impresa v-vi (PDFPAGE 9-10), encabezado de Cap. 4 pag. impresa 4.1 (PDFPAGE 127), pag. impresa 3.4 (PDFPAGE 86) y Apendice A, Sec. A.2, pag. impresa A.1 (PDFPAGE 190)

Lei src/criterios_adoptados.py:719-722: fuente="HDS-5 (FHWA) 3a ed., abril 2012, Cap. IV y Apendice A (curva de transicion tangente, sin ecuacion publicada)...". En el PDF, PDFPAGE 127 (impresa 4.1) encabeza "CHAPTER 4 / CULVERT DESIGN FOR AQUATIC ORGANISM PASSAGE (AOP)" y el indice dice "CHAPTER 4 - CULVERT DESIGN FOR AQUATIC ORGANISM PASSAGE (AOP).......... 4.1". Barri el Cap. 4 completo (lineas 6481-6911 del .txt) con grep de "transition": ninguna aparicion se refiere a la zona de transicion del control de entrada. La zona de transicion si esta en el Cap. 3, pag. impresa 3.4 (PDFPAGE 86): "This zone is approximated by plotting the unsubmerged and submerged flow equations and connecting them with a line tangent to both curves", y en el Apendice A, Sec. A.2, pag. impresa A.1 (PDFPAGE 190): "The transition zone is defined empirically by drawing a curve between and tangent to the curves defined by the unsubmerged and submerged equations."

**`R95-051` — hallazgo `H-11` — SE SOSTIENE (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna del repo: src/constantes_normativas.py:124-126 contra docs/hoja_de_ruta_alcantarillas_v8.md (911 lineas). Contraste normativo del valor: FHWA-HIF-12-026 pag. impresa 3.10 (PDFPAGE 92)

Lei src/constantes_normativas.py:124-126: "DISCREPANCIA ABIERTA CON LA HOJA DE RUTA: docs/hoja_de_ruta_alcantarillas_v8.md (lineas 432, 436, 790 y 901) sigue escribiendo 19.62". `grep -n "19\.62" docs/hoja_de_ruta_alcantarillas_v8.md` devuelve exactamente cuatro aciertos: 436, 440, 797 y 908. Las lineas citadas que NO contienen 19.62 son, verbatim: 432 = "### 4.3 Control de salida [C]", 790 = "    \"circular_cmp_mitered\":                   {\"K\": 0.0210, \"M\": 1.33," y 901 = "### Notas criticas de programacion". La linea 440 ("**Nota de unidades.** **19.62** es el valor SI...") es una ocurrencia real y no esta citada.

**`R95-052` — hallazgo `H-13` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5 3a ed., 2012), Sec. 3.3.3, pag. impresa 3.24 (PDFPAGE 106) y Sec. 3.1.4, pag. impresa 3.12 (PDFPAGE 94)

Lei src/modulos/M4_control.py:493-494: "h_o_geometrico = (critico.y_c + D) / 2" / "h_o = max(TW, h_o_geometrico)", sin guarda alguna (las unicas validaciones previas son Q, D, S, L y TW>=0). El PDF, pag. impresa 3.24, dice literal: "Approximate hydraulic gradeline ho = (dc + D)/2 can only be used if the barrel flows full for most of its length.  It should not be used if the inlet is not submerged." y "If the headwater depth falls below 0.75D, the approximate method should not be used."; la pag. 3.12 dice "Adequate results are obtained down to a headwater of 0.75D.  For lower headwaters, backwater calculations are required to obtain accurate headwater elevations." PERO el repo SI declara el limite, cualitativamente, en src/criterios_adoptados.py:879-883 (verificacion_pendiente de `geometria_control_salida`): "Con TW bajo y pendiente pronunciada el barril puede no llegar a llenarse ... verificar que el punto donde el control de salida GOBIERNE sea uno donde la hipotesis de seccion llena tenga sentido fisico", con `reemplazado_por` = "Procedimiento de barril parcialmente lleno de HDS-5" (CA:876), y esa advertencia SI se imprime en la memoria (src/modulos/M11_reporte.py:1059-1062 vuelca `verificacion_pendiente` de cada criterio); el manifiesto la recoge en su linea 280.

**`R95-053` — hallazgo `H-17` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5 3a ed., 2012), Sec. 2.2.5.d "Agency Constraints", pag. impresa 2.10 (PDFPAGE 72); inicio de Sec. 2.2.5 en pag. impresa 2.9 (PDFPAGE 71); indice en pag. impresa v (PDFPAGE 9)

Lei src/criterios_adoptados.py:886-906: valor 1.5 en :887 y fuente en :901-904 = "HDS-5 (FHWA) 3a ed., abril 2012, Sec. 2.2.5, pag. 2.14 - rango de HW/D de 1.0 a 1.5 para el diseno corriente. CITA CERRADA por verificacion externa contra el documento"; el manifiesto lo repite en :279 ("**Sec. 2.2.5, pag. 2.14**"). En el PDF: el indice dice "2.2.5    Allowable Headwater .............. 2.9"; el encabezado "2.2.5  Allowable Headwater" abre la pag. impresa 2.9 (PDFPAGE 71) y el texto del rango esta en la 2.10 (PDFPAGE 72): "d.  Agency Constraints. ... The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5." La pag. impresa 2.14 (PDFPAGE 76) que cita el repo contiene la Figura 2.8 de espolones de hormigon, la estabilidad de cauce (HEC-20/HEC-23) y la Sec. 2.3.3 "Safety Assessment": no menciona HW/D.

**`R95-054` — hallazgo `H-15` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5 3a ed., 2012), Apendice C: Tabla C.2 "Entrance Loss Coefficients", pag. impresa C.6 (PDFPAGE 216); pag. impresa C.2 (PDFPAGE 212); Tabla A.1, pag. impresa A.8 (PDFPAGE 197)

Lei src/criterios_adoptados.py:820-845: valor 0.5 en :821 y fuente en :837-842 = "...Apendice C, Tabla C.2, pag. C.2 - coeficientes de perdida de entrada; fila 'square edge with headwall', ke = 0.5. CITA CERRADA por verificacion externa contra el documento"; manifiesto :277 repite "Tabla C.2, pag. C.2". En el PDF, PDFPAGE 216 abre con el folio "C.6" seguido de "Table C.2.  Entrance Loss Coefficients." y bajo "Pipe, Concrete" lista "Headwall or headwall and wingwalls / Socket end of pipe (groove-end 0.2 / Square-edge 0.5". La pag. impresa C.2 (PDFPAGE 212) es el indice de cartas: "Chart / Concrete Box Culverts (Continued) ... 11A, 11B Headwater Depth for Inlet Control, Single Barrel Box Culverts, Skewed Headwalls...". El rotulo entrecomillado por el repo aparece verbatim en OTRA tabla: la A.1 (PDFPAGE 197) trae "Square edge w/headwall".

**`R95-055` — hallazgo `H-20` — REFUTADO (OK, CONFIRMA)**

*Dónde se miró:* FHWA-HIF-12-026 (HDS-5, 3a ed. 2012), pag. impresa 3.9 (PDFPAGE 91) tras la Ec. (3.3) y pag. impresa B.1 (PDFPAGE 203) tras la Ec. (B.1)

El PDF original, leido como imagen en la pagina PDF 91 (impresa 3.9), dice literalmente: 'g is the acceleration due to gravity, 32.2 ft/s2 (9.8 m/s2)'; identico en B.1 (PDFPAGE 203). El dato del auditor es correcto. Pero la linea del repo que cita como prueba dice otra cosa: docs/manifiesto_citas.md:81 declara la gravedad de M4 como '(constante fisica, sin numeral que citar - igual que pi)' y '**Ya no vive aqui**: ... constante fisica universal, no una cita del Manual de Hidrologia'. src/constantes_fisicas.py:19-31 razona lo mismo, y src/modulos/M4_control.py:107-116 y src/constantes_normativas.py:117-123 retiran expresamente la justificacion '19.62 = 2*9.81': 'Es una coincidencia numerica ... y no el origen de la constante. HDS-5 no deriva K de la gravedad'.

**`R95-056` — hallazgo `H-21` — AJUSTADO (MEDIA, CONTRADICE)**

*Dónde se miró:* Verificacion interna del repositorio: docs/manifiesto_citas.md:268-270 y :275 contra src/constantes_normativas.py:99-127 (no hay PDF que consultar)

Lei el diccionario: 'HDS5_INLET = {' abre en CN:99; la entrada de concreto ocupa CN:100-101 (los valores c=0.0398 e Y=0.67 estan en la 101), 'circular_cmp_headwall' CN:102-103, 'circular_cmp_mitered' CN:104-105 y el cierre '}' en CN:106. Las tres filas del manifiesto (268, 269, 270) citan las tres el mismo '[CN:99-100](src/constantes_normativas.py:99)'. CN:110 es literalmente '# ================= Control de salida (SI) ==================================', y el comentario 'ho = max(TW, (yc + D)/2)' esta en CN:127. El manifiesto se propone decir 'donde esta escrito en el repositorio' (linea 33) y no declara ninguna convencion de rango aproximado (lineas 62-63 solo definen las abreviaturas CN/CA/DS).

**`R95-057` — hallazgo `H-02` — AJUSTADO (CRITICA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD Bridge Design Specifications, 9th ed. 2020 - Art. 12.6.6.3 'Minimum Cover', pag. impresa 12-21 (PDFPAGE 1659) y Tabla 12.6.6.3-1, pag. impresa 12-22 (PDFPAGE 1660)

Lei las dos paginas del PDF como imagen. Art. 12.6.6.3: 'The minimum cover, including a well-compacted granular subbase and base course, shall not be less than that specified in Table 12.6.6.3-1'. Tabla 12.6.6.3-1: 'Corrugated Metal Pipe | - | S/8 >= 12.0 in.' y 'Reinforced Concrete Pipe | Under unpaved areas or top of flexible pavement | Bc/8 or B'c/8, whichever is greater, >= 12.0 in.' / 'Under bottom of rigid pavement | 9.0 in.', con la nota '* Minimum cover taken from top of rigid pavement or bottom of flexible pavement'. En el repo: docs/manifiesto_citas.md:597 'El vacio es real y esta cerrado - la busqueda se agoto en las tres fuentes donde podia estar', y src/criterios_adoptados.py:1113-1115 'fuente=NINGUNA ... la busqueda esta cerrada en las tres fuentes donde podia estar'. Y docs/hoja_de_ruta_alcantarillas_v8.md:53 lista en la tabla de normas aplicables: 'Seccion 12 (estructuras enterradas) | AASHTO LRFD Bridge Design Specifications | Norma matriz'.

**`R95-058` — hallazgo `H-03` — SE SOSTIENE (ALTA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD 9th ed. 2020 - Art. 12.6.6.3 y C12.6.6.3, pag. impresa 12-21 (PDFPAGE 1659); Tabla 12.6.6.3-1, pag. 12-22 (PDFPAGE 1660); Art. 12.8.3.1.1 y su comentario, pag. impresa 12-30 (PDFPAGE 1668)

La pagina 12-21 leida como imagen no contiene la palabra 'typical' ni dispensa alguna por armadura: el articulo entero es 'The minimum cover, including a well-compacted granular subbase and base course, shall not be less than that specified in Table 12.6.6.3-1' mas la definicion de S, Bc, B'c e ID, y la unica clausula de relevo va en sentido contrario: 'If the minimum cover provided in Table 12.6.6.3-1 is not sufficient to avoid placement of the pipe within the pavement layer, then the minimum cover should be increased to a minimum of the pavement thickness, unless an analysis is performed...'. El lenguaje 'special design' aparece en 12-30: 'Use of soil cover less than the minimum values shown for a given radius shall require a special design' (C12.8.3.1.1, planchas metalicas de gran luz). En el repo lei docs/manifiesto_citas.md:635 - 'El tipico es 1.0 ft (~0.305 m) salvo diseno especial de armadura ... la verificacion deberia confirmarla, no corregirla | AASHTO LRFD Art. 12.6.6.3' - y la misma frase, palabra por palabra, en src/criterios_adoptados.py:1147-1155.

**`R95-059` — hallazgo `H-04` — AJUSTADO (BAJA, CONTRADICE)**

*Dónde se miró:* AASHTO LRFD 9th ed. 2020 - Tabla 12.6.6.3-1 'Minimum Cover', pag. impresa 12-22 (PDFPAGE 1660)

Tabla leida en el PDF original: 'Thermoplastic Pipe | Under unpaved areas | ID/8 >= 12.0 in. || Under paved roads | ID/2 >= 24.0 in.'; 'Reinforced Concrete Pipe | Under unpaved areas or top of flexible pavement | Bc/8 or B'c/8, whichever is greater, >= 12.0 in.'; 'Corrugated Metal Pipe | - | S/8 >= 12.0 in.'. En el repo, docs/manifiesto_citas.md:598 y src/criterios_adoptados.py:1091-1103: 'el HDPE es el material con MENOR tolerancia a cobertura reducida bajo carga viva -- es el que menos rigidez de anillo aporta y el que mas depende del confinamiento del relleno'. La magnitud que el criterio fija es 'desde la clave hasta el nivel de la subrasante' (EG-2013 508.07), es decir, bajo prisma de carretera.

