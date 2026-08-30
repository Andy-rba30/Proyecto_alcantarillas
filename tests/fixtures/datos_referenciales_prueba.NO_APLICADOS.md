# Datos referenciales NO aplicados a criterios_adoptados.py

> **REVISADO EN S16 --- SIS-F-15 (cluster C09).** Este documento afirmaba
> cinco cosas del codigo que ya eran falsas: los cinco sitios de
> `AssertionError` (referencias `archivo:linea` corridas, y uno de los cinco
> retirado), el remanso que "aborta la corrida" (hoy no), `v_max_hdpe` y
> `v_max_tmc` como vacios (hoy cerrados, con otra fuente y otro numero),
> `Material.v_max_rango` (simbolo retirado) y el baseline de 653 tests.
> Cada afirmacion falsa se corrige EN SU SITIO, con la razon, en vez de
> borrarse: un fixture que describe mal el codigo es una trampa para quien lo
> lea, y borrar la traza impediria entender por que lo era.

Acompana a `datos_referenciales_prueba.md`. De sus 21 entradas se aplicaron 14
con `provisional=True`; estas 7 NO se aplicaron. Ninguna se omitio por criterio
estetico: cada una rompe la corrida o exige inventar un dato.

## Grupo 1 - El consumidor es un stub que aborta la corrida (4)

`TR_evento_extremo`, `clases_producto_por_relleno`, `metodo_estabilidad_global`
y --- en su dia --- `remanso_derecho_via`.

> **CORREGIDO EN S16 (SIS-F-15): hoy son TRES, no cuatro.**
> `remanso_derecho_via` **ya no aborta la corrida**. El stub de `AssertionError`
> que tenia se sustituyo por un `DatoFaltanteError("ancho_derecho_via_m")`
> --- `M5_verificaciones.v5_remanso_derecho_via` ---, que SI es `ErrorProyecto`:
> `cli._etapa` lo captura, lo anota como bloqueo y sigue con el resto del punto,
> igual que con el criterio vacio. Declararlo cambia un bloqueo por otro bloqueo,
> mejor explicado, y no por un crash. Las otras tres siguen como se describe.

Las tres se consumen con este patron:

    ca.valor(CRITERIO_X)      # CriterioPendienteError mientras falte
    raise AssertionError("inalcanzable mientras 'X' este vacio")

La verificacion NO esta implementada: el modulo lee el criterio solo para
detenerse con una excepcion limpia. Con el criterio VACIO sale
`CriterioPendienteError`, que es `ErrorProyecto`, y `cli._etapa` la captura,
la anota como bloqueo y sigue con el resto del punto. Con el criterio CON VALOR
se pasa de largo y estalla el `AssertionError`, que NO es `ErrorProyecto`: nadie
lo captura y aborta la corrida entera, todos los puntos incluidos.

Es el mismo patron de `N_cq_N_gammaq_meyerhof` (M9_cabezal.py:1088), que ya
estaba correctamente excluido. Darles valor no destraba nada: cambia un bloqueo
declarado por un crash.

Sitios, ANCLADOS POR SIMBOLO y no por numero de linea (corregido en S16: las
cinco referencias `archivo:linea` de esta lista estaban corridas, y una de las
cinco ya no existe):

    TR_evento_extremo            M5_verificaciones.py::v8_evento_extremo
    clases_producto_por_relleno  M8_estructural.py::seleccionar_clase_calibre
    metodo_estabilidad_global    M9_cabezal.py::verificar_estabilidad_global

Y los `AssertionError` hermanos que NO cuelgan de este fixture, para que la
lista este completa: `M9_cabezal.py::verificar_talud`,
`M9_cabezal.py::capacidad_portante_zapata_en_talud` (el caso
`N_cq_N_gammaq_meyerhof` que ya estaba excluido) y
`M2_material.py::espesor_pared`.

Para destrabarlas hay que IMPLEMENTAR la verificacion (perfil de remanso, tabla
de clase por altura de relleno, analisis de superficies de falla), no declarar
un valor.

## Grupo 2 - La forma del dato no es la que el codigo consume (3)

### predimensionamiento_cabezal
El fixture da `{'espesor_pantalla', 'espesor_zapata', 'talon', 'puntera'}`.
`M9.geometria_adoptada()` hace `GeometriaCabezal(**dimensiones)` y ese
dataclass (modelos.py:996) exige `H`, `B`, `D_f`, `espesor_corona`,
`espesor_base_muro`, `espesor_zapata`. Son dos parametrizaciones distintas:
faltan 5 campos obligatorios y sobran 3 desconocidos -> `TypeError`, crash.
Es el unico criterio que hoy bloquea la Fase 9 del proyecto.

### v_max_hdpe y v_max_tmc --- ENTRADA CADUCA, reescrita en S16

**Ya no son un vacio, y por lo tanto ya no son "datos no aplicados": estan
CERRADOS en el codigo, con otra fuente y otro numero.** `criterios_adoptados`
los declara hoy con `valor = 4.572` m/s, etiqueta `[C]`, citando el WSDOT
Hydraulics Manual M 23-03.12 (abril 2026), Cap. 8, Tabla 8-4 'Pipe Abrasion
Levels', pp. 8-27/8-28 --- los 15 ft/s de esa tabla en SI. Los 6.0 y 4.5 del
fixture no vienen de ninguna fuente citada y aplicarlos encima PISARIA un
valor verificado.

Lo que este bloque decia, y por que ya no vale (se conserva porque explica un
defecto real que costo dos correcciones):

1. Decia que el codigo consume el techo como RANGO, via
   `Material.v_max_rango`, y que un escalar rompia el desempaquetado. Ese
   campo YA NO EXISTE: el techo escalar viaja en `Material.v_max_adoptado` y
   la fila de la Tabla N 10 en `Material.v_max_tabla10`. Un solo campo
   transportando las dos formas era justamente el defecto SIS-A-06.
2. Decia que convertirlos a tupla exigiria inventar el limite INFERIOR. Falso
   por partida doble: los dos numeros de la fila de la Tabla N 10 son ambos
   MAXIMOS --- no un piso y un techo ---, y el piso de velocidad es V2
   (0.25 m/s), que vale para todos los materiales.

## Datos que NO son criterio: van al CSV o a --datos-externos

### luz_m  <- el bloqueo dominante de la corrida
No lo trae el fixture y es lo que hoy detiene a los 4 puntos en Fase 2. No es
columna de Sec. 1.2 ni criterio: es dato externo por punto. Se declara con
`--luz` o en `--datos-externos`. Sin el no se separa alcantarilla de puente y
ningun punto se dimensiona.

### TW_receptor -> aplicado como criterio, pero conviene revisarlo
Se aplico `TW_receptor = 0.0`. El fixture dice: escenario "salida libre",
TW = cota_fondo_receptor del punto. `TW` NO es una cota: M4_control.py:463
lo define como tirante EN METROS SOBRE EL FONDO DE LA SALIDA, y admite
`TW = 0` como salida libre. Un nivel de agua igual al fondo del receptor es
exactamente un tirante 0. Por eso 0.0 traduce fielmente el escenario.

Ojo: como criterio es UN valor para todo el corredor. Si el escenario deja de
ser "salida libre" y TW pasa a variar por punto, el sitio correcto es la
columna `cota_TW` del CSV (ya existe, hoy vacia) o `TW_m` en
`--datos-externos`, que pisan al criterio (cli.py:_resolver_tw).

### L_hidraulico_m
Bloquea la Fase 10 de B-01. Dato externo, no criterio: `--l-hidraulico`.

### Q_m3s de C-01
La celda viene vacia en el CSV. C-01 queda bloqueada por falta de caudal, que
es lo esperado segun el propio fixture (Sec. 4).

## Efecto sobre la suite

Baseline en limpio: **653 passed, 1 skipped CUANDO SE ESCRIBIO ESTE
DOCUMENTO**, y ese numero lleva tiempo caducado: la suite crecio en cada
sesion de correccion. No se actualiza aqui a proposito ---seria una carrera
perdida contra el commit siguiente---; el conteo vigente se lee corriendo
`python3 -m pytest -q` sobre `origin/main`, que es lo que manda CLAUDE.md, y
distinguiendo `passed` de `collected` (hay un `skipped` permanente, de modo
que `collected = passed + 1`).

Con los 14 valores provisionales, en aquella corrida: 25 failed, 614 passed.
La PROPORCION es lo que importa y sigue valiendo; el numero absoluto, no.

Los 25 fallos son tests-guardia que afirman que ESOS criterios siguen vacios
(p.ej. `test_el_criterio_del_talud_sigue_declarado_sin_valor`). Fallan por
diseno al declarar los valores: son la red que impide que un valor entre sin
declararse. No son regresiones del codigo. Confirman que este fixture es un
experimento de rama, no un candidato a merge.
