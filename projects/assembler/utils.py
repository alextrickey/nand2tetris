import re
from typing import List, Optional


def remove_whitespace(line: str):
    return re.sub(r"\s+", "", line)

def is_empty_string(line: str):
    return line == ""

def regex_any(codes: List[str]):
    return '((' + ')|('.join(codes) + '))'

def binary_string_from_int(value: int, binary_width: int = None):
    if not binary_width:
        return bin(value)[2:]
    max_value = 2**(binary_width)
    if value >= max_value:
        raise Exception(f"Input value to large to represent with {binary_width} digits")
    return bin(value + max_value)[3:]
