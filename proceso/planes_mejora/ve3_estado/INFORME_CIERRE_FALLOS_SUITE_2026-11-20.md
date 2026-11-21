# Informe de fallos de la suite de cierre VE-7 y su resolución (2026-11-20)

Material de proceso (`proceso/`), no del entregable. Deja declarados todos los
fallos detectados al completar la corrida íntegra de la suite tras los arreglos
de cierre de VE-7 (`claude/optimistic-carson-ag7mwp`), su clasificación por
gravedad y complejidad, su causa raíz verificada y cómo se resolvió cada uno.

## 1. Línea base de diagnóstico

- **Rama y commit evaluado:** `claude/optimistic-carson-ag7mwp` en `e65b1c8`
  (idéntico en código, documentos del entregable y tests a `8472063`, que sólo
  editó `proceso/planes_mejora/ve3_estado/LEEME.md`).
- **Corrida completa en GitHub Actions:** workflow `Pruebas`, run
  `44824122722` (`ubuntu-24.04`, Python 3.12, `xvfb-run`, Tk y WeasyPrint, sin
  `NORMAS_DIR`), duración `2 h 28 min 12 s`.
- **Resultado antes de estas correcciones:** **`6 failed, 9001 passed, 174 skipped`**
  (sobre 9 181 tests del entregable). Ningún cálculo de `src/modulos/`, ningún
  test de ventana real, ni la exportación ni la línea base fallaron.

---

## 2. Fallos encontrados, clasificación y solución aplicada

### Fallo 1 — Gravedad: MEDIA · Complejidad: MEDIA
- **Test:** `tests/test_t11_sensibilidad.py::test_el_cabezal_de_la_regla_frente_a_sus_dos_A`
- **Síntoma:** El test exigía `set(estados[(p, "E3-LRFD.est.e")]) == {"no cumple"}`
  para los cuatro puntos (`A-01`, `A-02`, `B-01`, `C-01`), pero en **`C-01`**
  devolvía `{'cumple', 'no cumple'}`. Además, en `docs/validacion_sensibilidad.md`
  §3.1 había una contradicción interna: la tabla regenerada ya imprimía
  `pasa en C-01` para `'muros_tabla_11_5_7'` y para `'aplicar'`/`'omitir'`,
  mientras el párrafo inmediatamente inferior (generado por
  `tests/apoyo/sensibilidad.py`) seguía afirmando *«Ninguno de los dos hace
  pasar E3 estática a la ENTRADA»*.
- **Causa raíz verificada (comparando `cb15e32` pre-VE-7 contra `8472063`):**
  No es una regresión de cálculo. Desde `5f9a662` (`VE-7 fix-suite`, ficha
  `VE7B-11`), el juego declara `espesor_pared_cajon = 0.30 m` (en lugar de
  `0.20 m`) para cerrar el pórtico de `C-01`. Eso eleva 0.10 m la coronación
  del cabezal de entrada de `C-01` (`38.45 → 38.55 m`, `H_c = 2.35 → 2.45 m`)
  y ensancha la zapata propuesta por la regla (`B = 1.645 → 1.715 m`, talón
  `0.802 → 0.849 m`). La resistencia al deslizamiento crece de `38.66` a
  `41.46 kN/m` mientras el empuje apenas varía (`40.69 → 40.94 kN/m`), de modo
  que `E3-LRFD.est.e` pasa en `C-01` con `fila_phi_estabilidad_cabezal =
  'muros_tabla_11_5_7'` (`40.94 ≤ 41.46 kN/m`) y vuelve a fallar con
  `'zapatas_seccion_10'` (`40.94 > 33.17 kN/m`). En los tres tubos circulares
  (`A-01`, `A-02`, `B-01`) `E3-LRFD.est.e` sigue sin pasar con ninguno de los
  dos `[A]`.
- **Solución:**
  1. Se corrigió el párrafo de §3.1 en `tests/apoyo/sensibilidad.py` y en
     `docs/validacion_sensibilidad.md` para que coincida con la tabla medida.
  2. Se actualizó `test_el_cabezal_de_la_regla_frente_a_sus_dos_A` en
     `tests/test_t11_sensibilidad.py`, declarando la causa en su docstring y
     fijando el comportamiento medido de `C-01` (`("cumple", "no cumple")` en
     `fila_phi_estabilidad_cabezal` y `("cumple", "cumple")` en
     `factores_inclinacion_carga_portante`) y `{"no cumple"}` en `A-01`,
     `A-02` y `B-01`.

### Fallo 2 — Gravedad: MEDIA · Complejidad: MEDIA-BAJA
- **Test:** `tests/test_t11_sensibilidad.py::test_los_juicios_del_anexo`
- **Síntoma:** El diccionario esperado de clasificación por efecto en el test
  no reflejaba los cambios de VE-4/VE-5/VE-7 ya presentes en el anexo
  `docs/validacion_sensibilidad.md` regenerado en `8ea380b`:
  - `MUEVE EL DISEÑO` (11) y `MUEVE EL HW` (2) **no cambiaron**.
  - **12 criterios pasaron de `LEÍDO, SIN EFECTO MEDIBLE` a `MUEVE VEREDICTOS`**
    (verificado fila por fila en el anexo):
    - 11 de cabezal/terraplén/longitud que ahora mueven veredictos de
      estabilidad o armado de los **aleros verificados como muro** (VE-7,
      `T7C-04`): `distribucion_incremento_sismico`, `eta_ductilidad_cabezal`,
      `eta_importancia_operativa_conducto`, `eta_redundancia_cabezal`,
      `fc_cabezal_mpa`, `fraccion_delta_sobre_phi_trasdos`, `gamma_EQ`,
      `metodo_longitud_conducto`, `momento_talon_cabezal`,
      `peso_especifico_relleno_kn_m3` y `talud_terraplen`.
    - `espesor_pared_cajon` (0.30 → 0.25 / 0.20 m), que ahora mueve los
      veredictos del **pórtico del marco de C-01** (`A1`, `A2`, `A3`, `A4` y
      `A6` de las losas superior e inferior con `0.25 m`, y además `E3-ASD`
      del alero con `0.20 m`; VE-7, `VE7B-11`).
  - **1 criterio nuevo en `MUEVE VEREDICTOS`:**
    `factores_forma_profundidad_portante` (mueve `E1-ASD` de cabezal y alero).
  - **`demanda_sismica_licuefaccion`** pasó de `NO LO LEE LA CORRIDA` a
    `LEÍDO, SIN EFECTO MEDIBLE` porque el juego declara `licuefaccion_ems`
    desde `5f9a662`.
  - **5 criterios nuevos en el censo:** `clase_concreto_losa_entrega` y
    `relacion_co_poza_enrocado_hec14` en `LEÍDO, SIN EFECTO MEDIBLE`;
    `carga_viva_tubo_concreto_somero`, `empuje_sismico_muro_que_no_cede` e
    `intervalos_de_clase_chi_cuadrado` en `NO LO LEE LA CORRIDA`.
- **Solución:** Se actualizó el diccionario esperado de
  `test_los_juicios_del_anexo` en `tests/test_t11_sensibilidad.py`, declarando
  en comentarios la causa medida de cada movimiento.

### Fallo 3 — Gravedad: BAJA · Complejidad: BAJA
- **Test:** `tests/test_t11_sensibilidad.py::test_lo_que_la_corrida_no_lee_es_lo_que_el_anexo_explica`
- **Síntoma:** `S.NO_LEIDO_PORQUE` en `tests/apoyo/sensibilidad.py` conservaba
  `("demanda_sismica_licuefaccion", "juego")` (que ahora sí se lee) y no
  incluía explicación para los tres criterios nuevos no leídos en el juego
  (que imprimían `SIN RAZÓN ESCRITA` en `docs/validacion_sensibilidad.md`).
- **Solución:** Se retiró `demanda_sismica_licuefaccion` de `NO_LEIDO_PORQUE` y
  se añadieron las razones verificadas contra el código fuente para
  `intervalos_de_clase_chi_cuadrado` (sólo prueba chi-cuadrado del caudal
  calculado), `carga_viva_tubo_concreto_somero` (sólo tubo de concreto con
  cobertura `< 2.0 ft`) y `empuje_sismico_muro_que_no_cede` (sólo
  `regimen_cabezal = 'no_cedente'`), sincronizando
  `docs/validacion_sensibilidad.md`.

### Fallo 4 — Gravedad: BAJA · Complejidad: MUY BAJA
- **Test:** `tests/test_t11_validacion_integral.py::test_la_hidrologia_calculada_entra_al_indice_de_formulas`
- **Síntoma:** El test afirmaba que `FH.RM_INTENSIDAD`, `FH.RM_C` y
  `FH.RM_CAUDAL` seguían en la sección `## 4` (*no ejercitados*) de
  `docs/indice_formulas.md`, y luego exigía que no quedara ningún otro `` `FH. ``
  en esa sección.
- **Causa raíz:** Mejora de cobertura de VE-7 (`VE7C-06`): la cuarta corrida de
  referencia (`materiales_y_ramas`) sí ejercita el método racional modificado,
  por lo que los tres fundamentos pasaron legítimamente al §2 del índice
  (líneas 183–185). En §4.2 quedó únicamente `FH.C_SUBAREAS` (VE-7 lote B,
  `VE7B-06`, columna opcional `subareas` no presente en las corridas de
  referencia).
- **Solución:** Se actualizó `test_la_hidrologia_calculada_entra_al_indice_de_formulas`
  para comprobar que `FH.RM_INTENSIDAD`, `FH.RM_C` y `FH.RM_CAUDAL` están en el
  cuerpo (§2) y fuera del cuadro 4, que `FH.C_SUBAREAS` y `FH.FACTOR_P24` son
  los únicos `FH.*` restantes en §4, y que no falta ningún otro fundamento de
  la Fase 1-bis.

### Fallos 5 y 6 — Gravedad: ESPERADA / INFORMATIVA · Complejidad: TRIVIAL
- **Tests:**
  - `tests/test_indice_formulas.py::test_el_sello_lleva_fecha_commit_y_par_de_la_suite`
  - `tests/test_trazabilidad_csv.py::test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes`
- **Síntoma:** Ambos rechazaban `'PROVISIONAL: suite por medir'` (escrito en
  `5bafd44`) porque exigen el patrón `\d+ passed, \d+ skipped`.
- **Causa y solución:** Comportamiento intencional del sello provisional hasta
  medir la suite limpia completa con `NORMAS_DIR` y sellar los documentos con
  `python -m src.indice_formulas --escribir --suite "..."` y
  `python -m src.normativa.manifiesto --escribir --suite "..."`.

---

## 3. Verificación posterior

### Auditoría adversarial independiente (`auditor-argon`, Gemini 4 Argon High)
- **Veredicto:** **APROBADO** en los 5 ejes (cifras de `C-01` contrastadas
  contra `cb15e32` vs `8472063`, conjunto exacto `11 / 27 / 2 / 38 / 19` en
  `test_los_juicios_del_anexo`, exactitud de las 19 razones de
  `NO_LEIDO_PORQUE` y prosa §3.1, cobertura `FH.RM_*` / `FH.C_SUBAREAS`, y
  guardias AST / separación `tests/` vs `proceso/`). Se aplicó la precisión
  BAJA sobre el alcance de veredictos que mueve `espesor_pared_cajon`.

### Corridas de verificación tras las 4 correcciones (en clon aislado, sin modificar la copia local)
- `tests/test_t11_sensibilidad.py`: **9 passed** (`1 h 48 min 16 s`),
  incluyendo `test_el_anexo_de_sensibilidad_esta_sincronizado` (coincidencia
  exacta byte a byte con `docs/validacion_sensibilidad.md`),
  `test_lo_que_la_corrida_no_lee_es_lo_que_el_anexo_explica`,
  `test_los_juicios_del_anexo` y
  `test_el_cabezal_de_la_regla_frente_a_sus_dos_A`.
- `tests/test_t11_validacion_integral.py`: **31 passed** (`1 h 07 min 36 s`),
  incluyendo `test_la_hidrologia_calculada_entra_al_indice_de_formulas`.
- `pytest -m pdf` con `NORMAS_DIR` (`Andy-rba30/Normas`): **158 passed**
  (`2 min 24 s`).
- `tests/test_guardias_de_la_suite.py`, `tests/test_decisiones_diferidas.py`,
  `tests/test_sin_literales.py`, `tests/test_ve2_materiales.py`:
  **561 passed**.
- `proceso/tests`: **145 passed** (`0.91 s`).
- **Sellado definitivo (Fallos 5 y 6):** ejecutado en árbol LF limpio tras el
  commit de estas 4 correcciones y verificado con `test_indice_formulas.py`,
  `test_manifiesto_citas.py`, `test_trazabilidad_csv.py`,
  `test_ext9_paquete_servicio.py` y `test_t12_entregable.py`, quedando listo
  para validación íntegra en Linux por el workflow `Pruebas` de GitHub Actions.
