import matplotlib.pyplot as plt

def afficher_solution(vehicle_routing):
    plt.figure(figsize=(10, 6))

    # Affichage des dépôts
    for depot in vehicle_routing.depots:
        plt.plot(depot.x, depot.y, 'ro', markersize=15, label='Depot')

    # Affichage des clients
    for client in vehicle_routing.clients:
        plt.plot(client.x, client.y, 'bo', markersize=8)
        plt.text(client.x, client.y, client.idName, fontsize=8)

    # Affichage des trajets
    for camion in vehicle_routing.camions:
        trajets = camion.createTrajets(vehicle_routing.clients, vehicle_routing.depots[0])
        for trajet in trajets:
            depart, arrivee = trajet[0], trajet[1]
            plt.arrow(depart.x, depart.y, arrivee.x - depart.x, arrivee.y - depart.y,
                      head_width=1, head_length=1, fc='k', ec='k')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Visualisation du problème de VRP')
    plt.legend()
    plt.grid(True)
    plt.show()
