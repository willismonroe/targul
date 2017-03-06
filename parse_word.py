# Akkadian vowels and consonants
short_vowels = ['a', 'e', 'i', 'u']
macron_vowels = ['ā', 'ē', 'ī', 'ū']
circumflex_vowels = ['â', 'ê', 'î', 'û']

consonants = ['b', 'd', 'g', 'ḫ', 'k', 'l', 'm',
              'n', 'p', 'q', 'r', 's', 'ṣ', 'š',
              't', 'ṭ', 'w', 'y', 'z', 'ʾ']

vowels = short_vowels + macron_vowels + circumflex_vowels


def get_syllables(word):
    """
    Convert normalized word to a list of syllables.
    This function will not analyze stress.

    The general logic follows Huehnergard 3rd edition (pg. 3):
    (a) Every syllable has one, and only one, vowel.
    (b) With two exceptions, no syllable may begin with a vowel. The exceptions
    are: the beginning of a word; the second of two successive vowels (note:
    some scholars prefer to write ʾ between any two vowels in a word: e.g.,
    kiʾam rather than our kiam).
    (c) No syllable may begin or end with two consonants.
    :param word: a string in Akkadian
    :return: a list of syllables
    """
    syllables = []

    # If there's an initial vowel and the word is longer than 2 letters,
    # and the third syllable is a consonant (easy way to check for VCC pattern),
    # the initial vowel is the first syllable.
    # Rule (b.ii)
    if word[0] in vowels:
        if len(word) > 2 and word[2] not in consonants:
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
        if char in vowels:
            syllables_reverse.append(word[i + 1] + word[i])
            i += 2

        # CVC and VC:
        elif char in consonants:
            if word[i + 1] in vowels:
                # If there are only two syllables left, that's it.
                if i + 2 >= len(word):
                    syllables_reverse.append(word[i + 1] + word[i])
                    break
                # CVC
                elif word[i + 2] in consonants:
                    syllables_reverse.append(word[i + 2] + word[i + 1] + word[i])
                    i += 3
                # VC (remember it's backwards here)
                elif word[i + 2] in vowels:
                    syllables_reverse.append(word[i + 1] + word[i])
                    i += 2

    return syllables + syllables_reverse[::-1]


def find_stress(word):
    """
    Find the stressed syllable in a word.

    The general logic follows Huehnergard 3rd edition (pgs. 3-4):
    (a) Light: ending in a short vowel: e.g., -a, -ba
    (b) Heavy: ending in a long vowel marked with a macron, or in a
    short vowel plus a consonant: e.g., -ā, -bā, -ak, -bak
    (c) Ultraheavy: ending in a long vowel marked with a circumflex,
    in any long vowel plus a consonant: e.g., -â, -bâ, -āk, -bāk, -âk, -bâk.

    (a) If the last syllable is ultraheavy, it bears the stress.
    (b) Otherwise, stress falls on the last non-final heavy or ultraheavy syllable.
    (c) Words that contain no non-final heavy or ultraheavy syllables have the
    stress fall on the first syllable.

    :param word: a string (or list) in Akkadian
    :return: a list of syllables with stressed syllable surrounded by "[]"
    """
    if type(word) is str:
        word = get_syllables(word)

    syllables_stress = []
    for i, syllable in enumerate(word):
        # Enumerate over the syllables and mark them for length
        # We check each type of length by looking at the length of the
        # syllable and verifying rules based on character length.

        # Ultraheavy:
        # -â, -bâ, -āk, -bāk, -âk, -bâk.
        if len(syllable) == 1:
            if syllable in circumflex_vowels:
                syllables_stress.append((syllable, "Ultraheavy"))
                continue
        elif len(syllable) == 2:
            if syllable[0] in consonants and syllable[1] in circumflex_vowels:
                syllables_stress.append((syllable, "Ultraheavy"))
                continue
            if syllable[0] in macron_vowels + circumflex_vowels and syllable[1] in consonants:
                syllables_stress.append((syllable, "Ultraheavy"))
                continue
        elif len(syllable) == 3:
            if syllable[1] in macron_vowels + circumflex_vowels:
                syllables_stress.append((syllable, "Ultraheavy"))
                continue

        # Heavy:
        # -ā, -bā, -ak, -bak
        if len(syllable) == 1:
            if syllable in macron_vowels:
                syllables_stress.append((syllable, "Heavy"))
                continue
        elif len(syllable) == 2:
            if syllable[0] in consonants and syllable[1] in macron_vowels:
                syllables_stress.append((syllable, "Heavy"))
                continue
            if syllable[0] in short_vowels and syllable[1] in consonants:
                syllables_stress.append((syllable, "Heavy"))
                continue
        elif len(syllable) == 3:
            if syllable[1] in short_vowels:
                syllables_stress.append((syllable, "Heavy"))
                continue

        # Light:
        # -a, -ba
        if len(syllable) == 1:
            if syllable in short_vowels:
                syllables_stress.append((syllable, "Light"))
                continue
        elif len(syllable) == 2:
            if syllable[0] in consonants and syllable[1] in short_vowels:
                syllables_stress.append((syllable, "Light"))
                continue

    # It's easier to find stress backwards
    syllables_stress = syllables_stress[::-1]

    syllables = []
    found_stress = 0
    for i, syllable in enumerate(syllables_stress):
        # If we've found the stressed syllable just append the next syllable
        if found_stress:
            syllables.append(syllable[0])
            continue

        # Rule (a)
        elif syllable[1] == "Ultraheavy" and i == 0:
            syllables.append("[{}]".format(syllable[0]))
            found_stress = 1
            continue

        # Rule (b)
        elif syllable[1] in ['Ultraheavy', 'Heavy'] and i > 0:
            syllables.append("[{}]".format(syllable[0]))
            found_stress = 1
            continue

        # Final 'Heavy' syllable, gets no stress
        elif syllable[1] == 'Heavy' and i == 0:
            syllables.append(syllable[0])
            continue

        # Light syllable gets no stress
        elif syllable[1] == "Light":
            syllables.append(syllable[0])
            continue

    # Reverse the list again
    syllables = syllables[::-1]

    # If we still haven't found stress then rule (c) applies
    # Rule (c)
    if not found_stress:
        syllables[0] = "[{}]".format(syllables[0])

    return syllables


def test_syllabification():
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

    # The syllabification rules fail on this example from the stress rules
    print(get_syllables('ibnû') == ['ib', 'nû'])


def test_stress():
    print(find_stress('ibnû') == ['ib', '[nû]'])
    print(find_stress('idūk') == ['i', '[dūk]'])
    print(find_stress('iparras') == ['i', '[par]', 'ras'])
    print(find_stress('nidittum') == ['ni', '[dit]', 'tum'])
    print(find_stress('idūkū') == ['i', '[dū]', 'kū'])
    print(find_stress('tēteneppušā') == ['tē', 'te', '[nep]', 'pu', 'šā'])
    print(find_stress('itâršum') == ['i', '[târ]', 'šum'])
    print(find_stress('napištašunu') == ['na', '[piš]', 'ta', 'šu', 'nu'])
    print(find_stress('zikarum') == ['[zi]', 'ka', 'rum'])
    print(find_stress('šunu') == ['[šu]', 'nu'])
    print(find_stress('ilū') == ['[i]', 'lū'])
