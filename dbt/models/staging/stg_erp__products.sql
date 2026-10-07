-- Staging model for the product master.
-- One row per product. Types converted from text; nothing filtered out.

with source as (

    select * from {{ source('erp', 'products') }}

),

renamed as (

    select
        trim(sku)                                                       as sku,
        trim(product_name)                                              as product_name,
        trim(category)                                                  as category,
        trim(unit)                                                      as unit,
        try_convert(bit, is_consumable)                                 as is_consumable,
        try_convert(decimal(12, 2), replace(cost_eur, ',', '.'))        as cost_eur,
        try_convert(decimal(12, 2), replace(list_price_eur, ',', '.'))  as list_price_eur,
        _source_file,
        _loaded_at
    from source

)

select * from renamed