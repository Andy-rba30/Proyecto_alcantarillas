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
> vigente: **S2 (cluster C08) lo dejó en 743 `passed`, 1 `skipped`** — 18
> tests nuevos, ninguno retirado —, y **S9 (cluster C04, cadena sísmica) lo
> dejó en 744 `passed`, 1 `skipped` → 745 `collected`**. S9 no escribió
> ningún test nuevo: el `+1` es la expansión de
> `test_criterio_pendiente_lanza_error_y_no_devuelve_default`, ya
> parametrizado sobre los criterios sin valor, al que le entró el vacío nuevo
> `gamma_EQ`. Un test se renombró (el del factor de muro) y ninguno se
> retiró. **S10 (cluster C07, recubrimiento) lo dejó en 749 `passed`, 1
> `skipped` → 750 `collected`**: cinco tests nuevos, y son la excepción
> deliberada a la regla de no escribir tests antes de la fase que les toca —
> no congelan el comportamiento actual, comprueban que los dos vacíos nuevos
> **detienen** el cálculo y que la fila ausente de una tabla no se lee como
> un «no». Eso era, hasta S10, una afirmación que solo vivía en la prosa de
> los docstrings.
>
> **S12 (clusters C11, C12 y C02 — el registro normativo) lo dejó en 843
> `passed`, 1 `skipped` → 844 `collected`**: 94 tests nuevos, ninguno
> retirado. Son la guardia del registro (T0–T24) y las pruebas de los tres
> clusters.
>
> **A partir de S12 el conteo depende de si `requirements-dev.txt` está
> instalado, y hay que decir cuál de los dos se cita.** Los 32 tests de
> `tests/test_normativa_pdf.py` —los que abren los PDF de `normas/` y hacen
> verdadera la palabra «verificado»— llevan `@pytest.mark.pdf` y se **saltan**
> si falta PyMuPDF. Los dos números:
>
> | Entorno | passed | skipped | collected |
> |---|---|---|---|
> | Con `pip install -r requirements-dev.txt` | **843** | 1 | 844 |
> | Sin PyMuPDF | **811** | 33 | 844 |
>
> `collected` **no** cambia entre los dos: lo que cambia es de qué lado del
> reparto caen esos 32. La regla vieja «`collected` = `passed` + 1» solo vale
> con PyMuPDF instalado; sin él el skip permanente de SIS-F-20 deja de ser el
> único. PyMuPDF es dependencia de **TEST**, no de producción: no está en
> `requirements.txt` y el software calculado no lo importa nunca.

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

Cada una en su propio commit, suite verde antes de cada uno. El conteo que se
cita abajo es el de HOY, no el de entonces: este documento se mantiene al día
con la suite vigente (1517 passed, 1 skipped) y no como fotografía de S1 —
`verificar_sesion.py` avisa si se desincroniza.

| Hallazgo | Commit | Qué cambió |
|---|---|---|
| **SIS-A-15** | `59440a9` + `8b033b6` | `Claude.md` y `tests/test_sin_literales.py` decían "constantes_fisicas.py: hoy solo la gravedad"; el módulo ya declara cinco nombres (`G`, `RHO_AGUA`, `N_POR_KN`, `GAMMA_AGUA`, `GAMMA_AGUA_KN_M3`). Dos ubicaciones, dos commits — la cita del hallazgo señalaba ambas. |
| **SIS-B-03** | `08ba613` | `Claude.md` listaba `pandas` y `jinja2` como dependencias (cero usos en `src/`, `gui/`, `cli.py`; no instalados) y omitía `weasyprint` (pineado en `requirements.txt`, usado en `M11_reporte.py` para exportar PDF). |
| **SIS-F-18** | `3c526b4` | `docs/auditoria_y_ruta_despliegue_v9.md` citaba "12 módulos, 595 tests en verde"; se corrigió al conteo vigente en ese momento (línea base de S1, ver §2). El conteo de módulos (13) no ha cambiado; el de tests sí — mantenido al día en `docs/auditoria_y_ruta_despliegue_v9.md`, hoy 843 `passed` + 1 `skipped` (811 + 33 sin PyMuPDF). |
| **SIS-C-10** | `219f584` | `tests/ejemplo_puntos.informe.json` era salida de corrida versionada que cualquier ejecución de `cli.py` sobre `tests/ejemplo_puntos.csv` pisa (`cli.py:1475`); ningún test la lee. Se destraqueó (`git rm --cached`, sigue en disco) y se agregó `tests/*.informe.json` al `.gitignore`. |

Estas cinco correcciones son **documentales o de control de versión** —
ninguna toca `src/`, `gui/` o `cli.py`. La suite se mantuvo verde en todo
momento; hoy son **1517 passed, 1 skipped (1518 collected)** con `requirements-dev.txt` instalado, u **1485 passed, 33 skipped** sin PyMuPDF — mismo `collected`, ver la tabla de §2.

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

**Reincidencia y saldo, al cierre de S9 (cluster C04).** El 403 se reprodujo
igual, y ya no es una rama sino **tres** las que están fusionadas en `main` y
sin borrar en el remoto:

| Rama | Sesión | Fusionada en `main` |
|---|---|---|
| `claude/cluster-c13-rasante-geometria-2p5fqc` | S7 | sí |
| `claude/cluster-c03-lrfd-factors-23mrzf` | S8 | sí |
| `claude/cluster-c04-sismica-ay9szt` | S9 | sí |

S9 intentó borrar las tres —la suya y las dos heredadas— y las tres
devolvieron el mismo `HTTP 403`. No hay tampoco herramienta de borrado de
referencias en el servidor MCP de GitHub de la sesión (`create_branch` existe,
`delete_branch` no). De modo que `verificar_sesion.py` seguirá dando
`[FALLO] … ya fusionada, debería estar borrada` tres veces, **y ninguna de las
tres significa trabajo sin entregar**: el chequeo comprueba antes que la rama
no tenga commits fuera de `main`, y las tres pasan esa comprobación. Las dos
salidas siguen siendo las mismas dos de arriba, y las dos están fuera del
alcance de la sesión.

**Saldo al cierre de S10 (cluster C07): cinco.** El intento se repitió sobre
las cinco y ninguna se borró; esta vez el fallo no llegó rotulado como
`HTTP 403` sino como `send-pack: unexpected disconnect while reading sideband
packet` seguido de `Everything up-to-date`, que es la misma negativa del
remoto contada de otra manera —la referencia sigue ahí después del intento—.

| Rama | Sesión | Fusionada en `main` |
|---|---|---|
| `claude/cluster-c13-rasante-geometria-2p5fqc` | S7 | sí |
| `claude/cluster-c03-lrfd-factors-23mrzf` | S8 | sí |
| `claude/cluster-c04-sismica-ay9szt` | S9 | sí |
| `claude/cluster-c07-recubrimiento-nadl34` | S10 | sí |
| `claude/s10-cluster-c07-resume-p19vmh` | S10 | sí |

La quinta es la rama que el propio arranque de la sesión creó para retomar
S10; no llevó trabajo propio —se dejó apuntando a `main`— y aun así cuenta
para el chequeo 3, porque el chequeo mira referencias del remoto y no de dónde
salió cada una.

De modo que `verificar_sesion.py` dará `[FALLO] … ya fusionada, debería estar
borrada` **cinco** veces, y **ninguna de las cinco significa trabajo sin
entregar**: el chequeo comprueba antes que la rama no tenga commits fuera de
`main`, y las cinco pasan esa comprobación. Las dos salidas siguen siendo las
mismas dos de arriba y las dos están fuera del alcance de la sesión.

**Saldo al cierre de S11 (diseño del registro normativo): una.** Las cinco
anteriores **ya no están en el remoto** —`git branch -r` lista hoy solo `main` y
la rama de esta sesión—, de modo que alguien con permisos las borró entre S10 y
S11. Eso no cambia el diagnóstico: el intento desde la sesión volvió a fallar,
y esta vez con las dos formas de la negativa **a la vez**, `HTTP 403` y el
`send-pack: unexpected disconnect` seguido de `Everything up-to-date`.

| Rama | Sesión | Fusionada en `main` |
|---|---|---|
| `claude/diseno-registro-normativo-607nkm` | S11 | sí (`66bf252`) |

Cuarta reincidencia, y con ella lo que se puede afirmar cambia de tono: **el
borrado de ramas no es una tarea de la sesión, es una tarea del propietario del
repositorio.** El token de la sesión puede crear referencias y no puede
borrarlas, y ninguna de las cuatro veces que se ha intentado ha funcionado. Lo
que sí está en manos de la sesión —fusionar a `main` y dejarlo verificado— se
hizo antes de intentar el borrado, y es lo que decide si hay trabajo entregado.

`verificar_sesion.py` dará `[FALLO] … ya fusionada, debería estar borrada`
**una** vez, y **no significa trabajo sin entregar**: el chequeo comprueba
antes que la rama no tenga commits fuera de `main`, y esta lo pasa.

**Saldo al cierre de S12 (registro normativo, clusters C11/C12/C02): dos.**
Quinta reincidencia, y la primera en la que la rama anterior **sigue estando**:
la de S11 no la borró nadie entre sesiones, de modo que a la de S12 se le suma.
Los dos intentos —`git push origin --delete` sobre cada una— devolvieron otra
vez las dos formas de la negativa a la vez, `HTTP 403` seguido de
`send-pack: unexpected disconnect while reading sideband packet` y de un
`Everything up-to-date` que delata que el borrado ni siquiera llegó a
proponerse.

| Rama | Sesión | Fusionada en `main` |
|---|---|---|
| `claude/diseno-registro-normativo-607nkm` | S11 | sí (`66bf252`) |
| `claude/registro-normativo-pymupdf-0fo35b` | S12 | sí (`66fde80`) |

Las dos pasan la comprobación de «sin commits fuera de `main`», que es la que
distingue una rama olvidada de trabajo sin entregar. `verificar_sesion.py`
dará el `[FALLO]` **dos** veces y el resultado global será `FALLA` por eso y
solo por eso: los cuatro chequeos que dependen de la sesión —suite, conteos,
árbol limpio y tracker— están en `[OK]`. **Las borra el propietario desde la
web**; no hay nada más que la sesión pueda hacer, y ya van cinco veces
comprobado.

**Saldo al cierre de S14 (vacíos y cableado, clusters C01/C04/C06/C08/C11):
cuatro.** Sexta reincidencia, y la primera en la que se acumulan **cuatro**
ramas a la vez: las dos que S12 dejó anotadas siguen ahí, más la de S13 —que
tampoco se borró entre sesiones— y la de S14. Se intentaron las cuatro, una a
una, con `git push origin --delete` y después con el refspec explícito
(`git push origin :refs/heads/<rama>`), y las dos formas devolvieron lo mismo
de siempre: `HTTP 403` y `send-pack: unexpected disconnect while reading
sideband packet`, seguidos de un `Everything up-to-date` que delata que el
borrado ni siquiera llegó a proponerse. Se comprobó además, esta vez, que el
proxy de la sesión está sano y sin fallos de relay
(`$HTTPS_PROXY/__agentproxy/status`, `recentRelayFailures: []`): la negativa es
del permiso del token sobre el remoto, no del transporte.

| Rama | Sesión | Fusionada en `main` |
|---|---|---|
| `claude/diseno-registro-normativo-607nkm` | S11 | sí (`66bf252`) |
| `claude/registro-normativo-pymupdf-0fo35b` | S12 | sí (`66fde80`) |
| `claude/conflicto-8-clasificacion-sitio-r5dpf1` | S13 | sí (`6f7e780`) |
| `claude/clusters-vacios-criterios-wku6xo` | S14 | sí (`5b379ec`) |

Las cuatro pasan la comprobación de «sin commits fuera de `main`».
`verificar_sesion.py` dará el `[FALLO]` **cuatro** veces y el resultado global
será `FALLA` por eso y solo por eso: los cuatro chequeos que dependen de la
sesión —suite, conteos, árbol limpio y tracker— están en `[OK]`, y el tracker
pasa además la comprobación nueva de que todo hallazgo cerrado cita un commit
**presente en `main`**. **Las borra el propietario desde la web.** Van seis
veces comprobado, y la acumulación es el argumento que faltaba: mientras nadie
las borre entre sesiones, el `[FALLO]` crece una línea por sesión y el chequeo
pierde valor de señal.

**Saldo al cierre de S15 (modo de resolución de las variables): una, y las
cuatro anteriores ya no están.** Buena noticia primero: al empezar S15,
`verificar_sesion.py` daba `[OK] solo existe origin/main` — el propietario
borró desde la web las cuatro ramas que S14 dejó anotadas, que es exactamente
lo que aquella nota pedía. La única abierta es la de esta sesión,
`claude/variable-entrada-modo-resolucion-7ezfh3`, fusionada en `main`
(`5a200ff`) y sin un solo commit fuera de ella. Se intentó borrarla con las dos
formas de siempre —`git push origin --delete` y el refspec explícito
`git push origin :refs/heads/<rama>`— y las dos devolvieron el mismo `HTTP 403`
seguido de `Everything up-to-date`, con el proxy de la sesión sano
(`recentRelayFailures: []`). Séptima comprobación, y el diagnóstico no ha
cambiado: **el permiso del token no alcanza para borrar ramas en el remoto, y
la borra el propietario desde la web.** El `[FALLO]` de esta sesión es ese y
solo ese; los cuatro chequeos que dependen de la sesión —suite, conteos, árbol
limpio y tracker— están en `[OK]`.

---

## 7. T-11 de la cadena T: la validación integral sobre la línea base (2026-11-13)

Este documento es la FOTO de la línea base de S1 y el estado de la suite vive en
`CLAUDE.md` («Cierre de tarea»), que lleva la cadena de totales. Se deja aquí lo que la
validación integral de T-11 —el último prompt de la cadena que toca la línea base antes
de T-12— dice de ella, porque es el primer prompt que la recorre ENTERA de punta a punta:

- **El fixture de siempre (`tests/ejemplo_puntos.csv`) sigue cargando y ningún número de
  cálculo se movió.** T-11 no cambia cálculo. La línea base de la Familia C
  (`tests/linea_base_familia_c/`) se regeneró y se midió contra `14f6138` con el
  comparador de E-B: `informe_expediente.json` e `informe_rama_error.json` IGUALES;
  `informe_perfil_ancho.json` e `informe_familia_c.json`, 4 diferencias y 0 no
  comparables, todas de diagnóstico o de formato (el «no factible por rasante» de B-01 de
  la corrección de T11-03 y `HW_salida_m` de A-02 a `null` por decisión del dueño); el
  tipo de cabezal del cuadro resumen sale del punto. **Diámetros, secciones, materiales y
  HW que gobierna movidos: ninguno.** El detalle, archivo por archivo, en el README de esa
  carpeta.
- **Con un juego de DATOS DE PRUEBA completo las tres familias llegan a la Fase 11 con
  diseño** (A-01, A-02 y B-01 concreto Ø 0.90; C-01 marco 1.20 × 0.90): `docs/validacion_integral.md`,
  generado. **Sin el juego, ningún punto pasa de la Fase 2** (la luz del cruce no es
  columna del CSV), y la lista exacta de lo que el proyecto debe entregar está en la §7 de
  `docs/contrato_entradas.md`.
- **El par de la suite al cierre de T-11**, medido en «PyMuPDF sí · ventana Tk no» con el
  repositorio de normas enlazado: **6446 passed, 23 skipped → 6469 `collected`** (sin
  `NORMAS_DIR`, 6423 y 46). Lo invariante sigue siendo `collected = passed + skipped`.

---

## 8. T-12 de la cadena T: la línea base en la versión de sustentación (2026-11-13)

T-12, el último prompt de la cadena, no cambia cálculo. Lo que dice de la línea base:

- **La línea base de la Familia C se regeneró y se midió contra `f77c5d4` con el comparador
  de E-B**: los cuatro JSON IGUALES; los dos CSV de resumen y cuatro de los cinco
  `cli_*.txt`, idénticos byte a byte. Las cuatro memorias completas cambian sólo por el
  rótulo «FIXTURE DE PRUEBA, NO ES UN RESULTADO DEL PROYECTO» que les pone el generador
  (`regenerar.sh`, con `tests/apoyo/rotulo_fixture.py`, después de la CLI: el programa no
  lo conoce) y, en `memoria_perfil_ancha.html`, por la cadena de T11-09 de A-02 («salida
  no se forma: el perfil no alcanza la entrada»); `cli_expediente.txt` gana la línea de la
  memoria resumida, y `memoria_resumida_expediente.html` es nuevo. **Diámetros, secciones,
  materiales y HW movidos: ninguno.** El detalle, archivo por archivo, en el README de esa
  carpeta.
- **El estado de la suite ya no vive en `CLAUDE.md`**: la sección «Cierre de tarea» se
  movió entera, con la tabla de las configuraciones y la cadena de totales, a
  `proceso/bitacora_conteos_y_entorno.md`, que es material de proceso y no viaja en una
  exportación del entregable. Desde T-12 hay dos suites: la del entregable (`python -m
  pytest`, sólo `tests/`) y la de proceso (`python -m pytest proceso/tests`).
- **El par al cierre de T-12**, en «PyMuPDF sí · ventana Tk no»: la suite del entregable
  con el repositorio de normas enlazado, **6402 passed, 23 skipped → 6425 `collected`**
  (sin `NORMAS_DIR`, 6250 y 175: sin él se salta todo lo que abre un PDF); sobre una
  exportación (`git archive HEAD`) con `NORMAS_DIR`, 6398 y 27, sin ningún fallo;
  la de proceso pasa entera (145 de 145). Lo invariante sigue siendo `collected = passed + skipped`.

---

## 9. UI-5 de la cadena de interfaz: la línea base tras cuatro decisiones del dueño (2026-11-15)

UI-5 no cambia cálculo. Dos de sus decisiones tocan la salida, y la línea base de la Familia
C se regeneró con su script (`sh tests/linea_base_familia_c/regenerar.sh`) declarando la
causa:

- **Lo que la resumida dice de su completa y de su encabezado** (ficha UI2-01 b): en
  `memoria_resumida_expediente.html`, el párrafo de la remisión, que decía que el
  encabezado de trazabilidad «es el mismo en las dos» y hoy dice sólo lo que el encabezado
  prueba (`M11.REMISION_COMO_COMPROBARLO`), y el párrafo del bloque «0. Encabezado de
  trazabilidad» de la plantilla, que prometía lo mismo desde T-12 y contaba la huella de la
  hoja de ruta, que se lee al exportar. La revisión de UI-5 y su verificación (fichas UI5-02
  y UI5-03) corrigieron esos textos; cada regeneración movió esos textos y nada más. Sin
  números.
- **La huella de `criterios_adoptados.py`** (ficha UI3-03: su guardia exige la forma de las
  claves): `criterios_sha1` en los cuatro JSON y la fila del encabezado en las cuatro
  memorias de la CLI. Ningún valor, ficha ni nivel de criterio cambió.

Ocho archivos (13 líneas nuevas por 12), y nada más: los cinco `cli_*.txt`, los dos CSV de resumen y la
memoria del cajón, idénticos byte a byte. **Diámetros, secciones, materiales y HW movidos:
ninguno.** El detalle, en el README de la carpeta; el par de la suite, en
`proceso/bitacora_conteos_y_entorno.md`.

---

## 10. VE-1: la progresión declarada se recorre tal cual, y la línea base no mueve ningún número (2026-11-15)

VE-1 cambia UNA línea de cálculo: el escalón siguiente de la progresión de diámetros
(`M2.siguiente_diametro`), que se redondeaba a dos decimales y con la serie de 6 in de la
ficha de `diametros_normalizados` (0.9144 + 0.1524) fabricaba 1.07 m (ficha VE1-01, D1).
Hoy lo calcula `M2._escalon_de_la_serie` en aritmética decimal sobre los dos números
declarados. Con la progresión de archivo (0.90 / 0.15) da los mismos trece escalones, y
por eso la línea base **no se movió**: regenerada con su script sobre el árbol de VE-1, el
`git diff` de los dieciséis archivos sale **vacío**. Quitar el redondeo a secas no habría
pasado esta prueba: `0.9 + 6 · 0.15` es 1.7999999999999998 en binario, y con ese mutante
caen los dos tests de `tests/test_linea_base.py` que comparan contra lo comprometido.
**Diámetros, secciones, materiales y HW movidos: ninguno.**

Las correcciones de la revisión independiente de VE-1 (ficha VE1-01: H1, H2 y H3)
movieron **una cosa, y no es un número**: la huella de `criterios_adoptados.py`, porque
H2 le añadió a su guardia la de los campos de la progresión
(`_verificar_campos_de_la_progresion`): `criterios_sha1` en los cuatro JSON y la fila del
encabezado en las cuatro memorias de la CLI, ocho líneas en ocho archivos. El rótulo
nuevo de la sección (H1, `modelos.texto_de_dimension`) escribe los mismos «Ø 0.90 m» y
«marco 1.20 × 0.90 m» de siempre: ningún otro byte cambió.

---

## 11. VE-2, bloque 1: la velocidad de erosión resuelve su propio tirante, y la línea base SÍ se mueve (2026-11-17)

VE-2 corrige un defecto de MÉTODO aprobado por el dueño (ficha VE2-B; decisión (b) de
VE1-02): la velocidad alta de la regla de doble n era la de n mínimo sobre el tirante de
n máximo, V(n_máx)·n_máx/n_mín, con V·A = 1.3·Q en el concreto, y hoy es la del tirante
normal resuelto con n mínimo, `V_erosion = Q / A(y_n con n_mín)` (`M3.resolver_manning`;
HDS-5 núm. 3.3.2, pág. impresa 3.24; HEC-14 núm. 3.2.2, pág. impresa 3-7). Es el ÚNICO
bloque de VE-2 que mueve números. Regenerada con `sh tests/linea_base_familia_c/regenerar.sh`
sobre `72a8d01`, diez de los dieciséis archivos cambian (108 líneas por 108); los
`informe_expediente.json`, `informe_rama_error.json`, `cli_expediente.txt`,
`cli_perfil.txt`, `cli_rama_error.txt` y `resumen_expediente.csv` quedan idénticos.

**Lo que se movió, punto por punto** (corrida ancha de perfil y corrida de la Familia C
dimensionada; las dos dan los mismos números en A-01 y A-02):

| Punto | Magnitud | Antes | Ahora |
|---|---|---|---|
| A-01 (Ø 0.90, control de entrada) | `V_erosion` = `V_salida` = V3 (m/s) | 3.206 | 3.040 |
| A-01 | d50 de Laushey (m) | 0.338 | 0.304 |
| A-01 | espesor adoptado 1.75·d50 (m) | 0.592 | 0.532 |
| A-01 | lo que rige con la envolvente | 0.770 m · 5.40 m, clase 4 | sin cambio |
| A-01 | Froude de HEC-14 Fr_e (ye, m) | 1.567 (0.427) | 1.466 (0.438) |
| A-02 (Ø 0.90, control de entrada) | `V_erosion` = `V_salida` = V3 (m/s) | 2.883 | 2.681 |
| A-02 | d50 de Laushey (m) | 0.274 | 0.237 |
| A-02 | clase de la piedra (Tabla 10.1) | 4 (0.35 m) | 3 (0.25 m) |
| A-02 | espesor y longitud que rigen (m) | 0.770 · 5.40 | 0.600 · 5.00 |
| A-02 | espesor adoptado (m) | 0.479 | 0.414 |
| A-02 | Froude Fr_e (ye, m) | 1.714 (0.289) | 1.565 (0.299) |
| C-01 (marco 1.20 × 0.90, control de salida) | `V_erosion` = V3 (m/s) | 2.084 | 1.955 |
| C-01 | aviso de la banda de régimen: V y d50 con n mínimo | 2.084 m/s · 0.143 m | 1.955 m/s · 0.126 m |
| Punto de cajón (driver) | `V_erosion` (m/s) | 2.694463 | 2.496046 |

C-01 conserva su `V_salida` (1.908 m/s, la crítica: control de salida, HDS-5 3.1.6) y su
d50. En la corrida de expediente ningún punto dimensiona y sólo cambian las trazas de
los escalones intentados en la memoria (las velocidades y los márgenes de V3 de los
escalones que no cierran). Las memorias cambian además en el texto del paso 4.1 (los
dos tirantes, V = Q/A de cada rama, las dos citas), del 4.3b (`y_n_min` bajo control de
entrada) y del fundamento `F4.MANNING` en el anexo.

**Diámetros, secciones, materiales y HW movidos: ninguno, y ningún diámetro sube.** Los
dos tubos ya estaban en Ø 0.90 m, el mínimo de la progresión, y el marco no se mueve.
Bajar la velocidad de erosión sólo puede aliviar V3: un diámetro puede bajar, no subir
(el caso UPAO ALC46 de la validación externa pasa de Ø 1.35 a Ø 0.90 m;
`tests/test_ve2_velocidad_erosion.py`).

**Fuera de la línea base, lo que también se movió y se declaró en su test** (cada uno
cambiado con la causa escrita junto al assert): los dorados de CP-2 y CP-2R ganan la
rama de n mínimo con su tirante (`V_erosion_esperado` 2.8315 y 3.6620 m/s;
`V_con_n_min_esperado` queda como el contraste de la fórmula sobre una geometría dada);
el caso subcrítico del dictamen (`test_ext3_regimen_barril`) pasa de 1.184 a 1.107 m/s;
A-01 a mano (`test_cierre_perfil`) de 3.206 a 3.040 m/s con y_n = 0.523 m; los números
de A-01 y A-02 en `test_t8_correcciones` y `test_t8_proteccion`; el caso G2 de
`test_t4_materiales_durabilidad` sube su pendiente de 0.012 a 0.015 para que el concreto
siga incumpliendo V3 en toda su progresión (con 0.012 el Ø 1.65 m ya cumple, 5.95 m/s) y
llega a los mismos escalones del TMC; el techo de la memoria por punto
(`test_ext8_rendimiento_gui.KB_POR_PUNTO_MAX`) sube de 107.5 a 109.0 KB, medidos 108.50
contra 107.04; y la variante `caudal_calculado` del juego de T-11 vacía el caudal del
evento extremo, que era el de su Q declarado (ficha VE2-B). Los documentos generados
(`indice_formulas.md`, `validacion_integral.md`, `validacion_hy8.md`, `manifiesto_citas.md`,
`manifiesto_registro_normativo.md` y `trazabilidad.csv`, con la cita nueva de HEC-14) se
regeneraron con sus comandos; `validacion_hds5.md` y `validacion_sensibilidad.md` salen
idénticos.

## 12. VE-2 (a) y (g): la columna del n del concreto y los diámetros designados, criterios [A]; ningún número se mueve (2026-11-17)

**VE-2 (a)** (`validacion(VE-2.2)`, ficha VE2-A): la columna del n del tubo de concreto
pasa a ser el criterio [A] `columna_n_manning_concreto`, con la doble n de siempre como
valor de archivo. Se mueven **ocho archivos y ningún número de cálculo**: la huella de
`criterios_adoptados.py` y el recuento «141 → 142 criterios declarados» del encabezado;
la entrada del criterio en los criterios usados de los cuatro JSON; su ficha y su fila
en las memorias, y en la memoria ancha el paso nuevo `F4.N_CONCRETO` (A-01 y su remisión)
con el fundamento y las dos citas del HDS-5 en el anexo. Medido con un diff por
fragmentos de las memorias contra `HEAD`: sólo reemplazos de recuento y huella, y
inserciones. **Diámetros, secciones, materiales, n y HW movidos: ninguno.**

**VE-2 (g)** (`validacion(VE-2.4)`, ficha VE2-G): los escalones tienen que ser diámetros
designados por la norma de producto de cada material, y el criterio [A]
`diametro_de_diseno_concreto` (archivo: `designado`) decide si el concreto admite además
el diámetro inglés convertido. La progresión de archivo es toda designada: se mueven
**los mismos ocho archivos y ningún número de cálculo** —la huella de
`criterios_adoptados.py`, el recuento «142 → 143 criterios declarados», la entrada del
criterio en los cuatro JSON (también en la rama de error, cuyo bloqueo y motivo no
cambian: un escalón no positivo lo sigue rechazando la hidráulica) y su ficha y su fila
en las memorias—. **Diámetros, secciones, materiales y HW movidos: ninguno.**

## 13. VE-2 (c1): V7 se justifica con la norma y no con el sitio; ningún número se mueve (2026-11-17)

VE-2.2 (c1) no cambia cálculo: reemplaza la justificación de la flotación (V7) por el NF
somero del Bajo Piura por la del Manual de Puentes, núm. 2.4.3.8.1 (el nivel de agua de
diseño lo fija el Propietario; ficha VE2-C). Regenerada con su script, la línea base cambia
**tres memorias HTML y ningún número**: en `memoria_perfil.html`, `memoria_perfil_ancha.html`
y `memoria_expediente.html`, el `por_que` de F5.V7 (anexo de fundamentos) y, en la ancha,
el paso de V7 de los puntos que lo evalúan, que cita además la frase del 2.4.3.8.1 (y con
ella cambian los anclajes `paso-…`, que son huellas del contenido). Los JSON, los CSV de
resumen, los cinco `cli_*.txt` y la memoria del cajón, idénticos byte a byte; los valores
de V7 (estabilizante y desestabilizante) que la memoria imprime, los mismos.
**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 14. VE-2 (c2): el nivel de agua de diseño de V7, criterio [A]; ningún número de cálculo se mueve (2026-11-17)

VE-2.4 (c2) añade `nivel_agua_diseno_v7` [A] (valor de archivo `en_la_clave`, lo que V7
calculaba) y `margen_estacional_nf_v7_m` [A] sin valor (ficha VE2-C). Regenerada con su
script, la línea base cambia **ocho archivos y ningún número de cálculo** (las hojas
numéricas de los cuatro JSON, fuera de la lista de criterios usados, idénticas): la huella
de `criterios_adoptados.py` (cuatro JSON y las memorias); el criterio nuevo en los criterios
usados de las corridas que evalúan V7 y el margen en la lista de los que siguen sin valor;
en las memorias, la elección del nivel en el paso de V7 (fundamento F5.V7_NIVEL), la fila
de los dos criterios y el recuento del encabezado, **«141 criterios declarados, 20 todavía
sin valor» → «143 …, 21 …»** medido en su rama sobre `72a8d01`; integrado detrás de (a) y (g), «143 … » → «145 …». Los cinco `cli_*.txt`, los dos CSV de resumen y la memoria
del cajón, idénticos. **Diámetros, secciones, materiales y HW movidos: ninguno.**

## 15. VE-2 (e), (f) y (d), la parte de hidrología: sólo la huella de `criterios_adoptados.py` (2026-11-17)

La línea base no ejercita la Fase 1-bis (sus corridas traen `Q_m3s` lleno), de modo que
el aviso de consistencia de la serie (e), el método racional modificado (f) y el factor de
intervalo fijo (d) no la tocan. Lo único que se movió es el archivo de criterios: en (f)
cambió el texto de `verificacion_pendiente` de `coeficiente_uniformidad_temez` (que ya no
es cierto que el método completo no esté implementado), y en (d) entró el criterio
`factor_intervalo_fijo_p24`. Resultado: `criterios_sha1` en los cuatro JSON, y en las
cuatro memorias de la CLI la fila de la huella y la del recuento («142 criterios
declarados» por 141 en su rama; integrado detrás de (a), (g) y (c), 145 → 146), regenerada con `sh tests/linea_base_familia_c/regenerar.sh`.

**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 16. VE-2 integrado (2026-11-17): regenerada sobre el conjunto; sólo (b) mueve números

Las cuatro partes de VE-2 se integraron en este orden —(b), (a) y (g), (c), (e) (f) y
(d)— y la línea base se **regeneró sobre el conjunto** con `sh
tests/linea_base_familia_c/regenerar.sh` tras cada una. Contra la del bloque 1 (§11), el
conjunto sólo añade lo que §12 a §15 describen: la huella de `criterios_adoptados.py`, el
recuento del encabezado («146 criterios declarados, 21 todavía sin valor»), los cuatro
criterios nuevos que la corrida usa en la lista de criterios usados de los JSON
(`columna_n_manning_concreto`, `diametro_de_diseno_concreto`, `nivel_agua_diseno_v7`;
`factor_intervalo_fijo_p24` no, porque la línea base trae `Q_m3s` lleno), el margen
estacional entre los que siguen sin valor, y los textos de V7 y de la columna del n. **Los
números de cálculo son los de §11, y ningún diámetro, sección, material ni HW se movió
respecto de `72a8d01` salvo lo que §11 lista** (A-01, A-02, C-01 y el cajón, por (b); medido hoja por hoja en los cuatro JSON, con un
único número que §11 no escribía: el ancho final de la clase de A-02, 6.30 → 5.70 m, que
acompaña al paso de la clase 4 a la 3).

## 17. Correcciones de la revisión independiente de VE-2 y de su verificación (2026-11-17): la huella de `criterios_adoptados.py` y la etiqueta del peso saturado

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh` (con el Python del proyecto
primero en el `PATH`: el `python3` del sistema puede no traer scipy). De las seis
correcciones (ficha VE2-03), sólo M3 y M4 tocan `criterios_adoptados.py`: el nivel de
`peso_especifico_saturado_relleno_kn_m3` (expediente → perfil) y el campo `no_negativo` de
`margen_estacional_nf_v7_m`. Resultado: `criterios_sha1` en los cuatro JSON y la fila de la
huella en las cuatro memorias, y nada más. A1 (el dato que falta en la Fase 5) no mueve la
línea base: ninguna de sus corridas tiene un punto al que la Fase 5 le detenga por un dato
que falta un escalón que cumple; sí mueve `docs/validacion_integral.md` (variante
`caudal_calculado`, B-01) y el resumen de la tercera corrida del índice de fórmulas.

Y de la verificación de esas correcciones (ficha VE2-05), regenerada otra vez sobre el
conjunto: N2 reetiqueta `peso_especifico_saturado_relleno_kn_m3` de [A] a [S], y eso se ve
en la etiqueta de su fila en las tablas de criterios de las memorias de perfil (las dos
veces que la lista aparece) y de expediente, además de la huella. N1 (A1 acotada al dato
del punto) no mueve la línea base, por la misma razón que A1.

**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 18. VE-3.1 (ficha VE2-04): bajo control de salida V3 juzga la mayor de V_erosion y V_salida; ningún número se mueve (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh` (Python del proyecto primero en
el `PATH`). Bajo control de SALIDA, V3 compara contra el techo de la Tabla Nº 10 la mayor de
la velocidad del tirante normal de n mínimo (`V_erosion`) y la de la sección de salida
(`V_salida`, HDS-5 núm. 3.1.6). En las corridas de la línea base, todo escalón bajo control
de salida tiene la salida MÁS LENTA que el tirante normal, de modo que V3 sigue comparando
`V_erosion`: **ningún número de los cuatro JSON cambia** (ni `valor_obtenido` de V3, ni
veredicto, ni diámetro). Lo único que se mueve es la procedencia de esa velocidad en las
memorias, que ahora dice con qué se comparó: «Bajo control de SALIDA V3 juzga la MAYOR de
esta y la de la sección de salida […], que aquí es menor (V_salida = x m/s)». Escalones
afectados: tres en `memoria_expediente.html` (V_salida 0.149, 1.908 y 2.412 m/s), tres en
`memoria_perfil.html` (0.066, 0.357 y 0.924 m/s) y dos en `memoria_perfil_ancha.html`
(0.084 y 1.908 m/s).

Fuera de la línea base, en la corrida de referencia `expediente_cabezal` del índice de
fórmulas un escalón de TMC bajo control de salida pasa a comparar `V_salida` = 1.739 m/s
contra su techo de 4.572 m/s: cumple igual que antes.

**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 19. VE-3.2 (ficha VE2-05): los parámetros del suelo de fundación son [S]; ningún número se mueve (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh`. `c_phi_fundacion` y
`capacidad_portante_adm` pasan de [A] a [S] pendiente de ensayo, con su `trazabilidad`, y la
capacidad portante lleva `positivo`. Resultado: `criterios_sha1` en los cuatro JSON y en las
cuatro memorias, y la etiqueta de esas dos filas ([A] → [S]) en las tablas de criterios de
`memoria_expediente.html`, `memoria_perfil.html` y `memoria_perfil_ancha.html`. Nada más.

**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 20. VE-3.5: el cabezal se dimensiona por estabilidad; la línea base no ejercita la estabilidad y no mueve ningún número (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh` (con el Python del proyecto
primero en el `PATH`). VE-3.5 añade el criterio `dimensionamiento_zapata_cabezal` [A] de
expediente, SIN valor de archivo (el paso y el tope del ancho de la zapata), y el
dimensionamiento de la zapata por intentos detrás de la estabilidad de la geometría de la
regla (`M9.dimensionar_zapata_por_estabilidad`). Ninguna corrida de la línea base llega a
evaluar la estabilidad de un cabezal (la de expediente se detiene antes en los criterios
del EMS y del relleno que no declara), de modo que el dimensionamiento no corre en ella y
el criterio nuevo no se lee. Lo que se mueve: `criterios_sha1` en los cuatro JSON, la
clave nueva en la lista de criterios sin valor de los cuatro JSON, y en las memorias la
fila de la huella, el recuento («147 criterios declarados, 22 todavía sin valor») y la
fila del criterio nuevo en la lista de pendientes (nota de perfil y Tablero 1).

**Diámetros, secciones, materiales, HW y geometrías de cabezal movidos: ninguno.** Donde
el dimensionamiento sí corre (la validación integral, que declara el criterio con datos de
PRUEBA, y la corrida de referencia `expediente_cabezal` del índice de fórmulas), las
zapatas crecen y las filas E1 a E3 cumplen: lo dicen `docs/validacion_integral.md`, la
ficha nueva y `tests/test_ve3_dimensionamiento_cabezal.py`.

## 21. VE-3.6 (Familia C): VC3, la rasante hidráulica del canal; ningún número se mueve (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh` (con el Python del proyecto
primero en el `PATH`). VC3 compara las pérdidas de la obra con el desnivel F que el perfil
del canal provee en el cruce (USBR, *Design of Small Canal Structures*, 1978, núm. 2-6), y
F es un dato del proyecto del canal (`desnivel_perfil_canal_m`, --datos-externos) que las
entradas de la línea base no traen. Por eso VC3 no tiene fila en ninguna corrida de la
línea base, y lo que cambia es: en C-01 de la corrida de la Familia C (`cli_familia_c.txt`
e `informe_familia_c.json`) el **aviso** de que VC3 no se evaluó, y en las tres memorias
completas el bloque de umbrales de la Fase 5, que suma la ficha de VC3 (y una frase en la
de VC1: «Esa otra mitad la cierra VC3 desde VE-3.6»). La huella de
`criterios_adoptados.py` no cambia (VE-3.6 no toca criterios).

**Diámetros, secciones, materiales y HW movidos: ninguno.** Con F declarado, VC3 decide
como cualquier fila de la tabla y puede agrandar la sección: lo fija
`tests/test_ve3_familia_c.py` (C-01 con el fondo en el canal y F = 0.30 m pasa de
1.20 × 0.90 a 1.50 × 1.20 m), fuera de la línea base y fuera del juego de T-11, cuyas
variantes no mueven secciones.

## 22. VE-3.7 (Familia C): el remanso del canal por paso directo; sólo la huella de `criterios_adoptados.py` (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh`. El perfil por paso directo
(`M3.perfil_remanso_trapecial`) sólo corre en la Familia C con la sección medida del canal
(`seccion_receptor_medida`), que las entradas de la línea base no traen: el remanso de C-01
sigue «no se evaluó». Lo único que cambia es la huella de `criterios_adoptados.py` (el
criterio opcional nuevo `fraccion_fin_remanso_canal`) en los cuatro JSON y en las memorias.
**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 23. VE-3.9: el paso y el tope de la zapata como valor de archivo, y el peralte dimensionado por su armado; sólo la huella y el recuento (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh` (con el Python del proyecto
primero en el `PATH`). `dimensionamiento_zapata_cabezal` pasa de vacío a valor de archivo
({paso 0.10 m, tope 1.5·H_c}, decisión del dueño) y el peralte de la zapata se dimensiona
por su armado (`M9.dimensionar_peralte_por_armado`), pero ninguna corrida de la línea base
llega a la estabilidad ni al armado del cabezal: lo único que cambia es la huella de
`criterios_adoptados.py` en los cuatro JSON y, en las cuatro memorias, la fila de la huella
y la del recuento («148 criterios declarados, 21 todavía sin valor»; la línea base de
partida decía «147», porque no se había regenerado tras integrar la Familia C, que sumó un
criterio). **Diámetros, secciones, materiales y HW movidos: ninguno.** Donde sí se mueve el
cabezal es en `docs/validacion_integral.md`: en la corrida titular el peralte crece en los
ocho cabezales y en el juego en dos, y el armado de la zapata deja de tener filas sin
cumplir.

Medido sobre los datos de PRUEBA de la validación integral (no del proyecto):

| Corrida | Cabezales con peralte dimensionado | Peraltes adoptados | Filas de la zapata sin cumplir | Filas de estabilidad LRFD sin cumplir |
|---|---|---|---|---|
| Titular (decisiones de archivo: trasdós sin drenaje) | 8 de 8 | 1.004 a 1.504 m (anchos 3.38 a 5.28 m) | 0 | 0 |
| Juego (trasdós drenado) | 2 de 8 (salidas de A-01 y A-02) | 0.804 y 0.704 m | 0 | 0 |

Lo que sigue sin cumplir es de la PANTALLA y del ALERO, que este dimensionamiento no toca:
A1 (flexión) de la pantalla y del alero de la salida de A-01 en las dos corridas, y de A-02
y C-01 en el juego; A2 (cortante) como indicador en los mismos elementos. Las filas ASD de
estabilidad que no salen «cumple» son indicadores, no deciden. Los peraltes de la titular
son grandes porque entre 16 in y el peralte cuyo vuelo queda bajo 3·d_v el cortante sale
de AASHTO 5.7.3.4.1 y el programa no implementa el procedimiento general (5.7.3.4.2): esos
peraltes no se pueden verificar y el dimensionamiento pasa al primero verificable, que es
conservador.

En el anexo de sensibilidad (`docs/validacion_sensibilidad.md`) dos claves pasan de «mueve
veredictos» a «leído, sin efecto medible» (`clase_exposicion_fisuracion_cabezal` y
`metodo_longitud_conducto`): cambiaban un veredicto del armado de la zapata que hoy el
peralte absorbe. Y el barrido de §3.1 vuelve a medir la zapata de la REGLA: la base
`juego_cabezal_de_la_regla` declaraba el criterio sin valor y el barrido no lo aplicaba
(`tests/apoyo/sensibilidad.py::medir` lo aplica desde VE-3.9).

## 24. VE-3.10 (Familia C): VC3 sin el desnivel del perfil del canal DETIENE el punto (2026-11-17)

Decisión del dueño (ficha VE3-06): en un paso de canal sin `desnivel_perfil_canal_m` el
punto ya no sale con el aviso de 7.B («VC3 … no se evaluó», retirado): se detiene en el
bucle de MD con `DatoFaltanteError` de esa clave, en la posición de VC1 y también a
`--alcance perfil`. Para que la corrida dedicada de la Familia C siga dimensionando C-01,
`entradas_ampliadas.json` declara **F = 1.20 m como DATO DE PRUEBA rotulado** (con la entrada
en el terreno del cruce y el TW de 0.30 m, el marco de 1.20 × 0.90 m pierde 1.023 m; un F
de canal real, 0.30-0.40 m, lo dejaría sin sección). Regenerada con
`sh tests/linea_base_familia_c/regenerar.sh`, punto por punto:

- **C-01, corrida de la Familia C (`informe_familia_c.json`, `cli_familia_c.txt`):** la
  fila VC3 se evalúa y CUMPLE (pérdida 1.0230 m frente a F = 1.20 m, margen 0.177 m), y el
  aviso de 7.B desaparece. **La sección (marco 1.20 × 0.90 m), el material y el HW no se
  mueven.**
- **C-01 en las otras tres corridas (perfil estrecha y ancha, expediente):** sin cambio:
  se detiene antes, en VC1, por la coronación del canal que esas corridas no traen; F no
  llega a pedirse.
- **A-01, A-02 y B-01:** sin cambio (la clave sólo la usa la Familia C).
- **Lo que la regeneración trae de la integración de VE-3.5 y VE-3.7, que el árbol de
  partida tenía sin regenerar:** la huella `criterios_sha1` en los cuatro JSON y en las
  memorias, el recuento «148 criterios declarados, 22 todavía sin valor», y
  `dimensionamiento_zapata_cabezal` entre los criterios sin valor.

**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 25. VE-3.11: hallazgos de los ensayos de diseño del conducto (H2, H3, H4, H6) (2026-11-17)

Regenerada con `sh tests/linea_base_familia_c/regenerar.sh` sobre `33bd7fc`. Lo que se
mueve, punto por punto, comparado hoja por hoja en los cuatro JSON:

- **H4, V7 suma el peso propio del concreto** (γ_c · (A_exterior − A_interior), con
  `peso_especifico_concreto_kn_m3` = 23.56 kN/m³, que pasa a ser criterio usado de la
  corrida de perfil):
  - `informe_familia_c.json` y `informe_perfil_ancho.json`, A-01, V7: lado estabilizante
    15.988 → 22.650 kN/m; A-02: 16.830 → 23.491 kN/m (los dos ya cumplían).
  - `informe_familia_c.json`, C-01 (marco), V7: 23.256 → 44.460 kN/m (ya cumplía).
  - B-01 (las dos corridas): los escalones de concreto Ø 1.20, 1.35 y 1.50 m dejan de
    incumplir V7 (siguen incumpliendo V2); en Ø 1.65 y 1.80 m V7 sigue sin cumplir, con el
    lado estabilizante 7.165 → 26.851 y 2.467 → 25.491 kN/m.
- **H6, el titular nombra la causa real**: B-01 (las dos corridas) pasa de «NO FACTIBLE POR
  RASANTE» a «NO FACTIBLE POR V2: no cumple en ningun escalon evaluado…» (V2 incumplida en
  todos los escalones de los dos candidatos que llegaron a la subrasante).
- **H2** (V1 con el resalto dentro del barril bajo control de entrada) y **H3** (el rótulo
  de V7 en el delta de 7.A): sin efecto en estas corridas.
- La huella `criterios_sha1` en los cuatro JSON y en las memorias, y la lista de criterios
  usados (se suma `peso_especifico_concreto_kn_m3`).

**Diámetros, secciones, materiales y HW movidos: ninguno.**
