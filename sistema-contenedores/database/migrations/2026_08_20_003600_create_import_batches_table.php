<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-SIS-04: "el sistema requerira una funcion de importacion desde Excel
 *             para esa carga inicial"
 * RN-MIG-01 .. RN-MIG-04
 *
 * La bitacora es imprescindible porque RN-MIG-01 documenta que EL INVENTARIO
 * DEL EXCEL NO ES CONFIABLE (416 contenedores que fisicamente no existen).
 * Hay que poder decir exactamente que entro, que fallo y por que.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('import_batches', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            // containers|customers|rentals|sales|expenses|vehicles
            $table->string('type', 40);

            $table->string('original_name', 255);
            $table->string('path', 500);       // se conserva el archivo original

            $table->string('status', 20)->default('pending');
            // pending|processing|completed|failed

            $table->unsignedInteger('total_rows')->default(0);
            $table->unsignedInteger('imported_rows')->default(0);
            $table->unsignedInteger('failed_rows')->default(0);

            $table->json('errors')->nullable();   // fila + motivo del rechazo

            $table->timestamp('started_at')->nullable();
            $table->timestamp('finished_at')->nullable();

            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();

            $table->timestamps();

            $table->index(['company_id', 'type', 'status']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('import_batches');
    }
};
