@echo off
REM ============================================
REM Installation RAPIDE optimisations Jarvis
REM Sans webrtcvad (pose probleme de compilation)
REM ============================================

echo.
echo ========================================
echo   INSTALLATION RAPIDE OPTIMISATIONS
echo ========================================
echo.
echo Ce script va installer UNIQUEMENT :
echo - Noisereduce (reduction de bruit)
echo - Scipy (filtres audio)
echo.
echo webrtcvad sera DESACTIVE (pose probleme de compilation C++)
echo Les autres filtres suffisent pour le film en fond !
echo.
pause

echo.
echo [1/3] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo [2/3] Installation des dependances compatibles...
pip install noisereduce scipy

echo.
echo [3/3] Application de la configuration optimisee...
echo.

REM Copier config_optimise vers config si absent
if not exist config\config.yaml (
    copy config\config_optimise.yaml config\config.yaml
    echo Configuration copiee : config\config.yaml
) else (
    echo Config existante detectee.
)

echo.
echo ========================================
echo   INSTALLATION TERMINEE !
echo ========================================
echo.
echo IMPORTANT : Pour accelerer Jarvis :
echo.
echo 1. Ouvrez config\config.yaml
echo.
echo 2. Changez la ligne :
echo    model: "small"
echo    PAR :
echo    model: "tiny"
echo.
echo 3. Relancez : python main.py
echo.
echo RESULTAT ATTENDU :
echo - Latence reduite de 2-4s a moins de 1s (4x plus rapide)
echo - Filtrage audio maintenu (noisereduce + scipy)
echo - Consommation RAM reduite de 50%%
echo.
pause
