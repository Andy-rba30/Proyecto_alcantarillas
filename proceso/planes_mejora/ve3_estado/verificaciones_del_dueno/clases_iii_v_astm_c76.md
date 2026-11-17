> Verificación independiente pedida por el dueño (decisión 1 del LEEME), hecha con el modelo Fable desde otra sesión, sin acceso a las conclusiones de VE-3 salvo el enunciado de H1. La sesión que la envía comprobó por su cuenta la tabla del USACE (pág. impresa B-7, PDF 71): coincide. Leer con H1 (tope de diámetro por clase) ANTES de transcribir la Clase V.

# Verificación independiente: D-load de las Clases III a V (AASHTO M 170M / ASTM C76M)

Rama revisada: `origin/claude/youthful-shannon-rjzmuc` en `ad8dd9f`. Todavía no hay ningún commit que transcriba III–V: `clases_producto_por_relleno` sigue en `{"concreto_reforzado": {"II": 50.0}}`.

## Veredicto

Las cifras 40 / 50 / 65 / 100 / 140 N/m/mm coinciden con lo impreso en el USACE y se pueden transcribir como [C], en métrico nominal y no como conversión de lb/ft/ft. Dos condiciones antes de que gobiernen diseños:

1. **Tope de diámetro por clase (H1, alto).** M 170M no tabula la Clase V con pared B por encima de 1200 mm, y el programa usa pared B con tope único de 2700 mm.
2. **Cita honesta (H2, medio).** La fuente es un ejemplo resuelto del USACE, sin edición de la norma y sin D-ult. El ejemplar de M 170M sólo corrobora en parte.

El programa no necesita la D-ult: AASHTO LRFD 12.10.4.3.1 verifica sólo en servicio (fisura de 0.01 in).

## Tabla de las cinco clases

Fuente A: `ejemplos_resueltos/conducto/usace_em_1110_2_2902.pdf`, pág. PDF 71, pág. impresa B-7 (cabecera «EM 1110-2-2902 / Change 1 / 31 Mar 98»), Apéndice B, recuadro «Chapter 3: Circular Precast Concrete Pipe for Small Dams and Major Levees – D-Load Analysis». La tabla se titula «ASTM C76 Class and D0.01», con columnas «Class» y «D0.01». Leída en la imagen a 150 ppp; el `pdftotext` coincide.

Fuente B: `normas/AASHTO M 170M-04 … .pdf`, notas al pie de las Tablas 1 a 5, leídas por imagen a 200 ppp. El archivo es una recomposición OCR, no un escaneo limpio.

| Clase | USACE B-7, literal | lb/ft/ft × 0.047880 | M 170M-04, D-load 0.3 mm | M 170M-04, D-load última |
|---|---|---|---|---|
| I | «40 (800)» | 38.30 | PDF 3: «dtl0», ilegible | PDF 3: «f>t1.0», ilegible |
| II | «50 (1,000)» | 47.88 | PDF 5 (M 170M-5): «50.0», legible | PDF 5: «?S.0», primer dígito ilegible |
| III | «65 (1,350)» | 64.64 | no se ve | PDF 7 (M 170M-7): «100.0», legible |
| IV | «100 (2,000)» | 95.76 | no se ve | PDF 9 (M 170M-9): «iS.00», ilegible |
| V | «140 (3,000)» | 143.64 | PDF 11 (M 170M-11): «\ 40.0», primer dígito ilegible | PDF 11: «1 ISD», ilegible |

Lectura de la tabla:

- **Unidades.** La tabla no las imprime. Se deducen de la misma página («W1 = 145,940 N/m (10,000 plf)», «Si = 1,200 mm (4 ft)») y de la B-8 (PDF 72): «D0.01 = 57 N/m/mm (1,172 plf/ft) ASTM C76M Class III».
- **C76 o C76M, y edición.** El título dice «ASTM C76»; el resultado de la B-8 dice «ASTM C76M»; el cuerpo (PDF 39, Tabla 5-1) dice «ASTM C 76 M or AASHTO M 170». No se cita año de edición en ningún sitio; el documento es de 1998.
- **Redondeo.** Los métricos son los nominales de la norma métrica, no una conversión: 100 ≠ 95.76 y 140 ≠ 143.64. El paréntesis es la clase de la norma en unidades inglesas.
- **D-ult.** El USACE no la trae: la tabla sólo tiene la columna D0.01.
- **Qué debe usar el programa.** Los métricos nominales (40/50/65/100/140). EG-2013 506 remite a «AASHTO M-170M», la métrica (líneas 40038, 40256, 40262 y 40290 del `pdftotext` del PDF). LRFD 12.10.4.3.1 remite a «AASHTO M 170M and M 170 (ASTM C76M and C76)». M8 ya calcula en SI (N/m ÷ mm), así que no hay conversión que hacer.

Contraste con una segunda fuente:

- **M 170M-04** corrobora tres cosas, en parte: Clase II 0.3 mm = 50.0 (completo), Clase III última = 100.0 (coherente con 65 × 1.5 = 97.5, redondeado) y Clase V 0.3 mm = «?40.0» (compatible con 140.0). Las Clases I y IV, y el 65 de la III, no se pueden confirmar ahí. La sesión tenía razón en eso.
- **ACPA** (`acpa_cpdm_cap4.pdf`, PDF 28, pág. impresa 54, «Application of Factor of Safety») no lista las clases, pero da la relación: «The relationship between ultimate D-load and 0.01-inch crack D-load is 1.5 for 0.01 inch crack D-loads of 2,000 or less; 1.25 for 0.01 inch crack D loads of 3,000 or more». Eso es coherente con los paréntesis del USACE (2,000 y 3,000 como Clases IV y V) y con la última = 100.0 de la Clase III. `acpa_dd1.pdf` y `acpa_dd22.pdf` no traen la tabla.
- No encontré ninguna discrepancia entre fuentes.

## Hallazgos

### H1 (alto): al habilitar IV y V, el programa ofrecerá clases en diámetros que M 170M no tabula con pared B

- **Evidencia.** M 170M-04, Tabla 5 «Design Requirements for Class V Reinforced Concrete Pipe», PDF 10, pág. impresa M 170M-10 (escaneo real, legible, girado):
  - Wall A: sin diseño en ningún diámetro.
  - Wall B: pared y acero de 300 a 1200 mm (50 … 125 mm). De 1350 a 3600 mm, llamada a nota y rayas.
  - Wall C: de 300 a 1800 mm (69 … 194 mm). De 1950 mm en adelante, rayas.
  - Nota: «For modified or special designs, see Section 7.2 or with the permission of the owner utilize the provision of M 242M».
- **Qué hace el código.** Toma el espesor de la columna de pared B. Usa un tope único `DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM = 2700`, leído de las Tablas 1 y 3. Por clase sólo tiene el mínimo, `DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM`.
- **Consecuencia.** Con V transcrita, un tubo de 1500 mm saldría «Clase V» con pared B, que la norma no tabula: es diseño especial de la sección 7.2. Es el mismo defecto que la auditoría de T-5 cerró por abajo con la Clase I.
- **Corrección.** Añadir un diámetro máximo tabulado por clase y pared, gemelo del mínimo, y que `clases_de_concreto_para(D)` no ofrezca la clase por encima. Clase V pared B: 1200 mm, verificado. El de la Clase III se deja leer en la continuación de su tabla (PDF 7: la última fila con acero es 2700).
- **Pendiente dentro del hallazgo.** La Tabla 4 (Clase IV, PDF 8) es ilegible salvo su primera fila, así que su tope no se puede leer. No debe inventarse: Clase IV queda con tope `None` y bloqueo (`DatoFaltanteError`) por encima del mayor diámetro que se llegue a verificar, o el dueño aporta un ejemplar legible.

### H2 (medio): la cita debe decir lo que la fuente es

La fuente no es la norma de producto ni una tabla normativa del USACE. Es un dato dentro de un ejemplo resuelto (Apéndice B), titulado «ASTM C76», sin edición y sin unidades impresas en la tabla. La ficha del criterio debe:

1. Citar «USACE EM 1110-2-2902, Change 1, 31 Mar 98, Apéndice B, pág. impresa B-7 (PDF 71), tabla "ASTM C76 Class and D0.01"» con el literal de cada fila.
2. Declarar que la fuente primaria (M 170M-04) sólo corrobora II = 50.0, la última de III = 100.0 y V = «?40.0», y que I, IV y el 65 de III siguen sin verificarse contra ella. `reemplazado_por` (ejemplar legible de M 170M-23 o C76M) debe seguir abierto.
3. No presentarlo como «AASHTO M 170M-04, Tablas 3 a 5» en la memoria. El texto actual `descripcion_umbral="D-load de 0.3 mm de la Clase {clase} (AASHTO M 170M)"` y la cita `AASHTO_M170M.T2#DLOAD` sólo valen para la Clase II.
4. Actualizar `nota_clases`, `verificacion_pendiente` y `DIFERIDO_CLASES_M170M`, que hoy afirman «sólo la Clase II es legible».

### H3 (medio): métrico nominal, no conversión; y el tubo suministrado tiene que ser M 170M

- Las clases inglesas valen 47.88 / 64.64 / 95.76 / 143.64 N/m/mm.
- Si la obra recibe tubo ASTM C76 en unidades inglesas, la Clase IV resiste un 4.2 % menos que el 100 del programa, la III un 0.6 % menos y la II un 4.2 % menos (esto último ya ocurre hoy con la Clase II).
- EG-2013 exige M-170M, de modo que el programa está bien.
- **Corrección.** Sólo documental: la ficha debe decir que las cifras son de la norma métrica y que no equivalen a la clase homónima en lb/ft/ft. No se debe transcribir 38.3 / 47.9 / 64.6 / 95.8 / 143.6.

### H4 (sin defecto): la D-ult no hace falta

- **Qué usa M8.** `verificar_concreto` compara sólo con la D-load de 0.3 mm: `D = [(W_E+W_F)/B_FE + W_L/B_FLL]/S_i`, × 1.10 en el Tipo 1, sin factor de seguridad.
- **Qué exige la norma.** AASHTO LRFD 9.ª ed., 12.10.4.3.1, pág. impresa 12-64: «The service limit state shall apply using the criterion of acceptable crack width specified herein». El comentario C12.10.4.3.1 dice que la resistencia última es la D-load de servicio «multiplied by a strength factor specified in the manufacturing standard», es decir, la garantiza la norma de producto, no el diseñador.
- **ACPA** (PDF 28, pág. 54): «a factor of safety of 1.0 should be applied if the 0.01 inch crack strength is used as the design criterion».
- El `Hf = 1.3` que aparece en la B-7 del USACE es un «hydraulic factor» propio de presas y diques (EM, párr. 3-7, Ec. 3-2). No es de LRFD y no debe copiarse con la tabla.

### H5 (bajo): la premisa «Ø 0.90 m, 3.0 m, Tipo 2, no cierra con Clase II» no se reproduce

Con el código de la rama, ese caso cierra con Clase II en el Tipo 2. El que no cierra es el Tipo 3, que es el valor de archivo de `instalacion_estandar_concreto`. El «≈ 2.4 m» de H1 corresponde al Tipo 3: la corrida da un relleno máximo de Clase II de 2.82 m en Tipo 3 y 3.80 m en Tipo 2. Conviene que el informe de ensayos diga con qué tipo se midió.

## Caso recalculado: Ø 0.90 m, H = 3.0 m, γ = 19 kN/m³

Datos leídos de la corrida del código de la rama (punto A01 con el relleno forzado a 3.0 m):

- t = 0.100 m (pared B), así que B_c = 1.10 m.
- e_paq = 0.15 m, con γ_p = 0.140 kcf = 21.99 kN/m³.
- La carga viva no se desprecia a 3.0 m (regla vigente en la rama): W_L = 8.618 kN/m (lo tomo de la corrida, no lo recalculé a mano), B_FLL = 2.2.
- D = 900 / 25.4 = 35.43 in.

Aritmética:

- W_F = 9.81 · π · 0.90² / 4 = 6.24 kN/m.
- Prisma: 19 · 3.0 + 21.99 · 0.15 = 60.30 kPa.
- **Tipo 2.** VAF = 1.40; B_FE = 3.0 − 0.1 · (35.43 − 24) / 12 = 2.905.
  - W_E = 1.40 · 1.10 · 60.30 = 92.86 kN/m.
  - D = [(92.86 + 6.24) / 2.905 + 8.618 / 2.2] · 1000 / 900 = (34.12 + 3.92) / 0.9 = **42.3 N/m/mm**, menor que 50: **Clase II cierra**.
- **Tipo 3** (valor de archivo). VAF = 1.40; B_FE = 2.4 − 0.1 · 0.952 = 2.305.
  - D = (43.00 + 3.92) / 0.9 = **52.1 N/m/mm**, mayor que 50: pide **Clase III** (65), con margen de 12.9.

Corrida del código con las cinco clases declaradas en caliente, Ø 0.90 m, γ = 19:

| H (m) | Tipo 1 | Tipo 2 | Tipo 3 | Tipo 4 |
|---|---|---|---|---|
| 2.4 | 30.4 → II | 37.0 → II | 45.1 → II | 60.8 → III |
| 3.0 | 34.0 → II | 42.3 → II | 52.1 → III | 71.3 → IV |
| 4.0 | 41.1 → II | 52.1 → III | 64.8 → III (margen 0.16) | 89.7 → IV |
| 6.0 | 56.8 → III | 73.1 → IV | 91.7 → IV | 128.0 → V |

Relleno máximo por clase en esa corrida: Tipo 2, 3.80 m (II), 5.24 m (III) y 8.46 m (IV); Tipo 3, 2.82 m (II), 4.01 m (III) y 6.60 m (IV).

Cómo se corrió: `scipy` no está instalado en este entorno. Para que `_relleno_maximo` funcionara usé un `brentq` de bisección sustituto, en una copia exportada de la rama dentro del scratchpad. Las D-load no dependen de él; los rellenos máximos sí, con la precisión de la bisección. No toqué ningún repositorio.

## Etiqueta

**[C] es la correcta.**

- No es [N→]: no hay analogía, la clase de tubo se aplica a su propio objeto.
- Hay un argumento para [N] por remisión, porque EG-2013 506 manda cumplir «AASHTO M-170M». Pero el proyecto ya etiqueta [C] la Clase II leída del propio M 170M, y [N] exige «numeral verificado», que para III–V no se cumple contra el ejemplar normativo. Mientras la lectura venga del USACE, [C] con la procedencia secundaria declarada es lo honesto.

## Lo que no pude verificar

- **D-load de 0.3 mm de las Clases I, III y IV, y última de I, II, IV y V, en M 170M-04.** Ilegibles en el ejemplar. Sólo consta el USACE, más la coherencia con la relación 1.5 / 1.25 de ACPA.
- **Edición de ASTM C76/C76M que usa el USACE.** No la cita.
- **Tope de diámetro tabulado de la Clase IV, por pared.** Tabla 4 ilegible.
- **M 170M-23 vigente.** No está en `/home/user/Normas`, así que no sé si mantiene los valores.
- **Existencia de una norma peruana de tubos (NTP).** No hay ningún PDF en el repositorio de normas que lo confirme o lo niegue.
- **Informe `ENSAYOS_DISENO_CONDUCTO.md`.** No lo leí.
