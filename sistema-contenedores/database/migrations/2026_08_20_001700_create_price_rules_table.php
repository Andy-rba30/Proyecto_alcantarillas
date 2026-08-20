<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-INV-06: "El estado se mantiene, lo que varia es el precio de acuerdo al SEASON...
 *             un AS-IS te puede costar 1000 hoy y la semana que viene 700"
 * RN-INV-07: comprar en volumen mejora el precio
 * RN-COM-02: storage y exportacion tienen precios distintos
 * RN-REN-12 / C-4: para RENTA sigue abierto si el precio depende del tamaño
 *
 * R1 dejo abierto que se parametriza y que se captura libre (pregunta #3).
 * Esta tabla permite AMBAS: si hay regla vigente se sugiere el precio; si no,
 * se captura a mano. Nada obliga a usarla.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('price_rules', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            $table->string('scope', 10);   // sale | rent   (rent sujeto a C-4)

            // NULL = aplica a todos
            $table->foreignId('container_type_id')->nullable()
                  ->constrained('container_types')->nullOnDelete();
            $table->foreignId('container_size_id')->nullable()
                  ->constrained('container_sizes')->nullOnDelete();
            $table->foreignId('container_grade_id')->nullable()
                  ->constrained('container_grades')->nullOnDelete();

            $table->string('intended_use', 20)->nullable();   // storage | export -- RN-COM-02

            $table->unsignedInteger('min_quantity')->default(1);  // RN-INV-07

            $table->decimal('amount', 12, 2);

            $table->date('effective_from');                   // RN-INV-06: temporada
            $table->date('effective_to')->nullable();         // NULL = vigente

            $table->boolean('is_active')->default(true);
            $table->string('notes', 255)->nullable();

            $table->timestamps();

            $table->index(['company_id', 'scope', 'effective_from', 'effective_to'], 'price_rules_lookup_idx');
            $table->index(['container_size_id', 'container_grade_id', 'intended_use'], 'price_rules_combo_idx');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('price_rules');
    }
};
