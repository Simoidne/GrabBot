from confusables import confusable_regex
import re
from typing import List

def msg_contains_forbidden(msg: str, forbidden_words: List[str]) -> bool:
  """Returns True if msg contains a word in the forbidden_words list or
  is confusable with any words in forbidden_words
  """

  contains_forbidden = False
  for word in forbidden_words:
    regex_string = confusable_regex(word, include_character_padding=True)
    regex = re.compile(regex_string)

    contains_forbidden = regex.search(msg)
  
  return contains_forbidden