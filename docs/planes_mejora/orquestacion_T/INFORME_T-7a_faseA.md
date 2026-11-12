# Informe de FASE A — T-7a · Cabezal: geometría por punto y aleros

- Worktree `/home/user/wt/T-7a`, rama `tesis/T-7a` (empujada a `origin`), base `df1b23c`.
- Último commit de la rama: ver la línea «SHA» al final (serie `wip(T-7a)`; al integrar se
  aplasta en `tesis(T-7a): …`). NO fusionado a `main`.

## 1. IDs

| ID canónico | Estado propuesto | Por qué |
|---|---|---|
| `INF-4.2` | **Cerrado** | `M9.predimensionar_cabezal`: coronación = max(clave exterior + recubrimiento + bordillo, nivel de agua + resguardo); D_f ≥ 0.80 m (E.050 Art. 26.2, [N]) y a la salida bajo el fondo de la hoya − 2.0 ft (AASHTO 12.6.5, [C]); tipo por altura (ciclópeo ≤ 2.0 m); pantalla, zapata (≥ 0.30 m en ciclópeo, E.060 22.7.4 [N]), punta, talón, longitud del muro; losa de entrega y dentellón. Cada dimensión con origen «propuesta por regla» / «declarada». |
| `INF-4.3` | **Cerrado** | `Aleros` + `M9.predimensionar_aleros` (α, L_a, H_inicial, H_f, espesor, zapata); `angulo_aletas` con valor (regla 45°/30°); coherencia embocadura↔ke↔carta del marco (`verificar_coherencia_embocadura_cajon`). |
| `INF-5.1.15` (el «INF-5.1.12» del prompt) | **Cerrado** | La Fase 9 es por punto (`InformePunto.cabezal`, `servicio._fase_9`); el proyecto conserva la suma (`InformeCabezal.por_punto`); `geometria_adoptada` (geometría única) retirada. |
| `INF-4.1` | **En parte** | Al cabezal entran por punto D o B×H, HW, cotas de 7.B, talud, esviaje y socavación (`ExtremoDelConducto`). Los geotécnicos y sísmicos (γ, φ, c, q_adm, NF en empujes, PGA, γ_EQ) los ensambla T-7b. |
| `INF-3.4.1` | **Cerrado** | `predimensionamiento_cabezal` deja de estar vacío (reglas [A]) y `GeometriaCabezal` gana longitud. |
| `INF-3.4.2` | **Cerrado** | Los aleros existen (tipo, función, criterio con valor). |
| `INF-3.4.7` / `INF-4.7` | **En parte** (sin cambio de estado sugerido; T-10) | La memoria imprime la Fase 9 del punto (tabla dimensión/valor/origen/regla + pasos 9.0.x) **cuando el punto tiene cabezal**, que a expediente hoy no ocurre (V5, ficha T7A-01). Sin tablas de estabilidad (T-7b). |
| `INF-5.1.12` canónico (M10) | **No tocado** | Es de T-9. |

## 2. Tests y par

- **Nuevo:** `tests/test_t7a_cabezal_geometria.py`, **67 tests** (fichas y constantes; 8 citas;
  bandas de aletas = filas de cajón transcritas; regla del ángulo; coherencia del marco; el
  tubo no se mueve; predimensionamiento con aritmética escrita —voladizo, gravedad con el
  mínimo de E.060, salida con hoya, aleros con coseno, sin aleros, alero que no se alarga—;
  CB1-CB5; dimensiones declaradas y la puerta de `cabezal_declarado`; longitud entre
  cabezales; pipeline perfil/expediente; Fase 9 de A-01, A-02 y del marco C-01; memoria,
  JSON y CLI). **+7** en `test_decisiones_diferidas` (fichas T7A-01..07). Total **+74**.
- **No se escribieron en rojo primero** (declarado, ficha T7A-07). Rojo **medido** copiando el
  archivo a un `git archive df1b23c`: **63 failed + 3 errors de 66, 0 passed** (con imports
  protegidos; sin protegerlos, error de colección).
- **Reescritos al contrato nuevo (sin sumar ni restar):** `test_M9_cabezal` (geometría por
  criterio retirada; `predimensionamiento_cabezal` sale de la lista de vacíos de Fase 9),
  `test_modelos` (talón sin declarar → `DatoFaltanteError`), `test_cli` (Fase 9 ya no se
  detiene en `predimensionamiento_cabezal`), `test_criterios_adoptados` y `test_ext5_forma_gui`
  (el criterio de prueba vacío/float pasa de `angulo_aletas` a `Mw_licuefaccion`),
  `test_nivel_medido` (`angulo_aletas` sale de `SIN_CONSUMIDOR_Y_SIN_MEDIDA`),
  `test_variables_entrada` (`angulo_aletas` con consumidor M9), `test_t8_proteccion` (la
  embocadura de la entrada es la del punto), `test_memoria_sustentada` (siete `F9.*` en el
  censo de inalcanzables), `test_sin_literales` (`src/dominios.py`: 11 → 12),
  `test_ext8_rendimiento_gui` (techo de páginas 21 → 22, **remedido**: bytes por punto
  idénticos a la base, 70.3 KB; la memoria de 1 punto bajó de 101 a 100 páginas y la de 4
  sigue en 163), y el fixture `tests/fixtures/datos_referenciales_prueba.md` (saca los dos
  criterios que ya tienen valor).
- **Par medido sobre la rama (commit `64f7d02`), con `NORMAS_DIR`, PyMuPDF sí · Tk no:
  5034 passed / 16 skipped / 5050 collected** (base `df1b23c`: 4960 / 16 / 4976).

## 3. Línea base

- Regenerada (README con sección T-7a). Cambia FORMATO: la huella de criterios y de la hoja
  de ruta; una línea «Embocadura: …» por punto en los cuatro `cli_*.txt`; la clave `cabezal`
  por punto en los JSON (embocadura con aleros a 45°, `cabezales: null`); en el bloque del
  proyecto sale `geometria` y entra `por_punto` (vacío); sale el bloqueo y la ficha de
  `predimensionamiento_cabezal`; recuentos 102/35 → 105/33; notas del cabezal; en la ancha,
  la protección de entrada de A-01/A-02 pasa de `cabezal_recto` a `cabezal_con_aleros`.
- Sin cambio: los dos CSV de resumen y `memoria_punto_cajon.html`.
- **Diámetros movidos: ninguno.** Comparador de E-B en los tres JSON: ninguna diferencia en
  `diseno`. Medido además fuera de la línea base: HW de A-01/A-02/B-01 idénticos bit a bit
  con aleros a 45°, a 60° y con cabezal recto; C-01 con los siete del cajón sigue en
  marco 1.20 × 0.90 m con HW 0.623401… idéntico a la base.

## 4. Diferidos y pendientes

- Fichas (Parte XLVI provisional de `docs/decisiones_diferidas.md`): **T7A-01** Fase 9 por
  punto inalcanzable a expediente mientras V5 pare (`servicio._fase_9`); **T7A-02**
  embocadura de perfil y coherencia del marco, caja receptora no adoptada, Carta 11 sin
  banda, choque previsible con T-3; **T7A-03** cos α frente al «sen α» del encargo;
  **T7A-04** reglas [A] en el extremo de más material, VARIOS no disponible, E.060 14.5.3.2 no
  aplica, pie del muro; **T7A-05** desplante bajo la hoya con 2.0 ft (lectura [C]); **T7A-06**
  longitud entre cabezales cerrada sin sustituir a la del diseño (cierra la mitad de T6-01);
  **T7A-07** aceptación escrita después del código.
- Criterios: ninguno nuevo sin valor. `angulo_aletas` y `predimensionamiento_cabezal` pasan a
  tener valor (35 → 33 sin valor). Nuevos con valor: `embocadura_cabezal` [A] perfil,
  `margen_zapata_bajo_socavacion_m` [C] expediente (0.6096 m), `dentellon_losa_entrega` [N->]
  expediente (0.80 × 0.40 m, Lámina 04). Total 105 criterios.
- No hecho: ayuda de entrada de la GUI para `cabezal_declarado`; verificación CB del mínimo de
  0.30 m de E.060 cuando el proyectista DECLARA una zapata de gravedad más delgada; excepción
  de roca de E.050 26.2; tipo «caja receptora»; «plano tipo MTC para D ≤ 1.20 m» (las Láminas
  no tienen cotas: `SIN_COTAS_LAMINA_03`, Lámina 02/02-A con letras); mutación de M9 con el
  arnés de EXT-11; tests de ventana real (no hay Tk en el contenedor).

## 5. Citas nuevas (verificadas por la sesión contra el PDF: texto, título y paginación)

`E050.26.2#PROFUNDIDAD` (pág. 38/PDF 38) · `AASHTO_LRFD_9.12.6.5#ZAPATAS`, `#DENTELLON`,
`#ALEROS` (12-20/PDF 1658) · `AASHTO_LRFD_9.10.6.1.2#DESPLANTE` (10-52/PDF 1341) ·
`E060.22.7.4#ZAPATA` (193/PDF 193) · `MC_HHD.LAMINA_02A` (208/PDF 211, por imagen y texto) ·
`MC_HHD.LAMINA_04#DENTELLON` (210/PDF 213, por imagen y texto). Siete fundamentos `F9.*`.

## 6. Filas del tracker para la FASE B

| ID | Estado | Responsable | Nota |
|---|---|---|---|
| INF-4.2 | Cerrado | Claude Code (cadena T, T-7a) | `M9.predimensionar_cabezal` + CB1-CB5; ver T7A-04, T7A-05 |
| INF-4.3 | Cerrado | Claude Code (cadena T, T-7a) | `Aleros`, `predimensionar_aleros`, `verificar_coherencia_embocadura_cajon`; cos α (T7A-03) |
| INF-5.1.15 | Cerrado | Claude Code (cadena T, T-7a) | Fase 9 por punto; `geometria_adoptada` retirada |
| INF-3.4.1 | Cerrado | Claude Code (cadena T, T-7a) | criterio con reglas; `GeometriaCabezal.longitud` |
| INF-3.4.2 | Cerrado | Claude Code (cadena T, T-7a) | aleros con tipo y función |
| INF-4.1 | En parte | Claude Code (cadena T, T-7a) | datos geométricos/hidráulicos por punto; geotécnicos y sísmicos: T-7b |
| INF-3.4.7, INF-4.7 | (sin cambio; nota) | — | bloque de memoria del punto existe; inalcanzable a expediente (T7A-01); tablas de estabilidad: T-7b/T-10 |

`LO_QUE_ESCRIBIO_CADA_PROMPT` (test_t0_gobernanza): fila T-7a con los cinco cerrados y el en
parte de arriba. CLAUDE.md al integrar: 105 criterios / 33 sin valor; `dominios.py` 12
marcas; `servicio.CLAVES_DE_CABEZAL`; la cuenta de tests (+74).

## 7. Preguntas para el dueño

1. **Embocadura del marco (choque con T-3).** Con `embocadura_cabezal = cabezal_con_aleros`
   (archivo) y aleros a 45°, `embocadura_cajon`/`ke_entrada_cajon` deben ser de la banda
   30–75° (Carta 8 escala 1 o Cartas 9/12/13 de 45°; ke `cajon_aletas_30_75_*`, 0.4). Si T-3
   adopta «square edge headwall 90°» (sin aleros), C-01 se detendrá en la coherencia.
   Opciones: (a) T-3 adopta las filas de 30–75° (recomendada: es lo que ya declaran todos
   los tests del cajón y el HW de C-01 no cambia); (b) `embocadura_cabezal = cabezal_recto`,
   que vale para TODA la obra (con tubo no mueve nada; C-01 pasa a ke 0.5 y su HW sube de
   0.6234 a 0.6391 m con la misma sección). Un criterio por familia no existe hoy.
2. **¿Correr la Fase 9 del punto como anticipo a perfil?** A expediente nunca corre (V5 se
   detiene en `ancho_derecho_via_m`, sin puerta). El encargo dice que no; se pregunta si se
   quiere ver el cabezal en la memoria de perfil como información no bloqueante.
3. Confirmar las tres lecturas del proyecto: cos α (y no sen α) con α medido con el eje; el
   pie del cabezal de salida en la más baja entre solera y fondo del receptor (en A-01 baja
   el desplante 0.69 m); y que la zapata del cabezal es una «footing of structures» de
   AASHTO 12.6.5 (margen de 2.0 ft, [C], ventana 0–0.6096 m).
4. Nota: la rama «60° en caja receptora» del encargo no se adoptó (Lámina 02-A: caja
   receptora sin aleros); queda como valor declarable dentro de la ventana.

## 8. Paradas

PARADA (c): no se activó (ningún diámetro ni sección ni HW del fixture se mueve). Las
paradas (a) y (b) no aplican a T-7a.

## SHA

Rama `tesis/T-7a`, último commit de código `64f7d02` (suite medida sobre él). Sólo en la
rama; `origin/main` sigue en `df1b23c`.
