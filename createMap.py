import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import random

def afficher_solution(vehicle_routing):
    plt.figure(figsize=(14, 8))

    # Couleurs aléatoires pour chaque camion
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']  # Vous pouvez ajouter plus de couleurs si nécessaire
    random.shuffle(colors)

    # Affichage des dépôts
    for depot in vehicle_routing.depots:
        plt.plot(depot.x, depot.y, 'ro', markersize=25, label='Depot')

    # Affichage des clients
    # for client in vehicle_routing.clients:
    #     print(client.idName)
    #     plt.plot(client.x, client.y, 'bo', markersize=25, markeredgewidth=2, markeredgecolor='black', alpha=1, fillstyle='none')
    #     plt.text(client.x, client.y, client.idName, fontsize=15)

    # Affichage des trajets
    for i, camion in enumerate(vehicle_routing.camions):
        color = colors[i % len(colors)]  # Utilisation des couleurs aléatoires
        # Affichage des clients
        for client in camion.liste_clients:
            plt.plot(client.x, client.y, 'o', markersize=25, markeredgewidth=2, markeredgecolor=color, alpha=1,
                     fillstyle='none', color=color)
            plt.text(client.x, client.y, client.idName, fontsize=15)
        trajets = camion.createTrajets(vehicle_routing.clients, vehicle_routing.depots[0])

        for trajet in trajets:
            depart, arrivee = trajet[0], trajet[1]
            arrow = FancyArrowPatch((depart.x, depart.y), (arrivee.x, arrivee.y),
                                    arrowstyle='-|>', mutation_scale=30, color=color)
            plt.gca().add_patch(arrow)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Visualisation du problème de VRP')
    plt.legend()
    plt.grid(True)
    plt.show()