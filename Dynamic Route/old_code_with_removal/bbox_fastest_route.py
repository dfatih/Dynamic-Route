import bbox_graph_functions as graph_func
import bbox_check_weather as check_weather
import bbox_weather_fetcher as weather_fetch

import sp_functions as sp_func

import networkx as nx
import osmnx as ox
import time

WEATHER_S = time.time() # MEASURE TIME NEEDED FOR PROCESSING
###########################-------------------------------------------LOAD GRAPH
G = graph_func.load_graph()
###########################-------------------------------------------LOAD GRAPH ;

########################### -------------------------------------- TURNRESTRICTIONS DELETION
G = graph_func.map_turn_restrictions(G)
########################### -------------------------------------- TURNRESTRICTIONS DELETION ;

########################### -------------------------------------- MAPPING WEATHER_DATA AND PROHIBITED AREA
G_MAPPED = weather_fetch.map_weather(G)
########################### -------------------------------------- MAPPING WEATHER_DATA AND PROHIBITED AREA ;
WEATHER_E = time.time() - WEATHER_S
print(f"Total time loading and mapping: {WEATHER_E}")

#^^^^^^^^^^^^^^^^^^^^^^^^^^-----------------DIE WHILE LOOP SOLLTE HIER STARTEN: Unendlich routen bis user z.B. q eingibt
###########################-------------------------------------------FINDING PLACE
APPROX_START, APPROX_END = sp_func.start_to_dest()
###########################-------------------------------------------FINDING PLACE ;

###########################-------------------------------------- DEFINE START AND END ON THE ROAD AND DATE_REGION
WEATHER_G = check_weather.w_main_exec(G_MAPPED)
START, DESTINATION  = graph_func.find_neares_S_D(WEATHER_G, APPROX_START, APPROX_END)
###########################-------------------------------------- DEFINE START AND END ON THE ROAD AND DATE_REGION ;

###########################--------------------------------------SHORTEST PATH MIT LA DIRECTION
print("\n")
DIRECTIONS, FASTEST_PATH = sp_func.shortest_path_with_directions(WEATHER_G, START, DESTINATION) # removing nodes
sp_func.give_direction_with_GUI(DIRECTIONS, G, FASTEST_PATH) # also startsup the GUI
#^^^^^^^^^^^^^^^^^^^^^^^^^^-----------------DIE WHILE LOOP SOLLTE HIER ENDEN

GRAPH_SAVE_S = time.time()
##############################-------------SAVE WEATHER GRAPH
ox.save_graphml(G_MAPPED, filepath='./graph/berlin_drive_network-osmnx-wetter.graphml')
##############################-------------SAVE WEATHER GRAPH ; 
GRAPH_SAVE_E = time.time() - GRAPH_SAVE_S

print(f"Time for save: {GRAPH_SAVE_E}")