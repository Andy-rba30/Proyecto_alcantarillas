import sys, json, math, pathlib, tempfile
sys.path.insert(0, "/home/user/wt/T-7c")
import conftest  # declara lo de la corrida de pruebas
from src import criterios_adoptados as ca, servicio
from src.modulos import M9_cabezal as M9
from src.modelos import CondicionAnalisis
import tests.test_t7c_cabezal_armado as T
T._sin_datos_de_exposicion()
tmp = pathlib.Path(tempfile.mkdtemp(dir="/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c-aud"))
informe, a01 = T._correr_de_prueba(tmp)
print("dimensionado", a01.dimensionado, a01.resultado.seccion.etiqueta())
cab = a01.cabezal
for g in cab.geometrias:
    print("GEOM", g)
print("bloqueos", [(b.etapa, b.tipo) for b in a01.bloqueos])
for a in cab.armado:
    print("=== ARMADO", a.extremo, a.tipo, a.regimen, "K0", a.K0, "K_A", a.K_A, "fc", a.fc_mpa, "fy", a.fy_mpa)
    for s in a.secciones:
        print(" --", s.clave, "h", s.espesor, "rec", s.recubrimiento_mm, s.origen_recubrimiento, "d", round(s.d,4))
        for x in s.solicitaciones:
            print("     ", x.combinacion, x.condicion.name, "M_u", round(x.M_u,3), "V_u", round(x.V_u,3), "phi", x.phi_flexion, "ced", None if x.M_u_cedente is None else round(x.M_u_cedente,3), round(x.V_u_cedente,3), "rep", None if x.M_u_reposo is None else round(x.M_u_reposo,3), None if x.V_u_reposo is None else round(x.V_u_reposo,3), "|", x.nota)
        print("     As_res", round(s.As_resistencia,1), "As_minf", round(s.As_minimo_flexion,1), "As_minc", round(s.As_minimo_constructivo,1), s.origen_minimo, "adopt", round(s.As_adoptado,1), s.gobierna)
        print("     barra", s.barra.texto if s.barra else None, "s_max", s.s_max, s.origen_s_max, "M_r", round(s.M_r,2), "eps", s.epsilon_t, "d_v", round(s.d_v,4), "V_c", round(s.V_c,2), "V_r", round(s.V_r,2))
        print("     E060", s.M_u_e060, s.V_u_e060, s.As_e060, s.V_r_e060)
        for v in s.verificaciones:
            print("       ", v.codigo, v.cumple, v.paso.veredicto.tipo.name, round(v.valor_obtenido,3), round(v.valor_admisible,3))
    for f in a.tabla:
        print("   T:", f.elemento, "|", f.posicion, "| req", round(f.As_requerido), "min", round(f.As_minimo), "adopt", round(f.As_adoptado), "|", f.barra.texto if f.barra else None, "| smax", f.s_max, "|", f.gobierna)
    for av in a.avisos:
        print("   AVISO:", av[:400])
import pickle
print("\n\n######## ENTORNOS Y CARGAS")
import dataclasses
ents = []
for g in cab.geometrias:
    pass
# reconstruir entornos como lo hace el servicio
import inspect
src = inspect.getsource(servicio._fase_9_armado) if hasattr(servicio, "_fase_9_armado") else ""
print(src[:6000])
