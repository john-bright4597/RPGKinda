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

location = ""

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

POTION_DATA =  {
    "health-potion": {"heal": 25},
    "greater-health-potion": {"heal": 50},
    "defence-potion": {"defence": 10}
}
               
ITEMS_SALE_POTION = {
    "health-potion" : 15,
    "greater-health-potion": 30,
    "defence-potion": 25
}

ITEMS_SALE_MATERIALS = {
    "wood" : 2,
    "stone" : 2,
    "raw-iron" : 6
}

ITEMS_SALE_WEAPONS = {
    "wooden-sword": {"money": 15, "material": {"wood": 20}},
    "iron-sword" : {"money": 30, "material": {"wood": 10, "raw-iron": 15}},
    "steel-sword" : {"money": 50, "material": {"wood": 10, "raw-iron": 20, "stone": 15}}
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
            "potion": {"health-potion": 0, "greater-health-potion": 0, "defence-potion": 0},
            "material": {"wood": 0, "stone": 0, "raw-iron": 0}
        }
        
        self.equip_weapon = ""
        self.equip_armor = ""

    def add(self, where, what):
        if where in self.inv:
            if where == "material" or where == "potion":
                self.inv[where][what] += 1
            else:
                self.inv[where].append(what)

        update_inv()
        
    def equip(self, where, what):
        
        if where == "weapon":
            self.equip_weapon = what.name
        elif where == "armor":
            self.equip_armor = what.name

        self.update_max_health()
            
        #print(str(self.equip_armor) + " " + str(self.equip_weapon) + " " + str(self.health) + " " + str(self.max_health))
            
        update_inv()

    def update_max_health(self):
        equipped_armor = next(
            (item for item in self.inv["armor"] if item.name == self.equip_armor),
            None)
        self.max_health = 150 if equipped_armor and "extra-health" in equipped_armor.effects else 100

    def use(self, what):

        if self.inv["potion"].get(what, 0) < 1:
            return

        effect = POTION_DATA.get(what, {})

        if "heal" in effect:
            self.health = min(self.max_health, self.health + effect["heal"])

        if "defence-buff" in effect:
            self.temp_defence_buff = effect["defence-buff"]

        self.inv["potion"][what] -= 1
        update_inv()

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

class Monster():

    def __init__(self):

        self.type = random.choice(["goblin", "orc", "slime", "giant"])

# Functions

def clear_screen(what= "main"):
    
    if what == "main":
        for widget in main.winfo_children():
            if widget not in (inv, bottom_right_frame, bottom_left_frame):
                widget.destroy()
                    
    else:
        for widget in inv.winfo_children():
            widget.destroy()

def begin_game():
    
    clear_screen()

    global explore_button
    
    explore_button = tk.Button(bottom_left_frame, text="Explore", font= FONT, command= explore)
    explore_button.pack(side="left", padx=0)

    town("grimsby")
    
    #button = tk.Button(main, text= "Secret Button", font = FONT, command= lambda: [player1.add("weapon", Item("weapon", "dev-sword")), player1.add("armor", Item("armor", "dev-armor"))])
    #button.place(relx = 0.5, rely=0.5,anchor="center")

def town(what):

    global location

    location = what

    town_name = tk.Label(main, text= what.title(), font=TITLE_FONT)
    town_name.place(relx=0.5, rely=0.2, anchor="center")

    town_frame = tk.Frame(main)
    town_frame.place(relx=0.5, rely=0.5,anchor="center")

    shop_button = tk.Button(town_frame, text= "Shop", font= FONT, command= lambda: [shop(what, "general"), explore_button.pack_forget()])
    shop_button.pack(side="left")
    
    black_smith_button = tk.Button(town_frame, text= "Black Smith", font= FONT, command= lambda: [shop(what, "black-smith"), explore_button.pack_forget()])
    black_smith_button.pack(side="left", padx= 5)

def shop(where, which):

    global back_button
    clear_screen()
    back_button.pack(side="right", padx= 0)

    if where == "grimsby":
        if which == "general":
            name = tk.Label(main, text= "Mud & Dirt Co.", font= TITLE_FONT)
            name.place(relx= 0.5, rely= 0.2, anchor= "center")

            items_frame = tk.Frame(main)
            items_frame.place(relx=0.5, rely=0.4, anchor="center")

            material_frame = tk.Frame(items_frame)
            material_frame.pack(side="left", padx=20, anchor="n")

            potion_frame = tk.Frame(items_frame)
            potion_frame.pack(side="right", padx=20, anchor="n")

            for item, cost in ITEMS_SALE_MATERIALS.items():
                shop_frame = tk.Frame(material_frame)
                shop_frame.pack(pady= 2)

                shop_label = tk.Label(shop_frame, text=f"{item.replace("-", " ").title()} ${cost}", font= FONT)
                shop_label.pack(side= "left")

                buy_button = tk.Button(shop_frame, text= "Buy", font= FONT, command= lambda i = item: buy(i))
                buy_button.pack(side= "left", padx=0)

            for item, cost in ITEMS_SALE_POTION.items():
                shop_frame = tk.Frame(potion_frame)
                shop_frame.pack(pady= 2)

                buy_button = tk.Button(shop_frame, text= "Buy", font= FONT, command= lambda i = item: buy(i))
                buy_button.pack(side= "right", padx=0)

                shop_label = tk.Label(shop_frame, text=f"{item.replace("-", " ").title()} ${cost}", font= FONT)
                shop_label.pack(side= "right")
                
        elif which == "black-smith":
            
            name = tk.Label(main, text= "Stone & Sons", font= TITLE_FONT)
            name.place(relx= 0.5, rely= 0.2, anchor= "center")
            
            items_frame = tk.Frame(main)
            items_frame.place(relx=0.5, rely=0.4, anchor="center")
            
            for item, details in ITEMS_SALE_WEAPONS.items():
                
                weapon_frame = tk.Frame(items_frame)
                weapon_frame.pack(pady=2)

                material_text = ", ".join(
                f"{mat.replace('-', ' ').title()}: {amt}"
                for mat, amt in details["material"].items()
                )
                
                shop_label = tk.Label(weapon_frame, text=f"{item.replace("-", " ").title()} - ${details["money"]} and ({material_text})", font= FONT)
                shop_label.pack(side= "left", pady= 2)
                
                buy_button = tk.Button(weapon_frame, text= "Buy", font= FONT, command= lambda i = item: buy(i))
                buy_button.pack(side= "left", padx=2)

    else:
        name = tk.Label(main, text= "Congrats! You've found a unknown shop!", font= TITLE_FONT)
        name.place(relx= 0.5, rely= 0.2, anchor= "center")

def buy(what):

    if what in ITEMS_SALE_MATERIALS:
        if player1.money >= ITEMS_SALE_MATERIALS[what]:
            player1.money -= ITEMS_SALE_MATERIALS[what]
            player1.add("material", what)
    if what in ITEMS_SALE_POTION:
        if player1.money >= ITEMS_SALE_POTION[what]:
            player1.money -= ITEMS_SALE_POTION[what]
            player1.add("potion", what)
    if what in ITEMS_SALE_WEAPONS:
        attribute = ITEMS_SALE_WEAPONS[what]
        broke_or_nope = player1.money >=  attribute["money"]and all(player1.inv["material"].get(mat, 0) >= amt for mat, amt in attribute["material"].items())

        if broke_or_nope:
            player1.money -= attribute["money"]
            for mat, amt in attribute["material"].items():
                player1.inv["material"][mat] -= amt
            player1.add("weapon", Item("weapon", what))

    update_inv()

def back(where):

    clear_screen()
    town(where)
    explore_button.pack(side="left", padx=0)
    back_button.pack_forget()

def start_screen():
    title = tk.Label(main, text="Game", font= TITLE_FONT)
    title.place(relx= 0.5, rely= 0.3, anchor="center")
    title_start_button = tk.Button(main, text="Start", command= begin_game, font= FONT)
    title_start_button.place(relx= 0.5, rely= 0.7, anchor="center")
    
def open_inventory():
    
    global inv
    inv.deiconify()
    
def update_inv():
    
    global inv
    
    clear_screen("inv")
    
    money_label = tk.Label(inv, text= f"Money: {player1.money}", font= FONT)
    money_label.pack(pady=2)
    
    for key, value in player1.inv.items():
        key_label = tk.Label(inv, text=f' <-- {key} -->', font=FONT)
        key_label.pack(pady=2)
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                inv_frame = tk.Frame(inv)
                inv_frame.pack(pady=2)

                inv_label = tk.Label(inv_frame, text=f'{sub_key.replace("-", " ").title()}: {sub_val}', font=FONT)
                inv_label.pack(side="left")

                if key == "potion" and sub_val > 0:
                    use_button = tk.Button(inv_frame, text="Use", font=FONT, command=lambda s=sub_key: player1.use(s))
                    use_button.pack(side="left", padx=5)
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

bottom_left_frame = tk.Frame(main)
bottom_left_frame.place(relx=0, rely=1, anchor="sw")

bottom_right_frame = tk.Frame(main)
bottom_right_frame.place(relx= 1, rely= 1, anchor="se")

exit_button = tk.Button(bottom_right_frame, text= "Exit", command= my_exit, font= FONT)
exit_button.pack(side="right")

back_button = tk.Button(bottom_right_frame, text= "Back", font= FONT, command= lambda: back(location))

inventory_button = tk.Button(bottom_left_frame, text="Inventory", command= lambda: [open_inventory(), update_inv()], font=FONT)
inventory_button.pack(side="left")

player1 = Player()
player1.add("weapon", Item("weapon", "fists"))

start_screen()

main.mainloop()
