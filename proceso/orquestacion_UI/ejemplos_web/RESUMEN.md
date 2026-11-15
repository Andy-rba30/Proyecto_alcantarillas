# Resumen: ejemplos web de alcantarillas (segunda pasada, con red)

Datos en `ejemplos.json` (10 registros). PDF descargados en `pdf/`, texto extraido junto a ellos.
Todo recalculado cuando fue posible; nada inventado (lo no publicado esta como null o dicho en notas).

| id | tipo | origen | fuente | completo para recalcular |
|---|---|---|---|---|
| TDOT-EX1-circ-mano | hidraulica_circular | manual_oficial | TDOT Drainage Manual cap. 6, Ej. 1, pp. 6-73..6-80 | SI (HW entrada/salida, dc, ho, H, vel.; lecturas de nomograma aprox.) |
| TDOT-EX2-circ-HY8 | hidraulica_circular | manual_oficial | TDOT cap. 6, Ej. 2 (HY-8), pp. 6-81..6-90 | SI (tabla de 10 caudales con HW, normal, critico, TW, velocidad) |
| TDOT-EX4-circ-S3pct-HY8 | hidraulica_circular | manual_oficial | TDOT cap. 6, Ej. 4, pp. 6-94..6-100 | PARCIAL (HW 347.25 cuadrada; resto es entrada mejorada) |
| UNC-COCAHUAYCO-racional | hidrologia_racional | tesis | UNC, drenajes transversales Cocahuayco, Tabla 15 | SI para Q=CIA/3.6 (I inconsistente con su IDF) |
| UNC-COCAHUAYCO-Tc-Temez | tiempo_concentracion | tesis | idem | SI (3 casos, reproducidos) |
| UNC-COCAHUAYCO-alc36-French | hidraulica_circular | tesis | idem, pp. 90-91 | PARCIAL (metodo French, solo dc y Sc) |
| UPAO-JALCA-Gumbel-Pd | frecuencias | tesis | UPAO La Jalca, p. 94 / anexo 302 | SI (serie de 17 anios + parametros + XT; reproducido) |
| UPAO-JALCA-Tinas-Temez | hidrologia_racional | tesis | UPAO La Jalca, p. 267 | SI (Temez completo + Kirpich; reproducido) |
| UPAO-JALCA-cuneta1-Kirpich | tiempo_concentracion | tesis | UPAO La Jalca, pp. 107-108 | SI (trivial, Kirpich + IDF K,m,n) |
| UPAO-JALCA-alcantarillas-Manning | hidraulica_circular | tesis | UPAO La Jalca, pp. 121-123 | PARCIAL (solo Manning; unidad de S no publicada) |

Por tipo: hidraulica_circular HDS-5 completos: 2 (TDOT 1 y 2, mismo sitio); hidraulica_cajon: 0;
hidrologia racional/Temez completos: 2; tiempo_concentracion: 3 (Temez x3 casos, Kirpich); frecuencias (Gumbel): 1;
enrocado_salida: 0; espaciamiento_alivio: 0.

## Mas fuertes para contrastar
1. TDOT-EX2 (HY-8 con tabla completa, mismo sitio que el EX1 a mano): control de entrada, dc, TW, velocidad en 10 caudales.
2. UPAO-JALCA-Gumbel-Pd: serie completa y resultados; encadena con Tinas-Temez (Pd100=69.48 mm).
3. UPAO-JALCA-Tinas-Temez: Tc, K, KA, P, I, Po, C, Q y Kirpich, todos reproducibles.
4. TDOT-EX1: referencia a mano (nomogramas), tolerancia por lectura.

## Fuentes miradas y descartadas
- TDOT cap. 6 Ej. 3 (rebose de calzada): fuera del alcance del programa.
- CDOT Drainage Design Manual cap. 9: el enlace de la busqueda dio 404 (JSON) y no se hallo otro; no leido. Ruta alternativa: pagina del manual 2019 en codot.gov (no abierta).
- Guilford County NC cap. 5 (Ej. 5-1): host guilfordcountync.gov NO esta en la lista permitida (403 del proxy); ademas solo control de entrada.
- ESPOL T-70549 (cajon con HY-8, Ecuador): host dspace.espol.edu.ec / www.dspace.espol.edu.ec NO accesible (403 / ENOTFOUND); anotar para permitir.
- HY-8 Applications Guide (FHWA-EPD-87-101, rosap 54218): PDF escaneado sin texto y sin OCR instalado (tesseract ausente); 3 ejemplos (cajon, seccion irregular, barriles multiples) por leer a ojo.
- FHWA-RD-88-125 (HYDRAIN vol. VI, HY-8 documentacion): sin ejemplos numericos extraibles.
- HEC-5 (FHWA 1965): texto sin ejemplos extraibles (escaneo parcial).
- HEC-13 (entradas mejoradas, ej. doble 8x8) y HEC-14: fuera de alcance / ya usado.
- Tesis UNC Robles y Mashcon (T016): drenaje urbano sostenible e inundaciones; no alcantarillas.
- Scribd (MD-5, Georgia y otros): reposteo, descartado por politica.
- Tesis UNAM, USP Caraz (OS.060 urbano): no corresponden al Manual MTC.
- TDOT otros capitulos (04, 09): URL por adivinar devolvio 403; no se probo mas.
- No se encontraron en esta pasada: ejemplos de enrocado de salida (no HEC-14) ni de espaciamiento de alcantarillas de alivio con datos completos. Las cunetas de La Jalca no traen calculo de espaciamiento (los "espaciamiento" de la tesis son de armadura).

## Hosts a anotar
Faltan en la lista de red: guilfordcountync.gov, dspace.espol.edu.ec (y www.), nhi.fhwa.dot.gov. www.codot.gov esta permitido pero la URL citada da 404.
Nota: repositorio.upao.edu.pe y repositorio.unc.edu.pe son DSpace; se bajan por /backend/api/core/bitstreams/<uuid>/content y /server/api/core/bitstreams/<uuid>/content (la pagina handle es una SPA).
