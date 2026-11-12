# INFORME T-9 · FASE A — Espaciamiento de alivios con L hidráulico calculado

Rama `tesis/T-9`, worktree `/home/user/wt/T-9`, base `df1b23c`. **HEAD = `304cea6`**
(empujado a `origin/tesis/T-9`; tres commits `wip(T-9)`: `cd1dc30`, `97b602f`, `304cea6`).
**No se fusionó ni se empujó nada a `main`.** No se tocó el `.xlsx`, la tabla de conteos de
`CLAUDE.md` ni `verificar_sesion.py`.

## 1. IDs

| ID | Veredicto | Por qué |
|---|---|---|
| **INF-5.1.12** (la cadena lo llama «INF-5.1.11») | **Cerrado** | El paso 10.1 (`F10.CUNETA`) ya no dice «cumple»: es un límite, veredicto `SIN_VEREDICTO`. La verificación es **VB1** (`M10.verificar_tramo`), el espaciamiento ADOPTADO por tramo contra el máximo, y **puede fallar** (test con 2+450 / 2+700: 250 m > 200 m → NO_CUMPLE, margen −50 m, llega a `InformePunto.verificaciones()/incumplidas()`, RESUMEN, `cerrado`, CLI, JSON, memoria). |
| **INF-3.3.8** («INF-3.3 espaciamiento») | **Cerrado** | `L_hidraulico_m` declarado sigue ganando; si no viene, M10 lo calcula: capacidad de la cuneta (dos límites del núm. 4.1.2.1 a): cuneta llena por Manning ec. (117) con n = 1/K de la Tabla Nº 32, y caudal a la velocidad límite de la Tabla Nº 33 por las ec. (4.2)/(4.5)), q' = q·b/10⁶, L = Q_adm/q'. Falta algo → `DatoFaltanteError` dentro de `_etapa`. |
| **INF-5.1.8** (`area_ha` en B sin consumidor) | **Cerrado** (se mantiene obligatoria) | Consumidor real: con el caudal **declarado**, la Fase 10 usa q = Q/`area_ha` (escorrentía específica del área tributaria del alivio) para la longitud por capacidad; test: duplicar `area_ha` duplica L. Ya la leían el contraste Q/A y la coherencia de áreas de T-1. Contrato de entradas actualizado. |
| Aceptación Familia B (ficha T0-03) | **Cableada** | `PERFILES[Familia.B].verificaciones_aceptacion = ("V1","V2","V4","V5","VB1")`. Sigue siendo huella (SIS-B-13): test por AST de que ningún módulo lee el campo. |

## 2. Tests y par de la suite

- Nuevo `tests/test_t9_espaciamiento.py`: **82** tests (4 con marca `pdf`: citas y Tablas 32/33/34 contra el PDF). Más: +9 `test_familias_del_csv` (3 son saltos de DISEÑO: B usa las tres claves nuevas), +6 anclajes de fichas en `test_decisiones_diferidas`, +3 `test_ext5_forma_gui` (criterios nuevos), +1 `test_guia_perfil` (ejemplo `--declarar seccion_cuneta`), +1 `test_criterios_adoptados`. **Total +102 collected.**
- Rojo: escritos **después** del código; medido contra árbol exportado de `df1b23c` con `xfail(strict=True)` de módulo: 81/82 en rojo, 1 XPASS (guardia «M10 no importa MH», vale antes y después). Ficha T9-06.
- **Par medido (HEAD 304cea6, PyMuPDF sí · Tk no · `NORMAS_DIR` enlazado): 5059 passed / 19 skipped / 5078 collected** (base 4960/16/4976; los 3 saltos nuevos son de diseño de `test_familias_del_csv`). Sin `NORMAS_DIR` no medido.
- Tests reescritos (sin restar): `test_M1_clasificacion` (B con VB1 + AST), `test_t0_gobernanza` (B ya no None), `test_criterios_adoptados`/`test_cierre_perfil` (`seccion_cuneta` entre los vacíos de perfil), `test_sin_literales` (censo: M10 = 2 marcas), `test_memoria_sustentada` (recorrido de pasos de la Fase 10 y F10.* no alcanzados), `test_ayuda_entrada`/`test_ext5_forma_gui` (17 externos no columna), `test_familias_del_csv` (valores de prueba).

## 3. Línea base — números movidos

`tests/linea_base_familia_c/` regenerada y medida con el comparador de E-B contra `df1b23c`: cambian `criterios_sha1`, `hoja_ruta_sha1` (notas de la v8), recuento 102/35 → 105/36, clave `tramo_alivio` (null salvo B-01), en B-01 el texto del bloqueo de la Fase 10 y un aviso «VB1 NO SE EVALUO» (única obra B, sin extremo). **Ningún número de cálculo.** Corridas de `docs/guia_perfil.md` (7 comandos) en las dos ramas: mismos códigos de salida y mismos diseños. **Diámetros movidos: ninguno** (A-01, A-02 Ø 0.90; B-01 y C-01 dimensionan/se detienen igual en las tres corridas de la línea base; en la guía los cuatro igual). README de la línea base con sección T-9.

## 4. Diferido / pendiente (con símbolo)

- `seccion_cuneta` [A] **sin valor de archivo** (ventana: d 0.20–0.60, a 0.50–2.40, talud ext. 0.10–2.0 H:V, borde libre 0–0.10 m): `criterios_adoptados.py::seccion_cuneta`, ficha T9-01. Lo destraba la sección típica del trazo (DG-2018).
- Datos externos nuevos (Familia B, trazo, opcionales, sin defecto): `ancho_tributario_m`, `S_cuneta`, `inicio_tramo_cuneta_km` (21 en `CLAVES_EXTERNAS`).
- Criterios con valor: `revestimiento_cuneta` [A] = concreto (núm. 4.1.2.1 y su e)), `lectura_velocidad_limite_cuneta` [A] = extremo_inferior.
- Fichas (Parte XLVI provisional): T9-01 sección/borde libre, T9-02 escorrentía e intensidad no iterada, T9-03 VB1 por tramo (obras A no son extremo salvo declarado), T9-04 ec. (4.1),(4.3),(4.4),(4.6) del Manual erróneas (no se usan), T9-05 pendiente de cuneta (Manual 0.5–2 % vs DG-2018 0.2 %), T9-06 rojo. T0-03 anotada como cerrada para B.
- Sección trapezoidal/rectangular de cuneta no implementada.

## 5. Fuentes verificadas por mí contra el PDF (texto + imagen)

Manual de Hidrología (desfase +3): 4.1.2 a) p.171/PDF174; 4.1.2 c) p.172/175 («0.5 % < i < 2 %», EXIGENCIA); 4.1.2.1 p.173/176 (triangular preferente; concreto); a) p.174/177 (dos límites, ec. 117); Tablas 32 y 33 p.175/178; ec. (4.2)/(4.5) p.176/179; b) p.177/180 (Q = CIA/3.6); Tabla 34 p.178/181; d) p.179/182 (250 «será … como máximo», 200 «se recomienda»); e) p.180/183 («deben ser revestidas», concreto 175 kg/cm² recomendado). DG-2018 (desfase +1): 304.10 Tabla p.204/205; 304.11 p.208/209. 11 citas nuevas (`tesis/T-9`), 3 `TablaNormativa` (T32, T33, T34), 4 fundamentos (F10.CAPACIDAD/APORTE/L_HIDRAULICO/TRAMO). Dorados a mano: d 0.30, a 0.75, Z2 1, S 0.01 concreto → Q_llena 0.267789 m³/s, V 1.700 m/s; q 30.024, b 12 → L 743.26 m; tierra arena fina → Q_v 4.2909e-4 (gobierna velocidad).

## 6. Filas del tracker a escribir en FASE B

- **INF-5.1.12** Cerrado — VB1 por tramo puede fallar; paso 10.1 sin veredicto; `M10.verificar_tramo`.
- **INF-3.3.8** Cerrado — L_hidraulico calculado (M10.capacidad_cuneta/longitud_hidraulica), declarado gana; `seccion_cuneta` [A] sin valor (entrada del trazo).
- **INF-5.1.8** Cerrado — `area_ha` obligatoria en B con consumidor real (Fase 10, q = Q/A con Q declarado); nota en «Vínculos».
- `LO_QUE_ESCRIBIO_CADA_PROMPT` de `test_t0_gobernanza`: fila de T-9 con esos tres IDs (al integrar).

## 7. Preguntas para el dueño (ninguna PARADA obligatoria se disparó)

1. **Sección de la cuneta.** La dejé sin valor (es del trazo). Propuesta si se quiere valor: mínimo Tabla Nº 34 «muy lluviosa (1600–3000)» 0.40 × 1.20 m (coherente con los 200 m de `long_max_cuneta` por FEN), talud exterior = talud de corte del EMS. ¿Valor o sigue pendiente?
2. **Borde libre** (v8 Fase 10 «con borde libre», sin cifra; el Manual: cuneta llena). ¿Cifra en la v8, o se retira la frase? Hoy es campo [A] 0–0.10 m.
3. **TR de la cuneta**: se usa el del punto B (35 años, fila «descarga de agua de cunetas», la que fija la v8); la fila «Drenaje de la plataforma (a nivel longitudinal)» daría ≈30 años. ¿Confirma 35?
4. **Extremos del tramo**: hoy sólo obras B o `inicio_tramo_cuneta_km` declarado; ¿las obras A cuentan como desagüe por defecto?
5. Premisa del orquestador corregida: la Fase 10 **no** era de nivel expediente: `long_max_cuneta` es NIVEL_PERFIL y M10 corre a perfil; los tres criterios nuevos son de perfil y su nivel lo mide una corrida de perfil en `test_t9_espaciamiento`.

## 8. Lo que no hice

- No medí el par sin `NORMAS_DIR` ni las configuraciones con Tk / sin PyMuPDF.
- No iteré tc con la longitud de la cuneta (ficha T9-02; el veredicto de VB1 es exacto igual).
- No escribí la fila de T-9 en `LO_QUE_ESCRIBIO_CADA_PROMPT` ni el párrafo de CLAUDE.md (FASE B).
- No corrí auditor adversarial ni mutación sobre M10.
- Documentos generados regenerados con sello provisional (commit 97b602f+cambios); se regeneran al integrar.
