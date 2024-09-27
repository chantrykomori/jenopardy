"""
Displays the user's profile information, which is currently
just a list of all of their scores.
"""

from prettytable import PrettyTable, DOUBLE_BORDER
import utils.dbaccess as db

def user_profile(user_id: int):
    """Displays the user profile."""
    result = db.get_scores(user_id)
    username = db.get_username(user_id)
    table = PrettyTable()
    table.field_names = ["#", "Score", "Episode Title", "Earned Date"]
    for index, row in enumerate(result):
        score = int(row[0])
        title = str(row[1])
        time = row[2]
        table.add_row([index + 1, score, title, time])
    table.set_style(DOUBLE_BORDER)
    print(f"{username}'s Top 10 Scores")
    print(table)
