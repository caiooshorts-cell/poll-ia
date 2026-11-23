@echo off
title DevPilot - Instalar IA local
echo.
echo ==========================================
echo   DevPilot - Configuracao de IA local
echo ==========================================
echo.
where ollama >nul 2>&1
if errorlevel 1 (
  echo O Ollama ainda nao esta instalado.
  echo Uma pagina de instalacao sera aberta agora.
  start "" "https://ollama.com/download/windows"
  echo.
  echo Depois de instalar o Ollama, feche esta janela e execute este arquivo novamente.
  pause
  exit /b
)

echo Baixando o cerebro local do DevPilot...
echo Tamanho aproximado: 1 GB. Isto acontece apenas uma vez.
ollama pull qwen2.5-coder:1.5b
if errorlevel 1 (
  echo.
  echo Nao foi possivel baixar o modelo. Confira sua internet e tente novamente.
  pause
  exit /b 1
)

echo.
echo Pronto! A IA agora roda no seu PC, sem chave de API.
echo Abra o DevPilot.exe e escolha qwen2.5-coder:1.5b.
pause
