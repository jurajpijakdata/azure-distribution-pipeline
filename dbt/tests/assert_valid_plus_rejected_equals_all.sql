-- Every unique order line is either valid or rejected - never lost, never both.
with counts as (
    select
        (select count(*) from {{ ref('int_orders__deduplicated') }})                    as all_lines,
        (select count(*) from {{ ref('int_orders__validated') }}
            where rejection_reasons is null)                                           as valid_lines,
        (select count(*) from {{ ref('int_orders__rejected') }})                        as rejected_lines
)
select *
from counts
where all_lines <> valid_lines + rejected_lines