import sys, math
sys.path.insert(0, "/home/user/wt/main")
from src.modulos import M9_cabezal as M9
from src.modelos import MetodoNoEvaluableError, DatoInvalidoError, LimiteNumericoError
def coulomb(phi, i, delta):
    p, b, d = map(math.radians, (phi, i, delta))
    G = (1 + math.sqrt(math.sin(p + d) * math.sin(p - b) / (math.cos(d) * math.cos(b)))) ** 2
    return math.cos(p) ** 2 / (G * math.cos(d))
def MO(phi, i, delta, kh, kv=0.0):
    # AASHTO A11.3.1-1 con muro vertical (beta=0)
    p, b, d = map(math.radians, (phi, i, delta)); th = math.atan2(kh, 1 - kv)
    num = math.cos(p - th) ** 2
    den = math.cos(th) * math.cos(d + th) * (1 + math.sqrt(math.sin(p + d) * math.sin(p - th - b) / (math.cos(d + th) * math.cos(b)))) ** 2
    return num / den
print("== 1. Coulomb, talud infinito (subida = inf)")
for phi, delta, talud, h, g in ((34, 22.78, 2.0, 2.5, 17.0), (30, 20, 3.0, 4.0, 19.0), (38, 0, 2.5, 1.7, 18.0)):
    i = math.degrees(math.atan(1 / talud))
    P, rho = M9.cuna_de_tanteo(h=h, subida=math.inf, talud=talud, phi_grados=phi, delta_grados=delta, gamma=g)
    Pc = 0.5 * coulomb(phi, i, delta) * g * h * h
    print(f"  phi {phi} delta {delta} talud {talud}: cuña {P:.6f} | Coulomb {Pc:.6f} | dif {P-Pc:+.2e} rho {rho:.3f}")
print("== 2. Mononobe-Okabe, relleno horizontal (subida = 0)")
for phi, delta, kh, kv, h, g in ((34, 22.78, 0.25, 0.0, 2.5, 17.0), (34, 22.78, 0.5, 0.0, 2.5, 17.0), (30, 20.1, 0.25, 0.0, 2.4, 18.0), (36, 12, 0.2, 0.1, 3.0, 19.0), (32, 0, 0.3, -0.0, 2.0, 18.0)):
    P, rho = M9.cuna_de_tanteo(h=h, subida=0.0, talud=2.0, phi_grados=phi, delta_grados=delta, gamma=g, k_h=kh, k_v=kv)
    Pm = 0.5 * MO(phi, 0, delta, kh, kv) * g * h * h * (1 - kv)
    print(f"  phi {phi} delta {delta} kh {kh} kv {kv}: cuña {P:.6f} | M-O {Pm:.6f} | dif {P-Pm:+.2e} rho {rho:.3f}")
print("== 2b. M-O con talud infinito y sismo")
for phi, delta, kh, talud in ((34, 22.78, 0.1, 3.0), (36, 20, 0.15, 4.0)):
    i = math.degrees(math.atan(1 / talud)); h=3.0; g=18.0
    P, rho = M9.cuna_de_tanteo(h=h, subida=math.inf, talud=talud, phi_grados=phi, delta_grados=delta, gamma=g, k_h=kh)
    print(f"  cuña {P:.6f} | M-O {0.5*MO(phi,i,delta,kh)*g*h*h:.6f}")
print("== 3. Oraculos A-01")
for nombre, h, zrel, rise_total, talon in (("entrada", 2.477625, 2.10, 0.80, 0.75525), ("salida", 3.325459, 2.786784, 0.913216, 1.077352)):
    rise = rise_total - min(talon / 2.0, rise_total)
    for kh in (0.0, 0.25, 0.5):
        try:
            P, rho = M9.cuna_de_tanteo(h=h, subida=rise, talud=2.0, phi_grados=34.0, delta_grados=22.78, gamma=17.0, k_h=kh)
            print(f"  {nombre} kh {kh}: P = {P:.3f} rho {rho:.2f}")
        except Exception as e:
            print(f"  {nombre} kh {kh}: {type(e).__name__}: {str(e)[:160]}")
print("== 4. Guardias")
casos = {
 "talud infinito mas empinado que phi": dict(h=2.0, subida=math.inf, talud=1.2, phi_grados=34.0, delta_grados=20.0, gamma=17.0),
 "talud infinito con sismo fuera de dominio (i > phi - psi)": dict(h=2.0, subida=math.inf, talud=2.0, phi_grados=34.0, delta_grados=20.0, gamma=17.0, k_h=0.25),
 "kh enorme, relleno quebrado": dict(h=2.0, subida=0.5, talud=2.0, phi_grados=34.0, delta_grados=20.0, gamma=17.0, k_h=0.9),
 "kh = 0.7 horizontal (phi < psi)": dict(h=2.0, subida=0.0, talud=2.0, phi_grados=34.0, delta_grados=20.0, gamma=17.0, k_h=0.7),
 "h = 0": dict(h=0.0, subida=0.0, talud=2.0, phi_grados=34.0, delta_grados=20.0, gamma=17.0),
 "delta > phi": dict(h=2.0, subida=0.0, talud=2.0, phi_grados=30.0, delta_grados=31.0, gamma=17.0),
 "k_v = 1": dict(h=2.0, subida=0.0, talud=2.0, phi_grados=30.0, delta_grados=20.0, gamma=17.0, k_v=1.0),
 "nan": dict(h=float('nan'), subida=0.0, talud=2.0, phi_grados=30.0, delta_grados=20.0, gamma=17.0),
 "subida negativa": dict(h=2.0, subida=-0.1, talud=2.0, phi_grados=30.0, delta_grados=20.0, gamma=17.0),
 "k_v negativo": dict(h=2.0, subida=0.0, talud=2.0, phi_grados=30.0, delta_grados=20.0, gamma=17.0, k_h=0.2, k_v=-0.1),
 "subida enorme finita, talud > phi": dict(h=2.0, subida=1e6, talud=1.2, phi_grados=34.0, delta_grados=20.0, gamma=17.0),
}
for n, kw in casos.items():
    try:
        r = M9.cuna_de_tanteo(**kw); print(f"  {n}: SIN ERROR -> {r}")
    except Exception as e:
        print(f"  {n}: {type(e).__name__}: {str(e)[:150]}")
