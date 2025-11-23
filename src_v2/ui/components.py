from nicegui import ui
import random

class AudioVisualizer:
    def __init__(self):
        # Configuration ECharts pour un spectre audio futuriste
        self.chart = ui.echart({
            'backgroundColor': 'transparent',
            'grid': {
                'top': '5%',
                'bottom': '5%',
                'left': '0%',
                'right': '0%'
            },
            'xAxis': {
                'type': 'category',
                'show': False,
                'data': list(range(40)) # Plus de barres pour un effet spectre plus fin
            },
            'yAxis': {
                'type': 'value',
                'show': False,
                'min': 0,
                'max': 100
            },
            'series': [{
                'data': [5] * 40,
                'type': 'bar',
                'barWidth': '70%',
                'showBackground': False,
                'itemStyle': {
                    'color': {
                        'type': 'linear',
                        'x': 0, 'y': 0, 'x2': 0, 'y2': 1,
                        'colorStops': [
                            {'offset': 0, 'color': '#00f3ff'}, # Cyan Néon (Haut)
                            {'offset': 0.5, 'color': '#0066ff'}, # Bleu (Milieu)
                            {'offset': 1, 'color': 'rgba(0, 243, 255, 0.0)'} # Transparent (Bas)
                        ]
                    },
                    'borderRadius': [2, 2, 0, 0],
                    'shadowBlur': 10,
                    'shadowColor': '#00f3ff'
                },
                'animationDuration': 50, # Très rapide pour la réactivité
                'animationDurationUpdate': 50,
            }]
        }).classes('w-full h-32') # Un peu plus haut
        
    def update(self, level: float):
        """
        Met à jour le visualiseur avec un effet de spectre simulé (Mode Écoute).
        """
        # On simule un spectre complet à partir d'un seul niveau de volume
        base_val = min(100, max(2, level * 1000))
        
        new_data = []
        for i in range(40):
            # Simulation d'une courbe en cloche (Bell curve) pour le spectre
            # Le centre (i=20) est le plus haut
            dist_from_center = abs(i - 20)
            factor = max(0.1, 1.0 - (dist_from_center / 15))
            
            # Ajout de bruit aléatoire pour faire "vivant"
            noise = random.uniform(0.5, 1.5)
            
            val = base_val * factor * noise
            new_data.append(min(100, val))
            
        self.chart.options['series'][0]['data'] = new_data
        self.chart.update()

    def simulate_speaking(self):
        """
        Simule une activité vocale (Mode Parole).
        Génère une onde sinusoïdale mouvante ou aléatoire dynamique.
        """
        import math
        import time
        
        # On utilise le temps pour faire bouger l'onde
        t = time.time() * 10
        
        new_data = []
        for i in range(40):
            # Onde sinusoïdale complexe
            val = 50 + 40 * math.sin(i * 0.3 + t) * math.sin(i * 0.1 - t * 0.5)
            # Ajout de bruit
            val += random.uniform(-10, 10)
            new_data.append(max(5, min(100, val)))
            
        self.chart.options['series'][0]['data'] = new_data
        self.chart.update()
