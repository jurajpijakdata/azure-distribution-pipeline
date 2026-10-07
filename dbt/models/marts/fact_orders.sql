-- Fact: one row per valid order line (order_no + line_no).
-- Returns have negative quantity, revenue, cost and margin.
-- Amounts in EUR; CZK converted with the ECB rate of the order day.

with valid_lines as (

    select * from {{ ref('int_orders__validated') }}
    where rejection_reasons is null

),

products as (

    select sku, cost_eur from {{ ref('stg_erp__products') }}

)

select
    o.order_no,
    o.line_no,
    o.order_type,
    o.original_order_no,
    o.order_date,
    o.warehouse_code,
    o.customer_id,
    o.sku_standard                                              as sku,
    o.quantity,
    o.unit,
    o.currency                                                  as original_currency,
    o.unit_price                                                as unit_price_original,
    o.unit_price_eur,
    o.line_total_eur                                            as revenue_eur,
    cast(o.quantity * p.cost_eur as decimal(14, 2))             as cost_eur,
    cast(o.line_total_eur - o.quantity * p.cost_eur as decimal(14, 2)) as margin_eur,
    o.vat_rate,
    o._source_file                                              as source_file
from valid_lines o
join products p
    on o.sku_standard = p.sku
