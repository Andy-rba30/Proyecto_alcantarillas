<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Pivote venta <-> contenedores. Una venta puede llevar varios (RN-INV-07: volumen).
 *
 * RN-REP-02 y RN-DOC-03 dependen de esta tabla: es la que permite responder
 * "que fue lo que se le vendio" y calcular la ganancia real.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sale_containers', function (Blueprint $table) {
            $table->id();

            $table->foreignId('sale_id')->constrained('sales')->cascadeOnDelete();
            $table->foreignId('container_id')->constrained('containers');

            $table->decimal('unit_price', 12, 2)->default(0);

            // ====================================================================
            // unit_cost_snapshot: COPIA de containers.total_cost AL MOMENTO DE VENDER.
            //
            // Por que no leer containers.total_cost al vuelo: si el mes que viene
            // se registra un gasto tardio contra ese contenedor, total_cost sube y
            // la ganancia de una venta YA CERRADA cambiaria retroactivamente. Los
            // reportes de meses cerrados dejarian de reproducirse.
            // Mismo principio que congelar tax_rate.
            // ====================================================================
            $table->decimal('unit_cost_snapshot', 12, 2)->default(0);
            $table->decimal('line_profit', 12, 2)->default(0); // unit_price - unit_cost_snapshot

            $table->timestamps();

            $table->unique(['sale_id', 'container_id']);
            $table->index('container_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('sale_containers');
    }
};
