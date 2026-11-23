@echo off
setlocal
title Iniciando DevPilot
echo.
echo Preparando sua IA local...

where ollama >nul 2>&1
if errorlevel 1 (
  echo Instalando o motor local da IA. Aguarde...
  where winget >nul 2>&1
  if errorlevel 1 (
    echo O instalador do Windows nao foi encontrado.
    start "" "https://ollama.com/download/windows"
    echo Instale o Ollama pela pagina aberta e execute este arquivo novamente.
    pause
    exit /b 1
  )
  winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo Nao foi possivel instalar o Ollama automaticamente.
    pause
    exit /b 1
  )
)

echo Iniciando o cerebro local...
start "" /b ollama serve
timeout /t 3 /nobreak >nul

ollama list | findstr /i "qwen2.5-coder:1.5b" >nul
if errorlevel 1 (
  echo Baixando o modelo de programacao. Isto acontece somente na primeira vez.
  ollama pull qwen2.5-coder:1.5b
  if errorlevel 1 (
    echo Falha ao baixar o modelo. Confira a sua internet e tente novamente.
    pause
    exit /b 1
  )
)

echo Tudo pronto. Abrindo DevPilot...
start "" "%~dp0DevPilot.exe"
exit /b 0
