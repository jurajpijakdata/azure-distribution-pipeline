-- Shipments, Brno (Czech ERP). Dates dd.mm.yyyy.
-- Carrier names are only trimmed here; spelling variants are unified later.

with source as (

    select * from {{ source('erp', 'shipments_brn') }}

),

renamed as (

    select
        trim([Číslo zásilky])                                                                 as shipment_id,
        trim([Číslo objednávky])                                                              as order_no,
        trim([Sklad])                                                                         as warehouse_code,
        trim([Dopravce])                                                                      as carrier,
        [Dopravce]                                                                            as carrier_raw,
        try_convert(date, [Datum expedice], 104)                                              as ship_date,
        try_convert(date, [Slíbený termín], 104)                                              as promised_date,
        try_convert(date, [Datum doručení], 104)                                              as delivered_date,
        [Datum doručení]                                                                      as delivered_date_raw,
        case [Stav] when N'Doručeno' then 'DELIVERED' when N'V přepravě' then 'IN_TRANSIT' end as status,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
