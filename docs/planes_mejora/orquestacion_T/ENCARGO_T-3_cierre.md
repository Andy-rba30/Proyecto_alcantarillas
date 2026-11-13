# Encargo: T-3 (Familia C) — correcciones de la auditoría adversarial + integración en main

Sigue `ENCARGO_COMUN_CORRECCIONES_E_INTEGRACION.md` (léelo primero, entero). Worktree `/home/user/wt/T-3`, rama `tesis/T-3`,
HEAD `255c97a`, base `df1b23c`; `origin/main` = `e78a4e7`. Auditoría: `ORQ/AUDITORIA_T-3.md` (AJUSTADO: 1 ALTA, 5 MEDIA, 6 BAJA;
«diámetros/secciones movidos: ninguno»; su sección D trae el ensayo de merge sobre `e78a4e7`). Te tocan TODOS sus hallazgos.

## Resoluciones del orquestador (vinculantes; si el PDF contradice una premisa, gana la fuente y lo reportas)
- **H1 (ALTA, cita) — `n_manning_cajon`**: pasa a **[C]** con la fila propia de la fuente: `HDS5_3ED.TB.1#concrete_boxes`
  («Concrete Boxes | Smooth | 0.012–0.015 | FHWA 1961», HDS-5 Tabla B.1, pág. impresa B.6 / PDF 208), valor = la FILA nombrada por
  clave → par (0.012, 0.015). Razón: es la fila específica del marco, de la misma fuente que la carta (A.1) y el ke (C.2) que el
  cálculo ya usa, y es el mismo trato que T-4 dio al HDPE. En `sensibilidad`/`justificacion`: el texto de HDS-5 B.3 (pág. impresa
  B.2 / PDF 204: vaciado in situ 0.012–0.022 según el encofrado, remite a HDS-3) como ventana hacia arriba del n de capacidad, y la
  fila «afinado» de la Tabla N° 09 del MTC —lectura corregida del corrimiento, (0.011, 0.014)— como alternativa barrible, diciendo
  la DIRECCIÓN de cada extremo (n alto: lado seguro para tirante y HW; n bajo: lado seguro para V3 y d50). Retira la frase «describe
  el acabado que tiene un marco vaciado in situ». Verifica tú las dos páginas. **Mide C-01 antes/después** (guía y corrida 6): la
  SECCIÓN no puede moverse (1.20 × 0.90); el HW de salida y los tirantes que cambien se declaran uno a uno con su causa. Si la
  sección se moviera: deja (0.012, 0.015) como alternativa barrible, conserva el valor de hoy y repórtalo.
- **H10**: la discrepancia `DIS-MCHHD-T09-A2-DESPLAZADA` se sostiene en la evidencia INTERNA de la página (lo que el auditor
  describe); quita «contrastada con Ven Te Chow 1983» (no está en `normas/`); di que la lectura literal sería más conservadora
  para capacidad; si el corrimiento alcanza B.1, B.2 y C, dilo en la discrepancia. Las tres obligaciones de «gana la fuente
  primaria» aquí se cumplen declarando la errata DE LA FUENTE en el punto de uso y en la v8.
- **H2 + H3 — `M7.remanso_canal`**: calcula el y_c del canal; con y_n ≤ y_c (pendiente fuerte) dh/S NO es cota inferior → el
  remanso «no concluye» (aviso con la razón: S1 con resalto), sin cifra presentada como cota; con VC2 fuera de tolerancia el
  remanso tampoco concluye (el HW sale de una descarga libre que el canal no tiene) y lo dice. Corrige `RemansoCanal`,
  `F7.REMANSO_CANAL` y el aviso. Tests de los dos casos con dorado a mano (el del auditor: b 1.2, n 0.014, S 0.02, Q 0.85, HW 0.90
  → y_c 0.371 > y_n 0.231).
- **H4 — G2 frente a VC2 en la Familia C**: gobierna VC2 el empalme; en Familia C, G2 admite por debajo la tolerancia de VC2
  (`desajuste_empalme_canal_m`), de modo que la banda sea de verdad de dos lados y los dos veredictos no se contradigan (tabla del
  auditor: 36.195 debe CUMPLIR en ambos). Familias A y B: G2 no cambia en nada.
- **H5 — `cobertura_minima_cajon`**: el valor 0.3048 m se mantiene como UMBRAL DE AVISO (analogía con el tubo), pero **G1 del marco
  AVISA (INDICADOR) y no bloquea**: la fuente admite el marco sin relleno. Cita en `fuente`/`justificacion` los tres textos que el
  auditor da (MTC 4.1.1.3.4 a) `#NIVELES`, Lámina N.º 03, AASHTO LRFD 12.6.6.3 «If soil cover is not provided…», pág. 12-22 /
  PDF 1660: verifícalos) y di que 0.3048 m es más restrictivo que la fuente (criterio general del dueño: «las analogías avisan»).
  El aviso llega a `InformePunto.avisos()` y cuenta en «Verificaciones con aviso». G1 del TUBO no cambia. Con cobertura menor que
  2 ft la Fase 8 de T-5 ya responde «método no evaluable» (diferible a perfil): comprueba que la cadena no cae fuera de
  `ErrorProyecto` con el caso del auditor (rasante 38.40 / subrasante 38.25) y di qué pasa ahora.
- **H6 — V7 sin peso propio**: NO toques `M5.v7_flotacion`. Reescribe la frase «no cabe bajo una rasante con poco relleno» en
  `secciones_cajon_normalizadas` y en la ficha T3-01 con la causa REAL (V7 lleva DC = 0: lado seguro, y es lo que deja fuera la
  progresión de la cadena y a C-01 sin dimensionar con t ≥ 0.26 m), declara en `espesor_pared_cajon` que 0.20 m es el extremo
  favorable a V7 de su ventana, y abre ficha diferida con símbolo sobre `M5_verificaciones.py::v7_flotacion` (peso propio del
  marco con `peso_especifico_concreto_kn_m3`; con DC y la progresión de la cadena C-01 pasaría probablemente a 1.00 × 1.00:
  mueve una sección, decisión del dueño).
- **H7**: `formula_cita_id` vacío en los pasos 7.B.R, 7.B.M y VC2 (la cita no contiene esa fórmula); la cita va a
  `citas_textuales` y al umbral.
- **H8**: arregla el test vacuo (`test_el_remanso_rechaza_un_canal_sin_pendiente`) y mata los mutantes vivos que el auditor lista
  (margen y frontera de VC2, `cota_lamina_entrada_msnm`, guardias de no finitud, tolerancia 0, sentido SOBRE/BAJO, tabique con N = 1).
- **H9**: el aviso de VC2 imprime la S que cerraría el empalme con las cotas dadas (valor calculado, rotulado como tal).
- **H11**: textos al día con la DECISIÓN del dueño (la progresión (1.20, 0.90), (1.50, 1.20), (2.00, 1.50) deja de ser
  «provisional»: es la decisión, [A] con ventana; ampliarla queda diferida con ficha a cuando exista la sección real del canal
  de ANA / la Junta), en el criterio, la `sensibilidad`, la nota de la v8 §2.3 y la ficha T3-01.
- **H12**: deja `espesor_pared_cajon` en [A] y di la razón en la ficha (el 14.5.3.2 es del método empírico de muros; hay ventana).
- Decisiones del dueño (sección T-3 de `ORQ/DECISIONES_DUENO_2026-11-12.md`): progresión mantenida; embocadura de aletas 30–75°
  (la coherencia embocadura ↔ ke ↔ carta la cierra T-7a, que se integra después); VC2 aviso, no bloqueo.

## Integración — lo específico de T-3
- Sección D de la auditoría: conflictos por anexar al final en `modelos.py`, `normativa/citas.py`, `normativa/fundamentos.py`
  (cierra el paréntesis de `MARCO_DEMANDA` de T-5 antes del bloque de T-3), `variables_entrada.py`; `MARCO` y `MARCO_DEMANDA`
  conviven. Censos esperables: 110 criterios; «sin valor» 34 − 7 = 27 (recalcúlalo). Tu Parte de `decisiones_diferidas.md` es la
  siguiente libre tras la XLVI (T-5). `GeometriaMarco` queda sin consumidor de M8 (dilo en la ficha T3-06, no lo fuerces).
- Línea base contra `e78a4e7`: sólo puede moverse lo que T-3 declara (C-01: de bloqueado por criterio a bloqueado por dato en las
  corridas ancha y de expediente; corrida 6 nueva con C-01 marco 1.20 × 0.90; claves nuevas; avisos; huellas; recuentos). A-01,
  A-02 y B-01: NADA de cálculo. La Fase 6 de C-01 en la corrida 6 sale con la envolvente de las correcciones de T-8 (para un marco
  HEC-14 no es evaluable y rige Laushey con aviso): decláralo.
- IDs canónicos del tracker: `INF-0.4` (cerrado), `INF-3.2.1` (cerrado: la mitad del cajón), `INF-0.5` (en parte: nota).
- Commit: `tesis(T-3): Familia C — el marco de concreto se dimensiona … — INF-0.4, INF-3.2.1 (cerrados); INF-0.5 (en parte)`.

Entrega: la del encargo común (`SP/INFORME_T-3_final.md` + resumen < 350 palabras).
