"""
Module d'actions système pour Jarvis Commander.
Gère l'ouverture/fermeture d'applications, le contrôle clavier/souris, et la recherche de fichiers.
"""

import os
import sys
import logging
import subprocess
import psutil
import pyautogui
import webbrowser
import time
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import threading
import difflib

logger = logging.getLogger(__name__)


class SystemController:
    """Contrôleur d'actions système Windows."""
    
    def __init__(self, app_paths: Optional[Dict[str, str]] = None):
        """
        Initialise le contrôleur système.
        
        Args:
            app_paths: Dictionnaire des applications et leurs chemins
        """
        self.app_paths = app_paths or {}
        
        # Configuration pyautogui pour plus de sécurité
        pyautogui.FAILSAFE = True  # Bouger souris dans coin = arrêt
        pyautogui.PAUSE = 0.1  # Pause entre les actions
    
    def set_app_paths(self, app_paths: Dict[str, str]):
        """
        Définit les chemins des applications.
        
        Args:
            app_paths: Dictionnaire {nom_app: chemin_executable}
        """
        self.app_paths = app_paths
        logger.info(f"Chemins d'applications configurés : {len(app_paths)} entrées")

    def get_app_path(self, app_name: str) -> Optional[str]:
        """
        Récupère le chemin d'une application si elle existe.
        
        Args:
            app_name: Nom de l'application
            
        Returns:
            Chemin de l'application ou None
        """
        matched_app = self._find_best_app_match(app_name)
        if matched_app:
            return self.app_paths[matched_app]
        return None
    
    def _find_best_app_match(self, app_name: str) -> Optional[str]:
        """
        Trouve la meilleure correspondance d'application même avec des erreurs de transcription.
        
        Args:
            app_name: Nom de l'application (peut contenir des erreurs)
            
        Returns:
            Nom exact de l'application ou None
        """
        app_name_lower = app_name.lower().strip()
        
        # 1. Correspondance exacte
        if app_name_lower in self.app_paths:
            return app_name_lower
        
        # 2. Correspondance partielle (contient le mot)
        for app_key in self.app_paths.keys():
            if app_name_lower in app_key or app_key in app_name_lower:
                logger.info(f"Correspondance partielle : '{app_name}' → '{app_key}'")
                return app_key
        
        # 3. Correspondance floue (similitude)
        best_match = difflib.get_close_matches(
            app_name_lower, 
            self.app_paths.keys(), 
            n=1, 
            cutoff=0.6  # 60% de similarité minimum
        )
        
        if best_match:
            logger.info(f"Correspondance floue : '{app_name}' → '{best_match[0]}'")
            return best_match[0]
        
        return None
    
    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Ouvre une application.
        
        Args:
            app_name: Nom de l'application
            
        Returns:
            Tuple (succès, nom_app_ouvert)
        """
        # Trouver la meilleure correspondance
        matched_app = self._find_best_app_match(app_name)
        
        if not matched_app:
            logger.error(f"Application '{app_name}' non trouvée dans la configuration")
            return False, app_name
        
        app_path = self.app_paths[matched_app]
        
        # Résoudre les variables d'environnement (%USERNAME%, etc.)
        app_path = os.path.expandvars(app_path)
        
        try:
            logger.info(f"Ouverture de '{matched_app}' : {app_path}")
            
            # Vérifier si le chemin existe (pour les .exe directs)
            if app_path.endswith('.exe') and not os.path.exists(app_path):
                logger.warning(f"Chemin non trouvé : {app_path}")
                # Tenter quand même l'exécution (peut être dans PATH)
            
            # Lancer l'application
            if app_path.lower().endswith('.lnk'):
                # Les raccourcis .lnk doivent être lancés via le shell ou os.startfile
                logger.info(f"Lancement du raccourci : {app_path}")
                os.startfile(app_path)
            elif '--' in app_path:
                # Commande avec arguments (ex: Discord)
                subprocess.Popen(app_path, shell=True)
            else:
                # Exécutable direct
                if app_path.lower().endswith('.exe'):
                    subprocess.Popen([app_path], shell=False)
                else:
                    # Par défaut pour le reste, utiliser le shell
                    subprocess.Popen(app_path, shell=True)
            
            logger.info(f"Application '{matched_app}' lancée avec succès")
            return True, matched_app
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture de '{matched_app}' : {e}")
            return False, matched_app
    
    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Ferme une application.
        
        Args:
            app_name: Nom de l'application
            
        Returns:
            Tuple (succès, nom_app_fermé)
        """
        # Trouver la meilleure correspondance
        matched_app = self._find_best_app_match(app_name)
        
        if not matched_app:
            matched_app = app_name.lower()
        
        # Mapping nom -> nom de processus
        process_names = self._get_process_names(matched_app)
        
        if not process_names:
            logger.warning(f"Aucun nom de processus trouvé pour '{matched_app}'")
            return False, matched_app
        
        closed_count = 0
        
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Vérifier si le processus correspond
                    if any(pn in proc_name for pn in process_names):
                        logger.info(f"Fermeture du processus : {proc.info['name']} (PID: {proc.info['pid']})")
                        
                        # Tenter une fermeture propre
                        proc.terminate()
                        
                        # Attendre un peu
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            # Forcer la fermeture si nécessaire
                            proc.kill()
                        
                        closed_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    continue
            
            if closed_count > 0:
                logger.info(f"Application '{matched_app}' fermée ({closed_count} processus)")
                return True, matched_app
            else:
                logger.warning(f"Aucun processus trouvé pour '{matched_app}'")
                return False, matched_app
                
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de '{matched_app}' : {e}")
            return False, matched_app
    
    def _get_process_names(self, app_name: str) -> List[str]:
        """
        Obtient les noms de processus possibles pour une application.
        
        Args:
            app_name: Nom de l'application
            
        Returns:
            Liste des noms de processus à rechercher
        """
        # Mapping personnalisé
        mapping = {
            'chrome': ['chrome.exe'],
            'firefox': ['firefox.exe'],
            'edge': ['msedge.exe'],
            'bambu_studio': ['bambustudio.exe', 'bambu'],
            'fusion_360': ['fusion360.exe', 'fusion'],
            'discord': ['discord.exe'],
            'vscode': ['code.exe'],
            'notepad': ['notepad.exe'],
            'explorer': ['explorer.exe'],
            'calculator': ['calc.exe', 'calculator.exe'],
        }
        
        if app_name in mapping:
            return mapping[app_name]
        
        # Par défaut, essayer le nom + .exe
        return [f"{app_name}.exe", app_name]
    
    def scroll_down(self, amount: int = 3) -> bool:
        """
        Défile vers le bas.
        
        Args:
            amount: Nombre de "clics" de molette (négatif = vers le bas)
            
        Returns:
            True si succès
        """
        try:
            logger.info(f"Scroll vers le bas : {amount} clics")
            pyautogui.scroll(-amount * 100)  # Négatif = bas
            return True
        except Exception as e:
            logger.error(f"Erreur lors du scroll : {e}")
            return False
    
    def scroll_up(self, amount: int = 3) -> bool:
        """
        Défile vers le haut.
        
        Args:
            amount: Nombre de "clics" de molette (positif = vers le haut)
            
        Returns:
            True si succès
        """
        try:
            logger.info(f"Scroll vers le haut : {amount} clics")
            pyautogui.scroll(amount * 100)  # Positif = haut
            return True
        except Exception as e:
            logger.error(f"Erreur lors du scroll : {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """
        Tape du texte (dictée).
        
        Args:
            text: Texte à taper
            
        Returns:
            True si succès
        """
        try:
            logger.info(f"Saisie de texte : '{text}'")
            
            # Petite pause pour laisser le temps à l'utilisateur de cliquer
            time.sleep(0.5)
            
            # Taper le texte
            pyautogui.write(text, interval=0.05)
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la saisie de texte : {e}")
            return False
    
    def close_active_window(self) -> bool:
        """
        Ferme la fenêtre active (Alt+F4).
        
        Returns:
            True si succès
        """
        try:
            logger.info("Fermeture de la fenêtre active")
            pyautogui.hotkey('alt', 'f4')
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de fenêtre : {e}")
            return False
    
    def web_search(self, query: str) -> bool:
        """
        Ouvre une recherche web (via Comet si disponible, sinon défaut).
        
        Args:
            query: Requête de recherche
            
        Returns:
            True si succès
        """
        try:
            logger.info(f"Recherche web : '{query}'")
            
            # Encoder la requête pour l'URL
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            
            # URL de recherche (Perplexity par défaut pour Comet)
            url = f"https://www.perplexity.ai/search?q={encoded_query}"
            
            # Vérifier si Comet est configuré
            comet_path = self.get_app_path('comet')
            if comet_path and os.path.exists(comet_path):
                logger.info(f"Utilisation de Comet : {comet_path}")
                subprocess.Popen([comet_path, url])
            else:
                logger.info("Comet non trouvé, utilisation du navigateur par défaut")
                webbrowser.open(url)
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la recherche web : {e}")
            return False
    
    def search_files(
        self,
        query: str,
        extension: Optional[str] = None,
        drive: Optional[str] = None,
        max_results: int = 50
    ) -> List[str]:
        """
        Recherche des fichiers sur le(s) disque(s).
        
        Args:
            query: Terme de recherche (dans le nom du fichier)
            extension: Extension à rechercher (ex: "stl")
            drive: Lettre de lecteur (ex: "A") ou None pour tous
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des chemins de fichiers trouvés
        """
        results = []
        query_lower = query.lower()
        
        # Déterminer les lecteurs à parcourir
        if drive:
            drives = [f"{drive.upper()}:\\"]
        else:
            # Tous les lecteurs disponibles
            drives = [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:\\")]
        
        logger.info(f"Recherche de fichiers : query='{query}', ext={extension}, drives={drives}")
        
        try:
            for drive_path in drives:
                if len(results) >= max_results:
                    break
                
                logger.info(f"Parcours de {drive_path}...")
                
                # Parcourir récursivement
                for root, dirs, files in os.walk(drive_path):
                    # Ignorer certains dossiers système
                    dirs[:] = [d for d in dirs if d not in ['$RECYCLE.BIN', 'System Volume Information', 'Windows']]
                    
                    for file in files:
                        # Vérifier l'extension si spécifiée
                        if extension and not file.lower().endswith(f".{extension.lower()}"):
                            continue
                        
                        # Vérifier si le nom contient la requête
                        if query_lower in file.lower():
                            full_path = os.path.join(root, file)
                            results.append(full_path)
                            logger.info(f"Trouvé : {full_path}")
                            
                            if len(results) >= max_results:
                                break
                    
                    if len(results) >= max_results:
                        break
            
            logger.info(f"Recherche terminée : {len(results)} fichiers trouvés")
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de fichiers : {e}")
            return results
    
    def search_files_async(
        self,
        query: str,
        extension: Optional[str] = None,
        drive: Optional[str] = None,
        max_results: int = 50,
        callback=None
    ):
        """
        Recherche de fichiers en arrière-plan (non-bloquant).
        
        Args:
            query: Terme de recherche
            extension: Extension à rechercher
            drive: Lettre de lecteur
            max_results: Nombre max de résultats
            callback: Fonction appelée avec les résultats (callback(results))
        """
        def search_thread():
            results = self.search_files(query, extension, drive, max_results)
            if callback:
                callback(results)
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
