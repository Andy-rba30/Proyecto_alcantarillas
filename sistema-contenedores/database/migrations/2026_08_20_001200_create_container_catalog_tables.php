<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Catalogos de contenedor. Son TABLAS y no enums de PHP por RN-SIS-03
 * (terminologia estandar y administrable) y porque el catalogo comercial crece.
 *
 * RN-INV-03: tipos -- seco y refrigerado
 * RN-INV-04: medidas -- 20, 40, (45), (40 con chassis)  [A-2 abierta]
 * RN-INV-05: grados -- tres lineas de producto
 */
return new class extends Migration
{
    public function up(): void
    {
        // RN-INV-03: "que tipo de contenedor quiere, si seco o refrigerado"
        Schema::create('container_types', function (Blueprint $table) {
            $table->id();
            $table->string('code', 20)->unique();      // DRY | REEFER
            $table->string('name_es', 60);
            $table->string('name_en', 60);
            $table->smallInteger('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        // RN-INV-04. A-2: "40 con chassis" NO es una medida -- el chassis es
        // equipo rodante independiente. has_chassis es una solucion PROVISIONAL
        // hasta que el cliente aclare si se vende/renta aparte.
        Schema::create('container_sizes', function (Blueprint $table) {
            $table->id();
            $table->string('code', 20)->unique();      // 20 | 40 | 45 | 40_CHASSIS
            $table->unsignedSmallInteger('length_ft');
            $table->boolean('has_chassis')->default(false);
            $table->string('name_es', 60);
            $table->string('name_en', 60);
            $table->smallInteger('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        // RN-INV-05: "si lo vas a desglosar dentro del usado estan dos categorias,
        // una economica que seria un AS-IS y un W4, y un estandar que serian los
        // cargo worthy... Premium es todo lo nuevo"
        Schema::create('container_grades', function (Blueprint $table) {
            $table->id();
            $table->string('code', 20)->unique();      // NEW | CW | AS_IS | W4
            $table->string('name_es', 60);
            $table->string('name_en', 60);
            $table->string('product_line', 20);        // premium | standard | economy
            $table->string('condition', 10);           // new | used

            // [PROPUESTA] Derivado de "estandar, toda exportacion, cargo worthy".
            // Que AS-IS y W4 NO sirvan para exportar es INFERENCIA, no afirmacion
            // del cliente. Confirmar.
            $table->boolean('export_capable')->default(false);

            $table->smallInteger('sort_order')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->index('product_line');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('container_grades');
        Schema::dropIfExists('container_sizes');
        Schema::dropIfExists('container_types');
    }
};
