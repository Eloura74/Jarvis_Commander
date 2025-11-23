import os
import sys
import threading
import asyncio
import logging
import yaml
from nicegui import ui, app

# Plus besoin de sys.path hack car tout est dans le même package
from brain import Brain
from ui import build as build_ui

# Imports Backend (Locaux maintenant)
from audio.wake_word import WakeWordDetector
from audio.stt import STTEngine
from audio.tts import TTSEngine
from nlu.intent_parser import IntentParser
from actions.system_control import SystemController
# On garde config_manager pour l'UI mais on charge le yaml pour le backend
from config_manager import config as ui_config

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JarvisController:
    """Contrôleur principal pour Jarvis V2."""
    
    _instance_initialized = False

    def __init__(self, ui_instance):
        self.ui = ui_instance
        self.is_active = False
        self.is_processing = False
        self.backend_config = {}
        
        # Charger la config YAML complète pour le backend
        self._load_backend_config()
        
        # Composants
        self.wake_word_detector = None
        self.stt_engine = None
        self.tts_engine = None
        self.intent_parser = None
        self.system_controller = None
        
        # Threading
        self.loop_thread = None
        
    def _load_backend_config(self):
        """Charge config/config.yaml."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                self.backend_config = yaml.safe_load(f)
            logger.info("Config backend chargée")
        except Exception as e:
            logger.error(f"Erreur chargement config backend: {e}")
            self.backend_config = {}

    def initialize_components(self):
        """Initialise les composants backend."""
        if JarvisController._instance_initialized:
            logger.warning("JarvisController déjà initialisé, ignoré.")
            return

        self.ui.add_log("INITIALISATION DU NOYAU...", "SYS")
        
        try:
            # 1. TTS
            tts_conf = self.backend_config.get('tts', {})
            self.tts_engine = TTSEngine(
                rate=tts_conf.get('rate', 180),
                volume=tts_conf.get('volume', 0.9),
                voice=tts_conf.get('voice')
            )
            self.ui.add_log("MODULE TTS: OK", "SYS")
            
            # 2. STT
            stt_conf = self.backend_config.get('stt', {})
            audio_conf = self.backend_config.get('audio', {})
            self.stt_engine = STTEngine(
                model_size=stt_conf.get('model', 'tiny'),
                language=stt_conf.get('language', 'fr'),
                use_gpu=stt_conf.get('use_gpu', False),
                enable_noise_reduction=stt_conf.get('enable_noise_reduction', True),
                enable_vad=stt_conf.get('enable_vad', True),
                level_callback=self.ui.update_audio_level_threadsafe  # Callback visuel thread-safe
            )
            self.ui.add_log("MODULE STT: OK (Whisper Tiny)", "SYS")
            
            # 3. Wake Word
            ww_conf = self.backend_config.get('wake_word', {})
            self.wake_word_detector = WakeWordDetector(
                access_key=ww_conf.get('access_key', ''),
                sensitivity=ww_conf.get('sensitivity', 0.7),
                device_index=audio_conf.get('input_device_index'),
                callback=self._on_wake_word_detected,
                level_callback=self.ui.update_audio_level_threadsafe  # Callback visuel thread-safe
            )
            self.ui.add_log("DÉTECTEUR WAKE WORD: OK", "SYS")
            
            # 4. NLU & Actions
            self.intent_parser = IntentParser(
                self.backend_config.get('app_aliases', {}), 
                self.backend_config.get('applications', {})
            )
            self.system_controller = SystemController(self.backend_config.get('applications', {}))
            self.ui.add_log("SYSTÈMES DE CONTRÔLE: OK", "SYS")
            
            self.ui.add_log("TOUS LES SYSTÈMES OPÉRATIONNELS", "SYS")
            JarvisController._instance_initialized = True
            
        except Exception as e:
            logger.error(f"Erreur init: {e}")
            self.ui.add_log(f"ERREUR CRITIQUE: {e}", "ERR")

    def start_listening(self):
        """Démarre l'écoute du wake word."""
        if self.wake_word_detector and not self.is_active:
            if self.wake_word_detector.start_listening():
                self.is_active = True
                self.ui.status_label.text = "EN VEILLE"
                self.ui.add_log("SURVEILLANCE AUDIO ACTIVÉE", "AUDIO")
            else:
                self.ui.add_log("ÉCHEC ACTIVATION MICRO", "ERR")

    def _on_wake_word_detected(self):
        """Callback quand 'Jarvis' est entendu."""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        # Lancer le traitement dans un thread pour ne pas bloquer l'UI
        threading.Thread(target=self._process_command_loop, daemon=True).start()

    def _process_command_loop(self):
        """Boucle de traitement d'une commande."""
        try:
            # 1. Pause Wake Word
            if self.wake_word_detector:
                self.wake_word_detector.stop_listening()
                # time.sleep(0.5) # SUPPRIMÉ pour vitesse
            
            # Update UI -> LISTENING
            self.ui.set_state_threadsafe("LISTENING")
            self.ui.add_log_threadsafe("WAKE WORD DÉTECTÉ", "AUDIO")
            
            # 2. Feedback Audio (SUPPRIMÉ pour vitesse)
            # if self.tts_engine:
            #     self.ui.set_state_threadsafe("SPEAKING")
            #     self.tts_engine.parler("Oui ?")
            #     self.tts_engine.wait_until_finished() 
            #     self.ui.set_state_threadsafe("LISTENING")
            
            # 3. Écoute
            audio_conf = self.backend_config.get('audio', {})
            texte = self.stt_engine.ecouter_et_transcrire(
                device_index=audio_conf.get('input_device_index')
            )
            
            if not texte:
                self.ui.add_log_threadsafe("Aucune voix détectée", "AUDIO")
                self.ui.set_state_threadsafe("IDLE")
                if self.tts_engine:
                    self.ui.set_state_threadsafe("SPEAKING")
                    self.tts_engine.parler("Je n'ai rien entendu.")
                    self.tts_engine.wait_until_finished()
                    self.ui.set_state_threadsafe("IDLE")
                return

            self.ui.add_log_threadsafe(f"COMMANDE: '{texte}'", "USR")
            self.ui.set_state_threadsafe("PROCESSING")
            
            # 4. Analyse
            intent_data = self.intent_parser.parse(texte)
            intent = intent_data['intent']
            params = intent_data['parameters']
            self.ui.add_log_threadsafe(f"INTENTION: {intent}", "AI")
            
            # 5. Exécution
            self._execute_action(intent, params)
            
            # Attendre la fin de la réponse vocale avant de reprendre l'écoute
            if self.tts_engine:
                self.tts_engine.wait_until_finished()
            
        except Exception as e:
            logger.error(f"Erreur process: {e}")
            self.ui.add_log_threadsafe(f"ERREUR TRAITEMENT: {e}", "ERR")
            if self.tts_engine:
                self.ui.set_state_threadsafe("SPEAKING")
                self.tts_engine.parler("Erreur système.")
                self.tts_engine.wait_until_finished()
                
        finally:
            self.is_processing = False
            self.ui.set_state_threadsafe("IDLE")
            
            # Reprise Wake Word
            if self.wake_word_detector:
                self.wake_word_detector.start_listening()

    def _execute_action(self, intent, params):
        """Exécute l'action demandée."""
        response = ""
        success = False
        
        if intent == 'open_app':
            app_name = params.get('app_name', '')
            # Vérifier si l'app est connue avant de tenter l'ouverture
            if self.system_controller.get_app_path(app_name):
                success, real_name = self.system_controller.open_app(app_name)
                response = f"J'ouvre {real_name} immédiatement." if success else f"Je n'arrive pas à lancer {real_name}."
            else:
                # App inconnue, on ne dit rien ou une phrase plus douce
                logger.warning(f"App inconnue demandée : {app_name}")
                response = f"Je ne connais pas l'application {app_name}."
            
        elif intent == 'close_app':
            app_name = params.get('app_name', '')
            success, real_name = self.system_controller.close_app(app_name)
            response = f"Je ferme {real_name} pour vous." if success else f"Je ne peux pas fermer {real_name}."
            
        elif intent == 'web_search':
            query = params.get('query', '')
            if query:
                success = self.system_controller.web_search(query)
                response = f"Je recherche '{query}' sur Comet." if success else "Impossible de lancer la recherche."
            else:
                response = "Que voulez-vous que je cherche ?"
            
        elif intent == 'small_talk':
            st_type = params.get('type', 'unknown')
            if st_type == 'greeting':
                import random
                response = random.choice(["Bonjour commandant.", "Salut.", "Je suis à l'écoute.", "Systèmes prêts."])
            elif st_type == 'thanks':
                response = "Je vous en prie."
            elif st_type == 'goodbye':
                response = "Au revoir, à bientôt."
                # Optionnel : self.stop()
            elif st_type == 'status':
                response = "Tous les systèmes sont opérationnels et prêts."
            else:
                response = "Je suis là."
            success = True

        # ... Ajouter les autres intents ici ...
        
        else:
            # Fallback sur le Brain LLM si pas de commande système
            if self.ui.brain:
                # On ne répond que si le brain est confiant ou si c'est une vraie question
                # Pour l'instant on simplifie : on ne répond pas "Commande inconnue" vocalement
                response = self.ui.brain.think(params.get('text', '')) 
                success = True
            else:
                # Silence radio pour les commandes non comprises
                response = "" 
        
        if response:
            self.ui.add_log_threadsafe(f"RÉPONSE: {response}", "SYS")
            if self.tts_engine:
                self.tts_engine.parler(response)


def main():
    # 1. Chargement du Cerveau
    print("🧠 Initialisation du cerveau...")
    brain = Brain()
    
    # 2. Construction de l'interface
    print("🖥️ Lancement de l'interface...")
    jarvis_ui = build_ui(brain)
    
    # 3. Initialisation du Contrôleur Backend
    controller = JarvisController(jarvis_ui)
    
    # Hook sur le démarrage de l'UI pour lancer les composants
    async def on_startup():
        # On attend un peu que l'UI soit affichée
        await asyncio.sleep(1)
        # Initialisation lourde en background pour ne pas bloquer l'affichage initial
        # Initialisation lourde en background
        await asyncio.to_thread(controller.initialize_components)
        
        # Démarrage automatique de l'écoute (plus besoin de cliquer pour le backend)
        controller.start_listening()
        
        # On connecte quand même le bouton pour l'animation UI si pas encore fait
        if hasattr(jarvis_ui, 'start_system'):
             # On garde l'anim UI mais le backend est déjà lancé
             pass
        
    # Utilisation de ui.timer pour le démarrage en mode script (app.on_startup pose problème ici)
    ui.timer(0.1, on_startup, once=True)
    
    # 4. Démarrage
    ui.run(title='Jarvis Commander V2', dark=True, reload=False, port=8080)

if __name__ == "__main__":
    main()
