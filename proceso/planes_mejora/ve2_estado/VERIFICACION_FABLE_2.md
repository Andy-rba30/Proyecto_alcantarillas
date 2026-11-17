# Verificación independiente (segunda vuelta) de las correcciones N1 y N2 de VE-2

- Fecha: 2026-11-17. Verificador: Fable (independiente, adversarial; no corrige nada).
- Diff verificado: `d698046..claude/youthful-shannon-rjzmuc` (cabeza `0099c99`; commits
  `a78c9ff` N1, `bda51b6` N2, `0099c99` integración).
- Clon propio en `/home/user/verif2`; base de comparación `d9b59f9` (`/home/user/verif_fable_base`).
- No se corrió la suite completa (había dos en marcha). Se corrieron 16 archivos de test
  (1171 + 220 pasan) y scripts propios.

## Veredicto

**Integrar en main**, después de re-sellar `docs/indice_formulas.md` y
`docs/trazabilidad.csv` (llevan sello `PROVISIONAL` y hoy fallan sus dos tests de sello;
es el paso de cierre, no un defecto de las correcciones). N1 y N2 están resueltos como el
dueño decidió. No hay hallazgos bloqueantes, altos ni medios; quedan cinco bajos.

## Estado de N1 — resuelto

- **Los dos casos pedidos reproducen** (script propio sobre `vi.correr_juego`):
  - B-01 de la variante `caudal_calculado`: `DatoFaltanteError`, campo
    `Q_evento_extremo_m3s`, etapa «material y diametro (bucle de MD)». A-01 y A-02 siguen
    «no factible».
  - A-01 con `Q_m3s` = 1.0, `S_cauce` = 0.004 y `Q_evento_extremo_m3s` = 3.0:
    `DisenoNoFactibleError`, `delta_rasante_m` = 0.31981. La traza conserva el escalón HDPE
    Ø 1.35 m «no se pudo evaluar — falta `espesor_pared_conducto[hdpe][1350]`» en el motivo.
- **Barrido de la verificación anterior repetido** (mismos scripts, mismos 243 puntos-caso a
  expediente y 135 a perfil):

  | Comparación | Expediente | Perfil |
  |---|---|---|
  | rama contra `d9b59f9` | 6 cambian, los 6 por `Q_evento_extremo_m3s` | 0 cambian |
  | rama contra `5622940` (cabeza anterior) | 22 vuelven a «no factible» | 8 vuelven a «no factible» |

  Los 30 casos de la pared vuelven exactamente a lo de `d9b59f9` (mismo bloqueo, mismo
  delta). Ningún diámetro, sección ni material cambia.
- **La frontera es correcta para todo lo que hoy llega a la Fase 5.** Revisados todos los
  `raise DatoFaltanteError(` de M5, M2 y M8 y los `punto.exigir(...)`:
  - Dato del punto (el campo no es criterio, decide): `Q_evento_extremo_m3s`,
    `TW_evento_extremo_m`, `cota_desborde`, `ancho_derecho_via_m`,
    `cota_afectacion_aguas_arriba_msnm`, `cota_coronacion_canal`, `cota_fondo_entrada`,
    `S_cauce`, `NF_profundidad_m`.
  - Dato de catálogo en la Fase 5 (la raíz es criterio, no decide): sólo
    `espesor_pared_conducto[mat]` y `espesor_pared_conducto[mat][D]` (`M2_material.py:811`, `:840`).
  - Ninguna columna del CSV, campo de `PuntoCritico` ni clave de `servicio.CLAVES_EXTERNAS`
    coincide con una clave de `ca.CRITERIOS` (medido: intersección vacía en los tres).
  - Los datos de producto de la Fase 8 (`perfil_hdpe`, `resistencia_costura_tmc`,
    `resistencia_costura_empernada_tmc`, cuyo campo no es criterio, y
    `clases_producto_por_relleno`, `perfil_hdpe_fabricante`, que sí lo son) llevan la marca
    `escalon_cumple_lo_demas` y deciden por la rama de T-5, que el filtro nuevo no toca. Sin
    cambio respecto de `d9b59f9`.
- **Mutantes sobre `MD._falta_un_dato_de_catalogo`:** devolver siempre `False`, siempre
  `True`, y quitar el corte por el corchete mueren los tres. El test del caso real usa la
  excepción real de la pared (por el servicio), no la sintética.
- `CLAUDE.md` («Excepciones», DatoFaltanteError) recoge A1 y N1 y dice lo que el código hace.

## Estado de N2 — resuelto

- **Ficha:** etiqueta `S`, nivel `perfil`, `positivo=True`, sin `sensibilidad`, `DeEnsayo`,
  `trazabilidad` escrita, valor `None`.
- **Regla 3 y CLAUDE.md:** `_verificar_nivel` (función entera) y la sección «Nivel de
  entrega» de `CLAUDE.md` son idénticas byte a byte a las de `d9b59f9` (`diff` vacío).
- **Nivel medido:** `test_m3_medido_la_corrida_de_perfil_lo_invoca_sin_diferir` y
  `tests/test_nivel_medido.py` pasan; la medida no se relajó.
- **`Criterio.positivo` por los tres caminos** (`_verificar_criterio` con `replace`,
  `establecer_valor_dinamico`, `verificar_declaracion`, que es la guardia de
  `escribir_valor_en_archivo`): `0`, `0.0`, `-20.0`, `-1e-300`, `nan`, `inf`, `True` y
  `'20'` salen con `ValueError`; `1e-9`, `5.0` y `20.0` entran.
- **Por la CLI:** `--declarar …=0`, `=0.0` y `=-20.0` terminan con código 2 y «tiene que ser
  positivo (mayor que cero)»; `=nan` se rechaza antes. `=20.0` corre.
- **Mutantes:** `> 0` por `>= 0`, reponer la exención de `DeEnsayo` en la regla 3 y quitar
  `positivo` de la ficha mueren los tres.
- **Consumidores de un [S] guardado en `criterios_adoptados`:**
  - Pestaña 2 y `criterios_del_alcance`: filtran por `nivel`, no por etiqueta; lo muestran a perfil.
  - `editores.declarar`: sin nota, `ValueError`; con nota entra; con `0.0`, `ValueError`.
  - `barrido.motivo_para_no_barrer`: no barrible (sin ventana).
  - Memoria: la ficha sale con `[S]`, «De un ensayo … Trazabilidad exigida» y el campo
    «Trazabilidad». Ya no aparece en el anexo A.4 («Criterios [A] adoptados y su
    sensibilidad»), que filtra `etiqueta == "A"`; es coherente con que no tenga ventana.
  - JSON: `criterios.usados[]` lo lleva con `etiqueta: "S"`.
  - Ningún consumidor lo trata distinto de los otros tres [S] de ese archivo
    (`clase_sitio`, `exposicion_quimica_ems`, `PERFIL_SUELO_PRESUNTO`).

## Fichas y línea base — dicen la verdad

- **VE2-03, VE2-05, VE2-C:** lo que afirman de N1 y N2 coincide con lo medido (30 casos,
  delta 0.31981, frontera `exc.campo in ca.CRITERIOS` que existe en `MD.py:1039`, VE2-C con
  el punto (1) cerrado). VE2-05 declara el residuo de la CLI («un dato de ensayo se declara
  sin nota»).
- **`docs/linea_base.md` §17:** cierto. En los cuatro JSON cambia sólo `criterios_sha1`; en
  las tres memorias completas, la fila de la huella y la etiqueta `A` → `S` de una fila; en
  la resumida, sólo la huella.

## Hallazgos nuevos

Bloqueantes, altos y medios: ninguno.

### Bajos

- **B1 · La regla «dato del punto» sólo está fijada por `Q_evento_extremo_m3s`.** El mutante
  `_falta_un_dato_de_catalogo` → `campo != "Q_evento_extremo_m3s"` **sobrevive** a
  `test_ve2_correcciones`, `test_MD`, `test_t4_materiales_durabilidad`,
  `test_t11_no_factible_por_rasante` y `test_t11_validacion_integral` (232 pasan; no medido
  contra la suite completa). Hay al menos otro dato del punto que la regla mueve y ningún
  test fija: A-01 con Q = 1.5, S = 0.004, extremo 4.5 y sin `TW_evento_extremo_m` pasa de «no
  factible», delta 0.3198 (`d9b59f9`), a «falta `TW_evento_extremo_m`» (rama). Es lo que la
  decisión pide; falta un test con un segundo campo. `src/modulos/MD.py:1128-1131`.
- **B2 · La frontera es por nombre, no por origen.** `MD.py:1310` clasifica por «la raíz del
  campo es una clave de `ca.CRITERIOS`». Hoy acierta en todos los casos (arriba), pero un
  dato de catálogo futuro de la Fase 5 cuyo campo no sea un criterio (como ya pasa en la
  Fase 8 con `perfil_hdpe` o `resistencia_costura_tmc`) decidiría como dato del punto sin
  que nada avise. No hay test que censa los campos que la Fase 5 puede levantar.
- **B3 · La memoria imprime el valor declarado junto a «NO SE HA EJECUTADO NINGUN ENSAYO».**
  Con `--declarar peso_especifico_saturado_relleno_kn_m3=20.0` la ficha dice «Valor 20.0
  [declarado para esta corrida]» y, más abajo, «Trazabilidad: NO SE HA EJECUTADO NINGUN
  ENSAYO…» (texto estático de la ficha, `src/criterios_adoptados.py:10762`). La procedencia
  sí avisa («nadie registró de dónde»), y es el mismo patrón de los otros [S] pendientes; con
  la etiqueta [S] el contraste es más visible. Es el residuo de la CLI que VE2-05 declara.
- **B4 · La razón de N2 no se aplica a los otros tres datos de ensayo.** VE2-05 dice «un dato
  determinado por un procedimiento … es [S]», y `c_phi_fundacion`, `capacidad_portante_adm`
  y `Mw_licuefaccion` siguen [A] con `DeEnsayo` (de expediente, sin ventana; la regla 3 no
  les alcanza). La ficha no lo menciona. No afecta a ningún cálculo.
- **B5 · Dos textos atrasados.** `gui/app.py:1628` dice «[S] SÍ está — hoy tres entradas»
  (son cuatro). El título de `docs/linea_base.md` §17 sigue diciendo «sólo la huella» y su
  último párrafo ya cuenta la etiqueta; «las dos veces que la lista aparece» se lee mejor
  como «las dos memorias de perfil» (hay una fila por archivo).

### Pendiente de cierre (no es hallazgo)

- `docs/indice_formulas.md` y `docs/trazabilidad.csv` llevan sello `bda51b6+cambios-sin-commit`
  y suite `PROVISIONAL`: fallan `test_indice_formulas.py::test_el_sello_lleva_fecha_commit_y_par_de_la_suite`
  y `test_trazabilidad_csv.py::test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes`.
  Hay que re-sellar con el par de la suite completa antes de integrar.

## Lista corta

1. N1 resuelto: 30 de 30 casos de la pared vuelven a «no factible» con su delta; quedan los
   6 cambios por `Q_evento_extremo_m3s`, que es lo que A1 buscaba.
2. N2 resuelto: [S] con trazabilidad, regla 3 y CLAUDE.md idénticos a `d9b59f9`, 0 y
   negativos rechazados por los tres caminos y por la CLI.
3. Fichas y §17 de la línea base dicen la verdad.
4. Cinco bajos (B1 a B5); ninguno bloquea.
5. Re-sellar los dos documentos generados antes de integrar.
