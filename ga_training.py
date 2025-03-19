import copy
import torch

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Ajoute le chemin actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Ajoute le parent

from ants.antNet import AntNet
from ants.model import AntColonyModel
from ants.config import NUM_ANTS,GRID_WIDTH,GRID_HEIGHT,STEPS
from ants.agents import AntAgent

POPULATION_SIZE = 100

base_model = AntNet(input_size=5, hidden_size=16, output_size=4)
base_model.load_state_dict(torch.load("best_antnet_ga.pth"))
base_model.eval()

def create_population_from_base(base_model, population_size=POPULATION_SIZE, initial_mutation_rate=0.1):
    population = []
    for _ in range(population_size):
        # Clone ton modèle existant
        new_model = copy.deepcopy(base_model)
        # Mutation initiale pour générer diversité autour du modèle existant
        mutate(new_model, mutation_rate=initial_mutation_rate)
        population.append(new_model)
    return population


def create_population():
    return [AntNet() for _ in range(POPULATION_SIZE)]

def evaluate_network(network):
    simulation = AntColonyModel(N=NUM_ANTS, width=GRID_WIDTH, height=GRID_HEIGHT)
    total_reward = 0
    for step in range(STEPS):
        simulation.step()
        for agent in simulation.schedule.agents:
            if isinstance(agent, AntAgent):
                agent.nn_model = network
                state = agent.state.unsqueeze(0)
                with torch.no_grad():
                    action = torch.argmax(network(state)).item()
                agent.execute_action(action)
                reward = agent.calculate_reward()
                total_reward += reward
    return total_reward

def select_top_networks(population, scores, num_top=5):
    sorted_pop = [net for _, net in sorted(zip(scores, population), key=lambda x: x[0], reverse=True)]
    return sorted_pop[:num_top]

def crossover(parent1, parent2):
    child = AntNet()
    child_state_dict = child.state_dict()
    p1_dict = parent1.state_dict()
    p2_dict = parent2.state_dict()

    for key in child_state_dict.keys():
        child_state_dict[key] = (p1_dict[key] + p2_dict[key]) / 2
    child.load_state_dict(child_state_dict)
    return child

def mutate(network, mutation_rate=0.1):
    for param in network.parameters():
        param.data += mutation_rate * torch.randn_like(param.data)

def create_next_generation(top_networks, population_size=POPULATION_SIZE):
    new_population = []
    
    # Élites (on garde les meilleurs sans modification)
    new_population.extend(top_networks)

    # Croisement + mutation pour compléter la population
    while len(new_population) < population_size:
        parent1, parent2 = torch.randperm(len(top_networks))[:2]
        child = crossover(top_networks[parent1], top_networks[parent2])
        mutate(child, mutation_rate=0.05)
        new_population.append(child)

    return new_population

GENERATIONS = 20

#population = create_population_from_base(base_model)
population = create_population()

# Initialiser le meilleur réseau global
best_network_ever = None
best_score_ever = float('-inf')  # initialisé à -infini pour être sûr d'être dépassé rapidement

for generation in range(GENERATIONS):
    print(f"\n🔄 Génération {generation}")

    # Évaluer chaque réseau
    scores = [evaluate_network(network) for network in population]

    # Afficher la meilleure fitness de la génération actuelle
    generation_best_score = max(scores)
    generation_best_network = population[scores.index(generation_best_score)]
    print(f"Meilleur score cette génération : {generation_best_score}")

    # Vérifier et mettre à jour le meilleur réseau global
    if generation_best_score > best_score_ever:
        best_score_ever = generation_best_score
        best_network_ever = copy.deepcopy(generation_best_network)
        print(f"🏆 Nouveau meilleur réseau trouvé à la génération {generation} avec un score de {best_score_ever}")

    # Sélectionner les meilleurs
    top_networks = select_top_networks(population, scores, num_top=5)

    # Créer génération suivante
    population = create_next_generation(top_networks, population_size=POPULATION_SIZE)

# Sauvegarder le meilleur réseau global obtenu (sur toutes les générations)
torch.save(best_network_ever.state_dict(), "best_antnet_ga_global.pth")
print("✅ Meilleur modèle global sauvegardé : best_antnet_ga_global.pth")
