from typing import TypeAlias
from prettytable import PrettyTable

# a value set can either contain one of the money values or the letter "x"
# to indicate that it was already chosen
ValueSet : TypeAlias = list[int | str]
Category : TypeAlias = dict[str, ValueSet]
CategoriesWithValues : TypeAlias = list[Category]

def get_value_set(categories_w_values: CategoriesWithValues, category_name: str) -> ValueSet:
    category_name = category_name.upper()
    for category_set in categories_w_values:
        if category_name in category_set:
            value_set = category_set[category_name]
    if value_set is not None:
        return value_set
    else:
        raise ValueError("Value set not found")
        
def remove_value(categories_w_values: CategoriesWithValues, category_name, value) -> None:
    for category_set in categories_w_values:
        if category_name in category_set:
            values_left = category_set[category_name]
            index_of_val_to_replace = values_left.index(value)
            values_left.insert(index_of_val_to_replace, "x")
            category_set[category_name].remove(value)

def check_for_valid_categories(categories_w_values: CategoriesWithValues) -> bool:
    """
    Determines if there are any remaining valid temporary
    categories to choose from, and returns False if not.

    Parameters
    ----------
    listOfDicts : CategoriesWithValues
        A data structure representing all six categories, along with
        their associated values. Equivalent to list[dict[str, list[int]]].
    """
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
    else:
        return False

def should_remove_category(categories_w_values: CategoriesWithValues, category_name: str) -> bool | None:
    """
    Determines if a temporary category and its associated values should
    be removed from the board because it's been depleted. If it should
    be removed, returns True.

    Parameters
    ----------
    listOfDicts : CategoriesWithValues
        A data structure representing all six categories, along with
        their associated values. Equivalent to list[dict[str, list[str]]].
    category : str
        The category to search for in the listOfDicts.
    """
    for category_set in categories_w_values:
        if category_name in category_set:
            values = category_set[category_name]
            check = len(set(values))
            if check == 1:
                return True
            else:
                return False
    
    raise ValueError("The category does not exist in the given set")

def draw_table(categories: CategoriesWithValues, player_score: int = 0) -> None:
    """
    Draws the current game board to the console. Runs in the main loop
    every time the player answers a question. Prints both the board 
    and the current score.

    Parameters
    ----------
    categories : CategoriesWithValues
        text
    playerScore : int
        text
    """
    table = PrettyTable()
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
    """
    Draws the Final Jeopardy game board to the console. Runs in the
    main loop after two rounds of play_game have elapsed.

    Parameters
    ----------
    category : str
        The category the FJ belongs to.
    question : str
        The clue to display.
    playerScore : int
        The current score.
    """
    table = PrettyTable()
    table.field_names = [category]
    table.add_row([question])
    print(table)
    print(f"Player score: {player_score}")