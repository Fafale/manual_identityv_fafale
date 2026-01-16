# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionSet, Visibility
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any

from ..GameInfo import all_survivors_names

####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class DeductionPointPercentage(Range):
    """Percentage of required Deduction Points (mcguffin) from the total available in order to goal."""
    display_name = "Percentage of Deduction Points"
    range_start = 50
    range_end = 100
    default = 90

class FillerItemsPercentage(Range):
    """Excluding progression items, all the exceeding items would become Deduction Points,
    but this option will replace a part of it with (mostly) useful filler instead.
    
    Filler items functionality is explained on the Github page."""
    display_name = "Filler Items Percentage"
    range_start = 0
    range_end = 50
    default = 10

class ShuffledSurvivorList(OptionSet):
    """List of characters that can be shuffled in the multiworld.
    
    (The names here do NOT have special characters, like double quotes)"""
    display_name = "Shuffled Survivor List"
    valid_keys = all_survivors_names
    default = sorted(all_survivors_names)

class ShuffledSurvivorAmount(Range):
    """Amount of characters from the list to shuffle on the multiworld. (Including starting characters)
    
    (If this value is higher than the list length, it'll be reduced to it)"""
    display_name = "Shuffled Survivor Amount"
    range_start = 5
    range_end = len(all_survivors_names)
    default = 20

class StartingSurvivorAmount(Range):
    """Amount of characters to start with unlocked.
    
    (This amount is included on the shuffled_survivor_amount value)"""
    display_name = "Starting Character Amount"
    range_start = 1
    range_end = 5
    default = 3

class StartingPersonaMethod(Choice):
    """Choose HOW Personas for starting characters should be handled.
    The value/percentage is set on the next YAML option.

    Percentage Character - A given % of starting characters will have all their personas unlocked.
    Percentage Total - A given % of all starting characters' personas will be unlocked randomly.

    For example, 25% of 4 starting characters (16 personas total):
    - 1 Character will start with all their personas unlocked.
    - 4 Personas from starting characters will be unlocked randomly."""
    display_name = "Starting Persona Method"
    option_percentage_character = 0
    option_percentage_total = 1
    default = 0

class StartingPersonaPercentage(Range):
    """Choose the percentage value from the option above. (Rounded up)
    
    If set to 0 or 100, the chosen method won't have any differences."""
    display_name = "Starting Persona Percentage"
    range_start = 0
    range_end = 100
    default = 50


class ShuffleBorrowedTime(DefaultOnToggle):
    """Whether Borrowed Time persona will be included on the item pool.
    
    If disabled, locations related to Borrowed Time are removed, and you're allowed to
    use it alongside other personas to complete their "Win using only X persona" locations"""
    display_name = "Shuffle Borrowed Time"

class EnableClassChallenges(Choice):
    """If enabled, each character will have an additional location related to their classification (Decode, Rescue, Assist, Contain)
    
    Disabled - Remove these locations
    Enabled with character - These checks only require the character unlock item
    Enabled with item - These checks require both the character and their "Class Challenge Unlock" item"""
    display_name = "Enable Class Challenges"
    option_disabled = 0
    option_enabled_with_character = 1
    option_enabled_with_item = 2
    default = 2

class EnableUniqueChallenges(Choice):
    """NOT IMPLEMENTED YET, ALWAYS DISABLED
    
    If enabled, each character will have an additional location related to themselves (Similar to Deduction Tasks)
    
    Disabled - Remove these locations
    Enabled with character - These checks only require the character unlock item
    Enabled with item - These checks require both the character and their "Unique Challenge Unlock" item"""
    display_name = "Enable Unique Challenges"
    option_disabled = 0
    #option_enabled_with_character = 1
    #option_enabled_with_item = 2
    default = 0

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["deduction_point_percentage"] = DeductionPointPercentage
    options["filler_item_percentage"] = FillerItemsPercentage

    options["shuffled_survivor_list"] = ShuffledSurvivorList
    options["shuffled_survivor_amount"] = ShuffledSurvivorAmount
    options["starting_survivor_amount"] = StartingSurvivorAmount

    options["starting_persona_method"] = StartingPersonaMethod
    options["starting_persona_percentage"] = StartingPersonaPercentage

    options["shuffle_borrowed_time"] = ShuffleBorrowedTime

    options["enable_class_challenges"] = EnableClassChallenges
    options["enable_unique_challenges"] = EnableUniqueChallenges
    
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options
    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
