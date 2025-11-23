# Module Brain (Cerveau)
# Gère le chargement du modèle LLM et la génération de réponses.

import sys
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import skills  # Import du module de compétences

class Brain:
    def __init__(self, model_repo="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", model_file="mistral-7b-instruct-v0.2.Q4_K_M.gguf"):
        self.model_path = self._download_model(model_repo, model_file)
        print(f"🧠 Chargement du modèle depuis {self.model_path}...")
        
        # Configuration pour GPU (n_gpu_layers=-1 pour tout mettre sur le GPU)
        # verbose=False pour éviter de spammer la console
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,          # Contexte réduit pour éviter OOM (4096 -> 2048)
                n_gpu_layers=-1,     # Utilise tout le GPU disponible
                verbose=False
            )
            print("✅ Cerveau chargé (Mode GPU activé) !")
        except Exception as e:
            print(f"⚠️ Erreur chargement GPU, tentative CPU... ({e})")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_gpu_layers=0,      # Mode CPU
                verbose=False
            )
            print("✅ Cerveau chargé (Mode CPU secours) !")

        # Définition de la personnalité et des outils
        self.system_prompt = """Tu es Jarvis, une IA assistante intelligente et utile connectée à un PC Windows.
Tu dois répondre de manière concise et précise en français.
Tu as la capacité d'effectuer des actions réelles sur l'ordinateur.

COMMANDES DISPONIBLES :
- Pour ouvrir Google Chrome, réponds UNIQUEMENT : [CMD:open_chrome]
- Pour ouvrir YouTube, réponds UNIQUEMENT : [CMD:open_youtube]

RÈGLES :
1. Si l'utilisateur demande une action listée ci-dessus, utilise le code [CMD:...] correspondant.
2. Sinon, réponds normalement à la question.
3. Ne dis jamais "Je ne peux pas faire ça" pour les actions listées ci-dessus.
"""

    def _download_model(self, repo_id, filename):
        """Télécharge le modèle automatiquement si absent."""
        print(f"🔍 Vérification du modèle {filename}...")
        try:
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir="./models",
                local_dir_use_symlinks=False
            )
            return model_path
        except Exception as e:
            print(f"❌ Erreur de téléchargement : {e}")
            sys.exit(1)

    def think(self, text):
        """Génère une réponse à partir du texte utilisateur."""
        # Construction du prompt avec System Prompt (Format Mistral)
        # On injecte le system prompt avant l'instruction utilisateur
        full_prompt = f"[INST] {self.system_prompt}\n\nUtilisateur : {text} [/INST]"
        
        output = self.llm(
            full_prompt,
            max_tokens=512,
            stop=["</s>", "[/INST]"],
            echo=False
        )
        
        response = output['choices'][0]['text'].strip()
        
        # Détection et exécution des commandes
        if "[CMD:open_chrome]" in response:
            skills.execute_skill("open_chrome")
            return "J'ouvre Google Chrome pour vous."
        elif "[CMD:open_youtube]" in response:
            skills.execute_skill("open_youtube")
            return "J'ouvre YouTube tout de suite."
            
        return response

    def analyze_intent(self, text):
        """
        Analyse l'intention avec le LLM si les regex ont échoué.
        Retourne un dict {intent, parameters}.
        """
        import json
        import re
        
        prompt = f"""[INST] Tu es un analyseur d'intentions pour un assistant vocal.
Ton but est de convertir une phrase utilisateur en commande structurée JSON.

INTENTIONS POSSIBLES :
- web_search : pour faire une recherche sur internet (param: query)
- open_app : pour ouvrir un logiciel (param: app_name)
- close_app : pour fermer un logiciel (param: app_name)
- scroll_down : pour descendre dans une page
- scroll_up : pour monter dans une page
- small_talk : pour la conversation (param: type=greeting|thanks|goodbye|unknown)
- unknown : si aucune intention ne correspond

RÈGLES :
1. Réponds UNIQUEMENT avec le JSON valide.
2. Pas de blabla avant ou après.
3. Si c'est ambigu, choisis l'intention la plus probable.

Exemples :
"Cherche météo Paris" -> {{"intent": "web_search", "parameters": {{"query": "météo Paris"}}}}
"Ouvre Chrome" -> {{"intent": "open_app", "parameters": {{"app_name": "Chrome"}}}}
"Descends un peu" -> {{"intent": "scroll_down", "parameters": {{}}}}
"Bonjour" -> {{"intent": "small_talk", "parameters": {{"type": "greeting"}}}}

Phrase à analyser : "{text}" [/INST]"""

        try:
            output = self.llm(
                prompt,
                max_tokens=128,
                stop=["</s>", "[/INST]"],
                echo=False,
                temperature=0.1 # Très déterministe
            )
            
            response = output['choices'][0]['text'].strip()
            
            # Nettoyage pour extraire le JSON (au cas où le LLM bavarde)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return {'intent': 'unknown', 'parameters': {}}
                
        except Exception as e:
            print(f"Erreur analyse LLM : {e}")
            return {'intent': 'unknown', 'parameters': {}}

# Test rapide si exécuté directement
if __name__ == "__main__":
    brain = Brain()
    print("Réponse :", brain.think("Ouvre chrome s'il te plait"))
