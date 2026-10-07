-- Staging model for Bratislava order lines (Slovak ERP export).
-- One row per line in the export. Duplicates are NOT removed here.
-- Columns that can fail conversion keep their raw text in *_raw columns,
-- so bad values stay visible and testable.

with source as (

    select * from {{ source('erp', 'orders_ba') }}

),

renamed as (

    select
        trim([Číslo dokladu])                                   as order_no,
        try_convert(int, [Riadok])                              as line_no,
        case [Typ dokladu]
            when 'Predaj'   then 'SALE'
            when 'Vrátenie' then 'RETURN'
        end                                                     as order_type,
        nullif(trim([Pôvodný doklad]), '')                      as original_order_no,
        try_convert(date, [Dátum], 104)                         as order_date,
        [Dátum]                                                 as order_date_raw,
        trim([Sklad])                                           as warehouse_code,
        nullif(trim([Zákazník]), '')                            as customer_id,
        trim([Kód tovaru])                                      as sku,
        [Kód tovaru]                                            as sku_raw,
        trim([Názov tovaru])                                    as product_name,
        try_convert(int, [Množstvo])                            as quantity,
        [Množstvo]                                              as quantity_raw,
        case [MJ] when 'ks' then 'pcs' else [MJ] end            as unit,
        try_convert(decimal(12, 2), replace([Jedn. cena], ',', '.')) as unit_price,
        [Mena]                                                  as currency,
        try_convert(decimal(14, 2), replace([Spolu], ',', '.'))      as line_total,
        _source_file,
        _loaded_at
    from source

)

select * from renamed