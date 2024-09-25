import utils.dbaccess as db
from prettytable import PrettyTable, DOUBLE_BORDER

def view_leaderboard() -> None:
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