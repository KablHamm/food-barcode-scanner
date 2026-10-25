# Publish the Food Barcode Scanner project to a GitHub repository using the
# GitHub Contents API (no git required). Run from the project folder.
#
# Usage:
#   .\publish_to_github.ps1
# You will be prompted for your GitHub username, repo name, branch, and a
# Personal Access Token (classic) with "repo" scope.
# Create a token at: https://github.com/settings/tokens/new  (scope: repo)

param(
    [string]$Owner = "KablHamm",
    [string]$Repo  = "food-barcode-scanner",
    [string]$Branch = "main",
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"

Write-Host "GitHub publisher for Food Barcode Scanner" -ForegroundColor Cyan
$Owner  = Read-Host "GitHub username/owner [$Owner]";  if (-not $Owner)  { $Owner = "KablHamm" }
$Repo   = Read-Host "Repository name [$Repo]";         if (-not $Repo)   { $Repo = "food-barcode-scanner" }
$Branch = Read-Host "Branch [$Branch]";                if (-not $Branch) { $Branch = "main" }
if (-not $Token) {
    $Token  = Read-Host "Personal Access Token (repo scope)" -AsSecureString
    $TokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Token))
} else {
    $TokenPlain = $Token
}

if (-not $TokenPlain) { throw "Token is required." }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Headers = @{
    Authorization = "Bearer $TokenPlain"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

# Files/folders to skip
$skipDirs  = @(".certs", ".git")
$skipFiles = @()  # keep gen_icons.py etc.

function Get-RepoFiles($base) {
    Get-ChildItem -Path $base -Recurse -File | Where-Object {
        $rel = $_.FullName.Substring($base.Length + 1)
        $parts = $rel -split '\\'
        foreach ($d in $skipDirs) { if ($parts -contains $d) { return $false } }
        return $true
    }
}

$files = Get-RepoFiles $root
Write-Host "Found $($files.Count) files to upload." -ForegroundColor Green

foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length + 1) -replace '\\', '/'
    $content = [Convert]::ToBase64String([IO.File]::ReadAllBytes($f.FullName))
    $url = "https://api.github.com/repos/$Owner/$Repo/contents/$rel"

    $body = @{
        message = "Add $rel"
        content = $content
        branch  = $Branch
    } | ConvertTo-Json -Depth 5

    try {
        Invoke-RestMethod -Uri $url -Method Put -Headers $Headers -Body $body -ContentType "application/json" | Out-Null
        Write-Host "  uploaded: $rel" -ForegroundColor Gray
    } catch {
        # If file exists, fetch its sha and retry (update)
        try {
            $existing = Invoke-RestMethod -Uri "$url`?ref=$Branch" -Headers $Headers
            $bodyObj = @{
                message = "Update $rel"
                content = $content
                branch  = $Branch
                sha     = $existing.sha
            } | ConvertTo-Json -Depth 5
            Invoke-RestMethod -Uri $url -Method Put -Headers $Headers -Body $bodyObj -ContentType "application/json" | Out-Null
            Write-Host "  updated:  $rel" -ForegroundColor DarkGray
        } catch {
            Write-Host "  FAILED:   $rel  -> $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Done. View at: https://github.com/$Owner/$Repo" -ForegroundColor Cyan
Write-Host "Enable Pages: Settings -> Pages -> Source -> GitHub Actions" -ForegroundColor Yellow
