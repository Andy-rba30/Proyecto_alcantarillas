import sys, time, traceback
from tests.apoyo import sensibilidad as S
from src import criterios_adoptados as ca
casos = [
 ("v_max_concreto_eleccion", (3.0, 6.0)),
 ("regimen_v2b", ()),
 ("HW_D_max", ()),
 ("espesor_pared_cajon", (0.20, 0.25, 0.30)),
 ("duracion_caudal_pico_socavacion_min", ()),
 ("borde_libre_canal_m", (0.5, 0.3)),
 ("velocidad_minima_autolimpieza_m_s", (0.25, 0.6, 0.9)),
 ("cobertura_minima_cajon", (0.3048, 0.6)),
 ("pendiente_maxima_conducto", (0.1, 0.02)),
 ("pendiente_minima_conducto", (0.0, 0.005)),
 ("desnivel_minimo_entrega_m", (0.0, 0.3)),
 ("long_max_cuneta", (200.0, 250.0)),
 ("metodo_longitud_conducto", ()),
]
sel = sys.argv[1:]
for clave, valores in casos:
    if sel and clave not in sel: continue
    t = time.time()
    try:
        m = S.medir(S.Barrido(clave, "x", "aud", valores=valores))
    except Exception as e:
        print("###", clave, "EXC", type(e).__name__, str(e)[:500]); continue
    print("###", clave, m.valores, "leido=", m.leido, "efecto=", m.efecto, f"{time.time()-t:.0f}s")
    for k, v in m.movimientos().items():
        if v: print("    ", k, v[:12])
    for f in m.resultado.filas:
        print("      ", repr(f.valor)[:30], f.id_punto, S._diseno(f), f.HW_gobernante_m, list(f.verificaciones_que_cambian)[:8], list(f.incumplidas_en_la_progresion)[:6], "" if f.dimensionado else m.bloqueo(f.valor, f.id_punto))
    sys.stdout.flush()
