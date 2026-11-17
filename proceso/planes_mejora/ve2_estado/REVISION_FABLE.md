# Revisión independiente de VE-2 (Fable)

Material de proceso. Revisor: sesión independiente con el modelo Fable 5.2, sin las
conclusiones de quienes implementaron. Fecha: 2026-11-17.

## Qué se revisó

- El commit de integración **existe**: `8dd435e` («validacion(VE-2): integración — VE1-02
  (a) a (g)») en `origin/claude/elegant-rubin-4ax72s`. Se revisó el diff `72a8d01..8dd435e`
  y sus cinco commits intermedios (`9a9b998` (b), `4c077c2` (a), `9fedc8d` (g), `2b9aa21`
  (c), `c250d06` (e, f, d)). No se revisó ningún `*.wip.patch` como terminado: los dos que
  siguen en `proceso/planes_mejora/ve2_estado/` (`c_flotacion_v7.wip.patch`,
  `e_f_d_hidrologia.wip.patch`) son anteriores a los commits `2b9aa21` y `c250d06`, que
  son lo revisado.
- Entorno: clon limpio en `/home/user/revision_fable` (fuera de cualquier otro checkout),
  `python` 3.12 con tkinter, ttkbootstrap, weasyprint, PyMuPDF, `xvfb-run -a`,
  `NORMAS_DIR` = clon de `Andy-rba30/Normas`.
- No se corrigió nada. No se integró nada en `main`.

## Veredicto

**Integrar con correcciones.** El cambio de método (b) es correcto y está bien probado;
(f), (d), (g), (c) y (a) reproducen lo que el prompt pide y lo que los PDF dicen. No hay
hallazgo bloqueante. Hay **un hallazgo alto** (A1) que conviene resolver, o al menos
declarar con su ficha, antes de llevar VE-2 a `main`, porque un documento generado de la
validación integral afirma algo que el propio programa desmiente; el resto son medios y
bajos que pueden ir a ficha.

## Par de la suite

`xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header` en el clon limpio, en
`8dd435e`, con `NORMAS_DIR` y Tk:

**7425 passed, 10 skipped, 7435 collected** (839 s, exit 0; passed + skipped = collected).

Coincide con el par que la bitácora de la integración anota (7425 / 10 / 7435).

## Hallazgos

### Bloqueantes

Ninguno.

### Altos

**A1 · El cambio del fixture `caudal_calculado` tapa un punto «NO FACTIBLE» que no lo es
(B-01), y el documento generado lo publica.**

- Dónde: `tests/fixtures/juego_validacion_integral.py:419-438` (la variante vacía
  `Q_evento_extremo_m3s` de A-01, A-02 y B-01; el comentario dice «Con eso los tres puntos
  quedan como estaban (NO FACTIBLE)»), su copia
  `tests/fixtures/corridas_de_referencia/hidrologia_calculada/externos.json`,
  `docs/validacion_integral.md:231` («B-01: resultado: ningun material ni seccion cumple —
  Fase 5») y la causa de fondo en `src/modulos/MD.py:1016-1024` y `1103-1115`
  (`disenar_punto`, que VE-2 no tocó).
- Evidencia (script propio sobre `tests.apoyo.validacion_integral`, variante aplicada con
  `vi.aplicar(vi.juego_completo(), cambios)` y `vi.correr_juego`):
  1. Con la variante tal como quedó (extremo vacío), B-01 (Q calculado 1.7905 m³/s):
     `HDPE Ø 1.20 m: el escalon no se pudo evaluar -- DatoFaltanteError: Falta el dato
     'Q_evento_extremo_m3s' en el punto B-01`, y el punto sale con bloqueo
     `DisenoNoFactibleError`, `campo: None`, `delta_rasante_m: 0.3698`.
  2. Con la variante anterior (extremo 0.106 del juego): el mismo escalón levanta
     `DatoInvalidoError` y el punto sale con bloqueo `DatoInvalidoError`,
     `campo: Q_evento_extremo_m3s` (lo relanza `MD._exigir_datos_validos`, T11-03).
  3. Con un extremo coherente declarado a mano (`Q_evento_extremo_m3s` = 1.99, 1.11 veces
     el calculado): B-01 sale con bloqueo `DatoFaltanteError`, `campo:
     perfil_hdpe_fabricante` («el HDPE de 1.20 m queda no verificado con un producto
     real»). Es decir, **ese escalón cumple toda la tabla de la Fase 5** y sólo le falta un
     dato.
- Por qué es un defecto: `CLAUDE.md` («Excepciones», DatoFaltanteError / DatoInvalidoError)
  fija que «un punto al que solo le falta un dato no es "no factible"» y que el dato
  inválido sigue «el mismo patrón que PC-28 y T-5 para el dato que falta». En `MD` el
  patrón no es simétrico: un `DatoInvalidoError` de V8 sobre un escalón que cumple lo demás
  es decisivo (`_exigir_datos_validos`), y un `DatoFaltanteError` de V8 sobre el mismo
  escalón no lo es (sólo son decisivos los que traen `ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`, que
  pone la Fase 8). El defecto es anterior a VE-2, pero VE-2 lo tenía a la vista (la
  validación «lo tomaba por un hallazgo», dice el comentario) y lo resolvió quitando el
  dato del fixture, con lo que el informe pasó de un bloqueo honesto (corregir un dato) a
  «no existe diseño» con un delta de rasante. La ficha VE2-B menciona que la variante vacía
  el caudal, no que B-01 queda mal rotulado.
- Corrección sugerida (una de dos, decide el dueño): (i) que `MD.disenar_punto` trate el
  `DatoFaltanteError` que levanta la Fase 5 sobre un escalón que cumple lo evaluado como
  decisivo, igual que hace con el inválido, y regenerar `validacion_integral.md` (B-01
  saldría «entrada del proyecto que falta — Q_evento_extremo_m3s»); o (ii) dejar `MD` como
  está, abrir ficha con este caso medido y corregir el comentario del fixture y la fila del
  documento para que no digan «quedan como estaban». En ambos casos conviene un test que
  fije el caso 3 de arriba.

### Medios

**M1 · V3 no mira la velocidad de salida bajo control de salida, y VE-2 ensancha la
brecha.** `src/modulos/M5_verificaciones.py:1602-1627` (`_velocidad_de_v3`): con S > 0 V3
compara siempre `V_erosion` (tirante normal de n mínimo). En pendiente suave con salida
libre la mayor velocidad del barril es la de la sección de salida a y_c (HDS-5 3.1.6), que
el propio programa calcula: en el caso del dictamen (`M4.resolver_control`, Ø 0.90 m,
Q = 0.3, S = 0.001, TW = 0) `V_salida` = 1.508 m/s y `V_erosion` = 1.107 m/s (1.184 antes
de VE-2). Es anterior a VE-2 y el prompt mandó no tocar la velocidad de salida, pero el
30 % de más de la fórmula vieja cubría parte de la diferencia y ya no. Con los techos de
3 a 6 m/s del concreto rara vez decide; no está en ninguna ficha de VE-2. Sugerencia:
ficha, y decisión del dueño sobre si V3 juzga max(V_erosion, V_salida) bajo control de
salida.

**M2 · Bajo control de entrada la velocidad y el tirante de salida son de dos rugosidades
distintas, y el contraste de HEC-14 queda del lado bajo.**
`src/modulos/M4_control.py:1570-1586` devuelve `V_erosion` (tirante de n mínimo) con
`normal.geometria.y` (tirante de n máximo); `src/modulos/M6_proteccion.py:775-784`
(`apron_hec14`) usa ese tirante en D' de la Ec. (10.5), y como D50 va con D'^(-4/3) la
piedra del contraste sale menor que con el tirante coherente. Está **declarado y
diferido** (ficha VE2-B (i), VE2-02): no es un defecto oculto. Se anota porque es el único
consumidor que quedó con el par mixto; el Froude sí quedó coherente (usa A = Q/V).

**M3 · Con `nivel_agua_diseno_v7` = `nf_del_punto` una corrida de perfil consume un
criterio de expediente.** `src/modulos/M8_estructural.py`
(`peso_relleno_bajo_el_nivel_kn_m`, línea 565) lee `peso_especifico_saturado_relleno_kn_m3` cuando
el nivel pasa de la clave. Medido con una corrida propia a `--alcance perfil` (NF 0.05 m,
margen 5 m, sin el peso saturado declarado): el punto sale con bloqueo `CriterioPendienteError` de ese criterio. Declarado en VE2-C y VE2-02; contradice la
regla de dos direcciones de «Nivel de entrega» sólo con la alternativa declarada (con el
valor de archivo no se invoca). Queda para el dueño.

**M4 · `margen_estacional_nf_v7_m` es [A] de perfil con `forma` float y `sensibilidad`
de texto.** `src/criterios_adoptados.py:7879` (ficha del criterio): la ventana son dos frases,
no un rango, y el signo lo rechaza el consumidor (`M8.cota_nivel_agua_v7_del_nf`,
`DatoInvalidoError`) y no la puerta. Funciona (medido: −1.0 sale como bloqueo
`DatoInvalidoError` con `campo` = la clave), pero un barrido de sensibilidad sobre este
criterio no tiene ventana numérica que recorrer y el valor negativo entra a la sesión.
Sugerencia: `no_negativo` en la puerta, o decirlo en la ficha.

### Bajos

- **B1 ·** `tests/test_t4_materiales_durabilidad.py:1284` (`CASO_G2`): S pasó de 0.012 a
  0.015. El cambio está declarado y es legítimo (el caso existe para que el concreto
  incumpla V3 en toda la progresión; con la velocidad corregida a S = 0.012 ya no lo
  hace), y no tapa un defecto. Pero el caso original del auditor (S = 0.012) ya no lo fija
  nadie: convendría un test más con lo que hoy da (se detiene en la clase D-load de la
  Fase 8).
- **B2 ·** `src/modulos/M8_estructural.py:561` (`empuje_flotacion_bajo_el_nivel_kn_m`):
  `raise TypeError("forma de seccion no implementada")`, fuera de `ErrorProyecto`. Es
  inalcanzable con las dos formas que existen; se anota por la regla de excepciones.
- **B3 ·** `src/tolerancias.py:80` (`TOL_REL_CONTINUIDAD_MANNING` = 1e-9): el comentario dice
  «doce veces por encima de lo medido» (8.1e-11). En un barrido propio de 20 000 casos
  aleatorios (seis diámetros, S de 1e-4 a 0.3, Q de 0.1 % a 99.99 % del lleno) la peor
  desviación fue 1.34e-10: el margen real es de unas siete veces. La tolerancia sigue
  valiendo; el número del comentario depende de la malla.
- **B4 ·** `proceso/planes_mejora/ve2_estado/LEEME.md` sigue diciendo que ningún agente
  había commiteado y lista parches `*.wip.patch` que ya no describen el estado; la carpeta
  versiona unas 13 700 líneas de parches ya integrados. Conviene actualizar el LEEME o
  retirar los parches al integrar.
- **B5 ·** `src/modulos/M2_material.py:1099` (`_exigir_escalon_designado`) admite para el concreto, con la opción inglesa,
  tanto 1.0668 m como 1.067 m (la celda redondeada de la Table 6): son dos diámetros de
  cálculo distintos para el mismo tubo. Declarado en la `Interpretacion` de la tabla.

## Lo verificado que está bien

**(b) Velocidad de erosión.**
- UPAO ALC46 con un script propio (Brent sobre la Sec. 4.1, sin `M3`): Q = 0.317, S = 0.10,
  D = 0.90. Con n = 0.013: y = 0.1438 m, V = 4.834 m/s. Con n = 0.010: y = 0.1266 m,
  A = 0.05454 m², **V = Q/A = 5.812 m/s** (y Manning sobre ese tirante da lo mismo). La
  fórmula vieja da 6.284. `M3.resolver_manning` devuelve 5.81220, 0.126649 y 0.143810, y
  `V_erosion · A(n_mín)` = 0.317 exacto. El test de punta a punta dimensiona Ø 0.90 m.
- A-01 de la línea base: V_erosion 3.2055 → 3.0401 m/s, igual a la cuenta a mano que el
  test `test_cierre_perfil` rehace (y_n de n mínimo 0.5234 m, A = 0.38387 m²); Froude de
  HEC-14 con ye = (A/2)^0.5 = 0.4381 m → 1.4664, que coincide.
- Continuidad y convergencia: 20 000 casos aleatorios, ninguno sin converger en la rama
  de n mínimo cuando converge la de n máximo; siempre y(n_mín) < y(n_máx) y
  V_erosion > V_sedimentacion. En el borde Q ≥ Q_lleno(n_máx) devuelve `None` (sin
  sustituto). Q diminuto (1e-12) mantiene V·A/Q = 1.
- Control de salida: `velocidad_de_salida` no cambió en esa rama (1.508 m/s en el caso
  del dictamen). No se encontró ningún caso con control de entrada y y_n(n_máx) > y_c en
  un barrido de Q, S, L y TW sobre Ø 0.90 m, de modo que el rótulo de régimen del Froude
  no contradice la velocidad.
- Consumidores: `grep` de `V_erosion` y `n_para_velocidad_maxima` en `src/`, `gui/` y
  `cli.py`: ninguno recalcula con la fórmula vieja. M9 no lee `V_erosion`.
- Citas: HEC-14 núm. 3.2.2, pág. impresa 3-7 (PDF 38), leída: «normal flow is assumed at
  the culvert outlet and the outlet velocity is computed using Manning's Equation»; el
  ejemplo de la PDF 39 resuelve un tirante por cada n (0.012 y 0.024).

**Línea base.** Comparación clave a clave de los cuatro `informe_*.json`:
- `72a8d01..9a9b998` (b): sólo se mueven V_erosion, V_salida, su procedencia, d50, Froude,
  espesor y clase de la piedra y los avisos que los imprimen, en A-01, A-02 y C-01
  (`informe_familia_c.json` 36 claves, `informe_perfil_ancho.json` 33; expediente y rama
  de error, 0). Todos bajan. **Ningún diámetro, sección ni material cambia.**
- `9a9b998..8dd435e`: sólo las listas de criterios (dos usados más, uno sin valor más) y
  huellas; ningún número de cálculo.

**(f) Racional modificado.** Ecuaciones (29) a (35) leídas en la imagen de las págs.
impresas 51 y 52 (PDF 54 y 55): Q = 0,278 CIAK; Tc = 0.3(L/S^0.25)^0.76;
K = 1 + Tc^1.25/(Tc^1.25 + 14); KA = 1 – (log10 A/15); P = kA·Pd;
I = (P/24)·11^((28^0.1 − Tc^0.1)/(28^0.1 − 1)); C = (Pd − Po)(Pd + 23Po)/(Pd + 11Po)²;
Po = 5000/CN − 50. El código las transcribe igual; la (32) se lee 1 − log10(A)/15 y lo
declara como `Interpretacion`; la (35) usa Pd y lo declara en el paso. Cuenca de 55.9 km²
(L = 15 km, S = 0.02, CN = 75) recalculada con un script propio: con Pd = 100 mm,
Tc = 4.9403 h, K = 1.34473, KA = 0.883506, I = 14.1664 mm/h, C = 0.501730, Q = 148.533
m³/s; con la serie de prueba (Pd = 99.812 mm) el programa da Q = 148.058 m³/s y la cuenta
a mano lo mismo hasta el último dígito. Límites medidos: 9.999 km² → racional simple;
10.0 → modificado; 769.99 → calcula; 770 y 800 → `MetodoNoEvaluableError` con el rótulo
de hidrología y los métodos de hidrograma nombrados; Tc de 0.001, 0.059 y 120.7 h →
`MetodoNoEvaluableError`.

**(d) Factor de intervalo fijo.** Valor de archivo 1.0, ventana (1.0, 1.13), [A] de perfil,
forma float; se aplica a cada máximo anual antes del ajuste. Con 1.13 la lluvia de diseño
sube 1.1300 exacto y el caudal del racional modificado 1.2264 (C crece con la lluvia, como
dice la ficha).

**(e)** El aviso de consistencia existe como paso `FH.CONSISTENCIA` sin umbral; no se
encontró ningún número de corte en el módulo (lo fija además un test).

**(c2) V7.** Medido con corridas propias: sin NF y con `nf_del_punto` → `DatoFaltanteError`
de `NF_profundidad_m`; con NF y sin margen → `CriterioPendienteError` del margen; con el
nivel bajo el fondo exterior → «no aplica»; con el nivel entre fondo y clave → U parcial;
con el nivel sobre la clave → pide el peso saturado y U vuelve al valor de la sumersión
completa (9.3228 kN/m, el mismo que `en_la_clave`). Citas leídas: Manual de Puentes
2.4.3.8.1 (PDF 114) «Los niveles de agua de diseño […] serán los especificados y/o
aprobados por el Propietario»; AASHTO LRFD 12.6.1 (PDF 1652) «Water buoyancy loads shall
be evaluated for buried structures with inverts below the water table».

**(g) Table 6 de AASHTO M 170M.** Leída celda por celda en la imagen de la PDF 20 (3×) y
en su capa de texto. Las 21 filas transcritas (300 a 2700 mm) coinciden con la imagen
salvo exactamente las nueve celdas de DIS-M170M-T6-RECOMPOSICION: «30S» → 305, «1$» → 15,
«3gl» → 381, «123» → 525, «S4» → 54, «1659» → 1650, «lS00» → 1800, «i950» → 1950,
«9d» → 96. Las nueve correcciones son las únicas compatibles con la serie y con
pulgada × 25.4 redondeada (12 → 304.8, 15 → 381.0, 21 → 533.4, 54 → 1371.6, 66 → 1676.4,
72 → 1828.8, 78 → 1981.2, 96 → 2438.4); las 54 celdas restantes se leen tal cual. Las
filas de 2850 a 3600 no se transcriben, y la imagen ahí es ilegible («iM8», «3333»,
«U38», última fila), como dice el `Acotada`. Los trece escalones de 0.90 + 0.15 m son
designados en las tres series hasta el tope de cada material. El diámetro inglés sólo
entra para el concreto y sólo con `diametro_de_diseno_concreto` =
`designado_o_ingles_convertido`.

**Integración.** 146 criterios en `criterios_adoptados.CRITERIOS` (141 + 5); los cinco
nuevos son [A] de perfil con forma, sensibilidad y resolución; ninguno de los 146 sin
nivel ni forma. `CLAUDE.md` dice «146 desde VE-2» en los tres sitios del recuento.
`datos_sitio.py`, `MD.py` y la hoja de ruta no cambian. En el diff de `src/` no hay
comparación de floats con `==` ni excepción genérica nueva salvo B2. Los tests de
sincronía de los documentos generados, del censo de literales y de las citas contra el
PDF son parte de la suite, cuyo par está arriba.
