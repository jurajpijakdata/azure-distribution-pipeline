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