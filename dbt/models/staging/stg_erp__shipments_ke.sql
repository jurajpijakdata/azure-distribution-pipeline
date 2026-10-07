-- Shipments, Košice (Excel export). Dates yyyy-mm-dd.
-- Carrier names are only trimmed here; spelling variants are unified later.

with source as (

    select * from {{ source('erp', 'shipments_ke') }}

),

renamed as (

    select
        trim([Zasielka])                                                                    as shipment_id,
        trim([Cislo objednavky])                                                            as order_no,
        trim([Sklad])                                                                       as warehouse_code,
        trim([Prepravca])                                                                   as carrier,
        [Prepravca]                                                                         as carrier_raw,
        try_convert(date, [Odoslane], 23)                                                   as ship_date,
        try_convert(date, [Termin], 23)                                                     as promised_date,
        try_convert(date, [Dorucene], 23)                                                   as delivered_date,
        [Dorucene]                                                                          as delivered_date_raw,
        case [Stav] when 'Dorucene' then 'DELIVERED' when 'Na ceste' then 'IN_TRANSIT' end  as status,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
