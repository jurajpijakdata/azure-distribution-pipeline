-- Order lines with product match, EUR amounts and validation.
-- Every line stays in this model; rejection_reasons explains what is wrong.
-- Valid lines (rejection_reasons IS NULL) continue to the star schema.

with orders as (

    select * from {{ ref('int_orders__deduplicated') }}

),

products as (

    select sku, unit as product_unit from {{ ref('stg_erp__products') }}

),

customers as (

    select customer_id from {{ ref('stg_erp__customers') }}

),

matched as (

    select
        o.*,
        p.sku                    as sku_standard,   -- official code, NULL if unknown
        c.customer_id            as customer_found,
        r.czk_per_eur
    from orders o
    left join products p
        on upper(o.sku) = upper(p.sku)              -- fixes case typos only
    left join customers c
        on o.customer_id = c.customer_id
    outer apply (
        -- ECB rate of the order day, or the latest earlier one
        select top 1 e.czk_per_eur
        from {{ ref('ecb_eur_czk') }} e
        where o.currency = 'CZK'
          and e.rate_date <= o.order_date
        order by e.rate_date desc
    ) r

),

validated as (

    select
        *,
        cast(case
            when currency = 'EUR' then unit_price
            when currency = 'CZK' then round(unit_price / czk_per_eur, 2)
        end as decimal(12, 2)) as unit_price_eur,
        cast(case
            when currency = 'EUR' then line_total
            when currency = 'CZK' then round(line_total / czk_per_eur, 2)
        end as decimal(14, 2)) as line_total_eur,
        nullif(concat_ws('; ',
            case when order_type is null then 'unknown order type' end,
            case when order_date is null then 'invalid order date: ' + order_date_raw end,
            case when quantity is null then 'invalid quantity: ' + quantity_raw end,
            case when order_type = 'SALE' and quantity < 0 then 'sale with negative quantity' end,
            case when unit_price is null then 'missing price' end,
            case when customer_id is null then 'missing customer' end,
            case when customer_id is not null and customer_found is null then 'unknown customer' end,
            case when sku_standard is null then 'unknown product: ' + sku_raw end
        ), '') as rejection_reasons
    from matched

)

select * from validated
