-- Data quality: one row per rejected record, from orders, shipments and inventory.
-- Built for the client: each row says where it came from (source file and
-- record) and why it was rejected, so it can be fixed at the source.

select
    'orders'                                                    as area,
    warehouse_code,
    _source_file                                                as source_file,
    order_no + ' / line ' + cast(line_no as nvarchar(10))       as record,
    rejection_reasons                                           as reason
from {{ ref('int_orders__validated') }}
where rejection_reasons is not null

union all

select
    'shipments',
    warehouse_code,
    _source_file,
    shipment_id + ' (order ' + order_no + ')',
    rejection_reasons
from {{ ref('int_shipments__validated') }}
where rejection_reasons is not null

union all

select
    'inventory',
    warehouse_code,
    _source_file,
    sku + ' on ' + convert(nvarchar(10), snapshot_date, 23),
    rejection_reasons
from {{ ref('int_inventory__validated') }}
where rejection_reasons is not null
