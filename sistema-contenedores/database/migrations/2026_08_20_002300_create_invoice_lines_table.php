<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * ====================================================================
 * is_taxable A NIVEL DE LINEA -- DECISION ESTRUCTURAL DEL MODELO
 *
 * Es la unica forma de cumplir SIMULTANEAMENTE cuatro reglas que, juntas,
 * no se pueden resolver con un impuesto de cabecera:
 *
 *   RN-FIN-02  el 7% grava SOLO el contenedor
 *   RN-FIN-03  la transportacion NUNCA lleva impuesto
 *   RN-ORG-06  Transporte SI grava cuando vende un contenedor
 *   RN-FIN-04  el cliente exento no paga en NINGUNA linea
 *
 * => La condicion de gravado no depende de la compañía ni de la factura,
 *    sino de QUE CONTIENE CADA LINEA.
 *
 *   taxable_base = SUM(line_total) WHERE is_taxable = 1 AND cliente no exento
 *   tax_amount   = taxable_base * tax_rate
 *   total        = subtotal + tax_amount + credit_card_fee - discount - deposit
 * ====================================================================
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('invoice_lines', function (Blueprint $table) {
            $table->id();

            $table->foreignId('invoice_id')->constrained('invoices')->cascadeOnDelete();

            $table->unsignedSmallInteger('line_number')->default(1);

            // container|delivery|rent|fee|deposit|discount|late_fee
            $table->string('line_type', 20);

            $table->string('description', 255);   // RN-COM-03: descripcion consolidada

            // RN-REP-02: sin vincular el contenedor no hay ganancia real.
            // "QuickBooks entrega el monto facturado pero desconoce en cuanto se
            //  compro el contenedor" (R1 §6)
            $table->foreignId('container_id')->nullable()
                  ->constrained('containers')->nullOnDelete();

            $table->decimal('quantity', 10, 2)->default(1);
            $table->decimal('unit_price', 12, 2)->default(0);
            $table->decimal('line_total', 12, 2)->default(0);

            $table->boolean('is_taxable')->default(true);

            $table->timestamps();

            $table->index('invoice_id');
            $table->index('container_id');
            $table->index(['invoice_id', 'is_taxable']);   // calculo de taxable_base
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('invoice_lines');
    }
};
