# Webscraping and Analysis of Pokémon Trading Cards
### By: Greg Janesch
### January 14, 2016


## Background and Justification
This project is intended to perform an analysis of cards in the Pokémon Trading Card Game, as well as to attempt to generate new cards via neural networks, as a demonstration of my ability to use Python in multiple ways.  The project code was written in Python 3.4.


### Background: The Pokémon Trading Card Game
The Pokémon Trading Card Game (TCG) is a large portion of the Pokémon franchise, debuting in 1996 in Japan.  The mechanics of the TCG attempt to broadly approximate those in the video games, though there are reasonable adaptations for the medium.

Cards in the TCG belong to one of three general categories:
* Pokémon, which do the actual attacking and are at the center (mechanically) of the game.  There are several components to them
* Energy, which are attached to Pokémon to power their attacks.  Energy can be either 'Basic' (they give one of one type's energy and that's it) or 'Special' (anything that has additional effects or gives more than one energy).
* Trainers, which are a broad class of cards with greatly varying functionality.

One example of each:

<img src="http://cdn.bulbagarden.net/upload/9/94/AlakazamBaseSet1.jpg" width="218px" height="300px" />  <img src="http://cdn.bulbagarden.net/upload/a/a5/FireEnergyBaseSet98.jpg" width="215px" height="300px" />  <img src="http://cdn.bulbagarden.net/upload/c/c6/DefenderUndaunted72.jpg" width="216px" height="300px"/>

It is possible to further separate or label the cards based on other factors.  Trainer cards, in particular, have been subdivided into a few other card types, such as Stadiums (which grant a "field effect" to both players) or Technical Machines (which allow Pokémon to use an attack they can't normally use). However, as all such cards still have the word "Trainer" printed on them, and some are re-releases of older cards from before such distinctions, they are all classified here as trainers.


### Background: Serebii
A Pokémon-oriented website, <a href="www.serebii.net">Serebii</a>, attempts to maintain a comprehensive archive of most facets of the Pokémon franchise.  The website has extensive information, including full listings of all Pokémon cards available.  It is, however, prone to typos and other minor errors.

It was decided, after inspecting the pages for several cards - both the rendered page and the raw HTML - that the formatting and the organization of the pages was regular enough that their listings could be easily scraped.


## Class Definitions
In order to store and organize the card data, four custom classes were created - PokemonCard, EnergyCard, TrainerCard, and PokemonCardAttack - one for each category of cards and one for a Pokémon's attacks.

Energy and trainer cards are relatively simple in terms of how they are represented.  Energy cards can be characterized by the energy they provide, and whether or not they have additional effects; ones that do have additional effects are called 'Special' energy while the remainder are called 'Basic' energy.  Trainers can be characterized by their description text and which subtype of trainer cards they belong to (older cards before such distinctions are just given the subtype of 'trainer').

The PokemonCard class, however, is much more complex.  All cards have a few elements in common - hit points (HP), card type, weaknesses and/or resistances to other types, a retreat cost (energy that has to be discarded to move that card to the sidelines), and other things.  All but a very few cards have attacks, but the attacks themselves are complicated enough that defining a PokemonCardAttack class streamlines the representations.

To better illustrate this, consider one of the more famous cards, the Base Set Charizard:

<img src="http://cdn.bulbagarden.net/upload/4/4e/CharizardBaseSet4.jpg" width="212px" height="300px" />

The way the PokemonCard class is set up, the card looks like this:

CARD NAME: Charizard
120 HP
R TYPE 
ABILITY: Energy Burn: As often as you like during your turn (before your attack), you may turn all Energy attached to Charizard into R Energy for the rest of the turn. This power can't be used if Charizard is Asleep, Confused, or Paralyzed. 
ATTACK: Fire Spin 
&nbsp;&nbsp;COSTS R/R/R/R 
&nbsp;&nbsp;100 DAMAGE 
&nbsp;&nbsp;DESCRIPTION: Discard 2 Energy cards attached to Charizard in order to use this attack.
WEAKNESSES: W (x2) 
RESISTANCES: F ( -30) 
RETREAT COST: 3

Note that there are shorthands used for the energy types (here, 'R' is used for the Fire type).


## Webscraping
The website serebii.net maintains descriptions of all cards in the TCG, with individual webpages allotted for individual cards.  The cards' URLs all follow the same general structure:

    http://www.serebii.net/[expansion]/[card_number]

However, the expansion names don't follow any real pattern, and there is no universal pattern for the card numbers.  

As a result, the webscraping process begins by examining a pair of HTML tables - <a href="http://www.serebii.net/card/english.shtml">one</a> for the main expansions and <a href="http://www.serebii.net/card/engpromo.shtml">one</a> for the promotional sets.  The main tables on the pages lists all of the expansions and contains links to them.  Once it gathers those links, it goes through the expansions' pages, each of which also has an HTML table on it containing full listings and links for the cards in the expansion.  The scraper gathers up all the links for all the cards in this manner.

The next step is then to scrape the pages of the individual cards.  Much like the other pages, the card information is stored in a couple of HTML tables; however, in order to account for some of the shifts in the TCG's card structures - particularly regarding rules about Pokémon variations - these pages are less uniform in their formatting.

The script uses two functions to gather the information needed for processing: <TT>get_card_types()</TT>, which is used to determine whether the target page is describing a Pokémon, an energy, or a trainer card (and, if applicable, which kind of trainer); and <TT>get_card_rows()</TT>, which extracts the rows from the relevant tables for processing.  There are a few cards listed on Serebii which do not have any card types listed; this is presumed to be an error, and inspection reveals that they are all trainer cards, so the program defaults to that classification.

The output of <TT>get_card_types()</TT> is used as a switch, as the functions for turning the HTML into a PokemonCard, EnergyCard, or TrainerCard are separate.  The processing done by <TT>get_trainer()</TT> and <TT>get_energy()</TT> are similar, with the differences lying in the former taking the card type as an argument (for the subtype attribute) and the latter doing a check to see if it is a basic energy or not.  Additionally, the trainer card structure may not actually contain all of the text, as some of the subtypes have quirks that are too easily missed by the scraper.

<TT>get_pokemon()</TT>, however, is trickier.  Because of the varying number of attacks, abilities, and clauses present on cards, the order of operations has to accommodate this by eliminating clauses relating to Pokémon variants (adding to the traits attribute as needed) as well as any empty rows first.  It then works over the first and last couple rows, which hold parts of the card like HP, weaknesses, and retreat cost, since these rows have a constant format and always appear at the start and end of the tables.  The remaining rows are classified as pertaining to either an ability or an attack, and are treated appropriately.

The final output of the scraper is a list of lists, where each sublist contained the card listings for an expansion (expansion names were not preserved).  This output was then saved to a file courtesy of the <TT>pickle</TT> package.


## Text Analyses
Since the cards' information is largely stored in a pure-text form, we can run some fairly straightforward analyses.  The mechanical complexity of the cards means that there are a variety of potential analyses to run; this exercise concerns itself with only a few.  The focus of these analyses is largely on the PokemonCardAttacks, so it is useful to go ahead and collect all of the attack texts:

    attack_text = []
    full_attack_list = []
    type_attack_list = []
    for expansion in full_card_list:
        for card in expansion:
            if type(card).__name__ == "PokemonCard":
                for attack in card.attacks:
                    attack.description = replace_name(attack.description, card.name)
                    full_attack_list.attack(attack)
                    type_attack_list.extend((card.type, attack))

The <TT>replace_name()</TT> function replaces any appearances of the card's name in the description text with the phrase "this pokémon."  The reason for this replacement is partly to generalize the attack descriptions, and partly because some expansions use the phrase while others use the card name.


## Analysis: (Unique) Attack Descriptions
As with the main video games, there are a variety of different attacks in the TCG with similar effects.  This can be emphasized, to some degree, by checking the number of unique attack descriptions versus the full set of descriptions.

First, though, it might be useful to see how many attacks actually have descriptions.  To do this, we simply create a list of all the attacks that have descriptions (which we'll use a bit later) and count how many there are versus how many total attacks there are.

    attack_text = []
    for attack in full_attack_list:
        if attack.description:
            attack_text.append(attack.description.lower())
    
    number_of_attacks = len(full_attack_list)
    number_of_descriptions = len(attack_text)
    percent_with_descriptions = 100 * number_of_descriptions/number_of_attacks

Running this, we see that 9,350 of the 11,842 cards' attacks - roughly 79% - have descriptions.

To determine how many totally unique descriptions there are, not counting attacks without descriptions, we can employ Python's <TT>Counter</TT> function (from the <TT>collections</TT> package) to tabulate the descriptions.

    attack_counter = Counter(attack_text)
    top_ten_attacks = attack_counter.most_common(10)
    top_ten_list = [txt.strip()+" ("+str(cntr) + ")\n" for txt,cntr in top_ten_attacks]

The resulting rankings:

<table>
<tr><td style="text-align:right"> 377 </td><td> flip a coin. if heads, the defending pokémon is now paralyzed. </td></tr>
<tr><td style="text-align:right"> 180 </td><td> the defending pokémon is now asleep. </td></tr>
<tr><td style="text-align:right"> 134 </td><td> flip a coin. if tails, this attack does nothing. </td></tr>
<tr><td style="text-align:right"> 131 </td><td> flip a coin. if heads, the defending pokémon is now confused. </td></tr>
<tr><td style="text-align:right"> 106 </td><td> the defending pokémon is now poisoned. </td></tr>
<tr><td style="text-align:right"> 95 </td><td> the defending pokémon can't retreat during your opponent's next turn.</td></tr>
<tr><td style="text-align:right"> 92 </td><td> this pokémon does 10 damage to itself.  </td></tr>
<tr><td style="text-align:right"> 88 </td><td> flip 2 coins. this attack does 20 damage times the number of heads. </td></tr>
<tr><td style="text-align:right"> 73 </td><td> flip a coin. if heads, the defending pokémon is now poisoned. </td></tr>
<tr><td style="text-align:right"> 69 </td><td> flip 2 coins. this attack does 10 damage times the number of heads. </td></tr>
</table>

There is a lot of coin-based action in these ten descriptions.  Status infliction (confusion, paralysis, sleep, poison) is also quite common, and is often dependent on coin flips.

Note that the 8th and 10th most common descriptions are functionally the same, differing only in how much damage is dealt.  In fact, there are a lot of attacks which function in almost the same manner, with only slight variations in the damage dealt, the number of coins flipped, or which status they inflict.  So we can replace the amount of damage, the inflicted status, and the number of coin flips with dummy strings via regular expressions and see how common these more generalized descriptions are.

    attack_text_2 = [re.sub("[0-9]{1,2}0 damage|[1-9] damage counter(s)?", "_AMOUNT_ damage", attack) for attack in attack_text]
    attack_text_2 = [re.sub("[0-9]{1,2}0 more damage", "_AMOUNT_ more damage", attack) for attack in attack_text_2]
    attack_text_2 = [re.sub("flip [a1-9] coin(s)?", "flip _N_ coins", attack) for attack in attack_text_2]
    
    special_conditions = ["asleep", "burned", "confused", "paralyzed", "poisoned"]
    for status in special_conditions:
        attack_text_2 = [re.sub(status, "_STATUS_", attack) for attack in attack_text_2]
    
    attack_counter_2 = Counter(attack_text_2)
    top_ten_attacks_2 = attack_counter_2.most_common(10)
    top_ten_list_2 = [txt.strip()+" ("+str(cntr) + ")\n" for txt,cntr in top_ten_attacks_2]

The new rankings:

<table>
<tr><td style="text-align:right"> 661 </td><td> flip _N_ coins. if heads, the defending pokémon is now _STATUS_. </td></tr>
<tr><td style="text-align:right"> 448 </td><td> flip _N_ coins. this attack does _AMOUNT_ damage times the number of heads. </td></tr>
<tr><td style="text-align:right"> 383 </td><td> flip _N_ coins. if heads, this attack does _AMOUNT_ more damage. </td></tr>
<tr><td style="text-align:right"> 382 </td><td> the defending pokémon is now _STATUS_. </td></tr>
<tr><td style="text-align:right"> 157 </td><td> this pokémon does _AMOUNT_ damage to itself. </td></tr>
<tr><td style="text-align:right"> 134 </td><td> flip _N_ coins. if tails, this attack does nothing. </td></tr>
<tr><td style="text-align:right"> 95 </td><td> the defending pokémon can't retreat during your opponent's next turn. </td></tr>
<tr><td style="text-align:right"> 66 </td><td> draw a card. </td></tr>
<tr><td style="text-align:right"> 64 </td><td> flip _N_ coins. if tails, this pokémon does _AMOUNT_ damage to itself. </td></tr>
<tr><td style="text-align:right"> 62 </td><td> choose 1 of your opponent's pokémon. this attack does _AMOUNT_ damage to that pokémon. (don't apply weakness and resistance for benched pokémon.). </td></tr>
</table>

The top 10 from the previous listing have now been compressed into the top 6, with four rather different effects now appearing.  Combined, these ten account for 2,452 descriptions, which is only about 26% of all descriptions.


## Analysis: Do Attacks With the Same Name Have the Same Effects?
In the video games, with very few exceptions, attacks behave the same irrespective of which species of Pokémon is using it.  The TCG does not need to abide by this restriction, though attacks that appear in the games and the card game are likely to behave the same

This difference can be illustrated by checking how many unique attack names there are.  We also reuse the regular expressions from before to generalize the attack descriptions.

    attack_name_descriptions = {}
    for attack in full_attack_list:
        name = attack.attack_name
        description = attack.description.lower()
        description = re.sub("[0-9]{1,2}0 damage|[1-9] damage counter(s)?", "_AMOUNT_ damage", description)
        description = re.sub("[0-9]{1,2}0 more damage", "_AMOUNT_ more damage", description)
        description = re.sub("flip [a1-9] coin(s)?", "flip _N_ coins", description)
    if name in attack_name_descriptions:
        attack_name_descriptions[name].append(description)
    else:
        attack_name_descriptions[name] = [description]
    
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

It was discovered that there were 3,923 unique attack names, of which 765 appeared at least twice and all appearances had the same description.  It is likely that at least some of those 765 are from reprints of older cards, but this is not easily testable.  The 11 most frequent of these (there's a tie for 10th place), with descriptions:

| Attack Name | Count |             Description |
| ----------- | ----: | ----------------------- |
| Tackle      |  181  |                         |
| Bite        |  117  |                         |
| Scratch     |  103  |                         |
| Slash       |   80  |                         |
| Headbutt    |   76  |                         |
| Pound       |   62  |                         |
| Fury Swipes |   54  | flip _N_ coins. this attack does _AMOUNT_ damage times the number of heads. |
| Peck        |   52  |                         |
| Razor Leaf  |   49  |                         |
| Flare       |   44  |                         |
| Gnaw        |   44  |                         |

Of these 11, all but 2 (Flare and Gnaw) are actually from the games.  The top seven are also all attacks which are learned by a variety of Pokémon in the games, largely because they are fairly basic attacks that a lot of Pokémon can physically employ (that is, it's easy for a lot of them to scratch or bite things).  The lack of descriptions reflects this somewhat - while Bite, Slash, Headbutt, and Razor Leaf all have additional effects in the games, the TCG doesn't really have the mechanics to transfer them over.  Fury Swipes, the only one in this list with a description, functions as close as possible to the video games, where it lands two to five hits (the number is randomly decided) of constant power.


## Generating New Cards with a Recurrent Neural Network
Inspired <a href="http://www.mtgsalvation.com/forums/creativity/custom-card-creation/612057-generating-magic-cards-using-deep-recurrent-neural">this</a> post, which generated Magic: The Gathering cards using a recurrent neural network (RNN), I attempted to create an RNN which would generate Pokémon cards.  The RNN used here is adapted from code relating to <a href="http://www.wildml.com/2015/10/recurrent-neural-network-tutorial-part-4-implementing-a-grulstm-rnn-with-python-and-theano/">this</a> post.

To start, slightly modified versions of __repr__() for both PokemonCard and PokemonCardAttack were created to create a format better suited for the neural network.  There are two reasons for this.  First, the tokenizer (<TT>nltk.word_tokenize()</TT>) does not split words on slashes, meaning that the energy costs would be read as single words rather than a delimited sequence of energy types. and second, semicolons were used instead of the newline character in order to get nltk.word_tokenize() to acknowledge it. The tokenizer does split on semicolons, meaning it counts them as words, but since they don't otherwise appear in PokémonCard text, this isn't really an issue.