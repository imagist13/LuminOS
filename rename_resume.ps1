# LuminOS rename script - resilient version
$ErrorActionPreference = 'Continue'
$root = (Get-Location).Path
$patterns = @(
  @{ old='luminos'; new='luminos' },
  @{ old='Lumin'; new='Lumin' },
  @{ old='LUMINOS'; new='LUMINOS' },
  @{ old='LuminOS'; new='LuminOS' }
)
$excludeDirs = @('.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build')
$excludeExts = @('.lock', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.db', '.sqlite', '.svg', '.woff', '.woff2', '.ttf', '.otf', '.eot', '.mp3', '.mp4', '.zip', '.tar', '.gz', '.7z', '.rar', '.exe', '.dll', '.so', '.dylib', '.bin')

$sep = [System.IO.Path]::DirectorySeparatorChar
$totalFiles = 0
$totalReplacements = 0
$skippedNull = 0
$skippedEncoding = 0
$skippedExcluded = 0
$skippedAlreadyDone = 0
$errorFiles = @()

# Only process files NOT yet modified by git
$allFiles = Get-ChildItem -Recurse -File
foreach ($file in $allFiles) {
  $path = $file.FullName
  $rel = $path.Substring($root.Length + 1)

  # Already modified? skip.
  $gitStatus = & git status --short -- $rel 2>$null
  if ($gitStatus -and $gitStatus.Length -gt 0 -and $gitStatus[0] -match '^.M') {
    $skippedAlreadyDone++
    continue
  }

  # Check excluded dirs
  $excluded = $false
  foreach ($d in $excludeDirs) {
    if ($path.Contains($sep + $d + $sep)) { $excluded = $true; $skippedExcluded++; break }
  }
  if ($excluded) { continue }

  # Check excluded extensions
  foreach ($e in $excludeExts) {
    if ($path.ToLower().EndsWith($e)) { $excluded = $true; $skippedExcluded++; break }
  }
  if ($excluded) { continue }

  # Read content
  try {
    $content = Get-Content -LiteralPath $path -Raw -Encoding UTF8 -ErrorAction Stop
  } catch {
    $skippedEncoding++
    continue
  }

  if ($null -eq $content -or $content.Length -eq 0) {
    $skippedNull++
    continue
  }

  # Apply replacements
  $fileHits = 0
  $newContent = $content
  foreach ($p in $patterns) {
    $count = ([regex]::Matches($newContent, [regex]::Escape($p.old))).Count
    if ($count -gt 0) {
      $newContent = $newContent.Replace($p.old, $p.new)
      $fileHits += $count
    }
  }

  if ($fileHits -gt 0) {
    try {
      Set-Content -LiteralPath $path -Value $newContent -NoNewline -Encoding UTF8 -ErrorAction Stop
      $totalFiles++
      $totalReplacements += $fileHits
      Write-Host ("{0,-6} {1}" -f $fileHits, $rel)
    } catch {
      $errorFiles += $rel
      Write-Host "ERROR: $rel - $($_.Exception.Message)"
    }
  }
}

Write-Host ""
Write-Host "=== Summary ==="
Write-Host ("Modified: {0} files, {1} replacements" -f $totalFiles, $totalReplacements)
Write-Host ("Skipped already done: {0}" -f $skippedAlreadyDone)
Write-Host ("Skipped null/empty: {0}" -f $skippedNull)
Write-Host ("Skipped encoding: {0}" -f $skippedEncoding)
Write-Host ("Skipped excluded: {0}" -f $skippedExcluded)
if ($errorFiles.Count -gt 0) {
  Write-Host ("Errors: {0}" -f $errorFiles.Count)
  foreach ($e in $errorFiles) { Write-Host "  - $e" }
}