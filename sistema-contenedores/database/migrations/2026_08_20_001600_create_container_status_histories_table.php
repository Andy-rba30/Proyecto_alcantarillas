<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * [PROPUESTA] -- no pedida explicitamente.
 *
 * Justificacion: RN-DOC-03 exige ver todo el historial de una venta "en un solo
 * lado", y RN-MIG-01 documenta que el inventario actual NO es confiable
 * (416 contenedores que fisicamente no existen). Sin bitacora de movimientos,
 * el sistema nuevo hereda el mismo problema sin forma de auditarlo.
 *
 * Append-only: sin updated_at ni softDeletes.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('container_status_histories', function (Blueprint $table) {
            $table->id();

            $table->foreignId('container_id')->constrained('containers')->cascadeOnDelete();

            $table->string('from_status', 30)->nullable();
            $table->string('to_status', 30);
            $table->string('reason', 255)->nullable();

            // Que operacion lo movio: Sale, Rental, Trip, Release...
            $table->nullableMorphs('sourceable');

            $table->foreignId('user_id')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamp('created_at')->nullable();

            $table->index(['container_id', 'created_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('container_status_histories');
    }
};
