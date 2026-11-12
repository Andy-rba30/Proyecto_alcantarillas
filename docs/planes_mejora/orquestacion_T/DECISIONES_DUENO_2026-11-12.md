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

Pendientes de respuesta del dueño (T-9, recomendación del orquestador dada, NO aprobada todavía): valor de `seccion_cuneta`
(0.40 × 1.20 m), borde libre de la cuneta, TR de 35 años (a verificar por el auditor), obras A como extremo de tramo.
