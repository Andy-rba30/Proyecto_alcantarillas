<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-VIA-03: "Hay tres depots nada mas. El del depot no [varia]: siempre el
 *             mismo fee". La recogida tiene costo FIJO, el delivery va por millas.
 * RN-REL-03: es donde quedan los contenedores del release aun no retirados.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('depots', function (Blueprint $table) {
            $table->id();

            $table->foreignId('supplier_id')->nullable()
                  ->constrained('suppliers')->nullOnDelete();

            $table->string('name', 150);
            $table->string('address_line1', 150)->nullable();
            $table->string('city', 80)->nullable();
            $table->char('state', 2)->nullable();
            $table->string('zip', 10)->nullable();

            // RN-VIA-03: costo FIJO de recogida, no por millas
            $table->decimal('pickup_flat_fee', 10, 2)->nullable();

            $table->boolean('is_active')->default(true);

            $table->timestamps();
            $table->softDeletes();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('depots');
    }
};
