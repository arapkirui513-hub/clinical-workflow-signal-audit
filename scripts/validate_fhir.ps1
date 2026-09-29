$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Validator = Join-Path $Root "validation\validator_cli.jar"
$Package = Join-Path $Root "validation\clinical-workflow-signal-audit-1.0.0.tgz"
$Generator = Join-Path $Root "scripts\generate_fhir_validation_samples.py"
$ValidationDir = Join-Path $Root "validation"

Write-Host ""
Write-Host "=== FHIR R4 Validation ===" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
if (-not (Test-Path $Validator)) {
    throw "FHIR validator not found: $Validator"
}

if (-not (Test-Path $Package)) {
    throw "FHIR package not found: $Package"
}

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    throw "Java was not found on PATH."
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found on PATH."
}

# Regenerate validation examples
Write-Host "[1/2] Generating validation artifacts..." -ForegroundColor Yellow

Push-Location $Root
try {
    python $Generator
}
finally {
    Pop-Location
}

# Validate each resource
Write-Host ""
Write-Host "[2/2] Validating FHIR R4 resources..." -ForegroundColor Yellow
Write-Host ""

$Artifacts = @(
    "Patient-validation.json",
    "Observation-validation.json",
    "Task-validation.json",
    "Bundle-validation.json"
)

$Failed = $false

foreach ($Artifact in $Artifacts) {
    $Path = Join-Path $ValidationDir $Artifact

    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host "Validating $Artifact" -ForegroundColor Cyan
    Write-Host "----------------------------------------"

    & java "-Dfile.encoding=UTF-8" `
        -jar $Validator `
        $Path `
        -version 4.0.1 `
        -ig $Package

    if ($LASTEXITCODE -ne 0) {
        $Failed = $true
        Write-Host ""
        Write-Host "FAILED: $Artifact" -ForegroundColor Red
    }
    else {
        Write-Host ""
        Write-Host "PASSED: $Artifact" -ForegroundColor Green
    }

    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan

if ($Failed) {
    Write-Host "FHIR validation FAILED." -ForegroundColor Red
    exit 1
}
else {
    Write-Host "FHIR validation completed successfully." -ForegroundColor Green
    Write-Host "FHIR version: 4.0.1"
    Write-Host "Validator: HAPI FHIR 6.10.4"
    exit 0
}