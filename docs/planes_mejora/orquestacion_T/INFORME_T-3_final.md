# Informe final — T-3 (Familia C: el marco de concreto se dimensiona), correcciones + integración

## 1. Entrega

- **`origin/main` = `6c25f1d`** (fast-forward desde `e78a4e7`; un solo commit
  `tesis(T-3): … — INF-0.4, INF-3.2.1 (cerrados); INF-0.5 (en parte)`, pie de la cuarta sesión).
  Confirmado con `git fetch origin main`: `origin/main == HEAD == 6c25f1d`.
  La rama `tesis/T-3` quedó empujada en el mismo commit.
- Ritual: la FASE A se aplastó y se rebasó sobre `e78a4e7` (conflictos resueltos conservando las dos
  partes: `modelos.py`, `citas.py`, `fundamentos.py` —cerrado el paréntesis de `MARCO_DEMANDA`—,
  `variables_entrada.py`, `test_memoria_sustentada.py`, `test_ext8`, `decisiones_diferidas.md`
  —Parte de T-3 renumerada a **XLVII**—; los generados y la línea base se tomaron de main y se
  regeneraron). Después, las correcciones H1–H12, y al final todo aplastado sobre `origin/main`.

## 2. Par de la suite (configuración «PyMuPDF sí · ventana Tk no»)

| Árbol | Con `NORMAS_DIR` | Sin `NORMAS_DIR` |
|---|---|---|
| final, antes del push | 5336 passed, 16 skipped | 5318 passed, 34 skipped |
| `origin/main` = `6c25f1d` (remedido) | **5336 passed, 16 skipped (collected 5352)** | — (mismo árbol salvo un comentario de `modelos.py`) |

Base `e78a4e7`: 5230/16/5246. **+106 tests netos**, ninguno `pdf`, Tk ni `NORMAS_DIR`
(los `-m pdf` siguen en 105 en los dos árboles, contado con `--collect-only`).
CLAUDE.md: «sí · no» MEDIDO 5336/16; las otras tres DERIVADAS (+106): 5349/3, 5245/107, 5232/120.

## 3. IDs

| ID | Estado | Por qué |
|---|---|---|
| **INF-0.4** | **Cerrado (entero)** | Los siete del marco con valor de archivo, fila, cita y ventana; con los datos del canal C-01 sale marco 1.20 × 0.90 sin declarar nada; lo que detiene la Familia C es ya sólo el dato (Q, S, coronación). |
| **INF-3.2.1** | **Cerrado (entero)** | La mitad del cajón: `n_manning_cajon` [C] = fila «Concrete Boxes» de HDS-5 Tabla B.1. La del HDPE la cerró T-4; la fila pasó de «Cerrado parcial» (T-4) a «Cerrado» (T-3) con el texto de T-4 detrás de «Anterior:». |
| **INF-0.5** | **En parte (nota)** | Sigue «Abierto»; nota: los siete del cajón salen de los vacíos, 110 criterios / 27 sin valor; quedan los de T-7a/b/c. |

`tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`: fila de T-3 (`INF-0.4`, `INF-3.2.1`
cerrados) y `INF-3.2.1` retirado del parcial de T-4.

## 4. Hallazgos de la auditoría, uno a uno

- **H1 (ALTA) — cerrado.** Verificado contra el PDF: HDS-5 Tabla B.1, pág. impresa B.6 / PDF 208,
  «Concrete Boxes | Smooth | 0.012-0.015 | FHWA 1961»; B.3, pág. impresa B.2 / PDF 204 (renderizada:
  la página imprime «0.022␣␣see concrete lined open channels␣␣from HDS 3 Table 1»). `n_manning_cajon`
  = `concrete_boxes` **[C]**; par leído del registro (`constantes_normativas.MANNING_CAJON_HDS5`);
  `tablas.py` marca la fila `Usada`; cita nueva `HDS5_3ED.B.3#CAJON_IN_SITU`; fundamento nuevo
  `F4.N_CAJON_TB1` (el `F4.N_CAJON` queda para la alternativa). Ficha con las tres lecturas y la
  DIRECCIÓN de cada extremo; retirada la frase del «acabado». Alternativa barrible: «afinado» de la
  Tabla N° 09 (verificado: entra por `--declarar`; por `editores.declarar`/barrido exige nota, porque
  la resolución tiene dos tablas y la primera es la B.1). **Sección de C-01 sin mover** (guía y
  corrida 6); movidos en la corrida 6: y_n 0.4043 → 0.4248 m, V erosión 2.230 → 2.084, V
  sedimentación 1.752 → 1.667 m/s, y/H (V1) 0.448 → 0.468, perfil y_entrada 0.4034 → 0.4209, V_min
  1.756 → 1.683; **HW de salida 0.6234 → 0.6230 m** (E a la entrada +4.7 mm por fricción, pérdida de
  entrada −5.1 mm por menor velocidad; comprobado a mano). HW de entrada (0.590/0.589) no se mueve.
- **H2 — cerrado.** `M3.tirante_critico_trapecial` (Q²T = gA³; cita `HDS5_3ED.A.3.1#CRITICO`);
  con y_n ≤ y_c el remanso NO concluye (S1 con resalto), `longitud_minima_m` = None. Dorado del
  auditor a mano: y_c = (Q²/gb²)^{1/3} = 0.3712, y_n (bisección) = 0.231.
- **H3 — cerrado.** `remanso_canal(..., vc2=)`: con VC2 INDICADOR no concluye y no publica ni dh ni
  L. El caso del auditor (guía + sección b 1, z 1, n 0.025, S 0.001) ya no dice «no levanta».
  `RemansoCanal.concluye`, `y_critico_canal_m`, `motivo_no_concluye` en el objeto y en el JSON.
- **H4 — cerrado.** En Familia C, G2 = fondo + desnivel − desajuste de VC2; tabla del auditor:
  36.195 CUMPLE/CUMPLE, 36.185 NO_CUMPLE/INDICADOR. A y B sin cambio (test).
- **H5 — cerrado.** Verificados los tres textos: MTC 4.1.1.3.4 a) impresa 72 / PDF 75; Lámina N° 03
  impresa 209 / PDF 212 (renderizada); AASHTO LRFD 12.6.6.3, 12-22 / PDF 1660 («If soil cover is not
  provided…»; cita nueva `AASHTO_LRFD_9.12.6.6.3#SIN_COBERTURA`). `TamizadoRasante.cobertura_como_aviso`:
  en el marco bloquean la clave bajo la subrasante y el resguardo; la cobertura 0.3048 da INDICADOR
  (llega a `avisos()` y a «Verificaciones con aviso»). G1 del tubo sin cambio. **Caso del auditor
  (rasante 38.40 / subrasante 38.25):** la corrida termina sin salir de `ErrorProyecto`; C-01 no
  dimensiona: escalón 1 incumple V4 y V7, escalón 2 `DatoInvalidoError` (clave sobre la subrasante)
  detiene el material. Con la geometría de C-01 el aviso de G1 es inalcanzable en corrida: V7 (DC = 0)
  exige ~0.83 m de relleno con sumersión completa.
- **H6 — cerrado (textos + ficha).** V7 no se tocó. Verificado a mano: 1.00×1.00 → 18.21 vs 19.23
  kN/m; 1.50×1.20 → 18.9 vs 29.8; t = 0.26 → 23.42 vs 23.96. Textos corregidos en
  `secciones_cajon_normalizadas`, `espesor_pared_cajon` («extremo favorable a V7») y ficha T3-01;
  ficha nueva **T3-08** sobre `src/modulos/M5_verificaciones.py::v7_flotacion`.
- **H7 — cerrado.** `formula_cita_id = ""` en 7.B.R, 7.B.M y VC2 (citas en `citas_textuales` y umbral).
- **H8 — cerrado.** Test vacuo reescrito (mide `campo == "seccion_receptor_medida"`); tests para margen
  y frontera de VC2, `cota_lamina`, guardias de no finitud (Q, HW, S, t), tolerancia 0, SOBRE/BAJO,
  tabique con N = 1. Mutación (arnés EXT-11, seis funciones tocadas): 104/120 → **113/120 (94.2 %)**;
  los 7 vivos son equivalentes (frontera y_n = y_c con TOL 1e-9 ×2, desajuste = 0, semilla/duplicación/
  signo del corchete del crítico ×4), censados en T3-12.
- **H9 — cerrado.** El aviso de VC2 imprime S = (entrada − fondo)/L, «valor calculado, de primer
  orden» (C-01 corrida 6: 0.0326 m/m).
- **H10 — cerrado.** Página 78 renderizada: el corrimiento alcanza A.2, B.1, B.2 y C (A.1 alineado).
  `DIS-MCHHD-T09-A2-DESPLAZADA` reescrita sobre la evidencia interna (gana «MC_HHD (evidencia interna
  de la pagina)»), sin Chow; dice que la literal sería más conservadora para capacidad. Retirado
  «contrastada con Ven Te Chow» del criterio, de `constantes_normativas`, `tablas.py` y del test.
  Nota en la v8 bajo la tabla de Manning.
- **H11 — cerrado.** «Provisional»/«sin decidir»/«pendiente del dueño» retirados (criterio, sensibilidad,
  v8 §2.3, ficha T3-01); ampliar la progresión diferido a la sección del canal (ANA/Junta).
- **H12 — cerrado.** `espesor_pared_cajon` sigue [A]; ficha **T3-11** con la razón.
- Decisiones del dueño aplicadas: progresión mantenida; embocadura aletas 30–75 (coherencia a T-7a);
  VC2 aviso.

## 5. Tests

- Nuevos: `tests/test_t3_familia_c.py` (44; FASE A, rojo medido 38/3 contra `df1b23c`) y
  `tests/test_t3_correcciones_auditoria.py` (63; escritos antes del código, sin `xfail`; rojo medido
  contra `c6712d4` con el archivo final: **33 rojos, 30 verdes**, guardias y matadores de mutantes).
- Crecen: 12 anclajes T3-01..12 (`test_decisiones_diferidas`), 1 en `test_ext5_forma_gui`.
- Bajan: 7 en `test_criterios_adoptados` (vacíos del cajón) y 7 en `test_guia_perfil` (ejemplos de
  `--declarar` del cajón).
- Reescritos declarándolo: `test_t3_familia_c` (fila de Manning fuera del parametrizado de la guía;
  reproducción con el n de archivo; remanso de la sonda de la guía «no concluye»; test vacuo),
  `test_memoria_sustentada` (`F4.N_CAJON_TB1`), `test_ext8` (techo 110 KB; medido 109.7 KB y 31.7 pág.),
  `test_t0_gobernanza`.

## 6. Números movidos — **diámetros/secciones/materiales movidos: ninguno**

Comparador contra la línea base de `e78a4e7`: A-01, A-02, B-01 sin diferencias de cálculo
(sólo `geometria_marco`/`remanso_canal` en `null`). C-01: de `CriterioPendienteError(embocadura_cajon)`
a `DatoFaltanteError(cota_coronacion_canal)` en las corridas ancha y de expediente; huellas; 34 → 27
sin valor; corrida 6 nueva con C-01 **marco 1.20 × 0.90**, control de salida, HW 0.623 m, Fase 6 bajo
la envolvente (HEC-14 no evaluable para un marco: rige Laushey d50 0.120 m, espesor 0.210, longitud
5.000, con aviso); dentro de la corrida 6, los deltas de H1 de §4 y el admisible de G2 36.200 → 36.190
(H4). Sin cambio: `cli_perfil.txt`, `cli_rama_error.txt`, los dos CSV, `entradas_ampliadas.json`.
Detalle en `tests/linea_base_familia_c/README.md`.

## 7. Diferidos (Parte XLVII)

T3-01 progresión (ampliar con la sección del canal) · T3-02 embocadura (T-7a) · T3-03 VC2 (tolerancia
del canal para bloquear) · T3-04 remanso paso a paso · T3-05 multicelda (dato de arrastre) · T3-06
`GeometriaMarco` sin consumidor en M8 (M8 lee `Seccion`/`espesor_pared`/`M5.cota_clave`; no forzado) ·
T3-07 R4 del ke · **T3-08 V7 sin peso propio** · T3-09 n del marco · T3-10 G1 del marco avisa ·
T3-11 espesor [A] · T3-12 rojo y mutación.

## 8. Preguntas para el dueño (con recomendación)

1. **V7 con el peso propio del marco (T3-08).** Hoy DC = 0 (lado seguro). Pesar el concreto haría
   alcanzables escalones que hoy V7 rechaza y, con la progresión de la cadena, probablemente daría
   1.00 × 1.00 a C-01 (parada (c)). Recomiendo decidirlo cuando exista la sección del canal (ANA/Junta),
   midiendo el fixture antes y después.
2. **n del marco.** Aplicada la resolución del orquestador (B.1 [C]); «afinado» queda barrible.
3. **VC2 como bloqueo**: necesita la tolerancia del proyecto del canal.

## 9. Lo que NO se hizo

- No se tocó V7 ni M8 (no se migró la demanda del marco a `GeometriaMarco`).
- El remanso sigue sin perfil paso a paso; cuando no concluye, no da cifra.
- Los tests de las correcciones no usan `xfail(strict=True)`: el rojo se midió contra el árbol previo.
- No se midieron las tres configuraciones con Tk o sin PyMuPDF (se dicen derivadas).
- No se ejercitó la pestaña 2 de la GUI (sin Tk): la alternativa de la Tabla N° 09 desde un editor
  exige nota por tener la resolución dos tablas (verificado por `editores.declarar`).
