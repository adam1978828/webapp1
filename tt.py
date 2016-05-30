# # -*- coding: utf-8 -*-
# __author__ = 'D.Ivanets'
#
# def countLines(name):
#     return len(open(name, 'r').readlines())
#
#
# def countChars(name):
#     return len(open(name, 'r').read())
#
# def testFile(name):
#     return countLines(name), countChars(name)
#
#
# if __name__ == '__main__':
#     pass

VOWELS = "AEIOUY"
CONSONANTS = "BCDFGHJKLMNPQRSTVWXZ"


def striped_words(text):
    text = text.replace(',', ' ')
    text = text.replace('.', ' ')
    text = text.replace('?', ' ')
    text = text.upper()
    res = 0
    for word in text.split():
        if len(word) <= 1:
            continue
        last = word[0]
        for letter in word[1:]:
            if last in VOWELS and letter in VOWELS:
                break
            if last in CONSONANTS and letter in CONSONANTS:
                break
            if last not in CONSONANTS + VOWELS:
                break
            if letter not in CONSONANTS + VOWELS:
                break
            last = letter
        else:
            res += 1
    return res


if __name__ == '__main__':
    # These "asserts" using only for self-checking and not necessary for auto-testing
    assert striped_words("My name is ...") == 3, "All words are striped"
    assert striped_words("Hello world") == 0, "No one"
    assert striped_words("A quantity of striped words.") == 1, "Only of"
    assert striped_words("Dog,cat,mouse,bird.Human.") == 3, "Dog, cat and human"
    assert striped_words("To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it?")