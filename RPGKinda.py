# <--- Game --->

# Imports

import tkinter as tk
from tkinter import ttk
import sys
import random
import json
import os
import functools
import textwrap

# json data handling

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "saves.json")

try:
    with open(json_path, 'r') as file:
        data = json.load(file)
except json.JSONDecodeError as e:
    print("failed to load json file", e)
    data = {"saves": "none"}
except FileNotFoundError as e:
    print("couldn't find json file", e)
    data = {"saves": "none"}

# Window creation

main = tk.Tk()
main.geometry("800x600")
main.title("RPGKinda")
main.minsize(width=800, height=600)
main.maxsize(width=800, height=600)
main.config(background= "#FFFFFF")
main.tk_setPalette(background="#FFFFFF", foreground="#2B2B2B")

inv = tk.Toplevel(main)
inv.title("Inventory")
inv.geometry("300x600")
inv.maxsize(width=300, height=600)
inv.minsize(width=300, height=600)
inv.tk_setPalette(background="#FFFFFF", foreground="#2B2B2B")
inv.protocol("WM_DELETE_WINDOW", inv.withdraw)
inv.withdraw()

# Constants

location = "main-menu"
turn = True
mons = None
update_tracker = False
in_inv = False
first_time = {"gs":True,"bs":True}
exit_area_ind = False
unbound= None
speech_jobs = []

style = ttk.Style()

style.configure("TScale", 
    borderwidth=5, 
    relief="solid", 
    background="#FFFFFF")

#   SETTINGS

text_scroll_speed = tk.IntVar(value=50)

TITLE_FONT = ('arial', 24)
FONT = ('arial', 14)

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

ITEMS_SALE_WEAPONS = {
    "wooden-sword": {"money": 15, "material": {"wood": 20}},
    "iron-sword" : {"money": 30, "material": {"wood": 10, "raw-iron": 15}},
    "steel-sword" : {"money": 50, "material": {"wood": 10, "raw-iron": 20, "stone": 15}}
}

MONSTER_RANDOM ={
    "goblin": {"attack": {"h": 15, "l": 10}},
    "orc": {"attack": {"h": 33, "l": 28}},
    "slime": {"attack": {"h": 12, "l": 7}},
    "giant": {"attack": {"h": 27, "l": 22}}
}

MONSTER_DATA = {
    "goblin": {"health": random.randint(20,30), "attack": random.randint(MONSTER_RANDOM["goblin"]["attack"]["l"], MONSTER_RANDOM["goblin"]["attack"]["h"]), "defence": random.randint(1,10), "reward": {"money": 10, "exp": random.randint(5, 20)}},
    "orc": {"health": random.randint(20,40), "attack": random.randint(MONSTER_RANDOM["orc"]["attack"]["l"],MONSTER_RANDOM["orc"]["attack"]["h"]), "defence": random.randint(5,15), "reward": {"money": 20, "exp": random.randint(15, 35)}},
    "slime": {"health": random.randint(5,20), "attack": random.randint(MONSTER_RANDOM["slime"]["attack"]["l"],MONSTER_RANDOM["slime"]["attack"]["h"]), "defence": random.randint(0,5), "reward": {"money": 5, "exp": random.randint(1, 10)}},
    "giant": {"health": random.randint(40,50), "attack": random.randint(MONSTER_RANDOM["giant"]["attack"]["l"],MONSTER_RANDOM["giant"]["attack"]["h"]), "defence": random.randint(10,20), "reward": {"money": 40, "exp": random.randint(40, 60)}}
}

MATERIAL_DATA = {
#   name         sell/buy price,  sold in shop?,    explore drop weight
    "wood":         {"price": 2,  "in_shop": True,  "find_weight": 5},
    "stone":        {"price": 2,  "in_shop": True,  "find_weight": 5},
    "raw-iron":     {"price": 6,  "in_shop": True,  "find_weight": 2},
    "eldenite":     {"price": 20, "in_shop": False, "find_weight": 0},
    "kenvilite":    {"price": 25, "in_shop": False, "find_weight": 0},
    "dragon-scale": {"price": 60, "in_shop": False, "find_weight": 0},
}

MATERIAL_LIST = list(MATERIAL_DATA)

ITEMS_SALE_MATERIALS = {m: d["price"] for m, d in MATERIAL_DATA.items() if d["in_shop"]}

IMAGES = {
    "gs": r"Assets\GS_Keep.png",
    "bs": r"Assets\BS_Keep.png",
    "sm": r"Assets\S_Man.png"
}

# Classes

class Player():

    def __init__(self):

        global data, exp_to_next_level, text_scroll_speed

        self.max_health = 100
        self.health = 100
        self.money = 0
        self.inv = default_inventory()
        self.level = 0
        self.exp = 0        

        if data["saves"] != "none":
            self.max_health = data["max_health"]
            self.health = data["health"]
            self.money = data["money"]
            self.level = data["level"]
            self.exp = data["exp"]
            for i in data["inv"]["weapon"]: 
                self.inv["weapon"].append(Item("weapon", i))
            for i in data["inv"]["armor"]: 
                self.inv["armor"].append(Item("armor", i))
            self.inv["potion"].update(data["inv"]["potion"])
            self.inv["material"].update(data["inv"]["material"])
            text_scroll_speed.set(data.get("settings", {}).get("text-scroll", 50))

        exp_to_next_level = 10 * 1.5 ** self.level

        self.equip_weapon = Item("weapon", "none")
        self.equip_armor = Item("armor", "none")

    def add(self, where, what, amount= 1):
        if where in self.inv:
            if where == "material" or where == "potion":
                self.inv[where][what] += amount
            else:
                self.inv[where].append(what)

                current = self.equip_weapon if where == "weapon" else self.equip_armor
                if (what.damage, what.defence) > (current.damage, current.defence):
                    self.equip(where, what)

        update_inv()

    def level_up(self):

        global exp_to_next_level

        if self.exp >= exp_to_next_level:
            self.level += 1
            self.exp -= exp_to_next_level
            exp_to_next_level *= 1.5
        
    def equip(self, where, what):
        
        if where == "weapon":
            self.equip_weapon = what
        elif where == "armor":
            self.equip_armor = what

        self.update_max_health()
            
        #print(str(self.equip_armor) + " " + str(self.equip_weapon) + " " + str(self.health) + " " + str(self.max_health))
            
        update_inv()

    def update_max_health(self):
        self.max_health = 150 if "extra-health" in self.equip_armor.effects else 100

        if self.health >= self.max_health: self.health = self.max_health

    def use(self, what):

        global update_tracker

        if self.inv["potion"].get(what, 0) < 1:
            return

        effect = POTION_DATA.get(what, {})

        if "heal" in effect:
            self.health = min(self.max_health, self.health + effect["heal"])

        if "defence-buff" in effect:
            self.temp_defence_buff = effect["defence"]

        self.inv["potion"][what] -= 1
        update_inv()

        if update_tracker:
            update_combat_display(mons, health_label)

    def to_save(self):
        data = {
            "saves": "player1",
            "health": self.health, 
            "max_health": self.max_health, 
            "money": self.money,
            "level": self.level,
            "exp": self.exp, 
            "inv": {
                "weapon": [i.name for i in self.inv["weapon"]],
                "armor": [i.name for i in self.inv["armor"]], 
                "potion": self.inv["potion"],
                "material": self.inv["material"]
            },
            "settings": {
                "text-scroll": int(text_scroll_speed.get())
            }               
        }

        try:
            with open(json_path, 'w') as file:
                json.dump(data, file, indent= 4)
        except json.JSONDecodeError as e:
            print("failed to load json file", e)
            data = {"saves": "none"}
        except FileNotFoundError as e:
            print("couldn't find json file", e)
            data = {"saves": "none"}

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

        global mons

        self.type = random.choice(list(MONSTER_DATA.keys()))

        stats = MONSTER_DATA[self.type]
        self.health = stats["health"]
        self.attack = stats["attack"]
        self.defence = stats["defence"]
        self.reward = stats.get("reward", {})

        mons = self

    def change_dmg(self):

        self.attack = random.randint(MONSTER_RANDOM[self.type]["attack"]["l"],MONSTER_RANDOM[self.type]["attack"]["h"])

class ExitInterrupt(Exception):
    pass

# Functions

def interruptible(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ExitInterrupt:
            pass
    return wrapper

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

    wipe_save_btn.destroy()
    settings_button.destroy()
    
    explore_button.pack(side="right", padx=0)

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

@interruptible
def shop(where, which):

    global back_button, in_inv
    clear_screen()
    back_button.pack(side="right", padx= 0)

    if where == "grimsby":
        if which == "general":

            if first_time["gs"]:
                first_time["gs"] = False
                say("Hello, welcome to Mud & Dirt Co.",
                "The finest general store all of the king's land.", where="gs")

            in_inv = True

            update_inv()

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

            if first_time["bs"]:
                first_time["bs"] = False
                say("Welcome in to Stone & Sons", "I can sell you some fresh weapons or upgrade your gear.", where="bs")
            
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

def back(where, flee=False, what= None):

    global in_inv, update_tracker, exit_area_ind

    exit_area_ind = False

    if flee:
        flee_chance = random.randint(0,100)
        if flee_chance % 2 == 0:
            failed_label = tk.Label(main, text="You failed to flee!", font= FONT, fg="red")
            failed_label.place(relx=0.5, rely=0.5, anchor="center")
            main.after(1000, failed_label.destroy)
            monster_turn(what)
            return

    if where == "main-menu":
        clear_screen()
        start_screen()
        back_button.pack_forget()
        return

    in_inv=False
    update_tracker = False
    update_inv()
    exit_button.config(state="normal")

    clear_screen()
    town(where)
    explore_button.pack(side="right", padx=0)
    back_button.pack_forget()
    flee_button.pack_forget()

def default_inventory():
    return {
        "weapon": [],
        "armor": [],
        "potion": {p: 0 for p in POTION_DATA},
        "material": {m: 0 for m in MATERIAL_DATA},
    }

def clean_save():

    global data, player1

    data = {
        "saves": "none",
        "health": 100, 
        "max_health": 100, 
        "money": 0, 
        "level": 0,
        "exp": 0,
        "inv": default_inventory(),
        "settings": {"text-scroll": int(text_scroll_speed.get())}              
    }

    try:
        with open(json_path, 'w') as file:
            json.dump(data, file, indent= 4)
    except json.JSONDecodeError as e:
        print("failed to load json file", e)
        data = {"saves": "none"}
    except FileNotFoundError as e:
        print("couldn't find json file", e)
        data = {"saves": "none"}

    player1 = Player()
    if not any(i.name == "fists" for i in player1.inv["weapon"]):
        player1.add("weapon", Item("weapon", "fists"))

    inv.after(100, update_inv)
    main.after(100, start_screen)

def you_sure():

    clear_screen()

    inventory_button.pack_forget()
    exit_button.pack_forget()
    explore_button.pack_forget()
    wipe_save_btn.pack_forget()

    label = tk.Label(main, text= "Are you sure?", font=FONT)
    label.place(relx=0.5, rely= 0.4, anchor="center")

    frame = tk.Frame(main)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    clear_save = tk.Button(frame, text= "Clear Save", font=FONT, command= clean_save)
    clear_save.pack(side= "left", padx= 5)

    keep_save = tk.Button(frame, text= "Keep Save", font=FONT, command= start_screen)
    keep_save.pack(side= "right", padx= 5)

def start_screen():

    global bottom_right_frame

    clear_screen()
    clear_buttons()

    inventory_button.pack(side="left")
    exit_button.pack(side="right")
    wipe_save_btn.pack(side= "right")
    settings_button.pack(side="right")
        
    title = tk.Label(main, text="RPGKinda", font= TITLE_FONT)
    title.place(relx= 0.5, rely= 0.3, anchor="center")
    title_start_button = tk.Button(main, text="Start", command= begin_game, font= FONT)
    title_start_button.place(relx= 0.5, rely= 0.7, anchor="center")

def open_inventory():
    
    global inv
    inv.deiconify()
    
def update_inv(in_shop = False):
    
    global inv
    
    clear_screen("inv")

    if in_inv: 
        in_shop = True
    
    money_label = tk.Label(inv, text= f"Money: {player1.money}", font= FONT)
    money_label.pack(pady=2)

    level_label = tk.Label(inv, text=f"Level {player1.level}  EXP: {int(player1.exp)}/{int(exp_to_next_level)}", font=FONT)
    level_label.pack(pady=2)

    for key, value in player1.inv.items():
        key_label = tk.Label(inv, text=f' <-- {key} -->', font=FONT)
        key_label.pack(pady=2)
        if isinstance(value, dict):
            value = {k: v for k, v in value.items() if v > 0}
            if not value:
                continue
            for sub_key, sub_val in value.items():
                inv_frame = tk.Frame(inv)
                inv_frame.pack(pady=2)

                inv_label = tk.Label(inv_frame, text=f'{sub_key.replace("-", " ").title()}: {sub_val}', font=FONT)
                inv_label.pack(side="left")

                if key == "material" and in_shop:
                    sell_button = tk.Button(inv_frame, text= "Sell", font=FONT, command=lambda s=sub_key: sell(s))
                    sell_button.pack(side= "left", padx= 5)

                if key == "potion" and sub_val > 0:
                    use_button = tk.Button(inv_frame, text="Use", font=FONT, command=lambda s=sub_key: player1.use(s))
                    use_button.pack(side="left", padx=5)
        else:
              for val in sorted(value, key=lambda i: (i.damage, i.defence)):
                inv_frame = tk.Frame(inv)
                inv_frame.pack(pady=2)
                  
                inv_label = tk.Label(inv_frame, text=val, font=FONT)
                inv_label.pack(side= "left")
                
                is_equipped = (val is player1.equip_weapon) or (val is player1.equip_armor)
                
                if not is_equipped and val.type != "none":
                    equip_button = tk.Button(inv_frame, text="Equip", font=FONT, command= lambda v=val: player1.equip(v.type, v))
                    equip_button.pack(side="left", padx = 5)

def sell(what):

    global player1

    if what in player1.inv["material"] and player1.inv["material"][what] > 0:
        price = MATERIAL_DATA[what]["price"]
        player1.inv["material"][what] -= 1
        player1.money += max(0,price - random.randint(0, price // 2))

    update_inv()

def my_exit():
    
    global inv
    
    if 'inv' in globals() and inv.winfo_exists() and inv.state() == "normal":
        inv.destroy()
        
    main.destroy()
    sys.exit()

def exit_area():

    global in_inv, exit_area_ind

    clear_screen()
    clear_buttons()
    clear_screen()

    exit_area_ind = True

    cancel_speech()

    in_inv = False
    update_inv()

    if location == "main-menu":
        my_exit()

    save_exit_button = tk.Button(main, text= "Save and Exit", font= FONT, command= lambda: [player1.to_save(), my_exit()])
    save_exit_button.place(relx=0.4, rely=0.5, anchor="center")

    act_exit_button = tk.Button(main, text= "Exit", font= FONT, command= my_exit)
    act_exit_button.place(relx= 0.6, rely= 0.5, anchor="center")

    cancel_button = tk.Button(main, text= "Cancel", font= FONT, command= lambda: [back(location), exit_button.pack(side="right"), inventory_button.pack(side="left")])
    cancel_button.place(relx= 0.5, rely= 0.6, anchor="center")

def player_attack(what):
    damage = max(0, player1.equip_weapon.damage - what.defence)
    what.health -= damage
    return damage
 
def monster_attack(what):
    damage = max(0, what.attack - player1.equip_armor.defence)
    player1.health -= damage
    return damage
 
def set_combat_buttons(yes):
    state = "normal" if yes else "disabled"
    attack_button.config(state=state)

def update_combat_display(what, health_label):
    health_label.config(
        text=f"Your HP: {max(0, player1.health)}   {what.type.title()} HP: {max(0, what.health)}"
    )

def combat(what):

    global update_tracker 

    update_tracker = True

    global flee_button, attack_button, status_label, health_label

    clear_screen()
    explore_button.pack_forget()
    flee_button.pack(side="right", padx= 0)
    exit_button.config(state="disabled")

    status_label = tk.Label(main, text= f"You have encountered a {what.type}!", font= FONT)
    status_label.place(relx= 0.5, rely= 0.3, anchor="center")

    health_label = tk.Label(main, text="", font=FONT)
    health_label.place(relx=0.5, rely=0.35, anchor="center")
    update_combat_display(what, health_label)

    action_frame = tk.Frame(main)
    action_frame.place(relx=0.5, rely= 0.7, anchor="center")

    attack_button = tk.Button(action_frame, text= "Attack", font= FONT, command= lambda: player_turn(what))
    attack_button.pack(side= "left")

    set_combat_buttons(True)

    update_inv()

    #main.after(600, lambda: resolve_monster_turn(what))

def player_turn(what):
 
    global turn
 
    if not turn:
        return 
 
    turn = False
    set_combat_buttons(False)
    update_inv()
 
    dmg = player_attack(what)
    status_label.config(text=f"You hit the {what.type} for {dmg} damage!")
    update_combat_display(what, health_label)
 
    if what.health <= 0:
        end_combat(what, won=True)
        return
 
    main.after(500, lambda: monster_turn(what))

def monster_turn(what):
 
    global turn

    what.change_dmg()
 
    dmg = monster_attack(what)
    status_label.config(text=f"The {what.type} hits you for {dmg} damage!")
    update_combat_display(what, health_label)
 
    if player1.health <= 0:
        end_combat(what, won=False)
        return
 
    turn = True
    set_combat_buttons(True)
    update_inv()

def end_combat(what, won):
 
    global turn, update_tracker
 
    turn = True
    attack_button.pack_forget()
    flee_button.pack_forget()
 
    if won:
        reward = what.reward
        if "money" in reward:
            player1.money += reward["money"]
        if "material" in reward:
            for mat, amt in reward["material"].items():
                player1.inv["material"][mat] += amt
        result_text = f"You defeated the {what.type}!"
        if "exp" in reward:
            player1.exp += reward["exp"]

            while player1.exp >= exp_to_next_level:
                player1.level_up()

    else:
        main.after(250, clear_screen())
        exit_button.config(state="normal", command= lambda: [clean_save(), my_exit()])
        return
 
    status_label.config(text=result_text)
    health_label.config(text="")
 
    update_inv()

    update_tracker = False
 
    main.after(1500, lambda: back(location))

def gather_material():

    names = [m for m, d in MATERIAL_DATA.items() if d["find_weight"] > 0]
    weights = [MATERIAL_DATA[m]["find_weight"] for m in names]
    player1.add("material", random.choices(names, weights)[0])  

def explore():
    
    instance = random.randint(0,1000000)
    
    if instance == 564609:
        player1.add("weapon", Item("weapon", "dev-sword"))
        player1.add("armor", Item("armor", "dev-armor"))
        return
    if instance % 5 == 0:
        player1.money += 1
    elif instance % 2 == 1 and instance < player1.level * 50000:
        combat(Monster())
    else:
        gather_material()

    player1.exp += random.randint(1, int(exp_to_next_level * 0.1))

    while player1.exp >= exp_to_next_level:
        player1.level_up()

    if inv.state() == "normal":
        update_inv()

def cancel_speech():
    for job in speech_jobs:
        main.after_cancel(job)
    speech_jobs.clear()

    if unbound is not None:
        unbound.set(True)

def speech_box(text, where):

    global unbound, speech_jobs

    wrapped = textwrap.fill(text, width= 40)

    unbound = tk.BooleanVar(value=False)
    speech_jobs = []
    typing = [bool(wrapped)]

    frame = tk.Frame(main, borderwidth=3, relief="solid")
    frame.place(relx=0, rely=0, relheight=.15, relwidth=1, anchor="nw")

    logo = tk.PhotoImage(file=os.path.join(base_dir, IMAGES[where]))
    img_lbl = tk.Label(frame, image=logo)
    img_lbl.image = logo
    img_lbl.place(relx=0.2, rely=0.5, anchor="center")

    label = tk.Label(frame, text="", font=FONT)
    label.place(relx=0.5, rely=0.5, anchor="center")

    def show(i):

        if exit_area_ind or not label.winfo_exists():
            return
        label.config(text=wrapped[:i + 1])
        if i == len(wrapped) - 1:
            typing[0] = False

    def on_enter(event=None):
        if typing[0]:                 
            cancel_jobs_only()
            label.config(text= wrapped)
            typing[0] = False
        else:                         
            unbound.set(True)

    def cancel_jobs_only():
        global speech_jobs
        for job in speech_jobs:
            main.after_cancel(job)
        speech_jobs = []

    for i in range(len(wrapped)):
        speech_jobs.append(main.after(text_scroll_speed.get() * i, show, i))

    main.bind("<Return>", on_enter)
    main.bind("<1>", on_enter)
    main.wait_variable(unbound)
    main.unbind("<Return>")
    main.unbind("<1>")
    cancel_jobs_only()

    if frame.winfo_exists():
        frame.destroy()
    if exit_area_ind:
        raise ExitInterrupt

def settings_window():

    clear_screen()
    clear_buttons()
    back_button.pack(side="right")

    text_scroll_label = tk.Label(main, font=FONT, text= "Text Scroll Speed")
    text_scroll_label.place(anchor="nw",relx=0,rely=0)

    text_scroll_frame = tk.Frame(main)
    text_scroll_frame.place(relx=0,rely=0.05,anchor="nw")
    text_scroll_speed_bar = ttk.Scale(text_scroll_frame, from_=100, to=0, length= 200, variable=text_scroll_speed, command= lambda value: text_scroll_indicator.config(text=((text_scroll_speed.get()-100)*-1)))
    text_scroll_speed_bar.pack(side="left")
    text_scroll_indicator = tk.Label(text_scroll_frame, font= FONT, text= ((text_scroll_speed.get()-100)*-1))
    text_scroll_indicator.pack(side="right")

def clear_buttons():

    inventory_button.pack_forget()
    exit_button.pack_forget()
    explore_button.pack_forget()
    wipe_save_btn.pack_forget()
    flee_button.pack_forget()
    back_button.pack_forget()
    settings_button.pack_forget()

def say(*lines, where):
    for line in lines:
        speech_box(line, where)

# Main 

bottom_left_frame = tk.Frame(main)
bottom_left_frame.place(relx=0, rely=1, anchor="sw")

bottom_right_frame = tk.Frame(main)
bottom_right_frame.place(relx= 1, rely= 1, anchor="se")

exit_button = tk.Button(bottom_right_frame, text= "Exit", command= exit_area, font= FONT)

back_button = tk.Button(bottom_right_frame, text= "Back", font= FONT, command= lambda: back(location))

flee_button = tk.Button(bottom_right_frame, text= "Flee", font= FONT, command= lambda: back(location, flee= True, what= mons))

explore_button = tk.Button(bottom_left_frame, text="Explore", font= FONT, command= explore)

settings_button = tk.Button(bottom_right_frame, text="Settings", font= FONT, command= settings_window)

wipe_save_btn = tk.Button(bottom_right_frame, text= "Clear Save", font= FONT, command= you_sure)

inventory_button = tk.Button(bottom_left_frame, text="Inventory", command= lambda: [open_inventory(), update_inv()], font=FONT)

player1 = Player()

if not any(i.name == "fists" for i in player1.inv["weapon"]):
    player1.add("weapon", Item("weapon", "fists"))

start_screen()

main.mainloop()
