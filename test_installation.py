"""
Script de test pour vérifier l'installation de Jarvis Commander.
Teste tous les composants critiques avant le premier lancement.
"""

import sys
import os

def print_header(text):
    """Affiche un en-tête formaté."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_python_version():
    """Teste la version de Python."""
    print("\n🐍 Test de la version Python...")
    version = sys.version_info
    print(f"   Version détectée : {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor in [10, 11, 12]:
        print("   ✅ Version Python compatible")
        return True
    else:
        print(f"   ⚠️  Version recommandée : 3.10, 3.11 ou 3.12")
        return True  # Pas bloquant

def test_imports():
    """Teste l'import des modules critiques."""
    print("\n📦 Test des imports...")
    
    modules = {
        'PySide6': 'Interface graphique (Qt)',
        'numpy': 'Calculs numériques',
        'sounddevice': 'Capture audio',
        'pvporcupine': 'Wake word detection',
        'faster_whisper': 'Speech-to-Text',
        'pyttsx3': 'Text-to-Speech',
        'psutil': 'Contrôle processus',
        'pyautogui': 'Contrôle clavier/souris',
        'yaml': 'Configuration'
    }
    
    results = {}
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"   ✅ {module:20s} ({description})")
            results[module] = True
        except ImportError as e:
            print(f"   ❌ {module:20s} - ERREUR: {e}")
            results[module] = False
    
    success = all(results.values())
    if success:
        print("\n   ✅ Tous les modules sont installés")
    else:
        print("\n   ❌ Certains modules sont manquants")
        print("      Exécutez : pip install -r requirements.txt")
    
    return success

def test_cuda():
    """Teste la disponibilité de CUDA pour GPU."""
    print("\n🎮 Test CUDA (GPU)...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   ✅ CUDA disponible")
            print(f"      GPU : {torch.cuda.get_device_name(0)}")
            print(f"      Version CUDA : {torch.version.cuda}")
            return True
        else:
            print("   ⚠️  CUDA non disponible (CPU sera utilisé)")
            print("      Whisper fonctionnera mais sera plus lent")
            return True  # Pas bloquant
    except ImportError:
        print("   ℹ️  PyTorch non installé (CUDA optionnel)")
        print("      Pour GPU : pip install torch --index-url https://download.pytorch.org/whl/cu118")
        return True  # Pas bloquant

def test_config():
    """Teste l'existence et la validité du fichier de configuration."""
    print("\n⚙️  Test de la configuration...")
    
    config_path = "config/config.yaml"
    
    if not os.path.exists(config_path):
        print(f"   ❌ {config_path} non trouvé")
        print("      Copiez config/config.yaml.example vers config/config.yaml")
        return False
    
    print(f"   ✅ {config_path} existe")
    
    # Charger et vérifier le contenu
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Vérifier la clé API Picovoice
        access_key = config.get('wake_word', {}).get('access_key', '')
        if access_key == 'VOTRE_CLE_API_PICOVOICE_ICI' or not access_key:
            print("   ⚠️  Clé API Picovoice non configurée")
            print("      1. Allez sur https://console.picovoice.ai/")
            print("      2. Créez un compte gratuit")
            print("      3. Copiez votre Access Key")
            print("      4. Collez-la dans config/config.yaml")
            return False
        else:
            print(f"   ✅ Clé API configurée ({access_key[:10]}...)")
        
        # Vérifier les applications
        apps = config.get('applications', {})
        print(f"   ✅ {len(apps)} applications configurées")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la lecture : {e}")
        return False

def test_audio_devices():
    """Liste les périphériques audio disponibles."""
    print("\n🎤 Périphériques audio disponibles...")
    
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        print("\n   Entrées (Microphones) :")
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                default = " [DÉFAUT]" if i == sd.default.device[0] else ""
                print(f"      [{i}] {dev['name']}{default}")
        
        print("\n   Sorties (Haut-parleurs) :")
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                default = " [DÉFAUT]" if i == sd.default.device[1] else ""
                print(f"      [{i}] {dev['name']}{default}")
        
        print("\n   ℹ️  Pour changer de micro, modifiez 'input_device_index' dans config.yaml")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_tts_voices():
    """Liste les voix TTS disponibles."""
    print("\n🔊 Voix TTS disponibles...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"\n   {len(voices)} voix détectées :\n")
        for i, voice in enumerate(voices):
            lang = voice.languages[0] if voice.languages else "?"
            print(f"      [{i}] {voice.name}")
            print(f"          ID: {voice.id}")
            print(f"          Langue: {lang}\n")
        
        # Trouver une voix française
        fr_voices = [v for v in voices if 'fr' in str(v.languages).lower() or 'french' in v.name.lower()]
        if fr_voices:
            print(f"   ✅ {len(fr_voices)} voix française(s) trouvée(s)")
        else:
            print("   ⚠️  Aucune voix française trouvée")
            print("      Jarvis utilisera la voix par défaut")
        
        engine.stop()
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def test_whisper_models():
    """Vérifie les modèles Whisper disponibles."""
    print("\n🎙️  Modèles Whisper...")
    
    print("\n   Modèles disponibles au téléchargement :")
    models = {
        'tiny': '~75 MB (le plus rapide, moins précis)',
        'base': '~150 MB',
        'small': '~500 MB (recommandé)',
        'medium': '~1.5 GB',
        'large': '~3 GB (le plus précis, le plus lent)'
    }
    
    for name, desc in models.items():
        print(f"      • {name:10s} : {desc}")
    
    print("\n   ℹ️  Le modèle sera téléchargé au premier lancement")
    print("      Configuration actuelle dans config.yaml")
    
    return True

def main():
    """Fonction principale."""
    print_header("JARVIS COMMANDER - Test d'installation")
    
    results = {
        'Python Version': test_python_version(),
        'Modules Python': test_imports(),
        'CUDA/GPU': test_cuda(),
        'Configuration': test_config(),
        'Périphériques Audio': test_audio_devices(),
        'Voix TTS': test_tts_voices(),
        'Modèles Whisper': test_whisper_models()
    }
    
    # Résumé
    print_header("RÉSUMÉ")
    
    critical_tests = ['Modules Python', 'Configuration']
    critical_failed = [name for name in critical_tests if not results[name]]
    
    if critical_failed:
        print("\n❌ TESTS CRITIQUES ÉCHOUÉS :\n")
        for test in critical_failed:
            print(f"   • {test}")
        print("\n⚠️  Jarvis ne peut pas démarrer.")
        print("   Corrigez les erreurs ci-dessus avant de continuer.\n")
        return False
    else:
        print("\n✅ TOUS LES TESTS CRITIQUES RÉUSSIS !\n")
        print("   Jarvis est prêt à démarrer.\n")
        
        warnings = [name for name, result in results.items() 
                   if not result and name not in critical_tests]
        if warnings:
            print("⚠️  Avertissements (non bloquants) :\n")
            for test in warnings:
                print(f"   • {test}")
            print()
        
        print("🚀 Pour lancer Jarvis :")
        print("   • Windows : start_jarvis.bat")
        print("   • Manuel : python main.py\n")
        
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
