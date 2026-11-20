# Sensibilidad de los criterios adoptados sobre el juego de prueba (T-11)

> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe `python -m tests.apoyo.sensibilidad --escribir` y `tests/test_t11_sensibilidad.py` lo regenera y lo compara. Cada barrido es `src/barrido.py` (PF-3) sobre el juego de **DATOS DE PRUEBA, NO DEL PROYECTO** de la validación integral, a `--alcance expediente`. **Ningún valor de archivo cambia**: un barrido declara cada valor para su corrida y deja el proceso como estaba.

## 1. Cómo leer este anexo

- **La base de los barridos es el juego tal como está**, la variante que ejercita el empuje sísmico reducido (`docs/validacion_integral.md` §2.1), y **no la corrida titular** (§2, con la decisión de archivo del muro que no cede): con k_h = k_h0 la condición sísmica del cabezal no cumple en ningún cabezal del juego, y hace falta una base donde el cabezal cierre para medir los [A] del cabezal. Lo que la decisión de archivo hace se lee en su propio barrido (`factor_muro_eleccion`); el trasdós es drenado de archivo desde VE-3.16, y el otro lado se lee en el barrido de `drenaje_trasdos`.
- **Primer valor = el efectivo en el juego** (el que el juego declara o el de archivo): su corrida es la del juego, y cada otra se compara con ella por el comparador de E-B. Los demás valores son los extremos de la ventana del criterio (`Criterio.sensibilidad`), o sus otras opciones.
- **MUEVE EL DISEÑO**: algún punto cambia de material o de sección, o deja de dimensionar. **MUEVE VEREDICTOS**: cambia el veredicto de alguna verificación del conducto, del cabezal o de la Fase 10. **MUEVE EL HW**: sólo cambia la carga que gobierna, en más de 5e-05 m (media unidad de la cuarta cifra con que se imprime). **LEÍDO, SIN EFECTO MEDIBLE** quiere decir que la corrida lee el criterio y que no cambian ni el material, ni la sección, ni ningún veredicto, ni el HW que gobierna: **las demás magnitudes no se comparan** (la hoya de socavación, el espesor y la longitud de la protección, las longitudes, los márgenes, el armado), y pueden cambiar. **NO LO LEE LA CORRIDA**: la clave no está entre los criterios usados de ninguna corrida del barrido, y barrerla no mueve nada en ESTE juego (la razón, en la tabla).
- **La lista se deriva del censo**: se barre todo criterio con valor efectivo en el juego y ventana legible por máquina (una categoría cerrada o dos extremos numéricos), más los que necesitan valores propios. Los que no se barren están en §5, **por nombre y con su razón**. Un barrido mide UNA clave a la vez, sobre UN juego: no es el producto cartesiano ni dice nada de otro sitio.

## 2. Resumen

| Grupo | Criterio | Etiqueta | Ventana | Valores barridos | Base | Efecto | Detalle |
|---|---|---|---|---|---|---|---|
| conducto | `HW_D_max` | [A] | 1.2–1.5 | 1.5, 1.2 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `borde_libre_bajo_tw_ahogante` | [A] | no_cumple / aviso | 'no_cumple', 'aviso' | juego | NO LO LEE LA CORRIDA | el TW del juego (0.30 m sobre el fondo de la salida; 0.41 m en C-01) no supera el llenado admisible de V1 (0.75 de la altura: 0.675 m en el Ø 0.90 y en el marco de 0.90 m): la lectura sólo se pide cuando el nivel del receptor toma el borde libre |
| conducto | `seccion_receptor` | [A] | b_m 1.5–3.0; z_HV 1.0–2.0; S 0.0005–0.0015; n 0.025–0.035; altura_total_m 1.2–2.5 | sección de archivo, sección estrecha, sección ancha | juego | NO LO LEE LA CORRIDA | el juego declara `TW_m` (vía 1 de la Sec. 1.3), que manda sobre las vías 3 y 4, las únicas que usan la sección del receptor |
| conducto | `seccion_receptor` | [A] | b_m 1.5–3.0; z_HV 1.0–2.0; S 0.0005–0.0015; n 0.025–0.035; altura_total_m 1.2–2.5 | sección de archivo, sección estrecha, sección ancha | juego_sin_TW | MUEVE EL DISEÑO | diseño: A-01 con sección estrecha: no dimensiona → Concreto reforzado, Ø 0.90 m; A-02 con sección estrecha: no dimensiona → Concreto reforzado, Ø 0.90 m · veredictos que cambian: A-01 con sección estrecha: 297; A-02 con sección estrecha: 297 |
| conducto | `v_max_tmc` | [A] | 3.048–4.572 | 4.572, 3.048 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `v_max_hdpe` | [C] | 0.25–4.572 | 4.572, 0.25 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `v_max_concreto_eleccion` | [A] | 3.0–6.0 | 3.0, 6.0 | juego | MUEVE EL DISEÑO | diseño: A-01 con 3.0: Concreto reforzado, Ø 0.90 m (juego) → TMC galvanizada, Ø 1.20 m · veredictos que cambian: A-01 con 6.0: 4 |
| conducto | `v_max_concreto_eleccion` | [A] | 3.0–6.0 | 3.0, 6.0 | juego_tmc_excluida | MUEVE EL DISEÑO | diseño: A-01 con 3.0: Concreto reforzado, Ø 0.90 m (juego) → no dimensiona · veredictos que cambian: A-01 con 6.0: 297 |
| conducto | `regimen_v2b` | [A] | umbral_duro / indicador_con_aviso | 'indicador_con_aviso', 'umbral_duro' | juego | MUEVE EL DISEÑO | diseño: C-01 con 'umbral_duro': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: C-01 con 'umbral_duro': 389 |
| conducto | `hw_entrada_fuera_de_rango` | [A] | energia_critica / descartar | 'energia_critica', 'descartar' | juego | NO LO LEE LA CORRIDA | ningún punto queda fuera del rango de la corrección por pendiente (la carta da carga positiva en todos los escalones evaluados) |
| conducto | `n_manning_cajon` | [C] | 'concrete_boxes' / 'concreto_afinado' / num. B.3 del HDS-5 (cita HDS5_3ED.B.3#CAJON_IN_SITU): 0.012 a 0.022 en un cajon VACIADO IN SITU, segun el encofrado | 'concrete_boxes', 'concreto_afinado' | juego | MUEVE EL HW | HW: C-01 con 'concreto_afinado': 0.6231 → 0.6233 m |
| conducto | `espesor_pared_cajon` | [A] | EL SIGNO, Y QUE SE INVIRTIO EN VE-3.11: desde entonces V7 suma el peso propio del concreto (H4 de los ensayos de diseño del conducto), y ENGROSAR LA PARED MEJORA LA FLOTACION: el anillo que se agrega pesa gamma_c = 23.56 kN/m3 y desplaza agua de 9.81, de modo que por cada metro de t el lado estabilizante crece 0.90*gamma_c*2*(Bc + B'c) y el empuje solo gamma_w*2*(Bc + B'c). Medido sobre un marco de 2.00 x 1.50 m con 0.95 m de relleno y gamma_r = 18 kN/m3: t = 0.15 da margen +18.96 kN/m, t = 0.20 da +25.28 y t = 0.25 da +31.83. HASTA VE-3.11, con DC = 0, era al reves / HACIA ABAJO el limite no es la flotacion sino el propio calculo estructural, que este alcance difiere: una pared que flota mejor puede no resistir el empuje de tierras ni la carga viva. Por eso la ventana no se puede cerrar a nivel de perfil y el criterio se ADOPTA en vez de optimizarse: el optimo de V7 y el minimo estructural empujan en sentidos opuestos y solo la Fase 8 tiene los dos numeros / VENTANA DE LA ADOPCION (T-3): 0.20 m | 0.3, 0.25, 0.2 | juego | MUEVE VEREDICTOS | veredictos que cambian: C-01 con 0.25: 20; C-01 con 0.2: 24 |
| conducto | `borde_libre_y_sobre_d_max` | [A] | 0.0–0.75 | 0.75, 0.6, 0.0 | juego | MUEVE EL DISEÑO | diseño: A-01 con 0.6: Concreto reforzado, Ø 0.90 m → Concreto reforzado, Ø 1.05 m; A-01 con 0.0: Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 0.0: Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 0.0: Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 0.0: Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 0.0: 297; A-02 con 0.0: 297; B-01 con 0.0: 297; C-01 con 0.0: 389 |
| conducto | `ke_entrada` | [C] | 0.2–0.9 | 0.5, 0.2, 0.9 | juego | MUEVE EL HW | HW: A-01 con 0.9: 1.0420 → 1.0618 m |
| conducto | `embocadura_cabezal` | [A] | cabezal_con_aleros / cabezal_recto | 'cabezal_con_aleros', 'cabezal_recto' | juego | MUEVE EL DISEÑO | diseño: C-01 con 'cabezal_recto': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'cabezal_recto': 204; A-02 con 'cabezal_recto': 204; B-01 con 'cabezal_recto': 204; C-01 con 'cabezal_recto': 389 |
| conducto | `fraccion_llena_mayor_parte` | [A] | 0.5–0.9 | 0.5, 0.9 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `instalacion_estandar_concreto` | [A] | tipo_1 / tipo_2 / tipo_3 / tipo_4 | 'tipo_3', 'tipo_1', 'tipo_2', 'tipo_4' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `carga_viva_bajo_relleno_alto` | [A] | conservar / despreciar_3_6_1_2_6a | 'conservar', 'despreciar_3_6_1_2_6a' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `eta_importancia_operativa_conducto` | [A] | 0.95–1.05 | 1.05, 0.95 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.95: 1; A-02 con 0.95: 1; B-01 con 0.95: 1 |
| cabezal | `factor_muro_eleccion` | [A] | sin_reduccion / reduccion_por_desplazamiento | 'reduccion_por_desplazamiento', 'sin_reduccion' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'sin_reduccion': 26; A-02 con 'sin_reduccion': 25; B-01 con 'sin_reduccion': 21; C-01 con 'sin_reduccion': 22 |
| cabezal | `gamma_EQ` | [A] | 0.0–1.0 | 0.5, 0.0, 1.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: C-01 con 0.0: 1; B-01 con 1.0: 1; C-01 con 1.0: 1 |
| cabezal | `fraccion_delta_sobre_phi_trasdos` | [C] | 0.33–0.67 | 0.67, 0.33 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.33: 2; A-02 con 0.33: 2; C-01 con 0.33: 2 |
| cabezal | `fila_phi_estabilidad_cabezal` | [A] | zapatas_seccion_10 / muros_tabla_11_5_7 | 'muros_tabla_11_5_7', 'zapatas_seccion_10' | juego_cabezal_de_la_regla | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'zapatas_seccion_10': 10; A-02 con 'zapatas_seccion_10': 9; B-01 con 'zapatas_seccion_10': 11; C-01 con 'zapatas_seccion_10': 11 |
| cabezal | `factores_inclinacion_carga_portante` | [A] | aplicar / omitir | 'aplicar', 'omitir' | juego_cabezal_de_la_regla | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'omitir': 27; A-02 con 'omitir': 28; B-01 con 'omitir': 26; C-01 con 'omitir': 19 |
| cabezal | `regla_pendiente_relleno_trasdos` | [A] | cuna_de_tanteo / talud_quebrado_2h / talud_del_terraplen | 'cuna_de_tanteo', 'talud_quebrado_2h', 'talud_del_terraplen' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'talud_quebrado_2h': 2; A-02 con 'talud_quebrado_2h': 5; B-01 con 'talud_quebrado_2h': 2; C-01 con 'talud_quebrado_2h': 3; A-01 con 'talud_del_terraplen': 5; A-02 con 'talud_del_terraplen': 7; B-01 con 'talud_del_terraplen': 4; C-01 con 'talud_del_terraplen': 5 |
| cabezal | `regimen_resistencia_elementos_cabezal` | [A] | no_cedente_k0 / cedente | 'cedente', 'no_cedente_k0' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'no_cedente_k0': 199; A-02 con 'no_cedente_k0': 198; B-01 con 'no_cedente_k0': 197; C-01 con 'no_cedente_k0': 197 |
| cabezal | `eta_ductilidad_cabezal` | [A] | 0.95–1.05 | 1.0, 0.95, 1.05 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.95: 1; A-02 con 0.95: 1; B-01 con 0.95: 1; A-01 con 1.05: 1; A-02 con 1.05: 1; B-01 con 1.05: 3; C-01 con 1.05: 2 |
| cabezal | `eta_redundancia_cabezal` | [A] | 0.95–1.05 | 1.0, 0.95, 1.05 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.95: 1; A-02 con 0.95: 1; B-01 con 0.95: 1; A-01 con 1.05: 1; A-02 con 1.05: 1; B-01 con 1.05: 3; C-01 con 1.05: 2 |
| cabezal | `marco_estabilidad_cabezal` | [A] | lrfd_rige_asd_informa / asd_rige_lrfd_informa / envolvente_de_los_dos | 'lrfd_rige_asd_informa', 'asd_rige_lrfd_informa', 'envolvente_de_los_dos' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'asd_rige_lrfd_informa': 16; A-02 con 'asd_rige_lrfd_informa': 17; B-01 con 'asd_rige_lrfd_informa': 22; C-01 con 'asd_rige_lrfd_informa': 19; A-01 con 'envolvente_de_los_dos': 16; A-02 con 'envolvente_de_los_dos': 17; B-01 con 'envolvente_de_los_dos': 22; C-01 con 'envolvente_de_los_dos': 19 |
| cabezal | `regimen_cabezal` | [A] | cedente / no_cedente | 'cedente', 'no_cedente' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'no_cedente': 33; A-02 con 'no_cedente': 31; B-01 con 'no_cedente': 26; C-01 con 'no_cedente': 29 |
| cabezal | `drenaje_trasdos` | [A] | sin_drenaje / drenado | 'drenado', 'sin_drenaje' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'sin_drenaje': 76; A-02 con 'sin_drenaje': 77; B-01 con 'sin_drenaje': 73; C-01 con 'sin_drenaje': 77 |
| cabezal | `fc_cabezal_mpa` | [A] | 17.5–35.0 | 21.0, 17.5, 35.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 17.5: 1 |
| cabezal | `duracion_caudal_pico_socavacion_min` | [A] | 30.0–360.0 | 360.0, 30.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| hidrología | `factor_intervalo_fijo_p24` | [A] | 1.0–1.13 | 1.0, 1.13 | juego_caudal_calculado | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `F_pga_lectura_columna_extrema` | [A] | limite_inclusive / limite_estricto | 'limite_inclusive', 'limite_estricto' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'limite_estricto': 199; A-02 con 'limite_estricto': 198; B-01 con 'limite_estricto': 197; C-01 con 'limite_estricto': 197 |
| cabezal | `inclinacion_muro_beta` | [A] | 0.0–10.0 | 0.0, 10.0 | juego | NO LO LEE LA CORRIDA | sólo lo lee la vía de contraste de Coulomb / Mononobe-Okabe; el empuje que rige sale de la cuña de tanteo sobre el plano vertical del talón |
| cabezal | `punto_aplicacion_incremento_sismico` | [C] | 0.333–0.6 | 0.6, 0.333 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| hidrología | `homogeneidad_serie_fen` | [A] | serie_completa / serie_sin_fen / dos_poblaciones | 'serie_completa', 'serie_sin_fen', 'dos_poblaciones' | juego | NO LO LEE LA CORRIDA | sólo lo lee el caudal CALCULADO; en el juego el caudal es el declarado del CSV (lo mide la variante `caudal_calculado_sin_fen` de `docs/validacion_integral.md`) |
| sin consumidor | `umbral_area_quebrada_importante_ha` | [A] | 50.0–200.0 | 100.0, 50.0, 200.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| hidrología | `distribucion_precipitacion_maxima` | [A] | mejor_ajuste_ks / normal / lognormal_2p / gumbel / lognormal_3p / gamma_2p / gamma_3p / log_pearson_3 / log_gumbel | 'mejor_ajuste_ks', 'normal', 'lognormal_2p', 'gumbel', 'lognormal_3p', 'gamma_2p', 'gamma_3p', 'log_pearson_3', 'log_gumbel' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado, y en el juego el caudal es el declarado |
| hidrología | `nivel_significancia_ks` | [A] | 0.01–0.1 | 0.05, 0.01, 0.1 | juego | NO LO LEE LA CORRIDA | hidrología: sólo lo lee el caudal calculado |
| hidrología | `intervalos_de_clase_chi_cuadrado` | [A] | sturges / raiz_de_n | 'sturges', 'raiz_de_n' | juego | NO LO LEE LA CORRIDA | SIN RAZÓN ESCRITA |
| hidrología | `relacion_intensidad_duracion` | [A] | dick_peschke / tabla_04_coeficientes_de_duracion / idf_regional_ec17 | 'dick_peschke', 'tabla_04_coeficientes_de_duracion', 'idf_regional_ec17' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado |
| hidrología | `duracion_minima_lluvia_min` | [C] | 5.0–15.0 | 5.0, 15.0 | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado |
| hidrología | `tc_fuera_de_la_poblacion_del_metodo` | [A] | no_evaluable / indicador_con_aviso | 'no_evaluable', 'indicador_con_aviso' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado |
| hidrología | `coeficiente_uniformidad_temez` | [A] | aplicar / no_aplicar | 'aplicar', 'no_aplicar' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado con Témez |
| conducto | `columna_n_manning_concreto` | [A] | doble_n_minimo_maximo / columna_normal / n_unico_hds5 | 'doble_n_minimo_maximo', 'columna_normal', 'n_unico_hds5' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `esviaje_max_grados` | [A] | 45.0–60.0 | 45.0, 60.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `borde_libre_canal_m` | [A] | 0.3–0.5 | 0.5, 0.3 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cuneta | `long_max_cuneta` | [A] | 200.0–250.0 | 200.0, 250.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cuneta | `revestimiento_cuneta` | [A] | concreto / roca_dura / roca_blanda / terreno_hierba / terreno_arcilla_grava / terreno_con_vegetacion / terreno_arena_arcillosa / terreno_arena_fina_o_limo | 'concreto', 'roca_dura', 'roca_blanda', 'terreno_hierba', 'terreno_arcilla_grava', 'terreno_con_vegetacion', 'terreno_arena_arcillosa', 'terreno_arena_fina_o_limo' | juego | MUEVE VEREDICTOS | veredictos que cambian: B-01 con 'terreno_con_vegetacion': 2; B-01 con 'terreno_arena_arcillosa': 2; B-01 con 'terreno_arena_fina_o_limo': 2 |
| cuneta | `lectura_velocidad_limite_cuneta` | [A] | extremo_inferior / extremo_superior | 'extremo_inferior', 'extremo_superior' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cuneta | `obras_familia_a_extremo_de_cuneta` | [A] | si / no | 'si', 'no' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `origen_cota_fondo_entrada` | [A] | cota_terreno / cota_fondo_entrada | 'cota_terreno', 'cota_fondo_entrada' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'cota_fondo_entrada': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'cota_fondo_entrada': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'cota_fondo_entrada': Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 'cota_fondo_entrada': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'cota_fondo_entrada': 297; A-02 con 'cota_fondo_entrada': 297; B-01 con 'cota_fondo_entrada': 297; C-01 con 'cota_fondo_entrada': 389 |
| conducto | `remanso_derecho_via` | [A] | embalse_a_nivel / cota_de_afectacion / perfil_de_remanso_paso_a_paso | 'cota_de_afectacion', 'embalse_a_nivel', 'perfil_de_remanso_paso_a_paso' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'embalse_a_nivel': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'embalse_a_nivel': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'embalse_a_nivel': Concreto reforzado, Ø 0.90 m → no dimensiona; A-01 con 'perfil_de_remanso_paso_a_paso': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'perfil_de_remanso_paso_a_paso': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'perfil_de_remanso_paso_a_paso': Concreto reforzado, Ø 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'embalse_a_nivel': 297; A-02 con 'embalse_a_nivel': 297; B-01 con 'embalse_a_nivel': 297; A-01 con 'perfil_de_remanso_paso_a_paso': 297; A-02 con 'perfil_de_remanso_paso_a_paso': 297; B-01 con 'perfil_de_remanso_paso_a_paso': 297 |
| conducto | `acceso_mantenimiento_v2b` | [A] | camara_o_buzon_en_cabecera / acceso_por_cabezal_sin_obra_adicional / sin_acceso_declarado_como_limitacion | 'camara_o_buzon_en_cabecera', 'acceso_por_cabezal_sin_obra_adicional', 'sin_acceso_declarado_como_limitacion' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `pendiente_minima_conducto` | [A] | 0.0–0.005 | 0.0, 0.005 | juego | MUEVE EL DISEÑO | diseño: C-01 con 0.005: Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: C-01 con 0.005: 389 |
| conducto | `pendiente_maxima_conducto` | [A] | 0.02–0.1 | 0.1, 0.02 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `phi_relleno_trasdos` | [A] | 30.0–38.0 | 34.0, 30.0, 38.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 30.0: 3; A-02 con 30.0: 3; B-01 con 30.0: 4; C-01 con 30.0: 2; A-01 con 38.0: 1; A-02 con 38.0: 3; B-01 con 38.0: 3; C-01 con 38.0: 4 |
| sin consumidor | `demanda_sismica_licuefaccion` | [A] | 475–1000 | 1000, 475 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `diametro_de_diseno_concreto` | [A] | designado / designado_o_ingles_convertido | 'designado', 'designado_o_ingles_convertido' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `condicion_pavimento` | [A] | no_pavimentado / flexible / rigido | 'flexible', 'no_pavimentado', 'rigido' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `corrugacion_y_espesor_tmc` | [A] | 68x13/1.32 / 68x13/1.63 / 68x13/2.01 / 68x13/2.77 / 68x13/3.51 / 68x13/4.27 / 75x25/1.32 / 75x25/1.63 / 75x25/2.01 / 75x25/2.77 / 75x25/3.51 / 75x25/4.27 / 125x25/1.63 / 125x25/2.01 / 125x25/2.77 / 125x25/3.51 / 125x25/4.27 | '68x13/2.01', '68x13/1.32', '68x13/1.63', '68x13/2.77', '68x13/3.51', '68x13/4.27', '75x25/1.32', '75x25/1.63', '75x25/2.01', '75x25/2.77', '75x25/3.51', '75x25/4.27', '125x25/1.63', '125x25/2.01', '125x25/2.77', '125x25/3.51', '125x25/4.27' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `suelo_agresivo_lrfd_sobre_tmc` | [A] | aviso / excluye | 'aviso', 'excluye' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `relleno_max_contraste_acpa_m` | [A] | 0.6096–1.5 | 1.0, 0.6096, 1.5 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `peso_especifico_relleno_kn_m3` | [A] | 17.0–20.0 | 17.0, 20.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 20.0: 2; C-01 con 20.0: 1 |
| conducto | `nivel_agua_diseno_v7` | [A] | en_la_clave / nf_del_punto | 'en_la_clave', 'nf_del_punto' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'nf_del_punto': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'nf_del_punto': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'nf_del_punto': Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 'nf_del_punto': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'nf_del_punto': 297; A-02 con 'nf_del_punto': 297; B-01 con 'nf_del_punto': 297; C-01 con 'nf_del_punto': 389 |
| conducto | `fabricacion_tmc` | [A] | helicoidal / anular_remachada_simple / anular_remachada_doble / anular_empernada | 'anular_remachada_simple', 'helicoidal', 'anular_remachada_doble', 'anular_empernada' | juego | NO LO LEE LA CORRIDA | ningún punto adopta TMC: el concreto es el primer candidato |
| conducto | `relleno_estructural_hdpe` | [A] | Sn-100 / Sn-95 / Si-95 / Cl-95 | 'Si-95', 'Sn-100', 'Sn-95', 'Cl-95' | juego | NO LO LEE LA CORRIDA | ningún punto adopta HDPE: el concreto es el primer candidato |
| conducto | `carga_viva_tubo_concreto_somero` | [A] | largo_del_neumatico / e_span_a_un_pie | 'largo_del_neumatico', 'e_span_a_un_pie' | juego | NO LO LEE LA CORRIDA | SIN RAZÓN ESCRITA |
| conducto | `talud_terraplen` | [A] | 1.5–2.0 | 2.0, 1.5 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 1.5: 1; A-02 con 1.5: 2; B-01 con 1.5: 3; C-01 con 1.5: 2 |
| protección | `espesor_proteccion_salida` | [A] | 1.5–2.0 | 1.75, 1.5, 2.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `longitud_proteccion_salida` | [A] | 3.0–8.0 | 5.0, 3.0, 8.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `tipo_proteccion_entrada` | [A] | emboquillado_de_piedra / enchapado_de_roca_acomodada / otro_revestimiento | 'emboquillado_de_piedra', 'enchapado_de_roca_acomodada', 'otro_revestimiento' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `lectura_coeficientes_socavacion_hec14` | [A] | envolvente_de_filas_vecinas / interpolacion_lineal | 'envolvente_de_filas_vecinas', 'interpolacion_lineal' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `regla_espesor_longitud_proteccion_salida` | [A] | manual / envolvente_hec14 | 'envolvente_hec14', 'manual' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `relacion_co_poza_enrocado_hec14` | [A] | envolvente / mejor_ajuste | 'envolvente', 'mejor_ajuste' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `referencia_profundidad_socavacion` | [A] | fondo_del_cauce_receptor / solera_de_salida | 'fondo_del_cauce_receptor', 'solera_de_salida' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'solera_de_salida': 4; A-02 con 'solera_de_salida': 5; B-01 con 'solera_de_salida': 1; C-01 con 'solera_de_salida': 3 |
| conducto | `regimen_cortante_muro_e060_art_11_10_2` | [A] | en_el_plano / perpendicular_al_plano | 'perpendicular_al_plano', 'en_el_plano' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `margen_zapata_bajo_socavacion_m` | [C] | 0.0–0.6096 | 0.0, 0.6096 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.6096: 3; A-02 con 0.6096: 3; C-01 con 0.6096: 1 |
| conducto | `umbral_no_colapso_evento_extremo` | [A] | sin_desborde_de_la_plataforma / desborde_admitido_con_terraplen_protegido | 'sin_desborde_de_la_plataforma', 'desborde_admitido_con_terraplen_protegido' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'desborde_admitido_con_terraplen_protegido': 297; A-02 con 'desborde_admitido_con_terraplen_protegido': 297; B-01 con 'desborde_admitido_con_terraplen_protegido': 297; C-01 con 'desborde_admitido_con_terraplen_protegido': 389 |
| cabezal | `terreno_delante_del_cabezal` | [A] | horizontal / talud_descendente | 'horizontal', 'talud_descendente' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'talud_descendente': 144; A-02 con 'talud_descendente': 144; B-01 con 'talud_descendente': 144; C-01 con 'talud_descendente': 144 |
| cabezal | `factores_forma_profundidad_portante` | [A] | corrida_sin_profundidad / forma_con_la_longitud_del_cabezal / forma_y_profundidad | 'corrida_sin_profundidad', 'forma_con_la_longitud_del_cabezal', 'forma_y_profundidad' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'forma_con_la_longitud_del_cabezal': 1; A-02 con 'forma_con_la_longitud_del_cabezal': 2; A-01 con 'forma_y_profundidad': 3; A-02 con 'forma_y_profundidad': 2 |
| conducto | `acero_refuerzo_cabezal` | [A] | A615_grado_60 / A706_grado_60 | 'A615_grado_60', 'A706_grado_60' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `regla_minimos_constructivos_cabezal` | [A] | mas_exigente_aashto_e060 / solo_aashto | 'mas_exigente_aashto_e060', 'solo_aashto' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `criterio_traccion_cabezal_ciclopeo` | [A] | tracciones_nulas / traccion_admisible_e060 | 'tracciones_nulas', 'traccion_admisible_e060' | juego | NO LO LEE LA CORRIDA | ningún cabezal del juego es de gravedad: con D >= 0.90 m todos son voladizo armado (T-7a) |
| conducto | `clase_exposicion_fisuracion_cabezal` | [A] | clase_1 / clase_2 | 'clase_2', 'clase_1' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `junta_arranque_cabezal_ciclopeo` | [A] | junta_de_construccion / vaciado_monolitico | 'junta_de_construccion', 'vaciado_monolitico' | juego | NO LO LEE LA CORRIDA | ningún cabezal del juego es de gravedad |
| conducto | `metodo_longitud_conducto` | [A] | terraplen_simetrico / por_extremo | 'por_extremo', 'terraplen_simetrico' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'terraplen_simetrico': 1; A-02 con 'terraplen_simetrico': 1; C-01 con 'terraplen_simetrico': 1 |
| conducto | `desnivel_minimo_entrega_m` | [A] | 0.0–0.3 | 0.0, 0.3 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `desajuste_empalme_canal_m` | [A] | 0.01–0.02 | 0.01, 0.02 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `momento_talon_cabezal` | [A] | peso_entero / exacto | 'exacto', 'peso_entero' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'peso_entero': 3; A-02 con 'peso_entero': 1 |
| cabezal | `carga_pantalla_cabezal` | [A] | plano_virtual_del_talon / cuna_sobre_la_pantalla | 'cuna_sobre_la_pantalla', 'plano_virtual_del_talon' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `distribucion_incremento_sismico` | [A] | segun_regimen / fraccion_de_h / distribucion_estatica | 'segun_regimen', 'fraccion_de_h', 'distribucion_estatica' | juego | MUEVE VEREDICTOS | veredictos que cambian: B-01 con 'fraccion_de_h': 2 |
| cabezal | `empuje_sismico_muro_que_no_cede` | [A] | reposo_mas_incremento / mayor_de_reposo_y_total | 'reposo_mas_incremento', 'mayor_de_reposo_y_total' | juego | NO LO LEE LA CORRIDA | SIN RAZÓN ESCRITA |
| cabezal | `agua_del_relleno_bajo_sismo` | [C] | se_mueve_con_el_suelo / relleno_muy_abierto | 'se_mueve_con_el_suelo', 'relleno_muy_abierto' | juego | NO LO LEE LA CORRIDA | el trasdós del juego es drenado (valor de archivo desde VE-3.16) y su freático queda bajo las zapatas: no hay agua en el plano de empuje bajo sismo, que es lo único que lee la elección (VE-3.14, C11.6.5.3) |
| sin consumidor | `clase_concreto_losa_entrega` | [A] | C / D / E / F / G | 'E', 'C', 'D', 'F', 'G' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |

## 3. Lo que el resumen dice, por clase

- **MUEVE EL DISEÑO** (11): `seccion_receptor` (juego_sin_TW), `v_max_concreto_eleccion`, `v_max_concreto_eleccion` (juego_tmc_excluida), `regimen_v2b`, `borde_libre_y_sobre_d_max`, `embocadura_cabezal`, `origen_cota_fondo_entrada`, `remanso_derecho_via`, `pendiente_minima_conducto`, `nivel_agua_diseno_v7`, `umbral_no_colapso_evento_extremo`.
- **MUEVE VEREDICTOS** (27): `espesor_pared_cajon`, `eta_importancia_operativa_conducto`, `factor_muro_eleccion`, `gamma_EQ`, `fraccion_delta_sobre_phi_trasdos`, `fila_phi_estabilidad_cabezal` (juego_cabezal_de_la_regla), `factores_inclinacion_carga_portante` (juego_cabezal_de_la_regla), `regla_pendiente_relleno_trasdos`, `regimen_resistencia_elementos_cabezal`, `eta_ductilidad_cabezal`, `eta_redundancia_cabezal`, `marco_estabilidad_cabezal`, `regimen_cabezal`, `drenaje_trasdos`, `fc_cabezal_mpa`, `F_pga_lectura_columna_extrema`, `revestimiento_cuneta`, `phi_relleno_trasdos`, `peso_especifico_relleno_kn_m3`, `talud_terraplen`, `referencia_profundidad_socavacion`, `margen_zapata_bajo_socavacion_m`, `terreno_delante_del_cabezal`, `factores_forma_profundidad_portante`, `metodo_longitud_conducto`, `momento_talon_cabezal`, `distribucion_incremento_sismico`.
- **MUEVE EL HW** (2): `n_manning_cajon`, `ke_entrada`.
- **LEÍDO, SIN EFECTO MEDIBLE** (38): `HW_D_max`, `v_max_tmc`, `v_max_hdpe`, `fraccion_llena_mayor_parte`, `instalacion_estandar_concreto`, `carga_viva_bajo_relleno_alto`, `duracion_caudal_pico_socavacion_min`, `factor_intervalo_fijo_p24` (juego_caudal_calculado), `punto_aplicacion_incremento_sismico`, `umbral_area_quebrada_importante_ha`, `columna_n_manning_concreto`, `esviaje_max_grados`, `borde_libre_canal_m`, `long_max_cuneta`, `lectura_velocidad_limite_cuneta`, `obras_familia_a_extremo_de_cuneta`, `acceso_mantenimiento_v2b`, `pendiente_maxima_conducto`, `demanda_sismica_licuefaccion`, `diametro_de_diseno_concreto`, `condicion_pavimento`, `corrugacion_y_espesor_tmc`, `suelo_agresivo_lrfd_sobre_tmc`, `relleno_max_contraste_acpa_m`, `espesor_proteccion_salida`, `longitud_proteccion_salida`, `tipo_proteccion_entrada`, `lectura_coeficientes_socavacion_hec14`, `regla_espesor_longitud_proteccion_salida`, `relacion_co_poza_enrocado_hec14`, `regimen_cortante_muro_e060_art_11_10_2`, `acero_refuerzo_cabezal`, `regla_minimos_constructivos_cabezal`, `clase_exposicion_fisuracion_cabezal`, `desnivel_minimo_entrega_m`, `desajuste_empalme_canal_m`, `carga_pantalla_cabezal`, `clase_concreto_losa_entrega`.
- **NO LO LEE LA CORRIDA** (19): `borde_libre_bajo_tw_ahogante`, `seccion_receptor`, `hw_entrada_fuera_de_rango`, `inclinacion_muro_beta`, `homogeneidad_serie_fen`, `distribucion_precipitacion_maxima`, `nivel_significancia_ks`, `intervalos_de_clase_chi_cuadrado`, `relacion_intensidad_duracion`, `duracion_minima_lluvia_min`, `tc_fuera_de_la_poblacion_del_metodo`, `coeficiente_uniformidad_temez`, `fabricacion_tmc`, `relleno_estructural_hdpe`, `carga_viva_tubo_concreto_somero`, `criterio_traccion_cabezal_ciclopeo`, `junta_arranque_cabezal_ciclopeo`, `empuje_sismico_muro_que_no_cede`, `agua_del_relleno_bajo_sismo`.

### 3.1 El cabezal de la regla: E3 estática y E1 sísmica del marco LRFD frente a sus dos [A]

Con la zapata que propone la regla de T-7a, SIN dimensionar (base `juego_cabezal_de_la_regla`: desde VE-3.5 la zapata del juego crece hasta cumplir, y estas filas pasan con cualquier valor), estas cuatro filas no pasan en todos los puntos (desde VE-3.15, con la fila de phi de muros y el talon exacto, algunas pasan en algunos: la tabla lo dice punto a punto). Lo que cada uno de los dos [A] de los que dependen hace con ellas, medido (la primera fila de cada criterio es su valor de archivo):

| Criterio | Valor | `E1-LRFD.sis.e` | `E1-LRFD.sis.s` | `E3-LRFD.est.e` | `E3-LRFD.est.s` |
|---|---|---|---|---|---|
| `fila_phi_estabilidad_cabezal` | 'muros_tabla_11_5_7' | pasa en A-01, C-01 | no pasa en ninguno | pasa en C-01 | pasa en A-01, C-01 |
| `fila_phi_estabilidad_cabezal` | 'zapatas_seccion_10' | pasa en A-01, C-01 | no pasa en ninguno | no pasa en ninguno | no pasa en ninguno |
| `factores_inclinacion_carga_portante` | 'aplicar' | pasa en A-01, C-01 | no pasa en ninguno | pasa en C-01 | pasa en A-01, C-01 |
| `factores_inclinacion_carga_portante` | 'omitir' | pasa en A-01, A-02, B-01, C-01 | pasa en A-01, A-02, B-01, C-01 | pasa en C-01 | pasa en A-01, C-01 |

Ninguno de los dos hace pasar E3 estática a la ENTRADA: ahí el deslizamiento lo resuelve la zapata más ancha —la que el dimensionamiento de VE-3.5 adopta, o la declarada de la variante `zapata_declarada_3m` de `docs/validacion_integral.md` §5—, no la lectura de un [A].

### 3.2 `v_max_concreto_eleccion`: lo que el dueño decidió y de qué depende el resultado

El criterio **se queda SIN valor por decisión del dueño (2026-11-13)**: es opcional y V3 aplica el máximo de 6.0 m/s de la Tabla Nº 10 del Manual para el concreto. Lo que el barrido mide con el extremo inferior de esa misma fila (3.0 m/s) es un **resultado de la tesis que no cambia el fixture**:

- base `juego` (el juego completo): A-01 con 3.0 m/s → TMC galvanizada, Ø 1.20 m.
- base `juego_tmc_excluida` (el juego con `suelo_agresivo_lrfd_sobre_tmc` = 'excluye' (dentro de su ventana): el TMC queda fuera por los sulfatos del juego (500 ppm > 200)): A-01 con 3.0 m/s → no dimensiona (DatoFaltanteError: material y diametro (bucle de MD) (perfil_hdpe_fabricante)).

Ese resultado depende de **otro [A]**: el TMC al que A-01 pasa está en un suelo que la misma corrida califica de agresivo para el acero galvanizado (sulfatos de 500 ppm frente a los 200 ppm de AASHTO LRFD 11.10.6.4.2a que `suelo_agresivo_acero_lrfd` aplica por analogía; para el concreto son «insignificantes» por la Tabla 4.4 de E.060). Con `suelo_agresivo_lrfd_sobre_tmc` = 'aviso' (el de archivo) la TMC sigue candidata con aviso; con 'excluye', dentro de su ventana, sale, y A-01 se detiene en el siguiente candidato, el HDPE, por el dato del fabricante que falta.

Lectura de ingeniería (no la escribe el programa): un criterio que MUEVE EL DISEÑO dentro de su ventana es una decisión que el proyectista tiene que poder defender con la cita de su ficha, porque otra lectura igual de admisible da otra obra; uno que NO LO LEE ESTA CORRIDA puede gobernar en otro punto u otro sitio (otro material candidato, otro TW): este anexo no lo absuelve.

## 4. Detalle por criterio

### `HW_D_max`

tope de V4b (PRECISIONES). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.2 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.2 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.2 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.2 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `borde_libre_bajo_tw_ahogante`

lectura de V1 cuando el receptor llena la sección (PRECISIONES). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'no_cumple' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'no_cumple' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'no_cumple' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'no_cumple' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'aviso' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'aviso' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'aviso' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'aviso' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `seccion_receptor`

sección adoptada del receptor (PRECISIONES), con el TW del juego. Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| sección de archivo | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| sección de archivo | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| sección de archivo | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| sección de archivo | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| sección estrecha | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| sección estrecha | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| sección estrecha | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| sección estrecha | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| sección ancha | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| sección ancha | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| sección ancha | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| sección ancha | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `seccion_receptor` — base `juego_sin_TW`

sección adoptada del receptor (PRECISIONES), con el TW por la vía 4. Base: el juego sin `TW_m` (el TW sale de la vía 4 de la Sec. 1.3, los escenarios acotados con la sección del receptor). Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| sección de archivo | A-01 | no dimensiona | — | — | ninguna | V1, V4, V4b, V7 | sí |
| sección de archivo | A-02 | no dimensiona | — | — | ninguna | V1, V2, V7 | sí |
| sección de archivo | B-01 | no dimensiona | — | — | ninguna | V1, V2, V4, V7 | sí |
| sección de archivo | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| sección estrecha | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, CB1.e, CB1.s, CB2.e, CB2.s, CB3.e, CB3.s, CB4.e, CB4.s, CB5.s, CB6.e, CB6.s, CB7.e, CB7.s, E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75, F8.CLASE, G1, G2, G3, V1, V10, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9 | — | NO: el punto tiene diseño en B y no en A: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| sección estrecha | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, CB1.e, CB1.s, CB2.e, CB2.s, CB3.e, CB3.s, CB4.e, CB4.s, CB5.s, CB6.e, CB6.s, CB7.e, CB7.s, E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75, F8.CLASE, G1, G2, G3, V1, V10, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9 | — | NO: el punto tiene diseño en B y no en A: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| sección estrecha | B-01 | no dimensiona | — | — | ninguna | V1, V2, V7 | sí |
| sección estrecha | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| sección ancha | A-01 | no dimensiona | — | — | ninguna | V1, V4, V4b, V5, V7 | sí |
| sección ancha | A-02 | no dimensiona | — | — | ninguna | V1, V2, V4, V4b, V7 | sí |
| sección ancha | B-01 | no dimensiona | — | — | ninguna | V1, V2, V4, V4b, V5, V7 | sí |
| sección ancha | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `v_max_tmc`

techo de V3 del TMC (PRECISIONES). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 4.572 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 4.572 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 4.572 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 4.572 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 3.048 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 3.048 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 3.048 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 3.048 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `v_max_hdpe`

techo de V3 del HDPE (PRECISIONES). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 4.572 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 4.572 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 4.572 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 4.572 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.25 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.25 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.25 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.25 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `v_max_concreto_eleccion`

techo de V3 del concreto, opcional (PRECISIONES). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

El primer valor NO es el del juego (el juego no lo declara: rige la regla de su ficha). Referencia, el juego sin barrer: A-01 Concreto reforzado, Ø 0.90 m; A-02 Concreto reforzado, Ø 0.90 m; B-01 Concreto reforzado, Ø 0.90 m; C-01 Concreto reforzado, marco 1.20 × 0.90 m.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 3.0 | A-01 | TMC galvanizada, Ø 1.20 m | 0.954 | salida | ninguna | — | sí |
| 3.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 3.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 3.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 6.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | F8.AREA, F8.CLASE, F8.COSTURA, F8.FF | — | NO: métodos distintos (control_gobernante: 'salida' frente a 'entrada', perfil_tipo: 'M2' frente a 'S1'): los numeros del diseño salieron de formulas distintas y no se comparan uno a uno |
| 6.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 6.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 6.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `v_max_concreto_eleccion` — base `juego_tmc_excluida`

techo de V3 del concreto con el TMC excluido por los sulfatos (correcciones de T-11, H6: el resultado de 3.0 m/s depende de `suelo_agresivo_lrfd_sobre_tmc`). Base: el juego con `suelo_agresivo_lrfd_sobre_tmc` = 'excluye' (dentro de su ventana): el TMC queda fuera por los sulfatos del juego (500 ppm > 200). Efecto: **MUEVE EL DISEÑO**.

El primer valor NO es el del juego (el juego no lo declara: rige la regla de su ficha). Referencia, el juego sin barrer: A-01 Concreto reforzado, Ø 0.90 m; A-02 Concreto reforzado, Ø 0.90 m; B-01 Concreto reforzado, Ø 0.90 m; C-01 Concreto reforzado, marco 1.20 × 0.90 m.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 3.0 | A-01 | no dimensiona | — | — | ninguna | V1, V3, V7 | sí |
| 3.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 3.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 3.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 6.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, CB1.e, CB1.s, CB2.e, CB2.s, CB3.e, CB3.s, CB4.e, CB4.s, CB5.s, CB6.e, CB6.s, CB7.e, CB7.s, E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75, F8.CLASE, G1, G2, G3, V1, V10, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9 | — | NO: el punto tiene diseño en B y no en A: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 6.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 6.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 6.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `regimen_v2b`

régimen del indicador de V2b (PRECISIONES). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'indicador_con_aviso' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'indicador_con_aviso' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'indicador_con_aviso' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'indicador_con_aviso' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'umbral_duro' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'umbral_duro' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'umbral_duro' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'umbral_duro' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | V2b | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `hw_entrada_fuera_de_rango`

carga de entrada fuera del rango de la corrección (PRECISIONES). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'energia_critica' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'energia_critica' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'energia_critica' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'energia_critica' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'descartar' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'descartar' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'descartar' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'descartar' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `n_manning_cajon`

doble n del marco (PRECISIONES). Se barre la alternativa de TABLA (n menor); el lado ALTO de la ventana, el num. B.3 del HDS-5 (0.012 a 0.022 en un cajón vaciado in situ), NO SE MIDIÓ: la ficha dice que se declara «como el par de la especificación del encofrado», y la puerta lo rechaza (la forma del criterio es `str`). C-01 lo gobierna la salida, que es donde n pesa. Base: el juego completo. Efecto: **MUEVE EL HW**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'concrete_boxes' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'concrete_boxes' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'concrete_boxes' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'concrete_boxes' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'concreto_afinado' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'concreto_afinado' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'concreto_afinado' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'concreto_afinado' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | NO: métodos distintos (perfil_tipo: 'M2' frente a 'M1'): los numeros del diseño salieron de formulas distintas y no se comparan uno a uno |

### `espesor_pared_cajon`

espesor de pared del marco (correcciones de T-11, H3); la ventana está en prosa (0.20 a 0.30 m, ficha T3-08). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.3 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.3 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.3 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.3 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.25 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.25 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.25 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.25 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.losa_inferior_1_derecha.interior, A1.losa_inferior_1_izquierda.interior, A1.losa_superior_1_derecha.interior, A1.losa_superior_1_izquierda.interior, A2.losa_inferior_1_derecha.interior, A2.losa_inferior_1_izquierda.interior, A2.losa_superior_1_derecha.interior, A2.losa_superior_1_izquierda.interior, A3.losa_inferior_1_derecha.interior, A3.losa_inferior_1_izquierda.interior, A3.losa_superior_1_derecha.interior, A3.losa_superior_1_izquierda.interior, A4.losa_inferior_1_derecha.interior, A4.losa_inferior_1_izquierda.interior, A4.losa_superior_1_derecha.interior, A4.losa_superior_1_izquierda.interior, A6.losa_inferior_1_derecha.interior, A6.losa_inferior_1_izquierda.interior, A6.losa_superior_1_derecha.interior, A6.losa_superior_1_izquierda.interior | — | sí |
| 0.2 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.2 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.2 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.2 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.losa_inferior_1_derecha.interior, A1.losa_inferior_1_izquierda.interior, A1.losa_superior_1_derecha.interior, A1.losa_superior_1_izquierda.interior, A2.losa_inferior_1_derecha.exterior, A2.losa_inferior_1_derecha.interior, A2.losa_inferior_1_izquierda.exterior, A2.losa_inferior_1_izquierda.interior, A2.losa_superior_1_derecha.interior, A2.losa_superior_1_izquierda.interior, A3.losa_inferior_1_derecha.interior, A3.losa_inferior_1_izquierda.interior, A3.losa_superior_1_derecha.interior, A3.losa_superior_1_izquierda.interior, A4.losa_inferior_1_derecha.interior, A4.losa_inferior_1_izquierda.interior, A4.losa_superior_1_derecha.interior, A4.losa_superior_1_izquierda.interior, A6.losa_inferior_1_derecha.interior, A6.losa_inferior_1_izquierda.interior, A6.losa_superior_1_derecha.interior, A6.losa_superior_1_izquierda.interior, E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.50 | — | sí |

### `borde_libre_y_sobre_d_max`

umbral de V1, sólo endurecible (T-11). Se barre además un valor intermedio (0.6): el extremo inferior de la ventana (0.0) no lo cumple ningún conducto con caudal. Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.75 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.75 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.75 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.75 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.6 | A-01 | Concreto reforzado, Ø 1.05 m | 0.920 | entrada | ninguna | — | sí |
| 0.6 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.6 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.0 | A-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 0.0 | A-02 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 0.0 | B-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 0.0 | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | V1 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `ke_entrada`

pérdida de entrada del tubo en el control de salida (T-11). Base: el juego completo. Efecto: **MUEVE EL HW**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.2 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.2 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.2 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.2 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.9 | A-01 | Concreto reforzado, Ø 0.90 m | 1.062 | salida | ninguna | — | NO: métodos distintos (control_gobernante: 'entrada' frente a 'salida'): los numeros del diseño salieron de formulas distintas y no se comparan uno a uno |
| 0.9 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.9 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.9 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `embocadura_cabezal`

tipo de embocadura del punto: carta, ke y cabezal (T-11). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cabezal_con_aleros' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cabezal_con_aleros' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cabezal_con_aleros' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cabezal_con_aleros' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'cabezal_recto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'cabezal_recto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'cabezal_recto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'cabezal_recto' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | DatoInvalidoError: coherencia de la embocadura del marco con el cabezal (T-7a) (embocadura_cajon) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `fraccion_llena_mayor_parte`

regla del perfil de la lámina, «la mayor parte» lleno (T-11). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.9 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.9 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.9 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.9 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `instalacion_estandar_concreto`

instalación del tubo de concreto en la Fase 8 (T-11). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'tipo_3' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'tipo_3' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'tipo_3' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'tipo_3' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'tipo_1' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'tipo_1' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'tipo_1' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'tipo_1' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'tipo_2' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'tipo_2' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'tipo_2' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'tipo_2' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'tipo_4' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'tipo_4' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'tipo_4' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'tipo_4' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `carga_viva_bajo_relleno_alto`

carga viva pasados 8 ft de relleno en la Fase 8 (T-11). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'conservar' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'conservar' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'conservar' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'conservar' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'despreciar_3_6_1_2_6a' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'despreciar_3_6_1_2_6a' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'despreciar_3_6_1_2_6a' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'despreciar_3_6_1_2_6a' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `eta_importancia_operativa_conducto`

el η del cruce: Fase 8 y combinaciones del cabezal (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.05 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.05 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.05 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.05 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.95 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero | — | sí |
| 0.95 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.e.alero | — | sí |
| 0.95 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.100 | — | sí |
| 0.95 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `factor_muro_eleccion`

reducción de k_h por desplazamiento (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'reduccion_por_desplazamiento' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'reduccion_por_desplazamiento' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'reduccion_por_desplazamiento' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'reduccion_por_desplazamiento' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'sin_reduccion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.100, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'sin_reduccion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.100, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'sin_reduccion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.100, E1-LRFD.sis.e.alero, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.s.alero, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'sin_reduccion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.100, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |

### `gamma_EQ`

factor de la carga viva en el Evento Extremo I (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E3-ASD.sis.s.alero.50 | — | sí |
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E3-ASD.sis.s.alero.25 | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.s.alero.100 | — | sí |

### `fraccion_delta_sobre_phi_trasdos`

fricción del trasdós δ/φ (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.67 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.67 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.67 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.67 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.33 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.100 | — | sí |
| 0.33 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.75 | — | sí |
| 0.33 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.33 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.50 | — | sí |

### `fila_phi_estabilidad_cabezal` — base `juego_cabezal_de_la_regla`

fila de φ de la estabilidad LRFD (PRECISIONES). Base: el juego sin `dimensionamiento_zapata_cabezal`: la zapata es la de la regla de T-7a, sin dimensionar (VE-3.5, VE-3.9). Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'muros_tabla_11_5_7' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'muros_tabla_11_5_7' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'muros_tabla_11_5_7' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'muros_tabla_11_5_7' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'zapatas_seccion_10' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-LRFD.est.s.alero.100, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75 | — | sí |
| 'zapatas_seccion_10' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75 | — | sí |
| 'zapatas_seccion_10' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-LRFD.est.e.alero, E1-LRFD.est.s.alero.50, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75 | — | sí |
| 'zapatas_seccion_10' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E3-LRFD.est.e, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75 | — | sí |

### `factores_inclinacion_carga_portante` — base `juego_cabezal_de_la_regla`

factores de inclinación de la capacidad portante (PRECISIONES). Base: el juego sin `dimensionamiento_zapata_cabezal`: la zapata es la de la regla de T-7a, sin dimensionar (VE-3.5, VE-3.9). Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'aplicar' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'aplicar' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'aplicar' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'aplicar' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'omitir' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e.alero, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75 | — | sí |
| 'omitir' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75 | — | sí |
| 'omitir' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.25, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.25, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75 | — | sí |
| 'omitir' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.est.s.alero, E1-ASD.est.s.alero.25, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.s.alero, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75 | — | sí |

### `regla_pendiente_relleno_trasdos`

superficie del relleno para el empuje (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cuna_de_tanteo' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cuna_de_tanteo' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cuna_de_tanteo' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cuna_de_tanteo' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'talud_quebrado_2h' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.75 | — | sí |
| 'talud_quebrado_2h' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero, E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.75 | — | sí |
| 'talud_quebrado_2h' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.75 | — | sí |
| 'talud_quebrado_2h' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.50 | — | sí |
| 'talud_del_terraplen' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero, E3-ASD.sis.s | — | sí |
| 'talud_del_terraplen' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero, E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.50 | — | sí |
| 'talud_del_terraplen' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero.100, E3-ASD.sis.s.alero | — | sí |
| 'talud_del_terraplen' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50 | — | sí |

### `regimen_resistencia_elementos_cabezal`

empuje con que se arman los elementos (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cedente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cedente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cedente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cedente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'no_cedente_k0' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.25, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'no_cedente_k0' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'no_cedente_k0' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'no_cedente_k0' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |

### `eta_ductilidad_cabezal`

η_D del cabezal (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.95 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero | — | sí |
| 0.95 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.e.alero | — | sí |
| 0.95 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.100 | — | sí |
| 0.95 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.05 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.75 | — | sí |
| 1.05 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.75 | — | sí |
| 1.05 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero | — | sí |
| 1.05 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero.25 | — | sí |

### `eta_redundancia_cabezal`

η_R del cabezal (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.95 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero | — | sí |
| 0.95 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.e.alero | — | sí |
| 0.95 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.100 | — | sí |
| 0.95 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.05 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.75 | — | sí |
| 1.05 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.75 | — | sí |
| 1.05 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero | — | sí |
| 1.05 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero.25 | — | sí |

### `marco_estabilidad_cabezal`

cuál marco de estabilidad rige (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'lrfd_rige_asd_informa' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'lrfd_rige_asd_informa' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'lrfd_rige_asd_informa' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'lrfd_rige_asd_informa' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'asd_rige_lrfd_informa' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75 | — | sí |
| 'asd_rige_lrfd_informa' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s.alero.100 | — | sí |
| 'asd_rige_lrfd_informa' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75 | — | sí |
| 'asd_rige_lrfd_informa' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.75 | — | sí |
| 'envolvente_de_los_dos' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75 | — | sí |
| 'envolvente_de_los_dos' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s.alero.100 | — | sí |
| 'envolvente_de_los_dos' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75 | — | sí |
| 'envolvente_de_los_dos' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.75 | — | sí |

### `regimen_cabezal`

muro que cede o que no cede en la estabilidad (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cedente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cedente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cedente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cedente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'no_cedente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.pantalla.s, E1-ASD.sis.e.alero.100, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'no_cedente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.100, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'no_cedente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.100, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.s.alero, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'no_cedente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.100, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E3-ASD.sis.e.alero, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |

### `drenaje_trasdos`

trasdós drenado o no (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'drenado' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'drenado' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'drenado' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'drenado' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'sin_drenaje' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'sin_drenaje' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A5.alero.s, A5.pantalla.s, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'sin_drenaje' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A5.talon_alero.s, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'sin_drenaje' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A5.talon.s, A5.talon_alero_50.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |

### `fc_cabezal_mpa`

resistencia del concreto del cabezal (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 21.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 21.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 21.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 21.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 17.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A5.talon_alero_50.s | — | sí |
| 17.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 17.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 17.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 35.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 35.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 35.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 35.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `duracion_caudal_pico_socavacion_min`

duración del pico para la hoya de socavación, que baja el desplante del cabezal de salida (T-11). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 360.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 360.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 360.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 360.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 30.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 30.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 30.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 30.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `factor_intervalo_fijo_p24` — base `juego_caudal_calculado`

factor de intervalo fijo de la serie de 24 h (VE-2 (d)), sobre el caudal CALCULADO: con el juego completo el caudal es el declarado y el factor no se lee. Base: el juego con `Q_m3s` vacío en A-01, A-02 y B-01 (variante `caudal_calculado`): el caudal lo calcula la Fase 1-bis. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.0 | A-01 | no dimensiona | — | — | ninguna | V1, V3, V4, V4b, V5 | sí |
| 1.0 | A-02 | no dimensiona | — | — | ninguna | V3, V4, V4b, V5 | sí |
| 1.0 | B-01 | no dimensiona | — | — | ninguna | V1, V4, V4b, V7 | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.13 | A-01 | no dimensiona | — | — | ninguna | DisenoNoFactibleError: material y diametro (bucle de MD) | sí |
| 1.13 | A-02 | no dimensiona | — | — | ninguna | V1, V3, V4, V4b, V5 | sí |
| 1.13 | B-01 | no dimensiona | — | — | ninguna | V3, V4, V7 | sí |
| 1.13 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `F_pga_lectura_columna_extrema`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'limite_inclusive' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'limite_inclusive' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'limite_inclusive' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'limite_inclusive' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'limite_estricto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.25, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'limite_estricto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'limite_estricto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'limite_estricto' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.e, A1.alero.s, A1.alero_mitad.e, A1.alero_mitad.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A1.talon_alero.e, A1.talon_alero.s, A1.talon_alero_100.e, A1.talon_alero_100.s, A1.talon_alero_25.e, A1.talon_alero_25.s, A1.talon_alero_50.e, A1.talon_alero_50.s, A1.talon_alero_75.e, A1.talon_alero_75.s, A2.alero.e, A2.alero.s, A2.alero_mitad.e, A2.alero_mitad.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A2.talon_alero.e, A2.talon_alero.s, A2.talon_alero_100.e, A2.talon_alero_100.s, A2.talon_alero_25.e, A2.talon_alero_25.s, A2.talon_alero_50.e, A2.talon_alero_50.s, A2.talon_alero_75.e, A2.talon_alero_75.s, A3.alero.e, A3.alero.s, A3.alero_mitad.e, A3.alero_mitad.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A3.talon_alero.e, A3.talon_alero.s, A3.talon_alero_100.e, A3.talon_alero_100.s, A3.talon_alero_25.e, A3.talon_alero_25.s, A3.talon_alero_50.e, A3.talon_alero_50.s, A3.talon_alero_75.e, A3.talon_alero_75.s, A4.alero.e, A4.alero.s, A4.alero_mitad.e, A4.alero_mitad.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A4.talon_alero.e, A4.talon_alero.s, A4.talon_alero_100.e, A4.talon_alero_100.s, A4.talon_alero_25.e, A4.talon_alero_25.s, A4.talon_alero_50.e, A4.talon_alero_50.s, A4.talon_alero_75.e, A4.talon_alero_75.s, A5.alero.e, A5.alero.s, A5.alero_mitad.e, A5.alero_mitad.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A5.talon_alero.e, A5.talon_alero.s, A5.talon_alero_100.e, A5.talon_alero_100.s, A5.talon_alero_25.e, A5.talon_alero_25.s, A5.talon_alero_50.e, A5.talon_alero_50.s, A5.talon_alero_75.e, A5.talon_alero_75.s, A6.alero.e, A6.alero.s, A6.alero_mitad.e, A6.alero_mitad.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A6.talon_alero.e, A6.talon_alero.s, A6.talon_alero_100.e, A6.talon_alero_100.s, A6.talon_alero_25.e, A6.talon_alero_25.s, A6.talon_alero_50.e, A6.talon_alero_50.s, A6.talon_alero_75.e, A6.talon_alero_75.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.est.s.alero, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |

### `inclinacion_muro_beta`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 10.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 10.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 10.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 10.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `punto_aplicacion_incremento_sismico`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.6 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.6 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.6 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.333 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.333 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.333 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.333 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `homogeneidad_serie_fen`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'serie_completa' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'serie_completa' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'serie_completa' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'serie_completa' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'serie_sin_fen' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'serie_sin_fen' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'serie_sin_fen' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'serie_sin_fen' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'dos_poblaciones' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'dos_poblaciones' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'dos_poblaciones' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'dos_poblaciones' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `umbral_area_quebrada_importante_ha`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 100.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 100.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 100.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 100.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 50.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 50.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 50.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 50.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 200.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 200.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 200.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 200.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `distribucion_precipitacion_maxima`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'mejor_ajuste_ks' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'mejor_ajuste_ks' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'mejor_ajuste_ks' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'mejor_ajuste_ks' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'normal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'normal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'normal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'normal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'lognormal_2p' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'lognormal_2p' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'lognormal_2p' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'lognormal_2p' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'gumbel' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'gumbel' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'gumbel' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'gumbel' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'lognormal_3p' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'lognormal_3p' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'lognormal_3p' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'lognormal_3p' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'gamma_2p' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'gamma_2p' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'gamma_2p' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'gamma_2p' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'gamma_3p' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'gamma_3p' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'gamma_3p' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'gamma_3p' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'log_pearson_3' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'log_pearson_3' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'log_pearson_3' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'log_pearson_3' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'log_gumbel' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'log_gumbel' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'log_gumbel' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'log_gumbel' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `nivel_significancia_ks`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.05 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.05 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.05 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.05 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.01 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.01 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.01 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.01 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.1 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.1 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.1 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.1 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `intervalos_de_clase_chi_cuadrado`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'sturges' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'sturges' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'sturges' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'sturges' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'raiz_de_n' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'raiz_de_n' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'raiz_de_n' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'raiz_de_n' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `relacion_intensidad_duracion`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'dick_peschke' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'dick_peschke' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'dick_peschke' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'dick_peschke' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'tabla_04_coeficientes_de_duracion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'tabla_04_coeficientes_de_duracion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'tabla_04_coeficientes_de_duracion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'tabla_04_coeficientes_de_duracion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'idf_regional_ec17' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'idf_regional_ec17' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'idf_regional_ec17' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'idf_regional_ec17' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `duracion_minima_lluvia_min`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 5.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 5.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 5.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 5.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 15.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 15.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 15.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 15.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `tc_fuera_de_la_poblacion_del_metodo`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'no_evaluable' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'no_evaluable' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'no_evaluable' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'no_evaluable' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'indicador_con_aviso' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'indicador_con_aviso' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'indicador_con_aviso' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'indicador_con_aviso' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `coeficiente_uniformidad_temez`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'aplicar' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'aplicar' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'aplicar' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'aplicar' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'no_aplicar' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'no_aplicar' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'no_aplicar' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'no_aplicar' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `columna_n_manning_concreto`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'doble_n_minimo_maximo' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'doble_n_minimo_maximo' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'doble_n_minimo_maximo' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'doble_n_minimo_maximo' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'columna_normal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'columna_normal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'columna_normal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'columna_normal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'n_unico_hds5' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'n_unico_hds5' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'n_unico_hds5' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'n_unico_hds5' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `esviaje_max_grados`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 45.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 45.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 45.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 45.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 60.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 60.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 60.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 60.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `borde_libre_canal_m`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.3 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.3 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.3 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.3 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `long_max_cuneta`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 200.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 200.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 200.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 200.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 250.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 250.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 250.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 250.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `revestimiento_cuneta`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'concreto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'concreto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'concreto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'concreto' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'roca_dura' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'roca_dura' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'roca_dura' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'roca_dura' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'roca_blanda' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'roca_blanda' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'roca_blanda' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'roca_blanda' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'terreno_hierba' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'terreno_hierba' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'terreno_hierba' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'terreno_hierba' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'terreno_arcilla_grava' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'terreno_arcilla_grava' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'terreno_arcilla_grava' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'terreno_arcilla_grava' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'terreno_con_vegetacion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'terreno_con_vegetacion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'terreno_con_vegetacion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | VB1, VB2 | — | sí |
| 'terreno_con_vegetacion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'terreno_arena_arcillosa' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'terreno_arena_arcillosa' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'terreno_arena_arcillosa' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | VB1, VB2 | — | sí |
| 'terreno_arena_arcillosa' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'terreno_arena_fina_o_limo' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'terreno_arena_fina_o_limo' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'terreno_arena_fina_o_limo' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | VB1, VB2 | — | sí |
| 'terreno_arena_fina_o_limo' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `lectura_velocidad_limite_cuneta`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'extremo_inferior' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'extremo_inferior' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'extremo_inferior' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'extremo_inferior' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'extremo_superior' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'extremo_superior' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'extremo_superior' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'extremo_superior' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `obras_familia_a_extremo_de_cuneta`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'si' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'si' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'si' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'si' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'no' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'no' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'no' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'no' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `origen_cota_fondo_entrada`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cota_terreno' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cota_terreno' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cota_terreno' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cota_terreno' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'cota_fondo_entrada' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'cota_fondo_entrada' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'cota_fondo_entrada' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'cota_fondo_entrada' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `remanso_derecho_via`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cota_de_afectacion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cota_de_afectacion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cota_de_afectacion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cota_de_afectacion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'embalse_a_nivel' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1, V5, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'embalse_a_nivel' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V5, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'embalse_a_nivel' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V5, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'embalse_a_nivel' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'perfil_de_remanso_paso_a_paso' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'perfil_de_remanso_paso_a_paso' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (sobreelevacion_admisible_remanso_m) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'perfil_de_remanso_paso_a_paso' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (sobreelevacion_admisible_remanso_m) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'perfil_de_remanso_paso_a_paso' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `acceso_mantenimiento_v2b`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'camara_o_buzon_en_cabecera' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'camara_o_buzon_en_cabecera' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'camara_o_buzon_en_cabecera' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'camara_o_buzon_en_cabecera' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'acceso_por_cabezal_sin_obra_adicional' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'acceso_por_cabezal_sin_obra_adicional' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'acceso_por_cabezal_sin_obra_adicional' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'acceso_por_cabezal_sin_obra_adicional' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'sin_acceso_declarado_como_limitacion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'sin_acceso_declarado_como_limitacion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'sin_acceso_declarado_como_limitacion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'sin_acceso_declarado_como_limitacion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `pendiente_minima_conducto`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.005 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.005 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.005 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.005 | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | V10 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `pendiente_maxima_conducto`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.1 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.1 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.1 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.1 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.02 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.02 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.02 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.02 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `phi_relleno_trasdos`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 34.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 34.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 34.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 34.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 30.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E3-ASD.sis.s.alero.100 | — | sí |
| 30.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero.75 | — | sí |
| 30.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero | — | sí |
| 30.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.75, E3-ASD.sis.s.alero.50 | — | sí |
| 38.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.75 | — | sí |
| 38.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.100 | — | sí |
| 38.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero, E3-ASD.sis.s.alero.25 | — | sí |
| 38.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.75, E1-ASD.sis.s.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.s.alero.75 | — | sí |

### `demanda_sismica_licuefaccion`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1000 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1000 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1000 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1000 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 475 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 475 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 475 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 475 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `diametro_de_diseno_concreto`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'designado' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'designado' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'designado' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'designado' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'designado_o_ingles_convertido' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'designado_o_ingles_convertido' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'designado_o_ingles_convertido' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'designado_o_ingles_convertido' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `condicion_pavimento`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'flexible' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'flexible' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'flexible' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'flexible' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'no_pavimentado' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'no_pavimentado' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'no_pavimentado' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'no_pavimentado' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'rigido' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'rigido' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'rigido' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'rigido' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `corrugacion_y_espesor_tmc`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| '68x13/2.01' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '68x13/2.01' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '68x13/2.01' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '68x13/2.01' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '68x13/1.32' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '68x13/1.32' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '68x13/1.32' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '68x13/1.32' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '68x13/1.63' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '68x13/1.63' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '68x13/1.63' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '68x13/1.63' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '68x13/2.77' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '68x13/2.77' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '68x13/2.77' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '68x13/2.77' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '68x13/3.51' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '68x13/3.51' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '68x13/3.51' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '68x13/3.51' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '68x13/4.27' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '68x13/4.27' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '68x13/4.27' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '68x13/4.27' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '75x25/1.32' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '75x25/1.32' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '75x25/1.32' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '75x25/1.32' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '75x25/1.63' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '75x25/1.63' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '75x25/1.63' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '75x25/1.63' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '75x25/2.01' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '75x25/2.01' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '75x25/2.01' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '75x25/2.01' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '75x25/2.77' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '75x25/2.77' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '75x25/2.77' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '75x25/2.77' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '75x25/3.51' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '75x25/3.51' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '75x25/3.51' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '75x25/3.51' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '75x25/4.27' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '75x25/4.27' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '75x25/4.27' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '75x25/4.27' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '125x25/1.63' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '125x25/1.63' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '125x25/1.63' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '125x25/1.63' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '125x25/2.01' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '125x25/2.01' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '125x25/2.01' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '125x25/2.01' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '125x25/2.77' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '125x25/2.77' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '125x25/2.77' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '125x25/2.77' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '125x25/3.51' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '125x25/3.51' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '125x25/3.51' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '125x25/3.51' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| '125x25/4.27' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| '125x25/4.27' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| '125x25/4.27' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| '125x25/4.27' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `suelo_agresivo_lrfd_sobre_tmc`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'aviso' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'aviso' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'aviso' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'aviso' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'excluye' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'excluye' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'excluye' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'excluye' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `relleno_max_contraste_acpa_m`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.6096 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.6096 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.6096 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6096 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `peso_especifico_relleno_kn_m3`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 17.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 17.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 17.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 17.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 20.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e.alero.100, E3-ASD.sis.e.alero | — | sí |
| 20.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 20.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 20.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.100 | — | sí |

### `nivel_agua_diseno_v7`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'en_la_clave' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'en_la_clave' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'en_la_clave' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'en_la_clave' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'nf_del_punto' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'nf_del_punto' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (margen_estacional_nf_v7_m) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'nf_del_punto' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (margen_estacional_nf_v7_m) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'nf_del_punto' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (margen_estacional_nf_v7_m) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `fabricacion_tmc`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'anular_remachada_simple' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'anular_remachada_simple' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'anular_remachada_simple' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'anular_remachada_simple' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'helicoidal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'helicoidal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'helicoidal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'helicoidal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'anular_remachada_doble' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'anular_remachada_doble' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'anular_remachada_doble' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'anular_remachada_doble' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'anular_empernada' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'anular_empernada' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'anular_empernada' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'anular_empernada' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `relleno_estructural_hdpe`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'Si-95' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'Si-95' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'Si-95' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'Si-95' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'Sn-100' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'Sn-100' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'Sn-100' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'Sn-100' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'Sn-95' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'Sn-95' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'Sn-95' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'Sn-95' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'Cl-95' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'Cl-95' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'Cl-95' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'Cl-95' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `carga_viva_tubo_concreto_somero`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'largo_del_neumatico' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'largo_del_neumatico' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'largo_del_neumatico' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'largo_del_neumatico' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'e_span_a_un_pie' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'e_span_a_un_pie' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'e_span_a_un_pie' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'e_span_a_un_pie' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `talud_terraplen`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 2.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 2.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 2.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 2.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero.25 | — | sí |
| 1.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero.25 | — | sí |
| 1.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.25, E3-ASD.sis.s.alero.25 | — | sí |
| 1.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e.alero.75, E3-ASD.sis.e.alero.25 | — | sí |

### `espesor_proteccion_salida`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.75 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.75 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.75 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.75 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 2.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 2.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 2.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 2.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `longitud_proteccion_salida`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 5.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 5.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 5.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 5.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 3.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 3.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 3.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 3.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 8.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 8.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 8.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 8.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `tipo_proteccion_entrada`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'emboquillado_de_piedra' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'emboquillado_de_piedra' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'emboquillado_de_piedra' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'emboquillado_de_piedra' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'enchapado_de_roca_acomodada' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'enchapado_de_roca_acomodada' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'enchapado_de_roca_acomodada' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'enchapado_de_roca_acomodada' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'otro_revestimiento' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'otro_revestimiento' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'otro_revestimiento' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'otro_revestimiento' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `lectura_coeficientes_socavacion_hec14`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'envolvente_de_filas_vecinas' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'envolvente_de_filas_vecinas' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'envolvente_de_filas_vecinas' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'envolvente_de_filas_vecinas' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'interpolacion_lineal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'interpolacion_lineal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'interpolacion_lineal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'interpolacion_lineal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `regla_espesor_longitud_proteccion_salida`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'envolvente_hec14' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'envolvente_hec14' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'envolvente_hec14' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'envolvente_hec14' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'manual' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'manual' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'manual' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'manual' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `relacion_co_poza_enrocado_hec14`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'envolvente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'envolvente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'envolvente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'envolvente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'mejor_ajuste' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'mejor_ajuste' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'mejor_ajuste' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'mejor_ajuste' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `referencia_profundidad_socavacion`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'fondo_del_cauce_receptor' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'fondo_del_cauce_receptor' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'fondo_del_cauce_receptor' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'fondo_del_cauce_receptor' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'solera_de_salida' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.s, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75 | — | sí |
| 'solera_de_salida' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.s.alero.100, E3-ASD.sis.s, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75 | — | sí |
| 'solera_de_salida' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E3-ASD.sis.s.alero | — | sí |
| 'solera_de_salida' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50 | — | sí |

### `regimen_cortante_muro_e060_art_11_10_2`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'perpendicular_al_plano' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'perpendicular_al_plano' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'perpendicular_al_plano' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'perpendicular_al_plano' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'en_el_plano' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'en_el_plano' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'en_el_plano' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'en_el_plano' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `margen_zapata_bajo_socavacion_m`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.6096 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A5.talon_alero_100.s, E3-ASD.sis.s, E3-ASD.sis.s.alero.100 | — | sí |
| 0.6096 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.s, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75 | — | sí |
| 0.6096 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6096 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E3-ASD.sis.s.alero.50 | — | sí |

### `umbral_no_colapso_evento_extremo`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'sin_desborde_de_la_plataforma' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'sin_desborde_de_la_plataforma' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'sin_desborde_de_la_plataforma' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'sin_desborde_de_la_plataforma' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'desborde_admitido_con_terraplen_protegido' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | V1 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'desborde_admitido_con_terraplen_protegido' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (caudal_unitario_admisible_desborde_m2s) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'desborde_admitido_con_terraplen_protegido' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 297 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (caudal_unitario_admisible_desborde_m2s) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'desborde_admitido_con_terraplen_protegido' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 389 cambian o desaparecen) | CriterioPendienteError: material y diametro (bucle de MD) (caudal_unitario_admisible_desborde_m2s) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `terreno_delante_del_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'horizontal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'horizontal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'horizontal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'horizontal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'talud_descendente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'talud_descendente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'talud_descendente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |
| 'talud_descendente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.est.e, E1-ASD.est.e.alero, E1-ASD.est.e.alero.100, E1-ASD.est.e.alero.25, E1-ASD.est.e.alero.50, E1-ASD.est.e.alero.75, E1-ASD.est.s, E1-ASD.est.s.alero, E1-ASD.est.s.alero.100, E1-ASD.est.s.alero.25, E1-ASD.est.s.alero.50, E1-ASD.est.s.alero.75, E1-ASD.sis.e, E1-ASD.sis.e.alero, E1-ASD.sis.e.alero.100, E1-ASD.sis.e.alero.25, E1-ASD.sis.e.alero.50, E1-ASD.sis.e.alero.75, E1-ASD.sis.s, E1-ASD.sis.s.alero, E1-ASD.sis.s.alero.100, E1-ASD.sis.s.alero.25, E1-ASD.sis.s.alero.50, E1-ASD.sis.s.alero.75, E1-LRFD.est.e, E1-LRFD.est.e.alero, E1-LRFD.est.e.alero.100, E1-LRFD.est.e.alero.25, E1-LRFD.est.e.alero.50, E1-LRFD.est.e.alero.75, E1-LRFD.est.s, E1-LRFD.est.s.alero, E1-LRFD.est.s.alero.100, E1-LRFD.est.s.alero.25, E1-LRFD.est.s.alero.50, E1-LRFD.est.s.alero.75, E1-LRFD.sis.e, E1-LRFD.sis.e.alero, E1-LRFD.sis.e.alero.100, E1-LRFD.sis.e.alero.25, E1-LRFD.sis.e.alero.50, E1-LRFD.sis.e.alero.75, E1-LRFD.sis.s, E1-LRFD.sis.s.alero, E1-LRFD.sis.s.alero.100, E1-LRFD.sis.s.alero.25, E1-LRFD.sis.s.alero.50, E1-LRFD.sis.s.alero.75, E2-ASD.est.e, E2-ASD.est.e.alero, E2-ASD.est.e.alero.100, E2-ASD.est.e.alero.25, E2-ASD.est.e.alero.50, E2-ASD.est.e.alero.75, E2-ASD.est.s, E2-ASD.est.s.alero, E2-ASD.est.s.alero.100, E2-ASD.est.s.alero.25, E2-ASD.est.s.alero.50, E2-ASD.est.s.alero.75, E2-ASD.sis.e, E2-ASD.sis.e.alero, E2-ASD.sis.e.alero.100, E2-ASD.sis.e.alero.25, E2-ASD.sis.e.alero.50, E2-ASD.sis.e.alero.75, E2-ASD.sis.s, E2-ASD.sis.s.alero, E2-ASD.sis.s.alero.100, E2-ASD.sis.s.alero.25, E2-ASD.sis.s.alero.50, E2-ASD.sis.s.alero.75, E2-LRFD.est.e, E2-LRFD.est.e.alero, E2-LRFD.est.e.alero.100, E2-LRFD.est.e.alero.25, E2-LRFD.est.e.alero.50, E2-LRFD.est.e.alero.75, E2-LRFD.est.s, E2-LRFD.est.s.alero, E2-LRFD.est.s.alero.100, E2-LRFD.est.s.alero.25, E2-LRFD.est.s.alero.50, E2-LRFD.est.s.alero.75, E2-LRFD.sis.e, E2-LRFD.sis.e.alero, E2-LRFD.sis.e.alero.100, E2-LRFD.sis.e.alero.25, E2-LRFD.sis.e.alero.50, E2-LRFD.sis.e.alero.75, E2-LRFD.sis.s, E2-LRFD.sis.s.alero, E2-LRFD.sis.s.alero.100, E2-LRFD.sis.s.alero.25, E2-LRFD.sis.s.alero.50, E2-LRFD.sis.s.alero.75, E3-ASD.est.e, E3-ASD.est.e.alero, E3-ASD.est.e.alero.100, E3-ASD.est.e.alero.25, E3-ASD.est.e.alero.50, E3-ASD.est.e.alero.75, E3-ASD.est.s, E3-ASD.est.s.alero, E3-ASD.est.s.alero.100, E3-ASD.est.s.alero.25, E3-ASD.est.s.alero.50, E3-ASD.est.s.alero.75, E3-ASD.sis.e, E3-ASD.sis.e.alero, E3-ASD.sis.e.alero.100, E3-ASD.sis.e.alero.25, E3-ASD.sis.e.alero.50, E3-ASD.sis.e.alero.75, E3-ASD.sis.s, E3-ASD.sis.s.alero, E3-ASD.sis.s.alero.100, E3-ASD.sis.s.alero.25, E3-ASD.sis.s.alero.50, E3-ASD.sis.s.alero.75, E3-LRFD.est.e, E3-LRFD.est.e.alero, E3-LRFD.est.e.alero.100, E3-LRFD.est.e.alero.25, E3-LRFD.est.e.alero.50, E3-LRFD.est.e.alero.75, E3-LRFD.est.s, E3-LRFD.est.s.alero, E3-LRFD.est.s.alero.100, E3-LRFD.est.s.alero.25, E3-LRFD.est.s.alero.50, E3-LRFD.est.s.alero.75, E3-LRFD.sis.e, E3-LRFD.sis.e.alero, E3-LRFD.sis.e.alero.100, E3-LRFD.sis.e.alero.25, E3-LRFD.sis.e.alero.50, E3-LRFD.sis.e.alero.75, E3-LRFD.sis.s, E3-LRFD.sis.s.alero, E3-LRFD.sis.s.alero.100, E3-LRFD.sis.s.alero.25, E3-LRFD.sis.s.alero.50, E3-LRFD.sis.s.alero.75 | — | sí |

### `factores_forma_profundidad_portante`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'corrida_sin_profundidad' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'corrida_sin_profundidad' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'corrida_sin_profundidad' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'corrida_sin_profundidad' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'forma_con_la_longitud_del_cabezal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.s | — | sí |
| 'forma_con_la_longitud_del_cabezal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.s, E3-ASD.sis.s.alero.100 | — | sí |
| 'forma_con_la_longitud_del_cabezal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'forma_con_la_longitud_del_cabezal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'forma_y_profundidad' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.e.alero.75 | — | sí |
| 'forma_y_profundidad' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.s, E3-ASD.sis.s.alero.100 | — | sí |
| 'forma_y_profundidad' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'forma_y_profundidad' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `acero_refuerzo_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'A615_grado_60' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'A615_grado_60' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'A615_grado_60' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'A615_grado_60' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'A706_grado_60' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'A706_grado_60' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'A706_grado_60' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'A706_grado_60' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `regla_minimos_constructivos_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'mas_exigente_aashto_e060' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'mas_exigente_aashto_e060' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'mas_exigente_aashto_e060' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'mas_exigente_aashto_e060' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'solo_aashto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'solo_aashto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'solo_aashto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'solo_aashto' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `criterio_traccion_cabezal_ciclopeo`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'tracciones_nulas' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'tracciones_nulas' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'tracciones_nulas' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'tracciones_nulas' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'traccion_admisible_e060' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'traccion_admisible_e060' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'traccion_admisible_e060' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'traccion_admisible_e060' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `clase_exposicion_fisuracion_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'clase_2' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'clase_2' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'clase_2' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'clase_2' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'clase_1' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'clase_1' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'clase_1' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'clase_1' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `junta_arranque_cabezal_ciclopeo`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'junta_de_construccion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'junta_de_construccion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'junta_de_construccion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'junta_de_construccion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'vaciado_monolitico' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'vaciado_monolitico' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'vaciado_monolitico' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'vaciado_monolitico' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `metodo_longitud_conducto`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'por_extremo' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'por_extremo' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'por_extremo' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'por_extremo' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'terraplen_simetrico' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-ASD.sis.e.alero | — | sí |
| 'terraplen_simetrico' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.e.alero | — | sí |
| 'terraplen_simetrico' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'terraplen_simetrico' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.s.alero.100 | — | sí |

### `desnivel_minimo_entrega_m`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.3 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.3 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.3 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.3 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `desajuste_empalme_canal_m`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.01 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.01 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.01 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.01 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.02 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.02 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.02 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.02 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `momento_talon_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'exacto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'exacto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'exacto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'exacto' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'peso_entero' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon_alero.s, A2.talon_alero_25.s, A2.talon_alero_50.s | — | sí |
| 'peso_entero' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-ASD.sis.s.alero.100 | — | sí |
| 'peso_entero' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'peso_entero' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `carga_pantalla_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cuna_sobre_la_pantalla' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cuna_sobre_la_pantalla' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cuna_sobre_la_pantalla' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cuna_sobre_la_pantalla' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'plano_virtual_del_talon' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'plano_virtual_del_talon' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'plano_virtual_del_talon' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'plano_virtual_del_talon' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `distribucion_incremento_sismico`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'segun_regimen' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'segun_regimen' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'segun_regimen' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'segun_regimen' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'fraccion_de_h' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'fraccion_de_h' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'fraccion_de_h' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e.alero.100, E3-ASD.sis.s.alero.25 | — | sí |
| 'fraccion_de_h' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'distribucion_estatica' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'distribucion_estatica' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'distribucion_estatica' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'distribucion_estatica' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `empuje_sismico_muro_que_no_cede`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'reposo_mas_incremento' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'reposo_mas_incremento' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'reposo_mas_incremento' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'reposo_mas_incremento' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'mayor_de_reposo_y_total' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'mayor_de_reposo_y_total' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'mayor_de_reposo_y_total' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'mayor_de_reposo_y_total' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `agua_del_relleno_bajo_sismo`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'se_mueve_con_el_suelo' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'se_mueve_con_el_suelo' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'se_mueve_con_el_suelo' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'se_mueve_con_el_suelo' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'relleno_muy_abierto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'relleno_muy_abierto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'relleno_muy_abierto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'relleno_muy_abierto' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `clase_concreto_losa_entrega`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **LEÍDO, SIN EFECTO MEDIBLE**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'E' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'E' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'E' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'E' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'C' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'C' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'C' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'C' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'D' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'D' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'D' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'D' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'F' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'F' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'F' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'F' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'G' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'G' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'G' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'G' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

## 5. Los criterios que no se barren, por nombre

97 barridos sobre 95 criterios; estos 74 no se barren, y la razón:

| Criterio | Etiqueta | Por qué no se barre |
|---|---|---|
| `PERFIL_SUELO_PRESUNTO` | [S] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `clase_sitio` | [S] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `F_pga` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `k_v` | [A] | forma compuesta (categoria o numero) con la ventana en prosa: ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `pendiente_relleno_trasdos_i` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
| `fraccion_fin_remanso_canal` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
| `friccion_muro_suelo_delta` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
| `riesgo_admisible_propietario` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
| `coeficiente_escorrentia_superficie_vial` | [C] | Derivada de otros criterios o del registro: no se declara |
| `hds5_embocadura_hdpe` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `metodo_transicion_hds5` | [C] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `n_manning_hdpe` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `geometria_control_salida` | [C] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `velocidad_minima_autolimpieza_m_s` | [A] | sólo endurecible por encima de 0.25 m/s, sin techo: ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `resguardo_HW_subrasante` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `TW_receptor` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato del receptor (ANA / Junta), y con la sección de archivo de `seccion_receptor` nunca se lee |
| `seccion_cuneta` | [A] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ) |
| `dimensionamiento_zapata_cabezal` | [A] | valor de archivo del dueño (paso 0.10 m, tope 1.5·H_c, VE-3.9); ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ) |
| `TR_evento_extremo` | [A] | el juego lo declara (500 años) pero la ficha no tiene ventana: el TR del evento extremo lo fija el Propietario con el estudio hidrológico |
| `c_phi_fundacion` | [S] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `caudal_unitario_admisible_desborde_m2s` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer |
| `sobreelevacion_admisible_remanso_m` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; y el juego no lo lee (metodo de V5 sin perfil de remanso) |
| `fila_phi_estabilidad_global` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; y el juego no lo lee (sin FS de E4/E5 declarado) |
| `coeficientes_desborde_plataforma` | [C] | la Figura 3.11 del HDS-5 digitalizada (curvas por superficie); valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer; y el juego no lo lee (umbral sin desborde) |
| `capacidad_portante_adm` | [S] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `Mw_licuefaccion` | [A] | el juego lo declara (8.0, dato de prueba) pero no tiene ventana: dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `factores_idf_regional` | [S] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; y sólo los lee el caudal calculado con 'relacion_intensidad_duracion' = 'idf_regional_ec17' |
| `incremento_acero_por_despiece` | [A] | el juego lo declara (0.10, dato de prueba) pero la ficha no tiene ventana (lo fija el despiece de los planos); y sólo mueve el metrado del acero, que el anexo no compara |
| `sobreancho_excavacion_estructuras_m` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara; y sólo mueve el metrado de la excavación, que el anexo no compara |
| `techos_de_transcripcion_fase_6` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara; sin declarar no emite ningún aviso de transcripción |
| `diametros_normalizados` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `secciones_cajon_normalizadas` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `embocadura_cajon` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `n_celdas_cajon` | [A] | ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `ke_entrada_cajon` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `D_max_catalogo` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
| `cobertura_minima_aashto` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `cobertura_minima_cajon` | [A] | ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `h_eq_bajo_altura_tabulada` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; condicional que el juego no dispara (muro de menos de 1.524 m) |
| `h_eq_banda_intermedia_borde` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; condicional que el juego no dispara (trasdós a menos de 0.3048 m del borde) |
| `espesor_pared_conducto` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `D_max_norma_producto` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `durabilidad_tmc_umbrales` | [C] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ) |
| `sucs_fundacion_deficiente` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `suelo_agresivo_acero_lrfd` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `clases_producto_por_relleno` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `parametros_diseno_hdpe` | [A] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ) |
| `perfil_hdpe_fabricante` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
| `angulo_aletas` | [A] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ) |
| `factores_carga_aashto` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `peso_especifico_concreto_kn_m3` | [C] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `predimensionamiento_cabezal` | [A] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ). El campo que la lectura del cabezal de la regla pide, `fraccion_ancho_zapata` = 0.7, YA ES EL TECHO de su ventana (0.4–0.7): dentro de la ventana la zapata sólo puede achicarse, y una zapata más ancha se declara por punto (`cabezal_declarado`, variante `zapata_declarada_3m`) |
| `talud_delante_del_cabezal` | [S] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; condicional que el juego no dispara (terreno en talud delante del cabezal) |
| `metodo_estabilidad_global` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; E4 y E5 no se evalúan (ficha T7B-07) |
| `categoria_refuerzo_aashto` | [A] | el juego lo declara ('A'), pero su ventana es la lista de filas de la tabla con su descripción y la forma es `str`: su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `factor_recubrimiento_banda_intermedia_ac` | [C] | ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `exposicion_quimica_ems` | [S] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `situacion_recubrimiento_aashto` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `tabla_recubrimiento_aashto_mm` | [C] | Derivada de otros criterios o del registro: no se declara |
| `cortante_alto_muro_e060_art_11_10_10_2` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `cuantia_vertical_cortante_alto_e060_art_11_10_10_3` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `procedimiento_flexion_corte_aashto_sec5` | [C] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `dentellon_losa_entrega` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `profundidad_cimentacion_min_cabezal_m` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `peralte_min_zapata_armada_m` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `peso_especifico_saturado_relleno_kn_m3` | [S] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `catalogo_barras_refuerzo_cabezal` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `concreto_ciclopeo_cabezal` | [A] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ); ningún cabezal del juego es de gravedad |
| `espesor_min_zapata_concreto_simple_m` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `cuantia_minima_muro_e060` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `edicion_que_rige_el_expediente` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `edicion_legal_que_rige_el_expediente` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `margen_estacional_nf_v7_m` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `nivel_agua_relleno_sin_drenaje_bajo_sismo` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; condicional que el juego no dispara (trasdós sin drenaje declarado) |

