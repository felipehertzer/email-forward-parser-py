import email.errors
import email.header
import re
import unicodedata
from re import Match, Pattern

# A run of RFC 2047 encoded words ("=?utf-8?q?caf=C3=A9?="), where adjacent words
# may be separated by spaces or tabs that are not part of the decoded text. The
# encoded text cannot contain "?" and a word never spans lines.
_ENCODED_WORD = r"=\?[^?\s]+\?[bBqQ]\?[^?\n]*\?="
ENCODED_WORDS = re.compile(rf"{_ENCODED_WORD}(?:[ \t]*{_ENCODED_WORD})*")


def is_graphic(char: str) -> bool:
    """Check if a character is a graphic character."""
    if char in {"\n", "\r", "\t"}:
        return True
    return unicodedata.category(char)[0] in {"L", "M", "N", "P", "S", "Z"}


def decode_encoded_words(match: Match[str]) -> str:
    """Decode one run of encoded words, or keep it verbatim when it cannot be decoded."""
    words = match.group(0)
    try:
        return "".join(
            part.decode(charset or "ascii", errors="replace") if isinstance(part, bytes) else part
            for part, charset in email.header.decode_header(words)
        )
    except LookupError, UnicodeError, email.errors.HeaderParseError:
        return words


def preprocess_string(s: str) -> str:
    s = "".join(char for char in s if is_graphic(char))
    s = s.replace("\ufeff", "")
    # Decode encoded words in place. email.header.decode_header() on the whole
    # text would join every line into one (so no line-anchored pattern could
    # match) and raises on an unknown charset or invalid bytes.
    return ENCODED_WORDS.sub(decode_encoded_words, s)


def find_named_matches(pattern: Pattern[str], s: str) -> dict[str, str]:
    match = pattern.match(s)
    if match:
        return match.groupdict()
    return {}


def find_all_string_submatch_index(pattern: Pattern[str], s: str, n: int = -1) -> list[list[int]]:
    matches: list[list[int]] = []

    for match in pattern.finditer(s):
        # Extracting the start and end indices of the match and all submatches
        # This is equivalent to flattening the match indices as done in the Go code
        flat_indices: list[int] = []
        for group in range(len(match.groups()) + 1):  # +1 to include the whole match
            flat_indices.extend(match.span(group))

        matches.append(flat_indices)

        # If n is specified and we've reached the limit, break
        if n > 0 and len(matches) >= n:
            break
    return matches


def split_with_regexp(pattern: Pattern[str], s: str) -> list[str]:
    split_indices = find_all_string_submatch_index(pattern, s)

    if not split_indices:
        return [s]

    result: list[str] = []
    prev_index = 0

    new_split_indices: list[list[int]] = []
    for indices in split_indices:
        new_indices: list[int] = []
        for i in range(0, len(indices), 2):
            ia, ib = indices[i], indices[i + 1]
            if i > 0:
                ya, yb = indices[i - 2], indices[i - 1]
                if ia == ya and ib == yb:
                    continue
            new_indices.extend([ia, ib])
        new_split_indices.append(new_indices)

    split_indices = new_split_indices

    if split_indices[0][0] == 0:
        result.append("")

    for indices in split_indices:
        for i in range(0, len(indices), 2):
            ia, ib = indices[i], indices[i + 1]
            if prev_index < ia:
                result.append(s[prev_index:ia])
            result.append(s[ia:ib])
            prev_index = ib

    if prev_index < len(s):
        result.append(s[prev_index:])

    return result
