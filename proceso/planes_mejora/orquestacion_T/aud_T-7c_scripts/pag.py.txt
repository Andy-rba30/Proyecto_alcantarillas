import sys, warnings
warnings.simplefilter("ignore")
import fitz
N="/home/user/andy-rba30/normas/normas/"
F={"aashto":"AASHTO.LRFD.Bridge.Design.Specifications_9th.Edition.2020.pdf","e060":"Norma E.060 Concreto armado.pdf","eg":"MC-01-13 Especificaciones Tecnicas Generales para Construcción - EG-2013 - (Versión Revisada - JULIO 2013).pdf","mp":"Puentes (Versión Libro).pdf","e050":"Norma E.050 Suelos y cimentaciones.pdf"}
d=fitz.open(N+F[sys.argv[1]])
for p in sys.argv[2:]:
    if p.startswith("png:"):
        n=int(p[4:]); d[n-1].get_pixmap(dpi=110).save(f"{sys.argv[0].rsplit('/',1)[0]}/{sys.argv[1]}_{n}.png"); print("png", n); continue
    n=int(p); print(f"=========== {sys.argv[1]} PDF {n} ==========="); print(d[n-1].get_text())
