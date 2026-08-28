# Datos referenciales NO aplicados a criterios_adoptados.py

Acompana a `datos_referenciales_prueba.md`. De sus 21 entradas se aplicaron 14
con `provisional=True`; estas 7 NO se aplicaron. Ninguna se omitio por criterio
estetico: cada una rompe la corrida o exige inventar un dato.

## Grupo 1 - El consumidor es un stub que aborta la corrida (4)

`TR_evento_extremo`, `clases_producto_por_relleno`, `metodo_estabilidad_global`,
`remanso_derecho_via`.

Las cuatro se consumen con este patron:

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

Sitios: M5_verificaciones.py:309 y :424, M8_estructural.py:189,
M9_cabezal.py:981 y :997.

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

### v_max_hdpe y v_max_tmc
El fixture da un escalar (6.0 y 4.5). El codigo los consume como RANGO: M2
los asigna a `Material.v_max_rango: Optional[Tuple[float, float]]` y V5 hace
`v_min, v_max = material.v_max_rango` (M5_verificaciones.py:202). La tabla
normativa homologa tiene esa forma: `V_MAX['concreto'] = (3.0, 6.0)`.
Un escalar rompe el desempaquetado.

Convertirlos a tupla exigiria inventar el limite INFERIOR, que el fixture no
trae y ninguna fuente citada respalda. CLAUDE.md lo prohibe expresamente
("Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes").
Se necesita el par (v_min, v_max) de PPI/FHWA, no solo el maximo.

> **ESTE PARRAFO YA NO DESCRIBE EL CODIGO (aviso dejado al cerrar C05).** Su
> premisa se cayo dos veces. Primera: los dos numeros de la fila de la Tabla
> N 10 son ambos MAXIMOS, no un piso y un techo, de modo que no hay ningun
> "limite inferior" que inventar -- el piso de velocidad es V2 (0.25 m/s) y
> vale para todos los materiales. Segunda: `Material.v_max_rango` ya no
> existe. El techo escalar de TMC y HDPE viaja en `Material.v_max_adoptado` y
> la fila de la tabla en `Material.v_max_tabla10`, precisamente porque un solo
> campo transportando las dos formas era el defecto SIS-A-06. El archivo
> entero esta declarado como contenido caduco (SIS-F-15, cluster C09) y se
> corrige alli; esta nota solo evita que alguien busque un simbolo retirado.

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

Baseline en limpio: 653 passed, 1 skipped.
Con los 14 valores provisionales: 25 failed, 614 passed.

Los 25 fallos son tests-guardia que afirman que ESOS criterios siguen vacios
(p.ej. `test_el_criterio_del_talud_sigue_declarado_sin_valor`). Fallan por
diseno al declarar los valores: son la red que impide que un valor entre sin
declararse. No son regresiones del codigo. Confirman que este fixture es un
experimento de rama, no un candidato a merge.
