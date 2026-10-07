-- Deduplication must keep exactly one row per distinct order line:
-- the count after dedup must equal the number of distinct lines before.
with before_dedup as (
    select count(*) as n
    from (select distinct order_no, line_no from {{ ref('int_orders__unioned') }}) d
),
after_dedup as (
    select count(*) as n from {{ ref('int_orders__deduplicated') }}
)
select b.n as distinct_lines_in_source, a.n as lines_after_dedup
from before_dedup b
cross join after_dedup a
where b.n <> a.n