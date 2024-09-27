"""
Builds the gameboard to display to the player.
"""

from typing import TypeAlias
from prettytable.colortable import ColorTable, Themes

# a value set can either contain one of the money values or the letter "x"
# to indicate that it was already chosen
ValueSet : TypeAlias = list[int | str]
Category : TypeAlias = dict[str, ValueSet]
CategoriesWithValues : TypeAlias = list[Category]

def get_value_set(categories_w_values: CategoriesWithValues, category_name: str) -> ValueSet:
    """Gets the correct set of values to use for the category."""
    category_name = category_name.upper()
    for category_set in categories_w_values:
        if category_name in category_set:
            value_set = category_set[category_name]
    if value_set is not None:
        return value_set
    else:
        raise ValueError("Value set not found")

def remove_value(categories_w_values: CategoriesWithValues, category_name, value) -> None:
    """Removes a value from the category's value set. 
    Used to indicate a question has been answered."""
    for category_set in categories_w_values:
        if category_name in category_set:
            values_left = category_set[category_name]
            index_of_val_to_replace = values_left.index(value)
            values_left.insert(index_of_val_to_replace, "x")
            category_set[category_name].remove(value)

def check_for_valid_categories(categories_w_values: CategoriesWithValues) -> bool:
    """Checks if any categories are valid for the player 
    to choose a question from. A category is valid if there
    is at least one question left in the value set to answer."""
    valid_categories = []
    for category_set in categories_w_values:
        all_value_sets = list(category_set.values())
        for value_set in all_value_sets:
            # convert to a set to flatten all duplicate "x" values into 1
            # if there's more than one in the set then there's still a valid option
            check = len(set(value_set))
            if check > 1:
                valid_categories.append(category_set)
    if len(valid_categories) >= 1:
        return True
    return False

def should_remove_category(cat_and_values: CategoriesWithValues, category_name: str) -> bool | None:
    """Checks if a category has any remaining values left besides 'x'. 
    If not, it should be removed."""
    for category_set in cat_and_values:
        if category_name in category_set:
            values = category_set[category_name]
            check = len(set(values)) # sets flatten identical values into 1 element
            if check == 1:
                return True
            return False

    raise ValueError("The category does not exist in the given set")

def draw_table(categories: CategoriesWithValues, player_score: int = 0) -> None:
    """
    Ok heres the deal:

    The things I want are double border support with colorization, header wrapping,
    and dividers. Dividers are probably the easiest thing to add, by changing to
    adding rows instead of columns. I will need to refactor how I get the data from
    the CategoriesWithValue object. This is also an opportunity to refactor how
    the board is built in play_game, which should not be in that file anyway.

    Double border with colors may be possible with subclassing themes but I have yet
    to get it to work right. I might also have good results with directly creating
    the changes in this function. We'll see.

    Header wrapping is probably not going to happen on my end. It seems like a pretty
    regular request on Github, so let's see if that ever goes anywhere.
    """

    table = ColorTable(theme=Themes.OCEAN)
    # table.bottom_junction_char = "╩"
    # table.bottom_left_junction_char = "╚"
    # table.bottom_right_junction_char = "╝"
    # table.horizontal_char = "═"
    # table.junction_char = "╬"
    # table.left_junction_char = "╠"
    # table.right_junction_char = "╣"
    # table.top_junction_char = "╦"
    # table.top_left_junction_char = "╔"
    # table.top_right_junction_char = "╗"
    # table.vertical_char = "║"

    for category_dict in categories:
        keys = list(category_dict.keys())
        header = keys[0]
        values = []
        for value in category_dict[header]:
            values.append(value)
        table.add_column(header, values)
    print(table)
    print(f"Player score: {player_score}")

def draw_fj(category: str, question: str, player_score: int = 0) -> None:
    """Draws the Final Jeopardy gameboard, which has unique mechanics.
    It only has one category and one table, and no value checking is necessary
    because once the question has been answered, the game is over."""
    table = ColorTable(theme=Themes.OCEAN)
    table.field_names = [category]
    table.add_row([question])
    # table.set_style(DOUBLE_BORDER)
    print(table)
    print(f"Player score: {player_score}")
