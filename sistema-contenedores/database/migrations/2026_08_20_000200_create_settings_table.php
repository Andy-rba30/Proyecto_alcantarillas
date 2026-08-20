<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-NOT-05, RN-USR-05, RN-REN-04, RN-REN-05, RN-GAS-02
 *
 * Denisse pidio explicitamente poder cambiar plazos y cadencias sin llamar al
 * desarrollador ("eso se puede configurar en la parte de configuracion del sistema").
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('settings', function (Blueprint $table) {
            $table->id();

            // NULL = valor global; con valor = override por compañía (RN-ORG-01)
            $table->foreignId('company_id')->nullable()
                  ->constrained('companies')->nullOnDelete();

            $table->string('group', 50);              // billing | rentals | notifications | releases
            $table->string('key', 100);
            $table->text('value')->nullable();
            $table->string('type', 20)->default('string'); // string|integer|decimal|boolean|json
            $table->string('label', 150)->nullable();
            $table->boolean('is_editable')->default(true); // separa lo que el cliente puede tocar

            $table->timestamps();

            $table->unique(['company_id', 'key']);
            $table->index('group');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('settings');
    }
};
