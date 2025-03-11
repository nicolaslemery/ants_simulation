#visualization.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Ajoute le chemin actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le parent

from ants.model import AntColonyModel
from ants.agents import AntAgent, NestAgent, SugarAgent, PheromoneAgent
from ants.config import NUM_ANTS, GRID_WIDTH, GRID_HEIGHT

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    """Définit l'apparence des agents """

    if isinstance(agent, PheromoneAgent):
        pheromone_color = get_pheromone_color(agent.intensity)
        return {
            "Shape": "rect",
            "Color": pheromone_color,
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1
        }

    if isinstance(agent, NestAgent):
        return {
            "Shape": "rect",
            "Color": "brown",
            "Filled": "true",
            "Layer": 1,
            "w": 1,
            "h": 1,
            "text": str(agent.sugar_collected),
            "text_color": "white"
        }

    if isinstance(agent, SugarAgent):
        return {
            "Shape": "rect",
            "Color": "green",
            "Filled": "true",
            "Layer": 1,
            "w": 0.4,
            "h": 0.4
        }

    if isinstance(agent, AntAgent):
        return {
            "Shape": "circle",
            "Color": "blue" if agent.has_food else "black",
            "Filled": "true",
            "Layer": 2, 
            "r": 0.5
        }

    return None 

#TODO: remplacer cette fonction par un dico
def get_pheromone_color(value, max_value=10):
    """Convertit une concentration de phéromones en couleur entre jaune et rouge."""
    value = min(value, max_value)  # ✅ Évite de dépasser la concentration maximale
    intensity = int((value / max_value) * 255)  # ✅ Convertit en échelle de 0 à 255
    return f"rgb(255, {255 - intensity}, 0)"  # ✅ Dégrade du jaune vers le rouge


# Création de l'espace
grid = CanvasGrid(agent_portrayal, GRID_WIDTH, GRID_HEIGHT, 500, 500)

# Création du serveur Mesa
server = ModularServer(
    AntColonyModel,
    [grid],
    "Colonie de Fourmis de Nicolas",
    {"N": NUM_ANTS, "width": GRID_WIDTH, "height": GRID_HEIGHT}
)

server.launch()
print("Début de la simulation des fourmis -> http://127.0.0.1:8521")

