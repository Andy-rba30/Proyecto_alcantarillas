"""Funciones de recalculo a mano (independientes de la app): seccion circular, Manning,
critico y control de entrada de HDS-5 3a ed. (Apendice A), en unidades inglesas (Ku = 1)."""
import math
from scipy.optimize import brentq
G_FT = 32.174
def geo(y, D):
    th = 2 * math.acos(1 - 2 * y / D)
    A = D**2 / 8 * (th - math.sin(th)); P = th * D / 2; T = D * math.sin(th / 2)
    return A, P, T
def q_manning_ft(y, D, n, S):
    A, P, _ = geo(y, D); return 1.486 / n * A * (A / P)**(2/3) * S**0.5
def yn_ft(Q, D, n, S):
    ymax = 0.938 * D
    if q_manning_ft(ymax, D, n, S) < Q: raise ValueError('sin tirante normal (Q > Q pico de la seccion parcial)')
    return brentq(lambda y: q_manning_ft(y, D, n, S) - Q, 1e-6, ymax)
def yc_ft(Q, D): return brentq(lambda y: geo(y, D)[0]**3 / geo(y, D)[2] - Q**2 / G_FT, 1e-6, 0.99999 * D)
def q_critico_ft(y, D): A, _, T = geo(y, D); return math.sqrt(A**3 / T * G_FT)
def _hw_u(Q, D, S, K, M, Ks):
    A = math.pi * D**2 / 4; q = Q / (A * D**0.5)
    dc = yc_ft(Q, D); Ac, _, _ = geo(dc, D); Hc = dc + (Q / Ac)**2 / (2 * G_FT)
    return D * (Hc / D + K * q**M + Ks * S)
def _hw_s(Q, D, S, c, Y, Ks):
    A = math.pi * D**2 / 4; q = Q / (A * D**0.5); return D * (c * q**2 + Y + Ks * S)
def hw_entrada_ft(Q, D, S, K=0.0098, M=2.0, c=0.0398, Y=0.67, Ks=-0.5):
    """Concreto, borde cuadrado con muro (Carta 1, escala 1). Transicion 3.5 < q* < 4.0: lineal
    entre la no sumergida en q* = 3.5 y la sumergida en q* = 4.0."""
    A = math.pi * D**2 / 4; q = Q / (A * D**0.5)
    if q <= 3.5: return _hw_u(Q, D, S, K, M, Ks), 'no sumergido (Forma 1)'
    if q >= 4.0: return _hw_s(Q, D, S, c, Y, Ks), 'sumergido'
    Q1, Q2 = 3.5 * A * D**0.5, 4.0 * A * D**0.5
    h1, h2 = _hw_u(Q1, D, S, K, M, Ks), _hw_s(Q2, D, S, c, Y, Ks)
    return h1 + (h2 - h1) * (Q - Q1) / (Q2 - Q1), 'transicion (interpolacion lineal)'
