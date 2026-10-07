-- Every warehouse must have a stock snapshot every Friday in the data range.
-- Returns each (warehouse, Friday) without any snapshot.
-- Severity warn: a missing week is reported, but does not stop the pipeline.
{{ config(severity='warn') }}

with recursive_fridays as (
    select min(snapshot_date) as friday, max(snapshot_date) as last_friday
    from {{ ref('int_inventory__validated') }}
    union all
    select dateadd(day, 7, friday), last_friday
    from recursive_fridays
    where friday < last_friday
),
warehouses as (
    select distinct warehouse_code from {{ ref('int_inventory__validated') }}
),
expected as (
    select w.warehouse_code, f.friday
    from warehouses w cross join recursive_fridays f
)
select e.warehouse_code, e.friday as missing_snapshot_date
from expected e
left join {{ ref('int_inventory__validated') }} i
    on i.warehouse_code = e.warehouse_code and i.snapshot_date = e.friday
where i.warehouse_code is null