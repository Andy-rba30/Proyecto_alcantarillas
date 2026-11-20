import traceback
from tests.apoyo import validacion_integral as V
from src.modelos import ErrorProyecto
casos = {
 "NF=0": tuple(("celda", i, "NF_profundidad_m", "0.0") for i in ("A-01","A-02","B-01","C-01")),
 "NF=0.5": tuple(("celda", i, "NF_profundidad_m", "0.5") for i in ("A-01","A-02","B-01","C-01")),
 "NF=1.0": tuple(("celda", i, "NF_profundidad_m", "1.0") for i in ("A-01","A-02","B-01","C-01")),
 "TW=0": (("externo","globales","TW_m",0.0),),
 "TW=0.9": (("externo","globales","TW_m",0.9),),
 "luz=6.5": (("externo","globales","luz_m",6.5),),
 "Qext<Q": (("externo","A-01","Q_evento_extremo_m3s",0.5),),
 "Qext grande": (("externo","A-01","Q_evento_extremo_m3s",6.0),),
 "afectacion baja": (("externo","A-01","cota_afectacion_aguas_arriba_msnm",42.0),),
 "S_cuneta=0.1": (("externo","B-01","S_cuneta",0.1),),
 "inicio posterior": (("externo","B-01","inicio_tramo_cuneta_km",2.6),),
 "peralte+bombeo": (("externo","globales","peralte",0.04),),
 "phi=20 fundacion cohesivo": (("declarar","c_phi_fundacion",{"cohesivo": True, "c_kpa": 30.0, "phi_grados": 0.0, "gamma_kn_m3": 17.0}),),
 "dist borde 0.1": (("sitio","distancia_borde_calzada_al_trasdos_m",{"valor":0.1,"trazabilidad":"DATOS DE PRUEBA, NO DEL PROYECTO","fecha":"2026-11-13"}),),
 "perpendicular": (("sitio","orientacion_muro_respecto_al_trafico",{"valor":"perpendicular_al_trafico","trazabilidad":"DATOS DE PRUEBA, NO DEL PROYECTO","fecha":"2026-11-13"}),),
 "Q C-01 3.0": (("externo","C-01","Q_m3s",3.0),),
 "cat B": (("declarar","categoria_refuerzo_aashto","B"),),
 "clase_1": (("declarar","clase_exposicion_fisuracion_cabezal","clase_1"),),
 "sin hidrologia + caudal vacio": (("hidrologia", False), ("csv_caudal_vacio", ("A-01",))),
 "esviaje C01 lecho B01 cohesivo": (("externo","B-01","material_lecho_salida",{"tipo":"cohesivo","IP":8,"Sv_Pa":25000,"pasa_200_pct":60}),),
 "TR 100": (("declarar","TR_evento_extremo",100.0),),
}
for nombre, cambios in casos.items():
    try:
        inf = V.correr_juego(V.aplicar(V.juego_completo(), cambios))
        res = []
        for p in inf.puntos:
            try:
                bl = [V.clasificar(p.punto.id, b) for b in p.bloqueos]
                cl = ";".join(sorted({f"{b.tipo}:{b.que}" for b in bl if b.que != "VC1-01"}))
            except ValueError as e:
                cl = "SIN-CLASE: " + str(e)[:160]
            res.append(f"{p.punto.id}:{'D' if p.dimensionado else 'x'}{'['+cl+']' if cl else ''}")
        try:
            pb = [V.clasificar("proyecto", b).que for b in (inf.cabezal.bloqueos if inf.cabezal else ())]
        except ValueError as e:
            pb = ["SIN-CLASE " + str(e)[:120]]
        print(f"{nombre:32s}", " ".join(res), pb or "")
    except ErrorProyecto as e:
        print(f"{nombre:32s} ErrorProyecto fuera de etapa: {type(e).__name__}: {' '.join(str(e).split())[:200]}")
    except Exception as e:
        print(f"{nombre:32s} *** {type(e).__name__}: {' '.join(str(e).split())[:300]}")
        tb = traceback.format_exc().splitlines(); print("      ", " | ".join(tb[-6:-1])[:600])
