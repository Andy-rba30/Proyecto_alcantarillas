<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * RN-USR-01 .. RN-USR-05, RN-SIS-01
 *
 * Se EXTIENDE la tabla users de Laravel en lugar de reemplazarla, para no perder
 * compatibilidad con auth, password reset y los paquetes de Spatie.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->foreignId('company_id')->nullable()->after('id')
                  ->constrained('companies')->nullOnDelete();

            $table->string('locale', 5)->default('es')->after('password'); // RN-SIS-01
            $table->boolean('is_active')->default(true)->after('locale');
            $table->timestamp('last_login_at')->nullable()->after('is_active');

            $table->softDeletes();

            $table->index(['company_id', 'is_active']);
        });
    }

    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropForeign(['company_id']);
            $table->dropIndex(['company_id', 'is_active']);
            $table->dropColumn(['company_id', 'locale', 'is_active', 'last_login_at', 'deleted_at']);
        });
    }
};
