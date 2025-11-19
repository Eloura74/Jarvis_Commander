# 🛠️ Fix Rapide : Problème "calculatrice"

## Problème
Vous dites : **"ouvre calculatrice"**  
Jarvis entend : `"recalculate"` ou `"recalculatrice"`  
Résultat : ❌ Commande non reconnue

## ✅ Solutions Appliquées (Automatiques)

Les améliorations suivantes ont été automatiquement intégrées dans le code :

### 1. Initial Prompt pour Whisper
Le moteur de reconnaissance vocale est maintenant guidé avec des exemples de commandes françaises courantes.

**Fichier** : `audio/stt.py`

### 2. Corrections Automatiques
Les erreurs de transcription courantes sont corrigées automatiquement :
- `recalculate` → `calculatrice` ✓
- `recalculatrice` → `calculatrice` ✓
- `calculette` → `calculatrice` ✓
- `calculate` → `calculatrice` ✓

**Fichier** : `nlu/intent_parser.py`

### 3. Fuzzy Matching
Le système trouve automatiquement l'application même avec des petites erreurs d'orthographe (60% de similarité).

**Fichier** : `nlu/intent_parser.py`

---

## 🎯 Configuration Recommandée

Pour optimiser la reconnaissance de "calculatrice", ajoutez dans votre `config/config.yaml` :

```yaml
# MÉTHODE SIMPLE (Recommandée)
applications:
  calculator: "calc.exe"
  calculatrice: "calc.exe"
  calculette: "calc.exe"
  calcul: "calc.exe"
  calc: "calc.exe"

# Alias optionnels (pour gérer les erreurs persistantes)
app_aliases:
  recalculate: calculator
  calculateur: calculator
```

---

## 🧪 Test

1. **Redémarrez Jarvis** :
   ```bash
   python main.py
   ```

2. **Testez ces variations** :
   - "Jarvis, ouvre calculatrice"
   - "Jarvis, lance calculette"
   - "Jarvis, ouvre calcul"
   - Même si Whisper transcrit mal, le système devrait corriger automatiquement !

---

## 📊 Résultat Attendu

```
[INFO] 🎯 Wake word détecté!
[INFO] Transcription : ouvre calculatrice
[INFO] Intention : open_app | Params : {'app_name': 'calculator'}
[INFO] ✅ Lancement de calculator
```

---

## 🔍 Si ça ne marche toujours pas

### Vérifiez votre config
```bash
# Ouvrez config/config.yaml et cherchez "calculator"
notepad config/config.yaml
```

### Activez les logs DEBUG
```yaml
logging:
  level: "DEBUG"
```

### Consultez les logs
```bash
# Les logs montrent exactement ce qui se passe
type logs\jarvis_*.log
```

---

## 🎤 Autres Commandes à Tester

- "ouvre chrome" / "lance navigateur"
- "ouvre explorateur" / "lance fichiers"
- "recherche python sur google"
- "ferme chrome"

---

## 📚 Documentation Complète

Pour plus de détails, consultez :
- **AMELIORATION_RECONNAISSANCE_VOCALE.md** - Guide complet
- **COMMANDES.md** - Liste de toutes les commandes
- **README.md** - Documentation générale
