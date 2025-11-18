"""
Module de synthèse vocale (Text-To-Speech) pour Jarvis Commander.
Utilise pyttsx3 pour une TTS locale rapide et fiable.
"""

import pyttsx3
import logging
from typing import Optional
import threading

logger = logging.getLogger(__name__)


class TTSEngine:
    """Moteur de synthèse vocale thread-safe."""
    
    def __init__(self, rate: int = 180, volume: float = 0.9, voice: Optional[str] = None):
        """
        Initialise le moteur TTS.
        
        Args:
            rate: Vitesse de parole en mots par minute (défaut: 180)
            volume: Volume de 0.0 à 1.0 (défaut: 0.9)
            voice: ID de la voix spécifique ou None pour la voix par défaut
        """
        self.rate = rate
        self.volume = volume
        self.voice_id = voice
        self.engine = None
        self.lock = threading.Lock()
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialise le moteur pyttsx3."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Sélectionner la voix si spécifiée
            if self.voice_id:
                self.engine.setProperty('voice', self.voice_id)
            else:
                # Tenter de sélectionner une voix française par défaut
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        logger.info(f"Voix française sélectionnée : {voice.name}")
                        break
            
            logger.info("Moteur TTS initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du moteur TTS : {e}")
            self.engine = None
    
    def parler(self, texte: str) -> bool:
        """
        Prononce le texte donné.
        
        Args:
            texte: Le texte à prononcer
            
        Returns:
            True si succès, False sinon
        """
        if not texte or not texte.strip():
            logger.warning("Texte vide fourni à TTS")
            return False
        
        if not self.engine:
            logger.error("Moteur TTS non initialisé")
            return False
        
        try:
            with self.lock:
                logger.info(f"TTS : {texte}")
                self.engine.say(texte)
                self.engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse vocale : {e}")
            # Tenter de réinitialiser le moteur
            try:
                self._initialize_engine()
            except:
                pass
            return False
    
    def parler_async(self, texte: str):
        """
        Prononce le texte de manière asynchrone (non-bloquante).
        
        Args:
            texte: Le texte à prononcer
        """
        thread = threading.Thread(target=self.parler, args=(texte,), daemon=True)
        thread.start()
    
    def arreter(self):
        """Arrête la synthèse vocale en cours."""
        try:
            if self.engine:
                with self.lock:
                    self.engine.stop()
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du moteur TTS : {e}")
    
    def set_rate(self, rate: int):
        """Modifie la vitesse de parole."""
        try:
            self.rate = rate
            if self.engine:
                self.engine.setProperty('rate', rate)
                logger.info(f"Vitesse de parole modifiée : {rate} mpm")
        except Exception as e:
            logger.error(f"Erreur lors de la modification de la vitesse : {e}")
    
    def set_volume(self, volume: float):
        """Modifie le volume (0.0 à 1.0)."""
        try:
            self.volume = max(0.0, min(1.0, volume))
            if self.engine:
                self.engine.setProperty('volume', self.volume)
                logger.info(f"Volume modifié : {self.volume}")
        except Exception as e:
            logger.error(f"Erreur lors de la modification du volume : {e}")
    
    def get_voices(self) -> list:
        """
        Récupère la liste des voix disponibles.
        
        Returns:
            Liste des voix disponibles avec leurs propriétés
        """
        try:
            if self.engine:
                voices = self.engine.getProperty('voices')
                return [{'id': v.id, 'name': v.name, 'languages': v.languages} for v in voices]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des voix : {e}")
        return []
    
    def cleanup(self):
        """Nettoie les ressources du moteur TTS."""
        try:
            if self.engine:
                self.engine.stop()
                self.engine = None
                logger.info("Moteur TTS nettoyé")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du moteur TTS : {e}")
