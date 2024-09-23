from config import Config
from modules.login import log_in
from modules.play_game import game_loop
from modules.leaderboard import view_leaderboard
from modules.user_profile import user_profile
from modules.debug import debug_menu
from modules.credits import view_credits

def intro() -> int:
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
    userID = log_in()
    return userID

def main_menu(userID: int) -> None:
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
            game_loop(userID)
        case 2:
            view_leaderboard()
        case 3:
            user_profile(userID)
        case 4:
            view_credits()
        case 5:
            quit_game()
        case 6:
            if userID == Config.ADMIN_ID:
                debug_menu(userID)
            else:
                print("Incorrect admin account")
        case _:
            print("Please enter a number between 1 and 4!")

def quit_game() -> None:
    quitting = True
    while quitting:
        choice = input("Are you sure you want to quit? Y/N ")
        if choice == "y":
            input("Thanks for playing! Press any button to quit.")
            quit()
        elif choice == "n":
            print("Returning to menu...")
            quitting = False
            return
        else:
            print("Invalid input!")

def main() -> None:
    userID = intro()
    while True:
        main_menu(userID)

if __name__ == "__main__":
    main()