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

# Test rapide si exécuté directement
if __name__ == "__main__":
    brain = Brain()
    print("Réponse :", brain.think("Ouvre chrome s'il te plait"))
