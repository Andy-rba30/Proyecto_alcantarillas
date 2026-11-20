import sys, time
from tests.apoyo import sensibilidad as S
from tests.fixtures import juego_validacion_integral as J
from src import criterios_adoptados as ca
ya = {b.clave for b in S.BARRIDOS}
res = {}
for clave, c in ca.CRITERIOS.items():
    if clave in ya: continue
    s = c.sensibilidad
    efectivo = J.DECLARACIONES.get(clave, c.valor)
    vals = None
    if c.forma == "categoria" and isinstance(s, tuple) and efectivo is not None:
        vals = (efectivo,) + tuple(v for v in s if v != efectivo)
    elif c.forma in ("float", "int") and isinstance(s, tuple) and len(s) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in s) and efectivo is not None:
        vals = tuple(dict.fromkeys((efectivo, type(efectivo)(s[0]), type(efectivo)(s[1]))))
    if vals is None or len(vals) < 2:
        res[clave] = ("NO-BARRIBLE-AUTO", c.forma, str(s)[:60]); continue
    try:
        m = S.medir(S.Barrido(clave, "x", "aud", valores=vals))
    except Exception as e:
        res[clave] = ("EXC", type(e).__name__, " ".join(str(e).split())[:300]); print("###", clave, res[clave]); sys.stdout.flush(); continue
    mov = m.movimientos()
    res[clave] = (m.efecto, vals)
    print("###", clave, f"[{c.etiqueta}] {c.nivel}", vals, "→", m.efecto if m.leido else "NO LEIDO")
    for k in ("diseno", "veredictos", "hw"):
        if mov[k]: print("     ", k, mov[k][:8])
    sys.stdout.flush()
print("=== NO BARRIBLES AUTO:", [k for k, v in res.items() if v[0] == "NO-BARRIBLE-AUTO"])
