from unittest import TestCase
from solver import Solver, LettersHotness, WordHotness


class SolverTest(TestCase):

    number_of_letters = 5
    fixture = Solver('data/words_dictionary.json', number_of_letters)

    def _testLettersHotness(self, expected, actual):
        self.assertEqual(expected.hotness, actual.hotness)
        self.assertEqual(expected.freq, actual.freq)

    def test_hotness_of_invalid_word(self):
        with self.assertRaises(AssertionError) as context:
            self.fixture.hotness("adfaf", "point")

    def test_hotness_of_invalid_target(self):
        with self.assertRaises(AssertionError) as context:
            self.fixture.hotness("point", "adafd")

    def test_valid(self):
        self.assertFalse(self.fixture.is_valid_word("adfaf"))

    def test_hotness_of_correct_word(self):
        self.assertEqual([1,2,3,4,5], self.fixture.hotness("point", "point").hotness)

    def test_hotness_of_word_with_all_wrong_letters(self):
        self.assertEqual([0,0,0,0,0], self.fixture.hotness("bread", "point").hotness)

    def test_hotness_of_word_with_both_correct_and_wrong_and_close_letters(self):
        self.assertEqual([0,2,3,0,0], self.fixture.hotness("boils", "point").hotness)

    def test_hotness_of_word_with_only_correct_or_wrong_letters(self):
        self.assertEqual([-1,0,3,0,0], self.fixture.hotness("nails", "point").hotness)

    def test_is_valid_by_hotness(self):
        letters_hotness = LettersHotness(
            {'a': [3], 'b': [-2], 'c': [4], 'e': [5], 'i': [0]},
            {'a': 1, 'b': 1, 'c': 1, 'e': 1, 'i': 1},
        )

        self.assertTrue(self.fixture.is_valid_by_hotness("brace", letters_hotness))
        self.assertFalse(self.fixture.is_valid_by_hotness("slice", letters_hotness))

    def test_valid_words_from_hotness(self):
        hotness = LettersHotness(
            {'a': [-3], 'b': [1], 'r': [2], 'e': [-4], 'd': [5], 'i': [0], 'o': [0]},
            {'a': 1, 'b': 1, 'r': 1, 'e': 1, 'd': 1, 'i': 1, 'o': 1},
        )

        valid_words = self.fixture.all_valid_words_from_hotness(hotness)

        self.assertTrue('bread' in valid_words)

    def test_letters_hotness(self):
        letter_hotness = LettersHotness(
            {'a': [1], 'b': [-2], 'c': [0]},
            {'a': 1, 'b': 1, 'c': 0},
        )

        actual = letter_hotness
        expected = LettersHotness(
            {
                'a': [1],
                'b': [-2],
                'c': [0],
            },
            {
                'a': 1,
                'b': 1,
                'c': 0,
            }
        )

        self._testLettersHotness(expected, actual)

    def test_update_letters_hotness(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [0, -2, 3, 0, 5])
        letter_hotness.update_word(word, word_hotness)

        actual = letter_hotness
        expected = LettersHotness(
            {
                'p': [0],
                'a': [-2],
                'i': [3],
                'n': [0],
                't': [5],
            },
            {
                'p': 0,
                'a': 1,
                'i': 1,
                'n': 0,
                't': 1,
            }
        )

        self._testLettersHotness(expected, actual)

    def test_update_letters_hotness_multiple_times(self):
        word = 'rinse'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [-1, 0, -3, 0, 0])
        letter_hotness.update_word(word, word_hotness)
        letter_hotness_after_one_update = letter_hotness.copy()
        letter_hotness_after_one_update.update_word(word, word_hotness)

        self._testLettersHotness(letter_hotness_after_one_update, letter_hotness)

    def test_update_letters_hotness_with_repeated_letters(self):
        word = 'leeks'
        letter_hotness = LettersHotness({'e': [3], 'l': [4]}, {'e': 1, 'l': 4})
        word_hotness = WordHotness(word, [-1, 2, 3, 0, 5])
        letter_hotness.update_word(word, word_hotness)

        actual = letter_hotness
        expected = LettersHotness(
            {
                'l': [-1, 4],
                'e': [2, 3],
                'k': [0],
                's': [5],
            },
            {
                'l': 1,
                'e': 2,
                'k': 0,
                's': 1,
            }
        )
        self._testLettersHotness(expected, actual)

    def test_update_letters_hotness_with_repeated_letters_2(self):
        word = 'leeks'
        letter_hotness = LettersHotness({'e': 3, 'l': 4})
        word_hotness = WordHotness(word, [-1, -2, 3, 0, 5])
        letter_hotness.update_word(word, word_hotness)

        actual = letter_hotness
        expected = LettersHotness(
            {
                'l': [-1, 4],
                'e': [-2, 3],
                'k': [0],
                's': [5],
            },
            {
                'l': 1,
                'e': 2,
                'k': 0,
                's': 1,
            }
        )

        self._testLettersHotness(expected, actual)

    def test_update_letters_hotness_with_repeated_letters_3(self):
        word = 'again'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [0, -2, 0, 0, 5])
        letter_hotness.update_word(word, word_hotness)

        actual = letter_hotness
        expected = LettersHotness(
            {
                'a': [0],
                'g': [-2],
                'i': [0],
                'n': [5],
            },
            {
                'a': 0,
                'g': 1,
                'i': 0,
                'n': 1,
            }
        )

        self._testLettersHotness(expected, actual)

    def test_update_letters_hotness_with_letters_in_multiple_wrong_locations(self):
        word = 'again'
        letter_hotness = LettersHotness({'g': [-1]}, {'g': 1})
        word_hotness = WordHotness(word, [0, -2, 0, 0, 5])
        letter_hotness.update_word(word, word_hotness)

        actual = letter_hotness
        expected = LettersHotness(
            {
                'a': [0],
                'g': [-2, -1],
                'i': [0],
                'n': [5],
            },
            {
                'a': 0,
                'g': 1,
                'i': 0,
                'n': 1,
            }
        )

        self._testLettersHotness(expected, actual)

    def test_update_sequence_of_letters_hotness(self):
        letter_hotness = LettersHotness()
        letter_hotness.update_word('rinse', WordHotness('rinse', [-1, 0, 0, 0, 0]))
        letter_hotness.update_word('today', WordHotness('today', [ 0,-2, 0,-4, 0]))
        letter_hotness.update_word('arrow', WordHotness('arrow', [-1,-2, 0, 4, 0]))

        actual = letter_hotness
        expected = LettersHotness(
            {
                'r': [-3, -2, -1],
                'i': [0],
                'n': [0],
                's': [0],
                'e': [0],
                't': [0],
                'o': [-2, 4],
                'd': [0],
                'a': [-4, -1],
                'y': [0],
                'w': [0],
            },
            {
                'r': 1,
                'i': 0,
                'n': 0,
                's': 0,
                'e': 0,
                't': 0,
                'o': 1,
                'd': 0,
                'a': 1,
                'y': 0,
                'w': 0,
            }
        )

        self._testLettersHotness(expected, actual)

    def test_score_word_by_letters_closeness(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [1, 2, 3, 4, 5])
        letter_hotness.update_word(word, word_hotness)

        self.assertEqual(self.fixture.score_word(word, letter_hotness), self.fixture.hotness_weights[1]*len(word))

    def test_score_word_by_letters_closeness_2(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [0, 0, -3, 4, 5])
        letter_hotness.update_word(word, word_hotness)

        another_word = 'flint'
        expected = self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[0] + \
                   self.fixture.hotness_weights[4] + \
                   self.fixture.hotness_weights[5]

        self.assertEqual(expected, self.fixture.score_word(another_word, letter_hotness))

    def test_score_word_by_letters_closeness_3(self):
        word = 'paint'
        letter_hotness = LettersHotness()
        word_hotness = WordHotness(word, [0, 0, 3, 4, 0])
        letter_hotness.update_word(word, word_hotness)

        another_word = 'cling'
        expected = self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[3] + \
                   self.fixture.hotness_weights[4] + \
                   self.fixture.hotness_weights[None]

        self.assertEqual(expected, self.fixture.score_word(another_word, letter_hotness))

    def test_score_word_by_letters_closeness_4(self):
        letter_hotness = LettersHotness(
            {'a': [0], 'l': [-2], 'o': [2], 'r': [0], 's': [-1], 't': [1], 'y': [0]},
            {'a': 0, 'l': 1, 'o': 1, 'r': 0, 's': 1, 't': 1, 'y': 0})

        guess = 'tools'
        expected = self.fixture.hotness_weights[1] + \
                   self.fixture.hotness_weights[2] + \
                   0 + \
                   self.fixture.hotness_weights[-2] + \
                   self.fixture.hotness_weights[-1]

        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_word_does_not_use_all_letters(self):
        letter_hotness = LettersHotness(
            {'a': [-2], 'o': [2], 'r': [0], 's': [-1], 't': [1], 'y': [0]},
            {'a': 1, 'o': 1, 'r': 0, 's': 1, 't': 1, 'y': 0})

        guess = 'toons'
        expected = self.fixture.hotness_weights[0]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_letter_freq_is_more_than_required(self):
        letter_hotness = LettersHotness(
            {'t': [-2], 'o': [-1]},
            {'t': 1, 'o': 1}
        )

        guess = 'toons'
        expected = self.fixture.hotness_weights[-2] + \
                   self.fixture.hotness_weights[-1] + \
                   0 + \
                   self.fixture.hotness_weights[None] + \
                   self.fixture.hotness_weights[None]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_letter_freq_is_less_than_required(self):
        letter_hotness = LettersHotness(
            {'a': [-2], 'o': [2], 'r': [0], 's': [-1], 't': [1], 'y': [0]},
            {'a': 1, 'o': 3, 'r': 1, 's': 1, 't': 1, 'y': 1})

        guess = 'toons'
        expected = float('-inf')
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_word_has_letter_at_wrong_position(self):
        letter_hotness = LettersHotness(
            {'a': [-1]},
            {'a': 1})

        guess = 'almug'
        expected = float('-inf')
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_word_has_letter_at_wrong_position_2(self):
        letter_hotness = LettersHotness(
            {'a': [1]},
            {'a': 1})

        guess = 'traps'
        expected = float('-inf')
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_word_has_repeated_letters_at_wrong_position(self):
        letter_hotness = LettersHotness(
            {'a': [-4, -5]},
            {'a': 2},
        )

        guess = 'alarm'
        expected = self.fixture.hotness_weights[-4] + \
                   self.fixture.hotness_weights[-5]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_word_has_letter_at_correct_position_derived_from_exclusion_rule(self):
        letter_hotness = LettersHotness(
            {'m': [-1,-2,-3,-4]},
            {'m': 1}
        )

        guess = 'alarm'
        expected = self.fixture.hotness_weights[5]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_letter_has_both_wrong_position_and_correct_hotness(self):
        letter_hotness = LettersHotness(
            {'m': [-1, 5]},
            {'m': 1}
        )

        guess = 'alarm'
        expected = self.fixture.hotness_weights[5]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_letter_has_both_wrong_position_and_correct_hotness_2(self):
        letter_hotness = LettersHotness(
            {'c': [-1, 4]},
            {'c': 1}
        )

        guess = 'click'
        expected = self.fixture.hotness_weights[0]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_score_word_by_letters_closeness_when_letter_has_both_wrong_position_and_correct_hotness_multiple_letters(self):
        letter_hotness = LettersHotness(
            {'m': [-1, 5]},
            {'m': 2}
        )

        guess = 'alarm'
        expected = self.fixture.hotness_weights[0]
        self.assertEqual(expected, self.fixture.score_word(guess, letter_hotness))

    def test_suggestions(self):
        letter_hotness = LettersHotness(
            {'e': [0], 'i': [0], 'n': [-3], 'r': [-1], 's': [0]},
            {'e': 0, 'i': 0, 'n': 1, 'r': 1, 's': 0},
        )
        suggestions = self.fixture.suggestions(letter_hotness, 10)

        self.assertTrue((2, 'angry') in suggestions)

    def test_suggestions_2(self):
        letters_hotness = LettersHotness(
            {'a': [0], 'c': [0], 'd': [0], 'e': [0], 'h': [0], 'i': [0], 'n': [-5, -3], 'o': [0], 'r': [-4, -1], 's': [0], 't': [0], 'u': [3], 'y': [0]},
            {'a': 0, 'c': 0, 'd': 0, 'e': 0, 'h': 0, 'i': 0, 'n': 1, 'o': 0, 'r': 1, 's': 0, 't': 0, 'u': 1, 'y': 0},
        )
        suggestions = self.fixture.suggestions(letters_hotness, 10)

        self.assertTrue((7, 'wrung') in suggestions)
