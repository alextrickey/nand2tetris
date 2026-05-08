import re
from typing import List, Optional


def remove_whitespace(line: str):
    """Clears any whitespace from the provided line of text
        
    Parameters
    ----------
    line : str 
        A line of text 

    Returns
    ----------
    str
        The line with whitespace removed
    """
    return re.sub(r"\s+", "", line)

def is_empty_string(line: str):
    """Compares the line of text with an empty string
        
    Parameters
    ----------
    line : str 
        A line of text 

    Returns
    ----------
    bool
        True if the line is empty, otherwise False
    """
    return line == ""

def regex_any(codes: List[str]):
    """Given a list of raw strings / regex patterns (codes), generate 
    the regex pattern that will match another string if that string 
    contains any of the codes in the list.
        
    Parameters
    ----------
    codes : List[str] 
        A list of strings 

    Returns
    ----------
    str
        The regex pattern matching any of the provided codes
    """
    return r'((' + r')|('.join(codes) + r'))'

def binary_string_from_int(value: int, binary_width: Optional[int] = None):
    """Given a base-10 formatted integer generate the corresponding binary 
    integer as string. If binary_width is not None, left-pad the string with
    zeros so that it is exactly binary_width bits long. Error if the provided
    width is too small to represent the binary number. 
        
    Parameters
    ----------
    value : int
        The number to be converted to binary
    binary_width : Optional[int]
        The number of bits to return. (The result will be left-padded with zeros 
        to achieve the required binary_width.)

    Returns
    ----------
    str
        A string containing the binary representation
    
    Raises
    ----------
    Exception
        If the provided binary_width is too narrow to represent the value
    """
    if not binary_width:
        return bin(value)[2:]
    max_value = 2**(binary_width)
    if value >= max_value:
        raise Exception(f"Input value to large to represent with {binary_width} digits")
    return bin(value + max_value)[3:]
