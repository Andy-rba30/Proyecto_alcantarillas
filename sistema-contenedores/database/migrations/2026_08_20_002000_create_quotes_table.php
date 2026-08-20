<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-CLI-04: "el cliente debe quedar registrado AUNQUE SOLO HAYA SOLICITADO UN PRESUPUESTO"
 * RN-COM-01: secuencia de calificacion (tipo -> tamaño -> condicion -> uso -> delivery)
 * RN-COM-02: storage y exportacion tienen precios distintos
 *
 * SUJETA A P-1: si se decide integrar QuickBooks, los estimados se crean alla
 * y esta tabla solo espeja. Si se decide construir, esta tabla es el origen.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('quotes', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();
            $table->foreignId('customer_id')->constrained('customers');

            $table->string('quote_number', 30);
            $table->string('status', 20)->default('draft');
            // draft|sent|accepted|rejected|expired|converted

            $table->date('quoted_on');
            $table->date('valid_until')->nullable();   // RN-INV-06: el precio cambia por temporada

            // RN-COM-01 paso 4 / RN-COM-02
            $table->string('intended_use', 20)->nullable();       // storage | export

            // RN-COM-01 pasos 5 y 6
            $table->string('delivery_mode', 20)->default('customer_pickup'); // delivery|customer_pickup
            $table->string('delivery_zip', 10)->nullable();
            $table->decimal('delivery_miles', 8, 2)->nullable();  // RN-VIA-03: delivery por millas

            // ====================================================================
            // RN-COM-04 -- LA REGLA MAS DETERMINANTE DEL MODELO DE FACTURACION
            // "coger SOLAMENTE el precio del contenedor, aplicarle el 7% y sumarle
            //  el costo del delivery. El cliente ve solamente el numero final"
            // Aunque al cliente se le da precio consolidado (RN-COM-03), el sistema
            // DEBE guardar los dos importes por separado.
            // ====================================================================
            $table->decimal('container_amount', 12, 2)->default(0);  // base imponible
            $table->decimal('delivery_amount', 12, 2)->default(0);   // NO gravado (RN-FIN-03)

            $table->decimal('discount_amount', 12, 2)->default(0);   // RN-FIN-09
            $table->decimal('deposit_amount', 12, 2)->default(0);    // RN-FIN-10

            // Tasa CONGELADA en la transaccion: si Florida sube el impuesto,
            // los documentos viejos deben seguir mostrando el que se les aplico.
            $table->decimal('tax_rate', 6, 4)->default(0);
            $table->decimal('tax_amount', 12, 2)->default(0);

            $table->decimal('credit_card_fee_rate', 6, 4)->nullable();   // RN-FIN-07
            $table->decimal('credit_card_fee_amount', 12, 2)->default(0);

            $table->decimal('total_amount', 12, 2)->default(0);      // RN-COM-03: lo que ve el cliente

            $table->foreignId('salesperson_employee_id')->nullable()
                  ->constrained('employees')->nullOnDelete();        // RN-COM-09

            // FK añadida en 003800 (sales aun no existe)
            $table->unsignedBigInteger('converted_sale_id')->nullable();

            $table->string('quickbooks_id', 50)->nullable();         // solo si P-1 = integrar

            $table->text('notes')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['company_id', 'quote_number']);
            $table->index(['customer_id', 'quoted_on']);
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('quotes');
    }
};
