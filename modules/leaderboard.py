"""
Creates a leaderboard table of the top ten highest scores in the database,
as well as who earned the score, when, and what episode they played.
"""

from prettytable import PrettyTable, DOUBLE_BORDER
import utils.dbaccess as db

def view_leaderboard() -> None:
    """Creates a leaderboard PrettyTable to display the top ten scores."""
    result = db.get_leaderboard()
    table = PrettyTable()
    table.field_names = ["#", "Player", "Score", "Episode Title", "Earned Date"]
    for index, row in enumerate(result):
        username = str(row[0])
        score = int(row[1])
        title = str(row[2])
        time = row[3]
        table.add_row([index, username, score, title, time])
    table.set_style(DOUBLE_BORDER)
    print("\nTop 10 Global Scores")
    print(table)
