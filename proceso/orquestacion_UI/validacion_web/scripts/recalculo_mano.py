"""Recalculo independiente (sin importar la app) para sostener las clasificaciones.
Unidades inglesas donde la fuente las usa; SI donde la fuente es peruana."""
import math, json
from scipy.optimize import brentq
G_FT = 32.174
def geo(y, D):
    th = 2 * math.acos(1 - 2 * y / D)
    A = D**2 / 8 * (th - math.sin(th)); P = th * D / 2; T = D * math.sin(th / 2)
    return A, P, T
def q_manning_ft(y, D, n, S):
    A, P, _ = geo(y, D); return 1.486 / n * A * (A / P)**(2/3) * S**0.5
def yn_ft(Q, D, n, S): return brentq(lambda y: q_manning_ft(y, D, n, S) - Q, 1e-6, 0.938 * D)
def yc_ft(Q, D): return brentq(lambda y: geo(y, D)[0]**3 / geo(y, D)[2] - Q**2 / G_FT, 1e-6, 0.9999 * D)
def q_critico_ft(y, D): A, _, T = geo(y, D); return math.sqrt(A**3 / T * G_FT)
def hw_entrada_ft(Q, D, S, K=0.0098, M=2.0, c=0.0398, Y=0.67, Ks=-0.5):
    A = math.pi * D**2 / 4; q = Q / (A * D**0.5)
    if q <= 3.5:
        dc = yc_ft(Q, D); Ac, _, _ = geo(dc, D); Hc = dc + (Q / Ac)**2 / (2 * G_FT)
        return D * (Hc / D + K * q**M + Ks * S), 'no sumergido (Forma 1)'
    if q >= 4.0:
        return D * (c * q**2 + Y + Ks * S), 'sumergido'
    return None, 'transicion'
r = {}
D = 3.0
r['EX2_Q25_HW_entrada_HDS5_ft'] = hw_entrada_ft(25, D, 0.005)
r['EX2_Q2.5_yn_n0.013_ft'] = yn_ft(2.5, D, 0.013, 0.005)
r['EX2_Q2.5_yc_exacto_ft'] = yc_ft(2.5, D)
r['EX2_Q2.5_Q_que_da_yn_HY8_0.444_ft'] = q_manning_ft(0.444, D, 0.013, 0.005)
r['EX2_Q2.5_Q_que_da_yc_HY8_0.470_ft'] = q_critico_ft(0.470, D)
r['EX2_Q25_yn_ft'] = yn_ft(25, D, 0.013, 0.005); r['EX2_Q25_yc_ft'] = yc_ft(25, D)
# EX1: perdidas con n real y L real (HDS-5 3a ed.) frente al nomograma con L ajustada
A = math.pi * D**2 / 4; V = 25 / A; R = D / 4
H = (1 + 0.5 + 29.0 * 0.013**2 * 110 / R**(4/3)) * V**2 / (2 * G_FT)   # 29 n^2 L / R^1.33 (ingles)
dc = yc_ft(25, D); ho = max(1.8, (dc + D) / 2)
r['EX1_H_ft'] = H; r['EX1_ho_ft'] = ho; r['EX1_HWo_ft'] = H + ho - 0.005 * 110
r['EX1_V_salida_normal_ft_s'] = 25 / geo(yn_ft(25, D, 0.013, 0.005), D)[0]
# EX4
r['EX4_Q69.2_HW_entrada_ft'] = hw_entrada_ft(69.2, D, 0.03)
r['EX4_Q90_yc_exacto_ft'] = yc_ft(90, D)
r['EX4_Q90_yn_n0.012_ft'] = yn_ft(90, D, 0.012, 0.03); r['EX4_Q90_yn_n0.013_ft'] = yn_ft(90, D, 0.013, 0.03)
r['EX4_Q90_V_normal_n0.013_ft_s'] = 90 / geo(r['EX4_Q90_yn_n0.013_ft'], D)[0]
r['EX4_Q90_V_a_2.072ft_HY8_ft_s'] = 90 / geo(2.072, D)[0]
# Gumbel UPAO (momentos, Manual 3.7.1.7)
serie = [29.5,44.3,37.4,45.0,36.0,30.0,28.0,47.0,27.0,31.5,30.5,44.5,33.9,41.4,53.9,35.1,30.7]
n = len(serie); mu = sum(serie)/n; s = math.sqrt(sum((x-mu)**2 for x in serie)/(n-1))
alfa_inv = s / 1.2825; beta = mu - 0.45 * s
r['UPAO_media'] = mu; r['UPAO_s'] = s; r['UPAO_alfa(escala)_mm'] = alfa_inv; r['UPAO_beta(u)_mm'] = beta
for T in (2, 5, 10, 25, 50, 71, 100, 500):
    r[f'UPAO_XT_{T}'] = beta - math.log(-math.log(1 - 1/T)) * alfa_inv
# Temez y Kirpich
temez = lambda L_km, S: 0.3 * (L_km / S**0.25)**0.76
kirpich = lambda L_m, S: 0.01947 * L_m**0.77 * S**-0.385
r['UPAO_Tinas_Tc_temez_h'] = temez(14.73917, 0.0602)
r['UPAO_Tinas_K'] = 1 + r['UPAO_Tinas_Tc_temez_h']**1.25 / (r['UPAO_Tinas_Tc_temez_h']**1.25 + 14)
r['UPAO_Tinas_Tc_kirpich_min'] = kirpich(14739.17, 0.0602)
r['UPAO_cuneta1_Tc_kirpich_min'] = kirpich(50, 0.08)
for nombre, L, S in (('Cajahuache', 5.76, 0.15), ('A1', 1.94, 0.27), ('A2', 1.58, 0.21)):
    r[f'UNC_{nombre}_Tc_temez_h'] = temez(L, S)
# Intensidad de Temez (Manual ec. 32-34) frente a Dick-Peschke (ec. 16) para Tinas
tc = r['UPAO_Tinas_Tc_temez_h']; A_km2 = 55.911
KA = 1 - math.log10(A_km2) / 15; P = 69.48 * KA
r['UPAO_Tinas_KA'] = KA; r['UPAO_Tinas_P_corregida'] = P
r['UPAO_Tinas_I_temez_ec34'] = P / 24 * 11**((28**0.1 - tc**0.1) / (28**0.1 - 1))
for P24, rot in ((r['UPAO_XT_100'], 'sin_1.13'), (69.48, 'con_1.13')):
    Pd = P24 * (tc * 60 / 1440)**0.25
    r[f'UPAO_Tinas_I_dick_peschke_{rot}'] = Pd / tc
Po = (5000 / 72 - 50); r['UPAO_Tinas_Po'] = Po
Pd = 69.48; r['UPAO_Tinas_C_ec35'] = (Pd - Po) * (Pd + 23 * Po) / (Pd + 11 * Po)**2
json.dump(r, open('/tmp/validacion_web/recalculo_mano.json', 'w'), indent=1)
for k, v in r.items(): print(f'{k:45s} {v}')
