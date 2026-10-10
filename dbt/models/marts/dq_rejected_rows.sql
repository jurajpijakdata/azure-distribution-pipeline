-- Data quality: one row per rejected record, from orders, shipments and inventory.
-- Built for the client: each row identifies the record as the ERP does
-- (document + line for orders, shipment number, product + date for stock)
-- and says why it was rejected, so it can be fixed at the source.

select
    'orders'                         as area,
    warehouse_code,
    _source_file                     as source_file,
    order_no                         as document,
    line_no                          as line,
    cast(null as nvarchar(200))      as related_order,
    sku_raw                          as product,
    order_date_raw                   as record_date,
    rejection_reasons                as reason
from {{ ref('int_orders__validated') }}
where rejection_reasons is not null

union all

select
    'shipments',
    warehouse_code,
    _source_file,
    shipment_id,
    cast(null as int),
    order_no,
    cast(null as nvarchar(200)),
    delivered_date_raw,
    rejection_reasons
from {{ ref('int_shipments__validated') }}
where rejection_reasons is not null

union all

select
    'inventory',
    warehouse_code,
    _source_file,
    cast(null as nvarchar(200)),
    cast(null as int),
    cast(null as nvarchar(200)),
    sku,
    convert(nvarchar(10), snapshot_date, 23),
    rejection_reasons
from {{ ref('int_inventory__validated') }}
where rejection_reasons is not null
