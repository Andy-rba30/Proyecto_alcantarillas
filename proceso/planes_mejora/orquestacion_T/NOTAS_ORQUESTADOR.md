# Notas del orquestador (para encargos futuros)

## Aprobado por el dueño (2026-11-11)
- Familia B: conjunto de aceptación «V1 + V2 + V4 + V5 + espaciamiento de Fase 10» (v8 §2.3, ficha T0-03) -> cablear en T-9
  (`M1.PERFILES[Familia.B].verificaciones_aceptacion`), cuando M10 tenga verificación real.
- INF-5.1.8 (`area_ha` obligatoria en B sin consumidor) -> T-9.
- V5: sigue pendiente de entrada (`ancho_derecho_via_m`); método de remanso -> T-3 punto 2; censo -> T-11.
- Severidades INF- del tracker: aceptadas como «propuestas».
- Huérfanos ya enviados: INF-5.1.3 + V8 -> T-1; INF-3.2.5 + INF-3.2.9 -> T-2; INF-5.1.9 + INF-5.1.16 -> T-4.

## Erratas de la cadena (T-0)
- T-8: HEC-14 socavación = cap. 5 (no 3); velocidad de salida cap. 3; disipadores internos cap. 7.
- T-4: Tabla 8-4 WSDOT en 8-27 y 8-28.
- T-2: HDS-5 barril horizontal num. 3.3.4 pág. 3.25.

## Orden de integración lote 1 (serializar): T-2 -> T-4 -> T-1 -> T-6 (T-6 conecta S_conducto con criterios de T-2)

## Para el encargo de T-5 (del auditor de T-4)
- La plancha TMC 68×13/2.01 no cumple el factor de flexibilidad de ASTM A796 §10 (FF = s²/(EI) ≤ 0.245 mm/N) desde ~1.39 m:
  T-5 debe cerrar FF y calibre/corrugación TAMBIÉN a nivel de perfil (hoy la Fase 8 se difiere a expediente y un TMC Ø 1.95
  con 2.01 mm podría adoptarse). `espesor_pared` de TMC/HDPE es envolvente geométrica, no espesor estructural.
- HDPE 1350/1500 sin OD (LRFD A12-11 termina en 48 in); concreto > 2.70 m = diseño especial M 170M 7.2.
## Para el encargo de T-7a (del auditor de T-6)
- Longitud entre cabezales (construcción/metrado) se cierra con la coronación del cabezal; hoy la hidráulica usa L al fondo (cota superior).
## Para T-9: H3/H12 de T-1 (duración mínima de lluvia y C de pavimento) deben estar resueltos.

## PENDIENTE fuera de la cadena (dueño, 2026-11-12 ~17:15 UTC): armado del marco de la Familia C
Ningún prompt de la cadena diseña en concreto armado la SECCIÓN del marco (pórtico cerrado: momentos y cortantes en losas y muros,
acero por flexión, cortante, mínimo y de temperatura, fisuración). T-3 lo dimensiona hidráulicamente, T-5 entrega la demanda
(AASHTO 12.11) y un paso «diseño del pórtico: diferido al expediente»; T-7c arma el CABEZAL, no el cajón. El orquestador propuso
un prompt adicional (después de T-7c, reutilizando sus rutinas de flexión y cortante; una celda; AASHTO LRFD 12.11 y Sec. 5 /
E.060). **Decisión del dueño: queda como PENDIENTE; para la tesis basta el dimensionamiento.** No se lanza. T-11 (censo final) y
T-12 deben dejarlo dicho en `docs/decisiones_diferidas.md` y en el README como alcance declarado, no como omisión.
