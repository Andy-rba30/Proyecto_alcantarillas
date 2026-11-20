from tests.apoyo import validacion_integral as V
import cli, json
for fondo, extra in (("36.284", ()), ("36.284", (("declarar","origen_cota_fondo_entrada","cota_fondo_entrada"),)), ("36.326", (("externo","C-01","S_conducto",0.006),))):
    cambios = (("celda","C-01","cota_fondo_entrada",fondo),) + extra
    try:
        inf = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
    except Exception as e:
        print(fondo, extra, "EXC", type(e).__name__, " ".join(str(e).split())[:400]); continue
    vol = cli.informe_json(inf)
    p = next(x for x in vol["puntos"] if x["id"] == "C-01")
    print("=== fondo", fondo, extra, "dim:", p["dimensionado"], (p.get("diseno") or {}).get("seccion"), "HW", (p.get("diseno") or {}).get("HW_gobernante_m"), (p.get("diseno") or {}).get("control_gobernante"))
    print("   no cumple:", {v["codigo"]: v["estado"] for v in p.get("verificaciones") or [] if v["estado"] not in ("cumple","no aplica") and not v["codigo"].startswith(("E","A"))})
    for b in p.get("bloqueos") or []:
        if b["tipo"] != "DiferidoPorAlcance": print("   BLOQ", b["tipo"], b["etapa"], " ".join(b["mensaje"].split())[:700])
    for it in p.get("iteraciones") or []:
        print("    it", it.get("seccion"), it.get("incumplidas"), (it.get("motivo") or "")[:160])
    print("   avisos:", [a[:230] for a in p["avisos"] if "emanso" in a or "VC2" in a or "fondo" in a][:5])
    geo = p.get("geometria") or {}
    print("   geo:", {k: geo.get(k) for k in ("cota_entrada_msnm","cota_salida_msnm","longitud_m")})
