from dataclasses import dataclass
from typing import *

@dataclass
class FileResults:
    animals_in_file : Set[str]
    animals_not_in_file : Set[str]

# Given an input file, return two sets containing every animal in the file and every animal not in the file
def animals_in_file(input : str) -> FileResults:
    pass