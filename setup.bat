@echo off
REM Script d'installation automatique pour Jarvis Commander
REM Configure l'environnement virtuel et installe les dependances

echo ========================================
echo   JARVIS COMMANDER - Installation
echo ========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH.
    echo Installez Python 3.10 ou 3.12 depuis python.org
    echo.
    pause
    exit /b 1
)

echo Python detecte:
python --version
echo.

REM Créer l'environnement virtuel
if exist "venv\" (
    echo Environnement virtuel deja existant.
    choice /C YN /M "Voulez-vous le recreer (Y/N)"
    if errorlevel 2 goto :skip_venv
    echo Suppression de l'ancien environnement...
    rmdir /s /q venv
)

echo Creation de l'environnement virtuel...
python -m venv venv

if errorlevel 1 (
    echo ERREUR lors de la creation du venv.
    pause
    exit /b 1
)

:skip_venv

REM Activer l'environnement
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Mettre à jour pip
echo.
echo Mise a jour de pip...
python -m pip install --upgrade pip

REM Installer les dépendances
echo.
echo Installation des dependances...
echo Cela peut prendre plusieurs minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERREUR lors de l'installation des dependances.
    pause
    exit /b 1
)

REM Créer config.yaml si n'existe pas
if not exist "config\config.yaml" (
    echo.
    echo Creation du fichier de configuration...
    copy "config\config.yaml.example" "config\config.yaml"
    echo.
    echo ========================================
    echo   IMPORTANT: Configuration requise
    echo ========================================
    echo.
    echo 1. Allez sur https://console.picovoice.ai/
    echo 2. Creez un compte gratuit
    echo 3. Obtenez votre cle API
    echo 4. Editez config\config.yaml
    echo 5. Remplacez VOTRE_CLE_API_PICOVOICE_ICI par votre cle
    echo.
)

REM Vérifier les installations critiques
echo.
echo Verification des installations...
python -c "import pvporcupine; print('✓ pvporcupine OK')" 2>nul || echo ✗ pvporcupine ERREUR
python -c "import faster_whisper; print('✓ faster-whisper OK')" 2>nul || echo ✗ faster-whisper ERREUR
python -c "import pyttsx3; print('✓ pyttsx3 OK')" 2>nul || echo ✗ pyttsx3 ERREUR
python -c "import PySide6; print('✓ PySide6 OK')" 2>nul || echo ✗ PySide6 ERREUR

echo.
echo ========================================
echo   Installation terminee !
echo ========================================
echo.
echo Prochaines etapes:
echo 1. Configurez votre cle API dans config\config.yaml
echo 2. Lancez Jarvis avec: start_jarvis.bat
echo.

deactivate
pause
