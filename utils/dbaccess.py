"""
Functions that allow user-side access to the database.
"""

import pymysql
import sshtunnel
from pymysql import MySQLError
from werkzeug.security import generate_password_hash, check_password_hash
from prettytable import from_db_cursor, PrettyTable
from altconfig import Config
import utils.access_queries as q

sshtunnel.SSH_TIMEOUT = 300.0
sshtunnel.TUNNEL_TIMEOUT = 300.0

def add_player_to_table(username: str, password: str) -> None:
    """Adds a new player account to the users table."""
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
        hashed = generate_password_hash(password)
        try:
            cur.execute(q.INSERT_PLAYER, (username, hashed))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def check_username_exists(username: str) -> bool:
    """Checks if the username the user tried to create an account with already exists."""
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
            cur.execute(q.GET_USERNAME, (username))
            result = cur.fetchone()
        except MySQLError as e:
            print(e)
            result = None
        finally:
            cur.close()
            conn.close()
        if result is None:
            return False
        return True

def check_password(username: str, password: str) -> bool:
    """Checks the entered password against the user's 
    stored hashed password to determine if it's correct."""
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
            cur.execute(q.GET_PASSWORD_HASH_BY_USERNAME, (username))
            result = cur.fetchone()
        except MySQLError:
            result = None
        finally:
            cur.close()
            conn.close()

    if result is not None:
        hashed = str(result[0])
        password_check = check_password_hash(hashed, password)
        if password_check is False:
            print("Incorrect password!")
        return password_check
    return False

def get_user_id(username: str) -> int:
    """Retrieves the unique user ID of the username."""
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
            cur.execute(q.GET_USERID_BY_USERNAME, (username))
            result = cur.fetchone()
            if result is not None:
                user_id = int(result[0])
        except MySQLError as e:
            print(e)
            user_id = None
        finally:
            cur.close()
            conn.close()

    if user_id is None:
        raise ValueError("UserID not found")
    return user_id

def get_username(user_id: int) -> str:
    """Retrieves the username associated with the unique user ID."""
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
            cur.execute(q.GET_USERNAME_BY_USERID, (user_id))
            result = cur.fetchone()
            if result is not None:
                username = str(result[0])
        except MySQLError as e:
            print(e)
            username = None
        finally:
            cur.close()
            conn.close()

    if username is None:
        raise ValueError("Username not found!")
    return username

def get_random_ep() -> int:
    """
    Retrieves a random episodeID from the database.
    """
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
            cur.execute(q.GET_RANDOM_EP)
            result = cur.fetchone()
            if result is not None:
                episode_id = int(result[0])
        except MySQLError as e:
            print(f"Error: {e}")
            episode_id = None
        finally:
            cur.close()
            conn.close()

    if episode_id is None:
        raise ValueError("EpisodeID not found")
    return episode_id

def get_ep_id_from_date(ep_date: str) -> int:
    """
    Retrieves an episode ID from the database based on the datetime given.
    """
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
            cur.execute(q.GET_EPID_FROM_DATE, (ep_date, ep_date))
            result = cur.fetchone()
            if result is not None:
                episode_id = int(result[0])
        except MySQLError:
            print("No episode found for the date given!")
            choice = input("Generate random episode? y/n ")
            if choice == "y":
                episode_id = get_random_ep()
            else:
                episode_id = None
        finally:
            cur.close()
            conn.close()

    if episode_id is None:
        raise ValueError("EpisodeID not found")
    return episode_id

def get_ep_title(episode_id: int) -> str | None:
    """
    Retrieves the episode title that corresponds to an episodeID from the database.
    """
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
            cur.execute(q.GET_EP_TITLE, (episode_id))
            result = cur.fetchone()
            if result is not None:
                ep_title = str(result[0])
        except MySQLError as e:
            print(f"Error: {e}")
            ep_title = None
        finally:
            cur.close()
            conn.close()

    if ep_title is None:
        raise ValueError("Episode title not found")
    return ep_title

def get_categories(episode_id: int, what_round: str) -> list[str]:
    """
    Retrieves a list of the categories in a given round from the database. 
    Round can be either "Regular" or "Double".
    """
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
            cur.execute(q.GET_CATEGORIES, (episode_id, what_round))
            result = cur.fetchall()
            if result is not None:
                categories = []
                for r in result:
                    categories.append(str(r[0]))
        except MySQLError as e:
            print(f"Error: {e}")
            categories = None
        finally:
            cur.close()
            conn.close()
    if categories is None:
        raise ValueError(f"No categories found for episodeID #{episode_id} in round {what_round}")
    return categories

def get_category_id(episode_id: int, name: str) -> int:
    """
    Gets the unique category ID of a category. NOTE: Category names are not unique.
    """
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
            cur.execute(q.GET_CATEGORY_ID, (episode_id, name))
            result = cur.fetchone()
            if result is not None:
                category_id = int(result[0])
        except MySQLError as e:
            print(f"Error: {e}")
            category_id = None
        finally:
            cur.close()
            conn.close()
    if category_id is None:
        raise ValueError("CategoryID not found")
    return category_id

def get_clue(category_id: int, moneyvalue: int) -> tuple[str, str]:
    """
    Retrieves a clue and its corresponding answer.

    Parameters
    ----------
    categoryID : int
        The category the cluegroup belongs to.
    moneyvalue : int
        The value of the clue.
    
    Returns
    -------
    result : tuple[str, str]
        A tuple representing the cluegroup. The first value
        is the clue, and the second is the answer. To use,
        call individual elements.
    """
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
            cur.execute(q.GET_CLUE, (category_id, moneyvalue))
            result = cur.fetchone()
        except MySQLError as e:
            print(f"Error: {e}")
            result = None
        finally:
            cur.close()
            conn.close()

    if result is None:
        raise ValueError("Clue not found")
    else:
        return result

def get_final_jeopardy(episode_id: int) -> tuple:
    """
    Retrieves all the information for Final Jeopardy from the
    database. Unlike get_clue, this also retrieves the category.
    
    Returns
    -------
    fj : tuple[str, str, str]
        The representation of the FJ round. The first element is
        the category, the second is the clue, and the third is
        the answer. To use, call individual elements.
    """
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
            cur.execute(q.GET_CATEGORIES, (episode_id, "Final"))
            result = cur.fetchone()
            if result is not None:
                category_name = str(result[0])
            cur.execute(q.GET_CATEGORY_ID, (episode_id, category_name))
            result = cur.fetchone()
            if result is not None:
                category_id = int(result[0])
            cur.execute(q.GET_CLUES, (category_id))
            result = cur.fetchone()
            if result is not None:
                clue_and_answer = list(result)
        except MySQLError as e:
            print(f"Error: {e}")
            category_name = None
            clue_and_answer = None
        finally:
            cur.close()
            conn.close()
    if clue_and_answer is None:
        raise ValueError("Can't find clue and answer group")
    fj = (category_name, clue_and_answer[0], clue_and_answer[1])
    return fj

def write_score(episode_id: int, user_id: int, score: int) -> None:
    """Adds a new score to the scores table."""
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
            cur.execute(q.INSERT_SCORE, (episode_id, user_id, score))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def check_score_id_exists(score_id: int) -> bool:
    """Check if the score ID exists in the scores table."""
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
            cur.execute(q.GET_SCORE_ID, (score_id))
            result = cur.fetchone()
        except MySQLError as e:
            print(e)
            result = None
        finally:
            cur.close()
            conn.close()

    if result is None:
        return False
    return True

def get_scores(user_id: int) -> tuple:
    """Get all scores that have a specific user ID attached."""
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
            cur.execute(q.GET_SCORES, (user_id))
            result = cur.fetchall()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

    if result is None:
        raise ValueError("No scores found")
    return result

def get_leaderboard() -> tuple:
    """Generates a leaderboard of the top 10 scores in the scores table."""
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
            cur.execute(q.GET_LEADERBOARD)
            result = cur.fetchall()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

    if result is None:
        raise ValueError("No scores found")
    return result

def generate_player_table() -> PrettyTable:
    """Creates a result set of all the players currently in the database.
    Accessible only to the admin."""
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
            cur.execute(q.GET_ALL_PLAYERS)
            player_table = from_db_cursor(cur)
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

    if player_table is None:
        raise ValueError("Can't generate player table")
    return player_table

def generate_score_table() -> PrettyTable:
    """Creates a result set of all the scores currently in the database.
    Accessible only to the admin."""
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
            cur.execute(q.GET_ALL_SCORES)
            score_table = from_db_cursor(cur)
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

    if score_table is None:
        raise ValueError("Can't generate score table")
    return score_table

def delete_scores_by_player(user_id: int) -> None:
    """Deletes all scores attached to a certain user ID.
    Accessible only to the admin."""
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
            cur.execute(q.DELETE_ALL_SCORES_BY_PLAYER, (user_id))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def delete_score_by_score_id(score_id: int) -> None:
    """Delete a score from the scores table.
    Accessible only to the admin."""
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
            cur.execute(q.DELETE_SCORE_BY_SCOREID, (score_id))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def delete_player(user_id: int) -> None:
    """Removes a user from the users table.
    Accessible only to the admin."""
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
            cur.execute(q.DELETE_PLAYER, (user_id))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()
