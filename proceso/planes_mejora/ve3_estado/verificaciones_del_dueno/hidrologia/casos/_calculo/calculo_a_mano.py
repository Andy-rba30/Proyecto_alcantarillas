# -*- coding: utf-8 -*-
"""
CALCULO A MANO, INDEPENDIENTE, de los casos reales de hidrologia.
No importa nada de /home/user/Proyecto_alcantarillas/src. Solo math,
statistics y scipy (cuantil normal y cuantil exacto de Kolmogorov-Smirnov).

Formulas, tal como las ESCRIBE el Manual de Hidrologia, Hidraulica y Drenaje
(MTC), capitulo III (paginas impresas):
  3.7.1.1 Normal: mu = media, S = desv. estandar (n-1)            (pag. 26)
  3.7.1.2 Log Normal 2P: media y desv. (n-1) de los logaritmos     (pag. 26-27)
  3.7.1.7 Gumbel por momentos: alfa = 1.2825/sigma ;
          beta = mu - 0.45 sigma ; F(x) = exp(-exp(-alfa(x-beta))) (pag. 29)
  3.7.2 b K-S: D = max|Fo(xm) - F(xm)| ; Fo(xm) = 1 - m/(n+1), m = orden de
          mayor a menor (ec. 13) ; Tabla N 03                      (pag. 32-33)
  3.8.1  Dick-Peschke: Pd = P24 (d/1440)^0.25 ; I = Pd / d  (ec. 16, pag. 37)
  3.9    Tabla N 05, Kirpich: tc = 0.01947 L^0.77 S^-0.385 (min, m, m/m)
  3.12.2 Racional: Q = 0.278 C I A  (ec. 28, pag. 49) ; Tabla N 08 (pag. 50)
  3.12.2.1 Racional modificado (pag. 51-52):
          Tc = 0.3 (L/S^0.25)^0.76 (30) ; K = 1 + Tc^1.25/(Tc^1.25+14) (31)
          KA = 1 - log10(A)/15 (32) ; P = KA Pd (33)
          I = (P/24) 11^((28^0.1 - Tc^0.1)/(28^0.1 - 1)) (34)
          C = (Pd-Po)(Pd+23Po)/(Pd+11Po)^2 ; Po = 5000/CN - 50 (35)
          Q = 0.278 C I A K (29)
"""
import json, math, statistics as st, sys, os
from scipy.stats import norm, kstwo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datos_publicados as D

OUT = []
RES = {}
def p(*a):
    OUT.append(" ".join(str(x) for x in a))

T03 = {5:0.56, 10:0.41, 15:0.34, 20:0.29, 25:0.26, 30:0.24, 35:0.22, 40:0.21}  # alfa 0.05

def d_critico(n, alfa=0.05):
    if alfa == 0.05 and n in T03:
        return T03[n], "Tabla N 03"
    return float(kstwo.ppf(1 - alfa, n)), "cuantil exacto K-S (la Tabla N 03 no trae la fila)"

def ks(valores, F):
    n = len(valores)
    orden = sorted(valores, reverse=True)
    return max(abs((1 - m/(n+1)) - F(x)) for m, x in enumerate(orden, 1))

def ks_clasico(valores, F):
    """K-S de escalon (Dn = max(i/n - F, F - (i-1)/n)), el de los programas
    estadisticos generales; NO es el del Manual. Solo contraste de metodo."""
    n = len(valores); o = sorted(valores)
    return max(max((i+1)/n - F(x), F(x) - i/n) for i, x in enumerate(o))

def ajustes(valores, TRs):
    n = len(valores); mu = st.fmean(valores); s = st.stdev(valores)
    r = {"n": n, "media": mu, "s": s}
    N = lambda x: norm.cdf((x - mu)/s)
    r["normal"] = dict(D=ks(valores, N), Dcl=ks_clasico(valores, N),
                       P={T: mu + norm.ppf(1-1/T)*s for T in TRs})
    if min(valores) > 0:
        ln = [math.log(v) for v in valores]; Y = st.fmean(ln); Sy = st.stdev(ln)
        L = lambda x: norm.cdf((math.log(x) - Y)/Sy)
        r["lognormal_2p"] = dict(Y=Y, Sy=Sy, Y10=Y/math.log(10), Sy10=Sy/math.log(10),
                                 D=ks(valores, L), Dcl=ks_clasico(valores, L),
                                 P={T: math.exp(Y + norm.ppf(1-1/T)*Sy) for T in TRs})
    alfa = 1.2825/s; beta = mu - 0.45*s
    G = lambda x: math.exp(-math.exp(-alfa*(x - beta)))
    r["gumbel"] = dict(alfa=alfa, beta=beta, D=ks(valores, G), Dcl=ks_clasico(valores, G),
                       P={T: beta - math.log(-math.log(1-1/T))/alfa for T in TRs},
                       KT={T: (beta - math.log(-math.log(1-1/T))/alfa - mu)/s for T in TRs})
    r["d"], r["d_origen"] = d_critico(n)
    dist = [k for k in ("normal", "lognormal_2p", "gumbel") if k in r]
    r["mejor"] = min(dist, key=lambda k: r[k]["D"])
    return r

def muestra(nombre, r, TRs):
    p(f"  [{nombre}] n = {r['n']}  media = {r['media']:.4f}  s(n-1) = {r['s']:.4f}  "
      f"d(0.05) = {r['d']:.4f} ({r['d_origen']})")
    for k in ("normal", "lognormal_2p", "gumbel"):
        if k not in r: p(f"    {k}: no evaluable (hay 0 mm)"); continue
        a = r[k]
        extra = (f" Y = {a['Y']:.4f} Sy = {a['Sy']:.4f} (log10: {a['Y10']:.4f}, {a['Sy10']:.4f})"
                 if k == "lognormal_2p" else
                 f" alfa = {a['alfa']:.5f} beta = {a['beta']:.4f}" if k == "gumbel" else "")
        p(f"    {k}: D = {a['D']:.4f} ({'pasa' if a['D'] < r['d'] else 'NO pasa'}) "
          f"[K-S de escalon: {a['Dcl']:.4f}]{extra}")
        p("      P(TR): " + "  ".join(f"{T}: {a['P'][T]:.2f}" for T in TRs))
    p(f"    mejor ajuste K-S (menor D): {r['mejor']}")

def tc_temez_h(L_km, S): return 0.3*(L_km/S**0.25)**0.76
def K_unif(Tc_h): return 1 + Tc_h**1.25/(Tc_h**1.25 + 14)
def KA(A_km2): return 1 - math.log10(A_km2)/15
def I_34(P_mm, Tc_h): return P_mm/24*11**((28**0.1 - Tc_h**0.1)/(28**0.1 - 1))
def Po(CN): return 5000/CN - 50
def C_35(Pd, CN):
    po = Po(CN); return (Pd - po)*(Pd + 23*po)/(Pd + 11*po)**2
def CN_de_C(Pd, C):
    lo, hi = 20.0, 100.0
    for _ in range(200):
        mid = (lo + hi)/2
        if C_35(Pd, mid) < C: lo = mid
        else: hi = mid
    return (lo + hi)/2
def I_dp(P24, d_min): return P24*(d_min/1440)**0.25/(d_min/60)
def kirpich_min(L_m, S, exp_L=0.77): return 0.01947*L_m**exp_L*S**-0.385
def dif(a, b): return 100*(a - b)/b

# =========================================================================
p("="*78); p("CASO 1. INDECI-OEA Piura, estacion Miraflores 1971-2008"); p("="*78)
TR1 = [2, 5, 10, 20, 25, 50, 100, 200, 500, 1000]
completa = [D.PIURA[a] for a in sorted(D.PIURA)]
sin_fen = [D.PIURA[a] for a in sorted(D.PIURA) if a not in D.PIURA_FEN_ESTUDIO]
solo_fen = [D.PIURA[a] for a in D.PIURA_SOLO_FEN]
rc, rs = ajustes(completa, TR1), ajustes(sin_fen, TR1)
muestra("serie completa (con FEN), 38 años", rc, TR1)
muestra("sin FEN segun el estudio (quita 1972,1973,1983,1987,1992,1998), 32 años", rs, TR1)
RES["piura"] = {"completa": rc, "sin_fen": rs}
for clave, r in (("con_fen", rc), ("sin_fen", rs)):
    imp = D.PIURA_IMPRESO[clave]
    p(f"  -- contraste con lo impreso ({clave}) --")
    p(f"    media {r['media']:.2f} vs {imp['mu']}; s {r['s']:.2f} vs {imp['s']}; "
      f"log10: {r['lognormal_2p']['Y10']:.3f} vs {imp['mu_log10']}; {r['lognormal_2p']['Sy10']:.3f} vs {imp['s_log10']}")
    for dist, col in (("normal", "normal"), ("lognormal_2p", "lognormal"), ("gumbel", "gumbel_mod")):
        difs = [dif(r[dist]["P"][T], v) for T, v in imp[col].items()]
        p(f"    {dist} vs columna «{col}»: dif. max = {max(difs, key=abs):+.2f} %  "
          f"(TR 25: {r[dist]['P'][25]:.2f} vs {imp[col][25]})")
    p(f"    Gumbel momentos vs columna «Gumbel» (N=20, Ponce): TR 25: {r['gumbel']['P'][25]:.2f} vs {imp['gumbel_N20'][25]} "
      f"({dif(r['gumbel']['P'][25], imp['gumbel_N20'][25]):+.1f} %)")
    p(f"    K_T Gumbel momentos TR 5/25/100: {r['gumbel']['KT'][5]:.4f} {r['gumbel']['KT'][25]:.4f} {r['gumbel']['KT'][100]:.4f} "
      f"vs impreso «modificado» {D.PIURA_KT_GUMBEL_MOD[5]} {D.PIURA_KT_GUMBEL_MOD[25]} {D.PIURA_KT_GUMBEL_MOD[100]}")
    dl = imp["delta"]
    p(f"    Delta K-S (ec. 13) normal {r['normal']['D']:.3f} vs {dl['normal']}; LN {r['lognormal_2p']['D']:.3f} vs {dl['lognormal']}; "
      f"Gumbel mom. {r['gumbel']['D']:.3f} vs «mod.» {dl['gumbel_mod']} / «N=20» {dl['gumbel_N20']}; "
      f"critico {r['d']:.4f} vs {dl['tab']} (1.36/raiz(n) = {1.36/math.sqrt(r['n']):.4f})")
p("  -- solo FEN (5 datos): media %.2f s %.2f ; log10 %.3f %.3f (impreso 106.5, 57.76, 1.961, 0.286)" % (
    st.fmean(solo_fen), st.stdev(solo_fen), st.fmean([math.log10(v) for v in solo_fen]), st.stdev([math.log10(v) for v in solo_fen])))
p("  -- regla FEN (mas conservador): P24(TR) LN completa vs LN sin FEN --")
for T in (25, 50, 100):
    p(f"    TR {T}: completa {rc['lognormal_2p']['P'][T]:.1f} mm ; sin FEN {rs['lognormal_2p']['P'][T]:.1f} mm ; "
      f"razon {rc['lognormal_2p']['P'][T]/rs['lognormal_2p']['P'][T]:.2f}")
# lo observado: mayor registro con T empirico <= TR
def cubre(valores, anios, TR):
    n = len(valores); m = math.ceil((n+1)/TR)
    o = sorted(zip(valores, anios), reverse=True)
    return o[m-1], m, (n+1)/m
for T in (25, 50, 100):
    (v, a), m, Te = cubre(completa, sorted(D.PIURA), T)
    p(f"    contraste con lo observado TR {T}: registro {v} mm ({a}), m = {m}, T emp = {Te:.1f}; LN da {rc['lognormal_2p']['P'][T]:.1f}")
# variantes de declaracion FEN
p("  -- sensibilidad a la declaracion de años FEN (LN, TR 25 / 100) --")
variantes = {"estudio (6 años)": D.PIURA_FEN_ESTUDIO,
             "solo los 5 del Anexo 07.3 (1973 se queda)": D.PIURA_SOLO_FEN,
             "estudio + 1997": D.PIURA_FEN_ESTUDIO + (1997,),
             "estudio + 1997 + 2002": D.PIURA_FEN_ESTUDIO + (1997, 2002)}
RES["piura"]["variantes"] = {}
for nombre, fen in variantes.items():
    v = [D.PIURA[a] for a in sorted(D.PIURA) if a not in fen]
    r = ajustes(v, TR1)
    RES["piura"]["variantes"][nombre] = r
    p(f"    {nombre}: n = {r['n']}, mejor = {r['mejor']} (D {r[r['mejor']]['D']:.4f}), LN P25 = {r['lognormal_2p']['P'][25]:.1f}, P100 = {r['lognormal_2p']['P'][100]:.1f}")
sin1971 = [D.PIURA[a] for a in sorted(D.PIURA) if a != 1971]
r = ajustes(sin1971, TR1); RES["piura"]["sin_1971"] = r
p(f"    serie completa sin 1971 (año parcial): n = {r['n']}, LN P25 = {r['lognormal_2p']['P'][25]:.1f}, P100 = {r['lognormal_2p']['P'][100]:.1f}, D LN = {r['lognormal_2p']['D']:.4f}")
p("  -- intensidad del estudio (Cuadro 27): P24/6 h: 131.82/6 = %.2f (impreso 21.97)" % (131.82/6))

# =========================================================================
p(""); p("="*78); p("CASO 2. UPeU Colpahuayco-Langui, estacion Sicuani 1993-2020"); p("="*78)
TR2 = [5, 20, 35, 50, 70, 100]
sic = [D.SICUANI[a] for a in sorted(D.SICUANI)]
r2 = ajustes(sic, TR2); RES["upeu"] = {"sicuani": r2}
muestra("Sicuani, 28 años", r2, TR2)
p("    Pearson III impreso (Tabla 7): " + "  ".join(f"{T}: {v}" for T, v in D.SICUANI_P3_IMPRESO.items()))
for k in ("normal", "lognormal_2p", "gumbel"):
    p(f"    {k} vs Pearson III impreso, TR 35 / 70: {dif(r2[k]['P'][35], 42.62):+.1f} % / {dif(r2[k]['P'][70], 44.98):+.1f} %")
p(f"    Delta tabular impreso 0.2570 = 1.36/raiz(28) = {1.36/math.sqrt(28):.4f}; el del programa: {r2['d']:.4f}")
Pd = 44.98
p("  -- racional modificado del documento (TR 70, Pd = 44.98 mm), recalculado con la Tabla 6 --")
p("   id   A6km2  A8ha   L km   s     Tc_h   K     K_imp  KA     I(34)  I_imp  dif%   C_imp CN(C)  Q_T6   Q_T8A  Q_T8A_sinK  Q_imp")
RES["upeu"]["paso"] = {}
for i, (Kimp, Iimp, Aha, Cimp, Qimp) in D.UPEU_T8.items():
    t = D.UPEU_T6[i]; Tc = tc_temez_h(t["L"], t["s"]); K = K_unif(Tc); ka = KA(t["A"])
    I = I_34(ka*Pd, Tc); cn = CN_de_C(Pd, Cimp)
    Q6 = 0.278*Cimp*I*t["A"]*K; Q8 = 0.278*Cimp*I*(Aha/100)*K; Q8s = 0.278*Cimp*I*(Aha/100)
    Q8imp = 0.278*Cimp*Iimp*(Aha/100)
    RES["upeu"]["paso"][i] = dict(Tc_h=Tc, K=K, KA=ka, I34=I, CN_implicito=cn, Q_T6=Q6, Q_T8A=Q8, Q_T8A_sinK=Q8s,
                                   Q_impresos_sinK=Q8imp, Q_impresos_conK=Q8imp*Kimp)
    p(f"   {i:>2}  {t['A']:6.2f} {Aha:7.2f} {t['L']:5.2f} {t['s']:5.2f} {Tc:6.3f} {K:5.3f} {Kimp:5.2f} {ka:6.4f} {I:6.2f} {Iimp:6.2f} {dif(I, Iimp):+5.1f} "
       f"{Cimp:5.2f} {cn:5.1f} {Q6:6.2f} {Q8:6.2f} {Q8s:6.2f}      {Qimp:5.2f}   [0.278·C·I_imp·A8: sin K {Q8imp:.2f}, con K {Q8imp*Kimp:.2f}]")
p("  -- lo que hace MH bajo 10 km2 (metodo racional, tc Temez, Dick-Peschke, K aplicado): I y Q por unidad de C --")
p("   id   tc_min  Pd_dp  I_dp   I(34)  dp/34   Q/C con K (A Tabla 6)   Temez en rango 0.25-24 h")
for i in D.UPEU_T8:
    t = D.UPEU_T6[i]; Tc = tc_temez_h(t["L"], t["s"]); d = Tc*60
    I = I_dp(Pd, d); I34 = I_34(KA(t["A"])*Pd, Tc)
    RES["upeu"]["paso"][i].update(I_dp=I, Q_por_C_MH=0.278*I*t["A"]*K_unif(Tc))
    p(f"   {i:>2}  {d:6.2f} {Pd*(d/1440)**0.25:6.2f} {I:6.2f} {I34:6.2f} {I/I34:5.2f}   {0.278*I*t['A']*K_unif(Tc):7.3f}                 {'si' if 0.25 <= Tc <= 24 else 'NO'}")
p("  -- cuencas 7 y 14 (>= 10 km2): racional modificado completo, falta CN --")
RES["upeu"]["mayores"] = {}
for i in (7, 14):
    t = D.UPEU_T6[i]; Tc = tc_temez_h(t["L"], t["s"]); K = K_unif(Tc); ka = KA(t["A"]); I = I_34(ka*Pd, Tc)
    fila = {cn: 0.278*C_35(Pd, cn)*I*t["A"]*K for cn in (70, 75, 80, 85, 90) if Pd > Po(cn)}
    # CN que reproduce el HEC-HMS
    lo, hi = 55.0, 99.0
    for _ in range(100):
        mid = (lo+hi)/2
        if 0.278*C_35(Pd, mid)*I*t["A"]*K < D.UPEU_HMS[i]: lo = mid
        else: hi = mid
    RES["upeu"]["mayores"][i] = dict(Tc_h=Tc, K=K, KA=ka, P=ka*Pd, I34=I, Q_por_CN=fila, CN_equivalente_HMS=lo)
    p(f"   {i}: A = {t['A']} km2, Tc = {Tc:.3f} h, K = {K:.4f}, KA = {ka:.4f}, P = {ka*Pd:.2f} mm, I = {I:.2f} mm/h; "
      + "; ".join(f"CN {cn}: Q = {q:.2f}" for cn, q in fila.items())
      + f"; HEC-HMS impreso {D.UPEU_HMS[i]} m3/s <-> CN equivalente {lo:.1f}; Po(CN) = Pd en CN = {5000/(Pd+50):.1f}")
p("  -- Tc de la Tabla 6 (min) vs Kirpich del Manual (0.01947 L^0.77 S^-0.385) --")
for i in (1, 2, 7, 14):
    t = D.UPEU_T6[i]
    p(f"   {i}: impreso {t['Tc']} min ; Kirpich con s = {kirpich_min(t['L']*1000, t['s']):.2f} ; con S = {kirpich_min(t['L']*1000, t['S']):.2f}; (Hmax-hmin)/L = {(t['Hmax']-t['hmin'])/(t['L']*1000):.3f}")

# =========================================================================
p(""); p("="*78); p("CASO 3. UNTumbes TU-107, estacion Cañaveral (40 años)"); p("="*78)
TR3 = [5, 10, 25, 35, 50, 70, 100, 140, 500]
ts = D.tumbes_serie(); tm = D.tumbes_mensual()
tv = [ts[a] for a in sorted(ts)]
r3 = ajustes(tv, TR3); RES["tumbes"] = {"serie_publicada": r3}
muestra("Cañaveral tal como se publica, 40 años", r3, TR3)
ti = D.TUMBES_IMPRESO
p(f"    impreso: media {ti['media']}, s {ti['s']}, ln: {ti['media_ln']}, {ti['s_ln']}; Delta N {ti['delta']['normal']}, LN2 {ti['delta']['lognormal_2p']}, Gumbel {ti['delta']['gumbel']}; critico {ti['delta']['tab']}")
p("    LN2 vs Tabla 47 (HidroEsta): " + "  ".join(f"{T}: {r3['lognormal_2p']['P'][T]:.2f}/{ti['ln2'][T]} ({dif(r3['lognormal_2p']['P'][T], ti['ln2'][T]):+.2f}%)" for T in TR3 if T in ti['ln2']))
p("  -- filas duplicadas mes a mes (Tabla 23) --")
anios = sorted(tm)
dup = []
for i, a in enumerate(anios):
    for b in anios[i+1:]:
        ig = sum(1 for x, y in zip(tm[a][0], tm[b][0]) if abs(x-y) < 1e-9)
        cerca = sum(1 for x, y in zip(tm[a][0], tm[b][0]) if abs(x-y) <= 0.11)
        if cerca >= 11 and sum(tm[a][0]) > 0:
            dup.append((a, b, ig, cerca)); p(f"    {a} y {b}: {ig} de 12 meses identicos ({cerca} de 12 a menos de 0.11 mm); maximo anual {tm[a][1]} y {tm[b][1]}")
from collections import Counter
rep = {v: [a for a in ts if ts[a] == v] for v, c in Counter(tv).items() if c > 1}
p(f"    maximos anuales repetidos (valor: años): {rep}")
RES["tumbes"]["duplicados"] = dup
tv2 = [ts[a] for a in sorted(ts) if a not in (2001, 2002)]
r3b = ajustes(tv2, TR3); RES["tumbes"]["sin_2001_2002"] = r3b
muestra("sin las dos filas copiadas (2001, 2002), 38 años", r3b, TR3)
p(f"    efecto de quitar las copias en LN2: P35 {dif(r3b['lognormal_2p']['P'][35], r3['lognormal_2p']['P'][35]):+.1f} %, P70 {dif(r3b['lognormal_2p']['P'][70], r3['lognormal_2p']['P'][70]):+.1f} %, P140 {dif(r3b['lognormal_2p']['P'][140], r3['lognormal_2p']['P'][140]):+.1f} %")
p("  -- plausibilidad: meses con «maxima en 24 h» >= 300 mm --")
for a in anios:
    g = [f"{x:g}" for x in tm[a][0] if x >= 300]
    if g: p(f"    {a}: {', '.join(g)}")
p(f"    max/mediana de la serie: {max(tv):.1f}/{st.median(tv):.1f} = {max(tv)/st.median(tv):.1f}")
tc_ = D.tumbes_cuencas(); tt = D.tumbes_tc(); tq = D.tumbes_q()
p("  -- 41 cuencas: Temez (ec. 30) con L y S de la Tabla 26 vs la columna TEMEZ de la Tabla 27 --")
peor = 0; fuera = []
RES["tumbes"]["cuencas"] = {}
for c, v in tc_.items():
    Tc = tc_temez_h(v["L"], v["S"]); Sx = (v["zmax"] - v["zmin"])/(v["L"]*1000); Tcx = tc_temez_h(v["L"], Sx)
    RES["tumbes"]["cuencas"][c] = dict(Tc_h_S2dec=Tc, S_cotas=Sx, Tc_h_S_cotas=Tcx, impreso=tt[c][1])
    peor = max(peor, abs(Tcx - tt[c][1]))
    if not 0.25 <= Tcx <= 24: fuera.append((c, round(Tcx, 3)))
p(f"    con S = (cota max - cota min)/L: desvio maximo contra lo impreso = {peor:.3f} h (redondeo a 2 decimales = 0.005)")
p(f"    fuera del rango 0.25-24 h de Temez: {fuera}")
for c in ("C-1", "C-2", "C-6", "C-20", "C-35"):
    x = RES["tumbes"]["cuencas"][c]
    p(f"    {c}: S tabla {tc_[c]['S']}, S cotas {x['S_cotas']:.4f}; Tc(S tabla) {x['Tc_h_S2dec']:.3f}, Tc(S cotas) {x['Tc_h_S_cotas']:.3f}, impreso {x['impreso']}")
p("  -- caudal del documento: IDF propia y C I A / 3.6, recalculado --")
idf = D.TUMBES_IDF
for c in ("C-1", "C-2", "C-35", "C-39"):
    A, S, C, I35, I70, I140, Q35, Q70, Q140 = tq[c]; t = tt[c][3]
    I = idf["K"]*35**idf["m"]/t**idf["n"]
    p(f"    {c}: I35 = {I:.2f} (impreso {I35}); Q35 = C·I·A/3.6 = {C*I35*A/3.6:.2f} (impreso {Q35}); A que reproduce Q: {Q35*3.6/(C*I35):.3f} km2 (tabla {A})")
p("  -- lo que daria el metodo del Manual que MH implementa (LN2 serie publicada, f = 1.00, Dick-Peschke, K Temez) --")
p("   cuenca  A     tc_min(Temez,S cotas)  P24(35)  I_dp    Q/C·K    | doc: I35     razon I_dp/I_doc")
for c in ("C-1", "C-2", "C-5", "C-35", "C-39"):
    v = tc_[c]; Tc = RES["tumbes"]["cuencas"][c]["Tc_h_S_cotas"]; d = Tc*60
    P35 = r3["lognormal_2p"]["P"][35]; I = I_dp(P35, d)
    RES["tumbes"]["cuencas"][c].update(I_dp_35=I, Q_por_C_35=0.278*I*v["A"]*K_unif(Tc), K=K_unif(Tc))
    p(f"   {c:5} {v['A']:5.2f} {d:8.2f}               {P35:7.1f} {I:7.1f} {0.278*I*v['A']*K_unif(Tc):7.2f}   | {tq[c][3]:7.2f}    {I/tq[c][3]:.2f}")

# =========================================================================
p(""); p("="*78); p("CASO 4. UNSAAC Roquepata, estacion Colquepata 1990-2014"); p("="*78)
TR4 = [10, 30, 35, 70, 100, 150, 200, 250, 500, 1000]
col = [D.COLQUEPATA[a] for a in sorted(D.COLQUEPATA)]
r4 = ajustes(col, TR4); RES["unsaac"] = {"colquepata": r4}
muestra("Colquepata, 25 años", r4, TR4)
ci = D.COLQUEPATA_IMPRESO
p(f"    impreso: media {ci['media']}, s {ci['s']}; desv. poblacional (n) = {st.pstdev(col):.3f}")
p("    Gumbel por momentos vs Tabla 6.7 (K, Pmax): " + "  ".join(
    f"{T}: K {r4['gumbel']['KT'][T]:.4f}/{ci['gumbel'][T][0]} P {r4['gumbel']['P'][T]:.3f}/{ci['gumbel'][T][1]}" for T in TR4))
p(f"    dif. maxima P: {max(abs(dif(r4['gumbel']['P'][T], ci['gumbel'][T][1])) for T in TR4):.3f} %")
m1 = st.fmean(col[:8]); m2 = st.fmean(col[8:])
p(f"    inhomogeneidad: media 1990-1997 = {m1:.2f} mm (max {max(col[:8])}), media 1998-2014 = {m2:.2f} mm (min {min(col[8:])})")
r4b = ajustes(col[8:], TR4); RES["unsaac"]["colquepata_1998_2014"] = r4b
muestra("solo 1998-2014 (17 años), para ver el efecto del quiebre", r4b, TR4)
p("  -- Dick-Peschke (ec. 16), Tabla 6.8: I = P24 (d/1440)^0.25 / (d/60) --")
peor = 0
for T, (P24, fila) in D.UNSAAC_DP.items():
    for d, imp in zip(D.UNSAAC_DP_D, fila):
        peor = max(peor, abs(I_dp(P24, d) - imp))
p(f"    48 celdas recalculadas con la P24 impresa a 2 decimales: desvio maximo = {peor:.3f} mm/h")
p(f"    ejemplo T = 70, d = 20 min: {I_dp(60.89, 20):.2f} (impreso 62.71)")
p("  -- 15 microcuencas: Temez (ec. 30) vs Tabla 6.5; rango 0.25-24 h; Kirpich y su poblacion 3-10 % --")
p("   id    A km2   L m   S      Temez_min imp    en rango  Kirpich_min   Q_doc35  I_doc35 | MH: I_dp(tc Temez) K     Q35(C=0.5,K)  dif% vs doc")
P35 = r4["gumbel"]["P"][35]; P70 = r4["gumbel"]["P"][70]
RES["unsaac"]["cuencas"] = {}
for c, (Am2, L, Sp, tT, tB, tP, I30, I35, I70, Q30, Q35, Q70) in D.UNSAAC.items():
    A = Am2/1e6; S = Sp/100; Tc = tc_temez_h(L/1000, S); d = Tc*60
    enr = 0.25 <= Tc <= 24
    I = I_dp(P35, d); K = K_unif(Tc); Q = 0.278*0.5*I*A*K
    Idoc = D.UNSAAC_IDF["K"]*35**D.UNSAAC_IDF["m"]/tP**D.UNSAAC_IDF["n"]
    RES["unsaac"]["cuencas"][c] = dict(A_km2=A, tc_temez_min=d, en_rango=enr, kirpich_min=kirpich_min(L, S),
        I_dp_35=I, K=K, Q35_MH=Q, Q35_MH_sinK=Q/K, I_doc_recalc=Idoc, Q_doc_recalc=0.5*I35*(Am2/1e4)/360,
        I_dp_70=I_dp(P70, d), Q70_MH=0.278*0.5*I_dp(P70, d)*A*K)
    p(f"   {c:4} {A:6.4f} {L:5} {S:6.4f} {d:8.2f} {tT:6.2f}  {'si' if enr else 'NO':3}     {kirpich_min(L, S):6.2f}       {Q35:5.2f}   {I35:6.2f}  | {I:7.2f}           {K:.3f}  {Q:6.2f}      {dif(Q, Q35):+5.1f}   [I doc recalc {Idoc:.2f}; Q doc recalc {0.5*I35*(Am2/1e4)/360:.2f}]")
p(f"    P24 Gumbel TR 35 = {P35:.3f} mm ; TR 70 = {P70:.3f} mm")

# =========================================================================
p(""); p("="*78); p("CASO 5. UPAO La Jalca, estacion Chachapoyas (dos series)"); p("="*78)
TR5 = [2, 5, 10, 25, 50, 100, 175, 500]
ca_ = [D.CHACHA_A[a] for a in sorted(D.CHACHA_A)]; cb_ = [D.CHACHA_B[a] for a in sorted(D.CHACHA_B)]
r5a, r5b = ajustes(ca_, TR5), ajustes(cb_, TR5); RES["upao"] = {"serie_A": r5a, "serie_B": r5b}
muestra("serie A, Cuadro 18 (1964-73, 1995-2001), 17 años", r5a, TR5)
ia = D.CHACHA_A_IMPRESO
for k, col_ in (("normal", "normal"), ("lognormal_2p", "lognormal"), ("gumbel", "gumbel")):
    p(f"    {k}: D {r5a[k]['D']:.4f} vs impreso {ia[col_][0]}; P: " + "  ".join(f"{T}: {r5a[k]['P'][T]:.2f}/{v}" for T, v in ia[col_][1].items()))
p(f"    critico impreso 0.3298 = 1.36/raiz(17) = {1.36/math.sqrt(17):.4f}; exacto: {r5a['d']:.4f}")
muestra("serie B, tabla Gumbel (1965-73, 2004-11), 17 años", r5b, TR5)
ib = D.CHACHA_B_IMPRESO
p(f"    suma {sum(cb_):.1f} vs {ib['suma']}; SC {sum((x-st.fmean(cb_))**2 for x in cb_):.1f} vs {ib['sc']}; media {r5b['media']:.2f} vs {ib['media']}; s {r5b['s']:.2f} vs {ib['s']}; "
  f"1/alfa {1/r5b['gumbel']['alfa']:.3f} vs {ib['alfa']}; beta {r5b['gumbel']['beta']:.3f} vs u {ib['u']}")
p("    XT' impreso vs Gumbel momentos del Manual: " + "  ".join(f"{T}: {r5b['gumbel']['P'][T]:.4f}/{v} ({dif(r5b['gumbel']['P'][T], v):+.3f}%)" for T, v in ib["xt"].items()))
comunes = [a for a in D.CHACHA_A if a in D.CHACHA_B and D.CHACHA_A[a] != D.CHACHA_B[a]]
p(f"    años comunes con valor distinto entre las dos series: {[(a, D.CHACHA_A[a], D.CHACHA_B[a]) for a in comunes]}")
u = D.UPAO_ALC19
p(f"  -- alcantarilla 19: Kirpich impreso con exponente 0.76: {kirpich_min(u['L_m'], u['S'], 0.76):.2f} min (impreso {u['tc_min']}); con 0.77 (Manual): {kirpich_min(u['L_m'], u['S']):.2f} min")
I19 = u["K"]*u["TR"]**u["m"]/u["tc_min"]**u["n"]
p(f"     I = {I19:.3f} (impreso {u['I']}); Q = 0.278·0.35·I·1.25 = {0.278*0.35*u['I']*1.25:.3f} (impreso {u['Q']}); pendiente 0.211 fuera de 3-10 %")
tK = kirpich_min(u["L_m"], u["S"]); P50 = r5b["gumbel"]["P"][50]
p(f"     MH (Gumbel serie B, f = 1.00, Dick-Peschke en tc Kirpich 0.77 = {tK:.2f} min): P24(50) = {P50:.2f}; I = {I_dp(P50, tK):.2f} mm/h; Q/C = {0.278*I_dp(P50, tK)*1.25:.3f}")
RES["upao"]["alc19"] = dict(kirpich_076=kirpich_min(u['L_m'], u['S'], 0.76), kirpich_077=tK, I_dp=I_dp(P50, tK))

# =========================================================================
p(""); p("="*78); p("CASO 6. ESPOL Intervalles (Ecuador): cuatro series INAMHI, solo K-S"); p("="*78)
es = D.espol_series(); RES["espol"] = {}
for nombre, serie in es.items():
    v = [serie[a] for a in sorted(serie)]
    r = ajustes(v, [25, 50, 100]); RES["espol"][nombre] = r
    h = D.ESPOL_DMAX[nombre]
    p(f"  {nombre}: n = {r['n']} (impreso {D.ESPOL_N[nombre]}), media {r['media']:.2f}, s {r['s']:.2f}, d = {r['d']:.4f}")
    for k, kh in (("normal", "normal"), ("lognormal_2p", "lognormal"), ("gumbel", "gumbel")):
        p(f"     {k}: D ec.13 = {r[k]['D']:.4f}; D de escalon = {r[k]['Dcl']:.4f}; Hydrognomon = {h[kh]}; P25/50/100 = {r[k]['P'][25]:.1f}/{r[k]['P'][50]:.1f}/{r[k]['P'][100]:.1f}")


# =========================================================================
# PARTE 2. Complementos y SALIDA ESPERADA de las entradas preparadas
# =========================================================================
p(""); p("="*78); p("COMPLEMENTOS"); p("="*78)
p("  -- UPeU: Temez con la pendiente de la MICROCUENCA (S) en vez de la del cauce (s) --")
p("   id   Tc_h(S)  K(S)   I(34) con S   I_imp   dif%")
RES["upeu"]["paso_con_S_cuenca"] = {}
for i, (Kimp, Iimp, Aha, Cimp, Qimp) in D.UPEU_T8.items():
    t = D.UPEU_T6[i]; Tc = tc_temez_h(t["L"], t["S"]); I = I_34(KA(t["A"])*Pd, Tc)
    RES["upeu"]["paso_con_S_cuenca"][i] = dict(Tc_h=Tc, K=K_unif(Tc), I34=I)
    p(f"   {i:>2}  {Tc:6.3f}  {K_unif(Tc):5.3f}  {I:6.2f}        {Iimp:6.2f}  {dif(I, Iimp):+5.2f}")
p("  -- Tumbes: cuencas de 10 km2 o mas, racional modificado del Manual con el CN de la Tabla 67 --")
TUMBES_CN = {"C-6": (62, 1326.75, 1827.93), "C-7": (70, 252.71, 345.23), "C-13": (62, 269.05, 372.98),
             "C-16": (70, 392.15, 534.64), "C-17": (62, 247.81, 345.99)}   # N, Q35, Q70 (Tabla 67, p. 93)
RES["tumbes"]["mayores"] = {}
for c, (cn, q35, q70) in TUMBES_CN.items():
    v = tc_[c]; Tc = RES["tumbes"]["cuencas"][c]["Tc_h_S_cotas"]; K = K_unif(Tc); ka = KA(v["A"])
    fila = {}
    for T in (35, 70):
        PdT = r3["lognormal_2p"]["P"][T]; I = I_34(ka*PdT, Tc); C = C_35(PdT, cn)
        fila[T] = dict(Pd=PdT, P=ka*PdT, I34=I, Po=Po(cn), C=C, Q=0.278*C*I*v["A"]*K)
    RES["tumbes"]["mayores"][c] = dict(A=v["A"], CN=cn, Tc_h=Tc, K=K, KA=ka, por_TR=fila)
    p(f"   {c}: A {v['A']} km2, CN {cn}, Tc {Tc:.3f} h, K {K:.4f}, KA {ka:.4f}; TR35: I {fila[35]['I34']:.1f}, C {fila[35]['C']:.3f}, Q {fila[35]['Q']:.1f} (doc HU {q35}); "
      f"TR70: I {fila[70]['I34']:.1f}, C {fila[70]['C']:.3f}, Q {fila[70]['Q']:.1f} (doc HU {q70})")

# ------------------------------------------------------------------ entradas
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAB_E = "estacion,anio,p24_mm,fen\n"
CAB_C = "id,area_km2,L_cauce_m,S_cauce_cuenca,S_terreno,cobertura,suelo,estacion,metodo_tc,H_desnivel_m,ajuste_kirpich,CN\n"
def escribe(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "w", encoding="utf-8", newline="\n").write(texto)
def com(*lineas): return "".join("# " + l + "\n" for l in lineas)
def serie_csv(nombre, serie, fen=(), fen_vacio=False):
    return "".join(f"{nombre},{a},{serie[a]:g},{'' if fen_vacio else ('si' if a in fen else 'no')}\n" for a in sorted(serie))
ESP = {}

def esperado_P(valores, TRs):
    r = ajustes(valores, TRs)
    return {k: (dict(D=r[k]["D"], P_TR_mm={str(T): r[k]["P"][T] for T in TRs},
                     parametros={x: r[k][x] for x in ("Y", "Sy", "alfa", "beta") if x in r[k]})
                if k in r else None) for k in ("normal", "lognormal_2p", "gumbel")} | {
            "n": r["n"], "media": r["media"], "s": r["s"], "d_critico_0.05": r["d"], "d_origen": r["d_origen"],
            "mejor_ajuste_ks": r["mejor"]}

def racional(P24, A, L_km, S, C, metodo="temez"):
    if metodo == "temez":
        Tc = tc_temez_h(L_km, S)
        if not 0.25 <= Tc <= 24:
            return dict(excepcion="MetodoNoEvaluableError", motivo=f"Temez Tc = {Tc:.3f} h fuera de 0.25-24 h", Tc_h=Tc)
        tc = Tc*60; K = K_unif(Tc)
    else:
        tc = kirpich_min(L_km*1000, S); K = 1.0
    d = max(tc, 5.0); Pdd = P24*(d/1440)**0.25; I = Pdd/(d/60)
    return dict(metodo="racional (ec. 28)", tc_min=tc, duracion_min=d, Pd_mm=Pdd, I_mm_h=I, C=C, K=K, Q_m3s=0.278*C*I*A*K,
                Q_sin_K_m3s=0.278*C*I*A)
def modificado(Pd_, A, L_km, S, CN):
    Tc = tc_temez_h(L_km, S); K = K_unif(Tc); ka = KA(A); I = I_34(ka*Pd_, Tc); C = C_35(Pd_, CN)
    return dict(metodo="racional modificado (ec. 29-35)", Tc_h=Tc, K=K, KA=ka, P_mm=ka*Pd_, I_mm_h=I, Po_mm=Po(CN), C=C,
                Q_m3s=0.278*C*I*A*K)

# ---- Caso 1 Piura
ROT = "DATOS DE CASO REAL PUBLICADO. "
escribe(f"{RAIZ}/indeci_piura/estacion.csv", com(
    ROT + "INDECI-OEA, «Mapa de peligros de la ciudad de Piura», jun. 2009.",
    "Serie: Vol. I, Cuadro N 13 (PDF 105, pag. impresa 89), columna ANUAL, estacion Miraflores 1971-2008;",
    "identica a la lista del Anexo 07.2 del Vol. II (PDF 346). Fuente de la serie: Proyecto Especial Chira-Piura.",
    "Columna fen: los seis años que el Anexo 07.1 (Vol. II PDF 338) quita de la serie «sin FEN» (1972, 1973, 1983,",
    "1987, 1992, 1998; el estudio escribe «72/73, 83, 87, 92, 98», Vol. I PDF 126, imp. 110). Es la declaracion DEL ESTUDIO.",
    "1971 es año parcial (Cuadro 13 trae solo abril-diciembre): entra como lo usa el estudio.") + CAB_E
    + serie_csv("Miraflores", D.PIURA, D.PIURA_FEN_ESTUDIO))
escribe(f"{RAIZ}/indeci_piura/estacion_fen_5_sin_1973.csv", com(
    ROT + "Variante: columna fen con los CINCO años del Anexo 07.3 «solo FEN» (Vol. II PDF 354): 1973 queda «no».",
    "Sirve para medir la sensibilidad a la declaracion; la serie es la misma.") + CAB_E
    + serie_csv("Miraflores", D.PIURA, D.PIURA_SOLO_FEN))
TRP = [25, 50, 100]
ESP["indeci_piura"] = {
  "entrada": "indeci_piura/estacion.csv", "funcion": "MH.precipitacion_de_diseno(serie, TR)", "TR": TRP,
  "serie_completa": esperado_P(completa, TRP), "serie_sin_fen__ajuste_que_se_reporta_como_contraste": esperado_P(sin_fen, TRP),
  "serie_sin_fen": {"excepcion": "MetodoNoEvaluableError", "motivo": "da menos lluvia que la serie completa (regla del mas conservador)"},
  "dos_poblaciones": {"excepcion": "MetodoNoEvaluableError"},
  "sin_declarar_homogeneidad_serie_fen": {"excepcion": "CriterioPendienteError"},
  "serie_completa + distribucion=normal": {"excepcion": "MetodoNoEvaluableError", "motivo": "D >= d"},
  "serie_completa + distribucion=gumbel": {"excepcion": "MetodoNoEvaluableError", "motivo": "D >= d (0.2219 vs 0.2154)"},
  "aviso_lo_observado": {"TR25": "P24 = 131.8 mm < 151.4 mm (1983, T empirico 19.5 años): aviso, no detiene", "TR50": "cubre 173.6 (1998)"},
  "variante_fen_5": esperado_P([D.PIURA[a] for a in sorted(D.PIURA) if a not in D.PIURA_SOLO_FEN], TRP)}

# ---- Caso 2 UPeU
filas = ""
ESP["upeu_colpahuayco"] = {"TR": [35, 70], "estacion": esperado_P(sic, [35, 70]), "cuencas": {}}
C_VEH = 0.30
for i in range(1, 15):
    t = D.UPEU_T6[i]; cn = ""
    filas += f"MC-{i:02d},{t['A']:g},{t['L']*1000:g},{t['s']:g},{t['S']:g},pastos_vegetacion_ligera,permeable,Sicuani,temez,{t['Hmax']-t['hmin']:g},,{cn}\n"
    if t["A"] < 10:
        ESP["upeu_colpahuayco"]["cuencas"][f"MC-{i:02d}"] = {str(T): racional(r2["lognormal_2p"]["P"][T], t["A"], t["L"], t["s"], C_VEH) for T in (35, 70)}
    else:
        ESP["upeu_colpahuayco"]["cuencas"][f"MC-{i:02d}"] = {"excepcion": "DatoFaltanteError", "campo": "CN",
            "si_se_declarara_CN": {str(cn_): modificado(r2["lognormal_2p"]["P"][70], t["A"], t["L"], t["s"], cn_) for cn_ in (70, 75, 80)}}
escribe(f"{RAIZ}/upeu_colpahuayco/cuencas.csv", com(
    ROT + "Huaman Guerra y Marrujo Carpio (UPeU, 2023), carretera Colpahuayco-Langui, doc.pdf.",
    "area_km2, L_cauce_m (L km x 1000), S_cauce_cuenca (fila «s», pendiente del cauce principal), S_terreno (fila «S»,",
    "pendiente de la microcuenca) y H_desnivel_m (Hmax - hmin): Tabla 6, p. 18 (pagina impresa = PDF).",
    "NO PUBLICADO, y por eso VEHICULO DEL VERIFICADOR, no dato del caso: cobertura y suelo (el documento da C = 0.22 a 0.32",
    "sacado de un CN que no imprime; la Tabla N 08 no puede dar esos valores). Se pone pastos/permeable, que con «alta > 20 %»",
    "lee C = 0.30. El CN de MC-07 y MC-14 (>= 10 km2) no se publica: va VACIO a proposito.") + CAB_C + filas)
escribe(f"{RAIZ}/upeu_colpahuayco/estacion.csv", com(
    ROT + "Tabla 2, p. 13: estacion automatica Sicuani (SENAMHI), 1993-2020, 28 años.",
    "Columna fen: el documento NO declara años FEN. «no» es DECLARACION DEL VERIFICADOR para que el archivo cargue;",
    "el programa tiene que avisar que la serie no declara ningun año FEN.") + CAB_E + serie_csv("Sicuani", D.SICUANI))

# ---- Caso 3 Tumbes
escribe(f"{RAIZ}/untumbes_tu107/estacion_como_se_publica_fen_vacio.csv", com(
    ROT + "Ramos Estrada (UNTumbes, 2025), TU-107 Bocapan-Tamarindo, tesis.pdf, Tabla 24, p. 61 (impresa = PDF).",
    "Estacion Cañaveral, 40 años (1983-87, 1989-2021, 2023-24). La tesis NO menciona El Niño: la columna fen va VACIA,",
    "que es lo que la publicacion declara. ESPERADO: la carga se detiene con DatoFaltanteError('fen').",
    "ADVERSARIAL: 2001 es copia de 1996 y 2002 es copia de 1989 (Tabla 23, p. 60, mes a mes).") + CAB_E
    + serie_csv("Cañaveral", ts, fen_vacio=True))
FEN_T = (1983, 1987, 1992, 1998)
escribe(f"{RAIZ}/untumbes_tu107/estacion_fen_declarado_por_el_verificador.csv", com(
    ROT + "Misma serie (Tabla 24, p. 61). Columna fen: DECLARACION DEL VERIFICADOR, no de la tesis: los años que el estudio",
    "INDECI-OEA de Piura nombra como FEN dentro del periodo (83, 87, 92, 98; Vol. I PDF 126, imp. 110).",
    "OJO: en esta serie el maximo (729.2 mm) esta en 1997 y no en 1998; declarar 1997 es otra variante (ver dossier).",
    "ADVERSARIAL: 2001 = 1996 y 2002 = 1989, copiados mes a mes; el programa hoy no lo detecta.") + CAB_E
    + serie_csv("Cañaveral", ts, FEN_T))
VEH = {0.10: ("bosques_densa_vegetacion", "permeable", 0.03), 0.15: ("bosques_densa_vegetacion", "permeable", 0.10),
       0.20: ("bosques_densa_vegetacion", "permeable", 0.30)}
filas = ""; ESP["untumbes_tu107"] = {"TR": [35, 70], "estacion_serie_completa": esperado_P(tv, [35, 70, 140]),
    "estacion_fen_vacio": {"excepcion": "DatoFaltanteError", "campo": "fen"}, "cuencas": {}}
sin_fen_t = [ts[a] for a in sorted(ts) if a not in FEN_T]
ESP["untumbes_tu107"]["contraste_sin_fen_verificador"] = esperado_P(sin_fen_t, [35, 70, 140])
for c, v in tc_.items():
    Sx = round((v["zmax"] - v["zmin"])/(v["L"]*1000), 4); H = v["zmax"] - v["zmin"]
    if c in TUMBES_CN:
        cn = TUMBES_CN[c][0]; cob, suelo, St = VEH[0.10]
        ESP["untumbes_tu107"]["cuencas"][c] = {str(T): modificado(r3["lognormal_2p"]["P"][T], v["A"], v["L"], Sx, cn) for T in (35, 70)}
    else:
        cn = ""; C = tq[c][2]; cob, suelo, St = VEH[C]
        ESP["untumbes_tu107"]["cuencas"][c] = {str(T): racional(r3["lognormal_2p"]["P"][T], v["A"], v["L"], Sx, C) for T in (35, 70)}
        if "excepcion" in ESP["untumbes_tu107"]["cuencas"][c]["35"]:
            ESP["untumbes_tu107"]["cuencas"][c] = ESP["untumbes_tu107"]["cuencas"][c]["35"]
    filas += f"{c},{v['A']:g},{v['L']*1000:g},{Sx:g},{St:g},{cob},{suelo},Cañaveral,temez,{H:g},,{cn}\n"
escribe(f"{RAIZ}/untumbes_tu107/cuencas.csv", com(
    ROT + "Ramos Estrada (UNTumbes, 2025), tesis.pdf, Tabla 26, p. 64: area, longitud de cauce y cotas maxima y minima.",
    "S_cauce_cuenca = (cota max - cota min) / L, a 4 decimales: la tabla la imprime a 2 y la columna TEMEZ de la Tabla 27",
    "(p. 65) solo se reproduce con la no redondeada. H_desnivel_m = cota max - cota min. CN: columna «N» de la Tabla 67 (p. 93),",
    "solo en las cinco cuencas de 10 km2 o mas.",
    "NO PUBLICADO, VEHICULO DEL VERIFICADOR: cobertura, suelo y S_terreno. La tesis da C = 0.10, 0.15 o 0.20 por cuenca",
    "(Tabla 66, p. 92) sin decir de que fila; se pone bosques/permeable con S_terreno 0.03, 0.10 o 0.30 para que la",
    "Tabla N 08 lea ese mismo C (suave 0.10, media 0.15, alta 0.20). S_terreno NO es un dato del caso.") + CAB_C + filas)

# ---- Caso 4 UNSAAC
filas = ""; ESP["unsaac_42tmc"] = {"TR": [35, 70], "estacion": esperado_P(col, [35, 70]), "cuencas_con_distribucion_gumbel": {},
    "dick_peschke_tabla_6_8": "I = P24 (d/1440)^0.25/(d/60): 48 celdas, desvio maximo 0.013 mm/h con la P24 impresa a 2 decimales"}
for c, t in D.UNSAAC.items():
    A = t[0]/1e6
    filas += f"{c},{A:.6f},{t[1]:g},{t[2]/100:.4f},0.30,pastos_vegetacion_ligera,semipermeable,Colquepata,temez,,,\n"
    e35 = racional(P35, A, t[1]/1000, t[2]/100, 0.5); e70 = racional(P70, A, t[1]/1000, t[2]/100, 0.5)
    ESP["unsaac_42tmc"]["cuencas_con_distribucion_gumbel"][c] = e35 if "excepcion" in e35 else {"35": e35, "70": e70}
escribe(f"{RAIZ}/unsaac_42tmc/cuencas.csv", com(
    ROT + "Bermejo Colque y Cruz Huaman (UNSAAC, 2019), camino vecinal Emp. CU112-Roquepata, tesis.pdf.",
    "area_km2 (m2 / 1e6), L_cauce_m y S_cauce_cuenca (%, Taylor-Schwarz / 100): Tablas 6.4 y 6.5, PDF 98-100 (imp. 86-88).",
    "NO PUBLICADO, VEHICULO DEL VERIFICADOR: cobertura, suelo y S_terreno. La tesis usa C = 0.5 unico (Tabla 6.13, PDF 111,",
    "imp. 99) sin fila; pastos/semipermeable con S_terreno = 0.30 («alta > 20 %») lee C = 0.50 en la Tabla N 08.") + CAB_C + filas)
escribe(f"{RAIZ}/unsaac_42tmc/estacion.csv", com(
    ROT + "Tabla 6.6, PDF 101 (imp. 89): estacion Colquepata (SENAMHI), 1990-2014, 25 años.",
    "Columna fen: la tesis NO declara años FEN; «no» es DECLARACION DEL VERIFICADOR.",
    "ADVERTENCIA: serie inhomogenea (1990-1997: 4.4 a 9.3 mm; 1998-2014: 20.1 a 48.2 mm).") + CAB_E + serie_csv("Colquepata", D.COLQUEPATA))

# ---- Caso 5 UPAO
escribe(f"{RAIZ}/upao_la_jalca/estacion.csv", com(
    ROT + "Campos Muñoz e Inga Yopan (UPAO, 2016), La Jalca-Nueva Esperanza, tesis.pdf. Estacion Chachapoyas, DOS series:",
    "«Chachapoyas-A»: Cuadro N 18, PDF 91-92 (imp. 71-72), 1964-73 y 1995-2001 (la de los Cuadros 19 y 20).",
    "«Chachapoyas-B»: tabla mensual y tabla Gumbel, PDF 113-114 (imp. 93-94), 1965-73 y 2004-11 (la de las curvas IDF).",
    "1973 vale 25.5 en la A y 27.0 en la B. Columna fen: la tesis no declara años FEN; «no» es DECLARACION DEL VERIFICADOR.") + CAB_E
    + serie_csv("Chachapoyas-A", D.CHACHA_A) + serie_csv("Chachapoyas-B", D.CHACHA_B))
escribe(f"{RAIZ}/upao_la_jalca/cuencas.csv", com(
    ROT + "Alcantarilla N 19, PDF 138-140 (imp. 118-120): A = 1.25 km2 (1252631.84 m2), L = 2415.58 m, S = 0.211, Kirpich.",
    "NO PUBLICADO, VEHICULO DEL VERIFICADOR: cobertura, suelo y S_terreno (la tesis usa C = 0.35 sin fila;",
    "bosques/semipermeable con S_terreno = 0.10, «media > 5 %», lee 0.35). Estacion: la serie B, que es la de sus IDF.") + CAB_C
    + "ALC-19,1.25,2415.58,0.211,0.10,bosques_densa_vegetacion,semipermeable,Chachapoyas-B,kirpich,,ninguno,\n")
ESP["upao_la_jalca"] = {"Chachapoyas-A": esperado_P(ca_, [10, 50, 100, 175, 500]), "Chachapoyas-B": esperado_P(cb_, [2, 5, 10, 25, 50, 100, 500]),
    "ALC-19": {"por_omision": {"excepcion": "MetodoNoEvaluableError", "motivo": "Kirpich con S = 21.1 %, fuera de 3-10 %"},
               "con tc_fuera_de_la_poblacion_del_metodo=indicador_con_aviso, TR 50": racional(r5b["gumbel"]["P"][50], 1.25, 2.41558, 0.211, 0.35, "kirpich")}}

# ---- Caso 6 ESPOL
texto = com(ROT + "Luna Chalan (ESPOL, 2023), via Intervalles (Loja, Ecuador), tesis.pdf, Anexo 2, PDF 94-96 (imp. 89-91).",
    "Cuatro estaciones INAMHI: La Argelia M033, Gonzanama M149, Malacatos M143, Catamayo M060; 1964-2013.",
    "Columna fen: no aplica al estudio (Ecuador, sierra de Loja); «no» es DECLARACION DEL VERIFICADOR.") + CAB_E
ESP["espol_intervalles"] = {}
for nombre, serie in es.items():
    texto += serie_csv(nombre, serie)
    ESP["espol_intervalles"][nombre] = esperado_P([serie[a] for a in sorted(serie)], [25, 50, 100])
escribe(f"{RAIZ}/espol_intervalles/estacion.csv", texto)

for caso, e in ESP.items():
    json.dump(e, open(f"{RAIZ}/{caso}/salida_esperada.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

base = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(base, "resultados_a_mano.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
json.dump(RES, open(os.path.join(base, "resultados_a_mano.json"), "w", encoding="utf-8"), indent=1, sort_keys=True, default=str)
print("\n".join(OUT))
