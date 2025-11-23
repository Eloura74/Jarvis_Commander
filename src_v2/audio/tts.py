"""
Module de synthèse vocale (Text-To-Speech) pour Jarvis Commander.
Utilise pyttsx3 avec une file d'attente pour éviter les blocages de thread.
"""

import pyttsx3
import logging
from typing import Optional
import threading
import queue
import time

logger = logging.getLogger(__name__)

class TTSEngine:
    """Moteur de synthèse vocale thread-safe avec file d'attente."""
    
    def __init__(self, rate: int = 180, volume: float = 0.9, voice: Optional[str] = None):
        self.rate = rate
        self.volume = volume
        self.voice_id = voice
        
        # File d'attente pour les messages
        self.queue = queue.Queue()
        self.is_running = True
        
        # Thread dédié au TTS
        self.thread = threading.Thread(target=self._run_loop, daemon=True, name="TTS_Thread")
        self.thread.start()
        
        logger.info("Moteur TTS initialisé (Mode Queue)")

    def _run_loop(self):
        """Boucle principale du thread TTS (Version PowerShell)."""
        import subprocess
        import platform
        
        is_windows = platform.system() == "Windows"
        
        while self.is_running:
            try:
                # Attente bloquante d'un message
                text = self.queue.get(timeout=1.0)
                
                if text is None: # Signal d'arrêt
                    self.queue.task_done()
                    break
                
                logger.info(f"TTS: {text}")
                
                if is_windows:
                    # Échapper les guillemets pour PowerShell
                    safe_text = text.replace("'", "''").replace('"', '`"')
                    
                    # Commande PowerShell pour SAPI
                    voice_cmd = f"$s.SelectVoice('{self.voice_id}');" if self.voice_id else ""
                    
                    ps_command = (
                        f"Add-Type -AssemblyName System.Speech; "
                        f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                        f"{voice_cmd} "
                        f"$s.Rate = {int((self.rate - 180) / 10)}; " # Mapping approximatif rate pyttsx3 -> SAPI (-10 à 10)
                        f"$s.Volume = {int(self.volume * 100)}; "
                        f"$s.Speak('{safe_text}');"
                    )
                    
                    try:
                        # Exécution bloquante
                        subprocess.run(
                            ["powershell", "-NoProfile", "-Command", ps_command],
                            check=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
                    except Exception as e:
                        logger.error(f"Erreur PowerShell TTS: {e}")
                else:
                    # Fallback dummy pour non-Windows (ou remettre pyttsx3 si besoin)
                    logger.warning("TTS PowerShell non supporté sur cet OS")
                    time.sleep(len(text) * 0.1) # Simulation temps de parole
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Erreur boucle TTS: {e}")

    def _configure_engine(self, engine):
        """Non utilisé avec PowerShell."""
        pass

    def parler(self, texte: str):
        """Ajoute le texte à la file d'attente (non-bloquant)."""
        if texte and texte.strip():
            self.queue.put(texte)

    def parler_async(self, texte: str):
        """Alias pour parler (déjà async via queue)."""
        self.parler(texte)

    def wait_until_finished(self):
        """Bloque jusqu'à ce que tout le texte ait été dit."""
        self.queue.join()

    def arreter(self):
        """Arrête le moteur."""
        self.is_running = False
        self.queue.put(None) # Signal d'arrêt
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)

    def cleanup(self):
        self.arreter()

    def get_available_voices(self):
        """Retourne la liste des voix installées via PowerShell."""
        import subprocess
        
        ps_command = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }"
        )
        
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            voices = result.stdout.strip().split('\n')
            return [v.strip() for v in voices if v.strip()]
        except Exception as e:
            logger.error(f"Erreur récupération voix: {e}")
            return []

    def set_voice(self, voice_name: str):
        """Change la voix active."""
        self.voice_id = voice_name
        logger.info(f"Voix changée pour : {voice_name}")
