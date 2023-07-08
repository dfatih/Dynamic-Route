import requests
import json
import networkx as nx
import osmnx as ox

def autofill_all_streets(location):
    url = f'https://nominatim.openstreetmap.org/search?q={location}&format=json'
    response = requests.get(url)
    data = json.loads(response.text)
    data = data[:5] # nehme nur die ersten 5 Adressen ;) 
    if data:
        for i, item in enumerate(data):
            display_name = item.get('display_name', '') # display_name gibt aus Straße, Ort, Stadt, Postleitzahl, Land
            print(f'{i+1}. {display_name}')

        auswahl = int(input("Wähle eine Option, wenn die Eingabe ausversehen war gebe ein: 0 ")) # Wähle welche Koordianten du willst von welcher Straße
        while auswahl != 0:
            if auswahl >= 1 and auswahl <= len(data):
                ausgewaehltes_item = data[auswahl-1]
                latitude = float(ausgewaehltes_item['lat'])
                longitude = float(ausgewaehltes_item['lon'])
                return latitude, longitude
            else:
                print("Ungültige Option. Probiere es nochmal")
                new_location = input("Gib erneut Straße ein: ")
                return autofill_all_streets(new_location)
        new_location = input("Gib erneut Straße ein: ")
        return autofill_all_streets(new_location)
    else:
        print(f"Keine Straßen mit dem Namen {location} gefunden .. Probiere nochmal: \n")
        new_location = input("Gib erneut Straße ein: ")
        return autofill_all_streets(new_location)

def name_place_all_streets(G, FASTEST_PATH):
    for u in range(0, len(FASTEST_PATH) - 1): # G.edges(data=True): , u, v, data
        if 'name' in G[FASTEST_PATH[u]][FASTEST_PATH[u + 1]][0]: # in data:
            continue
        latitude = G.nodes[FASTEST_PATH[u]]['y']
        longitude = G.nodes[FASTEST_PATH[u]]['x']
        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}'
        response = requests.get(url)
        osm_data = json.loads(response.text)
        # Extract street name from OpenStreetMap data
        if osm_data:
            display_name = osm_data['display_name'] # display_name gibt aus Straße, Ort, Stadt, Postleitzahl, Land
            parts = display_name.split(",")
            if any(char.isdigit() for char in parts[0]):
                parts.pop(0) # Remove the part containing numbers
            else: #if any(char.isdigit() for char in parts[1]):
                #parts.pop(0)
                parts.pop(1)  # Remove the other part

            steet_name = parts[0]
            nx.set_edge_attributes(G, {(FASTEST_PATH[u], FASTEST_PATH[u + 1], 0): {"name": steet_name}})
        else:
            print("something went wrong")
    return G
            

if __name__ == "__main__":
    location = input("Gib Straße ein: ")
    latitude, longitude = autofill_all_streets(location)
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")