# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

from ..GameInfo import all_survivors_names

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

# Import random lib to shuffle lists and select included characters randomly
import random

import math

IDV_gen_data = {}

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################


def IDV_define_max_mcguffins(multiworld: MultiWorld, player: int,
                             shuffledSurvivorAmount: int, startingSurvivorAmount: int, personaAmount: int):
    
    checks_per_surv = 15
    # 2 char unlock + 4 personas + 2 challenges
    items_per_surv = 8

    option_shuffleBT = get_option_value(multiworld, player, "shuffle_borrowed_time")
    option_classChallenges = get_option_value(multiworld, player, "enable_class_challenges")
    option_uniqueChallenges = get_option_value(multiworld, player, "enable_unique_challenges")

    if option_shuffleBT == 0:
        checks_per_surv -= 4
        items_per_surv -= 1
    
    if option_classChallenges == 0:
        checks_per_surv -= 1
    if option_classChallenges <= 1:
        items_per_surv -= 1

    if option_uniqueChallenges == 0:
        checks_per_surv -= 1
    if option_uniqueChallenges <= 1:
        items_per_surv -= 1
    
    total_checks = checks_per_surv * shuffledSurvivorAmount
    total_items = items_per_surv * shuffledSurvivorAmount

    total_items -= startingSurvivorAmount
    total_items -= personaAmount
    
    print(f"[{player}]\tchecks per surv: {checks_per_surv}, items per surv: {items_per_surv}")
    print(f"[{player}]\tsurvs: {shuffledSurvivorAmount}, starting: {startingSurvivorAmount}, persona: {personaAmount}")
    print(f"[{player}]\ttotal checks: {total_checks}, total items: {total_items}")

    max_mcguffins = max(min(total_checks - total_items, 500), 1)
    return max_mcguffins

    

# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """

    IDV_gen_data[player] = {}

    shuffledSurvivorList = list(get_option_value(multiworld, player, "shuffled_survivor_list"))
    shuffledSurvivorListLength = len(shuffledSurvivorList)
    shuffledSurvivorAmount = get_option_value(multiworld, player, "shuffled_survivor_amount")
    startingSurvivorAmount = get_option_value(multiworld, player, "starting_survivor_amount")

    if (shuffledSurvivorListLength == 0):
        shuffledSurvivorList = list(all_survivors_names.copy())
        shuffledSurvivorListLength = len(all_survivors_names)
    elif (shuffledSurvivorAmount > shuffledSurvivorListLength):
        shuffledSurvivorAmount = shuffledSurvivorListLength
    
    if (startingSurvivorAmount > shuffledSurvivorAmount):
        startingSurvivorAmount = shuffledSurvivorAmount
    

    world.disabled_challenge_items: set[str] = set()
    if get_option_value(multiworld, player, "enable_class_challenges") != 2: world.disabled_challenge_items.add("class")
    if get_option_value(multiworld, player, "enable_unique_challenges") != 2: world.disabled_challenge_items.add("unique")

    # Set a random seed for the lib
    random.seed()
    
    includedSurvivors = []
    IDV_gen_data[player]["startingSurvivors"] = []
    
    world.disabled_survivors: set[str] = set()

    IDV_gen_data[player]["survivors"] = {}

    random.shuffle(shuffledSurvivorList)
    for i in range(shuffledSurvivorAmount):
        surv_name = shuffledSurvivorList[i]

        includedSurvivors.append(surv_name)
        if (i < startingSurvivorAmount):
            IDV_gen_data[player]["startingSurvivors"].append(surv_name)

        IDV_gen_data[player]["survivors"][surv_name] = True
    
    IDV_gen_data[player]["includedSurvivors"] = includedSurvivors

    for surv_name in all_survivors_names:
        if not surv_name in includedSurvivors:
            world.disabled_survivors.add(f"{surv_name} Locations")
            world.disabled_survivors.add(f"{surv_name} Items")
    


    startingPersonaMethod = get_option_value(multiworld, player, "starting_persona_method")
    startingPersonaPercentage = get_option_value(multiworld, player, "starting_persona_percentage")

    startingPersonaList = []

    available_personas = ["Flywheel Effect", "Tide Turner", "Knee Jerk Reflex"]
    if is_option_enabled(multiworld, player, "shuffle_borrowed_time"): available_personas.append("Borrowed Time")

    personas_qty = len(available_personas)

    IDV_gen_data[player]["startingPersonas"] = []

    persona_amount = startingSurvivorAmount
    if (startingPersonaMethod == 1): persona_amount *= personas_qty

    persona_amount = math.ceil(persona_amount * startingPersonaPercentage/100)

    if (startingPersonaMethod == 0): # Percentage of characters
        for i in range(persona_amount):
            surv_name = IDV_gen_data[player]["startingSurvivors"][i]
            for persona_name in available_personas:
                IDV_gen_data[player]["startingPersonas"].append(f"{surv_name} - {persona_name} Persona Unlock")

    elif (startingPersonaMethod == 1): # Percentage of total personas
        possible_personas = []
        
        for i in range(startingSurvivorAmount):
            surv_name = IDV_gen_data[player]["startingSurvivors"][i]
            for persona_name in available_personas:
                possible_personas.append(f"{surv_name} - {persona_name} Persona Unlock")
        
        random.shuffle(possible_personas)

        for i in range(persona_amount):
            IDV_gen_data[player]["startingPersonas"].append(possible_personas[i])
    
    persona_item_count = persona_amount
    if startingPersonaMethod == 0: persona_item_count = persona_amount * personas_qty

    max_mcguffins = IDV_define_max_mcguffins(multiworld, player, shuffledSurvivorAmount, startingSurvivorAmount, persona_item_count)
    fillerItemPercentage = get_option_value(multiworld, player, "filler_item_percentage")

    available_mcguffins = math.ceil(max_mcguffins * (100 - fillerItemPercentage)/100)
    multiplier = get_option_value(multiworld, player, "deduction_point_percentage")
    mcguffins = round(available_mcguffins * multiplier / 100)

    print(f"[{player}]\tmax mcguffin: {max_mcguffins}, filler pctg: {fillerItemPercentage}, available mcguffins: {available_mcguffins}, goal: {mcguffins}")

    IDV_gen_data[player]["availableMcguffins"] = available_mcguffins

    if mcguffins == 0:
        mcguffins = 1
    if mcguffins == 1:
        goal_index = world.victory_names.index(f"Gather 1 Deduction Point")
    else:
        goal_index = world.victory_names.index(f"Gather {mcguffins} Deduction Points")

    # Set goal location
    world.options.goal.value = goal_index




# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    for surv_name in IDV_gen_data[player]["startingSurvivors"]:
        item = next(i for i in item_pool if i.name == f"{surv_name} - Character Unlock")
        item_pool.remove(item)
        multiworld.push_precollected(item)
    
    for persona_item in IDV_gen_data[player]["startingPersonas"]:
        item = next(i for i in item_pool if i.name == persona_item)
        item_pool.remove(item)
        multiworld.push_precollected(item)

    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    badMcguffins = 500 - IDV_gen_data[player]["availableMcguffins"]
    for _ in range(badMcguffins):
        itemNamesToRemove.append("Deduction Point")
    

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        remove_specific_item(item_pool, item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
