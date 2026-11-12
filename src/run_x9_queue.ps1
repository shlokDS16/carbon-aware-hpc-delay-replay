<#
  run_x9_queue.ps1  (Windows PowerShell 5.1)  -  unattended queue for Paper A item X9 (capacity-capped replay, research/P4_PLAN_X9.md C1).
  Runs src\sens_x9.py for PM100 first, then FDATA, then KIT_FH2; a trace is started only if the previous trace finished in under
  MaxTraceMinutes (45) minutes (PM100 always runs).  Smoke test: py src\sens_x9.py --smoke --bas CISO,ERCO --n-jobs 2000 --reps 1 --B 50.

  Gate: same as run_p4x_queue.ps1 / run_p4_queue.ps1 (physical RAM free >= MinFreeGB and commit < MaxCommitPct, both holding StableMinutes
  in a row before EVERY item; train.py ignored with -IgnoreTrainPy; Paper B hpo ignored with -AllowPaperB), PLUS the queue first waits until
  no powershell process runs run_p4x_queue.ps1 or run_p4_queue.ps1 (switch -SkipQueueWait for testing only).
  Items run one at a time (at most 2 simulation workers); an item is skipped if tables\ledger_TEST_sens_x9.csv already holds rows
  'sens.x9.<TRACE>.' (the script writes them only when the trace is finished); a failed item is logged and the queue continues.
  Status rows are APPENDED to ..\_shared\GPU_SCHEDULE.md and logs\x9_queue.log.  The runner never kills any process.
  Lock file logs\x9_queue.lock prevents a second copy.

  Start (same switches and defaults as the P4x queue):
    powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\src\run_x9_queue.ps1" -AllowPaperB -IgnoreTrainPy -Workers 2 -Threads 10
  Optional: -MinFreeGB 5 -MaxCommitPct 90 -StableMinutes 5 -PollSeconds 30 -MaxTraceMinutes 45 -DryRun -SkipQueueWait
#>
param(
    [double]$MinFreeGB = 5,
    [double]$MaxCommitPct = 90,
    [int]$StableMinutes = 5,
    [int]$PollSeconds = 30,
    [switch]$AllowPaperB,
    [switch]$IgnoreTrainPy,
    [string]$Workers = '2',
    [string]$Threads = '10',     # accepted for switch compatibility with the P4x queue; X9 does not use it
    [double]$MaxTraceMinutes = 45,
    [switch]$SkipQueueWait,      # do not wait for the P4 / P4x queues (testing only)
    [switch]$DryRun              # print the gate state and the item list, run nothing
)

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Shared = Join-Path (Split-Path $Root -Parent) '_shared\GPU_SCHEDULE.md'
$QLog = Join-Path $Root 'logs\x9_queue.log'
$Lock = Join-Path $Root 'logs\x9_queue.lock'
$Utf8 = New-Object System.Text.UTF8Encoding $false
New-Item -ItemType Directory -Force -Path (Join-Path $Root 'logs') | Out-Null

function Now-IST { [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date), 'India Standard Time').ToString('yyyy-MM-dd HH:mm') }
function Write-QLog([string]$m) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Host $line
    [System.IO.File]::AppendAllText($QLog, $line + [Environment]::NewLine, $Utf8)
}
function Add-Schedule([string]$job, [string]$log, [string]$start, [string]$end, [string]$status) {
    # append-only table row (same columns as the existing rows)
    $row = '| A | {0} | {1} | {2} | {3} | {4} |' -f $job, $log, $start, $end, $status
    try { [System.IO.File]::AppendAllText($Shared, $row + [Environment]::NewLine, $Utf8) }
    catch { Write-QLog ('WARN could not append to GPU_SCHEDULE.md: ' + $_.Exception.Message) }
}

function Get-Gate {
    $os = Get-CimInstance Win32_OperatingSystem
    $freeGB = $os.FreePhysicalMemory / 1MB                       # KB -> GB
    $limitKB = [double]$os.TotalVirtualMemorySize
    $usedKB = $limitKB - [double]$os.FreeVirtualMemory
    $commitPct = 100.0 * $usedKB / $limitKB
    $blockers = @()
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe' OR Name='py.exe'"
    foreach ($p in $procs) {
        $cl = ([string]$p.CommandLine).Replace('\', '/').ToLower()
        if ((-not $IgnoreTrainPy) -and $cl.Contains('src/train.py')) { $blockers += ('train.py pid ' + $p.ProcessId) }
        if ((-not $AllowPaperB) -and $cl.Contains('paper_b') -and $cl.Contains('hpo')) { $blockers += ('paper_B hpo pid ' + $p.ProcessId) }
    }
    $ok = ($freeGB -ge $MinFreeGB) -and ($commitPct -lt $MaxCommitPct) -and ($blockers.Count -eq 0)
    [pscustomobject]@{ Ok = $ok; FreeGB = [math]::Round($freeGB, 2); CommitPct = [math]::Round($commitPct, 1); Blockers = ($blockers -join ', ') }
}

function Wait-Gate([string]$what) {
    $since = $null
    $lastNote = Get-Date '2000-01-01'
    while ($true) {
        $g = Get-Gate
        if ($g.Ok) {
            if ($null -eq $since) { $since = Get-Date; Write-QLog ("gate open for $what (free {0} GB, commit {1} %); must hold {2} min" -f $g.FreeGB, $g.CommitPct, $StableMinutes) }
            if (((Get-Date) - $since).TotalMinutes -ge $StableMinutes) {
                Write-QLog ("gate stable for $StableMinutes min; starting $what (free {0} GB, commit {1} %)" -f $g.FreeGB, $g.CommitPct)
                return
            }
        } else {
            if ($null -ne $since) { Write-QLog ("gate closed again while waiting for $what (free {0} GB, commit {1} %, blockers: {2})" -f $g.FreeGB, $g.CommitPct, $g.Blockers) }
            $since = $null
            if (((Get-Date) - $lastNote).TotalMinutes -ge 10) {
                Write-QLog ("waiting for ${what}: free {0} GB (need {1}), commit {2} % (need < {3}), blockers: [{4}]" -f $g.FreeGB, $MinFreeGB, $g.CommitPct, $MaxCommitPct, $g.Blockers)
                $lastNote = Get-Date
            }
        }
        Start-Sleep -Seconds $PollSeconds
    }
}

function Test-QueuesRunning {
    # true while any powershell process runs run_p4_queue.ps1 or run_p4x_queue.ps1 (this script is not matched: its name differs)
    $running = @()
    foreach ($p in (Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'")) {
        $cl = ([string]$p.CommandLine).ToLower()
        if ($p.ProcessId -ne $PID -and ($cl.Contains('run_p4_queue.ps1') -or $cl.Contains('run_p4x_queue.ps1'))) { $running += $p.ProcessId }
    }
    [pscustomobject]@{ Running = ($running.Count -gt 0); Pids = ($running -join ',') }
}

function Wait-Queues {
    $lastNote = Get-Date '2000-01-01'
    while ($true) {
        $f = Test-QueuesRunning
        if (-not $f.Running) { Write-QLog 'run_p4_queue.ps1 and run_p4x_queue.ps1 are not running; continuing'; return }
        if (((Get-Date) - $lastNote).TotalMinutes -ge 10) {
            Write-QLog ('waiting for run_p4_queue.ps1 / run_p4x_queue.ps1 to finish (pids {0})' -f $f.Pids)
            $lastNote = Get-Date
        }
        Start-Sleep -Seconds $PollSeconds
    }
}

function Test-LedgerHas([string]$trace) {
    $led = Join-Path $Root 'tables\ledger_TEST_sens_x9.csv'
    if (-not (Test-Path $led)) { return $false }
    return [bool](Select-String -Path $led -Pattern ('sens.x9.' + $trace + '.') -SimpleMatch -Quiet)
}

if ($DryRun) {
    $g = Get-Gate
    Write-Host ('DRY RUN gate: ok={0} free={1} GB commit={2} % blockers=[{3}]' -f $g.Ok, $g.FreeGB, $g.CommitPct, $g.Blockers)
    $f = Test-QueuesRunning
    Write-Host ('DRY RUN P4 / P4x queue running={0} (pids {1})' -f $f.Running, $f.Pids)
}
# ---- lock
if ($DryRun) { $Lock = Join-Path $Root 'logs\x9_queue_dryrun.lock' }
if (Test-Path $Lock) {
    $old = (Get-Content $Lock -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($old -and (Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue)) {
        Write-QLog "another X9 queue runner is already running (pid $old); exiting"
        exit 2
    }
}
Set-Content -Path $Lock -Value $PID

$py = 'py'
$items = @(
    @{ id = 'x9_PM100';   trace = 'PM100';   desc = 'X9 capacity-capped replay PM100 (CPU)';   script = 'sens_x9.py'; extra = @('--traces', 'PM100',   '--workers', $Workers) },
    @{ id = 'x9_FDATA';   trace = 'FDATA';   desc = 'X9 capacity-capped replay F-DATA (CPU)';  script = 'sens_x9.py'; extra = @('--traces', 'FDATA',   '--workers', $Workers) },
    @{ id = 'x9_KIT_FH2'; trace = 'KIT_FH2'; desc = 'X9 capacity-capped replay KIT FH2 (CPU)'; script = 'sens_x9.py'; extra = @('--traces', 'KIT_FH2', '--workers', $Workers) }
)

Write-QLog ('X9 queue runner started (pid {0}); root {1}; gate: free >= {2} GB, commit < {3} %, stable {4} min; workers {5}; next trace only if the previous took < {6} min' -f $PID, $Root, $MinFreeGB, $MaxCommitPct, $StableMinutes, $Workers, $MaxTraceMinutes)
$summary = @()
$prevMin = 0.0
try {
    if ((-not $DryRun) -and (-not $SkipQueueWait)) { Wait-Queues }
    foreach ($it in $items) {
        if (Test-LedgerHas $it.trace) { Write-QLog ("skip {0}: ledger rows exist (ledger_TEST_sens_x9.csv)" -f $it.id); $summary += ($it.id + ' skipped'); continue }
        if ($prevMin -ge $MaxTraceMinutes) { Write-QLog ("not started {0}: the previous trace took {1} min (limit {2})" -f $it.id, $prevMin, $MaxTraceMinutes); $summary += ($it.id + ' not started (time rule)'); continue }
        if ($DryRun) { Write-Host ('DRY RUN would run {0}: py src\{1} {2}' -f $it.id, $it.script, ($it.extra -join ' ')); continue }
        Wait-Gate $it.id
        $logRel = 'paper_A/logs/sens_x9.log'
        $t0 = Get-Date
        Add-Schedule $it.desc $logRel (Now-IST) '-' 'IN USE'
        Write-QLog ("RUN {0}: py src\{1} {2}" -f $it.id, $it.script, ($it.extra -join ' '))
        $args = @(('"' + (Join-Path $Root ('src\' + $it.script)) + '"')) + $it.extra
        $out = Join-Path $Root ('logs\x9_queue_{0}.out' -f $it.id)
        $err = Join-Path $Root ('logs\x9_queue_{0}.err' -f $it.id)
        $p = Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $Root -NoNewWindow -Wait -PassThru `
             -RedirectStandardOutput $out -RedirectStandardError $err
        $mins = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
        $prevMin = $mins
        if ($p.ExitCode -eq 0 -and (Test-LedgerHas $it.trace)) {
            Write-QLog ("DONE {0} in {1} min (exit 0, ledger rows written)" -f $it.id, $mins)
            Add-Schedule $it.desc $logRel (Now-IST) (Now-IST) 'DONE'
            $summary += ($it.id + ' done')
        } else {
            Write-QLog ("FAILED {0} after {1} min (exit {2}); see logs\sens_x9.log and logs\x9_queue_{0}.err; continuing" -f $it.id, $mins, $p.ExitCode)
            Add-Schedule $it.desc $logRel (Now-IST) (Now-IST) ('FAILED exit ' + $p.ExitCode + ' (rerun the queue to resume)')
            $summary += ($it.id + ' FAILED')
            $prevMin = 0.0
        }
    }
    Write-QLog ('queue finished: ' + ($summary -join '; '))
}
finally {
    Remove-Item -Path $Lock -ErrorAction SilentlyContinue
}
