# 📁 Structure du projet Jarvis Commander

## Arborescence complète

```
A:\Dev\Jarvis_Commander\
│
├─── 📄 main.py                          # 🚀 Point d'entrée principal
├─── 📄 requirements.txt                 # 📦 Dépendances Python
├─── 📄 .gitignore                       # 🚫 Fichiers ignorés par Git
│
├─── 📄 README.md                        # 📖 Documentation complète
├─── 📄 QUICKSTART.md                    # ⚡ Guide de démarrage rapide
├─── 📄 COMMANDES.md                     # 🗣️ Liste des commandes vocales
├─── 📄 EXEMPLE_FLUX.md                  # 🔄 Exemple de flux détaillé
├─── 📄 STRUCTURE_PROJET.md              # 📁 Ce fichier
│
├─── 📄 setup.bat                        # 🔧 Script d'installation automatique
├─── 📄 start_jarvis.bat                 # ▶️ Script de lancement rapide
├─── 📄 test_installation.py             # ✅ Script de test
│
├─── 📂 config/
│   ├─── config.yaml                     # ⚙️ Configuration principale
│   └─── config.yaml.example             # 📋 Exemple de configuration
│
├─── 📂 audio/
│   ├─── __init__.py                     # 📦 Module audio
│   ├─── wake_word.py                    # 🎯 Détection "jarvis" (Porcupine)
│   ├─── stt.py                          # 🎤 Speech-to-Text (Whisper)
│   └─── tts.py                          # 🔊 Text-to-Speech (pyttsx3)
│
├─── 📂 nlu/
│   ├─── __init__.py                     # 📦 Module NLU
│   └─── intent_parser.py                # 🧠 Analyse d'intentions
│
├─── 📂 actions/
│   ├─── __init__.py                     # 📦 Module actions
│   └─── system_control.py               # 🎮 Contrôle système Windows
│
├─── 📂 ui/
│   ├─── __init__.py                     # 📦 Module interface
│   └─── main_window.py                  # 🖥️ Interface Qt/PySide6
│
├─── 📂 logs/                            # 📝 Logs datés (créés auto)
│   └─── jarvis_YYYYMMDD.log             # Fichiers de logs quotidiens
│
└─── 📂 venv/                            # 🐍 Environnement virtuel (créé par setup)
     └─── ...                             # Dépendances installées
```

---

## 📊 Statistiques du projet

| Catégorie | Quantité |
|-----------|----------|
| **Fichiers Python** | 8 modules |
| **Fichiers Config** | 2 (yaml + example) |
| **Documentation** | 5 fichiers MD |
| **Scripts utilitaires** | 3 (bat + py) |
| **Lignes de code Python** | ~2500+ |
| **Lignes de commentaires** | ~800+ |

---

## 🎯 Fichiers essentiels

### À configurer avant le premier lancement

1. **config/config.yaml**
   - ⚠️ Remplacez `VOTRE_CLE_API_PICOVOICE_ICI` par votre vraie clé
   - Ajoutez/modifiez les chemins d'applications
   - Ajustez les paramètres audio si besoin

### À lire en priorité

1. **QUICKSTART.md** → Démarrage en 5 minutes
2. **README.md** → Documentation complète
3. **COMMANDES.md** → Liste des commandes vocales

### Scripts de lancement

1. **setup.bat** → Installation première fois
2. **start_jarvis.bat** → Lancement quotidien
3. **test_installation.py** → Vérification après installation

---

## 🔧 Modules principaux

### 1. `main.py` - Orchestrateur (400+ lignes)

**Responsabilités :**
- Initialisation de tous les composants
- Gestion du cycle de vie de l'application
- Coordination entre modules
- Gestion des événements

**Classes :**
- `JarvisController` : Contrôleur principal

**Fonctions clés :**
- `initialize_components()` : Initialise tous les modules
- `_process_command()` : Traite une commande vocale complète
- `_execute_action()` : Exécute l'action selon l'intention
- `start()` / `stop()` : Active/désactive Jarvis

---

### 2. `audio/wake_word.py` - Détection wake word (200+ lignes)

**Technologie :** Picovoice Porcupine

**Classe :**
- `WakeWordDetector`

**Méthodes principales :**
- `start_listening()` : Lance l'écoute en arrière-plan
- `_listen_loop()` : Boucle d'écoute (thread)
- `stop_listening()` : Arrête l'écoute
- `set_sensitivity()` : Modifie la sensibilité

**Performance :**
- Latence : ~100ms
- CPU : Très faible (<1%)
- Thread-safe : ✅

---

### 3. `audio/stt.py` - Speech-to-Text (300+ lignes)

**Technologie :** faster-whisper (OpenAI Whisper optimisé)

**Classe :**
- `STTEngine`

**Méthodes principales :**
- `enregistrer_audio()` : Capture audio avec détection de silence
- `transcrire_audio()` : Transcrit audio en texte
- `ecouter_et_transcrire()` : Combo des deux

**Performance :**
- Model small + GPU : 1-2s pour 5s audio
- Model tiny + CPU : 2-4s pour 5s audio
- Précision : 90-95% (français clair)

---

### 4. `audio/tts.py` - Text-to-Speech (200+ lignes)

**Technologie :** pyttsx3

**Classe :**
- `TTSEngine`

**Méthodes principales :**
- `parler()` : Synthèse vocale synchrone
- `parler_async()` : Synthèse vocale asynchrone
- `set_rate()` / `set_volume()` : Paramètres

**Performance :**
- Latence : Quasi-instantanée
- Thread-safe : ✅ (Lock)

---

### 5. `nlu/intent_parser.py` - NLU (300+ lignes)

**Technologie :** Règles regex (pas d'IA)

**Classe :**
- `IntentParser`

**Intentions supportées :**
- `open_app` : Ouvrir une application
- `close_app` : Fermer une application
- `web_search` : Recherche web
- `scroll_down` / `scroll_up` : Défilement
- `file_search` : Recherche de fichiers
- `dictation` : Dictée de texte
- `close_window` : Fermer fenêtre active

**Méthodes principales :**
- `parse()` : Analyse texte → intention
- `_extract_parameters()` : Extrait paramètres selon intention

---

### 6. `actions/system_control.py` - Actions système (400+ lignes)

**Technologies :** subprocess, psutil, pyautogui, webbrowser

**Classe :**
- `SystemController`

**Méthodes principales :**
- `open_app()` : Lance une application
- `close_app()` : Ferme une application (psutil)
- `scroll_down()` / `scroll_up()` : Contrôle scroll
- `type_text()` : Saisie clavier (dictée)
- `web_search()` : Ouvre recherche Google
- `search_files()` : Recherche fichiers sur disques
- `close_active_window()` : Alt+F4

**Caractéristiques :**
- Gestion des alias d'applications
- Recherche de fichiers asynchrone
- Mapping processus intelligent

---

### 7. `ui/main_window.py` - Interface graphique (500+ lignes)

**Technologie :** PySide6 (Qt6)

**Classe :**
- `JarvisMainWindow`

**Composants :**
- En-tête avec titre
- Indicateur d'état visuel (émojis + couleurs)
- Onglet Journal (logs HTML colorés)
- Onglet Paramètres (sensibilité, TTS, STT)
- Boutons de contrôle (Activer/Désactiver, Quitter)

**Thème :**
- Thème sombre moderne
- Palette de couleurs cohérente
- Police Segoe UI / Consolas

**Thread-safety :**
- Signaux Qt pour communications inter-threads
- `log_signal` et `status_signal`

---

## 🔄 Flux de données

```
[Micro] → [Wake Word] → [Callback] → [Controller]
                                         ↓
                                    [TTS: "Oui?"]
                                         ↓
                                    [STT: Record]
                                         ↓
                                    [STT: Transcribe]
                                         ↓
                                    [Intent Parser]
                                         ↓
                                    [System Controller]
                                         ↓
                                    [TTS: Confirm]
                                         ↓
                                      [UI Log]
```

---

## 📦 Dépendances clés

| Package | Version | Usage |
|---------|---------|-------|
| **PySide6** | ≥6.5.0 | Interface graphique |
| **pvporcupine** | ≥3.0.0 | Wake word detection |
| **faster-whisper** | ≥0.9.0 | Speech-to-Text |
| **pyttsx3** | ≥2.90 | Text-to-Speech |
| **sounddevice** | ≥0.4.6 | Capture audio |
| **psutil** | ≥5.9.0 | Gestion processus |
| **pyautogui** | ≥0.9.54 | Contrôle clavier/souris |
| **PyYAML** | ≥6.0 | Configuration |
| **numpy** | ≥1.24.0 | Traitement audio |

---

## 🎨 Personnalisation

### Ajouter une nouvelle commande vocale

1. **Ajouter le pattern** dans `nlu/intent_parser.py` :
   ```python
   'mon_intent': [
       r'(?:mon|ma)\s+(?:pattern|commande)\s+(.+)',
   ]
   ```

2. **Extraire les paramètres** dans `_extract_parameters()` :
   ```python
   elif intent == 'mon_intent':
       params['mon_param'] = match.group(1)
   ```

3. **Ajouter l'action** dans `actions/system_control.py` :
   ```python
   def mon_action(self, param):
       # Votre code
       return True
   ```

4. **Gérer l'exécution** dans `main.py` → `_execute_action()` :
   ```python
   elif intent == 'mon_intent':
       param = params.get('mon_param')
       success = self.system_controller.mon_action(param)
       response = "Action effectuée" if success else "Erreur"
   ```

---

## 🐛 Fichiers de logs

Les logs sont stockés dans `logs/` avec rotation quotidienne :

```
logs/
├── jarvis_20241118.log
├── jarvis_20241119.log
└── jarvis_20241120.log
```

**Format :**
```
2024-11-18 10:30:15,234 - __main__ - INFO - Jarvis Commander - Démarrage
2024-11-18 10:30:16,123 - audio.wake_word - INFO - Porcupine initialisé
2024-11-18 10:30:20,456 - audio.wake_word - INFO - 🎯 Wake word 'jarvis' détecté!
2024-11-18 10:30:22,789 - audio.stt - INFO - Transcription : Ouvre Chrome
```

---

## ✅ Checklist avant le premier lancement

- [ ] Python 3.10 ou 3.12 installé
- [ ] Environnement virtuel créé (`setup.bat`)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Clé API Picovoice dans `config/config.yaml`
- [ ] Chemins d'applications vérifiés dans `config.yaml`
- [ ] Micro configuré dans Windows (GXTrust ou autre)
- [ ] NVIDIA Broadcast activé (optionnel, si RTX)
- [ ] Test d'installation réussi (`python test_installation.py`)

---

## 🚀 Prochaines étapes après installation

1. **Tester l'installation** : `python test_installation.py`
2. **Lancer Jarvis** : `start_jarvis.bat`
3. **Activer** via l'interface
4. **Tester** : "Jarvis" → "Ouvre la calculatrice"
5. **Personnaliser** : Ajouter vos applications dans config.yaml
6. **Explorer** : Testez toutes les commandes de COMMANDES.md

---

**Architecture complète prête à l'emploi ! 🎉**
