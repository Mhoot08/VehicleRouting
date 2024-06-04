from classes import Depot
from classes import Client
from classes import Camion


class VehicleRouting:

    depots = None
    CAPACITY = 0
    camions = None
    clients = None
    depots = None

    def __init__(self):
        # Read file
        self.camions = []
        self.depots = []
        self.clients = []
        self.read_file('data/data101.vrp')

    def read_file(self, file_path):
        with open(file_path, 'r') as file:
            # Read vrp file
            file_content = file.read()
            # Split file content by lines
            file_lines = file_content.split('\n')
            for line in file_lines:
                line_values = line.split()
                if line.startswith('MAX_QUANTITY'):
                    print('Max quantity')
                    print(line_values[1])
                    self.CAPACITY = int(line_values[1])
                if line.startswith("DATA_DEPOTS"):
                    # On prend la prochaine ligne
                    line = file_lines[file_lines.index(line) + 1]
                    # Parcours entre les espaces
                    line_values = line.split()
                    # On ajoute le depot
                    self.depots.append(Depot(line_values[0], line_values[1], line_values[2], line_values[3], line_values[4]))
                if line.startswith("DATA_CLIENTS"):
                    for i in range (file_lines.index(line) + 1, len(file_lines)):
                        line = file_lines[i]
                        line_values = line.split()
                        if line_values:
                            self.clients.append(Client(line_values[0], line_values[1], line_values[2], line_values[3], line_values[4], line_values[5], line_values[6]))
        # garder que les 30 premiers clients
        self.clients = self.clients[:30]

        # Afficher la capacité total des clients
        print(self.getCapacityClient())


    def getCapacityClient(self):
        # Parcours les clients et additionne leur demande
        capacity = 0
        for client in self.clients:
            capacity += client.demand
        print("Capacity: " + str(capacity))
        return capacity

    def getNbMinVehicle(self):
        return int(self.getCapacityClient() / self.CAPACITY) + 1
    
    def calculer_distance_total(self):
        distance = 0
        for camion in self.camions:
            distance += camion.calculer_distance_trajet(self.depots[0])
        return distance
    
    def copy(self):
        new_solution = self.__class__()
        new_solution.camions = [camion.copy() for camion in self.camions]
        new_solution.clients = self.clients
        new_solution.depots = self.depots
        new_solution.CAPACITY = self.CAPACITY
        return new_solution

    def __eq__(self, other):
        return self.camions == other.camions and self.clients == other.clients


