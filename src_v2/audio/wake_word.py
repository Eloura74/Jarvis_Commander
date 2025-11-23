"""
Module de détection du wake word "jarvis" pour Jarvis Commander.
Utilise Picovoice Porcupine pour une détection locale ultra-rapide.
"""

import logging
import struct
import numpy as np
import sounddevice as sd
from typing import Optional, Callable
import threading

logger = logging.getLogger(__name__)

# Import conditionnel de pvporcupine
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    logger.warning("pvporcupine n'est pas installé. Le wake word ne fonctionnera pas.")


class WakeWordDetector:
    """Détecteur de wake word "jarvis" utilisant Porcupine."""
    
    def __init__(
        self,
        access_key: str,
        sensitivity: float = 0.7,
        device_index: Optional[int] = None,
        callback: Optional[Callable] = None,
        level_callback: Optional[Callable[[float], None]] = None
    ):
        """
        Initialise le détecteur de wake word.
        
        Args:
            access_key: Clé API Picovoice
            sensitivity: Sensibilité (0.0 à 1.0)
            device_index: Index du périphérique audio
            callback: Fonction appelée lors de la détection du wake word
            level_callback: Fonction appelée avec le niveau audio (0.0 à 1.0)
        """
        self.access_key = access_key
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        self.device_index = device_index
        self.callback = callback
        self.level_callback = level_callback
        self.porcupine = None
        self.is_listening = False
        self.listen_thread = None
        
        if not PORCUPINE_AVAILABLE:
            logger.error("pvporcupine non disponible")
            return
        
        if not access_key or access_key == "VOTRE_CLE_API_PICOVOICE_ICI":
            logger.error("Clé API Picovoice invalide")
            return
        
        self._initialize_porcupine()

    def _initialize_porcupine(self):
        """Initialise l'instance de Porcupine."""
        try:
            # Mots clés disponibles par défaut dans Porcupine (version gratuite)
            keywords = ["jarvis"]
            
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=keywords,
                sensitivities=[self.sensitivity] * len(keywords)
            )
            logger.info(f"✅ Porcupine initialisé (Wake Word: {keywords})")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Porcupine : {e}")
            self.porcupine = None

    def start_listening(self) -> bool:
        """
        Démarre l'écoute du wake word dans un thread séparé.
        
        Returns:
            True si démarré avec succès, False sinon
        """
        if not PORCUPINE_AVAILABLE or not self.porcupine:
            logger.error("Impossible de démarrer : Porcupine non initialisé")
            return False
            
        if self.is_listening:
            logger.warning("Déjà en train d'écouter")
            return True
            
        try:
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            logger.info("👂 Écoute du wake word démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage écoute : {e}")
            self.is_listening = False
            return False


    def _listen_loop(self):
        """Boucle d'écoute principale (exécutée dans un thread)."""
        try:
            # Buffer pour stocker les échantillons audio
            audio_buffer = []
            
            def audio_callback(indata, frames, time, status):
                """Callback appelé pour chaque bloc audio."""
                if status:
                    logger.warning(f"Status audio : {status}")
                
                # Convertir en int16 pour Porcupine
                audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
                audio_buffer.extend(audio_int16)
                
                # Calculer le niveau RMS pour le visualiseur
                if self.level_callback:
                    rms = np.sqrt(np.mean(indata[:, 0]**2))
                    # Normaliser un peu (0.1 est déjà fort)
                    level = min(1.0, rms * 10)
                    try:
                        self.level_callback(level)
                    except:
                        pass
            
            # Ouvrir le flux audio
            logger.info(f"🔍 Tentative d'ouverture du flux audio sur le device #{self.device_index}")
            with sd.InputStream(
                samplerate=self.porcupine.sample_rate,
                channels=1,
                dtype='float32',
                callback=audio_callback,
                device=self.device_index,
                blocksize=self.porcupine.frame_length
            ):
                logger.info(f"✅ Flux audio ouvert sur device #{self.device_index}, en attente du wake word...")
                
                while self.is_listening:
                    # Vérifier si on a assez d'échantillons
                    if len(audio_buffer) >= self.porcupine.frame_length:
                        # Extraire une frame
                        frame = audio_buffer[:self.porcupine.frame_length]
                        audio_buffer = audio_buffer[self.porcupine.frame_length:]
                        
                        # Détecter le wake word
                        keyword_index = self.porcupine.process(frame)
                        
                        if keyword_index >= 0:
                            logger.info("🎯 Wake word 'jarvis' détecté!")
                            
                            # Appeler le callback si défini
                            if self.callback:
                                try:
                                    self.callback()
                                except Exception as e:
                                    logger.error(f"Erreur dans le callback du wake word : {e}")
                    else:
                        # Attendre un peu si pas assez de données
                        sd.sleep(10)
                        
        except Exception as e:
            logger.error(f"Erreur dans la boucle d'écoute : {e}")
        finally:
            logger.info("Boucle d'écoute terminée")
    
    def stop_listening(self):
        """Arrête l'écoute du wake word."""
        if not self.is_listening:
            return
        
        logger.info("Arrêt de l'écoute du wake word...")
        self.is_listening = False
        
        # Attendre la fin du thread
        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)
        
        logger.info("Écoute du wake word arrêtée")
    
    def set_sensitivity(self, sensitivity: float):
        """
        Modifie la sensibilité du détecteur.
        Nécessite un redémarrage de l'écoute.
        
        Args:
            sensitivity: Nouvelle sensibilité (0.0 à 1.0)
        """
        was_listening = self.is_listening
        
        if was_listening:
            self.stop_listening()
        
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        
        # Réinitialiser Porcupine
        self.cleanup()
        self._initialize_porcupine()
        
        if was_listening:
            self.start_listening()
        
        logger.info(f"Sensibilité modifiée : {self.sensitivity}")
    
    def cleanup(self):
        """Nettoie les ressources de Porcupine."""
        try:
            self.stop_listening()
            
            if self.porcupine:
                self.porcupine.delete()
                self.porcupine = None
                logger.info("Porcupine nettoyé")
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de Porcupine : {e}")
