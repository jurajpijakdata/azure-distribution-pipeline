-- One-time database setup. Run as the Microsoft Entra admin.
-- Safe to run more than once: each step checks if it is already done.

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'staging')
    EXEC('CREATE SCHEMA staging');
GO

-- Managed identity of the Data Factory (no password).
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'adf-distpipeline-jp')
    CREATE USER [adf-distpipeline-jp] FROM EXTERNAL PROVIDER;
GO

-- DELETE is needed to reload a file without creating duplicates.
-- GRANT is naturally safe to repeat.
GRANT SELECT, INSERT, DELETE ON SCHEMA::staging TO [adf-distpipeline-jp];
GO