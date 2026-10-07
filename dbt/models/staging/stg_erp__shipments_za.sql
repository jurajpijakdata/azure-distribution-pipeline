-- Shipments, Žilina (English ERP). Dates yyyy-mm-dd, status already standard.
-- Carrier names are only trimmed here; spelling variants are unified later.

with source as (

    select * from {{ source('erp', 'shipments_za') }}

),

renamed as (

    select
        trim([shipment_id])                 as shipment_id,
        trim([order_id])                    as order_no,
        trim([warehouse])                   as warehouse_code,
        trim([carrier])                     as carrier,
        [carrier]                           as carrier_raw,
        try_convert(date, [shipped], 23)    as ship_date,
        try_convert(date, [promised], 23)   as promised_date,
        try_convert(date, [delivered], 23)  as delivered_date,
        [delivered]                         as delivered_date_raw,
        trim([status])                      as status,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
