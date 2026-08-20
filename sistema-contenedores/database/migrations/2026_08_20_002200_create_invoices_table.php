<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-FIN-09 .. RN-FIN-12, RN-REN-03, RN-ORG-07, RN-ORG-09, RN-DOC-05
 *
 * Va ANTES que sales y rentals porque rental_periods.invoice_id la referencia.
 * El vinculo hacia la operacion de origen es POLIMORFICO (invoiceable), lo que
 * evita FKs circulares y permite facturar ventas, rentas, viajes e intercompañia
 * con una sola tabla.
 *
 * SUJETA A P-1 (contradiccion C-1: integrar QuickBooks vs. construir facturacion).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('invoices', function (Blueprint $table) {
            $table->id();

            // RN-ORG-09: "son dos invoices" -- la factura pertenece a la compañía emisora
            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            $table->string('invoice_number', 30);
            $table->string('invoice_type', 20); // sale|rental|trip|intercompany|other

            $table->foreignId('customer_id')->nullable()
                  ->constrained('customers')->nullOnDelete();

            // RN-ORG-07: al cierre de semana Transporte factura a Contenedores
            $table->foreignId('counterparty_company_id')->nullable()
                  ->constrained('companies')->nullOnDelete();

            $table->nullableMorphs('invoiceable');  // Sale | Rental | Trip

            $table->date('issue_date');
            $table->date('due_date')->nullable();

            // ====================================================================
            // RN-REN-03 -- REQUISITO OPERATIVO NACIDO DE DISPUTAS REALES
            // "el primero fue del 2 de agosto al 2 de septiembre. Ya el proximo
            //  tiene que ser del 2 de septiembre al 2 de octubre... para que el
            //  cliente siempre sepa este es el periodo que estas pagando"
            // ====================================================================
            $table->date('period_start')->nullable();
            $table->date('period_end')->nullable();

            $table->decimal('subtotal', 12, 2)->default(0);

            // RN-FIN-02: base imponible = SOLO el contenedor.
            // Campo propio y no derivado del total: es lo unico que hace auditable
            // el reporte fiscal que Denisse pidio expresamente (RN-REP-03).
            $table->decimal('taxable_base', 12, 2)->default(0);

            $table->decimal('tax_rate', 6, 4)->default(0);
            $table->decimal('tax_amount', 12, 2)->default(0);

            $table->decimal('discount_amount', 12, 2)->default(0);   // RN-FIN-09
            $table->decimal('deposit_applied', 12, 2)->default(0);   // RN-FIN-10: se RESTA
            $table->decimal('credit_card_fee_amount', 12, 2)->default(0); // RN-FIN-07

            $table->decimal('total_amount', 12, 2)->default(0);
            $table->decimal('balance_due', 12, 2)->default(0);       // dashboard: cuentas por cobrar

            $table->string('status', 20)->default('draft');
            // draft|sent|partial|paid|overdue|void

            $table->string('payment_link_url', 500)->nullable();     // RN-FIN-08: Square

            $table->foreignId('pdf_document_id')->nullable()
                  ->constrained('documents')->nullOnDelete();        // RN-DOC-05

            // Solo si P-1 = integrar. QBO exige el sync token en cada update.
            $table->string('quickbooks_id', 50)->nullable();
            $table->string('quickbooks_sync_token', 20)->nullable();
            $table->timestamp('quickbooks_synced_at')->nullable();

            $table->text('notes')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['company_id', 'invoice_number']);
            $table->index(['customer_id', 'issue_date']);   // RN-DOC-05: facturas por cliente
            $table->index(['status', 'due_date']);
            $table->index('quickbooks_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('invoices');
    }
};
