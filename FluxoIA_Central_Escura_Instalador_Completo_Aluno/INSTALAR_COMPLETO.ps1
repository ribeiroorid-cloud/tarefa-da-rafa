$ErrorActionPreference = 'Stop'

function Check-Exit($name) {
    if ($LASTEXITCODE -ne 0) { throw "$name falhou (codigo $LASTEXITCODE). Veja o erro acima." }
}

$root = Join-Path $env:USERPROFILE 'Downloads\FluxoIA_CENTRAL_COMPLETA'
$project = Join-Path $root 'fluxoia'
$venv = Join-Path $root '.venv'
$pythonExe = Join-Path $venv 'Scripts\python.exe'
$sourceTheme = Join-Path $PSScriptRoot 'Aparencia\fluxoia'

Write-Host "`n=== FLUXOIA - INSTALACAO NO COMPUTADOR ATUAL ===" -ForegroundColor Cyan
Write-Host "Usuario Windows: $env:USERNAME"
Write-Host "Pasta do projeto: $root"

# O pacote anterior continha apenas o layout. Baixamos o projeto original do
# repositorio publico do usuario; os arquivos de modelo e de YOLO estao nele.
if (-not (Test-Path (Join-Path $project 'supervisao.py'))) {
    $stage = Join-Path $env:TEMP ('fluxoia_instalador_' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    $archive = Join-Path $stage 'fluxoia_main.zip'
    $unpack = Join-Path $stage 'extraido'
    $url = 'https://github.com/slakkk0804-blip/fluxo-IA/archive/refs/heads/main.zip'
    Write-Host "`n1/4 Baixando o projeto original do GitHub..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing -TimeoutSec 180
        Expand-Archive -LiteralPath $archive -DestinationPath $unpack -Force
    } catch {
        throw "Nao consegui baixar o GitHub. Verifique a internet e tente novamente. Detalhes: $_"
    }
    $match = Get-ChildItem -LiteralPath $unpack -Recurse -File -Filter 'supervisao.py' |
        Where-Object { $_.Directory.Name -eq 'fluxoia' } | Select-Object -First 1
    if ($null -eq $match) { throw 'O ZIP do GitHub nao contem a pasta fluxoia/supervisao.py.' }
    $source = $match.Directory.FullName
    New-Item -ItemType Directory -Path $project -Force | Out-Null
    Get-ChildItem -LiteralPath $source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $project -Recurse -Force
    }
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "`n1/4 Projeto original ja encontrado: mantendo os arquivos existentes." -ForegroundColor Green
}

if (-not (Test-Path (Join-Path $project 'app.py'))) { throw 'O projeto original nao contem app.py.' }
Write-Host '2/4 Aplicando somente a interface escura...' -ForegroundColor Cyan
$backup = Join-Path $project 'app_backup_antes_do_tema.py'
if (-not (Test-Path $backup)) { Copy-Item (Join-Path $project 'app.py') $backup }
Copy-Item (Join-Path $sourceTheme 'app.py') (Join-Path $project 'app.py') -Force
Copy-Item (Join-Path $sourceTheme 'estilo_central.css') (Join-Path $project 'estilo_central.css') -Force
New-Item -ItemType Directory -Path (Join-Path $project '.streamlit') -Force | Out-Null
Copy-Item (Join-Path $sourceTheme '.streamlit\config.toml') (Join-Path $project '.streamlit\config.toml') -Force

if (-not (Test-Path $pythonExe)) {
    Write-Host "`n3/4 Criando ambiente Python (.venv)..." -ForegroundColor Cyan
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $selected = '-3'
        foreach ($v in @('-3.12','-3.11','-3.13')) {
            try {
                & py $v --version 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) { $selected = $v; break }
            } catch {
                # Versao nao instalada: tenta a proxima.
            }
        }
        Write-Host "Usando Python Launcher: $selected"
        & py $selected -m venv $venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv $venv
    } else {
        throw 'Python nao encontrado. Instale Python 3.12 em python.org, marque Add Python to PATH e execute novamente.'
    }
    Check-Exit 'Criar ambiente virtual'
} else {
    Write-Host "`n3/4 Ambiente Python ja existe." -ForegroundColor Green
}

Write-Host "`n4/4 Instalando as bibliotecas necessarias..." -ForegroundColor Cyan
& $pythonExe -m pip install --disable-pip-version-check -r (Join-Path $project 'requirements.txt')
Check-Exit 'Instalacao do Streamlit e bibliotecas de previsao'

if ((Test-Path (Join-Path $project 'requirements_supervisao.txt'))) {
    Write-Host "`nInstalando tambem as bibliotecas de supervisao (YOLO e OpenCV)..." -ForegroundColor Cyan
    & $pythonExe -m pip install --disable-pip-version-check -r (Join-Path $project 'requirements_supervisao.txt')
    Check-Exit 'Instalacao do YOLO e OpenCV'
}

$art = Join-Path $project 'artefatos'
$need = @('modelo_fluxo.joblib','metricas.json','demonstracao_teste.csv')
$missing = @($need | Where-Object { -not (Test-Path (Join-Path $art $_)) })
if ($missing.Count -gt 0) {
    Write-Host 'Os artefatos ainda nao estao no repositorio. Preparando treino local...' -ForegroundColor Yellow
    Push-Location $project
    try { & $pythonExe 'preparar.py'; Check-Exit 'Treinamento local' } finally { Pop-Location }
}

Write-Host "`nINSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "Pasta: $project" -ForegroundColor Green
Write-Host 'Para abrir use 2_ABRIR_FLUXOIA.bat. URL: http://localhost:8501' -ForegroundColor Green
Write-Host 'Nenhuma alteracao foi enviada ao GitHub ou Render.' -ForegroundColor Cyan
