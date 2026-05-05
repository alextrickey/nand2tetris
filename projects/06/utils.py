import re
from typing import List


def remove_whitespace(line: str):
    return re.sub(r"\s+", "", line)

def is_empty_string(line: str):
    return line == ""

def regex_any(codes: List[str]):
    return '((' + ')|('.join(codes) + '))'
