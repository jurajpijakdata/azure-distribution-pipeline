-- Weekly stock snapshots of all warehouses with validation.
-- Valid rows have rejection_reasons = NULL.

with unioned as (

    select * from {{ ref('stg_erp__inventory_ba') }}
    union all
    select * from {{ ref('stg_erp__inventory_za') }}
    union all
    select * from {{ ref('stg_erp__inventory_ke') }}
    union all
    select * from {{ ref('stg_erp__inventory_brn') }}

),

products as (

    select sku from {{ ref('stg_erp__products') }}

)

select
    i.*,
    p.sku as sku_standard,
    nullif(concat_ws('; ',
        case when i.snapshot_date is null then 'invalid snapshot date' end,
        case when i.qty_on_hand is null then 'invalid quantity: ' + i.qty_on_hand_raw end,
        case when i.qty_on_hand < 0 then 'negative stock' end,
        case when p.sku is null then 'unknown product: ' + i.sku end
    ), '') as rejection_reasons
from unioned i
left join products p
    on upper(i.sku) = upper(p.sku)