import sys, json, math, pathlib, tempfile, pickle
sys.path.insert(0, "/home/user/wt/T-7c")
import conftest
from src import criterios_adoptados as ca, servicio
from src.modulos import M9_cabezal as M9
from src.modelos import CondicionAnalisis
import tests.test_t7c_cabezal_armado as T
T._sin_datos_de_exposicion()
SPD="/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c-aud"
tmp = pathlib.Path(tempfile.mkdtemp(dir=SPD))
ENT = []
orig = servicio.solicitaciones_de_resistencia
def wrap(e):
    ENT.append(e); return orig(e)
servicio.solicitaciones_de_resistencia = wrap
informe, a01 = T._correr_de_prueba(tmp)
est, sis = CondicionAnalisis.ESTATICO, CondicionAnalisis.SISMICO
for e in ENT:
    print("=====", e.extremo, {k: getattr(e, k) for k in ("cota_relleno","cota_borde_plataforma","talud","esviaje_grados","cota_freatico","cota_pie","suelo")})
    for cond in (est, sis):
        try:
            cargas, datos = M9.cargas_del_cabezal(e, cond)
        except Exception as ex:
            print("  ", cond.name, "NO EVALUABLE", type(ex).__name__, str(ex)[:300]); continue
        print("  --", cond.name)
        for c in cargas:
            print("     %-14s %-3s V=%9.4f H=%9.4f x=%s z=%s sobre=%s" % (c.codigo, c.tipo, c.V, c.H, None if c.x is None else round(c.x,4), None if c.z is None else round(c.z,4), c.sobre))
        print("     datos:", {k: (round(v,5) if isinstance(v,float) else v) for k,v in datos.items() if k not in ("relleno","angulos")})
        print("     relleno:", {k: (round(v,5) if isinstance(v,float) else v) for k,v in datos["relleno"].items()})
        print("     angulos:", datos["angulos"])
        combos = M9.combinaciones_de_estabilidad(cargas, datos, cond, e.geometria.B)
        for c in combos:
            if c.marco == "LRFD":
                print("     COMBO", c.nombre, "N=%.3f H=%.3f e=%.4f B=%.3f" % (c.N, c.H, c.excentricidad, c.B), dict(c.factores))
    cargas, datos = M9.cargas_del_cabezal(e, est)
    c0 = M9.cargas_en_reposo(cargas, datos)
    for c in M9._combinaciones_en_reposo(c0, e.geometria.B):
        print("     COMBO0", c.nombre, "N=%.3f H=%.3f e=%.4f B=%.3f" % (c.N, c.H, c.excentricidad, c.B), dict(c.factores), M9.presion_de_contacto_lineal(c))
print("cadena", M9.cadena_sismica())
pickle.dump(ENT, open(SPD+"/ent.pkl","wb"))
