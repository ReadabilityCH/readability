import re
import string
from collections import Counter
from itertools import dropwhile
from typing import Optional

import nltk
import textstat
from nltk import tokenize
from nltk.corpus import cmudict
from nltk.corpus import stopwords

from .graph import get_value_from_raygor_graph, get_value_from_fry_graph
from .postagger import get_tagger

TAGGER = get_tagger()

en_stopwords = stopwords.words('english')
phoneme_dict = dict(cmudict.entries())

named_entity = ['ORGANIZATION', 'PERSON', 'LOCATION', 'DATE', 'TIME', 'MONEY', 'PERCENT', 'FACILITY', 'GPE']

pos_tags = {
    'QL',  # qualifier
    'CC',  # coordinating conjunction
    'CD',  # cardinal digit
    'DT',  # determiner
    'EX',  # existential there (like: "there is" ... think of it like "there exists")
    'FW',  # foreign word
    'IN',  # preposition/subordinating conjunction
    'JJ',  # adjective	'big'
    'JJR',  # adjective, comparative	'bigger'
    'JJS',  # adjective, superlative	'biggest'
    'LS',  # list marker	1)
    'MD',  # modal	could, will
    'NN',  # noun, singular 'desk'
    'NNS',  # noun plural	'desks'
    'NNP',  # proper noun, singular	'Harrison'
    'NNPS',  # proper noun, plural	'Americans'
    'PDT',  # predeterminer	'all the kids'
    'POS',  # possessive ending	parent\'s
    'PRP',  # personal pronoun	I, he, she
    'PRP$',  # possessive pronoun	my, his, hers
    'RB',  # adverb	very, silently,
    'RBR',  # adverb, comparative	better
    'RBS',  # adverb, superlative	best
    'RP',  # particle	give up
    'TO',  # to	go 'to' the store.
    'UH',  # interjection	errrrrrrrm
    'VB',  # verb, base form	take
    'VBD',  # verb, past tense	took
    'VBG',  # verb, gerund/present participle	taking
    'VBN',  # verb, past participle	taken
    'VBP',  # verb, sing. present, non-3d	take
    'VBZ',  # verb, 3rd person sing. present	takes
    'WDT',  # wh-determiner	which
    'WP',  # wh-pronoun	who, what
    'WP$',  # possessive wh-pronoun	whose
    'WRB',  # wh-abverb	where, when
}

allowed_pos_tags = {
    'JJ',  # adjective	'big'
    'JJR',  # adjective, comparative	'bigger'
    'JJS',  # adjective, superlative	'biggest'
    'NN',  # noun, singular 'desk'
    'NNS',  # noun plural	'desks'
    'NNP',  # proper noun, singular	'Harrison'
    'NNPS',  # proper noun, plural	'Americans'
    'RB',  # adverb	very, silently,
    'RBR',  # adverb, comparative	better
    'RBS',  # adverb, superlative	best
}


# redability

def passivep(tags):
    def find_compound_words(word, postToBe):
        words_return = ""
        for post in enumerate(postToBe, 0):
            words_return = words_return + f" {post[1][0]}"
            if word == post[1][0]:
                break
        return words_return.strip()

    postToBe = list(dropwhile(lambda tag: not tag[1].startswith("BE"), tags))
    nongerund = lambda tag: tag[1].startswith("V") and not tag[1].startswith("VBG")

    filtered = filter(nongerund, postToBe)
    out = any(filtered)
    list_words_return = []
    if out:
        words_found = list(filter(nongerund, postToBe))
        word = words_found[0]
        list_words_return.append(find_compound_words(word[0], postToBe))

    return list_words_return


def tag_sentence(sent):
    assert isinstance(sent, str)

    tokens = nltk.word_tokenize(sent)
    return TAGGER.tag(tokens)


def find_passives(sentences):
    passive_voises_return = []
    for sent in sentences:
        tagged = tag_sentence(sent)
        list_words_return = passivep(tagged)
        if list_words_return:
            passive_voises_return.append(list_words_return[0])
    return passive_voises_return


def find_adverbs(pos_tags):
    adverbs_return = []
    for item in pos_tags:
        if item[1] in ['RB', 'RBR', 'RBS']:
            adverbs_return.append(item[0])

    return adverbs_return


def get_grade_levels(grade_level):
    return round(grade_level.score, 2)


def count_average_grade_levels(grade_levels):
    # A 100.00-90.00
    # B 90.0–80.0 80.0–70.0
    # C 70.0–60.0
    # D 60.0–50.0
    # E 50.0–30.0 30.0–0.0

    grade_score = grade_levels.get('flesch')

    if int(grade_score) in range(90, 1001):
        return 'A'
    elif int(grade_score) in range(70, 91):
        return 'B'
    elif int(grade_score) in range(60, 71):
        return 'C'
    elif int(grade_score) in range(50, 61):
        return 'D'
    else:
        return 'E'


def count_ielts_levels(grade_levels):
    grade_score = grade_levels.get('flesch')

    if int(grade_score) in range(75, 1001):
        return '1-2'
    elif int(grade_score) in range(60, 76):
        return '3-4'
    elif int(grade_score) in range(45, 61):
        return '5-6'
    elif int(grade_score) in range(30, 46):
        return '7-8'
    else:
        return '9'


def count_cefr_levels(grade_levels):
    grade_score = grade_levels.get('flesch')

    if int(grade_score) in range(90, 1001):
        return 'A1'
    elif int(grade_score) in range(75, 91):
        return 'A2'
    elif int(grade_score) in range(60, 76):
        return 'B1'
    elif int(grade_score) in range(45, 61):
        return 'B2'
    elif int(grade_score) in range(30, 46):
        return 'C1'
    else:
        return 'C2'


def reading_time(words_count):
    return round(words_count / 265, 2)


def speaking_time(words_count):
    return round(words_count / 130, 2)


def compute_unique_word_count(data_list):
    unic_words = [item[0] for item in data_list if item[0] not in string.punctuation and item[1] == 1]
    return len(unic_words)


def syllables_in_word(word):
    if phoneme_dict.get(word.lower(), None):
        return len([ph for ph in phoneme_dict.get(word, []) if ph.strip(string.ascii_letters)])
    return 0


def words_sentence_syllables(data_list):
    words_12_letters = []
    words_4_syllables = []
    words_12_count = 0
    words_4_count = 0

    for sentence in data_list:
        for word in sentence.split():
            count4 = textstat.syllable_count(word)
            count12 = textstat.letter_count(word)
            if count12 > 12:
                words_12_count += 1
                words_12_letters.append((count12, word))
            if count4 > 4:
                words_4_count += 1
                words_4_syllables.append((count4, word))
    return words_12_letters, words_12_count, words_4_syllables, words_4_count


def count_sentences_syllables(data_list):
    sentences_30_syllables = []
    sentences_20_syllables = []
    sentences_30_count = 0
    sentences_20_count = 0

    for sentence in data_list:
        count = sum([textstat.syllable_count(word) for word in sentence.split()])
        if count > 30:
            sentences_30_count += 1
            sentences_30_syllables.append((sentences_30_count, sentence))
        if count > 20 and count < 30:
            sentences_20_count += 1
            sentences_20_syllables.append((sentences_20_count, sentence))
    return sentences_30_syllables, sentences_30_count, sentences_20_syllables, sentences_20_count


def count_raygor_readability(data_list):
    sentence_numbers = 0
    words_count_bigger_six = 0
    # computation
    words_count = 0
    for sentence in data_list:
        sentence_numbers = sentence_numbers + 1
        words_count = words_count + textstat.lexicon_count(sentence)
        words_count_bigger_six = words_count_bigger_six + len([1 for n in sentence.split() if len(n) > 6])
        if words_count >= 50:
            break

    # computation
    words_count = 0
    for sentence in reversed(data_list):
        sentence_numbers = sentence_numbers + 1
        words_count = words_count + textstat.lexicon_count(sentence)
        words_count_bigger_six = words_count_bigger_six + len([1 for n in sentence.split() if len(n) > 6])
        if words_count >= 50:
            break

    return get_value_from_raygor_graph(sentence_numbers, words_count_bigger_six)


def count_fry_readability(data_list):
    sentence_numbers = 0
    syllables_numbers = 0
    # computation
    words_count = 0
    for sentence in data_list:
        sentence_numbers = sentence_numbers + 1
        syllables_numbers = syllables_numbers + textstat.syllable_count(sentence)
        words_count = words_count + textstat.lexicon_count(sentence)
        if words_count >= 150:
            break

    # computation
    words_count = 0
    for sentence in reversed(data_list):
        sentence_numbers = sentence_numbers + 1
        syllables_numbers = syllables_numbers + textstat.syllable_count(sentence)
        words_count = words_count + textstat.lexicon_count(sentence)
        if words_count >= 150:
            break

    avg_sentence_numbers = round(sentence_numbers / 3)
    avg_syllables_numbers = round(syllables_numbers / 3)

    return get_value_from_fry_graph(avg_sentence_numbers, avg_syllables_numbers)


def find_limit_offcet(data_text: str, sentence_list: list, rule: str,
                      type_err: str, message: str, issueType: str) -> Optional[dict]:
    new_list_words = list()
    replacements = list()
    words_which_were_wound = dict()
    for key in sentence_list:
        if isinstance(key, tuple):
            value = key[1]
        else:
            value = key
        words_sentence = value.split()
        if len(words_sentence) > 1:
            list_limit_offset = [(m.start(), m.end()) for m in re.finditer(value, data_text)]
            for item in list_limit_offset:
                for word in words_sentence:

                    new_word = ''
                    for character in word:
                        if character not in ['.', ',', '"', ':', '(', ')']:  # string.punctuation:
                            new_word = new_word + character

                    for word_id in re.finditer(rf"\b({new_word})\b", data_text):
                        if word_id.start() >= item[0] and word_id.end(1) <= item[1]:
                            res = word_id.start()
                            new_dict_to_add = dict(sentence=word,
                                                   offset=res,
                                                   length=len(new_word),
                                                   message=message,
                                                   rule=dict(id=rule, issueType=issueType),
                                                   type=dict(typeName=type_err),
                                                   replacements=replacements)

                            if new_dict_to_add not in new_list_words:
                                words_which_were_wound[res] = new_dict_to_add

        else:
            list_limit_offset = [(m.start(), m.end()) for m in re.finditer(rf"\b({value})\b", data_text)]
            for item in list_limit_offset:
                new_dict_to_add = dict(sentence=value,
                                       offset=item[0],
                                       length=len(value),
                                       message=message,
                                       rule=dict(id=rule, issueType=issueType),
                                       type=dict(typeName=type_err),
                                       replacements=replacements)
                if new_dict_to_add not in new_list_words:
                    words_which_were_wound[item[0]] = new_dict_to_add

    for n in words_which_were_wound:
        new_list_words.append(words_which_were_wound[n])

    return new_list_words


def get_redability_assessments(data_text: str) -> Optional[dict]:
    divided_text = tokenize.sent_tokenize(data_text)
    word_tokenizes = nltk.word_tokenize(data_text)
    pos_tags = nltk.pos_tag(word_tokenizes)
    pos_tags_tagger = TAGGER.tag(word_tokenizes)
    f_dist = nltk.FreqDist(word_tokenizes)

    uniqueWordCount = compute_unique_word_count(f_dist.most_common())

    paragraphCount = max(len(data_text.split('\n')), len(data_text.split('\r\n')))

    counts = Counter(tag for word, tag in pos_tags)

    # Readability Grade Levels
    readability_grade_levels = dict(fleschKincaid=0, gunningFog=0, colemanLiau=0, smog=0,
                                    ari=0, forecastGradeLevel=0, powersSumnerKearlGrade=0, rix=0,
                                    raygorReadability=0, fryReadability=0, flesch=0)

    readability_grade_levels.update(fleschKincaid=textstat.flesch_kincaid_grade(data_text))
    readability_grade_levels.update(gunningFog=textstat.gunning_fog(data_text))
    readability_grade_levels.update(colemanLiau=textstat.coleman_liau_index(data_text))
    readability_grade_levels.update(smog=textstat.smog_index(data_text))
    readability_grade_levels.update(ari=textstat.automated_readability_index(data_text))
    readability_grade_levels.update(rix=textstat.rix(data_text))

    # need to check
    readability_grade_levels.update(forcastGradeLevel=round(20 - (textstat.avg_syllables_per_word(data_text) / 10), 2))

    readability_grade_levels.update(powersSumnerKearlGrade=round(textstat.avg_sentence_length(data_text) +
                                                                 textstat.avg_syllables_per_word(data_text) +
                                                                 2.7971, 2))
    readability_grade_levels.update(raygorReadability=count_raygor_readability(divided_text))
    readability_grade_levels.update(fryReadability=count_fry_readability(divided_text))
    # need to check

    readability_grade_levels.update(flesch=textstat.flesch_reading_ease(data_text))

    # Readability Scores
    readability_scores = dict(readableRating="", fleschReadingEase=0, cefrLevel='', ieltsLevel='', spacheScore=0,
                              newDaleChallScore=0, lixReadability=0, lensearWrite=0)
    readability_scores.update(readableRating=count_average_grade_levels(readability_grade_levels))
    readability_scores.update(fleschReadingEase=textstat.flesch_reading_ease(data_text))
    readability_scores.update(cefrLevel=count_cefr_levels(readability_grade_levels))
    readability_scores.update(ieltsLevel=count_ielts_levels(readability_grade_levels))
    readability_scores.update(spacheScore=round(textstat.spache_readability(data_text), 2))
    readability_scores.update(newDaleChallScore=textstat.dale_chall_readability_score_v2(data_text))
    readability_scores.update(lixReadability=textstat.lix(data_text))
    readability_scores.update(lensearWrite=textstat.linsear_write_formula(data_text))

    # Text Statistics
    text_statistics = dict(characterCount=0, syllableCount=0, wordCount=0, uniqueWordCount=0,
                           sentenceCount=0, paragraphCount=0)
    text_statistics.update(characterCount=textstat.char_count(data_text))
    text_statistics.update(syllableCount=textstat.syllable_count(data_text))
    text_statistics.update(wordCount=textstat.lexicon_count(data_text))
    text_statistics.update(uniqueWordCount=uniqueWordCount)
    text_statistics.update(sentenceCount=textstat.sentence_count(data_text))
    text_statistics.update(paragraphCount=paragraphCount)

    # Timings
    timings_statistics = dict(readingTime=0, speakingTime=0)
    timings_statistics.update(readingTime=reading_time(textstat.lexicon_count(data_text)))
    timings_statistics.update(speakingTime=speaking_time(textstat.lexicon_count(data_text)))

    # Text Composition
    text_composition = dict(adjectives=0, adverbs=0, conjunctions=0, determiners=0, interjections=0, nouns=0, verbs=0,
                            properNouns=0, prepositions=0, pronouns=0, qualifiers=0, unrecognised=0, nonWords=0)

    text_composition.update(adjectives=counts.get('JJ', 0) + counts.get('JJR', 0) + counts.get('JJS', 0))
    text_composition.update(adverbs=counts.get('RB', 0) + counts.get('RBR', 0) + counts.get('RBS', 0))
    text_composition.update(conjunctions=counts.get('CC', 0))
    text_composition.update(determiners=counts.get('DT', 0) + counts.get('PDT', 0) + counts.get('WDT', 0))
    text_composition.update(interjections=counts.get('UH', 0))
    text_composition.update(nouns=counts.get('NN', 0) + counts.get('NNS', 0))
    text_composition.update(
        verbs=counts.get('VB', 0) + counts.get('VBD', 0) + counts.get('VBG', 0) + counts.get('VBN', 0) + counts.get(
            'VBP', 0) + counts.get('VBZ', 0))
    text_composition.update(properNouns=counts.get('NNP', 0) + counts.get('NNPS', 0))
    text_composition.update(prepositions=counts.get('IN', 0))
    text_composition.update(
        pronouns=counts.get('PRP', 0) + counts.get('PRP$', 0) + counts.get('WP', 0) + counts.get('WP$', 0))
    text_composition.update(qualifiers=counts.get('RB', 0))
    text_composition.update(unrecognised=counts.get(None, 0))
    text_composition.update(nonWords=counts.get('.', 0) + counts.get(',', 0) + counts.get(':', 0))

    # Readability Issues
    text_readability_issues = dict(sentences30SyllablesCount=0, sentences20SyllablesCount=0,
                                   sentences30Syllables=[], sentences20Syllables=[],
                                   words4SyllablesCount=0, words12LettersCount=0,
                                   words4Syllables=[], words12Letters=[])

    sentences_30_syllables, sentences_30_count, sentences_20_syllables, sentences_20_count = count_sentences_syllables(
        divided_text)

    sentences_30_syllables = find_limit_offcet(data_text, sentences_30_syllables,
                                               "sentences_30_syllables",
                                               "sentences_30_syllables",
                                               "This sentence has more than 30 syllables. Consider rewriting it to be shorter or splitting it into smaller sentences.",
                                               "Readability Issues")
    sentences_20_syllables = find_limit_offcet(data_text, sentences_20_syllables,
                                               "sentences_20_syllables",
                                               "sentences_20_syllables",
                                               "This sentence has more than 20 syllables. Consider rewriting it to be shorter or splitting it into smaller sentences.",
                                               "Readability Issues")

    text_readability_issues.update(sentences30SyllablesCount=sentences_30_count,
                                   sentences20SyllablesCount=sentences_20_count)

    words_12_letters, words_12_count, words_4_syllables, words_4_count = words_sentence_syllables(divided_text)

    words_12_letters = find_limit_offcet(data_text, words_12_letters,
                                         "words_12_letters",
                                         "words_12_letters",
                                         "This word is more than 12 letters",
                                         "Readability Issues")
    words_4_syllables = find_limit_offcet(data_text, words_4_syllables,
                                          "words_4_syllables",
                                          "words_4_syllables",
                                          "This word is more than 4 syllables",
                                          "Readability Issues")

    text_readability_issues.update(words4SyllablesCount=words_4_count,
                                   words12LettersCount=words_12_count)

    # Writing Style Issues
    text_style_issues = dict(passiveVoiceCount=0, passiveVoices=[],
                             adverbsCount=0, adverbs=[],
                             clicheCount=0, cliches=[])
    passive_voises_return = find_passives(divided_text)
    passive_voises_return = find_limit_offcet(data_text, passive_voises_return,
                                              "passive_voises",
                                              "passive_voises",
                                              "Too much of using passive voises",
                                              "Writing Style Issues")
    adverbs_return = find_adverbs(pos_tags_tagger)
    adverbs_return = find_limit_offcet(data_text, adverbs_return,
                                       "adverbs",  # writing_style_issues
                                       "adverbs",
                                       "Too much of using adverbs",
                                       "Writing Style Issues")
    text_style_issues.update(passiveVoiceCount=len(passive_voises_return),
                             adverbsCount=len(adverbs_return))

    # Text Density Issues
    text_density_issues = dict(charactersPerWord=0, syllablesPerWord=0, wordsPerSentence=0,
                               wordsPerParagraph=0, sentencesPerParagraph=0)

    text_density_issues.update(charactersPerWord=textstat.avg_character_per_word(data_text),
                               syllablesPerWord=textstat.avg_syllables_per_word(data_text),
                               wordsPerSentence=round(textstat.lexicon_count(data_text) / len(divided_text), 2),
                               wordsPerParagraph=round(textstat.lexicon_count(data_text) / paragraphCount, 2),
                               sentencesPerParagraph=round(len(divided_text) / paragraphCount, 2))

    # Language Issues
    text_language_issues = dict(spellingIssuesCount=0, grammarIssueCount=0)

    matches_limit_offcet = sentences_20_syllables + sentences_30_syllables + words_4_syllables + words_12_letters + \
                           passive_voises_return + adverbs_return

    return dict(readabilityGradeLevels=readability_grade_levels,
                readabilityScores=readability_scores,
                textStatistics=text_statistics,
                timings=timings_statistics,
                textComposition=text_composition,
                textReadabilityIssues=text_readability_issues,
                textStyleIssues=text_style_issues,
                textDensityIssues=text_density_issues,
                textLanguageIssues=text_language_issues,
                matches=matches_limit_offcet)
