<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-INV-12: el campo que hoy se llama "cliente" en la hoja de compras
 *            ES EN REALIDAD EL PROVEEDOR. Debe renombrarse en el sistema nuevo.
 * RN-REL-02, RN-REL-05, RN-REL-07
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('suppliers', function (Blueprint $table) {
            $table->id();

            $table->string('name', 150);
            $table->string('contact_name', 100)->nullable();
            $table->string('phone', 25)->nullable();
            $table->string('email', 150)->nullable();   // RN-REL-08: se documenta por correo

            $table->string('address_line1', 150)->nullable();
            $table->string('city', 80)->nullable();
            $table->char('state', 2)->nullable();
            $table->string('zip', 10)->nullable();

            $table->unsignedSmallInteger('default_free_days')->default(14); // RN-REL-05

            // RN-REL-07: "uno te cobra 8 al dia, otro 6 y otro 2".
            // Vive en el PROVEEDOR, no en settings: la tarifa es por proveedor.
            $table->decimal('default_storage_fee_per_day', 10, 2)->nullable();

            $table->boolean('is_active')->default(true);
            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->index('name');
            $table->index('is_active');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('suppliers');
    }
};
