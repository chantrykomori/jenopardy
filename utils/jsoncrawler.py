"""
Crawls the website j-archive for all Jeopardy episodes that they have currently uploaded,
and saves the data as a JSON file.
NOTE: Some data on the website is missing. When this occurs, a null value must be generated
in order for the JSON file to be structured correctly and the database to remain consistent.
Currently, this scraper gets all data every single time. Updates to check for changes to
the website are necessary.
"""

from typing import TypeAlias
from urllib.parse import urlparse
from urllib.parse import parse_qs
import re
import json
from bs4 import BeautifulSoup
import requests

WHERE = "jsondump/"

SEASONS_URL = "https://j-archive.com/listseasons.php"
ROOT_URL = "https://j-archive.com/"

CLUE_CONSTS = [1, 2, 3, 4, 5]
CATEGORY_CONSTS = [1, 2, 3, 4, 5, 6]
DJ_KEY = "DJ"
SJ_KEY = "J"
NJ_KEY = "NJ"

Rounds: TypeAlias = tuple[BeautifulSoup, BeautifulSoup, BeautifulSoup]
ClueDict: TypeAlias = dict[str, dict[str, str]]

def soupify_link(url) -> BeautifulSoup:
    """Converts a link into a BeautifulSoup object."""
    html = requests.get(url, timeout=10)
    soup = BeautifulSoup(html.text, 'lxml')
    return soup

def get_seasons() -> list[str]:
    """Retrieves a list of all links that go to a season's page."""
    soup = soupify_link(SEASONS_URL)
    links = soup.find_all("a")
    season_links = []
    for link in links:
        parsed = urlparse(link.attrs["href"])
        if parsed.path == "showseason.php":
            query = parse_qs(parsed.query)
            season_number = (query["season"])[0]
            print(f"Adding season {season_number} to queue...")
            season_id = link.attrs['href']
            temp_url = f"{ROOT_URL}{season_id}"
            season_links.append(temp_url)
    return season_links[2:]

def get_episodes(season_link) -> list[str]:
    """From a season's page, retrieves all episode page links."""
    game_links = []
    soup = soupify_link(season_link)
    links = soup.find_all("a")
    for link in links:
        parsed = urlparse(link.attrs['href'])
        if parsed.path == "showgame.php":
            query = parse_qs(parsed.query)
            game_number = (query["game_id"])[0]
            print(f"Adding game_id {game_number} to queue...")
            game_id = link.attrs['href']
            temp_url = f"{ROOT_URL}{game_id}"
            game_links.append(temp_url)
    return game_links

def create_rounds(soup: BeautifulSoup) -> Rounds:
    """Creates a tuple of three soups, which represents each round of Jeopardy."""
    # regex is the devil
    game_soup = soup.find("div", {"id":"game_title"})
    if game_soup is not None:
        game_title = game_soup.get_text()
    regex = re.compile(r"[0-9]+", re.IGNORECASE)
    regexed_game_title = regex.search(game_title)
    if regexed_game_title is not None:
        game_number = str(regexed_game_title.group(0))
    print(f"Creating rounds for game {game_number}...")

    jeopardy_round = soup.find("div", {"id":"jeopardy_round"})
    if jeopardy_round is None:
        jeopardy_round = "null"
    double_jeopardy_round = soup.find("div", {"id":"double_jeopardy_round"})
    if double_jeopardy_round is None:
        double_jeopardy_round = "null"
    final_jeopardy_round = soup.find("div", {"id":"final_jeopardy_round"})
    if final_jeopardy_round is None:
        final_jeopardy_round = "null"
    jrounds = (jeopardy_round, double_jeopardy_round, final_jeopardy_round)
    print("Rounds created!")
    return jrounds # type: ignore

def get_categories(soup: BeautifulSoup) -> list[str]:
    """Gets all categories from a soup. NOTE: This is for every round."""
    jround = soup.find("table", {"class":"round"})
    category_soups = jround.find_all("td", {"class":"category_name"}) # type: ignore
    categories = []
    if category_soups is not None:
        for csoup in category_soups:
            category_text = csoup.text
            categories.append(category_text)
        return categories
    raise ValueError("Can't get categories")

def get_clues(jround: BeautifulSoup, is_double: bool) -> ClueDict:
    """Gets all clues in an episode soup. NOTE: This is slow."""
    clue_lists = []
    answer_lists = []

    for category in CATEGORY_CONSTS:
        clue_list = []
        answer_list = []

        # NOTE: There is a separate set of tags for double jeopardy. Fortunately,
        # I am already capturing single/double jeopardy states, so it will just mean adding
        # another value to the interpolated strings below.

        for clue in CLUE_CONSTS:
            # first number represents category, second represents position
            if is_double is True:
                selected_key = DJ_KEY
            else:
                selected_key = SJ_KEY

            if jround == "null":
                selected_key = NJ_KEY
                clue_string = f"null_{selected_key}_{category}_{clue}"
                answer_string = f"null_{selected_key}_{category}_{clue}_r"
                # dd_string = "False"
            else:
                # dd_soup = jround.find_all("td", {"class":"clue_value_daily_double"})
                clue_soup = jround.find_all(
                    "td", {"id":f"clue_{selected_key}_{category}_{clue}"})
                answer_soup = jround.find_all(
                    "td", {"id":f"clue_{selected_key}_{category}_{clue}_r"})
                if len(clue_soup) > 0:
                    clue_string = clue_soup[0].get_text()
                # checking for if the length is just one char might work well
                else:
                    clue_string = f"null_{selected_key}_{category}_{clue}"
                if len(answer_soup) > 0:
                    nested_answer = answer_soup[0].find("em", {"class":"correct_response"})
                    answer_string = nested_answer.get_text()
                else:
                    answer_string = f"null_{selected_key}_{category}_{clue}_r"

            clue_list.append(clue_string)
            answer_list.append(answer_string)

        if len(clue_list) < 5:
            i = 0
            while len(clue_list) < 5:
                i += 1
                null_string = f"null_null_{i}_q"
                clue_list.append(null_string)
        if len(answer_list) < 5:
            i = 0
            while len(answer_list) < 5:
                i += 1
                null_string = f"null_null_{i}_q"
                answer_list.append(null_string)

        clue_lists.append(clue_list)
        answer_lists.append(answer_list)

    round_dict = {}
    if jround == "null":
        category_names = ["null_c_1", "null_c_2", "null_c_3", "null_c_4", "null_c_5", "null_c_6"]
    else:
        category_names = get_categories(jround)
        print("Adding round...")
    for index, category in enumerate(category_names):
        round_dict[category] = dict(zip(clue_lists[index], answer_lists[index]))
    return round_dict

def get_final_jeopardy(jround: BeautifulSoup) -> ClueDict:
    """Gets all aspects of Final Jeopardy and returns it as a tuple."""
    if jround == "null":
        category_string = "null_category"
        clue_string = "null_FJ"
        answer_string = "null_FJ_r"
    else:
        category_string = jround.find("td", {"class":"category_name"}).get_text() # type: ignore
        clue_string = jround.find("td", {"id":"clue_FJ"}).get_text() # type: ignore
        answer_string = jround.find("em", {"class":"correct_response"}).get_text() # type: ignore
    clue_and_answer = {clue_string: answer_string}
    final_jeopardy_round = {category_string: clue_and_answer}
    print("Adding FJ...")
    return final_jeopardy_round

def build_episode_data(soup) -> tuple[ClueDict, ClueDict, ClueDict]:
    """Creates a full episode as a tuple of three rounds."""
    # This needs to run for all episodes, not just the two on the pilots
    jrounds = create_rounds(soup)
    full_episode_list = []
    for round_number, jround in enumerate(jrounds):
        # Here is where getClues needs to get single or double Jeopardy
        if round_number == 0:
            clues_and_answers = get_clues(jround, is_double=False)
        elif round_number == 1:
            clues_and_answers = get_clues(jround, is_double=True)
        elif round_number == 2:
            #here is where final jeopardy parsing should happen
            clues_and_answers = get_final_jeopardy(jround)
        full_episode_list.append(clues_and_answers)
    full_episode = tuple(full_episode_list)
    return full_episode

def get_title(episode_link: str) -> str:
    """Finds the episode title to use from the episode link."""
    episode_soup = soupify_link(episode_link)
    title_soup = episode_soup.find("div", {"id":"game_title"})
    title_string = title_soup.get_text() # type: ignore
    return title_string

def crawl():
    """Crawls the entire j-archive website for all currently listed episodes,
    parses them, and dumps the data to a JSON."""
    seasons = get_seasons()
    for season in seasons:
        episodes = get_episodes(season)
        for episode in episodes:
            ep_title = get_title(episode)
            jsondata = f"{ep_title}.json"
            soup = soupify_link(episode)
            episode_data = build_episode_data(soup)
            with open(WHERE + jsondata, "w", encoding="utf-8") as jf:
                json.dump(episode_data, jf)
