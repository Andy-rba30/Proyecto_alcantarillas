# Segunda pasada de VE-1 (822091f frente a 0bf1cc2)

Veredicto: H1, H2, H3 y H5 están corregidos, D1-D3 siguen bien y la línea base sólo cambia en la huella de criterios. Quedan tres observaciones nuevas, todas BAJAS.

## Estado de los hallazgos

**H1 · CORREGIDO.** Con la serie de 6 in por la CLI (perfil, rc=0):
- JSON: `diseno.seccion = "Ø 1.2192 m"`; iteraciones «Ø 0.9144 m», «Ø 1.0668 m: incumple V1…», «Ø 1.2192 m».
- Consola: «Seccion : Ø 1.2192 m (interior)». CSV de resumen: `P1,Ø 1.2192 m`.
- Memoria HTML: «Ø 1.2192 m» ×5, «Ø 1.0668 m» ×2, «Ø 0.9144 m» ×2; memoria resumida: «Ø 1.2192 m» ×2. Ningún «Ø 1.07», «Ø 1.22» ni «Ø 0.91» en ninguna salida.
- Sin cambio: `SeccionCircular(0.9)` → «Ø 0.90 m»; `SeccionRectangular(1.2, 0.9)` → «marco 1.20 × 0.90 m»; (2.0, 1.5) → «marco 2.00 × 1.50 m».
- Valores raros en `texto_de_dimension`: 1/3 → «0.3333333333333333»; 0.15239999999999998 → «0.15239999999999998»; 1.7999999999999998 → igual; 1e-5 → «0.00001»; 1 → «1.00»; nan → «nan»; inf → «inf». No lanza excepción con ninguno.
- Mutante (volver a `:.2f`): caen 3 tests de `test_ve1_validacion.py`.

**H2 · CORREGIDO.** Por la CLI con `--declarar`, los cuatro casos dan rc=2 con «No se pudo declarar el criterio: … no es una progresion que se pueda recorrer», sin traza: paso 0, paso de texto, inicio de texto y campo ausente. También se rechazan `paso: True`, `paso: -0.15` y un campo de más (`tope`).
- No rechaza lo que antes era válido: `inicio: 1` (entero) y `paso: 1` corren; `inicio: -0.9` sigue llegando a su `DatoInvalidoError` dentro de `ErrorProyecto` (la rama de error de la línea base, idéntica).
- Los 141 criterios cargan con su valor de archivo: el módulo importa y los 41 archivos de test que tocan `_verificar_criterio`, `diametros_normalizados`, `restaurar_sesion`, `etiqueta()`, manifiesto y trazabilidad dan 4034 passed.
- Mutantes: quitar la llamada a la guardia → caen 18 tests; aceptar paso 0 (`< 0` en vez de `not > 0`) → caen 2.

**H3 · CORREGIDO.** La discrepancia de la «Regla [N]» está declarada con su cita (núm. 4.1.1.3.6, pág. impresa 74, y Tabla Nº 09, pág. impresa 75) y con el «sigue mal mientras el dueño no la corrija» en el docstring de `src/modulos/M3_hidraulica.py` (bloque «DISCREPANCIA CON LA HOJA DE RUTA», tras la línea 42) y en el Sec. 3.4 de `M2_material.py`. La cita es la que verifiqué en la primera pasada.

**H5 · CORREGIDO.** El concepto de `NF_profundidad_m` quedó en tres frases; VE1-02 (g) lleva número (+0.3 % de diámetro, +0.6 % de área: 1.07 frente a 1.0668 da +0.30 % y +0.60 %, correcto); «Dónde vive» nombra un símbolo por decisión.

**H4** (archivos de ritual) no era defecto; sigue igual.

## Lo demás que pediste

- **Línea base: sólo `criterios_sha1`.** Regenerada en una copia fuera del checkout: los 16 archivos coinciden byte a byte con los comprometidos en 822091f. Frente a la de 0bf1cc2 difieren 8 archivos, una línea cada uno: la clave `criterios_sha1` en los 4 JSON y la celda de esa misma huella en las 4 memorias HTML. Ningún número.
- **Manifiesto coherente.** `docs/manifiesto_citas.md` cambia 5 líneas, todas referencias de línea movidas por los docstrings, y apuntan bien: `M3_hidraulica.py:164` es `NUMERAL_MANNING = "4.1"`; `M2_material.py:296` y `:297` son `NUMERAL_CATALOGO` y `NUMERAL_MATERIAL`. `trazabilidad.csv` sólo cambia el sello; sus tests de sincronía pasan. El par del sello (6739 passed, 10 skipped) coincide con la bitácora, pero no lo medí yo.
- **D1-D3 intactos.** La línea del escalón de M2 no cambió respecto de 5f04170 (sólo docstrings); la fila del contrato, M5 y M8 no tienen diff; la hoja de ruta sigue sin editar. `test_ve1_validacion.py` + `test_linea_base.py` + `test_sin_literales.py`: 119 passed.

## Hallazgos nuevos

**N1 · BAJA · CONFIRMADO · residuo de H1 fuera del rótulo.**
- Los pasos de la memoria siguen sustituyendo «D = 1.22 m» con D = 1.2192 (8 veces en la memoria de la corrida de 6 in). La ficha VE1-01 lo declara como abierto y fuera de permiso.
- No declarado: dos mensajes de la Fase 8 formatean el diámetro con dos decimales, `src/modulos/M8_estructural.py:1366` («el tubo de concreto de {D:.2f} m pide una D-load…») y `:2033` («el TMC de {D:.2f} m necesita la plancha…»). No los disparé; lo leo del código (PLAUSIBLE en la salida).

**N2 · BAJA · CONFIRMADO en proceso · `src/modelos.py::texto_de_dimension`.** Imprime todos los decimales del `repr`, así que una dimension que llegue con ruido flotante lo enseña: `SeccionRectangular(3*0.4, 0.9).etiqueta()` → «marco 1.2000000000000002 × 0.90 m». Con valores tecleados (la serie declarada, los pares del cajón) no ocurre; sólo si alguien declara un número calculado (p. ej. `6*0.0254`).

**N3 · BAJA · nota de estilo · `src/modelos.py::texto_de_dimension`.** El mínimo de dos decimales se toma de `CIFRAS_FACTOR`, una constante con otro significado (cifras de un factor). Hoy coincide; si alguien cambia las cifras de los factores, mueve los rótulos de sección.

## Qué no hice

No corrí la suite entera, por instrucción; corrí 44 archivos de test (4153 tests) sobre una copia. No abrí la ventana real. El checkout queda sin modificar.

Material en `/tmp/revisor_ve1/`: `INFORME_2.md`; `lb2/` (línea base regenerada); `e2.json`, `e2.html`, `e2r.html`, `e2.csv`, `e2.txt` (corrida de 6 in).
