import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7b-aud")
sys.path.insert(0, "/home/user/wt/T-7b")
from a01 import correr
for ancho in (40.0, 300.0):
    inf, a = correr(ancho=ancho)
    print("ancho", ancho, "dimensionado", a.dimensionado, "seccion", a.resultado.seccion.etiqueta() if a.resultado and a.resultado.seccion else None, "aceptado", getattr(a.resultado, "aceptado", None))
    for b in a.bloqueos:
        print("   BLOQ", b.fase, "|", b.etapa, "|", b.tipo, "|", b.mensaje[:400])
    print("   traza:", len(a.traza))
    for t in a.traza[:40]:
        inc = getattr(t, "incumplidas", None)
        print("     ", getattr(t, "material", None) and t.material.nombre if hasattr(getattr(t,'material',None),'nombre') else getattr(t,'material',None), getattr(t, "D", None), inc, str(getattr(t, "motivo", ""))[:160])
    print("   avisos exp:", [x[:200] for x in a.avisos_de_expediente])
