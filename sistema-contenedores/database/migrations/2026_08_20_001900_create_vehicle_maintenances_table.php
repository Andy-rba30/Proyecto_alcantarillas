<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-VIA-11 -- mencionado como necesario pero SIN DETALLE.
 * Estructura deliberadamente minima: no se inventan campos que el cliente
 * no pidio. Se ampliara cuando entregue el formato de vehiculos (§20 #6).
 *
 * expense_id se enlaza en la migracion 003800 (FK diferida).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('vehicle_maintenances', function (Blueprint $table) {
            $table->id();

            $table->foreignId('vehicle_id')->constrained('vehicles')->cascadeOnDelete();

            $table->date('performed_on');
            $table->string('description', 255);
            $table->decimal('cost', 12, 2)->default(0);   // RN-GAS-03: categoria "vehiculos"
            $table->unsignedInteger('odometer')->nullable();  // [PROPUESTA]

            // FK añadida en 003800_add_deferred_foreign_keys (expenses aun no existe)
            $table->unsignedBigInteger('expense_id')->nullable();

            $table->timestamps();

            $table->index(['vehicle_id', 'performed_on']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('vehicle_maintenances');
    }
};
