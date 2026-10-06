-- Staging table for the product master file (master/products.csv).
-- All business columns are text: values are stored exactly as delivered,
-- cleaning happens later in dbt. Safe to run more than once.

IF OBJECT_ID('staging.products') IS NULL
CREATE TABLE staging.products (
    sku             NVARCHAR(100),
    product_name    NVARCHAR(400),
    category        NVARCHAR(200),
    unit            NVARCHAR(50),
    is_consumable   NVARCHAR(10),
    cost_eur        NVARCHAR(50),
    list_price_eur  NVARCHAR(50),
    -- lineage: where each row came from and when it was loaded
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);