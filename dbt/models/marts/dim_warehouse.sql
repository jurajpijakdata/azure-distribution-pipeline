-- Dimension: one row per warehouse (from the seed warehouses.csv).

select warehouse_code, warehouse_name, city, country, currency
from {{ ref('warehouses') }}
