# -*- coding: utf-8 -*-
"""
DESPUES de congelar el calculo a mano (SHA1SUMS_congelado.txt): corre las
funciones publicas de MH_hidrologia sobre las entradas preparadas y compara
con salida_esperada.json. Se ejecuta con el directorio del proyecto como cwd;
no escribe nada en el repositorio.
"""
import json, math, os, sys, traceback
sys.path.insert(0, "/home/user/Proyecto_alcantarillas")
from src import criterios_adoptados as ca
from src.modulos import MH_hidrologia as MH
from src.modelos import ErrorProyecto
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = []
def p(*a): OUT.append(" ".join(str(x) for x in a)); print(OUT[-1])
def decl(**kw):
    ca.limpiar_valores_dinamicos()
    for k, v in kw.items(): ca.establecer_valor_dinamico(k, v)
def rel(a, b): return abs(a - b)/abs(b) if b else abs(a)
PEOR = [0.0]
def cmp_(nombre, prog, esp, tol=1e-9):
    r = rel(prog, esp); PEOR[0] = max(PEOR[0], r)
    if r > tol: p(f"    DIFIERE {nombre}: programa {prog!r} vs a mano {esp!r} (rel {r:.2e})")
    return r <= tol
def intenta(f):
    try: return f(), None
    except ErrorProyecto as e: return None, e
    except Exception as e: return None, e

def caso_estacion(caso, archivo, estaciones_TRs, clave_esp=None, **criterios):
    esp_caso = json.load(open(f"{RAIZ}/{caso}/salida_esperada.json", encoding="utf-8"))
    series = MH.cargar_estacion(f"{RAIZ}/{caso}/{archivo}")
    for est, (clave, TRs) in estaciones_TRs.items():
        esp = esp_caso
        for k in clave: esp = esp[k]
        for dist in ("mejor_ajuste_ks", "normal", "lognormal_2p", "gumbel"):
            decl(homogeneidad_serie_fen="serie_completa", distribucion_precipitacion_maxima=dist, **criterios)
            for T in TRs:
                res, err = intenta(lambda: MH.precipitacion_de_diseno(series[est], T))
                d_esp = esp["mejor_ajuste_ks"] if dist == "mejor_ajuste_ks" else dist
                e = esp[d_esp]
                if err is not None:
                    pasa_esp = e["D"] < esp["d_critico_0.05"]
                    p(f"  {caso}/{est} {dist} TR {T}: {type(err).__name__} | a mano: D = {e['D']:.4f} vs d = {esp['d_critico_0.05']:.4f} -> {'INESPERADO' if pasa_esp else 'esperado (no pasa K-S)'}")
                    if pasa_esp: p("     ", str(err)[:300])
                    continue
                adoptado, evaluados, trat, pasos, avisos = res
                ok = adoptado.distribucion == d_esp
                ok &= cmp_("P", adoptado.P_TR_mm, e["P_TR_mm"][str(T)]); ok &= cmp_("D", adoptado.D, e["D"])
                ok &= cmp_("d", adoptado.d_critico, esp["d_critico_0.05"])
                p(f"  {caso}/{est} {dist} TR {T}: {adoptado.distribucion} P = {adoptado.P_TR_mm:.4f} D = {adoptado.D:.4f} d = {adoptado.d_critico:.4f} -> {'COINCIDE' if ok else 'DIFIERE'}; avisos: {len(avisos)}")
    return series

p("=== Caso 1 Piura")
s = caso_estacion("indeci_piura", "estacion.csv", {"Miraflores": (["serie_completa"], [25, 50, 100])})
decl(homogeneidad_serie_fen="serie_completa")
res, err = intenta(lambda: MH.precipitacion_de_diseno(s["Miraflores"], 25))
for a in res[4]: p("   AVISO:", a[:330])
for trat in ("serie_sin_fen", "dos_poblaciones"):
    decl(homogeneidad_serie_fen=trat)
    res, err = intenta(lambda: MH.precipitacion_de_diseno(s["Miraflores"], 25))
    p(f"  {trat}: {type(err).__name__ if err else 'SIN EXCEPCION'}: {str(err)[:420] if err else ''}")
ca.limpiar_valores_dinamicos()
res, err = intenta(lambda: MH.precipitacion_de_diseno(s["Miraflores"], 25))
p(f"  sin declarar: {type(err).__name__ if err else 'SIN EXCEPCION'}")
decl(homogeneidad_serie_fen="serie_completa", distribucion_precipitacion_maxima="gumbel", nivel_significancia_ks=0.01)
res, err = intenta(lambda: MH.precipitacion_de_diseno(s["Miraflores"], 25))
p(f"  gumbel con alfa 0.01: {'P = %.2f D = %.4f d = %.4f' % (res[0].P_TR_mm, res[0].D, res[0].d_critico) if res else type(err).__name__}")
s5 = MH.cargar_estacion(f"{RAIZ}/indeci_piura/estacion_fen_5_sin_1973.csv")
decl(homogeneidad_serie_fen="serie_sin_fen")
res, err = intenta(lambda: MH.precipitacion_de_diseno(s5["Miraflores"], 25))
p(f"  variante fen 5, serie_sin_fen: {type(err).__name__ if err else 'SIN EXCEPCION'}")

def caso_cuencas(caso, f_est, clave_cuencas, TRs, **criterios):
    esp_caso = json.load(open(f"{RAIZ}/{caso}/salida_esperada.json", encoding="utf-8"))
    ent = MH.cargar_entrada(f"{RAIZ}/{caso}/cuencas.csv", f"{RAIZ}/{caso}/{f_est}")
    n_ok = n_exc_ok = n_mal = 0
    for cid, cuenca in ent.cuencas.items():
        esp = esp_caso[clave_cuencas][cid]
        for T in TRs:
            decl(homogeneidad_serie_fen="serie_completa", **criterios)
            res, err = intenta(lambda: MH.caudal_de_diseno(cuenca, ent.estaciones[cuenca.estacion], T))
            e = esp if "excepcion" in esp else esp[str(T)]
            if "excepcion" in e:
                if err is not None and type(err).__name__ == e["excepcion"]:
                    n_exc_ok += 1; p(f"  {caso}/{cid} TR {T}: {type(err).__name__} (esperada) {str(getattr(err,'campo',''))}")
                else:
                    n_mal += 1; p(f"  {caso}/{cid} TR {T}: ESPERABA {e['excepcion']} y salio {type(err).__name__ if err else 'Q = %.3f' % res.Q_m3s}: {str(err)[:300] if err else ''}")
                break
            if err is not None:
                n_mal += 1; p(f"  {caso}/{cid} TR {T}: INESPERADO {type(err).__name__}: {str(err)[:400]}"); continue
            ok = cmp_("Q", res.Q_m3s, e["Q_m3s"]) & cmp_("I", res.I_mm_h, e["I_mm_h"]) & cmp_("C", res.C, e["C"])
            if "tc_min" in e: ok &= cmp_("tc", res.tc_min, e["tc_min"])
            if "Tc_h" in e: ok &= cmp_("tc", res.tc_min, e["Tc_h"]*60)
            n_ok += ok; n_mal += (not ok)
            if not ok or cid in ("MC-01", "C-1", "C-6", "A1", "ALC-19"):
                p(f"  {caso}/{cid} TR {T}: Q = {res.Q_m3s:.4f} I = {res.I_mm_h:.3f} C = {res.C} tc = {res.tc_min:.3f} min P24 = {res.P24_TR_mm:.3f} ({res.distribucion}) -> {'COINCIDE' if ok else 'DIFIERE'}")
    p(f"  {caso}: {n_ok} (cuenca, TR) coinciden, {n_exc_ok} excepciones esperadas, {n_mal} discrepancias")
    return ent

p("=== Caso 2 UPeU")
caso_estacion("upeu_colpahuayco", "estacion.csv", {"Sicuani": (["estacion"], [35, 70])})
caso_cuencas("upeu_colpahuayco", "estacion.csv", "cuencas", [35, 70])
p("=== Caso 3 Tumbes")
res, err = intenta(lambda: MH.cargar_estacion(f"{RAIZ}/untumbes_tu107/estacion_como_se_publica_fen_vacio.csv"))
p(f"  fen vacio: {type(err).__name__ if err else 'CARGA SIN ERROR'}: {str(err)[:200] if err else ''}")
st_ = caso_estacion("untumbes_tu107", "estacion_fen_declarado_por_el_verificador.csv", {"Cañaveral": (["estacion_serie_completa"], [35, 70, 140])})
decl(homogeneidad_serie_fen="serie_completa")
res, err = intenta(lambda: MH.precipitacion_de_diseno(st_["Cañaveral"], 35))
for a in res[4]: p("   AVISO:", a[:260])
p("   paso de consistencia:", res[3][-1].nota_del_proyecto[-330:])
caso_cuencas("untumbes_tu107", "estacion_fen_declarado_por_el_verificador.csv", "cuencas", [35, 70])
p("=== Caso 4 UNSAAC")
caso_estacion("unsaac_42tmc", "estacion.csv", {"Colquepata": (["estacion"], [35, 70])})
caso_cuencas("unsaac_42tmc", "estacion.csv", "cuencas_con_distribucion_gumbel", [35, 70], distribucion_precipitacion_maxima="gumbel")
p("=== Caso 5 UPAO")
caso_estacion("upao_la_jalca", "estacion.csv", {"Chachapoyas-A": (["Chachapoyas-A"], [10, 50, 100, 175, 500]), "Chachapoyas-B": (["Chachapoyas-B"], [2, 5, 10, 25, 50, 100, 500])})
ent = MH.cargar_entrada(f"{RAIZ}/upao_la_jalca/cuencas.csv", f"{RAIZ}/upao_la_jalca/estacion.csv")
esp = json.load(open(f"{RAIZ}/upao_la_jalca/salida_esperada.json", encoding="utf-8"))["ALC-19"]
c = ent.cuencas["ALC-19"]
decl(homogeneidad_serie_fen="serie_completa")
res, err = intenta(lambda: MH.caudal_de_diseno(c, ent.estaciones[c.estacion], 50))
p(f"  ALC-19 por omision: {type(err).__name__ if err else 'Q = %.3f' % res.Q_m3s}")
decl(homogeneidad_serie_fen="serie_completa", tc_fuera_de_la_poblacion_del_metodo="indicador_con_aviso")
res, err = intenta(lambda: MH.caudal_de_diseno(c, ent.estaciones[c.estacion], 50))
e = esp["con tc_fuera_de_la_poblacion_del_metodo=indicador_con_aviso, TR 50"]
if res: p(f"  ALC-19 con indicador: Q = {res.Q_m3s:.4f} (a mano {e['Q_m3s']:.4f}) I = {res.I_mm_h:.3f} ({e['I_mm_h']:.3f}) tc = {res.tc_min:.3f} ({e['tc_min']:.3f}) -> {'COINCIDE' if cmp_('Q', res.Q_m3s, e['Q_m3s']) else 'DIFIERE'}")
else: p("  ALC-19 con indicador:", type(err).__name__, str(err)[:300])
p("=== Caso 6 ESPOL")
caso_estacion("espol_intervalles", "estacion.csv", {k: ([k], [25, 50, 100]) for k in ("La Argelia", "Gonzanama", "Malacatos", "Catamayo")})
p(f"PEOR DIFERENCIA RELATIVA programa vs calculo a mano en lo comparado: {PEOR[0]:.3e}")
# adversarial: año repetido con la MISMA etiqueta
import tempfile
t = tempfile.mkdtemp()
open(f"{t}/e.csv", "w").write("estacion,anio,p24_mm,fen\nX,2001,63,no\nX,2001,63,no\n")
res, err = intenta(lambda: MH.cargar_estacion(f"{t}/e.csv")); p("etiqueta de año repetida:", type(err).__name__ if err else "carga")
ca.limpiar_valores_dinamicos()
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparacion_con_programa.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
