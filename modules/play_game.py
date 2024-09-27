"""
Plays a game of Jeopardy.
"""

from thefuzz import fuzz, process
import utils.dbaccess as db
from config import Config
import modules.build_game as build

def play_game(episode_id: int,
              what_round: str,
              current_score: int = 0,
              debug_mode: bool = False) -> int:
    """
    I want to implement caching to make the gameplay less annoying with the
    slow connection speed. Probably the best way to do it is to save the
    CategoriesWithValues object, rather than recreating it every time.

    This function first gets all the categories and only does it once. That's
    fine. The problem is getting the clues. Right now it only gets a clue if 
    the player selects a value, and that's a big performance problem.

    First brainwave is to make a new function that gets all of the clues and
    pairs them to a value. The question is how do I then mark those as completed
    and still include them in the table?
    """

    if debug_mode is True:
        amount = int(input("How much do you want your score to be?"))
        return amount

    player_bank = current_score
    value_set = []
    match what_round:
        case "Regular":
            value_set = Config.VALUE_REGULAR
        case "Double":
            value_set = Config.VALUE_DOUBLE

    categories = db.get_categories(episode_id, what_round)
    lower_case_categories = []
    category_value_dicts = []
    for category in categories:
        # string parsing needs uniform case
        lower_case = category.lower()
        lower_case_categories.append(lower_case)
        # this is necessary because otherwise valueSet is getting modified
        new_value_set = []
        for value in value_set:
            new_value_set.append(value)
        category_and_values = {category: new_value_set}
        category_value_dicts.append(category_and_values)

    clues_on_the_board = True
    while clues_on_the_board:
        category_not_chosen = True
        build.draw_table(category_value_dicts, player_bank)
        while category_not_chosen:
            chosen_category = input("Choose a category: ")
            lowercase_category = chosen_category.lower()
            if lowercase_category not in lower_case_categories:
                print("Invalid category! (Try copy and pasting!)")
            else:
                category_not_chosen = False
        category_id = db.get_category_id(episode_id, lowercase_category)

        value_not_chosen = True
        no_answer = True
        valid_choices = build.get_value_set(category_value_dicts, lowercase_category)
        while value_not_chosen:
            while no_answer:
                try:
                    value = int(input("What value of clue? "))
                    no_answer = False
                except ValueError:
                    print("You must enter a number!")
            if value not in valid_choices:
                print("Valid values are:")
                for valid_value in valid_choices:
                    print(valid_value)
            else:
                value_not_chosen = False
                category_match = process.extractOne(lowercase_category, categories)
                # this SHOULD be the unformatted category as a result
                # and should be able to be used in the unformatted categories
                found_category = category_match[0]
                build.remove_value(category_value_dicts, found_category, value)
                category_should_be_removed = build.should_remove_category(
                    category_value_dicts, found_category)
                if category_should_be_removed:
                    categories.remove(found_category)

        clue = db.get_clue(category_id, value)
        question, correct_answer = clue[0], clue[1].lower() # type: ignore
        print(question)
        player_answer = input("What is... ").lower()
        simple_ratio_comparison = fuzz.ratio(correct_answer, player_answer)
        token_sort_ratio_comparison = fuzz.token_sort_ratio(correct_answer, player_answer)
        if simple_ratio_comparison > 80 or token_sort_ratio_comparison > 80:
            print("Correct!")
            player_bank += value # type: ignore
        else:
            print(f"Incorrect! The answer was {correct_answer}")
            player_bank -= value # type: ignore
        valid_categories_remaining = build.check_for_valid_categories(category_value_dicts)
        if valid_categories_remaining is False:
            clues_on_the_board = False

    return player_bank

def play_final_jeopardy(episode_id: int, player_score: int = 0, debug_mode: bool = False) -> int:
    """Runs a round of Final Jeopardy. The player can bet any amount of their current score, and
    that amount will be added or subtracted depending on if they get it right. The resulting score
    is the final score."""
    if debug_mode is True:
        amount = int(input("How much do you want your score to be?"))
        category = "COLORS THAT END IN URPLE"
        question = "Suck it, Trebek!"
        build.draw_fj(category, question, player_score)
        return amount

    final_score = player_score
    fj_tuple = db.get_final_jeopardy(episode_id)
    category, question, correct_answer = fj_tuple
    print(f"The category is {category}!")
    bidding_not_complete = True
    while bidding_not_complete:
        try:
            bid = int(input("How much would you like to bid? "))
        except ValueError:
            print("You must enter a number!")
        if bid > player_score:
            print("You can only bid up to your current score!")
        elif bid < 0:
            print("You can't bid a negative number!")
        else:
            bidding_not_complete = False

    build.draw_fj(category, question, player_score)
    player_answer = input("What is... ")
    simple_ratio_comparison = fuzz.ratio(correct_answer, player_answer)
    token_sort_ratio_comparison = fuzz.token_sort_ratio(correct_answer, player_answer)
    if simple_ratio_comparison > 80 or token_sort_ratio_comparison > 80:
        print("Correct!")
        final_score += bid
    else:
        print(f"Incorrect! The correct answer was: {correct_answer}")
        final_score -= bid

    return final_score

def game_loop(user_id: int, debug_mode: bool = False) -> None:
    """The entire game loop of a full Jeopardy game. 
    Two rounds of Jeopardy are played, Regular and Double,
    followed by Final Jeopardy. After each round, 
    play_game and play_fj pass the modified score to the
    next round (or the end)."""
    warning = """
    NOTE: If you are asked a question that begins with "null", the answer is the exact text of the question.
This is because the question is missing on j-archive, and the selected value is a placeholder.
"""
    print(warning)
    choice = input("Do you want to start with a specific game? Y/N ")
    if choice == "y":
        date_not_chosen = True
        while date_not_chosen:
            ep_date = input("Please enter episode date (format yyyy-mm-dd): ")
            episode_id = db.get_ep_id_from_date(ep_date)
            if episode_id is None:
                continue
            date_not_chosen = False
    elif choice == "n":
        episode_id = db.get_random_ep()
    else:
        print("Invalid response, getting random game...")
        episode_id = db.get_random_ep()
    ep_title = db.get_ep_title(episode_id)
    print(f"Selected episode {ep_title}!")
    print("Let's begin our first round...")
    score = play_game(episode_id, "Regular", debug_mode=debug_mode)
    print(f"Your score is {score} - it's time for Double Jeopardy!")
    double_score = play_game(episode_id, "Double", score, debug_mode=debug_mode)
    print(f"Great job! Your score after Double Jeopardy is {double_score}")
    print("It's time for Final Jeopardy...")
    final_score = play_final_jeopardy(episode_id, double_score, debug_mode=debug_mode)
    db.write_score(episode_id, user_id, final_score)
    print(f"Your final score is {final_score}!")
    print("Thanks for playing!")
