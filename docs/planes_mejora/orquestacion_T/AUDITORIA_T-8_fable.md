# AUDITORÍA ADVERSARIAL (segunda, independiente) — T-8, protección de entrada y salida (Fase 6)

- Árbol auditado: `/home/user/wt/main`, `df1b23c` (sólo lectura). Diff: `git diff 7e74065 df1b23c`.
- Todo lo ejecutado corrió sobre copias en
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-8-aud/`
  (`arbol/` = `df1b23c`, `base/` = `7e74065`, `mut/` = copia con git para el arnés). Nada se editó en `/home/user/wt/main`.
- Fuentes abiertas: `hec14.pdf`, `Hidrología, Hidráulica y Drenaje (Versión Libro).pdf`, `MC-01-13 … EG-2013 ….pdf`,
  `hif12026.pdf` (HDS-5), todas en `/home/user/andy-rba30/normas/normas/`. Figuras y láminas leídas por imagen.

## VEREDICTO: **AJUSTADO**

Lo que rige por defecto está bien: **ningún número de la línea base está mal ni se movió**, las fórmulas y las tablas
están transcritas celda a celda como el PDF y los dorados reproducen los ejemplos resueltos de la fuente. No hay
hallazgo BLOQUEANTE. Hay **2 ALTA, 4 MEDIA y 8 BAJA**, más una observación fuera del diff (H14); las dos altas están del lado NO conservador: una en la
alternativa que se le ofrece al dueño (`envolvente_hec14`) y otra en la rama «sin enrocado».

| Severidad | Nº | IDs |
|---|---|---|
| BLOQUEANTE | 0 | — |
| ALTA | 2 | H1, H2 |
| MEDIA | 4 | H3, H4, H5, H6 |
| BAJA | 8 | H7 a H13, H15 |
| Observación fuera del diff | 1 | H14 (M4, anterior a T-8) |

---

## A. Lo que se comprobó y está BIEN (con la evidencia)

**A.1 Fórmulas, coeficientes y tablas contra el PDF (punto 1 del encargo).**

| Objeto | Fuente (impresa / PDF) | Texto o valor del PDF | Código | ¿Coincide? |
|---|---|---|---|---|
| Ec. (10.4) | HEC-14 10-17 / 218 | `D50 = 0.2·D·[Q/(g^0.5·D^2.5)]^(4/3)·(D/TW)`, «recommended for circular culverts» | `apron_hec14`, `HEC14_APRON_COEFICIENTE/EXPONENTE` | sí |
| Límites de TW | 10-17 / 218 | «should be limited to between 0.4D and 1.0D. If tailwater is unknown, use 0.4D» | 0.4 / 1.0; por debajo acota a 0.4D (como el ejemplo, «use TW = 0.4D»); por encima no evaluable («Figure 10.3 should be used», 10-18) | sí |
| Ec. (10.5) | 10-17 / 218 | «Whenever the flow is supercritical in the culvert… D' = (D + yn)/2», «D' = adjusted culvert rise», «yn = normal (supercritical) depth» | `D_calc = (D + y_salida)/2` | sí (ver H10-a: los límites de TW con D' son lectura) |
| Tabla 10.1 | 10-18 / 219 | 125/4D/3.5 · 150/4D/3.3 · 250/5D/2.4 · 350/6D/2.2 · 500/7D/2.0 · 550/8D/2.0; «D is the culvert rise»; clase «D50 greater than or equal to the required size» | `HEC14_TABLA_10_1` (6 filas, en m) | sí, las 18 celdas |
| Ancho | 10-18, 10-19 / 219-220; Fig. 10.4 (por imagen, 10-16 / 217) | «1:3 flare»; «Width (at apron end) = 3D + (2/3)L»; la figura acota D a cada lado del tubo | 3.0 y 2/3 | sí |
| Piso del espesor | 10-18 / 219; 10-1 / 202 | «to a limit of 2.0D50 for the larger riprap sizes»; «lined with riprap that is at least 2D50 thick» (poza) | `HEC14_ESPESOR_MIN_EN_D50 = 2.0` | sí (es lectura razonable: la Tabla 10.1 es un «example») |
| Filtro | 10-18 / 219 | «A filter blanket should also be provided as described in HEC 11»; Fig. 10.4 dibuja «Geotextile» | requisito declarado | sí |
| Nota 8, Tabla 1.1 | 1-2 / 15 | «Riprap apron ⁸» en «Energy Dissipators and Limitations»; «⁸Culvert rise less than or equal to 1500 mm (60 in)» | `HEC14_APRON_ALTURA_MAX_M = 1.5` | la fuente lo dice así y para ese método; **ver H5** (60 in = 1.524 m) |
| Ec. (5.1) | 5-1 / 54 | `[hs,Ws,Ls]/Rc = Cs·Ch·(α/σ^(1/3))·[Q/(g^0.5·Rc^2.5)]^β·(t/316)^θ`; Rc «assuming full flow»; t en minutos; σ = (D84/D16)^0.5 | `hoya_de_socavacion_hec14` | sí |
| Tabla 5.1 | 5-2 / 55 | 2.27/0.39/0.06 · 6.94/0.53/0.08 · 17.10/0.47/0.10 · 127.08/1.24/0.18 | `HEC14_SOCAVACION_NO_COHESIVO` | sí, 12 celdas |
| Tabla 5.2 (Ch) | 5-3 / 56 | Hd 0: 1.00 ×4 · 1: 1.22/1.51/0.73/1.28 · 2: 1.26/1.54/0.73/1.47 · 4: 1.34/1.66/0.73/1.55 | `HEC14_SOCAVACION_CH` | sí, 16 celdas |
| Tabla 5.3 (Cs) | 5-3 / 56 | 0: 1.00 ×4 · 2: 1.03/1.28/1.17/1.30 · 5: 1.08/… · >7: 1.12/… | `HEC14_SOCAVACION_CS` | sí, 16 celdas |
| 30 min | 5-2 / 55; 5-7 / 60 | «it is recommended that a time of 30 minutes be used»; «approximately 2/3 to 3/4 of the maximum scour depth occurs in the first 30 minutes»; exponentes «not applicable for the first 30 minutes»; cohesivo: «Use 30 minutes… if it is not known» | [C] 30 min; < 30 se acota a 30 como cota superior | sí (ver H8 por el verbo) |
| Ec. (5.2)/(5.3), Tabla 5.4 | 5-6, 5-7 / 59-60 | α 0.86/3.55/2.82/0.62; β 0.18/0.17/0.33/0.93; θ 0.10/0.07/0.09/0.23; αe 1.37/5.63/4.48/2.48; ye = (A/2)^1/2; ρ = 1000 kg/m3 | `HEC14_SOCAVACION_COHESIVO` | sí, 16 celdas (αe = α/0.63 recomputado) |
| Ec. (5.4) | 5-7 / 60 | `τc = 0.001(Sv + αu) tan(30 + 1.73 PI)`; «αU = 8630 N/m2 (SI), 180 lb/ft2 (CU)»; «limited to sandy clay soils with a plasticity index of 5 to 16» | `HEC14_TAU_C_*`, `HEC14_TAU_C_ALFA_U_SI = 8630` | sí. 180 lb/ft² = 8618.4 N/m² (0.14 % bajo 8630): el comentario lo dice. La fuente NO limita Sv, y el código tampoco |
| Cabezal | 5-2 / 55 | «the headwall should extend to a depth equal to the maximum depth of scour» | `socavacion_salida` | sí |
| 0.4·Ls | 5-2 / 55 | «approximately 0.4 Ls downstream of the culvert outlet» | 0.4 | sí |
| ye y Froude | 10-2 / 203; 9-40 / 197 | «For circular culverts, ye = (A/2)^1/2, where A is the brink area»; ejemplo: A = Q/Vo | `froude_salida` | sí |
| Tirante de borde | 3-3 / 34 | «The flow goes through critical depth upstream of the outlet when the tailwater elevation is below the critical depth elevation» | `_aviso_tirante_de_borde` | sí (ver H2) |
| Apéndice D | D-1, D-2 / 280-281 | Berry 0.0413 (SI); Searcy `0.692/(S−1)·V²/2g` → 0.02138·V² con S = 2.65; «not recommended because they do not consider tailwater effects» | docstring de M6 | sí; Laushey 1/(3.1·9.8) = 0.03292 |
| Laushey, ec. (49) | Manual 80 / 83 (por imagen) | `d50 = V²/(3.1g)`; V «velocidad media del flujo a la salida» | `laushey_d50` | sí |
| Tabla Nº 11 | Manual 77 / 80 (texto **e imagen**) | 13 filas × 2 columnas | `MC_HHD.T11` → `V_MAX_NO_REVESTIDOS` | sí, las 26 celdas |
| Láminas 04 y 05 | Manual 210-211 / 213-214 (imagen) | 05: «FILTRO», «CAMA DE APOYO», «H:V», «VARIABLE», sin una cota; 04: aliviadero con cotas («0.80 min.») | citas `MC_HHD.LAMINA_04/05` | sí |
| EG-2013 511.08 | 1014-1015 / 1022-1023 | Tabla 511-06: < 15 / 15-50 / > 50 → permitividad 0,7 / 0,2 / 0,1; TAA 0,43 / 0,25 / 0,22(5); clases 2 (tejido monofilamento) y 1 | `GEOTEXTIL_EROSION_T511_06` | sí (ver H4 por la nota (5)) |
| HDS-5 5.3.2 | 5.11 / 147 | «…is typically a standard practice unless field investigation at similar culverts in the vicinity indicates that such protection is not needed» | `_aviso_salida_sin_enrocado` | sí |

La socavación está citada por el **Capítulo 5**, la velocidad de salida por el 3 y el apron por el 10.2: la errata de la
cadena está corregida en todo lo que leí. Los coeficientes sin sufijo `_SI` son adimensionales (los ejemplos SI y CU de
la fuente usan los mismos 0.2, 2.27, 316…), y el único dimensional, αu, lo lleva con su equivalente inglés.

**A.2 Dorados rehechos a mano (punto 2).**

- Apron SI (10-18/10-19): `Q/(√g·D^2.5) = 2.33/(3.1321·2.7557) = 0.26996`; `^(4/3) = 0.1745`;
  `D50 = 0.2·1.5·0.1745·2.5 = 0.1309 m` (fuente 0.13) → clase 2 → L = 6 m, e = 0.495 m (fuente «0.50»), W = 8.5 m.
- Apron CU (10-19): `0.2·5·(85/(5.6745·55.9017))^(4/3)·2.5 = 0.4319 ft` (fuente 0.43 ft).
- Hoya no cohesiva (5-4): Rc = 0.11425; `Q/(√g·Rc^2.5) = 55.286`; `hs = 1.03·1.26·(2.27/1.2320)·55.286^0.39·0.094937^0.06·0.11425 = 1.1343 m` (fuente 1.14).
- Hoya cohesiva (5-8): `τc = 32.6·tan(50.76°) = 39.91 N/m²`; `ρV²/τc = 377.2`; `hs = 0.86·377.2^0.18·0.0949^0.10·0.61 = 1.206 m` (fuente 1.2).
- Marco cohesivo del bloque 9 (aritmética del test): 1.22·1.37·2.48345·0.790212·0.447214 = 1.46688 m. Coincide.
- A-01 de la línea base, rehecho entero: d50 = 3.206²/(3.1·9.8) = 0.3383 m; e = 1.75·d50 = 0.592 m; A = 1.167/3.206 = 0.3640 m²;
  ye = 0.4266 m; Fr_e = 1.567; D' = (0.9 + 0.627)/2 = 0.7636; TW acotado a 0.3054; D50 = 0.2516 m → clase 4 → 5.4 m, 0.77 m, 6.3 m.
  Con el lecho `D84 = 0.02, D16 = 0.002`: hs = 1.03·1.22·(2.27/1.4678)·15.516^0.39·0.86825·0.225 = 1.1061 m (el programa: 1.10609).

**Sobre el «CU escalado a λ = 0.9».** Es legítimo *como prueba de la fórmula*: la Ec. (10.4) es dimensionalmente homogénea
(`D50/D = 0.2·Q*^(4/3)·(D/TW)`), la escala de Froude (longitudes × λ, caudal × λ^2.5) deja Q* y D/TW intactos y el oráculo
(0.43 ft) es el número impreso, no una salida del código; un exponente o un coeficiente mal puesto lo rompería. No se
prueba a sí mismo. **Pero la razón por la que hubo que escalar es un defecto, no una rareza**: ver H5.

**A.3 Lo que no debía moverse (punto 6).** Medido corriendo la CLI sobre `base/` (`7e74065`) y `arbol/` (`df1b23c`) con las
tres corridas de la línea base y comparando con `cli.py --comparar`:

```
perfil ancho : 29 diferencias, 0 no comparables — criterios_sha1, dos textos de advertencias y sólo claves NUEVAS
               (apron_hec14, froude_salida, filtro, proteccion_entrada, socavacion_salida, …)
expediente   : 1 diferencia (criterios_sha1)        perfil estrecha : 1 diferencia (criterios_sha1)
resumen_perfil_ancho.csv y resumen_expediente.csv: idénticos byte a byte (cmp)
bloque `diseno` de A-01, A-02, B-01, C-01: idéntico      d50 0.3382 / 0.2736 m · espesor 0.5919 / 0.4787 m · longitud 5.0 m
informe_perfil_ancho.json comprometido frente al regenerado: IGUALES
```

**Diámetros movidos: ninguno** (A-01 y A-02 siguen en Ø 0.90 m; también con `--declarar
regla_espesor_longitud_proteccion_salida=envolvente_hec14`, columnas 1-13 del CSV iguales).

**A.4 Robustez (punto 5).** `rob1.py` (más de 50 valores malos en los seis datos externos: NaN, ±inf, negativos, cero, cadenas,
booleanos, listas, objetos a medias), `rob2.py` / `rob3.py` / `rob6.py` (S = 0, TW = 0, TW ≫ D, Q de 1e-12 a 12 m³/s, marco de
1 celda por la CLI con los siete criterios del cajón declarados, N = 2, D = 1.8 m, caída negativa / NaN / > 4 alturas,
Fase 6 bloqueada pieza a pieza con los cuatro exportadores): **ninguna excepción fuera de `ErrorProyecto` llega por el
pipeline**; todo lo malo se rechaza en la carga con `DatoInvalidoError` y lo que el método no cubre sale como aviso en
CLI, JSON y memoria. Las tres excepciones que sí encontré son de llamada directa a funciones públicas (H7) y dos
latentes (H6).

---

## B. HALLAZGOS — refutado con evidencia

### H1 · ALTA · `envolvente_hec14` calla los avisos de HEC-14 sobre la PIEDRA y entrega una protección incoherente

`proteccion_salida` sólo llama a `_avisos_del_contraste` y a `_avisos_de_la_piedra` bajo `if regla == REGLA_MANUAL and
apron is not None`. Con la regla que se le ofrece al dueño como la opción **más** conservadora desaparecen justo los dos
avisos que hablan del tamaño de la piedra («HEC-14 Ec. (10.4) pide una piedra mayor que Laushey» y «el D50 supera la
mayor clase de la Tabla 10.1: la salida pide un disipador»), y la envolvente sólo sube espesor y longitud: la piedra
sigue siendo la de Laushey.

Caso numérico (tubo Ø 0.90 m a sección llena, Q = 1.15 m³/s, V = Q/A = 1.808 m/s, TW = 0.36 m; `T-8-aud/rob8.py`):

```
regla manual           | d50 0.108 | apron D50 0.168, clase 3 | e 0.188  L 5.0
   - HEC-14 Ec. (10.4) pide una piedra mayor que Laushey (D50 = 0.168 m contra d50 = 0.108 m)
   - el espesor adoptado (0.188 m) es menor que la profundidad del apron de HEC-14 (0.600 m, clase 3)   [+2 avisos más]
regla envolvente_hec14 | d50 0.108 | apron D50 0.168, clase 3 | e 0.600  L 5.0
   - rige la envolvente con HEC-14: espesor 0.188 -> 0.600 m, longitud 5.00 -> 5.00 m                  [y NINGÚN otro]
```

A mano: Laushey 1.808²/30.38 = 0.108 m; HEC-14 `0.2·0.9·(1.15/(3.132·0.7684))^(4/3)·2.5 = 0.168 m`. Resultado bajo
«envolvente»: una capa de 0.60 m (la de la clase 3, 2.4 × 0.25 m) hecha con piedra de 0.108 m —5.6 veces su d50— y
rotulada «rige la envolvente con HEC-14» cuando HEC-14 pide un 56 % más de piedra. Y no es un caso raro: a sección
llena `D50_HEC14 / d50_Laushey = 2.04·(D^2.5/Q)^(2/3)`, mayor que 1 siempre que Q/D^2.5 < 2.9, es decir en toda
descarga llena corriente. El caso extremo (`rob7.py`, D50 de HEC-14 = 1.19 m, fuera de la Tabla 10.1): con «manual» sale
«la salida pide un disipador diseñado por HEC-14»; con «envolvente_hec14» sólo «rige la envolvente… 0.230 -> 0.495 m».

La línea de la CLI además sigue diciendo `Fase 6  d50 = …, espesor 0.770 m, longitud 5.400 m (num. 4.1.1.3.7 c))`: atribuye
al numeral del Manual un espesor y una longitud que con esa regla salen de la Tabla 10.1 de HEC-14.

**Corrección, por símbolo:** en `M6_proteccion.proteccion_salida`, sacar del `if regla == REGLA_MANUAL` los avisos que no
dependen de la regla (`d50 < apron.D50_requerido` y `apron.clase is None` de `_avisos_del_contraste`; la rama
`clase.clase is None` de `_avisos_de_la_piedra`). En `_regla_espesor_longitud`, cuando `apron.clase is None` decir que
HEC-14 no da apron (hoy «rige la envolvente» con la sola clase de la piedra adoptada). En `cli._volcar` (línea `Fase 6`)
separar el numeral del d50 del origen de espesor y longitud. Test: el caso de arriba bajo las dos reglas. Ver D1.

### H2 · ALTA · «Sin enrocado» se decide con una velocidad que el propio programa declara subestimada

Bajo control de salida con TW < y_c, `V_salida` es Q/A(y_c) (HDS-5 3.1.6) y `_aviso_tirante_de_borde` avisa que «V, el
Froude y el d50 quedan subestimados (no conservador)». Pero `velocidad_admisible_del_cauce` compara esa misma V con la
Tabla Nº 11 y, si no la supera, `proteccion_salida` devuelve `requerida=False`, `d50=None`, sin advertencias, y el CSV de
resumen deja las tres celdas vacías. Los dos avisos salen juntos y el resultado es el no conservador.

Caso (`T-8-aud/rob5.py`; A-02 de la línea base con `S_conducto = 0`, `tipo_terreno_receptor = graduado_grava`,
`regimen_flujo_descarga = permanente`, TW = 0.30 m):

```
D 0.9  ctrl SALIDA  TW 0.3  yc 0.4031  y_sal 0.4031  V_sal 1.739
requerida False   d50 None   V_adm 1.8
 - Proteccion de salida: la velocidad de salida se tomo con el tirante critico … quedan subestimados (no conservador)
 - Proteccion de salida: SIN enrocado porque la velocidad de salida no supera la admisible del terreno (Tabla Nº 11) …
KuQ/D^2.5 = 1.131   TW/D = 0.333
```

HEC-14 Figura 3.4 (pág. impresa 3-6, PDF 37, leída por imagen), curvas `KuQ/D^2.5` = 1.0 y 1.5 en TW/D = 0.33:
yo/D ≈ 0.365 y 0.43 → para 1.13, **yo/D ≈ 0.38** (frente a y_c/D = 0.448). Con el área de ese tirante,
V = 0.48/A(0.385·0.9) = **2.13 m/s > 1.80 m/s**: la salida SÍ supera la admisible. El programa dice «sin enrocado».

Orden de magnitud general, de la misma figura: descarga libre (TW/D → 0), curva 2.0 → yo/D = 0.47 con y_c/D = 0.604:
V_borde/V_c = A(y_c)/A(yo) = **1.37** y el d50 de Laushey, que va con V², queda en **1/1.87** del que daría la velocidad
de borde. Es decir, también cuando SÍ se dimensiona, el d50 que RIGE bajo control de salida con TW bajo puede estar a
la mitad. El marco C-01 que corrí (`run/c_1.txt`) cae en ese caso: V = 1.908 m/s al crítico, d50 = 0.120 m.
(La fuente llama a usar el crítico «not conservative, but… acceptable» sólo para formas sin figura; para la circular y
la rectangular da las Figuras 3.3 y 3.4.)

**Corrección, por símbolo:** en `M6_proteccion.proteccion_salida`, cuando `_aviso_tirante_de_borde(resultado)` no es
vacío y `admisible.supera` es False, no concluir: `requerida = None`, dimensionar como sin el dato y decir en el aviso
que la comparación no es concluyente con esa velocidad. La solución de fondo es digitalizar las Figuras 3.3 y 3.4 de
HEC-14 en M4 (decisión del dueño, D2). Mientras tanto, el aviso de borde debería dar la cota: «hasta un 37 % más de
velocidad en descarga libre (Fig. 3.4)». Afecta también, en menor medida, a la hoya cohesiva (`ρV²/τc`, hs ∝ V^0.36).

### H3 · MEDIA · El fundamento `F6.FROUDE` afirma lo que el paso 6.3 (y la primera auditoría) desmienten

`fundamentos.FROUDE_SALIDA.por_que`, que la memoria imprime bajo «Por qué se hace» (comprobado en
`T-8-aud/run/c_1.html`): «El Froude de la salida dice en que regimen entrega el conducto el agua al cauce: por debajo de
1 la lamina sale subcritica y se acomoda al tirante del receptor; por encima de 1 sale supercritica…». El veredicto del
mismo paso dice «Fr_e es el parametro de diseño de HEC-14, no el que clasifica el regimen», y `flujo_supercritico`
existe precisamente porque Fr_e no lo clasifica. Contraejemplos de la propia corrida: A-02 con S = 0 descarga al
tirante CRÍTICO con **Fr_e = 0.911** (por el `por_que`, «subcrítica y se acomoda al receptor»); el caso del test `aud2`
es supercrítico con Fr_e = 0.920.

Además `que_pasa_si_no_se_hace` dice «…regimen rapido, que es cuando un apron plano deja de bastar y la fuente pide un
disipador»: HEC-14 no dice eso. La Tabla 1.1 da al «Riprap apron» Froude **«na»** (pág. 1-2), y la Ec. (10.5) existe
para el flujo supercrítico. Es una afirmación atribuida a «la fuente» sin cita que la sostenga.

**Corrección:** reescribir `por_que` y `que_pasa_si_no_se_hace` de `F6.FROUDE` con lo que el paso hace (parámetro de
HEC-14; el régimen sale del tirante contra el crítico) y quitar la frase del disipador o sostenerla con una cita.

### H5 · MEDIA · El límite de 1500 mm rechaza el ejemplo resuelto de la propia fuente (60 in = 1.524 m)

La nota 8 dice «1500 mm **(60 in)**» y la Sec. 10.2 «1500 mm (60 in) or smaller»; el ejemplo CU de la pág. 10-19 usa
**D = 5.0 ft = 60 in**. `HEC14_APRON_ALTURA_MAX_M = 1.5` con `TOL_UMBRAL_NORMATIVO = 1e-9`:

```
M6.apron_hec14(Q_celda=85 ft³/s, D=5 ft, TW=1.6 ft)  ->  MetodoNoEvaluableError: … el conducto mide 1.52 m de alto y la
Tabla 1.1 de HEC-14 limita el apron de enrocado a conductos de hasta 1.50 m (nota 8)          (T-8-aud/rob9.py)
```

El docstring de `test_apron_es_adimensional_el_ejemplo_ingles_da_lo_mismo_en_SI` lo reconoce («queda justo sobre el
limite… el SI es la conversion redondeada») y lo esquiva escalando. Un límite que deja fuera el ejemplo de la fuente
está mal transcrito; y 60 in es un diámetro comercial de TMC (hoy no se alcanza porque `diametros_normalizados` va de
0.15 en 0.15 m y pasa por 1.50).

**Corrección:** `HEC14_APRON_ALTURA_MAX_M = 1.524` (60 in, el mayor de los dos equivalentes impresos), con las dos
cifras en el comentario; y entonces el ejemplo CU entra tal cual como dorado, sin λ.

### H6 · MEDIA · Tres lecturas del proyecto se imprimen como si fueran la fuente (una sola `Interpretacion` en todo T-8)

T-8 añade 40 citas y una única `Interpretacion` (`INTERPRETACION_SIN_ENROCADO`). Al menos estas tres lecturas, con
efecto numérico, viajan como «procedencia» o como `por_que`, no en la cara `class="interpretacion"`:

1. Los límites de TW con **D'** (`tw_min/tw_max = 0.4/1.0 · D_calc`): la fuente da los límites en D y ajusta «the culvert
   diameter»; aplicarlos a D' es una lectura. Efecto: con A-01 y TW = 0.80 m (< D = 0.90) el apron sale «no evaluable» con
   el mensaje «TW <= 1·D = 0.764 m», que llama D a D'.
2. «Si la velocidad calculada la supera, el Manual recomienda proteger el cauce» (`F6.V_ADMISIBLE`): el num. 4.1.1.3.7 c)
   dice «si la velocidad… es alta»; que «alta» sea «mayor que la Tabla Nº 11» es del proyecto. Lo mismo, en negativo,
   en `velocidad_admisible_del_cauce` (veredicto CUMPLE: «la Tabla Nº 11 no pide proteger»), en el aviso de
   `socavacion_salida` («la Tabla Nº 11 no pide revestir la salida»), en la v8 punto (b) y en `contrato_entradas.md`
   («el Manual no pide proteger»): son restos de la inversa que la primera auditoría mandó declarar.
3. La nota (5) b en las tres columnas (H4).

**Corrección:** una `Interpretacion` por lectura, colgada de `HEC14.10.2#TW`, `MC_HHD.4.1.1.3.7c#PROTECCION` y
`EG2013.511.08#T511_06`, y los textos de arriba en primera persona del proyecto.

---

## C. HALLAZGOS — sospecha fundada (no refutada con fuente primaria)

### H4 · MEDIA · Nota (5) b de la Tabla 511-06 aplicada a las tres columnas: en «15-50» RELAJA el requisito

`requisito_de_filtro(pasa_200_pct=30, indice_plasticidad=10, tipo_lecho="cohesivo")` → abertura **0.30 mm** donde la
celda dice **0,25**; con 10 % → 0.30 donde dice 0,43 (`rob9.py`). El PDF (pág. 1015 / 1023) trae DOS llamadas —«Tamaño de
Abertura Aparente (3) (4) (5)» en el rótulo y «0,22(5)» en la celda de «>50»— y DOS notas, (5) a y (5) b. La lectura
adoptada (la del primer auditor) asigna las dos notas a toda la fila; la alternativa natural es rótulo → (5) a
(diseño específico, vale para cualquier columna) y celda → (5) b (0.30 mm sólo donde está la llamada). El texto no lo
decide, y por eso no lo doy por refutado. Lo que sí es objetivo: (i) en la columna «15-50» la lectura adoptada va del
lado NO conservador (0.25 → 0.30 mm, una abertura mayor para una arena arcillosa); (ii) el paso lo imprime como hecho
(«La llamada (5) la lleva el rotulo de la fila: vale en las tres columnas»); (iii) el comentario de
`constantes_normativas.GEOTEXTIL_EROSION_IP_COHESIVO` dice todavía lo contrario («es en esa columna donde el proyecto
la aplica»). La tabla es la de AASHTO M 288, que no está en `normas/`: con ella a la vista se decide. Ver D4.

### H14 · (fuera del diff de T-8, pero gobierna el d50) · Salto de `V_salida` en la banda y_n(n_max) > y_c > y_n(n_min)

`rob4.py`, A-01 bajando la pendiente declarada: S = 0.0058 → control de entrada, V_salida = 3.160 m/s, d50 = 0.329 m;
S = 0.0056 → control de salida, V_salida = 2.412 m/s (crítica), d50 = 0.191 m. Un 3 % de pendiente mueve el d50 un
42 %, y en esa banda el tirante con n mínimo sigue siendo supercrítico (y(A = Q/V) = 0.507 m < y_c = 0.640 m). El
docstring de M6 dice que bajo control de entrada entra «la estimación ALTA»; en la banda no entra. Es de M4 (EXT-3), no
de T-8, y lo dejo como sospecha para quien toque M4; se suma a H2.

### (observación) `TERRENOS_COHESIVOS_T11` clasifica como cohesivas las filas «Arcilla arenosa / limosa (no coloidal)»
La Tabla Nº 11 declara fuente «Manual de Carreteras de California», que no está en `normas/`; por los valores (0.75,
0.90 m/s) y el «(no coloidal)» esas filas parecen francos («loam») traducidos como «arcilla». Sólo alimenta el aviso de
incoherencia terreno/lecho, que con un lecho no cohesivo declarado daría un falso positivo. Sin la fuente no se refuta.

---

## D. HALLAZGOS BAJOS (refutados, de poco alcance)

- **H7 · BAJA · Guardias de segunda línea incompletas (TypeError fuera de `ErrorProyecto`).**
  `M6.velocidad_admisible_del_cauce(V=…, tipo_terreno=["grava_fina"], …)` y `M6.proteccion_entrada(resultado=r,
  tipo_embocadura=["x"])` → `TypeError: unhashable type: 'list'` (`rob3.py`); con `regimen_flujo` lista sí sale
  `DatoInvalidoError`. Por el pipeline no se alcanza (`_de_catalogo_externo` exige `str`). Corrección: `isinstance(x, str)
  and x in …` en los dos sitios. (`donde` inválido lanza `ValueError`: es error de programa, pero es público.)
- **H8 · BAJA · Verbo de obligación sobre una recomendación.** «lo que HEC-14 num. 5.1.2 **manda** usar a falta de ese
  dato» (aviso de `socavacion_salida`, `origen_t` de la hoya, docstrings): la cita `HEC14.5.1.2#T30` es
  `RECOMENDACION` («it is recommended that…»). Sale por CLI, JSON y memoria. Corrección: «recomienda».
- **H9 · BAJA · Cita que no sostiene lo que se le cuelga.** El paso 6.14 y la ficha de
  `referencia_profundidad_socavacion` apoyan «la Figura 10.1 mide hs desde la solera de salida» en `HEC14.10.1#DOS_D50`,
  cuyo literal es «The basin is pre-shaped and lined with riprap that is at least 2D50 thick». La figura (vista por
  imagen, pág. 10-1) sí lo muestra; la cita no. Corrección: una cita propia de la Figura 10.1, o «The riprap floor is
  constructed at the approximate depth of scour, hs» de la misma página.
- **H10 · BAJA · Mensajes y comentarios que dicen otra cosa.** (a) `apron_hec14`: «TW <= 1·D = 0.764 m» con D = 0.90 m
  (es D'). (b) `hoya_de_socavacion_hec14`: el `LimiteNumericoError` nombra como par culpable «Q_celda y altura del
  conducto» cuando lo provoca `D84/D16` (probado con 1e300 / 1e-300). (c) `servicio._numero_externo`: «no un numero
  (SI, metros o m3/s)» para `duracion_caudal_pico_min`, que va en minutos. (d) el comentario de
  `GEOTEXTIL_EROSION_IP_COHESIVO` (H4). (e) `modelos.ProteccionSalida.V`: «siempre `ResultadoHidraulico.V_erosion`»,
  falso desde EXT-3 (anterior a T-8, en un bloque que T-8 reescribió).
- **H11 · BAJA · CSV de resumen: «sin enrocado» son tres celdas vacías**, iguales a las de una Fase 6 bloqueada. Falta
  una columna (`proteccion_requerida`) o un texto; hoy quien lea sólo el CSV no distingue «no hace falta» de «no se
  calculó».
- **H12 · BAJA · Datos sin techo físico.** Entran `duracion_caudal_pico_min = 1e9` (hoya × 2.8 respecto de la de 30 min: 3.13 m en A-01 con 0.20 m de caída),
  `profundidad_socavacion_estimada_m = 1e6`, `Sv_Pa = 1e300` (→ «estimada» de 1.4e-53 m) y `D84_m = 5.0`. Ninguno rompe;
  ninguno es un dato. Y las dos claves numéricas admiten cadena (`"1.0"`) por la puerta general mientras que dentro de
  `material_lecho_salida` la cadena se rechaza. Corrección: entradas en `dominios.py` / `_DOMINIO_DE_CLAVE`.
- **H13 · BAJA · Transcripción fijada sólo en parte por los tests.** `test_la_tabla_11…` fija 4 de 13 filas;
  `test_las_tablas_de_hec14…` no fija las columnas de ancho de las Tablas 5.2/5.3 ni las Tablas 5.1/5.4 (éstas sólo por
  los ejemplos). Las leí todas del PDF y están bien; un cambio en `Ch["ancho"]` de Hd = 4 hoy no lo ve nadie.
- **H15 · BAJA · Dos `None` que se resuelven en silencio (latentes: M4 los llena siempre).**
  `apron_hec14(y_salida=None)` → `bool(None)` = «no supercrítico» sin aviso: con el resultado de A-01 sin `y_salida_m`,
  D50 = 0.171 m (clase 3) en vez de 0.252 m (clase 4). Y un `ResultadoHidraulico` con `TW_m` o `y_critico` en `None` hace
  que el `DatoInvalidoError` de la pieza de CONTRASTE tumbe toda `proteccion_salida` (el punto pierde su d50 de
  Laushey), contra lo que promete el docstring del módulo («lo que falta en una pieza no debe dejar al punto sin las
  demás»). Corrección: `supercritico is None` → aviso «régimen no determinado»; recoger `DatoInvalidoError` del apron
  como aviso, o validar antes de calcular Laushey.

---

## E. Coherencia ingenieril: dirección de cada [A]/[C] (punto 3)

| Criterio | Valor de archivo | Dirección | Dictamen |
|---|---|---|---|
| `regla_espesor_longitud_proteccion_salida` | `manual` | NO conservadora frente a HEC-14 (A-01: 0.592 m contra 0.770 m; 5.00 contra 5.40 m) | Declarado y avisado en todo punto. La alternativa tiene el defecto H1 |
| `duracion_caudal_pico_socavacion_min` [C] | 30 min | NO conservadora (extremo bajo de la ventana); ×1.161 a 360 min con θ = 0.06 (comprobado: 12^0.06) | Es lo que la fuente recomienda; avisado con la cifra. D3 |
| `lectura_coeficientes_socavacion_hec14` | envolvente | Conservadora en profundidad, ancho y longitud (toma el mayor también donde Ch baja) | Bien. Salto en Hd = 0⁺ (1.00 → 1.22), aceptable |
| `referencia_profundidad_socavacion` | fondo del cauce | Conservadora: la hoya queda la caída más abajo (0.69 m en A-01) | Bien |
| `tipo_proteccion_entrada` | emboquillado | Sin efecto numérico | Bien: es lo único que las Láminas 02/02-A/03 dibujan |
| Fuera de rango | — | TW > D, D > 1.5 m, marco, N > 1, IP fuera de 5-16, Hd > 4: no evaluable → aviso; TW < 0.4D y t < 30: acotado como la fuente | Coherente con lo que cada texto prohíbe («should be limited», «Limitations») o sólo describe |
| Profundidad para el desplante (T-7a) | — | Sin lecho: `None` y aviso (no supone suelo). Con lecho: peor caso local, a 30 min. La declarada gana aunque sea MENOR (avisado) | Ver D3 y H2 (V subestimada en cohesivo) |

Una sola regla de régimen: sí en el código (`flujo_supercritico` para el Froude y la Ec. 10.5); el texto del fundamento
la contradice (H3).

---

## F. Tests y mutación (punto 7)

**Mutación, remedida.** Arnés de EXT-11 sobre una copia con git (`T-8-aud/mut/`), M6 entero contra
`tests/test_t8_proteccion.py`, dos trabajadores:

```
python3 -m tests.apoyo.mutacion --modulo M6_proteccion --objetivo tests/test_t8_proteccion.py --trabajadores 2
514 mutantes generados en 1 modulos
PRIMERA VUELTA (tests/test_t8_proteccion.py): 472/514 muertos, score 0.9183          (T-8-aud/mut_M6.log, mut_M6.json)
```

**La cifra de la ficha T8-06 (472 de 514, 91.8 %) es exacta**, y su reparto de los 42 vivos también: 35 de banda de
tolerancia (`±TOL_UMBRAL_NORMATIVO`, `<` frente a `<=`), 3 equivalentes (`_aviso_terreno_contra_lecho` `or`→`and`;
`coeficiente_de_tabla` `x < abscisas[-1]` y `len(abscisas) - 1`), 2 de la guardia de salida de la hoya y 2 de
presentación (`cifras=0` de ρ; `return ''` de `_nota_de_sensibilidad`). **Ninguno esconde un defecto vivo**: probé a mano
el comportamiento en cada borde (`rob10.py`) y es el correcto —IP = 5 y 16 entran, 4.999 y 16.001 no; Hd = 4 da
Ch = 1.34; TW = D se evalúa; TW = 0.4D no se acota; espesor = 2.0·d50 no avisa; V = V_adm no «supera»; t = 30 no se acota;
d50 = 0.125 m es clase 1 y 0.1250001 m, clase 2—.

**Pero «banda de tolerancia» agrupa seis bordes INCLUSIVOS de la fuente que ningún test fija**, y varios son valores
naturales de entrada (parte de H13): IP = 5 e IP = 16 (enteros de laboratorio; mutantes 30-31: `IP_MIN + TOL` deja fuera
el 5 y sigue verde), Hd = 4 (33-34), TW = 1.0·D (6, 8), el techo 2.0 de la ventana de `espesor_proteccion_salida` (23-24:
con `+ TOL` el aviso «bajo el piso» saldría también declarando 2.0, que es justo el valor con que la ficha dice que
deja de salir), la igualdad «greater than or equal» de la clase (9-10, 17-18) y V = V_adm (3-4). Un test por borde
los mata; hoy un cambio de signo en la tolerancia de cualquiera de ellos pasa la suite.

**Tests vacuos:** no encontré ninguno. Los oráculos son los ejemplos impresos y aritmética escrita que rehice (A.2);
los de la carga comprueban el MOTIVO y no sólo la clave. Aserciones débiles, que no vacuas:
`test_un_lecho_uniforme…` y `test_conducto_mayor_de_1500_mm…` (`> 0`), `test_con_el_barril_horizontal…`
(`p.apron is None or …`). Huecos de cobertura que sí importan: (i) ninguno ejerce `envolvente_hec14` con
`apron.D50_requerido > d50` ni con `apron.clase is None` —es el hueco por el que pasa H1—; (ii) ninguno cruza
`_aviso_tirante_de_borde` con `requerida is False` (H2); (iii) el ejemplo CU sólo entra escalado (H5).

**Suite entera (una sola corrida, sobre la copia):** `NORMAS_DIR=… python3 -m pytest -q -p no:cacheprovider --no-header` sobre
`T-8-aud/mut/` → `1 failed, 4959 passed, 16 skipped in 334.92s` (**collected 4976**; `T-8-aud/suite.log`). El único rojo,
`test_ext8_rendimiento_gui.py::test_pc10_import_cli_cabe_en_el_presupuesto_sin_weasyprint` («`import cli` cuesta 0.381 s…
el presupuesto es 0.3 s»), **es un artefacto de mi corrida, no del árbol**: la lancé con `PYTHONDONTWRITEBYTECODE=1`
(para no dejar `.pyc`), y sin caché de bytecode el subproceso recompila en cada import. Repetido solo y sin esa
variable: `1 passed` dos veces. El par que declara CLAUDE.md para «PyMuPDF sí · Tk no» con `NORMAS_DIR`
(**4960 passed / 16 skipped / 4976 collected**) se sostiene; lo medido en una pasada es 4959 + 1 + 16 = 4976.
`tests/test_t8_proteccion.py`: 96 passed en 1.4 s.


---

## G. Decisiones del dueño

- **D1.** `regla_espesor_longitud_proteccion_salida`: `manual` o `envolvente_hec14`. Y, si es la envolvente, si debe
  alcanzar también al **tamaño de la piedra** (hoy no: H1). Recomendación: corregir H1 antes de decidir; con la
  envolvente, el d50 debería ser el mayor de Laushey y la Ec. (10.4), o al menos avisarse.
- **D2.** Tirante de borde: digitalizar las Figuras 3.3 y 3.4 de HEC-14 (M4) o, como mínimo, no concluir «sin enrocado»
  bajo control de salida con TW < y_c (H2). Recomendación: lo segundo ya; lo primero en un prompt propio.
- **D3.** Qué profundidad se entrega al desplante cuando falta la duración del pico: la de 30 min (lo que HEC-14
  recomienda) o la del techo de la ventana (360 min, +16 %). La fuente dice además que a los 30 min se ha alcanzado
  «2/3 to 3/4» de la máxima.
- **D4.** Nota (5) b de la Tabla 511-06: en las tres columnas (hoy) o sólo en «>50» (H4). Recomendación: conseguir
  AASHTO M 288 y, mientras, la lectura que no relaja la columna «15-50».
- **D5.** Límite del apron: 1.500 m o 60 in = 1.524 m (H5). Recomendación: 1.524.
- **D6.** Si la salida puede quedar «sin enrocado» sólo por la Tabla Nº 11, cuando el HDS-5 pide además la inspección
  de campo (hoy: sí, con aviso).

## H. Scripts de reproducción

Todos en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-8-aud/`,
con `NORMAS_DIR=/home/user/andy-rba30/normas python3 <script>`: `rob.py` (apoyo), `rob1.py` (seis datos externos),
`rob2.py` y `rob6.py` (pipeline y exportadores), `rob3.py` (funciones públicas), `rob4.py` (banda de régimen),
`rob5.py` (H2), `rob7.py` y `rob8.py` (H1), `rob9.py` (H4, H5, H10-a); `lb/` (línea base, base contra auditado);
`run/` (marco, envolvente); `mut_M6.log` / `mut_M6.json` (mutación); `pg.py` (lector de PDF) y los PNG de las figuras.
