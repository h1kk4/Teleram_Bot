import re
import math
import nltk
import nltk.data
import collections
from nltk.stem import WordNetLemmatizer, SnowballStemmer

NLTK_PUNKT_TOKENIZER = 'tokenizers/punkt/english.pickle'
NLTK_STEMMER = 'english'


def get_unknown_words(text):
    tokenizer = nltk.data.load(NLTK_PUNKT_TOKENIZER)
    lemmatizer = WordNetLemmatizer()
    stemmer = SnowballStemmer(NLTK_STEMMER)

    ne_stems = set()
    word_map = collections.defaultdict(list)

    text = re.sub('n\'[ts]', '', text)
    sents = tokenizer.tokenize(text)

    for sent in sents:

        tokens = nltk.wordpunct_tokenize(sent)
        tokens = [t for t in tokens if t.isalpha() and len(t) > 2]

        for i in range(len(tokens)):

            token = tokens[i].lower()
            for pos in ['a', 'n', 'v']:
                token = lemmatizer.lemmatize(token, pos)

            stem = stemmer.stem(token)

            if i == 0 or tokens[i][0].islower():
                word_map[stem].append(token)
            else:
                ne_stems.add(stem)

    scored_words = []
    for stem, words in word_map.items():
        if stem not in ne_stems:
            word = min(words, key=len)
            scored_words.append(word)

    scored_words = [w for w in scored_words if len(w) > 2]

    return scored_words
