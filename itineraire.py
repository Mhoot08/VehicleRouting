import copy
import random
import math
import matplotlib.pyplot as plt

from classes import Camion
from createMap import sauvegarder_solution, delete_all_images


def generer_solution_aleatoire(v, nombre_camions):
    clients = v.clients[:]  # Copie de la liste originale des clients
    max_capacity = v.CAPACITY
    solution = []

    # On mélange les clients
    random.shuffle(clients)

    # Créer le nombre spécifié de camions avec la capacité maximale
    camions = [Camion(max_capacity) for _ in range(nombre_camions)]

    # Ajouter un client à chaque camion
    for camion in camions:
        if clients:
            client = clients.pop()  # Prendre un client au hasard
            camion.add_client(client)

    # Attribuer les clients restants de manière aléatoire aux camions
    while clients:
        for camion in camions:
            if clients:
                client = clients.pop()  # Prendre un client au hasard
                if camion.capacity + client.demand <= max_capacity:
                    camion.add_client(client)

    # Ajouter uniquement les camions qui ont des clients à la solution
    solution.extend([camion for camion in camions if camion.liste_clients])

    v.camions = solution
    return v

def generer_solution_aleatoire_opti(v):
    clients = v.clients
    max_capacity = v.CAPACITY
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
    return v


def comparer_solutions(solution1, solution2):
    diff_clients = {}  # Dictionnaire pour stocker les différences entre les solutions
    
    # Comparer les camions dans les deux solutions
    for camion1, camion2 in zip(solution1.camions, solution2.camions):
        diff_clients[camion1] = []  # Initialisation des listes vides pour chaque camion

        # Comparer les listes de clients des camions dans les deux solutions
        for client1, client2 in zip(camion1.liste_clients, camion2.liste_clients):
            if client1 != client2:  # Si le client a changé entre les deux solutions
                diff_clients[camion1].append((client1.idName, client2.idName))  # Ajouter les ID des clients à la liste correspondante

    return diff_clients

# Relocate va prendre un client et soit le donner à un autre camion à un endroit aléatoire, soit le replacer dans son camion à un autre endroit
# Dans le cas où on vide un camion, on le supprime
def relocate(solution):
    voisins = []
    for i in range(len(solution.camions)):
        camion_i = solution.camions[i]
        for j in range(len(camion_i.liste_clients)):
            client_i = camion_i.liste_clients[j]

            # Relocalisation intra-camion
            for j_prime in range(len(camion_i.liste_clients)):
                if j == j_prime:  # Ignorer le déplacement du client vers la même position
                    continue
                voisin = solution.copy()
                voisin.camions[i].liste_clients[j], voisin.camions[i].liste_clients[j_prime] = \
                voisin.camions[i].liste_clients[j_prime], voisin.camions[i].liste_clients[j]
                voisins.append(voisin)

            # Relocalisation extra-camion
            for k in range(len(solution.camions)):
                if i == k:  # Ignorer le déplacement du client vers le même camion
                    continue
                voisin = solution.copy()
                voisin.camions[i].liste_clients.pop(j)
                voisin.camions[k].liste_clients.append(client_i)
                if voisin.camions[i].capacite_suffisante(voisin.camions[i].liste_clients) and voisin.camions[k].capacite_suffisante(voisin.camions[k].liste_clients):
                    # Supprimer le camion si vide
                    if not voisin.camions[i].liste_clients:
                        voisin.camions.pop(i)
                    voisins.append(voisin)

    return voisins

# On change de place un client dans un camion
def relocate_intra(camion, client, index):
    # On insère le client à l'index choisi
    camion.liste_clients.remove(client)

    camion.liste_clients.insert(index, client)

     # Recalculer la capacité
    camion.capacity = sum([client.demand for client in camion.liste_clients])

    return [camion]

def exchange_intra(camion, client1, client2):
    # On échange deux clients dans un même camion
    if len(camion.liste_clients) > 1:
        # On échange les clients
        index1 = camion.liste_clients.index(client1)
        index2 = camion.liste_clients.index(client2)

        camion.liste_clients[index1] = client2
        camion.liste_clients[index2] = client1

    # Recalculer la capacité
    camion.capacity = sum([client.demand for client in camion.liste_clients])

    return [camion]

def exchange_extra(camion1, camion2, client1, client2):
    # On échange un client entre deux camions
    if camion1.liste_clients and camion2.liste_clients:
        if camion1.capacity - client1.demand + client2.demand <= camion1.max_capacity and camion2.capacity - client2.demand + client1.demand <= camion2.max_capacity:
            # On échange les clients
            if client1 not in camion1.liste_clients:
                print("Client1 not in camion1")
            camion1.liste_clients.remove(client1)
            if client2 not in camion2.liste_clients:
                print("Client2 not in camion1")
            camion2.liste_clients.remove(client2)

            camion1.liste_clients.append(client2)
            camion2.liste_clients.append(client1)


    # Recalculer les capacités
    camion1.capacity = sum([client.demand for client in camion1.liste_clients])
    camion2.capacity = sum([client.demand for client in camion2.liste_clients])
    return [camion1, camion2]

def relocate_extra(camion1, camion2, client1, client2):

    if camion2.capacity + client1.demand < camion2.max_capacity:
        # On échange les clients
        camion1.liste_clients.remove(client1)
        camion2.liste_clients.insert(client2, client1)

    # Recalculer les capacités
    camion1.capacity = sum([client.demand for client in camion1.liste_clients])
    camion2.capacity = sum([client.demand for client in camion2.liste_clients])

    return [camion1, camion2]

def choisir_voisin(solution):
    result = None
    operateurs = ["exchange_extra(camion1, camion2, client1, client2)", "exchange_intra(camion1, client1, client2_camion1)", "relocate_intra(camion1, client1, index1_relocate)", "relocate_extra(camion1, camion2, client1, index2_relocate)"]
    #operateurs = ["exchange_extra(camion1, camion2, client1, client2)"]
    while not result:
        operateur = random.choice(operateurs)
        solution_deepcopy = copy.deepcopy(solution)

        if operateur == "exchange_extra(camion1, camion2, client1, client2)":
            camion1 = random.choice(solution_deepcopy.camions)
            camion2 = random.choice(solution_deepcopy.camions)
            while camion1 == camion2:
                camion2 = random.choice(solution_deepcopy.camions)
            client1 = random.choice(camion1.liste_clients)
            client2 = random.choice(camion2.liste_clients)
            while client1 == client2:
                client2 = random.choice(camion2.liste_clients)
            if client2 not in camion2.liste_clients:
                print("Client2 not in camion1")
        if operateur == "exchange_intra(camion1, client1, client2_camion1)":
            camion1 = random.choice(solution_deepcopy.camions)
            client1 = random.choice(camion1.liste_clients)
            client2_camion1 = random.choice(camion1.liste_clients)
        if operateur == "relocate_intra(camion1, client1, index1_relocate)":
            camion1 = random.choice(solution_deepcopy.camions)
            client1 = random.choice(camion1.liste_clients)
            index1_relocate = random.randint(0, len(camion1.liste_clients) - 1)
        if operateur == "relocate_extra(camion1, camion2, client1, index2_relocate)":
            camion1 = random.choice(solution_deepcopy.camions)
            camion2 = random.choice(solution_deepcopy.camions)
            client1 = random.choice(camion1.liste_clients)
            index2_relocate = random.randint(0, len(camion2.liste_clients) - 1)

        result = eval(operateur)
        camion1, camion2, client1, client2, index1_relocate, index2_relocate = None, None, None, None, None, None

    for camion in result:
        index_camion = solution_deepcopy.camions.index(camion)
        solution_deepcopy.camions[index_camion] = camion

    for camion in solution_deepcopy.camions:
        if not camion.liste_clients:
            solution_deepcopy.camions.remove(camion)

    return solution_deepcopy, operateur


def recuit_simule(solution_initiale, temperature_initiale, alpha, seuil_sans_amelioration):
    delete_all_images()
    meilleure_solution = solution_initiale
    temperature = temperature_initiale
    iterations_sans_amelioration = 0
    iterations = 0
    n1 = int(math.log(math.log(0.8) / math.log(0.1)) / math.log(alpha))
    print(f"n1: {n1}")
    fmin = solution_initiale.calculer_distance_total()

    for k in range(n1):
        iterations_sans_amelioration = 0
        for i in range(100000):
            solution_courante, operateur = choisir_voisin(meilleure_solution)
            delta = solution_courante.calculer_distance_total() - meilleure_solution.calculer_distance_total()

            if delta < 0:
                meilleure_solution = copy.deepcopy(solution_courante)
                if meilleure_solution.calculer_distance_total() < fmin:
                    fmin = meilleure_solution.calculer_distance_total()
                    meilleure_solution = copy.deepcopy(solution_courante)
                    print(f"Iteration: {k}.{iterations} Distance: {meilleure_solution.calculer_distance_total()} Température: {temperature} Opérateur: {operateur}")
            else:
                iterations_sans_amelioration += 1
                if random.random() < math.exp(-delta / temperature):
                    meilleure_solution = copy.deepcopy(solution_courante)

            if iterations_sans_amelioration >= seuil_sans_amelioration:
                print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
                break

            iterations += 1

        temperature *= alpha

        sauvegarder_solution(meilleure_solution, k)

    return meilleure_solution





def generer_voisins(solution):
    voisins = []

    # Relocate_inter
    for camion in solution.camions:
        for client1 in camion.liste_clients:
            for index in range(len(camion.liste_clients)):
                solution_deepcopy = copy.deepcopy(solution)
                result = relocate_intra(camion, client1, index)
                for camion2 in result:
                    index_camion = solution.camions.index(camion2)
                    solution_deepcopy.camions[index_camion] = camion2

                for camion2 in solution_deepcopy.camions:
                    if not camion2.liste_clients:
                        solution_deepcopy.camions.remove(camion2)

                voisins.append(solution_deepcopy)


    # Exchange_intra
    for camion in solution.camions:
        for client1 in camion.liste_clients:
            for client2 in camion.liste_clients:
                if client1 != client2:
                    solution_deepcopy = copy.deepcopy(solution)
                    result = exchange_intra(camion, client1, client2)
                    for camion2 in result:
                        index_camion = solution.camions.index(camion2)
                        solution_deepcopy.camions[index_camion] = camion2

                    for camion2 in solution_deepcopy.camions:
                        if not camion2.liste_clients:
                            solution_deepcopy.camions.remove(camion2)

                    voisins.append(solution_deepcopy)

    # Exchange_extra
    for camion_i in solution.camions:
        for camion_j in solution.camions:
            if camion_i != camion_j:
                for client1 in camion_i.liste_clients:
                    for client2 in camion_j.liste_clients:
                        if client1.idName != client2.idName:
                            if client1 not in camion_i.liste_clients:
                                print("Client1 not in camion1")
                                # LE pROBLEME VIENT DE LINSTANCE DE SOLUTION METTRE UN POINT DARRET 304 POUR COMPRENDRE
                            result = exchange_extra(camion_i, camion_j, client1, client2)
                            solution_deepcopy = copy.deepcopy(solution)
                            for camion2 in result:
                                index_camion = solution.camions.index(camion2)
                                solution_deepcopy.camions[index_camion] = camion2

                            for camion2 in solution_deepcopy.camions:
                                if not camion2.liste_clients:
                                    solution_deepcopy.camions.remove(camion2)

                            voisins.append(solution_deepcopy)


    # Relocate_extra
    for camion_i in solution.camions:
        for camion_j in solution.camions:
            if camion_i != camion_j:
                for client1 in camion_i.liste_clients:
                    for index in range(len(camion_j.liste_clients)):
                        solution_deepcopy = copy.deepcopy(solution)
                        result = relocate_extra(camion_i, camion_j, client1, index)
                        for camion2 in result:
                            index_camion = solution.camions.index(camion2)
                            solution_deepcopy.camions[index_camion] = camion2

                        for camion2 in solution_deepcopy.camions:
                            if not camion2.liste_clients:
                                solution_deepcopy.camions.remove(camion2)

                        voisins.append(solution_deepcopy)

    return voisins

def recherche_tabou(solution_initiale, taille_liste_tabou, max_iterations, seuil_sans_amelioration):
    meilleure_solution = copy.deepcopy(solution_initiale)
    fmin = solution_initiale.calculer_distance_total()
    i = 0

    liste_tabou = []
    iterations_sans_amelioration = 0

    for i in range(max_iterations):
        voisins = generer_voisins(meilleure_solution)
        meilleure_voisin = None
        meilleure_distance = float('inf')

        for voisin in voisins:
            if voisin in liste_tabou:
                continue

            distance = voisin.calculer_distance_total()
            if distance < meilleure_distance:
                meilleure_voisin = voisin
                meilleure_distance = distance

        if meilleure_voisin:
            print(f"Meilleure distance de ce voisinage: {meilleure_distance}")
            if meilleure_distance < fmin:
                print(f"Meilleure distance trouvée: {meilleure_distance}")
                fmin = meilleure_distance
                meilleure_solution = copy.deepcopy(meilleure_voisin)
                print(f"Iteration: {i} Distance: {meilleure_distance}")
            else:
                iterations_sans_amelioration += 1

            liste_tabou.append(meilleure_voisin)
            if len(liste_tabou) > taille_liste_tabou:
                liste_tabou.pop(0)

            if iterations_sans_amelioration >= seuil_sans_amelioration:
                print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
                break



def start_metaheuristique(v):
    nb_min_vehicule = v.getNbMinVehicle()
    list_solutions = {}
    best_solution = copy.deepcopy(v)  # Crée une copie indépendante de v

    new_best_solution = copy.deepcopy(v)  # Crée une copie indépendante de v

    for i in range(2, 100):

        for i in range(nb_min_vehicule, 10):
            print(f"itération métaheuristique: {i} camions")
            solution_initiale = generer_solution_aleatoire(v, i)
            v = recherche_tabou(solution_initiale, 100, 1000000, 10)
            print(f"v.calculer_distance_total(): {v.calculer_distance_total()}")
            print(f"best_solution.calculer_distance_total(): {best_solution.calculer_distance_total()}")
            list_solutions[i] = v.calculer_distance_total();
            if v.calculer_distance_total() < best_solution.calculer_distance_total():
                best_solution = copy.deepcopy(v)  # Met à jour best_solution avec la nouvelle meilleure solution
                print(f"Meilleure solution: {best_solution.calculer_distance_total()} avec {i} camions")
        print(f"Meilleure solution finale: {best_solution.calculer_distance_total()}")
        if new_best_solution.calculer_distance_total() > best_solution.calculer_distance_total():
            new_best_solution = copy.deepcopy(best_solution)

    return best_solution

