#run.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Ajoute le chemin actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le parent

from ants.model import AntColonyModel
from ants.config import NUM_ANTS, GRID_WIDTH, GRID_HEIGHT, STEPS



# Créer le modèle
model = AntColonyModel(NUM_ANTS, GRID_WIDTH, GRID_HEIGHT)

# Lancer la simulation
for i in range(STEPS):
    model.step()
    print(f"Step {i+1} completed")

print("Simulation terminée.")
