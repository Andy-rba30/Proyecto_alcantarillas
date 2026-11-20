# INFORME T-11 · FASE A — validación integral de las tres familias

- **Rama:** `tesis/T-11` (worktree `/home/user/wt/T-11`), base `origin/main` = `14f6138`. **SHA empujado:
  `c774035`** (`origin/tesis/T-11 == HEAD`, verificado). **No** se fusionó ni se empujó a `main`. No se tocó el `.xlsx`, la tabla de
  conteos de `CLAUDE.md`, `docs/linea_base.md` ni `verificar_sesion.py`.
- **T-11 valida y no cambia cálculo.** Ningún archivo de `src/modulos/` cambió. En `src/` sólo: dos entradas de
  `modelos.ALCANCE_DECLARADO` (texto) y `src/indice_formulas.py` (tercera corrida de referencia y la unidad `m2` en
  la máscara de valores del índice). Ningún valor de prueba en `criterios_adoptados.py`, `datos_sitio.py` ni
  `constantes_normativas.py` (un test lo fija).
- Retomé el trabajo del agente anterior (`bc3531b`, punto 1). Revisado: su suite pasaba (21 passed, 1 xfailed) y
  sus juicios están escritos en el docstring de `tests/apoyo/validacion_integral.py`.

## 1. IDs (canónicos)

T-11 no trae IDs propios en su prompt. Lo que propongo escribir al integrar (FASE B), con la evidencia:

| ID | Estado actual | Propuesta | Por qué (evidencia) |
|---|---|---|---|
| `INF-0.5` | Abierto | **Cerrado (T-11)** | «Criterios vacíos que detienen todo; la corrida de referencia dimensiona 0 de 4». Medido: con el juego de prueba los 4 puntos dimensionan y llegan a la Fase 11 (`docs/validacion_integral.md` §2); sin juego cada bloqueo es entrada / criterio del Propietario o proyectista / método con ficha (§3, test). Los 2 criterios de perfil sin valor no opcionales esperan una entrada (`homogeneidad_serie_fen`, `TW_receptor`). Los sin valor de expediente son decisiones del dueño o ensayos (§6). |
| `INF-3.2.2` | Cerrado parcial | **Sigue parcial + NOTA** | T-11 deja `docs/validacion_hds5.md` (HDS-5 y HEC-14 contra sus ejemplos, generado) y `docs/validacion_hy8.md` (procedimiento). Falta la corrida de HY-8 del autor. |
| `INF-3.4.3` | Abierto | **Propuesta: Cerrado (por T-7b; verificado por T-11)** — que lo decida el integrador | Las fórmulas de carga las consume el ensamble (`M9.cargas_del_cabezal`, `ensamble_estabilidad`); las sueltas están en `M9.FUNCIONES_SIN_CONSUMIDOR` con razón, y el test de T-11 comprueba que ninguna tiene llamador de producción y que el ensamble sí. φ es entrada del EMS; δ, i, γ_EQ son [A]/[C] con ventana, barridos en el anexo. |
| `INF-3.4.4` | Abierto | **Propuesta: Cerrado (por T-7b)** | Ensamble con dos marcos (LRFD rige, ASD informa: decisión del dueño); capacidad portante de AASHTO 10.6.3.1.2a; E4/E5 diferidas declaradas; ningún `AssertionError`/`NotImplementedError` en `src/modulos/` (test de T-11, por AST). |
| `INF-3.4.6` | Abierto | **Propuesta: Cerrado (por T-7b)** | k_h: `factor_muro_eleccion` [A] del Propietario; k_v: criterio con valor `prescrito_sin_caso_reservado`. Sensibilidad medida por T-11 (`sin_reduccion` cambia 6 filas por punto). |
| `INF-5.1.3`, `INF-5.1.9`, `INF-5.1.16` | Cerrado (T-1, T-4, T-4) | sin cambio | Estado real verificado en el tracker: cerrados (los tres «sin prompt» los recogieron T-1 y T-4). |
| `INF-5.1.8` | Cerrado parcial (T-9) | sigue parcial | Nada comprueba que el área sea la del tramo de cuneta: lo destraba el estudio hidrológico (ficha T9-07). |

Los demás `INF-` no cerrados (19 en total; lista en §8) no cambian con T-11.

## 2. Tests nuevos y par

| Archivo | Tests | Notas |
|---|---|---|
| `tests/test_t11_validacion_integral.py` | 25 (1 `xfail(strict=True)`) | juego, Fase 11, tres clases, lista exacta = contrato §7, variantes, tercera corrida, censo final |
| `tests/test_t11_validacion_externa.py` | 12 (5 con marca `pdf`, abren `hec14.pdf`: saltan sin `NORMAS_DIR`) | sincronía de los dos documentos, censo HDS-5, intervalo del CMP, HEC-14 por página |
| `tests/test_t11_sensibilidad.py` | 6 (5 `lento`) | sincronía, ventana, no-leídos, juicios por clase, cabezal frente a sus dos [A] |
| `tests/test_decisiones_diferidas.py` | +8 anclajes (T11-01..08) | crecen solos |
| `tests/test_t10_memoria.py` | 0 (reescrito, declarado) | el set de `ALCANCE_DECLARADO` pasa de 5 a 7 claves |

**+51 netos**: collected 6360 → **6411**. Marca `pdf`: 145 → **150**. Sin `NORMAS_DIR` saltan 5 más (41 → 46).
Par medido sobre la rama (`PyMuPDF sí · Tk no`, con `NORMAS_DIR`): **6387 passed / 23 skipped / 1 xfailed — collected 6411** (ver §10).

**Rojo**: no escrito primero (ficha T11-08). Medido con los archivos finales de `tests/` sobre un worktree de la base
`14f6138` (sin `src/` ni `docs/` de T-11): **8 rojos** (las cinco sincronías de documentos, la §7 del contrato, la
tercera corrida y su entrada al índice, y el alcance de `test_t10_memoria`), **77 verdes** (comportamiento que ya
existía y que T-11 mide) y el `xfail` del defecto.

## 3. La LISTA EXACTA de lo que sigue requiriendo entrada del proyecto

Medida (corrida sin juego + quitar una entrada a la vez del juego completo), clasificada, y **repetida en la §7 de
`docs/contrato_entradas.md`** (un test exige igualdad en los dos sentidos):

- **Entradas del proyecto (15):** `luz_m`, `L_hidraulico_m` (o `S_cuneta`), `S_cuneta`, `Q_m3s` y `S_cauce` de la
  Familia C, `cota_coronacion_canal`, `NF_profundidad_m`, `phi_relleno_trasdos` (EMS), `c_phi_fundacion` (EMS, o
  `suelo_fundacion` por punto), `orientacion_muro_respecto_al_trafico` y `distancia_borde_calzada_al_trasdos_m` ([S]
  de corredor, trazo), `exposicion_quimica_ems` (EMS), `Q_evento_extremo_m3s`, `TW_evento_extremo_m`,
  `cota_afectacion_aguas_arriba_msnm`.
- **Criterios que se declaran (4):** `TR_evento_extremo`, `umbral_no_colapso_evento_extremo` (Propietario),
  `remanso_derecho_via`, `categoria_refuerzo_aashto` (proyectista).
- **Método diferido con ficha (1):** `drenaje_trasdos` — con el valor de archivo (`sin_drenaje`) la sísmica del
  cabezal es «método no evaluable» (T7B-05).
- **Condicionales no disparadas por el juego** (contrato §7): `homogeneidad_serie_fen` (sólo caudal calculado;
  medida con la variante `caudal_calculado_sin_fen`), `perfil_hdpe_fabricante`, las D-load de M 170M, la costura
  empernada del TMC, `ancho_tributario_m`, `ancho_derecho_via_m`, `TW_receptor`.
- **No detiene pero cambia el diseño:** sin `TW_m` (ni `cota_TW` ni `Q_receptor_m3s`) **ningún punto dimensiona**
  con la sección adoptada del receptor.
- **Corrección 3.4 del contrato:** decía que sin `exposicion_quimica_ems` / `categoria_refuerzo_aashto` había sólo
  «aviso»; medido: la Fase 9 del PROYECTO queda bloqueada en la 9.4 (cuatro y tres etapas). También: NF, φ del
  relleno y los [S] de la sobrecarga detienen el ARMADO además de la estabilidad.

## 4. Qué llega a la Fase 11 y qué no, y por qué

- **Juego completo (`--alcance expediente`, CLI real y servicio):** A-01, A-02, B-01 → concreto Ø 0.90 m; C-01 →
  marco 1.20 × 0.90 m. Los cuatro con bloque en la memoria y fila en el CSV resumen. Único bloqueo: C-01, VC1-01
  (alcance diferido de la Sec. 2.3). B-01 corre con TW 0.30 m y el tramo declarado (150 m); con el TW de 1.00 m de la
  línea base no dimensiona (V2) y sin el inicio de tramo VB1 no cumple (530 m): las dos variantes se imprimen.
- **El cabezal de la regla no pasa** E3 estática ni E1 sísmica (LRFD) en ningún punto: es un RESULTADO (la zapata no
  se itera, T7B-09). Sensibilidad medida: omitir los factores de inclinación hace pasar E1 sísmica en los cuatro;
  la fila de φ de muros hace pasar E3 estática de salida en A-01, A-02 y C-01; E3 estática de entrada no pasa con
  ninguno (sí con la zapata de 3 m en A-01). Además A1 de la pantalla/alero de salida no pasa donde la socavación
  baja el desplante.
- **Sin juego:** ningún punto pasa de la Fase 2 (falta `luz_m`, que no es columna del CSV). Bloqueos: luz (4),
  `L_hidraulico_m` (B-01), VC1-01 (C-01), y en el proyecto `categoria_refuerzo_aashto` (3) y
  `exposicion_quimica_ems` (1). Ninguna excepción fuera de `ErrorProyecto` en ninguna de las ~70 corridas.

## 5. Qué [A] mueven un diámetro o un veredicto dentro de su ventana (`docs/validacion_sensibilidad.md`)

31 barridos (17 del conducto, 14 del cabezal), una clave a la vez, sobre el juego:

- **Mueven el diseño (5):** `v_max_concreto_eleccion` (opcional; 3.0 m/s → A-01 pasa de concreto Ø 0.90 a **TMC
  Ø 1.20**), `regimen_v2b` (`umbral_duro` → C-01 no dimensiona), `borde_libre_y_sobre_d_max` (0.6 → A-01 Ø 1.05;
  0.0 → nada dimensiona), `embocadura_cabezal` (`cabezal_recto` → C-01 se detiene en la coherencia con
  `embocadura_cajon`: dos criterios acoplados), `seccion_receptor` sin `TW_m`.
- **Mueven veredictos (14):** η del cruce, y en el cabezal `factor_muro_eleccion`, `gamma_EQ`, δ/φ,
  `fila_phi_estabilidad_cabezal`, `factores_inclinacion_carga_portante`, `regla_pendiente_relleno_trasdos`,
  `regimen_resistencia_elementos_cabezal`, η_D, η_R, `marco_estabilidad_cabezal`, `regimen_cabezal`,
  `drenaje_trasdos`, `fc_cabezal_mpa`.
- **Sólo el HW (2):** `n_manning_cajon` (0.6230 → 0.6234 m), `ke_entrada` (A-01 1.042 → 1.062 m con 0.9).
- **Leídos sin efecto (7):** `HW_D_max`, `v_max_tmc`, `v_max_hdpe`, `fraccion_llena_mayor_parte`,
  `instalacion_estandar_concreto`, `carga_viva_bajo_relleno_alto`, `duracion_caudal_pico_socavacion_min`.
- **No los lee la corrida (3), con razón escrita y testada:** `borde_libre_bajo_tw_ahogante` (TW 0.30 < 0.675 m),
  `seccion_receptor` con `TW_m` declarado, `hw_entrada_fuera_de_rango`.

## 6. Defectos de cálculo dejados en `xfail(strict=True)` (no corregidos)

1. **Diagnóstico** (ficha T11-03): sin `TW_m`, A-01 sube hasta Ø 1.80 m, donde la clave queda 0.025 m sobre la
   subrasante; `M5.altura_relleno_sobre_clave` lo levanta como `DatoInvalidoError` sobre 'cota_subrasante', MD da
   el material por «no evaluable» y el `DisenoNoFactibleError` final no trae `delta_rasante_m` (CLAUDE.md lo exige
   «si aplica»). Test: `test_el_escalon_que_no_cabe_bajo_la_subrasante_es_no_factible_por_rasante`. No mueve ningún
   número del fixture. El mismo diagnóstico sale en la variante `caudal_calculado` (cuencas sintéticas).

Observaciones que **no** clasifiqué como defecto (para el auditor):
- Con `exposicion_quimica_ems` declarado y exposición insignificante (sin f'c mínimo), la fila A7 no aparece y no
  hay aviso (`M9`, rama `requisitos.fc_min_MPa is None`). No se rellena nada; es un hueco de transparencia.
- En el JSON, `diseno.HW_salida_m` conserva la aproximación h_o SUSTITUIDA cuando el perfil la reemplaza
  (A-02, B-01: `perfil_sustituye_aproximacion = true`, el perfil S1 no alcanza la entrada). Documentado en
  `docs/validacion_hy8.md` §4; un consumidor del JSON tiene que leer las dos claves.

## 7. Números movidos

**Diámetros, secciones, materiales y HW movidos: ninguno.** Línea base de la Familia C regenerada y medida contra
`14f6138`: sólo cambia `alcance.declarado` (5 → 7 entradas; las cinco anteriores idénticas) en los cuatro JSON, dos
líneas en los cinco `cli_*.txt` y dos `<li>` en las tres memorias. Comparador de E-B: los cuatro JSON **IGUALES**
(0 diferencias, 0 no comparables); quitando `alcance.declarado`, cada JSON es igual al de la base.
`memoria_punto_cajon.html` y los dos CSV de resumen idénticos (`cmp`). README de la línea base con la sección de
T-11.

## 8. Diferidos con símbolo (Parte LIV provisional; fichas T11-01..08)

T11-01 juego por las puertas (`juego_validacion_integral.py::OMITIDAS_A_PROPOSITO`) · T11-02 lista exacta y §7
(`validacion_integral.py::lista_exacta`) · T11-03 defecto de diagnóstico (el test xfail) · T11-04 validación
externa y HY-8 (`validacion_externa.py::EJEMPLOS_HEC14`) · T11-05 sensibilidad (`sensibilidad.py::BARRIDOS`) ·
T11-06 tercera corrida del índice (`indice_formulas.py::CORRIDAS_DE_REFERENCIA`) · T11-07 alcance declarado
(`modelos.py::ALCANCE_DECLARADO`) · T11-08 rojo no escrito primero.

`INF-` no cerrados, con quién los destraba (19): `INF-5.1.8` parcial (estudio hidrológico: área del tramo);
`INF-5.2.1`–`5.2.4`, `5.2.6`, `5.2.7` abiertos (T-12: historial, material de IA, PDF con copyright, fixtures,
fuentes ausentes —ejemplar legible de M 170M y M 294 original del dueño—, LICENSE/pyproject); `INF-3.1.1` parcial
(delimitación de cuencas: estudio hidrológico); `INF-3.1.4` parcial (R y n del TR: Propietario); `INF-3.2.2` parcial
(HY-8: autor); `INF-3.2.5` verificado sin corrección; `INF-3.2.6` parcial (nivel del receptor medido: ANA/Junta);
`INF-3.2.8` parcial (levantamiento del receptor: ANA/Junta/topografía); `INF-3.2.9` abierto (n del cauce: dato,
T2-06); `INF-3.4.3`, `3.4.4`, `3.4.6` abiertos (propuesta de cierre, §1); `INF-4.3` parcial (cabezal paralelo del
marco, T7A-03); `INF-0.5` abierto (propuesta de cierre, §1).

## 9. Filas del tracker a escribir al integrar

- `INF-0.5` → Cerrado (T-11), Responsable «Claude Code (cadena T, T-11)», nota: validación integral §2, §3, §6.
- `INF-3.2.2` → NOTA (sigue parcial): HDS-5/HEC-14 en `docs/validacion_hds5.md`; procedimiento HY-8.
- `INF-3.4.3`, `INF-3.4.4`, `INF-3.4.6` → decisión del integrador (propuesta: Cerrado por T-7b, verificado por T-11).
- NOTA en `INF-5.1.8` (estado real) y en `INF-5.1.3`, `INF-5.1.9`, `INF-5.1.16` (estado real: cerrados).
- `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`: fila de T-11.
- `CLAUDE.md` (FASE B): tabla de pares y collected (6411), «desde T-10 son DOS corridas» → tres, `-m pdf` 145 → 150,
  saltos sin `NORMAS_DIR` 18 → 23 (los 5 de HEC-14 de T-11).

## 10. Suite

Medida sobre la rama `tesis/T-11` en `0f190e9` (el árbol de `c774035` sólo cambia el sello del índice), con
`NORMAS_DIR=/home/user/andy-rba30/normas`, PyMuPDF sí, Tk no: **6387 passed, 23 skipped, 1 xfailed; collected
6411** (= 6387 + 23 + 1; el xfailed es el defecto T11-03). Base `14f6138`: 6337 / 23 / 6360. Los 23 saltos son los
mismos de la base (los cinco `pdf` nuevos de HEC-14 corren con `NORMAS_DIR`). Sin `NORMAS_DIR` no se midió; derivado:
6364 passed, 46 skipped, 1 xfailed (6319 + 45; los cinco de HEC-14 saltan). Una primera corrida dio 1 failed
(`test_guardias_de_la_suite::test_ningun_assert_compara_floats_con_igualdad_exacta`: dos `== 0.3`/`== 2.3` del
punto 1); corregido con `pytest.approx(…, rel=REL_TRANSPORTE)` y remedido.

## 11. Preguntas

1. ¿Cierra el integrador `INF-0.5`, `INF-3.4.3`, `INF-3.4.4` e `INF-3.4.6` (§1)? Recomiendo sí con la evidencia.
2. La tolerancia de la comparación con HY-8 (3 % coincide / 3–10 % explicar / >10 % discrepancia) es propuesta de
   T-11: ¿la acepta el dueño?
3. El defecto T11-03: ¿lo corrige Fable o Opus? Es de diagnóstico (MD/M5), no de fórmula ni de cita.
4. El hallazgo `v_max_concreto_eleccion` = 3.0 m/s → TMC Ø 1.20 en A-01: el criterio es opcional y sin valor; con
   él declarado al extremo inferior de la Tabla Nº 10 el diseño cambia de material. ¿Lo quiere declarar el dueño?

## 12. Lo que NO hice

- No corrí HY-8 (no está en el entorno) ni afirmo resultados suyos.
- No corregí el defecto de diagnóstico (T11-03), ni las dos observaciones de §6.
- No barrí todos los [A]: 31 barridos de una lista razonada; los ensayos (φ, c, γ) no se barren.
- No toqué el `.xlsx`, la tabla de `CLAUDE.md`, `docs/linea_base.md` ni `verificar_sesion.py` (FASE B).
- Los documentos generados (`indice_formulas.md`) llevan un sello provisional con el par de la base; se resellan al
  integrar. `manifiesto_citas.md`, `manifiesto_registro_normativo.md` y `trazabilidad.csv` no se tocaron (ninguna
  cita, criterio ni fundamento cambió).
- No medí las otras tres configuraciones (sin Tk; PyMuPDF no se desinstaló).
