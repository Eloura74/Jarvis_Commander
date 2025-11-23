import sounddevice as sd
import numpy as np
import time

def list_devices():
    print("\n=== Périphériques Audio ===")
    print(sd.query_devices())
    print("===========================\n")

def test_recording():
    print("\n=== Test des micros ===")
    devices = sd.query_devices()
    
    for i, dev in enumerate(devices):
        # On ne teste que les entrées (max_input_channels > 0)
        if dev['max_input_channels'] > 0:
            print(f"\nTest du périphérique #{i}: {dev['name']}")
            try:
                # Test court de 2 secondes
                duration = 2
                max_rms = 0
                
                def callback(indata, frames, time, status):
                    nonlocal max_rms
                    rms = np.sqrt(np.mean(indata**2))
                    if rms > max_rms:
                        max_rms = rms
                    print(f"  Niveau: {rms:.4f}", end='\r')

                with sd.InputStream(device=i, channels=1, samplerate=16000, callback=callback):
                    time.sleep(duration)
                
                print(f"\n  -> Pic Max: {max_rms:.4f}")
                if max_rms > 0.01:
                    print("  ✅ SIGNAL DÉTECTÉ !")
                else:
                    print("  ❌ SILENCE")
                    
            except Exception as e:
                print(f"  ⚠️ Erreur: {e}")

if __name__ == "__main__":
    # list_devices() # On le fait déjà dans la boucle
    test_recording()
