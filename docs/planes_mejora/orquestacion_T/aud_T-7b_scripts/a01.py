import json, sys, tempfile, math
from pathlib import Path
sys.path.insert(0, "/home/user/wt/T-7b")
from src import criterios_adoptados as ca, datos_sitio as ds, servicio
from src.modulos import M9_cabezal as M9
from src.modelos import CondicionAnalisis
RAIZ = Path("/home/user/wt/T-7b")
CSV = RAIZ/"tests"/"ejemplo_puntos.csv"
DECL = {
    "remanso_derecho_via": "embalse_a_nivel",
    "TR_evento_extremo": 500.0,
    "umbral_no_colapso_evento_extremo": "sin_desborde_de_la_plataforma",
    "phi_relleno_trasdos": 34.0,
    "c_phi_fundacion": {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0, "gamma_kn_m3": 18.0},
    "drenaje_trasdos": "drenado",
    "factor_muro_eleccion": "reduccion_por_desplazamiento",
}
FILA = ("A-01,0+380,A,1.167,850,0.006,42.10,44.20,44.05,8.5,15,9.60,41.30,,,SM,,,")
def correr(extra=None, decl=None, NF="1.4", ancho=400.0, alcance=None):
    tmp = Path(tempfile.mkdtemp(dir="/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud"))
    a01 = {"ancho_derecho_via_m": ancho, "Q_evento_extremo_m3s": 1.3, "TW_evento_extremo_m": 0.5}
    a01.update(extra or {})
    (tmp/"ext.json").write_text(json.dumps({"globales": {"luz_m": 3.0, "TW_m": 0.3}, "puntos": {"A-01": a01}}))
    ext = servicio.cargar_datos_externos(tmp/"ext.json", {})
    for k, v in dict(DECL, **(decl or {})).items():
        ca.establecer_valor_dinamico(k, v)
    ds.establecer_dato_dinamico("orientacion_muro_respecto_al_trafico", "paralelo_al_trafico", "de prueba", "2026-11-13", origen="prueba")
    ds.establecer_dato_dinamico("distancia_borde_calzada_al_trasdos_m", 1.6, "de prueba", "2026-11-13", origen="prueba")
    t = CSV.read_text(encoding="utf-8"); assert FILA in t
    (tmp/"p.csv").write_text(t.replace(FILA, FILA.replace(",SM,,,", f",SM,{NF},,")), encoding="utf-8")
    inf = servicio.correr(tmp/"p.csv", ext, alcance=alcance or servicio.ALCANCE_EXPEDIENTE)
    return inf, next(p for p in inf.puntos if p.punto.id == "A-01")
if __name__ == "__main__":
    inf, a = correr()
    print("dim", a.dimensionado, a.resultado.seccion.etiqueta())
    for v in a.resultado.verificaciones:
        print(v.codigo, v.estado, v.valor_obtenido, v.valor_admisible)
    print("bloqueos", [(b.etapa, b.tipo, str(b)[:200]) for b in a.bloqueos])
    for g in a.cabezal.geometrias:
        print(g)
    for e in a.cabezal.estabilidad:
        print("=====", e.extremo, e.condicion, "K_A", e.K_A, "K_AE", e.K_AE, "i", e.i_grados, "delta", e.delta_grados, "h", e.altura_empuje, "heq", e.h_eq, "kh", e.k_h)
        for c in e.cargas:
            print("   ", c.codigo, c.tipo, "V", round(c.V,4), "H", round(c.H,4), "x", round(c.x,4), "z", round(c.z,4), c.sobre)
        for c in e.combinaciones:
            print("  C", c.marco, c.nombre, "|", c.para, "N", round(c.N,3), "H", round(c.H,3), "Me", round(c.M_estabilizante,3), "Mv", round(c.M_volcante,3), "e", round(c.excentricidad,4))
            print("     ", c.factores)
        for v in e.verificaciones:
            print("  V", v.codigo, v.estado, v.valor_obtenido, v.valor_admisible)
