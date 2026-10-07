-- Staging model for Žilina order lines (English ERP export).
-- Schema change from 2026-03: 'qty' became 'quantity' and 'vat_rate' was added.
-- Both versions are handled here, so later models see one clean column.

with source as (

    select * from {{ source('erp', 'orders_za') }}              

),

renamed as (

    select
        trim([order_id])                                    as order_no,
        try_convert(int, [line])                            as line_no,
        [doc_type]                                          as order_type,        
        nullif(trim([ref_order]), '')                       as original_order_no,
        try_convert(date, [date], 23)                       as order_date,         
        [date]                                              as order_date_raw,
        trim([warehouse])                                   as warehouse_code,
        nullif(trim([customer]), '')                        as customer_id,
        trim([item_code])                                   as sku,
        [item_code]                                         as sku_raw,
        cast(null as nvarchar(400))                         as product_name,      
        try_convert(int, coalesce([quantity], [qty]))       as quantity,        
        coalesce([quantity], [qty])                         as quantity_raw,
        [uom]                                               as unit,               
        try_convert(decimal(12, 2), [price])                as unit_price,        
        [currency]                                          as currency,
        try_convert(decimal(14, 2), [total])                as line_total,
        try_convert(decimal(5, 2), [vat_rate])              as vat_rate,           
        _source_file,
        _loaded_at
    from source

)

select * from renamed