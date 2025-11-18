"""
Interface graphique principale pour Jarvis Commander.
Utilise PySide6/Qt pour une interface moderne et fluide.
"""

import logging
from datetime import datetime
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget,
    QGroupBox, QSpinBox, QDoubleSpinBox, QComboBox,
    QLineEdit, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, Slot
from PySide6.QtGui import QFont, QPalette, QColor

logger = logging.getLogger(__name__)


class JarvisMainWindow(QMainWindow):
    """Fenêtre principale de Jarvis Commander."""
    
    # Signaux personnalisés
    log_signal = Signal(str, str)  # (message, niveau)
    status_signal = Signal(str)  # Changement d'état
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Connecter les signaux
        self.log_signal.connect(self._add_log_entry)
        self.status_signal.connect(self._update_status)
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("Jarvis Commander")
        self.setGeometry(100, 100, 900, 700)
        
        # Appliquer le thème sombre
        self.apply_dark_theme()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # === EN-TÊTE ===
        header = self._create_header()
        main_layout.addWidget(header)
        
        # === INDICATEUR D'ÉTAT ===
        status_group = self._create_status_indicator()
        main_layout.addWidget(status_group)
        
        # === ONGLETS ===
        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 10))
        
        # Onglet Journal
        log_tab = self._create_log_tab()
        tabs.addTab(log_tab, "📋 Journal")
        
        # Onglet Paramètres
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "⚙️ Paramètres")
        
        main_layout.addWidget(tabs, stretch=1)
        
        # === BOUTONS DE CONTRÔLE ===
        control_layout = self._create_control_buttons()
        main_layout.addLayout(control_layout)
        
        logger.info("Interface graphique initialisée")
    
    def _create_header(self) -> QWidget:
        """Crée l'en-tête de l'application."""
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre
        title = QLabel("🤖 JARVIS COMMANDER")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Assistant vocal intelligent pour Windows")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)
        
        return header
    
    def _create_status_indicator(self) -> QGroupBox:
        """Crée l'indicateur d'état."""
        group = QGroupBox("État du système")
        group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        layout = QHBoxLayout(group)
        
        # Label d'état
        self.status_label = QLabel("⚪ Initialisation...")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_label)
        
        return group
    
    def _create_log_tab(self) -> QWidget:
        """Crée l'onglet du journal."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Zone de texte pour les logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        # Bouton pour effacer les logs
        clear_btn = QPushButton("🗑️ Effacer le journal")
        clear_btn.clicked.connect(self.log_text.clear)
        clear_btn.setStyleSheet(self._get_button_style("#555"))
        layout.addWidget(clear_btn)
        
        return tab
    
    def _create_settings_tab(self) -> QWidget:
        """Crée l'onglet des paramètres."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)
        
        # === Paramètres Wake Word ===
        ww_group = QGroupBox("Wake Word (Porcupine)")
        ww_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        ww_layout = QVBoxLayout(ww_group)
        
        # Sensibilité
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(QLabel("Sensibilité (0.0 - 1.0):"))
        self.sensitivity_spin = QDoubleSpinBox()
        self.sensitivity_spin.setRange(0.0, 1.0)
        self.sensitivity_spin.setSingleStep(0.1)
        self.sensitivity_spin.setValue(0.7)
        sens_layout.addWidget(self.sensitivity_spin)
        sens_layout.addStretch()
        ww_layout.addLayout(sens_layout)
        
        layout.addWidget(ww_group)
        
        # === Paramètres TTS ===
        tts_group = QGroupBox("Synthèse vocale (TTS)")
        tts_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        tts_layout = QVBoxLayout(tts_group)
        
        # Vitesse
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Vitesse (mots/min):"))
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(100, 300)
        self.rate_spin.setValue(180)
        rate_layout.addWidget(self.rate_spin)
        rate_layout.addStretch()
        tts_layout.addLayout(rate_layout)
        
        # Volume
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume (0.0 - 1.0):"))
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.0, 1.0)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(0.9)
        vol_layout.addWidget(self.volume_spin)
        vol_layout.addStretch()
        tts_layout.addLayout(vol_layout)
        
        layout.addWidget(tts_group)
        
        # === Paramètres STT ===
        stt_group = QGroupBox("Reconnaissance vocale (STT)")
        stt_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        stt_layout = QVBoxLayout(stt_group)
        
        # Modèle Whisper
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Modèle Whisper:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText("small")
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        stt_layout.addLayout(model_layout)
        
        layout.addWidget(stt_group)
        
        # Bouton Appliquer
        apply_btn = QPushButton("✅ Appliquer les paramètres")
        apply_btn.clicked.connect(self._apply_settings)
        apply_btn.setStyleSheet(self._get_button_style("#2d7d46"))
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
        return tab
    
    def _create_control_buttons(self) -> QHBoxLayout:
        """Crée les boutons de contrôle."""
        layout = QHBoxLayout()
        
        # Bouton Activer/Désactiver
        self.toggle_btn = QPushButton("🎤 Activer Jarvis")
        self.toggle_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.toggle_btn.setMinimumHeight(50)
        self.toggle_btn.setStyleSheet(self._get_button_style("#2d7d46"))
        layout.addWidget(self.toggle_btn)
        
        # Bouton Quitter
        quit_btn = QPushButton("❌ Quitter")
        quit_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        quit_btn.setMinimumHeight(50)
        quit_btn.setStyleSheet(self._get_button_style("#8b2c2c"))
        quit_btn.clicked.connect(self._confirm_quit)
        layout.addWidget(quit_btn)
        
        return layout
    
    def apply_dark_theme(self):
        """Applique le thème sombre à l'application."""
        dark_palette = QPalette()
        
        # Couleurs de base
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(212, 212, 212))
        dark_palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
        dark_palette.setColor(QPalette.Text, QColor(212, 212, 212))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        QApplication.instance().setPalette(dark_palette)
        
        # Style global
        QApplication.instance().setStyleSheet("""
            QGroupBox {
                border: 2px solid #3e3e3e;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e3e;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #2d2d2d;
                border: 1px solid #3e3e3e;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3e3e3e;
            }
        """)
    
    def _get_button_style(self, bg_color: str) -> str:
        """Génère le style pour un bouton."""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(bg_color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color)};
            }}
        """
    
    def _lighten_color(self, hex_color: str) -> str:
        """Éclaircit une couleur hexadécimale."""
        # Simple éclaircissement
        return hex_color  # Pour simplifier, retourne la même couleur
    
    def _darken_color(self, hex_color: str) -> str:
        """Assombrit une couleur hexadécimale."""
        return hex_color  # Pour simplifier, retourne la même couleur
    
    @Slot(str, str)
    def _add_log_entry(self, message: str, level: str):
        """
        Ajoute une entrée au journal (slot thread-safe).
        
        Args:
            message: Message à logger
            level: Niveau de log (INFO, WARNING, ERROR, etc.)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Couleur selon le niveau
        color_map = {
            'DEBUG': '#888',
            'INFO': '#4ec9b0',
            'WARNING': '#ce9178',
            'ERROR': '#f48771',
            'CRITICAL': '#ff0000'
        }
        color = color_map.get(level, '#d4d4d4')
        
        # Formater le message
        formatted = f'<span style="color: #666;">[{timestamp}]</span> '
        formatted += f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
        formatted += f'<span style="color: #d4d4d4;">{message}</span>'
        
        self.log_text.append(formatted)
        
        # Scroller automatiquement vers le bas
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @Slot(str)
    def _update_status(self, status: str):
        """
        Met à jour l'indicateur d'état (slot thread-safe).
        
        Args:
            status: Nouveau statut
        """
        # Mapping statut -> emoji + couleur
        status_map = {
            'idle': ('⚪', 'Veille - En attente du wake word', '#888'),
            'listening': ('🔵', 'Écoute passive...', '#4ec9b0'),
            'recording': ('🔴', 'Enregistrement en cours...', '#f48771'),
            'processing': ('🟡', 'Traitement de la commande...', '#dcdcaa'),
            'executing': ('🟢', 'Exécution...', '#4ec9b0'),
            'error': ('❌', 'Erreur', '#ff0000'),
            'disabled': ('⚫', 'Désactivé', '#555'),
        }
        
        emoji, text, color = status_map.get(status, ('⚪', status, '#888'))
        
        self.status_label.setText(f"{emoji} {text}")
        self.status_label.setStyleSheet(f"color: {color};")
    
    @Slot()
    def _apply_settings(self):
        """Applique les paramètres modifiés."""
        # Cette méthode sera connectée au contrôleur principal
        QMessageBox.information(
            self,
            "Paramètres",
            "Les paramètres seront appliqués au redémarrage de Jarvis."
        )
    
    @Slot()
    def _confirm_quit(self):
        """Demande confirmation avant de quitter."""
        reply = QMessageBox.question(
            self,
            "Quitter Jarvis",
            "Êtes-vous sûr de vouloir quitter Jarvis Commander ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
    
    def add_log(self, message: str, level: str = "INFO"):
        """
        Ajoute un message au journal (thread-safe).
        
        Args:
            message: Message à logger
            level: Niveau de log
        """
        self.log_signal.emit(message, level)
    
    def set_status(self, status: str):
        """
        Modifie le statut affiché (thread-safe).
        
        Args:
            status: Nouveau statut
        """
        self.status_signal.emit(status)
    
    def get_settings(self) -> dict:
        """
        Récupère les paramètres de l'interface.
        
        Returns:
            Dictionnaire des paramètres
        """
        return {
            'wake_word': {
                'sensitivity': self.sensitivity_spin.value()
            },
            'tts': {
                'rate': self.rate_spin.value(),
                'volume': self.volume_spin.value()
            },
            'stt': {
                'model': self.model_combo.currentText()
            }
        }
