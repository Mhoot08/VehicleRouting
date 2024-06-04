import copy
import random
import math
import itertools


import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrowPatch

import config
from VehicleRouting import VehicleRouting
from classes import Camion
from createMap import sauvegarder_solution, afficher_solution


def open_setup_window():
    def submit():
        setup(
            timewindow_var.get(),
            recuit_var.get(),
            tabou_var.get(),
            descente_var.get(),
            float(recuit_alpha_var.get()),
            int(recuit_temp_initiale_var.get()),
            int(tabou_taille_var.get()),
            int(tabou_nombre_var.get()),
            int(descente_nombre_var.get()),
            int(nombre_camion_var.get()),
            [op for op, var in operateur_vars.items() if var.get()],
            int(nombre_lancer_var.get()),
            int(nombre_clients_var.get())
        )
        root.destroy()

    root = tk.Tk()
    root.title("Setup Parameters")

    ttk.Label(root, text="Time Window:").grid(column=0, row=0, padx=10, pady=5)
    timewindow_var = tk.BooleanVar(value=config.TIMEWINDOW)
    ttk.Checkbutton(root, variable=timewindow_var).grid(column=1, row=0)

    ttk.Label(root, text="Recuit:").grid(column=0, row=1, padx=10, pady=5)
    recuit_var = tk.BooleanVar(value=config.RECUIT)
    ttk.Checkbutton(root, variable=recuit_var).grid(column=1, row=1)

    ttk.Label(root, text="Tabou:").grid(column=0, row=2, padx=10, pady=5)
    tabou_var = tk.BooleanVar(value=config.TABOU)
    ttk.Checkbutton(root, variable=tabou_var).grid(column=1, row=2)

    ttk.Label(root, text="Descente:").grid(column=0, row=3, padx=10, pady=5)
    descente_var = tk.BooleanVar(value=config.DESCENTE)
    ttk.Checkbutton(root, variable=descente_var).grid(column=1, row=3)

    ttk.Label(root, text="Recuit Alpha:").grid(column=0, row=4, padx=10, pady=5)
    recuit_alpha_var = tk.StringVar(value=str(config.RECUIT_ALPHA))
    ttk.Entry(root, textvariable=recuit_alpha_var).grid(column=1, row=4)

    ttk.Label(root, text="Recuit Temp Initiale:").grid(column=0, row=5, padx=10, pady=5)
    recuit_temp_initiale_var = tk.StringVar(value=str(config.RECUIT_TEMPERATURE_INITIALE))
    ttk.Entry(root, textvariable=recuit_temp_initiale_var).grid(column=1, row=5)

    ttk.Label(root, text="Tabou Taille Liste:").grid(column=0, row=6, padx=10, pady=5)
    tabou_taille_var = tk.StringVar(value=str(config.TABOU_TAILLE_LISTE_TABOU))
    ttk.Entry(root, textvariable=tabou_taille_var).grid(column=1, row=6)

    ttk.Label(root, text="Tabou Nombre Iterations:").grid(column=0, row=7, padx=10, pady=5)
    tabou_nombre_var = tk.StringVar(value=str(config.TABOU_NOMBRE_ITERATIONS))
    ttk.Entry(root, textvariable=tabou_nombre_var).grid(column=1, row=7)

    ttk.Label(root, text="Descente Nombre Iterations:").grid(column=0, row=8, padx=10, pady=5)
    descente_nombre_var = tk.StringVar(value=str(config.DESCENTE_NOMBRE_ITERATIONS))
    ttk.Entry(root, textvariable=descente_nombre_var).grid(column=1, row=8)

    ttk.Label(root, text="NB Camion:").grid(column=0, row=9, padx=10, pady=5)
    nombre_camion_var = tk.StringVar(value=str(config.NOMBRE_CAMIONS))
    ttk.Entry(root, textvariable=nombre_camion_var).grid(column=1, row=9)

    ttk.Label(root, text="NB Lancer:").grid(column=0, row=10, padx=10, pady=5)
    nombre_lancer_var = tk.StringVar(value=str(config.NOMBRE_LANCERS))
    ttk.Entry(root, textvariable=nombre_lancer_var).grid(column=1, row=10)

    ttk.Label(root, text="NB Clients:").grid(column=0, row=11, padx=10, pady=5)
    nombre_clients_var = tk.StringVar(value=str(config.NOMBRE_CLIENTS))
    ttk.Entry(root, textvariable=nombre_clients_var).grid(column=1, row=11)

    ttk.Label(root, text="Operateurs:").grid(column=0, row=12, padx=10, pady=5)
    operateur_vars = {}
    for i, operateur in enumerate(config.OPERATEURS):
        var = tk.BooleanVar(value=True)
        operateur_vars[operateur] = var
        ttk.Checkbutton(root, text=operateur, variable=var).grid(column=1, row=13 + i, sticky=tk.W)

    submit_button = ttk.Button(root, text="Submit", command=submit)
    submit_button.grid(column=0, row=13 + len(config.OPERATEURS), columnspan=2, pady=10)

    root.mainloop()


def setup(timewindow, recuit, tabou, descente, recuit_alpha, recuit_temperature_initiale, tabou_taille, tabou_nombre, descente_nombre, nombre_camion ,operateurs, nombre_lancer, nombre_clients):
    config.TIMEWINDOW = timewindow
    config.RECUIT = recuit
    config.TABOU = tabou
    config.DESCENTE = descente
    config.RECUIT_ALPHA = recuit_alpha
    config.RECUIT_TEMPERATURE_INITIALE = recuit_temperature_initiale
    config.TABOU_TAILLE_LISTE_TABOU = tabou_taille
    config.TABOU_NOMBRE_ITERATIONS = tabou_nombre
    config.DESCENTE_NOMBRE_ITERATIONS = descente_nombre
    config.OPERATEURS = operateurs
    config.NOMBRE_CAMIONS = nombre_camion
    config.NOMBRE_LANCERS = nombre_lancer
    config.NOMBRE_CLIENTS = nombre_clients

def calculer_temps_trajet(client1, client2):
    temps_x = abs(client1.x - client2.x)
    temps_y = abs(client1.y - client2.y)
    return temps_y + temps_x
def time_condition_overall(camion):
    time = 0
    for i in range(-1, len(camion.liste_clients) - 1):
        if i == -1:
            time = abs(camion.liste_clients[0].x + camion.liste_clients[0].y) + camion.liste_clients[0].service
            continue
        if i == len(camion.liste_clients) - 1:
            time += abs(camion.liste_clients[i].x + camion.liste_clients[i].y)
            if time > 230:
                return False
            continue
        arrivee = time + calculer_temps_trajet(camion.liste_clients[i], camion.liste_clients[i + 1])
        if arrivee > camion.liste_clients[i + 1].dueTime:
            return False
        elif arrivee < camion.liste_clients[i + 1].readyTime:
            time = camion.liste_clients[i + 1].readyTime + camion.liste_clients[i + 1].service
        else :
            time = arrivee + camion.liste_clients[i + 1].service
    return True


def generer_solution_aleatoire(v, nombre_camions):
    if config.TIMEWINDOW:
        clients = v.clients[:]  # Copie de la liste originale des clients
        max_capacity = v.CAPACITY
        solution = []

        # On mélange les clients
        random.shuffle(clients)

        # Créer le nombre spécifié de camions avec la capacité maximale
        camions = [Camion(max_capacity) for _ in range(nombre_camions)]

        rejected_clients = assign_one_client(camions, clients, max_capacity)

        # Retry assigning rejected clients to different camions
        clientInRejected = True
        compteur = 0
        while clientInRejected:
            for client in rejected_clients:
                for camion in camions:
                    if camion.capacity + client.demand <= max_capacity:
                        if not time_condition_overall(camion):
                            continue
                        camion.add_client(client)
                        rejected_clients.remove(client)
                        break
                if len(rejected_clients) == 0:
                    clientInRejected = False
            compteur += 1
            print(len(rejected_clients))
            if compteur > 100:
                return None
        # Ajouter uniquement les camions qui ont des clients à la solution
        solution.extend([camion for camion in camions if camion.liste_clients])

        v.camions = solution
        return v
    else:
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


def assign_one_client(camions, clients, max_capacity):
    # Ajouter un client à chaque camion
    for camion in camions:
        if clients:
            client = clients.pop()  # Prendre un client au hasard
            camion.add_client(client)
    # Attribuer les clients restants de manière aléatoire aux camions
    rejected_clients = []
    while clients:
        for camion in camions:
            if clients:
                client = clients.pop()  # Prendre un client au hasard
                if camion.capacity + client.demand <= max_capacity:
                    camion.add_client(client)
                    if not time_condition_overall(camion):
                        camion.remove_client(client)
                        rejected_clients.append(client)  # Add to rejected clients list
    return rejected_clients


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
    if config.TIMEWINDOW and not time_condition_overall(camion):
        return None
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
        if config.TIMEWINDOW and not time_condition_overall(camion):
            return None
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
            if config.TIMEWINDOW and not time_condition_overall(camion1) or not time_condition_overall(camion2):
                return None
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
        if config.TIMEWINDOW and not time_condition_overall(camion2):
            return None
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
        if config.TIMEWINDOW and not time_condition_overall(camion1) or not time_condition_overall(camion2):
            return None, None, None
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
    operateurs = []
    if "relocate_intra" in config.OPERATEURS:
        operateurs.append("relocate_intra(camion1, client1, index1_relocate)")
    if "exchange_intra" in config.OPERATEURS:
        operateurs.append("exchange_intra(camion1, client1, client2_camion1)")
    if "exchange_extra" in config.OPERATEURS:
        operateurs.append("exchange_extra(camion1, camion2, client1, client2)")
    if "relocate_extra" in config.OPERATEURS:
        operateurs.append("relocate_extra(camion1, camion2, client1, index2_relocate)")

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


def recuit_simule():
    global_solution = None
    global_solution_distance = float('-inf')
    print("Début de l'algorithme de recuit simulé")
    v = VehicleRouting()
    liste_resultats = []
    meilleure_solution = generer_solution_aleatoire(v, config.NOMBRE_CAMIONS)
    afficher_solution(meilleure_solution)
    temperature = config.RECUIT_TEMPERATURE_INITIALE
    iterations_sans_amelioration = 0
    iterations = 0
    n1 = int(math.log(math.log(0.8) / math.log(0.1)) / math.log(config.RECUIT_ALPHA))
    print(f"n1: {n1}")
    fmin = meilleure_solution.calculer_distance_total()

    for k in range(n1):
        iterations_sans_amelioration = 0
        for i in range(1000):
            solution_courante, operateur = choisir_voisin(meilleure_solution)
            delta = solution_courante.calculer_distance_total() - meilleure_solution.calculer_distance_total()
            if delta < 0:
                meilleure_solution = copy.deepcopy(solution_courante)
                if meilleure_solution.calculer_distance_total() < fmin:
                    fmin = meilleure_solution.calculer_distance_total()
                    meilleure_solution = copy.deepcopy(solution_courante)
                    print(f"Iteration: {k}.{iterations} Distance: {meilleure_solution.calculer_distance_total()} Température: {temperature} Opérateur: {operateur}")
                    liste_resultats.append(fmin)
                    if meilleure_solution.calculer_distance_total() < global_solution_distance:
                        global_solution_distance = meilleure_solution.calculer_distance_total()
                        global_solution = copy.deepcopy(meilleure_solution)

            else:
                iterations_sans_amelioration += 1
                if random.random() < math.exp(-delta / temperature):
                    meilleure_solution = copy.deepcopy(solution_courante)

            iterations += 1

        temperature *= config.RECUIT_ALPHA

        sauvegarder_solution(meilleure_solution, k)

    print("salut")
    #ecrire_fichier_resultats(liste_resultats)
    print("Réalisation de la courbe")
    show_courbe(liste_resultats)
    return global_solution





def generer_voisins(solution):
    voisins = []
    if "relocate_intra" in config.OPERATEURS:
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

    if "exchange_intra" in config.OPERATEURS:
        # Exchange_intra
        for camion in solution.camions:
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
                        voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])

    # Exchange_extra
    if "exchange_extra" in config.OPERATEURS:
        for camion_i in solution.camions:
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

                                voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])

    if "relocate_extra" in config.OPERATEURS:
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
    if "cross_exchange" in config.OPERATEURS:
        # Cross_exchange
        for camion1 in solution.camions:
            for camion2 in solution.camions:
                if camion1 != camion2:
                    for index1 in range(len(camion1.liste_clients)):
                        for index2 in range(len(camion2.liste_clients)):
                            # Itérer sur différentes longueurs de segments pour camion1 et camion2
                            for len1 in range(0, len(camion1.liste_clients) - index1 + 1):
                                for len2 in range(0, len(camion2.liste_clients) - index2 + 1):
                                    if len1 == 0 and len2 == 0:
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

                                        for camion3 in solution_deepcopy.camions:
                                            if not camion3.liste_clients:
                                                solution_deepcopy.camions.remove(camion3)

                                        operation_inverse = [
                                            f"cross exchange, {[liste_clients1_idName, liste_clients2_idName]}",
                                            f"cross exchange, {[liste_clients2_idName, liste_clients1_idName]}"]
                                        operation_a_faire = [
                                            f"cross exchange, {[liste_clients1_idName, liste_clients2_idName]}"]

                                        voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])
    if "rotate_camion" in config.OPERATEURS:
        # Rotate_camion
        for camion in solution.camions:
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
                voisins.append([solution_deepcopy, operation_inverse, operation_a_faire])



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



def recherche_tabou():
    print("Début de l'algorithme de recherche tabou")
    v = VehicleRouting()
    meilleure_solution = generer_solution_aleatoire(v, config.NOMBRE_CAMIONS)
    afficher_solution(meilleure_solution)
    fmin = meilleure_solution.calculer_distance_total()
    i = 0

    liste_tabou = []
    iterations_sans_amelioration = 0
    liste_resultats = []

    for i in range(config.TABOU_NOMBRE_ITERATIONS):
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
                if len(liste_tabou) > config.TABOU_TAILLE_LISTE_TABOU:
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

    show_courbe(liste_resultats[:30])
    return meilleure_solution

def start():
    open_setup_window()
    list_result = []
    for i in range(config.NOMBRE_LANCERS):
        if config.RECUIT:
            best = recuit_simule()
        elif config.TABOU:
            best = recherche_tabou()
        #afficher_solution(best)
        print(f"Fitness : {best.calculer_distance_total()}")
        list_result.append(best.calculer_distance_total())
    ecrire_fichier_resultats(list_result)