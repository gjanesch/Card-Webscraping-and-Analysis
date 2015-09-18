from webscrapeFunctions import *
import pickle

## Define the URLs
BASE_URL = "http://www.serebii.net"
SECTION_EXPANSIONS = "http://www.serebii.net/card/english.shtml"
SECTION_PROMOS = "http://www.serebii.net/card/engpromo.shtml"

## Create a dictionary of the energy (and other) images, in order to map
## any discovered images in the text
IMAGE_DICT = {"/card/image/colorless.png":"C", "/card/colorless.png":"C",
               "/card/image/darkness.png":"K", "/card/darkness.png":"K",
               "/card/image/dragon.png":"D", "/card/dragon.png":"D",
               "/card/image/electric.png":"E", "/card/electric.png":"E",
               "/card/image/fairy.png":"Y", "/card/fairy.png":"Y",
               "/card/image/fighting.png":"F", "/card/fighting.png":"F",
               "/card/image/fire.png":"R", "/card/fire.png":"R",
               "/card/image/grass.png":"G", "/card/grass.png":"G",
               "/card/image/metal.png":"M", "/card/metal.png":"M",
               "/card/image/psychic.png":"P", "/card/psychic.png":"P",
               "/card/image/water.png":"W", "/card/water.png":"W",
               "/card/image/empty.png":"-", "/card/empty.png":"-",
               "/card/image/shining.png":"-Star",
               "/card/image/g.png":"Galactic", "/card/image/gl.png":"GL",
               "/card/image/e4.png":"E4", "/card/image/fb.png":"FB",
               "/card/image/c.png":"Champion", "/card/image/m.png":"Movie",
               "/card/image/legend.png":"LEGEND", "/card/image/.png":"E",
               "/card/image/galactic.png":"Galactic"}

## Get the list of all Pokémon species (to help determine whether a given
## card is a Pokemon, Energy, or Trainer card).
with open("pokemon_species.txt") as file:
    pokemon_species = [line.strip("\n") for line in file]

## Get the links for the expansions and promotional sets
expansion_list = get_expansion_links(BASE_URL, SECTION_EXPANSIONS)
#promo_list = get_expansion_links(BASE_URL, SECTION_PROMOS)
#expansion_list.extend(promo_list)

full_card_list = []

for expansion in expansion_list:
    expansion_cards = []
    
    ## For each expansion, get the list of links to access each card
    print("NOW WORKING ON EXPANSION: " + expansion[1])
    card_links = get_card_links(expansion[0], BASE_URL)
    
    for link in card_links:
        print("RIPPING " + link)
        
        ## Get the card types and rows
        card_types = get_card_type(link)
        card_rows = get_card_rows(link)
        
        ## Switching code - use card_types to figure out whether the link
        ## is for a Trainer, Energy, or Pokemon card
        if not card_types:
            card = get_trainer(card_rows, IMAGE_DICT)
            card.subtype = ["Trainer"]
        elif card_types[0] in pokemon_species:
            card = get_pokemon(card_rows, IMAGE_DICT, card_types)
        elif card_types[0] == "Energy":
            card = get_energy(card_rows, IMAGE_DICT)
        else:
            card = get_trainer(card_rows, IMAGE_DICT)
            card.subtype = card_types
        expansion_cards.append(card)
    
    full_card_list.append(expansion_cards)

## Open the target file and dump the card list to it
with open("full_card_list_file","wb") as file:
    pickle.dump(full_card_list, file)