# Datos Referenciales - Vía de Evitamiento La Unión, Bajo Piura
**SOLO PARA PRUEBA INTEGRAL. NINGUNO DE ESTOS VALORES ESTA APLICADO EN EL
CODIGO, y ninguno puede aplicarse a una memoria de calculo: no estan
verificados contra norma ni contra ensayo.**

Son valores de destrabe para una corrida exploratoria: se cargan en caliente
(`establecer_valor_dinamico`) o con `provisional=True`, se mira que puntos
completan diseno, y se revierten. Los criterios de `criterios_adoptados.py`
siguen en `valor=None` a proposito, y los tests de invariante lo exigen.

(La rama `prueba-integral` en que se hizo esta corrida fue renombrada a
`main`; el documento se conserva por sus hallazgos, no como receta a aplicar.)

Versión corregida: se retiraron 6 entradas que ya están cerradas o retiradas en el código real
(factores_carga_aashto, recubrimiento_aashto_mm, peso_especifico_concreto_kn_m3,
procedimiento_flexion_corte_aashto_sec5, FS_flotacion, N_cq_N_gammaq_meyerhof). Aplicar estos
valores encima pisaría trabajo ya verificado con cita.

## 1. Geometría y Geotecnia Básica
*   **v_max_concreto_eleccion**: `3.0` (m/s)
*   **talud_terraplen**: `1.5` (H:V)
*   **pendiente_relleno_trasdos_i**: `0.0` (°)
*   **inclinacion_muro_beta**: `0.0` (°)
*   **friccion_muro_suelo_delta**: `20.0` (°)
*   **punto_aplicacion_incremento_sismico**: `0.6` (H)
*   **angulo_aletas**: `45.0` (°)
*   **predimensionamiento_cabezal**: `{'espesor_pantalla': 0.30, 'espesor_zapata': 0.40, 'talon': 0.50, 'puntera': 0.50}` (m)
*   **metodo_estabilidad_global**: `"Bishop_Simplificado"`

## 2. Hidrología e Hidráulica
*   **longitud_proteccion_salida**: `3.0` (m)
*   **TR_evento_extremo**: `100` (años)
*   **umbral_area_quebrada_importante_ha**: `100.0` (ha)
*   **v_max_hdpe**: `6.0` (m/s)
*   **v_max_tmc**: `4.5` (m/s)

## 3. Normas de Producto
*   **clases_producto_por_relleno**: `"Clase_III"`

## 4. Datos externos (Tablero 3 — no cierran vía código, son de sitio)
*   **c_phi_fundacion**: `{'phi': 28.0, 'c': 0.0}` (SUCS SM)
*   **capacidad_portante_adm**: `80.0` (kPa)
*   **phi_relleno_trasdos**: `30.0` (°)
*   **peso_especifico_relleno_kn_m3**: `18.0`
*   **TW_receptor**: escenario "salida libre" — TW = cota_fondo_receptor del punto
*   **remanso_derecho_via**: asumir cumple (dentro de derecho de vía) para B-01
*   **Q_receptor / homogeneidad FEN**: no aplica a A-01/A-02/B-01; C-01 sigue bloqueada (correcto)
