<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Detalle del presupuesto. is_taxable a nivel de linea por RN-FIN-02 / RN-FIN-03.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('quote_lines', function (Blueprint $table) {
            $table->id();

            $table->foreignId('quote_id')->constrained('quotes')->cascadeOnDelete();

            $table->unsignedSmallInteger('line_number')->default(1);
            $table->string('line_type', 20)->default('container'); // container|delivery|fee|discount
            $table->string('description', 255);

            $table->foreignId('container_type_id')->nullable()
                  ->constrained('container_types')->nullOnDelete();
            $table->foreignId('container_size_id')->nullable()
                  ->constrained('container_sizes')->nullOnDelete();
            $table->foreignId('container_grade_id')->nullable()
                  ->constrained('container_grades')->nullOnDelete();

            $table->decimal('quantity', 10, 2)->default(1);
            $table->decimal('unit_price', 12, 2)->default(0);
            $table->decimal('line_total', 12, 2)->default(0);

            // RN-FIN-02 / RN-FIN-03: la linea de delivery va con is_taxable = false
            $table->boolean('is_taxable')->default(true);

            $table->timestamps();

            $table->index('quote_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('quote_lines');
    }
};
