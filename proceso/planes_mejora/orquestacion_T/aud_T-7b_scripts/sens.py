import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud")
sys.path.insert(0, "/home/user/wt/T-7b")
from a01 import correr
from src import criterios_adoptados as ca
casos = {
 "base (prueba del informe)": {},
 "fila phi = muros_tabla_11_5_7": {"fila_phi_estabilidad_cabezal": "muros_tabla_11_5_7"},
 "inclinacion = omitir": {"factores_inclinacion_carga_portante": "omitir"},
 "muros + omitir": {"fila_phi_estabilidad_cabezal": "muros_tabla_11_5_7", "factores_inclinacion_carga_portante": "omitir"},
 "talud_del_terraplen": {"regla_pendiente_relleno_trasdos": "talud_del_terraplen"},
 "kh sin reduccion (archivo)": {"factor_muro_eleccion": "sin_reduccion"},
 "sin_drenaje (archivo)": {"drenaje_trasdos": "sin_drenaje"},
 "sin_drenaje + gamma_sat 20": {"drenaje_trasdos": "sin_drenaje", "peso_especifico_saturado_relleno_kn_m3": 20.0},
}
for nombre, decl in casos.items():
    try:
        inf, a = correr(decl=decl)
    except Exception as e:
        print(nombre, "EXC", type(e).__name__, str(e)[:300]); continue
    print("==", nombre, "| dim", a.dimensionado)
    if a.cabezal is not None:
        for e in a.cabezal.estabilidad:
            print("   ", e.extremo, e.condicion.value, " ".join(f"{v.codigo.split('.')[0]}:{v.estado.name[:3]}({v.valor_obtenido:.1f}/{v.valor_admisible:.1f})" for v in e.verificaciones))
    for b in a.bloqueos:
        print("   BLOQ", b.etapa, "|", b.tipo.name, "|", b.mensaje[:200])
    # reponer
    for k in decl:
        pass
