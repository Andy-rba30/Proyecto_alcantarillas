<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

/**
 * Semillas de catalogo.
 *
 * REGLA DE ESTE ARCHIVO: solo se siembra lo que el cliente dijo EXPLICITAMENTE.
 * Nada de valores "razonables" inventados. Donde falta el dato, se siembra NULL
 * para que el modulo falle de forma visible y obligue a preguntar.
 */
class BusinessCatalogSeeder extends Seeder
{
    public function run(): void
    {
        $now = now();

        // ------------------------------------------------------------------
        // RN-INV-03: "que tipo de contenedor quiere, si seco o refrigerado"
        // Otros tipos que existen en el mercado real (open top, flat rack,
        // high cube) NO fueron mencionados por el cliente. No se inventan.
        // ------------------------------------------------------------------
        DB::table('container_types')->insert([
            ['code' => 'DRY',    'name_es' => 'Seco',        'name_en' => 'Dry',   'sort_order' => 1, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => 'REEFER', 'name_es' => 'Refrigerado', 'name_en' => 'Reefer','sort_order' => 2, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
        ]);

        // ------------------------------------------------------------------
        // RN-INV-04. A-2 ABIERTA: "40 con chassis" (R1 §5) no es una medida --
        // el chassis es equipo rodante independiente. has_chassis es provisional.
        // ------------------------------------------------------------------
        DB::table('container_sizes')->insert([
            ['code' => '20',         'length_ft' => 20, 'has_chassis' => false, 'name_es' => "20 pies",              'name_en' => "20 ft",              'sort_order' => 1, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => '40',         'length_ft' => 40, 'has_chassis' => false, 'name_es' => "40 pies",              'name_en' => "40 ft",              'sort_order' => 2, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => '45',         'length_ft' => 45, 'has_chassis' => false, 'name_es' => "45 pies",              'name_en' => "45 ft",              'sort_order' => 3, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => '40_CHASSIS', 'length_ft' => 40, 'has_chassis' => true,  'name_es' => "40 pies con chassis",  'name_en' => "40 ft with chassis", 'sort_order' => 4, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
        ]);

        // ------------------------------------------------------------------
        // RN-INV-05 -- transcripcion literal de R3 (00:32:55):
        // "Premium es todo lo nuevo, estandar toda exportacion cargo worthy lo
        //  mejor usado, y en economico que es la linea economica tiene dos:
        //  los AS-IS y el W4"
        //
        // NOTA: export_capable en CW=1 y AS_IS/W4=0 es INFERENCIA del equipo
        // tecnico a partir de "estandar, toda exportacion". El cliente NO dijo
        // que AS-IS y W4 no sirvan para exportar. CONFIRMAR.
        // ------------------------------------------------------------------
        DB::table('container_grades')->insert([
            ['code' => 'NEW',   'name_es' => 'Nuevo',        'name_en' => 'New',          'product_line' => 'premium',  'condition' => 'new',  'export_capable' => true,  'sort_order' => 1, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => 'CW',    'name_es' => 'Cargo Worthy', 'name_en' => 'Cargo Worthy', 'product_line' => 'standard', 'condition' => 'used', 'export_capable' => true,  'sort_order' => 2, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => 'AS_IS', 'name_es' => 'AS-IS',        'name_en' => 'AS-IS',        'product_line' => 'economy',  'condition' => 'used', 'export_capable' => false, 'sort_order' => 3, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
            ['code' => 'W4',    'name_es' => 'W4',           'name_en' => 'W4',           'product_line' => 'economy',  'condition' => 'used', 'export_capable' => false, 'sort_order' => 4, 'is_active' => true, 'created_at' => $now, 'updated_at' => $now],
        ]);

        // ------------------------------------------------------------------
        // RN-GAS-01, RN-GAS-03, RN-GAS-04, RN-COM-09, RN-INV-09, RN-VIA-02
        // SOLO categorias que el cliente NOMBRO. La lista definitiva la entrega
        // Denisse (RN-GAS-05 / entregable §20 #9).
        // 'transportation' va con is_system porque RN-GAS-04 la exige:
        // "hay una categoria que TIENE QUE DECIR transportacion".
        // ------------------------------------------------------------------
        $categories = [
            ['transportation', 'Transportación',              'Transportation',        true],
            ['yard',           'Yarda',                       'Yard',                  false],
            ['vehicles',       'Vehículos',                   'Vehicles',              false],
            ['fuel',           'Combustible',                 'Fuel',                  false],
            ['container_fee',  'Container fee / almacenaje',  'Container fee/storage', false],
            ['materials',      'Materiales / insumos',        'Materials/supplies',    false],
            ['payroll',        'Nómina / salarios',           'Payroll',               false],
            ['parts',          'Repuestos',                   'Parts',                 false],
            ['business_meals', 'Almuerzos de negocio',        'Business meals',        false],
            ['commissions',    'Comisiones de vendedor',      'Sales commissions',     false],
            ['refurbishment',  'Reacondicionamiento',         'Refurbishment',         false],
            ['per_diem',       'Viáticos',                    'Per diem',              false],
            ['tires',          'Cauchos',                     'Tires',                 false],
        ];

        $rows = [];
        foreach ($categories as $i => [$code, $es, $en, $system]) {
            $rows[] = [
                'parent_id'  => null,
                'code'       => $code,
                'name_es'    => $es,
                'name_en'    => $en,
                'is_system'  => $system,
                'is_active'  => true,
                'sort_order' => $i + 1,
                'created_at' => $now,
                'updated_at' => $now,
            ];
        }
        DB::table('expense_categories')->insert($rows);
    }
}
