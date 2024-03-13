import math


class Depot:
    def __init__(self, idName, x, y, readyTime, dueTime):
        self.idName = idName
        self.x = int(x)
        self.y = int(y)
        self.readyTime = int(readyTime)
        self.dueTime = int(dueTime)

    def __str__(self):
        return "Depot: " + self.idName + " x: " + str(self.x) + " y: " + str(self.y) + " ready time: " + str(self.readyTime) + " due time: " + str(self.dueTime)


class Client:
    def __init__(self, idName, x, y, readyTime, dueTime, demand, service):
        self.idName = idName
        self.x = int(x)
        self.y = int(y)
        self.readyTime = int(readyTime)
        self.dueTime = int(dueTime)
        self.demand = int(demand)
        self.service = int(service)

    def __str__(self):
        return "Client: " + self.idName + " x: " + str(self.x) + " y: " + str(self.y) + " ready time: " + str(self.readyTime) + " due time: " + str(self.dueTime) + " demand: " + str(self.demand) + " service: " + str(self.service)

class Camion:
    def __init__(self, max_capacity):
        self.max_capacity = int(max_capacity)
        self.liste_clients = []
        self.capacity = 0
        

    def add_client(self, client):
        self.liste_clients.append(client)
        self.capacity += client.demand

    def set_capacity(self, capacity):
        self.capacity = capacity

    # créer tous les trajets, chaque trajet est une liste avec en indice 0 le client de départ et en indice 1 le client d'arrivée
    # Excepté pour le dernier trajet qui est le retour au dépôt et le premier qui est le départ du dépôt
    def createTrajets(self, liste_clients, depot):
        trajets = []

        # Trajet du dépôt au premier client
        trajets.append([depot, self.liste_clients[0]])

        # Trajets entre les clients
        for i in range(len(self.liste_clients) - 1):
            trajets.append([self.liste_clients[i], self.liste_clients[i + 1]])



        # Trajet du dernier client au dépôt
        trajets.append([self.liste_clients[-1], depot])
        return trajets

    def calculer_distance_trajet(self, depot):
        distance = 0
        # Ajouter le calcul de la distance entre le dépôt et le premier client et entre le dernier client et le dépôt

        # Trajet du dépôt au premier client
        distance += self.calculer_distance(depot, self.liste_clients[0])
        for i in range(len(self.liste_clients) - 1):
            distance += self.calculer_distance(self.liste_clients[i], self.liste_clients[i + 1])
        distance += self.calculer_distance(self.liste_clients[-1], depot)
        return distance


    def __str__(self):
        return "Camion: " + str(self.max_capacity) + " capacity: " + str(self.capacity) + " liste_clients: " + str(self.liste_clients)

    def calculer_distance(self, client1, client2):
        return math.sqrt((client1.x - client2.x) ** 2 + (client1.y - client2.y) ** 2)

    def echanger_clients(self, i, j):
        temp = self.liste_clients[i]
        self.liste_clients[i] = self.liste_clients[j]
        self.liste_clients[j] = temp
        return self.liste_clients

    def copy(self):
        new_camion = self.__class__(self.max_capacity)
        new_camion.capacity = self.capacity
        new_camion.liste_clients = self.liste_clients[:]
        return new_camion
    

    def capacite_suffisante(self, liste_clients):
        capacite = 0
        for client in liste_clients:
            capacite += client.demand
        return capacite <= self.max_capacity



