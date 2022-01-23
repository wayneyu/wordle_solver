from string import ascii_lowercase


def a2i(letter):
    return ord(letter) - ord('a')


def i2a(i):
    return ascii_lowercase[i]


def dict2arr(dictionary, default=None):
    """

    :param dictionary: {'a': v1, 'b': v2, ...}
    :return: [v1, v2, ... ]
    """
    alphabet_length = 26
    res = [default.copy() for _ in range(alphabet_length)]
    for l, v in dictionary.items():
        if default is None:
            res[a2i(l)] = v
        elif type(default) is list:
            res[a2i(l)] = v if type(v) is list else [v]
        elif type(default) is set:
            res[a2i(l)] = v if type(v) is set else {v}
        elif type(default) is dict:
            res[a2i(l)] = v if type(v) is dict else {v: 1}

    return res


def arr2dict(arr):
    """

    :param arr: [v1, v2, ... ]
    :return: {'a': v1, 'b': v2, ...}
    """

    return {i2a(i): v for i, v in enumerate(arr)}
