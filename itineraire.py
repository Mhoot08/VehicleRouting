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

def comparer_solutions(solution1, solution2):
    diff_clients = {}  # Dictionnaire pour stocker les différences entre les solutions
    
    # Comparer les camions dans les deux solutions
    for camion1, camion2 in zip(solution1, solution2):
        diff_clients[camion1] = []  # Initialisation des listes vides pour chaque camion

        # Comparer les listes de clients des camions dans les deux solutions
        for client1, client2 in zip(camion1.liste_clients, camion2.liste_clients):
            if client1 != client2:  # Si le client a changé entre les deux solutions
                diff_clients[camion1].append((client1.idName, client2.idName))  # Ajouter les ID des clients à la liste correspondante

    return diff_clients

def opt_2(solution):
    voisins = []

    # Parcourir tous les camions
    for i in range(len(solution.camions)):
        camion_i = solution.camions[i]
        
        # Parcourir tous les clients du camion i
        for j in range(len(camion_i.liste_clients)):
            client_i = camion_i.liste_clients[j]
            
            # Parcourir tous les autres camions
            for k in range(len(solution.camions)):
                camion_k = solution.camions[k]
                
                # Éviter de transférer le client_i vers son propre camion
                if k != i:
                    # Parcourir tous les clients du camion k
                    for l in range(len(camion_k.liste_clients)):
                        client_k = camion_k.liste_clients[l]
                        
                        # Créer une copie de la solution actuelle
                        voisin = solution.copy()  
                        
                        # Échanger les clients entre les camions
                        voisin.camions[i].liste_clients[j] = client_k
                        voisin.camions[k].liste_clients[l] = client_i
                        
                        # Vérifier si les capacités des camions sont respectées
                        if voisin.camions[i].capacite_suffisante(voisin.camions[i].liste_clients) and voisin.camions[k].capacite_suffisante(voisin.camions[k].liste_clients):
                            voisins.append(voisin)

    return voisins


def recuit_simule(solution_initiale, temperature_initiale, alpha, nombre_iterations, seuil_sans_amelioration):
    meilleure_solution = solution_initiale
    temperature = temperature_initiale
    iterations_sans_amelioration = 0
    voisins_actuel = None
    

    for i in range(nombre_iterations):
        if voisins_actuel is None:
            voisins_actuel = opt_2(meilleure_solution)
            voisin_choisi = random.choice(voisins_actuel)
        else:
            voisin_choisi = random.choice(voisins_actuel)

        if voisin_choisi is not None:
            delta_distance = voisin_choisi.calculer_distance_total() - meilleure_solution.calculer_distance_total()

            if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
                meilleure_solution = voisin_choisi
                iterations_sans_amelioration = 0  # Réinitialiser le compteur
                voisins_actuel = None
                if i > 5000:
                    print(f"itération: {i} distance: {meilleure_solution.calculer_distance_total()}")
            else:
                iterations_sans_amelioration += 1

            if iterations_sans_amelioration >= seuil_sans_amelioration:
                print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
                break

        temperature *= alpha

    return meilleure_solution



