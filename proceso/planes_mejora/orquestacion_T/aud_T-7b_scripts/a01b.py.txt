import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud")
sys.path.insert(0, "/home/user/wt/T-7b")
from a01 import correr
from src.modulos import M9_cabezal as M9
from src.modelos import CondicionAnalisis as CA
inf, a = correr()
ents = M9.datos_del_cabezal_del_punto(punto=a.punto, cabezal=a.cabezal, geometria=a.geometria, socavacion=getattr(a,'socavacion',None))
for en in ents:
    print(en.extremo, "cota_relleno", en.cota_relleno, "borde", en.cota_borde_plataforma, en.origen_cota_borde, "talud", en.talud, "NF", en.NF_profundidad_m, "pie", en.cota_pie, "hoya", en.cota_fondo_hoya, "esv", en.esviaje_grados)
    r = M9.geometria_del_relleno(en)
    print({k: v for k, v in r.items()})
    cargas, d = M9.cargas_del_cabezal(en, CA.SISMICO)
    print({k: v for k, v in d.items() if k not in ("relleno",)})
print(a.punto)
print(a.geometria)
print([x for x in dir(a) if not x.startswith('_')])
