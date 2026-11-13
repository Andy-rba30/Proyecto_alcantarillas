# AUDITORÍA ADVERSARIAL T-3 — FASE A (`tesis/T-3`, `255c97a`, base `df1b23c`)

## Veredicto: AJUSTADO

## A. Refutado con evidencia

### H1 · ALTA · cita: sí · fórmula: no — `n_manning_cajon` ignora la fila propia de HDS-5
- HDS-5 Tabla B.1, pág. impresa B.6 (PDF 208): «Concrete Boxes | Smooth | 0.012-0.015 | FHWA 1961».
- HDS-5 B.3, pág. impresa B.2 (PDF 204): «Manning's n values for cast-in-place boxes range from 0.012 to 0.022 see concrete lined open channels from HDS 3 Table 1 (FHWA 1961).»
- La fila está en `src/normativa/tablas.py` como `("concrete_boxes", "Concrete Boxes", "Smooth", 0.012, 0.015, "FHWA 1961", False)`, marcada no usada. T-4 usó esa misma tabla como [C] para el HDPE.
- La ficha de `n_manning_cajon` y `docs/ruta_familia_c.md` no mencionan ni la fila ni el B.3 (grep vacío).
- La justificación afirma que «afinado» «describe el acabado que tiene un marco vaciado in situ». No tiene sustento: el B.3 liga el n del vaciado in situ a la calidad del encofrado.
- Dirección: n_max 0.014 < 0.015, no conservador para tirante y HW de salida; n_min 0.011 < 0.012, conservador para V3 y d50.
- Efecto sobre C-01, a mano: con n = 0.015, y/H pasa de 0.449 a 0.472 (S = 0.004); con 0.022, y/H = 0.625 y HW ≈ 0.675. La sección no se mueve.
- **Corrección:** en `criterios_adoptados.py::n_manning_cajon`, citar `HDS5_3ED.TB.1#concrete_boxes` y el B.3 en `sensibilidad` y `justificacion`, declarar la dirección y retirar la frase del acabado. Cuál rige lo decide el dueño.

### H2 · MEDIA · fórmula: sí — «cota inferior» del remanso es falsa en canal de pendiente fuerte
`M7.remanso_canal` no compara y_n con y_c del canal. Llamada directa con canal rectangular b = 1.2, n = 0.014, S = 0.02, Q = 0.85, HW = 0.90:
- Código: y_n = 0.231, dh = 0.669, «AL MENOS 33.4 m … cota inferior: el perfil real llega más lejos».
- Paso directo independiente: y_c = 0.371 > y_n; el remanso es un S1 que termina en resalto (conjugado 0.559 m) a **15.2 m**.
- En canal suave (b = 1, z = 1, n = 0.025, S = 0.001) la afirmación sí vale: 235 m frente a 745 m reales.
- **Corrección:** calcular el y_c del canal; con y_n ≤ y_c no llamar «cota inferior» a dh/S. Corregir `RemansoCanal`, `F7.REMANSO_CANAL` y el aviso. Falta un test del caso.

### H3 · MEDIA — «la obra no levanta la lámina» es un artefacto cuando VC2 está disparado
Corrida de la guía con `seccion_receptor_medida = {b 1.0, z 1.0, n 0.025, S 0.001, altura 1.2}`:
- HW = 0.667 < y_n = 0.715, y el aviso dice «la obra no levanta la lámina del canal en el cruce».
- En la misma corrida VC2 avisa que la salida queda 0.679 m sobre el fondo del canal.
- El HW sale de una descarga en caída libre que el canal no tiene. Con el empalme cerrado, TW ≈ y_n y HW > y_n siempre.
- **Corrección:** en `M7.compatibilidad_geometrica` / `remanso_canal`, si VC2 está fuera de tolerancia el remanso debe decir que no concluye.

### H4 · MEDIA — G2 y VC2 se contradicen en la mitad negativa de la banda
`M7.g2_cota_salida` y `M7.vc2_empalme_canal` sobre C-01 (fondo 36.20):

| cota_salida | G2 | VC2 |
|---|---|---|
| 36.205 | CUMPLE | CUMPLE |
| 36.195 | **NO_CUMPLE** | **CUMPLE** |
| 36.185 | NO_CUMPLE | INDICADOR |

La «banda de dos lados» del docstring sólo existe hacia arriba. El §16.17 de `docs/ruta_familia_c.md` ya había medido que G2 «rechaza la geometría correcta» por 5 mm, y T-3 no lo concilió.
**Corrección:** en Familia C, G2 con la tolerancia de VC2 por debajo, o VC2 sustituyendo a G2. Decisión del dueño.

### H5 · MEDIA · cita: sí — `cobertura_minima_cajon`: la fuente tiene regla propia para el marco y el criterio dice «NINGUNA»
- Manual MTC 4.1.1.3.4 a), impresa 72 (PDF 75): «Las alcantarillas tipo marco de concreto de sección rectangular o cuadrada pueden ubicarse a niveles que se requiera, como colocarse de tal manera que el nivel de la rasante coincida con el nivel superior de la losa o debajo del terraplén.» Es la cita `MC_HHD.4.1.1.3.4a#NIVELES`, que `F7.MARCO` usa y este criterio no.
- Lámina N.º 03 (impresa 209, PDF 212), renderizada: la figura «…EN CRUCE DE CANAL DE RIEGO» dibuja la losa a nivel de calzada, sin relleno.
- AASHTO LRFD 12.6.6.3, pág. 12-22 (PDF 1660), tras la tabla: «If soil cover is not provided, the top of precast or cast-in-place reinforced concrete box structures shall be designed for direct application of vehicular loads.» La tabla no tiene fila de cajón de concreto (confirmado).
- La `sensibilidad` sí nombra la rama «0 (sin cobertura)», pero el valor de archivo es el piso del tubo y G1 lo aplica como umbral duro. Contradice el criterio general del dueño para T-4: «las analogías avisan».
- Reproducción con rasante 38.40 / subrasante 38.25: C-01 no dimensiona. El primer escalón incumple V4 y V7; el segundo da `DatoInvalidoError` («la clave queda a nivel de la subrasante o por encima»). La tipología de la Lámina 03 es hoy inalcanzable.
- C-01 del fixture no se ve afectado (39.10 ≥ 38.455).
- **Corrección:** citar los tres textos en `fuente` y `justificacion`, y decir que 0.3048 m es más restrictivo que la fuente. Aviso o bloqueo en G1 lo decide el dueño.

### H6 · MEDIA — V7 del marco omite el peso propio, y de eso cuelgan la PARADA (c) y el espesor
`M5.v7_flotacion` lleva `DC = 0.0`. Es código de C7, no de T-3, pero T-3 apoya en él sus textos.
- El docstring de M8 lo justifica con «la densidad no la declara nadie». Hoy existe `peso_especifico_concreto_kn_m3` [C].
- Reproducida la progresión de la cadena T: 1.00 × 1.00 incumple V7 por 18.21 frente a 19.23 kN/m. A mano, el concreto de ese marco (0.96 m² × ~23.5 kN/m³ ≈ 22.6 kN/m) supera por sí solo al empuje.
- Barrido `espesor_pared_cajon=0.20,0.25,0.26,0.30`: C-01 dimensiona con 0.20 y 0.25 y deja de dimensionar con 0.26 y 0.30 por V7. El valor adoptado está en el extremo favorable de su ventana (0.20–0.30). La ficha ya admite que el signo es contraintuitivo.
- De la progresión adoptada sólo el primer escalón es alcanzable bajo la rasante de C-01: 1.50 × 1.20 incumple V7 con 18.9 frente a 29.8.
- La justificación de `secciones_cajon_normalizadas` y la decisión del dueño dicen «no cabe bajo una rasante con poco relleno». La causa real es `DC = 0`.
- La decisión se sostiene igual: con DC, la progresión de la cadena daría probablemente 1.00 × 1.00 y movería C-01.
- **Corrección:** reescribir esa frase en el criterio y en la ficha T3-01, y abrir ficha con símbolo sobre `v7_flotacion`. No tocar V7 en T-3.

### H7 · BAJA-MEDIA · cita: sí — pasos que imprimen como cita de la fórmula una que no la contiene
En la memoria generada, el paso 7.B.R imprime «Formula dh = HW - y_n ; L_min = dh / S_canal — num. 4.1.1.3.6 'Diseño hidráulico' pág. 74». Ese numeral sólo da Manning.
- 7.B.M cita `MC_HHD.LAMINA_03` para las fórmulas de ancho y canto; la lámina no acota nada.
- VC2 cita `EG2013.503.11g#COTAS` para la desigualdad.
- `formula_cita_id` es opcional (`modelos.py`, valor por defecto `""`).
- **Corrección:** dejarlo vacío en los tres y llevar la cita sólo a `citas_textuales` y al umbral.

### H8 · BAJA — tests y mutación
Arnés sobre copia aislada: `vc2_empalme_canal`, `remanso_canal`, `geometria_marco`, `_desajuste_admisible`.
- Con `test_t3_familia_c.py`: 39/57 muertos. Sumando `test_linea_base`, `test_cierre_perfil` y `test_M7_geometria`: 42/57. V6: 11/12. `ancho_exterior_de_celdas`: 9/9.
- **Test vacuo:** `test_el_remanso_rechaza_un_canal_sin_pendiente` sigue verde con la guardia mutada a `S >= 0`. La excepción sale de otro sitio, no de la guardia que dice medir.
- Vivos que importan:
  - margen del veredicto de VC2 (`tol - abs` → `tol + abs`);
  - frontera exacta de la tolerancia (`<=` → `<`, `+TOL` → `−TOL`);
  - `cota_lamina_entrada_msnm` (`+ HW` → `− HW`), que se publica en el JSON;
  - guardias de no finitud de Q, HW, S y t, y tolerancia igual a 0.
- El sentido SOBRE/BAJO del aviso y `tabique_m = 0.0` con N = 1 sólo los mata la línea base.
- Los dorados son independientes: bisección propia para y_n, geometría escrita a mano. HW 0.589 lo recalculé: 0.5892.
- Los tests reescritos con `sin_valor(...)` conservan lo que medían.

### H9 · BAJA — la tolerancia de VC2 está por debajo de la resolución de los datos
Con cotas al centímetro y S declarada a tres decimales, S·L se mueve 2.1 cm por milésima (L ≈ 21.4 m), más que la tolerancia. VC2 avisará casi siempre salvo que S se derive de las dos cotas.
- En el fixture (+0.571 / +0.614 m) el aviso dice algo cierto: las cotas no casan con S.
- Usar una tolerancia de ejecución como umbral de diseño es aceptable porque es [A], con ventana y sólo avisa.
- **Corrección:** que el aviso imprima el valor numérico de la S que cierra el empalme.

### H10 · BAJA · cita: sí — Tabla N.º 09: el corrimiento es real, pero «contrastada con Ven Te Chow» no es verificable en `normas/`
- Renderizada la pág. impresa 75 (PDF 78): «a. Concreto» y «b. Madera» llevan terna; «Tubo con moldaje madera en bruto» y «c. Albañilería de piedra» quedan vacías; el bloque A.1 está alineado. Corregido, «afinado» = 0.011 / 0.012 / 0.014. Confirmado.
- El mismo corrimiento sigue en B.1, B.2 y C; la discrepancia registrada sólo nombra A.2.
- Chow 1983 no está en `normas/`. La ficha de T-3 dice «contrastada con Ven Te Chow 1983». Debe apoyarse en la evidencia interna de la página.
- La v8 no dice que la fila adoptada es una lectura corregida.
- La lectura literal (0.013–0.017) sería más conservadora para capacidad; falta decirlo en la ficha.

### H11 · BAJA — textos desfasados respecto de la decisión del dueño
- Comentario «PROVISIONAL Y A PREGUNTA DEL DUEÑO» en `secciones_cajon_normalizadas`.
- Entrada de `sensibilidad` «PARADA (c) sin decidir».
- Nota de la v8 §2.3 «queda pendiente del dueño».
- Ficha T3-01.
- El pie de `255c97a` no es el de `ORQUESTACION.md`; se reescribe al aplastar.

### H12 · BAJA — etiquetas de las analogías
`n_manning_cajon` es [N→], pero `espesor_pared_cajon` (E.060, también norma peruana por analogía) es [A]. Recomiendo dejar [A]: el 14.5.3 se declara del método empírico de 14.5 y hay ventana. Conviene decir la razón en la ficha.

## B. Comprobado y no refutado
- **Citas nuevas, literales contra el PDF:**
  - `MC_HHD.4.1.1.3.4a#SEPARACION` (impresa 72 / PDF 75, «se recomienda»);
  - `E060.14.5.3.2` (pág. 134; el título del 14.5.3 es el del método empírico, y la ficha lo dice);
  - `EG2013.503.11g#COTAS` (impresa 934 / PDF 942, bajo «2. Otras tolerancias»);
  - `EG2013.501.07` (impresa 889 / PDF 897).
- **HDS-5:** Tabla A.1, Carta 8 escala 1 «30° to 75° wingwall flares», Forma 1, K 0.026, M 1.0, c 0.0347, Y 0.81. Tabla C.2 «Wingwalls at 30° to 75° to barrel / Square-edged at crown» 0.4. Carta y ke coherentes. La alternativa de cabezal recto da 0.629 a mano.
- **AASHTO:** el 12.11 no fija espesor mínimo para el marco; M 259 y M 273 son de prefabricado y no están.
- **C-01 a mano, guía (S = 0.006):**
  - y_c = 0.3712, y_n (n 0.014) = 0.3501, V_sed = 2.023;
  - HW de entrada = 0.5568 + 0.9·0.026·1.5024 − 0.5·0.006·0.9 = 0.5892;
  - HW de salida = 0.6356 + (1 + 0.4 + 0.5067)·0.03157 − 0.1293 = 0.5665.
- **C-01 a mano, corrida 6 (S = 0.004):** entrada 0.590; salida por perfil M2 ≈ 0.403 + 1.4·V²/2g = 0.623.
- **V7:** 0.9·17.0·1.60·0.95 = 23.256 frente a 9.81·1.60·1.30 = 20.405, con sumersión completa y DC = 0.
- **Geometría:** 1.60 × 1.30, clave exterior 38.000, relleno 0.950.
- **V6 con N = 2:** Q/N 0.425, tabique 0.20, ancho 3.00, sigue rechazada. `ancho_exterior_de_celdas` es la única cuenta para M5 y M7; 7.A y V7 siguen por celda, declarado en la ficha T3-05.
- **Ficha T3-07, reproducida:**
  - `--declarar ke_entrada=cajon_aletas_30_75_escuadra` se rechaza (no es número).
  - `--barrido ke_entrada=0.4 --barrido-fila cajon_aletas_30_75_escuadra` pasa la puerta en T-3 (en la base lo frenaba R4) y ningún punto dimensiona.
  - No hay tubo que corra con fila de cajón. La tabla del barrido deja el motivo vacío.
  - La pestaña 2 de la GUI no se pudo ejercitar (sin Tk).
- **Pre-vuelo:** dice la verdad para C-01 (Q, S_cauce y coronación detienen; con el JSON ampliado, sólo la coronación).
- **Bloqueo:** el `DatoFaltanteError(cota_coronacion_canal)` viaja como `Bloqueo` dentro de `_etapa`. `_fase_7` construye la sección del canal fuera, pero ya validada en la carga.
- **Avisos:** el remanso «no se evaluó» y VC2 llegan a `avisos()`, CLI, JSON y memoria.
- **`vacio_verificado`:** las cuatro anclas (§14.1, §15.3.1, §15.3.2, §16.12) existen.
- **Techo de `test_ext8`:** remedido, 108.70 KB por punto frente al techo de 109.0. No está relajado.
- **Línea base:** regenerada por mí, idéntica byte a byte a la comprometida.
- **Tests afectados:** 355 pasan (`test_normativa_pdf`, `test_guia_perfil`, `test_linea_base`, `test_cierre_c10`, `test_decisiones_diferidas`, `test_normativa`, `test_pf2_prevuelo`, `test_memoria_sustentada`). M11 no se tocó.

## C. PARADA (c): diámetros/secciones movidos — ninguno
- `informe_perfil_ancho`, `informe_expediente`, `informe_rama_error`: A-01 y A-02 sólo ganan `geometria_marco` y `remanso_canal` en `null`; B-01 sin diferencias. `cli_perfil.txt`, `cli_rama_error.txt` y los dos CSV de resumen, idénticos.
- C-01 pasa de `CriterioPendienteError(embocadura_cajon)` a `DatoFaltanteError(cota_coronacion_canal)`.
- Guía: base con los siete declarados frente a T-3 sin declarar. Mismo diseño en los cuatro puntos; lo nuevo es VC2, la geometría del marco, el remanso y las banderas `declarado_en_caliente`.

## D. Riesgos de integración sobre `e78a4e7` (merge de ensayo en copia, ya retirado)
- **Conflictos de fuente,** los cuatro por anexar al final: `src/modelos.py`, `src/normativa/citas.py`, `src/normativa/fundamentos.py`, `src/variables_entrada.py`. En `fundamentos.py` hay que cerrar el paréntesis de `MARCO_DEMANDA` antes del bloque de T-3. `MARCO` y `MARCO_DEMANDA` no chocan.
- **Otros conflictos:** tres documentos generados, README y seis archivos de la línea base, `test_ext8_rendimiento_gui.py`, `test_memoria_sustentada.py`.
- **Resultado con la unión:** la corrida 6 da C-01 en marco 1.20 × 0.90, HW 0.623, V7 23.256 / 20.405, sin fila `F8.*` a perfil (la demanda del marco queda diferida). La Fase 6 cambia por la envolvente, que para un marco no es evaluable y deja a Laushey. Frente a la línea base de main, la corrida ancha sólo difiere en lo de T-3.
- **No ejercitado:** `M8.demanda_marco` a expediente; C-01 se detiene antes, en V5/V8.
- **A recalcular:** techos de `test_ext8`; censos (previsiblemente 110 criterios y 27 sin valor); `LO_QUE_ESCRIBIO_CADA_PROMPT`.
- **Cobertura y M8:** con 0.30–0.61 m de relleno G1 pasa, y T-5 da «método no evaluable» por debajo de 2 ft.
- `GeometriaMarco` queda sin consumidor; M8 usa la misma `M5.cota_clave`.

## E. Para el dueño, con recomendación
1. **n del marco (H1).** (a) Mantener [N→] «afinado» declarando HDS-5; (b) [C] `HDS5_3ED.TB.1#concrete_boxes` (0.012, 0.015). Recomiendo (b): es la fila específica, coherente con el HDPE y con la carta y el ke de la misma fuente. No mueve la sección; mueve y_n, V y números de la línea base.
2. **Cobertura (H5).** Recomiendo mantener 0.3048 m como valor, pero que G1 del marco avise en vez de bloquear, citando MTC y AASHTO.
3. **V7 con peso propio (H6).** Recomiendo ficha diferida y corregir el texto; no cambiar V7 ahora. Con DC y la progresión de la cadena, C-01 probablemente pasaría a 1.00 × 1.00.
4. **G2 en Familia C (H4).** Recomiendo que VC2 gobierne el empalme y G2 use su tolerancia por debajo.
5. **Remanso en pendiente fuerte y con VC2 abierto (H2, H3).** Recomiendo «no concluye» con aviso.

Temporales en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-3-aud/` (corridas en `guia/`, línea base en `lb_base/` y `lb_t3/`, informes de mutación `mut_m7.json`, `mut_m7b.json`, `mut_m5.json`, `mut_mod.json`). Los worktrees `base` y `merge` están retirados y `/home/user/wt/T-3` queda limpio en `255c97a`.