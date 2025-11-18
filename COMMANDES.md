# 🗣️ Liste des commandes vocales - Jarvis Commander

## 📱 Gestion d'applications

### Ouvrir une application
```
"Jarvis, ouvre Chrome"
"Jarvis, lance Discord"
"Jarvis, démarre Bambu Studio"
"Jarvis, exécute Fusion 360"
"Jarvis, ouvre la calculatrice"
"Jarvis, lance le bloc-notes"
"Jarvis, démarre Visual Studio Code"
```

### Fermer une application
```
"Jarvis, ferme Chrome"
"Jarvis, quitte Discord"
"Jarvis, arrête Bambu Studio"
"Jarvis, ferme la calculatrice"
"Jarvis, termine Visual Studio Code"
```

### Fermer la fenêtre active
```
"Jarvis, ferme la fenêtre active"
"Jarvis, ferme la fenêtre courante"
```

---

## 🌐 Recherche web

```
"Jarvis, recherche impression 3D résine"
"Jarvis, cherche tutoriel Python"
"Jarvis, trouve Arduino Uno pinout"
"Jarvis, fais une recherche sur les servo moteurs"
"Jarvis, google NVIDIA RTX 3060 specs"
"Jarvis, cherche recette crêpes"
```

---

## 🖱️ Contrôle de navigation

### Scroll
```
"Jarvis, scroll vers le bas"
"Jarvis, descends"
"Jarvis, défile vers le bas"
"Jarvis, page suivante"

"Jarvis, scroll vers le haut"
"Jarvis, remonte"
"Jarvis, défile vers le haut"
"Jarvis, page précédente"
```

---

## ⌨️ Dictée de texte

```
"Jarvis, dicte Bonjour tout le monde"
"Jarvis, écris ceci est un test"
"Jarvis, tape Hello World"
"Jarvis, dicte le texte suivant : Je suis content"
"Jarvis, écris mon adresse email@example.com"
```

**Note** : Le texte sera tapé dans la fenêtre active.

---

## 📁 Recherche de fichiers

### Recherche simple
```
"Jarvis, recherche robot"
"Jarvis, cherche impression"
"Jarvis, trouve design"
```

### Recherche sur un disque spécifique
```
"Jarvis, recherche sur le disque A les fichiers .stl"
"Jarvis, cherche sur le disque C les fichiers .py"
"Jarvis, trouve sur le disque Z les documents"
```

### Recherche par extension
```
"Jarvis, recherche les fichiers .stl de robot"
"Jarvis, cherche les fichiers .py sur le disque A"
"Jarvis, trouve les fichiers .pdf de manuel"
```

---

## 💡 Variantes de formulation

Jarvis comprend plusieurs façons de formuler la même commande :

### Synonymes pour "ouvrir"
- ouvre / lance / démarre / exécute / active

### Synonymes pour "fermer"
- ferme / quitte / arrête / termine

### Synonymes pour "rechercher"
- recherche / cherche / trouve / google

### Synonymes pour "descendre"
- descends / scroll en bas / défile vers le bas / va en bas

### Synonymes pour "remonter"
- remonte / scroll en haut / défile vers le haut / va en haut

### Synonymes pour "écrire"
- dicte / écris / tape / saisis

---

## 🎯 Conseils d'utilisation

### ✅ Bonnes pratiques

1. **Prononcez clairement** "Jarvis" pour activer l'écoute
2. **Attendez** le "Oui ?" avant de parler
3. **Soyez concis** : "Ouvre Chrome" plutôt que "Pourrais-tu ouvrir Chrome s'il te plaît"
4. **Parlez naturellement** mais distinctement

### ❌ À éviter

- Ne parlez pas trop vite
- N'enchaînez pas plusieurs commandes d'un coup
- Évitez le bruit de fond excessif (sauf si NVIDIA Broadcast activé)

---

## 🔄 Workflow typique

```
1. 🎤 Vous : "Jarvis"
2. 🤖 Jarvis : "Oui ?"
3. 🎤 Vous : "Ouvre Chrome"
4. 🤖 Jarvis : "J'ouvre Chrome" [Chrome s'ouvre]
5. ⏱️ Attendez quelques secondes
6. 🔁 Répétez : "Jarvis" pour une nouvelle commande
```

---

## 📋 Applications préconfigurées (par défaut)

Ces applications fonctionnent sans configuration supplémentaire :

- ✅ **Chrome** (si installé au chemin standard)
- ✅ **Firefox** (si installé)
- ✅ **Edge** (Windows 11)
- ✅ **Calculatrice** (Windows)
- ✅ **Bloc-notes** (Windows)
- ✅ **Explorateur** (Windows)
- ✅ **Visual Studio Code** (si installé)

**Pour ajouter d'autres apps** : Éditez `config\config.yaml`

---

## 🎨 Alias personnalisés

Vous pouvez créer des raccourcis dans `config\config.yaml` :

```yaml
app_aliases:
  navigateur: chrome
  calculette: calculator
  code: vscode
  musique: spotify
```

Puis utilisez :
```
"Jarvis, ouvre navigateur"  → Ouvre Chrome
"Jarvis, lance musique"     → Ouvre Spotify
```

---

## 🆘 En cas de problème

Si Jarvis ne comprend pas :
1. Vérifiez que le micro capte bien votre voix
2. Consultez les logs dans l'interface (onglet Journal)
3. Augmentez la sensibilité du wake word (Paramètres)
4. Essayez de reformuler avec un synonyme

**Logs détaillés** : `logs\jarvis_YYYYMMDD.log`

---

**Imprimez cette page pour l'avoir à portée de main ! 📄**
