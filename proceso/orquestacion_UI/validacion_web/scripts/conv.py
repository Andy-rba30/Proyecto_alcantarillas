# Conversiones exactas usadas en la validacion (anotadas en INFORME.md)
FT = 0.3048                 # m por pie (exacto)
CFS = 0.028316846592        # m3/s por ft3/s (exacto: 0.3048^3)
IN = 0.0254                 # m por pulgada (exacto)
def ft(x): return x * FT
def cfs(x): return x * CFS
def a_ft(m): return m / FT
def a_cfs(q): return q / CFS
