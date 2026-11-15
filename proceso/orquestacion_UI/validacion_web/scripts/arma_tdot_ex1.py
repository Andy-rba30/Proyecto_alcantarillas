"""TDOT Ejemplo 1 (a mano, nomogramas): mismo sitio que el Ej. 2, Q50 = 25 cfs,
TW = 1.8 ft DECLARADO (dato del ejemplo), L = 110 ft, S = 0.005, RCP 36 in,
n = 0.013, ke = 0.5 (square edge with headwall, Tabla 6A-6).
DATOS DE PRUEBA (no publicados): area_ha, cota_terreno, cota_subrasante, cbr,
esviaje, sucs, luz_m, y la rasante SUBIDA (la publicada, 345.32 ft, deja al
36 in fuera por V4/V7 de la app; ver TDOT_EX2/publicada)."""
import json, sys, csv
sys.path.insert(0, '/tmp/validacion_web/scripts')
from conv import ft, cfs
out, variante = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'base')
P = dict(base=dict(area_ha=50.0, terr=0.0, paq=0.15, cbr=10.0, sucs='SM', luz=3.0, extra=1.25),
         alt=dict(area_ha=500.0, terr=0.30, paq=0.30, cbr=4.0, sucs='GW', luz=5.0, extra=2.25))[variante]
inv_ent, inv_sal = ft(341.25), ft(340.70); ras = ft(345.32) + P['extra']
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
fila = dict(id='TDOT-EX1', progresiva_km='0+100', familia='A', Q_m3s=f"{cfs(25):.6f}", area_ha=P['area_ha'], S_cauce='0.005',
            cota_terreno=f"{inv_ent+P['terr']:.6f}", cota_rasante=f"{ras:.6f}", cota_subrasante=f"{ras-P['paq']:.6f}",
            cbr_subrasante=P['cbr'], esviaje_grados=0, ancho_plataforma=f"{ft(30):.6f}", cota_fondo_receptor=f"{inv_sal:.6f}",
            Q_receptor_m3s='', cota_TW='', sucs_fundacion=P['sucs'], NF_profundidad_m='', cota_fondo_entrada=f"{inv_ent:.6f}", cota_coronacion_canal='')
with open(f"{out}/puntos.csv", 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerow(fila)
json.dump({"globales": {"luz_m": P['luz'], "longitud_m": ft(110.0), "S_conducto": 0.005, "TW_m": ft(1.8),
           "acceso_mantenimiento_previsto": True}}, open(f"{out}/externos.json", 'w'), indent=1)
json.dump({"corredor_del_proyecto": {"valor": "VALIDACION TDOT Ej. 1 (DATOS DE PRUEBA)",
           "trazabilidad": "DATOS DE PRUEBA, NO DEL PROYECTO: rotulo del caso de validacion externa (TDOT cap. 6 Ej. 1)", "fecha": "2026-11-15"}},
          open(f"{out}/sitio.json", 'w'), indent=1)
