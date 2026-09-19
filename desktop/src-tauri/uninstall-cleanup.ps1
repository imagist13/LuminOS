param(
    [string]$AppRoot,
    [string]$DetachedRuntime,
    [int]$DeleteData = 0,
    [switch]$ValidateOnly
)
$ErrorActionPreference = 'Stop'

# Entries whose deletion failed in the current pass (locked by a process that is
# still exiting, or transiently busy). They are retried before giving up.
$script:cleanupFailures = New-Object 'System.Collections.Generic.List[string]'
$script:cleanupRetries = 6
$script:cleanupRetryDelaySeconds = 5

function Get-LuminOSNativePath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if ($full.StartsWith('\\?\')) { return $full }
    if ($full.StartsWith('\\')) { return '\\?\UNC\' + $full.Substring(2) }
    return '\\?\' + $full
}

function Assert-LuminOSPlainPath([string]$Path) {
    # Check every existing ancestor before NSIS accesses local-server/data.
    # Reject redirected roots instead of operating on another directory tree.
    $current = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    while ($current) {
        try {
            $attrs = [IO.File]::GetAttributes((Get-LuminOSNativePath $current))
            if (($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Refusing redirected cleanup path: $current"
            }
        } catch [IO.FileNotFoundException] {
        } catch [IO.DirectoryNotFoundException] {
        }
        $current = [IO.Path]::GetDirectoryName($current)
    }
}

function Assert-LuminOSCleanupRoot([string]$Root) {
    if (-not $Root -or -not [IO.Path]::IsPathRooted($Root)) { throw 'Cleanup root must be absolute' }
    $full = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    if ([IO.Path]::GetFileName($full) -ne 'com.luminos.desktop') { throw 'Unexpected application root' }
    Assert-LuminOSPlainPath $full
    Assert-LuminOSPlainPath (Join-Path $full 'local-server')
}

function Stop-LuminOSRuntimeProcesses([string]$Root) {
    # Every process still executing a binary from inside the application root
    # belongs to this product (server, script runner, MCP servers, or orphans a
    # crashed server left behind). They hold the runtime files open; end them
    # with their children before deleting. Nothing outside the root is touched.
    $prefix = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $processes = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ExecutablePath -and [IO.Path]::GetFullPath($_.ExecutablePath).StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
    })
    foreach ($process in $processes) {
        & taskkill.exe /PID $process.ProcessId /T /F 2>$null | Out-Null
    }
    if ($processes.Count -gt 0) { Start-Sleep -Milliseconds 500 }
}

function Remove-LuminOSEntry([string]$Path, [string]$Root) {
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    if (-not $full.StartsWith($Root + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Cleanup entry escaped application root'
    }
    # This function never recursively enumerates a reparse point. A junction
    # is removed with Directory.Delete(path, false), which removes only the link.
    $native = Get-LuminOSNativePath $full
    try { $attrs = [IO.File]::GetAttributes($native) }
    catch [IO.FileNotFoundException] { return }
    catch [IO.DirectoryNotFoundException] { return }
    try {
        if (($attrs -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            if (($attrs -band [IO.FileAttributes]::Directory) -ne 0) { [IO.Directory]::Delete($native, $false) }
            else { [IO.File]::Delete($native) }
            return
        }
        if (($attrs -band [IO.FileAttributes]::Directory) -ne 0) {
            foreach ($child in [IO.Directory]::GetFileSystemEntries($native)) {
                # Strip the extended prefix before comparing lexical containment.
                $childPath = if ($child.StartsWith('\\?\UNC\')) { '\\' + $child.Substring(8) }
                    elseif ($child.StartsWith('\\?\')) { $child.Substring(4) } else { $child }
                Remove-LuminOSEntry $childPath $Root
            }
            [IO.Directory]::Delete($native, $false)
        } else {
            if (($attrs -band [IO.FileAttributes]::ReadOnly) -ne 0) {
                [IO.File]::SetAttributes($native, ($attrs -band (-bnot [IO.FileAttributes]::ReadOnly)))
            }
            [IO.File]::Delete($native)
        }
    } catch [IO.IOException] {
        # Busy or locked: keep going and retry this entry later instead of
        # abandoning the whole runtime directory on the first locked file.
        $script:cleanupFailures.Add($full)
    } catch [UnauthorizedAccessException] {
        $script:cleanupFailures.Add($full)
    }
}

function Remove-LuminOSEntries([string[]]$Paths, [string]$Root) {
    $script:cleanupFailures.Clear()
    foreach ($path in $Paths) { Remove-LuminOSEntry $path $Root }
    for ($attempt = 1; $attempt -le $script:cleanupRetries -and $script:cleanupFailures.Count -gt 0; $attempt++) {
        Start-Sleep -Seconds $script:cleanupRetryDelaySeconds
        Stop-LuminOSRuntimeProcesses $Root
        $retry = @($script:cleanupFailures)
        $script:cleanupFailures.Clear()
        foreach ($path in $retry) { Remove-LuminOSEntry $path $Root }
    }
    if ($script:cleanupFailures.Count -gt 0) {
        throw ("Cleanup left {0} locked entries, first: {1}" -f $script:cleanupFailures.Count, $script:cleanupFailures[0])
    }
}

function Invoke-LuminOSCleanup([string]$AppRoot, [string]$DetachedRuntime, [bool]$DeleteUserData) {
    Assert-LuminOSCleanupRoot $AppRoot
    $root = [IO.Path]::GetFullPath($AppRoot).TrimEnd('\')
    $detached = [IO.Path]::GetFullPath($DetachedRuntime).TrimEnd('\')
    if ([IO.Path]::GetDirectoryName($detached) -ne $root -or
        -not ([IO.Path]::GetFileName($detached)).StartsWith('remove-', [StringComparison]::Ordinal)) {
        throw 'Detached runtime must be a dedicated direct child of the application root'
    }
    Stop-LuminOSRuntimeProcesses $root
    $targets = @($detached)
    if ($DeleteUserData) {
        # These are the v2 user-managed top-level stores. Preserve all by default.
        foreach ($name in @('skills', 'plugins', 'agents', 'mcp.json', '.capabilities')) {
            $targets += (Join-Path $root $name)
        }
    }
    Remove-LuminOSEntries $targets $root
}

# Dot-sourcing exposes the same file-operation functions to isolated fixtures.
if ($MyInvocation.InvocationName -ne '.') {
    try {
        if ($ValidateOnly) { Assert-LuminOSCleanupRoot $AppRoot }
        else { Invoke-LuminOSCleanup $AppRoot $DetachedRuntime ($DeleteData -eq 1) }
        exit 0
    } catch {
        Write-Error $_
        exit 1
    }
}
