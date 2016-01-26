### Greg Janesch, updated 01/14/2016
### Description: Defines four custom object classes used for storing information about a card in the
### Pokemon Trading Card Game.
import re

### Class intended to be used for Pokemon Cards
class PokemonCard():
    
    def __init__(self):
        self.name = str()
        self.traits = []
        self.HP = int()
        self.type = []
        self.abilities = {}
        self.attacks = []
        self.weaknesses = {}
        self.resistances = {}
        self.retreat_cost = int()
    
    def __repr__(self):
        output = "  CARD NAME: {0}\n   {1} HP\n   {2} TYPE \n"
        output = output.format(self.name, self.HP, "/".join(self.type))
        for ability, description in self.abilities.items():
            output += "ABILITY: {0}: {1} \n".format(ability, description)
        for attack in self.attacks:
            output += "  " + str(attack) + "\n"
        output += "  WEAKNESSES: "
        for weakness, adjust in self.weaknesses.items():
            output += "{0} ({1}) ".format(weakness, adjust)
        output += "\n  RESISTANCES: "
        for resistance, adjust in self.resistances.items():
            output += "{0} ({1}) ".format(resistance, adjust)
        output += "\n  RETREAT COST: {0}".format(self.retreat_cost)
        return(output)

    ## Since some of this project involves scraping card texts, a simple built-in way of getting the
    ## text from the abilities and attacks is useful
    def get_descriptions(self):
        ability_text = list(self.abilities.values())
        attack_text = [attack.description for attack in self.attacks]
        return [ability_text, attack_text]

    ## This is an alternate __repr__() function to output the card text, intended to be
    ## used for the neural network code
    def nn_card(self):
        output = "{0} HP # {1} TYPE # "
        output = output.format(self.HP, " / ".join(self.type))
        ability_num = 0
        attack_num = 0
        for ability, description in self.abilities.items():
            descript = description.replace(ability, "of this")
            ability_num += 1
            output += "ABILITY{0}: {1} #".format(ability_num, descript)
        for attack in self.attacks:
            attack_num += 1
            output += "  " + attack.nn_attack(attack_num) + " # "
        output = output.replace(self.name, "this pokémon")
        output += "  WEAKNESSES: "
        for weakness, adjust in self.weaknesses.items():
            output += "{0}({1}) ".format(weakness, adjust)
        output += "#  RESISTANCES: "
        for resistance, adjust in self.resistances.items():
            output += "{0}({1}) ".format(resistance, adjust)
        output += "#  RETREAT COST: {0}".format(self.retreat_cost)
        
        #output = "CARDNAME: {0} # ".format(self.name) + output
        
        return(output)
      

### Since attacks require more information than can be conveniently stored in a dictionary, this
### object is intended to hold all of the information.
class PokemonCardAttack():
    
    def __init__(self):
        self.attack_name = str()
        self.energy_cost = []
        self.base_damage = str()
        self.description = str()
    
    def __repr__(self):
        output = "ATTACK: {0} \n    COSTS {1} \n    {2} DAMAGE \n    DESCRIPTION: {3}"
        output = output.format(self.attack_name, "/".join(self.energy_cost), self.base_damage, self.description)
        return output

    def nn_attack(self, num):
        output = "ATTACK{0}:  COSTS {1},  {2} DAMAGE,  DESCRIPTION: {3} #"
        output = output.format(num, " / ".join(self.energy_cost), self.base_damage, self.description)
        return output



### Class to be used for Energy Cards
class EnergyCard():
    
    def __init__(self):
        self.name = str()
        self.basic = True
        self.description = str()
    
    def __repr__(self):
        if self.basic:
            is_basic = "Basic Energy"
        else:
            is_basic = "Special Energy"
        output = "ENERGY CARD: {0}\n  {1}\n  {2}".format(self.name, is_basic, self.description)
        return output

### Class to be used for Trainer cards (all variants)
class TrainerCard():
    
    def __init__(self):
        self.name = str()
        self.subtype = str()
        self.description = str()
    
    def __repr__(self):
        output = "TRAINER CARD: {0}\n  {1}".format(self.name, self.description)
        return output