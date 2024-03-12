import random
import math

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

def generer_solution_aleatoire_opti(VehicleRouting):
    clients = VehicleRouting.clients
    max_capacity = VehicleRouting.CAPACITY
    solution = []

    # On mélange les clients
    random.shuffle(clients)

    camion = Camion(max_capacity)  # Créer un nouveau camion avec la capacité maximale

    for client in clients:
        if camion.capacity + client.demand <= max_capacity:
            camion.add_client(client)
        else:
            solution.append(camion)
            camion = Camion(max_capacity)
            camion.add_client(client)

    solution.append(camion)

    return solution

def exchange_intra(camions):
    # On échange deux clients dans un même camion
    for camion in camions:
        if len(camion.liste_clients) > 2:
            # On prend deux clients aléatoirement mais différents

            client1 = random.choice(camion.liste_clients)
            client2 = random.choice(camion.liste_clients)
            while client1 == client2:
                client2 = random.choice(camion.liste_clients)

            # On échange les clients
            index1 = camion.liste_clients.index(client1)
            index2 = camion.liste_clients.index(client2)

            camion.liste_clients[index1] = client2
            camion.liste_clients[index2] = client1

    return camions

"""
@:param camions: liste de 2 tournées (camions) qui ont plus de 2 clients
@:return camions: liste de 2 tournées (camions) qui ont plus de 2 clients
"""
def exchange_extra(tournees_a_permuter):
    # On échange un client d'un camion avec un autre client d'un autre camion en vérifiant que la capacité est respectée
    if len(tournees_a_permuter) != 2:
        return

    camion1 = tournees_a_permuter[0]
    camion2 = tournees_a_permuter[1]

    # On prend un client aléatoire dans chaque camion
    client1 = random.choice(camion1.liste_clients)
    client2 = random.choice(camion2.liste_clients)

    # On vérifie que la capacité est respectée
    if camion1.capacity - client1.demand + client2.demand <= camion1.max_capacity and camion2.capacity - client2.demand + client1.demand <= camion2.max_capacity:
        # On échange les clients
        index1 = camion1.liste_clients.index(client1)
        index2 = camion2.liste_clients.index(client2)

        camion1.liste_clients[index1] = client2
        camion2.liste_clients[index2] = client1

    tournees = [camion1, camion2]

    return tournees

def opt_2(camion):
    voisins = []

    if len(camion.liste_clients) <= 3:
        return voisins

    for i in range(1, len(camion.liste_clients) - 2):
        for j in range(i + 1, len(camion.liste_clients) - 1):
            # Crée un voisin en appliquant l'opérateur 2-opt
            voisin = Camion(camion.max_capacity)
            voisin.liste_clients = camion.liste_clients[:i] + camion.liste_clients[i:j+1][::-1] + camion.liste_clients[j+1:]
            voisins.append(voisin)

    return voisins


def get_voisins(solution):
    all_voisins = opt_2(solution)
    return all_voisins


def recuit_simule(solution_initiale, temperature_initiale, alpha, nombre_iterations):
    solution_actuelle = solution_initiale
    meilleure_solution = solution_initiale
    temperature = temperature_initiale

    for i in range(nombre_iterations):
        voisins = get_voisins(solution_actuelle)
        voisin_choisi = random.choice(voisins)

        delta_distance = voisin_choisi.calculer_distance_trajet() - solution_actuelle.calculer_distance_trajet()

        if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
            solution_actuelle = voisin_choisi

        if solution_actuelle.calculer_distance_trajet() < meilleure_solution.calculer_distance_trajet():
            meilleure_solution = solution_actuelle

        temperature *= alpha
        print(f"itération: {i} distance: {meilleure_solution.calculer_distance_trajet()}")

    return meilleure_solution



