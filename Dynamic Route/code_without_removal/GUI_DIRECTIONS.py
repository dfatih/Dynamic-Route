import sp_functions as sp_func

import tkinter as tk
from PIL import ImageTk, Image
from tkinter import scrolledtext
import osmnx as ox
import time
import msvcrt
import os

def get_input():
    CHAR = msvcrt.getch().decode('utf-8')
    os.system('cls')
    return CHAR

def create_GUI_directions(TEXTLIST, G, ROUTE_PLOT):
    WINDOW = tk.Tk()
    WINDOW.title("Route directions")
    WINDOW.geometry("800x370")

    # Create a scrollable text widget
    TEXT_WIDGET = scrolledtext.ScrolledText(WINDOW, width=90, height=20)
    TEXT_WIDGET.pack()

    # List to store the image references
    IMAGE_REF = []

    # Iterate over the texts
    for TEXT in TEXTLIST:
        try:
            # Load the image
            IMG = Image.open(f'./img/{TEXT[1]}.png')

            # Resize the image
            NEW_WIDTH = 36
            ASPECT_RATIO = IMG.width / IMG.height
            NEW_HEIGHT = int(NEW_WIDTH / ASPECT_RATIO)
            RESIZED_IMG = IMG.resize((NEW_WIDTH, NEW_HEIGHT))

            # Convert the image to Tkinter-compatible format
            TK_IMG = ImageTk.PhotoImage(RESIZED_IMG)

            # Append the image reference to the list
            IMAGE_REF.append(TK_IMG)

            # Insert the text and image into the text widget
            TEXT_WIDGET.image_create(tk.END, image=TK_IMG)
            TEXT_WIDGET.insert(tk.END, TEXT[0] + "\n")

        except (FileNotFoundError, OSError):
            # Display a placeholder image if loading the image fails
            PLACEHOLDE_IMG = Image.open('./img/placeholder.png')
            PLACEHOLDE_IMG = PLACEHOLDE_IMG.resize((200, 150))
            TK_IMG = ImageTk.PhotoImage(PLACEHOLDE_IMG)

            # Append the image reference to the list
            IMAGE_REF.append(TK_IMG)

            # Insert the placeholder image and error text into the text widget
            TEXT_WIDGET.image_create(tk.END, image=TK_IMG)
            TEXT_WIDGET.insert(tk.END, "Error loading image\n")

# Prevent the image references from being garbage collected
    WINDOW.IMAGE_REF = IMAGE_REF

    # Function to handle the plot button click event
    def plot_button_click():
        SP_NODES = [node_id for node_id in ROUTE_PLOT]
        SUBGRAPH = G.subgraph(SP_NODES)
        SUBGRAPH_LON = list(SUBGRAPH.nodes(data='x'))
        REAL_SUBGRAPH_LON = [t[1] for t in SUBGRAPH_LON]
        SUBGRAPH_LAT = list(SUBGRAPH.nodes(data='y'))
        REAL_SUBGRAPH_LAT = [i[1] for i in SUBGRAPH_LAT]
        REAL_SUBGRAPH = ox.graph_from_bbox(max(REAL_SUBGRAPH_LAT) + 0.01, min(REAL_SUBGRAPH_LAT) - 0.01, max(REAL_SUBGRAPH_LON) + 0.01, min(REAL_SUBGRAPH_LON) - 0.01, network_type = 'drive', simplify=True)
        sp_func.plot_route(REAL_SUBGRAPH, ROUTE_PLOT)
    def exit_button_click():
        WINDOW.destroy()

    # Create a button for plotting
    PLOT_BUTTON = tk.Button(WINDOW, text="Visualize Route", command=plot_button_click)
    PLOT_BUTTON.pack()

    # Create an exit button
    EXIT_BUTTON = tk.Button(WINDOW, text="Exit", command=exit_button_click)
    EXIT_BUTTON.pack()

    # Run the GUI event loop
    WINDOW.mainloop()

#create_GUI_directions([("HELLO", "Left")] * 100)