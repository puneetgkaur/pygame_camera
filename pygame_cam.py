import pygame
import pygame.camera
from pygame.locals import *

import sys, os

import dbus

from sugar3.activity import activity

class pygameCam(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
	#init pygame
	pygame.init()
	pygame.camera.init()
	#screen=pygame.display.set_mode((640,480))
    	camlist = pygame.camera.list_cameras()
    	if camlist:
            self.cam = pygame.camera.Camera(camlist[0],(640,480))
	self.cam.start()
	"""      
        while 1:
	    self.image=self.cam.get_image()
	    screen.blit(self.image,(0,0))
	    pygame.display.update()
	    for event in pygame.event.get():
		if event.type == pygame.QUIT or  (event.type == KEYDOWN and event.key == K_ESCAPE):
		    #save the image
		    self.image=self.cam.get_image()
		    self.cam.stop()

	"""	
	    

	def get_imageStream(self):
	    self.image=self.cam.get_image()
	    return self.image

	def stop_camera(self):
	    self.cam.stop()
