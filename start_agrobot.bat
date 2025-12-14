@echo off
title AgroBot Server
color 0A

echo =================================================
echo      🚜 INICIANDO SISTEMA AGROBOT V5 🚜
echo =================================================
echo.

echo [1/3] Verificando processos antigos...
:: O comando abaixo mata qualquer python.exe rodando para evitar o erro "Conflict"
taskkill /F /IM python.exe /T 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    -> Processos antigos encerrados com sucesso.
) else (
    echo    -> Nenhum processo antigo encontrado. Limpo.
)

echo.
echo [2/3] Aguardando liberacao da porta...
timeout /t 2 >nul

echo.
echo [3/3] Iniciando AgroBot (Telegram + Vision + Engine V5)...
echo.
echo    [LOG] O Bot esta online! Pressione CTRL+C para parar.
echo.

:: Inicia o bot
python telegram_bot.py

:: Se o bot cair, pausa para ler o erro
echo.
echo =================================================
echo    ⚠️  O AGROBOT PAROU. VEJA O ERRO ACIMA.  ⚠️
echo =================================================
pause
