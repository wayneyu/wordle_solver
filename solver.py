import json
import random
from util import dict2arr, arr2dict, a2i, i2a
from enum import Enum
from collections import Counter, defaultdict


class Solver:

    def __init__(self, words_list_path, number_of_letters=5, max_guesses=6, hotness_weights=None):
        self.words_list_path = words_list_path
        self.number_of_letters = number_of_letters
        all_words_dict = self.load_words(words_list_path)
        self.words_dict = {w: k for w, k in all_words_dict.items() if len(w) == self.number_of_letters}
        self.max_guesses = max_guesses
        if hotness_weights is None:
            self.hotness_weights = {}
            self.hotness_weights.update({i: 5 for i in range(1, self.number_of_letters+1)})
            self.hotness_weights.update({-i: 1 for i in range(1, self.number_of_letters+1)})
            self.hotness_weights.update({HotnessType.WRONG.value: float('-inf'), None: 0})
        else:
            self.hotness_weights = hotness_weights

        print(f"Dictionary size: {len(self.words_dict)}")

    def load_words(self, file_path):
        return json.load(open(file_path))

    def random_word(self, words_dict=None):
        if not words_dict:
            words_dict = self.words_dict

        return random.choice(list(words_dict.keys()))

    def is_valid_word(self, word, words_dict=None):
        if not words_dict:
            words_dict = self.words_dict

        return word in words_dict

    def all_valid_words_from_hotness(self, letters_hotness):
        """
        Get all valid words given a hotness array

        :param word: str
        :param letters_hotness: LettersHotness
        :return: list of words given the hints
        """
        return {w: v for w, v in self.words_dict.items() if self.is_valid_by_hotness(w, letters_hotness)}

    def is_valid_by_hotness(self, word, letters_hotness):
        for letter in word:
            hv = letters_hotness.get(letter)
            if hv and hv[0] == 0:
                return False
        return True

    def hotness(self, word, target):
        """
        Returns hotness of a word relative to a target word. Both words need to be of same length
        Output is an array where the value at each index of the array indicates the closeness of the word.
        A value of >=1 at index `i` indicates the letter word[i] matches the letter target[i]. The value is the index i
        A value of <=-1 at index `i` indicates the letter word[i] matches the letter target[i]
            but the letter word[i] appears at other position in `target`. The value is the index i
        A value of 0 at index `i` indicates the letter word[i] does not match the letter target[i]
            and the letter word[i] does not appear at any other position in `target`

        :param word: str
        :param target: str
        :return: [-1, 2, 0, ...]
        """
        if len(word) != len(target):
            raise Exception(f"Input words {word} and {target} are not of the same length")

        assert self.is_valid_word(word), f"{word} is not valid"
        assert self.is_valid_word(target), f"{target} is not valid"

        res = []
        target_letters = set(list(target))
        for i in range(len(word)):
            if word[i] == target[i]:
                res.append(i+1)
            elif word[i] != target[i] and word[i] in target_letters:
                res.append(-i-1)
            else:
                res.append(0)

        h = WordHotness()
        h.update_word(word, res)
        return h

    def score_word(self, word, letters_hotness):
        score = 0
        wrong_letter_score = self.hotness_weights[HotnessType.WRONG.value]

        # check letter frequency
        word_letter_freq = Counter(word)
        for letter, freq in word_letter_freq.items():
            if letters_hotness.freq[a2i(letter)] is not None and freq < letters_hotness.freq[a2i(letter)]:
                score += wrong_letter_score
                break
        for i, freq in enumerate(letters_hotness.freq):
            letter = i2a(i)
            if freq is not None and (word_letter_freq[letter] < freq or freq == 0 and word_letter_freq[letter] > 0):
                score += wrong_letter_score
                break

        word_score = defaultdict(int)
        for letter in set(word):
            idx = a2i(letter)
            for h in letters_hotness.hotness[idx]:
                if h == 0:
                    word_score[letter] = wrong_letter_score
                    break
                elif h > 0:
                    if word[h-1] == letter:
                        word_score[letter] = max(word_score[letter], self.hotness_weights[h])
                    else:
                        word_score[letter] = wrong_letter_score
                        break
                else:
                    if letter == word[-h-1]:
                        word_score[letter] = wrong_letter_score
                        break
                    else:
                        possible_positions = [j for j in range(1, self.number_of_letters + 1) if -j not in letters_hotness.hotness[idx]]
                        if len(possible_positions) == 1 and word[possible_positions[0] - 1] == letter:
                            word_score[letter] = max(word_score[letter], self.hotness_weights[possible_positions[0] - 1])
                        else:
                            word_score[letter] = max(word_score[letter], self.hotness_weights[h])

        score += sum([score * letters_hotness.freq[a2i(letter)] for letter, score in word_score.items() if letters_hotness.freq[a2i(letter)] > 0])

        return score

    def suggestions(self, letters_hotness, num_suggestions=5):
        """
        Given a word hotness array, what's the next best guess to make
        :param letters_hotness: LetterHotness
        :return: List[str]
        """
        import heapq
        top_n = []
        for word in self.words_dict:
            score = self.score_word(word, letters_hotness)
            if len(top_n) < num_suggestions:
                heapq.heappush(top_n, (score, word))
            elif top_n[0][0] < score:
                heapq.heappop(top_n)
                heapq.heappush(top_n, (score, word))

        return top_n

    def play(self):
        # pick a random word
        # wait for input
        # if correct guess, finish game
        # validate word,if not valid print "invalid word", wait for input, if valid, go to next step
        # calculate hotness of word
        # calculate hotness of all letters from all attempts
        # display letter hotness
        # repeat from wait for input
        target = self.random_word()
        letters_hotness = LettersHotness()
        for guess_number in range(1, self.max_guesses+1):
            while True:
                guess = input(f"Guess next word. Current hotness of letters: \n{letters_hotness}\nGuess {guess_number}: ")
                if len(guess) != len(target):
                    print(f"Guess needs to be a {self.number_of_letters}-letter word")
                elif not self.is_valid_word(guess):
                    print(f"Invalid word. Guess again.")
                else:
                    break

            if guess == target:
                print(f'Your guess {target} is correct!')
                return
            else:
                word_hotness = self.hotness(guess, target)
                letters_hotness.update_word(guess, word_hotness)
                print(f"Your guess is not correct but close. Here're some suggestions: "
                      f"{', '.join([f'{word}({score})' for score, word in sorted(self.suggestions(letters_hotness, 10), reverse=True)])}, {self.score_word(target, letters_hotness)}")
                print(word_hotness)

        print(f"Sorry, you ran out of guesses. The correct word is {target}")
        return

    def suggest(self, num_suggestions=10):
        # wait for word input
        # wait for hotness input
        # update letters hotness
        # print suggestions
        # repeat

        letters_hotness = LettersHotness()
        input_to_hotness_map = {'?': -1, '1': 1, 'x': 0}
        for i in range(1, self.max_guesses+1):
            while True:
                try:
                    word = input(f"Type in guess {i}: ")
                    assert self.is_valid_word(word), f"{word} is an invalid word"
                    word_hotness_input = list(input(f"Type in word hotness like (ex: ??x11), ?(right but wrong pos), x (wrong char), 1 (right char right pos): "))
                    arr = [input_to_hotness_map[x]*(i + 1) for i, x in enumerate(word_hotness_input)]

                    assert len(word) == len(word_hotness_input), "length of word and hotness must be the same"
                    assert all([-self.number_of_letters <= x <= self.number_of_letters for x in arr]), "some input value are incorrect"

                    if all([x >= 1 for x in arr]):
                        return
                    else:
                        word_hotness = WordHotness(word, arr)
                        break
                except AssertionError as e:
                    print(e)
                except ValueError as e:
                    print("Input value or format is not correct")

            letters_hotness.update_word(word, word_hotness)
            suggestions = sorted(self.suggestions(letters_hotness, num_suggestions), reverse=True)
            print(f"Current letter hotness: \n{letters_hotness}")
            print(f"Here are some suggestions: {', '.join([f'{word}({score})' for score, word in suggestions])}")

        return


class HotnessType(Enum):
    CORRECT_CHAR_POS = 1
    WRONG = 0
    CORRECT_CHAR = -1


class Hotness:
    hotness_to_char_mapping = {i: str(i) for i in range(-27, 27)}
    hotness_to_char_mapping.update({HotnessType.WRONG.value: 'x', None: ' '})
    hotness = None
    freq = None


class WordHotness(Hotness):

    def __init__(self, word=None, hotness=None):
        self.hotness = hotness
        self.word = word

    def update_word(self, word, hotness):
        self.word = word
        self.hotness = hotness

    def __str__(self):
        res = f"[{' '.join([c.rjust(2, ' ') for c in self.word])}]"
        res += "\n"
        res += f"[{' '.join([self.hotness_to_char_mapping[h].rjust(2, ' ') for i,h in enumerate(self.hotness)])}]"

        return res


class LettersHotness(Hotness):

    def __init__(self, hotness=None, freq=None):
        """
        An array representing the hotness of all alphabetical letters.
        1->N for the position in a word
        0 for correct but wrong position
        -1 for wrong letter
        None for unknown hotness
        """
        if hotness is None:
            hotness = {}
        if freq is None:
            freq = {}
        self.hotness = dict2arr(hotness, [])
        self.freq = dict2arr(freq, None)

    def update_word(self, word, word_hotness):
        freq = defaultdict(int)
        for i, h in enumerate(word_hotness.hotness):
            letter = word[i]
            idx = a2i(letter)
            f = 0 if h == 0 else 1
            freq[idx] += f

        for idx, f in freq.items():
            self.freq[idx] = f

        new_letter_hotness = dict2arr({}, [])
        for wi, wh in enumerate(word_hotness.hotness):
            c = word[wi]
            # case when letter is correct but duplicated,
            # the hotness of the duplicated letter carries positional information
            if wh == 0 and freq[a2i(c)] > 0:
                new_letter_hotness[a2i(c)].append(-wi-1)
            else:
                new_letter_hotness[a2i(c)].append(wh)

        # one letter:
        #   case 1: [-1], [-2]
        #   case 2: [-1], [4]
        #   case 3: [4], [-1]
        #   case 4: [4], [4]
        #   case 5: [0], [0]
        # multiple letters:
        #   case 6: [-1], [-2]
        #   case 7: [-1], [-1, -2]
        #   case 8: [-1], [-2, -3]
        #   case 9: [-1], [-2, 4]
        #   case 10: [-1], [3, 4]
        #   case 11: [-1, -2], [-1, -2]
        #   case 12: [-1, -2], [-3, -4]
        #   case 13: [-1, -2], [-3, 4]
        #   case 7: [-1, -2], [3, 4]
        #   case 3: [4], [-1]
        #   case 3: [4], [-1, -2]
        #   case 3: [4], [-1, 4]
        #   case 3: [4], [5]
        #   case 3: [4], [4, 5]

        for i, hv in enumerate(new_letter_hotness):
            if hv:
                if self.hotness[i]:
                    if self.hotness[i][-1] == HotnessType.WRONG.value:
                        continue
                    else:
                        self.hotness[i] = sorted(set(self.hotness[i] + hv))
                else:
                    self.hotness[i] = sorted(set(hv))

    def get(self, letter):
        return self.hotness[a2i(letter)]

    def __str__(self):
        rpad = 8
        res = f"[{' '.join([(i2a(i)).rjust(rpad, ' ') for i,h in enumerate(self.hotness)])}]"
        res += "\n"
        res += f"[{' '.join([','.join([self.hotness_to_char_mapping[h] for h in hv]).rjust(rpad, ' ') for i,hv in enumerate(self.hotness)])}]"
        res += "\n"
        res += f"[{' '.join([(str(f) if f is not None else '').rjust(rpad, ' ') for i,f in enumerate(self.freq)])}]"

        return res

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        o = LettersHotness()
        o.hotness = self.hotness.copy()
        o.freq = self.freq.copy()
        return o


if __name__ == '__main__':
    number_of_letters = 5
    max_guesses = 6
    dictionary_path = 'data/words_dictionary.json'
    # s = Solver(dictionary_path, number_of_letters, max_guesses).play()
    s = Solver(dictionary_path, number_of_letters, max_guesses).suggest(20)

