import torch
import torch.optim as optim

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Ajoute le chemin actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le parent

from ants.model import AntColonyModel
from ants.agents import AntAgent
from ants.antNet import AntNet
from ants.config import NUM_ANTS, GRID_WIDTH, GRID_HEIGHT, STEPS

# Paramètres d'entraînement
num_episodes = 100
learning_rate = 0.001

# Supposons que tous vos agents partagent le même réseau pour simplifier
shared_nn_model = AntNet()
optimizer = optim.Adam(shared_nn_model.parameters(), lr=learning_rate)

for episode in range(num_episodes):
    simulation = AntColonyModel(N=NUM_ANTS, width=GRID_WIDTH, height=GRID_HEIGHT)
    
    episode_transitions = []  # pour stocker (state, action, reward)
    done = False
    total_reward = 0

    # Exécuter un épisode complet (par exemple, un nombre fixe de steps)
    for step in range(STEPS):
        simulation.step()  # L'agent effectue son step, interagit avec l'environnement
        
        # Pour chaque agent, récupérer les informations pertinentes
        for agent in simulation.schedule.agents:
            if isinstance(agent, AntAgent):
                state = agent.state
                action = agent.last_action  # par exemple, 0,1,2 ou 3
                reward = agent.calculate_reward()
                print("reward = " , reward)
                total_reward += reward
                
                episode_transitions.append((state, action, reward))
        
    # Calculer la perte de Policy Gradient
    # On suppose ici une approche simple où on considère la somme des récompenses comme "retour"
    # et on maximise la probabilité des actions ayant donné lieu à de bonnes récompenses.
    loss = 0
    for state, action, reward in episode_transitions:
        state = state.unsqueeze(0)  # dimension batch
        output = shared_nn_model(state)
        # Calcul de la log-probabilité de l'action choisie
        log_prob = torch.log_softmax(output, dim=1)[0, action]
        loss += -log_prob * reward  # on minimise l'opposé de la récompense pondérée par la probabilité

    # Mise à jour du réseau
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    print(f"Episode {episode} - Total reward: {total_reward}")

torch.save(shared_nn_model.state_dict(), "antnet_weights.pth")
print("✅ Modèle sauvegardé : antnet_weights.pth")