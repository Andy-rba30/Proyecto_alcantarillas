import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud")
sys.path.insert(0, "/home/user/wt/T-7b")
from a01 import correr
for q in (1.3, 1.4, 1.5, 1.75, 2.3):
    inf, a = correr(extra={"Q_evento_extremo_m3s": q})
    sec = a.resultado.seccion.etiqueta() if a.resultado is not None and a.resultado.seccion is not None else None
    v8 = None
    if a.resultado is not None and getattr(a.resultado, "verificaciones", None):
        v8 = [(v.valor_obtenido, v.valor_admisible, v.estado.name) for v in a.resultado.verificaciones if v.codigo == "V8"]
    print("Q_ext", q, "(x%.2f)" % (q/1.167), "dim", a.dimensionado, sec, "V8", v8, "cabezal", a.cabezal is not None)
    for b in a.bloqueos:
        print("   BLOQ", b.etapa, "|", b.tipo.name, "|", b.mensaje[:230])
