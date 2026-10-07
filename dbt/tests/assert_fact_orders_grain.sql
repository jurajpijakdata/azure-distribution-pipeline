-- Grain of fact_orders: one row per order line.
select order_no, line_no, count(*) as n
from {{ ref('fact_orders') }}
group by order_no, line_no
having count(*) > 1
