import sys, os
import pygtk, Gtk, gobject
import Gdk
import pygst
pygst.require("0.10")
import gst

from sugar3.activity import widgets
from sugar3.activity.widgets import StopButton
from sugar3.activity import activity
from sugar3.graphics import style


class GTK_Main(activity.Activity):

    def __init__(self, handle):
        super(Record, self).__init__(handle)
        self.props.enable_fullscreen_mode = True
        #Instance(self)

	#detect camera
        v4l2src = gst.element_factory_make('v4l2src')
        if v4l2src.props.device_name is not None:
	    self._has_camera = True
	else:
	    self._has_camera = False

        pipeline = gst.Pipeline()
        caps = gst.Caps('video/x-raw-yuv,framerate=10/1')
        fsink = gst.element_factory_make('fakesink')
        pipeline.add(v4l2src, fsink)
        v4l2src.link(fsink, caps)
        self._can_limit_framerate = pipeline.set_state(gst.STATE_PAUSED) != gst.STATE_CHANGE_FAILURE
        pipeline.set_state(gst.STATE_NULL)

        self._pipeline = gst.Pipeline("Camera")
#----------------------------------------create photobin-------------------------------------
	#create photobin
        queue = gst.element_factory_make("queue", "pbqueue")
        queue.set_property("leaky", True)
        queue.set_property("max-size-buffers", 1)

        colorspace = gst.element_factory_make("ffmpegcolorspace", "pbcolorspace")
        jpeg = gst.element_factory_make("jpegenc", "pbjpeg")

        sink = gst.element_factory_make("fakesink", "pbsink")
        sink.connect("handoff", self._photo_handoff)
        sink.set_property("signal-handoffs", True)

        self._photobin = gst.Bin("photobin")
        self._photobin.add(queue, colorspace, jpeg, sink)

        gst.element_link_many(queue, colorspace, jpeg, sink)

        pad = queue.get_static_pad("sink")
        self._photobin.add_pad(gst.GhostPad("sink", pad))



        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._bus_message_handler)



	
#--------------------------------------from below the ui_init() start ---------------------------------------------------        

	self._fullscreen = True
	self._showing_info = False

	# FIXME: if _thumb_tray becomes some kind of button group, we wouldn't
	# have to track which recd is active
	self._active_recd = None

	self.connect_after('key-press-event', self._key_pressed)

	self._active_toolbar_idx = 0

	self._toolbar_box = ToolbarBox()
	activity_button = ActivityToolbarButton(self)
	self._toolbar_box.toolbar.insert(activity_button, 0)
	self.set_toolbar_box(self._toolbar_box)
	self._toolbar = self.get_toolbar_box().toolbar

	tool_group = None
	if self.model.get_has_camera():
	self._photo_button = RadioToolButton()
	self._photo_button.props.group = tool_group
	tool_group = self._photo_button
	self._photo_button.props.icon_name = 'camera-external'
	self._photo_button.props.label = _('Photo')
	self._photo_button.mode = constants.MODE_PHOTO
	self._photo_button.connect('clicked', self._mode_button_clicked)
	self._toolbar.insert(self._photo_button, -1)

	self._video_button = RadioToolButton()
	self._video_button.props.group = tool_group
	self._video_button.props.icon_name = 'media-video'
	self._video_button.props.label = _('Video')
	self._video_button.mode = constants.MODE_VIDEO
	self._video_button.connect('clicked', self._mode_button_clicked)
	self._toolbar.insert(self._video_button, -1)
	else:
	self._photo_button = None
	self._video_button = None

	self._audio_button = RadioToolButton()
	self._audio_button.props.group = tool_group
	self._audio_button.props.icon_name = 'media-audio'
	self._audio_button.props.label = _('Audio')
	self._audio_button.mode = constants.MODE_AUDIO
	self._audio_button.connect('clicked', self._mode_button_clicked)
	self._toolbar.insert(self._audio_button, -1)

	self._toolbar.insert(gtk.SeparatorToolItem(), -1)

	self._toolbar_controls = RecordControl(self._toolbar)

	separator = gtk.SeparatorToolItem()
	separator.props.draw = False
	separator.set_expand(True)
	self._toolbar.insert(separator, -1)
	self._toolbar.insert(StopButton(self), -1)
	self.get_toolbar_box().show_all()

	main_box = gtk.VBox()
	self.set_canvas(main_box)
	main_box.get_parent().modify_bg(gtk.STATE_NORMAL, COLOR_BLACK)
	main_box.show()

	self._media_view = MediaView()
	self._media_view.connect('media-clicked', self._media_view_media_clicked)
	self._media_view.connect('pip-clicked', self._media_view_pip_clicked)
	self._media_view.connect('info-clicked', self._media_view_info_clicked)
	self._media_view.connect('full-clicked', self._media_view_full_clicked)
	self._media_view.connect('tags-changed', self._media_view_tags_changed)
	self._media_view.show()

	self._controls_hbox = gtk.HBox()
	self._controls_hbox.show()

	self._shutter_button = ShutterButton()
	self._shutter_button.connect("clicked", self._shutter_clicked)
	self._controls_hbox.pack_start(self._shutter_button, expand=True, fill=False)

	self._countdown_image = CountdownImage()
	self._controls_hbox.pack_start(self._countdown_image, expand=True, fill=False)

	self._play_button = PlayButton()
	self._play_button.connect('clicked', self._play_pause_clicked)
	self._controls_hbox.pack_start(self._play_button, expand=False)

	self._playback_scale = PlaybackScale(self.model)
	self._controls_hbox.pack_start(self._playback_scale, expand=True, fill=True)

	self._progress = ProgressInfo()
	self._controls_hbox.pack_start(self._progress, expand=True, fill=True)

	self._title_label = gtk.Label()
	self._title_label.set_markup("<b><span foreground='white'>"+_('Title:')+'</span></b>')
	self._controls_hbox.pack_start(self._title_label, expand=False)

	self._title_entry = gtk.Entry()
	self._title_entry.modify_bg(gtk.STATE_INSENSITIVE, COLOR_BLACK)
	self._title_entry.connect('changed', self._title_changed)
	self._controls_hbox.pack_start(self._title_entry, expand=True, fill=True, padding=10)

	self._record_container = RecordContainer(self._media_view, self._controls_hbox)
	main_box.pack_start(self._record_container, expand=True, fill=True,
	padding=6)
	self._record_container.show()

	self._thumb_tray = HTray()
	self._thumb_tray.set_size_request(-1, 150)
	main_box.pack_end(self._thumb_tray, expand=False)
	self._thumb_tray.show_all()
#--------------------------------------from below the ui_init() end --------------------------------------------------- 

        #the main classes
        self.model = Model(self)
        self.ui_init()
        
        #CSCL
        self.connect("shared", self._shared_cb)
        if self.get_shared_activity():
            #have you joined or shared this activity yourself?
            if self.get_shared():
                self._joined_cb(self)
            else:
                self.connect("joined", self._joined_cb)
        
        # Realize the video view widget so that it knows its own window XID
        self._media_view.realize_video()

        # Changing to the first toolbar kicks off the rest of the setup
        if self.model.get_has_camera():
            self.model.change_mode(constants.MODE_PHOTO)
        else:
            self.model.change_mode(constants.MODE_AUDIO)

