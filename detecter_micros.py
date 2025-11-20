"""
Script pour détecter tous les micros disponibles.
Exécuter : python detecter_micros.py
"""

import sounddevice as sd

print("=" * 60)
print("   LISTE DES MICROS DISPONIBLES")
print("=" * 60)
print()

# Récupérer la liste des périphériques
devices = sd.query_devices()

print("Périphériques d'ENTRÉE (microphones) :")
print()

for idx, device in enumerate(devices):
    # Ne montrer que les périphériques d'entrée
    if device['max_input_channels'] > 0:
        # Marquer le périphérique par défaut
        is_default = " [DÉFAUT]" if idx == sd.default.device[0] else ""
        
        # Marquer NVIDIA Broadcast
        is_nvidia = " ⭐ [NVIDIA BROADCAST]" if "nvidia broadcast" in device['name'].lower() else ""
        
        print(f"Index {idx}: {device['name']}{is_default}{is_nvidia}")
        print(f"  - Canaux d'entrée : {device['max_input_channels']}")
        print(f"  - Fréquence d'échantillonnage : {device['default_samplerate']} Hz")
        print()

print("=" * 60)
print()
print("ACTION : Note l'index du micro 'NVIDIA Broadcast'")
print("Exemple : Si c'est 'Index 5', tu dois mettre '5' dans config.yaml")
print()
print("=" * 60)
