"""
SQL queries used to access the database server-side.
"""

SQL_INSERT_EPISODE = """
    INSERT INTO episodes 
    (epDate, epTitle) 
    VALUES 
    (%s, %s)
"""

SQL_INSERT_CATEGORY = """
    INSERT INTO categories
    (name, round, position, episodeID)
    VALUES
    (%s, %s, %s, %s)
"""

SQL_INSERT_CLUE = """
    INSERT INTO clues
    (categoryID, question, answer, moneyvalue)
    VALUES
    (%s, %s, %s, %s)
"""

SQL_GET_EPISODEID_BY_EPTITLE = """
    SELECT episodeID FROM episodes
    WHERE epTitle = %s
    ORDER BY episodeID
"""

SQL_GET_EPTITLE_EXISTENCE = """
    SELECT epTitle FROM episodes
    WHERE epTitle = %s
"""

SQL_GET_CATEGORYID_BY_NAME_AND_EPID = """
    SELECT categoryID FROM categories
    WHERE name = %s AND episodeID = %s
"""

SQL_GET_MAX_EPISODEID = """
    SELECT MAX(episodeID) + 1 FROM episodes
"""

SQL_GET_CATEGORY_ROUND = """
    SELECT round FROM categories
    WHERE categoryID = %s
"""

SQL_ALTER_AUTOINCREMENT = """
    ALTER TABLE episodes AUTO_INCREMENT = %s
"""

SQL_GET_CATEGORYIDS_BY_ROUND = """
    SELECT categoryID FROM categories
    WHERE round = %s AND episodeID = %s
    ORDER BY position
"""

SQL_GET_CLUES_BY_CATEGORYID = """
    SELECT clueID FROM clues
    WHERE categoryID = %s
    ORDER BY moneyvalue
"""

SQL_UPDATE_CATEGORY = """
    UPDATE categories 
    SET name = %s 
    WHERE categoryID = %s
"""

SQL_UPDATE_CLUES = """
    UPDATE clues 
    SET question = %s, answer = %s 
    WHERE clueID = %s
"""

SQL_GET_RANDOM_EP = """
    SELECT episodeID FROM episodes
    ORDER BY RAND()
    LIMIT 1;
"""

SQL_GET_EP_TITLE = """
    SELECT epTitle FROM episodes
    WHERE episodeID = %s
"""

SQL_GET_CATEGORIES = """
    SELECT name FROM categories
    WHERE episodeID = %s AND round = %s
    ORDER BY position;
"""

SQL_GET_CATEGORY_ID = """
    SELECT categoryID FROM categories
    WHERE episodeID = %s AND name = %s
"""

SQL_GET_EPISODE_ID_BY_CATEGORY_ID = """
    SELECT episodeID FROM categories
    WHERE categoryID = %s
"""

SQL_GET_ROUND_BY_EPISODE_ID_AND_MONEYVALUE = """
    SELECT name FROM categories
    WHERE episodeID = %s AND round = %s
"""

SQL_GET_ALL_CLUES_IN_MONEY_BRACKET = """
    SELECT
        clues.question AS question,
        clues.answer AS answer
    FROM
        clues
    JOIN
        categories ON clues.categoryID = categories.categoryID
    WHERE
        categories.round = %s AND
        clues.moneyvalue = %s AND
        categories.episodeID = %s
    ORDER BY
        categories.position
"""

SQL_GET_CLUE_BY_CATID_AND_MONEYVALUE = """
    SELECT question, answer FROM clues
    WHERE categoryID = %s AND moneyvalue = %s
"""

SQL_GET_CLUES_BY_CATID = """
    SELECT question, answer FROM clues
    WHERE categoryID = %s
"""
