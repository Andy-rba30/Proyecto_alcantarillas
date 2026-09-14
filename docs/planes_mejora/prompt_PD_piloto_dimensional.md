# Prompt PD — Cierre del piloto dimensional: el coeficiente de Manning declarado

**Prerrequisito:** ninguno externo. Todo lo que hace falta está en el repo:
el piloto de I4 (`tests/test_dimensional_piloto.py`) es el test que falla
antes, con las cuatro inconsistencias censadas y su razón escrita.

**Configuración:** Opus 5 · esfuerzo high · plan mode activado (toca M3 y M4,
que son motor validado; la condición de la casa para tocarlo, un test que
falle antes, ya está cumplida por el censo del piloto).

**Al aprobar su plan, vigila:** que NINGÚN número de cálculo cambie. La
corrección multiplica por 1.0 y reordena texto de la memoria. Si el plan
propone tocar el valor de `n`, de `K_FRICCION_SI` o de cualquier umbral,
recházalo: eso sería otra sesión con otro nombre.

Pega desde aquí hacia abajo como primer mensaje de la sesión nueva:

---

Antes de tocar código: entra en plan mode / propón tu plan y espera mi aprobación.

Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md, y en particular la
regla de Unidades: «las constantes empíricas dependientes de unidades llevan
sufijo _SI en su nombre y un comentario con el valor imperial equivalente y
por qué NO se usa». I4 corrió un chequeo dimensional piloto sobre M3, M4 y
M5 (tests/test_dimensional_piloto.py) y midió CUATRO inconsistencias, todas
de presentación y ninguna de valor, censadas en INHOMOGENEIDADES_CENSADAS,
UMBRALES_INCONMENSURABLES_CENSADOS y en el test
test_K_FRICCION_SI_cierra_desde_2g_sobre_phi_cuadrado_y_no_desde_el_29. La
ficha I4-01 de docs/decisiones_diferidas.md las difirió porque corregirlas
toca el motor validado. Esta sesión las cierra, sin mover un solo número.

La principal: la fórmula de Manning no es homogénea. En SI la cierra el
coeficiente de unidades k_n = 1.0 m^(1/3)/s (1.486 ft^(1/3)/s en el sistema
inglés), que la Sec. 4.1 de la hoja de ruta escribe como «1/n» y que
M3._caudal_manning aplica como (1 / n) sin declararlo. Es exactamente lo que
la regla de Unidades prohíbe, y los dos precedentes de la casa marcan el
molde: KU_SI = 1.811 en src/constantes_normativas.py, con su «Imperial: 1.0»
al lado y el bloque que explica por qué el imperial se nombra y no se usa; y
K_FRICCION_SI = 19.63 con su «29 es el valor inglés». El paso de memoria que
imprime Manning es "F4.MANNING", emitido en src/modulos/M4_control.py con
formula_cita_id="MC_HHD.4.1.1.3.6".

Tarea, en orden:

1. K_MANNING_SI. Declara en src/constantes_normativas.py, junto a KU_SI y
   con su misma forma, K_MANNING_SI = 1.0 con unidad m^(1/3)/s, el valor del
   sistema inglés (1.486 ft^(1/3)/s) en el comentario y la explicación de por
   qué no se usa (todo el código opera en SI). Lanza verificador-normativo
   sobre MC_HHD.4.1.1.3.6 con una pregunta concreta: ¿el Manual escribe
   Manning en forma SI, sin coeficiente explícito? Eso es lo que sostiene el
   1.0. Para el 1.486 NO inventes cita: si ninguna fuente de normas/ lo
   imprime, el comentario lo dice con esas palabras («valor del sistema
   inglés según la práctica; ninguna fuente de normas/ lo imprime»).
   Decide la etiqueta con la taxonomía de CLAUDE.md y el precedente de
   KU_SI, y decláralo en el comentario.

2. M3._caudal_manning multiplica explícitamente por K_MANNING_SI y su
   docstring escribe Q = (K_MANNING_SI/n)·A·R^(2/3)·S^(1/2). El paso
   "F4.MANNING" incluye K_MANNING_SI en su sustitución, con unidad y
   procedencia, y su texto de fórmula lo nombra. M11 no cambia: solo
   imprime lo que el paso trae.

3. Las otras tres, con el mismo criterio de «presentación, no valor»:
   a. El paso 4.2 (HW de entrada) devuelve metros con una sustitución
      adimensional (q*, Ks): añade a la sustitución el D que cierra, con su
      procedencia, sin recalcular nada.
   b. El paso 4.3 juzga contra un umbral sobre HW/D e imprime HW_salida en
      metros: haz conmensurables resultado y umbral en la PRESENTACIÓN del
      paso (imprimir HW/D junto al HW, o el umbral en metros con su D),
      sin cambiar qué se compara ni el veredicto.
   c. El comentario de K_FRICCION_SI enuncia una derivación («desde el 29»)
      que no cierra al 0.1 %, mientras que 2·32.2/1.486² sí cierra, como el
      propio test demuestra: reescribe el comentario para que diga la
      derivación que cierra, sin tocar el valor 19.63 ni su cita.
   Si al hacer cualquiera de las tres descubres que exige cambiar un
   número, NO la hagas: déjala censada con esa razón nueva y repórtalo.

4. El piloto pasa a positivo: la relación de "F4.MANNING@4.1" en RELACIONES
   gana el factor k_n con dimensión L^(1/3)/T; su entrada sale de
   INHOMOGENEIDADES_CENSADAS; test_manning_no_cierra_por_L_un_tercio_sobre_T
   se convierte en su afirmación positiva; K_MANNING_SI entra al censo de
   constantes _SI del piloto (dimensión y comentario imperial). Los umbrales
   de 4.3 salen de UMBRALES_INCONMENSURABLES_CENSADOS. Objetivo: los dos
   censos en cero, y si alguno no llega a cero, con la razón escrita.

5. Guardia de que nada se movió: tests/fixtures/casos_patron.py intacto y
   en verde sin tocar una tolerancia; la línea base (tests/linea_base_*)
   regenerada con el diff declarado en el cierre, que tiene que ser SOLO
   texto de la memoria (la constante nueva en la sustitución, el D en 4.2,
   la presentación de 4.3). Un diff numérico aborta el commit.

6. Regenera docs/indice_formulas.md (el texto de la fórmula cambia) con
   python3 src/indice_formulas.py --escribir --suite "..." y, si el conteo
   se mueve, también los tres documentos del manifiesto con
   python3 -m src.normativa.manifiesto --escribir --suite "...". Actualiza
   la ficha I4-01 de decisiones_diferidas.md: qué se cerró, qué queda si
   algo queda, y la decisión sobre extender el barrido dimensional a M6 a
   M9 ahora que el piloto sale limpio (decídelo con el argumento medido,
   no lo hagas en esta sesión).

7. Lanza auditor-adversarial sobre el conjunto antes de fusionar, con
   veredicto por pieza. Pregunta obligada: ¿algún número de la línea base
   cambió?

Reglas duras: cero cambios de valor; cero citas inventadas; K_MANNING_SI no
va a constantes_fisicas.py (no es una constante universal, es una
convención de sistema de unidades, como KU_SI); no se toca la hoja de ruta
(su «1/n» es la forma SI y es correcta; si el verificador dice lo
contrario, se reporta como discrepancia, no se edita aquí).

Cierre: suite en verde; commit «unidades(PD): coeficiente de Manning
declarado como K_MANNING_SI y censo del piloto dimensional a cero — sin
cambio de valor»; entrega en origin/main por fast-forward; conteo como par
passed+skipped=collected desde origin/main con el entorno (PyMuPDF sí/no,
Tk sí/no); si el conteo se movió, la tabla de CLAUDE.md se re-mide en las
cuatro configuraciones y los sellos de indice_formulas.md y
trazabilidad.csv se vuelven a firmar con el par nuevo; borra la rama de
trabajo del remoto una vez fusionada.
