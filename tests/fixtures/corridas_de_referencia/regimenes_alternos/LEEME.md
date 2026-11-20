# DATOS DE PRUEBA, NO DEL PROYECTO

Esta carpeta es la quinta corrida de referencia del índice de fórmulas
(`src/indice_formulas.py::CORRIDAS_DE_REFERENCIA`, VE-7 lote C, dictamen Fable
del 2026-11-20, abierto (i-c)). **Ningún valor es del proyecto y la corrida NO ES
UN DISEÑO VÁLIDO**: ejercita fórmulas. Parte del juego de la validación integral
de T-11 con el caudal DECLARADO (`tests/apoyo/validacion_integral.py::juego_completo`,
materializado) y cambia los criterios que valen para TODA la corrida, a los
regímenes alternos que las otras cuatro no recorren, más tres puntos dedicados.
El CSV y los JSON no admiten esta cabecera; vale para los cinco archivos.

| Dato | Qué ejercita |
|---|---|
| `remanso_derecho_via` = perfil paso a paso, `sobreelevacion_admisible_remanso_m`, `seccion_cauce_aproximacion` por punto y `ancho_derecho_via_m` = 200 | V5 por el perfil de remanso (`F5.V5_PERFIL`), con los datos de `tests/test_ve4c_v5_remanso.py` |
| `umbral_no_colapso_evento_extremo` = desborde admitido, `caudal_unitario_admisible_desborde_m2s`, `longitud_cresta_desborde_m`, Q extremo de A-01 = 2.3 m³/s | V8 con el reparto del desborde (`F5.V8.DESBORDE`), como «de punta a punta» de `tests/test_ve4d_v8_desborde.py` |
| `n_manning_cajon` = `concreto_afinado` | la fila de la Tabla Nº 09 por analogía para el marco de C-01 (`F4.N_CAJON`) |
| `region_natural` = selva alta (`sitio.json`) | la rama de selva alta del TMC (`F3.SELVA_ALTA_TMC`): la emite el TMC de A-06, que se evalúa porque el concreto no cierra |
| A-03 (el E07 de `tests/fixtures/ve3_13_gobierno_receptor/`, TW = 1.0 m) | el diámetro gobernado por el nivel del receptor (`F5.V1.RECEPTOR`) |
| A-04 (receptor 3.8 m bajo la entrada, S = 0.001, lecho no cohesivo) | la salida colgada con la caída recta de HEC-14 Cap. 11 (`F6.CAIDA`, `F6.CAIDA_ESTANQUE`) |
| A-05 (entrada a 40.45, relleno somero) y `carga_viva_tubo_concreto_somero` | la cobertura mínima con relleno por debajo del dominio de la rueda distribuida (`F8.COBERTURA`) |
| A-06 (Q = 0.02 m³/s, S = 0.09) | el piso de la carga de control de entrada cuando Ks·S la anula (`F4.PISO_HW`, elección); el punto no cierra (V2) |
| `licuefaccion_ems`, `Mw_licuefaccion`, `incremento_acero_por_despiece`, `clase_concreto_losa_entrega` | quitar bloqueos que no son el objeto de esta corrida |

La corrida ejercita fórmulas y no es un diseño: no cumplen `A2` del pórtico de C-01 y, en
A-04, el deslizamiento sísmico de la franja extrema de los aleros de salida
(`E3-LRFD.sis.s.alero.100`: su zapata llega al tope 1.5·H_c), y se dejan así
(`NO_CUMPLE_EN_LA_QUINTA`, ficha VE7C-06).

Lo que esta corrida NO alcanza, con su razón medida, está en el censo
`SIN_EJERCITAR` de `tests/test_ve7_lote_c_cuarta_corrida.py` y en la ficha VE7C-06.
