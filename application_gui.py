# serial_monitor.py

import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import numpy as np
import serial
import serial.tools.list_ports
import threading
from form_fields import FormFields
from serial_monitor import SerialMonitor

kivy.require('2.0.0')


# Serial Monitor Class
class Application(BoxLayout):

    # Init Function
    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Init The Plots
        self.init_plots()

        # List to keep track of ID TextInputs
        self.id_inputs = []

        # Add four sets of form fields
        self.forms = FormFields(self, num_fields=4)
        self.add_widget(self.forms)
        
        self.control = SerialMonitor(self)
        self.add_widget(self.control)

    # Unused but keep if there needs to be things that are destryed
    def close_application(self):
        if self.control.get_is_serial_connection() and self.control.get_is_serial_connection_open:
            self.control.disconnect_from_serial()
        

    def init_plots(self):
        self.data = {'C1': [0] * 100, 'C2': [0] * 100, 'C3': [0] * 100, 'C4': [0] * 100}
        self.fig, (self.ax1, self.ax2, self.ax3, self.ax4) = plt.subplots(4, 1, figsize=(10, 8))
        self.line1, = self.ax1.plot(self.data['C1'])
        self.line2, = self.ax2.plot(self.data['C2'])
        self.line3, = self.ax3.plot(self.data['C3'])
        self.line4, = self.ax4.plot(self.data['C4'])
        self.ax1.set_ylim(0, 1)
        self.ax2.set_ylim(0, 1)
        self.ax3.set_ylim(0, 1)
        self.ax4.set_ylim(0, 1)
        #self.canvas = FigureCanvasKivyAgg(self.fig)
        self.add_widget(FigureCanvasKivyAgg(self.fig)) 
        #self.add_widget(self.canvas)
        #plt.show()

    def update_plot(self, channel, value):
            self.data[channel].append(value)
            self.data[channel].pop(0)
            if channel == 'C1':
                self.line1.set_ydata(self.data['C1'])
                self.ax1.draw_artist(self.ax1.patch)
                self.ax1.draw_artist(self.line1)
            elif channel == 'C2':
                self.line2.set_ydata(self.data['C2'])
                self.ax2.draw_artist(self.ax2.patch)
                self.ax2.draw_artist(self.line2)
            elif channel == 'C3':
                self.line3.set_ydata(self.data['C3'])
                self.ax3.draw_artist(self.ax3.patch)
                self.ax3.draw_artist(self.line3)
            elif channel == 'C4':
                self.line4.set_ydata(self.data['C4'])
                self.ax4.draw_artist(self.ax4.patch)
                self.ax4.draw_artist(self.line4)
            self.canvas.blit()