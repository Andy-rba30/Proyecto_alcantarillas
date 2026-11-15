import sys, importlib
from decimal import Decimal
from src import criterios_adoptados as ca
from src.modulos import M2_material as M2
from src.modelos import ErrorProyecto
def serie(ini, paso, mat="concreto_reforzado", maxn=40):
    ca.establecer_valor_dinamico("diametros_normalizados", {"inicio": ini, "paso": paso})
    out=[]; D=None
    for _ in range(maxn):
        try:
            D = M2.siguiente_diametro(mat, D)
        except Exception as e:
            out.append(f"EXC {type(e).__name__}: {e}"[:150]); break
        if D is None: break
        out.append(D)
    return out
import inspect
print(inspect.signature(ca.establecer_valor_dinamico))
casos=[(0.90,0.15),(0.9144,0.1524),(0.90,0.075),(0.90,0.125),(0.914,0.152),(0.9,0.1),(0.9,0.3048),(0.91440,0.15240),(0.9,0.0254),(0.9,0.123456),(0.900001,0.150001),(1,0.15),(0.9,1/3),(0.9, 0.05),(0.9,1e-5),(36*0.0254,6*0.0254)]
for ini,paso in casos:
    for mat in ("concreto_reforzado","tmc","hdpe"):
        try:
            s=serie(ini,paso,mat, maxn=30)
        except Exception as e:
            print(ini,paso,mat,"FALLO",type(e).__name__,e); continue
        nums=[x for x in s if not isinstance(x,str)]
        exact=[float(Decimal(repr(float(ini)))+k*Decimal(repr(float(paso)))) for k in range(len(nums))]
        ok = nums==exact
        ruido=[x for x in nums if len(repr(x))>10]
        print(ini,paso,mat,len(nums),"ok" if ok else "DIFIERE", s[:4], s[-2:], "RUIDO" if ruido else "", ruido[:3])
