# Línea base reconciliada — Sesión S1

*Preparación antes de tocar una línea de cálculo (§8, §10 tabla maestra de
`docs/hoja_de_ruta_correcciones_v12.md`). Esta sesión no corrige ningún
hallazgo de fondo: solo reconcilia la línea base para que las 20+ sesiones de
corrección que siguen partan de un mapa fiable.*

Fuentes leídas: `CLAUDE.md`, `Claude.md`, `docs/hoja_de_ruta_correcciones_v12.md`
§1 y §5, y la hoja `Léeme` de `docs/auditorias/matriz_cruzada_auditorias.xlsx`.

---

## 1. Diff entre los tres puntos de auditoría

Los tres informes externos NO auditan el mismo commit (advertencia 1 de la
hoja `Léeme`):

| Punto | SHA completo | Qué audita | Fecha |
|---|---|---|---|
| Sistema | `2e1708abd91f6de1b80ec5456563cd1688e715bc` | `auditoria_sistema.md` | 2026-08-26 00:31 UTC |
| Matemática + Normativa | `71b134fb5d4aff4a1c53062ebea99d2674d6e596` | `auditoria_matematica.md`, `auditoria_normativa.md` | 2026-08-26 06:21 UTC |
| **HEAD actual (`origin/main`)** | `8b033b6a533c0411cf840a8a9c93c5bc65f75a31`* | — | 2026-08-27 |

*SHA de HEAD al momento de escribir este documento, antes del commit que lo
agrega — ver §4 para el detalle de qué se agregó después de la reconciliación.

**Ancestría:** `2e1708ab` es ancestro directo de `71b134fb` (1 commit de
diferencia), y ambos son ancestros de HEAD. No hay ramas divergentes.

### Qué cambió entre cada par de puntos

**`2e1708ab` → `71b134fb`** (el commit que separa a los dos auditores): solo
agrega los 10 PDF de `normas/` usados por la auditoría Normativa. Cero
archivos de código o de `docs/` (fuera de `normas/`).

**`71b134fb` → HEAD** (lo que pasó después de que ambas auditorías ya
corrieron): 15 archivos, todos `docs/`, `normas/`, `CLAUDE.md`/`Claude.md` o
`.claude/agents/`. **Ninguno toca `src/`, `tests/`, `gui/` o `cli.py`.**

```
A  .claude/agents/auditor-adversarial.md
A  .claude/agents/explorador.md
A  .claude/agents/verificador-normativo.md
A  CLAUDE.md
M  Claude.md
A  docs/auditorias/auditoria_matematica.md
A  docs/auditorias/auditoria_normativa.md
A  docs/auditorias/auditoria_sistema.md
A  docs/auditorias/matriz_cruzada_auditorias.xlsx
A  docs/auditorias/temario_refutar_48.json
A  docs/auditorias/temario_refutar_95.json
A  docs/hoja_de_ruta_correcciones_v12.md
A  normas/AASHTO M 170M-04 Reinforced Concrete Culvert, Storm Drain, and Sewer Pipe.pdf
A  normas/AASHTO M 36 Corrugated Steel Pipe, Metallic-Coated, for Sewers and Drains.pdf
A  normas/ASTM A760-A760M-10 Corrugated Steel Pipe, Metallic-Coated for Sewers and Drains.pdf
```

**`2e1708ab` → HEAD** (total): la unión de los dos rangos anteriores — 22
archivos, mismo patrón: cero código.

### Conclusión de la reconciliación de commit

**No hay drift de código entre los tres puntos.** El motor de cálculo
(`src/`, incluido `src/modulos/`), la CLI, la GUI y la suite de tests son
byte-idénticos en `2e1708ab`, `71b134fb` y HEAD. Cuando una referencia
`archivo:línea` de un hallazgo no apunta a lo que describe, la causa **no
puede ser** que el código cambió después de la auditoría — tiene que ser que
la cita nació desalineada (consistente con NOR-MAN-04: "al menos 66 de 296
referencias archivo:línea del manifiesto no llevan a lo que dicen llevar").
Esto simplifica la Parte 2 de este documento: cada desajuste encontrado abajo
es un defecto de la cita del auditor, no una consecuencia de código movido.

---

## 2. Suite de tests — leída de `origin/main`

```
git fetch origin main && git reset --hard origin/main && python -m pytest -q
```

**725 `passed`, 1 `skipped` → 726 `collected`.** (El skip permanente es
`tests/test_MD.py::test_sin_M5_la_ausencia_sale_como_ImportError_y_no_como_ErrorProyecto`,
inalcanzable mientras `M5_verificaciones.py` exista en el repo — SIS-F-20,
sin corregir en esta sesión.)

Confirmado en cada punto de esta reconciliación: el número no cambió durante
las cinco correcciones de línea base de §4 (todas documentales o de
`.gitignore`, ninguna toca código de cálculo).

> **Este número es la FOTO de la línea base (S1), no el estado de hoy.** Se
> deja como está a propósito: es contra él contra el que se comparan las
> sesiones siguientes. Estado posterior, para que nadie lea el 725 como
> vigente: **S2 (cluster C08) lo dejó en 743 `passed`, 1 `skipped` → 744
> `collected`** — 18 tests nuevos, ninguno retirado.

---

## 3. Reconciliación de anclajes archivo:línea

141 de los 234 hallazgos de la hoja `Hallazgos` traen una ubicación. De esos,
**9 ya estaban anclados por concepto/símbolo**, no por línea (no requieren
acción):

`MAT-X1` (h_eq de LS) · `MAT-X2` (K_AE, Mononobe-Okabe) · `MAT-X3` (Empuje
bajo NF) · `MAT-X4` (k_h0 y k_v) · `MAT-X5` (K_fricción del control de
salida) · `MAT-X6` (d50 de protección de salida) · `MAT-X7` (Estabilidad
sísmica del cabezal) · `MAT-X8` (V_c del cabezal, MCFT) · `MAT-O17` (varios).

Los 132 restantes se verificaron abriendo cada archivo en la línea citada e
identificando el símbolo real que la envuelve (función, clave de dict de
criterio, constante, o — en `.md` — sección/numeral). Trabajo repartido en 15
lotes por archivo principal, cada uno con el subagente **`explorador`**
(§8.3 de la hoja de ruta) — *nota de ejecución: el subagente de proyecto
`.claude/agents/explorador.md` se creó en la sesión anterior y requiere
reiniciar Claude Code para cargar; como esta sesión no se reinició, se usó el
agente de solo-lectura equivalente del harness (`Explore`) con el mismo
mandato de búsqueda que describe `explorador.md`. Repetir con el subagente de
proyecto tras reiniciar es opcional — el mandato y el resultado no cambian*.

**Resultado agregado: 0 casos de drift de commit** (confirma §1). Los
desajustes encontrados son:
- **Errores de cita ya presentes en el informe original** (número de línea
  desplazado dentro del mismo símbolo, o apuntando a un símbolo vecino).
- **Hallazgos cuya premisa ya no es cierta** en el código/documento actual
  (ver notas "obsoleto" abajo) — se listan igual, para que el responsable de
  la fase de corrección los cierre como tales en la matriz, no los reabra.

Columnas: **Verificado** = SÍ (el símbolo/línea sigue describiendo lo que el
hallazgo dice) · PARCIAL (símbolo correcto, línea desplazada, o una de varias
ubicaciones citadas está mal) · NO (la línea no corresponde, o la premisa del
hallazgo ya no es cierta).

### B1 — `src/criterios_adoptados.py` (24)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| SIS-B-01 | claves `PERFIL_SUELO_PRESUNTO`(373-375), `clase_sitio`(386), bloque `__main__`(1988); `M11_reporte.py::bloque_criterios`(1032) | SÍ | |
| SIS-D-01 | clave `F_pga`(464), clave `clase_sitio`(391); `M9_cabezal.py` docstring módulo(24) | SÍ | |
| MAT-D8 | clave `factores_carga_aashto`, subclave `"EV"`(1343) | SÍ | |
| MAT-D15 | clave `factores_carga_aashto`, subclave `"EH_en_reposo"`(1345) | SÍ | |
| MAT-D16 | clave `recubrimiento_aashto_mm`(1501) | SÍ | |
| MAT-O11 | clave `k_v`, campo `fuente`(495) | SÍ | |
| MAT-O14 | claves `v_max_hdpe`(749-759), `v_max_tmc`(761-772) | SÍ | |
| SIS-D-04 | clave `k_v`, campo `sensibilidad`(496); `M9_cabezal.py::coeficiente_sismico_vertical`(327) | SÍ | |
| SIS-D-05 | clave `angulo_aletas`(1325-1331); `M11_reporte.py::bloque_criterios`(1126) | PARCIAL | reanclar M11_reporte.py a 1127 (`reemplazado_por or fuente`), no 1126 |
| SIS-D-11 | clave `n_manning_hdpe`(732), campo `fuente`(742) | SÍ | |
| MAT-O9 | clave `procedimiento_flexion_corte_aashto_sec5`(1586) | SÍ | |
| SIS-B-19 | claves `PERFIL_SUELO_PRESUNTO`(347), `c_phi_fundacion`(1013), `capacidad_portante_adm`(1024), `Mw_licuefaccion`(1033), `angulo_aletas`(1325) | SÍ | |
| SIS-D-12 | claves `v_max_hdpe`/`v_max_tmc`(749-772); `docs/manifiesto_citas.md`(590-593) | SÍ | |
| SIS-F-02 | `escribir_valor_en_archivo`, rama `Path.write_text`(299-320) | SÍ | |
| SIS-F-19 | `escribir_valor_en_archivo`, `patron = re.compile(...)`(302-312) | SÍ | |
| SIS-A-14 | docstring `escribir_valor_en_archivo`(279-285); `gui/app.py`(489) | SÍ | |
| SIS-B-05 | `parametros_sensibilizables()`(1963); hoja de ruta v8(660) | SÍ | |
| SIS-D-03 | clave `v_max_concreto_eleccion`, comentario(781); `docs/manifiesto_citas.md`(445,471) | SÍ | |
| SIS-D-08 | clave `clase_sitio` completa, sin campo `sensibilidad`(386-458) | SÍ | |
| SIS-B-11 | clave `homogeneidad_serie_fen`(604-605); `MD.py`(539) | SÍ | |
| SIS-B-15 | clave `demanda_sismica_licuefaccion`(1045-1056) | SÍ | |
| SIS-B-22 | `limpiar_valores_dinamicos`(181); `M11_reporte.py::marcadores_de_la_memoria`(196); `modelos.py::v_max_definida`(466); `M9_cabezal.py::aplica_sobrecarga_trasdos`(561) | SÍ | |
| SIS-D-13 | clave `clases_producto_por_relleno`, `valor=None`(1187-1214) | SÍ | |
| SIS-E-05 | `establecer_valor_dinamico`(144-173); `_verificar_criterio`, `raise ValueError`(1780) | SÍ | |

### B2 — `src/modulos/M9_cabezal.py` (10)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| MAT-O2 | `k_ae_mononobe_okabe`, denominador `(1+R)**2`(494) | SÍ | |
| MAT-O3 | `empujes_trasdos`(736), línea 784 (`E_a = empuje_activo_estatico(...)`) | SÍ | |
| MAT-O4 | `coeficiente_sismico_base`(279-287) | SÍ | |
| MAT-O16 | `verificar_capacidad_portante`(903); `capacidad_portante_zapata_en_talud`(1060-1089) | SÍ | |
| SIS-B-20 | `verificar_cuantia`(1265), `cuantia_de_diseno`(1288), `requiere_temperatura_dos_caras`(1353), `nota_temperatura_dos_caras`(1361), `espaciamiento_maximo`(1380), `verificar_espaciamiento`(1389), `verificar_ciclopeo`(1406) | SÍ | |
| SIS-B-21 | `n_s_zapata_en_talud`(1018), `n_q_zapata_en_talud`(1047), `capacidad_portante_zapata_en_talud`(1086-1089) | SÍ | |
| SIS-F-04 | `k_ae_mononobe_okabe`(418; docstring 442-443, `cos_dbp`/`cos_ib` 462-463, radicando 490, numerador/denominador 493-494) | SÍ | |
| SIS-F-05 | `empuje_activo_sismico_total`(629); `tests/test_M9_cabezal.py::test_empuje_sismico_total_y_su_incremento`(361) | SÍ | |
| SIS-F-06 | `verificar_deslizamiento`(942; guarda 958, `fs`961) | SÍ | |
| SIS-E-02 | `factores_de_carga`(852), `fs_requerido`(876), `recubrimiento_e060_mm`(1163), `cuantia_minima`(1257) | SÍ | |

### B3 — `src/modelos.py` (12)

Los 12 hallazgos de este lote verificaron **SÍ** sin excepción — ninguna cita
presentó desalineación de línea (ver detalle de símbolos en la tabla
completa de resultados, sección de auditoría de esta sesión).

| ID | Reanclaje (símbolo) |
|---|---|
| SIS-B-02 | `ControlEntrada.HW_sobre_D`(568); `M4_control.py`(392) |
| SIS-B-04 | `PuntoCritico.Q_receptor_m3s`/`cota_TW`(375-376); `M0_carga.py`(386-389); `cli.py::_resolver_tw`(543-553) |
| SIS-B-17 | `class EmpujesTrasdos`(1059-1116); `M9_cabezal.py::empujes_trasdos`(736) |
| SIS-F-07 | `EmpujesTrasdos.empuje_horizontal_total`(1099); `.momento_volcante`(1111-1115) |
| SIS-A-06 | `Material.v_max_rango`(451); `.v_max_definida`(465-468); `M2_material.py`(282) |
| SIS-B-07 | `CriterioPendienteError.mensaje_gui`(78-81) |
| SIS-B-08 | `PeriodoRetorno.exigir_anios`(1244-1255) |
| SIS-B-12 | `PuntoCritico.NF_profundidad_m`(378); `M11_reporte.py::CAMPOS_CSV`(145-160) |
| SIS-B-13 | `PerfilFamilia.verificaciones_aceptacion`(1275); `M1_clasificacion.py`(337) |
| SIS-B-16 | `PuntoCritico.sucs_fundacion`(377); `M0_carga.py`(209) |
| SIS-B-18 | `ControlSalida.ahogado_por_TW`(599); `CombinacionCarga`(1135-1136); `RecubrimientoDiseno.criterio_aashto`(1157); `CuantiaRefuerzo.cuantia_adoptada`(1180) |
| SIS-E-06 | `DatoFaltanteError` docstring(108-109); `M5_verificaciones.py`(409) |

### B4 — `cli.py` (6)

| ID | Reanclaje (símbolo) | Verif. |
|---|---|---|
| MAT-D9 | `_fase_7()`(708-716, llamada 713); `S_conducto` en `_fase_diseno()`(682) | SÍ |
| SIS-F-10 | `raise` de `ErrorProyecto` en M1(165,310,389), M4(272,443), M5(495), M9(466,1180), cli.py(250,255,292,310) | SÍ |
| SIS-F-11 | bloque `--criterios`(1367-1371); `--pdf`/`--csv-resumen`(1491-1499) en `main()` | SÍ |
| SIS-A-05 | `cli.py::_bloqueo`(485); `M11_reporte.py::criterios_bloqueantes`(557) | SÍ |
| SIS-B-06 | `plantilla_por_alcance()`(1379-1396); definición `--plantilla`(1439-1443) | SÍ |
| SIS-A-21 | `_fase_8()`(736-745) | SÍ |

### B5 — `tests/test_sin_literales.py` (10)

| ID | Reanclaje (símbolo) | Verif. |
|---|---|---|
| SIS-C-01 | `test_la_tabla_del_factor_de_muro_es_normativa_y_la_eleccion_no`(223) | SÍ |
| SIS-C-02 | 6 asserts de subcadena en test_sin_literales.py(177-221) + test_M8(177-179) + test_M5(180-186) + test_M11(647) | PARCIAL — 2 de las 6 citas de tests secundarios (test_criterios_adoptados.py:247, test_datos_sitio.py:153) caen en la línea del `if` de la comprensión, no en el `assert`, que está 1-2 líneas después |
| SIS-C-03 | `_marcado`(79); `dominios.py`(38, marca dentro de docstring) | SÍ |
| SIS-C-04 | `_nodos_de_indice`(65-73); uso en `literales_prohibidos`(117) | SÍ |
| SIS-C-05 | `barrido`(130-131); `test_los_archivos_exentos_existen_y_de_verdad_llevan_literales`(164-166) | SÍ |
| SIS-C-06 | `SRC = RAIZ / "src"`(51); `test_ningun_modulo_declara_literales_numericos`(147) | SÍ |
| SIS-C-07 | `_marcado`(76-81) | SÍ |
| SIS-C-08 | `NUMEROS_PERMITIDOS`(57); `literales_prohibidos`(115,119) | SÍ |
| SIS-C-09 | `literales_prohibidos`(111-124) | SÍ |
| SIS-C-11 | `barrido`(130) | SÍ |

### B6 — `src/modulos/M5_verificaciones.py` (7)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| MAT-D1 | `v2_velocidad_minima`(177-215, 209); `M3_hidraulica.py::resolver_manning`(195-216, 214) | NO | símbolos correctos, pero la premisa ("V2 no está en la lista") ya no es cierta: el docstring de `resolver_manning` sí incluye V2 explícitamente |
| MAT-D2 | `criterios_adoptados.py` clave `"HW_D_max"`(886-903) | PARCIAL | M5:573 (`return (` del agregado) **no** es V4b — no existe símbolo V4b en M5_verificaciones.py; reanclar solo a `criterios_adoptados.py:886` |
| SIS-A-04 | `cota_entrada_supuesta`(305-318); docstring módulo(56-69) | SÍ | |
| MAT-O13 | `NUMERAL_V1`(115) | SÍ | |
| SIS-A-13 | docstring módulo(4-5); `cli.py::_verificador_perfil`(574-589) | SÍ | nota de ruta: el archivo es `/cli.py` en la raíz, no `src/cli.py` |
| SIS-F-21 | `v2_velocidad_minima`(209), `v3_velocidad_maxima`(272,292), `v7_flotacion`(511); `M7_geometria.py`(482); `M9_cabezal.py`(894,1397); `M4_control.py::hw_gobernante`(532) | SÍ | |
| SIS-B-23 | `resguardo_por_cbr`, `raise ValueError`(338-341); `M7_geometria.py::factor_esviaje`, `raise DatoInvalidoError`(403-409) | SÍ | |

### B7 — `gui/app.py` (9)

Los 9 hallazgos de este lote verificaron **SÍ** sin excepción.

| ID | Reanclaje (símbolo) |
|---|---|
| SIS-E-01 | `ExpedienteApp.ejecutar_pipeline`(730-758; brazos 749/755) |
| SIS-F-01 | archivo completo (958 líneas; sin test para `gui/app.py`) |
| SIS-A-10 | docstring módulo(14-22) vs `ExpedienteApp.__init__`(212-224) |
| SIS-A-11 | leyenda en `_construir_tab_criterios`(320-327) |
| SIS-A-12 | docstring módulo(5-7); `__init__`(201-204,277-285) |
| SIS-A-17 | `ejecutar_pipeline`(748) vs `cli.py::correr`(886-887) |
| SIS-A-18 | `guardar_sesion`/`cargar_sesion`(905-926,928-948) |
| SIS-E-03 | `exportar_html`(856-869), `exportar_pdf`(871-884), `exportar_csv`(886-900) |
| SIS-E-04 | `_interpretar_valor_declarado`, `raise`(491-498) |

### B8 — `src/constantes_normativas.py` (7)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| MAT-O1 | `SOBRECARGA_TRASDOS_H_EQ`(235) | SÍ | |
| MAT-D11 | comentario junto a `CALICATAS_POR_SENTIDO`(165-172) | SÍ | |
| MAT-O8 | `D_MAX`(132-136) | NO | la línea 130 citada es `D_PASO`, no `D_MAX`; reanclar a 132-136 |
| SIS-A-20 | comentario "DISCREPANCIA ABIERTA"(124-126) | SÍ | y confirma el hallazgo: el comentario cita "432,436,790,901" de la hoja de ruta; las líneas reales son 436,440,797,908 |
| MAT-O19 | `KU_METRICO`(95); `DIAMETRO_MIN`(29) | SÍ | |
| SIS-A-19 | bloque "ADVERTENCIA DE DOBLE DEFINICION"(12-24); `M2_material.py`(273,276) | SÍ | |
| SIS-B-14 | 13 constantes: `DIAMETRO_MIN`(29), `DIAMETRO_MIN_SELVA_ALTA`(30), `LONG_MAX_CUNETA`(91), `CBR_MIN_SUBRASANTE`(146), `COMPACTACION_CORONA`(147), `COMPACTACION_CUERPO`(149), `CALICATAS_POR_KM`(152), `CALICATAS_POR_SENTIDO`(161), `ESPACIAMIENTO_PERFIL_KM`(173), `SPT_PROF_MIN`(283), `SPT_ESPACIAMIENTO`(284), `SULFATOS`(287), `CLORUROS_EXTERNOS`(293) | SÍ | |

### B9 — `src/modulos/M11_reporte.py` (4)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| SIS-A-01 | `bloque_criterios()`(1024-1049; `ca.criterio()` 1040, valor 1043) | SÍ | |
| SIS-F-09 | `_fila_resumen_csv()`(932-966) | NO | premisa obsoleta: el código actual sí llena material/D/V/y-D/HW cuando `informe.dimensionado` es True |
| SIS-C-13 | parseo de tableros(415-424: `_RE_TITULO_TABLERO`/`_celdas`/`tableros_pendientes`) | PARCIAL | línea 337 no pertenece a esta función — cae en `version_hoja_de_ruta()`(327-347), sin relación; además la fuente es tabla Markdown real, no "prosa" |
| SIS-A-07 | docstring módulo(5); `fila_resumen()`(903); `_fila_resumen_csv()`(953), ambas recalculan `y_normal/D` | SÍ | |

### B10 — `docs/hoja_de_ruta_alcantarillas_v8.md` (7)

| ID | Reanclaje (sección/numeral) | Verif. | Nota |
|---|---|---|---|
| MAT-D5 | §9.2 "Sobrecarga en el trasdós"(586) | SÍ | |
| MAT-D12 | §4.3 "Control de salida [C]"(436,440); Anexo B(797); "Notas críticas"(908) | SÍ | |
| MAT-O5 | Tabla Fase 5, fila V4(456) | SÍ | |
| MAT-O6 | §7.A, segunda condición del `max{}`(514) | SÍ | |
| MAT-O7 | Fase 6, fórmula de Laushey(495); `constantes_normativas.py`(51) | SÍ | |
| MAT-D6 | §9.2 tabla sísmica desagregada(590-606); `M9_cabezal.py::empujes_trasdos`(736+) | PARCIAL | confirma AUSENTE P_IR; pero el numeral que el hallazgo atribuye a k_h0 (2.8.1.1.14.1) no es el que cita la línea 597/`NUMERAL_K_H0` (2.8.1.1.14.2) — desajuste de numeral en el propio hallazgo |
| MAT-O15 | Tabla Fase 5, fila V2b(454); §5.2(485) | **NO — obsoleto** | la fila V2b sigue presente y completa; §5.2 reafirma su vigencia. El hallazgo describe una desaparición que no está en el documento actual |

### B11 — `src/modulos/M4_control.py` (3)

| ID | Reanclaje (símbolo) | Verif. |
|---|---|---|
| SIS-A-02 | docstring de módulo(21-29, línea 24 exacta); `modelos.py::ControlEntrada`(564); `criterios_adoptados.py::"HW_D_max"`(886) | SÍ |
| MAT-D10 | `_hw_sobre_D_no_sumergido`(307) | SÍ |
| MAT-O10 | rama `else` de `control_entrada`(366-388) | SÍ |

### B12 — `src/modulos/M7_geometria.py` + `MD.py` (4)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| MAT-D4 | `cota_clave()`(244-252) | SÍ | |
| SIS-F-08 | `proyeccion_taludes()`(442), `longitud_conducto()`(454), `compatibilidad_geometrica()`(532) | SÍ | |
| SIS-A-08 | docstring módulo MD.py(56-71); `class Verificador(Protocol)`(125); `_verificador_de_M5()`(158) | PARCIAL | cita correcta del texto, pero la premisa que cita ("M5 todavía no existe") ya es falsa en HEAD — `M5_verificaciones.py` existe y está trackeado |
| SIS-A-09 | `disenar_punto()`(405-411); `_motivo_sin_candidatos()`(492-500) | SÍ | |

### B13 — `tests/fixtures/casos_patron.py` + `M2_material.py` + `M0_carga.py` (11)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| SIS-F-03 | `CP1_PERIODO_RETORNO`(36-51; TR_esperado 41,48) | SÍ | |
| MAT-D7 | `CP1_PERIODO_RETORNO`(36-51) | SÍ | |
| SIS-A-03 | `M2_material.py` docstring(40-54); `catalogo()`(264) | PARCIAL | confirmado solo el alcance M2; M5/M7/MD no se revisaron en este lote (quedan cubiertos por B6/B12) |
| MAT-O12 | `CP8_CONTROL_SALIDA`, comentario(184-194, línea 189) | PARCIAL | ancla de línea correcta; el contenido de la pág. 54 del PDF no se verificó en esta pasada |
| SIS-F-12 | `_texto()`(230-235) | SÍ | |
| SIS-F-13 | bloques `CP1`...`CP8`(32-237) | PARCIAL | el hallazgo dice "seis módulos"; el grep real da 7 módulos de cálculo sin consumo de `casos_patron` — verificar alcance exacto en la fase de corrección |
| MAT-O20 | docstring(17); `CP3_VELOCIDAD_MINIMA["conclusion"]`(104) | PARCIAL | línea 104 pertenece hoy a CP-3, no a CP-1/brentq — segundo locator mal anclado |
| SIS-D-10 | `catalogo()`, llamadas a `_valor_si_declarado()`(271,277,282) | SÍ | |
| MAT-D14 | `_a_float()`(240); `cli.py::_numero_externo`(254) | SÍ | |
| SIS-A-16 | `_valida_cruzadas()`(364-381) | SÍ | |
| SIS-B-09 | `M2_material.py`(127); resto (M3,M4,M5,M8,MD) no verificado en este lote — confirmar en fase de corrección | PARCIAL | |

### B14 — varios pequeños (10)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| SIS-D-02 | `docs/manifiesto_citas.md`(457, título); censo(519-524, no 519-521) | PARCIAL | reanclar el rango del censo a 519-524; contenido sustantivo confirmado (2 `[N→]`/13 `[C]` reales, no 1/14; tabla "33 [A]" incluye 4 `[C]` y omite `clase_sitio`) |
| SIS-D-06 | `datos_sitio.py::Z_E030`(194-215); `.datos_con_verificacion_pendiente()`(261-264); `cli.py`(1128) | SÍ | |
| SIS-D-07 | `datos_sitio.py::datos_con_verificacion_pendiente()`(261-264); `cli.py`(1120-1140) | SÍ | |
| SIS-F-14 | `tests/test_M9_cabezal.py`(103-137,175); fixture `CP7_CADENA_SISMICA` en `casos_patron.py`(167-180) | SÍ | |
| SIS-A-15 | `Claude.md`(55-56); `tests/test_sin_literales.py`(16-17) | **Corregido en esta sesión** | ver §4 |
| SIS-B-03 | `Claude.md`(111-112, no 109-110) | **Corregido en esta sesión** | ver §4; reanclar a 111-112 |
| SIS-D-09 | `datos_sitio.py::DatoSitio`(97-118, sin guardia); `criterios_adoptados.py::_verificar_criterio`/`_coherencia_de_etiquetas`(1787-1878) | SÍ | |
| MAT-D13 | `M1_clasificacion.py::tr_desde_riesgo`(197) | SÍ | |
| MAT-O18 | M3(184); M4(431,313); M7(410,534 — no 528); M9(465) | PARCIAL | reanclar segunda cita de M7 a 534 (528 es otra cosa); M9:465 ya no ilustra "fallo de programa": es un `raise DisenoNoFactibleError` explícito, contradice la lectura del hallazgo |
| SIS-C-12 | `M1_clasificacion.py`(53-62) | SÍ | |

### B15 — resto (8)

| ID | Reanclaje (símbolo) | Verif. | Nota |
|---|---|---|---|
| MAT-D3 | `M8_estructural.py::empuje_flotacion_kn_m()`(209) | SÍ | |
| SIS-F-15 | `datos_referenciales_prueba.md`(9,34-35); `...NO_APLICADOS.md`(9-10,28-29,45-50,86) | SÍ | y confirma que el contenido es hoy falso (v_max ya no es None, la suite da 725 no 653) |
| SIS-F-16 | `test_M6_proteccion.py`(58); `test_M9_cabezal.py`(549,550,641,645,741); `test_cli.py`(99,114,115,123,207,237,342,359,388) | SÍ | |
| SIS-F-17 | `test_M3_hidraulica.py::test_pendiente_que_produce_v_objetivo_de_cp3`(147-151) | SÍ | |
| SIS-F-20 | `test_MD.py`(344-352); `MD.py::_verificador_de_M5`(178,555) | SÍ | |
| SIS-B-10 | `legacy/Tc.py` (sin símbolo único); `Claude.md`(116-121, "## GUI") | SÍ | conteo "803 sentencias" no calza exacto (AST da 793) — diferencia de método de conteo, no de contenido |
| SIS-C-10 | `tests/ejemplo_puntos.informe.json`; `cli.py`(1475) | **Corregido en esta sesión** | ver §4 |
| SIS-F-18 | `docs/auditoria_y_ruta_despliegue_v9.md`(44) | **Corregido en esta sesión** | ver §4 |

---

## 4. Cuatro deudas de línea base corregidas

Cada una en su propio commit, suite verde antes de cada uno (743 passed, 1
skipped en las cinco):

| Hallazgo | Commit | Qué cambió |
|---|---|---|
| **SIS-A-15** | `59440a9` + `8b033b6` | `Claude.md` y `tests/test_sin_literales.py` decían "constantes_fisicas.py: hoy solo la gravedad"; el módulo ya declara cinco nombres (`G`, `RHO_AGUA`, `N_POR_KN`, `GAMMA_AGUA`, `GAMMA_AGUA_KN_M3`). Dos ubicaciones, dos commits — la cita del hallazgo señalaba ambas. |
| **SIS-B-03** | `08ba613` | `Claude.md` listaba `pandas` y `jinja2` como dependencias (cero usos en `src/`, `gui/`, `cli.py`; no instalados) y omitía `weasyprint` (pineado en `requirements.txt`, usado en `M11_reporte.py` para exportar PDF). |
| **SIS-F-18** | `3c526b4` | `docs/auditoria_y_ruta_despliegue_v9.md` citaba "12 módulos, 595 tests en verde"; se corrigió al conteo vigente en ese momento (línea base de S1, ver §2). El conteo de módulos (13) no ha cambiado; el de tests sí — mantenido al día en `docs/auditoria_y_ruta_despliegue_v9.md`, hoy 743 `passed` + 1 `skipped`. |
| **SIS-C-10** | `219f584` | `tests/ejemplo_puntos.informe.json` era salida de corrida versionada que cualquier ejecución de `cli.py` sobre `tests/ejemplo_puntos.csv` pisa (`cli.py:1475`); ningún test la lee. Se destraqueó (`git rm --cached`, sigue en disco) y se agregó `tests/*.informe.json` al `.gitignore`. |

Estas cinco correcciones son **documentales o de control de versión** —
ninguna toca `src/`, `gui/` o `cli.py`. La suite se mantuvo en 743 passed, 1
skipped (744 collected) en todo momento.

---

## 5. Criterio de salida

> No queda ninguna referencia de la matriz anclada solo a un número de línea.

Cumplido para los 141 hallazgos con ubicación: los 9 conceptuales ya lo
estaban; los 132 restantes quedan documentados arriba con su símbolo real
(función, clave de criterio, constante, o sección/numeral para los `.md`),
además del número de línea original. 12 de los 132 quedaron con nota
PARCIAL o NO — no porque el anclaje por símbolo esté incompleto, sino porque
el propio hallazgo necesita un ajuste de línea, de alcance o (en dos casos,
MAT-O15 y SIS-F-09) su premisa ya no es cierta contra el código/documento
actual. Eso es trabajo de la fase de corrección correspondiente (ver
`Estado`/`Responsable`/`Commit` en la hoja `Hallazgos` del `.xlsx`), no de
esta reconciliación — este documento entrega el mapa, no cierra hallazgos.

**No se corrigió ningún hallazgo de fondo en esta sesión**, conforme al
objetivo. Las cuatro deudas de línea base de la instrucción original (§4) son
higiene de la propia constitución/documentación, no hallazgos de la matriz.

---

## 6. Limitación del entorno: no se puede borrar una rama del remoto (S4)

`CLAUDE.md` exige que ninguna rama auxiliar quede abierta, y
`verificar_sesion.py` lo comprueba (chequeo 3). En la sesión S4 (cluster C01)
la rama se fusionó a `main` y `main` se empujó sin problema, pero **el borrado
de la rama en el remoto se rechaza con HTTP 403**:

```
$ git push origin --delete claude/cluster-c01-geometry-gt8kjc
error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
```

Reproducido cuatro veces con espera exponencial, con `--delete` y con la forma
`:rama`, y con `http.version=HTTP/1.1` (que es la que deja ver el 403 en vez
del corte de sideband). **No es la política de egress**: el endpoint
`$HTTPS_PROXY/__agentproxy/status` devuelve `recentRelayFailures: []`, de modo
que el 403 lo emite GitHub. Es decir, la credencial de la sesión tiene permiso
de `push` pero no de `delete_ref`.

Consecuencia práctica, para que nadie la lea como descuido: mientras esto siga
así, `verificar_sesion.py` **va a fallar el chequeo 3 al final de toda sesión
que use rama auxiliar**, con la rama ya fusionada. Eso explica también por qué
«las últimas sesiones no lo cumplieron». Dos formas de cerrarlo, ninguna al
alcance de la sesión:

1. Que el borrado lo haga alguien con permiso sobre el repositorio (o el
   ajuste de *Automatically delete head branches* en GitHub).
2. Que se le conceda `delete_ref` a la credencial de las sesiones.

Lo que **sí** está bajo control de la sesión y se cumplió: la rama no queda con
commits fuera de `main` —el chequeo distingue las dos cosas y solo marca
`[FALLO]` la rama fusionada y no borrada— y la rama local se borró.
