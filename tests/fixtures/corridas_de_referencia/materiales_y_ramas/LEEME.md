# DATOS DE PRUEBA, NO DEL PROYECTO

Esta carpeta es la cuarta corrida de referencia del índice de fórmulas
(`src/indice_formulas.py::CORRIDAS_DE_REFERENCIA`, VE-7 lote C, ítem C6;
ficha VE5GUI-47). **Ningún valor es del proyecto**: se escribieron para que la
corrida recorra las ramas que las otras tres no alcanzan. El CSV de puntos y
los JSON no admiten esta cabecera; vale para los siete archivos.

| Archivo / punto | Qué ejercita |
|---|---|
| `declaraciones.json` · `D_max_catalogo` = 0.75 m para el concreto | el concreto queda fuera del catálogo: los puntos de Familia A se dimensionan en TMC o HDPE y llegan a la Fase 8 de esos materiales (`F8.TMC_*`, `F8.HDPE_*`) |
| `declaraciones.json` · `perfil_hdpe_fabricante` | el perfil del HDPE con los mínimos de AASHTO M 294 (traducción no oficial), como en `tests/test_t5_correcciones_auditoria.py` |
| A-01 (TMC Ø 1.20 m) · `material_lecho_salida`, `duracion_caudal_pico_min` | la hoya de socavación de HEC-14 Cap. 5 y el filtro bajo el enrocado (`F6.SOCAVACION`, `F6.FILTRO`); desde N3 (plan 12), `D85_m` = 0.032 y `D15_m` = 0.001 m, el suelo del Ejemplo 1 de HEC-11 (PDF 61), dan el filtro granular (`F6.FILTRO_GRANULAR`) |
| A-01 · `estabilidad_global_declarada` | E4 y E5 con el FS declarado del EMS (`F9.GLOBAL_DECLARADA`) |
| A-01 · cabezal en voladizo de la regla | la pantalla crece por su armado (`F9.DIMENSIONADO_PANTALLA`) |
| A-02 · `pH` = 4.0 | el TMC sale de los candidatos por durabilidad y el punto se dimensiona en HDPE |
| A-02 · `cabezal_declarado.tipo` = `gravedad_ciclopeo`, `S_conducto` = 0 | el cabezal de gravedad en concreto ciclópeo (`F9.CICLOPEO`) y el barril horizontal (`F4.HORIZONTAL`) |
| A-03 · `Q_m3s` vacío, cuenca de 55.9 km² en `cuencas.csv` | el método racional modificado de la Fase 1-bis (`FH.RM_INTENSIDAD`, `FH.RM_C`, `FH.RM_CAUDAL`); con ese caudal el punto no cabe |
| A-03 · `sucs_fundacion` = OH | el aviso de suelo de fundación deficiente para un conducto que no es marco (`F3.DUR.SUELO_FUNDACION`) |
| C-01 · `n_manning_cajon` = (0.013, 0.016) | el par del encofrado de un marco vaciado in situ (`F4.N_CAJON_IN_SITU`) |
| `externos.json` · `licuefaccion_ems`, `declaraciones.json` · `Mw_licuefaccion` | la Fase 0-bis con el resultado del EMS declarado (`F0.LICUEFACCION`) |
| `declaraciones.json` · `exposicion_quimica_ems` (SO₄ 0.15 %), `incremento_acero_por_despiece`, `clase_concreto_losa_entrega` | la fila A7 del armado por durabilidad (`F9.ARM_DURABILIDAD`) y el metrado del acero (`F11.ACERO`) |

La corrida ejercita fórmulas y no es un diseño: varias filas del cabezal no cumplen
(A7 de A-01 y C-01, el ciclópeo declarado de A-02, las sísmicas E1/E3, y en C-01 también
`A2.losa_inferior_1_{derecha,izquierda}.exterior` de la Fase 8, heredado del marco de
`hidrologia_calculada`), y se dejan así: el rótulo de la corrida dice «NO ES UN DISEÑO VÁLIDO».

`estacion.csv` es la serie SINTÉTICA de T-1 (copia de la de `hidrologia_calculada`).
`cuencas.csv` es la cuenca sintética de `tests/fixtures/hidrologia/cuencas_racional_modificado_prueba.csv`
con el id A-03. Lo que esta corrida NO ejercita, y por qué, está en la ficha VE7C-06 de
`docs/decisiones_diferidas.md`.
