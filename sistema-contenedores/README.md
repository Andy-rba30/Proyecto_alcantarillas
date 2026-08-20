# Sistema de gestión de contenedores — Diseño de base de datos

Entregable de la fase de diseño de base de datos, construido a partir de las minutas de
levantamiento de requerimientos.

> ⚠️ **Nota sobre la ubicación.** Este material está en el repositorio `Proyecto_alcantarillas`,
> que contiene un proyecto de ingeniería de alcantarillas en Python — dominio distinto. Se dejó
> aquí, aislado en `sistema-contenedores/`, porque es la rama de trabajo indicada. Cuando arranques
> el proyecto Laravel, copia `database/` a la raíz del proyecto nuevo y `docs/` donde corresponda.

---

## Contenido

```
sistema-contenedores/
├── docs/
│   ├── 01_reglas_de_negocio_consolidadas.md    ← reglas con trazabilidad, contradicciones, pendientes
│   ├── 02_modelo_de_datos.md                   ← diccionario de datos: tablas, campos, tipos
│   ├── 03_migraciones_explicadas.md            ← orden, convenciones y decisiones de las migraciones
│   └── 04_quickbooks_vs_facturacion_propia.md  ← análisis y recomendación
└── database/
    ├── migrations/   38 archivos, verificados con php -l
    └── seeders/      catálogos, parámetros y roles — solo valores trazables a las minutas
```

**Orden de lectura sugerido:** 01 → 04 → 02 → 03.
El 04 va segundo porque la decisión sobre QuickBooks condiciona el alcance del módulo de finanzas.

---

## Stack

Laravel 12.55 · PHP 8.2.4 · Livewire 4 · Vite 7 · Tailwind 4 · AdminLTE 4 ·
Spatie Permission · MySQL 8.0+ / MariaDB 10.6+

---

## Resumen del modelo

**38 migraciones · 38 tablas propias**, más `users` de Laravel, 5 de Spatie Permission y 1 de
Spatie Activitylog.

| Módulo | Tablas |
|--------|--------|
| Núcleo | `companies`, `settings`, `employees` (+ extensión de `users`) |
| Terceros | `customers`, `customer_contacts`, `tax_exemption_certificates`, `suppliers`, `depots` |
| Catálogos | `container_types`, `container_sizes`, `container_grades` |
| Compras e inventario | `releases`, `release_lines`, `containers`, `container_status_histories` |
| Precios | `price_rules` |
| Comercial | `quotes`, `quote_lines`, `sales`, `sale_containers` |
| Rentas | `rentals`, `rental_periods`, `yard_storage_charges` |
| Transporte | `vehicles`, `vehicle_maintenances`, `trips`, `driver_payouts` |
| Finanzas | `invoices`, `invoice_lines`, `payments`, `payment_allocations`, `expense_categories`, `expenses` |
| Documental | `documents` |
| Notificaciones | `notification_rules`, `notification_logs` |
| Soporte | `import_batches`, `quickbooks_sync_states` |

---

## Las cinco decisiones que sostienen el modelo

1. **Multiempresa desde el día uno.** `RN-ORG-01`: son dos compañías que tributan distinto y se
   facturan entre sí. No es un `tenant_id` de SaaS — el aislamiento no puede ser total.

2. **`invoice_lines.is_taxable` a nivel de línea.** Única forma de cumplir a la vez que el 7 % grava
   solo el contenedor (`RN-FIN-02`), que el transporte nunca tributa (`RN-FIN-03`), que Transporte sí
   grava cuando vende (`RN-ORG-06`) y que el cliente exento no paga en ninguna línea (`RN-FIN-04`).

3. **Contenedor y delivery separados internamente, consolidados de cara al cliente.** `RN-COM-03` y
   `RN-COM-04`. Y `delivery_amount` (lo que se cobra) ≠ `delivery_cost` (lo que se paga a Transporte).

4. **`rental_periods` materializa cada ciclo como fila.** De ahí salen el período explícito en factura
   (`RN-REN-03`), el semáforo (`RN-REN-07`), los pagos adelantados (`RN-REN-08`) y el dashboard de
   morosidad (`RN-REP-06`).

5. **Valores congelados en cada transacción**: `tax_rate`, `grace_days`, `late_fee_amount`,
   `unit_cost_snapshot`. Si el parámetro global cambia mañana, los documentos históricos siguen
   reproduciéndose igual.

---

## 🔴 Bloqueantes antes de cargar datos

| # | Pregunta | Bloquea |
|---|----------|---------|
| **P-1** | ¿QuickBooks se integra o se construye la facturación? | Todo el módulo de Finanzas |
| **P-2** | ¿Cuál es el catálogo de **estados** de un contenedor? | `containers.status`, dashboard, disponibilidad |
| **P-3** | ¿Se hizo el conteo físico? ¿Cuál es el inventario real? | La carga inicial completa |

P-2 merece énfasis: Erik preguntó **tres veces** por los estados del ciclo de vida y la respuesta fue
siempre sobre categoría comercial. **La pregunta nunca se respondió.** Los valores del esquema son una
propuesta señalada como tal.

Las 15 decisiones pendientes están en `docs/01_reglas_de_negocio_consolidadas.md` §19.

---

## Puesta en marcha

```bash
composer require spatie/laravel-permission spatie/laravel-activitylog
php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"
php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-migrations"
```

🔴 En `config/permission.php`, **antes** del primer `migrate`:

```php
'teams' => true,   // RN-ORG-01: permisos por compañía
```

```bash
php artisan migrate --seed
```

Detalles y errores frecuentes: `docs/03_migraciones_explicadas.md` §6 y §7.

---

## Sobre las fuentes

Se recibieron tres PDFs, pero corresponden a **dos reuniones**:

| ID | Reunión | Naturaleza |
|----|---------|-----------|
| **R1** | 8 ago 2026, 17:31 — Ronny + Erik | Minuta redactada por una persona |
| **R2** | 8 ago 2026, 17:31 — Ronny + Erik | Notas automáticas de Gemini de **esa misma llamada** |
| **R3** | 14 ago 2026, 09:43 — Ronny + Erik + **Denisse Hernández** | Notas + transcripción literal (87 págs.) |

R1 y R2 son la misma sesión: mismo día, misma hora, mismos participantes. Una discrepancia entre ellas
no es una contradicción del cliente, sino ruido de transcripción. Jerarquía adoptada: **R3 > R1 > R2**.

Detalle y justificación: `docs/01_reglas_de_negocio_consolidadas.md` §0.
