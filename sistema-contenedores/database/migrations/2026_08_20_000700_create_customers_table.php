<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-CLI-01 .. RN-CLI-07, RN-FIN-04, RN-FRD-03, RN-FRD-04
 *
 * Hoy NO existe modulo de clientes: un cliente frecuente se vuelve a registrar
 * por completo en cada operacion (RN-CLI-01). Esta tabla es el nucleo del CRM.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('customers', function (Blueprint $table) {
            $table->id();

            // P-12 SIN RESOLVER: no se pregunto si la cartera es compartida
            // entre ambas compañías. NULL = compartido.
            $table->foreignId('company_id')->nullable()
                  ->constrained('companies')->nullOnDelete();

            $table->string('customer_code', 20)->nullable()->unique();

            // RN-CLI-05: un contacto personal puede facturar a nombre de otra organizacion
            $table->string('type', 20)->default('individual'); // individual|company

            $table->string('display_name', 150);
            $table->string('first_name', 80)->nullable();
            $table->string('last_name', 80)->nullable();
            $table->string('organization_name', 150)->nullable();

            // RN-CLI-05: el dueño pidio expresamente poder buscar por telefono.
            // VARCHAR y no INT: un telefono no se suma, lleva +1, guiones y parentesis.
            $table->string('primary_phone', 25)->nullable();
            $table->string('primary_email', 150)->nullable();

            // RN-CLI-07: facturacion y shipping SEPARADAS
            $table->string('billing_address_line1', 150)->nullable();
            $table->string('billing_address_line2', 150)->nullable();
            $table->string('billing_city', 80)->nullable();
            $table->char('billing_state', 2)->nullable();
            $table->string('billing_zip', 10)->nullable();

            $table->string('shipping_address_line1', 150)->nullable();
            $table->string('shipping_city', 80)->nullable();
            $table->char('shipping_state', 2)->nullable();
            $table->string('shipping_zip', 10)->nullable();  // alimenta el calculo de millas RN-COM-01

            $table->boolean('is_tax_exempt')->default(false); // RN-FIN-04

            // RN-FRD-03: verificacion en Sunbiz (registro mercantil de Florida)
            $table->boolean('sunbiz_verified')->default(false);
            $table->string('sunbiz_document_number', 30)->nullable();
            $table->date('sunbiz_verified_at')->nullable();

            // RN-FRD-04: por DEFECTO NO se acepta tarjeta. Se habilita tras verificar.
            $table->boolean('credit_card_allowed')->default(false);
            $table->string('credit_card_policy_note', 255)->nullable();

            $table->string('source', 30)->nullable();  // RN-COM-11. P-14 abierta
            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            // RN-CLI-05: filtros multiples -- nombre, telefono, organizacion
            $table->index('display_name');
            $table->index('organization_name');
            $table->index('primary_phone');
            $table->index(['company_id', 'type']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('customers');
    }
};
