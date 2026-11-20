# Dictamen del verificador normativo — velocidad máxima TMC / HDPE (T-4 punto 3, opción A elegida por el dueño)

Verificado contra los PDF de `/home/user/andy-rba30/normas/normas/` (2026-11-11). Re-verifica tú cada cita antes de escribirla.

## WSDOT Hydraulics Manual (`HydraulicsManual.pdf`) — edición «M 23-03.12 April 2026» (portada, PDF 1)

- §8-6 «Abrasion», «Table 8-4 Pipe Abrasion Levels», págs. impresas 8-27 y 8-28 = PDF 242 y 243. Columnas: Abrasion Level /
  General Site Characteristics / Recommended Invert Protection.
  - Non-abrasive: «Little or no bed load · Slope less than 1% · Velocities less than 3 ft/s».
  - Low abrasive: «Minor bed loads of sands, silts, and clays · Slopes 1%–2% · Velocities less than 6 ft/s» → metal: «an additional
    gage thickness may be specified if existing pipes in the vicinity show susceptibility to abrasion, or any of the protective
    treatments specified in Section 8-5.3.1».
  - Moderately abrasive: «Moderate bed loads of sands and gravels, with stone sizes up to about 3 inches · Slopes 2%–4% ·
    Velocities from 6 to 15 ft/s» → «Metal pipe thickness shall be increased one or two standard gages…»; «Thermoplastic pipe may
    be used without additional treatments.»
  - Severely abrasive: «Heavy bed loads of sands, gravel, and rocks, with stone sizes up to 12 inches or larger · Slopes steeper
    than 4% · Velocities greater than 15 ft/s» → «Metal pipe thickness shall be increased at least two standard gages, or the pipe
    invert shall be lined with concrete.» La fila severa NO nombra «thermoplastic»: imprime «Sacrificial metal pipe … shall not be
    used in this condition» (probable errata; es inferencia, no texto).
  - Nota de la tabla (8-27): «The abrasion level descriptions are intended to serve as general guidance only; not all of the
    criteria listed for a particular abrasion level need to be present to justify placing a site at that level.»
- **En ningún sitio dice que 15 ft/s sea techo de velocidad para metal**: para metal prescribe remedio, no prohibición. Y el
  «shall» de +1 o 2 calibres ya rige entre 6 y 15 ft/s en sitio moderadamente abrasivo.
- §8-3.3 «Thermoplastic Pipe: General», pág. 8-13 = PDF 228: «…because thermoplastic pipe cannot be structurally reinforced, it
  shall not be used for severely abrasive conditions as described in Table 8-4.» La prohibición está atada al NIVEL, no a la
  velocidad sola. Citar la prohibición SÓLO del §8-3.3; la Tabla 8-4 sólo por el umbral.
- §3-3.5 «Velocities in Culverts: General», pág. 3-11 = PDF 76: «Culverts that produce velocities in the range of 3 to 10 feet per
  second (ft/s) tend to have fewer operational problems…»; «Velocities less than 3 ft/s or more than 10 ft/s must be discussed
  with the RHE…»; «If velocities exceed about 10 ft/s, abrasion due to bed load movement through the culvert and erosion
  downstream of the outlet can increase significantly. … Corrugated metal culverts may be designed with extra thickness…».
  10 ft/s = 3.048 m/s es umbral de consulta, no prohibición.

## Manual MTC de Hidrología, Hidráulica y Drenaje

- §4.1.1.3.7 «Consideraciones para el diseño» (impresa 77 / PDF 80). e) Abrasión (impresa 81 / PDF 84): cualitativo, sin valor.
  f) Corrosión (81–82 / 84–85): zonas costeras, TMC con recubrimiento asfáltico «muchas veces no es suficiente». g) Seguridad y
  vida útil (82–83 / 85–86): con «velocidades excesivas con presencia de elementos abrasivos…, aguas salinas o ácidas… no es
  recomendable el uso de alcantarillas metálicas… se recomienda… concreto de alta resistencia o tubos de alta densidad».
- Tabla N° 10 (§4.1.1.3.6, impresa 76 / PDF 79): concreto 3.0–6.0; ladrillo con concreto 2.5–3.5; mampostería 2.0. NO incluye
  metal ni plástico. Ningún techo numérico para TMC en el manual.

## Otras fuentes

- AASHTO LRFD 9.ª, 12.6.9 «Corrosive and Abrasive Conditions» y C12.6.9 (impresa 12-24 / PDF 1662): niveles FHWA de abrasión —
  «Level 2 … velocities of 5.0 ft/s or less», «Level 3 … between 5.0 ft/s and 15.0 ft/s», «Level 4—Severe … velocities exceeding
  15.0 ft/s»— como nivel (carga de fondo Y velocidad), no techo. Segunda fuente del corte de 15 ft/s.
- ASTM A796 §21.1 (PDF 6): «…Where additional resistance to abrasion is required, consider the use of invert paving as well.» Sin
  límite. AASHTO M 36 §1.2, HDS-5 §2.3.4 a. (2.17–2.18 / PDF 79–80): cualitativo, sin límite.
- Avisos de ejemplar: M 36 es escaneo sin texto; el «ASTM A760» es traducción con capa de texto cifrada (leer por imagen);
  A796 tiene la capa de texto duplicada.

## Recomendación (dentro de la opción A)

- `v_max_tmc` → **[A]**, valor **4.572 m/s** (15 ft/s exactos; no mueve nada). Ventana recomendada **(3.048, 4.572)**:
  piso = 10 ft/s de WSDOT §3-3.5 (umbral de consulta por abrasión), techo = 15 ft/s (corte moderately/severely de la Tabla 8-4 y
  de LRFD C12.6.9). El techo 4.6 que sugería la cadena NO tiene respaldo (15.09 ft/s; reintroduce el redondeo que MAT-O14
  corrigió y entra en la banda donde la fuente exige ≥ 2 calibres o invert de concreto). 3.0 sólo como redondeo declarado.
  Comprueba que la ventana nueva no rompa a quien use el piso actual `V_MIN` (barrido PF-3, tests, guía de perfil).
- Redacción: «Ninguna fuente consultada fija velocidad máxima para TMC. El proyecto adopta como techo de V3 el corte entre los
  niveles "moderately" y "severely abrasive" de la Tabla 8-4 (15 ft/s = 4.572 m/s), que es una clasificación de abrasión
  dependiente también de la carga de fondo y la pendiente, no un límite de velocidad. V3 no sustituye la protección del invert
  que esa tabla y ASTM A796 §21.1 piden según el nivel del sitio.» Dejar dicho el corte de 6 ft/s (1.829 m/s).
  QUITAR de la ficha: «límite conservador» y «por encima de este valor exige mayor calibre…» (falso tal como está: el «shall»
  de calibre rige desde 6 ft/s).
- `v_max_hdpe` → sigue **[C]** 4.572 pero: sustituir «techo duro: por encima de 15 ft/s… prohibido» por la frase literal del
  §8-3.3 + Interpretación declarada («el proyecto toma el criterio de velocidad por sí solo como suficiente para clasificar el
  sitio como severamente abrasivo, lectura conservadora que la fuente permite —nota de la Tabla 8-4— pero no impone»).
- Declarar la asimetría [A]/[C] con el mismo número (al termoplástico la fuente le asocia «shall not be used»; al metal, un remedio).
- Coherencia con el sitio (Bajo Piura, costa, salinidad, NF alto): MTC §4.1.1.3.7 f) y g) pesan contra el TMC; eso lo recoge
  la matriz de durabilidad de T-4 punto 4, no V3. El nivel de abrasión del sitio puede quedar como entrada [S] opcional de esa
  matriz (`abrasion`, categoría), sin sustituir a `v_max_tmc`.
