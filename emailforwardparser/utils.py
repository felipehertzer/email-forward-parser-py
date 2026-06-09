import email.header
import unicodedata
from re import Pattern


def is_graphic(char: str) -> bool:
    """Check if a character is a graphic character."""
    if char in {"\n", "\r", "\t"}:
        return True
    return unicodedata.category(char)[0] in {"L", "M", "N", "P", "S", "Z"}


def preprocess_string(s: str) -> str:
    s = "".join(char for char in s if is_graphic(char))
    s = s.replace("\ufeff", "")
    s = str(email.header.make_header(email.header.decode_header(s)))
    return s


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
    # test = [match.span() for match in pattern.finditer(s)]
    split_indices = find_all_string_submatch_index(pattern, s)

    if not split_indices:
        return [s]

    # if split_indices:
    # print(f"splitIndices: {split_indices}")

    result: list[str] = []
    prev_index = 0

    new_split_indices: list[list[int]] = []
    for indices in split_indices:
        new_indicie = []
        for i in range(0, len(indices), 2):
            ia, ib = indices[i], indices[i + 1]
            if i > 0:
                ya, yb = indices[i - 2], indices[i - 1]
                if ia == ya and ib == yb:
                    continue
            new_indicie.extend([ia, ib])
        new_split_indices.append(new_indicie)

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
