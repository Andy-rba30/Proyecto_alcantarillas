# Encargo: AUDITORÍA ADVERSARIAL (primera pasada) de T-5 — estructural del conducto, Fase 8 real

Eres el auditor adversarial. SOLO LECTURA sobre el repositorio: no edites ni hagas commits. Tu trabajo es intentar REFUTAR el
trabajo de otro agente antes de que se integre en `main`. Es para una tesis de ingeniería: todo tiene que estar verificado contra
el PDF de la norma y ser ingenierilmente coherente.

- Worktree a auditar: `/home/user/wt/T-5` (rama `tesis/T-5`, HEAD `ab7fc3a`). Diff a auditar: `git diff 7fb7926 ab7fc3a`
  (3 commits; base `7fb7926` = T-0+T-2+T-4). `origin/main` ya va por `df1b23c` (T-1, T-6, T-8 después): la integración vendrá luego.
- Lee primero: `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ORQUESTACION.md` (convenciones, reglas no negociables, lecciones de auditorías previas) y
  `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/orq/ENCARGO_T-5.md` (lo que se le pidió al implementador, con las precisiones del orquestador). De `CLAUDE.md` del worktree:
  «Fuente de verdad», «Taxonomía», «Arquitectura», «Nivel de entrega», «Excepciones». Los mensajes de los 3 commits resumen lo hecho.
- PDF: `/home/user/andy-rba30/normas/normas/` (`export NORMAS_DIR=/home/user/andy-rba30/normas`). Leer:
  `python3 -m src.normativa.extraccion texto <fragmento> <pagPDF>` o `import fitz`. Página escaneada → renderízala
  (`page.get_pixmap(dpi=170).save('/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud/x.png')`) y léela como imagen con Read. Temporales sólo en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud/`.
- Puedes correr tests y scripts (no la suite entera más de una vez; 4 CPU compartidas). Para experimentos que necesiten editar
  código (mutantes), usa `tests/apoyo/mutacion.py` (trabaja sobre copias) o una copia del árbol en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud/`; nunca edites el worktree.

## Qué comprobar (como mínimo)

1. **Cada cita y cada número contra el PDF** (numeral, título, página impresa y PDF, texto literal; unidades y conversión a SI con
   su sufijo `_SI`): AASHTO LRFD 9.ª 3.6.1.2.6 a/b/c (LLDF, área de contacto, presión por el relleno), 3.6.2.2 (IM), 3.6.1.1.2
   (presencia múltiple), 3.4.1 y Tabla 3.4.1-2 (γ de EV por tipo de estructura enterrada), 12.5.5 y Tabla 12.5.5-1 (φ), 12.6.6.3
   (cobertura mínima), 12.7.2.x (empuje, área de pared, pandeo, costura, flexibilidad), 12.10.2.1 (Fe / tipos de instalación),
   12.10.4.3 (factores de cama), 12.11, 12.12.3.x (empuje, pandeo, deformación, propiedades a largo plazo); AASHTO M 170M Tablas 1–5
   (D-load por clase: el implementador declaró «ilegibles» las de las Clases I, III, IV y V — COMPRUÉBALO renderizando las páginas;
   si se pueden leer, es un hallazgo ALTO porque `clases_producto_por_relleno` quedaría cojo); ASTM A796 §7–§11; AASHTO M 36;
   M 294; EG-2013 505–508. Toda transcripción de tabla: valor a valor en una muestra amplia (todas las filas si son < 30).
2. **Coherencia ingenieril**: rehaz A MANO (aritmética escrita, independiente del código) un caso por material —concreto Ø 0.90,
   TMC, HDPE y marco— con las entradas del fixture (A-01: relleno real) y compáralo con lo que el código imprime; órdenes de
   magnitud; dirección del conservadurismo; que NO se mezclen γ/φ de LRFD con FS de ASD (A796) en una misma comprobación; que el
   «caso VARIOS» (D 0.90, H 0.30, DL 4.5 kPa, LL 86 kPa, C 40.7 kN/m, A 0.354 mm²/mm, FF 0.109) sea dorado de aritmética y esté
   rotulado «según el INFORME §1.1, páginas no verificadas».
3. **Ningún valor inventado ni relleno silencioso**: cada criterio nuevo ([A] con ventana y justificación que NO atribuya a la
   fuente lo que es elección; [C] con cita; vacío → `CriterioPendienteError`). En particular los valores por defecto que el
   implementador eligió y el dueño debe confirmar: `fabricacion_tmc` (remachada simple), tipo de instalación (Tipo 3), η = 1.05,
   relleno/compactación (Cl-95 o como se llame). ¿Son el más desfavorable admisible? ¿la ventana es real? ¿qué mueve cada alternativa?
4. **Nivel de entrega y PARADA (c)**: el implementador hizo que `F8.*` corra también a nivel de perfil. Comprueba `Criterio.nivel`
   de cada criterio nuevo contra `tests/test_nivel_medido.py` / `test_cierre_perfil.py`; y mide con el comparador de E-B
   (`cli.py --comparar` o `src/comparador.py`) las corridas de la línea base (`tests/linea_base_familia_c/`, `tests/ejemplo_puntos.csv`
   a perfil y a expediente, con y sin los datos externos del fixture) en `7fb7926` (usa `git worktree add --detach /tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud/base 7fb7926`)
   frente a `ab7fc3a`: **material, diámetro/sección, veredictos y bloqueos** por punto. Cualquier diámetro, material o «dimensionado»
   que se mueva es BLOQUEANTE. Di explícitamente «diámetros movidos: ninguno» o la lista.
5. **Robustez**: guardias de segunda línea en las públicas de M8 (signo, NaN, finitud; forma MAT-D13); toda excepción nueva
   desciende de `ErrorProyecto` y se captura como `Bloqueo` (ningún `AssertionError`/`KeyError`/`TypeError` alcanzable con entradas
   válidas: prueba H = 0, H muy grande, D fuera de tabla, HDPE 1350/1500 sin OD, concreto > 2.70 m, TMC sin plancha que cumpla,
   marco sin criterios del cajón); los avisos llegan a `InformePunto.avisos()` (CLI, JSON, memoria); consumidores de valores que
   ahora pueden ser `None` (CSV de resumen, M11, GUI).
6. **Tests**: ¿los dorados están calculados a mano o repiten la fórmula del código? ¿hay tests vacuos (pasan con el código roto)?
   Corre el arnés de mutación de EXT-11 (`tests/apoyo/mutacion.py`) sobre las funciones nuevas de `src/modulos/M8_estructural.py`
   (acótalo en tiempo: ~20 min) y lista los mutantes vivos que importen.
7. **Residuos declarados**: costura empernada, flexión/deformación combinada del HDPE (12.12.3.10.2b), «la plancha elegida no vuelve
   a 7.A/V7» (ficha T5-03), D-load ilegible: ¿cada uno tiene ficha en `docs/decisiones_diferidas.md` con símbolo, y la memoria lo
   dice sin vender como verificado lo que no lo está? ¿`verificacion_diferida_estructural` imprime sólo lo que sigue diferido?
   ¿quedan `AssertionError("inalcanzable")` en M8?
8. Lo que tú veas: docstrings falsos, fuente/interpretación/lo-que-el-proyecto-hace pegados, verbos de obligación sin cita con ese carácter.

## Entrega

Escribe el informe en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/AUDITORIA_T-5_opus.md`: veredicto (APROBADO / AJUSTADO / RECHAZADO), y hallazgos numerados H1… cada uno con
severidad (BLOQUEANTE / ALTA / MEDIA / BAJA), evidencia reproducible (comando y salida, o página y texto literal), y la corrección
que propones (concreta, anclada por símbolo). Separa «refutado con evidencia» de «sospecha no comprobada». Lista aparte las
decisiones que son del dueño. Devuélveme sólo un resumen de menos de 300 palabras: veredicto, nº de hallazgos por severidad, los
tres más graves, «diámetros movidos», y decisiones para el dueño.
