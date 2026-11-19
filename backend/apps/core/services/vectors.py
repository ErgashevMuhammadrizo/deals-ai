"""Sparse hashed word and character-trigram embeddings for local retrieval."""
from collections import Counter
import hashlib
import math
import re
import unicodedata


def embed(text):
    words=re.findall(r'\w+',unicodedata.normalize('NFKC',text).casefold())
    weights=Counter()
    for word in words:
        features=[(word,3)]+[(word[i:i+3],1) for i in range(len(word)-2)]
        for feature,weight in features:
            index=hashlib.blake2s(feature.encode(),digest_size=3).hexdigest()
            weights[index]+=weight
    length=math.sqrt(sum(value**2 for value in weights.values())) or 1
    return {index:round(value/length,6) for index,value in weights.items()}


def similarity(query, document):
    return sum(weight*document.get(index,0) for index,weight in query.items())
