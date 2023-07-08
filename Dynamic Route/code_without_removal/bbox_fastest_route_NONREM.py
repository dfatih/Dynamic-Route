import bbox_check_weather_NONREM as check_weather_NONREM
import bbox_weather_fetcher as weather_fetch
import GUI_DIRECTIONS as GUI
import bbox_graph_functions as graph_func


import sp_functions as sp_func

import networkx as nx
import osmnx as ox
import time

import os

from tqdm.auto import tqdm
from cprint import *
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

print("\n \n \n \n \n \n \n \n \n")

print(Style.BRIGHT+Fore.CYAN+"Starting Programm....  \n")
for i in tqdm(range(3100)):
    print("", end='\r')
os.system('cls')

cprint(Style.BRIGHT+Fore.CYAN+"""
    ____                              _         ____              __   
   / __ \__  ______  ____ _____ ___  (_)____   / __ \____  __  __/ /____
  / / / / / / / __ \/ __ `/ __ `__ \/ / ___/  / /_/ / __ \/ / / / __/ _ \

 / /_/ / /_/ / / / / /_/ / / / / / / / /__   / _, _/ /_/ / /_/ / /_/  __/
/_____/\__, /_/ /_/\__,_/_/ /_/ /_/_/\___/  /_/ |_|\____/\__,_/\__/\___/
      /____/
    ____  __                  _
   / __ \/ /___ _____  ____  (_)___  ____ _
  / /_/ / / __ `/ __ \/ __ \/ / __ \/ __ `/
 / ____/ / /_/ / / / / / / / / / / / /_/ /
/_/   /_/\__,_/_/ /_/_/ /_/_/_/ /_/\__, /
                                  /____/ by Nils, Robert, Krzysztof, Nikita



""")

WEATHER_S = time.time() # MEASURE TIME NEEDED FOR PROCESSING
###########################-------------------------------------------LOAD GRAPH
G = graph_func.loader()
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
print("If you want to calculate a route please press any button except q ")
QUIT_Y_N = GUI.get_input()# input("If you want to calculate a route please press any button accept q: ")
while(QUIT_Y_N != "q"):
    ###########################-------------------------------------------FINDING PLACE
    APPROX_START, APPROX_END = sp_func.start_to_dest()
    ###########################-------------------------------------------FINDING PLACE ;

    ###########################-------------------------------------- DEFINE START AND END ON THE ROAD AND DATE_REGION
    WEATHER_G, CONDITIONS, DEPART, ARRIVAL = check_weather_NONREM.w_main_exec(G_MAPPED)
    #WEATHER_G = check_weather.w_main_exec(G_MAPPED) # removing nodes
    START, DESTINATION  = graph_func.find_neares_S_D(WEATHER_G, APPROX_START, APPROX_END)
    ###########################-------------------------------------- DEFINE START AND END ON THE ROAD AND DATE_REGION ;

    ###########################--------------------------------------SHORTEST PATH MIT LA DIRECTION
    print("\n")
    # 3: return possible route with real starting date and ending date
    DIRECTIONS, FASTEST_PATH, DEP, ARR, TIME_NEEDED = sp_func.shortest_path_with_directions_NONREM(WEATHER_G, START, DESTINATION, DEPART, ARRIVAL, CONDITIONS)
    ### TIME CONVERTER
    R_TIME = TIME_NEEDED * 1.3
    IN_SECONDS = int(R_TIME) % 60
    IN_MINUTES = int((R_TIME // 60) % 60)
    IN_HOURS = int((R_TIME // 3600) % 24)
    IN_DAYS = int(R_TIME // (3600 * 24))
    TIME_STR = ""  # String to store the result

    if IN_DAYS > 0:
        TIME_STR += str(IN_DAYS) + " days, "
    if IN_HOURS > 0:
        TIME_STR += str(IN_HOURS) + " hours, "
    if IN_MINUTES > 0:
        TIME_STR += str(IN_MINUTES) + " minutes, "
    if IN_SECONDS > 0:
        TIME_STR += str(IN_SECONDS) + " seconds"

    TIME_STR = TIME_STR.rstrip(", ")

    #print(TIME_STR)
    ### TIME CONVERTER ;
    print(f"Earliest departure possible: {DEP.day}.{DEP.month}.{DEP.year} and earliest arrival: {ARR.day}.{ARR.month}.{ARR.year}, estimated time {TIME_STR}: ")
    #DIRECTIONS, FASTEST_PATH = sp_func.shortest_path_with_directions(WEATHER_G, START, DESTINATION) # removing nodes
    sp_func.give_direction_with_GUI(DIRECTIONS, G, FASTEST_PATH) # also startsup the GUI
    print("If you want to calculate a route please press any button except q ")
    QUIT_Y_N = GUI.get_input()# input("If you want to calculate a route please press any button accept q: ")
    #^^^^^^^^^^^^^^^^^^^^^^^^^^-----------------DIE WHILE LOOP SOLLTE HIER ENDEN
CREATE_TIME = os.path.getmtime('./graphNONREM/berlin_drive_network-osmnx-wetter.graphml')
CURR_TIME = time.time()

if os.path.getsize('./graphNONREM/berlin_drive_network-osmnx-wetter.graphml') // 1024 == 0 or CURR_TIME - CREATE_TIME >= 86400:
    print(Style.BRIGHT+Fore.YELLOW+"Saving graph! \n")
    GRAPH_SAVE_S = time.time()
    ##############################-------------SAVE WEATHER GRAPH
    ox.save_graphml(G_MAPPED, filepath='./graphNONREM/berlin_drive_network-osmnx-wetter.graphml')  # or for instant remove: "./graph/berlin_drive_network-osmnx.graphml"
    ##############################-------------SAVE WEATHER GRAPH ; 
    GRAPH_SAVE_E = time.time() - GRAPH_SAVE_S
    print(f"Time for save: {GRAPH_SAVE_E}\n")

print(Style.BRIGHT+Fore.RED+"Closing... \n")
time.sleep(10)