"""
The main module of Jenopardy that must be run in order to play the game.
This does not include any of the web scraping/db insertion logic, aside
from score and user management.
"""

import sys
from altconfig import Config
from modules.login import log_in
from modules.play_game import game_loop
from modules.leaderboard import view_leaderboard
from modules.user_profile import user_profile
from modules.debug import debug_menu
from modules.credits import view_credits

def intro() -> int:
    """Entry point to the game. Logs the player in and returns the relevant user ID."""
    input("Press ENTER to begin")
    splash = """

     ___  _______  __    _  _______  _______  _______  ______    ______   __   __  __  
    |   ||       ||  |  | ||       ||       ||   _   ||    _ |  |      | |  | |  ||  | 
    |   ||    ___||   |_| ||   _   ||    _  ||  |_|  ||   | ||  |  _    ||  |_|  ||  | 
    |   ||   |___ |       ||  | |  ||   |_| ||       ||   |_||_ | | |   ||       ||  | 
 ___|   ||    ___||  _    ||  |_|  ||    ___||       ||    __  || |_|   ||_     _||__| 
|       ||   |___ | | |   ||       ||   |    |   _   ||   |  | ||       |  |   |   __  
|_______||_______||_|  |__||_______||___|    |__| |__||___|  |_||______|   |___|  |__| 

"""
    welcome = """
Welcome to Jenopardy, a single-player Jeopardy experience. Play by selecting a category, then a value.
At the end, see how you stack up to others who have played on the leaderboard!

(Press ENTER to continue)\n"""
    input(splash + welcome)
    user_id = log_in()
    return user_id

def main_menu(user_id: int) -> None:
    """Allows the user to choose whether to play a new game, check scores, 
    view credits, or quit.
    There is also a secret debug option for the admin that is not listed."""
    menu = """
What would you like to do?

1. Play a game
2. Check leaderboard
3. View user stats
4. Credits
5. Quit
"""
    choice_not_made = True
    while choice_not_made:
        try:
            choice = int(input(menu))
            choice_not_made = False
        except ValueError:
            print("You must enter a number!")
    match choice:
        case 1:
            game_loop(user_id)
        case 2:
            view_leaderboard()
        case 3:
            user_profile(user_id)
        case 4:
            view_credits()
        case 5:
            quit_game()
        case 6:
            if user_id == Config.ADMIN_ID:
                debug_menu(user_id)
            else:
                print("Incorrect admin account")
        case _:
            print("Please enter a number between 1 and 4!")

def quit_game() -> None:
    """Quits the program."""
    quitting = True
    while quitting:
        choice = input("Are you sure you want to quit? Y/N ")
        if choice == "y":
            input("Thanks for playing! Press any button to quit.")
            sys.exit()
        elif choice == "n":
            print("Returning to menu...")
            quitting = False
            return
        else:
            print("Invalid input!")

def main() -> None:
    """Outside of the game proper, this is the main loop of the program."""
    user_id = intro()
    while True:
        main_menu(user_id)

if __name__ == "__main__":
    main()
