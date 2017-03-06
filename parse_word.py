# Akkadian vowels and consonants
vowels = ['a', 'e', 'i', 'u']
consonants = ['b', 'd', 'g', 'ḫ', 'k', 'l', 'm',
              'n', 'p', 'q', 'r', 's', 'ṣ', 'š',
              't', 'ṭ', 'w', 'y', 'z', 'ʾ']

vowels_with_length = ['ā', 'ē', 'ī', 'ū', 'â', 'ê', 'î', 'û']

vowels = vowels + vowels_with_length


def get_syllables(word):
    """
    Convert normalized word to a list of syllables.
    This function will not analyze stress.

    The general logic follows Huehnergard 3rd edition:
    (a) Every syllable has one, and only one, vowel.
    (b) With two exceptions, no syllable may begin with a vowel. The exceptions
    are: the beginning of a word; the second of two successive vowels (note:
    some scholars prefer to write ʾ between any two vowels in a word: e.g.,
    kiʾam rather than our kiam).
    (c) No syllable may begin or end with two consonants.
    """
    syllables = []

    # Rule (b.ii)
    if word[0] in vowels:
        syllables.append(word[0])
        word = word[1:]

    # flip the word and count from the back:
    word = word[::-1]
    syllables_reverse = []
    i = 0
    while i < len(word):
        char = word[i]

        # CV:
        # "iṭ" -> "ṭi"
        if char in vowels:
            syllables_reverse.append(word[i + 1] + word[i])
            i += 2

        # CVC and VC:
        # "mul" -> "lum"
        # "ma" -> "am"
        elif char in consonants:
            if word[i + 1] in vowels:
                if word[i + 2] in consonants:
                    syllables_reverse.append(word[i + 2] + word[i + 1] + word[i])
                    i += 3
                elif word[i + 2] in vowels:
                    syllables_reverse.append(word[i + 1] + word[i])
                    i += 2

    return syllables + syllables_reverse[::-1]


def test():
    # small test suite
    # TODO: move this out to a real test system
    print(get_syllables('balāṭī') == ['ba', 'lā', 'ṭī'])
    print(get_syllables('elûm') == ['e', 'lûm'])
    print(get_syllables('ṣabat') == ['ṣa', 'bat'])
    print(get_syllables('īteneppuš') == ['ī', 'te', 'nep', 'puš'])
    print(get_syllables('narkabtum') == ['nar', 'kab', 'tum'])
    print(get_syllables('epištašu') == ['e', 'piš', 'ta', 'šu'])
    print(get_syllables('kiam') == ['ki', 'am'])
    print(get_syllables('kiʾam') == ['ki', 'ʾam'])
