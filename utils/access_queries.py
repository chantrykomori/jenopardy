INSERT_PLAYER = """
    INSERT INTO players
    (username, password_hash)
    VALUES
    (%s, %s)
"""

GET_USERNAME = """
    SELECT username FROM players
    WHERE username = %s
"""

GET_PASSWORD_HASH_BY_USERNAME = """
    SELECT password_hash FROM players
    WHERE username = %s
"""

GET_USERID_BY_USERNAME = """
    SELECT userID FROM players
    WHERE username = %s
"""

GET_USERNAME_BY_USERID = """
    SELECT username FROM players
    WHERE userID = %s
"""

GET_RANDOM_EP = """
    SELECT episodeID FROM episodes
    ORDER BY RAND()
    LIMIT 1;
"""

GET_EPID_FROM_DATE = """
    SELECT episodeID FROM episodes
    WHERE epdate >= %s AND epdate < %s + INTERVAL 1 DAY
"""

GET_EP_TITLE = """
    SELECT epTitle FROM episodes
    WHERE episodeID = %s
"""

GET_CATEGORIES = """
    SELECT name FROM categories
    WHERE episodeID = %s AND round = %s
    ORDER BY position;
"""

GET_CATEGORY_ID = """
    SELECT categoryID FROM categories
    WHERE episodeID = %s AND name = %s
"""

GET_CLUE = """
    SELECT question, answer FROM clues
    WHERE categoryID = %s AND moneyvalue = %s
"""

GET_CLUES = """
    SELECT question, answer FROM clues
    WHERE categoryID = %s
"""

INSERT_SCORE = """
    INSERT INTO highscores
    (epID, player, score, date)
    VALUES
    (%s, %s, %s, NOW())
"""

GET_SCORES = """
    SELECT
        highscores.score,
        episodes.epTitle,
        highscores.date
    FROM
        highscores
    JOIN
       episodes ON highscores.epID = episodes.episodeID
    WHERE
        highscores.player = %s
    ORDER BY
        highscores.score DESC
    LIMIT 10;
"""

GET_ALL_SCORES = """
    SELECT
        highscores.scoreID AS "Score ID",
        players.userID AS "User ID",
        players.username AS "Username",
        highscores.score AS "Score",
        episodes.epTitle AS "Episode Title",
        episodes.epdate AS "Episode Airdate",
        highscores.date AS "Earned Date"
    FROM
        highscores
    JOIN
        players ON highscores.player = players.userID
    JOIN
        episodes ON highscores.epID = episodes.episodeID
    ORDER BY
        highscores.scoreID
"""

GET_LEADERBOARD = """
    SELECT
        players.username,
        highscores.score,
        episodes.epTitle,
        highscores.date
    FROM
        highscores
    JOIN
        players ON highscores.player = players.userID
    JOIN
        episodes ON highscores.epID = episodes.episodeID
    ORDER BY
        highscores.score DESC
    LIMIT 10;
"""

GET_SCORE_ID = """
    SELECT scoreID FROM highscores
    WHERE scoreID = %s
"""

DELETE_ALL_SCORES_BY_PLAYER = """
    DELETE FROM highscores
    WHERE player = %s
"""

DELETE_SCORE_BY_SCOREID = """
    DELETE FROM highscores
    WHERE scoreID = %s
"""

DELETE_PLAYER = """
    DELETE FROM players
    WHERE userID = %s
"""

GET_ALL_PLAYERS = """
    SELECT 
        userID AS "User ID",
        username AS "Username"
    FROM
        players
    ORDER BY
        userID
"""