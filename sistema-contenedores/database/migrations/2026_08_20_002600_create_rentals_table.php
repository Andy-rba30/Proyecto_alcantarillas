<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-REN-01 .. RN-REN-11
 *
 * Alquiler por mes, minimo un mes, con ciclo anclado a la FECHA EFECTIVA DEL
 * DELIVERY y no al dia 1 del mes calendario (RN-REN-02).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('rentals', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();
            $table->foreignId('customer_id')->constrained('customers');
            $table->foreignId('container_id')->constrained('containers');

            $table->string('rental_number', 30);

            // RN-REN-02: "yo te hago el delivery el dia 2, a partir de ahi empieza
            // todo hasta el 2 del mes que viene"
            $table->date('start_date');
            $table->unsignedTinyInteger('billing_day');   // derivado de start_date
            $table->date('end_date')->nullable();

            $table->decimal('monthly_amount', 12, 2);     // RN-REN-11. C-4 abierta
            $table->unsignedSmallInteger('minimum_months')->default(1);  // RN-REN-01
            $table->decimal('deposit_amount', 12, 2)->default(0);        // A-7 abierta

            $table->boolean('is_tax_exempt')->default(false);
            $table->decimal('tax_rate', 6, 4)->default(0);  // RN-REN-10: taxes del contrato

            // ====================================================================
            // RN-REN-04 / RN-REN-05: se copian de settings y SE CONGELAN AQUI.
            // Motivo de negocio: ambos estan EN EL CONTRATO FIRMADO. Si el cliente
            // cambia el parametro global, los contratos vigentes deben seguir
            // rigiendose por lo que se firmo.
            // ====================================================================
            $table->unsignedSmallInteger('grace_days')->default(5);
            $table->decimal('late_fee_amount', 10, 2)->default(100.00);

            $table->string('status', 20)->default('active'); // active|finished|cancelled

            $table->date('next_due_date')->nullable();     // RN-REN-08: los adelantos lo mueven
            $table->date('paid_through_date')->nullable(); // RN-REN-10: "hasta que mes esta pagado"

            // FK añadida en 003800 (trips aun no existe)
            $table->unsignedBigInteger('delivery_trip_id')->nullable();

            $table->foreignId('contract_document_id')->nullable()
                  ->constrained('documents')->nullOnDelete();   // RN-REN-05: "el contrato lo dice"

            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['company_id', 'rental_number']);
            $table->index(['company_id', 'status']);
            $table->index(['status', 'next_due_date']);   // dashboard de morosidad (RN-REP-06)
            $table->index('container_id');
            $table->index('customer_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rentals');
    }
};
