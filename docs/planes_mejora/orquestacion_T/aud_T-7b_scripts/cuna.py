import math
def coulomb(phi, i, delta):
    # AASHTO 3.11.5.3-1, theta = 90
    p, b, d = map(math.radians, (phi, i, delta))
    G = (1 + math.sqrt(math.sin(p + d) * math.sin(p - b) / (math.cos(d) * math.cos(b)))) ** 2
    return math.cos(p) ** 2 / (G * math.cos(d))
def cuña(h, rise, talud, phi, delta, gamma, kh=0.0):
    """Culmann sobre plano vertical de altura h; superficie sube 'rise' con 1V:talud H y luego horizontal. kh: seudoestatico (M-O por cuña)."""
    p, d = math.radians(phi), math.radians(delta)
    xq = rise * talud
    best = (0, None)
    for k in range(1, 8000):
        rho = math.radians(k * 90.0 / 8000)
        if rho <= p: continue
        t = math.tan(rho)
        # interseccion del plano de falla (desde base, y = x*t) con la superficie
        # tramo inclinado: y = h + x/talud, 0<=x<=xq ; horizontal: y = h + rise
        if t - 1 / talud > 0 and h / (t - 1 / talud) <= xq:
            x = h / (t - 1 / talud); 
            area = 0.5 * h * x   # triangulo (0,0),(0,h),(x, x t)
        else:
            x = (h + rise) / t
            # poligono (0,0),(0,h),(xq,h+rise),(x,h+rise)
            pts = [(0, 0), (x, h + rise), (xq, h + rise), (0, h)]
            area = 0.5 * abs(sum(pts[j][0] * pts[(j + 1) % 4][1] - pts[(j + 1) % 4][0] * pts[j][1] for j in range(4)))
        W = gamma * area
        psi = math.atan(kh)
        # equilibrio con inercia: W' = W/cos(psi) inclinado psi
        P = (W / math.cos(psi)) * math.sin(rho - p + psi) / math.cos(rho - p - d)
        if P > best[0]: best = (P, math.degrees(rho))
    return best
for nombre, h, zrel, rise_total, talon in (("entrada", 2.477625, 2.10, 0.80, 0.75525), ("salida", 3.325459, 2.786784, 0.913216, 1.077352)):
    talud, phi, delta, gamma = 2.0, 34.0, 22.78, 17.0
    rise_plano = rise_total - min(talon / talud, rise_total)
    i_eq = math.degrees(math.atan2(min(2 * zrel / talud, rise_total), 2 * zrel))
    PA_cod = 0.5 * coulomb(phi, i_eq, delta) * gamma * h ** 2
    P_cuña, rho = cuña(h, rise_plano, talud, phi, delta, gamma)
    P_h0 = 0.5 * coulomb(phi, 0, delta) * gamma * h ** 2
    P_inf = 0.5 * coulomb(phi, math.degrees(math.atan(1 / talud)), delta) * gamma * h ** 2
    print(nombre, "i_eq", round(i_eq, 3), "P_A codigo", round(PA_cod, 3), "| cuña real", round(P_cuña, 3), "rho", round(rho, 2), "| i=0:", round(P_h0, 3), "| talud entero:", round(P_inf, 3), "| codigo/cuña", round(PA_cod / P_cuña, 3))
    # sismico kh=0.25
    for kh in (0.25, 0.5):
        Pae, rho = cuña(h, rise_plano, talud, phi, delta, gamma, kh)
        print("   kh", kh, "P_AE cuña real", round(Pae, 3), "rho", round(rho, 2))
# chequeo: cuña con superficie horizontal reproduce Coulomb
print("chk", cuña(2.0, 0.0, 2.0, 34, 22.78, 17)[0], 0.5 * coulomb(34, 0, 22.78) * 17 * 4)
