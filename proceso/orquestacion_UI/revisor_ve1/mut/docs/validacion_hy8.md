# Validación con HY-8: procedimiento para que el autor lo corra (T-11)

> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe `python -m tests.apoyo.validacion_externa --escribir` y `tests/test_t11_validacion_externa.py` lo regenera y lo compara. **HY-8 no está en el entorno de la cadena T y este documento NO afirma ningún resultado de HY-8**: dice qué entradas de cada punto hay que cargar, qué salida comparar y con qué tolerancia. Las entradas son las de la corrida del juego de la validación integral, que son **DATOS DE PRUEBA, NO DEL PROYECTO** (`tests/fixtures/juego_validacion_integral.py`).

## 1. Qué se valida y qué no

HY-8 es el programa de la FHWA para el análisis hidráulico de alcantarillas, que implementa los procedimientos del HDS-5. La comparación valida la **hidráulica del conducto** de cada punto dimensionado: la carga a la entrada con control de entrada, la carga con control de salida, cuál gobierna, HW/D, los tirantes normal y crítico, y la velocidad a la salida donde los dos programas la sacan del mismo modo (§5, regla 4). No valida nada de lo que HY-8 no calcula: la clasificación, el TR, la Fase 8, el cabezal, la protección, la Fase 10, ni las verificaciones V1 a V10 como veredictos.

## 2. Las convenciones del programa que hay que reproducir

- **Doble n (hoja de ruta §4.1).** El programa calcula la carga, los tirantes y el control con el n **máximo** del material (la estimación alta de la pérdida). En HY-8 cada barril se corre con el n que se le carga: la corrida que se compara con veredicto es la de **n máximo** (el «Tirante normal» de §4 está calculado con él). La velocidad de erosión del programa usa el n **mínimo** sobre ese mismo tirante (§5, regla 4): una segunda corrida de HY-8 con n mínimo es opcional e informativa.
- **El TW es un tirante sobre el fondo de la salida**, no una cota: en HY-8 se carga como cota de agua constante del receptor = cota de salida + TW.
- **El cabezal es normal al eje del conducto** (alcance declarado): no se declara esviaje de la embocadura en HY-8; el esviaje del cruce ya está en la longitud del conducto.
- **Longitud.** El programa calcula la longitud por extremo (7.B) sobre el eje del barril; la proyección horizontal es más corta en 1 − 1/√(1 + S²) ≈ S²/2, que §3 da por punto (del orden de milésimas de por ciento). Cargar en HY-8 la estación de salida igual a la longitud y las dos cotas de fondo de la tabla.
- **Roadway Data.** HY-8 la exige: perfil de cota constante, **cota de la cresta = la rasante del punto** y **ancho = el de la plataforma** (§3); la longitud de la cresta es la del tramo de vía sobre el cauce, que no es dato del programa (cualquiera vale si no hay desborde). Con los caudales de diseño **no debe haber desborde** (en el programa V5 y V8 lo exigen); si HY-8 reporta caudal sobre la vía, la corrida no es comparable y se dice.

## 3. Entradas por punto (corrida del juego, `--alcance expediente`)

| Punto | Fam. | Sección | Material | n mín. / máx. | Embocadura (HDS-5 Tabla A.1) | ke | Barriles | Q (m³/s) | Longitud (m) y su diferencia con la horizontal | Pendiente (m/m) | Cota de fondo entrada / salida (msnm) | TW (m) y cota del receptor (msnm) | Roadway Data: cota de cresta (msnm) / ancho (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-01 | A | Ø 0.90 m | Concreto reforzado | 0.01 / 0.013 | Chart 1, scale 1: Circular Concrete, Square edge w/headwall (`circular_concreto_square_edge_headwall`; K 0.0098, M 2.0, c 0.0398, Y 0.67, Forma 1) | 0.5 | 1 | 1.167 | 18.467 (0.0018%) | 0.0060 | 42.100 / 41.989 | 0.300 → 42.289 | 44.200 / 9.60 |
| A-02 | A | Ø 0.90 m | Concreto reforzado | 0.01 / 0.013 | Chart 1, scale 1: Circular Concrete, Square edge w/headwall (`circular_concreto_square_edge_headwall`; K 0.0098, M 2.0, c 0.0398, Y 0.67, Forma 1) | 0.5 | 1 | 0.480 | 18.176 (0.0032%) | 0.0080 | 39.850 / 39.705 | 0.300 → 40.005 | 42.000 / 9.60 |
| B-01 | B | Ø 0.90 m | Concreto reforzado | 0.01 / 0.013 | Chart 1, scale 1: Circular Concrete, Square edge w/headwall (`circular_concreto_square_edge_headwall`; K 0.0098, M 2.0, c 0.0398, Y 0.67, Forma 1) | 0.5 | 1 | 0.095 | 18.384 (0.0050%) | 0.0100 | 38.400 / 38.216 | 0.300 → 38.516 | 40.600 / 9.60 |
| C-01 | C | marco 1.20 × 0.90 m | Concreto reforzado | 0.012 / 0.015 | Chart 8, scale 1: Rect. Box Concrete, 30° to 75° wingwall flares (`cajon_concreto_aletas_30_75`; K 0.026, M 1.0, c 0.0347, Y 0.81, Forma 1) | 0.4 | 1 | 0.850 | 20.997 (0.0008%) | 0.0040 | 36.900 / 36.816 | 0.410 → 37.226 | 39.100 / 9.60 |

## 4. Salidas del programa que hay que comparar

Las cargas son alturas sobre el fondo de la entrada (HW), en metros. En HY-8, «headwater elevation» menos la cota de fondo de la entrada. HW/D es la carga entre la ALTURA interior del conducto: el D del tubo o la altura de la celda del marco. El tirante normal es el de **n máximo**.

| Punto | Altura D (m) | HW control de entrada (m) · HW/D | HW control de salida (m) · HW/D | HW que gobierna (m) · HW/D | Control | Tirante normal, n máx. (m) | Tirante crítico (m) | Velocidad a la salida (m/s) | Cómo sale la velocidad | ¿Lleva veredicto? | Régimen del barril |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-01 | 0.900 | 1.042 · 1.158 | 0.993 · 1.104 | 1.042 · 1.158 | entrada | 0.627 | 0.640 | 3.206 | control de entrada: V_erosión = (1/n_mín)·R^(2/3)·S^(1/2) sobre el tirante normal de n_máx (regla de doble n de la v8 §4.1, `M3.resolver_manning`; V·A ≠ Q por diseño), la estimación alta para V3 y el d50. No es la velocidad de un perfil: HY-8 la saca del perfil supercrítico del barril | no | parcialmente lleno |
| A-02 | 0.900 | 0.572 · 0.636 | no se forma: el perfil S1 no alcanza la entrada (la aproximación descartada da 0.562) | 0.572 · 0.636 | entrada | 0.336 | 0.403 | 2.883 | control de entrada: V_erosión = (1/n_mín)·R^(2/3)·S^(1/2) sobre el tirante normal de n_máx (regla de doble n de la v8 §4.1, `M3.resolver_manning`; V·A ≠ Q por diseño), la estimación alta para V3 y el d50. No es la velocidad de un perfil: HY-8 la saca del perfil supercrítico del barril | no | parcialmente lleno |
| B-01 | 0.900 | 0.232 · 0.258 | no se forma: el perfil S1 no alcanza la entrada (la aproximación descartada da 0.356) | 0.232 · 0.258 | entrada | 0.140 | 0.175 | 1.956 | control de entrada: V_erosión = (1/n_mín)·R^(2/3)·S^(1/2) sobre el tirante normal de n_máx (regla de doble n de la v8 §4.1, `M3.resolver_manning`; V·A ≠ Q por diseño), la estimación alta para V3 y el d50. No es la velocidad de un perfil: HY-8 la saca del perfil supercrítico del barril | no | parcialmente lleno |
| C-01 | 0.900 | 0.590 · 0.656 | 0.623 (remanso, perfil M2) · 0.692 | 0.623 · 0.692 | salida | 0.425 | 0.371 | 1.728 | control de salida: Q/A en la sección de salida con el tirante y_salida = 0.410 m (HDS-5 3.1.6; el perfil de la lámina arranca ahí), sin n: la misma magnitud que HY-8 da en la salida | sí | parcialmente lleno |

## 5. Tolerancia de la comparación: criterio del proyecto, NO normativo (aceptado por el dueño el 2026-11-13)

Ninguna norma fija estas cifras. Son un **criterio del proyecto**, propuesto por T-11 y aceptado por el dueño, coherente con la tolerancia de lectura del 3% con que se juzgan los ejemplos publicados del HDS-5 (`docs/validacion_hds5.md`). La diferencia se mide contra el programa (HY-8 / programa − 1), con dos decimales.

1. **Hasta 3%**: coincidencia. Entre 3% y 10%: diferencia que hay que **explicar** con su causa antes de darla por buena (la forma de la ecuación de control de entrada, la regla del HDS-5 núm. 3.3.3 para la carga de salida entre 0.75 D y 1.2 D, el perfil de la lámina, la entrada sumergida o no). **Más de 10%** —el ±10 % en carga que el HDS-5 declara para su propio procedimiento, pág. impresa 3.1, PDF 83—: **discrepancia** que se investiga y se reporta contra el programa con el caso.
2. La regla se aplica a **HW y a HW/D** (las dos columnas de §4).
3. Si el **tipo de control** (entrada o salida) de HY-8 no es el del programa, el punto va a **«explicar» sea cual sea el porcentaje**: las cargas salen de ecuaciones distintas.
4. La **velocidad de salida** se informa **sin veredicto** donde el programa no la saca del mismo modo que HY-8 (columna «¿Lleva veredicto?» de §4): bajo control de entrada el programa da la estimación alta de la regla de doble n y HY-8 la del perfil del barril. Donde sí lleva veredicto (control de salida, sección de salida con el mismo tirante) se juzga con las bandas de la regla 1, por la misma razón que HW: lectura de T-11 sobre la decisión del dueño, que nombra HW y HW/D.
5. La **versión de HY-8** y la **fecha de la corrida** son campo obligatorio del encabezado de cada tabla de §6: sin ellas la tabla no vale.

## 6. Cómo dejar escrito el resultado

Una tabla por punto, con este encabezado y estas filas; las columnas de HY-8, la diferencia y el juicio las llena el autor. Si un número del programa cambia, este documento cambia con él: la comparación vale para el commit cuyo sello lleve.

### A-01 — versión de HY-8: ______ · fecha de la corrida: ______ (obligatorios)

| Magnitud | Programa | HY-8 | Diferencia (%) | Juicio (§5) |
|---|---|---|---|---|
| HW que gobierna (m) | 1.042 | | | |
| HW/D que gobierna | 1.158 | | | |
| Control | entrada | | | |
| HW control de entrada (m) | 1.042 | | | |
| HW control de salida (m) | 0.993 | | | |
| Velocidad a la salida (m/s) — sin veredicto | 3.206 | | | |

### A-02 — versión de HY-8: ______ · fecha de la corrida: ______ (obligatorios)

| Magnitud | Programa | HY-8 | Diferencia (%) | Juicio (§5) |
|---|---|---|---|---|
| HW que gobierna (m) | 0.572 | | | |
| HW/D que gobierna | 0.636 | | | |
| Control | entrada | | | |
| HW control de entrada (m) | 0.572 | | | |
| HW control de salida (m) | no se forma | | | |
| Velocidad a la salida (m/s) — sin veredicto | 2.883 | | | |

### B-01 — versión de HY-8: ______ · fecha de la corrida: ______ (obligatorios)

| Magnitud | Programa | HY-8 | Diferencia (%) | Juicio (§5) |
|---|---|---|---|---|
| HW que gobierna (m) | 0.232 | | | |
| HW/D que gobierna | 0.258 | | | |
| Control | entrada | | | |
| HW control de entrada (m) | 0.232 | | | |
| HW control de salida (m) | no se forma | | | |
| Velocidad a la salida (m/s) — sin veredicto | 1.956 | | | |

### C-01 — versión de HY-8: ______ · fecha de la corrida: ______ (obligatorios)

| Magnitud | Programa | HY-8 | Diferencia (%) | Juicio (§5) |
|---|---|---|---|---|
| HW que gobierna (m) | 0.623 | | | |
| HW/D que gobierna | 0.692 | | | |
| Control | salida | | | |
| HW control de entrada (m) | 0.590 | | | |
| HW control de salida (m) | 0.623 | | | |
| Velocidad a la salida (m/s) | 1.728 | | | |

