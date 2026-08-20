<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;
use Spatie\Permission\PermissionRegistrar;

/**
 * RN-USR-01 .. RN-USR-05
 *
 * Roles TAL COMO los nombro el cliente:
 *   admin       Denisse y Michael -- "los que mas vamos a utilizarlo somos yo y Michael"
 *   operator    RN-USR-02 -- "un usuario con restriccion de ciertas cosas de finanzas,
 *               pero si a la parte de entrar los contenedores, entrar los releases"
 *   salesperson RN-USR-03
 *   driver      RN-VIA-07 -- "un panel especifico para los choferes"
 *   viewer      RN-USR-04 -- "el dueño consulta reportes sin capturar informacion"
 *
 * NOTA: config/permission.php debe tener 'teams' => true ANTES de correr esto.
 * Habilitarlo despues obliga a migrar las tablas pivote con datos productivos
 * dentro. Cuesta una tarde ahora y una semana en seis meses.
 */
class RolesAndPermissionsSeeder extends Seeder
{
    public function run(): void
    {
        app(PermissionRegistrar::class)->forgetCachedPermissions();

        $modules = [
            'customer', 'quote', 'sale', 'rental', 'rental_payment',
            'container', 'release', 'supplier', 'trip', 'vehicle',
            'invoice', 'payment', 'expense', 'document',
            'report', 'setting', 'user',
        ];

        foreach ($modules as $module) {
            foreach (['view', 'create', 'update', 'delete'] as $action) {
                Permission::findOrCreate("{$module}.{$action}");
            }
        }

        // Permisos de negocio que no son CRUD
        Permission::findOrCreate('rental.waive_late_fee');   // RN-REN-06
        Permission::findOrCreate('payment.accept_credit_card'); // RN-FRD-04
        Permission::findOrCreate('report.view_financials');  // RN-USR-02
        Permission::findOrCreate('company.switch');          // RN-ORG-01

        Role::findOrCreate('admin')->givePermissionTo(Permission::all());

        // RN-USR-02: contenedores y releases SI, finanzas NO
        Role::findOrCreate('operator')->syncPermissions([
            'customer.view', 'customer.create', 'customer.update',
            'container.view', 'container.create', 'container.update',
            'release.view', 'release.create', 'release.update',
            'supplier.view',
            'trip.view', 'trip.create', 'trip.update',
            'document.view', 'document.create',
        ]);

        Role::findOrCreate('salesperson')->syncPermissions([
            'customer.view', 'customer.create', 'customer.update',
            'quote.view', 'quote.create', 'quote.update',
            'sale.view', 'sale.create',
            'container.view',
            'document.view', 'document.create',
        ]);

        // RN-VIA-07: panel propio para registrar sus operaciones y gastos
        Role::findOrCreate('driver')->syncPermissions([
            'trip.view', 'trip.update',
            'expense.view', 'expense.create',
            'document.create',
        ]);

        // RN-USR-04: el dueño consulta, no captura
        Role::findOrCreate('viewer')->syncPermissions([
            'customer.view', 'quote.view', 'sale.view', 'rental.view',
            'container.view', 'release.view', 'trip.view',
            'invoice.view', 'payment.view', 'expense.view',
            'report.view', 'report.view_financials',
        ]);
    }
}
