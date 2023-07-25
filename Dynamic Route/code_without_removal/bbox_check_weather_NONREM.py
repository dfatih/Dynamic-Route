import networkx as nx
import time
import datetime as dt
import ast
import os
import osmnx as ox

TODAY = dt.date.today()

def validate_dates(INPUT1, INPUT2):
    # Check if the input date is in the past
    if INPUT1 < TODAY or INPUT2 < TODAY:
        return False
    
    # Calculate the difference between the input date and today's date
    DIFF1 = INPUT1 - TODAY
    DIFF2 = INPUT2 - TODAY

    # Check if the difference is within the allowed range
    if DIFF1 <= dt.timedelta(days=7) and DIFF2 <= dt.timedelta(days=7):
        return True
    else:
        return False
    
def which_condition():
    os.system('cls')
    CONDITION_LIST = []
    POSSIBILITIES = ["Rain", "Frost", "Snow", "Wind", "ALL", "Stop conditions"]
    CONDITIONS = ""
    
    while (len(POSSIBILITIES) != 1):
        print(f"Type in, what you want to avoid, until now you have: {CONDITION_LIST}")
        for i in range(0, len(POSSIBILITIES)):
            print(f"[{i + 1}] {POSSIBILITIES[i]}")

        CONDITIONS = input()
        if POSSIBILITIES[-2] == "ALL" and int(CONDITIONS) == len(POSSIBILITIES) - 1:
            os.system('cls')
            print(f"All conditions will be included: [Rain, Frost, Snow, Wind]")
            CONDITION_LIST.append(POSSIBILITIES[0])
            CONDITION_LIST.append(POSSIBILITIES[1])
            CONDITION_LIST.append(POSSIBILITIES[2])
            CONDITION_LIST.append(POSSIBILITIES[3])
            break
        if int(CONDITIONS) < len(POSSIBILITIES) and int(CONDITIONS) > 0:
            CONDITION_LIST.append(POSSIBILITIES[int(CONDITIONS) - 1])
            os.system('cls')
            print(f"{POSSIBILITIES[int(CONDITIONS) - 1]} was added! :) \n")
            POSSIBILITIES.pop(int(CONDITIONS) - 1)
            if POSSIBILITIES[-2] == "ALL":
                POSSIBILITIES.pop(-2)
            continue
        if int(CONDITIONS) == len(POSSIBILITIES):
            os.system('cls')
            print(f"Following conditions will be avoided: {CONDITION_LIST}")
            break
        if CONDITIONS == "remove": # for future?
            print("//TODO")
        
        os.system('cls')
        print(f"{CONDITIONS} is not valid .. \n")

    if len(POSSIBILITIES) == 1:
        print("All conditions added, this might take a while...")
    return CONDITION_LIST

def get_date(ANNOUNCE):
    DATE_ENTRY = input(f'{ANNOUNCE} in DD.MM.YYYY format: ')
    D, M, Y = map(int, DATE_ENTRY.split('.'))
    DATE = dt.date(Y, M, D)
    return DATE

def condition_executer(DEPART, ARRIVAL, G, CONDITION_LIST):
    GRAPH_COPY = G.copy()
    while CONDITION_LIST != []:
        if 'Rain' in CONDITION_LIST:
            CONDITION_LIST.remove('Rain')
            GRAPH_COPY = check_rain(GRAPH_COPY, DEPART, ARRIVAL)
        if 'Frost' in CONDITION_LIST:
            CONDITION_LIST.remove('Frost')
            GRAPH_COPY = check_frost(GRAPH_COPY, DEPART, ARRIVAL)
        if 'Snow' in CONDITION_LIST:
            CONDITION_LIST.remove('Snow')
            GRAPH_COPY = check_snow(GRAPH_COPY, DEPART, ARRIVAL)
        if 'Wind' in CONDITION_LIST:
            CONDITION_LIST.remove('Wind')
            GRAPH_COPY = check_wind(GRAPH_COPY, DEPART, ARRIVAL)
    return GRAPH_COPY

def check_rain(G, DEPART, ARRIVAL):
    GRAPH = G.copy()
    # Calculate the difference between the input date and today's date
    DIFF = DEPART.day - TODAY.day
    for u, data in GRAPH.nodes(data=True):
        SET = False
        W_DATA = data['weather']
        if isinstance(W_DATA, str): # this is important, because at one time the user downloades the first time ever and another time he uses already a graph downloaded before
            W_DATA = ast.literal_eval(W_DATA)
        while DIFF <= (ARRIVAL - TODAY).days:
            if W_DATA['rain_sum'][DIFF] != None and W_DATA['rain_sum'][DIFF] > 1:
                W_DATA['rain_sum'][DIFF] = None
                SET = True
            DIFF += 1
        if SET == True:
            nx.set_node_attributes(G, {u: W_DATA}, name="weather")
    return GRAPH

def check_snow(G, DEPART, ARRIVAL):
    GRAPH = G.copy()
    # Calculate the difference between the input date and today's date
    DIFF = DEPART.day - TODAY.day
    for u, data in GRAPH.nodes(data=True):
        SET = False
        W_DATA = data['weather']
        if isinstance(W_DATA, str): # this is important, because at one time the user downloades the first time ever and another time he uses already a graph downloaded before
            W_DATA = ast.literal_eval(W_DATA)
        while DIFF <= (ARRIVAL - TODAY).days:
            if W_DATA['rain_sum'][DIFF] != None and W_DATA['snowfall_sum'][DIFF] > 0.5:
                W_DATA['snowfall_sum'][DIFF] = None
                SET = True
            DIFF += 1
        if SET == True:
            nx.set_node_attributes(G, {u: W_DATA}, name="weather")
    return GRAPH

def check_wind(G, DEPART, ARRIVAL):
    GRAPH = G.copy()
    # Calculate the difference between the input date and today's date
    DIFF = DEPART.day - TODAY.day
    for u, data in GRAPH.nodes(data=True):
        SET = False
        W_DATA = data['weather']
        if isinstance(W_DATA, str): # this is important, because at one time the user downloades the first time ever and another time he uses already a graph downloaded before
            W_DATA = ast.literal_eval(W_DATA)
        while DIFF <= (ARRIVAL - TODAY).days:
            if W_DATA['rain_sum'][DIFF] != None and W_DATA['windspeed_10m_max'][DIFF] > 39:
                W_DATA['windspeed_10m_max'][DIFF] = None
                SET = True
            DIFF += 1
        if SET == True:
            nx.set_node_attributes(G, {u: W_DATA}, name="weather")
    return GRAPH

def check_frost(G, DEPART, ARRIVAL):
    GRAPH = G.copy()
    # Calculate the difference between the input date and today's date
    DIFF = DEPART.day - TODAY.day
    for u, data in GRAPH.nodes(data=True):
        SET = False
        W_DATA = data['weather']
        if isinstance(W_DATA, str): # this is important, because at one time the user downloades the first time ever and another time he uses already a graph downloaded before
            W_DATA = ast.literal_eval(W_DATA)
        while DIFF <= (ARRIVAL - TODAY).days:
            if W_DATA['rain_sum'][DIFF] != None and W_DATA['temperature_2m_min'][DIFF] < 0:
                W_DATA['temperature_2m_min'][DIFF] = None
                SET = True
            DIFF += 1
        if SET == True:
            nx.set_node_attributes(G, {u: W_DATA}, name="weather")
    return GRAPH

def w_main_exec(G):
    ###########################-------------------------------------CHECK WEATHER CONDITONS
    DATE_S, DATE_E = get_date("Enter starting Date (you can only check the weather for 7 days in advance)"), get_date("Enter Date of last possible arrival")
    if validate_dates(DATE_S, DATE_E):
        COND_LIST = which_condition()
        COND_LIST_ROUTE = COND_LIST.copy()
        print(f"Starting to realise weather conditions onto our route \n")

        WT_CON_S = time.time()
        WEATHER_G = condition_executer(DATE_S, DATE_E, G, COND_LIST)
        WT_CON_E = time.time() - WT_CON_S
        print(f"Time needed for weather conditions to be realised: {WT_CON_E}")
        if len(WEATHER_G.nodes) > 0 and len(WEATHER_G.edges) > 0:
            return WEATHER_G, COND_LIST_ROUTE, DATE_S, DATE_E
        print("Graph is emtpy due to all nodes have a condition .. closing")
        time.sleep(5)
        quit()
    else:
        print("Could not do a forcast ... given dates not suitable try again .. \n\n")
        time.sleep(2)
        return w_main_exec(G)
    ###########################-------------------------------------CHECK WEATHER CONDITONS ;

if __name__ == "__main__": 
    FILE_PATH = "./graphNONREM/berlin_drive_network-osmnx.graphml"
    GRAPH = ox.load_graphml(filepath = FILE_PATH)
    w_main_exec(GRAPH)
