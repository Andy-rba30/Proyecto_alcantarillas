# Encargo T-5 (estructural del conducto: Fase 8 real) — MODO PARALELO, FASE A

Worktree `/home/user/wt/T-5`, rama `tesis/T-5` (base `7fb7926` = T-0 + T-2 + T-4). Otros agentes integran T-1 y T-6 en `main` y otro
trabaja T-8: no toques sus worktrees ni `/home/user/proyecto_alcantarillas` (checkout de `main`).

PRIMERO lee entero `/tmp/claude-0/-home-user/8c9a9d01-15e4-5a10-91d4-d894b414664c/scratchpad/ORQUESTACION.md` (rutas, entorno con
`NORMAS_DIR`, reglas no negociables, paradas, decisiones del dueño, LECCIONES de las auditorías, FASE A/FASE B, commit e informe).
Después, en el worktree: `CLAUDE.md` ENTERO, la nota del orquestador y la §2 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`,
`docs/contrato_entradas.md`, las fichas T4-01, T4-02 y T4-08 de `docs/decisiones_diferidas.md` (son tu entrada), y del INFORME
(`/home/user/andy-rba30/cotas-esviaje-alcantarillas/INFORME_evaluacion_app_alcantarillas_vs_PDF.md`) §0, §1.1, §2, §3.3, §5.1.

## El prompt, tal cual (bloque T-5 de la cadena)

```text
Ejecuta únicamente T-5 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.3 "carga viva / clase / relleno máximo" e INF-5.1.5 "Fase 8 no verifica nada". Fuentes: AASHTO LRFD 9.ª: 3.6.1.2.6 (distribución de la carga viva a través del relleno), 3.6.2.2 (impacto en estructuras enterradas), 12.6 (general, cobertura mínima 12.6.6.3), 12.7 (metal corrugado: empuje de anillo, área de pared, pandeo, costuras, factor de flexibilidad, 12.7.2.x), 12.10 (tubería de concreto: método indirecto por D-load con factor de cama, 12.10.4.3), 12.11 (box), 12.12 (termoplástico: empuje, pandeo, deformación); AASHTO M 170M Tablas 1–5 (clases I–V por D-load); ASTM A796 §7–§11 (procedimiento de diseño de TMC: el mismo que el PDF de VARIOS aplica en pp. 50–66 con el CSPI, útil como caso de comprobación numérica: D 0.90 m, H 0.30 m, DL 4.5 kPa, LL 86 kPa H-20, C 40.7 kN/m, A 0.354 mm²/mm); AASHTO M 294; EG-2013 505–508 (camas, rellenos, compactación 95 %). Manual de Puentes 2.4.3 (HL-93).

1. Carga de tierra sobre el conducto (AASHTO 12.10.2 / 12.7.2 según material, con factor de interacción suelo-estructura Fe = 1 + 0.20·H/Bc donde AASHTO lo prescribe) y carga viva HL-93 distribuida a través del relleno (3.6.1.2.6 con impacto 3.6.2.2), ambas como PasoDeMemoria con fórmula sustituida. Altura de relleno real por punto = cota_subrasante − cota de clave (ya existe M5.altura_relleno_sobre_clave) más el paquete estructural donde corresponda.

2. Concreto: clase por D-load (M 170M Tablas 1–5 transcritas a constantes_normativas con página; clases_producto_por_relleno deja de ser None) con factor de cama por tipo de instalación (AASHTO 12.10.4.3, Tabla de factores de cama; tipo de instalación como [A] con ventana, por defecto el más desfavorable que EG-2013 admita). Resultado: clase mínima requerida y relleno máximo admisible por clase.

3. TMC: procedimiento de A796 / AASHTO 12.7.2: empuje de anillo, área de pared requerida vs tabla de M 36 (T-4), pandeo, resistencia de costura, factor de flexibilidad, relleno mínimo y máximo. Caso de comprobación: el ejemplo del PDF de VARIOS (valores arriba) debe reproducirse dentro de tolerancia declarada, con la salvedad de que el PDF usa H-20 y la app HL-93 (documentar la diferencia).

4. HDPE: AASHTO 12.12 (empuje, pandeo, deflexión 5 %) con M 294.

5. Marco: AASHTO 12.11 (cargas sobre losa y paredes); el diseño de la sección del marco (momentos, As) sigue fuera del alcance (hoja de ruta): deja la demanda calculada y un PasoDeMemoria "diseño del pórtico: diferido al expediente, demanda en kN·m/m".

6. Elimina los AssertionError("inalcanzable") de M8 sustituyéndolos por las rutas reales; verificacion_diferida_estructural pasa a imprimir solo lo que de verdad siga diferido.

Tests: un dorado por material calculado a mano con página; test de que la Fase 8 produce al menos una Verificacion con cumple ∈ {True, False} por material candidato (hoy produce cero).

Ritual de cierre.
```

## Precisiones del orquestador

- IDs canónicos: lo que el prompt llama `INF-5.1.5` («Fase 8 no verifica nada») es **`INF-3.3.5`** (el `INF-5.1.5` canónico es «mezcla
  de marcos», de T-7b: NO lo cierres); «INF-3.3 carga viva / clase / relleno máximo» son las `INF-3.3.k` que T-0 te asigna; `INF-5.2.6`
  lleva una nota de T-4 que te nombra. Hoja `Hallazgos` sólo lectura en FASE A (`tests/apoyo/tracker.py`).
- **Lo que T-4 dejó y debes consumir (no re-transcribir):** `constantes_normativas.TMC_PLANCHA_CORRUGADA` (clave `"68x13/2.01"`:
  `A_mm2_mm`, `I_mm4_mm`, `r_mm`, `espesor_m`, `profundidad_m`; 17 planchas 68×13 y otras corrugaciones), `DIAMETROS_ESTANDAR_TMC`,
  criterio `corrugacion_y_espesor_tmc`, `M2.espesor_pared_de_tmc`, `M2.tope_de_diametro`, tablas del registro `ASTM_A796.T5/T7/T9`,
  `AASHTO_M36.T1/T6/T7`, `AASHTO_LRFD_9.TA12-11` (A, c, I mínimos de PE), `AASHTO_M170M.T5`,
  `DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM` (2700). **`espesor_pared_conducto` de TMC/HDPE es una ENVOLVENTE geométrica
  (exterior − interior), no un espesor estructural: no la uses como sección resistente.**
- **Entrada obligada (ficha T4-08, hallazgo del auditor de T-4):** la plancha 68×13/2.01 NO cumple el factor de flexibilidad de ASTM
  A796 §10 (FF = s²/(E·I) ≤ 0.245 mm/N en terraplén, 13 mm de profundidad; I = 39.20 mm⁴/mm, E = 200 000 MPa → s máx ≈ 1.386 m) y el
  catálogo la ofrece hasta 2.10 m; y hoy la Fase 8 se DIFIERE a nivel de perfil, de modo que un TMC Ø 1.95 con 2.01 mm podría adoptarse.
  Ciérralo: decide con la fuente y con «Nivel de entrega» de CLAUDE.md qué parte de la verificación estructural corre también a PERFIL
  (como mínimo lo que decide si la combinación material/diámetro/plancha/clase EXISTE: FF, área de pared, pandeo, clase D-load
  disponible) y cómo se elige plancha/corrugación/clase (progresión dentro de la tabla hasta que cumpla, o `DisenoNoFactibleError` con
  motivo). **PARADA (c):** adoptados del fixture: concreto Ø 0.90 m (A-01, A-02) y, donde dimensionan, B-01 Ø 0.90 y C-01 marco
  1.20×0.90. Si correr la Fase 8 (a perfil o a expediente) cambia material, diámetro o el «dimensionado» de un punto de la línea base,
  NO lo actives por defecto: impleméntalo, mide antes/después y devuelve la pregunta para el dueño. Ganar verificaciones estructurales
  con cumple=True en la memoria es movimiento declarado, no parada.
- **Marco LRFD:** el proyecto es AASHTO LRFD de extremo a extremo y el dueño confirmó LRFD. La Sec. 12 rige el conducto (factores de
  carga de 3.4.1 / Tabla 3.4.1-2 para EV por tipo de estructura enterrada; factores de resistencia de la Tabla 12.5.5-1; η). ASTM A796
  es ASD: úsala para procedimiento/propiedades y como contraste, pero NO mezcles en una misma comprobación γ de LRFD con FS de A796;
  declara qué marco rige cada verificación. Verifica en el PDF el numeral REAL de cada cosa (los que cita la cadena pueden no coincidir:
  gana la fuente y se declara).
- **Carga viva:** HL-93 (camión y tándem; carril según 3.6.1.2.6 / 3.6.1.3 para enterradas), LLDF de la Tabla 3.6.1.2.6a-1 (la 9.ª
  partió 3.6.1.2.6 en a/b/c), impacto 3.6.2.2 IM = 33·(1 − 0.125·D_E) ≥ 0 con D_E en pies en el original (conviértelo, sufijo `_SI`),
  presencia múltiple. Todo en SI; valor imperial en comentario.
- **«Caso de comprobación» del PDF de VARIOS:** ese PDF NO está en la sesión. Los valores (D 0.90 m, H 0.30 m, DL = 15·0.30 = 4.5 kPa,
  LL 86 kPa H-20 —Tabla 6.8 del CSPI—, Pv 90.5 kPa, C = Pv·S/2 = 40.7 kN/m, D/r 207 < 294 → fb 230 MPa, fc 115 MPa, A = 0.354 mm²/mm,
  FF 0.109 < 0.245) los da el INFORME §1.1: úsalo como dorado de ARITMÉTICA del procedimiento de A796 con esas entradas, citado «según
  el INFORME §1.1; páginas del PDF original no verificadas en esta sesión», y documenta H-20 vs HL-93.
- **Entradas que no se inventan:** tipo de instalación/cama y compactación (numerales reales de EG-2013 505–508), módulo del relleno
  (Tabla 12.12.3.5-1), resistencia de costura (tabla de A796/M 36 si la trae; si no, vacío declarado), propiedades de largo plazo del PE
  (Tabla 12.12.3.3-1), paquete estructural del pavimento. Elección → [A] con ventana y el más desfavorable admisible por defecto;
  dato → entrada opcional sin valor por defecto; tabla → transcrita con página y test.
- Marco (punto 5): la sección del marco la define T-3 (no integrado: los criterios del cajón siguen vacíos); implementa 12.11 contra la
  interfaz actual de modo que con los criterios del cajón declarados corra, y sin ellos el bloqueo sea el `CriterioPendienteError` de siempre.
- `M8` tiene consumidores en M5 (V7 importa `peso_relleno_kn_m` y `CRITERIO_FACTORES_CARGA`): no rompas V7 ni su línea base.
- Zonas calientes: `criterios_adoptados.py` (88 criterios), `constantes_normativas.py`, `modelos.py`, `servicio.py`, `M11_reporte.py`,
  `normativa/{citas,tablas,fundamentos}.py`, `decisiones_diferidas.md` (Partes XLI–XLIV ocupadas: rótulo provisional), v8, `CLAUDE.md`,
  `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`. Bloques `# --- T-5 ---`; no reordenes nada ajeno. Tu módulo: `src/modulos/M8_estructural.py`.

Al terminar la FASE A (suite entera verde en tu rama con `NORMAS_DIR`, commits intermedios frecuentes —puede haber cortes por límite de
uso—, SIN tocar xlsx / tabla de CLAUDE.md / `verificar_sesion.py`, SIN fusionar ni empujar, NUNCA `git stash`), devuelve el informe con
el formato de ORQUESTACION.md, con las filas del tracker y el antes/después de material/diámetro por punto. No ejecutes ningún otro prompt.
