

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

        print(trajets)
        for trajet in trajets:
            print(trajet[0].idName, trajet[1].idName)
        return trajets



    def __str__(self):
        return "Camion: " + str(self.max_capacity) + " capacity: " + str(self.capacity) + " liste_clients: " + str(self.liste_clients)



