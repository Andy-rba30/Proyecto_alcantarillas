<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-FIN-07, RN-FIN-08, RN-FIN-12, RN-FIN-13, RN-FRD-01, RN-FRD-02
 *
 * REGLA DE DOMINIO OBLIGATORIA (RN-FRD-01 / RN-FRD-04):
 * si method = 'credit_card', el pago NO puede registrarse sin
 * authorization_document_id, y customers.credit_card_allowed debe ser true.
 * Se implementa como validacion de dominio, no solo en el formulario:
 * es una politica que ya le costo dinero a la empresa (RN-FRD-05, chargebacks).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payments', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();
            $table->foreignId('customer_id')->nullable()
                  ->constrained('customers')->nullOnDelete();

            $table->string('payment_number', 30);
            $table->date('paid_on');
            $table->decimal('amount', 12, 2);

            // RN-FIN-13: efectivo, tarjeta, cheque, transferencia, Zelle
            $table->string('method', 20);
            $table->string('gateway', 30)->nullable();          // RN-FIN-08: square. P-11
            $table->string('gateway_reference', 100)->nullable();
            $table->string('check_number', 30)->nullable();

            $table->decimal('credit_card_fee_amount', 12, 2)->default(0);  // RN-FIN-07: 3.5%

            // RN-FRD-01 / RN-FRD-02: el Credit Card Authorization Form firmado
            // se archiva JUNTO con la factura antes de procesar el cobro.
            $table->foreignId('authorization_document_id')->nullable()
                  ->constrained('documents')->nullOnDelete();

            $table->boolean('is_advance')->default(false);   // RN-REN-08: pagos adelantados

            $table->text('notes')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['company_id', 'payment_number']);
            $table->index(['customer_id', 'paid_on']);
            $table->index(['company_id', 'paid_on']);   // RN-REP-03: reporte por rango
            $table->index('method');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payments');
    }
};
