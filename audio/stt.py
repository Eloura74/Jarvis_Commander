"""
Module de reconnaissance vocale (Speech-To-Text) pour Jarvis Commander.
Utilise faster-whisper pour une transcription locale rapide avec support GPU CUDA.
"""

import logging
import numpy as np
import sounddevice as sd
from typing import Optional, Tuple
import wave
import tempfile
import os

logger = logging.getLogger(__name__)

# Import conditionnel de faster-whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("faster-whisper n'est pas installé. Le module STT ne fonctionnera pas.")


class STTEngine:
    """Moteur de reconnaissance vocale utilisant Whisper."""
    
    def __init__(
        self,
        model_size: str = "small",
        language: str = "fr",
        use_gpu: bool = True,
        compute_type: str = "float16",
        sample_rate: int = 16000,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        max_duration: float = 10.0
    ):
        """
        Initialise le moteur STT.
        
        Args:
            model_size: Taille du modèle Whisper (tiny, base, small, medium, large)
            language: Code langue (fr, en, etc.)
            use_gpu: Utiliser GPU si disponible
            compute_type: Type de calcul (float16 pour GPU, int8 pour CPU)
            sample_rate: Fréquence d'échantillonnage en Hz
            silence_threshold: Seuil de détection du silence (amplitude)
            silence_duration: Durée de silence pour arrêter l'enregistrement
            max_duration: Durée maximale d'enregistrement en secondes
        """
        self.model_size = model_size
        self.language = language
        self.use_gpu = use_gpu
        self.compute_type = compute_type if use_gpu else "int8"
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.model = None
        
        if WHISPER_AVAILABLE:
            self._initialize_model()
        else:
            logger.error("Impossible d'initialiser STT : faster-whisper non disponible")
    
    def _initialize_model(self):
        """Initialise le modèle Whisper."""
        try:
            # Forcer CPU car CUDA incomplet sur ce système
            device = "cpu"
            compute_type = "int8"
            logger.info(f"Chargement du modèle Whisper '{self.model_size}' sur {device}...")
            
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type
            )
            
            logger.info("Modèle Whisper chargé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle Whisper : {e}")
            # Fallback sur CPU si GPU échoue
            if self.use_gpu:
                logger.info("Tentative de chargement sur CPU...")
                try:
                    self.model = WhisperModel(
                        self.model_size,
                        device="cpu",
                        compute_type="int8"
                    )
                    logger.info("Modèle Whisper chargé sur CPU")
                except Exception as e2:
                    logger.error(f"Échec du chargement sur CPU : {e2}")
                    self.model = None
    
    def enregistrer_audio(
        self,
        device_index: Optional[int] = None
    ) -> Optional[np.ndarray]:
        """
        Enregistre l'audio depuis le micro jusqu'à détection de silence ou durée max.
        
        Args:
            device_index: Index du périphérique d'entrée (None = défaut)
            
        Returns:
            Tableau numpy contenant l'audio enregistré ou None si erreur
        """
        try:
            logger.info("Début de l'enregistrement audio...")
            
            # Buffer pour stocker l'audio
            audio_buffer = []
            silence_samples = int(self.silence_duration * self.sample_rate)
            max_samples = int(self.max_duration * self.sample_rate)
            silent_count = 0
            total_samples = 0
            
            # Callback pour capturer l'audio
            def audio_callback(indata, frames, time, status):
                nonlocal silent_count, total_samples
                
                if status:
                    logger.warning(f"Status audio : {status}")
                
                # Ajouter au buffer
                audio_buffer.append(indata.copy())
                total_samples += len(indata)
                
                # Vérifier le niveau audio (RMS)
                rms = np.sqrt(np.mean(indata**2))
                
                if rms < self.silence_threshold:
                    silent_count += len(indata)
                else:
                    silent_count = 0
            
            # Démarrer l'enregistrement
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=audio_callback,
                device=device_index
            ):
                # Attendre jusqu'à silence ou durée max
                while silent_count < silence_samples and total_samples < max_samples:
                    sd.sleep(100)  # Vérifier toutes les 100ms
            
            # Concaténer les buffers
            if audio_buffer:
                audio_data = np.concatenate(audio_buffer, axis=0)
                duration = len(audio_data) / self.sample_rate
                logger.info(f"Enregistrement terminé : {duration:.2f}s")
                return audio_data
            else:
                logger.warning("Aucun audio enregistré")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement audio : {e}")
            return None
    
    def transcrire_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Transcrit l'audio en texte.
        
        Args:
            audio_data: Données audio sous forme de tableau numpy
            
        Returns:
            Texte transcrit ou None si erreur
        """
        if not WHISPER_AVAILABLE or not self.model:
            logger.error("Modèle Whisper non disponible")
            return None
        
        if audio_data is None or len(audio_data) == 0:
            logger.warning("Données audio vides")
            return None
        
        try:
            # Sauvegarder temporairement en WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Convertir en format int16 pour WAV
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Écrire le fichier WAV
            with wave.open(tmp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16 bits
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            logger.info("Transcription en cours...")
            
            # Transcrire avec Whisper
            segments, info = self.model.transcribe(
                tmp_path,
                language=self.language,
                beam_size=5,
                vad_filter=False  # VAD désactivé pour éviter de filtrer la voix
            )
            
            # Extraire le texte
            texte = " ".join([segment.text for segment in segments]).strip()
            
            # Supprimer le fichier temporaire
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            if texte:
                logger.info(f"Transcription : '{texte}'")
                return texte
            else:
                logger.warning("Aucun texte transcrit")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la transcription : {e}")
            return None
    
    def ecouter_et_transcrire(
        self,
        device_index: Optional[int] = None
    ) -> Optional[str]:
        """
        Enregistre l'audio et le transcrit en une seule opération.
        
        Args:
            device_index: Index du périphérique d'entrée
            
        Returns:
            Texte transcrit ou None si erreur
        """
        audio_data = self.enregistrer_audio(device_index)
        if audio_data is not None:
            return self.transcrire_audio(audio_data)
        return None
    
    def cleanup(self):
        """Nettoie les ressources du moteur STT."""
        try:
            # faster-whisper gère automatiquement la mémoire
            self.model = None
            logger.info("Moteur STT nettoyé")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du moteur STT : {e}")
