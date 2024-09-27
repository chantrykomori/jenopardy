"""A module to display the game's credits. It sits in its own module for length reasons."""

def view_credits() -> None:
    """Displays the game's credits."""
    game_credits = """
Enormous thanks to j-archive.com, whose work made this project possible.
Logo courtesy of the ASCII Art Generator by Patrick Gillespie at http://patorjk.com/blog/software/
Icon courtesy of Freepik
Dedicated to Alex Trebek.

Jenopardy! Console Game © 2024 by Jenova Edenson is licensed under CC BY-NC-SA 4.0"""
    print(game_credits)
