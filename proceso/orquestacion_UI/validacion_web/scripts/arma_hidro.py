"""Cadena hidrologica UPAO (La Jalca) + Temez/C de UNC (Cocahuayco) por la app.
PUBLICADO: serie P24 de Chachapoyas (17 anios, UPAO p. 94), L, S, A, desnivel y CN de
Tinas (UPAO p. 267), L=50 m, S=0.08, A=0.0015 km2 de la cuneta 1 (UPAO pp. 107-108),
L, S, A de las tres cuencas UNC (Cajahuache, A1, A2) y su C: 'pendiente media, pastos
con vegetacion ligera, suelo semipermeable' (UNC p. 51).
DATOS DE PRUEBA (rotulados, no entran en lo comparado): la columna fen (la tesis no
declara anios FEN; con 'serie_completa' no entra al ajuste), S_terreno/cobertura/suelo
de Tinas y de la cuneta (la tesis usa CN, no la Tabla 08: el C de la app NO se compara
para esos puntos), S_terreno numerico de UNC dentro de la clase 'media' (>5 % y <=20 %),
y todo lo hidraulico del CSV de puntos (cotas, CBR, esviaje, TW, luz).
VARIANTE DE DIAGNOSTICO: TINAS-T-DIAG y TINAS-K-DIAG llevan AREA DE PRUEBA 9.5 km2 en
vez de 55.911 km2, solo para pasar la puerta del racional (A < 10 km2) y leer Tc, K,
P24 e I, que no dependen del area. Su C y su Q NO se comparan."""
import csv, json, sys
out, variante = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'base')
alt = variante == 'alt'
serie = {1965: 29.5, 1966: 44.3, 1967: 37.4, 1968: 45.0, 1969: 36.0, 1970: 30.0, 1971: 28.0,
         1972: 47.0, 1973: 27.0, 2004: 31.5, 2005: 30.5, 2006: 44.5, 2007: 33.9, 2008: 41.4,
         2009: 53.9, 2010: 35.1, 2011: 30.7}
fen_si = {1972, 1973} if alt else set()      # DATO DE PRUEBA
with open(f'{out}/estacion.csv', 'w') as f:
    f.write('# Serie PUBLICADA: P24 max anual de la estacion Chachapoyas, tesis UPAO (Campos e Inga,\n'
            '# 2016), Tabla Gumbel p. 94 / anexo p. 302; omite 1974-2003 tal como esta publicada.\n'
            '# La columna fen es DATO DE PRUEBA: la tesis no declara anios FEN.\n')
    f.write('estacion,anio,p24_mm,fen\n')
    for a, p in serie.items():
        f.write(f'CHACHAPOYAS,{a},{p},{"si" if a in fen_si else "no"}\n')
Sterr = 0.15 if alt else 0.10            # DATO DE PRUEBA (UNC: clase 'media' de la Tabla 08)
cov_t, suelo_t = (('cultivos', 'permeable') if alt else ('pastos_vegetacion_ligera', 'semipermeable'))  # PRUEBA (Tinas)
cuencas = [
    # id, area_km2, L_m, S_cauce, S_terreno, cobertura, suelo, metodo, H, ajuste, CN
    ('TINAS', 55.911, 14739.17, 0.0602, 0.20 if alt else 0.30, cov_t, suelo_t, 'temez', 888, '', 72),
    ('TINAS-T-DIAG', 9.0 if alt else 9.5, 14739.17, 0.0602, 0.20 if alt else 0.30, cov_t, suelo_t, 'temez', 888, '', 72),
    ('TINAS-K-DIAG', 9.0 if alt else 9.5, 14739.17, 0.0602, 0.20 if alt else 0.30, cov_t, suelo_t, 'kirpich', 888, 'ninguno', 72),
    ('CUNETA1', 0.0015, 50.0, 0.08, 0.08, 'talud_de_tierra' if alt else 'pavimento', '', 'kirpich', '', 'ninguno', ''),
    ('UNC-CAJ', 9.863, 5760.0, 0.15, Sterr, 'pastos_vegetacion_ligera', 'semipermeable', 'temez', '', '', ''),
    ('UNC-A1', 1.191, 1940.0, 0.27, Sterr, 'pastos_vegetacion_ligera', 'semipermeable', 'temez', '', '', ''),
    ('UNC-A2', 0.736, 1580.0, 0.21, Sterr, 'pastos_vegetacion_ligera', 'semipermeable', 'temez', '', '', ''),
]
with open(f'{out}/cuencas.csv', 'w') as f:
    f.write('# UPAO La Jalca (Tinas, cuneta 1) y UNC Cocahuayco (Cajahuache, A1, A2). Ver arma_hidro.py:\n'
            '# L, S, A, desnivel y CN publicados; S_terreno/cobertura/suelo de TINAS y CUNETA1 son DATOS DE\n'
            '# PRUEBA; las filas *-DIAG llevan AREA DE PRUEBA 9.5 km2 (variante de diagnostico).\n')
    f.write('id,area_km2,L_cauce_m,S_cauce_cuenca,S_terreno,cobertura,suelo,estacion,metodo_tc,H_desnivel_m,ajuste_kirpich,CN\n')
    for c in cuencas:
        f.write(','.join(str(x) for x in (c[0], c[1], c[2], c[3], c[4], c[5], c[6], 'CHACHAPOYAS', c[7], c[8], c[9], c[10])) + '\n')
cols = "id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal".split(',')
filas = []
for i, c in enumerate(cuencas):
    fam = 'B' if c[0] == 'CUNETA1' else 'A'
    filas.append(dict(id=c[0], progresiva_km=f'{i+1}+000', familia=fam, Q_m3s='', area_ha=f'{c[1]*100:.6g}',
        S_cauce='0.02', cota_terreno='100.00', cota_rasante='104.50' if alt else '104.00', cota_subrasante='104.35' if alt else '103.85',
        cbr_subrasante='12' if alt else '10', esviaje_grados='0', ancho_plataforma='8.0', cota_fondo_receptor='99.00',
        Q_receptor_m3s='', cota_TW='', sucs_fundacion='SM', NF_profundidad_m='', cota_fondo_entrada='', cota_coronacion_canal=''))
with open(f'{out}/puntos.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(filas)
json.dump({"globales": {"luz_m": 4.0 if alt else 3.0, "TW_m": 0.4 if alt else 0.3, "acceso_mantenimiento_previsto": True},
           "puntos": {"CUNETA1": {"S_cuneta": 0.012 if alt else 0.01, "ancho_tributario_m": 8.0 if alt else 6.0,
                                  "inicio_tramo_cuneta_km": 3.9 if alt else 3.95}}},
          open(f'{out}/externos.json', 'w'), indent=1)
json.dump({"corredor_del_proyecto": {"valor": "VALIDACION hidrologia UPAO/UNC (DATOS DE PRUEBA)",
           "trazabilidad": "DATOS DE PRUEBA, NO DEL PROYECTO: rotulo del caso de validacion externa", "fecha": "2026-11-15"}},
          open(f'{out}/sitio.json', 'w'), indent=1)
