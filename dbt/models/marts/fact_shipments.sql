-- Fact: one row per valid shipment.
-- delivery_delay_days = delivered - promised in calendar days (negative = early),
-- only for delivered shipments.

select
    shipment_id,
    order_no,
    warehouse_code,
    carrier_standard                                            as carrier,
    ship_date,
    promised_date,
    delivered_date,
    status,
    case when status = 'DELIVERED'
         then datediff(day, promised_date, delivered_date) end  as delivery_delay_days,
    case when status = 'DELIVERED'
         then case when delivered_date > promised_date then 1 else 0 end
    end                                                         as is_late
from {{ ref('int_shipments__validated') }}
where rejection_reasons is null
