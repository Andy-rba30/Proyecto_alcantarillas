<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * "Renta de yarda": cobro por permanencia del contenedor en el patio DESPUES de
 * vendido. 2 dias de gracia; desde el 3ro se cobra el espacio. Se implemento el
 * año pasado porque quedaban contenedores hasta dos semanas sin retirar.
 *   -- R1 §4 y R2 (00:26:58)
 *
 * ADVERTENCIA: R3 NO la menciono, y la TARIFA DIARIA nunca se levanto (A-4 / P-8).
 * Por eso daily_rate es NULLABLE: mientras P-8 no se responda el modulo no puede
 * calcular importes y debe fallar visiblemente. Es deliberado -- prefiero un
 * error ruidoso a un cargo inventado.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('yard_storage_charges', function (Blueprint $table) {
            $table->id();

            $table->foreignId('sale_id')->constrained('sales')->cascadeOnDelete();
            $table->foreignId('container_id')->constrained('containers');

            $table->date('free_until');         // sold_on + 2 dias
            $table->date('charged_from');       // 3er dia
            $table->date('charged_to')->nullable();  // = sales.picked_up_on

            $table->unsignedInteger('days_charged')->default(0);
            $table->decimal('daily_rate', 10, 2)->nullable();   // P-8 SIN RESOLVER
            $table->decimal('amount', 12, 2)->default(0);

            $table->foreignId('invoice_id')->nullable()
                  ->constrained('invoices')->nullOnDelete();

            $table->string('status', 20)->default('accruing'); // accruing|invoiced|waived

            $table->timestamps();

            $table->index(['status', 'charged_from']);
            $table->index('container_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('yard_storage_charges');
    }
};
