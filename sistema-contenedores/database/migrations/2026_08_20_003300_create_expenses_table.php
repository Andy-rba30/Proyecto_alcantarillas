<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-GAS-01 .. RN-GAS-06, RN-INV-09, RN-REL-06, RN-VIA-02, RN-ORG-08
 *
 * LA RELACION POLIMORFICA `expensable` NO ES ADORNO: resuelve cinco reglas
 * distintas con UNA sola tabla, y hace que el reporte de RN-GAS-04
 * ("materiales, salarios, transportacion") salga de una unica consulta agrupada:
 *
 *   Container -> RN-INV-09  reacondicionamiento, suma a containers.refurbishment_cost
 *   Release   -> RN-REL-06  fee de almacenaje del deposito
 *   Trip      -> RN-VIA-02  gasolina, viaticos, cauchos, reparaciones en ruta
 *   Vehicle   -> RN-VIA-11  mantenimiento
 *   NULL      -> RN-GAS-01  gasto general (nomina, almuerzos de negocio)
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('expenses', function (Blueprint $table) {
            $table->id();

            // RN-ORG-08: los gastos se separan por compañía. La categoria
            // "transportacion" acumula lo que Contenedores debe a Transporte.
            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            $table->foreignId('expense_category_id')->constrained('expense_categories');

            $table->date('expense_date');

            $table->foreignId('supplier_id')->nullable()
                  ->constrained('suppliers')->nullOnDelete();   // RN-REL-06

            $table->string('description', 255);     // RN-GAS-01: tipo Y descripcion
            $table->decimal('amount', 12, 2);
            $table->string('payment_method', 20)->nullable();

            $table->nullableMorphs('expensable');

            $table->foreignId('document_id')->nullable()
                  ->constrained('documents')->nullOnDelete();   // factura del proveedor
            $table->string('reference', 60)->nullable();        // n.º de factura del proveedor

            $table->text('notes')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamps();
            $table->softDeletes();

            $table->index(['company_id', 'expense_date']);            // RN-REP-03
            $table->index(['expense_category_id', 'expense_date']);   // RN-GAS-04
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('expenses');
    }
};
