<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-VIA-06 ("no existe ficha de choferes ni de trabajadores"), RN-VIA-11,
 * RN-GAS-06 (nomina como gasto), RN-COM-09 (comision de vendedor).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('employees', function (Blueprint $table) {
            $table->id();

            $table->foreignId('company_id')->constrained('companies')->cascadeOnDelete();

            // Nullable: no todo empleado tiene acceso al sistema (RN-VIA-07)
            $table->foreignId('user_id')->nullable()->unique()
                  ->constrained('users')->nullOnDelete();

            $table->string('employee_code', 20)->nullable()->unique();
            $table->string('first_name', 80);
            $table->string('last_name', 80);

            // RN-USR-03, RN-GAS-06: driver|salesperson|admin|office|other
            $table->string('position', 40);

            $table->string('phone', 25)->nullable();
            $table->string('email', 150)->nullable();
            $table->date('hire_date')->nullable();

            $table->string('driver_license_number', 40)->nullable(); // [PROPUESTA] pendiente §20 #7
            $table->date('license_expires_on')->nullable();

            // A-1 / P-7 SIN RESOLVER: R1 dice "85 de 280" (monto fijo),
            // R3 dice "el 30% de los 400" (porcentaje). El par scheme+rate
            // soporta ambas lecturas sin migracion posterior.
            $table->string('pay_scheme', 20)->nullable();   // percentage|fixed_per_trip|salary
            $table->decimal('pay_rate', 10, 4)->nullable(); // 0.3000  o  85.0000

            $table->decimal('commission_rate', 6, 4)->nullable(); // RN-COM-09

            $table->boolean('is_active')->default(true);    // RN-USR-05: alta/baja desde el sistema
            $table->text('notes')->nullable();

            $table->timestamps();
            $table->softDeletes();

            $table->index(['company_id', 'position']);
            $table->index('is_active');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('employees');
    }
};
