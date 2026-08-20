<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-REN-08: "debe permitir pagos adelantados (por ejemplo, tres meses de una vez)
 *             y actualizar la fecha del proximo vencimiento"
 *
 * Un pago de 450 puede cubrir tres meses de renta. Sin esta tabla habria que
 * crear tres pagos ficticios o perder la trazabilidad de que mes quedo cubierto.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payment_allocations', function (Blueprint $table) {
            $table->id();

            $table->foreignId('payment_id')->constrained('payments')->cascadeOnDelete();

            $table->foreignId('invoice_id')->nullable()
                  ->constrained('invoices')->nullOnDelete();
            $table->foreignId('rental_period_id')->nullable()
                  ->constrained('rental_periods')->nullOnDelete();

            $table->decimal('amount', 12, 2);

            $table->timestamps();

            $table->index('invoice_id');
            $table->index('rental_period_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payment_allocations');
    }
};
