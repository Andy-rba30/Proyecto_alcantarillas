<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-REL-01: "un numero de release agrupa N contenedores del MISMO TIPO Y MEDIDA".
 *
 * Un release puede pactar varias combinaciones tipo/medida/grado, cada una con su
 * cantidad y costo unitario. Sin esta tabla no se sabe a que precio entro cada
 * contenedor de un lote mixto -- y sin eso RN-REP-02 (ganancia real) es incalculable.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('release_lines', function (Blueprint $table) {
            $table->id();

            $table->foreignId('release_id')->constrained('releases')->cascadeOnDelete();

            $table->foreignId('container_type_id')->constrained('container_types');
            $table->foreignId('container_size_id')->constrained('container_sizes');
            $table->foreignId('container_grade_id')->nullable()
                  ->constrained('container_grades')->nullOnDelete();

            $table->unsignedInteger('quantity');
            $table->decimal('unit_cost', 12, 2);          // RN-INV-07: volumen mejora el precio
            $table->unsignedInteger('picked_quantity')->default(0);  // RN-REL-04

            $table->timestamps();

            $table->index(['release_id', 'container_size_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('release_lines');
    }
};
