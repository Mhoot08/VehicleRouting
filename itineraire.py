import copy
import random
import math
import itertools
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
    return None

def exchange_extra(camion1, camion2, client1, client2):
    # On échange un client entre deux camions
    if camion1.liste_clients and camion2.liste_clients:
        if camion1.capacity - client1.demand + client2.demand <= camion1.max_capacity and camion2.capacity - client2.demand + client1.demand <= camion2.max_capacity:
            # Trouver l'index des clients dans les listes des camions
            index_client1_camion1 = camion1.liste_clients.index(client1)
            index_client2_camion2 = camion2.liste_clients.index(client2)

            # Échanger les clients en utilisant leurs index
            camion1.liste_clients[index_client1_camion1] = client2
            camion2.liste_clients[index_client2_camion2] = client1


            # Recalculer les capacités
            camion1.capacity = sum([client.demand for client in camion1.liste_clients])
            camion2.capacity = sum([client.demand for client in camion2.liste_clients])
            return [camion1, camion2]
    return None

def relocate_extra(camion1, camion2, client1, client2):

    if camion2.capacity + client1.demand < camion2.max_capacity:
        # On échange les clients
        camion1.liste_clients.remove(client1)
        camion2.liste_clients.insert(client2, client1)

        # Recalculer les capacités
        camion1.capacity = sum([client.demand for client in camion1.liste_clients])
        camion2.capacity = sum([client.demand for client in camion2.liste_clients])
        return [camion1, camion2]
    else:
        return None

def cross_exchange(camion1, camion2, index1, index2, num_clients1, num_clients2):
    """
    Échange des groupes de clients de tailles différentes entre deux camions.

    Args:
    - camion1: Premier camion impliqué dans l'échange.
    - camion2: Deuxième camion impliqué dans l'échange.
    - index1: Index du premier client dans le premier camion.
    - index2: Index du premier client dans le deuxième camion.
    - num_clients1: Nombre de clients à échanger du premier camion.
    - num_clients2: Nombre de clients à échanger du deuxième camion.

    Returns:
    - camion1: Premier camion après l'échange.
    - camion2: Deuxième camion après l'échange.
    """
    if num_clients1 == 1 and num_clients2 == 1:
        return None, None, None  # Éviter l'échange de segments de taille 1
    if num_clients1 > len(camion1.liste_clients) - index1 or num_clients2 > len(camion2.liste_clients) - index2:
        return None, None, None  # Impossible d'échanger plus de clients que ce que les camions ont

    # Extraire les groupes de clients à échanger
    clients_to_exchange_camion1 = camion1.liste_clients[index1:index1 + num_clients1]
    clients_to_exchange_camion2 = camion2.liste_clients[index2:index2 + num_clients2]

    # Vérifier si l'échange est possible en termes de capacité des camions
    demand_camion1 = sum(client.demand for client in clients_to_exchange_camion1)
    demand_camion2 = sum(client.demand for client in clients_to_exchange_camion2)
    if (camion1.capacity - demand_camion1 + demand_camion2 <= camion1.max_capacity) and \
       (camion2.capacity - demand_camion2 + demand_camion1 <= camion2.max_capacity):
        # Effectuer l'échange
        camion1.liste_clients[index1:index1 + num_clients1] = clients_to_exchange_camion2
        camion2.liste_clients[index2:index2 + num_clients2] = clients_to_exchange_camion1

        # Recalculer les capacités
        camion1.capacity = sum(client.demand for client in camion1.liste_clients)
        camion2.capacity = sum(client.demand for client in camion2.liste_clients)

        return camion1, camion2, [clients_to_exchange_camion1, clients_to_exchange_camion2]
    else:
        return None, None, None

def rotate_camion(camion, index1):
    """
    Rotation des clients d'un camion entre deux indices.

    Args:
    - camion: Camion dont les clients doivent être tournés.
    - index1: Index du premier client.
    - index2: Index du deuxième client.

    Returns:
    - camion: Camion après la rotation.
    """
    if index1 == 0:
        return None  # Éviter la rotation de taille 0

    # Extraire les clients à tourner
    clients_to_rotate = camion.liste_clients[:index1]

    # Effectuer la rotation
    camion.liste_clients = camion.liste_clients[index1:] + clients_to_rotate

    return camion

def choisir_voisin(solution):
    result = None
    operateurs = ["exchange_extra(camion1, camion2, client1, client2)", "exchange_intra(camion1, client1, client2_camion1)", "relocate_intra(camion1, client1, index1_relocate)", "relocate_extra(camion1, camion2, client1, index2_relocate)"]
    #operateurs = ["relocate_extra(camion1, camion2, client1, index2_relocate)"]
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


def ecrire_fichier_resultats(liste_resultats):
    nom_fichier = "resultats.txt"
    print(f"Ecriture des résultats dans le fichier {nom_fichier}")
    with open(nom_fichier, 'w+') as fichier:
        for resultat in liste_resultats:
            fichier.write(f"{resultat}\n")
    print("Ecriture terminée")
    return


def recuit_simule(solution_initiale, temperature_initiale, alpha, seuil_sans_amelioration):
    liste_resultats = []
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
        for i in range(50000):
            solution_courante, operateur = choisir_voisin(meilleure_solution)
            delta = solution_courante.calculer_distance_total() - meilleure_solution.calculer_distance_total()
            if delta < 0:
                meilleure_solution = copy.deepcopy(solution_courante)
                if meilleure_solution.calculer_distance_total() < fmin:
                    fmin = meilleure_solution.calculer_distance_total()
                    meilleure_solution = copy.deepcopy(solution_courante)
                    print(f"Iteration: {k}.{iterations} Distance: {meilleure_solution.calculer_distance_total()} Température: {temperature} Opérateur: {operateur}")
                    liste_resultats.append(fmin)
                    if round(fmin, 0) <= 365:
                        #ecrire_fichier_resultats(liste_resultats)
                        #show_courbe(liste_resultats)
                        return meilleure_solution
                        for camion in meilleure_solution.camions:
                            clients_str = ", ".join([f"{client.idName}" for client in camion.liste_clients])
                            print(f"Camion {camion.id} : [{clients_str}]")
                            break

            else:
                iterations_sans_amelioration += 1
                if random.random() < math.exp(-delta / temperature):
                    meilleure_solution = copy.deepcopy(solution_courante)


            # if iterations_sans_amelioration >= seuil_sans_amelioration:
            #     print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
            #     break

            iterations += 1

        temperature *= alpha

        sauvegarder_solution(meilleure_solution, k)

    print("salut")
    #ecrire_fichier_resultats(liste_resultats)
    print("Réalisation de la courbe")
    show_courbe(liste_resultats)
    return meilleure_solution





def generer_voisins(solution):
    voisins = []

    # Relocate_intra
    for camion in solution.camions:
        for client1 in camion.liste_clients:
            for index in range(len(camion.liste_clients)):

                solution_deepcopy = copy.deepcopy(solution)
                index_camion = solution_deepcopy.camions.index(camion)
                deepcopy_camion = solution_deepcopy.camions[index_camion]
                deepcopy_client1 = deepcopy_camion.liste_clients[deepcopy_camion.liste_clients.index(client1)]

                client_at_index = deepcopy_camion.liste_clients[index]
                if index == deepcopy_camion.liste_clients.index(client1):
                    continue
                result = relocate_intra(deepcopy_camion, deepcopy_client1, index)
                if not result:
                    continue
                client1_previous = None if index == 0 else deepcopy_camion.liste_clients[index - 1].idName
                client1_next = None if index == len(deepcopy_camion.liste_clients) - 1 else deepcopy_camion.liste_clients[index + 1].idName

                client_at_index_previous = None if index == 0 else deepcopy_camion.liste_clients[index - 1].idName
                client_at_index_next = None if index == len(deepcopy_camion.liste_clients) - 1 else deepcopy_camion.liste_clients[index + 1].idName

                for camion2 in result:
                    index_camion = solution_deepcopy.camions.index(camion2)
                    solution_deepcopy.camions[index_camion] = camion2

                for camion2 in solution_deepcopy.camions:
                    if not camion2.liste_clients:
                        solution_deepcopy.camions.remove(camion2)

                operation_inverse = [f"relocate intra, {[client1_previous, deepcopy_camion.liste_clients[index].idName]}", f"relocate intra, {[deepcopy_camion.liste_clients[index].idName, client1_next]}"]
                operation_a_faire = [f"relocate intra, {[client_at_index_previous, deepcopy_camion.liste_clients[index].idName]}", f"relocate intra, {[deepcopy_camion.liste_clients[index].idName, client_at_index_next]}"]
                voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])


    # Exchange_intra
    for camion in solution.camions:
        break
        for client1 in camion.liste_clients:
            for client2 in camion.liste_clients:
                if client1 != client2:
                    solution_deepcopy = copy.deepcopy(solution)
                    index_camion = solution_deepcopy.camions.index(camion)
                    deepcopy_camion = solution_deepcopy.camions[index_camion]
                    deepcopy_client1 = deepcopy_camion.liste_clients[deepcopy_camion.liste_clients.index(client1)]
                    deepcopy_client2 = deepcopy_camion.liste_clients[deepcopy_camion.liste_clients.index(client2)]

                    result = exchange_intra(deepcopy_camion, deepcopy_client1, deepcopy_client2)
                    if not result:
                        continue
                    for camion2 in result:
                        index_camion = solution_deepcopy.camions.index(camion2)
                        solution_deepcopy.camions[index_camion] = camion2

                    for camion2 in solution_deepcopy.camions:
                        if not camion2.liste_clients:
                            solution_deepcopy.camions.remove(camion2)

                    operation_inverse = [f"exchange intra, {camion.id}, {deepcopy_client1.idName}, {deepcopy_client2.idName}", f"exchange intra, {camion.id}, {deepcopy_client2.idName}, {deepcopy_client1.idName}"]
                    operation_a_faire = [f"exchange intra, {camion.id}, {deepcopy_client1.idName}, {deepcopy_client2.idName}"]
                    #voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])

    # Exchange_extra
    for camion_i in solution.camions:
        break
        for camion_j in solution.camions:
            if camion_i != camion_j:
                for client1 in camion_i.liste_clients:
                    for client2 in camion_j.liste_clients:
                        if client1.idName != client2.idName:
                            solution_deepcopy = copy.deepcopy(solution)
                            index_camion_i_deepcopy = solution_deepcopy.camions.index(camion_i)
                            index_camion_j_deepcopy = solution_deepcopy.camions.index(camion_j)
                            deepcopy_camion_i = solution_deepcopy.camions[index_camion_i_deepcopy]
                            deepcopy_camion_j = solution_deepcopy.camions[index_camion_j_deepcopy]
                            deepcopy_client1 = deepcopy_camion_i.liste_clients[deepcopy_camion_i.liste_clients.index(client1)]
                            deepcopy_client2 = deepcopy_camion_j.liste_clients[deepcopy_camion_j.liste_clients.index(client2)]

                            operation_inverse = (deepcopy_camion_i, deepcopy_camion_j, deepcopy_client2, deepcopy_client1)

                            result = exchange_extra(deepcopy_camion_i, deepcopy_camion_j, deepcopy_client1, deepcopy_client2)
                            if not result:
                                continue
                            for camion2 in result:
                                index_camion = solution_deepcopy.camions.index(camion2)
                                solution_deepcopy.camions[index_camion] = camion2

                            for camion2 in solution_deepcopy.camions:
                                if not camion2.liste_clients:
                                    solution_deepcopy.camions.remove(camion2)


                            operation_inverse = [f"exchange extra, {deepcopy_client2.idName}, {deepcopy_client1.idName}", f"exchange extra, {deepcopy_client1.idName}, {deepcopy_client2.idName}"]
                            operation_a_faire = [f"exchange extra, {deepcopy_client1.idName}, {deepcopy_client2.idName}"]

                            #voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])


    # Relocate_extra
    for camion_i in solution.camions:
        for camion_j in solution.camions:
            if camion_i != camion_j:
                for client1 in camion_i.liste_clients:
                    for index in range(len(camion_j.liste_clients)):
                        solution_deepcopy = copy.deepcopy(solution)
                        index_camion_i_deepcopy = solution_deepcopy.camions.index(camion_i)
                        index_camion_j_deepcopy = solution_deepcopy.camions.index(camion_j)
                        deepcopy_camion_i = solution_deepcopy.camions[index_camion_i_deepcopy]
                        deepcopy_camion_j = solution_deepcopy.camions[index_camion_j_deepcopy]
                        deepcopy_client1 = deepcopy_camion_i.liste_clients[deepcopy_camion_i.liste_clients.index(client1)]


                        client_at_index_j = deepcopy_camion_j.liste_clients[index]
                        index_client_i = deepcopy_camion_i.liste_clients.index(deepcopy_client1)
                        camion_depart = deepcopy_camion_i.liste_clients
                        if deepcopy_client1 not in deepcopy_camion_j.liste_clients:
                            result = relocate_extra(deepcopy_camion_i, deepcopy_camion_j, deepcopy_client1, index)
                            if not result:
                                continue
                            camion_depart_result = result[0].liste_clients
                            camion_arrivee_result = result[1].liste_clients



                            depart_previous = None if index_client_i == 0 else camion_depart_result[index_client_i - 1].idName
                            depart_next = None if index_client_i == len(camion_depart_result) else camion_depart_result[index_client_i].idName

                            arrive_previous = None if index == 0 else camion_arrivee_result[index - 1].idName
                            arrivee_next = None if index == len(camion_arrivee_result) - 1 else camion_arrivee_result[index + 1].idName


                            for camion2 in result:
                                index_camion = solution_deepcopy.camions.index(camion2)
                                solution_deepcopy.camions[index_camion] = camion2

                            for camion2 in solution_deepcopy.camions:
                                if not camion2.liste_clients:
                                    solution_deepcopy.camions.remove(camion2)



                            operation_inverse = [f"relocate extra, {[depart_previous, camion_arrivee_result[index].idName]}", f"relocate extra, {[camion_arrivee_result[index].idName, depart_next]}", f"relocate extra, {[arrive_previous, camion_arrivee_result[index].idName]}", f"relocate extra, {[camion_arrivee_result[index].idName, arrivee_next]}"]
                            operation_a_faire = [f"relocate extra, {[arrive_previous, camion_arrivee_result[index].idName]}", f"relocate extra, {[camion_arrivee_result[index].idName, arrivee_next]}"]
                            voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])

    # Cross_exchange
    for camion1 in solution.camions:
        break
        for camion2 in solution.camions:
            if camion1 != camion2:
                for index1 in range(len(camion1.liste_clients)):
                    for index2 in range(len(camion2.liste_clients)):
                        # Itérer sur différentes longueurs de segments pour camion1 et camion2
                        for len1 in range(1, len(camion1.liste_clients) - index1 + 1):
                            for len2 in range(1, len(camion2.liste_clients) - index2 + 1):
                                if len1 == 1 and len2 == 1:
                                    continue
                                    # Il ne faut pas échanger tous les clients avec tous les clients de l'autre
                                if len1 == len(camion1.liste_clients) and len2 == len(camion2.liste_clients):
                                    continue
                                if len1 == len(camion1.liste_clients) - 1 and len2 == len(camion2.liste_clients) - 1:
                                    continue
                                solution_deepcopy = copy.deepcopy(solution)
                                index_camion1_deepcopy = solution_deepcopy.camions.index(camion1)
                                index_camion2_deepcopy = solution_deepcopy.camions.index(camion2)
                                deepcopy_camion1 = solution_deepcopy.camions[index_camion1_deepcopy]
                                deepcopy_camion2 = solution_deepcopy.camions[index_camion2_deepcopy]

                                new_camion1, new_camion2, clients_to_exchange = cross_exchange(
                                    solution_deepcopy.camions[index_camion1_deepcopy],
                                    solution_deepcopy.camions[index_camion2_deepcopy],
                                    index1, index2, len1, len2)
                                if not new_camion1 and not new_camion2 and not clients_to_exchange:
                                    continue
                                if new_camion1 and new_camion2:
                                    solution_deepcopy.camions[index_camion1_deepcopy] = new_camion1
                                    solution_deepcopy.camions[index_camion2_deepcopy] = new_camion2

                                    # Récupérer tous les clients entre les index pour les segments échangés
                                    clients_to_exchange_camion1 = clients_to_exchange[0]
                                    clients_to_exchange_camion2 = clients_to_exchange[1]

                                    liste_clients1_idName = [client.idName for client in clients_to_exchange_camion1]
                                    liste_clients2_idName = [client.idName for client in clients_to_exchange_camion2]

                                    operation_inverse = [
                                        f"cross exchange, {[liste_clients1_idName, liste_clients2_idName]}",
                                        f"cross exchange, {[liste_clients2_idName, liste_clients1_idName]}"]
                                    operation_a_faire = [
                                        f"cross exchange, {[liste_clients1_idName, liste_clients2_idName]}"]

                                    #voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])

        # Rotate_camion
        for camion in solution.camions:
            break
            for index1 in range(len(camion.liste_clients)):
                solution_deepcopy = copy.deepcopy(solution)
                index_camion_deepcopy = solution_deepcopy.camions.index(camion)
                deepcopy_camion = solution_deepcopy.camions[index_camion_deepcopy]

                new_camion = rotate_camion(deepcopy_camion, index1)
                if not new_camion:
                    continue
                solution_deepcopy.camions[index_camion_deepcopy] = new_camion

                operation_inverse = [f"rotate camion, {[camion.id, len(camion.liste_clients)-index1]}"]
                operation_a_faire = [f"rotate camion, {[camion.id, index1]}"]
                #voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])



    print(f"Nombre de voisins générés: {len(voisins)}")
    print(f"Nombre de camions dans la solution: {len(solution_deepcopy.camions)}")
    return voisins


def show_courbe(liste_resultats):
    """
    Affiche une courbe des résultats à partir d'une liste de nombres.

    Args:
    - liste_resultats: Liste de nombres représentant les résultats à afficher.
    """
    plt.figure(figsize=(10, 5))  # Taille de la figure
    plt.plot(liste_resultats, marker='o', linestyle='-', color='b', label='Résultats')
    plt.title('Courbe des Résultats')
    plt.xlabel('Indice')
    plt.ylabel('Valeur')
    plt.legend()
    plt.grid(True)
    plt.show()



def recherche_tabou(solution_initiale, taille_liste_tabou, max_iterations, seuil_sans_amelioration):
    meilleure_solution = copy.deepcopy(solution_initiale)
    fmin = solution_initiale.calculer_distance_total()
    i = 0

    liste_tabou = []
    iterations_sans_amelioration = 0
    liste_resultats = []

    for i in range(max_iterations):
        if i > 30:
            print("salut")
        voisins = generer_voisins(meilleure_solution)
        meilleure_voisin = None
        meilleure_distance = float('inf')
        meilleure_operateurs = None

        # if i > 25:
        #     print("f")
        continue_outer_loop = False
        for j in range(len(voisins)):
            voisin = voisins[j][0]
            operateurs_a_faire = voisins[j][2]
            liste_tabou_temp = list(itertools.chain(*liste_tabou))
            for operateur_a_faire in operateurs_a_faire:
                if operateur_a_faire in liste_tabou_temp:
                    # Saute l'itération de la boucle externe
                    continue_outer_loop = True
                    break
            if continue_outer_loop:
                continue_outer_loop = False
                continue

            distance = voisin.calculer_distance_total()
            if round(distance, 10) <= round(meilleure_distance, 10):
                meilleure_voisin = voisin
                meilleure_distance = distance
                operateur_inverse = voisins[j][1]
                meilleure_operateurs = [voisins[j][1], voisins[j][2]]

        if meilleure_voisin:

            meilleure_solution = copy.deepcopy(meilleure_voisin)
            if round(fmin, 10) <= round(meilleure_distance, 10):
                liste_tabou.append(operateur_inverse)
                if len(liste_tabou) > taille_liste_tabou:
                    liste_tabou.pop(0)
            fmin = meilleure_distance

            print(f"Iteration: {i}")
            print(f"Distance: {meilleure_distance}")
            print(f"taille_tabou: {len(liste_tabou)}")
            print(f"Inverse : {meilleure_operateurs[0]}")
            print(f"opération faite : {meilleure_operateurs[1]}")
            print(f"liste_tabou{liste_tabou}")
            for camion in meilleure_solution.camions:
                clients_str = ", ".join([f"{client.idName}" for client in camion.liste_clients])
                print(f"Camion {camion.id} : [{clients_str}] Capacité du camion : {camion.capacity}")
            print("____________________________________________________________________________________________________________________")
            liste_resultats.append(meilleure_distance)

            if iterations_sans_amelioration >= seuil_sans_amelioration:
                print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
                break


    show_courbe(liste_resultats[:30])
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

