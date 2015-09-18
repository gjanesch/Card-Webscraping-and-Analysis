Webscraping and Analysis of Pokémon Trading Cards

This project is intended to perform a basic analysis of cards in the Pokémon Trading Card Game.  The project code was written in Python 3.4.

## Background: The Pokémon Trading Card Game
The Pokémon Trading Card Game (TCG) is a trading card game which forms a portion of the Pokémon franchise.  The mechanics of the TCG attempt to broadly approximate those in the video games, with reasonable changes for the medium.

Cards belong to one of three general categories:
* Pokémon, which do the actual attacking and are at the center (mechanically) of the game.
* Energy, which are attached to Pokémon to power their attacks.
* Trainers, which is a broad classification covering a large number of cards designed to affect the flow of the game in various ways.

These categories can be further subdivided, as the game has introduced variations or labels for large subsets of cards.  For instance, Stadiums are a subtype of trainer card which introduce a "field effect" that applies to both players, while the TM subtype can be attached to a Pokémon for a single turn in order to give an attack that it could not otherwise have.


## Background: Serebii
A Pokémon-oriented website, <a href="www.serebii.net">Serebii</a>, attempts to be a comprehensive archive of most facets of the Pokémon franchise.  The information it has is considerable, including listings of all Pokémon cards available.  It is, however, prone to typos and other minor issues.

After inspecting their pages for a few assorted cards (both the raw HTML and browser-rendered version), it was determined that Serebii's organization of the cards' information was regular enough that it would be a good candidate for webscraping.


## Class definitions
In order to store and organize the card data effectively, four custom classes were created - PokemonCard, EnergyCard, TrainerCard, and PokemonCardAttack - one for each category of cards and one for a Pokémon's attacks.

Because they are generally quite simple, the EnergyCard and TrainerCard classes only have a few attributes.  Both have <TT>name</TT> and <TT>description</TT> attributes, intended to hold the card name and description of card effects respectively.  EnergyCard also has a boolean <TT>basic</TT> attribute, which has a specific meaning in the TCG (as basic and special energy cards behave and are affected differently).  TrainerCard contains a <TT>subtype</TT> attribute for handling the multitude of variations of trainer cards.

The PokemonCard class, however, stores nine separate attributes as a result of the Pokémon cards' relative mechanical complexity.  These attributes are nearly sufficient to cover the functionality of the card; the only issue remaining is that the card's attacks are more complicated than Python's basic data types can conveniently handle.  As such, the PokemonCardAttack class holds the four data points which define an attack (energy cost, damage, name, and description of effects, if any).


## Webscraping
The website serebii.net maintains descriptions of all cards in the TCG, with individual webpages allotted for individual cards.  The cards' URLs all follow the same general structure:

http://www.serebii.net/[expansion]/[card_number]

However, the expansion names don't follow any real pattern, and while the card numbers are mostly three-digit numbers, there are a few anomalous cases.  As a result, the webscraping process began by examining an HTML table (on <a href="http://www.serebii.net/card/english.shtml">this</a> page) that lists and links to all of the card expansions.  Similarly, on each of the expansions' pages, the individual card links are listed and were scraped.

The next step is then to scrape the pages of the individual cards.  Two functions are used for this.

One is <TT>get_card_rows()</TT>, which goes into the HTML and extracts the table where the information is located.  Conveniently, no matter which kind of card it is, it is always the same table, so the function is pretty simple.  The function then extracts the rows of the table, which are fed to more specialized functions for processing.

The other function is <TT>get_card_types()</TT>.  On most cards' pages, there is a link for "Other ____ Cards."  The function extracts the "____" terms and check what the first one corresponds to - either "Trainer," "Energy," or a species of Pokémon.  That is used for the switching code, as well as noting other potential subsets of interest.

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

There are a few cards listed on Serebii which do not have any card types listed; this is presumed to be an error, so such cards are designated as trainers, and handled as such.

Additionally, in order to properly rip the cards, we need to handle the presence of images (especially in the context of energy symbols) in the text.  The <TT>IMAGE_DICT</TT> object is a dictionary which is intended to use for substituting the \<img\> tags in the HTML for a corresponding string.

The exact procedures of <TT>get_trainer()</TT> and <TT>get_energy()</TT> functions are largely the same: get the card name, basic/subtype, and description attributes from the only rows present, and then populate the necessary objects.

(Note: The variability of the game over time means that certain trainer card types cannot be reliably unified into a single model, based on the available information from Serebii.  As such, some of the Trainer cards' descriptions do not contain a full listing of the actual effects.)

The Pokémon are trickier, however.  Many variants of cards come with additional clauses that have to be accounted for in the program.  Additionally, the total numbers of abilities and attacks on a card are not constant.  The <TT>get_pokemon()</TT> function handles this by first filtering out all unneeded rows, then extracting all attributes aside from the abilities and attacks (and removing those rows), and then checking the remaining rows and assigning them to the abilities or attacks attribute as appropriate.

The ultimate result was a list of lists, where each sublist corresponded to an expansion (names were not preserved).  This was then dumped to a file courtesy of the <TT>pickle</TT> package.


## Text Analyses
Since the cards' information is largely stored in a pure-text form, we can run some fairly straightforward analyses.  The mechanical complexity of the cards means that there are a variety of potential analyses to run, though this report only performs a few.

The focus of these analyses is largely on the PokemonCardAttacks, so it is useful to go ahead and collect all of the attack texts:

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

First, though, it might be useful to see how many attacks actually have descriptions.

    attack_text = []
    for attack in full_attack_list:
        if attack.description:
            attack_text.append(attack.description.lower())
    
    number_of_attacks = len(full_attack_list)
    number_of_descriptions = len(attack_text)
    percent_with_descriptions = 100 * number_of_descriptions/number_of_attacks

Running this, we see that 8,464 of the 10,726 attacks found have descriptions - approximately 79%.

To determine how many totally unique descriptions, there are, we can employ Python's <TT>Counter</TT> function (from the <TT>collections</TT> package).

    attack_counter = Counter(attack_text)
    top_ten_attacks = attack_counter.most_common(10)
    top_ten_list = [txt.strip()+" ("+str(cntr) + ")\n" for txt,cntr in top_ten_attacks]

The resulting rankings:

| --: | :---------------------------------------------------------------------|
| 343 |flip a coin. if heads, the defending pokémon is now paralyzed.
| 174 |the defending pokémon is now asleep.
| 125 |flip a coin. if tails, this attack does nothing.
| 122 |flip a coin. if heads, the defending pokémon is now confused.
| 103 |the defending pokémon is now poisoned.
|  86 |the defending pokémon can't retreat during your opponent's next turn.
|  83 |flip 2 coins. this attack does 20 damage times the number of heads.
|  82 |this pokémon does 10 damage to itself.
|  71 |flip a coin. if heads, the defending pokémon is now poisoned.
|  64 |flip 2 coins. this attack does 10 damage times the number of heads.

So there is a lot of coin-based action in the top ten.  Status infliction (confusion, paralysis, sleep, poison) is also quite common.

Note, though that the 7th and 10th most common descriptions are functionally the same, with only a difference for the actual damage dealt.  Inspection of various other cards shows that there are many instances of cards with functionally identical attacks, but with slight variations in the damage dealt and other details.  So we can replace the amount of damage and coin flips with dummy strings for just such a result.  Regular expression substitution is the method of choice here.

    attack_text_2 = [re.sub("[0-9]{1,2}0 damage|[1-9] damage counter(s)?", "_AMOUNT_ damage", attack) for attack in attack_text]
    attack_text_2 = [re.sub("[0-9]{1,2}0 more damage", "_AMOUNT_ more damage", attack) for attack in attack_text_2]
    attack_text_2 = [re.sub("flip [a1-9] coin(s)?", "flip _N_ coins", attack) for attack in attack_text_2]
    attack_counter_2 = Counter(attack_text_2)
    top_ten_attacks_2 = attack_counter_2.most_common(10)
    top_ten_list_2 = [txt.strip()+" ("+str(cntr) + ")\n" for txt,cntr in top_ten_attacks_2]

The new rankings:

| --: | :-------------------------------------------------------------------------------------|
| 402 | flip _N_ coins. this attack does _AMOUNT_ damage times the number of heads.           |
| 343 | flip _N_ coins. if heads, the defending pokémon is now paralyzed.                     |
| 328 | flip _N_ coins. if heads, this attack does _AMOUNT_ more damage.                      |
| 174 | the defending pokémon is now asleep.                                                  |
| 141 | this pokémon does _AMOUNT_ damage to itself.                                          |
| 125 | flip _N_ coins. if tails, this attack does nothing.                                   |
| 122 | flip _N_ coins. if heads, the defending pokémon is now confused.                      |
| 103 | the defending pokémon is now poisoned.                                                |
|  86 | the defending pokémon can't retreat during your opponent's next turn.                 |
|  71 | flip _N_ coins. if heads, the defending pokémon is now poisoned.                      |

It's a notable rearrangement, but the bulk of the entries here were on the previous top 10.  In fact, the only entry on this list that didn't appear on the previous one in any form is "flip _N_ coins. if heads, this attack does _AMOUNT_ more damage."


## Analysis: Do Attacks With the Same Name Have the Same Effects?
In the video games, with only a handful of exceptions, attacks behave the same irrespective of which species of Pokémon is using it.  The TCG, however, does not need to abide by this restriction.

This difference can be illustrated by checking how many unique attack names there are.  We also employ the regular expressions to 

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

It was discovered that there were 3,713 unique attack names, though only 575 had all of the same descriptions.  The 10 most frequent of these, with descriptions:

| Attack Name | Count | Description |
| ----------- | ----: | ----------- |
| Tackle      |  167  |             |
| Bite        |  107  |             |
| Scratch     |   87  |             |
| Slash       |   73  |             |
| Headbutt    |   69  |             |
| Pound       |   52  |             |
| Peck        |   44  |             |
| Gnaw        |   40  |             |
| Razor Leaf  |   40  |             |
| Flare       |   39  |             |

Perhaps unsurprisingly, the top ten attacks do not have any descriptions whatsoever.  Inspection of the ranked_names object reveals that the highest-ranked attack with an actual description is ranked 43rd overall (Bind: Flip a coin.  If heads, the Defending Pokémon is now paralyzed.) and has only 12 instances.

Additionally, eight of the top 10 above are actual attacks in the games (all except Gnaw and Flare). The top six overall are fairly common attacks that are learned by a wide variety of Pokémon in the games.  Presumably, this accounts for their frequency here.

Frequency on this table doesn't mean that they dominate the card descriptions, though.  Combined, the top ten here account for 718 attacks, about 6.6% of all the cards' attacks.  This sort of mirrors the video games, in that there are a handful of attacks which are learned by significant fractions of available Pokémon naturally.  However, there are also a large number of attacks can be "tutored" to Pokémon, either by items or other characters, and many of these are available for a variety of Pokémon.