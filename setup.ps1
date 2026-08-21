param(
    [Parameter(Mandatory = $true)]
    [string]$SendKey
)

Set-Location $PSScriptRoot

Write-Host "1/3 Pushing code to GitHub..."
git push -u origin main

Write-Host "2/3 Setting ServerChan SendKey..."
gh secret set SERVERCHAN_SENDKEY --repo Booom711/DailyPlan --body $SendKey

Write-Host "3/3 Triggering a test push..."
gh workflow run "Daily Fitness Push" --repo Booom711/DailyPlan

Write-Host "Done. Check the Actions page for the test run."
