# Module UI (Interface Utilisateur) - Jarvis V2
# Design "Iron Man" / Futuriste

import asyncio
from datetime import datetime
from nicegui import ui, app
from config_manager import config

# --- CSS GLOBAL & THEME ---
# On injecte les styles CSS pour l'effet "Iron Man"
THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Share+Tech+Mono&display=swap');

:root {
    --neon-cyan: #00f3ff;
    --neon-blue: #0066ff;
    --dark-bg: #050510;
    --panel-bg: rgba(10, 20, 40, 0.7);
    --border-color: rgba(0, 243, 255, 0.3);
}

body {
    background-color: var(--dark-bg);
    color: var(--neon-cyan);
    font-family: 'Share Tech Mono', monospace;
    overflow: hidden; /* Pas de scroll global */
}

.orbitron {
    font-family: 'Orbitron', sans-serif;
}

/* Effet de grille en arrière-plan */
.bg-grid {
    background-image: 
        linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px);
    background-size: 30px 30px;
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1;
}

/* Panneaux vitrés */
.glass-panel {
    background: var(--panel-bg);
    border: 1px solid var(--border-color);
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
    backdrop-filter: blur(5px);
    border-radius: 4px;
    position: relative;
}

/* Coins décoratifs */
.glass-panel::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px;
    width: 10px; height: 10px;
    border-top: 2px solid var(--neon-cyan);
    border-left: 2px solid var(--neon-cyan);
}
.glass-panel::after {
    content: '';
    position: absolute;
    bottom: -1px; right: -1px;
    width: 10px; height: 10px;
    border-bottom: 2px solid var(--neon-cyan);
    border-right: 2px solid var(--neon-cyan);
}

/* Animation Arc Reactor */
.arc-reactor-container {
    position: relative;
    width: 200px;
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.arc-circle {
    position: absolute;
    border-radius: 50%;
    border: 2px solid var(--neon-cyan);
    box-shadow: 0 0 20px var(--neon-cyan), inset 0 0 20px var(--neon-cyan);
}

.c1 { width: 180px; height: 180px; border-width: 4px; animation: spin-right 10s linear infinite; border-color: rgba(0, 243, 255, 0.6); border-left-color: transparent; border-right-color: transparent; }
.c2 { width: 140px; height: 140px; border-width: 2px; animation: spin-left 7s linear infinite; border-color: rgba(0, 243, 255, 0.8); border-top-color: transparent; border-bottom-color: transparent; }
.c3 { width: 100px; height: 100px; border-width: 6px; box-shadow: 0 0 30px var(--neon-cyan); background: rgba(0, 243, 255, 0.1); }

.core-glow {
    width: 60px; height: 60px;
    background: radial-gradient(circle, #fff 0%, var(--neon-cyan) 60%, transparent 100%);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes spin-right { 100% { transform: rotate(360deg); } }
@keyframes spin-left { 100% { transform: rotate(-360deg); } }
@keyframes pulse { 0%, 100% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } }

/* Scrollbar custom */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #050510; }
::-webkit-scrollbar-thumb { background: var(--neon-cyan); border-radius: 3px; }
"""

from ui.components import AudioVisualizer

class JarvisUI:
    def __init__(self, brain_instance=None):
        self.brain = brain_instance
        self.logs_container = None
        self.status_label = None
        self.visualizer = None
        self.time_label = None
        self.date_label = None
        self.start_overlay = None
        
        # Configuration de l'app
        ui.add_head_html(f'<style>{THEME_CSS}</style>')
        
        # Construction de l'interface
        self.build_interface()
        
        # Timer pour l'heure
        self.timer = ui.timer(1.0, self.update_time)

    def build_interface(self):
        """Construit la structure complète de la page."""
        
        # Arrière-plan grille
        ui.element('div').classes('bg-grid')
        
        # --- HEADER ---
        with ui.row().classes('w-full h-16 items-center justify-between px-6 glass-panel mb-4'):
            with ui.row().classes('items-center gap-4'):
                ui.label('SYS.OS.V.14.2').classes('text-xs opacity-70')
                self.time_label = ui.label('00:00:00').classes('orbitron text-3xl font-bold text-white tracking-widest')
                self.date_label = ui.label('INIT...').classes('text-sm text-cyan-300')
            
            with ui.row().classes('items-center gap-4'):
                ui.label('LOCALISATION: TRIANGULATION...').classes('text-xs text-right opacity-70')
                ui.icon('fingerprint', size='32px').classes('text-cyan-400 animate-pulse')

        # --- MAIN CONTENT (GRID) ---
        with ui.grid(columns='1fr 2fr 1fr').classes('w-full h-[calc(100vh-140px)] gap-4 px-4'):
            
            # 1. GAUCHE : Status Système
            with ui.column().classes('h-full glass-panel p-4 justify-between'):
                ui.label('ÉTAT ARMURE').classes('orbitron text-lg border-b border-cyan-500/30 w-full pb-2')
                
                # Placeholder visuel (Graphiques CSS)
                with ui.column().classes('w-full gap-2 my-4 flex-grow justify-center items-center opacity-80'):
                    # Simulation d'un diagramme
                    for i in range(5):
                        with ui.row().classes('w-full items-center gap-2'):
                            ui.label(f'SYS-{i:02d}').classes('text-xs w-12')
                            ui.element('div').classes('h-2 bg-cyan-900 flex-grow rounded overflow-hidden').style(f'width: {100}%').content = \
                                f'<div style="width: {60 + i*5}%; height: 100%; background: var(--neon-cyan);"></div>'
                
                # CPU / RAM Footer
                with ui.row().classes('w-full justify-between text-xs border-t border-cyan-500/30 pt-2'):
                    ui.label('MEM: 64TB')
                    ui.label('PWR: ARC-IV REACTOR')

            # 2. CENTRE : Arc Reactor & Interaction
            with ui.column().classes('h-full items-center justify-center relative glass-panel p-8'):
                # Arc Reactor Animation
                with ui.element('div').classes('arc-reactor-container mb-12'):
                    ui.element('div').classes('arc-circle c1')
                    ui.element('div').classes('arc-circle c2')
                    ui.element('div').classes('arc-circle c3')
                    ui.element('div').classes('core-glow')
                
                # Status Text
                self.status_label = ui.label('EN ATTENTE').classes('orbitron text-4xl font-bold tracking-[0.5em] text-cyan-100 animate-pulse')
                
                # Visualizer Audio (Real-time)
                with ui.row().classes('w-full justify-center mt-8'):
                    self.visualizer = AudioVisualizer()

            # 3. DROITE : Modules & Logs
            with ui.column().classes('h-full glass-panel p-4 gap-4'):
                # Modules Actifs
                with ui.column().classes('w-full gap-2'):
                    ui.label('MODULES ACTIFS').classes('orbitron text-lg border-b border-cyan-500/30 w-full pb-2')
                    self._module_item('PROTOCOLE VOICE', True)
                    self._module_item('ARMEMENT (OFFLINE)', False)
                    self._module_item('SURVEILLANCE RÉSEAU', True)
                    self._module_item('I.A. NEURONALE', True)
                
                # Logs Terminal
                with ui.column().classes('w-full flex-grow border-t border-cyan-500/30 pt-2 overflow-hidden'):
                    ui.label('LOG SYSTÈME').classes('orbitron text-sm mb-2 opacity-80')
                    self.logs_container = ui.column().classes('w-full h-full overflow-y-auto text-xs font-mono gap-1 scroll-smooth')
                    self.add_log("SYSTÈME INITIALISÉ...", "SYS")
                    self.add_log("CONNEXION AU SERVEUR CENTRAL...", "NET")
                    self.add_log("JARVIS: Bonjour monsieur.", "AI")

        # --- FOOTER ---
        with ui.footer().classes('bg-transparent p-2 text-center'):
            ui.label('CONNECTÉ AU SERVEUR STARK INDUSTRIES').classes('text-[10px] opacity-50 tracking-widest w-full')

        # --- OVERLAY START ---
        self.start_overlay = ui.element('div').classes('fixed inset-0 bg-black z-50 flex flex-col items-center justify-center cursor-pointer')
        with self.start_overlay:
            ui.icon('power_settings_new', size='64px').classes('text-cyan-400 animate-pulse mb-4')
            ui.label('J.A.R.V.I.S.').classes('orbitron text-6xl font-bold text-white tracking-widest mb-2')
            ui.label('CLIQUER POUR INITIALISER LE SYSTÈME').classes('text-sm opacity-70 tracking-widest')
        
        # Event click pour démarrer (et supprimer l'overlay)
        self.start_overlay.on('click', self.start_system)

    def _module_item(self, name, active):
        """Crée un item de module avec indicateur."""
        color = 'bg-cyan-400' if active else 'bg-red-500'
        opacity = 'opacity-100' if active else 'opacity-50'
        with ui.row().classes(f'w-full items-center gap-2 p-2 bg-cyan-900/20 rounded {opacity}'):
            ui.element('div').classes(f'w-2 h-2 rounded-full {color} shadow-[0_0_5px_currentColor]')
            ui.label(name).classes('text-xs')

    def update_time(self):
        """Met à jour l'heure et la date."""
        now = datetime.now()
        if self.time_label:
            self.time_label.text = now.strftime('%H:%M:%S')
        if self.date_label:
            self.date_label.text = now.strftime('%A %d %B %Y').upper()

    def add_log(self, message, source="SYS"):
        """Ajoute une ligne de log."""
        if self.logs_container:
            timestamp = datetime.now().strftime('%H:%M:%S')
            with self.logs_container:
                ui.label(f"[{timestamp}] >>> {source}: {message}").classes('text-cyan-300 hover:text-white transition-colors')
            # Auto-scroll
            self.logs_container.run_method('scrollTo', 0, 10000)

    def update_audio_level(self, level: float):
        """Met à jour le visualiseur audio."""
        if self.visualizer:
            self.visualizer.update(level)

    def set_state(self, state: str):
        """Change l'état visuel de l'interface."""
        if not self.status_label:
            return
            
        # Reset classes
        base_classes = 'orbitron text-4xl font-bold tracking-[0.5em] animate-pulse'
        
        if state == "IDLE":
            self.status_label.text = "EN VEILLE"
            self.status_label.classes(replace=f'{base_classes} text-cyan-100')
            self._update_reactor_color('#00f3ff') # Cyan
            
        elif state == "LISTENING":
            self.status_label.text = "ÉCOUTE..."
            self.status_label.classes(replace=f'{base_classes} text-green-400')
            self._update_reactor_color('#00ff00') # Green
            
        elif state == "PROCESSING":
            self.status_label.text = "ANALYSE..."
            self.status_label.classes(replace=f'{base_classes} text-purple-400')
            self._update_reactor_color('#a855f7') # Purple
            
        elif state == "SPEAKING":
            self.status_label.text = "VOCALISATION"
            self.status_label.classes(replace=f'{base_classes} text-orange-400')
            self._update_reactor_color('#f97316') # Orange

    def _update_reactor_color(self, color: str):
        """Change la couleur du réacteur (via JS car CSS variables c'est mieux mais ici on fait simple)."""
        # On pourrait utiliser des classes CSS, mais pour l'instant on laisse comme ça
        # Idéalement on injecterait une variable CSS --reactor-color
        ui.run_javascript(f"""
            document.documentElement.style.setProperty('--neon-cyan', '{color}');
        """)

    async def start_system(self):
        """Initialise le système au clic."""
        self.start_overlay.style('display: none;')
        self.add_log("INITIALISATION PROTOCOLES AUDIO...", "SYS")
        await asyncio.sleep(0.5)
        self.add_log("MICROPHONE ACTIVÉ", "AUDIO")
        self.set_state("IDLE")
        ui.notify('Système Jarvis activé', type='positive')

# Fonction factory pour main.py
def build(brain=None):
    return JarvisUI(brain)
