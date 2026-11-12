<#
  run_p4x_queue.ps1  (Windows PowerShell 5.1)  -  unattended queue for the Paper A post-freeze items that follow the P4 queue:
  S2b (data latency 24/48 h), X1, X3, arms (threshold / padded / quantile runtime), placement shift, X2, X4, X5, X6, X7.
  Specs: research/P4_PLAN_AMEND.md, P4_PLAN_AMEND2.md, P4_PLAN_X.md (binding). Implementation report: research/A21_X_IMPL.md.

  Gate: same as run_p4_queue.ps1 (physical RAM free >= MinFreeGB and commit < MaxCommitPct, both holding StableMinutes in a row before
  EVERY item; train.py ignored with -IgnoreTrainPy; Paper B hpo ignored with -AllowPaperB), PLUS the queue waits until
  run_p4_queue.ps1 has finished: no powershell process runs that script and logs\p4_queue.log holds at least one " RUN " line
  (so a runner that never started anything does not count as finished).
  Items run one at a time; an item is skipped if tables\ledger_TEST_sens_<id>.csv exists (every script writes its ledger only when
  finished); a failed item is logged and the queue continues. Status rows are APPENDED to ..\_shared\GPU_SCHEDULE.md and
  logs\p4x_queue.log. The runner never kills any process. Lock file logs\p4x_queue.lock prevents a second copy.

  Start (same switches and defaults as the restarted P4 queue):
    powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Shlok\Downloads\Sustainable Computing papers\paper_A\src\run_p4x_queue.ps1" -AllowPaperB -IgnoreTrainPy -Workers 2 -Threads 10
  Optional: -MinFreeGB 5 -MaxCommitPct 90 -StableMinutes 5 -PollSeconds 30 -DryRun -SkipP4Wait
#>
param(
    [double]$MinFreeGB = 5,
    [double]$MaxCommitPct = 90,
    [int]$StableMinutes = 5,
    [int]$PollSeconds = 30,
    [switch]$AllowPaperB,
    [switch]$IgnoreTrainPy,
    [string]$Workers = '2',
    [string]$Threads = '10',
    [switch]$SkipP4Wait,     # do not wait for run_p4_queue.ps1 (testing only)
    [switch]$DryRun          # print the gate state and the item list, run nothing
)

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Shared = Join-Path (Split-Path $Root -Parent) '_shared\GPU_SCHEDULE.md'
$QLog = Join-Path $Root 'logs\p4x_queue.log'
$P4Log = Join-Path $Root 'logs\p4_queue.log'
$Lock = Join-Path $Root 'logs\p4x_queue.lock'
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

function Test-P4Finished {
    # finished = no powershell process runs run_p4_queue.ps1 AND the P4 log shows that at least one item was started (" RUN ")
    $running = $false
    foreach ($p in (Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'")) {
        if (([string]$p.CommandLine).ToLower().Contains('run_p4_queue.ps1') -and $p.ProcessId -ne $PID) { $running = $true }
    }
    $ranAny = $false
    if (Test-Path $P4Log) { $ranAny = [bool](Select-String -Path $P4Log -Pattern ' RUN ' -SimpleMatch -Quiet) }
    [pscustomobject]@{ Done = ((-not $running) -and $ranAny); Running = $running; RanAny = $ranAny }
}

function Wait-P4 {
    $lastNote = Get-Date '2000-01-01'
    while ($true) {
        $f = Test-P4Finished
        if ($f.Done) { Write-QLog 'run_p4_queue.ps1 has finished; continuing'; return }
        if (((Get-Date) - $lastNote).TotalMinutes -ge 10) {
            Write-QLog ('waiting for run_p4_queue.ps1 to finish (running={0}, an item has run={1})' -f $f.Running, $f.RanAny)
            $lastNote = Get-Date
        }
        Start-Sleep -Seconds $PollSeconds
    }
}

if ($DryRun) {
    $g = Get-Gate
    Write-Host ('DRY RUN gate: ok={0} free={1} GB commit={2} % blockers=[{3}]' -f $g.Ok, $g.FreeGB, $g.CommitPct, $g.Blockers)
    $f = Test-P4Finished
    Write-Host ('DRY RUN P4 queue finished={0} (running={1}, an item has run={2})' -f $f.Done, $f.Running, $f.RanAny)
}
# ---- lock
if ($DryRun) { $Lock = Join-Path $Root 'logs\p4x_queue_dryrun.lock' }
if (Test-Path $Lock) {
    $old = (Get-Content $Lock -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($old -and (Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue)) {
        Write-QLog "another P4x queue runner is already running (pid $old); exiting"
        exit 2
    }
}
Set-Content -Path $Lock -Value $PID

$py = 'py'
$items = @(
    @{ id = 's2b';   desc = 'P4x S2b data latency 24/48 h (CPU)';                      ledger = 'ledger_TEST_sens_s2b.csv';   script = 'sens_s2b.py';  extra = @('--workers', $Workers) },
    @{ id = 'x1';    desc = 'P4x X1 runtime-estimate sweep (CPU)';                     ledger = 'ledger_TEST_sens_x1.csv';    script = 'sens_x.py';    extra = @('--item', 'x1', '--workers', $Workers) },
    @{ id = 'x3';    desc = 'P4x X3 forecast-lead cap (CPU)';                          ledger = 'ledger_TEST_sens_x3.csv';    script = 'sens_x.py';    extra = @('--item', 'x3', '--workers', $Workers) },
    @{ id = 'arms';  desc = 'P4x threshold / padded / quantile arms (CPU)';            ledger = 'ledger_TEST_sens_arms.csv';  script = 'sens_arms.py'; extra = @('--item', 'arms', '--workers', $Workers) },
    @{ id = 'shift'; desc = 'P4x placement shift +/-3 h, PM100 (CPU)';                 ledger = 'ledger_TEST_sens_shift.csv'; script = 'sens_arms.py'; extra = @('--item', 'shift', '--workers', $Workers) },
    @{ id = 'x2';    desc = 'P4x X2 injected noise vs forecast (CPU)';                 ledger = 'ledger_TEST_sens_x2.csv';    script = 'sens_x.py';    extra = @('--item', 'x2', '--workers', $Workers) },
    @{ id = 'x4';    desc = 'P4x X4 load concentration + job dump (CPU)';              ledger = 'ledger_TEST_sens_x4.csv';    script = 'sens_x.py';    extra = @('--item', 'x4', '--workers', $Workers) },
    @{ id = 'x5';    desc = 'P4x X5 penalty concentration (CPU, reads X4 dump)';       ledger = 'ledger_TEST_sens_x5.csv';    script = 'sens_x.py';    extra = @('--item', 'x5', '--workers', $Workers) },
    @{ id = 'x6';    desc = 'P4x X6 when the saving accrues (CPU, reads X4 dump)';     ledger = 'ledger_TEST_sens_x6.csv';    script = 'sens_x.py';    extra = @('--item', 'x6', '--workers', $Workers) },
    @{ id = 'x7';    desc = 'P4x X7 fossil-only proxy, forecast refit + arms (CPU)';   ledger = 'ledger_TEST_sens_x7.csv';    script = 'sens_x.py';    extra = @('--item', 'x7', '--workers', $Workers, '--threads', $Threads) }
)

Write-QLog ('P4x queue runner started (pid {0}); root {1}; gate: free >= {2} GB, commit < {3} %, stable {4} min; workers {5}, threads {6}' -f $PID, $Root, $MinFreeGB, $MaxCommitPct, $StableMinutes, $Workers, $Threads)
$summary = @()
try {
    if ((-not $DryRun) -and (-not $SkipP4Wait)) { Wait-P4 }
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
        $out = Join-Path $Root ('logs\p4x_queue_{0}.out' -f $it.id)
        $err = Join-Path $Root ('logs\p4x_queue_{0}.err' -f $it.id)
        $p = Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $Root -NoNewWindow -Wait -PassThru `
             -RedirectStandardOutput $out -RedirectStandardError $err
        $mins = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
        if ($p.ExitCode -eq 0 -and (Test-Path $ledger)) {
            Write-QLog ("DONE {0} in {1} min (exit 0, ledger written)" -f $it.id, $mins)
            Add-Schedule $it.desc $logRel (Now-IST) (Now-IST) 'DONE'
            $summary += ($it.id + ' done')
        } else {
            Write-QLog ("FAILED {0} after {1} min (exit {2}); see logs\sens_{0}.log and logs\p4x_queue_{0}.err; continuing with the next item" -f $it.id, $mins, $p.ExitCode)
            Add-Schedule $it.desc $logRel (Now-IST) (Now-IST) ('FAILED exit ' + $p.ExitCode + ' (rerun the queue to resume)')
            $summary += ($it.id + ' FAILED')
        }
    }
    Write-QLog ('queue finished: ' + ($summary -join '; '))
}
finally {
    Remove-Item -Path $Lock -ErrorAction SilentlyContinue
}
