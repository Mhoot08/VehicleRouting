from VehicleRouting import VehicleRouting
from createMap import afficher_solution
from itineraire import *

v = VehicleRouting()
v.read_file('data/data101.vrp')

solution = generer_solution_aleatoire(v, 10)

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
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

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

# Test de voisinage pour tous les trajets 
 #afficher_solution(v)
all_voisins = opt_2(v)
#afficher_solution(v)
# Afficher le voisin qui a la plus petite distance

temp_distance = 10000000
for voisin in all_voisins:
    if voisin.calculer_distance_total() < temp_distance:
        temp_distance = voisin.calculer_distance_total()
    
print(f"PLus petite distance: {temp_distance}")

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
print("Début de l'algorithme de recuit simulé")
solution = generer_solution_aleatoire(v, 8)
afficher_solution(solution)
# liste_camion_opti = []

# # Utilisation de l'algorithme de recuit simulé
# temperature_initiale = 10
# alpha = 0.95
# nombre_iterations = 100000000

# solution_initiale = v
# meilleure_solution = recuit_simule(solution_initiale, temperature_initiale, alpha, nombre_iterations, 100000)
# #meilleure_solution = recuit_simule2(solution_initiale, temperature_initiale)
# v = meilleure_solution
# print(v)
# afficher_solution(v)


# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

# Recherche Tabou

#meilleure_solution = recherche_tabou(v, 10, 1000, 10)
#afficher_solution(meilleure_solution)

s = start_metaheuristique(v)
afficher_solution(s)