# main.py

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from form_fields import FormFields
from serial_monitor import SerialMonitor
from plot_gui import Plotter
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout

kivy.require('2.3.0')

class SerialMonitorApp(App):
    
    def build(self):
        # Create a simple Box Layout
        layout = BoxLayout()
        layout.orientation = 'vertical'
        
        # Init The Plots
        self.plots = Plotter(self, hint=0.5)
        layout.add_widget(self.plots)

        # Add four sets of form fields
        self.forms = FormFields(self, num_fields=4, hint=0.3)
        layout.add_widget(self.forms)
        
        # Create Serial Control GUI
        self.control = SerialMonitor(self, hint=0.3)
        layout.add_widget(self.control)
        
        self.forms.add_observer(self.plots)
        
        # Allow control GUI to send events to Plots
        self.control.add_observer(self.plots)

        return layout
    

    def on_stop(self):
        # Ensure the serial connection is closed when the app exits
        self.control.disconnect_from_serial()

if __name__ == '__main__':
    SerialMonitorApp().run()
