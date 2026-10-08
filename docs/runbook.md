# Runbook

## SQL: "Client with IP address ... is not allowed to access the server"
**Cause:** home IP address changed (dynamic IP from the provider).
**Fix:** update the firewall rule with the current IP:
```powershell
$myip = (Invoke-RestMethod https://api.ipify.org)
az sql server firewall-rule create -g rg-distribution-pipeline -s sql-distpipeline-jp -n home-pc --start-ip-address $myip --end-ip-address $myip
```

## SQL: "Login failed for user '<token-identified principal>'"
**Cause (seen):** wrong database name in the connection. Azure SQL hides
whether a database exists, so a wrong name looks like a login failure.
**Fix:** use the real database name `free-sql-db-8791495`. Also check that
the Microsoft Entra tenant is "Default Directory".

## SQL: "Database ... is not currently available"
**Cause:** the serverless database is waking up from auto-pause.
**Fix:** wait 1–2 minutes and connect again. Not an error.

## Data Factory: "Debug" does nothing / "Validation of model(s) failed"
**Cause:** an object has a validation error (seen: a mapping row with an
empty source). Debug silently refuses to start.
**Fix:** click "Validate all" in the top bar, read the error, fix it.
Columns filled by a database DEFAULT must be removed from the mapping,
not left with an empty source.

## Staging: row count higher than the files contain
**Check:** group by `_source_file` and `_loaded_at` to see which rows are extra.
**Seen once:** leftovers from an old wildcard load with a corrupted
`_source_file` value ("23"). Delete those rows; current loads are per file.

## dbt debug: "Azure authentication requires the optional dependency 'azure-identity'"
**Fix:** `pip install azure-identity` (already in requirements.txt).
If it then asks to log in: run `az login` and try again.

## Data Factory: "SqlFailedToConnect ... timeout already expired"
**Cause:** the serverless database was paused (auto-pause) and did not wake up
in time for the first connection.
**Fix:** copy activities have Retry = 2, interval 60 s. If it still fails,
check the database status: `az sql db show ... --query status`.
