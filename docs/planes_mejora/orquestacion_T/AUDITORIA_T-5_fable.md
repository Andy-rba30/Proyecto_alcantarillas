# Auditoría adversarial de T-5 (segunda pasada, independiente) — Fase 8 real del conducto

- Árbol auditado: `/home/user/wt/T-5`, rama `tesis/T-5`, HEAD `ab7fc3a`; diff `git diff 7fb7926 ab7fc3a` (3 commits).
- Solo lectura: el worktree quedó limpio (`git status --short` vacío, HEAD `ab7fc3a`). Base de medida propia:
  `…/scratchpad/T-5-aud-fable/base` (worktree `--detach` de `7fb7926`).
- Evidencia y sondas (todas reproducibles): `/tmp/claude-0/-home-user-Proyecto-alcantarillas/003c3043-1fc3-5405-8650-52c813ca2100/scratchpad/T-5-aud-fable/`
  (`sonda1.py` … `sonda7.py`, `corridas.sh`, `resumen.py`, `out_base/`, `out_t5/`, `esc/`, `mutacion_m8.txt|json`, `m170_*.png`,
  `s3_*.txt`, `s12_*.txt`). Las sondas se corren desde el worktree con
  `PYTHONPATH=/home/user/wt/T-5:<carpeta> PYTHONDONTWRITEBYTECODE=1 python3 <carpeta>/sondaN.py`.
- No leí `AUDITORIA_T-5_opus.md`.

## VEREDICTO: AJUSTADO

Ningún hallazgo BLOQUEANTE. **Diámetros movidos: ninguno** (ni material, ni sección, ni veredicto previo, ni tipo de bloqueo; medido
abajo). Las citas y tablas que T-5 transcribe están, salvo lo que se dice, donde dice y con el número que dice, y los tres dorados
de material se rehacen a mano. Pero hay **dos errores del lado inseguro en la demanda** (H1, H2) que conviene corregir ANTES de
integrar, porque la memoria los imprime como verificación cumplida, y cinco ajustes de severidad media.

| Severidad | Nº | Hallazgos |
|---|---|---|
| BLOQUEANTE | 0 | — |
| ALTA | 2 | H1, H2 |
| MEDIA | 5 | H3, H4, H5, H6, H7 |
| BAJA | 8 | H8 … H15 |

---

## Parada (c): medida con el comparador de E-B

`corridas.sh` corre en los dos árboles las cuatro corridas de la línea base y una quinta sin `--luz`
(perfil estrecha, perfil ancha con `entradas_ampliadas.json`, expediente con y sin externos); después
`python3 cli.py --comparar out_base/X.json out_t5/X.json`:

| Corrida | Diferencias | Qué son |
|---|---|---|
| perfil (estrecha) | 3 | `criterios_sha1`, `sin_valor_declarados` 35→34, `verificacion_pendiente` 24→25 |
| perfil ancha | 17 | las 3 de arriba; el texto del diferimiento de la Fase 8 (A-01, A-02); `estructural` None→bloque; `F8.CLASE` «ausente»→«evaluada» en A-01 y A-02; dos criterios usados nuevos |
| expediente (con y sin externos) | 3 | las tres de huella/recuento |
| perfil sin `--luz` | 3 | ídem |

Los dos CSV de resumen son idénticos byte a byte (`cmp`). Por punto: A-01 y A-02 concreto reforzado Ø 0.90 m en las dos (ahora
con «Clase II»); B-01 «no factible» (V2) en las dos; C-01 detenido en los criterios del cajón en las dos; a expediente los cuatro
se detienen donde se detenían. **Diámetros movidos: ninguno. Materiales movidos: ninguno. Veredictos previos movidos: ninguno.**

Fuera de la línea base SÍ cambia el resultado, y es lo esperable (`esc/esc.csv`, corrida de perfil ancha en los dos árboles):

| Escenario | `7fb7926` | `ab7fc3a` |
|---|---|---|
| S1: A-01 con 3.95 m de relleno | concreto Ø 0.90 | **no dimensiona**: `DatoFaltanteError` (pide 63.5 N/m/mm; solo hay Clase II). El TMC Ø 1.20 cumple todo y NO se acepta (regla T4-10) |
| S3: Q = 6, rasante 52.20 (~8.5 m) | concreto Ø 1.65 | **no factible** (concreto sin clase; TMC y HDPE por diámetro) |
| S4: 0.65 m hasta la rasante | concreto Ø 0.90 | concreto Ø 0.90, Clase II |

---

## REFUTADO CON EVIDENCIA

### H1 · ALTA · El vehículo que «gobierna» se elige por PRESIÓN y no por EFECTO: la demanda sale del lado inseguro

`M8.carga_viva_enterrada` hace `max(candidatos, key=lambda c: c[-1])`, es decir, se queda con el camión o el tándem según cuál dé
mayor `P_L` (kPa). Lo que carga al conducto no es la presión sino `W_L = P_L·min(l_w, B_c)` (concreto, 12.10.2.3) o el término
`P_L·C_L·F_1` (flexibles, 12.7.2.2-1 y 12.12.3.5-1). Con poco relleno y luz grande el camión da más presión sobre un parche corto
y el tándem (ejes a 4 ft, que ya interactúan desde ~0.8 m) da menos presión sobre un parche 1.6–1.9 veces más largo: gobierna el
tándem y el código elige el camión.

Evidencia (`sonda2.py`, `sonda4.py`): 174 combinaciones (D, H) de una malla en que el elegido no es el de mayor efecto.

| Caso | Código (camión) | Por efecto (tándem) | Diferencia |
|---|---|---|---|
| concreto Ø 2.10, H_rel 0.47 m: `W_L` | 65.5 kN/m | 102.4 kN/m | +56 % |
| ídem: D-load requerida | **30.75** (lo que M8 imprime: `F8.CLASE:OK(30.75/50.0)`) | **38.73** N/m/mm | +26 % |
| concreto Ø 2.40 / 2.70, H_rel 0.60–0.65 | 30.1 / 30.4 | 36.1 / 35.5 | +20 % / +17 % |
| concreto Ø 1.80, H_rel 0.50 | 32.8 | 38.8 | +18 % |
| TMC Ø 2.10, H = 1.14 m: término `P_L·C_L·F_1` | 53.6 | 62.7 | +17 % |

Con una sola clase transcrita no cambia hoy ningún veredicto (38.7 < 50), pero la cifra «D-load requerida», el margen y el relleno
máximo que la memoria imprime son falsos por defecto, y con las clases completas cambiaría la clase elegida. Además el test que
debía defenderlo, `_hl93_a_mano` de `tests/test_t5_estructural_conducto.py`, **repite la misma regla** (`if mejor is None or PL >
mejor[0]`): es una segunda copia del criterio, no un contraste.

Corrección: que `carga_viva_enterrada` devuelva los DOS candidatos (o reciba el ancho efectivo / una función de efecto) y que cada
consumidor elija por su efecto: `verificar_concreto._demanda` por `P_L·min(l_w, B_c)`, `verificar_tmc._empuje` y
`verificar_hdpe._estado` por `P_L·C_L·F_1`, `demanda_marco` por `P_L` sobre la luz. Dorado nuevo a mano: concreto Ø 2.10 con
H_rel 0.47 m (38.73 N/m/mm, tándem). El paso `F8.LL` debe decir el vehículo que gobierna EL EFECTO.

### H2 · ALTA · La carga viva se desprecia pasados 8 ft por un PERMISO de la fuente, sin criterio, y eso cambia un veredicto

AASHTO LRFD 3.6.1.2.6a, pág. 3-26 (PDF 80): «the effects of live load **may be neglected** where the depth of fill is more than
8.0 ft and exceeds the span length». Es un permiso (el registro lo tiene bien: `#DESPRECIABLE`, `Caracter.PERMISO`). El código lo
toma siempre (`despreciada = H > 8 ft and H > D_i` → `P_L = 0`), sin criterio [A] ni aviso en `InformePunto.avisos()`: es una
elección del lado NO conservador, que la regla de la cadena manda declarar («elección → [A] con ventana y el más desfavorable
admisible por defecto»).

Evidencia (`sonda4.py`, concreto Ø 0.90, Tipo 3, Clase II = 50.0):

| H_rel (m) | D-load, despreciando (código) | D-load, conservando la carga viva |
|---|---|---|
| 2.2 | 42.79 | 42.79 |
| 2.3 | **37.65** (salto de −14 %) | 43.78 |
| 2.9 | 46.04 → cumple | **50.59 → no alcanza la Clase II** |
| 3.0 | 47.44 → cumple | 51.80 |
| 3.15 | 49.54 → cumple | 53.63 |

El «relleno máximo 3.183 m» de la línea base (A-01, A-02) sale de ahí: conservando la carga viva es ≈ 2.85 m. Entre ~2.85 y 3.18 m
el programa acepta un tubo Clase II que con la carga viva no pasa.

Corrección: por defecto NO despreciar (la carga viva a esa profundidad es chica pero no nula y el método sigue valiendo), y dejar
el permiso como criterio [A] categórico (`carga_viva_bajo_relleno_alto`: `conservar` | `despreciar_3_6_1_2_6a`), barrible; o, si
el dueño prefiere tomar el permiso, que salga como aviso del punto y no solo en el `que` del paso. Regenerar el H_max de la línea
base (movimiento declarado: no es un diámetro).

### H3 · MEDIA · Con los valores por defecto el HDPE no cumple en NINGÚN diámetro ni altura, y no está dicho

`sonda1.py` y `sonda3b.py`: con `relleno_estructural_hdpe = Cl-95`, 75 años, K_γE = 1.5 y A_eff = 0.417·A_g (el mínimo de M 294
7.7), los HDPE de 0.90, 1.05 y 1.20 m fallan `F8.EMPUJE` y `F8.DEFLEXION` en todo relleno de 0.2 a 30 m (solo la carga
permanente de 1 m de tierra ya consume ε = 3.87 % de un límite de 4.1 %). Con Si-95 el de 0.90 cumple hasta 1.48 m; con Sn-95
hasta 2.20 m; con Sn-100, K_γE = 1.0 y 50 años, hasta 7.5 m. El modelo es coherente (lo rehice a mano: ver abajo), pero el
efecto del conjunto de «lo más desfavorable» es **sacar el HDPE del catálogo**. La ficha T5-05 solo dice que «el HDPE de 0.90 m
de A-01 no cumple»; ni la ficha T5-09, ni el contrato de entradas, ni la guía de perfil dicen que con los valores por defecto no
cumple nunca. Antes de T-5 el HDPE era adoptable a nivel de perfil.

Corrección: decirlo con esas palabras en T5-05/T5-09, en `docs/contrato_entradas.md` y en la `justificacion` de
`relleno_estructural_hdpe`; y un test que lo fije (que HDPE × {0.90, 1.05, 1.20} × malla de alturas no cumple con los valores de
archivo y sí con `Sn-95`), para que el día que cambie se vea. **Decisión del dueño** (D1).

### H4 · MEDIA · `fabricacion_tmc` por defecto (remachada simple) no es lo que el EG-2013 describe, y `F8.COSTURA` sale «cumple»

EG-2013 507.02 a), pág. impresa 969 (PDF 977), literal: «Tubos **conformados estructuralmente de planchas o láminas corrugadas**
de acero galvanizado en caliente. Para los tubos, circulares y/o abovedados **y sus accesorios (pernos, tuercas)** de corruga
(68mm x 13mm) […] 900 mm y 2100 mm de diámetro […] El corrugado, **perforado** y formación de las planchas…». Es tubería armada con
pernos. La `justificacion` del criterio dice que la norma «nombra pernos y tuercas entre sus accesorios sin fijar la
fabricación» y adopta la costura REMACHADA simple de la Tabla 5 de ASTM A796 («Riveted or Spot Welded») como «la más desfavorable
de las que tienen resistencia tabulada». Que una costura remachada de 266 kN/m sea más desfavorable que la empernada del producto
peruano no está demostrado por ninguna fuente del repositorio (la propia ficha T5-03 dice que la empernada no tiene tabla): el
valor por defecto imprime `F8.COSTURA [OK]` con la resistencia de otra fabricación. Es exactamente «vender como verificado lo que
no lo está», aunque esté escrito en la ficha.

Corrección (cualquiera de las dos, decide el dueño, D2): (a) dejar el valor por defecto y añadir un AVISO fijo del punto mientras
`fabricacion_tmc` sea el de archivo («la costura se verificó con la resistencia de la remachada simple de ASTM A796 Tabla 5; el
EG-2013 507.02 describe tubería empernada: confirmar con el fabricante»), además de corregir la frase de la `justificacion`; o
(b) dejar `F8.COSTURA` como «no evaluada / dato que falta» por defecto (lo que hoy hace `anular_empernada`) y que AREA y FF sigan
decidiendo.

### H5 · MEDIA · Completar `clases_producto_por_relleno` «sin tocar código» (lo que la ficha T5-02 manda) da resultados falsos

Confirmé la premisa del implementador: renderizadas las páginas PDF 3 a 11 de M 170M (`m170_*.png`), **solo** la D-load de 0.3 mm
de la Clase II se lee («50.0», PDF 5). Clase I: «dtl0» (PDF 3); Clase III: no aparece (solo el «100.0» último, PDF 7); Clase IV:
solo «iS.00» último (PDF 9); Clase V: «\ 40.0» (PDF 11). No es hallazgo contra él. Lo que sí lo es (`sonda5.py`, declarando en
caliente las cinco clases 40/50/65/100/140):

1. Ø 0.90 con 1.0 m de relleno → `sel='Clase I'`. M 170M no tabula la Clase I por debajo de 1500 mm (Tabla 1, PDF 3: primera fila
   1500); el propio criterio lo escribe («La Clase I, además, solo se tabula de 1500 mm en adelante») y el código no lo aplica.
2. Ø 0.90 con 30 m → `DatoFaltanteError`: «Las Clases III a V de AASHTO M 170M existen pero su D-load de 0.3 mm no es legible…».
   Con las cinco declaradas el mensaje es falso y la excepción es la equivocada: no falta un dato, el tubo no cumple. `F8.CLASE`
   lleva `cumple=True` escrito a mano y **no puede** salir `False`; MD lo trata como «escalón sin evaluar» y, por la regla T4-10,
   bloquea también a los materiales que vienen detrás.

Corrección: en `verificar_concreto`, (i) el dict por clase lleva su diámetro mínimo tabulado (o una constante
`DIAMETRO_MIN_CLASE_I_M170M_MM = 1500` con su página) y la clase no se ofrece por debajo; (ii) si la clase que falta está entre las
de `CLASES_M170M` no declaradas → `DatoFaltanteError` como hoy; si están las cinco y ninguna alcanza → `Verificacion` con
`cumple=False` contra la Clase V (NO_CUMPLE: MD prueba el siguiente material). Tests de los dos.

### H6 · MEDIA · Huecos de test que la mutación deja a la vista (arnés de EXT-11 sobre M8)

`python3 -m tests.apoyo.mutacion --modulo src/modulos/M8_estructural.py --funcion … --objetivo
tests/test_t5_estructural_conducto.py --objetivo tests/test_M8_estructural.py`: **559 mutantes, 436 muertos (78 %), 123 vivos**
(`mutacion_m8.txt`). Por función: `verificar_hdpe` 165/196, `verificar_tmc` 72/110, `verificar_concreto` 32/41,
`_relleno_maximo` 9/23, `tension_critica_de_pandeo` 14/23, `carga_viva_enterrada` 17/25, `_presion_de_un_vehiculo` 33/36,
`demanda_marco` 20/21. Los vivos que importan (el resto son fronteras `<`/`<=` y textos):

- **El umbral de la deflexión del HDPE no está fijado**: `params['deflexion_admisible'] * D` → `/ D` sobrevive (0.045 m pasa a
  0.0556 m y ningún test lo nota: el único dorado no cumple con los dos).
- **La rama elástica del pandeo del TMC (Eq. 12.7.2.4-2) no la toca ningún test**: `return 12*E/esbeltez**2` → `None`, `12` → `13`,
  `**2` → `*2`, y el `24` del umbral, todos vivos. (Con el catálogo de 68 × 13 hasta 2.10 m no se alcanza —el umbral es S ≈ 2.47 m—,
  pero `tension_critica_de_pandeo` es pública y `area_requerida_asd_a796` la llama.)
- **El relleno máximo del HDPE y el del TMC por área no se prueban**: los tres términos de `_margen` de `verificar_hdpe` con el
  signo cambiado, `if cumple_todo` → `if not cumple_todo` (HDPE y TMC) y `A*phi*f_res` → `A*phi/f_res` sobreviven.
- **`test_el_relleno_maximo_es_el_PRIMER_cruce_y_no_cualquiera` no defiende el muestreo**: `(H_techo - H_rel) / TRAMOS` → `* TRAMOS`
  sobrevive (un solo tramo, Brent sobre el intervalo entero: justo lo que el test dice impedir), y también `i * tramo` → `i / tramo`.
- **La rama del nivel freático** (`NF_profundidad_m`) del TMC y del HDPE: cuatro signos vivos en cada una (`cota_terreno - nf` →
  `+`, etc.). Medí que con el fondo adoptado igual al terreno la rama casi no se alcanza (`sonda6.py`: NF = 0 da el mismo P_w),
  pero entra en cuanto haya `cota_fondo_entrada` medida por debajo del terreno, y es un dato de sitio que mueve el empuje.
- El contraste ASD dentro de `verificar_tmc` (`P_sp + P_L` → `-`), el relleno recalculado por plancha (`H_rel0 - (…)` → `+`), los
  márgenes de todos los veredictos (`eps_lim - eps_uc` → `+`, `D_clase - D_req` → `+`) y `H_total_m` del concreto.
- `demanda_marco`: `gamma_s * H_rel` → `/ H_rel` sobrevive porque el test usa `altura_relleno=1.00`.

Corrección: un dorado de HDPE que CUMPLA (p. ej. Sn-95, 0.90 m, 1.0 m: ε = 0.0304, u = 0.124, Δ = 0.0251 m, H_max 2.199 m) con
Δ_A afirmado; un caso de la Eq. 12.7.2.4-2 a mano; H_max del TMC helicoidal (gobierna el área); el test del primer cruce con una
función cuyo segundo cruce Brent encontraría; un caso con NF sobre la clave; el marco con H ≠ 1.

### H7 · MEDIA · `Umbral.caracter = "EXIGENCIA"` escrito a mano para TODAS las F8, incluido el 5 % de deflexión

`M8._campos_f8` fija `caracter="EXIGENCIA"`. En `F8.DEFLEXION` el umbral (5 % del diámetro) no es una exigencia de la fuente:
12.12.2.2 exige Δ_t ≤ Δ_A y es C12.12.2.2 (pág. 12-74, comentario) quien dice «The construction specifications set the allowable
deflection, ΔA, for thermoplastic pipe at five percent as a generally appropriate limit», y el valor es además un campo [A]
(`parametros_diseno_hdpe.deflexion_admisible`, ventana 0.02–0.05). El texto de `aplicacion` lo aclara («la RECOMENDACION de
C12.12.2.2 aplicada como umbral duro por decisión del proyecto»), pero el campo que M11 imprime como «carácter en la fuente» dice
EXIGENCIA y el `cita_id` del umbral apunta a 12.12.2.2 y no a C12.12.2.2: es NOR-MEM-01 en pequeño. Lo mismo, más leve, en
`F8.FF` («exigencia de manejo e instalación»: C12.5.6.1 dice que no representa ningún estado límite en servicio; la tabla sí es
«shall not exceed»).

Corrección: `_campos_f8` recibe `caracter`; `F8.DEFLEXION` → RECOMENDACION con `cita_umbral="AASHTO_LRFD_9.C12.12.2.2"`.

### H8 · BAJA · «Medido en tests/test_nivel_medido.py» es cierto para dos de los seis criterios

El bloque de `criterios_adoptados.py` dice de los cinco nuevos: «los invocan las verificaciones F8.* de la Fase 5 … (medido en
tests/test_nivel_medido.py)». `tests/test_nivel_medido.py` no cambió en el diff, y las corridas de referencia solo invocan
`clases_producto_por_relleno` e `instalacion_estandar_concreto` (comparador: son los dos únicos criterios «presentes» nuevos; el
README de la línea base lo dice bien). `fabricacion_tmc`, `eta_importancia_operativa_conducto`, `relleno_estructural_hdpe` y
`parametros_diseno_hdpe` son de perfil por ARGUMENTO, no por medida. CLAUDE.md pide decir qué corrida midió cada uno o decir que no
se puede medir. Corrección: una corrida de medida que llegue al TMC y al HDPE (el concreto excluido por durabilidad o por
`D_max_catalogo`), o reescribir el comentario.

### H9 · BAJA · Código muerto: la fila «< 2.0 ft» de B_FLL

En `verificar_concreto._demanda`, `fila = BFLL_RELLENO_MENOR_2_PIES if H + e_paq < 2 ft` no se alcanza nunca:
`carga_viva_enterrada` ya levantó `MetodoNoEvaluableError` para un tubo de concreto con menos de 2.0 ft. La constante
`BFLL_RELLENO_MENOR_2_PIES` no tiene consumidor real (mutante `<` → `<=` vivo). Quitar la rama o decirlo.

### H10 · BAJA · Docstrings y textos que quedaron atrás

- `servicio.correr_punto`: «Con alcance de perfil … la Fase 8 no se ejecuta: queda como bloqueo diferido» (ya no es verdad).
- `M8.pesos_especificos_de_carga`: el «piso de AASHTO LRFD 12.10.2.1, 110 lb/ft³» (17.28 kN/m³) no puede gobernar nunca, porque
  el 0.120 kcf del Manual (18.85) entra siempre en el `max` (mutante `if piso_tubo_concreto` → `if not` vivo). Es decorativo: decirlo.
- T5-09 dice que los cinco [A] traen «lo más desfavorable»: `nu_suelo = 0.40` no lo es dentro de su ventana (0.25–0.45; 0.45
  reduce más el pandeo), ni `K_B = 0.10` (0.110) ni `D_L = 1.5` (6.0). La `justificacion` del criterio sí dice «típico»; la ficha no.

### H11 · BAJA · `verificacion_diferida` imprime la lista global, no la del material

`ResultadoEstructural.diferido` existe por material, pero el JSON (`cli._estructural_json`) y la memoria (`M11`) imprimen
`verificacion_diferida_estructural()` entera: el bloque de A-01 (tubo de concreto) lista el pórtico del marco, la flexión del HDPE
y la costura empernada del TMC. No vende nada como verificado, pero tampoco es «solo lo que sigue diferido» de ESE conducto.
Corrección: imprimir `r.diferido` (y completar el del concreto con `DIFERIDO_CLASES_M170M`, el del TMC con la costura empernada).

### H12 · BAJA · Dorados que repiten la fórmula del código

- `test_el_marco_da_la_demanda…`: el docstring dice «Calculado a mano» y el cuerpo recalcula con las mismas expresiones y las
  constantes de `CN`. (A mano de verdad, independiente: F_e = 1.10; w_EV = 24.364 kPa; P_L = 34.25 kPa, camión; w_u = 97.47 kPa;
  M_ref = 56.32 kN·m/m — coincide con M8, `sonda7.py`.) Poner esos números como dorado.
- `test_con_relleno_somero_y_luz_grande_F1…`: reconstruye T_L con la fórmula de M8 y las magnitudes del propio paso.
- `_hl93_a_mano`: ver H1.

### H13 · BAJA · Pie de los tres commits

Los tres llevan `Co-Authored-By: Claude Opus 5.5` y otra URL de sesión; ORQUESTACION manda el pie literal (otro modelo, sesión
`session_015HTdHjggReUnNNncetQU39`). Se corrige al aplastar en la FASE B. Ojo también: `MetodoNoEvaluableError(rotulo=)` lo
añade T-5 a `modelos.py` por su cuenta y `origin/main` ya lo trae de T-1: conflicto seguro en el rebase.

### H14 · BAJA · Entradas raras que pasan sin decirlo

- `carga_viva_enterrada(conducto="lo_que_sea")` se trata como concreto/cajón (no hay guardia del conjunto cerrado).
- `_clases_transcritas` ignora en silencio una clave que no sea I…V (`{"VI": 200}` desaparece).

### H15 · BAJA · El contraste ASD mezcla la carga viva de LRFD en una cuenta de A796

`F8.ASD` usa `P_sp + P_L` con el `P_L` del HL-93 (con m = 1.20 e IM del Manual) y el SF = 2 de A796. No hay γ/φ de LRFD junto a un
FS (lo comprobé; el test por AST también), está rotulado «NO RIGE» y el paso dice «HL-93, no la H20 del núm. 6.2.2.1». Solo falta
decir que la presencia múltiple de 1.20 es un concepto de LRFD que A796 no tiene: el número no es «A796 puro».

---

## SOSPECHA NO COMPROBADA (o lectura declarada que debe ver el dueño)

- **12.7.2.2 sin K_γE.** La fuente dice «P_FD = factored dead load vertical crown pressure as specified in Article 12.12.3.4 with
  VAF taken as 1.0 and D_o taken as S» (pág. 12-25). La ecuación a la que remite (12.12.3.5-1) lleva K_γE·K_2. El implementador lee
  la remisión SIN K_γE (nota del paso `F8.T`, ficha T5-04) apoyándose en C12.7.2.2. Me parece la lectura correcta (γ_EV = 1.95 del
  metal ya trae la seguridad tradicional; 1.95 × 1.5 sería absurdo), pero es la lectura del lado de la menor demanda y la letra no
  la dice.
- **Baterías de tubos.** 3.6.1.2.6a da otra condición para despreciar la carga viva en alcantarillas de varios vanos (relleno
  mayor que la distancia entre caras interiores de los muros extremos). `carga_viva_enterrada` solo conoce la de un vano. No medí
  si una batería (`numero_celdas > 1`) de circulares llega a la Fase 8 con esa regla.
- **Tablas 5 y 7 de ASTM A796 (costura).** No las releí por imagen en esta pasada: las cifras (244/266/341/357/374 simple;
  315/435/683/715/748 doble) ya estaban en el registro antes de T-5 y coinciden con la conversión de la Tabla A12-2 de AASHTO
  que recuerdo, que no es una verificación.
- **«VARIOS».** El PDF no está: lo único comprobable es que la aritmética reproduce las cifras del INFORME §1.1 (C = 40.725,
  A = 0.354 con f_y 230), y que está rotulado «según el INFORME §1.1; páginas no verificadas» en el caso patrón, en el test y en la
  ficha T5-04. El FF 0.109 no se reproduce y está dicho (corresponde a I ≈ 37.1 mm⁴/mm, otra tabla de propiedades).

---

## LO QUE VERIFIQUÉ Y ESTÁ BIEN

**Contra el PDF (texto extraído, página impresa / PDF):**

- AASHTO LRFD 9.ª: 3.6.1.2.6a (3-26 / 80: dominios 1.0 ft y 2.0 ft, un carril, solo ejes, permiso de 8 ft); Tabla 3.6.1.2.6a-1
  (3-27 / 81: 1.15 – 1.75, interpolación); Eqs. 3.6.1.2.6b-1 a -7 (3-27/3-28: `0.06 D_i`, `s_w` 6 ft, `w_t` 20 in, `l_t` 10 in);
  12.5.4 (12-11 / 1649: «buried structures shall be considered **redundant**» — η_R = 1.00 es correcto en la 9.ª); Tabla 12.5.5-1
  (12-12 / 1650: metal 1.00 y 0.67; PE 1.00 / 0.90 / 0.70); Tabla 12.5.6.1-1 (12-13: 43, 43, 33 in/kip → 0.2455 mm/N);
  12.7.2.2 a 12.7.2.4 (12-25/12-26: T_L, C_L, F_1, F_min = 15/(12S) ≥ 1, f_cr, k = 0.22); Tabla A12-9 (12-107: 45 / 33 / 29 000);
  12.10.2.1 (12-52: W_E = F_e w B_c H, 110 lb/ft³), Tabla 12.10.2.1-3 (VAF 1.35/1.40/1.40/1.45), 12.10.2.2, 12.10.2.3,
  12.10.4.3.1 (12-64: ecuación y 1.10 del Tipo 1), Tabla 12.10.4.3.2a-1 (las 20 celdas), Tabla 12.10.4.3.2c-1 (las 8 celdas);
  12.11.2.1 y 12.11.2.2.1 (12-68/12-69: F_e = 1 + 0.20 H/B_c ≤ 1.15 / 1.40); 12.12.2.2 (ecuación de Spangler, D_L 1.5, K_B 0.10,
  0.083–0.110, 1.0–6.0); Tabla 12.12.3.3-1 (fila M 294: 5.0 / 4.1 / 3.0 / 110 / 0.90 / 22 / 0.90 / 21); 12.12.3.5 (T_u, T_s, VAF,
  S_H, C_L, F_1, F_min = 15/D_i, F_2, K_γE 1.5, K_2); Tabla 12.12.3.5-1 (las 24 celdas de Sn-100, Sn-95, Si-95 y Cl-95, incluida
  la celda vacía de Si-95 a 60 psi); 12.12.3.7-3 (0.11 D_o); Eq. 12.12.3.10.1b-5 y Tabla 12.12.3.10.1b-1 (0.9 / 0.3 / 0.25);
  12.12.3.10.1c-e (C_n 0.55, R_h = 11.4/(11 + D/12H)); Tabla A12-11 (las 8 filas y la llamada «*» de 42 y 48 in).
- Manual de Puentes: 2.4.3.2.2.2/.3/.5 (104 / 105: 32.0 kip, 14.0–30.0 ft, 25.0 kip a 4.0 ft, 6.0 ft, 20 × 10 in); 2.4.3.3.2
  (109 / 110: IM = 33(1.0 − 0.125 D_E) ≥ 0 %, D_E en ft); Tabla 2.4.2.1-1 (102 / 103: 0.120 y 0.140 kcf, «a falta de una
  información precisa, podrán usarse»); 2.3.2.5 (99 / 100: ≥ 1.05, 1.00, ≥ 0.95).
- EG-2013: Tabla 507-01 (970 / 978: las cinco filas); 508.07 (984 / 992: > 95 % del Proctor Modificado, relleno de la Sección
  502); 506.02 y 506.10 (959, 961); 205.12 (193 / 201: 90 % base y cuerpo, 95 % corona); 507.02 a) (969 / 977; ver H4).
- AASHTO M 294 (traducción), 7.7, hoja 8: el 50 % del área bruta por el límite elástico mínimo.
- AASHTO M 170M: ilegibilidad confirmada por imagen (ver H5).
- `tests/test_normativa_pdf.py`, `test_t5_estructural_conducto.py`, `test_M8_estructural.py`, `test_nivel_medido.py`,
  `test_cierre_perfil.py`, `test_sin_literales.py`: verdes con `NORMAS_DIR` (código de salida 0). No corrí la suite entera.

**A mano (aritmética propia, sin el código), sobre A-01:**

- Concreto Ø 0.90, Tipo 3: H_rel 0.95 m, e 0.15 m; γ_s 18.850; W_E = 1.40·1.10·(17.908 + 3.299) = 32.658 kN/m; W_F = 6.241;
  LLDF 1.2453; IM 20.14 %; camión con ruedas interactuando: w_w 3.7606, l_w 1.6238, P_L = 33.607 kPa (tándem 29.99);
  W_L = 33.607·1.10 = 36.968; B_FE 2.3047, B_FLL 2.2; D = (16.878 + 16.804)/0.9 = **37.424 N/m/mm** = lo que imprime M8. Clase II.
- TMC Ø 0.90, 68×13/2.01: H 1.185 m; P_L 33.49 kPa; P_sp 22.809; P_w 4.562; P_FD = 1.05(1.95·22.809 + 4.562) = 51.49;
  T_L = 23.17 + 27.69 = **50.865 kN/m**; f_cr = 42.0 ksi > F_y; A_req = 50.865/227.5 = **0.2236 mm²/mm** (2.049 disponibles);
  costura 0.67·266 = 178.2 ≥ 50.9; FF = 900²/(199 948·39.2) = **0.1033** ≤ 0.2455. Coincide.
- HDPE Ø 0.90 (perfil mínimo de 36 in, Cl-95, 75 años): P_sp 493.6 psf; M_s 0.5877 ksi; S_H 1.3085; VAF 0.7367;
  T_d = 1.05(1.3·1.5·0.7367·493.6 + 110.5)·1.7708 = 1524 lb/ft; ε_d = 127.0/3281 = 0.0387; con la carga viva, ε = 0.0479 > 0.041:
  **no cumple**, como dice el caso patrón. Órdenes de magnitud sensatos; el factor 1.95 total es γ_EV 1.30 × K_γE 1.5.
- Marco 2.00 × 1.50, t 0.15: ver H12 (56.32 kN·m/m; coincide).

**Marco de verificación:** TMC y HDPE por LRFD (γ de la Tabla 2.4.5.3.1-2 del Manual: 1.95 flexible, 1.30 termoplástico; γ_LL
1.75; φ de 12.5.5-1; η solo en resistencia), concreto por el método indirecto en servicio (sin γ ni φ), deflexión del HDPE en
servicio, A796 solo como contraste. No encontré ningún γ/φ combinado con un FS.

**Robustez** (`sonda1.py`, `sonda5.py`; 3 materiales × 5–7 diámetros × 12 alturas de 0 a 10⁴ m, y 18 declaraciones raras):
ninguna excepción fuera de `ErrorProyecto`. H = 0 → `DatoInvalidoError`; relleno somero → `MetodoNoEvaluableError` con su rótulo
propio; concreto > 2.70 y HDPE 1350/1500 → `DatoFaltanteError` en el espesor (antes de la Fase 8); TMC sin plancha que cumpla →
verificaciones `False` y `seleccion=''`; costura empernada y corrugación sin costura tabulada → `DatoFaltanteError`; marco sin
criterios → `CriterioPendienteError`; NaN / inf / negativos → `DatoInvalidoError` (forma MAT-D13). La puerta de los criterios
rechaza `tipo_4`, η = 1.2, ν = 0.5, años = NaN y un dict con campos de más o de menos. No queda ningún `raise AssertionError` en
M8. CLI de texto, JSON y memoria reciben `estructural` con `None` bien tratados; los CSV de resumen no cambian.

**Residuos declarados:** costura empernada, flexión combinada del HDPE, plancha que no vuelve a 7.A/V7, D-load ilegible, pórtico
del marco: las cinco tienen ficha (T5-02, T5-03, T5-05, T5-07) con símbolo, y la memoria los lista en «Fase 8 — Lo que no se
verifica». Salvedades: H4 (la costura por defecto) y H11 (lista global).

---

## DECISIONES QUE SON DEL DUEÑO

- **D1 · Relleno del HDPE por defecto (`Cl-95`, con 75 años y K_γE 1.5).** Deja al HDPE fuera en todo punto (H3). Alternativas
  dentro de la ventana: `Si-95` (0.90 m cumple hasta 1.48 m) o `Sn-95` (2.20 m). ¿Se confirma «arcilla» como lo que el EG-2013
  508.07 / Sección 502 admite alrededor de un tubo plástico?
- **D2 · Fabricación del TMC por defecto.** Remachada simple (A796) frente a la tubería empernada que describe EG-2013 507.02 (H4).
- **D3 · Instalación del tubo de concreto: Tipo 3**, y la lectura de que el EG-2013 excluye el Tipo 4 y no alcanza el Tipo 1.
- **D4 · η_I = 1.05** («puente crítico o esencial») mientras el Propietario no declare la importancia; 1.00 es «típico».
- **D5 · Despreciar o no la carga viva pasados 8 ft** (H2): propongo conservarla por defecto.
- **D6 · Conseguir un M 170M / ASTM C76M legible.** Hasta entonces el tubo de concreto solo existe en Clase II: con el Tipo 3 eso
  son ~2.4 a 3.2 m de relleno según el diámetro, y por la regla T4-10 un punto con más relleno NO se dimensiona aunque un TMC
  cumpla (escenario S1). ¿Se acepta ese bloqueo, o el dato que falta en el concreto debe dejar pasar al TMC con aviso?
- **D7 · Tres lecturas del proyecto en el HDPE y el TMC**: 12.7.2.2 sin K_γE; la deformación del HDPE sumada por duración con
  A_eff = 0.5·A_g·F_u,ini·K_t/F_u (mínimo de M 294 7.7); ν = 0.40 sin fuente.
- **D8 · La Fase 8 a nivel de perfil** (enmienda a la v8, ficha T5-01): no mueve la línea base; fuera de ella sí cambia qué se
  dimensiona (S1, S3, el caso G2 de T-4).
