param(
    [ValidateSet('ImportIG','ImportGap','ImportStress','ImportStressGap')]
    [string]$Expert = 'ImportIG'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$terminalData = 'C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58'
$terminal = 'C:\Program Files\IG Markets MetaTrader 5 Terminal\terminal64.exe'
$editor = 'C:\Program Files\IG Markets MetaTrader 5 Terminal\MetaEditor64.exe'
if (Get-Process terminal64 -ErrorAction SilentlyContinue) { throw 'Close MT5 before importing.' }
$link = Join-Path $env:APPDATA 'MetaQuotes\Terminal\Common\Files\GBP100'
$data = Join-Path $root 'data\replay'
if (-not (Test-Path -LiteralPath $link)) {
    New-Item -ItemType Junction -Path $link -Target $data | Out-Null
} else {
    $item = Get-Item -LiteralPath $link
    $linkedTarget = [string]($item.Target | Select-Object -First 1)
    if ($item.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath($linkedTarget) -ne [IO.Path]::GetFullPath($data)) {
        throw 'The existing GBP100 common-files junction points elsewhere; inspect it before importing.'
    }
}
$destination = Join-Path $terminalData "MQL5\Experts\$Expert.mq5"
Copy-Item -LiteralPath (Join-Path $root "src\$Expert.mq5") -Destination $destination -Force
Start-Process $editor -ArgumentList "/compile:`"$destination`" /log" -Wait -WindowStyle Hidden
$log = Get-Content ([IO.Path]::ChangeExtension($destination,'.log'))
if (-not ($log -match 'Result: 0 errors, 0 warnings')) { throw 'Importer compilation failed.' }
$config = Join-Path $root "config\run-$Expert.ini"
@"
[Experts]
Enabled=1
AllowLiveTrading=0
[StartUp]
Expert=$Expert.ex5
Symbol=USDJPY
Period=H1
ShutdownTerminal=1
"@ | Set-Content -LiteralPath $config -Encoding ASCII
Start-Process $terminal -ArgumentList "/config:`"$config`"" -Wait -WindowStyle Hidden
$subdir = if ($Expert -in @('ImportGap','ImportStressGap')) {'Gap'} else {'USDJPY'}
$filename = if ($Expert.StartsWith('ImportStress')) {'stress-import-result.txt'} else {'import-result.txt'}
$result = Get-Content -LiteralPath (Join-Path $data "$subdir\$filename")
if ($result -match 'ERROR' -or $result[-1] -ne 'IMPORT_COMPLETE') { throw 'Importer read-back validation failed.' }
$result | Select-Object -Last 2
