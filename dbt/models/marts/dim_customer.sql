-- Dimension: one row per customer.
-- Street and e-mail are left out on purpose: reporting does not need them
-- (data minimisation).

select
    customer_id,
    customer_name,
    customer_type,
    postal_code,
    city,
    country,
    home_warehouse_code,
    created_date
from {{ ref('stg_erp__customers') }}
