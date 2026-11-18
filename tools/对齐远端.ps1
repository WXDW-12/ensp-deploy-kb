# 对齐本地 git 历史与 GitHub 远端（网络恢复后执行一次）
# 背景：远端部分提交是用 API 直接写的，本地历史与远端没有共同祖先，git push 会被拒。
# 这个脚本保留本地文件内容，只把历史对齐到远端，然后重新提交并推送。

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "仓库目录: $root" -ForegroundColor Cyan

Write-Host "`n[1/5] 备份当前本地提交" -ForegroundColor Cyan
$stamp = Get-Date -Format 'yyyyMMdd-HHmm'
git branch -f "local-backup-$stamp" 2>$null | Out-Null
Write-Host "  已建分支 local-backup-$stamp"

Write-Host "`n[2/5] 拉取远端" -ForegroundColor Cyan
git -c http.version=HTTP/1.1 fetch origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  fetch 失败：GitHub 仍不可达，稍后再试" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/5] 历史对齐到远端（本地文件保留在工作区）" -ForegroundColor Cyan
git reset --soft origin/main

Write-Host "`n[4/5] 提交本地差异" -ForegroundColor Cyan
git add -A
git -c user.name="eNSP KB" -c user.email="kb@local" commit -m "本地：问题4-6、命令库、工具（对齐远端后补提交）"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  没有需要提交的差异" -ForegroundColor Yellow
}

Write-Host "`n[5/5] 推送" -ForegroundColor Cyan
git -c http.version=HTTP/1.1 push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n完成：本地与远端已对齐，以后可直接 git push" -ForegroundColor Green
    Write-Host "如需回滚：git reset --hard local-backup-$stamp" -ForegroundColor DarkGray
} else {
    Write-Host "`n推送失败：检查网络/凭据；本地提交已保留" -ForegroundColor Red
}
Start-Sleep -Seconds 3