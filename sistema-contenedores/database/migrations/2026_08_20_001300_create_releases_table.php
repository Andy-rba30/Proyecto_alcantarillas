<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-REL-01 .. RN-REL-10
 *
 * Un "release" es una orden de compra por lote pactada con un proveedor grande.
 * Denisse: "es cuando ya te autorizan a recogerlos".
 *
 * Los contenedores del release SOLO se registran individualmente cuando llegan
 * fisicamente a la yarda (RN-REL-03); el resto sigue en el deposito del proveedor.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('releases', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();
            $table->foreignId('supplier_id')->constrained('suppliers');   // RN-REL-02: "quien lo vendio"
            $table->foreignId('depot_id')->nullable()
                  ->constrained('depots')->nullOnDelete();                // RN-REL-03

            $table->string('release_number', 50);
            $table->date('issued_on');

            $table->unsignedSmallInteger('free_days')->default(14);       // RN-REL-05

            // Se ALMACENA en lugar de calcularse porque RN-REL-08 permite extenderlo.
            // La fecha efectiva es COALESCE(deadline_extended_to, pickup_deadline).
            $table->date('pickup_deadline');
            $table->date('deadline_extended_to')->nullable();             // RN-REL-08
            $table->string('extension_reason', 255)->nullable();          // rastro documental

            // RN-REL-07: se copia del proveedor y se CONGELA en el release
            $table->decimal('storage_fee_per_day', 10, 2)->nullable();

            $table->unsignedInteger('total_quantity')->default(0);        // RN-REL-02
            // RN-REL-04: "me faltan cinco por recoger". Desnormalizado a proposito:
            // es una consulta de pantalla constante; contar filas en cada render
            // de Livewire seria innecesario. Se mantiene con un observer.
            $table->unsignedInteger('picked_quantity')->default(0);

            $table->decimal('total_cost', 14, 2)->default(0);             // RN-REL-02

            $table->string('status', 20)->default('open'); // open|partially_picked|closed|expired

            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->unique(['supplier_id', 'release_number']);
            $table->index(['status', 'pickup_deadline']);  // alerta de releases por vencer
            $table->index(['company_id', 'issued_on']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('releases');
    }
};
