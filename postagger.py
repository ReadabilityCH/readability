import os
from _pickle import dump, load

import nltk
from nltk.corpus import brown

TAGGER = None


def create_tagger():
    train_sents = brown.tagged_sents()

    t0 = nltk.RegexpTagger(
        [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
         (r'(The|the|A|a|An|an)$', 'AT'),  # articles
         (r'.*able$', 'JJ'),  # adjectives
         (r'.*ness$', 'NN'),  # nouns formed from adjectives
         (r'.*ly$', 'RB'),  # adverbs
         (r'.*s$', 'NNS'),  # plural nouns
         (r'.*ing$', 'VBG'),  # gerunds
         (r'.*ed$', 'VBD'),  # past tense verbs
         (r'.*', 'NN')  # nouns (default)
         ])

    t1 = nltk.UnigramTagger(train_sents, backoff=t0)

    t2 = nltk.BigramTagger(train_sents, backoff=t1)

    t3 = nltk.TrigramTagger(train_sents, backoff=t2)

    return t3


def save_tagger(tagger):
    output = open('tagger.pkl', 'wb')
    dump(tagger, output, -1)
    output.close()


def get_tagger():
    if os.path.exists("tagger.pkl"):
        input = open('tagger.pkl', 'rb')
        tagger = load(input)
        input.close()
        return tagger
    else:
        tagger = create_tagger()
        save_tagger(tagger)
        return tagger
