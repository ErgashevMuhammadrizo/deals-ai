"""Independent checks for numeric claims made in customer-facing answers."""
import re
import unicodedata

NUMBER = re.compile(r'\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?\s*%?')


def numeric_claims(text):
    normalized = unicodedata.normalize('NFKC', text)
    return {match.group().replace(' ', '').replace(',', '.') for match in NUMBER.finditer(normalized)}


def unsupported_numbers(answer, sources):
    evidence = set().union(*(numeric_claims(source.content) for source in sources))
    return numeric_claims(answer) - evidence
