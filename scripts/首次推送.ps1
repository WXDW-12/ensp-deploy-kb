# 首次推送到 GitHub（在有网、有账号的机器上执行一次）
# 用法：右键“使用 PowerShell 运行”，或命令行：
#   powershell -ExecutionPolicy Bypass -File scripts\首次推送.ps1 -RepoUrl https://github.com/你的账号/ensp-deploy-kb.git

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoUrl
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "仓库目录: $root" -ForegroundColor Cyan
Write-Host "目标远程: $RepoUrl" -ForegroundColor Cyan

# 已有 origin 就先改地址
$hasOrigin = (git remote get-url origin 2>$null)
if ($LASTEXITCODE -eq 0 -and $hasOrigin) {
    git remote set-url origin $RepoUrl
    Write-Host "已更新 origin" -ForegroundColor Yellow
} else {
    git remote add origin $RepoUrl
    Write-Host "已添加 origin" -ForegroundColor Green
}

git branch -M main
Write-Host ""
Write-Host "开始推送（首次会要求输入 GitHub 用户名和 Token/密码）..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "推送成功！以后用 tools\同步.bat 即可 pull/push。" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "推送失败，常见原因：" -ForegroundColor Red
    Write-Host "  1. 仓库还没在 GitHub 上创建（先在网页 New repository，不要勾 README）"
    Write-Host "  2. 密码要用 Personal Access Token（Settings -> Developer settings -> Tokens）"
    Write-Host "  3. 账号无该仓库权限"
}
Start-Sleep -Seconds 3