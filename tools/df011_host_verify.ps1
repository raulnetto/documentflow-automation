[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string]$ReportPath
)

$ErrorActionPreference = 'Stop'
$scriptFile = $PSCommandPath
if ([string]::IsNullOrWhiteSpace($scriptFile)) {
    $scriptFile = $MyInvocation.MyCommand.Path
}
if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
    if ([string]::IsNullOrWhiteSpace($scriptFile)) {
        throw 'Cannot resolve project directory: script file path is unavailable.'
    }
    $scriptDirectory = Split-Path -Parent (Resolve-Path -LiteralPath $scriptFile).Path
    $ProjectPath = Split-Path -Parent $scriptDirectory
}
if (-not (Test-Path -LiteralPath $ProjectPath -PathType Container)) {
    throw "Project directory does not exist: $ProjectPath"
}
$ProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path
if (-not (Test-Path -LiteralPath (Join-Path $ProjectPath 'app\main.py') -PathType Leaf)) {
    throw "Project directory is not a DocumentFlow checkout: $ProjectPath"
}
if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path $ProjectPath 'df011-host-report.txt'
}
$ReportPath = [System.IO.Path]::GetFullPath($ReportPath)
$reportDirectory = Split-Path -Parent $ReportPath
if (-not (Test-Path -LiteralPath $reportDirectory -PathType Container)) {
    throw "Report directory does not exist: $reportDirectory"
}

$lines = [System.Collections.Generic.List[string]]::new()
function Record([string]$Text) {
    $lines.Add($Text)
    Write-Output $Text
}
function Get-FreeTcpPort {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    try {
        $listener.Start()
        return ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
    }
    finally { $listener.Stop() }
}
function Restore-ProcessEnvironment([hashtable]$Values) {
    foreach ($name in $Values.Keys) {
        [System.Environment]::SetEnvironmentVariable($name, $Values[$name], 'Process')
    }
}
function Invoke-CapturedProcess([string]$FilePath, [string[]]$Arguments) {
    $stdoutPath = $null
    $stderrPath = $null
    try {
        $stdoutPath = [System.IO.Path]::GetTempFileName()
        $stderrPath = [System.IO.Path]::GetTempFileName()
        $argumentLine = ($Arguments | ForEach-Object {
            if ($_ -match '\s|"') { '"' + $_.Replace('"', '\"') + '"' }
            else { $_ }
        }) -join ' '
        $process = Start-Process -FilePath $FilePath -ArgumentList $argumentLine `
            -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
        [pscustomobject]@{
            ExitCode = $process.ExitCode
            Stdout = [System.IO.File]::ReadAllText($stdoutPath)
            Stderr = [System.IO.File]::ReadAllText($stderrPath)
        }
    }
    finally {
        foreach ($temporaryLog in @($stdoutPath, $stderrPath)) {
            if ($temporaryLog) {
                Remove-Item -LiteralPath $temporaryLog -ErrorAction SilentlyContinue
            }
        }
    }
}
function Record-ProcessOutput($Result) {
    foreach ($line in ([string]$Result.Stdout -split "`r?`n")) {
        Record "STDOUT: $line"
    }
    foreach ($line in ([string]$Result.Stderr -split "`r?`n")) {
        Record "STDERR: $line"
    }
}

$environmentNames = @(
    'DATABASE_URL', 'DF011_TEST_DATABASE_URL', 'DF011_POSTGRES_DB',
    'DF011_PG_HOST_PORT', 'DF011_API_HOST_PORT', 'PATH'
)
$savedEnvironment = @{}
foreach ($name in $environmentNames) {
    $savedEnvironment[$name] = [System.Environment]::GetEnvironmentVariable($name, 'Process')
}
$composeProject = "documentflow-df011-$PID-$([Guid]::NewGuid().ToString('N').Substring(0, 8))"
$originalLocation = Get-Location
$composeStarted = $false
$failure = $null
$docker = $null
$stage = 'Bootstrap'
$exitCode = $null

try {
    Set-Location -LiteralPath $ProjectPath
    Record "DF-011 HOST verification $(Get-Date -Format o)"
    Record "PROJECT=$ProjectPath"
    $python = Join-Path $ProjectPath '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "Missing project Python: $python"
    }
    Record "PYTHON=$(& $python --version 2>&1)"

    # Keep legacy process URLs away from the SQLite regression and all later steps.
    $env:DATABASE_URL = $null
    $env:DF011_TEST_DATABASE_URL = $null
    Record '--- SQLite regression (PostgreSQL variables cleared) ---'
    $sqliteOutput = @(& $python -m pytest -q --ignore=tests/test_postgres_integration.py 2>&1)
    $sqliteExit = $LASTEXITCODE
    foreach ($line in $sqliteOutput) { Record $line }
    $sqliteText = [string]::Join("`n", [string[]]$sqliteOutput)
    if ($sqliteExit -ne 0) { throw "SQLite regression failed (exit $sqliteExit)" }
    if ($sqliteText -notmatch '\d+ passed') { throw 'SQLite regression produced no passed-test summary.' }
    if ($sqliteText -match '\d+ skipped') { Record 'SQLITE STATUS: PASSED WITH SKIPS' }
    else { Record 'SQLITE STATUS: PASSED' }

    $stage = 'Docker CLI discovery'
    $docker = (Get-Command docker -ErrorAction SilentlyContinue | Select-Object -First 1).Source
    if (-not $docker) {
        $dockerCandidates = @(
            "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe",
            "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe",
            "$env:LOCALAPPDATA\Programs\Docker\Docker\resources\bin\docker.exe",
            "$env:LOCALAPPDATA\Docker\Docker\resources\bin\docker.exe"
        )
        $docker = $dockerCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
    }
    if (-not $docker) { throw 'Docker CLI not found on HOST or in standard per-user locations.' }
    # Docker Desktop installs its credential helper beside the CLI. Expose it
    # only to this runner process so a cold image pull can use the configured helper.
    $dockerDirectory = Split-Path -Parent $docker
    $env:PATH = if ([string]::IsNullOrWhiteSpace($env:PATH)) {
        $dockerDirectory
    }
    else {
        "$dockerDirectory;$env:PATH"
    }
    Record "DOCKER=$docker"
    $credentialHelper = Join-Path $dockerDirectory 'docker-credential-desktop.exe'
    Record "DOCKER_CREDENTIAL_HELPER_PRESENT=$(Test-Path -LiteralPath $credentialHelper -PathType Leaf)"
    $stage = 'Docker Engine preflight'
    $dockerResult = Invoke-CapturedProcess -FilePath $docker `
        -Arguments @('version', '--format', '{{.Server.Version}}')
    $exitCode = $dockerResult.ExitCode
    Record-ProcessOutput $dockerResult
    if ($exitCode -ne 0) { throw "Docker Engine preflight exited with code $exitCode." }
    Record "DOCKER_ENGINE=$($dockerResult.Stdout.Trim())"

    # Use a unique Compose project and free host ports so no existing stack is reused or stopped.
    $env:DF011_POSTGRES_DB = "documentflow_test_$PID"
    $postgresPort = Get-FreeTcpPort
    do { $apiPort = Get-FreeTcpPort } while ($apiPort -eq $postgresPort)
    $env:DF011_PG_HOST_PORT = [string]$postgresPort
    $env:DF011_API_HOST_PORT = [string]$apiPort
    $composeArgs = @('compose', '-p', $composeProject, '-f', 'compose.yaml')
    Record "COMPOSE_PROJECT=$composeProject"
    Record "POSTGRES_TEST_DATABASE=$env:DF011_POSTGRES_DB"
    Record '--- Docker build ---'
    $exitCode = $null
    $stage = 'Docker build'
    $buildResult = Invoke-CapturedProcess -FilePath $docker `
        -Arguments (@('compose', '--progress=plain', '-p', $composeProject, '-f', 'compose.yaml', 'build', '--no-cache', '--pull'))
    $exitCode = $buildResult.ExitCode
    Record-ProcessOutput $buildResult
    Record "DOCKER_BUILD_EXIT_CODE=$exitCode"
    if ($exitCode -ne 0) { throw "Docker build exited with code $exitCode." }

    Record '--- isolated Compose startup ---'
    $exitCode = $null
    $stage = 'Compose startup'
    $composeStarted = $true
    $upResult = Invoke-CapturedProcess -FilePath $docker `
        -Arguments ($composeArgs + @('up', '-d', '--wait'))
    $exitCode = $upResult.ExitCode
    Record-ProcessOutput $upResult
    if ($exitCode -ne 0) { throw "Compose startup exited with code $exitCode." }

    $env:DF011_TEST_DATABASE_URL = "postgresql+psycopg://documentflow:documentflow_local@127.0.0.1:$env:DF011_PG_HOST_PORT/$env:DF011_POSTGRES_DB"
    Record '--- PostgreSQL integration (explicit isolated URL) ---'
    $postgresOutput = @(& $python -m pytest -q -rs tests/test_postgres_integration.py 2>&1)
    $postgresExit = $LASTEXITCODE
    foreach ($line in $postgresOutput) { Record $line }
    $postgresText = [string]::Join("`n", [string[]]$postgresOutput)
    if ($postgresExit -ne 0) { throw "PostgreSQL integration failed (exit $postgresExit)" }
    if ($postgresText -match '\d+ skipped') { throw 'PostgreSQL integration was skipped; no PostgreSQL pass is claimed.' }
    if ($postgresText -notmatch '1 passed') { throw 'PostgreSQL integration produced no passed-test summary.' }
    Record 'POSTGRES STATUS: PASSED'

    Record '--- HTTP smoke ---'
    $apiUrl = "http://127.0.0.1:$env:DF011_API_HOST_PORT"
    $response = Invoke-WebRequest -UseBasicParsing "$apiUrl/"
    if ($response.StatusCode -ne 200) { throw "Root HTTP status was $($response.StatusCode)." }
    Record "HTTP_ROOT=$($response.StatusCode) $($response.Content)"
    $flowId = [Guid]::NewGuid().ToString('D')
    $probeFile = "df011-host-missing-$flowId.pdf"
    $payload = @{
        nome_arquivo = $probeFile
        origem = 'df011-host-runner'
        id_fluxo = $flowId
    } | ConvertTo-Json -Compress
    $postStatus = $null
    try {
        $postResponse = Invoke-WebRequest -UseBasicParsing `
            -Uri "$apiUrl/webhooks/processar-documento" `
            -Method Post -ContentType 'application/json' -Body $payload
        $postStatus = [int]$postResponse.StatusCode
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $postStatus = [int]$_.Exception.Response.StatusCode
        }
        else { throw }
    }
    if ($postStatus -ne 404) { throw "Expected missing-file POST to return 404; got $postStatus." }
    Record "HTTP_POST_EXPECTED=$postStatus FLOW_ID=$flowId"

    $history = Invoke-WebRequest -UseBasicParsing "$apiUrl/processamentos"
    if ($history.StatusCode -ne 200) { throw "History HTTP status was $($history.StatusCode)." }
    $historyRecords = @($history.Content | ConvertFrom-Json)
    $persisted = @($historyRecords | Where-Object {
        $_.id_fluxo -eq $flowId -and $_.arquivo_origem -eq $probeFile
    })
    if ($persisted.Count -ne 1) { throw 'POST processing record was not recovered from HTTP history.' }
    $record = $persisted[0]
    if ($record.status -ne 'erro' -or $record.origem -ne 'df011-host-runner') {
        throw 'Recovered history record did not preserve expected processing metadata.'
    }
    $detailResponse = Invoke-WebRequest -UseBasicParsing `
        "$apiUrl/processamentos/$($record.id)"
    if ($detailResponse.StatusCode -ne 200) { throw "Record detail HTTP status was $($detailResponse.StatusCode)." }
    $detail = $detailResponse.Content | ConvertFrom-Json
    if ($detail.id -ne $record.id -or $detail.id_fluxo -ne $flowId) {
        throw 'GET by UUID did not recover the POST-created record.'
    }
    Record "HTTP_POST_PERSISTENCE_GET=PASSED RECORD_ID=$($record.id)"
    Record 'OVERALL STATUS: PASSED'
}
catch {
    $failure = $_.Exception
    Record "FAILED_STAGE=$stage"
    if ($null -ne $exitCode) { Record "FAILED_EXIT_CODE=$exitCode" }
    Record ('OVERALL STATUS: FAILED - ' + $failure.Message)
}
finally {
    if ($composeStarted -and $docker) {
        Record '--- cleanup of this run isolated Compose project ---'
        $downResult = Invoke-CapturedProcess -FilePath $docker `
            -Arguments (@('compose', '-p', $composeProject, '-f', 'compose.yaml', 'down', '--rmi', 'local', '--volumes', '--remove-orphans'))
        Record-ProcessOutput $downResult
        if ($downResult.ExitCode -ne 0) {
            Record "CLEANUP STATUS: FAILED (exit $($downResult.ExitCode))"
            if (-not $failure) { $failure = [InvalidOperationException]::new('Isolated Compose cleanup failed.') }
        }
        else { Record 'CLEANUP STATUS: removed this run project, volume, and local image' }
    }
    Restore-ProcessEnvironment $savedEnvironment
    Set-Location -LiteralPath $originalLocation.Path
    [System.IO.File]::WriteAllLines($ReportPath, $lines)
    Record "REPORT=$ReportPath"
}
if ($failure) { throw $failure }
