<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-COM-03 .. RN-COM-10, RN-FIN-02, RN-FIN-04, RN-DOC-03, RN-REP-02, RN-ORG-08
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sales', function (Blueprint $table) {
            $table->id();

            // RN-ORG-06: Transporte tambien puede vender contenedores
            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();
            $table->foreignId('customer_id')->constrained('customers');
            $table->foreignId('quote_id')->nullable()->constrained('quotes')->nullOnDelete();

            $table->string('sale_number', 30);
            $table->date('sold_on');
            $table->string('status', 20)->default('open');
            // open|invoiced|paid|delivered|closed|cancelled

            // RN-COM-02: storage y exportacion tienen precios distintos
            $table->string('intended_use', 20)->default('storage');  // storage | export

            // ====================================================================
            // RN-COM-04: los dos importes SIEMPRE separados en base de datos,
            // aunque al cliente se le presente uno solo (RN-COM-03 "bound price").
            // ====================================================================
            $table->decimal('container_amount', 12, 2)->default(0);  // base del 7%
            $table->decimal('delivery_amount', 12, 2)->default(0);   // INGRESO por delivery, exento
            $table->boolean('is_bundled_price')->default(true);      // RN-COM-03

            $table->decimal('discount_amount', 12, 2)->default(0);
            $table->decimal('deposit_amount', 12, 2)->default(0);    // RN-FIN-10. A-7 abierta

            // RN-FIN-04 / RN-FIN-05: se guarda QUE certificado estaba vigente
            // al momento de la venta, no solo un booleano.
            $table->boolean('is_tax_exempt')->default(false);
            $table->foreignId('tax_exemption_certificate_id')->nullable()
                  ->constrained('tax_exemption_certificates')->nullOnDelete();

            $table->decimal('tax_rate', 6, 4)->default(0);   // congelada
            $table->decimal('tax_amount', 12, 2)->default(0); // = container_amount * tax_rate

            $table->decimal('credit_card_fee_rate', 6, 4)->nullable();
            $table->decimal('credit_card_fee_amount', 12, 2)->default(0);

            $table->decimal('total_amount', 12, 2)->default(0);

            // RN-COM-05 / RN-COM-08: en exportacion el 98-99% NO lleva delivery
            $table->string('delivery_mode', 20)->default('customer_pickup');

            // RN-COM-10 + A-3: el dropdown lista varios transportistas ("Ares Transport"),
            // pero solo se documento una compañía de transporte propia. Se soportan ambos.
            $table->string('carrier_type', 20)->nullable();          // own_company | external
            $table->foreignId('carrier_company_id')->nullable()
                  ->constrained('companies')->nullOnDelete();
            $table->foreignId('carrier_supplier_id')->nullable()
                  ->constrained('suppliers')->nullOnDelete();
            $table->foreignId('driver_employee_id')->nullable()
                  ->constrained('employees')->nullOnDelete();

            // ====================================================================
            // RN-ORG-08: delivery_cost != delivery_amount. Son dos hechos distintos:
            //   delivery_amount = lo que se COBRA al cliente (exento de tax)
            //   delivery_cost   = lo que Contenedores PAGA a Transporte
            // "Florida ya tiene un gasto de 400 que le tiene que pagar a transporte"
            // Fundirlos haria imposible calcular la ganancia real (RN-REP-01)
            // y descuadraria la conciliacion semanal (RN-ORG-07).
            // ====================================================================
            $table->decimal('delivery_cost', 12, 2)->default(0);

            $table->foreignId('salesperson_employee_id')->nullable()
                  ->constrained('employees')->nullOnDelete();
            $table->decimal('commission_amount', 12, 2)->default(0); // RN-COM-09: es GASTO. P-13

            // R1 §4: 2 dias de gracia en yarda; desde el 3ro se cobra. A-4 / P-8 abiertas.
            $table->date('yard_free_until')->nullable();
            $table->date('picked_up_on')->nullable();   // RN-COM-07: cierra la renta de yarda

            // RN-COM-02 / RN-DOC-04: el certificado de exportacion se genera como PDF
            $table->foreignId('export_certificate_document_id')->nullable()
                  ->constrained('documents')->nullOnDelete();

            $table->string('quickbooks_invoice_id', 50)->nullable();  // P-1

            $table->text('notes')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['company_id', 'sale_number']);
            $table->index(['customer_id', 'sold_on']);
            $table->index(['company_id', 'sold_on']);    // RN-REP-03: reporte por rango de fechas
            $table->index('status');
            $table->index('intended_use');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('sales');
    }
};
