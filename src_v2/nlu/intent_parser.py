"""
Module d'interprétation des intentions (NLU) pour Jarvis Commander.
Analyse les commandes vocales et extrait les intentions + paramètres.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from difflib import get_close_matches

logger = logging.getLogger(__name__)


class IntentParser:
    """Analyseur d'intentions basé sur des règles."""
    
    def __init__(self, app_aliases: Optional[Dict[str, str]] = None, app_paths: Optional[Dict[str, str]] = None):
        """
        Initialise le parseur d'intentions.
        
        Args:
            app_aliases: Dictionnaire des alias d'applications (ex: {"navigateur": "chrome"})
            app_paths: Dictionnaire des chemins d'applications (pour fuzzy matching)
        """
        self.app_aliases = app_aliases or {}
        self.app_paths = app_paths or {}
        
        # Corrections communes de transcription (erreurs fréquentes de Whisper)
        self.transcription_corrections = {
            'recalculate': 'calculatrice',
            'recalculatrice': 'calculatrice',
            'calculette': 'calculatrice',
            'calcul': 'calculatrice',
            'calculate': 'calculatrice',
            'chrome': 'chrome',
            'crom': 'chrome',
            'navigateur': 'navigateur',
            'navigater': 'navigateur',
            'explorateur': 'explorateur',
            'explorer': 'explorateur',
            'explorate': 'explorateur',
            'côme': 'chrome',
            'crome': 'chrome',
            'chrom': 'chrome',
        }
        
        # Patterns pour chaque type d'intention
        self.patterns = {
            'open_app': [
                r'(?:ouvre|lance|démarre|ouvrir|lancer|démarrer|exécute|exécuter)\s+(.+)',
                r'(?:ouvrir|lancer)\s+l\'application\s+(.+)',
                r'(?:c\'est|cest|met|mets)\s+(?:le\s+|la\s+)?(.+)', # "C'est le Chrome"
                r'(?:je\s+veux)\s+(?:lancer\s+|ouvrir\s+)?(.+)',
                r'^([a-zA-Z0-9\s]+)$', # Nom d'app direct (ex: "Chrome")
            ],
            'close_app': [
                r'(?:ferme|quitte|arrête|fermer|quitter|arrêter|termine|terminer)\s+(.+)',
                r'(?:fermer|quitter)\s+l\'application\s+(.+)',
                r'(?:coupe)\s+(.+)',
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
            'small_talk': [
                r'^(?:bonjour|salut|hello|coucou|hey)(?:\s+jarvis)?$',
                r'^(?:merci|c\'est\s+tout|cest\s+tout|stop|arrête|arrete)(?:\s+jarvis)?$',
                r'^(?:au\s+revoir|bye|à\s+plus|a\s+plus)(?:\s+jarvis)?$',
                r'^(?:ça\s+va|comment\s+vas\s+tu|tu\s+vas\s+bien)(?:\s+jarvis)?$',
            ],
        }
    
    def _correct_transcription_errors(self, texte: str) -> str:
        """
        Corrige les erreurs courantes de transcription.
        
        Args:
            texte: Texte potentiellement erroné
            
        Returns:
            Texte corrigé
        """
        words = texte.split()
        corrected_words = []
        
        for word in words:
            # Vérifier si le mot a une correction connue
            if word in self.transcription_corrections:
                corrected_words.append(self.transcription_corrections[word])
                logger.debug(f"Correction : '{word}' -> '{self.transcription_corrections[word]}'")
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

    def _clean_parasitic_words(self, texte: str) -> str:
        """
        Nettoie les mots parasites pour faciliter l'extraction.
        
        Args:
            texte: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        # Liste de mots/expressions parasites à supprimer
        parasites = [
            r"\bs'il te pla[îi]t\b", r"\bs'il vous pla[îi]t\b", r"\bstp\b", r"\bsvp\b",
            r"\bmerci\b", r"\bvite\b", r"\bmaintenant\b", r"\btout de suite\b",
            r"\ble\b", r"\bla\b", r"\bles\b", r"\bl'\b", r"\bun\b", r"\bune\b", r"\bdes\b",
            r"\bmon\b", r"\bma\b", r"\bmes\b", r"\bton\b", r"\bta\b", r"\btes\b",
            r"\bce\b", r"\bcette\b", r"\bces\b", r"\bcet\b"
        ]
        
        cleaned = texte
        for p in parasites:
            cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
            
        # Nettoyer les espaces multiples
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _resolve_app_name(self, app_name: str) -> str:
        """
        Résout le nom d'une application avec fuzzy matching.
        
        Args:
            app_name: Nom brut de l'application
            
        Returns:
            Nom résolu de l'application
        """
        # 1. Vérifier d'abord les alias exacts
        if app_name in self.app_aliases:
            resolved = self.app_aliases[app_name]
            logger.debug(f"Alias trouvé : '{app_name}' -> '{resolved}'")
            return resolved
        
        # 2. Vérifier si le nom existe directement dans les applications
        if app_name in self.app_paths:
            return app_name
        
        # 3. Fuzzy matching avec les noms d'applications et alias disponibles
        all_possible_names = list(self.app_paths.keys()) + list(self.app_aliases.keys())
        matches = get_close_matches(app_name, all_possible_names, n=1, cutoff=0.6)
        
        if matches:
            match = matches[0]
            # Si c'est un alias, résoudre
            if match in self.app_aliases:
                resolved = self.app_aliases[match]
                logger.info(f"Fuzzy match via alias : '{app_name}' -> '{match}' -> '{resolved}'")
                return resolved
            else:
                logger.info(f"Fuzzy match : '{app_name}' -> '{match}'")
                return match
        
        # 4. Aucune correspondance, retourner le nom original
        logger.debug(f"Aucune correspondance pour : '{app_name}'")
        return app_name
    
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
        
        # Supprimer la ponctuation (garder lettres, chiffres et espaces)
        texte = re.sub(r'[^\w\s]', '', texte)
        
        # Corriger les erreurs de transcription courantes
        texte = self._correct_transcription_errors(texte)
        
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
            # Nettoyer les mots parasites avant résolution
            app_name = self._clean_parasitic_words(app_name)
            # Résoudre les alias et fuzzy matching
            app_name = self._resolve_app_name(app_name)
            params['app_name'] = app_name
            
        elif intent == 'close_app':
            app_name = match.group(1).strip()
            # Nettoyer les mots parasites avant résolution
            app_name = self._clean_parasitic_words(app_name)
            # Résoudre les alias et fuzzy matching
            app_name = self._resolve_app_name(app_name)
            params['app_name'] = app_name
            
        elif intent == 'web_search':
            query = match.group(1).strip()
            # Nettoyer la requête
            query = self._clean_parasitic_words(query)
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
            
        elif intent == 'small_talk':
            # Identifier le type de small talk
            text = texte.lower()
            if any(w in text for w in ['bonjour', 'salut', 'hello', 'coucou']):
                params['type'] = 'greeting'
            elif any(w in text for w in ['merci', 'stop', 'arrête', 'arrete', 'tout']):
                params['type'] = 'thanks'
            elif any(w in text for w in ['revoir', 'bye', 'plus']):
                params['type'] = 'goodbye'
            elif any(w in text for w in ['va', 'vas']):
                params['type'] = 'status'
            else:
                params['type'] = 'unknown'
        
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
