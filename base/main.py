import string
import sys
import unittest
from typing import *
from dataclasses import dataclass
sys.setrecursionlimit(10**6)

IntList : TypeAlias = Optional["IntNode"]
WordLinesList : TypeAlias = Optional["WordLineNode"]


@dataclass
class LLIterator:
    list : IntList | WordLinesList
    def __iter__(self) -> Self:
        return self
    def __next__(self) -> "int | WordLines":
        if (self.list is None):
            raise StopIteration
        to_return = self.list.value
        self.list = self.list.next
        return to_return


@dataclass(frozen=True)
class IntNode:
    value: int
    next: IntList
    def __iter__(self) -> LLIterator:
        return LLIterator(self)


@dataclass
class WordLines:
    word: str
    line_numbers: IntList

@dataclass(frozen=True)
class WordLineNode:
    value : WordLines
    next: WordLinesList
    def __iter__(self) -> LLIterator:
        return LLIterator(self)

@dataclass
class HashTable:
    table : List[WordLinesList]
    count : int

# Returns a hash of string
def hash_fn(v:str) -> int:
    pow = 1
    n = 0
    for i in reversed(range(len(v))):
        n += ord(v[i]) * pow
        pow *= 31
    return n

# Makes an empty hashtable
def make_hash(size:int) -> HashTable:
    return HashTable([None] * size, 0)

# Return the number of elements in the given hash table
def hash_count(ht:HashTable) -> int:
    return ht.count

# Return the size of the given hash table
def hash_size(ht:HashTable) -> int:
    return len(ht.table)

# Does the hash table contain a mapping for the given word?
def has_key(ht:HashTable, key:str) -> bool:
    if ht.table[hash_fn(key) % len(ht.table)] != None:
        return find_word_line(ht.table[hash_fn(key) % len(ht.table)], key) is not None
    else:
        return False

# What line numbers is the given key mapped to in the given hash table?
def lookup(ht:HashTable, key:str) -> List[int]:
    if ht.table[hash_fn(key) % len(ht.table)] != None:
        line : Optional[WordLines] = find_word_line(ht.table[hash_fn(key) % len(ht.table)], key)
        if line != None:
            result : List[int] = [number for number in line.line_numbers]
            return result
        else:
            result : List[int] = []
            return result
    else:
        result: List[int] = []
        return result

# Finds a word line with the given key in a word line list
def find_word_line(word_line_list: WordLinesList, word:str) -> Optional[WordLines]:
    return None if word_line_list is None else (
        word_line_list.value if word_line_list.value.word == word else find_word_line(word_line_list.next,word)
    )

# Adds the value to the end of the list if it isn't already in the list
def append_list(list : IntList | WordLinesList, value : int | WordLines) -> IntList | WordLinesList:
    return (IntNode(value,None) if isinstance(value,int) else WordLineNode(value,None)) if list is None else (
        (
            IntNode(list.value, append_list(list.next, value)) if isinstance(value,int) else WordLineNode(list.value, append_list(list.next, value))
        ) if list.value != value else list
    )
# Adds a word-line mapping to an array
def add_word_lines(array: List[WordLinesList], value :  WordLines) -> None:
    array[hash_fn(value.word) % len(array)] = append_list(array[hash_fn(value.word) % len(array)], value)


# Add a mapping from the given word to the given line number in
# the given hash table
def add(ht: HashTable, word: str, line_number: int) -> None:
    lines : WordLinesList = ht.table[hash_fn(word) % len(ht.table)]
    if lines is not None:
        line : WordLines = find_word_line(lines, word)
        if line is not None:
            line.line_numbers = append_list(line.line_numbers, line_number)
        else:
            add_word_lines(ht.table, WordLines(word,IntNode(line_number,None)))
            ht.count += 1
    else:
        add_word_lines(ht.table, WordLines(word,IntNode(line_number,None)))
        ht.count += 1

    if (ht.count >= len(ht.table)):
        new_table : List[WordLinesList] = [None] * len(ht.table) * 2
        for section in ht.table:
            if section is not None:
                for word_lines in section:
                    add_word_lines(new_table, word_lines)

        ht.table = new_table

# What are the words that have mappings in this hash table?
def hash_keys(ht: HashTable) -> List[str]:
    keys : List[str] = [""] * ht.count
    i = 0
    for section in ht.table:
        if section is not None:
            for word_line in section:
                keys[i] = word_line.word
                i+= 1
    return keys

# given a list of stop words and a list of strings representing lines of
# a text, return a hash table
def make_concordance(stop_words: HashTable, text: List[str]) -> HashTable:
    table : HashTable = make_hash(128)
    for i in range(len(text)):
        line = text[i].replace("'","")
        for char in string.punctuation:
            line = line.replace(char," ")
        line = line.lower().split()
        for token in line:
            if token.isalpha() and not has_key(stop_words, token):
                add(table,token,i)
    return table

# given an input file , a stop-words file, and an output file, overwrite the output file with
# a sorted concordance of the input file.
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:
    stop_words : HashTable
    with open(stop_words_file) as stop_words_file:
        stop_words = make_concordance(make_hash(1), stop_words_file.readlines())
    lines : List[str]
    with open(in_file) as in_file:
        lines = in_file.readlines()

    concordance = make_concordance(stop_words, lines)

    words = hash_keys(concordance)
    words.sort()
    data = '\n'.join(f"{word} {' '.join(map(str,lookup(concordance, word)))}" for word in words)


    with open(out_file, "w") as out_file:
        out_file.write(data)

if __name__ == "__main__":
    full_concordance("in","stop","out")

class Tests(unittest.TestCase):
    def test_hash_fn(self):
        self.assertEqual(hash_fn("abc"), 96354)
    def test_make_hash(self):
        self.assertEqual(make_hash(10), HashTable([None] * 10, 0))
    def test_has_key(self):
        self.assertEqual(has_key(make_hash(10), ""), False)
        self.assertEqual(has_key(make_hash(10), "a"), False)
        self.assertEqual(has_key(make_hash(10), "b"), False)
        table = make_hash(10)
        add(table,"a",0)
        add(table,"b",1)
        add(table,"c",2)
        self.assertEqual(has_key(table, "a"), True)
        self.assertEqual(has_key(table, "b"), True)
        self.assertEqual(has_key(table, "c"), True)
        self.assertEqual(has_key(table, "d"), False)
        self.assertEqual(has_key(table, "e"), False)
    def test_add(self):
        table = make_hash(1)
        add(table,"a",0)
        add(table,"b",1)
        add(table,"c",2)
        self.assertEqual(len(table.table), 4)
        self.assertTrue(has_key(table, "a"))
        self.assertTrue(has_key(table, "b"))
        self.assertTrue(has_key(table, "c"))
        self.assertFalse(has_key(table, "d"))
        self.assertFalse(has_key(table, "e"))
    def test_hash_keys(self):
        table = make_hash(256)
        add(table,"icy",0)
        add(table,"nature",0)
        add(table,"derrek",0)
        add(table,"yay",0)
        add(table,"suppamen",0)
        keys = hash_keys(table)
        self.assertEqual(len(keys), 5)
        self.assertEqual(set(keys), {"icy","nature","derrek","yay","suppamen"})
    def test_append_list(self):
        # Appending duplicates should have no effect
        list : IntList = IntNode(0,None)
        list = append_list(list, 1)
        list = append_list(list, 2)
        list = append_list(list, 3)
        list = append_list(list, 2)
        list = append_list(list, 4)
        list = append_list(list, 3)
        self.assertEqual(list, IntNode(0,IntNode(1,IntNode(2,IntNode(3,IntNode(4,None))))))
    def test_make_concordance(self):
        stop_words : HashTable = make_hash(128)
        add(stop_words,"melt",1)
        add(stop_words,"fish",2)
        concordance = make_concordance(stop_words,["I melt a fish every day and it is wonderful", "wowie text works and that is cool", "So cool in fact that my punctuation disappears!!!!!!wow.much,cool;bingo.bongo,nonumbershere'andthisisallverylongoneword.hiphiphooray. Anyway I hope your having a good day and this line is rather long indeed bingo"])
        self.assertEqual(set(hash_keys(concordance)),{'works', 'hiphiphooray', 'anyway', 'indeed', 'much', 'every', 'day', 'this', 'wow', 'in', 'having', 'that', 'is', 'it', 'my', 'text', 'bingo', 'disappears', 'your', 'hope', 'good', 'cool', 'rather', 'and', 'punctuation', 'so', 'a', 'wonderful', 'nonumbershereandthisisallverylongoneword', 'i', 'bongo', 'fact', 'line', 'wowie', 'long'})