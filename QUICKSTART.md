# 🚀 Guide de démarrage rapide - Jarvis Commander

**Installation et lancement en 5 minutes !**

---

## ⚡ Installation Express

### 1️⃣ Obtenir une clé API Picovoice (2 min)

1. Allez sur **https://console.picovoice.ai/**
2. Créez un compte gratuit
3. Copiez votre **Access Key**

### 2️⃣ Installer Jarvis (3 min)

```bash
# Dans le dossier A:\Dev\Jarvis_Commander
setup.bat
```

Attendez la fin de l'installation (téléchargement des dépendances).

### 3️⃣ Configurer la clé API (30 sec)

1. Ouvrez `config\config.yaml`
2. Trouvez la ligne :
   ```yaml
   access_key: "VOTRE_CLE_API_PICOVOICE_ICI"
   ```
3. Remplacez par votre clé :
   ```yaml
   access_key: "VotreCléCopiéeDepuisPicovoice"
   ```
4. Sauvegardez le fichier

### 4️⃣ Lancer Jarvis (10 sec)

```bash
start_jarvis.bat
```

Ou manuellement :
```bash
venv\Scripts\activate
python main.py
```

---

## 🎤 Premier test

1. **Dans l'interface**, cliquez sur **"🎤 Activer Jarvis"**
2. L'indicateur passe à **"🔵 Écoute passive..."**
3. Dites clairement : **"Jarvis"**
4. Jarvis répond : **"Oui ?"**
5. Dites : **"Ouvre la calculatrice"**
6. ✅ La calculatrice Windows s'ouvre !

---

## 📝 Commandes de test rapides

### Sans configuration supplémentaire

```
✅ "Jarvis, ouvre la calculatrice"
✅ "Jarvis, ouvre le bloc-notes"
✅ "Jarvis, recherche Python tutorial"
✅ "Jarvis, scroll vers le bas"
✅ "Jarvis, ferme la calculatrice"
```

### Avec vos applications (nécessite config)

Ajoutez dans `config\config.yaml` :

```yaml
applications:
  spotify: "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe"
  steam: "C:\\Program Files (x86)\\Steam\\steam.exe"
```

Puis :
```
"Jarvis, ouvre Spotify"
"Jarvis, lance Steam"
```

---

## 🔧 Problèmes courants

### ❌ "Clé API invalide"
→ Vérifiez que vous avez bien collé la clé dans `config.yaml`

### ❌ Wake word non détecté
→ Augmentez la sensibilité dans l'interface (Paramètres → 0.8 ou 0.9)

### ❌ "Application non trouvée"
→ Vérifiez le chemin dans `config.yaml` (clic droit → Propriétés sur le raccourci)

### ❌ Whisper trop lent
→ Changez le modèle dans Paramètres : `small` → `tiny`

---

## 📚 Aller plus loin

- **Documentation complète** : Consultez `README.md`
- **Personnalisation** : Ajoutez vos applications dans `config\config.yaml`
- **Logs** : Consultez `logs\jarvis_YYYYMMDD.log` en cas de problème

---

## 💡 Astuces

### Filtrage audio (NVIDIA RTX)
Si vous avez une carte NVIDIA RTX :
1. Installez **NVIDIA Broadcast**
2. Activez la suppression de bruit
3. Sélectionnez le micro NVIDIA Broadcast dans Windows

### Lancement automatique au démarrage
1. Créez un raccourci de `start_jarvis.bat`
2. Appuyez sur `Win + R`, tapez `shell:startup`
3. Collez le raccourci dans ce dossier

### Mode silencieux
Réduisez le volume TTS dans l'interface si Jarvis parle trop fort.

---

**C'est tout ! Profitez de Jarvis Commander ! 🤖✨**
