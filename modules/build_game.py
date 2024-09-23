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
    for category_set in categories_w_values:
        if category_name in category_set:
            values = category_set[category_name]
            check = len(set(values)) # sets flatten identical values into 1 element
            if check == 1:
                return True
            else:
                return False
    
    raise ValueError("The category does not exist in the given set")

def draw_table(categories: CategoriesWithValues, player_score: int = 0) -> None:
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
    table = PrettyTable()
    table.field_names = [category]
    table.add_row([question])
    print(table)
    print(f"Player score: {player_score}")