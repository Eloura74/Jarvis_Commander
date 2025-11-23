# Module Skills (Compétences)
# Contient les fonctions réelles que Jarvis peut exécuter sur le PC.

import os
import webbrowser
import platform
import subprocess
from config_manager import config

def execute_skill(skill_name):
    """Exécute une compétence par son nom."""
    print(f"🔧 Exécution de la compétence : {skill_name}")
    
    if skill_name == "open_chrome":
        return open_chrome()
    elif skill_name == "open_youtube":
        return open_youtube()
    elif skill_name == "get_time":
        return "Il est l'heure de coder." # TODO: Vraie heure
    else:
        return f"Compétence inconnue : {skill_name}"

def open_chrome():
    """Ouvre Google Chrome."""
    path = config.get_app_path("chrome")
    
    # Si le chemin est défini et existe, on l'utilise
    if path and os.path.exists(path):
        try:
            subprocess.Popen([path])
            return "J'ouvre Google Chrome (via chemin configuré)."
        except Exception as e:
            return f"Erreur ouverture Chrome : {e}"
            
    # Sinon fallback système
    system = platform.system()
    try:
        if system == "Windows":
            os.system("start chrome")
            return "J'ouvre Google Chrome (commande système)."
        else:
            return "Je ne peux ouvrir Chrome que sur Windows pour l'instant."
    except Exception as e:
        return f"Erreur lors de l'ouverture de Chrome : {e}"

def open_youtube():
    """Ouvre YouTube dans le navigateur par défaut."""
    url = config.get_app_path("youtube_url") or "https://www.youtube.com"
    webbrowser.open(url)
    return "J'ouvre YouTube."
