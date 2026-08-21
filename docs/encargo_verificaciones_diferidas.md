# Verificaciones diferidas por nivel de estudio — hoja de trabajo para Claude Code

**Repositorio:** `Andy-rba30/Proyecto_alcantarillas` · **Base:** commit `c890ed7`

---

## Cómo usar esta hoja

1. **Guarda este archivo en el repo** como `docs/encargo_verificaciones_diferidas.md`
   y haz commit. Los prompts lo referencian, así que Claude Code puede releerlo si
   pierde contexto.
2. **Copia los prompts uno por uno**, en orden. Cada bloque gris se pega tal cual.
3. **Después de cada uno, mira el diff** antes de seguir. Bajo cada prompt hay
   una línea de "qué revisar" — es para ti, no se pega.
4. **No los juntes.** Los pasos 2 a 5 son cuatro conversiones parecidas y ahí es
   donde un asistente acelera y generaliza de más.

Son once prompts. Los pasos 0 y 6 no escriben código.

---

# Contexto (esto lo lee Claude Code en el paso 0)

## A dónde va el programa

El objetivo final de esta herramienta es producir, para cada punto crítico del
corredor, **la geometría real de la obra**: material y diámetro adoptados,
longitud del conducto, esviaje, cotas de entrada y salida, pendiente, las
dimensiones del enrocado de protección y la geometría del cabezal. Con eso el
proyecto arma un modelo 3D y los planos.

Ese esqueleto ya existe en el JSON que emite M11: los nodos `diseno`,
`geometria`, `proteccion_salida` y `cabezal.geometria`. Hoy salen todos en
`null` porque **ningún punto llega a `dimensionado = True`**.

Este encargo destraba eso.

## Por qué hoy no cierra ningún punto

El pipeline se detiene en cuatro sitios con el mismo patrón:

```python
ca.valor(CRITERIO_X)      # CriterioPendienteError mientras el criterio esté vacío
raise AssertionError("inalcanzable mientras 'X' este vacio")
```

Son **topes declarados**, no errores de programación. Mientras el criterio está
vacío se comportan como bloqueo limpio; si se les da valor, la línea siguiente
aborta la corrida entera, porque el cálculo que consumiría ese valor nunca se
escribió.

| # | Qué es | Dónde | Criterio |
|---|---|---|---|
| 1 | **V8** — evento extremo (FEN) | `M5_verificaciones.py:447-448` | `TR_evento_extremo` |
| 2 | **V5** — remanso aguas arriba | `M5_verificaciones.py:322-324` | `remanso_derecho_via`, y detrás `ancho_derecho_via_m` |
| 3 | **Fase 8** — clase/calibre por norma de producto | `M8_estructural.py:187-190` | `clases_producto_por_relleno` |
| 4 | **E4/E5** — estabilidad global del cabezal | `M9_cabezal.py:979-981` y `:995-997` | `metodo_estabilidad_global` |

Dos más con el mismo patrón **no entran** en este encargo:
`M9_cabezal.py:1086-1088` (`N_cq_N_gammaq_meyerhof`, que además nadie llama
desde la CLI) y `M7_geometria.py:267-270` (`h_relleno_min_concreto_tmc`, que
solo se dispara cuando M2 dejó el campo en `None` — se resuelve solo en el
paso 8).

## La decisión de proyecto que hay detrás

Este trabajo es una **propuesta de diseño a nivel perfil**, no un expediente
técnico definitivo. El Manual de Suelos del MTC reconoce el nivel perfil como
etapa con su propia densidad de investigación exigida; el repositorio ya lo cita
en `constantes_normativas.py` (`ESPACIAMIENTO_PERFIL_KM = 4.0  # nivel perfil`).
La campaña geotécnica es coherente con ese nivel: 5 calicatas en 5 km, sin SPT,
corte directo ni ensayos químicos completos.

**Las cuatro verificaciones pertenecen al nivel de expediente definitivo y se
difieren, con su fundamento declarado.** No se calculan, no se aproximan y no se
ocultan.

Esta decisión ya está tomada. No se vuelve a evaluar.

## Por qué esta forma no hipoteca el futuro

El objetivo declarado del proyecto es que la herramienta llegue algún día a
producir expedientes completos.

**La interfaz de hoy es la misma que la de mañana.** El día que se implemente el
perfil de remanso completo de V5, se cambia el cuerpo de esa función para que
devuelva `cumple=True/False` con su valor numérico. MD, M11, la CLI y la GUI **no
se tocan**: ya saben leer un `Verificacion`. La costura queda en la función, que
es donde debe estar.

**Por eso no se implementa un "modo perfil" conmutable.** Un interruptor supondría
dos rutas vivas y la segunda no existe: hoy alternaría entre diferir y abortar.
Cuando el cálculo de expediente exista, el nivel de estudio podrá convertirse en
una bifurcación real dentro de cada función, sin rediseñar nada.

## Reglas que aplican a toda la sesión

- **No inventes numerales, valores ni fundamentos.** Si algo de este documento no
  coincide con el repositorio o con la hoja de ruta, **detente y avísalo**.
- **No declares ningún criterio de `criterios_adoptados.py`.** Este encargo no
  rellena criterios: cambia cómo se reporta su ausencia. `TR_evento_extremo`,
  `clases_producto_por_relleno`, `metodo_estabilidad_global` y
  `N_cq_N_gammaq_meyerhof` **se quedan vacíos**.
- **No toques los otros dos topes** (`M9:1086`, `M7:267`).
- **No borres ni simplifiques** el sistema de etiquetas, los criterios adoptados
  ni el manifiesto de citas. Es el núcleo del trabajo.
- **No difieras ninguna verificación fuera de las cuatro nombradas.** Si aparece
  una quinta que bloquea, avísalo en vez de diferirla.
- Si un cambio exige tocar más de un módulo a la vez, **para y explícalo** antes.
- Commit por paso, con el nombre del módulo en el mensaje, como pide `Claude.md`.

---

# Los prompts

## Paso 0 — Reconocimiento

```
Vas a trabajar en este repositorio siguiendo el encargo que está en
docs/encargo_verificaciones_diferidas.md.

En este paso NO escribas ni modifiques nada. Solo lee y reporta.

1. Lee Claude.md completo.
2. Lee docs/encargo_verificaciones_diferidas.md completo.
3. Lee estas partes del código:
   - modelos.py, la clase Verificacion
   - M8_estructural.py, la funcion verificacion_diferida_estructural (M8:322)
     y donde cli.py la imprime (cli.py:884). Es el patron que este encargo
     generaliza.
   - Los cuatro topes: M5_verificaciones.py:447-448 y :322-324,
     M8_estructural.py:187-190, M9_cabezal.py:979-981 y :995-997
   - datos_sitio.py, la entrada PGA_roca_B, como modelo de forma
4. Corre la suite de tests y dime el estado de partida.

Despues dime, en no mas de 15 lineas: que entendiste que hay que hacer, y si
encontraste alguna discrepancia entre el encargo y lo que dice el codigo.

No propongas enfoques alternativos al del encargo.
```

> **Qué revisar:** que los cuatro topes que encontró coincidan con la tabla, y
> que los tests pasen de entrada. Si reporta una discrepancia, resuélvela antes
> de seguir.

---

## Paso 1 — El tipo y el dato de nivel

```
Paso 1. Dos cambios aditivos, ninguno toca logica de negocio.

a) En modelos.py, clase Verificacion:
   - cumple: bool  ->  cumple: Optional[bool]
   - agrega el campo: nota_diferida: Optional[str] = None
   En el docstring, documenta los tres estados: True cumple, False incumple,
   None diferida (no se evaluo, con razon declarada en nota_diferida).

b) En datos_sitio.py, agrega una entrada a DATOS_SITIO con la misma forma que
   PGA_roca_B:
     clave:  nivel_estudio
     valor:  "perfil"
     concepto: nivel de profundidad del estudio
     fuente: Manual de Suelos MTC, num. 4.2, Cuadro 4.1
     procedimiento: declarado por el proyecto (5 calicatas en 5 km, sin SPT,
       corte directo ni ensayos quimicos completos)
     trazabilidad: corresponde a la densidad de investigacion del Cuadro 4.1
       para nivel perfil, no a la de expediente definitivo

   Antes de escribirla, verifica que el numeral 4.2 / Cuadro 4.1 sea correcto
   contrastandolo con lo que ya cita constantes_normativas.py en
   ESPACIAMIENTO_PERFIL_KM. Si no coincide, PARA y avisame.

Corre la suite completa. No debe romperse nada: el campo nuevo lleva default.
Muestrame el diff.
```

> **Qué revisar:** que ningún `Verificacion(...)` existente haya sido modificado.
> Si tocó más de dos archivos, algo se desvió.

---

## Paso 2 — V8

```
Paso 2. Convierte V8 en verificacion diferida. Ubicacion: M5_verificaciones.py:447-448.

Hoy:
    ca.valor(CRITERIO_EVENTO_EXTREMO)
    raise AssertionError("inalcanzable mientras 'TR_evento_extremo' este vacio")

Las DOS lineas se van, no solo el raise. La funcion pasa a devolver un
Verificacion con:
    cumple = None
    codigo = "V8"
    numeral = el que ya usa la funcion
    valor_obtenido = None, valor_admisible = None
    criterio_aplicado = None
    nota_diferida = texto que diga TRES cosas: (1) que V8 se difiere al
      expediente tecnico; (2) que a nivel perfil (Manual de Suelos num. 4.2)
      no estan definidos ni el TR mayor del regimen FEN ni el umbral
      cuantitativo de colapso -- p.ej. HW sobre la corona del terraplen; y
      (3) que haria falta para dejar de diferirla.

Por que se retira tambien la llamada a ca.valor: Claude.md dice que cada
invocacion de un criterio se registra para que M11 imprima solo los usados.
Una verificacion diferida no aplico el criterio a nada; dejar la llamada lo
haria figurar como usado, que seria falso.

NO le des valor a TR_evento_extremo. Sigue vacio.

Corre los tests de M5. Si alguno espera el AssertionError, actualizalo para
que espere el Verificacion diferido, y dime cual cambiaste y por que.
Muestrame el diff.
```

> **Qué revisar:** que `ca.valor` haya desaparecido de esa función y que la nota
> tenga las tres partes. Esta es la conversión modelo: si sale bien, las tres
> siguientes son mecánicas.

---

## Paso 3 — V5

```
Paso 3. Misma conversion que el paso 2, ahora para V5.
Ubicacion: M5_verificaciones.py:322-324.

Este tope tiene dos capas: ca.valor(CRITERIO_REMANSO) y, detras, un
DatoFaltanteError("ancho_derecho_via_m") que ademas no tiene ninguna via de
entrega en el codigo. Las dos capas se van.

Verificacion diferido con codigo "V5" y nota_diferida que diga: que se difiere
al expediente tecnico; que requiere un perfil de remanso (paso a paso o
HEC-RAS) y el ancho de derecho de via legal por punto, ninguno definido a
nivel perfil; y que eso es lo que haria falta para dejar de diferirla.

NO declares remanso_derecho_via ni abras una entrada para ancho_derecho_via_m.

Corre los tests de M5, incluido tests/test_M5_verificaciones.py:249 que hoy
afirma sobre el DatoFaltanteError. Muestrame el diff.
```

> **Qué revisar:** que haya quitado las dos capas, no solo la primera. El test
> de la línea 249 tiene que haber cambiado.

---

## Paso 4 — Fase 8

```
Paso 4. Misma conversion, ahora para la clase/calibre de norma de producto.
Ubicacion: M8_estructural.py:187-190.

Verificacion diferido con nota_diferida que diga: que se difiere al expediente
tecnico; que requiere transcribir la tabla clase/calibre x diametro x rango de
altura de relleno de AASHTO M-170M (concreto) y ASTM A-807 / AASHTO M36 (TMC),
y ramificar por material; y que eso es lo que falta.

Ojo con un detalle ya conocido: cli._fase_8 llama a esta verificacion para
TODO material, aunque el docstring diga que HDPE esta exento. No lo arregles
en este paso -- solo anotalo en tu respuesta si lo confirmas.

NO declares clases_producto_por_relleno.

Este modulo ya tiene verificacion_diferida_estructural para su item 5. Deja
las dos conviviendo; no unifiques ni refactorices esa funcion.

Corre los tests de M8. Muestrame el diff.
```

> **Qué revisar:** que no haya tocado `verificacion_diferida_estructural`. La
> tentación de unificar las dos es real y aquí sería un error: una devuelve
> texto por diseño previo, la otra devuelve `Verificacion`.

---

## Paso 5 — E4 y E5

```
Paso 5. Ultima conversion: la estabilidad global del cabezal.
Ubicaciones: M9_cabezal.py:979-981 (E4, verificar_estabilidad_global) y
M9_cabezal.py:995-997 (E5, verificar_talud).

Son dos funciones, mismo criterio (metodo_estabilidad_global) y misma razon.
Convierte las dos.

nota_diferida: que se difiere al expediente tecnico; que requiere el analisis
de estabilidad global por equilibrio limite del EMS, con su metodo y sus
superficies criticas -- que es lo que la propia justificacion del criterio ya
dice; y que eso es lo que falta.

NO declares metodo_estabilidad_global.
NO toques M9:1086 (N_cq_N_gammaq_meyerhof). Queda fuera de este encargo.

Nota de contexto: cli.py no ensambla E1-E5 todavia (ver
cli.NOTA_ESTABILIDAD_CABEZAL, cli.py:153), asi que estas dos no se alcanzan
hoy desde la CLI. Se convierten igual, para que el dia que se ensamblen no
aborten.

Corre los tests de M9. Muestrame el diff.
```

> **Qué revisar:** que haya convertido las dos y no solo una, y que `M9:1086`
> siga intacto.

---

## Paso 6 — Inventario de los nueve `.cumple`

```
Paso 6. Solo lectura. No cambies nada todavia.

Corre:  grep -rn "\.cumple\b" src/ cli.py

Para cada resultado, dime en una linea:
  - que hace hoy con cumple = True y con cumple = False
  - que haria HOY con cumple = None, tal como esta escrito ahora
  - que deberia hacer

Presta atencion especial a:
  - MD.py:276  ->  all(v.cumple for v in verificaciones)
  - MD.py:206  ->  motivos de rechazo
  - cli.py:390 ->  tuple(v for _, v in ... if not v.cumple)
  - M11_reporte.py:744 y :748
  - cli.py:761 (JSON) y cli.py:974 (marca)
  - M1_clasificacion.py:426

En Python None es falsy: cualquier "if not v.cumple" existente trataria un
diferido como incumplimiento sin avisar. Ese bug silencioso es la razon de ser
de este paso.

Solo el inventario. No propongas codigo todavia.
```

> **Qué revisar:** que sean nueve y que para cada uno diga qué pasaría hoy con
> `None`. Si alguno lo trataría como incumplimiento, ese es el que importa.

---

## Paso 7 — Aplicar los nueve, con sus tests

```
Paso 7. Aplica los cambios del inventario anterior.

Decision que quiero que respetes en MD.py:276: un diferido NO cuenta como
incumplimiento ni como cumplimiento, y SI permite aceptar el diametro. Si un
diferido impidiera aceptarlo, el efecto seria identico al AssertionError de
hoy y este encargo no habria servido de nada.

Documenta en el docstring de esa funcion la consecuencia, que es real y no se
maquilla: como V5 y V8 se evaluan dentro del bucle por cada diametro
candidato, al diferirlas un diametro que antes se habria rechazado ahora pasa.
El diametro obtenido a nivel perfil es un LIMITE INFERIOR; el expediente puede
requerir uno mayor al evaluar V5 y V8.

Esa misma advertencia tiene que quedar impresa en la memoria junto al diametro
adoptado de cada punto.

En M11 y en la CLI: marca propia para el diferido, distinta de cumple y de
incumple, con nota_diferida visible.
En el JSON: cumple sale null y se agrega nota_diferida.

Escribe tests nuevos: uno por sitio, comprobando que un Verificacion con
cumple=None no se cuenta como incumplimiento.

Corre la suite completa. Muestrame el diff.
```

> **Qué revisar:** este es el paso de mayor riesgo. Lee cada uno de los nueve
> cambios. Verifica que en `cli.py:390` un diferido no aparezca en la lista de
> incumplimientos.

---

## Paso 8 — El bug de M2

```
Paso 8. Un arreglo de una linea, independiente de todo lo anterior.

M2_material._valor_si_declarado (M2:187-197) decide si un criterio esta vacio
con ca.criterio(clave).valor, que devuelve el dataclass congelado y NO
consulta _OVERRIDES (criterios_adoptados.py:145-147). ca.valor() si lo hace
(:135-136).

Resultado: un criterio declarado con establecer_valor_dinamico -- que es lo
que usa la GUI (gui/app.py:509) -- le sigue pareciendo vacio a M2. El catalogo
sale con el campo en None y M7 cae en el AssertionError de M7:269 en vez de
usar el valor recien declarado.

Efecto practico hoy: con h_relleno_min_concreto_tmc declarado dinamicamente,
concreto y TMC quedan fuera del catalogo y solo sobrevive HDPE, que tiene tope
de 1.50 m.

Arreglalo de forma que la funcion consulte los overrides, conservando su
contrato actual: devolver None sin lanzar CriterioPendienteError y sin
registrar el uso cuando el criterio sigue vacio.

Escribe un test que declare h_relleno_min_concreto_tmc con
establecer_valor_dinamico y compruebe que M2 lo ve.

Corre la suite completa. Muestrame el diff.
```

> **Qué revisar:** que el test nuevo falle sin el arreglo y pase con él. Pídeselo
> si no lo demuestra.

---

## Paso 9 — Exponer la Fase 7.A

```
Paso 9. Abrir una entrada para el tamizado de rasante.

Problema: tamizado_rasante (M7:293) solo se alcanza desde
compatibilidad_geometrica (7.B), que corre dentro de "if informe.dimensionado"
en cli.correr_punto. Pero la Sec. 7.A de la hoja de ruta dice que el tamizado
se corre "antes de definir el perfil longitudinal": es la GENERADORA de la
rasante, no una verificacion de ella. Hoy la unica fase que el proyecto
necesita antes de trazar el perfil es la unica sin puerta de entrada.

Agrega un subcomando o bandera (p.ej. --modo-rasante) que corra la cadena
M0 -> M2 -> M4 -> M7.tamizado_rasante SIN exigir dimensionamiento, y emita por
punto: diametro tamizado, HW, control gobernante, cota por recubrimiento, cota
por resguardo, cota minima de rasante y condicion gobernante.

Dos cosas que tiene que hacer bien:

1. Barrer el catalogo de diametros, no correr solo con el maximo. Las dos
   condiciones de 7.A se mueven en sentidos opuestos -- subir D sube la clave
   pero baja el HW -- asi que la cota minima NO es monotona en D. Reporta la
   tabla por diametro y cual minimiza la cota. El docstring del propio modulo
   ya advierte que el D maximo no es conservador para las dos condiciones a la
   vez.
2. Funcionar con una rasante provisional. M7.espesor_paquete usa
   (cota_rasante - cota_subrasante), que es un espesor de la seccion tipica,
   no una elevacion: la cota minima es invariante frente al valor absoluto de
   la rasante del CSV. Documentalo, porque es lo que permite correr el
   tamizado antes de que exista el perfil.

Familia C devuelve tupla vacia en materiales_candidatos: reportalo como
"fuera del catalogo circular (marco o multicelda, Sec. 2.3)", no como error.

Tests para el subcomando. Muestrame el diff.
```

> **Qué revisar:** que el barrido de diámetros esté, no solo el máximo. Es lo
> que evita levantar el terraplén más de lo necesario en todo el corredor.

---

## Paso 10 — Corrida y reporte

```
Paso 10. Corre el pipeline completo sobre el CSV del proyecto y reportame:

1. Cuantos puntos quedan en dimensionado = True.
2. Para cada punto que NO cierre, que criterio o dato lo bloqueo y en que fase.
3. Que las cuatro verificaciones diferidas aparezcan en el reporte HTML con su
   fundamento, distinguibles a simple vista de las que cumplen y las que no.
4. Que el JSON traiga cumple: null y nota_diferida poblada en esas cuatro.
5. Confirma que ningun criterio de criterios_adoptados.py cambio de valor.

Nota importante: es posible que ningun punto llegue a dimensionado = True
todavia, porque los 11 criterios de decision del proyectista (Etapa C.1 de
docs/auditoria_y_ruta_despliegue_v9.md) siguen vacios y bloquean ANTES que
estas cuatro verificaciones -- umbral_area_quebrada_importante_ha en M1 Fase 2
y talud_terraplen en M7 Fase 7.B son los primeros de la cascada. Si es asi,
reportalo con la lista de que criterio bloqueo cada punto. Eso NO es un fallo
de este encargo: es el siguiente frente de trabajo.

Lo que si tiene que ser cierto: que NINGUNA corrida aborte con AssertionError.
```

---

# Cómo sé que salió bien

- La suite de tests pasa completa.
- **Ninguna corrida aborta con `AssertionError`.** Este es el criterio central.
- Las cuatro verificaciones diferidas aparecen en el reporte HTML con su
  fundamento, distinguibles de las que cumplen y de las que no.
- El JSON trae `cumple: null` y `nota_diferida` poblada en esas cuatro.
- Las cuatro funciones convertidas ya no llaman a `ca.valor()`, y esos cuatro
  criterios no figuran como usados en la memoria.
- Ningún criterio de `criterios_adoptados.py` cambió de valor.
- El subcomando de tamizado emite la cota mínima de rasante por punto sin
  exigir dimensionamiento.

**No es criterio de éxito** que algún punto llegue a `dimensionado = True`. Eso
depende de la Etapa C.1, que es otro frente.

# Después de esto

El siguiente frente es la Etapa C.1: los 11 criterios que se cierran con una
decisión tuya y de tu asesor. Con este encargo hecho, cerrarlos deja de ser una
trampa — hoy declarar `TR_evento_extremo` aborta la corrida, y al retirar las
llamadas a `ca.valor()` de las cuatro funciones eso desaparece.

Conviene actualizar `docs/auditoria_y_ruta_despliegue_v9.md` para anotarlo: su
Etapa C planifica cerrar los 25 criterios, incluidos tres que hoy rompen el
programa si se les da valor.
