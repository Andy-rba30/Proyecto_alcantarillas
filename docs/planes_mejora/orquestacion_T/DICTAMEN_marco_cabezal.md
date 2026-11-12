# Dictamen del verificador normativo — marco de estabilidad del cabezal (T-7b punto 1, opción (b) elegida por el dueño)

Verificado contra los PDF de `/home/user/andy-rba30/normas/normas/` (2026-11-11). Paginación: AASHTO «sección-página» impresa / PDF;
Manual de Puentes PDF = impresa + 1; E.050 PDF = impresa. Re-verifica tú cada cita antes de escribirla.

Decisión del dueño: **rige LRFD AASHTO 11.6; ASD de E.050 se calcula e imprime en paralelo; cuál rige es [A] con justificación.**
El verificador la CONFIRMA como coherente, con correcciones de enunciado (abajo).

## AASHTO LRFD 9.ª ed. (2020)

| Qué | Numeral | Impresa / PDF | Lo que dice |
|---|---|---|---|
| Excentricidad (resistencia) | 11.6.3.3 «Eccentricity Limits»; 10.6.3.3 | 11-24 / 1493; 10-83–84 / 1372–1373 | Suelo: resultante «within the middle two-thirds of the base width» (e ≤ B/3 desde el centro, sobre cargas FACTORADAS); roca: nueve décimos (0.45 B). C10.6.3.3: B/3 LRFD ≈ B/6 ASD. C11.6.3.3: la excentricidad REEMPLAZA al FS de volteo. |
| Portante | 11.6.3.2 «Bearing Resistance» | 11-21 / 1490 | Cargas y resistencias factoradas; presión uniforme sobre B−2e en suelo: σv = ΣV/(B−2e) (ec. 11.6.3.2-1); en roca lineal (11-22 / 1491). |
| Deslizamiento | 11.6.3.6 → 10.6.3.4 | 11-24 / 1493; 10-84 / 1373 | R_R = φτ·Rτ + φep·Rep; Rτ = C·V·tan φf, C = 1.0 concreto vaciado contra suelo. 11.6.3.5: pasiva despreciada salvo condiciones. |
| φ de zapatas | 10.5.5.2.2, Tabla 10.5.5.2.2-1 | 10-42 / 1331 | φb: 0.50 arcilla; 0.50 arena CPT; 0.45 arena SPT; 0.45 semiempírico; 0.45 roca; 0.55 placa. φτ: 0.90 prefabricado/arena; 0.80 in situ/arena; 0.85 sobre arcilla; 0.90 suelo/suelo. φep 0.50. |
| φ de muros | 11.5.7, Tabla 11.5.7-1 (y 11.5.5) | 11-15 / 1484; tabla 11-17 / 1486; 11-11 / 1480 | Muros de gravedad y semigravedad: portante **0.55**; deslizamiento **1.0**. Los φ de Sec. 10 valen «unless specifically identified in Table 11.5.7-1». TENSIÓN INTERNA con 11.6.3.6→10.6.3.4 (φτ 0.80): cuál se usa es LECTURA a declarar. |
| φ evento extremo | 11.5.8 | 11-18 / 1487 | «Unless otherwise specified, all resistance factors shall be taken as 1.0 … overall stability 0.9 … bearing resistance 0.8 for gravity and semigravity walls». NO es «φ = 1.0» a secas. |
| Sismo, excentricidad | 11.6.5.1 | 11-25–26 / 1494–1495 | Dos tercios centrales con γEQ = 0.0; ocho décimos (0.4 B) con γEQ = 1.0; interpolación lineal. P_IR = kh(Ww+Ws). Casos: 100 % P_AE + 50 % P_IR y 50 % P_AE (no menos que el activo estático) + 100 % P_IR. |
| Reducción de kh | 11.6.5.2.2 | 11-28 / 1497 | kh = 0.5·kh0 sólo si el muro es libre de moverse 1–2 in o más Y el Propietario acepta el desplazamiento. |
| Mononobe-Okabe | 11.6.5.3 (y C) | 11-29–30 / 1498–1499 | Sólo con relleno uniforme sin cohesión en la cuña 3H:1V, no saturado/licuable, y φ ≥ i + arctan[kh/(1−kv)] (con kh 0.50, kv 0: φ ≥ i + 26.6°). P_AE total aplicado con la distribución estática «but no less than H/3»; el comentario admite 0.4h–0.5h; el 0.6h de Seed-Whitman figura como «past practice». Decir a QUÉ fuerza se aplica la fracción (P_AE total vs ΔP_AE). |
| Muro no cedente | 11.6.5.4 | 11-32 / 1501 | kh = 1.0·kh0; ejemplos: estribos con aleros estructurales; resultante h/2 puede justificarse. Un cabezal monolítico con barril y aleros se parece a este caso. |
| ¿Exención sísmica? | 11.5.4.2 | 11-9 / 1478 | Sólo zonas 1–3 o As ≤ 0.4 g: con 0.50 g Evento Extremo I se exige. |
| Factores de carga | 3.4.1, Tablas 3.4.1-1 y -2; C11.5.6 Figs. -1/-2/-4 | 3-17 / 71; 3-18 / 72; 11-11–15 / 1480–1484 | Strength I: LS 1.75, WA 1.00; γp: DC 1.25/0.90, EH activo 1.50/0.90, EV muros 1.35/1.00. Extreme Event I: permanentes 1.00, LS γEQ, WA 1.00, EQ 1.00. Portante: máximos; deslizamiento y excentricidad: DC 0.90, EV 1.00, EH 1.50, y la LS NO se incluye sobre el talón. γEQ «project-specific» (C: 0.50 razonable; es comentario). |
| Coulomb / heq / agua | 3.11.5.3; 3.11.6.4 Tablas -1/-2; 3.11.3 | 3-121 / 175; 3-151 / 205; 3-118 / 172 | Confirmados (heq 5 ft→4.0, 10→3.0, ≥20→2.0 ft con interpolación; pesos sumergidos bajo el NF). |
| ¿11.6 aplica a cabezales? | 11.1, 11.6.1.1, 11.6.1.4; 12.6.8, 12.8.6.2 | 11-1 / 1470 … 12-23 / 1661 | NO hay remisión expresa Sec. 12 → 11.6. Aplica porque el cabezal se MODELA como muro de semigravedad: hipótesis de modelación, no mandato. No escribir «AASHTO manda diseñar el cabezal por 11.6». |

## Manual de Puentes MTC (ejemplar R.D. 041-2016-MTC/14)

- Introducción (43 / 44): adaptación de AASHTO LRFD 7.ª ed. (2014); formato LRFD; el propietario «podrá considerar las actualizaciones».
  Objeto: puentes carreteros; no extiende el Título II a cabezales de alcantarilla → aplicarlo es **[N→]**.
- 2.8.1.1.12 (248 / 249) portante con cargas y resistencias factoradas y σv = ΣV/(B−2e); «2.3.1.1.12.3 Límites de Excentricidad»
  (impreso así, errata por 2.8…; 250 / 251): dos tercios centrales; 2.8.1.1.12.6 y Tabla -1 (250–252 / 251–253): mismos φ de la
  Tabla 10.5.5.2.2-1 (NO transcribe la 11.5.7-1); 2.8.1.1.14.1 (252–253 / 253–254): Evento Extremo I con φ del 11.5.8 AASHTO
  («tercio central» es errata ya declarada en el repo); 2.4.5.3.1 y Tabla -1 (140–143 / 141–144): γEQ por proyecto.
- Vigencia: `fuentes.py` dice que la RD 19-2018 lo sustituyó (edición 2018 no está en `normas/`): citar como «ed. 2016, sustituida
  en 2018; numerales pendientes de contraste», no como [N] vigente sin salvedad.

## E.050 (RM 406-2018-VIVIENDA)

- Art. 21 (pág. 34): FS 3,0 estático; 2,5 «solicitación máxima de sismo o viento». 39.13.6 (pág. 72): volteo y deslizamiento 1.50
  estático / 1.25 «pseudo-dinámico». 39.13.8 (pág. 73): drenaje (remite a un «39.14.6» inexistente: errata por 39.13.6, declararla).
  Art. 17.1 (pág. 32): los FS van con **cargas de servicio**.
- Ámbito (Art. 1, 3, 6.1; pág. 7, 12): edificaciones (RNE); 39.13 está bajo «Sostenimiento de excavaciones». Para un cabezal vial es
  **[N→] por analogía, no [N]**. El rótulo «§9.3 Estabilidad — E.050 [N]» de la hoja de ruta está mal: defecto de la hoja a reportar.

## Reglas y recomendación

- **Regla de no cruce**: ASD = todas las cargas con γ = 1, resistencia nominal sin φ, cociente contra FS (E.050 17.1). LRFD = Σγ·Q
  (máx/mín según la verificación, C3.4.1 y Figs. C11.5.6) contra φ·Rn + excentricidad sobre cargas factoradas. Nunca cruzar: el FS
  de volteo no existe en LRFD; B/3 no es límite ASD (el equivalente de servicio es B/6).
- Hoy el repo SÍ mezcla: `M9.factores_de_carga` da γ LRFD y `verificar_volteo/deslizamiento/capacidad_portante` comparan con FS de
  E.050 sin decir qué cargas reciben. No hay ningún φ geotécnico transcrito ni verificación de excentricidad estática (sólo la sísmica, E6).
- Transcribir con página: Tabla 10.5.5.2.2-1, Tabla 11.5.7-1 y 11.5.8. Dejar en criterio [A] aparte cuál fila de φ rige
  (sugerencia: la conservadora que el Manual transcribe, 0.45–0.50 / 0.80–0.85, con sensibilidad hacia 0.55 / 1.0).
- La justificación del [A] del marco debe decir: ninguna norma peruana ni AASHTO Sec. 12 prescribe el marco de estabilidad de un
  cabezal de alcantarilla; se modela como muro de semigravedad y se adopta 11.6 por coherencia con la Vía 1 de la hoja y con el
  formato LRFD del Manual; E.050 se calcula en paralelo sobre cargas de servicio como contraste por analogía. NO debe decir «la
  norma exige LRFD para cabezales», ni «φ = 1.0 en evento extremo» a secas, ni «E.050 [N]».
- Declarar la **regla de desempate** entre marcos (si ASD no cumple y LRFD sí —probable con kh 0.50—: ASD informativo con aviso, o
  envolvente; es [A]).
- Abrir como vacíos/criterios declarados: condición cedente vs no cedente (11.6.5.4) —coherente con kh sin reducir—; aplicabilidad
  de M-O con NF alto y arenas licuables (11.6.5.3); γEQ; estabilidad global (9.ª: Strength I con φ 0.75/0.65, 11.6.3.7, 11-25 / 1494;
  Manual 2016: Servicio I; E.050: FS 1.5/1.25).
