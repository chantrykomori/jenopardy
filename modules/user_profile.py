import utils.dbaccess as db
from prettytable import PrettyTable

def user_profile(userID: int):
    result = db.get_scores(userID)
    username = db.get_username(userID)
    table = PrettyTable()
    table.field_names = ["#", "Score", "Episode Title", "Earned Date"]
    for index, row in enumerate(result):
        score = int(row[0])
        title = str(row[1])
        time = row[2]
        table.add_row([index + 1, score, title, time])
    print(f"{username}'s Top 10 Scores")
    print(table)