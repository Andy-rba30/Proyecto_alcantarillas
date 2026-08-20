<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-CLI-06 ("puedo agregar mas de un email... y hay veces en contaduria son dos personas")
 * RN-NOT-02 ("el sistema va a utilizar los modos de comunicacion que tengamos
 *             archivados para ese cliente")
 *
 * Sin esta tabla, RN-NOT-02 es IMPOSIBLE de cumplir: no habria donde guardar
 * los dos telefonos que Denisse menciona.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('customer_contacts', function (Blueprint $table) {
            $table->id();

            $table->foreignId('customer_id')->constrained('customers')->cascadeOnDelete();

            $table->string('kind', 10);           // phone | email
            $table->string('value', 150);
            $table->string('label', 50)->nullable();        // owner | accounting | mobile
            $table->string('contact_name', 100)->nullable(); // RN-CLI-06

            $table->boolean('is_primary')->default(false);
            $table->boolean('receives_billing')->default(true);  // RN-FIN-12
            $table->boolean('receives_dunning')->default(true);  // RN-NOT-02
            $table->boolean('is_active')->default(true);

            $table->timestamps();

            $table->unique(['customer_id', 'kind', 'value']);
            $table->index(['kind', 'receives_dunning']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('customer_contacts');
    }
};
