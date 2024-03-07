import random

from classes import Camion


def generer_solution_aleatoire(VehicleRouting):
    clients = VehicleRouting.clients
    max_capacity = VehicleRouting.CAPACITY
    solution = []

    # On mélange les clients
    random.shuffle(clients)

    camion = Camion(max_capacity)  # Créer un nouveau camion avec la capacité maximale

    for client in clients:
        if camion.capacity <= client.demand:
            camion.add_client(client)
        else:
            solution.append(camion)
            camion = Camion(max_capacity)
            camion.add_client(client)

    solution.append(camion)

    return solution








