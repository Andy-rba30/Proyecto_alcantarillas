<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-DOC-01 .. RN-DOC-05, RN-FIN-05, RN-FIN-06, RN-FRD-02, RN-REN-05
 *
 * Requisito repetido por Denisse: "que todo este linkado, para cuando yo busque
 * una venta ya tengo todo en un solo lado" + eliminar el papel.
 *
 * Va TEMPRANO en el orden porque muchas tablas la referencian (certificados,
 * ventas, pagos, gastos). Ella no referencia a nadie via FK: usa relacion
 * polimorfica, que no crea constraint.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('documents', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->nullable()
                  ->constrained('companies')->nullOnDelete();

            // RN-DOC-03: se ancla a Customer, Sale, Container, Invoice, Payment, Rental, Vehicle
            $table->nullableMorphs('documentable');

            // RN-DOC-02: export_certificate | tax_exemption | cc_authorization |
            //            invoice_pdf | rental_contract | supplier_invoice |
            //            vehicle_document | receipt | other
            $table->string('category', 40);

            $table->string('title', 150)->nullable();
            $table->string('original_name', 255);
            $table->string('path', 500);
            $table->string('disk', 30)->default('local');  // permite migrar a S3 sin tocar datos
            $table->string('mime_type', 100)->nullable();
            $table->unsignedInteger('size_bytes')->nullable();

            $table->date('issued_on')->nullable();
            $table->date('expires_on')->nullable();        // RN-FIN-06: renovacion anual

            $table->foreignId('uploaded_by')->nullable()
                  ->constrained('users')->nullOnDelete();

            $table->string('notes', 255)->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->index(['category', 'expires_on']);     // alerta de "certificados por vencer"
            $table->index(['company_id', 'category']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('documents');
    }
};
