<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * TABLA CLAVE DEL MODULO DE RENTAS.
 * RN-REN-02, RN-REN-03, RN-REN-06, RN-REN-07, RN-REN-08, RN-NOT-03, RN-REP-06
 *
 * Materializa cada ciclo mensual como UNA FILA. Sin ella, el periodo explicito
 * en factura (RN-REN-03) y el semaforo (RN-REN-07) habria que calcularlos al
 * vuelo en cada render -- inviable con Livewire y fragil ante pagos adelantados.
 *
 * SEMAFORO RN-REN-07 (derivado, NO se almacena el color):
 *   rojo     : status IN (pending, overdue)  AND  hoy > grace_until
 *   amarillo : status = pending  AND  paid_amount = 0
 *              (Denisse: "cuando yo le doy guardar, como he puesto que todavia
 *               no me ha pagado, YA ME SALE AMARILLO automaticamente")
 *   normal   : status IN (paid, waived)
 *
 * No se almacena el color porque obligaria a un job que repintara filas cada
 * medianoche, y quedaria desincronizado cualquier dia que el job fallara.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('rental_periods', function (Blueprint $table) {
            $table->id();

            $table->foreignId('rental_id')->constrained('rentals')->cascadeOnDelete();

            $table->unsignedInteger('period_number');   // 1, 2, 3...

            // RN-REN-03: "del 2 de agosto al 2 de septiembre"
            $table->date('period_start');
            $table->date('period_end');

            // Congelado: monthly_amount del contrato puede cambiar a futuro
            $table->decimal('amount', 12, 2);
            $table->decimal('tax_amount', 12, 2)->default(0);

            $table->date('due_date');                   // RN-REN-02
            $table->date('grace_until');                // due_date + rentals.grace_days

            $table->string('status', 20)->default('pending'); // pending|paid|overdue|waived

            $table->decimal('paid_amount', 12, 2)->default(0);
            $table->date('paid_at')->nullable();

            // RN-REN-05: fee FIJO de $100, independiente de los dias de atraso
            $table->decimal('late_fee_amount', 10, 2)->default(0);

            // RN-REN-06: "a veces en la practica no lo hemos enforzado... que me des
            // la opcion de que a lo mejor no se lo quiero cobrar".
            // Se registra QUIEN condono y POR QUE: mueve dinero, necesita auditoria.
            $table->boolean('late_fee_waived')->default(false);
            $table->foreignId('late_fee_waived_by')->nullable()
                  ->constrained('users')->nullOnDelete();
            $table->string('late_fee_waived_reason', 255)->nullable();

            $table->foreignId('invoice_id')->nullable()
                  ->constrained('invoices')->nullOnDelete();   // RN-REN-03

            // RN-NOT-06: control de cadencia configurable
            $table->unsignedSmallInteger('notifications_sent')->default(0);
            $table->date('last_notified_at')->nullable();

            $table->timestamps();

            $table->unique(['rental_id', 'period_number']);
            $table->index(['status', 'due_date']);      // RN-REP-06: morosos por dia
            $table->index(['status', 'grace_until']);   // semaforo rojo
            $table->index('due_date');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rental_periods');
    }
};
