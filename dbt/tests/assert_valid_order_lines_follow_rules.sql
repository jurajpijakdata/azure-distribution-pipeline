-- A line marked valid (no rejection reason) must really satisfy every rule.
-- If this returns rows, the validation logic in int_orders__validated has a gap.
select *
from {{ ref('int_orders__validated') }}
where rejection_reasons is null
  and (
        order_date is null
     or quantity is null
     or (order_type = 'SALE' and quantity < 0)
     or unit_price is null
     or customer_found is null
     or sku_standard is null
     or (currency = 'CZK' and czk_per_eur is null)
  )