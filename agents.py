#agents.py
import random
from mesa import Agent


class AntAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.has_food = False 

    def step(self):
        """Action exécutée à chaque pas de simulation"""
        self.move()

        # Vérifier si la fourmi est au nid pour y déposer le sucre
        if self.pos == (self.model.nest_x, self.model.nest_y) and self.has_food:
            self.has_food = False  
            self.model.nest.add_sugar() 

        if self.has_food:
            intensity = max(1, 10 - self.distance_to_nest())  # ✅ Intensité décroissante avec la distance
            self.model.pheromone_grid[self.pos[0]][self.pos[1]] += intensity
            self.model.pheromone_agents[(self.pos[0], self.pos[1])].intensity = self.model.pheromone_grid[self.pos[0]][self.pos[1]]

        else:
            #Regarde si y'a un sucre par terre
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            for obj in cell_contents:
                if isinstance(obj, SugarAgent) :
                    self.has_food = True  
                    self.model.grid.remove_agent(obj)  
                    break 

    def move(self):
        """Déplacement sur une grille discrète en évitant les bords."""
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Déplacements en haut, bas, gauche, droite
        dx, dy = random.choice(possible_moves)
        
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Vérifier que la nouvelle position est dans les limites de la grille
        if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
            self.model.grid.move_agent(self, (new_x, new_y))

    def search_food(self):
        """Chercher de la nourriture """

    def return_to_nest(self):
        """Retourner au nid après avoir trouvé de la nourriture"""
        self.has_food = False  # Dépose la nourriture au nid

    def distance_to_nest(self):
        """Calcule la distance L1 (Manhattan) entre la fourmi et le nid."""
        return abs(self.pos[0] - self.model.nest_x) + abs(self.pos[1] - self.model.nest_y)
        
class PheromoneAgent(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model) 
        self.intensity = 0

    def step(self):
        """Mise à jour de l'intensité en fonction du pheromone_grid du modèle"""
        x,y = self.pos
        self.intensity = self.model.pheromone_grid[x][y]



class NestAgent(Agent):
    """Représente le nid au centre de la grille."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sugar_collected = 0

    def add_sugar(self):
        self.sugar_collected += 1


class SugarAgent(Agent):
    """Représente une pile de sucre placée sur la grille."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
