import subprocess, sys, os, shutil
RAIZ = os.getcwd()
M9 = "src/modulos/M9_cabezal.py"; M5 = "src/modulos/M5_verificaciones.py"
MUT = [
 ("EV min->max en Resistencia I minimos", M9, 'factores(DC=g["DC"]["min"], EV=g["EV"]["min"], EH=g["EH"]["max"],', 'factores(DC=g["DC"]["min"], EV=g["EV"]["max"], EH=g["EH"]["max"],'),
 ("DC min->max en minimos", M9, 'factores(DC=g["DC"]["min"], EV=g["EV"]["min"], EH=g["EH"]["max"],', 'factores(DC=g["DC"]["max"], EV=g["EV"]["min"], EH=g["EH"]["max"],'),
 ("LS_v entra en minimos (estatico)", M9, 'LS=g["LS"], LS_v=0.0, WA=g["WA"]["max"]), B,', 'LS=g["LS"], WA=g["WA"]["max"]), B,'),
 ("piso estatico del caso 2 retirado", M9, 'and f_ae * datos["P_AE"] < datos["P_A"])', 'and False)'),
 ("phi portante sismico 0.8 -> general 1.0", M9, 'return {"portante": PHI_EVENTO_EXTREMO_11_5_8[\n                    "portante_gravedad_y_semigravedad"],', 'return {"portante": PHI_EVENTO_EXTREMO_11_5_8[\n                    "general"],'),
 ("suelo sumergido -> saturado (agua dos veces)", M9, 'gamma_sum = (gamma_sat - GAMMA_AGUA_KN_M3) if gamma_sat is not None else 0.0', 'gamma_sum = (gamma_sat) if gamma_sat is not None else 0.0'),
 ("subpresion del lado del talon con el nivel natural", M9, 'u_talon = GAMMA_AGUA_KN_M3 * h_w\n', 'u_talon = GAMMA_AGUA_KN_M3 * h_w_natural\n'),
 ("E3 LRFD sin phi", M9, 'R_R = phis["deslizamiento"] * R_tau', 'R_R = R_tau'),
 ("limite e sismico usa el estatico", M9, 'e_max = excentricidad_admisible_sismica(B=B, gamma_EQ=g_eq)', 'e_max = EXCENTRICIDAD_ESTATICA_FRACCION_B["suelo"] * B'),
 ("inclinacion con cargas FACTORADAS", M9, 'q_n, origen_q, det = _q_nominal(entorno, datos, suelo,\n                                        presion.ancho_efectivo, servicio)', 'q_n, origen_q, det = _q_nominal(entorno, datos, suelo,\n                                        presion.ancho_efectivo, c)'),
 ("LS sismica con gamma_EQ=1", M9, 'cargas, factores(LS=g_eq, LS_v=0.0, **comunes), B,', 'cargas, factores(LS=1.0, LS_v=0.0, **comunes), B,'),
 ("inercia del suelo fuera de P_IR", M9, 'EQ_PIR_muro=f_ir, EQ_PIR_suelo=f_ir)', 'EQ_PIR_muro=f_ir, EQ_PIR_suelo=0.0)'),
 ("h del plano = z_rel (sin la subida sobre el talon)", M9, '    h = z_rel + sobre_talon\n', '    h = z_rel\n'),
 ("D_w de la hoya sin corregir", M9, 'D_w = max(datos["NF"] - (entorno.cota_pie - terreno), 0.0)', 'D_w = max(datos["NF"], 0.0)'),
 ("brazo incremento sobre z_rel? fraccion*h -> h/3", M9, '        z_dP = fraccion * h\n', '        z_dP = h / 3\n'),
 ("V5: HW/S sin cos(esviaje)", M5, '    d = (semilongitud + x_embalse) * coseno\n', '    d = (semilongitud + x_embalse)\n'),
 ("V5: sin L_boca", M5, '    d = (semilongitud + x_embalse) * coseno\n', '    d = (x_embalse) * coseno\n'),
 ("V5: ancho entero en vez de la mitad", M5, '    medio = ancho / 2\n', '    medio = ancho\n'),
 ("V8: cota de desborde +1", M5, '    cumple = cota_embalse <= cota_desborde + TOL_UMBRAL_NORMATIVO\n    return Verificacion(\n        cumple=cumple,\n        numeral=NUMERAL_V8,', '    cumple = cota_embalse <= cota_desborde + 1.0\n    return Verificacion(\n        cumple=cumple,\n        numeral=NUMERAL_V8,'),
 ("entorno: cota_pie de la salida = terreno (datum)", M9, '            NF_profundidad_m=punto.NF_profundidad_m,\n', '            NF_profundidad_m=(None if punto.NF_profundidad_m is None else punto.NF_profundidad_m - 0.5),\n'),
]
lentos = "--lentos" in sys.argv
for nombre, ruta, viejo, nuevo in MUT:
    src = open(ruta, encoding="utf-8").read()
    n = src.count(viejo)
    if n != 1:
        print(f"[NO APLICA x{n}] {nombre}"); continue
    open(ruta, "w", encoding="utf-8").write(src.replace(viejo, nuevo))
    try:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-x", "tests/test_t7b_cabezal_estabilidad.py"] + ([] if lentos else ["-m", "not lento"])
        r = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, NORMAS_DIR="/home/user/andy-rba30/normas"))
        ult = [l for l in r.stdout.splitlines() if l.strip()][-1] if r.stdout.strip() else r.stderr[-200:]
        primero = next((l for l in r.stdout.splitlines() if l.startswith("FAILED") or l.startswith("ERROR")), "")
        print(("[MUERTO]" if r.returncode != 0 else "[VIVO]  "), nombre, "|", primero[:110] or ult[:80])
    finally:
        open(ruta, "w", encoding="utf-8").write(src)
