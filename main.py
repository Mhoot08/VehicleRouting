from VehicleRouting import VehicleRouting
from createMap import afficher_solution
from itineraire import *

v = VehicleRouting()
v.read_file('data/data101.vrp')

print(v.getNbMinVehicle())

solution = generer_solution_aleatoire(v)
for camion in solution:
    # sauvegarder les camions dans le vehicle routing
    v.camions.append(camion)

for camion in v.camions:
    print(camion.createTrajets(v.clients, v.depots[0]))

afficher_solution(v)
