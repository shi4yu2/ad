#! /usr/bin/env python3
#  -*- coding: utf-8 -*-

__author__ = 'ShY'
__copyright__ = 'Copyright 2019, SHY'
__version__ = '0.1s.0 (20190818)'
__maintainer__ = 'ShY'
__email__ = 'shi4yu2@gmail.com'
__status__ = 'Development'


import pygame
import pygame.draw
import pygame.event
import pygame.font
import pygame.image
import sys
import os
from pygame.locals import *
import libpsypsy.psypsyio as psypsyio
import libpsypsy.psypsyaxb as psypsyaxb
import libpsypsy.psypsyinterface as psypsyinterface


# MAIN =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
if __name__ == "__main__":

	# == command-line args: exp, subj  =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	expd = sys.argv[1]
	subj = sys.argv[2]
	print("expd: " + expd)
	print(subj)

	if expd != "abx":
		raise Exception("Exp type should be abx or ident")

	if not subj.isdigit():
		raise Exception("Subj argument should be a number.")
	# Parameter	 =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*=*=*=*=*
	# == Path =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	stimuli_path = "stimuli/"
	training_path = stimuli_path + "training/"
	results_path = "results/" + expd + "/"
	instructions_path = "instructions/"


	# == Instructions =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	instructions = {"start": instructions_path + "instruction.png",
					"pause": instructions_path + "instruction_break.png",
					"end_training": instructions_path + "instruction_end_training.png",
					"end_exp": instructions_path + "instruction_end_exp.png"}

	# == Program environment parameter	=*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	font = "helvetica"
	background = (150, 150, 150)  # gray

	# Experiment parameter =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*
	isi = 1000	# ISI = 1000ms
	interTrial = 1000  # inter-trial time = 1000ms
	fixation_duration = 500	 # fixation point duration


	# == EXP =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	# initialise pygame graphics *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	screen, screen_width, screen_height = psypsyinterface.initialisation_pygame(background)

	# General instructions 
	psypsyinterface.display_instruction(instructions.get("start"),
		screen, screen_width, screen_height, background)

	pygame.time.wait(2000)
	pygame.quit()

