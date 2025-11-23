from nicegui import ui
import random

class AudioVisualizer:
    def __init__(self):
        # Configuration ECharts pour un spectre audio futuriste
        self.chart = ui.echart({
            'backgroundColor': 'transparent',
            'grid': {
                'top': '10%',
                'bottom': '10%',
                'left': '0%',
                'right': '0%'
            },
            'xAxis': {
                'type': 'category',
                'show': False,
                'data': list(range(30)) # Plus de barres pour un effet spectre
            },
            'yAxis': {
                'type': 'value',
                'show': False,
                'min': 0,
                'max': 100
            },
            'series': [{
                'data': [5] * 30, # Valeur minimale pour voir les barres
                'type': 'bar',
                'barWidth': '60%',
                'showBackground': False,
                'itemStyle': {
                    'color': {
                        'type': 'linear',
                        'x': 0, 'y': 0, 'x2': 0, 'y2': 1,
                        'colorStops': [
                            {'offset': 0, 'color': '#00f3ff'}, # Cyan Néon (Haut)
                            {'offset': 1, 'color': 'rgba(0, 243, 255, 0.1)'} # Transparent (Bas)
                        ]
                    },
                    'borderRadius': [2, 2, 0, 0],
                    'shadowBlur': 5,
                    'shadowColor': '#00f3ff'
                },
                'animationDuration': 50, # Très rapide pour la réactivité
                'animationDurationUpdate': 50,
            }]
        }).classes('w-full h-24')
        
    def update(self, level: float):
        """
        Met à jour le visualiseur avec un effet de spectre simulé.
        """
        # On simule un spectre complet à partir d'un seul niveau de volume
        # Les basses (gauche) et hautes (droite) fréquences sont moins fortes que les médiums
        base_val = min(100, max(5, level * 1000))
        
        new_data = []
        for i in range(30):
            # Simulation d'une courbe en cloche (Bell curve) pour le spectre
            # Le centre (i=15) est le plus haut
            dist_from_center = abs(i - 15)
            factor = max(0.2, 1.0 - (dist_from_center / 15))
            
            # Ajout de bruit aléatoire pour faire "vivant"
            noise = random.uniform(0.8, 1.2)
            
            val = base_val * factor * noise
            new_data.append(min(100, val))
            
        self.chart.options['series'][0]['data'] = new_data
        self.chart.update()
