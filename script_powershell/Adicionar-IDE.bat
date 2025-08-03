@echo off
REM Este script executa o arquivo PowerShell para criar o atalho da IDE

REM Define a política de execução para permitir que este script rode
powershell -Command "Set-ExecutionPolicy Unrestricted -Scope Process"

REM Executa o script PowerShell que está na mesma pasta
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\Criar-Atalho.ps1"

pause