-- Shipments, Bratislava (Slovak ERP). Dates dd.mm.yyyy.
-- Carrier names are only trimmed here; spelling variants are unified later.

with source as (

    select * from {{ source('erp', 'shipments_ba') }}

),

renamed as (

    select
        trim([Číslo zásielky])                                                              as shipment_id,
        trim([Číslo dokladu])                                                               as order_no,
        trim([Sklad])                                                                       as warehouse_code,
        trim([Dopravca])                                                                    as carrier,
        [Dopravca]                                                                          as carrier_raw,
        try_convert(date, [Dátum expedície], 104)                                           as ship_date,
        try_convert(date, [Sľúbený termín], 104)                                            as promised_date,
        try_convert(date, [Dátum doručenia], 104)                                           as delivered_date,
        [Dátum doručenia]                                                                   as delivered_date_raw,
        case [Stav] when 'Doručené' then 'DELIVERED' when 'Na ceste' then 'IN_TRANSIT' end  as status,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
