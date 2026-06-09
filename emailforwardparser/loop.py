from re import Match, Pattern
from typing import Sequence

from .utils import split_with_regexp


def loop_regexes_replace(regexes: Sequence[Pattern[str]], string: str) -> str:
    match = string
    for regex in regexes:
        current_match = regex.sub("", string)
        if len(current_match) < len(match):
            match = current_match
            break
    return match


def loop_regexes_split(
    regexes: Sequence[Pattern[str]], string: str, highest_position: bool
) -> list[str]:
    match: list[str] = []
    for regex in regexes:
        current_match = split_with_regexp(regex, string)
        if len(current_match) > 1:
            if highest_position:
                if not match or len(match[0]) > len(current_match[0]):
                    match = current_match
            else:
                match = current_match
                break
    return match


def loop_regexes_match(
    regexes: Sequence[Pattern[str]], string: str
) -> tuple[list[str], Pattern[str] | None]:
    # leave match a match object until we are returning, cleans up code
    match: Match[str] | None = None
    regex_matched: Pattern[str] | None = None
    match_index = 0

    for regex in regexes:
        current_match = regex.search(string)
        if not current_match:  # style note
            continue
        current_match_index = current_match.start()
        # grab match that is closer to beginning of string
        if match is None or current_match_index < match_index:
            match = current_match
            match_index = current_match_index
            regex_matched = regex

    # Convert match from None to an empty list if no match is found
    if match is None:
        return [], regex_matched
    else:
        return [match.group(0), *[group or "" for group in match.groups()]], regex_matched
