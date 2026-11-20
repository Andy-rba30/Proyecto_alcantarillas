# Auditoría adversarial de T-5 (Fase 8 real del conducto), primera pasada

- Árbol auditado: `/home/user/wt/T-5`, rama `tesis/T-5`, HEAD `ab7fc3a` (3 commits sobre `7fb7926`).
- Método: lectura del diff completo de `M8_estructural.py`, `servicio.py`, `M5`, `criterios_adoptados.py`, `constantes_normativas.py`, CLI/M11, fichas T5-01…09 y tests; lectura de las páginas del PDF (texto y, en M 170M, imagen); cálculo a mano; corridas antes/después con el comparador de E-B; barridos directos de M8; arnés de mutación de EXT-11.
- Todo se corrió sobre copias exportadas con `git archive` en `scratchpad/T-5-aud/{base,head}`. **Transparencia:** dos órdenes de lectura que lancé al principio con `cwd` en el worktree crearon `__pycache__/` (rutas ignoradas por `.gitignore`). Las borré: `git status` está limpio, HEAD = `ab7fc3a`, no queda ningún `__pycache__`.

## Veredicto: **AJUSTADO**

Ningún diámetro, material, veredicto previo ni «dimensionado» de la línea base se movió (medido). La aritmética de los tres tubos coincide con la que hice a mano, y todas las constantes que comprobé coinciden con su página. **Pero** hay tres defectos ALTA que hay que cerrar o llevar al dueño antes de integrar:

1. con los valores por defecto, el HDPE queda excluido **en todo el dominio**, y nadie lo dice;
2. el «Tipo 3 por defecto» está justificado con una lógica invertida, y el Tipo 4 no entra en la ventana;
3. hay una PARADA (c) en un test de T-4 que se resolvió reescribiendo el test, sin subir la pregunta al dueño.

Hay además cinco MEDIA: una lectura del pandeo del HDPE que no se ancla en 12.12.3.3, un FF del HDPE que falta, un docstring falso, una tabla de clases que no conoce los diámetros y huecos de test medidos por mutación.

**Diámetros movidos: ninguno.** Se compararon 5 corridas × 4 puntos, base `7fb7926` contra `ab7fc3a`, con `cli.py --comparar`: perfil estrecho, perfil ancho, rama de error, expediente ancho y expediente estrecho. Solo cambian tres cosas: la fila nueva `F8.CLASE` en A-01 y A-02 (37.424 y 37.042 N/m/mm, frente a 50.0), el bloque `estructural` del JSON y el texto del diferido de la Fase 8. A expediente no cambia nada por punto, porque A-01 y A-02 siguen detenidos en V5/V8. **Fuera de la línea base sí se movió un «dimensionado»** (ver H3).

---

## Refutado con evidencia

### H1 · ALTA — Con los valores por defecto el HDPE no pasa a ninguna altura de relleno, y la base de propiedades es una que la fuente declara «not meaningful for design»
- **Evidencia (barrido directo de `M8.verificar_conducto` sobre A-01, moviendo la subrasante):**
  - HDPE Ø0.90 y Ø1.20 con relleno sobre la clave de 0.5, 0.65, 0.8, 1.0, 1.5, 2.5, 3.5 y 5.0 m: `F8.EMPUJE` **falla siempre** (ε_uc 0.046–0.152 frente a 0.041) y `F8.DEFLEXION` también (5.7 %–19 % frente a 5 %).
  - Con `Si-95` o `Sn-95` sí pasa entre 0.6 y 2 m. En Ø0.90 a 1.0 m: Sn-95 da TTT, Cl-95 da FTF.
  - Script: `scratchpad/T-5-aud/barrido_h.py` y `hdpe_sens.py`.
- **Las dos causas:**
  - (a) **El perfil.** El perfil mínimo de la Tabla A12-11 con el 50 % del ensayo de compresión de M 294 núm. 7.7 da A_eff,75 = 0.417 A_g. Y AASHTO C12.12.3.2 (PDF 1713–1714, pág. 12-75/76) dice literalmente que esos mínimos «*have been minimum values and are not meaningful for design … there is no way to provide meaningful generic information on section properties*». 12.12.3.2 manda tomarlas «*from cut sections of pipe or obtained from the pipe manufacturer*».
  - (b) **El relleno.** El valor por defecto `Cl-95` se justifica con «*cualquier material apto para terraplén*» (cita `EG2013.508.07#COMPACTACION`). Esa justificación omite EG-2013 **508.02 d)** (PDF 990, pág. 982): «*La cama de asiento y la sujeción lateral se construirán con material granular … Subsección 400.02 y la Sección 301*».
    - La Sección 301 (Tabla 301-01, PDF 246) admite entre 5 y 25 % de finos con IP de 4 a 9. Un `Cl` solo es admisible para una franja con más de 20 % de finos plásticos (GC/SC, Tabla 12.12.3.5-2).
    - La afirmación de la ficha es por tanto falsa como premisa, aunque el `Cl` no quede del todo excluido.
- **Qué falta:** la ficha T5-05 dice que A-01 no cumple. No dice que el HDPE queda fuera en todo el dominio ni a qué se debe, y la memoria tampoco.
- **Corrección propuesta:**
  - `verificar_hdpe`: con propiedades genéricas, emitir aviso de «perfil mínimo de la Tabla A12-11, no significativo para diseño (C12.12.3.2)» en `ResultadoEstructural.avisos`. O bien, mejor, `DatoFaltanteError('perfil_hdpe_fabricante')` cuando el veredicto dependa de él. **Decide el dueño.**
  - `relleno_estructural_hdpe`: reescribir la justificación citando 508.02 d), y reconsiderar `Si-95` como la opción más desfavorable que esa subsección admite. **Decide el dueño.**
  - Ficha T5-05: añadir el resultado del barrido.

### H2 · ALTA — «Tipo 3, el más desfavorable que la norma peruana admite» es una lógica invertida, y la ventana deja fuera el Tipo 4
- **Fuente:**
  - AASHTO Tabla 12.10.2.1-1 (PDF 1688, pág. 12-50): el Tipo 4 es «*No compaction required, except if Category III, use 85% Category III*».
  - Diseñar como Tipo 4 es válido y conservador para **cualquier** instalación compactada.
  - Que EG-2013 exija compactación no «excluye» el Tipo 4. Lo que hace es garantizar como mucho el Tipo 3: es el tipo **más favorable** que EG-2013 asegura con cualquier suelo, no el más desfavorable.
- **Evidencia:**
  - `ca.establecer_valor_dinamico('instalacion_estandar_concreto','tipo_4')` → `ValueError`. El dueño no puede ni barrerlo.
  - En A-01, sustituyendo el criterio:

    | Tipo | D-load (N/m/mm) | H_max |
    |---|---|---|
    | tipo_1 | 32.04 | 5.46 m |
    | tipo_2 | 33.55 | 4.11 m |
    | tipo_3 | 37.42 | 3.18 m |
    | tipo_4 | 44.86 | 1.69 m |

  - La clase no cambia (II), pero el **relleno máximo impreso se reduce a la mitad**.
- **Corrección:**
  - Añadir `tipo_4` a `sensibilidad`.
  - Reescribir la justificación de `instalacion_estandar_concreto`, la ficha T5-09 y la nota de la v8, que repite «el Tipo 4 no la exige y queda fuera».
  - El valor por defecto (3 o 4) lo decide el dueño.
  - El test `test_la_instalacion_por_defecto_es_la_mas_desfavorable_que_admite_EG2013` congela la afirmación falsa.

### H3 · ALTA — PARADA (c) en un test: el caso G2 de T-4 deja de dimensionarse y se reescribió el test en vez de preguntar
- `tests/test_t4_materiales_durabilidad.py::test_h1_el_caso_del_auditor_adopta_tmc…` fijaba la adopción de TMC Ø1.95 m.
- Con los valores por defecto de T-5 (`fabricacion_tmc = anular_remachada_simple`) ninguna plancha de 68×13 desarrolla el empuje: 317 frente a 0.67 × 374 = 251 kN/m, según la ficha T5-08. Reproducido en mi caso P-MUY: «Ø 2.10 m: incumple F8.COSTURA … 741.3 frente a 250.58».
- El implementador añadió `FABRICACION_DEL_CASO_G2 = {"fabricacion_tmc": "anular_remachada_doble"}` para que el test siga verde.
- `ORQUESTACION.md` («PARADAS», c) cubre literalmente «cualquier test que fije un diámetro».
- El movimiento está documentado (T5-08) y es correcto en ingeniería, pero **la pregunta y el valor por defecto de `fabricacion_tmc` (simple / doble / helicoidal) son del dueño**.

### H4 · MEDIA — El pandeo del HDPE usa el módulo inicial para la parte viva sin anclarse en 12.12.3.3
- **Fuente:** AASHTO 12.12.3.3 (PDF 1714, pág. 12-76), literal: «*Except for buckling, the choice of either initial or long-term mechanical property requirements … shall be determined by the Engineer. Investigation of general buckling shall be based on the value of modulus of elasticity that represents the design life of the project.*»
- **Qué hace el código:** `u = ε_d/ε_bck,lp + ε_l/ε_bck,ini`. Lo apoya en `AASHTO_LRFD_9.12.12.3.10.1c#EP`, que es la definición de E_p para la **deformación de compresión**, no para el pandeo. La frase de 12.12.3.3 no está en el registro.
- **Medido** (`scratchpad/T-5-aud/bck.py`): con la lectura «todo a vida de diseño» (E_75 y A_eff,75 también para la carga viva):
  - Cl-95 a 0.6 m pasa de 0.650 (cumple) a **0.707 > 0.70 (no cumple)**.
  - En Sn-95 y Si-95 la lectura del código resulta más conservadora: 0.183 frente a 0.144.
  - La dirección depende del suelo, y por eso tiene que ser una lectura declarada, no implícita.
- **Corrección:** citar 12.12.3.3 en el paso F8.PANDEO y declarar la lectura como `Interpretacion` / [A] con su sensibilidad, o aplicar E_75 a todo el pandeo.

### H5 · MEDIA — Falta el factor de flexibilidad del HDPE
- **Fuente:**
  - 12.5.3 (PDF 1648) enumera para el termoplástico «*Wall area, Buckling, Flexibility limit*».
  - 12.12.3.6 (PDF 1720): FF = S²/(E I), con E el **inicial**, «*shall be limited as specified in Article 12.5.6.3*».
  - 12.5.6.3 (PDF 1652): «*shall not exceed 95.0 in./kip*».
- **Estado:** `verificar_hdpe` no lo verifica y `verificacion_diferida_estructural()` no lo lista.
- **Medido:** con los perfiles mínimos, FF = 29.5–54.5 in/kip; pasarían.
- **Corrección:** añadir `F8.FF` al HDPE (un paso, una cita) y un test.

### H6 · MEDIA — Docstring y ficha falsos: «subir de diámetro no lo resuelve (W crece con B_c y S_i con D)»
- **Dónde:** el docstring de `verificar_concreto` y la ficha T5-02.
- **Contraejemplo** (geometría de A-01, relleno sobre la clave 0.50 m más 0.15 de paquete, Tipo 3):

  | Diámetro | D-load (N/m/mm) | Resultado |
  |---|---|---|
  | Ø0.90 | 52.2 | `DatoFaltanteError`, pide Clase III |
  | Ø1.20 | 41.7 | Clase II |
  | Ø1.50 | 36.0 | Clase II |

  La afirmación solo vale con relleno profundo (a 3.5 m: 54.4, 55.7 y 57.2).
- **Corrección:** reescribir la justificación. Bloquear con `DatoFaltanteError` puede seguir siendo la decisión, pero argumentada como «la solución de ingeniería es la Clase III, no un tubo mayor», no con una monotonía que no existe. Decide el dueño.

### H7 · MEDIA — `clases_producto_por_relleno` no sabe en qué diámetros existe cada clase
- **Fuente:** M 170M Tabla 1 (PDF 3, leída por imagen). La Clase I solo existe de 1500 a 3450 mm.
- **Evidencia:** `reemplazado_por` indica añadir filas «sin tocar el código». Haciéndolo con `{"concreto_reforzado": {"I": 40.0, "II": 50.0}}` (la puerta lo acepta), `verificar_concreto` devuelve **«Clase I» para Ø0.90**. Reproducido en `robust.py`.
- La puerta acepta también `{"II": "50"}` y la clase `"VI"`; las detiene la segunda línea.
- **Corrección:** estructura por clase con el rango de diámetros de su tabla, o una guardia, y un test.

### H8 · MEDIA — Huecos de test medidos por mutación
- **Corrida:** `python3 -m tests.apoyo.mutacion --modulo M8_estructural` sobre las 21 funciones de T-5, con objetivos `test_t5_estructural_conducto.py` y `test_M8_estructural.py`, 3 trabajadores.
- **Resultado:** **448/572 muertos (78.3 %), 124 vivos.** Informe en `scratchpad/T-5-aud/mut_m8.json`.
- **Los vivos que importan:**
  - **Relleno máximo del TMC y del HDPE sin test.** En los dos sobrevive `if cumple_todo` → `if not cumple_todo`. En el TMC también `A·φ·f_res` → `A·φ/f_res` y `φ_s·SS − T` → `+ T`.
  - **La deflexión admisible del HDPE no se afirma.** Sobrevive `deflexion_admisible * D` → `/ D`.
  - **La rama del NF** (agua sobre la clave, TMC y HDPE): sobreviven siete mutantes de signo de `centro`, `nf` y `D/2`. El NF es un dato real del Bajo Piura.
  - **El dorado del marco con H_rel = 1.00 m** no distingue `γ_s·H_rel` de `γ_s/H_rel`.
  - **`_relleno_maximo` tiene 14 vivos**, entre ellos `tramo = (H_techo−H_rel)/400` → `*400`. El test del «primer cruce» no discrimina el muestreo que dice proteger.
  - Los márgenes de los `Veredicto`.
- **Por qué la línea base no los mata:** no tiene NF, ni TMC o HDPE adoptados, ni marco a expediente.
- **Lo que sobrevive y es equivalente o inalcanzable:**
  - la rama elástica de `tension_critica_de_pandeo` (con 68×13 el umbral es 2471 mm, mayor que la mayor luz del catálogo);
  - φ = 1.0;
  - K₂ = 1.0;
  - F_min = 1.
- **Los tests no se escribieron en rojo primero** (lo declara el propio archivo).

### H9 · BAJA — Lo que «no se verifica» se imprime entero en cada punto
- M11 y el JSON imprimen `verificacion_diferida_estructural()` completa en todos los puntos. La memoria del concreto de A-01 lista la flexión del HDPE, la costura empernada y el pórtico del marco.
- `ResultadoEstructural.diferido`, que sí distingue por material, no tiene consumidor de producción (solo un test).

### H10 · BAJA — Dos valores por defecto no son el extremo desfavorable de su ventana
- La cabecera del bloque dice «cada uno trae por defecto la opción MÁS DESFAVORABLE». Sin embargo:
  - `nu_suelo` = 0.40, cuando el extremo desfavorable de su ventana (0.25, 0.45) es 0.45;
  - `K_B` = 0.10, cuando el de (0.083, 0.110) es 0.110.
- Están declarados como «típico», pero la cabecera dice otra cosa.

### H11 · BAJA — La carga viva se desprecia sin criterio, y el marco multicelda usa la luz de una celda
- Pasados 8 ft de relleno que además superan la luz, la carga viva se desprecia **automáticamente**. Es un PERMISO («*may be neglected*») aplicado del lado no conservador sin [A].
- En el marco multicelda se usa la luz de una celda B. 3.6.1.2.6a pide, para «*multiple span culverts*», la «*distance between inside faces of end walls*».

### H12 · BAJA — Dos públicas sin guardia de segunda línea
- `incremento_dinamico_enterrado(-5.0)` devuelve IM = 100.7 %.
- `carga_viva_enterrada(conducto="xx")` lo acepta en silencio y lo trata como concreto con LLDF 1.15.

### H13 · BAJA — El nivel «medido» de cuatro criterios nuevos no lo midió ninguna corrida
- `fabricacion_tmc`, `eta_importancia_operativa_conducto`, `relleno_estructural_hdpe` y `parametros_diseno_hdpe` dicen «medido en tests/test_nivel_medido.py».
- Ninguna corrida los invoca; quedan clasificados solo por consumidor estático. El README de la línea base lo admite («esta corrida no alcanza»).
- CLAUDE.md pide decir qué corrida midió cada uno.

### H14 · BAJA — Motivo engañoso cuando el TMC se agota por la Fase 8
- Cuando el TMC se agota por `F8.COSTURA`, MD informa «material descartado por diámetro requerido».
- Además sube de diámetro inútilmente: en el TMC el empuje crece con S, así que un diámetro mayor nunca arregla un fallo de empuje.

---

## Sospechas no comprobadas, y lo comprobado sin hallazgo

**Comprobado contra el PDF, sin hallazgo:**
- AASHTO 3.6.1.2.6a/b (PDF 80–82): ecuaciones −1 a −7, LLDF, dominios de 1 y 2 ft.
- Tabla 12.5.5-1, con φ 1.00 / 0.67 / 0.90 / 0.70.
- Tabla 12.5.6.1-1: 43 y 33 in/kip, que son 0.2455 mm/N.
- 12.7.2.2–12.7.2.6, con F_min = 15/(12 S) ≥ 1 y k = 0.22.
- 12.10.2.1: W_E = F_e w B_c H con F_e = VAF y el piso de 110 pcf.
- Tablas 12.10.2.1-3, 12.10.4.3.2a-1 y 12.10.4.3.2c-1, valor a valor.
- 12.10.4.3.1, incluido el factor 1.10 del Tipo 1.
- 12.11.2.2.1, con los topes 1.15 y 1.40.
- 12.12.3.5 a 12.12.3.10.1e, la Tabla 12.12.3.3-1, la Tabla 12.12.3.5-1 (4 columnas × 6 niveles) y la Tabla 12.12.3.10.1b-1.
- ASTM A796 núm. 4: f_y 225, f_u 310, E 200 000. Núm. 10.3: 0.245 mm/N en terraplén. Tablas 5 y 7: costuras 244/315, 266/435, 341/683, 357/715, 374/748 y 419…1032 kN/m.
- EG-2013 Tabla 507-01 (PDF 978).
- Manual de Puentes: Tabla 2.4.2.1-1 (0.120 y 0.140 kcf), HL-93, área de contacto 20×10 in y m = 1.20.
- La conversión a SI.
- **M 170M leída por imagen:** las D-load de 0.3 mm de las Clases I («dtl0»), III («° .!!»), IV (ausente) y V («\ 40.0») **son efectivamente ilegibles**. La afirmación del implementador se sostiene y `clases_producto_por_relleno` no queda cojo por error de lectura.

**Recalculado a mano, coincide:**
- Concreto en A-01:
  - Carga viva: LLDF 1.24528, IM 20.143 %, w_w 3.7606 m, l_w 1.6238 m, P_L 33.607 kPa.
  - Cargas: W_E 32.658 kN/m, W_F 6.241 kN/m, W_L 36.967 kN/m.
  - D-load: 37.424 N/m/mm frente a 50.
- TMC en A-01: T_L 50.86 kN/m, f_cr 42.015 ksi, A_req 0.2236 mm²/mm, FF 0.1033 mm/N.
- HDPE en A-01: ε_bck,75 0.14073, VAF 0.7367, M_s 0.58766 ksi.
- El «caso VARIOS» (A = 0.354 con f_y 230; C = 40.725) está rotulado «según el INFORME §1.1, páginas no verificadas», y la no reproducción de FF 0.109 está declarada.

**Sin mezcla LRFD/ASD:**
- γ_EV del TMC = 1.95, igual que el 1.95 EL de A796 núm. 9.1.
- El ASD queda aislado en un paso rotulado «NO RIGE».

**Robustez:**
- Sin caídas fuera de `ErrorProyecto` con H = 0, NaN, 1e300, el HDPE de 1350 mm, el TMC con costura empernada o con 75×25 remachada simple, y relleno de 20 m (caso P-MUY).
- No queda ningún `AssertionError` en M8.

**Sospechas no comprobadas:**
- No pude ejercitar la etapa de expediente de punta a punta en la CLI: el fixture se detiene en V5/V8, y la demanda del marco solo la ejercitan los tests directos.
- No corrí la segunda vuelta de mutación (línea base, CLI): por diseño del fixture no mataría los vivos de H8.

---

## Decisiones del dueño

1. **Instalación del concreto (H2).** Tipo 3 o Tipo 4 por defecto; en todo caso, `tipo_4` dentro de la ventana. En A-01 el relleno máximo pasa de 3.18 a 1.69 m.
2. **HDPE (H1).** Tres opciones: (a) aceptar que con las propiedades genéricas queda excluido; (b) exigir las propiedades de sección del fabricante (C12.12.3.2); (c) cambiar el relleno por defecto a `Si-95` por EG-2013 508.02 d).
3. **Fabricación del TMC (H3).** `anular_remachada_simple`, doble o helicoidal por defecto, y aceptar o no el cambio del caso G2 de T-4.
4. **Lectura del pandeo del HDPE (H4)** frente a 12.12.3.3.
5. **Concreto que pide más que la Clase II (H6).** Bloquear (lo actual) o dejar que MD suba de diámetro.
6. **η_I = 1.05:** que lo confirme el propietario.
