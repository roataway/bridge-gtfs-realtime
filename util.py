import random
import string
import csv


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def build_trolley_relation(path):
    # TODO: skip first line of file, it is the csv header
    with open(path, mode='r') as infile:
        reader = csv.reader(infile)
        return {rows[0].replace('"', '') : rows[1].replace('"', '') for rows in reader}