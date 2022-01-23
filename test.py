from unittest import TestCase
from solver import Solver, LettersHotness, WordHotness
from util import a2i, dict2arr


class SolverTest(TestCase):

    number_of_letters = 5
    fixture = Solver('data/words_dictionary.json', number_of_letters)

    def test_hotness_of_invalid_word(self):
        with self.assertRaises(AssertionError) as context:
            self.fixture.hotness("adfaf", "point")

    def test_hotness_of_invalid_target(self):
        with self.assertRaises(AssertionError) as context:
            self.fixture.hotness("point", "adafd")

    def test_valid(self):
        self.assertFalse(self.fixture.is_valid_word("adfaf"))

    def test_hotness_of_correct_word(self):
        self.assertEqual(self.fixture.hotness("point", "point").hotness, list(range(1,6)))

    def test_hotness_of_word_with_all_wrong_letters(self):
        self.assertEqual(self.fixture.hotness("bread", "point").hotness, [-1]*self.number_of_letters)

    def test_hotness_of_word_with_only_correct_or_wrong_letters(self):
        self.assertEqual(self.fixture.hotness("boils", "point").hotness, [-1,2,3,-1,-1])

    def test_hotness_of_word_with_both_correct_and_wrong_and_close_letters(self):
        self.assertEqual(self.fixture.hotness("nails", "point").hotness, [0,-1,3,-1,-1])

    def test_is_valid_by_hotness(self):
        hotness = {'a': 1, 'b': 0, 'c': 1, 'e': 1, 'i': -1}
        letters_hotness = LettersHotness(hotness)

        self.assertTrue(self.fixture.is_valid_by_hotness("brace", letters_hotness))
        self.assertFalse(self.fixture.is_valid_by_hotness("slice", letters_hotness))

    def test_valid_words_from_hotness(self):
        hotness = LettersHotness({'a': 0, 'b': 1, 'r': 1, 'e': 0, 'd': 1, 'i': -1, 'o': -1})

        valid_words = self.fixture.all_valid_words_from_hotness(hotness)

        self.assertTrue('bread' in valid_words)

    def test_letters_hotness(self):
        letter_hotness = LettersHotness({'a': 1, 'b': -1, 'c': 0})

        actual = letter_hotness.hotness
        expected = [[] for _ in range(26)]
        expected[0] = [1]
        expected[1] = [-1]
        expected[2] = [0]

        self.assertEqual(actual, expected)

    def test_update_letters_hotness(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [-1, 0, 3, -1, 5])
        letter_hotness.update_word(word, word_hotness, word)

        actual = letter_hotness.hotness
        expected = [[] for _ in range(26)]
        expected[a2i('p')].append(-1)
        expected[a2i('a')].append(0)
        expected[a2i('i')].append(3)
        expected[a2i('n')].append(-1)
        expected[a2i('t')].append(5)

        self.assertEqual(actual, expected)

    def test_update_letters_hotness_with_repeated_letters(self):
        word = 'leeks'
        letter_hotness = LettersHotness({'e': 3, 'l': 4})
        word_hotness = WordHotness(word, [0, 2, 3, -1, 5])
        letter_hotness.update_word(word, word_hotness, 'feels')

        actual = letter_hotness.hotness
        expected = [[] for _ in range(26)]
        expected[a2i('e')] = [2, 3]
        expected[a2i('l')] = [4]
        expected[a2i('k')] = [-1]
        expected[a2i('s')] = [5]

        self.assertEqual(actual, expected)

    def test_update_letters_hotness_with_repeated_letters_2(self):
        word = 'leeks'
        letter_hotness = LettersHotness({'e': 3, 'l': 4})
        word_hotness = WordHotness(word, [0, 0, 3, -1, 5])
        letter_hotness.update_word(word, word_hotness, word)

        actual = letter_hotness.hotness
        expected = [[] for _ in range(26)]
        expected[a2i('e')] = [0, 3]
        expected[a2i('l')] = [4]
        expected[a2i('k')] = [-1]
        expected[a2i('s')] = [5]

        self.assertEqual(actual, expected)

    def test_update_letters_hotness_with_repeated_letters_3(self):
        word = 'again'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [-1, 0, -1, -1, 5])
        letter_hotness.update_word(word, word_hotness, word)

        actual = letter_hotness.hotness
        expected = [[] for _ in range(26)]
        expected[a2i('a')] = [-1]
        expected[a2i('g')] = [0]
        expected[a2i('i')] = [-1]
        expected[a2i('n')] = [5]

        self.assertEqual(actual, expected)

    def test_score_word_by_letters_closeness(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [1, 2, 3, 4, 5])
        letter_hotness.update_word(word, word_hotness, word)

        self.assertEqual(self.fixture.score_word(word, letter_hotness), self.fixture.hotness_weights[1]*len(word))

    def test_score_word_by_letters_closeness_2(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [-1, -1, 0, 4, 5])
        letter_hotness.update_word(word, word_hotness, word)

        another_word = 'flint'
        expected = self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[0] + \
                   self.fixture.hotness_weights[4] + \
                   self.fixture.hotness_weights[5]

        self.assertEqual(self.fixture.score_word(another_word, letter_hotness), expected)

    def test_score_word_by_letters_closeness_3(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [-1, -1, 3, 4, -1])
        letter_hotness.update_word(word, word_hotness, word)

        another_word = 'cling'
        expected = self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[3] + \
                   self.fixture.hotness_weights[4] + \
                   self.fixture.hotness_weights[None]

        self.assertEqual(self.fixture.score_word(another_word, letter_hotness), expected)

    def test_score_word_by_letters_closeness_4(self):
        letter_hotness = LettersHotness({'a': -1, 'l': 0, 'o': 2, 'r': -1, 's': 0, 't': 1, 'y': -1})

        guess = 'tools'
        expected = self.fixture.hotness_weights[1] + \
                   self.fixture.hotness_weights[2] + \
                   0 + \
                   self.fixture.hotness_weights[0] + \
                   self.fixture.hotness_weights[0]

        self.assertEqual(self.fixture.score_word(guess, letter_hotness), expected)

    def test_score_word_by_letters_closeness_when_word_does_not_use_all_letters(self):
        letter_hotness = LettersHotness({'a': 0, 'o': 2, 'r': -1, 's': 0, 't': 1, 'y': -1})

        guess = 'toons'
        expected = float('-inf')
        self.assertEqual(self.fixture.score_word(guess, letter_hotness), expected)

    def test_score_word_by_letters_closeness_when_word_has_repeated_letters_at_wrong_position(self):
        letter_hotness = LettersHotness({'a': [0,0]})

        guess = 'almug'
        expected = float('-inf')
        self.assertEqual(self.fixture.score_word(guess, letter_hotness), expected)