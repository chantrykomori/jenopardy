import utils.dbaccess as db
from config import Config
from modules.build_game import draw_table, draw_fj, get_value_set, remove_value, should_remove_category, check_for_valid_categories
from thefuzz import fuzz, process

def play_game(episodeID: int, what_round: str, current_score: int = 0, debug_mode: bool = False) -> int:
    """
    Play a regular round of Jeopardy. In the main loop, this will
    execute twice, followed by play_final_jeopardy.
    
    Parameters
    ----------
    randomEp : int
        EpisodeID field of the episode to use
    whatRound : str
        String representation of the round to use. Takes either "Regular" or "Double".
    currentScore : int
        If there is a previous score, uses it. Otherwise defaults to 0.
    
    Returns
    -------
    playerBank : int
        Player's current score at the end of the round.
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

    categories = db.get_categories(episodeID, what_round)
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
        draw_table(category_value_dicts, player_bank)
        while category_not_chosen:
            chosen_category = input("Choose a category: ")
            formatted_category = chosen_category.lower()
            if formatted_category not in lower_case_categories:
                print("Invalid category! (Try copy and pasting!)")
            else:
                category_not_chosen = False
        categoryID = db.get_category_ID(episodeID, formatted_category)

        value_not_chosen = True
        no_answer = True
        valid_choices = get_value_set(category_value_dicts, formatted_category)
        while value_not_chosen:
            while no_answer:
                try:
                    value = int(input("What value of clue? "))
                    no_answer = False
                except ValueError:
                    print("You must enter a number!")
            if value not in valid_choices:
                print(f"Valid values are:")
                for valid_value in valid_choices:
                    print(valid_value)
            else:
                value_not_chosen = False
                category_match = process.extractOne(formatted_category, categories)
                # this SHOULD be the unformatted category as a result 
                # and should be able to be used in the unformatted categories
                processed_category = category_match[0]
                remove_value(category_value_dicts, processed_category, value)
                category_should_be_removed = should_remove_category(category_value_dicts, processed_category)
                if category_should_be_removed:
                    categories.remove(processed_category)

        # bunch of type ignores here because i already checked if its an int
        # type checking really struggles with multi-type data structures tbh
        clue = db.get_clue(categoryID, value) # type: ignore
        print(clue[0])
        correct_answer = clue[1].lower()
        player_answer = input("What is... ").lower()
        simple_ratio = fuzz.ratio(correct_answer, player_answer)
        token_sort_ratio = fuzz.token_sort_ratio(correct_answer, player_answer)
        if simple_ratio > 80 or token_sort_ratio > 80:
            print("Correct!")
            player_bank += value # type: ignore
        else:
            print(f"Incorrect! The answer was {clue[1]}")
            player_bank -= value # type: ignore
        valid_categories_remaining = check_for_valid_categories(category_value_dicts)
        if valid_categories_remaining == False:
            clues_on_the_board = False

    return player_bank

def play_final_jeopardy(episodeID: int, player_score: int = 0, debug_mode: bool = False):
    """
    Plays a Final Jeopardy round. In the main game loop, this runs
    just once, after play_game runs twice. In a typical gameplay
    scenario, the playerScore variable should always have a value,
    but on the off-chance it doesn't it defaults to 0.

    Parameters
    ----------
    randomEp : int
        EpisodeID field of the episode to use.
    playerScore : int
        The current score. Defaults to 0.
    
    Returns
    ----------
    finalScore : int
        The score at the end of the round.
    """
    if debug_mode is True:
        amount = int(input("How much do you want your score to be?"))
        category = "COLORS THAT END IN URPLE"
        question = "Suck it, Trebek!"
        draw_fj(category, question, player_score)
        return amount
    
    final_score = player_score
    fj_tuple = db.get_final_jeopardy(episodeID)
    category = fj_tuple[0]
    question = fj_tuple[1]
    correct_answer = fj_tuple[2]
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
    
    draw_fj(category, question, player_score)
    player_answer = input("What is... ")
    simple_ratio = fuzz.ratio(correct_answer, player_answer)
    token_sort_ratio = fuzz.token_sort_ratio(correct_answer, player_answer)
    if simple_ratio > 80 or token_sort_ratio > 80:
        print("Correct!")
        final_score += bid
    else:
        print(f"Incorrect! The correct answer was: {correct_answer}")
        final_score -= bid
 
    return final_score

def game_loop(userID: int, debug_mode: bool = False):
    warning = """NOTE: If you are asked a question that begins with "null", the answer is the exact text of the question.
This is because the question is missing on j-archive, and the selected value is a placeholder.
"""
    print(warning)
    choice = input("Do you want to start with a specific game? Y/N ")
    if choice == "y":
        date_not_chosen = True
        while date_not_chosen:
            ep_date = input("Please enter episode date (format yyyy-mm-dd): ")
            episodeID = db.get_epID_from_date(ep_date)
            if episodeID == None:
                continue
            date_not_chosen = False
    elif choice == "n":
        episodeID = db.get_random_ep()
    else:
        print("Invalid response, getting random game...")
        episodeID = db.get_random_ep()
    ep_title = db.get_ep_title(episodeID)
    print(f"Selected episode {ep_title}!")
    print("Let's begin our first round...")
    score = play_game(episodeID, "Regular", debug_mode=debug_mode)
    print(f"Your score is {score} - it's time for Double Jeopardy!")
    doubleScore = play_game(episodeID, "Double", score, debug_mode=debug_mode)
    print(f"Great job! Your score after Double Jeopardy is {doubleScore}")
    print("It's time for Final Jeopardy...")
    finalScore = play_final_jeopardy(episodeID, doubleScore, debug_mode=debug_mode)
    db.write_score(episodeID, userID, finalScore)
    print(f"Your final score is {finalScore}!")
    print("Thanks for playing!")