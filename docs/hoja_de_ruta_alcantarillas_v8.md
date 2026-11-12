# Hoja de ruta — Diseño de alcantarillas y cabezales · v8
**Vía de evitamiento, distrito de La Unión (Piura) — nivel de perfil**
*Cierres normativos integrados. Pendientes segregados por naturaleza.*

> **Corregido (`INF-5.1.11`, T-0, 2026-11-11).** Este encabezado decía «· v7» dentro de un archivo que se llama `hoja_de_ruta_alcantarillas_v8.md` y al que todo el repositorio —`CLAUDE.md`, el código, las notas de este mismo documento— cita como «la v8». Se corrige el título y **no se reescribe la tabla de versiones de abajo**: sus filas describen lo que integró cada versión hasta la v7 y son historia. Lo que distingue a la v8 no es una fila más sino las **enmiendas fechadas que cada apartado lleva como nota «Corregido (…)»**, cada una con el ID del hallazgo que la motivó; el clon del repositorio tiene un solo commit, de modo que qué cambió exactamente al renombrar el archivo de v7 a v8 no se puede reconstruir desde el historial, y aquí no se inventa. T-0 de la cadena T (`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`) añade las de §1.1, §1.2, §2.3, la fila V5 de la Fase 5, §7.B, §9 y los Anexos A y B. Cuatro de ellas son **prospectivas**: declaran lo que la hoja pasa a pedir y qué prompt de la cadena lo implementa, y dicen qué hace hoy el código mientras tanto.

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
| **v8** | **Este archivo.** La v7 enmendada en sitio por las sesiones de corrección: cada cambio es una nota «Corregido (…)» en el apartado que corrige, con su ID. El encabezado decía «v7» hasta T-0 (`INF-5.1.11`) |

### Cambios respecto de la v6

| v6 decía | v7 corrige | Origen |
|---|---|---|
| "La Tabla A.1 organiza sus entradas **por geometría, no por material**" | **Sobreafirmación mía.** La Tabla A.1 organiza por **carta de material/forma** y, dentro de cada carta, por configuración de borde. Ver §4.2.1 | Autocorrección |
| Excepción de periodo corto: verificación pendiente | **Retirada — la regla no existe.** Verificado contra AASHTO LRFD 9.ª ed. (2020), Art. 3.10.3.1 y C3.10.3.1: la Clase F exige estudio de respuesta de sitio, sin dispensa. Pasa a adopción declarada `[A]` — ver §0.5 | Corrección posterior a la v7 |
| F_pga: valores por confirmar | **Confirmados** en Tabla 2.4.3.11.2.1.2-1: C=1.0, D=1.0, E=0.9 para PGA ≥ 0.50 | Cierre 3 |
| Catálogo comercial de diámetros bloquea M2, M7, M8 | **Desbloqueado.** Progresión normalizada 0.90 m + 0.15 m, con topes por norma de producto. Sin catálogo de proveedor | Cierre 7 |
| n de HDPE: vacío sin valor | **Rango declarado** (0.010–0.013) por analogía. **No un valor puntual** — ver §4.1.1. *Corregido en T-4 (`INF-3.2.1`): el rango ya no es una analogía; es `[C]` **0.009–0.015**, fila «Corrugated Polyethylene, Smooth» de la Table B.1 de HDS-5 (pág. B.6)* | Cierre 7, corregido |
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
| Clase de sitio sísmica (indeterminada; prohibido suponerla E o F, §0.5); Sección 12 (estructuras enterradas) | **AASHTO LRFD Bridge Design Specifications** | Norma matriz. `[C]` donde el Manual no tipifica; la clase de sitio **no** es uno de esos casos: es un dato de sitio `[S]` pendiente de ensayo, y la elección de filas de `F_pga` es `[A]` — ver §0.5 |
| Capacidad portante, FS de muros, licuefacción, c y φ, cimentación en talud | **RNE E.050** (RM 406-2018-VIVIENDA) | [N] |
| Perfil de suelo licuable (señal técnica) | **RNE E.030** (RM 183-2026-VIVIENDA) | [N] con reserva de ámbito (0.4) |
| Durabilidad del concreto y recubrimientos | **RNE E.060**, Cap. 4 y Art. 7.7 | [N] por excepción declarada (0.2) |
| Materiales, camas, rellenos, ejecución, partidas | **EG-2013, Sección 500** (RD 22-2013-MTC/14) | [N] |
| Diámetros normalizados y clases de tubería | **ASTM C76 / AASHTO M170** (concreto), **AASHTO M36 / ASTM A760** (TMC), **AASHTO M294 / ASTM F2306** (HDPE) | [C] normas de producto |
| Control de entrada y salida, HW/D | **HDS-5 (FHWA), 3ª edición, abril 2012** | [C] |
| Velocidades máximas en materiales flexibles | **WSDOT Hydraulics Manual M 23-03.12, Tabla 8-4 «Pipe Abrasion Levels»** (fuente técnica; NO está en `normas/` de este repositorio — *desde T-0, 2026-11-11, sí está en el repositorio de normas y en el registro como fuente presente `WSDOT_HM`, con la Tabla 8-4 en las págs. impresas 8-27 y 8-28; la cita con su frase la transcribe T-4*) | [C] — 4.572 m/s (15 ft/s) para TMC y HDPE, `'v_max_tmc'` / `'v_max_hdpe'`. *Corregido desde* «PPI / FHWA — valores por extraer» (`R48-030`, `MAT-O14`): la fuente que cerró el criterio es WSDOT, no PPI/FHWA, y el valor está extraído |

### 0.2 Regla de consistencia carga–resistencia — RESUELTA

El Manual de Puentes establece que las combinaciones se rigen por **AASHTO LRFD Sección 3.4.1** y el diseño del concreto por **AASHTO LRFD Sección 5** (num. 2.4.5.3 y Sección 2.9, págs. 140-143 y 337).

**Vía 1 adoptada: AASHTO LRFD de extremo a extremo.** E.060 no gobierna el diseño estructural.

**Excepción declarada — durabilidad.** E.060 Cap. 4 y Art. 7.7 sí aplican, por ser especificación de **materiales**, no de la relación carga–resistencia, y por estar calibrados con cementos peruanos (Tipo V, nomenclatura NTP). Regla de conflicto: rige el recubrimiento **mayor** entre AASHTO y E.060. Única mezcla admitida; se escribe expresamente en la memoria.

### 0.3 Vacíos normativos y su estado

| Vacío | Estado en v7 |
|---|---|
| Control de entrada / salida | El Manual MTC no lo desarrolla. HDS-5 3ª ed. (2012) aplicado **por encima** del mínimo normativo `[C]`. **Aporte metodológico** |
| Relación HW/D | No existe en el Manual MTC. **`[A]` 1.2–1.5** (corregido desde `[C]`: el rango 1.0–1.5 **no lo prescribe el HDS-5**, lo describe — ver V4b en Fase 5. Ref. `NOR-HDS-02`, `MAT-D2`). Cableado en `M5.v4b_relacion_hw_d` desde S14. El control real del embalse sigue siendo V5: V4b es un tope de práctica y cumplirlo no dice nada sobre el remanso dentro del derecho de vía |
| Velocidad máxima en TMC y HDPE | Tabla Nº 10 no los cubre. **`[C]` 4.572 m/s** (15 ft/s, conversión exacta) para los dos, de la Tabla 8-4 del WSDOT Hydraulics Manual M 23-03.12, adoptado como techo conservador porque el catálogo de M2 no modela protección por calibre ni revestimiento (`'v_max_tmc'`, `'v_max_hdpe'`). *Corregido desde* «Fuentes identificadas (PPI, FHWA); valores numéricos aún por extraer» (`R48-030`, `MAT-O14`). ***Corregido en T-4 (`INF-3.2.4`):** los dos valen 4.572 m/s y **no son la misma cosa**. El del **HDPE** sigue `[C]`: la fuente **prohíbe** el termoplástico en abrasión severa (§8-3.3, pág. 8-13) y la Tabla 8-4 pone ese nivel por encima de 15 ft/s. El del **TMC** pasa a `[A]` con ventana (3.048, 4.572) m/s: para el metal la tabla no prohíbe nada, pide más calibre o solera de concreto, de modo que «techo conservador de la Tabla 8-4» no era lo que la fuente dice — ver la nota de §3.4* |
| n de Manning para HDPE | Tabla Nº 09 no lo lista. **Rango 0.010–0.013 aplicado por analogía al concreto** `[N→]` (corregido desde `[A]`: lo exige la **regla de coherencia** de §0.1 — un valor justificado invocando una fila de una tabla normativa no puede ser `[A]` —, y es el mismo caso que `resguardo_HW_subrasante` y `h_relleno_min_concreto_tmc`. Ref. SIS-D-11). ***Corregido en T-4 (`INF-3.2.1`):** hay fuente técnica que da el n del polietileno corrugado de interior liso —HDS-5 Table B.1, 0.009–0.015—, de modo que la analogía se retira y el criterio es `[C]`, con el rango de la fila* |
| Flotación de conductos | El Manual de Puentes define subpresión (2.4.3.8.2, pág. 113) pero no incorpora AASHTO LRFD Sec. 12. Definición `[N]`; la verificación se plantea como **equilibrio de factores de carga LRFD** (§Fase 5, V7), con los γ de las **Tablas 2.4.5.3.1-1 y 2.4.5.3.1-2 del propio Manual** (pág. impresa 143; son las 3.4.1-1/-2 de AASHTO, transcritas) `[N]`, y `factores_carga_aashto` `[A]` limitado a **qué fila** de γp describe a cada estructura. **Corrección de esta tabla** (`NOR-PUE-04`): decía «los γ … vía `factores_carga_aashto` `[A]`», y llamaba adoptado a lo que la norma peruana escribe. El Manual sí transcribe las dos tablas, en la misma página que este documento ya citaba. **Ya no un FS global:** un FS es lenguaje de tensión admisible y §0.2 adopta LRFD de extremo a extremo |
| Clase de sitio | **Cerrado en contra de lo que decía la v7, dos veces.** AASHTO no concede dispensa alguna para la Clase de Sitio F: exige estudio de respuesta de sitio específico. Y el expediente ya no se atribuye esa clase — suponerla E o F está vedado sin dato geotécnico —: la clase es `[S]` sin valor y leer los factores tabulados como envolvente C/D/E es adopción `[A]` del proyectista (`F_pga`) — §0.5 |

### 0.4 Marco sísmico — CERRADO

**Aceleración en roca.** Mapa **"Isoaceleraciones Espectrales Suelo Tipo B, AASHTO 2014 (Roca), periodo estructural 0.0 seg (PGA)"**, Manual de Puentes, Apéndice A3, Tr = 1000 años. Lectura para La Unión (Piura): **PGA = 0.50 g** `[N]`.

Se descartan expresamente los mapas de S_s (T = 0.2 s) y S₁ (T = 1.0 s), que corresponden a aceleraciones espectrales y no a la aceleración pico del terreno.

No se usa el Z = 0.45 de E.030 para las fuerzas sobre el muro, y el argumento **de ámbito va primero** — pero no es el que parece. El **Art. 4 «Ámbito de aplicación»** (pág. impresa 7) aplica la norma «a) al diseño de **edificaciones** nuevas. b) al reforzamiento de **edificaciones** existentes…», y un cabezal de alcantarilla no es una edificación: cierto, pero insuficiente. **E.030 no guarda silencio sobre lo que no es edificación.** Su **Art. 7.3** (pág. impresa 8) los nombra y se los **atrae**:

> «Mientras no se cuente con normas nacionales específicas para estructuras tales como reservorios, tanques, silos, **puentes**, torres de transmisión, muelles, **estructuras hidráulicas**, túneles y todas aquellas cuyo comportamiento sísmico difiera del de las edificaciones se deben utilizar los valores *Z* y *S* del Capítulo II de la presente Norma Técnica amplificados de acuerdo a la importancia de la estructura, debiendo ser sustentado por el proyectista tomando en cuenta estándares internacionales.»

Es decir: «no es una edificación» **no es lo que saca al cabezal de E.030 — es el disparador del artículo que lo mete**. Lo que lo saca es que la condición suspensiva **no se cumple**: el MTC *sí* cuenta con norma nacional específica, el Manual de Puentes, de modo que el mandato de usar *Z* y *S* nunca llega a activarse. Es un fundamento **positivo** y más fuerte que el silencio: la propia E.030 cede el paso ante la norma sectorial. El argumento por periodo de retorno es el tercero y el discutible (`NOR-E030-03`).

El periodo de retorno de referencia de Z **no lo escribe el Art. 11.1**: escribe «una probabilidad de 10 % de ser excedida en 50 años». Los 475 años son una derivación —Tr = −50/ln 0,90 = 474,6— y la cifra sólo aparece literal en el **Anexo III** de E.030 (pág. impresa 67), sobre estudios de microzonificación (`NOR-E030-01`).

> **Único resto pendiente:** registrar en la memoria las **coordenadas o la curva de isoaceleración** sobre la que se hizo la lectura. Las curvas varían dentro de un mismo departamento y el revisor puede querer reproducir la lectura. Es un dato de trazabilidad, no un cambio de valor.

**Factor de sitio.** Tabla 2.4.3.11.2.1.2-1 del Manual de Puentes, para PGA ≥ 0.50:

| Clase de sitio | F_pga | A_s resultante |
|---|---|---|
| C | 1.0 | 0.50 g |
| D | 1.0 | 0.50 g |
| E | 0.9 | 0.45 g |

Los valores de tabla son **[N]**. La **elección** de F_pga = 1.0 sin conocer la clase de sitio definitiva es **[A]**: conservadora o exacta frente a las tres clases plausibles, con incertidumbre acotada al 10 %.

**Alcance de "conservador":** lo es dentro del marco tabulado. El análisis de respuesta específica de sitio —el que la **Clase de Sitio F** exigiría, sin dispensa posible (§0.5)— podría arrojar valores mayores. Declararlo.

### 0.5 Clase de sitio sísmica — INDETERMINADA; las fuentes prohíben suponerla E o F

**Este expediente no se atribuye ninguna clase de sitio, y en particular deja de atribuirse la Clase de Sitio F.** No porque una fuente diga que el sitio no lo sea, sino por algo más fuerte: **las dos fuentes prohíben expresamente *suponer* la clase E o F sin dato geotécnico o determinación de la autoridad**, y este expediente no tiene ninguna de las dos — el SPT está pendiente (Tablero 3.6). AASHTO LRFD, articulado, al pie de la Tabla 3.10.3.1-1 (pág. impresa 3-102): «Site classes E or F should not be assumed unless the authority having jurisdiction determines that site classes E or F could be present at the site or in the event that site classes E or F are established by geotechnical data». El Manual de Puentes lo endurece (num. 2.4.3.11.2.1.1, pág. impresa 122): «Las clases de Sitio E o F no serán supuestas a no ser que la Entidaddetermine la clase de sitio E o F o estas sean establecidas por datos geotécnicos» *(«Entidaddetermine», sin espacio, es errata del impreso y se transcribe tal cual)*. La misma cláusula trae el deber positivo, que es el trabajo pendiente: «a site investigation shall be undertaken sufficient to determine the site class».

Los tres hechos que el expediente sí declara, cada uno con su cita y **sin traslado entre ellos**:

1. **E.030 clasifica el sitio como perfil S5** «Suelos excepcionales», por su primera viñeta («Suelos potencialmente licuables»): arenas saturadas con NF a 1.4 m en la llanura del Bajo Piura. Esa clasificación trae una prohibición condicionada de construir (Fase 0-bis) — y es un esquema **distinto** del de AASHTO: S0–S5 por descripción, no A–F por rigidez medida sobre los 100 ft superiores. Ninguna de las dos fuentes imprime una equivalencia «S5 = Clase F», y ambas coinciden en la consecuencia: ninguna tabula factor para su categoría excepcional (la Tabla Nº 4 de E.030 no tiene columna S5; la fila F son cinco asteriscos).
2. **La clase de sitio de AASHTO / Manual de Puentes está indeterminada**, y suponerla E o F está vedado (citas de arriba). La cierra la caracterización de los **100 ft (30.48 m) superiores** (Vs30 o N̄) — la profundidad que el Art. 3.10.3.1 escribe: «Sites shall be classified by their stiffness as determined by the shear wave velocity in the upper 100 ft». **No la cierra el SPT de 15 m** de E.050 Art. 38, que responde a otra pregunta (licuefacción) y se detiene a mitad de la columna que esta clase necesita.
3. **Mientras esté indeterminada, el factor de sitio se lee como envolvente de las filas C, D y E** (§0.4): la tabla es `[N]` y la elección de filas es `[A]` — el criterio `F_pga`, con su sensibilidad declarada. La fila F no está entre las leídas por dos razones que valen hoy: **no da factor** (cinco asteriscos y remisión a estudio) y **suponerla está vedado**. Si la campaña devolviera Clase F, no queda fila con factor: queda el estudio, y esta memoria no podría cerrarse sin él.

**La licuefacción entra por otra vía, no por la clase de sitio.** AASHTO la evalúa en su Sección 10 (Cimentaciones), Art. 10.5.4.2 «Liquefaction Design Requirements» (pág. impresa 10-34), disparada por *zona sísmica 3 o 4* más *napa freática en los 50 ft superiores* más *características del suelo*: ninguna de las tres condiciones es la clase de sitio, y «Site Class F» no aparece en ninguna página de la Sección 10. Y el propio 10.5.4.2 **espera** que a un sitio licuable le aplique un factor de sitio tabulado — manda analizar en configuración no licuada y licuada con «The design spectrum should be the same as that used in the nonliquefied configuration», acotado por «the site factors in Article 3.10.3.2» —, lo que es incompatible con que la licuefacción hiciera Clase F por sí sola: la fila F no tiene factor con que empezar. El reparto coherente es el que este expediente hace: clasificar por rigidez medida (pendiente) y evaluar la licuefacción aparte, con el SPT de la Fase 0-bis.

**Lo que sí cambió antes y se conserva anotado — la dispensa que no existe.** Las versiones previas de este apartado afirmaban que AASHTO LRFD, Art. 3.10.3.1, autoriza una dispensa por periodo fundamental corto (T ≤ 0.5 s) que permitiría clasificar el sitio como si los suelos no licuaran. **Esa regla no existe.** Se verificó contra la 9.ª edición (2020): no está en el Art. 3.10.3.1, ni en su comentario, ni en ninguna tabla o nota de clases de sitio. Para un sitio que clasifique F, el estudio de respuesta se exige con `shall` — y el anclaje correcto es el **Art. 3.10.2 «Seismic Hazard»** (pág. impresa 3-71), no la Nota 2 de las tablas de factores, que dice `should`. Esto no fue un vacío rellenado en silencio: fue una **autorización normativa atribuida a una norma que no la concede**, y es el error más grave que ha tenido este expediente. Un vacío se ve; una cita falsa se cree. Queda anotado aquí, y no borrado, para que nadie vuelva a cerrarlo por el mismo camino.

**Alcance de la adopción de `F_pga`, sin coartada.** Los factores tabulados permiten **dimensionar** el elemento estructural. **No constituyen una evaluación del riesgo de licuefacción**, que permanece como el condicionante técnico no resuelto del proyecto (Fase 0-bis), y los efectos de la licuefacción —asentamiento, desplazamiento lateral, pérdida de capacidad portante— quedan fuera del alcance del script y remitidos al estudio geotécnico del expediente. Un análisis de respuesta específica de sitio **puede arrojar valores mayores** que los tabulados: la adopción **no es conservadora por construcción**, y esa es exactamente la razón de que la elección de filas sea `[A]` y no `[N→]`.

**Lo que cierra este apartado — dos ensayos de profundidades distintas, pedirlos juntos:** (1) la caracterización de los 100 ft (30.48 m) superiores (Vs30 o N̄), con la que se lee la clase; y (2) solo si esa caracterización diera Clase F, el análisis de respuesta dinámica de sitio que el Art. 3.10.2 exige con `shall`.

> **Corregido (`DIS-HR-CLASE-DE-SITIO-F`, `DIS-HR-VIA-DE-LA-LICUEFACCION`, `DIS-HR-30M-VS-100FT`, I2; resolución vinculante del conflicto #8 en `docs/resolucion_clase_sitio.md`).** Este apartado se titulaba «Clase de sitio F — ADOPCIÓN DECLARADA, NO DISPENSA NORMATIVA» y abría con «El sitio clasifica como **Clase de Sitio F** por susceptibilidad a licuefacción […] Eso no ha cambiado». Tres defectos, cada uno con su cita en contra: (1) el salto «suelo licuable → Clase F» no lo escribe ninguno de los dos documentos que la cadena sísmica invoca — en las 1905 páginas de AASHTO, los conjuntos de páginas con `liquef` y con «Site Class F» son disjuntos — y las dos fuentes **prohíben suponer** la clase E o F sin dato geotécnico (`AASHTO_LRFD_9.3.10.3.1#EXCEPCIONES`, `MP.2.4.3.11.2.1.1#EXCEPCIONES`, verificadas); (2) la licuefacción se evalúa por el Art. 10.5.4.2, nunca por la clase de sitio (`AASHTO_LRFD_9.10.5.4.2`, `AASHTO_LRFD_9.10.5.4.2#ESPECTRO`); (3) el Art. 3.10.3.1 escribe «the upper 100 ft», no «30 m» (`AASHTO_LRFD_9.3.10.3.1`). El valor `clase_sitio = "F_con_factores_tabulados_por_adopcion"` que este apartado citaba ya no existe en el código: desde S14 `clase_sitio` es un dato de sitio **`[S]` sin valor**, pendiente de ensayo, y el `[A]` que sí existe es la elección de filas de `F_pga`. Nota de vocabulario (`NOR-VOC-04`): «Clase F» designa tres cosas sin relación en las normas de este expediente — la clase de sitio sísmica, la clase de resistencia del concreto (EG-2013 Tabla 503-07, la matriz del ciclópeo de §9.4) y una clase del acero ASTM A668 que el Manual tabula — y toda mención va calificada.

### 0.6 Demanda sísmica para la evaluación de licuefacción — CERRADO

**Adoptado: Tr = 1000 años** `[A]`, es decir a_max derivado del mismo PGA = 0.50 g usado para la estructura. Se descarta el sismo de 475 años de E.030.

**Fundamento:** al tratarse de infraestructura vial regida por el Manual de Puentes, se exige al suelo la misma demanda sísmica que a la estructura de concreto que soporta. Un terreno evaluado a 475 años bajo una estructura diseñada a 1000 años es una incoherencia de niveles de seguridad dentro del mismo expediente.

> **Parámetro adicional que esta decisión genera.** El procedimiento simplificado de evaluación de licuefacción no se alimenta solo de a_max: requiere también la **magnitud del sismo (M_w)** para el factor de escala de magnitud (MSF). El PGA del mapa no la entrega. Debe adoptarse y declararse una M_w —por desagregación del peligro sísmico o por adopción justificada del sismo de diseño de la zona de subducción del norte peruano— antes de que la evaluación sea ejecutable. **Nuevo criterio `[A]` en el tablero.**

### 0.7 Gobierno de criterios adoptados

**Regla arquitectónica:** todo parámetro que no sea una exigencia normativa verificada se declara **una sola vez**, en `criterios_adoptados.py`, y se propaga desde allí.

> **Corregido (`EXT-V-01`, EXT-10).** La regla es de **un solo punto de definición**, no de un solo archivo, y la frase de arriba se quedó corta dos veces. Primero, desde S14 los datos de sitio **[S]** de corredor —el PGA del mapa, la zona sísmica, el corredor mismo— viven en `datos_sitio.py` y no en `criterios_adoptados.py`, porque no se eligen: se leen (taxonomía [S] de `CLAUDE.md`). Segundo, la auditoría externa del 2026-09-19 (V-01) leyó esos [S] como «hardcoding indebido», y no lo son: el repositorio **es** el expediente de una obra y un [S] con trazabilidad en un archivo versionado es más revisable que un campo de formulario. Lo que faltaba era un **requisito de producto**: que el mismo despliegue calcule **otra obra** sin editar código. Desde EXT-10 un [S] de otra obra se declara **por sesión** —bloque `sitio` de la sesión JSON, formato 3, o `--datos-sitio sitio.json`— con **trazabilidad y fecha obligatorias**, por la misma guardia que el archivo (`datos_sitio.establecer_dato_dinamico`); la sesión aporta el **valor y su lectura**, la ficha (concepto, procedimiento, fuente, ámbito) sigue definida **una sola vez** en `datos_sitio.py`, y la memoria imprime de qué archivo salió cada [S] y advierte si el nombre del proyecto no coincide con `corredor_del_proyecto`. Un proyecto nuevo se crea cargando una sesión vacía, nunca vaciando `datos_sitio.py`. El defecto era de esta hoja: describía dos contenedores donde el código tiene tres, y ninguno para la obra que no es la del repositorio.

| Contenedor | Qué contiene |
|---|---|
| **Anexo B** | Solo constantes **[N]** con numeral verificado |
| **`criterios_adoptados.py`** | Todo **[N→]**, **[C]** y **[A]**, con valor, etiqueta, justificación, fuente, ensayo que lo sustituye, rango de sensibilidad y verificación pendiente |
| **`datos_sitio.py`** | Los **[S]** únicos para todo el corredor de la obra del repositorio, con procedimiento, fuente, trazabilidad, ámbito y nivel (EXT-10) |
| **Sesión JSON, bloque `sitio`** (formato 3, EXT-10) | Los **[S]** de OTRA obra, declarados por sesión con valor, trazabilidad y fecha; la memoria los imprime como «declarado (sesión)» con el valor del archivo al lado |

La inconsistencia Clase D/F que motivó la v5 no fue un error de cálculo: fue el mismo parámetro definido dos veces en dos lugares. Un único punto de definición hace esa contradicción estructuralmente imposible.

**Comportamiento exigido:** un criterio con valor `None` detiene el script con excepción, nunca sustituye por defecto. Cada invocación se registra para que M11 imprima solo los criterios usados. Los pendientes se imprimen en bloque aparte.

---

## Fase 0-bis — Licuefacción: el condicionante mayor del proyecto

**E.030 (RM 183-2026-VIVIENDA), Art. 14.6, Tabla Nº 2 — Perfil S5 "Suelos excepcionales".** La celda es una lista de diez viñetas; la primera nombra este suelo y el cierre trae la prohibición. Se transcriben esas dos partes, **con la elisión marcada**:

> Suelos potencialmente licuables. […] Estos casos no están cubiertos en la clasificación establecida en la Tabla Nº2 de la presente Norma Técnica. **Se prohíbe las construcciones apoyadas sobre estos perfiles, salvo que, se efectúe un estudio específico para el sitio, en el cual se debe considerar los mejoramientos en el estrato del perfil.**

> **Corregido (defectos de literalidad de `DIS-HR-CLASE-DE-SITIO-F`, I2; §3 de `docs/resolucion_clase_sitio.md`).** Este pasaje empalmaba la viñeta 1 y el cierre como texto contiguo, con ocho viñetas elididas y sin marca; escribía «en la clasificación de la Tabla Nº 2» donde la fuente imprime «en la clasificación establecida en la Tabla Nº2 de la presente Norma Técnica»; y «salvo que se efectúe» donde la fuente imprime «salvo que, se efectúe», con coma. El literal verificado es la cita `E030.T2#S5`; `constantes_normativas.E030_S5_TEXTO` ya lo transcribía exacto — el defecto era de esta hoja.

**E.050, Art. 38 — condiciones concurrentes:** suelo arenoso/limo arenoso no plástico o grava en esa matriz; sumergido bajo napa freática; historia sísmica que haga sospechar la posibilidad.

**E.050, Art. 38 — ensayo exigido:** **SPT (NTP 339.133), perforaciones ≥ 15 m, ensayos cada 1 m.** DPSH, CPT y Vs como preliminares o complementarios, con calibración previa contra SPT (salvo CPT y Vs, que pueden calcular directamente el potencial complementando al SPT).

**Demanda sísmica de evaluación:** a_max de Tr = 1000 años (§0.6), más M_w por declarar.

### Lo que significa

1. **El elemento en riesgo no es el cabezal: es el terraplén de 5 km.** El modo de falla es asentamiento y desplazamiento lateral del cuerpo del terraplén, con las alcantarillas como puntos de concentración de daño.
2. Sin ensayos no se cierra ninguna de las dos preguntas, **y son dos, de dos taxonomías que ninguna fuente empareja**: el SPT de 15 m evalúa la licuefacción (la que hace del sitio un perfil S5 de E.030); la clase de sitio de AASHTO se lee sobre los 100 ft (30.48 m) superiores, y suponerla E o F está vedado (§0.5). *(Esta línea decía «la condición S5 / Clase F»: la barra asimilaba las dos taxonomías — el defecto de fondo dicho en un signo de puntuación.)*
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

> **Corregido (`INF-3.1.5`, `INF-5.2.5`, T-0, 2026-11-11).** La fila «Caudal de diseño Q» da como origen «Tc.py + IDF con TR de Fase 2». **El programa no calcula el caudal y `legacy/Tc.py` no corre en este repositorio** (importa `matplotlib` en su nivel superior, que no está en `requirements.txt`; `CLAUDE.md`, sección GUI): `Q_m3s` entra **ya calculado** por la columna del CSV, y lo único que el programa comprueba de él es que sea positivo y finito. Desde T-0 el origen que esta hoja declara es otro: **el caudal lo calculará el módulo de hidrología `MH_hidrologia` que crea T-1** de la cadena T —tiempo de concentración (Manual, §3.9 y Tabla 05), intensidad desde la serie de la estación y la relación IDF (§3.7, §3.8.1), coeficiente C (Tabla 08) y método racional (§3.12.2), con el TR de la Fase 2—, **sin quitar la vía actual**: si `Q_m3s` viene lleno, gana, y la memoria lo imprime como caudal declarado por el estudio hidrológico. `legacy/Tc.py` queda como antecedente. **Mientras T-1 no exista**, el único origen real del caudal es el estudio hidrológico externo que llena la columna, y `M1_clasificacion.PERFILES[Familia.A].origen_del_caudal` sigue nombrando a `Tc.py`: lo cambia T-1 con su test. Las entradas de diseño y quién las aporta están en `docs/contrato_entradas.md`.

> **Hecho (`INF-3.1.2` a `INF-3.1.6`, `INF-5.2.5`, T-1, 2026-11-11).** `MH_hidrologia` existe (`src/modulos/MH_hidrologia.py`, Fase 1-bis) y `PERFILES[Familia.A].origen_del_caudal` lo nombra. El caudal de un punto de Familia A o B tiene tres orígenes, en este orden: (1) `Q_m3s` declarado en `--datos-externos`; (2) la columna `Q_m3s` llena, que la memoria imprime como «Q declarado por el estudio hidrológico»; (3) la columna **vacía** y la corrida trae `--cuencas` y `--estacion`: lo calcula el programa con el TR de la Fase 2 y deja nueve pasos de memoria con su cita (ocho hasta la auditoría de T-1, que sumó el 1b.3b). Sin ninguna de las tres, `DatoFaltanteError('Q_m3s')` como antes. **Cuatro precisiones contra la fuente primaria, que corrigen la nota de T-0 de arriba y el prompt de T-1:** *la Tabla Nº 05 no lista a Témez* —sus filas son Kirpich, California Culverts Practice, Izzard, FAA, onda cinemática y retardo SCS—; la fórmula de Témez es la **ecuación (30) del núm. 3.12.2.1** (pág. impresa 51), con L en km y Tc en horas; *el método racional vale para «A<10 Km2»*, desigualdad estricta (pág. impresa 49); *la Tabla Nº 08 no tiene fila de pavimento*; y *de las ocho distribuciones del núm. 3.7.1 el Manual sólo imprime el estimador de tres* (Normal, Log Normal de 2 parámetros y Gumbel), que son las que el programa ajusta. **Y cinco que dejó la auditoría de T-1:** *la Tabla Nº 05 describe, no prohíbe* —el «(3 a 10%)» de Kirpich y las «800 Ha» de la ecuación de retardo son la población de la que salió cada fórmula, y qué se hace fuera lo decide el criterio [A] `tc_fuera_de_la_poblacion_del_metodo` (no evaluar, valor de archivo, o evaluar con aviso), con el mismo trato para California, que la tabla llama «esencialmente» la de Kirpich—; *de la tabla se implementan cuatro filas*, las dos de cauce más la de la FAA (flujo superficial) y la de retardo SCS (con el número de curva como columna opcional), para que una cuenca plana y una cuneta tengan un tiempo de concentración evaluable; Izzard y onda cinemática llevan la intensidad dentro de la fórmula y quedan diferidas (ficha `T1-07`); *la fórmula de Témez trae consigo el coeficiente de uniformidad K* de la ecuación (31), y usarla con el racional simple es un **uso híbrido** que se declara: K lo decide el criterio [A] `coeficiente_uniformidad_temez` (ficha `T1-08` para el método completo); *el Manual no fija una duración mínima de lluvia* y la cubre una fuente técnica [C], WSDOT Hydraulics Manual núm. 2-6.3 (5 minutos), criterio `duracion_minima_lluvia_min`; y *el coeficiente de una superficie de la plataforma vial* sale de la Table 2-2 de la misma fuente [C], criterio `coeficiente_escorrentia_superficie_vial`, nunca de una fila de la Tabla Nº 08 puesta por omisión. La fila de arriba, «Tc.py + IDF con TR de Fase 2», **sigue mal** en la tabla y se deja con esta nota: léase «declarado en `Q_m3s`, o calculado por `MH_hidrologia`». La serie, las cuencas y los años FEN son entradas del proyecto (`docs/contrato_entradas.md` §2-bis).

### 1.2 Encabezado del CSV

```
id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,
cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,
cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,
NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal
```

> **Corregido (`INF-5.1.11`, T-0, 2026-11-11).** Este encabezado listaba **16** columnas y el programa carga **19**: las de `M0_carga.COLUMNAS`, que no es una lista escrita a mano sino los campos de `modelos.PuntoCritico` en su orden. Las tres que faltaban aquí se añadieron al final del tipo, cada una por una corrección ya cerrada, y la hoja no se enteró: **`NF_profundidad_m`** (profundidad del nivel freático en el cruce, dato de sitio `[S]` medido punto a punto; la lee V7), **`cota_fondo_entrada`** (el invert de entrada MEDIDO; vacía, rige el criterio `origen_cota_fondo_entrada`) y **`cota_coronacion_canal`** (la cota del labio del canal que compara `VC1` en la Familia C). Las tres admiten celda vacía; qué celdas pueden venir vacías, y en qué familia, lo fija `M0_carga.VACIOS_ADMITIDOS` y no esta hoja. Un test (`tests/test_t0_gobernanza.py`) compara este bloque con `M0_carga.COLUMNAS`, para que no vuelvan a separarse. El origen de cada columna —quién la mide y con qué— está en `docs/contrato_entradas.md`.

### 1.3 TW: se calcula, no se mide

1. Obtener Q de diseño del receptor (ANA / Junta de Usuarios) **[N]**
2. Manning en la sección del receptor con ese Q y su pendiente → tirante normal → cota de agua **[N]**
3. Sin caudal documentado: **dos escenarios acotados** (salida libre / receptor a sección llena), cumplir en ambos **[A]**

> **Los tres pasos piden un dato que esta hoja no lista en ninguna parte, y el
> defecto es de esta hoja** (`SIS-B-04`, cerrado en S20). El paso 2 dice «Manning
> **en la sección del receptor**» y el paso 3 dice «receptor **a sección
> llena**»: los dos necesitan la **geometría de esa sección** —ancho de solera,
> talud, pendiente longitudinal, n de Manning y **profundidad total del cauce**,
> esta última porque sin ella «a sección llena» no es un nivel—. Ni la Sec. 1.1
> ni el encabezado de la Sec. 1.2 la traen, y ningún numeral la fija: es la
> geometría de una obra de terceros, el dren de la Junta de Usuarios, que hay
> que ir a levantar.
>
> **Cómo lo resolvió el código, para que quien lea la hoja sin leer el código no
> se quede con un procedimiento que no arranca.** La sección entra por el
> criterio `seccion_receptor` **[A]**, con su ventana y su trazabilidad, y el
> procedimiento vive en `M3_hidraulica.tw_seccion_1_3`, que recorre **cuatro**
> vías en orden de precedencia —de lo más determinado a lo más supuesto—:
>
> 1. TW declarado por el proyectista (`--tw`).
> 2. Columna **`cota_TW`** del CSV. El Tablero 3.1 la rotula «Calculada (1.3)»:
>    es el paso 2 resuelto fuera, y lo que faltaba era la resta que la convierte
>    en tirante, `TW = cota_TW − cota_fondo_salida`.
> 3. Columna **`Q_receptor_m3s`** + `seccion_receptor`: los pasos 1 y 2 enteros.
> 4. Sin caudal documentado: el paso 3, los dos escenarios acotados.
>
> **Sobre «cumplir en ambos» del paso 3.** El diseño corre con el escenario
> **gobernante** —el TW mayor— y los dos se imprimen en la memoria. No es un
> atajo: `h_o = max(TW, (y_c + D)/2)` no decrece con TW, `HW` de salida crece con
> `h_o`, y el control que gobierna es el mayor de los dos HW; luego V4 y V4b,
> que son las únicas verificaciones que dependen del TW, tienen su peor caso en
> el TW mayor. Cumplir con el mayor implica cumplir con el otro, y la memoria
> publica los dos números para que se pueda comprobar en vez de creerlo.
>
> **Corregido (`EXT-M-01`, `PC-04`, EXT-0).** «V4 y V4b, que son las únicas
> verificaciones que dependen del TW» es **falso bajo TW ahogante**. Cuando el
> TW alcanza la clave del conducto (TW ≥ D), o la carga a la entrada supera D
> con la salida sumergida, el barril fluye **lleno** —en la salida y en el tramo
> aguas abajo del resalto cuando gobierna el control de entrada, HDS-5 3.1.3,
> pág. 3.2; en toda la longitud sólo bajo control de salida, flujo tipo 4—, y
> entonces el tirante y la velocidad con que se comparan **V1 y V2** ya no son
> los del flujo uniforme de
> Manning (§4.1): son los del **régimen del barril**, que depende del TW. El
> Manual MTC lo dice de las dos: «las alcantarillas no deben ser diseñadas para
> trabajar a sección llena» (num. 4.1.1.3.7 b), pág. impresa 79, PDF 82) y la
> velocidad dentro del conducto y a la salida hay que verificarla (num.
> 4.1.1.3.6, págs. impresas 76-77, PDF 79-80). El HDS-5 fija con qué área se
> mide la velocidad a la salida bajo control de salida: la del tirante crítico,
> la del TW, o la sección entera del barril cuando el TW supera su clave (num.
> 3.1.6, pág. impresa 3.18, PDF 100). Hasta esta corrección el código seguía a
> esta hoja: con TW = 1.2 m sobre un D = 0.90 m la memoria imprimía «manda TW:
> la salida está ahogada» y, en la misma página, V1 [OK] con y/D = 0.135 y V2
> evaluada con la velocidad uniforme, cuando a sección llena la velocidad es
> Q/A_llena = 0.0786 m/s < 0.25 m/s y el borde libre no existe. El caso inverso
> también existe: en pendiente suave con salida libre (y_n > y_c) la velocidad
> de salida a y_c supera a la uniforme (1.508 frente a 1.184 m/s en el caso
> medido), de modo que la protección de salida de la Fase 6 recibía una
> velocidad **menor** que la real. Lo que cambia: (1) el TW gobierna también
> V1, V2 y la velocidad que entra a la Fase 6; (2) el «cumplir en ambos» del
> paso 3 sigue valiendo tal cual para V4 y V4b, y para V1/V2 el escenario de TW
> mayor es el gobernante sólo si el barril llena en los dos — si llena en uno
> solo, se evalúan los dos. **Implementado en EXT-3 (2026-09-20)** salvo la
> frase anterior: `M4.resolver_control` emite el régimen del barril
> (`modelos.RegimenBarril`) y la velocidad de salida (`M4.velocidad_de_salida`),
> V1/V2 se evalúan por régimen en `M5` y la Fase 6 recibe
> `ResultadoHidraulico.V_salida`. **Lo que EXT-3 NO hizo, y queda declarado:**
> la corrida sigue evaluando V1/V2 con el escenario de TW **gobernante** (el
> mayor) y no los dos por separado. Bajo «cumplir en ambos» eso no cambia la
> aceptación —si el mayor llena, V1 no cumple y el D se rechaza igual; si
> ninguno llena, el mayor es el que puede caer bajo control de salida y dejar
> V1/V2 pendientes, que ya impide cerrar—, pero sí deja sin imprimir el segundo
> escenario. Ficha `EXT-3-02` en `docs/decisiones_diferidas.md`. Ver la nota
> de §4.1 y las filas V1/V2 de la Fase 5.
>
> **Discrepancia con la fuente primaria, verificada (EXT-3, auditoría
> adversarial).** «El barril fluye lleno» con TW ≥ D no vale a secas bajo
> **control de entrada**: HDS-5 3.1.3, pág. impresa 3.2 (PDF 84), «In Figure
> 3.1C, submergence of the outlet end of the culvert does not assure outlet
> control. In this case, the flow just downstream of the inlet is supercritical
> and a hydraulic jump forms in the culvert barrel» —y la Fig. 3.1D: la
> sumergencia de los dos extremos «does not assure full flow»—. Lo que va lleno
> es la salida y el tramo aguas abajo del resalto; el de aguas arriba sigue
> supercrítico. El código (`modelos.RegimenBarril`, `M4.regimen_del_barril`)
> conserva LLENO para V1 y V2 también bajo control de entrada porque es ese
> tramo el que no tiene borde libre y el que fija la velocidad mínima
> (Q/A_llena), y lo declara así en el punto de uso con la cita
> `HDS5_3ED.3.1.3#SUMERGENCIA`; la velocidad de salida bajo control de entrada
> sigue siendo la del tirante normal (mayor: conservadora para d50). La frase
> de arriba («fluye lleno») lleva el matiz desde esta misma sesión; hasta EXT-3
> se leía como flujo a presión en toda la longitud.

> **Corregido (`INF-3.2.8`, `INF-5.1.7`, T-2, 2026-11-11).** Tres cosas de
> las vías 3 y 4, y las tres son de entrada o de impresión: ningún número de
> la línea base se mueve.
>
> **(a) La sección del receptor puede venir MEDIDA, y entonces gana.** Hasta
> T-2 la sección entraba sólo por el criterio `seccion_receptor` **[A]**, de
> modo que el TW de las vías 3 y 4 salía siempre de una geometría adoptada
> aunque existiera el levantamiento. Entra ahora, opcional y sin valor por
> defecto, por la clave **`seccion_receptor_medida`** de `--datos-externos`
> (global o por punto): un objeto con los cinco campos de
> `servicio.CAMPOS_SECCION_RECEPTOR` —`b_m`, `z_HV`, `S`, `n`,
> `altura_total_m`—, los mismos del criterio. Si está, `M3.seccion_del_receptor`
> la usa y el criterio no se invoca; si falta un campo, sobra uno o alguno
> queda fuera de su dominio, la carga se detiene (`DatoInvalidoError`): no se
> completa con el del criterio.
>
> **(b) La memoria dice de dónde salió la sección, y avisa.** El paso 1.3 y el
> JSON por punto (`tw_seccion_receptor`) llevan el origen
> —«seccion medida (levantamiento del receptor)» o «seccion adoptada [A] por
> falta de levantamiento» (`modelos.SECCION_RECEPTOR_MEDIDA` /
> `SECCION_RECEPTOR_ADOPTADA`)— y, cuando es adoptada, un **aviso**
> (`TWDeterminado.avisos`, `InformePunto.avisos()`): bajo la vía 4 el TW que
> gobierna el diseño es la profundidad total de una sección que nadie midió.
> El aviso no cambia el veredicto de ninguna verificación.
>
> **(c) `Q_receptor_m3s = 0` es un receptor seco, no un dato inválido.** M0
> rechazaba el cero junto con los negativos; un dren que no lleva agua durante
> la avenida es un hecho del sitio. Con 0 la vía 3 entrega TW = 0 (salida
> libre) y lo dice; el negativo se sigue rechazando.

### 1.4 Densidad de investigación geotécnica

**Manual de Suelos, num. 4.2, Cuadro 4.1** (pág. impresa 28). Nivel **Perfil**: **si no existe información secundaria en el tramo**, número de calicatas del Cuadro 4.1 **espaciadas cada 4.0 km** — el orden de prelación que la fuente imprime es usar *primero* la información secundaria existente. Ese 4.0 km **no está en el Cuadro 4.1** sino en un párrafo del num. 4.2, pág. impresa 29; el mismo párrafo fija **2.0 km** para factibilidad y prefactibilidad, ése sí incondicional.

| Clase | IMDA (veh/día) | Calicatas | Profundidad |
|---|---|---|---|
| Autopistas | > 6000 | 2 carriles/sentido: 4 · 3 carriles/sentido: 4 · **4 carriles/sentido: 6** — × km × sentido | 1.50 m |
| Duales / multicarril | 4001–6000 | 2 carriles/sentido: 4 · 3 carriles/sentido: 4 · **4 carriles/sentido: 6** — × km × sentido | 1.50 m |
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

> **Corregido (`INF-3.1.4`, T-1, 2026-11-11).** El texto de arriba mezcla un **hecho** (qué años de El Niño contiene la serie) con una **decisión** (qué se hace con ellos), y el criterio `homogeneidad_serie_fen` heredaba la mezcla: su ventana eran dos frases y ningún módulo lo leía. Desde T-1 van separados y el criterio **tiene consumidor**. *El hecho* lo declara el archivo de la estación (`--estacion`), año por año, en su columna obligatoria `fen`. *La decisión* es el criterio, una categoría de tres valores: `serie_completa`, `serie_sin_fen` y `dos_poblaciones`; sigue **sin valor de archivo**, porque se decide con la serie delante. Qué hace el programa: si el caudal lo **calcula** (`Q_m3s` vacío con cuenca y estación) y el criterio no está declarado, el cálculo hidrológico del punto se **detiene** con `CriterioPendienteError`; si el caudal entra **declarado** por la columna, no se detiene nada —es responsabilidad del estudio hidrológico— y la memoria imprime **siempre** un aviso: el criterio rige sólo el caudal calculado, y al declarado el programa no le atribuye ningún tratamiento. **La regla de arriba sigue en pie y el programa la juzga** (la primera redacción de esta nota decía que no se imponía; la auditoría de T-1 la restauró, porque rebajar una regla de esta hoja no es decisión de una sesión). «Reportar el ajuste con y sin ellos» se cumple siempre que la serie trae años FEN: el paso 1b.1 imprime la lluvia de diseño de las dos series. «Adoptar el más conservador, declarar el criterio» lo juzga el paso **1b.3b**: `serie_sin_fen` se puede declarar —el criterio es del proyectista—, pero cuando da **menos** lluvia que la serie completa **el cálculo hidrológico del punto se detiene** (decisión del dueño de esta hoja, 2026-11-11, ficha `T1-09`): un punto no queda dimensionado sobre un caudal que incumple la exigencia del núm. 3.4 y la regla de arriba. Sale por la misma vía que un ajuste que no pasa K-S (`MetodoNoEvaluableError`), con las dos lluvias en el mensaje y el remedio: declarar `serie_completa`, o traer el caudal del estudio hidrológico por la columna `Q_m3s`. Si da igual o más que la completa, pasa, y el paso imprime las dos. Un caudal **declarado** por columna no cambia: avisa y no bloquea. Una serie sin ningún año FEN se avisa como limitación central. Y un tercer contraste que esta hoja no pedía y la auditoría sí: aun con la serie completa, la distribución que pasa K-S puede dejar la lluvia de diseño **por debajo** de un año ya registrado (medido en la serie de prueba: 99.8 mm para 71 años con 173.5 mm observados); el paso 1b.2 lo contrasta con la probabilidad observada de la ecuación (13) y lo avisa, con la advertencia del núm. 3.12.5 (pág. impresa 64) sobre Piura y Tumbes. `dos_poblaciones` se puede declarar y **no se evalúa**: ninguna fuente de `normas/` da el procedimiento (ficha `T1-02` de `docs/decisiones_diferidas.md`). La fuente normativa del mandato es el **núm. 3.4** del Manual de Hidrología (pág. impresa 22): la serie «deberá incluir» los años de El Niño y esa información «debe ser evaluada de tal manera que no se originen sobredimensionamientos»; el Manual no dice cómo. Este apartado deja de estar «abierto» en el programa; sigue abierto en el Tablero 3 mientras la serie de SENAMHI no llegue.

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

**B — Alcantarillas de alivio.** Q del drenaje longitudinal. TR 35 años. Espaciamiento por Fase 10. Terraplén <1.5 m sin bordillo (geomalla); >1.5 m con bordillo y bajantes a ambos lados, a un solo lado en curvas peraltadas. Aceptación: V1 + V2 + V4 + V5 + espaciamiento de la Fase 10 (ver la nota).

> **Corregido (`INF-5.1.11`, T-0, 2026-11-11).** Esta sección declaraba el conjunto de verificaciones de aceptación de la Familia A («V1 + V2 + V4 + V5») y, con otra redacción, el de la C («No puede alterar la rasante hidráulica ni el borde libre del canal», que el código lee como `VC1`), y **no decía nada de la B**. El código lo refleja tal cual: `M1_clasificacion.PERFILES[Familia.B].verificaciones_aceptacion` vale `None`, con el comentario «Sec. 2.3 no declara conjunto propio». **Desde T-0 la hoja lo declara**, y lo que declara no es una elección nueva sino lo que sus otros apartados ya dicen: (a) una alcantarilla de alivio es el mismo conducto de cruce que una de paso con otro origen de caudal, y la tabla de la Fase 5 no exime a ninguna familia —de ahí **V1 + V2 + V4 + V5**, las que esta sección nombra para la A—; (b) lo que la B tiene de propio es que su posición no la fija un cauce sino la cuneta que descarga, y eso es el **espaciamiento de la Fase 10**, que esta misma frase ya nombraba. **Lo que NO cambia**: el conjunto es la *huella* de lo que esta sección nombra, no un filtro —la Fase 5 sigue aplicándose entera, punto por punto, a las tres familias, y ningún módulo despacha sobre ese campo (`modelos.PerfilFamilia`, `SIS-B-13`)—. **Lo que queda por hacer en el código**: `verificaciones_aceptacion` de la B sigue en `None` porque la verificación de espaciamiento no tiene todavía código de verificación propio (lo que hoy devuelve `M10_espaciamiento.espaciamiento_alivio` cumple siempre, por construcción: `INF-5.1.12`); lo cablea **T-9**, que es el prompt que la convierte en una verificación real, y hasta entonces la discrepancia entre esta frase y el `None` del código queda **declarada aquí** y en la ficha `T0-03` de `docs/decisiones_diferidas.md`.

**C — Cruces de canales y drenes.** Q = caudal de diseño del canal (ANA / Junta). **No puede alterar la rasante hidráulica ni el borde libre del canal.** Requiere autorización de obras en fuente natural / faja marginal. Marco o multicelda. **Bloqueada por falta del dato de ANA** — ver Tablero 3.

---

## Fase 3 — Tipo, material y durabilidad

### 3.1 Reglas duras [N]

- Luz ≥ 6.0 m → fuera de alcance
- **Diámetro mínimo 0.90 m (36")** — num. 4.1.1.3.4 a), pág. 72
- Excepción de selva alta (TMC Ø48", cauces en V, pendientes 5–60 %) — num. 4.1.1.3.7 a), pág. 78: **no aplica en costa.** Programar la rama y declararla inactiva. *Nota (T-4, `INF-5.1.16`): la rama **no está programada** y no se programó en T-4 —ningún dato de entrada dice en qué región natural está la obra, y activarla por defecto sería inventarlo—. La constante `DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO` se conserva sin consumidor; qué haría falta para cablearla está en la ficha T4-06 de `docs/decisiones_diferidas.md`*
- Suelo de fundación deficiente → orientar a marco de concreto
- Con palizada: sección única mayor, no múltiple

### 3.2 Catálogo de diámetros normalizado — **nuevo en v7** [C]

**Decisión: no se emplean catálogos de proveedores ni marcas.** El diseño opera con una progresión normalizada que garantiza neutralidad comercial, exigible en proyectos públicos.

**Progresión:** desde **0.90 m** (mínimo normativo MTC) con incrementos de **0.15 m**.

$$D \in \{0.90,\ 1.05,\ 1.20,\ 1.35,\ 1.50,\ 1.65,\ 1.80,\ ...\}$$

**Por qué funciona.** Las normas de producto avanzan en pasos de 6 pulgadas (0.1524 m) por encima de los 24–36", y AASHTO M 294 lo hace en pasos de 150 mm por encima de 750 mm (300, 375, 450, 525, 600, 675, 750 y, desde ahí, 900, 1050, 1200, 1350 y 1500 — num. 7.2.1, leído de la traducción no oficial de `normas/`). La progresión de 0.15 m reproduce esas series con error despreciable.

> **Corregido (`DIS-HR-M294-PASO`, N2).** Esta frase decía «en pasos de 150 mm por encima de 600 mm», con lo que tras el 600 vendría el 750 y no existiría el 675. El num. 7.2.1 de M 294-11 (traducción no oficial, cita `AASHTO_M294_TRAD.7.2.1`, sin firma) lista el 675: de 300 a 750 el paso es de 75 mm y el de 150 mm empieza en 750. Inocuo para el cálculo —ningún tamaño bajo 0.90 m se recorre— y se corrige igual, porque lo que la hoja de ruta dice y la fuente desmiente se reporta contra la hoja de ruta.

**Nota de conservadurismo:** usar 0.90 m redondo en lugar del equivalente exacto de 36" (0.9144 m) subestima el área en ~3 %. El error va del lado de la seguridad y debe declararse.

**Topes superiores de diámetro — de CATÁLOGO `[A]`, obligatorios en el script:**

| Material | Qué tabula la norma de producto (leída del PDF) | Tope de catálogo adoptado |
|---|---|---|
| Concreto reforzado | AASHTO M 170M, Tablas 1 a 5: el conjunto cubre de 300 a 3600 mm, y su Sec. 7.2 «Modified and Special Designs» prevé diseños por encima de lo tabulado | ~2.70 m |
| TMC | ASTM A760, Tabla 1: diámetros nominales de 100 mm (4 in) a 3600 mm (144 in); los 2100 mm son una fila más de la serie, no un máximo | ~2.10 m |
| **HDPE** | AASHTO M 294-11, num. 1.1.1 y 7.2.1: tamaños nominales **de 300 a 1500 mm**, doce diámetros, y el 1500 es la última fila — leído de la **traducción no oficial** que hay en `normas/` (cita `AASHTO_M294_TRAD.7.2.1`, sin firma; el original en inglés sigue ausente) | **~1.50 m** (coincide con el techo de la serie) |

> **Corregido (`DIS-HR-D-MAX`, I2).** Esta tabla se titulaba «Topes superiores por norma de producto» y atribuía los tres topes a ASTM C76 / AASHTO M170, AASHTO M36 / ASTM A760 y AASHTO M294, con la nota «deben confirmarse contra el texto de cada norma de producto antes de citarlos». Se confirmaron **en contra** (verificación por imagen renderizada de los PDF de `normas/`, citas `ASTM_A760.T1` y `AASHTO_M170M.T1_T5#DIAMETROS` del registro): las dos atribuciones contrastables tabulan hasta 3 600 mm, de modo que 2.70 y 2.10 m **no son topes de esas normas** sino topes de **catálogo** — y rotulados como norma descartaban material con una cita que ninguna norma sostiene. Viven como adopción `[A]` en `criterios_adoptados.py` (`'D_max_catalogo'`), con advertencia obligatoria en la memoria; el del HDPE queda además sin contrastar porque M294 está ausente (deuda de gabinete — §15 del plan de correcciones).
>
> **Actualizado (N2).** El tope del HDPE se contrastó sobre la **traducción no oficial** de AASHTO M 294-11 que entró en `normas/` (el original sigue ausente), y el resultado es el contrario que en los otros dos: la serie de tamaños nominales **termina en 1500 mm** (num. 1.1.1 y 7.2.1; tabla de 7.2.2 transcrita como `AASHTO_M294_TRAD.T7.2.2`). No devuelve el tope a la norma: los tres siguen siendo de catálogo `[A]` porque la elección es la misma para los tres y V9 descarta por catálogo; lo que cambia es que la sensibilidad del HDPE declara ese techo como su extremo, y que la memoria ya no puede decir que no se contrastó. Una traducción sin firma no sostiene el rótulo «por norma de producto».
>
> **Corregido (`INF-3.3.1`, T-4, 2026-11-11).** La tabla de arriba y las dos notas anteriores describen el estado hasta T-4, en que los tres topes eran de catálogo `[A]` (`'D_max_catalogo'` = 2.70 / 2.10 / 1.50 m) y dos de ellos no tenían respaldo. **Desde T-4 el tope de diámetro es el menor de tres cosas, y el programa dice cuál gobernó:** (1) el mayor diámetro que la **norma de producto** cubre —`'D_max_norma_producto'` `[C]`: **2.70 m** concreto, que es el último con **diseño estándar** de AASHTO M 170M (Tablas 1 y 3, leídas por imagen): su serie sigue hasta 3600 mm, pero esas filas llevan rayas y remiten a la Sección 7.2, «special designs» cuya pared da el fabricante (núm. 7.2.1 y 7.2.2, pág. M 170M-13); **3.60 m** TMC (AASHTO M 36 Table 6); **1.50 m** HDPE (AASHTO M 294 núm. 7.2.2, traducción no oficial)—; (2) en **TMC**, el mayor diámetro en que la **corrugación adoptada** es estándar según la Table 6 de M 36 —**2.10 m** con la de 68 por 13 mm, criterio `'corrugacion_y_espesor_tmc'` `[A]`; con la de 75 por 25 mm, 3.60 m—; (3) la **disponibilidad de mercado**, `'D_max_catalogo'` `[A]`, que pasa a ser **opcional y sin valor**: el proyectista la declara si la conoce y **sólo puede bajar** el tope (un valor por encima de (1) o (2) se rechaza). Consecuencia: **ninguno de los tres topes se mueve** (2.70 / 2.10 / 1.50 m) y ahora tienen de dónde salir. *(Una primera versión de esta nota llevaba el concreto a 3.60 m; la auditoría de T-4 lo refutó contra la fuente: por encima de 2700 mm la norma no tabula pared.)* El tope de 2.10 m del TMC es el de la **corrugación**, no el de la plancha: con 2.01 mm de espesor el factor de flexibilidad de ASTM A796 núm. 10.3 deja de cumplirse desde ~1.39 m, y eso lo verifica la Fase 8. Ningún punto del expediente de referencia cambia de diámetro.
>
> **Requisito de programación (vigente).** Sin tope superior, la iteración puede converger a un "diámetro" que no existe como producto. El caso especialmente restrictivo es el **HDPE**: si un punto crítico exige más de ~1.50 m, queda descartado por catálogo antes que por hidráulica. El módulo debe devolver *"material descartado por diámetro requerido"*, no un número imposible — y el descarte se rotula como catálogo, nunca como norma.

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

| Material | Vacíos normativos | Tope de diámetro (catálogo `[A]`, §3.2) | Durabilidad |
|---|---|---|---|
| **Concreto reforzado** | **Ninguno.** n y velocidad máxima en Tablas Nº 09 y Nº 10; carta propia en HDS-5 | ~2.70 m | Tabla 4.4 fija cemento, a/c y f'c según ensayo |
| **TMC galvanizada** | **Uno:** velocidad máxima (`[C]` 4.572 m/s, WSDOT M 23-03.12 Tabla 8-4; *corregido desde* «PPI/FHWA, valor por extraer», `R48-030`) | ~2.10 m | Requiere pH y resistividad; en suelos salinos la galvanización cae fuertemente |
| **HDPE** | **Tres:** velocidad máxima, n de Manning y carta propia en HDS-5 | **~1.50 m** | Inmune a agresividad química. Condicionantes: rigidez, flotación, relleno mínimo 0.30 m |

> **Corregido (`INF-3.3.1`, `INF-3.3.4`, `INF-3.2.4`, `INF-3.2.1`, `INF-5.1.17`, `INF-5.1.9`, T-4, 2026-11-11).** La matriz de arriba era una tabla de argumentos; desde T-4 es un **filtro que el programa aplica** (`M2.matriz_durabilidad` → `M2.materiales_candidatos`), y cuatro de sus celdas cambian:
>
> - **Tope de diámetro:** 2.70 m concreto (último diseño estándar de M 170M), 2.10 m TMC (por la corrugación adoptada), 1.50 m HDPE — ver la nota de §3.2.
> - **Vacíos del TMC:** su velocidad máxima es `[A]` (4.572 m/s, ventana 3.048–4.572), no `[C]`. Y ya **no se descarta por falta de espesor**: lo que separa su diámetro hidráulico del exterior es la profundidad de la corrugación más el espesor de la plancha (13 mm + 2.01 mm con la adopción `'corrugacion_y_espesor_tmc'`), porque el diámetro nominal se mide en la cresta interior (AASHTO M 36 núm. 8.1.1).
> - **Vacíos del HDPE:** el n de Manning deja de serlo (`[C]`, HDS-5 Table B.1, 0.009–0.015); la velocidad máxima sigue `[C]`; la carta de HDS-5 sigue siendo el vacío que era. Su espesor sale del diámetro exterior máximo de la Table A12-11 de AASHTO LRFD, que termina en 48 in: **1350 y 1500 mm no tienen fila** y se detienen por falta de ese dato. «Relleno mínimo 0.30 m» (EG-2013 508.07) **participa y no gobierna**: la cobertura de AASHTO para el termoplástico es 0.61 m bajo pavimento y 0.3048 m sin él.
> - **Durabilidad — entradas.** Seis ensayos **opcionales y sin valor por defecto**, del EMS y del estudio de campo, que entran por `--datos-externos` (sección `globales` para el sitio, `puntos` para una calicata): `sulfatos_suelo_ppm`, `sulfatos_agua_ppm`, `cloruros_ppm`, `pH`, `resistividad_ohm_cm` y `abrasion` (uno de los cuatro niveles de la Tabla 8-4 de WSDOT: `no_abrasivo`, `poco_abrasivo`, `moderadamente_abrasivo`, `severamente_abrasivo`). **Sin ensayos la matriz no actúa** y la memoria imprime «durabilidad: sin ensayos, matriz no aplicada».
> - **Durabilidad — reglas, cada una con su fuente.** pH fuera de 5.0–8.5 o resistividad menor de 1000 ohm-cm → **TMC excluida** (`[C]`, WSDOT §8-5.1 y §8-5.2; `'durabilidad_tmc_umbrales'`). pH menor de 5.8 → la TMC sigue y **exige protección** (`[N]`, EG-2013 507.10, pág. 974: es el único umbral numérico de durabilidad de tubería que la norma peruana escribe). Abrasión severa → **HDPE excluido** (WSDOT §8-3.3); al metal y al concreto, aviso de la protección que la Tabla 8-4 pide. Sulfatos → al concreto se le **exige** el cemento, la a/c y el f'c de la Tabla 4.4 de E.060; nunca se excluye. Cloruros → para el **concreto**, aviso: E.060 4.4.2 define la exposición por el origen del cloruro y no por un umbral en ppm. «Inmune a agresividad química» del HDPE se lee así: ningún ensayo químico lo excluye.
> - **Durabilidad — suelo agresivo para el acero, por analogía (auditoría de T-4).** AASHTO LRFD define el suelo no agresivo para **acero galvanizado enterrado** (Art. 11.10.6.4.2a, pág. 11-89; 11.12.8, pág. 11-134): pH 5 a 10, resistividad ≥ 3000 ohm-cm, cloruros ≤ 100 ppm, sulfatos ≤ 200 ppm. Son criterios de refuerzos de muros y anclajes, no de alcantarillas: se aplican por analogía (`'suelo_agresivo_acero_lrfd'` `[C]`) y, con uno incumplido, la TMC recibe **aviso** —o queda **excluida** si el proyectista declara `'suelo_agresivo_lrfd_sobre_tmc'` `[A]` = `excluye`; el valor adoptado es `aviso`, porque la exclusión se reserva a la fuente que habla de tubería—. Con ese suelo agresivo, o con sulfatos sobre la exposición insignificante de E.060, la TMC lleva además la **exigencia de protección** de EG-2013 507.10 («o que los suelos circundantes presenten sustancias agresivas»: la norma no las cuantifica y esa lectura es del proyecto).
> - **Aviso fijo del Manual para el metal.** Sin ensayo que lo dispare, toda TMC candidata lleva el aviso del núm. 4.1.1.3.7 f) y g): zonas costeras, aguas salinas o ácidas, suelos alcalinos o con turba — el Manual no recomienda alcantarillas metálicas; verificar la condición del sitio.
> - **Suelo de fundación deficiente → marco (§3.1): aviso, no filtro.** Lo lee de la columna `sucs_fundacion`. El Manual no define «mala calidad»; qué grupos SUCS cuentan lo declara `'sucs_fundacion_deficiente'` `[A]`, por defecto `OL`, `OH`, `PT` (los suelos sobre los que el Art. 24 de la E.050 no deja cimentar y manda remover y reemplazar). Un suelo fuera del conjunto **no queda calificado como apto**: la línea remite al Art. 38 de la E.050 (licuación de suelos granulares bajo la napa), que el programa no evalúa.
>
> **El nivel de abrasión no se deduce de la velocidad** —la Tabla 8-4 lo define también por la carga de fondo, y su nota dice que no hace falta que concurran todas las características—: es un dato de campo. V3 sigue comparando la velocidad contra su techo y no sustituye la protección de la solera.

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

> **Corregido (`EXT-M-01`, `PC-24`, EXT-0).** Esta sección presentaba la
> ecuación de Manning como **la** que produce el tirante y la velocidad que V1 y
> V2 comparan, y eso sólo es cierto cuando el barril fluye **parcialmente lleno
> en régimen uniforme**: bajo control de entrada, o bajo control de salida con
> salida libre y barril que no llena. Con TW ahogante —o con carga a la entrada
> superior a D y salida sumergida— el barril va lleno: el tirante es D y la
> velocidad Q/A_llena. Bajo control de salida con salida libre la velocidad **a
> la salida** es la del tirante crítico (HDS-5 num. 3.1.6, pág. impresa 3.18,
> PDF 100). **El tirante y la velocidad que se comparan salen del régimen del
> barril, no del uniforme**; Manning sigue siendo la herramienta del régimen
> parcialmente lleno y del control de entrada. Bajo control de salida con el
> barril parcialmente lleno, el tirante y la velocidad dentro del conducto no
> se conocen sin el perfil de la lámina de agua (§4.3): ahí V1 y V2 quedaban
> **pendientes**, no aprobadas con el tirante normal, y no se inventa un
> criterio de llenado para cerrarlas. **Corregido en E-A (2026-09-21):** el
> perfil existe (`M4.perfil_lamina`, paso 4.3c/4.3d de la memoria) y V1 y V2
> se evalúan sobre él: V1 con el **tirante máximo** del barril (`y_max`, D si
> hay tramo lleno) y V2 con la **velocidad mínima**, Q/A(y_max), las dos con
> n_max —más tirante y menos velocidad, el lado conservador de las dos—. La
> consecuencia medida en el corredor de referencia: B-01 con el TW ampliado
> de 1.00 m **no cierra en ningún diámetro** —la curva S1 arranca en el TW y
> deja V_min entre 0.06 y 0.11 m/s < 0.25— y termina en «no factible» con el
> motivo de V2, donde antes salía «dimensionado» con V1/V2 diferidas.
>
> Y las dos verificaciones no son [N] de una pieza. **El deber de verificar es
> [N]**: el Manual manda «verificar que la velocidad mínima del flujo dentro
> del conducto no produzca sedimentación» (num. 4.1.1.3.6, el párrafo arranca
> en la pág. impresa 76 y la cifra está en la 77; PDF 79-80) y tomar en cuenta
> el borde libre (num. 4.1.1.3.7 b), pág. impresa 79, PDF 82). Pero **el valor
> aplicado como umbral duro es [A]**, porque las dos cifras llegan con «se
> recomienda»: «recomendándose que la velocidad mínima sea igual a 0.25 m/s»
> (pág. 77) y «Se recomienda que el diseño hidráulico considere como mínimo el
> 25 % de la altura, diámetro o flecha de la estructura» (pág. 79). Aplicar una
> recomendación como rechazo es una adopción del proyectista y, como tal,
> lleva sensibilidad. La tabla de la Fase 5 lo recoge fila por fila.
> Precedentes: `NOR-HID-10` y `NOR-MEM-01` ya habían medido que las dos frases
> son del mismo tipo y que el matiz «recomienda, no prohíbe» tenía que
> imprimirse; aquí el matiz llega a la etiqueta. El código (`M5`) todavía lo
> lleva como [N] en `constantes_normativas` (`Y_SOBRE_D_MAX`, `V_MIN`).
> **EXT-3 (2026-09-20) NO lo cambió**, y esta frase decía que lo cambiaría:
> el reetiquetado toca 56 usos en 13 archivos, la tabla de criterios, el
> nivel medido y los manifiestos, y no cabía en la sesión que movía el
> régimen. Queda para una sesión propia, **EXT-3c**, con ficha `EXT-3-01` en
> `docs/decisiones_diferidas.md`. Mientras no exista, **esta hoja está
> corregida en la etiqueta y el código no**: la memoria imprime el matiz
> («recomienda») pero el valor sigue rotulado [N]. Lo que EXT-3 sí cambió del
> régimen —el tirante y la velocidad que V1/V2 comparan— está en el código.
>
> **Corregido (`PC-24`, cierre C05, 2026-09-22).** El párrafo anterior ya no
> describe el código: la adopción vive en `criterios_adoptados.py` como dos
> criterios [A] de perfil con el valor recomendado por defecto,
> `'borde_libre_y_sobre_d_max'` (0.75) y `'velocidad_minima_autolimpieza_m_s'`
> (0.25 m/s), que sólo se pueden endurecer (M5 rechaza un y/D máximo mayor o
> un piso menor); las cifras siguen [N] en `constantes_normativas` porque las
> escribe el Manual, y V1/V2 declaran `criterio_aplicado`. La ficha
> `EXT-3-01` quedó cerrada (C05-01).

#### 4.1.1 Por qué el n de HDPE es un rango y no 0.012 — **corrección**

Adoptar un **valor puntual** de n = 0.012 para HDPE rompe la regla de los dos valores: con un solo número, la verificación de capacidad y la de velocidad usan la misma rugosidad y **una de las dos deja de ser conservadora**. Concretamente, con n = 0.012 la velocidad calculada resulta menor que con n = 0.010, lo que subestima el riesgo de erosión y el d₅₀ de la protección de salida.

Si la analogía al concreto es el fundamento, hay que tomar **el rango completo del concreto** (0.010–0.013), no su valor medio. Así el HDPE se somete a la misma arquitectura de doble n que el resto de materiales.

> **Corregido (`INF-3.2.1`, T-4, 2026-11-11).** La analogía dejó de ser el fundamento. La Table B.1 de HDS-5 (3.ª ed., pág. B.6) da el n del polietileno corrugado de interior liso: **0.009 a 0.015**. El criterio `'n_manning_hdpe'` es `[C]`, su valor se deriva de esa fila del registro y la regla de doble n se conserva: capacidad con 0.015, velocidad contra el techo con 0.009. El rango es más ancho que el del concreto en los dos sentidos. La fila «HDPE (interior liso)» de la tabla de arriba se lee con estos dos números.

**Condición de validez:** la analogía solo aplica a HDPE de **interior liso**. El HDPE de interior corrugado tiene n del orden de 0.018–0.025 y la analogía sería gruesamente insegura. Especificar el tipo de producto en la memoria.

### 4.2 Control de entrada — HDS-5 [C]

**Fuente a citar:** FHWA, *Hydraulic Design of Highway Culverts*, 3ª edición, abril 2012, Apéndice A, Tabla A.1, pág. A.8.

**Caudal adimensional:**

$$q^* = \frac{K_u\,Q}{A\,D^{0.5}}, \qquad K_u = 1.811 \ \text{(SI)}$$

**Régimen no sumergido (q\* ≤ 3.5), Forma 1 — ec. (A.1):**

$$\frac{HW_i}{D} = \frac{H_c}{D} + K\,(q^*)^{M} + K_s\,S$$

**Régimen no sumergido (q\* ≤ 3.5), Forma 2 — ec. (A.2):**

$$\frac{HW_i}{D} = K\,(q^*)^{M}$$

> **Corregido (`DIS-HR-FORMAS-HDS5`, D9).** Hasta esta corrección, esta sección escribía **una** sola ecuación de control de entrada no sumergido —la (A.1), rotulada «Forma 1»— y nunca decía que existiera otra: medido sobre el documento entero, «Forma» aparecía tres veces y las tres eran «Forma 1». El HDS-5 tiene **dos**, y lo dice en el num. A.2.1 (pág. impresa A.1 / PDF 190, verificado en D9 contra el PDF): «The unsubmerged equation has two forms. Form (1) is based on the specific head at critical depth, adjusted with correction factors. Form (2) is an exponential equation similar to a weir equation. Form (1) is preferable from a theoretical standpoint, but Form (2) is easier to apply and is the only documented form of equation for some of the inlet control equations.» La Forma 2 es la ec. (A.2), pág. impresa A.2 / PDF 191 (cita `HDS5_3ED.A.2`, verificada): `HW_i/D = K·(q*)^M` **y nada más** — **sin `H_c/D` y sin `K_s·S`**; el contraste está en la misma página, porque la ec. (A.3) sumergida sí lleva `+ Y + K_s·S`. **Cuál de las dos aplica no lo elige el proyectista: lo fija la carta.** La Tabla A.1 trae una columna **«Equation Form»** con valores 1 y 2, **fila por fila** (transcrita en el registro como la columna `equation_form` de `T_HDS5_A1`; sus 18 filas —las tres circulares desde C0, las quince del cajón desde C2— se leyeron contra la tabla del PDF 197 y se releyeron en I3 y en D9). Las tres configuraciones circulares que esta sección tabula abajo —filas de las Cartas 1 y 2— son **todas Forma 1**, y por eso la omisión no se notaba en las Familias A y B. Del cajón rectangular de concreto **sólo la Carta 8 es Forma 1**; las Cartas **9, 10, 11 y 12 son Forma 2**. Lo que el num. A.3 sí prohíbe (`HDS5_3ED.A.3#FORMAS`, pág. impresa A.2 / PDF 191: «coefficients for rectangular (box) shapes should not be used for nonrectangular (circular, arch, pipe-arch, etc.) shapes and vice-versa») es cruzar coeficientes entre **geometrías**, no entre formas: la misma geometría vive en las dos formas —«Rect. Box Concrete» es Forma 1 en la Carta 8 y Forma 2 en las Cartas 9 a 11— y la regla que separa las formas es la columna, no ese numeral. `K_s` sigue entrando bajo las dos formas por la rama **sumergida**, ec. (A.3), que es común a ambas. El código bifurca por forma desde C3 (`modelos.ConstantesHDS5.forma`, `M4._hw_sobre_D_no_sumergido`) y la memoria imprime qué forma usó y por qué (`F4.FORMA_HDS5`); lo que estaba mal era esta hoja, y la discrepancia que lo decía queda resuelta con esta nota.

**Régimen sumergido (q\* ≥ 4.0) — ec. (A.3), común a las dos formas:**

$$\frac{HW_i}{D} = c\,(q^*)^{2} + Y + K_s\,S$$

**Transición (3.5 < q\* < 4.0):** interpolar linealmente **entre el valor de la rama no sumergida en q\* = 3.5 y el de la sumergida en q\* = 4.0** (no entre las dos ramas evaluadas en el q\* real: dentro de la ventana ninguna de las dos vale).

> *Corregido (`DIS-HR-FORMAS-HDS5`, D9): esta línea decía «la forma no sumergida» y «las dos formas» para nombrar las dos **ramas** —no sumergida y sumergida—, que colisiona con el término «Equation Form» de la Tabla A.1 del HDS-5. En esta hoja «Forma» queda reservado a la Forma 1 / Forma 2 de la ecuación no sumergida, y las ramas se llaman ramas. Bajo Forma 2 el extremo inferior de la recta sale de la ec. (A.2), sin `K_s·S`, y el superior de la (A.3), con él.*

> **La recta NO es el método del HDS-5, y esta línea la presentaba como si lo fuera** (`MAT-O10`). El HDS-5 empalma las dos ramas con una **curva tangente** ajustada sobre sus datos de laboratorio, **de la que no publica ecuación cerrada**. Quien prescribe la recta es esta hoja de ruta, no la fuente. Es una **simplificación adoptada** `[C]`, declarada en `criterios_adoptados` como `metodo_transicion_hds5` e invocada solo al entrar en la rama, de modo que la memoria la declara únicamente si algún punto del corredor cae de verdad en la transición. El error está acotado —la recta coincide con cada rama en su borde de validez— y acotado no es lo mismo que normativo.

> **Corregido (`EXT-M-04`, `PC-19`, EXT-0).** «El valor de la rama no sumergida
> en q\* = 3.5» era ambiguo, y el código lo resolvió mal: evaluaba la ec. (A.1)
> en q\* = 3.5 **con el H_c del caudal real** —el del q\* que cae en la
> transición—, cuando la rama no sumergida en q\* = 3.5 es la del **caudal que
> corresponde a q\* = 3.5**, `Q_lo = 3.5·A_llena·√D / K_u`, y por tanto con el
> **H_c de ese caudal**, `H_c(Q_lo)`. Con el H_c del caudal real el extremo
> inferior de la recta se mueve con q\*, y lo que la memoria imprime como
> «recta» es una curva (incrementos de 20.8 a 5.6 mm por paso de q\* en el caso
> medido). El error es **conservador** (+1.9 % de HW en CP-5: 1.129037883
> frente a 1.107921425 m, la media exacta de los dos extremos; +38.4 mm en el
> marco) y sólo afecta a la **Forma 1**, porque la ec. (A.2) de la Forma 2 no
> lleva H_c. Un test fijaba el extremo móvil con `rel=1e-12`
> (`test_la_interpolacion_reproduce_la_recta_entre_los_dos_extremos`): un
> oráculo con la misma lectura que el código, no una aceptación. Se corrige en
> EXT-2; hasta entonces, **hoja corregida y código no**, del lado conservador.

**K_s** = −0.5 para embocaduras no en inglete; **+0.7** para inglete. *(No figura en la Tabla A.1: proviene de la formulación de las ecuaciones. No omitirlo.)*

> **El término K_s·S no tiene tope, y una carga negativa no existe** (`MAT-D10`). Con K_s = −0.5, una pendiente grande y un caudal chico llevan las dos ramas a devolver **HW_i/D negativo** —una lámina de agua por debajo del fondo del conducto—. El umbral del signo, **para la Forma 1**, es `S > 2·(H_c/D + K·(q*)^M)`: con D = 0.90 m, Q = 0.05 m³/s y la carta de concreto vale `S > 0.3770624`, y hasta la corrección el diseño se **aceptaba entero** con HW = −0.010 m, o sea con V4 y el tamizado de 7.A evaluados 0.18 m del lado no conservador.
>
> *Corregido (`DIS-HR-FORMAS-HDS5`, D9): esta nota decía «las dos formas» por las dos **ramas**, y el umbral que escribe vale sólo bajo la **Forma 1**, que es la única que lleva `K_s·S` en la rama no sumergida. Bajo Forma 2 ese término **no existe** en la ec. (A.2), de modo que la rama no sumergida no puede hacerse negativa por pendiente; `K_s` entra entonces sólo por la rama sumergida, ec. (A.3), común a las dos formas, y por el extremo superior de la recta de transición (cita `HDS5_3ED.A.2`).*
>
> `M4.control_entrada()` **rechaza** ese resultado con `DisenoNoFactibleError`. Es un rechazo, no un piso: adoptar una carga en su lugar —la lectura física sería HW ≈ H_c— exige un valor que **ni esta hoja ni el HDS-5 fijan**, y ponerlo aquí sería rellenar un vacío en silencio. Y no es `DatoInvalidoError`: una S de 0.40 m/m es del tipo correcto, cae dentro de `dominios.S_CAUCE_MAX` y no contradice a nadie —no hay dato que el revisor tenga que corregir—; lo que no cierra es el **método** sobre esa combinación de Q, D y S.
>
> *Corregido (`PF-1`, PC-03, 2026-09-21): el párrafo anterior describía la conducta del software hasta PF-1 y ya no es la que hay. El rechazo era **definitivo y mudo** —descartaba el material entero y el bloqueo viajaba sin criterio, invisible en el tablero de pendientes—, y la regla de la constitución para un vacío que ni esta hoja ni la fuente fijan no es descartar: es la entrada con valor vacío, etiqueta [A] y la excepción que detiene el cálculo hasta que el proyectista declare. Desde PF-1 ese vacío es el criterio [A] de perfil `hw_entrada_fuera_de_rango` (`M4._resolver_hw_fuera_de_rango`): sin declarar, `CriterioPendienteError` con el par (Q, S) y el S* de la carta; declarado «energia_critica», HW = H_c —la energía específica crítica que el paso 4.2.1 ya resolvió— con el piso impreso en la memoria junto al HW/D que la ecuación devolvió; declarado «descartar», la conducta que este párrafo describía. El piso **acota el signo y no impone H_c como mínimo**: por debajo de S* la ecuación sigue entregando su carga, aunque sea menor que H_c, y por eso la carga salta en S*; la ficha del criterio lo declara. Sigue sin ponerse un piso en el código: lo que cambia es que ahora hay un sitio donde declararlo. El resto de esta nota —el umbral, lo que cierra y lo que queda abierto— no cambia.*
>
> *Corregido (`INF-0.5`, T-2, 2026-11-11): el criterio `hw_entrada_fuera_de_rango` ya no está vacío en el archivo: vale **`energia_critica`**, con etiqueta **[A]** y «descartar» en su ventana. La cadena T pedía etiquetarlo [C] citando una «nota de Ks·S de la Tabla A.1»; **esa nota no existe** —verificado contra la página (Tabla A.1, PDF 197: su única nota es bibliográfica)— y la fuente **no prescribe piso alguno**, de modo que la etiqueta sigue siendo [A]. Lo que la fuente sí dice, y sostiene la elección: «Form (1) is based on the specific head at critical depth, adjusted with correction factors.» (A.2.1, pág. impresa A.1 / PDF 190, cita `HDS5_3ED.A.2.1#FORMA_1`) y «the slope effect is small» (A.3, pág. impresa A.2 / PDF 191, cita `HDS5_3ED.A.3#PENDIENTE_2`). H_c es la base de la que la ecuación parte y un número que el paso 4.2.1 ya tiene. **No es una cota conservadora de la carga**: omite el término K·(q*)^M y queda por debajo de lo que la misma ecuación da con S = 0; sólo acota frente a la carga nula o negativa que la ecuación entregaba. Y con la pendiente del conducto limitada a 0.10 por V10 es prácticamente inalcanzable: con el tubo de 0.90 m la ecuación sólo deja de entregar carga por debajo de 0.10 con caudales menores de 0.005 m³/s. Ninguna corrida de la línea base cae fuera de rango, así que ningún número se movió.*
>
> *Corregido (`INF-5.1.6`, T-2, 2026-11-11): **S = 0 se admite** en `M3.resolver_manning`, `M4.control_entrada`, `M4.control_salida` y `M4.perfil_lamina`; la guardia (forma MAT-D13, `not S >= 0`) rechaza sólo la pendiente negativa y el NaN. Fuente: HDS-5 num. 3.3.4 «Culverts with Horizontal or Adverse Slopes», pág. impresa 3.25 / PDF 107, citas `HDS5_3ED.3.3.4#HORIZONTAL`, `#KS` y `#H_SIN_AJUSTE`. Con S = 0: (1) Manning no tiene tirante normal y M3 lo dice con `modelos.SinTiranteNormal` —ni excepción ni `None`—; (2) el término `K_s·S` vale cero —el «+0.01» que el numeral manda sumar al HW/D del nomograma es 0.5 × 0.02, la corrección que el nomograma lleva restada por haberse trazado al 2 %; el código resuelve la ecuación con la S real y no suma nada—; (3) la pérdida H del control de salida es la misma y la caída S·L desaparece; (4) el perfil de la lámina se integra con el mismo paso directo y se rotula **H2** (`TipoDePerfil.H2`; la fuente nombra los perfiles horizontales en 3.5.1, pág. impresa 3.37 / PDF 119); (5) V1 y V2 se juzgan sobre el perfil, y V3 y el d50 sobre la velocidad de salida. **Lo que la fuente admite y el proyecto no:** el mismo numeral aplica sus procedimientos a la pendiente **adversa**, que describe como asentamiento de la entrada («Adverse slopes can occur when entrances settle more than outlet»); este proyecto no diseña con ella y S < 0 sigue siendo dato inválido. `S_cauce = 0` tampoco se admite en el CSV: quien quiera el barril horizontal lo declara por `S_conducto` (ficha `T2-01` de `docs/decisiones_diferidas.md`, que registra además la discontinuidad con la convención de PC-06 para S pequeña y positiva).*
>
> **Cuánto cierra este rechazo, con números.** Cierra el signo y poco más. Con `S = 0.37706` el diseño se sigue aceptando con HW = +10⁻⁶ m, y V4 y 7.A quedan evaluados **0.1695 m** del lado no conservador —el 94 % del error—: de los 0.1798 m que el hallazgo denuncia, el rechazo retira 0.0103, el **5.7 %**. En el corredor de este expediente (S_cauce = 0.006–0.008) no se dispara nunca: en D = 0.90 hace falta `S > 0.27` y además Q = 0.025 m³/s. Acotar el rango de validez **entero** de la corrección exige una pendiente máxima que ni esta hoja ni el manual escriben, y ponerla sería inventarla: **queda abierto**.

| Configuración | K | M | c | Y | K_s |
|---|---|---|---|---|---|
| Circular Concrete — Square edge w/headwall | 0.0098 | 2.00 | 0.0398 | 0.67 | −0.5 |
| Circular CMP — con cabezal | 0.0078 | 2.00 | 0.0379 | 0.69 | −0.5 |
| Circular CMP — mitered to slope | 0.0210 | 1.33 | 0.0463 | 0.75 | +0.7 |

> **Corregido (`DIS-HR-FORMAS-HDS5`, D9).** Esta tabla presentaba `K, M, c, Y` como si **una sola** ecuación las consumiera. **`K` y `M` están ajustadas cada una a SU forma**: son dos regresiones distintas sobre dos conjuntos de ensayos, y la Tabla A.1 lo hace visible en la columna «Equation Form» de cada fila (de las 18 filas transcritas en `T_HDS5_A1`, las doce de Forma 2 del cajón llevan M = 0.667 y las seis de Forma 1 traen M = 2.00, 1.33, 1.0 o 0.75; la Tabla A.1 entera, con sus 36 filas, trae más valores en cada forma). Las tres filas de arriba son Forma 1 y con ellas la (A.1) es la ecuación correcta. Quien implemente el cajón leyendo sólo esta hoja copiará la (A.1) y le cambiará las constantes por las de una carta de Forma 2, y el HW le saldrá **MAYOR que el real**: la (A.1) arrastra dos términos que la (A.2) no tiene, `H_c/D` y `K_s·S`, y el que domina es el primero, por dos órdenes de magnitud. Medido en la auditoría de I3 sobre el marco de la línea base de la Familia C (2.00 × 1.50 m, Q = 6 m³/s, S = 0.004, Carta 10 escala 1): **3.047 m frente a 1.592 m reales, +91 %** — sobrediseño y falsos no-factibles, con sus deltas de rasante inventados. Para que la dirección se invirtiera haría falta `S > 2·H_c/D`, fuera incluso de `dominios.S_CAUCE_MAX`. **Ojo con la dirección**: la fila D-9 de `docs/ruta_familia_c.md` decía desde C2 «el HW sale menor, lado no conservador», mirando el término `K_s·S` sin mirar el `H_c/D` que la copia arrastra; la auditoría adversarial de I3 lo refutó con ese número, y la dirección corregida vive en `DIS-HR-FORMAS-HDS5.efecto_si_se_sigue_la_otra` y en `F4.FORMA_HDS5`. El error no falla ruidosamente: el resultado es positivo y plausible, y ninguna guardia de signo lo ve.

> **Corregido (`INF-3.2.2`, T-2, 2026-11-11).** La cadena T pedía transcribir las filas de la Tabla A.1 «para aleros (cajón y tubo, socket/bevel)». Verificado contra la página (HDS-5 3.ª ed., Tabla A.1, PDF 197): **la tabla no tiene filas de tubo circular con aleros** —los aleros («wingwall flares») sólo existen en las cartas de cajón (8, 9, 11, 12, 13)—. Lo que se transcribió, fila a fila contra la página, son las ocho que faltaban de las cartas en uso: Carta 1 esc. 2 y 3 (concreto, espiga «groove end» con cabezal y saliente), Carta 2 esc. 3 (CMP saliente), Carta 3 esc. A y B (anillos biselados de 45° y 33.7°) y Carta 13 esc. 1 a 3 (cajón con bisel superior y aletas desplazadas de 45°, 33.7° y 18.4°). `T_HDS5_A1` tiene ahora 26 filas de las 36 de la tabla (las diez que quedan fuera son las de entradas mejoradas «tapered», que el proyecto no diseña); la Tabla C.2 (`T_HDS5_C2`, pág. impresa C.6 / PDF 216) ya estaba transcrita entera, con sus 22 filas. **La embocadura adoptada no cambia** —la línea de abajo sigue valiendo—: las filas nuevas son elegibles para quien declare otra, y ninguna corrida de la línea base las usa.

**Configuración adoptada por diseño:** tubo a ras del muro (*square edge w/headwall*), coherente con el detalle de cabezal de la Fase 9.

#### 4.2.1 Corrección a la v6 sobre la organización de la Tabla A.1

En la v6 escribí que la Tabla A.1 *"organiza sus entradas por geometría de embocadura, no por material"*. **Eso fue una sobreafirmación mía y conviene corregirla**, porque es citable y es falsa tal como estaba redactada.

La Tabla A.1 se organiza en **cartas por forma y material** (*Circular Concrete*, *Circular CMP*, etc.) y, **dentro de cada carta**, por configuración de borde. Prueba de ello es que la misma configuración *square edge w/headwall* tiene constantes distintas en concreto (K = 0.0098) y en metal corrugado (K = 0.0078).

**Lo que sigue siendo cierto, y es lo que sostiene la adopción para HDPE:** esas diferencias entre materiales responden al **perfil de la pared en la boca** —una pared corrugada contrae el flujo de entrada distinto a una pared lisa—, **no a la fricción del barril a lo largo del conducto**, que interviene únicamente en el control de salida.

**Justificación correcta para el HDPE:** se adopta la carta *Circular Concrete, square edge w/headwall* porque el HDPE de **interior liso** con extremo cortado a ras del muro presenta, en la boca, una pared lisa y un borde cuadrado — es decir, la misma condición de entrada que el concreto, y no la del metal corrugado. Etiqueta **[C]**.

**Requisito de programación:** la Forma 1 necesita **H_c** (H_c = y_c + V_c²/2g). El tirante crítico en sección circular no tiene solución cerrada: se resuelve

$$\frac{Q^{2}\,T}{g\,A^{3}} = 1$$

con un segundo Brent sobre θ. **M4 requiere dos solvers, no uno.**

> **Corregido (`DIS-HR-FORMAS-HDS5`, D9).** Este requisito traía sólo la mitad de la Forma 1. La otra mitad: **la Forma 2 NO usa `H_c` en control de entrada** — la ec. (A.2) no lo lleva (cita `HDS5_3ED.A.2`, pág. impresa A.2 / PDF 191). El tirante crítico se resuelve igual bajo las dos formas, pero cuando gobierna la Forma 2 lo necesita **únicamente `h_o` del control de salida** (§4.3, `h_o = max(TW, (y_c + D)/2)`), y sólo para eso. Un M4 que exigiera `H_c` para el control de entrada de una carta de Forma 2 estaría calculando un término que la ecuación no tiene; el que lo pusiera en la (A.2) reproduciría el error de dirección de la nota de §4.2.

### 4.3 Control de salida [C]

$$HW = H + h_o - S\,L$$

$$H = \left(1 + k_e + \frac{19.63\,n^{2}L}{R^{4/3}}\right)\frac{V^{2}}{2g} \qquad \text{(SI)}$$

$$h_o = \max\left(TW,\ \frac{y_c + D}{2}\right)$$

> **h_o tiene numeral, y tiene una condición de uso que esta hoja no recogía** (`NOR-HDS-05`). La fórmula está en **HDS-5 3.ª ed., num. 3.3.3 «Outlet Control», pág. impresa 3.24** (el manifiesto marcaba la fila «⚠ sin numeral»), y allí mismo viene acotada:
>
> «Approximate hydraulic gradeline ho = (dc + D)/2 **can only be used if the barrel flows full for most of its length. It should not be used if the inlet is not submerged.**» (viñeta de la lista «The manual method has the assumptions:») · «If outlet control governs and the headwater depth (referenced to the inlet invert) is **less than 1.2D**, it is possible that the barrel flows partly full though its entire length. In this case, **caution should be used** in applying the approximate method of setting the downstream elevation based on the greater of tailwater or (dc + D)/2. If a more accurate headwater is necessary, backwater calculations (Section 3.5) should be used to check the result from the approximate method. If the headwater depth falls below **0.75D**, the approximate method should not be used.» (párrafo de prosa que sigue a esa lista) — son **tres** condiciones, no dos.
>
> **Corregido (`EXT-M-02`, `PC-25`, EXT-0).** La segunda cita estaba **elidida
> sin marcar**: entre «…(dc + D)/2.» y «If the headwater depth falls below
> 0.75D…» la fuente escribe «If a more accurate headwater is necessary,
> backwater calculations (Section 3.5) should be used to check the result from
> the approximate method.» (pág. impresa 3.24, PDF 106, verificada). Es la
> oración que dice **qué hacer** en la banda de cautela, y la elisión se
> repetía en `constantes_normativas.H_O_CONDICION_TEXTO` (corregida en la misma
> sesión; el registro, `HDS5_3ED.3.3.3#HO_1_2D`, ya la traía entera).
>
> La forma con el **máximo** —que es la que implementa `M4.control_salida`— la 3.ª ed. no la numera: la escribe en prosa («the greater of tailwater or (dc + D)/2»). Impresa como igualdad está en la edición de 1985 que también vive en `normas/`: «ho = TW or (dc + D)/2 whichever is larger.»
>
> **De las tres condiciones, el proyecto EVALÚA dos y declara la tercera.** Las dos evaluables son los límites sobre HW/D, que son una comparación entre dos números que `control_salida()` ya tiene: cuando el control de salida **gobierna** un punto y su HW/D cae bajo 1.2 o bajo 0.75, la memoria **de ese punto** lo dice junto al HW (`ResultadoHidraulico.h_o_fuera_de_rango`), no como advertencia general. Un aviso que no señala el punto afectado es el «nadie se entera» que el hallazgo denuncia. Los dos números son `[N]`: los escribe la fuente (`H_O_HW_SOBRE_D_MIN`, `H_O_HW_SOBRE_D_CAUTELA`) — y el 0.75 **no es** el 0.75 del borde libre de V1: aquél es del Manual MTC sobre el *tirante*, éste del HDS-5 sobre la *carga a la entrada*.
>
> La tercera —que el barril fluya lleno en la mayor parte de su longitud— **no se evalúa**, y ahí sí: exige un perfil de la lámina de agua a lo largo del conducto que este script no calcula. El criterio `geometria_control_salida = "seccion_llena"` **presupone lo mismo** que habría que verificar, de modo que esa premisa entra dos veces por dos puertas y no se comprueba por ninguna. Queda declarada en su `verificacion_pendiente`. Lo que la cerraría es el **procedimiento de barril parcialmente lleno del Cap. III**.
>
> **Circularidad que conviene ver:** el HW con que se evalúan los dos límites lo produce la propia aproximación, de modo que un h_o sobreestimado puede hacer que el control de salida gobierne un punto donde no gobernaría. El aviso se emite igual; deshacerla exige el procedimiento completo.
>
> **Decisión sobre HW/D < 0.75 bajo control de salida (`EXT-M-02`, `PC-27`,
> EXT-0; reabre `NOR-HDS-05`).** Hasta aquí esta hoja decía «el aviso se emite
> igual», y el código acepta el punto como dimensionado con
> `h_o_fuera_de_rango=True` mientras el `PasoDeMemoria` del mismo punto imprime
> NO_CUMPLE: memoria y pipeline dicen cosas distintas, que es lo que `SIS-A-07`
> prohíbe. **No es un aviso.** Cuando el control de salida gobierna y HW/D cae
> bajo 0.75 el método aproximado **no está definido** para ese punto —«should
> not be used»— y el HW que se publica no es un resultado sino un número fuera
> del dominio del método. **Tampoco es una `Verificacion(cumple=False)`**: subir
> de diámetro sólo baja HW/D (medido 0.589 → 0.526), y convertirlo en
> incumplimiento haría recorrer el catálogo hasta `DisenoNoFactibleError` por
> una condición que ningún diámetro puede cumplir. **Es un «método no
> evaluable»**, y viaja por la vía `Bloqueo`: **diferible a nivel de perfil** —el
> punto sale como dimensionado con HW no evaluable y el motivo «método no
> evaluable (HDS-5 3.24, Sección 3.5)» impreso junto al HW— **y no diferible a
> nivel de expediente**, donde el punto no cierra hasta que exista el cálculo de
> remanso (Sección 3.5) que la propia fuente manda usar. En la banda
> 0.75 ≤ HW/D < 1.2 el método sí se usa, con cautela, y el remanso es la
> comprobación que la fuente pide «if a more accurate headwater is necessary»;
> a nivel de expediente lo es. **Implementado en EXT-3 (2026-09-20)**:
> `modelos.MetodoNoEvaluableError` (sexta de la taxonomía) viaja como
> `Bloqueo` con `TipoDeBloqueo.METODO_NO_EVALUABLE`; la compuerta es
> `cli._compuerta_metodo_h_o`, que lee el MISMO campo que juzga el paso F4.HO
> (`ResultadoHidraulico.h_o_fuera_de_rango`, ahora con veredicto DIFERIDO y
> no NO_CUMPLE), diferible sólo a nivel de perfil. El punto B-01 del corredor
> de referencia sale como dimensionado **con** el bloqueo diferido y el motivo
> impreso junto al HW. El perfil por paso directo, que deshace la
> circularidad, sigue siendo la sesión EXT-3b / E-A.

> **Hecho en E-A (2026-09-21; cierra `NOR-HDS-05` entera).** El perfil de la
> lámina de agua se calcula por **paso directo** desde la salida hacia la
> entrada (`M4.perfil_lamina`, pasos 4.3c y 4.3d de la memoria), tal como la
> pág. impresa 3.12 del HDS-5 (PDF 94) lo escribe: la frontera aguas abajo es
> «critical depth at the culvert outlet or … the tailwater depth, whichever
> is higher», acotada a D; donde la lámina está sobre la clave rige «a
> straight, full flow hydraulic grade line» con la pendiente de fricción de
> la **Ec. 3.7** (S_f = K_u·n²·V²/(R^{4/3}·2g), el mismo término de fricción
> de H); y en la entrada «the inlet losses and the velocity head are added
> to the elevation of the hydraulic grade line» (HW = y_entrada +
> (1 + k_e)·V²/2g). Se integra sobre el parámetro propio de la sección
> (regla vinculante #12 de la Familia C) y los perfiles se rotulan como en la
> Sección 3.5.1 (M1, M2, S1, uniforme, llena). **De las tres condiciones de
> uso de h_o se evalúan las tres**: los dos límites sobre HW/D en el paso 4.3
> y la primera —«flows full for most of its length»— **medida** en el 4.3c
> como fracción de longitud a sección llena, leyendo «most» como más de la
> mitad (`'fraccion_llena_mayor_parte'` [A], 0.5 con sensibilidad 0.5–0.9;
> la lectura, con lo que juega en contra, en `citas.INTERPRETACION_MAYOR_PARTE`).
> **Bajo HW/D < 0.75 la aproximación no se usa**: el HW del punto es el del
> remanso (pág. 3.12: «For lower headwaters, backwater calculations are
> required»), y si el remanso **no alcanza la entrada** —la S1 corta el
> tirante crítico antes, o tiene longitud cero en un barril supercrítico con
> TW ≤ y_c— el control de salida no impone carga y **gobierna la entrada**:
> es la circularidad deshecha (el caso (b) del dictamen, Q = 0.3, S = 0.005,
> TW = 0, es un barril supercrítico —y_n = 0.2965 < y_c = 0.3157— que la
> aproximación clasificaba como control de salida con HW/D = 0.589). El
> bloqueo «método no evaluable» deja de producirse y queda como guardia de un
> resultado sin perfil. En la banda 0.75 ≤ HW/D < 1.2 la aproximación sigue
> siendo el método y el remanso es la comprobación que la fuente pide
> («should be used to check the result»): **si la comprobación pide más
> carga, manda ella** (`PerfilLamina.comprobacion_manda`; medido en E-A, en
> 165 de 228 combinaciones de la banda el remanso supera a la aproximación,
> hasta +5 %), porque del lado de la inundación no se publica la carga menor
> teniendo la mayor. Por encima de 1.2 la aproximación, con el remanso
> impreso. Y la asíntota de la lámina es la de su propia ley de fricción
> —la Ec. 3.7 con 19.63, un 0.05 % por encima del y_n de Manning con k = 1—,
> impresa como y_n' junto a y_n en el paso 4.3c (ficha EA-07).
>
> **Discrepancia dentro de la fuente, declarada.** La viñeta de la pág. 3.24
> dice que la aproximación «can only be used if the barrel flows full for
> most of its length»; la prosa de la pág. 3.12 dice que da «adequate
> results» hasta HW = 0.75D aun con el barril «partly full over its entire
> length». Esta hoja aplica la regla **cuantificada** de la 3.12 y **mide** la
> de la 3.24: cuando la aproximación se usa (HW/D ≥ 0.75) y el barril no va
> lleno en la mayor parte, el paso 4.3c lo dice con **NO CUMPLE sobre esa
> condición**, con la cita de la 3.12 que ampara el HW y el remanso al lado;
> el punto **no se rechaza** por ello, porque lo que no se cumple es la
> condición ideal de un método cuya validez la propia fuente extiende, no una
> exigencia sobre el diseño. Los dorados del perfil son límites de la propia
> fórmula —flujo lleno de punta a punta y flujo uniforme— y el balance de
> energía estación a estación; ninguna corrida HY-8 se fabrica (conflicto
> #7). Lo que el perfil **no** hace queda en `docs/decisiones_diferidas.md`
> (Parte XXVIII): no sitúa el resalto por momentum, no calcula S2 desde la
> entrada y no cambia V3.

> **Nota de unidades.** **19.63** es el valor SI. El **29** de la literatura FHWA es del sistema inglés. Usar 29 en métrico no falla ruidosamente: devuelve números plausibles y equivocados. **Test unitario obligatorio.**
>
> **Corregido desde 19.62** (conflicto #6 del plan de correcciones; `MAT-D12`, `MAT-X5`, `MAT-O12`, `NOR-COH-01`, `SIS-A-20`). Esta hoja escribía 19.62 en sus **cuatro** menciones y el código sostenía 19.63 desde antes, declarando la discrepancia. Gana la fuente primaria, verificada contra el PDF: **HDS-5 3.ª ed. (2012), num. 3.1.4, ec. (3.4b), pág. impresa 3.10** — «KU = 29 in English Units (19.63 in SI)» —, repetido en la ec. (DG 3.1), pág. DG3.3. **Ojo con la otra copia de `normas/`:** `fhwa_culvert_hydraulics_hds5si.pdf` es la edición de **1985** y, pese al «si» del nombre, imprime sus ecs. (4b) y (5) con **29** y rótulos duales «ft (m)»; leerla literal «en SI» reproduce el error que esta nota advierte: **×1.477 sobre el término de fricción (+47.7 %)**, que en CP-8 sube H de 0.4977 a 0.5455 m (+9.6 %).
>
> Y el parecido con **2·g no es una coincidencia**: `K = 2g/φ²`, con φ = 1.486 en el sistema inglés y φ = 1 en SI. De ahí `2·32.2/1.486² = 29.16` y `2·9.81456 = 19.629`. Lo único que separa 19.63 de 19.62 es **cuál g**: HDS-5 trabaja con 32.2 ft/s² = 9.81456 m/s² y el proyecto usa `constantes_fisicas.G = 9.81`. Se conserva el 19.63 **transcrito de la fuente**, no el 2·G derivado; la diferencia afecta al término de fricción en un +0.05 %, frente al **×1.477 sobre el mismo término (+47.7 %)** del 29 imperial, que en CP-8 sube H de 0.4977 a 0.5455 m (+9.6 %) y es el error que esta nota existe para advertir.
>
> *Corregido (`EXT-G-03`, EXT-0): estas dos frases decían «+9.6 %» a secas y
> comparaban con él el +0.05 % del término, mezclando bases: el 9.6 % es sobre
> **H** en CP-8 y el 47.7 % sobre el **término de fricción**; `M4_control` y el
> registro citan el 47.7 %. Ahora las dos bases van juntas y la comparación es
> término contra término.*

> **k_e — vacío que pasó inadvertido hasta la implementación.** Ningún numeral del Manual MTC ni del Manual de Puentes fija el coeficiente de pérdida de entrada k_e. Para la embocadura *square edge with headwall* (adoptada en §9.1), se toma **k_e = 0.5** de las tablas de coeficiente de pérdida de entrada del HDS-5. Etiqueta **[C]**, declarado en `criterios_adoptados.py` como `ke_entrada`.

**Relevancia en este proyecto:** con descarga a drenes con nivel propio, el TW puede ahogar la alcantarilla. Se puede cumplir y/D ≤ 0.75 en el barril y aun así embalsar más de un metro sobre terreno agrícola.

---

## Fase 5 — Verificaciones

| # | Verificación | Criterio | Ancla |
|---|---|---|---|
| **V1** | Borde libre | Mínimo **25 % de altura, diámetro o flecha** → **y/D ≤ 0.75**, evaluado sobre el **tirante del régimen del barril**: a sección llena **no cumple**; bajo control de salida con barril parcialmente lleno, sobre el **tirante máximo del perfil de lámina** (E-A; §4.1, §4.3) | **[N] el deber de verificar**, 4.1.1.3.7 b), pág. impresa 79 · **[A] el 0.75 como umbral duro** («Se recomienda…»). *Corregido desde* «[N] 4.1.1.3.7 b), pág. 79» (`EXT-M-01`, `PC-24`, EXT-0; ver la nota de §4.1) |
| **V2** | Velocidad mínima | **V ≥ 0.25 m/s**, con la **velocidad del régimen del barril**: a sección llena Q/A_llena; bajo control de entrada, la del tirante normal (n_max); bajo control de salida con barril parcialmente lleno, la **velocidad mínima del perfil de lámina**, Q/A(y_max) (E-A) | **[N] el deber de verificar**, 4.1.1.3.6, págs. impresas **76-77** · **[A] el 0.25 m/s como umbral duro** («recomendándose…»). *Corregido desde* «[N] 4.1.1.3.6, pág. 75» (`EXT-M-01`, `PC-24`, `NOR-HID-09`, EXT-0): la cifra está en la 77 y el párrafo arranca en la 76; la 75 es la Tabla Nº 09 |
| **V2b** | Sedimentación / colmatación | **S_conducto ≥ S_cauce** (indicador del HDS-5, num. 5.3.3) + **acceso de mantenimiento en planos** | **[C]** + [A] — *corregido desde* «Material sólido de arrastre + acceso de mantenimiento en planos», que era `[N] + [A]`; ver la nota de abajo (`SIS-A-13`, `MAT-O15`) |
| **V3** | Velocidad máxima | **Solo techo admisible.** Concreto **V ≤ 6.0 m/s**; ladrillo con concreto **V ≤ 3.5**; mampostería de piedra **V ≤ 2.0**. El par de la Tabla Nº 10 es un rango de valores MÁXIMOS según calidad del revestimiento, **no** un piso y un techo: el extremo inferior es el máximo admisible del acabado más pobre, y V3 no lo exige como mínimo. El piso universal de autolimpieza es **V2** (0.25 m/s). **TMC y HDPE: `[C]` V ≤ 4.572 m/s** (15 ft/s, WSDOT Hydraulics Manual M 23-03.12, Tabla 8-4; `'v_max_tmc'`, `'v_max_hdpe'`). *Corregido desde* «PPI/FHWA, valor por extraer» (`R48-030`, `MAT-O14`). ***Corregido en T-4 (`INF-3.2.4`):** HDPE `[C]` (prohibición en WSDOT §8-3.3, umbral en la Tabla 8-4); TMC `[A]`, mismo valor, ventana (3.048, 4.572) m/s — la fuente no fija una velocidad máxima para el metal* | [N] Tabla Nº 10, num. 4.1.1.3.6, pág. 76 / [C] WSDOT M 23-03.12 §8-3.3 y Tabla 8-4 (HDPE) / [A] `'v_max_tmc'` (TMC) |
| **V4** | Carga a la entrada HW | **cota de entrada + HW ≤ cota de subrasante − resguardo(CBR)** — *corregido desde* «HW ≤ cota de subrasante − resguardo(CBR)», que comparaba una **carga** con una **cota** (`MAT-O5`); ver la nota de datum en 5.1 | **[N→]** ver 5.1 |
| **V4b** | Relación HW/D | 1.2 – 1.5 | **[A]** — *corregido desde `[C]`.* El HDS-5 **no fija** HW/D: su num. 2.2.5 d) «Agency Constraints», pág. impresa **2.10** (la v8 citaba la 2.14, que trata de espolones de escombros y seguridad vial) **describe** lo que imponen las agencias viales de EE. UU. — «The allowable HW/D ratio varies throughout the country, but commonly ranges from 1.0 to 1.5» — y en el Perú la agencia es el MTC, que no fija ninguno. Elegir 1.5, que es el extremo **menos restrictivo**, es adopción del proyectista. **Implementada** en `M5.v4b_relacion_hw_d` (S14), una vez cerrada la procedencia del umbral: el HW que se divide entre D es el del control **gobernante**, porque lo que la fuente acota es el embalse que la obra produce. Ref. `NOR-HDS-02`, `MAT-D2`, `SIS-A-02`, `SIS-B-02` |
| **V5** | Remanso aguas arriba | Embalse dentro del **derecho de vía**, sin afectación a terceros ni a faja marginal | **Tres etiquetas, no una** — *corregido desde* «[N] DG-2018 + Ley 29338» (`EXT-N-04`, EXT-0). (a) **El requisito jurídico es [N]**: el derecho de vía es bien de dominio público (DG-2018 num. 304.07.01) y su ancho mínimo lo fija la **Tabla 304.09** por clase de carretera (16 a 40 m), incrementado en 5.00 m «del borde más alejado de las obras de drenaje» (num. **304.07.02**, págs. impresas 198-199, PDF 199-200; verificado); la faja marginal, Ley 29338. (b) **El método hidráulico** con que se decide si el embalse cabe en esa faja es **[A]** (`remanso_derecho_via`): el 304.07 no enuncia condición hidráulica alguna, y el código ya lo lleva como [A] de expediente (`SIN_FUNDAMENTO` F5.V5) — la contradicción viva era esta hoja. (c) **El ancho del derecho de vía de ESTE corredor es un dato de sitio [S]** (`ancho_derecho_via_m`), que hoy no llega por ninguna vía y detiene V5. En la Familia C V5 no se difiere: se sustituye (`VC1-02`). La DG-2018 está en `normas/` desde el 2026-09-18 y entra al registro en EXT-6. **Corregido (`INF-0.5`, T-0, 2026-11-11), dos precisiones sobre (b) y (c):** *el método de remanso* sigue siendo el criterio `[A]` `remanso_derecho_via`, **sin valor** —esta hoja no adopta ninguno: ni el nivel horizontal a la cota del HW proyectado sobre el terreno, ni una curva de remanso aguas arriba—, y elegirlo es del proyectista; *el ancho* `ancho_derecho_via_m` se declara aquí como **dato externo del proyecto, por punto** (lo fija la resolución que aprueba el derecho de vía del tramo, sobre el piso de la Tabla 304.09; no lo mide el programa ni es igual en todo el corredor): debe entrar como las demás claves de `--datos-externos`, y **hoy no es una de ellas** (`servicio.CLAVES_EXTERNAS` no lo lista; V5 lo reclama con `DatoFaltanteError` una vez declarado el método). Ningún prompt de la cadena T implementa V5: queda **diferida con este texto**, y T-11 la lista entre lo que sigue requiriendo entrada del proyecto (`docs/contrato_entradas.md`) |
| **V6** | Material sólido de arrastre | Con palizada: sección única mayor | [N] |
| **V7** | Flotación del conducto | **γ_DC,min · DC + γ_EV,min · EV ≥ γ_WA · U.** Tubería vacía, NF en su cota más alta. Las cargas que estabilizan (peso propio DC y peso del relleno EV) se **minoran**; la subpresión, que desestabiliza (WA), se **mayora**. Con el mínimo de la fila que corresponde a un **conducto enterrado** en la Tabla 2.4.5.3.1-2 es la forma 0.90·(DC + EV) ≥ 1.00·U. **Corrección** (`MAT-D8`, `NOR-PUE-03`): esa tabla no tiene un γ_EV único, lo desglosa por **tipo de estructura** —«Estructura rígida enterrada» 1.30/0.90, «Alcantarillas termoplásticas» 1.30/0.90, flexibles «Entre otros» 1.95/0.90, y **«Muros y estribos de retención» 1.35/1.00**, que es la del cabezal de §Fase 9—. El 0.90 de V7 es el del conducto y no vale para el cabezal. **Corrige la redacción anterior**, ΣW ≥ FS · U, que era un factor de seguridad global de tensión admisible dentro de un marco LRFD (§0.2) | [N] subpresión 2.4.3.8.2 + [N] los γ (Manual de Puentes, Tablas 2.4.5.3.1-1/-2, pág. impresa 143) + [A] la fila de γp por estructura (`factores_carga_aashto`) |
| **V8** | Evento extremo (FEN) | A TR mayor: la vía **no colapsa** aunque desborde | [N] verificación, no diseño |
| **V9** | **Disponibilidad de diámetro** | D requerido ≤ tope de la norma de producto del material | **[C]** — nuevo en v7 |
| **V10** | **Pendiente del conducto** | **`pendiente_minima_conducto` ≤ S ≤ `pendiente_maxima_conducto`**, con la pendiente con que se dimensionó (`ResultadoHidraulico.S`) | **[N] el deber**, 4.1.1.3.3 «Pendiente longitudinal», pág. impresa 71 (sin cifra) · **[A] la banda**: 0.0 (HDS-5 3.3.4, barril horizontal) a 0.10 (HDS-5 5.4.4, pág. impresa 5.16) — nuevo en T-2 (`INF-5.1.6`, `INF-3.2.7`) |

> **Corregido (`INF-5.1.6`, `INF-3.2.7`, `INF-3.2.6`, `INF-0.5`, T-2, 2026-11-11).** Cuatro cosas de esta tabla.
>
> **V10 es nueva y no mueve ningún diseño.** El Manual exige cuidar la pendiente y no da número (num. 4.1.1.3.3, pág. impresa 71 / PDF 74, cita `MC_HHD.4.1.1.3.3`: «La pendiente longitudinal de la alcantarilla debe ser tal que no altere desmesuradamente los procesos geomorfológicos, como la erosión y sedimentación…»). La banda es adopción: el piso, **0.0**, es el barril horizontal que el HDS-5 admite (num. 3.3.4), con ventana hasta 0.005; el techo, **0.10**, es el límite hasta el que el HDS-5 dice que no hacen falta anclajes («Most culverts are constructed on slopes that are less than 10% and the effects of slope are neglected in hydraulic equations. For these culverts, no special structural measures are used.», num. 5.4.4, pág. impresa 5.16 / PDF 152, cita `HDS5_3ED.5.4.4#PENDIENTE_10`), con ventana desde 0.02, la pendiente con que se trazaron las cartas (A.3). V10 no depende del diámetro: si no cumple, el remedio es otra pendiente. Vive en `M5.v10_pendiente_conducto`, corre en los dos alcances y **no cambia V2b**, que sigue comparando S_conducto con S_cauce. La tabla la lista al final, pero **se evalúa detrás de V4b y antes de V5**: detrás de V5 y de V8, que a nivel de expediente se detienen por un criterio pendiente, no llegaba a evaluarse. En el corredor del repositorio (0.004 a 0.010) cumple siempre.
>
> **V1 distingue quién le quita el borde libre al barril** (`borde_libre_bajo_tw_ahogante` **[A]**, `no_cumple` / `aviso`). «A sección llena no cumple» sigue valiendo sin matiz cuando es el **caudal de diseño** el que llena o deja al barril sin borde libre (num. 4.1.1.3.7 b), pág. impresa 79). Cuando es el **nivel del receptor** —el TW por encima del llenado admisible (TW/D > 0.75 con el umbral por defecto) y fijando el tirante máximo dentro del barril, llegue o no a la clave— el numeral no distingue el caso y la lectura se declara: `no_cumple`, el valor del archivo, es la literal; `aviso` acepta el diámetro si con su propio caudal el barril conserva el borde libre, y lo imprime como indicador con el TW y su vía. La lectura es **una sola a lo largo del TW**: no cambia al cruzar TW = D (la primera redacción de T-2 sólo actuaba con el barril lleno, y bajo `aviso` más ahogamiento resultaba más permisivo; se corrigió antes de integrar). Con el barril horizontal no hay tirante normal con que separar los dos casos y V1 no cumple bajo las dos lecturas. **El valor del archivo es `no_cumple` por decisión del dueño del proyecto (2026-11-11)**: `aviso` cambia qué puntos se dimensionan en la corrida estrecha de la línea base (A-02 pasa a dimensionar con Ø 0.90 m, ahogado por un TW de 1.196 m que sale de la vía 4 con la sección adoptada) y queda como alternativa barrible (`--barrido borde_libre_bajo_tw_ahogante=no_cumple,aviso`; ficha `T2-02`).
>
> **V2b: el valor de archivo de `regimen_v2b` pasa a `indicador_con_aviso`**, que es aplicar la fuente como está escrita (ver la nota de §5.2). Un indicador que no detiene se dice fuera de su fila: sube a los avisos del punto (`InformePunto.avisos()`) y el RESUMEN de la corrida cuenta aparte las «Verificaciones con aviso», para que «Verificaciones incumplidas: 0» no lo calle. La etiqueta sigue siendo [A]: el HDS-5 define el indicador y no prescribe qué hacer con él.
>
> **V3 y V2 con barril horizontal** se juzgan con la velocidad del régimen del barril (perfil H2 y velocidad de salida), porque no hay tirante normal.

### 5.1 Resguardo de V4 — valor y advertencia

**Manual de Suelos, num. 4.5.4 y 9.1(3)** (págs. 42, 89-90):

| CBR | Calidad | Resguardo sobre la napa |
|---|---|---|
| ≥ 20 % | Excelente – muy buena | **0.60 m** |
| 6 – 20 % | Buena – regular | **0.80 m** |
| 3 – 6 % | Insuficiente | **1.00 m** |
| < 3 % | Inadecuada | **1.20 m** |

> **NOTA DE DATUM — los dos términos de V4 son NIVELES** (`MAT-O5`, `MAT-O6`). Esta hoja escribía V4 como «HW ≤ cota de subrasante − resguardo» y la segunda condición de 7.A como «HW + resguardo + e_paq», poniendo a **HW** —que es una **carga en metros sobre el fondo de la entrada** (§4.2/§4.3)— del mismo lado de la desigualdad que una **cota en msnm**. Leído literal no es conservador ni no conservador: es **dimensionalmente incoherente**, y se cumple siempre (0.5 ≤ 43.25). El código nunca lo escribió así —`M5.v4_carga_entrada` y `M7.tamizado_rasante` suman la cota de entrada de `M5.cota_entrada_supuesta`—, de modo que **el defecto era solo documental y está corregido en esta hoja**: V4 y la segunda condición de 7.A llevan ahora el sumando `cota de entrada` explícito.
>
> La forma nivel-contra-nivel es además la del numeral, verificada contra el PDF (Manual de Suelos, **num. 4.5.4, pág. impresa 42**): *«El nivel superior de la sub rasante debe quedar encima del nivel de la napa freática como mínimo a 0.60 m cuando se trate de una sub rasante excelente - muy buena (CBR ≥ 20 %); a 0.80 m … buena - regular (6% ≤ CBR < 20%); a 1.00 m … Insuficiente (3% ≤ CBR < 6%); y, a 1.20 m … inadecuada (CBR < 3%). En caso necesario, se colocarán subdrenes o capas anticontaminantes y/o drenantes o se elevará la rasante hasta el nivel necesario.»* Los dos términos que el Manual compara —«el nivel superior de la sub rasante» y «el nivel de la napa freática»— son del mismo tipo. Lo que el Manual **no** escribe es una ecuación de cotas ni un datum: enuncia una separación relativa, y de ahí no se sigue una forma «cota_A ≤ cota_B − separación» más que por lectura del proyecto.
>
> **Qué cota de entrada.** No es columna de §1.2: sale de la regla declarada en `origen_cota_fondo_entrada` **[A]** (ver §0.7, «Gobierno de criterios adoptados»). Mientras esa regla no sea la cota de invert medida por punto, las dos desigualdades quedan amarradas a un supuesto, no a un levantamiento.

> **ADVERTENCIA DE APLICACIÓN.** El numeral regula la separación frente a la **napa freática** (nivel permanente), **no** frente a un nivel transitorio de avenida. Aplicarlo al HW es una **extensión por analogía** y se declara como **[N→]**. Verificado contra el PDF: el Manual **no menciona HW ni carga hidráulica en ningún numeral** —«carga hidráulica» no aparece, y todas las ocurrencias de «HW» son parte de la sigla «FHWA»—, de modo que la analogía es del proyecto entera y no admite lectura [N].
>
> Redacción: *"Ante la ausencia de un criterio normativo peruano que relacione la carga hidráulica de entrada con el nivel de subrasante, se adopta por analogía el resguardo que el Manual de Suelos (num. 4.5.4) exige frente al nivel freático, por ser el único parámetro normativo nacional que protege la subrasante de la saturación."*

Si no se cumple: subdrenes, capas drenantes/anticontaminantes o **elevar la rasante** — lo que alimenta 7.A.

### 5.2 Por qué V2 nunca gobierna

Para D = 0.90 m, y/D = 0.75 y n = 0.013, alcanzar 0.25 m/s requiere **S ≈ 0.00006 (0.006 %)**, muy por debajo de cualquier pendiente constructiva. **El piso normativo se cumple siempre y no restringe el diseño.**

La norma no protege del riesgo real, que es la **colmatación** en una llanura de riego con alta carga de finos. Por eso V2b existe y el acceso de mantenimiento va en los planos.

> **Dos correcciones a la fila V2b, y las dos son de esta hoja** (`SIS-A-13`,
> `MAT-O15`; implementada en S20 como `M5.v2b_sedimentacion`).
>
> **1. La mitad [N] no era «material sólido de arrastre».** Ese es el asunto de
> **V6**, dos filas más abajo, y ninguna de las dos filas puede ser la otra: V6
> exige sección única frente a palizada y V2b trata de finos que se depositan.
> Atribuir a V2b la mitad normativa de V6 dejaba a V2b, en la práctica, sin
> ninguna: la fila entera quedaba en el aire y por eso **no existió en ninguna
> línea de código** hasta S20.
>
> **2. «La norma no protege del riesgo real» es cierto del Manual peruano y
> falso del cuerpo normativo que este proyecto ya aplica.** El **HDS-5 3.ª ed.
> (FHWA-HIF-12-026)** —el mismo del que salen el control de salida y `h_o`, y
> que vive en `normas/`— dedica su **num. 5.3.3 «Sedimentation», pág. impresa
> 5.11**, exactamente a esto, y lo dice en términos de dos números que este
> cálculo ya tiene:
>
> > «Therefore, barrel slope less than the natural channel and roughness greater
> > than the channel are key indicators of potential problems at culvert sites.»
>
> y da la contracara en la misma página: «Culverts which are located on and
> aligned with the natural channel generally do not have a sedimentation
> problem.» Por eso la mitad evaluable de V2b es **[C]** y no [N]: es un vacío
> del Manual peruano cubierto con fuente técnica reconocida, que es la
> definición de esa etiqueta.
>
> **De los dos indicadores se evalúa uno, y hay que decir cuál.** El de
> pendiente —`S_conducto ≥ S_cauce`— se evalúa: las dos pendientes están. El de
> rugosidad exige el **n de Manning del cauce natural**, que no es columna de la
> Sec. 1.2 ni lo fija esta hoja; queda declarado como pendiente y la memoria lo
> imprime en la propia fila. Es el dato que cerraría la fila entera.
>
> **El carácter de la fuente se conserva.** El HDS-5 escribe «are key
> indicators of potential problems», no un umbral: el proyecto lo endurece a
> umbral duro por decisión propia, igual que hace con las recomendaciones de V1
> y de V2, y lo declara en el bloque de umbrales de la memoria.
>
> *Corregido (`PF-4`, 2026-09-21): la fila de la tabla ya decía «indicador» donde
> la fuente dice «indicator» y no hay nada que corregir en ella; lo que estaba
> mal era el párrafo anterior, que describía la «decisión propia» como si
> estuviera declarada y no lo estaba: vivía cableada en `M5.v2b_sedimentacion`
> como «umbral duro, por decisión conservadora del proyecto», sin ficha, sin
> ventana ni procedencia, que es lo que la constitución prohíbe a un [A]. Y su
> consecuencia se midió en la corrida de perfil de la revisión de E-B: con la
> pendiente de sonda de C-01 (0.004 frente a 0.006 del cauce) el umbral duro
> descartó los tres marcos de la progresión, cumpliendo todo lo demás, cuando
> en un cruce de canal la pendiente del conducto la fija el canal. Verificado
> contra el PDF (pág. impresa 5.11 = PDF 147): el 5.3.3 nombra DOS «key
> indicators of potential problems at culvert sites», no escribe cifra alguna y
> no contiene «shall» ni «should» (`caracter` DEFINICION de
> `HDS5_3ED.5.3.3#INDICADORES`). Desde PF-4 el régimen es el criterio [A] de
> perfil `regimen_v2b`, con dos opciones cerradas: `umbral_duro` (la conducta
> de S20, valor del archivo: el indicador disparado deja `cumple = False` y la
> sección se descarta) e `indicador_con_aviso` (V2b se evalúa igual, la memoria
> imprime el texto literal de la fuente con el veredicto INDICADOR —un valor
> nuevo de `TipoDeVeredicto`, no una cuarta capa del estado de verificación,
> PC-27— y el diámetro no se descarta). El paso F5.V2b imprime siempre la
> elección con su fundamento (`F5.V2b.REGIMEN`, verbo DEFINE, el único que el
> carácter de la cita sostiene). Ningún número de la línea base se movió. El
> segundo indicador —el n de Manning del cauce natural— sigue pendiente bajo
> los dos regímenes, como dice el párrafo de arriba.*
>
> *Corregido (`INF-0.5`, `INF-3.2.9`, T-2, 2026-11-11): el valor de archivo de
> `regimen_v2b` pasa de `umbral_duro` a **`indicador_con_aviso`**, y
> `umbral_duro` queda en la ventana. Medido antes y después sobre las diez
> corridas de la línea base: no cambia ningún diámetro ni qué puntos se
> dimensionan (C-01, el único punto con S_conducto < S_cauce, se detiene antes
> en los criterios del cajón). La etiqueta **no** pasa a [C], como pedía la
> cadena T: la fuente define el indicador y no dice qué hacer con él. Lo que
> sostiene la elección es el final del numeral, ya en la pág. impresa 5.12
> (PDF 148, cita `HDS5_3ED.5.3.3#DEPRESION`): «Culverts built with an upstream
> depression possess a barrel slope which is less than that of the natural
> channel. Sedimentation is the likely result, especially during times of low
> flow. However, self-cleaning usually occurs during periods of high
> discharge.» **El numeral entero, leído en T-2:** presenta DOS indicadores
> —pendiente y rugosidad del conducto frente a las del cauce— y nombra además,
> sin cifra, la magnitud del caudal y el material del cauce, los cauces en
> agradación, los cambios de pendiente a la entrada, las instalaciones
> multibarril y las entradas deprimidas. **La aplicación evalúa uno**, la
> pendiente. El segundo exige el n de Manning del cauce natural, que no es
> columna del CSV ni dato externo y **no se suple con un valor por defecto**:
> queda diferido con símbolo (`CRITERIOS["regimen_v2b"].verificacion_pendiente`,
> ficha `T2-06` de `docs/decisiones_diferidas.md`).*
>
> *Corregido (`INF-0.5`, T-2): la mitad [N] de la fila es el num. 4.1.1.3.7 d)
> «Mantenimiento y limpieza» del Manual (pág. impresa 80 / PDF 83, cita
> `MC_HHD.4.1.1.3.7d`), que el paso de V2b imprime; el criterio
> `acceso_mantenimiento_v2b` sigue siendo [A] porque lo que adopta es el
> DISPOSITIVO, que el numeral no prescribe. Y si el acceso está PREVISTO en
> los planos de cada punto entra, opcional y sin valor por defecto, por la
> clave booleana `acceso_mantenimiento_previsto` de `--datos-externos`: con
> `false` la memoria y la CLI imprimen el aviso
> `modelos.AVISO_SIN_ACCESO_DE_MANTENIMIENTO`; sin el dato no se afirma nada.*
>
> **La mitad [A] dejó de ser un párrafo.** El acceso de mantenimiento entra por
> el criterio `acceso_mantenimiento_v2b`, que **detiene** la corrida mientras
> siga vacío. Antes era una constancia que la memoria imprimía y que nadie
> tenía que contestar; ahora es una pregunta que el expediente responde.

---

## Fase 6 — Protección de entrada y salida [N]

**Laushey** — num. 4.1.1.3.7 c), pág. 80:

$$d_{50} = \frac{V^{2}}{3.1\,g}$$

d₅₀ en m, V en m/s. **La constante 3.1 asume sistema métrico.**

> **Corregido (`NOR-HID-01`, `MAT-O7`).** Esta hoja escribía «g = 9.8 m/s²» bajo el encabezado del num. 4.1.1.3.7 c), presentando el número como si ese numeral lo imprimiera. **No lo imprime**: verificado contra el PDF, su lista de variables dice sólo «g : Aceleración de la gravedad (m/s2)», sin valor. El **valor 9.8 sí es el del Manual** y sigue vigente, pero lo escriben otros dos numerales — **3.12.5 «Otras Metodologías», pág. impresa 63**, y **4.1.1.5.4 b.2.4) «Método de Laursen», pág. impresa 111** —; el 9.81 no aparece ni una vez en sus 225 páginas. Se corrige la atribución, no el número. Es el mismo género de defecto que el «19.62 = 2g» que este documento ya purgó: una cita que suena razonable, que nadie comprueba porque el número es correcto, y que manda al revisor a una página donde no está lo que promete.

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

$$\text{cota rasante} \ \ge\ \max\begin{cases} \text{cota clave} + h_{rec} + e_{paq} \\ \text{cota entrada} + HW + \text{resguardo}(CBR) + e_{paq} \end{cases}$$

Correr el tamizado con el diámetro máximo supuesto **antes** de definir el perfil longitudinal.

> **El sumando `cota entrada` de la segunda condición es una corrección de esta hoja** (`MAT-O6`), no un cambio de criterio. La v8 escribía esa línea como «HW + resguardo + e_paq», mezclando la **carga** HW con las **cotas** de las otras dos —la misma incoherencia de V4, y por la misma razón: las dos condiciones son la misma desigualdad escrita al revés (ver la nota de datum de §5.1). Con el sumando explícito, la equivalencia con V4 es álgebra de una línea: `cota rasante ≥ cota entrada + HW + resguardo + e_paq` ⟺ `cota entrada + HW ≤ (cota rasante − e_paq) − resguardo` = `cota de subrasante − resguardo`, que es V4. El código ya la sumaba (`M7.tamizado_rasante`, término `entrada + HW + resguardo + e_paq`); lo que estaba mal era la hoja.
>
> La **primera** condición no necesitaba corrección: `cota clave`, `h_rec` y `e_paq` son una cota y dos espesores, y el resultado es una cota.

**Altura mínima de relleno sobre la clave:**

| Material | h_rec mínimo | Fuente |
|---|---|---|
| **HDPE/PAD** | **0.30 m** desde la clave hasta la subrasante | [N] EG-2013 508.07, pág. impresa 984 |
| Concreto y TMC | **Lo fija AASHTO LRFD**: Art. 12.6.6.3 «Minimum Cover» y su Tabla 12.6.6.3-1, que tabula la cobertura mínima por tipo de conducto («shall not be less than that specified in Table 12.6.6.3-1»). Transcrita íntegra en el registro; gobierna el criterio `'cobertura_minima_aashto'` | [C] AASHTO LRFD 12.6.6.3, pág. impresa 12-21 — AASHTO no es norma peruana: cubre el vacío que EG-2013 y el Manual dejan, y el criterio que gobierna es `[C]` |

Nota constructiva [N] (EG-2013 508.08, pág. impresa 985): el equipo pesado no circula sobre el conducto antes de que el relleno alcance 0.30 m — exigencia de ejecución, distinta de la cobertura de diseño.

> **Corregido (`DIS-HR-H-RELLENO-MIN`, I2).** La fila de concreto y TMC decía «**No fijado.** Remite al Proyecto, AASHTO M-170M (clases I–V) o ASTM A-807 | [C] norma de producto». Las dos remisiones eran falsas — M 170M es especificación de fabricación y compra (su Nota 1 lo dice) y no da alturas de relleno; A-807 no es la norma que se le atribuía — y «no fijado» no era cierto: lo fija el Art. 12.6.6.3 de AASHTO LRFD (cita `AASHTO_LRFD_9.12.6.6.3#COBERTURA`, verificada), que es el cuerpo normativo que §0.2 adopta de extremo a extremo. Declarar un vacío sobre la fuente que sí trae el dato es el defecto que §0.5 llama el más grave. La página del 0.30 m del HDPE también se corrige aquí: es la impresa 984, no la 982 (`DIS-CN-EG-508-07`, resuelta).

### 7.B Verificación final por punto

- **Longitud** = ancho de plataforma + proyección de taludes, afectada por esviaje
- **Esviaje** siguiendo el alineamiento natural del cauce [N]
- **Pendiente de la alcantarilla:** la del cauce (V2 nunca la restringe). La restricción real es constructiva y de cota del receptor
- **Cotas de entrada y salida** amarradas al perfil del cauce y a la cota de fondo del receptor
- El chequeo devuelve *"no factible → subir rasante X cm"*, nunca un resultado silencioso

> **7.B corre con LA MISMA pendiente que la Fase 4, no con una suya** (`MAT-D9`). «La del cauce» es la regla y sigue siéndolo: es el valor por defecto, `S_cauce` de §1.2. Pero no todos los puntos la usan —la Familia B se dimensiona con el caudal del drenaje longitudinal y la C con el del canal (§2.3), y esos cruces declaran su propia pendiente por la vía de datos externos (`S_conducto`)—, y hasta esta corrección 7.B **no se enteraba**: el HW, las velocidades y el tirante salían de la pendiente declarada, mientras la caída `S·L` y la cota de salida se recalculaban con la del cauce. Dos pendientes en el mismo punto, ninguna marcada como distinta de la otra en el informe. La pendiente viaja ahora dentro del resultado hidráulico (`ResultadoHidraulico.S`) y `M7.compatibilidad_geometrica` la lee de ahí: **ya no es argumento suyo**, de modo que no puede volver a elegirse dos veces.

> **Corregido (`INF-3.2.7`, `INF-5.1.6`, `INF-5.1.18`, T-0, 2026-11-11).** Dos renglones de la lista de arriba dejan de ser prosa y **pasan a criterios declarables**, que crean T-2 y T-6 de la cadena T; aquí no se adelanta ningún valor. **(a) Pendiente del conducto.** «La del cauce (V2 nunca la restringe). La restricción real es constructiva» describía un límite sin nombrarlo. Pasan a ser dos criterios `[A]` de perfil con ventana, **`pendiente_minima_conducto`** y **`pendiente_maxima_conducto`**, con la verificación que los aplica (T-2), y M7 imprime cuál de los tres orígenes de la pendiente adoptada gobernó —la del cauce, la declarada (`S_conducto`) o la mínima/máxima— (T-6). Con ellos la pendiente **nula** deja de ser un dato inválido: el HDS-5 aplica sus procedimientos a barriles horizontales (num. 3.3.4 «Culverts with Horizontal or Adverse Slopes», pág. impresa 3.25 / PDF 107: «they can be reasonably applied to culverts with no slope (horizontal) or an adverse slope»; leído en T-0, sin cita en el registro todavía: la transcribe T-2). **(b) Entrega al receptor.** «Amarradas … a la cota de fondo del receptor» se verifica hoy como `cota_salida ≥ cota_fondo_receptor` (`M7`, G2), sin margen. Pasa a exigir un **desnivel mínimo de entrega**, el criterio `[A]` **`desnivel_minimo_entrega_m`** (T-6): `cota_salida ≥ cota_fondo_receptor + desnivel`. **(c)** y la cota de fondo de ENTRADA, que cuando la columna `cota_fondo_entrada` viene vacía se adopta igual a la del terreno de la plataforma (`origen_cota_fondo_entrada`), pasa a imprimirse como adoptada y a marcar el delta de rasante de 7.A como provisional (T-6). **Hoy el código no tiene ninguno de los tres criterios**: no existe verificación de pendiente mínima ni máxima, `S = 0` se rechaza con `DatoInvalidoError` en M3 y M4, y G2 compara sin desnivel.

> **Corregido (`INF-5.1.6`, `INF-3.2.7`, T-2, 2026-11-11).** La última frase de la nota anterior ya no es cierta en su parte (a): **los dos criterios de pendiente existen** (`pendiente_minima_conducto` = 0.0, ventana 0.0–0.005; `pendiente_maxima_conducto` = 0.10, ventana 0.02–0.10), los aplica **V10** (`M5.v10_pendiente_conducto`; fila nueva de la Fase 5) y `S = 0` se admite en M3 y M4 (nota de §4.2). `M5.limites_de_pendiente()` devuelve el par y es lo que M7 (T-6) tiene que leer para decir cuál de los orígenes de la pendiente gobernó. Las partes (b) y (c) siguen pendientes de T-6.

> **Corregido (`INF-3.3.3`, `INF-5.1.18`, `INF-3.2.7`, T-6, 2026-11-11).** La lista de 7.B queda así, y el párrafo anterior deja de ser cierto en lo que toca a T-6. **(1) Longitud.** «Ancho de plataforma + proyección de taludes, afectada por esviaje» no decía con qué altura se proyecta cada talud, y el código usaba la del eje (rasante − terreno) para los dos. Es el criterio `[A]` **`metodo_longitud_conducto`**, con dos valores: **`por_extremo`** (el del archivo) y `terraplen_simetrico` (la fórmula anterior, conservada como caso particular). Por extremo, el conducto se superpone a la sección transversal **del cruce** —la esviada—, que es lo que el HDS-5 describe con el barril estimado (núm. 2.2.4 b. «Culvert Length» y Figura 2.4, pág. impresa 2.8 / PDF 70, cita `HDS5_3ED.2.2.4#LONGITUD`): un talud a cada lado y la salida más baja que la entrada. **Hasta qué nivel baja cada talud lo elige el proyecto, no la fuente:** la figura del HDS-5 dibuja los taludes muriendo en la cara superior del barril y la Lámina Nº 01 a) del Manual en la coronación de los cabezales; aquí el talud baja desde el borde de la plataforma hasta el **fondo** del conducto en ese extremo —un barril de altura cero—, y la salida queda `S·L` más baja que la entrada, de modo que `L = [ancho + talud·(H_entrada + H_salida0)] / [cos(esviaje) − talud·S]`, con `H` medida desde el borde de la plataforma (la rasante, corregida por `bombeo` o por `peralte` cuando la sección típica los da: DG-2018 núm. 304.05 y 304.06, datos externos opcionales) hasta el fondo de la **entrada**. El proyecto mide al fondo y no a la clave porque la longitud hace falta **antes** de conocer la sección: el HDS-5 dice que el diseño arranca con una longitud aproximada (núm. 3.1.4, pág. impresa 3.9) y manda encajar después la sección elegida (núm. 3.3.5, pág. impresa 3.25: «the length should be close to the approximate length»), que es lo que 7.B hace al imprimir la **longitud entre cabezales a la clave** de la sección adoptada, sin tolerancia —la fuente no la da— y sin sustituir a la del diseño. La longitud al fondo es la **cota superior** y **no es el lado seguro por construcción**: alargar el conducto suma fricción y resta caída, y en A-01 del corredor de referencia el HW de salida es 0.9925 m con la longitud al fondo contra 1.0002 m con la longitud a la clave (7.7 mm menos; sin consecuencia allí, porque gobierna la entrada con 1.042 m). Con el fondo de entrada **adoptado** igual al terreno —que es la cota del terreno en el eje— el método ancla ahí la entrada y carga toda la caída aguas abajo (para un lecho que pasara por esa cota en el eje, A-01 daría 18.638 m y no 18.869); con el fondo medido es exacto. `bombeo` y `peralte` son **excluyentes** en un mismo punto, y su ausencia se avisa. La longitud entre cabezales, que es la de construcción y metrado, la cierra el cabezal por punto (T-7a). **(2) Esviaje.** El factor es `1/cos(esviaje)`, con el ángulo medido desde la **normal** al eje de la vía (HDS-5 núm. 5.4.1, pág. impresa 5.12). El criterio `[A]` **`esviaje_max_grados`** pasa a tener valor, **45°** (ventana 45°–60°), por analogía con el máximo práctico del esviaje de **embocadura** del HDS-5 (núm. 5.4.2, pág. impresa 5.13), que coincide con el del barril cuando el cabezal va paralelo a la vía; superarlo es **aviso** (verificación G3) y no bloqueo, porque el esviaje es un dato de entrada y el Manual admite acondicionar el cauce (núm. 4.1.1.3.2, pág. impresa 71). **(3) Pendiente.** M7 resuelve una vez la pendiente adoptada y la memoria imprime su origen: la del cauce, la declarada (`S_conducto`), o la mínima/máxima cuando gobierna (`pendiente_minima_conducto` / `pendiente_maxima_conducto`, que crea T-2; sin ellos el tercer origen no existe). **(4) Cotas.** La cota de salida es `cota_entrada − S·L` y G2 verifica `cota_salida ≥ cota_fondo_receptor + desnivel`, con el criterio `[A]` **`desnivel_minimo_entrega_m`** = **0.0 m** (ventana 0.0–0.30 m): la entrega a nivel del fondo del receptor. **Ninguna fuente da ese desnivel** —el núm. 4.1.1.3.3 del Manual exige que la pendiente no altere la erosión y la sedimentación, sin cifra y sin mencionar la entrega; su Lámina Nº 01 tipifica las ubicaciones sin acotarlas—, y no es conservador en un solo sentido: una salida elevada descarga en caída. El remanso del receptor no se cubre con él sino con el TW de §1.3. **(5) Cota de entrada.** Cuando la columna `cota_fondo_entrada` trae el fondo medido, gana; cuando falta, rige `origen_cota_fondo_entrada` y la memoria avisa —«fondo de entrada adoptado igual al terreno de plataforma: medir en el cauce»— y marca como **provisional** el delta de rasante de 7.A. Todo lo anterior se imprime como pasos con fórmula sustituida (7.B.1 a 7.B.5, G2 y G3).

**Acoplamiento circular declarado:** rasante → paquete estructural → subrasante → CBR → resguardo → V4 → rasante. Se corta fijando la rasante en 7.A y congelándola.

---

## Fase 8 — Verificación estructural del conducto

**Sin catálogo de proveedor.** La selección se hace contra las **normas de producto**, coherente con la decisión de neutralidad comercial de §3.2:

| Material | Norma que define clases / calibres por altura de relleno |
|---|---|
| Concreto reforzado | **AASHTO M-170M** — clases I a V |
| TMC | **ASTM A796/A796M** (práctica de diseño estructural: el calibre sale de su procedimiento, §7 a §10, y se elige de sus Tablas 2 a 35; cobertura mínima §11) — con **ASTM A760/A760M = AASHTO M 36** como norma de producto |
| HDPE | **AASHTO M294** + AASHTO LRFD Sec. 12 (M 294-11 num. 1.4 lo escribe así: excluye camas, relleno y carga de cubierta y remite el diseño estructural a LRFD Sec. 12 — verificado en N2 sobre la traducción no oficial de `normas/`, afirmación negativa `SIN_CLASE_POR_ALTURA_M294_TRAD`) |

> **Corregido (`DIS-HR-A807`, N1).** Esta fila decía «**ASTM A-807 / AASHTO M36** — calibre según altura», y desde I2 llevaba la remisión cuestionada al pie sin fuente contra la que corregirla. N1 incorporó ASTM A796/A796M-13 a `normas/` y la leyó entera (verificación por imagen renderizada: su capa de texto llega duplicada). Tres cosas, cada una con su cita: (1) **A-807 no es la norma del calibre**: es una práctica de **instalación** — el num. 22.1 de A796 manda que la construcción e instalación «shall conform to Practice A798/A798M or A807/A807M», y es la única mención de A807 en las 20 páginas con contenido del ejemplar —la impresa 1, con la lista de normas referenciadas del num. 2.1, falta— (`ASTM_A796.22.1`); es exactamente para lo que 507.05/.06/.08 del EG-2013 la invocan. (2) **El calibre lo fija A796, pero no en una tabla por altura**: el espesor es la *salida* de su procedimiento (presión de diseño, empuje, área de pared requerida con SF = 2, pandeo, costura, factor de flexibilidad) y se *selecciona* de las Tablas 2 a 35 de propiedades seccionales «equal to or greater than the required wall area (A)» (`ASTM_A796.8.1.1.2#SELECCION`); las «tablas de calibre por altura de cobertura» de la práctica norteamericana son derivadas por fabricantes y no están en la norma (afirmación negativa `SIN_TABLA_CALIBRE_POR_COBERTURA_A796`, con su ámbito barrido). El único cruce espesor/cobertura de A796 va al revés: cobertura mínima de 600 mm si el espesor es menor de 1.32 mm, y 300 mm en todo caso (`ASTM_A796.11.1#PISOS`). (3) La mitad «AASHTO M36» de la fila era correcta como **norma de producto** — A796 §17.1 remite los materiales a A760/A760M, que es M 36 en doble designación (`ASTM_A796.17.1`) — y falsa como fuente del calibre. Consecuencia para los ítems 1-2 de abajo: para el TMC no hay «tabla» que transcribir; hay un **procedimiento** que implementar, y `clases_producto_por_relleno` lo declara así. Las siete tablas SI de propiedades seccionales de las corrugaciones del catálogo (Tablas 3, 5, 7, 9, 11, 15 y 17) están transcritas enteras en el registro como insumo de ese procedimiento, con los límites del factor de flexibilidad de cada perfil (§10.2 a §10.6). La cabecera de la columna («Norma que define clases / calibres por altura de relleno») y los ítems 1-2 se conservan tal cual por la regla de edición quirúrgica, y se leen con esta nota: para el TMC la «norma que define el calibre» lo define por procedimiento, y «seleccionar el calibre según la altura real de relleno» es correrlo, no leer una fila.

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

> **Corregido (`INF-5.1.15`, `INF-3.4.1`, `INF-3.4.2`, T-0, 2026-11-11).** Esta fase está escrita para **un** cabezal, sin decir de qué punto, y el código la siguió al pie de la letra: la Fase 9 es «del proyecto» —una sola `GeometriaCabezal` para todo el corredor, también para el marco de la Familia C, mientras el nivel freático que entra en sus empujes sí es el de cada punto—, el predimensionamiento es un criterio vacío (`predimensionamiento_cabezal`) y **las aletas no existen**: no hay ni función ni tipo, solo el criterio `angulo_aletas`, también vacío. Desde T-0 esta hoja pide otra cosa, y la implementa T-7 de la cadena T en tres pasos: **el cabezal es POR PUNTO** —cada alcantarilla dimensionada tiene el suyo, con su D o B×H, su HW de diseño, su cota de fondo, su altura de terraplén y su NF— **y tiene aleros** con geometría propia (ángulo, longitud, alturas inicial y final), coherentes con la embocadura adoptada en §4.2: si la embocadura pasa a ser con aleros, k_e y la carta de control de entrada cambian con ella, que es la frase «ambas decisiones deben moverse juntas» de §9.1 llevada a su consecuencia (T-7a); la estabilidad se **ensambla** por punto en un solo marco de verificación —hoy M9 mezcla factores de carga LRFD con factores de seguridad globales de E.050 sin decir si las cargas son factoradas o de servicio (`INF-5.1.5`)—, y **qué marco rige lo decide el dueño del proyecto**, no esta hoja ni el prompt (T-7b); y el armado o la alternativa ciclópea (T-7c). **Hoy** nada de eso está: §9.2 a §9.4 siguen describiendo las piezas —cargas, cadena sísmica, factores, cuantías— que M9 implementa como biblioteca sin ensamblar, y siguen valiendo como tales.

### 9.1 Condición normativa

EG-2013 Sección 503 (Concreto Estructural), num. 503.01, pág. 905, describe el suministro de concreto para *"estructuras de drenaje, muros de contención, cabezales de alcantarillas, cajas de captación, aletas, sumideros..."*.

**Precisión:** los cabezales **no tienen partida con numeral propio**; se pagan bajo el volumen de concreto estructural (Sec. 503) y el acero (Sec. 504). Que aparezcan nominados en 503.01 confirma que son elemento estándar de terminación, pero el argumento es más débil que "existe una partida específica".

**Geometría de embocadura:** tubo a ras del muro (*square edge*), coherente con las constantes HDS-5 adoptadas en §4.2. Ambas decisiones deben moverse juntas: cambiar el detalle obliga a cambiar las constantes.

### 9.2 Cargas — AASHTO LRFD vía Manual de Puentes [N]

**Combinaciones:** AASHTO LRFD Sec. 3.4.1 — Resistencia I, Servicio I, Evento Extremo I (num. 2.4.5.3, págs. 140-143). Sus **factores** están transcritos en el propio Manual, Tablas 2.4.5.3.1-1 y 2.4.5.3.1-2, pág. impresa 143: son `[N]`, no un vacío (`NOR-PUE-04`).

**Carga viva:** **HL-93** (num. 2.4.3.2.2.1, págs. 103-104).

**Sobrecarga en el trasdós** (num. **2.4.2.2** «Cargas de Suelo: EH, ES, y DD», **pág. impresa 102**): con tráfico a distancia horizontal ≤ H/2 desde la parte superior de la estructura, se añade sobrecarga vertical **no menor que la equivalente a 0.60 m de relleno**. Presión horizontal = γ · h_eq · k_a. **En un cabezal bajo terraplén vial siempre aplica**, salvo que se diseñe una losa de aproximación, que el propio numeral exime; este expediente no proyecta ninguna.

> **Corregido dos veces (`NOR-PUE-01`, `NOR-PUE-02`, `MAT-D5`, `MAT-O1`, `MAT-X1`; conflicto #4 del plan de correcciones).**
>
> **El numeral.** Esta hoja citaba el num. 2.1.4.3.9, pág. 91. Ese numeral existe y se titula **«Aparatos de Apoyo»**: va de la conexión entre superestructura y subestructura, y no contiene la palabra «sobrecarga», ni «trasdós», ni el valor 0.60. El texto real está en el **2.4.2.2**, pág. impresa 102. El numeral falso estaba propagado a seis puntos del repositorio.
>
> **El valor.** El 0.60 m es un **piso** —el Manual escribe «no menor que»—, no un valor de diseño, y el Manual **no transcribe** las tablas de altura de suelo equivalente de AASHTO: su traducción de la Sec. 3.11 se corta en el empuje pasivo k_p. El valor lo tabula **AASHTO LRFD 3.11.6.4** (pág. impresa 3-151) por altura del muro, con interpolación lineal obligatoria, y para un cabezal de 2.0 m con tráfico perpendicular da **1.12 m** — 1.87 veces el 0.60 adoptado, con γ_LS = 1.75.
>
> **Cómo se resuelve.** Los dos rigen y gobierna el mayor (regla del mayor de §0.2): `h_eq = max(0.60 m, h_eq_AASHTO(altura, orientación, borde))`. **Cuál de las dos tablas de AASHTO aplica depende de la orientación del muro respecto del tráfico**, que es un dato de sitio de este expediente y **está declarado como pendiente**: mientras no se declare, el cálculo se detiene. Tres matices de la fuente que hay que conservar: AASHTO ofrece **dos binomios acoplados** (estribo+perpendicular, muro+paralelo) y no un eje libre de orientación —aplicar la Tabla ‑1 a un cabezal es analogía declarada—; **ninguna frase del articulado reparte las dos tablas**, lo hacen sus títulos y el comentario C3.11.6.4; y el umbral de distancia es **1.0 ft = 0.3048 m exactos**, no 0.30 m.

**Empuje de tierras:** activo, con el **Ka de Coulomb** del Manual de Puentes, num. **2.4.4.1.5.3** «Coeficiente de Empuje Lateral Activo, ka» (3.11.5.3 AASHTO), ecs. 2.4.4.1.5.3-1 y -2, págs. impresas **135-136** (PDF 136-137: el numeral y las dos ecuaciones arrancan en la 135; la figura de simbología y la Tabla 2.4.4.1.5.3-1 de δ están en la 136), que con talud del relleno β = 0, fricción muro-relleno δ = 0 y trasdós vertical (θ = 90°) **se reduce a tan²(45 − φ/2)**, la forma que esta hoja escribía. **Empuje hidrostático y subpresión:** con NF a 1.4 m no es opcional.

> **Corregido (`EXT-M-06`, EXT-0).** Esta hoja escribía «Ka = tan²(45 − φ/2)»
> sin decir de dónde sale, y el código la seguía: el empuje estático y la
> sobrecarga del trasdós iban con Rankine (`ka_rankine`) mientras el incremento
> sísmico iba con Mononobe-Okabe, que es Coulomb con aceleración — dos familias
> de coeficiente sobre el mismo muro, decisión declarada en los docstrings de
> `empujes_trasdos` y `ka_rankine` pero no autorizada por ninguna fuente. La
> fuente primaria del marco elegido en §9.1 es el Manual de Puentes y su
> coeficiente activo es el de Coulomb (verificado). Con ángulos nulos las dos
> expresiones coinciden (diferencia medida −5.6e-17), de modo que **para un
> cabezal con β = δ = 0 ningún número se mueve**; dentro de las ventanas
> declaradas la diferencia del coeficiente va de **−11.1 %** (φ = 30°, i = β =
> 0, δ = 22.7°) a **+44.4 %** (φ = 38°, i = β = 10°, δ = 0), y con el
> k_h = 0.5 de esta obra Mononobe-Okabe deja de tener solución para
> i ≥ φ − 26.6° (3.4° con φ = 30°, 8.4° con φ = 35°), que es un límite que la
> sensibilidad del criterio dice. Lo implementó EXT-7 (`k_a_coulomb`, cita
> `MP.2.4.4.1.5.3`, discrepancia `DIS-HR-KA-COULOMB`). Precedentes:
> `NOR-PUE-07`, `NOR-PUE-08`.
>
> **Corregido (`EXT-M-06`, EXT-7).** La enmienda de EXT-0 escribía aquí «la
> diferencia va de −6.25 % a +7.23 %» y «desde i ≥ 5° con φ = 30°»: los dos
> números eran falsos. Medidos con `M9.k_a_coulomb` sobre las cuatro ventanas
> de `criterios_adoptados.py` (φ 30–38, i 0–10, β 0–10, δ 0–22.7): el rango
> es el de arriba, y el bloque C de CP-9 (dentro de las cuatro) da +9.67 %.
> Además la resultante de Coulomb actúa a δ + β de la horizontal y el cálculo
> la toma **entera como horizontal** (declarado en `M9.empujes_trasdos`;
> descomposición diferida, `EXT-7-04`).

#### Cadena sísmica — desagregada

| Paso | Símbolo | Valor | Origen | Etiqueta |
|---|---|---|---|---|
| Aceleración pico en roca Clase B, Tr = 1000 años | PGA | **0.50 g** | Manual de Puentes, Apéndice A3, mapa "PGA, T = 0.0 seg" | **[S]** (era [N]) |
| Factor de sitio | F_pga | **1.0** | Tabla 2.4.3.11.2.1.2-1, pág. impresa 123 (valores [N]); **elección de las FILAS** ante ausencia de caracterización de sitio | [A] |
| Aceleración ajustada por sitio | **A_s = F_pga · PGA** | **0.50 g** | Calculado | — |
| Coeficiente sísmico de base | **k_h0 = A_s** | **0.50** | Manual de Puentes, **2.8.1.1.14.2.1** | [N] |
| Factor de muro (sin reducción) | — | **1.0** | Manual de Puentes, **2.8.1.1.14.2.2** — el numeral fija **un** valor, 0.5, y de forma permisiva; el 1.0 es la ausencia de reducción | **[A]** (la declaración) |
| **Coeficiente sísmico horizontal de diseño** | **k_h** | **0.50** | Calculado | — |
| Coeficiente sísmico vertical | k_v | **0** | Manual de Puentes, **2.8.1.1.14.2.1** — «kv **se asumirá cero**… a no ser que…» | **[N] condicionado** (era [A]) |
| **Fuerza de inercia del muro** | **P_IR = k_h·(W_w + W_s)** | — | Manual de Puentes, **2.8.1.1.14.1**, ec. 2.8.1.1.14.1-1 | [N] |

*Si el muro admitiera desplazamiento de **1.0 a 2.0 in o más** (25.4–50.8 mm; el «o más» abre el rango por arriba y no debe recortarse), k_h = 0.5 · k_h0 = 0.25. **No asumirlo en un cabezal empotrado en terraplén.** AASHTO condiciona además esa reducción a que el movimiento sea aceptable para el propietario, de modo que la decisión no es sólo técnica.*

Para K_AE por **Mononobe-Okabe** se requieren además φ del relleno, pendiente del relleno (i), inclinación del muro (β) y fricción muro-suelo (δ).

**Todos estos valores se leen desde `criterios_adoptados.py`.**

#### Lo que esta sección omitía, y por qué la cadena no termina en k_h

Las cinco correcciones de abajo se levantaron contra la fuente primaria (los PDF de `normas/`) y **el defecto es de esta hoja de ruta**, no del código. Se dejan escritas aquí para que quien lea la hoja sin leer el código no diseñe con la versión incompleta.

1. **Faltaba `P_IR` y faltaba la combinación.** La cadena de arriba terminaba en k_h y K_AE. El num. **2.8.1.1.14.1** — la misma sección de la que esta hoja toma k_h0 y la reducción por desplazamiento, un nivel más arriba — exige combinar el empuje sísmico con la **inercia de la masa del muro**, `P_IR = k_h·(W_w + W_s)`, donde W_w es el peso de la pared y W_s el del suelo inmediatamente encima del muro **incluido el talón**. Y no como suma: los dos efectos **no son simultáneos**, de modo que se investigan dos casos y rige el más desfavorable —
   - **100 % P_AE + 50 % P_IR**, y
   - **50 % P_AE** (pero *«no sea menor que la presión estática activa del terreno»*) **+ 100 % P_IR**.

   Con k_h = 0.50, P_IR vale la mitad del peso movilizado — el mismo orden que el propio incremento sísmico del empuje —, así que la omisión iba del lado **inseguro** en volteo y en deslizamiento sísmicos (`MAT-D6`, `MAT-X7`).

2. **Faltaba la excentricidad de la resultante en la base**, que el mismo num. 2.8.1.1.14.1 acota bajo sismo, y el límite **depende de γ_EQ**: **dos tercios centrales (e ≤ B/3)** con γ_EQ = 0.0, ocho décimas centrales (e ≤ 0,4·B) con γ_EQ = 1.0, e **interpolación lineal** en medio. Y γ_EQ es un vacío que este expediente todavía no ha declarado (`MAT-O16`).

   **El «dos tercios» no sale del literal del Manual, que imprime «tercio central» — es su tercera errata en esta cadena, y la única que mueve un número.** AASHTO 11.6.5.1 escribe «middle **two-thirds**» (pág. impresa 11-25); el propio Manual traduce bien ese giro tres páginas antes, en su numeral estático de límites de excentricidad («dentro **los dos tercios centrales** del ancho de la base»), y en el mismo párrafo sísmico traduce bien «eight-tenths». Y la lectura literal es **normativamente imposible**: dejaría el límite bajo sismo (B/6) al doble de estricto que el límite estático del mismo Manual (B/3), invirtiendo la filosofía de estados límite. Con el texto de AASHTO el artículo es coherente: **ancla** en γ_EQ = 0.0 sobre el mismo B/3 del estático y **relaja** hasta 0,4·B. El código sigue a AASHTO.

3. **`k_h0 = A_s` no es incondicional.** El num. 2.8.1.1.14.2.1 añade que *«para muros cimentados sobre Sitio con suelos Clase A o B (roca dura o blanda), k_h0 estará basado en 1.2 veces el coeficiente de aceleración pico del suelo»*. Con cimentación en roca serían 0.60 y no 0.50 (`MAT-O4`, `NOR-PUE-12`). **El paréntesis que el Manual imprime a continuación —«(es decir, 1.2 kh0=FpgaPGA)»— es errata**: leído al pie de la letra da una *reducción* del 17 %. Gana la prosa, coincidente con AASHTO 11.6.5.2.1.

4. **El Manual imprime K_AE con «1 − √(…)» y eso es errata de imprenta** (Apéndice A11, num. A.11.3.1, pág. impresa 586). AASHTO — que el propio Manual declara transcribir — imprime «1 + √(…)». Con el menos, K_AE **diverge** cuando el radicando tiende a 1 y el caso límite k_h = k_v = 0 deja de devolver el Ka de Coulomb. **El código sigue a AASHTO y hace bien**; esta hoja no advertía de la discrepancia, de modo que un revisor que «corrigiera» el código contra la letra impresa rompía la fórmula (`MAT-O2`, `MAT-X2`).

5. **El agua bajo el NF.** Esta sección dice que «empuje hidrostático y subpresión no son opcionales» y no dice nada de cómo entra el freático en el **empuje de tierras**. El código usa γ total en toda la altura más la hidrostática completa, con lo que cuenta el agua de poros dos veces en la zona sumergida; AASHTO 3.11.3 *«Presence of Water»* exige γ **sumergido** bajo el nivel freático. La desviación es **conservadora** y su magnitud es un valor absoluto constante, no un porcentaje: el exceso de presión horizontal vale Ka·γ_w·h_agua — 1,96 kPa con Ka = 1/3 y 0,60 m de agua —, de modo que en relativo pesa +25 % sobre un muro de 0,60 m (que es como la ficha `MAT-O3` lo calculó), +11 % sobre uno de 2,00 m con el freático a 1,40 m, y menos cuanto más alto sea el muro. Se declara en el punto de uso; corregirla exige un peso específico sumergido del relleno que el expediente no tiene (`MAT-O3`, `MAT-X3`).

### 9.3 Estabilidad — E.050 [N]

| Verificación | Estático | Sísmico | Numeral |
|---|---|---|---|
| Capacidad portante (falla por corte) | **3.0** | **2.5** | Art. 21.1/21.2, pág. 34 |
| Volteo — estabilidad interna | **1.50** | **1.25** | 39.13.6 a), pág. 72 |
| Deslizamiento — estabilidad interna | **1.50** | **1.25** | 39.13.6 a), pág. 72 |
| Estabilidad global del muro | **1.50** | **1.25** | 39.13.6 b), pág. 72 |
| Estabilidad del talud | **1.50** | **1.25** | Art. 30.3, pág. 39 |

**Y una sexta fila, que E.050 no escribe y el Manual de Puentes sí (`MAT-O16`):** la **ubicación de la resultante en la base bajo sismo**, num. 2.8.1.1.14.1 — dentro de los **dos tercios centrales** (e ≤ B/3) con γ_EQ = 0.0, dentro de las **ocho décimas centrales** (e ≤ 0,4·B) con γ_EQ = 1.0, e interpolación lineal entre ambos (ver la advertencia de errata en §9.2). No es un FS y por eso no cabe en la tabla de arriba.

**Y la `q_actuante` que la primera fila da por resuelta tiene su propio numeral, que no es el sísmico:** el num. **2.8.1.1.12.2 «Capacidad de Carga»** (pág. impresa 248) reparte la distribución de presión de contacto **por terreno de fundación** — presión **uniforme** sobre el ancho efectivo B − 2e si el muro se apoya en **suelo**; distribución **lineal** sobre B, con su forma triangular fuera del núcleo, si se apoya en **roca**. Este cabezal se funda en la llanura arenosa: le corresponde la primera. Y el mismo capítulo trae el límite **estático** de excentricidad (dos tercios centrales en suelo, nueve décimos en roca) que es el que ancla el extremo γ_EQ = 0.0 del límite sísmico.

**Parámetros de resistencia** (Art. 20, pág. 33): en cohesivos φ = 0; en friccionantes c = 0. No se combinan.

**Zapata próxima al talud** — doble verificación:
- **E.050 Art. 30.1-30.2:** capacidad de carga considerando inclinación de la superficie y de la base; análisis de estabilidad global del talud con la estructura cargándolo
- **Manual de Puentes 2.8.1.3.1.2c** (págs. 272-273): **N_q = 0.0**; N_c y N_γ se reemplazan por **N_cq** y **N_γq** (figuras 2.8.1.3.1.2c-1 y -2, Meyerhof 1957). N_s = 0 si B < H_s; N_s = γH_s/c si B ≥ H_s

La penalización es severa por pérdida de confinamiento. **El cabezal se apoya en el borde del terraplén, no en terreno horizontal.**

### 9.4 Refuerzo y durabilidad

- Flexión y corte por **AASHTO LRFD Sección 5**
- **Durabilidad y recubrimientos por E.060** (excepción de 0.2). Rige el recubrimiento mayor entre AASHTO y E.060
- **Referencia de cuantías mínimas** (E.060 Art. 14.3.1, pág. 133): horizontal ≥ 0.002, vertical ≥ 0.0015; acero por temperatura en ambas caras si espesor ≥ 250 mm (Art. 14.8.3); espaciamiento ≤ 3h y ≤ 400 mm (Art. 14.3.3)
- **Cuantías mínimas por cortante en el plano** (E.060 **Arts. 11.10.10.2 y 11.10.10.3**, pág. 104; verificado): bajo el régimen del 11.10.10 —cortante **en el plano** del muro, que el Art. 14.2.4 aplica a muros— la cuantía horizontal no debe ser menor que **0.0025** (11.10.10.2) **y la vertical tampoco**: ρv = 0.0025 + 0.5·(2.5 − hm/ℓm)·(ρh − 0.0025) ≥ 0.0025, ec. **(11-32)**, «pero no necesita ser mayor que el valor de ρh requerido por 11.10.10.1», con hm la altura total y ℓm la longitud total del muro (11.10.10.3). El 0.0015 vertical del Art. 14.3.1 es el mínimo **general**; con cortante alto en el plano el vertical **también** sube, y esta hoja sólo decía lo del horizontal

  > **Corregido (`EXT-M-05`, `R95-031`, EXT-0).** Esta lista traía el 14.3.1 y
  > callaba el 11.10.10.3, y el código lo ejecuta: `M9.cuantia_de_diseno` en su
  > rama vertical afirma en su docstring que «cortante_alto=True no cambia el
  > mínimo del Art. 14.3.1» y devuelve 0.0015 —1.67 veces menos acero que el
  > piso del 11.10.10.3—. Sin consumidor de producción, pero el hallazgo estaba
  > verificado desde `R95-031` (auditoría normativa, ALTA) y nunca entró al
  > tracker. Y hay una **pregunta previa que decide si los dos artículos rigen**:
  > el **11.10.2** gobierna las «fuerzas cortantes horizontales **en el plano**
  > del muro» (11.10.3 a 11.10.10), y el **11.10.1** manda las cortantes
  > **perpendiculares** al plano a las disposiciones para losas del **11.12**
  > (pág. 103; verificado). Un cabezal en voladizo bajo empuje de tierras
  > trabaja **perpendicular** a su plano: si no hay cortante en el plano, ni el
  > 11.10.10.2 ni el .3 rigen y el mínimo es el del 14.3.1. Esa aplicabilidad es
  > una decisión del proyectista que **no está declarada**: entra como criterio
  > [A] de expediente en EXT-7, junto con hm, ℓm y el ρh requerido que la ec.
  > (11-32) necesita y que `GeometriaCabezal` no tiene. La ec. (11-32) no se
  > implementa hasta tenerlos; la rama vertical con cortante alto **se detiene**.
  > Precedente: `NOR-E060-03` (el 11.10.10.2 no define umbral; lo define el
  > 11.10.10.1).
- **Alternativa en concreto ciclópeo** — dos mínimos sobre el mismo material, y **gobierna el mayor** (regla del mayor de §0.2): E.060 Art. 22.10 (págs. 194-195) pide f'c de matriz ≥ 10 MPa y piedra desplazadora ≤ 30 % del volumen; la **Tabla 503-07 del EG-2013** (503.04, pág. impresa 912) clasifica el concreto ciclópeo como **Clase G** — «Se compone de concreto simple Clase F y agregado ciclópeo, en proporción de 30% del volumen total, como máximo» — con matriz de **14 MPa**. Para esta obra vial rigen los dos: **f'c de matriz ≥ 14 MPa**. Admitido para muros de gravedad. **Opción realista para cabezales pequeños**

  > **Corregido (`DIS-HR-CICLOPEO`, I2).** Esta línea pedía «f'c de matriz ≥ 10 MPa» citando solo el Art. 22.10 de E.060: miraba una de las dos normas que rigen sobre el mismo material. Quien la leyera sin leer el código habría dimensionado una matriz de 10 MPa que `M9.verificar_ciclopeo` (que contrasta contra `CICLOPEO_FC_MATRIZ_MIN_APLICABLE` = 14 MPa) rechaza. Cita ancla: `EG2013.503.04#T503_07`, verificada. Sigue vigente la deuda anotada en el código: el Art. 22.10.2.3 añade un techo de cálculo (φ = 0.5 y f'c de diseño ≤ 10 MPa) — se especifica con el mayor de los mínimos y se diseña con el techo.

---

## Fase 10 — Alcantarillas de alivio: espaciamiento

**Espaciamiento de diseño = mín(límite normativo, longitud por capacidad).**

**1. Límite normativo [N]** — num. 4.1.2.1 d), pág. impresa **179** (PDF 182):

> **Corregido (`PC-30`, `NOR-HID-02`, EXT-0).** Esta línea decía «pág. 178». La
> 178 es la Tabla Nº 34 (dimensiones mínimas de cuneta); el apartado d)
> «Desagüe de las cunetas», con los 250 m y los 200 m, está en la 179
> (verificado; es la página que el registro, `MC_HHD_CUNETA`, lleva desde S12).
> `NOR-HID-02` figuraba «Cerrado» mientras lo que la memoria imprime
> —`NUMERAL_FASE_10`, `Espaciamiento.numeral`, la ficha de `long_max_cuneta`—
> y esta hoja seguían en 178: cierre incompleto en cuatro sitios más el
> manifiesto. La hoja se corrige aquí, los textos del código en EXT-6, y el
> hallazgo se reabre.

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
| 1.2 | **VERIFICADO EN CONTRA — los topes no son de las normas de producto** (discrepancia del registro, resuelta en I2; manifiesto §7). A760 Tabla 1 tabula 100–3600 mm y M 170M Tablas 1–5 cubre 300–3600 mm (su Sec. 7.2 prevé diseños mayores): 2.70 y 2.10 m son topes de CATÁLOGO `[A]` (`'D_max_catalogo'`, con advertencia obligatoria). El del HDPE (~1.50 m) se contrastó en N2 sobre la traducción no oficial de M 294-11: la serie termina en 1500 mm (`AASHTO_M294_TRAD.7.2.1`, sin firma), coincide, y sigue siendo tope de catálogo `[A]` | ASTM A760 Tabla 1 · AASHTO M 170M Tablas 1–5 (leídas de los PDF) · M 294-11 num. 1.1.1 y 7.2.1 (traducción no oficial) | **Cerrado en contra** en concreto y TMC; **cerrado a favor** en HDPE, sobre traducción. V9 descarta por catálogo, nunca «por norma» |
| 1.3 | **VERIFICADO EN IMPLEMENTACIÓN — los valores están extraídos**: 4.572 m/s (15 ft/s) para TMC y HDPE, de la Tabla 8-4 «Pipe Abrasion Levels» del WSDOT Hydraulics Manual M 23-03.12 (`'v_max_tmc'`, `'v_max_hdpe'`, `[C]`). Lo que queda para gabinete es traer la Tabla 8-4 a `normas/`, porque hoy la cita no es auditable contra un documento del repositorio (`MAT-O14`). *Corregido desde* «PPI / FHWA — valores numéricos» (`R48-030`). *Actualizado (T-0 y T-4): el manual está en el repositorio de normas y T-4 transcribió con página el §8-3.3, la Tabla 8-4, el §3-3.5, el §8-5.1 y el §8-5.2; la cita ya es auditable. El del TMC quedó como `[A]`* | WSDOT M 23-03.12 | V3 para materiales flexibles |
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
| 3.5 | pH y resistividad (solo si TMC sigue en carrera) | Laboratorio | Defensibilidad del TMC. *Desde T-4 son entradas del programa (`pH`, `resistividad_ohm_cm` en `--datos-externos`) y la matriz de §3.4 las aplica; igual los sulfatos y cloruros del 3.4* | Baja |
| 3.6 | Dos ensayos de profundidades distintas, pedirlos juntos: SPT ≥ 15 m cada 1 m (licuefacción, E.050 Art. 38) y caracterización de los 100 ft = 30.48 m superiores, Vs30 o N̄ (clase de sitio, AASHTO 3.10.3.1) | Estudio geotécnico | Evaluación de licuefacción y clase de sitio definitiva | Diferida al expediente |

**Lectura del tablero:** los ítems 3.1 y 3.2 son los verdaderamente críticos. El 3.1 bloquea una familia entera de estructuras y el TW de todas las demás; el 3.2 condiciona el caudal de diseño de todo el estudio. Ambos estaban fuera de la lista original de siete y son los de mayor plazo, porque dependen de terceros.

---

## Anexo A — Índice de criterios no normativos

**Contenido completo en `criterios_adoptados.py`.**

| Criterio | Etiqueta | Estado |
|---|---|---|
| PGA en roca (0.50 g) | [N] | **Cerrado.** Falta registrar coordenadas de lectura |
| Clase de sitio | [S] | **Sin valor — dato de sitio pendiente de ensayo** (desde S14; `DIS-HR-CLASE-DE-SITIO-F`). Las fuentes prohíben suponerla E o F sin dato geotécnico. Lo cierra la caracterización de los 100 ft (30.48 m) superiores (Vs30 o N̄) y, solo si diera Clase F, el estudio de respuesta de sitio — §0.5. La elección de filas C/D/E es el criterio aparte `F_pga` [A] |
| F_pga = 1.0 | [A] | Tabla [N]; elección [A]. Sensibilidad (0.9, 1.0) |
| Factor de muro = 1.0 | [N] | Firme |
| k_v = 0 | [A] | Sensibilidad (0, 0.5·k_h) |
| M_w para licuefacción | [A] | **Sin valor.** Tablero 2.2 |
| Constantes HDS-5 para HDPE | [C] | Carta *Circular Concrete, square edge*. Condicionado a HDPE de interior liso |
| k_e (coeficiente de pérdida de entrada, §4.3) | [C] | HDS-5, embocadura square edge with headwall. **Cerrado en implementación** — sin numeral peruano |
| n de Manning para HDPE | [N→] | **Rango (0.010, 0.013)** por analogía. No valor puntual. El código lo **lee de** `constantes_normativas.MANNING["concreto_tubo_recto"]` (*corregido en T-0, `INF-5.1.11`: decía `["concreto_recto"]`, clave que no existe*), no lo copia: una analogía que duplica el literal de su origen deja de serlo en cuanto uno de los dos cambie. ***Corregido en T-4 (`INF-3.2.1`):** `[C]`, **(0.009, 0.015)**, derivado de la fila «Corrugated Polyethylene, Smooth» de la Table B.1 de HDS-5 en el registro normativo; ya no se lee de `MANNING["concreto_tubo_recto"]`* |
| Velocidad máxima en HDPE y TMC | [C] | **4.572 m/s** (15 ft/s), WSDOT Hydraulics Manual M 23-03.12, Tabla 8-4; fuente ausente de `normas/` (`MAT-O14`). *Corregido desde* «Sin valor. Fuente identificada (PPI/FHWA), valores por extraer» (`R48-030`). ***Corregido en T-4 (`INF-3.2.4`):** HDPE `[C]`; TMC `[A]` con ventana (3.048, 4.572) m/s. La fuente está en el repositorio de normas desde T-0* |
| Progresión de diámetros | [C] | 0.90 m + 0.15 m; los topes superiores son de catálogo `[A]` (`'D_max_catalogo'`) — §3.2, `DIS-HR-D-MAX`. ***Corregido en T-4 (`INF-3.3.1`):** el tope es el de la norma de producto (`'D_max_norma_producto'` `[C]`: 2.70 / 3.60 / 1.50 m; en concreto, el último diámetro con diseño estándar) y, en TMC, el de la corrugación adoptada (2.10 m); `'D_max_catalogo'` es opcional y sólo puede bajarlo* |
| Corrugación y espesor de plancha del TMC | [A] | `'corrugacion_y_espesor_tmc'` = 68 por 13 mm, 2.01 mm (T-4); se elige entre las diecisiete planchas de ASTM A796 Tablas 5, 7 y 9. Fija el espesor que separa el diámetro hidráulico del exterior y el tope del TMC |
| Umbrales de durabilidad del TMC | [C] | `'durabilidad_tmc_umbrales'`: pH 5.0–8.5, resistividad ≥ 1000 ohm-cm (WSDOT M 23-03.12 §8-5.1 y §8-5.2); sólo se pueden endurecer — §3.4 (T-4) |
| Suelo agresivo para acero galvanizado enterrado | [C] por analogía | `'suelo_agresivo_acero_lrfd'`: pH 5–10, resistividad ≥ 3000 ohm-cm, cloruros ≤ 100 ppm, sulfatos ≤ 200 ppm (AASHTO LRFD 11.10.6.4.2a y 11.12.8) — §3.4 (T-4) |
| Efecto del suelo agresivo (por analogía) sobre el TMC | [A] | `'suelo_agresivo_lrfd_sobre_tmc'` = `aviso`; alternativa `excluye` — §3.4 (T-4) |
| Suelos de fundación deficientes | [A] | `'sucs_fundacion_deficiente'` = OL, OH, PT, elegido en la Figura 3 de la E.050 — aviso de marco de §3.1 (T-4, `INF-5.1.9`) |
| HW/D máximo (1.5) | [A] | Sensibilidad (1.2, 1.5), **subrango** de la banda 1.0–1.5 que el HDS-5 describe (no prescribe). Corregido desde [C]. Ref. `NOR-HDS-02` |
| Resguardo HW–subrasante | [N→] | Analogía declarada desde el criterio de napa freática |
| TW en el receptor | [A] | **Sin valor.** Tablero 3.1 |
| Longitud máxima de cuneta (200 m) | [A] | Sensibilidad (200, 250) |
| φ del relleno del trasdós | [A] | **Sin valor.** Corte directo |
| c, φ del suelo de fundación | [A] | **Sin valor.** Corte directo o SPT |
| Capacidad portante admisible | [A] | **Sin valor.** EMS conforme a E.050 |
| Espesor de protección de salida (1.75 · d₅₀) | [A] | Sensibilidad (1.5, 2.0) |
| Ángulo de aletas | [A] | Según esviaje de cada punto |
| Método de la longitud del conducto (`metodo_longitud_conducto`) | [A] | `por_extremo` (T-6). Ventana: `terraplen_simetrico` / `por_extremo`. HDS-5 núm. 2.2.4 b., pág. impresa 2.8, para la superposición; medir al fondo es elección del proyecto |
| Desnivel mínimo de entrega al receptor (`desnivel_minimo_entrega_m`) | [A] | 0.0 m (T-6). Sensibilidad (0.0, 0.30). Ninguna fuente da el valor ni habla de la entrega: el núm. 4.1.1.3.3 del Manual exige cuidar la pendiente y su Lámina Nº 01 tipifica dónde puede quedar la salida; contrastarla con el fondo del receptor es lectura del proyecto |
| Esviaje máximo, como aviso (`esviaje_max_grados`) | [A] | 45° (T-6). Sensibilidad (45, 60). HDS-5 núm. 5.4.2, pág. impresa 5.13, por analogía |
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
# (T-4, INF-5.1.16) En el codigo se llama DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO
# y NO tiene consumidor: la rama de selva alta no esta programada.
Y_SOBRE_D_MAX = 0.75                # borde libre >= 25% (4.1.1.3.7 b)
V_MIN = 0.25                        # m/s (4.1.1.3.6)
LAUSHEY_K = 3.1                     # d50 = V^2/(3.1*g), metrico (4.1.1.3.7 c)
G_LAUSHEY = 9.8                     # m/s2; SOLO para Laushey (M6). Ver la nota.

RIESGO_ADMISIBLE = {                # Tabla N 02, num. 3.6
    "quebrada_importante": {"R": 0.30, "n": 25},   # -> TR = 71 anios
    "quebrada_menor":      {"R": 0.35, "n": 15},   # -> TR = 35 anios
}
# TR = 1 / (1 - (1-R)**(1/n))       # sin piso normativo

MANNING = {                         # Tabla N 09: (n_min, n_max)
    "metal_corrugado_dren_aguas_lluvias": (0.021, 0.030),
    "concreto_tubo_recto":                (0.010, 0.013),
    "madera_duelas":                      (0.010, 0.014),
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

# ================= constantes_fisicas.py (NO es [N]: ver la nota) ==========
G = 9.81                            # m/s2; gravedad generica: M4 y todo lo demas

# ================= HDS-5 (FHWA) 3a ed., abril 2012 =========================
# Apendice A, Tabla A.1, pag. A.8
KU_SI = 1.811                       # q* = KU*Q/(A*D**0.5). Imperial: 1.0 (MAT-O19)
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
# D_MAX ya NO es una constante [N] de este anexo: los topes 2.70 / 2.10 /
# 1.50 son de CATALOGO, no de norma de producto. La marca "VERIFICAR" que
# llevaban se resolvio EN CONTRA de la atribucion (DIS-HR-D-MAX, corregida
# en I2): A760 Tabla 1 tabula 100-3600 mm, M 170M Tablas 1-5 cubre
# 300-3600 mm (y su Sec. 7.2 preve diseños mayores); M 294-11 esta en
# normas/ desde N2 como TRADUCCION NO OFICIAL y su serie (1.1.1, 7.2.1) SI
# termina en 1500 mm: el tope del HDPE coincide con ella, sin firma, y sigue
# siendo de catalogo por la misma razon que los otros dos. Viven como adopcion [A]
# en criterios_adoptados 'D_max_catalogo', con advertencia obligatoria.
# (T-4, INF-3.3.1) DESDE T-4 el tope es el de la SERIE de la norma de producto
# ('D_max_norma_producto' [C]: 2.70 / 3.60 / 1.50 m; en concreto, el ultimo
# diametro con diseño estandar de M 170M) y, en TMC, el mayor
# diametro estandar de la corrugacion adoptada (2.10 m con 68 x 13 mm);
# 'D_max_catalogo' queda opcional, sin valor, y solo puede BAJAR el tope.
# Sin tope, el solver puede converger a un diametro inexistente.
# Superado el tope: devolver "material descartado por diametro requerido"
# -- descarte ADOPTADO, no normativo.

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
    "hdpe":     0.30,               # m, clave a subrasante (508.07/508.08,
                                    # pag. impresa 984)
    "concreto": None,               # EG-2013 no lo fija para este material;
    "tmc":      None,               # la cobertura minima es de AASHTO LRFD
                                    # 12.6.6.3 / Tabla 12.6.6.3-1, via el
                                    # criterio 'cobertura_minima_aashto'
                                    # (DIS-HR-H-RELLENO-MIN, corregida en I2)
}
SUBSECCION = {"concreto_simple": "505", "concreto_reforzado": "506",
              "tmc": "507", "hdpe": "508"}
SECCION_CABEZALES = "503"           # concreto estructural (+504 acero)

# ================= Manual de Puentes (RD 041-2016-MTC/14) ==================
SOBRECARGA_TRASDOS_H_EQ = 0.60      # m; PISO del num. 2.4.2.2, pag. impresa
                                    # 102 ("no menor que la equivalente a
                                    # 0.60 m"), condicional a trafico a
                                    # distancia <= H/2. El h_eq de diseño es
                                    # max(piso, Tabla AASHTO 3.11.6.4-1/-2
                                    # por altura y orientacion) -- ver la
                                    # correccion de 9.2 (DIS-HR-H-EQ, I2;
                                    # esta linea citaba el numeral falso
                                    # 2.1.4.3.9)
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

> **Corregido (`INF-5.1.11`, `INF-5.1.14`, T-0, 2026-11-11).** Tres cosas de este anexo no coincidían con el código que dice describir, y las tres se corrigen aquí porque quien lea la hoja sin leer el código programaría con ellas. **(1) Las claves de Manning.** El anexo escribía `"metal_corrugado"` y `"concreto_recto"`; ninguna de las dos existe. `constantes_normativas.MANNING` se deriva de la transcripción completa de la Tabla Nº 09 (`TABLA_09_FILAS`) y sus claves nombran la **fila**: `"metal_corrugado_dren_aguas_lluvias"` (0.021, 0.030) —la tabla tiene además `"metal_corrugado_subdren"` (0.017, 0.021), que no es la del TMC de cruce— y `"concreto_tubo_recto"` (0.010, 0.013) —además de `"concreto_afinado"` (0.011, 0.014)—. La clave larga no es adorno: con la corta no se sabía cuál de las dos filas de cada material se estaba leyendo. **(2) La gravedad son DOS constantes y este anexo traía una.** Decía `G = 9.8` a secas. En el código hay `constantes_fisicas.G = 9.81` m/s², la aceleración estándar, que usan M4 (tirante crítico, control de salida, perfil de lámina) y todo lo demás; y `constantes_normativas.G_LAUSHEY = 9.8` m/s², que usa **solo** M6 en la fórmula de d₅₀ de la Fase 6. **(3) Por qué son dos, dicho una sola vez** (era `INF-5.1.14`: «declaradas, pero sin unificar la explicación»): el 9.8 es el valor de g que el propio Manual escribe —en sus num. 3.12.5 y 4.1.1.5.4 b.2.4), ver la nota de la Fase 6—, y la fórmula de Laushey es del Manual: se evalúa con la g del Manual para que el d₅₀ sea el que el Manual daría. El 9.81 es una constante física universal y **no es `[N]`**: por eso vive en `constantes_fisicas.py` y no en este anexo de constantes normativas, donde aparece solo para que no se confunda con la otra. Se mantienen separadas **a propósito** —unificarlas en 9.81 movería el d₅₀ de Laushey un 0.1 % respecto del que la fuente produce; unificarlas en 9.8 metería en HDS-5 una gravedad que HDS-5 no usa— y con nombres distintos, para que una obra no tenga dos valores de «g» conviviendo sin declararlo. La diferencia entre ambas en cualquier resultado es del orden del 0.1 %.

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
- **Tope superior de diámetro obligatorio por material** — de catálogo `[A]` (`'D_max_catalogo'`, §3.2), no de norma. Superado el tope, el material se descarta con mensaje explícito y rótulo de catálogo. El HDPE (~1.50 m) es el crítico. *Corregido en T-4 (`INF-3.3.1`): el tope es el de la serie de la norma de producto o el de la corrugación adoptada, y el mensaje de descarte nombra cuál; el rótulo de catálogo queda para la disponibilidad que el proyectista declare.*
- **Q(y/D) no es monótona** cerca de sección llena (máximo en y/D ≈ 0.938). Al topar en 0.75 se evita la zona, pero el solver debe manejar el caso "sin solución" → siguiente diámetro.
- **M4 necesita tirante crítico:** Q²T/(gA³) = 1, segundo Brent sobre θ.
- **Unidades del control de salida:** 19.63 en SI, no 29 (corregido desde 19.62; ver la nota de unidades de §4.3). Test unitario obligatorio.
- **El n de HDPE es un rango, no un valor.** Un valor puntual rompe la regla de doble n y subestima velocidad y socavación.
- Cada verificación devuelve el **booleano y el numeral que la sustenta**.
- M11 imprime los criterios usados y, al final, los pendientes que no deben citarse en la memoria.
