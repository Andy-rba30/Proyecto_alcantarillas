# Validación hidrológica de MH con casos reales publicados

> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe `python -m tests.apoyo.validacion_hidrologica --escribir` y `tests/test_validacion_hidrologica.py` lo regenera y lo compara. Las cifras publicadas están transcritas con su documento, página y tabla en `tests/apoyo/validacion_hidrologica.py`; las entradas, en `tests/fixtures/hidrologia_casos_reales/` (DATOS DE CASO REAL PUBLICADO — no son datos de este proyecto); la cuenta es la de las funciones de `src/modulos/MH_hidrologia.py`. Los PDF están en el repositorio de normas, `ejemplos_resueltos/casos_reales/`.

## 1. Qué es, de dónde sale y qué no valida

El material es de una verificación independiente (dossier `hidrologia_casos_reales.md`, en la carpeta `verificaciones_del_dueno/hidrologia/` del estado de VE-3 del material de proceso): el verificador transcribió los seis documentos, hizo el cálculo a mano sin importar `src/`, lo congeló con sha1 antes de correr el programa y después comparó. Este documento rehace la comparación con el programa en cada corrida de la suite.

**Lo que ningún caso valida: el caudal de punta a punta.** Ninguno de los seis documentos calcula el caudal con el método de MH (P24 por ajuste con K-S, tc de la Tabla N.º 05 o de Témez, Dick-Peschke bajo 1 h, C de la Tabla N.º 08, racional o racional modificado): todos usan otra relación intensidad-duración, otro tc o un C que la Tabla N.º 08 no puede dar. Lo que se valida con números de terceros son PIEZAS: el estadístico K-S de la ecuación (13), los tres estimadores (Normal, Log Normal 2P, Gumbel por momentos), Dick-Peschke, Témez y el K de Témez. El caudal se compara sólo contra el cálculo a mano del verificador (sección 10).

Tampoco se validan: el C (ningún documento publica `cobertura`, `suelo` ni `S_terreno`; en los CSV son VEHÍCULO DEL VERIFICADOR que lleva a la Tabla N.º 08 al C declarado), el CN del racional modificado (ninguno lo publica con su caudal), la Log Pearson III y las demás distribuciones sin estimador impreso (MH no las ajusta), y el pipeline completo por la CLI (no hay CSV de puntos publicable sin inventar columnas).

| Caso | Documento | Clasificación | Por qué | Qué NO valida |
|---|---|---|---|---|
| INDECI Piura | INDECI-OEA, «Mapa de peligros de la ciudad de Piura», jun. 2009, Vol. I (`mapa_peligros_vol1.pdf`; impresa = PDF − 16) y Vol. II anexos (`mapa_peligros_vol2_anexos.pdf`; se cita la página del PDF). Estación Miraflores 1971-2008 | **oráculo numérico de piezas** | publica la P24(TR) de Normal, Log Normal y Gumbel por momentos (su «Gumbel modificado») con y sin años FEN, y el Δ de K-S calculado con la misma ecuación (13) del Manual. Es el mejor caso del conjunto, y el único que nombra sus años FEN | el caudal: no publica longitud ni pendiente de ninguna cuenca, y su intensidad es P24/6 h |
| UNTumbes TU-107 | Ramos Estrada, tesis UNTumbes, 2025, carretera Bocapán–Tamarindo (`tesis.pdf`; impresa = PDF). Estación Cañaveral, 40 años | **adversarial (y oráculo de la estadística)** | su estadística (media, s, Δ de Normal, LN2 y Gumbel, P24 LN2) y los 41 Témez reproducen a la cifra impresa, pero la serie no es creíble: filas mensuales copiadas entre años, lluvias de 24 h de hasta 729 mm, sin años FEN declarados. Lo que vale es qué hace el programa con esa entrada | el caudal: IDF propia ajustada a la Tabla N.º 04 y extrapolada a minutos, y hidrograma triangular sobre 10 km²; la serie misma es inverosímil |
| UNSAAC Roquepata | Bermejo Colque y Cruz Huamán, tesis UNSAAC, 2019, camino vecinal Emp. CU112–Roquepata (`tesis.pdf`; impresa = PDF − 12). Estación Colquepata 1990-2014 | **oráculo numérico de piezas** | Gumbel por momentos (10 TR), Dick-Peschke (48 celdas) y Témez (15 microcuencas) con números de terceros; el caudal es contraste de método | el caudal: tc promediado con Bransby-Williams e IDF de regresión; la serie es inhomogénea (quiebre en 1998) |
| UPAO La Jalca | Campos Muñoz e Inga Yopan, tesis UPAO, 2016, La Jalca–Nueva Esperanza (`tesis.pdf`; impresa = PDF − 20). Estación Chachapoyas, dos series discordantes (A y B) | **oráculo numérico de piezas** | serie A: Δ y P24 de Normal, LN y Gumbel; serie B: Gumbel por momentos (siete TR). Segundo oráculo completo de estimadores y K-S, independiente del de Piura | el caudal: IDF ajustada a la Tabla N.º 04 y evaluada a 14 min, y elige Log Pearson III, que MH no ajusta |
| UPeU Colpahuayco | Huamán Guerra y Marrujo Carpio, UPeU, 2023, carretera Colpahuayco–Langui (`doc.pdf`; impresa = PDF). Estación Sicuani 1993-2020 | **contraste de método** | es el único que aplica el racional modificado de Témez con sus pasos, pero su P24 sale de Pearson III y su C de un CN que no imprime; sólo el K se contrasta, y no en todas las filas | la P24, el C y el caudal |
| ESPOL Intervalles | Luna Chalán, tesis ESPOL, 2023, vía Intervalles, Loja, Ecuador (`tesis.pdf`; impresa = PDF − 5). Cuatro estaciones INAMHI | **descartable para el caudal; contraste de método del K-S** | la hidrología es ecuatoriana (IDF del INAMHI, fórmula del MTOP); lo que aporta son cuatro series reales con el Dmax de K-S de Hydrognomon, que coincide en Normal y Gumbel en tres estaciones | toda la hidrología de MH; el cajón con HY-8 es de M3/M4 |

## 2. Tolerancias y regla de juicio

| Nombre | Valor | Por qué |
|---|---|---|
| `TOL_P24_INDECI` | ±0.1 % | dossier §2.5: el estudio redondea z y los logaritmos a 3 decimales (medido: 0.05 %) |
| `TOL_D_INDECI` | ±0.0005 | dossier §2.5: el Δ se imprime a 3 decimales |
| `TOL_P24_UNTUMBES` | ±0.05 % | dossier §3.5: redondeo de z en HidroEsta (medido: 0.04 %) |
| `TOL_D_UNTUMBES` | ±5e-05 | dossier §3.5: el Δ se imprime a 4 decimales |
| `TOL_TC_UNTUMBES` | ±0.007 h | dossier §3.2 y §3.5: desvío máximo medido contra la columna TÉMEZ, con la pendiente derivada de las cotas |
| `TOL_P24_UNSAAC` | ±0.01 % | dossier §4.5 (medido: 0.004 %) |
| `TOL_I_UNSAAC` | ±0.02 mm/h | dossier §4.5: la P24 de la Tabla 6.8 está a 2 decimales (medido: 0.013 mm/h) |
| `TOL_TC_UNSAAC` | ±0.005 min | dossier §4.5: el tc se imprime a 2 decimales |
| `TOL_D_UPAO` | ±5e-05 | dossier §5.5: el Δ se imprime a 4 decimales |
| `TOL_P24_UPAO_A` | ±0.02 mm | dossier §5.5: las 15 lluvias de la serie A |
| `TOL_XT_UPAO_B` | ±0.005 % | dossier §5.5: XT' de la serie B (medido: 0.003 %) |
| `TOL_K_UPEU` | ±0.006 | dossier §6.5: el K se imprime a 2 decimales |
| `TOL_D_ESPOL` | ±0.0001 | dossier §7: Dmax de Hydrognomon en Normal y Gumbel |
| `TOL_REL_A_MANO` | ±1e-09 (relativa) | dossier §2.5: programa contra el cálculo a mano del verificador, la misma aritmética |
| medio último dígito impreso | 0.5·10^−k | los estadísticos (media, desviación) impresos a k decimales |

Juicios: «coincide» (dentro de la tolerancia), «difiere por método (declarado)» (fuera, con la diferencia de método escrita), «fuera de la tolerancia del dossier (explicado)» (fuera por menos que el redondeo de la propia tolerancia, con el programa igual al cálculo a mano y la razón escrita), «el programa se detiene (esperado)» (el caso adversarial: la excepción del programa es la esperada) y «DEFECTO» (ninguno de los anteriores). La suite exige cero defectos. En una tolerancia relativa la diferencia es relativa; en una absoluta, absoluta.

## 3. INDECI Piura — oráculo numérico, con y sin años FEN

| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | Juicio | Cita |
|---|---|---|---|---|---|---|---|
| estadísticos, con FEN (n = 38) | media μ | 30.5 | 30.49474 | -0.0053 | ±0.05 | coincide | Vol. II, Anexo 07.2, PDF 346 |
| estadísticos, con FEN (n = 38) | desviación σ (n − 1) | 40.68 | 40.68278 | +0.0028 | ±0.005 | coincide | Vol. II, Anexo 07.2, PDF 346 |
| estadísticos, con FEN (n = 38) | media de log10 P | 1.17 | 1.170498 | +0.0005 | ±0.0005 | coincide | Vol. II, Anexo 07.2, PDF 346 |
| estadísticos, con FEN (n = 38) | desviación de log10 P | 0.542 | 0.5422296 | +0.00023 | ±0.0005 | coincide | Vol. II, Anexo 07.2, PDF 346 |
| Δ de K-S, ec. (13), con FEN (n = 38) | Normal | 0.245 | 0.2447046 | -0.0003 | `TOL_D_INDECI` ±0.0005 | coincide | Vol. I, Cuadro N.º 22, PDF 128 (imp. 112) |
| Δ de K-S, ec. (13), con FEN (n = 38) | Log Normal | 0.059 | 0.05911852 | +0.00012 | `TOL_D_INDECI` ±0.0005 | coincide | Vol. I, Cuadro N.º 22, PDF 128 (imp. 112) |
| Δ de K-S, ec. (13), con FEN (n = 38) | Gumbel por momentos («Gumbel modificado») | 0.222 | 0.2218914 | -0.00011 | `TOL_D_INDECI` ±0.0005 | coincide | Vol. I, Cuadro N.º 22, PDF 128 (imp. 112) |
| P24(TR) Normal, con FEN (n = 38) | TR 2 | 30.49 | 30.49474 | +0.016 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 5 | 64.73 | 64.73423 | +0.007 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 10 | 82.64 | 82.63182 | -0.010 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 20 | 97.43 | 97.41196 | -0.019 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 25 | 101.73 | 101.7175 | -0.012 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 50 | 114.06 | 114.047 | -0.011 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 100 | 125.15 | 125.137 | -0.010 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 200 | 135.3 | 135.2866 | -0.010 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 500 | 147.6 | 147.5864 | -0.009 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Normal, con FEN (n = 38) | TR 1000 | 156.23 | 156.214 | -0.010 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 2 | 14.81 | 14.80806 | -0.013 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 5 | 42.34 | 42.34968 | +0.023 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 10 | 73.37 | 73.34886 | -0.029 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 20 | 115.5 | 115.448 | -0.045 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 25 | 131.82 | 131.7565 | -0.048 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 50 | 192.46 | 192.3542 | -0.055 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 100 | 270.49 | 270.3416 | -0.055 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 200 | 369.33 | 369.1383 | -0.052 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 500 | 538.65 | 538.4219 | -0.042 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Log Normal, con FEN (n = 38) | TR 1000 | 701.89 | 701.6389 | -0.036 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 5 | 59.77 | 59.76778 | -0.004 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 10 | 83.57 | 83.57244 | +0.003 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 20 | 106.4 | 106.4064 | +0.006 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 25 | 113.65 | 113.6497 | 0.000 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 50 | 135.96 | 135.9627 | +0.002 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 100 | 158.11 | 158.111 | +0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 200 | 180.18 | 180.1784 | -0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 500 | 209.29 | 209.2922 | +0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| P24(TR) Gumbel por momentos, con FEN (n = 38) | TR 1000 | 231.29 | 231.2957 | +0.002 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.2, PDF 347 |
| estadísticos, sin FEN (n = 32) | media μ | 18.6 | 18.63437 | +0.034 | ±0.05 | coincide | Vol. II, Anexo 07.1, PDF 338 |
| estadísticos, sin FEN (n = 32) | desviación σ (n − 1) | 21.66 | 21.65747 | -0.0025 | ±0.005 | coincide | Vol. II, Anexo 07.1, PDF 338 |
| estadísticos, sin FEN (n = 32) | media de log10 P | 1.037 | 1.037241 | +0.00024 | ±0.0005 | coincide | Vol. II, Anexo 07.1, PDF 338 |
| estadísticos, sin FEN (n = 32) | desviación de log10 P | 0.467 | 0.466972 | -2.8e-05 | ±0.0005 | coincide | Vol. II, Anexo 07.1, PDF 338 |
| Δ de K-S, ec. (13), sin FEN (n = 32) | Normal | 0.236 | 0.2361147 | +0.00011 | `TOL_D_INDECI` ±0.0005 | coincide | Vol. I, Cuadro N.º 21, PDF 127 (imp. 111) |
| Δ de K-S, ec. (13), sin FEN (n = 32) | Log Normal | 0.08 | 0.08038603 | +0.00039 | `TOL_D_INDECI` ±0.0005 | coincide | Vol. I, Cuadro N.º 21, PDF 127 (imp. 111) |
| Δ de K-S, ec. (13), sin FEN (n = 32) | Gumbel por momentos («Gumbel modificado») | 0.184 | 0.184136 | +0.00014 | `TOL_D_INDECI` ±0.0005 | coincide | Vol. I, Cuadro N.º 21, PDF 127 (imp. 111) |
| P24(TR) Normal, sin FEN (n = 32) | TR 2 | 18.63 | 18.63437 | +0.023 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 5 | 36.86 | 36.86177 | +0.005 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 10 | 46.39 | 46.38955 | -0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 20 | 54.27 | 54.25775 | -0.023 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 25 | 56.56 | 56.54981 | -0.018 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 50 | 63.12 | 63.11339 | -0.010 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 100 | 69.03 | 69.01719 | -0.019 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 200 | 74.43 | 74.42033 | -0.013 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 500 | 80.98 | 80.96809 | -0.015 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Normal, sin FEN (n = 32) | TR 1000 | 85.57 | 85.561 | -0.011 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 2 | 10.9 | 10.89535 | -0.043 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 5 | 26.93 | 26.93114 | +0.004 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 10 | 43.23 | 43.22051 | -0.022 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 20 | 63.9 | 63.87659 | -0.037 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 25 | 71.61 | 71.57519 | -0.049 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 50 | 99.19 | 99.1481 | -0.042 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 100 | 132.98 | 132.917 | -0.047 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 200 | 173.89 | 173.8126 | -0.045 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 500 | 240.67 | 240.5814 | -0.037 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Log Normal, sin FEN (n = 32) | TR 1000 | 302.29 | 302.199 | -0.030 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 5 | 34.22 | 34.21788 | -0.006 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 10 | 46.89 | 46.89028 | +0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 20 | 59.04 | 59.04596 | +0.010 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 25 | 62.9 | 62.9019 | +0.003 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 50 | 74.78 | 74.78024 | 0.000 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 100 | 86.57 | 86.57086 | +0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 200 | 98.32 | 98.31847 | -0.002 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 500 | 113.82 | 113.8172 | -0.002 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |
| P24(TR) Gumbel por momentos, sin FEN (n = 32) | TR 1000 | 125.53 | 125.5308 | +0.001 % | `TOL_P24_INDECI` ±0.1 % | coincide | Vol. II, Anexo 07.1, PDF 339 |

## 4. UNTumbes TU-107 — adversarial; su estadística es oráculo

| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | Juicio | Cita |
|---|---|---|---|---|---|---|---|
| estadísticos | media | 188.6725 | 188.6725 | -2.8e-14 | ±5e-05 | coincide | Tabla 28, p. 66 |
| estadísticos | desviación (n − 1) | 169.5565 | 169.5565 | -9.2e-06 | ±5e-05 | coincide | Tabla 28, p. 66 |
| estadísticos | media de ln P | 4.875 | 4.874973 | -2.7e-05 | ±5e-05 | coincide | Tabla 29, p. 67 |
| estadísticos | desviación de ln P | 0.8955 | 0.8954618 | -3.8e-05 | ±5e-05 | coincide | Tabla 29, p. 67 |
| Δ de K-S, ec. (13) | Normal | 0.1618 | 0.1617658 | -3.4e-05 | `TOL_D_UNTUMBES` ±5e-05 | coincide | Tabla 36, p. 74 |
| Δ de K-S, ec. (13) | Log Normal 2P | 0.0535 | 0.05351899 | +1.9e-05 | `TOL_D_UNTUMBES` ±5e-05 | coincide | Tabla 36, p. 74 |
| Δ de K-S, ec. (13) | Gumbel | 0.1074 | 0.1074212 | +2.1e-05 | `TOL_D_UNTUMBES` ±5e-05 | coincide | Tabla 36, p. 74 |
| P24(TR) Log Normal 2P | TR 5 | 278.23 | 278.2757 | +0.016 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 10 | 412.7 | 412.6307 | -0.017 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 20 | 571.46 | 571.2781 | -0.032 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 25 | 628.29 | 628.0658 | -0.036 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 50 | 824.21 | 823.8811 | -0.040 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 70 | 930.62 | 930.2483 | -0.040 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 100 | 1052.08 | 1051.663 | -0.040 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 140 | 1175.25 | 1174.798 | -0.038 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 200 | 1315.4 | 1314.918 | -0.037 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| P24(TR) Log Normal 2P | TR 500 | 1724.28 | 1723.748 | -0.031 % | `TOL_P24_UNTUMBES` ±0.05 % | coincide | Tabla 47, p. 80 (XT', antes del 1.13) |
| Témez, ec. (30) | C-1 | 0.46 | 0.4610946 | +0.0011 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-2 | 1.02 | 1.017705 | -0.0023 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-3 | 0.84 | 0.8399944 | -5.6e-06 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-4 | 0.51 | 0.5117324 | +0.0017 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-5 | 1.05 | 1.047066 | -0.0029 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-6 | 7.17 | 7.176713 | +0.0067 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-7 | 3.25 | 3.2513 | +0.0013 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-8 | 0.28 | 0.2799701 | -3e-05 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-9 | 0.82 | 0.8134172 | -0.0066 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-10 | 0.52 | 0.5252385 | +0.0052 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-11 | 0.43 | 0.4274154 | -0.0026 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-12 | 0.67 | 0.6765404 | +0.0065 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-13 | 4.66 | 4.652699 | -0.0073 | `TOL_TC_UNTUMBES` ±0.007 h | fuera de la tolerancia del dossier (explicado) | Tabla 27, p. 65 |
| Témez, ec. (30) | C-14 | 0.59 | 0.5851487 | -0.0049 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-15 | 0.76 | 0.7638397 | +0.0038 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-16 | 3.77 | 3.774643 | +0.0046 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-17 | 3.15 | 3.154794 | +0.0048 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-18 | 0.56 | 0.5616208 | +0.0016 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-19 | 0.32 | 0.3152508 | -0.0047 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-20 | 0.2 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNTUMBES` ±0.007 h | el programa se detiene (esperado) | Tabla 27, p. 65 |
| Témez, ec. (30) | C-21 | 0.65 | 0.6510423 | +0.001 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-22 | 1.03 | 1.024969 | -0.005 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-23 | 0.54 | 0.5395817 | -0.00042 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-24 | 1.53 | 1.527899 | -0.0021 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-25 | 0.77 | 0.771347 | +0.0013 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-26 | 0.49 | 0.4917644 | +0.0018 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-27 | 0.25 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNTUMBES` ±0.007 h | el programa se detiene (esperado) | Tabla 27, p. 65 |
| Témez, ec. (30) | C-28 | 0.87 | 0.8700224 | +2.2e-05 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-29 | 0.35 | 0.3499448 | -5.5e-05 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-30 | 0.38 | 0.3843019 | +0.0043 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-31 | 0.38 | 0.3818889 | +0.0019 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-32 | 0.45 | 0.4465021 | -0.0035 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-33 | 0.26 | 0.2580661 | -0.0019 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-34 | 1.68 | 1.685598 | +0.0056 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-35 | 2.49 | 2.487605 | -0.0024 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-36 | 0.91 | 0.9125709 | +0.0026 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-37 | 0.48 | 0.4771724 | -0.0028 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-38 | 0.68 | 0.6816292 | +0.0016 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-39 | 0.29 | 0.2947159 | +0.0047 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-40 | 0.9 | 0.901449 | +0.0014 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |
| Témez, ec. (30) | C-41 | 0.58 | 0.5804289 | +0.00043 | `TOL_TC_UNTUMBES` ±0.007 h | coincide | Tabla 27, p. 65 |

Fuera de la tolerancia del dossier, *C-13*: la tesis imprime 4.66 h; con la longitud y las cotas de su Tabla 26 la ec. (30) da 4.6527 h, que es tambien el calculo a mano del verificador (4.652699 h en su `salida_esperada.json`). El ±0.007 h del dossier es su desvio maximo redondeado a tres decimales, y esta es la fila de ese maximo (0.0073 h, 0.16 %). La tolerancia no se ensancha para que pase.

## 5. UNSAAC Roquepata — oráculo de Gumbel, Dick-Peschke y Témez

| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | Juicio | Cita |
|---|---|---|---|---|---|---|---|
| estadísticos | media | 23.43 | 23.428 | -0.002 | ±0.005 | coincide | Tabla 6.6, PDF 102 (imp. 90) |
| estadísticos | desviación (n − 1) | 13.11 | 13.11194 | +0.0019 | ±0.005 | coincide | Tabla 6.6, PDF 102 (imp. 90) |
| P24(TR) Gumbel por momentos | TR 10 | 40.5334 | 40.53478 | +0.003 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 30 | 52.1259 | 52.12775 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 35 | 53.7268 | 53.72874 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 70 | 60.8874 | 60.88965 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 100 | 64.556 | 64.55833 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 150 | 68.7183 | 68.72085 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 200 | 71.668 | 71.6706 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 250 | 73.9544 | 73.95709 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 500 | 81.0509 | 81.05389 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| P24(TR) Gumbel por momentos | TR 1000 | 88.1423 | 88.14556 | +0.004 % | `TOL_P24_UNSAAC` ±0.01 % | coincide | Tabla 6.7, PDF 104 (imp. 92) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 5 min | 118.07 | 118.0619 | -0.0081 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 10 min | 70.21 | 70.20002 | -0.01 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 15 min | 51.8 | 51.79273 | -0.0073 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 20 min | 41.74 | 41.74118 | +0.0012 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 25 min | 35.31 | 35.30874 | -0.0013 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 30 min | 30.8 | 30.79614 | -0.0039 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 35 min | 27.44 | 27.43381 | -0.0062 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 10, d = 40 min | 24.82 | 24.81945 | -0.00055 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 5 min | 151.84 | 151.8521 | +0.012 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 10 min | 90.28 | 90.29181 | +0.012 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 15 min | 66.61 | 66.61621 | +0.0062 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 20 min | 53.68 | 53.68783 | +0.0078 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 25 min | 45.41 | 45.41438 | +0.0044 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 30 min | 39.61 | 39.61023 | +0.00023 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 35 min | 35.28 | 35.28558 | +0.0056 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 30, d = 40 min | 31.92 | 31.92298 | +0.003 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 5 min | 156.5 | 156.5128 | +0.013 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 10 min | 93.06 | 93.06309 | +0.0031 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 15 min | 68.66 | 68.66083 | +0.00083 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 20 min | 55.33 | 55.33564 | +0.0056 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 25 min | 46.81 | 46.80826 | -0.0017 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 30 min | 40.82 | 40.82597 | +0.006 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 35 min | 36.37 | 36.36859 | -0.0014 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 35, d = 40 min | 32.9 | 32.90277 | +0.0028 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 5 min | 177.36 | 177.3696 | +0.0096 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 10 min | 105.46 | 105.4646 | +0.0046 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 15 min | 77.81 | 77.81049 | +0.00049 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 20 min | 62.71 | 62.70961 | -0.00039 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 25 min | 53.04 | 53.04587 | +0.0059 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 30 min | 46.26 | 46.26639 | +0.0064 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 35 min | 41.21 | 41.21503 | +0.005 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 70, d = 40 min | 37.29 | 37.28736 | -0.0026 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 5 min | 188.05 | 188.0601 | +0.01 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 10 min | 111.81 | 111.8212 | +0.011 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 15 min | 82.5 | 82.50033 | +0.00033 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 20 min | 66.49 | 66.48928 | -0.00072 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 25 min | 56.24 | 56.24309 | +0.0031 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 30 min | 49.05 | 49.05499 | +0.005 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 35 min | 43.7 | 43.69916 | -0.00084 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 100, d = 40 min | 39.53 | 39.53476 | +0.0048 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 5 min | 256.75 | 256.7475 | -0.0025 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 10 min | 152.67 | 152.663 | -0.007 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 15 min | 112.64 | 112.6329 | -0.0071 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 20 min | 90.78 | 90.77394 | -0.0061 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 25 min | 76.79 | 76.7854 | -0.0046 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 30 min | 66.97 | 66.97192 | +0.0019 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 35 min | 59.66 | 59.65992 | -8.4e-05 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Dick-Peschke, ec. (16), con la P24 impresa | TR 1000, d = 40 min | 53.98 | 53.97451 | -0.0055 | `TOL_I_UNSAAC` ±0.02 mm/h | coincide | Tabla 6.8, PDF 106 (imp. 94) |
| Témez, ec. (30) | A1 | 24.18 | 24.17752 | -0.0025 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A2 | 22.19 | 22.18778 | -0.0022 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A3 | 17.93 | 17.93301 | +0.003 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A4 | 21.07 | 21.07292 | +0.0029 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A5 | 17.26 | 17.2636 | +0.0036 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A6 | 15.95 | 15.94694 | -0.0031 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A7 | 15.57 | 15.57351 | +0.0035 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A8 | 12.44 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A9 | 12.74 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A10 | 9.02 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A11 | 7.81 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A12 | 8.48 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A13 | 13.63 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A14 | 16.23 | 16.23201 | +0.002 | `TOL_TC_UNSAAC` ±0.005 min | coincide | Tabla 6.5, PDF 99-100 (imp. 87-88) |
| Témez, ec. (30) | A15 | 11.51 | MetodoNoEvaluableError: Témez da un Tc bajo 0.25 h y el Manual la acota a 0.25-24 h (núm. 3.12.2.1) | — | `TOL_TC_UNSAAC` ±0.005 min | el programa se detiene (esperado) | Tabla 6.5, PDF 99-100 (imp. 87-88) |

## 6. UPAO La Jalca — oráculo de la estadística (series A y B)

| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | Juicio | Cita |
|---|---|---|---|---|---|---|---|
| serie A: Δ de K-S, ec. (13) | Normal | 0.1591 | 0.1590601 | -4e-05 | `TOL_D_UPAO` ±5e-05 | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Normal | TR 10 | 59.72 | 59.71782 | -0.0022 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Normal | TR 50 | 71.56 | 71.55269 | -0.0073 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Normal | TR 100 | 75.74 | 75.7306 | -0.0094 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Normal | TR 175 | 78.85 | 78.84131 | -0.0087 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Normal | TR 500 | 84.19 | 84.18782 | -0.0022 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: Δ de K-S, ec. (13) | Log Normal | 0.1149 | 0.1149494 | +4.9e-05 | `TOL_D_UPAO` ±5e-05 | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Log Normal | TR 10 | 56.9 | 56.89249 | -0.0075 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Log Normal | TR 50 | 72.52 | 72.50556 | -0.014 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Log Normal | TR 100 | 79.0 | 78.98594 | -0.014 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Log Normal | TR 175 | 84.2 | 84.18436 | -0.016 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Log Normal | TR 500 | 93.94 | 93.93103 | -0.009 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: Δ de K-S, ec. (13) | Gumbel | 0.1032 | 0.1032448 | +4.5e-05 | `TOL_D_UPAO` ±5e-05 | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Gumbel | TR 10 | 60.07 | 60.07217 | +0.0022 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Gumbel | TR 50 | 79.81 | 79.8089 | -0.0011 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Gumbel | TR 100 | 88.15 | 88.15271 | +0.0027 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Gumbel | TR 175 | 94.86 | 94.86604 | +0.006 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie A: P24(TR) Gumbel | TR 500 | 107.43 | 107.434 | +0.004 | `TOL_P24_UPAO_A` ±0.02 mm | coincide | Cuadro N.º 19, PDF 93 (imp. 73) |
| serie B: estadísticos | media | 36.81 | 36.80588 | -0.0041 | ±0.005 | coincide | PDF 114 (imp. 94) |
| serie B: estadísticos | desviación (n − 1) | 7.87 | 7.868805 | -0.0012 | ±0.005 | coincide | PDF 114 (imp. 94) |
| serie B: XT' Gumbel por momentos | TR 2 | 35.5133 | 35.51367 | +0.001 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |
| serie B: XT' Gumbel por momentos | TR 5 | 42.4672 | 42.46783 | +0.001 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |
| serie B: XT' Gumbel por momentos | TR 10 | 47.0712 | 47.07209 | +0.002 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |
| serie B: XT' Gumbel por momentos | TR 25 | 52.8885 | 52.88959 | +0.002 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |
| serie B: XT' Gumbel por momentos | TR 50 | 57.2041 | 57.20534 | +0.002 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |
| serie B: XT' Gumbel por momentos | TR 100 | 61.4878 | 61.48923 | +0.002 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |
| serie B: XT' Gumbel por momentos | TR 500 | 71.3868 | 71.38863 | +0.003 % | `TOL_XT_UPAO_B` ±0.005 % | coincide | PDF 115 (imp. 95) |

## 7. UPeU Colpahuayco — contraste de método (el K de Témez)

| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | Juicio | Cita |
|---|---|---|---|---|---|---|---|
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-01 | 1.04 | 1.038513 | -0.0015 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-02 | 1.03 | 1.033193 | +0.0032 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-03 | 1.05 | 1.04874 | -0.0013 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-04 | 1.06 | 1.060439 | +0.00044 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-05 | 1.05 | 1.054473 | +0.0045 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-06 | 1.06 | 1.063195 | +0.0032 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-08 | 1.08 | 1.089711 | +0.0097 | `TOL_K_UPEU` ±0.006 | difiere por método (declarado) | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-09 | 1.05 | 1.058437 | +0.0084 | `TOL_K_UPEU` ±0.006 | difiere por método (declarado) | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-10 | 1.02 | 1.019383 | -0.00062 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-11 | 1.02 | 1.02179 | +0.0018 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-12 | 1.04 | 1.036636 | -0.0034 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez, ec. (31), con la «s» del cauce (entrada de MH) | MC-13 | 1.02 | 1.024303 | +0.0043 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; L y s de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-01 | 1.04 | 1.037999 | -0.002 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-02 | 1.03 | 1.032906 | +0.0029 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-03 | 1.05 | 1.046425 | -0.0036 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-04 | 1.06 | 1.055197 | -0.0048 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-05 | 1.05 | 1.0505 | +0.0005 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-06 | 1.06 | 1.060432 | +0.00043 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-08 | 1.08 | 1.076396 | -0.0036 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-09 | 1.05 | 1.05461 | +0.0046 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-10 | 1.02 | 1.019043 | -0.00096 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-11 | 1.02 | 1.022983 | +0.003 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-12 | 1.04 | 1.036042 | -0.004 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |
| K de Témez con la «S» de la microcuenca (la que usó el documento) | MC-13 | 1.02 | 1.025187 | +0.0052 | `TOL_K_UPEU` ±0.006 | coincide | Tabla 8, p. 20; S de la Tabla 6, p. 18 |

Diferencias de método declaradas:

- *MC-08, MC-09*: el documento calculó Témez con la pendiente de la microcuenca (fila «S» de su Tabla 6), no con la del cauce mayor que la ec. (30) pide (fila «s»): con «S» el K coincide (dossier §6.2).

## 8. ESPOL Intervalles — contraste de método del K-S

| Pieza | Qué | Publicado | Programa | Diferencia | Tolerancia | Juicio | Cita |
|---|---|---|---|---|---|---|---|
| Dmax de K-S, La Argelia | Normal | 0.10209 | 0.1020943 | +4.3e-06 | `TOL_D_ESPOL` ±0.0001 | coincide | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, La Argelia | Gumbel | 0.0896 | 0.08963484 | +3.5e-05 | `TOL_D_ESPOL` ±0.0001 | coincide | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, La Argelia | Log Normal | 0.07205 | 0.06888291 | -0.0032 | `TOL_D_ESPOL` ±0.0001 | difiere por método (declarado) | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Gonzanama | Normal | 0.09365 | 0.09365075 | +7.5e-07 | `TOL_D_ESPOL` ±0.0001 | coincide | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Gonzanama | Gumbel | 0.06861 | 0.06855824 | -5.2e-05 | `TOL_D_ESPOL` ±0.0001 | coincide | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Gonzanama | Log Normal | 0.06859 | 0.05996226 | -0.0086 | `TOL_D_ESPOL` ±0.0001 | difiere por método (declarado) | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Malacatos | Normal | 0.08111 | 0.08948228 | +0.0084 | `TOL_D_ESPOL` ±0.0001 | difiere por método (declarado) | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Malacatos | Gumbel | 0.08131 | 0.0786599 | -0.0027 | `TOL_D_ESPOL` ±0.0001 | difiere por método (declarado) | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Malacatos | Log Normal | 0.07291 | 0.07087844 | -0.002 | `TOL_D_ESPOL` ±0.0001 | difiere por método (declarado) | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Catamayo | Normal | 0.23595 | 0.2359512 | +1.2e-06 | `TOL_D_ESPOL` ±0.0001 | coincide | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Catamayo | Gumbel | 0.16758 | 0.1676234 | +4.3e-05 | `TOL_D_ESPOL` ±0.0001 | coincide | Anexos 3 a 6, PDF 96-98 |
| Dmax de K-S, Catamayo | Log Normal | 0.15415 | 0.1671934 | +0.013 | `TOL_D_ESPOL` ±0.0001 | difiere por método (declarado) | Anexos 3 a 6, PDF 96-98 |

Diferencias de método declaradas:

- *La Argelia Log Normal, Gonzanama Log Normal, Catamayo Log Normal*: Hydrognomon estima la Log Normal de otra forma que el núm. 3.7.1.2 (logaritmos, n − 1).
- *Malacatos Normal, Malacatos Gumbel, Malacatos Log Normal*: con las otras tres estaciones cuadrando, la serie impresa en el Anexo 2 no es exactamente la que entró a Hydrognomon (dossier §7).

## 9. Las detenciones: qué hace el programa con la entrada defectuosa

| Caso | Entrada | Esperada | Obtenida | Por qué |
|---|---|---|---|---|
| INDECI Piura | `serie_sin_fen`, TR 25 | MetodoNoEvaluableError | MetodoNoEvaluableError | sin FEN da menos lluvia que la serie completa: la hoja de ruta manda adoptar la más conservadora (ficha T1-09); INDECI tomó la serie con FEN «por criterio conservador» |
| INDECI Piura | variante con los 5 años FEN del Anexo 07.3, `serie_sin_fen` | MetodoNoEvaluableError | MetodoNoEvaluableError | la declaración de años FEN mueve la lluvia sin FEN, no la adoptada |
| INDECI Piura | `dos_poblaciones` | MetodoNoEvaluableError | MetodoNoEvaluableError | ninguna fuente da el procedimiento de población mixta |
| INDECI Piura | sin declarar `homogeneidad_serie_fen` | CriterioPendienteError | CriterioPendienteError | sin decidir qué se hace con los años FEN no hay serie que ajustar |
| INDECI Piura | `normal` declarada | MetodoNoEvaluableError | MetodoNoEvaluableError | no pasa K-S: D ≥ d crítico (0.2154, cuantil exacto n = 38) |
| INDECI Piura | `gumbel` declarada | MetodoNoEvaluableError | MetodoNoEvaluableError | no pasa K-S: D ≥ d crítico |
| UNTumbes TU-107 | la serie como se publica (`fen` vacío) | DatoFaltanteError (`fen`) | DatoFaltanteError (`fen`) | la tesis no declara años FEN, y una celda vacía no se lee como «no»: es la guardia que de verdad protege aquí |
| UNTumbes TU-107 | la fila de 2002 rotulada 1989 (la misma etiqueta de año dos veces) | DatoInvalidoError (`anio`) | DatoInvalidoError (`anio`) | un máximo anual por año: el dato está y contradice a otro |
| UNSAAC Roquepata | `lognormal_2p` declarada | MetodoNoEvaluableError | MetodoNoEvaluableError | no pasa K-S: D ≥ 0.26 (Tabla N.º 03, n = 25) |
| UPAO La Jalca | ALC-19 con Kirpich, por omisión | MetodoNoEvaluableError | MetodoNoEvaluableError | S = 21.1 %, fuera de la población de Kirpich (3 a 10 %, Tabla N.º 05); la salida es otra fórmula, `indicador_con_aviso` o el caudal declarado |
| UPeU Colpahuayco | MC-07 (≥ 10 km², racional modificado) | DatoFaltanteError (`CN`) | DatoFaltanteError (`CN`) | el documento no publica el CN; va vacío a propósito |
| UPeU Colpahuayco | MC-14 (≥ 10 km², racional modificado) | DatoFaltanteError (`CN`) | DatoFaltanteError (`CN`) | el documento no publica el CN; va vacío a propósito |

## 10. Caudales: el documento (otro método) y el cálculo a mano

El caudal **no** se juzga contra el documento: es otro método (columna «por qué difiere»). Se juzga contra el cálculo a mano del verificador (`salida_esperada.json` de cada caso, sellado antes de correr el programa) con `TOL_REL_A_MANO`.

| Caso | Cuenca | TR | Magnitud | Documento | Programa | Programa / documento | A mano | ¿Coincide a mano? | Cita del documento |
|---|---|---|---|---|---|---|---|---|---|
| UNTumbes | C-1 | 35 | tc (min) | 26.81 | 27.66568 | 1.03 | 27.66568 | sí | Tabla 27, p. 65 (promedio con Bransby-Williams) |
| UNTumbes | C-1 | 35 | I (mm/h) | 280.28 | 580.8167 | 2.07 | 580.8167 | sí | Tabla 66, p. 92 |
| UNTumbes | C-1 | 35 | Q (m³/s) | 2.86 | 6.215005 | 2.17 | 6.215005 | sí | Tabla 66, p. 92 |
| UNTumbes | C-6 | 70 | Q (m³/s) | 1827.93 | 3751.955 | 2.05 | 3751.955 | sí | Tabla 67, p. 93 (hidrograma triangular, CN 62) |
| UNTumbes | C-6 | 70 | C | — | 0.915803 | — | 0.915803 | sí | no publicado |
| UNTumbes | C-7 | 70 | Q (m³/s) | 345.23 | 734.2562 | 2.13 | 734.2562 | sí | Tabla 67, p. 93 |
| UNTumbes | C-13 | 70 | Q (m³/s) | 372.98 | 835.2301 | 2.24 | 835.2301 | sí | Tabla 67, p. 93 |
| UNTumbes | C-16 | 70 | Q (m³/s) | 534.64 | 1131.18 | 2.12 | 1131.18 | sí | Tabla 67, p. 93 |
| UNTumbes | C-17 | 70 | Q (m³/s) | 345.99 | 771.4236 | 2.23 | 771.4236 | sí | Tabla 67, p. 93 |
| UNSAAC | A1 | 35 | tc (min) | 22.51 | 24.17752 | 1.07 | 24.17752 | sí | Tabla 6.5, PDF 99 (promedio) |
| UNSAAC | A1 | 35 | I (mm/h) | — | 47.99638 | — | 47.99638 | sí | no publicado |
| UNSAAC | A1 | 35 | Q (m³/s) | 5.2 | 5.675265 | 1.09 | 5.675265 | sí | Tabla 6.13, PDF 111 (imp. 99) |
| UPAO | ALC-19 | 50 | tc (min) | 14.27 | 14.27065 | 1 | 14.27065 | sí | PDF 139 (imp. 119) |
| UPAO | ALC-19 | 50 | I (mm/h) | 32.72327 | 75.88649 | 2.32 | 75.88649 | sí | PDF 139 (imp. 119) |
| UPAO | ALC-19 | 50 | Q (m³/s) | 3.99 | 9.229694 | 2.31 | 9.229694 | sí | PDF 140 (imp. 120) |
| UPeU | MC-01 | 70 | tc (min) | — | 37.77321 | — | 37.77321 | sí | no publicado |
| UPeU | MC-01 | 70 | I (mm/h) | 27.1 | 28.59115 | 1.06 | 28.59115 | sí | Tabla 8, p. 20 |
| UPeU | MC-01 | 70 | Q (m³/s) | 2.41 | 2.402045 | 0.997 | 2.402045 | sí | Tabla 8, p. 20 |

Por qué el documento da otro caudal:

- **UNTumbes.** IDF propia ajustada a la Tabla N.º 04 (1 a 24 h) y extrapolada a minutos, con el factor 1.13; tc promedio de Témez y Bransby-Williams; sobre 10 km² hidrograma triangular. MH: Dick-Peschke bajo 1 h, Témez solo, racional modificado desde 10 km².
- **UNSAAC.** tc promedio de Témez y Bransby-Williams e IDF de regresión sobre Dick-Peschke; MH: Témez solo, Dick-Peschke en tc y K (`gumbel` declarada como en la tesis).
- **UPAO.** IDF ajustada a la Tabla N.º 04 y evaluada a 14 min; MH: Dick-Peschke, que el núm. 3.8.1 manda bajo 1 h (Kirpich fuera de su población, con `indicador_con_aviso`).
- **UPeU.** P24 de Pearson III, I de la ec. (34) y C de un CN no publicado; MH: racional (ec. 28) con Dick-Peschke y el C del vehículo (0.30).

## 11. Hallazgos sobre MH: contrastes de método, sin cambiar el cálculo

Ninguno es un error numérico (dossier §8). Salvo H1, que desde la ficha VE3-19 de `docs/decisiones_diferidas.md` es un renglón del aviso de consistencia, quedan documentados aquí y el cálculo no cambia.

**H1. Filas copiadas entre años (UNTumbes).** Con un máximo por año la copia no es demostrable y dos máximos iguales son normales. Desde VE3-19 el aviso de consistencia sin umbral (paso 1b.3c) lista los máximos repetidos con sus años, sin detener, quitar ni juzgar. Para Cañaveral el programa imprime:

> Maximos anuales que se repiten en la serie registrada: 129.0 mm (1989 y 2002); 63.0 mm (1996 y 2001). El programa no distingue una coincidencia de un año copiado de otro, y no quita ni juzga ninguno: el proyectista tiene que contrastar esos años con el registro mensual o diario de origen (ficha VE3-19).

Y la misma etiqueta de año dos veces sigue siendo `DatoInvalidoError` (sección 9).

**H2. La guardia que protege en Tumbes es la celda `fen` obligatoria.** La serie como se publica no carga (sección 9). Una vez que alguien escribe «no» en toda la columna, sólo queda el aviso de que la serie no declara ningún año FEN.

**H3. Con la serie de Tumbes el programa entrega caudal, con aviso.** P24(70) = 930.2 mm (Log Normal 2P) y, en la quebrada Sapotal (C-6, 102.71 km²), Q70 = 3752 m³/s por el racional modificado. No se detiene: no hay umbral que inventar. Los avisos que acompañan a ese caudal:

- La serie de «Cañaveral» no es continua: entre 1983 y 2024 faltan 2 años (1988, 2022). El programa ajusta los años que hay y no rellena los que faltan; si entre ellos hay un año del fenomeno El Niño, la lluvia de diseño esta subestimada.
- El caudal de esta cuenca (102.71 km2) se calculo por el metodo racional modificado, que el Manual describe asi: «Es el método racional según la formulación propuesta por Témez (1987, 1991) adaptada para las condiciones climáticas de España.» (num. 3.12.2.1 · 'Método Racional Modificado' · pag. impresa 50 · PDF 53). El Manual lo adopta para el Peru sin decir como se adapto; el estudio hidrologico tiene que defender su uso en esta cuenca.

La defensa real es que el proyectista lea la memoria: un revisor externo esperará una detención.

**H4. El valor crítico de K-S no es 1.36/√n.** Los cuatro documentos peruanos usan 1.36/√n; MH usa la celda de la Tabla N.º 03 cuando n es fila y, si no, el cuantil exacto del mismo estadístico, que es más estricto. Conviene que la memoria lo diga, porque es lo que el revisor recalculará.

| Caso | Serie | n | d del documento | Cita | d del programa | De dónde sale |
|---|---|---|---|---|---|---|
| INDECI Piura | Miraflores sin FEN | 32 | 0.24 | Vol. I, Cuadro N.º 21 | 0.2342 | cuantil exacto 1 − alfa del estadistico de Kolmogorov-Smirnov para n = 32 y alfa = 0.05: la Tabla N 03 no tiene esa fila o esa columna, y este calculo reproduce sus 24 celdas impresas |
| INDECI Piura | Miraflores con FEN | 38 | 0.22 | Vol. I, Cuadro N.º 22 | 0.2154 | cuantil exacto 1 − alfa del estadistico de Kolmogorov-Smirnov para n = 38 y alfa = 0.05: la Tabla N 03 no tiene esa fila o esa columna, y este calculo reproduce sus 24 celdas impresas |
| UNTumbes TU-107 | Cañaveral | 40 | 0.215 | Tabla 36, p. 74 («1.36/√N») | 0.2100 | Tabla N 03, fila n = 40, columna alfa = 0.05 |
| UPAO La Jalca | Chachapoyas-A | 17 | 0.3298 | Cuadro N.º 19, PDF 93 | 0.3180 | cuantil exacto 1 − alfa del estadistico de Kolmogorov-Smirnov para n = 17 y alfa = 0.05: la Tabla N 03 no tiene esa fila o esa columna, y este calculo reproduce sus 24 celdas impresas |
| UPeU Colpahuayco | Sicuani | 28 | 0.257 | p. 19 | 0.2499 | cuantil exacto 1 − alfa del estadistico de Kolmogorov-Smirnov para n = 28 y alfa = 0.05: la Tabla N 03 no tiene esa fila o esa columna, y este calculo reproduce sus 24 celdas impresas |

Cambia un veredicto de los revisados: la Normal de Miraflores sin FEN (D = 0.2361) pasa con 0.24 y no pasa con 0.2342.

**H5. Dick-Peschke frente a la Tabla N.º 04 extrapolada bajo 1 h.** Para tc < 1 h MH da una intensidad del orden del doble que las tesis que extrapolan los coeficientes de la Tabla N.º 04 (válidos de 1 a 24 h): 2.32 veces en UPAO (ALC-19) y 2.07 en UNTumbes (C-1, y la tesis lleva además el factor 1.13). MH aplica lo que el núm. 3.8.1 manda para duraciones menores de 1 hora, y el criterio `relacion_intensidad_duracion` ya lo declara. Donde la tesis usa Dick-Peschke (UNSAAC), el caudal de MH queda entre +6.0 % y +10.5 % sobre el impreso en las ocho microcuencas que Témez deja evaluar (Tabla 6.13, PDF 111).

**H6. Las microcuencas pequeñas y empinadas no tienen, por omisión, fórmula de tc evaluable.** En UNSAAC 7 de 15 dan Témez bajo 0.25 h y 15 de 15 están fuera de la población de Kirpich; en UNTumbes, 2 de 41. El programa se detiene con `MetodoNoEvaluableError` y ofrece la salida (otra fórmula, `indicador_con_aviso` o el caudal declarado). Es la letra del Manual; en sierra es una limitación práctica que la guía de uso conviene que anticipe.

**H7. `serie_sin_fen` no es adoptable en costa norte.** En Miraflores la Log Normal a 25 años da 71.6 mm sin FEN y 131.8 mm con FEN (razón 1.84): `serie_sin_fen` se detiene con las dos declaraciones de años FEN (sección 9), que es la regla de la ficha T1-09 y la decisión de INDECI. En una estación con FEN extraordinario el criterio tiene un solo valor utilizable.

**H8. `mejor_ajuste_ks` puede elegir la Normal en una serie con quiebre.** Colquepata: la Normal da P24(35) = 48.37 mm, apenas sobre el máximo registrado (48.2 mm). El defecto es de la serie (inhomogénea), no de la regla; el aviso de consistencia deja a la vista el mínimo y el máximo.

**H9. El contrato no marca un año incompleto.** 1971 en Miraflores trae nueve meses y entra con 1.6 mm; quitarlo mueve la Log Normal a 25 años de 131.8 a 130.5 mm (-1.0 %). Menor.

## 12. Erratas de los documentos (dossier)

Ninguna afecta a los números que se usan de oráculo.

**INDECI Piura.**

- Cuadro 13, fila «Prom. S/Niños», ANUAL: imprime 42.5; la media sin Niños es 18.6 (su propio Anexo 07.1).
- Cuadro 13, fila «MAX S/Niños», ANUAL: imprime 107.1, que es 1992, año que el estudio trata como FEN; sería 103.5 (2002).
- Anexos 07.1 y 07.3: 1973 sale de «sin FEN» y no entra en «sólo FEN» (el estudio escribe «72/73» como un evento).
- Cuadro 22: Normal (0.245), Gumbel (0.254) y Gumbel modificado (0.222) superan el Δ tabular 0.22 y el texto no lo comenta.
- Vol. I PDF 125 (imp. 109), ítem e): repite «sin considerar los fenómenos El Niño»; por el Anexo 07.5 es «considerando».
- Figura 26, PDF 133: eje rotulado «Caudal m3/s» sobre curvas de precipitación.
- Cuadro 13, 1971: año parcial (abril a diciembre, máximo 1.6 mm) que entra en las dos series.
- La serie «sin FEN» conserva 1997 (54.0 mm, diciembre, inicio del FEN 97-98) y 2002 (103.5 mm).

**UNTumbes TU-107.**

- Tabla 23, p. 60: filas copiadas; 2002 = 1989 en los 12 meses y 2001 = 1996 en 11 de 12 (mayo: 11.00 frente a 11.10).
- Tabla 23: 14 celdas mensuales de 300 mm o más en 24 h (1983, 1987, 1991, 1992, 1997, 2000, 2017, 2023); el máximo de Miraflores en 38 años es 173.6 mm.
- El evento de 1998 aparece en «1997» (502 a 729 mm de enero a abril; «1998», 150 mm).
- No menciona El Niño, con 1983 y 1997-98 en la serie; faltan 1988 y 2022 (Tabla 22).
- Tabla 27: promedia Témez con Bransby-Williams y usa Témez bajo 0.25 h (C-20: 0.20 h; C-27: 0.25 h impreso, 0.246 h recalculado).
- Tablas 48 y 65: IDF ajustada a los coeficientes de la Tabla N.º 04 (1 a 24 h) y aplicada a duraciones de 11 a 60 min.

**UNSAAC Roquepata.**

- Tabla 6.7, título: dice «distribución normal»; el contenido es Gumbel.
- Tabla 6.13, encabezado: «T= 35 AÑOS» dos veces; la tercera columna es 70 años.
- PDF 100-101: dice 28 registros de 1990 a 2017; la serie llega a 2014 (25 años).
- Serie inhomogénea: 1990-1997 de 4.4 a 9.3 mm (media 6.54); 1998-2014 de 20.1 a 48.2 mm (media 31.38).
- PDF 103: afirma que el mejor ajuste es Gumbel; con el K-S del Manual es la Normal, y el anexo no se publicó.

**UPAO La Jalca.**

- Series A y B, 1973: 25.5 mm en la A y 27.0 en la B; en la tabla mensual 25.50 es junio y 27.00 abril: el máximo es 27.0.
- PDF 139 (imp. 119): escribe Kirpich con L^0.76; los 14.27 min impresos salen con 0.77, el exponente del Manual.
- PDF 115 (imp. 95), lluvia de 18 h a 25 años: 47.21 mm; sería 0.90 · 59.76 = 53.79, y contamina la regresión de TR 25.
- PDF 90 (imp. 70): anuncia «tres estaciones» y registros hasta 2003; hay una estación y la serie acaba en 2001.
- Alcantarilla 19: Kirpich con S = 21.1 %, fuera de la población de 3 a 10 %.

**UPeU Colpahuayco.**

- Tablas 6 y 8: las áreas no coinciden (0.97 km² frente a 113.89 ha; 0.20 frente a 25.57; 3.70 frente a 403.16).
- Tabla 8, columna Q: el K no entra en el caudal impreso (0.278·C·I·A sin K reproduce las filas 1, 9, 10, 11 y 13).
- Témez con la pendiente de la microcuenca, no la del cauce mayor (sección 7 de este documento).
- Ec. (1), p. 13: «R = 1 − (1 − T)^n»; es 1 − (1 − 1/T)^n.
- p. 15: «P0 = [(500/CN) – 50]»; el Manual escribe 5000/CN (ec. 35).
- Tabla 4, p. 14: Kirpich con 3.98 y unidad «h»; ese coeficiente da minutos.
- Tabla 8: C a 2 decimales (±1.7 %), lo que impide separar la fila 2 con K y sin K.

**ESPOL Intervalles.**

- Malacatos: el Dmax de Hydrognomon no corresponde a la serie impresa en el Anexo 2 (las otras tres estaciones cuadran).

## 13. Resumen

- **INDECI Piura** (oráculo numérico de piezas): 72 contrastes — 72 «coincide»; 0 «difiere por método (declarado)»; 0 «fuera de la tolerancia del dossier (explicado)»; 0 «el programa se detiene (esperado)»; 0 «DEFECTO».
- **UNTumbes TU-107** (adversarial (y oráculo de la estadística)): 58 contrastes — 55 «coincide»; 0 «difiere por método (declarado)»; 1 «fuera de la tolerancia del dossier (explicado)»; 2 «el programa se detiene (esperado)»; 0 «DEFECTO».
- **UNSAAC Roquepata** (oráculo numérico de piezas): 75 contrastes — 68 «coincide»; 0 «difiere por método (declarado)»; 0 «fuera de la tolerancia del dossier (explicado)»; 7 «el programa se detiene (esperado)»; 0 «DEFECTO».
- **UPAO La Jalca** (oráculo numérico de piezas): 27 contrastes — 27 «coincide»; 0 «difiere por método (declarado)»; 0 «fuera de la tolerancia del dossier (explicado)»; 0 «el programa se detiene (esperado)»; 0 «DEFECTO».
- **UPeU Colpahuayco** (contraste de método): 24 contrastes — 22 «coincide»; 2 «difiere por método (declarado)»; 0 «fuera de la tolerancia del dossier (explicado)»; 0 «el programa se detiene (esperado)»; 0 «DEFECTO».
- **ESPOL Intervalles** (descartable para el caudal; contraste de método del K-S): 12 contrastes — 6 «coincide»; 6 «difiere por método (declarado)»; 0 «fuera de la tolerancia del dossier (explicado)»; 0 «el programa se detiene (esperado)»; 0 «DEFECTO».
- **Detenciones:** 12 de 12 con la excepción esperada.
- **Caudales contra el cálculo a mano:** 18 de 18 dentro de `TOL_REL_A_MANO`.
- **Defectos del programa: 0.** Ningún caso valida el caudal de punta a punta.
