# Prompt N1 — Incorporación de ASTM A796/A796M-13 al registro

**Prerrequisito:** el PDF debe estar ya en `normas/` en `main` (subido vía
GitHub web). Verifica antes de abrir la sesión que aparezca en
https://github.com/Andy-rba30/Proyecto_alcantarillas/tree/main/normas

**Configuración:** Fable 5 · esfuerzo high · plan mode activado.
**Al aprobar su plan, vigila:** que la resolución de DIS-HR-A807 salga de lo
que la tabla del PDF DIGA de verdad (verificado), no del «gana» que la
discrepancia traía anotado como provisional.

Pega desde aquí hacia abajo como primer mensaje de la sesión nueva:

---

Antes de tocar código: entra en plan mode / propón tu plan y espera mi aprobación.

Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md (reglas de corrección
de hallazgos incluidas: tracker .xlsx, conflictos vinculantes, subagentes).
El dueño consiguió una de las dos fuentes ausentes más valiosas y ya está
en normas/: «ASTM A796-A796M-13 Structural Design of Corrugated Steel Pipe,
Pipe-Arches, and Arches.pdf». Datos del ejemplar, medidos: edición 2013
(el censo de FUENTES_AUSENTES suponía la 2019 — se registra la que ES),
21 páginas, SHA-1 df7858f04caf61bc1c3a4ea3d664e38cacddee25, primera página
en blanco, y capa de texto DUPLICADA (cada línea aparece dos veces —
artefacto de compresión/OCR): la verificación de texto literal necesitará
normalización o método IMAGEN, como M 36 y A760. La otra fuente ausente
top (AASHTO M294, HDPE) sigue faltando: nada de lo suyo se toca.

Tarea, en orden:
1. Incorporar la fuente al registro: ASTM_A796 pasa de FUENTES_AUSENTES a
   FUENTES en src/normativa/fuentes.py, como Fuente presente con
   archivo_pdf, sha1 (el de arriba — verifícalo tú mismo con la
   herramienta de extracción), paginas_pdf, paginación medida
   (extraccion cabeceras), edicion 2013, y texto_extraible según lo que
   midas (el texto existe pero duplicado — decide con el precedente de las
   fuentes raster si se declara extraíble o va por imagen, y déjalo dicho
   en la nota). Revisa qué citas/notas del registro decían «A796 ausente»
   y actualízalas a pretérito donde dejen de ser ciertas.
2. Con verificador-normativo, localizar y transcribir como TablaNormativa
   la(s) tabla(s) del A796 que fijan la ALTURA MÍNIMA DE COBERTURA y el
   CALIBRE (espesor) del TMC por cobertura — lo que NOR-PRO-04(2) declaró
   bloqueado por esta fuente. Transcripción COMPLETA (regla dura de la
   casa), verificada contra el PDF.
3. Cerrar lo que la fuente destraba, cada cosa por su vía:
   a. NOR-PRO-04(2) — el calibre TMC por cobertura: con la tabla
      transcrita, evalúa si el hallazgo cierra del todo; actualiza su
      ficha y el tracker matriz_cruzada_auditorias.xlsx (openpyxl
      preautorizado).
   b. DIS-HR-A807 — la discrepancia viva que esperaba esta fuente: ahora
      sus partes PUEDEN llevar cita. Transcribe las citas, decide el
      «gana» con la fuente en la mano (el «gana» asertivo anotado era
      provisional — la fuente decide, no el anticipo), y si procede
      corregir la v8 (Fase 8, el calibre), sigue el protocolo de I2:
      edición quirúrgica con nota «Corregido (…)» y cita verificada;
      revisa la cascada de guardias (paso/criterio que la declare) como
      hizo I2.
   c. La mitad TMC de clases_producto_por_relleno: si la tabla nueva la
      sostiene, complétala por la vía del registro (uso/condiciones), sin
      inventar nada que la tabla no diga.
4. Lanza auditor-adversarial sobre el conjunto antes de fusionar, con
   veredicto por pieza (regla 3). Regenera manifiestos y línea base si
   corresponde, con diff declarado.

Reglas duras: cero valores inventados (lo que la tabla no traiga, queda
declarado como sigue faltando); ningún valor de cálculo cambia salvo que
una tabla verificada lo exija — y en ese caso, dilo en el plan ANTES y va
en commit separado con su caso patrón; AASHTO M294 sigue ausente y su
censo no se toca.

Cierre: suite en verde; commit «normativa(N1): ASTM A796/A796M-13
incorporada — <qué cerró>»; entrega en origin/main; conteo como par
passed+skipped=collected desde origin/main, con el entorno (PyMuPDF sí/no,
Tk sí/no).
