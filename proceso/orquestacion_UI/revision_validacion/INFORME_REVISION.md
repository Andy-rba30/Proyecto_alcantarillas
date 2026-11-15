# Revisión independiente de la validación de punta a punta (/tmp/validacion_web)

Programa: /home/user/val_web, commit 2d37c2c, árbol limpio antes y después. Todo lo mío está en /tmp/revision_validacion/ (corridas en ex2/, ex2alt/, wis/, upao/, d1/, d2/, gui_ex2/; recálculo propio en scripts/mano.py, que no importa nada de la app ni del validador).

Incidencia mía: al probar `cli.py --sesion` la CLI escribió su JSON por omisión junto al CSV (`/tmp/validacion_web/casos/TDOT_EX2/base/puntos.informe.json`). Ese archivo no existía antes; lo borré y la carpeta quedó como estaba.

## Veredicto por punto

| # | Punto | Veredicto |
|---|---|---|
| 1 | Validación de punta a punta | CONFIRMADO |
| 2 | Datos tomados de la fuente | CONFIRMADO |
| 3 | Invariancia de los datos de prueba | CONFIRMADO |
| 4 | Clasificaciones | (b) CONFIRMADO; (c) CON RESERVA |
| 5 | Defectos D1 y D2 | CONFIRMADOS los dos |
| 6 | Observaciones «que no son defectos» | CON RESERVA: dos esconden decisiones del dueño con efecto en el diseño |

## 1. Punta a punta — CONFIRMADO

- Repetí tres corridas con los comandos de COMANDOS.md y las entradas de casos/: TDOT Ej. 2 base (rc 0), WisDOT D = 2.5 ft base (rc 1) y la cadena UPAO/UNC TR 100/50 (rc 1). Los tres JSON son idénticos a los del validador salvo `expediente.generado_utc` (una sola diferencia en cada uno).
- Las cifras del informe salen de esos JSON. Ej. 2 a 25 cfs: HW 0.72401 m = 2.375 ft, y_n 1.553 ft, y_c 1.613 ft, TW 1.791 ft, V_erosion 8.80 ft/s. UPAO: P24(100) = 61.4892 mm, Tc 237.24 min, K 1.2848, I 9.908 mm/h. WisDOT C9: HW gobernante 2.211 y 2.596 ft.
- Ventana real: repetí el recorrido de TDOT Ej. 2 bajo xvfb. El JSON exportado por la ventana es igual al de mi corrida de CLI, 0 diferencias, y `cli.py --sesion` con la sesión guardada dice «REPRODUCE».
- Los scripts de tablas sólo leen los `*.informe.json` y la memoria HTML; ninguno importa `src`, salvo el conductor de la ventana y la reproducción mínima de D1, como declara el informe.

Reservas menores:
- **Escalones descartados:** su hidráulica (WisDOT C2 a C7, Ej. 4, Dale) no está en el JSON; se leyó de la memoria HTML de la misma corrida con expresiones regulares. Sigue siendo la CLI. La comprobé a mano en C3 y C4, y en C9 contra el JSON.
- **Ventana:** los diálogos de archivo están sustituidos y los criterios entran por la variable del campo «Valor nuevo» más el botón. Es la ventana real, pero no hay tecleo literal.
- **WisDOT C9:** G2 sale «no cumple» por 4·10⁻⁸ m, por el redondeo de `S_conducto` a 8 decimales en las entradas. El informe dice que C9 «pasa todas las verificaciones»; es inexacto y sin efecto en lo comparado.

## 2. Datos de entrada contra la fuente — CONFIRMADO

- **TDOT Ej. 2** (tdot6.pdf, págs. impresas 6-73, 6-84 y 6-88): inverts 341.25 y 340.70 ft, L = 110 ft, S = 0.005, n = 0.013, 36 in, canal trapecial b = 3 ft, z = 3, n = 0.065 (Figura 6A-19, leída de la imagen), calzada 345.32 ft. Las diez filas de la Tabla 2 coinciden con las usadas. Conversiones exactas (341.25 ft = 104.013 m; 25 cfs = 0.707921 m³/s).
- **WisDOT C3 y C9** (PDF págs. 21, 23, 24, 68, 70 y 71): inverts 798.50/798.33 y 796.27/796.08 ft, L 56 y 66 ft, D = 2.5 ft, n = 0.012, canal rectangular b = 8 ft, S = 0.33, n = 0.029, crestas 801.75 y 802.30 ft. Todo coincide con `puntos.csv` y `externos.json` (243.3828 m, 17.0688 m, S = 0.00303571 y 0.00287879). Los resultados de HY-8 usados son los del PDF.
- **Serie UPAO** (tesis, págs. 93 y 94): los 17 valores de 1965–1973 y 2004–2011 coinciden uno a uno, igual que la tabla Gumbel (57.2041, 61.4878, 71.3868) y los datos de Tinas (L = 14 739.17 m, S = 0.0602, A = 55.911 km², Tc = 3.95 h, K = 1.28, I = 11.51).
- Nota: la portada del manual TDOT dice 15-sep-2020 y `ejemplos.json` dice 2025. No cambia nada.

## 3. Invariancia — CONFIRMADO

Repetí TDOT Ej. 2 `alt`, que cambia área, terreno, rasante, subrasante, CBR, SUCS, luz y altura del canal. La diferencia máxima en HW, y_n, y_c, TW, y de salida y velocidades es 2.96·10⁻¹¹ m, igual que en `invariancia.json`. Sí cambian, como debe ser, el relleno (1.32 → 2.17 m) y la altura del terraplén. Mi `alt` es idéntico al suyo.

## 4. Clasificaciones

### Las tres (b) «error de la fuente» — CONFIRMADO

Recálculo propio:
- **Ej. 2, 2.5 cfs, y_n:** Manning con D = 3 ft, n = 0.013, S = 0.005 da 0.4693 ft. El 0.444 de HY-8 transporta 2.23 cfs con n = 0.013, y 2.42 con n = 0.012; con ninguno da 2.5.
- **Ej. 2, 2.5 cfs, y_c:** el exacto es 0.4916 ft. El 0.470 de HY-8 corresponde a 2.29 cfs.
- **Ej. 4, 90 cfs, y_c:** el exacto es 2.846 ft. El 2.967 de HY-8 corresponde a 134 cfs; HY-8 crece linealmente (+0.144 ft cada 9 cfs) cuando y_c/D se acerca a 1.

Es imprecisión numérica de HY-8, no errata de TDOT. La clasificación vale.

### Muestra de las (c), y todas las de diferencia grande — CON RESERVA

Lo recalculado coincide con la app en todos los casos. Ninguna (c) esconde un error de cálculo. Tres rótulos necesitan corrección y uno esconde un hallazgo.

| Grupo | Dif. | Mi comprobación | Veredicto |
|---|---|---|---|
| I y Q de TU-107 con Dick-Peschke (68 filas) | +48 a +136 % | C-1 a mano: P24(35) = 719.34 mm; I = 579.18 mm/h; Q = 6.038 m³/s, iguales a la app | Legítima. El Manual (núm. 3.8.1, pág. impresa 37) da Dick-Peschke para menos de 1 h y la Tabla N° 04 «entre 1 hora y 48 horas». La tesis extrapola bajo 1 h una regresión de la Tabla N° 04, fuera del rango de la tabla. El criterio `relacion_intensidad_duracion` [A] ya declara el 81 % en su ficha |
| Factor 1.13 (UPAO y TU-107) | −11.5 % | Ninguna ocurrencia de «1.13» ni «intervalo fijo» en el PDF del Manual | Legítima según la regla «no se inventa». Es del lado inseguro: decisión del dueño (§6) |
| y_n con n = 0.013 frente a 0.012 (13 filas) | +5 a +8 % | C9-Qm: 1.894 ft con 0.012 (HY-8 1.898) y 2.048 con 0.013 (app 2.048) | Diferencia cierta, **rótulo incorrecto**: no es «norma» (§6.1) |
| V de salida bajo control de entrada (17 filas) | +24 a +36 % | La app da exactamente 1.30 × V(n = 0.013); Manning resuelto con n = 0.010 da sólo +21.5 a +23 % | Documentada, pero **esconde un hallazgo** (§6.2) |
| Ej. 4, V a 90 cfs | +4.5 % | V(2.072 ft) = 17.28 ft/s; V normal = 18.07 ft/s | Debería ser «no comparable»: la fila de HY-8 es de la corrida con entrada de pendiente variable (garganta a 339.25 ft, pág. 6-100) |
| Dale Blvd | +16 y +31 % | No recalculado | Otra configuración: «no comparable», no una fila de tolerancia |
| I de Tinas | −13.9 % | Ecs. 32–34 sobre P24 × 1.13: 11.51 (la tesis cuadra); Dick-Peschke: 9.908 (app) | Legítima (ficha T1-08) |
| Tinas y 5 cuencas de TU-107 detenidas | — | «A<10 Km2» (pág. impresa 49); racional modificado «menores de 770 km2 … 0.25 y 24 horas» (pág. impresa 51) | Legítima. Tinas es un puente, fuera de alcance por partida doble |
| 6 escalones de WisDOT «sin hidráulica» | — | C4-Qm: el caudal a sección llena con n = 0.013 (unos 22.5 cfs) queda bajo los 26 cfs | Legítima como descarte de diseño. Es una limitación para verificar tubos existentes |

No cotejé contra el PDF la inversión de columnas de Tc de TU-107 en `obras.json` que el validador señala. Sí rehíce P24 LN2P (719.34 y 934.90) y el Δ de K-S (0.0535).

## 5. Defectos candidatos

### D1 — CONFIRMADO (severidad media)

Reproducido por la CLI y en proceso. Con `{"inicio": 0.9144, "paso": 0.1524}` la serie sale 0.9144 → 1.07 (debía ser 1.0668) y el tercer escalón levanta `DatoInvalidoError … (valor leído: 1.07)`. El punto termina como `DisenoNoFactibleError`, «material no evaluable», en los tres materiales.

Es peor de lo que dice el informe:
- El segundo escalón **se evalúa con 1.07 m**, un diámetro que nadie declaró y que pide la fila de espesor 1070. Es una sustitución silenciosa.
- Falla igual con 0.90 + 0.075 (da 0.97), 0.90 + 0.125 (da 1.02) y 0.914 + 0.152.
- El error culpa al dato `D`, que el usuario no escribió, y se degrada a «no factible». Un fallo del programa se presenta como problema del expediente.

**Corrección: el código.** La ficha de `diametros_normalizados` [C] nombra los 0.9144 m como «la serie real» y la puerta los acepta; el consumidor no puede alterarlos.
- En `src/modulos/M2_material.py:973`, devolver `inicio + (n + 1) * paso` sin `round(…, 2)`. La guardia de pertenencia ya absorbe el ruido flotante con `TOL_UMBRAL_NORMATIVO`, y la clave de espesor ya redondea al milímetro.
- Añadir un test con la serie de 6 in y otro con paso de 0.075.
- Si el dueño prefiriera resolución de centímetro, el rechazo va en la puerta (`_verificar_criterio`, `ValueError`, patrón EXT-5) y hay que corregir la ficha. No es lo que la ficha dice hoy.

### D2 — CONFIRMADO como defecto documental (severidad baja)

Reproducido: mismo punto sin NF y con `NF_profundidad_m = 10.0`; V7 da 1.2745 frente a 9.6235 kN/m en los dos y el motivo del descarte es idéntico.

**Corrección: la documentación, no el código.** El código está sostenido por:
- la fila V7 de la hoja de ruta (`hoja_de_ruta_alcantarillas_v8.md:859`): «Tubería vacía, NF en su cota más alta»;
- el Manual de Puentes núm. 2.4.3.8.2, que refiere la subpresión al «nivel de agua de diseño», no a una medición de un día;
- los docstrings de `M8_estructural.py` (líneas 136–152) y `M5.v7_flotacion`, que lo declaran.

Hacer que V7 lea el NF medido exigiría un nivel de agua de diseño y una regla de sumersión parcial que ninguna fuente del proyecto fija: sería inventar un criterio.

Sitios a corregir:
1. `docs/contrato_entradas.md:71`: quitar «La lee V7» y «V7 queda pendiente de ese dato».
2. La hoja de ruta, línea 223 («la lee V7»), que contradice su propia fila V7. El defecto se reporta contra ella.
3. El concepto de la columna en `src/variables_entrada.py:787` («para la flotación (V7)»), que es el texto que imprime el pre-vuelo.

Nota: el docstring de M8 justifica la sumersión completa con «el NF somero de la llanura del Bajo Piura», un argumento de sitio aplicado a cualquier obra desde EXT-10. Además DC = 0. Juntas, las dos hipótesis equivalen a exigir un relleno de unas 0.45 veces el diámetro exterior en todo cruce, haya o no agua. Es decisión del dueño (§6.5).

## 6. Observaciones «que no son defectos»

### 6.1 n del concreto no declarable — CON RESERVA: rótulo de taxonomía y decisión del dueño

El informe dice «es la norma que la app sigue». No es exacto.
- La Tabla N° 09 (pág. impresa 75) da MÍNIMO / NORMAL / MÁXIMO (0.010 / 0.011 / 0.013). El texto del Manual no dice cuál usar; busqué «rugosidad» junto a máximo/mínimo en todo el PDF.
- La regla de doble n es de la hoja de ruta (línea 557), rotulada «Regla [N]» sin numeral que la sostenga.
- Regla del proyecto: «Tabla y elección se separan siempre»; los valores son [N] y cuál aplica es [A].
- Precedentes en el propio repositorio: `v_max_concreto_eleccion` [A], y `n_manning_hdpe` y `n_manning_cajon`, que sí son declarables.

Recomendación: corregir el rótulo de la línea 557 a adopción del proyecto. El dueño decide si la elección de columna pasa a ser un criterio [A] con ventana mín–normal–máx.

### 6.2 Velocidad de salida con n mínimo — decisión del dueño, con efecto medido en el diseño

`V_erosion` no es Manning resuelto con n mínimo. Es V(n máx) × n_máx/n_mín sobre la geometría de n máx, es decir × 1.30, y no cumple continuidad. Manning resuelto con n = 0.010 da +21.5 a +23 %. El exceso es de un 7 % sobre el máximo que cualquier n del rango puede producir.

Está documentado (`modelos.TiranteNormal`, caso patrón CP-2), pero cambia diseños. En UPAO ALC46 (Q = 0.317 m³/s, S = 0.10):

| Diámetro | V(n máx) | V_erosion de la app | Manning con n mín | Resultado frente a 6.0 m/s |
|---|---|---|---|---|
| 0.90 m | 4.83 | 6.28 | 5.81 | La app lo rechaza; con n mín resuelto cumpliría |
| 1.35 m | 4.58 | 5.96 | 5.50 | La app lo adopta |

La app sube a 1.35 m para 317 L/s. La hoja de ruta dice «n mínimo para velocidad máxima», no «sobre la geometría de n máximo». El dueño decide: mantener la convención como [A] con su sensibilidad, o resolver Manning con n mínimo. El validador lo dejó como «(c) método» sin medir esta consecuencia.

### 6.3 Dos relaciones intensidad–duración — no es defecto

Ya es un criterio [A] con la sensibilidad escrita en su ficha (81 % a 1 h). No pide acción. Opcional: avisar, con Tc ≥ 1 h, cuánto daría la otra relación.

### 6.4 Factor 1.13 — decisión del dueño

No está en el Manual, así que no aplicarlo cumple la regla. Pero deja P24 y Q un 11.5 % por debajo de la práctica peruana que usan las dos tesis. Opciones: un criterio [C] u [A] de valor 1.0 con ventana hasta 1.13, o decir en `docs/contrato_entradas.md` (fila `p24_mm`) si la serie debe entrar ya corregida.

### 6.5 Hipótesis de V7 — decisión del dueño

Sumersión completa sea cual sea el NF, y DC = 0. Decidir si se quedan fijas, con la documentación corregida por D2, o pasan a criterio declarado para otras obras.

### 6.6 Serie de 729 mm/24 h ajustada sin aviso — decisión del dueño

No es defecto: no hay umbral normativo y poner uno sería inventarlo.
- El Manual sí manda evaluar «la consistencia de los datos registrados» (núm. 3.4, pág. impresa 21).
- El programa ya tiene el patrón de un contraste sin umbral (`FH.Q_ESPECIFICO`, «AVISO DE PLAUSIBILIDAD, sin umbral»).
- Un aviso análogo sobre la serie (máximo frente a mediana, valores repetidos) no inventaría nada.
- En TU-107 la serie tiene mediana de 140 mm, máximo de 729 mm y dos pares repetidos, y produce I = 579 mm/h en 28 min.

### 6.7 Racional modificado (ficha T1-08) — decisión del dueño

El Manual trae el método para cuencas de hasta 770 km² (ecs. 29–35). Hoy la app se detiene desde 10 km². Implementarlo es decisión de alcance.

## Defectos CONFIRMADOS

1. **D1** — `src/modulos/M2_material.py:973`: quitar el redondeo a 2 decimales y añadir tests con la serie de 6 in.
2. **D2** — documental: corregir `docs/contrato_entradas.md:71`, la línea 223 de la hoja de ruta y `src/variables_entrada.py:787`. No tocar V7.
3. **Rótulo «Regla [N]» de la regla de doble n** (hoja de ruta, línea 557) — nuevo, documental y de taxonomía: el Manual no la enuncia. Corregir el rótulo.

Ningún error de cálculo hidráulico ni hidrológico: todo lo recalculado a mano coincide con la app.

## Decisiones del dueño

1. Si el n del concreto, o la columna de la Tabla N° 09 que se usa, pasa a ser declarable [A].
2. Definición de `V_erosion`: × n_máx/n_mín sobre la geometría de n máx, o Manning resuelto con n mín. Cambia diseños (ALC46).
3. Hipótesis de V7 (sumersión completa y DC = 0): fijas o criterio declarado.
4. Factor 1.13 de intervalo fijo: criterio o nota de contrato.
5. Aviso de plausibilidad de la serie, sin umbral.
6. Implementar el racional modificado (T1-08).
7. En D1, si se prefiere resolución de centímetro: rechazo en la puerta y ficha corregida.

## Correcciones al informe del validador

- Cambiar «(c) norma» por «adopción del proyecto» en y_n.
- Pasar Dale y la V del Ej. 4 a «no comparable».
- Añadir a D1 la evaluación silenciosa con 1.07 m.
- Añadir a la observación 2 el efecto medido en ALC46.
- Corregir «C9 pasa todas las verificaciones» (G2 falla por redondeo de entrada).
