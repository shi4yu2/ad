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
import libpsypsy.psypsyrandom as psypsyrandom

#------------------------------------------------------------------------------
#		abx() function
#------------------------------------------------------------------------------
def abx(screen, background, expedir, input_file, result_file, instructions, isi=1000, fixation_duration=500, interTrial=1000, train=False):
	try:
	# Get trials from input_file
	# stimuli are organised in a python dictionary: trial[field][i]  
		trial, header_index = psypsyio.read_stimuli(input_file, "\t")
		nb_trials = int(trial["trial_number"])
		pause_i = int(nb_trials/2 -1) 
		# print(trial["trial_number"])

		# Create result file
		result = open(result_file, "w")

		# Add header to result output file
		psypsyio.write_result_header(result, trial, result_columns)

		# Initialize counts for feedback
		nb_trials = nb_correct = nb_wrong = nb_missed = 0
		correct_rt = wrong_rt = 0

		for i in range(trial["trial_number"]):
			screen.fill(background)
			pygame.display.flip()

			# Pauses (test phase): halfway, 1 break
			if not train:
				if i == pause_i:
					psypsyaxb.axb_pause(screen, screen_width, screen_height, background, instructions.get("pause"))

			# Processing sound stimuli =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			if train:
				path = "stimuli/training/"
			else:
				path = "stimuli/test/"

			# Get stimuli path
			stimulus_a = path + trial["A"][i] 
			stimulus_x = path + trial["X"][i] 
			stimulus_b = path + trial["B"][i] 
			sound_path = [stimulus_a, stimulus_b, stimulus_x]

			# Load stimuli & Compute sound stimuli duration, get offset
			mixed_sounds, duration_sounds = psypsyinterface.mix_sound_stimuli(sound_path)
			# offset = int(trial["offset"][i])
#			print(stimulus_a, stimulus_x, stimulus_b, offset)

			# Compute target result
			if trial["X"][i][:-2] == trial["A"][i][:-2]:
				# compare two strings of A and X if identical then A else B
				target_response = "A"
			else:
				target_response = "B"

			# Prepare output line
			trial_result = []
			for key in header_index:
				trial_result.append(trial[header_index[key]][i])

			# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			# Play sounds and record response						   *
			# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			# Display fixation point
			psypsyinterface.point_fixation(screen, fixation_duration)
			# 500ms of display
			psypsyinterface.clear_screen(screen, background)

			# Play A ==============
			start_sound_a = pygame.time.get_ticks()
			mixed_sounds[0].play()	# PLAY SOUND A
			while pygame.mixer.get_busy():	# sound playing
				continue
			end_sound_a = pygame.time.get_ticks()

			while pygame.time.get_ticks() - end_sound_a < isi:
				continue
			pygame.event.pump()
			pygame.event.clear()  # clear event and wait for response

			# Play X and B and record response (Type, Time) =============
			xb_sequence = [mixed_sounds[1], mixed_sounds[2]]
			xb_measures = []
			response = False
			response_type = []
			response_time = []

			# indication for X and B
			# index_b == 0: ISI after X
			# index_b == 1: ISI after B
			index_b = 0

			for s in xb_sequence:
				# get start point of the sound
				duration = int(round(pygame.mixer.Sound.get_length(s), 3) * 1000)
				start_sound = pygame.time.get_ticks()
				xb_measures.append(start_sound)
				s.play()  # play sound

				# index_b == 1: 2000ms after sound B
				if index_b == 1:
					isi_post = 2000
				else:
					# index_b == 0: 1000ms after sound X
					isi_post = 1000

				while pygame.mixer.get_busy() and not response or (
						pygame.time.get_ticks() - start_sound <= duration + isi_post):
					for e in pygame.event.get():
						if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
							raise Exception("aborted")
						elif e.type == KEYDOWN:
							if e.key == K_LEFT:
								response_time = [pygame.time.get_ticks()]
								response_type = ["A"]
								response = True
							elif e.key == K_RIGHT:
								response_time = [pygame.time.get_ticks()]
								response_type = ["B"]
								response = True
						else:
							response = False

				# Get end point of the sound
				if index_b == 1:
					xb_measures.append(pygame.time.get_ticks() - 2*isi)
				elif index_b == 0:
					xb_measures.append(pygame.time.get_ticks() - isi)

				index_b += 1

			# Get measures
			start_sound_x = xb_measures[0]
			end_sound_x = xb_measures[1]
			start_sound_b = xb_measures[2]
			end_sound_b = xb_measures[3]

			# Handle empty response
			# response time =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			if response_time != []:
				response_time_s = response_time[0]
				real_rt = response_time_s - start_sound_b 
			else:
				response_time_s = 0
				real_rt = 0
			# response type =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			if response_type != []:
				response_type_s = response_type[0]
			else:
				response_type_s = "NA"

			# Compute the correctness of response
			# And display feedback for training
			nb_trials += 1

			if response_type_s == target_response:
				correct = "T"
				nb_correct += 1
				correct_rt += real_rt
				if train:
					psypsyinterface.display_text_colour(screen, str(real_rt) + " ms", colour=(0, 255, 0))
					pygame.time.wait(500)
					psypsyinterface.clear_screen(screen, background)
			elif response_type_s == "NA":
				correct = "F"
				nb_missed += 1
				if train:
					psypsyinterface.display_text_colour(screen, "???")
					pygame.time.wait(500)
					psypsyinterface.clear_screen(screen, background)
			else:
				correct = "F"
				# Calculate wrong response number and mean(rt)
				nb_wrong += 1
				wrong_rt += real_rt
				if train:
					for click in range(3):
						psypsyinterface.display_text_colour(screen, str(real_rt) + "ms")
						pygame.time.wait(100)
						psypsyinterface.clear_screen(screen, background)
						pygame.time.wait(50)

			# Append trial measures
			trial_result.extend([start_sound_a, duration_sounds[0], end_sound_a,
								 start_sound_b, duration_sounds[1], end_sound_b,
								 start_sound_x, duration_sounds[2], end_sound_x,
								 response_time_s, target_response, response_type_s, real_rt, correct])

			# Output results
			psypsyio.write_result_line(result, trial_result)

			# inter-trial time
			pygame.time.wait(interTrial)

		# Avoid division by zero for averaged RTs
		if nb_correct == 0:
			ave_crt = 0
		else:
			ave_crt = int(correct_rt / nb_correct)
		if nb_wrong == 0:
			ave_wrt = 0
		else:
			ave_wrt = int(wrong_rt / nb_wrong)

		resume = {"nb_trials": nb_trials,
				  "nb_correct": nb_correct,
				  "nb_wrong": nb_wrong,
				  "nb_missed": nb_missed,
				  "ave_crt": ave_crt,
				  "ave_wrt": ave_wrt}

		result.close()

	finally:

		if not train:
#			print("End experiment\n")
			pygame.time.wait(1000)
		else:
			summary = "nb ok: " + str(resume["nb_correct"]) + "/" \
 + str(resume["nb_trials"]) + ", ok RT: " + str(int(resume["ave_crt"])) \
 + " ==> Space to continue"
			psypsyinterface.display_text(screen, summary)
			psypsyinterface.wait_for_space()
			psypsyinterface.clear_screen(screen, background)
#			print("End training\n")

	return resume


#------------------------------------------------------------------------------
#		ident() function
#------------------------------------------------------------------------------
# Response function
def wait_ident(dur):
    ticks0 = pygame.time.get_ticks()
    while True:
        if dur != None and pygame.time.get_ticks() > ticks0 + dur:
            return
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                raise Exception
            if ev.type == KEYDOWN:
                if ev.key == K_s:
                    return ['0', pygame.time.get_ticks() - ticks0]
                if ev.key == K_d:
                    return ['a', pygame.time.get_ticks() - ticks0]
                if ev.key == K_f:
                    return ['i', pygame.time.get_ticks() - ticks0]
                if ev.key == K_j:
                    return ['u', pygame.time.get_ticks() - ticks0]
                if ev.key == K_k:
                    return ['e', pygame.time.get_ticks() - ticks0]
                elif ev.key == K_l:
                    return ['o', pygame.time.get_ticks() - ticks0]


def ident(screen, background, expedir, input_file, result_file, instructions, isi=1000, fixation_duration=500, interTrial=1000, train=False):
	try:
		# Get trials from input_file
		# stimuli are organised in a python dictionary: trial[field][i]  
		trial, header_index = psypsyio.read_stimuli(input_file, "\t")
		nb_trials = int(trial["trial_number"])
		pause_i = int(nb_trials/2 -1) 
		# print(trial["trial_number"])

		# Create result file
		result = open(result_file, "w")

		# Add header to result output file
		psypsyio.write_result_header(result, trial, result_columns)

		# Initialize counts for feedback
		nb_trials = nb_correct = nb_wrong = nb_missed = 0
		correct_rt = wrong_rt = 0

		for i in range(trial["trial_number"]):
			screen.fill(background)
			pygame.display.flip()

			# Processing sound stimuli =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			if train:
				path = "stimuli/training/"
			else:
				path = "stimuli/test/"

			# Prepare output line
			trial_result = []
			for key in header_index:
				trial_result.append(trial[header_index[key]][i])

			stimulus_path = "stimuli/test/" + trial["Filename"][i]
			token = trial["Token"][i]
			middlev = trial["presence_middleV"][i]
			consonne = trial["Consonne"][i]
			voyelle = trial["Voyelle"][i]
			image_path = "ident/" + voyelle + consonne + "p" + voyelle + ".png"
			sound = pygame.mixer.Sound(stimulus_path)
			sound.play()
			time.sleep(pygame.mixer.Sound.get_length(sound) + 0.5)
			# image

			stimuli_text = voyelle + consonne + "?p" + voyelle
			psypsyinterface.display_text(screen, stimuli_text)
			pygame.display.flip()
			resp, rt = wait_ident(None)
			screen.fill(background)
			pygame.display.flip()


			# Append trial measures =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			trial_result.extend([resp, str(rt)])

			# Output results =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*
			psypsyio.write_result_line(result, trial_result)

			pygame.time.wait(interTrial)
	
	finally:
		print("ident fin")
	
	return

# MAIN =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
if __name__ == "__main__":

	# == command-line args: exp, subj  =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	expd = sys.argv[1]
	subj = sys.argv[2]

	if not (expd == "abx" or expd == "ident"):
		raise Exception("Exp type should be abx or ident")

	if not subj.isdigit():
		raise Exception("Subj argument should be a number.")

	# Parameter	 =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*=*=*=*=*
	# == Path =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	instructions_path = "instructions/"

	stimuli_path = "stimuli/"
	training_path = stimuli_path + "training/"

	list_path = "list/"
	list_exp_path = list_path + expd + "/"

	results_path = "results/" + expd + "/"

	# == Instructions =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	instructions = {"start": instructions_path + "instruction.png"}
					# "pause": instructions_path + "instruction_break.png",
					# "end_training": instructions_path + "instruction_end_training.png",
					# "end_exp": instructions_path + "instruction_end_exp.png"}

	# == Program environment parameter	=*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	font = "helvetica"
	background = (150, 150, 150)  # gray

	# Experiment parameter =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*
	isi = 1000	# ISI = 1000ms
	interTrial = 1000  # inter-trial time = 1000ms
	fixation_duration = 500	 # fixation point duration

	# == Input / Output =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*=*
	#-------------------------
	# specify randomisation constraints here
	#-------------------------
	# for randomisation without constraints: {0: 0}
	if expd == "abx":
		# 6 repetitions
		constraints = {3: 2, 9: 2}
		randomisation_files = ["list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv"]
	elif expd == "ident":
		# 7 repetitions
		constraints = {3: 2, 4: 2}
		randomisation_files = ["list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv", "list/" + expd + ".csv"]

	psypsyrandom.randomisation_parts(randomisation_files, list_exp_path, 1, subj, constraints)

	# trial-list spec files for test (randomized)
	abx_input = list_exp_path + str(subj) + ".csv"
	ident_input = list_exp_path + str(subj) + ".csv"
	# train_input = expd + "/list_trial/axb_training.csv"

	# Result file columns  =*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=**=*=*=*=*=*=*
	result_columns = ["start_A", "duration_A", "end_A", "start_B", "duration_B", "end_B", "start_X", "duration_X", "end_X", "RT", "target_Response", "response", "real_RT", "Correctness"]

	ident_result_columns = ["resp", "rt"]

	# results file names for test and training
	abx_result = results_path + expd + "_" + str(subj) + ".csv"
	ident_result = results_path + expd + "_" + str(subj) + ".csv"
	train_result = results_path + "training" + "_" + str(subj) + ".csv"

	# Check whether the result file exists
	if os.path.isfile(abx_result) and os.path.isfile(train_result):
		raise Exception("Results for this subject already exist.")

	if os.path.isfile(ident_result) and os.path.isfile(train_result):
		raise Exception("Results for this subject already exist.")

	# *=*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	# == EXP =*=*=**=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	# initialise pygame graphics *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
	screen, screen_width, screen_height = psypsyinterface.initialisation_pygame(background)

	# General instructions 
	#psypsyinterface.display_instruction(instructions.get("start"),
	#	screen, screen_width, screen_height, background)

# # (A) Training 
# 	# sampling rate 
# 	pygame.mixer.quit()
# 	sampling_freq = psypsyio.get_expt_sf(expd + "/training")
# 	pygame.mixer.init(sampling_freq, -16, 2)
# 	resume = axb(screen, background, expd, train_input, train_result, instructions, isi, fixation_duration, interTrial, train=True)
# #	print("nb ok: " + str(resume["nb_correct"]) + "/" + str(resume["nb_trials"]))
# #	print(str(int(resume["ave_crt"])))

# (B) Test
	# # sampling rate 
	pygame.mixer.quit()
	#sampling_freq = psypsyio.get_expt_sf(expd + "/stim")
	pygame.mixer.init(44100, -16, 2)
	psypsyinterface.display_instruction(instructions.get("start"), screen, screen_width, screen_height, background)

	resume = abx(screen, background, list_exp_path, abx_input, abx_result, instructions, isi, fixation_duration)

	psypsyinterface.display_instruction(instructions.get("start"), screen, screen_width, screen_height, background)

	pygame.quit()

