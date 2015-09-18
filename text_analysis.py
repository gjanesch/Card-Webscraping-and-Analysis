from collections import Counter
from PokemonCardClasses import *
import re
import pickle

def read_text_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    return lines

def replace_name(text, name):
    replace_text = "this Pokémon"
    changed_text = re.sub(name, replace_text, text)
    return changed_text


TARGET_FILE = "text_analysis.txt"

with open("full_card_list_file","rb") as file:
    full_card_list = pickle.load(file)



## PART 1: ATTACK TEXT ANALYSIS

attack_text = read_text_file("attack_text.txt")
attack_text = [attack.lower() for attack in attack_text]

attack_text = []
full_attack_list = []
type_attack_list = []
for expansion in full_card_list:
    for card in expansion:
        if type(card).__name__ == "PokemonCard":
            for attack in card.attacks:
                attack.description = replace_name(attack.description, card.name)
                if attack.description and not attack.description[-1] == ".":
                    attack.description += "."
                full_attack_list.append(attack)
                type_attack_list.extend((card.type, card.attacks))
            


### Part 1a: See how many attacks have additional descriptions.

## Start by getting all of the attack texts into a list; we want lower-case in case of 
attack_text = []
for attack in full_attack_list:
    if attack.description:
        attack_text.append(attack.description.lower())

number_of_attacks = len(full_attack_list)
number_of_descriptions = len(attack_text)
percent_with_descriptions = 100 * number_of_descriptions/number_of_attacks


## Part 1b: Check for attack descriptions, see how many totally unique ones there are.
attack_counter = Counter(attack_text)
top_ten_attacks = attack_counter.most_common(10)
top_ten_list = [txt.strip()+" ("+str(cntr) + ")\n" for txt,cntr in top_ten_attacks]


## Part 1c: Check for attack descriptions, see if replacing the damage done with a dummy string changes anything
attack_text_2 = [re.sub("[0-9]{1,2}0 damage|[1-9] damage counter(s)?", "_AMOUNT_ damage", attack) for attack in attack_text]
attack_text_2 = [re.sub("( _AMOUNT_ damage plus)? [0-9]{1,2}0 more damage", " _AMOUNT_ more damage", attack) for attack in attack_text_2]
attack_text_2 = [re.sub("flip [a1-9] coin(s)?", "flip _N_ coins", attack) for attack in attack_text_2]
attack_counter_2 = Counter(attack_text_2)
top_ten_attacks_2 = attack_counter_2.most_common(10)
top_ten_list_2 = [txt.strip()+" ("+str(cntr) + ")\n" for txt,cntr in top_ten_attacks_2]


## Write the necessary information to a file for storage
with open(TARGET_FILE, "a") as file:
    file.write("Total number of attacks: " + str(number_of_attacks) + "\n")
    file.write("Number of attacks with descriptions: " + str(number_of_descriptions) + "\n")
    file.write("Percentage of attacks with descriptions: {:.2f}% \n \n".format(percent_with_descriptions))

    file.write("Top 10 attack descriptions: \n")
    for item in top_ten_list:
        file.write(item)
    file.write("\n")

    file.write("Top 10 descriptions with generic damage strings: \n")
    for item in top_ten_list_2:
        file.write(item)
    file.write("\n \n")
        


## PART 2: ATTACK NAMES VS DESCRIPTIONS

attack_name_descriptions = {}
for attack in full_attack_list:
    name = attack.attack_name
    description = attack.description
    description = re.sub("[0-9]{1,2}0 damage|[1-9] damage counter(s)?", "_AMOUNT_ damage", description)
    description = re.sub("[0-9]{1,2}0 more damage", "_AMOUNT_ more damage", description)
    description = re.sub("flip [a1-9] coin(s)?", "flip _N_ coins", description)
    if name in attack_name_descriptions:
        attack_name_descriptions[name].append(attack.description)
    else:
        attack_name_descriptions[name] = [attack.description]

num_unique_names = len(attack_name_descriptions)


## Note: 'SDA' is short for 'single description attack'
SDAs = {}
unique_attack_descriptions = {}
SDA_counts = {}
for name in attack_name_descriptions:
    and_name = attack_name_descriptions[name]
    attack_descriptions = Counter(and_name)
    unique_attack_descriptions[name] = set(attack_descriptions)
    description_count =  len(attack_descriptions)
    if description_count == 1 and len(and_name) > 1:
        SDAs[name] = list(attack_descriptions.keys())[0]
        SDA_counts[name] = len(and_name)

ranked_names = sorted(SDA_counts, key=SDA_counts.get, reverse=True)



with open("attack_descriptions.txt", "a") as file:
    for name in ranked_names:
        file.write("There are " + str(SDA_counts[name]) + " instances of the attack " + name + ":\n" + SDAs[name] + "\n")

with open(TARGET_FILE, "a") as file:
    file.write("Number of unique attack names: " + str(num_unique_names) + "\n")
    file.write("Number of unique attack names where all instances have the same description: " + str(len(SDAs)) + "\n\n")
    file.write("Top 10 unique attacks with unique descriptions: \n")
    for name in ranked_names:
        file.write("There are " + str(SDA_counts[name]) + " instances of the attack " + name + "\n Description:" + SDAs[name] + "\n")
    file.write("\n \n")
