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
def exchange_extra(solution):
    voisins = []

    for _ in range(10000):
        # Sélectionner aléatoirement deux camions différents
        camion1_idx, camion2_idx = random.sample(range(len(solution.camions)), 2)
        camion1 = solution.camions[camion1_idx]
        camion2 = solution.camions[camion2_idx]

        # Sélectionner aléatoirement un client dans chaque camion
        client1_idx, client2_idx = random.randint(0, len(camion1.liste_clients) - 1), random.randint(0, len(camion2.liste_clients) - 1)
        client1 = camion1.liste_clients[client1_idx]
        client2 = camion2.liste_clients[client2_idx]

        # Échanger les clients entre les camions
        nouveau_trajet1 = camion1.liste_clients.copy()
        nouveau_trajet2 = camion2.liste_clients.copy()
        nouveau_trajet1[client1_idx] = client2
        nouveau_trajet2[client2_idx] = client1

        # Vérifier si les capacités des camions sont respectées
        if camion1.capacite_suffisante(nouveau_trajet1) and camion2.capacite_suffisante(nouveau_trajet2):
            voisin = solution.copy()  # Créer une copie de la solution actuelle
            voisin.camions[camion1_idx].liste_clients = nouveau_trajet1
            voisin.camions[camion2_idx].liste_clients = nouveau_trajet2
            voisins.append(voisin)  # Ajouter la nouvelle solution à la liste des voisins

    return voisins  # Retourner la liste des voisins

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

def fusion(solution):
    voisins = []
    # Parcours tous les camions et fusionner 2 camions si la capacité totale est respectée
    for i in range(len(solution.camions)):
        camion_i = solution.camions[i]
        for j in range(len(solution.camions)):
            camion_j = solution.camions[j]
            if i != j:
                if camion_i.capacity + camion_j.capacity <= solution.CAPACITY:
                    voisin = copy.deepcopy(solution)
                    voisin.camions[i].liste_clients.extend(voisin.camions[j].liste_clients)
                    voisin.camions[i].capacity += voisin.camions[j].capacity
                    voisin.camions.pop(j)
                    voisins.append(voisin)
    return voisins


def choisir_voisinage(solution):
    # Choisir un voisinage aléatoire
    methode_voisinages = ["relocate(solution)", "opt_2(solution)", "exchange_extra(solution)","fusion(solution)"]
    voisins = eval(random.choice(methode_voisinages))
    if not voisins:
        voisins = choisir_voisinage(solution)
    return voisins

def recuit_simule(solution_initiale, temperature_initiale, alpha, nombre_iterations, seuil_sans_amelioration):
    delete_all_images()
    meilleure_solution = solution_initiale
    temperature = temperature_initiale
    iterations_sans_amelioration = 0
    voisins_actuel = None
    

    for i in range(nombre_iterations):
        if voisins_actuel is None:
            voisins_actuel = choisir_voisinage(meilleure_solution)
            voisin_choisi = random.choice(voisins_actuel)
        else:
            voisin_choisi = random.choice(voisins_actuel)

        if voisin_choisi is not None:
            delta_distance = voisin_choisi.calculer_distance_total() - meilleure_solution.calculer_distance_total()
            if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
                meilleure_solution = voisin_choisi
                iterations_sans_amelioration = 0  # Réinitialiser le compteur
                voisins_actuel = None
                print(f"itération: {i} distance: {meilleure_solution.calculer_distance_total()}")
            else:
                iterations_sans_amelioration += 1

            if iterations_sans_amelioration >= seuil_sans_amelioration:
                print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
                break

        temperature *= alpha

    return meilleure_solution


def recherche_tabou(solution_initiale, taille_liste_tabou, max_iterations, seuil_sans_amelioration):
    delete_all_images()
    solution_courante = solution_initiale
    meilleure_solution = solution_initiale
    liste_tabou = []

    iterations_sans_amelioration = 0

    for i in range(max_iterations):
        # Générer les voisins de la solution courante
        voisins = relocate(
            solution_courante)

        # Choisir le meilleur voisin non tabou
        meilleur_voisin = None
        meilleure_distance = float('inf')

        for voisin in voisins:
            if voisin not in liste_tabou:
                distance_voisin = voisin.calculer_distance_total()
                if distance_voisin < meilleure_distance:
                    meilleur_voisin = voisin
                    meilleure_distance = distance_voisin

        # Si aucun voisin n'est autorisé (tous sont tabous), on arrête l'algorithme
        if meilleur_voisin is None:
            print("Aucun voisin autorisé trouvé. Arrêt de l'algorithme.")
            break

        # Mettre à jour la solution courante
        solution_courante = meilleur_voisin

        # Mettre à jour la meilleure solution
        if meilleure_distance < meilleure_solution.calculer_distance_total():
            meilleure_solution = meilleur_voisin
            iterations_sans_amelioration = 0
            print(f"Iteration: {i}, Distance: {meilleure_distance}, nb voisin: {len(voisins)}")

        else:
            iterations_sans_amelioration += 1
        
        if iterations_sans_amelioration >= seuil_sans_amelioration:
            for camion in meilleure_solution.camions:
                print(f"Camion charge: {camion.capacity}")
            print(f"Aucune amélioration observée depuis {seuil_sans_amelioration} itérations. Arrêt de l'itération.")
            break

        # Mettre à jour la liste tabou
        liste_tabou.append(meilleur_voisin)

        # Si la taille de la liste tabou dépasse la taille maximale, enlever le plus ancien élément
        if len(liste_tabou) > taille_liste_tabou:
            liste_tabou.pop(0)

        # Vérifier si l'algorithme doit s'arrêter en cas d'absence d'amélioration
        

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

