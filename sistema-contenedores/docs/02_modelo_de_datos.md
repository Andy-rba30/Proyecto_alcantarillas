# Modelo de datos — Sistema de gestión de contenedores

**Stack:** Laravel 12.55 · PHP 8.2.4 · MySQL 8.0+ / MariaDB 10.6+ · Livewire 4 · Spatie Permission

Cada tabla y cada campo llevan referencia a la regla de negocio que los justifica
(`RN-XXX-NN` → ver `01_reglas_de_negocio_consolidadas.md`).
Los campos marcados `[PROPUESTA]` **no provienen de las minutas**: son decisiones técnicas mías,
señaladas para que puedas cuestionarlas o eliminarlas.

---

## 0. Convenciones globales

### 0.1 Motor y juego de caracteres

```php
// config/database.php → connections.mysql
'charset'   => 'utf8mb4',
'collation' => 'utf8mb4_unicode_ci',
'engine'    => 'InnoDB',
```

`utf8mb4` es obligatorio, no opcional: hay nombres de clientes en español con acentos, direcciones en
inglés y notas que pueden traer emojis desde WhatsApp. `utf8` de MySQL es de 3 bytes y **rompe** con
cualquier carácter fuera del BMP.

### 0.2 Tipos por familia de dato

| Familia | Tipo SQL | Laravel | Por qué |
|---------|----------|---------|---------|
| **Clave primaria** | `BIGINT UNSIGNED AUTO_INCREMENT` | `$table->id()` | Por defecto en Laravel 12. `INT` se agota a 4.2 mil millones; en `notification_logs` eso no es teórico |
| **Clave foránea** | `BIGINT UNSIGNED` | `$table->foreignId()` | Debe coincidir **exactamente** con el PK o el FK falla al crearse |
| **Dinero** | `DECIMAL(12,2)` | `$table->decimal(x, 12, 2)` | 🔴 **Nunca `FLOAT` ni `DOUBLE`.** Ver §0.3 |
| **Dinero agregado** | `DECIMAL(14,2)` | `decimal(x, 14, 2)` | Totales de release y acumulados de reportes |
| **Tasa / porcentaje** | `DECIMAL(6,4)` | `decimal(x, 6, 4)` | `0.0700` = 7 %, `0.0350` = 3.5 %. Ver §0.4 |
| **Cantidad entera** | `INT UNSIGNED` / `SMALLINT UNSIGNED` | `unsignedInteger` | Cantidades de release, días de plazo |
| **Fecha de negocio** | `DATE` | `$table->date()` | Sin hora: "vence el 23" es un día, no un instante |
| **Marca de auditoría** | `TIMESTAMP` | `timestamps()` | Con hora |
| **Booleano** | `TINYINT(1)` | `$table->boolean()` | MySQL no tiene BOOL real |
| **Texto corto** | `VARCHAR(n)` | `$table->string(n)` | Dimensionado por caso, no `255` por inercia |
| **Texto largo** | `TEXT` | `$table->text()` | Notas y descripciones libres |
| **Estructura variable** | `JSON` | `$table->json()` | Payloads de integración, logs de importación |
| **Enumerado cerrado** | `VARCHAR(n)` + Enum PHP | `$table->string()` | Ver §0.5 |

### 0.3 Dinero: por qué `DECIMAL` y no `FLOAT`

`FLOAT`/`DOUBLE` son binarios de base 2 y **no pueden representar exactamente** valores decimales.
En este sistema eso no es un tecnicismo: `RN-FIN-02` obliga a calcular el 7 % sobre el contenedor y
sumar el delivery aparte. Con `FLOAT`:

```
150.00 en FLOAT  →  150.00000000000002...
× 1.07           →  160.50000000000003
```

Multiplica eso por cientos de rentas mensuales y el reporte fiscal de `RN-REP-03` — el que Denisse
pidió expresamente para declarar impuestos — deja de cuadrar contra el banco por centavos que nadie
sabe explicar.

`DECIMAL(12,2)` almacena **exacto**, con techo en 9.999.999.999,99. Sobra: la venta más alta citada
ronda los 3.500 (`R1 §2`) y el mes revisado movió 269.000 (`RN-REP-07`).

**Regla de implementación:** todo cálculo monetario se hace en PHP con `bcmath` o con enteros de
centavos, **jamás** con aritmética de punto flotante nativa.

```php
// app/Casts/Money.php  [PROPUESTA]
// Cast que garantiza string decimal en ida y vuelta, evitando que PHP
// convierta a float al hidratar el modelo.
```

### 0.4 Tasas: por qué `DECIMAL(6,4)` y no `DECIMAL(5,2)`

Guardar `7.00` (como porcentaje) obliga a dividir entre 100 en cada uso — y a recordar hacerlo.
Guardar `0.0700` (como factor) permite multiplicar directo.

`(6,4)` da 2 enteros + 4 decimales: hasta `99.9999` como factor, y precisión de **una diezmilésima**.
Necesaria para el 3.5 % de `RN-FIN-07`: `0.0350`.

> Se guarda la tasa **congelada en cada transacción**, no solo en configuración. Si mañana Florida
> sube el impuesto al 7.5 %, las facturas viejas deben seguir mostrando el 7 % con el que se
> emitieron. Por eso `sales.tax_rate`, `invoices.tax_rate` y `rentals.tax_rate` existen además de
> `settings`.

### 0.5 Enumerados: cuándo `VARCHAR`, cuándo tabla

`RN-GAS-02` y `RN-USR-05` son explícitos: el cliente quiere administrar listas **desde el sistema**.
Eso parte los enumerados en dos grupos, y la decisión no es estética:

| Criterio | Solución | Ejemplos |
|----------|----------|----------|
| El cliente **añadirá valores** sin llamarnos | **Tabla de catálogo** con FK | `expense_categories` (RN-GAS-02), `container_grades`, `container_types`, `container_sizes` |
| El valor tiene **lógica de negocio asociada en código** | `VARCHAR` + Enum PHP respaldado | `sales.status`, `rental_periods.status`, `payments.method` |

**Nunca `ENUM` de MySQL.** Añadir un valor exige `ALTER TABLE` con bloqueo de tabla, no es portable a
PostgreSQL y Laravel lo soporta a medias en migraciones de modificación.

```php
// app/Enums/RentalPeriodStatus.php
enum RentalPeriodStatus: string {
    case Pending = 'pending';
    case Paid    = 'paid';
    case Overdue = 'overdue';
    case Waived  = 'waived';
}
// En el modelo:  protected $casts = ['status' => RentalPeriodStatus::class];
```

Ventaja concreta: el semáforo de `RN-REN-07` vive como método del enum, no como `if` repartido por
las vistas Livewire.

### 0.6 Multiempresa

`RN-ORG-01` obliga a que **casi toda tabla transaccional lleve `company_id`**. No es un `tenant_id`
de SaaS: son dos compañías de un mismo dueño que **se facturan entre sí** (`RN-ORG-07`), así que el
aislamiento **no puede ser total**.

```php
// app/Models/Concerns/BelongsToCompany.php  [PROPUESTA]
// Global scope que filtra por la compañía activa en sesión,
// con método ->withoutCompanyScope() para los reportes consolidados
// y para la facturación intercompañía.
```

### 0.7 Borrado lógico

`softDeletes()` en toda tabla maestra y transaccional. Razón de negocio, no de gusto: `RN-DOC-03`
exige poder recuperar el histórico completo de una venta en cualquier momento, y `RN-DOC-05` exige
las facturas históricas por cliente. Un `DELETE` físico rompe ambas.

**Excepción:** las tablas de bitácora (`notification_logs`, `container_status_histories`,
`activity_log`) **no** llevan `softDeletes`. Son append-only por definición.

### 0.8 Nomenclatura

`RN-SIS-03` es una regla de negocio real, no una preferencia: Denisse pidió términos genéricos porque
**contempla vender la empresa** y quiere que el software siga siendo comprensible.

⇒ Nombres de tabla y columna **en inglés estándar de dominio** (`containers`, `invoices`, `releases`,
`quotes`), no en jerga interna (`yarda`, `movida`, `rilas`). La traducción a español vive en los
archivos de idioma (`RN-SIS-01`), no en el esquema.

---

# A. Núcleo y configuración

## A.1 `companies`

> **Fuente:** `RN-ORG-01` a `RN-ORG-09`. Sin esta tabla el modelo entero es incorrecto:
> las dos compañías tributan distinto y se facturan entre sí.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | PK |
| `name` | `VARCHAR(150)` | No | — | Nombre comercial ("Florida", "Transporte") |
| `legal_name` | `VARCHAR(200)` | Sí | `NULL` | Razón social para la factura. `[PROPUESTA]` — pendiente de los ejemplos de factura (§20 #2) |
| `tax_id` | `VARCHAR(30)` | Sí | `NULL` | EIN. `[PROPUESTA]` |
| `kind` | `VARCHAR(20)` | No | — | `containers` \| `transport` — `RN-ORG-01` |
| `collects_sales_tax` | `TINYINT(1)` | No | `0` | 🔴 `RN-ORG-03` / `RN-ORG-04`. Ver nota abajo |
| `default_tax_rate` | `DECIMAL(6,4)` | Sí | `NULL` | `0.0700` — `RN-FIN-01`, **sujeto a P-9** |
| `credit_card_fee_rate` | `DECIMAL(6,4)` | Sí | `NULL` | `0.0350` — `RN-FIN-07`, **sujeto a P-9** |
| `address_line1` | `VARCHAR(150)` | Sí | `NULL` | Pie de factura |
| `city` | `VARCHAR(80)` | Sí | `NULL` | |
| `state` | `CHAR(2)` | Sí | `NULL` | Estado de EE. UU. Exactamente 2 → `CHAR`, no `VARCHAR` |
| `zip` | `VARCHAR(10)` | Sí | `NULL` | Formato ZIP+4 `33101-1234` = 10 caracteres |
| `phone` | `VARCHAR(25)` | Sí | `NULL` | Ver §B.1 sobre teléfonos |
| `email` | `VARCHAR(150)` | Sí | `NULL` | |
| `logo_path` | `VARCHAR(500)` | Sí | `NULL` | Logo en factura y en AdminLTE |
| `invoice_prefix` | `VARCHAR(10)` | Sí | `NULL` | `RN-ORG-09`: facturas separadas por compañía |
| `is_active` | `TINYINT(1)` | No | `1` | |
| `created_at` / `updated_at` | `TIMESTAMP` | Sí | `NULL` | |
| `deleted_at` | `TIMESTAMP` | Sí | `NULL` | |

> ⚠️ **`collects_sales_tax` NO decide el impuesto por sí solo.**
> `RN-ORG-06` es explícita: Transporte también puede vender contenedores, y en ese caso **sí** cobra
> impuesto. Este campo es solo el **valor por defecto** al abrir una operación. La decisión real de
> gravar vive en `invoice_lines.is_taxable` (§I.2), porque depende de **qué se vende**, no de **quién
> lo vende**.

---

## A.2 `settings`

> **Fuente:** `RN-NOT-05`, `RN-USR-05`, `RN-GAS-02`, `RN-REN-04`, `RN-REN-05`.
> El cliente pidió explícitamente poder cambiar plazos y cadencias sin llamar al desarrollador.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `NULL` = valor global. `RN-ORG-01` |
| `group` | `VARCHAR(50)` | No | — | `billing`, `rentals`, `notifications`, `releases` |
| `key` | `VARCHAR(100)` | No | — | Clave técnica |
| `value` | `TEXT` | Sí | `NULL` | Valor serializado |
| `type` | `VARCHAR(20)` | No | `'string'` | `string`\|`integer`\|`decimal`\|`boolean`\|`json` — para castear al leer |
| `label` | `VARCHAR(150)` | Sí | `NULL` | Etiqueta visible en la pantalla de configuración |
| `is_editable` | `TINYINT(1)` | No | `1` | Distingue lo que el cliente puede tocar de lo técnico |
| `created_at` / `updated_at` | `TIMESTAMP` | Sí | `NULL` | |

**Índices:** `UNIQUE (company_id, key)`

**Semillas obligatorias**, todas trazables:

| `key` | Valor | Tipo | Regla | Estado |
|-------|-------|------|-------|--------|
| `sales_tax_rate` | `0.0700` | decimal | `RN-FIN-01` | ⚠️ P-9 |
| `credit_card_fee_rate` | `0.0350` | decimal | `RN-FIN-07` | ⚠️ P-9 |
| `rent_grace_days` | `5` | integer | `RN-REN-04` | ✅ |
| `rent_late_fee_amount` | `100.00` | decimal | `RN-REN-05` | ✅ |
| `rent_minimum_months` | `1` | integer | `RN-REN-01` | ✅ |
| `release_free_days` | `14` | integer | `RN-REL-05` | ✅ |
| `yard_free_days` | `2` | integer | R1 §4 | ⚠️ A-4 |
| `yard_daily_rate` | `NULL` | decimal | — | 🔴 **P-8: nunca levantado** |
| `dunning_start_day` | `6` | integer | `RN-NOT-06` | ⚠️ C-5 |
| `dunning_interval_days` | `2` | integer | `RN-NOT-06` | ⚠️ C-5 |
| `dunning_end_day` | `10` | integer | `RN-NOT-06` | ⚠️ C-5 |
| `driver_pay_rate_default` | `0.3000` | decimal | `RN-VIA-08` | 🔴 **P-7: ambiguo** |

> Nota de método: `yard_daily_rate` se siembra en `NULL` **a propósito**. Si se sembrara con un
> número inventado, el sistema calcularía cargos falsos y nadie lo notaría. En `NULL`, el módulo
> falla ruidosamente y obliga a preguntar. Prefiero un error visible a un dato inventado.

---

## A.3 `users` — extensión de la tabla de Laravel

> **Fuente:** `RN-USR-01` a `RN-USR-05`, `RN-SIS-01`.

Se conserva la migración por defecto de Laravel 12 y se **añaden** columnas en una migración aparte:

| Columna añadida | Tipo SQL | Null | Default | Regla / Justificación |
|-----------------|----------|------|---------|----------------------|
| `company_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Compañía por defecto al iniciar sesión. `RN-ORG-01` |
| `locale` | `VARCHAR(5)` | No | `'es'` | `es` \| `en` — `RN-SIS-01` |
| `is_active` | `TINYINT(1)` | No | `1` | Desactivar sin borrar (preserva la autoría histórica) |
| `last_login_at` | `TIMESTAMP` | Sí | `NULL` | `[PROPUESTA]` |
| `deleted_at` | `TIMESTAMP` | Sí | `NULL` | `[PROPUESTA]` |

**Roles y permisos:** los provee **Spatie Permission** con sus 5 tablas (`roles`, `permissions`,
`model_has_roles`, `model_has_permissions`, `role_has_permissions`). No se reinventan.

Roles a sembrar, todos documentados:

| Rol | Origen | Alcance |
|-----|--------|---------|
| `admin` | `RN-USR-01`, `RN-USR-03` | Denisse y Michael. Todo. |
| `operator` | `RN-USR-02` | Contenedores y releases, **sin finanzas** |
| `salesperson` | `RN-USR-03`, `RN-COM-09` | Clientes, cotizaciones, ventas |
| `driver` | `RN-USR-03`, `RN-VIA-07` | Panel propio: sus viajes y sus gastos |
| `viewer` | `RN-USR-04` | Solo reportes, sin captura (perfil del dueño) |

> Spatie soporta `team_id` para permisos por compañía. Dado `RN-ORG-01`, **habilítalo desde el
> principio** (`config/permission.php → teams => true`). Añadirlo después obliga a migrar las tablas
> pivote con datos productivos dentro. Es el tipo de decisión que cuesta una tarde ahora y una semana
> en seis meses.

---

## A.4 `employees`

> **Fuente:** `RN-VIA-06` ("no existe ficha de chóferes ni de trabajadores"), `RN-VIA-11`,
> `RN-GAS-06`, `RN-COM-09`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | `RN-ORG-01`. Los chóferes pertenecen a Transporte |
| `user_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `UNIQUE`. Nulo: no todo empleado tiene acceso al sistema |
| `employee_code` | `VARCHAR(20)` | Sí | `NULL` | `UNIQUE`. `[PROPUESTA]` |
| `first_name` | `VARCHAR(80)` | No | — | |
| `last_name` | `VARCHAR(80)` | No | — | |
| `position` | `VARCHAR(40)` | No | — | `driver`\|`salesperson`\|`admin`\|`office`\|`other` — `RN-USR-03`, `RN-GAS-06` |
| `phone` | `VARCHAR(25)` | Sí | `NULL` | |
| `email` | `VARCHAR(150)` | Sí | `NULL` | |
| `hire_date` | `DATE` | Sí | `NULL` | `[PROPUESTA]` — nómina (`RN-GAS-06`) |
| `driver_license_number` | `VARCHAR(40)` | Sí | `NULL` | `[PROPUESTA]` — pendiente del formato de chóferes (§20 #7) |
| `license_expires_on` | `DATE` | Sí | `NULL` | `[PROPUESTA]` |
| `pay_scheme` | `VARCHAR(20)` | Sí | `NULL` | 🔴 `percentage`\|`fixed_per_trip`\|`salary` — **P-7 / A-1 sin resolver** |
| `pay_rate` | `DECIMAL(10,4)` | Sí | `NULL` | Si `percentage` → `0.3000`; si `fixed_per_trip` → `85.00`. `RN-VIA-08` |
| `commission_rate` | `DECIMAL(6,4)` | Sí | `NULL` | Vendedores. `RN-COM-09` |
| `is_active` | `TINYINT(1)` | No | `1` | `RN-USR-05`: alta y baja desde el sistema |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `UNIQUE (user_id)` · `INDEX (company_id, position)` · `INDEX (is_active)`

> `pay_scheme` + `pay_rate` es un par diseñado **precisamente porque A-1 no está resuelto**. Soporta
> las dos lecturas (30 % vs. $85 fijo) sin obligar a decidir ahora, y sin migración cuando el cliente
> responda. Es la forma correcta de tratar una ambigüedad: no adivinar, dejar el hueco tipado.

---

# B. Terceros

## B.1 `customers`

> **Fuente:** `RN-CLI-01` a `RN-CLI-07`, `RN-FRD-03`, `RN-FRD-04`, `RN-FIN-04`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 **P-12 sin resolver.** `NULL` = compartido entre ambas compañías |
| `customer_code` | `VARCHAR(20)` | Sí | `NULL` | `UNIQUE`. `[PROPUESTA]` |
| `type` | `VARCHAR(20)` | No | `'individual'` | `individual` \| `company` — `RN-CLI-05`, `RN-FRD-04` |
| `display_name` | `VARCHAR(150)` | No | — | Nombre de búsqueda. `RN-CLI-05` |
| `first_name` | `VARCHAR(80)` | Sí | `NULL` | |
| `last_name` | `VARCHAR(80)` | Sí | `NULL` | |
| `organization_name` | `VARCHAR(150)` | Sí | `NULL` | 🔴 `RN-CLI-05`: se factura a una organización distinta del contacto |
| `primary_phone` | `VARCHAR(25)` | Sí | `NULL` | 🔴 **Indexado.** `RN-CLI-05`: el dueño busca por teléfono |
| `primary_email` | `VARCHAR(150)` | Sí | `NULL` | |
| `billing_address_line1` | `VARCHAR(150)` | Sí | `NULL` | `RN-CLI-07` |
| `billing_address_line2` | `VARCHAR(150)` | Sí | `NULL` | |
| `billing_city` | `VARCHAR(80)` | Sí | `NULL` | |
| `billing_state` | `CHAR(2)` | Sí | `NULL` | |
| `billing_zip` | `VARCHAR(10)` | Sí | `NULL` | |
| `shipping_address_line1` | `VARCHAR(150)` | Sí | `NULL` | 🔴 `RN-CLI-07`: dirección de shipping separada |
| `shipping_city` | `VARCHAR(80)` | Sí | `NULL` | |
| `shipping_state` | `CHAR(2)` | Sí | `NULL` | |
| `shipping_zip` | `VARCHAR(10)` | Sí | `NULL` | Alimenta el cálculo de millas de `RN-COM-01` |
| `is_tax_exempt` | `TINYINT(1)` | No | `0` | `RN-FIN-04`. Bandera rápida; el certificado vigente manda |
| `sunbiz_verified` | `TINYINT(1)` | No | `0` | 🔴 `RN-FRD-03` |
| `sunbiz_document_number` | `VARCHAR(30)` | Sí | `NULL` | `RN-FRD-03` |
| `sunbiz_verified_at` | `DATE` | Sí | `NULL` | `RN-FRD-03` |
| `credit_card_allowed` | `TINYINT(1)` | No | `0` | 🔴 `RN-FRD-04`: por defecto **NO**. Se habilita tras verificar |
| `credit_card_policy_note` | `VARCHAR(255)` | Sí | `NULL` | Ej. "solo presencial en yarda" — `RN-FRD-04` |
| `source` | `VARCHAR(30)` | Sí | `NULL` | `facebook`\|`referral`\|`phone`\|`walk_in` — `RN-COM-11`. ⚠️ P-14 |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:**
```sql
INDEX (display_name)          -- RN-CLI-05
INDEX (organization_name)     -- RN-CLI-05
INDEX (primary_phone)         -- RN-CLI-05 · petición directa del dueño (R1 §8, acuerdo #6)
INDEX (company_id, type)
FULLTEXT (display_name, organization_name)   -- [PROPUESTA] búsqueda difusa
```

> **Sobre `VARCHAR(25)` para teléfono:** no se usa un tipo numérico. Un teléfono no es un número: no
> se suma, puede llevar `+1`, paréntesis, guiones y extensión, y un cero inicial es significativo.
> `INT` destruiría `+1 (305) 555-0123`. Se guarda como texto y se normaliza en la capa de aplicación
> **antes** de indexar, para que la búsqueda por teléfono de `RN-CLI-05` funcione escriba el usuario
> lo que escriba.

---

## B.2 `customer_contacts`

> **Fuente:** `RN-CLI-06` (varios emails, contactos de contaduría, a veces dos personas),
> `RN-NOT-02` (notificar a **todos** los medios registrados).

Sin esta tabla, `RN-NOT-02` es imposible de cumplir.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `customer_id` | `BIGINT UNSIGNED` | No | — | FK → `customers`, `ON DELETE CASCADE` |
| `kind` | `VARCHAR(10)` | No | — | `phone` \| `email` — `RN-NOT-02` |
| `value` | `VARCHAR(150)` | No | — | El número o correo |
| `label` | `VARCHAR(50)` | Sí | `NULL` | `owner`, `accounting`, `mobile` — `RN-CLI-06` |
| `contact_name` | `VARCHAR(100)` | Sí | `NULL` | `RN-CLI-06`: "dos personas en contaduría" |
| `is_primary` | `TINYINT(1)` | No | `0` | |
| `receives_billing` | `TINYINT(1)` | No | `1` | `RN-FIN-12` |
| `receives_dunning` | `TINYINT(1)` | No | `1` | 🔴 `RN-NOT-02` |
| `is_active` | `TINYINT(1)` | No | `1` | |
| timestamps | | | | |

**Índices:** `UNIQUE (customer_id, kind, value)` · `INDEX (kind, receives_dunning)`

---

## B.3 `tax_exemption_certificates`

> **Fuente:** `RN-FIN-04`, `RN-FIN-05`, `RN-FIN-06` (renovación **anual**), `RN-DOC-02`.

Tabla propia y no un campo en `customers` **porque el certificado vence y se renueva todos los años**.
Un solo campo perdería el histórico y no permitiría saber si en la fecha de una venta pasada el
cliente estaba realmente exento — dato que hace falta ante una auditoría.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `customer_id` | `BIGINT UNSIGNED` | No | — | FK → `customers` |
| `certificate_number` | `VARCHAR(50)` | No | — | `RN-FIN-06`: «es el mismo número» año a año |
| `issued_on` | `DATE` | Sí | `NULL` | |
| `expires_on` | `DATE` | No | — | 🔴 `RN-FIN-06`: cambia cada año |
| `document_id` | `BIGINT UNSIGNED` | Sí | `NULL` | FK → `documents`. `RN-FIN-05` |
| `is_active` | `TINYINT(1)` | No | `1` | |
| `notes` | `VARCHAR(255)` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `INDEX (customer_id, expires_on)` · `INDEX (expires_on)` — alimenta el aviso de
"certificados por vencer".

---

## B.4 `suppliers`

> **Fuente:** `RN-INV-11`, `RN-INV-12` (el campo hoy llamado "cliente" **es** el proveedor),
> `RN-REL-02`, `RN-REL-07`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `name` | `VARCHAR(150)` | No | — | `RN-INV-12` |
| `contact_name` | `VARCHAR(100)` | Sí | `NULL` | |
| `phone` | `VARCHAR(25)` | Sí | `NULL` | |
| `email` | `VARCHAR(150)` | Sí | `NULL` | `RN-REL-08`: se documenta por correo |
| `address_line1` | `VARCHAR(150)` | Sí | `NULL` | |
| `city` | `VARCHAR(80)` | Sí | `NULL` | |
| `state` | `CHAR(2)` | Sí | `NULL` | |
| `zip` | `VARCHAR(10)` | Sí | `NULL` | |
| `default_free_days` | `SMALLINT UNSIGNED` | Sí | `14` | `RN-REL-05` |
| `default_storage_fee_per_day` | `DECIMAL(10,2)` | Sí | `NULL` | 🔴 `RN-REL-07`: «uno cobra 8, otro 6, otro 2» |
| `is_active` | `TINYINT(1)` | No | `1` | |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

> `default_storage_fee_per_day` vive en el proveedor, **no** en `settings`, precisamente por
> `RN-REL-07`: la tarifa es por proveedor. Ponerla como parámetro global sería contradecir una regla
> explícita.

---

## B.5 `depots`

> **Fuente:** `RN-VIA-03` («hay tres depots nada más», fee de recogida **fijo**), `RN-REL-03`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `supplier_id` | `BIGINT UNSIGNED` | Sí | `NULL` | FK → `suppliers` |
| `name` | `VARCHAR(150)` | No | — | |
| `address_line1` | `VARCHAR(150)` | Sí | `NULL` | |
| `city` | `VARCHAR(80)` | Sí | `NULL` | |
| `state` | `CHAR(2)` | Sí | `NULL` | |
| `zip` | `VARCHAR(10)` | Sí | `NULL` | |
| `pickup_flat_fee` | `DECIMAL(10,2)` | Sí | `NULL` | 🔴 `RN-VIA-03`: costo **fijo**, no por millas |
| `is_active` | `TINYINT(1)` | No | `1` | |
| timestamps + `deleted_at` | | | | |

---

# C. Catálogos de contenedor

Las tres son **tablas** y no enums de PHP, por `RN-SIS-03` (terminología estándar y administrable) y
porque el catálogo comercial puede crecer.

## C.1 `container_types`

> **Fuente:** `RN-INV-03` — seco y refrigerado.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `code` | `VARCHAR(20)` | No | — | `UNIQUE`. `DRY`, `REEFER` |
| `name_es` | `VARCHAR(60)` | No | — | "Seco", "Refrigerado" — `RN-SIS-01` |
| `name_en` | `VARCHAR(60)` | No | — | "Dry", "Reefer" |
| `sort_order` | `SMALLINT` | No | `0` | |
| `is_active` | `TINYINT(1)` | No | `1` | |

**Se siembran únicamente `DRY` y `REEFER`.** Otros tipos que existen en el mercado real (open top,
flat rack, high cube) **no fueron mencionados por el cliente** y no se inventan. La tabla permite
añadirlos si aparecen.

## C.2 `container_sizes`

> **Fuente:** `RN-INV-04` — 20, 40, (45), (40 con chassis). ⚠️ **A-2 sin resolver.**

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `code` | `VARCHAR(20)` | No | — | `UNIQUE`. `20`, `40`, `45`, `40_CHASSIS` |
| `length_ft` | `SMALLINT UNSIGNED` | No | — | `20`, `40`, `45` |
| `has_chassis` | `TINYINT(1)` | No | `0` | ⚠️ **A-2**: solución provisional para "40 con chassis" |
| `name_es` / `name_en` | `VARCHAR(60)` | No | — | |
| `sort_order` | `SMALLINT` | No | `0` | |
| `is_active` | `TINYINT(1)` | No | `1` | |

> El chassis es equipo rodante independiente del contenedor. Modelarlo como una "medida" es
> **provisional y probablemente incorrecto**. Si al responder A-2 resulta que se vende/renta aparte,
> hará falta una tabla `equipment` y `has_chassis` pasa a ser una relación. Queda señalado.

## C.3 `container_grades`

> **Fuente:** `RN-INV-05` — tres líneas de producto, cinco grados.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `code` | `VARCHAR(20)` | No | — | `UNIQUE`. `NEW`, `CW`, `AS_IS`, `W4` |
| `name_es` / `name_en` | `VARCHAR(60)` | No | — | |
| `product_line` | `VARCHAR(20)` | No | — | `premium` \| `standard` \| `economy` — `RN-INV-05` |
| `condition` | `VARCHAR(10)` | No | — | `new` \| `used` — `RN-INV-05` |
| `export_capable` | `TINYINT(1)` | No | `0` | `RN-INV-05`: Cargo Worthy es el grado de exportación |
| `sort_order` | `SMALLINT` | No | `0` | |
| `is_active` | `TINYINT(1)` | No | `1` | |

**Semilla exacta según `RN-INV-05`:**

| code | name_es | product_line | condition | export_capable |
|------|---------|--------------|-----------|----------------|
| `NEW` | Nuevo | `premium` | `new` | 1 |
| `CW` | Cargo Worthy | `standard` | `used` | **1** |
| `AS_IS` | AS-IS | `economy` | `used` | 0 |
| `W4` | W4 | `economy` | `used` | 0 |

> `export_capable` deriva de la frase literal *«estándar, toda exportación, cargo worthy, lo mejor
> usado»*. **Que AS-IS y W4 no sirvan para exportar es inferencia mía, no afirmación del cliente.**
> Marcado como `[PROPUESTA]` — confirmar.

---

# D. Compras e inventario

## D.1 `releases`

> **Fuente:** `RN-REL-01` a `RN-REL-10`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | `RN-ORG-01` |
| `supplier_id` | `BIGINT UNSIGNED` | No | — | `RN-REL-02`: «quién lo vendió» |
| `depot_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REL-03`: dónde quedan los no retirados |
| `release_number` | `VARCHAR(50)` | No | — | `RN-REL-01` |
| `issued_on` | `DATE` | No | — | Arranca el conteo de los 14 días |
| `free_days` | `SMALLINT UNSIGNED` | No | `14` | `RN-REL-05` |
| `pickup_deadline` | `DATE` | No | — | `issued_on + free_days`. Se **almacena**, no se calcula al vuelo |
| `deadline_extended_to` | `DATE` | Sí | `NULL` | 🔴 `RN-REL-08`: extensión por culpa del proveedor |
| `extension_reason` | `VARCHAR(255)` | Sí | `NULL` | `RN-REL-08`: rastro documental |
| `storage_fee_per_day` | `DECIMAL(10,2)` | Sí | `NULL` | `RN-REL-07`. Se copia del proveedor y se **congela** |
| `total_quantity` | `INT UNSIGNED` | No | `0` | `RN-REL-02`: cantidad pactada |
| `picked_quantity` | `INT UNSIGNED` | No | `0` | 🔴 `RN-REL-04`: cuántos ya entraron |
| `total_cost` | `DECIMAL(14,2)` | No | `0.00` | `RN-REL-02`: «cuánto costó» |
| `status` | `VARCHAR(20)` | No | `'open'` | `open`\|`partially_picked`\|`closed`\|`expired` |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `UNIQUE (supplier_id, release_number)` · `INDEX (status, pickup_deadline)` — alimenta la
alerta de releases por vencer.

> **Por qué `pickup_deadline` se almacena en lugar de calcularse:** `RN-REL-08` permite extenderlo.
> Un campo calculado no admitiría la extensión, y la fecha efectiva
> (`COALESCE(deadline_extended_to, pickup_deadline)`) es la que gobierna el cobro del fee.
>
> **Por qué `picked_quantity` está desnormalizado:** `RN-REL-04` es una consulta de pantalla
> ("me faltan cinco por recoger") que se ejecuta constantemente. Contar filas de `containers` en cada
> render de Livewire es innecesario. Se mantiene con un observer sobre `Container`.

## D.2 `release_lines`

> **Fuente:** `RN-REL-01` — «un número de release agrupa N contenedores del **mismo tipo y medida**».

Un release puede pactar varias combinaciones tipo/medida/grado; cada una con su cantidad y costo
unitario. Sin esta tabla no se puede saber a qué precio entró cada contenedor de un lote mixto — y sin
eso, `RN-REP-02` (ganancia real) es incalculable.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `release_id` | `BIGINT UNSIGNED` | No | — | FK, `ON DELETE CASCADE` |
| `container_type_id` | `BIGINT UNSIGNED` | No | — | `RN-REL-01` |
| `container_size_id` | `BIGINT UNSIGNED` | No | — | `RN-REL-01` |
| `container_grade_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-INV-05` |
| `quantity` | `INT UNSIGNED` | No | — | |
| `unit_cost` | `DECIMAL(12,2)` | No | — | `RN-INV-07`: mejor precio por volumen |
| `picked_quantity` | `INT UNSIGNED` | No | `0` | `RN-REL-04` |
| timestamps | | | | |

## D.3 `containers`

> **Tabla central del sistema.** Fuente: `RN-INV-01` a `RN-INV-12`, `RN-REL-03`, `RN-REP-02`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | `RN-ORG-01` |
| `number` | `VARCHAR(20)` | No | — | 🔴 `UNIQUE`. `RN-INV-01` («como una cédula»), `RN-INV-02` |
| `container_type_id` | `BIGINT UNSIGNED` | No | — | `RN-INV-03` |
| `container_size_id` | `BIGINT UNSIGNED` | No | — | `RN-INV-04` |
| `container_grade_id` | `BIGINT UNSIGNED` | No | — | `RN-INV-05` |
| `status` | `VARCHAR(30)` | No | `'in_yard'` | 🔴 **P-2 SIN RESOLVER** — ver nota |
| `release_line_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-REL-09`: **nulo** = compra suelta |
| `supplier_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-INV-11`, `RN-INV-12` |
| `purchase_date` | `DATE` | Sí | `NULL` | `RN-INV-11` |
| `purchase_price` | `DECIMAL(12,2)` | Sí | `NULL` | `RN-INV-11` |
| `pickup_cost` | `DECIMAL(12,2)` | No | `0.00` | `RN-INV-11`: traslado hasta la yarda |
| `refurbishment_cost` | `DECIMAL(12,2)` | No | `0.00` | `RN-INV-09`. Denormalizado desde `expenses` |
| `total_cost` | `DECIMAL(12,2)` | No | `0.00` | 🔴 Base de `RN-REP-02`. Ver nota |
| `arrived_at_yard_on` | `DATE` | Sí | `NULL` | `RN-REL-03`: entrada física |
| `sold_on` | `DATE` | Sí | `NULL` | |
| `released_on` | `DATE` | Sí | `NULL` | `RN-COM-07`: salida física de la yarda |
| `yard_location` | `VARCHAR(50)` | Sí | `NULL` | `[PROPUESTA]` — no levantado. Útil para `RN-MIG-03` |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:**
```sql
UNIQUE (number)                      -- RN-INV-01 / RN-INV-02  ⚠️ ver A-6
INDEX  (company_id, status)          -- dashboard: contenedores disponibles (RN-REP-04)
INDEX  (release_line_id)             -- RN-REL-04
INDEX  (container_grade_id, status)  -- reportes por línea de producto (RN-INV-05)
INDEX  (arrived_at_yard_on)
```

> ### 🔴 Nota sobre `status` — el hueco más grande del modelo
>
> `RN-INV-08` documenta que Erik preguntó **tres veces** por los estados del contenedor y Denisse
> respondió siempre por **categoría comercial**. **El catálogo de estados nunca se levantó.**
>
> Los siguientes valores son **`[PROPUESTA]` pura**, derivados de operaciones que sí están
> documentadas. **No los tomes como regla de negocio:**
>
> | Valor | Derivado de |
> |-------|-------------|
> | `at_depot` | `RN-REL-03`: comprado, aún en el depósito del proveedor |
> | `in_yard` | `RN-REL-03`: entró físicamente |
> | `in_refurbishment` | `RN-INV-09`: se está reacondicionando |
> | `available` | `RN-MIG-02`: sin registro de venta ni renta |
> | `reserved` | `[PROPUESTA]` — no documentado |
> | `sold` | `RN-COM-08` |
> | `rented` | `RN-REN-01` |
> | `awaiting_pickup` | R1 §4: vendido, aún en yarda (renta de yarda) |
> | `delivered` | `RN-COM-07` |
>
> **Valídalo con Denisse antes de la carga inicial.** Si el catálogo cambia, cambian el dashboard
> (`RN-REP-04`), la disponibilidad y la conciliación de `RN-MIG-01`.

> ### Nota sobre `total_cost`
>
> `RN-REP-02` señala el problema central: *el sistema de facturación conoce el monto vendido pero no
> en cuánto se compró el contenedor*. `total_cost` es la respuesta:
>
> ```
> total_cost = COALESCE(purchase_price,0) + pickup_cost + refurbishment_cost
> ```
>
> Coincide con el ejemplo de `R1 §2`: compra 600 + arreglos 250 = **850**.
>
> Se guarda **materializado** en lugar de columna generada porque `refurbishment_cost` se alimenta de
> `expenses` mediante un observer, y las columnas generadas de MySQL no pueden depender de otra tabla.

> ### ⚠️ Nota sobre `UNIQUE (number)` — riesgo A-6
>
> `RN-INV-01` dice que el número es la cédula del contenedor. Pero si la empresa **recompra** un
> contenedor que ya vendió, el `UNIQUE` bloquea el registro. El caso no se preguntó (A-6).
>
> Se implementa el `UNIQUE` porque es lo que el cliente describió y porque `RN-INV-02` pide avisar de
> duplicados. Si A-6 se resuelve como "puede volver a entrar", la salida es un `UNIQUE` parcial sobre
> `(number, deleted_at)` o un campo `acquisition_seq`. **Está señalado para no descubrirlo en producción.**

## D.4 `container_status_histories`

> `[PROPUESTA]` — no pedida explícitamente, pero exigida en la práctica por `RN-DOC-03`
> («que todo esté linkado, para cuando yo busque una venta ya tengo todo en un solo lado»)
> y por la desconfianza en el inventario de `RN-MIG-01`.

| Columna | Tipo SQL | Null | Default | Justificación |
|---------|----------|------|---------|---------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `container_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `from_status` | `VARCHAR(30)` | Sí | `NULL` | |
| `to_status` | `VARCHAR(30)` | No | — | |
| `reason` | `VARCHAR(255)` | Sí | `NULL` | |
| `sourceable_type` | `VARCHAR(120)` | Sí | `NULL` | Morfo: qué operación lo movió |
| `sourceable_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `user_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Quién |
| `created_at` | `TIMESTAMP` | Sí | `NULL` | Append-only: **sin** `updated_at` ni `deleted_at` |

**Índices:** `INDEX (container_id, created_at)` · `INDEX (sourceable_type, sourceable_id)`

---

# E. Precios

## E.1 `price_rules`

> **Fuente:** `RN-INV-06` (el precio varía **por temporada**), `RN-INV-07` (volumen),
> `RN-COM-02` (storage ≠ exportación), `RN-REN-12` ⚠️ C-4, y la pregunta abierta #3 de R1.

R1 dejó abierto qué se parametriza y qué se captura libre. Esta tabla permite **ambas**: si existe
regla vigente se sugiere el precio; si no, se captura a mano. Nada obliga a usarla.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | |
| `scope` | `VARCHAR(10)` | No | — | `sale` \| `rent` — ⚠️ C-4 para `rent` |
| `container_type_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `NULL` = aplica a todos |
| `container_size_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REN-12` |
| `container_grade_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-INV-05` |
| `intended_use` | `VARCHAR(20)` | Sí | `NULL` | `storage` \| `export` — 🔴 `RN-COM-02` |
| `min_quantity` | `INT UNSIGNED` | No | `1` | `RN-INV-07` |
| `amount` | `DECIMAL(12,2)` | No | — | |
| `effective_from` | `DATE` | No | — | 🔴 `RN-INV-06`: temporada |
| `effective_to` | `DATE` | Sí | `NULL` | `NULL` = vigente |
| `is_active` | `TINYINT(1)` | No | `1` | |
| `notes` | `VARCHAR(255)` | Sí | `NULL` | |
| timestamps | | | | |

**Índices:** `INDEX (company_id, scope, effective_from, effective_to)` ·
`INDEX (container_size_id, container_grade_id, intended_use)`

> Los precios de renta observados (150 / 192 / 300 — `RN-REN-11`) **no se siembran**. Son
> observaciones de datos históricos, no una tarifa declarada, y C-4 sigue abierta.

---

# F. Comercial

## F.1 `quotes` (presupuestos / estimates)

> **Fuente:** `RN-COM-01`, `RN-COM-02`, `RN-CLI-04` (el cliente queda registrado aunque solo pida
> presupuesto), `RN-FIN-09`. ⚠️ **Sujeta a P-1** (QuickBooks).

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | `RN-ORG-09` |
| `customer_id` | `BIGINT UNSIGNED` | No | — | `RN-CLI-04` |
| `quote_number` | `VARCHAR(30)` | No | — | `UNIQUE (company_id, quote_number)` |
| `status` | `VARCHAR(20)` | No | `'draft'` | `draft`\|`sent`\|`accepted`\|`rejected`\|`expired`\|`converted` |
| `quoted_on` | `DATE` | No | — | |
| `valid_until` | `DATE` | Sí | `NULL` | `RN-INV-06`: el precio cambia por temporada |
| `intended_use` | `VARCHAR(20)` | Sí | `NULL` | 🔴 `storage`\|`export` — `RN-COM-01` paso 4, `RN-COM-02` |
| `delivery_mode` | `VARCHAR(20)` | No | `'customer_pickup'` | `delivery`\|`customer_pickup` — `RN-COM-01` paso 5 |
| `delivery_zip` | `VARCHAR(10)` | Sí | `NULL` | `RN-COM-01` paso 5 |
| `delivery_miles` | `DECIMAL(8,2)` | Sí | `NULL` | `RN-COM-01` paso 6, `RN-VIA-03` |
| `container_amount` | `DECIMAL(12,2)` | No | `0.00` | 🔴 `RN-COM-04`: base imponible |
| `delivery_amount` | `DECIMAL(12,2)` | No | `0.00` | 🔴 `RN-COM-04`: **no** gravado |
| `discount_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-09` |
| `deposit_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-10` |
| `tax_rate` | `DECIMAL(6,4)` | No | `0.0000` | `RN-FIN-01`. Congelada |
| `tax_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-02` |
| `credit_card_fee_rate` | `DECIMAL(6,4)` | Sí | `NULL` | `RN-FIN-07` |
| `credit_card_fee_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-07` |
| `total_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-COM-03`: lo que ve el cliente |
| `salesperson_employee_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-COM-09` |
| `converted_sale_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Trazabilidad presupuesto → venta |
| `quickbooks_id` | `VARCHAR(50)` | Sí | `NULL` | ⚠️ Solo si P-1 = integrar |
| `notes` | `TEXT` | Sí | `NULL` | |
| `created_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

## F.2 `quote_lines`

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `quote_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `line_number` | `SMALLINT UNSIGNED` | No | `1` | |
| `line_type` | `VARCHAR(20)` | No | `'container'` | `container`\|`delivery`\|`fee`\|`discount` |
| `description` | `VARCHAR(255)` | No | — | |
| `container_type_id` / `container_size_id` / `container_grade_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-COM-01` |
| `quantity` | `DECIMAL(10,2)` | No | `1.00` | |
| `unit_price` | `DECIMAL(12,2)` | No | `0.00` | |
| `line_total` | `DECIMAL(12,2)` | No | `0.00` | |
| `is_taxable` | `TINYINT(1)` | No | `1` | 🔴 `RN-FIN-02` / `RN-FIN-03` |
| timestamps | | | | |

## F.3 `sales`

> **Fuente:** `RN-COM-03` a `RN-COM-10`, `RN-FIN-02`, `RN-FIN-04`, `RN-DOC-03`, `RN-REP-02`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | `RN-ORG-06`, `RN-ORG-09` |
| `customer_id` | `BIGINT UNSIGNED` | No | — | |
| `quote_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `sale_number` | `VARCHAR(30)` | No | — | `UNIQUE (company_id, sale_number)` |
| `sold_on` | `DATE` | No | — | |
| `status` | `VARCHAR(20)` | No | `'open'` | `open`\|`invoiced`\|`paid`\|`delivered`\|`closed`\|`cancelled` |
| `intended_use` | `VARCHAR(20)` | No | `'storage'` | 🔴 `storage`\|`export` — `RN-COM-02` |
| **`container_amount`** | `DECIMAL(12,2)` | No | `0.00` | 🔴🔴 `RN-COM-04`: **base del 7 %** |
| **`delivery_amount`** | `DECIMAL(12,2)` | No | `0.00` | 🔴🔴 `RN-COM-04`: ingreso de delivery, **exento** |
| `is_bundled_price` | `TINYINT(1)` | No | `1` | `RN-COM-03`: se presenta junto al cliente |
| `discount_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-09` |
| `deposit_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-10`. ⚠️ A-7 |
| `is_tax_exempt` | `TINYINT(1)` | No | `0` | `RN-FIN-04` |
| `tax_exemption_certificate_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-FIN-05`: certificado **vigente al momento de la venta** |
| `tax_rate` | `DECIMAL(6,4)` | No | `0.0000` | Congelada — §0.4 |
| `tax_amount` | `DECIMAL(12,2)` | No | `0.00` | `= container_amount × tax_rate` (`RN-FIN-02`) |
| `credit_card_fee_rate` | `DECIMAL(6,4)` | Sí | `NULL` | `RN-FIN-07` |
| `credit_card_fee_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-07` |
| `total_amount` | `DECIMAL(12,2)` | No | `0.00` | |
| `delivery_mode` | `VARCHAR(20)` | No | `'customer_pickup'` | `RN-COM-08`, `RN-COM-05` |
| `carrier_type` | `VARCHAR(20)` | Sí | `NULL` | `own_company`\|`external` — ⚠️ **A-3** |
| `carrier_company_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-ORG-02` |
| `carrier_supplier_id` | `BIGINT UNSIGNED` | Sí | `NULL` | ⚠️ A-3: "Ares Transport" |
| `driver_employee_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-COM-10` |
| **`delivery_cost`** | `DECIMAL(12,2)` | No | `0.00` | 🔴 `RN-ORG-08`: lo que **se paga** al transportista. ≠ `delivery_amount` |
| `salesperson_employee_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-COM-09` |
| `commission_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-COM-09`: es **gasto**. ⚠️ P-13 |
| `yard_free_until` | `DATE` | Sí | `NULL` | R1 §4: 2 días de gracia. ⚠️ A-4 |
| `picked_up_on` | `DATE` | Sí | `NULL` | `RN-COM-07`. Cierra la renta de yarda |
| `export_certificate_document_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-COM-02`, `RN-DOC-04` |
| `quickbooks_invoice_id` | `VARCHAR(50)` | Sí | `NULL` | ⚠️ P-1 |
| `notes` | `TEXT` | Sí | `NULL` | |
| `created_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

> ### 🔴 `delivery_amount` vs. `delivery_cost` — no son lo mismo
>
> Son **dos hechos económicos distintos** que R3 separa con claridad y que un modelo ingenuo fundiría
> en un solo campo:
>
> | Campo | Qué es | Fuente |
> |-------|--------|--------|
> | `delivery_amount` | Lo que **cobra al cliente** por el traslado. Va dentro del bound price y **no** lleva impuesto | `RN-COM-04`, `RN-FIN-03` |
> | `delivery_cost` | Lo que la compañía de Contenedores **le paga a Transporte** por ese viaje | `RN-ORG-08`: «Florida ya tiene un gasto de 400 que le tiene que pagar a transporte» |
>
> Fundirlos haría imposible calcular la ganancia real de `RN-REP-01` y descuadrar la conciliación
> semanal de `RN-ORG-07`.

## F.4 `sale_containers`

> Pivote. Una venta puede incluir varios contenedores (`RN-INV-07`: compras y ventas por volumen).

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `sale_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `container_id` | `BIGINT UNSIGNED` | No | — | 🔴 `RN-REP-02`, `RN-DOC-03` |
| `unit_price` | `DECIMAL(12,2)` | No | `0.00` | Precio de ese contenedor |
| `unit_cost_snapshot` | `DECIMAL(12,2)` | No | `0.00` | 🔴 Copia de `containers.total_cost` **al momento de vender** |
| `line_profit` | `DECIMAL(12,2)` | No | `0.00` | `unit_price − unit_cost_snapshot` |
| timestamps | | | | |

**Índices:** `UNIQUE (sale_id, container_id)` · `INDEX (container_id)`

> **Por qué `unit_cost_snapshot` y no leer `containers.total_cost` al vuelo:** si el mes que viene se
> registra un gasto tardío contra ese contenedor, `total_cost` sube y **la ganancia de una venta ya
> cerrada cambiaría retroactivamente**. Los reportes de meses cerrados dejarían de reproducirse. El
> snapshot congela el costo en el instante de la venta. Es el mismo principio que congelar `tax_rate`.

---

# G. Rentas

## G.1 `rentals`

> **Fuente:** `RN-REN-01` a `RN-REN-11`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | `RN-ORG-06` |
| `customer_id` | `BIGINT UNSIGNED` | No | — | |
| `container_id` | `BIGINT UNSIGNED` | No | — | R1 §4: se elige de la lista de disponibles |
| `rental_number` | `VARCHAR(30)` | No | — | `UNIQUE (company_id, rental_number)` |
| `start_date` | `DATE` | No | — | 🔴 `RN-REN-02`: **fecha efectiva del delivery** |
| `billing_day` | `TINYINT UNSIGNED` | No | — | Día del mes derivado de `start_date`. `RN-REN-02` |
| `end_date` | `DATE` | Sí | `NULL` | |
| `monthly_amount` | `DECIMAL(12,2)` | No | — | `RN-REN-11`. ⚠️ C-4 |
| `minimum_months` | `SMALLINT UNSIGNED` | No | `1` | `RN-REN-01` |
| `deposit_amount` | `DECIMAL(12,2)` | No | `0.00` | ⚠️ A-7 |
| `is_tax_exempt` | `TINYINT(1)` | No | `0` | `RN-FIN-04` |
| `tax_rate` | `DECIMAL(6,4)` | No | `0.0000` | `RN-REN-10`: «taxes generados por el contrato» |
| `grace_days` | `SMALLINT UNSIGNED` | No | `5` | 🔴 `RN-REN-04`. Copiado de `settings` y **congelado** |
| `late_fee_amount` | `DECIMAL(10,2)` | No | `100.00` | 🔴 `RN-REN-05`. Congelado |
| `status` | `VARCHAR(20)` | No | `'active'` | `active`\|`finished`\|`cancelled` — `RN-REN-10` |
| `next_due_date` | `DATE` | Sí | `NULL` | `RN-REN-08`: los pagos adelantados lo mueven |
| `paid_through_date` | `DATE` | Sí | `NULL` | 🔴 `RN-REN-10`: «hasta qué mes está pagado» |
| `delivery_trip_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REN-02`: el viaje fija la fecha efectiva |
| `contract_document_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REN-05`: «el contrato lo dice» |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `INDEX (company_id, status)` · `INDEX (status, next_due_date)` — dashboard de morosidad
(`RN-REP-06`) · `INDEX (container_id)`

> `grace_days` y `late_fee_amount` se copian de `settings` y **se congelan en el contrato**. Motivo de
> negocio: `RN-REN-04`/`RN-REN-05` dicen que están **en el contrato firmado**. Si el cliente cambia el
> parámetro global, los contratos vigentes deben seguir rigiéndose por lo que firmaron.

## G.2 `rental_periods`

> **Tabla clave del módulo de rentas.** Fuente: `RN-REN-02`, `RN-REN-03`, `RN-REN-07`, `RN-REN-08`,
> `RN-NOT-03`, `RN-REP-06`.

Materializa cada ciclo mensual como una **fila**. Sin ella, `RN-REN-03` (período explícito en factura)
y el semáforo de `RN-REN-07` habría que calcularlos al vuelo en cada render — inviable con Livewire y
frágil ante pagos adelantados.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `rental_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `period_number` | `INT UNSIGNED` | No | — | 1, 2, 3… |
| **`period_start`** | `DATE` | No | — | 🔴 `RN-REN-03`: "del 2 de agosto…" |
| **`period_end`** | `DATE` | No | — | 🔴 `RN-REN-03`: "…al 2 de septiembre" |
| `amount` | `DECIMAL(12,2)` | No | — | Congelado: `monthly_amount` puede cambiar |
| `tax_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-REN-10` |
| `due_date` | `DATE` | No | — | `RN-REN-02` |
| `grace_until` | `DATE` | No | — | 🔴 `due_date + rentals.grace_days` (`RN-REN-04`) |
| `status` | `VARCHAR(20)` | No | `'pending'` | 🔴 `pending`\|`paid`\|`overdue`\|`waived` — `RN-REN-07` |
| `paid_amount` | `DECIMAL(12,2)` | No | `0.00` | |
| `paid_at` | `DATE` | Sí | `NULL` | |
| `late_fee_amount` | `DECIMAL(10,2)` | No | `0.00` | `RN-REN-05`: $100 fijo |
| `late_fee_waived` | `TINYINT(1)` | No | `0` | 🔴 `RN-REN-06`: el admin puede condonar |
| `late_fee_waived_by` | `BIGINT UNSIGNED` | Sí | `NULL` | Quién condonó — auditoría |
| `late_fee_waived_reason` | `VARCHAR(255)` | Sí | `NULL` | `RN-REN-06` |
| `invoice_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REN-03` |
| `notifications_sent` | `SMALLINT UNSIGNED` | No | `0` | `RN-NOT-06`: control de cadencia |
| `last_notified_at` | `DATE` | Sí | `NULL` | `RN-NOT-05` |
| timestamps | | | | |

**Índices:** `UNIQUE (rental_id, period_number)` · `INDEX (status, due_date)` ·
`INDEX (status, grace_until)` · `INDEX (due_date)`

> ### El semáforo de `RN-REN-07` sale de aquí, sin campo extra
>
> ```php
> // app/Enums/RentalTrafficLight.php
> // 🔴 rojo    : status = pending|overdue  AND  hoy > grace_until
> // 🟡 amarillo: status = pending          AND  hoy > due_date  AND  hoy <= grace_until
> // ⚫ normal  : status = paid|waived      OR   hoy <= due_date
> ```
>
> No se almacena el color: es **derivado**. Guardarlo obligaría a un job que repintara filas cada
> medianoche y quedaría desincronizado cualquier día que el job fallara.
>
> Matiz de `RN-REN-07`: Denisse pidió amarillo **al guardar una renta sin pago**, incluso antes del
> vencimiento («ya me sale amarillo automáticamente»). Ese caso se cubre con
> `status = pending AND paid_amount = 0`, sin depender de la fecha.

## G.3 `yard_storage_charges`

> **Fuente:** R1 §4 y R2 (00:26:58) — 2 días de gracia tras la venta, cobro desde el 3.er día.
> ⚠️ **A-4 / P-8: R3 no lo mencionó y la tarifa diaria nunca se levantó.**

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `sale_id` | `BIGINT UNSIGNED` | No | — | |
| `container_id` | `BIGINT UNSIGNED` | No | — | |
| `free_until` | `DATE` | No | — | `sold_on + 2` (R1 §4) |
| `charged_from` | `DATE` | No | — | 3.er día |
| `charged_to` | `DATE` | Sí | `NULL` | `= sales.picked_up_on` |
| `days_charged` | `INT UNSIGNED` | No | `0` | |
| `daily_rate` | `DECIMAL(10,2)` | Sí | `NULL` | 🔴 **P-8: nunca levantado** |
| `amount` | `DECIMAL(12,2)` | No | `0.00` | |
| `invoice_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `status` | `VARCHAR(20)` | No | `'accruing'` | `accruing`\|`invoiced`\|`waived` |
| timestamps | | | | |

> Tabla creada porque la regla **existe documentada**, con `daily_rate` **nullable**: mientras P-8 no
> se responda, el módulo no puede calcular importes y debe fallar visiblemente. Es deliberado.

---

# H. Transporte

## H.1 `vehicles`

> **Fuente:** `RN-VIA-11` — VIN, placa, tipo, mantenimiento. Denisse tiene el Excel (§20 #6).

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | Pertenecen a Transporte — `RN-ORG-01` |
| `vin` | `CHAR(17)` | Sí | `NULL` | 🔴 `UNIQUE`. `RN-VIA-11`. El VIN es **exactamente** 17 caracteres → `CHAR` |
| `plate_number` | `VARCHAR(15)` | Sí | `NULL` | `RN-VIA-11` |
| `vehicle_type` | `VARCHAR(40)` | Sí | `NULL` | `RN-VIA-11`: «¿qué tipo de vehículos son?» |
| `make` / `model` | `VARCHAR(40)` | Sí | `NULL` | `[PROPUESTA]` |
| `year` | `SMALLINT UNSIGNED` | Sí | `NULL` | `[PROPUESTA]` |
| `is_active` | `TINYINT(1)` | No | `1` | |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

## H.2 `vehicle_maintenances`

> **Fuente:** `RN-VIA-11` — mencionado como necesario, **sin detalle**. Estructura mínima a propósito.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `vehicle_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `performed_on` | `DATE` | No | — | |
| `description` | `VARCHAR(255)` | No | — | |
| `cost` | `DECIMAL(12,2)` | No | `0.00` | `RN-GAS-03`: categoría "vehículos" |
| `odometer` | `INT UNSIGNED` | Sí | `NULL` | `[PROPUESTA]` |
| `expense_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Enlace al gasto |
| timestamps | | | | |

## H.3 `trips` (viajes: delivery y pickup)

> **Fuente:** `RN-VIA-01` a `RN-VIA-10`, `RN-ORG-07`, `RN-ORG-08`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | Normalmente Transporte |
| `trip_number` | `VARCHAR(30)` | No | — | `UNIQUE (company_id, trip_number)` |
| `kind` | `VARCHAR(20)` | No | — | 🔴 `delivery` \| `pickup` — `RN-VIA-03` |
| `trip_date` | `DATE` | No | — | |
| `status` | `VARCHAR(20)` | No | `'scheduled'` | `scheduled`\|`in_progress`\|`completed`\|`cancelled` |
| `sale_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-VIA-04`: el delivery se registra en la venta |
| `rental_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REN-02` |
| `release_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-VIA-04`: el pickup se registra en la compra |
| `container_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Nulo si ⚠️ P-6 = sí (contenedor de tercero) |
| `customer_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `depot_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-VIA-03`: pickup, fee fijo |
| `origin_address` | `VARCHAR(255)` | Sí | `NULL` | |
| `destination_address` | `VARCHAR(255)` | Sí | `NULL` | |
| `destination_zip` | `VARCHAR(10)` | Sí | `NULL` | `RN-COM-01` paso 5 |
| `miles` | `DECIMAL(8,2)` | Sí | `NULL` | 🔴 `RN-VIA-03`: solo delivery |
| `revenue_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-VIA-02`: ingreso propio |
| `vehicle_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-VIA-11` |
| `driver_employee_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-COM-10`, `RN-VIA-06` |
| `driver_pay_scheme` | `VARCHAR(20)` | Sí | `NULL` | 🔴 ⚠️ **A-1 / P-7** |
| `driver_pay_rate` | `DECIMAL(10,4)` | Sí | `NULL` | `0.3000` o monto fijo |
| `driver_pay_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-VIA-09`: se descuenta del ingreso |
| `driver_payment_status` | `VARCHAR(20)` | No | `'pending'` | 🔴 `RN-VIA-09`: «pendiente por pagar» |
| `driver_payout_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-VIA-09`: cierre de los lunes |
| `is_third_party_container` | `TINYINT(1)` | No | `0` | ⚠️ **P-6 sin responder** — `RN-VIA-10` |
| `intercompany_invoice_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-ORG-07`: factura semanal Transporte → Contenedores |
| `notes` | `TEXT` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `INDEX (company_id, trip_date)` · `INDEX (kind, trip_date)` — reporte semanal de
`RN-VIA-05` · `INDEX (driver_employee_id, driver_payment_status)` · `INDEX (intercompany_invoice_id)`

> Los **gastos del viaje** (`RN-VIA-02`: viáticos, gasolina, cauchos, reparaciones) **no** tienen tabla
> propia: son filas de `expenses` con `expensable_type = Trip`. Ver §I.6. Así `RN-GAS-01` y `RN-GAS-02`
> se cumplen en un solo lugar y el reporte de gastos por categoría (`RN-GAS-04`) no tiene que unir
> tres tablas distintas.

## H.4 `driver_payouts`

> **Fuente:** `RN-VIA-09` (pagos los lunes, estatus pendiente), `RN-VIA-05` (reporte semanal).

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | |
| `employee_id` | `BIGINT UNSIGNED` | No | — | |
| `period_start` / `period_end` | `DATE` | No | — | `RN-VIA-05`: semana |
| `trips_count` | `INT UNSIGNED` | No | `0` | `RN-VIA-05` |
| `total_amount` | `DECIMAL(12,2)` | No | `0.00` | |
| `status` | `VARCHAR(20)` | No | `'pending'` | `pending`\|`paid` — `RN-VIA-09` |
| `paid_on` | `DATE` | Sí | `NULL` | `RN-VIA-09`: los lunes |
| `expense_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-GAS-06`: nómina como gasto |
| timestamps | | | | |

**Índices:** `UNIQUE (employee_id, period_start, period_end)` · `INDEX (status)`

---

# I. Finanzas

## I.1 `invoices`

> **Fuente:** `RN-FIN-09` a `RN-FIN-12`, `RN-REN-03`, `RN-ORG-07`, `RN-ORG-09`, `RN-DOC-05`.
> ⚠️ **Sujeta a P-1.**

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | 🔴 `RN-ORG-09`: factura por compañía emisora |
| `invoice_number` | `VARCHAR(30)` | No | — | `UNIQUE (company_id, invoice_number)` |
| `invoice_type` | `VARCHAR(20)` | No | — | `sale`\|`rental`\|`trip`\|`intercompany`\|`other` |
| `customer_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Nulo si es intercompañía |
| `counterparty_company_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-ORG-07`: Transporte factura a Contenedores |
| `invoiceable_type` | `VARCHAR(120)` | Sí | `NULL` | Morfo: `Sale`, `Rental`, `Trip` |
| `invoiceable_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `issue_date` | `DATE` | No | — | |
| `due_date` | `DATE` | Sí | `NULL` | |
| **`period_start`** | `DATE` | Sí | `NULL` | 🔴 `RN-REN-03`: período de renta cubierto |
| **`period_end`** | `DATE` | Sí | `NULL` | 🔴 `RN-REN-03` |
| `subtotal` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-09` |
| **`taxable_base`** | `DECIMAL(12,2)` | No | `0.00` | 🔴 `RN-FIN-02`: **solo el contenedor** |
| `tax_rate` | `DECIMAL(6,4)` | No | `0.0000` | Congelada |
| `tax_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-02` |
| `discount_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-09` |
| `deposit_applied` | `DECIMAL(12,2)` | No | `0.00` | 🔴 `RN-FIN-10`: se **resta** |
| `credit_card_fee_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-07`, `RN-FIN-09` |
| `total_amount` | `DECIMAL(12,2)` | No | `0.00` | |
| `balance_due` | `DECIMAL(12,2)` | No | `0.00` | Dashboard: cuentas por cobrar (`RN-REP-04`) |
| `status` | `VARCHAR(20)` | No | `'draft'` | `draft`\|`sent`\|`partial`\|`paid`\|`overdue`\|`void` |
| `payment_link_url` | `VARCHAR(500)` | Sí | `NULL` | `RN-FIN-08`: Square |
| `pdf_document_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-DOC-05` |
| `quickbooks_id` | `VARCHAR(50)` | Sí | `NULL` | ⚠️ P-1 |
| `quickbooks_sync_token` | `VARCHAR(20)` | Sí | `NULL` | ⚠️ P-1. QBO exige el token en cada update |
| `quickbooks_synced_at` | `TIMESTAMP` | Sí | `NULL` | ⚠️ P-1 |
| `notes` | `TEXT` | Sí | `NULL` | |
| `created_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `UNIQUE (company_id, invoice_number)` · `INDEX (customer_id, issue_date)` — `RN-DOC-05` ·
`INDEX (status, due_date)` · `INDEX (invoiceable_type, invoiceable_id)` ·
`INDEX (quickbooks_id)`

> `taxable_base` es **campo propio y no derivado del total**, por `RN-FIN-02`. Es la única forma de
> que el reporte fiscal de `RN-REP-03` — el que Denisse pidió expresamente — sea auditable: permite
> demostrar sobre qué base se calculó cada centavo de impuesto recaudado.

## I.2 `invoice_lines`

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `invoice_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `line_number` | `SMALLINT UNSIGNED` | No | `1` | |
| `line_type` | `VARCHAR(20)` | No | — | `container`\|`delivery`\|`rent`\|`fee`\|`deposit`\|`discount`\|`late_fee` |
| `description` | `VARCHAR(255)` | No | — | `RN-COM-03`: descripción consolidada |
| `container_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-REP-02`: sin esto no hay ganancia real |
| `quantity` | `DECIMAL(10,2)` | No | `1.00` | |
| `unit_price` | `DECIMAL(12,2)` | No | `0.00` | |
| `line_total` | `DECIMAL(12,2)` | No | `0.00` | |
| **`is_taxable`** | `TINYINT(1)` | No | `1` | 🔴🔴 Ver nota |
| timestamps | | | | |

> ### 🔴 `is_taxable` a nivel de línea — decisión estructural
>
> Es la pieza que hace posible cumplir simultáneamente cuatro reglas que, juntas, **no** se pueden
> resolver con un impuesto de cabecera:
>
> | Regla | Exigencia |
> |-------|-----------|
> | `RN-FIN-02` | El 7 % grava **solo el contenedor** |
> | `RN-FIN-03` | La transportación **nunca** lleva impuesto |
> | `RN-ORG-06` | Transporte **sí** grava cuando vende un contenedor |
> | `RN-FIN-04` | El cliente exento no paga en **ninguna** línea |
>
> ⇒ La condición de gravado **no depende de la compañía ni de la factura**, sino de **qué contiene
> cada línea**. Motor de impuestos:
>
> ```
> taxable_base = Σ line_total  WHERE is_taxable = 1  AND  invoice.customer no exento
> tax_amount   = taxable_base × tax_rate
> total        = subtotal + tax_amount + credit_card_fee − discount − deposit_applied
> ```
>
> Coincide exactamente con `RN-FIN-02`: *«coger solamente el precio del contenedor, aplicarle el 7 % y
> sumarle el costo del delivery»*.

## I.3 `payments`

> **Fuente:** `RN-FIN-07`, `RN-FIN-08`, `RN-FIN-12`, `RN-FIN-13`, `RN-FRD-01`, `RN-FRD-02`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | |
| `customer_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `payment_number` | `VARCHAR(30)` | No | — | `UNIQUE (company_id, payment_number)` |
| `paid_on` | `DATE` | No | — | |
| `amount` | `DECIMAL(12,2)` | No | — | |
| `method` | `VARCHAR(20)` | No | — | `cash`\|`credit_card`\|`check`\|`transfer`\|`zelle`\|`other` — `RN-FIN-13` |
| `gateway` | `VARCHAR(30)` | Sí | `NULL` | `square`\|`paypal` — `RN-FIN-08`. ⚠️ P-11 |
| `gateway_reference` | `VARCHAR(100)` | Sí | `NULL` | ID de la transacción |
| `check_number` | `VARCHAR(30)` | Sí | `NULL` | `RN-FIN-13` |
| `credit_card_fee_amount` | `DECIMAL(12,2)` | No | `0.00` | `RN-FIN-07` |
| `authorization_document_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-FRD-01`, `RN-FRD-02` |
| `is_advance` | `TINYINT(1)` | No | `0` | `RN-REN-08`: pagos adelantados |
| `notes` | `TEXT` | Sí | `NULL` | |
| `created_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

> **Regla de aplicación obligatoria** (`RN-FRD-01`): si `method = 'credit_card'`, el pago **no puede
> registrarse** sin `authorization_document_id`, y `customers.credit_card_allowed` debe ser `1`. Se
> implementa como validación de dominio, no solo en el formulario — es una política que ya le costó
> dinero a la empresa (`RN-FRD-05`).

## I.4 `payment_allocations`

> **Fuente:** `RN-REN-08` (pagos adelantados de varios meses), `RN-REN-09`.

Un pago de 450 puede cubrir tres meses de renta. Sin esta tabla habría que crear tres pagos ficticios
o perder la trazabilidad de qué mes quedó cubierto.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `payment_id` | `BIGINT UNSIGNED` | No | — | FK, `CASCADE` |
| `invoice_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `rental_period_id` | `BIGINT UNSIGNED` | Sí | `NULL` | 🔴 `RN-REN-08` |
| `amount` | `DECIMAL(12,2)` | No | — | |
| timestamps | | | | |

**Índices:** `INDEX (payment_id)` · `INDEX (invoice_id)` · `INDEX (rental_period_id)`

## I.5 `expense_categories`

> **Fuente:** 🔴 `RN-GAS-02` — el cliente pidió **explícitamente** un dropdown administrable.
> Esta tabla existe porque el cliente lo pidió, no por diseño académico.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `parent_id` | `BIGINT UNSIGNED` | Sí | `NULL` | Auto-FK: jerarquía. `RN-GAS-02` |
| `code` | `VARCHAR(30)` | No | — | `UNIQUE` |
| `name_es` / `name_en` | `VARCHAR(80)` | No | — | `RN-SIS-01` |
| `is_system` | `TINYINT(1)` | No | `0` | Protege las que el sistema necesita (ej. `transportation`) |
| `is_active` | `TINYINT(1)` | No | `1` | `RN-GAS-02`: se desactiva, no se borra |
| `sort_order` | `SMALLINT` | No | `0` | |
| timestamps | | | | |

**Semilla — solo categorías nombradas por el cliente** (`RN-GAS-01`, `RN-GAS-03`, `RN-GAS-04`):

| code | name_es | Fuente | `is_system` |
|------|---------|--------|-------------|
| `transportation` | Transportación | `RN-GAS-04` | **1** |
| `yard` | Yarda | `RN-GAS-03` | 0 |
| `vehicles` | Vehículos | `RN-GAS-03` | 0 |
| `fuel` | Combustible | `RN-GAS-03`, `RN-GAS-01` | 0 |
| `container_fee` | Container fee / almacenaje | `RN-REL-06`, `RN-GAS-03` | 0 |
| `materials` | Materiales / insumos | `RN-GAS-03`, `RN-GAS-01` | 0 |
| `payroll` | Nómina / salarios | `RN-GAS-01`, `RN-GAS-03` | 0 |
| `parts` | Repuestos | `RN-GAS-01` | 0 |
| `business_meals` | Almuerzos de negocio | `RN-GAS-01` | 0 |
| `commissions` | Comisiones de vendedor | `RN-COM-09` | 0 |
| `refurbishment` | Reacondicionamiento | `RN-INV-09` | 0 |
| `per_diem` | Viáticos | `RN-VIA-02` | 0 |
| `tires` | Cauchos | `RN-VIA-02` | 0 |

> No se inventan categorías. La lista definitiva la entrega Denisse (§20 #9 / `RN-GAS-05`).

## I.6 `expenses`

> **Fuente:** `RN-GAS-01` a `RN-GAS-06`, `RN-INV-09`, `RN-REL-06`, `RN-VIA-02`, `RN-ORG-08`.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | 🔴 `RN-ORG-08`: los gastos se separan por compañía |
| `expense_category_id` | `BIGINT UNSIGNED` | No | — | `RN-GAS-02` |
| `expense_date` | `DATE` | No | — | |
| `supplier_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REL-06` |
| `description` | `VARCHAR(255)` | No | — | `RN-GAS-01`: tipo **y** descripción |
| `amount` | `DECIMAL(12,2)` | No | — | |
| `payment_method` | `VARCHAR(20)` | Sí | `NULL` | |
| `expensable_type` | `VARCHAR(120)` | Sí | `NULL` | 🔴 Morfo. Ver nota |
| `expensable_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `document_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-REL-06`: factura del proveedor |
| `reference` | `VARCHAR(60)` | Sí | `NULL` | N.º de factura del proveedor |
| `notes` | `TEXT` | Sí | `NULL` | |
| `created_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `INDEX (company_id, expense_date)` — reporte de `RN-REP-03` ·
`INDEX (expense_category_id, expense_date)` — `RN-GAS-04` ·
`INDEX (expensable_type, expensable_id)`

> ### La relación polimórfica `expensable` no es adorno
>
> Resuelve cuatro reglas distintas con **una** tabla:
>
> | `expensable_type` | Regla | Efecto |
> |-------------------|-------|--------|
> | `Container` | `RN-INV-09` | Reacondicionamiento → suma a `containers.refurbishment_cost` |
> | `Release` | `RN-REL-06` | Fee de almacenaje del depósito |
> | `Trip` | `RN-VIA-02` | Gasolina, viáticos, cauchos, reparaciones en ruta |
> | `Vehicle` | `RN-VIA-11` | Mantenimiento |
> | `NULL` | `RN-GAS-01` | Gasto general (nómina, almuerzos) |
>
> Y el reporte de `RN-GAS-04` («materiales, salarios, transportación») sale de **una sola** consulta
> agrupada, sin unir cinco tablas.

---

# J. Gestión documental

## J.1 `documents`

> **Fuente:** 🔴 `RN-DOC-01` a `RN-DOC-05`, `RN-FIN-05`, `RN-FRD-02`, `RN-REN-05`.
> Requisito explícito y repetido de Denisse: *«que todo esté linkado... y evitar el papel»*.

| Columna | Tipo SQL | Null | Default | Regla / Justificación |
|---------|----------|------|---------|----------------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `documentable_type` | `VARCHAR(120)` | Sí | `NULL` | 🔴 Morfo: `Customer`, `Sale`, `Container`, `Invoice`, `Payment`, `Rental`, `Vehicle` |
| `documentable_id` | `BIGINT UNSIGNED` | Sí | `NULL` | `RN-DOC-03` |
| `category` | `VARCHAR(40)` | No | — | Ver catálogo abajo |
| `title` | `VARCHAR(150)` | Sí | `NULL` | |
| `original_name` | `VARCHAR(255)` | No | — | Nombre con que lo subieron |
| `path` | `VARCHAR(500)` | No | — | Ruta en el disco de Laravel |
| `disk` | `VARCHAR(30)` | No | `'local'` | Permite migrar a S3 sin tocar datos |
| `mime_type` | `VARCHAR(100)` | Sí | `NULL` | |
| `size_bytes` | `INT UNSIGNED` | Sí | `NULL` | `RN-FIN-06`: Denisse notó que pesan poco |
| `issued_on` | `DATE` | Sí | `NULL` | |
| `expires_on` | `DATE` | Sí | `NULL` | 🔴 `RN-FIN-06`: renovación anual |
| `uploaded_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `notes` | `VARCHAR(255)` | Sí | `NULL` | |
| timestamps + `deleted_at` | | | | |

**Índices:** `INDEX (documentable_type, documentable_id)` · `INDEX (category, expires_on)` ·
`INDEX (company_id, category)`

**Catálogo de `category` — todas documentadas** (`RN-DOC-02`):

| Valor | Documento | Fuente |
|-------|-----------|--------|
| `export_certificate` | Certificado de exportación (PDF generado) | `RN-COM-02`, `RN-DOC-04` |
| `tax_exemption` | Certificado de exención de impuestos | `RN-FIN-04`, `RN-FIN-06` |
| `cc_authorization` | Credit Card Authorization Form firmado | `RN-FRD-01`, `RN-FRD-02` |
| `invoice_pdf` | Copia de la factura | `RN-DOC-05` |
| `rental_contract` | Contrato de renta | `RN-REN-05` |
| `supplier_invoice` | Factura del proveedor (fees de almacenaje) | `RN-REL-06` |
| `vehicle_document` | Documentación del vehículo | `RN-VIA-11` |
| `receipt` | Comprobante de gasto | `RN-GAS-01` |
| `other` | — | |

---

# K. Notificaciones

## K.1 `notification_rules`

> **Fuente:** 🔴 `RN-NOT-05` — «la frecuencia y el inicio serán administrables desde la configuración».
> ⚠️ C-5: los valores concretos siguen abiertos.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | |
| `event` | `VARCHAR(50)` | No | — | `rent_due`\|`rent_overdue`\|`tax_cert_expiring`\|`release_deadline` |
| `channel` | `VARCHAR(20)` | No | — | `email` \| `sms` — `RN-NOT-02` |
| `start_offset_days` | `SMALLINT` | No | `0` | 🔴 Desde el vencimiento. ⚠️ C-5 |
| `interval_days` | `SMALLINT UNSIGNED` | No | `2` | 🔴 ⚠️ C-5 |
| `end_offset_days` | `SMALLINT` | No | `10` | ⚠️ C-5 |
| `max_notifications` | `SMALLINT UNSIGNED` | Sí | `NULL` | `RN-NOT-06`: «son tres notificaciones» |
| `template_key` | `VARCHAR(50)` | No | — | Plantilla en `resources/lang` |
| `is_active` | `TINYINT(1)` | No | `1` | |
| timestamps | | | | |

**Índices:** `UNIQUE (company_id, event, channel)`

> Los offsets son **`SMALLINT` con signo, no `UNSIGNED`**, a propósito: la propuesta de Ronny
> (`RN-NOT-06`) incluye enviar correo **desde antes** del vencimiento, lo que exige valores negativos.
> Declararlo `UNSIGNED` cerraría esa opción sin que nadie lo hubiera decidido.

## K.2 `notification_logs`

> **Fuente:** `RN-NOT-01`, `RN-NOT-02`. Necesaria para probar que se avisó antes de cobrar el fee de
> `RN-REN-05` — *«no se ha recibido ninguna comunicación»* es la condición contractual del cobro.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `notification_rule_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `customer_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `notifiable_type` / `notifiable_id` | `VARCHAR(120)` / `BIGINT UNSIGNED` | Sí | `NULL` | Morfo: `RentalPeriod` |
| `channel` | `VARCHAR(20)` | No | — | `RN-NOT-02` |
| `recipient` | `VARCHAR(150)` | No | — | Teléfono o correo concretos |
| `subject` | `VARCHAR(200)` | Sí | `NULL` | |
| `body` | `TEXT` | Sí | `NULL` | `RN-NOT-03`: guarda el período notificado |
| `status` | `VARCHAR(20)` | No | `'queued'` | `queued`\|`sent`\|`failed` |
| `sent_at` | `TIMESTAMP` | Sí | `NULL` | |
| `provider_reference` | `VARCHAR(100)` | Sí | `NULL` | |
| `error_message` | `VARCHAR(255)` | Sí | `NULL` | |
| `created_at` | `TIMESTAMP` | Sí | `NULL` | Append-only |

**Índices:** `INDEX (notifiable_type, notifiable_id)` · `INDEX (customer_id, sent_at)` ·
`INDEX (status)`

---

# L. Soporte e integración

## L.1 `import_batches`

> **Fuente:** `RN-SIS-04` (importación desde Excel), `RN-MIG-01` a `RN-MIG-04`.
> Dado que `RN-MIG-01` documenta que **el inventario del Excel no es confiable**, la importación
> necesita bitácora auditable: hay que poder decir qué entró, qué falló y por qué.

| Columna | Tipo SQL | Null | Default | Regla |
|---------|----------|------|---------|-------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | |
| `type` | `VARCHAR(40)` | No | — | `containers`\|`customers`\|`rentals`\|`sales`\|`expenses`\|`vehicles` |
| `original_name` | `VARCHAR(255)` | No | — | |
| `path` | `VARCHAR(500)` | No | — | Se conserva el archivo original |
| `status` | `VARCHAR(20)` | No | `'pending'` | `pending`\|`processing`\|`completed`\|`failed` |
| `total_rows` / `imported_rows` / `failed_rows` | `INT UNSIGNED` | No | `0` | |
| `errors` | `JSON` | Sí | `NULL` | Fila + motivo del rechazo |
| `started_at` / `finished_at` | `TIMESTAMP` | Sí | `NULL` | |
| `created_by` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| timestamps | | | | |

## L.2 `quickbooks_sync_states`

> ⚠️ **Crear solo si P-1 = integrar.** Fuente: `RN-ORG-07` (C-1), R1 §6.

| Columna | Tipo SQL | Null | Default | Justificación |
|---------|----------|------|---------|---------------|
| `id` | `BIGINT UNSIGNED` | No | AI | |
| `company_id` | `BIGINT UNSIGNED` | No | — | El realm de QBO es por compañía |
| `entity_type` | `VARCHAR(40)` | No | — | `Customer`\|`Invoice`\|`Estimate`\|`Payment`\|`Item` |
| `local_id` | `BIGINT UNSIGNED` | Sí | `NULL` | |
| `qbo_id` | `VARCHAR(50)` | No | — | |
| `qbo_sync_token` | `VARCHAR(20)` | Sí | `NULL` | 🔴 QBO lo exige en cada `update` |
| `direction` | `VARCHAR(10)` | No | `'push'` | `push` \| `pull` |
| `status` | `VARCHAR(20)` | No | `'synced'` | `synced`\|`pending`\|`conflict`\|`failed` |
| `last_synced_at` | `TIMESTAMP` | Sí | `NULL` | |
| `last_error` | `VARCHAR(500)` | Sí | `NULL` | |
| `payload` | `JSON` | Sí | `NULL` | Último cuerpo enviado/recibido |
| timestamps | | | | |

**Índices:** `UNIQUE (company_id, entity_type, qbo_id)` · `INDEX (entity_type, local_id)` ·
`INDEX (status)`

## L.3 Bitácora de actividad

Usar **`spatie/laravel-activitylog`** con su migración estándar. No se reinventa.

Justificación de negocio, no técnica: `RN-REN-06` permite al administrador **condonar** el fee de
$100, y `RN-FRD-04` restringe quién puede aceptar tarjetas. Ambas decisiones mueven dinero y necesitan
quedar registradas con autor y momento.

---

## M. Resumen: 38 tablas propias + tablas de terceros

| # | Tabla | Módulo | Reglas que la exigen |
|---|-------|--------|----------------------|
| 1 | `companies` | Núcleo | RN-ORG-01…09 |
| 2 | `settings` | Núcleo | RN-NOT-05, RN-USR-05 |
| 3 | `employees` | Núcleo | RN-VIA-06, RN-GAS-06 |
| 4 | `customers` | Terceros | RN-CLI-01…07 |
| 5 | `customer_contacts` | Terceros | RN-CLI-06, RN-NOT-02 |
| 6 | `tax_exemption_certificates` | Terceros | RN-FIN-04…06 |
| 7 | `suppliers` | Terceros | RN-INV-12, RN-REL-07 |
| 8 | `depots` | Terceros | RN-VIA-03 |
| 9 | `container_types` | Catálogo | RN-INV-03 |
| 10 | `container_sizes` | Catálogo | RN-INV-04 |
| 11 | `container_grades` | Catálogo | RN-INV-05 |
| 12 | `releases` | Compras | RN-REL-01…10 |
| 13 | `release_lines` | Compras | RN-REL-01, RN-REL-04 |
| 14 | `containers` | Inventario | RN-INV-01…12 |
| 15 | `container_status_histories` | Inventario | RN-DOC-03 `[PROPUESTA]` |
| 16 | `price_rules` | Precios | RN-INV-06, RN-COM-02 |
| 17 | `quotes` | Comercial | RN-CLI-04, RN-COM-01 |
| 18 | `quote_lines` | Comercial | RN-COM-04 |
| 19 | `sales` | Comercial | RN-COM-03…10 |
| 20 | `sale_containers` | Comercial | RN-REP-02 |
| 21 | `rentals` | Rentas | RN-REN-01…11 |
| 22 | `rental_periods` | Rentas | RN-REN-03, RN-REN-07 |
| 23 | `yard_storage_charges` | Rentas | R1 §4 ⚠️ A-4 |
| 24 | `vehicles` | Transporte | RN-VIA-11 |
| 25 | `vehicle_maintenances` | Transporte | RN-VIA-11 |
| 26 | `trips` | Transporte | RN-VIA-01…10 |
| 27 | `driver_payouts` | Transporte | RN-VIA-09 |
| 28 | `invoices` | Finanzas | RN-FIN-09…12 |
| 29 | `invoice_lines` | Finanzas | RN-FIN-02, RN-FIN-03 |
| 30 | `payments` | Finanzas | RN-FIN-07, RN-FRD-01 |
| 31 | `payment_allocations` | Finanzas | RN-REN-08 |
| 32 | `expense_categories` | Finanzas | RN-GAS-02 |
| 33 | `expenses` | Finanzas | RN-GAS-01…06 |
| 34 | `documents` | Documental | RN-DOC-01…05 |
| 35 | `notification_rules` | Notificaciones | RN-NOT-05 |
| 36 | `notification_logs` | Notificaciones | RN-NOT-01 |
| 37 | `import_batches` | Soporte | RN-SIS-04 |
| 38 | `quickbooks_sync_states` | Integración | ⚠️ solo si P-1 = integrar |

Más: `users`, `password_reset_tokens`, `sessions`, `cache`, `jobs`, `failed_jobs` (Laravel) ·
5 tablas de **Spatie Permission** · 1 de **Spatie Activitylog**.
