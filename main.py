"""
Point d'entrée principal de Jarvis Commander.
Orchestre tous les modules : wake word, STT, TTS, NLU, actions système et UI.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
import yaml
import threading
from typing import Optional, Dict, Any

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot

# Imports des modules Jarvis
from audio.wake_word import WakeWordDetector
from audio.stt import STTEngine
from audio.tts import TTSEngine
from nlu.intent_parser import IntentParser
from actions.system_control import SystemController
from ui.main_window import JarvisMainWindow


class JarvisController(QObject):
    """Contrôleur principal de Jarvis Commander."""
    
    # Signaux
    log_signal = Signal(str, str)  # message, level
    status_signal = Signal(str)  # status
    
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__()
        
        self.config_path = config_path
        self.config = None
        self.is_active = False
        self.is_processing = False
        
        # Composants
        self.wake_word_detector: Optional[WakeWordDetector] = None
        self.stt_engine: Optional[STTEngine] = None
        self.tts_engine: Optional[TTSEngine] = None
        self.intent_parser: Optional[IntentParser] = None
        self.system_controller: Optional[SystemController] = None
        self.window: Optional[JarvisMainWindow] = None
        
        # Initialiser le logging
        self._setup_logging()
        
        # Charger la configuration
        self._load_config()
    
    def _setup_logging(self):
        """Configure le système de logging."""
        # Créer le dossier logs s'il n'existe pas
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Nom du fichier de log avec date
        log_file = log_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("Jarvis Commander - Démarrage")
        self.logger.info("=" * 60)
    
    def _load_config(self):
        """Charge le fichier de configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Configuration chargée depuis {self.config_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la config : {e}")
            # Configuration par défaut minimale OPTIMISÉE
            self.config = {
                'applications': {},
                'audio': {
                    'sample_rate': 16000,
                    'silence_threshold': 0.01,
                    'silence_duration': 0.8,  # Optimisé pour réactivité
                    'max_record_duration': 8.0  # Optimisé pour commandes courtes
                },
                'wake_word': {'sensitivity': 0.7, 'access_key': ''},
                'stt': {
                    'model': 'tiny',  # Optimisé pour vitesse
                    'language': 'fr',
                    'use_gpu': False,  # CUDA incomplet
                    'compute_type': 'int8',  # CPU optimisé
                    'enable_noise_reduction': True,  # Filtre le bruit
                    'enable_vad': True  # Détection de voix
                },
                'tts': {'rate': 180, 'volume': 0.9},
                'logging': {'level': 'INFO'}
            }
    
    def initialize_components(self):
        """Initialise tous les composants de Jarvis."""
        self.logger.info("Initialisation des composants...")
        
        # 1. TTS Engine
        tts_config = self.config.get('tts', {})
        self.tts_engine = TTSEngine(
            rate=tts_config.get('rate', 180),
            volume=tts_config.get('volume', 0.9),
            voice=tts_config.get('voice')
        )
        self._emit_log("Moteur TTS initialisé", "INFO")
        
        # 2. STT Engine (avec nouvelles optimisations audio)
        stt_config = self.config.get('stt', {})
        audio_config = self.config.get('audio', {})
        self.stt_engine = STTEngine(
            model_size=stt_config.get('model', 'tiny'),  # Changé de 'small' à 'tiny' par défaut
            language=stt_config.get('language', 'fr'),
            use_gpu=stt_config.get('use_gpu', False),  # Changé de True à False (CUDA incomplet)
            compute_type=stt_config.get('compute_type', 'int8'),  # Changé de 'float16' à 'int8'
            sample_rate=audio_config.get('sample_rate', 16000),
            silence_threshold=audio_config.get('silence_threshold', 0.01),
            silence_duration=audio_config.get('silence_duration', 0.8),  # Changé de 1.5 à 0.8
            max_duration=audio_config.get('max_record_duration', 8.0),  # Changé de 10.0 à 8.0
            enable_noise_reduction=stt_config.get('enable_noise_reduction', True),  # NOUVEAU
            enable_vad=stt_config.get('enable_vad', True)  # NOUVEAU
        )
        self._emit_log("Moteur STT initialisé (optimisé pour vitesse)", "INFO")
        
        # 3. Intent Parser
        app_aliases = self.config.get('app_aliases', {})
        app_paths = self.config.get('applications', {})
        self.intent_parser = IntentParser(app_aliases, app_paths)
        self._emit_log("Parseur d'intentions initialisé", "INFO")
        
        # 4. System Controller
        app_paths = self.config.get('applications', {})
        self.system_controller = SystemController(app_paths)
        self._emit_log("Contrôleur système initialisé", "INFO")
        
        # 5. Wake Word Detector
        ww_config = self.config.get('wake_word', {})
        self.wake_word_detector = WakeWordDetector(
            access_key=ww_config.get('access_key', ''),
            sensitivity=ww_config.get('sensitivity', 0.7),
            device_index=audio_config.get('input_device_index'),
            callback=self._on_wake_word_detected
        )
        self._emit_log("Détecteur de wake word initialisé", "INFO")
        
        self.logger.info("Tous les composants sont initialisés")
    
    def _on_wake_word_detected(self):
        """Callback appelé lorsque le wake word est détecté."""
        if self.is_processing:
            self.logger.warning("Déjà en train de traiter une commande, ignoré")
            return
        
        self.is_processing = True
        
        # Lancer le traitement dans un thread séparé
        thread = threading.Thread(target=self._process_command, daemon=True)
        thread.start()
    
    def _process_command(self):
        """Traite une commande vocale complète."""
        try:
            self._emit_status('recording')
            self._emit_log("🎯 Wake word détecté!", "INFO")
            
            # Répondre à l'utilisateur
            self.tts_engine.parler("Oui ?")
            
            # Enregistrer et transcrire
            self._emit_log("Enregistrement en cours...", "INFO")
            audio_config = self.config.get('audio', {})
            texte = self.stt_engine.ecouter_et_transcrire(
                device_index=audio_config.get('input_device_index')
            )
            
            if not texte:
                self._emit_log("Aucun texte transcrit", "WARNING")
                self.tts_engine.parler("Je n'ai rien entendu.")
                self._emit_status('listening')
                return
            
            self._emit_log(f"Transcription : {texte}", "INFO")
            
            # Analyser l'intention
            self._emit_status('processing')
            intent_data = self.intent_parser.parse(texte)
            intent = intent_data['intent']
            params = intent_data['parameters']
            
            self._emit_log(f"Intention : {intent} | Params : {params}", "INFO")
            
            # Exécuter l'action
            self._emit_status('executing')
            self._execute_action(intent, params)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement : {e}", exc_info=True)
            self._emit_log(f"Erreur : {e}", "ERROR")
            self.tts_engine.parler("Désolé, une erreur s'est produite.")
            self._emit_status('error')
            
        finally:
            self.is_processing = False
            self._emit_status('listening')
    
    def _execute_action(self, intent: str, params: Dict[str, Any]):
        """
        Exécute l'action correspondant à l'intention.
        
        Args:
            intent: Type d'intention
            params: Paramètres de l'intention
        """
        success = False
        response = ""
        
        if intent == 'open_app':
            app_name = params.get('app_name', '')
            success = self.system_controller.open_app(app_name)
            response = f"J'ouvre {app_name}" if success else f"Je ne peux pas ouvrir {app_name}"
            
        elif intent == 'close_app':
            app_name = params.get('app_name', '')
            success = self.system_controller.close_app(app_name)
            response = f"Je ferme {app_name}" if success else f"Je ne peux pas fermer {app_name}"
            
        elif intent == 'web_search':
            query = params.get('query', '')
            success = self.system_controller.web_search(query)
            response = f"Recherche de {query}" if success else "Impossible d'effectuer la recherche"
            
        elif intent == 'scroll_down':
            amount = params.get('amount', 3)
            success = self.system_controller.scroll_down(amount)
            response = "Je descends" if success else "Erreur de scroll"
            
        elif intent == 'scroll_up':
            amount = params.get('amount', 3)
            success = self.system_controller.scroll_up(amount)
            response = "Je remonte" if success else "Erreur de scroll"
            
        elif intent == 'dictation':
            text = params.get('text', '')
            success = self.system_controller.type_text(text)
            response = "Texte saisi" if success else "Erreur de saisie"
            
        elif intent == 'close_window':
            success = self.system_controller.close_active_window()
            response = "Je ferme la fenêtre" if success else "Erreur"
            
        elif intent == 'file_search':
            query = params.get('query', '')
            extension = params.get('extension')
            drive = params.get('drive')
            
            response = f"Recherche de fichiers : {query}"
            self.tts_engine.parler(response)
            
            # Lancer la recherche en async
            def on_search_complete(results):
                count = len(results)
                msg = f"J'ai trouvé {count} fichier{'s' if count > 1 else ''}"
                self.tts_engine.parler(msg)
                self._emit_log(f"Fichiers trouvés : {count}", "INFO")
                for path in results[:5]:  # Afficher les 5 premiers
                    self._emit_log(f"  - {path}", "INFO")
            
            self.system_controller.search_files_async(
                query, extension, drive,
                callback=on_search_complete
            )
            return  # Pas de réponse immédiate
            
        else:
            response = "Je n'ai pas compris la commande"
            success = False
        
        # Répondre à l'utilisateur
        self.tts_engine.parler(response)
        
        level = "INFO" if success else "WARNING"
        self._emit_log(f"Action : {response}", level)
    
    def start(self):
        """Démarre Jarvis (écoute du wake word)."""
        if self.is_active:
            self.logger.warning("Jarvis est déjà actif")
            return
        
        self.logger.info("Démarrage de Jarvis...")
        self._emit_log("Démarrage de l'écoute...", "INFO")
        
        if self.wake_word_detector and self.wake_word_detector.start_listening():
            self.is_active = True
            self._emit_status('listening')
            self._emit_log("✅ Jarvis est à l'écoute", "INFO")
            self.tts_engine.parler("Jarvis activé")
        else:
            self._emit_log("❌ Impossible de démarrer l'écoute", "ERROR")
            self._emit_status('error')
    
    def stop(self):
        """Arrête Jarvis."""
        if not self.is_active:
            return
        
        self.logger.info("Arrêt de Jarvis...")
        self._emit_log("Arrêt de l'écoute...", "INFO")
        
        if self.wake_word_detector:
            self.wake_word_detector.stop_listening()
        
        self.is_active = False
        self._emit_status('disabled')
        self._emit_log("Jarvis désactivé", "INFO")
        self.tts_engine.parler("Jarvis désactivé")
    
    def cleanup(self):
        """Nettoie les ressources."""
        self.logger.info("Nettoyage des ressources...")
        
        if self.wake_word_detector:
            self.wake_word_detector.cleanup()
        
        if self.stt_engine:
            self.stt_engine.cleanup()
        
        if self.tts_engine:
            self.tts_engine.cleanup()
        
        self.logger.info("Ressources nettoyées")
    
    def _emit_log(self, message: str, level: str = "INFO"):
        """Émet un message de log vers l'UI."""
        self.log_signal.emit(message, level)
    
    def _emit_status(self, status: str):
        """Émet un changement de statut vers l'UI."""
        self.status_signal.emit(status)
    
    def set_window(self, window: JarvisMainWindow):
        """Associe la fenêtre principale."""
        self.window = window

        # Connecter les signaux
        self.log_signal.connect(window.add_log)
        self.status_signal.connect(window.set_status)

        # Connecter le bouton toggle
        window.toggle_btn.clicked.connect(self._toggle_jarvis)

        # Mettre à jour les badges de capacités (anti-bruit, GPU...)
        try:
            window.update_capabilities(self._capabilities_data())
        except Exception:
            self.logger.debug("Impossible de mettre à jour les capacités UI", exc_info=True)

    def _capabilities_data(self) -> Dict[str, Any]:
        """Construit un snapshot des optimisations actives pour l'UI."""
        stt = self.stt_engine
        return {
            'noise_reduction': bool(stt and stt.enable_noise_reduction),
            'vad': bool(stt and stt.enable_vad),
            'fast_mode': bool(stt and stt.model_size in {"tiny", "base"}),
            'gpu': bool(stt and stt.use_gpu and stt.compute_type != "int8"),
            'wake_word': bool(self.wake_word_detector),
        }
    
    @Slot()
    def _toggle_jarvis(self):
        """Active/désactive Jarvis."""
        if self.is_active:
            self.stop()
            self.window.toggle_btn.setText("🎤 Activer Jarvis")
            self.window.toggle_btn.setStyleSheet(
                self.window._get_button_style("#2d7d46")
            )
        else:
            self.start()
            self.window.toggle_btn.setText("⏸️ Désactiver Jarvis")
            self.window.toggle_btn.setStyleSheet(
                self.window._get_button_style("#8b6c2c")
            )


def main():
    """Fonction principale."""
    # Créer l'application Qt
    app = QApplication(sys.argv)
    
    # Créer le contrôleur
    controller = JarvisController()
    
    # Initialiser les composants
    controller.initialize_components()
    
    # Créer et afficher la fenêtre
    window = JarvisMainWindow()
    controller.set_window(window)
    window.show()
    
    # Message initial
    controller._emit_log("Bienvenue dans Jarvis Commander!", "INFO")
    controller._emit_log("Cliquez sur 'Activer Jarvis' pour commencer", "INFO")
    controller._emit_status('idle')
    
    # Gérer la fermeture propre
    def on_exit():
        controller.stop()
        controller.cleanup()
    
    app.aboutToQuit.connect(on_exit)
    
    # Lancer l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
