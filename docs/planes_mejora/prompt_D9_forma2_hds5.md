# Prompt D9 — La hoja de ruta v8 gana la Forma 2 de HDS-5 y la discrepancia se resuelve

**Prerrequisito:** ninguno externo. El paquete de corrección está escrito
entero en `docs/ruta_familia_c.md`, §16.19, apartado 2, bajo el título «El
paquete de corrección de la v8», con sus cinco puntos y las citas
verificadas que lo sostienen.

**Configuración:** Fable 5 · esfuerzo high · plan mode activado (edita la
hoja de ruta v8 y el paso `de_forma` de M4).

**Al aprobar su plan, vigila:** que el reemplazo de la «vía 2» del canal de
discrepancias no sea un invento. La vía existe para que un paso de memoria
declare una discrepancia sobre el número que ese paso sustituye. Si el plan
propone un usuario que no cumple eso, rechaza el usuario y acepta el censo
sin usuario, que es la salida honesta y ya tiene precedente.

Pega desde aquí hacia abajo como primer mensaje de la sesión nueva:

---

Antes de tocar código: entra en plan mode / propón tu plan y espera mi aprobación.

Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md, y en particular la
jerarquía de fuentes y las TRES obligaciones cuando la fuente primaria gana
sobre la hoja de ruta: declarar en el punto de uso, reportar contra la hoja
de ruta y dejar dicho que sigue mal mientras no se corrija. Para todo lo de
Familia C rige además docs/ruta_familia_c.md (§6 reglas, §16 bitácora).

DIS-HR-FORMAS-HDS5 es hoy una de las dos discrepancias vivas del registro y
la única ABIERTA_CONTRA_HOJA_DE_RUTA. Su objeto: la v8, en su §4.2, escribe
UNA sola ecuación de control de entrada no sumergido, la Forma 1 con el
término Ks·S, y nunca dice que exista la Forma 2, HW_i/D = K·(q*)^M, sin
H_c/D y sin Ks·S. La Tabla A.1 del HDS-5 trae una columna «Equation Form»
con valores 1 y 2 fila por fila; las configuraciones circulares que la v8
tabula son todas Forma 1 y por eso el error no se notaba en las Familias A y
B, pero del cajón solo la Carta 8 es Forma 1. El código ya está bien:
modelos.ConstantesHDS5.forma, M4._hw_sobre_D_no_sumergido y la memoria
(F4.FORMA_HDS5) bifurcan por forma. Quien implemente el cajón leyendo solo
la v8 obtendrá un HW un 91 % mayor que el real, medido en I3 sobre el marco
de la línea base. La fuente primaria está transcrita y verificada: las 18
filas de T_HDS5_A1 con su equation_form, las citas HDS5_3ED.A.2 y
HDS5_3ED.A.3#FORMAS.

Por qué no se corrigió en I3, y qué decide esta sesión: el paso de_forma de
src/modulos/M4_control.py declara discrepancias=("DIS-HR-FORMAS-HDS5",) y es
hoy el ÚNICO usuario de producción de la vía 2 del canal
(PasoDeMemoria.discrepancias). Al resolverla, la guardia de paso() exige
retirar esa declaración en el mismo commit, y entonces
tests/test_canal_discrepancias.py::test_la_via_del_paso_tiene_usuario_de_produccion
falla. Su docstring nombra las dos salidas admitidas: darle a la vía otro
usuario real, o censarla como sin usuario de producción. El precedente del
censo es N1 con la vía 3 (ficha N1-01 de docs/decisiones_diferidas.md y el
test test_la_via_del_criterio_existe_porque_V9_no_emite_paso).

Tarea, en orden:

1. Aplica a docs/hoja_de_ruta_alcantarillas_v8.md los CINCO puntos del
   paquete de §16.19 (el bloque de la Forma 2 tras la ec. (A.1) con la regla
   de selección por la columna «Equation Form»; «formas» → «ramas» en la nota
   de la transición y en la de MAT-D10, con el umbral del signo condicionado
   a la Forma 1; la mitad que falta del requisito de programación de §4.2.1,
   que la Forma 2 no usa H_c en control de entrada; y que K y M están
   ajustadas cada una a su forma, con la dirección del error CORREGIDA por
   la auditoría de I3: el HW sale MAYOR, no menor). Edición quirúrgica con
   nota «Corregido (`DIS-HR-FORMAS-HDS5`, D9)» como las de I2 y N1, citando
   HDS5_3ED.A.2, T_HDS5_A1 y HDS5_3ED.A.3#FORMAS. No renombres el archivo:
   M11 lo localiza por patrón y exige exactamente uno. Antes de editar,
   lanza verificador-normativo sobre HDS5_3ED.A.3#FORMAS y sobre la columna
   equation_form de T_HDS5_A1 para confirmar que la lectura sigue en pie.

2. Pasa DIS-HR-FORMAS-HDS5 a RESUELTA en src/normativa/discrepancias.py,
   con su parte hoja_de_ruta en pretérito (qué decía, qué dice ahora y en
   qué commit), como se hizo con DIS-HR-A807 en N1. Comprueba que M11 y
   F4.FORMA_HDS5 dejan de imprimir la advertencia y que
   Registro.discrepancias_abiertas() pasa de 2 a 1.

3. Retira discrepancias=("DIS-HR-FORMAS-HDS5",) del paso de_forma de M4 en
   el MISMO commit, y resuelve la vía 2 por una de las dos salidas:
   a. Usuario real. Un paso de producción que sustituya un número sobre el
      que hable una discrepancia VIVA. La única viva que queda es
      DIS-AASHTO-GAMMA-EV-12.6.1, que habla de γ_EV en la flotación (V7).
      Verifica con M11.pasos_del_informe sobre la corrida de referencia si
      V7 emite un paso; si lo emite, comprueba si la discrepancia ya le
      llega por la vía 1 (las citas de su fundamento incluyen
      AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX a propósito) y decide si declararla
      además por la vía 2 aporta algo real o es un duplicado. Solo es
      usuario si aporta.
   b. Censo sin usuario. Si no hay usuario honesto, censa la vía 2 como sin
      usuario de producción calcando la forma de N1-01: ficha en
      decisiones_diferidas.md con qué se difirió, por qué, qué haría falta
      para que vuelva a tener usuario, y dónde vive; y el test de la vía 2
      reescrito con la misma forma que el de la vía 3, de modo que la
      mecánica siga probada y el censo no crezca en silencio.
   No inventes un usuario para conservar el test.

4. Lanza auditor-adversarial sobre el conjunto, con veredicto por pieza:
   la edición de la v8 contra sus citas, la dirección del error, el estado
   de la discrepancia, la salida elegida para la vía 2.

5. Bitácora: entrada nueva en §16 de docs/ruta_familia_c.md con esta
   sesión, que cierre el cabo que §16.19 dejó abierto. Regenera la línea
   base de la Familia C y declara el diff: tiene que ser SOLO la
   desaparición de la advertencia de la discrepancia en la memoria y el
   texto asociado; ningún número cambia. Regenera los documentos generados
   que dependan del registro (manifiestos y trazabilidad.csv) con el par de
   la suite.

Reglas duras: cero valores de cálculo cambian (el código ya bifurca bien;
esta sesión corrige el documento y el registro); la v8 se edita solo con
citas verificadas y solo en los puntos del paquete; una discrepancia
resuelta no se deja declarada en ningún paso ni criterio; la otra viva,
gamma EV, no se toca salvo como candidata a usuario de la vía 2.

Cierre: suite en verde; commit «cierre(D9): la v8 gana la Forma 2 de HDS-5 —
DIS-HR-FORMAS-HDS5 resuelta y la vía 2 del canal <con usuario real: cuál |
censada sin usuario>»; entrega en origin/main por fast-forward; conteo como
par passed+skipped=collected desde origin/main con el entorno; si el conteo
se movió, tabla de CLAUDE.md re-medida en las cuatro configuraciones y
sellos de indice_formulas.md y trazabilidad.csv firmados con el par nuevo;
borra la rama de trabajo del remoto una vez fusionada. En el cierre di
explícitamente cuál de las tres obligaciones de la fuente primaria deja de
hacer falta ahora que la hoja de ruta ya no está mal.
