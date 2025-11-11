# -----------------------------------------------------------------
# The Emberstone Legacy
# A text-based RPG fulfilling all project requirements.
# -----------------------------------------------------------------

import random
import time
import sys

# -----------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------

def type_text(text, delay=0.03):
    """
    Prints text slowly, one character at a time, for a typewriter effect.
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line after finishing

def prompt(text, options):
    """
    Presents a prompt and a list of valid numbered options.
    Handles invalid input gracefully.
    """
    type_text(text)
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        choice = input("\n> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        else:
            # Error handling for invalid input
            print("That's not a valid choice. Please enter a number from 1 to " + str(len(options)) + ".")

# -----------------------------------------------------------------
# Item Class
# -----------------------------------------------------------------

class Item:
    """
    Represents an item in the game's inventory.
    """
    def __init__(self, name, description, item_type, effect=None):
        self.name = name
        self.description = description
        self.item_type = item_type  # 'potion', 'weapon', 'artifact'
        self.effect = effect  # e.g., ('heal', 25) or ('boost', 'str', 2)

    def __str__(self):
        return self.name

# -----------------------------------------------------------------
# Enemy Class
# -----------------------------------------------------------------

class Enemy:
    """
    Represents an enemy for the player to fight.
    """
    def __init__(self, name, hp, strength, agility, magic, description):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.strength = strength
        self.agility = agility
        self.magic = magic
        self.description = description

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        type_text(f"{self.name} takes {damage} damage! [{self.hp}/{self.max_hp} HP]")

    def attack(self, target):
        """
        A basic enemy attack.
        """
        type_text(f"{self.name} attacks {target.name}!")
        time.sleep(0.5)
        if target.is_defending:
            damage = self.strength + random.randint(1, 4)
            damage = damage // 2  # Halve damage if player is defending
            type_text(f"{target.name} defends against the attack, taking reduced damage.")
        else:
            # Dodge check based on player agility
            dodge_chance = target.stats['agility'] * 0.01
            if random.random() < dodge_chance:
                type_text(f"{target.name} nimbly dodges the attack!")
                return
            damage = self.strength + random.randint(1, 6)
        
        target.take_damage(damage)

# -----------------------------------------------------------------
# Player Class
# -----------------------------------------------------------------

class Player:
    """
    Represents the player character, handling stats, inventory, and combat actions.
    """
    def __init__(self, name):
        self.name = name
        self.char_class = ""
        self.stats = {'strength': 0, 'agility': 0, 'magic': 0}
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.inventory = []
        self.is_defending = False

    def setup_class(self, char_class):
        self.char_class = char_class
        if char_class == "Guardian":
            self.stats = {'strength': 15, 'agility': 8, 'magic': 5}
            self.max_hp = 120
            self.hp = 120
            self.max_mp = 30
            self.mp = 30
            self.inventory.append(Item("Soldier's Sword", "A reliable steel sword.", "weapon", ('boost', 'strength', 2)))
        elif char_class == "Mage":
            self.stats = {'strength': 6, 'agility': 10, 'magic': 18}
            self.max_hp = 80
            self.hp = 80
            self.max_mp = 80
            self.mp = 80
            self.inventory.append(Item("Apprentice Staff", "A smooth wooden staff, warm to the touch.", "weapon", ('boost', 'magic', 2)))
        elif char_class == "Shadow":
            self.stats = {'strength': 10, 'agility': 16, 'magic': 10}
            self.max_hp = 90
            self.hp = 90
            self.max_mp = 50
            self.mp = 50
            self.inventory.append(Item("Twin Daggers", "A pair of sharp, quiet daggers.", "weapon", ('boost', 'agility', 2)))
        
        # Add starter items for everyone
        self.inventory.append(Item("Health Potion", "Restores 25 HP.", "potion", ('heal', 25)))
        self.inventory.append(Item("Health Potion", "Restores 25 HP.", "potion", ('heal', 25)))

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        type_text(f"{self.name} takes {damage} damage! [{self.hp}/{self.max_hp} HP]")

    def show_stats(self):
        print("\n--- YOUR STATS ---")
        print(f"  Name:     {self.name}")
        print(f"  Class:    {self.char_class}")
        print(f"  HP:       {self.hp}/{self.max_hp}")
        print(f"  MP:       {self.mp}/{self.max_mp}")
        print(f"  Strength: {self.stats['strength']}")
        print(f"  Agility:  {self.stats['agility']}")
        print(f"  Magic:    {self.stats['magic']}")
        print("--------------------\n")

    def show_inventory(self):
        """
        Manages the inventory screen.
        Handles viewing, using, and discarding items.
        Handles edge case of empty inventory.
        """
        print("\n--- INVENTORY ---")
        if not self.inventory:
            # Edge Case: Empty inventory
            print("  Your bag is empty.")
            print("-----------------")
            return

        item_counts = {}
        for item in self.inventory:
            item_counts[item.name] = item_counts.get(item.name, 0) + 1
        
        for name, count in item_counts.items():
            print(f"  {name} (x{count})")
        print("-----------------")

        while True:
            print("Type 'use [item]', 'view [item]', 'discard [item]', or 'back'.")
            action = input("> ").lower().strip()

            if action == 'back':
                return
            
            try:
                command, item_name = action.split(' ', 1)
                item_to_act = None
                
                # Find the item in inventory
                for item in self.inventory:
                    if item.name.lower() == item_name:
                        item_to_act = item
                        break
                
                if not item_to_act:
                    print(f"You don't have an item called '{item_name}'.")
                    continue

                if command == 'use':
                    self.use_item(item_to_act)
                    return # Exit inventory screen after using an item
                elif command == 'view':
                    print(f"\n{item_to_act.name}: {item_to_act.description}")
                elif command == 'discard':
                    self.inventory.remove(item_to_act)
                    print(f"You discarded {item_to_act.name}.")
                else:
                    print(f"Invalid command: '{command}'.")

            except ValueError:
                # Error Handling: Input didn't have two parts
                print("Invalid format. Try 'use health potion' or 'back'.")

    def use_item(self, item):
        """
        Applies an item's effect.
        """
        if item.item_type != 'potion':
            print(f"You can't 'use' {item.name} right now.")
            return

        if item.effect[0] == 'heal':
            if self.hp == self.max_hp:
                print("Your health is already full!")
                return
            heal_amount = item.effect[1]
            self.hp += heal_amount
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            print(f"{self.name} uses a {item.name} and restores {heal_amount} HP.")
            print(f"You now have {self.hp}/{self.max_hp} HP.")
            self.inventory.remove(item)
        
        elif item.effect[0] == 'mana':
            if self.mp == self.max_mp:
                print("Your mana is already full!")
                return
            mana_amount = item.effect[1]
            self.mp += mana_amount
            if self.mp > self.max_mp:
                self.mp = self.max_mp
            print(f"{self.name} uses a {item.name} and restores {mana_amount} MP.")
            print(f"You now have {self.mp}/{self.max_mp} MP.")
            self.inventory.remove(item)

    def attack(self, target):
        """
        Standard player attack. Based on Strength and a dice roll.
        Includes a critical hit chance based on Agility.
        """
        type_text(f"{self.name} attacks {target.name}!")
        time.sleep(0.5)

        # Critical hit check
        crit_chance = self.stats['agility'] * 0.015
        base_damage = self.stats['strength'] + random.randint(-2, 5)

        if random.random() < crit_chance:
            type_text("CRITICAL HIT!")
            damage = int(base_damage * 1.8)
        else:
            damage = base_damage
        
        if damage < 1:
            damage = 1
            
        target.take_damage(damage)

    def special_move(self, target):
        """
        Class-specific special moves.
        """
        cost = 15
        if self.mp < cost:
            type_text(f"Not enough MP! (Costs {cost})")
            return False # Failed action

        self.mp -= cost
        type_text(f"{self.name} uses a special move! ({self.mp}/{self.max_mp} MP)")
        time.sleep(0.5)

        if self.char_class == "Guardian":
            damage = self.stats['strength'] + random.randint(5, 10)
            type_text(f"You use **Shield Bash**!")
            type_text(f"It's a powerful blow, staggering the {target.name}.")
            target.take_damage(damage)
        elif self.char_class == "Mage":
            damage = self.stats['magic'] + random.randint(8, 15)
            type_text(f"You conjure a **Fireball**!")
            type_text(f"The flame erupts over the {target.name}.")
            target.take_damage(damage)
        elif self.char_class == "Shadow":
            damage = self.stats['agility'] + random.randint(6, 12)
            type_text(f"You unleash a **Shadow Strike**!")
            type_text(f"You strike from an unexpected angle.")
            target.take_damage(damage)
        
        return True # Successful action

# -----------------------------------------------------------------
# Game Globals
# -----------------------------------------------------------------
player = None
game_flags = {
    "golem_befriended": False,
    "golem_fought": False,
    "golem_sneaked": False,
    "has_sunstone": False
}

# -----------------------------------------------------------------
# Combat System
# -----------------------------------------------------------------

def start_combat(enemy):
    """
    Main turn-based combat loop.
    """
    global player
    type_text(f"\n--- A wild {enemy.name} appears! ---")
    type_text(enemy.description)
    time.sleep(1)

    while player.is_alive() and enemy.is_alive():
        # Reset per-turn flags
        player.is_defending = False
        print("\n--- PLAYER'S TURN ---")
        print(f"{player.name} [HP: {player.hp}/{player.max_hp} | MP: {player.mp}/{player.max_mp}]")
        print(f"{enemy.name} [HP: {enemy.hp}/{enemy.max_hp}]")
        print("What will you do? (attack, special, defend, item, flee)")
        
        action_taken = False
        while not action_taken:
            action = input("> ").lower().strip()

            if action == 'attack':
                player.attack(enemy)
                action_taken = True
            elif action == 'special':
                action_taken = player.special_move(enemy) # This returns True on success, False on failure (e.g., no MP)
            elif action == 'defend':
                player.is_defending = True
                type_text(f"{player.name} takes a defensive stance.")
                action_taken = True
            elif action == 'item':
                player.show_inventory()
                # Using an item doesn't end the turn, so we loop again
                print("\nWhat will you do? (attack, special, defend, item, flee)")
            elif action == 'flee':
                if random.random() > 0.33: # 33% chance to fail
                    type_text("You successfully fled the battle!")
                    return 'fled'
                else:
                    type_text("You couldn't get away!")
                    action_taken = True # Failed attempt costs the turn
            else:
                # Error Handling: Invalid combat command
                print("Invalid command. Choose: attack, special, defend, item, flee")
        
        # Check if enemy died on player's turn
        if not enemy.is_alive():
            type_text(f"\n{enemy.name} has been defeated!")
            return 'victory'
        
        time.sleep(1)

        # --- ENEMY'S TURN ---
        print("\n--- ENEMY'S TURN ---")
        enemy.attack(player)
        
        # Check if player died on enemy's turn
        if not player.is_alive():
            return 'defeat'
        
        time.sleep(1)

    return 'defeat' # Should only be reached if player.is_alive() is false at start


# -----------------------------------------------------------------
# Story Progression / World
# -----------------------------------------------------------------

def character_creation():
    """
    Guides the player through creating their character.
    """
    global player
    type_text("Welcome, apprentice, to the Silver Spire Academy.")
    type_text("Your journey begins now. What is your name?")
    name = input("> ").strip()
    if not name:
        name = "Alex" # Default name
        print(f"No name? Very well, you shall be known as {name}.")
    
    player = Player(name)

    choice = prompt(
        f"\nWelcome, {player.name}. What is your calling?",
        [
            "Guardian: A wielder of steel and shield, high in strength and health.",
            "Mage: A master of the arcane arts, high in magic and mana.",
            "Shadow: A rogue of swift action, high in agility and critical strikes."
        ]
    )
    
    if choice == 1:
        player.setup_class("Guardian")
    elif choice == 2:
        player.setup_class("Mage")
    elif choice == 3:
        player.setup_class("Shadow")

    type_text(f"\nYou have chosen the path of the {player.char_class}.")
    player.show_stats()
    type_text("Press [Enter] to begin your story...")
    input()

def stage_1_academy():
    """
    The first stage of the game.
    """
    type_text("\n--- The Silver Spire ---")
    type_text("Your peaceful studies are shattered by a scream.")
    type_text("You run to the central hall to see Archmage Valerius, your mentor, holding a pulsing black artifact.")
    type_text("His eyes glow with a malevolent purple light. He is corrupted.")
    type_text(f"\"Apprentices!\" he booms, his voice distorted. \"The 'Shadow Ember' has shown me *true* power! Join me, or be... purified.\"")
    type_text("Corrupted gargoyles animate and block the main entrance. You must find another way out.")

    choice = prompt(
        "\nWhat do you do?",
        [
            "Run to the library to research the 'Shadow Ember'.",
            "Flee through the dormitory service tunnels.",
            "Try to reason with Archmage Valerius."
        ]
    )

    if choice == 1:
        type_text("\nYou dash to the library. You find a passage: 'Only the Sunstone of the Golems can counter the Shadow Ember.'")
        type_text("A small, corrupted sapling bursts from a planter and attacks!")
        enemy = Enemy("Corrupted Sapling", 20, 5, 5, 0, "A small tree, twisted with dark energy.")
        result = start_combat(enemy)
        if result == 'defeat':
            return 'game_over'
        type_text("You defeat the creature and escape the academy, your goal clear: find the Sunstone.")
    elif choice == 2:
        type_text("\nYou duck into the tunnels. It's dark and damp, but you know the way.")
        type_text("You emerge outside the academy walls, the screams fading behind you.")
        type_text("You know you can't abandon your home. You recall old lessons... 'The Sunstone... in the Crystal Caves... it can repel darkness.'")
    elif choice == 3:
        type_text(f"\"Master Valerius!\" you cry. \"This isn't you!\"")
        type_text(f"He turns. \"Isn't it, {player.name}? Or is it *finally* me?\"")
        type_text("He raises his hand and blasts you with dark energy.")
        player.take_damage(25)
        type_text("The pain is immense, but you are saved by your House Prefect, who shoves you through a hidden passage.")
        type_text("\"Go!\" he yells. \"Find... the Sunstone...\" He is consumed by shadows.")
        type_text("You flee, wounded and grim, with your mission clear.")

    # Give player an item for the next stage
    type_text("\nYou find a 'Mana Potion' on the ground as you flee.")
    player.inventory.append(Item("Mana Potion", "Restores 25 MP.", "potion", ('mana', 25)))
    
    return 'stage_2' # Progress to the next stage

def stage_2_woods():
    """
    The second stage of the game.
    """
    type_text("\n--- The Whispering Woods ---")
    type_text("To reach the Crystal Caves, you must pass through the Whispering Woods.")
    type_text("The woods are eerily quiet, the trees twisted and grey.")
    type_text("You see a large, shadowy figure move between the trees.")
    
    enemy = Enemy("Shadow Stalker", 40, 10, 14, 5, "A beast of pure shadow with glowing red eyes.")
    result = start_combat(enemy)
    
    if result == 'defeat':
        return 'game_over'
    elif result == 'fled':
        type_text("You escape the beast, but you feel like you lost a part of your resolve.")
    elif result == 'victory':
        type_text("The beast dissolves into nothing.")
        type_text("You find a 'Greater Health Potion' on its remains.")
        player.inventory.append(Item("Greater Health Potion", "Restores 50 HP.", "potion", ('heal', 50)))

    type_text("\nDeeper in the woods, you find the path blocked by a giant, ancient Treant.")
    type_text("\"Halt, little one,\" it rumbles. \"The corruption of the Spire seeps into my roots. I am in pain.\"")
    
    choice_options = ["Offer to help purify its roots.", "Try to sneak around it.", "Threaten it to move."]
    
    # Check for Mage-specific option
    if player.char_class == "Mage":
        choice_options.insert(1, "[MAGE] Use your arcane knowledge to cleanse the corruption.")
    
    choice = prompt("\nWhat do you do?", choice_options)

    if player.char_class == "Mage" and choice == 2:
        type_text("\nYou channel your magic, focusing on the Treant's roots.")
        type_text("It costs you energy, but the dark magic recedes.")
        player.mp -= 20
        type_text(f"\"You... have my thanks, little mage.\" The Treant rumbles. \"My strength is yours.\"")
        type_text("The Treant grants you the 'Barkskin Blessing'! (Max HP +10)")
        player.max_hp += 10
        player.hp += 10
    elif choice == 1:
        type_text("\nYou spend an hour picking away the corrupted vines. It's hard work.")
        type_text("\"A kind soul. Rare. Go, and take this.\"")
        type_text("The Treant gives you a 'Seed of Life'.")
        player.inventory.append(Item("Seed of Life", "A magical seed that grants a one-time, full heal.", "potion", ('heal', 999)))
    elif player.char_class == "Mage" and choice == 3: # Sneak option
        type_text("You're a mage, not a rogue. You try to sneak, but trip on a root.")
        type_text("\"Foolish!\" the Treant rumbles, and smacks you with a branch.")
        player.take_damage(10)
        type_text("You scramble away, bruised and embarrassed.")
    elif player.char_class != "Mage" and choice == 2: # Sneak option
        if player.stats['agility'] > 12:
            type_text("You use the shadows and your light feet to slip past the great tree unnoticed.")
        else:
            type_text("You try to sneak, but trip on a root.")
            type_text("\"Foolish!\" the Treant rumbles, and smacks you with a branch.")
            player.take_damage(10)
            type_text("You scramble away, bruised and embarrassed.")
    else: # Threaten
        type_text("\"Move, or I will make you!\" you shout.")
        type_text("\"Impudent!\" The Treant strikes you with a branch for your arrogance.")
        player.take_damage(15)
        type_text("It lets you pass, but you feel a sense of shame.")

    type_text("\nYou exit the woods and see the entrance to the caves.")
    return 'stage_3' # Progress to stage 3

def stage_3_caves():
    """
    The third stage. This is the major branching point.
    """
    global game_flags
    type_text("\n--- The Crystal Caves ---")
    type_text("The caves glitter with energy. You follow a path to a large, open cavern.")
    type_text("In the center is a massive, stone Golem, humming with power. It guards a glowing, golden crystal on a pedestal: the Sunstone.")
    type_text("\"WHO. DISTURBS. THE. GUARDIAN.\" its voice echoes in your head.")

    choice_options = [
        "\"I must take the Sunstone! It's an emergency!\"",
        "Attack the Golem.",
    ]

    # Add special choices based on stats
    if player.stats['magic'] > 15:
        choice_options.append("[MAGIC > 15] Try to reason with it using arcane logic.")
    if player.stats['agility'] > 15:
        choice_options.append("[AGILITY > 15] Try to sneak past it and grab the stone.")
    
    choice = prompt("\nThe Golem blocks your path.", choice_options)

    # Resolve choice
    action = 'fight' # default
    if choice == 1:
        type_text("\"'EMERGENCY'. IS. NOT. AN. EXCUSE. FOR. THEFT.\"")
        action = 'fight'
    elif choice == 2:
        type_text("\"SO. BE. IT.\"")
        action = 'fight'
    
    # Check special choices
    if player.stats['magic'] > 15 and choice == 3:
        action = 'talk'
    elif player.stats['agility'] > 15 and choice == (4 if player.stats['magic'] > 15 else 3):
        action = 'sneak'
    elif choice == 3 or choice == 4: # Handle failed stat checks
        type_text("You don't have the skill to back up your words. The Golem sees you as a threat.")
        action = 'fight'


    # --- Resolve Branching Path ---
    
    if action == 'talk':
        # Path 1: Befriend
        type_text("\nYou explain the Shadow Ember, the corruption of Valerius, and the threat to the Spire.")
        type_text("You speak of the balance of magic and the Golem's duty.")
        type_text("It stands silent for a full minute.")
        type_text("\"THE. SPIRE. IS. A. KEY. TO. THE. BALANCE. YOUR. LOGIC. IS. SOUND.\"")
        type_text("\"TAKE. A. SHARD. OF. THE. SUNSTONE. IT. WILL. BE. ENOUGH. NOW. GO.\"")
        type_text("The Golem steps aside and chips off a piece of the stone for you.")
        player.inventory.append(Item("Sunstone Shard", "A piece of the Sunstone, glowing with pure light.", "artifact"))
        game_flags["golem_befriended"] = True
        game_flags["has_sunstone"] = True
        
    elif action == 'sneak':
        # Path 2: Sneak
        type_text("\nYou use every shadow, moving silently.")
        type_text("The Golem is powerful, but slow. It scans the room, but you are a whisper.")
        type_text("You get to the pedestal, grab the entire Sunstone, and dash for the exit!")
        type_text("\"THIEF!\" its roar shakes the cave, but you are too fast.")
        player.inventory.append(Item("The Sunstone", "The complete Sunstone. It feels heavy.", "artifact"))
        game_flags["golem_sneaked"] = True
        game_flags["has_sunstone"] = True
        
    else: # action == 'fight'
        # Path 3: Fight
        type_text("\nYou ready your weapon. The Crystal Golem activates!")
        enemy = Enemy("Crystal Golem", 100, 15, 3, 10, "A massive, ancient protector made of enchanted stone.")
        result = start_combat(enemy)
        
        if result == 'defeat':
            return 'game_over'
        
        type_text("The Golem crumbles to dust.")
        type_text("You feel a pang of regret... it was only doing its duty.")
        type_text("You take the Sunstone from the pedestal.")
        player.inventory.append(Item("The Sunstone", "The complete Sunstone. It feels heavy.", "artifact"))
        game_flags["golem_fought"] = True
        game_flags["has_sunstone"] = True

    type_text("\With the artifact in hand, you race back to the Silver Spire.")
    return 'stage_4' # Progress to the final stage

def stage_4_spire():
    """
    The final confrontation and ending choices.
    """
    type_text("\n--- The Corrupted Spire ---")
    type_text("You arrive back at the Academy. It is dark, twisted. Shadow magic holds it captive.")
    type_text("You find Archmage Valerius in the main hall, floating above the ground, the Shadow Ember fused with his staff.")
    type_text(f"\"So, the little apprentice returns,\" he sneers. \"You are too late. I amASCENDANT!\"")

    if game_flags["golem_befriended"]:
        type_text("\"Master, please!\" you shout, holding up the Sunstone Shard. \"There is still good in you!\"")
        type_text(f"\"THAT. WEAKNESS. WAS. PURGED.\" he roars, and attacks!")
    else:
        type_text("\"It's over, Valerius!\" you yell, raising the Sunstone.")
        type_text(f"\"GIVE. ME. THAT. TOY.\" he snarls, and lunges.")

    # Final Boss
    boss = Enemy("Archmage Valerius", 150, 18, 12, 25, "Your former master, consumed by the Shadow Ember's power.")
    result = start_combat(boss)
    
    if result == 'defeat':
        return 'game_over'

    type_text("\nWith a final, agonizing scream, Valerius collapses. The Shadow Ember clatters to the floor, its purple light dimming.")
    type_text("Valerius whispers, \"...thank you...\" and his body turns to dust.")
    type_text("The Spire begins to stabilize, the shadows receding.")
    type_text("You are left alone with the Shadow Ember.")
    type_text("It whispers to you. It promises power. Knowledge. Everything Valerius wanted.")

    # --- Final Choice & Endings ---
    
    final_choice_options = [
        "Destroy the Shadow Ember with the Sunstone.",
        "Take the Shadow Ember. Claim its power for yourself."
    ]
    
    # Add the "Good" option only if the Golem was befriended
    if game_flags["golem_befriended"]:
        final_choice_options.insert(0, "Use the Sunstone Shard to *purify* the Shadow Ember.")

    final_choice = prompt("\nThe artifact pulses. What is your final decision?", final_choice_options)

    if game_flags["golem_befriended"]:
        if final_choice == 1:
            return 'ending_good'
        elif final_choice == 2:
            return 'ending_neutral'
        elif final_choice == 3:
            return 'ending_bad'
    else:
        if final_choice == 1:
            return 'ending_neutral'
        elif final_choice == 2:
            return 'ending_bad'
            
    return 'ending_neutral' # Failsafe

# -----------------------------------------------------------------
# Endings
# -----------------------------------------------------------------

def game_over():
    """
    Handles the player's death.
    """
    type_text(f"\nYour vision fades to black...")
    type_text("Your courage was great, but the darkness was stronger.")
    type_text("The Silver Spire falls, and the world is one step closer to shadow.")
    type_text("\n--- GAME OVER ---")

def ending_good():
    """
    Ending 1: The "Good" ending.
    (Requires befriending the Golem)
    """
    type_text("\nYou hold the Sunstone Shard to the Ember.")
    type_text("Instead of destruction, you channel your will, your magic, your *compassion*.")
    type_text("The shard burns bright. The dark artifact screams, and then... is silent.")
    type_text("The black crystal turns a pure, translucent white. The 'Heartstone'.")
    type_text("You have not just defeated the darkness, you have redeemed it.")
    type_text("\nYou rebuild the Silver Spire, not as a simple apprentice, but as its new, wise leader.")
    type_text("Your reign is one of balance and understanding, and the academy thrives for a thousand years.")
    type_text("\n--- THE END (Path of the Sage) ---")

def ending_neutral():
    """
    Ending 2: The "Neutral" ending.
    (Requires fighting/sneaking, and destroying the Ember)
    """
    type_text("\nYou reject the Ember's whispers.")
    type_text("You strike it with the Sunstone. There is a blinding flash of light, and the artifact shatters, exploding into dust.")
    type_text("The magic is broken. The Spire is saved.")
    type_text("You stand tall as the Hero of the Spire. You are celebrated, lauded, and made the new Archmage.")
    type_text("But... you always wonder. You destroyed the threat, but what knowledge, what power, was lost that day?")
    type_text("Your rule is effective, but tinged with a cold pragmatism.")
    type_text("\n--- THE END (Path of the Victor) ---")

def ending_bad():
    """
    Ending 3: The "Bad" ending.
    (Requires taking the Ember's power)
    """
    type_text("\n...Yes. Why destroy such power?")
    type_text("Valerius was just weak. You are strong.")
    type_text("You reach out and take the Shadow Ember. It fuses with your hand, your arm, your very soul.")
    type_text("The power is agonizing... and ecstatic.")
    type_text("The Silver Spire is saved, yes. But its new Archmage is far more terrible, and far more *effective*, than the last.")
    type_text("The world will not fall to shadow. It will be *conquered* by it.")
    type_text("\n--- THE END (Path of the Tyrant) ---")

# -----------------------------------------------------------------
# Main Game Loop
# -----------------------------------------------------------------

def main():
    """
    The main game function that controls the flow.
    """
    # 1. Character Creation
    character_creation()
    
    # 2. Story Progression
    game_stage = 'stage_1'
    
    while game_stage != 'game_over' and not game_stage.startswith('ending'):
        if game_stage == 'stage_1':
            game_stage = stage_1_academy()
        elif game_stage == 'stage_2':
            game_stage = stage_2_woods()
        elif game_stage == 'stage_3':
            game_stage = stage_3_caves()
        elif game_stage == 'stage_4':
            game_stage = stage_4_spire()
            
    # 3. Game Conclusion
    if game_stage == 'game_over':
        game_over()
    elif game_stage == 'ending_good':
        ending_good()
    elif game_stage == 'ending_neutral':
        ending_neutral()
    elif game_stage == 'ending_bad':
        ending_bad()

    print("\nThank you for playing The Emberstone Legacy!")

# -----------------------------------------------------------------
# Run the Game
# -----------------------------------------------------------------
if __name__ == "__main__":
    main()