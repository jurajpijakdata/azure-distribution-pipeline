-- Dimension: one row per calendar day, 2025-09-01 to 2026-12-31.
-- Weekday numbers do not depend on server settings: Monday = 1 ... Sunday = 7.

with numbers as (

    select top (datediff(day, '2025-09-01', '2026-12-31') + 1)
        row_number() over (order by (select null)) - 1 as n
    from sys.all_objects a
    cross join sys.all_objects b

),

dates as (

    select dateadd(day, n, cast('2025-09-01' as date)) as date_day
    from numbers

)

select
    date_day,
    year(date_day)                                   as year,
    datepart(quarter, date_day)                      as quarter,
    month(date_day)                                  as month_number,
    datename(month, date_day)                        as month_name,
    format(date_day, 'yyyy-MM')                      as year_month,
    datepart(iso_week, date_day)                     as iso_week,
    (datediff(day, '19000101', date_day) % 7) + 1    as weekday_number,
    datename(weekday, date_day)                      as weekday_name,
    case when (datediff(day, '19000101', date_day) % 7) + 1 >= 6
         then 1 else 0 end                           as is_weekend
from dates
