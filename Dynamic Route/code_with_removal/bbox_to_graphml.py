import osmnx as ox
import time

import bbox_graph_functions as graph_func


import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

def fetch_graph():
    # GROB! Bounding box coordinates for Berlin-Brandenburg
    north = graph_func.north
    south = graph_func.south
    east = graph_func.east
    west = graph_func.west
    # Fetch the road network data with turn restrictions using osmnx
    #print(Style.BRIGHT+Fore.YELLOW+"Downloading Graph of Place: \n")

    #save_graph_s = time.time()
    DOWNLOAD_S = time.time()
    ##############################-------------DOWNLOAD GRAPH
    G = ox.graph_from_bbox(north, south, east, west, network_type = 'drive', simplify=True)
    ##############################-------------DOWNLOAD GRAPH ;
    DOWNLOAD_E = time.time() - DOWNLOAD_S
    # Check if the graph contains any nodes and edges
    if len(G.nodes) > 0 and len(G.edges) > 0:
        print("Road network data with turn restrictions retrieved successfully.")

        ##############################-------------EDGE SPEEDS | TRAVEL TIMES
        print("Add edge speeds + travel times")

        edge_speed_s = time.time()
        GRAPH = ox.add_edge_speeds(G)
        edge_speed_e = time.time() - edge_speed_s 

        edge_travel_s = time.time()
        GRAPH = ox.add_edge_travel_times(GRAPH)
        edge_travel_e = time.time() - edge_travel_s

        print(f"Done, \nTime needed add_edge_speeds: {edge_speed_e}, \nTime needed add_edge_travel_times: {edge_travel_e} \n")
        ##############################-------------EDGE SPEEDS | TRAVEL TIMES ; 
        print(f"Graph hat: {DOWNLOAD_E} gebraucht zum downloaden. \n")
        ##############################-------------SAVE GRAPH
        ox.save_graphml(GRAPH, filepath='./graphNONREM/berlin_drive_network-osmnx.graphml')  # changed path !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ##############################-------------SAVE GRAPH ; 
        return GRAPH


        #save_graph_e = time.time() - save_graph_s

        #print(f"Graph hat: {save_graph_e} gebraucht zum downloaden und speichern. \n")
    else:
        print("No road network data with turn restrictions available for the specified bounding box.")