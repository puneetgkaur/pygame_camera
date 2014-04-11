import pygame
import pygame.camera
from pygame.locals import *

import sys, os

import dbus
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio

GObject.threads_init()

from sugar3.activity import activity
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity import widgets
from sugar3.graphics import style

class pygameCam(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

	#creating ui
        toolbox = widgets.ActivityToolbar(self)
        toolbox.share.props.visible = False

        stop_button = StopButton(self)
        stop_button.show()
        toolbox.insert(stop_button, -1)

        self.set_toolbar_box(toolbox)


        toolbox.show()


	#init pygame
	pygame.init()
	pygame.camera.init()

	#self.movie_window = Gtk.DrawingArea()

	screen=pygame.display.set_mode((640,480))

	#self.movie_window.add(screen)
	#self.movie_window.show()

    	camlist = pygame.camera.list_cameras()
    	if camlist:
            cam = pygame.camera.Camera(camlist[0],(640,480))

        cam.start()

        while 1:
	    self.image=cam.get_image()
	    screen.blit(self.image,(0,0))
	    pygame.display.update()
	    for event in pygame.event.get():
		if event.type == pygame.QUIT or  (event.type == KEYDOWN and event.key == K_ESCAPE):
		    #save the image
		    self.image=cam.get_image()


	def get_imageStream(self):
	    self.image=cam.get_image()
	    return self.image
