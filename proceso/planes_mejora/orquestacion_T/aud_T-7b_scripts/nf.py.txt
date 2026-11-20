import sys
from dataclasses import replace
sys.path.insert(0, "/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud")
sys.path.insert(0, "/home/user/wt/T-7b")
from a01 import correr
from src import criterios_adoptados as ca
from src.modulos import M9_cabezal as M9
from src.modelos import CondicionAnalisis as CA, ErrorProyecto
inf, a = correr()
ents = M9.datos_del_cabezal_del_punto(punto=a.punto, cabezal=a.cabezal, geometria=a.geometria, socavacion=a.socavacion)
sal = ents[1]
print("salida: cota_pie", sal.cota_pie, "cota_terreno", a.punto.cota_terreno, "desplante", sal.geometria.cota_desplante, "NF col", a.punto.NF_profundidad_m)
print("cota NF segun M8 (cota_terreno - NF):", a.punto.cota_terreno - a.punto.NF_profundidad_m, "| segun M9 (cota_pie - NF):", sal.cota_pie - sal.NF_profundidad_m)
nf_coherente = a.punto.NF_profundidad_m - (a.punto.cota_terreno - sal.cota_pie)
sal2 = replace(sal, NF_profundidad_m=nf_coherente)
for cond in (CA.ESTATICO, CA.SISMICO):
    try:
        e = M9.ensamble_estabilidad(sal2, cond)
        print(cond.value, [(v.codigo, v.estado.name, round(v.valor_obtenido, 2), round(v.valor_admisible, 2)) for v in e.verificaciones])
    except ErrorProyecto as ex:
        print(cond.value, "->", type(ex).__name__, str(ex)[:260])
ca.establecer_valor_dinamico("peso_especifico_saturado_relleno_kn_m3", 20.0)
for cond in (CA.ESTATICO, CA.SISMICO):
    try:
        e = M9.ensamble_estabilidad(sal2, cond)
        print("gsat=20", cond.value, [(v.codigo, v.estado.name, round(v.valor_obtenido, 2), round(v.valor_admisible, 2)) for v in e.verificaciones])
    except ErrorProyecto as ex:
        print("gsat=20", cond.value, "->", type(ex).__name__, str(ex)[:260])
