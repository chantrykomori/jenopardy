"""
Handles all account creation and logging in, including
password hashing, checking, and ensuring unique identifiers.
"""

from pwinput import pwinput
import utils.dbaccess as db

def log_in() -> int:
    """Allows the user to either create a new player account or log in."""
    not_logged_in = True
    no_choice = True
    prompt = """
What do you want to do?

1. Log in
2. Create account
"""
    while no_choice:
        try:
            choice = int(input(f"{prompt}"))
            no_choice = False
        except ValueError:
            print("You must enter a number!")
    while not_logged_in:
        username = input("Enter your username: ")
        password = pwinput("Enter your password: ")
        match choice:
            case 1:
                user_check = db.check_username_exists(username)
                password_check = db.check_password(username, password)
                if password_check is True and user_check is True:
                    user_id = db.get_user_id(username)
                    print(f"\nLogged in as {username}")
                    not_logged_in = False
                elif password_check is False or user_check is False:
                    if user_check is False:
                        print("Invalid username!")
                    error_found = True
                    while error_found:
                        try:
                            recheck = int(input("Try again (1) or create a new account (2)? "))
                            choice = recheck
                            error_found = False
                        except ValueError:
                            print("You must enter a number!")
                    continue
            case 2:
                user_check = db.check_username_exists(username)
                if user_check is False:
                    db.add_player_to_table(username, password)
                    user_id = db.get_user_id(username)
                    print(f"Created an account for {username}!")
                    not_logged_in = False
                elif user_check is True:
                    print("Username already exists!")
                    error_found = True
                    while error_found:
                        try:
                            recheck = int(input("Log in (1) or try again (2)? "))
                            choice = recheck
                            error_found = False
                        except ValueError:
                            print("You must enter a number!")
            case _:
                print("You must choose either 1 or 2!")
    return user_id
