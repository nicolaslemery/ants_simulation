#agents.py
import random
import torch
from mesa import Agent

from ants.config import GRID_WIDTH, GRID_HEIGHT, DEBUG_FLAG
from ants.antNet import AntNet

# Charger le modèle entraîné
nn_model = AntNet(input_size=5, hidden_size=16, output_size=4)
nn_model.load_state_dict(torch.load("best_antnet_ga_global.pth"))
nn_model.eval()



class AntAgent(Agent):
    def __init__(self, unique_id, model, nn_model = nn_model):
        super().__init__(unique_id, model)
        self.has_food = False 
        self.current_position_pheromone = 0.0
        self.distance_to_nest = 0
        self.sugars_collected = 0
        self.last_action = 0
        self.state = torch.tensor
        self.taken_food_flag = False
        self.dropped_food_flag = False
        self.bump_wall_flag = False


        if nn_model == None:
            self.nn_model = AntNet()
        else:
            self.nn_model = nn_model

    def step(self): #TODO remplacer le code poubelle par des fonctions -> release_pheromones(), get_state()
        self.get_state()
        self.bump_wall_flag = False
        self.distance_to_nest = self.distance_L1_to_nest()
        self.current_position_pheromone = self.model.pheromone_grid[self.pos[0]][self.pos[1]]

        if DEBUG_FLAG:
            print(f"Fourmi {self.unique_id} : \n    Distance au nid : {self.distance_to_nest} \n    Taux de phéromones : {self.current_position_pheromone}\n Chargé en sucre : {self.has_food}")
        
        #self.move_with_nn()

        action = 0
        with torch.no_grad():
            output = self.nn_model(self.state.unsqueeze(0))
        
        # Choisir l'action avec le score maximal
        action = torch.argmax(output, dim=1).item()
        #print(action)
        self.last_action = action
        self.execute_action(action)

        if self.has_food:
            self.taken_food_flag = False
            
            # Dépose les phéromones 
            max_range_nest = GRID_WIDTH * 2
            max_pheromone_intensity_ant = 0.2 # L'intensité max de phéromone déposée en une fois
            intensity = max(0, (max_range_nest - self.distance_L1_to_nest())*(max_pheromone_intensity_ant/max_range_nest))
            new_pheromone_value = min ((self.model.pheromone_grid[self.pos[0]][self.pos[1]] + intensity), 1)
            
            self.update_pheromone_grid(new_pheromone_value)
            self.model.pheromone_agents[(self.pos[0], self.pos[1])].intensity = self.model.pheromone_grid[self.pos[0]][self.pos[1]]
            
            # Dépose automatiquement le sucre au nid 
            if self.pos == (self.model.nest_x, self.model.nest_y):
                self.drop_sugar()
                

        #Regarde si y'a un sucre par terre
        else:
            self.dropped_food_flag = False
            self.look_and_take_sugar()
    
    def get_state(self):
        max_distance = GRID_WIDTH + GRID_HEIGHT
        normalized_distance_to_nest = self.distance_to_nest/max_distance
        sugar_flag = 1.0 if self.has_food else 0.0 

        input_vector = torch.tensor([self.pos[0],self.pos[1],normalized_distance_to_nest,sugar_flag,self.current_position_pheromone],dtype = torch.float32)
        self.state = input_vector
    
    def drop_sugar(self):
        self.has_food = False
        self.sugars_collected += 1
        self.model.nest.add_sugar()
        self.dropped_food_flag = True

            
    def update_pheromone_grid(self,value):
        self.model.pheromone_grid[self.pos[0]][self.pos[1]] = value

    def move_with_nn(self):
        # Get state
        max_distance = GRID_WIDTH + GRID_HEIGHT
        normalized_distance_to_nest = self.distance_to_nest/max_distance
        sugar_flag = 1.0 if self.has_food else 0.0 

        # Vecteur d'entrée
        input_vector = torch.tensor([self.pos[0],self.pos[1],normalized_distance_to_nest,sugar_flag,self.current_position_pheromone],dtype = torch.float32)
        self.state = input_vector
        input_vector = input_vector.unsqueeze(0)

        # Obtenir les scores pour chaque direction
        with torch.no_grad():
            output = self.nn_model(input_vector)
        
        # Choisir l'action avec le score maximal
        action = torch.argmax(output, dim=1).item()
        self.last_action = action
        
        # Mapping de l'action aux directions : 0=haut, 1=bas, 2=gauche, 3=droite
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = directions[action]
        
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy
        
        # Vérifier que la nouvelle position est dans les limites de la grille
        if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
            self.model.grid.move_agent(self, (new_x, new_y))
        else:
            if DEBUG_FLAG:
                print("Se cogne au bord")
            self.bump_wall_flag = True

    def execute_action(self,action):
        #4 actions possibles 0=haut, 1=bas, 2=gauche, 3=droite
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = directions[action]
        
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy
        
        # Vérifier que la nouvelle position est dans les limites de la grille
        if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
            self.model.grid.move_agent(self, (new_x, new_y))
        else:
            if DEBUG_FLAG:
                print("Se cogne au bord")
            self.bump_wall_flag = True


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
                self.taken_food_flag = True
                break 

    def distance_L1_to_nest(self):
        """Distance L1 (Manhattan) entre la fourmi et le nid."""
        return abs(self.pos[0] - self.model.nest_x) + abs(self.pos[1] - self.model.nest_y)
    
    def calculate_reward(self):
        reward = 0
        if self.taken_food_flag :
            reward += 10
        if self.dropped_food_flag : 
            reward += 20
        if self.bump_wall_flag:
            reward -= 1

        if self.has_food:
            reward -= 1/100 * self.distance_to_nest
        else:
            reward += 1/100 * self.distance_to_nest

        reward -= 1/10

        return reward
        

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
