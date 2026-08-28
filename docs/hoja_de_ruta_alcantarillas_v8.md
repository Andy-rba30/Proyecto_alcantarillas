# Hoja de ruta — Diseño de alcantarillas y cabezales · v7
**Vía de evitamiento, distrito de La Unión (Piura) — nivel de perfil**
*Cierres normativos integrados. Pendientes segregados por naturaleza.*

---

## Estado de esta versión

| Versión | Estado |
|---|---|
| v1–v2 | Ruta normativizada con numerales por verificar |
| v3 | Numerales verificados. Vacíos normativos identificados |
| v4 | Parche: PGA + constantes HDS-5 |
| v5 | Corrección de la clase de sitio. Control de salida incorporado |
| v6 | Gobierno centralizado de criterios. Cadena sísmica desagregada |
| **v7** | **Siete cierres integrados. Catálogo de diámetros normalizado. Tablero de pendientes segregado en tres categorías.** |

### Cambios respecto de la v6

| v6 decía | v7 corrige | Origen |
|---|---|---|
| "La Tabla A.1 organiza sus entradas **por geometría, no por material**" | **Sobreafirmación mía.** La Tabla A.1 organiza por **carta de material/forma** y, dentro de cada carta, por configuración de borde. Ver §4.2.1 | Autocorrección |
| Excepción de periodo corto: verificación pendiente | **Retirada — la regla no existe.** Verificado contra AASHTO LRFD 9.ª ed. (2020), Art. 3.10.3.1 y C3.10.3.1: la Clase F exige estudio de respuesta de sitio, sin dispensa. Pasa a adopción declarada `[A]` — ver §0.5 | Corrección posterior a la v7 |
| F_pga: valores por confirmar | **Confirmados** en Tabla 2.4.3.11.2.1.2-1: C=1.0, D=1.0, E=0.9 para PGA ≥ 0.50 | Cierre 3 |
| Catálogo comercial de diámetros bloquea M2, M7, M8 | **Desbloqueado.** Progresión normalizada 0.90 m + 0.15 m, con topes por norma de producto. Sin catálogo de proveedor | Cierre 7 |
| n de HDPE: vacío sin valor | **Rango declarado** (0.010–0.013) por analogía. **No un valor puntual** — ver §4.1.1 | Cierre 7, corregido |
| Lista única de 7 "verificaciones pendientes" | **Tres tableros separados** por naturaleza del pendiente, con dos ítems que faltaban | Reestructuración |

---

## Convención de etiquetas

| Etiqueta | Significado |
|---|---|
| **[N]** | Exigencia normativa peruana vigente, con numeral verificado |
| **[N→]** | Valor normativo aplicado **por analogía**. Requiere declaración expresa |
| **[C]** | Vacío normativo cubierto con fuente técnica reconocida (FHWA, AASHTO, ASTM), declarado |
| **[A]** | Sin norma ni fuente única. Adopción declarada + análisis de sensibilidad obligatorio |

**Regla de coherencia:** la etiqueta debe corresponder al origen real del valor. Un criterio justificado invocando una disposición normativa no puede etiquetarse `[A]`. Cuando una tabla normativa aporta los valores pero la elección entre ellos es del proyectista, se desdobla: **la tabla es [N], la elección es [A]**.

---

## 0. Marco normativo

### 0.1 Jerarquía

| Ámbito | Documento | Rol |
|---|---|---|
| Hidrología, TR, tipo de obra, Manning, velocidades, borde libre, protección de salida, cunetas | **Manual de Hidrología, Hidráulica y Drenaje** (RD 20-2011-MTC/14) | [N] Norma base |
| Resguardo napa–subrasante, compactación, densidad de calicatas, terraplén sobre NF somero | **Manual de Suelos, Geología, Geotecnia y Pavimentos** (RD 10-2014-MTC/14) | [N] |
| Cargas, combinaciones, HL-93, sobrecarga en trasdós, PGA, zapatas en talud, diseño del concreto | **Manual de Puentes** (RD 041-2016-MTC/14) | [N] |
| Clase de sitio F (exige estudio de respuesta de sitio, §0.5); Sección 12 (estructuras enterradas) | **AASHTO LRFD Bridge Design Specifications** | Norma matriz. `[C]` donde el Manual no tipifica; la clase de sitio **no** es uno de esos casos: es `[A]` — ver §0.5 |
| Capacidad portante, FS de muros, licuefacción, c y φ, cimentación en talud | **RNE E.050** (RM 406-2018-VIVIENDA) | [N] |
| Perfil de suelo licuable (señal técnica) | **RNE E.030** (RM 183-2026-VIVIENDA) | [N] con reserva de ámbito (0.4) |
| Durabilidad del concreto y recubrimientos | **RNE E.060**, Cap. 4 y Art. 7.7 | [N] por excepción declarada (0.2) |
| Materiales, camas, rellenos, ejecución, partidas | **EG-2013, Sección 500** (RD 22-2013-MTC/14) | [N] |
| Diámetros normalizados y clases de tubería | **ASTM C76 / AASHTO M170** (concreto), **AASHTO M36 / ASTM A760** (TMC), **AASHTO M294 / ASTM F2306** (HDPE) | [C] normas de producto |
| Control de entrada y salida, HW/D | **HDS-5 (FHWA), 3ª edición, abril 2012** | [C] |
| Velocidades máximas en materiales flexibles | **PPI / FHWA** | [C] — valores por extraer |

### 0.2 Regla de consistencia carga–resistencia — RESUELTA

El Manual de Puentes establece que las combinaciones se rigen por **AASHTO LRFD Sección 3.4.1** y el diseño del concreto por **AASHTO LRFD Sección 5** (num. 2.4.5.3 y Sección 2.9, págs. 140-143 y 337).

**Vía 1 adoptada: AASHTO LRFD de extremo a extremo.** E.060 no gobierna el diseño estructural.

**Excepción declarada — durabilidad.** E.060 Cap. 4 y Art. 7.7 sí aplican, por ser especificación de **materiales**, no de la relación carga–resistencia, y por estar calibrados con cementos peruanos (Tipo V, nomenclatura NTP). Regla de conflicto: rige el recubrimiento **mayor** entre AASHTO y E.060. Única mezcla admitida; se escribe expresamente en la memoria.

### 0.3 Vacíos normativos y su estado

| Vacío | Estado en v7 |
|---|---|
| Control de entrada / salida | El Manual MTC no lo desarrolla. HDS-5 3ª ed. (2012) aplicado **por encima** del mínimo normativo `[C]`. **Aporte metodológico** |
| Relación HW/D | No existe en el Manual MTC. **`[A]` 1.2–1.5** (corregido desde `[C]`: el rango 1.0–1.5 **no lo prescribe el HDS-5**, lo describe — ver V4b en Fase 5. Ref. `NOR-HDS-02`, `MAT-D2`). El control real del embalse es V5 |
| Velocidad máxima en TMC y HDPE | Tabla Nº 10 no los cubre. Fuentes identificadas (PPI, FHWA); **valores numéricos aún por extraer** |
| n de Manning para HDPE | Tabla Nº 09 no lo lista. **Rango 0.010–0.013 aplicado por analogía al concreto** `[N→]` (corregido desde `[A]`: lo exige la **regla de coherencia** de §0.1 — un valor justificado invocando una fila de una tabla normativa no puede ser `[A]` —, y es el mismo caso que `resguardo_HW_subrasante` y `h_relleno_min_concreto_tmc`. Ref. SIS-D-11) |
| Flotación de conductos | El Manual de Puentes define subpresión (2.4.3.8.2, pág. 113) pero no incorpora AASHTO LRFD Sec. 12. Definición `[N]`; la verificación se plantea como **equilibrio de factores de carga LRFD** (§Fase 5, V7), con los γ de las Tablas 3.4.1-1/-2 vía `factores_carga_aashto` `[A]`. **Ya no un FS global:** un FS es lenguaje de tensión admisible y §0.2 adopta LRFD de extremo a extremo |
| Clase de sitio F | **Cerrado en contra de lo que decía la v7.** AASHTO no concede dispensa alguna: exige estudio de respuesta de sitio específico. Usar factores tabulados es adopción `[A]` del proyectista — §0.5 |

### 0.4 Marco sísmico — CERRADO

**Aceleración en roca.** Mapa **"Isoaceleraciones Espectrales Suelo Tipo B, AASHTO 2014 (Roca), periodo estructural 0.0 seg (PGA)"**, Manual de Puentes, Apéndice A3, Tr = 1000 años. Lectura para La Unión (Piura): **PGA = 0.50 g** `[N]`.

Se descartan expresamente los mapas de S_s (T = 0.2 s) y S₁ (T = 1.0 s), que corresponden a aceleraciones espectrales y no a la aceleración pico del terreno.

No se usa el Z = 0.45 de E.030 para las fuerzas sobre el muro; su periodo de retorno de referencia (475 años) difiere del adoptado.

> **Único resto pendiente:** registrar en la memoria las **coordenadas o la curva de isoaceleración** sobre la que se hizo la lectura. Las curvas varían dentro de un mismo departamento y el revisor puede querer reproducir la lectura. Es un dato de trazabilidad, no un cambio de valor.

**Factor de sitio.** Tabla 2.4.3.11.2.1.2-1 del Manual de Puentes, para PGA ≥ 0.50:

| Clase de sitio | F_pga | A_s resultante |
|---|---|---|
| C | 1.0 | 0.50 g |
| D | 1.0 | 0.50 g |
| E | 0.9 | 0.45 g |

Los valores de tabla son **[N]**. La **elección** de F_pga = 1.0 sin conocer la clase de sitio definitiva es **[A]**: conservadora o exacta frente a las tres clases plausibles, con incertidumbre acotada al 10 %.

**Alcance de "conservador":** lo es dentro del marco tabulado. El análisis de respuesta específica de sitio —el que la Clase F **exige**, sin dispensa posible (§0.5)— podría arrojar valores mayores. Declararlo.

### 0.5 Clase de sitio F — ADOPCIÓN DECLARADA, NO DISPENSA NORMATIVA

El sitio clasifica como **Clase de Sitio F** por susceptibilidad a licuefacción: arenas saturadas con NF a 1.4 m en la llanura del Bajo Piura. Clasificarlo como D o E mientras la Fase 0-bis advierte riesgo de licuefacción sería una contradicción interna del expediente. Eso no ha cambiado.

**Lo que sí cambia — corrección de la versión anterior de este apartado.** Las versiones previas afirmaban que AASHTO LRFD, Art. 3.10.3.1, autoriza una dispensa por periodo fundamental corto (T ≤ 0.5 s) que permitiría clasificar el sitio como si los suelos no licuaran y usar los factores de sitio tabulados. **Esa regla no existe.** Se verificó contra **AASHTO LRFD Bridge Design Specifications, 9.ª edición (2020)**: no está en el Art. 3.10.3.1, no está en su comentario C3.10.3.1, y no está en ninguna tabla ni nota a tabla de clases de sitio. **AASHTO exige, de forma incondicional, un estudio de respuesta de sitio específico para la Clase F.**

Esto no fue un vacío rellenado en silencio: fue una **autorización normativa atribuida a una norma que no la concede**, y es el error más grave que ha tenido este expediente. Un vacío se ve; una cita falsa se cree. Queda anotado aquí, y no borrado, para que nadie vuelva a cerrarlo por el mismo camino.

**Consecuencia sobre la etiqueta: de `[C]` a `[A]`.** Un `[C]` es un vacío normativo **cubierto** con fuente técnica reconocida. Aquí no hay fuente que lo cubra: la que se citaba no dice lo que se le hacía decir. Por tanto, mientras no exista el estudio de respuesta de sitio, **seguir el cálculo con los factores de sitio tabulados es una adopción declarada del proyectista, no un permiso de la norma.** Etiqueta **[A]**, declarada en `criterios_adoptados.py` como `clase_sitio = "F_con_factores_tabulados_por_adopcion"`. La memoria de cálculo debe decirlo con esas palabras y **no citar AASHTO como respaldo de la adopción**.

**Alcance de la adopción, ahora sin coartada.** Los factores tabulados permiten **dimensionar** el elemento estructural. **No constituyen una evaluación del riesgo de licuefacción**, que permanece como el condicionante técnico no resuelto del proyecto (Fase 0-bis), y los efectos de la licuefacción —asentamiento, desplazamiento lateral, pérdida de capacidad portante— quedan fuera del alcance del script y remitidos al estudio geotécnico del expediente. Un análisis de respuesta específica de sitio **puede arrojar valores mayores** que los tabulados: la adopción **no es conservadora por construcción**, y esa es exactamente la razón de que sea `[A]` y no `[N→]`.

**Lo que cierra este apartado.** El estudio de respuesta de sitio específico que AASHTO exige para la Clase F, programado en la campaña geotécnica junto con la caracterización de los 30 m superiores (Vs30 o N̄) que define la clase.

### 0.6 Demanda sísmica para la evaluación de licuefacción — CERRADO

**Adoptado: Tr = 1000 años** `[A]`, es decir a_max derivado del mismo PGA = 0.50 g usado para la estructura. Se descarta el sismo de 475 años de E.030.

**Fundamento:** al tratarse de infraestructura vial regida por el Manual de Puentes, se exige al suelo la misma demanda sísmica que a la estructura de concreto que soporta. Un terreno evaluado a 475 años bajo una estructura diseñada a 1000 años es una incoherencia de niveles de seguridad dentro del mismo expediente.

> **Parámetro adicional que esta decisión genera.** El procedimiento simplificado de evaluación de licuefacción no se alimenta solo de a_max: requiere también la **magnitud del sismo (M_w)** para el factor de escala de magnitud (MSF). El PGA del mapa no la entrega. Debe adoptarse y declararse una M_w —por desagregación del peligro sísmico o por adopción justificada del sismo de diseño de la zona de subducción del norte peruano— antes de que la evaluación sea ejecutable. **Nuevo criterio `[A]` en el tablero.**

### 0.7 Gobierno de criterios adoptados

**Regla arquitectónica:** todo parámetro que no sea una exigencia normativa verificada se declara **una sola vez**, en `criterios_adoptados.py`, y se propaga desde allí.

| Contenedor | Qué contiene |
|---|---|
| **Anexo B** | Solo constantes **[N]** con numeral verificado |
| **`criterios_adoptados.py`** | Todo **[N→]**, **[C]** y **[A]**, con valor, etiqueta, justificación, fuente, ensayo que lo sustituye, rango de sensibilidad y verificación pendiente |

La inconsistencia Clase D/F que motivó la v5 no fue un error de cálculo: fue el mismo parámetro definido dos veces en dos lugares. Un único punto de definición hace esa contradicción estructuralmente imposible.

**Comportamiento exigido:** un criterio con valor `None` detiene el script con excepción, nunca sustituye por defecto. Cada invocación se registra para que M11 imprima solo los criterios usados. Los pendientes se imprimen en bloque aparte.

---

## Fase 0-bis — Licuefacción: el condicionante mayor del proyecto

**E.030 (RM 183-2026-VIVIENDA), Art. 14.6, Tabla Nº 2 — Perfil S5 "Suelos excepcionales":**

> Suelos potencialmente licuables. Estos casos no están cubiertos en la clasificación de la Tabla Nº 2. **Se prohíbe las construcciones apoyadas sobre estos perfiles, salvo que se efectúe un estudio específico para el sitio, en el cual se debe considerar los mejoramientos en el estrato del perfil.**

**E.050, Art. 38 — condiciones concurrentes:** suelo arenoso/limo arenoso no plástico o grava en esa matriz; sumergido bajo napa freática; historia sísmica que haga sospechar la posibilidad.

**E.050, Art. 38 — ensayo exigido:** **SPT (NTP 339.133), perforaciones ≥ 15 m, ensayos cada 1 m.** DPSH, CPT y Vs como preliminares o complementarios, con calibración previa contra SPT (salvo CPT y Vs, que pueden calcular directamente el potencial complementando al SPT).

**Demanda sísmica de evaluación:** a_max de Tr = 1000 años (§0.6), más M_w por declarar.

### Lo que significa

1. **El elemento en riesgo no es el cabezal: es el terraplén de 5 km.** El modo de falla es asentamiento y desplazamiento lateral del cuerpo del terraplén, con las alcantarillas como puntos de concentración de daño.
2. Sin SPT no se clasifica el perfil ni se descarta la condición S5 / Clase F.
3. La conducta correcta a nivel de perfil es declararlo como condicionante principal, especificar el ensayo con su alcance normativo y remitir la solución al expediente.
4. Si se confirma, la solución es mejoramiento del terreno de fundación bajo el terraplén, con impacto en presupuesto y plazo. Va en las conclusiones.

**Reserva de ámbito.** E.030 es norma de edificaciones y una vía no lo es: la prohibición literal del S5 no es directamente exigible al bypass, pero la señal técnica sí. Declararlo en ambos sentidos.

---

## Fase 1 — Datos de entrada

### 1.1 Por punto crítico (fila del CSV)

| Dato | Unidad | Origen | Ancla |
|---|---|---|---|
| Progresiva del cruce | km | Red de cauces ∩ trazo (QGIS) | — |
| Caudal de diseño Q | m³/s | Tc.py + IDF con TR de Fase 2 | [N] |
| Área de cuenca | ha | r.watershed — **solo clasificador** | [N] |
| Pendiente del cauce S | m/m | DEM | — |
| Cota de terreno natural | msnm | DEM / topografía | — |
| Cota de rasante | msnm | Perfil longitudinal, tras 7.A | [N] DG-2018 |
| Cota de subrasante | msnm | Rasante − espesor del paquete estructural | [N] |
| **CBR de diseño de la subrasante** | % | Calicatas | [N] — define el resguardo de V4 |
| Ángulo de esviaje | ° | QGIS | [N] |
| Ancho de plataforma | m | Sección típica | [N] DG-2018 |
| Cota de fondo del receptor | msnm | Nivelación del dren/canal | — |
| Q de diseño del receptor | m³/s | ANA / Junta de Usuarios | [N] Ley 29338 |
| Cota TW | msnm | **Calculada** (1.3) | [C] |
| Clasificación SUCS de fundación | — | Calicata más cercana | [N] E.050 |
| Familia | A/B/C | Fase 2 | [N] |

### 1.2 Encabezado del CSV

```
id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,
cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,
cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion
```

### 1.3 TW: se calcula, no se mide

1. Obtener Q de diseño del receptor (ANA / Junta de Usuarios) **[N]**
2. Manning en la sección del receptor con ese Q y su pendiente → tirante normal → cota de agua **[N]**
3. Sin caudal documentado: **dos escenarios acotados** (salida libre / receptor a sección llena), cumplir en ambos **[A]**

### 1.4 Densidad de investigación geotécnica

**Manual de Suelos, num. 4.2, Cuadro 4.1** (págs. 28-29). Nivel **Perfil**: número de calicatas del Cuadro 4.1 **espaciadas cada 4.0 km**.

| Clase | IMDA (veh/día) | Calicatas | Profundidad |
|---|---|---|---|
| Autopistas | > 6000 | 4 (6 si 4 carriles/sentido) × km × sentido | 1.50 m |
| Duales / multicarril | 4001–6000 | 4 (o 6) × km × sentido | 1.50 m |
| 1ª clase | 2001–4000 | 4 × km | 1.50 m |
| 2ª clase | 401–2000 | 3 × km | 1.50 m |
| 3ª clase | 201–400 | 2 × km | 1.50 m |
| Bajo volumen | ≤ 200 | 1 × km | 1.50 m |

La regla es **[N]** y está cerrada. Lo que sigue abierto es el **dato de entrada**: el IMDA de diseño, que proviene del estudio de demanda. Con 5 km y estaciones cada 4.0 km hay 2 estaciones; si la vía resulta de 2ª clase, el requisito es 6 calicatas. Si tienes 5, **decláralo como limitación**.

### 1.5 Aclaración de datos que se confunden

| Dato | **No** es | **Sí** es |
|---|---|---|
| γ, φ del trasdós | Suelo bajo la zapata | Material de cantera detrás del cabezal. Es el que **empuja** |
| c o φ de fundación | Material de cantera | Suelo natural bajo la zapata. Es el que **resiste** |
| γ del relleno | γd del Proctor | Peso unitario **húmedo en servicio**: γ = γd(1+w) |
| c y φ juntos | Ambos a la vez | Solo uno. E.050 Art. 20.2: φ=0 en cohesivos; 20.3: c=0 en friccionantes |
| Pendiente S | La de la alcantarilla | La del **cauce natural** |
| Cota de rasante | Cota de subrasante | Superficie de rodadura. El chequeo de HW va contra la **subrasante** |
| Cota TW | Nivel dentro de la alcantarilla | Nivel en el receptor **durante la avenida** |
| Diámetro mínimo | Diámetro de diseño | Piso normativo (0.90 m). El de diseño sale de la iteración |
| NF 1.4 m | Bajo la rasante | Bajo el **terreno natural**, antes del terraplén |
| PGA 0.50 g | Z de E.030, ni S_s | Aceleración pico en roca Clase B, Tr = 1000 años |
| **A_s** | **k_h** | Aceleración ajustada por sitio. k_h se obtiene aplicándole el factor de muro |
| a_max para licuefacción | Suficiente por sí solo | Requiere además **M_w** para el factor de escala de magnitud |

---

## Fase 1-bis — Hidrología: población mixta por FEN

La serie de precipitación máxima anual en Piura es de **población mixta**: los años con El Niño extraordinario (1983, 1998, 2017) no pertenecen estadísticamente a la misma población que los años neutros.

- Verificar si la serie SENAMHI **contiene** esos años.
  - **Si los contiene:** el ajuste K-S puede estar dominado por dos o tres outliers. Reportar el ajuste con y sin ellos, adoptar el más conservador, declarar el criterio.
  - **Si no los contiene:** el Q de diseño está subestimado de forma grave. Declararlo como limitación central.
- Registrar longitud de registro, estación y años faltantes.
- Va **antes** de la Fase 4. **Sigue abierto** — ver Tablero 3.

---

## Fase 2 — Clasificación y periodo de retorno

### 2.1 Umbral de luz — binario [N]

**Manual MTC, num. 4.1.1.3.1 y 4.1.1.5.1** (págs. 70 y 88):

| Luz | Denominación |
|---|---|
| **< 6.0 m** | Alcantarilla → Manual de Hidrología |
| **≥ 6.0 m** | Puente → Manual de Puentes |

**No existe la categoría "pontón"** en la normativa MTC. El Manual de Puentes remite al Glosario de Términos (pág. 44).

- Canal de **12 m** → **puente**, fuera del alcance del script
- Canal de **2.75 m** y drenes de tierra → **alcantarillas**

### 2.2 Periodo de retorno — calculado [N]

**Manual MTC, num. 3.6, Tabla Nº 02** (pág. 25):

$$R = 1-\left(1-\frac{1}{T}\right)^{n} \quad\Longrightarrow\quad T = \frac{1}{1-(1-R)^{1/n}}$$

| Categoría | R | n | **TR de diseño** |
|---|---|---|---|
| Quebradas importantes / badenes | 30 % | 25 años | **71 años** |
| Quebradas menores / descarga de cunetas | 35 % | 15 años | **35 años** |

**No existe TR mínimo obligatorio independiente.** No adoptar 50 años "por costumbre".

### 2.3 Familias

**A — Alcantarillas de paso.** Q hidrológico propio. TR 71 o 35 años. Aceptación: V1 + V2 + V4 + V5.

**B — Alcantarillas de alivio.** Q del drenaje longitudinal. TR 35 años. Espaciamiento por Fase 10. Terraplén <1.5 m sin bordillo (geomalla); >1.5 m con bordillo y bajantes a ambos lados, a un solo lado en curvas peraltadas.

**C — Cruces de canales y drenes.** Q = caudal de diseño del canal (ANA / Junta). **No puede alterar la rasante hidráulica ni el borde libre del canal.** Requiere autorización de obras en fuente natural / faja marginal. Marco o multicelda. **Bloqueada por falta del dato de ANA** — ver Tablero 3.

---

## Fase 3 — Tipo, material y durabilidad

### 3.1 Reglas duras [N]

- Luz ≥ 6.0 m → fuera de alcance
- **Diámetro mínimo 0.90 m (36")** — num. 4.1.1.3.4 a), pág. 72
- Excepción de selva alta (TMC Ø48", cauces en V, pendientes 5–60 %) — num. 4.1.1.3.7 a), pág. 78: **no aplica en costa.** Programar la rama y declararla inactiva
- Suelo de fundación deficiente → orientar a marco de concreto
- Con palizada: sección única mayor, no múltiple

### 3.2 Catálogo de diámetros normalizado — **nuevo en v7** [C]

**Decisión: no se emplean catálogos de proveedores ni marcas.** El diseño opera con una progresión normalizada que garantiza neutralidad comercial, exigible en proyectos públicos.

**Progresión:** desde **0.90 m** (mínimo normativo MTC) con incrementos de **0.15 m**.

$$D \in \{0.90,\ 1.05,\ 1.20,\ 1.35,\ 1.50,\ 1.65,\ 1.80,\ ...\}$$

**Por qué funciona.** Las normas de producto avanzan en pasos de 6 pulgadas (0.1524 m) por encima de los 24–36", y AASHTO M294 lo hace en pasos de 150 mm por encima de 600 mm. La progresión de 0.15 m reproduce esas series con error despreciable.

**Nota de conservadurismo:** usar 0.90 m redondo en lugar del equivalente exacto de 36" (0.9144 m) subestima el área en ~3 %. El error va del lado de la seguridad y debe declararse.

**Topes superiores por norma de producto — obligatorios en el script:**

| Material | Norma de producto | Diámetro máximo aproximado |
|---|---|---|
| Concreto reforzado | ASTM C76 / AASHTO M170 | ~2.70 m |
| TMC | AASHTO M36 / ASTM A760 | ~2.10 m |
| **HDPE** | AASHTO M294 | **~1.50 m** |

> **Requisito de programación.** Sin tope superior, la iteración puede converger a un "diámetro" que no existe como producto. El caso especialmente restrictivo es el **HDPE**, que en la práctica no supera 1.50 m: si un punto crítico exige más, el HDPE queda descartado por catálogo antes que por hidráulica. El módulo debe devolver *"material descartado por diámetro requerido"*, no un número imposible.
>
> Los topes de la tabla deben confirmarse contra el texto de cada norma de producto antes de citarlos. Ver Tablero 1.

### 3.3 Durabilidad — E.060 Cap. 4 (excepción de 0.2)

**Tabla 4.4 — sulfatos** (Art. 4.3, pág. 38):

| Exposición | SO₄ suelo (% peso) | SO₄ agua (ppm) | Cemento | a/c máx | f'c mín |
|---|---|---|---|---|---|
| Insignificante | 0.00 – 0.10 | 0 – 150 | — | — | — |
| Moderada | 0.10 – 0.20 | 150 – 1500 | II, IP(MS), IS(MS), P(MS), I(PM)(MS), I(SM)(MS) | 0.50 | 28 MPa |
| Severa | 0.20 – 2.00 | 1500 – 10000 | **V** | 0.45 | 31 MPa |
| Muy severa | > 2.00 | > 10000 | **V + puzolana** | 0.45 | 31 MPa |

**Cloruros externos** (Art. 4.2 y 4.4, págs. 37 y 39): a/c ≤ **0.40**, f'c ≥ **35 MPa**.

**Concurrencia [N]:** con sulfatos y cloruros simultáneos rige la **a/c más baja y el f'c más alto**.

**Cloruros en concreto endurecido — Tabla 4.5** (% peso del cemento): preesforzado 0.06; armado expuesto a cloruros 0.15; armado seco o protegido 1.00; otras construcciones 0.30.

**Recubrimientos** (Art. 7.7.1, pág. 54):

| Condición | Recubrimiento |
|---|---|
| Vaciado contra el suelo, expuesto permanentemente a él | **70 mm** |
| Expuesto a suelo o intemperie, barras ≥ 3/4" | **50 mm** |
| Expuesto a suelo o intemperie, barras ≤ 5/8" y mallas | **40 mm** |
| Ambientes corrosivos (Art. 7.7.5.1) | Aumentar adecuadamente |

Con NF a 1.4 m y suelos salinos, el Art. 7.7.5.1 es directamente invocable.

### 3.4 Matriz de decisión de material

| Material | Vacíos normativos | Tope de diámetro | Durabilidad |
|---|---|---|---|
| **Concreto reforzado** | **Ninguno.** n y velocidad máxima en Tablas Nº 09 y Nº 10; carta propia en HDS-5 | ~2.70 m | Tabla 4.4 fija cemento, a/c y f'c según ensayo |
| **TMC galvanizada** | **Uno:** velocidad máxima (fuente PPI/FHWA, valor por extraer) | ~2.10 m | Requiere pH y resistividad; en suelos salinos la galvanización cae fuertemente |
| **HDPE** | **Tres:** velocidad máxima, n de Manning y carta propia en HDS-5 | **~1.50 m** | Inmune a agresividad química. Condicionantes: rigidez, flotación, relleno mínimo 0.30 m |

**Argumento de defensibilidad:** el concreto reforzado es el único material cuyos parámetros hidráulicos están íntegramente dentro del marco normativo peruano, y el que admite mayores diámetros. Esto no descarta al HDPE —puede ganar por durabilidad y costo en los puntos de menor caudal—, pero el costo de defensibilidad debe entrar explícito en la matriz.

---

## Fase 4 — Dimensionamiento hidráulico

### 4.1 Manning — lo que exige la norma [N]

Sección circular parcialmente llena:

- A = (D²/8)(θ − sen θ)  ·  P = D·θ/2  ·  R = A/P
- Q = (1/n)·A·R^(2/3)·S^(1/2)

Resolver con **bisección o Brent sobre θ ∈ (0, 2π)**.

**Tabla Nº 09 — Manning** (num. 4.1.1.3.6, pág. 75):

| Material | n mín | n máx | Ancla |
|---|---|---|---|
| Metal corrugado (dren de lluvias) | 0.021 | 0.030 | [N] |
| Concreto, tubo recto | 0.010 | 0.013 | [N] |
| Madera (duelas) | 0.010 | 0.014 | [N] |
| **HDPE (interior liso)** | **0.010** | **0.013** | **[N→]** por analogía al concreto (ver §0.3 y la regla de coherencia de §0.1) |

**Regla [N]:** **n máximo** para capacidad y tirante (conservador del lado de la inundación); **n mínimo** para velocidad máxima y socavación (conservador del lado de la erosión).

#### 4.1.1 Por qué el n de HDPE es un rango y no 0.012 — **corrección**

Adoptar un **valor puntual** de n = 0.012 para HDPE rompe la regla de los dos valores: con un solo número, la verificación de capacidad y la de velocidad usan la misma rugosidad y **una de las dos deja de ser conservadora**. Concretamente, con n = 0.012 la velocidad calculada resulta menor que con n = 0.010, lo que subestima el riesgo de erosión y el d₅₀ de la protección de salida.

Si la analogía al concreto es el fundamento, hay que tomar **el rango completo del concreto** (0.010–0.013), no su valor medio. Así el HDPE se somete a la misma arquitectura de doble n que el resto de materiales.

**Condición de validez:** la analogía solo aplica a HDPE de **interior liso**. El HDPE de interior corrugado tiene n del orden de 0.018–0.025 y la analogía sería gruesamente insegura. Especificar el tipo de producto en la memoria.

### 4.2 Control de entrada — HDS-5 [C]

**Fuente a citar:** FHWA, *Hydraulic Design of Highway Culverts*, 3ª edición, abril 2012, Apéndice A, Tabla A.1, pág. A.8.

**Caudal adimensional:**

$$q^* = \frac{K_u\,Q}{A\,D^{0.5}}, \qquad K_u = 1.811 \ \text{(SI)}$$

**Régimen no sumergido (q\* ≤ 3.5), Forma 1:**

$$\frac{HW_i}{D} = \frac{H_c}{D} + K\,(q^*)^{M} + K_s\,S$$

**Régimen sumergido (q\* ≥ 4.0):**

$$\frac{HW_i}{D} = c\,(q^*)^{2} + Y + K_s\,S$$

**Transición (3.5 < q\* < 4.0):** interpolar linealmente **entre el valor de la forma no sumergida en q\* = 3.5 y el de la sumergida en q\* = 4.0** (no entre las dos formas evaluadas en el q\* real: dentro de la ventana ninguna de las dos vale).

> **La recta NO es el método del HDS-5, y esta línea la presentaba como si lo fuera** (`MAT-O10`). El HDS-5 empalma las dos ramas con una **curva tangente** ajustada sobre sus datos de laboratorio, **de la que no publica ecuación cerrada**. Quien prescribe la recta es esta hoja de ruta, no la fuente. Es una **simplificación adoptada** `[C]`, declarada en `criterios_adoptados` como `metodo_transicion_hds5` e invocada solo al entrar en la rama, de modo que la memoria la declara únicamente si algún punto del corredor cae de verdad en la transición. El error está acotado —la recta coincide con cada rama en su borde de validez— y acotado no es lo mismo que normativo.

**K_s** = −0.5 para embocaduras no en inglete; **+0.7** para inglete. *(No figura en la Tabla A.1: proviene de la formulación de las ecuaciones. No omitirlo.)*

> **El término K_s·S no tiene tope, y una carga negativa no existe** (`MAT-D10`). Con K_s = −0.5, una pendiente grande y un caudal chico llevan las dos formas a devolver **HW_i/D negativo** —una lámina de agua por debajo del fondo del conducto—. El umbral del signo, para la Forma 1, es `S > 2·(H_c/D + K·(q*)^M)`: con D = 0.90 m, Q = 0.05 m³/s y la carta de concreto vale `S > 0.3770624`, y hasta la corrección el diseño se **aceptaba entero** con HW = −0.010 m, o sea con V4 y el tamizado de 7.A evaluados 0.18 m del lado no conservador.
>
> `M4.control_entrada()` **rechaza** ese resultado con `DisenoNoFactibleError`. Es un rechazo, no un piso: adoptar una carga en su lugar —la lectura física sería HW ≈ H_c— exige un valor que **ni esta hoja ni el HDS-5 fijan**, y ponerlo aquí sería rellenar un vacío en silencio. Y no es `DatoInvalidoError`: una S de 0.40 m/m es del tipo correcto, cae dentro de `dominios.S_CAUCE_MAX` y no contradice a nadie —no hay dato que el revisor tenga que corregir—; lo que no cierra es el **método** sobre esa combinación de Q, D y S.
>
> **Cuánto cierra este rechazo, con números.** Cierra el signo y poco más. Con `S = 0.37706` el diseño se sigue aceptando con HW = +10⁻⁶ m, y V4 y 7.A quedan evaluados **0.1695 m** del lado no conservador —el 94 % del error—: de los 0.1798 m que el hallazgo denuncia, el rechazo retira 0.0103, el **5.7 %**. En el corredor de este expediente (S_cauce = 0.006–0.008) no se dispara nunca: en D = 0.90 hace falta `S > 0.27` y además Q = 0.025 m³/s. Acotar el rango de validez **entero** de la corrección exige una pendiente máxima que ni esta hoja ni el manual escriben, y ponerla sería inventarla: **queda abierto**.

| Configuración | K | M | c | Y | K_s |
|---|---|---|---|---|---|
| Circular Concrete — Square edge w/headwall | 0.0098 | 2.00 | 0.0398 | 0.67 | −0.5 |
| Circular CMP — con cabezal | 0.0078 | 2.00 | 0.0379 | 0.69 | −0.5 |
| Circular CMP — mitered to slope | 0.0210 | 1.33 | 0.0463 | 0.75 | +0.7 |

**Configuración adoptada por diseño:** tubo a ras del muro (*square edge w/headwall*), coherente con el detalle de cabezal de la Fase 9.

#### 4.2.1 Corrección a la v6 sobre la organización de la Tabla A.1

En la v6 escribí que la Tabla A.1 *"organiza sus entradas por geometría de embocadura, no por material"*. **Eso fue una sobreafirmación mía y conviene corregirla**, porque es citable y es falsa tal como estaba redactada.

La Tabla A.1 se organiza en **cartas por forma y material** (*Circular Concrete*, *Circular CMP*, etc.) y, **dentro de cada carta**, por configuración de borde. Prueba de ello es que la misma configuración *square edge w/headwall* tiene constantes distintas en concreto (K = 0.0098) y en metal corrugado (K = 0.0078).

**Lo que sigue siendo cierto, y es lo que sostiene la adopción para HDPE:** esas diferencias entre materiales responden al **perfil de la pared en la boca** —una pared corrugada contrae el flujo de entrada distinto a una pared lisa—, **no a la fricción del barril a lo largo del conducto**, que interviene únicamente en el control de salida.

**Justificación correcta para el HDPE:** se adopta la carta *Circular Concrete, square edge w/headwall* porque el HDPE de **interior liso** con extremo cortado a ras del muro presenta, en la boca, una pared lisa y un borde cuadrado — es decir, la misma condición de entrada que el concreto, y no la del metal corrugado. Etiqueta **[C]**.

**Requisito de programación:** la Forma 1 necesita **H_c** (H_c = y_c + V_c²/2g). El tirante crítico en sección circular no tiene solución cerrada: se resuelve

$$\frac{Q^{2}\,T}{g\,A^{3}} = 1$$

con un segundo Brent sobre θ. **M4 requiere dos solvers, no uno.**

### 4.3 Control de salida [C]

$$HW = H + h_o - S\,L$$

$$H = \left(1 + k_e + \frac{19.63\,n^{2}L}{R^{4/3}}\right)\frac{V^{2}}{2g} \qquad \text{(SI)}$$

$$h_o = \max\left(TW,\ \frac{y_c + D}{2}\right)$$

> **h_o tiene numeral, y tiene una condición de uso que esta hoja no recogía** (`NOR-HDS-05`). La fórmula está en **HDS-5 3.ª ed., num. 3.3.3 «Outlet Control», pág. impresa 3.24** (el manifiesto marcaba la fila «⚠ sin numeral»), y allí mismo viene acotada:
>
> «Approximate hydraulic gradeline ho = (dc + D)/2 **can only be used if the barrel flows full for most of its length. It should not be used if the inlet is not submerged.**» (viñeta de la lista «The manual method has the assumptions:») · «If outlet control governs and the headwater depth (referenced to the inlet invert) is **less than 1.2D**, it is possible that the barrel flows partly full though its entire length. In this case, **caution should be used** in applying the approximate method of setting the downstream elevation based on the greater of tailwater or (dc + D)/2. If the headwater depth falls below **0.75D**, the approximate method should not be used.» (párrafo de prosa que sigue a esa lista) — son **tres** condiciones, no dos.
>
> La forma con el **máximo** —que es la que implementa `M4.control_salida`— la 3.ª ed. no la numera: la escribe en prosa («the greater of tailwater or (dc + D)/2»). Impresa como igualdad está en la edición de 1985 que también vive en `normas/`: «ho = TW or (dc + D)/2 whichever is larger.»
>
> **De las tres condiciones, el proyecto EVALÚA dos y declara la tercera.** Las dos evaluables son los límites sobre HW/D, que son una comparación entre dos números que `control_salida()` ya tiene: cuando el control de salida **gobierna** un punto y su HW/D cae bajo 1.2 o bajo 0.75, la memoria **de ese punto** lo dice junto al HW (`ResultadoHidraulico.h_o_fuera_de_rango`), no como advertencia general. Un aviso que no señala el punto afectado es el «nadie se entera» que el hallazgo denuncia. Los dos números son `[N]`: los escribe la fuente (`H_O_HW_SOBRE_D_MIN`, `H_O_HW_SOBRE_D_CAUTELA`) — y el 0.75 **no es** el 0.75 del borde libre de V1: aquél es del Manual MTC sobre el *tirante*, éste del HDS-5 sobre la *carga a la entrada*.
>
> La tercera —que el barril fluya lleno en la mayor parte de su longitud— **no se evalúa**, y ahí sí: exige un perfil de la lámina de agua a lo largo del conducto que este script no calcula. El criterio `geometria_control_salida = "seccion_llena"` **presupone lo mismo** que habría que verificar, de modo que esa premisa entra dos veces por dos puertas y no se comprueba por ninguna. Queda declarada en su `verificacion_pendiente`. Lo que la cerraría es el **procedimiento de barril parcialmente lleno del Cap. III**.
>
> **Circularidad que conviene ver:** el HW con que se evalúan los dos límites lo produce la propia aproximación, de modo que un h_o sobreestimado puede hacer que el control de salida gobierne un punto donde no gobernaría. El aviso se emite igual; deshacerla exige el procedimiento completo.

> **Nota de unidades.** **19.63** es el valor SI. El **29** de la literatura FHWA es del sistema inglés. Usar 29 en métrico no falla ruidosamente: devuelve números plausibles y equivocados. **Test unitario obligatorio.**
>
> **Corregido desde 19.62** (conflicto #6 del plan de correcciones; `MAT-D12`, `MAT-X5`, `MAT-O12`, `NOR-COH-01`, `SIS-A-20`). Esta hoja escribía 19.62 en sus **cuatro** menciones y el código sostenía 19.63 desde antes, declarando la discrepancia. Gana la fuente primaria, verificada contra el PDF: **HDS-5 3.ª ed. (2012), num. 3.1.4, ec. (3.4b), pág. impresa 3.10** — «KU = 29 in English Units (19.63 in SI)» —, repetido en la ec. (DG 3.1), pág. DG3.3. **Ojo con la otra copia de `normas/`:** `fhwa_culvert_hydraulics_hds5si.pdf` es la edición de **1985** y, pese al «si» del nombre, imprime sus ecs. (4b) y (5) con **29** y rótulos duales «ft (m)»; leerla literal «en SI» reproduce el error de +9.6 % que esta nota advierte.
>
> Y el parecido con **2·g no es una coincidencia**: `K = 2g/φ²`, con φ = 1.486 en el sistema inglés y φ = 1 en SI. De ahí `2·32.2/1.486² = 29.16` y `2·9.81456 = 19.629`. Lo único que separa 19.63 de 19.62 es **cuál g**: HDS-5 trabaja con 32.2 ft/s² = 9.81456 m/s² y el proyecto usa `constantes_fisicas.G = 9.81`. Se conserva el 19.63 **transcrito de la fuente**, no el 2·G derivado; la diferencia afecta al término de fricción en un +0.05 % — unas 190 veces menos que el 9.6 % del 29 imperial, que es el error que esta nota existe para advertir.

> **k_e — vacío que pasó inadvertido hasta la implementación.** Ningún numeral del Manual MTC ni del Manual de Puentes fija el coeficiente de pérdida de entrada k_e. Para la embocadura *square edge with headwall* (adoptada en §9.1), se toma **k_e = 0.5** de las tablas de coeficiente de pérdida de entrada del HDS-5. Etiqueta **[C]**, declarado en `criterios_adoptados.py` como `ke_entrada`.

**Relevancia en este proyecto:** con descarga a drenes con nivel propio, el TW puede ahogar la alcantarilla. Se puede cumplir y/D ≤ 0.75 en el barril y aun así embalsar más de un metro sobre terreno agrícola.

---

## Fase 5 — Verificaciones

| # | Verificación | Criterio | Ancla |
|---|---|---|---|
| **V1** | Borde libre | Mínimo **25 % de altura, diámetro o flecha** → **y/D ≤ 0.75** | [N] 4.1.1.3.7 b), pág. 79 |
| **V2** | Velocidad mínima | **V ≥ 0.25 m/s** | [N] 4.1.1.3.6, pág. 75 |
| **V2b** | Sedimentación / colmatación | Material sólido de arrastre + **acceso de mantenimiento en planos** | [N] + [A] |
| **V3** | Velocidad máxima | **Solo techo admisible.** Concreto **V ≤ 6.0 m/s**; ladrillo con concreto **V ≤ 3.5**; mampostería de piedra **V ≤ 2.0**. El par de la Tabla Nº 10 es un rango de valores MÁXIMOS según calidad del revestimiento, **no** un piso y un techo: el extremo inferior es el máximo admisible del acabado más pobre, y V3 no lo exige como mínimo. El piso universal de autolimpieza es **V2** (0.25 m/s). **TMC y HDPE: PPI/FHWA, valor por extraer** | [N] Tabla Nº 10, num. 4.1.1.3.6, pág. 76 / [C] |
| **V4** | Carga a la entrada HW | **HW ≤ cota de subrasante − resguardo(CBR)** | **[N→]** ver 5.1 |
| **V4b** | Relación HW/D | 1.2 – 1.5 | **[A]** — *corregido desde `[C]`.* El HDS-5 **no fija** HW/D: su num. 2.2.5 d) «Agency Constraints», pág. impresa **2.10** (la v8 citaba la 2.14, que trata de espolones de escombros y seguridad vial) **describe** lo que imponen las agencias viales de EE. UU. — «The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5» — y en el Perú la agencia es el MTC, que no fija ninguno. Elegir 1.5, que es el extremo **menos restrictivo**, es adopción del proyectista. **No implementada:** ver `M5.verificaciones_no_evaluadas()`. Ref. `NOR-HDS-02`, `MAT-D2`, `SIS-A-02` |
| **V5** | Remanso aguas arriba | Embalse dentro del **derecho de vía**, sin afectación a terceros ni a faja marginal | [N] DG-2018 + Ley 29338 |
| **V6** | Material sólido de arrastre | Con palizada: sección única mayor | [N] |
| **V7** | Flotación del conducto | **γ_DC,min · DC + γ_EV,min · EV ≥ γ_WA · U.** Tubería vacía, NF en su cota más alta. Las cargas que estabilizan (peso propio DC y peso del relleno EV) se **minoran**; la subpresión, que desestabiliza (WA), se **mayora**. Con los mínimos de la Tabla 3.4.1-2 es la forma 0.90·(DC + EV) ≥ 1.00·U. **Corrige la redacción anterior**, ΣW ≥ FS · U, que era un factor de seguridad global de tensión admisible dentro de un marco LRFD (§0.2) | [N] subpresión 2.4.3.8.2 + [A] los γ (`factores_carga_aashto`, Tablas 3.4.1-1/-2) |
| **V8** | Evento extremo (FEN) | A TR mayor: la vía **no colapsa** aunque desborde | [N] verificación, no diseño |
| **V9** | **Disponibilidad de diámetro** | D requerido ≤ tope de la norma de producto del material | **[C]** — nuevo en v7 |

### 5.1 Resguardo de V4 — valor y advertencia

**Manual de Suelos, num. 4.5.4 y 9.1(3)** (págs. 42, 89-90):

| CBR | Calidad | Resguardo sobre la napa |
|---|---|---|
| ≥ 20 % | Excelente – muy buena | **0.60 m** |
| 6 – 20 % | Buena – regular | **0.80 m** |
| 3 – 6 % | Insuficiente | **1.00 m** |
| < 3 % | Inadecuada | **1.20 m** |

> **ADVERTENCIA DE APLICACIÓN.** El numeral regula la separación frente a la **napa freática** (nivel permanente), **no** frente a un nivel transitorio de avenida. Aplicarlo al HW es una **extensión por analogía** y se declara como **[N→]**.
>
> Redacción: *"Ante la ausencia de un criterio normativo peruano que relacione la carga hidráulica de entrada con el nivel de subrasante, se adopta por analogía el resguardo que el Manual de Suelos (num. 4.5.4) exige frente al nivel freático, por ser el único parámetro normativo nacional que protege la subrasante de la saturación."*

Si no se cumple: subdrenes, capas drenantes/anticontaminantes o **elevar la rasante** — lo que alimenta 7.A.

### 5.2 Por qué V2 nunca gobierna

Para D = 0.90 m, y/D = 0.75 y n = 0.013, alcanzar 0.25 m/s requiere **S ≈ 0.00006 (0.006 %)**, muy por debajo de cualquier pendiente constructiva. **El piso normativo se cumple siempre y no restringe el diseño.**

La norma no protege del riesgo real, que es la **colmatación** en una llanura de riego con alta carga de finos. Por eso V2b existe y el acceso de mantenimiento va en los planos.

---

## Fase 6 — Protección de entrada y salida [N]

**Laushey** — num. 4.1.1.3.7 c), pág. 80:

$$d_{50} = \frac{V^{2}}{3.1\,g}$$

d₅₀ en m, V en m/s, g = 9.8 m/s². **La constante 3.1 asume sistema métrico.**

| V salida (m/s) | d₅₀ (m) |
|---|---|
| 1.0 | 0.03 |
| 2.0 | 0.13 |
| 3.0 | 0.30 |
| 4.0 | 0.53 |

**d₅₀ no es un diseño de enrocado.** Completar con espesor (1.5–2.0 · d₅₀) **[A]**, longitud aguas abajo **[A]**, granulometría completa y **filtro**. Sin filtro el enrocado se socava por debajo y falla.

Con pendientes bajas los d₅₀ son pequeños (3–13 cm): lo probable es que gobierne el **emboquillado de piedra** por razones constructivas.

---

## Fase 7 — Compatibilidad geométrica

### 7.A Tamizado previo — fija la rasante una sola vez

$$\text{cota rasante} \ \ge\ \max\begin{cases} \text{cota clave} + h_{rec} + e_{paq} \\ HW + \text{resguardo}(CBR) + e_{paq} \end{cases}$$

Correr el tamizado con el diámetro máximo supuesto **antes** de definir el perfil longitudinal.

**Altura mínima de relleno sobre la clave — EG-2013:**

| Material | h_rec mínimo | Fuente |
|---|---|---|
| **HDPE/PAD** | **0.30 m** desde la clave hasta la subrasante | [N] 508.07/508.08, pág. 982 |
| Concreto y TMC | **No fijado.** Remite al Proyecto, AASHTO M-170M (clases I–V) o ASTM A-807 | [C] norma de producto |

Nota constructiva [N]: el equipo pesado no circula sobre el conducto antes de que el relleno alcance 0.30 m.

### 7.B Verificación final por punto

- **Longitud** = ancho de plataforma + proyección de taludes, afectada por esviaje
- **Esviaje** siguiendo el alineamiento natural del cauce [N]
- **Pendiente de la alcantarilla:** la del cauce (V2 nunca la restringe). La restricción real es constructiva y de cota del receptor
- **Cotas de entrada y salida** amarradas al perfil del cauce y a la cota de fondo del receptor
- El chequeo devuelve *"no factible → subir rasante X cm"*, nunca un resultado silencioso

**Acoplamiento circular declarado:** rasante → paquete estructural → subrasante → CBR → resguardo → V4 → rasante. Se corta fijando la rasante en 7.A y congelándola.

---

## Fase 8 — Verificación estructural del conducto

**Sin catálogo de proveedor.** La selección se hace contra las **normas de producto**, coherente con la decisión de neutralidad comercial de §3.2:

| Material | Norma que define clases / calibres por altura de relleno |
|---|---|
| Concreto reforzado | **AASHTO M-170M** — clases I a V |
| TMC | **ASTM A-807 / AASHTO M36** — calibre según altura |
| HDPE | **AASHTO M294** + AASHTO LRFD Sec. 12 |

1. Seleccionar clase o calibre según la altura real de relleno del punto.
2. Verificar que esa altura cae en el rango admisible de la clase.
3. **Flotación (V7)** — obligatoria con NF a 1.4 m.
4. **Cama de apoyo y relleno lateral según EG-2013** (8.1). En estructuras flexibles el relleno lateral **es parte de la estructura**.
5. **Diferir al expediente** la verificación detallada: rigidez de anillo, pandeo y resistencia de costura por AASHTO LRFD Sec. 12 (que el Manual de Puentes **no incorpora**), o clase D-load con factor de cama.

Para el **marco de concreto** del canal de 2.75 m no aplica la simplificación: diseño completo por AASHTO LRFD Sección 5.

### 8.1 Cama de apoyo y relleno lateral — EG-2013 Sección 500

| Material | Cama de apoyo | Sujeción / relleno lateral | Numeral |
|---|---|---|---|
| **Concreto simple** | Concreto Clase F (f'c = 14 MPa), ≥ 15 cm | Clase F hasta ≥ **1/4** del diámetro exterior. Relleno Sec. 502 ≥ 95 % MDS | 505.03/.07/.10/.11, págs. 950-951 |
| **Concreto reforzado** | Subbase granular (Sec. 402) ≥ 15 cm, ≥ 95 % | Subbase hasta ≥ **1/6** del diámetro exterior. Relleno Sec. 502 | 506.03/.07/.10/.11, págs. 959-960 |
| **TMC** | Subbase granular ≥ 15 cm, ≥ 95 %, con arena suelta de 12 mm | Capas de 15–20 cm: ≥ **90 %** en base y cuerpo, ≥ **95 %** en corona | 507.06/.07/.08, pág. 970 |
| **HDPE/PAD** | **Arena gruesa**, capas de 15 cm, espesor 15–30 cm (30 en roca o suelo blando) | Capas alternadas y simétricas de 15 cm a > **95 %**; los 30 cm superiores a ≥ **100 %**. **Prohibida la anegación** | 508.05/.07, págs. 981-982 |

Partidas independientes: 505.A, 506.A, 507.A/B, 508.A.

---

## Fase 9 — Cabezal y aletas

### 9.1 Condición normativa

EG-2013 Sección 503 (Concreto Estructural), num. 503.01, pág. 905, describe el suministro de concreto para *"estructuras de drenaje, muros de contención, cabezales de alcantarillas, cajas de captación, aletas, sumideros..."*.

**Precisión:** los cabezales **no tienen partida con numeral propio**; se pagan bajo el volumen de concreto estructural (Sec. 503) y el acero (Sec. 504). Que aparezcan nominados en 503.01 confirma que son elemento estándar de terminación, pero el argumento es más débil que "existe una partida específica".

**Geometría de embocadura:** tubo a ras del muro (*square edge*), coherente con las constantes HDS-5 adoptadas en §4.2. Ambas decisiones deben moverse juntas: cambiar el detalle obliga a cambiar las constantes.

### 9.2 Cargas — AASHTO LRFD vía Manual de Puentes [N]

**Combinaciones:** AASHTO LRFD Sec. 3.4.1 — Resistencia I, Servicio I, Evento Extremo I (num. 2.4.5.3, págs. 140-143).

**Carga viva:** **HL-93** (num. 2.4.3.2.2.1, págs. 103-104).

**Sobrecarga en el trasdós** (num. 2.1.4.3.9, pág. 91): con tráfico a distancia horizontal ≤ H/2 desde la parte superior de la estructura, se añade sobrecarga vertical **≥ 0.60 m de relleno equivalente**. Presión horizontal = γ · 0.60 · k_a. **En un cabezal bajo terraplén vial siempre aplica.**

**Empuje de tierras:** activo, Ka = tan²(45 − φ/2). **Empuje hidrostático y subpresión:** con NF a 1.4 m no es opcional.

#### Cadena sísmica — desagregada

| Paso | Símbolo | Valor | Origen | Etiqueta |
|---|---|---|---|---|
| Aceleración pico en roca Clase B, Tr = 1000 años | PGA | **0.50 g** | Manual de Puentes, Apéndice A3, mapa "PGA, T = 0.0 seg" | [N] |
| Factor de sitio | F_pga | **1.0** | Tabla 2.4.3.11.2.1.2-1 (valores [N]); **elección** ante ausencia de SPT | [A] |
| Aceleración ajustada por sitio | **A_s = F_pga · PGA** | **0.50 g** | Calculado | — |
| Coeficiente sísmico de base | **k_h0 = A_s** | **0.50** | Manual de Puentes, 2.8.1.1.14.2 | [N] |
| Factor de muro (rígido, empotrado) | — | **1.0** | Manual de Puentes, 2.8.1.1.14.2 | [N] |
| **Coeficiente sísmico horizontal de diseño** | **k_h** | **0.50** | Calculado | — |
| Coeficiente sísmico vertical | k_v | **0** | Adopción habitual en muros de baja altura | [A] |

*Si el muro admitiera desplazamiento de 25–50 mm, k_h = 0.5 · k_h0 = 0.25. **No asumirlo en un cabezal empotrado en terraplén.***

Para K_AE por **Mononobe-Okabe** se requieren además φ del relleno, pendiente del relleno (i), inclinación del muro (β) y fricción muro-suelo (δ).

**Todos estos valores se leen desde `criterios_adoptados.py`.**

### 9.3 Estabilidad — E.050 [N]

| Verificación | Estático | Sísmico | Numeral |
|---|---|---|---|
| Capacidad portante (falla por corte) | **3.0** | **2.5** | Art. 21.1/21.2, pág. 34 |
| Volteo — estabilidad interna | **1.50** | **1.25** | 39.13.6 a), pág. 72 |
| Deslizamiento — estabilidad interna | **1.50** | **1.25** | 39.13.6 a), pág. 72 |
| Estabilidad global del muro | **1.50** | **1.25** | 39.13.6 b), pág. 72 |
| Estabilidad del talud | **1.50** | **1.25** | Art. 30.3, pág. 39 |

**Parámetros de resistencia** (Art. 20, pág. 33): en cohesivos φ = 0; en friccionantes c = 0. No se combinan.

**Zapata próxima al talud** — doble verificación:
- **E.050 Art. 30.1-30.2:** capacidad de carga considerando inclinación de la superficie y de la base; análisis de estabilidad global del talud con la estructura cargándolo
- **Manual de Puentes 2.8.1.3.1.2c** (págs. 272-273): **N_q = 0.0**; N_c y N_γ se reemplazan por **N_cq** y **N_γq** (figuras 2.8.1.3.1.2c-1 y -2, Meyerhof 1957). N_s = 0 si B < H_s; N_s = γH_s/c si B ≥ H_s

La penalización es severa por pérdida de confinamiento. **El cabezal se apoya en el borde del terraplén, no en terreno horizontal.**

### 9.4 Refuerzo y durabilidad

- Flexión y corte por **AASHTO LRFD Sección 5**
- **Durabilidad y recubrimientos por E.060** (excepción de 0.2). Rige el recubrimiento mayor entre AASHTO y E.060
- **Referencia de cuantías mínimas** (E.060 Art. 14.3.1, pág. 133): horizontal ≥ 0.002, vertical ≥ 0.0015; acero por temperatura en ambas caras si espesor ≥ 250 mm (Art. 14.8.3); espaciamiento ≤ 3h y ≤ 400 mm (Art. 14.3.3)
- **Alternativa en concreto ciclópeo** (E.060 Art. 22.10, págs. 194-195): f'c de matriz ≥ 10 MPa, piedra desplazadora ≤ 30 % del volumen. Admitido para muros de gravedad. **Opción realista para cabezales pequeños**

---

## Fase 10 — Alcantarillas de alivio: espaciamiento

**Espaciamiento de diseño = mín(límite normativo, longitud por capacidad).**

**1. Límite normativo [N]** — num. 4.1.2.1 d), pág. 178:

| Región | Longitud máxima de cuneta |
|---|---|
| Seca o poco lluviosa | **250 m** |
| Muy lluviosa | **200 m** |

**Adoptado: 200 m [A].** El régimen normal de Piura es árido (250 m), pero el evento de diseño relevante es el FEN, durante el cual la zona se comporta como región muy lluviosa. Sensibilidad (200, 250).

**2. Límite hidráulico [N]:** diseñar la cuneta → capacidad admisible con borde libre → caudal aportante por metro lineal (área tributaria, intensidad de TR = 35 años) → longitud a la cual se agota la capacidad.

**Condición de descarga [N]:** toda descarga hacia predio agrícola sin dren receptor genera afectación. Reconducir a un dren existente o mantener dentro del **derecho de vía** (DG-2018) sin afectación a terceros (Ley 29338).

---

## Fase 11 — Entregables

1. **Memoria de cálculo por punto crítico:** datos con fuente, iteraciones, cada verificación con "cumple / no cumple" **y su numeral**
2. **Bloque de declaración de criterios adoptados** generado por M11 desde `criterios_adoptados.py`, con verificaciones pendientes al final
3. **Tabla resumen:** progresiva, familia, TR, tipo, material y norma de producto, diámetro, V, y/D, HW, control gobernante, protección de salida, tipo de cabezal
4. **Declaración de vacíos normativos** (0.3) como capítulo de la metodología
5. **Análisis de sensibilidad** alimentado por los rangos de `criterios_adoptados.py`
6. **Validación externa:** correr 1–2 puntos en HY-8 (FHWA, gratuito) y adjuntar la comparación
7. **Planos:** planta y perfil por obra; cabezal y aletas con el detalle de embocadura a ras; cama de apoyo y relleno lateral por material; protección de salida con filtro; **acceso de mantenimiento**
8. **Especificaciones y metrados** referidos a EG-2013 Sec. 500 (conductos) y 503/504 (cabezales)
9. **Cuadro de compatibilidad rasante–alcantarilla** (salida de 7.A)

---

## Tableros de pendientes

Los pendientes no son homogéneos. Separarlos por naturaleza permite estimar esfuerzo y asignar responsable.

### Tablero 1 — Verificaciones documentales
*Abrir el documento y confirmar. Esfuerzo: minutos a una hora cada una.*

| # | Qué verificar | Documento | Bloquea |
|---|---|---|---|
| 1.1 | **VERIFICADO — la dispensa por periodo corto de la Clase F no existe.** No figura en el articulado 3.10.3.1, ni en el comentario C3.10.3.1, ni en ninguna tabla o nota a tabla. AASHTO exige estudio de respuesta de sitio específico para la Clase F, de forma incondicional. La cita se retira de la memoria y el uso de factores tabulados pasa a adopción `[A]` (§0.5) | AASHTO LRFD 9.ª ed. (2020), Art. 3.10.3.1 y C3.10.3.1 | **Cerrado.** Reabre §0.5 como decisión de proyecto, no como cita normativa |
| 1.2 | Topes superiores de diámetro por material | ASTM C76 / AASHTO M36 / M294 | V9 y el tope del script |
| 1.3 | Velocidades máximas admisibles para TMC y HDPE — **valores numéricos** | PPI / FHWA | V3 para materiales flexibles |
| 1.4 | Registrar coordenadas o curva de isoaceleración de la lectura del PGA | Manual de Puentes, Apéndice A3 | Trazabilidad de §0.4 |

### Tablero 2 — Decisiones de proyecto
*No se resuelven leyendo una norma. Las tomas tú y las declaras.*

| # | Decisión | Estado | Bloquea |
|---|---|---|---|
| 2.1 | Tipo de HDPE: interior liso o corrugado | **Abierta.** Condiciona la validez de la analogía del n y de las constantes HDS-5 | §4.1.1 y §4.2.1 |
| 2.2 | Magnitud sísmica **M_w** para el factor de escala de la evaluación de licuefacción | **Abierta.** El PGA no la entrega | Fase 0-bis |
| 2.3 | Detalle de embocadura del cabezal | **Cerrada:** tubo a ras del muro (*square edge*) | §4.2 y §9.1 — deben moverse juntas |
| 2.4 | Demanda sísmica para licuefacción | **Cerrada:** Tr = 1000 años | Fase 0-bis |
| 2.5 | Longitud máxima de cuneta | **Cerrada:** 200 m por régimen FEN | Fase 10 |

### Tablero 3 — Datos externos por conseguir
*Dependen de terceros o de otros estudios. Son los de mayor plazo.*

| # | Dato | Fuente | Bloquea | Criticidad |
|---|---|---|---|---|
| 3.1 | **Caudal de diseño y geometría de los drenes y canales receptores** | ANA / Junta de Usuarios del Bajo Piura | **TW de todas las alcantarillas + la Familia C completa** | **Máxima** |
| 3.2 | ¿La serie SENAMHI contiene 1983, 1998 y 2017? | SENAMHI / tu propio análisis | Q de diseño de **todos** los puntos | **Máxima** |
| 3.3 | IMDA de diseño → clase de vía | Estudio de demanda | Número de calicatas exigido (§1.4) | Media |
| 3.4 | Ensayos de sulfatos, cloruros y sales solubles | Laboratorio | Clase de exposición E.060 → cemento, a/c, f'c, recubrimiento | Media |
| 3.5 | pH y resistividad (solo si TMC sigue en carrera) | Laboratorio | Defensibilidad del TMC | Baja |
| 3.6 | SPT ≥ 15 m, cada 1 m | Estudio geotécnico | Clase de sitio definitiva y evaluación de licuefacción | Diferida al expediente |

**Lectura del tablero:** los ítems 3.1 y 3.2 son los verdaderamente críticos. El 3.1 bloquea una familia entera de estructuras y el TW de todas las demás; el 3.2 condiciona el caudal de diseño de todo el estudio. Ambos estaban fuera de la lista original de siete y son los de mayor plazo, porque dependen de terceros.

---

## Anexo A — Índice de criterios no normativos

**Contenido completo en `criterios_adoptados.py`.**

| Criterio | Etiqueta | Estado |
|---|---|---|
| PGA en roca (0.50 g) | [N] | **Cerrado.** Falta registrar coordenadas de lectura |
| Clase de sitio (F, factores tabulados por adopción) | [A] | **Reabierto y redeclarado.** La dispensa por periodo corto que lo cerraba no existe en AASHTO (verificado contra la 9.ª ed., 2020). Usar factores tabulados es adopción del proyectista, no permiso de la norma. Lo cierra el estudio de respuesta de sitio específico — §0.5 |
| F_pga = 1.0 | [A] | Tabla [N]; elección [A]. Sensibilidad (0.9, 1.0) |
| Factor de muro = 1.0 | [N] | Firme |
| k_v = 0 | [A] | Sensibilidad (0, 0.5·k_h) |
| M_w para licuefacción | [A] | **Sin valor.** Tablero 2.2 |
| Constantes HDS-5 para HDPE | [C] | Carta *Circular Concrete, square edge*. Condicionado a HDPE de interior liso |
| k_e (coeficiente de pérdida de entrada, §4.3) | [C] | HDS-5, embocadura square edge with headwall. **Cerrado en implementación** — sin numeral peruano |
| n de Manning para HDPE | [N→] | **Rango (0.010, 0.013)** por analogía. No valor puntual. El código lo **lee de** `constantes_normativas.MANNING["concreto_recto"]`, no lo copia: una analogía que duplica el literal de su origen deja de serlo en cuanto uno de los dos cambie |
| Velocidad máxima en HDPE y TMC | [C] | **Sin valor.** Fuente identificada (PPI/FHWA), valores por extraer |
| Progresión de diámetros | [C] | 0.90 m + 0.15 m, topes por norma de producto |
| HW/D máximo (1.5) | [A] | Sensibilidad (1.2, 1.5), **subrango** de la banda 1.0–1.5 que el HDS-5 describe (no prescribe). Corregido desde [C]. Ref. `NOR-HDS-02` |
| Resguardo HW–subrasante | [N→] | Analogía declarada desde el criterio de napa freática |
| TW en el receptor | [A] | **Sin valor.** Tablero 3.1 |
| Longitud máxima de cuneta (200 m) | [A] | Sensibilidad (200, 250) |
| φ del relleno del trasdós | [A] | **Sin valor.** Corte directo |
| c, φ del suelo de fundación | [A] | **Sin valor.** Corte directo o SPT |
| Capacidad portante admisible | [A] | **Sin valor.** EMS conforme a E.050 |
| Espesor de protección de salida (1.75 · d₅₀) | [A] | Sensibilidad (1.5, 2.0) |
| Ángulo de aletas | [A] | Según esviaje de cada punto |
| Origen de la cota de fondo de entrada (`origen_cota_fondo_entrada`) | [A] | **Sin valor.** HW es una carga *sobre el fondo de la entrada* (§4.2/4.3) y esa cota **no es columna de §1.2**: el CSV trae `cota_terreno`, `cota_rasante`, `cota_subrasante` y `cota_fondo_receptor` —la de la salida—, no la del invert de entrada. §7.B pide las cotas «amarradas al perfil del cauce y a la cota de fondo del receptor» sin fijar la regla. Gobierna **V4, V7 y las dos condiciones del tamizado 7.A**, o sea la rasante. Regla implementada: `"cota_terreno"` (adoptar el terreno natural del cruce). Lo cierra la **cota de invert medida por punto**, como columna propia del CSV. Ref. SIS-A-04 |
| Homogeneidad de la serie hidrológica (FEN) | [A] | Tablero 3.2 |

---

## Anexo B — Constantes normativas para el script

**Solo constantes [N] con numeral verificado.** Todo lo demás en `criterios_adoptados.py`.

```python
# ================= Manual de Hidrologia (RD 20-2011-MTC/14) =================
LUZ_MAX_ALCANTARILLA = 6.0          # m; >= 6.0 -> puente (4.1.1.3.1 / 4.1.1.5.1)
DIAMETRO_MIN = 0.90                 # m (4.1.1.3.4 a)
DIAMETRO_MIN_SELVA_ALTA = 1.22      # m = 48"; NO aplica en costa (4.1.1.3.7 a)
Y_SOBRE_D_MAX = 0.75                # borde libre >= 25% (4.1.1.3.7 b)
V_MIN = 0.25                        # m/s (4.1.1.3.6)
LAUSHEY_K = 3.1                     # d50 = V^2/(3.1*g), metrico (4.1.1.3.7 c)
G = 9.8                             # m/s2

RIESGO_ADMISIBLE = {                # Tabla N 02, num. 3.6
    "quebrada_importante": {"R": 0.30, "n": 25},   # -> TR = 71 anios
    "quebrada_menor":      {"R": 0.35, "n": 15},   # -> TR = 35 anios
}
# TR = 1 / (1 - (1-R)**(1/n))       # sin piso normativo

MANNING = {                         # Tabla N 09: (n_min, n_max)
    "metal_corrugado": (0.021, 0.030),
    "concreto_recto":  (0.010, 0.013),
    "madera_duelas":   (0.010, 0.014),
    # HDPE no listado -> criterios_adoptados.valor("n_manning_hdpe")
}
# n_max -> capacidad y tirante ; n_min -> velocidad y socavacion

V_MAX = {         # Tabla N 10 "Velocidades maximas admisibles" (4.1.1.3.6, pag. 76)
    "concreto":            (3.0, 6.0),
    "ladrillo_c_concreto": (2.5, 3.5),
    "mamposteria_piedra":  (2.0, 2.0),
    # TMC y HDPE no listados -> criterios_adoptados
}
# Los DOS extremos son velocidades MAXIMAS (rango por calidad del
# revestimiento), no un piso y un techo. V3 verifica solo el superior; el
# minimo de autolimpieza es V2 = 0.25 m/s (misma pagina) y vale para todos.

LONG_MAX_CUNETA = {"seca": 250.0, "muy_lluviosa": 200.0}   # m (4.1.2.1 d)

# ================= HDS-5 (FHWA) 3a ed., abril 2012 =========================
# Apendice A, Tabla A.1, pag. A.8
KU_METRICO = 1.811                  # q* = KU*Q/(A*D**0.5)
Q_LIM_NO_SUMERGIDO = 3.5
Q_LIM_SUMERGIDO    = 4.0            # entre ambos: interpolacion lineal

HDS5_INLET = {   # cartas por forma/material; dentro de cada una, por borde
    "circular_concreto_square_edge_headwall": {"K": 0.0098, "M": 2.00,
                                               "c": 0.0398, "Y": 0.67, "Ks": -0.5},
    "circular_cmp_headwall":                  {"K": 0.0078, "M": 2.00,
                                               "c": 0.0379, "Y": 0.69, "Ks": -0.5},
    "circular_cmp_mitered":                   {"K": 0.0210, "M": 1.33,
                                               "c": 0.0463, "Y": 0.75, "Ks":  0.7},
}
# Ks NO figura en la Tabla A.1: proviene de la formulacion (-0.5 / +0.7). No omitir.
# HDPE -> criterios_adoptados.valor("hds5_embocadura_hdpe")

# ================= Control de salida (SI) ==================================
K_FRICCION_SI = 19.63               # H = (1 + ke + 19.63*n^2*L/R^(4/3)) * V^2/(2g)
                                    # OJO: 29 es el valor ingles.
                                    # TEST UNITARIO OBLIGATORIO.
# ho = max(TW, (yc + D)/2)

# ================= Diametros normalizados (ASTM / AASHTO) ==================
D_PASO = 0.15                       # m; reproduce las series de 6" y 150 mm
D_INICIO = 0.90                     # m; minimo normativo MTC
D_MAX = {                           # topes por norma de producto - VERIFICAR
    "concreto_reforzado": 2.70,     # ASTM C76 / AASHTO M170
    "tmc":                2.10,     # AASHTO M36 / ASTM A760
    "hdpe":               1.50,     # AASHTO M294  <- el mas restrictivo
}
# Sin tope, el solver puede converger a un diametro inexistente.
# Superado el tope: devolver "material descartado por diametro requerido".

# ================= Manual de Suelos (RD 10-2014-MTC/14) ====================
RESGUARDO_NAPA_SUBRASANTE = [       # (CBR_min, CBR_max, resguardo_m)  num. 4.5.4
    (20.0, None, 0.60), (6.0, 20.0, 0.80),
    (3.0, 6.0, 1.00),   (None, 3.0, 1.20),
]
# Su aplicacion al HW es POR ANALOGIA [N->] -> ver criterios_adoptados
CBR_MIN_SUBRASANTE = 6.0            # % (num. 3.3)
COMPACTACION_CORONA = 0.95          # 0.30 m superiores, capas de 0.15 m
COMPACTACION_CUERPO = 0.90          # capas de hasta 0.30 m

CALICATAS_POR_KM = {"autopista": 4, "dual": 4, "primera_clase": 4,
                    "segunda_clase": 3, "tercera_clase": 2, "bajo_volumen": 1}
ESPACIAMIENTO_PERFIL_KM = 4.0       # nivel perfil

# ================= EG-2013, Seccion 500 ====================================
H_RELLENO_MIN = {
    "hdpe":     0.30,               # m, clave a subrasante (508.07/508.08)
    "concreto": None,               # AASHTO M-170M (clases I a V)
    "tmc":      None,               # ASTM A-807 / AASHTO M36
}
SUBSECCION = {"concreto_simple": "505", "concreto_reforzado": "506",
              "tmc": "507", "hdpe": "508"}
SECCION_CABEZALES = "503"           # concreto estructural (+504 acero)

# ================= Manual de Puentes (RD 041-2016-MTC/14) ==================
SOBRECARGA_TRASDOS_H_EQ = 0.60      # m de relleno equivalente (2.1.4.3.9)
CARGA_VIVA = "HL-93"                # (2.4.3.2.2.1)
NQ_ZAPATA_EN_TALUD = 0.0            # (2.8.1.3.1.2c)
F_PGA_TABLA = {                     # Tabla 2.4.3.11.2.1.2-1, PGA >= 0.50
    "C": 1.0, "D": 1.0, "E": 0.9,
}
# PGA, F_pga elegido, factor de muro y k_v -> criterios_adoptados

# ================= E.050 (RM 406-2018-VIVIENDA) ============================
FS = {
    "capacidad_portante": {"estatico": 3.00, "sismico": 2.50},   # Art. 21
    "volteo":             {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 a
    "deslizamiento":      {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 a
    "estabilidad_global": {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 b
    "talud":              {"estatico": 1.50, "sismico": 1.25},   # Art. 30.3
}
SPT_PROF_MIN = 15.0                 # m (Art. 38)
SPT_ESPACIAMIENTO = 1.0             # m entre ensayos

# ================= E.060 (durabilidad, excepcion declarada) ================
SULFATOS = [                        # Tabla 4.4: (SO4_min%, SO4_max%, cemento, a/c, f'c_MPa)
    (0.00, 0.10, None,               None, None),
    (0.10, 0.20, "II/IP(MS)/IS(MS)", 0.50, 28),
    (0.20, 2.00, "V",                0.45, 31),
    (2.00, None, "V + puzolana",     0.45, 31),
]
CLORUROS_EXTERNOS = {"a_c_max": 0.40, "fc_min_MPa": 35}   # Art. 4.2 / 4.4
RECUBRIMIENTO = {"contra_suelo": 70, "suelo_intemperie_ge_3_4": 50,
                 "suelo_intemperie_le_5_8": 40}           # Art. 7.7.1

# ================= E.030 (RM 183-2026-VIVIENDA) - solo referencia ==========
ZONA_SISMICA_LA_UNION = 4
Z_E030 = 0.45                       # Tr = 475 anios - NO se usa para el cabezal
PERFIL_SUELO_PRESUNTO = "S5"        # suelos potencialmente licuables (Art. 14.6)
```

---

## Anexo C — Arquitectura del script

```
criterios_adoptados.py     <- fuente unica de verdad para [N->], [C] y [A]
constantes_normativas.py   <- Anexo B: solo [N]
M0_carga.py ... M11_reporte.py
```

| Módulo | Fase | Estado |
|---|---|---|
| M0 · Carga y validación CSV | 1 | **Codificable** |
| M1 · Clasificación y TR | 2 | **Codificable** |
| M2 · Selección de material | 3 | **Codificable** — desbloqueado por §3.2 |
| M3 · Motor hidráulico (Manning + Brent) | 4.1 | **Codificable** |
| M4 · Control entrada/salida | 4.2-4.3 | **Codificable** — **dos solvers**: tirante normal y crítico |
| M5 · Verificaciones | 5 | **Codificable** — V3 incompleta para TMC/HDPE hasta Tablero 1.3 |
| M6 · Protección de salida | 6 | **Codificable** |
| M7 · Compatibilidad geométrica | 7 | **Codificable** — desbloqueado por §3.2 y §8 |
| M8 · Estructural del conducto | 8 | **Codificable** — normas de producto en lugar de catálogo |
| M9 · Cabezal | 9 | **Codificable** con la cadena sísmica de 9.2 |
| M10 · Alivio | 10 | **Codificable** |
| M11 · Reporte | 11 | **Codificable** — debe invocar `reporte_criterios()` |

**Los doce módulos están desbloqueados.** Lo que falta son datos de entrada (Tablero 3), no arquitectura.

### Notas críticas de programación

- **Ningún módulo declara valores no normativos.** Todos se leen con `criterios_adoptados.valor(clave)`. Un literal fuera de esos dos archivos es un defecto de arquitectura.
- **Un criterio con valor `None` detiene el script con excepción.** Nunca se sustituye por defecto.
- **Tope superior de diámetro obligatorio por material.** Superado el tope, el material se descarta con mensaje explícito. El HDPE (~1.50 m) es el crítico.
- **Q(y/D) no es monótona** cerca de sección llena (máximo en y/D ≈ 0.938). Al topar en 0.75 se evita la zona, pero el solver debe manejar el caso "sin solución" → siguiente diámetro.
- **M4 necesita tirante crítico:** Q²T/(gA³) = 1, segundo Brent sobre θ.
- **Unidades del control de salida:** 19.63 en SI, no 29 (corregido desde 19.62; ver la nota de unidades de §4.3). Test unitario obligatorio.
- **El n de HDPE es un rango, no un valor.** Un valor puntual rompe la regla de doble n y subestima velocidad y socavación.
- Cada verificación devuelve el **booleano y el numeral que la sustenta**.
- M11 imprime los criterios usados y, al final, los pendientes que no deben citarse en la memoria.
