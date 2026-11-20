# Censo de lo pendiente en la app (consultor Fable, 2026-11-20, sólo lectura)

Encargado por la sesión `claude/jolly-clarke-qojnbj` sobre la rama `claude/cool-euler-tpoj7o`
(punta `075420d`), por el objetivo del dueño: «que no quede nada implementable pendiente».
Recorrió: las 334 fichas de `docs/decisiones_diferidas.md`; los 37 sitios de
`MetodoNoEvaluableError`; `ALCANCE_DECLARADO`; los `DIFERIDO_*` de M8; los 28 criterios con
`valor=None`; `SIN_CONSUMIDOR_Y_SIN_MEDIDA`; el manifiesto §2/§7/§8; la hoja de ruta v8, y la GUI
y la CLI. «Verificado» = leído por el consultor en el PDF (página impresa y PDF); «registro» = cita
ya registrada en el repositorio, no releída.

En curso cuando se hizo el censo (no se proponen): VE-4a (T7B-07), VE-4b (T1-04), VE-4c
(T7B-01), VE-4d (T7B-02), VE-4e (VE3-21), VE-4f (M8, 3.6.1.2.6a; cubre también VE3-11 y T3-10),
VE-4g (M6). Planeados: el muro que no cede (T7B-14) y el cabezal paralelo en un marco (T7A-03).
Aviso: la Ec. (10.4) rechaza también el marco (`M6_proteccion.py:794`, «for circular
culverts»); hay que confirmar que VE-4g lo cubre.

Clases: (A) implementable ya; (B) necesita decisión del dueño; (C) depende de un dato o un
documento externo; (D) fuera de alcance razonable.

## 1. Prioridad alta: cobertura de diseño

| # | Id | Qué falta | Clase | Norma | Esfuerzo / módulos |
|---|---|---|---|---|---|
| 1 | T5-07, `ALCANCE_DECLARADO.armado_seccion_marco`, `M8.DIFERIDO_MARCO`, `DIFERIDO_EMPUJE_LATERAL_MARCO`; T3-06 | Análisis y armado del pórtico del marco (losas, muros, tabique): flexión, cortante, fisuración, mínimos y empuje lateral. Es el hueco mayor: la Fase 8 de la v8 manda el «diseño completo por AASHTO LRFD Sección 5» y la Familia C sale sin acero | A, con tres decisiones B menores | Verificado. AASHTO 12.11.1, pág. 12-68 (PDF 1706); 12.11.5.1, pág. 12-73 (PDF 1711): «All sections shall be designed for the applicable factored loads… Shear in culverts shall be investigated in conformance with Article 5.12.7.3»; 12.11.5.3.1: mínimos de 5.6.3.3 y 5.10.6; 12.11.4: fisuración por 5.6.7; 3.11.7 (PDF 206): «a 50 percent reduction may be used» | 3–4 sesiones. `M8_estructural`, `modelos` (`GeometriaMarco`), `servicio` (Fase 8), `M11`, criterios. Después de VE-4f |
| 2 | T8-01 (3), T8-07, nota de la Fase 6, `M6:794/812/833/2099`, T6-02 | Poza de enrocado (HEC-14 10.1), Figura 10.3 (TW sobre el rango de la Ec. 10.4), delantal de sección rectangular, y la caída cuando gobierna la pendiente máxima o se agota la Tabla 5.2 (HEC-14 Cap. 11) | A (10.1, Fig. 10.3, marco); B (caída del Cap. 11) | Verificado. HEC-14 Cap. 10, pág. 10-1 (PDF 202) | 2 sesiones, +1 con el Cap. 11. `M6_proteccion`, `normativa/tablas`. Después de VE-4g. Los Caps. 7–9 son D |
| 3 | T7B-04, `M9:7336`, `N_cq_N_gammaq_meyerhof` | Capacidad portante: reducción por talud y factores de forma y de profundidad | A | Verificado. AASHTO 10.6.3.1.2c, pág. 10-74 (PDF 1363): «shall be determined using a reduction coefficient (RCBC)…» (Tablas 10.6.3.1.2c-1 y -2) | 1–1.5 sesiones. `M9_cabezal`, `normativa/tablas`, criterios |
| 4 | T7B-06, `M9:6582/6737/6948` | Empuje sísmico fuera del dominio de Mononobe-Okabe, cuña sobre trasdós inclinado, cuña sin máximo interior | A (cuña de tanteo sísmica); C (GLE como resultado declarado) | Verificado. AASHTO C11.6.5.3: «A11.3.3, or a Coulomb trial wedge analysis should be used»; A11.3.3, pág. 11-149 (PDF 1618) | 1.5–2 sesiones. `M9_cabezal` |
| 5 | VE3-15, `M9:6911` | Sismo con agua en el plano de empuje y `relleno_muy_abierto`: falta la presión hidrodinámica | C (fuente) | Verificado. AASHTO C11.6.5.3 (PDF 1501): «an additional force component due to hydrodynamic effects should be added… (see Kramer, 1996)… Westergaard». La norma la nombra y no da la fórmula | 0.5 sesión cuando esté la fuente. `M9_cabezal` |
| 6 | Fase 0-bis de la v8; `Mw_licuefaccion`, `demanda_sismica_licuefaccion` (sin consumidor) | Evaluación de licuefacción | B + C | Verificado. AASHTO 10.5.4.2, pág. 10-34 (PDF 1323): «A liquefaction assessment shall be conducted for Seismic Zones 3 and 4 if both…»; E.050 38.5.1, pág. 52: Seed e Idriss / NCEER, sin imprimir sus ecuaciones | (a) resultado declarado del EMS con bloqueo de expediente: 1 sesión (recomendado; E.050 38.3 lo asigna al responsable del EMS), o (b) calculadora CSR/CRR: 2–3 sesiones y exige la fuente |
| 7 | T7A-02 (3) | Caja receptora de la Familia B (Lámina 02-A): no está en el catálogo de embocaduras | B + C | Las Tablas A.1 y C.2 del HDS-5 no traen el drop inlet; su hidráulica es de HEC-22, que no está en Normas | Con HEC-22: 1.5 sesiones. `M9.embocadura_del_punto`, `M4`, criterios |
| 8 | Fase 11 de la v8, entregables 8 y 9 | Metrados (concreto, acero, excavación, enrocado, conducto, geotextil) referidos a EG-2013 y el cuadro de compatibilidad rasante–alcantarilla | A | v8 Fase 11, ítems 8 y 9 | 1.5–2 sesiones. Módulo nuevo, `M11`, `cli`, `gui/app` |
| 9 | VE3-14 (H-13), T7B-08 | El alero se dimensiona con la pantalla y no por secciones | A | AASHTO Sección 5 | 1 sesión. `M9_cabezal` |
| 10 | T7C-09 (2)(3) | Cabezal de gravedad ciclópeo: cuerpo bajo sismo y zapata como voladizo de concreto simple | A | E.060 22.10.2.2, pág. 195 (registro) | 0.5–1 sesión. `M9_cabezal` |

## 2. Prioridad media: hidrología e hidráulica

| # | Id | Qué falta | Clase | Norma / recomendación | Esfuerzo / módulos |
|---|---|---|---|---|---|
| 11 | T1-03 | V8 no pide su caudal a la Fase 1-bis (con cuenca, estación y `TR_evento_extremo`); el declarado sigue ganando | A | v8 fila V8 | 0.5–1. `servicio`. Después de VE-4d |
| 12 | T1-07 | Tc por Izzard y por onda cinemática (Tabla Nº 05) y el punto fijo tc ↔ I | A | Manual de Hidrología, Tabla Nº 05 (PDF 42) | 1. `MH_hidrologia`, cargador de cuencas, contrato |
| 13 | T1-01 | Cinco distribuciones (Log Normal 3P, Gamma 2P/3P, Log Pearson III, Log Gumbel) y la prueba χ² | B | Verificado. Manual pág. 31 (PDF 34): χ² con k intervalos, sin fijar k. Recomendación: momentos / factor de frecuencia como [C] (Chow) y k de Sturges como [A] | 2. `MH_hidrologia` |
| 14 | T1-05, ec. (17) | Puerta para recibir K, m, n de una IDF regional | A (B la ponderación de C) | Manual 3.8 / ec. 17 | 0.5. `MH_hidrologia` |
| 15 | T1-02 | FEN `dos_poblaciones` | C/D | Sin fuente con el procedimiento | No hacer salvo fuente y serie larga |
| 16 | `MH:456/1877/2184`, VE2-F | Cuencas ≥ 770 km² y Pd ≤ Po | D | — | No hacer |
| 17 | EA-02, VE3-08 | Resalto por momentum; V2 con la velocidad aguas abajo del resalto | A | HEC-14 Cap. 6 (PDF 69–70) | 2. `M4_control`, `M5` |
| 18 | EXT-2-01, T3-05 | V6 nunca acepta multicelda: falta el dato `arrastre_de_solidos` por punto | A (puerta) | Verificado. Manual 4.1.1.3.4 (PDF 75) | 0.5. `M5`, `servicio.CLAVES_EXTERNAS` |
| 19 | T2-06, C10-02 | Segundo indicador de sedimentación (n del conducto frente al del cauce) | A (puerta); B (regla) | HDS-5 5.3.3, pág. 5.11. Recomendación: indicador, no veredicto | 0.5. `M5` |
| 20 | T4-06, v8 §3.1 | Rama de selva alta, programada e inactiva | A | Verificado. Manual 4.1.1.3.7 a) (PDF 82): «Se recomienda utilizar, en zonas de selva alta… TMC Ф 48"» | 0.5. `datos_sitio`, `M2.catalogo` |
| 21 | T9-01 | Cuneta trapezoidal para región > 3000 mm/año | A | Verificado. Tabla Nº 34 (PDF 181–182) | 0.5. `M10_espaciamiento` |
| 22 | T6-01, T7A-06 | El control de salida con la longitud entre cabezales | B | Sin numeral; efecto de centímetros. Recomendación: pasada de refinamiento con aviso | 1. `MD`, `M7`, `servicio` |
| 23 | T5-03 | La plancha del TMC que elige la Fase 8 no vuelve a la geometría | A | Coherencia interna | 0.5–1. `M2`, `M8`, `MD` |
| 24 | VE2-G, T4-02 | Con serie inglesa, V9 compara el diámetro de cálculo y no el designado; concreto de 2850–3600 mm | B menor | AASHTO M 170M Tabla 6. Recomendación: comparar por el designado | 0.5. `M5`, `M2` |
| 25 | T2-01 (1) | Pendiente adversa del barril | D | — | No hacer |
| 26 | T7V-01, T8-08, T3-08 | Escalón en HW/D = 1.2; tirante de borde fuera de las figuras; V7 del marco sin peso propio | D, D, B | Recomendación: con el ítem 1, contar el DC del marco con γ mínimo | 0.25. `M5` |
| 27 | EXT-3-02 | V1/V2 sólo con el TW gobernante | D | Equivalencia demostrada | No hacer |

## 3. Prioridad media-baja: cabezal y protección

| # | Id | Qué falta | Clase | Recomendación |
|---|---|---|---|---|
| 28 | T7B-11 | Orientación del muro y distancia al borde por punto | A | Dos claves por punto. 0.5, `M9`, `servicio` |
| 29 | T7C-10 | `CUANTIA_MIN_MURO` sigue [N] cuando su ámbito la hace [N→] | A | 0.5–1. `constantes_normativas` → `criterios_adoptados` |
| 30 | T8-03 | Zampeado, uña y dentellón | C/B | Plano tipo del dueño o regla [A]. 0.5 |
| 31 | T8-05 | Filtro granular bajo el enrocado | C | Con HEC-11: 1 sesión |
| 32 | T7B-09, VE3-05 (3) | Dentellón con pasivo, mejoramiento, pilotes | B/D | No hacer salvo petición |
| 33 | T7B-03 | Cabezal con el vano y la restricción del barril | D | Modelo actual del lado seguro |
| 34 | VE3-13, T11-03 (2), VE3-08 | Fila NF sin iterar el peralte; delta de rasante con V4; progresión que sólo empeora; G1 fuera del bucle | A menor | 1 sesión conjunta. `M9`, `MD` |
| 35 | T9-02, T9-09 | Iterar tc con la longitud de cuneta; cuneta en terraplén | B / D | Sólo si se pide; lo segundo, fuera |
| 36 | T4-04, T4-09 | Umbral de cloruros; agresividad para acero corrugado | C | E.060 no da el umbral |

## 4. Software, GUI y CLI (A, sin norma)

| # | Id | Qué falta | Esfuerzo / archivos |
|---|---|---|---|
| 37 | EB-06, T11-10 | La ventana emergente sin campo de nota | 0.5; `gui/ventana_normativa.py` |
| 38 | UI3-01, UI4-01 | Panel de la pestaña 2 sin scroll; botón PDF cortado a 900 px | 0.5; `gui/app.py`, `gui/componentes.py` |
| 39 | UI5-01 (c)(d) | Temporales fijos al exportar; fallo del PDF como traza de Python | 0.5; `M11_reporte`, `cli.py` |
| 40 | T6-04 | `bombeo`, `peralte`, `S_conducto` sin campo ni bandera | 0.5; `src/sesion.py`, `gui/app.py`, `cli.py` |
| 41 | EXT-10, R4 | Sin editor de [S] en la ventana | B: no hacer salvo que el dueño cambie R4 |
| 42 | UI1-02 | Editor tipado sólo con la primera tabla | 0.5; `src/editores.py` |
| 43 | T4-09 | Claves de durabilidad fuera de `variables_entrada`, la ayuda y el pre-vuelo | 0.5 |
| 44 | T8-11 | Avisos de techo de transcripción en la Fase 6 | 0.5; `dominios`, `servicio` |
| 45 | C8-02 | Estado del expediente con las discrepancias abiertas; lista de corridas para comparar | 1; `M11`, `gui/app.py` |
| 46 | VE2-02, VE2-A, VE1-01 | Ids `FH.*` en el índice; fila fija de doble n en M11; `D` con dos decimales | 0.5; `indice_formulas`, `M11` |
| 47 | T10-02, T11-06, I4-01 | Veinte fundamentos sin ejercitar en el índice; chequeo dimensional de M6 a M10 | 1; fixtures y tests |
| 48 | SIS-F-01, C09-01 | La integración continua no corre los tests de ventana | 0.25 |
| 49 | UI5-01 (a)(b), UI2-01 (b) | Campos de la pestaña 1 que no invalidan el informe; el hijo del PDF recalcula | B: que el hijo lea la corrida embebida. 1.5 |

## 5. Criterios con `valor=None` (28)

- **Elección o dato de ensayo, no pendiente de código:** `homogeneidad_serie_fen`, `TW_receptor`,
  `riesgo_admisible_propietario`, `v_max_concreto_eleccion`, `D_max_catalogo`,
  `margen_estacional_nf_v7_m`, `pendiente_relleno_trasdos_i`, `friccion_muro_suelo_delta`,
  `fraccion_fin_remanso_canal`, `phi_relleno_trasdos`, `c_phi_fundacion`,
  `peso_especifico_saturado_relleno_kn_m3`, `exposicion_quimica_ems`,
  `categoria_refuerzo_aashto`, `clase_exposicion_fisuracion_cabezal`,
  `h_eq_bajo_altura_tabulada`, `h_eq_banda_intermedia_borde`, `perfil_hdpe_fabricante` y las
  dos de edición que rige.
- **Esconden un método (en VE-4):** `remanso_derecho_via`, `TR_evento_extremo`,
  `umbral_no_colapso_evento_extremo`, `metodo_estabilidad_global`.
- **Sin consumidor, pendiente real:** `Mw_licuefaccion` y `demanda_sismica_licuefaccion` (ítem
  6); `capacidad_portante_adm` (duplica `q_adm_kpa`: retirarlo o darle consumidor con el ítem
  3); `clase_sitio` y `PERFIL_SUELO_PRESUNTO` (que la clase medida valide la fila de `F_pga`);
  `N_cq_N_gammaq_meyerhof` (lo sustituye el ítem 3).

## 6. Manifiesto y discrepancias

- §8: 0 campos por transcribir; seis citas sin firma (cinco de `AASHTO_M294_TRAD`, C, y
  `HDS5_SI_1985.EC4B#K`).
- §7: dos discrepancias abiertas (`DIS-AASHTO-GAMMA-EV-12.6.1`, `DIS-LUZ-DENOMINACION`),
  posturas declaradas sin código pendiente.
- Hoja de ruta que sigue mal (sólo el dueño la corrige): VE3-19 (aviso de máximos repetidos en la
  Fase 1-bis), T7A-08 (§9.3 rotula E.050 como [N] para el cabezal vial), SIS-A-16 (Sec. 1.5 sin
  dos validaciones cruzadas de M0), Fase 11 (qué entregables produce la app).

## 7. Plan de lotes (después de integrar VE-4a a VE-4g)

- **M8** (secuencial): 1 → 23 → 26.
- **M9** (secuencial, un solo agente): muro que no cede → 4 → 3 → 9 → 10 → 28 → 29; el cabezal
  paralelo (T7A-03) al final porque toca también `M4`.
- **M6:** 2; después 30 y 31 si llegan los documentos.
- **MH:** 12 + 14 → 13 → 11.
- **M4/M5:** 17 → 18 → 19 → 24.
- **Catálogo y Fase 10:** 20 y 21.
- **Metrados:** 8.
- **GUI/CLI:** 37, 38, 40, 42; 39 y 46; 43 a 45 y 47 a 48.
- **Integrador al final:** 22, 34, documentos, línea base, conteos.

Total estimado: 28–34 sesiones.

## 8. Decisiones del dueño

1. Licuefacción (6): resultado declarado del EMS (recomendado) o calculadora.
2. Distribuciones y χ² (13): momentos / factor de frecuencia [C] y k de Sturges [A].
3. Pórtico (1): empuje lateral en reposo (3.11.5.2), la reducción del 50 % de 3.11.7 sólo para el
   momento positivo de la losa superior, cantos separados de losa y pared.
4. Caída (HEC-14 Cap. 11) y caja receptora (2 y 7): si entran al alcance.
5. Longitud entre cabezales en el control de salida (22).
6. Ítems 24, 26, 30, 41 y 49.
7. Reescribir o no la historia de git para quitar los PDF (T12-01); no es de la app.

## 9. Lo que no se cierra con código

- **EMS por punto:** φ, c y γ de fundación y del relleno, peso saturado, capacidad portante o
  `q_n` en roca, clase de sitio, SPT, M_w, sulfatos y cloruros, lecho de salida (D50, D84, IP),
  pasante para el geotextil, talud de corte. Todas las puertas existen salvo la de licuefacción.
- **Estudio hidrológico:** series SENAMHI reales, cuencas, años FEN, caudal del evento extremo,
  región pluvial en año FEN, n del cauce natural, arrastre de sólidos por punto.
- **Topografía y trazo:** cota de fondo levantada, sección del receptor, sección del cauce de
  aproximación (V5), inicio de tramos de cuneta, velocidad de diseño e IMDA, ancho del derecho de
  vía.
- **Fabricante:** perfil del HDPE, costura empernada del TMC, concreto de 2850–3600 mm.
- **Documentos para Normas:** ejemplar legible de AASHTO M 170M o ASTM C76M; AASHTO M 294
  original; HEC-11, HEC-22 y Kramer (1996) o un manual FHWA con Westergaard; Chow o Aparicio;
  AASHTO M 288 y el manual de California; DS 034-2008-MTC; M 259 / M 273 sólo para el marco
  prefabricado.
- **Propietario:** riesgo y vida útil, TR y umbral del evento extremo, aceptación escrita de la
  reducción de k_h y del muro que cede, η_R del cabezal, edición que rige.
- **Validación externa:** la tabla HY-8 contra la app (INF-3.2.2); un ejemplo publicado de carga
  viva con la edición 2013 o posterior (VE3-04); un ejemplo de paso directo; el expediente vial del
  caso patrón de M10.
