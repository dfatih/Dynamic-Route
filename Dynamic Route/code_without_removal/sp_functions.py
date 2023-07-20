import bbox_name_finder as name_finder

import sp_coordinates as sp_coo

import GUI_DIRECTIONS as GUI

import osmnx as ox
import time
import datetime as dt
import ast
import math

TODAY = dt.date.today()

def start_to_dest():
    location = input("Give a starting address: ")
    s_latitude, s_longitude = name_finder.autofill_all_streets(location)
    # print(f"Latitude: {s_latitude}, Longitude: {s_longitude}")

    location = input("Give a destination address: ")
    e_latitude, e_longitude = name_finder.autofill_all_streets(location)
    # print(f"Latitude: {e_latitude}, Longitude: {e_longitude}")
    return (s_latitude, s_longitude), (e_latitude, e_longitude)

def shortest_path_with_directions(G, START, DESTINATION): # This is the node removal method (very bad :| )
    FASTEST_PATH = ox.shortest_path(G, START, DESTINATION, weight='travel_time')
    ###########################-------------------------------------- GET ALL IMPORTANT LISTS FOR DIRECTION
    LAT_LON_LIST = sp_coo.get_lat_lon(G, FASTEST_PATH)
    DISTANCE_LIST = sp_coo.get_dist_list(G, FASTEST_PATH)
    ANGLE_LIST = sp_coo.angle_checker(LAT_LON_LIST)
    ###########################-------------------------------------- GET ALL IMPORTANT LISTS FOR DIRECTION ; 

    DIRECTIONS = sp_coo.dist_and_turn(ANGLE_LIST, DISTANCE_LIST)
    return DIRECTIONS, FASTEST_PATH

def shortest_path_with_directions_NONREM(G, START, DESTINATION, DEPART, ARRIVAL, CONDITIONS):
    # 1: SP berechnen
    FASTEST_PATH = ox.shortest_path(G, START, DESTINATION, weight='travel_time')
    # 2: check all conditions to avoid
    FASTEST_PATH, DEP, ARR = check_all_cond(G, FASTEST_PATH, CONDITIONS, DEPART, ARRIVAL, START, DESTINATION)
    ###########################-------------------------------------- GET ALL IMPORTANT LISTS FOR DIRECTION
    LAT_LON_LIST = sp_coo.get_lat_lon(G, FASTEST_PATH)
    DISTANCE_LIST = sp_coo.get_dist_list(G, FASTEST_PATH)
    ANGLE_LIST = sp_coo.angle_checker(LAT_LON_LIST)
    ###########################-------------------------------------- GET ALL IMPORTANT LISTS FOR DIRECTION ; 

    DIRECTIONS = sp_coo.dist_and_turn(ANGLE_LIST, DISTANCE_LIST)
    return DIRECTIONS, FASTEST_PATH, DEP, ARR, get_travel_time_FP(G, FASTEST_PATH, 1)

def check_all_cond(G, FASTEST_PATH, CONDITIONS, DEPART, ARRIVAL, START, DESTINATION): # part of NONREM
    # 2.1: if node es occure, that cant be in the route, then this node shall be added to the list beneath and needs to be removed from G
    # repeat until list is empty 
    #print(DEPART, ARRIVAL)
    LIST_TO_REM_FROM_G = []
    LIVE_DATE = DEPART - TODAY
    #print(LIVE_DATE)
    MAX_DATE = ARRIVAL - TODAY
    #print(MAX_DATE)
    TIME_NEEDED_FOR_FP = get_travel_time_FP(G, FASTEST_PATH) # rounded down because 0h-24h is within a day (meaning 0 days total needed)
    #print(TIME_NEEDED_FOR_FP)
    LIVE_TIME_NEEDED = TIME_NEEDED_FOR_FP
    while CONDITIONS != []:
        LIVE_COND = CONDITIONS[0]
        CONDITIONS.pop(0)
        while LIVE_DATE + dt.timedelta(days=TIME_NEEDED_FOR_FP) <= MAX_DATE:
            DELETE_Y_N = False
            for n in FASTEST_PATH:
                W_DATA = G.nodes[n]['weather']
                if isinstance(W_DATA, str): # this is important, because at one time the user downloades the first time ever and another time he uses already a graph downloaded before
                    W_DATA = ast.literal_eval(W_DATA)
                if LIVE_COND == 'Rain':
                    if W_DATA['rain_sum'][LIVE_DATE.days] == None:
                        LIVE_DATE += dt.timedelta(days=1)
                        DELETE_Y_N = True
                        if n not in LIST_TO_REM_FROM_G:
                            LIST_TO_REM_FROM_G.append(n) # potentially this node is a threat
                        break # this is needed because altering the LIVE_DATE can cause problems with nodes, that where "safe" before
                if LIVE_COND == 'Frost':
                    if W_DATA['temperature_2m_min'][LIVE_DATE.days] == None:
                        LIVE_DATE += dt.timedelta(days=1)
                        DELETE_Y_N = True
                        if n not in LIST_TO_REM_FROM_G:
                            LIST_TO_REM_FROM_G.append(n)
                        break
                if LIVE_COND == 'Snow':
                    if W_DATA['snowfall_sum'][LIVE_DATE.days] == None:
                        LIVE_DATE += dt.timedelta(days=1)
                        DELETE_Y_N = True
                        if n not in LIST_TO_REM_FROM_G:
                            LIST_TO_REM_FROM_G.append(n)
                        break
                if LIVE_COND == 'Wind':
                    if W_DATA['windspeed_10m_max'][LIVE_DATE.days] == None:
                        LIVE_DATE += dt.timedelta(days=1)
                        DELETE_Y_N = True
                        if n not in LIST_TO_REM_FROM_G:
                            LIST_TO_REM_FROM_G.append(n)
                        break
            # 2.2: delete all nodes if needed and if there was no node to delete, then we would have a working route :)
            if LIST_TO_REM_FROM_G == [] and LIVE_TIME_NEEDED == 0: # if inspected days have no None
                break # this means that for a certain restrictions all nodes comply
            if LIVE_TIME_NEEDED == 0 and DELETE_Y_N == False: # if we appended but we have a days where it still works
                break # this means that for a certain restrictions all nodes comply
            if LIVE_TIME_NEEDED != 0:
                LIVE_TIME_NEEDED -= 1
            G.remove_nodes_from(LIST_TO_REM_FROM_G)
            try:
                FASTEST_PATH = ox.shortest_path(G, START, DESTINATION, weight='travel_time')
                TIME_NEEDED_FOR_FP = get_travel_time_FP(G, FASTEST_PATH)
            except:
                print("No route was possible to make, due to restrictions!")
                return
        LIVE_TIME_NEEDED = TIME_NEEDED_FOR_FP
        LIVE_DATE = DEPART - TODAY
    DEPART = DEPART + dt.timedelta(days=LIVE_DATE.days)
    ARRIVAL = DEPART + dt.timedelta(days=TIME_NEEDED_FOR_FP)

    return FASTEST_PATH, DEPART, ARRIVAL

def plot_route(G, FASTEST_PATH):
    plot_s = time.time()
    ox.plot_graph_route(G, FASTEST_PATH, filepath=f'./start_to_dest.svg', save=True, node_size = 0, edge_linewidth = 0.1, route_linewidth=0.5, route_alpha=0.5, orig_dest_size=10, ax=None)
    plot_e = time.time() - plot_s

    print(f"Time for plotting was: {plot_e}s")

def streetnames(G, FASTEST_PATH):
    names = []
    for i in range(0, len(FASTEST_PATH) - 1):
        edge_data = G.get_edge_data(FASTEST_PATH[i], FASTEST_PATH[i + 1])
        #print(edge_data)
        name = edge_data[0]['name']
        names.append(name)
    return names

def give_direction_with_GUI(DIRECTIONS, G, FASTEST_PATH):
    STRAIGHT_COUNTER = 0
    FOR_GUI = []
    G = name_finder.name_place_all_streets(G, FASTEST_PATH) # finds edges. that didn't hat any stree name due to formating an other stuff
    NAMES = streetnames(G, FASTEST_PATH)
    LOCAL_I = 0
    for i in DIRECTIONS:
        #print(NAMES[LOCAL_I])
        if i[1] == "Straight":
            STRAIGHT_COUNTER += i[0]
            LOCAL_I += 1
            """if LOCAL_I != 0:
                if NAMES[LOCAL_I - 1] == NAMES[LOCAL_I]:
                    LOCAL_I += 1
                    continue
                TEXT = f"Drive straight on: {NAMES[LOCAL_I]}"
                #print(f"Drive {round(i[0] + STRAIGHT_COUNTER, 1)}m straight to destination \n")
                FOR_GUI.append((TEXT, "Straight"))
                LOCAL_I += 1"""
        elif i[1] == "Straight_To_Destination":
            TEXT = f"Drive {round(i[0] + STRAIGHT_COUNTER, 1)}m straight to destination"
            #print(f"Drive {round(i[0] + STRAIGHT_COUNTER, 1)}m straight to destination \n")
            FOR_GUI.append((TEXT, "Straight"))
        else:
            TEXT = f"Make {i[1]} turn from: {NAMES[LOCAL_I]} into: {NAMES[LOCAL_I + 1]} in {round(i[0] + STRAIGHT_COUNTER, 1)}m"
            #print(f"Turn {i[1]} in {round(i[0] + STRAIGHT_COUNTER, 1)}m \n")
            FOR_GUI.append((TEXT, i[1]))
            STRAIGHT_COUNTER = 0
            LOCAL_I += 1
    GUI.create_GUI_directions(FOR_GUI, G, FASTEST_PATH)
    return

def get_travel_time_FP(G, FASTEST_PATH, val=0):
    IN_SECONDS = 0
    for n in range(0, len(FASTEST_PATH) - 1):
        IN_SECONDS += G[FASTEST_PATH[n]][FASTEST_PATH[n + 1]][0]['travel_time']
    IN_DAYS = (IN_SECONDS / 86400) # / 60 / 60 / 24
    if val == 0: # is needed for the condition checking and live_date tracking
        return math.floor(IN_DAYS)
    return IN_SECONDS