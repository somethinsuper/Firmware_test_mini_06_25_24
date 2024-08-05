import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
import serial
import serial.tools.list_ports
import threading
from kivy.clock import mainthread

# Class to create Serial monitor
class SerialMonitor(BoxLayout):
    
    # Init layout and create all the GUI Widgets
    def __init__(self, application_gui, hint: float, **kwargs):
        
        # Create Layout
        super(SerialMonitor, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create List of Observers
        self.observers = []
        
        # Layout for connecting to board TODO: Make better
        topLayout = BoxLayout(size_hint_y=hint / 4, size_hint_x=1)
        topLayout.orientation = 'horizontal'
        self.size_hint_y = hint
        
        # Get Serial ports and make a spinner that shows the value
        self.serial_ports = self.get_serial_ports()
        self.serial_port_spinner = Spinner(text='Select Serial Port', values=self.serial_ports, size_hint_y=1,)
        
        # When the Spinner is touched, update the serial ports avaible
        self.serial_port_spinner.bind(on_touch_down=self.update_serial_ports)
        
        # Connection Area TODO: Change baud_rate to be spinner       
        self.baud_rate = TextInput(hint_text='Enter Baud Rate (e.g., 9600)', size_hint_y=1)
        self.connect_button = Button(text='Connect', size_hint_y=1)
        self.connect_button.bind(on_press=self.toggle_connection)
        self.output_label = Label(size_hint_y=1)
        
        # Create a layout for the start an stop buttons
        self.button_layout = BoxLayout(size_hint_y=1)
        
        # Create start and stop button layouts
        self.start_button = Button(text='Start')
        self.stop_button = Button(text='Stop')
        
        # Bind start and stop buttons to start and stop command
        self.start_button.bind(on_press=self.send_start_command)
        self.stop_button.bind(on_press=self.send_stop_command)
        
        # Add these Widgets to Button layout
        self.button_layout.add_widget(self.start_button)
        self.button_layout.add_widget(self.stop_button)

        # Add all the widgets and layouts to GUI
        self.add_widget(self.serial_port_spinner)
        self.add_widget(self.baud_rate)
        self.add_widget(self.connect_button)
        self.add_widget(self.output_label)
        self.add_widget(self.button_layout)

        # Set global varibles for Serial Connection
        self.serial_connection = None
        self.read_thread = None
        self.stop_thread = False
    
    # Returns a list of serial ports connected to PC
    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    # Event activated when Serial Port Spinner is touched
    def update_serial_ports(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.serial_port_spinner.values = self.get_serial_ports()
    
    # Toggle function switching Connect button to connect or disconnect
    def toggle_connection(self, instance):
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect_from_serial() # Disconnnect if connected
        else:
            self.connect_to_serial() # Else Connect
    
    # Serial connection function
    # NOTE: this runs on a seperate thread so that the serial can run uninterupted. Any events called
    # from serial must use @mainthread to be rendered on the GUI
    def connect_to_serial(self):
        
        # Get Port and Baud_rate
        port = self.serial_port_spinner.text
        baud_rate = int(self.baud_rate.text)
        
        # Try to connect to Serial
        try:
            # Create Serial Connection
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            self.output_label.text = 'Connected to {} at {} baud'.format(port, baud_rate)
            
            # Set varibles to verfiy that thread is running and serial is connected
            self.connect_button.text = 'Disconnect'
            self.stop_thread = False
            
            # Create Seperate thread for serial
            self.read_thread = threading.Thread(target=self.read_from_serial)
            self.read_thread.start()
            
        # If not throw and error instead of crashing
        except Exception as e:
            self.output_label.text = 'Failed to connect: {}'.format(e)
            
    # Function to disconnect seperate thread from Serial
    def disconnect_from_serial(self):
        
        # Only stop if serial is connected
        if self.serial_connection and self.serial_connection.is_open:
            
            # Stop Serial Connection
            self.stop_thread = True
            self.serial_connection.close()
            
            # Set GUI
            self.output_label.text = 'Disconnected'
            self.connect_button.text = 'Connect'
            
    # On the seperate thread, read from the serial monitor
    # NOTE: New messages must be on a new line 
    def read_from_serial(self):
        
        # Check if serial is open
        while not self.stop_thread and self.serial_connection.is_open:
            
            # Try to read Serial. If there is a new line then parse it
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    self.update_output_label(line)
                    
                    # Try to Parse the Incoming Data
                    try:
                        data_pairs = line.split(',')
                        
                        # Notify observers
                        for pair in data_pairs:
                            self.notify_observers(pair)
                    
                    # Else throw and error
                    except ValueError:
                        self.update_output_label('Error: Invalid data format')
            
            # if not throw and error instead of crashing
            except Exception as e:
                self.update_output_label('Error: {}'.format(e))
                break
            
    # Function to Update Output Labels
    def update_output_label(self, text):
        
        # Needs to be done on main thread, so callback is being created 
        def update_label(*args):
            self.output_label.text = text
            self.output_label.texture_update()

        # Update using Clock
        Clock.schedule_once(update_label)
        
    # Send 'Start to Arduino ir serial is connected
    def send_start_command(self, instance):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(b'Start\n')
            self.update_output_label('Sent: Start')

    # Send 'Stop to Arduino ir serial is connected
    def send_stop_command(self, instance):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(b'Stop\n')
            self.update_output_label('Sent: Stop')
            
    # Add observers (in this case the Plotter Class Used)
    def add_observer(self, observer):
        self.observers.append(observer)
    
    # Notify the observers on the main thread
    @mainthread
    def notify_observers(self, pair):
        for observer in self.observers:
            observer.update_plot(pair=pair)
            
    # Getters and Setters
    def get_is_serial_connection(self):
        return self.serial_connection
    
    def get_is_serial_connection_open(self):
        return self.serial_connection.is_open