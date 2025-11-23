# Module Config Manager
# Gère la configuration persistante de l'application.

import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "apps": {
        "chrome": r"C:\Users\faber\AppData\Local\Google\Chrome\Application\chrome.exe",
        "youtube_url": "https://www.youtube.com"
    }
}

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """Charge la configuration depuis le fichier JSON."""
        if not os.path.exists(CONFIG_FILE):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur lecture config: {e}, chargement défaut.")
            return DEFAULT_CONFIG

    def save_config(self, new_config=None):
        """Sauvegarde la configuration."""
        if new_config:
            self.config = new_config
            
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            print("✅ Configuration sauvegardée.")
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")

    def get_app_path(self, app_name):
        """Récupère le chemin d'une application."""
        return self.config.get("apps", {}).get(app_name, "")

    def set_app_path(self, app_name, path):
        """Définit le chemin d'une application."""
        if "apps" not in self.config:
            self.config["apps"] = {}
        self.config["apps"][app_name] = path
        self.save_config()

# Instance globale
config = ConfigManager()
