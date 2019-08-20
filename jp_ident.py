#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import pygame.font
import pygame.event
import pygame.draw
import pygame.image
import ypinterface
import ypio
import time
from pygame.locals import *

__author__ = 'ShY'

# subject
subj = "24"

# Filename
ident_list = "list_ident/ident_" + subj + ".xlsx"

# output file
ident_result = "result_ident/ident_" + subj + ".txt"

# Program environment parameter
font = "helvetica"
background = [255, 255, 255]  # white


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


# ---------------------------------------------------------------

# initialisation pygame
pygame.init()
pygame.mixer.init()
largeur, hauteur = ypinterface.get_screensize()
screen = pygame.display.set_mode((largeur, hauteur), pygame.FULLSCREEN)
# Desactiver la souris
pygame.mouse.set_visible(False)

screen.fill(background)
pygame.display.flip()
# ypinterface.wait_for_key()


# Import stimuli file ===========================================
ident_stimuli = ypio.excel_stimuli_processing(ident_list)

# instruction
instructionImage = pygame.image.load("instructionident.png")
w, h = instructionImage.get_size()
screen.blit(instructionImage, [largeur / 2 - w / 2, hauteur / 2 - h / 2])
pygame.display.flip()
ypinterface.wait_for_key()
screen.fill(background)
pygame.display.flip()

pygame.time.wait(1000)
screen.fill(background)
pygame.display.flip()
#

# training

# training_exp_sortie = open("result_identification_training.txt", 'w')


# =================== Debut experience ========================
ident_exp_sortie = open(ident_result, 'w')

print >> ident_exp_sortie, "Number" + '\t' + "File" \
                           + '\t' + "Token" \
                           + '\t' + "Middlev" \
                           + '\t' + "Voyelle" \
                           + '\t' + "Consonne" \
                           + '\t' + "Response" + '\t' + "RT"


for i in range(ident_stimuli["trial_number"]):
    stimulus_path = "stimuli/" + ident_stimuli["Filename"][i]
    token = ident_stimuli["Token"][i]
    middlev = ident_stimuli["presence_middleV"][i]
    consonne = ident_stimuli["Consonne"][i]
    voyelle = ident_stimuli["Voyelle"][i]
    image_path = "ident/" + voyelle + consonne + "p" + voyelle + ".png"
    sound = pygame.mixer.Sound(stimulus_path)
    sound.play()
    time.sleep(pygame.mixer.Sound.get_length(sound) + 0.5)
    # image

    stimuli_text = voyelle + consonne + "?p" + voyelle
    ypinterface.display_text(screen, stimuli_text)
    pygame.display.flip()
    resp, rt = wait_ident(None)
    screen.fill(background)
    pygame.display.flip()
    print >> ident_exp_sortie, str(i) + '\t' + ident_stimuli["Filename"][i] \
                               + '\t' + token\
                               + '\t' + middlev\
                               + '\t' + voyelle\
                               + '\t' + consonne\
                               + '\t' + resp + '\t' + str(rt)
    pygame.time.wait(1000)

ident_exp_sortie.close()

#
pygame.quit()
