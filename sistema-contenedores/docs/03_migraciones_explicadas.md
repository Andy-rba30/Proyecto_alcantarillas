# Las migraciones, explicadas en detalle

38 migraciones en `database/migrations/`. Este documento explica **por qué están en ese orden**, qué
hace cada bloque, y las decisiones que en seis meses te van a parecer arbitrarias si no quedan escritas.

---

## 1. Qué es una migración y por qué importa el orden

Una migración es una clase con dos métodos: `up()` aplica el cambio, `down()` lo revierte. Laravel
guarda en la tabla `migrations` cuáles ya corrieron, y ejecuta las pendientes **en orden alfabético
del nombre de archivo**. Por eso el prefijo `2026_08_20_XXXXXX_` no es decorativo: **es el orden de
ejecución**.

El orden importa por una razón concreta: **una clave foránea no puede apuntar a una tabla que todavía
no existe.** MySQL rechaza el `CREATE TABLE` con error 1215 (*cannot add foreign key constraint*), que
además es notoriamente poco informativo — no te dice qué FK falló.

Numeración usada, en bloques de 100 para poder intercalar después sin renumerar:

| Rango | Bloque | Por qué va ahí |
|-------|--------|----------------|
| `000100–000600` | Núcleo | `companies` primero: casi todas las demás la referencian |
| `000700–001200` | Terceros y catálogos | Clientes, proveedores, catálogos de contenedor |
| `001300–001900` | Inventario y flota | Releases → contenedores. Los contenedores dependen de los catálogos |
| `002000–002500` | Comercial | Cotizaciones → facturas → ventas |
| `002600–002800` | Rentas | Dependen de contenedores y facturas |
| `002900–003000` | Transporte | Los viajes dependen de ventas, rentas y releases |
| `003100–003300` | Finanzas | Pagos y gastos: los que más FKs consumen |
| `003400–003700` | Soporte | Notificaciones, importación, QuickBooks |
| `003800` | FKs diferidas | Cierra los ciclos. Ver §4 |

---

## 2. Anatomía de una migración de este proyecto

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-REL-01 .. RN-REL-10
 *
 * Un "release" es una orden de compra por lote pactada con un proveedor grande.
 * Denisse: "es cuando ya te autorizan a recogerlos".
 */
return new class extends Migration
{
    public function up(): void   { /* ... */ }
    public function down(): void { /* ... */ }
};
```

Tres cosas deliberadas:

**Clase anónima (`return new class extends Migration`).** Es el estilo de Laravel 9+ y el que genera
Laravel 12. Evita colisiones de nombre de clase, que aparecen cuando dos migraciones se llaman parecido
en momentos distintos del proyecto.

**Docblock con los `RN-` que la justifican.** Dentro de seis meses nadie va a recordar por qué
`storage_fee_per_day` está en `suppliers` y no en `settings`. El docblock lo dice y apunta a la regla.
Es la diferencia entre un esquema mantenible y uno que se toca con miedo.

**`down()` siempre implementado.** Aunque en producción casi nunca hagas rollback, `migrate:fresh` lo
usa constantemente en desarrollo y en CI. Una migración sin `down()` correcto rompe el ciclo de tests.

---

## 3. Convenciones aplicadas y su razón

### 3.1 `foreignId()->constrained()`

```php
$table->foreignId('supplier_id')->constrained('suppliers');
```

Equivale a:

```php
$table->unsignedBigInteger('supplier_id');
$table->foreign('supplier_id')->references('id')->on('suppliers');
```

Además de ser más corto, garantiza que el tipo coincida (`BIGINT UNSIGNED`). El error más común al
escribir FKs a mano es declarar la columna como `integer()` mientras el PK es `bigIncrements()`: MySQL
falla con el mismo 1215 opaco.

### 3.2 Política de borrado: `cascadeOnDelete` vs. `nullOnDelete`

No es una preferencia estética; cada elección es una decisión de negocio:

| Política | Cuándo | Ejemplo en este esquema |
|----------|--------|------------------------|
| `cascadeOnDelete()` | El hijo **no tiene sentido** sin el padre | `invoice_lines` → `invoices`, `rental_periods` → `rentals`, `release_lines` → `releases` |
| `nullOnDelete()` | El hijo **sobrevive** perdiendo la referencia | `containers.supplier_id`, `sales.quote_id`, `documents.uploaded_by` |
| Sin acción (`RESTRICT`) | Borrar el padre **debe fallar** | `sales.customer_id`, `containers.container_type_id` |

Ejemplo concreto: `sales.customer_id` va **sin** política, o sea `RESTRICT`. Si alguien intenta borrar
un cliente con ventas, MySQL lo impide. Es lo correcto: `RN-DOC-05` exige que las facturas históricas
del cliente sigan siendo consultables *«puede ser que después de tres meses me diga: mándame el invoice
del mes pasado»*. Un `CASCADE` ahí borraría el historial silenciosamente.

En la práctica casi nunca se llega a ese error, porque todas las tablas maestras usan `softDeletes()` y
el borrado real no ocurre. La FK es la red de seguridad para cuando alguien corra un `DELETE` a mano.

### 3.3 `nullableMorphs()` para relaciones polimórficas

```php
$table->nullableMorphs('expensable');
```

Crea `expensable_type VARCHAR(255)` + `expensable_id BIGINT UNSIGNED` **y su índice compuesto**.

No genera FK — no puede: la columna apunta a tablas distintas según la fila. Ese es exactamente el
motivo por el que resuelve elegantemente los ciclos de dependencia (§4).

Se usa en cuatro sitios, y en cada uno resuelve una regla real:

| Tabla | Morfo | Reglas que resuelve |
|-------|-------|--------------------|
| `expenses` | `expensable` | `RN-INV-09` (reacondicionamiento), `RN-REL-06` (almacenaje), `RN-VIA-02` (gastos de viaje), `RN-VIA-11` (mantenimiento) |
| `documents` | `documentable` | `RN-DOC-03`: certificados y facturas colgando de cliente, venta, contenedor… |
| `invoices` | `invoiceable` | Facturar ventas, rentas, viajes e intercompañía con una sola tabla |
| `notification_logs` | `notifiable` | Bitácora de avisos por período de renta |

> **Advertencia sobre `nullableMorphs()`:** el `_type` guarda el nombre completo de la clase
> (`App\Models\Container`). Si renombras o mueves el modelo, los datos existentes quedan huérfanos.
> Se resuelve con `Relation::enforceMorphMap()` en `AppServiceProvider`, mapeando alias cortos
> (`'container' => Container::class`). **Hazlo antes de la carga inicial**, no después.

### 3.4 Longitudes de `VARCHAR` deliberadas

Nada quedó en el `255` por defecto sin pensarlo. Ejemplos con su razón:

| Columna | Tipo | Por qué |
|---------|------|---------|
| `vehicles.vin` | `CHAR(17)` | El VIN tiene **exactamente** 17 caracteres (ISO 3779). `CHAR` documenta la invariante y es marginalmente más rápido |
| `companies.state` | `CHAR(2)` | Estado de EE. UU.: siempre 2 letras |
| `customers.billing_zip` | `VARCHAR(10)` | ZIP+4 = `33101-1234` = 10 caracteres |
| `customers.primary_phone` | `VARCHAR(25)` | `+1 (305) 555-0123 ext 42` cabe |
| `containers.number` | `VARCHAR(20)` | ISO 6346 usa 11 (`ABCU1234567`); 20 da margen para números no estándar de contenedores usados |
| `invoices.payment_link_url` | `VARCHAR(500)` | Las URLs de Square con parámetros pasan de 255 |

En MySQL con `utf8mb4`, un índice sobre `VARCHAR(255)` consume 1020 bytes y roza el límite de 3072 del
formato `DYNAMIC` cuando se combina en índices compuestos. Dimensionar bien no es purismo: evita
`ERROR 1071 (Specified key was too long)`.

### 3.5 Índices: solo los que responden a una consulta real

Cada índice acelera lecturas y **encarece escrituras**. Se declararon solo los que sirven a una pantalla
o reporte documentado:

| Índice | Consulta que sirve | Regla |
|--------|-------------------|-------|
| `customers(primary_phone)` | Buscar cliente por teléfono | `RN-CLI-05` — petición directa del dueño |
| `rental_periods(status, grace_until)` | Semáforo rojo | `RN-REN-07` |
| `rental_periods(status, due_date)` | Listado de morosos por día y mes | `RN-REP-06` |
| `containers(company_id, status)` | Contenedores disponibles en el dashboard | `RN-REP-04` |
| `releases(status, pickup_deadline)` | Releases por vencer los 14 días | `RN-REL-05` |
| `invoice_lines(invoice_id, is_taxable)` | Cálculo de `taxable_base` | `RN-FIN-02` |
| `expenses(expense_category_id, expense_date)` | Reporte de gastos por categoría | `RN-GAS-04` |
| `documents(category, expires_on)` | Certificados de exención por vencer | `RN-FIN-06` |
| `trips(kind, trip_date)` | Reporte semanal de deliveries y pickups | `RN-VIA-05` |

**Índices con nombre explícito.** MySQL limita los identificadores a 64 caracteres. Un índice compuesto
de cuatro columnas genera un nombre automático que puede pasarse:

```php
// Falla: el nombre autogenerado excede 64 caracteres
$table->index(['company_id', 'scope', 'effective_from', 'effective_to']);

// Correcto:
$table->index(['company_id', 'scope', 'effective_from', 'effective_to'], 'price_rules_lookup_idx');
```

Aplicado en `price_rules`, `driver_payouts` y `quickbooks_sync_states`.

---

## 4. Dependencias circulares y la migración `003800`

### El problema

Cuatro pares de tablas se referencian mutuamente. **No existe orden de creación que satisfaga a los dos
lados a la vez:**

```
quotes.converted_sale_id  ──►  sales
sales.quote_id            ──►  quotes          ← ciclo

rentals.delivery_trip_id  ──►  trips
trips.rental_id           ──►  rentals         ← ciclo

trips.driver_payout_id    ──►  driver_payouts
driver_payouts (cierre semanal de trips)       ← ciclo

driver_payouts.expense_id ──►  expenses
vehicle_maintenances.expense_id ──► expenses   (expenses va casi al final)
```

### Tres soluciones posibles

| Opción | Veredicto |
|--------|-----------|
| Renunciar a la FK y dejar la columna suelta | ❌ Pierdes integridad referencial. Terminas con `delivery_trip_id = 9999` apuntando a nada |
| `Schema::disableForeignKeyConstraints()` | ❌ Oculta el problema y no es portable |
| **Crear la columna sin constraint, añadir la FK después** | ✅ La estándar |

### Cómo está implementado

En la migración original, la columna se declara **sin** `constrained()`:

```php
// 002600_create_rentals_table.php
$table->unsignedBigInteger('delivery_trip_id')->nullable();
// FK añadida en 003800 (trips aun no existe)
```

Y al final, una migración cierra todos los ciclos de golpe:

```php
// 003800_add_deferred_foreign_keys.php
Schema::table('rentals', function (Blueprint $table) {
    $table->foreign('delivery_trip_id')
          ->references('id')->on('trips')->nullOnDelete();
});
```

**El `down()` las suelta en orden inverso.** Sin eso, `migrate:rollback` fallaría al intentar borrar una
tabla que aún tiene FKs apuntándole.

> **Por qué `nullOnDelete()` en todas:** si se borra la venta, el presupuesto debe sobrevivir sin
> referencia colgante. Coherente con `RN-CLI-04`: *«el cliente debe quedar registrado aunque solo haya
> solicitado un presupuesto»*.

### Los ciclos que **no** existen gracias a los morfos

`invoices` podría haber generado tres ciclos más (con `sales`, `rentals` y `trips`). No los genera
porque usa `invoiceable` polimórfico, que no crea constraint. Por eso `invoices` puede ir en `002200`,
antes que las tres, y `rental_periods.invoice_id` funciona sin diferir nada.

Es un beneficio secundario de una decisión que se tomó por modelo de negocio (`RN-ORG-07`: hay que
facturar cuatro cosas distintas), no por conveniencia técnica. Cuando ambas cosas coinciden, suele ser
señal de que el modelo está bien planteado.

---

## 5. Recorrido bloque por bloque

### Bloque 1 · Núcleo (`000100`–`000600`)

| # | Migración | Nota |
|---|-----------|------|
| `000100` | `create_companies_table` | **Primera obligatoriamente.** `RN-ORG-01`: son dos compañías |
| `000200` | `create_settings_table` | `RN-NOT-05`: parámetros editables por el cliente |
| `000300` | `add_business_fields_to_users_table` | **Extiende**, no reemplaza, la tabla de Laravel |
| `000400` | `create_documents_table` | Va temprano: muchas tablas la referencian; ella no referencia a nadie (usa morfo) |
| `000500` | `create_employees_table` | `RN-VIA-06`: hoy no existe ficha de chóferes |
| `000600` | `create_expense_categories_table` | `RN-GAS-02`: el cliente pidió el dropdown administrable |

> **Sobre `000300`:** se extiende `users` con `Schema::table()` en lugar de editar la migración original
> de Laravel. Si editaras la original, cualquiera que ya hubiera corrido `migrate` no vería los cambios
> —Laravel no reejecuta migraciones ya aplicadas— y tendrías un esquema distinto en cada máquina.

### Bloque 2 · Terceros y catálogos (`000700`–`001200`)

`001200_create_container_catalog_tables` crea **tres tablas en una sola migración**
(`container_types`, `container_sizes`, `container_grades`). Es una excepción deliberada a
"una tabla por migración": son catálogos pequeños, del mismo dominio, que siempre se crean y borran
juntos. El `down()` las suelta en orden inverso.

### Bloque 3 · Inventario y flota (`001300`–`001900`)

Orden crítico: `releases` → `release_lines` → `containers`. Un contenedor apunta a `release_line_id`
para saber a qué precio unitario entró (`RN-REP-02`), y ese campo es **nullable** por `RN-REL-09`:
*«esa restricción ya se eliminó para permitir compras sueltas a proveedores pequeños»*.

### Bloque 4 · Comercial (`002000`–`002500`)

Orden: `quotes` → `quote_lines` → **`invoices`** → `invoice_lines` → `sales` → `sale_containers`.

`invoices` va **antes** que `sales`, que es contraintuitivo. La razón es que `rental_periods.invoice_id`
(bloque 5) la necesita, y `invoices` no depende de `sales` gracias al morfo `invoiceable`.

### Bloque 5 · Rentas (`002600`–`002800`)

`rental_periods` es donde vive la inteligencia del módulo. Materializar cada ciclo como fila permite:

- `RN-REN-03`: el período explícito de la factura sale de `period_start`/`period_end`
- `RN-REN-07`: el semáforo se calcula comparando `hoy` contra `due_date` y `grace_until`
- `RN-REN-08`: un pago adelantado marca tres filas como `paid` vía `payment_allocations`
- `RN-REN-06`: la condonación queda auditada con `late_fee_waived_by` y motivo

### Bloque 6 · Transporte (`002900`–`003000`)

`trips` es la tabla con más FKs del esquema (11). Va tarde porque referencia ventas, rentas, releases,
facturas, empleados, vehículos y depósitos.

### Bloque 7 · Finanzas (`003100`–`003300`)

`expenses` va casi al final porque su morfo `expensable` puede apuntar a contenedores, releases, viajes
y vehículos: todos deben existir para que los datos tengan sentido (aunque el morfo no cree FK).

### Bloque 8 · Soporte (`003400`–`003700`)

`003700_create_quickbooks_sync_states` **está condicionada a P-1**. Si el cliente decide construir la
facturación en el sistema, esta migración no debe correrse. Está aislada al final precisamente para
poder omitirla sin tocar nada más.

---

## 6. Ejecución

```bash
# Primera vez
php artisan migrate

# Con las semillas de catálogo, configuración y roles
php artisan migrate --seed

# Reconstruir desde cero (SOLO en desarrollo: borra todos los datos)
php artisan migrate:fresh --seed

# Ver qué corrió y qué falta
php artisan migrate:status

# Simular sin ejecutar: imprime el SQL
php artisan migrate --pretend
```

`migrate --pretend` es el que más vale la pena antes de tocar producción: te muestra el SQL exacto sin
aplicarlo.

### Dependencias previas

```bash
composer require spatie/laravel-permission
composer require spatie/laravel-activitylog

php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"
php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-migrations"
```

🔴 **Antes de correr `migrate`**, en `config/permission.php`:

```php
'teams' => true,   // RN-ORG-01: permisos por compañía
```

Habilitarlo después obliga a migrar las tablas pivote con datos productivos dentro.

### Registrar los seeders

```php
// database/seeders/DatabaseSeeder.php
public function run(): void
{
    $this->call([
        BusinessCatalogSeeder::class,   // tipos, medidas, grados, categorías de gasto
        SettingsSeeder::class,          // parámetros con su trazabilidad
        RolesAndPermissionsSeeder::class,
    ]);
}
```

---

## 7. Errores frecuentes y cómo se evitaron aquí

| Error | Causa | Prevención aplicada |
|-------|-------|--------------------|
| `1215 Cannot add foreign key constraint` | Tabla destino no existe, o tipos distintos | Orden por bloques + `foreignId()->constrained()` + migración `003800` |
| `1071 Specified key was too long` | Índice sobre `VARCHAR(255)` con `utf8mb4` | Longitudes dimensionadas por caso |
| `Identifier name is too long` | Nombre de índice autogenerado > 64 chars | Nombres explícitos en índices de 3+ columnas |
| Descuadre de centavos en reportes | `FLOAT` para dinero | `DECIMAL(12,2)` en todo importe |
| `migrate:rollback` falla | `down()` incompleto o en mal orden | Todos implementados; `003800` suelta en orden inverso |
| Ganancia histórica que cambia sola | Leer el costo actual del contenedor | `sale_containers.unit_cost_snapshot` |
| Facturas viejas con el impuesto nuevo | Leer la tasa de `settings` al renderizar | `tax_rate` congelada en cada documento |
| Morfos huérfanos tras renombrar un modelo | `_type` guarda el FQCN | `Relation::enforceMorphMap()` — **pendiente de implementar** |

---

## 8. Lo que estas migraciones **no** resuelven

Ser explícito sobre esto vale más que una lista de features:

1. **`containers.status` es una propuesta, no una regla** (P-2 / `RN-INV-08`). El catálogo de estados
   nunca se levantó. Si cambia, cambian el dashboard, la disponibilidad y la conciliación de inventario.

2. **El módulo de facturación depende de P-1.** Si se integra QuickBooks, `quotes` e `invoices` pasan a
   ser espejos de solo lectura y sobran varios campos. Si se construye, son el origen del dato.
   Ver `04_quickbooks_vs_facturacion_propia.md`.

3. **`yard_storage_charges` no puede calcular nada** hasta que se responda P-8 (tarifa diaria). Está
   creada porque la regla existe documentada, con `daily_rate` nullable a propósito.

4. **El pago al chofer admite dos esquemas** (A-1 / P-7) porque las fuentes se contradicen. El par
   `pay_scheme` + `pay_rate` evita tener que migrar cuando el cliente responda, pero **no sustituye la
   respuesta**.

5. **No hay tabla de nómina completa.** `RN-GAS-06` la menciona como aceptada, pero no se levantó
   ninguna regla: ni periodicidad, ni conceptos, ni retenciones. Modelarla ahora sería inventar.

6. **Falta el modelo de leads** (`RN-COM-12` / P-14). Se pregunta desde R1 y sigue sin respuesta.

---

## 9. Antes de la primera carga de datos

En este orden:

- [ ] **P-2**: validar el catálogo de estados de contenedor con Denisse
- [ ] **P-3**: confirmar que el conteo físico se hizo y obtener el inventario real (`RN-MIG-04`)
- [ ] **P-1**: decidir QuickBooks vs. facturación propia (define si corre `003700`)
- [ ] **P-9**: confirmar 7 % y 3.5 % como valores exactos
- [ ] Recibir los diagramas de Visio de Denisse (§20 #1) — puede alterar el modelo de operaciones
- [ ] Recibir ejemplos de factura de ambas compañías (§20 #2) — define `invoice_lines`
- [ ] Implementar `Relation::enforceMorphMap()` antes de que existan datos polimórficos
- [ ] Poner `'teams' => true` en `config/permission.php`

Los tres primeros son **bloqueantes**. Los demás se pueden trabajar en paralelo.
