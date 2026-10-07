-- Weekly stock snapshots, Bratislava. Dates dd.mm.yyyy.

with source as (

    select * from {{ source('erp', 'inventory_ba') }}

),

renamed as (

    select
        try_convert(date, [Dátum], 104)               as snapshot_date,
        trim([Sklad])                                 as warehouse_code,
        trim([Kód tovaru])                            as sku,
        try_convert(int, [Stav zásob])                as qty_on_hand,
        [Stav zásob]                                  as qty_on_hand_raw,
        case [MJ] when 'ks' then 'pcs' else [MJ] end  as unit,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
