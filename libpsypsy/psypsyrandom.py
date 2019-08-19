#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A modified version of Christophe Pallier's Shuffle

Shuffles lines from a table with optional constraints on repetitions.

Constraints:
max_rep: maximum number of repetitions of a string in a columns
min_gap: minimum distances (in rows) between two repetitions of a string
(maxrep and mingat are dictionaries mapping column number
to a number expressing the constraint)
"""

__author__ = 'ShY'
__copyright__ = 'Copyright 2018, SHY'
__version__ = '0.2.0 (20180531)'
__maintainer__ = 'ShY, Pierre Halle'
__email__ = 'shi4yu2@gmail.com'
__status__ = 'Development'


import random
import time
import itertools
from libpsypsy.psypsyio import *


def swap(table, row_i, row_j):
    # type: (list, int, int) -> list
    """
    swap two elements of a list
    :param table: list to modify
    :type table: list
    :param row_i: row number i
    :type row_i: int
    :param row_j: row number j
    :type row_j: int
    :return: table: the same list after swap
    :rtype: table: list
    """
    tmp = table[row_i]
    table[row_i] = table[row_j]
    table[row_j] = tmp
    return table


def condition_to_keys(header):
    # type: (list) -> dict
    """
    make all columns to a dict of {column_name: column_position}
    :param header: list of header
    :type header: list
    :return header_index: dict of {column_name: column_position}
    :rtype header_index: dict
    """
    header_index = {}
    for condition in header:
        index = header.index(condition)
        header_index[condition] = index
    return header_index


def make_constraints(header, constraints):
    # type: (list, dict) -> dict
    """
    make constraints dict for randomisation
    :param header: list of header
    :type header: list
    :param constraints: constraints of randomisation
    :type constraints: dict
    :return position_constrains: constraint format for randomisation
    :rtype position_constraints: dict
    """
    header_index = condition_to_keys(header)

    # create position index
    position_constraints = {}

    # fill position index with constraints
    for key, value in constraints.items():
        position = header_index[key]
        position_constraints[position] = value

    return position_constraints


def shuffle_eq_prob(table, max_rep=None, min_gap=None, time_limit=1):
    # type: (list, dict, dict, int) -> list
    """
    Make a large number of randomisation to reach the eq-probability
    :param table: table of conditions
    :type table: list[list[str]]
    :param max_rep: maximum number of repetitions of a string in a columns
    :type max_rep: dict
    :param min_gap: minimum distances (in rows) between two repetitions of a string
    in the same column
    :type min_gap: dict
    :param time_limit: max time in second of execution
    :type time_limit: int
    :return: table after randomisation
    :rtype: list[list[str]]
    """
    start_time = time.time()
    continue_shuffle = True  # test if table respect all constraints
    test = True  # return bool value of constraints check

    while continue_shuffle and (time.time() < (start_time + time_limit)):
        random.shuffle(table)  # Randomise lines in table
        test, _ = check_constraints(table, max_rep, min_gap)
        continue_shuffle = not test  # end condition for while
    if not test:
        raise Exception("No possible randomisation")
    else:
        return table


def check_constraints(table, max_rep=None, min_gap=None, row_i=0):
    # type: (list, dict, dict, int) -> (bool, int)
    """
    Checks if a permutation respects constraints.
    :param table: input list
    :type table: list
    :param max_rep: maximum number of repetitions of a string in a columns
    :type max_rep: dict
    :param min_gap: minimum distances (in rows) between two repetitions of a string
    :type min_gap: dict
    :param row_i: selected line
    :type row_i: int
    :return: tuple of test and row number
    :rtype: tuple(bool, int)
    """
    if max_rep is not None:
        repetitions = max_rep.copy()  # make a copy of max repetition constraints
        for field in repetitions.keys():
            repetitions[field] = 1

    if row_i < 0:
        row_i = 0

    previous_line = table[row_i]  # get selected line of table
    row_i += 1
    da = True

    while da and row_i < len(table):
        line = table[row_i]

        # check max_rep constraints ===========================================
        if max_rep is not None:
            for field in max_rep.keys():
                if previous_line[field] == line[field]:
                    # test if condition for line & pre-line are the same
                    repetitions[field] += 1
                    da = (repetitions[field] <= max_rep[field])
                else:
                    repetitions[field] = 1
                if not da:
                    break

        # check min_gap constraints ===========================================
        if min_gap is not None:
            for field in min_gap.keys():
                previous_col = row_i - min_gap[field]
                if previous_col < 0:
                    previous_col = 0

                while da and (previous_col < row_i):
                    da = da and (table[previous_col][field] != table[row_i][field])
                    previous_col += 1
                if not da:
                    break

        previous_line = line

        if da:
            row_i += 1

    return da, row_i


def randomise_stimuli(table, max_rep=None, min_gap=None, time_limit=1):
    """
    Shuffle the condition table
    :param table: table of conditions
    :type table: list[list[str]]
    :param max_rep: maximum number of repetitions of a string in a columns
    :type max_rep: dict
    :param min_gap: minimum distances (in rows) between two repetitions of a string
    :type min_gap: dict
    :param time_limit: max time in second of execution
    :type time_limit: int
    :return table: table after randomisation
    :rtype table: list[list[str]]
    """
    n = len(table)  # get length of the table

    m1, m2 = 0, 0
    if min_gap is not None:
        m1 = max(min_gap.values())
    if max_rep is not None:
        m2 = max(max_rep.values())

    backtrack = max(m1, m2)

    start_time = time.time()
    random.shuffle(table)

    da = False
    row_i = 0
    n_failure = 0

    while not da and (time.time() < (start_time + time_limit)):
        da, row_i = check_constraints(table, max_rep, min_gap, row_i - backtrack)

        if not da:
            n_failure += 1
            if (row_i >= (n - 1)) or (n_failure > (n * 100)):  # start again
                # Reinitialise all, redo randomisation
                random.shuffle(table)
                row_i = 0
                n_failure = 0
            else:  # swap current row with another one further down the table
                row_j = random.choice(range(row_i + 1, n))
                swap(table, row_i, row_j)

    if da:
        return table
    else:
        raise Exception("No possible randomisation")


def randomisation_parts(filename, result_path, part, subj, constraints):
    # type: (list, str, str, str, dict) -> ()
    """
    Generic Parts randomisation
    :param filename: list of stimuli table file
    :type filename: list
    :param result_path: result file name
    :type result_path: str
    :param part: part indication
    :type part: str
    :param subj: subject number
    :type subj: str
    :param constraints: constrains on repetition
    :type constraints: dict
    """
    # Generate all permutations of the file list
    permutations = list(itertools.permutations(filename))
    length_permutation = len(permutations)

    if int(part) > length_permutation:
        raise Exception

    # get header
    _, header = read_csv(filename[0])
    results = [header[:] + ['part']]
    # print(list(permutations[0]))
    # print(length_permutation)

    order = list(permutations[int(part) - 1])
    for i in range(len(order)):
        table, _ = read_csv(order[i])
        table_random = randomise_stimuli(table, max_rep=constraints)
        for line in range(len(table_random)):
            table_random[line].append(str(part))

        results += table_random

    result_file = result_path + "gemination_axb_" + subj + ".csv"
    write_result_table(result_file, results)
    return
