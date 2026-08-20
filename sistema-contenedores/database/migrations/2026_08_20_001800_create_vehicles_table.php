<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-VIA-11: "el VIN number, el plate number, que tipo de vehiculos son...
 *             hay una parte de transporte que es vehiculos [y] mantenimiento".
 * Denisse ya tiene el Excel de vehiculos (entregable §20 #6).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('vehicles', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            // El VIN tiene EXACTAMENTE 17 caracteres por norma ISO 3779 -> CHAR, no VARCHAR
            $table->char('vin', 17)->nullable()->unique();
            $table->string('plate_number', 15)->nullable();
            $table->string('vehicle_type', 40)->nullable();

            $table->string('make', 40)->nullable();     // [PROPUESTA]
            $table->string('model', 40)->nullable();    // [PROPUESTA]
            $table->unsignedSmallInteger('year')->nullable();

            $table->boolean('is_active')->default(true);
            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->index(['company_id', 'is_active']);
            $table->index('plate_number');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('vehicles');
    }
};
