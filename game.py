# <--- Game --->

# Imports

import tkinter as tk
import sys
import random

# Window creation

main = tk.Tk()
main.geometry("800x600")
main.title("Game")
main.minsize(width=800, height=600)
main.maxsize(width=800, height=600)

inv = tk.Toplevel(main)
inv.title("Inventory")
inv.geometry("300x600")
inv.maxsize(width=300, height=600)
inv.minsize(width=300, height=600)
inv.protocol("WM_DELETE_WINDOW", inv.withdraw)
inv.withdraw()

# Constants

TITLE_FONT = ('arial', 24)
FONT = ('arial', 10)

ITEM_DATA = {
    "weapon": {
        "fists": {"damage": 1},
        "wooden-sword": {"damage": 2},
        "copper-sword": {"damage": 3},
        "iron-sword": {"damage": 5},
        "steel-sword": {"damage": 7},
        "dev-sword": {"damage": 1000, "effects": ["bleeding", "flame", "poison"]},
    },
    "armor": {
        "leather": {"defence": 2, "effects": ["e-resist"]},
        "chain-mail": {"defence": 5},
        "iron": {"defence": 8},
        "steel": {"defence": 12},
        "dev-armor": {
            "defence": 1000,
            "effects": ["defence-up", "thorns", "extra-health", "resist"]},
    },
}

# Classes

class Player():

    def __init__(self):
        self.max_health = 100
        self.health = 100
        self.money = 0
        self.inv = {
            "weapon": [], 
            "armor": [],
            "potion": [],
            "material": {"wood": 0, "stone": 0}
        }
        
        self.equip_weapon = ""
        self.equip_armor = ""

    def add(self, where, what):
        if where in self.inv:
            self.inv[where].append(what)
        update_inv()
        
    def equip(self, where, what):
        
        if where == "weapon":
            self.equip_weapon = what.name
        elif where == "armor":
            self.equip_armor = what.name

        self.update_max_health()
            
        print(str(self.equip_armor) + " " + str(self.equip_weapon) + " " + str(self.health) + " " + str(self.max_health))
            
        update_inv()

    def update_max_health(self):
        equipped_armor = next(
            (item for item in self.inv["armor"] if item.name == self.equip_armor),
            None,
        )
        self.max_health = 150 if equipped_armor and "extra-health" in equipped_armor.effects else 100

class Item():

    def __init__(self,type= "none", what= "none"):
        
        self.name = str(what)
        self.type = type
        self.damage = 0
        self.defence = 0
        self.effects = []

        stats = ITEM_DATA.get(type, {}).get(what, {})
        
        self.damage = stats.get("damage", 0)
        self.defence = stats.get("defence", 0)
        self.effects = stats.get("effects", [])

    def __str__(self):
        return self.name.replace("-", " ").title()


# Functions

def clear_screen(what= "main"):
    
    if what == "main":
        for widget in main.winfo_children():
            if widget not in (inv, exit_button, bottom_left_frame):
                    widget.place_forget()
                    
    else:
        for widget in inv.winfo_children():
            widget.destroy()

def begin_game():
    
    clear_screen()
    
    explore_button = tk.Button(bottom_left_frame, text="Explore", font= FONT, command= explore)
    explore_button.pack(side="left", padx=0)
    
    button = tk.Button(main, text= "Secret Button", font = FONT, command= lambda: [player1.add("weapon", Item("weapon", "dev-sword")), player1.add("armor", Item("armor", "dev-armor"))])
    button.place(relx = 0.5, rely=0.5,anchor="center")

def start_screen():
    title = tk.Label(main, text="Game", font= TITLE_FONT)
    title.place(relx= 0.5, rely= 0.3, anchor="center")
    title_start_button = tk.Button(main, text="Start", command= begin_game, font= FONT)
    title_start_button.place(relx= 0.5, rely= 0.7, anchor="center")
    
def open_inventory():
    
    global inv
    
    """ Reappear """
    
    inv.deiconify()
    
    
def update_inv():
    
    global inv
    
    clear_screen("inv")
    
    money_label = tk.Label(inv, text= f"money: {player1.money}", font= FONT)
    money_label.pack(pady=2)
    
    for key, value in player1.inv.items():
        key_label = tk.Label(inv, text=f' <-- {key} -->', font=FONT)
        key_label.pack(pady=2)
        if isinstance(value, dict):
          for sub_key, sub_val in value.items():
            inv_label = tk.Label(inv, text=f'{sub_key}: {sub_val}', font=FONT)
            inv_label.pack(pady=2)
        else:
          for val in value:
            inv_frame = tk.Frame(inv)
            inv_frame.pack(pady=2)
              
            inv_label = tk.Label(inv_frame, text=val, font=FONT)
            inv_label.pack(side= "left")
            
            is_equipped = (val.name == player1.equip_weapon) or (val.name == player1.equip_armor)
            
            if not is_equipped and val.type != "none":
                equip_button = tk.Button(inv_frame, text="Equip", font=FONT, command= lambda v=val: player1.equip(v.type, v))
                equip_button.pack(side="left", padx = 5)



def my_exit():
    
    global inv
    
    if 'inv' in globals() and inv.winfo_exists() and inv.state() == "normal":
        inv.destroy()
        
    main.destroy()
    sys.exit()
    
def explore():
    
    instance = random.randint(0,100000)
    
    if instance == 56469:
        player1.add("weapon", Item("weapon", "dev-sword"))
        return
    if instance >= 50000 and instance % 2 == 0:
        player1.inv["material"]["stone"] += 1
    elif instance < 50000 and instance % 2 == 0:
        player1.inv["material"]["wood"] += 1
    elif instance % 5 == 0:
        player1.money += 1
        
    if inv.state() == "normal":
        update_inv()
        

# Main 

exit_button = tk.Button(main, text= "Exit", command= my_exit, font= FONT)
exit_button.place(relx=1,rely=1,anchor="se")

bottom_left_frame = tk.Frame(main)
bottom_left_frame.place(relx=0, rely=1, anchor="sw")

inventory_button = tk.Button(bottom_left_frame, text="Inventory", command= lambda: [open_inventory(), update_inv()], font=FONT)
inventory_button.pack(side="left")

player1 = Player()
player1.add("weapon", Item("weapon", "fists"))

start_screen()

main.mainloop()