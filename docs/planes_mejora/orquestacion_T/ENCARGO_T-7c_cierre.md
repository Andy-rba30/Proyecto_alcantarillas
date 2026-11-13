# Encargo: T-7c (cabezal: armado y alternativa ciclópea) — correcciones de la auditoría adversarial + integración en main

Sigue `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (léelo primero, entero; donde dice base `df1b23c`, la de T-7c es `451a10a`,
par de referencia con `NORMAS_DIR` 5979 passed / 23 skipped / 6002 collected, sin él 5961 / 41). Worktree `/home/user/wt/T-7c`,
rama `tesis/T-7c`, HEAD `f50edbe`; `origin/main` = `451a10a` (nadie más empuja a main). Lee además `ORQ/ENCARGO_T-7c.md`,
`ORQ/PRECISIONES_T-7c.md`, `ORQ/INFORME_T-7b_final.md`, `ORQ/INFORME_T-7c_faseA.md` y **`ORQ/AUDITORIA_T-7c.md`** (AJUSTADO:
2 ALTA, 5 MEDIA, 5 BAJA; trae el caso a mano de A-01, la expresión correcta y los DORADOS DE CONTROL de cada corrección de
fórmula, y aprueba la cuña de T-7b). Te tocan TODOS sus hallazgos. Scripts del auditor: `ORQ/aud_T-7c_scripts/` (referencia).

## Resoluciones del orquestador (vinculantes; si el PDF contradice una premisa, gana la fuente y lo reportas)
- **H1 (ALTA, fórmula) — momento de la pantalla y del alero.** En `M9.solicitaciones_por_elemento` (código de T-7b, ya en main)
  integra cada diagrama POR ENCIMA del arranque, como da el auditor: suelo H = K·γ·(h − e_z)²/2·cos(δ+β), M = H·(h − e_z)/3 (con
  el tramo sumergido como en `acciones_sobre_una_seccion(z_seccion=e_z)`); sobrecarga H = K·γ·h_eq·(h − e_z), M = H·(h − e_z)/2;
  inercia sólo la de la pantalla, k_h·W_pant·(z_pant − e_z). Corrige el docstring («del lado seguro» era falso para el momento),
  `_momento_con_resultante_a_media_altura` y `cargas_en_reposo` en coherencia, y REHAZ el dorado `CP_T7C_ARMADO` a mano
  (control del auditor, muro T-00: activo V_u 26.491 kN/m, M_u 21.466 kN·m/m; reposo 43.502 y 35.402; A_s 476 mm²/m; mínimo con
  M_cr 46.437 → 630.7 mm²/m). OJO: el cortante de la cara: decide con la fuente si se integra también sobre el arranque (el
  auditor lo escribe así) y dilo. Los tests de T-7b que fijan la pantalla y los aleros se reescriben DECLARÁNDOLO (qué fijaban,
  qué fijan, por qué). La ESTABILIDAD externa no cambia en nada (compruébalo: las filas E1–E3 de A-01 idénticas).
- **H2 (ALTA, fórmula y cita) — sismo con el régimen que no cede.** Con `regimen_resistencia_elementos_cabezal = no_cedente_k0`
  las cargas sísmicas DEL ARMADO se calculan con k_h = `cadena.k_h0` (AASHTO 11.6.5.4, pág. impresa 11-32 / PDF 1501: «shall be
  increased to 1.0kh0»: verifica el literal y cítalo con su carácter), por una puerta de sobrescritura de k_h en
  `cargas_del_cabezal` que la estabilidad externa NO usa. Controles del auditor (A-01, datos de prueba, k_h0 0.50): pantalla de
  entrada M_u 57.27 → 703 mm²/m, Ø 1/2" @ 0.175; pantalla de salida M_u 135.51 → 1798 mm²/m, Ø 5/8" @ 0.10; punta de salida
  755 mm²/m (recalcúlalos con H1 aplicado y da los valores finales). `F9.ARM_REGIMEN` y el paso dicen lo que el código hace.
- **H3 + pregunta 5 — fisuración 5.6.7.** Impleméntala en `diseno_flexion_corte` (ec. 5.6.7-1, verificada en la pág. impresa
  5-55 / PDF 414, con su condición de aplicación 0.8·f_r, f_ss elástico de sección fisurada, d_c, β_s; constante 700 en ksi-in
  convertida con sufijo `_SI`) sobre la combinación de Servicio I de las mismas cargas. La **clase de exposición** (γ_e 1.00 /
  0.75) es criterio [A] categórico SIN valor de archivo (la decide el Propietario): sin declararla, la fila de fisuración sale
  como INDICADOR «no decidida» imprimiendo el espaciamiento máximo con Clase 1 y con Clase 2 y si el propuesto los cumple;
  declarada, DECIDE (y la propuesta de barras la respeta). A4 deja de decir CUMPLE a secas cuando 5.6.7 aplica y no está
  decidida. Dorado a mano (control del auditor, pantalla de salida de A-01: s ≤ 145 mm Clase 1; ≤ 60 mm Clase 2).
- **H4 — E.060 15.7.** Fila (o aviso por `avisos()`) en `ensamblar_armado`: altura de la zapata sobre el refuerzo inferior
  (e_z − recubrimiento de la cara inferior − lo que corresponda) frente a 300 mm, con el recubrimiento con que SE ARMA. No iteres.
- **H5 + pregunta 8 — ciclópeo.** Cita E.060 22.4.7 (pág. 191: tracción no transmitida por juntas de construcción) y 22.6.3;
  C2 (tracciones nulas en el arranque) DECIDE SIEMPRE salvo vaciado monolítico declarado; tracciones nulas siguen de archivo;
  corrige la ficha T7C-09 y la justificación («ninguna fuente exige» era falso); el umbral de C1–C3 con `Interpretacion` (la cita
  `E060.22.6.3#TERCIO` no exige e ≤ B/6 con cargas de servicio). Test con C6 incumpliendo bajo `traccion_admisible_e060`.
- **H6**: el aviso de «lo que el armado NO cubre» y la ficha T7C-04 nombran el VANO del conducto (la pantalla es hueco en más de
  la mitad de su longitud: refuerzo de borde alrededor de la abertura —E.060 22.6.6.5 por analogía para el ciclópeo; verifica—),
  la losa de entrega y el dentellón. Sin dimensionar: decirlo.
- **H7**: textos que afirman lo que el código no hace (A6 inexistente → o fila que decide cuando el dato existe, o corregir;
  A5/A1; R4-R5/C4-C5; «lado seguro» de EQ.PIR.muro).
- **H8**: d_v se acota a d_e (lectura conservadora DECLARADA como `Interpretacion`: la letra de 5.7.2.8 permite 0.72·h, que con
  el recubrimiento de cota supera al peralte efectivo), con el valor de la letra impreso al lado y aviso cuando difieren.
  Recalcula y di si algún veredicto de A-01 cambia.
- **H9**: aviso cuando la combinación «Resistencia I (mínimos), reposo» deja la resultante fuera de la base y se descarta.
  **H10**: imprime la sensibilidad de K0 con relleno en talud (K0·(1 + sen i)) como contraste, sin adoptarla.
  **H11**: los dos mutantes vivos con test. **H12**: sufijo `_SI` en las conversiones de constantes empíricas y
  `BARRA_GRUESA_DESDE` fuera del módulo de cálculo (constante/criterio con su cita).
- **Preguntas del informe** (resueltas; el dueño delegó: «sigue con tus recomendaciones»):
  1. E.060 22.7.4 (0.30 m) y 14.3.1 pasan a **[N→]** (ámbito: edificaciones; la excepción de la §0.2 de la v8 cubre sólo
     durabilidad, y por eso 7.7.1 queda [N]): hazlo en este cierre si es un cambio acotado (constante → criterio [N→], censos);
     si al tocarlo ves que arrastra más de lo que parece, déjalo en la ficha T7C-10 con el porqué.
  2. Recubrimiento sin dato: se mantiene la cota de 91.44 mm; el aviso dice dónde NO es el lado seguro (5.6.7, E.060 15.7, cortante).
  3. Talón: peso entero (11.6.1.2 «shall … unless a more exact method is used»), el exacto impreso al lado.
  4. Pantalla como losa frente a 5.7.2.3: se mantiene, con fila INDICADOR en A2 cuando V_u > 0.5·φ·V_c (en la salida de A-01 ocurre).
  6. **η del cabezal**: el mismo modificador de carga del conducto (`η_I` de T-5, [A] del Propietario; η_D y η_R como T-5 los
     dejó) en las combinaciones de Resistencia I del cabezal —estabilidad Y armado—, aplicado como manda AASHTO 1.3.2.1 (η ≥ 0.95
     con factores máximos; 1/η ≤ 1.0 con factores mínimos; η = 1 en Evento Extremo salvo lo que diga la fuente): verifica el
     literal en el PDF ANTES; dorado a mano; declara cómo se mueven las filas E1–E3 y el armado de A-01 con datos de prueba. Si
     la fuente no lo sostiene así o el cambio no es acotado, NO lo apliques: ficha con la evidencia y repórtalo.
  7. Es H2. 8. Es H5.
- **Tracker**: `INF-4.6` cerrado con residuales nombrados (T7C-03, -04, -06, -09 y lo que quede de 5.6.7), `INF-3.4.5` cerrado,
  ficha `EXT-7-01` cerrada; notas en `INF-0.5`, `EXT-M-05`, `R95-031`, `INF-4.3`.

## Integración — lo específico de T-7c
Censos esperables: criterios 136 + los que añadas (clase de exposición; los [N→] de la pregunta 1), sin valor 19 + 1;
`FUNCIONES_SIN_CONSUMIDOR` ocho → seis; marcas `literal-ok` de M9. Tu Parte de `decisiones_diferidas.md` (rótulo provisional
«LI») se renumera a la siguiente libre. Línea base contra `451a10a`: sólo huellas, recuentos y notas (ninguna corrida de la línea
base llega a armar). **Diámetros, secciones, materiales y HW: ninguno.** Mutación con el arnés sobre lo que TOCASTE en el cierre.
Commit: `tesis(T-7c): cabezal — armado con AASHTO LRFD Seccion 5 (E.060 de contraste) y alternativa ciclopea … — INF-4.6, INF-3.4.5 (cerrados); EXT-7-01`.
Deja dicho en tu informe, para T-10 (memoria): qué pasos y tablas emite el armado y por dónde (`PasoDeMemoria`, datos del JSON).

Entrega: `SP/INFORME_T-7c_final.md` + resumen < 350 palabras (SHA en `origin/main`, par con y sin `NORMAS_DIR`, IDs, tests
nuevos, armado final de A-01 con datos de prueba —pantalla, punta y talón de entrada y salida—, movidos, diferidos, preguntas).
