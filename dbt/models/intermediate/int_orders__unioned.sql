-- All order lines of the 4 warehouses in one table.
-- Same columns from every warehouse; vat_rate exists only in Žilina's
-- newer exports, so the others get NULL. Nothing removed here.

{% set columns %}
    order_no, line_no, order_type, original_order_no,
    order_date, order_date_raw, warehouse_code, customer_id,
    sku, sku_raw, product_name, quantity, quantity_raw, unit,
    unit_price, currency, line_total
{% endset %}

select {{ columns }}, cast(null as decimal(5, 2)) as vat_rate, _source_file, _loaded_at
from {{ ref('stg_erp__orders_ba') }}

union all

select {{ columns }}, vat_rate, _source_file, _loaded_at
from {{ ref('stg_erp__orders_za') }}

union all

select {{ columns }}, cast(null as decimal(5, 2)) as vat_rate, _source_file, _loaded_at
from {{ ref('stg_erp__orders_ke') }}

union all

select {{ columns }}, cast(null as decimal(5, 2)) as vat_rate, _source_file, _loaded_at
from {{ ref('stg_erp__orders_brn') }}