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

kivy.require('2.0.0')

class ClearTextInput(TextInput):
    def on_focus(self, instance, value):
        if value:  # If the TextInput is focused
            self.text = ''

# Serial Monitor Class
class SerialMonitor(BoxLayout):

    # Init Function
    def __init__(self, **kwargs):
        super(SerialMonitor, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.serial_ports = self.get_serial_ports()
        self.serial_port_spinner = Spinner(
            text='Select Serial Port',
            values=self.serial_ports,
            size_hint_y=None,
            height=40
        )

        self.serial_port_spinner.bind(on_touch_down=self.update_serial_ports)

        # Init The Plots
        self.init_plots()


        # Connection Area        
        self.baud_rate = TextInput(hint_text='Enter Baud Rate (e.g., 9600)', size_hint_y=None, height=40)
        self.connect_button = Button(text='Connect', size_hint_y=None, height=40)
        self.connect_button.bind(on_press=self.toggle_connection)
        self.output_label = Label(size_hint_y=None, height=40)

        # List to keep track of ID TextInputs
        self.id_inputs = []

        # Add four sets of form fields
        self.forms = FormFields(self, num_fields=4)
        self.add_widget(self.forms)


        
        self.button_layout = BoxLayout(size_hint_y=None, height=40)
        self.start_button = Button(text='Start')
        self.stop_button = Button(text='Stop')
        self.start_button.bind(on_press=self.send_start_command)
        self.stop_button.bind(on_press=self.send_stop_command)
        self.button_layout.add_widget(self.start_button)
        self.button_layout.add_widget(self.stop_button)

        self.add_widget(self.serial_port_spinner)
        self.add_widget(self.baud_rate)
        self.add_widget(self.connect_button)
        self.add_widget(self.output_label)
        self.add_widget(self.button_layout)

        self.serial_connection = None
        self.read_thread = None
        self.stop_thread = False

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def update_serial_ports(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.serial_port_spinner.values = self.get_serial_ports()

    def toggle_connection(self, instance):
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect_from_serial()
        else:
            self.connect_to_serial()

    def connect_to_serial(self):
        port = self.serial_port_spinner.text
        baud_rate = int(self.baud_rate.text)
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            self.output_label.text = 'Connected to {} at {} baud'.format(port, baud_rate)
            self.connect_button.text = 'Disconnect'
            self.stop_thread = False
            self.read_thread = threading.Thread(target=self.read_from_serial)
            self.read_thread.start()
        except Exception as e:
            self.output_label.text = 'Failed to connect: {}'.format(e)

    def disconnect_from_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.stop_thread = True
            self.serial_connection.close()
            self.output_label.text = 'Disconnected'
            self.connect_button.text = 'Connect'

    def read_from_serial(self):
        while not self.stop_thread and self.serial_connection.is_open:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.update_output_label(line)
                    self.parse_serial_data(line)
            except Exception as e:
                self.update_output_label('Error: {}'.format(e))
                break

    def parse_serial_data(self, line):
        try:
            data_pairs = line.split(',')
            for pair in data_pairs:
                key, value = pair.split(':')
                value = int(value)
                #self.update_plot(key, value)
        except ValueError:
            self.update_output_label('Error: Invalid data format')

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

    def update_output_label(self, text):
        def update_label(*args):
            self.output_label.text = text
            self.output_label.texture_update()

        Clock.schedule_once(update_label)

    def send_start_command(self, instance):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(b'Start\n')
            self.update_output_label('Sent: Start')

    def send_stop_command(self, instance):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(b'Stop\n')
            self.update_output_label('Sent: Stop')

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