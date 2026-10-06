-- One-time database setup. Run as the Microsoft Entra admin.
-- Creates the staging schema and the Data Factory user with
-- the smallest permissions it needs (read/insert/delete in staging only).

CREATE SCHEMA staging;
GO

-- Managed identity of the Data Factory (no password).
CREATE USER [adf-distpipeline-jp] FROM EXTERNAL PROVIDER;
GO

-- DELETE is needed to reload a file without creating duplicates.
GRANT SELECT, INSERT, DELETE ON SCHEMA::staging TO [adf-distpipeline-jp];
GO