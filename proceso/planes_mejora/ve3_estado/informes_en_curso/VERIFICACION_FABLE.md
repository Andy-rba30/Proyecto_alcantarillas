# Verificación independiente de las correcciones a la revisión de VE-2 (Fable)

Material de proceso. Verificador: sesión independiente y adversarial (modelo Fable 5.2).
Fecha: 2026-11-17. No se corrigió nada, no se hizo commit ni push en ningún repositorio.

## Qué se verificó y cómo

- Diff `d9b59f9..claude/youthful-shannon-rjzmuc` (cabeza `5622940`; seis commits:
  `b3b2832`, `09bc85f`, `16c0cb6`, `91fe918`, `f39e26f`, `5622940`).
- Clones propios, fuera del repositorio de trabajo: `/home/user/verif_fable` (la rama),
  `/home/user/verif_fable_base` (`d9b59f9`, para comparar comportamiento antes/después) y
  `/home/user/verif_fable_mut` (mutantes). Python 3.12 del `venv312`, Tk con `xvfb-run -a`,
  `NORMAS_DIR=/home/user/Normas`.
- Leídos antes: `CLAUDE.md`, `proceso/reglas_de_correccion_de_auditorias.md`,
  `proceso/planes_mejora/ve2_estado/REVISION_FABLE.md`, el bloque VE-2 de la cadena.
- Los scripts propios están en el scratchpad de la sesión (no en el repositorio); los
  comandos y salidas relevantes van citados en cada punto.

## Veredicto

**Integrar con correcciones.** Las diez decisiones del dueño están aplicadas como se
pidieron, la línea base sólo mueve `criterios_sha1`, y la suite sólo falla en los dos sellos
provisionales esperados (par abajo).
Pero la corrección de A1 hace **más** de lo que su comentario, su test y sus fichas dicen:
además del caudal del evento extremo, vuelve decisiva la **fila de pared que falta** (V7), y
con eso puntos que eran «NO FACTIBLE POR RASANTE» con su delta pasan a «falta un dato»
—un dato que, declarado, devuelve el mismo «no factible»—. Eso contradice lo que el propio
diff afirma que «no cambia» (ficha T4-10) y no lo fija ningún test. Hay que decidirlo y
documentarlo (o acotar la regla) antes de llevar VE-2 a `main`. Es el único hallazgo alto;
el resto son medios y bajos.

## Par de la suite

`xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header` en `/home/user/verif_fable`
(`5622940`, clon sin worktrees, con `NORMAS_DIR` y Tk):

**7456 passed, 10 skipped, 2 failed — 7468 collected** (1158 s, exit 1).

Los dos fallos son **sólo** los sellos provisionales, que el encargo da por esperados:

- `tests/test_indice_formulas.py::test_el_sello_lleva_fecha_commit_y_par_de_la_suite`
- `tests/test_trazabilidad_csv.py::test_el_sello_va_en_la_primera_linea_y_lleva_sus_cuatro_partes`

Los dos con el mismo motivo: «el sello tiene que llevar el PAR de la suite: 'PROVISIONAL
(PyMuPDF sí · ventana Tk sí · repositorio de normas enlazado)'» (sello con
`commit: f39e26f+cambios-sin-commit`). Ningún otro test falla. Con el re-sellado el par
esperado es **7458 passed / 10 skipped / 7468 collected** (33 tests más que la referencia;
31 son los de `test_ve2_correcciones.py`, `test_ve2_revision_m3_m4.py` y el de B1, el resto
casos parametrizados que crecen con el diff). Mientras no se
re-selle, la cabeza de la rama no está en verde y no debe ir a `main` así (regla de «Git»:
no hay commit sin la suite verde).

**Par medido: 7456 passed / 10 skipped / 7468 collected, 2 failed (sellos).**

Referencia antes de las correcciones: 7425 / 10 / 7435. La salida completa queda en
`/home/user/verificacion_fable/suite_completa.txt`.

## Estado de cada hallazgo de REVISION_FABLE.md

| Hallazgo | Decisión del dueño | Estado | Evidencia |
|---|---|---|---|
| **A1** | vía (i) | **Resuelto en su caso, con un efecto colateral no declarado** (ver N1) | abajo |
| **M1** | sólo ficha | **Correctamente diferido** | ficha VE2-04 |
| **M2** | se deja | **Correctamente diferido** (VE2-B (i), VE2-02; sin cambios) | — |
| **M3** | pasar a perfil | **Resuelto** (con dos observaciones: N2, N3) | abajo |
| **M4** | rechazo en la puerta, sin tope | **Resuelto** | abajo |
| **B1** | corregir | **Resuelto** | test nuevo `test_b1_el_caso_original_del_auditor_se_detiene_en_la_clase_d_load` |
| **B2** | dejar | **Dejado** (sin cambios en `M8.empuje_flotacion_bajo_el_nivel_kn_m`) | — |
| **B3** | corregir | **Resuelto**; re-medido | abajo |
| **B4** | corregir | **Resuelto** (los cuatro parches retirados, LEEME reescrito y cierto) | `ls proceso/planes_mejora/ve2_estado/` |
| **B5** | dejar | **Dejado** | — |

### A1 — reproducción propia

Script propio sobre `vi.correr_juego(vi.aplicar(vi.juego_completo(), cambios))`, B-01 de la
variante `caudal_calculado` (Q calculado 1.7905 m³/s), alcance de expediente:

| `Q_evento_extremo_m3s` de B-01 | `d9b59f9` (revisión) | `5622940` |
|---|---|---|
| vacío (la variante) | `DisenoNoFactibleError`, `campo None`, delta 0.3698 | `DatoFaltanteError`, `campo Q_evento_extremo_m3s`, etapa «material y diametro (bucle de MD)» |
| 1.99 | — | `DatoFaltanteError`, `campo perfil_hdpe_fabricante` |
| 1.80 | — | `DatoFaltanteError`, `campo perfil_hdpe_fabricante` |
| 0.106 (el del juego, incoherente) | `DatoInvalidoError` | `DatoInvalidoError`, `campo Q_evento_extremo_m3s` |
| 5.0 | — | `DatoFaltanteError`, `campo espesor_pared_conducto[hdpe][1350]` (**N1**) |

A-01 y A-02 siguen «NO FACTIBLE POR RASANTE» en la variante, como dice el comentario
corregido del fixture. El caso de la revisión queda resuelto y el caso 3 (1.99) fijado por
`tests/test_ve2_correcciones.py::test_con_el_evento_extremo_coherente_B01_espera_el_perfil_del_hdpe`.
`docs/validacion_integral.md` dice ahora «DETIENE … B-01: entrada del proyecto que falta —
Q_evento_extremo_m3s».

El refactor de `_exigir_datos_validos` a `_detuvo_un_escalon_que_cumplia` es equivalente
(los inválidos que le llegan ya son de la Fase 5).

Mutantes sobre `MD.py` (doce archivos de test: `test_ve2_correcciones`, `test_MD`,
`test_t11_no_factible_por_rasante`, `test_t4_materiales_durabilidad`, los dos de T-5, etc.):

| Mutante | Resultado |
|---|---|
| decisivo sin exigir que lo evaluado cumpla | muere (`…ya_incumple_no_decide`) |
| `all` → `any` | muere (`…primera_fila…`) |
| quitar `_lo_levanto_la_fase_5` | muere (`…antes_de_la_fase_5…`) |
| `decisivos[-1]` | muere |
| no decidir con la tupla vacía | muere |
| **decisivo sólo si el campo es `Q_evento…`** | **sobrevive** |
| **decisivo salvo la pared (`espesor_pared…`)** | **sobrevive** (y sobrevive también a la **suite completa**: mismo resultado que sin mutar, 7456 passed y los dos sellos) |

Los dos que sobreviven son la prueba de N1: ningún test fija qué pasa con un dato que
falta en la Fase 5 que no sea el del evento extremo.

### M3 — el nivel está medido, no opinado

Corrida propia por la CLI (CSV propio, un punto de Familia A con NF a 0.10 m):

```
python cli.py p.csv --datos-externos ext.json --alcance perfil \
  --declarar nivel_agua_diseno_v7=nf_del_punto --declarar margen_estacional_nf_v7_m=3.5 --json out.json
→ puntos[0].bloqueos[1]: tipo CriterioPendienteError, criterio peso_especifico_saturado_relleno_kn_m3,
  etapa «material y diametro (bucle de MD)», diferido_por_alcance False
```

Una corrida de perfil lo invoca y el bloqueo no queda diferido: por la segunda dirección de
«Nivel de entrega» es de perfil. `criterios_del_alcance("perfil")` lo incluye y
`criterios_de_perfil_sin_valor()` lo lista (4 claves). En `tests/test_nivel_medido.py` sigue
censado en `DE_UNA_ALTERNATIVA_NO_DE_ARCHIVO` (con los valores de archivo ninguna corrida
lo invoca) y la medida vive en
`test_ve2_revision_m3_m4.py::test_m3_medido_la_corrida_de_perfil_lo_invoca_sin_diferir`;
aceptable, y dicho en el comentario del campo.

### M4 — la puerta rechaza el negativo por todos los caminos

Medido: `cli.py --declarar margen_estacional_nf_v7_m=-0.5` → «No se pudo declarar el
criterio … no admite un valor negativo»; `editores.declarar`, `editores.verificar`,
`barrido.verificar_valores`, `ca.establecer_valor_dinamico`, `ca.escribir_valor_en_archivo`
(sobre una copia: −0.1 no se escribe y el archivo queda igual; 0.5 sí) y `declaracion.restaurar_sesion` (sesión con −2.0: queda en `rechazados`, no se declara)
lo rechazan. 0 y positivos entran; NaN no. No hay tope. La segunda línea de M8 sigue.
`no_negativo` sólo en este criterio (fijado por test). Mutantes `>= 0` → `> 0` y «eximir de
ventana a lo que no sea `EnRango`»: mueren.

### B3 — re-medido con barrido propio

Oráculo propio (Brent sobre la Sec. 4.1, `xtol=1e-15`), semillas distintas:

| Barrido | Manning sobre geometría de n_mín vs Q/A | V_erosion·A_indep/Q − 1 |
|---|---|---|
| marcos, 40 000, Q 0.1 %–99.99 %, semilla 7 | 1.885e-9 | 1.150e-9 |
| marcos, semilla 123 | 1.641e-9 | 1.001e-9 |
| marcos, semilla 99991 | 1.817e-9 | 1.109e-9 |
| marcos, Q ≥ 5 % (malla de la suite) | 1.73e-10 | 1.18e-10 |
| circulares, 20 000, semilla 20261117 | 1.252e-10 | 8.70e-11 |
| marcos, Q desde **0.01 %** | **1.81e-8** | 1.09e-8 |

El comentario nuevo de `tolerancias.py` (1.81e-9 y 1.10e-9 en marcos, 1.25e-10 en
circulares, peor caso en el marco 1.0 × 1.0 hacia el 0.5 % del lleno, «cinco veces y
media») es cierto dentro del dominio que declara. La desviación crece como 1/Q: bajo el
0.1 % del lleno 1e-8 ya no cubre (última fila). No es defecto —la tolerancia sólo la lee la
suite, cuya malla empieza en el 5 %, y el comentario dice su dominio—; se anota (B-n4).

## Hallazgos nuevos

### Bloqueantes

Ninguno.

### Altos

**N1 · La corrección de A1 vuelve decisiva también la fila de pared que falta (V7), y eso
convierte en «falta un dato» puntos que son «NO FACTIBLE POR RASANTE»; el diff afirma lo
contrario y ningún test lo fija.**

- Dónde: `src/modulos/MD.py:1120-1124` (`decisivos`, `_detuvo_un_escalon_que_cumplia`), su
  comentario `MD.py:1109-1119` («La otra mitad de T4-10 no cambia: el que falta … antes de
  la Fase 5 (sin `verificaciones_completadas`), no decide»), el docstring de
  `tests/test_ve2_correcciones.py::test_el_dato_que_falta_antes_de_la_fase_5_sigue_como_hasta_hoy`
  («la pared de un diametro, que M2 pide antes de la tabla»), las fichas T4-10 («Al revés no
  cambia»), T-5 («la otra mitad de T4-10 … no cambia») y VE2-03 de
  `docs/decisiones_diferidas.md`, y `docs/linea_base.md` §17.
- El hecho que lo desmiente: la pared **no** se pide antes de la tabla. La pide V7, dentro de
  la Fase 5, y su `DatoFaltanteError` llega a MD **con** `verificaciones_completadas`
  (V1 a V6). Medido en `d9b59f9` y en la rama: el escalón HDPE Ø 1.35 m sale con
  `[V1, V2, V2b, V3, V4, V4b, V10, V5, V6]`, todas cumplen, y la excepción
  `espesor_pared_conducto[hdpe][1350]`. El test nuevo simula el caso con una excepción
  sintética **sin** el atributo, que no es lo que el programa produce.
- Evidencia (barrido propio sobre el juego de T-11, mismo script en los dos clones; Q
  declarado de A-01, A-02 y B-01 ∈ {0.3 … 8.0}, `S_cauce` ∈ {0.004, 0.01, 0.03}, evento
  extremo ∈ {vacío, 1.11·Q, 3·Q}; 243 puntos-caso a expediente):
  - 28 cambian de `DisenoNoFactibleError` a `DatoFaltanteError`: **6** por
    `Q_evento_extremo_m3s` (lo que A1 buscaba) y **22** por
    `espesor_pared_conducto[hdpe][1350]`. Ningún otro cambio (ningún diámetro, ningún caso
    al revés).
  - A alcance de perfil (135 puntos-caso, sin evento extremo): **8** cambian, todos por la
    pared del HDPE.
  - En los 30 casos de la pared, `d9b59f9` daba delta de rasante (p. ej. A-01 con Q = 1.0,
    S = 0.004, extremo 3.0: «NO FACTIBLE POR RASANTE», `delta_rasante_m` = 0.3198; la rama:
    `DatoFaltanteError`, `campo espesor_pared_conducto[hdpe][1350]`, sin delta). En ese
    punto el concreto incumple V7 de Ø 1.20 a 1.65 m y no cabe en 1.80; el TMC incumple V7
    de 1.35 a 1.80 y no cabe en 1.95; el HDPE incumple V8 en 1.05 y **V7 en 1.20**.
  - Declarando a mano las filas que faltan (hdpe 1350: 0.11, 1500: 0.12, valores de prueba)
    los tres casos probados vuelven a `DisenoNoFactibleError` con el mismo delta (0.3198,
    0.4198, 0.3698): el HDPE Ø 1.35 y 1.50 m incumple V7 como el 1.20. El bloqueo manda a
    conseguir la ficha de un fabricante para llegar al mismo «no factible».
- Por qué es un defecto: (1) es un cambio de comportamiento **no declarado**, sobre la
  mitad de T4-10 que el propio diff dice que conserva («ahí nadie sabe si ese escalón
  cumpliría»); (2) el punto pierde el rótulo «NO FACTIBLE POR RASANTE» y el delta de 7.A,
  que es la información útil; (3) la justificación escrita («V8 sólo corre sobre el
  candidato que ya cumple lo anterior») vale para V8 y no para V7: detrás de un V7 sin
  pared quedan sin evaluar V7 y V8, de modo que «cumple lo evaluado» no es «sólo le falta
  un dato»; (4) los mutantes que excluyen la pared, o que limitan la regla al evento
  extremo, sobreviven.
- Atenuante: es literalmente lo que la vía (i) de la revisión pedía («sobre un escalón que
  cumple lo evaluado») y es simétrico con T11-03 para el dato inválido. No es un número
  mal calculado; es una clasificación que el dueño no vio al decidir.
- Corrección sugerida (decide el dueño, una de dos):
  (a) **acotar**: que sea decisivo sólo el dato que falta cuando no queda ninguna
  verificación sin evaluar que pueda incumplir —en la práctica, que `M5.verificar` y el
  verificador de perfil marquen `escalon_cumple_lo_demas` al `DatoFaltanteError` de la
  pieza de V8 (cuya condición de entrada ya es «todo lo anterior cumple»), y que MD no
  generalice—; o
  (b) **aceptar y decirlo**: reescribir la ficha T4-10, el comentario de `MD.disenar_punto`,
  el docstring del test y VE2-03 con el caso de la pared medido, y fijarlo con un test por
  el servicio (el caso A-01 de arriba), aceptando que se pierde el delta de rasante.
  En los dos casos, un test con la excepción real de la pared (con `completadas`), no la
  sintética.

### Medios

**N2 · La excepción a la regla 3 de «Nivel de entrega» es coherente con la guardia y no abre
hueco hoy, pero se justifica con la definición de [S] y deja un [A] de perfil sin ninguna
puerta en la CLI.**

- Dónde: `CLAUDE.md` («Nivel de entrega», regla 3 y su invariante),
  `src/criterios_adoptados.py::_verificar_nivel`, ficha de
  `peso_especifico_saturado_relleno_kn_m3`.
- Lo que está bien (medido): `ETIQUETAS_DE_ELECCION = ('A',)`; de 146 criterios hay 69 [A]
  de perfil y **uno solo** sin `sensibilidad`, el peso saturado. Hay cuatro [A] con
  `DeEnsayo` (`c_phi_fundacion`, `capacidad_portante_adm`, `Mw_licuefaccion`, de
  expediente, y éste); ningún otro [A] de perfil pasa hoy sin ventana. La exención exige
  `resolucion` y sólo vale para `DeEnsayo`, que a su vez exige `ensayo` y
  `trazabilidad_exigida` y prohíbe la ventana (`_verificar_criterio`). Las dos guardias
  eran, en efecto, incompatibles. `editores.declarar` exige la nota (medido: sin nota,
  `ValueError`), `barrido.motivo_para_no_barrer` lo declara no barrible, y la memoria
  imprime «De un ensayo … Trazabilidad exigida …».
- La tensión: la taxonomía de `CLAUDE.md` separa [S] de [A] con esta regla: «un [A] se
  defiende con un rango de sensibilidad porque hubo elección; un [S] no tiene rango que
  elegir y se defiende con la trazabilidad». El texto nuevo usa esa misma razón («la misma
  razón por la que un [S] declara trazabilidad y no sensibilidad») para un [A]. Por la regla
  de la propia constitución, un dato de ensayo del relleno es un **[S] pendiente de ensayo**
  («puede quedar en criterios_adoptados.py con el campo `trazabilidad`», como
  `exposicion_quimica_ems` y `clase_sitio`), y con etiqueta [S] la regla 3 no le aplicaría
  y no haría falta excepción. No es nuevo (los otros tres [A] de ensayo ya existían en
  expediente), pero la excepción lo lleva a la constitución.
- El hueco práctico: «su ventana es la trazabilidad que `DeEnsayo` exige al declararlo» es
  cierto en la pestaña 2 y **no** en la CLI. Medido:
  `cli.py … --declarar peso_especifico_saturado_relleno_kn_m3=20.0` entra sin nota (la
  memoria lo dice: «se declaró al lanzar la corrida y nadie registró de dónde»), y la
  puerta acepta también `5.0`, `0` y `-20.0`; los rechaza el consumidor
  (`DatoInvalidoError`, «tiene que ser mayor que el peso específico del agua»). Es el M4 de
  la revisión reaparecido en el criterio que M3 acaba de pasar a perfil: un [A] de perfil
  cuya puerta no rechaza nada. `docs/guia_perfil.md` (generado) propone ahora esa línea
  `--declarar … =20.0` entre las de perfil, sin trazabilidad.
- Sugerencia: decisión del dueño entre (i) dejarlo y precisar en `CLAUDE.md` que la
  trazabilidad se exige en la ventana y no en `--declarar`, y marcar el criterio con un
  signo o cota inferior en la puerta (`positivo`), o (ii) reetiquetar los datos de ensayo
  como [S] y retirar la excepción. Ninguna de las dos bloquea la integración.

### Bajos

- **N3 · Fichas que quedaron diciendo lo contrario.** `docs/decisiones_diferidas.md`,
  ficha VE2-C («Abierto: (1) … una corrida de perfil se detiene en
  `peso_especifico_saturado_relleno_kn_m3`, de expediente … que el filtro de perfil de la
  pestaña 2 no muestra») y ficha VE2-02 («(c2) … se detiene en un dato de ensayo de
  expediente (VE2-C)») siguen dando por abierto lo que M3 cerró; VE2-03 lo cierra más
  abajo sin tocar las otras dos. Corrección: marcar cerrado el punto (1) de VE2-C y el
  (c2) de VE2-02 con remisión a VE2-03.
- **N4 · `CLAUDE.md` («Excepciones», DatoFaltanteError) no recoge A1.** Sigue describiendo
  como decisivos sólo los tres datos de producto de la Fase 8
  (`ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`); desde A1 decide también el que falta en la Fase 5.
  El commit de integración dice «CLAUDE.md» y sólo toca «Nivel de entrega». Depende de cómo
  se resuelva N1.
- **N5 · Orden de las fichas.** VE2-04 está antes que VE2-03 en
  `docs/decisiones_diferidas.md`. Cosmético.
- **N6 · B3, dominio de la tolerancia.** Bajo el 0.1 % del lleno la desviación pasa de
  1e-8 (1.81e-8 con Q desde el 0.01 %). El comentario lo acota bien; conviene que diga
  también que la desviación crece como 1/Q, para que nadie baje la malla de la suite sin
  volver a medir.
- **N7 · Mutante trivial vivo en `_verificar_signo`.** Cortar con `valor is None` antes de
  comprobar la forma sobrevive: el test de «`no_negativo` sobre una categoría es una ficha
  mal escrita» usa un criterio con valor. Un caso con `valor=None` lo mataría.

## Lo verificado que está bien

- **Línea base.** Los cuatro `informe_*.json` comparados hoja por hoja contra `d9b59f9`
  (1086, 2209, 1838 y 721 hojas): la única que cambia es `/expediente/criterios_sha1`. En
  las cuatro memorias HTML, sólo la fila de la huella (`cdc46295…` → `16cd612a…`). Ningún
  diámetro, sección, material ni HW.
- **Recuentos.** 146 criterios; `CLAUDE.md` dice «146 desde VE-2» en sus tres recuentos; no
  entra ni sale ningún criterio (sólo el campo `no_negativo` y un cambio de nivel).
- **Ficha VE2-04 (M1).** La cita está donde dice: HDS-5 (hif12026), PDF 100, pág. impresa
  3.18, «In outlet control, the cross sectional area of the flow is defined by the geometry
  of the outlet and either critical depth, tailwater depth, or the height of the conduit».
  Los números, recalculados: `V_salida` = 1.5076 m/s y `V_erosion` = 1.1069 m/s
  (Ø 0.90 m, Q = 0.3, S = 0.001, L = 20, TW = 0, concreto). El símbolo
  `M5._velocidad_de_v3` existe. No se tocó el cálculo.
- **Ficha VE2-03.** Lo que afirma de M3, M4, B1, B3 y B4 es cierto; lo de A1 es cierto y
  está incompleto (N1).
- **B1.** El caso G2 original (S = 0.012) queda fijado con lo que da hoy (bloqueo
  `DatoFaltanteError` de `clases_producto_por_relleno` en Ø 1.65 m); la tolerancia del
  test es nombrada (`ABS_UN_MM_POR_S`).
- **Reglas de estilo en el diff de `src/`.** Sin literales nuevos fuera de los permitidos
  (el `0` de `>= 0`; `tolerancias.py` está exento); sin `==` entre floats; la guardia de
  signo está en positivo y negada (`not c.valor >= 0`, forma MAT-D13) y va detrás de la
  finitud; `ValueError` en la puerta es la convención de SIS-E-05, no lógica de negocio;
  ninguna excepción nueva fuera de `ErrorProyecto` en el cálculo.
- **Tests modificados.** Cada cambio en un test existente (`test_t7b`, `test_ve2_flotacion`,
  `test_cierre_perfil`, `test_criterios_adoptados`, `test_nivel_medido`,
  `test_t11_validacion_integral`) declara su causa y corresponde a M3 o M4; ninguno relaja
  una comprobación de cálculo.
- **Documentos generados.** Los tests de sincronía del cuerpo (manifiestos, índice de
  fórmulas, trazabilidad, validación integral, guía de perfil, decisiones diferidas) pasan
  dentro de la suite. Los sellos «PROVISIONAL» de `indice_formulas.md` y `trazabilidad.csv`
  son los dos únicos fallos, esperados; no se cuentan como hallazgo, pero hay que
  re-sellar antes de integrar.

## Lista corta

1. **N1 (alto):** A1 hace decisiva también la fila de pared que falta en V7; 30 de 378
   puntos-caso del barrido pasan de «NO FACTIBLE POR RASANTE» con delta a «falta
   `espesor_pared_conducto[hdpe][1350]`», y con esa fila declarada vuelven a «no factible».
   Contradice T4-10 y el comentario del propio diff; sin test. Decidir: acotar o documentar.
2. **N2 (medio):** la excepción de la regla 3 no abre hueco en la guardia (un solo [A] de
   perfil sin ventana), pero se apoya en la definición de [S] y en una trazabilidad que la
   CLI no exige; la puerta acepta −20 para el peso saturado.
3. **N3–N7 (bajos):** fichas VE2-C y VE2-02 desactualizadas; `CLAUDE.md` «Excepciones» sin
   A1; orden de fichas; dominio de la tolerancia de B3; un mutante trivial.
