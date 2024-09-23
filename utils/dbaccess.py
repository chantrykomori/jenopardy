import pymysql
import sshtunnel
import utils.access_queries as q
from config import Config
from pymysql import MySQLError
from werkzeug.security import generate_password_hash, check_password_hash
from prettytable import from_db_cursor, PrettyTable

sshtunnel.SSH_TIMEOUT = 300.0
sshtunnel.TUNNEL_TIMEOUT = 300.0

def add_player_to_table(username: str, password: str) -> None:
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
        hash = generate_password_hash(password)
        try:
            cur.execute(q.INSERT_PLAYER, (username, hash))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def check_username_exists(username: str) -> bool:
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
        
        if result == None:
            return False
        else:
            return True

def check_password(username: str, password: str) -> bool:
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
        hash = str(result[0])
        password_check = check_password_hash(hash, password)
        if password_check is False:
            print("Incorrect password!")
        return password_check
    else:
        return False
    
def get_user_id(username: str) -> int:
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
                userID = int(result[0])
        except MySQLError as e:
            print(e)
            userID = None
        finally:
            cur.close()
            conn.close()

    if userID is None:
        raise ValueError("UserID not found")
    else:
        return userID

def get_username(userID: int) -> str:
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
            cur.execute(q.GET_USERNAME_BY_USERID, (userID))
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
    else:
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
                episodeID = int(result[0])
        except MySQLError as e:
            print(f"Error: {e}")
            episodeID = None
        finally:
            cur.close()
            conn.close()

    if episodeID is None:
        raise ValueError("EpisodeID not found")
    else:
        return episodeID

def get_epID_from_date(ep_date: str) -> int:
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
                episodeID = int(result[0])
        except MySQLError:
            print("No episode found for the date given!")
            choice = input("Generate random episode? y/n ")
            if choice == "y":
                episodeID = get_random_ep()
            else:
                episodeID = None
        finally:
            cur.close()
            conn.close()

    if episodeID is None:
        raise ValueError("EpisodeID not found")
    else:
        return episodeID

def get_ep_title(episodeID: int) -> str | None:
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
            cur.execute(q.GET_EP_TITLE, (episodeID))
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
    else:
        return ep_title

def get_categories(episodeID: int, what_round: str) -> list[str]:
    """
    Retrieves a list of the categories in a given round from the database.

    Parameters
    ----------
    episodeID : int
        EpisodeID field of the episode to use
    whatRound : str
        String representation of the round to use. Takes either "Regular" or "Double".
    
    Returns
    -------
    categories : list[str]
        The categories corresponding to the episodeID and round.
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
            cur.execute(q.GET_CATEGORIES, (episodeID, what_round))
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
        raise ValueError(f"No categories found for episodeID #{episodeID} in round {what_round}")
    else:
        return categories

def get_category_ID(episodeID: int, name: str) -> int:
    """
    Retrieves the categoryID field from a category in the database.

    Parameters
    ----------
    episodeID : int
        EpisodeID field of the episode to use
    name : str
        The name of the category
    
    Returns
    -------
    categoryID : int
        The unique categoryID field corresponding to the category name and episodeID.
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
            cur.execute(q.GET_CATEGORY_ID, (episodeID, name))
            result = cur.fetchone()
            if result is not None:
                categoryID = int(result[0])
        except MySQLError as e:
            print(f"Error: {e}")
            categoryID = None
        finally:
            cur.close()
            conn.close()
    
    if categoryID is None:
        raise ValueError("CategoryID not found")
    else:
        return categoryID

def get_clue(categoryID: int, moneyvalue: int) -> tuple[str, str]:
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
            cur.execute(q.GET_CLUE, (categoryID, moneyvalue))
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

# need to fix this
def get_final_jeopardy(episodeID: int) -> tuple:
    """
    Retrieves all the information for Final Jeopardy from the
    database. Unlike get_clue, this also retrieves the category.

    Parameters
    ----------
    episodeID : int
        The episodeID from the database.

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
            cur.execute(q.GET_CATEGORIES, (episodeID, "Final"))
            result = cur.fetchone()
            if result is not None:
                category_name = str(result[0])
            cur.execute(q.GET_CATEGORY_ID, (episodeID, category_name))
            result = cur.fetchone()
            if result is not None:
                categoryID = int(result[0])
            cur.execute(q.GET_CLUES, (categoryID))
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
    else:
        fj = (category_name, clue_and_answer[0], clue_and_answer[1])
        return fj

def write_score(episodeID: int, userID: int, score: int) -> None:
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
            cur.execute(q.INSERT_SCORE, (episodeID, userID, score))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def check_scoreID_exists(scoreID: int) -> bool:
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
            cur.execute(q.GET_SCORE_ID, (scoreID))
            result = cur.fetchone()
        except MySQLError as e:
            print(e)
            result = None
        finally:
            cur.close()
            conn.close()

    if result is None:
        return False
    else:
        return True

def get_scores(userID: int) -> tuple:
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
            cur.execute(q.GET_SCORES, (userID))
            result = cur.fetchall()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

    if result is None:
        raise ValueError("No scores found")
    else:
        return result

def get_leaderboard() -> tuple:
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
    else:
        return result

def generate_player_table() -> PrettyTable:
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
    else:
        return player_table

def generate_score_table() -> PrettyTable:
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
    else:
        return score_table

def delete_scores_by_player(userID: int) -> None:
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
            cur.execute(q.DELETE_ALL_SCORES_BY_PLAYER, (userID))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()
    
def delete_score_by_scoreID(scoreID: int) -> None:
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
            cur.execute(q.DELETE_SCORE_BY_SCOREID, (scoreID))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()

def delete_player(userID: int) -> None:
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
            cur.execute(q.DELETE_PLAYER, (userID))
            cur.connection.commit()
        except MySQLError as e:
            print(e)
        finally:
            cur.close()
            conn.close()