# Prompt para revisar VE-2 con Fable desde otra cuenta

Copia el bloque `text` entero en una sesión nueva de Claude Code (modelo Fable) con acceso
al repositorio `Andy-rba30/Proyecto_alcantarillas`.

```text
Eres el REVISOR INDEPENDIENTE y adversarial de la etapa VE-2 del repositorio Andy-rba30/Proyecto_alcantarillas (software peruano de diseño de alcantarillas). No recibes las conclusiones de quienes lo implementaron: juzgas el código, los tests y la norma.

0. Prepara el entorno:
   - git clone del repositorio y git fetch origin claude/elegant-rubin-4ax72s main.
   - apt-get install -y python3-tk xvfb; usa python3.12 (si el python por defecto no trae tkinter) con: pip install -r requirements.txt PyMuPDF "pillow<13".
   - git clone https://github.com/Andy-rba30/Normas.git y export NORMAS_DIR=<ese clon>. Lee PDF con: python -m src.normativa.extraccion buscar|texto|png <fragmento> ... (hif12026 = HDS-5 3.ª ed., hec14, Hidro = Manual de Hidrología MTC, Puentes = Manual de Puentes, LRFD = AASHTO LRFD 9.ª, 170M, 294, "M 36", A760).
   - Lee enteros CLAUDE.md, proceso/reglas_de_correccion_de_auditorias.md y el bloque «### VE-2» de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md (es el encargo: hallazgos de la revisión normativa y el prompt). Lee proceso/planes_mejora/ve2_estado/LEEME.md.

1. Ubica lo que se revisa. En la rama claude/elegant-rubin-4ax72s busca el commit de integración de VE-2 (mensaje que empieza por «validacion(VE-2): integración»). Si EXISTE, revisa el diff 72a8d01..<ese commit> (más sus commits validacion(VE-2.n) intermedios). Si NO existe, la sesión que integraba se cortó: los cambios están como parches en proceso/planes_mejora/ve2_estado/ (*.commit.patch = terminados, aplícalos con git am sobre 72a8d01 en una rama tuya; *.wip.patch = a medias, NO se revisan como terminados: dilo en el informe). No integres en main.

2. Revisa en este orden (lo más crítico primero) y busca defectos REALES con evidencia reproducible:
   a) (b) velocidad de erosión, M3.resolver_manning y sus consumidores (M4 V_salida y y_salida, M5 V3, M6 Laushey/HEC-14/Froude, M9, M11). Recalcula a mano con un script tuyo el caso UPAO ALC46 (Q = 0.317 m³/s, S = 0.10, D = 0.90 m, concreto, n 0.010 / 0.013: se espera ~5.81 m/s y Ø 0.90 m) y el punto A-01 de la línea base; comprueba continuidad Q = V·A con el tirante de n mínimo, convergencia y el control de salida (HDS-5 3.1.6, 3.3.2; HEC-14 3.2.2).
   b) Cambios a tests y fixtures existentes hechos para que la suite quede verde: ¿alguno tapa un defecto? Mira en particular la variante `caudal_calculado` del juego de T-11 (se vació el caudal del evento extremo porque V8 lo rechazaba en B-01) y el cambio de S 0.012 → 0.015 en test_t4 (caso G2).
   c) (f) racional modificado en MH_hidrologia: cada ecuación (29) a (35) del Manual núm. 3.12.2.1, págs. impresas 50-52, contra la IMAGEN de la pág. 52 (png); límites 10 ≤ A < 770 km² y 0.25 ≤ Tc ≤ 24 h; recalcula a mano una cuenca de 55.9 km². (d) factor_intervalo_fijo_p24 = 1.00 de archivo, ventana 1.00-1.13, dónde se aplica. (e) aviso de consistencia sin umbral.
   d) (c2) nivel de agua de diseño de V7 como criterio [A] (Manual de Puentes 2.4.3.8.1; AASHTO LRFD 12.6.1 y 3.7.2; γ' por analogía 2.4.4.1.3) y (c1) su justificación. (g) diámetros designados por norma de producto: la tabla de AASHTO M 170M se transcribió desde una imagen con errores de OCR y se corrigieron nueve celdas (discrepancia DIS-M170M-T6-RECOMPOSICION): verifícalas contra el PDF celda por celda; el diámetro inglés convertido sólo para concreto. (a) columna_n_manning_concreto.
   e) Integración: recuentos de criterios coherentes en código, tests y CLAUDE.md; línea base: todo número movido tiene como causa (b) y ningún diámetro sube; documentos generados en sincronía (sus tests); ninguna cita sin verificar contra el PDF; ningún criterio sin nivel, forma, sensibilidad o resolución; ningún valor rellenado en silencio (regla de CLAUDE.md); literales sin `# literal-ok`, tolerancias sin nombre, floats con ==, excepciones fuera de ErrorProyecto.
   f) Corre la suite completa en un clon limpio fuera del repositorio (no en un checkout con worktrees dentro): xvfb-run -a python -m pytest -q -p no:cacheprovider --no-header. Anota passed / skipped / collected.

3. NO corrijas nada. Entrega un informe en español en proceso/planes_mejora/ve2_estado/REVISION_FABLE.md (commit en una rama tuya `revision/ve2-fable` y push de esa rama), con: hallazgos por severidad (bloqueante / alta / media / baja), cada uno con archivo:línea, evidencia (comando y salida, o cálculo) y corrección sugerida; lo verificado que está bien; el par de la suite; y un veredicto: integrar en main / integrar con correcciones / no integrar.
```
