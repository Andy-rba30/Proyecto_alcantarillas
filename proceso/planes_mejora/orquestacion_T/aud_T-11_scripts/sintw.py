import json
from tests.apoyo import validacion_integral as V
import cli
inf = V.correr_juego(V.aplicar(V.juego_completo(), (("externo","globales","TW_m",None),)))
vol = cli.informe_json(inf)
for p in vol["puntos"]:
    print("=====", p["id"], p["dimensionado"])
    for b in p.get("bloqueos", []):
        print("  BLOQ:", json.dumps(b, ensure_ascii=False)[:3000])
    for it in p.get("iteraciones", [])[:60]:
        print("   it:", {k: it[k] for k in it if k in ("material","seccion","D_m","incumplidas","motivo","cumple","etiqueta")})
    print("  avisos:", [a[:200] for a in p.get("avisos", [])][:6])
    print("  tw:", json.dumps(p.get("tw") or p.get("TW") or {}, ensure_ascii=False)[:800])
