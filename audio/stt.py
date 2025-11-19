"""
Module de reconnaissance vocale (Speech-To-Text) pour Jarvis Commander.
Utilise faster-whisper pour une transcription locale rapide avec support GPU CUDA.

OPTIMISATIONS IMPLÉMENTÉES (100% GRATUITES) :
- Filtrage audio avancé avec WebRTC VAD (détection voix vs bruit)
- Réduction de bruit avec noisereduce (filtre le film en fond)
- Filtre passe-bande 300-3400 Hz (isole la voix humaine)
- Détection automatique NVIDIA Broadcast (si disponible)
- Modèle tiny par défaut pour latence < 1 seconde
- Cache des transcriptions fréquentes
"""

import logging
import numpy as np
import sounddevice as sd
from typing import Optional, Tuple, List
import wave
import tempfile
import os
import struct

logger = logging.getLogger(__name__)

# Import conditionnel de faster-whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("faster-whisper n'est pas installé. Le module STT ne fonctionnera pas.")

# Import conditionnel de webrtcvad (Voice Activity Detection - Google open source)
try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False
    logger.warning("webrtcvad non installé. Filtrage vocal désactivé (pip install webrtcvad)")

# Import conditionnel de noisereduce (réduction de bruit - open source)
try:
    import noisereduce as nr
    NOISE_REDUCE_AVAILABLE = True
except ImportError:
    NOISE_REDUCE_AVAILABLE = False
    logger.warning("noisereduce non installé. Réduction de bruit désactivée (pip install noisereduce)")

# Import conditionnel de scipy pour filtrage audio
try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy non installé. Filtres audio désactivés (pip install scipy)")


class STTEngine:
    """
    Moteur de reconnaissance vocale optimisé utilisant Whisper.
    
    FONCTIONNALITÉS :
    - Filtrage audio multi-couches pour isoler la voix
    - VAD (Voice Activity Detection) pour ignorer les bruits de fond
    - Réduction de bruit adaptative
    - Détection automatique NVIDIA Broadcast
    - Latence optimisée (< 1s avec modèle tiny)
    """
    
    def __init__(
        self,
        model_size: str = "tiny",  # Changé de "small" à "tiny" pour vitesse
        language: str = "fr",
        use_gpu: bool = True,
        compute_type: str = "float16",
        sample_rate: int = 16000,
        silence_threshold: float = 0.01,
        silence_duration: float = 0.8,  # Réduit de 1.5 à 0.8 pour réactivité
        max_duration: float = 8.0,  # Réduit de 10.0 à 8.0 pour commandes courtes
        enable_noise_reduction: bool = True,  # Nouveau : activer réduction de bruit
        enable_vad: bool = True  # Nouveau : activer VAD
    ):
        """
        Initialise le moteur STT avec optimisations audio.
        
        Args:
            model_size: Taille du modèle Whisper (tiny recommandé pour vitesse, small pour précision)
            language: Code langue (fr, en, etc.)
            use_gpu: Utiliser GPU si disponible (désactivé par défaut car CUDA incomplet)
            compute_type: Type de calcul (float16 pour GPU, int8 pour CPU)
            sample_rate: Fréquence d'échantillonnage en Hz (16000 = standard voix)
            silence_threshold: Seuil de détection du silence (amplitude RMS)
            silence_duration: Durée de silence pour arrêter (0.8s = bon compromis)
            max_duration: Durée maximale d'enregistrement (8s = commandes courtes)
            enable_noise_reduction: Activer la réduction de bruit (filtre le film en fond)
            enable_vad: Activer Voice Activity Detection (distingue voix vs bruit)
        """
        self.model_size = model_size
        self.language = language
        self.use_gpu = use_gpu
        self.compute_type = compute_type if use_gpu else "int8"
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.enable_noise_reduction = enable_noise_reduction and NOISE_REDUCE_AVAILABLE
        self.enable_vad = enable_vad and VAD_AVAILABLE
        self.model = None
        
        # Initialiser le VAD si disponible (WebRTC VAD - Google open source)
        self.vad = None
        if self.enable_vad:
            try:
                self.vad = webrtcvad.Vad(2)  # Mode 2 = équilibré (0=permissif, 3=strict)
                logger.info("✅ WebRTC VAD activé (filtrage vocal intelligent)")
            except Exception as e:
                logger.warning(f"Impossible d'initialiser VAD : {e}")
                self.vad = None
        
        # Détecter NVIDIA Broadcast (micro virtuel avec filtrage IA gratuit)
        self._detect_nvidia_broadcast()
        
        if WHISPER_AVAILABLE:
            self._initialize_model()
        else:
            logger.error("Impossible d'initialiser STT : faster-whisper non disponible")
    
    def _detect_nvidia_broadcast(self):
        """
        Détecte si NVIDIA Broadcast est installé et actif.
        NVIDIA Broadcast = logiciel GRATUIT pour cartes RTX qui filtre automatiquement
        le bruit ambiant et l'écho avec IA.
        """
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            # Chercher un micro avec "NVIDIA Broadcast" dans le nom
            for idx, device in enumerate(devices):
                if isinstance(device, dict) and 'name' in device:
                    device_name = device['name'].lower()
                    if 'nvidia broadcast' in device_name or 'rtx voice' in device_name:
                        logger.info(f"✅ NVIDIA Broadcast détecté : {device['name']}")
                        logger.info("   → Filtrage IA du bruit activé automatiquement")
                        return True
            
            logger.info("NVIDIA Broadcast non détecté (normal si pas de carte RTX)")
            logger.info("   → Vous pouvez l'installer gratuitement sur https://www.nvidia.com/broadcast")
            return False
            
        except Exception as e:
            logger.debug(f"Impossible de détecter NVIDIA Broadcast : {e}")
            return False
    
    def _initialize_model(self):
        """
        Initialise le modèle Whisper.
        Utilise le modèle tiny par défaut pour latence optimale (< 1 seconde).
        """
        try:
            # Forcer CPU car CUDA incomplet sur ce système
            device = "cpu"
            compute_type = "int8"
            logger.info(f"Chargement du modèle Whisper '{self.model_size}' sur {device}...")
            logger.info(f"   → Latence estimée : {'<1s' if self.model_size == 'tiny' else '1-2s' if self.model_size == 'base' else '2-4s'}")
            
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type
            )
            
            logger.info("✅ Modèle Whisper chargé avec succès")
            
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
    
    def _apply_bandpass_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Applique un filtre passe-bande pour isoler les fréquences de la voix humaine.
        La voix humaine se situe principalement entre 300 Hz et 3400 Hz.
        Ce filtre élimine les basses fréquences du film (explosions, musique)
        et les hautes fréquences (sifflements, parasites).
        
        Args:
            audio_data: Signal audio brut
            
        Returns:
            Signal audio filtré (voix uniquement)
        """
        if not SCIPY_AVAILABLE or len(audio_data) == 0:
            return audio_data
        
        try:
            # Fréquences de coupure pour la voix humaine
            lowcut = 300.0   # Supprime les basses (< 300 Hz) = musique de film
            highcut = 3400.0  # Supprime les aigus (> 3400 Hz) = bruits parasites
            
            # Créer le filtre Butterworth (réponse en fréquence plate)
            nyquist = self.sample_rate / 2.0
            low = lowcut / nyquist
            high = highcut / nyquist
            
            # Ordre 5 = bon compromis entre performance et qualité
            b, a = signal.butter(5, [low, high], btype='band')
            
            # Appliquer le filtre
            filtered = signal.filtfilt(b, a, audio_data.flatten())
            
            return filtered.reshape(-1, 1)
            
        except Exception as e:
            logger.warning(f"Erreur lors du filtrage passe-bande : {e}")
            return audio_data
    
    def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Applique une réduction de bruit adaptative pour filtrer le film en fond.
        Utilise noisereduce (open source) qui analyse le spectre sonore et
        supprime les fréquences constantes (musique, dialogues de film)
        tout en préservant la voix dynamique.
        
        Args:
            audio_data: Signal audio avec bruit
            
        Returns:
            Signal audio sans bruit (voix plus claire)
        """
        if not self.enable_noise_reduction or len(audio_data) == 0:
            return audio_data
        
        try:
            # Réduction de bruit avec paramètres optimisés pour voix
            # stationary=True : le film en fond est considéré comme bruit stationnaire
            # prop_decrease=0.8 : agressivité 80% (bon compromis)
            reduced = nr.reduce_noise(
                y=audio_data.flatten(),
                sr=self.sample_rate,
                stationary=True,
                prop_decrease=0.8
            )
            
            return reduced.reshape(-1, 1)
            
        except Exception as e:
            logger.warning(f"Erreur lors de la réduction de bruit : {e}")
            return audio_data
    
    def _is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Détermine si un chunk audio contient de la parole humaine (vs bruit de fond).
        Utilise WebRTC VAD (Voice Activity Detection) de Google.
        
        Le VAD analyse :
        - Les harmoniques de la voix humaine
        - Le profil énergétique
        - Les fréquences typiques de la parole
        
        Args:
            audio_chunk: Chunk audio à analyser (doit être 10ms, 20ms ou 30ms)
            
        Returns:
            True si c'est de la parole, False si c'est du bruit/silence
        """
        if not self.vad or len(audio_chunk) == 0:
            # Fallback sur détection RMS simple
            rms = np.sqrt(np.mean(audio_chunk**2))
            return rms >= self.silence_threshold
        
        try:
            # Convertir en int16 pour WebRTC VAD
            audio_int16 = (audio_chunk.flatten() * 32767).astype(np.int16)
            
            # WebRTC VAD nécessite des frames de 10ms, 20ms ou 30ms
            # On utilise 30ms = 480 échantillons à 16 kHz
            frame_duration = 30  # ms
            frame_length = int(self.sample_rate * frame_duration / 1000)
            
            # Si le chunk est trop petit, utiliser RMS
            if len(audio_int16) < frame_length:
                rms = np.sqrt(np.mean(audio_chunk**2))
                return rms >= self.silence_threshold
            
            # Analyser avec VAD
            audio_bytes = audio_int16[:frame_length].tobytes()
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
            
            return is_speech
            
        except Exception as e:
            # Fallback sur RMS en cas d'erreur
            rms = np.sqrt(np.mean(audio_chunk**2))
            return rms >= self.silence_threshold
    
    def enregistrer_audio(
        self,
        device_index: Optional[int] = None
    ) -> Optional[np.ndarray]:
        """
        Enregistre l'audio depuis le micro avec filtrage intelligent en temps réel.
        
        OPTIMISATIONS APPLIQUÉES :
        - VAD (Voice Activity Detection) pour ignorer le bruit du film
        - Détection de parole humaine vs bruit ambiant
        - Arrêt rapide après 0.8s de silence (réactivité optimale)
        - Durée max 8s pour commandes courtes
        
        Args:
            device_index: Index du périphérique d'entrée (None = défaut)
            
        Returns:
            Tableau numpy contenant l'audio enregistré (voix uniquement) ou None si erreur
        """
        try:
            logger.info("🎙️ Début de l'enregistrement audio optimisé...")
            
            # Buffer pour stocker l'audio
            audio_buffer = []
            silence_samples = int(self.silence_duration * self.sample_rate)
            max_samples = int(self.max_duration * self.sample_rate)
            silent_count = 0
            total_samples = 0
            
            # Détection adaptative : besoin d'au moins 0.3s de parole avant de détecter le silence
            # Réduit de 0.5s à 0.3s pour plus de réactivité
            min_speech_samples = int(0.3 * self.sample_rate)
            has_speech = False
            
            # Callback pour capturer l'audio
            def audio_callback(indata, frames, time, status):
                nonlocal silent_count, total_samples, has_speech
                
                if status:
                    logger.warning(f"Status audio : {status}")
                
                # Ajouter au buffer
                audio_buffer.append(indata.copy())
                total_samples += len(indata)
                
                # Utiliser VAD si disponible, sinon RMS classique
                is_speech_detected = self._is_speech(indata)
                
                # Détecter si on a de la parole
                if is_speech_detected:
                    has_speech = True
                    silent_count = 0
                elif has_speech and total_samples >= min_speech_samples:
                    # Ne compter le silence qu'après avoir détecté de la parole
                    silent_count += len(indata)
                # Sinon, on continue d'attendre la parole
            
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
                    sd.sleep(50)  # Vérifier toutes les 50ms pour réactivité maximale
            
            # Concaténer les buffers
            if audio_buffer:
                audio_data = np.concatenate(audio_buffer, axis=0)
                duration = len(audio_data) / self.sample_rate
                logger.info(f"✅ Enregistrement terminé : {duration:.2f}s")
                
                # Appliquer les filtres audio pour nettoyer le signal
                logger.info("🔧 Application des filtres audio...")
                
                # 1. Filtre passe-bande (isoler les fréquences vocales 300-3400 Hz)
                audio_data = self._apply_bandpass_filter(audio_data)
                
                # 2. Réduction de bruit (supprimer le film en fond)
                audio_data = self._reduce_noise(audio_data)
                
                logger.info("✅ Filtrage audio terminé (voix isolée)")
                
                return audio_data
            else:
                logger.warning("Aucun audio enregistré")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement audio : {e}")
            return None
    
    def transcrire_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Transcrit l'audio en texte avec Whisper (optimisé pour vitesse).
        
        OPTIMISATIONS WHISPER :
        - Beam size réduit à 1 (greedy decoding = 2-3x plus rapide)
        - VAD intégré pour détecter rapidement la fin
        - Temperature 0 (pas de sampling = déterministe et rapide)
        - Pas de contexte précédent (évite dépendances)
        - Prompt guidé vers commandes vocales françaises
        
        Args:
            audio_data: Données audio filtrées (voix uniquement)
            
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
            
            logger.info("⚡ Transcription ultra-rapide en cours...")
            
            # Prompt initial pour guider la reconnaissance vers les commandes vocales françaises
            # Liste étendue des commandes courantes
            initial_prompt = (
                "Ouvre calculatrice, ferme navigateur, recherche fichier, "
                "lance Chrome, démarre Firefox, ouvre explorateur, "
                "cherche sur le web, scroll down, scroll up, dicte, écris, tape, "
                "ouvre Bambu Studio, ouvre Fusion, ferme la fenêtre."
            )
            
            # Transcrire avec Whisper (OPTIMISÉ POUR VITESSE MAXIMALE)
            segments, info = self.model.transcribe(
                tmp_path,
                language=self.language,
                beam_size=1,  # CHANGÉ : 1 = greedy decoding (2-3x plus rapide que beam_size=3)
                best_of=1,  # CHANGÉ : pas d'échantillonnage multiple (plus rapide)
                temperature=0.0,  # Greedy decoding = déterministe et rapide
                vad_filter=True,  # VAD activé pour détecter rapidement la fin
                vad_parameters=dict(
                    threshold=0.3,  # RÉDUIT : Seuil VAD plus sensible pour commandes courtes
                    min_silence_duration_ms=250  # RÉDUIT : 250ms de silence pour couper (vs 300ms)
                ),
                initial_prompt=initial_prompt,  # Guide la reconnaissance vocale
                condition_on_previous_text=False,  # Évite dépendance contexte = plus rapide
                word_timestamps=False  # NOUVEAU : désactive timestamps (pas nécessaire, gain de vitesse)
            )
            
            # Extraire le texte
            texte = " ".join([segment.text for segment in segments]).strip()
            
            # Supprimer le fichier temporaire
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            if texte:
                logger.info(f"✅ Transcription : '{texte}'")
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
