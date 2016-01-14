### Greg Janesch, updated 01/14/2016
### Description: Takes the list of Pokémon cards, extracts the text text for attacks, abilities,
### trainer cards, and energy cards, and writes them to specified, respective files.

from PokemonCardClasses import *
import pickle
import re

## Function description: shorthand for appending something to a file
def append_to_file(object, target_file):
    if not object[-1] == "." and not object[-1] == ")":
        object += "."
    with open(target_file, "a") as file:
        file.write(object + "\n")

def replace_name(text, name, cnt=0):
    replace_text = "this Pokémon"
    changed_text = re.sub(re.escape(name), replace_text, text, cnt)
    return changed_text

with open("full_card_list_file","rb") as file:
    full_card_list = pickle.load(file)


attack_text_file = "attack_text.txt"
ability_text_file = "ability_text.txt"
trainer_text_file = "trainer_text.txt"
energy_text_file = "energy_text.txt"
nn_pokemon_file = "card_texts.csv"

for expansion in full_card_list:
    expansion_no = full_card_list.index(expansion) + 1
    expansion_text = "EXPANSION " + str(expansion_no) + " of " + str(len(full_card_list))
    for card in expansion:
        card_no = str(expansion.index(card) + 1)
        print(expansion_text + ", CARD " + card_no + " of " + str(len(expansion)))
        print(card.name)
        card_class = type(card).__name__
        if card_class == "TrainerCard":
            append_to_file(card.description, trainer_text_file)
        elif card_class == "EnergyCard":
            append_to_file(card.description, energy_text_file)
        elif card_class == "PokemonCard":
            for ability in card.abilities:
                ability_text = replace_name(card.abilities[ability], card.name)
                if ability_text:
                    append_to_file(ability_text, ability_text_file)
            for attack in card.attacks:
                if attack.description:
                    attack_text = replace_name(attack.description, card.name)
                    append_to_file(attack_text, attack_text_file)
            
            with open(nn_pokemon_file, "a") as file:
                file.write(card.nn_card() + "\n")


## Change up the 
with open("card_texts.csv", 'r') as f:
    card_texts = f.readlines()

with open("pokemon_species.txt") as g:
    pokemon_species = g.readlines()

pokemon_species = [species.strip() for species in pokemon_species]

for mon in pokemon_species:
    card_texts = [re.sub(mon, "_othermon_", tex) for tex in card_texts]

with open("card_texts2.csv", 'w') as q:
    q.writelines(card_texts)