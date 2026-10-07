-- Staging model for Košice order lines (Excel export).

with source as (

    select * from {{ source('erp', 'orders_ke') }}

),

renamed as (

    select
        trim([Cislo objednavky])                            as order_no,
        try_convert(int, [Polozka])                         as line_no,
        case [Typ]
            when 'P' then 'SALE'
            when 'V' then 'RETURN'
        end                                                 as order_type,
        nullif(trim([Povodny doklad]), '')                  as original_order_no,
        try_convert(date, [Datum], 23)                      as order_date,
        [Datum]                                             as order_date_raw,
        trim([Sklad])                                       as warehouse_code,
        nullif(trim([Odberatel]), '')                       as customer_id,
        trim([Kod])                                         as sku,
        [Kod]                                               as sku_raw,
        cast(null as nvarchar(400))                         as product_name,
        try_convert(int, [Mnozstvo])                        as quantity,
        [Mnozstvo]                                          as quantity_raw,
        case [MJ] when 'ks' then 'pcs' else [MJ] end        as unit,
        try_convert(decimal(12, 2), [Cena])                 as unit_price,
        [Mena]                                              as currency,
        try_convert(decimal(14, 2), [Suma])                 as line_total,
        _source_file,
        _loaded_at
    from source

)

select * from renamed