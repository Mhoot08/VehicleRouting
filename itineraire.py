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
def relocate_intra(camion):
     # On prend un client aléatoire
    client = random.choice(camion.liste_clients)

    # Prendre un index aléatoire
    index = random.randint(0, len(camion.liste_clients) - 1)

    # On insère le client à l'index choisi
    camion.liste_clients.remove(client)

    camion.liste_clients.insert(index, client)

     # Recalculer la capacité
    camion.capacity = sum([client.demand for client in camion.liste_clients])

    return [camion]

def exchange_intra(camion):
    # On échange deux clients dans un même camion
    if len(camion.liste_clients) > 1:
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

    # Recalculer la capacité
    camion.capacity = sum([client.demand for client in camion.liste_clients])

    return [camion]

def exchange_extra(camion1, camion2):
    # On échange un client entre deux camions
    if camion1.liste_clients and camion2.liste_clients:
        client1 = random.choice(camion1.liste_clients)
        client2 = random.choice(camion2.liste_clients)

        if camion1.capacity - client1.demand + client2.demand <= camion1.max_capacity and camion2.capacity - client2.demand + client1.demand <= camion2.max_capacity:
            # On échange les clients
            camion1.liste_clients.remove(client1)
            camion2.liste_clients.remove(client2)

            camion1.liste_clients.append(client2)
            camion2.liste_clients.append(client1)
    # Recalculer les capacités
    camion1.capacity = sum([client.demand for client in camion1.liste_clients])
    camion2.capacity = sum([client.demand for client in camion2.liste_clients])
    return [camion1, camion2]

def relocate_extra(camion1, camion2):
    # On prend un client aléatoire dans le premier camion
    client = random.choice(camion1.liste_clients)

    # On prend un index aléatoire dans le deuxième camion
    index = random.randint(0, len(camion2.liste_clients) - 1)

    if camion2.capacity + client.demand < camion2.max_capacity:
        # On échange les clients
        camion1.liste_clients.remove(client)
        camion2.liste_clients.insert(index, client)

    # Recalculer les capacités
    camion1.capacity = sum([client.demand for client in camion1.liste_clients])
    camion2.capacity = sum([client.demand for client in camion2.liste_clients])

    return [camion1, camion2]

def choisir_voisin(solution):
    result = None
    operateurs = ["exchange_extra(camion1, camion2)", "exchange_intra(camion1)", "relocate_intra(camion1)", "relocate_extra(camion1, camion2)"]
    #operateurs = ["relocate_extra(camion1, camion2)"]
    while not result:
        solution_deepcopy = copy.deepcopy(solution)
        camion1 = random.choice(solution_deepcopy.camions)
        camion2 = random.choice(solution_deepcopy.camions)
        operateur = random.choice(operateurs)
        while camion1 == camion2:
            camion2 = random.choice(solution_deepcopy.camions)
        if operateur == "exchange_intra(camion1)" or operateur == "relocate_intra(camion1)":
            camion2 = None
        result = eval(operateur)

    for camion in result:
        index_camion = solution_deepcopy.camions.index(camion)
        solution_deepcopy.camions[index_camion] = camion

    for camion in solution_deepcopy.camions:
        if not camion.liste_clients:
            solution_deepcopy.camions.remove(camion)

    return solution_deepcopy, operateur


def recuit_simule(solution_initiale, temperature_initiale, alpha, nombre_iterations, seuil_sans_amelioration):
    delete_all_images()
    meilleure_solution = solution_initiale
    temperature = temperature_initiale
    iterations_sans_amelioration = 0

    for i in range(nombre_iterations):
        r = choisir_voisin(copy.deepcopy(meilleure_solution))
        voisin = r[0]
        delta_distance = round(voisin.calculer_distance_total() - meilleure_solution.calculer_distance_total())
        if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
            if not voisin.__eq__(meilleure_solution):
                meilleure_solution = voisin
                iterations_sans_amelioration = 0
                print(f"itération: {i} distance: {meilleure_solution.calculer_distance_total()} opérateur : {r[1]} Camions: {len(meilleure_solution.camions)}")
        else:
            iterations_sans_amelioration += 1

        if iterations_sans_amelioration >= seuil_sans_amelioration:
            print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
            break

        temperature *= alpha

    return meilleure_solution


def generer_voisins(solution):
    voisins = []

    # Pour chaque camion dans la solution
    for camion1 in solution.camions:
        for camion2 in solution.camions:
            solution_temp = copy.deepcopy(solution)
            if camion1 == camion2:
                continue

            # Opérateur: échange extra
            voisin = exchange_extra(copy.deepcopy(camion1), copy.deepcopy(camion2))
            if voisin:
                index_camion1 = solution.camions.index(camion1)
                index_camion2 = solution.camions.index(camion2)
                solution_temp.camions[index_camion1] = voisin[0]
                solution_temp.camions[index_camion2] = voisin[1]
                voisins.append(solution_temp)

            # Opérateur: échange intra
            voisin = exchange_intra(copy.deepcopy(camion1))
            if voisin:
                index_camion1 = solution.camions.index(camion1)
                solution_temp.camions[index_camion1] = voisin[0]
                voisins.append(solution_temp)

            # Opérateur: relocalisation intra
            voisin = relocate_intra(copy.deepcopy(camion1))
            if voisin:
                index_camion1 = solution.camions.index(camion1)
                solution_temp.camions[index_camion1] = voisin[0]
                voisins.append(solution_temp)

            # Opérateur: relocalisation extra
            voisin = relocate_extra(copy.deepcopy(camion1), copy.deepcopy(camion2))
            if voisin:
                index_camion1 = solution.camions.index(camion1)
                index_camion2 = solution.camions.index(camion2)
                solution_temp.camions[index_camion1] = voisin[0]
                solution_temp.camions[index_camion2] = voisin[1]
                voisins.append(solution_temp)

    return voisins

def recherche_tabou(solution_initiale, taille_liste_tabou, max_iterations, seuil_sans_amelioration):
    meilleure_solution = copy.deepcopy(solution_initiale)
    meilleure_valeur = meilleure_solution.calculer_distance_total()
    solution_courante = meilleure_solution
    liste_tabou = []  # Liste tabou initialement vide
    iterations_sans_amelioration = 0

    for i in range(max_iterations):
        meilleur_voisin = None
        meilleure_valeur_voisin = float('inf')

        for voisin in generer_voisins(solution_initiale):
            if voisin not in liste_tabou:
                valeur_voisin = voisin.calculer_distance_total()
                if valeur_voisin < meilleure_valeur_voisin:
                    meilleur_voisin = voisin
                    meilleure_valeur_voisin = valeur_voisin


        if meilleur_voisin:
            solution_courante = meilleur_voisin
            valeur_courante = meilleure_valeur_voisin

            if valeur_courante < meilleure_valeur_voisin:
                meilleure_solution = copy.deepcopy(solution_courante)

            liste_tabou.append(meilleur_voisin)
            if len(liste_tabou) > taille_liste_tabou:
                liste_tabou.pop(0)  # Supprimer le plus ancien voisin tabou
            iterations_sans_amelioration = 0
            print(f"Itération: {i} Distance: {meilleure_solution.calculer_distance_total()}")

        else:
            iterations_sans_amelioration += 1

        if iterations_sans_amelioration >= seuil_sans_amelioration:
            print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
            break

    return meilleure_solution

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

