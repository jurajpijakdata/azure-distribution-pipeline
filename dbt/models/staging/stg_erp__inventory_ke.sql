-- Weekly stock snapshots, Košice (Excel export). One week is missing in the source.

with source as (

    select * from {{ source('erp', 'inventory_ke') }}

),

renamed as (

    select
        try_convert(date, [Datum], 23)                as snapshot_date,
        trim([Sklad])                                 as warehouse_code,
        trim([Kod])                                   as sku,
        try_convert(int, [Mnozstvo])                  as qty_on_hand,
        [Mnozstvo]                                    as qty_on_hand_raw,
        case [MJ] when 'ks' then 'pcs' else [MJ] end  as unit,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
