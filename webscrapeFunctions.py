### Greg Janesch, updated 08/20/2015
### Description: a collection of functions intended to scrape all of serebii.net's Pokemon
### TCG info


from bs4 import BeautifulSoup
import urllib.request
import re
from PokemonCardClasses import *

### Function description: generates the soup from a given url
def get_soup(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup


### Function description: gets the energy symbols out of some description text and returns a
### list of the string equivalents defined in a dictionary
def energy_as_strings(rows, energy_dict):
    energy_images = rows.find_all("img")
    energy = [source["src"].lower() for source in energy_images]
    energy = [energy_dict[img] for img in energy]
    return energy


### Function description: Takes the urls for the english set and promo lists, and returns the
### links and names for each individual set/promotional set
def get_expansion_links(BASE_URL, section_url):
    soup = get_soup(section_url)
    target_table = soup.find("table", attrs={"width":"100% border="})
    rows = target_table.find_all("tr")
    expansion_list = []
    for tr in range(1,len(rows)):
        row = rows[tr]
        expansion = [BASE_URL + row.a["href"]]
        expansion.extend([text for text in row.stripped_strings])
        expansion_list.append(expansion)
    return expansion_list


### Function description: Serebii's card pages have card "types" listed (e.g., "Trainer" or a
### particular species of Pokemon).  This function extracts those types, if available.
def get_card_type(card_url):
    card_type_list = []
    soup = get_soup(card_url)
    type_links = soup.find("td", attrs = {"width":"160"})
    if not type_links:
        type_links = soup.find("td", attrs = {"width":"125"})
    if type_links:
        type_links = type_links.find_all("a")
        for link in type_links:
            card_type = [x for x in link.stripped_strings]
            if len(card_type) > 1:
                type_image = link.img["src"]
                if type_image == "/card/image/star.png":
                    card_type = "Pokémon-star"
                else:
                    card_type = "Pokémon SP"
            else:
                card_type = card_type[0][6:-6]
            card_type_list.append(card_type)
    return card_type_list



### Function description: Given the URL for one of the expansions, scrape the webpage for the
### links of all the individual cards.
def get_card_links(expansion_url, base_url):
    
    card_links = []
    
    soup = get_soup(expansion_url)
    expansion_rows = soup.find_all("td", attrs = {"width":"20%"})
    expansion_rows.pop(0)
    
    for row in expansion_rows:
        link = base_url + row.a["href"]
        card_links.append(link)
    
    return card_links
            

### Function description: The HTML for the cards is organized in a <table> element, with the
### various rows containing the data.  This function extracts all of the rows of that table.
def get_card_rows(card_url):
    soup = get_soup(card_url)
    target_table = soup.find("table", attrs={"width":"100%","border":"0","cellspacing":"0","cellpadding":"5"})
    target_rows = target_table.find_all("tr")[1:]
    return target_rows


### Function description: Processes the output of get_rows() and extracts the information to
### populate an EnergyCard() object.
def get_energy(energy_rows, energy_dict):
    
    energy_card = EnergyCard()
    
    energy_card.name = energy_rows[1].b.get_text()
    if not energy_card.name.endswith("Energy"):
        energy_card.name += " Energy"
    
    if not energy_rows[1].i.get_text() == "":
        energy_card.basic = False
    
    energy = energy_as_strings(energy_rows[3], energy_dict)
    
    description_text = str(energy_rows[3].p)
    for n in range(len(energy)):
        description_text = re.sub("<img.*?>", energy[n], description_text, count = 1)
    
    description_text = re.sub("<.*?>", "", description_text)
    
    energy_card.description = description_text
    
    return energy_card


### Function description: Processes the output of get_rows() and extracts the information to
### populate an TrainerCard() object.
def get_trainer(trainer_rows, energy_dict):
    
    trainer_card = TrainerCard()
    
    trainer_card.name = trainer_rows[1].td.get_text().strip()
    
    energy = energy_as_strings(trainer_rows[3], energy_dict)
    description_text = str(trainer_rows[3].p)
    for n in range(len(energy)):
        description_text = re.sub("<img.*?>", energy[n], description_text, count = 1)
    
    description_text = re.sub("<.*?>", "", description_text).strip()
    
    trainer_card.description = description_text
    
    return trainer_card


### Function description: Processes the output of get_rows() and extracts the information to
### populate an EnergyCard() object.
def get_pokemon(pokemon, energy_dict, card_types):
    
    ## This is a bunch of clauses that concern how certain cards behave in the game.  In the
    ## HTML, they are their own rows and throw off the behavior of the rest of this function.
    MEGA_CLAUSE = "When 1 of your Pokémon becomes a Mega Evolution Pokémon, your turn ends."
    EX_CLAUSE1 = "When Pokémon-ex has been Knocked Out, your opponent takes 2 Prize cards."
    EX_CLAUSE2 = "When Pokémon-EX has been Knocked Out, your opponent takes 2 Prize cards."
    BABY_CLAUSE = {"Baby Pokémon":"If this Baby Pokémon is your Active Pokémon and your opponent tries to attack, your opponent flips a coin (before doing anything else required in order to use that attack). If tails, your opponent's turn ends without an attack."}
    HOLON_CLAUSE1 = "You may attach this as an Energy card from your hand to 1 of your Pokémon that already has an Energy card attached to it. When you attach this card, return an Energy card attached to that Pokémon to your hand. While attached, this card is a Special Energy card and provides every type of Energy but 2 Energy at a time. (Has no effect other than providing Energy.)"
    HOLON_CLAUSE2a = "You may attach this as an Energy card from your hand to 1 of your Pokémon. While attached, this card is a Special Energy card and provides  Energy."
    HOLON_CLAUSE2b = "You may attach this as an Energy card from your hand to 1 of your Pokémon. While attached, this card is a Special Energy card and provides C Energy."
    ARCEUS_CLAUSE = "You may have any number of Arceus cards in your deck"
    BREAK_CLAUSE = "BREAK retains the attacks, Abilities, Weakness, Resistance, and Retreat Cost of its previous Evolution."
    
    pokemon_card = PokemonCard()
    
    pokemon_card.traits = card_types
    
    ## Remove all undesired rows
    pokemon_rows = []
    for row in pokemon:
        row_text = row.get_text().strip()
        if row_text == MEGA_CLAUSE:
            pokemon_card.traits.append("Mega")
        elif row_text == EX_CLAUSE1 or row_text == EX_CLAUSE2 or row_text == ARCEUS_CLAUSE:
            pass
        elif row_text.startswith("If this Baby Pokémon is your Active Pokémon"):
            pokemon_card.abilities.update(BABY_CLAUSE)
        elif row_text == "You may have up to 4 Basic Pokémon cards in your deck with Unown in their names":
            pass
        elif row_text == HOLON_CLAUSE1:
            pokemon_card.abilities.update({"Holon Pokémon":HOLON_CLAUSE1})
        elif row_text == HOLON_CLAUSE2a:
            pokemon_card.abilities.update({"Holon Pokémon":HOLON_CLAUSE2b})
        elif row_text.startswith("You can't have more than "):
            pass
        elif "#" in row_text:
            pass
        elif row_text.endswith("Lv. X can use any attack, Poké-Power, or Poké-Body from its previous Level."):
            pass
        elif row_text.endswith("Once you have both cards, place both on your Bench"):
            pass
        elif row_text.endswith("BREAK retains the attacks, Abilities, Weakness, Resistance, and Retreat Cost of its previous Evolution."):
            pass
        elif not row_text == "":
            pokemon_rows.append(row)
    
    pokemon_rows = pokemon_rows[:-1]
    
    ## The first of the remaining rows contains the card's name and the HP
    top_row = pokemon_rows[0]
    pokemon_card.name = top_row.find("td").b.get_text().strip()
    HP = top_row.find("font", attrs={"color":"#FF0000"}).get_text().strip()
    if not HP[:-3] == "":
        pokemon_card.HP = int(HP[:-3])
    
    ## The next row contains the type(s)
    pokemon_card.type = energy_as_strings(top_row.find_all("td")[-1], energy_dict)
    pokemon_rows = pokemon_rows[1:]
    
    ## Extract the retreat cost from the last row, then remove it from the list
    retreat_cost = pokemon_rows[-1].find_all("img")
    pokemon_card.retreat_cost = len(retreat_cost)
    pokemon_rows = pokemon_rows[:-1]
    
    ## Extract the weaknesses and resistances
    weak_resist = pokemon_rows[-1].find_all("td")
    weakness_list = weak_resist[1].find_all("img")
    resistance_list = weak_resist[3].find_all("img")
    
    if weak_resist[1].get_text() == "":
        weakness_adj = "x2"
    else:
        weakness_adj = weak_resist[1].get_text()
    
    resistance_adj = weak_resist[3].get_text()
    
    for image in weakness_list:
        weakness = energy_dict[image["src"]]
        pokemon_card.weaknesses[weakness] = weakness_adj
    for image in resistance_list:
        resistance = energy_dict[image["src"]]
        pokemon_card.resistances[resistance] = resistance_adj
    
    pokemon_rows = pokemon_rows[:-2]
    
    ## The remaining rows should be either moves or abilities; switch between them as appropriate
    while len(pokemon_rows) > 0:
        next_row = pokemon_rows[0].find_all("td")
        if not next_row[0].img == None and next_row[0].img["src"] in energy_dict.keys():
            attack = get_attack(next_row, energy_dict)
            pokemon_card.attacks.append(attack)
        elif next_row[0].get_text().strip() == "" and next_row[0].img == None:
            attack = get_attack(next_row, energy_dict)
            pokemon_card.attacks.append(attack)
        else:
            ability = get_ability(next_row, energy_dict)
            pokemon_card.abilities.update(ability)
        pokemon_rows = pokemon_rows[1:]
    
    return pokemon_card


### Function description: Processes one of the HTML rows in order to extract the information
### about an attack and populate a PokemonCardAttack object.
def get_attack(attack_row, energy_dict):
    
    attack = PokemonCardAttack()
    
    ## Get the energy cost of the attack from the first <td> element
    attack.energy_cost = energy_as_strings(attack_row[0], energy_dict)
    
    ## From the next <td>, get the attack name and (if present) description
    attack.attack_name = attack_row[1].b.get_text().strip()
    if not attack.attack_name == attack_row[1].get_text().strip():
        description_text = str(attack_row[1])
        energy = energy_as_strings(attack_row[1], energy_dict)
        description_text = re.sub(".*?br/>", "", description_text, count = 1)
        for n in range(len(energy)):
            description_text = re.sub("<img.*?>", energy[n], description_text, count = 1)
        description_text = re.sub("<.*?>", "", description_text).strip()
        attack.description = description_text
    
    ## From the last element, get the attack's base damage, if present
    attack.base_damage = attack_row[2].get_text().strip()
    if attack.base_damage == "":
        attack.base_damage = "0"
    
    return attack

### Function description: Processes one of the HTML rows in order to extract the information
### about an ability and return it as a dictionary object.
def get_ability(ability_row, energy_dict):
    
    ## Since abilities/powers/bodies come in a couple different 
    if ability_row[0].img or ability_row[0].get_text().strip()[0] == "P":
        ability_name = ability_row[1].b.get_text().strip()
        ability_description = str(ability_row[1].font)
        ability_description = re.sub(".*br/>|<i>|</i>","", ability_description)[:-7].strip()
    else:
        ability_name = ability_row[0].get_text().strip()
        ability_description = str(ability_row[1])[19:-6]
        ability_description = re.sub("<i>|</i>", "", ability_description)
    
    ## If there are any energy images present 
    ability_energy = energy_as_strings(ability_row[1], energy_dict)
    if ability_energy:
        for n in range(len(ability_energy)):
            ability_description = re.sub("<.*?>", ability_energy[n], ability_description, count = 1)
    
    return {ability_name:ability_description}