<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-VIA-09: "los pagos se hacen los lunes" + estatus "pendiente por pagar"
 * RN-VIA-05: reporte semanal ("se hicieron siete recogidas, 11 deliveries, total tanto")
 * RN-GAS-06: la nomina es un gasto que reduce la ganancia real
 *
 * expense_id se enlaza en 003800 (FK diferida).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('driver_payouts', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();
            $table->foreignId('employee_id')->constrained('employees');

            $table->date('period_start');   // RN-VIA-05: semana
            $table->date('period_end');

            $table->unsignedInteger('trips_count')->default(0);
            $table->decimal('total_amount', 12, 2)->default(0);

            $table->string('status', 20)->default('pending');  // pending | paid
            $table->date('paid_on')->nullable();               // RN-VIA-09: los lunes

            $table->unsignedBigInteger('expense_id')->nullable();

            $table->timestamps();

            $table->unique(['employee_id', 'period_start', 'period_end'], 'driver_payouts_period_unq');
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('driver_payouts');
    }
};
