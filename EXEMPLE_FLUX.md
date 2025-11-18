# 🔄 Exemple de flux complet - Jarvis Commander

Ce document détaille le chemin complet d'une commande vocale à travers tous les modules de Jarvis.

---

## 📝 Commande exemple : "Ouvre Chrome"

### Étape 0 : État initial
```
┌─────────────────────────────────────┐
│  Jarvis est actif et en veille      │
│  Status UI : 🔵 Écoute passive...   │
└─────────────────────────────────────┘
```

---

### Étape 1 : Détection du Wake Word

**Module** : `audio/wake_word.py` (Porcupine)

```
🎤 Utilisateur prononce : "Jarvis"
         ↓
[WakeWordDetector]
  • Capture audio en continu (16 kHz)
  • Analyse frame par frame avec Porcupine
  • Détection : keyword_index >= 0
         ↓
✅ Wake word détecté !
         ↓
Callback → _on_wake_word_detected()
```

**Log UI** :
```
[10:30:15] [INFO] 🎯 Wake word détecté!
```

**Status UI** : 🔴 Enregistrement en cours...

---

### Étape 2 : Synthèse vocale de confirmation

**Module** : `audio/tts.py` (pyttsx3)

```
[JarvisController._process_command()]
         ↓
tts_engine.parler("Oui ?")
         ↓
[TTSEngine.parler()]
  • Lock thread pour synchronisation
  • engine.say("Oui ?")
  • engine.runAndWait()
         ↓
🔊 Sortie audio : "Oui ?"
```

**Log UI** :
```
[10:30:15] [INFO] TTS : Oui ?
```

---

### Étape 3 : Enregistrement audio

**Module** : `audio/stt.py` (sounddevice)

```
[STTEngine.enregistrer_audio()]
         ↓
🎤 Ouverture du flux audio
  • Sample rate : 16000 Hz
  • Channels : 1 (mono)
  • Device : GXTrust (ou défaut)
         ↓
🎤 Utilisateur parle : "Ouvre Chrome"
         ↓
📊 Capture audio en temps réel
  • Buffer audio en mémoire
  • Calcul RMS pour détecter le silence
  • Condition d'arrêt :
    - Silence > 1.5s OU
    - Durée max > 10s
         ↓
⏹️ Arrêt de l'enregistrement
  • Durée totale : ~2.3s
  • Audio data : numpy array
```

**Log UI** :
```
[10:30:16] [INFO] Enregistrement en cours...
[10:30:18] [INFO] Enregistrement terminé : 2.30s
```

**Status UI** : 🟡 Traitement de la commande...

---

### Étape 4 : Transcription (Speech-to-Text)

**Module** : `audio/stt.py` (Whisper)

```
[STTEngine.transcrire_audio(audio_data)]
         ↓
💾 Sauvegarde temporaire en WAV
  • Conversion float32 → int16
  • Fichier : C:\Temp\tmp_xyz.wav
         ↓
🧠 Whisper - Transcription
  • Modèle : small (~500 MB)
  • Langue : fr
  • Device : CUDA (GPU RTX 3060)
  • VAD Filter : activé
         ↓
⚡ Traitement GPU (~1.2s)
  • Segments détectés : 1
  • Texte brut : "Ouvre Chrome"
         ↓
🧹 Nettoyage
  • Strip espaces
  • Suppression fichier temporaire
         ↓
✅ Transcription : "Ouvre Chrome"
```

**Log UI** :
```
[10:30:18] [INFO] Transcription en cours...
[10:30:19] [INFO] Transcription : Ouvre Chrome
```

---

### Étape 5 : Analyse d'intention (NLU)

**Module** : `nlu/intent_parser.py`

```
[IntentParser.parse("Ouvre Chrome")]
         ↓
🔤 Normalisation
  • Texte → lowercase : "ouvre chrome"
  • Strip ponctuation finale
         ↓
🔍 Test des patterns (regex)
  • Pattern 'open_app' : ✅ Match!
    Regex : r'(?:ouvre|lance|démarre)\s+(.+)'
    Group 1 : "chrome"
         ↓
📦 Extraction des paramètres
  • intent : "open_app"
  • parameters.app_name : "chrome"
         ↓
🔄 Résolution des alias
  • Vérif dans app_aliases : "chrome" → "chrome" (pas d'alias)
         ↓
✅ Intention reconnue
{
  "intent": "open_app",
  "parameters": {
    "app_name": "chrome"
  }
}
```

**Log UI** :
```
[10:30:19] [INFO] Analyse de l'intention : 'ouvre chrome'
[10:30:19] [INFO] Intention détectée : {'intent': 'open_app', 'parameters': {'app_name': 'chrome'}}
```

**Status UI** : 🟢 Exécution...

---

### Étape 6 : Exécution de l'action

**Module** : `actions/system_control.py`

```
[SystemController.open_app("chrome")]
         ↓
📋 Vérification configuration
  • Lookup dans self.app_paths["chrome"]
  • Chemin trouvé : "C:\Program Files\Google\Chrome\Application\chrome.exe"
         ↓
🔧 Résolution des variables
  • os.path.expandvars() appliqué
  • Pas de %USERNAME% dans ce cas
         ↓
🚀 Lancement processus
  • subprocess.Popen([chemin_chrome])
  • Shell : False
  • Détachement du processus
         ↓
✅ Chrome démarré (PID: 12345)
```

**Log UI** :
```
[10:30:19] [INFO] Ouverture de 'chrome' : C:\Program Files\Google\Chrome\Application\chrome.exe
[10:30:19] [INFO] Application 'chrome' lancée avec succès
```

---

### Étape 7 : Confirmation vocale

**Module** : `audio/tts.py`

```
[tts_engine.parler("J'ouvre Chrome")]
         ↓
🔊 Synthèse vocale
  • Rate : 180 mpm
  • Volume : 0.9
  • Voix : Française (système)
         ↓
🔊 Sortie audio : "J'ouvre Chrome"
```

**Log UI** :
```
[10:30:19] [INFO] TTS : J'ouvre Chrome
[10:30:19] [INFO] Action : J'ouvre Chrome
```

---

### Étape 8 : Retour à l'état de veille

```
[JarvisController._process_command()] - Fin
         ↓
self.is_processing = False
         ↓
_emit_status('listening')
```

**Status UI** : 🔵 Écoute passive...

**Log UI** :
```
[10:30:20] [INFO] ✅ Commande exécutée avec succès
```

---

## 🖥️ Vue d'ensemble visuelle

```
┌────────────────────────────────────────────────────────────────┐
│                    FLUX COMPLET - "Ouvre Chrome"                │
└────────────────────────────────────────────────────────────────┘

 🎤 Audio brut
  │
  ├─► [Wake Word Detector]  ───► "Jarvis" détecté ─┐
  │                                                  │
  ↓                                                  ↓
🔊 TTS: "Oui ?"                            🎯 Callback wake_word
  │
  ↓
 🎤 Enregistrement audio (1.5s - 10s max)
  │
  ├─► [STT Engine - Whisper] ───► "Ouvre Chrome"
  │
  ↓
 📝 Texte transcrit
  │
  ├─► [Intent Parser] ───► {intent: "open_app", params: {app_name: "chrome"}}
  │
  ↓
 🧠 Intention structurée
  │
  ├─► [System Controller] ───► subprocess.Popen(chrome.exe)
  │
  ↓
 ✅ Chrome lancé
  │
  ├─► [TTS Engine] ───► 🔊 "J'ouvre Chrome"
  │
  ↓
 🔄 Retour à l'écoute passive
```

---

## ⏱️ Chronométrage typique

| Étape | Durée | Bloquant UI |
|-------|-------|-------------|
| Wake word detection | ~100ms | ❌ Non (thread) |
| TTS "Oui ?" | ~300ms | ⚠️ Semi (async) |
| Enregistrement audio | 2-5s | ✅ Oui |
| Transcription Whisper | 1-3s | ✅ Oui |
| Parsing intention | <10ms | ✅ Oui |
| Exécution action | 100-500ms | ✅ Oui |
| TTS confirmation | 500ms | ⚠️ Semi (async) |
| **TOTAL** | **~4-9s** | |

**Note** : L'interface reste réactive grâce au threading (traitement dans un thread séparé).

---

## 🔀 Variantes du flux

### Commande "Ferme Chrome"

Différence à l'étape 6 :
```
[SystemController.close_app("chrome")]
  • Mapping nom → processus : "chrome" → ["chrome.exe"]
  • Énumération psutil.process_iter()
  • Terminaison propre : proc.terminate()
  • Timeout 3s → proc.kill() si nécessaire
```

### Commande "Recherche Python tutoriel"

Différence à l'étape 6 :
```
[SystemController.web_search("Python tutoriel")]
  • Encodage URL : urllib.parse.quote_plus()
  • Construction URL Google
  • webbrowser.open(url)
```

### Commande "Dicte Hello World"

Différence à l'étape 6 :
```
[SystemController.type_text("Hello World")]
  • Pause 0.5s (laisser utilisateur cliquer fenêtre)
  • pyautogui.write("Hello World", interval=0.05)
  • Simulation frappe clavier dans fenêtre active
```

---

## 🛡️ Gestion d'erreurs

À chaque étape, des try/except capturent les erreurs :

```python
try:
    # Exécution de l'étape
    result = execute_step()
except Exception as e:
    logger.error(f"Erreur : {e}")
    self._emit_log(f"Erreur : {e}", "ERROR")
    self._emit_status('error')
    tts_engine.parler("Désolé, une erreur s'est produite.")
```

Exemples d'erreurs gérées :
- 🎤 Micro déconnecté → Log + TTS "Problème de micro"
- 🔊 Haut-parleurs muets → Log (pas de crash)
- 📁 App non trouvée → Log + TTS "Je ne trouve pas cette application"
- 🌐 Pas d'Internet (recherche web) → Ouvre navigateur quand même
- ⌨️ Fenêtre fermée (dictée) → Log l'erreur

---

**Ce flux garantit une expérience utilisateur fluide et robuste ! 🚀**
