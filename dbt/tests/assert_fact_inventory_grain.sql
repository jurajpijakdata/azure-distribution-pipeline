-- Grain of fact_inventory: one row per product, warehouse and snapshot date.
select snapshot_date, warehouse_code, sku, count(*) as n
from {{ ref('fact_inventory') }}
group by snapshot_date, warehouse_code, sku
having count(*) > 1
