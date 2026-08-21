param(
    [Parameter(Mandatory = $true)]
    [string]$SendKey
)

Set-Location $PSScriptRoot

Write-Host "1/3 推送代码到 GitHub..."
git push -u origin main

Write-Host "2/3 配置 Server酱 SendKey..."
gh secret set SERVERCHAN_SENDKEY --repo Booom711/DailyPlan --body $SendKey

Write-Host "3/3 触发一次测试推送..."
gh workflow run "Daily Fitness Push" --repo Booom711/DailyPlan

Write-Host "完成。可以到 Actions 页面查看测试结果。"
