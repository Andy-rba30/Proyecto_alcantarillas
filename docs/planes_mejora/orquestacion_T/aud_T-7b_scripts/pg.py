import sys, fitz
PDF = {"aashto": "/home/user/andy-rba30/normas/normas/AASHTO.LRFD.Bridge.Design.Specifications_9th.Edition.2020.pdf",
       "hds5": "/home/user/andy-rba30/normas/normas/hif12026.pdf",
       "e050": "/home/user/andy-rba30/normas/normas/Norma E.050 Suelos y cimentaciones.pdf",
       "mp": "/home/user/andy-rba30/normas/normas/Puentes (Versión Libro).pdf",
       "hh": "/home/user/andy-rba30/normas/normas/Hidrología, Hidráulica y Drenaje (Versión Libro).pdf",
       "dg": "/home/user/andy-rba30/normas/normas/Manual.de.Carreteras.DG-2018.pdf"}
d = fitz.open(PDF[sys.argv[1]])
if sys.argv[2] == "png":
    for p in sys.argv[3:]:
        d[int(p)-1].get_pixmap(dpi=int(130)).save(f"{sys.argv[1]}_{p}.png")
elif sys.argv[2] == "find":
    pat = sys.argv[3]
    lo, hi = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1, len(d))
    for i in range(lo-1, hi):
        t = d[i].get_text()
        if pat in t:
            print("PDF", i+1)
else:
    for p in sys.argv[2:]:
        print(f"======== PDF {p} ========")
        print(d[int(p)-1].get_text())
