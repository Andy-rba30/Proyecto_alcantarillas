<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

/**
 * Parametros del sistema (RN-NOT-05, RN-USR-05).
 *
 * Cada fila lleva en `label` la regla que la respalda y su estado de confirmacion.
 * Los marcados P-x siguen SIN CONFIRMAR por el cliente.
 *
 * yard_daily_rate se siembra en NULL A PROPOSITO (P-8): nunca se levanto la
 * tarifa. Si se sembrara un numero inventado, el sistema calcularia cargos
 * falsos y nadie lo notaria. En NULL, el modulo falla ruidosamente.
 */
class SettingsSeeder extends Seeder
{
    public function run(): void
    {
        $now = now();

        $settings = [
            // group,          key,                      value,     type,      label
            ['billing',       'sales_tax_rate',          '0.0700',  'decimal', 'RN-FIN-01 · 7% Florida · ⚠️ P-9 sin confirmar'],
            ['billing',       'credit_card_fee_rate',    '0.0350',  'decimal', 'RN-FIN-07 · 3.5% Square · ⚠️ P-9 sin confirmar'],
            ['billing',       'payment_gateway',         'square',  'string',  'RN-FIN-08 · ⚠️ P-11 Denisse quedó de enviar datos'],

            ['rentals',       'rent_grace_days',         '5',       'integer', 'RN-REN-04 · 5 días de gracia por contrato'],
            ['rentals',       'rent_late_fee_amount',    '100.00',  'decimal', 'RN-REN-05 · $100 fijo, independiente de los días'],
            ['rentals',       'rent_minimum_months',     '1',       'integer', 'RN-REN-01 · mínimo un mes'],

            ['releases',      'release_free_days',       '14',      'integer', 'RN-REL-05 · plazo de retiro del proveedor'],

            ['yard',          'yard_free_days',          '2',       'integer', 'R1 §4 · 2 días de gracia · ⚠️ A-4 R3 no lo mencionó'],
            ['yard',          'yard_daily_rate',         null,      'decimal', '🔴 P-8 · TARIFA NUNCA LEVANTADA · el módulo debe fallar'],

            ['notifications', 'dunning_start_day',       '6',       'integer', 'RN-NOT-06 · ⚠️ C-5 tres propuestas, ninguna cerrada'],
            ['notifications', 'dunning_interval_days',   '2',       'integer', 'RN-NOT-06 · ⚠️ C-5'],
            ['notifications', 'dunning_end_day',         '10',      'integer', 'RN-NOT-06 · ⚠️ C-5'],
            ['notifications', 'dunning_channels',        '["email","sms"]', 'json', 'RN-NOT-02 · todos los medios registrados'],

            ['payroll',       'driver_pay_rate_default', '0.3000',  'decimal', '🔴 P-7 / A-1 · R1 dice monto fijo, R3 dice 30%'],
        ];

        $rows = [];
        foreach ($settings as [$group, $key, $value, $type, $label]) {
            $rows[] = [
                'company_id'  => null,   // global
                'group'       => $group,
                'key'         => $key,
                'value'       => $value,
                'type'        => $type,
                'label'       => $label,
                'is_editable' => true,
                'created_at'  => $now,
                'updated_at'  => $now,
            ];
        }

        DB::table('settings')->insert($rows);
    }
}
