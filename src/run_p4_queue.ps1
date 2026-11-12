<#
  run_p4_queue.ps1  (Windows PowerShell 5.1)  -  unattended queue for Paper A post-freeze sensitivities S4, S2, S5, S3 (a, b), S1.

  Gate (ALL must hold for 5 consecutive minutes before an item starts; re-checked before EVERY item):
    - physical RAM free >= 6 GB
    - commit charge < 85 % of the commit limit
    - no python process whose command line contains "src/train.py"
    - no python process whose command line contains "paper_B" and "hpo"   (Paper B's HPO goes first)
  Items run one at a time. An item is skipped if its ledger tables\ledger_TEST_sens_<id>.csv exists (resumable; every
  script writes its ledger only when finished). A failed item is logged and the queue continues with the next one.
  Status lines are APPENDED to ..\_shared\GPU_SCHEDULE.md (IN USE / DONE / FAILED rows for Paper A) and to logs\p4_queue.log.
  The runner never kills any process. A lock file (logs\p4_queue.lock) prevents a second copy.

  Start (from any folder):
    powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\src\run_p4_queue.ps1"
  Optional: -MinFreeGB 6 -MaxCommitPct 85 -StableMinutes 5 -PollSeconds 30
#>
param(
    [double]$MinFreeGB = 6,
    [double]$MaxCommitPct = 85,
    [int]$StableMinutes = 5,
    [int]$PollSeconds = 30,
    [switch]$AllowPaperB,
    [switch]$IgnoreTrainPy,   # memory gate only; the patent project keeps starting runs (controller 01:20)    # run beside Paper B's HPO (agreed by Paper B 2026-11-12 01:25)
    [string]$Workers = '3',
    [string]$Threads = '20',
    [switch]$DryRun          # print the gate state and the item list, run nothing
)

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Shared = Join-Path (Split-Path $Root -Parent) '_shared\GPU_SCHEDULE.md'
$QLog = Join-Path $Root 'logs\p4_queue.log'
$Lock = Join-Path $Root 'logs\p4_queue.lock'
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

if ($DryRun) {
    $g = Get-Gate
    Write-Host ('DRY RUN gate: ok={0} free={1} GB commit={2} % blockers=[{3}]' -f $g.Ok, $g.FreeGB, $g.CommitPct, $g.Blockers)
}
# ---- lock
if ($DryRun) { $Lock = Join-Path $Root 'logs\p4_queue_dryrun.lock' }
if (Test-Path $Lock) {
    $old = (Get-Content $Lock -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($old -and (Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue)) {
        Write-QLog "another queue runner is already running (pid $old); exiting"
        exit 2
    }
}
Set-Content -Path $Lock -Value $PID

$py = 'py'
$items = @(
    @{ id = 's4';  desc = 'P4 S4 TIMEOUT-included jobs (PM100, CPU, 3 workers)';        ledger = 'ledger_TEST_sens_s4.csv';  script = 'sens_s4.py'; extra = @('--workers', $Workers) },
    @{ id = 's2';  desc = 'P4 S2 data-latency k=1,3,6 h (CPU, 3 workers)';              ledger = 'ledger_TEST_sens_s2.csv';  script = 'sens_s2.py'; extra = @('--workers', $Workers) },
    @{ id = 's5';  desc = 'P4 S5 Optuna 100 trials + refit + arms (CPU, 20 threads)';   ledger = 'ledger_TEST_sens_s5.csv';  script = 'sens_s5.py'; extra = @('--threads', $Threads, '--workers', $Workers) },
    @{ id = 's3a'; desc = 'P4 S3a direct emission factors, refit + arms (CPU)';         ledger = 'ledger_TEST_sens_s3a.csv'; script = 'sens_s3.py'; extra = @('--variant', 'a', '--workers', $Workers) },
    @{ id = 's3b'; desc = 'P4 S3b lifecycle oil 1116, refit + arms (CPU)';              ledger = 'ledger_TEST_sens_s3b.csv'; script = 'sens_s3.py'; extra = @('--variant', 'b', '--workers', $Workers) },
    @{ id = 's1';  desc = 'P4 S1 user-cluster x block bootstrap, 30 outer (CPU)';       ledger = 'ledger_TEST_sens_s1.csv';  script = 'sens_s1.py'; extra = @('--n-outer', '30', '--budget-hours', '8', '--workers', $Workers) }
)

Write-QLog ('queue runner started (pid {0}); root {1}; gate: free >= {2} GB, commit < {3} %, stable {4} min' -f $PID, $Root, $MinFreeGB, $MaxCommitPct, $StableMinutes)
$summary = @()
try {
    foreach ($it in $items) {
        $ledger = Join-Path $Root ('tables\' + $it.ledger)
        if (Test-Path $ledger) { Write-QLog ("skip {0}: ledger exists ({1})" -f $it.id, $it.ledger); $summary += ($it.id + ' skipped'); continue }
        if ($DryRun) { Write-Host ('DRY RUN would run {0}: py src\{1} {2}' -f $it.id, $it.script, ($it.extra -join ' ')); continue }
        Wait-Gate $it.id
        $logRel = 'paper_A/logs/sens_{0}.log' -f $it.id
        $t0 = Get-Date
        Add-Schedule $it.desc $logRel (Now-IST) '-' 'IN USE'
        Write-QLog ("RUN {0}: py src\{1} {2}" -f $it.id, $it.script, ($it.extra -join ' '))
        $args = @(('"' + (Join-Path $Root ('src\' + $it.script)) + '"')) + $it.extra
        $out = Join-Path $Root ('logs\p4_queue_{0}.out' -f $it.id)
        $err = Join-Path $Root ('logs\p4_queue_{0}.err' -f $it.id)
        $p = Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $Root -NoNewWindow -Wait -PassThru `
             -RedirectStandardOutput $out -RedirectStandardError $err
        $mins = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
        if ($p.ExitCode -eq 0 -and (Test-Path $ledger)) {
            Write-QLog ("DONE {0} in {1} min (exit 0, ledger written)" -f $it.id, $mins)
            Add-Schedule $it.desc $logRel (Now-IST) (Now-IST) 'DONE'
            $summary += ($it.id + ' done')
        } else {
            Write-QLog ("FAILED {0} after {1} min (exit {2}); see logs\sens_{0}.log and logs\p4_queue_{0}.err; continuing with the next item" -f $it.id, $mins, $p.ExitCode)
            Add-Schedule $it.desc $logRel (Now-IST) (Now-IST) ('FAILED exit ' + $p.ExitCode + ' (rerun the queue to resume)')
            $summary += ($it.id + ' FAILED')
        }
    }
    Write-QLog ('queue finished: ' + ($summary -join '; '))
}
finally {
    Remove-Item -Path $Lock -ErrorAction SilentlyContinue
}
