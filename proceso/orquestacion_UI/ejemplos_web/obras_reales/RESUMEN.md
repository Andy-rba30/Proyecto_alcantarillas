# Obras reales con diseño de alcantarillas — resumen de búsqueda (actualizado 2026-11-15)

## Casos registrados (`obras.json`)
| id | tipo | obra | completo p/ recalcular | fuente y páginas |
|---|---|---|---|---|
| OR-US-WI-03 | hidraulica_circular | WisDOT, STH 32 Pulaski–STH 22, Oconto Co., proyecto 9190-26(27)-00: 9 cruces con tubo circular de concreto | **SÍ** (hidráulica HDS-5/HY-8; sin hidrología) | trust.dot.state.wi.us, reporte HY-8 71 pp.; tablas por cruce en pp. 4-68 |
| OR-PE-TU107-04 | hidrologia_racional (+tiempo_concentracion, frecuencias) | Vía departamental TU-107 Bocapán–Tamarindo, Tumbes: 41 cuencas, serie P24 de Cañaveral, Log Normal 2P, IDF, Q racional TR 35/70/140 | **SÍ** (con reservas sobre la serie de lluvia) | tesis UNT 2026, tablas 23-27, 36, 47-50, 65-67; pp. impresas 60-93 |
| OR-PE-TU107-05 | hidraulica_circular (capacidad a sección llena) | Mismo estudio: 11 alcantarillas TMC/marco existentes, Manning n=0.024, S=0.02 | NO para HDS-5 (no hay HW, ke, L, TW) | Tabla 68, p. 95-96 |
| OR-PE-QUERARI-06 | frecuencias | Puente Querari, CU-1430, Marangani, Cusco (expediente IOARR 2024): serie P24 Sicuani, K-S, IDF, Mac-Math | NO (inconsistencias internas graves) | apps.proviasdes.gob.pe, Cuadros 12-26 |
| OR-US-DALE-01 | hidraulica_circular | Dale Boulevard (VA), dos tubos de concreto en serie; ensayo de laboratorio | NO (fuera de HDS-5) | FHWA-RD-01-095 |
| OR-US-MN-02 | otro | 50 alcantarillas de Minnesota; geometría y Q pico; HY-8 sólo desborde/umbrales | NO | MnDOT 2021-29 |

PDF en `pdf/`: WisDOT HY-8, tesis UNT TU-107, Querari, FHWA-RD-01-095, MnDOT 2021-29.

## Verificación de consistencia interna (resumen; detalle en `notas` de cada caso)
- WisDOT: pendiente = (invert ent. − invert sal.)/L coincide en los 9 cruces; HW = invert + profundidad gobernante (máx. entrada/salida) coincide (≤0.01 ft). Reserva: el canal de salida es idéntico en los 9 cruces (ancho 8 ft, pendiente 0.33, n 0.029), parece genérico; el TW casi no influye. Sin hidrología (Q es dato). El propio reporte señala que en el Cruce 3 HW excede 2.6 in la subrasante asumida.
- TU-107: Q = C·I·A/3.6 recalculado reproduce los 36 caudales dentro de ±3 % (redondeo de área); los cuantiles Log Normal 2P de 5 y 10 años recalculados (278.3 y 412.7 mm) coinciden con los publicados; el diámetro calculado de la Tabla 68 sale de Q = 1.5·D^(8/3) en las 11 filas. Hallazgos: P24 de hasta 729 mm/24 h y filas de la Tabla 23 repetidas (1996/2001, 1989/2002) sugieren totales mensuales o datos copiados; la capacidad de los marcos no se reproduce con el Manning declarado (razón 0.60-0.71 respecto a sección llena) y usa n de acero corrugado.
- Querari: la serie ordenada (45-185 mm) es incompatible con el P24 de T=2 de 36 mm del Cuadro 21, y el Cuadro 25 usa otros P24 (29.2 mm) que el Cuadro 21; Q no recalculable.

## Fuentes miradas y descartadas
- Descartadas por no ser obras reales: manuales (WSDOT M 23-03, TDOT, FHWA HDS-5, HY-8 tutorial, MTC), plantillas de reporte. Excluidos por regla: Scribd, SlideShare, PDFCoffee, idoc.pub (incluye «Estudio hidrológico-hidráulico Matacoto, Áncash» y «Diseño de una alcantarilla TMC»: reposteos, no usados).
- cdn.www.gob.pe: Oyón–Ambo (sólo inventario TMC/MCA sin Q ni verificación), ayuda memoria Bellavista–Mazán, normas CE.040/OS.060: sin datos de cálculo.
- UNI (Cañete–Yauyos–Huancayo, tesis Pomacaja 2009 y Pérez 2010): el PDF requiere autenticación (401). rosap/MnDOT usados, otros informes FHWA son laboratorio.
- **Provías Nacional** (`gis.pvn.gob.pe` y `gis.proviasnac.gob.pe`, p. ej. «Alcantarilla Marco km 31+836.971», LP0024-2012, y los expedientes LP_02_2017, LP_0006_2020, Carretera Central «05. Hidrología e Hidráulica»): **no accesible**: el servidor sólo sirve HTTP y el proxy sólo admite túneles HTTPS (https: conexión reiniciada; http: no resuelve/503). Son los candidatos más valiosos para Perú; requieren acceso HTTP al puerto 80 o un espejo.
- Maine DOT `hr018283.00.pdf` (HY-8 de una alcantarilla existente y su reemplazo de 3 marcos 13'x3'; solo pude comprobar por el buscador, no lo pude descargar: 403 a curl) y un reporte HY-8 en documents.dps.ny.gov / mansfield.civicweb.net (municipal): sin revisar; candidatos pendientes.
- WSDOT no publica los Hydraulic Design Reports de proyecto en su sitio (sólo plantillas).
- Otros hosts bloqueados en rondas previas: transparencia.mtc.gob.pe (502), core.ac.uk (Cloudflare), asotincd.org (Cougar Creek BOD, WSDOT fish passage), securedemo.rco.wa.gov.
