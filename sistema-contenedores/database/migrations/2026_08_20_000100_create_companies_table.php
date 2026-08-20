<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-ORG-01 .. RN-ORG-09
 *
 * El negocio son DOS compañías: una de contenedores ("Florida") y una de transporte.
 * Tributan distinto (RN-ORG-03 / RN-ORG-04) y se facturan entre sí (RN-ORG-07).
 * Esta tabla debe existir ANTES que cualquier otra: casi todas llevan company_id.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('companies', function (Blueprint $table) {
            $table->id();

            $table->string('name', 150);
            $table->string('legal_name', 200)->nullable();   // [PROPUESTA] pendiente de ejemplos de factura
            $table->string('tax_id', 30)->nullable();        // [PROPUESTA] EIN

            // RN-ORG-01: 'containers' | 'transport'
            $table->string('kind', 20);

            // RN-ORG-03 / RN-ORG-04. OJO: es solo el DEFAULT.
            // RN-ORG-06: transporte tambien puede vender contenedores y entonces SI grava.
            // La decision real de gravar vive en invoice_lines.is_taxable.
            $table->boolean('collects_sales_tax')->default(false);

            // RN-FIN-01 (7%) y RN-FIN-07 (3.5%). Ambos sujetos a P-9.
            $table->decimal('default_tax_rate', 6, 4)->nullable();
            $table->decimal('credit_card_fee_rate', 6, 4)->nullable();

            $table->string('address_line1', 150)->nullable();
            $table->string('city', 80)->nullable();
            $table->char('state', 2)->nullable();            // estado de EE.UU.: exactamente 2 chars
            $table->string('zip', 10)->nullable();           // ZIP+4 = 33101-1234
            $table->string('phone', 25)->nullable();
            $table->string('email', 150)->nullable();

            $table->string('logo_path', 500)->nullable();
            $table->string('invoice_prefix', 10)->nullable(); // RN-ORG-09: facturas separadas

            $table->boolean('is_active')->default(true);

            $table->timestamps();
            $table->softDeletes();

            $table->index('kind');
            $table->index('is_active');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('companies');
    }
};
