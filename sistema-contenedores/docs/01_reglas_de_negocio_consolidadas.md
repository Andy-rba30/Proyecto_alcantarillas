# Reglas de negocio consolidadas — Sistema de gestión de contenedores

> Documento construido **exclusivamente** a partir de las minutas y transcripciones entregadas.
> Nada de lo marcado como `[REGLA]` es interpretación del equipo técnico: todo tiene cita de origen.
> Lo que el equipo técnico propone va marcado como `[PROPUESTA]` y **no** tiene fuerza de regla
> hasta que el cliente lo confirme.

---

## 0. Fuentes

| ID | Documento | Fecha / hora | Participantes | Naturaleza |
|----|-----------|--------------|---------------|------------|
| **R1** | `Minuta_Reunion_Sistema_Contenedores_20260808.pdf` | 8 ago 2026, 17:31 GMT-04:00 | Ronny Ramírez, Erik Rojas | Minuta **redactada por una persona** a partir de la transcripción |
| **R2** | `reunion_con_desarrollador_del_excel.pdf` | 8 ago 2026, 17:31 GMT-04:00 | Ronny Ramírez, Erik Rojas | Notas **automáticas de Gemini** |
| **R3** | `Segundo_levantamiento_con_los_dueños__Notas_de_Gemini.pdf` | 14 ago 2026, 09:43 GMT-04:00 | Ronny Ramírez, Erik Rojas, **Denisse Hernández** | Notas de Gemini + **transcripción literal** (87 págs.) |

### 0.1 Advertencia sobre las fuentes — leer antes de usar este documento

**R1 y R2 son la misma reunión.** Mismo día, misma hora (17:31 GMT-04:00), mismos dos participantes.
R1 es la minuta curada por una persona; R2 es la transcripción automática de Gemini de esa misma
llamada. **No son dos reuniones distintas.**

Consecuencia metodológica, y es importante:

- Se dispone de **dos reuniones de levantamiento**, no de tres.
- Una discrepancia entre R1 y R2 **no es una contradicción del cliente**: es ruido de transcripción
  o criterio del redactor. Se resuelve leyendo, no preguntando.
- Una discrepancia entre `{R1,R2}` y **R3** **sí** puede ser una contradicción real, porque cambian
  los interlocutores: en R1/R2 hablan los dos desarrolladores *interpretando* un Excel; en R3 habla
  **Denisse Hernández, del lado del negocio**.

**Jerarquía de autoridad adoptada** (y la razón):

```
R3  >  R1  >  R2
```

- **R3 manda** porque es la dueña/administradora describiendo su propia operación, y además es
  posterior.
- **R1 sobre R2** porque R2 es salida cruda de un ASR con errores fonéticos evidentes
  ("Kickbook" = QuickBooks, "Zombies" = Sunbiz, "jaz"/"has"/"Assis" = AS-IS, "cargorti" =
  Cargo Worthy, "dipos" = depots, "releas"/"rilas" = releases, "chóeres" = chóferes).
- Ni R1 ni R2 son fuente de negocio primaria: **ambas son desarrolladores infiriendo reglas desde
  una hoja de cálculo.** Varias "reglas" de R1 resultaron ser inferencias, y R3 las corrigió.

Ninguna de las tres fuentes documenta al **Sr. Michael** hablando directamente. Todo lo atribuido a
él llega de segunda mano vía Ronny o Denisse.

### 0.2 Convenciones

| Marca | Significado |
|-------|-------------|
| `[REGLA]` | Afirmada explícitamente por el cliente. Se implementa. |
| `[REGLA-C]` | Afirmada, pero **condicionada** a confirmar un parámetro (monto, %, plazo). |
| `[PENDIENTE]` | Identificada como necesaria pero **nunca definida**. Bloquea diseño si no se responde. |
| `[CONTRADICCIÓN]` | Dos fuentes dicen cosas incompatibles. |
| `[AMBIGUO]` | Una sola fuente, redacción que admite dos lecturas operativas distintas. |
| `[PROPUESTA]` | Diseño del equipo técnico. **No es regla de negocio.** |

---

## 1. Estructura societaria

Este es el hallazgo de R3 con **mayor impacto sobre la base de datos**, y no aparece en absoluto en
R1 ni R2.

**RN-ORG-01** `[REGLA]` — El negocio son **dos compañías**, no una.
> «es una compañía con madre con dos abajo, transporte y contenedores» — Denisse, R3 (01:12:19)

- **Contenedores** (referida como "Florida"): compra, reacondiciona, vende y renta contenedores.
- **Transporte**: presta los servicios de traslado.

**RN-ORG-02** `[REGLA]` — La compañía de **Contenedores subcontrata todo su transporte** a la
compañía de Transporte.
> «Florida subcontrata toda su transportación a transporte porque eso tienes que mantenerlo separado» — R3 (01:13:00)

**RN-ORG-03** `[REGLA]` — **Transporte NO cobra impuestos a sus clientes.** La transportación no
está gravada.
> «transporte no le cobra tax a sus clientes porque la transportación no tiene taxes. Yo no tengo que darle nada al estado de la Florida» — R3 (01:13:10)

**RN-ORG-04** `[REGLA]` — **Contenedores SÍ recauda impuestos**, por tratarse de venta de bienes.
> «Contenedor, sí es una venta, entonces tiene que colectar taxes» — R3 (01:13:33)

**RN-ORG-05** `[REGLA]` — La separación existe por **motivos fiscales**: los impuestos de fin de año
se declaran **por categoría de actividad**.
> «los impuestos fines y año se hacen por categoría» — R3 (01:14:00)

**RN-ORG-06** `[REGLA]` — **Transporte también puede vender contenedores y hacer rentas.** Cuando lo
hace, se comporta fiscalmente como la compañía de Contenedores (recauda impuestos).
> «transporte, aunque sea una compañía de transporte, puede vender un contenedor y puede hacer una renta como lo es actualmente. En ese momento sí coleccionamos taxes, hacemos todo como si fuera la de contenedor» — R3 (01:13:45)

> ⚠️ **Impacto en el modelo**: el tratamiento fiscal **no puede derivarse de la compañía emisora**.
> Depende de la **naturaleza de la operación** (venta de bien vs. servicio de transporte). Esto obliga
> a que la decisión de gravar viva en la **línea de factura**, no en la cabecera ni en la compañía.

**RN-ORG-07** `[REGLA]` — **Facturación intercompañía semanal**: al cierre de cada semana, Transporte
emite **una factura a Contenedores** por todos los viajes de esa semana.
> «Al final de la semana transporte le manda un invoice a Florida de todos los viajes que se hicieron esa semana» — R3 (01:14:20)

**RN-ORG-08** `[REGLA]` — Cada viaje genera, en la compañía de Contenedores, un **gasto acumulable**
en la categoría "transportación", que debe cuadrar contra la factura semanal de Transporte.
> «en gastos transportación debe irse acumulando para que le dé un reporte al final de semana» / «¿Qué te dio a ti? Ah, está todo bien. Se hace el pago» — R3 (01:16:26–01:17:46)

**RN-ORG-09** `[REGLA]` — Se emiten **facturas separadas por compañía**. Una movida se factura por
Transporte; una venta de contenedor se factura por Contenedores.
> «cuando es una movida, tú le haces un invoice por [transporte] y cuando es la venta de contenedor de aquí se hace un invoice por Flori. Son dos invoices» — R3 (00:43:07)

**RN-ORG-10** `[PENDIENTE]` — ¿La cartera de **clientes es compartida** entre ambas compañías o cada
una lleva la suya? Nunca se preguntó. Determina si `customers` se particiona por compañía.

---

## 2. Catálogo de contenedores

**RN-INV-01** `[REGLA]` — El **número de contenedor es el identificador único**, funciona "como una
cédula".
> R1 §5; confirmado en R3: «el sistema debe ser capaz de gestionar los contenedores por números de serie»

**RN-INV-02** `[REGLA]` — El sistema debe **avisar si el número ya existe** al intentar registrarlo.
> «esto te debe salir algo como que te dice "número contenedor existe" o whatever. Te lo pone en rojo» — R3 (01:23:02)

**RN-INV-03** `[REGLA]` — Tipos: **seco (dry)** y **refrigerado (reefer)**.
> «Lo primero le preguntamos es qué tipo de contenedor quiere, si seco o refrigerado» — R3 (00:34:20)

**RN-INV-04** `[REGLA-C]` — Medidas: **20 y 40 pies** (R3), **45 pies y "40 con chassis"** (R1).
> R3 (00:34:20): «¿qué tamaño busca? 20 pies, 40 pies» — pero al ejemplificar dice «¿de qué size está buscando? 20, 40, 45» (00:35:29)
> R1 §5: «medida (20, 40, 45 pies, 40 con chassis)»
>
> **A confirmar**: "40 con chassis" no es una medida — el chassis es equipo rodante independiente.
> ¿Es una medida más del catálogo, un accesorio facturable aparte, o un ítem de inventario propio?

**RN-INV-05** `[REGLA]` — Hay **tres líneas de producto** por condición comercial:

| Línea | Grado | Descripción textual de Denisse |
|-------|-------|-------------------------------|
| **Premium** | Nuevo | «Premium es todo lo nuevo» |
| **Estándar** | Cargo Worthy | «estándar, toda exportación, cargo worthy, lo mejor usado» |
| **Económico** | AS-IS · W4 | «en económico, que es la línea económica, tiene dos: los AS-IS y el W4» |

> R3 (00:32:55–00:33:30)

**RN-INV-06** `[REGLA]` — La **condición no cambia**; lo que cambia es el **precio**, según temporada.
> «El estado se mantiene, lo que varía es el precio de acuerdo al season... un AS-IS te puede costar 1000 pesos hoy y la semana que viene puede estar en 700» — R3 (00:34:20)

**RN-INV-07** `[REGLA]` — **Comprar en volumen mejora el precio de costo.**
> «cuando compras en volumen afecta precios porque el precio que tú vas a coger del contenedor es un poquito mejor» — R3 (00:33:30)

**RN-INV-08** `[CONTRADICCIÓN — resuelta por lectura, confirmar]` — **"Estado" ≠ "categoría".**

Erik preguntó tres veces por los **estados del ciclo de vida** de un contenedor (disponible, vendido,
en reparación…). Denisse respondió siempre con la **categoría comercial** (nuevo/usado, AS-IS/W4/CW).
La pregunta **nunca fue respondida**:

> Erik: «¿Cuáles son los estados de un contenedor? Por ejemplo, vendido, puede ser también dañado, en reparación»
> Denisse: «Ella dice así: usado y nuevo» — R3 (00:31:37–00:32:55)

⇒ **`[PENDIENTE]` crítico**: el catálogo de **estados de inventario no está levantado.** Se modela
con una propuesta técnica (ver §11) que **debe validarse** antes de cargar datos.

**RN-INV-09** `[REGLA]` — Modelo operativo: compran contenedores usados o en mal estado, los
**reacondicionan** (pintura, techo, luces, piso) y los venden o rentan. El reacondicionamiento se
registra como **gasto y suma al costo del contenedor**.
> R1 §2; confirmado R2 y R3 (00:14:37)

**RN-INV-10** `[REGLA]` — **No prestan servicio de reparación a terceros.** Solo reacondicionan lo propio.
> R2 (00:14:37 / 00:37:20)

**RN-INV-11** `[REGLA]` — Al comprar se registra: número, tipo (nuevo/usado), medida, **precio de
compra**, **proveedor** y **pickup** (costo del traslado hasta la yarda).
> R1 §5

**RN-INV-12** `[REGLA]` — El campo hoy llamado "cliente" en la hoja de compras **es en realidad el
proveedor**; debe renombrarse.
> R1 §5

---

## 3. Releases (compras por lote)

**RN-REL-01** `[REGLA]` — Un **release** es una orden de compra por lote pactada con un proveedor:
agrupa N contenedores del mismo tipo y medida bajo un número de release.
> R1 §5

**RN-REL-02** `[REGLA]` — Un release se registra con: **quién lo vendió (proveedor), número de
release, costo y cantidad**.
> «Yo lo pongo en la parte de los releases. Ponemos ahí quién lo vendió, el release, cuánto costó y la cantidad» — R3 (00:46:44)

**RN-REL-03** `[REGLA]` — Los contenedores de un release se **registran individualmente solo cuando
llegan físicamente a la yarda**. El resto permanece en el depósito del proveedor.
> «A medida que yo lo reciba aquí en la yarda es que le doy entrada en la computadora, entonces ya me va descontando» — R3 (00:46:44); R1 §5

**RN-REL-04** `[REGLA]` — El sistema debe mostrar, por release, **cuántos faltan por recoger**.
> «de release este me faltan cinco por recoger que están en el depósito, porque ya aquí entraron 14» — R3 (00:47:00)

**RN-REL-05** `[REGLA]` — El proveedor otorga un plazo de retiro de **14 días**.
> «tiene 14 días para sacarlos» — R3 (00:46:44)
>
> Nota: R1 dejaba esto como pregunta abierta («¿el proveedor cobra almacenaje?»). **R3 la responde.**

**RN-REL-06** `[REGLA]` — Superado el plazo, el depósito cobra un **fee diario**. El proveedor emite
una factura por esos días y el cargo se registra como **gasto**.
> «Si pasan los 14 días... un fee diario» / «La compañía proveedora te manda un invoice por los fees... Ese invoice pasa para el sistema como un gasto» — R3 (00:46:44–00:49:46)

**RN-REL-07** `[REGLA]` — El **fee diario varía por proveedor**, no es un valor único del sistema.
> «depende del tipo. Varía por el tipo. Uno te puede cobrar 8 al día, otro te puede cobrar 6 y otro te puede cobrar 2» — R3 (00:49:46)

**RN-REL-08** `[REGLA]` — El plazo **se extiende sin cargo** cuando el retraso es imputable al
proveedor. Se deja rastro documental (correo con copia al vendedor).
> «yo pongo a mi vendedor en el CC para que vea que yo traté de recogerlo y el tipo es el que no está listo... me lo tienen que extender porque no es culpa mía» — R3 (00:47:47–00:48:44)

**RN-REL-09** `[REGLA]` — Ya **no es obligatorio** que toda compra pertenezca a un release. El sistema
debe soportar **compras sueltas** a proveedores pequeños **y** compras por release.
> R1 §5

**RN-REL-10** `[REGLA]` — La penalización por almacenaje es de **baja frecuencia**, pero debe existir.
> «casi nunca lo hemos tenido que hacer, pero sí, en gastos» — R3 (00:47:00)

---

## 4. Proceso comercial: cotización y venta

**RN-COM-01** `[REGLA]` — Secuencia exacta de calificación de un prospecto, en este orden:

1. ¿Tipo? **seco o refrigerado**
2. ¿Tamaño? **20 o 40 pies**
3. ¿Condición? **nuevo o usado**
4. ¿Uso? **storage o exportación** ← *determina precio distinto*
5. ¿Delivery o lo recoge? Si delivery → **zip code**
6. Se **calculan millas** y se arma el shipping
7. Se entrega **un precio único consolidado** (*bound price*)

> R3 (00:34:20–00:36:26)

**RN-COM-02** `[REGLA]` — **Storage y exportación tienen precios distintos**, porque la exportación
lleva un **certificado de exportación emitido por un inspector**.
> «Storage tiene precio y exportación es otro precio... porque el de exportación lleva un certificado de exportación por un inspector» — R3 (00:35:29–00:36:00)

**RN-COM-03** `[REGLA]` — Al cliente se le entrega **precio consolidado (contenedor + delivery
juntos)**, nunca desglosado. Es decisión **comercial deliberada**.
> «no se pone precio de contenedor tanto, delivery tanto, no. Lo que se pone es "20ft contenedor con delivery"... si tú le dices "el contenedor cuesta 5 pero el delivery cuesta 15", te va a decir no, no, no» — R3 (00:38:44)

**RN-COM-04** `[REGLA]` — 🔴 **Aunque el precio se presente junto, el sistema debe almacenar
contenedor y delivery por separado**, porque el impuesto se calcula **solo sobre el contenedor**.

> «los taxes que se van a calcular van a ser del valor del contenedor. Es decir, en el background... ella tiene que ser inteligente: coger solamente el precio del contenedor, aplicarle el 7% y sumarle el costo del delivery. El cliente ve solamente el número final»
> «lo que sí tenemos que tener claro es alimentar la fórmula del precio del contenedor y el precio del delivery por separado» — R3 (00:38:44–00:41:11)

> ⚠️ **Esta es la regla más determinante del modelo de facturación.** Impide guardar un único
> importe de venta. Ver `RN-FIN-02`.

**RN-COM-05** `[REGLA]` — En exportación, **98–99 % de las veces NO se hace delivery**: el cliente
contrata su propia naviera/transportista, que recoge el contenedor en la yarda.
> «La exportación, 98%, 99% no hacemos el delivery... esa parte de logística nosotros no tenemos nada que ver» — R3 (00:36:26–00:37:45)

**RN-COM-06** `[REGLA]` — Excepción: si el contenedor va **vacío** a una terminal específica, sí se
hace el delivery y **se cobra una cuota de delivery**.
> «si no le va a poner nada dentro del contenedor... "es vacío, déjalo en esta terminal", eso sí lo podemos hacer» + «ellos cancelan el delivery» — R3 (00:36:26–00:38:44)

**RN-COM-07** `[REGLA]` — La operación de exportación **termina** cuando el cliente paga y se le
entrega el certificado, y el contenedor sale de la yarda.
> «La operación termina con exportación cuando pagan el contenedor y le damos el certificado y cuando viene el tipo aquí y sale el contenedor» — R3 (00:37:45)

**RN-COM-08** `[REGLA]` — El registro de venta captura: tipo de contenedor, número de contenedor,
**comisión de vendedor** (si aplica), **ganancia de la venta**, marca de **exportación / tax-exempt /
no aplica**, y **quién lo transportó** (transportista + chofer + monto de delivery) o si el cliente
lo recogió.
> R3 (01:15:03–01:16:26)

**RN-COM-09** `[REGLA]` — La **comisión de vendedor es un gasto** que debe registrarse.
> «si hay comisión, porque tenemos vendedores y hay veces que sí tengo que registrar la comisión porque es un gasto que voy a tener» — R3 (01:15:03)

**RN-COM-10** `[REGLA]` — Selección de transportista mediante **dropdown en cascada**: transportista →
chofer de ese transportista → monto cobrado.
> «Hay un dropdown, un menú que tú escoges. Te dice transportista, salen todos los transportistas que nosotros utilizamos... te da otra opción que dice "¿qué driver fue el que lo llevó?"» — R3 (01:16:26)

> ⚠️ Nota: implica que existen **transportistas externos además de la compañía propia de Transporte**.
> `[PENDIENTE]` — ¿Cuáles? ¿Se les paga como proveedor?

**RN-COM-11** `[REGLA]` — Los **leads** llegan por grupos de Facebook, referencias y grupos de teléfono.
Hay varios vendedores.
> R1 §3, R2 (00:18:43)

**RN-COM-12** `[PENDIENTE]` — **Cómo se centralizan los leads** y cuántos vendedores participan.
Declarado abierto en R1 (pregunta #2) y **nunca tratado en R3**.

**RN-COM-13** `[REGLA]` — El Sr. Michael **cierra las negociaciones por llamada**; Denisse formaliza
después.
> R1 §3

---

## 5. Rentas

**RN-REN-01** `[REGLA]` — Alquiler **por mes, mínimo un mes**, con pago mensual recurrente.
> R1 §2

**RN-REN-02** `[REGLA]` — El ciclo de facturación se **ancla a la fecha efectiva del delivery**, no al
día 1 del mes calendario.
> «Si el contrato se hace exactamente con la fecha efectiva del día del delivery, yo te hago el delivery el día 2, a partir de ahí empieza todo hasta el 2 del mes que viene. Ya tú sabes que los días 2 te toca a ti» — R3 (01:00:03)

**RN-REN-03** `[REGLA]` — 🔴 Cada factura de renta debe **indicar explícitamente el período cubierto**
(desde–hasta). Es un requisito operativo nacido de disputas reales con clientes.
> «los invoices que se le manden a colectar: el primero fue del 2 de agosto al 2 de septiembre. Ya el próximo tiene que ser del 2 de septiembre al 2 de octubre, y así, para que el cliente siempre sepa este es el período que estás pagando»
> «Porque a veces como se demora, ellos pagan esta semana y la otra semana les coge el otro y dicen "hace 10 días te pagué"» — R3 (00:58:53–01:00:03)

**RN-REN-04** `[REGLA-C]` — **Período de gracia de 5 días** establecido en contrato.
> «el contrato lo dice: si tú te pasas de la renta... tú tienes después 5 días de gracia» — R3 (00:56:44)

**RN-REN-05** `[REGLA-C]` — Vencida la gracia sin comunicación del cliente, se aplica un **fee fijo de
$100**, **independiente de los días de atraso**.
> Ronny: «el día 6 puede llamar, pero si llama el día 10 igual 100. No importa los días que pase, son 100.»
> Denisse: «Sí.» — R3 (00:56:44–00:57:00)

**RN-REN-06** `[REGLA]` — El fee **está en contrato pero en la práctica no siempre se aplica**. El
sistema debe calcularlo y notificarlo, pero **permitir que el administrador lo condone manualmente**.
> «a veces en la práctica no lo hemos enforzado, pero en el contrato sí está»
> «lo que puede ser muy flexible es que me des la opción de que a lo mejor no se lo quiero cobrar» — R3 (00:56:44–00:58:00)

**RN-REN-07** `[REGLA]` — **Semáforo de estado**, con esta semántica exacta:

| Color | Significado | Momento de activación |
|-------|-------------|----------------------|
| Normal / negro | Al día | Sin deuda |
| 🟡 **Amarillo** | Pendiente por cobrar — "tengo que llamar" | **Inmediatamente** al guardar una renta sin pago registrado |
| 🔴 **Rojo** | Vencido | **Al terminar el período de gracia** |

> Erik: «¿en amarillo ustedes quieren que salga cuando ya han pasado esos 5 días o cuando comienza?»
> Denisse: «No, no. Cuando comienza.» — R3 (01:01:14)
> «Cuando yo le doy guardar, como he puesto que todavía no me ha pagado, ya me sale amarillo automáticamente» — R3 (01:01:14)
> «Rojo es cuando debe [vencido]... El amarillo es más para decirme que tengo que llamar» — R3 (01:02:13)

**RN-REN-08** `[REGLA]` — Debe soportar **pagos adelantados** (p. ej. tres meses de una vez) y
recalcular la fecha del próximo vencimiento.
> R1 §4

**RN-REN-09** `[REGLA]` — Mecanismo de un clic: **"este cliente pagó el mes"** que registre fecha y
monto automáticamente, conociendo el monto pactado.
> R1 §4

**RN-REN-10** `[REGLA]` — La hoja actual ya calcula y el sistema debe conservar: meses en renta, pagos
realizados, meses adeudados, **hasta qué mes está pagado**, total pagado, estatus y taxes generados
por el contrato.
> R1 §4

**RN-REN-11** `[REGLA-C]` — Montos de renta observados: **150** (mayoría), **192** (uno), **300** (dos).
> R1 §4

**RN-REN-12** `[REGLA]` — El monto de renta **varía según el tamaño del contenedor**.
> R2 (00:25:07)
>
> ⚠️ Ver `[CONTRADICCIÓN C-4]`.

---

## 6. Cobranza automática y notificaciones

**RN-NOT-01** `[REGLA]` — Vencido el plazo, el sistema debe **enviar notificaciones automáticas**, sin
gestión manual.
> «El sistema automáticamente... yo no voy a estar pendiente de eso» — R3 (01:03:04)

**RN-NOT-02** `[REGLA]` — Las notificaciones van a **todos los medios de contacto registrados**: todos
los teléfonos (por SMS) **y** el correo.
> «A veces en la renta me ponen dos teléfonos. ¿Se lo mandará el sistema a los dos teléfonos y al correo?» → «el sistema va a utilizar los modos de comunicación que tengamos archivados para ese cliente. Si hay un teléfono y hay un email: una notificación por email y un text message» — R3 (01:03:04–01:06:07)

**RN-NOT-03** `[REGLA]` — El texto de la notificación debe incluir el **período de renta adeudado**
(coherente con `RN-REN-03`).
> «siempre vamos a poner "de esta fecha a esta fecha"» — R3 (01:04:00)

**RN-NOT-04** `[REGLA]` — El contenido del aviso debe advertir la **penalidad en la que va a incurrir**
y pedir el pago antes de una fecha.
> «"ya estás atrasado, no se ha recibido ninguna comunicación, vas a incurrir en este fee de penalti. Por favor mándalo antes de este día para no pasar eso"» — R3 (00:57:57)

**RN-NOT-05** `[REGLA]` — 🔴 La **cadencia y el día de inicio deben ser configurables desde el
sistema**, sin intervención del desarrollador.
> «eso se puede configurar en la parte de configuración del sistema... para que ustedes no vengan y nos digan "mira, ya no quiero que aparezca a partir del primer día sino del quinto"» — R3 (01:07:12)

**RN-NOT-06** `[AMBIGUO]` — **La cadencia concreta nunca se cerró.** En la misma conversación
aparecen tres propuestas distintas y ninguna se declaró ganadora:

| Propuesta | Quién | Cita |
|-----------|-------|------|
| Del día 5 al 10, **una notificación diaria** | Denisse | «a partir del 5 hasta el 10 te va a mandar notificaciones todos los días» (01:03:04) |
| **Cada dos días** → días 6, 8, 10 = **3 avisos** | Denisse | «cada dos días mande una notificación. El 6 empieza la primera, la próxima sería el 8 y la última sería el 10. Son tres notificaciones» (01:05:01) |
| **Correo desde el día 1**, SMS a partir del día 5 | Ronny | «desde el día uno yo mandaría la información por correo... y ya después, como dice Denisse, en el día 5 empezar cada dos días mandarlo directamente al teléfono» (01:04:00) |

Denisse cierra devolviendo la pregunta al equipo: *«en la experiencia de ustedes, ¿cómo lo han visto:
una vez al día o cada dos?»* — **sin respuesta**.

⇒ Resuelto por `RN-NOT-05`: **se implementa configurable** y se siembra con la opción intermedia
(inicio día 6, cada 2 días, fin día 10). **Confirmar el valor inicial.**

> **Nota sobre las notas de Gemini:** el resumen curado de R3 afirma como decidido *«alertas entre el
> día 5 y el 10, con una frecuencia de un aviso cada dos días»*. La transcripción muestra que eso fue
> **una de tres opciones en debate**, no un acuerdo. Ejemplo de por qué la transcripción manda sobre
> el resumen automático.

---

## 7. Impuestos, cargos y medios de pago

**RN-FIN-01** `[REGLA-C]` — Tasa de impuesto: **7 %**, en Florida.
> R1 §4, R2 (00:32:24), R3 (00:41:11)
>
> R1 la califica de "aproximadamente 7 %" y pide verificar. **Sigue sin verificarse formalmente.**

**RN-FIN-02** `[REGLA]` — 🔴 **Base imponible = solo el valor del contenedor.** El delivery se suma
**después** de aplicar el impuesto.
> R3 (00:41:11) — ver cita completa en `RN-COM-04`

```
total = (precio_contenedor × (1 + tasa_tax)) + precio_delivery
```

**RN-FIN-03** `[REGLA]` — **La transportación nunca lleva impuesto**, en ningún caso.
> «Nada de transportación lleva taxes» — R3 (00:42:17)

**RN-FIN-04** `[REGLA]` — Existen clientes con **certificado de exención de impuestos**. A ellos no se
les cobra tax.
> «hay clientes que en Florida, muchos negocios, tienen un certificado de excepción de taxes» — R3 (00:52:57)

**RN-FIN-05** `[REGLA]` — El certificado de exención **se solicita al inicio**, al coordinar formas de
pago, y **se archiva junto a la cuenta del cliente y a la factura**.
> R3 (00:52:57)

**RN-FIN-06** `[REGLA]` — El certificado de exención **se renueva anualmente**: mismo número,
documento nuevo cada año. El sistema debe permitir **subir el documento actualizado y reemplazarlo**.
> «todos los años se renueva. Es el mismo número, pero él tiene que mandar el papel actualizado... todos los años nosotros tenemos que pedírselo al cliente y subir la foto» — R3 (00:54:11–00:49:00)

**RN-FIN-07** `[REGLA-C]` — **Credit card fee de 3.5 %**, constante, cuando el pago es con tarjeta.
> «si paga por tarjeta sí tiene que aplicarse el credit card fee, el fee de la tarjeta que te cobra la máquina por pasar la tarjeta. Es un 3.5 constante» — R3 (00:42:17–00:43:00)

**RN-FIN-08** `[REGLA-C]` — La plataforma de pago actual es **Square**.
> «Square» — R3 (00:43:00)
>
> `[PENDIENTE]` Denisse quedó de **enviar el nombre/credenciales de la plataforma** al grupo. No consta
> que se haya hecho. Confirmar antes de diseñar la integración de cobros.

**RN-FIN-09** `[REGLA]` — La factura debe **desglosar explícitamente**: impuestos, **depósito**,
**descuento** y **credit card fee**, además de subtotales. (Aunque el precio de venta vaya consolidado
— `RN-COM-03`.)
> «aparte de tax puede haber depósito, puede haber descuento y puede haber el credit card fee, y ya en los subtotales» — R3 (00:51:47)

**RN-FIN-10** `[REGLA]` — El **depósito se resta** del total en la factura, mostrando la deducción.
> «si tú me diste $200 de depósito, cuando te va el invoice yo tengo que poner en una parte que diga "depósito menos 200" y que quite esos 200 del resto» — R3 (00:51:47)

**RN-FIN-11** `[REGLA]` — Las combinaciones de cargos son **variables**: a veces están tax + card fee +
depósito juntos, a veces solo el tax, a veces solo el total sin nada.
> «a veces pueden estar todos juntos... y a veces está solamente el total porque no hay ni taxes ni nada» — R3 (00:52:57)

**RN-FIN-12** `[REGLA]` — La factura debe listar **todas las formas de pago disponibles** al pie, para
que el cliente elija.
> «abajo los invoices tienes todas las formas de pago para que cuando le llegue eso al cliente, si quiere pagar por [Zelle], ahí está» — R3 (00:43:07)

**RN-FIN-13** `[REGLA]` — Medios de pago mencionados: **efectivo, tarjeta de crédito, cheque,
transferencia, Zelle** (R1) · **Square, PayPal** (R3).

---

## 8. Control antifraude en pagos con tarjeta

Bloque completo de R3, **inexistente en R1/R2**. Es política de negocio dura, nacida de pérdidas reales.

**RN-FRD-01** `[REGLA]` — Ningún pago con tarjeta se procesa hasta que el cliente devuelve firmado un
**Credit Card Authorization Form**, que incluye datos de la tarjeta, dirección de facturación y firma
autorizando el cargo **por un monto específico**.
> «eso no sucede hasta que nosotros le enviemos un credit authorization form... la firma de que esa compañía o persona me está autorizando a correr esa tarjeta por el monto que nosotros le enviamos» — R3 (00:43:07–00:44:22)

**RN-FRD-02** `[REGLA]` — El formulario firmado **se archiva junto con la factura** antes de procesar
el cobro.
> «Yo la printeo y entonces lo tenemos junto con el invoice, todo junto, de que ya podemos pasar la tarjeta» — R3 (00:44:22)

**RN-FRD-03** `[REGLA]` — Las tarjetas **solo se procesan a compañías verificadas** en **Sunbiz** (el
registro mercantil del estado de Florida). Si la compañía no aparece activa, es señal de fraude.
> «le hacemos la verificación en Sunbiz, que es el lugar donde aquí en Florida todas las compañías tienen que estar registradas y activas. Si no está ahí, eso es un plan de robo para nosotros» — R3 (00:44:22)
> *(En la transcripción aparece como "Zombies" — error del ASR.)*

**RN-FRD-04** `[REGLA]` — Se acepta tarjeta a **personas físicas solo presencialmente en la yarda**,
con identificación. **Nunca por teléfono o a distancia**, salvo compañía ya verificada.
> «Solamente vamos a aceptar tarjeta de crédito a personas físicas en la yarda. Si es físico aquí que te da identificación, aquí sí lo hacemos. Pero si es por teléfono... a no ser que sea una compañía que verificamos» — R3 (00:45:27)

**RN-FRD-05** `[REGLA]` — Motivo: **chargebacks**. El titular real reclama al banco, el banco abre
investigación y la empresa pierde los fondos **más penalidades**.
> «el verdadero dueño después se da cuenta que ese charge se hizo, lo reclama al banco... y todos esos fondos más las penalidades se aplican. Ya hemos tenido experiencia» — R3 (00:45:27)

---

## 9. Gestión documental

**RN-DOC-01** `[REGLA]` — El sistema debe **archivar documentos digitalmente**, vinculados al cliente
y a la venta, para eliminar el papel y la búsqueda en carpetas.
> «que el sistema debe archivar documentos vinculados a cada cliente y venta, facilitando la recuperación... y evitando el uso excesivo de papel» — R3, resumen (00:51:47)

**RN-DOC-02** `[REGLA]` — Documentos a archivar, nombrados explícitamente:
certificados de **exportación** · certificados de **exención de impuestos** · **credit card
authorization forms** · **facturas** · **contratos** de renta.
> R3 (00:52:57, 00:44:22, 00:55:19)

**RN-DOC-03** `[REGLA]` — 🔴 **Todo debe quedar enlazado a la venta**: al buscar una venta deben verse
factura, número de factura, certificado de exportación (si aplica), certificado de tax-exempt (si
aplica), qué se vendió, tipo, medida y monto — **en un solo lugar**.
> «que todo esté linkado, para cuando yo busque una venta de esta persona ya yo tengo todo en un solo lado. Aquí el invoice, el número de invoice. Si era exportación, ahí está el certificado. Si era tax-exempt, está ahí también. ¿Y cuánto se le vendió? ¿Y qué fue lo que se le vendió? Un reefer, ¿qué size? 40...» — R3 (00:55:19–00:56:00)

**RN-DOC-04** `[REGLA]` — El certificado de exportación **se genera como PDF desde el sistema** y se
envía digital al cliente.
> «lo que queremos es, cuando nosotros [hagamos] el certificado de exportación, crear el PDF... muchos se los enviamos digitales a los customers» — R3 (00:55:19)

**RN-DOC-05** `[REGLA]` — Al buscar un cliente deben aparecer **todas las facturas históricas** que se
le han emitido.
> «yo tengo que tener en el sistema todos los invoices por cliente... puede ser que después de tres meses me diga "oye, mándame el invoice del mes pasado que no lo encuentro"» — R3 (00:52:57)

---

## 10. Clientes / CRM

**RN-CLI-01** `[REGLA]` — Hoy **no existe** módulo de clientes. Un cliente frecuente se vuelve a
registrar por completo en **cada** operación.
> R1 §3 y §8

**RN-CLI-02** `[REGLA]` — Registrar **una sola vez** (nombre, teléfono, dirección, correo, empresa) y
reutilizar en cotizaciones, ventas, rentas y viajes.
> R1 §8, R2 (00:23:22)

**RN-CLI-03** `[REGLA]` — Debe existir **historial por cliente**: qué contenedores compró y cuáles rentó.
> R1 §8

**RN-CLI-04** `[REGLA]` — El cliente queda registrado **aunque solo haya solicitado un presupuesto**.
> R1 §8

**RN-CLI-05** `[REGLA]` — **Filtros múltiples**: por nombre, **por teléfono** y por organización. Un
contacto personal puede facturar a nombre de una organización distinta.
> R1 §8

**RN-CLI-06** `[REGLA]` — Un cliente puede tener **varios correos y varios teléfonos**, incluyendo
contactos de **contaduría** distintos del contacto principal, y a veces **dos personas en contaduría**.
> «puedo agregar más de un email porque a veces me dice "mándamelo a mí pero también a contaduría", y hay veces en contaduría son dos personas» — R3 (01:09:40)

**RN-CLI-07** `[REGLA]` — La ficha debe guardar **dirección de facturación y dirección de shipping**
por separado.
> «ahí mismo tengo la información de dirección, shipping, teléfono, emails» — R3 (01:09:40)

---

## 11. Viajes / delivery y chóferes

**RN-VIA-01** `[REGLA]` — La hoja "Viajes" **existe pero no se usa**; el cliente quiere empezar a usarla.
> R1 §9

**RN-VIA-02** `[REGLA]` — El viaje es un **servicio con ingreso propio y gastos asociados**: viáticos,
gasolina, cauchos y reparaciones en ruta.
> R1 §9

**RN-VIA-03** `[REGLA]` — Se distinguen **dos operaciones con costeo distinto**:

| Operación | Costeo |
|-----------|--------|
| **Delivery** (salida al cliente) | **Variable, por millas** |
| **Pickup / recogida** (traer del depósito) | **Fijo**, asociado al depósito |

> «el delivery sí trabaja con millas y varía. El del depot no: siempre el mismo fee, porque los depots están aquí mismo. **Hay tres depots nada más.** Entonces ese nunca va a cambiar» — R3 (01:17:46)

**RN-VIA-04** `[REGLA]` — El **delivery se registra en la venta**; el **pickup se registra en la compra**
(entrada de inventario).
> «la recogida es cuando entra... el pickup [está en la compra] y el delivery está en la venta» / «en la compra, que es el incoming» — R3 (01:19:16)

**RN-VIA-05** `[REGLA]` — Reporte semanal al transportista: número de recogidas, número de deliveries y
totales, que debe **cuadrar** con la factura que él emite.
> «se hicieron siete recogidas, 11 deliveries, total tanto... y ya él tiene el total, que tiene que machear» — R3 (01:17:46)

**RN-VIA-06** `[REGLA]` — **No existe ficha de chóferes ni de trabajadores**: hoy solo aparece el
nombre suelto dentro del viaje.
> R1 §9

**RN-VIA-07** `[REGLA]` — Los chóferes tendrán un **panel propio** para registrar sus operaciones y
gastos de forma independiente.
> «se desarrollará un panel específico para los chóferes, permitiéndoles registrar operaciones y gastos de manera independiente» — R3, resumen (00:30:28)

**RN-VIA-08** `[AMBIGUO]` — 🔴 **El esquema de pago al chofer no está definido.** Las dos fuentes
sugieren cosas distintas y ninguna lo declara como regla:

| Fuente | Dato | Lectura |
|--------|------|---------|
| R1 §9 | «de 280 cobrados, 85 para el chofer» | Monto **fijo negociado** (30.4 %) |
| R3 (01:15:03) | «me puse el 30 % de los 400, por ejemplo» | **Porcentaje** del 30 % |

**A confirmar**: ¿porcentaje fijo del 30 %, porcentaje por chofer, o monto negociado por viaje? Cambia
si `driver_pay` es campo calculado o capturado.

**RN-VIA-09** `[REGLA]` — El pago al chofer **se descuenta del ingreso del viaje** y se paga los
**lunes**; el sistema debe manejar el estatus **"pendiente por pagar"**.
> R1 §9

**RN-VIA-10** `[PENDIENTE]` — 🔴 **¿Hacen delivery de contenedores de terceros o solo de los propios?**
Pregunta abierta #1 de R1, repetida en R2 como próximo paso del grupo. **Nunca se le preguntó a
Denisse en R3.** Sigue sin respuesta.

Hay un indicio a favor en R3, pero es de Ronny planteando un caso hipotético, **no de Denisse
confirmando la política**:
> Ronny: «yo le compré un contenedor a ustedes hace años y lo tengo en un sitio, pero quiero moverlo... ¿ese servicio no lleva fee, no lleva taxes?»
> Denisse: «Nada de transportación lleva taxes» — R3 (00:41:11–00:42:17)

Denisse responde sobre **impuestos**, no sobre si aceptan el servicio. **No se puede tomar como
respuesta.**

**RN-VIA-11** `[REGLA]` — Datos de vehículos a registrar: **VIN, número de placa, tipo de vehículo**, y
una sección de **mantenimiento**. Denisse ya los tiene en un Excel.
> «el VIN number, el plate number, ¿qué tipo de vehículos son?... hay una parte de transporte que es vehículos [y] mantenimiento» — R3 (01:30:25)

---

## 12. Gastos

**RN-GAS-01** `[REGLA]` — Todo gasto se registra con **tipo y descripción**. Ejemplos citados: nómina,
gasolina, repuestos, almuerzos de negocio, compras de insumos.
> R1 §5

**RN-GAS-02** `[REGLA]` — 🔴 Las **categorías de gasto deben ser una lista extensible desde el sistema
(dropdown), administrable por el cliente**, no un catálogo cerrado en código.
> «podemos crear un dropdown, una lista que empieza a categorizarlos... A medida que vamos teniendo, yo los puedo ir alimentando: "mira, tenemos que agregar una categoría aquí porque esto es un nuevo proveedor"» — R3 (00:50:36)

**RN-GAS-03** `[REGLA]` — Categorías nombradas por el cliente: **yarda**, **vehículos**,
**combustible**, **container fee / almacenaje**, **transportación**, **materiales**, **salarios**.
> R3 (00:50:36, 01:17:46)

**RN-GAS-04** `[REGLA]` — Debe existir obligatoriamente la categoría **"transportación"** en el reporte
de gastos de la compañía de Contenedores (por `RN-ORG-08`).
> «en el reporte de gastos de la compañía hay una categoría que tiene que decir transportación, para que tú veas: estás gastando materiales, salarios, transportación» — R3 (01:17:46)

**RN-GAS-05** `[REGLA]` — Denisse entregará el listado de categorías **actualmente en uso**; Ronny le
enviará una plantilla imprimible para llenarla.
> R3 (00:51:47) — **tarea pendiente de entrega**

**RN-GAS-06** `[REGLA]` — Ampliaciones propuestas por Erik y **aceptadas** en R3: inventario de
**materiales de reparación**, inventario de **camiones**, **nómina completa** (chóferes, secretaria,
administrador, limpieza) como gasto que reduce la ganancia real.
> R1 §9; R3 confirma nómina y vehículos (01:30:25, resumen pág. 7)

---

## 13. Ganancia y reportes

**RN-REP-01** `[REGLA]` — Fórmula de ganancia neta por libro:
```
ganancia = ventas + rentas − compras − gastos − taxes
```
> R1 §7

**RN-REP-02** `[REGLA]` — Para calcular la **ganancia real de una venta** hace falta vincular el
**contenedor** a la factura: el sistema de facturación conoce el monto vendido pero **no** en cuánto
se compró el contenedor.
> R1 §6

**RN-REP-03** `[REGLA]` — 🔴 Reporte de impuestos **filtrable por rango de fechas**, mostrando taxes
recaudados, ventas y gastos del período. Petición **directa y explícita** de Denisse.
> «necesito que se vean los taxes... yo pongo la fecha de ese mes y me salen los taxes, cuántos taxes se han colectado» / «yo pongo la fecha y me sale cuánto se hizo ese mes, cuánto se gastó y cuánto es de taxes» — R3 (00:26:47)

**RN-REP-04** `[REGLA]` — Métricas validadas del **dashboard** (Denisse las revisó y aceptó): pagos
pendientes de clientes · ventas del mes · cuentas por cobrar · rentas activas · contenedores
disponibles · gráfica de ventas de los últimos 6 meses · resumen de operaciones · clientes registrados.
> R3 (00:25:10)

**RN-REP-05** `[REGLA]` — **El dashboard es la vista del día a día; los reportes son la consulta
histórica por rango.** Distinción aceptada por el cliente.
> Ronny: «el dashboard es como algo día a día, lo que yo veo día a día que me interesa más rápido» → Denisse: «Okay, entiendo» — R3 (00:28:00)

**RN-REP-06** `[REGLA]` — **Dashboard de morosidad**: listado de morosos siempre visible, filtrable
por día y por mes.
> R1 §4

**RN-REP-07** — Cifras del mes revisado en R1 §7 (**no usar como dato**, el propio R1 las invalida):
compras 256.000 · ventas 269.000 · ganancia 97.020 · rentas 2.292.
> R1 advierte: archivo de hace ~1 mes, con un error de resta ya corregido. Además, **97.020 no es
> consistente** con 269.000 − 256.000 = 13.000. Son cifras de ejemplo, no de referencia.

---

## 14. Usuarios, roles y accesos

**RN-USR-01** `[REGLA]` — Usuarios iniciales: **Denisse y Michael** (uso principal), más una tercera
persona.
> «los tres debemos usar el sistema. Los que más vamos a utilizarlo somos yo y Michael» — R3 (00:30:28)

**RN-USR-02** `[REGLA]` — Habrá a futuro un usuario **con acceso a contenedores y releases pero
restringido en finanzas**.
> «sí vas a tener un usuario con una restricción de ciertas cosas de finanzas, a las que no tiene que tener acceso, pero sí a la parte de entrar los contenedores, entrar los releases» — R3 (00:30:28)

**RN-USR-03** `[REGLA]` — Roles nombrados: **administrador** (Denisse, Michael), **vendedor**, **chófer**.
> R3 (00:51:47)

**RN-USR-04** `[REGLA]` — Las **secretarias registran** las operaciones; el **dueño consulta** reportes
y cifras sin capturar información.
> R1 §9

**RN-USR-05** `[REGLA]` — 🔴 **Todo el sistema debe ser administrable**: menús, nombres, roles de
empleados, altas y bajas de chóferes.
> Denisse: «¿va a quedar el programa como que nosotros podemos quitar nombre y poner nombre o agregar chóferes, empleados?» → Erik: «**Todo el sistema va a ser administrable**» — R3 (01:08:22)

---

## 15. Requisitos transversales

**RN-SIS-01** `[REGLA]` — El sistema debe estar en **inglés y español**, con selector de idioma.
> R1 §5; R3 (01:20:13) — Denisse pregunta y Erik confirma

**RN-SIS-02** `[REGLA]` — Criterio de diseño del Sr. Michael: **operar con clics, no escribiendo**.
Todo lo que pueda resolverse con un clic, debe resolverse con un clic (ej.: selector de calendario en
lugar de teclear la fecha).
> R1 §1, R2 (00:05:35)

**RN-SIS-03** `[REGLA]` — 🔴 **Terminología genérica y estándar**, no personalizada al cliente. Razón
declarada: que el software siga siendo usable si venden o hacen crecer la compañía.
> «no quiero hacerlo tan custom a nosotros porque entonces solamente lo entendemos nosotros... si hacemos el software muy custom, nos limitamos en el momento en que otra persona lo vaya a utilizar» / «para cualquiera que en un futuro, si la vendemos... que sea un software [donde] yo sé que es inventario, yo sé que es estimado, yo sé que es invoice» — R3 (01:24:15–01:32:32)

**RN-SIS-04** `[REGLA]` — Se requiere **importación desde Excel** para la carga inicial.
> R1 §5

**RN-SIS-05** `[REGLA]` — Módulos acordados y **validados por Denisse** en R3 (00:28:55):

| Módulo | Contenido |
|--------|-----------|
| Comercial | clientes, presupuestos, ventas |
| Operaciones | contenedores, rentas, deliveries, chóferes |
| Compras | proveedores, compras, releases |
| Inventario | insumos, camiones |
| Finanzas | facturación, pagos, gastos |
| Administración | usuarios, roles y permisos |
| Reportes | consolidados por rango de fechas |
| Configuración | parametrización |

---

## 16. Calidad de datos y migración

**RN-MIG-01** `[REGLA]` — La hoja de ventas arrojaba **416 contenedores** en stock. **Denisse afirma no
tenerlos físicamente.**
> R1 §5

**RN-MIG-02** `[REGLA]` — Ya se depuró la base y se ajustaron fórmulas para contar solo los
contenedores **sin registro de venta ni de renta**.
> R1 §5, R2 (00:48:09)

**RN-MIG-03** `[REGLA]` — Se solicitó al cliente **conteo físico** de los contenedores en la yarda.
> R1 §5, R2 (00:52:47)

**RN-MIG-04** `[PENDIENTE]` — 🔴 **No consta que el conteo físico se haya realizado.** No se menciona
en R3, seis días después. **Es prerrequisito de la carga inicial.**

**RN-MIG-05** — Ejemplo de depuración: en julio se compraron 108 contenedores y quedaron 63 sin venta
ni renta. — R1 §5

**RN-MIG-06** `[REGLA]` — El Excel actual **refleja pedidos puntuales del dueño acumulados en el
tiempo, no una lógica administrativa estándar**. Al normalizar aparecerán decisiones que él podría
extrañar; conviene mapear explícitamente qué vistas y comportamientos se conservan sí o sí.
> R1 §12

---

## 17. Contradicciones detectadas

### 🔴 C-1 — QuickBooks: ¿se integra o se reemplaza?

**La contradicción de mayor impacto del proyecto.** Invalida el acuerdo principal de la primera reunión.

| Fuente | Postura |
|--------|---------|
| **R1 §6** | Evalúa dos opciones y concluye: **Opción B — integración por API. «Opción preferida por ambos.»** Se descarta facturación propia por «asumir la parte legal y fiscal de EE. UU.» |
| **R2** | Aún más rotundo: **«Se decidió utilizar la API de QuickBooks»**, listado como decisión estratégica del resumen |
| **R3 (01:10:59)** | Denisse: «me dijiste que **si hacemos que esta [plataforma] mande los invoices y haga todas las cosas y registre el pago y todo lo demás, ya no tengo que usar QuickBooks, puedo transicionar a esta**» |

Ronny le repregunta explícitamente — *«¿y vas a seguir manteniendo el QuickBooks?»* — y ella responde
que **no**, si el sistema cubre invoices y registro de pagos.

**Agravante que nadie detectó en R1/R2:**

> Erik: «Entonces básicamente todas las finanzas las llevan allí.»
> Denisse: «**de una sola [compañía], que es la de transporte. La otra se está llevando en el Excel que creó Ronny**» — R3 (01:10:59–01:12:19)

⇒ **QuickBooks solo cubre la compañía de Transporte.** Toda la operación de contenedores —ventas,
rentas, taxes, releases— **nunca estuvo en QuickBooks**: está en el Excel que el sistema viene a
reemplazar.

Esto derriba la premisa de R1. La Opción B se eligió creyendo que QuickBooks ya resolvía la
facturación del negocio de contenedores. **No la resuelve.** Análisis y recomendación: `04_quickbooks_vs_facturacion_propia.md`.

**Estado: ABIERTA. Bloquea el alcance de Finanzas.**

---

### 🟠 C-2 — Base del impuesto del 7 %: ¿medio de pago o naturaleza del bien?

| Fuente | Regla enunciada |
|--------|-----------------|
| **R1 §4** | «Aproximadamente **7 % sobre todo pago que no sea en efectivo** (tarjeta, cheque, transferencia, Zelle)» |
| **R2 (00:32:24)** | «cualquier pago recibido por medios distintos al efectivo (tarjeta, débito, cheque) **genera un impuesto del 7 %**» |
| **R3 (00:38:44–00:42:17)** | El 7 % se aplica **al valor del contenedor**; el delivery **nunca** lleva tax; los clientes con certificado de exención **no pagan tax con ningún medio de pago** |

Son reglas **estructuralmente incompatibles**: R1/R2 hacen depender el impuesto del **medio de pago**;
R3 lo hace depender de la **naturaleza de la operación** y del **estatus fiscal del cliente**.

**Lectura del equipo técnico** (`[PROPUESTA]`, a validar — no la conviertas en regla sin confirmar):
en R1/R2 parecen haberse fusionado **dos cargos distintos** que R3 separa con claridad:

1. **Sales tax ~7 %** → sobre el valor del contenedor, exento con certificado, nunca sobre transporte.
2. **Credit card fee 3.5 %** → sí depende del medio de pago (`RN-FIN-07`).

Esto explicaría el origen del error: en el Excel ambos cargos caen sobre el total y se confunden. Pero
**es una hipótesis técnica, no una regla**: hay que confirmarla.

**Estado: ABIERTA.** Preguntar a Denisse: *"¿el 7 % depende de cómo pague el cliente, o de qué se le
vende?"* Se implementa según R3, marcado como sujeto a confirmación.

---

### 🟠 C-3 — Morosidad: ¿deuda al día siguiente o 5 días de gracia?

| Fuente | Regla |
|--------|-------|
| **R1 §4** | «El pago vence el día exacto... **Al día siguiente ya se considera deuda**» + «si le toca pagar el 23, el 24 quiero saber que me debe» (atribuido al dueño) |
| **R2 (00:29:00)** | «generar alertas automáticas para los clientes que superen el plazo de pago (**dando un margen de 5 días**)» |
| **R3 (00:56:44)** | «el contrato lo dice: **tú tienes 5 días de gracia**», con fee de $100 al vencerlos |

R1 y R2 son la misma reunión y ya se contradicen entre sí → indica que en esa reunión el punto no
estaba claro.

**Resolución propuesta** (`[PROPUESTA]`, encaja con las tres fuentes sin forzar ninguna): R1 y R3
hablan de **cosas distintas**, no opuestas:

- R1 describe una necesidad de **visibilidad**: el dueño quiere *ver* el impago de inmediato.
- R3 describe la **consecuencia contractual**: la penalidad no corre hasta el día 6.

El **semáforo de `RN-REN-07` satisface ambas**: 🟡 amarillo el día siguiente al vencimiento
(visibilidad para el dueño) · 🔴 rojo al agotar la gracia (deuda formal + fee). El propio R3 lo
confirma: *«¿en amarillo cuando pasan los 5 días o cuando comienza?» → «Cuando comienza».*

**Estado: RESUELTA por diseño.** Confirmar con Michael que ver amarillo el día 24 le satisface.

---

### 🟡 C-4 — ¿El precio de renta depende del tamaño?

| Fuente | Postura |
|--------|---------|
| **R1 §4 y pregunta abierta #3** | Lo declara **pregunta abierta**: «¿El monto de renta depende del tamaño y tipo?» |
| **R2 (00:25:07)** | Lo afirma como hecho: «los montos de renta **varían según el tamaño** del contenedor (150, 192, 300)» |
| **R3** | **No se trató.** Solo se habló de precios de **venta** (varían por season, volumen, grado y uso) |

R2 parece una **inferencia del ASR/resumen** a partir de que existen tres montos distintos — no consta
que nadie lo afirmara.

**Estado: ABIERTA.** Sin respuesta del negocio para **rentas**. Ver `RN-REN-12` y la pregunta abierta #3
de R1 (tarifa estándar, descuentos a frecuentes), **que R3 tampoco respondió**.

---

### 🟡 C-5 — Cadencia de notificaciones de cobranza

El resumen curado de R3 la presenta como **decidida** («un aviso cada dos días»); la transcripción
muestra **tres propuestas en debate y ninguna cerrada**, terminando con Denisse devolviendo la
pregunta al equipo. Detalle en `RN-NOT-06`.

**Estado: ABIERTA**, mitigada por `RN-NOT-05` (configurable).

---

### 🟡 C-6 — "Estado" del contenedor: pregunta hecha, nunca respondida

Erik preguntó **tres veces** por los estados del ciclo de vida; Denisse respondió siempre por
categoría comercial. Detalle en `RN-INV-08`.

**Estado: ABIERTA. Bloquea el diseño de `containers.status`.**

---

## 18. Ambigüedades no resueltas

| # | Ambigüedad | Fuente | Por qué importa |
|---|-----------|--------|-----------------|
| A-1 | **Pago al chofer**: ¿30 % fijo, % por chofer, o monto negociado? | R1 §9 vs R3 01:15:03 | Define si `driver_pay_amount` es calculado o capturado |
| A-2 | **"40 con chassis"**: ¿medida, accesorio o ítem de inventario? | R1 §5 | Define si `container_sizes` alcanza o hace falta equipo aparte |
| A-3 | **Transportistas externos**: el dropdown lista varios («Ares Transport»), pero solo se documentó una compañía de transporte propia | R3 01:16:26 | Define si `carrier` es la compañía propia, un proveedor, o ambos |
| A-4 | **Renta de yarda**: R1/R2 la describen (2 días de gracia, cobro desde el 3.º). **R3 no la menciona.** No hay tarifa diaria levantada | R1 §4, R2 00:26:58 | No se puede calcular el cargo sin la tarifa |
| A-5 | **Clientes compartidos entre las dos compañías** o separados | Nunca preguntado | Define el particionado de `customers` |
| A-6 | **Reventa de un contenedor recomprado**: si vuelve a entrar el mismo número, ¿es el mismo registro o uno nuevo? | Nunca preguntado | `containers.number UNIQUE` colisiona |
| A-7 | **Depósito (deposit)**: aparece en facturas de venta (`RN-FIN-10`) y en rentas. ¿Es reembolsable? ¿Se aplica a la última cuota? | R3 00:51:47 | Define si es pasivo o anticipo de ingreso |
| A-8 | **Rol de Denisse**: R1 la lista como «administración del cliente»; R3 se titula «levantamiento con los dueños» y ella habla como propietaria | R1 vs R3 | Afecta quién tiene autoridad para aprobar reglas |

---

## 19. Decisiones pendientes — bloqueantes para la base de datos

Ordenadas por impacto. Las tres primeras **bloquean el arranque de migraciones**.

| # | Pregunta | Bloquea | Origen |
|---|----------|---------|--------|
| **P-1** | 🔴 ¿Se **integra** QuickBooks o se **construye** la facturación? | Todo el módulo Finanzas | C-1 |
| **P-2** | 🔴 ¿Cuáles son los **estados de inventario** de un contenedor? | `containers.status`, dashboard, disponibilidad | C-6 / RN-INV-08 |
| **P-3** | 🔴 ¿El **conteo físico** ya se hizo? ¿Cuál es el inventario real? | Carga inicial completa | RN-MIG-04 |
| P-4 | ¿El 7 % depende del medio de pago o del bien vendido? | Motor de impuestos | C-2 |
| P-5 | ¿Tarifa de renta por tamaño/tipo? ¿Descuentos a frecuentes? | `price_rules` para renta | C-4 / R1 #3 |
| P-6 | ¿Hacen delivery de contenedores de **terceros**? | Si `trips` requiere `container_id` | RN-VIA-10 / R1 #1 |
| P-7 | ¿Esquema de pago al chofer? | `trips.driver_pay_*` | A-1 |
| P-8 | ¿Tarifa diaria de **renta de yarda**? ¿Sigue vigente? | `yard_storage_charges` | A-4 |
| P-9 | ¿Confirman **7 %** y **3.5 %** como valores exactos? | Semilla de `settings` | RN-FIN-01, RN-FIN-07 |
| P-10 | ¿Entregan **credenciales de la API de QuickBooks**? | Solo si P-1 = integrar | R1 #9 |
| P-11 | ¿Qué **pasarela** exactamente? Denisse quedó de enviarla | Cobro en línea | RN-FIN-08 |
| P-12 | ¿Clientes compartidos entre compañías? | Particionado de `customers` | A-5 |
| P-13 | ¿Se **factura** la comisión del vendedor o solo se registra? | `sales.commission_amount` | RN-COM-09 |
| P-14 | ¿Cómo se centralizan los **leads**? | Módulo comercial | RN-COM-12 / R1 #2 |
| P-15 | ¿Requisitos formales/fiscales de la factura en EE. UU.? | Plantilla de factura | R1 #8 |

---

## 20. Entregables comprometidos por el cliente (R3) — aún no recibidos

Denisse se comprometió el 14 ago a entregar «este fin de semana». **Ninguno consta como recibido.**
Varios son insumo directo del modelo de datos:

| # | Entregable | Impacto en la BD |
|---|-----------|------------------|
| 1 | **Diagramas de procesos en Visio** de ambas compañías, con puntos de decisión y de carga de documentos | Valida el modelo completo |
| 2 | **Ejemplos de facturas y estimados** de cada compañía | Estructura de `invoices` / `invoice_lines` |
| 3 | Ejemplo de **certificado de exportación** | `documents` |
| 4 | Ejemplo de **certificado de impuestos** (y dónde va el número) | `tax_exemption_certificates` |
| 5 | Ejemplo de **credit card authorization form** | `documents` |
| 6 | **Excel de vehículos** con VIN y placas | Carga de `vehicles` |
| 7 | **Formato entregado a los chóferes** | Panel de chofer |
| 8 | Nombre y datos de la **plataforma de pago** | Integración de cobros |
| 9 | Plantilla llena de **roles** y de **categorías de gasto** | Semillas de `roles` y `expense_categories` |

> Erik acordó en R3 (01:32:32) que el equipo avanza **la base de datos en paralelo**, «que es algo
> que no va a cambiar». Denisse pidió expresamente **no escribir código de pantallas** hasta recibir
> sus diagramas, para no rehacer.
>
> Matiz honesto: la base de datos **sí puede cambiar** si P-1 (QuickBooks) o P-2 (estados) se
> resuelven en contra de lo asumido. Por eso ambos están marcados como bloqueantes.

---

## 21. Riesgos abiertos

**RG-1 — Crecimiento de alcance por encima de lo cotizado.** `[R1 §12]`
Entre nómina, inventario de camiones, materiales de reparación, integración con QuickBooks y pasarela
de pago, el alcance supera lo cotizado. R3 **añadió más**: gestión documental, antifraude con Sunbiz,
segunda compañía, facturación intercompañía, notificaciones SMS+email, panel de chóferes y reportes
fiscales. R1 recomendaba delimitar por escrito la fase 1 **antes** de la reunión con el cliente; la
reunión ocurrió y **no consta que se delimitara**.

**RG-2 — La calidad del dato es prerrequisito, no un detalle.** `[R1 §12]`
Sin conteo físico, la migración arranca con cifras erróneas y el sistema hereda el problema que viene
a resolver.

**RG-3 — El Excel refleja pedidos puntuales, no lógica administrativa.** `[R1 §12]`
Al normalizar aparecerán comportamientos que el dueño podría extrañar.

**RG-4 — Solo se ha entrevistado a una persona del negocio.** `[observación]`
El Sr. Michael, decisor y usuario del dashboard, **no ha sido entrevistado directamente** en ninguna
de las dos reuniones. Sus preferencias llegan de segunda mano.

**RG-5 — Riesgo normativo si se construye facturación propia.** `[R1 §6]`
Implica asumir la parte legal y fiscal de EE. UU. Ver `04_quickbooks_vs_facturacion_propia.md`.

**RG-6 — Tensión entre "todo administrable" y plazo.** `[observación]`
`RN-USR-05`, `RN-GAS-02`, `RN-NOT-05` y `RN-SIS-03` exigen que menús, categorías, cadencias, roles y
nomenclatura sean configurables en runtime. Es correcto, y **multiplica el trabajo** frente a valores
fijos en código. Debe estar reflejado en la estimación.
