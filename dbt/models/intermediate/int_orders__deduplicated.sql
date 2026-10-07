-- One row per order line (order_no + line_no).
-- Removes exact duplicate rows and lines exported twice (re-exported files).
-- If a line appears in several files, the copy from the original file wins.

with numbered as (

    select
        *,
        row_number() over (
            partition by order_no, line_no
            order by
                case when _source_file like '%reexport%' then 1 else 0 end,
                _source_file,
                _loaded_at
        ) as copy_number,
        count(*) over (partition by order_no, line_no) as copies_in_source
    from {{ ref('int_orders__unioned') }}

)

select *
from numbered
where copy_number = 1