import sys, json, ast
from tests.apoyo import validacion_integral as V
def run(cambios, show_ver=False, pts=None):
    inf = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
    for p in inf.puntos:
        if pts and p.punto.id not in pts: continue
        r = p.resultado
        print(p.punto.id, "dim" if p.dimensionado else "NO-dim", r.seccion.etiqueta() if r else None, r.material.nombre if r else None)
        for b in p.bloqueos:
            print("   BLOQ", b.tipo.value, "|", b.etapa, "|", b.campo, b.criterio, "|", " ".join(str(b.mensaje).split())[:300])
        if show_ver:
            v = V.verificaciones_del_punto(inf, p.punto.id)
            print("   ", {k:e for k,e in v.items() if e not in ("cumple","no aplica")})
    cab = inf.cabezal
    for b in (cab.bloqueos if cab else ()):
        print("  PROY BLOQ", b.tipo.value, "|", b.etapa, "|", b.criterio)
    return inf
if __name__ == "__main__":
    cambios = ast.literal_eval(sys.argv[1])
    run(cambios, show_ver=len(sys.argv)>2)
