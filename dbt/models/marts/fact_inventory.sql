-- Fact: one row per product per warehouse per weekly snapshot (Fridays).
-- Stock value at cost price (EUR).

with valid_rows as (

    select * from {{ ref('int_inventory__validated') }}
    where rejection_reasons is null

),

products as (

    select sku, cost_eur from {{ ref('stg_erp__products') }}

)

select
    i.snapshot_date,
    i.warehouse_code,
    i.sku_standard                                              as sku,
    i.qty_on_hand,
    i.unit,
    cast(i.qty_on_hand * p.cost_eur as decimal(14, 2))          as stock_value_eur
from valid_rows i
join products p
    on i.sku_standard = p.sku
