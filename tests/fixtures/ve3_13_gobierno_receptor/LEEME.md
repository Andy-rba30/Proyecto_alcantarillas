# DATOS DE PRUEBA — no son del proyecto

El escenario E07 de los ensayos de diseño del conducto (revisor independiente,
`proceso/planes_mejora/ve3_estado/ENSAYOS_DISENO_CONDUCTO.md`): Familia A,
Q = 0.6 m³/s, S = 0.004, TW = 1.0 m sobre el fondo de la salida. Con
`borde_libre_bajo_tw_ahogante` = `no_cumple` (valor de archivo) el diámetro es
Ø 1.35 m; con `aviso`, Ø 0.90 m. Lo usa `tests/test_ve3_13_gobierno_receptor.py`
(decisión 8 del dueño). `externos_salida_libre.json` es la misma obra con
TW = 0, donde el receptor no gobierna nada.
