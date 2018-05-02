import datetime
import socket
import sys
import threading
import random
import string

def help_info(arg):
    info = ''
    for key, value in commands.items():
        info += key + value + '\n'
    return info



def hello(arg):
    return 'Hello ' + arg



def flip(arg):
    return random.choice(['Heads', 'Tails'])


def nextchar(chars):
    return random.choice(chars)


def randpass(arg):
    try:
        if arg < 6 or arg > 20:
            return "Length outside (6-20) range"
        length = arg - 3
        pwd = []
        possible_chars = string.ascii_letters + string.digits + string.punctuation
        pwd.append(random.choice(string.ascii_lowercase))
        pwd.append(random.choice(string.ascii_uppercase))
        pwd.append(str(random.randint(0,9)))
        for i in range(length):
            pwd.append(nextchar(possible_chars))
    except ValueError:
        return "Invalid length"
    random.shuffle(pwd)
    return ''.join(pwd)


def dice(arg):
    return random.choice(['1', '2', '3', '4', '5', '6'])


def damerau_levenshtein_distance(a, b):
    # "Infinity" -- greater than maximum possible edit distance
    # Used to prevent transpositions for first characters
    INF = len(a) + len(b)

    # Matrix: (M + 2) x (N + 2)
    matrix  = [[INF for n in range(len(b) + 2)]]
    matrix += [[INF] + range(len(b) + 1)]
    matrix += [[INF, m] + [0] * len(b) for m in range(1, len(a) + 1)]

    # Holds last row each element was encountered: `DA` in the Wikipedia pseudocode
    last_row = {}

    # Fill in costs
    for row in range(1, len(a) + 1):
        # Current character in `a`
        ch_a = a[row-1]

        # Column of last match on this row: `DB` in pseudocode
        last_match_col = 0

        for col in range(1, len(b) + 1):
            # Current character in `b`
            ch_b = b[col-1]

            # Last row with matching character; `i1` in pseudocode
            last_matching_row = last_row.get(ch_b, 0)

            # Cost of substitution
            cost = 0 if ch_a == ch_b else 1

            # Compute substring distance
            matrix[row+1][col+1] = min(
                matrix[row][col] + cost, # Substitution
                matrix[row+1][col] + 1,  # Addition
                matrix[row][col+1] + 1,  # Deletion

                # Transposition
                matrix[last_matching_row][last_match_col]
                    + (row - last_matching_row - 1) + 1
                    + (col - last_match_col - 1))

            # If there was a match, update last_match_col
            # Doing this here lets me be rid of the `j1` variable from the original pseudocode
            if cost == 0:
                last_match_col = col

        # Update last row for current character
        last_row[ch_a] = row

    # Return last element
    return matrix[-1][-1]

