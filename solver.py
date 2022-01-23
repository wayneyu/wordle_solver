import json
import random
from util import dict2arr, arr2dict, a2i, i2a
from collections import Counter

class Solver:

    def __init__(self, words_list_path, number_of_letters=5, max_guesses=6, hotness_weights=None):
        self.words_list_path = words_list_path
        self.number_of_letters = number_of_letters
        all_words_dict = self.load_words(words_list_path)
        self.words_dict = {w: k for w, k in all_words_dict.items() if len(w) == self.number_of_letters}
        self.max_guesses = max_guesses
        self.hotness_weights = {i: 5 for i in range(1, self.number_of_letters+1)} if not hotness_weights else hotness_weights
        self.hotness_weights.update({0: 1, -1: float('-inf'), None: 0})
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
            if hv and hv[0] == -1:
                return False
        return True

    def hotness(self, word, target):
        """
        Returns hotness of a word relative to a target word. Both words need to be of same length
        Output is an array where the value at each index of the array indicates the closeness of the word.
        A value of >=1 at index `i` indicates the letter word[i] matches the letter target[i]. The value is the index i
        A value of -1 at index `i` indicates the letter word[i] does not match the letter target[i]
            and the letter word[i] does not appear at any other position in `target`
        A value of 0 at index `i` indicates the letter word[i] does not match the letter target[i]
            but the letter word[i] appears at other position in `target`

        :param word: str
        :param target: str
        :return: [-1, 1, 0, ...]
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
                res.append(0)
            else:
                res.append(-1)

        h = WordHotness()
        h.update_word(word, res)
        return h

    def score_word(self, word, letters_hotness):
        score = 0
        letter_freq = Counter(word)
        for i, hv in enumerate(letters_hotness.hotness):
            c = i2a(i)
            if hv:
                if hv[0] == -1:
                    if c in word:
                        # word has not allowed letter
                        score += self.hotness_weights[-1]
                elif hv[0] == 0:
                    if c in word and letter_freq[c] == len(hv):
                        # word has required letter
                        score += self.hotness_weights[0]
                    else:
                        # word does not have required letter
                        score += self.hotness_weights[-1]
                else:
                    for h in hv:
                        if word[h-1] == c:
                            score += self.hotness_weights[h]
                        else:
                            score += self.hotness_weights[-1]

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
        # print(target)
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
                letters_hotness.update_word(guess, word_hotness, target)
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
        input_to_hotness_map = {'x': -1, '1': 1, '0': 0}
        for i in range(1, self.max_guesses+1):
            while True:
                try:
                    word = input(f"Type in guess {i}: ")
                    assert self.is_valid_word(word), f"{word} is an invalid word"
                    word_hotness_input = list(input(f"Type in word hotness like (ex: 11x00): "))
                    arr = [input_to_hotness_map[x] if input_to_hotness_map[x] <= 0 else (i + 1) for i, x in enumerate(word_hotness_input)]
                    assert len(word) == len(word_hotness_input), "length of word and hotness must be the same"
                    assert all([-1 <= x <= self.number_of_letters for x in arr]), "some input value are incorrect"

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



class Hotness:
    hotness_to_char_mapping = {i: str(i) for i in range(1, 27)}
    hotness_to_char_mapping.update({-1: 'X', 0: 'O', 1: '1', None: ' '})
    hotness = None


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

    def __init__(self, hotness=None):
        """
        An array representing the hotness of all alphabetical letters.
        1->N for the position in a word
        0 for correct but wrong position
        -1 for wrong letter
        None for unknown hotness
        """
        if hotness is None:
            hotness = {}
        self.hotness = dict2arr(hotness, [])

    def update_word(self, word, word_hotness, target=None):
        new_letter_hotness = dict2arr({}, [])
        for wi, wh in enumerate(word_hotness.hotness):
            c = word[wi]
            if not (new_letter_hotness[a2i(c)] and new_letter_hotness[a2i(c)][0] == -1):
                new_letter_hotness[a2i(c)].append(wh)

        for i, hv in enumerate(new_letter_hotness):
            # if hv:
            #     print('i', i, 'i2a', i2a(i), 'hotness', self.hotness[i], 'new_hotness', hv)
            if hv:
                if self.hotness[i]:
                    if self.hotness[i][-1] <= 0 and 0 <= min(hv):
                        self.hotness[i] = hv
                    elif 1 <= self.hotness[i][-1] and (1 <= min(hv) or len(self.hotness[i]) < len(hv)):
                        self.hotness[i] = list(set(self.hotness[i] + hv))
                else:
                    self.hotness[i] = hv
            # if hv:
            #     print('--combined', self.hotness[i])

    def get(self, letter):
        return self.hotness[a2i(letter)]

    def __str__(self):
        res = f"[{' '.join([(i2a(i)).rjust(3, ' ') for i,h in enumerate(self.hotness)])}]"
        res += "\n"
        res += f"[{' '.join([','.join([self.hotness_to_char_mapping[h] for h in hv]).rjust(3, ' ') for i,hv in enumerate(self.hotness)])}]"

        return res

if __name__ == '__main__':
    number_of_letters = 5
    max_guesses = 6
    dictionary_path = 'data/words_dictionary.json'
    # s = Solver(dictionary_path, number_of_letters, max_guesses).play()
    s = Solver(dictionary_path, number_of_letters, max_guesses).suggest(20)

