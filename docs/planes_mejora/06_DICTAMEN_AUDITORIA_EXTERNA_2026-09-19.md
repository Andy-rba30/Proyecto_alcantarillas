# Dictamen sobre la auditoría externa del 2026-09-19 y sus dos planes

**Objeto:** `Informe_auditoria_alcantarillas.md` (22 hallazgos: A-01..03, N-01..04, M-01..07,
V-01..06, G-01..03), `2026-09-19-correccion-alcantarillas.md` (cadena P00–P19) y
`Plan_prompts_mejoras_alcantarillas.md` (cadena E00–E25 y rutas H/G/S/D/B), los tres
producidos por otra IA sobre un ZIP del repositorio.

**Árbol revisado:** `origin/main` en `5196dd2`. Es el árbol de la auditoría más tres
PDF subidos el 2026-09-18 (`Manual.de.Carreteras.DG-2018.pdf`,
`Manual_de_Seguridad_Vial_2017.pdf`, `MANUAL DE DISPOSITIVOS DE CONTROL DE TRÁNSITO…pdf`)
y menos uno borrado en HEAD (`Reglamento Nacional de Gestion de Infraestructura Vial.pdf`).
El último commit de **código** es `b3e3e62` (2026-09-14): nada del registro normativo
conoce todavía los PDF nuevos.

**Método.** Todo lo que sigue se midió ejecutando el código, en solo lectura, con los
módulos reales importados como los importa `conftest.py` (`src/` en `sys.path`,
nombres planos). Ocho verificadores reprodujeron los 22 hallazgos agrupados por
módulo; ocho lentes buscaron lo que la auditoría no miró (numérica, estado global,
rendimiento, GUI con ventana real, suite, PDF, contratos, constitución); dos
evaluadores revisaron los planes; cada hallazgo nuevo de severidad alta o media pasó
por un refutador independiente. Los scripts y salidas literales están en el
scratchpad de la sesión; aquí se citan los números.

**Línea base medida:** `python3 -m pytest -q` sobre `5196dd2` → **1974 passed, 8
skipped en 79.6 s** (1982 recolectados), que es exactamente la fila «PyMuPDF sí ·
Ventana Tk no» de la tabla de CLAUDE.md. La auditoría declaró la suite «no
ejecutada» por falta de `pytest`; el coste real de ejecutarla es de 80 segundos, y
esa omisión explica la mitad de sus puntos ciegos.

---

## 1. Análisis crítico de la auditoría

### 1.1 Precisión de los hallazgos: 18 confirmados, 3 parciales, 0 refutados

La auditoría es **muy buena en los hechos**: todos los números que publica se
reproducen dígito a dígito con los módulos reales (M-01: los seis valores de su
tabla; M-02: HW 0.530324827; M-03: las cinco cifras; M-04: 1.129037883 vs
1.107921425; M-06: KR/KC/KAE; V-02: −9.903915917 m; V-05: 4.639080910 m). Donde
falla es en el **contexto**: no conocía la constitución del proyecto (CLAUDE.md, la
hoja de ruta v8 como fuente de verdad, la matriz de 8 conflictos,
`decisiones_diferidas.md`, el tracker) y no ejecutó nada. Por eso sus severidades y
sus correcciones necesitan ajuste en más de la mitad de los casos.

| ID | Veredicto | Severidad (auditoría → reevaluada) | Lo que acierta | Lo que yerra u omite |
|---|---|---|---|---|
| A-01 | Confirmado | alta → **alta** | `Informe` no captura criterios efectivos, procedencias, usos ni huellas; los 4 exportadores leen estado global al exportar (medido: 39 llamadas; `exportar_csv` está limpio); `_USADOS` nunca se vacía (27 heredados, no 28). | Omite la agravante: la memoria imprime «esta corrida usó OTRO» con la fila `1.7675 \| 1.75` mientras la memoria del punto usa 1.75 (`espesor 0.592 m`) — **la memoria afirma algo falso**. La premisa «proceso == corrida» está escrita como decisión (SIS-B-22) y es verdadera para la CLI: el defecto es de la GUI y de todo consumidor que reutilice el proceso. Su `ContextoCorrida` es correcto, pero P01 lo acopla a `Proyecto` y versionado de esquema (big-bang innecesario). |
| A-02 | Confirmado | alta → **alta** | `restaurar_sesion` es aditiva; los `externos` de la GUI solo se pisan si vienen. | Dos agravantes medibles: la mezcla **se persiste** (`estado_de_sesion()` de B guarda las claves de A) y una clave restaurada sin procedencia **hereda la procedencia de A**. SIS-A-18 (cerrado) solo probó ida y vuelta de una sesión. La corrección obvia reabre SIS-B-22 («`limpiar_valores_dinamicos` no tiene llamador a propósito»): abrir sesión ES el caso de uso que faltaba. |
| A-03 | Confirmado | alta → **alta** | Mecanismo y corrección (duplicados con `TOL_UMBRAL_NORMATIVO`, que es la que ya usa `_misma_seccion`). | «Cinco visitas» porque abortó: el bucle es sin término (50 escalones en 0.00 s). Vale también no adyacente (ciclo de longitud 2) y casi-duplicado (5e-10). «Recorrer por índice» choca con la API por valor fijada por tres tests. `MD.disenar_material` no tiene guardia de progreso: cualquier regresión futura cuelga la GUI sin `ErrorProyecto`. |
| N-01 | Parcial | alta → **media** | La ventana «citada o vigente, para las siete a la vez» trata igual una norma aprobada por RD del MTC (derogada) que cinco normas técnicas de EE.UU. | Parafrasea mal la ficha: dice «expediente EN CURSO» (régimen transitorio), no «no hay norma». El proyecto **ya registra** la derogación (`fuentes.MP.nota`, T1, RD 19-2018-MTC/14). La contradicción interna fuerte que no vio: el propio MP-2016 ancla AASHTO LRFD 2014 (PDF 44) mientras el registro cita la 9.ª de 2020 y la ficha dice «cuya edición no la manda nadie». |
| N-02 | Confirmado | media → **media** | sha1 y páginas exactos; `DG2018 = _ausente(...)`; Seguridad Vial y Dispositivos sin registrar. | Causa temporal: los PDF entraron cuatro días después del último commit de código; el proyecto tiene el procedimiento hecho dos veces (N1, N2). Defecto estructural nuevo: **no existe guardia «PDF presente sin `Fuente`»** (T17 solo vigila el sentido inverso). DG-2018 §304.07.01 remite al RNGIV (DS 034-2008-MTC), que HEAD borró. Tres textos hoy mienten (`SIN_FUNDAMENTO` F5.V5, ficha de `talud_terraplen`). |
| N-03 | Confirmado | media → **media (latente)** | `_NORMA_PRODUCTO` solo por material; M 170M §1.1 y Nota 1 verificados. | Hoy no llega a ninguna salida: los 4 sitios que la imprimen van bajo `informe.dimensionado` y un marco no cierra (se detiene en `cota_coronacion_canal` y luego en `TR_evento_extremo`). La norma de cajón prefabricado sería M 259/M 273 (LRFD 12.4.2.4 y 12.11.1, verificados), ausentes. El proyecto ya decidió «vaciado in situ» en `ruta_familia_c.md` §14.1; es un resto de C7. `Material.norma_producto` es `str` obligatorio: tocar el modelo y tres formateadores. |
| N-04 | Confirmado | media → **media** | La v8 rotula V5 «[N] DG-2018 + Ley 29338» sin numeral; §304.07 no enuncia condición hidráulica alguna. | El código **ya no** trata V5 como [N]: el criterio es [A] de expediente y `SIN_FUNDAMENTO` F5.V5 lo censa. La contradicción viva es v8 (línea 545) ↔ código: se reporta contra la hoja. Lo aprovechable de DG-2018 que no vio: Tabla 304.09 (anchos por clase) y «+5.00 m del borde de las obras de drenaje» dan un **piso [N]** al ancho del derecho de vía. VC1-02: en Familia C V5 no se difiere, se sustituye. |
| M-01 | Confirmado | alta → **alta** | Todo lo medible; la memoria es internamente contradictoria («manda TW: la salida está ahogada» junto a V1 [OK] con y/D = 0.135). | El código **sigue a la v8** (§1.3 «V4 y V4b, las únicas que dependen del TW»; §4.3 «Relevancia»; filas V1/V2): por la regla de fuente de verdad, la corrección empieza por la v8, con MC-HHD págs. 76-77 y 79 y HDS-5 3.18 (verificadas) decidiendo. Caso inverso que no vio: en pendiente suave con salida libre (y_n > y_c) la velocidad de salida a y_c supera a `V_erosion` (1.508 vs 1.184 m/s, −21 %): M6 **subestima** d50 ahí. `H_O_CONDICION_APLICACION` afirma «M5 no cambia»: falso. `ahogado_por_TW` no llega al JSON ni a la GUI (SIS-B-18). Ningún test cubre `h_o_fuera_de_rango` ni «NO DEBE USARSE». |
| M-02 | Confirmado | alta → **media** | Aceptación con `h_o_fuera_de_rango=True`; la bandera no tiene lector fuera de M11; subir de diámetro empeora HW/D (medido 0.589 → 0.526). | Es una **decisión registrada** (NOR-HDS-05 «Cerrado parcial», v8 §4.3 «el aviso se emite igual», paquete I1 escrito en `H_O_CONDICION_APLICACION`): bloquear es revertirla y exige reabrir la ficha y la v8. El corredor de referencia **ya está en esa condición** (B-01: control salida, HW/D 0.395, `fuera_rango=True`) y lo fijan tres tests. «Prohíbe» sobrelee «should not be used»; la frase «backwater calculations (Section 3.5) should be used…» está **elidida sin marcar** en v8 §4.3 y `H_O_CONDICION_TEXTO`. En el caso medido el barril es supercrítico y el HW aproximado es conservador. Agravante nueva: el `PasoDeMemoria` ya emite `NO_CUMPLE` mientras MD acepta — memoria y pipeline dicen cosas distintas (la divergencia que SIS-A-07 prohíbe). |
| M-03 | Confirmado | alta → **alta (latente)** | Cinco cifras a nueve decimales; +113.8 %; cambio de control. | Viola la **regla vinculante #3** del propio proyecto (`ruta_familia_c.md` §6), y R9 afirma una cobertura que no existe (solo `_caudal_por_barril`). La memoria sale irreproducible (Q = 9.0 impreso con un y_n que solo da V·A = 3.000). V6 (`cumple = celdas == 1`) impide hoy que un multicelda se **acepte**: el defecto vive en la traza y en el motivo de rechazo. HDS-5 §5.4.3 (PDF 151) respalda el reparto y no está en el registro. `ResultadoHidraulico.Q` tiene 3 lectores que lo imprimen como caudal del punto: **Q sigue siendo total** y `Q_celda`/`n_celdas` son campos nuevos con default (6 constructores en tests). |
| M-04 | Confirmado | media → **media** | Extremo móvil; solo Forma 1; propiedad de punto medio. | Dirección: el error es **conservador** (+1.9 %). La implementación **no es una recta** (incrementos 20.8 → 5.6 mm por paso de q*): el criterio [C] dice «interpolación lineal» y la memoria imprime «recta» calculando una curva. Un test **fija el extremo móvil con rel=1e-12** (`test_la_interpolacion_reproduce_la_recta_entre_los_dos_extremos`): test escrito contra el comportamiento actual. La ambigüedad nace en v8 §4.2 («el valor en q* = 3.5» sin decir con qué H_c). Vale también para el marco (+38.4 mm). |
| M-05 | Confirmado | media → **media (sin consumidor)** | Reproducción exacta; cita literal del 11.10.10.3. | Lo presenta como nuevo y el proyecto **ya lo tenía verificado** (`auditoria_normativa.md` R95-031/H-13, ALTA) sin que entrara nunca al tracker. Omite la pregunta que lo decide: §11.10.2 restringe 11.10.3–11.10.10 al cortante **en el plano**; un cabezal en voladizo trabaja perpendicular (§11.10.1 → §11.12). «Pedir hm/lm y ρh» no es ejecutable (`GeometriaCabezal` sin lm; Vu sale de `diseno_flexion_corte`, `NotImplementedError`). |
| M-06 | Confirmado | media → **baja** | Aritmética exacta; diagnóstico estructural correcto. | El caso i = 20° **no es declarable** (ventana 0–10°, rechazado) y con el k_h = 0.5 real M-O no tiene solución para i ≥ 5° (φ = 30) o i = 10° (φ = 35). Dentro de las ventanas: −6.25 % a +7.23 %. La base mixta es una **decisión declarada** (docstrings de `empujes_trasdos` y `ka_rankine`; v8 §9.2 «Ka = tan²(45 − φ/2)»): se reporta contra la v8 con fuente primaria MP 2.4.4.1.5.3 (Coulomb, pág. impresa 136, verificada). La sobrecarga también va con Rankine. `demanda_sismica_cabezal` ya es homogénea. |
| M-07 | Confirmado | media → **baja** | `estable=True` con E1–E3; docstring promete cinco; conjunto vacío → True. | La partición E1–E3 / E4–E5 es **deliberada** (docstring) y calca E.050 39.13.6 a)/b). El código no usa `all()` sino `not verificaciones_incumplidas`. E1 no es del 39.13.6 sino del Art. 21; existe E6 (`verificar_excentricidad_sismica`). Dos tests pinean `estable` con tres ítems. Sin lector productivo. |
| V-01 | Parcial | alta → **media** | Hechos exactos (70/36/21; 9/4; sin API de escritura; `cadena_sismica()` usa PGA = 0.50). | **Confunde hardcoding indebido con falta de mecanismo multi-obra.** Que los [S] del corredor vivan en `datos_sitio.py` con trazabilidad es el diseño constitucional (v8 §0.7, taxonomía [S], `auditoria_y_ruta_despliegue_v9.md` A.0). Su tabla mezcla cinco cosas distintas. Zona y Z no gobiernan ningún cálculo. «Todo a None + `Proyecto`» rompe `_verificar_nivel`, `test_nivel_medido`, `test_cierre_perfil` y las líneas base. Radio real medido: la corrida de perfil **no lee ningún** dato de sitio; la de expediente solo `PGA_roca_B`; mueren 18 tests en 5 archivos (0 en los cuatro que el plan teme); `DatoSitio` no tiene `nivel`. |
| V-02 | Confirmado | alta → **media** (alta en constitución) | −50 aceptado con procedencia «proviene de la fila». | También de **tipo**: `'texto'`, `True`, `[1,2]` se declaran igual y el consumidor lanza `TypeError` fuera de `ErrorProyecto`. `--declarar ke_entrada=-50` produce `HW_salida_m = −7.668` con el punto dimensionado y 0 incumplidas. Mitigaciones que existen: la ventana prellena la celda y la memoria rotula «TANTEO». Su «resolvedor» choca con la separación proponer/declarar fijada por test; pero **C5-02 ya define la migración** de `ke_entrada` a clave de fila: pasa de «limpieza» a defecto. |
| V-03 | Confirmado | alta → **alta** | Asimetría exacta con la rama rectangular. | `True` es peor: pared de **1.0 m** (D_ext 2.9 m, cota clave 44.0). `0` se devuelve como `int`. El predicado correcto ya existe (`criterios_adoptados._es_real`); la duplicación del `isinstance` en dos ramas es la causa. |
| V-04 | Confirmado | media → **media** | Ambas pruebas literales. | `Derivada` solo está protegida en la **cara** de la ventana; `Z_E030` está protegido por accidente (por ser [S]). `test_la_tabla_de_recubrimiento…` afirma en su docstring que el modo impide editar: falso. Solo hay 2 Derivadas y 1 consumidor (M9): la guardia es barata. Z(zona) ejecutable exige transcribir la Tabla N.º 1 de E.030. |
| V-05 | Confirmado | media → **media** | Ventana en prosa no evaluada; tirante ×5. | La no-evaluación de lo simbólico es **deliberada y fijada por test**; lo no previsto es un dict con ventanas numéricas escritas como prosa. `n='0.03'` → `TypeError`; `n=True` → 1; clave desconocida ignorada. Son 14 criterios con valor en la misma situación. |
| V-06 | Confirmado | media → **media** | Las tres excepciones exactas; tumban la corrida en CLI (con `--luz`). | Omite el caso peor: fila con errata o clave `'r'` se **ignora en silencio** y la memoria imprime «DECLARADOS POR EL PROPIETARIO» con los valores por defecto. `bool` pasa como número. |
| G-01 | Confirmado | media → **media** | Lista vs cadena entre paneles. | El docstring de `_valor_tecleado` dice «misma regla que la pestaña»: falso desde C8. Alcanza tuplas y dicts; un literal mal cerrado lo acepta la ventana y lo rechaza el panel. «Parser compartido CLI + GUI» choca con un test que fija la divergencia CLI/GUI a propósito (`ast.literal_eval('1,5')` = tupla): el parser compartido es **GUI–GUI**. |
| G-02 | Confirmado | media → **media** | Números exactos (3 diferidas, 0 reales). | El defecto mayor es el **resumen**: la GUI dice «Etapas bloqueadas: 12» y la CLI, sobre el mismo `Informe`, 1. Su snippet falla con `Informe.bloqueos()` (tuplas). Contar en la GUI reproduce la asimetría CLI/GUI (SIS-E-01): la cuenta va en `cli.Informe`. `criterios_bloqueantes` también mezcla. |
| G-03 | Parcial | baja → **baja** | 6/8 fichas vacías; «dos resoluciones»; 47.7 %; Tabla N.º 02 sin columna TR; pág. 179. | Fricción: 47.7 % es sobre el término, 9.6 % sobre H (CP-8); la mezcla de bases está también en v8 línea 527. «Escenarios independientes» contradice MAT-D1/CP-2: la corrección es de texto. La columna «TR de diseño» existe en la tabla derivada de la v8 §2.2, no en la del Manual. NOR-HID-02 figura «Cerrado» y `NUMERAL_FASE_10` (lo que imprime la memoria) sigue en 178: cierre incompleto en 4 sitios + v8 + manifiesto. Las 6 fichas vacías son una **decisión** (docstring de `FichaDeClaveExterna`: «prefiere un hueco declarado a una frase inventada»), discutible pero no un olvido. |

### 1.2 Los cuatro errores sistemáticos de la auditoría

1. **No leyó la constitución.** Cinco correcciones piden cambiar código que hace
   exactamente lo que la v8 prescribe (M-01, M-02, M-04, M-05, M-06) y una contradice
   el diseño (V-01). La regla del proyecto es: el defecto se reporta **contra la hoja
   de ruta primero** y la fuente primaria decide, verificada en el PDF. La
   verificación existe en los cinco casos (HDS-5 3.18/3.24, MC-HHD 76-79, E.060
   11.10.10.3, MP 2.4.4.1.5.3): las correcciones son legítimas, pero empiezan por un
   commit documental, no por M4.
2. **No ejecutó nada**, y por eso no vio los tres lugares donde **la propia suite
   defiende el defecto**: `test_la_interpolacion_reproduce_la_recta…` (M-04, rel=1e-12),
   la línea base de Familia C (B-01 congelado en la condición de M-02, regenerable
   desde el código con un comando) y el test de ventana real que teclea `'1'` para
   `n_celdas_cajon` y afirma que C-01 no dimensiona. Tampoco vio que M-03 es latente
   (V6 lo contiene), que N-03 no llega a ninguna salida y que M-05/06/07 no tienen
   consumidor productivo.
3. **No cruzó con el tracker ni con `decisiones_diferidas.md`.** M-02 (NOR-HDS-05),
   V-02 (C5-02), A-02 (SIS-B-22/SIS-A-18) y M-05 (R95-031) ya tenían estado o
   argumento. Cuatro de sus correcciones «obvias» reabren una decisión escrita.
4. **Anclas por número de línea de otro árbol** en los 22 hallazgos, y prefijos de ID
   (A-, N-, M-, V-, G-) que **colisionan** con los de la auditoría de Sistema
   (`SIS-A-02` ≠ `A-02`). Al darlos de alta hay que renombrarlos (`EXT-`).

### 1.3 Puntos ciegos: lo que la auditoría no vio

Treinta y un hallazgos nuevos, todos reproducidos. Se listan por dimensión, con la
severidad que les asigno.

**Cálculo y variables dependientes**

- **PC-01 (alta)** Un par `(n_min, n_max)` **invertido pero dentro de la ventana**
  se acepta en caliente: `_verificar_sensibilidad` valida cada extremo por separado
  y `Material` no exige el orden. Con `n_manning_hdpe=(0.013, 0.010)` todas las
  velocidades de M3→M5→M6 cambian al lado no conservador (y/D 0.665 → 0.559;
  `V_erosion` 2.89 → 2.10; `V_sedimentacion` 2.23 → 2.74) sin excepción. Refutación
  independiente: **confirmado**, y peor de lo dicho. Con Q = 1.167 m³/s y S = 0.020
  el par nominal descarta el HDPE en todos los diámetros por V3 (`V_erosion` 5.11 >
  4.572) y el par invertido **aprueba Ø 0.90** con V1/V2/V3 en verde y un d50 de
  Laushey que baja de 0.860 a 0.443 m (exige que el espesor HDPE esté declarado,
  como lo estará cuando entre el material). Y un escalar (`--declarar
  n_manning_hdpe=0.012`, o `[0.012]`) no revienta solo en el punto HDPE: tumba la
  corrida **entera** de la CLI con traza, para todos los puntos, porque
  `M2.materiales_candidatos` construye el catálogo de los tres materiales; la GUI lo
  mostraría como fallo de programa. Ninguna regla ni ficha justifica no validar el
  orden: el «no validamos el orden» de `progresion_de_cajon` es un argumento de dos
  dimensiones que no se traslada a un par escalar que la v8 (línea 427) presupone
  ordenado.
- **PC-02 (media)** `ke_entrada` es [C] sin ventana ni dominio: `--declarar
  ke_entrada=-0.5` pasa la CLI entera, baja el HW de salida, **cambia el control
  gobernante** y puede pasar V4b de «no cumple» a «cumple» (HW/D 1.336 → 1.140).
  `perdida_carga` no valida signo (H negativo). Mismo hueco en `v_max_tmc` y
  `v_max_hdpe`. Es el reverso de V-02 por la vía `--declarar`, sin procedencia.
- **PC-03 (media)** MAT-D10 descarta el material entero por HWi/D ≤ 0 en Q chico ×
  S grande (con D = 0.90: S ≥ 0.38 para Q = 0.05 m³/s, S ≥ 0.54 para 0.10): un cruce
  trivialmente factible sale como `DisenoNoFactibleError` definitivo en vez de un
  vacío declarable.
- **PC-04 (alta, parte de M-01)** En pendiente suave con salida libre M6 recibe
  `V_erosion` (régimen uniforme) cuando la velocidad de salida a y_c es mayor: la
  auditoría solo vio la dirección conservadora.
- **PC-05 (baja)** `M3._validar_parametros` y `M4._validar_positivo` escriben
  `if x <= 0` (permeable a NaN) en vez de la plantilla MAT-D13 que CLAUDE.md
  declara obligatoria: NaN por la API interna sale como `ValueError` de `brentq`;
  `control_salida` devuelve HW = nan/inf con TW o L no finitos. No alcanzable desde
  producción (M0 y `_numero_externo` filtran), pero es asimetría de contrato.
- **PC-06 (baja)** El bracket rectangular `(0, H)` usa el perímetro de lámina libre
  en y = H, de modo que `tirante_normal` devuelve un «tirante normal» en la banda
  (Q_lleno, Q_manning(H)) = (7.70, 9.64) m³/s para el marco 2.00×1.50, donde
  físicamente el conducto va a presión. V1 rechaza, pero la traza publica un régimen
  que no existe.

**Estado global y arquitectura**

- **PC-07 (alta)** `cli._geometria_json` tiene la clave `"cota_entrada_origen"`
  **duplicada en el mismo literal `dict`**: la segunda gana y publica la regla que
  gobierna *ahora* en el registro global (`ca.valor_si_declarado`), no la que produjo
  la cota impresa al lado. Es A-01 en un campo por punto. Ningún test ni lector lo
  cubre (desde `25acb9e`).
- **PC-08 (media)** **Identidad doble de módulos**: `src/` no es paquete y cinco
  archivos insertan `src/` en `sys.path`; `import src.criterios_adoptados` crea un
  segundo módulo con su propio `_OVERRIDES`/`_USADOS`. Demostrado en vivo durante
  esta revisión: `catalogo(CONCRETO, RECTANGULAR)` importado por `src.modulos` devuelve
  en silencio `seccion_eg2013='506'` y la norma del tubo (el enum `FormaSeccion` es
  otro objeto), mientras por import plano exige los criterios del cajón y da
  `'503 + 504'`. Los prompts P01–P19 escriben `src/modulos/...`.
- **PC-09 (media)** El registro de usos nunca se vacía y el `Informe` no lo captura,
  pero la fuga está **acotada**: dos corridas en el mismo proceso difieren en 98
  campos, todos bajo `/criterios/usados` y `/datos_sitio/usados`; fuera de ahí los
  JSON son idénticos byte a byte. Los 79 escritores de `_USADOS` pasan por tres
  funciones (`ca.valor`, `ca.valor_si_declarado`, `ds.valor`): la instantánea no
  exige enhebrar ningún parámetro por M2–M10. La suite ya hace la foto **a mano**
  (27 accesos a `_USADOS` en 9 archivos, 70 líneas de limpieza).
- **PC-10 (baja)** `import cli` cuesta 0.8–1.0 s: weasyprint se importa siempre
  (357–414 ms) aunque no haya `--pdf`, scipy.optimize 230–313 ms,
  `variables_entrada` parsea el AST de 13 módulos al importar (123 ms). El registro
  normativo se construye cinco veces (inocuo, ≈2 ms).

**Rendimiento** (la auditoría lo declaró «no medido»)

- **PC-11 (alta)** El único cuello real es el **PDF**: 11 s y 287 MB para 4 puntos,
  69 s y 1.29 GB para 40 (31 páginas por punto), y corre **en el hilo de Tk**. El
  cálculo es despreciable: 2.1–2.4 ms por punto, `cli.correr` de 1000 puntos en
  2.1 s. La congelación que un usuario sufre está en exportar, no en calcular; el
  plan P (§A P1) y E06/E07 apuntan al sitio equivocado.
- **PC-12 (media)** La memoria HTML pesa 67 KB por punto y el 44 % de los bytes son
  nodos de texto repetidos ≥ 10 veces (el párrafo del umbral de 6.0 m ×80, las dos
  citas de la definición ×80, discrepancias ×90). Es lineal con constante alta; el
  pico de RAM al construirla es 4× su tamaño.

**GUI** (verificado con ventana real: `apt-get install python3-tk` para 3.12 + `xvfb-run`;
los 4 tests de ventana corren)

- **PC-13 (alta)** La GUI **no puede declarar un entero**: `'1'` → `1.0` en los dos
  parsers, y `M2` exige `isinstance(int)` para `n_celdas_cajon`; desde la ventana el
  marco nunca pasa de ahí, por la CLI (`ast.literal_eval`) sí. El único test de
  ventana real teclea `'1'` y **afirma que C-01 no dimensiona**: fija el defecto.
- **PC-14 (media)** 32 criterios numéricos sin rango numérico aceptan **cadenas**
  (`'0,30 m'`, `'cero'`) y el panel confirma; `'1,200'` vale 1.2 en las tres puertas;
  el validador al escribir de la emergente acepta `nan` con ámbar y el botón lo
  rechaza después (dos veredictos para la misma tecla).
- **PC-15 (media)** Tras una **corrida fallida** la ventana sigue presentando el
  informe anterior como vigente (pestañas 3 y 4, barra «Ejecutado (…)», cuatro
  exportadores activos), y el nombre del proyecto se lee al exportar, no al correr.
- **PC-16 (media)** `cargar_sesion` aplica la sesión **a medias** si el archivo está
  deformado (`"externos": null` → `AttributeError` fuera del manejador, a stderr, sin
  diálogo, con proyecto y CSV ya pisados); `null` se muestra como el texto `'None'`.
- **PC-17 (baja)** Accesibilidad: el motivo de un botón apagado vive solo en el
  tooltip; la rueda no funciona en X11/macOS (`<MouseWheel>` solo, `delta/120`);
  sin Escape ni atajos.

**Suite**

- **PC-18 (alta)** La línea base de Familia C **congela M-02** (B-01: control salida,
  HW/D 0.40, memoria «NO DEBE USARSE» y V1 [OK]) y **no puede ver M-01 ni M-03**:
  todos los TW son ≤ 0.3 < D y `punto_cajon.py` fija `n_celdas_cajon = 1` con el
  comentario «con N = 1 daría el mismo número». El oráculo se regenera desde el
  código con un comando.
- **PC-19 (alta)** `test_M4_control.py` fija con rel=1e-12 el extremo móvil de la
  transición (M-04): test contra el comportamiento actual, sin test de punto medio.
- **PC-20 (media)** 34 tests de 15 archivos dependen de las declaraciones sintéticas
  de `conftest.py`; 4 de `test_cli` prueban las Fases 6/7/8 sobre un stub HDPE que
  el producto **nunca puede dimensionar**. Los otros 1948 no cambian; la línea base
  (subproceso sin conftest) sí representa el producto.
- **PC-21 (media)** `test_anticipo` cuenta ocurrencias con `inspect.getsource`
  (los comentarios cuentan): el mutante que borra un uso real sigue verde. Mismo
  patrón que S16 pasó al AST.
- **PC-22 (baja)** Cuatro tests suman 27 s de los 80; el skip de `test_MD` es un test
  que nunca puede correr; 16 funciones públicas de `src/modulos` sin referencia
  textual en tests.

**Registro normativo**

- **PC-23 (alta, de proceso)** No hay guardia «PDF presente sin `Fuente`»; los tres
  PDF nuevos son invisibles al registro; HEAD borró el RNGIV al que DG-2018 remite.
- **PC-24 (baja)** V1 y V2 nacen de frases «se recomienda» (RECOMENDACION, verificado)
  y la v8 las rotula [N]; el «umbral duro» es una adopción sin criterio; la v8 cita
  «pág. 75» y es 76-77.
- **PC-25 (media)** Frase elidida sin marcar en v8 §4.3 y `H_O_CONDICION_TEXTO`
  (regla «ningún texto literal se transcribe dos veces»).
- **PC-26 (media)** `edicion_que_rige_el_expediente` mezcla norma legal (MP, RD
  derogada) con normas técnicas de EE.UU. en una ventana cerrada «siete a la vez».

**Contratos**

- **PC-27 (media)** El «estado de verificación» que P01 quiere «formalizar» **ya
  existe en tres capas incompatibles**: `Verificacion.cumple: bool` (20 constructores,
  13 lectores), `TipoDeVeredicto` con DIFERIDO y SIN_VEREDICTO pero adosado al
  `PasoDeMemoria`, y `cli.Bloqueo.diferido_por_alcance` fuera de `modelos.py`.
  «Fuera de dominio» es una bandera sin lector de compuerta; «no aplica» no existe.
- **PC-28 (baja)** `MD.disenar_punto` degrada un `DatoFaltanteError` de todos los
  candidatos a `DisenoNoFactibleError` con `campo=None`: el tablero pierde la columna
  que falta.

**Proceso**

- **PC-29 (alta, de proceso)** Hallazgos «ajustados» de las rondas de refutación
  R95/R48 sin fila en el tracker (al menos H-13/R95-031, ALTA). Los temarios
  registran 19 + 20 ítems «cerrados en la corrida original, antes del corte por
  límite de créditos» y 76 + 28 con `origen_del_cierre` nulo: hace falta un cruce
  sistemático `auditoria_normativa.md` ↔ hoja `Hallazgos`.
- **PC-30 (baja)** Cierre incompleto de NOR-HID-02: la cita está en 179 y lo que la
  memoria imprime (`NUMERAL_FASE_10`, `Espaciamiento.numeral`, ficha de
  `long_max_cuneta`, v8 línea 821) sigue en 178.
- **PC-31 (baja)** `Registro` construido cinco veces y cuatro instancias distintas
  (`ca._registro`, `modelos._registro_normativo`, `constantes_normativas._reg`,
  `M11._reg_M11`): sin daño, sin singleton.

---

## 2. Evaluación del plan propuesto

### 2.1 Cadena de corrección P00–P19

**Veredicto:** el orden general (contratos → datos → módulos → orquestación →
reportes → GUI → verificación) es defendible como *idea*, pero el plan pone un
**big-bang arquitectónico (P01–P04) delante de correcciones locales, verificables y
urgentes**, y varias de sus fases contradicen reglas escritas del repositorio que
harían que un ejecutor las implementara mal.

Problemas de orden y riesgos ocultos, medidos:

1. **P01 es cuatro cambios en uno** (`Proyecto`, `ContextoCorrida`, estados de
   verificación, `Q_total/Q_celda`, `EstabilidadCabezal`). Hoy **no existe** ninguna
   clase `Proyecto`/`Contexto`; `Verificacion` tiene 20 constructores y 13 lectores;
   `ResultadoHidraulico` 1 constructor de producción y 6 en tests. Los estados que
   pide ya existen en tres capas (PC-27): «formalizar» sin decidir primero cuál de
   las tres gobierna produce una cuarta. A-01/A-02 se cierran con un cambio
   acotado (vaciar al entrar en `correr`, fotografiar al salir, 39 sitios de
   exportación) que no necesita `Proyecto`.
2. **P02/P03 rompen la constitución antes de enmendarla.** «Los datos requeridos de
   un proyecto nuevo deben empezar pendientes» choca con v8 §0.7, con la taxonomía
   [S] y con la tercera regla de `_verificar_nivel` (criterio de salida del nivel de
   perfil). El radio medido de P02 es pequeño (18 tests en 5 archivos; la corrida de
   perfil no lee ningún [S]) pero exige un campo `nivel` en `DatoSitio` que no existe.
   El radio de P03 está **en los tests, no en producción**: 28 de 44 archivos
   importan `criterios_adoptados`, 157 accesos a `ca.CRITERIOS`, 84 a
   `establecer_valor_dinamico`, sobre un archivo de 6973 líneas. Un objeto `Proyecto`
   con «sitio, adopciones y procedencias» duplica lo que `DatoSitio`, `Criterio` y
   `Procedencia` ya modelan.
3. **P00 pide tests de regresión antes de corregir.** La regla 6 de CLAUDE.md lo
   permite solo si son tests de **fallo esperado** (aceptación), nunca tests que
   copien la salida actual; el plan no lo distingue, y la línea base de Familia C
   (PC-18) es exactamente un oráculo copiado que se regenera desde el código. La
   suite no usa `xfail` en ningún sitio (0 ocurrencias): la forma correcta de P00 es
   `pytest.mark.xfail(strict=True)` con la expectativa del invariante o de la fuente
   (punto medio = media de los extremos con H_c(Q_lo); N=3/Q=9 ≡ N=1/Q=3;
   V_salida = Q/A_llena; espesor ≤ 0 → `DatoInvalidoError`), que pasa a verde en la
   fase que lo cierra.
4. **P04 «parser compartido por CLI, panel y emergente»** choca con un test que fija
   la divergencia CLI/GUI a propósito; el parser compartido es GUI–GUI. «Resolvedor
   que obtiene el valor de la tabla» choca con proponer/declarar (test) pero
   coincide con C5-02: hay que ejecutar C5-02, no inventar un resolvedor genérico.
5. **P07 «escenarios realmente independientes»** contradice MAT-D1 y el fixture CP-2
   (misma R, dos n): la corrección de F4.MANNING es solo de texto.
6. **P08 «bloquear la aceptación» por h_o** revierte NOR-HDS-05 y la v8 §4.3, y
   pone rojos tres tests del corredor de referencia. Convertir la bandera en una
   `Verificacion` con `cumple=False` haría que MD recorra el catálogo y termine en
   `DisenoNoFactibleError` (subir D solo empeora HW/D). La vía del proyecto es
   `Bloqueo` «método no evaluable», diferible en perfil y no en expediente.
7. **P09 cambia el significado de `ResultadoHidraulico.Q`**: sus tres lectores lo
   imprimen como caudal del punto; Q debe seguir siendo total y `Q_celda`/`n_celdas`
   entrar con default. V6 es hoy la guardia que contiene M-03: cambiarla y el
   contrato van en el mismo commit.
8. **Doble toque del mismo archivo**: P03 y P12a (criterios), P10 y P12b (M5). La
   regla del repositorio es un cluster entero por commit; esto invita a dos commits
   parciales sobre el mismo objeto.
9. **P12** no dice que registrar una fuente es una sesión con molde (N1/N2):
   paginación medida, marca de vigencia T1, regeneración de los tres documentos
   generados con sello. Su «matriz requisito-aplicabilidad-responsable-evidencia» no
   tiene forma en el esquema `Fuente/Cita/Ausencia/Discrepancia`.
10. **P13** «pedir geometría y ρh» no es ejecutable; y omite la decisión previa de
    aplicabilidad del régimen en el plano (§11.10.2).
11. **P16/P17** y el «cálculo en segundo plano» del backlog atacan una congelación
    que no existe (10–30 ms por corrida) e ignoran la real (PDF, 11–69 s). Un hilo
    con el estado global actual es peligroso; el subproceso no.
12. **Convenciones que ningún prompt menciona**: el mensaje de commit (CLAUDE.md
    escribe `fase1(Sn)`, y los últimos 30 commits usan `<área>(<sesión>): …`, por
    ejemplo `normativa(N2)`, `cierre(PD)`: conviene fijar una serie nueva, p. ej.
    `ext(En)`), tracker `.xlsx` por ID, regenerar `manifiesto_citas.md`,
    `manifiesto_registro_normativo.md`, `trazabilidad.csv` e `indice_formulas.md` con
    sello (y el sello exige el par de la suite medido sobre `origin/main`, que no se
    conoce antes de fusionar), el par `passed + skipped = collected`, la fusión a
    `main` como cierre (el plan dice literalmente «no empujar a un remoto»), y que los
    imports son planos (`modulos.X`), no `src.modulos.X` (PC-08). Dos añadidos de
    orden: P12 y P12a no dependen de `Proyecto` y deben ir **antes** de P03, con
    P12a fundido en P03 y P12b en P10; y `informe_json` tiene que exportar el bloque
    h_o (hoy 0 ocurrencias en `cli.py`) antes de que P08 lo convierta en estado.

**Fases que faltan:** enmiendas a la v8 como paso previo; registro de la DG-2018 y
guardia «PDF presente»; PDF fuera del hilo; cruce de temarios con el tracker; alta de
los 22 hallazgos con prefijo propio.

**Fases que sobran o se difieren:** `Proyecto` y versionado de esquema (P01–P03),
que son requisito de producto (multi-obra) y no corrección; P19 como «auditoría de
lo acumulado» sin criterio de aceptación más allá de la suite.

### 2.2 Cadena de evolución E00–E25 y rutas H/G/S/D/B

- **Se escribió sin leer el árbol.** Los 60 prompts mandan «ejecuta únicamente Exx
  del `Plan_prompts_mejoras_alcantarillas.md`», un archivo que no existe con ese
  nombre, y citan un backlog (`Plan_estrategico_alcantarillas_v2.md`) que no está en
  el repositorio. E00 solo habilita la ruta si «la cadena P00–P19 está acreditada»:
  ejecutado literalmente, bloquea la ruta E para siempre o invita al ejecutor a
  acreditarla sin evidencia. Hay que reescribirlo como «medir la base real» (HEAD,
  par de la suite, tracker por ID, fichas de `decisiones_diferidas.md` que la ruta
  va a pisar: SIS-A-18, SIS-B-05, NOR-HDS-05).
- **Duplica lo que existe o está planificado por el proyecto**: el anticipo
  pre-corrida (`src/anticipo.py`) vs E13; la traza «¿de dónde sale este número?»
  (plan G4) vs E18/E21; vigencia (T1) vs E12; export CSV del registro (T3) vs E22;
  la sesión JSON versionada vs E04. `00_LEEME_DICTAMEN.md` ya midió que ~60 % de un
  plan anterior ya existía; aquí pasa lo mismo con la mitad de la ruta E.
- **E01 (servicio de cálculo)** es mecánico y bien acotado: `cli.py` tiene 736
  líneas de orquestación en 27 funciones, 146 de datos externos y 143 de modelo;
  JSON/texto/argparse son adaptadores. Pero exige antes PC-08 (paquete real) y el
  contexto de corrida (paso 4 de la hoja de ruta de abajo), o se extrae el estado
  global con él.
- **E06/E07 (ejecución en segundo plano)** con `_OVERRIDES/_USADOS/_PROCEDENCIAS` de
  módulo no es seguro entre hilos; y el problema que resuelve es el PDF. Un
  subproceso (`cli.py --json`) da aislamiento, progreso y cancelación sin tocar el
  estado global.
- **E09 (medir rendimiento)** llega tarde: esta revisión ya localiza el cuello
  (PC-11/PC-12); la primera optimización es de formato (dedup de la memoria), no
  instrumentación.
- **E15 (escenarios de rugosidad)** debe respetar la regla de doble n de M3 (una
  resolución con n_max, dos velocidades): «cada rugosidad requiere su propia
  solución» contradice MAT-D1 salvo que se defina como escenario de n_max.
- **E03a/E03b/E03c son tres sesiones para un cambio de diez líneas**: el anticipo
  usa 2 atributos de `cli`, la ayuda 5 y el índice de fórmulas 2. Se funden en E03,
  y E03c no puede «regenerar el índice con sello» dentro de la sesión porque el
  sello exige el par medido sobre `origin/main`.
- **E04 (persistencia con revisiones)** parte de una sesión `FORMATO_SESION = 2`
  sin identidad, sin sha1 del CSV, sin corridas y con `open('w')` directo: hace
  falta un formato 3 con migración explícita v2→v3, `informe_json` embebido por
  corrida y escritura temporal + `os.replace`, y cerrar A-02 sin romper el
  contrato de `ResultadoDeRestauracion`.
- **Ruta H (perfil gradualmente variado)**: el paquete I1 escrito en
  `H_O_CONDICION_APLICACION` (piezas 1–5: Ec. 3.7 pág. 3.12, umbrales pág. 3.24,
  Sección 3.5) ya es la especificación de H00; es lo que cierra M-01 y M-02 de una
  vez y merece sesión propia con plan mode, como dice NOR-HDS-05. Dos restricciones
  que el plan no ve: la **regla vinculante #12** de la Familia C (la vía por tirante
  de `Seccion` no puede ganar consumidores desde M3/M4 sin declararlos; un censo AST
  lo vigila), que obliga a integrar en `llenado` vía `geometria_en`; y el conflicto
  #7 (dorados no se fabrican): sin corrida HY-8 aportada por el dueño, el único caso
  patrón legítimo es el límite de flujo uniforme y el balance de energía. La primera
  salida útil no es un HW nuevo sino la **fracción de barril lleno**, que vuelve
  medida la primera condición de h_o. H03 tal como está («adaptar V1/V2/V3 al
  perfil») es vacío o peligroso mientras el paquete diga «M5 no cambia»; M-01
  demuestra que M5 sí cambia, pero eso se decide en la v8 (paso 0), no en H03.
- **Rutas G y B** implican dependencias nuevas (pyproj, shapely, rasterio,
  ifcopenshell) que CLAUDE.md exige consultar **antes**; el CSV no trae coordenadas
  (19 columnas, la única posicional es `progresiva_km`). **S04a** ya está
  especificado por N1 como sesión de cálculo en M8; S03/S04b esperan fuentes que no
  están en `normas/`; D00–D03 sin fuente primaria nueva.
- **Escala**: 60 prompts a «uno por mensaje» sin puertas de valor. Ocho a diez
  sesiones dan el 80 %: E00' (medición real), contexto de corrida, E01+E02 fundidas
  (≈1000 líneas de orquestación, modelo y carga a un módulo plano, con
  reexportaciones para los 21 atributos que usa la GUI y los 6 privados que usan los
  tests), E03 fundida, PDF por subproceso, E10 (editores tipados), E04 v3, E14
  (comparador sobre dos `informe_json`, reutilizando la comparación de
  `test_linea_base`) y H00–H02 como la sesión de NOR-HDS-05.

---

## 3. Propuestas propias

1. **Contexto de corrida por «vaciar y fotografiar», no por objeto `Proyecto`.**
   Los 79 escritores de uso pasan por tres funciones; basta vaciar `_USADOS` al
   entrar en `cli.correr`, capturar al salir un `ContextoCorrida` congelado en
   `modelos.py` (usados, valores efectivos copiados en profundidad, procedencias,
   declarados en caliente, pisados, `csv_sha1` de los **mismos bytes** que leyó M0)
   y hacer que los 39 sitios de exportación lean de ahí. Guardia: ampliar el test AST
   que ya barre M11 («no hace aritmética») a «no llama `ca.`/`ds.`/`_declaracion.`
   salvo lecturas estáticas». Si un día la GUI corre en hilo, el mismo almacén pasa
   a `contextvars` sin tocar M2–M10. Cierra A-01, A-02 (con restauración atómica),
   PC-07 y PC-09, y hace innecesarios los 27 accesos privados de la suite.

2. **Aislamiento y no-bloqueo de la GUI por proceso, no por hilo.** La CLI ya es un
   proceso de un solo uso con `--json`, `--html`, `--pdf`: la GUI puede lanzarla como
   subproceso para calcular y, sobre todo, para exportar PDF (el 100 % de la
   congelación medida). Aislamiento gratis (el estado global es por proceso),
   cancelación = terminar el proceso, progreso por líneas de stdout, y ningún riesgo
   de carrera con `_OVERRIDES`. Es lo que E06/E07 quieren, sin refactorizar el motor,
   y se puede hacer antes que el punto 1.

3. **Contrato de forma por criterio en la puerta única.** V-02 (tipo), V-03, V-05,
   V-06, G-01, PC-01, PC-02, PC-13 y PC-14 son el mismo defecto: `_verificar_criterio`
   valida etiqueta, nivel, finitud y una sensibilidad 2-tupla, pero no la
   **estructura** de un valor (int vs float, dict con campos y ventanas por campo,
   serie de pares sin repetidos, par ordenado, `Derivada` no editable). Un campo
   `Criterio.forma` (o una `sensibilidad` estructurada `{campo: (min, max)}`) validado
   en `establecer_valor_dinamico` cierra los nueve con «el mismo rasero por los tres
   caminos», sin literales nuevos fuera de los tres archivos, y permite que la
   ventana confirme solo lo que M2/M3 van a aceptar. Complemento: un parser GUI–GUI
   único (`gui/componentes.py`) que devuelva `int` para `[+-]?\d+`, conserve la
   divergencia deliberada con la CLI y rechace `'1.200,50'`.

4. **Pruebas de propiedades y mutación medida.** El proyecto ya hizo mutación a mano
   para `nivel`; conviene automatizarla en M3–M5/MD con `mutmut` y escribir con
   `hypothesis` los invariantes que hoy no defiende nadie: Q = V·A con n_max;
   Q_total = N·Q_celda **a través de** MD→M4 (HW(N=3) ≠ HW(N=1)); V_erosion ≥
   V_sedimentacion; continuidad **y linealidad** de la transición; monotonía de HW(Q)
   bajo control de entrada Forma 1; `tirante_normal` = None para Q ≥ Q_lleno en las
   dos formas. Son dependencias de test (como PyMuPDF), con consulta previa por la
   regla de dependencias. Cierra PC-18/19/21 de raíz, porque los oráculos dejan de
   ser la salida actual.

5. **Paquete `src/` real, guardia de identidad e imports perezosos.** Convertir `src/`
   en paquete con un solo nombre, retirar los cinco `sys.path.insert`, y mientras
   tanto un test que rechace `import src.` por AST y compruebe en subproceso que
   ningún módulo vive bajo dos claves de `sys.modules`. Weasyprint y scipy importados
   en el punto de uso y `VARIABLES` perezoso: −0.5 s por proceso (medir con
   `-X importtime`, no estimar). Es prerrequisito de E01 y de cualquier empaquetado.

6. **Deduplicar la memoria HTML sin tocar el cálculo.** Anexo único de citas,
   umbrales y discrepancias con ancla por `cita_id`, y cada punto enlaza; los textos
   siguen saliendo de `Registro.textos_literales()`. Objetivo medible: < 15 KB y
   < 10 páginas por punto; construir por streaming. Con eso el PDF de 40 puntos deja
   de costar 69 s y 1.3 GB.

7. **Tres guardias de proceso**: un test que liste `normas/*.pdf` y exija que cada
   archivo sea `Fuente` presente o figure en un censo `PRESENTES_SIN_REGISTRAR` con
   motivo (mismo recurso que `SIN_CONSUMIDOR_Y_SIN_MEDIDA`); un cruce automatizado de
   los temarios R95/R48 con la hoja `Hallazgos`; y prefijo `EXT-` para los 22
   hallazgos de esta auditoría al darlos de alta.

---

## 4. Veredicto y hoja de ruta consolidada

**Veredicto.** La auditoría acierta en 18 de 22 hallazgos y en todos sus números;
su dictamen («no aprobar como herramienta general de diseño») es correcto, pero por
una razón distinta de la que da: el repositorio **es un expediente** por diseño
(La Unión), y lo que falta para «herramienta general» es un requisito de producto
(multi-obra), no la corrección de un hardcoding. Lo que sí son defectos que aprueban
mal un diseño son M-01, M-03 (latente), V-03, A-03, PC-01 y PC-02, y ninguno exige la
arquitectura P01–P04 para cerrarse. El plan P es un big-bang puesto delante de
correcciones locales; el plan E duplica la mitad del backlog propio y ataca una
congelación que no existe. La hoja de ruta de abajo reordena lo mejor de ambos con lo
medido aquí. Cada paso es **un cluster, un commit, suite verde, tracker actualizado y
documentos generados regenerados con sello**; los tamaños son relativos (S/M/L), no
plazos.

**Paso 0 · Gobernanza y hoja de ruta (documental, S).** Dar de alta los 22 hallazgos
(`EXT-`) y los PC- en el tracker; cruzar R95/R48. Enmendar la v8 con las citas ya
verificadas: §1.3 y §4.1/§4.3 (régimen bajo TW ahogante; frase elidida de la pág.
3.24; estado de HW/D < 0.75), §4.2 (H_c del caudal del extremo), §9.2 (Ka de Coulomb,
MP 2.4.4.1.5.3), §9.4 (11.10.10.2/.3), fila V5 ([N] → requisito jurídico [N] + método
[A] + dato [S]), V1/V2 (deber de verificar [N] + valor [A]), «pág. 75» → 76-77,
178 → 179, fricción 47.7 %/9.6 % en la misma base. Reabrir NOR-HDS-05, C5-02,
SIS-B-22 y NOR-HID-02 con el argumento nuevo. Nada de esto toca código y desbloquea
todo lo demás.

**Paso 1 · Guardias locales sin cambio de contrato (cluster «entradas», M).**
A-03 (duplicados con TOL + guardia de progreso en MD); V-03 (un validador
`_espesor_valido` para las dos ramas, forma MAT-D13); V-06 (forma del mapa en
`_riesgo_del_propietario`, claves desconocidas rechazadas); PC-01 (orden del par en
la guardia y `Material.__post_init__`); PC-02 (`not ke >= 0` en `perdida_carga`;
ventana de tabla para los [C] escalares de perfil); V-04 (rechazo de `Derivada` en
`establecer_valor_dinamico`); V-05 (sensibilidad estructurada por campo; tipo en
`_seccion_declarada`); V-02 (procedencia veraz: `valor_de_la_celda` y «DIFIERE de la
celda», más C5-02); PC-05; PC-28. Tests parametrizados; ningún número de la línea
base se mueve.

**Paso 2 · Multicelda y transición (cluster hidráulico, M).** M-03: `Q_barril` a
`resolver_control` (o el reparto dentro de M4), `Q_celda`/`n_celdas` con default en
`ResultadoHidraulico`, `PasoDeMemoria` del reparto (F3.CELDAS ya existe), cita HDS-5
§5.4.3 al registro, test que mute `Q=Q_barril` → `Q=Q`. M-04: H_c(Q_lo) en Forma 1,
reescribir el test de rel=1e-12, tests de punto medio y linealidad, dorado
1.107921425 m, extremos en la sustitución de F4.CONTROL. PC-06: `Q_lleno` como techo
en las dos formas. Regenerar la línea base declarando archivo por archivo qué se
movió (A-01 en micras) y ensancharla con TW > D y N = 3.

**Paso 3 · Régimen y dominio del método (cluster C06, L).** Con la v8 enmendada:
M4 emite el régimen del barril y la velocidad de salida por HDS-5 3.1.6 como
magnitud con procedencia; V2 compara la velocidad de la sección efectiva (a sección
llena Q/A_llena = 0.0786 m/s en M-01 y falla); V1 a sección llena no cumple (pág.
79); bajo control de salida parcialmente lleno V1/V2 quedan **pendientes** por la vía
`Bloqueo` (diferible en perfil, no en expediente) hasta el perfil de lámina; h_o fuera
de rango → `Bloqueo` «método no evaluable», nunca `Verificacion(cumple=False)`; M6
recibe la velocidad de salida; el bloque h_o entero viaja al JSON y a la GUI
(cerrar la «decisión propia» de SIS-B-18); actualizar B-01 en los tres tests.
Después, en sesión propia con plan mode: el paquete I1 (perfil por paso directo), que
cierra M-01/M-02 de verdad; dorados solo con corrida externa citable (conflicto #7).

**Paso 4 · Contexto de corrida y sesiones (cluster estado, M).** Propuesta 1
completa; PC-07 como caso piloto; `restaurar_sesion(sustituir=True)` con candidato
validado y «Importar decisiones» aparte; `cargar_sesion` valida el esquema entero
antes de tocar un `StringVar` y repone los ausentes; `self.informe` inválido al
declarar/quitar/cargar/fallar, exportadores apagados con motivo (PC-15/16);
`root.report_callback_exception` con diálogo; G-02 con `bloqueos_reales()` en
`cli.Informe` consumido por CLI y GUI; `conftest` con snapshot/restore único y
retirada de los 27 accesos privados.

**Paso 5 · Forma por criterio y parser GUI–GUI (cluster GUI, M).** Propuesta 3;
`int` para `'1'` y reescritura del test de ventana que hoy congela PC-13; política
de coma/miles; cara de solo lectura para `Derivada` en la emergente; ayuda de las 6
claves externas derivada de `variables_entrada` (decidir si se mantiene el «hueco
declarado»).

**Paso 6 · Registro normativo (sesiones N3/N4, M).** DG-2018 como `Fuente`
presente (sha1 96ea0442…, 285 pp., paginación medida, marca T1), citas 304.07.02 y
Tabla 304.09 para V5, decidir si vuelve el RNGIV; Seguridad Vial y Dispositivos en
`PRESENTES_SIN_REGISTRAR`; guardia «PDF presente» (propuesta 7); citas E.060
11.10.10.2/.3, M 170M §1.1, HDS-5 §5.4.3; N-03 (`norma_producto` por material y
forma, rótulo explícito para el marco in situ); N-01 (partir la ventana: legal vs
técnica; `Fuente.vigencia` de T1-01); PC-30. Regenerar los cuatro generados.

**Paso 7 · Cabezal (cluster C07, S).** M-05: la rama vertical con cortante alto
**detiene** con un criterio nuevo (hm, lm, ρh) y un criterio de aplicabilidad del
régimen en el plano; docstring y `verificar_cuantia`. M-06: Ka de Coulomb en el
estático (se reduce a tan² con ángulos nulos, medido −5.6e-17) o guardia con umbral
nombrado; bloque de CP9 con ángulos no nulos. M-07: `EstabilidadCabezal` con
`exigidas`/`pendientes` y `__post_init__`. Nada se cablea a la CLI
(`FUNCIONES_SIN_CONSUMIDOR` sigue vigilando).

**Paso 8 · Rendimiento y GUI no bloqueante (S/M).** Propuestas 2 y 6; imports
perezosos (propuesta 5, mitad); test de presupuesto de `import cli`; límite de
puntos documentado en el botón de PDF.

**Paso 9 · Paquete `src/` y servicio de cálculo (E01–E03, M).** Solo después del
paso 4: extraer las 736 líneas de orquestación de `cli.py` con el contexto ya
aislado; CLI y GUI como adaptadores; guardia de identidad.

**Paso 10 · Multi-obra como requisito (V-01, L).** Enmienda constitucional
(CLAUDE.md, v8 §0.7) y luego: `datos_sitio.establecer_dato_dinamico` con
trazabilidad obligatoria, `DatoSitio.nivel`, `--datos-sitio sitio.json` y la sesión
como único lugar del «proyecto actual»; advertencia cuando `--proyecto` no coincide
con `corredor_del_proyecto`. Solo entonces tienen sentido E04 (persistencia con
revisiones), E05 y E06 con contexto aislado.

**Paso 11 · Propiedades, mutación e higiene de suite (S).** Propuesta 4; PC-20
(corrida real en concreto para las Fases 6/7/8); PC-21 al AST; PC-22.

**Después:** ruta H (H00 = paquete I1), E10–E13, E21, y las rutas S/D/G solo con
sus puertas (S exige los cierres del paso 7 y un EMS real).

**Lo que no hay que hacer:** poner los datos de sitio a `None` sin enmendar la
constitución; convertir `h_o_fuera_de_rango` en `cumple=False`; unificar el parser
con la CLI; «implementar escenarios independientes» en M3; poner techos en
`dominios.py`; hilos de Tk sobre el estado global actual; un `registro.yaml` o un
`Proyecto` que duplique `Criterio`/`DatoSitio`/`Procedencia`.
