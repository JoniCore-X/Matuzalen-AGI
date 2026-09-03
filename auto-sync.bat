@echo off
REM Auto-Sync Script for AutoPlan AGI
REM Este script mantiene el proyecto actualizado en GitHub automáticamente

echo [%date% %time%] Iniciando auto-sync de AutoPlan AGI...

cd /d "C:\Users\jonie\OneDrive\Desktop\AutoPlan"

REM Agregar todos los cambios
echo [%date% %time%] Agregando archivos al staging area...
git add .

REM Verificar si hay cambios
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [%date% %time%] No hay cambios para commitear.
    goto :end
)

REM Crear commit automático
echo [%date% %time%] Creando commit automático...
git commit -m "Auto-sync: Actualización automática del proyecto - %date% %time%

Generated with [Devin](https://devin.ai)

Co-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>"

REM Push a GitHub
echo [%date% %time%] Haciendo push a GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo [%date% %time%] Auto-sync completado exitosamente.
) else (
    echo [%date% %time%] Error en auto-sync. Código de error: %errorlevel%
)

:end
echo [%date% %time%] Auto-sync finalizado.
