<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-NOT-01, RN-NOT-02, RN-NOT-03
 *
 * Necesaria para PROBAR que se aviso antes de cobrar el fee de RN-REN-05:
 * la condicion contractual del cobro es "no se ha recibido ninguna comunicacion".
 * Sin bitacora, la penalidad de $100 no es defendible ante un reclamo.
 *
 * Append-only: sin updated_at ni softDeletes.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('notification_logs', function (Blueprint $table) {
            $table->id();

            $table->foreignId('notification_rule_id')->nullable()
                  ->constrained('notification_rules')->nullOnDelete();
            $table->foreignId('customer_id')->nullable()
                  ->constrained('customers')->nullOnDelete();

            $table->nullableMorphs('notifiable');   // RentalPeriod, Release...

            $table->string('channel', 20);
            $table->string('recipient', 150);       // RN-NOT-02: el telefono o correo concreto
            $table->string('subject', 200)->nullable();
            $table->text('body')->nullable();       // RN-NOT-03: guarda el periodo notificado

            $table->string('status', 20)->default('queued'); // queued|sent|failed
            $table->timestamp('sent_at')->nullable();
            $table->string('provider_reference', 100)->nullable();
            $table->string('error_message', 255)->nullable();

            $table->timestamp('created_at')->nullable();

            $table->index(['customer_id', 'sent_at']);
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notification_logs');
    }
};
