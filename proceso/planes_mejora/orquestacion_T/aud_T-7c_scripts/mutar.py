import subprocess, pathlib, os, sys
R = pathlib.Path("/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-7c-aud/mut")
F = R / "src/modulos/M9_cabezal.py"
orig = F.read_text(encoding="utf-8")
M = [
 ("M1 h/2 -> h/3 en la resultante sismica", 'return M_u - M_en_su_sitio + H * max(datos["h"] / 2 - e_z, 0.0)', 'return M_u - M_en_su_sitio + H * max(datos["h"] / 3 - e_z, 0.0)'),
 ("M2 LS.h sin escalar en reposo", 'c = _reemplazar(c, H=c.H * escala,', 'c = _reemplazar(c, H=c.H * 1.0,'),
 ("M3 EH reposo minimos: max -> min (2a combinacion)", 'EV=g["EV"]["min"], EH=reposo["max"],', 'EV=g["EV"]["min"], EH=reposo["min"],'),
 ("M4 minimo de flexion: min -> max", 'M_minimo = (min(FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO * M_resistencia,\n                    M_cr)', 'M_minimo = (max(FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO * M_resistencia,\n                    M_cr)'),
 ("M5 1.33 Mu con todas las combinaciones (tambien sismo)", 'estaticas = [s for s in sols if s.condicion is CondicionAnalisis.ESTATICO]\n    M_resistencia', 'estaticas = [s for s in sols]\n    M_resistencia'),
 ("M6 sismo sin h/2", 'M_u = max(M_c, M_r) if (usa_reposo and M_r is not None) \\\n                    else M_c', 'M_u = M_c'),
 ("M7 subpresion del talon con signo cambiado", '"talon": (V_peso - F_t - f_u * U_t, M_peso - M_t - f_u * MU_t),', '"talon": (V_peso - F_t + f_u * U_t, M_peso - M_t + f_u * MU_t),'),
 ("M8 d_v sin el piso 0.72 h", 'd_v = max(d - a / 2, DV_PISO_SOBRE_DE * d, DV_PISO_SOBRE_H * espesor)', 'd_v = max(d - a / 2, DV_PISO_SOBRE_DE * d)'),
 ("M9 E.060 muro siempre 1 capa", 'capas = 2 if requiere_refuerzo_dos_capas(espesor=espesor) else 1', 'capas = 1'),
 ("M10 C6 decide invertido", 'margen=1.0 - uso_e060, decide=not nulas, obtenido=uso_e060,', 'margen=1.0 - uso_e060, decide=nulas, obtenido=uso_e060,'),
 ("M11 ciclopeo sin reducir 50 mm", 't_r = a["t"] - REDUCCION_PERALTE_CONTRA_SUELO_M', 't_r = a["t"]'),
 ("M12 activo del ciclopeo sin cos(delta)", 'horizontal = 1.0 if en_reposo else math.cos(datos["inclinacion"])', 'horizontal = 1.0'),
 ("M13 cortante sin el reposo", 'candidatos_V = [abs(V_c)] + ([abs(V_r)] if usa_reposo\n                                         and V_r is not None else [])', 'candidatos_V = [abs(V_c)]'),
 ("M14 zapata siempre en el simplificado", 'if es_zapata and vuelo is not None and \\\n            vuelo < ZAPATA_SIMPLIFICADO_VECES_DV * d_v - TOL_UMBRAL_NORMATIVO:', 'if es_zapata:'),
 ("M15 aviso de k_h invertido", 'if usa_reposo and cadena.k_h < cadena.k_h0 - TOL_UMBRAL_NORMATIVO:', 'if usa_reposo and cadena.k_h > cadena.k_h0 + TOL_UMBRAL_NORMATIVO:'),
 ("M16 alero con el espesor de la pantalla", 'espesor=g.aleros.espesor, elemento=ELEMENTO_ALEROS,', 'espesor=g.espesor_base_muro, elemento=ELEMENTO_ALEROS,'),
 ("M17 phi del evento extremo = 0.9", 'phi_x = proc["phi_evento_extremo"]', 'phi_x = proc["phi_flexion"]'),
 ("M18 A1 sin exigir seccion controlada por traccion", 'cumple_M = (barra is not None and alcanza and controlada\n', 'cumple_M = (barra is not None and alcanza\n'),
 ("M19 talon: rige el exacto en vez del peso entero", 'return Mp, Vp, (\n                f"peso entero', 'return (z["talon"][1] if z else Mp), (z["talon"][0] if z else Vp), (\n                f"peso entero'),
 ("M20 punta sin subpresion", '"punta": (F_p + f_u * U_p - w * punta,\n                  M_p + f_u * MU_p - w * punta ** 2 / 2),', '"punta": (F_p - w * punta,\n                  M_p - w * punta ** 2 / 2),'),
 ("M21 EH.v se conserva en reposo", 'c = _reemplazar(c, V=0.0,', 'c = _reemplazar(c, V=c.V,'),
 ("M22 E.060 contraste con phi corte 0.90 (cruce de marcos)", 'V_r_e = (PHI_CORTE_E060 * VC_COEFICIENTE_E060', 'V_r_e = (PHI_CORTE_AASHTO_X * VC_COEFICIENTE_E060'),
 ("M23 temperatura: ancho = espesor (b = h)", 'As_ts = acero_de_temperatura_aashto(ancho=max(ancho, espesor),', 'As_ts = acero_de_temperatura_aashto(ancho=espesor,'),
 ("M24 espaciamiento E.060 no entra", 'if regla == MINIMOS_MAS_EXIGENTE:\n        candidatos.append((espaciamiento_maximo(espesor=espesor),', 'if False:\n        candidatos.append((espaciamiento_maximo(espesor=espesor),'),
 ("M25 C1 base sin la variante sin peso de LS", 'for con_peso_ls in (True, False):', 'for con_peso_ls in (True,):'),
 ("M26 ciclopeo: peor seccion toma solo el activo", 'juegos.append(("reposo", cargas_en_reposo(cargas, datos), True))', 'pass'),
]
env = dict(os.environ, NORMAS_DIR="/home/user/andy-rba30/normas", PYTHONDONTWRITEBYTECODE="1")
for nombre, a, b in M:
    if nombre.startswith("M22"):
        b = b.replace("PHI_CORTE_AASHTO_X", "0.90")
    if orig.count(a) != 1:
        print(f"{nombre}: NO APLICA (ocurrencias {orig.count(a)})"); continue
    F.write_text(orig.replace(a, b), encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-x", "-m", "not lento and not pdf", "tests/test_t7c_cabezal_armado.py"], cwd=R, env=env, capture_output=True, text=True)
    cola = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    falla = [l for l in r.stdout.splitlines() if l.startswith("FAILED") or l.startswith("ERROR")]
    print(f"{nombre}: {'MUERTO' if r.returncode else 'VIVO'} | {cola} | {falla[0][:120] if falla else ''}")
F.write_text(orig, encoding="utf-8")
