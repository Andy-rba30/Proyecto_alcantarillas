# Revisión independiente de VE-1 (5f04170 frente a 0bf1cc2)

Veredicto: el cambio hace lo que el encargo pide y no encontré ningún defecto que lo bloquee. Quedan cinco observaciones, ninguna ALTA; las dos primeras ya las declara la ficha VE1-01 como abiertas.

## Lo que está bien (comprobado)

1. **D1, serie tal cual: bien.** En proceso, con los tres materiales: 0.9144/0.1524 → 0.9144, 1.0668, 1.2192, 1.3716 … 2.5908; 0.90+0.075; 0.90+0.125; 0.914+0.152; pasos de 4 a 6 decimales (0.0254, 0.123456, 0.150001, 1e-5). Ningún escalón sale con ruido flotante, salvo cuando el propio número declarado lo trae (1/3, o 6*0.0254 = 0.15239999999999998).
2. **D1 por la CLI: bien.** Con la reproducción de `/tmp/validacion_web/defectos/D1_progresion_redondeo`, 0bf1cc2 da rc=1 y «no pertenece a la progresion … (valor leido: 1.07)» en los tres materiales; 5f04170 da rc=0 y dimensiona con D = 1.2192 (V9 `valor_obtenido` 1.2192, `apron_hec14/D_m` 1.2192). Funciona también declarando sólo la fila de espesor 1067, sin la 1070.
3. **Línea base: idéntica.** Corrí `regenerar.sh` en dos copias fuera del checkout (árbol de 5f04170 y el mismo árbol con `M2_material.py` y `variables_entrada.py` de 0bf1cc2). Los 16 archivos son iguales byte a byte entre sí y a los comprometidos.
4. **Guardia de pertenencia: sigue rechazando.** Con 0.90/0.15 rechaza 1.0, 1.07, 0.75 y 1.05+2e-9; con la serie de 6 in rechaza 1.07, 1.05 y 1.22, y acepta 1.0668000000000002 → 1.2192.
5. **Cajones y otros consumidores: sin cambio.** `_siguiente_seccion_cajon` no se tocó y `memoria_punto_cajon.html` sale idéntica.
6. **Literales y tolerancias: bien.** `_escalon_de_la_serie` (`src/modulos/M2_material.py:989`) no introduce ningún literal ni tolerancia; `tests/test_sin_literales.py` pasa. El `from decimal import Decimal` es local a la función (línea 1021) y es de la biblioteca estándar.
7. **D2: bien.** En el código, `NF_profundidad_m` lo leen `M8_estructural.py:1721` (TMC) y `:2260` (HDPE), con `H_w = max(agua hasta la clave, (cota_terreno − NF) − centro)` sólo si `nf is not None`, y M9 (`M9_cabezal.py:6494-6512`, `:8386`). `M8.empuje_flotacion_kn_m` (`:304`) y `M5.v7_flotacion` no lo leen, y M5 y M8 no tienen diff. En la reproducción O2, U = 1.2745119340799116 es idéntico con NF a 10 m y sin NF. El contrato (`docs/contrato_entradas.md:71`) y el concepto (`src/variables_entrada.py:787-800`) dicen eso mismo.
8. **D3, hoja de ruta: no se editó** (`git diff` vacío sobre `docs/hoja_de_ruta_alcantarillas_v8.md`). Las líneas 223 («la lee V7») y 557 («**Regla [N]:**») siguen ahí, y el centinela `test_d3_centinela_la_hoja_de_ruta_sigue_sin_corregir` las vigila.
9. **Citas al PDF: correctas** (leídas con `python -m src.normativa.extraccion`):
   - Manual de Puentes núm. 2.4.3.8.2, PDF 114, pág. impresa 113 según el índice: «…que actúa sobre todos los componentes de la estructura que se encuentran debajo del nivel de agua de diseño».
   - Manual de Hidrología núm. 4.1.1.3.6, PDF 77, pág. impresa 74: «n : Coeficiente de Manning (Ver Tabla Nº 09)».
   - Tabla Nº 09, PDF 78, pág. impresa 75: columnas MÍNIMO, NORMAL y MÁXIMO.
   - La corrección de VE1-02 (e) es cierta: «se debe evaluar … la consistencia de los datos registrados» está en el núm. 3.3 «Estudios de Campo» (pág. impresa 21); el 3.4 empieza después y es el que dice «primordial».
10. **Fichas.** VE1-01 dice lo cierto, y su recuento de tests cuadra (12 + 1 + 4 + 1 = 18, los 18 pasan). VE1-02 recoge las siete decisiones (a) a (g) sin tomar ninguna. Los números que pude cotejar con `INFORME_REVISION.md` coinciden: +5 a +8 %, +21.5 a +23 %, 6.28 frente a 5.81, 0.90 → 1.35 m, −11.5 %, 729 mm y 579 mm/h, 55.9 km², 770 km², y 1.2745 kN/m.
11. **Los tests no son tautológicos** (mutantes sobre una copia, `test_ve1_validacion.py` + `test_linea_base.py`):
    - `round(inicio + (n+1)*paso, 2)`: caen 9 — serie de 6 in ×3, pasos 0.075 y 0.125, tres y cinco decimales, y los dos de punta a punta.
    - `inicio + (n+1)*paso` sin redondeo: caen 6 — serie de 6 in en concreto y TMC, paso 0.075, la guardia de la progresión por defecto y los dos de `test_linea_base.py`.
    - `round(…, 4)`: cae 1, el de cinco decimales.
12. **Permisos.** En `src/` sólo cambian el escalón de M2 (docstring y función auxiliar) y el concepto de `NF_profundidad_m`. No se tocaron `criterios_adoptados.py`, `constantes_normativas.py`, `datos_sitio.py` ni la hoja de ruta. Los 54 archivos de test que mencionan las piezas tocadas, más `test_sin_literales.py`, pasan sobre la copia.

## Hallazgos

**H1 · MEDIA con una serie no centesimal, nula con la de archivo · CONFIRMADO · `src/modelos.py:1456`.** `SeccionCircular.etiqueta` es `f"Ø {self.D:.2f} m"`. Con la serie de 6 in por la CLI, el JSON trae `iteraciones[1].seccion = "Ø 1.07 m"` y el motivo «Ø 1.07 m: incumple V1», y el diseño sale «Ø 1.22 m» en la consola, en la memoria HTML y en el CSV de resumen. En la memoria «1.0668» no aparece nunca y «1.2192» una sola vez. El cálculo ya es correcto, pero el lector sigue viendo el «1.07 que nadie declaró», que era el síntoma de D1, y el resumen entrega un diámetro que no está en la serie. VE1-01 lo declara abierto y fuera de permiso, y es cierto; conviene cerrarlo antes de que alguien use la serie de 6 in en una entrega, o tomar VE1-02 (g).

**H2 · MEDIA, anterior a VE-1 e idéntico en 0bf1cc2 · CONFIRMADO · `src/modulos/M2_material.py:974`** (`pasos = (D - inicio) / paso`) y la puerta de `diametros_normalizados`. Por la CLI con `--declarar` sobre el punto de la reproducción, en los dos commits:
- `{"inicio": 0.9, "paso": 0}` → traza `ZeroDivisionError: float division by zero`.
- `{"inicio": 0.9, "paso": "0.15"}` → `TypeError: unsupported operand type(s) for /: 'float' and 'str'`.
- `{"inicio": "0.9", "paso": 0.15}` → `TypeError: '>' not supported between instances of 'str' and 'int'`, en M3 (`exigir_dimensiones_positivas`).
- `{"inicio": 0.9}` → `KeyError: 'paso'`.

Las cuatro están fuera de `ErrorProyecto` y tumban la corrida. VE1-01 sólo nombra las dos primeras: **faltan el inicio de texto y el campo ausente**. Además, `paso: True` se acepta y recorre 0.90 → 1.90. VE-1 no lo empeora.

**H3 · BAJA · CONFIRMADO · regla de tres partes, D3 (2).** La discrepancia de la «Regla [N]» de la doble n sólo está en la ficha VE1-01 y en el docstring del test. No hay declaración en ningún punto de uso: `M3_hidraulica.py:38` («Regla de doble n (Sec. 4.1)») y el docstring Sec. 3.4 de M2 siguen sin ella. La ficha lo justifica por permiso, y es cierto que el código no imprime la etiqueta [N] (la memoria la saca como `nota_del_proyecto`), así que nadie lee «norma» en la salida. Las partes 2 y 3 de la regla están cumplidas; la 1 sólo para «la lee V7». Queda para el prompt que tome VE1-02 (a).

**H4 · BAJA · CONFIRMADO · alcance del diff.** Se tocaron dos archivos fuera de la lista literal de permisos: `tests/linea_base_familia_c/README.md` (+11) y `proceso/bitacora_conteos_y_entorno.md` (+50). Los dos son anotaciones del ritual de cierre, sin efecto en resultados. Lo dejo dicho, no lo considero defecto.

**H5 · BAJA · detalles de las fichas y del texto.**
- VE1-02 (g) no lleva «número medido», que el encargo pedía para cada decisión.
- El «Dónde vive» de VE1-02 apunta a `M3_hidraulica.py::resolver_manning`, que sólo representa a (b).
- El concepto de `NF_profundidad_m` (el texto del pre-vuelo y de la ayuda) lleva ahora una referencia de proceso («ficha VE1-01», «sigue sin corregir») y es bastante más largo. Es deliberado por la regla de tres partes, pero se verá en la pantalla.

## Qué no hice

No corrí la suite entera, por instrucción. No abrí la ventana real: la GUI no se tocó.

Material en `/tmp/revisor_ve1/`: `serie.py`; `lb_nuevo/` y `lb_base/` (líneas base regeneradas); `d1_base.txt` y `d1_nuevo.txt` con sus JSON; `d1.html` y `d1.csv`.
