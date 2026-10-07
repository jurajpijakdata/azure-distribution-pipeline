-- Staging model for Brno order lines (Czech ERP export, Windows-1250, CZK).
-- Numbers use a space as thousands separator and a comma as decimal mark
-- (e.g. "12 345,60"), so spaces are removed before converting.

with source as (

    select * from {{ source('erp', 'orders_brn') }}

),

renamed as (

    select
        trim([Číslo objednávky])                            as order_no,
        try_convert(int, [Řádek])                           as line_no,
        case [Typ dokladu]
            when 'Prodej' then 'SALE'
            when 'Vratka' then 'RETURN'
        end                                                 as order_type,
        nullif(trim([Původní doklad]), '')                  as original_order_no,
        try_convert(date, [Datum], 104)                     as order_date,
        [Datum]                                             as order_date_raw,
        trim([Sklad])                                       as warehouse_code,
        nullif(trim([Odběratel]), '')                       as customer_id,
        trim([Kód zboží])                                   as sku,
        [Kód zboží]                                         as sku_raw,
        trim([Název zboží])                                 as product_name,
        try_convert(int, replace([Množství], ' ', ''))      as quantity,
        [Množství]                                          as quantity_raw,
        case [MJ] when 'ks' then 'pcs' else [MJ] end        as unit,
        try_convert(decimal(12, 2),
            replace(replace([Cena za jednotku], ' ', ''), ',', '.'))  as unit_price,
        [Měna]                                              as currency,
        try_convert(decimal(14, 2),
            replace(replace([Celkem], ' ', ''), ',', '.'))            as line_total,
        _source_file,
        _loaded_at
    from source

)

select * from renamed