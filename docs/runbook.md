# Runbook

## SQL: "Client with IP address ... is not allowed to access the server"
**Cause:** home IP address changed (dynamic IP from the provider).
**Fix:** update the firewall rule with the current IP:
```powershell
$myip = (Invoke-RestMethod https://api.ipify.org)
az sql server firewall-rule create -g rg-distribution-pipeline -s sql-distpipeline-jp -n home-pc --start-ip-address $myip --end-ip-address $myip
```