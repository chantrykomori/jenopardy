"""
Server-side program that takes the JSON files produced by
jsoncrawler.py, parses them, and inserts their values into the
database. If the data already exists in the database, it
updates the relevant data.

The program starts from the top and works down - episode, 
categories, clues.
"""

import os
import json
from typing import TypeAlias
from datetime import datetime
import pymysql
import sshtunnel
import builder_queries as q
from pymysql import MySQLError
from config import Config

sshtunnel.SSH_TIMEOUT = 300.0
sshtunnel.TUNNEL_TIMEOUT = 300.0

JRound : TypeAlias = dict[str, dict[str, str]]
EpisodeData : TypeAlias = list[JRound]

DIRECTORY = "jsondump/"

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
    """Helper function that opens the JSON cleanly."""
    with open(DIRECTORY + json_file, encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

def build_ep_date_from_file(json_file: str) -> datetime:
    """
    Builds an episode datetime object from the filename.
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
    Builds an episode title string from the filename.
    """
    file_name = os.path.basename(json_file)
    just_name = file_name.strip(".json")
    split_name = just_name.split(" - ")
    episode_title = split_name[0]
    return episode_title

def build_categories(json_round: JRound) -> list[str]:
    """Builds a list of categories from the json round."""
    categories = list(json_round.keys())
    return categories

def build_clues_and_answers(json_round: JRound, category_name: str) -> dict[str, str]:
    """Builds a dict of clues and answers, with the category name as a key."""
    clues_and_answers = dict(json_round[category_name].items())
    return clues_and_answers

def insert_episode(json_file: str) -> None:
    """Inserts the new episode in the JSON file into the database."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        episode_date = build_ep_date_from_file(json_file)
        episode_title = build_ep_title_from_file(json_file)
        try:
            cur.execute(q.SQL_INSERT_EPISODE, (episode_date, episode_title))
            cur.connection.commit()
        except MySQLError as e:
            print(f"Error: {e}")
            clean_episode_id()
        finally:
            cur.close()
            conn.close()

def insert_categories(json_round: JRound, round_position: int, episode_id: int) -> None:
    """Inserts categories in a JSON round into the episode."""
    if round_position not in VALID_ROUNDS:
        raise ValueError(f"insertCategories: roundPosition must be one of {VALID_ROUNDS}")

    categories = build_categories(json_round)
    if round_position == 0:
        what_round = "Regular"
    elif round_position == 1:
        what_round = "Double"
    elif round_position == 2:
        what_round = "Final"

    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            for index, category in enumerate(categories):
                position = index + 1
                cur.execute(q.SQL_INSERT_CATEGORY, (category, what_round, position, episode_id))
                conn.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def insert_clues_and_answers(
    json_round: JRound,
    round_position: int,
    category_name: str,
    episode_id: int) -> None:
    """Inserts all clues and answers in a category into the database."""
    if round_position not in VALID_ROUNDS:
        raise ValueError(f"insertCategories: roundPosition must be one of {VALID_ROUNDS}")

    clues_and_answers = build_clues_and_answers(json_round, category_name)
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            category_id = get_category_id(category_name, episode_id)
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
            for i, clue in enumerate(clue_list):
                clue_to_add = clue
                answer_to_add = answers_list[i]
                money_value = money_value_lookup[i]
                cur.execute(q.SQL_INSERT_CLUE, (
                    category_id,
                    clue_to_add,
                    answer_to_add,
                    money_value))
                cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def get_episode_id(episode_title: str) -> int:
    """Retrieves the episode ID based on the episode title string.
    The episode title should always be unique."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_GET_EPISODEID_BY_EPTITLE, (episode_title))
            result = cur.fetchone()
            if result is not None:
                episode_id = int(result[0])
        except MySQLError as e:
            print(e)
            result = None
        finally:
            cur.close()
            conn.close()

    if episode_id is None:
        raise ValueError("No episode ID found")
    return episode_id

def get_category_id(category_name: str, episode_id: int) -> int:
    """Retrieves the category ID from the database based on the category name.
    NOTE: Category names are not unique, but episode IDs are."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_GET_CATEGORYID_BY_NAME_AND_EPID, (category_name, episode_id))
            result = cur.fetchone()
            if result is not None:
                category_id = int(result[0])
        except MySQLError as e:
            print(e)
            result = None
        finally:
            cur.close()
            conn.close()

    if category_id is None:
        raise ValueError("CategoryID not found")
    return category_id

def get_category_ids_by_round(episode_id: int, what_round: str) -> list[int]:
    """Retrieves all category IDs in an episode's round."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_GET_CATEGORYIDS_BY_ROUND, (what_round, episode_id))
            result = cur.fetchall()
            if result is not None:
                category_ids = []
                for row in result:
                    id_to_add = row[0]
                    category_ids.append(id_to_add)
        except MySQLError as e:
            print(e)
            category_ids = None
        finally:
            cur.close()
            conn.close()

    if category_ids is None:
        raise ValueError("No categoryIDs found")
    return category_ids

def get_clue_ids_by_category_id(category_id: int) -> list[int]:
    """Retrieves all clue IDs that are associated with a category ID."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_GET_CLUES_BY_CATEGORYID, (category_id))
            result = cur.fetchall()
            if result is not None:
                clue_ids = []
                for row in result:
                    id_to_add = row[0]
                    clue_ids.append(int(id_to_add))
        except MySQLError as e:
            print(e)
            clue_ids = None
        finally:
            cur.close()
            conn.close()

    if clue_ids is None:
        raise ValueError("No clueIDs found")
    return clue_ids

def clean_episode_id() -> None:
    """If the db builder is interrupted, this function can reset the
    auto-increment property of the episodeID field in the episodes
    table. Not at all necessary, but aesthetically pleasing."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_GET_MAX_EPISODEID)
            max_result = cur.fetchone()
            if max_result is not None:
                max_id = int(max_result[0]) + 1
                cur.execute(q.SQL_ALTER_AUTOINCREMENT, (max_id))
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def update_category(category_name: str, category_id: int) -> None:
    """Updates a category that already exists in the database."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_UPDATE_CATEGORY, (category_name, category_id))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def update_clues_and_answers(question: str, answer: str, clue_id: int) -> None:
    """Updates the clues and answers that already exist in the database.
    NOTE: A better way to run this would be to check for the x value."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_UPDATE_CLUES, (question, answer, clue_id))
            conn.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def is_ep_in_database(episode_title: str) -> bool:
    """Checks if the episode title already exists in the database.
    If it does, that indicates that the episode should be updated,
    rather than added."""
    with sshtunnel.SSHTunnelForwarder(
        (Config.SSH_HOST),
        ssh_username=Config.SSH_USERNAME,
        ssh_password=Config.SSH_PASSWORD,
        remote_bind_address=(Config.SSH_REMOTE_BIND_ADDRESS, 3306)) as tunnel:
        conn = pymysql.connect(
            host=Config.LOCALHOST,
            user=Config.LOCALUSER,
            passwd=Config.LOCALPASSWORD,
            db=Config.DATABASE,
            port=tunnel.local_bind_port)
        cur = conn.cursor()
        try:
            cur.execute(q.SQL_GET_EPTITLE_EXISTENCE, (episode_title))
            result = cur.fetchone()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

    if result is None:
        return False
    return True

def update_database() -> None:
    """Updates the database, file by file, beginning at the episode level
    and working down to categories, then clues. If the episode doesn't
    already exist in the database, it is added. Otherwise, it will
    update."""
    for file in os.listdir(DIRECTORY):
        episode_title = build_ep_title_from_file(file)
        json_data = open_json(file)
        check = is_ep_in_database(episode_title)
        if check is False:
            print(f"Attempting to add {episode_title}...")
            insert_episode(file)
            for round_position, jround in enumerate(json_data):
                categories = build_categories(jround)
                episode_id = get_episode_id(episode_title)
                insert_categories(jround, round_position, episode_id)
                for category in categories:
                    insert_clues_and_answers(jround, round_position, category, episode_id)
            print("Episode added to database!")
        else:
            episode_id = get_episode_id(episode_title)
            print(f"Updating {episode_title}...")
            for round_position, jround in enumerate(json_data):
                what_round = ""
                match round_position:
                    case 0:
                        what_round = "Regular"
                    case 1:
                        what_round = "Double"
                    case 2:
                        what_round = "Final"
                category_ids = get_category_ids_by_round(episode_id, what_round)
                new_category_names = build_categories(jround)
                for i, cat_id in enumerate(category_ids):
                    update_category(new_category_names[i], cat_id)
                    clue_ids = get_clue_ids_by_category_id(cat_id)
                    new_clues = list(build_clues_and_answers(jround, new_category_names[i]).keys())
                    new_answers = list(build_clues_and_answers(
                        jround,
                        new_category_names[i]).values())
                    for c, clue_id in enumerate(clue_ids):
                        update_clues_and_answers(new_clues[c], new_answers[c], clue_id)
            print("Episode updated!")
