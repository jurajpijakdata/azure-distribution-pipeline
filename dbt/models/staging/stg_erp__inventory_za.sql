-- Weekly stock snapshots, Žilina. Dates yyyy-mm-dd.

with source as (

    select * from {{ source('erp', 'inventory_za') }}

),

renamed as (

    select
        try_convert(date, [date], 23)                   as snapshot_date,
        trim([warehouse])                               as warehouse_code,
        trim([item_code])                               as sku,
        try_convert(int, [on_hand])                     as qty_on_hand,
        [on_hand]                                       as qty_on_hand_raw,
        case [uom] when 'ks' then 'pcs' else [uom] end  as unit,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
