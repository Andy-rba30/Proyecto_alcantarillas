"""Reproduccion minima del defecto candidato D1 (correr desde /home/user/val_web:
   python /tmp/validacion_web/defectos/D1_progresion_redondeo/repro_minima.py).
La progresion de diametros declarada pasa la puerta del criterio, pero
M2.siguiente_diametro redondea el siguiente escalon a 2 decimales
(src/modulos/M2_material.py:973) y despues rechaza su propio resultado."""
import sys; sys.path.insert(0, '.')
from src import criterios_adoptados as ca
from src.modulos import M2_material as M2
from src.modelos import TipoMaterial
ca.establecer_valor_dinamico('diametros_normalizados', {"inicio": 0.9144, "paso": 0.1524})
d1 = M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO)
d2 = M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, d1)
print('D1 =', d1, ' D2 =', d2, ' (esperado 1.0668)')
try:
    print('D3 =', M2.siguiente_diametro(TipoMaterial.CONCRETO_REFORZADO, d2))
except Exception as e:
    print('D3 ->', type(e).__name__, e)
