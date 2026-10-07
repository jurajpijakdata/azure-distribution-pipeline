-- All shipments of the 4 warehouses, with unified carrier names and validation.
-- Valid shipments have rejection_reasons = NULL.

with unioned as (

    select * from {{ ref('stg_erp__shipments_ba') }}
    union all
    select * from {{ ref('stg_erp__shipments_za') }}
    union all
    select * from {{ ref('stg_erp__shipments_ke') }}
    union all
    select * from {{ ref('stg_erp__shipments_brn') }}

),

standardized as (

    select
        *,
        -- comparable form: uppercase, trimmed, no double spaces
        case replace(upper(trim(carrier_raw)), '  ', ' ')
            when 'OWN FLEET'     then 'Own fleet'
            when 'COURIER ALPHA' then 'Courier Alpha'
            when 'ALPHA'         then 'Courier Alpha'
            when 'COURIER BETA'  then 'Courier Beta'
            when 'BETA'          then 'Courier Beta'
        end as carrier_standard
    from unioned

),

orders as (

    select distinct order_no from {{ ref('int_orders__deduplicated') }}

),

validated as (

    select
        s.*,
        nullif(concat_ws('; ',
            case when s.carrier_standard is null then 'unknown carrier: ' + s.carrier_raw end,
            case when s.status is null then 'unknown status' end,
            case when s.ship_date is not null and s.delivered_date < s.ship_date
                 then 'delivered before shipped' end,
            case when o.order_no is null then 'shipment for unknown order' end
        ), '') as rejection_reasons
    from standardized s
    left join orders o
        on s.order_no = o.order_no

)

select * from validated