from VehicleRouting import VehicleRouting
from createMap import afficher_solution
from itineraire import *

v = VehicleRouting()
v.read_file('data/data101.vrp')

solution = generer_solution_aleatoire_opti(v)
for camion in solution:
    # sauvegarder les camions dans le vehicle routing
    v.camions.append(camion)

# # On fait ça seulement pour un camion qui a plus de 3 clients
# for i in range(len(v.camions)):
#     if len(v.camions[i].liste_clients) > 2:
#         # On crée un nouveau camion
#         v.camions = [v.camions[i]]
#         # On supprime les clients du nouveau camion dans le camion initial
#         v.clients = v.camions[0].liste_clients
#         break

# afficher_solution(v)
# v.camions = exchange_intra(v.camions)
#v.camions = opt_2(v.camions)
# afficher_solution(v)

# On fait la transformation exchange extra


# temp_camions = []
# # On prend 2 camions aléatoirement qui ont plus de 2 clients
# for i in range(len(v.camions)):
#     if len(v.camions[i].liste_clients) > 2:
#         print(f"i: {i}")
#         # On crée un nouveau camion
#         temp_camions.append(v.camions[i])
#         print(f"temp_camions: {temp_camions}")
#         # On supprime les clients du nouveau camion dans le camion initial
#         v.clients = v.camions[0].liste_clients
#         if len(temp_camions) == 2:
#             v.camions = temp_camions
#             break
#
# for camion in v.camions:
#     print(camion.liste_clients)
#     for client in camion.liste_clients:
#         print(f"main : {client.idName}")
#
# afficher_solution(v)
# v.camions = exchange_extra(v.camions)
# afficher_solution(v)

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

# Recuit simulé
afficher_solution(v)
liste_camion_opti = []
for camion in v.camions:
    all_voisins = get_voisins(camion)

    # Utilisation de l'algorithme de recuit simulé
    temperature_initiale = 1000
    alpha = 0.95
    nombre_iterations = 1000

    solution_initiale = camion
    meilleure_solution = recuit_simule(solution_initiale, temperature_initiale, alpha, nombre_iterations)
    liste_camion_opti.append(meilleure_solution)
v.camions = liste_camion_opti
afficher_solution(v)





