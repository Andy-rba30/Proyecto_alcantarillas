import sys, json, math, pathlib, tempfile
sys.path.insert(0, "/home/user/wt/T-7c")
import conftest
from src import criterios_adoptados as ca, servicio
from src.modulos import M9_cabezal as M9
from src.modelos import CondicionAnalisis
import tests.test_t7c_cabezal_armado as T
T._sin_datos_de_exposicion()
SPD="/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c-aud"
tmp = pathlib.Path(tempfile.mkdtemp(dir=SPD))
print("archivo factor_muro_eleccion:", ca.CRITERIOS["factor_muro_eleccion"].valor)
decl = dict(T.DECLARACIONES_DE_PRUEBA); decl.pop("factor_muro_eleccion")
T.DECLARACIONES_DE_PRUEBA.clear(); T.DECLARACIONES_DE_PRUEBA.update(decl)
informe, a01 = T._correr_de_prueba(tmp)
print("cadena", M9.cadena_sismica().k_h, M9.cadena_sismica().k_h0)
print("bloqueos", [(b.etapa, b.tipo.name, b.mensaje[:200]) for b in a01.bloqueos])
for a in a01.cabezal.armado:
    print("=== ARMADO", a.extremo, "sismico", a.sismico)
    for s in a.secciones:
        print(" --", s.clave, "rige", s.rige_flexion.combinacion, round(s.rige_flexion.M_u,2), "phi", s.rige_flexion.phi_flexion, "| As_res", round(s.As_resistencia), "adopt", round(s.As_adoptado), s.barra.texto if s.barra else None, "| V", s.rige_cortante.combinacion, round(s.rige_cortante.V_u,2), "V_r", round(s.V_r,1))
        for x in s.solicitaciones:
            if x.condicion is CondicionAnalisis.SISMICO:
                print("       ", x.combinacion[:40], "M", round(x.M_u,2), "V", round(x.V_u,2))
        for v in s.verificaciones:
            if not v.cumple or v.paso.veredicto.tipo.name != "CUMPLE":
                print("     !!", v.codigo, v.paso.veredicto.tipo.name, round(v.valor_obtenido,2), round(v.valor_admisible,2))
    for av in a.avisos:
        if "SOLO de Resistencia" in av or "NO cede" in av: print("   AVISO:", av[:500])
