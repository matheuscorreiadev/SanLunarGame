@echo off
setlocal

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python nao encontrado no PATH. Instale o Python ou execute este arquivo em um ambiente com Python.
    pause
    exit /b 1
)

python -m PyInstaller --version >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller nao encontrado.
    echo Instale com: python -m pip install pyinstaller
    pause
    exit /b 1
)

python -c "import pygame" >nul 2>nul
if %errorlevel% neq 0 (
    echo pygame nao encontrado.
    echo Instale com: python -m pip install pygame
    pause
    exit /b 1
)

python -m PyInstaller --noconfirm --clean --onefile --windowed --name SanLunar --add-data "assets;assets" main.py

echo.
echo Build concluido. O exe esta em dist\SanLunar.exe
pause
