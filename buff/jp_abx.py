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

	if expd != "abx" or expd != "ident":
		raise Exception("Exp type should be abx or ident")

	if not subj.isdigit():
		raise Exception("Subj argument should be a number.")

	# Parameter	 =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*=*=*=*=*
	# == Path =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	stimuli_path = "stimuli/"
	training_path = stimuli_path + "training/"
	results_path = "results/" + exp + "/"
	instructions_path = "instructions/"


	# == Instructions =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	instructions = {"start": instructions_path + "instruction_start.png",
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

	# trial-list spec files for test (randomized) and training (no randomization)
	# axb_input = expd + "/trial_axb/test_" + str(subj) + ".csv"
	# train_input = expd + "/list_trial/axb_training.csv"

	# results file names for test and training
	axb_result = results_path + str(subj) + ".csv"
	train_result = results_path + str(subj) + ".csv"

	# Check whether the result file exists
	if os.path.isfile(axb_result) and os.path.isfile(train_result):
		raise Exception("Results for this subject already exist.")

	# *=*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	# == EXP =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	# initialise pygame graphics *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	screen, screen_width, screen_height = psypsyinterface.initialisation_pygame(background)

	# General instructions 
	psypsyinterface.display_instruction(instructions.get("start"),
		screen, screen_width, screen_height, background)

# (A) Training 
	# sampling rate 
	pygame.mixer.quit()
	sampling_freq = psypsyio.get_expt_sf(expd + "/training")
	pygame.mixer.init(sampling_freq, -16, 2)
	resume = axb(screen, background, expd, train_input, train_result, instructions, isi, fixation_duration, interTrial, train=True)
#	print("nb ok: " + str(resume["nb_correct"]) + "/" + str(resume["nb_trials"]))
#	print(str(int(resume["ave_crt"])))

# (B) Test
	# sampling rate 
	pygame.mixer.quit()
	sampling_freq = psypsyio.get_expt_sf(expd + "/stim")
	pygame.mixer.init(sampling_freq, -16, 2)
	psypsyinterface.display_instruction(instructions.get("end_training"), screen, screen_width, screen_height, background)

	resume = axb(screen, background, expd, axb_input, axb_result, instructions, isi, fixation_duration)

	psypsyinterface.display_instruction(instructions.get("end_exp"), screen, screen_width, screen_height, background)

	pygame.quit()

