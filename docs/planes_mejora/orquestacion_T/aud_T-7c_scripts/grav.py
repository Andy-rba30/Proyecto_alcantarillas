import sys, pathlib, tempfile
sys.path.insert(0, "/home/user/wt/T-7c")
import conftest
from src import criterios_adoptados as ca, servicio
from src.modulos import M9_cabezal as M9
import tests.test_t7c_cabezal_armado as T
T._sin_datos_de_exposicion()
SPD="/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c-aud"
for crit in ("tracciones_nulas", "traccion_admisible_e060"):
    tmp = pathlib.Path(tempfile.mkdtemp(dir=SPD))
    informe, a01 = T._correr_de_prueba(tmp, extra_a01={"cabezal_declarado": {"tipo": "gravedad_ciclopeo"}}, declaraciones={"criterio_traccion_cabezal_ciclopeo": crit})
    print("#####", crit, "dimensionado", a01.dimensionado)
    for g in a01.cabezal.geometrias:
        print("  geom", g.extremo, "H", round(g.H,3), "B", round(g.B,3), "e_c", g.espesor_corona, "e_b", round(g.espesor_base_muro,3), "e_z", g.espesor_zapata, "talon", round(g.ancho_talon,3), "punta", round(g.ancho_punta,3))
    for a in a01.cabezal.armado:
        for v in a.verificaciones:
            print("   ", v.codigo, "cumple", v.cumple, v.paso.veredicto.tipo.name, "obt", round(v.valor_obtenido,3), "adm", round(v.valor_admisible,3))
    inc = [v.codigo for v in a01.incumplidas()]
    print("  incumplidas:", inc)
    est = [(e.extremo, e.condicion.name, [(v.codigo, v.paso.veredicto.tipo.name) for v in e.verificaciones if v.codigo.startswith("E")][:6]) for e in a01.cabezal.estabilidad]
    for e in est: print("  EST", e)
