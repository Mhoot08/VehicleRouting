import random
import math

from classes import Camion


def generer_solution_aleatoire(v, nombre_camions):
    clients = v.clients
    max_capacity = v.CAPACITY
    solution = []

    # On mélange les clients
    random.shuffle(clients)

    # Créer le nombre spécifié de camions avec la capacité maximale
    camions = [Camion(max_capacity) for _ in range(nombre_camions)]

    for client in clients:
        # Sélectionner un camion aléatoire parmi ceux qui n'ont pas atteint leur capacité maximale
        camion = random.choice([c for c in camions if c.capacity + client.demand <= max_capacity])

        # Ajouter le client au camion sélectionné
        camion.add_client(client)

    # Ajouter uniquement les camions qui ont des clients à la solution
    solution.extend([camion for camion in camions if camion.liste_clients])

    print(f"len(solution): {len(solution)}")
    for camion in solution:
        v.camions.append(camion)
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
            voisins_actuel = exchange_extra(meilleure_solution)
            voisin_choisi = random.choice(voisins_actuel)
            comparer_solutions(meilleure_solution, voisin_choisi)
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
    solution_courante = solution_initiale
    meilleure_solution = solution_initiale
    liste_tabou = []

    iterations_sans_amelioration = 0

    for i in range(max_iterations):
        # Générer les voisins de la solution courante
        voisins = opt_2(solution_courante)

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
            print(f"Iteration: {i}, Distance: {meilleure_distance}")
        else:
            iterations_sans_amelioration += 1
        
        if iterations_sans_amelioration >= seuil_sans_amelioration:
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
    meilleur_solution = v

    for i in range(nb_min_vehicule, 80):
        print(f"itération métaheuristique: {i} camions")
        v = generer_solution_aleatoire(v, i)
        v = recherche_tabou(v, 10, 1000, 10)
        if v.calculer_distance_total() < meilleur_solution.calculer_distance_total():
            meilleur_solution = v
            print(f"Meilleure solution: {meilleur_solution.calculer_distance_total()} avec {i} camions")
    return meilleur_solution

