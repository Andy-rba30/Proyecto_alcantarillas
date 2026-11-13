# Decisiones del dueño del 2026-11-12 (~16:40 UTC) — «aplica tus sugerencias»

El orquestador le presentó al dueño, como recomendación de ingeniería, una respuesta a cada pregunta que las auditorías de T-5 y
T-8 dejaban «para el dueño». El dueño las APROBÓ TODAS. Son decisiones tomadas: se aplican como valor de archivo y sustituyen a las
«resoluciones provisionales» de los encargos donde discrepen. Sigue valiendo, por encima de todas: gana la fuente primaria (si el
texto literal del PDF contradice la premisa de una decisión, NO la apliques: deja lo que la fuente sostiene y repórtalo), y
**ningún diámetro ni material adoptado del fixture se mueve** (A-01 y A-02 concreto Ø 0.90; B-01; C-01): eso NO se aprobó.

## T-5 (estructural del conducto)
1. **Instalación del concreto**: valor de archivo **Tipo 3**, justificado en que EG-2013 508.07 exige > 95 % del Proctor Modificado
   (la hipótesis de cálculo debe coincidir con lo que la especificación garantiza); `tipo_4` DENTRO de la ventana y **el Tipo 4
   impreso al lado como contraste** en el paso (clase y relleno máximo con Tipo 4: en A-01, 3.18 → 1.69 m), para que se vea cuánto
   pesa la compactación. Sin «el más desfavorable» a secas.
2. **HDPE**: las propiedades de sección son DATO DEL FABRICANTE (entrada opcional, sin valor por defecto). Sin ellas el resultado
   se rotula **«no verificado con un producto real»** (con el perfil mínimo de la Tabla A12-11 como cota inferior impresa y la cita
   de C12.12.3.2), no un «no cumple» a secas; y el HDPE no puede ADOPTARSE sin ese dato. Relleno de la zona del tubo flexible:
   **granular**, como lo exija el literal de EG-2013 508.02 (nunca `Cl-95` por inercia). Cuidado con la regla de T-4 («no se adopta
   un candidato si uno ANTERIOR quedó sin evaluar por un dato que falta»): la forma en que el HDPE quede «no verificado» NO puede
   bloquear ni mover el material adoptado de ningún punto del fixture; si chocan, gana no mover el fixture y se reporta.
3. **`fabricacion_tmc`**: valor de archivo **remachada simple** (la costura más débil tabulada). APROBADO que el TMC Ø 1.95 del caso
   G2 de T-4 cambie de resultado: el test se reescribe a la verdad nueva DECLARÁNDOLO (qué pasaba, qué pasa, por qué), no en
   silencio. La progresión debe intentar primero subir de plancha/costura dentro de la tabla antes de dar el punto por no factible.
4. **Carga viva sobre 8 ft**: valor de archivo **conservarla**; «despreciar según la fuente» queda como alternativa barrible.
5. **η_I = 1.05**: se mantiene, declarado como clasificación de importancia que hace el PROPIETARIO (vía de acceso en emergencia,
   FEN), [A] con la ventana que dé la fuente (Manual de Puentes 2.3.2.5); η_R según 12.5.4 de la 9.ª (el auditor leyó «redundant» → 1.00).
6. **Concreto que pide más que la Clase II**: **bloquear** (no subir de diámetro para esquivar una clase). El mensaje dice qué lo
   destraba: un ejemplar legible de AASHTO M 170M (o ASTM C76) para transcribir las Clases I, III, IV y V. Va a la lista de
   entradas que debe conseguir el dueño (`docs/contrato_entradas.md`).
7. **Pandeo del HDPE**: el módulo que manda la LETRA de 12.12.3.3 para cada carga (lectura conservadora).

## T-8 (protección de salida)
1. **`regla_espesor_longitud_proteccion_salida`**: valor de archivo **`envolvente_hec14`**, y la envolvente alcanza también al
   **tamaño de la piedra**: d50 adoptado = el MAYOR entre Laushey (manual MTC, que se sigue calculando e imprimiendo) y la Ec. (10.4)
   de HEC-14; espesor y longitud, la envolvente. `manual` queda como alternativa barrible que reproduce los números anteriores.
   Donde HEC-14 no es evaluable (sus límites), rige Laushey y se avisa. **APROBADO que se muevan los números de protección de la
   línea base** (d50, espesor, longitud: en A-01 el espesor pasa de 0.592 a 0.770 m): decláralos uno a uno con su causa. Ningún
   diámetro se mueve. Los avisos del contraste salen bajo las dos reglas.
2. **Tirante de borde (Figs. 3.3–3.4 de HEC-14)**: ahora, NO concluir «sin enrocado» cuando la velocidad es cota inferior;
   digitalizar las figuras queda para un prompt aparte (ficha diferida).
3. **Duración del pico para el desplante**: sin hidrograma, **360 min** (la fuente dice que a 30 min sólo se alcanza de 2/3 a 3/4 de
   la socavación máxima). El criterio pasa a ser una ELECCIÓN [A] dentro de la ventana 30–360 que la fuente sostiene, con 30 min
   (el valor que la fuente recomienda cuando no se conoce) como alternativa barrible y la cita literal. APROBADO que se mueva la
   profundidad de la hoya de la línea base: decláralo.
4. **Nota (5) b de la Tabla 511-06**: la lectura que NO relaja, declarada como `Interpretacion`, hasta conseguir AASHTO M 288.
5. **Límite del apron**: **1.524 m (60 in)**, declarado como lectura que deja evaluable el ejemplo resuelto de la propia fuente; el
   dorado del ejemplo vuelve a su escala real.
6. **«Sin enrocado»**: nunca como conclusión. La protección de Laushey/envolvente se calcula y se mantiene SIEMPRE; el contraste
   con la Tabla Nº 11 informa si el terreno resistiría, y suprimir la protección queda sujeto a inspección de campo (HDS-5 5.3.2),
   dicho en el paso y en los avisos. (Sin `tipo_terreno_receptor` la conducta de hoy no cambia.)

## T-3 (Familia C) — decidido por el dueño el 2026-11-12 ~16:55 UTC («aplica tu recomendación»)
1. **Progresión de secciones del marco (`secciones_cajon_normalizadas`)**: se MANTIENE como valor de archivo la que ya usaba el
   proyecto —(1.20, 0.90), (1.50, 1.20), (2.00, 1.50)—, [A] con su ventana; la de la cadena (anchos 1.00–4.00 paso 0.50, alturas
   1.00–3.00 paso 0.25) NO se activa porque no contiene 1.20 × 0.90 y deja a C-01 sin dimensionar (no cabe bajo una rasante con poco
   relleno). Ampliarla (alturas 0.60 y 0.75 m, más anchos) queda diferida a cuando exista la sección real del canal de ANA / la
   Junta: ficha con símbolo. Deja de ser «provisional»: es la decisión.
2. **Embocadura del cajón**: queda la de aletas de 30° a 75° que dejó T-3; la coherencia embocadura ↔ ke ↔ carta la cierra T-7a.
3. **VC2**: aviso, no bloqueo (para bloquear haría falta la tolerancia del proyecto del canal).

## T-7a (cabezal: geometría y aleros) — decidido por el dueño el 2026-11-12 ~17:10 UTC («sigue con tu recomendación»)
Se ACEPTAN, sujetas a lo que diga la auditoría adversarial (si el auditor las refuta con la fuente, gana la fuente):
1. Longitud de aleros con **cos α** (α medido desde el eje del conducto, convención de la Tabla C.2 de HDS-5), no el «sen α» del prompt.
2. Pie del cabezal de salida en **la más baja** entre la solera y el fondo del receptor (A-01: −0.69 m de desplante; lado seguro).
3. Caja receptora **sin aleros** (Lámina 02-A), no los 60° del prompt.
4. En la integración de T-7a se ABRE LA PUERTA de `ancho_derecho_via_m` como dato externo (opcional, sin valor por defecto, con
   forma y dominio), para que V5 deje de detener siempre la corrida de expediente y la Fase 9 por punto se alcance de punta a punta
   (hallazgo T7A-01); sin el dato, V5 sigue bloqueando como hoy.
5. Orden: no se lanza nada nuevo hasta que T-5 y las correcciones de T-8 entren en main y se mida la cuota.

## T-9 (espaciamiento de alivios) — decidido por el dueño el 2026-11-12 ~17:15 UTC («sí»)
1. **`seccion_cuneta`**: valor de archivo = el mínimo de la Tabla 34 del manual MTC para región «muy lluviosa» (0.40 m de
   profundidad × 1.20 m de ancho según el informe de FASE A: el auditor verifica las celdas contra el PDF antes de escribirlo),
   [A] con su ventana, coherente con los 200 m de longitud máxima por FEN.
2. **Borde libre de la cuneta**: se RETIRA de la v8 la frase «con borde libre» sin cifra (el Manual calcula a cuneta llena; nota
   de corrección en la hoja de ruta); queda el campo [A] de 0 a 0.10 m con valor 0.
3. **Obras de Familia A como extremo de tramo**: SÍ cuentan por defecto (una alcantarilla de cauce también descarga la cuneta);
   `inicio_tramo_cuneta_km` declarado sigue ganando.
4. **TR de 35 años**: NO confirmado todavía; depende de que el auditor verifique la fila en el PDF (¿es la de cunetas?, ¿da TR o
   riesgo y vida útil?). Si la fuente no lo sostiene, vuelve como pregunta.

## Cuarta sesión — decisiones del dueño del 2026-11-13

### T-7a punto 4 (sustituye a la decisión 4 de arriba, cuya premisa refutó la auditoría) — ~04:35 UTC: «estoy de acuerdo con tu plan»
- NO se abre sola la puerta de `ancho_derecho_via_m` en T-7a: V5 se detiene antes en el criterio vacío `remanso_derecho_via`,
  `M5.v5_remanso` no lee el dato (no hay método) y después V8 se detiene en `TR_evento_extremo`.
- T-7a entra en main con `INF-4.2` e `INF-4.3` **«en parte»** (residual: Fase 9 alcanzable a expediente, ficha T7A-01).
- **El método de V5 (embalse a nivel, como opción DECLARABLE sin valor por defecto) más la puerta del dato
  `ancho_derecho_via_m` van como PRIMER PUNTO de T-7b, implementado y auditado con Fable.** Sin el criterio declarado o sin el
  dato, V5 sigue bloqueando como hoy (ningún resultado del fixture cambia).

### Resoluciones del orquestador comunicadas al dueño el 2026-11-13 04:27 UTC (sin objeción; quedan barribles)
- T-3: `n_manning_cajon` → [C] fila `concrete_boxes` de HDS-5 Tabla B.1 (0.012, 0.015), con la del MTC como alternativa;
  `cobertura_minima_cajon` avisa en vez de bloquear (G1 del marco).
- T-9: `seccion_cuneta` = 0.40 × 1.20 m (Tabla 34 «muy lluviosa», verificada) con Z2 = 1.0 [A]; TR 35 años CONFIRMADO como
  envolvente (Tabla 02: riesgo 35 %, n = 15 → T ≈ 35.3); obras A como extremo de tramo por DG-2018 304.11, criterio conmutable;
  consecuencia declarada: VB1 de B-01 NO CUMPLE en el fixture (530 m desde A-02).

### Orientación del cabezal en cruces esviados — 2026-11-13 ~05:35 UTC: «sí, estoy de acuerdo»
- El cabezal queda **NORMAL AL EJE DEL CONDUCTO como valor por defecto en las tres familias** (es lo que supone toda la hidráulica:
  ke y cartas de HDS-5; no mueve ningún HW ni diámetro). T-7b se hace con esa orientación.
- El cabezal **paralelo a la vía** queda como alternativa declarable SÓLO para el marco de la Familia C (Carta 11 de HDS-5),
  DIFERIDA con ficha a un paso posterior a T-7c: cambiaría la carta y el HW de C-01 y la orientación del muro frente al tráfico.
- Mientras tanto, el alero largo de C-01 (8.1 m con 30° de esviaje) se puede resolver declarando un α menor de ese lado por
  `cabezal_declarado` (aleros asimétricos): la memoria lo dice.
- T-7b verifica contra el PDF lo que HDS-5 núm. 5.4.2 dice de las embocaduras esviadas antes de escribirlo en la ficha.

### Decisiones del dueño del 2026-11-13 ~09:45 UTC — «sí, sigue con tus recomendaciones» (cierra todas las preguntas abiertas)
Confirmadas las resoluciones que el orquestador aplicó sin respuesta (T-7b: `drenaje_trasdos` = `sin_drenaje`; no iterar la zapata
del cabezal por ahora; sin reducción de k_h por desplazamiento + cuña de tanteo; V5 con `cota_de_afectacion`; T-3: n del marco de
HDS-5 y cobertura que avisa; T-9: Z2 = 1.0) y además:
1. **Flotación del marco (V7 sin peso propio, ficha T3-08)**: se deja como está; se revisa cuando llegue la sección real del canal
   de ANA / la Junta. No se toca en la cadena.
2. **VB1 de B-01 NO CUMPLE en el fixture (530 m)**: se deja; es el resultado honesto del ejemplo.
3. **Figuras 3.3–3.4 de HEC-14**: SÍ se digitalizan, en un prompt APARTE y DESPUÉS de T-12 (no antes: no mueve diámetros ni la
   protección adoptada). T-11/T-12 lo dejan dicho como trabajo posterior.
4. **T-5, confirmadas las tres**: `DatoFaltanteError` cuando a un punto sólo le falta un dato de la Fase 8; pandeo del HDPE con el
   mayor de las dos lecturas; la tubería empernada de EG-2013 507.02 a) detiene (la alternativa de diferirla a perfil con aviso
   sólo si se consigue la tabla del fabricante).
5. De T-8 quedan confirmadas por la misma respuesta las recomendaciones dadas en la sesión anterior: `max(V_c, V_erosion)` en la
   banda de régimen de M4 → trabajo posterior junto con el punto 3 (no se toca M4 en la cadena); fuera de la Tabla 10.1, cotas
   inferiores + aviso (como está); 360 min (como está).

### Verificación Fable de las correcciones de fórmula de T-7b y T-7c — 2026-11-13 ~13:10 UTC: «estoy de acuerdo»
Las correcciones ALTA de fórmula de los cierres de T-7b y T-7c las implementó Opus (con especificación del orquestador y los
valores de control del auditor Fable). Cuando `tesis(T-7c)` esté en main se pasa UN verificador Fable corto, sólo lectura, sobre
esas correcciones de los dos cierres: T-7b — cota del nivel freático (H1), V5 `cota_de_afectacion` (H2), V8 con el barril a
presión (H3) (la cuña ya la aprobó el auditor de T-7c); T-7c — momento de pantalla y alero (H1), k_h0 para el armado (H2),
fisuración 5.6.7 (fórmula nueva), d_v acotado, modificador η en el cabezal. Si encuentra algo, lo corrige FABLE directamente
(commit propio `tesis(T-7): …` sobre main, con el ritual). T-10 arranca en paralelo (no toca cálculo).
