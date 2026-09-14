param([string]$Source='src\Challenge.mq5')
$ErrorActionPreference='Stop'
$dest='C:\Users\ian\AppData\Roaming\MetaQuotes\Terminal\DE9A4B13809164D991CFFF8AF2B25C58\MQL5\Experts\GBP100'
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item $Source "$dest\Challenge.mq5" -Force
$p=Start-Process 'C:\Program Files\IG Markets MetaTrader 5 Terminal\MetaEditor64.exe' -ArgumentList "/compile:`"$dest\Challenge.mq5`" /log" -PassThru -Wait -WindowStyle Hidden
$log=Get-Content "$dest\Challenge.log"
$log | Set-Content evidence/compile.log
$log | Select-Object -Last 2
if(-not ($log -match 'Result: 0 errors, 0 warnings')){throw 'Compilation failed'}
Copy-Item "$dest\Challenge.ex5" src/Challenge.ex5 -Force
