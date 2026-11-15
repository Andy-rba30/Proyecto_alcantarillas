# Sensibilidad de los criterios adoptados sobre el juego de prueba (T-11)

> **DOCUMENTO GENERADO — no se edita a mano.** Lo escribe `python -m tests.apoyo.sensibilidad --escribir` y `tests/test_t11_sensibilidad.py` lo regenera y lo compara. Cada barrido es `src/barrido.py` (PF-3) sobre el juego de **DATOS DE PRUEBA, NO DEL PROYECTO** de la validación integral, a `--alcance expediente`. **Ningún valor de archivo cambia**: un barrido declara cada valor para su corrida y deja el proceso como estaba.

## 1. Cómo leer este anexo

- **La base de los barridos es el juego tal como está**, la variante que ejercita la cadena sísmica y el caso drenado (`docs/validacion_integral.md` §2.1), y **no la corrida titular** (§2, con las decisiones de archivo): con `drenaje_trasdos` = 'sin_drenaje' la condición sísmica del cabezal es «método no evaluable» (ficha T7B-05), y hace falta una base donde el método sea evaluable para medir los [A] del cabezal. Lo que las dos decisiones de archivo hacen se lee en sus propios barridos (`drenaje_trasdos`, `factor_muro_eleccion`).
- **Primer valor = el efectivo en el juego** (el que el juego declara o el de archivo): su corrida es la del juego, y cada otra se compara con ella por el comparador de E-B. Los demás valores son los extremos de la ventana del criterio (`Criterio.sensibilidad`), o sus otras opciones.
- **MUEVE EL DISEÑO**: algún punto cambia de material o de sección, o deja de dimensionar. **MUEVE VEREDICTOS**: cambia el veredicto de alguna verificación del conducto, del cabezal o de la Fase 10. **MUEVE EL HW**: sólo cambia la carga que gobierna, en más de 5e-05 m (media unidad de la cuarta cifra con que se imprime). **LEÍDO, SIN EFECTO MEDIBLE** quiere decir que la corrida lee el criterio y que no cambian ni el material, ni la sección, ni ningún veredicto, ni el HW que gobierna: **las demás magnitudes no se comparan** (la hoya de socavación, el espesor y la longitud de la protección, las longitudes, los márgenes, el armado), y pueden cambiar. **NO LO LEE LA CORRIDA**: la clave no está entre los criterios usados de ninguna corrida del barrido, y barrerla no mueve nada en ESTE juego (la razón, en la tabla).
- **La lista se deriva del censo**: se barre todo criterio con valor efectivo en el juego y ventana legible por máquina (una categoría cerrada o dos extremos numéricos), más los que necesitan valores propios. Los que no se barren están en §5, **por nombre y con su razón**. Un barrido mide UNA clave a la vez, sobre UN juego: no es el producto cartesiano ni dice nada de otro sitio.

## 2. Resumen

| Grupo | Criterio | Etiqueta | Ventana | Valores barridos | Base | Efecto | Detalle |
|---|---|---|---|---|---|---|---|
| conducto | `HW_D_max` | [A] | 1.2–1.5 | 1.5, 1.2 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `borde_libre_bajo_tw_ahogante` | [A] | no_cumple / aviso | 'no_cumple', 'aviso' | juego | NO LO LEE LA CORRIDA | el TW del juego (0.30 m sobre el fondo de la salida; 0.41 m en C-01) no supera el llenado admisible de V1 (0.75 de la altura: 0.675 m en el Ø 0.90 y en el marco de 0.90 m): la lectura sólo se pide cuando el nivel del receptor toma el borde libre |
| conducto | `seccion_receptor` | [A] | b_m 1.5–3.0; z_HV 1.0–2.0; S 0.0005–0.0015; n 0.025–0.035; altura_total_m 1.2–2.5 | sección de archivo, sección estrecha, sección ancha | juego | NO LO LEE LA CORRIDA | el juego declara `TW_m` (vía 1 de la Sec. 1.3), que manda sobre las vías 3 y 4, las únicas que usan la sección del receptor |
| conducto | `seccion_receptor` | [A] | b_m 1.5–3.0; z_HV 1.0–2.0; S 0.0005–0.0015; n 0.025–0.035; altura_total_m 1.2–2.5 | sección de archivo, sección estrecha, sección ancha | juego_sin_TW | MUEVE EL DISEÑO | diseño: A-01 con sección estrecha: no dimensiona → Concreto reforzado, Ø 0.90 m; A-02 con sección estrecha: no dimensiona → Concreto reforzado, Ø 0.90 m · veredictos que cambian: A-01 con sección estrecha: 105; A-02 con sección estrecha: 105 |
| conducto | `v_max_tmc` | [A] | 3.048–4.572 | 4.572, 3.048 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `v_max_hdpe` | [C] | 0.25–4.572 | 4.572, 0.25 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `v_max_concreto_eleccion` | [A] | 3.0–6.0 | 3.0, 6.0 | juego | MUEVE EL DISEÑO | diseño: A-01 con 3.0: Concreto reforzado, Ø 0.90 m (juego) → TMC galvanizada, Ø 1.20 m · veredictos que cambian: A-01 con 6.0: 6 |
| conducto | `v_max_concreto_eleccion` | [A] | 3.0–6.0 | 3.0, 6.0 | juego_tmc_excluida | MUEVE EL DISEÑO | diseño: A-01 con 3.0: Concreto reforzado, Ø 0.90 m (juego) → no dimensiona · veredictos que cambian: A-01 con 6.0: 105 |
| conducto | `regimen_v2b` | [A] | umbral_duro / indicador_con_aviso | 'indicador_con_aviso', 'umbral_duro' | juego | MUEVE EL DISEÑO | diseño: C-01 con 'umbral_duro': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: C-01 con 'umbral_duro': 106 |
| conducto | `hw_entrada_fuera_de_rango` | [A] | energia_critica / descartar | 'energia_critica', 'descartar' | juego | NO LO LEE LA CORRIDA | ningún punto queda fuera del rango de la corrección por pendiente (la carta da carga positiva en todos los escalones evaluados) |
| conducto | `n_manning_cajon` | [C] | 'concrete_boxes' / 'concreto_afinado' / num. B.3 del HDS-5 (cita HDS5_3ED.B.3#CAJON_IN_SITU): 0.012 a 0.022 en un cajon VACIADO IN SITU, segun el encofrado | 'concrete_boxes', 'concreto_afinado' | juego | MUEVE EL HW | HW: C-01 con 'concreto_afinado': 0.6231 → 0.6233 m |
| conducto | `espesor_pared_cajon` | [A] | EL SIGNO ES CONTRAINTUITIVO Y VA PRIMERO, porque quien declare este criterio va a suponer lo contrario: ENGROSAR LA PARED EMPEORA LA FLOTACION. Una pared mas gruesa parece mas estructura y por tanto mas seguridad, y con `DC = 0` / HACIA ABAJO el limite no es la flotacion sino el propio calculo estructural, que este alcance difiere: una pared que flota mejor puede no resistir el empuje de tierras ni la carga viva. Por eso la ventana no se puede cerrar a nivel de perfil y el criterio se ADOPTA en vez de optimizarse: el optimo de V7 y el minimo estructural empujan en sentidos opuestos y solo la Fase 8 tiene los dos numeros / VENTANA DE LA ADOPCION (T-3): 0.20 m | 0.2, 0.25, 0.3 | juego | MUEVE EL DISEÑO | diseño: C-01 con 0.3: Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: C-01 con 0.3: 106 |
| conducto | `borde_libre_y_sobre_d_max` | [A] | 0.0–0.75 | 0.75, 0.6, 0.0 | juego | MUEVE EL DISEÑO | diseño: A-01 con 0.6: Concreto reforzado, Ø 0.90 m → Concreto reforzado, Ø 1.05 m; A-01 con 0.0: Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 0.0: Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 0.0: Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 0.0: Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 0.6: 1; A-01 con 0.0: 105; A-02 con 0.0: 105; B-01 con 0.0: 105; C-01 con 0.0: 106 |
| conducto | `ke_entrada` | [C] | 0.2–0.9 | 0.5, 0.2, 0.9 | juego | MUEVE EL HW | HW: A-01 con 0.9: 1.0420 → 1.0618 m |
| conducto | `embocadura_cabezal` | [A] | cabezal_con_aleros / cabezal_recto | 'cabezal_con_aleros', 'cabezal_recto' | juego | MUEVE EL DISEÑO | diseño: C-01 con 'cabezal_recto': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'cabezal_recto': 12; A-02 con 'cabezal_recto': 12; B-01 con 'cabezal_recto': 12; C-01 con 'cabezal_recto': 106 |
| conducto | `fraccion_llena_mayor_parte` | [A] | 0.5–0.9 | 0.5, 0.9 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `instalacion_estandar_concreto` | [A] | tipo_1 / tipo_2 / tipo_3 / tipo_4 | 'tipo_3', 'tipo_1', 'tipo_2', 'tipo_4' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `carga_viva_bajo_relleno_alto` | [A] | conservar / despreciar_3_6_1_2_6a | 'conservar', 'despreciar_3_6_1_2_6a' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `eta_importancia_operativa_conducto` | [A] | 0.95–1.05 | 1.05, 0.95 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.95: 2 |
| cabezal | `factor_muro_eleccion` | [A] | sin_reduccion / reduccion_por_desplazamiento | 'reduccion_por_desplazamiento', 'sin_reduccion' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'sin_reduccion': 6; A-02 con 'sin_reduccion': 6; B-01 con 'sin_reduccion': 6; C-01 con 'sin_reduccion': 6 |
| cabezal | `gamma_EQ` | [A] | 0.0–1.0 | 0.5, 0.0, 1.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 1.0: 1; A-02 con 1.0: 1; B-01 con 1.0: 2; C-01 con 1.0: 1 |
| cabezal | `fraccion_delta_sobre_phi_trasdos` | [C] | 0.33–0.67 | 0.67, 0.33 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.33: 7; A-02 con 0.33: 7; B-01 con 0.33: 10; C-01 con 0.33: 5 |
| cabezal | `fila_phi_estabilidad_cabezal` | [A] | zapatas_seccion_10 / muros_tabla_11_5_7 | 'zapatas_seccion_10', 'muros_tabla_11_5_7' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'muros_tabla_11_5_7': 1; A-02 con 'muros_tabla_11_5_7': 1; C-01 con 'muros_tabla_11_5_7': 1 |
| cabezal | `factores_inclinacion_carga_portante` | [A] | aplicar / omitir | 'aplicar', 'omitir' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'omitir': 4; A-02 con 'omitir': 4; B-01 con 'omitir': 4; C-01 con 'omitir': 4 |
| cabezal | `regla_pendiente_relleno_trasdos` | [A] | cuna_de_tanteo / talud_quebrado_2h / talud_del_terraplen | 'cuna_de_tanteo', 'talud_quebrado_2h', 'talud_del_terraplen' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'talud_quebrado_2h': 8; A-02 con 'talud_quebrado_2h': 2; B-01 con 'talud_quebrado_2h': 2; C-01 con 'talud_quebrado_2h': 4; A-01 con 'talud_del_terraplen': 17; A-02 con 'talud_del_terraplen': 19; B-01 con 'talud_del_terraplen': 19; C-01 con 'talud_del_terraplen': 17 |
| cabezal | `regimen_resistencia_elementos_cabezal` | [A] | no_cedente_k0 / cedente | 'no_cedente_k0', 'cedente' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'cedente': 2; A-02 con 'cedente': 6; B-01 con 'cedente': 2; C-01 con 'cedente': 4 |
| cabezal | `eta_ductilidad_cabezal` | [A] | 0.95–1.05 | 1.0, 0.95, 1.05 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.95: 2; B-01 con 1.05: 1 |
| cabezal | `eta_redundancia_cabezal` | [A] | 0.95–1.05 | 1.0, 0.95, 1.05 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.95: 2; B-01 con 1.05: 1 |
| cabezal | `marco_estabilidad_cabezal` | [A] | lrfd_rige_asd_informa / asd_rige_lrfd_informa / envolvente_de_los_dos | 'lrfd_rige_asd_informa', 'asd_rige_lrfd_informa', 'envolvente_de_los_dos' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'asd_rige_lrfd_informa': 8; A-02 con 'asd_rige_lrfd_informa': 8; B-01 con 'asd_rige_lrfd_informa': 8; C-01 con 'asd_rige_lrfd_informa': 8; A-01 con 'envolvente_de_los_dos': 4; A-02 con 'envolvente_de_los_dos': 4; B-01 con 'envolvente_de_los_dos': 4; C-01 con 'envolvente_de_los_dos': 4 |
| cabezal | `regimen_cabezal` | [A] | cedente / no_cedente | 'cedente', 'no_cedente' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'no_cedente': 24; A-02 con 'no_cedente': 24; B-01 con 'no_cedente': 24; C-01 con 'no_cedente': 24 |
| cabezal | `drenaje_trasdos` | [A] | sin_drenaje / drenado | 'drenado', 'sin_drenaje' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'sin_drenaje': 26; A-02 con 'sin_drenaje': 22; B-01 con 'sin_drenaje': 22; C-01 con 'sin_drenaje': 26 |
| cabezal | `fc_cabezal_mpa` | [A] | 17.5–35.0 | 21.0, 17.5, 35.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 17.5: 6; C-01 con 17.5: 2; A-01 con 35.0: 1; A-02 con 35.0: 4; B-01 con 35.0: 2; C-01 con 35.0: 2 |
| cabezal | `duracion_caudal_pico_socavacion_min` | [A] | 30.0–360.0 | 360.0, 30.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `F_pga_lectura_columna_extrema` | [A] | limite_inclusive / limite_estricto | 'limite_inclusive', 'limite_estricto' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'limite_estricto': 64; A-02 con 'limite_estricto': 64; B-01 con 'limite_estricto': 64; C-01 con 'limite_estricto': 64 |
| cabezal | `inclinacion_muro_beta` | [A] | 0.0–10.0 | 0.0, 10.0 | juego | NO LO LEE LA CORRIDA | sólo lo lee la vía de contraste de Coulomb / Mononobe-Okabe; el empuje que rige sale de la cuña de tanteo sobre el plano vertical del talón |
| cabezal | `punto_aplicacion_incremento_sismico` | [C] | 0.333–0.6 | 0.6, 0.333 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.333: 1; A-02 con 0.333: 1; C-01 con 0.333: 1 |
| hidrología | `homogeneidad_serie_fen` | [A] | serie_completa / serie_sin_fen / dos_poblaciones | 'serie_completa', 'serie_sin_fen', 'dos_poblaciones' | juego | NO LO LEE LA CORRIDA | sólo lo lee el caudal CALCULADO; en el juego el caudal es el declarado del CSV (lo mide la variante `caudal_calculado_sin_fen` de `docs/validacion_integral.md`) |
| sin consumidor | `umbral_area_quebrada_importante_ha` | [A] | 50.0–200.0 | 100.0, 50.0, 200.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| hidrología | `distribucion_precipitacion_maxima` | [A] | mejor_ajuste_ks / normal / lognormal_2p / gumbel / lognormal_3p / gamma_2p / gamma_3p / log_pearson_3 / log_gumbel | 'mejor_ajuste_ks', 'normal', 'lognormal_2p', 'gumbel', 'lognormal_3p', 'gamma_2p', 'gamma_3p', 'log_pearson_3', 'log_gumbel' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado, y en el juego el caudal es el declarado |
| hidrología | `nivel_significancia_ks` | [A] | 0.01–0.1 | 0.05, 0.01, 0.1 | juego | NO LO LEE LA CORRIDA | hidrología: sólo lo lee el caudal calculado |
| hidrología | `relacion_intensidad_duracion` | [A] | dick_peschke / tabla_04_coeficientes_de_duracion | 'dick_peschke', 'tabla_04_coeficientes_de_duracion' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado |
| hidrología | `duracion_minima_lluvia_min` | [C] | 5.0–15.0 | 5.0, 15.0 | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado |
| hidrología | `tc_fuera_de_la_poblacion_del_metodo` | [A] | no_evaluable / indicador_con_aviso | 'no_evaluable', 'indicador_con_aviso' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado |
| hidrología | `coeficiente_uniformidad_temez` | [A] | aplicar / no_aplicar | 'aplicar', 'no_aplicar' | juego | NO LO LEE LA CORRIDA | hidrología: sólo la lee el caudal calculado con Témez |
| conducto | `esviaje_max_grados` | [A] | 45.0–60.0 | 45.0, 60.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `borde_libre_canal_m` | [A] | 0.3–0.5 | 0.5, 0.3 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cuneta | `long_max_cuneta` | [A] | 200.0–250.0 | 200.0, 250.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cuneta | `revestimiento_cuneta` | [A] | concreto / roca_dura / roca_blanda / terreno_hierba / terreno_arcilla_grava / terreno_con_vegetacion / terreno_arena_arcillosa / terreno_arena_fina_o_limo | 'concreto', 'roca_dura', 'roca_blanda', 'terreno_hierba', 'terreno_arcilla_grava', 'terreno_con_vegetacion', 'terreno_arena_arcillosa', 'terreno_arena_fina_o_limo' | juego | MUEVE VEREDICTOS | veredictos que cambian: B-01 con 'terreno_con_vegetacion': 2; B-01 con 'terreno_arena_arcillosa': 2; B-01 con 'terreno_arena_fina_o_limo': 2 |
| cuneta | `lectura_velocidad_limite_cuneta` | [A] | extremo_inferior / extremo_superior | 'extremo_inferior', 'extremo_superior' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cuneta | `obras_familia_a_extremo_de_cuneta` | [A] | si / no | 'si', 'no' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `origen_cota_fondo_entrada` | [A] | cota_terreno / cota_fondo_entrada | 'cota_terreno', 'cota_fondo_entrada' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'cota_fondo_entrada': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'cota_fondo_entrada': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'cota_fondo_entrada': Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 'cota_fondo_entrada': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'cota_fondo_entrada': 105; A-02 con 'cota_fondo_entrada': 105; B-01 con 'cota_fondo_entrada': 105; C-01 con 'cota_fondo_entrada': 106 |
| conducto | `remanso_derecho_via` | [A] | embalse_a_nivel / cota_de_afectacion / perfil_de_remanso_paso_a_paso | 'cota_de_afectacion', 'embalse_a_nivel', 'perfil_de_remanso_paso_a_paso' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'embalse_a_nivel': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'embalse_a_nivel': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'embalse_a_nivel': Concreto reforzado, Ø 0.90 m → no dimensiona; A-01 con 'perfil_de_remanso_paso_a_paso': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'perfil_de_remanso_paso_a_paso': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'perfil_de_remanso_paso_a_paso': Concreto reforzado, Ø 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'embalse_a_nivel': 105; A-02 con 'embalse_a_nivel': 105; B-01 con 'embalse_a_nivel': 105; A-01 con 'perfil_de_remanso_paso_a_paso': 105; A-02 con 'perfil_de_remanso_paso_a_paso': 105; B-01 con 'perfil_de_remanso_paso_a_paso': 105 |
| conducto | `acceso_mantenimiento_v2b` | [A] | camara_o_buzon_en_cabecera / acceso_por_cabezal_sin_obra_adicional / sin_acceso_declarado_como_limitacion | 'camara_o_buzon_en_cabecera', 'acceso_por_cabezal_sin_obra_adicional', 'sin_acceso_declarado_como_limitacion' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `pendiente_minima_conducto` | [A] | 0.0–0.005 | 0.0, 0.005 | juego | MUEVE EL DISEÑO | diseño: C-01 con 0.005: Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: C-01 con 0.005: 106 |
| conducto | `pendiente_maxima_conducto` | [A] | 0.02–0.1 | 0.1, 0.02 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `phi_relleno_trasdos` | [A] | 30.0–38.0 | 34.0, 30.0, 38.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 30.0: 13; A-02 con 30.0: 6; B-01 con 30.0: 8; C-01 con 30.0: 7; A-01 con 38.0: 2; A-02 con 38.0: 4; B-01 con 38.0: 3; C-01 con 38.0: 5 |
| sin consumidor | `demanda_sismica_licuefaccion` | [A] | 475–1000 | 1000, 475 | juego | NO LO LEE LA CORRIDA | sin consumidor (`SIN_CONSUMIDOR_Y_SIN_MEDIDA`): la licuefacción no se evalúa |
| conducto | `condicion_pavimento` | [A] | no_pavimentado / flexible / rigido | 'flexible', 'no_pavimentado', 'rigido' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `corrugacion_y_espesor_tmc` | [A] | 68x13/1.32 / 68x13/1.63 / 68x13/2.01 / 68x13/2.77 / 68x13/3.51 / 68x13/4.27 / 75x25/1.32 / 75x25/1.63 / 75x25/2.01 / 75x25/2.77 / 75x25/3.51 / 75x25/4.27 / 125x25/1.63 / 125x25/2.01 / 125x25/2.77 / 125x25/3.51 / 125x25/4.27 | '68x13/2.01', '68x13/1.32', '68x13/1.63', '68x13/2.77', '68x13/3.51', '68x13/4.27', '75x25/1.32', '75x25/1.63', '75x25/2.01', '75x25/2.77', '75x25/3.51', '75x25/4.27', '125x25/1.63', '125x25/2.01', '125x25/2.77', '125x25/3.51', '125x25/4.27' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `suelo_agresivo_lrfd_sobre_tmc` | [A] | aviso / excluye | 'aviso', 'excluye' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `peso_especifico_relleno_kn_m3` | [A] | 17.0–20.0 | 17.0, 20.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 20.0: 11; A-02 con 20.0: 4; B-01 con 20.0: 6; C-01 con 20.0: 2 |
| conducto | `fabricacion_tmc` | [A] | helicoidal / anular_remachada_simple / anular_remachada_doble / anular_empernada | 'anular_remachada_simple', 'helicoidal', 'anular_remachada_doble', 'anular_empernada' | juego | NO LO LEE LA CORRIDA | ningún punto adopta TMC: el concreto es el primer candidato |
| conducto | `relleno_estructural_hdpe` | [A] | Sn-100 / Sn-95 / Si-95 / Cl-95 | 'Si-95', 'Sn-100', 'Sn-95', 'Cl-95' | juego | NO LO LEE LA CORRIDA | ningún punto adopta HDPE: el concreto es el primer candidato |
| conducto | `talud_terraplen` | [A] | 1.5–2.0 | 2.0, 1.5 | juego | MUEVE VEREDICTOS | veredictos que cambian: B-01 con 1.5: 1 |
| protección | `espesor_proteccion_salida` | [A] | 1.5–2.0 | 1.75, 1.5, 2.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `longitud_proteccion_salida` | [A] | 3.0–8.0 | 5.0, 3.0, 8.0 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `tipo_proteccion_entrada` | [A] | emboquillado_de_piedra / enchapado_de_roca_acomodada / otro_revestimiento | 'emboquillado_de_piedra', 'enchapado_de_roca_acomodada', 'otro_revestimiento' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `lectura_coeficientes_socavacion_hec14` | [A] | envolvente_de_filas_vecinas / interpolacion_lineal | 'envolvente_de_filas_vecinas', 'interpolacion_lineal' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'interpolacion_lineal': 1 |
| protección | `regla_espesor_longitud_proteccion_salida` | [A] | manual / envolvente_hec14 | 'envolvente_hec14', 'manual' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| protección | `referencia_profundidad_socavacion` | [A] | fondo_del_cauce_receptor / solera_de_salida | 'fondo_del_cauce_receptor', 'solera_de_salida' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'solera_de_salida': 5; A-02 con 'solera_de_salida': 4; B-01 con 'solera_de_salida': 2; C-01 con 'solera_de_salida': 2 |
| cabezal | `regimen_cortante_muro_e060_art_11_10_2` | [A] | en_el_plano / perpendicular_al_plano | 'perpendicular_al_plano', 'en_el_plano' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `margen_zapata_bajo_socavacion_m` | [C] | 0.0–0.6096 | 0.6096, 0.0 | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 0.0: 5; A-02 con 0.0: 6; B-01 con 0.0: 4; C-01 con 0.0: 3 |
| conducto | `umbral_no_colapso_evento_extremo` | [A] | sin_desborde_de_la_plataforma / desborde_admitido_con_terraplen_protegido | 'sin_desborde_de_la_plataforma', 'desborde_admitido_con_terraplen_protegido' | juego | MUEVE EL DISEÑO | diseño: A-01 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, Ø 0.90 m → no dimensiona; A-02 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, Ø 0.90 m → no dimensiona; B-01 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, Ø 0.90 m → no dimensiona; C-01 con 'desborde_admitido_con_terraplen_protegido': Concreto reforzado, marco 1.20 × 0.90 m → no dimensiona · veredictos que cambian: A-01 con 'desborde_admitido_con_terraplen_protegido': 105; A-02 con 'desborde_admitido_con_terraplen_protegido': 105; B-01 con 'desborde_admitido_con_terraplen_protegido': 105; C-01 con 'desborde_admitido_con_terraplen_protegido': 106 |
| cabezal | `terreno_delante_del_cabezal` | [A] | horizontal / talud_descendente | 'horizontal', 'talud_descendente' | juego | MUEVE VEREDICTOS | veredictos que cambian: A-01 con 'talud_descendente': 24; A-02 con 'talud_descendente': 24; B-01 con 'talud_descendente': 24; C-01 con 'talud_descendente': 24 |
| cabezal | `acero_refuerzo_cabezal` | [A] | A615_grado_60 / A706_grado_60 | 'A615_grado_60', 'A706_grado_60' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `regla_minimos_constructivos_cabezal` | [A] | mas_exigente_aashto_e060 / solo_aashto | 'mas_exigente_aashto_e060', 'solo_aashto' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `criterio_traccion_cabezal_ciclopeo` | [A] | tracciones_nulas / traccion_admisible_e060 | 'tracciones_nulas', 'traccion_admisible_e060' | juego | NO LO LEE LA CORRIDA | ningún cabezal del juego es de gravedad: con D >= 0.90 m todos son voladizo armado (T-7a) |
| cabezal | `clase_exposicion_fisuracion_cabezal` | [A] | clase_1 / clase_2 | 'clase_2', 'clase_1' | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| cabezal | `junta_arranque_cabezal_ciclopeo` | [A] | junta_de_construccion / vaciado_monolitico | 'junta_de_construccion', 'vaciado_monolitico' | juego | NO LO LEE LA CORRIDA | ningún cabezal del juego es de gravedad |
| conducto | `metodo_longitud_conducto` | [A] | terraplen_simetrico / por_extremo | 'por_extremo', 'terraplen_simetrico' | juego | MUEVE VEREDICTOS | veredictos que cambian: B-01 con 'terraplen_simetrico': 4 |
| conducto | `desnivel_minimo_entrega_m` | [A] | 0.0–0.3 | 0.0, 0.3 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |
| conducto | `desajuste_empalme_canal_m` | [A] | 0.01–0.02 | 0.01, 0.02 | juego | LEÍDO, SIN EFECTO MEDIBLE | — |

## 3. Lo que el resumen dice, por clase

- **MUEVE EL DISEÑO** (11): `seccion_receptor` (juego_sin_TW), `v_max_concreto_eleccion`, `v_max_concreto_eleccion` (juego_tmc_excluida), `regimen_v2b`, `espesor_pared_cajon`, `borde_libre_y_sobre_d_max`, `embocadura_cabezal`, `origen_cota_fondo_entrada`, `remanso_derecho_via`, `pendiente_minima_conducto`, `umbral_no_colapso_evento_extremo`.
- **MUEVE VEREDICTOS** (25): `eta_importancia_operativa_conducto`, `factor_muro_eleccion`, `gamma_EQ`, `fraccion_delta_sobre_phi_trasdos`, `fila_phi_estabilidad_cabezal`, `factores_inclinacion_carga_portante`, `regla_pendiente_relleno_trasdos`, `regimen_resistencia_elementos_cabezal`, `eta_ductilidad_cabezal`, `eta_redundancia_cabezal`, `marco_estabilidad_cabezal`, `regimen_cabezal`, `drenaje_trasdos`, `fc_cabezal_mpa`, `F_pga_lectura_columna_extrema`, `punto_aplicacion_incremento_sismico`, `revestimiento_cuneta`, `phi_relleno_trasdos`, `peso_especifico_relleno_kn_m3`, `talud_terraplen`, `lectura_coeficientes_socavacion_hec14`, `referencia_profundidad_socavacion`, `margen_zapata_bajo_socavacion_m`, `terreno_delante_del_cabezal`, `metodo_longitud_conducto`.
- **MUEVE EL HW** (2): `n_manning_cajon`, `ke_entrada`.
- **LEÍDO, SIN EFECTO MEDIBLE** (28): `HW_D_max`, `v_max_tmc`, `v_max_hdpe`, `fraccion_llena_mayor_parte`, `instalacion_estandar_concreto`, `carga_viva_bajo_relleno_alto`, `duracion_caudal_pico_socavacion_min`, `umbral_area_quebrada_importante_ha`, `esviaje_max_grados`, `borde_libre_canal_m`, `long_max_cuneta`, `lectura_velocidad_limite_cuneta`, `obras_familia_a_extremo_de_cuneta`, `acceso_mantenimiento_v2b`, `pendiente_maxima_conducto`, `condicion_pavimento`, `corrugacion_y_espesor_tmc`, `suelo_agresivo_lrfd_sobre_tmc`, `espesor_proteccion_salida`, `longitud_proteccion_salida`, `tipo_proteccion_entrada`, `regla_espesor_longitud_proteccion_salida`, `regimen_cortante_muro_e060_art_11_10_2`, `acero_refuerzo_cabezal`, `regla_minimos_constructivos_cabezal`, `clase_exposicion_fisuracion_cabezal`, `desnivel_minimo_entrega_m`, `desajuste_empalme_canal_m`.
- **NO LO LEE LA CORRIDA** (16): `borde_libre_bajo_tw_ahogante`, `seccion_receptor`, `hw_entrada_fuera_de_rango`, `inclinacion_muro_beta`, `homogeneidad_serie_fen`, `distribucion_precipitacion_maxima`, `nivel_significancia_ks`, `relacion_intensidad_duracion`, `duracion_minima_lluvia_min`, `tc_fuera_de_la_poblacion_del_metodo`, `coeficiente_uniformidad_temez`, `demanda_sismica_licuefaccion`, `fabricacion_tmc`, `relleno_estructural_hdpe`, `criterio_traccion_cabezal_ciclopeo`, `junta_arranque_cabezal_ciclopeo`.

### 3.1 El cabezal de la regla: E3 estática y E1 sísmica del marco LRFD frente a sus dos [A]

Con la zapata que propone la regla de T-7a (que no se itera, ficha T7B-09) estas cuatro filas no pasan en la corrida del juego (`docs/validacion_integral.md` §2). Lo que cada uno de los dos [A] de los que dependen hace con ellas, medido:

| Criterio | Valor | `E1-LRFD.sis.e` | `E1-LRFD.sis.s` | `E3-LRFD.est.e` | `E3-LRFD.est.s` |
|---|---|---|---|---|---|
| `fila_phi_estabilidad_cabezal` | 'zapatas_seccion_10' | no pasa en ninguno | no pasa en ninguno | no pasa en ninguno | no pasa en ninguno |
| `fila_phi_estabilidad_cabezal` | 'muros_tabla_11_5_7' | no pasa en ninguno | no pasa en ninguno | no pasa en ninguno | pasa en A-01, A-02, C-01 |
| `factores_inclinacion_carga_portante` | 'aplicar' | no pasa en ninguno | no pasa en ninguno | no pasa en ninguno | no pasa en ninguno |
| `factores_inclinacion_carga_portante` | 'omitir' | pasa en A-01, A-02, B-01, C-01 | pasa en A-01, A-02, B-01, C-01 | no pasa en ninguno | no pasa en ninguno |

Ninguno de los dos hace pasar E3 estática a la ENTRADA: ahí el deslizamiento de A-01 lo resuelve la zapata más ancha (variante `zapata_declarada_3m` de `docs/validacion_integral.md` §5), no la lectura de un [A].

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
| sección estrecha | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, CB1.e, CB1.s, CB2.e, CB2.s, CB3.e, CB3.s, CB4.e, CB4.s, CB5.s, CB6.e, CB6.s, CB7.e, CB7.s, E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s, F8.CLASE, G1, G2, G3, V1, V10, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9 | — | NO: el punto tiene diseño en B y no en A: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| sección estrecha | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, CB1.e, CB1.s, CB2.e, CB2.s, CB3.e, CB3.s, CB4.e, CB4.s, CB5.s, CB6.e, CB6.s, CB7.e, CB7.s, E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s, F8.CLASE, G1, G2, G3, V1, V10, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9 | — | NO: el punto tiene diseño en B y no en A: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
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
| 6.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-LRFD.sis.e, E3-LRFD.est.s, F8.AREA, F8.CLASE, F8.COSTURA, F8.FF | — | NO: métodos distintos (control_gobernante: 'salida' frente a 'entrada', perfil_tipo: 'M2' frente a 'S1'): los numeros del diseño salieron de formulas distintas y no se comparan uno a uno |
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
| 6.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, CB1.e, CB1.s, CB2.e, CB2.s, CB3.e, CB3.s, CB4.e, CB4.s, CB5.s, CB6.e, CB6.s, CB7.e, CB7.s, E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s, F8.CLASE, G1, G2, G3, V1, V10, V2, V2b, V3, V4, V4b, V5, V6, V7, V8, V9 | — | NO: el punto tiene diseño en B y no en A: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
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
| 'umbral_duro' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | V2b, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

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

espesor de pared del marco (correcciones de T-11, H3); la ventana está en prosa (0.20 a 0.30 m, ficha T3-08). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.2 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.2 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.2 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.2 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.25 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.25 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.25 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.25 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.3 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.3 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.3 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.3 | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `borde_libre_y_sobre_d_max`

umbral de V1, sólo endurecible (T-11). Se barre además un valor intermedio (0.6): el extremo inferior de la ventana (0.0) no lo cumple ningún conducto con caudal. Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.75 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.75 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.75 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.75 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.6 | A-01 | Concreto reforzado, Ø 1.05 m | 0.920 | entrada | E1-LRFD.sis.e | — | sí |
| 0.6 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.6 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.0 | A-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 0.0 | A-02 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 0.0 | B-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 0.0 | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | V1, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

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
| 'cabezal_recto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A2.alero.e, A2.alero.s, A3.alero.e, A3.alero.s, A4.alero.e, A4.alero.s, A5.alero.e, A5.alero.s, A6.alero.e, A6.alero.s | — | sí |
| 'cabezal_recto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A2.alero.e, A2.alero.s, A3.alero.e, A3.alero.s, A4.alero.e, A4.alero.s, A5.alero.e, A5.alero.s, A6.alero.e, A6.alero.s | — | sí |
| 'cabezal_recto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A1.alero.e, A1.alero.s, A2.alero.e, A2.alero.s, A3.alero.e, A3.alero.s, A4.alero.e, A4.alero.s, A5.alero.e, A5.alero.s, A6.alero.e, A6.alero.s | — | sí |
| 'cabezal_recto' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | DatoInvalidoError: coherencia de la embocadura del marco con el cabezal (T-7a) (embocadura_cajon) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

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
| 0.95 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s, E3-LRFD.est.s | — | sí |
| 0.95 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.95 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.95 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `factor_muro_eleccion`

reducción de k_h por desplazamiento (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'reduccion_por_desplazamiento' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'reduccion_por_desplazamiento' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'reduccion_por_desplazamiento' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'reduccion_por_desplazamiento' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'sin_reduccion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'sin_reduccion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'sin_reduccion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'sin_reduccion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

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
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-LRFD.sis.e | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-LRFD.sis.e | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E3-LRFD.sis.e | — | sí |

### `fraccion_delta_sobre_phi_trasdos`

fricción del trasdós δ/φ (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.67 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.67 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.67 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.67 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.33 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s, E1-LRFD.est.e, E1-LRFD.est.s, E2-ASD.sis.e, E2-LRFD.est.e, E3-ASD.est.e, E3-LRFD.sis.e | — | sí |
| 0.33 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-LRFD.est.e, E1-LRFD.est.s, E2-ASD.sis.e, E2-LRFD.est.e, E3-ASD.est.e, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 0.33 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.s, E1-LRFD.est.e, E1-LRFD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E3-ASD.est.e, E3-ASD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 0.33 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-LRFD.est.e, E1-LRFD.est.s, E3-ASD.est.e, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

### `fila_phi_estabilidad_cabezal`

fila de φ de la estabilidad LRFD (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'zapatas_seccion_10' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'zapatas_seccion_10' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'zapatas_seccion_10' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'zapatas_seccion_10' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'muros_tabla_11_5_7' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E3-LRFD.est.s | — | sí |
| 'muros_tabla_11_5_7' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E3-LRFD.est.s | — | sí |
| 'muros_tabla_11_5_7' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'muros_tabla_11_5_7' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E3-LRFD.est.s | — | sí |

### `factores_inclinacion_carga_portante`

factores de inclinación de la capacidad portante (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'aplicar' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'aplicar' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'aplicar' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'aplicar' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'omitir' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s | — | sí |
| 'omitir' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s | — | sí |
| 'omitir' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s | — | sí |
| 'omitir' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s | — | sí |

### `regla_pendiente_relleno_trasdos`

superficie del relleno para el empuje (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cuna_de_tanteo' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cuna_de_tanteo' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cuna_de_tanteo' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cuna_de_tanteo' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'talud_quebrado_2h' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.alero.s, A2.pantalla.s, A3.alero.s, A3.pantalla.s, A4.alero.s, A4.pantalla.s, A6.alero.s, A6.pantalla.s | — | sí |
| 'talud_quebrado_2h' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A5.alero.s, A5.pantalla.s | — | sí |
| 'talud_quebrado_2h' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s | — | sí |
| 'talud_quebrado_2h' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A2.alero.s, A2.pantalla.s, A5.alero.s, A5.pantalla.s | — | sí |
| 'talud_del_terraplen' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'talud_del_terraplen' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A5.alero.s, A5.pantalla.s, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'talud_del_terraplen' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'talud_del_terraplen' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

### `regimen_resistencia_elementos_cabezal`

empuje con que se arman los elementos (PRECISIONES). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'no_cedente_k0' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'no_cedente_k0' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'no_cedente_k0' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'no_cedente_k0' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'cedente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A5.alero.s, A5.pantalla.s | — | sí |
| 'cedente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.s, A1.pantalla.s, A2.alero.s, A2.pantalla.s, A5.alero.s, A5.pantalla.s | — | sí |
| 'cedente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s | — | sí |
| 'cedente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.s, A1.pantalla.s, A2.alero.s, A2.pantalla.s | — | sí |

### `eta_ductilidad_cabezal`

η_D del cabezal (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.95 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s, E3-LRFD.est.s | — | sí |
| 0.95 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.95 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.95 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.05 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.05 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.05 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-LRFD.est.s | — | sí |
| 1.05 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `eta_redundancia_cabezal`

η_R del cabezal (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 1.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 1.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.95 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s, E3-LRFD.est.s | — | sí |
| 0.95 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.95 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.95 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.05 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.05 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.05 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-LRFD.est.s | — | sí |
| 1.05 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

### `marco_estabilidad_cabezal`

cuál marco de estabilidad rige (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'lrfd_rige_asd_informa' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'lrfd_rige_asd_informa' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'lrfd_rige_asd_informa' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'lrfd_rige_asd_informa' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'asd_rige_lrfd_informa' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s | — | sí |
| 'asd_rige_lrfd_informa' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s | — | sí |
| 'asd_rige_lrfd_informa' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s | — | sí |
| 'asd_rige_lrfd_informa' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s | — | sí |
| 'envolvente_de_los_dos' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s | — | sí |
| 'envolvente_de_los_dos' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s | — | sí |
| 'envolvente_de_los_dos' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.sis.e, E1-ASD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s | — | sí |
| 'envolvente_de_los_dos' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.sis.e, E1-ASD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s | — | sí |

### `regimen_cabezal`

muro que cede o que no cede en la estabilidad (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cedente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cedente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cedente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cedente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'no_cedente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'no_cedente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'no_cedente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'no_cedente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

### `drenaje_trasdos`

trasdós drenado o no (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'drenado' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'drenado' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'drenado' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'drenado' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'sin_drenaje' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.alero.s, A2.pantalla.s, A6.alero.s, A6.pantalla.s, E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'sin_drenaje' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'sin_drenaje' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'sin_drenaje' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

### `fc_cabezal_mpa`

resistencia del concreto del cabezal (T-11). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 21.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 21.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 21.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 21.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 17.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A3.alero.s, A3.pantalla.s, A4.alero.s, A4.pantalla.s, A6.alero.s, A6.pantalla.s | — | sí |
| 17.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 17.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 17.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A5.alero.s, A5.pantalla.s | — | sí |
| 35.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s | — | sí |
| 35.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.s, A1.pantalla.s, A5.alero.s, A5.pantalla.s | — | sí |
| 35.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s | — | sí |
| 35.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.s, A1.pantalla.s | — | sí |

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

### `F_pga_lectura_columna_extrema`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'limite_inclusive' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'limite_inclusive' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'limite_inclusive' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'limite_inclusive' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'limite_estricto' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'limite_estricto' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'limite_estricto' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'limite_estricto' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.e, A1.alero.s, A1.pantalla.e, A1.pantalla.s, A1.punta.e, A1.punta.s, A1.talon.e, A1.talon.s, A2.alero.e, A2.alero.s, A2.pantalla.e, A2.pantalla.s, A2.punta.e, A2.punta.s, A2.talon.e, A2.talon.s, A3.alero.e, A3.alero.s, A3.pantalla.e, A3.pantalla.s, A3.punta.e, A3.punta.s, A3.talon.e, A3.talon.s, A4.alero.e, A4.alero.s, A4.pantalla.e, A4.pantalla.s, A4.punta.e, A4.punta.s, A4.talon.e, A4.talon.s, A5.alero.e, A5.alero.s, A5.pantalla.e, A5.pantalla.s, A5.punta.e, A5.punta.s, A5.talon.e, A5.talon.s, A6.alero.e, A6.alero.s, A6.pantalla.e, A6.pantalla.s, A6.punta.e, A6.punta.s, A6.talon.e, A6.talon.s, A7.concreto.e, A7.concreto.s, A8.zapata.e, A8.zapata.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

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

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 0.6 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.6 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.6 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.333 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-LRFD.sis.e | — | sí |
| 0.333 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-LRFD.sis.e | — | sí |
| 0.333 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.333 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-LRFD.sis.e | — | sí |

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
| 'cota_fondo_entrada' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'cota_fondo_entrada' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'cota_fondo_entrada' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'cota_fondo_entrada' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | DatoFaltanteError: longitud del conducto (7.B) (cota_fondo_entrada) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `remanso_derecho_via`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'cota_de_afectacion' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'cota_de_afectacion' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'cota_de_afectacion' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'cota_de_afectacion' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'embalse_a_nivel' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V1, V5, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'embalse_a_nivel' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V5, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'embalse_a_nivel' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V5, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'embalse_a_nivel' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'perfil_de_remanso_paso_a_paso' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V1 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'perfil_de_remanso_paso_a_paso' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | MetodoNoEvaluableError: material y diametro (bucle de MD) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'perfil_de_remanso_paso_a_paso' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | MetodoNoEvaluableError: material y diametro (bucle de MD) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
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
| 0.005 | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | V10, V7 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

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
| 30.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.alero.s, A2.pantalla.s, A3.alero.s, A3.pantalla.s, A4.alero.s, A4.pantalla.s, A6.alero.s, A6.pantalla.s, E1-ASD.est.s, E1-LRFD.est.e, E1-LRFD.est.s, E3-ASD.est.e, E3-LRFD.sis.e | — | sí |
| 30.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.s, E1-LRFD.est.e, E1-LRFD.est.s, E3-ASD.est.e, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 30.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.s, E1-LRFD.est.e, E1-LRFD.est.s, E2-ASD.sis.e, E3-ASD.est.e, E3-ASD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 30.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A5.alero.s, A5.pantalla.s, E1-LRFD.est.e, E1-LRFD.est.s, E3-ASD.est.e, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 38.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-LRFD.sis.e, E3-LRFD.est.s | — | sí |
| 38.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A5.alero.s, A5.pantalla.s, E1-LRFD.sis.e, E3-LRFD.est.s | — | sí |
| 38.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s, E1-LRFD.sis.e | — | sí |
| 38.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.s, A1.pantalla.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E3-LRFD.est.s | — | sí |

### `demanda_sismica_licuefaccion`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **NO LO LEE LA CORRIDA**.

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

### `peso_especifico_relleno_kn_m3`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 17.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 17.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 17.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 17.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 20.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.alero.s, A2.pantalla.s, A2.punta.s, A3.alero.s, A3.pantalla.s, A4.alero.s, A4.pantalla.s, A6.alero.s, A6.pantalla.s, E1-LRFD.est.s, E3-ASD.est.e | — | sí |
| 20.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-LRFD.est.e, E1-LRFD.est.s, E3-ASD.est.e, E3-LRFD.sis.e | — | sí |
| 20.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-LRFD.est.e, E1-LRFD.est.s, E3-ASD.est.e, E3-ASD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 20.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A5.alero.s, A5.pantalla.s | — | sí |

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

### `talud_terraplen`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 2.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 2.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 2.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 2.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 1.5 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 1.5 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 1.5 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-LRFD.est.s | — | sí |
| 1.5 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

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

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'envolvente_de_filas_vecinas' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'envolvente_de_filas_vecinas' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'envolvente_de_filas_vecinas' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'envolvente_de_filas_vecinas' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'interpolacion_lineal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s | — | sí |
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

### `referencia_profundidad_socavacion`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'fondo_del_cauce_receptor' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'fondo_del_cauce_receptor' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'fondo_del_cauce_receptor' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'fondo_del_cauce_receptor' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'solera_de_salida' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A1.alero.s, A1.pantalla.s, A2.talon.s, A5.alero.s, A5.pantalla.s | — | sí |
| 'solera_de_salida' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.s, A1.pantalla.s, A5.alero.s, A5.pantalla.s | — | sí |
| 'solera_de_salida' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s | — | sí |
| 'solera_de_salida' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.s, A1.pantalla.s | — | sí |

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
| 0.6096 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 0.6096 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 0.6096 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 0.6096 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 0.0 | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | A2.talon.s, A5.alero.s, A5.pantalla.s, E1-ASD.est.s, E1-LRFD.est.s | — | sí |
| 0.0 | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | A1.alero.s, A1.pantalla.s, A5.alero.s, A5.pantalla.s, E1-ASD.est.s, E1-LRFD.est.s | — | sí |
| 0.0 | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | A2.alero.s, A2.pantalla.s, E1-ASD.est.s, E1-LRFD.est.s | — | sí |
| 0.0 | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | A1.alero.s, A1.pantalla.s, E1-LRFD.est.s | — | sí |

### `umbral_no_colapso_evento_extremo`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE EL DISEÑO**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'sin_desborde_de_la_plataforma' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'sin_desborde_de_la_plataforma' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'sin_desborde_de_la_plataforma' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'sin_desborde_de_la_plataforma' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'desborde_admitido_con_terraplen_protegido' | A-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | V1 | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'desborde_admitido_con_terraplen_protegido' | A-02 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | MetodoNoEvaluableError: material y diametro (bucle de MD) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'desborde_admitido_con_terraplen_protegido' | B-01 | no dimensiona | — | — | (el punto no dimensiona: 105 cambian o desaparecen) | MetodoNoEvaluableError: material y diametro (bucle de MD) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |
| 'desborde_admitido_con_terraplen_protegido' | C-01 | no dimensiona | — | — | (el punto no dimensiona: 106 cambian o desaparecen) | MetodoNoEvaluableError: material y diametro (bucle de MD) | NO: el punto tiene diseño en A y no en B: no hay numeros que comparar (ver `dimensionado` y `bloqueos`) |

### `terreno_delante_del_cabezal`

derivado del censo (valor efectivo y ventana legible por máquina; correcciones de T-11, H3). Base: el juego completo. Efecto: **MUEVE VEREDICTOS**.

| Valor | Punto | Material y sección | HW (m) | Control | Verificaciones que cambian frente al primer valor | Incumplidas o bloqueo si no dimensiona | Comparable |
|---|---|---|---|---|---|---|---|
| 'horizontal' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'horizontal' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'horizontal' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | ninguna | — | sí |
| 'horizontal' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |
| 'talud_descendente' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'talud_descendente' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'talud_descendente' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'talud_descendente' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | E1-ASD.est.e, E1-ASD.est.s, E1-ASD.sis.e, E1-ASD.sis.s, E1-LRFD.est.e, E1-LRFD.est.s, E1-LRFD.sis.e, E1-LRFD.sis.s, E2-ASD.est.e, E2-ASD.est.s, E2-ASD.sis.e, E2-ASD.sis.s, E2-LRFD.est.e, E2-LRFD.est.s, E2-LRFD.sis.e, E2-LRFD.sis.s, E3-ASD.est.e, E3-ASD.est.s, E3-ASD.sis.e, E3-ASD.sis.s, E3-LRFD.est.e, E3-LRFD.est.s, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |

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
| 'terraplen_simetrico' | A-01 | Concreto reforzado, Ø 0.90 m | 1.042 | entrada | ninguna | — | sí |
| 'terraplen_simetrico' | A-02 | Concreto reforzado, Ø 0.90 m | 0.572 | entrada | ninguna | — | sí |
| 'terraplen_simetrico' | B-01 | Concreto reforzado, Ø 0.90 m | 0.232 | entrada | E1-LRFD.est.s, E3-ASD.est.e, E3-LRFD.sis.e, E3-LRFD.sis.s | — | sí |
| 'terraplen_simetrico' | C-01 | Concreto reforzado, marco 1.20 × 0.90 m | 0.623 | salida | ninguna | — | sí |

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

## 5. Los criterios que no se barren, por nombre

82 barridos sobre 80 criterios; estos 61 no se barren, y la razón:

| Criterio | Etiqueta | Por qué no se barre |
|---|---|---|
| `PERFIL_SUELO_PRESUNTO` | [S] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `clase_sitio` | [S] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `F_pga` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `k_v` | [A] | forma compuesta (categoria o numero) con la ventana en prosa: ventana en prosa (un piso o una regla, sin dos extremos): no es legible por máquina y no se barrió (NO SE MIDIÓ) |
| `pendiente_relleno_trasdos_i` | [A] | [A] OPCIONAL sin valor: sin declararlo rige la regla escrita en su ficha; el juego no lo declara |
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
| `TR_evento_extremo` | [A] | el juego lo declara (500 años) pero la ficha no tiene ventana: el TR del evento extremo lo fija el Propietario con el estudio hidrológico |
| `c_phi_fundacion` | [A] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `capacidad_portante_adm` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `Mw_licuefaccion` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
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
| `N_cq_N_gammaq_meyerhof` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; condicional que el juego no dispara (terreno en talud delante del cabezal) |
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
| `peso_especifico_saturado_relleno_kn_m3` | [A] | dato de ensayo o de sitio, sin ventana: se declara con su trazabilidad, no se elige |
| `catalogo_barras_refuerzo_cabezal` | [A] | su valor es una fila o un conjunto de filas de una tabla (forma estructurada) y la ventana, si la hay, va por fila o en prosa: no es legible por máquina |
| `concreto_ciclopeo_cabezal` | [A] | ventana POR CAMPO de un dict: barrerlo exige elegir una esquina por campo, y no se hizo (NO SE MIDIÓ); ningún cabezal del juego es de gravedad |
| `espesor_min_zapata_concreto_simple_m` | [N->] | valor de una fuente ([N→] o [C]) sin ventana: no hay rango que barrer |
| `edicion_que_rige_el_expediente` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |
| `edicion_legal_que_rige_el_expediente` | [A] | sin valor de archivo y el juego no lo declara: no hay valor efectivo desde el que barrer; sin consumidor (`tests/test_nivel_medido.py::SIN_CONSUMIDOR_Y_SIN_MEDIDA`) |

