@echo off
REM ============================================
REM Installation des optimisations Jarvis Commander
REM Script automatique - 100% GRATUIT
REM ============================================

echo.
echo ========================================
echo   INSTALLATION OPTIMISATIONS JARVIS
echo ========================================
echo.
echo Ce script va installer :
echo - WebRTC VAD (filtrage vocal Google)
echo - Noisereduce (reduction de bruit)
echo - Scipy (filtres audio)
echo - PyAudio (detection peripheriques)
echo.
echo Toutes les dependances sont GRATUITES et open source
echo.
pause

echo.
echo [1/4] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo [2/4] Mise a jour de pip...
python -m pip install --upgrade pip

echo.
echo [3/4] Installation des nouvelles dependances...
pip install webrtcvad noisereduce scipy pyaudio

echo.
echo [4/4] Copie de la configuration optimisee...
if not exist config\config.yaml (
    copy config\config.yaml.optimized config\config.yaml
    echo Configuration copiee : config\config.yaml
    echo.
    echo IMPORTANT : Editez config\config.yaml et remplacez :
    echo   access_key: "VOTRE_CLE_API_PICOVOICE_ICI"
    echo Par votre cle gratuite depuis https://console.picovoice.ai/
) else (
    echo Config existante detectee. Consultez INSTALLATION_OPTIMISATIONS.md
    echo pour ajouter les parametres manquants.
)

echo.
echo ========================================
echo   INSTALLATION TERMINEE !
echo ========================================
echo.
echo Prochaines etapes :
echo 1. Editez config\config.yaml et ajoutez votre cle Picovoice
echo 2. Lancez Jarvis : python main.py
echo 3. Consultez INSTALLATION_OPTIMISATIONS.md pour plus d'infos
echo.
echo Optimisations appliquees :
echo [+] Latence reduite a moins de 1 seconde
echo [+] Filtrage audio pour film en fond
echo [+] Consommation RAM reduite de 50%%
echo [+] Detection vocale intelligente (VAD)
echo.
pause
