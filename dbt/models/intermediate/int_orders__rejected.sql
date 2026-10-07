-- Quarantine: order lines that failed validation, with the reason.
-- Meant for the client: each row shows where the line came from and what
-- the ERP sent, so it can be corrected at the source.

select
    warehouse_code,
    _source_file      as source_file,
    order_no,
    line_no,
    order_type,
    order_date_raw,
    customer_id,
    sku_raw,
    quantity_raw,
    unit_price,
    rejection_reasons,
    _loaded_at        as loaded_at
from {{ ref('int_orders__validated') }}
where rejection_reasons is not null