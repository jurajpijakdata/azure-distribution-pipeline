-- Data quality: number of rejected rows per area, warehouse and reason.
-- The reason text before ':' is the category (e.g. 'invalid quantity').

with rejected as (

    select 'orders' as area, warehouse_code, rejection_reasons
    from {{ ref('int_orders__validated') }} where rejection_reasons is not null
    union all
    select 'shipments', warehouse_code, rejection_reasons
    from {{ ref('int_shipments__validated') }} where rejection_reasons is not null
    union all
    select 'inventory', warehouse_code, rejection_reasons
    from {{ ref('int_inventory__validated') }} where rejection_reasons is not null

)

select
    area,
    warehouse_code,
    case when charindex(':', rejection_reasons) > 0
         then left(rejection_reasons, charindex(':', rejection_reasons) - 1)
         else rejection_reasons
    end as reason,
    count(*) as rejected_rows
from rejected
group by
    area,
    warehouse_code,
    case when charindex(':', rejection_reasons) > 0
         then left(rejection_reasons, charindex(':', rejection_reasons) - 1)
         else rejection_reasons
    end