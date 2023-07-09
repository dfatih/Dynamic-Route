import osmnx as ox
import osmnx.distance as ox_dist
import requests
import time
import os.path as path

import bbox_to_graphml as graphml

from rich.console import Console
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

# Add the Loader class here
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

class Loader2:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.01):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ['|', '/', '-', '\\', '|', '/', '-', '\\']
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                print(f"", flush=True, end="")
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)
        return

# GROB! Bounding box coordinates for Berlin-Brandenburg
north = 53.5579500214
south = 52.33806627053
east = 14.7647105012
west = 12.2681664447

class CustomException(Exception):
    pass
            
console = Console()
tasks = [f"dummytask {n}" for n in range(1, 11)] # for later development in frontend (just for show)

def animate_loading(task):
    time.sleep(1)
    console.log(f"{task} complete")

def loader(): 
    print("Preparing loader: ")
    with console.status("[bold green]Working on tasks...") as status:
        while tasks:
            task = tasks.pop(0)
            time.sleep(0.15)
            console.log(f"{task} complete")

def load_graph():
    FILE_PATH = "./graphNONREM/berlin_drive_network-osmnx.graphml" # or for instant remove: "./graph/berlin_drive_network-osmnx.graphml"
    print(Style.BRIGHT+Fore.YELLOW+"Start graph loading! \n")
    try:
        CREATE_TIME = path.getmtime(FILE_PATH)
        CURR_TIME = time.time()
        #print(CREATE_TIME, CURR_TIME, CURR_TIME - CREATE_TIME)
        if path.getsize(FILE_PATH) // 1024 == 0 or CURR_TIME - CREATE_TIME >= 86400:
            print("Graph data is older than a day or empty ... refetching")
            raise CustomException("Graph data needs to be refetched")
        
        loader = Loader2("Load Graph from Memory...")
        loader.start()
        #print(Style.BRIGHT+Fore.YELLOW+"Load Graph from Memory ...")
        G_S = time.time()
        GRAPH = ox.load_graphml(filepath = FILE_PATH)
        G_E = time.time() - G_S
        loader.done = True

        print('\n')

        print(Style.BRIGHT+Fore.GREEN+f"Graph Loaded, Time needed: {G_E}")
        return GRAPH
    except CustomException:
        loader2 = Loader2("Downloading Graph from bounding box...")
        loader2.start()
        DOWNLOAD_S = time.time()
        GRAPH = graphml.fetch_graph()
        loader2.done = True
        DOWNLOAD_E = time.time() - DOWNLOAD_S
        print('\n\n')
        print(Style.BRIGHT+Fore.GREEN+f"Graph Downloaded and saved, Time needed: {DOWNLOAD_E}")
        return GRAPH
    except:
        loader3 = Loader2("Downloading Graph from bounding box...")
        loader3.start()
        DOWNLOAD_S = time.time()
        GRAPH = graphml.fetch_graph()
        loader3.done = True
        DOWNLOAD_E = time.time() - DOWNLOAD_S
        print('\n\n')
        print(Style.BRIGHT+Fore.GREEN+f"Graph Downloaded and saved, Time needed: {DOWNLOAD_E}")
        return GRAPH

def map_turn_restrictions(G):
    remove_turn_res_s = time.time()
    ###########################--------------------------------------QUERY TO FETCH RESTRICTION TYPE
    query = f"""
        [out:json];
        (
            relation["type"="restriction"]["restriction"~"no_(left_turn|right_turn|straight_on|u_turn)"]({south}, {west}, {north}, {east});
            way["type"="restriction"]["restriction"~"no_(left_turn|right_turn|straight_on|u_turn)"]({south}, {west}, {north}, {east});
            node["type"="restriction"]["restriction"~"no_(left_turn|right_turn|straight_on|u_turn)"]({south}, {west}, {north}, {east});
        );
        (._;>;);
        out body;
        >;
        out skel qt;
        """.format(north=north, south=south, east=east, west=west)
    ###########################--------------------------------------QUERY TO FETCH RESTRICTION TYPE ;

    ###########################--------------------------------------RESPONSE FROM OVERPASS-API
    response = requests.get(f"http://overpass-api.de/api/interpreter?data={query}")
    data = response.json()
    ###########################--------------------------------------RESPONSE FROM OVERPASS-API ;

    turn_restriction_data = data['elements']

    ###########################--------------------------------------RESTRICTION MAPPING TO ORIGINAL GRAPH
    turnres_del = 0
    for restriction in turn_restriction_data:
        if restriction['type'] == 'relation':
            if len(restriction['members']) != 3:
                members = restriction['members']

                from_edge = None
                via_node = None
                to_edge = None
                for member in members:
                    if member['role'] == 'from':
                        from_edge = member['ref']
                    if member['role'] == 'via':
                        via_node = member['ref']
                    if member['role'] == 'to':
                        to_edge = member['ref']
                for u, v, data in G.edges(data=True):
                    if isinstance(data['osmid'], int):
                        continue
                    if u == via_node:
                        if (from_edge in data['osmid'] and to_edge in data['osmid']):
                            data['osmid'].remove(to_edge)
                            turnres_del += 1
    ###########################--------------------------------------RESTRICTION MAPPING TO ORIGINAL GRAPH ;

    remove_turn_res_e = time.time() - remove_turn_res_s

    print(f"\nTime needed for Mapping: {remove_turn_res_e}")
    print(f"Turnrestrictions checked and removed : {turnres_del}\n")
    return G

def find_neares_S_D(G, START, DESTINATION):
    nearest_start = ox_dist.nearest_nodes(G, START[1], START[0], return_dist=False)
    nearest_dest = ox_dist.nearest_nodes(G, DESTINATION[1], DESTINATION[0], return_dist=False)    
    return nearest_start, nearest_dest
