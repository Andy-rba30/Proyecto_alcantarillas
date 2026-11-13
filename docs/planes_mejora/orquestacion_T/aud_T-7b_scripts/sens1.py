import sys, json
sys.path.insert(0, "/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud")
sys.path.insert(0, "/home/user/wt/T-7b")
from a01 import correr
nombre, decl = sys.argv[1], json.loads(sys.argv[2])
extra = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
inf, a = correr(decl=decl, extra=extra)
print("==", nombre, "| dim", a.dimensionado)
f = lambda x: "None" if x is None else (f"{x:.2f}" if isinstance(x, (int, float)) else str(x))
if a.cabezal is not None:
    for e in a.cabezal.estabilidad:
        print("   ", e.extremo[:3], e.condicion.value[:3], " ".join(f"{v.codigo.split('.')[0]}:{v.estado.name[:3]}({f(v.valor_obtenido)}/{f(v.valor_admisible)})" for v in e.verificaciones))
for b in a.bloqueos:
    print("   BLOQ", b.etapa[:60], "|", b.tipo.name, "|", b.mensaje[:260])
