#agents.py
import random
from mesa import Agent

from ants.config import GRID_WIDTH



class AntAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.has_food = False 
        self.current_position_pheromone = 0.0
        self.distance_to_nest = 0
        self.sugars_collected = 0

    def step(self):
        self.distance_to_nest = self.distance_L1_to_nest()
        self.current_position_pheromone = self.model.pheromone_grid[self.pos[0]][self.pos[1]]

        self.move_random()

        if self.has_food:
            # Dépose les phéromones 
            max_range_nest = GRID_WIDTH * 2
            max_pheromone_intensity_ant = 0.2 # L'intensité max de phéromone déposée en une fois
            intensity = max(0, (max_range_nest - self.distance_L1_to_nest())*(max_pheromone_intensity_ant/max_range_nest))
            new_pheromone_value = min ((self.model.pheromone_grid[self.pos[0]][self.pos[1]] + intensity), 1)
            
            self.update_pheromone_grid(new_pheromone_value)
            self.model.pheromone_agents[(self.pos[0], self.pos[1])].intensity = self.model.pheromone_grid[self.pos[0]][self.pos[1]]
            
            # Dépose automatiquement le sucre au nid 
            if self.pos == (self.model.nest_x, self.model.nest_y):
                self.has_food = False
                self.sugars_collected += 1
                self.model.nest.add_sugar()

        #Regarde si y'a un sucre par terre
        else:
            self.look_and_take_sugar()
        

            
    def update_pheromone_grid(self,value):
        self.model.pheromone_grid[self.pos[0]][self.pos[1]] = value

    def move_random(self):
        """Déplacement sur une grille discrète en évitant les bords."""
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        dx, dy = random.choice(possible_moves)
        
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Check si la nouvelle position est dans les limites de la grille
        if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
            self.model.grid.move_agent(self, (new_x, new_y))
        else: # Marche arrière
            new_x = new_x - 2*dx
            new_y = new_y - 2*dy
            self.model.grid.move_agent(self, (new_x, new_y))
    
    def look_and_take_sugar(self):
        """Regarde par terre si il y a un sucre, le prend si elle n'est pas chargée"""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, SugarAgent) and not self.has_food :
                self.has_food = True  
                self.model.grid.remove_agent(obj)  
                break 

    def distance_L1_to_nest(self):
        """Distance L1 (Manhattan) entre la fourmi et le nid."""
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
