"""
Module d'interprétation des intentions (NLU) pour Jarvis Commander.
Analyse les commandes vocales et extrait les intentions + paramètres.
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class IntentParser:
    """Analyseur d'intentions basé sur des règles."""
    
    def __init__(self, app_aliases: Optional[Dict[str, str]] = None):
        """
        Initialise le parseur d'intentions.
        
        Args:
            app_aliases: Dictionnaire des alias d'applications (ex: {"navigateur": "chrome"})
        """
        self.app_aliases = app_aliases or {}
        
        # Patterns pour chaque type d'intention
        self.patterns = {
            'open_app': [
                r'(?:ouvre|lance|démarre|ouvrir|lancer|démarrer|exécute|exécuter)\s+(.+)',
                r'(?:ouvrir|lancer)\s+l\'application\s+(.+)',
            ],
            'close_app': [
                r'(?:ferme|quitte|arrête|fermer|quitter|arrêter|termine|terminer)\s+(.+)',
                r'(?:fermer|quitter)\s+l\'application\s+(.+)',
            ],
            'web_search': [
                r'(?:recherche|cherche|trouve|google|googler)\s+(?:sur\s+)?(?:le\s+)?(?:web\s+)?(?:sur\s+)?(?:internet\s+)?(.+)',
                r'(?:fait|fais)\s+une\s+recherche\s+(?:web\s+)?(?:sur\s+)?(.+)',
                r'(?:fait|fais)\s+une\s+recherche\s+(?:web\s+)?(?:de|pour)\s+(.+)',
            ],
            'scroll_down': [
                r'(?:scroll|scrolle|défile|descends|descend)\s+(?:vers\s+)?(?:le\s+)?(?:bas|down)',
                r'(?:va|aller)\s+(?:vers\s+)?(?:le\s+)?bas',
                r'(?:page\s+)?(?:suivante|down)',
            ],
            'scroll_up': [
                r'(?:scroll|scrolle|défile|remonte|monte)\s+(?:vers\s+)?(?:le\s+)?(?:haut|up)',
                r'(?:va|aller)\s+(?:vers\s+)?(?:le\s+)?haut',
                r'(?:page\s+)?(?:précédente|up)',
            ],
            'file_search': [
                r'(?:recherche|cherche|trouve)\s+(?:sur\s+)?(?:le\s+)?(?:disque|lecteur)\s+([a-z])\s+(?:les\s+)?(?:fichiers?\s+)?(.+)',
                r'(?:recherche|cherche|trouve)\s+(?:les\s+)?(?:fichiers?\s+)?(.+)\s+(?:sur\s+)?(?:le\s+)?(?:disque|lecteur)\s+([a-z])',
                r'(?:recherche|cherche|trouve)\s+(?:les\s+)?(?:fichiers?\s+)?([^\s]+)\s+(?:sur\s+)?(?:mon|mes)\s+(?:disques?)',
            ],
            'dictation': [
                r'(?:dicte|écris|tape|écrire|taper|saisir|saisis)\s+(?:le\s+texte\s+)?(?:suivant\s+)?:?\s*(.+)',
                r'(?:dicte|écris|tape)\s+(.+)',
            ],
            'close_window': [
                r'(?:ferme|fermer)\s+(?:la\s+)?(?:fenêtre|fenetre)\s+(?:active|courante|en\s+cours)',
            ],
        }
    
    def parse(self, texte: str) -> Dict[str, Any]:
        """
        Analyse le texte et extrait l'intention + paramètres.
        
        Args:
            texte: Texte à analyser (commande vocale transcrite)
            
        Returns:
            Dictionnaire contenant 'intent' et 'parameters'
        """
        if not texte or not texte.strip():
            return {'intent': 'unknown', 'parameters': {}}
        
        # Normaliser le texte
        texte = texte.lower().strip()
        
        # Supprimer la ponctuation finale
        texte = re.sub(r'[.!?]+$', '', texte)
        
        logger.info(f"Analyse de l'intention : '{texte}'")
        
        # Tester chaque pattern
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, texte, re.IGNORECASE)
                if match:
                    parameters = self._extract_parameters(intent, match, texte)
                    result = {
                        'intent': intent,
                        'parameters': parameters
                    }
                    logger.info(f"Intention détectée : {result}")
                    return result
        
        # Aucune intention reconnue
        logger.warning(f"Intention inconnue pour : '{texte}'")
        return {'intent': 'unknown', 'parameters': {'text': texte}}
    
    def _extract_parameters(
        self,
        intent: str,
        match: re.Match,
        texte: str
    ) -> Dict[str, Any]:
        """
        Extrait les paramètres selon le type d'intention.
        
        Args:
            intent: Type d'intention
            match: Objet Match de la regex
            texte: Texte original
            
        Returns:
            Dictionnaire des paramètres
        """
        params = {}
        
        if intent == 'open_app':
            app_name = match.group(1).strip()
            # Résoudre les alias
            app_name = self.app_aliases.get(app_name, app_name)
            params['app_name'] = app_name
            
        elif intent == 'close_app':
            app_name = match.group(1).strip()
            app_name = self.app_aliases.get(app_name, app_name)
            params['app_name'] = app_name
            
        elif intent == 'web_search':
            query = match.group(1).strip()
            params['query'] = query
            
        elif intent in ['scroll_down', 'scroll_up']:
            direction = 'down' if intent == 'scroll_down' else 'up'
            params['direction'] = direction
            # Quantité par défaut
            params['amount'] = 3
            
        elif intent == 'file_search':
            # Extraire le disque et la requête
            groups = match.groups()
            
            if len(groups) >= 2:
                # Déterminer l'ordre des groupes
                if groups[0] and len(groups[0]) == 1 and groups[0].isalpha():
                    # Disque en premier
                    params['drive'] = groups[0].upper()
                    params['query'] = groups[1].strip()
                else:
                    # Requête en premier
                    params['query'] = groups[0].strip()
                    if groups[1] and len(groups[1]) == 1 and groups[1].isalpha():
                        params['drive'] = groups[1].upper()
                    else:
                        params['drive'] = None
            else:
                params['query'] = groups[0].strip() if groups else ''
                params['drive'] = None
            
            # Extraire l'extension si mentionnée
            ext_match = re.search(r'\.([a-z0-9]+)', params['query'], re.IGNORECASE)
            if ext_match:
                params['extension'] = ext_match.group(1)
            else:
                params['extension'] = None
                
        elif intent == 'dictation':
            text = match.group(1).strip()
            params['text'] = text
            
        elif intent == 'close_window':
            # Pas de paramètres spécifiques
            pass
        
        return params
    
    def add_app_alias(self, alias: str, app_name: str):
        """
        Ajoute un alias pour une application.
        
        Args:
            alias: L'alias (ex: "navigateur")
            app_name: Le nom réel de l'app (ex: "chrome")
        """
        self.app_aliases[alias.lower()] = app_name.lower()
        logger.info(f"Alias ajouté : '{alias}' -> '{app_name}'")
    
    def set_app_aliases(self, aliases: Dict[str, str]):
        """
        Définit tous les alias d'applications.
        
        Args:
            aliases: Dictionnaire des alias
        """
        self.app_aliases = {k.lower(): v.lower() for k, v in aliases.items()}
        logger.info(f"Aliases d'applications configurés : {len(self.app_aliases)} entrées")
    
    def get_supported_intents(self) -> List[str]:
        """
        Retourne la liste des intentions supportées.
        
        Returns:
            Liste des noms d'intentions
        """
        return list(self.patterns.keys()) + ['unknown']
