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
class SerialMonitor(BoxLayout):
    def __init__(self, application_gui, **kwargs):
        super(SerialMonitor, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 160  # Adjust height based on the number of form fields
        
        
        self.serial_ports = self.get_serial_ports()
        self.serial_port_spinner = Spinner(
            text='Select Serial Port',
            values=self.serial_ports,
            size_hint_y=None,
            height=40
        )
        
        self.serial_port_spinner.bind(on_touch_down=self.update_serial_ports)
        
        # Connection Area        
        self.baud_rate = TextInput(hint_text='Enter Baud Rate (e.g., 9600)', size_hint_y=None, height=40)
        self.connect_button = Button(text='Connect', size_hint_y=None, height=40)
        self.connect_button.bind(on_press=self.toggle_connection)
        self.output_label = Label(size_hint_y=None, height=40)
        
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
            
    # Getters and Setters
    def get_is_serial_connection(self):
        return self.serial_connection
    
    def get_is_serial_connection_open(self):
        return self.serial_connection.is_open