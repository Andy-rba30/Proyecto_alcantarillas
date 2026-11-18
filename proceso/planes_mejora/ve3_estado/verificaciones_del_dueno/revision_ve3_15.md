# Revisión independiente de VE-3.15 (`82a0cfa..1b6412b`)

Revisado sobre un worktree aparte en `1b6412b` (no se tocó el repositorio). Python `/home/user/venv312`, `NORMAS_DIR=/home/user/Normas`.

## Veredicto

**Integrar con correcciones.** Los cuatro valores de archivo (9, 10, 11, 14) y la guardia de la decisión 12 hacen lo que el dueño aceptó, y las citas por id existen y dicen lo que se les atribuye.
No se puede integrar tal cual: hay cuatro tests en rojo que son del diff (H1), la memoria de CB5/CB7 contradice la decisión 14 con margen 0 (H2) y la decisión 13 no quedó implementada como se aceptó (H3).
Los tests movidos no tapan una caída del programa, pero dos de ellos ya no miden lo que su nombre dice (H4) y el fixture esconde un cambio de comportamiento de los valores nuevos (H5).

## Hallazgos

### H1 · BLOQUEANTE · Cuatro tests en rojo en `1b6412b` que son del diff y no de los generados

Corridos uno a uno en el worktree:

1. `tests/test_decisiones_diferidas.py::test_cada_ficha_dice_las_cuatro_cosas`: `fichas incompletas: {'VE3-18 …': ['**Qué se difirió:**']}`. La ficha abre con «**Qué se decidió:**», etiqueta que el test no admite.
2. `tests/test_decisiones_diferidas.py::test_el_registro_no_transcribe_la_razon_dos_veces`: `fichas demasiado largas, probablemente transcritas: {'VE3-18 …': 2846}`. La ficha repite la justificación de los criterios.
3. `tests/test_guardias_de_la_suite.py::test_el_cupo_de_approx_sin_tolerancia_no_crece`: 208 → 209. La nueva es `tests/test_ve3_15_decisiones_cabezal.py:57` (`pytest.approx(0.5)` sin tolerancia).
4. `tests/test_t10_memoria.py::test_los_datos_de_la_corrida_de_expediente_son_los_de_T7b_y_T7c`: la corrida de referencia `expediente_cabezal` declara `reduccion_por_desplazamiento` + `cedente`, y `t7c.DECLARACIONES_DE_PRUEBA` pasó a `sin_reduccion`. El test exige que sean iguales y ya no lo son.

**Corrección:**
- 1 y 2: etiqueta admitida y ficha recortada a la cita (la razón vive en las justificaciones). No ampliar `CAMPOS` ni el tope.
- 3: tolerancia con nombre de `tests/apoyo/aproximacion.py`. No subir el cupo.
- 4: decidir cuál de los dos lados es la referencia y reescribir el test declarándolo. No igualar a ciegas.

### H2 · ALTO · Con margen 0 la memoria sigue diciendo que el proyecto aplica AASHTO 12.6.5 al cabezal

El diff cambió la `Interpretacion` de `AASHTO_LRFD_9.12.6.5#ZAPATAS` a «El proyecto NO lee incluida la zapata del cabezal de salida», pero no tocó los textos de `M9_cabezal.py` ni el `Fundamento` que la imprimen.
Corrida del juego de la validación integral con los valores de archivo, A-01 salida:

- **CB5.s:** umbral con `cita_id='AASHTO_LRFD_9.12.6.5#ZAPATAS'`, carácter EXIGENCIA, descripción «fondo de la hoya menos el margen de AASHTO», aplicación «EXIGENCIA de AASHTO para las zapatas de las estructuras enterradas, **leída por el proyecto como aplicable** a la del cabezal de salida». Sustitución: `margen = 0.0`; obtenido = admisible = 40.2223 msnm; veredicto CUMPLE.
- **`por_que` de CB5 (`F9.DESPLANTE`, `src/normativa/fundamentos.py` ~3326):** «AASHTO exige … con un margen, **y el proyecto lee que la del cabezal es una de ellas**».
- **CB7.s (`M9_cabezal.py` ~5206):** «EXIGENCIA de AASHTO 12.6.5 … **con el margen de 2.0 ft** que el artículo da a las zapatas», con `margen = 0.0`.
- **Paso 9.0.2:** `citas_textuales=('AASHTO_LRFD_9.12.6.5#ZAPATAS',)`, y la nota sin socavación dice «no es el que AASHTO 12.6.5 pide».

La memoria imprime CUMPLE contra una cita cuyo texto literal es «not less than 2.0 ft below», con 0 ft, y afirma una lectura que la `Interpretacion` de la misma cita niega.

**Corrección** (test en rojo primero, sobre el paso CB5/CB7 con margen 0):
- Umbral de CB5 con `HEC14.5.1.3#CABEZAL` (recomendación) y `AASHTO_LRFD_9.10.6.1.2#DESPLANTE`; 12.6.5 pasa a cita de contraste.
- Reescribir `aplicacion`, `descripcion_umbral`, el `por_que` de `F9.DESPLANTE`, la `aplicacion` de CB7 y la nota de 9.0.2.
- Si el margen declarado es > 0, el texto debe decir que es el extremo alto de la ventana, no una lectura del proyecto.

### H3 · ALTO · La decisión 13 no quedó implementada como se aceptó, en ninguno de los dos regímenes

Aceptado: «el mayor entre centroide estático y H/3 sólo con el muro que cede; h/2 con el que no cede».
Implementado: el archivo conserva `fraccion_de_h` (incremento a 0.6·h) para los dos regímenes (`M9_cabezal.py` 6943–6972).

**Muro que no cede (archivo).** La estabilidad externa no pone la resultante total a h/2. Queda en z/h = (1/3 + 0.6·r)/(1 + r), con r = ΔP_AE/P_A, que sólo llega a 0.5 si r ≥ 1.67. Con Mononobe-Okabe, δ = 2φ/3, relleno horizontal:

| φ | k_h0 | r | z_total/h | momento del empuje a h/2 ÷ implementado |
|---|---|---|---|---|
| 34° | 0.15 | 0.40 | 0.409 | 1.22 |
| 34° | 0.25 | 0.75 | 0.448 | 1.12 |
| 34° | 0.30 | 0.97 | 0.465 | 1.08 |
| 34° | 0.40 | 1.53 | 0.495 | 1.01 |
| 34° | 0.50 | 2.35 | 0.520 | 0.96 |

- Medido en A-01 entrada con valores de archivo (k_h = 0.50): EH.h = 15.67 kN/m a 0.935 m y ΔP_AE,h = 36.81 a 1.682 m, con h = 2.804 m → z = 0.520·h. Aquí cumple h/2 por la sismicidad del sitio.
- Con k_h0 ≤ 0.4 queda por debajo, hasta un 22 % menos de momento volcante del empuje.
- El armado sí aplica h/2 (`_pantalla_con_resultante_a_media_altura`); la estabilidad externa, no.
- La guardia que rechaza `distribucion_estatica` dice «para el muro que no cede C11.6.5.4 pide la resultante a h/2» y deja en su lugar algo que no es h/2.

**Muro que cede** (reducción + armado «cedente» declarados). El incremento sigue a 0.6·h salvo una tercera declaración (`distribucion_incremento_sismico` = `distribucion_estatica`).
- Ningún juego de prueba la hace: `grep -rn distribucion_estatica tests/fixtures` no devuelve nada.
- El dictamen pedía «valor de archivo 1/3 para la estabilidad externa del muro que cede».

**Corrección** (cualquiera de las dos, decidida por el dueño):
- (a) Derivar el brazo del régimen: cede → max(centroide estático, h/3); no cede → resultante total no menor que h/2 (p. ej. z_total = max(el de 0.6 sobre el incremento, h/2)). Con test a mano de las dos ramas.
- (b) Dejar el código y escribir en la ficha VE3-18 y en la justificación, con la tabla de arriba, que «h/2 con el que no cede» rige sólo en el armado y que con el muro que cede hace falta la tercera declaración.

Hoy `test_13_…` sólo comprueba que el archivo dice `fraccion_de_h` y que la justificación contiene «decision 13 del dueño».

### H4 · MEDIO · Tests que afirman el valor de ARCHIVO y pasan sólo por el fixture

`valores_previos_ve3_15` reemplaza `ca.CRITERIOS[clave]`. Bajo ese fixture de módulo, estos tests dicen comprobar el archivo y comprueban el parche:

- `test_t7a_cabezal_geometria.py::test_el_margen_bajo_la_socavacion_son_dos_pies_exactos`: `c.valor == 2.0·PIE` y `"12.6.5" in c.fuente`. El archivo dice 0.0.
- `test_t7b_cabezal_estabilidad.py::test_las_categorias_tienen_su_conjunto_cerrado_y_la_puerta_lo_exige[fila_phi_estabilidad_cabezal-zapatas_seccion_10-…]`: `c.valor == "zapatas_seccion_10"`. El archivo dice `muros_tabla_11_5_7`.
- `test_t7b_cabezal_estabilidad.py::test_los_factores_de_resistencia_salen_de_la_fila_declarada`: afirma (0.45, 0.80) sin declarar nada, como si fuera el valor por defecto.

Reproducido neutralizando el fixture (`yield` sin parchear, `ARGS_PREVIOS_VE3_15 = []`) y corriendo los siete archivos: 58 fallos. De ellos:
- 57 son dorados o trazas que cambian con los cuatro valores, sin ninguna excepción de programa. Los dos fallos de E3 (`StopIteration`, y el resumen sin «método no evaluable») son la consecuencia de que con margen 0 el agua ya no llega al plano de empuje; ver H5.
- 1 es un cambio de comportamiento (H5).

El uso del fixture es defendible para los dorados a mano, que miden un método. No lo es para estos tres.

**Corrección:** reescribirlos declarándolo contra el valor nuevo, fuera del fixture, o borrarlos en favor de `test_ve3_15_…` diciéndolo.

Otras observaciones sobre los tests:
- **E2 0.70 → 0.40 y E3 5.970 → 5.570:** legítimos. Los fixtures declaraban la reducción y ahora deben declarar «cedente». Medí E3 por la CLI con los valores previos: B = 5.570 m con pantalla de 0.50 m. La diferencia de 0.40 m exacta es de espesor de pantalla (B = B_estabilidad + Δe), así que el comentario del test («el peralte que el armado pide es otro») es impreciso.
- **`test_la_pantalla_crece_con_la_zapata…` con `monkeypatch`:** mide la aritmética B = B_est + Δe, que es lo que dice. Aceptable.
- **`test_t7c` con `sin_reduccion`:** correcto. La geometría es la de la regla (`sin_valor("dimensionamiento_zapata_cabezal")`) y el armado en reposo ya iba con k_h0, de modo que los momentos no cambian.
- **Hueco de cobertura:** ningún test con dorado a mano corre la tubería con los cuatro valores nuevos a la vez. `test_ve3_15_…` sólo compara cadenas del archivo. El peralte por armado, la reoptimización del ancho y la pantalla por armado ya no se disparan en el juego con los valores nuevos; quedan probados sólo con los previos.

### H5 · MEDIO · Con `cuna_sobre_la_pantalla` de archivo, una cuña de pantalla sin máximo detiene la estabilidad externa

Sin el fixture, `test_t7b_cabezal_estabilidad.py::test_los_valores_de_frontera_del_ensamble_si_entran` falla con excepción en su última línea:

```
MetodoNoEvaluableError: … empuje sismico sobre la cara de la pantalla del punto T-00 -- la cuña de tanteo no tiene maximo … (M9_cabezal.py:6552)
```

El caso: `regla_pendiente_relleno_trasdos` = `talud_quebrado_2h` (fórmula cerrada), φ = ψ exacto. Con el valor previo la estabilidad E1–E3 se evaluaba (K_AE > 0.9). Con el nuevo, `ensamble_estabilidad` entero se detiene por la carga estructural de la pantalla, que la estabilidad externa no necesita.
Es un caso de frontera, pero el acoplamiento es real y el fixture lo oculta.

**Corrección:** que la solicitación de la pantalla no evaluable quede como bloqueo de ese elemento (como hace `_fase_9_armado`) sin tumbar E1–E3; o declararlo en la ficha y dejar el test midiendo el comportamiento nuevo.

Relacionado: con margen 0, E3 ya no tiene agua en el plano de empuje (desplante 39.452 msnm frente a 38.843; h_w era 0.257 m). El escenario que VE-3.14 usaba para «sismo con agua» sólo existe con los valores previos.

### H6 · MEDIO · «Un solo régimen» cubre k_h, no el empuje; y la justificación de «cede» no se exige

- `regimen_cabezal` sigue en `cedente`. La estabilidad externa de archivo usa empuje activo (`EstabilidadDeCabezal.regimen == 'cedente'`, K_A = 0.254 frente a K0 = 0.441 en A-01) y el armado usa K0.
- `test_12_un_solo_regimen_y_no_cede_de_archivo` afirma en la misma función `regimen_cabezal == "cedente"`.
- El diff quitó de `CLAUDE.md` «—que sigue con el muro que cede—», que sigue siendo cierto para el empuje estático.
- La ficha VE3-18 no dice que el régimen único es sólo de k_h (lo que el dictamen verificó).
- La combinación inversa pasa sin aviso: armado `cedente` con `sin_reduccion`.
- «Cede sólo declarado con justificación» no lo exige nada. `--declarar regimen_resistencia_elementos_cabezal='cedente'` entra sin nota, y el programa no avisa aunque la pantalla mida menos de 1.524 m, dato que sí tiene.

**Corrección:**
- Decir en VE3-18 y en `CLAUDE.md` qué unifica la guardia.
- Emitir un aviso de memoria cuando se declara «cedente», con las tres condiciones y la altura de la pantalla contra 5.0 ft.
- Renombrar el test o partirlo.

### H7 · BAJO · Texto y código muertos tras la guardia

- `M9_cabezal.py` ~12439 (paso del régimen, se imprime en la memoria): «el armado va con k_h = 1.0·k_h0 (11.6.5.4) **aunque la estabilidad lo reduzca**». Ya no puede ocurrir.
- `M9_cabezal.py` ~11167–11190 y ~11220–11229: ramas `usa_reposo and cadena.k_h < cadena.k_h0` inalcanzables en producción. Sólo las alcanzan los tests que parchean `cadena_sismica` (`test_H2_…`).
- `M9_cabezal.py` ~6908 y ~6925: el remedio «admitir el desplazamiento del muro, `factor_muro_eleccion`» no dice que ahora hay que declarar además el armado «cedente».

**Corrección:** retirar o reescribir, con sus tests.

### H8 · BAJO · Citas de las justificaciones sin página ni registro

- `fila_phi_estabilidad_cabezal`: la justificación se apoya en C11.5.7 (pág. 11-16), en el Manual de Puentes 2.8.1.1.12.6 (págs. 250–251) y en el ejemplo de Caltrans (págs. 11.2-24 y 11.2-26). El campo `fuente` no los lleva, y no hay `Cita` de C11.5.7 en el registro (`grep C11.5.7 src/normativa/citas.py` no devuelve nada).
- `factor_muro_eleccion`: nombra C3.11.5.2 sin página; está en la `fuente` de `regimen_resistencia_elementos_cabezal` (3-120).

El contenido atribuido es correcto: lo comprobé en el volcado `lrfd.txt` (C11.5.7 «Smaller resistance factors should be used if site or material variability…»; C3.11.5.2 «typical cantilevered walls over 5.0 ft»; 11.6.1.2; 11.6.5.3; 10.6.1.2; C11.6.5.4).

**Corrección:** completar `fuente` y registrar la cita de C11.5.7.

### H9 · BAJO · Guardia de la decisión 12: correcta; dos efectos laterales

Sobre la guardia en sí:
- **Tipo de excepción:** `DatoInvalidoError` es la adecuada (hay que corregir una contradicción entre dos declaraciones). Es el mismo patrón que la guardia de `distribucion_estatica`.
- **Cómo viaja:** como `Bloqueo` `DATO_INVALIDO`. Medido: 1 del proyecto en «cadena sísmica (9.2)» y 4 por punto (estabilidad sísmica y armado, por extremo). La estabilidad estática sigue evaluándose y el ancho queda «dimensionada con la estabilidad evaluable (falta una condición)».
- **Caminos que la esquivan:** ninguno en producción. `factor_muro()` sólo se llama desde `cadena_sismica()`, y todo consumidor de k_h pasa por ella (`servicio.correr_cabezal`, `cargas_del_cabezal`, `solicitaciones_de_resistencia`). La lectura directa de `M9_cabezal.py` 6957 ocurre después. Con valores de archivo no se activa.
- **Perfil:** la Fase 9 se difiere entera, así que no rompe ese alcance.

Efectos laterales:
- Un cabezal de **gravedad** (no se arma) con la reducción declarada queda obligado a declarar un régimen de armado que no usa, y el criterio se registra como usado.
- Barrer `regimen_resistencia_elementos_cabezal` sobre un juego que declara la reducción da, para `no_cedente_k0`, todos los cabezales bloqueados. Afecta a `tests/apoyo/sensibilidad.py`, generado que no revisé.

### H10 · BAJO (fuera del diff, lo destapan los valores de archivo) · Ancho final sobre el tope y aviso desfasado

A-01 salida con valores de archivo: el aviso dice «B_max = 4.825 m … queda B = 4.752 m», y la geometría entregada tiene B = 4.852 m. La pantalla creció a 0.40 m por armado después del aviso, y el ancho final supera el tope de 1.5·H_c.

## Punto 5 · ¿A-01 no cierra el sismo con valores de archivo por defecto del cálculo o por los datos?

**Efecto legítimo de los datos, no un defecto del cálculo.**

Reproducido con el juego sin `factor_muro_eleccion` ni `regimen_resistencia…` declarados: A_s = k_h0 = k_h = 0.50, y los ocho cabezales quedan en el tope con E3-LRFD.sis (y E1 en las salidas) sin cumplir.

A mano, A-01 entrada (B = 3.375 m, H_c = 2.25 m), caso 50 % P_AE + 100 % P_IR:
- H = 0.5·15.67 + 0.5·7.39 + 0.5·36.81 + 0.5·(45.18 + 95.82) = 100.43 kN/m.
- R = 1.0·152.02·tan 32° = 94.99 kN/m. Coinciden con la app.
- Con k_h = 0.50 y tan φ_f = 0.625, cada kN de peso añade 0.625 de resistencia y 0.50 de inercia: 0.125 netos. Hacen falta unos 184 kN/m de peso y en el tope hay 141, es decir B ≈ 4.5 m ≈ 2.0·H_c.
- Es lo que el dictamen anticipó (hallazgo 8: 1.8 a 2.0·H_c).

Dos precisiones:
- El PGA de 0.50 g **no es dato de prueba**: es el `PGA_roca_B` [S] de `datos_sitio.py`. Lo de prueba es el suelo (φ 32°/34°).
- Con los valores de archivo y el PGA del sitio de la obra, el programa no entrega ninguna zapata corrida factible en este juego. La ficha VE3-18 no lo dice; debería, con los remedios que el propio aviso lista (dentellón con pasivo, tope, suelo, o el régimen «cede» declarado por el Propietario).

## Punto 1 · Valores y citas (resumen)

| Criterio | Archivo | ¿Como se decidió? |
|---|---|---|
| `momento_talon_cabezal` | `exacto` | Sí. El código descuenta la reacción lineal por combinación, sin tracción; con la resultante fuera de la base rige el peso entero; el contraste se imprime. |
| `carga_pantalla_cabezal` | `cuna_sobre_la_pantalla` | Sí en el valor. Las dos condiciones son de VE-3.14 y no las recalculé. Ver H5. |
| `fila_phi_estabilidad_cabezal` | `muros_tabla_11_5_7` | Sí. Sin «2.11.8.5» y con la tensión de 2.8.1.1.12.6 y la salvedad de C11.5.7. Ver H8. |
| `margen_zapata_bajo_socavacion_m` | 0.0 | Sí en el valor y la justificación. No en la memoria (H2). |
| `factor_muro_eleccion` / `regimen_resistencia_elementos_cabezal` | `sin_reduccion` / `no_cedente_k0` | Sí, con la guardia. Ver H6. |
| `distribucion_incremento_sismico` | `fraccion_de_h` | No como se aceptó (H3). |

- **Citas por id:** `HEC14.5.1.3#CABEZAL` (recomendación, pág. 5-2), `AASHTO_LRFD_9.10.6.1.2#DESPLANTE` (exigencia, 10-52) y `AASHTO_LRFD_9.12.6.5#ZAPATAS` (exigencia, 12-20) existen y su texto literal es el que la justificación usa.
- **Hoja de ruta:** §0.2 dice «AASHTO LRFD de extremo a extremo»; §0.1 pone la Sección 12 de AASHTO como [C]; §9.2 dice «No asumirlo en un cabezal empotrado en terraplén»; §9.4 (5) dice «el talón con el peso entero» (declarado en la ficha como lo que sigue mal).
- **Un matiz:** la justificación del margen dice «las dos fuentes son técnicas reconocidas (hoja de ruta §0.1)», y la tabla de §0.1 no nombra HEC-14 (sí AASHTO y HDS-5).

## Lo que no pude verificar

- **La suite completa: sólo hasta el 55 %** (4359 de 7788 tests; la corté ahí, con la máquina compartida con otras suites). En ese tramo hubo 14 fallos y 5 errores:
  - 4 fallos del diff (H1).
  - 9 de sincronía de generados, fuera del encargo: `test_indice_formulas` (2), `test_manifiesto_citas` (6) y `test_ext9_paquete_servicio::test_las_dos_entradas…` (índice desincronizado).
  - 1 que no se reprodujo: `test_ext6_registro_normativo::test_el_repositorio_de_normas_enlazado…` pasó al correrlo solo.
  - 5 errores de `test_linea_base`, de entorno: `regenerar.sh` usa el `python` del PATH, que no tiene scipy. No dicen nada de la línea base.
  - **El 45 % restante no se corrió** (desde `tests/test_t11_sensibilidad.py`, e incluye los siete archivos del cabezal con su fixture puesto). Esos siete sólo los corrí con el fixture neutralizado (H4).
- Los documentos generados y la línea base (excluidos por encargo).
- Las implementaciones de VE-3.14 de las opciones 9 y 10: no rehice sus dorados a mano. Sólo comprobé que el archivo las selecciona y que el camino del código corresponde a la condición.
- Los PDF en imagen. Las citas de AASHTO las contrasté con el volcado de texto; Caltrans y el Manual de Puentes los tomo del dictamen del dueño.
- Los commits posteriores a `1b6412b` (el repositorio avanzó durante la revisión: `6b08e4b` y siguientes) quedan fuera de lo revisado; puede que alguno de los hallazgos ya esté atendido allí.
