# Informe de las CORRECCIONES de T-7a (PARTE 1) — cabezal: geometría por punto y aleros

- Worktree `/home/user/wt/T-7a`, rama `tesis/T-7a` (empujada a `origin`), base `df1b23c`,
  FASE A en `1b83d39`. **No fusionado a `main`** (la PARTE 2 espera el «integra»).
- SHA de la rama: `d90cf1a` (ver §6).

## 1. Hallazgo por hallazgo

| ID | Veredicto | Qué se hizo (anclado por símbolo) |
|---|---|---|
| **H1** (ALTA) | **Cerrado** | `M9.predimensionar_aleros` recibe el esviaje (vía `EmbocaduraDelPunto.esviaje_grados`) y `modelos.Aleros` lleva `longitud_corto = (h0 − H_f)·talud/cos(α − θ)` y `longitud_largo = …/cos(α + θ)` (θ en valor absoluto; «corto/largo» porque el CSV no trae el sentido del giro). Guardia MAT-D13 `not cos(α+θ) > TOL` → `LimiteNumericoError` con el par (α, θ) y el remedio (declarar `longitud_aleros_m` o un α menor); con los aleros declarados no hay guardia. Convención citada: **HDS-5, List of Symbols, ΘW**, pág. impresa xix / PDF 23, literal «Flare angle of wingwalls with respect to extension of culvert side wall» (cita nueva `HDS5_3ED.SIMBOLOS#THETA_W`; para que la regla de paginación la prediga, `esquema.PorCapitulo` ganó `romanas` y `fuentes.HDS5_3ED` `romanas=4`, medido i = PDF 5 … xxii = PDF 26). Dorado: A-01 entrada 2.1/cos 30° = 2.425 m y 2.1/cos 60° = 4.200 m; salida 4.011 / 6.947 m; C-01 (θ 30°) largo/corto = cos 15°/cos 75°. Paso 9.0.3 con θ y talud en la sustitución; `F9.ALEROS` sin «avanza en la dirección del eje»; el docstring de `predimensionar_cabezal` ya no dice «los aleros absorben el giro» y dice Δz = L_c·sen θ/talud, que sale como **aviso** cuando θ ≠ 0 (A-01: 1.70·0.259/2 = 0.220 m). Ficha T7A-03: cabezal paralelo a la vía (Carta 11) diferido y aviso a T-7b del acoplamiento con `orientacion_muro_respecto_al_trafico`. |
| **H2** (ALTA) | **Cerrado** (la decisión 4 del dueño **NO se aplicó**: premisa refutada) | Medidas las tres capas sobre el árbol (`test_h2_las_tres_capas_que_detienen_la_fase_9_a_expediente`): (1) `remanso_derecho_via` vacío → `CriterioPendienteError`; (2) declarado → `M5.v5_remanso` levanta `DatoFaltanteError('ancho_derecho_via_m')` sin leerlo; (3) con V5 simulada → V8 en `TR_evento_extremo`. `ancho_derecho_via_m` sigue fuera de `CLAVES_EXTERNAS`. Ficha T7A-01 reescrita con las tres capas, «ningún test recorre la Fase 9 por la ruta real» y lo que la cerraría. Tracker propuesto: **`INF-4.2` e `INF-4.3` «en parte»**. |
| **H3** | **Cerrado** | Lámina Nº 04 releída por imagen (PDF 213, 250 y 400 ppp): la cota «0.80 min.» arranca en el terreno natural al borde del dentellón (= cara inferior del paquete losa 0.15 + granular 0.20) y llega a su base. `LosaDeEntrega` gana `cota_terreno` y `cota_base_dentellon`; la profundidad se mide desde `ExtremoDelConducto.cota_pie` (una referencia por extremo para desplante, losa y dentellón). A-01 salida: base 40.50 (antes 41.187, 0.11 m bajo el lecho). `nota` de `MC_HHD.LAMINA_04#DENTELLON` y docstring corregidos. |
| **H4** | **Cerrado** | `verificar_compatibilidad_cabezal` suma **CB6** (espesor de zapata ≥ mínimo de su tipo: 0.30 m de E.060 22.7.4 en gravedad; 0.30 m sobre el refuerzo de E.060 15.7 + 0.07 m de 7.7.1 a) en voladizo armado; `M9.peralte_minimo_zapata`) y **CB7** (base del dentellón ≤ min(terreno − 0.80 [N→], fondo de la hoya − margen [C])). Los dos casos del auditor fallan ahora (zapata de gravedad 0.20; dentellón 0.10 y dentellón que no baja bajo la hoya). |
| **H5** | **Cerrado** | Tests nuevos: hoya REAL de `M6.socavacion_salida` por `servicio._fase_9` con D_f, CB5 y dentellón a mano; CB5 fallando con desplante entre `hoya − margen` y `hoya`; `altura_total_m` declarada con su coronación; frontera de CB2 (±1 mm); marco de dos celdas (2·1.20 + 3·0.20); rama «método distinto de por extremo»; guardia de TW/y_salida nulos; guardias de α y de θ. Mutación remedida: ver §3. |
| **H6** | **Cerrado** | El talud muere en el relleno retenido (coronación − bordillo) contra el trasdós: `longitud_entre_cabezales(cota_relleno_entrada=, cota_relleno_salida=)`; A-01 → **13.486 m** (antes 12.865). `CabezalDelPunto.longitud_metrado` = L_cab + e_e + e_s (muros normales al eje: el espesor sobre el eje es e, sin factor de esviaje; la cifra 2·0.30·1.035 del auditor no aplica) → 14.086 m en A-01. «milímetros» → «centímetros» (1.6 cm en A-01, S 0.006 × ~2.7 m). h0 de los aleros: se mantiene coronación − pie con H_f medido igual (cresta del alero un bordillo sobre el talud) → h0 − H_f es exactamente la caída del talud; con H_f sobre el talud saldrían más cortos: dicho como «la lectura de más longitud». |
| **H7** | **Cerrado** | Ficha T7A-04 y aviso por punto: el umbral se mide sobre la altura TOTAL y con altura interior ≥ 0.90 m la mínima es 0.90 + 0.30 + 0.15 + 0.80 = 2.15 m + pared → todo cabezal sale voladizo armado. Cita nueva `E060.22.10.2#CICLOPEO` (pág. 195/PDF 195, 22.10.2.1 literal; 22.10.2.2 en la nota) y aviso cuando sale gravedad. Umbral y su referencia sin cambiar. |
| **H8** (dudoso 1) | **Cerrado** | `PROFUNDIDAD_CIMENTACION_MIN_M` sale de `constantes_normativas`; criterio nuevo **`profundidad_cimentacion_min_cabezal_m` [N→]** (0.80, expediente) con la analogía (Art. 1 y 3 pág. 7; 39.13.7 pág. 73, verificados) y `Interpretacion` en `E050.26.2#PROFUNDIDAD`. CB4 dice «por analogía» y gobierna el criterio. **Defecto de la hoja reportado** con nota en la v8 §0.1 («Defecto declarado (T-7a)»): la tabla y el «Estabilidad — E.050 [N]» de §9.3 siguen mal hasta que T-7b los corrija. Ficha T7A-08. |
| **H9** | **Cerrado** (los nueve ítems) | (1) origen nuevo `ORIGEN_DIMENSION_DERIVADA` («derivada de dimensiones declaradas») con la lista de declaradas de las que sale (talón, punta, B, zapata, aleros…); (2) JSON `criterios` sin el vacío con cabezal recto; (3) docstring de `servicio.correr_cabezal`; (4) aviso de desplante sin socavación con SU motivo (el `motivo_no_estimada` de M6, o el bloqueo de la etapa `ETAPA_SOCAVACION_SALIDA`); (5) dentellón BAJO la hoya con el margen; (6) `formula_cita_id` vacío en F9.CORONACION/ALEROS/LOSA/LONGITUD con `NOTA_FORMULA_DEL_PROYECTO`; (7) escala 3 de la Carta 12 sin banda; (8) el 0.30 m de recubrimiento sobre la clave deja de apoyarse en la Tabla 12.6.6.3-1 (queda [A] puro: se quitó la referencia, no se subió a 0.3048); (9) `variables_entrada` lleva una nota «se lee ANTES de la Fase 4» en `angulo_aletas` y `embocadura_cabezal` (la fase se sigue deduciendo del consumidor, por diseño); (10) la coherencia por familia se fija con un test (M2 da el marco solo a la Familia C) y se declara en el docstring. |
| **H10** | **Cerrado** | Ninguna frase dice que «más material» es el lado seguro: la justificación de `predimensionamiento_cabezal` y la ficha T7A-04 dicen que con kh = 0.50 y μ = tan 20° = 0.364 < kh la masa EMPEORA el deslizamiento sísmico, y que lo evalúa T-7b. |
| **Dudoso 3** | **Cerrado** | `margen_zapata_bajo_socavacion_m` sigue [C]; `Interpretacion` en `AASHTO_LRFD_9.12.6.5#ZAPATAS` (la fuente habla de la zapata de la estructura enterrada; el proyecto LEE incluida la del cabezal, y aplica el mismo margen al dentellón; en contra y a favor escritos). |
| **Dudoso 4** | **Cerrado** (el literal lo sostiene) | E.060 15.7 «PERALTE MÍNIMO DE LAS ZAPATAS», pág. 138/PDF 138: «La altura de las zapatas, medida sobre el refuerzo inferior no debe ser menor de 300 mm para zapatas apoyadas sobre el suelo» (cita nueva `E060.15.7#PERALTE`). Criterio nuevo **`peralte_min_zapata_armada_m` [N→]** = 0.30; `e_z = max(H/10, 0.30 + 0.070)` (7.7.1 a), `RECUBRIMIENTO['contra_suelo']`). A-01 entrada: 0.225 → **0.37 m**. |
| **Dudoso 5** | **Cerrado** | «H/8–H/6» sigue [A]; la justificación y la ficha dicen que su origen (VARIOS p. 42) no se pudo verificar. |
| **Decisión 3** | **Aplicada** | Aviso en cada punto de Familia B (`EmbocaduraDelPunto.avisos` → `InformePunto.avisos()`): la caja receptora no se modela. Ficha T7A-02. |
| **Coherencia sin ruido** | **Aplicada** | La nota de coherencia del marco ya no es una línea propia de la CLI ni un `div` de la memoria: va en la línea «Embocadura» («; coherente con la embocadura del marco»), en el JSON y en el paso 9.0.0. |

## 2. Tests y par

- **Nuevo:** `tests/test_t7a_correcciones.py`, **76 tests** (61 de la primera tanda, H1 a H10,
  dudosos y decisión 3; 15 de la segunda, escritos contra los supervivientes de la mutación).
- **Rojo medido** (no escrito con `xfail`, declarado en el docstring y en la ficha T7A-07):
  la primera tanda (61) copiada a un `git archive 1b83d39` (FASE A) con el import de
  `ORIGEN_DIMENSION_DERIVADA` protegido: **47 failed, 14 passed**. Los 14 verdes son guardias
  que valen antes y después: las tres de H2 (que fijan la REFUTACIÓN de la premisa de la
  decisión 4: la puerta no se abre, las tres capas, V5 no lee el dato), las de H5 sobre
  comportamiento de la FASE A que nadie probaba (CB5 fallando, frontera de CB2, marco de dos
  celdas, TW/y_salida nulos, cuatro guardias de α), la de H7 (todo cabezal sale voladizo) y
  la de la coherencia por familia.
- **Reescritos declarándolo** (docstring «REESCRITO en las correcciones de T-7a»): once tests
  de `tests/test_t7a_cabezal_geometria.py` (piso de zapata armada 0.225 → 0.37; dos aleros;
  dentellón bajo la hoya con margen y desde el terreno; CB1–CB7; origen «derivada»; longitud
  entre cabezales al relleno; E.050 [N→]). `tests/test_normativa.py` exime
  `E060.15.7#PERALTE` del detector de tildes (la frase de la pág. 138 no lleva ninguna; leída).
- Ningún test se restó.
- **Par de la rama**, suite entera medida sobre `cace28a` y otra vez sobre el SHA final `d90cf1a`
  (que solo añade una aserción y texto de ficha), con `NORMAS_DIR`, PyMuPDF sí · Tk no:
  **5113 passed / 16 skipped / 5129 collected** en las dos (FASE A: 5034 / 16 / 5050; +79 = 76 del archivo nuevo + 2 que
  crecen solos en `test_ext5_forma_gui` con los dos criterios nuevos + 1 anclaje de la ficha
  T7A-08 en `test_decisiones_diferidas`). Sin `NORMAS_DIR` no se midió en esta parte.

## 3. Mutación

Arnés de EXT-11 sobre las 17 funciones de la Fase 9 del punto en `M9_cabezal`
(`embocadura_del_punto` … `validar_cabezal_declarado`), objetivos `test_t7a_cabezal_geometria`,
`test_t7a_correcciones` (primera tanda) y `test_M9_cabezal`: **275/326 muertos (84.4 %)**
(la FASE A medida por el auditor: 185/226, 81.9 %). Los supervivientes que importaban
—incluidos todos los que la auditoría nombró: el signo del margen de CB5, el de CB2, la
coronación de una `altura_total_m` declarada, la socavación por la etapa, el ancho de N
celdas, la guardia de TW/y_salida, las de α y la rama de otro método de longitud— están
muertos en la primera vuelta o por la segunda tanda (15 tests: TW nulo con tirante,
α = 0, el mensaje α + θ, el resguardo, el texto de la regla del desplante, el criterio de
cada mínimo, el margen del veredicto, el criterio de CB7, H_c = 2.0 exactos, una L_cab corta
pero positiva, el motivo con profundidad sin cota, el talud sin longitud calculada, la
sustitución del paso 9.0.5 y el metrado con espesores distintos, las guardias de reglas y
margen, los mensajes de las puertas). Los que quedan son de FRONTERA con la tolerancia
nombrada (`>=`/`>` contra `TOL_UMBRAL_NORMATIVO`, `e_z < piso`, `talon >= 0`, `H_c > 0`, empates
en `por_hoya < por_terreno`), de TEXTO (`texto_dent or '-'`) o EQUIVALENTES en el dominio
(`caida > 0` vs `>= 0` solo cambia la nota). **Remedida con la segunda tanda: 309/326 (94.8 %)**,
y uno más (la sustitución `e_e + e_s` del paso 9.0.5) muerto después con una aserción y
comprobado a mano sobre una copia mutada: 16 vivos, todos de frontera contra
`TOL_UMBRAL_NORMATIVO`, de texto o equivalentes en el dominio (`H_c > 0` → `> 1`, inalcanzable con
0.80 m de desplante). Dicho en la ficha T7A-07.

## 4. Línea base y diámetros

Regenerada (README con sección «correcciones de T-7a»). Comparador de E-B contra la de la
FASE A: **una sola diferencia por JSON, `criterios_sha1`**; por `diff`, el aviso nuevo de
B-01 (caja receptora), «con la pared del barril» en la línea Embocadura de los cuatro
`cli_*.txt`, `hoja_ruta_sha1` y el recuento 105/33 → 107/33 en las memorias. CSV de resumen
y `memoria_punto_cajon.html` sin cambio. **Diámetros movidos: ninguno.**

## 5. Cosas que conviene saber para la PARTE 2

- Criterios: 105 → **107** en la rama (los dos [N→] nuevos, con valor: «sin valor» sigue en 33).
- `src/normativa/esquema.py::PorCapitulo` ganó el campo `romanas` (zona caliente
  `normativa/*`) y `manifiesto.py` lo imprime.
- `servicio.ETAPA_SOCAVACION_SALIDA` (constante nueva) nombra la etapa de T-8: al rebasar
  sobre main, comprobar que la etapa de socavación de main conserva ese nombre.
- `test_normativa::test_T21…` gana `E060.15.7#PERALTE` en su lista de exentas.

Además, fuera de la línea base: HW de A-01, A-02 y B-01 (perfil, TW 0.30) y de C-01 con los
siete del cajón **idénticos en `repr`** a la FASE A (A-01 Ø 0.90 concreto, HW 1.0420015370127218;
A-02 Ø 0.90, 0.5720081284009831; B-01 Ø 0.90, 0.2319944167649528; C-01 marco 1.20 × 0.90,
0.623401190456344).

## 6. SHA

Rama `tesis/T-7a` en `origin`: **`d90cf1a`** (serie `wip(T-7a)` desde `8296fcd`, sobre la FASE A
`1b83d39`). `origin/main` no se tocó.

## 7. Preguntas para el dueño

1. **Orientación del cabezal en los cruces esviados.** Hoy: normal al eje (dos aleros de
   distinta longitud y un desnivel Δz del talud a lo largo del muro, avisado; en C-01, θ 30°,
   Δz = 0.55 m frente a un bordillo de 0.15 m). Alternativa: paralelo a la vía (corona y
   talud coinciden), que lleva el marco a las filas de la Carta 11, hoy sin banda, y cambia
   la orientación respecto del tráfico que lee T-7b. Recomiendo decidirlo con T-7b; mientras
   tanto, normal al eje con el aviso.
2. **Cómo se alcanza la Fase 9 a expediente** (decisión 4 refutada): (a) método de remanso
   para V5 + valor de `remanso_derecho_via` + `ancho_derecho_via_m` + TR y Q del evento
   extremo de V8 (el orquestador lo lleva a un prompt posterior); (b) correr la Fase 9 como
   anticipo no bloqueante a perfil. Recomiendo (a) y no (b): la Fase 9 es de expediente y
   un anticipo a perfil mostraría cabezales sobre un punto que V5/V8 no han cerrado.
3. **Ámbito de E.060 para el cabezal de gravedad.** E.050 pasó a [N→] por su ámbito
   (edificaciones); E.060 22.7.4 sigue [N] porque la §9.4 de la hoja hace regir E.060 22.10
   sobre el ciclópeo, pero la misma objeción de ámbito lo alcanza. Recomiendo resolverlo en
   T-7c, que es quien verifica el ciclópeo.

## 8. Lo que NO hice

- No toqué el tracker `.xlsx`, `CLAUDE.md` ni `LO_QUE_ESCRIBIO_CADA_PROMPT`: son de la PARTE 2.
  Filas propuestas: `INF-4.2` e `INF-4.3` **en parte** (residual: alcanzable a expediente,
  ficha T7A-01); `INF-5.1.15`, `INF-3.4.1`, `INF-3.4.2` **cerrados** (H1 cerrado); `INF-4.1`
  en parte (geotécnicos y sísmicos: T-7b).
- No medí la suite sin `NORMAS_DIR` en esta parte (se mide al integrar).
- No cambié el umbral de 2.0 m del ciclópeo ni su referencia (H7 lo pedía así).
- El 0.30 m de relleno sobre la clave quedó [A] puro (se quitó la referencia a AASHTO
  12.6.6.3); no se subió a 0.3048 m.
