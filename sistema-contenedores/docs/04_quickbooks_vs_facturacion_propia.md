# QuickBooks API vs. facturación propia — análisis y recomendación

> Opinión técnica solicitada. Va firmada como criterio de ingeniería, no como regla de negocio:
> la decisión es del cliente. Lo que sí es un hecho verificable es que **la pregunta, tal como se
> planteó en la primera reunión, parte de una premisa falsa** — y eso hay que corregirlo antes de
> decidir.

---

## 1. La premisa que se cayó

En R1 §6 el equipo evaluó dos opciones y cerró así:

| Opción | Descripción | Evaluación en R1 |
|--------|-------------|------------------|
| A — Facturación propia | Rehacer presupuesto y factura dentro del sistema | «Implica asumir la parte legal y fiscal de EE. UU.» |
| **B — Integración por API** | Dejar presupuesto y factura en QuickBooks y consumirla | **«Opción preferida por ambos.** Denise ya domina la herramienta y evita riesgo normativo.» |

R2 lo elevó a decisión estratégica: *«Se decidió utilizar la API de QuickBooks»*.

**El 14 de agosto, Denisse desmontó el supuesto sobre el que se eligió B.**

> Erik: «Entonces básicamente todas las finanzas las llevan allí.»
> Denisse: «**de una sola [compañía], que es la de transporte. La otra se está llevando en el Excel
> que creó Ronny.**»
> — R3 (01:10:59–01:12:19)

Y poco después, cuando Ronny le pregunta directo si seguiría manteniendo QuickBooks:

> «me dijiste que si hacemos que esta [plataforma] mande los invoices y haga todas las cosas y
> registre el pago y todo lo demás, **ya no tengo que usar QuickBooks, puedo transicionar a esta**»
> — R3 (01:10:59)

### Qué significa esto en concreto

Se eligió la Opción B creyendo que **QuickBooks ya resolvía la facturación del negocio**. No la
resuelve. QuickBooks cubre la compañía de **Transporte**. Toda la operación de contenedores —ventas,
rentas, impuestos, releases, inventario— **nunca estuvo en QuickBooks**: está en el Excel que este
proyecto viene a reemplazar.

⇒ Integrarse a QuickBooks para "traer las facturas" traería **las facturas de la compañía equivocada**.

La decisión de R1 no fue un error de criterio: fue una decisión correcta sobre información incompleta.
Ahora la información cambió, y hay que volver a decidir. Eso es lo normal en un levantamiento; lo
anormal sería no revisarla.

---

## 2. La pregunta correcta

No es *"¿integrar o construir?"*. Son tres preguntas que se estaban tratando como una:

| # | Pregunta | Respuesta corta |
|---|----------|-----------------|
| 1 | ¿Dónde se **originan** presupuestos y facturas? | En el sistema nuevo |
| 2 | ¿Dónde vive la **contabilidad** (bancos, P&L, cierre fiscal)? | En QuickBooks |
| 3 | ¿Se **sincronizan** entre sí, en qué dirección y cuándo? | Sí, sistema → QBO, en fase 2 |

Fundir las tres en una sola pregunta es lo que produjo la decisión de R1.

---

## 3. Por qué la facturación tiene que originarse en el sistema

No es preferencia arquitectónica. Es que **las reglas que el propio cliente enunció en R3 no se pueden
cumplir desde QuickBooks.** Una por una:

| Requisito del cliente | Regla | ¿QuickBooks lo hace? |
|----------------------|-------|---------------------|
| Vincular **el número de contenedor** a la línea de factura para calcular la ganancia real | `RN-REP-02` | ❌ **No.** R1 §6 ya lo identificó: *«QuickBooks entrega el monto facturado pero desconoce en cuánto se compró el contenedor»* |
| Precio **consolidado** al cliente, pero impuesto calculado **solo sobre el contenedor** | `RN-COM-04` | ❌ No de forma nativa. Exige lógica de negocio propia sobre dos importes separados internamente |
| Ciclos de renta **anclados a la fecha del delivery** (día 2 → día 2), autogenerados | `RN-REN-02` | ❌ No. La facturación recurrente de QBO no modela contratos de renta con anclaje operativo |
| **Período explícito** en cada factura de renta | `RN-REN-03` | ⚠️ Solo escribiéndolo a mano en la descripción, que es justo lo que se quiere eliminar |
| **Semáforo** amarillo/rojo y dashboard de morosidad | `RN-REN-07`, `RN-REP-06` | ❌ No |
| Notificaciones automáticas **SMS + email a todos los contactos**, cadencia configurable | `RN-NOT-01`…`RN-NOT-06` | ❌ No |
| Fee de mora de **$100 condonable** con auditoría de quién condonó | `RN-REN-05`, `RN-REN-06` | ❌ No |
| Certificado de exención con **renovación anual** y documento adjunto por año | `RN-FIN-06` | ❌ No |
| **Certificado de exportación** en PDF vinculado a venta, contenedor y factura | `RN-COM-02`, `RN-DOC-04` | ❌ No |
| Bloqueo de tarjeta sin **Credit Card Authorization Form** y verificación en Sunbiz | `RN-FRD-01`…`RN-FRD-04` | ❌ No |
| **Releases** con plazo de 14 días y fee diario por proveedor | `RN-REL-05`…`RN-REL-07` | ❌ No |
| Ganancia real = venta − costo − gastos − impuestos | `RN-REP-01` | ❌ No, porque no conoce el costo del contenedor |

**Trece requisitos, ninguno resuelto por QuickBooks.**

La conclusión incómoda: bajo la Opción B habría que construir igualmente **casi toda** la lógica de
negocio alrededor de la factura. El documento PDF es la parte pequeña del trabajo. Lo caro es el
motor de impuestos por línea, los ciclos de renta y la cobranza automática — y eso hay que hacerlo
en los dos escenarios.

> Dicho de otro modo: la Opción B no ahorra el trabajo que parece ahorrar. Ahorra el **riesgo
> normativo**, que es una cosa distinta y sí es real. Ver §5.

---

## 4. Por qué NO hay que reemplazar QuickBooks

Denisse dijo que podría transicionar completamente. **Mi recomendación es que no lo haga**, y conviene
decírselo con claridad aunque no sea lo que espera oír.

Lo que QuickBooks aporta hoy y sería caro y arriesgado reconstruir:

| Función | Fuente | Por qué no reconstruirla |
|---------|--------|-------------------------|
| **Conciliación bancaria** con bancos de EE. UU. | R3 (01:08:22) | Requiere integraciones con feeds bancarios. Meses de trabajo y un problema de mantenimiento permanente |
| **Profit & Loss** y reportes financieros | R3 (01:08:22): «te saca también un profit and loss» | Contabilidad de doble partida. Es un producto en sí mismo |
| **Cierre fiscal de fin de año, por categoría** | `RN-ORG-05` | Trabajo del contador. El sistema no debe competir con eso |
| **El flujo del contador** | R1 §6: «el contador trabaja por el lado de las cuentas bancarias y los gastos» | Hay una persona externa con un proceso montado. Romperlo genera fricción real |
| Recibos de pago y registro de cuentas bancarias | R3 (01:08:22) | Ya funciona |

Hay además un argumento que suele pesar más que los técnicos: **el contador es un tercero que no es
parte del proyecto.** Si el sistema deja de alimentar QuickBooks, alguien tiene que reconstruir su
flujo de trabajo, y ese alguien no está en las reuniones ni en el presupuesto.

---

## 5. El riesgo que R1 identificó bien y sigue vigente

R1 §6 acertó al señalar que la facturación propia *«implica asumir la parte legal y fiscal de EE. UU.»*.
Ese riesgo no desaparece con este análisis. Concretamente:

**5.1 — El "7 %" no está verificado.** `RN-FIN-01` viene marcado como *aproximadamente* 7 % desde R1, y
sigue sin confirmarse (P-9). En Florida el impuesto sobre ventas se compone de una tasa estatal más un
recargo del condado, y el recargo **varía según el condado**. Antes de emitir una sola factura:

- Confirmar con el contador **cómo se compone** ese 7 % y si el recargo depende de la ubicación.
- Confirmar si la venta con delivery tributa según el condado del comprador o el del vendedor.
- El esquema ya soporta que la tasa cambie (`tax_rate` congelada por documento, `price_rules` con
  vigencia), pero **el sistema no puede decidir la regla fiscal**.

**5.2 — Requisitos formales de la factura.** Pregunta abierta #8 de R1, **nunca respondida**. Denisse
quedó de enviar ejemplos de factura de ambas compañías (§20 #2). Hasta tenerlos, la plantilla es una
suposición.

**5.3 — 🔴 Riesgo que nadie ha señalado todavía: PCI-DSS en el Credit Card Authorization Form.**

`RN-FRD-01` describe un formulario que el cliente llena **con el número de tarjeta, el billing y la
firma**, y `RN-FRD-02` dice que se archiva junto a la factura. En el modelo de datos eso sería
`documents.category = 'cc_authorization'`.

**Almacenar ese PDF en el sistema mete al proyecto dentro del alcance de PCI-DSS.** Un servidor
guardando números de tarjeta completos, aunque sea en imágenes escaneadas, cambia por completo las
obligaciones de seguridad, cifrado, retención y auditoría — y la responsabilidad ante una brecha.

Es especialmente delicado porque toda la política antifraude de `RN-FRD-01`…`RN-FRD-05` nació de
pérdidas reales por chargebacks: el cliente ya sabe lo que cuesta un incidente con tarjetas.

Recomendación concreta:

- **No almacenar el PDF con el número de tarjeta completo** en el sistema.
- Sustituir el flujo por la autorización propia de Square (*card on file* con token), que deja el dato
  sensible fuera de tu infraestructura y conserva el efecto legal.
- Si el cliente insiste en conservar el formulario firmado, guardar **solo** los últimos 4 dígitos y la
  firma, con el resto redactado.
- **Plantear esto a Denisse antes de construir el módulo de documentos**, no después.

Este punto no estaba en ninguna minuta. Lo señalo porque es exactamente el tipo de decisión que es
barata de tomar hoy y muy cara de revertir.

---

## 6. Recomendación

> ### Construir la facturación en el sistema. Mantener QuickBooks como sistema contable. Sincronizar en una sola dirección, y en fase 2.

Es un **híbrido**, no la Opción A ni la B de R1.

### Reparto de responsabilidades

| Dominio | Dónde vive | Por qué |
|---------|-----------|---------|
| Clientes, contactos, certificados | **Sistema** | `RN-CLI-01`…`RN-CLI-07`, `RN-FIN-06` |
| Contenedores, releases, inventario, costos | **Sistema** | QuickBooks no los conoce |
| Presupuestos y facturas de **Contenedores** | **Sistema** | Hoy están en Excel, no en QBO |
| Rentas, ciclos, mora, cobranza | **Sistema** | 13 requisitos que QBO no cubre |
| Viajes, chóferes, flota | **Sistema** | `RN-VIA-*` |
| Gastos operativos y ganancia real | **Sistema** | `RN-REP-01`, `RN-REP-02` |
| Cobro en línea | **Square** | `RN-FIN-08`. Ya está en uso, 3.5 % |
| Conciliación bancaria | **QuickBooks** | No reconstruir |
| P&L y estados financieros | **QuickBooks** | No reconstruir |
| Cierre fiscal anual | **QuickBooks + contador** | `RN-ORG-05` |
| Facturas de **Transporte** | **QuickBooks** (fase 1) → evaluar migrar | Ya funciona ahí |

### Dirección de la sincronización: **sistema → QuickBooks**, una sola vía

Sincronización bidireccional es donde estos proyectos se hunden: dos fuentes de verdad, conflictos de
`SyncToken`, registros duplicados y nadie sabe cuál gana. Una sola dirección con el sistema como origen
elimina la clase entera de problemas.

Se empujan a QBO: clientes, facturas, pagos. Se leen de QBO: nada, o como mucho el estado de
conciliación en una fase posterior.

---

## 7. Plan por fases

### Fase 1 — Sin integración (MVP)

Construir el módulo de facturación completo. **No tocar la API de QuickBooks todavía.**

- Presupuestos y facturas nativos, con el motor de impuestos por línea (`invoice_lines.is_taxable`)
- Cobro mediante **link de pago de Square** en la factura (`RN-FIN-08`)
- **Exportación CSV/Excel** para el contador: facturas, pagos y gastos por rango de fechas —
  que es exactamente el reporte que Denisse pidió en `RN-REP-03`
- Denisse sigue usando QuickBooks para Transporte, sin cambios

**Por qué empezar aquí:**
- P-10 (¿entregan las credenciales de la API?) **sigue sin respuesta** desde R1
- Publicar una app de Intuit en producción requiere revisión de su parte; el sandbox no sirve para operar
- La integración es la parte del sistema que **menos valor entrega el primer día**: el cliente necesita
  primero dejar el Excel
- Una exportación CSV cubre el 80 % del beneficio con el 5 % del esfuerzo

### Fase 2 — Sincronización unidireccional a QuickBooks

Una vez la facturación esté estable y el cliente entregue credenciales:

- OAuth 2.0 con Intuit, refresh token persistido y rotado
- Push de `Customer`, `Invoice` y `Payment` mediante cola de trabajos con reintentos
- `quickbooks_sync_states` (migración `003700`) guarda `qbo_id`, `SyncToken` y estado
- Los fallos van a un **módulo de pendientes** revisable — no se pierden en un log

### Fase 3 — Opcional, solo si el cliente lo pide

Lectura de conciliación bancaria, o migración de la facturación de Transporte al sistema.

---

## 8. Comparación de las tres rutas

| Criterio | A · Solo sistema, sin QBO | B · Solo integrar QBO | **Híbrido (recomendado)** |
|----------|--------------------------|----------------------|--------------------------|
| Cumple los 13 requisitos de R3 | ✅ | ❌ | ✅ |
| Ganancia real por contenedor | ✅ | ❌ | ✅ |
| Conserva el flujo del contador | ❌ | ✅ | ✅ |
| Riesgo normativo asumido | 🔴 Alto | 🟢 Bajo | 🟠 Medio, acotado a la emisión |
| Dependencia de credenciales de terceros (P-10) | 🟢 Ninguna | 🔴 Bloqueante | 🟢 No bloquea la fase 1 |
| Doble captura de datos | ✅ Ninguna | 🟠 Parcial | ✅ Ninguna |
| Riesgo de conflictos de sincronización | 🟢 N/A | 🔴 Alto (bidireccional) | 🟢 Bajo (unidireccional) |
| Entrega valor en fase 1 | ✅ | ❌ | ✅ |
| Reconstruye contabilidad | 🔴 Sí | ✅ No | ✅ No |

---

## 9. Lo que hay que confirmar con el cliente antes de escribir código de facturación

En orden:

1. **P-1** — Plantearle a Denisse el hallazgo de §1 y validar el híbrido. Es una conversación de quince
   minutos que evita semanas de trabajo equivocado.
2. **§20 #2** — Ejemplos de factura y estimado de **ambas** compañías. Sin ellos, la plantilla es
   suposición.
3. **P-9** — Confirmar con el contador la composición exacta del 7 % y si depende del condado.
4. **P-15** — Requisitos formales de la factura en EE. UU. (pregunta #8 de R1, aún abierta).
5. **§5.3** — Plantear el riesgo PCI del Credit Card Authorization Form y acordar la alternativa.
6. **P-11** — Datos de Square, que Denisse quedó de enviar.
7. **P-10** — Credenciales de QuickBooks, **solo si se aprueba la fase 2**.

---

## 10. Resumen en un párrafo

La decisión de la primera reunión —integrar QuickBooks y no construir facturación— era razonable con
la información de entonces, pero se apoyaba en creer que QuickBooks ya cubría el negocio de
contenedores. No lo cubre: solo cubre Transporte. Además, trece de los requisitos que el propio cliente
enunció en la reunión con los dueños son imposibles de satisfacer desde QuickBooks, empezando por el
más importante — vincular el contenedor a la factura para conocer la ganancia real. Al mismo tiempo,
reemplazar QuickBooks del todo, como Denisse llegó a plantear, significaría reconstruir conciliación
bancaria y contabilidad, que es un producto distinto y rompería el flujo del contador. La salida
sensata es el punto medio: **el sistema es el origen de la operación y de la factura; QuickBooks sigue
siendo el libro contable; la información viaja en una sola dirección, del sistema hacia QuickBooks, y
recién en una segunda fase.** La fase 1 arranca sin integración alguna y con una exportación para el
contador, porque el cliente necesita salir del Excel antes que sincronizar nada.
