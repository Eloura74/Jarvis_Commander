"""
Module d'indexation des applications Windows.
Scanne le menu démarrer et le système pour trouver toutes les applications exécutables.
"""

import os
import json
import time
import logging
import win32com.client
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AppIndexer:
    """Indexeur d'applications Windows via Shell."""
    
    def __init__(self, cache_file: str = "app_cache.json"):
        self.cache_file = os.path.join(os.path.dirname(__file__), "..", "config", cache_file)
        self.apps: Dict[str, str] = {}
        
    def get_installed_apps(self, force_refresh: bool = False) -> Dict[str, str]:
        """
        Récupère la liste des applications installées.
        Utilise le cache si disponible et récent.
        """
        if not force_refresh and self._load_cache():
            return self.apps
            
        logger.info("Indexation des applications en cours (cela peut prendre quelques secondes)...")
        self._scan_shell_apps()
        self._save_cache()
        return self.apps
    
    def _scan_shell_apps(self):
        """Scanne le dossier virtuel Applications de Windows."""
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            # "AppsFolder" est le dossier virtuel contenant toutes les apps installées (Store + Win32)
            apps_folder = shell.NameSpace("shell:AppsFolder")
            
            if not apps_folder:
                logger.error("Impossible d'accéder au dossier Applications.")
                return

            count = 0
            for item in apps_folder.Items():
                try:
                    name = item.Name
                    path = item.Path
                    
                    # Certaines apps UWP ont des chemins bizarres, on filtre ce qui est utilisable
                    # Pour les apps UWP, le path est souvent vide ou un ID.
                    # On essaie de récupérer le chemin d'analyse (parsing name)
                    if not path:
                        # Astuce pour lancer les apps UWP: shell:AppsFolder\PackageFamilyName!AppId
                        # Mais win32com ne donne pas toujours ça facilement.
                        # On va se concentrer sur ce qui a un chemin ou qui semble être un raccourci valide.
                        pass
                        
                    # Nettoyage du nom
                    clean_name = name.lower().strip()
                    
                    # On stocke le nom -> chemin (ou commande de lancement)
                    # Pour shell:AppsFolder, le "path" retourné par item.Path est souvent le chemin de l'exe
                    # Si c'est vide, on peut utiliser le parsing name pour `explorer.exe shell:AppsFolder\ParsingName`
                    
                    parsing_name = item.GetFolder.GetDetailsOf(item, 194) # 194 = Parsing Name parfois ? Non, instable.
                    # Plus simple : on utilise l'objet FolderItem pour obtenir le chemin
                    
                    # WORKAROUND: Pour lancer n'importe quelle app du dossier AppsFolder,
                    # on peut utiliser `explorer.exe shell:AppsFolder\<ParsingName>`
                    # Mais récupérer le ParsingName via win32com est pénible.
                    
                    # Approche hybride :
                    # 1. Si c'est un .lnk ou .exe direct, on prend le chemin.
                    # 2. Sinon, on ignore pour l'instant (v1) pour éviter les faux positifs.
                    
                    if path and (path.endswith('.exe') or path.endswith('.lnk')):
                        self.apps[clean_name] = path
                        count += 1
                        
                except Exception as e:
                    continue
                    
            # Ajout manuel des scans de dossiers Start Menu pour compléter
            self._scan_directory(os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"))
            self._scan_directory(os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"))
            
            logger.info(f"Indexation terminée : {len(self.apps)} applications trouvées.")
            
        except Exception as e:
            logger.error(f"Erreur critique lors du scan des apps : {e}")

    def _scan_directory(self, directory: str):
        """Scanne récursivement un dossier pour trouver des raccourcis."""
        if not os.path.exists(directory):
            return

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".lnk"):
                    name = os.path.splitext(file)[0].lower()
                    full_path = os.path.join(root, file)
                    self.apps[name] = full_path

    def _load_cache(self) -> bool:
        """Charge le cache JSON."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.apps = data
                logger.info(f"Cache chargé : {len(self.apps)} apps.")
                return True
        except Exception:
            pass
        return False

    def _save_cache(self):
        """Sauvegarde le cache JSON."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.apps, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache : {e}")

if __name__ == "__main__":
    # Test autonome
    logging.basicConfig(level=logging.INFO)
    indexer = AppIndexer()
    apps = indexer.get_installed_apps(force_refresh=True)
    print(f"Trouvé {len(apps)} applications.")
    # Affiche quelques exemples
    for k in list(apps.keys())[:10]:
        print(f"- {k} : {apps[k]}")
