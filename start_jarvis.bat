@echo off
REM Script de lancement rapide pour Jarvis Commander
REM Lance automatiquement l'environnement virtuel et Jarvis

echo ========================================
echo     JARVIS COMMANDER - Lancement
echo ========================================
echo.

REM Vérifier si venv existe
if not exist "venv\" (
    echo ERREUR: Environnement virtuel non trouve.
    echo Veuillez executer setup.bat d'abord.
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier si config.yaml existe
if not exist "config\config.yaml" (
    echo.
    echo ATTENTION: config\config.yaml n'existe pas.
    echo Copiez config\config.yaml.example vers config\config.yaml
    echo et modifiez votre cle API Picovoice.
    echo.
    pause
    exit /b 1
)

REM Lancer Jarvis
echo Lancement de Jarvis Commander...
echo.
python main.py

REM Si erreur
if errorlevel 1 (
    echo.
    echo ERREUR lors du lancement de Jarvis.
    echo Consultez les logs dans le dossier logs/
    echo.
    pause
)

deactivate
