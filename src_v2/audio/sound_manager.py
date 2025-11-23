"""
Gestionnaire de sons pour Jarvis V3.0.
Gère les effets sonores (bips, swooshes) pour le feedback utilisateur.
"""

import os
import logging
import threading
import winsound  # Standard sur Windows, pas besoin de dépendance externe lourde
from pathlib import Path

logger = logging.getLogger(__name__)

class SoundManager:
    """Gère la lecture des effets sonores."""
    
    def __init__(self, sound_dir: str = "assets/sounds"):
        self.sound_dir = Path(os.path.dirname(__file__)).parent.parent / sound_dir
        self.sounds = {
            'startup': 'startup.wav',
            'listening': 'listening.wav',
            'processing': 'processing.wav',
            'success': 'success.wav',
            'error': 'error.wav'
        }
        self._ensure_assets_dir()
        logger.info("SoundManager initialisé")

    def _ensure_assets_dir(self):
        """Vérifie que le dossier existe."""
        if not self.sound_dir.exists():
            try:
                self.sound_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Impossible de créer le dossier sons: {e}")

    def play(self, sound_name: str, async_mode: bool = True):
        """
        Joue un son.
        
        Args:
            sound_name: Nom de la clé dans self.sounds (ex: 'listening')
            async_mode: Si True, joue dans un thread séparé
        """
        if sound_name not in self.sounds:
            logger.warning(f"Son inconnu: {sound_name}")
            return

        filename = self.sounds[sound_name]
        filepath = self.sound_dir / filename

        if not filepath.exists():
            # Fallback sur un bip système si le fichier n'existe pas
            self._play_system_beep(sound_name)
            return

        if async_mode:
            threading.Thread(target=self._play_file, args=(str(filepath),), daemon=True).start()
        else:
            self._play_file(str(filepath))

    def _play_file(self, filepath: str):
        """Joue le fichier WAV."""
        try:
            # SND_FILENAME = fichier, SND_ASYNC = ne bloque pas le thread appelant (si utilisé directement)
            # Mais on est déjà souvent dans un thread dédié ici si async_mode=True
            winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            logger.error(f"Erreur lecture son {filepath}: {e}")

    def _play_system_beep(self, sound_type: str):
        """Joue un bip système par défaut selon le type."""
        try:
            if sound_type == 'listening':
                winsound.Beep(800, 200) # Aigu court
            elif sound_type == 'processing':
                winsound.Beep(600, 100)
            elif sound_type == 'success':
                winsound.Beep(1000, 300)
            elif sound_type == 'error':
                winsound.Beep(200, 400) # Grave long
            elif sound_type == 'startup':
                winsound.Beep(500, 300)
                winsound.Beep(700, 300)
                winsound.Beep(900, 500)
        except Exception:
            pass
