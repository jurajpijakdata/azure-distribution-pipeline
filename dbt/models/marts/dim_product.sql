-- Dimension: one row per product.
-- Cost and list price are a single price list (no price history; see README).

select sku, product_name, category, unit, is_consumable, cost_eur, list_price_eur
from {{ ref('stg_erp__products') }}
