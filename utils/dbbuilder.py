import os
import pymysql
import json
from typing import TypeAlias
from builder_queries import *
from datetime import datetime
from pymysql import MySQLError
from dotenv import load_dotenv

load_dotenv()

JRound : TypeAlias = dict[str, dict[str, str]]
EpisodeData : TypeAlias = list[JRound]

DIRECTORY = "jsondump/"
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

MONEYVALUES_SINGLE = {
    0:200,
    1:400,
    2:600,
    3:800,
    4:1000
}

MONEYVALUES_DOUBLE = {
    0:400,
    1:800,
    2:1200,
    3:1600,
    4:2000    
}

MONEYVALUES_FINAL = {
    0:4000    
}

VALID_ROUNDS = {0, 1, 2}

def open_json(json_file: str) -> EpisodeData:
    """
    Basic helper function to open up a JSON file in the project directory. Expects a filename, not a URL!
    """
    with open(DIRECTORY + json_file, encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

def build_ep_date_from_file(json_file: str) -> datetime:
    """
    Parses an episode's filename string into a datetime object that represents the episode's original airdate. 
    
    Expects a string formatted: {game number/tournament info} - {weekday}, {month} {dd}, {yyyy}
    """
    file_name = os.path.basename(json_file)
    just_name = file_name.strip(".json")
    split_name = just_name.split(" - ")
    broken_date_list = split_name[1].split(", ")
    broken_day = broken_date_list[1].split(" ")
    if len(broken_day[1]) < 2:
        formatted_day = f"0{broken_day[1]}"
    else:
        formatted_day = broken_day[1]
    date_string = f"{broken_day[0]} {formatted_day}, {broken_date_list[2]}"
    episode_date = datetime.strptime(date_string, '%B %d, %Y')
    return episode_date

def build_ep_title_from_file(json_file: str) -> str:
    """
    Gets the title of an episode from the filename.
    """
    file_name = os.path.basename(json_file)
    just_name = file_name.strip(".json")
    split_name = just_name.split(" - ")
    episode_title = split_name[0]
    return episode_title

def build_categories(json_round: JRound) -> list[str]:
    """
    Gets the categories for a round of Jeopardy as a list. Expects a dict that has keys for categories and clue/answer dicts for values.
    """
    categories = list(json_round.keys())
    return categories

def build_clues_and_answers(json_round: JRound, category_name: str) -> dict[str, str]:
    """
    Gets the clues and answers from a round of Jeopardy. Returns all of the cluegroups in one category.
    """
    clues_and_answers = dict(json_round[category_name].items())
    return clues_and_answers

def insert_episode(json_file: str) -> None:
    """
    Inserts an episode into the database based on a JSON file. Must be called before trying to insert categories or clues.
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    episode_date = build_ep_date_from_file(json_file)
    episode_title = build_ep_title_from_file(json_file)
    try:
        cur.execute(SQL_INSERT_EPISODE, (episode_date, episode_title))
        cur.connection.commit()
    except MySQLError as e:
        print(f"Error: {e}")
        clean_episode_ID()
    finally:
        cur.close()
        conn.close()

def insert_categories(json_round: JRound, round_position: int, episodeID: int) -> None:
    """
    Inserts the categories of an episode into the database, based on a round of Jeopardy. Must be called after inserting episodes, but before inserting clues.

    Parameters
    -----------
    jsonDataRound : dict
        A round of Jeopardy. A JSON file, when read, produces a list of three rounds.\n
    roundPosition : int
        The position in the round. 1 = Regular 2 = Double 3 = Final\n
    episodeID : int
        The episodeID field in the database the categories are associated with.
    """
    if round_position not in VALID_ROUNDS:
        raise ValueError("insertCategories: roundPosition must be one of %r" % VALID_ROUNDS)

    categories = build_categories(json_round)
    
    if round_position == 0:
        what_round = "Regular"
    elif round_position == 1:
        what_round = "Double"
    elif round_position == 2:
        what_round = "Final"

    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()

    try:
        for index, category in enumerate(categories):
            position = index + 1
            cur.execute(SQL_INSERT_CATEGORY, (category, what_round, position, episodeID))
            conn.commit()
    except MySQLError as e:
        print(e)
    finally:
        cur.close()
        conn.close()

def insert_clues_and_answers(json_round: JRound, round_position: int, category_name: str, episodeID: int) -> None:
    """
    Inserts the clues and answers of an episode into the database, based on a round of Jeopardy. Must be called after episodes, then categories, in that order.

    Parameters
    -----------
    jsonDataRound : dict
        A round of Jeopardy. A JSON file, when read, produces a list of two rounds.\n
    roundPosition : int
        The position in the round. 1 = Regular 2 = Double 3 = Final\n
    categoryName : str
        The name of the category the clues belong to.
    """
    if round_position not in VALID_ROUNDS:
        raise ValueError("insertCategories: roundPosition must be one of %r" % VALID_ROUNDS)

    clues_and_answers = build_clues_and_answers(json_round, category_name)
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()

    categoryID = get_category_ID(category_name, episodeID)
    if round_position == 0:
        money_value_lookup = MONEYVALUES_SINGLE
    elif round_position == 1:
        money_value_lookup = MONEYVALUES_DOUBLE
    else:
        money_value_lookup = MONEYVALUES_FINAL
    
    clues = clues_and_answers.keys()
    answers = clues_and_answers.values()
    clue_list = list(clues)
    answers_list = list(answers)

    try:
        for i, clue in enumerate(clue_list):
            clue_to_add = clue
            answer_to_add = answers_list[i]
            money_value = money_value_lookup[i]
            cur.execute(SQL_INSERT_CLUE, (categoryID, clue_to_add, answer_to_add, money_value))
            conn.commit()
    except MySQLError as e:
        print(e)
    finally:
        cur.close()
        conn.close()

def get_episode_ID(episode_title: str) -> int:
    """
    Retrieves the episode ID from the database, based on the episode's title. Returns None if none exists.
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_GET_EPISODEID_BY_EPTITLE, (episode_title))
        result = cur.fetchone()
        if result is not None:
            episodeID = int(result[0])
    except MySQLError as e:
        print(e)
        result = None
    finally:
        cur.close()
        conn.close()

    if episodeID is None:
        raise ValueError("No episode ID found")
    else:
        return episodeID

def get_category_ID(category_name: str, episodeID: int) -> int:
    """
    Retrieves the category ID from the database based on the category name and episode ID.
    
    Parameters
    -----------
    categoryName : str
        The name of the category to get
    episodeID : int
        The episodeID in the database containing the category
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_GET_CATEGORYID_BY_NAME_AND_EPID, (category_name, episodeID))
        result = cur.fetchone()
        if result is not None:
            categoryID = int(result[0])
    except MySQLError as e:
        print(e)
        result = None
    finally:
        cur.close()
        conn.close()
    
    if categoryID is None:
        raise ValueError("CategoryID not found")
    else:
        return categoryID

def get_category_IDs_by_round(episodeID: int, what_round: str) -> list[int]:
    """
    Gets a list of category IDs of every category in the round.

    Parameters
    -----------
    episodeID : int
        The episodeID from the database of the relevant episode
    whatRound : str
        The string that corresponds to the round to retrieve. Acceptable values are "Regular", "Double", or "Final".
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_GET_CATEGORYIDS_BY_ROUND, (what_round, episodeID))
        result = cur.fetchall()
        if result is not None:
            categoryIDs = []
            for row in result:
                id_to_add = row[0]
                categoryIDs.append(id_to_add)
    except MySQLError as e:
        print(e)
        categoryIDs = None
    finally:
        cur.close()
        conn.close()
    
    if categoryIDs is None:
        raise ValueError("No categoryIDs found")
    else:
        return categoryIDs

def get_clue_IDs_by_category_ID(categoryID: int) -> list[int]:
    """
    Gets the clue IDs for every clue in a category (represented by category ID).
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_GET_CLUES_BY_CATEGORYID, (categoryID))
        result = cur.fetchall()
        if result is not None:
            clueIDs = []
            for row in result:
                id_to_add = row[0]
                clueIDs.append(int(id_to_add))
    except MySQLError as e:
        print(e)
        clueIDs = None
    finally:
        cur.close()
        conn.close()

    if clueIDs is None:
        raise ValueError("No clueIDs found")
    else:
        return clueIDs

def clean_episode_ID() -> None:
    """
    Resets the auto-incrementing ID column of the episodes table so that there aren't huge gaps between DB execution pauses.
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_GET_MAX_EPISODEID)
        max_result = cur.fetchone()
        if max_result is not None:
            maxID = int(max_result[0]) + 1
            cur.execute(SQL_ALTER_AUTOINCREMENT, (maxID))
    except MySQLError as e:
        print(e)
    finally:
        cur.close()
        conn.close()

def update_category(category_name: str, categoryID: int) -> None:
    """
    Updates a previously existing category's name, based on the category ID given.

    Parameters
    -----------
    categoryName : str
        The new category name
    categoryID : int
        The categoryID of the category to be changed
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_UPDATE_CATEGORY, (category_name, categoryID))
        conn.commit()
    except MySQLError as e:
        print(e)
    finally:
        cur.close()
        conn.close()

def update_clues_and_answers(question: str, answer: str, clueID: int) -> None:
    """
    Updates a previously existing clue's question and answer, based on the clue ID given.

    Parameters
    -----------
    question : str
        The new question text to update the clue with
    answer : str
        The new answer text to update the clue with
    clueID : int
        The clueID corresponding to the clue that should be updated
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_UPDATE_CLUES, (question, answer, clueID))
        conn.commit()
    except MySQLError as e:
        print(e)
    finally:
        cur.close()
        conn.close()

def is_ep_in_database(episode_title: str) -> bool:
    """
    Checks if an episode title exists in the database already. If the result is None, returns False.
    """
    conn = pymysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)
    cur = conn.cursor()
    try:
        cur.execute(SQL_GET_EPTITLE_EXISTENCE, (episode_title))
        result = cur.fetchone()
    except MySQLError as e:
        print(e)
    finally:
        cur.close()
        conn.close()

    if result == None:
        return False
    else:
        return True

def update_database() -> None:
    for file in os.listdir(DIRECTORY):
        episode_title = build_ep_title_from_file(file)
        json_data = open_json(file)
        check = is_ep_in_database(episode_title)
        if check == False:
            print(f"Attempting to add {episode_title}...")
            insert_episode(file)
            for round_position, jRound in enumerate(json_data):
                categories = build_categories(jRound)
                episodeID = get_episode_ID(episode_title)
                insert_categories(jRound, round_position, episodeID)
                for category in categories:
                    insert_clues_and_answers(jRound, round_position, category, episodeID)
            print(f"Episode added to database!")
        else:
            episodeID = get_episode_ID(episode_title)
            print(f"Updating {episode_title}...")
            for round_position, jRound in enumerate(json_data):
                what_round = ""
                match round_position:
                    case 0:
                        what_round = "Regular"
                    case 1:
                        what_round = "Double"
                    case 2:
                        what_round = "Final"
                categoryIDs = get_category_IDs_by_round(episodeID, what_round)
                new_category_names = build_categories(jRound)
                for i, catID in enumerate(categoryIDs):
                    update_category(new_category_names[i], catID)
                    clueIDs = get_clue_IDs_by_category_ID(catID)
                    new_clues = list(build_clues_and_answers(jRound, new_category_names[i]).keys())
                    new_answers = list(build_clues_and_answers(jRound, new_category_names[i]).values())
                    for c, clueID in enumerate(clueIDs):
                        update_clues_and_answers(new_clues[c], new_answers[c], clueID)
            print(f"Episode updated!")
                
# if __name__ == "__main__":
#     main()

    



