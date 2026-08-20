<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * ====================================================================
 * CREAR SOLO SI P-1 = INTEGRAR.
 *
 * Contradiccion C-1 SIN RESOLVER:
 *   R1 §6 y R2 -> "se decidio usar la API de QuickBooks"
 *   R3 01:10:59 -> Denisse: "ya no tengo que usar QuickBooks, puedo
 *                  transicionar a esta [plataforma]"
 *   R3 01:12:19 -> QuickBooks solo cubre la compañía de TRANSPORTE;
 *                  la de contenedores esta en el Excel.
 *
 * Ver 04_quickbooks_vs_facturacion_propia.md antes de ejecutar esta migracion.
 * ====================================================================
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('quickbooks_sync_states', function (Blueprint $table) {
            $table->id();

            // El realm de QBO es por compañía (RN-ORG-01)
            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            // Customer|Invoice|Estimate|Payment|Item
            $table->string('entity_type', 40);
            $table->unsignedBigInteger('local_id')->nullable();

            $table->string('qbo_id', 50);

            // QBO exige el SyncToken en CADA update; si no coincide, rechaza con
            // error de concurrencia. Hay que persistirlo.
            $table->string('qbo_sync_token', 20)->nullable();

            $table->string('direction', 10)->default('push');   // push | pull
            $table->string('status', 20)->default('synced');    // synced|pending|conflict|failed

            $table->timestamp('last_synced_at')->nullable();
            $table->string('last_error', 500)->nullable();
            $table->json('payload')->nullable();

            $table->timestamps();

            $table->unique(['company_id', 'entity_type', 'qbo_id'], 'qbo_sync_unique_idx');
            $table->index(['entity_type', 'local_id']);
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('quickbooks_sync_states');
    }
};
