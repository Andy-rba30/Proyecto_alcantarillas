<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-FIN-04, RN-FIN-05, RN-FIN-06
 *
 * Tabla propia y no un campo booleano en customers PORQUE EL CERTIFICADO VENCE
 * Y SE RENUEVA CADA AÑO: "es el mismo numero, pero tiene que mandar el papel
 * actualizado... todos los años tenemos que pedirselo al cliente".
 *
 * Un solo campo perderia el historico y no permitiria demostrar, ante una
 * auditoria, si el cliente estaba exento EN LA FECHA de una venta pasada.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('tax_exemption_certificates', function (Blueprint $table) {
            $table->id();

            $table->foreignId('customer_id')->constrained('customers')->cascadeOnDelete();

            $table->string('certificate_number', 50);   // RN-FIN-06: el numero no cambia
            $table->date('issued_on')->nullable();
            $table->date('expires_on');                 // RN-FIN-06: la fecha SI cambia cada año

            $table->foreignId('document_id')->nullable()
                  ->constrained('documents')->nullOnDelete();

            $table->boolean('is_active')->default(true);
            $table->string('notes', 255)->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->index(['customer_id', 'expires_on']);
            $table->index('expires_on');   // alerta "certificados por vencer"
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('tax_exemption_certificates');
    }
};
