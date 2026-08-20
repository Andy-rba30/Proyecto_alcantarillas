<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * FKs DIFERIDAS -- resuelve las dependencias circulares del esquema.
 *
 * Cuatro pares de tablas se referencian mutuamente y no existe un orden de
 * creacion que satisfaga a los dos lados a la vez:
 *
 *   quotes.converted_sale_id     -> sales          (sales referencia quotes)
 *   rentals.delivery_trip_id     -> trips          (trips referencia rentals)
 *   trips.driver_payout_id       -> driver_payouts (driver_payouts se cierra despues)
 *   driver_payouts.expense_id    -> expenses       (expenses va al final)
 *   vehicle_maintenances.expense_id -> expenses
 *
 * Las columnas se crearon como unsignedBigInteger sin constraint en su migracion
 * original; aqui se les añade la FK. Es la practica estandar y mantiene
 * `migrate:fresh` reproducible.
 *
 * Todas usan nullOnDelete: si se borra la venta, el presupuesto sobrevive
 * sin referencia colgante -- coherente con RN-CLI-04 (el cliente queda
 * registrado aunque solo haya pedido presupuesto).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('quotes', function (Blueprint $table) {
            $table->foreign('converted_sale_id')
                  ->references('id')->on('sales')->nullOnDelete();
        });

        Schema::table('rentals', function (Blueprint $table) {
            $table->foreign('delivery_trip_id')
                  ->references('id')->on('trips')->nullOnDelete();
        });

        Schema::table('trips', function (Blueprint $table) {
            $table->foreign('driver_payout_id')
                  ->references('id')->on('driver_payouts')->nullOnDelete();
        });

        Schema::table('driver_payouts', function (Blueprint $table) {
            $table->foreign('expense_id')
                  ->references('id')->on('expenses')->nullOnDelete();
        });

        Schema::table('vehicle_maintenances', function (Blueprint $table) {
            $table->foreign('expense_id')
                  ->references('id')->on('expenses')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::table('vehicle_maintenances', fn (Blueprint $t) => $t->dropForeign(['expense_id']));
        Schema::table('driver_payouts',       fn (Blueprint $t) => $t->dropForeign(['expense_id']));
        Schema::table('trips',                fn (Blueprint $t) => $t->dropForeign(['driver_payout_id']));
        Schema::table('rentals',              fn (Blueprint $t) => $t->dropForeign(['delivery_trip_id']));
        Schema::table('quotes',               fn (Blueprint $t) => $t->dropForeign(['converted_sale_id']));
    }
};
