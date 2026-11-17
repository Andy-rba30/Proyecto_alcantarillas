# Validación externa de M8: el conducto contra ejemplos publicados

> **Este documento se GENERA.** No se edita a mano: lo produce `tests/apoyo/validacion_conducto.py` y `tests/test_validacion_conducto.py` lo regenera a memoria y lo compara. Regenerar: `python -m tests.apoyo.validacion_conducto --escribir`.

## 1. Qué se juzga, y con qué regla

Cada contraste lleva cuatro cifras en la unidad de la fuente: lo **publicado** (con su página impresa), lo **recalculado** con las fórmulas y los datos del propio ejemplo, la **referencia** —el método que M8 implementa, escrito a mano en otra unidad y sin llamar a M8— y lo que da el **motor**. La clase se decide en este orden:

- **DEFECTO**: el motor no reproduce su propio método (motor frente a referencia, fuera de `TOL_REL_MOTOR` = 1e-09).
- **COINCIDE**: el método de M8 da lo mismo que el ejemplo (referencia frente a recalculado, dentro de `TOL_REL_CIFRA_IMPRESA` = 0.005).
- **METODO**: el ejemplo usa otra edición u otro método; la diferencia se explica por causa.

Una **errata de la fuente** (publicado frente a recalculado) se anota aparte: lo que rige es lo recalculado.

## 2. Fuentes

| Clave | Documento | URL |
|---|---|---|
| DD1 | ACPA, Design Data 1 «Highway Live Loads on Concrete Pipe», DD 1 (07/09), 2009 | https://old.concretepipe.org/wp-content/uploads/DD_1.pdf |
| DD22 | ACPA, Design Data 22 «Flotation of Circular Concrete Pipe», DD 22 (11/12) | https://old.concretepipe.org/wp-content/uploads/2014/09/DD_22.pdf |
| CPDM | ACPA, Concrete Pipe Design Manual, Cap. 4 «Loads and Supporting Strengths» (ed. 2000; copia de un curso del NJIT) | https://web.njit.edu/~washd/cim305/download/notes/CHAPTERS/CH%204.pdf |
| USACE | US Army Corps of Engineers, EM 1110-2-2902 «Conduits, Culverts and Pipes», Apendice B «Design Examples», 1997 (Change 1, 1998) | https://damtoolbox.org/images/3/37/EM_1110-2-2902.pdf |
| PPI | Plastics Pipe Institute, Drainage Handbook — Structural Design Guide (Draft Rev 1), 2019 | https://clvr.imiscloud.com/common/Uploaded%20files/1-PPI/Manuals-Design%20Guides/Drainage%20Handbook/1st%20Edition/Design%20Guide%20Rev1%20.pdf |

Los PDF no se versionan (copyright; CLAUDE.md). Las cifras se transcribieron leyendo cada página; las del USACE, escaneadas, en la imagen.

## 3. Resultado

**42 contrastes: 32 coinciden, 10 difieren por método o edición, 0 defectos del motor.** 2 con errata de la fuente.

| Id | Fuente, pág. | Qué | Unidad | Publicado | Recalculado | Referencia (método de M8) | Motor | Motor − recalculado | Clase |
|---|---|---|---|---|---|---|---|---|---|
| DD1-IM-2ft | DD1, 7 | IM de componentes enterrados con 2 ft de cubierta | % | 24.75 | 24.75 | 24.75 | 24.75 | +0.00 % | COINCIDE |
| DD1-IM-6ft | DD1, 9 | IM de componentes enterrados con 6 ft de cubierta | % | 8.25 | 8.25 | 8.25 | 8.25 | +0.00 % | COINCIDE |
| DD1-EJ1 | DD1, 7 | Carga viva por pie de tubo, Ø 30 in pared B, 2 ft de relleno, trafico perpendicular al tubo | lb/ft | 3 272 | 3 280 | 5 417 | 5 417 | +65.16 % | METODO |
| DD1-EJ4 | DD1, 8-9 | Carga viva por pie de tubo, Ø 30 in pared B, 6 ft de relleno, trafico perpendicular al tubo | lb/ft | 855 | 856.4 | 1 108 | 1 108 | +29.41 % | METODO |
| CPDM-VAF-1 | CPDM, 38 | VAF de la instalacion estandar Tipo 1 |  | 1.35 | 1.35 | 1.35 | 1.35 | +0.00 % | COINCIDE |
| CPDM-VAF-2 | CPDM, 38 | VAF de la instalacion estandar Tipo 2 |  | 1.4 | 1.4 | 1.4 | 1.4 | +0.00 % | COINCIDE |
| CPDM-VAF-3 | CPDM, 38 | VAF de la instalacion estandar Tipo 3 |  | 1.4 | 1.4 | 1.4 | 1.4 | +0.00 % | COINCIDE |
| CPDM-VAF-4 | CPDM, 38 | VAF de la instalacion estandar Tipo 4 |  | 1.45 | 1.45 | 1.45 | 1.45 | +0.00 % | COINCIDE |
| CPDM-BFE-12-1 | CPDM, 52 | B_FE, Ø 12 in, Tipo 1 |  | 4.4 | 4.4 | 4.4 | 4.4 | +0.00 % | COINCIDE |
| CPDM-BFE-12-2 | CPDM, 52 | B_FE, Ø 12 in, Tipo 2 |  | 3.2 | 3.2 | 3.2 | 3.2 | +0.00 % | COINCIDE |
| CPDM-BFE-12-3 | CPDM, 52 | B_FE, Ø 12 in, Tipo 3 |  | 2.5 | 2.5 | 2.5 | 2.5 | +0.00 % | COINCIDE |
| CPDM-BFE-12-4 | CPDM, 52 | B_FE, Ø 12 in, Tipo 4 |  | 1.7 | 1.7 | 1.7 | 1.7 | +0.00 % | COINCIDE |
| CPDM-BFE-24-1 | CPDM, 52 | B_FE, Ø 24 in, Tipo 1 |  | 4.2 | 4.2 | 4.2 | 4.2 | +0.00 % | COINCIDE |
| CPDM-BFE-24-2 | CPDM, 52 | B_FE, Ø 24 in, Tipo 2 |  | 3 | 3 | 3 | 3 | +0.00 % | COINCIDE |
| CPDM-BFE-24-3 | CPDM, 52 | B_FE, Ø 24 in, Tipo 3 |  | 2.4 | 2.4 | 2.4 | 2.4 | +0.00 % | COINCIDE |
| CPDM-BFE-24-4 | CPDM, 52 | B_FE, Ø 24 in, Tipo 4 |  | 1.7 | 1.7 | 1.7 | 1.7 | +0.00 % | COINCIDE |
| CPDM-BFE-36-1 | CPDM, 52 | B_FE, Ø 36 in, Tipo 1 |  | 4 | 4 | 4 | 4 | +0.00 % | COINCIDE |
| CPDM-BFE-36-2 | CPDM, 52 | B_FE, Ø 36 in, Tipo 2 |  | 2.9 | 2.9 | 2.9 | 2.9 | +0.00 % | COINCIDE |
| CPDM-BFE-36-3 | CPDM, 52 | B_FE, Ø 36 in, Tipo 3 |  | 2.3 | 2.3 | 2.3 | 2.3 | +0.00 % | COINCIDE |
| CPDM-BFE-36-4 | CPDM, 52 | B_FE, Ø 36 in, Tipo 4 |  | 1.7 | 1.7 | 1.7 | 1.7 | +0.00 % | COINCIDE |
| CPDM-BFE-72-1 | CPDM, 52 | B_FE, Ø 72 in, Tipo 1 |  | 3.8 | 3.8 | 3.8 | 3.8 | +0.00 % | COINCIDE |
| CPDM-BFE-72-2 | CPDM, 52 | B_FE, Ø 72 in, Tipo 2 |  | 2.8 | 2.8 | 2.8 | 2.8 | +0.00 % | COINCIDE |
| CPDM-BFE-72-3 | CPDM, 52 | B_FE, Ø 72 in, Tipo 3 |  | 2.2 | 2.2 | 2.2 | 2.2 | +0.00 % | COINCIDE |
| CPDM-BFE-72-4 | CPDM, 52 | B_FE, Ø 72 in, Tipo 4 |  | 1.7 | 1.7 | 1.7 | 1.7 | +0.00 % | COINCIDE |
| CPDM-BFE-144-1 | CPDM, 52 | B_FE, Ø 144 in, Tipo 1 |  | 3.6 | 3.6 | 3.6 | 3.6 | +0.00 % | COINCIDE |
| CPDM-BFE-144-2 | CPDM, 52 | B_FE, Ø 144 in, Tipo 2 |  | 2.8 | 2.8 | 2.8 | 2.8 | +0.00 % | COINCIDE |
| CPDM-BFE-144-3 | CPDM, 52 | B_FE, Ø 144 in, Tipo 3 |  | 2.2 | 2.2 | 2.2 | 2.2 | +0.00 % | COINCIDE |
| CPDM-BFE-144-4 | CPDM, 52 | B_FE, Ø 144 in, Tipo 4 |  | 1.7 | 1.7 | 1.7 | 1.7 | +0.00 % | COINCIDE |
| CPDM-BFLL-12 | CPDM, 55 | B_FLL, Ø 12 in, 2.0 ft de relleno |  | 2.2 | 2.2 | 2.4 | 2.4 | +9.09 % | METODO |
| CPDM-BFLL-24 | CPDM, 55 | B_FLL, Ø 24 in, 2.0 ft de relleno |  | 2.2 | 2.2 | 2.4 | 2.4 | +9.09 % | METODO |
| CPDM-BFLL-36 | CPDM, 55 | B_FLL, Ø 36 in, 2.0 ft de relleno |  | 2.2 | 2.2 | 2.2 | 2.2 | +0.00 % | COINCIDE |
| CPDM-BFLL-48 | CPDM, 55 | B_FLL, Ø 48 in, 2.0 ft de relleno |  | 2 | 2 | 2.2 | 2.2 | +10.00 % | METODO |
| CPDM-4-2 | CPDM, 60-62 | D-load a 0.01 in, Ø 48 in pared B, 35 ft de relleno de 120 pcf, Tipo 1 | lb/ft/ft | 1 768 | 1 768 | 1 971 | 1 971 | +11.48 % | METODO |
| CPDM-4-5 | CPDM, 67-69 | D-load a 0.01 in, Ø 24 in pared B, 10 ft de relleno de 120 pcf, Tipo 4 | lb/ft/ft | 1 314 | 1 314 | 1 337 | 1 337 | +1.80 % | METODO |
| CPDM-4-7 | CPDM, 71-73 | D-load a 0.01 in, Ø 24 in pared B, 2 ft de relleno de 120 pcf, Tipo 2 | lb/ft/ft | 563.2 | 563.2 | 1 147 | 1 147 | +103.64 % | METODO (errata de la fuente) |
| DD22-U | DD22, 4 | Empuje: agua desplazada por el tubo de 72 in pared B (B_c = 86 in) | lb/ft | 2 519 | 2 517 | 2 519 | 2 519 | +0.08 % | COINCIDE |
| DD22-WI | DD22, 4-5 | Peso del relleno sumergido sobre el tubo, 8 ft bajo el nivel de agua (arena de 110 pcf, SG 2.65) | lb/ft | 4 276 | 4 276 | 3 927 | 3 927 | -8.16 % | METODO (errata de la fuente) |
| DD22-V7 | DD22, 5 | Fuerza neta hacia abajo del tubo vacio con el relleno completo (signo + = no flota) | lb/ft | 2 713 | 2 712 | 1 015 | 1 015 | -62.58 % | METODO |
| USACE-T | USACE, B-10 | Empuje en la pared, T = P S/2 | kN/m | 56.91 | 56.91 | 56.91 | 56.91 | +0.00 % | COINCIDE |
| USACE-A | USACE, B-10 | Area requerida de pared, A = T SF / f_y | mm2/mm | 0.5002 | 0.5002 | 0.5002 | 0.5002 | +0.00 % | COINCIDE |
| USACE-FC | USACE, B-10 | Tension critica de pandeo f_c, s = 1220 mm | MPa | 272 | 272.3 | 272.3 | 272.3 | +0.00 % | COINCIDE |
| USACE-CLASE-II | USACE, B-7 | D-load a 0.01 in de la Clase II de ASTM C76M | N/m/mm | 50 | 50 | 50 | 50 | +0.00 % | COINCIDE |

## 4. Por qué difiere cada contraste de método

- **DD1-EJ1** — DD 1 (2009) aplica la distribucion ANTERIOR a 2013 (dos ruedas duales HS 20 en paso, 32 000 lb, sin presencia multiple), LLDF 1.15 fijo, sin el termino 0.06 D_i, y reparte la carga a lo largo del tubo con la longitud efectiva L_e = L + 1.75 (3/4 R_o). M8 aplica AASHTO LRFD 9.a ed. 3.6.1.2.6b: HL-93 (gobierna el camion), m = 1.20, LLDF 1.200 interpolado por diametro (Tabla 3.6.1.2.6a-1), 0.06 D_i en el ancho y W_L = P_L min(l_w, B_c), sin L_e. El IM es el mismo (24.75 %, contraste DD1-IM). No es un defecto: son dos ediciones del metodo.
- **DD1-EJ4** — DD 1 (2009) aplica la distribucion ANTERIOR a 2013 (dos ruedas de dos cargas alternativas (Alternate Load) en paso, 50 000 lb, sin presencia multiple), LLDF 1.15 fijo, sin el termino 0.06 D_i, y reparte la carga a lo largo del tubo con la longitud efectiva L_e = L + 1.75 (3/4 R_o). M8 aplica AASHTO LRFD 9.a ed. 3.6.1.2.6b: HL-93 (gobierna el tandem), m = 1.20, LLDF 1.200 interpolado por diametro (Tabla 3.6.1.2.6a-1), 0.06 D_i en el ancho y W_L = P_L min(l_w, B_c), sin L_e. El IM es el mismo (8.25 %, contraste DD1-IM). No es un defecto: son dos ediciones del metodo.
- **CPDM-BFLL-12** — El CPDM (2000) tabula B_fLL para el HS 20 por diametro y por relleno de 0.5 a 6.5 ft; AASHTO LRFD 9.a ed. (Tabla 12.10.4.3.2c-1, pag. 12-66) la reduce a dos columnas (< 2.0 y >= 2.0 ft) y la ajusta por la distribucion longitudinal de la carga en los tubos pequeños (C12.10.4.3.2c). El CPDM manda ademas usar B_fe si es menor que B_fLL; la 9.a ed. no lo dice. M8 sigue la 9.a ed.
- **CPDM-4-2** — El ejemplo (CPDM 2000) y M8 (AASHTO LRFD 9.a ed.) difieren en: W_E sin el termino de los riñones de la Ec. 4 del CPDM (AASHTO 9.a ed. Ec. 12.10.2.1-1: W_E = F_e w B_c H): 27,405 lb/ft contra 27,791; el agua del tubo W_F = 785 lb/ft, que AASHTO 12.10.4.3.1 suma a la tierra y el CPDM no; el factor 1.10 del Tipo 1 (12.10.4.3.1), que el CPDM (2000) no aplica. Lo comun —la Ec. 28 del CPDM y la 12.10.4.3.1-1, el VAF y el B_FE— coincide (contrastes CPDM-VAF y CPDM-BFE). El termino de los riñones vale 301 lb/ft.
- **CPDM-4-5** — El ejemplo (CPDM 2000) y M8 (AASHTO LRFD 9.a ed.) difieren en: W_E sin el termino de los riñones de la Ec. 4 del CPDM (AASHTO 9.a ed. Ec. 12.10.2.1-1: W_E = F_e w B_c H): 4,350 lb/ft contra 4,466; el agua del tubo W_F = 196 lb/ft, que AASHTO 12.10.4.3.1 suma a la tierra y el CPDM no. Lo comun —la Ec. 28 del CPDM y la 12.10.4.3.1-1, el VAF y el B_FE— coincide (contrastes CPDM-VAF y CPDM-BFE). El termino de los riñones vale 80 lb/ft.
- **CPDM-4-7** — El ejemplo (CPDM 2000) y M8 (AASHTO LRFD 9.a ed.) difieren en: W_E sin el termino de los riñones de la Ec. 4 del CPDM (AASHTO 9.a ed. Ec. 12.10.2.1-1: W_E = F_e w B_c H): 840 lb/ft contra 952; el agua del tubo W_F = 196 lb/ft, que AASHTO 12.10.4.3.1 suma a la tierra y el CPDM no; la carga viva HL-93 por 3.6.1.2.6b: W_L = 4,676 lb/ft contra 1,780 de la Tabla 42 del CPDM (HS 20), con B_FLL = 2.40 (Tabla 12.10.4.3.2c-1) contra 2.20 (Ilustracion 4.21). Lo comun —la Ec. 28 del CPDM y la 12.10.4.3.1-1, el VAF y el B_FE— coincide (contrastes CPDM-VAF y CPDM-BFE). El termino de los riñones vale 80 lb/ft.
- **DD22-WI** — El peso sumergido por unidad de volumen es el mismo: DD 22 Ec. 4, w (1 - 1/SG) = 68.49 pcf, y M8 gamma_sat - gamma_w (`M8.peso_relleno_bajo_el_nivel_kn_m`, con el saturado de esa arena). Difiere el VOLUMEN: DD 22 suma el relleno sobre los riñones, 0.1073 B_c^2 (377 lb/ft), y M8 toma el prisma B_c H sobre la clave, la convencion declarada del proyecto (docstring de `M8.peso_relleno_kn_m`), que sujeta menos: del lado seguro en la flotacion. DD 22 redondea ademas w_I a 68 pcf y B_c a 7.17 ft.
- **DD22-V7** — DD 22 (ASD) suma el peso del tubo (1 811 lb/ft) y divide el relleno entre un factor de seguridad de 1.25; V7 de M8 (LRFD, Resistencia I) desprecia el peso propio (DC = 0, conservador) y hace gamma_EV EV - gamma_WA U con gamma_EV = 0.90 y gamma_WA = 1.00 (`M8.factores_carga_flotacion`), sobre el EV sin riñones de DD22-WI. Los dos metodos dan el mismo veredicto: el tubo no flota.

## 5. Lo que coincide

- **DD1-IM-2ft** — La misma ecuacion: DD 1 Eq. 1 y Manual de Puentes 2.4.3.3.2 (`M8.incremento_dinamico_enterrado`).
- **CPDM-VAF-1** — Tabla 12.10.2.1-3 de AASHTO LRFD 9.a ed.: la misma.
- **CPDM-BFE-12-1** — Tabla 12.10.4.3.2a-1 de AASHTO LRFD 9.a ed.: la misma.
- **CPDM-BFLL-36** — Ø 36 in con 2.0 ft: 2.2 en las dos ediciones (Tabla 12.10.4.3.2c-1, «30 and larger»).
- **DD22-U** — La misma ecuacion (gamma_w pi B_c^2/4, `M8.empuje_flotacion_kn_m`); el ejemplo lee 2519 de su Tabla 4 y la Ec. 2 da 2517 con 62.4 pcf, el motor 2519 con 9.81 kN/m3.
- **USACE-T** — ASTM A796 ec. 3, `M8.area_requerida_asd_a796`. La pag. B-9 tiene dos inconsistencias propias que no tocan esta cuenta: escribe EL = 56 550 N/m2 «(1,220 psf)» por 1 200 (10 ft x 120 pcf), y LL = 38 200 N/m2 cuando la suma P = 94 850 usa 38 300, el valor de su tabla para 0.6 m (2 ft) de cubierta, aunque el ejemplo tiene 3 m (10 ft). El contraste parte de P = 94 850 N/m2, como el ejemplo.
- **USACE-A** — ASTM A796 num. 8, con el f_y de 33 000 psi del ejemplo (M8 trae por defecto los 225 MPa de A796-13; aqui se le pasa el del ejemplo).
- **USACE-FC** — ASTM A796 ecs. 5 y 6 = AASHTO 12.7.2.4 (`M8.tension_critica_de_pandeo`); el ejemplo imprime 2.72e8 N/m2 (39 523 psi). Usa S = 1.2 m para el empuje y s = 1 220 mm (48 in) para el pandeo: se respeta.
- **USACE-CLASE-II** — La unica clase transcrita en 'clases_producto_por_relleno' (AASHTO M 170M). USACE imprime ademas I 40, III 65, IV 100 y V 140 N/m/mm (ASTM C76M de su edicion); M8 no las transcribe (ficha de DIFERIDO_CLASES_M170M) y este documento no las usa como fuente: solo el arnes de la D-load ofrece II y V para dejar la cuenta a la vista.

## 6. Erratas de las fuentes

- **CPDM-4-7** — la Ec. 28 imprime el intermedio «D0.01 = 597.3» y la respuesta «563.2»: rehecha con los datos que el propio ejemplo escribe ((952/3 + 1780/2.2)/2) da 563.2, de modo que la errata es el intermedio, no la respuesta. El paso 1 escribe ademas «H = 10» y calcula con H = 2 ft (PL = 680 lb/ft).
- **DD22-WI** — el paso 4 escribe «WB = +4267 + 0 = +4276»: el sumando 4267 es una transposicion de 4276, que es lo que da la Ec. 5 y lo que el ejemplo usa despues.

## 7. Lo que no se contrastó, y por qué

- **PPI, Ejemplos 1 y 2 (HDPE y PP).** El Ejemplo 2 (HDPE de 48 in, 2 ft de relleno) usa un vehiculo de obra (45 kip en 18 x 18 in, IM = 1.0) que M8 no admite —su carga viva es el HL-93 fijo— y un M_s por combinacion de suelos de la Tabla 7.3-6 del PPI (S_c = 0.53 sobre M_sb = 3 500 psi) donde M8 interpola la Tabla 12.12.3.5-1 de AASHTO por la presion; el Ejemplo 1 es de polipropileno, que M8 no trae. Las ECUACIONES coinciden en forma (P_sp con 0.11 D_o, S_H, VAF, F_2, la distribucion con 0.06 D_i y LLDF 1.15), pero ningun numero del ejemplo se puede reproducir con las entradas de M8. (El ejemplo tiene ademas una errata de transcripcion: su VAF escribe «27.98 + 2.92» por 7.98 + 2.92, y el resultado, 0.32, es el de 7.98.)
- **USACE, costura y factor de flexibilidad del TMC (pag. B-11).** M8 verifica la costura y el FF por AASHTO LRFD 12.7.2 dentro de `M8.verificar_tmc`, sin funcion publica para el contraste ASD; y la pagina escaneada da I = «39,198 mm4/mm (2.392 in.4/ft)», que no es una conversion consistente (2.392 in4/ft son 3 266 mm4/mm; 39 198 es 2.392 x 16 387, el factor de in3 a mm3), con FF = 0.00019 mm/N calculado sobre ese I. No se usa como oraculo.
- **USACE, Cap. 3 (tubo de concreto por Marston-Spangler).** D = (W_l + W_e) H_f /(B_f S_i) = 57 N/m/mm (pag. B-8) con el factor de carga de Spangler (cama de cuna de concreto, B_f = 6.098): es el metodo de las camas historicas, que AASHTO 12.10.2.1 sustituye por las instalaciones estandar. Solo su tabla de clases se contrasta (USACE-CLASE-II).

## 8. Observación para el dueño: la carga viva sobre tubos pequeños

No es un defecto —el motor reproduce su metodo en todos los contrastes—, pero es la diferencia mayor de este documento y conviene que la juzgue un ingeniero: con poco relleno, la carga viva de M8 sobre un tubo de concreto pequeño sale bastante por encima de la de ACPA (2000 y 2009): +65 % en DD1-EJ1 (30 in, 2 ft) y la D-load +104 % en CPDM-4-7 (24 in, 2 ft), casi toda por la carga viva. Las causas son de edicion (HL-93 con m = 1.20 y el termino 0.06 D_i desde 2013, frente al HS 20 sin presencia multiple) y de LECTURA: M8 toma W_L = P_L min(l_w, B_c) sin repartir la carga a lo largo del tubo, porque la 9.a ed. no da una longitud efectiva y C12.10.4.3.2c dice que el B_FLL ya esta ajustado por esa distribucion; ACPA (DD 1) la reparte con L_e = L + 1.75 (3/4 R_o). La lectura esta declarada en M8 (paso F8.CLASE_CONCRETO) y va del lado seguro, pero ninguna de estas fuentes resuelve un ejemplo con la edicion 2013 o posterior: hace falta uno para cerrarlo.

## 9. Defectos del motor

Ninguno: en todos los contrastes el motor reproduce su propio método, y donde el ejemplo usa la misma edición, el mismo número.
