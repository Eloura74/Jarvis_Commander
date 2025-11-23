# Module UI (Interface Utilisateur) - Jarvis V2.0 "Ultimate"
# Design "Iron Man" / Futuriste - Version Finale

import asyncio
from datetime import datetime
from nicegui import ui, app
import queue
from config_manager import config

# --- CSS GLOBAL & THEME V2.0 ---
THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;500;700&display=swap');

:root {
    --neon-cyan: #00f3ff;
    --neon-blue: #0066ff;
    --neon-purple: #bc13fe;
    --neon-orange: #ff9d00;
    --neon-red: #ff003c;
    --dark-bg: #020205;
    --panel-bg: rgba(5, 10, 20, 0.65);
    --glass-border: rgba(0, 243, 255, 0.2);
    --scanline-color: rgba(0, 255, 255, 0.03);
}

body {
    background-color: var(--dark-bg);
    color: var(--neon-cyan);
    font-family: 'Share Tech Mono', monospace;
    overflow: hidden;
    margin: 0;
}

.orbitron { font-family: 'Orbitron', sans-serif; }
.rajdhani { font-family: 'Rajdhani', sans-serif; }

/* --- BACKGROUND FX --- */
.bg-grid {
    position: absolute;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: 
        linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    transform: perspective(500px) rotateX(20deg) scale(1.5);
    transform-origin: top center;
    opacity: 0.5;
    z-index: -2;
    animation: grid-move 20s linear infinite;
}

@keyframes grid-move {
    0% { background-position: 0 0; }
    100% { background-position: 0 40px; }
}

.vignette {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, transparent 40%, #000 100%);
    z-index: -1;
    pointer-events: none;
}

.scanlines {
    position: fixed;
    inset: 0;
    background: linear-gradient(to bottom, transparent 50%, var(--scanline-color) 51%);
    background-size: 100% 4px;
    z-index: 999;
    pointer-events: none;
    opacity: 0.6;
}

/* --- HUD PANELS --- */
.hud-panel {
    background: var(--panel-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(8px);
    position: relative;
    clip-path: polygon(
        15px 0, 100% 0, 
        100% calc(100% - 15px), calc(100% - 15px) 100%, 
        0 100%, 0 15px
    );
    box-shadow: inset 0 0 20px rgba(0, 243, 255, 0.05);
    transition: all 0.3s ease;
}

.hud-panel:hover {
    border-color: rgba(0, 243, 255, 0.5);
    box-shadow: inset 0 0 30px rgba(0, 243, 255, 0.1);
}

.hud-corner {
    position: absolute;
    width: 20px; height: 20px;
    border: 2px solid var(--neon-cyan);
    opacity: 0.7;
    transition: all 0.3s ease;
}
.tl { top: 0; left: 0; border-right: none; border-bottom: none; }
.tr { top: 0; right: 0; border-left: none; border-bottom: none; }
.bl { bottom: 0; left: 0; border-right: none; border-top: none; }
.br { bottom: 0; right: 0; border-left: none; border-top: none; }

/* --- ARC REACTOR V2 --- */
.reactor-container {
    position: relative;
    width: 280px; height: 280px;
    display: flex; justify-content: center; align-items: center;
}

.reactor-ring {
    position: absolute;
    border-radius: 50%;
    border: 2px solid var(--neon-cyan);
    box-shadow: 0 0 15px var(--neon-cyan);
    opacity: 0.8;
}

.r1 { width: 260px; height: 260px; border-width: 1px; border-style: dashed; animation: spin-cw 20s linear infinite; opacity: 0.3; }
.r2 { width: 220px; height: 220px; border-width: 2px; border-top-color: transparent; border-bottom-color: transparent; animation: spin-ccw 10s linear infinite; }
.r3 { width: 180px; height: 180px; border-width: 4px; border-left-color: transparent; border-right-color: transparent; animation: spin-cw 5s linear infinite; }
.r4 { width: 100px; height: 100px; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--neon-cyan); box-shadow: inset 0 0 20px var(--neon-cyan); }

.reactor-core {
    width: 60px; height: 60px;
    background: radial-gradient(circle, #fff 0%, var(--neon-cyan) 50%, transparent 100%);
    border-radius: 50%;
    box-shadow: 0 0 40px var(--neon-cyan);
    animation: pulse-core 2s ease-in-out infinite;
    z-index: 10;
}

@keyframes spin-cw { 100% { transform: rotate(360deg); } }
@keyframes spin-ccw { 100% { transform: rotate(-360deg); } }
@keyframes pulse-core { 
    0%, 100% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 30px var(--neon-cyan); } 
    50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 60px var(--neon-cyan); } 
}

/* --- TEXT GLITCH --- */
.glitch-text {
    position: relative;
    animation: glitch-skew 3s infinite linear alternate-reverse;
}
.glitch-text::before, .glitch-text::after {
    content: attr(data-text);
    position: absolute;
    left: 0;
    width: 100%;
    height: 100%;
}
.glitch-text::before {
    left: 2px; text-shadow: -1px 0 #ff00c1; clip: rect(44px, 450px, 56px, 0);
    animation: glitch-anim 5s infinite linear alternate-reverse;
}
.glitch-text::after {
    left: -2px; text-shadow: -1px 0 #00fff9; clip: rect(44px, 450px, 56px, 0);
    animation: glitch-anim2 5s infinite linear alternate-reverse;
}

@keyframes glitch-anim {
    0% { clip: rect(12px, 9999px, 32px, 0); }
    100% { clip: rect(65px, 9999px, 89px, 0); }
}
@keyframes glitch-anim2 {
    0% { clip: rect(89px, 9999px, 12px, 0); }
    100% { clip: rect(12px, 9999px, 65px, 0); }
}

/* --- SCROLLBAR --- */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--neon-cyan); }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.5); }

"""

from .components import AudioVisualizer

class JarvisUI:
    def __init__(self, brain_instance=None):
        self.brain = brain_instance
        self.logs_container = None
        self.status_label = None
        self.visualizer = None
        self.time_label = None
        self.date_label = None
        self.start_overlay = None
        self.start_overlay = None
        self.reactor_core = None
        self.controller = None # Référence au contrôleur principal
        
        # Configuration de l'app
        ui.add_head_html(f'<style>{THEME_CSS}</style>')
        
        # Construction de l'interface
        self.build_interface()
        
        # Timer pour l'heure
        self.timer = ui.timer(1.0, self.update_time)

        # --- GESTION THREAD-SAFE ---
        self._ui_queue = queue.Queue()
        self._queue_timer = ui.timer(0.05, self._process_ui_queue)

    def _process_ui_queue(self):
        try:
            while True:
                func, args, kwargs = self._ui_queue.get_nowait()
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    print(f"Erreur UI Queue: {e}")
                finally:
                    self._ui_queue.task_done()
        except queue.Empty:
            pass

    def run_threadsafe(self, func, *args, **kwargs):
        self._ui_queue.put((func, args, kwargs))

    def set_state_threadsafe(self, state: str):
        self.run_threadsafe(self.set_state, state)

    def add_log_threadsafe(self, message: str, source: str = "SYS"):
        self.run_threadsafe(self.add_log, message, source)

    def update_audio_level_threadsafe(self, level: float):
        self.run_threadsafe(self.update_audio_level, level)

    def build_interface(self):
        """Construit l'interface V2.0."""
        
        # Background FX
        ui.element('div').classes('bg-grid')
        ui.element('div').classes('vignette')
        ui.element('div').classes('scanlines')
        
        # --- HEADER ---
        with ui.row().classes('w-full h-20 items-center justify-between px-8 pt-4 mb-2 z-10'):
            # Left: Time & Date
            with ui.row().classes('items-center gap-6'):
                with ui.column().classes('gap-0'):
                    self.time_label = ui.label('00:00:00').classes('orbitron text-4xl font-bold text-white tracking-widest drop-shadow-[0_0_10px_rgba(0,243,255,0.8)]')
                    self.date_label = ui.label('INIT...').classes('text-sm text-cyan-400 tracking-[0.2em] uppercase')
            
            # Center: Title
            with ui.column().classes('items-center'):
                ui.label('JARVIS COMMANDER').classes('orbitron text-xl font-bold tracking-[0.5em] opacity-80')
                ui.label('SYSTEM V2.0 // ONLINE').classes('text-[10px] text-cyan-600 tracking-widest')

            # Right: Tech Data
            with ui.row().classes('items-center gap-4 text-xs text-cyan-500 font-mono'):
                with ui.column().classes('items-end'):
                    ui.label('CPU: 34% // TEMP: 45°C')
                    ui.label('MEM: 12GB // NET: SECURE')
                with ui.button(icon='settings', on_click=self._show_settings_dialog).props('flat round dense').classes('text-cyan-400'):
                    ui.tooltip('Paramètres Système')
                ui.icon('hub', size='32px').classes('text-cyan-400 animate-spin-slow')

        # --- MAIN GRID ---
        with ui.grid(columns='1fr 2fr 1fr').classes('w-full h-[calc(100vh-120px)] gap-6 px-6 pb-6 z-10'):
            
            # 1. LEFT PANEL: SYSTEM STATUS
            with ui.column().classes('h-full hud-panel p-6 justify-between'):
                # Header Panel
                with ui.row().classes('w-full items-center justify-between border-b border-cyan-900 pb-2 mb-4'):
                    ui.label('DIAGNOSTICS').classes('orbitron text-lg text-cyan-100')
                    ui.element('div').classes('w-2 h-2 bg-cyan-400 rounded-full animate-pulse')

                # Content
                with ui.column().classes('w-full gap-4 flex-grow'):
                    self._stat_bar("INTEGRITY", 100, "bg-cyan-400")
                    self._stat_bar("POWER", 85, "bg-blue-500")
                    self._stat_bar("SHIELD", 0, "bg-red-500") # Offline
                    
                    ui.separator().classes('bg-cyan-900/50 my-2')
                    
                    # Fake Terminal Output
                    with ui.column().classes('w-full font-mono text-[10px] text-cyan-600 opacity-70 gap-1'):
                        for i in range(5):
                            ui.label(f"> CHECKING SECTOR {i+1}0{i}... OK")

                # Footer Panel
                ui.label('STARK INDUSTRIES // CONFIDENTIAL').classes('text-[9px] text-center w-full opacity-40 tracking-widest mt-2')

            # 2. CENTER PANEL: ARC REACTOR
            with ui.column().classes('h-full items-center justify-center relative'):
                
                # Reactor Container
                with ui.element('div').classes('reactor-container mb-16'):
                    ui.element('div').classes('reactor-ring r1')
                    ui.element('div').classes('reactor-ring r2')
                    ui.element('div').classes('reactor-ring r3')
                    ui.element('div').classes('reactor-ring r4')
                    self.reactor_core = ui.element('div').classes('reactor-core')
                
                # Status Label (Glitch Effect)
                self.status_label = ui.label('EN VEILLE').classes('orbitron text-5xl font-bold tracking-[0.3em] text-white drop-shadow-[0_0_20px_rgba(0,243,255,0.8)] mb-8')
                self.status_label.props('data-text="EN VEILLE"') # For glitch effect
                
                # Audio Visualizer
                with ui.row().classes('w-full justify-center h-24 items-end gap-1'):
                    self.visualizer = AudioVisualizer() # On garde le composant existant pour l'instant, on pourrait le customiser plus tard

            # 3. RIGHT PANEL: LOGS & MODULES
            with ui.column().classes('h-full hud-panel p-6'):
                # Header Panel
                with ui.row().classes('w-full items-center justify-between border-b border-cyan-900 pb-2 mb-4'):
                    ui.label('COMMUNICATION LOG').classes('orbitron text-lg text-cyan-100')
                    ui.icon('wifi', size='xs').classes('text-cyan-400')

                # Logs Container
                self.logs_container = ui.column().classes('w-full flex-grow overflow-y-auto text-xs font-mono gap-2 p-2 scroll-smooth')
                
                # Initial Logs
                self.add_log("SYSTEM BOOT SEQUENCE INITIATED...", "KERNEL")
                self.add_log("LOADING NEURAL INTERFACE...", "AI")
                self.add_log("WAITING FOR USER INPUT...", "SYS")

        # --- OVERLAY ---
        self.start_overlay = ui.element('div').classes('fixed inset-0 bg-black z-50 flex flex-col items-center justify-center cursor-pointer')
        with self.start_overlay:
            ui.element('div').classes('reactor-core w-32 h-32 mb-8 animate-pulse')
            ui.label('TOUCH TO INITIALIZE').classes('orbitron text-2xl text-cyan-400 tracking-[0.5em] animate-pulse')
        
        self.start_overlay.on('click', self.start_system)

    def _stat_bar(self, label, value, color_class):
        """Crée une barre de progression stylisée."""
        with ui.column().classes('w-full gap-1'):
            with ui.row().classes('w-full justify-between text-xs'):
                ui.label(label).classes('font-bold tracking-wider')
                ui.label(f"{value}%")
            ui.element('div').classes('h-1.5 w-full bg-gray-900 rounded-full overflow-hidden').content = \
                f'<div class="h-full {color_class} shadow-[0_0_10px_currentColor]" style="width: {value}%"></div>'

    def update_time(self):
        now = datetime.now()
        if self.time_label: self.time_label.text = now.strftime('%H:%M:%S')
        if self.date_label: self.date_label.text = now.strftime('%A %d %B %Y').upper()

    def add_log(self, message, source="SYS"):
        if self.logs_container:
            timestamp = datetime.now().strftime('%H:%M:%S')
            color = "text-cyan-300"
            if source == "USR": color = "text-white font-bold"
            elif source == "AI": color = "text-purple-300"
            elif source == "ERR": color = "text-red-400"
            
            with self.logs_container:
                ui.label(f"[{timestamp}] {source} >> {message}").classes(f'{color} border-l-2 border-cyan-900 pl-2 hover:bg-cyan-900/20 transition-colors w-full')
            self.logs_container.run_method('scrollTo', 0, 10000)

    def update_audio_level(self, level: float):
        if self.visualizer: self.visualizer.update(level)
        # Effet dynamique sur le réacteur
        scale = 1.0 + (level * 0.5)
        if self.reactor_core:
            self.reactor_core.style(f'transform: scale({scale}); box-shadow: 0 0 {40 + level*100}px var(--neon-cyan)')

    def set_state(self, state: str):
        if not self.status_label: return
        
        # Colors
        c_cyan = '#00f3ff'
        c_green = '#00ff41'
        c_orange = '#ff9d00'
        c_purple = '#bc13fe'
        
        text = "EN VEILLE"
        color = c_cyan
        
        if state == "LISTENING":
            text = "ÉCOUTE..."
            color = c_green
        elif state == "PROCESSING":
            text = "ANALYSE..."
            color = c_purple
        elif state == "SPEAKING":
            text = "VOCALISATION"
            color = c_orange
            
        self.status_label.text = text
        self.status_label.style(f'color: {color}; text-shadow: 0 0 20px {color}')
        self._update_reactor_color(color)

    def _update_reactor_color(self, color: str):
        ui.run_javascript(f"document.documentElement.style.setProperty('--neon-cyan', '{color}');")

    async def start_system(self):
        self.start_overlay.style('display: none;')
        self.add_log("SYSTEM ONLINE", "SYS")
        await asyncio.sleep(0.2)
        self.set_state("IDLE")
        ui.notify('SYSTEM READY', type='positive')

    def set_controller(self, controller):
        """Définit le contrôleur principal."""
        self.controller = controller

    def _show_settings_dialog(self):
        """Affiche la modale de paramètres."""
        if not self.controller:
            ui.notify("Contrôleur non connecté", type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('bg-[#050510] border border-cyan-500/50 w-96'):
            ui.label('CONFIGURATION SYSTÈME').classes('orbitron text-lg text-cyan-400 mb-4')
            
            # 1. Sélecteur de Voix
            ui.label('Synthèse Vocale').classes('text-xs opacity-70')
            voices = self.controller.tts_engine.get_available_voices() if self.controller.tts_engine else []
            
            if voices:
                ui.select(
                    options=voices, 
                    value=self.controller.tts_engine.voice_id,
                    label='Voix',
                    on_change=lambda e: self.controller.tts_engine.set_voice(e.value)
                ).classes('w-full mb-4').props('dark outlined')
            else:
                ui.label('Aucune voix détectée ou TTS non initialisé').classes('text-red-400 text-xs mb-4')
            
            # 2. Indexation Apps
            ui.label('Applications').classes('text-xs opacity-70')
            ui.label(f"Apps indexées : {len(self.controller.system_controller.app_paths) if self.controller.system_controller else 0}").classes('text-xs mb-2')
            
            def refresh_apps():
                ui.notify("Ré-indexation lancée...", type='info')
                # On lance l'indexation dans un thread pour ne pas bloquer
                import threading
                def run_index():
                    from utils.app_indexer import AppIndexer
                    indexer = AppIndexer()
                    apps = indexer.get_installed_apps(force_refresh=True)
                    
                    # Mise à jour du contrôleur via queue thread-safe si possible, ou direct (attention)
                    # Ici on le fait direct car c'est des dicts python (atomic operations mostly)
                    if self.controller.system_controller:
                        conf_apps = self.controller.backend_config.get('applications', {})
                        all_apps = apps.copy()
                        all_apps.update(conf_apps)
                        self.controller.system_controller.set_app_paths(all_apps)
                        if self.controller.intent_parser:
                            self.controller.intent_parser.app_paths = all_apps
                    
                    self.add_log_threadsafe(f"INDEXATION TERMINÉE: {len(apps)} APPS", "SYS")
                    self.run_threadsafe(lambda: ui.notify(f"Indexation terminée : {len(apps)} apps trouvées", type='positive'))
                    self.run_threadsafe(dialog.close)
                    
                threading.Thread(target=run_index, daemon=True).start()

            ui.button('Forcer Ré-indexation', on_click=refresh_apps, icon='refresh').props('outline').classes('w-full text-cyan-400 mb-4')
            
            # Footer
            with ui.row().classes('w-full justify-end'):
                ui.button('Fermer', on_click=dialog.close).props('flat text-color=white')
            
            dialog.open()

def build(brain=None):
    return JarvisUI(brain)
