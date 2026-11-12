# Correcciones de auditoría adversarial — qué se pidió a cada agente (para reanudar si se pierde su contexto)

## T-6 (geometría) — APLICADAS en `tesis/T-6` (`3462f8b`); queda SÓLO el ítem 2, que es de su FASE B (tras integrar T-2)
Ítem 2: choque `M7.pendiente_adoptada` (recorta la pendiente del CAUCE a MINIMA/MAXIMA) ↔ `M5.v10_pendiente_conducto` de T-2 (rechaza).
Decisión del orquestador: se mantiene lo que la cadena pide (M7 adopta el límite sólo sobre la pendiente del cauce; V10 juzga la
adoptada y por tanto sólo puede fallar con una DECLARADA), pero DICHO: (i) alinear docstring de V10 y ficha T2 con esa división;
(ii) origen MAXIMA → paso + aviso: S_conducto < S_cauce exige estructura de caída/disipación y V2b lo juzga según `regimen_v2b`;
origen MINIMA → la salida queda más baja que el cauce y G2 lo juzga; (iii) tests de punta a punta de los dos casos;
(iv) ampliar ficha T6-02; (v) comprobar que con 0.0 / 0.10 nada del fixture se mueve. `M5.limites_de_pendiente()` es lo que M7 lee.
Además en FASE B: liberar el test `skipif` de las claves de T-2, renumerar la «Parte XLI» de decisiones_diferidas si choca,
regenerar los cuatro generados, tracker, tabla de CLAUDE.md.
Para T-7a: la longitud entre cabezales (construcción/metrado; ~14.7 m en A-01 frente a 18.87 m de cálculo al fondo) se cierra
cuando exista la coronación del cabezal (ficha T6-01).

## T-1 (hidrología) — EN CURSO en `tesis/T-1` (base de la auditoría `a535295`); comprobar con `git log`/diff cuáles están hechas
H1 aviso+INDICADOR en 1b.2 cuando P24(TR) < máximo observado con T empírico (n+1)/m ≤ TR (ec. 13); llega a `avisos`; corregir la
   justificación de `distribucion_precipitacion_maxima`; cita nueva MTC pág. impresa 64 / PDF 67 (Piura y Tumbes, «tratamiento especial»).
H2 celda `fen` vacía → `DatoFaltanteError('fen')` (hoy se lee «no»).
H3 duración mínima de lluvia: criterio `duracion_minima_lluvia_min` — [C] si WSDOT (HydraulicsManual.pdf, cap. 2, racional) fija
   tc mínimo (verificar), si no [A] `valor=None` + `CriterioPendienteError`; tc < mínimo → se adopta el mínimo con aviso. Bloquea T-9.
H4 `ajuste_kirpich` obligatoria si `metodo_tc = kirpich`; `S_terreno` obligatoria (nada de caer a `S_cauce_cuenca`).
H5 con Q DECLARADO: `tratamiento_fen = None` + aviso permanente (no atribuir al estudio externo el criterio de los calculados).
H6 mismo trato Kirpich/California fuera de 3–10 %: criterio [A] categórico (`no_evaluable` valor de archivo / `indicador_con_aviso`),
   `Interpretacion` impresa; transcribir Tabla 05 ENTERA e implementar métodos de terreno plano (FAA al menos; SCS retardo con CN
   opcional; onda cinemática sólo si no exige datos que no hay) con dorado a mano. Témez < 0.25 h sigue no evaluable.
H7 Témez en racional simple: criterio [A] `coeficiente_uniformidad_temez` ∈ {aplicar (archivo), no_aplicar}; K = 1 + Tc^1.25/(Tc^1.25+14)
   (ec. 29, verificar pág.); paso declara uso HÍBRIDO; ficha diferida del Racional Modificado completo.
H8 cruce `area_ha` ↔ `area_km2`: `DatoInvalidoError` que nombre el par (tolerancia nombrada).
H9 `--prevuelo` avisa de `--cuencas/--estacion` que no aplica y no dice DETIENE lo que la hidrología cubre; corregir atribución en C-01.
H10 n < 5 → MetodoNoEvaluable; aviso de serie corta a `avisos`; `p24_mm = 0` admitido (excluye lognormal diciéndolo); 1b.1 imprime
   rango y AÑOS FALTANTES; el contraste sin FEN no detiene el adoptado; TR ≤ 1 → ErrorProyecto.
H11 RESTAURAR en la hoja de ruta «adoptar el más conservador» (el agente la había relajado a «no se impone»); `serie_sin_fen`
   declarable pero NO_CUMPLE contra `MC_HHD.3.4#FEN` (EXIGENCIA: «deberá incluir los años… El Niño») si da menos que la completa.
   CONFIRMADO POR EL DUEÑO.
H12 enlace T-9: `caudal_de_aporte_cuneta` devuelve PasoDeMemoria; ninguna pública salta la puerta FEN; un solo 0.278; C de
   pavimento/talud: [C] si WSDOT lo trae (verificar), si no [A] `valor=None`.
H13 docstrings falsos (MD.disenar_lote, constantes_normativas, test_cierre_perfil), sufijo `_SI` en las constantes empíricas, nota Gumbel asintótico.

## T-2 (hidráulica) — auditoría LLEGADA (AJUSTADO); el agente aplica correcciones y a continuación INTEGRA en main (primero del lote)
1 CSV de resumen imprime `&ndash;` con barril horizontal (`M11._fila_resumen_csv`). 2 alternativa `aviso` de V1 discontinua en TW
(sólo actúa con TW ≥ D): hacerla monótona (TW > 0.75·D y tirante por caudal ≤ 0.75·D); valor de archivo sigue `no_cumple`.
3 test del barril horizontal con control de ENTRADA (D 0.90, Q 1.5, L 12, S 0, TW 0) — tres mutantes vivos. 4 T2-01: decir la dirección
de la discontinuidad. 5 indicador de V2b a `avisos` del punto y cuenta de avisos en el RESUMEN; ficha de `energia_critica` sin
«lado seguro» a secas. 6 V10 antes de V5 en expediente. 7 `CP_HDS5_DG1`: comparar h_o de las filas CMP y la fila de SALIDA acotando n.
8 techos de n y altura en `seccion_receptor_medida`.

## T-4 (materiales/durabilidad) — auditoría LLEGADA (AJUSTADO, H1–H4 refutados); el agente aplica correcciones; integra tras T-2
H2 tope del concreto = último diámetro con diseño estándar tabulado en M 170M (2.70 m; 2850–3600 son «special designs» 7.2, la norma
no tabula pared): V9 vuelve a 2.70. H1 `MD.disenar_punto` no puede adoptar un material menos preferente si uno anterior quedó en
`faltantes`; si ninguno cierra sigue `DisenoNoFactibleError` pero dice qué escalones no se evaluaron. H3 criterios electroquímicos de
AASHTO LRFD 11.10.6.4.2a / 11.12.8 / 10.7.5 por analogía [C] como AVISO con umbral (el filtro de exclusión sigue con WSDOT y EG-2013 507.10).
H4 ventanas de `durabilidad_tmc_umbrales` que sólo endurezcan. H5 EG-2013 507.10 entero (sustancias agresivas → EXIGE protección).
H6 aviso fijo MTC 4.1.1.3.7 f) g) ligado a TMC candidata. H7 plancha 68×13/2.01 no cumple FF de A796 desde ~1.39 m: ENTRADA OBLIGADA
DE T-5 (FF y calibre también a perfil); `espesor_pared` de TMC/HDPE es envolvente geométrica. H8 cruce sulfatos ↔ `exposicion_quimica_ems`;
claves de durabilidad al censo como opcionales. H9 aviso SUCS: Art. 24 manda remover; SM/SP-SM/ML bajo napa → licuación Art. 38.2.
H10 test debilitado. H11 menores (techo 1e6 ppm, 0.61 m con pavimento, conftest con espesor sintético).
