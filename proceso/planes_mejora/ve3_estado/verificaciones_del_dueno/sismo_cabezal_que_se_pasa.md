# Evento Extremo I del cabezal: por qué no cierra, y qué se nos está pasando

Revisión independiente, 2026-11-18. No se modificó ningún repositorio. Los números salen del árbol
de trabajo sobre `9647d35` (tiene cambios sin confirmar de otros agentes) corrido con
`tests.apoyo.validacion_integral.juego_titular()`. «Pág.» es la página impresa.

## Resumen

1. **No hay error aritmético en el ensamble.** Las dos combinaciones de 11.6.5.1, el piso estático
   del 50 % de P_AE, la inercia del relleno sobre el talón, φ = 0.8 en portante y la excentricidad
   están bien. K_AE = 0.852 y K_A = 0.254 los reproduje a mano.
2. **Sí se está pasando algo, y es el agua.** La corrida titular calcula el sismo con el relleno
   lleno de agua hasta arriba (`drenaje_trasdos` = `sin_drenaje`). C11.6.5.3 (pág. 11-31) pide para
   el sismo «the time-averaged mean groundwater elevation». El freático del juego está bajo la zapata.
3. Esa agua es el factor de primer orden: sube H/N de 0.65 a 0.99 en la salida de A-01. Con el
   relleno drenado y k_h = 0.50 sin reducir, la entrada ya pasa la portante y el deslizamiento
   falla por 4 a 6 % en los dos cabezales.
4. **La exención de 11.5.4.2 no aplica.** Exige Zona Sísmica 1 a 3 o A_s ≤ 0.4 g. Aquí A_s = 0.50 g
   (0.45 g con Clase E) y S_D1 ≈ 0.63 a 0.72 (Zona 4, con mi lectura de S1 ≈ 0.47 g del mapa).
5. **k_h por desplazamiento existe** (Apéndice A11.5, págs. 11-154 a 11-158), además del 0.5·k_h0.
   Para 1, 2 y 4 in da k_h ≈ 0.29 a 0.31, 0.24 a 0.26 y 0.20 a 0.22. El Manual de Puentes traduce
   11.6.5.2.2 pero no el Apéndice A11.
6. Con relleno drenado y k_h = 0.25, A-01 **cierra con B/H ≈ 1.0** aplicando los factores de
   inclinación. Cierra también con k_h = 0.31 (1 in) y hasta con k_h = 0.40 (B/H 1.2 y 1.7).
7. **Factores de inclinación:** `aplicar` es la letra del artículo y es defendible; `omitir` lo
   permite el comentario con empotramiento modesto. No es un error; es una elección [A] que cuesta
   un 30 % de zapata en la salida. El «0.59 kPa admisible» es el deslizamiento visto por la portante.
8. **Incoherencia del valor de archivo:** k_h = k_h0 es, por definición de la fuente, «zero wall
   displacement». Un muro libre que no pasa el deslizamiento con k_h0 no colapsa: se desplaza. Las
   zapatas de 1.7·H equivalen a exigir menos de 3 mm de desplazamiento.
9. La alcantarilla misma está exenta de sismo (3.10.1, pág. 3-70; 12.6.1, pág. 12-14; Manual de
   Puentes pág. 121). El cabezal no hereda esa exención de forma expresa: se trata como muro.
10. **Recomendación:** corregir el nivel de agua sísmico (corrección), declarar el drenaje ([A]
    razonable y exigido por 11.6.6), y llevar al Propietario la aceptación de 1 a 2 in de
    desplazamiento. Con las dos primeras más la tercera, A-01 cierra con zapatas normales.

---

## 1. Exención de análisis sísmico (AASHTO 11.5.4.2)

**Lo que dice la fuente** (págs. 11-9 y 11-10; PDF 1478 y 1479):

> «A seismic design shall not be considered mandatory for walls located in Seismic Zones 1 through
> 3, or for walls at sites where the site adjusted peak ground acceleration, As, is less than or
> equal to 0.4g, unless one or more of the following is true: • Liquefaction induced lateral
> spreading or slope failure, or seismically induced slope failure, due to the presence of
> sensitive clays […] • The wall supports another structure that is required, based on the
> applicable design code or specification for the supported structure, to be designed for seismic
> loading and poor seismic performance of the wall could impact the seismic performance of that
> structure.»

El comentario (pág. 11-11) añade que conviene analizar en Zona 2 o más si el muro supera 30.0 ft, o
si el relleno no cumple el drenaje de las especificaciones de construcción «due to the possibility
that the backfill will not be adequately drained to prevent water build up in the backfill».

**¿Las cumple el cabezal?** No.

| Condición | Valor del sitio | ¿Cumple? |
|---|---|---|
| A_s ≤ 0.4 g | 0.50 × 1.0 = 0.50 g (C, D); 0.50 × 0.9 = 0.45 g (E) | No |
| Zona Sísmica 1 a 3 (S_D1 ≤ 0.50, Tabla 3.10.6-1; Manual de Puentes Tabla 2.4.3.11.5-1, pág. 125) | S_D1 = F_v·S1 ≈ 0.63 (C), 0.72 (D), 1.13 (E) | No: Zona 4 |
| Altura menor de 30 ft | 2 a 5 m | Sí |
| El muro no soporta estructura con diseño sísmico obligatorio | la alcantarilla está exenta | Sí |

S1 ≈ 0.47 g es **mi lectura** del mapa de 1.0 s del Apéndice A3 del Manual de Puentes (pág. 553,
PDF 554) para La Unión, entre las curvas 0.46 y 0.48. No es un dato [S] del proyecto:
`datos_sitio.py` sólo tiene el PGA. F_v sale de la Tabla 3.10.3.2-3 (pág. 3-106). La
conclusión no depende de la lectura fina: haría falta S1 < 0.36 g para caer en Zona 3 con Clase C.

Sólo en roca Clase B (F_v = 1.0, S_D1 ≈ 0.47) el sitio sería Zona 3 y el análisis no sería
obligatorio. El proyecto descarta la roca (llanura arenosa del Bajo Piura), y en roca k_h0 sube a
1.2·F_pga·PGA.

**El Manual de Puentes no transcribe 11.5.4.2.** No encontré el texto en el volcado. Lo que sí dice
(2.4.3.11.1, pág. 121): «No se requerirá considerar acciones de sísmo sobre alcantarillas tipo cajón
y otras estructuras totalmente enterradas. Excepto cuando estas atraviesan fallas activas.» Es la
traducción de AASHTO 3.10.1 (pág. 3-70): «Seismic effects for box culverts and buried structures
need not be considered, except where they cross active faults.» AASHTO 12.6.1 (pág. 12-14) lo
repite, y su comentario llama a los cabezales «appurtenances such as headwalls and railings».
Ninguna de las tres frases exime al cabezal. Leerlo así sería una interpretación [A], no norma.

**Efecto sobre A-01:** ninguno. La exención no está disponible.

Nota aparte: sobre el mapa de PGA (pág. 552, PDF 553) La Unión queda entre las curvas 0.50 y 0.52.
El 0.50 del archivo es plausible, quizá 0.51. La trazabilidad de esa lectura sigue abierta
(pendiente 1.4), como ya declara `datos_sitio.py`.

## 2. k_h en función del desplazamiento (11.6.5.2.2 y Apéndice A11.5)

**Lo que dice 11.6.5.2.2** (pág. 11-28; PDF 1497):

> «If the wall is free to move laterally under the influence of seismic loading and if lateral wall
> movement during the design seismic event is acceptable to the Owner, kh0 should be reduced to
> account for the allowed lateral wall deformation. […] Where the wall is capable of displacements
> of 1.0 to 2.0 in. or more during the design seismic event, kh may be reduced to 0.5kh0 without
> conducting a deformation analysis using the Newmark method (Newmark, 1965) or a simplified
> version of it.»

> «A Newmark sliding block analysis or a simplified form of that type of analysis should be used to
> estimate lateral deformation effects, unless the Owner approves the use of more sophisticated
> numerical analysis methods […]»

C11.6.5.2.2: «the amount of permanent ground displacement associated with kh = 0.5kh0 will in most
cases be less than 1.0 to 2.0 in. (i.e., use of kh = 0.5kh0 provides conservative results)». Y
también: «a well-designed gravity or semigravity wall could slide several inches and perhaps even a
foot or more, as well as tilt several degrees, without affecting the function of the wall or
causing collapse».

El artículo no da la ecuación; remite al Apéndice A11, que da tres métodos (pág. 11-154: «The three
alternative design procedures should not be mixed together in any way»).

- **A11.5.1, Kavazanjian et al. (1997)** (pág. 11-155): k_h = 0.74·A_S·(A_S/d)^0.25, con d en
  pulgadas. «This equation should not be used for displacements of less than 1.0 in. or greater
  than approximately 8 in.»
- **A11.5.2, NCHRP 611** (pág. 11-157; PDF 1626, leída en imagen): log d = −1.51 − 0.74·log(k_y/k_h0)
  + 3.27·log((1 − k_y)/k_h0) − 0.80·log k_h0 + 1.59·log(PGV), con PGV (in/s) = 38·F_v·S1
  (ec. A11.5.2-5). «Note that the above displacement equations represent mean values.» La
  reducción por dispersión de onda (α) sólo vale para h mayor de 20.0 ft: aquí α = 1.
- **A11.5.3, Bray et al.**: pide el período del muro y la magnitud. No lo evalué.

**Aviso sobre la ec. A11.5.2-3.** Tal como está impresa, el segundo término es (1 − k_y)/k_h0. Con
esa forma, k_y = 0.5·k_h0 da 65 in, lo que contradice al propio C11.6.5.2.2. La ecuación gemela
A11.5.2-4 imprime 1 − k_y/k_h0, y con esa forma sale 1.4 a 1.8 in, coherente con el comentario. Creo
que es una errata de la 9.ª edición, pero no pude verificarlo contra NCHRP 611, que no está en el
repositorio de normas. Los valores de abajo usan 1 − k_y/k_h0 y quedan como **estimación sin fuente
primaria verificada**. Los de Kavazanjian sí son literales.

**k_h para el sitio** (k_h0 = 0.50; S1 ≈ 0.47 g, mi lectura):

| Desplazamiento | Kavazanjian (A11.5.1) | NCHRP 611, Clase C (PGV 23.8) | Clase D (PGV 27.3) | Clase E (PGV 42.9) |
|---|---|---|---|---|
| 1 in (25 mm) | 0.311 | 0.272 | 0.285 | 0.322 |
| 2 in (51 mm) | 0.262 | 0.229 | 0.243 | 0.286 |
| 4 in (102 mm) | 0.220 | 0.182 | 0.197 | 0.245 |
| con k_y = 0.25 (0.5·k_h0) | — | 1.4 in | 1.8 in | 3.7 in |

El 0.5·k_h0 = 0.25 equivale a 1.4 a 1.8 in en Clase C o D. En Clase E ya no es «1 a 2 in»: son
3.7 in, y eso importa porque la clase de sitio sigue sin medir.

**El Manual de Puentes** (2.8.1.1.14.2.2, págs. 254 y 255) traduce el artículo completo: «Donde el
muro es capaz de desplazamientos de 1.0 a 2.0 in o más durante el evento sísmico de diseño, kh
puede ser reducido a 0.5kh0 sin llevar a cabo un análisis de la deformación mediante el método
Newmark […]» y «Un análisis del deslizamiento del block de Newmark o un análisis simplificado de
ese tipo, serán usados para estimar los efectos de las deformaciones laterales». No traduce el
Apéndice A11 ni sus ecuaciones.

**¿El programa lo hace bien?** Implementa las dos ramas del artículo (1.0 y 0.5). No implementa
A11.5. La ficha de `factor_muro_eleccion` es correcta en lo que cita. Su justificación («el cabezal
va empotrado en el terraplén y no tiene desplazamiento lateral admisible garantizado») es una
elección, no un hecho: ver el punto 4.3.

## 3. Factores de inclinación en la portante

**Lo que dice la fuente.** 10.6.3.1.2a (págs. 10-70 y 10-71; PDF 1359 y 1360) pone i_c, i_q, i_γ
dentro de N_cm, N_qm y N_γm, con «H = unfactored horizontal load», «V = unfactored vertical load».
El comentario C10.6.3.1.2a dice, literal:

> «However, in practice, not all of the factors included in these equations have been routinely
> used.»

> «Most geotechnical engineers nationwide have not used the load inclination factors.»

> «Therefore, the factors do not take into consideration the effects of depth of embedment.
> Meyerhof further showed that for footings with a depth of embedment ratio of Df /B = 1, the
> effects of load inclination on bearing resistance are relatively small.»

> «The combination of the resistance factors and the load inclination factors may be overly
> conservative for footings with an embedment of approximately Df /B = 1 or deeper because the load
> inclination factors were derived for footings without embedment. In practice, therefore, for
> footings with modest embedment, consideration may be given to omission of the load inclination
> factors.»

No dice nada específico para cargas sísmicas, ni que el ancho efectivo ya cubra la inclinación.
11.6.3.2 (pág. 11-21) sólo da σ_v = ΣV/(B − 2e) y no menciona los factores. 11.5.8 (pág. 11-18) fija
0.8 para la portante de muros de semigravedad en Evento Extremo. El Manual de Puentes transcribe
las ecuaciones (2.8.1.3.1.2a, pág. 270) y no encontré el comentario de la omisión.

**¿`aplicar` es la lectura correcta?** Es la letra del artículo y la ficha la describe con
fidelidad. No es «la más exigente sin base». Tampoco es obligada: el comentario abre la puerta con
empotramiento modesto. El cabezal de salida tiene D_f/B entre 0.2 y 0.45, y sólo cuenta lo que queda
bajo la hoya de socavación. Está lejos del D_f/B = 1 donde el comentario dice que el efecto es
pequeño, así que aplicar tiene más apoyo físico aquí que en una zapata de puente enterrada.

**El programa lo hace bien:** usa H y V sin factorar y n = 2 de zapata corrida.

**Lo que hay que entender del «0.59 kPa».** En la titular H/V llega a 0.92 a 0.99. Con
i_γ = (1 − H/V)³ la resistencia se anula. Pero con φ_f = 32° la zapata desliza desde H/V = 0.625: la
fila E1 no está midiendo una falla portante distinta, repite la falla por deslizamiento. Cuando el
deslizamiento cierra, H/V baja a 0.45 a 0.57 y la portante con inclinación vuelve a valores normales.

**Efecto sobre A-01:** `omitir` cierra la portante en todos los casos, pero no arregla el
deslizamiento. Con relleno drenado y k_h = 0.25, la salida pide B = 2.95 m con `aplicar` y 2.25 m
con `omitir`.

## 4. Otras comprobaciones

### 4.1 Combinaciones y cargas: correctas

11.6.5.1 (págs. 11-25 y 11-26): «PIR = kh(Ww + Ws)», con «Ws = the weight of soil that is
immediately above the wall, including the wall heel», y los dos casos «100 percent of the seismic
earth pressure, PAE, with 50 percent of the wall inertial force, PIR» y «50 percent of PAE but no
less than the static active earth pressure force […] with 100 percent of the wall inertial force,
PIR». C11.6.5.1 (pág. 11-27): «the inertial force for the soil mass over the wall heel is included
when determining the external stability of the wall».

Comprobé la salida de A-01 en la titular (kN/m), caso 50 % P_AE + 100 % P_IR:

| Carga | H | Factor | Aporta |
|---|---|---|---|
| EH + incremento sísmico (P_AE horizontal = 22.5 + 78.3) | 100.8 | 0.5 | 50.4 |
| Inercia del muro | 36.4 | 1.0 | 36.4 |
| Inercia del relleno sobre el talón | 118.8 | 1.0 | 118.8 |
| Agua del relleno (WA) | 46.1 | 1.0 | 46.1 |
| Sobrecarga viva (γ_EQ = 0.5) | 10.2 | 0.5 | 5.1 |
| **Total** | | | **256.8** |

Coincide con el programa. N = 258.5 kN/m, resistencia = 258.5·tan 32° = 161.5. No se aplica k_h a
nada que la norma no pida. K_AE = 0.852 coincide con Mononobe-Okabe a mano (φ = 34°, δ = 22.78°,
relleno horizontal en el plano del talón).

### 4.2 El agua bajo sismo: aquí está el defecto

La titular usa `drenaje_trasdos` = `sin_drenaje`. El programa llena entonces el relleno de agua
hasta su superficie (3.07 m en la salida) **también en la condición sísmica**. Eso mete a la vez:
46.1 kN/m de empuje hidrostático, 73.0 kN/m de subpresión que quita fricción, el peso saturado en la
inercia del talón y el incremento sísmico con el peso total.

C11.6.5.3 (pág. 11-31; PDF 1500) dice:

> «The groundwater within the active wedge or submerged conditions […] can influence the magnitude
> of the seismic active earth pressure. The time-averaged mean groundwater elevation should be used
> when assessing groundwater effects.»

11.6.6 (pág. 11-35) es la regla estática: «Backfills behind abutments and retaining walls shall be
drained or, if drainage cannot be provided, the abutment or wall shall be designed for loads due to
earth pressure, plus full hydrostatic pressure due to water in the backfill.» C3.4.1 (pág. 3-11)
da el mismo criterio de no concurrencia para la socavación con sismo.

El registro ya conoce la frase: la nota de la cita `AASHTO_LRFD_9.C11.6.5.3#AGUA_TOTAL` en
`src/normativa/citas.py` dice que el comentario «pide el nivel medio del agua en el tiempo». El
código no lo aplica: `M9.cargas_del_cabezal` usa el mismo `h_w` en estática y en sismo. Con el
freático del juego (3.0 m bajo el terreno, por debajo de la zapata) el nivel medio no moja el plano
de empuje, y el sismo debería calcularse en seco aunque el trasdós no drene.

El verbo es «should» y está en comentario: es recomendación, no mandato. Aun así, combinar el
relleno lleno hasta arriba con el sismo de 1000 años es lo que la fuente desaconseja.

### 4.3 «Muro que no cede» y deslizamiento a la vez

11.6.5.2.1 (pág. 11-27) define k_h0 como el coeficiente «assuming zero wall displacement occurs».
C11.6.5.4 (pág. 11-32) da los ejemplos de muro que no cede: «integral abutments, abutment walls
with structural wing walls, tunnel portal walls, and tied back cylinder pile walls», y habla de
«walls restrained from movement by structures, batter piles, or anchors».

Un muro que no cede es un muro **restringido por algo**. Si ese algo existe (el cajón monolítico,
los aleros estructurales), es quien resiste la fuerza horizontal, y verificar el deslizamiento como
muro libre sin contarlo no describe la estructura. Si no existe, el muro es libre y cede. La titular
toma lo peor de las dos lecturas: carga de muro restringido y resistencia de muro libre. Es
conservador, pero no es coherente.

Lo mismo en cifras: un muro que no pasa E3 con k_h0 no colapsa, se desplaza. Con la ecuación de
A11.5.2 (misma salvedad del punto 2), Clase D:

| k_y del muro | B/H que pide la salida (drenado, `aplicar`) | Desplazamiento medio estimado |
|---|---|---|
| 0.40 | 1.69 | 2 mm |
| 0.35 | 1.40 | 7 mm |
| 0.31 | 1.23 | 16 mm |
| 0.285 | 1.16 | 25 mm |
| 0.25 | 1.05 | 45 mm |
| 0.20 | 0.98 | 97 mm |

Pasar de B/H 1.05 a 1.69 compra 43 mm menos de desplazamiento en un cabezal de alcantarilla.

### 4.4 Lo que el modelo plano no ve

El cabezal de A-01 mide 1.7 m de largo y se calcula por metro como muro indefinido, con zapatas de
3.4 y 4.9 m de ancho. El conducto que lo atraviesa, los aleros y el rozamiento lateral no entran.
No tengo cita normativa que cuantifique esto, así que queda como observación: `marco_estabilidad_
cabezal` ya declara que modelarlo como muro de semigravedad es hipótesis del proyecto.

### 4.5 Sensibilidad medida sobre A-01

Corridas con el juego titular cambiando sólo lo indicado. Los k_h distintos de 0.50 y 0.25 los
obtuve sobrescribiendo en memoria la constante de reducción, sin tocar archivos. «Tope» es el
ancho máximo de la regla de dimensionamiento.

| Caso | Entrada (H = 1.85 m) | Salida (H = 2.81 m) | ¿Cierra? |
|---|---|---|---|
| Titular: sin drenaje, k_h 0.50, `aplicar` | B 3.38 (tope); E1 72.8/7.8; E3 128.6/81.4 | B 4.85 (tope); E1 100.6/0.59; E3 256.8/161.5 | No |
| Sin drenaje, k_h 0.50, `omitir` | E1 pasa; E3 128.6/81.4 | E1 pasa; E3 256.8/161.5 | No |
| Sin drenaje, k_h 0.25, `aplicar` | B 3.38; pasa | B 4.75; E1 68.0/43.2; E3 150.7/150.7 | No |
| Sin drenaje, k_h 0.20, `aplicar` | B 2.88; pasa | B 4.75; pasa | Sí, B/H 1.6 a 1.7 |
| **Drenado**, k_h 0.50, `aplicar` | B 3.38; E1 pasa; E3 100.4/95.0 | B 4.85; E1 81.7/33.2; E3 195.7/188.6 | No, por 4 a 6 % en E3 |
| Drenado, k_h 0.50, `omitir` | E3 100.4/95.0 | E3 195.7/188.6 | No |
| Drenado, k_h 0.40, `aplicar` | B 2.28 | B 4.75 | Sí, B/H 1.2 y 1.7 |
| Drenado, k_h 0.35, `aplicar` | B 1.88 | B 3.95 | Sí, B/H 1.0 y 1.4 |
| Drenado, k_h 0.31 (1 in, Kavazanjian), `aplicar` | B 1.78 | B 3.45 | Sí, B/H 1.0 y 1.2 |
| **Drenado, k_h 0.25 (0.5·k_h0), `aplicar`** | B 1.78 | B 2.95 | **Sí, B/H 1.0** |
| Drenado, k_h 0.25, `omitir` | B 1.78 | B 2.25 | Sí, B/H 1.0 y 0.8 |
| Drenado, k_h 0.20 (4 in), `aplicar` | B 1.78 | B 2.75 | Sí |

El caso «drenado» equivale, para la condición sísmica de este juego, a corregir el nivel de agua
del punto 4.2: en los dos el plano de empuje queda seco.

## 5. Por qué no cumple, en una frase

Porque la titular apila tres valores de archivo del lado más exigente (relleno lleno de agua
durante el sismo, k_h = PGA completo de 0.50 g y factores de inclinación) sobre una fundación de
φ_f = 32° sin pasivo. Con k_h = 0.50 y tan φ_f = 0.625, cada kN de zapata o relleno que se añade
aporta 0.625 de fricción y 0.50 de inercia: por eso B crece hasta 2·H sin cerrar. Es física
conocida, y es la razón de que 11.6.5.2.2 exista.

## 6. Recomendación al dueño, por solidez normativa

**A. Corrección (el programa se aparta de la fuente).**

1. **Nivel de agua en la condición sísmica.** Usar el freático medio del punto y no el relleno
   lleno de `sin_drenaje`. Apoyo: C11.6.5.3, pág. 11-31, «should». La estática sigue con 11.6.6.
   Efecto: la titular pasa a fallar sólo E3 por 4 a 6 % y la portante de salida. Es la única
   pieza que llamaría corrección; por ser comentario, conviene dejarla como criterio con valor de
   archivo `nivel_medio` y la cita, no como cambio silencioso.

**B. Elecciones [A] legítimas y más razonables que el valor de archivo.**

2. **`drenaje_trasdos` = `drenado`.** 11.6.6 manda drenar («shall be drained») y sólo admite la
   hidrostática plena «if drainage cannot be provided». Un cabezal con filtro y lloraderos es el
   detalle normal. `sin_drenaje` como valor de archivo es la excepción de la norma, no la regla.
3. **`factores_inclinacion_carga_portante`.** Mantener `aplicar` es defendible y yo lo dejaría: el
   empotramiento es pequeño y puede socavarse. `omitir` está permitido por el comentario y ahorra
   zapata, pero no destraba nada por sí solo.
4. **Datos de fundación reales.** φ_f = 32° es de prueba. Cada grado mueve el deslizamiento un 4 %,
   que es el margen por el que falla el caso drenado.

**C. Decisión del Propietario (la fuente lo dice con esas palabras).**

5. **Aceptar 1 a 2 in de desplazamiento y usar k_h = 0.5·k_h0** (11.6.5.2.2, pág. 11-28; Manual de
   Puentes 2.8.1.1.14.2.2, pág. 255). Con el punto 2, A-01 cierra con B/H ≈ 1.0. Condiciones que
   hay que poder afirmar: muro libre de moverse (aleros con junta, conducto que tolere el
   movimiento en la unión) y aceptación escrita. Advertencia: si el EMS da Clase E, 0.25
   corresponde a unos 3.7 in, no a 1 a 2.
6. **k_h por desplazamiento con Newmark simplificado** (A11.5). Sólo si el Propietario quiere fijar
   un desplazamiento distinto. Requiere S1 como dato [S] nuevo, la clase de sitio y resolver la
   errata aparente de la ec. A11.5.2-3 contra NCHRP 611. Kavazanjian (A11.5.1) es la vía limpia:
   1 in da k_h = 0.31 y A-01 cierra con B/H 1.0 y 1.2.

**D. Lo que no recomiendo.**

- Invocar la exención de 11.5.4.2: no se cumple (A_s > 0.4 g y Zona 4).
- Extender al cabezal la exención de estructuras enterradas: ninguna de las tres fuentes lo dice.
- Seguir agrandando la zapata con k_h = 0.50: no converge y compra milímetros.
- El dentellón: ya descartado en `dentellon_norma.md`, y este informe no cambia esa conclusión.

**Defectos a reportar contra la documentación.** La hoja de ruta (§9.2, «no asumirlo en un cabezal
empotrado») y la ficha de `factor_muro_eleccion` presentan «sin reducción» como el lado seguro sin
decir que implica desplazamiento nulo y que, con PGA 0.50 g, ningún cabezal del juego lo cumple.
Quien lea sólo la hoja diseñará con una exigencia que el propio programa no puede cerrar.

## 7. Límites de esta revisión

- S1 ≈ 0.47 g y la posición de La Unión en los mapas son lecturas mías sobre la imagen del PDF, sin
  coordenada registrada. No son verificación de un dato [S].
- La forma 1 − k_y/k_h0 de la ec. A11.5.2-3 no está verificada contra fuente primaria.
- No evalué A11.5.3 (Bray), la estabilidad global (E4, E5) ni la licuefacción, que 11.5.4.2 pone
  como condición previa y que en el Bajo Piura es la pregunta que queda abierta.
- No revisé el armado bajo el régimen `cedente`, que la reducción de k_h obliga a declarar junto.
- Sólo medí A-01. Los otros puntos del juego no se corrieron por separado.
