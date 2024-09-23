import os
import pymysql
import json
import sshtunnel
from typing import TypeAlias
from builder_queries import *
from datetime import datetime
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
    with open(DIRECTORY + json_file, encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

def build_ep_date_from_file(json_file: str) -> datetime:
    """
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
    file_name = os.path.basename(json_file)
    just_name = file_name.strip(".json")
    split_name = just_name.split(" - ")
    episode_title = split_name[0]
    return episode_title

def build_categories(json_round: JRound) -> list[str]:
    categories = list(json_round.keys())
    return categories

def build_clues_and_answers(json_round: JRound, category_name: str) -> dict[str, str]:
    clues_and_answers = dict(json_round[category_name].items())
    return clues_and_answers

def insert_episode(json_file: str) -> None:
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
            cur.execute(SQL_INSERT_EPISODE, (episode_date, episode_title))
            cur.connection.commit()
        except MySQLError as e:
            print(f"Error: {e}")
            clean_episode_ID()
        finally:
            cur.close()
            conn.close()

def insert_categories(json_round: JRound, round_position: int, episodeID: int) -> None:
    if round_position not in VALID_ROUNDS:
        raise ValueError("insertCategories: roundPosition must be one of %r" % VALID_ROUNDS)

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
                cur.execute(SQL_INSERT_CATEGORY, (category, what_round, position, episodeID))
                conn.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def insert_clues_and_answers(json_round: JRound, round_position: int, category_name: str, episodeID: int) -> None:
    if round_position not in VALID_ROUNDS:
        raise ValueError("insertCategories: roundPosition must be one of %r" % VALID_ROUNDS)

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
            
            for i, clue in enumerate(clue_list):
                clue_to_add = clue
                answer_to_add = answers_list[i]
                money_value = money_value_lookup[i]
                cur.execute(SQL_INSERT_CLUE, (categoryID, clue_to_add, answer_to_add, money_value))
                cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def get_episode_ID(episode_title: str) -> int:
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
            cur.execute(SQL_UPDATE_CATEGORY, (category_name, categoryID))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def update_clues_and_answers(question: str, answer: str, clueID: int) -> None:
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
            cur.execute(SQL_UPDATE_CLUES, (question, answer, clueID))
            conn.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def is_ep_in_database(episode_title: str) -> bool:
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

    



