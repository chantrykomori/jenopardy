"""
Debug functions only accessible to the admin that can modify important aspects of the database.
"""

import utils.dbaccess as db
from modules.play_game import game_loop

def debug_menu(admin_id: int) -> None:
    """Displays the debug menu, which is only viewable as the admin."""
    menu = """
1. View all players
2. View all scores
3. Remove a player
4. Remove a score
5. Play a debug game
6. Return to main menu
"""
    managing = True
    while managing:
        print(menu)
        choice = int(input("What would you like to do? "))
        match choice:
            case 1:
                table = db.generate_player_table()
                print(table)
            case 2:
                table = db.generate_score_table()
                print(table)
            case 3:
                remove_player()
            case 4:
                remove_score()
            case 5:
                game_loop(admin_id, debug_mode=True)
            case 6:
                managing = False

def remove_score() -> None:
    """Removes a score from the scores table."""
    removing_score = True
    while removing_score:
        score_to_remove = int(input("What is the scoreID you want to remove? "))
        check = db.check_score_id_exists(score_to_remove)
        if check is False:
            print(f"No score found with scoreID {score_to_remove}")
            continue_removing = input("Try again? Y/N ")
            if continue_removing == "y":
                continue
            elif continue_removing == "n":
                removing_score = False
        elif check is True:
            confirm = input(f"Are you sure you want to remove scoreID {score_to_remove}? Y/N ")
            if confirm == "y":
                db.delete_score_by_score_id(score_to_remove)
                print("Score removed.")
                removing_score = False
            elif confirm == "n":
                removing_score = False

def remove_player() -> None:
    """Removes a player (and their associated scores) from the database."""
    removing_player = True
    while removing_player:
        player_to_remove = input("What player would you like to remove? ")
        check = db.check_username_exists(player_to_remove)
        if check is False:
            print(f"No player found with username {player_to_remove}")
            continue_removing = input("Try again? Y/N ")
            if continue_removing == "y":
                continue
            elif continue_removing == "n":
                removing_player = False
        elif check is True:
            confirm = input(
                f"Are you sure you want to remove player {player_to_remove} and their scores? Y/N ")
            if confirm == "y":
                user_id = db.get_user_id(player_to_remove)
                db.delete_scores_by_player(user_id)
                db.delete_player(user_id)
                print(f"Player #{user_id} {player_to_remove} removed from database.")
                removing_player = False
            elif confirm == "n":
                removing_player = False
