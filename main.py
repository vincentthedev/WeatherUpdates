#!/usr/bin/python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import requests
from metar import Metar
from datetime import datetime

import os.path

class Main_Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Weather Updates")
        self.set_border_width(12)
        self.set_default_size(640, 480)
        self.set_icon_from_file('/usr/share/pixmaps/WeatherUpdates.png')
        self.obs = None
        self.get_weather_btn = Gtk.Button(label="Get weather")
        self.loc_label = Gtk.Label(label="Weather Station Callsign:")
        self.loc_entry = Gtk.Entry()
        self.text_view = Gtk.TextView()
        self.sc = Gtk.ScrolledWindow()
        self.sc.set_vexpand(True)
        self.sc.set_hexpand(True)
        self.sc.add(self.text_view)
        self.get_weather_btn.connect("clicked", self._on_get_weather_btn_clicked)
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(12)
        self.grid.set_column_spacing(12)
        self.grid.attach(self.loc_label, 0, 0, 1, 1)
        self.grid.attach(self.loc_entry, 0, 1, 1, 1)
        self.grid.attach(self.sc, 0, 2, 10, 10)
        self.grid.attach(self.get_weather_btn, 0, 13, 1, 1)
        self.add(self.grid)
        
    def _request_weather_data(self):
        req = requests.get('https://tgftp.nws.noaa.gov/data/observations/metar/stations/{0}.TXT'.format(self._station))
        if req.status_code == 200:
        	print('Got 200 OK from Noaa/NWS Servers!')
        	data = req.text.split('\n', 1)[1]
        	with open(self._filename, 'w') as file:
        		file.write(data)
        	self._decode_data(data)
        else:
        	dlg = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK,
        	text="System Outage, or Invalid weather station!\nPlease try again later.")
        	dlg.run()
        	dlg.destroy()

    def _on_get_weather_btn_clicked(self, widget):
        self._station = self.loc_entry.get_text()
        self._station = self._station.upper()
        self._filename = '/tmp/{0}.TXT'.format(self._station)
        if os.path.isfile(self._filename):
        	with open(self._filename, 'r') as file:
        		data = file.read()
        		self._decode_data(data)
        else:
            self._request_weather_data()
    		
    def _decode_data(self, data):
        self.obs = Metar.Metar(data)
        print(self.obs)
        buffer = self.text_view.get_buffer()
        buffer.set_text(str(self.obs))
        os.system('find ' + self._filename + ' -mmin +15 -type f -exec rm -fv {} \;')
        if os.path.isfile(self._filename) == False:
            self._request_weather_data()
 

win = Main_Window()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

