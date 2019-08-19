#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PSYchology Python by Shi Yu
AXB experiment support functions
"""

# Todo :
#

__author__ = 'ShY'
__copyright__ = 'Copyright 2018, SHY'
__version__ = '0.1.0 (20180531)'
__maintainer__ = 'ShY, Pierre Halle'
__email__ = 'shi4yu2@gmail.com'
__status__ = 'Development'


from libpsypsy.psypsyinterface import *
from libpsypsy.psypsyio import *
from libpsypsy.psypsyrandom import *


def axb_pause(screen, screen_width, screen_height, background, instruction):
    # type: (object, int, int, tuple, str) -> ()
    """
    Experiment break
    :param screen: current display surface
    :type screen: Surface
    :param screen_width: current display width
    :type screen_width: int
    :param screen_height: current display height
    :type screen_height: int
    :param background: triple value of background (RGB)
    :type background: tuple
    :param instruction: instruction image path
    :type instruction: str
    """
    screen.fill(background)
    pygame.display.flip()
    display_instruction(instruction, screen, screen_width, screen_height, background)
    return


def randomisation_one_part(filename, result_path, exp_type, subj, constraints):
    # type: (str, str, str, str, dict) -> ()
    """
    Two Parts randomisation
    :param filename: list of stimuli table file
    :type filename: list
    :param result_path: result file name
    :type result_path: str
    :param exp_type: experiment indication
    :type exp_type: str
    :param subj: subject number
    :type subj: str
    :param constraints: constrains on repetition
    :type constraints: dict
    """
    table, header = read_csv(filename)
    table_random = randomise_stimuli(table, max_rep=constraints)
    results = [header] + table_random
    result_file = result_path + exp_type + "_" + subj + ".csv"
    write_result_table(result_file, results)


def randomisation_two_parts(filename, result_path, generic, part, subj, constraints):
    # type: (list, str, str, str, str, dict) -> ()
    """
    Two Parts randomisation
    :param filename: list of stimuli table file
    :type filename: list
    :param result_path: path to result file
    :type result_path: str
    :param generic: generic result filename
    :type generic: str
    :param part: part indication
    :type part: str
    :param subj: subject number
    :type subj: str
    :param constraints: constrains on repetition
    :type constraints: dict
    """
    f0 = filename[0]
    f1 = filename[1]

    table_0, header_0 = read_csv(f0)
    table_1, header_1 = read_csv(f1)
    header_0.append('part')

    table_random_0 = randomise_stimuli(table_0, max_rep=constraints)
    table_random_1 = randomise_stimuli(table_1, max_rep=constraints)
    for line in range(len(table_random_0)):
        table_random_0[line].append(str(part))

    for line in range(len(table_random_1)):
        table_random_1[line].append(str(part))

    if int(part) == 1:
        results = [header_0] + table_random_0 + table_random_1
    elif int(part) == 2:
        results = [header_0] + table_random_1 + table_random_0
    else:
        raise Exception("first-part not 1 or 2")

    result_file = result_path + generic + subj + ".csv"
    write_result_table(result_file, results)
    return
