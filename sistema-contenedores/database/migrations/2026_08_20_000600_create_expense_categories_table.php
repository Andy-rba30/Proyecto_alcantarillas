<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-GAS-02 -- REGLA EXPLICITA DEL CLIENTE, no diseño academico:
 * "podemos crear un dropdown, una lista que empieza a categorizarlos...
 *  yo los puedo ir alimentando".
 *
 * Por eso es TABLA y no un enum de PHP: el cliente añade valores en runtime.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('expense_categories', function (Blueprint $table) {
            $table->id();

            $table->foreignId('parent_id')->nullable()
                  ->constrained('expense_categories')->nullOnDelete();

            $table->string('code', 30)->unique();
            $table->string('name_es', 80);
            $table->string('name_en', 80);   // RN-SIS-01: bilingue

            // Protege las que el sistema necesita para funcionar,
            // p.ej. 'transportation' exigida por RN-GAS-04
            $table->boolean('is_system')->default(false);

            $table->boolean('is_active')->default(true);   // se desactiva, no se borra
            $table->smallInteger('sort_order')->default(0);

            $table->timestamps();

            $table->index(['is_active', 'sort_order']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('expense_categories');
    }
};
