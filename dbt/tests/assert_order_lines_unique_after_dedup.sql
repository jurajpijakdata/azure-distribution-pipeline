-- After deduplication every order line (order_no + line_no) must exist once.
select order_no, line_no, count(*) as copies
from {{ ref('int_orders__deduplicated') }}
group by order_no, line_no
having count(*) > 1