#model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from ants.agents import AntAgent, NestAgent, SugarAgent, PheromoneAgent
from ants.config import FOOD_COUNT,FOOD_STACK_SIZE
import random

class AntColonyModel(Model):
    def __init__(self, N, width, height, food_count = FOOD_COUNT, stack_size = STACK_SIZE, nest_position = [1,1]):
        super().__init__()

        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=False) 
        self.schedule = RandomActivation(self)  # Exécution aléatoire des agents

        # Initialiser la grille des phéromones
        self.pheromone_grid = [[0 for _ in range(height)] for _ in range(width)]
        self.pheromone_agents = {}

        for x in range(width):
            for y in range(height):
                # Vérifie si un PheromoneAgent existe déjà (dans la grille et dans le dictionnaire)
                if (x, y) not in self.pheromone_agents :
                    
                    pheromone_agent = PheromoneAgent(f"pheromone_{x}_{y}", self)
                    self.grid.place_agent(pheromone_agent, (x, y))
                    self.schedule.add(pheromone_agent)
                    self.pheromone_agents[(x, y)] = pheromone_agent


        #Positionnement du nid
        self.nest = NestAgent("nest",self)
        self.nest_x = nest_position[0]
        self.nest_y = nest_position[1]
        self.grid.place_agent(self.nest,(self.nest_x,self.nest_y))


        #Positionnement du sucre
        for i in range(food_count):
            x = random.randint(1, self.grid.width - 1)
            y = random.randint(1, self.grid.height - 1)
            for j in range(stack_size):
                sugar = SugarAgent(f"sugar_{i}_{j}", self)
                self.grid.place_agent(sugar, (x, y))


        # Positionnement des fourmis
        for i in range(self.num_agents):
            x,y = nest_position[0], nest_position[1]
            ant = AntAgent(i, self)
            self.grid.place_agent(ant, (x, y))
            self.schedule.add(ant)

    def step(self):
        """Avancer la simulation d’un pas"""
        self.schedule.step()
        self.evaporate_pheromones()


    def evaporate_pheromones(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # ✅ Réduction de la concentration des phéromones
                self.pheromone_grid[x][y] *= 0.95

                # ✅ Mise à jour de l'agent PheromoneAgent associé
                if (x, y) in self.pheromone_agents:
                    self.pheromone_agents[(x, y)].intensity = self.pheromone_grid[x][y]
