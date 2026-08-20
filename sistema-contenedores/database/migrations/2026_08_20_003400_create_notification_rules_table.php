<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-NOT-05 -- REGLA EXPLICITA:
 * "la frecuencia y el inicio de las notificaciones automaticas seran
 *  administrables desde la configuracion del sistema... para que ustedes no
 *  vengan y nos digan mira, ya no quiero que aparezca a partir del primer dia"
 *
 * C-5 ABIERTA: la cadencia concreta NUNCA se cerro. En la misma conversacion
 * aparecen TRES propuestas y ninguna se declaro ganadora:
 *   - diario del dia 5 al 10                    (Denisse, 01:03:04)
 *   - cada dos dias: 6, 8, 10 = tres avisos     (Denisse, 01:05:01)
 *   - correo desde el dia 1, SMS desde el 5     (Ronny,   01:04:00)
 * Denisse cierra devolviendo la pregunta al equipo, sin respuesta.
 *
 * Se siembra la opcion intermedia y se deja configurable.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('notification_rules', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            // rent_due | rent_overdue | tax_cert_expiring | release_deadline
            $table->string('event', 50);
            $table->string('channel', 20);   // RN-NOT-02: email | sms

            // SMALLINT CON SIGNO a proposito: la propuesta de Ronny incluye enviar
            // correo ANTES del vencimiento, lo que exige valores negativos.
            // Declararlo UNSIGNED cerraria esa opcion sin que nadie lo decidiera.
            $table->smallInteger('start_offset_days')->default(0);
            $table->unsignedSmallInteger('interval_days')->default(2);
            $table->smallInteger('end_offset_days')->default(10);

            // RN-NOT-06: "son tres notificaciones"
            $table->unsignedSmallInteger('max_notifications')->nullable();

            $table->string('template_key', 50);   // plantilla en resources/lang (RN-SIS-01)
            $table->boolean('is_active')->default(true);

            $table->timestamps();

            $table->unique(['company_id', 'event', 'channel']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notification_rules');
    }
};
