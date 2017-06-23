from collections import OrderedDict

AKKADIAN = {
    'short_vowels': ['a', 'e', 'i', 'u'],
    'macron_vowels': ['ā', 'ē', 'ī', 'ū'],
    'circumflex_vowels': ['â', 'ê', 'î', 'û'],

    'consonants': ['b', 'd', 'g', 'ḫ', 'k', 'l', 'm',
                   'n', 'p', 'q', 'r', 's', 'ṣ', 'š',
                   't', 'ṭ', 'w', 'y', 'z', 'ʾ']
}

ENDINGS = {
    'm': {
        'singular': {
            'nominative': 'um',
            'accusative': 'am',
            'genitive': 'im'
        },
        'dual': {
            'nominative': 'ān',
            'oblique': 'īn'
        },
        'plural': {
            'nominative': 'ū',
            'oblique': 'ī'
        }
    },
    'f': {
        'singular': {
            'nominative': 'tum',
            'accusative': 'tam',
            'genitive': 'tim'
        },
        'dual': {
            'nominative': 'tān',
            'oblique': 'tīn'
        },
        'plural': {
            'nominative': ['ātum', 'ētum', 'ītum'],
            'oblique': ['ātim', 'ētim', 'ītum']
        }
    }
}


class Syllabifier(object):
    """Split Akkadian words into list of syllables"""

    def __init__(self, language=AKKADIAN):
        self.language = language

    def _is_consonant(self, char):
        return char in self.language['consonants']

    def _is_vowel(self, char):
        return char in self.language['short_vowels'] + \
                       self.language['macron_vowels'] + \
                       self.language['circumflex_vowels']

    def syllabify(self, word):
        syllables = []

        # If there's an initial vowel and the word is longer than 2 letters,
        # and the third syllable is a not consonant (easy way to check for VCC pattern),
        # the initial vowel is the first syllable.
        # Rule (b.ii)
        if self._is_vowel(word[0]):
            if len(word) > 2 and not self._is_consonant(word[2]):
                syllables.append(word[0])
                word = word[1:]

        # flip the word and count from the back:
        word = word[::-1]

        # Here we iterate over the characters backwards trying to match
        # consonant and vowel patterns in a hierarchical way.
        # Each time we find a match we store the syllable (in reverse order)
        # and move the index ahead the length of the syllable.
        syllables_reverse = []
        i = 0
        while i < len(word):
            char = word[i]

            # CV:
            if self._is_vowel(char):
                syllables_reverse.append(word[i + 1] + word[i])
                i += 2

            # CVC and VC:
            elif self._is_consonant(char):
                if self._is_vowel(word[i + 1]):
                    # If there are only two characters left, that's it.
                    if i + 2 >= len(word):
                        syllables_reverse.append(word[i + 1] + word[i])
                        break
                    # CVC
                    elif self._is_consonant(word[i + 2]):
                        syllables_reverse.append(word[i + 2] + word[i + 1] + word[i])
                        i += 3
                    # VC (remember it's backwards here)
                    elif self._is_vowel(word[i + 2]):
                        syllables_reverse.append(word[i + 1] + word[i])
                        i += 2

        return syllables + syllables_reverse[::-1]


syll = Syllabifier()


def get_cv_pattern(word, pprint=False):
    # input = iparras
    # pattern = [('V', 1, 'i'), ('C', 1, 'p'), ('V', 2, 'a'), ('C', 2, 'r'),
    #           ('C', 2, 'r'), ('V', 2, 'a'), ('C', 3, 's')]
    # pprint = V₁C₁V₂C₂C₂V₂C₃
    subscripts = {
        1: '₁',
        2: '₂',
        3: '₃',
        4: '₄',
        5: '₅',
        6: '₆',
        7: '₇',
        8: '₈',
        9: '₉',
        0: '₀'
    }
    pattern = []
    c_count = 1
    v_count = 1
    for char in word:
        if char in AKKADIAN['consonants']:
            cv = 'C'
        else:
            cv = 'V'
            # remove length:
            if char in AKKADIAN['macron_vowels']:
                char = AKKADIAN['short_vowels'][AKKADIAN['macron_vowels'].index(char)]
            elif char in AKKADIAN['circumflex_vowels']:
                char = AKKADIAN['short_vowels'][AKKADIAN['circumflex_vowels'].index(char)]
        if char not in [x[2] for x in pattern]:
            if cv == 'C':
                count = c_count
                c_count += 1
            elif cv == 'V':
                count = v_count
                v_count += 1
            pattern.append((cv, count, char))
        elif char in [x[2] for x in pattern]:
            pattern.append((cv, next(x[1] for x in pattern if x[2] == char), char))
    if pprint:
        output = ''
        for item in pattern:
            output += (item[0] + subscripts[item[1]])
        return output
    return pattern


def get_stem(noun, gender, mimation=True):
    stem = ''
    if mimation and noun[-1:] == 'm':
        # noun = noun[:-1]
        pass
    # Take off ending
    if gender == 'm':
        if noun[-2:] in list(ENDINGS['m']['singular'].values()) + \
                list(ENDINGS['m']['dual'].values()):
            stem = noun[:-2]
        elif noun[-1] in list(ENDINGS['m']['plural'].values()):
            stem = noun[:-1]
        else:
            print("Unknown masculine noun: {}".format(noun))
    elif gender == 'f':
        if noun[-4:] in ENDINGS['f']['plural']['nominative'] + \
                ENDINGS['f']['plural']['oblique']:
            stem = noun[:-4] + 't'
        elif noun[-3:] in list(ENDINGS['f']['singular'].values()) + \
                list(ENDINGS['f']['dual'].values()):
            stem = noun[:-3] + 't'
        elif noun[-2:] in list(ENDINGS['m']['singular'].values()) + \
                list(ENDINGS['m']['dual'].values()):
            stem = noun[:-2]
        else:
            print("Unknown feminine noun: {}".format(noun))
    else:
        print("Unknown noun: {}".format(noun))
    return stem


def get_bound_form(noun, gender):
    stem = get_stem(noun, gender)
    cv = get_cv_pattern(stem)
    if [x[0] for x in cv[-2:]] == ['V', 'C']:
        # Rule 1
        syllables = syll.syllabify(noun)
        if len(syllables) > 2:
            # awīlum > awīl, nakrum > naker
            pass
        elif len(syllables) > 1:
            # bēlum > bēl
            pass
        if stem in ['ab', 'aḫ']:
            return stem + 'i'


def decline_noun(noun, gender, case=None, number=None, mimation=True):
    stem = get_stem(noun, gender)
    declension = []
    for case in ENDINGS[gender]['singular']:
        if gender == 'm':
            form = stem + ENDINGS[gender]['singular'][case]
        else:
            form = stem + ENDINGS[gender]['singular'][case][1:]
        declension.append((form, {'case': case, 'number': 'singular'}))
    for case in ENDINGS[gender]['dual']:
        if gender == 'm':
            form = stem + ENDINGS[gender]['dual'][case]
        else:
            form = stem + ENDINGS[gender]['dual'][case][1:]
        declension.append((form, {'case': case, 'number': 'dual'}))
    for case in ENDINGS[gender]['plural']:
        if gender == 'm':
            form = stem + ENDINGS[gender]['plural'][case]
        else:
            if stem[-3] in AKKADIAN['macron_vowels']:
                theme_vowel = stem[-3]
            else:
                theme_vowel = 'ā'
            ending = [x for x in ENDINGS[gender]['plural'][case] if x[0] == theme_vowel]
            if stem[-2] in AKKADIAN['short_vowels']:
                form = stem[:-2] + ending[0]
            elif stem[-1] in AKKADIAN['consonants'] and stem[-2] in AKKADIAN['macron_vowels']:
                form = stem + ending[0]
            else:
                form = stem[:-1] + ending[0]
        declension.append((form, {'case': case, 'number': 'plural'}))
    return declension


def test_get_stem():
    print(get_stem('ilum', 'm') == 'il')
    print(get_stem('šarrū', 'm') == 'šarr')
    print(get_stem('ilātum', 'f') == 'ilt')
    print(get_stem('bēltān', 'f') == 'bēlt')


def test_decline_noun():
    print(sorted(decline_noun('ilum', 'm')) ==
          sorted([('ilim', {'case': 'genitive', 'number': 'singular'}),
                  ('ilum', {'case': 'nominative', 'number': 'singular'}),
                  ('ilam', {'case': 'accusative', 'number': 'singular'}),
                  ('ilīn', {'case': 'oblique', 'number': 'dual'}),
                  ('ilān', {'case': 'nominative', 'number': 'dual'}),
                  ('ilī', {'case': 'oblique', 'number': 'plural'}),
                  ('ilū', {'case': 'nominative', 'number': 'plural'})]))

    print(sorted(decline_noun('šarrum', 'm')) ==
          sorted([('šarrim', {'case': 'genitive', 'number': 'singular'}),
                  ('šarrum', {'case': 'nominative', 'number': 'singular'}),
                  ('šarram', {'case': 'accusative', 'number': 'singular'}),
                  ('šarrīn', {'case': 'oblique', 'number': 'dual'}),
                  ('šarrān', {'case': 'nominative', 'number': 'dual'}),
                  ('šarrī', {'case': 'oblique', 'number': 'plural'}),
                  ('šarrū', {'case': 'nominative', 'number': 'plural'})]))

    print(sorted(decline_noun('iltum', 'f')) ==
          sorted([('iltim', {'case': 'genitive', 'number': 'singular'}),
                  ('iltum', {'case': 'nominative', 'number': 'singular'}),
                  ('iltam', {'case': 'accusative', 'number': 'singular'}),
                  ('iltīn', {'case': 'oblique', 'number': 'dual'}),
                  ('iltān', {'case': 'nominative', 'number': 'dual'}),
                  ('ilātim', {'case': 'oblique', 'number': 'plural'}),
                  ('ilātum', {'case': 'nominative', 'number': 'plural'})]))

    print(sorted(decline_noun('šarratum', 'f')) ==
          sorted([('šarratim', {'case': 'genitive', 'number': 'singular'}),
                  ('šarratum', {'case': 'nominative', 'number': 'singular'}),
                  ('šarratam', {'case': 'accusative', 'number': 'singular'}),
                  ('šarratīn', {'case': 'oblique', 'number': 'dual'}),
                  ('šarratān', {'case': 'nominative', 'number': 'dual'}),
                  ('šarrātim', {'case': 'oblique', 'number': 'plural'}),
                  ('šarrātum', {'case': 'nominative', 'number': 'plural'})]))

    print(sorted(decline_noun('nārum', 'f')) ==
          sorted([('nārim', {'case': 'genitive', 'number': 'singular'}),
                  ('nārum', {'case': 'nominative', 'number': 'singular'}),
                  ('nāram', {'case': 'accusative', 'number': 'singular'}),
                  ('nārīn', {'case': 'oblique', 'number': 'dual'}),
                  ('nārān', {'case': 'nominative', 'number': 'dual'}),
                  ('nārātim', {'case': 'oblique', 'number': 'plural'}),
                  ('nārātum', {'case': 'nominative', 'number': 'plural'})]
                 ))
