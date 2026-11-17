# Ensayos de diseño del conducto — revisión independiente y adversarial

**Objeto.** Comprobar si la app de diseño de alcantarillas produce un **buen diseño del conducto** (Familias A y B), comparando cada resultado con un diseño **hecho a mano por el revisor y congelado antes de correr la app**.
**Versión ensayada.** Rama `claude/youthful-shannon-rjzmuc`, commit `d23aa74`, clon en `/home/user/ensayos_conducto` (el repositorio original no se tocó; `git status` limpio). Python `/home/user/venv312`, `NORMAS_DIR=/home/user/Normas`. Fecha: 2026-11-17.
**Alcance de las corridas.** `--alcance perfil` (el conducto se decide ahí: Fase 4, Fase 5 V1–V10 y, desde T-5, la Fase 8 del conducto). V5 y V8 quedan diferidas al expediente en todas las corridas y no se juzgan.
**Evidencia.** Todo en `/home/user/ensayos_conducto_casos/` (entradas, scripts, salidas de la app). Nada se escribió en el repositorio; no hay commit ni push.

---

## 0. Veredicto en una línea

**Sí, con reservas.** Dentro de sus criterios declarados, la app dimensiona el conducto **bien**: cada diseño cumple todas sus verificaciones, es el **mínimo** de su material, es **monótono** en caudal, pendiente, relleno y TW, y la hidráulica coincide con el diseño a mano **al milímetro** (HW, y/D, V2, V3 y L iguales con 3 decimales en los 33 casos comparables). Las reservas son de lógica de diseño, no de aritmética: (1) **sin la tabla de clases III–V del tubo de concreto no puede cerrar ningún tubo de concreto con más de ≈2.4 m de tierra sobre la clave** (13 de 57 corridas quedan sin diseño; en 11 de ellas la app ya había encontrado un TMC que cumple y no lo publica); (2) **V1 no aplica su propio criterio de borde libre bajo TW cuando gobierna el control de entrada** (acepta Ø 0.90 m con el barril a 0.80 m de agua aguas abajo del resalto); (3) el «no factible por rasante» **no entrega un delta utilizable**; (4) **V7 omite el peso propio del tubo**, contra la fórmula de la hoja de ruta, y eso cambia el material de concreto a TMC; (5) el criterio de archivo `borde_libre_bajo_tw_ahogante = no_cumple` **sobredimensiona hasta cuatro escalones**.

Hallazgos: **bloqueantes 0 · altos 1 · medios 4 · bajos 4** (§6).

---

## 1. Método y garantías de independencia

1. **Lectura previa**: `CLAUDE.md`, la hoja de ruta v8 (Fases 1–8, Anexo B), `docs/contrato_entradas.md`, el juego de `tests/fixtures/juego_validacion_integral.py` y la documentación interna de M2/M5/M7/MD **para saber qué verifica cada fase**. Para aprender el formato de entrada y de salida se corrió la app **sobre el juego del repositorio** (no sobre los escenarios de este ensayo).
2. **Escenarios** (`escenarios.py`): una sola fuente de entradas para el diseño a mano y para la app. 14 escenarios (12 de Familia A, 2 de Familia B) y 5 barridos de monotonía (43 variantes): 57 corridas.
3. **Diseño a mano** (`diseno_a_mano.py`): implementación propia, **sin importar `src/` ni llamar a la CLI** (solo `math` y `scipy.brentq`). Manning en sección circular (Manual MTC 4.1.1.3.6, doble n), control de entrada HDS-5 3.ª ed. Apéndice A (ecs. A.1 y A.3, Ku = 1.811, Ks = −0.5, Tabla A.1), control de salida HDS-5 3.3.3 con h_o = máx(TW, (yc + D)/2) y las tres condiciones de uso resueltas como manda la hoja (remanso por paso directo, HDS-5 pág. 3.12), Fase 5 con los criterios de `src/criterios_adoptados.py` transcritos a mano (y/D ≤ 0.75, V ≥ 0.25 m/s, 6.0 / 4.572 m/s, resguardo por CBR del Manual de Suelos 4.5.4, HW/D ≤ 1.5, 0 ≤ S ≤ 0.10, V7 con agua en la clave, topes 2.70/2.10/1.50 m), cobertura AASHTO Tabla 12.6.6.3-1 y longitud «por extremo». Orden de materiales del proyecto (concreto, TMC, HDPE; §3.4) y, en cada uno, el menor Ø que cumple todo.
4. **Congelado antes de la app**: `diseno_a_mano_CONGELADO_antes_de_la_app.json` (sha1 `78e3b82ea71e3ebd32c82d9b754cbedde1db0762`, escrito 20:15:18 UTC); la primera corrida de la app sobre un escenario es de 20:15:47 UTC. El único cambio de escenario hecho antes de congelar fue E13 (Q de 0.80 a 0.60 m³/s), porque con 0.80 el TW quedaba bajo el conjugado del tirante normal y el caso no discriminaba; está anotado en el propio archivo.
5. **Corridas de la app** (`generar_y_correr_app.py`): un CSV y un JSON de datos externos por escenario, `cli.py <csv> --alcance perfil --datos-externos <json> --json <salida>`. Variantes **post hoc**, rotuladas como del revisor: la tabla de clases completa declarada (`correr_con_clases.py`), la lectura `aviso` del borde libre (`correr_variante_aviso.py`), la rasante de E09 (`correr_e09_rasante.py`) y la monotonía local (`monotonia_local.py`).
6. **Comparación** (`comparar.py`, `informe_tablas.py`): solo lee los dos JSON.

**Convenciones comunes de los escenarios** (datos de prueba, no del proyecto): fondo de entrada **medido** = cota de terreno; paquete rasante − subrasante = 0.45 m; bombeo 2 %; ancho 9.60 m (14.40 m en E04); TW declarado (vía 1); `luz_m` 2.0 m; NF a 2.5 m; receptor 0.10 m bajo la salida; sin ensayos de durabilidad salvo donde se indica.

---

## 2. Matriz de escenarios

| Id | Fam. | Q (m³/s) | S | Relleno rasante−fondo (m) | CBR → resguardo (m) | TW (m) | Esviaje (°) | Ancho (m) | L por extremo (m) | Otros datos | Qué se busca |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E01 | A | 0.40 | 0.005 | 2.80 | 8 → 0.80 | 0.15 | 0 | 9.60 | 20.62 | — | Quebrada menor, caudal pequeño, relleno normal: deberia gobernar el diametro minimo de 0.90 m (concreto). |
| E02 | A | 1.20 | 0.010 | 3.20 | 15 → 0.80 | 0.30 | 0 | 9.60 | 22.47 | — | Quebrada media en pendiente moderada: control de entrada en la transicion (q* entre 3.5 y 4.0). |
| E03 | A | 2.50 | 0.006 | 4.00 | 12 → 0.80 | 0.40 | 15 | 9.60 | 26.43 | — | Quebrada importante con esviaje de 15 grados: V4b/V1 deberian sacar el diametro del minimo. |
| E04 | A | 2.00 | 0.002 | 3.80 | 10 → 0.80 | 0.70 | 0 | 14.40 | 29.14 | — | Pendiente suave, via de cuatro carriles (conducto largo) y TW alto: control de SALIDA. |
| E05 | A | 2.00 | 0.035 | 3.50 | 25 → 0.60 | 0.30 | 0 | 9.60 | 24.96 | pH=7.2, resistividad_ohm_cm=5000 | Pendiente fuerte: el concreto supera V3 (6 m/s) en todo diametro; deberia pasar a TMC (n mayor, 4.572 m/s). |
| E06 | A | 2.00 | 0.035 | 3.50 | 25 → 0.60 | 0.30 | 0 | 9.60 | 24.96 | pH=4.5, resistividad_ohm_cm=5000 | E05 con suelo acido (pH 4.5): TMC excluida por durabilidad; el HDPE (n_min 0.009) tampoco cumple V3. Caso SIN SOLUCION con los materiales del catalogo. |
| E07 | A | 0.60 | 0.004 | 3.50 | 6 → 0.80 | 1.00 | 0 | 9.60 | 23.40 | — | Receptor alto (dren con TW = 1.00 m) y caudal pequeño: el criterio de borde libre bajo TW ahogante gobierna. |
| E08 | A | 1.00 | 0.010 | 7.50 | 20 → 0.60 | 0.30 | 0 | 9.60 | 40.02 | — | Relleno alto (7.5 m): la hidraulica pide 0.90 m; lo estructural del concreto pide mas que la Clase II. |
| E09 | A | 1.50 | 0.005 | 1.85 | 5 → 1.00 | 0.30 | 0 | 9.60 | 16.78 | — | Relleno escaso y CBR bajo (resguardo 1.00 m): no cabe; deberia salir NO FACTIBLE con un delta de rasante. |
| E10 | A | 5.00 | 0.004 | 4.80 | 25 → 0.60 | 0.60 | 10 | 9.60 | 29.09 | — | Caudal alto (5 m3/s) en pendiente suave: diametro grande, posible control de salida. |
| E11 | B | 0.15 | 0.012 | 2.40 | 10 → 0.80 | 0.00 | 0 | 9.60 | 19.28 | S_cuneta=0.01, ancho_tributario_m=7.0, inicio_tramo_cuneta_km=4.85 | Alivio de cuneta, salida libre: 0.90 m concreto. |
| E12 | B | 0.12 | 0.004 | 3.00 | 10 → 0.80 | 0.95 | 0 | 9.60 | 21.39 | S_cuneta=0.01, ancho_tributario_m=7.0, inicio_tramo_cuneta_km=4.85 | Alivio que descarga a un dren con 0.95 m de agua: V1 pide D >= 1.35 y con ese D la velocidad (V2) cae; posible caso sin solucion. |
| E13 | A | 0.60 | 0.030 | 3.00 | 15 → 0.80 | 0.80 | 0 | 9.60 | 22.57 | — | Pendiente fuerte con TW alto (0.80 m, sobre el conjugado del tirante normal: resalto DENTRO del barril): control de ENTRADA con la salida casi ahogada. Prueba de coherencia de V1 con TW > 0.75 D. |
| E14 | A | 0.80 | 0.008 | 4.80 | 12 → 0.80 | 0.30 | 0 | 9.60 | 28.88 | pH=7.0, resistividad_ohm_cm=800; perfil HDPE de fabricante declarado | Relleno medio (4.8 m) con TMC excluida por resistividad (800 ohm-cm) y perfil de HDPE de fabricante declarado (valores de prueba >= minimos de la Tabla A12-11): camino al HDPE si el concreto se detiene en la Fase 8. |

**Barridos de monotonía** (sitio base: fondo 60.00, relleno 4.00 m, CBR 12, esviaje 0, ancho 9.60 m):

| Barrido | Variable | Valores | Fijos |
|---|---|---|---|
| MQ00–09 | Q (m³/s) | 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0 | S 0.006, TW 0.40 |
| MS00–07 | S (m/m) | 0.080, 0.040, 0.020, 0.010, 0.006, 0.004, 0.003, 0.002 | Q 2.0, TW 0.40 |
| MH00–05 | relleno rasante−fondo (m) | 2.6, 3.5, 4.5, 6.0, 8.0, 10.0 | Q 1.0, S 0.010, TW 0.30 |
| MT00–08 | TW (m) | 0, 0.3, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5 | Q 1.0, S 0.006 |
| MU00–09 | TW (m), pendiente fuerte | 0.3, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.89, 0.9, 1.0 | Q 0.6, S 0.030, sitio de E13 |

---

## 3. Diseño a mano frente al de la app

Columna «A MANO»: el diseño congelado. Columna «APP tal cual»: la corrida de la app sin tocar nada. Columna «con la tabla de clases completa»: la variante del revisor que declara por `--declarar` las D-load de 0.3 mm de ASTM C76M (II 50, III 65, IV 100, V 140 N/m/mm), solo para separar el vacío de datos de la lógica (§6, H1). La clase estructural de la columna «A MANO» se da corregida en §7, porque el diseño congelado la calculó con un peso específico equivocado (error del revisor, §8).

| Id | A MANO: material Ø (m) | control | HW (m) · HW/D | y/D (V1) | V2 · V3 (m/s) | APP tal cual | APP con la tabla de clases completa | Coincide |
|---|---|---|---|---|---|---|---|---|
| E01 | Concreto 0.90 | entrada | 0.515 · 0.572 | 0.384 | 1.78 · 2.15 | Concreto 0.90, entrada, HW 0.515 | Concreto 0.90, entrada, Clase II | sí |
| E02 | Concreto 0.90 | entrada | 1.066 · 1.185 | 0.595 | 3.04 · 3.72 | Concreto 0.90, entrada, HW 1.066 | (no se corrió: igual a la de la izquierda) | sí |
| E03 | Concreto 1.20 | entrada | 1.443 · 1.203 | 0.694 | 2.98 · 3.68 | Concreto 1.20, entrada, HW 1.443 | Concreto 1.20, entrada, Clase II | sí |
| E04 | Concreto 1.35 | salida | 1.191 · 0.882 | 0.640 | 2.07 · 2.45 | Concreto 1.35, salida, HW 1.191 | (no se corrió: igual a la de la izquierda) | sí |
| E05 | TMC 1.05 | entrada | 1.369 · 1.304 | 0.744 | 2.89 · 3.86 | TMC 1.05, entrada, HW 1.369 | (no se corrió: igual a la de la izquierda) | sí |
| E06 | SIN SOLUCIÓN | — | — | — | — | sin dimensionar: no factible | (no se corrió: igual a la de la izquierda) | sí |
| E07 | Concreto 1.35 | salida | 0.933 · 0.691 | 0.741 | 0.53 · 2.15 | Concreto 1.35, salida, HW 0.933 | (no se corrió: igual a la de la izquierda) | sí |
| E08 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase IV | sí con la tabla de clases (tal cual: bloqueado por dato) |
| E09 | SIN SOLUCIÓN (subir rasante 0.655 m: Concreto 1.20) | — | — | — | — | sin dimensionar: no factible | (no se corrió: igual a la de la izquierda) | sí |
| E10 | Concreto 1.65 | salida | 1.893 · 1.147 | 0.717 | 3.05 · 3.75 | sin dimensionar: falta clase > II (M 170M) | Concreto 1.65, salida, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| E11 | Concreto 0.90 | entrada | 0.295 · 0.328 | 0.186 | 1.84 · 2.21 | Concreto 0.90, entrada, HW 0.295 | (no se corrió: igual a la de la izquierda) | sí |
| E12 | SIN SOLUCIÓN | — | — | — | — | sin dimensionar: no factible | (no se corrió: igual a la de la izquierda) | sí |
| E13 | Concreto 1.20 | entrada | 0.558 · 0.465 | 0.667 | 3.69 · 4.44 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | **NO** |
| E14 | Concreto 0.90 | entrada | 0.792 · 0.880 | 0.497 | 2.54 · 3.08 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MQ00 | Concreto 0.90 | entrada | 0.587 · 0.652 | 0.413 | 2.02 · 2.44 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MQ01 | Concreto 0.90 | entrada | 0.928 · 1.031 | 0.624 | 2.39 · 2.93 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MQ02 | Concreto 1.05 | entrada | 1.098 · 1.046 | 0.622 | 2.65 · 3.24 | Concreto 1.05, entrada, HW 1.098 | (no se corrió: igual a la de la izquierda) | sí |
| MQ03 | Concreto 1.20 | entrada | 1.214 · 1.011 | 0.594 | 2.85 · 3.49 | Concreto 1.20, entrada, HW 1.214 | (no se corrió: igual a la de la izquierda) | sí |
| MQ04 | Concreto 1.20 | entrada | 1.443 · 1.203 | 0.694 | 2.98 · 3.68 | Concreto 1.20, entrada, HW 1.443 | (no se corrió: igual a la de la izquierda) | sí |
| MQ05 | Concreto 1.35 | entrada | 1.482 · 1.098 | 0.632 | 3.15 · 3.86 | Concreto 1.35, entrada, HW 1.482 | (no se corrió: igual a la de la izquierda) | sí |
| MQ06 | Concreto 1.35 | entrada | 1.685 · 1.248 | 0.706 | 3.24 · 4.00 | Concreto 1.35, entrada, HW 1.685 | (no se corrió: igual a la de la izquierda) | sí |
| MQ07 | Concreto 1.50 | entrada | 1.677 · 1.118 | 0.635 | 3.38 · 4.15 | Concreto 1.50, entrada, HW 1.677 | (no se corrió: igual a la de la izquierda) | sí |
| MQ08 | Concreto 1.50 | entrada | 1.853 · 1.235 | 0.690 | 3.46 · 4.26 | Concreto 1.50, entrada, HW 1.853 | (no se corrió: igual a la de la izquierda) | sí |
| MQ09 | Concreto 1.65 | entrada | 1.824 · 1.105 | 0.621 | 3.58 · 4.38 | Concreto 1.65, entrada, HW 1.824 | (no se corrió: igual a la de la izquierda) | sí |
| MS00 | SIN SOLUCIÓN | — | — | — | — | sin dimensionar: no factible | (no se corrió: igual a la de la izquierda) | sí |
| MS01 | TMC 1.05 | entrada | 1.367 · 1.302 | 0.705 | 3.07 · 4.07 | TMC 1.05, entrada, HW 1.367 | (no se corrió: igual a la de la izquierda) | sí |
| MS02 | Concreto 1.05 | entrada | 1.389 · 1.323 | 0.511 | 4.50 · 5.47 | Concreto 1.05, entrada, HW 1.389 | (no se corrió: igual a la de la izquierda) | sí |
| MS03 | Concreto 1.05 | entrada | 1.395 · 1.328 | 0.636 | 3.44 · 4.22 | Concreto 1.05, entrada, HW 1.395 | (no se corrió: igual a la de la izquierda) | sí |
| MS04 | Concreto 1.20 | entrada | 1.214 · 1.011 | 0.594 | 2.85 · 3.49 | Concreto 1.20, entrada, HW 1.214 | (no se corrió: igual a la de la izquierda) | sí |
| MS05 | Concreto 1.20 | salida | 1.272 · 1.060 | 0.681 | 2.44 · 2.99 | Concreto 1.20, salida, HW 1.272 | (no se corrió: igual a la de la izquierda) | sí |
| MS06 | Concreto 1.20 | salida | 1.267 · 1.055 | 0.726 | 2.28 · 2.67 | Concreto 1.20, salida, HW 1.267 | (no se corrió: igual a la de la izquierda) | sí |
| MS07 | Concreto 1.35 | salida | 1.190 · 0.882 | 0.636 | 2.08 · 2.45 | Concreto 1.35, salida, HW 1.190 | (no se corrió: igual a la de la izquierda) | sí |
| MH00 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | Concreto 0.90, entrada, HW 0.926 | Concreto 0.90, entrada, Clase II | sí |
| MH01 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | Concreto 0.90, entrada, HW 0.926 | Concreto 0.90, entrada, Clase II | sí |
| MH02 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MH03 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase IV | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MH04 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase V | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MH05 | Concreto 0.90 | entrada | 0.926 · 1.029 | 0.531 | 2.92 · 3.55 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase V | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MT00 | Concreto 0.90 | entrada | 0.928 · 1.031 | 0.624 | 2.39 · 2.93 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MT01 | Concreto 0.90 | entrada | 0.928 · 1.031 | 0.624 | 2.39 · 2.93 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MT02 | Concreto 0.90 | entrada | 0.928 · 1.031 | 0.624 | 2.39 · 2.93 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | sí con la tabla de clases (tal cual: bloqueado por dato) |
| MT03 | Concreto 1.05 | entrada | 0.831 · 0.791 | 0.667 | 2.41 · 2.92 | sin dimensionar: falta clase > II (M 170M) | Concreto 0.90, entrada, Clase III | **NO** |
| MT04 | Concreto 1.20 | salida | 0.840 · 0.700 | 0.667 | 1.25 · 2.90 | Concreto 1.20, salida, HW 0.840 | (no se corrió: igual a la de la izquierda) | sí |
| MT05 | Concreto 1.20 | salida | 0.882 · 0.735 | 0.750 | 1.10 · 2.90 | Concreto 1.20, salida, HW 0.882 | (no se corrió: igual a la de la izquierda) | sí |
| MT06 | Concreto 1.35 | salida | 0.929 · 0.688 | 0.741 | 0.88 · 2.87 | Concreto 1.35, salida, HW 0.929 | (no se corrió: igual a la de la izquierda) | sí |
| MT07 | Concreto 1.65 | salida | 1.083 · 0.656 | 0.727 | 0.60 · 2.81 | Concreto 1.65, salida, HW 1.083 | (no se corrió: igual a la de la izquierda) | sí |
| MT08 | TMC 2.10 | salida | 1.366 · 0.650 | 0.714 | 0.38 · 1.62 | TMC 2.10, salida, HW 1.366 | (no se corrió: igual a la de la izquierda) | sí |
| MU00 | Concreto 0.90 | entrada | 0.646 · 0.718 | 0.296 | 3.80 · 4.58 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | sí |
| MU01 | Concreto 0.90 | entrada | 0.646 · 0.718 | 0.296 | 3.80 · 4.58 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | sí |
| MU02 | Concreto 0.90 | entrada | 0.646 · 0.718 | 0.296 | 3.80 · 4.58 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | sí |
| MU03 | Concreto 0.90 | entrada | 0.646 · 0.718 | 0.296 | 3.80 · 4.58 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | sí |
| MU04 | Concreto 1.05 | entrada | 0.594 · 0.566 | 0.714 | 3.74 · 4.51 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | **NO** |
| MU05 | Concreto 1.20 | entrada | 0.558 · 0.465 | 0.667 | 3.69 · 4.44 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | **NO** |
| MU06 | Concreto 1.20 | entrada | 0.558 · 0.465 | 0.708 | 3.69 · 4.44 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | **NO** |
| MU07 | Concreto 1.20 | entrada | 0.558 · 0.465 | 0.742 | 3.69 · 4.44 | Concreto 0.90, entrada, HW 0.646 | (no se corrió: igual a la de la izquierda) | **NO** |
| MU08 | Concreto 1.20 | entrada | 0.558 · 0.465 | 0.750 | 3.69 · 4.44 | Concreto 1.05, entrada, HW 0.594 | (no se corrió: igual a la de la izquierda) | **NO** |
| MU09 | Concreto 1.35 | entrada | 0.531 · 0.393 | 0.741 | 3.64 · 4.37 | Concreto 1.05, entrada, HW 0.594 | (no se corrió: igual a la de la izquierda) | **NO** |

### 3.1 Coincidencia numérica de la hidráulica

En los **33 casos** en que la app y el revisor adoptan el mismo material y diámetro, **todas** las magnitudes coinciden con 3 decimales: longitud por extremo, HW de entrada, HW de salida (aproximación y remanso), control gobernante, y/D de V1, V2 y V3 (tabla completa: `comparacion.json`; ejemplos: E04 control de salida con el remanso mandando, HW 1.191 m en los dos; E10 con clases, salida, 1.893 m; MS05–MS07 control de salida; E05 TMC 1.369 m). Como el revisor implementó **los mismos métodos declarados** (ecuaciones HDS-5, recta de transición, reglas E-A del remanso), la coincidencia prueba que la app **programa bien su método**, no que el método esté validado por un tercero: eso lo hace `docs/validacion_hds5.md` contra los ejemplos DG-1 del HDS-5 (dentro del 3 %), que esta revisión no rehízo.

---

## 4. Las cuatro preguntas, escenario por escenario

| Id | (a) ¿Cumple todas sus verificaciones? | (b) ¿Es mínimo? (escalón inmediato menor del mismo material) | (c) ¿Monótono? (Q×1.25 · S×0.70 · relleno +1.5 m) | (d) ¿Coincide? |
|---|---|---|---|---|
| E01 | Sí, 15/15 | Sí: Ø 0.90 es el mínimo normativo | Sí · Sí · bloqueado por clase tal cual (con clases: Clase III) | Sí |
| E02 | Sí, 15/15 | Sí: mínimo normativo | Sí · Sí · bloqueado tal cual (con clases: III) | Sí |
| E03 | Sí, 15/15 | Sí: Ø 1.05 «no transporta Q en flujo libre» (a mano: V1 lleno y V4b, HW/D 1.70) | Sí (1.35) · Sí (1.35) · bloqueado tal cual (con clases: IV) | Sí |
| E04 | Sí, 15/15 | Sí: Ø 1.20 sin tirante normal (a mano: perfil M2 a y/D 0.769) | Sí (1.50) · Sí (1.50) · bloqueado tal cual (con clases: III) | Sí (salida, HW 1.191) |
| E05 | Sí, 17/17 (TMC) | Sí: TMC Ø 0.90 no transporta Q; concreto falla V3 en **todo** Ø (6.04 m/s aún en 2.70 m) | Sí (TMC 1.20) · Sí (pasa a concreto 1.05, mismo Ø) · Sí | Sí |
| E06 | — (sin diseño) | — | — | Sí: los dos sin solución (V3 en concreto y HDPE; TMC excluida por pH) |
| E07 | Sí, 15/15 | Sí: Ø 1.20 falla V1 (TW 1.00 / 1.20 = 0.833) | Sí · Sí · bloqueado tal cual (con clases: III) | Sí (ver H5: es el criterio el que lleva a 1.35) |
| E08 | Tal cual sin diseño (H1); con clases sí, 15/15 | Sí (Ø 0.90) | Con clases: Sí · Sí · Sí (IV → V) | Sí con clases |
| E09 | — (sin diseño) | — | — | En «sin solución» sí; **la app no da el delta de rasante** (H3); el revisor: +0.655 m con concreto Ø 1.20, comprobado con la app |
| E10 | Tal cual sin diseño (H1); con clases sí | Sí: Ø 1.50 sin tirante normal | Con clases: Sí (1.80) · Sí (1.80) · Sí (III → IV) | Sí con clases (salida, HW 1.893) |
| E11 | Sí, 15/15 + VB1/VB2 | Sí: mínimo normativo | Sí · Sí · Sí | Sí |
| E12 | — (sin diseño) | — | — | Sí: los dos sin solución (V2 en todo Ø); el titular de la app es engañoso (H6) |
| E13 | Sí **según sus reglas** | Sí según sus reglas | Sí · Sí · bloqueado tal cual (con clases: III) | **NO**: app Ø 0.90, revisor Ø 1.20 (H2) |
| E14 | Tal cual sin diseño (H1); con clases sí | Sí | Con clases: Sí · Sí · Sí (III → IV) | Sí con clases (el HDPE del camino alternativo no pasa la Fase 8 con el perfil de prueba) |

**Monotonía local** (`monotonia_local.json`): 57 perturbaciones; en **ninguna** baja la sección ni la clase; 6 quedan sin diseño tal cual porque el relleno extra pide Clase III (H1).

**Barridos** (app tal cual / app con clases / revisor):

| Barrido | App tal cual | App con la tabla de clases | Revisor | Juicio |
|---|---|---|---|---|
| MQ (Q ↑) | — — 1.05 1.20 1.20 1.35 1.35 1.50 1.50 1.65 | 0.90(III) 0.90(III) 1.05 … 1.65 | 0.90 0.90 1.05 1.20 1.20 1.35 1.35 1.50 1.50 1.65 | Monótono. Tal cual, **más caudal da diseño y menos caudal no** (Q 0.5 y 1.0 bloqueados por la clase, Q 1.5 dimensiona: el Ø mayor pide menos D-load) |
| MS (S ↓) | sin sol., TMC 1.05, C 1.05, C 1.05, C 1.20, C 1.20, C 1.20, C 1.35 | igual | igual | Monótono; idéntico |
| MH (relleno ↑) | II, II, — — — — | II, II, III, IV, V, V | II, II, III, IV, V, V (pesos corregidos) | Monótono; tal cual se pierde el diseño desde 3.5 m |
| MT (TW ↑, S 0.006) | — — — —, 1.20, 1.20, 1.35, 1.65, **TMC 2.10** | 0.90 ×4, 1.20, 1.20, 1.35, 1.65, TMC 2.10 | 0.90 ×3, **1.05**, 1.20, 1.20, 1.35, 1.65, TMC 2.10 | Monótono; difiere en TW 0.70 (H2); el TMC final lo decide V7 sin peso propio (H4) |
| MU (TW ↑, S 0.030) | 0.90 ×8, 1.05, 1.05 | igual | 0.90 ×4, 1.05, 1.20 ×4, 1.35 | Monótono pero **incoherente con su criterio** (H2): el salto ocurre en TW = D, no en TW = 0.75 D |

---

## 5. Lo que la app hace bien (para que los hallazgos se lean en proporción)

- **Ningún diseño adoptado incumple nada**: las 57 adopciones de las corridas principales y de la variante con la tabla de clases tienen 15/15 (concreto) o 17/17 (TMC) verificaciones en «cumple».
- **Mínimo y monótono**: la traza `iteraciones` muestra, para cada diseño, el escalón menor del mismo material con su verificación incumplida, y coincide con la del revisor.
- **Control de salida con remanso** (E04, E10, MS05–07, MT04–08): reproduce exactamente el procedimiento de la hoja (banda 0.75–1.2 con «manda la comprobación», remanso bajo 0.75, «el remanso no alcanza la entrada» en barriles supercríticos).
- **Cambio de material por V3** (E05, MS01) y **sin solución** cuando ningún material pasa (E06, MS00, E12), con la exclusión de durabilidad bien aplicada (E06: pH 4.5; E14: 800 ohm-cm).
- **Estructura**: la D-load del concreto se reproduce al 0.01 % en las 66 corridas que la imprimen, y el TMC da órdenes de magnitud correctos (§7).

---

## 6. Hallazgos por severidad

Clasificación de cada diferencia: **defecto del software**, **criterio declarado** (la app hace lo que su ficha dice, y se discute el efecto) o **error del revisor** (§8).

### ALTA

**H1 — Sin las clases III, IV y V de M 170M, ningún tubo de concreto con más de ≈2.4 m de tierra sobre la clave se puede cerrar, y la app descarta el TMC que ya encontró.** *(Vacío de datos declarado; efecto de diseño alto.)*
- **Evidencia**: 13 de 57 corridas tal cual quedan «sin dimensionar» con `DatoFaltanteError: clases_producto_por_relleno` (E08, E10, E14, MQ00–01, MH02–05, MT00–03). El relleno máximo con Clase II es de 2.49 m (Ø 0.90), 2.43 m (Ø 1.20) y 2.30 m (Ø 1.65) de tierra sobre la clave, más 0.45 m de paquete (§7): un terraplén corriente de 3.5–4 m ya lo supera (MQ00: D-load 50.7 > 50 N/m/mm).
- **El TMC sí cumplía y no se publica**: en 11 de los 13 la traza `iteraciones` ya tiene un TMC con `aceptado: True` (MQ00 Ø 0.90; E08 y MH02–05 Ø 1.05; MQ01 y MT00–03 Ø 1.20; en E10 el TMC no pasa la hidráulica y en E14 está excluido), y el punto sale «sin dimensionar» porque `MD.disenar_punto` relanza el dato que falta del concreto (`_exigir_datos_presentes`). Es la regla escrita en `MD` (no elegir un material por descarte de otro que no se evaluó), pero el usuario no ve ningún diseño.
- **Disponibilidad no monótona**: en MQ, Q = 0.5 y 1.0 m³/s no tienen diseño y Q = 1.5 sí (Ø 1.05, Clase II): el tubo mayor pide menos D-load con el mismo terraplén. Un usuario puede «resolver» el bloqueo inflando el caudal.
- **Lo que lo cierra**: con las D-load de ASTM C76M declaradas (`--declarar "clases_producto_por_relleno={'concreto_reforzado': {'II': 50.0, 'III': 65.0, 'IV': 100.0, 'V': 140.0}}"`), la app dimensiona los 13 casos y **16 de 17** corridas de la variante coinciden con el revisor (la que no, MT03, es H2). Esas cuatro cifras ya figuran en `docs/validacion_conducto.md` §5 (USACE EM 1110-2-2902, pág. B-7), que el proyecto decidió no usar como fuente. Remedio: transcribir las clases de un ejemplar legible de M 170M o C76M.

### MEDIA

**H2 — V1 no aplica `borde_libre_bajo_tw_ahogante = no_cumple` cuando gobierna el control de entrada y el TW queda entre 0.75 D y D.** *(Defecto del software frente a la hoja de ruta.)*
- **Evidencia (E13, Q 0.60 m³/s, S 0.030, TW 0.80 m)**: la app adopta Ø 0.90 con control de entrada, imprime en la misma página «h_o: 0.800 m (manda TW: salida ahogada)» y «Perfil: S1 … y_max = 0.800 m», y aprueba V1 con el tirante normal: «obtenido 0.296 | admisible 0.750». El tirante conjugado de y_n = 0.267 m es 0.729 m < TW = 0.80 m, de modo que el resalto se forma **dentro** del barril y aguas abajo de él la lámina está a 0.80 m: y/D = 0.889. HDS-5 3.ª ed., núm. 3.1.3, pág. impresa 3.2 (PDF 84), literal: «In Figure 3.1C, submergence of the outlet end of the culvert does not assure outlet control. In this case, the flow just downstream of the inlet is supercritical and a hydraulic jump forms in the culvert barrel.»
- **Contra qué regla**: la hoja de ruta, nota T-2 de la Fase 5 (línea 872): cuando el TW queda por encima del llenado admisible (TW/D > 0.75) «y fijando el tirante máximo dentro del barril, llegue o no a la clave», la lectura de archivo es `no_cumple`, y «La lectura es **una sola a lo largo del TW**: no cambia al cruzar TW = D». En la app **sí cambia en TW = D**: en MU (S 0.030), Ø 0.90 se acepta con TW 0.75, 0.80, 0.85 y 0.89 m y se rechaza recién con 0.90 m; y con TW = 1.00 m se acepta Ø 1.05 (TW/D = 0.95). En pendiente suave, con el mismo TW, el control de salida sí lo rechaza (MT04: Ø 0.90 y 1.05 fuera con TW 0.80). También aparece en una pendiente ordinaria: MT03 (S 0.006, Q 1.0, TW 0.70) con la tabla de clases: Ø 0.90, y_max del perfil 0.70 m, V1 «obtenido 0.624».
- **Efecto**: diseño **uno a dos escalones por debajo** de su propio criterio (E13: 0.90 frente a 1.20; MU09: 1.05 frente a 1.35). La carga HW sí es correcta (la entrada gobierna).
- **Causa en el código**: `M5._regimen_de_v1_v2` devuelve `REGIMEN_UNIFORME` bajo control de entrada mientras TW < D, y `v1_borde_libre` toma entonces `y_normal` aunque `resultado.perfil.y_max_m` ya valga TW.

**H3 — El «NO FACTIBLE POR RASANTE» no da un delta utilizable.** *(Defecto frente a la hoja: §7.B «El chequeo devuelve "no factible → subir rasante X cm", nunca un resultado silencioso», y `CLAUDE.md`, DisenoNoFactibleError.)*
- **E09** (relleno 1.85 m, CBR 5 → resguardo 1.00 m, Q 1.5): la app dice «No se da delta de rasante: ningún escalón que no cabe lo admite como geometría pura», porque los escalones que no caben también incumplen V4. Pero **V4 y V7 son condiciones de rasante**: las dos se arreglan subiéndola. El revisor calculó **+0.655 m con concreto Ø 1.20** (gobierna V7: relleno ≥ 0.730 m sobre la clave) y la app lo confirma: +0.60 → sin diseño (Ø 1.20 falla V4 y V7), +0.65 → sin diseño (V7), **+0.66 → concreto Ø 1.20** (`app_e09_rasante/`).
- **Y cuando sí da delta, no sirve**: con +0.53 m (el delta que 7.A daría al escalón Ø 1.35) la app sigue sin diseño y propone ahora «Delta de rasante de 7.A: 0.340 m, el de TMC galvanizada Ø 1.95 m». Es un Ø 1.95 m para 1.5 m³/s, alcanzado solo porque la progresión siguió creciendo a través de fallas de V7 (que empeoran con D), y su delta sale del tamizado de 7.A, que **no contiene V7**: con +0.34 m ese TMC seguiría sin flotar. El rótulo «COTA INFERIOR … no el remedio verificado» es honesto, pero el número no orienta: faltaban 0.125 m más con concreto Ø 1.20.
- **Remedio**: calcular el delta como el mínimo, sobre los escalones que cumplen lo que no depende del relleno (V1, V2, V3, V4b), de la rasante que satisface a la vez V4, V7 y la cobertura (es lo que hace `rasante_requerida()` en `diseno_a_mano.py`).

**H4 — V7 omite el peso propio del conducto (DC = 0), contra la fórmula de la hoja, y eso cambia el material.** *(Desviación conservadora de la hoja de ruta, con efecto adverso en el diseño.)*
- **La hoja** (Fase 5, fila V7, línea 859): «γ_DC,min · DC + γ_EV,min · EV ≥ γ_WA · U … es la forma 0.90·(DC + EV) ≥ 1.00·U». La app usa 0.90·EV ≥ U (`M8`, «Por que el peso propio del conducto no entra en V7»), apoyada en AASHTO C12.6.2.3 («the dead load on the crown of the structure should exceed the buoyancy of the culvert», comentario y `should`; pág. impresa 12-19, PDF 1657, verificado) y en que «la densidad no la declara nadie». **Esa razón ya no es cierta**: el proyecto declara `peso_especifico_concreto_kn_m3` = 23.56 kN/m³ [C] (lo usa el cabezal).
- **MT08** (TW 1.50): el concreto Ø 2.10 cumple V1 y **solo** falla V7: 0.9·EV = 47.81 < U = 48.15 kN/m (por 0.34 kN/m). Con su peso (DC = 34.05 kN/m): 0.9·(DC + EV) = 78.46 ≥ 48.15. La app adopta **TMC Ø 2.10 con plancha de 4.27 mm** en una costa donde el propio Manual desaconseja el metal (aviso fijo). Omitir DC penaliza al material **pesado** (pared gruesa = más U sin contar su peso) y favorece al liviano, que es el que sí puede flotar: el sentido contrario al de la física.
- **E09**: con DC, la rasante mínima bajaría de +0.655 m (Ø 1.20, V7) a ≈ +0.53 m (Ø 1.35, gobierna V4) (`verificacion_estructural.py`).

**H5 — El criterio de archivo `borde_libre_bajo_tw_ahogante = no_cumple` sobredimensiona mucho con receptor alto.** *(Criterio declarado, decisión del dueño del 2026-11-11; se informa el efecto medido.)*
- Con la otra opción de la ventana (`aviso`) y la tabla de clases completa (`app_variante_aviso/`): E07 (Q 0.6, TW 1.00) pasa de **1.35 a 0.90**; MT04–MT07 (TW 0.8–1.2) de 1.20/1.20/1.35/**1.65** a **0.90**; MT08 (TW 1.5) de **TMC 2.10 a concreto 1.05**. Es decir, hasta cuatro escalones y un cambio de material para un caudal de 1 m³/s.
- El Manual (núm. 4.1.1.3.7 b), pág. impresa 79) dice: «las alcantarillas no deben ser diseñadas para trabajar a sección llena … Se recomienda que el diseño hidráulico considere como mínimo el 25 % de la altura»: la frase habla del **diseño hidráulico** del conducto; que el nivel del receptor le quite el borde libre es lectura del proyecto. HDS-5 trata la salida sumergida como un caso normal del control de salida. Recomendación al dueño: reconsiderar el valor de archivo o al menos imprimir la sensibilidad en la memoria de cada punto afectado.

### BAJA

**H6 — Titulares engañosos en los «no factible».** E12 (alivio con TW 0.95 m) sale «NO FACTIBLE POR RASANTE» cuando la causa es V2 en **todo** diámetro (0.08–0.19 m/s; el concreto se recorrió hasta Ø 2.25 m antes de «no caber»); E06 sale «material descartado por diámetro requerido (… 2.70 m)» cuando la causa es V3 en todo diámetro (6.04 m/s aún en 2.70). El detalle lo explica, pero el titular manda al revisor a la rasante o al catálogo. Para E12 el remedio real (subir la cota de salida sobre el TW, o aceptar V2 como aviso) no se sugiere.

**H7 — La progresión sigue después de una falla que solo empeora con D.** Con V7 (o «no cabe») el Ø mayor nunca mejora, pero la app sigue recorriendo el catálogo (E05: concreto hasta 2.70 m con V3 y V7; E09 con +0.53: hasta TMC 1.95). No cambia el resultado, pero alarga la memoria y produce los «último intento» y deltas de H3 y H6.

**H8 — La cobertura mínima (G1) no está dentro del bucle.** Se evalúa después de adoptar (7.B). En concreto y TMC no se observó efecto porque V7 (sin DC) exige más relleno que la cobertura; en HDPE (cobertura 0.61 m > V7 0.54 m) un HDPE podría adoptarse y caer luego en G1 «subir rasante». Latente, no reproducido.

**H9 — HDPE sin pared tabulada en 1.35 y 1.50 m.** La progresión del HDPE se detiene en Ø 1.35 por `espesor_pared_conducto[hdpe][1350]` (E06, E09, E12), con un tope de producto de 1.50 m. Declarado (falta el diámetro exterior del fabricante); se anota porque reduce el catálogo efectivo del HDPE a 1.20 m.

---

## 7. Estructura del conducto (Fase 8): chequeo de orden de magnitud

**Tubo de concreto (AASHTO LRFD 12.10.4.3, método indirecto, Tipo 3).** D = [(W_E + W_F)/B_FE + W_L/B_FLL]/S_i (ec. 12.10.4.3.1-1, pág. 12-64); W_E = VAF·B_c·(γ_s·H_rel + γ_p·e_paq) con VAF 1.40, γ_s = 18.85 kN/m³ (0.120 kcf, Manual de Puentes Tabla 2.4.2.1-1), γ_p = 21.99 kN/m³; B_FE de la Tabla 12.10.4.3.2a-1 (pág. 12-65); W_L por 3.6.1.2.6b (págs. 3-27/28) con IM sobre la cubierta de tierra; B_FLL 2.2. **Reproducido por el revisor al 0.00–0.01 % en las 66 corridas** (`verificacion_estructural.py`): E01 39.14, E10 52.89, E08 96.51, MH05 130.90 N/m/mm.

| Ø (m) | Relleno máximo de tierra sobre la clave (paquete 0.45 m), Tipo 3 |
|---|---|
| 0.90 | Clase II 2.49 m · III 3.69 m · IV 6.31 m · V 9.21 m |
| 1.20 | II 2.43 · III 3.62 · IV 6.21 · V 9.10 |
| 1.65 | II 2.30 · III 3.47 · IV 6.02 · V 8.86 |

Orden de magnitud coherente con la práctica (Clase III para terraplenes de 3–4 m, IV–V para 6–9 m). Las hipótesis son conservadoras y están declaradas: γ del Manual de Puentes en vez del 17 kN/m³ del criterio, paquete a 22 kN/m³, IM con la tierra sola, carga viva conservada a gran profundidad y la distribución de la 9.ª ed. sin longitud efectiva (que en rellenos de 0.6 m da +65 % frente a ACPA, `docs/validacion_conducto.md` §8; en estos ensayos todos los rellenos superan 1.4 m y el efecto es menor). **No se encontró nada inseguro.** Lo único que falla es la disponibilidad de las clases (H1).

**TMC (AASHTO LRFD 12.7.2, 68 × 13 mm).**
- E05 (Ø 1.05, 1.98 m de tierra + 0.45 m): plancha **2.77 mm**, impuesta por el **espesor mínimo de la Tabla 507-01 del EG-2013**, no por la carga. Empuje T_L = 66.1 kN/m frente a costura remachada simple 228.5 kN/m (29 %); área requerida 0.29 frente a 2.87 mm²/mm (10 %); FF 0.098 frente a 0.246 mm/N; relleno máximo 9.48 m (gobierna la costura). Comprobación a mano: P_FD ≈ 1.05·1.95·(18.85·1.98 + 22·0.45) = 96.7 kPa → T_muerta ≈ 50.8 kN/m, más ≈ 15 kN/m de carga viva: 66 kN/m. ✔
- MT08 (Ø 2.10, 1.43 m + 0.45 m): plancha **4.27 mm**, impuesta por el **factor de flexibilidad** (0.235 frente a 0.246 mm/N; AASHTO 12.5.6.1); T_L = 125.6 frente a 250.6 kN/m; relleno máximo 5.20 m. Coherente con la nota de la hoja (§3.2: con 2.01 mm el FF falla desde ≈ 1.39 m).
- La app avisa que la costura se verificó con la resistencia **remachada** de ASTM A796 y que el EG-2013 507.02 describe tubería **empernada**, y que la geometría usa la plancha de catálogo 2.01 mm (la clave sube 0.8–2.3 mm con la real). Correcto y declarado. No hay sobredimensionamiento atribuible a la app: el espesor lo fijan el EG-2013 o el FF.

**HDPE (AASHTO LRFD 12.12).** Con el perfil de prueba declarado (A 10.5–11.5 mm²/mm, I 4 500–9 500 mm⁴/mm, ≥ mínimos de la Tabla A12-11) E14 no pasa empuje ni deflexión con 3.35 m de tierra en Ø 0.90–1.20. Es coherente con las hipótesis de archivo (propiedades a 75 años, K_γE 1.5, Si-95), que son las conservadoras de la norma. No inseguro; la ruta funciona y exige el perfil real del fabricante.

**Flotación (V7).** Ver H4: conservadora para cada material, pero sesga la elección en contra del concreto.

---

## 8. Errores del revisor (declarados)

1. **Peso específico en la D-load.** El diseño congelado usó 17 kN/m³ para la tierra y el paquete y el IM con la cubierta total; la app usa 18.85 y 21.99 kN/m³ (Manual de Puentes Tabla 2.4.2.1-1 y el piso de AASHTO 12.10.2.1) y el IM con la tierra. Mis D-load salieron un 10–11 % **bajas** (no conservadoras) y erré la clase en 7 corridas: MQ00, MQ01 y MT00–03 (dije II, es **III**), E10 (dije II, es **III**), MH04 (dije IV, es **V**). **La app tiene razón**; §7 da los valores corregidos.
2. **Regla de V1 bajo control de entrada.** No es un error sino una diferencia deliberada: el revisor aplica el conjugado del tirante normal para decidir si el resalto entra al barril (H2). Con TW apenas sobre el conjugado (MU04, TW 0.75 frente a 0.729) el resultado es sensible a ese cálculo.
3. **Delta de rasante de E09.** Se calculó sin rehacer la longitud con la rasante nueva; la app lo confirmó igual (+0.65 no, +0.66 sí).

---

## 9. Reproducir

```
cd /home/user/ensayos_conducto_casos
export PATH=/home/user/venv312/bin:$PATH NORMAS_DIR=/home/user/Normas
python diseno_a_mano.py              # diseño a mano (no importa src/)
python generar_y_correr_app.py       # 57 corridas de la app -> app/
python comparar.py                   # tabla mano vs app -> comparacion.json
python correr_con_clases.py E08 E10 E14 MQ00 MQ01 MH02 MH03 MH04 MH05 MT00 MT01 MT02 MT03
python correr_variante_aviso.py      # H5
python correr_e09_rasante.py         # H3
python monotonia_local.py            # monotonía local
python verificacion_estructural.py   # §7 y H4
```

Cada escenario tiene su CSV, su JSON y su línea de comando en `entradas/<id>/comando.txt`; la salida de la app en `app/<id>.json` y `app/<id>.txt`.

---

## 10. Veredicto

**¿La app produce buenos diseños de conducto? Sí, dentro de sus criterios, con cinco reservas.** La aritmética es impecable: un diseño independiente, hecho y congelado antes de verla, da el mismo material, diámetro, control, HW, y/D y velocidades en **todos** los casos en que los dos aplican la misma regla, y la D-load del concreto se reproduce al 0.01 %. Cada diseño adoptado cumple su Fase 5 y su Fase 8, es el menor de su material y es monótono ante más caudal, menos pendiente, más relleno y más TW.

Lo que impide usarla tal cual en un expediente real:
1. **(H1, alta)** no cierra tubos de concreto con más de ≈ 2.4 m de tierra sobre la clave hasta que se transcriban las clases III–V, y descarta el TMC que ya cumplía;
2. **(H2, media)** con salida ahogada y control de entrada deja el barril sin el borde libre que su propio criterio exige, uno o dos escalones por debajo;
3. **(H3, media)** cuando no cabe, no dice cuánto subir la rasante, o lo dice para un escalón absurdo;
4. **(H4, media)** su V7 sin peso propio cambia concreto por TMC en contra de la física;
5. **(H5, media, criterio)** su lectura del borde libre bajo TW sobredimensiona hasta cuatro escalones.

Ninguno produce un conducto inseguro por capacidad hidráulica ni estructural. H2 es el único que entrega un diseño por debajo de un criterio declarado del proyecto.
