<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * TABLA CENTRAL DEL SISTEMA.
 * RN-INV-01 .. RN-INV-12, RN-REL-03, RN-REL-09, RN-REP-02
 *
 * El numero de contenedor funciona como identificador unico, "tipo cedula" (RN-INV-01),
 * y el sistema debe avisar si ya existe (RN-INV-02).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('containers', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            // RN-INV-01 / RN-INV-02.
            // A-6 SIN RESOLVER: si la empresa RECOMPRA un contenedor que ya vendio,
            // este UNIQUE lo bloquea. El caso no se pregunto. Si A-6 se resuelve como
            // "puede volver a entrar", la salida es un unique parcial (number, deleted_at)
            // o un campo acquisition_seq.
            $table->string('number', 20)->unique();

            $table->foreignId('container_type_id')->constrained('container_types');
            $table->foreignId('container_size_id')->constrained('container_sizes');
            $table->foreignId('container_grade_id')->constrained('container_grades');

            // ====================================================================
            // P-2 SIN RESOLVER -- EL HUECO MAS GRANDE DEL MODELO
            // Erik pregunto TRES VECES por los estados del ciclo de vida y Denisse
            // respondio siempre por categoria comercial (RN-INV-08). El catalogo de
            // estados NUNCA SE LEVANTO.
            //
            // Valores [PROPUESTA], derivados de operaciones que si estan documentadas:
            //   at_depot          RN-REL-03  comprado, aun en deposito del proveedor
            //   in_yard           RN-REL-03  entro fisicamente
            //   in_refurbishment  RN-INV-09  se esta reacondicionando
            //   available         RN-MIG-02  sin registro de venta ni renta
            //   reserved          [PROPUESTA] no documentado
            //   sold              RN-COM-08
            //   rented            RN-REN-01
            //   awaiting_pickup   R1 §4      vendido, aun en yarda (renta de yarda)
            //   delivered         RN-COM-07
            //
            // VALIDAR CON EL CLIENTE ANTES DE LA CARGA INICIAL.
            // ====================================================================
            $table->string('status', 30)->default('in_yard');

            // RN-REL-09: NULL = compra suelta a proveedor pequeño.
            // El sistema debe soportar AMBOS casos.
            $table->foreignId('release_line_id')->nullable()
                  ->constrained('release_lines')->nullOnDelete();

            $table->foreignId('supplier_id')->nullable()
                  ->constrained('suppliers')->nullOnDelete();  // RN-INV-12

            $table->date('purchase_date')->nullable();
            $table->decimal('purchase_price', 12, 2)->nullable();  // RN-INV-11
            $table->decimal('pickup_cost', 12, 2)->default(0);     // RN-INV-11: traslado a la yarda

            // RN-INV-09: reacondicionamiento (pintura, techo, luces, piso).
            // Denormalizado desde expenses via observer.
            $table->decimal('refurbishment_cost', 12, 2)->default(0);

            // RN-REP-02: sin este campo no se puede calcular la ganancia real,
            // porque el sistema de facturacion no sabe en cuanto se compro.
            //   total_cost = purchase_price + pickup_cost + refurbishment_cost
            // Coincide con el ejemplo de R1 §2: 600 + 250 = 850.
            $table->decimal('total_cost', 12, 2)->default(0);

            $table->date('arrived_at_yard_on')->nullable();  // RN-REL-03: entrada fisica
            $table->date('sold_on')->nullable();
            $table->date('released_on')->nullable();         // RN-COM-07: salida fisica

            $table->string('yard_location', 50)->nullable(); // [PROPUESTA] no levantado

            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->index(['company_id', 'status']);         // dashboard: disponibles (RN-REP-04)
            $table->index('release_line_id');                // RN-REL-04
            $table->index(['container_grade_id', 'status']); // reportes por linea (RN-INV-05)
            $table->index('arrived_at_yard_on');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('containers');
    }
};
