# Validación externa: el motor contra los ejemplos resueltos de HDS-5 y HEC-14 (T-11)

> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe `python -m tests.apoyo.validacion_externa --escribir` y `tests/test_t11_validacion_externa.py` lo regenera y lo compara. Los casos son los que T-2 y T-8 transcribieron y verificaron contra su página; la cuenta es la del motor (M3, M4 y M6), con las mismas llamadas que sus tests. HY-8 no está en el entorno: su procedimiento está en `docs/validacion_hy8.md`, sin ningún resultado.

## 1. HDS-5, Design Guideline 1 (formularios de los ejemplos)

Fuente: HDS-5 3a ed. (FHWA-HIF-12-026, abril 2012), Design Guideline 1 «Culvert Design Using Nomographs»: DG 1.3 (circular) y DG 1.4 (cajon); formularios en las pags. impresas DG1.4 (PDF 275) y DG1.10 (PDF 281). Caso patrón `tests/fixtures/casos_patron.py::CP_HDS5_DG1`; comparación `tests/test_t2_hidraulica.py::_calcular_fila`.

- **Tolerancia de lectura: 3%.** Las cifras del formulario salen de leer nomogramas; lo que cae fuera lo censa el caso patrón con su causa, medida, y no se ajusta ni el motor ni la tolerancia.
- **Tolerancia de la fuente: ±10%**, «accurate to within plus or minus ten percent, in terms of headwater elevation» (HDS-5, PDF 83).
- La diferencia es (motor / publicado − 1); en `EL_ho_ft` se toma sobre la altura H + h_o y no sobre la cota, para que el 100 de la cota no la esconda.

| Ejemplo | Fila | Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto | Causa censada (si sale del 3 %) |
|---|---|---|---|---|---|---|---|---|
| circular | `rcp_54_groove` | `HW_sobre_D` | — | 1.770 | 1.761 | -0.52% | ≤ 3% | — |
| circular | `rcp_54_groove` | `HW_entrada_ft` | ft | 7.970 | 7.923 | -0.58% | ≤ 3% | — |
| circular | `rcp_54_groove` | `d_c_ft` | ft | 4.100 | 4.036 | -1.56% | ≤ 3% | — |
| circular | `rcp_54_groove` | `h_o_ft` | ft | 4.300 | 4.268 | -0.74% | ≤ 3% | — |
| circular | `rcp_54_groove` | `H_ft` | ft | 4.700 | 4.712 | +0.25% | ≤ 3% | — |
| circular | `rcp_54_groove` | `EL_ho_ft` | ft | 107.000 | 106.980 | -0.22% | ≤ 3% | — |
| circular | `rcp_54_groove` | `V_salida_ft_s` | ft/s | 15.300 | 15.227 | -0.47% | ≤ 3% | — |
| circular | `rcp_54_groove` | `control` | — | entrada | entrada | — | igual | — |
| circular | `rcp_60_groove` | `HW_sobre_D` | — | 1.360 | 1.341 | -1.42% | ≤ 3% | — |
| circular | `rcp_60_groove` | `HW_entrada_ft` | ft | 6.800 | 6.704 | -1.42% | ≤ 3% | — |
| circular | `rcp_60_groove` | `d_c_ft` | ft | 4.100 | 4.037 | -1.54% | ≤ 3% | — |
| circular | `rcp_60_groove` | `h_o_ft` | ft | 4.600 | 4.518 | -1.77% | ≤ 3% | — |
| circular | `rcp_60_groove` | `H_ft` | ft | 2.900 | 2.940 | +1.37% | ≤ 3% | — |
| circular | `rcp_60_groove` | `EL_ho_ft` | ft | 105.500 | 105.458 | -0.56% | ≤ 3% | — |
| circular | `rcp_60_groove` | `V_salida_ft_s` | ft/s | 15.600 | 15.588 | -0.08% | ≤ 3% | — |
| circular | `rcp_60_groove` | `control` | — | entrada | entrada | — | igual | — |
| circular | `cmp_72_bisel_45` | `HW_sobre_D` | — | 0.960 | 0.944 | -1.66% | ≤ 3% | — |
| circular | `cmp_72_bisel_45` | `HW_entrada_ft` | ft | 5.760 | 5.664 | -1.66% | ≤ 3% | — |
| circular | `cmp_72_bisel_45` | `d_c_ft` | ft | 3.800 | 3.865 | +1.72% | ≤ 3% | — |
| circular | `cmp_72_bisel_45` | `h_o_ft` | ft | 4.900 | 4.933 | +0.67% | ≤ 3% | — |
| circular | `cmp_60_bisel_45` | `HW_sobre_D` | — | 1.400 | 1.357 | -3.05% | ≤ 10% (fuera de la lectura) | -3.05 %: lectura de la Carta 3B. La ec. (A.3) con c = 0.0300 e Y = 0.74 da 1.357 para q* = 4.555; el formulario lee 1.40 |
| circular | `cmp_60_bisel_45` | `HW_entrada_ft` | ft | 7.100 | 6.787 | -4.42% | ≤ 10% (fuera de la lectura) | -4.42 %: ademas de la lectura anterior, la cifra impresa (7.10 ft) no es el producto de las dos que tiene al lado (1.40 x 5.0 ft = 7.00 ft) |
| circular | `cmp_60_bisel_45` | `d_c_ft` | ft | 4.100 | 4.037 | -1.54% | ≤ 3% | — |
| circular | `cmp_60_bisel_45` | `h_o_ft` | ft | 4.600 | 4.518 | -1.77% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `HW_sobre_D` | — | 1.570 | 1.590 | +1.26% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `HW_entrada_ft` | ft | 7.900 | 7.949 | +0.62% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `d_c_ft` | ft | 4.200 | 4.267 | +1.59% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `h_o_ft` | ft | 4.600 | 4.633 | +0.73% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `H_ft` | ft | 3.550 | 3.409 | -3.97% | ≤ 10% (fuera de la lectura) | -3.97 %: lectura del nomograma de control de salida (Carta 15B). La formula (7) que el propio formulario imprime al pie da 3.41 ft con sus datos (A = 30 ft2, R = 30/22 ft, n = 0.012, L = 250 ft, ke = 0.5); el formulario anota 3.55 |
| cajon | `cajon_6x5_escuadra` | `EL_ho_ft` | ft | 103.200 | 103.042 | -1.92% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `V_salida_ft_s` | ft/s | 21.100 | 21.110 | +0.05% | ≤ 3% | — |
| cajon | `cajon_6x5_escuadra` | `control` | — | entrada | entrada | — | igual | — |
| cajon | `cajon_5x5_escuadra` | `HW_sobre_D` | — | 1.910 | 1.942 | +1.65% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `HW_entrada_ft` | ft | 9.600 | 9.708 | +1.13% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `d_c_ft` | ft | 4.800 | 4.818 | +0.38% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `h_o_ft` | ft | 4.900 | 4.909 | +0.19% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `H_ft` | ft | 5.200 | 5.100 | -1.92% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `EL_ho_ft` | ft | 105.100 | 105.009 | -0.90% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `V_salida_ft_s` | ft/s | 20.800 | 21.163 | +1.74% | ≤ 3% | — |
| cajon | `cajon_5x5_escuadra` | `control` | — | entrada | entrada | — | igual | — |
| cajon | `cajon_5x5_bisel_45` | `HW_sobre_D` | — | 1.710 | 1.714 | +0.23% | ≤ 3% | — |
| cajon | `cajon_5x5_bisel_45` | `HW_entrada_ft` | ft | 8.550 | 8.570 | +0.23% | ≤ 3% | — |
| cajon | `cajon_5x5_bisel_45` | `d_c_ft` | ft | 4.800 | 4.818 | +0.38% | ≤ 3% | — |
| cajon | `cajon_5x5_bisel_45` | `h_o_ft` | ft | 4.900 | 4.909 | +0.19% | ≤ 3% | — |
| cajon | `cajon_5x5_bisel_45` | `H_ft` | ft | 5.000 | 4.429 | -11.42% | > 10% | -11.42 %: la cifra impresa (5.0 ft) NO se reproduce con la formula (7) del pie del formulario y el ke = 0.2 que la misma fila declara, que da 4.43 ft; con ke = 0.5 daria 5.10 ft, que es la fila de encima (5.2). Es una inconsistencia interna de la fuente: pasar de ke 0.5 a 0.2 tiene que bajar H en 0.3 x V^2/2g = 0.67 ft, y el formulario la baja 0.2 ft |
| cajon | `cajon_5x5_bisel_45` | `EL_ho_ft` | ft | 104.900 | 104.338 | -5.68% | ≤ 10% (fuera de la lectura) | -5.68 % sobre H + h_o (la altura sobre el fondo de la salida): arrastra el H de la linea anterior |
| cajon | `cajon_5x5_bisel_45` | `V_salida_ft_s` | ft/s | 20.800 | 21.163 | +1.74% | ≤ 3% | — |
| cajon | `cajon_5x5_bisel_45` | `control` | — | entrada | entrada | — | igual | — |

Resumen: **38 de 43** cifras dentro del 3% de lectura; las 5 restantes son las censadas con su causa; **5 de 5** controles gobernantes iguales al publicado.

### 1.1 Las dos filas de metal corrugado: el n que la fuente acota

El formulario no imprime el n del metal corrugado. La fuente lo acota en la Tabla B.1 (0.022–0.027, pág. impresa B.6, PDF 208) y da 0.024 como típico (pág. impresa 3.8, PDF 90). No se compara contra una cifra al 3 %: lo publicado tiene que caer en el intervalo que da el motor con los dos extremos del rango.

| Fila | Magnitud | Publicado | Motor, n bajo | Motor, n alto | Motor, n típico | ¿Dentro del intervalo? |
|---|---|---|---|---|---|---|
| `cmp_72_bisel_45` | `H_ft` | 2.600 | 2.211 | 2.858 | 2.454 | sí |
| `cmp_72_bisel_45` | `EL_ho_ft` | 105.500 | 105.144 | 105.791 | 105.387 | sí |
| `cmp_72_bisel_45` | `V_salida_ft_s` | 9.000 | 9.831 | 8.220 | 9.142 | sí |
| `cmp_72_bisel_45` | `control` | entrada | entrada | salida | entrada | igual con el n típico; cambia dentro del rango (entrada con el n bajo, salida con el alto) |
| `cmp_60_bisel_45` | `H_ft` | 6.300 | 5.314 | 7.025 | 5.956 | sí |
| `cmp_60_bisel_45` | `EL_ho_ft` | 108.900 | 107.832 | 109.543 | 108.475 | sí |
| `cmp_60_bisel_45` | `V_salida_ft_s` | 11.900 | 11.774 | 11.774 | 11.774 | no depende de n: -1.06%, ≤ 3% |
| `cmp_60_bisel_45` | `control` | salida | salida | salida | salida | igual con el n típico; el mismo en todo el rango |

Con el control de **salida** gobernando, la velocidad de salida no depende de n: es Q/A al tirante crítico (TW bajo el crítico), y es la que se compara.

### 1.2 Lo que este ejemplo no valida

- Ninguna de las siete filas cae en la transición 3.5 < q* < 4.0 del control de entrada: el ejemplo valida la rama no sumergida y la sumergida, no la recta de transición, que sigue sostenida sólo por los casos patrón internos (ficha T2-05).
- No hay ejemplo publicado del perfil de la lámina de agua (E-A), de V8 a presión, de la Fase 8 ni del cabezal: esos se sostienen con dorados calculados a mano en sus casos patrón.

## 2. HEC-14: los ejemplos resueltos que T-8 usó como oráculo

Tolerancia: 1% (la de T-8 para un ejemplo impreso: la fuente imprime dos o tres cifras y redondea los intermedios). Cada cifra publicada está **verificada en su página** por `tests/test_t11_validacion_externa.py` (marca `pdf`, con `NORMAS_DIR`: HEC-14 vive sólo en el repositorio de normas), que busca en el texto de la página la frase de la última columna.

### Design Example: Riprap Apron (SI)

HEC-14, págs. impresas 10-18 y 10-19 (PDF 219 y 220). Datos: Q = 2.33 m³/s, D = 1.5 m, TW = 0.5 m (TW < 0.4D: se usa 0.6 m).

| Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto | Texto en la página |
|---|---|---|---|---|---|---|
| D50 de la Ec. (10.4) | m | 0.130 | 0.131 | +0.66% | ≤ 1% | «equals 0.13 meters» |
| D50 de la clase (Tabla 10.1, clase 2) | m | 0.150 | 0.150 | +0.00% | ≤ 1% | «riprap class 2 (D50 = 0.15 m)» |
| longitud L = 4D | m | 6.000 | 6.000 | +0.00% | ≤ 1% | «L = 4D = 4(1.5) = 6 m» |
| profundidad 3.3·D50 | m | 0.500 | 0.495 | -1.00% | ≤ 1% | «3.3 (0.15) = 0.50 m» |
| ancho al final 3D + (2/3)L | m | 8.500 | 8.500 | +0.00% | ≤ 1% | «(2/3)(6) = 8.5 m» |

La profundidad sale −1.00 %, sobre la frontera del 1 %: es redondeo de la fuente, que imprime «3.3 (0.15) = 0.50 m» cuando 3.3 × 0.15 = 0.495 m; el motor da 0.495 m (T-8 lo fija con la fórmula, no con la cifra impresa).

### Design Example: Riprap Apron (CU), a su escala real

HEC-14, pág. impresa 10-19 (PDF 220). Datos: Q = 85 ft³/s, D = 5.0 ft = 60 in, TW = 1.6 ft (se usa 2.0 ft).

| Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto | Texto en la página |
|---|---|---|---|---|---|---|
| D50 de la Ec. (10.4) | ft | 0.430 | 0.432 | +0.47% | ≤ 1% | «equals 0.43 feet» |
| longitud L = 4D | ft | 20.000 | 20.000 | +0.00% | ≤ 1% | «L = 4D = 4(5) = 20 ft» |
| ancho al final 3D + (2/3)L | ft | 28.300 | 28.333 | +0.12% | ≤ 1% | «(2/3)(20) = 28.3 ft» |

D = 60 in es el límite de la nota 8 de la Tabla 1.1 que rige desde las correcciones de T-8 (`HEC14_APRON_ALTURA_MAX_M`); el ejemplo entra a su escala, sin la λ = 0.9 que T-8 había usado.

### Design Example: Estimating Scour Hole Geometry in a Cohesionless Soil (SI)

HEC-14, págs. impresas 5-4 y 5-5 (PDF 57 y 58). Datos: D = 457 mm, S = 2 %, caída 0.914 m (Hd = 2), Q = 0.764 m³/s, σ = 1.87, t = 30 min.

| Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto | Texto en la página |
|---|---|---|---|---|---|---|
| profundidad hs (Ec. 5.1) | m | 1.140 | 1.134 | -0.50% | ≤ 1% | «equals 1.14 meter» |
| ancho Ws | m | 8.820 | 8.813 | -0.08% | ≤ 1% | «equals 8.82 meters» |
| longitud Ls | m | 7.060 | 7.055 | -0.07% | ≤ 1% | «equals 7.06 meters» |
| distancia al máximo 0.4·Ls | m | 2.820 | 2.822 | +0.08% | ≤ 1% | «= 2.82 m» |

La velocidad no entra en la Ec. (5.1); el test le da 3.0 m/s y no influye. El D84/D16 se elige para σ = 1.87.

### Design Example: Estimating Scour Hole Geometry in a Cohesive Soil (SI)

HEC-14, págs. impresas 5-8 y 5-9 (PDF 61 y 62). Datos: D = 610 mm, S = 0, sin caída, Q = 1.133 m³/s, PI = 12, Sv = 23 970 N/m², V = 3.88 m/s, t = 30 min.

| Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto | Texto en la página |
|---|---|---|---|---|---|---|
| τc (Ec. 5.4) | N/m² | 39.900 | 39.915 | +0.04% | ≤ 1% | «= 39.9 N/m2» |
| profundidad hs (Ec. 5.2) | m | 1.200 | 1.206 | +0.50% | ≤ 1% | «= 1.2 m» |
| ancho Ws | m | 5.020 | 5.035 | +0.30% | ≤ 1% | «= 5.02 m» |
| longitud Ls | m | 9.810 | 9.858 | +0.49% | ≤ 1% | «= 9.81 m» |

La fuente escribe (0.09)^θ por (30/316)^θ = (0.0949)^θ: de ahí el medio por ciento de Ws y Ls (ficha de T-8).

### Design Example: USBR Type VI Impact Basin (SI), pasos 1 y 2

HEC-14, pág. impresa 9-40 (PDF 197). Datos: D = 1.219 m, Q = 8.5 m³/s, Vo = 12.192 m/s.

| Magnitud | Unidad | Publicado | Motor | Diferencia | Veredicto | Texto en la página |
|---|---|---|---|---|---|---|
| área A = Q/Vo | m² | 0.697 | 0.697 | +0.03% | ≤ 1% | «= 0.697 m2» |
| tirante equivalente ye = (A/2)^0.5 | m | 0.590 | 0.590 | +0.07% | ≤ 1% | «= 0.590 m» |
| Froude Fr = Vo/(g·ye)^0.5 | — | 5.070 | 5.066 | -0.08% | ≤ 1% | «= 5.07» |

