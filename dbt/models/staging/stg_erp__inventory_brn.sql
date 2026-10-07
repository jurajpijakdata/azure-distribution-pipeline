-- Weekly stock snapshots, Brno. Dates dd.mm.yyyy, space as thousands separator.

with source as (

    select * from {{ source('erp', 'inventory_brn') }}

),

renamed as (

    select
        try_convert(date, [Datum], 104)                    as snapshot_date,
        trim([Sklad])                                      as warehouse_code,
        trim([Kód zboží])                                  as sku,
        try_convert(int, replace([Stav skladu], ' ', ''))  as qty_on_hand,
        [Stav skladu]                                      as qty_on_hand_raw,
        case [MJ] when 'ks' then 'pcs' else [MJ] end       as unit,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
