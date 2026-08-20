<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-VIA-01 .. RN-VIA-11, RN-ORG-07, RN-ORG-08
 *
 * La hoja "Viajes" existe pero NO se usa; el cliente quiere empezar a usarla (RN-VIA-01).
 *
 * RN-VIA-03: delivery y pickup tienen COSTEO DISTINTO --
 *   delivery = variable por millas
 *   pickup   = fijo, asociado al deposito ("hay tres depots nada mas")
 *
 * Los GASTOS del viaje (viaticos, gasolina, cauchos, reparaciones -- RN-VIA-02)
 * NO tienen tabla propia: son filas de `expenses` con expensable_type = Trip.
 * Asi RN-GAS-01/RN-GAS-02 se cumplen en un solo lugar y el reporte por categoria
 * (RN-GAS-04) no tiene que unir tres tablas.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('trips', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            $table->string('trip_number', 30);
            $table->string('kind', 20);          // RN-VIA-03: delivery | pickup
            $table->date('trip_date');
            $table->string('status', 20)->default('scheduled');
            // scheduled|in_progress|completed|cancelled

            // RN-VIA-04: "el pickup esta en la compra y el delivery esta en la venta"
            $table->foreignId('sale_id')->nullable()->constrained('sales')->nullOnDelete();
            $table->foreignId('rental_id')->nullable()->constrained('rentals')->nullOnDelete();
            $table->foreignId('release_id')->nullable()->constrained('releases')->nullOnDelete();

            // Nullable por P-6: si hacen delivery de contenedores de TERCEROS,
            // no habra container_id propio. La pregunta sigue sin responder.
            $table->foreignId('container_id')->nullable()
                  ->constrained('containers')->nullOnDelete();

            $table->foreignId('customer_id')->nullable()
                  ->constrained('customers')->nullOnDelete();

            // RN-VIA-03: pickup desde uno de los tres depots, fee fijo
            $table->foreignId('depot_id')->nullable()->constrained('depots')->nullOnDelete();

            $table->string('origin_address', 255)->nullable();
            $table->string('destination_address', 255)->nullable();
            $table->string('destination_zip', 10)->nullable();   // RN-COM-01 paso 5

            $table->decimal('miles', 8, 2)->nullable();          // RN-VIA-03: solo delivery

            $table->decimal('revenue_amount', 12, 2)->default(0); // RN-VIA-02: ingreso propio

            $table->foreignId('vehicle_id')->nullable()->constrained('vehicles')->nullOnDelete();
            $table->foreignId('driver_employee_id')->nullable()
                  ->constrained('employees')->nullOnDelete();

            // A-1 / P-7 SIN RESOLVER: R1 dice "85 de 280" (fijo negociado),
            // R3 dice "el 30% de los 400" (porcentaje). El trio scheme/rate/amount
            // soporta ambas lecturas sin migracion posterior.
            $table->string('driver_pay_scheme', 20)->nullable();
            $table->decimal('driver_pay_rate', 10, 4)->nullable();
            $table->decimal('driver_pay_amount', 12, 2)->default(0);

            // RN-VIA-09: "los pagos se hacen los lunes, por lo que el sistema debe
            // manejar el estatus de pendiente por pagar"
            $table->string('driver_payment_status', 20)->default('pending'); // pending|paid

            // FK añadida en 003800 (driver_payouts aun no existe)
            $table->unsignedBigInteger('driver_payout_id')->nullable();

            // RN-VIA-10 / P-6 SIN RESPONDER
            $table->boolean('is_third_party_container')->default(false);

            // RN-ORG-07: al cierre de semana Transporte factura a Contenedores
            $table->foreignId('intercompany_invoice_id')->nullable()
                  ->constrained('invoices')->nullOnDelete();

            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['company_id', 'trip_number']);
            $table->index(['kind', 'trip_date']);   // RN-VIA-05: reporte semanal
            $table->index(['company_id', 'trip_date']);
            $table->index(['driver_employee_id', 'driver_payment_status']);
            $table->index('intercompany_invoice_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('trips');
    }
};
