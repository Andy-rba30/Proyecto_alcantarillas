# Precisiones del orquestador para T-7b (cabezal: ensamble de estabilidad en un solo marco) — cuarta sesión

Base: `origin/main` con T-3, T-9 y T-7a integrados (el orquestador te da el SHA). Lee `ORQ/ORQUESTACION.md` (con su ENMIENDA DE LA
CUARTA SESIÓN), `ORQ/DICTAMEN_marco_cabezal.md` ENTERO (re-verifica cada cita antes de escribirla), `ORQ/AUDITORIA_T-7a.md` y
`ORQ/INFORME_T-7a_final.md` (lo que T-7a dejó y sus residuales), y la sección «Cuarta sesión» de `ORQ/DECISIONES_DUENO_2026-11-12.md`.

- **IDs canónicos**: `INF-4.4`, `INF-4.5`, `INF-5.1.5` (aquí el número de la cadena SÍ es el del INFORME), las fichas EXT-7-01..04
  de `docs/decisiones_diferidas.md`, y —por el punto 0 de abajo— el residual de `INF-4.2` / `INF-4.3` (ficha T7A-01) y las filas
  del tracker que nombren V5 / `remanso_derecho_via` (búscalas con `tests/apoyo/tracker.py`; sólo lectura en FASE A).
- **Marco (decisión del dueño, PARADA (a) ya resuelta): OPCIÓN (b)** — rige LRFD AASHTO 11.6; la verificación ASD de E.050 se
  calcula e imprime EN PARALELO sobre cargas de servicio; cuál rige y la regla de desempate son [A] con justificación; nunca se
  cruzan los marcos (regla de no cruce del dictamen). E.050 para un cabezal vial es **[N→]**, no [N] (T-7a ya movió el Art. 26.2).
  No escribas «la norma exige LRFD para cabezales», ni «φ = 1.0 en evento extremo» a secas, ni «E.050 [N]».

## PUNTO 0 (decisión del dueño del 2026-11-13) — V5 con método declarable y la puerta de `ancho_derecho_via_m`
Hoy ninguna corrida de expediente llega a la Fase 9 por la ruta real: (1) `remanso_derecho_via` es un criterio [A] vacío y MD se
detiene ahí; (2) declarado, `M5.v5_remanso` levanta SIEMPRE `DatoFaltanteError('ancho_derecho_via_m')` sin leer el dato, porque no
hay método; (3) después V8 se detiene en `TR_evento_extremo` y en el caudal del evento extremo (ficha T1-03). Tu test «ningún punto
dimensionado sale de Fase 9 sin E1–E3 evaluadas» necesita esa ruta. Implementa, ANTES del ensamble:
1. **El método de V5 «embalse a nivel» como opción DECLARABLE, SIN valor de archivo**: el criterio `remanso_derecho_via` sigue con
   `valor=None` (sin declararlo, V5 bloquea como hoy con `CriterioPendienteError`: ningún resultado del fixture cambia) y pasa a
   elegir el MÉTODO (categoría con su ventana; `embalse_a_nivel` es hoy la única opción implementada; «perfil de remanso paso a
   paso» queda nombrada como diferida). El método: el nivel del embalse es horizontal a la cota del HW de M4; su extensión aguas
   arriba es donde ese plano corta el fondo del cauce (HW / S_cauce, con la geometría de M7 para situar la boca respecto del eje y
   el esviaje para proyectar); se compara con el límite del derecho de vía de ese lado. Antes de escribir una fórmula: lee la
   fila V5 de la v8 y el DG-2018 304.07 (ya en el registro), decide QUÉ distancia se compara con QUÉ ancho (¿el dato es el ancho
   total y la faja se toma simétrica al eje —supuesto a declarar como `Interpretacion`—, o la distancia del eje al límite del lado
   de aguas arriba?), busca en HDS-5 lo que sostenga el embalse a nivel (almacenamiento aguas arriba / «ponding», «storage
   routing») y cítalo con página, o decláralo [A] sin atribuirlo. Di en el paso TODO supuesto (plano horizontal: no es la curva de
   remanso; no hay topografía lateral; el M1 real se extiende más allá con tirantes mayores que el normal) y hacia qué lado sesga.
   Con cauce de pendiente fuerte o nula, o S_cauce no positiva: `MetodoNoEvaluableError`/guardia MAT-D13, nunca una cifra.
2. **La puerta del dato**: `ancho_derecho_via_m` como dato externo por punto (`servicio.CLAVES_EXTERNAS`, forma y dominio en
   `dominios.py`, pre-vuelo «espera/detiene» diciendo la verdad, `familias_que_usan` = A y B; la Familia C no usa V5), opcional y
   SIN valor por defecto; sin el dato y con el método declarado → `DatoFaltanteError` como hoy. El piso de la Tabla 304.09 del
   DG-2018 (+5.00 m de 304.07.02) se imprime como contraste del dato declarado (aviso si el dato queda por debajo), no lo sustituye.
3. **V8**: no inventes TR ni caudal del evento extremo; en tu test de ruta real se DECLARAN (criterio y dato externo, rotulados
   «de prueba»). Si para evaluar V8 falta algo más que entradas, dilo.
4. **Test de punta a punta**: una corrida `--alcance expediente` con todo declarado (método de V5, `ancho_derecho_via_m`, TR y Q
   del evento extremo, los [S] geotécnicos y sísmicos que tu ensamble pida, de prueba y rotulados) en la que A-01 llega a la Fase 9
   por `servicio.correr` (no llamando a `_fase_9` a mano) con E1–E3 evaluadas. Con eso `INF-4.2` e `INF-4.3` pasan a cerrados.
   V5 PUEDE fallar (test con un derecho de vía estrecho) y el HW/diámetro del fixture NO se mueve (sin declarar nada, todo igual).

## Lo que T-7a te deja (consúmelo, no lo rehagas)
- `GeometriaCabezal`, `Aleros` con DOS longitudes cuando hay esviaje (corto/largo), `ExtremoDelConducto` (D o B×H, HW, cotas,
  talud, esviaje, hoya de socavación), `LosaDeEntrega`, CB1–CB7, la longitud entre cabezales. El cabezal es NORMAL al eje del
  conducto: el [S] `orientacion_muro_respecto_al_trafico` y el conflicto #4 de la hoja `Conflictos` quedan acoplados a esa
  elección (léelos antes de tocar la sobrecarga viva / heq).
- La ficha T7A-04 dice que «más material» NO es el lado seguro con kh = 0.50 y μ < kh: tu ensamble es quien lo evalúa; si una
  regla de predimensionado de T-7a no pasa estabilidad en un punto del fixture con datos de prueba, NO la toques en silencio:
  repórtalo (la progresión de dimensiones del cabezal es decisión a devolver, no la inventes).
- Todo cabezal de la obra sale voladizo armado (la rama de gravedad no se alcanza con D ≥ 0.90 m).

## Fuentes
- El «PDF de VARIOS» (pp. 110–122) NO está en la sesión. Su ejemplo numérico (B 1.50 m, h 0.38, Ka 0.388, Kp 2.578, K_AE 0.498,
  heq 0.90, P_A 2793 kg, ΔP_AE 791 kg, M sísmico 4217.9 kg·m, DC 7.47 t, EV 3.07 t, EQ 1.58 t) sólo existe como cifras del prompt:
  puedes usarlo como contraste ROTULADO «cifras del encargo, fuente no disponible en la sesión» con tolerancia declarada y las
  diferencias explicadas (unidades, φ, δ), pero los DORADOS que fijan tu código se calculan a mano desde las ecuaciones de AASHTO
  (Coulomb 3.11.5.3, M-O 11.6.5.3, heq 3.11.6.4) con la aritmética escrita. Si no logras reproducir una cifra del ejemplo con
  ninguna lectura razonable, dilo; no ajustes el código al ejemplo.
- Tablas a transcribir con página y verificar celda a celda: 10.5.5.2.2-1, 11.5.7-1, el 11.5.8, 3.4.1-1/-2, 3.11.6.4-1/-2; los
  factores de talud N_cq / N_γq de 10.6.3.1.2: si las figuras no se dejan leer con seguridad, [A] con ventana y la fuente
  alternativa citada, o `MetodoNoEvaluableError` con rótulo propio en terreno inclinado; nunca un número leído a ojo sin decirlo.
- Entradas [S] geotécnicas (c, φ, γ, q_adm, NF) y sísmicas: del EMS / datos de sitio; sin dato → `CriterioPendienteError` /
  `DatoFaltanteError` que nombre el ensayo. Ningún valor por defecto.

## Reglas de siempre
PARADA (c): ningún diámetro, sección ni material del fixture se mueve. Toda excepción nueva desciende de `ErrorProyecto` y se
captura como `Bloqueo` del punto. La Fase 9 es de nivel EXPEDIENTE. Avisos por `InformePunto.avisos()`. M11 sin aritmética.
Tests primero en rojo (`xfail(strict=True)`) o rojo medido y declarado. Mutación con el arnés sobre lo nuevo de M9 y de V5.

## Añadido (decisión del dueño, 2026-11-13): orientación del cabezal
El cabezal es NORMAL AL EJE del conducto en las tres familias (valor por defecto; decisión tomada). El cabezal paralelo a la vía
queda diferido con ficha, sólo para el marco (Carta 11). Verifica en HDS-5 núm. 5.4.2 (y donde trate «inlet skew») lo que la
fuente dice de las embocaduras esviadas y escríbelo, con página, en la ficha T7A-03; y toma la orientación del muro frente al
tráfico coherente con esa elección al calcular la sobrecarga viva (heq).
