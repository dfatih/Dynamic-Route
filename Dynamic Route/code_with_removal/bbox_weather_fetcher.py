import requests
import osmnx as ox
import networkx as nx
import time
import numpy as np
import os.path as path

import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

# Add the Loader class here
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

class Loader:
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

# Rest of your code
END_LAT = 53.5 
START_LAT = 51.3
END_LON = 15.0
START_LON = 11.3
STEP = 0.2

OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast?"
PARAMS = "daily=temperature_2m_min,rain_sum,snowfall_sum,windspeed_10m_max&timezone=Europe%2FBerlin"
PATH = "./graphNONREM/berlin_drive_network-osmnx-wetter.graphml" # or for instant remove: "./graph/berlin_drive_network-osmnx.graphml"

class CustomException(Exception):
    pass

def getWeather(lat, lon):
    requestUrl = OPEN_METEO_API + "latitude=" + str(lat) + "&longitude=" + str(lon) + "&" + PARAMS
    # send the request and parse the response
    response = requests.get(requestUrl)
    data_w = response.json()
    daily_data_w = data_w['daily']
    data_w_in_dict = {'temperature_2m_min' : daily_data_w['temperature_2m_min'], 'rain_sum' : daily_data_w['rain_sum'], 'snowfall_sum' : daily_data_w['snowfall_sum'], 'windspeed_10m_max' : daily_data_w['windspeed_10m_max']}
    return data_w_in_dict

def map_weather(G):
    print(Style.BRIGHT+Fore.YELLOW+"Start weather fetching! \n")

    weather_s = time.time()

    try:
        CREATE_TIME = path.getmtime(PATH)
        CURR_TIME = time.time()
        if path.getsize(PATH) // 1024 == 0 or CURR_TIME - CREATE_TIME >= 86400:
            print("Weather data is older than a day or empty ... refetching")
            raise CustomException("Weather data needs to be refetched")
        
        loader = Loader("Load Weatherdata from Memory...")
        loader.start()
        TRY_G = ox.load_graphml(filepath=PATH)
        loader.done = True
        print('\n')
        print(Style.BRIGHT+Fore.GREEN+"Weather loaded.\n")
        return TRY_G
    except CustomException:
        loader2 = Loader("Fetching weather...")
        loader2.start()
       
        for i in np.arange(START_LAT, END_LAT, STEP):
            for j in np.arange(START_LON, END_LON, STEP):
                weather_data = getWeather(i, j)
                for u, data in G.nodes(data=True):
                    if round(abs(data['y'] - i), 2) <= 0.1 and round(abs(data['x'] - j), 2) <= 0.1:
                        nx.set_node_attributes(G, {u: weather_data}, name="weather") # -> Wetterdaten an den Knoten hängen
        loader2.done = True
        weather_e = time.time() - weather_s
        print("\n")
        print(Style.BRIGHT+Fore.GREEN+f"Weather fetching done for all nodes! Time needed: {weather_e}\n")
        return G
    except:
        loader3 = Loader("Fetching weather...")
        loader3.start()
        
        for i in np.arange(START_LAT, END_LAT, STEP):
            for j in np.arange(START_LON, END_LON, STEP):
                weather_data = getWeather(i, j)
                for u, data in G.nodes(data=True):
                    if round(abs(data['y'] - i), 2) <= 0.1 and round(abs(data['x'] - j), 2) <= 0.1: # 0.1 ~ 11km für uns akzeptabel
                        nx.set_node_attributes(G, {u: weather_data}, name="weather") # -> Wetterdaten an den Knoten hängen
        loader3.done = True
        weather_e = time.time() - weather_s
        print("\n")
        print(Style.BRIGHT+Fore.GREEN+f"Weather fetching done for all nodes! Time needed: {weather_e}\n")
        return G
