# Guide d'Amélioration de la Reconnaissance Vocale

## 🎯 Problèmes Courants et Solutions

### 1. Commande non reconnue ("unknown intent")

#### Symptômes
```
Transcription : Est-ce qu'il vous recalculate ?
Intention : unknown
```

#### Causes possibles
- Mauvaise transcription par Whisper
- Application non configurée
- Pattern d'intention non défini

#### Solutions

##### A. Améliorer la transcription
Le système inclut maintenant un **initial_prompt** pour guider Whisper vers les commandes françaises courantes. Vous pouvez l'adapter dans `audio/stt.py` :

```python
initial_prompt = (
    "Ouvre calculatrice, ferme navigateur, recherche fichier, "
    "lance Chrome, démarre Firefox, ouvre explorateur, "
    "cherche sur le web, scroll down, scroll up."
)
```

**Conseil :** Ajoutez vos commandes les plus fréquentes dans ce prompt.

##### B. Ajouter des corrections de transcription
Dans `nlu/intent_parser.py`, le dictionnaire `transcription_corrections` corrige automatiquement les erreurs courantes :

```python
self.transcription_corrections = {
    'recalculate': 'calculatrice',
    'recalculatrice': 'calculatrice',
    'calculette': 'calculatrice',
    # Ajoutez vos propres corrections ici
}
```

##### C. Configurer les applications et alias
Dans `config/config.yaml` :

```yaml
# Méthode 1 : Applications directes (RECOMMANDÉ)
applications:
  calculator: "calc.exe"
  calculatrice: "calc.exe"      # Variation française
  calculette: "calc.exe"         # Variation familière
  calcul: "calc.exe"             # Version courte

# Méthode 2 : Alias (optionnel si vous avez déjà la méthode 1)
app_aliases:
  calculatrice: calculator
  calculette: calculator
  recalculate: calculator  # Erreur de transcription courante
```

**💡 Conseil :** La méthode 1 (applications directes) est plus simple et plus robuste.

---

### 2. Transcription incorrecte

#### Exemples courants
| Vous dites | Whisper entend | Solution |
|------------|----------------|----------|
| "calculatrice" | "recalculate" | Ajouté dans corrections automatiques ✓ |
| "navigateur" | "navigator" | Ajoutez alias dans config.yaml |
| "explorateur" | "explorer" | Ajoutez alias dans config.yaml |

#### Améliorer la qualité audio
```yaml
# Dans config/config.yaml
audio:
  # Réduire le seuil de silence pour mieux capter la voix
  silence_threshold: -40
  
  # Augmenter la durée d'enregistrement
  max_record_duration: 12
  
  # Ajuster la durée de silence avant coupure
  silence_duration: 1.5
```

---

### 3. Utiliser un meilleur modèle Whisper

Pour une meilleure précision, utilisez un modèle plus grand :

```yaml
# Dans config/config.yaml
stt:
  model: "medium"  # Options: tiny, base, small, medium, large
  language: "fr"
  use_gpu: false
  compute_type: "int8"
```

**⚠️ Attention :** 
- `medium` et `large` sont plus lents mais plus précis
- `small` est le meilleur compromis vitesse/précision

---

## 🔧 Fuzzy Matching Automatique

Le système utilise maintenant le **fuzzy matching** pour corriger automatiquement les petites erreurs :

- "calculatice" → "calculatrice" ✓
- "crom" → "chrome" ✓
- "explorate" → "explorateur" ✓

Seuil de similarité : **60%** (ajustable dans `intent_parser.py`)

---

## 📝 Ajouter une Nouvelle Commande

### Exemple : Ajouter "Notepad++"

1. **Dans config/config.yaml** :
```yaml
applications:
  notepad++: "C:\\Program Files\\Notepad++\\notepad++.exe"
  notepadplusplus: "C:\\Program Files\\Notepad++\\notepad++.exe"
  éditeur: "C:\\Program Files\\Notepad++\\notepad++.exe"

app_aliases:
  editeur: notepad++  # Sans accent pour la transcription
  note pad: notepad++
```

2. **Tester** :
```
Vous : "Jarvis, ouvre éditeur"
Jarvis : [ouvre Notepad++] ✓
```

---

## 🐛 Déboguer les Problèmes

### Activer les logs détaillés
```yaml
# Dans config/config.yaml
logging:
  level: "DEBUG"  # Au lieu de "INFO"
```

### Vérifier les logs
Les logs sont dans `logs/jarvis_YYYYMMDD.log` et montrent :
- La transcription exacte
- Les corrections appliquées
- L'intention détectée
- Les paramètres extraits

### Exemple de log réussi
```
[INFO] Transcription : 'ouvre calculatrice'
[DEBUG] Correction : 'calculatrice' -> 'calculatrice'
[INFO] Analyse de l'intention : 'ouvre calculatrice'
[DEBUG] Alias trouvé : 'calculatrice' -> 'calculator'
[INFO] Intention détectée : {'intent': 'open_app', 'parameters': {'app_name': 'calculator'}}
```

---

## 🎤 Conseils pour une Meilleure Reconnaissance

1. **Parlez clairement** et pas trop vite
2. **Utilisez des commandes courtes** : "ouvre calculatrice" > "est-ce que tu peux ouvrir la calculatrice"
3. **Attendez le signal** après "Jarvis" avant de parler
4. **Évitez le bruit de fond** autant que possible
5. **Ajoutez vos propres variations** dans la config si Whisper transcrit mal

---

## 📊 Commandes Supportées

| Intention | Exemples |
|-----------|----------|
| `open_app` | "ouvre calculatrice", "lance chrome", "démarre firefox" |
| `close_app` | "ferme chrome", "quitte firefox" |
| `web_search` | "recherche sur google python", "cherche météo paris" |
| `scroll_down` | "descend", "scroll down", "page suivante" |
| `scroll_up` | "monte", "scroll up", "page précédente" |
| `file_search` | "recherche fichier photo.jpg sur C", "cherche *.pdf" |
| `dictation` | "écris bonjour", "tape hello world" |
| `close_window` | "ferme la fenêtre active" |

---

## ✨ Nouveautés Version Actuelle

- ✅ Initial prompt pour guider Whisper vers le français
- ✅ Corrections automatiques des erreurs de transcription courantes
- ✅ Fuzzy matching pour les noms d'applications
- ✅ Support de variations multiples (calculatrice, calculette, calcul, etc.)
- ✅ Logs améliorés pour le débogage

---

## 🆘 Support

Si un problème persiste :
1. Vérifiez les logs en mode DEBUG
2. Ajoutez l'erreur de transcription dans `transcription_corrections`
3. Ajoutez des alias dans config.yaml
4. Testez avec un modèle Whisper plus grand (medium/large)
