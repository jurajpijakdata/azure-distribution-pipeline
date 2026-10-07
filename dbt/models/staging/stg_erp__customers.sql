-- Customer master from the HQ ERP. One row per customer. Dates dd.mm.yyyy.

with source as (

    select * from {{ source('erp', 'customers') }}

),

renamed as (

    select
        trim(customer_id)                     as customer_id,
        trim(customer_name)                   as customer_name,
        trim(customer_type)                   as customer_type,
        trim(street)                          as street,
        trim(postal_code)                     as postal_code,
        trim(city)                            as city,
        trim(country)                         as country,
        trim(email)                           as email,
        trim(home_warehouse_code)             as home_warehouse_code,
        try_convert(date, created_date, 104)  as created_date,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
