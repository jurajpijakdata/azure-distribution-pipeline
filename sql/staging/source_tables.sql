-- Staging tables for all warehouse exports and the customer master.
-- Each table mirrors ONE source format exactly: original column names, every
-- business column as text (NVARCHAR). Renaming, typing and cleaning happen
-- later in dbt. Lineage columns: _source_file, _loaded_at.
-- Safe to run more than once. Generated from data_generator/export.py.

-- orders - Bratislava (Slovak ERP, CSV ; UTF-8)
IF OBJECT_ID('staging.orders_ba') IS NULL
CREATE TABLE staging.orders_ba (
    [Číslo dokladu]   NVARCHAR(200),
    [Riadok]          NVARCHAR(200),
    [Typ dokladu]     NVARCHAR(200),
    [Pôvodný doklad]  NVARCHAR(200),
    [Dátum]           NVARCHAR(200),
    [Sklad]           NVARCHAR(200),
    [Zákazník]        NVARCHAR(200),
    [Kód tovaru]      NVARCHAR(200),
    [Názov tovaru]    NVARCHAR(400),
    [Množstvo]        NVARCHAR(200),
    [MJ]              NVARCHAR(200),
    [Jedn. cena]      NVARCHAR(200),
    [Mena]            NVARCHAR(200),
    [Spolu]           NVARCHAR(200),
    _source_file      NVARCHAR(400) NOT NULL,
    _loaded_at        DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- orders - Žilina (English ERP, CSV , UTF-8) - superset of the schema before/after 2026-03
IF OBJECT_ID('staging.orders_za') IS NULL
CREATE TABLE staging.orders_za (
    [order_id]      NVARCHAR(200),
    [line]          NVARCHAR(200),
    [doc_type]      NVARCHAR(200),
    [ref_order]     NVARCHAR(200),
    [date]          NVARCHAR(200),
    [warehouse]     NVARCHAR(200),
    [customer]      NVARCHAR(200),
    [item_code]     NVARCHAR(200),
    [qty]           NVARCHAR(200),
    [quantity]      NVARCHAR(200),
    [uom]           NVARCHAR(200),
    [price]         NVARCHAR(200),
    [currency]      NVARCHAR(200),
    [total]         NVARCHAR(200),
    [vat_rate]      NVARCHAR(200),
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- orders - Košice (Excel, Slovak without diacritics)
IF OBJECT_ID('staging.orders_ke') IS NULL
CREATE TABLE staging.orders_ke (
    [Cislo objednavky]  NVARCHAR(200),
    [Polozka]           NVARCHAR(200),
    [Typ]               NVARCHAR(200),
    [Povodny doklad]    NVARCHAR(200),
    [Datum]             NVARCHAR(200),
    [Sklad]             NVARCHAR(200),
    [Odberatel]         NVARCHAR(200),
    [Kod]               NVARCHAR(200),
    [Mnozstvo]          NVARCHAR(200),
    [MJ]                NVARCHAR(200),
    [Cena]              NVARCHAR(200),
    [Mena]              NVARCHAR(200),
    [Suma]              NVARCHAR(200),
    _source_file        NVARCHAR(400) NOT NULL,
    _loaded_at          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- orders - Brno (Czech ERP, CSV ; Windows-1250)
IF OBJECT_ID('staging.orders_brn') IS NULL
CREATE TABLE staging.orders_brn (
    [Číslo objednávky]  NVARCHAR(200),
    [Řádek]             NVARCHAR(200),
    [Typ dokladu]       NVARCHAR(200),
    [Původní doklad]    NVARCHAR(200),
    [Datum]             NVARCHAR(200),
    [Sklad]             NVARCHAR(200),
    [Odběratel]         NVARCHAR(200),
    [Kód zboží]         NVARCHAR(200),
    [Název zboží]       NVARCHAR(400),
    [Množství]          NVARCHAR(200),
    [MJ]                NVARCHAR(200),
    [Cena za jednotku]  NVARCHAR(200),
    [Měna]              NVARCHAR(200),
    [Celkem]            NVARCHAR(200),
    _source_file        NVARCHAR(400) NOT NULL,
    _loaded_at          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- shipments - Bratislava (Slovak ERP, CSV ; UTF-8)
IF OBJECT_ID('staging.shipments_ba') IS NULL
CREATE TABLE staging.shipments_ba (
    [Číslo zásielky]   NVARCHAR(200),
    [Číslo dokladu]    NVARCHAR(200),
    [Sklad]            NVARCHAR(200),
    [Dopravca]         NVARCHAR(200),
    [Dátum expedície]  NVARCHAR(200),
    [Sľúbený termín]   NVARCHAR(200),
    [Dátum doručenia]  NVARCHAR(200),
    [Stav]             NVARCHAR(200),
    _source_file       NVARCHAR(400) NOT NULL,
    _loaded_at         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- shipments - Žilina (English ERP, CSV , UTF-8)
IF OBJECT_ID('staging.shipments_za') IS NULL
CREATE TABLE staging.shipments_za (
    [shipment_id]   NVARCHAR(200),
    [order_id]      NVARCHAR(200),
    [warehouse]     NVARCHAR(200),
    [carrier]       NVARCHAR(200),
    [shipped]       NVARCHAR(200),
    [promised]      NVARCHAR(200),
    [delivered]     NVARCHAR(200),
    [status]        NVARCHAR(200),
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- shipments - Košice (Excel, Slovak without diacritics)
IF OBJECT_ID('staging.shipments_ke') IS NULL
CREATE TABLE staging.shipments_ke (
    [Zasielka]          NVARCHAR(200),
    [Cislo objednavky]  NVARCHAR(200),
    [Sklad]             NVARCHAR(200),
    [Prepravca]         NVARCHAR(200),
    [Odoslane]          NVARCHAR(200),
    [Termin]            NVARCHAR(200),
    [Dorucene]          NVARCHAR(200),
    [Stav]              NVARCHAR(200),
    _source_file        NVARCHAR(400) NOT NULL,
    _loaded_at          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- shipments - Brno (Czech ERP, CSV ; Windows-1250)
IF OBJECT_ID('staging.shipments_brn') IS NULL
CREATE TABLE staging.shipments_brn (
    [Číslo zásilky]     NVARCHAR(200),
    [Číslo objednávky]  NVARCHAR(200),
    [Sklad]             NVARCHAR(200),
    [Dopravce]          NVARCHAR(200),
    [Datum expedice]    NVARCHAR(200),
    [Slíbený termín]    NVARCHAR(200),
    [Datum doručení]    NVARCHAR(200),
    [Stav]              NVARCHAR(200),
    _source_file        NVARCHAR(400) NOT NULL,
    _loaded_at          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- inventory - Bratislava (Slovak ERP, CSV ; UTF-8)
IF OBJECT_ID('staging.inventory_ba') IS NULL
CREATE TABLE staging.inventory_ba (
    [Dátum]         NVARCHAR(200),
    [Sklad]         NVARCHAR(200),
    [Kód tovaru]    NVARCHAR(200),
    [Stav zásob]    NVARCHAR(200),
    [MJ]            NVARCHAR(200),
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- inventory - Žilina (English ERP, CSV , UTF-8)
IF OBJECT_ID('staging.inventory_za') IS NULL
CREATE TABLE staging.inventory_za (
    [date]          NVARCHAR(200),
    [warehouse]     NVARCHAR(200),
    [item_code]     NVARCHAR(200),
    [on_hand]       NVARCHAR(200),
    [uom]           NVARCHAR(200),
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- inventory - Košice (Excel, Slovak without diacritics)
IF OBJECT_ID('staging.inventory_ke') IS NULL
CREATE TABLE staging.inventory_ke (
    [Datum]         NVARCHAR(200),
    [Sklad]         NVARCHAR(200),
    [Kod]           NVARCHAR(200),
    [Mnozstvo]      NVARCHAR(200),
    [MJ]            NVARCHAR(200),
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- inventory - Brno (Czech ERP, CSV ; Windows-1250)
IF OBJECT_ID('staging.inventory_brn') IS NULL
CREATE TABLE staging.inventory_brn (
    [Datum]         NVARCHAR(200),
    [Sklad]         NVARCHAR(200),
    [Kód zboží]     NVARCHAR(200),
    [Stav skladu]   NVARCHAR(200),
    [MJ]            NVARCHAR(200),
    _source_file    NVARCHAR(400) NOT NULL,
    _loaded_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- customer master - HQ ERP (CSV ; UTF-8)
IF OBJECT_ID('staging.customers') IS NULL
CREATE TABLE staging.customers (
    [customer_id]          NVARCHAR(200),
    [customer_name]        NVARCHAR(400),
    [customer_type]        NVARCHAR(200),
    [street]               NVARCHAR(400),
    [postal_code]          NVARCHAR(200),
    [city]                 NVARCHAR(200),
    [country]              NVARCHAR(200),
    [email]                NVARCHAR(400),
    [home_warehouse_code]  NVARCHAR(200),
    [created_date]         NVARCHAR(200),
    _source_file           NVARCHAR(400) NOT NULL,
    _loaded_at             DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO
